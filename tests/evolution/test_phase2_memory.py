from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.evolution.engine import evaluator, memory
from scripts.evolution.experience import add_experience, collect_run_experience, list_experiences, retrieve_experiences
from scripts.evolution.backends.mock_backend import MockBackend
from scripts.evolution.common import atomic_write_json
from scripts.evolution.engine.controller import EvolutionController
from scripts.evolution.skill_evolution import (
    apply_proposal,
    change_status,
    create_proposal,
    evaluate_proposal,
    rollback_proposal,
)


def _experience(root: Path, lesson: str, *, topic: str = "AgentOps", skill: str = "paper-reading", task_type: str = "research", types: list[str] | None = None) -> dict:
    row, _ = add_experience(root, {
        "task_type": task_type, "research_topic": topic, "skill_name": skill,
        "experience_type": types or ["success"], "lesson": lesson,
        "recommended_action": "Reuse the exact local source and read only relevant sections.",
        "evidence_refs": ["test:experience"],
    })
    return row


class ExperienceMemoryTests(unittest.TestCase):
    def test_add_deduplicate_and_retrieve_by_task(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            first = _experience(root, "Reuse the local PDF and avoid repeated search.")
            duplicate, created = add_experience(root, {
                "task_type": "research", "research_topic": "AgentOps", "skill_name": "paper-reading",
                "experience_type": ["success"], "lesson": first["lesson"],
                "recommended_action": first["recommended_action"], "evidence_refs": ["test:experience"],
            })
            _experience(root, "For lessons, annotate the pseudocode in Chinese.", topic="teaching", skill="lesson-authoring", task_type="teaching", types=["user_feedback"])
            self.assertFalse(created)
            self.assertEqual(first["experience_id"], duplicate["experience_id"])
            self.assertEqual(1, duplicate["occurrences"])
            results = retrieve_experiences(root, task_type="research", topic="AgentOps", skill_names=["paper-reading"], limit=3)
            self.assertTrue(results)
            self.assertEqual(first["experience_id"], results[0]["experience_id"])
            self.assertEqual(1, len(results), "teaching-only feedback should not leak into a different research task")
            self.assertEqual(2, len(list_experiences(root)))

    def test_retrieval_matches_chinese_prioritizes_global_preference_and_scopes_engine_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            preference, _ = add_experience(root, {
                "experience_type": ["user_feedback"], "task_type": "general", "persistent": True,
                "applicability": "all tasks", "lesson": "Keep validation proportional across tasks.",
            })
            tsad = _experience(root, "时间序列异常检测应覆盖非平稳正常模式。", topic="时间序列异常检测", skill="paper-reading")
            agentops = _experience(root, "Review AgentOps trajectory evidence before making reliability claims.", topic="AgentOps", skill="paper-reading")
            controller = _experience(root, "Keep Executor attempts separate and merge in the Controller.", topic="Agent Memory", skill="knowledge-evolution", types=["controller_issue"])
            engine_runtime, _ = add_experience(root, {
                "task_type": "research", "research_topic": "Agent Memory", "skill_name": "knowledge-evolution",
                "experience_type": ["environment_issue"], "applicability": "Evolution Engine runs",
                "lesson": "Check Engine runtime configuration before retrying a failed run.",
                "evidence_refs": ["test:engine-runtime"],
            })

            chinese_results = retrieve_experiences(root, task_type="research", topic="时间序列异常检测", skill_names=["paper-reading"], limit=5)
            chinese_ids = [item["experience_id"] for item in chinese_results]
            self.assertEqual(chinese_ids[0], preference["experience_id"])
            self.assertIn(tsad["experience_id"], chinese_ids)
            self.assertNotIn(controller["experience_id"], chinese_ids)
            self.assertNotIn(engine_runtime["experience_id"], chinese_ids)

            agentops_results = retrieve_experiences(root, task_type="research", topic="AgentOps", skill_names=["paper-reading"], limit=5)
            self.assertIn(agentops["experience_id"], [item["experience_id"] for item in agentops_results])

            engine_results = retrieve_experiences(root, task_type="research", topic="Agent Memory Controller retries", skill_names=["knowledge-evolution"], limit=5, include_engine=True)
            engine_ids = [item["experience_id"] for item in engine_results]
            self.assertIn(controller["experience_id"], engine_ids)
            self.assertIn(engine_runtime["experience_id"], engine_ids)

    def test_engine_memory_passes_bounded_experience_to_roles(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            _experience(root, "Judge should check pinpoint source locators, not trust summaries.", types=["evidence_gap"])
            engine_issue = _experience(root, "Keep retry artifacts separate and merge them in the Controller.", topic="Agent Memory", skill="knowledge-evolution", types=["controller_issue"])
            base = memory.initial_memory(root, {})
            self.assertEqual(2, len(base["relevant_experiences"]))
            self.assertIn(engine_issue["experience_id"], [item["experience_id"] for item in base["relevant_experiences"]])
            self.assertEqual(1, list_experiences(root)[0]["use_count"])
            current = memory.planner_memory(base, {"rounds": {}, "remaining_calls": 4}, 1, None)
            self.assertEqual(2, len(current["relevant_experiences"]))
            executor_context = memory.executor_memory(current, {}, {})
            self.assertEqual(2, len(executor_context["relevant_experiences"]))
            prompt = evaluator.build_judge_prompt({}, {}, {"findings": []}, {}, [], current)
            self.assertIn("Judge should check pinpoint source locators", prompt)
            self.assertIn("process guidance only", prompt)

    def test_terminal_collection_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_dir = root / "evolution/runs/run-test"
            run_dir.mkdir(parents=True)
            state = {
                "run_id": "run-test", "status": "NEEDS_REVIEW", "terminal_reason": "evidence needs review",
                "rounds": {"1": {"evaluation": {"decision": "NEEDS_REVIEW", "rationale": "Source evidence excerpt is insufficient."}}},
            }
            goal = {"research_focus": "Agent Memory"}
            first = collect_run_experience(root, run_dir, state, goal)
            second = collect_run_experience(root, run_dir, state, goal)
            rows = retrieve_experiences(root, task_type="research", topic="Agent Memory", skill_names=["paper-reading"])
            self.assertEqual(first, second)
            self.assertEqual(1, len(rows))
            self.assertIn("evidence_gap", rows[0]["experience_type"])

    def test_controller_collects_experience_at_terminal_state(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_dir = root / "evolution/runs/run-test"
            run_dir.mkdir(parents=True)
            (run_dir / "events.jsonl").write_text(
                '{"type":"controller_failure","details":{"type":"ValueError","message":"unexpected state transition"}}\n',
                encoding="utf-8",
            )
            atomic_write_json(run_dir / "goal.yaml", {"research_focus": "Agent Memory", "budgets": {"max_model_calls": 3}})
            state = {
                "run_id": "run-test", "status": "PLANNING", "current_round": 1,
                "started_at": "2026-01-01T00:00:00Z", "calls_started": 0, "rounds": {
                    "1": {"evaluation": {"decision": "NEEDS_REVIEW", "rationale": "Evidence locator is insufficient."}},
                },
            }
            controller = EvolutionController(MockBackend(), root=root, config={"backend": {}})
            result = controller._terminate(run_dir, state, "NEEDS_REVIEW", "test")
            self.assertTrue(result["experience_collection_complete"])
            self.assertTrue(result["experience_ids"])
            saved = list_experiences(root)
            self.assertTrue(any("controller_issue" in item["experience_type"] for item in saved))
            self.assertTrue((run_dir / "final-report.md").is_file())
            self.assertIn(result["experience_ids"][0], (run_dir / "final-report.md").read_text(encoding="utf-8"))


class SkillProposalTests(unittest.TestCase):
    def test_proposal_requires_approval_and_supports_apply_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills/demo-skill"
            skill_dir.mkdir(parents=True)
            target = skill_dir / "SKILL.md"
            original = "---\nname: demo-skill\ndescription: Small test Skill.\n---\n\n# Demo\n\n- Read the requested source carefully.\n- Keep the requested scope and preserve useful evidence references.\n\nFor a bounded task, inspect only the files needed to understand its execution and report any uncertainty directly.\n"
            target.write_text(original, encoding="utf-8")
            experience = _experience(root, "Use a narrow example to explain the execution path.", skill="demo-skill")
            candidate = original + "\nExplain one concrete caller-to-callee example.\n"
            proposal = create_proposal(root, "demo-skill", [experience["experience_id"]], candidate)
            proposal_id = proposal["proposal_id"]
            self.assertEqual(original, target.read_text(encoding="utf-8"))
            evaluated = evaluate_proposal(root, proposal_id)
            self.assertEqual("Inconclusive", evaluated["evaluation"]["result"])
            with self.assertRaises(ValueError):
                apply_proposal(root, proposal_id)
            change_status(root, proposal_id, "approved", "test approval")
            applied = apply_proposal(root, proposal_id)
            self.assertEqual(candidate, target.read_text(encoding="utf-8"))
            self.assertEqual(applied["applied_hash"], evaluated["evaluation"]["artifact_hashes"]["candidate_hash"])
            rollback_proposal(root, proposal_id)
            self.assertEqual(original, target.read_text(encoding="utf-8"))

    def test_skill_proposal_evaluation_stays_bound_to_its_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills/demo-skill"
            skill_dir.mkdir(parents=True)
            target = skill_dir / "SKILL.md"
            original = "---\nname: demo-skill\ndescription: A test.\n---\n\n# Demo\n\n- Keep this rule.\n"
            target.write_text(original, encoding="utf-8")
            experience = _experience(root, "A focused proposal integrity test.", skill="demo-skill")

            proposal = create_proposal(root, "demo-skill", [experience["experience_id"]], original + "\nA candidate rule.\n")
            evaluate_proposal(root, proposal["proposal_id"])
            candidate_path = root / "evolution/skill-proposals" / proposal["proposal_id"] / "candidate.md"
            candidate_path.write_text(candidate_path.read_text(encoding="utf-8") + "\nTampered after evaluation.\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                change_status(root, proposal["proposal_id"], "approved")
            self.assertEqual(original, target.read_text(encoding="utf-8"))

            mismatched = create_proposal(root, "demo-skill", [experience["experience_id"]], original + "\nAnother candidate rule.\n")
            diff_path = root / "evolution/skill-proposals" / mismatched["proposal_id"] / "changes.diff"
            diff_path.write_text(diff_path.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
            evaluated = evaluate_proposal(root, mismatched["proposal_id"])
            self.assertEqual("Regressed", evaluated["evaluation"]["result"])

            report_tamper = create_proposal(root, "demo-skill", [experience["experience_id"]], original + "\nA third candidate rule.\n")
            evaluate_proposal(root, report_tamper["proposal_id"])
            report_path = root / "evolution/skill-proposals" / report_tamper["proposal_id"] / "evaluation.md"
            report_path.write_text(report_path.read_text(encoding="utf-8") + "edited\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                change_status(root, report_tamper["proposal_id"], "approved")

    def test_stale_skill_hash_blocks_apply(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills/demo-skill"
            skill_dir.mkdir(parents=True)
            target = skill_dir / "SKILL.md"
            original = "---\nname: demo-skill\ndescription: A test.\n---\n\n# Demo\n\n- Keep this rule.\n"
            target.write_text(original, encoding="utf-8")
            experience = _experience(root, "A small and focused test experience.", skill="demo-skill")
            proposal = create_proposal(root, "demo-skill", [experience["experience_id"]], original + "\nA concise example.\n")
            evaluate_proposal(root, proposal["proposal_id"])
            change_status(root, proposal["proposal_id"], "approved")
            target.write_text(original + "\nuser edit\n", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                apply_proposal(root, proposal["proposal_id"])

    def test_proposal_can_be_rejected_without_touching_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill_dir = root / "skills/demo-skill"
            skill_dir.mkdir(parents=True)
            target = skill_dir / "SKILL.md"
            original = "---\nname: demo-skill\ndescription: A test.\n---\n\n# Demo\n\n- Keep this rule.\n"
            target.write_text(original, encoding="utf-8")
            experience = _experience(root, "A focused task experience that may not generalize.", skill="demo-skill")
            proposal = create_proposal(root, "demo-skill", [experience["experience_id"]], original + "\nA bounded optional hint.\n")
            reject = change_status(root, proposal["proposal_id"], "rejected", "Not reusable")
            self.assertEqual("rejected", reject["status"])
            self.assertEqual(original, target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
