from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.evolution.backends.codex_cli import CodexCliBackend
from scripts.evolution.backends.mock_backend import MockBackend, build_smoke_backend
from scripts.evolution.common import read_json
from scripts.evolution.engine.controller import EvolutionController, build_goal, load_engine_config
from scripts.evolution.engine.state import load_state, request_stop, safe_run_dir


def _backend(config: dict[str, Any], kind: str | None = None, scenario: str | None = None):
    backend_type = kind or config.get("backend", {}).get("type", "codex-cli")
    if backend_type == "mock":
        if scenario == "smoke":
            return build_smoke_backend()
        return MockBackend()
    if backend_type != "codex-cli":
        raise ValueError(f"unsupported backend type: {backend_type}")
    settings = config["backend"]
    return CodexCliBackend(
        executable=settings.get("executable", "codex"),
        model=settings.get("model"),
        reasoning_effort=settings.get("reasoning_effort"),
        search=bool(settings.get("search", True)),
    )


def _exit_code(status: str) -> int:
    if status in {"COMPLETED", "NO_UPDATE_NEEDED", "NO_PROGRESS"}:
        return 0
    if status in {"NEEDS_REVIEW", "BLOCKED", "BUDGET_EXHAUSTED", "INTERRUPTED"}:
        return 2
    return 3


def _print_summary(state: dict[str, Any], run_dir: Path) -> None:
    print(json.dumps({
        "run_id": state.get("run_id"),
        "status": state.get("status"),
        "terminal_reason": state.get("terminal_reason"),
        "calls_started": state.get("calls_started"),
        "rounds": len([item for item in state.get("rounds", {}).values() if item.get("status") in {"evaluated", "needs_review", "replan_requested"}]),
        "proposal_ids": state.get("proposal_ids", []),
        "report": str(run_dir / "final-report.md"),
    }, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a bounded, checkpointed Self-Evolution Engine as an independent Python process.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2], help="knowledge base root (defaults to this checkout)")
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="start a new evolution run")
    run.add_argument("--backend", choices=("codex-cli", "mock"), default=None)
    run.add_argument("--scenario", choices=("smoke",), help="deterministic test scenario; not research evidence")
    run.add_argument("--focus", default=None, help="research theme; omit to select a topic from existing knowledge gaps")
    run.add_argument("--max-rounds", type=int)
    run.add_argument("--max-model-calls", type=int)
    run.add_argument("--model")
    run.add_argument("--reasoning-effort", choices=("low", "medium", "high", "xhigh"))
    run.add_argument("--run-id")
    run.add_argument("--no-discovery", action="store_true", help="disable fresh provider discovery; useful for isolated tests")
    resume = commands.add_parser("resume", help="resume an interrupted run or explicitly retry a failed stage from completed checkpoints")
    resume.add_argument("run_id")
    resume.add_argument("--backend", choices=("codex-cli", "mock"), default=None)
    resume.add_argument("--scenario", choices=("smoke",))
    status = commands.add_parser("status", help="show one run or list runs")
    status.add_argument("run_id", nargs="?")
    stop = commands.add_parser("stop", help="request a cooperative stop at the next safe checkpoint")
    stop.add_argument("run_id")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.command == "status":
            runs = root / "evolution" / "runs"
            if args.run_id:
                run_dir = safe_run_dir(root, args.run_id)
                state = load_state(run_dir)
                _print_summary(state, run_dir)
            else:
                result = []
                for path in sorted(runs.iterdir()):
                    if path.is_dir() and (path / "state.json").is_file():
                        state = load_state(path)
                        result.append({"run_id": state.get("run_id"), "status": state.get("status"), "calls_started": state.get("calls_started"), "terminal_reason": state.get("terminal_reason")})
                print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "stop":
            run_dir = safe_run_dir(root, args.run_id)
            state = request_stop(run_dir)
            print(json.dumps({"run_id": args.run_id, "status": state.get("status"), "stop_requested": state.get("stop_requested")}, ensure_ascii=False))
            return 0
        if args.command == "run":
            config = load_engine_config(root)
            if args.backend:
                config["backend"]["type"] = args.backend
            if args.model:
                config["backend"]["model"] = args.model
            if args.reasoning_effort:
                config["backend"]["reasoning_effort"] = args.reasoning_effort
            if args.no_discovery:
                config["discovery"]["enabled"] = False
            if args.scenario and config["backend"]["type"] != "mock":
                raise ValueError("--scenario is only valid with --backend mock")
            goal = build_goal(config, args.max_rounds, args.max_model_calls, args.focus, root=root)
            backend = _backend(config, scenario=args.scenario)
            controller = EvolutionController(backend, root=root, config=config)
            run_dir = controller.create_run(goal, run_id=args.run_id)
            state = controller.execute(run_dir)
            _print_summary(state, run_dir)
            return _exit_code(state.get("status", "FAILED"))
        run_dir = safe_run_dir(root, args.run_id)
        state = load_state(run_dir)
        config = json.loads((run_dir / "engine-config.yaml").read_text(encoding="utf-8"))
        if args.backend and args.backend != config.get("backend", {}).get("type"):
            raise ValueError("backend cannot be changed while resuming a versioned run")
        backend = _backend(config, scenario=args.scenario)
        controller = EvolutionController(backend, root=root, config=config)
        final_state = controller.resume(args.run_id)
        _print_summary(final_state, run_dir)
        return _exit_code(final_state.get("status", "FAILED"))
    except KeyboardInterrupt:
        print("Controller interrupted; use `resume <RUN_ID>` to continue checkpointed stages.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(json.dumps({"error": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
