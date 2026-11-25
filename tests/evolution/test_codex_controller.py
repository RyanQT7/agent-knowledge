from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_engine import cleanup_worktree, evaluator_response, executor_response, make_root, planner_response  # noqa: E402

from scripts.evolution.backends.base import BackendRequest, BackendError
from scripts.evolution.backends.codex_cli import CodexCliBackend
from scripts.evolution.common import atomic_write_json
from scripts.evolution.engine.controller import EvolutionController, build_goal, load_engine_config
from scripts.evolution.engine.state import safe_run_dir

REPO = Path(__file__).resolve().parents[2]


class CodexControllerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.parent = Path(self.temp.name)
        self.root = make_root(self.parent, "codex-kb")
        self.run_ids: list[str] = []

    def tearDown(self) -> None:
        for run_id in self.run_ids:
            cleanup_worktree(self.root, run_id)
        self.temp.cleanup()

    def _fake_executable(self) -> Path:
        fake = self.parent / "fake-codex"
        helper = REPO / "tests/evolution/fake_codex_cli.py"
        fake.write_text(
            "#!/usr/bin/env python3\nimport os,sys\nos.execv(sys.executable,[sys.executable," + repr(str(helper)) + ",*sys.argv[1:]])\n",
            encoding="utf-8",
        )
        fake.chmod(0o755)
        return fake

    def test_codex_backend_runs_through_the_same_controller_interface(self) -> None:
        fake = self._fake_executable()
        call_log = self.parent / "calls.jsonl"
        catalog = self.parent / "catalog.json"
        synthetic_request = BackendRequest(
            "fixture-r01-executor", "executor", "Candidate artifact path:\nevolution/runs/fixture/round_01/candidate/research-memo.md",
            {}, self.root, self.parent / "unused-task", 10,
        )
        fixture_executor = executor_response(1, synthetic_request)
        fixture_executor["summary"] = "Synthetic fixture response through the Codex CLI adapter."
        fixture_executor["findings"][0]["evidence_quote"] = "Synthetic fixture evidence; never cite as research."
        atomic_write_json(catalog, {
            "planner": [planner_response(1), planner_response(2, "no_update_needed", ["r01-f01"])],
            "executor": fixture_executor,
            "evaluator": evaluator_response("PASS", ["r01-f01"]),
            "reflector": {"failure_type":"none", "failure_evidence":[], "possible_causes":[], "ineffective_attempts":[], "retry_worthwhile":False, "next_step":"Use the retained result.", "replan":False, "knowledge_summary":["Synthetic finding retained."], "remaining_gaps":["Synthetic gap remains."], "feedback_refs":["r01-f01"]},
        })
        prior = {key: os.environ.get(key) for key in ("EVOLUTION_FAKE_CODEX_CATALOG", "EVOLUTION_FAKE_CODEX_LOG", "EVOLUTION_FAKE_CODEX_MODE")}
        os.environ["EVOLUTION_FAKE_CODEX_CATALOG"] = str(catalog)
        os.environ["EVOLUTION_FAKE_CODEX_LOG"] = str(call_log)
        os.environ["EVOLUTION_FAKE_CODEX_MODE"] = "controller"
        try:
            config = load_engine_config(self.root)
            config["discovery"]["enabled"] = False
            controller = EvolutionController(
                CodexCliBackend(str(fake), search=False), root=self.root, config=config,
                source_getter=lambda uri, timeout: (True, "synthetic source fixture"),
            )
            run_id = "codex-controller-integration-001"
            self.run_ids.append(run_id)
            state = controller.run_new(build_goal(config, max_rounds=3, max_model_calls=12), run_id)
        finally:
            for key, value in prior.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

        calls = [json.loads(line) for line in call_log.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(state["status"], "COMPLETED")
        self.assertEqual(state["calls_started"], 5)
        self.assertTrue(state["rounds"]["2"]["feedback_driven_plan"])
        self.assertEqual([call["role"] for call in calls], ["planner", "executor", "evaluator", "reflector", "planner"])
        self.assertTrue(all(call["ephemeral"] for call in calls))
        self.assertFalse(any(call["search_flag"] for call in calls))
        self.assertEqual([call["sandbox"] for call in calls], ["read-only", "workspace-write", "read-only", "read-only", "read-only"])
        self.assertEqual((self.root / "evolution/claims/claims.jsonl").read_text(encoding="utf-8"), "")
        self.assertFalse(state["skills_modified"])
        run_dir = self.root / "evolution/runs" / state["run_id"]
        self.assertEqual(run_dir.stat().st_mode & 0o777, 0o700)
        self.assertEqual(Path(state["candidate_workspace"]).stat().st_mode & 0o777, 0o700)
        proposal = json.loads((self.root / "evolution/proposals" / f"{state['proposal_ids'][0]}.json").read_text(encoding="utf-8"))
        self.assertEqual(proposal["status"], "draft")

    def test_run_id_cannot_escape_runs_directory_or_follow_a_symlink(self) -> None:
        outside = self.parent / "outside"
        outside.mkdir()
        (outside / "state.json").write_text('{"status":"PENDING"}', encoding="utf-8")
        with self.assertRaises(ValueError):
            safe_run_dir(self.root, "../../outside")
        symlink = self.root / "evolution/runs/linked-run-001"
        symlink.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            safe_run_dir(self.root, symlink.name)
        result = subprocess.run(
            [sys.executable, str(REPO / "scripts/evolution/evolve.py"), "--root", str(self.root), "stop", "../../outside"],
            cwd=REPO, capture_output=True, text=True, timeout=15,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((outside / "state.json").read_text(encoding="utf-8"), '{"status":"PENDING"}')

    def test_codex_backend_timeout_kills_process_and_private_logs_are_restricted(self) -> None:
        fake = self._fake_executable()
        prior_mode = os.environ.get("EVOLUTION_FAKE_CODEX_MODE")
        os.environ["EVOLUTION_FAKE_CODEX_MODE"] = "timeout"
        try:
            task_dir = self.parent / "timeout-task"
            request = BackendRequest("codex-timeout-001", "planner", "wait", {"type":"object"}, self.root, task_dir, 1, sandbox="read-only", search=False)
            with self.assertRaises(BackendError) as raised:
                CodexCliBackend(str(fake), search=False).invoke(request)
        finally:
            if prior_mode is None:
                os.environ.pop("EVOLUTION_FAKE_CODEX_MODE", None)
            else:
                os.environ["EVOLUTION_FAKE_CODEX_MODE"] = prior_mode
        self.assertEqual(raised.exception.kind, "timeout")
        self.assertEqual(task_dir.stat().st_mode & 0o777, 0o700)
        self.assertEqual((task_dir / "stderr.log").stat().st_mode & 0o777, 0o600)

    def test_codex_backend_enforces_web_search_tool_budget(self) -> None:
        fake = self._fake_executable()
        prior_mode = os.environ.get("EVOLUTION_FAKE_CODEX_MODE")
        os.environ["EVOLUTION_FAKE_CODEX_MODE"] = "search-flood"
        try:
            request = BackendRequest(
                "codex-search-budget-001", "executor", "bounded", {"type":"object"}, self.root,
                self.parent / "search-budget-task", 15, sandbox="workspace-write", search=False, max_search_calls=2,
            )
            with self.assertRaises(BackendError) as raised:
                CodexCliBackend(str(fake), search=False).invoke(request)
        finally:
            if prior_mode is None:
                os.environ.pop("EVOLUTION_FAKE_CODEX_MODE", None)
            else:
                os.environ["EVOLUTION_FAKE_CODEX_MODE"] = prior_mode
        self.assertEqual(raised.exception.kind, "tool_budget")
        self.assertEqual(raised.exception.metadata["search_calls"], 3)


if __name__ == "__main__":
    unittest.main()
