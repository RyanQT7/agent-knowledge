from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.evolution.audit import audit
from scripts.evolution.common import (
    EVOLUTION, ROOT, atomic_write_json, file_lock, new_run_id, read_json,
    sha256_file, utc_now,
)
from scripts.evolution.discovery import discover, load_config, choose_topics, _query_string, _cursor_key

RUN_DIR = EVOLUTION / "runs"
STATE_PATH = EVOLUTION / "state" / "discovery.json"
RUN_LOCK = EVOLUTION / "state" / ".run.lock"
RELEVANT_SKILLS = (
    "skills/research-discovery/SKILL.md",
    "skills/knowledge-audit/SKILL.md",
    "skills/knowledge-evolution/SKILL.md",
    "skills/paper-reading/SKILL.md",
    "skills/learning-batch/SKILL.md",
    "skills/knowledge-review/SKILL.md",
    "skills/knowledge-query/SKILL.md",
    "skills/aiops-paper-reading/SKILL.md",
    "skills/aiops-learning-batch/SKILL.md",
    "skills/paper-code-discovery/SKILL.md",
    "skills/code-reading/SKILL.md",
)


def _manifest_path(root: Path, run_id: str) -> Path:
    return root / "evolution" / "runs" / f"{run_id}.json"


def _load_manifest(root: Path, run_id: str) -> dict[str, Any]:
    path = _manifest_path(root, run_id)
    value = read_json(path, None)
    if not isinstance(value, dict):
        raise FileNotFoundError(f"run manifest not found: {path.relative_to(root)}")
    return value


def _write_manifest(root: Path, run: dict[str, Any]) -> None:
    atomic_write_json(_manifest_path(root, run["run_id"]), run)


def _skill_versions(root: Path) -> dict[str, str]:
    return {path: sha256_file(root / path) for path in RELEVANT_SKILLS if (root / path).is_file()}


def _initial_manifest(root: Path, run_id: str, mode: str, focus_ids: list[str] | None, auto: bool, query_override: str | None = None) -> dict[str, Any]:
    config = load_config(root / "evolution" / "config" / "watchlist.yaml")
    if query_override:
        import re
        from scripts.evolution.common import stable_hash
        selected = [{
            "id": "custom-" + stable_hash(query_override, 10), "title": query_override,
            "keywords": re.findall(r"[\w-]+", query_override), "query": query_override,
            "research_questions": [query_override], "priority": 5,
            "sources": config.get("default_sources", []),
        }]
    else:
        selected = choose_topics(root, config, focus_ids, auto)
    state = read_json(root / "evolution" / "state" / "discovery.json", {"cursors": {}})
    queries = []
    before = {}
    for topic in selected:
        query = _query_string(topic)
        for source in topic.get("sources", config.get("default_sources", [])):
            key = _cursor_key(topic["id"], source, query)
            queries.append({"topic_id": topic["id"], "source": source, "query": query, "cursor_key": key})
            before[key] = state.get("cursors", {}).get(key)
    return {
        "run_id": run_id,
        "started_at": utc_now(),
        "finished_at": None,
        "mode": mode,
        "research_focus": ", ".join(topic["title"] for topic in selected) or "auto-selected gap",
        "topics": [topic["id"] for topic in selected],
        "query_override": query_override,
        "model": "unavailable (Codex runtime does not expose model identity to the script)",
        "token_usage": "unavailable",
        "api_cost": "unavailable",
        "skill_versions": _skill_versions(root),
        "queries": queries,
        "cursor_before": before,
        "cursor_after": {},
        "candidates_found": 0,
        "duplicates": 0,
        "papers_selected": [],
        "papers_read": [],
        "claims_reviewed": [],
        "proposals_created": [],
        "errors": [],
        "status": "running",
        "phases": {
            "discovery": "pending",
            "deterministic_audit": "pending",
            "paper_and_code_reading": "pending",
            "semantic_audit": "pending",
            "proposal": "pending",
            "approval": "pending",
            "report": "pending",
        },
        "mode_boundary": "No formal knowledge file is changed by this runner. Codex Skills own the semantic research/proposal stages; applying a proposal requires explicit human approval.",
    }


def start_run(root: Path = ROOT, mode: str = "proposal", focus_ids: list[str] | None = None, auto: bool | None = None, query_override: str | None = None, run_id: str | None = None) -> dict[str, Any]:
    if mode not in {"audit-only", "proposal"}:
        raise ValueError("mode must be audit-only or proposal")
    if auto is None:
        auto = not focus_ids and not query_override
    run_id = run_id or new_run_id()
    path = _manifest_path(root, run_id)
    with file_lock(root / "evolution" / "state" / ".run.lock"):
        if path.exists():
            raise FileExistsError(f"run already exists: {run_id}; use resume")
        run = _initial_manifest(root, run_id, mode, focus_ids, auto, query_override)
        _write_manifest(root, run)
    return _advance_deterministic(root, run)


