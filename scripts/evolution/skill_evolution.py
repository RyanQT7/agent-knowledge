from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.evolution.common import atomic_write_json, atomic_write_text, read_json, sha256_bytes, sha256_file, utc_now
from scripts.evolution.experience import list_experiences


PROPOSAL_ROOT = Path("evolution/skill-proposals")


def _skill_file(root: Path, name: str) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", name):
        raise ValueError("Skill name must be a simple lowercase directory name")
    path = root / "skills" / name / "SKILL.md"
    if not path.is_file():
        raise FileNotFoundError(f"Skill does not exist: {path.relative_to(root)}")
    if not path.resolve().is_relative_to((root / "skills").resolve()):
        raise ValueError("Skill path escapes skills/")
    return path


def _git_head(root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def _proposal_diff(skill_name: str, original: str, candidate: str) -> str:
    return "".join(difflib.unified_diff(
        original.splitlines(keepends=True), candidate.splitlines(keepends=True),
        fromfile=f"a/skills/{skill_name}/SKILL.md", tofile=f"b/skills/{skill_name}/SKILL.md",
    ))


def _artifact_state(root: Path, directory: Path, proposal: dict[str, Any]) -> tuple[str, str, str, dict[str, str], list[str]]:
    issues: list[str] = []
    paths = {"base_hash": directory / "original.md", "candidate_hash": directory / "candidate.md", "diff_hash": directory / "changes.diff"}
    contents: dict[str, str] = {}
    for name, path in paths.items():
        try:
            contents[name] = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            issues.append(f"Cannot read {path.name}: {type(exc).__name__}.")
            contents[name] = ""
    original, candidate, diff = contents["base_hash"], contents["candidate_hash"], contents["diff_hash"]
    snapshot = {key: sha256_bytes(value.encode("utf-8")) for key, value in contents.items()}
    if snapshot["base_hash"] != proposal.get("base_hash"):
        issues.append("Saved original Skill does not match the Proposal base hash.")
    if snapshot["candidate_hash"] != proposal.get("candidate_hash"):
        issues.append("Candidate Skill changed since the Proposal was created.")
    if snapshot["diff_hash"] != proposal.get("diff_hash"):
        issues.append("Review diff changed since the Proposal was created.")
    expected_diff = _proposal_diff(str(proposal.get("target_skill", "")), original, candidate)
    if diff != expected_diff:
        issues.append("Review diff does not represent the saved original and candidate Skill files.")
    try:
        target = _skill_file(root, str(proposal.get("target_skill", "")))
        if str(target.relative_to(root)) != proposal.get("target_path"):
            issues.append("Proposal target path does not match the Skill directory.")
        if sha256_file(target) != proposal.get("base_hash"):
            issues.append("Target Skill changed since the Proposal was created.")
    except (ValueError, FileNotFoundError, OSError):
        issues.append("Target Skill is missing or its path is invalid.")
    return original, candidate, diff, snapshot, issues


def _evaluation_digest(evaluation: dict[str, Any]) -> str:
    payload = {key: value for key, value in evaluation.items() if key != "record_sha256"}
    return sha256_bytes(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _validate_evaluated_proposal(root: Path, directory: Path, proposal: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    _, _, _, snapshot, artifact_issues = _artifact_state(root, directory, proposal)
    issues.extend(artifact_issues)
    evaluation = proposal.get("evaluation")
    if not isinstance(evaluation, dict):
        return issues + ["Proposal has no structured evaluation; evaluate it again before approval."]
    if evaluation.get("artifact_hashes") != snapshot:
        issues.append("Evaluation does not match the current baseline, candidate, and diff files.")
    if evaluation.get("record_sha256") != _evaluation_digest(evaluation):
        issues.append("Evaluation content changed after it was recorded.")
    try:
        report = (directory / "evaluation.md").read_bytes()
    except OSError:
        issues.append("Evaluation report is missing.")
    else:
        if sha256_bytes(report) != evaluation.get("report_sha256"):
            issues.append("Evaluation report changed after it was recorded.")
    return issues


def _proposal_dir(root: Path, proposal_id: str) -> Path:
    if not re.fullmatch(r"skill-[a-z0-9-]{3,100}", proposal_id):
        raise ValueError("invalid Skill Proposal ID")
    path = root / PROPOSAL_ROOT / proposal_id
    if not path.is_dir():
        raise FileNotFoundError(proposal_id)
    return path


def create_proposal(root: Path, skill_name: str, experience_ids: list[str], candidate_text: str, title: str = "") -> dict[str, Any]:
    root = root.resolve()
    target = _skill_file(root, skill_name)
    experiences = {item.get("experience_id"): item for item in list_experiences(root)}
    missing = sorted(set(experience_ids) - experiences.keys())
    if missing:
        raise ValueError("unknown Experience IDs: " + ", ".join(missing))
    original = target.read_bytes().decode("utf-8")
    if not candidate_text.strip():
        raise ValueError("candidate Skill content is empty")
    if candidate_text == original:
        raise ValueError("candidate is identical to the current Skill")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dt%H%M%Sz").lower()
    proposal_id = f"skill-{skill_name}-{stamp}-{sha256_bytes(candidate_text.encode())[:6]}"
    directory = root / PROPOSAL_ROOT / proposal_id
    directory.mkdir(parents=True, exist_ok=False)
    diff = _proposal_diff(skill_name, original, candidate_text)
    experience_summaries = [
        {"experience_id": item, "lesson": experiences[item].get("lesson", ""), "evidence_refs": experiences[item].get("evidence_refs", [])}
        for item in experience_ids
    ]
    proposal = {
        "schema_version": 1, "proposal_id": proposal_id, "title": title or f"Improve {skill_name}",
        "target_skill": skill_name, "target_path": str(target.relative_to(root)), "base_commit": _git_head(root),
        "base_hash": sha256_file(target), "experience_ids": experience_ids, "experience_summaries": experience_summaries,
        "problem": "Review the linked execution experience and determine whether this focused Skill edit addresses a reusable defect.",
        "suggested_change": "See candidate.md and changes.diff.", "expected_benefit": "Improve the observed task behavior with a minimal reusable instruction change.",
        "possible_side_effects": "May add context or constraints; evaluator should check for redundancy, conflicts, and loss of useful flexibility.",
        "status": "draft", "created_at": utc_now(), "candidate_hash": sha256_bytes(candidate_text.encode("utf-8")),
        "diff_hash": sha256_bytes(diff.encode("utf-8")),
        "applied_hash": None, "rollback": "restore the captured original.md only if current target hash still matches applied_hash",
    }
    atomic_write_text(directory / "original.md", original)
    atomic_write_text(directory / "candidate.md", candidate_text)
    atomic_write_text(directory / "changes.diff", diff)
    atomic_write_json(directory / "proposal.json", proposal)
    atomic_write_text(directory / "evaluation.md", "Not evaluated.\n")
    return proposal


def evaluate_proposal(root: Path, proposal_id: str) -> dict[str, Any]:
    directory = _proposal_dir(root.resolve(), proposal_id)
    proposal = read_json(directory / "proposal.json", {})
    if proposal.get("status") in {"approved", "applied", "rejected", "rolled_back"}:
        raise ValueError("terminal or approved Proposals cannot be re-evaluated")
    original, candidate, _, artifact_hashes, issues = _artifact_state(root.resolve(), directory, proposal)
    frontmatter = re.search(r"\A---\s*\n(.*?)\n---", candidate, re.S)
    declared_name = re.search(r"(?m)^name:\s*['\"]?([a-z0-9-]+)", frontmatter.group(1)) if frontmatter else None
    if not frontmatter or not declared_name:
        issues.append("Candidate lacks a parseable Skill frontmatter/name.")
    elif declared_name.group(1) != proposal.get("target_skill"):
        issues.append("Candidate Skill name does not match the target directory.")
    baseline_bytes = len(original.encode("utf-8"))
    candidate_bytes = len(candidate.encode("utf-8"))
    if candidate_bytes > baseline_bytes + max(250, int(baseline_bytes * 0.4)):
        issues.append("Candidate adds substantial text; simplify or justify the added instructions before approval.")
    original_rules = {line.strip() for line in original.splitlines() if line.strip().startswith(("- ", "1. "))}
    missing_rules = [line for line in original_rules if line not in candidate]
    result = "Regressed" if issues else "Inconclusive"
    if not issues and re.sub(r"\s+", " ", candidate).strip() == re.sub(r"\s+", " ", original).strip():
        result = "Equivalent"
    summary = [
        f"Result: **{result}** (static + retrospective only; no blind model execution).",
        "",
        "Static checks:",
        "- Target Skill path and candidate frontmatter checked.",
        f"- Candidate size: {candidate_bytes} bytes; baseline: {baseline_bytes} bytes.",
        f"- Baseline list rules not found verbatim in candidate: {len(missing_rules)}.",
        f"- Baseline/candidate/diff hashes: `{artifact_hashes['base_hash']}` / `{artifact_hashes['candidate_hash']}` / `{artifact_hashes['diff_hash']}`.",
        *([f"- Issue: {item}" for item in issues]),
        "",
        "Retrospective assessment:",
        "- The cited Experience records describe the historical problem and can be used to inspect whether the candidate addresses it.",
        "- This check does not execute the original and candidate Skills on a new task; it is not evidence of measured performance improvement.",
        "- A separate reviewer should inspect `changes.diff`, the linked evidence, and any removed rules before approval.",
    ]
    report_text = "\n".join(summary) + "\n"
    evaluation = {
        "result": result, "type": "static_and_retrospective", "evaluated_at": utc_now(),
        "issues": issues, "baseline_rules_not_verbatim": missing_rules[:30],
        "performance_claim": "not established",
        "artifact_hashes": artifact_hashes,
        "report_sha256": sha256_bytes(report_text.encode("utf-8")),
    }
    evaluation["record_sha256"] = _evaluation_digest(evaluation)
    proposal["status"] = "evaluated"
    proposal["evaluation"] = evaluation
    atomic_write_json(directory / "proposal.json", proposal)
    atomic_write_text(directory / "evaluation.md", report_text)
    return proposal


def change_status(root: Path, proposal_id: str, status: str, note: str = "") -> dict[str, Any]:
    directory = _proposal_dir(root.resolve(), proposal_id)
    path = directory / "proposal.json"
    proposal = read_json(path, {})
    if status == "approved":
        if proposal.get("status") != "evaluated":
            raise ValueError("evaluate the Proposal before approval")
        if proposal.get("evaluation", {}).get("result") == "Regressed":
            raise ValueError("a regressed Proposal cannot be approved")
        issues = _validate_evaluated_proposal(root.resolve(), directory, proposal)
        if issues:
            raise RuntimeError("Proposal artifacts/evaluation are stale or inconsistent: " + "; ".join(issues[:5]))
        proposal["approved_at"] = utc_now()
        proposal["approval_note"] = note
    elif status == "rejected":
        if proposal.get("status") in {"applied", "rolled_back"}:
            raise ValueError("an applied Proposal cannot be rejected")
        proposal["rejected_at"] = utc_now()
        proposal["rejection_note"] = note
    proposal["status"] = status
    atomic_write_json(path, proposal)
    return proposal


def apply_proposal(root: Path, proposal_id: str) -> dict[str, Any]:
    root = root.resolve()
    directory = _proposal_dir(root, proposal_id)
    path = directory / "proposal.json"
    proposal = read_json(path, {})
    if proposal.get("status") != "approved":
        raise ValueError("apply requires an explicitly approved Proposal")
    if proposal.get("evaluation", {}).get("result") == "Regressed":
        raise ValueError("a regressed Proposal cannot be applied")
    issues = _validate_evaluated_proposal(root, directory, proposal)
    if issues:
        raise RuntimeError("Proposal artifacts/evaluation are stale or inconsistent: " + "; ".join(issues[:5]))
    _, candidate, _, _, _ = _artifact_state(root, directory, proposal)
    target = root / proposal["target_path"]
    atomic_write_text(target, candidate, mode=target.stat().st_mode & 0o777)
    proposal["status"] = "applied"
    proposal["applied_at"] = utc_now()
    proposal["applied_hash"] = sha256_file(target)
    proposal["applied_commit_before"] = _git_head(root)
    atomic_write_json(path, proposal)
    return proposal


def rollback_proposal(root: Path, proposal_id: str) -> dict[str, Any]:
    root = root.resolve()
    directory = _proposal_dir(root, proposal_id)
    path = directory / "proposal.json"
    proposal = read_json(path, {})
    if proposal.get("status") != "applied":
        raise ValueError("only an applied Proposal can be rolled back")
    target = root / proposal["target_path"]
    if sha256_file(target) != proposal.get("applied_hash"):
        raise RuntimeError("Skill changed after application; refusing to overwrite later edits")
    original = (directory / "original.md").read_bytes().decode("utf-8")
    if sha256_bytes(original.encode("utf-8")) != proposal.get("base_hash"):
        raise RuntimeError("saved rollback copy does not match the original base hash")
    atomic_write_text(target, original, mode=target.stat().st_mode & 0o777)
    proposal["status"] = "rolled_back"
    proposal["rolled_back_at"] = utc_now()
    proposal["rollback_hash"] = sha256_file(target)
    atomic_write_json(path, proposal)
    return proposal


def list_proposals(root: Path) -> list[dict[str, Any]]:
    rows = []
    for path in sorted((root / PROPOSAL_ROOT).glob("*/proposal.json")):
        value = read_json(path, {})
        if value:
            rows.append({key: value.get(key) for key in ("proposal_id", "target_skill", "title", "status", "created_at", "evaluation")})
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create, evaluate, approve, apply, reject, or roll back a Skill Proposal.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list")
    show = commands.add_parser("show")
    show.add_argument("proposal_id")
    draft = commands.add_parser("draft")
    draft.add_argument("--skill", required=True)
    draft.add_argument("--experience", action="append", required=True)
    draft.add_argument("--candidate", type=Path, required=True, help="candidate SKILL.md generated for review; formal Skill is not modified")
    draft.add_argument("--title", default="")
    for command in ("evaluate", "approve", "reject", "apply", "rollback"):
        sub = commands.add_parser(command)
        sub.add_argument("proposal_id")
        if command in {"approve", "reject"}:
            sub.add_argument("--note", default="")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "list":
        print(json.dumps(list_proposals(root), ensure_ascii=False, indent=2))
    elif args.command == "show":
        directory = _proposal_dir(root, args.proposal_id)
        print(json.dumps(read_json(directory / "proposal.json", {}), ensure_ascii=False, indent=2))
        print((directory / "changes.diff").read_text(encoding="utf-8"))
        print((directory / "evaluation.md").read_text(encoding="utf-8"))
    elif args.command == "draft":
        proposal = create_proposal(root, args.skill, args.experience, args.candidate.read_text(encoding="utf-8"), args.title)
        print(json.dumps(proposal, ensure_ascii=False, indent=2))
    elif args.command == "evaluate":
        print(json.dumps(evaluate_proposal(root, args.proposal_id), ensure_ascii=False, indent=2))
    elif args.command in {"approve", "reject"}:
        print(json.dumps(change_status(root, args.proposal_id, "approved" if args.command == "approve" else "rejected", args.note), ensure_ascii=False, indent=2))
    elif args.command == "apply":
        print(json.dumps(apply_proposal(root, args.proposal_id), ensure_ascii=False, indent=2))
    else:
        print(json.dumps(rollback_proposal(root, args.proposal_id), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
