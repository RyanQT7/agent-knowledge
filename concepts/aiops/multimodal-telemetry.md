Status: evolving

# Multimodal Telemetry in AIOps

## Definition

Multimodal telemetry means using more than one operational evidence modality—such as metrics, logs, traces, alerts, topology, configuration, or traffic—to understand an incident. The modalities are not interchangeable: each exposes different aspects of system behavior.

## Why It Matters

Metrics can reveal quantitative deviation, logs can expose error semantics and component context, and traces can expose request paths and timing relationships. Combining them can reduce ambiguity, but only if their time windows, entity identities, and provenance are aligned.

## Core Mechanism

The integration point may be:

- feature or representation fusion before a model makes a prediction;
- graph fusion of telemetry and dependency structure;
- prompt/context-level integration;
- tool-based collection in which an Agent queries each modality at runtime.

Calling a system multimodal does not identify which of these mechanisms it uses. Source-specific extraction and evidence provenance should remain visible.

## Typical Architecture

```text
incident window
→ query modality-specific sources
→ normalize entities and time ranges
→ extract modality-specific evidence
→ align or cross-check evidence
→ rank candidates / explain diagnosis
```

## Example

RCAgentBench exposes separate tools for Prometheus metrics, Elasticsearch logs, and Jaeger traces. The Agent integrates their returned observations during diagnosis rather than feeding a single learned feature tensor to a multimodal classifier (Source: RCAgentBench, Sec. IV-B, p. 5).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Topology-aware RCA](topology-aware-rca.md)
- [Context Engineering](../../concepts/context-engineering.md)
- [Tool Use](../../concepts/tool-use.md)

## Representative Papers

- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — explicit metrics/logs/traces tool integration.
- [AIM](../../papers/aiops/aim/notes.md) — timestamp/service-aligned metrics, logs, traces, and alerts integrated at prompt level with selective KPI context.
- [TSGen](../../papers/aiops/tsgen/notes.md) — text-centric incident metadata and discussion processing; metrics, traces, and images are future directions rather than evaluated modalities.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — role-based collection of metrics, logs, traces where available, service dependencies, and incident text; D2 has no traces and the method is not feature-level fusion.

## Advantages

- Provides complementary evidence and can expose relationships unavailable in one source.
- Makes it possible to test which modality contributes to localization, diagnosis, or explanation.

## Limitations

- Time alignment, missingness, inconsistent identifiers, and unequal evidence quality can make fusion misleading.
- More sources increase collection cost and context size.
- A tool-based workflow may depend on tool definitions and access permissions as much as on the model.

## My Understanding

The important unit is not merely the list “metrics + logs + traces.” It is the handoff from each source to a candidate and a verifiable observation. For network AIOps, traffic/NetFlow, syslog, counters, topology, and configuration may need different tools and different temporal semantics.

The Batch 1 papers make the label boundary clearer: RCAgentBench is explicitly multimodal over metrics, logs, and traces; StaR combines metric time series with graph structure but does not fuse heterogeneous telemetry; LLMGuard combines operational tools, logs, metrics, alerts, and SOPs procedurally; KAT combines text/entities and graphs. AIM adds prompt-level fusion of time-aligned metrics, logs, traces, and alerts, with rule-based KPI severity and selective inclusion before LLM generation. “Multi-source” or “graph-augmented” should therefore not automatically be rewritten as feature-level multimodal telemetry fusion (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 3.1–3.2).

## Open Questions

- How should heterogeneous network telemetry be aligned when clocks and reporting delays differ?
- Which evidence should be retained in an explanation when modalities disagree?
