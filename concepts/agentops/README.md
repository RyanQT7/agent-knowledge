Status: evolving

# AgentOps — Operations for Agent Systems

**Working definition in this knowledge base:** methods for observing, diagnosing, attributing, verifying, and improving LLM Agent and Multi-Agent systems as the operational object. This is a local research category, not a universal paper taxonomy.

## Mental model

~~~text
Agent / harness execution
→ instrumented trajectory
→ detect anomalous behavior
→ localize failure step and responsible agent
→ reconstruct propagation dependencies
→ propose bounded recovery
→ verify with independent evidence
→ update runtime / workflow / governance
~~~

AgentOps asks whether an Agent understood the task, maintained state, selected and called the right tool, handled observations, coordinated with peers, verified its output, and terminated correctly. A terminal symptom and the root-cause step may belong to different Agents.

## Core concepts

- **Trajectory:** ordered execution events with identity, time, input/output, tool call/result, state updates, handoffs, dependencies and verification.
- **Failure attribution:** identify the earliest responsible step or Agent, failure class and the route by which the error reached the final symptom.
- **Harness reliability:** assess the runtime, context, tool, governance, lifecycle and verification behavior independently of the underlying model's task capability.
- **Recovery:** distinguish detection, diagnosis, guidance, retry, successful repair and independently observed recovery.

A complete trace is not automatically a causal explanation; missing context, incorrect dependency edges and ambiguous ground truth remain open problems.

## Entry points

- [AgentOps research index](../../notes/agentops/README.md)
- [Paper inventory](../../notes/agentops/paper-inventory.md)
- [AgentOps Review v1](../../notes/agentops/reviews/agentops-review-v1.md)
- [Research directions](../../notes/agentops/research-directions.md)
- [Research gaps](../../notes/agentops/research-gaps.md)
- [AgentRx](../../papers/agentops/agentrx.md) · [TraJudger](../../papers/agentops/trajudger.md) · [PROBE](../../papers/agentops/probe.md) · [Trial by Trace](../../papers/agentops/trial-by-trace.md)
- Existing related work reused: [CHIEF](../../papers/aiops/chief/notes.md) and [FlowFixer](../../papers/aiops/flowfixer/notes.md)
- [AgentOps vs OpsAgent](../../notes/guides/agentops-vs-opsagent.md)

## Related concepts

- [Agent Runtime](../agent-runtime.md) and [Agent Loop](../agent-loop.md) — execution and state transitions.
- [Evidence Provenance](../aiops/evidence-provenance.md) and [Verification](../aiops/verification.md) — traceable evidence and explicit checks.
- [Candidate Space](../aiops/candidate-space.md) — defines candidate steps, agents, failure types or propagation links.

## Boundary

AgentOps diagnoses and governs the Agent system. It is distinct from [OpsAgent](../opsagent/README.md), where the Agent operates IT infrastructure as its task domain. The two directions can form a reliability loop, but transferring an AgentOps evaluator into OpsAgent remains a research hypothesis until tested.
