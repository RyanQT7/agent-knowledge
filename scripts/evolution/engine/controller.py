from __future__ import annotations

import datetime as dt
import difflib
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

from scripts.evolution.backends import Backend, BackendError, BackendRequest, BackendResponse
from scripts.evolution.backends.codex_cli import CodexCliBackend
from scripts.evolution.backends.schema import validate_json
from scripts.evolution.common import (
    ROOT, atomic_write_json, atomic_write_text, normalize_title, read_json, read_jsonl,
    sha256_bytes, sha256_file, stable_hash, utc_now, validate_claim,
)
from scripts.evolution.discovery import discover, load_config
from scripts.evolution.engine.focus import apply_focus_to_config, resolve_focus
from scripts.evolution.engine import evaluator, executor, memory, planner, reflector
from scripts.evolution.engine.local_sources import find_local_paper_material
from scripts.evolution.engine.schemas import SCHEMAS
from scripts.evolution.engine.state import TERMINAL, append_event, is_stop_requested, load_state, safe_run_dir, save_state, transition
from scripts.evolution.engine.termination import BudgetExhausted, calls_remaining, executor_calls_reserved, full_reads_remaining, goal_criteria_satisfied, should_stop_no_progress
from scripts.evolution.proposals import check_proposal, create_proposal
from scripts.evolution.audit import audit
from scripts.evolution.experience import collect_run_experience


def load_engine_config(root: Path = ROOT) -> dict[str, Any]:
    path = root / "evolution" / "config" / "engine.yaml"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("version") != 1:
        raise ValueError(f"unsupported engine configuration: {path}")
    value["_knowledge_root"] = str(root.resolve())
    return value


def build_goal(config: dict[str, Any], max_rounds: int | None = None, max_model_calls: int | None = None, focus: str | None = None, root: Path | None = None) -> dict[str, Any]:
    knowledge_root = (root or Path(config.get("_knowledge_root", ROOT))).resolve()
    resolution = resolve_focus(knowledge_root, focus)
    apply_focus_to_config(config, resolution)
    budgets = dict(config["budgets"])
    if max_rounds is not None:
        if not 1 <= max_rounds <= int(config["budgets"]["max_rounds"]):
            raise ValueError(f"max_rounds must be between 1 and the configured hard cap ({config['budgets']['max_rounds']})")
        budgets["max_rounds"] = max_rounds
    if max_model_calls is not None:
        if not 1 <= max_model_calls <= int(config["budgets"]["max_model_calls"]):
            raise ValueError(f"max_model_calls must be between 1 and the configured hard cap ({config['budgets']['max_model_calls']})")
        budgets["max_model_calls"] = max_model_calls
    selected_context = resolution["research_context"]
    research_scope = [f"User research focus: {resolution['research_focus']}"]
    research_scope.extend(
        f"Watchlist scope: {topic['group']}: {topic['title']} ({'; '.join(topic['keywords'][:5])})"
        for topic in resolution["topics"]
    )
    research_scope.extend(
        f"Relevant knowledge file: {item['path']} — {item['title']}"
        for item in selected_context["related_concepts"]
    )
    research_scope.extend(
        f"Open research gap from {item['path']}: {item['excerpt'][:350]}"
        for item in selected_context["research_gaps"][:3]
    )
    return {
        "schema_version": 1,
        "goal_id": "self-evolution-" + stable_hash("|".join(resolution["topic_ids"]) + "|" + resolution["research_focus"], 12),
        "version": 1,
        "research_focus": resolution["research_focus"],
        "focus_selection": resolution["selection"],
        "focus_topics": resolution["topics"],
        "research_scope": research_scope,
        "research_questions": resolution["research_questions"],
        "research_context": selected_context,
        "allowed_topic_ids": list(resolution["topic_ids"]),
        "allowed_sources": list(config["discovery"]["sources"]) + ["publisher-primary", "conference-primary", "project-official"],
        "allowed_source_hosts": sorted(evaluator.ALLOWED_SOURCE_HOSTS),
        "read_scope": [
            "INDEX.md", "notes/questions.md", "concepts/", "papers/", "code/",
            "notes/**/research-gaps.md", "notes/**/reading-roadmap.md", "notes/**/reviews/",
            "evolution/claims/", "evolution/inbox/", "Phase 1 run and audit records",
            *[item["path"] for item in selected_context["related_concepts"]],
            *[item["path"] for item in selected_context["research_gaps"][:4]],
            *[item["path"] for item in selected_context["reading_roadmaps"][:2]],
            "official primary source pages",
        ],
        "existing_skill_protocols": {
            "experience-memory": "retrieve up to five relevant active execution lessons; use as process guidance only, never as current research evidence",
            "knowledge-evolution": "bounded discovery -> audit -> grounded reading -> Claims -> draft Proposal; no publication",
            "research-discovery": "read metadata/candidates only; do not infer paper understanding from abstracts",
            "knowledge-audit": "read-only; separate contradiction, scope, version, evidence gaps, and no-update",
            "paper-reading": "ground full-paper mechanisms/results/limitations in pinpoint locators; distinguish paper statements from interpretation",
            "paper-code-discovery": "confirm author/paper identity before labeling a repository official",
            "code-reading": "pin a full SHA and perform static analysis only; never execute third-party code",
        },
        "write_scope": ["isolated Git worktree candidate artifact under evolution/runs/<run_id>/round_<n>/candidate/", "draft Proposal under evolution/proposals/ after deterministic and independent evaluation"],
        "hard_constraints": [
            "Do not modify formal Concepts, Papers, Questions, Reviews, Lessons, Skills, INDEX, or existing Claim records; past Experience Memory is not evidence for new claims.",
            "Do not approve, apply, commit, push, install dependencies, run third-party code, or change scheduling.",
            "Do not change this resolved Goal, budgets, source allowlist, evaluation criteria, or permissions.",
            "Planner and Evaluator are read-only; Executor writes only its isolated candidate workspace artifact.",
            "Every candidate Claim stays needs_review and every proposal stays draft.",
            "Never count an abstract or selected sections as a full paper read.",
            "Token and cost values must be unavailable unless the CLI actually provides them.",
        ],
        "acceptance_criteria": {
            "min_verified_candidate_claims": 1,
            "min_evaluated_rounds": 1,
            "min_feedback_driven_rounds": 1,
            "require_source_identity_and_version": True,
            "require_locator_and_independent_evaluation": True,
            "require_no_new_deterministic_audit_regression": True,
            "formal_knowledge_auto_modified": False,
            "skill_auto_modified": False,
        },
        "budgets": budgets,
        "historical_audit_baseline": {
            "run_id": "first-evolution-20261125-v2",
            "finding_count": 58,
            "files_scanned": 358,
            "interpretation": "Initial reference only. The independent Python run audit calculates an exact current-base signature set and only reports new signatures as regressions.",
        },
        "stop_conditions": [
            "Planner selects no_update_needed or complete after considering actual evidence and prior feedback.",
            "Two consecutive evaluated rounds have no useful, evidence-backed knowledge gain.",
            "Model call, round, full-read, or wall-clock budget is exhausted.",
            "Permission, identity, source, or evidence hard gate fails and cannot be safely corrected.",
            "User requests stop.",
        ],
    }


def _hash_json(value: Any) -> str:
    return sha256_bytes(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def _clean_git_paths(root: Path) -> set[str]:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, capture_output=True, text=True, check=True)
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if len(line) > 3:
            paths.add(line[3:].split(" -> ")[-1])
    return paths


def _finding_signature(item: dict[str, Any]) -> tuple[str, str, str, str]:
    return (str(item.get("issue_type", "")), str(item.get("affected_file", "")), str(item.get("affected_claim") or ""), str(item.get("evidence", "")))


def _executor_attempt_outputs(round_dir: Path, before_attempt: int | None = None) -> tuple[list[int], list[dict[str, Any]]]:
    files: list[tuple[int, Path]] = []
    first = round_dir / "executor.json"
    if first.is_file():
        files.append((1, first))
    for path in round_dir.glob("executor-attempt-*.json"):
        match = re.fullmatch(r"executor-attempt-(\d+)\.json", path.name)
        if match:
            files.append((int(match.group(1)), path))
    outputs: list[dict[str, Any]] = []
    numbers: list[int] = []
    for number, path in sorted(files):
        if before_attempt is not None and number >= before_attempt:
            continue
        value = read_json(path, None)
        if isinstance(value, dict) and isinstance(value.get("findings"), list):
            numbers.append(number)
            outputs.append(value)
    return numbers, outputs


def _executor_attempt_context(numbers: list[int], outputs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "attempt_number": number,
            "summary": output.get("summary", "")[:500],
            "papers": output.get("papers", [])[:2],
            "findings": output.get("findings", [])[:8],
            "unresolved_questions": output.get("unresolved_questions", [])[:8],
            "artifact_path": output.get("artifact_path", ""),
        }
        for number, output in zip(numbers, outputs)
    ]


