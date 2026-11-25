from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable

from scripts.evolution.common import (
    EVOLUTION, ROOT, atomic_write_json, atomic_write_jsonl, candidate_id,
    candidate_identity_keys, existing_knowledge_identities, file_lock,
    normalize_arxiv, normalize_doi, normalize_repo_url, normalize_title,
    read_json, read_jsonl, stable_hash, title_author_key, utc_now,
)

WATCHLIST_PATH = EVOLUTION / "config" / "watchlist.yaml"
LIMITS_PATH = EVOLUTION / "config" / "limits.yaml"
STATE_PATH = EVOLUTION / "state" / "discovery.json"
CANDIDATES_PATH = EVOLUTION / "inbox" / "candidates.jsonl"
USER_AGENT = "agent-knowledge-evolution/0.1 (public research metadata client)"


def load_config(path: Path) -> dict[str, Any]:
    # The committed .yaml config files intentionally use JSON-compatible YAML,
    # which is also valid YAML 1.2 and keeps the runner on Python's stdlib.
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object in {path}")
    return value


def _iso_date(value: Any) -> str | None:
    if not value:
        return None
    text = str(value)
    try:
        return dt.date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _truncate(value: Any, limit: int = 2400) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def _author_names(items: Any, name_key: str = "name") -> list[str]:
    result: list[str] = []
    for item in items or []:
        if isinstance(item, dict):
            name = item.get(name_key) or item.get("display_name") or item.get("family")
            if name:
                if item.get("given") and item.get("family"):
                    name = f"{item['given']} {item['family']}"
                result.append(str(name))
        elif item:
            result.append(str(item))
    return result


def _base_record(topic: dict[str, Any], source: str, query: str, **values: Any) -> dict[str, Any]:
    record = {
        "record_type": values.get("record_type", "paper"),
        "title": _truncate(values.get("title"), 500),
        "authors": values.get("authors", []),
        "publication_date": _iso_date(values.get("publication_date")),
        "publication_status": values.get("publication_status") or "unknown",
        "venue": values.get("venue"),
        "doi": normalize_doi(values.get("doi")),
        "arxiv_id": values.get("arxiv_id"),
        "source_url": values.get("source_url"),
        "source_version": values.get("source_version"),
        "abstract": _truncate(values.get("abstract")),
        "official_repository": normalize_repo_url(values.get("official_repository")),
        "source_system": source,
        "source_record_id": values.get("source_record_id"),
        "query": query,
        "novelty_reason": "Pending comparison with indexed local knowledge; metadata alone does not establish research novelty.",
        "relevance_reason": "Pending watchlist relevance screening; metadata alone does not establish paper quality.",
        "research_topic": topic["id"],
        "related_questions": list(topic.get("research_questions", [])),
        "related_concepts": list(topic.get("concepts", [])),
        "discovered_at": utc_now(),
    }
    return record


def _request_json(url: str, timeout: int = 12, retries: int = 1) -> Any:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8", errors="replace"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {retries + 1} attempt(s): {type(last_error).__name__}: {last_error}")


def _request_text(url: str, timeout: int = 12, retries: int = 1, accept: str = "application/atom+xml,text/html") -> str:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {retries + 1} attempt(s): {type(last_error).__name__}: {last_error}")


def _query_string(topic: dict[str, Any]) -> str:
    explicit = topic.get("query")
    if explicit:
        return str(explicit).strip()
    title = str(topic.get("title", "")).strip()
    keywords = topic.get("keywords", [])
    phrases = [str(item).strip() for item in keywords[:5] if str(item).strip()]
    return " OR ".join([f'"{phrase}"' for phrase in phrases]) or title


def _source_since(topic_id: str, source: str, query: str, state: dict[str, Any], lookback_days: int, overlap_days: int) -> tuple[str, bool]:
    key = f"{topic_id}|{source}|{stable_hash(query, 20)}"
    previous = state.get("cursors", {}).get(key)
    if previous and previous.get("last_successful_at"):
        stamp = dt.datetime.fromisoformat(previous["last_successful_at"].replace("Z", "+00:00"))
        since = (stamp.date() - dt.timedelta(days=overlap_days)).isoformat()
        return since, True
    return (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=lookback_days)).isoformat(), False


