Status: evolving

# Topology-aware RCA

## Definition

Topology-aware RCA uses relationships among components to constrain, propagate, or interpret evidence during root-cause analysis. “Topology” can mean a service dependency graph, call graph, physical network graph, dynamic causal graph, anomaly dependency graph, or operational subsystem graph; the representation must be named explicitly.

## Why It Matters

Failures propagate through dependencies. Structure can reduce an otherwise large candidate space and help distinguish an upstream cause from downstream symptoms. However, a dependency edge is not automatically a physical causal edge.

## Core Mechanism

Topology can play different roles:

- input features to a graph model;
- a learned dynamic causal/dependency structure;
- a candidate-generation or pruning constraint;
- a ranking prior or propagation path;
- context supplied to an LLM;
- a troubleshooting procedure rather than a physical graph.

These roles should not be collapsed into one “topology-aware” label.

## Typical Architecture

```text
telemetry evidence
→ map evidence to components / variables
→ apply topology, dependency, or causal constraints
→ generate or rank candidate roots
→ verify against observations
```

## Example

RCAgentBench uses microservice call chains, service/pod relationships, and fault-level hierarchy as structural context for an Agent; it does not establish that this context is a learned physical causal graph. Removing the fault-level hierarchy sharply lowers localization (Source: RCAgentBench, Sec. V-D, Table V, p. 8).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Planning](../../concepts/planning.md)

## Representative Papers

- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — service call-chain and hierarchy context.
- [StaR](../../papers/aiops/star/notes.md) — dynamic graph and stateful causal discovery.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — anomaly-level diagnostic dependency graph and causal search.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — static service dependencies and dynamic node/pod/container context supplied to role agents; not a physical causal graph.

## Advantages

- Narrows or structures candidate reasoning.
- Represents propagation and component relationships that isolated signals miss.
- Can make explanations more operationally meaningful.

## Limitations

- Topology can be incomplete, stale, or at the wrong abstraction level.
- Learned Granger or dependency structure may predict useful relations without proving physical cause.
- Service, subsystem, and physical network graphs have different node and edge semantics.

## My Understanding

Topology is a source of structure, not a guarantee of causality. In the current AIOps work, it is more useful to ask “what role does this graph play in candidate generation and evidence verification?” than to ask only whether a paper is topology-aware.

StaR shows a stronger graph role than RCAgentBench: the dynamic graph participates in message passing and causal-coefficient estimation, while RCAgentBench uses service relationships and hierarchy mainly as diagnostic context and structural prior. StaR also explicitly distinguishes Granger-predictive usefulness from physical causality (Source: [StaR paper note](../../papers/aiops/star/notes.md), Sec. 3.3 and Sec. 5).

CAUSALDX shows a third role: its graph is over anomaly observations and resolution dependencies. It organizes search and back-propagation, but should not automatically be read as a physical service or network topology (Source: [CAUSALDX paper note](../../papers/aiops/causaldx/notes.md), Sec. 3.1).

KAT shows a fourth role: a directed graph of business-support subsystems retrieves cross-system context. This is useful dependency context, but it is not a physical network topology and does not by itself prove a causal edge (Source: [KAT paper note](../../papers/aiops/kat/notes.md), Sec. V).

ChatRCA shows a fifth role: the Architecture Agent supplies static service dependencies and dynamic node/container/pod details to other agents as context. This can guide hypothesis formation, but the paper does not use a formal topology algorithm to rank roots or establish physical network causality (Source: [ChatRCA paper note](../../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.2).

CHIEF adds a structural graph that is neither service topology nor physical topology: its subtask, Agent, and step/data-flow edges organize execution responsibility and candidate backtracking. Its “causal” attribution is supported by trajectory structure, virtual-oracle expectations, and counterfactual correction within an Agent benchmark; it should not be treated as evidence of physical network causality (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 3–4).

## Open Questions

- How can physical network topology and dynamic traffic paths be represented together?
- When should topology be trusted, updated, or treated as uncertain?
