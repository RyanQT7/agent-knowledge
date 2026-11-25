from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from scripts.evolution.common import atomic_write_json, file_lock, read_json, utc_now


TERMINAL = {"COMPLETED", "NO_UPDATE_NEEDED", "NO_PROGRESS", "NEEDS_REVIEW", "BLOCKED", "BUDGET_EXHAUSTED", "FAILED", "INTERRUPTED"}
TRANSITIONS = {
    "PENDING": {"PLANNING", "BLOCKED", "INTERRUPTED", "FAILED"},
    "PLANNING": {"RUNNING", "REFLECTING", "COMPLETED", "NO_UPDATE_NEEDED", "NEEDS_REVIEW", "BUDGET_EXHAUSTED", "BLOCKED", "INTERRUPTED", "FAILED"},
    "RUNNING": {"EVALUATING", "REFLECTING", "BUDGET_EXHAUSTED", "BLOCKED", "INTERRUPTED", "FAILED"},
    "EVALUATING": {"REFLECTING", "PLANNING", "COMPLETED", "NO_UPDATE_NEEDED", "NO_PROGRESS", "NEEDS_REVIEW", "BUDGET_EXHAUSTED", "BLOCKED", "INTERRUPTED", "FAILED"},
    "REFLECTING": {"RETRYING", "PLANNING", "EVALUATING", "NEEDS_REVIEW", "BUDGET_EXHAUSTED", "BLOCKED", "INTERRUPTED", "FAILED"},
    "RETRYING": {"RUNNING", "EVALUATING", "REFLECTING", "NEEDS_REVIEW", "BUDGET_EXHAUSTED", "BLOCKED", "INTERRUPTED", "FAILED"},
    "INTERRUPTED": {"PLANNING", "RUNNING", "EVALUATING", "REFLECTING", "RETRYING", "BUDGET_EXHAUSTED", "BLOCKED", "FAILED"},
    "NO_UPDATE_NEEDED": set(), "NO_PROGRESS": set(), "COMPLETED": set(), "NEEDS_REVIEW": set(),
    "BLOCKED": set(), "BUDGET_EXHAUSTED": set(), "FAILED": {"PLANNING"},
}


def safe_run_dir(root: Path, run_id: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{2,100}", run_id):
        raise ValueError("run ID contains unsafe characters")
    runs_path = root / "evolution" / "runs"
    if runs_path.is_symlink():
        raise ValueError("evolution/runs cannot be a symlink")
    runs = runs_path.resolve()
    path = runs / run_id
    if path.is_symlink() or path.resolve().parent != runs:
        raise ValueError("run path must be a direct, non-symlink child of evolution/runs")
    return path


def append_event(run_dir: Path, event_type: str, details: dict[str, Any] | None = None) -> None:
    event = {"at": utc_now(), "type": event_type, "details": details or {}}
    path = run_dir / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(run_dir / ".events.lock"):
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
            stream.flush()


def load_state(run_dir: Path) -> dict[str, Any]:
    state = read_json(run_dir / "state.json", None)
    if not isinstance(state, dict):
        raise FileNotFoundError(f"missing or invalid state in {run_dir}")
    return state


def save_state(run_dir: Path, state: dict[str, Any]) -> None:
    atomic_write_json(run_dir / "state.json", state)
    atomic_write_json(run_dir / "manifest.json", state)


def transition(run_dir: Path, state: dict[str, Any], new_status: str, reason: str) -> None:
    old_status = state["status"]
    if new_status == old_status:
        state["status_reason"] = reason
        save_state(run_dir, state)
        append_event(run_dir, "state_reason_updated", {"status": new_status, "reason": reason})
        return
    if new_status not in TRANSITIONS.get(old_status, set()):
        raise ValueError(f"invalid state transition {old_status} -> {new_status}")
    state["status"] = new_status
    state["status_reason"] = reason
    state["updated_at"] = utc_now()
    save_state(run_dir, state)
    append_event(run_dir, "state_transition", {"from": old_status, "to": new_status, "reason": reason})


def request_stop(run_dir: Path) -> dict[str, Any]:
    state = load_state(run_dir)
    if state.get("status") in TERMINAL:
        return state
    state["stop_requested"] = True
    state["updated_at"] = utc_now()
    atomic_write_json(run_dir / "stop-requested.json", {"at": state["updated_at"], "run_id": state.get("run_id")})
    save_state(run_dir, state)
    append_event(run_dir, "stop_requested", {"status": state.get("status")})
    return state


def is_stop_requested(run_dir: Path) -> bool:
    if (run_dir / "stop-requested.json").exists():
        return True
    try:
        return bool(load_state(run_dir).get("stop_requested"))
    except (OSError, ValueError):
        return False
