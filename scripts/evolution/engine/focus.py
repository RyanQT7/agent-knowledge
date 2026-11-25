from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from scripts.evolution.common import normalize_title, stable_hash
from scripts.evolution.discovery import choose_topics, load_config


_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "by", "for", "from", "how", "in",
    "into", "is", "of", "on", "or", "the", "to", "under", "using", "what",
    "when", "where", "which", "with", "research", "paper", "papers", "latest",
    "recent", "new", "current", "study", "studies", "topic", "topics", "agent", "agents", "llm",
}
_AUTO_VALUES = {"auto", "automatic", "highest-priority gap", "current knowledge gap"}


def _tokens(value: str) -> set[str]:
    normalized = normalize_title(value)
    tokens = {
        token for token in re.findall(r"[a-z0-9]+", normalized)
        if len(token) > 2 and token not in _STOPWORDS
    }
    for run in re.findall(r"[一-鿿]+", normalized):
        if len(run) <= 2:
            tokens.add(run)
        else:
            tokens.update(run[index:index + 2] for index in range(len(run) - 1))
    return tokens


def terms_for_text(value: str) -> set[str]:
    return _tokens(value)


def _topic_text(topic: dict[str, Any], fields: tuple[str, ...]) -> str:
    values: list[str] = []
    for field in fields:
        value = topic.get(field)
        if isinstance(value, list):
            values.extend(str(item) for item in value)
        elif value:
            values.append(str(value))
    return " ".join(values)


def _topic_score(focus_tokens: set[str], topic: dict[str, Any], focus: str) -> float:
    title = _tokens(_topic_text(topic, ("id", "title", "group")))
    keywords = _tokens(_topic_text(topic, ("keywords",)))
    questions = _tokens(_topic_text(topic, ("research_questions",)))
    score = 4 * len(focus_tokens & title) + 2 * len(focus_tokens & keywords) + 0.5 * len(focus_tokens & questions)
    normalized_focus = normalize_title(focus)
    normalized_topic = normalize_title(_topic_text(topic, ("id", "title", "group", "keywords")))
    if normalized_focus and normalized_focus in normalized_topic:
        score += 8
    return score


def _index_concept_paths(root: Path) -> tuple[list[Path], list[str]]:
    index_path = root / "INDEX.md"
    indexed: list[Path] = []
    index_lines: list[str] = []
    if index_path.is_file():
        text = index_path.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", line):
                relative = target.split("#", 1)[0]
                if not relative.startswith("concepts/"):
                    continue
                path = (root / relative).resolve()
                try:
                    path.relative_to(root.resolve())
                except ValueError:
                    continue
                if path.is_file():
                    indexed.append(path)
                    index_lines.append(line.strip())
    fallback = list((root / "concepts").rglob("*.md")) if (root / "concepts").is_dir() else []
    all_paths = list(dict.fromkeys(indexed + fallback))
    return all_paths, index_lines


def _blocks(text: str) -> list[str]:
    result: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        lines = [line.strip() for line in paragraph.splitlines() if line.strip()]
        if len(lines) > 1 and all(line.startswith("|") or line.startswith("-") for line in lines):
            result.extend(lines)
        elif paragraph.strip():
            result.append(" ".join(lines))
    return result


def _ranked_blocks(path: Path, text: str, terms: set[str], limit: int, max_chars: int, min_score: int = 1) -> list[dict[str, Any]]:
    ranked = []
    for index, block in enumerate(_blocks(text)):
        score = len(_tokens(block) & terms)
        if score >= min_score:
            ranked.append((score, index, block))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [
        {"path": str(path), "excerpt": block[:max_chars], "match_score": score}
        for score, _, block in ranked[:limit]
    ]


