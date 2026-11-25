from __future__ import annotations

import json
import re
import time
from collections import deque
from pathlib import Path
from typing import Any, Callable

from scripts.evolution.backends.base import BackendError, BackendRequest, BackendResponse
from scripts.evolution.backends.schema import validate_json
from scripts.evolution.common import atomic_write_json, atomic_write_text


class MockBackend:
    """Deterministic backend for testing the same controller/backend interface."""

    name = "mock"

    def __init__(self, responses: list[dict[str, Any] | Exception] | Callable[[BackendRequest], dict[str, Any]] | None = None, delay_seconds: float = 0):
        self.responses = deque(responses or []) if not callable(responses) else None
        self.response_factory = responses if callable(responses) else None
        self.delay_seconds = delay_seconds
        self.calls: list[str] = []

    def invoke(self, request: BackendRequest) -> BackendResponse:
        self.calls.append(request.task_id)
        request.task_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_text(request.task_dir / "prompt.txt", request.prompt)
        atomic_write_json(request.task_dir / "output-schema.json", request.schema)
        started = time.monotonic()
        while time.monotonic() - started < self.delay_seconds:
            if request.stop_requested and request.stop_requested():
                raise BackendError("stopped", "mock stop requested", request.task_id)
            if time.monotonic() - started > request.timeout_seconds:
                raise BackendError("timeout", "mock backend timed out", request.task_id, retryable=True)
            time.sleep(0.01)
        if self.response_factory:
            output = self.response_factory(request)
        elif self.responses:
            value = self.responses.popleft()
            if isinstance(value, Exception):
                raise value
            output = value
        else:
            raise BackendError("mock_exhausted", "no mock response was configured", request.task_id)
        errors = validate_json(output, request.schema)
        if errors:
            raise BackendError("schema", "; ".join(errors[:10]), request.task_id)
        atomic_write_json(request.task_dir / "last-message.json", output)
        return BackendResponse(request.task_id, request.role, output, self.name, model="mock", usage="unavailable", metadata={"elapsed_seconds": round(time.monotonic() - started, 3)})


def build_smoke_backend() -> MockBackend:
    """Small deterministic journey used by CLI process-isolation tests, never for research claims."""
    def response(request: BackendRequest) -> dict[str, Any]:
        match = re.search(r"-r(\d+)-", request.task_id)
        round_number = int(match.group(1)) if match else 1
        if request.role == "planner":
            if round_number == 1:
                return {"decision": "continue", "rationale": "The smoke run exercises one bounded research task.", "topic_id": "agent-memory", "research_question": "How does provenance constrain memory correction?", "feedback_refs": [], "candidate_ids": [], "max_full_reads": 1, "stop_reason": ""}
            return {"decision": "no_update_needed", "rationale": "The first round produced the only smoke-test signal; no additional mock task is useful.", "topic_id": None, "research_question": None, "feedback_refs": ["r01-f01"], "candidate_ids": [], "max_full_reads": 0, "stop_reason": "Smoke test has no further task."}
        if request.role == "executor":
            artifact_match = re.search(r"Candidate artifact path:\s*\n([^\n]+)", request.prompt)
            artifact_path = artifact_match.group(1).strip() if artifact_match else ""
            target = request.workspace / artifact_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Mock isolated candidate memo\n\nSynthetic test evidence only; not a research result.\n", encoding="utf-8")
            return {
                "status": "completed", "summary": "Synthetic mock response for runtime testing only.",
                "papers": [{"title": "Mock Agent Memory Test", "source_id": "arxiv:2401.01234", "source_version": "2401.01234v1", "publication_date": "2024-01-01", "source_uri": "https://arxiv.org/abs/2401.01234v1", "official_repository": None, "reading_extent": "full_text", "locators": ["Sec. 2"]}],
                "findings": [{"finding_id": "F1", "statement": "Mock evidence shows that source provenance can be represented separately from a memory utility score.", "claim_type": "interpretation", "scope": "Synthetic test only", "source_id": "arxiv:2401.01234", "source_version": "2401.01234v1", "source_uri": "https://arxiv.org/abs/2401.01234v1", "locator": "Sec. 2", "relation": "qualifies", "evidence_quote": "synthetic mock excerpt", "importance": "Exercise the proposal boundary, not a real knowledge claim.", "related_claim_ids": [], "related_finding_ids": []}],
                "unresolved_questions": ["Synthetic question: how should the test evaluator record a gap?"], "artifact_path": artifact_path, "limitations": ["Not a paper; must never be interpreted as real evidence."],
            }
        if request.role == "evaluator":
            return {
                "decision": "PASS", "criteria": [{"criterion": label, "passed": True, "evidence": "Synthetic deterministic fixture.", "failure_type": "none", "action": "none"} for label in ("identity", "locator", "scope", "artifact", "knowledge gain")],
                "accepted_finding_ids": ["r01-f01"] if round_number == 1 else [], "rejected_finding_ids": [],
                "gap_progress": [{"question": "Synthetic question: how should the test evaluator record a gap?", "status": "progress", "evidence": "Mock fixture only."}],
                "unresolved_questions": ["Synthetic question: continue only in test"], "rationale": "Synthetic fixture verifies runtime wiring only; no research conclusion is made.",
            }
        if request.role == "reflector":
            return {"failure_type": "none", "failure_evidence": [], "possible_causes": [], "ineffective_attempts": [], "retry_worthwhile": False, "next_step": "Use the retained test result.", "replan": False, "knowledge_summary": ["Mock evidence retained."], "remaining_gaps": ["Synthetic question remains."], "feedback_refs": ["r01-f01"]}
        raise BackendError("mock_exhausted", f"no smoke response for role {request.role}", request.task_id)
    return MockBackend(response)
