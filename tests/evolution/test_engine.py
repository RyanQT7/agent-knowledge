from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.evolution.backends.base import BackendError, BackendRequest
from scripts.evolution.backends.codex_cli import CodexCliBackend
from scripts.evolution.backends.mock_backend import MockBackend
from scripts.evolution.common import atomic_write_json, atomic_write_jsonl, read_json, read_jsonl
from scripts.evolution.discovery import _base_record, _cursor_key, _date_is_future, _is_relevant, _query_string, discover, load_config as load_discovery_config
from scripts.evolution.engine import evaluator, executor, memory
from scripts.evolution.engine.controller import EvolutionController, build_goal, load_engine_config
from scripts.evolution.engine.schemas import SCHEMAS


REPO = Path(__file__).resolve().parents[2]


def make_root(parent: Path, name: str = "kb") -> Path:
    root = parent / name
    root.mkdir()
    for rel in ("evolution/config", "evolution/claims", "evolution/inbox", "evolution/audits", "evolution/proposals", "evolution/state", "evolution/runs", "concepts", "papers", "notes"):
        (root / rel).mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / "evolution/config/engine.yaml", root / "evolution/config/engine.yaml")
    shutil.copy2(REPO / "evolution/config/limits.yaml", root / "evolution/config/limits.yaml")
    config = json.loads((root / "evolution/config/engine.yaml").read_text())
    config["discovery"]["enabled"] = False
    atomic_write_json(root / "evolution/config/engine.yaml", config)
    (root / "evolution/config/watchlist.yaml").write_text(json.dumps({"version": 1, "topics": [{"id": "agent-memory", "title": "Agent Memory", "keywords": ["agent memory"], "research_questions": ["How should memory evidence be corrected?"], "priority": 5, "enabled": True, "sources": ["arxiv"]}]}), encoding="utf-8")
    (root / "evolution/claims/claims.jsonl").write_text("", encoding="utf-8")
    (root / "evolution/inbox/candidates.jsonl").write_text("", encoding="utf-8")
    (root / "evolution/runs/first-evolution-report.md").write_text("# Phase 1 report\n\nOpen question: memory error correction.\n", encoding="utf-8")
    (root / "notes/questions.md").write_text("# Questions\n\n| Question | Status | Note |\n| --- | --- | --- |\n| How should memory evidence be corrected? | Open | Test baseline question. |\n", encoding="utf-8")
    (root / "concepts/memory.md").write_text("# Memory\n\nEvidence and utility are separate dimensions.\n", encoding="utf-8")
    (root / "INDEX.md").write_text("# Index\n\n- [Memory](concepts/memory.md)\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Engine Test"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "engine-test@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "add", "INDEX.md", "concepts", "notes", "evolution"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture baseline"], cwd=root, check=True)
    return root


def cleanup_worktree(root: Path, run_id: str) -> None:
    path = root.parent / f".{root.name}-evolution-{run_id}-workspace"
    if path.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(path)], cwd=root, capture_output=True, text=True)
        if path.exists():
            shutil.rmtree(path, ignore_errors=True)


def planner_response(round_number: int, decision: str = "continue", feedback: list[str] | None = None) -> dict:
    if decision == "continue":
        return {"decision": decision, "rationale": f"Select a bounded task for round {round_number} using the current evidence.", "topic_id": "agent-memory", "research_question": "How does source provenance constrain memory correction?", "feedback_refs": feedback or [], "candidate_ids": [], "max_full_reads": 1, "stop_reason": ""}
    return {"decision": decision, "rationale": "No additional high-value task is supported by the current evidence.", "topic_id": None, "research_question": None, "feedback_refs": feedback or [], "candidate_ids": [], "max_full_reads": 0, "stop_reason": "No high-value follow-up."}


