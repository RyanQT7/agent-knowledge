#!/usr/bin/env python3
"""Small local PDF inspection helpers for research papers.

User-facing page numbers are 1-based PDF physical page numbers. Printed page
numbers visible in the paper are intentionally not inferred or substituted.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_RENDER_ROOT = Path.home() / ".cache" / "agent-knowledge" / "paper-pdf"


def load_pymupdf() -> Any:
    try:
        import pymupdf

        return pymupdf
    except ImportError:
        try:
            import fitz

            return fitz
        except ImportError as exc:
            raise RuntimeError(
                "PyMuPDF is missing. Use the configured private environment or install PyMuPDF there."
            ) from exc


def parse_pages(spec: str | None, page_count: int) -> list[int]:
    """Parse page selectors like '2,4-6' into zero-based physical indices."""
    if not spec:
        return list(range(page_count))
    selected: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise ValueError("empty page selector; use values such as 2,4-6")
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text) if start_text else 1
            end = int(end_text) if end_text else page_count
            if start > end:
                raise ValueError(f"reversed page range: {part}")
            values = range(start, end + 1)
        else:
            values = [int(part)]
        for page_number in values:
            if page_number < 1 or page_number > page_count:
                raise ValueError(
                    f"physical page {page_number} is outside the PDF range 1-{page_count}"
                )
            selected.add(page_number - 1)
    return sorted(selected)


def page_text(page: Any, mode: str) -> str:
    if mode == "plain":
        return page.get_text("text", sort=False).strip()
    blocks = page.get_text("blocks", sort=True)
    texts = [str(block[4]).strip() for block in blocks if len(block) > 4 and str(block[4]).strip()]
    return "\n\n".join(texts)


def open_pdf(path: Path) -> tuple[Any, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    pymupdf = load_pymupdf()
    try:
        document = pymupdf.open(str(path))
    except Exception as exc:
        raise RuntimeError(f"cannot open PDF {path}: {exc}") from exc
    if not document.is_pdf:
        document.close()
        raise ValueError(f"not a PDF file: {path}")
    return pymupdf, document


def check_output(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite {path}; pass --force to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text_or_stdout(text: str, output: Path | None, force: bool) -> None:
    if output is None:
        sys.stdout.write(text)
        if text and not text.endswith("\n"):
            sys.stdout.write("\n")
        return
    check_output(output, force)
    output.write_text(text, encoding="utf-8")
    print(output)


def cmd_info(args: argparse.Namespace) -> None:
    _, document = open_pdf(args.pdf)
    try:
        metadata = document.metadata or {}
        result = {
            "path": str(args.pdf.resolve()),
            "file_size_bytes": args.pdf.stat().st_size,
            "page_count": document.page_count,
            "metadata": {key: value for key, value in metadata.items() if value not in (None, "")},
            "page_numbering": "physical PDF pages, 1-based; printed page numbers are not inferred",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        document.close()


def cmd_extract(args: argparse.Namespace) -> None:
    _, document = open_pdf(args.pdf)
    try:
        indices = parse_pages(args.pages, document.page_count)
        separator = "\n\n" if args.format == "md" else "\n\n"
        chunks: list[str] = []
        for index in indices:
            text = page_text(document[index], args.mode)
            label = f"## PDF physical page {index + 1}" if args.format == "md" else f"===== PDF physical page {index + 1} ====="
            chunks.append(f"{label}\n\n{text}" if text else f"{label}\n\n[No extractable text]")
        write_text_or_stdout(separator.join(chunks) + "\n", args.output, args.force)
    finally:
        document.close()


def cmd_search(args: argparse.Namespace) -> None:
    _, document = open_pdf(args.pdf)
    try:
        indices = parse_pages(args.pages, document.page_count)
        needle = args.query.casefold()
        results: list[dict[str, Any]] = []
        for index in indices:
            content = page_text(document[index], args.mode)
            folded = content.casefold()
            start = 0
            matches: list[str] = []
            while len(matches) < args.max_matches_per_page:
                found = folded.find(needle, start)
                if found < 0:
                    break
                left = max(0, found - args.context_chars)
                right = min(len(content), found + len(args.query) + args.context_chars)
                snippet = re.sub(r"\s+", " ", content[left:right]).strip()
                if left:
                    snippet = "…" + snippet
                if right < len(content):
                    snippet += "…"
                matches.append(snippet)
                start = found + max(1, len(needle))
            if matches:
                results.append({"pdf_physical_page": index + 1, "matches": matches})
        print(json.dumps({"query": args.query, "results": results}, ensure_ascii=False, indent=2))
    finally:
        document.close()


def parse_crop(spec: str | None, pymupdf: Any) -> Any | None:
    if not spec:
        return None
    try:
        coordinates = [float(value.strip()) for value in spec.split(",")]
    except ValueError as exc:
        raise ValueError("--crop must be x0,y0,x1,y1 in PDF points") from exc
    if len(coordinates) != 4:
        raise ValueError("--crop must be x0,y0,x1,y1 in PDF points")
    x0, y0, x1, y1 = coordinates
    if x1 <= x0 or y1 <= y0:
        raise ValueError("crop must have positive width and height")
    return pymupdf.Rect(x0, y0, x1, y1)


def cmd_render(args: argparse.Namespace) -> None:
    pymupdf, document = open_pdf(args.pdf)
    try:
        indices = parse_pages(args.pages, document.page_count)
        crop = parse_crop(args.crop, pymupdf)
        out_dir = args.output_dir or DEFAULT_RENDER_ROOT / args.pdf.stem
        suffix = "-crop" if crop else ""
        outputs = [out_dir / f"page-{index + 1:03d}{suffix}.png" for index in indices]
        if not args.force:
            existing = [path for path in outputs if path.exists()]
            if existing:
                raise FileExistsError(
                    "refusing to overwrite: " + ", ".join(str(path) for path in existing) + "; pass --force"
                )
        out_dir.mkdir(parents=True, exist_ok=True)
        scale = args.dpi / 72.0
        matrix = pymupdf.Matrix(scale, scale)
        for index, output in zip(indices, outputs):
            page = document[index]
            clip = page.rect & crop if crop else None
            if clip is not None and clip.is_empty:
                raise ValueError(f"crop does not intersect physical page {index + 1}")
            pixmap = page.get_pixmap(matrix=matrix, clip=clip, alpha=False)
            pixmap.save(str(output))
            print(output)
    finally:
        document.close()


def clean_rows(rows: Iterable[Iterable[Any]]) -> list[list[str]]:
    cleaned = [[re.sub(r"\s+", " ", str(cell or "")).strip() for cell in row] for row in rows]
    return [row for row in cleaned if any(row)]


def pymupdf_tables(document: Any, indices: list[int]) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    for index in indices:
        page = document[index]
        find_tables = getattr(page, "find_tables", None)
        if not callable(find_tables):
            continue
        try:
            tables = find_tables().tables
        except Exception:
            continue
        for table_number, table in enumerate(tables, start=1):
            rows = clean_rows(table.extract() or [])
            if len(rows) >= 2:
                found.append({"pdf_physical_page": index + 1, "table": table_number, "rows": rows})
    return found


def pdfplumber_tables(pdf_path: Path, indices: list[int]) -> list[dict[str, Any]]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError("pdfplumber is missing from the configured private environment") from exc
    found: list[dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for index in indices:
            for table_number, rows in enumerate(pdf.pages[index].extract_tables() or [], start=1):
                cleaned = clean_rows(rows)
                if len(cleaned) >= 2:
                    found.append({"pdf_physical_page": index + 1, "table": table_number, "rows": cleaned})
    return found


def tables_to_markdown(tables: list[dict[str, Any]]) -> str:
    output: list[str] = []
    for item in tables:
        rows = item["rows"]
        width = max((len(row) for row in rows), default=0)
        if not width:
            continue
        normalized = [row + [""] * (width - len(row)) for row in rows]
        output.append(f"### PDF physical page {item['pdf_physical_page']} — table {item['table']}")
        output.append("| " + " | ".join(normalized[0]) + " |")
        output.append("| " + " | ".join(["---"] * width) + " |")
        output.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
    return "\n\n".join(output) + ("\n" if output else "No tables detected.\n")


def tables_to_csv(tables: list[dict[str, Any]]) -> str:
    from io import StringIO

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["pdf_physical_page", "table", "row", "column", "value"])
    for item in tables:
        for row_number, row in enumerate(item["rows"], start=1):
            for column_number, value in enumerate(row, start=1):
                writer.writerow([item["pdf_physical_page"], item["table"], row_number, column_number, value])
    return buffer.getvalue()


def cmd_tables(args: argparse.Namespace) -> None:
    _, document = open_pdf(args.pdf)
    try:
        indices = parse_pages(args.pages, document.page_count)
        tables: list[dict[str, Any]] = []
        backend_used = args.backend
        if args.backend in {"auto", "pymupdf"}:
            tables = pymupdf_tables(document, indices)
            backend_used = "pymupdf"
        if args.backend == "pdfplumber" or (args.backend == "auto" and not tables):
            tables = pdfplumber_tables(args.pdf, indices)
            backend_used = "pdfplumber"
        if args.backend == "pymupdf" and not tables:
            backend_used = "pymupdf"

        if args.format == "json":
            rendered = json.dumps({"backend": backend_used, "tables": tables}, ensure_ascii=False, indent=2) + "\n"
        elif args.format == "csv":
            rendered = tables_to_csv(tables)
        else:
            rendered = tables_to_markdown(tables)
        write_text_or_stdout(rendered, args.output, args.force)
    finally:
        document.close()


def add_pdf_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("pdf", type=Path, help="local PDF file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Inspect, extract, search, render, and sample tables from local PDFs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info = subparsers.add_parser("info", help="show page count, metadata, and file path")
    add_pdf_argument(info)
    info.set_defaults(function=cmd_info)

    extract = subparsers.add_parser("extract", help="extract text with physical page boundaries")
    add_pdf_argument(extract)
    extract.add_argument("--pages", help="1-based physical pages, for example 1,3-5; default: all")
    extract.add_argument("--mode", choices=["plain", "layout"], default="plain")
    extract.add_argument("--format", choices=["txt", "md"], default="md")
    extract.add_argument("--output", type=Path, help="output file; default: stdout")
    extract.add_argument("--force", action="store_true", help="allow replacing an existing output file")
    extract.set_defaults(function=cmd_extract)

    search = subparsers.add_parser("search", help="search extracted PDF text and show nearby context")
    add_pdf_argument(search)
    search.add_argument("--query", required=True)
    search.add_argument("--pages", help="optional 1-based physical page selector")
    search.add_argument("--mode", choices=["plain", "layout"], default="plain")
    search.add_argument("--context-chars", type=int, default=220)
    search.add_argument("--max-matches-per-page", type=int, default=4)
    search.set_defaults(function=cmd_search)

    render = subparsers.add_parser("render", help="render selected physical pages to PNG")
    add_pdf_argument(render)
    render.add_argument("--pages", required=True, help="1-based physical pages, for example 2,4-6")
    render.add_argument("--dpi", type=int, default=190)
    render.add_argument("--crop", help="optional x0,y0,x1,y1 crop rectangle in PDF points")
    render.add_argument("--output-dir", type=Path, help=f"default: {DEFAULT_RENDER_ROOT}/<pdf-stem>")
    render.add_argument("--force", action="store_true", help="allow replacing existing PNG files")
    render.set_defaults(function=cmd_render)

    tables = subparsers.add_parser("tables", help="attempt table extraction on selected pages")
    add_pdf_argument(tables)
    tables.add_argument("--pages", required=True, help="1-based physical pages, for example 4-6")
    tables.add_argument("--backend", choices=["auto", "pymupdf", "pdfplumber"], default="auto")
    tables.add_argument("--format", choices=["md", "csv", "json"], default="md")
    tables.add_argument("--output", type=Path, help="output file; default: stdout")
    tables.add_argument("--force", action="store_true", help="allow replacing an existing output file")
    tables.set_defaults(function=cmd_tables)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.function(args)
        return 0
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as exc:
        print(f"paper-pdf: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
