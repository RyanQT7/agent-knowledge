from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote
from typing import Any


_STOPWORDS = {
    "a", "an", "and", "for", "from", "in", "of", "on", "the", "to", "via", "with",
    "using", "towards", "toward", "based", "large", "language", "model", "models",
}
_NOTE_NAMES = {"notes.md", "knowledge-dossier.md", "knowledge-card.md"}


def _identity_keys(identity: dict[str, Any]) -> tuple[list[str], list[str]]:
    exact: list[str] = []
    for field in ("arxiv_id", "source_id", "source_version", "doi", "source_uri", "source_url", "url"):
        value = str(identity.get(field) or "").strip().lower()
        if not value:
            continue
        arxiv = re.search(r"(?:arxiv:|arxiv\.org/(?:abs|pdf)/)?(\d{4}\.\d{4,5})(?:v\d+)?", value)
        if arxiv:
            exact.append(arxiv.group(1))
        doi = re.search(r"10\.\d{4,9}/[^\s?#]+", value)
        if doi:
            exact.append(doi.group(0).rstrip(".,;)]}"))
    exact.extend(str(alias).strip().lower() for alias in identity.get("local_aliases", []) if str(alias).strip())
    titles = [str(identity.get("title") or ""), *(str(value) for value in identity.get("local_aliases", []))]
    words = []
    for value in titles:
        title = re.sub(r"[^a-z0-9]+", " ", value.lower())
        words.extend(word for word in title.split() if len(word) >= 3 and word not in _STOPWORDS)
    words = list(dict.fromkeys(words))
    return list(dict.fromkeys(exact)), list(dict.fromkeys(words))


def _matches(path: Path, excerpt: str, exact: list[str], title_words: list[str]) -> bool:
    haystack = unquote((path.as_posix() + " " + excerpt).lower())
    if any(key and key in haystack for key in exact):
        return True
    if not title_words:
        return False
    haystack_words = set(re.findall(r"[a-z0-9]+", haystack))
    hits = sum(word in haystack_words for word in title_words)
    required = min(3, max(1, (len(title_words) * 2 + 2) // 3))
    return hits >= required


def _safe_path(path: Path, allowed_root: Path) -> Path | None:
    try:
        resolved = path.resolve(strict=True)
        resolved.relative_to(allowed_root.resolve())
    except (OSError, ValueError):
        return None
    return resolved if resolved.is_file() else None


def _linked_pdfs(note: Path, excerpt: str, sources_root: Path) -> list[Path]:
    references = re.findall(r"\[[^\]]*\]\(([^)]+\.pdf(?:#[^)]*)?)\)", excerpt, re.I)
    references += re.findall(r"(?:pdf_path|local_file)\s*:\s*[\"']?([^\s\"']+\.pdf)", excerpt, re.I)
    result: list[Path] = []
    for reference in references:
        value = unquote(reference.split("#", 1)[0].strip())
        if value.lower().startswith(("http://", "https://")):
            continue
        path = Path(value)
        candidate = path if path.is_absolute() else note.parent / path
        safe = _safe_path(candidate, sources_root)
        if safe and safe not in result:
            result.append(safe)
    return result


def _note_identity_excerpt(text: str) -> str:
    identity_lines = []
    for line in text.splitlines()[:50]:
        if line.startswith("# ") or re.match(
            r"^\s*(?:[-*]\s*)?(?:title|doi|url(?:\s*/\s*doi)?|arxiv(?:\s+id)?|source(?:\s+id)?|identifier|local file)\s*:",
            line,
            re.I,
        ):
            identity_lines.append(line)
    return "\n".join(identity_lines)


def find_local_paper_material(root: Path, identity: dict[str, Any]) -> dict[str, list[str]]:
    """Return matching local source paths only; never copy, extract, or cache paper bodies."""
    sources_root = root / "sources" / "papers"
    papers_root = root / "papers"
    exact, title_words = _identity_keys(identity)
    pdfs: list[Path] = []
    parsed_text: list[Path] = []
    notes: list[Path] = []

    if sources_root.is_dir():
        for pattern in ("*.pdf", "*.txt", "*.text"):
            for path in sources_root.rglob(pattern):
                if _matches(path, "", exact, title_words):
                    safe = _safe_path(path, sources_root)
                    if safe:
                        target = pdfs if safe.suffix.lower() == ".pdf" else parsed_text
                        if safe not in target:
                            target.append(safe)

    if papers_root.is_dir():
        for path in papers_root.rglob("*.md"):
            if path.name.lower() not in _NOTE_NAMES:
                continue
            try:
                excerpt = path.read_text(encoding="utf-8", errors="replace")[:16000]
            except OSError:
                continue
            if not _matches(path, _note_identity_excerpt(excerpt), exact, title_words):
                continue
            safe_note = _safe_path(path, papers_root)
            if safe_note:
                notes.append(safe_note)
            for linked in _linked_pdfs(path, excerpt, sources_root):
                if linked not in pdfs:
                    pdfs.append(linked)
                sidecar = _safe_path(linked.with_suffix(".txt"), sources_root)
                if sidecar and sidecar not in parsed_text:
                    parsed_text.append(sidecar)

    return {
        "pdf_paths": [str(path) for path in pdfs[:3]],
        "parsed_text_paths": [str(path) for path in parsed_text[:3]],
        "paper_note_paths": [str(path) for path in notes[:3]],
    }