def executor_response(round_number: int, request: BackendRequest, status: str = "completed", outside_write: bool = False) -> dict:
    artifact_match = re.search(r"Candidate artifact path:\s*\n([^\n]+)", request.prompt)
    artifact_path = artifact_match.group(1).strip() if artifact_match else ""
    if status == "completed":
        path = request.workspace / artifact_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Isolated test memo\n\nShort, evidence-linked candidate only.\n", encoding="utf-8")
        if outside_write:
            (request.workspace / "concepts/memory.md").write_text("modified by mock", encoding="utf-8")
        return {
            "status": "completed", "summary": "Test candidate output; fixture source is synthetic.",
            "papers": [{"title": "Test Agent Memory Paper", "source_id": "arxiv:2401.01234", "source_version": "2401.01234v1", "publication_date": "2024-01-01", "source_uri": "https://arxiv.org/abs/2401.01234v1", "official_repository": None, "reading_extent": "full_text", "locators": ["Sec. 2"]}],
            "findings": [{"finding_id": "F1", "statement": "Source provenance should be tracked separately from a task-relative memory utility estimate.", "claim_type": "interpretation", "scope": "Synthetic engine test only", "source_id": "arxiv:2401.01234", "source_version": "2401.01234v1", "source_uri": "https://arxiv.org/abs/2401.01234v1", "locator": "Sec. 2", "relation": "supports", "evidence_quote": "synthetic source fixture", "importance": "Test the isolated proposal and evidence flow.", "related_claim_ids": [], "related_finding_ids": []}],
            "unresolved_questions": ["How should a later observation revise a scoped memory?"], "artifact_path": artifact_path, "limitations": ["Synthetic fixture; never research evidence."],
        }
    return {"status": "no_update_needed", "summary": "No fixture update.", "papers": [], "findings": [], "unresolved_questions": ["How should a later observation revise a scoped memory?"], "artifact_path": "", "limitations": ["No mock update."]}


def evaluator_response(decision: str = "PASS", accepted: list[str] | None = None, question: str = "How should a later observation revise a scoped memory?") -> dict:
    return {
        "decision": decision,
        "criteria": [{"criterion": name, "passed": decision in {"PASS", "NO_UPDATE_NEEDED"}, "evidence": "Fixture evidence record.", "failure_type": "none" if decision in {"PASS", "NO_UPDATE_NEEDED"} else "evidence_gap", "action": "none"} for name in ("accuracy", "completeness", "method understanding", "evidence", "scope")],
        "accepted_finding_ids": accepted or [], "rejected_finding_ids": [],
        "gap_progress": [{"question": question, "status": "progress", "evidence": "The synthetic test exercises question tracking."}],
        "unresolved_questions": [question], "rationale": f"Fixture Judge returned {decision}; this is not real research.",
    }


def reflection_response(retry: bool = False, replan: bool = False) -> dict:
    failed = retry or replan
    return {"failure_type": "evidence_gap" if failed else "none", "failure_evidence": ["Fixture evaluator requested a change."] if failed else [], "possible_causes": ["Test condition."] if failed else [], "ineffective_attempts": ["Initial draft was insufficient."] if retry else [], "retry_worthwhile": retry, "next_step": "Add a pinpoint locator and re-evaluate." if retry else "Use the retained result and unresolved gap for the next plan.", "replan": replan, "knowledge_summary": ["Fixture finding was retained."], "remaining_gaps": ["Fixture gap remains."], "feedback_refs": ["r01-f01"]}


class EngineFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)
        self.root = make_root(self.parent)
        self.run_ids: list[str] = []

    def tearDown(self) -> None:
        for run_id in self.run_ids:
            cleanup_worktree(self.root, run_id)
        self.temp.cleanup()

    def run_controller(self, backend: MockBackend, run_id: str, max_calls: int = 12) -> tuple[EvolutionController, dict, Path]:
        self.run_ids.append(run_id)
        config = load_engine_config(self.root)
        config["discovery"]["enabled"] = False
        goal = build_goal(config, max_rounds=3, max_model_calls=max_calls)
        controller = EvolutionController(backend, root=self.root, config=config, source_getter=lambda uri, timeout: (True, "fixture source exists"))
        run_dir = controller.create_run(goal, run_id=run_id)
        state = controller.execute(run_dir)
        return controller, state, run_dir

    def test_planner_memory_respects_context_token_caps(self) -> None:
        rows = [{"candidate_id": f"cand-{index}", "title": f"Agent memory paper {index}", "research_topic": "agent-memory", "status": "discovered", "priority": 20-index, "abstract": "A" * 1000} for index in range(15)]
        atomic_write_jsonl(self.root / "evolution/inbox/candidates.jsonl", rows)
        config = load_engine_config(self.root)
        context = memory.initial_memory(self.root, config)
        self.assertEqual(len(context["candidate_queue"]), 8)
        self.assertLessEqual(len(context["phase1_summary"]), 2500)
        self.assertTrue(all(len(candidate["abstract"]) <= 240 for candidate in context["candidate_queue"]))

    def test_executor_attempt_merge_preserves_full_read_findings_and_finding_links(self) -> None:
        first = executor_response(1, BackendRequest("x", "executor", "Candidate artifact path:\nevolution/runs/x/round_01/candidate/research-memo.md", SCHEMAS["executor"], self.root, self.root, 1))
        first["findings"][0]["finding_id"] = "F1"
        first["papers"][0]["reading_extent"] = "full_text"
        second = executor_response(1, BackendRequest("x", "executor", "Candidate artifact path:\nevolution/runs/x/round_01/candidate/research-memo-attempt-02.md", SCHEMAS["executor"], self.root, self.root, 1))
        second["artifact_path"] = "evolution/runs/x/round_01/candidate/research-memo-attempt-02.md"
        second["papers"][0]["reading_extent"] = "sections_only"
        second["papers"][0]["locators"] = ["Sec. 3"]
        second["findings"][0]["finding_id"] = "F2"
        second["findings"][0]["related_claim_ids"] = ["F1"]
        merged = executor.merge_attempts([first, second], 1, set(), [1, 2])

        self.assertEqual(len(merged["findings"]), 2)
        self.assertEqual(merged["papers"][0]["reading_extent"], "full_text")
        self.assertEqual(merged["papers"][0]["locators"], ["Sec. 2", "Sec. 3"])
        self.assertEqual(merged["findings"][0]["finding_id"], "r01-f01")
        self.assertEqual(merged["findings"][1]["finding_id"], "r01-a02-f01")
        self.assertEqual(merged["findings"][1]["related_claim_ids"], [])
        self.assertEqual(merged["findings"][1]["related_finding_ids"], ["r01-f01"])

        goal = build_goal(load_engine_config(self.root))
        deterministic = evaluator.deterministic_evaluation(
            merged, planner_response(1), goal, [], source_getter=lambda uri, timeout: (True, "fixture"),
        )
        self.assertEqual(deterministic["full_reads"], 1)
        self.assertEqual(deterministic["hard_errors"], [])

    def test_judge_prompt_defers_future_run_acceptance_and_uses_compact_context(self) -> None:
        goal = build_goal(load_engine_config(self.root))
        prompt = evaluator.build_judge_prompt(
            goal, planner_response(1), {"findings": [], "papers": []}, {}, [],
            {"initial": {"phase1_summary": "x" * 5000, "claims": [], "open_questions": []}}, 1,
        )
        self.assertIn("Run-level acceptance criteria", prompt)
        self.assertIn("Current round: 1", prompt)
        self.assertNotIn("x" * 2000, prompt)

    def test_controller_applies_role_search_and_timeout_limits(self) -> None:
        backend = MockBackend(self.normal_responder)
        requests: list[BackendRequest] = []
        invoke = backend.invoke

        def capture(request: BackendRequest):
            requests.append(request)
            return invoke(request)

        backend.invoke = capture
        _, state, _ = self.run_controller(backend, "engine-role-budget-001")
        self.assertEqual(state["status"], "COMPLETED")
        limits = {request.role: (request.max_search_calls, request.timeout_seconds) for request in requests}
        self.assertEqual(limits["planner"], (0, 180))
        self.assertEqual(limits["executor"], (4, 600))
        self.assertEqual(limits["evaluator"], (2, 420))
        self.assertEqual(limits["reflector"], (0, 150))

    def normal_responder(self, request: BackendRequest) -> dict:
        match = re.search(r"-r(\d+)-", request.task_id)
        round_number = int(match.group(1)) if match else 1
        if request.role == "planner":
            return planner_response(round_number, "continue" if round_number == 1 else "no_update_needed", ["r01-f01"] if round_number > 1 else [])
        if request.role == "executor":
            return executor_response(round_number, request)
        if request.role == "evaluator":
            return evaluator_response(accepted=["r01-f01"] if round_number == 1 else [])
        if request.role == "reflector":
            return reflection_response()
        raise AssertionError(request.role)

    def test_normal_run_creates_draft_only_and_plans_from_prior_gain(self) -> None:
        backend = MockBackend(self.normal_responder)
        _, state, run_dir = self.run_controller(backend, "engine-normal-001")
        self.assertEqual(state["status"], "COMPLETED")
        self.assertEqual(state["calls_started"], 5)
        self.assertEqual(state["feedback_planning_rounds"], 1)
        self.assertTrue(state["rounds"]["2"]["feedback_driven_plan"])
        self.assertEqual(state["rounds"]["2"]["plan"]["decision"], "no_update_needed")
        self.assertEqual(state["rounds"]["1"]["audit_delta"]["new_findings"], 0)
        self.assertFalse(state["formal_knowledge_applied"])
        self.assertEqual((self.root / "evolution/claims/claims.jsonl").read_text(), "")
        proposal = read_json(self.root / "evolution/proposals" / f"{state['proposal_ids'][0]}.json", {})
        self.assertEqual(proposal["status"], "draft")
        self.assertEqual(state["rounds"]["1"]["knowledge_gain"]["candidate_gain"], 1)
        self.assertIn("Fixture gap remains.", state["rounds"]["1"]["unresolved_questions"])
        round_two_planner = (run_dir / "tasks/engine-normal-001-r02-planner-a01/prompt.txt").read_text(encoding="utf-8")
        self.assertIn("Fixture gap remains.", round_two_planner)
        self.assertTrue((run_dir / "round_01/artifacts/research-memo.md").is_file())
        self.assertEqual(state["token_usage"], "unavailable")

    def test_independent_evaluator_retry_and_reflection_then_targeted_executor_retry(self) -> None:
        evaluator_calls = {"count": 0}
        def responder(request: BackendRequest) -> dict:
            round_number = int(re.search(r"-r(\d+)-", request.task_id).group(1))
            if request.role == "planner":
                return planner_response(round_number, "continue" if round_number == 1 else "no_update_needed", ["r01-f01"] if round_number > 1 else [])
            if request.role == "executor":
                return executor_response(round_number, request)
            if request.role == "evaluator":
                evaluator_calls["count"] += 1
                return evaluator_response("RETRY", []) if evaluator_calls["count"] == 1 else evaluator_response("PASS", ["r01-f01"])
            return reflection_response(retry=True)
        backend = MockBackend(responder)
        _, state, run_dir = self.run_controller(backend, "engine-retry-001")
        self.assertEqual(state["status"], "COMPLETED")
        self.assertEqual(state["rounds"]["1"]["executor_retries"], 1)
        self.assertEqual(state["rounds"]["1"]["reflection"]["failure_type"], "evidence_gap")
        self.assertGreaterEqual(sum("executor" in call for call in backend.calls), 2)
        self.assertGreaterEqual(state["calls_started"], 7)
        artifacts = state["rounds"]["1"]["artifact_attempts"]
        self.assertEqual(set(artifacts), {"1", "2"})
        self.assertNotEqual(artifacts["1"]["path"], artifacts["2"]["path"])
        retry_prompt = (run_dir / "tasks/engine-retry-001-r01-executor-a02/prompt.txt").read_text(encoding="utf-8")
        self.assertIn("Earlier Executor attempts", retry_prompt)
        self.assertIn("research-memo-attempt-02.md", retry_prompt)

    def test_evaluator_replan_changes_the_next_outer_plan(self) -> None:
        def responder(request: BackendRequest) -> dict:
            round_number = int(re.search(r"-r(\d+)-", request.task_id).group(1))
            if request.role == "planner":
                if round_number == 1:
                    return planner_response(1)
                return planner_response(2, "no_update_needed", ["q-r01-01"])
            if request.role == "executor":
                return executor_response(round_number, request)
            if request.role == "evaluator":
                return evaluator_response("REPLAN", [], question="Check whether provenance policy changes with memory validity time.")
            return reflection_response(replan=True)
        _, state, _ = self.run_controller(MockBackend(responder), "engine-replan-001")
        self.assertEqual(state["status"], "NO_UPDATE_NEEDED")
        self.assertEqual(state["rounds"]["1"]["status"], "replan_requested")
        self.assertEqual(state["rounds"]["2"]["plan"]["feedback_refs"], ["q-r01-01"])
        self.assertTrue(state["rounds"]["2"]["feedback_driven_plan"])

    def test_two_rounds_without_gain_stop_as_no_progress(self) -> None:
        def responder(request: BackendRequest) -> dict:
            round_number = int(re.search(r"-r(\d+)-", request.task_id).group(1))
            if request.role == "planner":
                return planner_response(round_number, "continue", ["q-r01-01"] if round_number > 1 else [])
            if request.role == "executor":
                return executor_response(round_number, request, "no_update_needed")
            if request.role == "evaluator":
                return evaluator_response("NO_UPDATE_NEEDED", [])
            return reflection_response()
        _, state, _ = self.run_controller(MockBackend(responder), "engine-no-progress-001")
        self.assertEqual(state["status"], "NO_PROGRESS")
        self.assertEqual(state["no_progress_rounds"], 2)
        self.assertEqual(state["calls_started"], 8)
        self.assertEqual(state["proposal_ids"], [])

    def test_shared_model_call_budget_exhaustion_is_not_success(self) -> None:
        backend = MockBackend(lambda req: planner_response(1) if req.role == "planner" else executor_response(1, req))
        _, state, _ = self.run_controller(backend, "engine-call-budget-001", max_calls=2)
        self.assertEqual(state["status"], "BUDGET_EXHAUSTED")
        self.assertEqual(state["calls_started"], 1)
        self.assertIn("reserve", state["terminal_reason"])
        self.assertFalse(state["terminal_reason"].lower().find("not") < 0 and state["status"] == "COMPLETED")

    def test_timeout_is_retried_but_quota_failure_blocks_without_loop(self) -> None:
        calls = {"planner": 0}
        def timeout_responder(req: BackendRequest) -> dict:
            if req.role == "planner":
                calls["planner"] += 1
                if calls["planner"] == 1:
                    raise BackendError("timeout", "test timeout", req.task_id, retryable=True)
                return planner_response(1)
            return executor_response(1, req)
        _, timeout_state, _ = self.run_controller(MockBackend(timeout_responder), "engine-timeout-001", max_calls=2)
        self.assertEqual(timeout_state["status"], "BUDGET_EXHAUSTED")
        self.assertEqual(calls["planner"], 2)
        _, quota_state, _ = self.run_controller(MockBackend([BackendError("quota", "simulated quota limit", "quota-test")]), "engine-quota-001")
        self.assertEqual(quota_state["status"], "BLOCKED")
        self.assertEqual(quota_state["calls_started"], 1)

    def test_illegal_json_schema_response_fails_closed(self) -> None:
        backend = MockBackend([{"decision": "continue"}])
        _, state, _ = self.run_controller(backend, "engine-invalid-json-001")
        self.assertEqual(state["status"], "FAILED")
        self.assertEqual(state["calls_started"], 1)

    def test_codex_output_schemas_require_every_object_property(self) -> None:
        def check_schema(node: dict, path: str = "root") -> None:
            if node.get("type") == "object":
                self.assertFalse(node.get("additionalProperties", True), path)
                self.assertEqual(set(node.get("required", [])), set(node.get("properties", {})), path)
                for key, child in node.get("properties", {}).items():
                    check_schema(child, f"{path}.{key}")
            if node.get("type") == "array" and isinstance(node.get("items"), dict):
                check_schema(node["items"], f"{path}[]")
        for role, schema in SCHEMAS.items():
            with self.subTest(role=role):
                check_schema(schema, role)
        self.assertEqual(CodexCliBackend._classify("invalid_json_schema response_format text.format.schema"), ("schema", False))

    def test_future_date_and_source_identity_are_hard_evidence_gates(self) -> None:
        execution = executor_response(1, BackendRequest("x", "executor", "Candidate artifact path:\nevolution/runs/x/round_01/candidate/research-memo.md", SCHEMAS["executor"], self.root, self.root, 1))
        execution["papers"][0]["publication_date"] = "2999-01-01"
        execution["papers"][0]["source_version"] = "2401.99999v2"
        execution["findings"][0]["source_version"] = "2401.99999v2"
        normalized = {**execution, "findings": [{**execution["findings"][0], "finding_id": "r01-f01"}]}
        goal = build_goal(load_engine_config(self.root), max_rounds=1, max_model_calls=3)
        plan = planner_response(1)
        report = evaluator.deterministic_evaluation(normalized, plan, goal, [], source_getter=lambda uri, timeout: (True, "fixture"))
        types = {error["type"] for error in report["hard_errors"]}
        self.assertIn("future_date", types)
        self.assertIn("source_identity", types)
        self.assertIn("claim_source_identity", types)
        self.assertFalse(report["source_validity_gate"])

    def test_phase1_119_candidate_fault_replay_checks_date_field_and_query_relevance(self) -> None:
        source_run = read_json(REPO / "evolution/runs/first-evolution-20261125.json", {})
        rows = [row for row in read_jsonl(REPO / "evolution/inbox/candidates.jsonl") if row.get("status") == "rejected"]
        self.assertEqual(source_run.get("candidates_found"), 119)
        self.assertEqual(len(rows), 119)
        topics = {row["id"]: row for row in load_discovery_config(REPO / "evolution/config/watchlist.yaml")["topics"]}
        future_count = 0
        irrelevant_count = 0
        for row in rows:
            future_count += int(_date_is_future(row))
            irrelevant_count += int(not _is_relevant(row, topics.get(row.get("research_topic"), {})))
            self.assertTrue(_date_is_future(row) or not _is_relevant(row, topics.get(row.get("research_topic"), {})) or row.get("source_system") == "github")
        self.assertGreater(future_count, 0)
        self.assertGreater(irrelevant_count, 0)
        # Publication date is authoritative for a paper query; update/index dates do not make old work future-dated.
        self.assertTrue(_date_is_future({"publication_date": "2999-01-01", "updated_at": "2020-01-01"}))
        self.assertFalse(_date_is_future({"publication_date": "2020-01-01", "updated_at": "2999-01-01"}))

    def test_provider_failure_falls_back_to_successful_source_without_moving_failed_cursor(self) -> None:
        watchlist_path = self.root / "evolution/config/watchlist.yaml"
        watchlist = json.loads(watchlist_path.read_text())
        watchlist["topics"][0]["sources"] = ["arxiv", "openalex"]
        watchlist_path.write_text(json.dumps(watchlist), encoding="utf-8")
        topic = watchlist["topics"][0]
        query = _query_string(topic)
        key = _cursor_key(topic["id"], "arxiv", query)
        old_cursor = {"query": query, "topic_id": topic["id"], "source": "arxiv", "last_successful_at": "2026-11-10T00:00:00Z", "since": "2026-11-03"}
        (self.root / "evolution/state/discovery.json").write_text(json.dumps({"version": 1, "cursors": {key: old_cursor}, "topic_last_queried_at": {}}), encoding="utf-8")

        def fail(*args):
            raise RuntimeError("simulated arXiv timeout")

        def success(topic_arg, query_arg, since, _limits):
            return [_base_record(topic_arg, "openalex", query_arg, title="Agent Memory Evidence Revision", authors=["A. Researcher"], publication_date="2026-11-20", publication_status="published", arxiv_id="2511.12345v1", source_version="2511.12345v1", source_url="https://arxiv.org/abs/2511.12345v1", source_record_id="W123", abstract="A study of agent memory evidence provenance and correction.")]

        result = discover(root=self.root, topic_ids=[topic["id"]], source_filter={"arxiv", "openalex"}, provider_overrides={"arxiv": fail, "openalex": success}, run_id="engine-provider-fallback")
        state = json.loads((self.root / "evolution/state/discovery.json").read_text())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["candidates_added"], 1)
        self.assertEqual(state["cursors"][key], old_cursor)
        self.assertTrue(any(row.get("source_system") == "openalex" for row in read_jsonl(self.root / "evolution/inbox/candidates.jsonl")))

    def test_executor_attempt_to_write_formal_file_is_rejected_and_not_copied(self) -> None:
        def responder(request: BackendRequest) -> dict:
            if request.role == "planner":
                return planner_response(1)
            if request.role == "executor":
                return executor_response(1, request, outside_write=True)
            if request.role == "evaluator":
                return evaluator_response("PASS", ["r01-f01"])
            return reflection_response()
        original = (self.root / "concepts/memory.md").read_text()
        _, state, _ = self.run_controller(MockBackend(responder), "engine-permission-001")
        self.assertEqual(state["status"], "NEEDS_REVIEW")
        self.assertEqual((self.root / "concepts/memory.md").read_text(), original)
        self.assertEqual(state["proposal_ids"], [])
        self.assertIn("permission", [item["type"] for item in state["rounds"]["1"]["deterministic_evaluation"]["hard_errors"]])

    def test_history_baseline_findings_are_not_new_regressions(self) -> None:
        _, state, _ = self.run_controller(MockBackend(self.normal_responder), "engine-baseline-001")
        self.assertGreaterEqual(state["baseline_audit"]["finding_count"], 0)
        self.assertEqual(state["rounds"]["1"]["audit_delta"]["new_findings"], 0)

    def test_completed_stages_resume_without_repeating_planner_or_executor(self) -> None:
        backend = MockBackend(self.normal_responder)
        controller, state, run_dir = self.run_controller(backend, "engine-resume-001")
        initial_call_ids = list(backend.calls)
        resumed = controller.resume(state["run_id"])
        self.assertEqual(resumed["status"], "COMPLETED")
        self.assertEqual(backend.calls, initial_call_ids)

    def test_explicit_resume_retries_failed_stage_within_original_call_budget(self) -> None:
        planner_attempts = {"count": 0}
        def responder(request: BackendRequest) -> dict:
            if request.role == "planner":
                planner_attempts["count"] += 1
                if planner_attempts["count"] == 1:
                    raise BackendError("process_exit", "simulated CLI argument mismatch", request.task_id)
            return self.normal_responder(request)
        backend = MockBackend(responder)
        controller, failed, _ = self.run_controller(backend, "engine-failed-resume-001")
        self.assertEqual(failed["status"], "FAILED")
        self.assertEqual(failed["calls_started"], 1)
        resumed = controller.resume(failed["run_id"])
        self.assertEqual(resumed["status"], "COMPLETED")
        self.assertEqual(planner_attempts["count"], 3)  # round 1 retry plus round 2 plan
        self.assertEqual(resumed["calls_started"], 6)
        self.assertTrue(any(event_id.endswith("planner-a02") for event_id in backend.calls))

    def test_interrupted_targeted_retry_resumes_with_saved_reflection_feedback(self) -> None:
        stopped = {"once": False}
        evaluator_calls = {"count": 0}
        def responder(request: BackendRequest) -> dict:
            round_number = int(re.search(r"-r(\d+)-", request.task_id).group(1))
            if request.role == "planner":
                return planner_response(round_number, "continue" if round_number == 1 else "no_update_needed", ["r01-f01"] if round_number > 1 else [])
            if request.role == "executor":
                if "-executor-a02" in request.task_id and not stopped["once"]:
                    stopped["once"] = True
                    from scripts.evolution.engine.state import request_stop
                    request_stop(request.task_dir.parent.parent)
                    raise BackendError("stopped", "fixture interrupts the targeted retry", request.task_id)
                return executor_response(round_number, request)
            if request.role == "evaluator":
                evaluator_calls["count"] += 1
                if evaluator_calls["count"] == 1:
                    return evaluator_response("RETRY", [])
                return evaluator_response("PASS", ["r01-f01"])
            return reflection_response(retry=True)
        backend = MockBackend(responder)
        controller, interrupted, run_dir = self.run_controller(backend, "engine-retry-resume-001")
        self.assertEqual(interrupted["status"], "INTERRUPTED")
        self.assertEqual(interrupted["rounds"]["1"]["executor_retries"], 1)
        self.assertIn("pinpoint locator", interrupted["rounds"]["1"]["executor_retry_feedback"]["next_step"])
        resumed = controller.resume(interrupted["run_id"])
        self.assertEqual(resumed["status"], "COMPLETED")
        self.assertEqual(resumed["feedback_planning_rounds"], 1)
        self.assertEqual(resumed["rounds"]["1"]["stages"]["executor"]["attempts"], 3)
        retry_prompt = (run_dir / "tasks/engine-retry-resume-001-r01-executor-a03/prompt.txt").read_text(encoding="utf-8")
        self.assertIn("pinpoint locator", retry_prompt)
        self.assertEqual(backend.calls.count("engine-retry-resume-001-r01-planner-a01"), 1)

    def test_stop_and_resume_reuses_a_completed_planner_stage(self) -> None:
        controller_ref: dict[str, EvolutionController] = {}
        run_dir_ref: dict[str, Path] = {}
        first = {"stopped": False}
        def responder(request: BackendRequest) -> dict:
            round_number = int(re.search(r"-r(\d+)-", request.task_id).group(1))
            if request.role == "planner":
                return planner_response(round_number, "continue" if round_number == 1 else "no_update_needed", ["r01-f01"] if round_number > 1 else [])
            if request.role == "executor":
                output = executor_response(round_number, request)
                if not first["stopped"]:
                    first["stopped"] = True
                    from scripts.evolution.engine.state import request_stop
                    request_stop(request.task_dir.parent.parent)
                return output
            if request.role == "evaluator":
                return evaluator_response(accepted=["r01-f01"])
            return reflection_response()
        backend = MockBackend(responder)
        config = load_engine_config(self.root)
        config["discovery"]["enabled"] = False
        goal = build_goal(config, max_rounds=3, max_model_calls=12)
        controller = EvolutionController(backend, root=self.root, config=config, source_getter=lambda uri, timeout: (True, "fixture"))
        run_id = "engine-interrupt-001"
        self.run_ids.append(run_id)
        run_dir = controller.create_run(goal, run_id)
        state = controller.execute(run_dir)
        self.assertEqual(state["status"], "INTERRUPTED")
        self.assertIn("engine-interrupt-001-r01-planner-a01", backend.calls)
        calls_before_resume = len(backend.calls)
        resumed = controller.resume(run_id)
        self.assertEqual(resumed["status"], "COMPLETED")
        self.assertEqual(backend.calls.count("engine-interrupt-001-r01-planner-a01"), 1)
        self.assertGreater(len(backend.calls), calls_before_resume)

    def test_controller_refuses_unprivileged_interface_escalation(self) -> None:
        backend = CodexCliBackend(executable="missing-codex")
        req = BackendRequest("task", "executor", "", {"type": "object"}, self.root, self.root / "task", 1, sandbox="danger-full-access")
        with self.assertRaisesRegex(BackendError, "sandbox mode is not allowed"):
            backend.invoke(req)

    def test_codex_cli_adapter_uses_ephemeral_schema_json_and_shared_interface(self) -> None:
        fake = self.parent / "fake-codex"
        fake.write_text("""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
args = sys.argv[1:]
if args == ['--version']:
    print('codex-cli fake-test')
elif args[:2] == ['login', 'status']:
    print('Logged in using ChatGPT')
elif args[:2] == ['exec', '--help']:
    print('--ephemeral --json --output-schema --output-last-message --sandbox')
else:
    out = Path(args[args.index('--output-last-message') + 1])
    out.write_text('{\"ok\": true}', encoding='utf-8')
    print(json.dumps({'type':'turn.completed','usage':{'input_tokens':3,'output_tokens':2,'total_tokens':5}}))
""", encoding="utf-8")
        fake.chmod(0o755)
        backend = CodexCliBackend(str(fake), search=False)
        health = backend.healthcheck()
        self.assertTrue(health["ephemeral"])
        schema = {"type": "object", "additionalProperties": False, "required": ["ok"], "properties": {"ok": {"type": "boolean"}}}
        request = BackendRequest("codex-test-001", "planner", "return schema JSON", schema, self.root, self.parent / "codex-task", 10, sandbox="read-only", search=False)
        response = backend.invoke(request)
        self.assertEqual(response.output, {"ok": True})
        self.assertEqual(response.usage["total_tokens"], 5)
        self.assertTrue((request.task_dir / "events.jsonl").is_file())
        self.assertTrue((request.task_dir / "prompt.txt").is_file())

    def test_engine_cli_runs_as_independent_linux_process(self) -> None:
        run_id = "engine-process-smoke-001"
        self.run_ids.append(run_id)
        completed = subprocess.run(
            [sys.executable, str(REPO / "scripts/evolution/evolve.py"), "--root", str(self.root), "run", "--backend", "mock", "--scenario", "smoke", "--no-discovery", "--run-id", run_id],
            cwd=REPO, capture_output=True, text=True, timeout=90,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["status"], "COMPLETED")
        state = read_json(self.root / "evolution/runs" / run_id / "state.json", {})
        self.assertEqual(state["backend"]["name"], "mock")
        self.assertTrue(state["rounds"]["2"]["feedback_driven_plan"])


if __name__ == "__main__":
    unittest.main()