def _round_unresolved_questions(
    evaluation: dict[str, Any] | None,
    execution: dict[str, Any] | None,
    reflection: dict[str, Any] | None,
) -> list[str]:
    """Keep evaluator questions first, while carrying Reflector gaps to the next Planner."""
    questions: list[str] = []
    for source in (evaluation or {}, reflection or {}, execution or {}):
        values = source.get("unresolved_questions", source.get("remaining_gaps", []))
        for value in values if isinstance(values, list) else []:
            question = str(value).strip()
            if question and question.casefold() not in {existing.casefold() for existing in questions}:
                questions.append(question[:500])
            if len(questions) >= 12:
                return questions
    return questions


class EvolutionController:
    def __init__(
        self,
        backend: Backend,
        *,
        root: Path = ROOT,
        config: dict[str, Any] | None = None,
        source_getter: Callable[[str, int], tuple[bool, str]] | None = None,
        discovery_fn: Callable[..., dict[str, Any]] = discover,
        audit_fn: Callable[..., dict[str, Any]] = audit,
    ):
        self.root = root.resolve()
        self.backend = backend
        self.config = config or load_engine_config(self.root)
        self.source_getter = source_getter
        if backend.name == "mock" and source_getter is None:
            self.source_getter = lambda uri, timeout: (True, f"mock-verified {uri}")
        self.discovery_fn = discovery_fn
        self.audit_fn = audit_fn
        self._active_experiences: list[dict[str, Any]] = []

    def create_run(self, goal: dict[str, Any], run_id: str | None = None) -> Path:
        if self.backend.name == "codex-cli":
            if not isinstance(self.backend, CodexCliBackend):
                raise TypeError("codex-cli backend must implement healthcheck")
            backend_health = self.backend.healthcheck()
        else:
            backend_health = {"name": self.backend.name, "health": "test backend"}
        run_id = run_id or self._new_run_id()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,100}", run_id):
            raise ValueError("run ID contains unsafe characters")
        run_dir = self.root / "evolution" / "runs" / run_id
        if run_dir.exists():
            raise FileExistsError(f"run already exists: {run_id}; use resume")
        run_dir.mkdir(parents=True, mode=0o700)
        os.chmod(run_dir, 0o700)
        base_commit = _git(self.root, "rev-parse", "HEAD")
        config_snapshot = json.loads(json.dumps(self.config))
        atomic_write_json(run_dir / "goal.yaml", goal)
        atomic_write_json(run_dir / "engine-config.yaml", config_snapshot)
        workspace = self._workspace_path(run_id)
        state = {
            "schema_version": 1,
            "run_id": run_id,
            "status": "PENDING",
            "status_reason": "run created",
            "started_at": utc_now(),
            "updated_at": utc_now(),
            "started_epoch": time.time(),
            "finished_at": None,
            "goal_hash": _hash_json(goal),
            "config_hash": _hash_json(config_snapshot),
            "base_commit": base_commit,
            "candidate_workspace": str(workspace),
            "backend": {"name": self.backend.name, **backend_health},
            "calls_started": 0,
            "remaining_calls": int(goal["budgets"]["max_model_calls"]),
            "rounds": {},
            "current_round": 1,
            "feedback_planning_rounds": 0,
            "no_progress_rounds": 0,
            "discovery": {"status": "pending"},
            "baseline_audit": {"status": "pending"},
            "engine_generated_paths": [],
            "candidate_artifact_paths": [],
            "proposal_ids": [],
            "full_reads_used": 0,
            "accepted_candidate_claims": [],
            "unresolved_questions": [],
            "token_usage": "unavailable",
            "api_cost": "unavailable",
            "stop_requested": False,
            "terminal_reason": None,
            "formal_knowledge_applied": False,
            "skills_modified": False,
        }
        save_state(run_dir, state)
        append_event(run_dir, "run_created", {"base_commit": base_commit, "goal_hash": state["goal_hash"], "config_hash": state["config_hash"], "backend": state["backend"]})
        self._write_run_skeleton(run_dir, goal, state)
        return run_dir

    @staticmethod
    def _new_run_id() -> str:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return f"phase15-{stamp}-{os.urandom(3).hex()}"

    def _workspace_path(self, run_id: str) -> Path:
        parent = self.root.parent
        return parent / f".{self.root.name}-evolution-{run_id}-workspace"

    def _write_run_skeleton(self, run_dir: Path, goal: dict[str, Any], state: dict[str, Any]) -> None:
        atomic_write_text(run_dir / "events.jsonl", "")
        atomic_write_text(run_dir / "final-report.md", f"# Self-Evolution Run {state['run_id']}\n\n- Status: `{state['status']}`\n- Goal hash: `{state['goal_hash']}`\n")
        append_event(run_dir, "run_skeleton_created", {"round_limit": goal["budgets"]["max_rounds"], "call_limit": goal["budgets"]["max_model_calls"]})

    def resume(self, run_id: str) -> dict[str, Any]:
        run_dir = safe_run_dir(self.root, run_id)
        state = load_state(run_dir)
        if state.get("status") in TERMINAL and state.get("status") not in {"INTERRUPTED", "FAILED"}:
            return state
        if state.get("status") == "INTERRUPTED":
            state["stop_requested"] = False
            state["finished_at"] = None
            state["terminal_reason"] = None
            (run_dir / "stop-requested.json").unlink(missing_ok=True)
            save_state(run_dir, state)
            append_event(run_dir, "resume_requested", {"last_status": "INTERRUPTED"})
        elif state.get("status") == "FAILED":
            state["finished_at"] = None
            state["terminal_reason"] = None
            transition(run_dir, state, "PLANNING", "Explicit resume requested after a failed stage; completed checkpoints remain reusable and retry budgets still apply.")
            append_event(run_dir, "resume_requested", {"last_status": "FAILED", "failed_stage_will_retry": True})
        return self.execute(run_dir)

    def run_new(self, goal: dict[str, Any], run_id: str | None = None) -> dict[str, Any]:
        return self.execute(self.create_run(goal, run_id))

    def execute(self, run_dir: Path) -> dict[str, Any]:
        controller_lock = run_dir / ".controller.lock"
        from scripts.evolution.common import file_lock
        with file_lock(controller_lock, timeout_seconds=0.2):
            goal = json.loads((run_dir / "goal.yaml").read_text(encoding="utf-8"))
            goal_snapshot_hash = _hash_json(goal)
            state = load_state(run_dir)
            config_snapshot = json.loads((run_dir / "engine-config.yaml").read_text(encoding="utf-8"))
            if state.get("goal_hash") != goal_snapshot_hash or state.get("config_hash") != _hash_json(config_snapshot):
                return self._terminate(run_dir, state, "BLOCKED", "Goal or config snapshot changed; refusing to continue under different constraints.")
            if _git(self.root, "rev-parse", "HEAD") != state["base_commit"]:
                return self._terminate(run_dir, state, "BLOCKED", "main HEAD changed since run creation; candidate base is stale and needs review.")
            if state.get("status") in TERMINAL and state.get("status") not in {"INTERRUPTED", "FAILED"}:
                return state
            self.config = config_snapshot
            if isinstance(self.backend, CodexCliBackend):
                try:
                    self.backend.healthcheck()
                except BackendError as exc:
                    return self._terminate(run_dir, state, "BLOCKED", f"Codex CLI backend unavailable: {exc.kind}")
            try:
                self._ensure_workspace(run_dir, state)
                if self.config.get("audit", {}).get("enabled", True):
                    self._ensure_baseline(run_dir, state)
                elif state.get("baseline_audit", {}).get("status") == "pending":
                    state["baseline_audit"] = {"status": "skipped", "reason": "user-scoped research run; full-worktree audit disabled"}
                    save_state(run_dir, state)
                self._ensure_discovery(run_dir, state, goal)
                if state["status"] in {"PENDING", "INTERRUPTED"}:
                    transition(run_dir, state, "PLANNING", "Python Controller starts dynamic planning.")
                self._run_rounds(run_dir, state, goal)
            except BudgetExhausted as exc:
                return self._terminate(run_dir, state, "BUDGET_EXHAUSTED", str(exc))
            except KeyboardInterrupt:
                return self._terminate(run_dir, state, "INTERRUPTED", "Controller received an interrupt; completed role outputs are checkpointed.")
            except BackendError as exc:
                append_event(run_dir, "backend_failure", {"kind": exc.kind, "task_id": exc.task_id, "retryable": exc.retryable, "metadata": exc.metadata})
                self._record_runtime_reflection(run_dir, state, exc)
                terminal = "INTERRUPTED" if exc.kind == "stopped" else "BUDGET_EXHAUSTED" if exc.kind == "tool_budget" else "BLOCKED" if exc.kind in {"authentication", "quota", "permission", "unsupported_cli", "unavailable"} else "FAILED"
                return self._terminate(run_dir, state, terminal, f"{exc.kind}: {str(exc)[:700]}")
            except Exception as exc:
                append_event(run_dir, "controller_failure", {"type": type(exc).__name__, "message": str(exc)[:1000]})
                return self._terminate(run_dir, state, "FAILED", f"{type(exc).__name__}: {str(exc)[:700]}")
            return load_state(run_dir)

    def _ensure_workspace(self, run_dir: Path, state: dict[str, Any]) -> None:
        workspace = Path(state["candidate_workspace"])
        if workspace.exists():
            os.chmod(workspace, 0o700)
            top = Path(_git(workspace, "rev-parse", "--show-toplevel")).resolve()
            if top != workspace.resolve() or _git(workspace, "rev-parse", "HEAD") != state["base_commit"]:
                raise RuntimeError("candidate worktree path or base commit does not match the run checkpoint")
            return
        if workspace.is_symlink():
            raise RuntimeError("candidate workspace cannot be a symlink")
        workspace.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "worktree", "add", "--detach", str(workspace), state["base_commit"]], cwd=self.root, capture_output=True, text=True, check=True, timeout=60)
        os.chmod(workspace, 0o700)
        top = Path(_git(workspace, "rev-parse", "--show-toplevel")).resolve()
        if top != workspace.resolve():
            raise RuntimeError("created candidate worktree resolved outside its dedicated path")
        append_event(run_dir, "candidate_workspace_ready", {"path": str(workspace), "base_commit": state["base_commit"]})

    def _ensure_baseline(self, run_dir: Path, state: dict[str, Any]) -> None:
        if state.get("baseline_audit", {}).get("status") == "complete":
            return
        workspace = Path(state["candidate_workspace"])
        audit_id = f"{state['run_id']}-baseline"
        result = self.audit_fn(root=workspace, run_id=audit_id)
        baseline_dir = run_dir / "baseline"
        baseline_dir.mkdir(parents=True, exist_ok=True)
        source_json = workspace / "evolution" / "audits" / f"{audit_id}.json"
        source_md = workspace / "evolution" / "audits" / f"{audit_id}.md"
        shutil.copy2(source_json, baseline_dir / "audit.json")
        shutil.copy2(source_md, baseline_dir / "audit.md")
        generated = [f"evolution/audits/{audit_id}.json", f"evolution/audits/{audit_id}.md"]
        state["engine_generated_paths"] = sorted(set(state.get("engine_generated_paths", [])) | set(generated))
        state["baseline_audit"] = {
            "status": "complete", "files_scanned": result["files_scanned"], "finding_count": result["finding_count"],
            "signatures": [list(_finding_signature(item)) for item in result.get("findings", [])],
            "report": str((baseline_dir / "audit.json").relative_to(run_dir)),
        }
        save_state(run_dir, state)
        append_event(run_dir, "baseline_audit_complete", {"files_scanned": result["files_scanned"], "finding_count": result["finding_count"], "historical_baseline": "first-evolution-20261125-v2"})

    def _ensure_discovery(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any]) -> None:
        if state.get("discovery", {}).get("status") != "pending":
            return
        discovery_cfg = self.config.get("discovery", {})
        if not discovery_cfg.get("enabled", True):
            state["discovery"] = {"status": "disabled", "result": {}}
            save_state(run_dir, state)
            return
        append_event(run_dir, "discovery_started", {
            "focus": goal.get("research_focus"),
            "topic_ids": discovery_cfg.get("topic_ids", []),
            "query_override": discovery_cfg.get("query_override"),
            "sources": discovery_cfg.get("sources", []),
        })
        try:
            result = self.discovery_fn(
                root=self.root,
                topic_ids=[topic for topic in discovery_cfg.get("topic_ids", []) if topic in goal["allowed_topic_ids"]],
                initial_lookback_days=int(discovery_cfg.get("lookback_days", 90)),
                screen_limit=min(int(self.config["budgets"]["max_screened_candidates_per_round"]), 20),
                source_filter=set(discovery_cfg.get("sources", [])),
                run_id=f"engine-discovery-{state['run_id']}",
                query_override=discovery_cfg.get("query_override"),
                topic_overrides=discovery_cfg.get("topic_overrides", {}),
            )
            state["discovery"] = {
                "status": result.get("status", "unknown"),
                "topics": result.get("topics", []),
                "candidates_added": result.get("candidates_added", 0),
                "candidate_version_updates": result.get("candidate_version_updates", 0),
                "duplicates": result.get("duplicates", 0),
                "source_results": result.get("source_results", []),
                "errors": result.get("errors", []),
            }
            append_event(run_dir, "discovery_complete", {key: state["discovery"].get(key) for key in ("status", "candidates_added", "candidate_version_updates", "duplicates")})
        except Exception as exc:
            # Provider failure is recorded and the prior candidate queue remains usable.
            state["discovery"] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
            append_event(run_dir, "discovery_failed_fallback_to_existing_queue", state["discovery"])
        save_state(run_dir, state)

    def _remaining_seconds(self, state: dict[str, Any], goal: dict[str, Any]) -> int:
        elapsed = time.time() - float(state.get("started_epoch", time.time()))
        remaining = int(goal["budgets"]["run_timeout_seconds"] - elapsed)
        if remaining <= 0:
            raise BudgetExhausted("wall-clock run budget exhausted; the research goal is not marked complete")
        return remaining

    def _invoke(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any], role: str, prompt: str, round_number: int, sandbox: str, force_new: bool = False) -> dict[str, Any]:
        round_key = str(round_number)
        round_dir = run_dir / f"round_{round_number:02d}"
        round_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(round_dir, 0o700)
        role_state = state.setdefault("rounds", {}).setdefault(round_key, {}).setdefault("stages", {}).setdefault(role, {"status": "pending", "attempts": 0, "errors": []})
        output_file = round_dir / f"{role}.json"
        checkpoint_file = run_dir / role_state.get("output", str(output_file.relative_to(run_dir))) if role_state.get("output") else output_file
        if role_state.get("status") == "complete" and checkpoint_file.exists() and not force_new:
            value = json.loads(checkpoint_file.read_text(encoding="utf-8"))
            errors = validate_json(value, SCHEMAS[role])
            if errors:
                raise RuntimeError(f"checkpointed {role} output is invalid: {'; '.join(errors[:6])}")
            append_event(run_dir, "completed_stage_reused", {"round": round_number, "role": role})
            return value
        max_attempts = 1 + int(goal["budgets"]["max_retries_per_task"])
        while int(role_state.get("attempts", 0)) < max_attempts:
            if is_stop_requested(run_dir):
                raise BackendError("stopped", "user stop requested", f"{state['run_id']}-r{round_number:02d}-{role}")
            if calls_remaining(state, goal) <= 0:
                raise BudgetExhausted("model call budget exhausted; no additional Planner/Executor/Evaluator/Reflector calls may start")
            remaining_seconds = self._remaining_seconds(state, goal)
            attempt = int(role_state.get("attempts", 0)) + 1
            output_file = round_dir / (f"{role}.json" if attempt == 1 else f"{role}-attempt-{attempt:02d}.json")
            task_id = f"{state['run_id']}-r{round_number:02d}-{role}-a{attempt:02d}"
            task_dir = run_dir / "tasks" / task_id
            task_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
            os.chmod(task_dir, 0o700)
            role_state.update({"status": "running", "attempts": attempt, "task_id": task_id, "started_at": utc_now()})
            state["calls_started"] = int(state.get("calls_started", 0)) + 1
            state["remaining_calls"] = max(0, int(goal["budgets"]["max_model_calls"]) - state["calls_started"])
            save_state(run_dir, state)
            append_event(run_dir, "model_call_started", {"task_id": task_id, "role": role, "round": round_number, "call_count": state["calls_started"], "call_limit": goal["budgets"]["max_model_calls"], "sandbox": sandbox})
            search_limits = goal["budgets"].get("max_web_search_calls_by_role", {})
            search_limit = int(search_limits.get(role, goal["budgets"].get("max_web_search_calls_per_task", 4)))
            role_timeouts = self.config["budgets"].get("role_timeout_seconds", {})
            role_timeout = int(role_timeouts.get(role, self.config["budgets"]["task_timeout_seconds"]))
            request = BackendRequest(
                task_id=task_id, role=role, prompt=prompt, schema=SCHEMAS[role], workspace=Path(state["candidate_workspace"]),
                task_dir=task_dir, timeout_seconds=min(role_timeout, int(self.config["budgets"]["task_timeout_seconds"]), remaining_seconds),
                sandbox=sandbox, search=bool(self.config["backend"].get("search", True)) and search_limit > 0,
                max_search_calls=search_limit,
                model=self.config["backend"].get("model"), reasoning_effort=self.config["backend"].get("reasoning_effort"),
                stop_requested=lambda: is_stop_requested(run_dir),
            )
            expected_sandbox = {"planner": "read-only", "executor": "workspace-write", "evaluator": "read-only", "reflector": "read-only"}[role]
            if sandbox != expected_sandbox or self.config.get("permissions", {}).get(role) != expected_sandbox:
                raise BackendError("permission", f"role {role} sandbox is not the configured fixed boundary", task_id)
            try:
                response = self.backend.invoke(request)
                errors = validate_json(response.output, SCHEMAS[role])
                if errors:
                    raise BackendError("schema", "; ".join(errors[:8]), task_id)
                atomic_write_json(output_file, response.output)
                role_state.update({"status": "complete", "output": str(output_file.relative_to(run_dir)), "finished_at": utc_now(), "model": response.model or "unavailable", "usage": response.usage, "backend_metadata": response.metadata})
                state.setdefault("model_usage", []).append({"task_id": task_id, "role": role, "usage": response.usage, "model": response.model or "unavailable"})
                save_state(run_dir, state)
                append_event(run_dir, "model_call_complete", {"task_id": task_id, "role": role, "model": response.model or "unavailable", "usage": response.usage, "elapsed_seconds": response.metadata.get("elapsed_seconds")})
                return response.output
            except BackendError as exc:
                role_state.setdefault("errors", []).append({"task_id": task_id, "kind": exc.kind, "message": str(exc)[:900], "retryable": exc.retryable, "metadata": exc.metadata})
                role_state["status"] = "failed"
                save_state(run_dir, state)
                append_event(run_dir, "model_call_failed", {"task_id": task_id, "role": role, "kind": exc.kind, "retryable": exc.retryable, "attempt": attempt})
                if not exc.retryable or attempt >= max_attempts:
                    raise
            except Exception as exc:
                role_state.setdefault("errors", []).append({"kind": type(exc).__name__, "message": str(exc)[:900], "retryable": False})
                role_state["status"] = "failed"
                save_state(run_dir, state)
                raise
        raise RuntimeError(f"{role} attempts exhausted unexpectedly")

    def _reflect(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any], round_number: int, plan: dict[str, Any] | None, execution: dict[str, Any] | None, evaluation: dict[str, Any] | None, backend_error: dict[str, Any] | None = None, force_new: bool = False) -> dict[str, Any]:
        if state["status"] not in {"REFLECTING"}:
            transition(run_dir, state, "REFLECTING", "Failure or evaluator feedback requires diagnosis.")
        round_data = state.setdefault("rounds", {}).setdefault(str(round_number), {})
        reflector_stage = round_data.setdefault("stages", {}).setdefault("reflector", {"status": "pending", "attempts": 0, "errors": []})
        context_hash = _hash_json({"plan": plan, "execution": execution, "evaluation": evaluation, "backend_error": backend_error})
        if reflector_stage.get("status") == "complete" and reflector_stage.get("reflection_context_hash") != context_hash:
            force_new = True
            reflector_stage["status"] = "pending"
        reflector_stage["reflection_context_hash"] = context_hash
        save_state(run_dir, state)
        prompt = reflector.build_prompt(goal, plan, execution, evaluation, backend_error, self._active_experiences)
        try:
            result = self._invoke(run_dir, state, goal, "reflector", prompt, round_number, "read-only", force_new=force_new)
            state["rounds"].setdefault(str(round_number), {})["reflection"] = result
            append_event(run_dir, "reflection_recorded", {"round": round_number, "failure_type": result.get("failure_type"), "replan": result.get("replan"), "retry_worthwhile": result.get("retry_worthwhile")})
        except (BackendError, BudgetExhausted) as exc:
            if isinstance(exc, BudgetExhausted):
                raise
            result = {
                "failure_type": backend_error.get("kind", "other") if backend_error else "other",
                "failure_evidence": [str(exc)[:600]], "possible_causes": ["The bounded model backend did not return a usable reflection."],
                "ineffective_attempts": [], "retry_worthwhile": False,
                "next_step": "Stop this stage; preserve its diagnostic and use a new run only after the backend condition changes.", "replan": False,
                "knowledge_summary": [item.get("statement", "")[:400] for item in (execution or {}).get("findings", [])[:8]],
                "remaining_gaps": (evaluation or {}).get("unresolved_questions", [])[:8],
                "feedback_refs": [item.get("finding_id", "") for item in (execution or {}).get("findings", [])[:8]],
                "reflection_backend": "deterministic fallback",
            }
            state["rounds"].setdefault(str(round_number), {})["reflection"] = result
            append_event(run_dir, "deterministic_reflection_fallback", {"round": round_number, "error_kind": getattr(exc, "kind", "budget")})
        state["rounds"].setdefault(str(round_number), {})["stages"]["reflector"] = {"status": "complete", "result": result}
        save_state(run_dir, state)
        return result

    def _round_feedback_refs(self, state: dict[str, Any], round_number: int) -> set[str]:
        references: set[str] = set()
        for key, item in state.get("rounds", {}).items():
            if int(key) >= round_number:
                continue
            references.update(item.get("knowledge_gain", {}).get("feedback_ids", []))
            references.update(item.get("unresolved_question_ids", []))
            references.update(item.get("reflection", {}).get("feedback_refs", []))
        return references

    def _run_rounds(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any]) -> None:
        experience_config = {
            **self.config,
            "experience_skill_names": [*goal.get("existing_skill_protocols", {}).keys(), "experience-memory"],
            "fixed_candidate_queue": goal.get("fixed_candidate_queue"),
        }
        base_memory = memory.initial_memory(self.root, experience_config)
        self._active_experiences = base_memory.get("relevant_experiences", [])[:5]
        max_rounds = int(goal["budgets"]["max_rounds"])
        next_round = int(state.get("current_round", 1))
        while next_round <= max_rounds:
            if is_stop_requested(run_dir):
                self._terminate(run_dir, state, "INTERRUPTED", "User requested a stop between stages.")
                return
            if time.time() - float(state.get("started_epoch", time.time())) >= int(goal["budgets"]["run_timeout_seconds"]):
                raise BudgetExhausted("wall-clock budget exhausted; goal completion has not been established")
            if state["status"] != "PLANNING":
                transition(run_dir, state, "PLANNING", f"Planner selects the next task for outer round {next_round} from current memory.")
            state["current_round"] = next_round
            current_memory = memory.planner_memory(base_memory, state, next_round, state.get("discovery"))
            current_memory["remaining_calls"] = calls_remaining(state, goal)
            current_memory["remaining_full_reads"] = full_reads_remaining(state, goal)
            prompt = planner.build_prompt(goal, current_memory, next_round)
            plan = self._invoke(run_dir, state, goal, "planner", prompt, next_round, "read-only")
            plan_errors = planner.validate_plan(plan, goal, current_memory, next_round)
            if plan_errors:
                reflect_result = self._reflect(run_dir, state, goal, next_round, plan, None, {"hard_errors": plan_errors})
                round_data = state["rounds"].setdefault(str(next_round), {})
                round_data["plan_validation_errors"] = plan_errors
                round_data["reflection"] = reflect_result
                if not reflect_result.get("retry_worthwhile"):
                    self._terminate(run_dir, state, "NEEDS_REVIEW", "Planner output violated immutable Goal or feedback-reference constraints.")
                    return
                # A corrected Planner call uses the same round and counts against the same shared budget.
                retry_memory = {**current_memory, "planner_rejection": plan_errors, "reflection": reflect_result}
                prompt = planner.build_prompt(goal, retry_memory, next_round)
                if state["status"] == "REFLECTING":
                    transition(run_dir, state, "PLANNING", "Reflection requested a corrected plan.")
                plan = self._invoke(run_dir, state, goal, "planner", prompt, next_round, "read-only", force_new=True)
                plan_errors = planner.validate_plan(plan, goal, retry_memory, next_round)
                if plan_errors:
                    self._terminate(run_dir, state, "NEEDS_REVIEW", "Planner still violated scope or feedback constraints after one correction.")
                    return
            round_data = state["rounds"].setdefault(str(next_round), {})
            round_data["plan"] = plan
            round_data.setdefault("feedback_ids_used", []).extend(ref for ref in plan.get("feedback_refs", []) if ref not in round_data.get("feedback_ids_used", []))
            if next_round > 1 and set(plan.get("feedback_refs", [])) & self._round_feedback_refs(state, next_round):
                state["feedback_planning_rounds"] = int(state.get("feedback_planning_rounds", 0)) + 1
                round_data["feedback_driven_plan"] = True
            else:
                round_data["feedback_driven_plan"] = False
            save_state(run_dir, state)
            append_event(run_dir, "plan_selected", {"round": next_round, "decision": plan["decision"], "topic_id": plan.get("topic_id"), "research_question": plan.get("research_question"), "feedback_refs": plan.get("feedback_refs", []), "feedback_driven": round_data["feedback_driven_plan"]})

            if plan["decision"] in {"complete", "no_update_needed"}:
                if goal_criteria_satisfied(state, goal):
                    self._terminate(run_dir, state, "COMPLETED", plan.get("stop_reason") or "The Planner found no valuable follow-up after evidence-backed gains met the run's acceptance criteria.")
                else:
                    self._terminate(run_dir, state, "NO_UPDATE_NEEDED", plan.get("stop_reason") or "No high-value next task was supported by the current evidence; acceptance criteria remain incomplete.")
                return
            if plan["decision"] == "needs_review":
                self._terminate(run_dir, state, "NEEDS_REVIEW", plan.get("stop_reason") or plan.get("rationale", "Planner requested human review."))
                return
            if next_round > 1 and not round_data["feedback_driven_plan"]:
                self._terminate(run_dir, state, "NEEDS_REVIEW", "Autonomous planning could not demonstrate use of a prior round's exact finding or unresolved-question ID.")
                return

            expected_artifact = f"evolution/runs/{state['run_id']}/round_{next_round:02d}/candidate/research-memo.md"
            state["remaining_full_reads"] = full_reads_remaining(state, goal)
            execution_result, deterministic, llm_evaluation = self._execute_and_evaluate(run_dir, state, goal, next_round, plan, current_memory, expected_artifact)
            if execution_result is None:
                return
            normalized = round_data.get("normalized_execution") or executor.normalize_execution(execution_result, next_round)
            atomic_write_json(run_dir / f"round_{next_round:02d}" / "normalized-execution.json", normalized)
            round_data["execution_summary"] = {"status": normalized["status"], "finding_ids": [item["finding_id"] for item in normalized["findings"]], "papers": normalized["papers"]}
            round_data["deterministic_evaluation"] = deterministic
            round_data["evaluation"] = llm_evaluation
            round_data["full_reads"] = int(deterministic.get("full_reads", 0))
            state["full_reads_used"] = int(state.get("full_reads_used", 0)) + int(deterministic.get("full_reads", 0))
            if llm_evaluation.get("decision") == "NEEDS_REVIEW" or round_data.get("audit_delta", {}).get("new_findings", 0):
                round_data["status"] = "needs_review"
                state["no_progress_rounds"] = int(state.get("no_progress_rounds", 0)) + 1
                save_state(run_dir, state)
                self._terminate(run_dir, state, "NEEDS_REVIEW", llm_evaluation.get("rationale", "A hard audit or evaluator gate requires human review."))
                return
            elif normalized.get("status") == "no_update_needed" or llm_evaluation.get("decision") == "NO_UPDATE_NEEDED":
                round_data["knowledge_gain"] = self._empty_gain(normalized, llm_evaluation)
                round_data["unresolved_questions"] = _round_unresolved_questions(
                    llm_evaluation, normalized, round_data.get("reflection"),
                )
                round_data["unresolved_question_ids"] = [f"q-r{next_round:02d}-{idx:02d}" for idx, _ in enumerate(round_data["unresolved_questions"], start=1)]
                round_data["status"] = "evaluated"
                state["no_progress_rounds"] = int(state.get("no_progress_rounds", 0)) + 1
                save_state(run_dir, state)
                append_event(run_dir, "no_update_round", {"round": next_round, "reason": llm_evaluation.get("rationale", "no verifiable increment")})
            elif llm_evaluation.get("decision") == "PASS" and deterministic.get("batch_validity_gate", deterministic.get("source_validity_gate")):
                gain = self._knowledge_gain(normalized, llm_evaluation, round_data)
                round_data["knowledge_gain"] = gain
                round_data["unresolved_questions"] = _round_unresolved_questions(
                    llm_evaluation, normalized, round_data.get("reflection"),
                )
                round_data["unresolved_question_ids"] = [f"q-r{next_round:02d}-{idx:02d}" for idx, _ in enumerate(round_data["unresolved_questions"], start=1)]
                round_data["status"] = "evaluated"
                if gain["accepted_findings"]:
                    state["no_progress_rounds"] = 0
                    state["accepted_candidate_claims"].extend(gain["accepted_findings"])
                    state["unresolved_questions"] = round_data["unresolved_questions"]
                else:
                    state["no_progress_rounds"] = int(state.get("no_progress_rounds", 0)) + 1
                save_state(run_dir, state)
            else:
                round_data["status"] = "needs_review"
                state["no_progress_rounds"] = int(state.get("no_progress_rounds", 0)) + 1
                save_state(run_dir, state)
                if llm_evaluation.get("decision") == "RETRY":
                    self._terminate(run_dir, state, "NEEDS_REVIEW", "The bounded in-round correction loop has ended without a passing evaluation.")
                    return
                if llm_evaluation.get("decision") == "REPLAN":
                    if state["status"] != "REFLECTING":
                        transition(run_dir, state, "REFLECTING", "Independent evaluation requests a new bounded plan.")
                    reflection_result = self._reflect(run_dir, state, goal, next_round, plan, normalized, llm_evaluation)
                    round_data["reflection"] = reflection_result
                    if reflection_result.get("replan"):
                        round_data["status"] = "replan_requested"
                        round_data["unresolved_questions"] = _round_unresolved_questions(
                            llm_evaluation, normalized, reflection_result,
                        )
                        round_data["unresolved_question_ids"] = [f"q-r{next_round:02d}-{idx:02d}" for idx, _ in enumerate(round_data["unresolved_questions"], start=1)]
                        round_data.setdefault("knowledge_gain", self._empty_gain(normalized, llm_evaluation))
                        state["current_round"] = next_round + 1
                        transition(run_dir, state, "PLANNING", "Reflection requests a new plan based on the evaluated failure.")
                        next_round += 1
                        continue
                self._terminate(run_dir, state, "NEEDS_REVIEW", llm_evaluation.get("rationale", "Independent evaluation did not pass."))
                return

            self._write_round_knowledge_gain(run_dir, state, next_round)
            if should_stop_no_progress(state, goal):
                self._terminate(run_dir, state, "NO_PROGRESS", "Two consecutive evaluated outer rounds produced no accepted, evidence-backed gain.")
                return
            if next_round >= max_rounds:
                if goal_criteria_satisfied(state, goal):
                    self._terminate(run_dir, state, "COMPLETED", "Configured outer-round limit reached after the acceptance criteria were met.")
                else:
                    self._terminate(run_dir, state, "BUDGET_EXHAUSTED", "Maximum outer research rounds reached; the goal is not marked complete.")
                return
            state["current_round"] = next_round + 1
            save_state(run_dir, state)
            if state["status"] == "EVALUATING":
                transition(run_dir, state, "PLANNING", "Select the next task from evaluated knowledge gain and unresolved questions.")
            next_round += 1

    def _execute_and_evaluate(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any], round_number: int, plan: dict[str, Any], current_memory: dict[str, Any], artifact_path: str) -> tuple[dict[str, Any] | None, dict[str, Any], dict[str, Any]]:
        round_data = state["rounds"].setdefault(str(round_number), {})
        semantic_attempt = int(round_data.get("executor_retries", 0))
        retry_feedback = round_data.get("executor_retry_feedback", {})
        if semantic_attempt and not retry_feedback:
            retry_feedback = read_json(run_dir / f"round_{round_number:02d}" / "reflector.json", {})
            if retry_feedback:
                round_data["executor_retry_feedback"] = retry_feedback
                save_state(run_dir, state)
        while True:
            if state["status"] in {"PLANNING", "RETRYING"}:
                transition(run_dir, state, "RUNNING", "Executor receives the validated Planner task in the isolated worktree.")
            round_dir = run_dir / f"round_{round_number:02d}"
            executor_stage = round_data.get("stages", {}).get("executor", {})
            if executor_stage.get("status") != "complete":
                remaining = calls_remaining(state, goal)
                reserved = executor_calls_reserved(state, goal, round_number)
                if remaining <= reserved:
                    raise BudgetExhausted(f"Executor stopped with {remaining} calls remaining to reserve {reserved} for evaluation, reflection, and the next Planner.")
            if executor_stage.get("status") == "complete":
                attempt_number = max(1, int(executor_stage.get("attempts", 1)))
            else:
                attempt_number = max(1, int(executor_stage.get("attempts", 0)) + 1)
            base_path = Path(artifact_path)
            attempt_artifact_path = artifact_path if attempt_number == 1 else str(base_path.with_name(f"{base_path.stem}-attempt-{attempt_number:02d}{base_path.suffix}"))
            prior_numbers, prior_outputs = _executor_attempt_outputs(round_dir, before_attempt=attempt_number)
            executor_context = memory.executor_memory(current_memory, plan, self.config)
            prompt = executor.build_prompt(
                goal, plan, executor_context, attempt_artifact_path, retry_feedback,
                _executor_attempt_context(prior_numbers, prior_outputs),
            )
            try:
                execution_result = self._invoke(run_dir, state, goal, "executor", prompt, round_number, "workspace-write", force_new=executor_stage.get("status") == "retry_pending")
            except BackendError as exc:
                if exc.kind == "tool_budget":
                    raise
                reflection_result = self._reflect(run_dir, state, goal, round_number, plan, None, None, {"kind": exc.kind, "message": str(exc), "retryable": exc.retryable}, force_new=semantic_attempt > 0)
                round_data["reflection"] = reflection_result
                if exc.kind in {"quota", "authentication", "permission", "unavailable", "stopped"} or not reflection_result.get("retry_worthwhile"):
                    terminal = "INTERRUPTED" if exc.kind == "stopped" else "BLOCKED" if exc.kind in {"quota", "authentication", "permission", "unavailable"} else "NEEDS_REVIEW"
                    self._terminate(run_dir, state, terminal, f"Executor backend failure ({exc.kind}); failure is recorded and not repeated indefinitely.")
                    return None, {}, {}
                used_attempts = int(round_data.get("stages", {}).get("executor", {}).get("attempts", 0))
                if used_attempts >= 1 + int(goal["budgets"]["max_retries_per_task"]):
                    self._terminate(run_dir, state, "NEEDS_REVIEW", "Executor backend retries reached the per-task cap.")
                    return None, {}, {}
                if semantic_attempt >= int(goal["budgets"]["max_retries_per_task"]):
                    self._terminate(run_dir, state, "NEEDS_REVIEW", "Executor failure exceeded the bounded task retry count.")
                    return None, {}, {}
                retry_feedback = reflection_result
                semantic_attempt += 1
                round_data["executor_retries"] = semantic_attempt
                round_data["executor_retry_feedback"] = retry_feedback
                round_data.setdefault("stages", {}).setdefault("executor", {})["status"] = "retry_pending"
                save_state(run_dir, state)
                transition(run_dir, state, "RETRYING", "Reflection recommends a bounded retry after an executor failure.")
                continue
            if execution_result.get("status") == "completed":
                reported_path = execution_result.get("artifact_path", "")
                if reported_path != attempt_artifact_path or not executor.artifact_path_allowed(reported_path, state["run_id"], round_number):
                    execution_result["controller_path_error"] = "Executor did not use the controller-assigned attempt-specific artifact path."
                artifact_abs = Path(state["candidate_workspace"]) / reported_path
                if reported_path == attempt_artifact_path and artifact_abs.is_file() and not artifact_abs.is_symlink():
                    content = artifact_abs.read_text(encoding="utf-8", errors="replace")
                    if len(content) > 80_000:
                        execution_result["controller_path_error"] = "Candidate artifact exceeds the 80 KB cap."
                    else:
                        artifact_name = "research-memo.md" if attempt_number == 1 else f"research-memo-attempt-{attempt_number:02d}.md"
                        destination = round_dir / "artifacts" / artifact_name
                        atomic_write_text(destination, content)
                        round_data.setdefault("artifact_attempts", {})[str(attempt_number)] = {
                            "path": str(destination.relative_to(run_dir)),
                            "candidate_path": reported_path,
                            "sha256": sha256_file(destination),
                            "bytes": len(content.encode("utf-8")),
                        }
                        round_data["artifact"] = round_data["artifact_attempts"][str(attempt_number)]
                        if reported_path not in state.setdefault("candidate_artifact_paths", []):
                            state["candidate_artifact_paths"].append(reported_path)
                else:
                    execution_result["controller_path_error"] = "Expected candidate artifact is missing or not a regular file."
            if execution_result.get("controller_path_error"):
                append_event(run_dir, "candidate_artifact_rejected", {"round": round_number, "reason": execution_result["controller_path_error"]})
            workspace = Path(state["candidate_workspace"])
            dirty_paths = _clean_git_paths(workspace)
            allowed_dirty = set(state.get("engine_generated_paths", [])) | set(state.get("candidate_artifact_paths", []))
            unexpected = sorted(dirty_paths - allowed_dirty)
            if _git(workspace, "rev-parse", "HEAD") != state["base_commit"]:
                unexpected.append("candidate worktree HEAD changed")
            if unexpected:
                execution_result["controller_permission_error"] = "Executor changed paths outside its candidate artifacts: " + ", ".join(unexpected[:20])
            existing = read_jsonl(self.root / "evolution" / "claims" / "claims.jsonl")
            previous = [finding for data in state.get("rounds", {}).values() for finding in data.get("knowledge_gain", {}).get("accepted_findings", [])]
            attempt_numbers, attempt_outputs = _executor_attempt_outputs(round_dir)
            if not attempt_outputs:
                attempt_numbers, attempt_outputs = [attempt_number], [execution_result]
            normalized = executor.merge_attempts(
                attempt_outputs, round_number,
                {str(item.get("claim_id")) for item in existing if item.get("claim_id")},
                attempt_numbers,
            )
            deterministic = evaluator.deterministic_evaluation(normalized, plan, goal, existing, previous, self.source_getter)
            if execution_result.get("controller_path_error"):
                deterministic["hard_errors"].append({"type": "artifact_path", "evidence": execution_result["controller_path_error"]})
                deterministic["source_validity_gate"] = False
                deterministic["batch_validity_gate"] = False
            if execution_result.get("controller_permission_error"):
                deterministic["hard_errors"].append({"type": "permission", "evidence": execution_result["controller_permission_error"]})
                deterministic["source_validity_gate"] = False
                deterministic["batch_validity_gate"] = False
            if state.get("full_reads_used", 0) + deterministic.get("full_reads", 0) > int(goal["budgets"]["max_full_reads"]):
                deterministic["hard_errors"].append({"type": "run_read_budget", "evidence": "cumulative full reads exceed the Goal budget"})
                deterministic["source_validity_gate"] = False
                deterministic["batch_validity_gate"] = False
            raw_evidence = []
            for paper in normalized.get("papers", []):
                source_record = {key: paper.get(key) for key in ("source_id", "source_version", "source_uri", "title", "reading_extent", "locators")}
                local_material = find_local_paper_material(self.root, paper)
                if any(local_material.values()):
                    source_record["local_paper_material"] = local_material
                raw_evidence.append(source_record)
            atomic_write_json(run_dir / f"round_{round_number:02d}" / f"deterministic-evaluation-attempt-{semantic_attempt + 1:02d}.json", deterministic)
            if state["status"] == "RUNNING":
                transition(run_dir, state, "EVALUATING", "Deterministic artifact/evidence/policy checks completed; independent Judge is next.")
            judge_prompt = evaluator.build_judge_prompt(goal, plan, normalized, deterministic, raw_evidence, current_memory, round_number)
            evaluator_stage = round_data.setdefault("stages", {}).setdefault("evaluator", {"status": "pending", "attempts": 0, "errors": []})
            if evaluator_stage.get("status") == "complete" and evaluator_stage.get("executor_semantic_attempt") != semantic_attempt:
                evaluator_stage["status"] = "pending"
            evaluator_stage["executor_semantic_attempt"] = semantic_attempt
            save_state(run_dir, state)
            llm_eval = self._invoke(run_dir, state, goal, "evaluator", judge_prompt, round_number, "read-only")
            accepted = set(llm_eval.get("accepted_finding_ids", []))
            finding_ids = {item["finding_id"] for item in normalized.get("findings", [])}
            if accepted - finding_ids or set(llm_eval.get("rejected_finding_ids", [])) - finding_ids:
                llm_eval["controller_schema_error"] = "Evaluator referenced a finding ID absent from Executor output."
                llm_eval["decision"] = "NEEDS_REVIEW"
            invalid_finding_ids = set(deterministic.get("invalid_finding_ids", []))
            deterministic["judge_accepted_invalid_finding_ids"] = sorted(accepted & invalid_finding_ids)
            llm_eval["accepted_finding_ids"] = sorted(accepted - invalid_finding_ids)
            llm_eval["rejected_finding_ids"] = sorted(set(llm_eval.get("rejected_finding_ids", [])) | invalid_finding_ids)
            if deterministic["hard_errors"]:
                llm_eval["controller_hard_gate"] = "Deterministic hard errors cannot be overridden by the LLM Judge."
                llm_eval["decision"] = "NEEDS_REVIEW"
            round_data.update({"raw_execution": execution_result, "normalized_execution": normalized, "deterministic_evaluation": deterministic, "evaluation": llm_eval})
            atomic_write_json(run_dir / f"round_{round_number:02d}" / f"execution-attempt-{semantic_attempt + 1:02d}.json", execution_result)
            atomic_write_json(run_dir / f"round_{round_number:02d}" / f"normalized-execution-attempt-{semantic_attempt + 1:02d}.json", normalized)
            atomic_write_json(run_dir / f"round_{round_number:02d}" / f"llm-evaluation-attempt-{semantic_attempt + 1:02d}.json", llm_eval)
            # This is a deterministic, read-only audit of the isolated workspace, compared to its own pre-run baseline.
            self._run_round_audit(run_dir, state, round_number)
            save_state(run_dir, state)
            if llm_eval.get("decision") != "RETRY" or semantic_attempt >= int(goal["budgets"]["max_retries_per_task"]):
                if state["status"] == "REFLECTING":
                    transition(run_dir, state, "EVALUATING", "No additional task retry remains; retain the independent evaluator's decision.")
                if llm_eval.get("decision") in {"PASS", "NO_UPDATE_NEEDED"}:
                    reflection_result = self._reflect(run_dir, state, goal, round_number, plan, normalized, llm_eval)
                    round_data["reflection"] = reflection_result
                    save_state(run_dir, state)
                    if state["status"] == "REFLECTING":
                        transition(run_dir, state, "EVALUATING", "Reflector summarized candidate knowledge and remaining gaps for the next Planner.")
                return execution_result, deterministic, llm_eval
            if state["status"] == "EVALUATING":
                transition(run_dir, state, "REFLECTING", "Independent Evaluator requests a targeted correction.")
            reflection_result = self._reflect(run_dir, state, goal, round_number, plan, normalized, llm_eval)
            round_data["reflection"] = reflection_result
            if not reflection_result.get("retry_worthwhile"):
                transition(run_dir, state, "EVALUATING", "Reflection found no safe bounded retry.")
                return execution_result, deterministic, llm_eval
            retry_feedback = reflection_result
            semantic_attempt += 1
            round_data["executor_retries"] = semantic_attempt
            round_data["executor_retry_feedback"] = retry_feedback
            round_data.setdefault("stages", {}).setdefault("executor", {})["status"] = "retry_pending"
            save_state(run_dir, state)
            transition(run_dir, state, "RETRYING", "Reflection recommends a targeted correction; shared call budget still applies.")

    @staticmethod
    def _empty_gain(normalized: dict[str, Any], evaluation_result: dict[str, Any]) -> dict[str, Any]:
        return {
            "accepted_findings": [], "qualified_claim_ids": [], "new_conflicts": [], "gap_progress": evaluation_result.get("gap_progress", []),
            "new_evidence_relations": [], "duplicate_or_invalid_findings": [item["finding_id"] for item in normalized.get("findings", [])],
            "unverified_knowledge": [], "next_step_impact": evaluation_result.get("rationale", "No verified knowledge change."),
            "candidate_gain": 0, "approved_formal_gain": 0, "feedback_ids": [],
        }

    def _knowledge_gain(self, normalized: dict[str, Any], evaluation_result: dict[str, Any], round_data: dict[str, Any]) -> dict[str, Any]:
        accepted_ids = set(evaluation_result.get("accepted_finding_ids", []))
        claims = [item for item in normalized.get("findings", []) if item["finding_id"] in accepted_ids and not item.get("duplicate_or_repeated")]
        feedback_ids = [item["finding_id"] for item in claims]
        gaps = evaluation_result.get("gap_progress", [])
        conflicts = [item for item in claims if item.get("relation") == "contradicts"]
        qualified = [item.get("related_claim_ids", []) for item in claims if item.get("relation") == "qualifies"]
        return {
            "accepted_findings": claims,
            "qualified_claim_ids": sorted({claim_id for group in qualified for claim_id in group}),
            "new_conflicts": [item["finding_id"] for item in conflicts],
            "gap_progress": gaps,
            "new_evidence_relations": [{"finding_id": item["finding_id"], "relation": item["relation"], "related_claim_ids": item.get("related_claim_ids", [])} for item in claims],
            "duplicate_or_invalid_findings": [item["finding_id"] for item in normalized.get("findings", []) if item.get("duplicate_or_repeated") or item["finding_id"] not in accepted_ids],
            "unverified_knowledge": [],
            "next_step_impact": evaluation_result.get("rationale", ""),
            "candidate_gain": len(claims),
            "approved_formal_gain": 0,
            "feedback_ids": feedback_ids,
        }

    def _create_claim_proposal(self, run_dir: Path, state: dict[str, Any], goal: dict[str, Any], round_number: int, findings: list[dict[str, Any]]) -> Path | None:
        claim_file = self.root / "evolution" / "claims" / "claims.jsonl"
        old_text = claim_file.read_text(encoding="utf-8") if claim_file.exists() else ""
        known_ids = {item.get("claim_id") for item in read_jsonl(claim_file)}
        new_claims = []
        evidence_bundle = []
        for item in findings:
            source_id = str(item["source_id"])
            claim_id = "phase15." + stable_hash(source_id + "|" + normalize_title(item["statement"]), 24)
            if claim_id in known_ids:
                continue
            related_ids = [value for value in item.get("related_claim_ids", []) if value in known_ids]
            record = {
                "claim_id": claim_id,
                "statement": item["statement"],
                "claim_type": item["claim_type"],
                "scope": item["scope"],
                "status": "needs_review",
                "evidence": [{
                    "source_id": source_id, "source_version": item["source_version"], "source_uri": item["source_uri"],
                    "locator": item["locator"], "relation": item["relation"], "accessed_at": dt.date.today().isoformat(),
                }],
                "related_claims": related_ids,
                "supersedes": [],
                "last_reviewed_at": dt.date.today().isoformat(),
                "candidate_run": state["run_id"],
                "evidence_excerpt": item["evidence_quote"],
            }
            errors = validate_claim(record)
            if errors:
                append_event(run_dir, "claim_candidate_rejected", {"claim_id": claim_id, "errors": errors})
                continue
            new_claims.append(record)
            evidence_bundle.append(record["evidence"][0])
            known_ids.add(claim_id)
        if not new_claims:
            return None
        new_text = old_text
        if new_text and not new_text.endswith("\n"):
            new_text += "\n"
        new_text += "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in new_claims)
        patch_lines = list(difflib.unified_diff(old_text.splitlines(), new_text.splitlines(), fromfile="a/evolution/claims/claims.jsonl", tofile="b/evolution/claims/claims.jsonl", lineterm=""))
        patch_text = "diff --git a/evolution/claims/claims.jsonl b/evolution/claims/claims.jsonl\n" + "\n".join(patch_lines) + "\n"
        proposal_id = f"phase15-{state['run_id']}"
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".patch", delete=False) as stream:
            stream.write(patch_text)
            patch_path = Path(stream.name)
        try:
            path = create_proposal(
                proposal_id=proposal_id,
                title=f"Evidence-reviewed candidate Claims from {state['run_id']} round {round_number}",
                run_id=state["run_id"], research_focus=goal["research_focus"],
                files=["evolution/claims/claims.jsonl"], patch_file=patch_path,
                evidence=evidence_bundle,
                related_questions=goal["research_questions"], affected_claims=[item["claim_id"] for item in new_claims],
                uncertainties=["Candidate Claims remain needs_review and require human approval.", "Paper scope and reported results must be checked against the cited source before applying."],
                impact_scope="Append evidence-backed needs_review Claim records only; does not modify existing knowledge notes.",
                source_branch="isolated-evolution-worktree", source_commit=state["base_commit"], root=self.root,
            )
        finally:
            patch_path.unlink(missing_ok=True)
        proposal = json.loads(path.read_text(encoding="utf-8"))
        errors = check_proposal(proposal, self.root)
        if errors:
            raise RuntimeError("generated draft failed Proposal safety checks: " + "; ".join(errors))
        atomic_write_json(run_dir / "proposal-reference.json", {"proposal_id": proposal_id, "path": str(path.relative_to(self.root)), "status": proposal["status"], "files": proposal["files"], "base_hashes": proposal["base_hashes"]})
        return path

    def _run_round_audit(self, run_dir: Path, state: dict[str, Any], round_number: int) -> None:
        if not self.config.get("audit", {}).get("enabled", True):
            round_data = state["rounds"].setdefault(str(round_number), {})
            round_data["audit_delta"] = {"status": "skipped", "reason": "full-worktree audit disabled for this research task"}
            save_state(run_dir, state)
            append_event(run_dir, "round_audit_skipped", {"round": round_number, "reason": "disabled_by_run_scope"})
            return
        workspace = Path(state["candidate_workspace"])
        audit_id = f"{state['run_id']}-r{round_number:02d}"
        result = self.audit_fn(root=workspace, run_id=audit_id)
        baseline_signatures = {tuple(item) for item in state.get("baseline_audit", {}).get("signatures", [])}
        new_findings = [item for item in result.get("findings", []) if _finding_signature(item) not in baseline_signatures]
        audit_dir = run_dir / f"round_{round_number:02d}" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(workspace / "evolution" / "audits" / f"{audit_id}.json", audit_dir / "audit.json")
        shutil.copy2(workspace / "evolution" / "audits" / f"{audit_id}.md", audit_dir / "audit.md")
        state["engine_generated_paths"] = sorted(set(state.get("engine_generated_paths", [])) | {f"evolution/audits/{audit_id}.json", f"evolution/audits/{audit_id}.md"})
        round_data = state["rounds"].setdefault(str(round_number), {})
        round_data["audit_delta"] = {"baseline_findings": len(baseline_signatures), "current_findings": result["finding_count"], "new_findings": len(new_findings), "new_signatures": [list(_finding_signature(item)) for item in new_findings]}
        if new_findings:
            round_data["audit_delta"]["new_finding_details"] = new_findings
            if round_data.get("evaluation", {}).get("decision") == "PASS":
                round_data["evaluation"]["decision"] = "NEEDS_REVIEW"
                round_data["evaluation"]["controller_hard_gate"] = "New deterministic audit findings are a hard regression gate."
                round_data["knowledge_gain"] = self._empty_gain(round_data.get("normalized_execution", {}), round_data["evaluation"])
        save_state(run_dir, state)
        append_event(run_dir, "round_audit_complete", {"round": round_number, "baseline": len(baseline_signatures), "current": result["finding_count"], "new": len(new_findings)})

    def _write_round_knowledge_gain(self, run_dir: Path, state: dict[str, Any], round_number: int) -> None:
        round_data = state["rounds"].get(str(round_number), {})
        gain = round_data.get("knowledge_gain", self._empty_gain(round_data.get("normalized_execution", {}), round_data.get("evaluation", {})))
        atomic_write_json(run_dir / f"round_{round_number:02d}" / "knowledge_gain.json", gain)

    def _record_runtime_reflection(self, run_dir: Path, state: dict[str, Any], error: BackendError) -> dict[str, Any]:
        kind_map = {
            "timeout": "environment_error", "network": "environment_error", "quota": "quota",
            "authentication": "quota", "permission": "permission_error", "schema": "model_error",
            "invalid_json": "model_error", "stopped": "other", "unavailable": "environment_error",
        }
        reflection_result = {
            "failure_type": kind_map.get(error.kind, "other"),
            "failure_evidence": [f"{error.task_id}: {str(error)[:500]}", f"Backend error kind: {error.kind}; retryable={error.retryable}."],
            "possible_causes": ["Codex CLI/backend returned an error before a valid structured result was checkpointed."],
            "ineffective_attempts": [f"Task attempts recorded: {state.get('rounds', {}).get(str(state.get('current_round', 1)), {}).get('stages', {}).get(error.task_id.rsplit('-', 2)[-2], {}).get('attempts', 0)}"],
            "retry_worthwhile": bool(error.retryable and calls_remaining(state, json.loads((run_dir / "goal.yaml").read_text(encoding="utf-8")) ) > 0),
            "next_step": "Retry only in a new or resumed bounded task after the specific network, authentication, quota, permission, or output-schema cause is addressed.",
            "replan": False,
            "knowledge_summary": [],
            "remaining_gaps": [],
            "feedback_refs": [],
            "reflection_backend": "deterministic runtime fallback",
        }
        round_number = int(state.get("current_round", 1))
        round_data = state.setdefault("rounds", {}).setdefault(str(round_number), {})
        round_data["runtime_reflection"] = reflection_result
        round_data.setdefault("reflection", reflection_result)
        atomic_write_json(run_dir / f"round_{round_number:02d}" / "runtime-reflection.json", reflection_result)
        save_state(run_dir, state)
        append_event(run_dir, "runtime_failure_reflected", {"round": round_number, "task_id": error.task_id, "failure_type": reflection_result["failure_type"], "reflection_backend": reflection_result["reflection_backend"]})
        return reflection_result

    def _terminate(self, run_dir: Path, state: dict[str, Any], status: str, reason: str) -> dict[str, Any]:
        if state.get("accepted_candidate_claims") and not state.get("proposal_ids"):
            try:
                proposal_path = self._create_claim_proposal(
                    run_dir, state, json.loads((run_dir / "goal.yaml").read_text(encoding="utf-8")),
                    int(state.get("current_round", 1)), state["accepted_candidate_claims"],
                )
                if proposal_path:
                    state["proposal_ids"].append(proposal_path.stem)
                    append_event(run_dir, "draft_proposal_created", {"proposal_id": proposal_path.stem, "status": "draft"})
            except Exception as exc:
                state["proposal_error"] = f"{type(exc).__name__}: {exc}"
                append_event(run_dir, "draft_proposal_generation_failed", {"type": type(exc).__name__, "message": str(exc)[:900]})
                if status == "COMPLETED":
                    status = "NEEDS_REVIEW"
                    reason = "Knowledge gain passed research evaluation but the draft Proposal did not pass deterministic safety checks."
        if state.get("status") not in TERMINAL:
            transition(run_dir, state, status, reason)
        state["terminal_reason"] = reason
        state["finished_at"] = utc_now()
        state["formal_knowledge_applied"] = False
        state["skills_modified"] = False
        state["token_usage"] = self._usage_summary(state)
        state["api_cost"] = "unavailable"
        save_state(run_dir, state)
        append_event(run_dir, "run_terminal", {"status": status, "reason": reason})
        if not state.get("experience_collection_complete"):
            try:
                state["experience_ids"] = collect_run_experience(
                    self.root, run_dir, state,
                    json.loads((run_dir / "goal.yaml").read_text(encoding="utf-8")),
                )
                state["experience_collection_complete"] = True
                save_state(run_dir, state)
                append_event(run_dir, "experience_memory_updated", {"experience_ids": state["experience_ids"]})
            except Exception as exc:
                state["experience_collection_error"] = f"{type(exc).__name__}: {str(exc)[:400]}"
                save_state(run_dir, state)
        self._write_final_report(run_dir, state)
        return state

    @staticmethod
    def _usage_summary(state: dict[str, Any]) -> Any:
        known = [item for item in state.get("model_usage", []) if isinstance(item.get("usage"), dict)]
        if not known:
            return "unavailable"
        totals: dict[str, int] = {}
        for item in known:
            for key, value in item["usage"].items():
                if isinstance(value, int):
                    totals[key] = totals.get(key, 0) + value
        return totals or "unavailable"

    def _write_final_report(self, run_dir: Path, state: dict[str, Any]) -> None:
        lines = [
            f"# Self-Evolution Run {state['run_id']}", "",
            f"- Status: `{state['status']}`", f"- Stop reason: {state.get('terminal_reason') or state.get('status_reason')}",
            f"- Backend: `{state.get('backend', {}).get('name')}`", f"- Codex version: `{state.get('backend', {}).get('version', 'unavailable')}`",
            f"- Calls started: {state.get('calls_started', 0)} / {json.loads((run_dir / 'goal.yaml').read_text())['budgets']['max_model_calls']}",
            f"- Token usage: `{state.get('token_usage', 'unavailable')}`", f"- API cost: `{state.get('api_cost', 'unavailable')}`",
            f"- Formal knowledge applied: `{state.get('formal_knowledge_applied')}`", f"- Skills modified: `{state.get('skills_modified')}`", "",
            f"- Experience Memory references: `{', '.join(state.get('experience_ids', [])) or 'none'}`", "",
            "## Discovery", "", json.dumps(state.get("discovery", {}), ensure_ascii=False, indent=2), "",
            "## Rounds", "",
        ]
        for key in sorted(state.get("rounds", {}), key=lambda value: int(value)):
            item = state["rounds"][key]
            lines.extend([f"### Round {int(key)}", "", f"- Plan: {item.get('plan', {}).get('research_question', 'not selected')}", f"- Feedback-driven: {item.get('feedback_driven_plan', False)}", f"- Round status: {item.get('status', 'incomplete')}", f"- Accepted candidate Claims: {len(item.get('knowledge_gain', {}).get('accepted_findings', []))}", f"- Proposal: `{item.get('proposal_id', 'none')}`", ""])
            if item.get("plan"):
                lines.extend(["Planner rationale: " + item["plan"].get("rationale", ""), ""])
            if item.get("evaluation"):
                lines.extend(["Evaluator rationale: " + item["evaluation"].get("rationale", ""), ""])
            if item.get("audit_delta"):
                if item["audit_delta"].get("status") == "skipped":
                    lines.extend(["Audit status: skipped by scoped-run configuration; no full-worktree audit result is claimed.", ""])
                else:
                    lines.extend([f"Audit delta: {item['audit_delta'].get('new_findings', 0)} new findings from historical baseline ({item['audit_delta'].get('current_findings', 'n/a')} total current).", ""])
        lines.extend(["## Proposal boundary", "", "Every generated Proposal is a draft and requires explicit review. The controller does not apply, commit, or push knowledge updates.", ""])
        atomic_write_text(run_dir / "final-report.md", "\n".join(lines))
