# RCAgentBench — Source-Code Reading Notes

Paper: [RCAgentBench: An Agent-Oriented Benchmark for Multimodal Root Cause Analysis in Microservices](../../../papers/aiops/rcagentbench/notes.md)

## Repository Identity

- Repository: [CSTCloudOps/RCAgentBench](https://github.com/CSTCloudOps/RCAgentBench)
- Official status: Confirmed Official
- Evidence: The local paper note provides the repository URL.
- Local path: `sources/code/aiops/rcagentbench/RCAgentBench`
- Read at commit: `ab14bba1948202416535803825e1d58cfab391bd`
- Branch: `main`
- License: No top-level `LICENSE` was observed in the clone.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

RCAgentBench contains multimodal microservice-RCA data/tool adapters and
several LLM-agent variants. The inspected `workflow.py` provides a three-phase
workflow: understand the incident and time range, collect evidence through a
LlamaIndex ReAct agent, then ask an LLM for a structured component diagnosis.
The repository also contains direct ReAct, plan/execute, reflection, and
workflow-style runners.

## 2. Repository Architecture

```text
fault description / UUID
        ↓
LLM extracts time window and initial analysis
        ↓
ReActAgent calls metric / log / trace / system tools
        ↓
evidence text and reasoning trace
        ↓
LLM emits component candidates and reason
        ↓
JSONL result / benchmark evaluation
```

## 3. Entry Points

- `run.py` selects agent variants and processes benchmark records.
- `agents/workflow.py:RCAWorkflow` is the clearest event-driven implementation.
- `agents/base.py` initializes LLMs, tools, system context, and common runners.
- `tools/agent_tools.py` exposes metric, log, trace, and related diagnostic tools.
- `tools/multimodal_data.py` contains time parsing, metric mapping, anomaly detection, and data access.

## 4. Main Execution Flow

`RCAWorkflow.phase1_understand` asks the LLM to extract `START_TIME`,
`END_TIME`, and an analysis. `phase2_collect_evidence` instantiates a
`ReActAgent` with `STANDARD_TOOLS`, streams tool-call events, and records a
short reasoning trace. `phase3_analyze` sends the collected evidence to a
second LLM call and parses a JSON result containing component candidates and a
reason (`agents/workflow.py:53-209`).

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Multimodal telemetry | `tools/multimodal_data.py`; `tools/agent_tools.py` | Metric, log, and trace analysis functions/tools | The core representation is largely text returned to the LLM. |
| Evidence collection agent | `agents/workflow.py:109-166` | LlamaIndex `ReActAgent` chooses diagnostic tools | This is an evidence-gathering subloop. |
| Time-window extraction | `agents/workflow.py:53-106` | LLM emits labelled start/end time fields | Parsing is line-based and permissive. |
| RCA output | `agents/workflow.py:168-209` | Final LLM call returns component list and reason | It is a diagnosis text/JSON contract, not an independent ranker. |
| System context/topology hint | `agents/base.py:65-130` | Hard-coded service call chain and pod/node context | No general graph object was found in the inspected path. |
| Evaluation ground truth | `agents/base.py:_load_groundtruth_by_uuid` | Loads UUID-keyed ground truth for evaluation/hints | Ground truth use must be considered when interpreting benchmark modes. |

## 6. Core Modules

- `agents/workflow.py`: three-phase workflow and reasoning trace.
- `agents/react.py`, `plan_execute.py`, `reflection.py`, and related files: alternative agent runners.
- `tools/agent_tools.py`: tool wrappers and input schemas.
- `tools/multimodal_data.py`: data access, metric aliases, anomaly methods, and summaries.
- `config.py`: component lists, fault labels, data paths, and prompt settings.

## 7. Important Classes / Functions

- `RCAWorkflow.phase1_understand`, `phase2_collect_evidence`, and `phase3_analyze`.
- `BaseAgentRunner` and shared LLM/tool initialization in `agents/base.py`.
- `metrics_tool`, `log`/`trace` tool wrappers in `tools/agent_tools.py`.
- `_detect_anomalies_sigma`, `_detect_anomalies_darts`, and threshold routines in `tools/utils.py`.

## 8. Data Flow

```text
fault record
  → time window
  → tool parameters
  → metric/log/trace result
  → textual evidence summary
  → final JSON component candidates
```

Metrics can be normalized and analyzed deterministically before being placed
in the LLM context. The inspected workflow does not attach a mandatory source,
entity, timestamp, transformation, and confidence object to every evidence
item.

## 9. LLM Usage

LLMs extract incident timing, select tools in the ReAct variant, and synthesize
the final component diagnosis. The repository also supports multiple agent
styles, so “RCAgentBench” is a benchmark/codebase containing variants rather
than one single agent architecture.

## 10. Prompt Design

The workflow prompts require tool calls in a ReAct text format and final JSON
with component names/reasons. `config.py` supplies service/fault descriptions
and allowed labels. The prompt constrains the output, but the final analysis
still relies on LLM parsing and does not perform a deterministic candidate
validity check in the inspected code.

## 11. Tool System

Tools include time-series metric anomaly detection, trace anomaly detection,
log processing, and system information. They are read-oriented diagnostic
operations. Tool calls are emitted by the ReAct agent and their returned text
is recorded in `reasoning_trace`.

## 12. Planning / Orchestration

`RCAWorkflow` is an explicit three-phase orchestration. Its evidence phase is
ReAct-style multi-step collection, but no separate dynamic Planner or
replanning policy was found in this path. Other runner variants may use fixed
plan/execute prompts; they should not be conflated with free-form planning.

## 13. Memory / Context

The current workflow keeps evidence and a reasoning trace in process state and
serializes outputs to JSONL. No cross-incident persistent memory was found in
the inspected core path. Hard-coded system context is prompt context, not an
operational memory architecture.

## 14. Retrieval / RAG

No general RAG layer was required by the inspected workflow. Data tools read
configured metric/log/trace files. A returned evidence string is not
automatically provenance-rich retrieval.

## 15. Graph / Topology / Algorithms

`agents/base.py` includes a hard-coded service call chain and pod/node table as
system context. The inspected code does not construct a physical network
topology or a general graph-constrained RCA candidate space. Deterministic
anomaly routines remain important front-end components.

## 16. Verification

The benchmark can compare predictions with ground truth after the run, but the
workflow has no independent root-cause verifier, telemetry re-query gate, or
recovery check in the inspected path. A second LLM analysis is synthesis, not
strong verification by itself.

## 17. Evaluation

The codebase has common runner/evaluation infrastructure and supports token
tracking. The workflow output is a component list and reason; exact paper
metrics are kept in the paper note. The code does not expose a universal
tool-correctness, evidence-grounding, or remediation-safety metric.

## 18. Configuration

`config.py`, `config_local.py`, environment variables, and dataset paths set
model/API and telemetry locations. The README requires an API key; no secret
was read or stored.

## 19. Deterministic vs LLM Components

- Deterministic/ML: metric-name mapping, time parsing, sigma/Darts/threshold anomaly methods, file access, JSON extraction, and token counting.
- LLM: time-window interpretation, tool selection in agent variants, and final evidence synthesis.
- Agent runtime: LlamaIndex ReAct in the evidence phase; the exact variant depends on the runner.

## 20. Paper vs Code Differences

The repository gives a practical multimodal-agent benchmark implementation,
but the inspected workflow's RCA output is an LLM-selected component list,
not a separately verified root-cause ranking over a documented universe. The
service call chain is prompt context rather than demonstrated physical or
causal topology.

## 21. Reproducibility

Reproducibility is **Medium-Low** without the configured datasets, model/API,
and dependencies. The tool interfaces and data paths are visible, but no
execution or benchmark reproduction was attempted.

## 22. What I Learned from the Code

The benchmark's most reusable pattern is to place deterministic modality-
specific analysis behind tools and let an LLM choose which evidence to gather.
However, a tool-enabled evidence loop still needs a separate candidate model,
provenance schema, and verifier before it becomes reliable Network RCA.

## 23. Open Questions

- How are candidate components enumerated and aligned with ground-truth granularity in each runner?
- How much do hard-coded service context and fault hints affect agent results?
- Can metric/log/trace outputs be converted into auditable evidence tickets without overloading the prompt?

## Paper ↔ Code

Paper notes: [RCAgentBench paper notes](../../../papers/aiops/rcagentbench/notes.md)