def _fetch_arxiv(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    phrases = [item.strip('"') for item in re.split(r"\s+OR\s+", query, flags=re.I) if item.strip()]
    # Let urlencode perform the only URL escaping. Pre-quoting here double
    # escaped the query and silently returned an empty Atom feed.
    terms = " OR ".join(f'all:"{phrase}"' for phrase in phrases[:5])
    start = since.replace("-", "") + "0000"
    end = dt.datetime.now(dt.timezone.utc).date().strftime("%Y%m%d") + "2359"
    search = f"({terms}) AND submittedDate:[{start} TO {end}]"
    params = urllib.parse.urlencode({"search_query": search, "start": 0, "max_results": 20, "sortBy": "submittedDate", "sortOrder": "descending"})
    data = _request_text(f"https://export.arxiv.org/api/query?{params}", int(limits["http_timeout_seconds"]), int(limits["max_http_retries"]))
    root = ET.fromstring(data)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    rows: list[dict[str, Any]] = []
    for entry in root.findall("a:entry", ns):
        arxiv_url = entry.findtext("a:id", default="", namespaces=ns)
        base_id, version = normalize_arxiv(arxiv_url)
        title = _truncate(entry.findtext("a:title", default="", namespaces=ns), 500)
        authors = [node.findtext("a:name", default="", namespaces=ns) for node in entry.findall("a:author", ns)]
        published = entry.findtext("a:published", default="", namespaces=ns)
        updated = entry.findtext("a:updated", default="", namespaces=ns)
        links = entry.findall("a:link", ns)
        pdf = next((node.attrib.get("href") for node in links if node.attrib.get("title") == "pdf"), None)
        rows.append(_base_record(
            topic, "arxiv", query,
            title=title, authors=authors, publication_date=published,
            publication_status="preprint", arxiv_id=base_id + (version or ""),
            source_url=arxiv_url, source_version=version, abstract=entry.findtext("a:summary", default="", namespaces=ns),
            source_record_id=base_id, pdf_url=pdf, updated_at=_iso_date(updated),
        ))
        rows[-1]["pdf_url"] = pdf
        rows[-1]["updated_at"] = _iso_date(updated)
    return rows


def _fetch_crossref(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "query.title": re.sub(r"\s+OR\s+", " ", query, flags=re.I).replace('"', ""),
        "filter": f"from-pub-date:{since}", "rows": 20,
        "select": "DOI,title,author,published,created,type,publisher,URL,container-title",
        "sort": "published", "order": "desc",
    })
    body = _request_json(f"https://api.crossref.org/works?{params}", int(limits["http_timeout_seconds"]), int(limits["max_http_retries"]))
    rows: list[dict[str, Any]] = []
    for item in body.get("message", {}).get("items", []):
        date_parts = item.get("published", {}).get("date-parts", [[]])[0]
        date_value = "-".join(f"{int(value):02d}" if index else f"{int(value):04d}" for index, value in enumerate(date_parts[:3])) if date_parts else None
        if date_value and len(date_value) == 4:
            date_value += "-01-01"
        elif date_value and len(date_value) == 7:
            date_value += "-01"
        rows.append(_base_record(
            topic, "crossref", query,
            title=(item.get("title") or [""])[0], authors=_author_names(item.get("author"), "family"),
            publication_date=date_value, publication_status="published", venue=(item.get("container-title") or [None])[0],
            doi=item.get("DOI"), source_url=item.get("URL") or ("https://doi.org/" + item["DOI"] if item.get("DOI") else None),
            source_record_id=item.get("DOI"),
        ))
    return rows


def _openalex_abstract(inverted: dict[str, list[int]] | None) -> str:
    if not inverted:
        return ""
    words: list[str] = [""] * (max((max(pos) for pos in inverted.values() if pos), default=-1) + 1)
    for word, positions in inverted.items():
        for position in positions:
            if 0 <= position < len(words):
                words[position] = word
    return " ".join(words)


def _fetch_openalex(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "search": query.replace('"', ""), "filter": f"from_publication_date:{since}",
        "per-page": 20, "sort": "publication_date:desc",
        "select": "id,doi,title,publication_year,publication_date,authorships,primary_location,ids,abstract_inverted_index,type",
    })
    body = _request_json(f"https://api.openalex.org/works?{params}", int(limits["http_timeout_seconds"]), int(limits["max_http_retries"]))
    rows: list[dict[str, Any]] = []
    for item in body.get("results", []):
        authors = [auth.get("author", {}).get("display_name", "") for auth in item.get("authorships", [])]
        location = item.get("primary_location") or {}
        source = location.get("source") or {}
        ids = item.get("ids") or {}
        rows.append(_base_record(
            topic, "openalex", query, title=item.get("title"), authors=authors,
            publication_date=item.get("publication_date"), publication_status="published" if item.get("publication_date") else "unknown",
            venue=source.get("display_name"), doi=item.get("doi"), source_url=location.get("landing_page_url") or item.get("id"),
            source_record_id=ids.get("openalex") or item.get("id"), abstract=_openalex_abstract(item.get("abstract_inverted_index")),
        ))
    return rows


