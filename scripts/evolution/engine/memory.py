from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts.evolution.common import read_jsonl
from scripts.evolution.engine.local_sources import find_local_paper_material


def _open_questions(root: Path, limit: int = 30) -> list[str]:
    path = root / "notes" / "questions.md"
    if not path.is_file():
        return []
    result: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.search(r"\|\s*(?:Open|Partially Answered)\s*\|", line, re.I):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if cells:
                result.append(cells[0])
    if not result:
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if re.search(r"(?:仍未解决|仍开放|仍未回答|Open Question)", line, re.I):
                cleaned = re.sub(r"^\s*[-*]\s*", "", line).strip()
                if cleaned and len(cleaned) < 400:
                    result.append(cleaned)
    return result[:limit]


def initial_memory(root: Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    context_limits = (config or {}).get("context", {})
    summary_limit = max(1000, int(context_limits.get("phase1_summary_chars", 5000)))
    question_limit = max(1, int(context_limits.get("open_questions", 20)))
    candidate_limit = max(1, int(context_limits.get("planner_candidates", 12)))
    abstract_limit = max(100, int(context_limits.get("candidate_abstract_chars", 400)))
    report_path = root / "evolution" / "runs" / "first-evolution-report.md"
    report = report_path.read_text(encoding="utf-8", errors="replace") if report_path.exists() else ""
    candidate_rows = read_jsonl(root / "evolution" / "inbox" / "candidates.jsonl")
    relevant = [row for row in candidate_rows if row.get("research_topic") in {"agent-memory", "self-evolving-agent"} and row.get("status") not in {"rejected", "duplicate"}]
    relevant.sort(key=lambda row: (row.get("status") not in {"queued", "reading", "deferred"}, -float(row.get("priority", 0)), row.get("publication_date") or ""), reverse=False)
    candidate_queue = []
    for row in relevant[:candidate_limit]:
        candidate = {
            key: (str(row.get(key) or "")[:abstract_limit] if key == "abstract" else row.get(key))
            for key in ("candidate_id", "title", "authors", "publication_date", "publication_status", "arxiv_id", "doi", "source_url", "source_version", "official_repository", "research_topic", "related_questions", "related_concepts", "novelty_reason", "relevance_reason", "priority", "status", "abstract")
            if key in row
        }
        material = find_local_paper_material(root, row)
        if any(material.values()):
            candidate["local_paper_material"] = material
        candidate_queue.append(candidate)
    claims = read_jsonl(root / "evolution" / "claims" / "claims.jsonl")
    proposal_dir = root / "evolution" / "proposals"
    proposals = []
    for path in sorted(proposal_dir.glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        proposals.append({"proposal_id": item.get("proposal_id"), "status": item.get("status"), "title": item.get("title"), "files": item.get("files", [])})
    question_list = _open_questions(root, question_limit)
    return {
        "phase1_summary": report[:summary_limit],
        "open_questions": question_list,
        "claims": claims,
        "pending_proposals": [item for item in proposals if item.get("status") in {"draft", "approved"}],
        "candidate_queue": candidate_queue,
        "historical_audit_baseline": {"run_id": "first-evolution-20261125-v2", "finding_count": 58, "files_scanned": 358, "status": "historical; compare by signature, do not treat as new regressions"},
    }


def planner_memory(base: dict[str, Any], state: dict[str, Any], round_number: int, discovery: dict[str, Any] | None) -> dict[str, Any]:
    previous = []
    for key in sorted(state.get("rounds", {}), key=lambda value: int(value)):
        item = state["rounds"][key]
        if int(key) >= round_number:
            continue
        evaluation = item.get("evaluation", {})
        reflection = item.get("reflection", {})
        previous.append({
            "round": int(key),
            "plan": {field: item.get("plan", {}).get(field) for field in ("decision", "topic_id", "research_question", "candidate_ids", "feedback_refs")},
            "knowledge_gain": {
                "accepted_findings": [
                    {field: finding.get(field) for field in ("finding_id", "statement", "scope", "relation")}
                    for finding in item.get("knowledge_gain", {}).get("accepted_findings", [])
                ],
                "feedback_ids": item.get("knowledge_gain", {}).get("feedback_ids", []),
                "gap_progress": item.get("knowledge_gain", {}).get("gap_progress", [])[:8],
                "next_step_impact": item.get("knowledge_gain", {}).get("next_step_impact", "")[:500],
            },
            "evaluation": {
                "decision": evaluation.get("decision"),
                "rationale": evaluation.get("rationale", "")[:500],
                "gap_progress": evaluation.get("gap_progress", [])[:8],
            },
            "reflection": {
                "knowledge_summary": reflection.get("knowledge_summary", [])[:8],
                "remaining_gaps": reflection.get("remaining_gaps", [])[:8],
                "feedback_refs": reflection.get("feedback_refs", [])[:16],
                "next_step": reflection.get("next_step", "")[:400],
            },
            "unresolved_questions": item.get("unresolved_questions", [])[:10],
            "unresolved_question_ids": item.get("unresolved_question_ids", []),
        })
    discovery_summary = {
        key: (discovery or {}).get(key)
        for key in ("status", "candidates_added", "candidate_version_updates", "duplicates")
    }
    return {"initial": base, "fresh_discovery": discovery_summary, "previous_rounds": previous, "remaining_model_calls": state.get("remaining_calls"), "remaining_full_reads": state.get("remaining_full_reads")}


def executor_memory(current: dict[str, Any], plan: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    limits = config.get("context", {})
    initial = current.get("initial", {})
    candidate_ids = set(plan.get("candidate_ids", []))
    candidates = [row for row in initial.get("candidate_queue", []) if row.get("candidate_id") in candidate_ids]
    claims = initial.get("claims", [])
    relevant_claims = [
        row for row in claims
        if row.get("claim_id") in {
            claim_id for candidate in candidates for claim_id in candidate.get("related_claim_ids", [])
        }
    ]
    if not relevant_claims:
        relevant_claims = claims[:int(limits.get("executor_claims", 8))]
    compact_claims = [
        {
            "claim_id": row.get("claim_id"),
            "statement": str(row.get("statement", ""))[:500],
            "scope": str(row.get("scope", ""))[:250],
            "status": row.get("status"),
            "evidence": [
                {key: evidence.get(key) for key in ("source_id", "source_version", "source_uri", "locator", "relation")}
                for evidence in row.get("evidence", [])[:2]
            ],
            "related_claims": row.get("related_claims", [])[:8],
            "supersedes": row.get("supersedes", [])[:8],
        }
        for row in relevant_claims[:int(limits.get("executor_claims", 8))]
    ]
    selected_questions = list(initial.get("open_questions", []))[:int(limits.get("open_questions", 10))]
    return {
        "phase1_summary": str(initial.get("phase1_summary", ""))[:int(limits.get("executor_summary_chars", 1800))],
        "open_questions": selected_questions,
        "claims": compact_claims,
        "pending_proposals": [
            {key: row.get(key) for key in ("proposal_id", "status", "title")}
            for row in initial.get("pending_proposals", [])[:6]
        ],
        "candidate_queue": [
            {key: (str(row.get(key) or "")[:int(limits.get("candidate_abstract_chars", 240))] if key == "abstract" else row.get(key))
             for key in ("candidate_id", "title", "publication_date", "arxiv_id", "doi", "source_url", "source_version", "official_repository", "related_questions", "priority", "status", "abstract", "local_paper_material")
             if key in row}
            for row in candidates[:4]
        ],
        "fresh_discovery": current.get("fresh_discovery", {}),
        "previous_rounds": current.get("previous_rounds", [])[-2:],
        "remaining_model_calls": current.get("remaining_model_calls"),
        "remaining_full_reads": current.get("remaining_full_reads"),
    }
