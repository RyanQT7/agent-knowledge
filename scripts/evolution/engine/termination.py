from __future__ import annotations

from typing import Any

from scripts.evolution.engine.state import TERMINAL


class BudgetExhausted(RuntimeError):
    pass


def calls_remaining(state: dict[str, Any], goal: dict[str, Any]) -> int:
    return max(0, int(goal["budgets"]["max_model_calls"]) - int(state.get("calls_started", 0)))


def executor_calls_reserved(state: dict[str, Any], goal: dict[str, Any], round_number: int) -> int:
    budgets = goal["budgets"]
    reserve = budgets.get("executor_call_reserve", {"evaluator": 1, "reflector": 1, "next_planner": 1})
    return (
        max(0, int(reserve.get("evaluator", 1)))
        + max(0, int(reserve.get("reflector", 1)))
        + (max(0, int(reserve.get("next_planner", 1))) if round_number < int(budgets.get("max_rounds", 1)) else 0)
    )


def full_reads_remaining(state: dict[str, Any], goal: dict[str, Any]) -> int:
    consumed = sum(int(round_data.get("full_reads", 0)) for round_data in state.get("rounds", {}).values())
    return max(0, int(goal["budgets"]["max_full_reads"]) - consumed)


def should_stop_no_progress(state: dict[str, Any], goal: dict[str, Any]) -> bool:
    return int(state.get("no_progress_rounds", 0)) >= int(goal["budgets"]["max_no_progress_rounds"])


def goal_criteria_satisfied(state: dict[str, Any], goal: dict[str, Any]) -> bool:
    gain_count = sum(len(item.get("knowledge_gain", {}).get("accepted_findings", [])) for item in state.get("rounds", {}).values())
    completed_rounds = sum(1 for item in state.get("rounds", {}).values() if item.get("status") == "evaluated")
    feedback_rounds = int(state.get("feedback_planning_rounds", 0))
    required = goal["acceptance_criteria"]
    return gain_count >= int(required.get("min_verified_candidate_claims", 1)) and completed_rounds >= int(required.get("min_evaluated_rounds", 1)) and feedback_rounds >= int(required.get("min_feedback_driven_rounds", 1))


def finalize_status(state: dict[str, Any]) -> str | None:
    status = state.get("status")
    return status if status in TERMINAL else None
