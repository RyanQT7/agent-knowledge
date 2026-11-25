from __future__ import annotations

import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import unquote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[2]
EVOLUTION = ROOT / "evolution"
STATUS_VALUES = {
    "discovered", "screened", "queued", "reading", "read", "duplicate",
    "deferred", "rejected", "blocked",
}
CLAIM_STATUSES = {"active", "needs_review", "contested", "superseded", "retracted"}
CLAIM_RELATIONS = {"supports", "qualifies", "contradicts", "supersedes", "related_to"}
CLAIM_TYPES = {
    "paper_fact", "code_fact", "cross_source_synthesis", "interpretation",
    "learner_signal", "execution_observation",
}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_run_id() -> str:
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{os.urandom(3).hex()}"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def stable_hash(value: str, length: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def atomic_write_text(path: Path, text: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp_name, mode)
        os.replace(tmp_name, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp_name)


def atomic_write_json(path: Path, value: Any, mode: int = 0o600) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", mode)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    result: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: expected a JSON object")
        result.append(value)
    return result


def atomic_write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    content = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    atomic_write_text(path, content)


@contextlib.contextmanager
def file_lock(path: Path, timeout_seconds: float = 20.0) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out acquiring evolution lock: {path}")
                time.sleep(0.1)
        os.ftruncate(fd, 0)
        os.write(fd, f"pid={os.getpid()} acquired={utc_now()}\n".encode())
        yield
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    text = unquote(str(value)).strip().lower()
    text = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", text)
    text = text.rstrip(" .;,)")
    return text or None


