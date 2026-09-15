# ReWOO — Source-Code Reading Notes

Paper: [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](../../papers/rewoo/notes.md)

## Repository Identity

- Repository: [billxbf/ReWOO](https://github.com/billxbf/ReWOO)
- Official status: Confirmed Official
- Evidence: The local paper note provides the repository URL.
- Local path: `sources/code/agent/rewoo/ReWOO`
- Read at commit: `9cd0283043ff4be0c9d614fda2789d143ca6ffd1`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

The repository implements the Plan–Worker–Solver (PWS) pattern. A Planner LLM
creates a plan with evidence variables (`#E1`, `#E2`, …), Workers execute the
selected tools and fill those variables, and a Solver LLM receives the worker
log to produce the answer.

## 2. Repository Architecture

```text
input
  ↓
Planner LLM: plan + evidence calls
  ↓
sequential Worker execution
  ↓
worker log / evidence variables
  ↓
Solver LLM
  ↓
answer
```

The central implementation is `algos/PWS.py`; `app.py` provides a Gradio
entrypoint and `run.py` provides a CLI path with external API-key files.

## 3. Entry Points

- `algos/PWS.py:PWS.run` is the main pipeline.
- `nodes/Planner.py:Planner.run` sends the planning prompt and parses the output.
- `nodes/Worker.py` defines the worker registry and tool-backed workers.
- `nodes/Solver.py:Solver.run` creates the final answer from the input and worker log.

## 4. Main Execution Flow

`PWS.run` resets per-run evidence state, calls the Planner, parses plan lines
and evidence assignments, executes workers in order, substitutes prior
evidence variables where available, and calls the Solver with the resulting
worker log. The result records planner/worker/solver logs, number of steps,
tool usage, and estimated token/tool cost (`algos/PWS.py:29-69`).

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Planner | `nodes/Planner.py`; `algos/PWS.py:PWS.run` | LLM emits plan lines and `#E` assignments | Plan generation is a separate stage. |
| Worker | `nodes/Worker.py:WORKER_REGISTRY` | Google, Wikipedia, lookup, calculator, LLM, and document-search workers | Some workers wrap external APIs or LangChain components. |
| Evidence variable | `PWS._parse_planner_evidences`, `_get_worker_evidences` | Maps `#E` names to tool output | Substitution follows parsed insertion order. |
| Solver | `nodes/Solver.py` | LLM consumes original input plus worker log | It does not call tools in the inspected path. |
| Cost accounting | `PWS.run` | Counts calls/tokens/tool costs | This is instrumentation, not correctness verification. |

## 6. Core Modules

- `algos/PWS.py`: orchestration, parsing, worker execution, and cost accounting.
- `nodes/Planner.py`: planner prompt and output.
- `nodes/Worker.py`: worker implementations and registry.
- `nodes/Solver.py`: final synthesis prompt.
- `prompts/`: planner/solver few-shot prompt material.

## 7. Important Classes / Functions

- `PWS.run`.
- `PWS._parse_plans`, `PWS._parse_planner_evidences`, and `PWS._get_worker_evidences`.
- `Planner.run`, `Worker.run` implementations, and `Solver.run`.

## 8. Data Flow

```text
question
  → plan lines: Plan: ...
  → evidence assignments: #E1 = Tool[input]
  → worker output
  → later #E variables (when substituted)
  → worker log
  → Solver prompt
  → final response
```

## 9. LLM Usage

The Planner and Solver are LLM nodes; `LLMWorker` can add another LLM call as
an evidence-producing worker. Other workers call search, calculation, or
document retrieval systems. The implementation therefore separates planning
and synthesis from execution, but the amount of LLM involvement depends on
the selected worker set.

## 10. Prompt Design

The Planner prompt lists available worker names/descriptions and expects a
specific textual plan/evidence format. The Solver prompt receives the worker
log rather than the Planner's reasoning alone. This creates an explicit
interface between planning and execution.

## 11. Tool System

`WORKER_REGISTRY` contains Google, Wikipedia, lookup, WolframAlpha, Calculator,
LLM, and search-document workers. Workers return strings that are inserted
into evidence variables. The code does not impose a typed observation schema
or provenance fields on those strings.

## 12. Planning / Orchestration

This is plan-first orchestration: the Planner emits the tool plan before the
Workers run. `PWS.run` then executes the parsed plan sequentially. The
inspected path does not perform observation-interleaved replanning, so it is
not equivalent to a ReAct loop even though both can call external tools.

## 13. Memory / Context

`worker_evidences` and `worker_log` are run-local context. `PWS.run` explicitly
resets evidence state, so the core pipeline is stateless across runs. No
persistent memory subsystem was found.

## 14. Retrieval / RAG

Some workers use search or a vector-backed document store (`SearchSOTUWorker`),
but this is a worker capability. It should not be read as an Agent memory
system. Retrieval output is placed into the current worker log.

## 15. Graph / Topology / Algorithms

Not applicable in the inspected ReWOO application. The main structure is a
linear parsed plan with evidence dependencies, not a topology or causal graph.

## 16. Verification

The code records outputs and costs but no independent verifier for worker
evidence or final solver claims was found. A failed/empty worker result can
become “No evidence found” and still flow to the Solver.

## 17. Evaluation

The repository exposes task runners and cost/tool-use accounting. Exact
benchmark details are task-specific and were not rerun. Token and tool costs
are useful operational measurements, not proof of answer correctness.

## 18. Configuration

CLI/app configuration, prompt files, and API keys under an expected `keys/`
location configure execution. No key files were present/read and no external
call was made.

## 19. Deterministic vs LLM Components

- Deterministic: plan parsing, variable substitution, worker dispatch, log assembly, and counters.
- LLM: Planner, Solver, and optional LLM worker.
- External effects: search/API/document worker calls when run.

## 20. Paper vs Code Differences

The repository is a compact original implementation and README points to a
later Gentopia implementation elsewhere. The observed PWS path is a static
plan followed by sequential workers; it does not demonstrate dynamic
replanning after each observation. Variable substitution also depends on
previous evidence being available in iteration order, an implementation
constraint not equivalent to a general dependency scheduler.

## 21. Reproducibility

Reproducibility is **Medium-Low**: the core classes and prompts are visible,
but several workers require external APIs/LangChain integrations and model
credentials. No execution was attempted.

## 22. What I Learned from the Code

“Decoupling reasoning from observation” becomes a concrete interface: the
Planner creates symbolic evidence references, Workers populate them, and the
Solver sees a consolidated log. This improves call organization, but the
fixed plan also means that a bad early query is not automatically corrected by
new observations.

## 23. Open Questions

- How are dependency references validated when a plan uses an evidence variable before it is produced?
- What is the behavior of the newer implementation mentioned in the README?
- How would provenance and verification be added without collapsing the Planner–Worker separation?

## Paper ↔ Code

Paper notes: [ReWOO paper notes](../../papers/rewoo/notes.md)

