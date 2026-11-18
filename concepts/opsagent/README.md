Status: evolving

# OpsAgent — Agents for IT Operations

**Working definition in this knowledge base:** research on using LLM Agents and Multi-Agent systems to perform or assist IT incident management, troubleshooting, root-cause analysis, and governed operations. This is a local organizing category. The NKU paper titled *OpsAgent* is one specific system within this broader topic.

## Operational mental model

~~~text
Incident
→ telemetry and runtime evidence
→ candidate generation / constraint
→ Agent investigation and tool use
→ diagnosis or action proposal
→ independent verification and human gate
→ bounded remediation
→ recovery evidence and memory update
~~~

This is a synthesis map, not a claim that every paper implements every stage. Papers cover different parts: RCA and candidate pruning, multimodal evidence, tool orchestration, operational memory, workflow generation, execution safety, or production evaluation. A recommendation is not an executed remediation, and an executed command is not proof of recovery.

## Entry points

- [OpsAgent research index](../../notes/opsagent/README.md)
- [Paper inventory](../../notes/opsagent/paper-inventory.md)
- [OpsAgent Review v1](../../notes/opsagent/reviews/opsagent-review-v1.md)
- [Research directions](../../notes/opsagent/research-directions.md)
- [Research gaps](../../notes/opsagent/research-gaps.md)
- [NKU OpsAgent system](../../papers/opsagent/opsagent-system.md) · [KRCA](../../papers/opsagent/krca.md) · [OpsMem](../../papers/opsagent/opsmem.md) · [Graph of States](../../papers/opsagent/graph-of-states.md) · [PoS](../../papers/opsagent/pos.md)
- Related studies: [FlowXpert](../../papers/opsagent/flowxpert.md), [KnowLution](../../papers/opsagent/knowlution.md), [ToolRCA](../../papers/opsagent/toolrca.md)
- [AgentOps vs OpsAgent](../../notes/guides/agentops-vs-opsagent.md)

## Related AIOps concepts

- [Candidate Space](../aiops/candidate-space.md) — scope, granularity, pruning and ground-truth alignment.
- [Evidence Provenance](../aiops/evidence-provenance.md) — source, entity, time, freshness and query history.
- [Verification](../aiops/verification.md) — check evidence, diagnosis, action and recovery separately.
- [Agentic Incident Management](../aiops/agentic-incident-management.md) and [Network AIOps architecture synthesis](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md).

## Boundary

OpsAgent uses an Agent to operate on services, systems, networks or other IT infrastructure. [AgentOps](../agentops/README.md) treats the Agent and its harness as the system being operated. In a practical loop, an OpsAgent can fail and become an AgentOps diagnosis target.