def _fetch_semantic_scholar(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"query": query.replace('"', ""), "limit": 20, "fields": "title,authors,year,publicationDate,venue,externalIds,url,abstract,publicationTypes"})
    request = urllib.request.Request(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{params}",
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    )
    last_error: Exception | None = None
    for attempt in range(int(limits["max_http_retries"]) + 1):
        try:
            with urllib.request.urlopen(request, timeout=int(limits["http_timeout_seconds"])) as response:
                body = json.loads(response.read().decode("utf-8", errors="replace"))
            rows = []
            for item in body.get("data", []):
                ext = item.get("externalIds") or {}
                rows.append(_base_record(
                    topic, "semantic_scholar", query, title=item.get("title"),
                    authors=_author_names(item.get("authors")), publication_date=item.get("publicationDate") or item.get("year"),
                    publication_status="published" if item.get("venue") else "unknown", venue=item.get("venue"),
                    doi=ext.get("DOI"), arxiv_id=ext.get("ArXiv"), source_url=item.get("url"),
                    source_record_id=item.get("paperId"), abstract=item.get("abstract"),
                ))
            return rows
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < int(limits["max_http_retries"]):
                time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"request failed: {type(last_error).__name__}: {last_error}")


def _fetch_github(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    terms = re.sub(r"[^A-Za-z0-9\s-]", " ", query).split()
    search_terms = " ".join(terms[:6])
    github_query = f"{search_terms} in:name,description,readme pushed:>={since}"
    params = urllib.parse.urlencode({"q": github_query, "sort": "updated", "order": "desc", "per_page": 20})
    body = _request_json(f"https://api.github.com/search/repositories?{params}", int(limits["http_timeout_seconds"]), int(limits["max_http_retries"]))
    rows: list[dict[str, Any]] = []
    for item in body.get("items", []):
        repo_url = normalize_repo_url(item.get("html_url"))
        rows.append(_base_record(
            topic, "github", query, record_type="repository", title=item.get("full_name"),
            authors=[item.get("owner", {}).get("login", "")], publication_date=item.get("pushed_at"),
            publication_status="repository", venue=None, source_url=repo_url, official_repository=None,
            source_version=item.get("pushed_at"), abstract=item.get("description"), source_record_id=item.get("full_name"),
        ))
        rows[-1]["repository_default_branch"] = item.get("default_branch")
        rows[-1]["repository_pushed_at"] = item.get("pushed_at")
        rows[-1]["repository_stars"] = item.get("stargazers_count")
        rows[-1]["repository_license"] = (item.get("license") or {}).get("spdx_id")
        rows[-1]["repository_commit"] = None
    return rows


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "a":
            self._href = dict(attrs).get("href")
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.items.append((self._href, " ".join(" ".join(self._text).split())))
            self._href = None
            self._text = []


def _fetch_nku(topic: dict[str, Any], query: str, since: str, limits: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    tokens = [token.casefold() for token in re.findall(r"[a-zA-Z0-9]+", query) if len(token) > 2]
    for page in ("https://nkcs.iops.ai/", "https://nkcs.iops.ai/publications/"):
        html = _request_text(page, int(limits["http_timeout_seconds"]), int(limits["max_http_retries"]), "text/html")
        parser = _AnchorParser()
        parser.feed(html)
        for href, title in parser.items:
            if not title or not any(token in title.casefold() for token in tokens):
                continue
            source_url = urllib.parse.urljoin(page, href)
            rows.append(_base_record(
                topic, "nku", query, record_type="publication_or_project", title=title,
                authors=[], publication_date=None, publication_status="NKU site record",
                source_url=source_url, source_record_id=source_url, abstract="NKU publication/project page matched by title text; verify page contents manually.",
            ))
    return rows


PROVIDERS: dict[str, Callable[[dict[str, Any], str, str, dict[str, Any]], list[dict[str, Any]]]] = {
    "arxiv": _fetch_arxiv,
    "crossref": _fetch_crossref,
    "openalex": _fetch_openalex,
    "semantic_scholar": _fetch_semantic_scholar,
    "github": _fetch_github,
    "nku": _fetch_nku,
}


def _current_repo_commit(url: str, timeout: int) -> tuple[str | None, str | None]:
    repo = normalize_repo_url(url)
    if not repo:
        return None, "invalid repository URL"
    parsed = urllib.parse.urlsplit(repo)
    owner_repo = parsed.path.strip("/")
    try:
        metadata = _request_json(f"https://api.github.com/repos/{owner_repo}", timeout, 0)
        branch = metadata.get("default_branch") or "main"
        commits = _request_json(f"https://api.github.com/repos/{owner_repo}/commits?per_page=1", timeout, 0)
        sha = commits[0].get("sha") if commits else None
        return sha, branch
    except Exception as exc:  # The repository check is independent of paper search.
        return None, f"{type(exc).__name__}: {exc}"


def _merge_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    indexes: dict[str, int] = {}
    for raw in records:
        if not raw.get("title") and raw.get("record_type") != "repository":
            continue
        keys = candidate_identity_keys(raw)
        index = next((indexes[key] for key in sorted(keys) if key in indexes), None)
        if index is None:
            item = dict(raw)
            item["candidate_id"] = candidate_id(item)
            item["source_records"] = [{"source": raw.get("source_system"), "record_id": raw.get("source_record_id"), "url": raw.get("source_url"), "version": raw.get("source_version")}]
            merged.append(item)
            index = len(merged) - 1
        else:
            item = merged[index]
            _append_unique_source_records(item, [{"source": raw.get("source_system"), "record_id": raw.get("source_record_id"), "url": raw.get("source_url"), "version": raw.get("source_version")}])
            for field in ("doi", "arxiv_id", "venue", "publication_date", "abstract", "official_repository"):
                if raw.get(field) and not item.get(field):
                    item[field] = raw[field]
            if raw.get("arxiv_id"):
                item["arxiv_id"] = raw["arxiv_id"]
                item["source_version"] = raw.get("source_version")
            if raw.get("record_type") == "repository" and not item.get("official_repository"):
                item["official_repository"] = raw.get("official_repository")
            item.setdefault("source_systems", [])
            if raw.get("source_system") and raw["source_system"] not in item["source_systems"]:
                item["source_systems"].append(raw["source_system"])
        for key in keys:
            indexes[key] = index
        item_keys = candidate_identity_keys(merged[index])
        for key in item_keys:
            indexes[key] = index
    return merged


def _local_match(candidate: dict[str, Any], local_records: list[dict[str, Any]]) -> dict[str, Any] | None:
    keys = candidate_identity_keys(candidate)
    title_key = title_author_key(candidate)
    for local in local_records:
        local_keys = candidate_identity_keys(local)
        local_arxiv, local_version = normalize_arxiv(local.get("arxiv_id"))
        cand_arxiv, cand_version = normalize_arxiv(candidate.get("arxiv_id"))
        if keys & local_keys or (title_key and title_key == title_author_key(local)):
            match = dict(local)
            if cand_arxiv and local_arxiv and cand_arxiv == local_arxiv:
                match["local_arxiv_version"] = local_version
                match["candidate_arxiv_version"] = cand_version
            return match
    return None


def _version_number(value: str | None) -> int:
    match = re.search(r"v(\d+)$", value or "", re.I)
    return int(match.group(1)) if match else 0


def _priority(item: dict[str, Any], topics_by_id: dict[str, dict[str, Any]]) -> float:
    topic = topics_by_id.get(item.get("research_topic", ""), {})
    relevance = _relevance(item, topic)
    primary = 0.5 if item.get("source_system") in {"arxiv", "crossref", "openalex", "semantic_scholar", "nku"} else 0
    freshness_date = item.get("updated_at") or item.get("repository_pushed_at") or item.get("publication_date")
    freshness = 0.5 if freshness_date and freshness_date >= (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=365)).isoformat() else 0
    return round(float(topic.get("priority", 1)) + relevance * 0.5 + primary + freshness, 2)


_RELEVANCE_STOPWORDS = {"a", "an", "and", "for", "how", "in", "of", "on", "the", "to", "with", "agent", "agents", "llm"}


def _relevance(item: dict[str, Any], topic: dict[str, Any]) -> int:
    """Deterministic metadata relevance score; it does not infer paper quality."""
    text = normalize_title(" ".join(str(item.get(field) or "") for field in ("title", "abstract", "official_repository")))
    tokens = set(text.split())
    phrases = [normalize_title(str(value)) for value in topic.get("keywords", []) if value]

    def token_present(token: str) -> bool:
        return token in tokens or token + "s" in tokens or token.endswith("y") and token[:-1] + "ies" in tokens

    exact_phrases = sum(1 for phrase in phrases if phrase and (phrase in text or all(token_present(token) for token in phrase.split())))
    matched = set()
    for phrase in phrases:
        for token in phrase.split():
            if token in _RELEVANCE_STOPWORDS or len(token) < 4:
                continue
            if token_present(token):
                matched.add(token)
    return exact_phrases * 2 + len(matched)


def _is_relevant(item: dict[str, Any], topic: dict[str, Any]) -> bool:
    return _relevance(item, topic) >= 2


def _relevance_reason(item: dict[str, Any], topic: dict[str, Any]) -> str:
    text = normalize_title(" ".join(str(item.get(field) or "") for field in ("title", "abstract", "official_repository")))
    tokens = set(text.split())

    def present(token: str) -> bool:
        return token in tokens or token + "s" in tokens or token.endswith("y") and token[:-1] + "ies" in tokens

    matched = []
    for keyword in topic.get("keywords", []):
        phrase = normalize_title(str(keyword))
        if phrase and (phrase in text or all(present(token) for token in phrase.split())):
            matched.append(str(keyword))
    if matched:
        score = _relevance(item, topic)
        return f"Title/abstract metadata matched watchlist terms: {', '.join(matched)} (relevance score {score}, threshold 2); topical fit only, not a quality judgment."
    return f"Title/abstract passed deterministic relevance score {_relevance(item, topic)} (threshold 2); verify manually before reading, with no quality claim."


def _date_is_future(item: dict[str, Any]) -> bool:
    date_value = _iso_date(item.get("publication_date"))
    if not date_value:
        return False
    try:
        published = dt.date.fromisoformat(date_value)
    except ValueError:
        return False
    return published > dt.datetime.now(dt.timezone.utc).date()


def _append_unique_source_records(target: dict[str, Any], incoming: list[dict[str, Any]]) -> None:
    records = target.setdefault("source_records", [])
    seen = {(item.get("source"), item.get("record_id"), item.get("url"), item.get("version")) for item in records if isinstance(item, dict)}
    for item in incoming:
        key = (item.get("source"), item.get("record_id"), item.get("url"), item.get("version"))
        if key not in seen:
            records.append(item)
            seen.add(key)


def choose_topics(root: Path, config: dict[str, Any], requested: list[str] | None = None, auto: bool = False) -> list[dict[str, Any]]:
    active = [topic for topic in config.get("topics", []) if topic.get("enabled", False)]
    if requested:
        chosen = [topic for topic in active if topic["id"] in requested or topic.get("title", "").casefold() in {value.casefold() for value in requested}]
        missing = sorted(set(requested) - {topic["id"] for topic in chosen} - {topic.get("title", "") for topic in chosen})
        if missing:
            raise ValueError("unknown/disabled topic(s): " + ", ".join(missing))
        return chosen
    if not active:
        return []
    if not auto:
        return [max(active, key=lambda topic: (int(topic.get("priority", 0)), topic["id"]))]
    context_paths = [root / "notes/questions.md", *root.glob("notes/**/research-gaps.md"), *root.glob("notes/**/reading-roadmap.md"), *root.glob("notes/**/reviews/*.md")]
    chunks: list[str] = []
    for path in context_paths:
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            chunks.append(text[-8000:])
    context = "\n".join(chunks).casefold()
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for topic in active:
        terms = {normalize_title(word) for word in topic.get("keywords", [])}
        overlap = sum(1 for term in terms if len(term) > 3 and term in context)
        q_overlap = sum(1 for q in topic.get("research_questions", []) if any(part in context for part in re.findall(r"[a-z]{4,}|[\u4e00-\u9fff]{2,}", q.casefold())))
        scored.append((overlap + q_overlap, int(topic.get("priority", 0)), topic))
    scored.sort(key=lambda item: (-item[0], -item[1], item[2]["id"]))
    return [scored[0][2]]


def _cursor_key(topic_id: str, source: str, query: str) -> str:
    return f"{topic_id}|{source}|{stable_hash(query, 20)}"


def _find_duplicate_row(item: dict[str, Any], rows: list[dict[str, Any]]) -> int | None:
    keys = candidate_identity_keys(item)
    title_key = title_author_key(item)
    for index, existing in enumerate(rows):
        if keys & candidate_identity_keys(existing):
            return index
        if title_key and title_key == title_author_key(existing):
            return index
    return None


def discover(
    root: Path = ROOT,
    topic_ids: list[str] | None = None,
    auto: bool = False,
    initial_lookback_days: int | None = None,
    screen_limit: int | None = None,
    source_filter: set[str] | None = None,
    run_id: str | None = None,
    query_override: str | None = None,
    provider_overrides: dict[str, Callable[..., list[dict[str, Any]]]] | None = None,
) -> dict[str, Any]:
    evolution = root / "evolution"
    watchlist = load_config(evolution / "config" / "watchlist.yaml")
    limits = load_config(evolution / "config" / "limits.yaml")
    lookback = int(initial_lookback_days or limits["default_initial_lookback_days"])
    screen_limit = min(int(screen_limit or limits["max_screened_candidates_per_run"]), int(limits["max_screened_candidates_per_run"]))
    if query_override:
        query_override = query_override.strip()
        if not query_override:
            raise ValueError("query override cannot be empty")
        topic_id = "custom-" + stable_hash(query_override, 10)
        selected_topics = [{
            "id": topic_id, "group": "Custom", "title": query_override,
            "keywords": re.findall(r"[\w-]+", query_override), "query": query_override,
            "research_questions": [query_override], "concepts": [], "priority": 5,
            "sources": watchlist.get("default_sources", []), "enabled": True,
        }]
    else:
        selected_topics = choose_topics(root, watchlist, topic_ids, auto)
    if not selected_topics:
        return {"status": "no_topics", "topics": [], "sources_succeeded": [], "sources_failed": [], "candidates_found": 0}
    state_path = evolution / "state" / "discovery.json"
    candidates_path = evolution / "inbox" / "candidates.jsonl"
    lock_path = evolution / "state" / ".evolution.lock"
    run_id = run_id or f"discovery-{utc_now().replace(':', '').replace('-', '')}"
    source_results: list[dict[str, Any]] = []
    raw_records: list[dict[str, Any]] = []
    provider_map = dict(PROVIDERS)
    if provider_overrides:
        provider_map.update(provider_overrides)

    with file_lock(lock_path):
        state = read_json(state_path, {"version": 1, "cursors": {}, "topic_last_queried_at": {}, "repo_versions": {}})
        old_rows = read_jsonl(candidates_path)
        # A stable snapshot prevents a failed process from advancing cursors
        # without first persisting its candidates.
        calls: list[tuple[dict[str, Any], str, str, str, str, bool]] = []
        for topic in selected_topics:
            query = _query_string(topic)
            for source in topic.get("sources", watchlist.get("default_sources", [])):
                if source_filter and source not in source_filter:
                    continue
                if source not in provider_map:
                    source_results.append({"topic": topic["id"], "source": source, "status": "unsupported", "error": "provider not implemented"})
                    continue
                cursor_key = _cursor_key(topic["id"], source, query)
                previous = state["cursors"].get(cursor_key)
                if previous and previous.get("last_successful_at"):
                    stamp = dt.datetime.fromisoformat(previous["last_successful_at"].replace("Z", "+00:00"))
                    since = (stamp.date() - dt.timedelta(days=int(limits["overlap_days"]))).isoformat()
                    resumed = True
                else:
                    since = (dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=lookback)).isoformat()
                    resumed = False
                calls.append((topic, source, query, since, cursor_key, resumed))

        def call_provider(call: tuple[dict[str, Any], str, str, str, str, bool]) -> tuple[dict[str, Any], list[dict[str, Any]] | None, str | None]:
            topic, source, query, since, _, _ = call
            try:
                provider = provider_map[source]
                return call, provider(topic, query, since, limits), None
            except Exception as exc:
                return call, None, f"{type(exc).__name__}: {exc}"

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, max(1, len(calls)))) as pool:
            results = list(pool.map(call_provider, calls))

        successful_keys: list[tuple[str, dict[str, Any]]] = []
        for (topic, source, query, since, cursor_key, resumed), rows, error in results:
            if error is not None:
                source_results.append({"topic": topic["id"], "source": source, "query": query, "status": "failed", "error": error, "cursor_before": state["cursors"].get(cursor_key)})
                continue
            titled = [row for row in (rows or []) if row.get("title")]
            future = [row for row in titled if _date_is_future(row)]
            dated = [row for row in titled if row not in future]
            cleaned = [row for row in dated if _is_relevant(row, topic) or row.get("source_system") == "github-tracked"]
            source_results.append({
                "topic": topic["id"], "source": source, "query": query, "status": "success",
                "since": since, "resumed": resumed, "result_count": len(titled),
                "relevant_count": len(cleaned), "rejected_irrelevant_count": len(dated) - len(cleaned),
                "rejected_future_date_count": len(future),
            })
            successful_keys.append((cursor_key, {"query": query, "topic_id": topic["id"], "source": source, "since": since}))
            raw_records.extend(cleaned)

        # Poll explicitly watched repositories independently from keyword search.
        # A failure on one repository does not affect the paper-query cursor.
        topics_by_id = {topic["id"]: topic for topic in selected_topics}
        for repo_record in watchlist.get("tracked_repositories", []) if not source_filter or "github" in source_filter or "github-tracked" in source_filter else []:
            if not set(repo_record.get("topic_ids", [])) & set(topics_by_id):
                continue
            url = normalize_repo_url(repo_record.get("url"))
            if not url:
                continue
            repo_key = url
            sha, branch_or_error = _current_repo_commit(url, int(limits["http_timeout_seconds"]))
            if not sha:
                source_results.append({"topic": sorted(set(repo_record.get("topic_ids", [])) & set(topics_by_id))[0], "source": "github-tracked", "status": "failed", "repository": url, "error": branch_or_error})
                continue
            prior_sha = state.get("repo_versions", {}).get(repo_key, {}).get("commit")
            event = "version_update" if prior_sha and prior_sha != sha else "tracked_repository"
            if prior_sha != sha:
                first_topic_id = sorted(set(repo_record.get("topic_ids", [])) & set(topics_by_id))[0]
                topic = topics_by_id[first_topic_id]
                raw_records.append(_base_record(
                    topic, "github-tracked", url, record_type="repository", title=url.removeprefix("https://github.com/"),
                    authors=[], publication_date=utc_now()[:10], publication_status="repository version event",
                    source_url=url, official_repository=url, source_version=sha, source_record_id=url,
                ) | {"repository_commit": sha, "repository_branch": branch_or_error, "event_type": event, "previous_repository_commit": prior_sha})
                state.setdefault("repo_versions", {})[repo_key] = {"commit": sha, "branch": branch_or_error, "checked_at": utc_now()}
            source_results.append({"topic": ",".join(sorted(set(repo_record.get("topic_ids", [])) & set(topics_by_id))), "source": "github-tracked", "status": "success", "repository": url, "commit": sha, "previous_commit": prior_sha, "event_type": event})

        merged_new = _merge_records(raw_records)
        local_records = existing_knowledge_identities(root)
        topics_map = {topic["id"]: topic for topic in selected_topics}
        added_ids: list[str] = []
        updated_ids: list[str] = []
        for item in merged_new:
            match_index = _find_duplicate_row(item, old_rows)
            local = _local_match(item, local_records)
            item["relevance_reason"] = _relevance_reason(item, topics_map.get(item.get("research_topic", ""), {}))
            item["novelty_reason"] = (
                f"Existing local identity match: {local.get('path')}; compare versions or mark duplicate."
                if local else
                "No indexed local DOI/arXiv/repository/title-author identity match found; potential KB novelty only, methods not yet compared."
            )
            if match_index is None:
                item["status"] = "discovered"
                item["priority"] = _priority(item, topics_map)
                if local:
                    item["related_paper_note"] = local.get("path")
                    item["existing_knowledge_match"] = True
                    incoming_arxiv, incoming_ver = normalize_arxiv(item.get("arxiv_id"))
                    local_arxiv, local_ver = normalize_arxiv(local.get("arxiv_id"))
                    if item.get("record_type") == "repository":
                        incoming_sha = item.get("repository_commit") or item.get("source_version")
                        local_sha = local.get("repo_sha")
                        if local_sha and incoming_sha == local_sha:
                            item["status"] = "duplicate"
                            item["event_type"] = "repository_version_already_known"
                        else:
                            item["event_type"] = "version_update"
                            item["previous_repository_commit"] = local_sha
                    elif incoming_arxiv and local_arxiv and incoming_arxiv == local_arxiv and _version_number(incoming_ver) > _version_number(local_ver):
                        item["event_type"] = "version_update"
                        item["previous_version"] = local.get("arxiv_id")
                    else:
                        item["status"] = "duplicate"
                        item["event_type"] = "publication_or_existing_note_match"
                item["candidate_id"] = candidate_id(item)
                old_rows.append(item)
                added_ids.append(item["candidate_id"])
            else:
                existing = old_rows[match_index]
                existing["relevance_reason"] = item["relevance_reason"]
                if not existing.get("novelty_reason") or existing.get("novelty_reason", "").startswith("Pending"):
                    existing["novelty_reason"] = item["novelty_reason"]
                _append_unique_source_records(existing, item.get("source_records", []))
                for field in ("doi", "arxiv_id", "venue", "publication_date", "official_repository"):
                    if item.get(field) and (not existing.get(field) or field == "arxiv_id"):
                        existing[field] = item[field]
                old_version = existing.get("source_version")
                new_version = item.get("source_version")
                incoming_base, incoming_ver = normalize_arxiv(item.get("arxiv_id"))
                existing_base, existing_ver = normalize_arxiv(existing.get("arxiv_id"))
                if incoming_base and existing_base == incoming_base and _version_number(incoming_ver) > _version_number(existing_ver):
                    existing.setdefault("version_updates", []).append({"from": existing.get("arxiv_id"), "to": item.get("arxiv_id"), "detected_at": utc_now()})
                    existing["event_type"] = "version_update"
                    existing["arxiv_id"] = item.get("arxiv_id")
                    existing["source_version"] = incoming_ver
                    if existing.get("status") in {"duplicate", "deferred", "rejected"}:
                        existing["status"] = "discovered"
                    updated_ids.append(existing["candidate_id"])
                elif item.get("record_type") == "repository" and old_version and new_version and old_version != new_version:
                    existing.setdefault("version_updates", []).append({"from": old_version, "to": new_version, "detected_at": utc_now()})
                    existing["event_type"] = "version_update"
                    existing["source_version"] = new_version
                    existing["status"] = "discovered"
                    updated_ids.append(existing["candidate_id"])
                if local and not existing.get("related_paper_note"):
                    existing["related_paper_note"] = local.get("path")
                    existing["existing_knowledge_match"] = True
        # Save all safely fetched records before advancing any source cursor.
        old_rows.sort(key=lambda row: (row.get("research_topic", ""), row.get("candidate_id", "")))
        atomic_write_jsonl(candidates_path, old_rows)
        saved_at = utc_now()
        for cursor_key, entry in successful_keys:
            state.setdefault("cursors", {})[cursor_key] = {
                **entry,
                "last_successful_at": saved_at,
                "result_count": next((row["result_count"] for row in source_results if row.get("query") == entry["query"] and row.get("source") == entry["source"] and row.get("topic") == entry["topic_id"] and row["status"] == "success"), 0),
                "overlap_days": int(limits["overlap_days"]),
            }
            state.setdefault("topic_last_queried_at", {})[entry["topic_id"]] = saved_at
        state["last_discovery_run"] = run_id
        state["last_updated_at"] = saved_at
        state["version"] = 1
        atomic_write_json(state_path, state)

        # Screen only new/updated non-duplicate candidates. Existing decisions
        # remain stable; candidate scoring never silently requeues a rejection.
        pending = [row for row in old_rows if row.get("status") == "discovered"]
        pending.sort(key=lambda row: (-float(row.get("priority", 0)), row.get("publication_date") or "", row.get("candidate_id", "")))
        screened_ids = {row["candidate_id"] for row in pending[:screen_limit]}
        for row in pending:
            row["status"] = "screened" if row["candidate_id"] in screened_ids else "deferred"
            row["screened_at"] = utc_now()
        if pending:
            atomic_write_jsonl(candidates_path, old_rows)

        status = "success" if any(item.get("status") == "success" for item in source_results) and not any(item.get("status") == "failed" for item in source_results) else "partial" if any(item.get("status") == "success" for item in source_results) else "failed"
        return {
            "run_id": run_id,
            "status": status,
            "topics": [topic["id"] for topic in selected_topics],
            "focus_selection": "explicit" if topic_ids else "gap/question ranking" if auto else "highest configured priority",
            "source_results": source_results,
            "sources_succeeded": sum(1 for item in source_results if item.get("status") == "success"),
            "sources_failed": sum(1 for item in source_results if item.get("status") == "failed"),
            "records_fetched": len(raw_records),
            "candidates_found": len(merged_new),
            "candidates_added": len(added_ids),
            "duplicates": sum(1 for row in merged_new if row.get("status") == "duplicate"),
            "candidate_version_updates": len(updated_ids) + sum(1 for item in merged_new if item.get("event_type") == "version_update"),
            "screened_this_run": len(screened_ids),
            "candidate_ids": sorted(added_ids),
            "candidate_file": candidates_path.relative_to(root).as_posix(),
            "cursor_state": state_path.relative_to(root).as_posix(),
            "finished_at": saved_at,
        }


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Incrementally discover research papers and repositories.")
    parser.add_argument("--topic", action="append", dest="topics", help="watchlist topic id; repeat to select more than one")
    parser.add_argument("--auto", action="store_true", help="select the highest scoring topic from Questions, Research Gaps, Roadmaps, and Reviews")
    parser.add_argument("--days", type=int, help="initial lookback window; existing query cursors use overlap windows")
    parser.add_argument("--screen-limit", type=int)
    parser.add_argument("--source", action="append", dest="sources", help="restrict to a provider id; repeatable")
    parser.add_argument("--query", help="explicit research query; creates a temporary topic with its own cursors")
    parser.add_argument("--run-id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = discover(topic_ids=args.topics, auto=args.auto, initial_lookback_days=args.days, screen_limit=args.screen_limit, source_filter=set(args.sources) if args.sources else None, run_id=args.run_id, query_override=args.query)
    except Exception as exc:
        print(f"discovery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output if args.json else f"Discovery {result.get('status')}: {result.get('candidates_added', 0)} candidates added; {result.get('screened_this_run', 0)} screened; {result.get('sources_failed', 0)} source queries failed.")
    return 0 if result.get("status") in {"success", "partial", "no_topics"} else 1


if __name__ == "__main__":
    raise SystemExit(_main())
