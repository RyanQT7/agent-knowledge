from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from scripts.evolution.common import (
    EVOLUTION, ROOT, CLAIM_RELATIONS, STATUS_VALUES, atomic_write_json, atomic_write_text,
    extract_paper_identity, normalize_arxiv, normalize_doi, read_jsonl,
    resolve_local_path, utc_now, validate_claim,
)

CLAIMS_PATH = EVOLUTION / "claims" / "claims.jsonl"
CANDIDATES_PATH = EVOLUTION / "inbox" / "candidates.jsonl"
AUDIT_DIR = EVOLUTION / "audits"

LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\((<[^>]+>|[^)]+)\)")
HTTP_RE = re.compile(r"https?://[^\s)>\]]+", re.I)
SHA_RE = re.compile(r"\b[0-9a-f]{40}\b", re.I)
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|PLACEHOLDER|Not yet written|待补充|待填写)\b", re.I)


def markdown_links(text: str) -> list[str]:
    visible_lines: list[str] = []
    fence_char: str | None = None
    fence_width = 0
    for line in text.splitlines():
        opening = re.match(r"^[ \t]*(`{3,}|~{3,})", line)
        if fence_char is not None:
            closing = re.match(r"^[ \t]*(`{3,}|~{3,})[ \t]*$", line)
            if closing and closing.group(1)[0] == fence_char and len(closing.group(1)) >= fence_width:
                fence_char = None
                fence_width = 0
            continue
        if opening:
            fence_char = opening.group(1)[0]
            fence_width = len(opening.group(1))
            continue
        visible_lines.append(line)
    visible = "\n".join(visible_lines)
    # Links written as examples in inline-code spans are not navigable links.
    visible = re.sub(r"(?<!`)`+[^`\n]*`+(?!`)", "", visible)
    links = []
    for match in LINK_RE.finditer(visible):
        raw = match.group(1).strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1]
        raw = raw.split()[0] if raw else raw
        links.append(raw)
    return links


def _resolve_from_document(root: Path, document: Path, raw: str) -> Path | None:
    value = raw.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
    if not value or value.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    from urllib.parse import unquote
    value = unquote(value)
    target = (root / value.lstrip("/")).resolve() if value.startswith("/") else (document.parent / value).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def _finding(file: str, issue_type: str, impact: str, confidence: str, action: str, evidence: str, claim: str = "") -> dict[str, Any]:
    return {
        "finding_id": "finding-" + __import__("hashlib").sha256(f"{file}|{issue_type}|{claim}|{evidence}".encode()).hexdigest()[:14],
        "finding": issue_type.replace("_", " ").capitalize(),
        "affected_file": file,
        "affected_claim": claim or None,
        "evidence": evidence,
        "issue_type": issue_type,
        "impact": impact,
        "confidence": confidence,
        "suggested_action": action,
    }


def _markdown_paths(root: Path) -> list[Path]:
    excluded_parts = {".git", ".venv", "__pycache__", "node_modules"}
    result = []
    for path in root.rglob("*.md"):
        rel = path.relative_to(root)
        if excluded_parts.intersection(rel.parts) or rel.parts[:2] == ("sources", "code"):
            continue
        if path.is_file():
            result.append(path)
    return sorted(result)


