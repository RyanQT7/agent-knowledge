from __future__ import annotations

import json
from typing import Any


def build_prompt(goal: dict[str, Any], memory: dict[str, Any], round_number: int) -> str:
    return """You are the Planner in a bounded research-evolution runtime. Produce only the schema-conforming JSON requested by the runtime.

System constraints are immutable. Do not rewrite the goal, acceptance criteria, budgets, permissions, or source policy. Follow the existing knowledge-evolution and research-discovery Skill boundaries supplied in the Goal. Pick at most one next research task inside the resolved research_focus, focus_topics, and research_scope. Use the selected Concepts, open Questions, Research Gaps, Reading Roadmaps, current evidence, discovery queue, and previous round evaluation/knowledge gain. Do not repeat full reads already completed. Prefer no_update_needed or needs_review when new evidence is weak, unavailable, or redundant. Do not claim that an abstract-only result is a full paper read. On later rounds, stay within the same resolved focus, but choose a different sub-question when prior feedback shows the current one is resolved, unsupported, or low value.

For a continuation task: choose topic_id only from goal.allowed_topic_ids; ask a bounded question grounded in goal.research_questions, the initial open questions, or a previous round's actual unresolved questions. candidate_ids must come from the supplied discovery queue. max_full_reads cannot exceed the supplied remaining full-read budget or 2. Use source classes only from goal.allowed_sources. On rounds after round 1, feedback_refs must include one or more exact IDs from earlier round findings/questions that materially changed this plan. Round 1 feedback_refs must be empty. If no valuable bounded task remains, stop instead of filling the round quota.

Immutable Goal:
""" + json.dumps(goal, ensure_ascii=False, separators=(",", ":")) + "\nPlanner memory and prior evaluated feedback:\n" + json.dumps(memory, ensure_ascii=False, separators=(",", ":")) + f"\nCurrent planning round: {round_number}\n"


def validate_plan(plan: dict[str, Any], goal: dict[str, Any], memory: dict[str, Any], round_number: int) -> list[str]:
    errors: list[str] = []
    decision = plan.get("decision")
    if decision == "continue":
        if plan.get("topic_id") not in goal.get("allowed_topic_ids", []):
            errors.append("planner selected a topic outside the immutable goal")
        if not plan.get("research_question", "").strip():
            errors.append("continuation plan has no research question")
        if int(plan.get("max_full_reads", 0)) > int(memory.get("remaining_full_reads", 0)):
            errors.append("plan exceeds the remaining full-read budget")
        queue = {item.get("candidate_id") for item in memory.get("initial", {}).get("candidate_queue", [])}
        invalid_candidates = set(plan.get("candidate_ids", [])) - queue
        if invalid_candidates:
            errors.append("planner referenced candidate IDs outside the discovery queue: " + ", ".join(sorted(invalid_candidates)))
        selected_topic = plan.get("topic_id")
        mismatched = []
        for item in memory.get("initial", {}).get("candidate_queue", []):
            candidate_topics = item.get("related_topics") if isinstance(item.get("related_topics"), list) else []
            if not candidate_topics and item.get("research_topic"):
                candidate_topics = [item["research_topic"]]
            if item.get("candidate_id") in set(plan.get("candidate_ids", [])) and selected_topic not in set(candidate_topics):
                mismatched.append(item.get("candidate_id", ""))
        if mismatched:
            errors.append("planner selected candidates outside its chosen focus topic: " + ", ".join(mismatched[:8]))
    elif plan.get("topic_id") is not None or plan.get("research_question") is not None:
        errors.append("stop plan must not schedule a research task")
    if round_number == 1 and plan.get("feedback_refs"):
        errors.append("round 1 cannot reference feedback that does not exist")
    if round_number > 1:
        valid_refs: set[str] = set()
        for item in memory.get("previous_rounds", []):
            valid_refs.update(item.get("knowledge_gain", {}).get("feedback_ids", []))
            valid_refs.update(item.get("unresolved_question_ids", []))
            valid_refs.update(item.get("reflection", {}).get("feedback_refs", []))
        supplied = set(plan.get("feedback_refs", []))
        if not supplied or not (supplied & valid_refs):
            errors.append("planner did not ground this round in an actual prior finding or unresolved-question ID")
    return errors
