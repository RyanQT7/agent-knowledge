Status: evolving

# Evidence Provenance in AIOps

## Definition

Evidence Provenance records where an AIOps observation came from, which entity and time window it describes, how it was obtained, and how it supports or contradicts a candidate diagnosis. An Evidence Ticket is one operational representation of this idea.

## Why It Matters

RCA combines heterogeneous and imperfect evidence. Without source, time, entity, freshness, and query information, an LLM or operator may not be able to distinguish a current observation from a stale summary, a symptom from a cause, or a missing modality from a negative observation.

## Core Mechanism

An evidence item should preserve:

~~~text
source
modality
entity
time window
observation
confidence
provenance / query
freshness
missingness or conflict
related candidate
~~~

The item can then be passed to candidate generation, LLM reasoning, independent verification, or human review without losing its origin.

## Typical Architecture

~~~text
raw telemetry or document
→ modality-specific extraction
→ time/entity normalization
→ Evidence Ticket
→ candidate or hypothesis association
→ reasoning and verification
~~~

## Example

ChatRCA makes a standardized data ticket and asks a human to verify it. RCAgentBench exposes metrics, logs, and traces through separate diagnostic tools. LLMGuard preserves evidence chains through deterministic SOP checks, while CAUSALDX verifies candidate observations with tools. Cloud-OpsBench adds a related reproducibility boundary: historical telemetry, control-plane configuration, and runtime state are frozen, and commands return deterministic snapshot responses. That preserves state/query provenance for replay, but does not by itself establish that entity mapping, clock alignment, or causal interpretation is correct. These are different implementations of a related provenance requirement, not one shared protocol (Sources: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2; [RCAgentBench note](../../papers/aiops/rcagentbench/notes.md), Sec. IV-B; [LLMGuard note](../../papers/aiops/llmguard/notes.md), Sec. IV; [CAUSALDX note](../../papers/aiops/causaldx/notes.md), Sec. 4.3; [Cloud-OpsBench note](../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.2–2.4).

Cloud Intelligence/AIOps 2.0 adds provenance for the *knowledge side* of an operational decision: an OKA has identity, owner, scope, version, validation status, drift signals, and an anchor to a monitor or control point. This lets an audit ask which operational procedure guided an action. It does not replace telemetry provenance—source, entity, timestamp, query, freshness, and conflict status are still needed to verify the evidence itself (Source: [Cloud Intelligence note](../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.1–2.3).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Topology-aware RCA](topology-aware-rca.md)
- [Agentic Incident Management](agentic-incident-management.md)
- [Production Evaluation](production-evaluation.md)

## Representative Papers

- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md)
- [CAUSALDX](../../papers/aiops/causaldx/notes.md)
- [LLMGuard](../../papers/aiops/llmguard/notes.md)
- [ChatRCA](../../papers/aiops/chatrca/notes.md)
- [AIM](../../papers/aiops/aim/notes.md)
- [Cloud-OpsBench](../../papers/aiops/cloud-opsbench/notes.md)
- [Cloud Intelligence / AIOps 2.0](../../papers/aiops/cloud-intelligence/notes.md)

## Advantages

- Preserves source and time context across modalities.
- Makes LLM grounding and human review more auditable.
- Supports reproducible re-query and independent verification.
- Allows missing, stale, or conflicting evidence to be represented explicitly.

## Limitations

- Provenance does not make an observation correct.
- Entity mapping and clock alignment can remain uncertain.
- Large evidence sets still require selection, summarization, and compression.
- A shared schema must accommodate different telemetry systems without hiding modality-specific semantics.

## My Understanding

Evidence Provenance is the interface between raw operational data and a trustworthy RCA decision. It is narrower than a complete memory system and different from a final explanation: it preserves the evidence needed to produce, challenge, and audit that explanation.

The current papers support the need for evidence tickets, evidence chains, tool traces, and verification, but do not provide a unified network-specific schema. For Network AIOps, the schema must include physical entities, interface/link relationships, traffic/NetFlow windows, configuration versions, and conflict status.

## Open Questions

- How should evidence provenance represent delayed, duplicated, contradictory, or missing telemetry?
- How should one observation map to multiple candidate levels such as device, interface, link, and module?
- How much raw evidence should be retained versus summarized?
- How can provenance be checked automatically before an LLM or human accepts a root cause?
