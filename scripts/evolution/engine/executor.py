from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_READING_EXTENT_RANK = {"metadata_only": 0, "abstract_only": 1, "sections_only": 2, "full_text": 3}


def build_prompt(
    goal: dict[str, Any],
    plan: dict[str, Any],
    memory: dict[str, Any],
    artifact_path: str,
    retry_feedback: dict[str, Any] | None = None,
    prior_attempts: list[dict[str, Any]] | None = None,
) -> str:
    return """You are the Executor in a bounded research-evolution runtime. This is an independent task with no prior conversation context.

Stay within the immutable Goal's resolved research_focus, selected topic(s), questions, related Concepts, and Research Gaps. Research_scope defines the allowed bounds for this task. Use the supplied focused knowledge context to avoid revisiting settled material, but treat it as provisional evidence to check rather than as a constraint on new findings. Use only official or primary sources allowed by the immutable Goal and follow the paper-reading, paper-code-discovery, and code-reading evidence rules. Use supplied local_paper_material paths first: local PDFs or parsed text are the shared original source for you and the independent Judge; paper notes are orientation only. Open only the sections, figures, tables, or pages needed for the planned question. If a prior attempt records full_text, do not reread the whole paper; target only the evidence gaps. Do not copy or extract source files into run artifacts. If a supplied path is inaccessible, report that and use bounded primary-source retrieval only if needed. Batch search queries, reuse opened sources, and stay within the configured search limit. Read at most the plan's max_full_reads. Mark reading_extent precisely: full_text only if you actually read the complete paper; otherwise sections_only, abstract_only, or metadata_only. Never infer method details from an abstract. Give source version, date when shown, exact locators, and a short supporting excerpt. Distinguish a proxy metric from the task objective.

Write one concise Markdown memo to the attempt-specific artifact path in the isolated worktree. On a targeted retry, write only a short addendum to the new path; never overwrite earlier attempt artifacts. Do not edit any other file, formal knowledge, Skill, Lesson, Proposal, INDEX, or Git metadata. Do not install packages or execute third-party code. If no high-value verifiable evidence is found, return no_update_needed and leave artifact_path empty.

A finding is a candidate Claim, not approved knowledge. Use unique finding_id values across attempts. related_claim_ids may contain only exact Claim IDs shown in the supplied Claim store. Use related_finding_ids for temporary links to Findings from earlier attempts. Never put temporary IDs such as F2 in related_claim_ids. Use evidence relations only when warranted; semantic similarity alone is not support.

Immutable Goal:
""" + json.dumps(goal, ensure_ascii=False, separators=(",", ":")) + "\nPlanner task:\n" + json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\nBounded research memory:\n" + json.dumps(memory, ensure_ascii=False, separators=(",", ":")) + "\nEarlier Executor attempts (preserve their findings and full-read records):\n" + json.dumps(prior_attempts or [], ensure_ascii=False, separators=(",", ":")) + "\nCandidate artifact path:\n" + artifact_path + "\nTargeted correction from Reflection, if any:\n" + json.dumps(retry_feedback or {}, ensure_ascii=False, separators=(",", ":"))


def normalize_execution(output: dict[str, Any], round_number: int, attempt_number: int = 1) -> dict[str, Any]:
    raw_to_internal: dict[str, str] = {}
    findings = []
    seen: set[str] = set()
    for index, raw in enumerate(output.get("findings", []), start=1):
        raw_id = str(raw.get("finding_id", f"F{index}"))
        if raw_id in seen:
            raw_id = f"{raw_id}-{index}"
        seen.add(raw_id)
        attempt_tag = "" if attempt_number == 1 else f"-a{attempt_number:02d}"
        internal_id = f"r{round_number:02d}{attempt_tag}-f{index:02d}"
        raw_to_internal[raw_id] = internal_id
        findings.append({**raw, "source_finding_id": raw_id, "finding_id": internal_id})
    for finding in findings:
        finding["related_claim_ids"] = list(finding.get("related_claim_ids", []))
        finding["related_finding_ids"] = list(finding.get("related_finding_ids", []))
    return {**output, "findings": findings, "source_finding_id_map": raw_to_internal}


