from __future__ import annotations

import json
from typing import Any


def build_prompt(goal: dict[str, Any], plan: dict[str, Any] | None, executor_output: dict[str, Any] | None, evaluation: dict[str, Any] | None, backend_error: dict[str, Any] | None, relevant_experiences: list[dict[str, Any]] | None = None) -> str:
    return """You are the Reflector. Within the resolved Goal research_focus and selected knowledge context, summarize verified candidate knowledge, map progress against the selected Questions and Research Gaps, and identify the remaining focus-specific gaps from this round; then diagnose any failure from the evidence. Do not change the Goal, acceptance criteria, budget, permissions, Skills, or knowledge. Return structured JSON including concise knowledge_summary, remaining_gaps, and exact feedback_refs (Finding or question IDs only), as well as failure type, evidence, causes, ineffective attempts, retry_worthwhile, and a concrete next step/replan flag. If the round passed without a failure, set failure_type to none, leave failure evidence/causes empty, and set retry_worthwhile and replan to false. Separate model, retrieval, environment, permission, quota, evidence and task-feasibility failures. Avoid repeating an ineffective strategy. Experience Memory is process guidance only: do not treat it as evidence about the current paper or finding.

Immutable goal:
""" + json.dumps(goal, ensure_ascii=False, separators=(",", ":")) + "\nPlan:\n" + json.dumps(plan, ensure_ascii=False, separators=(",", ":")) + "\nMerged current-round findings and evidence:\n" + json.dumps(executor_output, ensure_ascii=False, separators=(",", ":")) + "\nIndependent evaluation:\n" + json.dumps(evaluation, ensure_ascii=False, separators=(",", ":")) + "\nRelevant prior process experiences (not factual evidence):\n" + json.dumps(relevant_experiences or [], ensure_ascii=False, separators=(",", ":")) + "\nBackend/runtime error:\n" + json.dumps(backend_error, ensure_ascii=False, separators=(",", ":"))
