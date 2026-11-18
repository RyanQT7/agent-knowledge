# AgentOps research directions

| Direction | Research question and methods | Evidence / maturity | Limitation and value |
| --- | --- | --- | --- |
| Agent observability and trace schema | What must be captured to reconstruct the agent’s view: identity, inputs/outputs, calls/results, compaction, state updates, delegation, dependencies, policy, verification? | Trial by Trace defines seven harness dimensions and a trace/evidence protocol; AgentRx normalizes heterogeneous logs. | Harness-specific instrumentation can omit hidden context or expose sensitive prompts. Foundational measurement problem. |
| Trajectory monitoring and anomaly detection | Can semantic failure be detected online, with what delay and false-alarm rate? | Agent System Operations surveys lifecycle-stage detection; most reviewed benchmarks/methods remain post-hoc. | Detection delay, false alarms, and operating cost are less established than terminal success or offline diagnosis. |
| Failure taxonomy and ground truth | How to label recoverable errors, first unrecoverable cause, propagation, terminal symptom, and uncertainty? | AgentRx has cross-domain categories; TraJudger has MAS-specific modes; PROBE has operational failure families. | Labels are expensive, category boundaries vary, and critical failure can be ambiguous. |
| Failure attribution and propagation | Which step/agent introduced an error, who carried it forward, and what evidence supports that chain? | AgentRx adds invariant evidence; TraJudger builds HCG and reverse-traces; CHIEF is existing related work. | Hidden/shared context and missed dependency edges still break causal reconstruction. Active 2026 topic. |
| Harness reliability | Did runtime preserve context, govern tools, complete delegation, expose failures, and verify lifecycle events? | Trial by Trace separates Agent and Harness score layers. | One selected run per cell, uneven tasks, and candidate links limit causal inference; repeated and validated studies needed. |
| Recovery and self-improvement | How can diagnosis become a bounded fix that is tested and retained? | PROBE tests diagnosis-derived one-retry guidance; existing FlowFixer repairs agent workflows. | Correct diagnosis does not guarantee repair; multi-round effects, regression prevention, and verification remain open. |
| Safety and governance | When should an agent retry, change a prompt/schema, execute a tool, or request human approval? | Agent System Operations and Trial by Trace frame governance; PROBE gates guidance by evidence and scope. | A correct textual diagnosis does not establish safe authority, rollback, or change control. |

## Maturity judgment

- **More established:** event/tool trace capture, deterministic schema/policy checks, offline task-outcome evaluation. These vary across harnesses and do not guarantee semantic observability.
- **Active in 2026:** full-trace benchmarks, step/agent attribution, structured evidence, explicit dependency reconstruction, harness-level scoring, guided recovery.
- **Unresolved:** online detection with calibrated false alarms; causal ground truth for MAS propagation; diagnosis under missing/compacted context; recovery verification; representative production benchmarks; privacy-preserving observability.

These judgments describe the reviewed set, not a field-wide consensus or SOTA claim.

## High-value questions

1. Can a trace contract make model-visible context, tool/environment state, and orchestration dependencies reconstructible with bounded storage and privacy?
2. Can deterministic checks and semantic judgments expose calibrated evidence and abstain when traces are insufficient?
3. Can causal graphs distinguish initiating fault, contributing condition, propagation conduit, and terminal symptom?
4. How should recovery be tested against independent environment state, with rollback and human approval?
5. Which harness criteria transfer across coding, GUI, web, and operations agents, and which require domain-specific evaluators?

## Paper links

- [AgentRx](../../papers/agentops/agentrx.md)
- [TraJudger](../../papers/agentops/trajudger.md)
- [PROBE](../../papers/agentops/probe.md)
- [Trial by Trace](../../papers/agentops/trial-by-trace.md)
- [Agent System Operations](../../papers/agentops/agent-system-operations.md)
- [Inventory](paper-inventory.md)