def normalize_arxiv(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    text = unquote(str(value)).strip()
    match = re.search(r"(?:arxiv:|abs/)?((?:\d{4}\.\d{4,5}|[a-z.-]+/\d{7}))(v\d+)?", text, re.I)
    if not match:
        return None, None
    return match.group(1).lower(), (match.group(2) or "v1").lower()


def normalize_repo_url(value: str | None) -> str | None:
    if not value:
        return None
    text = str(value).strip().strip("<>")
    if text.startswith("git@github.com:"):
        text = "https://github.com/" + text.split(":", 1)[1]
    if not text.startswith(("http://", "https://")):
        text = "https://github.com/" + text.strip("/")
    parts = urlsplit(text)
    host = parts.netloc.lower().removeprefix("www.")
    path = re.sub(r"\.git$", "", parts.path).rstrip("/")
    if host in {"github.com", "www.github.com"}:
        path_parts = [segment for segment in path.split("/") if segment]
        path = "/" + "/".join(path_parts[:2])
    return urlunsplit(("https", host, path, "", "")) if host else None


def normalize_title(value: str | None) -> str:
    if not value:
        return ""
    text = unicodedata.normalize("NFKD", str(value)).casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def normalize_author(value: str | None) -> str:
    if not value:
        return ""
    return normalize_title(str(value).replace(";", ","))


def candidate_identity_keys(item: dict[str, Any]) -> set[str]:
    keys: set[str] = set()
    doi = normalize_doi(item.get("doi"))
    arxiv_base, _ = normalize_arxiv(item.get("arxiv_id"))
    repo = normalize_repo_url(item.get("official_repository") or item.get("source_url") if item.get("record_type") == "repository" else item.get("official_repository"))
    title = normalize_title(item.get("title"))
    authors = normalize_author(",".join(item.get("authors", [])) if isinstance(item.get("authors"), list) else item.get("authors"))
    if doi:
        keys.add(f"doi:{doi}")
    if arxiv_base:
        keys.add(f"arxiv:{arxiv_base}")
    if repo:
        keys.add(f"repo:{repo}")
    for raw_repo in item.get("repositories", []) if isinstance(item.get("repositories"), list) else []:
        normalized_repo = normalize_repo_url(raw_repo)
        if normalized_repo:
            keys.add(f"repo:{normalized_repo}")
    if title:
        keys.add(f"title:{title}|authors:{authors}" if authors else f"title:{title}")
    return keys


def candidate_id(item: dict[str, Any]) -> str:
    doi = normalize_doi(item.get("doi"))
    arxiv_base, _ = normalize_arxiv(item.get("arxiv_id"))
    repo = normalize_repo_url(item.get("official_repository") or item.get("source_url") if item.get("record_type") == "repository" else item.get("official_repository"))
    identity = f"doi:{doi}" if doi else f"arxiv:{arxiv_base}" if arxiv_base else f"repo:{repo}" if repo else next(iter(sorted(candidate_identity_keys(item))), "unknown")
    return "cand-" + stable_hash(identity, 20)


def resolve_local_path(root: Path, raw: str) -> Path | None:
    value = raw.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
    if not value or value.startswith(("http://", "https://", "mailto:", "data:")):
        return None
    value = unquote(value)
    target = (root / value).resolve() if not value.startswith("/") else Path(value).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        return None
    return target


def extract_paper_identity(text: str, rel_path: str) -> dict[str, Any]:
    title = ""
    for line in text.splitlines():
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match and not match.group(1).lower().startswith(("bibliographic", "paper ", "code reading")):
            title = match.group(1).strip()
            break
    doi_match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    arxiv_match = re.search(r"(?:arxiv(?:\.org)?/(?:abs|html)/|arxiv:\s*)((?:\d{4}\.\d{4,5}|[a-z.-]+/\d{7}))(v\d+)?", text, re.I)
    authors_match = re.search(r"^\s*-?\s*Authors?:\s*(.+)$", text, re.I | re.M)
    repo_urls = re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", text)
    sha_match = re.search(r"(?:Commit(?: SHA)?|Read-at commit|SHA):\s*`?([0-9a-f]{40})", text, re.I)
    result: dict[str, Any] = {"title": title, "path": rel_path}
    if doi_match:
        result["doi"] = normalize_doi(doi_match.group(0))
    if arxiv_match:
        result["arxiv_id"] = arxiv_match.group(1) + (arxiv_match.group(2) or "")
    if authors_match:
        result["authors"] = authors_match.group(1).strip()
    if repo_urls:
        result["repositories"] = sorted({normalize_repo_url(url) for url in repo_urls if normalize_repo_url(url)})
    if sha_match:
        result["repo_sha"] = sha_match.group(1).lower()
    return result


def existing_knowledge_identities(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for pattern in ("papers/**/notes.md", "code/**/notes.md", "code/aiops/**/notes.md"):
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            record = extract_paper_identity(text, path.relative_to(root).as_posix())
            if record.get("title") or record.get("doi") or record.get("arxiv_id"):
                records.append(record)
    index_path = root / "code" / "repository-index.md"
    if index_path.is_file():
        for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines():
            repos = re.findall(r"https?://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?", line)
            sha_match = re.search(r"\b[0-9a-f]{40}\b", line, re.I)
            if not repos:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            records.append({
                "title": cells[0] if cells else "",
                "path": "code/repository-index.md",
                "repositories": sorted({normalize_repo_url(url) for url in repos if normalize_repo_url(url)}),
                **({"repo_sha": sha_match.group(0).lower()} if sha_match else {}),
            })
    return records


def title_author_key(item: dict[str, Any]) -> str | None:
    title = normalize_title(item.get("title"))
    if not title:
        return None
    authors = normalize_author(",".join(item.get("authors", [])) if isinstance(item.get("authors"), list) else item.get("authors"))
    return f"title:{title}|authors:{authors}" if authors else f"title:{title}"


def validate_claim(claim: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ("claim_id", "statement", "claim_type", "scope", "status", "evidence", "related_claims", "supersedes", "last_reviewed_at")
    for key in required:
        if key not in claim:
            errors.append(f"missing {key}")
    if claim.get("claim_type") not in CLAIM_TYPES:
        errors.append(f"invalid claim_type: {claim.get('claim_type')}")
    if claim.get("status") not in CLAIM_STATUSES:
        errors.append(f"invalid status: {claim.get('status')}")
    evidence = claim.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be a list")
    else:
        if claim.get("status") in {"active", "contested", "superseded"} and not evidence:
            errors.append("active/contested/superseded claim requires evidence")
        for index, item in enumerate(evidence):
            if not isinstance(item, dict):
                errors.append(f"evidence[{index}] must be an object")
                continue
            for key in ("source_id", "source_version", "source_uri", "locator", "relation", "accessed_at"):
                if not item.get(key):
                    errors.append(f"evidence[{index}] missing {key}")
            if item.get("relation") not in CLAIM_RELATIONS:
                errors.append(f"evidence[{index}] invalid relation: {item.get('relation')}")
    if not isinstance(claim.get("related_claims", []), list):
        errors.append("related_claims must be a list")
    if not isinstance(claim.get("supersedes", []), list):
        errors.append("supersedes must be a list")
    return errors


def safe_relative_path(raw: str, root: Path) -> tuple[str | None, str | None]:
    candidate = Path(raw)
    if candidate.is_absolute() or any(part in {"..", "."} for part in candidate.parts):
        return None, "path must be a normalized relative path"
    normalized = candidate.as_posix()
    if not normalized or normalized.startswith(("sources/", ".git/", "evolution/state/")):
        return None, "path is outside the allowed proposal scope"
    allowed_roots = ("concepts/", "papers/", "code/", "notes/", "lessons/")
    if normalized != "INDEX.md" and not normalized.startswith(allowed_roots):
        return None, "proposal target must be a knowledge file or INDEX.md"
    if normalized.startswith("skills/"):
        return None, "Skill changes are out of scope for Phase 1"
    resolved = (root / normalized).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None, "path resolves outside the knowledge base"
    return normalized, None