def merge_attempts(
    outputs: list[dict[str, Any]],
    round_number: int,
    known_claim_ids: set[str] | None = None,
    attempt_numbers: list[int] | None = None,
) -> dict[str, Any]:
    """Combine immutable Executor attempts and preserve read extent and evidence."""
    if not outputs:
        return {
            "status": "no_update_needed", "summary": "No executor output.", "papers": [],
            "findings": [], "unresolved_questions": [], "limitations": [], "artifact_path": "",
            "artifact_paths": [], "attempts": [],
        }
    known_claim_ids = known_claim_ids or set()
    merged: dict[str, Any] = {
        **outputs[-1], "papers": [], "findings": [], "unresolved_questions": [],
        "limitations": [], "attempts": [],
    }
    paper_index: dict[tuple[str, str, str], dict[str, Any]] = {}
    raw_finding_ids: dict[str, str] = {}
    attempt_numbers = attempt_numbers or list(range(1, len(outputs) + 1))
    if len(attempt_numbers) != len(outputs):
        raise ValueError("attempt_numbers must match outputs")
    for attempt_number, output in zip(attempt_numbers, outputs):
        normalized = normalize_execution(output, round_number, attempt_number)
        merged["attempts"].append({
            "attempt_number": attempt_number,
            "summary": output.get("summary", "")[:600],
            "artifact_path": output.get("artifact_path", ""),
            "finding_ids": [finding["finding_id"] for finding in normalized["findings"]],
        })
        for paper in normalized.get("papers", []):
            key = (str(paper.get("source_id", "")), str(paper.get("source_version", "")), str(paper.get("source_uri", "")))
            prior = paper_index.get(key)
            if prior is None:
                paper_index[key] = {**paper, "locators": list(paper.get("locators", []))}
                continue
            if _READING_EXTENT_RANK.get(paper.get("reading_extent", "metadata_only"), 0) > _READING_EXTENT_RANK.get(prior.get("reading_extent", "metadata_only"), 0):
                prior["reading_extent"] = paper["reading_extent"]
            for locator in paper.get("locators", []):
                if locator not in prior["locators"]:
                    prior["locators"].append(locator)
            if not prior.get("official_repository") and paper.get("official_repository"):
                prior["official_repository"] = paper["official_repository"]
        for finding in normalized.get("findings", []):
            claim_refs = []
            finding_refs = list(finding.get("related_finding_ids", []))
            for reference in finding.get("related_claim_ids", []):
                if reference in known_claim_ids:
                    claim_refs.append(reference)
                elif reference in raw_finding_ids:
                    finding_refs.append(raw_finding_ids[reference])
                else:
                    claim_refs.append(reference)
            finding["related_claim_ids"] = claim_refs
            finding["related_finding_ids"] = list(dict.fromkeys(
                raw_finding_ids.get(reference, reference) for reference in finding_refs
            ))
            merged["findings"].append(finding)
            raw_finding_ids[finding["source_finding_id"]] = finding["finding_id"]
            raw_finding_ids[finding["finding_id"]] = finding["finding_id"]
    for output in outputs:
        for field in ("unresolved_questions", "limitations"):
            for value in output.get(field, []):
                if value not in merged[field]:
                    merged[field].append(value)
    merged["papers"] = list(paper_index.values())
    merged["summary"] = "\n".join(output.get("summary", "") for output in outputs if output.get("summary"))[:2400]
    merged["artifact_paths"] = [output.get("artifact_path", "") for output in outputs if output.get("artifact_path")]
    if merged["findings"]:
        merged["status"] = "completed"
    merged["artifact_path"] = next((output.get("artifact_path") for output in reversed(outputs) if output.get("artifact_path")), "")
    merged["source_finding_id_map"] = {
        finding["source_finding_id"]: finding["finding_id"] for finding in merged["findings"]
    }
    return merged


def artifact_path_allowed(path_text: str, run_id: str, round_number: int) -> bool:
    expected_prefix = f"evolution/runs/{run_id}/round_{round_number:02d}/candidate/"
    path = Path(path_text)
    return bool(path_text) and not path.is_absolute() and ".." not in path.parts and path_text.startswith(expected_prefix) and path.suffix.lower() in {".md", ".json", ".jsonl"}
