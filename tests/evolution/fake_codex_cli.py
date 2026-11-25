"""Deterministic fake codex executable used only by Evolution Engine tests."""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

args = sys.argv[1:]
if args == ["--version"]:
    print("codex-cli fake-test")
    raise SystemExit(0)
if args[:2] == ["login", "status"]:
    print("Logged in using ChatGPT")
    raise SystemExit(0)
if args[:2] == ["exec", "--help"]:
    print("--ephemeral --json --output-schema --output-last-message --sandbox")
    raise SystemExit(0)
if os.environ.get("EVOLUTION_FAKE_CODEX_MODE") == "timeout":
    time.sleep(5)
    raise SystemExit(1)
if os.environ.get("EVOLUTION_FAKE_CODEX_MODE") == "search-flood":
    for index in range(3):
        print(json.dumps({"type":"item.started", "item":{"type":"web_search", "id":f"search-{index}"}}), flush=True)
    time.sleep(5)
    raise SystemExit(1)

schema_path = Path(args[args.index("--output-schema") + 1])
message_path = Path(args[args.index("--output-last-message") + 1])
task_id = message_path.parent.name
round_match = re.search(r"-r(\d+)-", task_id)
round_number = int(round_match.group(1)) if round_match else 1
required = set(json.loads(schema_path.read_text(encoding="utf-8"))["required"])
if "candidate_ids" in required:
    role = "planner"
elif "papers" in required:
    role = "executor"
elif "criteria" in required:
    role = "evaluator"
else:
    role = "reflector"

catalog = json.loads(Path(os.environ["EVOLUTION_FAKE_CODEX_CATALOG"]).read_text(encoding="utf-8"))
if role == "planner":
    result = catalog["planner"][min(round_number - 1, len(catalog["planner"]) - 1)]
elif role == "executor":
    prompt = sys.stdin.read()
    marker = "Candidate artifact path:\n"
    artifact_path = prompt.split(marker, 1)[1].splitlines()[0].strip()
    result = dict(catalog["executor"])
    result["artifact_path"] = artifact_path
    target = Path(args[args.index("--cd") + 1]) / artifact_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("# Fixture memo\n\nFake CLI integration output only; this is not research evidence.\n", encoding="utf-8")
else:
    result = catalog[role]

log_path = os.environ.get("EVOLUTION_FAKE_CODEX_LOG")
if log_path:
    entry = {"role": role, "task_id": task_id, "sandbox": args[args.index("--sandbox") + 1], "ephemeral": "--ephemeral" in args, "search_flag": "--search" in args}
    with Path(log_path).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(entry) + "\n")
message_path.write_text(json.dumps(result), encoding="utf-8")
print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 2, "total_tokens": 5}}))
