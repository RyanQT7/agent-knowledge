# Cloud-OpsBench — Source-Code Reading Notes

Paper: [Freezing the Crime Scene: A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation](../../../papers/aiops/cloud-opsbench/notes.md)

## Repository Identity

- Repository: [LLM4Ops/Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench)
- Official status: Likely Official
- Evidence: The README identifies the exact benchmark/state-snapshot project; direct author ownership was not fully established in the local paper note.
- Local path: `sources/code/aiops/cloud-opsbench/Cloud-OpsBench`
- Read at commit: `54bcec7c7faba390549bda833c175178a7513812`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

Cloud-OpsBench packages frozen fault snapshots, Kubernetes-like diagnostic
tools, a single-agent ReAct harness, a Skill-free baseline, a Skill-aware
variant, and trajectory/evidence evaluators. The README describes two
microservice systems, 57 fault types, and 754 cases. The repository is a
replayable benchmark environment, not a live production cluster.

## 2. Repository Architecture

```text
fault snapshot + metadata
        ↓
case state / context builder
        ↓
OpenAI-compatible LLM emits Thought + one Action
        ↓
snapshot-backed tool executor
        ↓
observation / error
        ↓
full case history in next prompt
        ↓
Submit structured Top-3 diagnosis
        ↓
golden trajectory / process-label evaluation
```

The `cloudops_skill_agent` adds symptom selection and on-demand diagnostic
graph skills; both agent variants maintain their own runtime/tools/evaluator.

## 3. Entry Points

- `agents/cloudops_agent/run.py` loads config, resolves cases, and runs the baseline.
- `agents/cloudops_agent/harness/harness.py:CloudOpsHarness` implements the loop.
- `agents/cloudops_agent/harness/context.py:ContextBuilder` builds prompts from full history.
- `agents/cloudops_agent/runtime/core.py` defines `CaseState`, `StepRecord`, parser, executor, and trace logger.
- `agents/cloudops_agent/tools/cloudops.py` and `snapshot.py` implement snapshot-backed tools.
- `agents/cloudops_skill_agent/runtime/skills.py` loads diagnostic graph skills.
- `interact.py` exposes manual repeated tool use and diagnosis submission.

## 4. Main Execution Flow

`CloudOpsHarness.run_case` repeatedly builds a prompt, calls `ModelRunner`,
parses exactly one text action, executes it, appends a `StepRecord`, and saves
the state. `Submit` is accepted only when its JSON has a non-empty evidence
summary and exactly three predictions. A step budget ends an unfinished case.
The state snapshot is read by tools rather than changed by a live cluster.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Frozen environment | benchmark snapshots; `tools/snapshot.py` | Read case JSON/YAML and emulate resource queries | No live cluster was used by the inspected runtime. |
| ReAct baseline | `harness/harness.py:CloudOpsHarness` | One Thought/Action per iteration, observation appended | Bounded runtime interaction. |
| LLM runner | `runtime/llm.py:ModelRunner` | OpenAI-compatible chat completion | Requires external API; not called here. |
| Tool execution | `runtime/core.py:ToolExecutor`, `tools/cloudops.py` | Registry dispatch, schema/signature filtering, string observation/error | Tools are diagnostic/read-oriented in the inspected set. |
| Structured diagnosis | `runtime/contracts.py:build_expected_output` | Fixed root-cause list, target kind/name, Top-3 predictions | Candidate universe is benchmark-defined and closed. |
| Skill variant | `cloudops_skill_agent/runtime/skills.py` | Loads symptom-specific Diagnostic Graph Skill | It adds graph guidance, not automatically a new planner. |
| Evaluation | `evaluation_utils/schema.py`, `matcher.py`, `evaluator.py` | Process labels, admissible tool/evidence patterns, trajectory matching | Evaluates interaction evidence, not a live repair outcome. |

## 6. Core Modules

- `runtime/core.py`: state, output parsing, tool execution, trace logging.
- `harness/context.py` and `harness/harness.py`: prompt/history and loop.
- `tools/`: snapshot/Kubernetes-like query functions.
- `runtime/contracts.py`: valid nodes/services/namespaces and diagnosis contract.
- `evaluation_utils/`: evidence-pattern and golden-trajectory evaluation.
- `cloudops_skill_agent/`: Skill-enabled parallel implementation.

## 7. Important Classes / Functions

- `CaseState.to_dict`, `StepRecord.to_dict`, and `OutputParser.parse`.
- `CloudOpsHarness.run_case` and `_run_step`.
- `ToolExecutor.execute`.
- `ContextBuilder.build` and `_history`.
- `build_expected_output` and `OutputParser.validate_submit_payload`.
- `CaseAnnotation`, `Milestone`, and evidence-pattern matching.