def _check_links(root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    findings = []
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        for link in markdown_links(text):
            target = _resolve_from_document(root, path, link)
            if target is not None and not target.exists():
                findings.append(_finding(rel, "broken_internal_link", "medium", "high", "Repair the destination or remove the stale link after checking its history.", link))
    return findings


def _check_index(root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    index_path = root / "INDEX.md"
    if not index_path.exists():
        return [_finding("INDEX.md", "missing_index", "high", "high", "Restore the root knowledge index.", "INDEX.md is absent")]
    reachable = {index_path.resolve()}
    pending = [index_path.resolve()]
    documents = {path.resolve(): path for path in paths}
    while pending:
        document = pending.pop()
        path = documents.get(document)
        if not path:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw in markdown_links(text):
            target = _resolve_from_document(root, path, raw)
            if target and target.suffix.lower() == ".md" and target.resolve() in documents and target.resolve() not in reachable:
                reachable.add(target.resolve())
                pending.append(target.resolve())
    for path in paths:
        rel = path.relative_to(root).as_posix()
        # The real index deliberately delegates to papers/README and concept
        # subindexes; report only when an entry is unreachable from INDEX.
        if rel.startswith(("papers/", "concepts/")) and path.resolve() not in reachable:
            findings.append(_finding(rel, "not_indexed", "low", "high", "Link this maintained knowledge entry from INDEX.md or an index already reachable from it.", f"No path of local Markdown links from INDEX.md reaches {rel}"))
    return findings


def _check_papers(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for path in sorted((root / "papers").glob("**/notes.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        record = extract_paper_identity(text, rel)
        doi = normalize_doi(record.get("doi"))
        arxiv_base, _ = normalize_arxiv(record.get("arxiv_id"))
        key = f"doi:{doi}" if doi else f"arxiv:{arxiv_base}" if arxiv_base else None
        if key:
            groups[key].append(record)
        elif not record.get("title") or not HTTP_RE.search(text):
            findings.append(_finding(rel, "missing_source", "high", "medium", "Verify the primary paper identity and add DOI/arXiv/publisher source links.", "Paper note has no detectable stable identifier or primary source URL."))
        if len(text.strip()) < 120 or PLACEHOLDER_RE.search(text[:3000]):
            findings.append(_finding(rel, "empty_or_placeholder_note", "medium", "medium", "Confirm whether the note is intentionally a stub, then finish or label its reading status.", "Note is unusually short or contains an explicit placeholder."))
    for key, records in groups.items():
        unique_paths = sorted({record["path"] for record in records})
        if len(unique_paths) > 1:
            for rel in unique_paths:
                findings.append(_finding(rel, "duplicate_paper_identity", "high", "high", "Review the identity records and cross-link or consolidate notes without deleting history.", f"Stable identifier {key} appears in: {', '.join(unique_paths)}"))
    return findings


def _check_concepts(root: Path, paths: list[Path]) -> list[dict[str, Any]]:
    concept_paths = sorted((root / "concepts").glob("**/*.md"))
    inbound: dict[Path, int] = defaultdict(int)
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        for link in markdown_links(text):
            target = _resolve_from_document(root, path, link)
            if target and target.resolve() in {p.resolve() for p in concept_paths}:
                inbound[target.resolve()] += 1
    findings = []
    for path in concept_paths:
        if path.name.lower() == "readme.md":
            continue
        if not inbound[path.resolve()]:
            rel = path.relative_to(root).as_posix()
            findings.append(_finding(rel, "orphan_concept", "low", "medium", "Check whether INDEX.md or other Concepts should link here; do not add a link just to raise graph degree.", "No inbound Markdown link was found."))
    return findings


def _check_code_notes(root: Path) -> list[dict[str, Any]]:
    findings = []
    for path in sorted((root / "code").glob("**/notes.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(root).as_posix()
        has_repo = bool(re.search(r"https?://github\.com/[\w.-]+/[\w.-]+", text, re.I))
        has_sha = bool(SHA_RE.search(text))
        if not has_repo or not has_sha:
            missing = ", ".join(name for name, present in (("repository URL", has_repo), ("full 40-character commit SHA", has_sha)) if not present)
            findings.append(_finding(rel, "incomplete_paper_code_mapping", "medium", "high", "Pin the repository URL and exact commit, or mark the mapping as unavailable/unclear.", f"Missing {missing}."))
    return findings


def _check_claims(root: Path) -> list[dict[str, Any]]:
    path = root / "evolution" / "claims" / "claims.jsonl"
    claims = read_jsonl(path)
    findings: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    source_urls: dict[str, set[str]] = defaultdict(set)
    latest_candidate_versions: dict[str, str] = {}
    for row in read_jsonl(root / "evolution" / "inbox" / "candidates.jsonl"):
        base, version = normalize_arxiv(row.get("arxiv_id"))
        if base and version and row.get("event_type") == "version_update":
            previous = latest_candidate_versions.get(base)
            if not previous or int(re.search(r"v(\d+)$", version).group(1)) > int(re.search(r"v(\d+)$", previous).group(1)):
                latest_candidate_versions[base] = version
    by_id = {str(item.get("claim_id")): item for item in claims if item.get("claim_id")}
    for line_number, claim in enumerate(claims, start=1):
        claim_id = str(claim.get("claim_id", ""))
        if claim_id in seen:
            findings.append(_finding("evolution/claims/claims.jsonl", "duplicate_claim_id", "high", "high", "Assign stable unique IDs and merge duplicate records without losing evidence.", f"Claim ID {claim_id} appears on lines {seen[claim_id]} and {line_number}.", claim_id))
        else:
            seen[claim_id] = line_number
        errors = validate_claim(claim)
        for error in errors:
            findings.append(_finding("evolution/claims/claims.jsonl", "invalid_claim_schema", "high", "high", "Correct the claim record before treating it as active knowledge.", f"line {line_number}: {error}", claim_id))
        for evidence in claim.get("evidence", []) if isinstance(claim.get("evidence"), list) else []:
            if isinstance(evidence, dict) and evidence.get("source_id") and evidence.get("source_uri"):
                source_urls[str(evidence["source_id"])].add(str(evidence["source_uri"]))
                base, claim_version = normalize_arxiv(evidence.get("source_version"))
                latest = latest_candidate_versions.get(base or "")
                if latest and claim_version and int(re.search(r"v(\d+)$", latest).group(1)) > int(re.search(r"v(\d+)$", claim_version).group(1)):
                    findings.append(_finding("evolution/claims/claims.jsonl", "stale_source_version", "medium", "high", "Review the new source version; retain the earlier evidence and update the claim only if the paper changed relevant content.", f"Claim cites {claim_version}; discovery records {latest} for arXiv {base}.", claim_id))
        relations = {item.get("relation") for item in claim.get("evidence", []) if isinstance(item, dict)}
        if "contradicts" in relations and claim.get("status") != "contested":
            findings.append(_finding("evolution/claims/claims.jsonl", "unresolved_claim_conflict", "high", "high", "Compare definition, scope, dataset, assumptions, and version; mark contested until resolved.", "A cited evidence relation says contradicts, but claim status is not contested.", claim_id))
        if "qualifies" in relations:
            findings.append(_finding("evolution/claims/claims.jsonl", "scope_qualification", "low", "high", "Record the limiting scope and preserve both evidence sources; do not treat qualification as a direct contradiction.", "A cited evidence relation says qualifies.", claim_id))
        if "supersedes" in relations and (claim.get("status") != "superseded" or not claim.get("supersedes")):
            findings.append(_finding("evolution/claims/claims.jsonl", "invalid_supersession", "medium", "high", "Link the old claim and mark its status superseded, or change the relation if it only qualifies it.", "Evidence says supersedes but claim status/linkage is incomplete.", claim_id))
        for related_id in claim.get("related_claims", []) if isinstance(claim.get("related_claims"), list) else []:
            if related_id not in by_id:
                findings.append(_finding("evolution/claims/claims.jsonl", "unknown_related_claim", "medium", "high", "Repair the claim reference or add the missing stable claim record.", f"related_claims refers to unknown ID {related_id}.", claim_id))
    for source_id, urls in source_urls.items():
        if len(urls) > 1:
            findings.append(_finding("evolution/claims/claims.jsonl", "source_id_uri_mismatch", "medium", "high", "Resolve whether these are versions of one source or separate sources, then normalize source_id.", f"Source ID {source_id} maps to multiple URIs: {', '.join(sorted(urls))}"))
    return findings


def _check_candidates(root: Path) -> list[dict[str, Any]]:
    path = root / "evolution" / "inbox" / "candidates.jsonl"
    rows = read_jsonl(path)
    findings = []
    seen_ids: dict[str, int] = {}
    for line, row in enumerate(rows, start=1):
        candidate_id_value = str(row.get("candidate_id", ""))
        required = (
            "candidate_id", "title", "authors", "publication_date", "publication_status", "venue",
            "doi", "arxiv_id", "source_url", "source_version", "discovered_at", "research_topic",
            "related_questions", "related_concepts", "official_repository", "novelty_reason",
            "relevance_reason", "priority", "status",
        )
        missing = [field for field in required if field not in row]
        if missing:
            findings.append(_finding("evolution/inbox/candidates.jsonl", "invalid_candidate_schema", "medium", "high", "Complete the metadata-only candidate schema before screening or keep the record out of the queue.", f"line {line}: missing {', '.join(missing)}", candidate_id_value))
        if row.get("status") not in STATUS_VALUES:
            findings.append(_finding("evolution/inbox/candidates.jsonl", "invalid_candidate_status", "medium", "high", "Use one of the documented candidate statuses and record a reason for the decision.", f"line {line}: invalid status {row.get('status')!r}", candidate_id_value))
        if candidate_id_value in seen_ids:
            findings.append(_finding("evolution/inbox/candidates.jsonl", "duplicate_candidate_id", "high", "high", "Merge duplicate candidate records and preserve version events.", f"Candidate ID {candidate_id_value} occurs on lines {seen_ids[candidate_id_value]} and {line}."))
        else:
            seen_ids[candidate_id_value] = line
        if row.get("status") in {"discovered", "screened", "queued", "blocked"}:
            findings.append(_finding("evolution/inbox/candidates.jsonl", "unprocessed_candidate", "low", "high", "Screen, queue, defer, or reject with a reason; do not force a paper read.", f"{candidate_id_value}: {row.get('title')} [{row.get('status')}]"))
    return findings


def _check_questions(root: Path) -> list[dict[str, Any]]:
    path = root / "notes" / "questions.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    open_count = len(re.findall(r"\|\s*(?:Open|Partially Answered)\s*\|", text, re.I))
    if open_count:
        return [_finding("notes/questions.md", "open_research_questions", "low", "high", "Use open questions as discovery signals; retain historical status and evidence links.", f"Found {open_count} open or partially answered items; semantic status is not inferred automatically.")]
    return []


def audit(root: Path = ROOT, run_id: str | None = None) -> dict[str, Any]:
    paths = _markdown_paths(root)
    findings = []
    findings.extend(_check_links(root, paths))
    findings.extend(_check_index(root, paths))
    findings.extend(_check_papers(root))
    findings.extend(_check_concepts(root, paths))
    findings.extend(_check_code_notes(root))
    findings.extend(_check_claims(root))
    findings.extend(_check_candidates(root))
    findings.extend(_check_questions(root))
    # A zero byte Markdown file is checked separately so it is never hidden by
    # the minimum-length paper check.
    for path in paths:
        if path.stat().st_size == 0:
            findings.append(_finding(path.relative_to(root).as_posix(), "empty_file", "medium", "high", "Populate the document or remove it after confirming it is not user data.", "File size is zero bytes."))
    result = {
        "run_id": run_id,
        "status": "complete",
        "created_at": utc_now(),
        "files_scanned": len(paths),
        "claims_scanned": len(read_jsonl(root / "evolution" / "claims" / "claims.jsonl")),
        "candidates_scanned": len(read_jsonl(root / "evolution" / "inbox" / "candidates.jsonl")),
        "finding_count": len(findings),
        "findings": findings,
        "semantic_scope": "LLM/manual semantic review is performed by skills/knowledge-audit/SKILL.md on a bounded set of at most 10 relevant pages; this script is deterministic only.",
    }
    audit_dir = root / "evolution" / "audits"
    audit_dir.mkdir(parents=True, exist_ok=True)
    basename = run_id or f"audit-{result['created_at'].replace(':', '').replace('-', '')}"
    json_path = audit_dir / f"{basename}.json"
    md_path = audit_dir / f"{basename}.md"
    atomic_write_json(json_path, result)
    lines = [f"# Knowledge Audit — {basename}", "", f"- Created: {result['created_at']}", f"- Files scanned: {len(paths)}", f"- Deterministic findings: {len(findings)}", "", "## Findings", ""]
    if not findings:
        lines.append("No deterministic findings.")
    for item in findings:
        lines.extend([
            f"### {item['finding_id']} — {item['finding']}",
            f"- Finding: {item['finding']}",
            f"- Affected file: `{item['affected_file']}`",
            f"- Affected claim: {item['affected_claim'] or 'N/A'}",
            f"- Evidence: {item['evidence']}",
            f"- Issue type: `{item['issue_type']}`",
            f"- Impact: {item['impact']}",
            f"- Confidence: {item['confidence']}",
            f"- Suggested action: {item['suggested_action']}",
            "",
        ])
    lines.extend(["## Semantic review boundary", "", result["semantic_scope"], ""])
    atomic_write_text(md_path, "\n".join(lines))
    result["json_report"] = json_path.relative_to(root).as_posix()
    result["markdown_report"] = md_path.relative_to(root).as_posix()
    return result


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a read-only deterministic Markdown and evidence audit.")
    parser.add_argument("--run-id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = audit(run_id=args.run_id)
    except Exception as exc:
        print(f"audit failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"Audit complete: {result['finding_count']} deterministic findings across {result['files_scanned']} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
