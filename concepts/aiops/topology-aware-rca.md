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
- CAUSALDX — anomaly dependency/causal graph (formal note pending in this batch).

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

## Open Questions

- How can physical network topology and dynamic traffic paths be represented together?
- When should topology be trusted, updated, or treated as uncertain?