## 8. Data Flow

```text
case metadata / snapshot
  → CaseState
  → prompt with tools, output contract, and prior steps
  → LLM action
  → snapshot query
  → observation/error
  → StepRecord and JSON trace
  → structured Submit
```

The trace records prompt, raw model output, action, parameters, observation,
latencies, and token counts. It does not require every observation to carry a
separate source/entity/timestamp/provenance ticket, although the case path and
tool name are available in the trace.

## 9. LLM Usage

The LLM chooses the next diagnostic action and final structured diagnosis.
Current knowledge-base classification: **bounded single-agent ReAct
benchmark**. The Skill variant has explicit symptom/graph guidance, but the
code remains one runtime harness rather than a multi-agent system.

## 10. Prompt Design

`ContextBuilder` includes a system prompt, available tools, final-output
contract, previous steps, current question, and step budget. `OutputParser`
accepts Thought/Action/Action Input text and validates JSON. This is a clear
tool/action protocol, but output correctness is separate from diagnosis truth.

## 11. Tool System

Tools model Kubernetes resource lists/descriptions, app YAML, logs, service
connectivity, source-code access, and node/system status. The inspected tools
read frozen snapshot data; they do not issue real cluster mutations. The
manual `interact.py` path permits repeated calls but still uses snapshot data.

## 12. Planning / Orchestration

The baseline is runtime ReAct: one next action per step from current history.
The Skill variant can load symptom-specific graph guidance and select a
symptom, but a free-form explicit Planner is not exposed. A step budget and
parser/retry behavior provide orchestration constraints.

## 13. Memory / Context

Full per-case history is retained in `CaseState.history` and the next prompt.
This is working trajectory context, not cross-case persistent memory. The
benchmark's frozen snapshot is environment state, not Agent memory.

## 14. Retrieval / RAG

Resource/log/source queries are tools over snapshot data. The Skill variant
loads diagnostic graph YAML. Neither should be automatically described as
RAG or long-term memory.

## 15. Graph / Topology / Algorithms

The benchmark models Kubernetes service/node/resource relationships and its
Skill variant loads diagnostic graphs. The inspected code does not establish
a physical network topology or a causal graph; the root-cause contract is
primarily a closed list of causes and target objects.

## 16. Verification

Evaluation matches tool calls and observations against admissible evidence
patterns and milestone formulas. `Submit` validates shape and labels, not
whether a live system recovered. There is no repair execution or recovery
verification in the inspected benchmark runtime.

## 17. Evaluation

The repository evaluates final Top-3 diagnosis and trajectory/process-label
behavior. `StepRecord` captures step count, model/tool latency, and token
metadata, enabling cost/interaction analysis. Because tools operate on frozen
snapshots, task success is reproducible but does not equal production safety.

## 18. Configuration

YAML model/diagnosis configuration specifies provider, API base/key, system,
fault category, dataset root, save root, and iteration budget. No config with
credentials was read and no API call was made.

## 19. Deterministic vs LLM Components

- Deterministic: snapshot queries, tool schemas/dispatch, action parsing, output validation, state/history logging, and evidence-pattern evaluation.
- LLM: next-action selection and diagnosis content.
- Benchmark control: fixed cases, fault labels, budgets, and golden trajectories.

## 20. Paper vs Code Differences

The benchmark makes Agent interaction measurable, but its tools and systems
are replay/snapshot abstractions rather than live operational surfaces. The
closed root-cause/resource lists and strict `Submit` contract also limit direct
claims about open-set Network RCA or autonomous remediation.

## 21. Reproducibility

Reproducibility is **High-Medium** for static benchmark execution structure:
cases, contracts, tools, and evaluators are visible. Actual agent runs still
need a compatible model endpoint and dependencies; none were run here.

## 22. What I Learned from the Code

Cloud-OpsBench turns “Agent capability” into observable events: selected tool,
arguments, returned observation, step budget, and final contract. This is a
strong template for Network Agent evaluation, provided live/controlled
telemetry and safety outcomes are added rather than inferred from text traces.

## 23. Open Questions

- How should a Network version expose physical topology, syslog, NetFlow, and configuration with equivalent admissible evidence patterns?
- How should the benchmark represent unknown and multi-root causes outside its fixed lists?
- What recovery signal should supplement final diagnosis and trajectory matching?

## Paper ↔ Code

Paper notes: [Cloud-OpsBench paper notes](../../../papers/aiops/cloud-opsbench/notes.md)

