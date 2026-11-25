from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from scripts.evolution.common import (
    EVOLUTION, ROOT, atomic_write_json, file_lock, read_json,
    safe_relative_path, sha256_file, utc_now,
)

PROPOSAL_DIR = EVOLUTION / "proposals"
DIFF_PATH_RE = re.compile(r"^(?:diff --git a/|--- a/|\+\+\+ b/)(.+?)(?:\s|$)", re.M)
ADDED_PATH_RE = re.compile(r"^--- /dev/null\s*\n\+\+\+ b/(.+?)(?:\t|$)", re.M)


def _git_value(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def patch_paths(patch: str) -> set[str]:
    return {match.group(1).replace("\\ ", " ") for match in DIFF_PATH_RE.finditer(patch) if match.group(1) != "/dev/null"}


def patch_added_paths(patch: str) -> set[str]:
    return {match.group(1).replace("\\ ", " ") for match in ADDED_PATH_RE.finditer(patch)}


def validate_proposal(proposal: dict[str, Any], root: Path = ROOT, check_hashes: bool = True) -> list[str]:
    errors: list[str] = []
    for required in ("proposal_id", "title", "run_id", "research_focus", "created_at", "status", "evidence", "files", "base_hashes", "base_revision", "patch", "uncertainties", "rollback"):
        if required not in proposal:
            errors.append(f"missing {required}")
    files = proposal.get("files")
    if not isinstance(files, list) or not files:
        errors.append("files must be a non-empty list")
        files = []
    if len(files) > 3:
        errors.append("a proposal may change at most 3 files")
    normalized: set[str] = set()
    patch = proposal.get("patch") if isinstance(proposal.get("patch"), str) else ""
    added_paths = patch_added_paths(patch)
    for raw in files:
        path, error = safe_relative_path(str(raw), root)
        if error:
            errors.append(f"invalid proposal path {raw!r}: {error}")
        elif path:
            normalized.add(path)
            target = root / path
            expected = proposal.get("base_hashes", {}).get(path, "__missing_key__")
            if expected == "ABSENT":
                if path not in added_paths:
                    errors.append(f"new proposal target is not a /dev/null addition: {path}")
                if target.exists():
                    errors.append(f"new proposal target already exists: {path}; approval is stale")
            elif expected == "__missing_key__" or not expected:
                errors.append(f"missing base hash for {path}")
            elif not target.is_file():
                errors.append(f"proposal target does not exist: {path}")
            elif check_hashes and sha256_file(target) != expected:
                errors.append(f"base hash changed for {path}; approval is stale")
    if not isinstance(proposal.get("base_hashes"), dict):
        errors.append("base_hashes must be an object")
    patch = proposal.get("patch")
    if not isinstance(patch, str) or not patch.strip():
        errors.append("patch must contain a unified diff")
    else:
        changed = patch_paths(patch)
        if changed != normalized:
            errors.append(f"patch paths {sorted(changed)} do not match declared files {sorted(normalized)}")
    evidence = proposal.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append("evidence must contain at least one source reference")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence[{index}] must be an object")
                continue
            for key in ("source_id", "source_version", "source_uri", "locator", "relation", "accessed_at"):
                if not item.get(key):
                    errors.append(f"evidence[{index}] missing {key}")
            if item.get("relation") not in {"supports", "qualifies", "contradicts", "supersedes", "related_to"}:
                errors.append(f"evidence[{index}] has invalid relation")
    if not isinstance(proposal.get("depends_on", []), list):
        errors.append("depends_on must be a list")
    for key in ("uncertainties",):
        if not isinstance(proposal.get(key), list):
            errors.append(f"{key} must be a list")
    return errors


def create_proposal(
    *, proposal_id: str, title: str, run_id: str, research_focus: str,
    files: list[str], patch_file: Path, evidence: list[dict[str, Any]],
    related_questions: list[str] | None = None, affected_claims: list[str] | None = None,
    uncertainties: list[str] | None = None, impact_scope: str = "",
    source_branch: str | None = None, source_commit: str | None = None,
    depends_on: list[str] | None = None,
    root: Path = ROOT,
) -> Path:
    with file_lock(root / "evolution" / "state" / ".evolution.lock"):
        normalized_files: list[str] = []
        for raw in files:
            normalized, error = safe_relative_path(raw, root)
            if error:
                raise ValueError(f"invalid proposal path {raw!r}: {error}")
            assert normalized is not None
            normalized_files.append(normalized)
        if len(set(normalized_files)) != len(normalized_files):
            raise ValueError("proposal files must be unique")
        patch = patch_file.read_text(encoding="utf-8")
        proposal = {
            "schema_version": 1,
            "proposal_id": proposal_id,
            "title": title,
            "run_id": run_id,
            "research_focus": research_focus,
            "related_questions": related_questions or [],
            "affected_claims": affected_claims or [],
            "depends_on": depends_on or [],
            "created_at": utc_now(),
            "status": "draft",
            "evidence": evidence,
            "files": normalized_files,
            "base_hashes": {path: sha256_file(root / path) if (root / path).is_file() else "ABSENT" for path in normalized_files},
            "base_revision": _git_value(root, "rev-parse", "HEAD"),
            "source_branch": source_branch or "unavailable",
            "source_commit": source_commit or "unavailable",
            "before": {path: (root / path).read_text(encoding="utf-8") if (root / path).is_file() else None for path in normalized_files},
            "patch": patch,
            "change_reason": title,
            "impact_scope": impact_scope,
            "uncertainties": uncertainties or [],
            "rollback": "After an approved commit, revert that commit; before commit, restore only the listed files from the recorded base revision.",
            "approval": None,
        }
        errors = validate_proposal(proposal, root, check_hashes=True)
        if errors:
            raise ValueError("proposal validation failed: " + "; ".join(errors))
        path = root / "evolution" / "proposals" / f"{proposal_id}.json"
        if path.exists():
            existing = read_json(path, {})
            idempotency_fields = ("title", "run_id", "research_focus", "evidence", "files", "base_hashes", "depends_on", "patch")
            if all(existing.get(key) == proposal.get(key) for key in idempotency_fields):
                return path
            raise FileExistsError(f"proposal id already exists with different content: {proposal_id}")
        atomic_write_json(path, proposal)
        return path


def approve_proposal(proposal_path: Path, approved_by: str, approval_note: str, root: Path = ROOT) -> dict[str, Any]:
    proposal = read_json(proposal_path, None)
    if not isinstance(proposal, dict):
        raise FileNotFoundError(proposal_path)
    errors = validate_proposal(proposal, root, check_hashes=True)
    if errors:
        raise ValueError("proposal is not approvable: " + "; ".join(errors))
    if not approved_by.strip() or not approval_note.strip():
        raise ValueError("approval requires a reviewer name and explicit approval note")
    proposal["status"] = "approved"
    proposal["approval"] = {"approved_by": approved_by.strip(), "note": approval_note.strip(), "approved_at": utc_now(), "patch_sha256": __import__("hashlib").sha256(proposal["patch"].encode()).hexdigest()}
    atomic_write_json(proposal_path, proposal)
    return proposal


def apply_proposal(proposal_path: Path, approved_by: str, approval_note: str, root: Path = ROOT) -> dict[str, Any]:
    with file_lock(root / "evolution" / "state" / ".evolution.lock"):
        proposal = read_json(proposal_path, None)
        if not isinstance(proposal, dict):
            raise FileNotFoundError(proposal_path)
        errors = validate_proposal(proposal, root, check_hashes=True)
        if errors:
            raise ValueError("proposal is not applicable: " + "; ".join(errors))
        for dependency_id in proposal.get("depends_on", []):
            dependency_path = root / "evolution" / "proposals" / f"{dependency_id}.json"
            dependency = read_json(dependency_path, None)
            if not isinstance(dependency, dict) or dependency.get("status") != "applied":
                raise ValueError(f"proposal dependency is not applied: {dependency_id}")
        if not approved_by.strip() or not approval_note.strip():
            raise ValueError("apply requires explicit human approval identity and note")
        if proposal.get("status") not in {"approved", "draft"}:
            raise ValueError(f"proposal status is not applicable: {proposal.get('status')}")
        if proposal.get("status") == "draft":
            proposal["status"] = "approved"
            proposal["approval"] = {"approved_by": approved_by.strip(), "note": approval_note.strip(), "approved_at": utc_now(), "patch_sha256": __import__("hashlib").sha256(proposal["patch"].encode()).hexdigest()}
            atomic_write_json(proposal_path, proposal)
        elif proposal.get("approval", {}).get("patch_sha256") != __import__("hashlib").sha256(proposal["patch"].encode()).hexdigest():
            raise ValueError("approved patch hash does not match the stored diff")
        changed_paths = proposal["files"]
        status = subprocess.run(["git", "status", "--porcelain", "--", *changed_paths], cwd=root, text=True, capture_output=True, check=True)
        if status.stdout.strip():
            raise ValueError("target knowledge files have local changes; refusing to overwrite")
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".patch", delete=False) as handle:
            handle.write(proposal["patch"])
            patch_path = Path(handle.name)
        try:
            subprocess.run(["git", "apply", "--check", str(patch_path)], cwd=root, check=True, capture_output=True, text=True)
            subprocess.run(["git", "apply", str(patch_path)], cwd=root, check=True, capture_output=True, text=True)
        finally:
            patch_path.unlink(missing_ok=True)
        proposal["status"] = "applied"
        proposal["applied_at"] = utc_now()
        proposal["applied_hashes"] = {path: sha256_file(root / path) for path in changed_paths}
        atomic_write_json(proposal_path, proposal)
        return proposal


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture, validate, explicitly approve, or apply a knowledge proposal.")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("check")
    check.add_argument("proposal", type=Path)
    create = commands.add_parser("create")
    create.add_argument("--id", required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--run-id", required=True)
    create.add_argument("--focus", required=True)
    create.add_argument("--file", action="append", dest="files", required=True)
    create.add_argument("--patch-file", required=True, type=Path)
    create.add_argument("--evidence-file", required=True, type=Path, help="JSON array with source_id/version/uri/locator/relation/accessed_at")
    create.add_argument("--source-branch")
    create.add_argument("--source-commit")
    create.add_argument("--depends-on", action="append", default=[])
    approve = commands.add_parser("approve")
    approve.add_argument("proposal", type=Path)
    approve.add_argument("--approved-by", required=True)
    approve.add_argument("--note", required=True)
    apply = commands.add_parser("apply")
    apply.add_argument("proposal", type=Path)
    apply.add_argument("--approved-by", required=True)
    apply.add_argument("--note", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            evidence = json.loads(args.evidence_file.read_text(encoding="utf-8"))
            result = create_proposal(proposal_id=args.id, title=args.title, run_id=args.run_id, research_focus=args.focus, files=args.files, patch_file=args.patch_file, evidence=evidence, source_branch=args.source_branch, source_commit=args.source_commit, depends_on=args.depends_on)
            print(result.relative_to(ROOT))
        elif args.command == "check":
            proposal = read_json(args.proposal, None)
            errors = validate_proposal(proposal or {})
            print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
            return 0 if not errors else 1
        elif args.command == "approve":
            result = approve_proposal(args.proposal, args.approved_by, args.note)
            print(f"approved: {result['proposal_id']}")
        else:
            result = apply_proposal(args.proposal, args.approved_by, args.note)
            print(f"applied: {result['proposal_id']}")
    except Exception as exc:
        print(f"proposal operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