def _advance_deterministic(root: Path, run: dict[str, Any]) -> dict[str, Any]:
    run_id = run["run_id"]
    if run["phases"].get("discovery") != "complete":
        run["phases"]["discovery"] = "running"
        _write_manifest(root, run)
        try:
            result = discover(root=root, topic_ids=run.get("topics") or None, query_override=run.get("query_override"), run_id=run_id)
            run["discovery_result"] = result
            run["candidates_found"] = result.get("candidates_added", 0)
            run["duplicates"] = result.get("duplicates", 0)
            run["phases"]["discovery"] = "complete" if result.get("status") in {"success", "partial", "no_topics"} else "failed"
            if result.get("status") == "partial":
                run["errors"].extend([item for item in result.get("source_results", []) if item.get("status") == "failed"])
        except Exception as exc:
            run["phases"]["discovery"] = "failed"
            run["errors"].append({"phase": "discovery", "error": f"{type(exc).__name__}: {exc}"})
            run["status"] = "partial"
            run["finished_at"] = utc_now()
            _write_manifest(root, run)
            return run
        _write_manifest(root, run)
    if run["phases"].get("deterministic_audit") != "complete":
        run["phases"]["deterministic_audit"] = "running"
        _write_manifest(root, run)
        try:
            result = audit(root=root, run_id=run_id)
            run["audit_result"] = {key: value for key, value in result.items() if key != "findings"}
            run["phases"]["deterministic_audit"] = "complete"
        except Exception as exc:
            run["phases"]["deterministic_audit"] = "failed"
            run["errors"].append({"phase": "deterministic_audit", "error": f"{type(exc).__name__}: {exc}"})
            run["status"] = "partial"
            run["finished_at"] = utc_now()
            _write_manifest(root, run)
            return run
        _write_manifest(root, run)
    run["cursor_after"] = read_json(root / "evolution" / "state" / "discovery.json", {}).get("cursors", {})
    if run["mode"] == "audit-only":
        run["status"] = "complete"
        run["finished_at"] = utc_now()
    else:
        run["status"] = "awaiting_codex_research"
        run["finished_at"] = None
    _write_manifest(root, run)
    return run


def resume_run(root: Path, run_id: str) -> dict[str, Any]:
    with file_lock(root / "evolution" / "state" / ".run.lock"):
        run = _load_manifest(root, run_id)
        if run.get("status") in {"complete", "approved", "cancelled"}:
            return run
        return _advance_deterministic(root, run)


def update_stage(root: Path, run_id: str, phase: str, status: str, note: str = "", values: dict[str, Any] | None = None) -> dict[str, Any]:
    allowed_phases = {"discovery", "deterministic_audit", "paper_and_code_reading", "semantic_audit", "proposal", "approval", "report"}
    allowed_status = {"pending", "running", "complete", "failed", "blocked", "not_needed"}
    if phase not in allowed_phases or status not in allowed_status:
        raise ValueError("invalid phase or phase status")
    with file_lock(root / "evolution" / "state" / ".run.lock"):
        run = _load_manifest(root, run_id)
        run.setdefault("phases", {})[phase] = status
        if note:
            run.setdefault("phase_notes", {}).setdefault(phase, []).append({"at": utc_now(), "note": note})
        if values:
            for key, value in values.items():
                if key in {"papers_selected", "papers_read", "claims_reviewed", "proposals_created"}:
                    existing = run.setdefault(key, [])
                    for item in value if isinstance(value, list) else [value]:
                        if item not in existing:
                            existing.append(item)
                elif key == "errors":
                    run.setdefault(key, []).extend(value if isinstance(value, list) else [value])
        _write_manifest(root, run)
        return run


def finish_run(root: Path, run_id: str, status: str = "complete", note: str = "") -> dict[str, Any]:
    if status not in {"complete", "partial", "blocked", "cancelled"}:
        raise ValueError("invalid final run status")
    with file_lock(root / "evolution" / "state" / ".run.lock"):
        run = _load_manifest(root, run_id)
        run["status"] = status
        run["finished_at"] = utc_now()
        if note:
            run.setdefault("completion_notes", []).append({"at": utc_now(), "note": note})
        _write_manifest(root, run)
        return run


def _print(run: dict[str, Any]) -> None:
    print(json.dumps(run, ensure_ascii=False, indent=2))


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Start/resume a durable knowledge evolution run.")
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start")
    start.add_argument("--mode", choices=("audit-only", "proposal"), default="proposal")
    start.add_argument("--topic", action="append", dest="topics")
    start.add_argument("--auto", action="store_true", default=None)
    start.add_argument("--query", help="explicit temporary research query")
    start.add_argument("--run-id")
    resume = commands.add_parser("resume")
    resume.add_argument("run_id")
    stage = commands.add_parser("stage")
    stage.add_argument("run_id")
    stage.add_argument("--phase", required=True)
    stage.add_argument("--status", required=True)
    stage.add_argument("--note", default="")
    finish = commands.add_parser("finish")
    finish.add_argument("run_id")
    finish.add_argument("--status", choices=("complete", "partial", "blocked", "cancelled"), default="complete")
    finish.add_argument("--note", default="")
    args = parser.parse_args(argv)
    try:
        if args.command == "start":
            run = start_run(mode=args.mode, focus_ids=args.topics, auto=args.auto, query_override=args.query, run_id=args.run_id)
        elif args.command == "resume":
            run = resume_run(ROOT, args.run_id)
        elif args.command == "stage":
            run = update_stage(ROOT, args.run_id, args.phase, args.status, args.note)
        else:
            run = finish_run(ROOT, args.run_id, args.status, args.note)
        _print(run)
    except Exception as exc:
        print(f"run operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
