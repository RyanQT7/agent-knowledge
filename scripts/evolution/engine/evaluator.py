from __future__ import annotations

import datetime as dt
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from scripts.evolution.common import normalize_arxiv, normalize_doi, normalize_title


ALLOWED_SOURCE_HOSTS = {
    "arxiv.org", "doi.org", "dx.doi.org", "openreview.net", "aclanthology.org", "proceedings.mlr.press",
    "dl.acm.org", "acm.org", "ieeexplore.ieee.org", "usenix.org", "proceedings.neurips.cc", "proceedings.mlsys.org",
    "jmlr.org", "nature.com", "sciencedirect.com", "link.springer.com", "github.com", "nkcs.iops.ai",
    "openalex.org", "api.crossref.org", "semanticscholar.org",
}


def verify_source_uri(uri: str, timeout: int = 10, getter: Callable[[str, int], tuple[bool, str]] | None = None) -> tuple[bool, str]:
    parsed = urllib.parse.urlparse(uri)
    if parsed.scheme != "https" or not parsed.hostname:
        return False, "evidence URL must be HTTPS"
    host = parsed.hostname.lower().removeprefix("www.")
    if not any(host == allowed or host.endswith("." + allowed) for allowed in ALLOWED_SOURCE_HOSTS):
        return False, f"source host is outside the configured primary-source allowlist: {host}"
    if getter:
        return getter(uri, timeout)
    request = urllib.request.Request(uri, headers={"User-Agent": "agent-knowledge-evolution/1.5", "Accept": "text/html,application/pdf,application/json"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response.read(1024)
            if int(getattr(response, "status", 200)) >= 400:
                return False, f"source returned HTTP {response.status}"
            return True, f"HTTP {getattr(response, 'status', 200)} {response.geturl()}"
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, f"source could not be verified: {type(exc).__name__}: {exc}"


def _identity_matches(item: dict[str, Any]) -> bool:
    source_id = item.get("source_id", "").strip().lower()
    uri = item.get("source_uri", "")
    arxiv_base, uri_version = normalize_arxiv(uri)
    item_base, item_version = normalize_arxiv(source_id)
    if source_id.startswith("arxiv:"):
        if not arxiv_base or arxiv_base != item_base:
            return False
        version_base, version = normalize_arxiv(item.get("source_version"))
        return version_base in (None, item_base) and version in (uri_version, item_version)
    if source_id.startswith("doi:"):
        return normalize_doi(source_id[4:]) in normalize_doi(uri or "") if normalize_doi(uri or "") else False
    return bool(source_id and uri)


def deterministic_evaluation(execution: dict[str, Any], plan: dict[str, Any], goal: dict[str, Any], existing_claims: list[dict[str, Any]], existing_findings: list[dict[str, Any]] | None = None, source_getter: Callable[[str, int], tuple[bool, str]] | None = None) -> dict[str, Any]:
    hard_errors: list[dict[str, str]] = []
    soft_notes: list[dict[str, str]] = []
    papers = execution.get("papers", [])
    full_reads = [paper for paper in papers if paper.get("reading_extent") == "full_text"]
    if len(full_reads) > min(int(plan.get("max_full_reads", 0)), int(goal["budgets"]["max_full_reads"])):
        hard_errors.append({"type": "budget", "evidence": "reported full reads exceed the immutable per-task budget"})
    today = dt.date.today()
    for paper in papers:
        raw_date = paper.get("publication_date")
        if raw_date:
            try:
                pub_date = dt.date.fromisoformat(str(raw_date)[:10])
                if pub_date > today:
                    hard_errors.append({"type": "future_date", "evidence": f"{paper.get('source_id')}: {raw_date} is later than {today.isoformat()}"})
            except ValueError:
                soft_notes.append({"type": "date_unparseable", "evidence": f"{paper.get('source_id')}: {raw_date}"})
        if not _identity_matches(paper):
            hard_errors.append({"type": "source_identity", "evidence": f"source ID/version does not match URI: {paper.get('source_id')} {paper.get('source_version')} {paper.get('source_uri')}"})
        verified, detail = verify_source_uri(str(paper.get("source_uri", "")), getter=source_getter)
        if not verified:
            hard_errors.append({"type": "source_unavailable", "evidence": f"{paper.get('source_uri')}: {detail}"})
        paper["source_verification"] = {"verified": verified, "detail": detail}
        if paper.get("reading_extent") in {"sections_only", "abstract_only", "metadata_only"}:
            soft_notes.append({"type": "partial_read", "evidence": f"{paper.get('source_id')} read extent: {paper.get('reading_extent')}"})
        if not paper.get("locators") and paper.get("reading_extent") != "metadata_only":
            hard_errors.append({"type": "missing_locator", "evidence": f"{paper.get('source_id')} has no section/equation/table locator"})
    normalized_existing = {normalize_title(item.get("statement")) for item in existing_claims}
    known_claim_ids = {item.get("claim_id") for item in existing_claims}
    normalized_existing.update(normalize_title(item.get("statement")) for item in (existing_findings or []))
    seen_statements: set[str] = set()
    known_finding_ids = {item.get("finding_id") for item in execution.get("findings", [])}
    known_finding_ids.update(item.get("finding_id") for item in (existing_findings or []))
    for finding in execution.get("findings", []):
        if finding.get("source_uri") not in {paper.get("source_uri") for paper in papers}:
            hard_errors.append({"type": "unlisted_evidence", "evidence": f"{finding.get('finding_id')} points to a source absent from the reviewed paper list"})
        if not _identity_matches(finding):
            hard_errors.append({"type": "claim_source_identity", "evidence": f"claim source identity does not match its URI: {finding.get('finding_id')}"})
        if not finding.get("locator") or not finding.get("evidence_quote"):
            hard_errors.append({"type": "missing_evidence_locator", "evidence": f"{finding.get('finding_id')} lacks a pinpoint locator or excerpt"})
        unknown_related = sorted(set(finding.get("related_claim_ids", [])) - known_claim_ids)
        if unknown_related:
            hard_errors.append({"type": "unknown_related_claim", "evidence": f"{finding.get('finding_id')} refers to unknown Claim IDs: {', '.join(unknown_related)}"})
        unknown_finding_refs = sorted(set(finding.get("related_finding_ids", [])) - known_finding_ids)
        if unknown_finding_refs:
            hard_errors.append({"type": "unknown_related_finding", "evidence": f"{finding.get('finding_id')} refers to unknown Finding IDs: {', '.join(unknown_finding_refs)}"})
        statement = normalize_title(finding.get("statement"))
        if statement in normalized_existing or statement in seen_statements:
            finding["duplicate_or_repeated"] = True
            soft_notes.append({"type": "duplicate_finding", "evidence": f"{finding.get('finding_id')} repeats an existing or same-round statement"})
        else:
            finding["duplicate_or_repeated"] = False
        seen_statements.add(statement)
    status = execution.get("status")
    if status == "completed" and not execution.get("artifact_path"):
        hard_errors.append({"type": "missing_artifact", "evidence": "completed execution supplied no candidate artifact path"})
    if status == "no_update_needed" and execution.get("findings"):
        hard_errors.append({"type": "status_mismatch", "evidence": "no_update_needed output contains findings"})
    return {
        "hard_errors": hard_errors,
        "soft_notes": soft_notes,
        "source_validity_gate": not hard_errors,
        "full_reads": len(full_reads),
        "verified_source_count": sum(bool(paper.get("source_verification", {}).get("verified")) for paper in papers),
        "candidate_distinct_findings": [finding["finding_id"] for finding in execution.get("findings", []) if not finding.get("duplicate_or_repeated")],
        "candidate_qualifications": [finding["finding_id"] for finding in execution.get("findings", []) if finding.get("relation") == "qualifies"],
        "historical_audit_baseline": goal.get("historical_audit_baseline"),
    }


def _compact_knowledge_context(existing_knowledge: dict[str, Any] | None, plan: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    context = existing_knowledge or {}
    initial = context.get("initial", {}) if isinstance(context.get("initial"), dict) else {}
    claims = initial.get("claims", []) if isinstance(initial.get("claims"), list) else []
    required_ids = {claim_id for finding in execution.get("findings", []) for claim_id in finding.get("related_claim_ids", [])}
    def compact_claim(claim: dict[str, Any]) -> dict[str, Any]:
        return {
            "claim_id": claim.get("claim_id"),
            "statement": str(claim.get("statement", ""))[:500],
            "scope": str(claim.get("scope", ""))[:250],
            "status": claim.get("status"),
            "evidence": [
                {key: evidence.get(key) for key in ("source_id", "source_version", "source_uri", "locator", "relation")}
                for evidence in claim.get("evidence", [])[:2]
            ],
            "related_claims": claim.get("related_claims", [])[:8],
            "supersedes": claim.get("supersedes", [])[:8],
        }
    selected = [compact_claim(claim) for claim in claims if claim.get("claim_id") in required_ids]
    selected_ids = {claim.get("claim_id") for claim in selected}
    selected.extend(compact_claim(claim) for claim in claims if claim.get("claim_id") not in selected_ids and len(selected) < 16)
    candidate_ids = set(plan.get("candidate_ids", []))
    queue = [row for row in initial.get("candidate_queue", []) if row.get("candidate_id") in candidate_ids]
    queue = [{key: row.get(key) for key in ("candidate_id", "title", "publication_date", "arxiv_id", "doi", "source_url", "source_version", "status", "local_paper_material")} for row in queue]
    return {
        "phase1_summary": str(initial.get("phase1_summary", ""))[:1200],
        "claims": selected,
        "open_questions": list(initial.get("open_questions", []))[:10],
        "selected_candidates": queue,
        "pending_proposals": [{key: row.get(key) for key in ("proposal_id", "status", "title")} for row in initial.get("pending_proposals", [])[:8]],
        "previous_rounds": context.get("previous_rounds", []),
        "historical_audit_baseline": initial.get("historical_audit_baseline"),
    }


def build_judge_prompt(goal: dict[str, Any], plan: dict[str, Any], execution: dict[str, Any], deterministic: dict[str, Any], raw_evidence: list[dict[str, Any]], existing_knowledge: dict[str, Any] | None = None, round_number: int = 1) -> str:
    round_scope = f"Evaluate research round {round_number} only. Run-level acceptance criteria such as the required feedback-driven Planner decision are enforced by the Controller after later planning; do not fail this round for future work."
    round_goal = {
        key: goal.get(key)
        for key in ("research_focus", "research_scope", "research_questions", "allowed_sources", "allowed_source_hosts", "hard_constraints", "budgets")
    }
    round_acceptance = {
        key: goal.get("acceptance_criteria", {}).get(key)
        for key in ("require_source_identity_and_version", "require_locator_and_independent_evaluation", "require_no_new_deterministic_audit_regression", "formal_knowledge_auto_modified", "skill_auto_modified")
    }
    return """You are an independent Evaluator in a bounded research-evolution runtime. This is a separate, stateless model call. Apply the read-only `knowledge-audit` Skill distinctions. Do not accept the Executor's summary or self-reported confidence as proof. Judge only the supplied goal, acceptance rules, actual candidate artifact, raw source references/excerpts, and deterministic checks. The shared source manifest may contain local_paper_material paths: inspect the original local PDF or parsed text first, and read only the sections/pages/figures needed to verify the specific Findings and locators. Do not repeat a full-paper read or copy source contents into run artifacts. If a path is inaccessible, state that explicitly and use the primary URL or a search tool actually exposed by this Codex CLI only when needed; report if the environment does not provide one. Web-search calls are capped by Goal.budgets.max_web_search_calls_per_task: batch focused checks and reuse opened pages instead of repeating searches. Do not mark an abstract-only/section-only read as a full read. Distinguish factual accuracy, completeness, method understanding, evidence sufficiency, research relevance, and scope. Treat historical audit findings as baseline; only new regressions are this run's failures.

Hard gates: any deterministic hard error means do not PASS; source identity/version and evidence location must be consistent; semantic similarity alone is not support; a retrieval proxy is not a task outcome; the candidate must not edit formal knowledge or Skills. A score or confidence alone cannot pass. Evaluate each finding against existing Claims and open questions. Provide evidence-based gap_progress for relevant questions; distinguish progress from resolution. If a finding needs human interpretation, mark NEEDS_REVIEW. If a bounded correction can repair a concrete defect, RETRY. If the plan itself is poor, REPLAN. If there is no new verifiable contribution, NO_UPDATE_NEEDED.

Immutable goal:\n""" + json.dumps(round_goal, ensure_ascii=False, separators=(",", ":")) + "\nCurrent-round acceptance:\n" + json.dumps(round_acceptance, ensure_ascii=False, separators=(",", ":")) + "\nCurrent round: " + str(round_number) + "\n" + round_scope + "\nRelevant existing knowledge:\n" + json.dumps(_compact_knowledge_context(existing_knowledge, plan, execution), ensure_ascii=False, separators=(",", ":")) + "\nTask plan:\n" + json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\nComplete merged Executor result:\n" + json.dumps(execution, ensure_ascii=False, separators=(",", ":")) + "\nShared source manifest (finding excerpts are already in the merged output):\n" + json.dumps(raw_evidence, ensure_ascii=False, separators=(",", ":")) + "\nDeterministic checks:\n" + json.dumps(deterministic, ensure_ascii=False, separators=(",", ":"))
