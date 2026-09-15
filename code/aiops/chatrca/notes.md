# ChatRCA — Source-Code Reading Notes

Paper: [ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop](../../../papers/aiops/chatrca/notes.md)

## Repository Identity

- Repository: [leocache/ChatRCA](https://github.com/leocache/ChatRCA)
- Official status: Author-Endorsed Implementation
- Evidence: The paper points to the repository; identity is kept conservative because the local code was read as an implementation artifact rather than independently validated against every paper result.
- Local path: `sources/code/aiops/chatrca/ChatRCA`
- Read at commit: `448c2714047a1cf05371937b811dfe75ca8394d6`
- Branch: `master`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

ChatRCA builds an AutoGen group-chat workflow with an observation engineer,
architecture/resource/network experts, an operator that executes registered
data-processing functions, and an OperationEngineer that synthesizes a
structured diagnosis. A UserProxy is present as the human interaction point.

## 2. Repository Architecture

```text
fault description
        ↓
UserProxy starts group chat
        ↓
observation engineer calls data/metric/log/trace/architecture functions
        ↓
specialist agents produce structured findings
        ↓
OperationEngineer merges findings
        ↓
FinalDiagnosis JSON
```

## 3. Entry Points

- `main.py:run_TrainTicket_fault` / `run_GAIA_fault` start conversations.
- `agents.py` defines agents, function registration, group chat, and JSON schemas.
- `schemas.py` defines `EvidenceItem`, `ExpertFinding`, and `FinalDiagnosis`.
- `utils/` contains data readers and metric/log/trace processing functions.

## 4. Main Execution Flow

`main.py` loads a fault record and calls `User_proxy.initiate_chat` with the
group-chat manager. The observation engineer can call registered functions
through `Operator`. Architect, Resource, and Network experts return JSON
findings; the OperationEngineer chooses a final category/location and includes
expert findings/evidence. `GroupChat` is configured with `max_round=20`.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Observation/evidence collection | `agents.py:237-307` | Observation engineer calls registered functions through Operator | Functions return processed source data and summaries. |
| Specialist agents | `agents.py:160-235` | Architecture, Resource, and Network expert prompts | They are role-specialized LLM agents. |
| Human-in-the-loop entry | `agents.py:40-43`, `main.py:17-20` | `UserProxyAgent` starts/manages group chat | Exact intervention timing is configuration-dependent. |
| Evidence schema | `schemas.py:26-31` | Source type/name, abnormal field/value, reason | Sources are limited to metric/log/trace/architecture. |
| Final diagnosis | `schemas.py:41-49` | Category, location, confidence, evidence, expert findings | Structured output, not necessarily independently verified. |

## 6. Core Modules

- `agents.py`: agent roles, prompts, function registration, and group-chat manager.
- `schemas.py`: structured diagnosis/evidence contracts.
- `main.py`: dataset-specific launch paths.
- `utils/`: telemetry readers, anomaly filters, summaries, and localization helpers.

## 7. Important Classes / Functions

- `Observable_engineer_agent`, `Architect_Expert_Agent`, `Resource_Expert_Agent`, `NetWork_Expert_Agent`, and `Operation_Engineer_Agent`.
- `register_function` calls for `data`, `architecture_information`, `log_data_processing`, `metric_data_processing`, and `trace_data_processing`.
- `EvidenceItem`, `ExpertFinding`, and `FinalDiagnosis`.

## 8. Data Flow

```text
fault file
  → registered data reader/processor
  → raw data + anomaly summary
  → specialist findings
  → final structured evidence and diagnosis
```

The evidence schema carries source type/name and abnormal values, but does not
require a timestamp, query ID, transformation history, freshness, or exact
candidate relation.

## 9. LLM Usage

The system uses several role-specialized LLM agents and a final synthesizer.
Current knowledge-base classification: **Multi-Agent / fixed role-based
agentic workflow**. The code demonstrates multi-agent communication and tool
execution, but not necessarily dynamic Planner/Replanner behavior.

## 10. Prompt Design

Expert prompts require JSON with category, service location, confidence, and
evidence. The observation prompt asks for both raw data and summarized
anomalies. This improves interface structure but does not by itself establish
truth or causal correctness.

## 11. Tool System

The registered tools read/process data, architecture, logs, metrics, and
traces. `Operator` owns execution; the observation agent selects calls. These
are primarily evidence/retrieval operations; no inspected tool performs a
network configuration change or remediation.

## 12. Planning / Orchestration

The group-chat protocol and role order provide fixed orchestration. Multiple
roles do not automatically mean an explicit Planner. No clear next-action
planner, replanning state, or verification loop was found in the inspected
files.

## 13. Memory / Context

Conversation history in AutoGen is the primary shared context. No separate
persistent episodic/long-term memory or memory selection policy was found in
the inspected core code.

## 14. Retrieval / RAG

The data/architecture/telemetry functions are operational retrieval tools.
They are not automatically RAG, and the conversation history is not a
long-term memory store.

## 15. Graph / Topology / Algorithms

Architecture information is a tool/evidence source, but the inspected code
does not expose a graph algorithm or physical network topology model. Expert
roles discuss dependencies through prompt context.

## 16. Verification

Experts provide confidence and evidence, and the final agent compares their
opinions. No independent telemetry re-query, deterministic consistency check,
execution feedback, or recovery verification was found. A final LLM synthesis
is not strong verification.

## 17. Evaluation

The code defines structured outputs suitable for diagnosis evaluation. Exact
benchmark metrics belong in the paper note; static inspection did not reveal a
complete tool-correctness, cost, latency, or remediation-success protocol.

## 18. Configuration

`config.yaml`, `.env.example`, AutoGen model configuration, and dataset utility
files configure execution. No secret was read and no model/API call was made.

## 19. Deterministic vs LLM Components

- Deterministic: data loading/filtering, registered-function dispatch, schemas, and conversation setup.
- LLM: specialist analysis, evidence interpretation, and final diagnosis synthesis.
- Human: UserProxy is structurally available, but exact intervention semantics were not execution-verified.

## 20. Paper vs Code Differences

The code supports a role-based multi-agent diagnostic conversation with tools,
but the inspected path is not a complete autonomous remediation Agent. There
is no demonstrated persistent memory, repair executor, rollback, or recovery
loop.

## 21. Reproducibility

Reproducibility is **Medium-Low** without AutoGen dependencies, data files,
model/API settings, and expected local tool environment. No execution was
attempted.

## 22. What I Learned from the Code

ChatRCA makes evidence schema and role specialization concrete. It also shows
why “multi-agent” is not enough for reliable RCA: roles can produce structured
opinions, but candidate control, evidence provenance, independent verification,
and action safety still need separate mechanisms.

## 23. Open Questions

- Does the UserProxy pause for human approval during diagnosis or only bootstrap the chat?
- How are conflicting specialist findings reconciled beyond the final LLM prompt?
- How would architecture evidence be extended to physical network topology and time-stamped telemetry?

## Paper ↔ Code

Paper notes: [ChatRCA paper notes](../../../papers/aiops/chatrca/notes.md)

