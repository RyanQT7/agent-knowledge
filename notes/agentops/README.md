# AgentOps: Operations for Agent Systems

**Scope here:** observe, diagnose, attribute, verify, and recover failures in LLM agent and multi-agent systems themselves. This local category is distinct from OpsAgent, which applies agents to IT operations.

## Start here

1. [AgentOps Knowledge Review v1](reviews/agentops-review-v1.md)
2. [Paper inventory](paper-inventory.md) — publication/full-read status, sources, and reading order.
3. [Research directions](research-directions.md) and [research gaps](research-gaps.md).
4. Method notes: [AgentRx](../../papers/agentops/agentrx.md), [TraJudger](../../papers/agentops/trajudger.md), [PROBE](../../papers/agentops/probe.md), [Trial by Trace](../../papers/agentops/trial-by-trace.md).

## Working model

AgentOps is a lifecycle, not a dashboard:

agent/harness execution → evidence capture → anomaly detection → step/agent attribution → bounded response → independent outcome verification

Preserve the earliest unrecoverable cause, the agents/steps through which it propagated, the terminal symptom, and evidence for each claim. Diagnosis, retry, and verified recovery are different outcomes.

## Boundaries

- This repository taxonomy does not imply that all papers use the same classification.
- Agent System Operations is a survey/framework; AgentRx and TraJudger diagnose trajectories; PROBE evaluates guided retry; Trial by Trace evaluates harness behavior.
- Reuse existing [CHIEF](../../papers/aiops/chief/notes.md) and [FlowFixer](../../papers/aiops/flowfixer/notes.md) analyses rather than duplicating them.
- The AgentOps ↔ OpsAgent integration is a research hypothesis in [the cross-topic guide](../guides/agentops-vs-opsagent.md).