def _read_text(path: Path, limit: int = 160_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _knowledge_context(root: Path, terms: set[str]) -> dict[str, Any]:
    min_score = 1 if len(terms) <= 1 else 2
    concepts: list[dict[str, Any]] = []
    concept_paths, index_lines = _index_concept_paths(root)
    concept_ranked: list[tuple[int, str, Path, str]] = []
    for path in concept_paths:
        text = _read_text(path)
        path_score = len(_tokens(path.relative_to(root).as_posix()) & terms)
        content_score = len(_tokens(text[:16_000]) & terms)
        score = path_score * 8 + content_score
        if path_score or content_score >= max(3, min_score):
            concept_ranked.append((score, path.as_posix(), path, text))
    concept_ranked.sort(key=lambda item: (-item[0], item[1]))
    for score, _, path, text in concept_ranked[:4]:
        blocks = _ranked_blocks(path, text, terms, 2, 250, min_score)
        concepts.append({
            "path": path.relative_to(root).as_posix(),
            "title": next((line.lstrip("# ").strip() for line in text.splitlines() if line.startswith("# ")), path.stem),
            "excerpt": "\n".join(item["excerpt"] for item in blocks)[:550],
            "match_score": score,
        })
    matched_index = [line for line in index_lines if len(_tokens(line) & terms) >= min_score][:10]

    question_paths = [root / "notes" / "questions.md", *root.glob("notes/**/questions.md")]
    questions: list[dict[str, str]] = []
    for path in dict.fromkeys(question_paths):
        if not path.is_file():
            continue
        for line in _read_text(path).splitlines():
            if not re.search(r"\|\s*(?:Open|Partially Answered)\s*\|", line, re.I):
                continue
            score = len(_tokens(line) & terms)
            if score >= min_score:
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if cells:
                    questions.append({"path": path.relative_to(root).as_posix(), "question": cells[0][:300], "context": " | ".join(cells[1:])[:240], "match_score": str(score)})
    questions.sort(key=lambda item: (-int(item["match_score"]), item["path"], item["question"]))

    def collect(pattern: str, max_items: int, max_chars: int) -> list[dict[str, Any]]:
        ranked: list[dict[str, Any]] = []
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            ranked.extend(_ranked_blocks(path, _read_text(path), terms, 4, max_chars, min_score))
        ranked.sort(key=lambda item: (-item["match_score"], item["path"], item["excerpt"]))
        for item in ranked[:max_items]:
            item["path"] = Path(item["path"]).relative_to(root).as_posix()
        return ranked[:max_items]

    return {
        "related_concepts": concepts,
        "index_refs": matched_index,
        "open_questions": questions[:10],
        "research_gaps": collect("notes/**/research-gaps.md", 4, 450),
        "reading_roadmaps": collect("notes/**/reading-roadmap.md", 2, 400),
        "recent_reviews": collect("notes/**/reviews/*.md", 2, 400),
    }


def resolve_focus(root: Path, focus: str | None) -> dict[str, Any]:
    root = root.resolve()
    watchlist = load_config(root / "evolution" / "config" / "watchlist.yaml")
    active = [topic for topic in watchlist.get("topics", []) if topic.get("enabled", False)]
    requested = (focus or "").strip()
    is_auto = not requested or requested.casefold() in _AUTO_VALUES
    selection = ""
    query_override = None
    if is_auto:
        selected = choose_topics(root, watchlist, auto=True)
        selection = "highest-ranked existing research gap/question"
        if not selected:
            raise ValueError("No enabled watchlist topics are available for automatic focus selection.")
        focus_label = "Auto: " + ", ".join(str(topic.get("title") or topic["id"]) for topic in selected)
    else:
        focus_tokens = _tokens(requested)
        normalized_request = normalize_title(requested)
        exact_group_names = {
            str(topic.get("group", ""))
            for topic in active
            if normalized_request and normalized_request == normalize_title(str(topic.get("group", "")))
        }
        exact_group = [topic for topic in active if topic.get("group") in exact_group_names]
        if not exact_group:
            exact_group = [
                topic for topic in active
                if focus_tokens and focus_tokens == _tokens(str(topic.get("group", "")))
            ]
        if exact_group:
            groups = {str(topic.get("group", "")) for topic in exact_group}
            selected = [topic for topic in active if topic.get("group") in groups]
            selection = "watchlist group match"
        else:
            ranked = sorted(
                ((_topic_score(focus_tokens, topic, requested), topic) for topic in active),
                key=lambda item: (-item[0], item[1].get("id", "")),
            )
            best = ranked[0][0] if ranked else 0
            selected = [topic for score, topic in ranked if score >= max(2, best * 0.5)][:6]
            selection = "watchlist title/keyword match" if selected else "custom user topic"
        focus_label = requested
        if not selected:
            custom_id = "custom-" + stable_hash(requested, 10)
            selected = [{
                "id": custom_id,
                "group": "Custom",
                "title": requested,
                "keywords": re.findall(r"[\w-]+", requested, flags=re.UNICODE),
                "research_questions": [f"What methods, evidence, limits, and unresolved questions apply to {requested}?"],
                "sources": watchlist.get("default_sources", []),
                "priority": 5,
                "enabled": True,
            }]
            query_override = requested

    topic_ids = [str(topic["id"]) for topic in selected]
    topic_sources = sorted({source for topic in selected for source in topic.get("sources", watchlist.get("default_sources", []))})
    topic_questions = list(dict.fromkeys(
        str(question).strip()
        for topic in selected
        for question in topic.get("research_questions", [])
        if str(question).strip()
    ))
    terms = _tokens(focus_label + " " + _topic_text({
        "keywords": [keyword for topic in selected for keyword in topic.get("keywords", [])],
        "title": " ".join(str(topic.get("title", "")) for topic in selected),
    }, ("title", "keywords")))
    context = _knowledge_context(root, terms)
    context_questions = [item["question"] for item in context["open_questions"]]
    research_questions = list(dict.fromkeys(topic_questions + context_questions))
    if not topic_questions:
        research_questions.insert(0, f"What are the current evidence-backed methods, limits, and open problems for {focus_label}?")
    topic_overrides: dict[str, dict[str, Any]] = {}
    concept_paths = [item["path"] for item in context["related_concepts"]]
    for topic in selected:
        override = {
            "concepts": concept_paths,
            "research_questions": list(dict.fromkeys(
                [str(item) for item in topic.get("research_questions", [])] + context_questions[:6]
            )),
        }
        if requested and not query_override:
            query_phrases = [requested] + [str(value) for value in topic.get("keywords", [])[:4]]
            override["query"] = " OR ".join(f'"{phrase}"' for phrase in dict.fromkeys(query_phrases) if phrase)
        topic_overrides[str(topic["id"])] = override
    return {
        "research_focus": focus_label,
        "selection": selection,
        "topic_ids": topic_ids,
        "query_override": query_override,
        "sources": topic_sources,
        "topics": [{
            "id": str(topic["id"]),
            "group": str(topic.get("group", "")),
            "title": str(topic.get("title", "")),
            "keywords": list(topic.get("keywords", [])),
            "research_questions": list(topic.get("research_questions", [])),
            "priority": int(topic.get("priority", 0)),
        } for topic in selected],
        "research_questions": research_questions[:18],
        "terms": sorted(terms),
        "research_context": context,
        "topic_overrides": topic_overrides,
    }


def apply_focus_to_config(config: dict[str, Any], resolution: dict[str, Any]) -> None:
    config["focus_resolution"] = resolution
    config["allowed_topic_ids"] = list(resolution["topic_ids"])
    discovery = config.setdefault("discovery", {})
    discovery["topic_ids"] = list(resolution["topic_ids"])
    discovery["query_override"] = resolution.get("query_override")
    discovery["sources"] = list(resolution.get("sources", []))
    discovery["topic_overrides"] = resolution.get("topic_overrides", {})
