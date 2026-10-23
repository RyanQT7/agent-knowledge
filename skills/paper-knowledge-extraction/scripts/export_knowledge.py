#!/usr/bin/env python3
"""Validate structured paper dossiers and build portable knowledge exports."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any
from urllib.parse import unquote


RECORD_PATTERN = re.compile(
    r"<!-- paper-knowledge-record:start -->\s*```json\s*(\{.*?\})\s*```\s*<!-- paper-knowledge-record:end -->",
    re.DOTALL,
)
REQUIRED_FIELDS = {
    "schema_version", "paper_id", "title_en", "title_zh", "authors", "year", "venue",
    "ccf_level", "ccf_provenance", "pdf_path", "reading_note_path", "knowledge_card_path", "code_url",
    "research_area", "method_tags", "research_scenario", "research_problem", "core_challenges",
    "existing_method_limits", "core_idea", "technical_innovations", "methodology",
    "experimental_evidence", "limitations", "research_implications", "related_papers",
    "evidence_references", "provenance",
}
REQUIRED_SECTIONS = [
    "## 1. Basic Information", "## 2. Research Scenario", "## 3. Research Problem",
    "## 4. Core Challenges", "## 5. Limitations of Existing Methods", "## 6. Core Idea",
    "## 7. Technical Innovations", "## 8. Methodology", "## 9. Experimental Evidence",
    "## 10. Limitations", "## 11. Research Implications", "## 12. Related Papers",
    "## 13. Evidence References",
]
FORBIDDEN_PLACEHOLDERS = ("[TODO", "[待填写", "PLACEHOLDER", "TBD", "<paper-id>")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def locate_dossier(root: Path, paper_id: str) -> Path:
    matches = [p for p in root.joinpath("papers").rglob("knowledge-dossier.md") if p.parent.name == paper_id]
    if len(matches) != 1:
        raise ValueError(f"Expected one dossier for {paper_id!r}; found {len(matches)}")
    return matches[0]


def read_record(dossier: Path) -> tuple[str, dict[str, Any]]:
    text = dossier.read_text(encoding="utf-8")
    match = RECORD_PATTERN.search(text)
    if not match:
        raise ValueError(f"{dossier}: missing bounded JSON record")
    try:
        record = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{dossier}: invalid JSON record: {exc}") from exc
    return text, record


def validate_type(record: dict[str, Any], dossier: Path) -> None:
    absent = sorted(REQUIRED_FIELDS - set(record))
    if absent:
        raise ValueError(f"{dossier}: missing record fields: {', '.join(absent)}")
    for field in (
        "paper_id", "title_en", "venue", "pdf_path", "reading_note_path", "knowledge_card_path", "research_area",
        "research_scenario", "research_problem", "core_idea",
    ):
        if not isinstance(record[field], str) or not record[field].strip():
            raise ValueError(f"{dossier}: {field} must be a non-empty string")
    for field in (
        "authors", "method_tags", "core_challenges", "existing_method_limits", "technical_innovations",
        "research_implications", "related_papers", "evidence_references",
    ):
        if not isinstance(record[field], list):
            raise ValueError(f"{dossier}: {field} must be a list")
    for field in ("methodology", "experimental_evidence", "limitations", "provenance"):
        if not isinstance(record[field], dict):
            raise ValueError(f"{dossier}: {field} must be an object")
    if not record["evidence_references"]:
        raise ValueError(f"{dossier}: evidence_references must not be empty")
    if record["provenance"].get("extraction_status") != "complete":
        raise ValueError(f"{dossier}: record is not marked complete")


def validate_paths(root: Path, record: dict[str, Any], dossier: Path) -> None:
    for field in ("pdf_path", "reading_note_path", "knowledge_card_path"):
        rel = Path(record[field])
        if rel.is_absolute():
            raise ValueError(f"{dossier}: {field} must be repository-relative")
        path = (root / rel).resolve()
        if not path.is_file():
            raise ValueError(f"{dossier}: {field} does not exist: {record[field]}")
        hash_field = {
            "pdf_path": "pdf_sha256",
            "reading_note_path": "reading_note_sha256",
            "knowledge_card_path": "knowledge_card_sha256",
        }[field]
        expected = record["provenance"].get(hash_field)
        if not isinstance(expected, str) or not expected:
            raise ValueError(f"{dossier}: provenance.{hash_field} is required")
        if sha256(path) != expected:
            raise ValueError(f"{dossier}: {field} changed since extraction; refresh dossier provenance")


def validate_dossier(root: Path, dossier: Path, requested_id: str | None = None) -> tuple[str, dict[str, Any]]:
    text, record = read_record(dossier)
    validate_type(record, dossier)
    missing_sections = [heading for heading in REQUIRED_SECTIONS if heading not in text]
    if missing_sections:
        raise ValueError(f"{dossier}: missing sections: {', '.join(missing_sections)}")
    lowered = text.lower()
    bad = [p for p in FORBIDDEN_PLACEHOLDERS if p.lower() in lowered]
    if bad:
        raise ValueError(f"{dossier}: unfinished scaffold placeholder(s): {', '.join(bad)}")
    if requested_id and record["paper_id"] != requested_id:
        raise ValueError(f"{dossier}: record ID {record['paper_id']!r} does not match requested ID {requested_id!r}")
    validate_paths(root, record, dossier)
    return text, record


def table_cell(value: Any, limit: int = 250) -> str:
    if isinstance(value, list):
        text = "; ".join(str(v) for v in value)
    elif isinstance(value, dict):
        text = "; ".join(f"{k}: {table_cell(v, 100)}" for k, v in value.items() if v)
    else:
        text = str(value or "")
    text = re.sub(r"\s+", " ", text).replace("|", "\\|").strip()
    return text[:limit - 1].rstrip() + "…" if len(text) > limit else text or "未提供"


def shift_headings(text: str) -> str:
    return re.sub(r"^(#{1,6}) ", lambda m: "#" * min(6, len(m.group(1)) + 1) + " ", text, flags=re.MULTILINE)


def make_export_links_portable(text: str, mode: str, paper_ids: set[str]) -> str:
    """Keep links within the PDF-free export useful and flatten excluded source links."""

    def replace(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        path = unquote(target.split("#", 1)[0]).replace("\\", "/")
        if not path:
            return label
        if path.lower().endswith(".pdf") or Path(path).name in {"notes.md", "knowledge-card.md"}:
            return f"`{label}`"
        other = re.search(
            r"(?:^|/)([a-z0-9][a-z0-9-]*)/(?:notes|knowledge-card|knowledge-dossier)\.md$",
            path,
        )
        if other and other.group(1) in paper_ids:
            rel = f"{other.group(1)}.md" if mode == "copy" else f"knowledge-dossiers/{other.group(1)}.md"
            return f"[{label}]({rel})"
        if path.endswith("/knowledge-dossier.md"):
            other_id = Path(path).parent.name
            if other_id in paper_ids:
                rel = f"{other_id}.md" if mode == "copy" else f"knowledge-dossiers/{other_id}.md"
                return f"[{label}]({rel})"
        return match.group(0)

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, text)


def write_exports(
    output: Path,
    prefix: str,
    jsonl_name: str,
    zip_enabled: bool,
    zip_name: str,
    items: list[tuple[Path, str, dict[str, Any]]],
    overview_addendum: str = "",
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    copies = output / "knowledge-dossiers"
    copies.mkdir(exist_ok=True)
    paper_ids = {record["paper_id"] for _, _, record in items}
    full = [f"# {prefix.replace('-', ' ').title()}", "", "## Contents", ""]
    for i, (_, _, record) in enumerate(items, 1):
        paper_id = record["paper_id"]
        name = record.get("title_zh") or record["title_en"]
        html_id = f"paper-{i:02d}-{re.sub(r'[^a-z0-9-]+', '-', paper_id.lower()).strip('-')}"
        full.append(f"- [Paper {i:02d} — {name}](#{html_id})")
    full.append("")
    overview = [
        f"# {prefix.replace('-', ' ').title()} Overview", "",
        f"论文数量：{len(items)}。本表用于快速导航，完整方法与证据见独立知识档案。", "",
        "| 论文 | Research Scenario | Core Challenges | Existing Limitations | Technical Innovations | Core Method | Experimental Evidence | Limitations |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    jsonl = []
    for i, (_, content, record) in enumerate(items, 1):
        paper_id = record["paper_id"]
        name = record.get("title_zh") or record["title_en"]
        html_id = f"paper-{i:02d}-{re.sub(r'[^a-z0-9-]+', '-', paper_id.lower()).strip('-')}"
        merged_content = make_export_links_portable(content, "merged", paper_ids)
        copy_content = make_export_links_portable(content, "copy", paper_ids)
        full.extend([f'<a id="{html_id}"></a>', f"## Paper {i:02d} — {name}", "", shift_headings(merged_content).rstrip(), "", "---", ""])
        jsonl.append(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
        methodology = record.get("methodology", {})
        experiments = record.get("experimental_evidence", {})
        overview.append(
            "| " + " | ".join([
                f"[{table_cell(name, 100)}](knowledge-dossiers/{paper_id}.md)",
                table_cell(record.get("research_scenario")), table_cell(record.get("core_challenges")),
                table_cell(record.get("existing_method_limits")), table_cell(record.get("technical_innovations")),
                table_cell(methodology), table_cell(experiments.get("main_results", [])),
                table_cell(record.get("limitations")),
            ]) + " |"
        )
        (copies / f"{paper_id}.md").write_text(copy_content, encoding="utf-8")

    if overview_addendum.strip():
        overview.extend(["", overview_addendum.strip(), ""])

    full_path = output / f"{prefix}-full.md"
    overview_path = output / f"{prefix}-overview.md"
    jsonl_path = output / jsonl_name
    full_path.write_text("\n".join(full), encoding="utf-8")
    overview_path.write_text("\n".join(overview).rstrip() + "\n", encoding="utf-8")
    jsonl_path.write_text("\n".join(jsonl) + "\n", encoding="utf-8")
    parsed = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").splitlines()]
    if len(parsed) != len(items):
        raise ValueError("JSONL record count does not match dossier count")

    if zip_enabled:
        zip_path = output / zip_name
        candidates = [p for p in output.rglob("*") if p.is_file() and p != zip_path and p.suffix.lower() != ".pdf"]
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for path in sorted(candidates):
                archive.write(path, path.relative_to(output).as_posix())
        with zipfile.ZipFile(zip_path) as archive:
            if any(name.lower().endswith(".pdf") for name in archive.namelist()):
                raise ValueError("PDF unexpectedly included in ZIP")

    print(f"Validated dossiers: {len(items)}")
    for path in (full_path, overview_path, jsonl_path):
        print(f"{path}: {path.stat().st_size} bytes")
    if zip_enabled:
        print(f"{output / zip_name}: {(output / zip_name).stat().st_size} bytes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repo_root(), help="knowledge-base root")
    parser.add_argument("--paper-ids", nargs="+", help="stable paper IDs; omit to scan all dossiers")
    parser.add_argument("--expected-count", type=int, help="fail unless exactly this many dossiers are included")
    parser.add_argument("--output-dir", type=Path, help="default: exports/paper-knowledge")
    parser.add_argument("--prefix", default="paper-knowledge", help="merged Markdown basename prefix")
    parser.add_argument("--jsonl-name", default="paper-knowledge.jsonl", help="JSONL basename")
    parser.add_argument("--zip-name", default="paper-knowledge-export.zip", help="ZIP basename")
    parser.add_argument(
        "--overview-addendum", type=Path,
        help="optional grounded cross-paper relation section appended to the overview",
    )
    parser.add_argument("--zip", action="store_true", help="create a ZIP without PDFs")
    parser.add_argument("--validate-only", action="store_true", help="validate without writing exports")
    args = parser.parse_args()

    root = args.root.resolve()
    output = (args.output_dir or root / "exports" / "paper-knowledge").resolve()
    if args.paper_ids:
        dossiers = [(paper_id, locate_dossier(root, paper_id)) for paper_id in args.paper_ids]
    else:
        dossiers = [(path.parent.name, path) for path in sorted(root.joinpath("papers").rglob("knowledge-dossier.md"))]
    if not dossiers:
        raise ValueError("No knowledge dossiers found")
    if args.expected_count is not None and len(dossiers) != args.expected_count:
        raise ValueError(f"Expected {args.expected_count} dossiers; found {len(dossiers)}")

    seen = set()
    items = []
    for requested_id, dossier in dossiers:
        content, record = validate_dossier(root, dossier, requested_id)
        if record["paper_id"] in seen:
            raise ValueError(f"Duplicate paper_id: {record['paper_id']}")
        seen.add(record["paper_id"])
        items.append((dossier, content, record))
    if args.validate_only:
        print(f"PASS: {len(items)} dossiers validated; no exports written.")
        return 0
    overview_addendum = args.overview_addendum.read_text(encoding="utf-8") if args.overview_addendum else ""
    write_exports(output, args.prefix, args.jsonl_name, args.zip, args.zip_name, items, overview_addendum)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
