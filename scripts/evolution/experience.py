from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.evolution.common import atomic_write_json, atomic_write_jsonl, file_lock, read_json, read_jsonl, sha256_bytes, utc_now


RECORDS = Path("evolution/experience/records.jsonl")
INDEX = Path("evolution/experience/index.json")
TYPES = {
    "success", "failure", "user_feedback", "efficiency_issue", "environment_issue",
    "controller_issue", "skill_issue", "model_issue", "evidence_gap",
}
STATUSES = {"active", "needs_review", "superseded", "rejected"}


def _plain_tokens(value: str) -> set[str]:
    text = value.lower()
    tokens = set(re.findall(r"[a-z0-9][a-z0-9_-]{1,}", text))
    for span in re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", text):
        if len(span) == 1:
            tokens.add(span)
        else:
            tokens.update(span[index:index + 2] for index in range(len(span) - 1))
    return tokens


def _engine_specific(record: dict[str, Any]) -> bool:
    types = record.get("experience_type", [])
    if isinstance(types, str):
        types = [types]
    if "controller_issue" in types:
        return True
    scope = str(record.get("applicability", "")).casefold()
    return "evolution engine" in scope or scope.startswith("engine controller")


def _global_preference(record: dict[str, Any]) -> bool:
    types = record.get("experience_type", [])
    if isinstance(types, str):
        types = [types]
    applicability = str(record.get("applicability", "")).strip().casefold()
    return bool(
        record.get("persistent")
        and "user_feedback" in types
        and (applicability in {"all tasks", "all", "global"} or (
            str(record.get("task_type", "general")) == "general"
            and not record.get("research_topic")
            and not record.get("skill_name")
        ))
    )


def _fingerprint(record: dict[str, Any]) -> str:
    basis = "|".join([
        ",".join(sorted(record.get("experience_type", []))),
        str(record.get("skill_name") or "").lower(),
        re.sub(r"\s+", " ", str(record.get("lesson", "")).strip().lower()),
        re.sub(r"\s+", " ", str(record.get("recommended_action", "")).strip().lower()),
    ])
    return sha256_bytes(basis.encode("utf-8"))[:20]


def _write_index(root: Path, records: list[dict[str, Any]]) -> None:
    value = {
        "schema_version": 1,
        "updated_at": utc_now(),
        "record_count": len(records),
        "active_count": sum(item.get("status") == "active" for item in records),
        "experience_ids": [item["experience_id"] for item in records],
    }
    atomic_write_json(root / INDEX, value)


