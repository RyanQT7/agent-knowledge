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
    original = target.read_text(encoding="utf-8")
    if not candidate_text.strip():
        raise ValueError("candidate Skill content is empty")
    if candidate_text == original:
        raise ValueError("candidate is identical to the current Skill")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dt%H%M%Sz").lower()
    proposal_id = f"skill-{skill_name}-{stamp}-{sha256_bytes(candidate_text.encode())[:6]}"
    directory = root / PROPOSAL_ROOT / proposal_id
    directory.mkdir(parents=True, exist_ok=False)
    diff = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), candidate_text.splitlines(keepends=True),
        fromfile=f"a/skills/{skill_name}/SKILL.md", tofile=f"b/skills/{skill_name}/SKILL.md",
    ))
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
    original = (directory / "original.md").read_text(encoding="utf-8")
    candidate = (directory / "candidate.md").read_text(encoding="utf-8")
    issues = []
    frontmatter = re.search(r"\A---\s*\n(.*?)\n---", candidate, re.S)
    declared_name = re.search(r"(?m)^name:\s*['\"]?([a-z0-9-]+)", frontmatter.group(1)) if frontmatter else None
    if not frontmatter or not declared_name:
        issues.append("Candidate lacks a parseable Skill frontmatter/name.")
    elif declared_name.group(1) != proposal.get("target_skill"):
        issues.append("Candidate Skill name does not match the target directory.")
    try:
        target = _skill_file(root, str(proposal.get("target_skill", "")))
        target_matches = str(target.relative_to(root)) == proposal.get("target_path") and target.is_file() and sha256_file(target) == proposal.get("base_hash")
    except (ValueError, FileNotFoundError):
        target_matches = False
    if not target_matches:
        issues.append("Target Skill changed since this Proposal was created; regenerate the candidate against the current version.")
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
        *([f"- Issue: {item}" for item in issues]),
        "",
        "Retrospective assessment:",
        "- The cited Experience records describe the historical problem and can be used to inspect whether the candidate addresses it.",
        "- This check does not execute the original and candidate Skills on a new task; it is not evidence of measured performance improvement.",
        "- A separate reviewer should inspect `changes.diff`, the linked evidence, and any removed rules before approval.",
    ]
    proposal["status"] = "evaluated"
    proposal["evaluation"] = {
        "result": result, "type": "static_and_retrospective", "evaluated_at": utc_now(),
        "issues": issues, "baseline_rules_not_verbatim": missing_rules[:30],
        "performance_claim": "not established",
    }
    atomic_write_json(directory / "proposal.json", proposal)
    atomic_write_text(directory / "evaluation.md", "\n".join(summary) + "\n")
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
    target = root / proposal["target_path"]
    if proposal.get("target_path") != f"skills/{proposal.get('target_skill')}/SKILL.md":
        raise ValueError("Proposal target path no longer matches its Skill name")
    if not target.resolve().is_relative_to((root / "skills").resolve()):
        raise ValueError("target path escapes skills/")
    if sha256_file(target) != proposal.get("base_hash"):
        raise RuntimeError("Skill changed since Proposal creation; approval is stale")
    candidate = (directory / "candidate.md").read_text(encoding="utf-8")
    if sha256_bytes(candidate.encode("utf-8")) != proposal.get("candidate_hash"):
        raise RuntimeError("candidate changed since evaluation")
    diff = (directory / "changes.diff").read_text(encoding="utf-8")
    if sha256_bytes(diff.encode("utf-8")) != proposal.get("diff_hash"):
        raise RuntimeError("review diff changed since evaluation")
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
    original = (directory / "original.md").read_text(encoding="utf-8")
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
