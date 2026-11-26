# Evolution Engine (Phase 1.5)

`scripts/evolution/evolve.py` is the independent process entrypoint. Python owns the state machine, budgets, source and path checks, retry caps, checkpoints, candidate workspace and approval boundary. The model backend supplies only schema-validated role outputs.

## Components

- `engine/controller.py`: versioned Goal, baseline audit, discovery handoff, round orchestration, scope checks, knowledge-gain accounting, and draft Proposal creation.
- `engine/planner.py`: bounded next-task prompt and validation against the immutable Goal and exact prior-round feedback IDs.
- `engine/executor.py`: source-grounded analysis, attempt-specific artifacts, merged evidence/read history, and temporary Finding links.
- `engine/evaluator.py`: deterministic identity/date/locator/permission checks plus a separate independent LLM Judge prompt.
- `engine/reflector.py`: concise knowledge/gap summary and failure diagnosis for bounded retry or replan.
- `engine/memory.py`: current questions, Claims, pending proposals, Phase 1 report, candidate queue, prior-round evaluations, gains, and unresolved questions.
- `engine/state.py`: state transition table, atomic manifest updates, events, cooperative stop, and safe run-path validation.
- `engine/termination.py`: shared call/read budgets, acceptance criteria, and no-progress stop.
- `backends/base.py`: replaceable `BackendRequest` / `BackendResponse` interface.
- `backends/codex_cli.py`: authenticated Codex CLI subprocess adapter using ephemeral `codex exec --json`, schema file, output file, explicit read-only or workspace-write sandbox, bounded timeouts, private task logs, and a Python-enforced per-task web-search cap. It detects whether the installed CLI accepts a `--search` switch; CLI 0.172.0 does not, although this environment still exposed its web-search tool during the real run.
- `backends/mock_backend.py`: deterministic test backend; do not use it as a source of research claims.

## State and roles

The controller drives `PENDING → PLANNING → RUNNING → EVALUATING` and, when needed, `REFLECTING → RETRYING` or a new outer planning round. Terminal outcomes distinguish `COMPLETED`, `NO_UPDATE_NEEDED`, `NO_PROGRESS`, `NEEDS_REVIEW`, `BLOCKED`, `BUDGET_EXHAUSTED`, `INTERRUPTED`, and `FAILED`. A limit stop is not reported as goal completion.

Planner, Evaluator, and Reflector receive `read-only`; Executor gets `workspace-write` in a detached worktree based on the frozen starting commit. Each Executor attempt writes a unique Markdown artifact; the Python controller merges Findings and source read extents while retaining each artifact separately. Temporary Finding references use `related_finding_ids`; `related_claim_ids` accepts only IDs in the Claim store. Out-of-scope workspace changes, changed worktree HEAD, invalid artifacts, permission violations, budget violations, and new deterministic audit regressions remain batch-wide gates. Source identity/version, locator, and reference failures are attached to individual Findings; invalid Findings are excluded while valid siblings remain eligible for independent Judge review. The Judge evaluates only the current round; the Controller checks run-level acceptance after later planning. The Judge cannot override a deterministic hard gate.

The accepted research findings are still candidate Claims. The controller writes one draft Proposal only after accepted findings pass evidence checks; it does not append them to `claims.jsonl` or modify the formal knowledge base. Proposals require a separate user action through the Phase 1 Proposal tools. Skill and Lesson changes, automatic application, commit, push, training, and scheduling are disabled.

## Checkpoints and recovery

Each run freezes `goal.yaml`, `engine-config.yaml`, and the starting commit. `state.json` and `manifest.json` are atomically replaced; every major state change is appended to `events.jsonl`. Each model role has a unique task ID and private prompt / CLI event / stderr / response files. Completed outputs are schema-checked and reused after interruption. The controller lock prevents concurrent writers. A run whose frozen Goal/config or base commit changed is blocked rather than silently replanned under new permissions.

Use `python3 scripts/evolution/evolve.py status [RUN_ID]`, `stop RUN_ID`, or `resume RUN_ID`. A stop request kills a live CLI process group cooperatively. An `INTERRUPTED` run resumes its unfinished stage; an explicit `resume` on `FAILED` retries only the failed stage within the original call and attempt budgets while reusing completed checkpoints. `NEEDS_REVIEW`, `BLOCKED`, and other terminal outcomes are not silently resumed. A model task timeout, CLI authentication/quota problem, network failure, invalid schema/JSON, and permission violation are recorded with distinct failure types. Retryable calls consume the same global call budget; no unbounded retry is allowed.

## Backend settings and budgets

Defaults live in `evolution/config/engine.yaml`. `backend.model: null` delegates model selection to the installed Codex CLI configuration; no model identifier is hard-coded. CLI `--model` and `--reasoning-effort` override the run snapshot only at run creation. Planner and Judge use separate ephemeral processes with no conversation history; each task has a unique output schema, task directory, and response file. Actual usage is stored if the CLI emits token counts; otherwise it is `unavailable`.

The Python controller enforces the configured hard ceilings: 3 rounds, 12 model calls across Planner / Executor / Evaluator / Reflector and retries, 2 retries per task, 2 no-gain rounds, 20 screened candidates per round, 2 full reads, 4 web-search tool calls per Executor and 2 per Evaluator, one model process at a time, and a 3600-second run cap. Role-specific timeouts are 180 seconds for Planner, 600 for Executor, 420 for Evaluator, and 150 for Reflector. Before starting an Executor attempt, the Controller reserves calls for evaluation, possible reflection, and the next Planner. Context passed to each role is bounded; the Judge receives compact relevant knowledge and evidence excerpts, not the full Phase 1 memory. Per-run overrides can reduce round and call ceilings, not increase them. There is no scheduler.

## Running and reviewing

```bash
python3 scripts/evolution/evolve.py run --focus "Agent Memory and Self-Evolving Agents"
python3 scripts/evolution/evolve.py status
python3 scripts/evolution/evolve.py resume <RUN_ID>
```

After completion, read `final-report.md`, `round_*/knowledge_gain.json`, `round_*/evaluation.json` (or role stage results), source task outputs, raw evidence and any Proposal reference. A draft Proposal is a review request only. Inspect and approve/reject it explicitly; apply only after the Proposal hash check passes and the user approves that exact diff. If target file hashes changed, regenerate and re-review. Use `git revert` to undo an approved committed patch. Mock outputs and unit-test fixtures are never evidence.