def add_experience(root: Path, record: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    root = root.resolve()
    path = root / RECORDS
    types = record.get("experience_type", [])
    if isinstance(types, str):
        types = [types]
    types = sorted({str(item) for item in types})
    unknown = set(types) - TYPES
    if not types or unknown:
        raise ValueError(f"experience_type must use supported values; unknown: {sorted(unknown)}")
    message = str(record.get("lesson") or record.get("observed_behavior") or "").strip()
    if not message:
        raise ValueError("lesson or observed_behavior is required")
    normalized = {
        "created_at": record.get("created_at") or utc_now(),
        "task_type": str(record.get("task_type") or "general"),
        "research_topic": str(record.get("research_topic") or ""),
        "run_id": str(record.get("run_id") or ""),
        "skill_name": str(record.get("skill_name") or ""),
        "skill_version": str(record.get("skill_version") or ""),
        "experience_type": types,
        "expected_behavior": str(record.get("expected_behavior") or ""),
        "observed_behavior": str(record.get("observed_behavior") or message),
        "outcome": str(record.get("outcome") or ""),
        "suspected_cause": str(record.get("suspected_cause") or ""),
        "confirmed_cause": str(record.get("confirmed_cause") or ""),
        "evidence_refs": list(dict.fromkeys(str(item) for item in record.get("evidence_refs", []) if item)),
        "lesson": message[:1200],
        "recommended_action": str(record.get("recommended_action") or "")[:1200],
        "applicability": str(record.get("applicability") or record.get("research_topic") or "relevant tasks"),
        "persistent": bool(record.get("persistent", False)),
        "status": str(record.get("status") or "active"),
        "occurrences": 1,
        "use_count": 0,
        "last_used_at": None,
    }
    if normalized["status"] not in STATUSES:
        raise ValueError(f"unsupported experience status: {normalized['status']}")
    fingerprint = _fingerprint(normalized)
    normalized["fingerprint"] = fingerprint
    with file_lock(root / "evolution/experience/.records.lock"):
        rows = read_jsonl(path)
        prior = next((item for item in rows if item.get("fingerprint") == fingerprint), None)
        if prior:
            if prior.get("status") == "rejected":
                return prior, False
            prior_refs = set(prior.get("evidence_refs", []))
            new_refs = set(normalized["evidence_refs"])
            if not new_refs or not new_refs <= prior_refs:
                prior["occurrences"] = int(prior.get("occurrences", 1)) + 1
            prior["evidence_refs"] = list(dict.fromkeys(prior.get("evidence_refs", []) + normalized["evidence_refs"]))
            prior["last_seen_at"] = utc_now()
            if normalized["persistent"]:
                prior["persistent"] = True
            if normalized["status"] == "active" and prior.get("status") == "needs_review":
                prior["status"] = "active"
            atomic_write_jsonl(path, rows)
            _write_index(root, rows)
            return prior, False
        normalized["experience_id"] = str(record.get("experience_id") or f"exp-{fingerprint[:12]}")
        normalized["last_seen_at"] = normalized["created_at"]
        rows.append(normalized)
        atomic_write_jsonl(path, rows)
        _write_index(root, rows)
        return normalized, True


def list_experiences(root: Path, status: str | None = None) -> list[dict[str, Any]]:
    records = read_jsonl(root.resolve() / RECORDS)
    return [item for item in records if status is None or item.get("status") == status]


def set_experience_status(root: Path, experience_id: str, status: str) -> dict[str, Any]:
    if status not in STATUSES:
        raise ValueError(f"unsupported status: {status}")
    root = root.resolve()
    path = root / RECORDS
    with file_lock(root / "evolution/experience/.records.lock"):
        rows = read_jsonl(path)
        for row in rows:
            if row.get("experience_id") == experience_id:
                row["status"] = status
                row["status_updated_at"] = utc_now()
                atomic_write_jsonl(path, rows)
                _write_index(root, rows)
                return row
    raise KeyError(experience_id)


def retrieve_experiences(
    root: Path, *, task_type: str = "", topic: str = "", skill_names: list[str] | None = None,
    stage: str = "", limit: int = 5, mark_used: bool = False, include_engine: bool = False,
) -> list[dict[str, Any]]:
    root = root.resolve()
    records = list_experiences(root, "active")
    skills = {name.lower() for name in (skill_names or []) if name}
    query_tokens = _plain_tokens(" ".join([task_type, topic, stage, *skills]))
    ranked: list[tuple[bool, float, int, str, dict[str, Any]]] = []
    for row in records:
        if not include_engine and _engine_specific(row):
            continue
        score = 0.0
        row_skills = {str(row.get("skill_name", "")).lower()} - {""}
        if skills & row_skills:
            score += 8
        if task_type and task_type.lower() == str(row.get("task_type", "")).lower():
            score += 4
        elif task_type and str(row.get("task_type", "")).lower() not in {"", "general"}:
            score -= 2
        if row.get("persistent") and "user_feedback" in row.get("experience_type", []):
            score += 4
        searchable = " ".join(str(row.get(field, "")) for field in (
            "research_topic", "lesson", "recommended_action", "applicability", "expected_behavior", "observed_behavior"
        ))
        overlap = len(query_tokens & _plain_tokens(searchable))
        score += min(overlap, 8) * 0.6
        preference = _global_preference(row)
        if score > 0 or preference:
            ranked.append((preference, score, int(row.get("occurrences", 1)), str(row.get("created_at", "")), row))
    ranked.sort(key=lambda item: item[:4], reverse=True)
    selected = []
    now = utc_now()
    for _, score, _, _, row in ranked[:max(0, limit)]:
        compact = {key: row.get(key) for key in (
            "experience_id", "task_type", "research_topic", "skill_name", "experience_type", "lesson",
            "recommended_action", "applicability", "status", "persistent", "evidence_refs"
        )}
        compact["relevance"] = round(score, 1)
        selected.append(compact)
    if mark_used and selected:
        used_ids = {item["experience_id"] for item in selected}
        path = root / RECORDS
        with file_lock(root / "evolution/experience/.records.lock"):
            rows = read_jsonl(path)
            for row in rows:
                if row.get("experience_id") in used_ids:
                    row["use_count"] = int(row.get("use_count", 0)) + 1
                    row["last_used_at"] = now
            atomic_write_jsonl(path, rows)
            _write_index(root, rows)
    return selected


def collect_run_experience(root: Path, run_dir: Path, state: dict[str, Any], goal: dict[str, Any]) -> list[str]:
    """Persist only reusable run outcomes/failures from structured checkpoints."""
    run_id = str(state.get("run_id", run_dir.name))
    focus = str(goal.get("research_focus", ""))
    rows: list[dict[str, Any]] = []
    for event in read_jsonl(run_dir / "events.jsonl"):
        if event.get("type") != "controller_failure":
            continue
        details = event.get("details", {})
        message = str(details.get("message", "Unexpected Controller exception"))[:700]
        rows.append({
            "task_type": "research", "research_topic": focus, "run_id": run_id,
            "skill_name": "knowledge-evolution", "skill_version": str(state.get("base_commit") or ""),
            "experience_type": ["failure", "controller_issue"], "outcome": "controller_failure",
            "observed_behavior": f"{details.get('type', 'Exception')}: {message}",
            "suspected_cause": "controller", "confirmed_cause": "",
            "evidence_refs": [f"run:{run_id}:events.jsonl:controller_failure"],
            "lesson": "An unexpected exception occurred in the Python Controller; diagnose and fix program logic before changing a Skill.",
            "recommended_action": "Reproduce the failure from the saved stage/state, then fix the Controller or runtime boundary; do not add a Skill instruction for a programming defect.",
            "applicability": "Evolution Engine runtime",
        })
    runtime_types = {
        "environment_error": ("environment_issue", "runtime_environment"),
        "quota": ("environment_issue", "model_quota_or_auth"),
        "permission_error": ("environment_issue", "runtime_permission"),
        "model_error": ("model_issue", "model_output_or_schema"),
        "controller_issue": ("controller_issue", "controller"),
    }
    rounds = state.get("rounds", {})
    for number, data in rounds.items():
        runtime = data.get("runtime_reflection", {})
        runtime_type = str(runtime.get("failure_type", ""))
        if runtime_type in runtime_types:
            category, cause = runtime_types[runtime_type]
            rows.append({
                "task_type": "research", "research_topic": focus, "run_id": run_id,
                "skill_name": "knowledge-evolution", "skill_version": str(state.get("base_commit") or ""),
                "experience_type": ["failure", category], "outcome": "runtime_failure",
                "observed_behavior": " ".join(str(item) for item in runtime.get("failure_evidence", [])[:2])[:700],
                "suspected_cause": cause, "confirmed_cause": "",
                "evidence_refs": [f"run:{run_id}:round:{number}:runtime-reflection"],
                "lesson": f"A research run encountered a {category.replace('_', ' ')} before completing its bounded stage.",
                "recommended_action": str(runtime.get("next_step") or "Address the specific runtime condition before resuming; do not change a Skill for an environment or model failure.")[:700],
                "applicability": "Evolution Engine runs",
            })
        decision = data.get("evaluation", {}).get("decision")
        detail = str(data.get("evaluation", {}).get("rationale", ""))[:500]
        if decision in {"NEEDS_REVIEW", "RETRY"}:
            hard_errors = data.get("deterministic_evaluation", {}).get("hard_errors", [])
            error_types = {str(item.get("type", "")) for item in hard_errors}
            if error_types & {"artifact_path", "permission", "unknown_related_claim", "unknown_related_finding"}:
                cause, types, lesson, action = (
                    "controller_issue", ["failure", "controller_issue"],
                    "Deterministic runtime checks caught a structured-output, artifact, or permission-boundary defect; fix the Controller boundary before changing Skills.",
                    "Use the run's deterministic error and exact field/path to fix Controller logic; do not patch a Skill unless independent evidence shows a Skill rule caused it.",
                )
            elif "source_unavailable" in error_types:
                cause, types, lesson, action = (
                    "source_environment", ["failure", "environment_issue"],
                    "The research evaluation could not access or verify a referenced primary source; this may be a transient network/provider condition.",
                    "Check source availability and retry only the specific verification after the environment condition changes; do not change a Skill to compensate for temporary unavailability.",
                )
            elif any(kind in {"missing_evidence_locator", "unlisted_evidence", "evidence_quote", "source_identity", "claim_source_identity"} for kind in error_types) or "evidence" in detail.lower():
                cause, types, lesson, action = (
                    "evidence_gap", ["failure", "evidence_gap"],
                    "The independent evaluation could not verify at least one candidate claim from its source locator or saved excerpt.",
                    "Provide the Judge with the relevant local primary-source section and precise locator; keep unsupported claims unverified.",
                )
            elif error_types & {"future_date", "schema", "invalid_json"}:
                cause, types, lesson, action = (
                    "model_output", ["failure", "model_issue"],
                    "A model-generated field or structured response failed a deterministic validation check.",
                    "Correct the specific model output field or ask for a constrained correction; change a Skill only if the required behavior was missing or ambiguous.",
                )
            else:
                cause, types, lesson, action = (
                    "needs_review", ["failure"],
                    f"A research round ended {decision}; inspect the saved evaluation before repeating work.",
                    "Resume only the concrete unresolved check; do not repeat discovery or full-paper reading when saved evidence is available.",
                )
            rows.append({
                "task_type": "research", "research_topic": focus, "run_id": run_id,
                "skill_name": "knowledge-evolution", "skill_version": str(state.get("base_commit") or ""),
                "experience_type": types, "observed_behavior": detail or decision,
                "outcome": decision, "suspected_cause": cause, "confirmed_cause": cause,
                "evidence_refs": [f"run:{run_id}:round:{number}:evaluation"], "lesson": lesson,
                "recommended_action": action, "applicability": "bounded research tasks with independent evidence evaluation",
            })
    if state.get("status") == "BUDGET_EXHAUSTED":
        usage = state.get("token_usage", "unavailable")
        total = usage.get("input_tokens") if isinstance(usage, dict) else None
        rows.append({
            "task_type": "research", "research_topic": focus, "run_id": run_id,
            "skill_name": "knowledge-evolution", "skill_version": str(state.get("base_commit") or ""),
            "experience_type": ["efficiency_issue"], "outcome": "budget_exhausted",
            "observed_behavior": str(state.get("terminal_reason", "budget exhausted"))[:500],
            "suspected_cause": "resource_budget", "evidence_refs": [f"run:{run_id}:state.json"],
            "lesson": "A bounded research run exhausted its configured budget before task completion.",
            "recommended_action": "Reuse saved sources and completed stages; reserve calls for independent evaluation and reflection, and stop when further work has low expected value.",
            "applicability": "bounded research tasks", "outcome_details": {"reported_input_tokens": total if total is not None else "unavailable"},
        })
    if not rows and state.get("status") in {"COMPLETED", "NO_UPDATE_NEEDED"}:
        gains = [len(item.get("knowledge_gain", {}).get("accepted_findings", [])) for item in rounds.values()]
        if any(gains):
            rows.append({
                "task_type": "research", "research_topic": focus, "run_id": run_id,
                "skill_name": "knowledge-evolution", "skill_version": str(state.get("base_commit") or ""),
                "experience_type": ["success"], "outcome": "completed_with_verified_candidate_gain",
                "observed_behavior": f"Completed bounded research with {sum(gains)} independently accepted candidate finding(s); formal knowledge remains review-only.",
                "suspected_cause": "", "evidence_refs": [f"run:{run_id}:final-report.md"],
                "lesson": "Keep candidate knowledge separate from approved formal knowledge; use independent source checks and preserve evidence locators.",
                "recommended_action": "Generate a reviewable proposal only after independent evaluation; do not auto-apply findings.",
                "applicability": "evidence-based research evolution",
            })
    saved = []
    for row in rows:
        item, _ = add_experience(root, row)
        saved.append(item["experience_id"])
    return list(dict.fromkeys(saved))


def import_history(root: Path) -> list[dict[str, Any]]:
    historical = [
        {"experience_type": ["efficiency_issue"], "task_type": "research", "research_topic": "Agent Memory and Self-Evolving Agents", "skill_name": "knowledge-evolution", "confirmed_cause": "execution_efficiency", "evidence_refs": ["evolution/runs/phase-1.5-progress-and-issues.md#measured-usage-and-cost", "run:phase15-memfolder-cont-20261125-a3a68a8:final-report.md"], "observed_behavior": "MemFolder initial Executor reported 1,082,826 input tokens; the wider pilot reported 2,035,756 input tokens across completed responses.", "outcome": "later bounded continuation reused saved sources and used 63,157 input tokens across three calls", "lesson": "Prefer existing local paper sources and saved reading results; a targeted evidence gap should not trigger repeated discovery or a full reread.", "recommended_action": "Reuse local PDFs/text and completed run records, then read only the sections needed for the unresolved claim. Keep search, call, and time caps.", "applicability": "paper research and evidence follow-up"},
        {"experience_type": ["failure", "controller_issue"], "task_type": "research", "research_topic": "Agent Memory and Self-Evolving Agents", "skill_name": "knowledge-evolution", "confirmed_cause": "controller_retry_artifact_overwrite", "evidence_refs": ["evolution/runs/phase-1.5-progress-and-issues.md#issues-found"], "observed_behavior": "A targeted Executor retry overwrote the shared artifact path and hid the earlier complete findings/full-read record from evaluation.", "outcome": "fixed in Controller by separate immutable attempt artifacts and merged evaluation context", "lesson": "Executor retries must preserve each attempt and Controller must merge prior valid evidence with the targeted addendum before evaluation.", "recommended_action": "Fix artifact/state aggregation in Python Controller; do not add a Skill rule for an already fixed Controller defect.", "applicability": "Evolution Engine retries"},
        {"experience_type": ["failure", "controller_issue"], "task_type": "research", "research_topic": "Agent Memory and Self-Evolving Agents", "skill_name": "knowledge-evolution", "confirmed_cause": "finding_claim_reference_boundary", "evidence_refs": ["evolution/runs/phase-1.5-progress-and-issues.md#issues-found"], "observed_behavior": "Temporary Finding ID F2 was placed in related_claim_ids although it was absent from the formal Claim store.", "outcome": "fixed with distinct related_finding_ids and deterministic Claim-ID validation", "lesson": "Temporary Findings and stable knowledge Claims are distinct identifiers; reject or remap invalid references at the Controller boundary.", "recommended_action": "Use related_claim_ids only for IDs present in the Claim store; use related_finding_ids for temporary Finding links.", "applicability": "structured research findings"},
        {"experience_type": ["failure", "evidence_gap"], "task_type": "research", "research_topic": "Agent Memory and Self-Evolving Agents", "skill_name": "knowledge-evolution", "confirmed_cause": "insufficient_source_excerpt", "evidence_refs": ["evolution/runs/phase15-memfolder-cont-20261125-a3a68a8/final-report.md#rounds"], "observed_behavior": "The Judge accepted 1 of 5 Findings; the remaining four lacked sufficient saved excerpts to substantiate their claims.", "outcome": "one scoped Finding accepted; four remain unverified", "lesson": "An independent Judge needs access to the relevant primary-source sections and pinpoint locators; an Executor summary is not a substitute.", "recommended_action": "Reuse the local full-read record and inspect only the sections needed for each Finding; preserve unsupported Findings as unverified.", "applicability": "independent evidence evaluation"},
        {"experience_type": ["user_feedback"], "task_type": "teaching", "research_topic": "Agent Memory and Self-Evolving Agents", "skill_name": "source-code-annotation", "evidence_refs": ["user-feedback:Phase-2 experience import request; Lesson 2 teaching feedback"], "expected_behavior": "Make technical teaching explanations concrete and trace execution, with Chinese pseudocode comments and real paper examples; teaching visuals can help when useful.", "observed_behavior": "User reported that some Lesson 2 explanations were too abstract and requested concrete cases, Chinese pseudocode comments, internal execution explanation, and optional teaching diagrams.", "outcome": "follow-up Lesson 2 enhancement task was recorded by the user", "lesson": "For teaching artifacts, explain how the mechanism runs using a real paper example and annotated execution steps; add a teaching diagram only when it clarifies the process.", "recommended_action": "Retain as teaching feedback; apply to a matching lesson or source-annotation task, not to unrelated query Skills.", "applicability": "teaching and source-annotation tasks", "status": "active"},
        {"experience_type": ["user_feedback"], "task_type": "general", "research_topic": "", "skill_name": "", "persistent": True, "evidence_refs": ["user-feedback:Phase-2 long-term work preference"], "expected_behavior": "Use enough verification to protect correctness and safety while keeping effort proportional to task value.", "observed_behavior": "User prefers avoiding repeated verification, excessive audit, needless engineering, and unnecessary cost; stricter verification should be used when explicitly requested.", "outcome": "persistent user preference", "lesson": "Keep validation proportional to task risk and value; prioritize the requested result, and avoid repeated checks that cannot change the decision.", "recommended_action": "Use a focused, task-relevant check by default; run deeper verification when explicitly requested or when the change has material correctness or safety risk.", "applicability": "all tasks", "status": "active"},
    ]
    result = []
    for row in historical:
        saved, _ = add_experience(root, row)
        result.append(saved)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record and retrieve compact reusable task experience.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add")
    add.add_argument("--type", action="append", required=True, dest="types")
    add.add_argument("--task-type", default="general")
    add.add_argument("--topic", default="")
    add.add_argument("--skill", default="")
    add.add_argument("--message", required=True)
    add.add_argument("--expected", default="")
    add.add_argument("--recommended-action", default="")
    add.add_argument("--applicability", default="")
    add.add_argument("--source-ref", action="append", default=[])
    add.add_argument("--persistent", action="store_true", help="mark as a reusable long-term preference")
    add.add_argument("--needs-review", action="store_true")
    listing = commands.add_parser("list")
    listing.add_argument("--status", choices=sorted(STATUSES))
    search = commands.add_parser("search")
    search.add_argument("--task-type", default="")
    search.add_argument("--topic", default="")
    search.add_argument("--skill", action="append", default=[])
    search.add_argument("--stage", default="")
    search.add_argument("--limit", type=int, default=5)
    search.add_argument("--include-engine", action="store_true", help="include Evolution Engine/controller execution experiences")
    status = commands.add_parser("status")
    status.add_argument("experience_id")
    status.add_argument("value", choices=sorted(STATUSES))
    commands.add_parser("import-history", help="idempotently import the six known Phase 1.5/user-feedback experiences")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "add":
        user_feedback = "user_feedback" in args.types
        row, created = add_experience(root, {
            "experience_type": args.types, "task_type": args.task_type, "research_topic": args.topic,
            "skill_name": args.skill, "expected_behavior": args.expected or (args.message if user_feedback else ""),
            "observed_behavior": "User provided this feedback." if user_feedback else args.message,
            "lesson": args.message, "evidence_refs": args.source_ref,
            "recommended_action": args.recommended_action,
            "applicability": args.applicability or ("all tasks" if args.persistent else args.topic or args.task_type),
            "persistent": args.persistent, "status": "needs_review" if args.needs_review else "active",
        })
        print(json.dumps({"created": created, **row}, ensure_ascii=False, indent=2))
    elif args.command == "list":
        print(json.dumps(list_experiences(root, args.status), ensure_ascii=False, indent=2))
    elif args.command == "search":
        print(json.dumps(retrieve_experiences(root, task_type=args.task_type, topic=args.topic, skill_names=args.skill, stage=args.stage, limit=max(0, min(args.limit, 20)), mark_used=True, include_engine=args.include_engine), ensure_ascii=False, indent=2))
    elif args.command == "status":
        print(json.dumps(set_experience_status(root, args.experience_id, args.value), ensure_ascii=False, indent=2))
    else:
        imported = import_history(root)
        print(json.dumps({"imported_or_matched": len(imported), "experience_ids": [item["experience_id"] for item in imported]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
