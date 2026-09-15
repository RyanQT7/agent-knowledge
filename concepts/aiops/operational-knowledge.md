Status: evolving

# Operational Knowledge for AIOps

## Definition

Operational knowledge is domain-specific information that connects symptoms or incident descriptions to context, checks, root causes, and actions. It can be stored as troubleshooting guides, SOP trees, knowledge graphs, expert rules, historical cases, or verified tool definitions.

## Why It Matters

Raw telemetry is often incomplete and LLMs do not automatically know local system semantics. Operational knowledge can constrain candidate generation, make checks executable, support explanations, and preserve lessons from previous incidents. Its quality, freshness, provenance, and coverage are part of RCA quality.

## Core Mechanism

An operational-knowledge lifecycle is:

```text
incident / symptom
→ retrieve relevant knowledge
→ add system context
→ execute checks or reason over cases
→ verify root cause
→ recommend / gate action
→ collect feedback
→ update, compress, or retire knowledge
```

Different systems implement different parts:

- **SOP tree:** guide-covered checks become deterministic branches and leaves.
- **Anomaly/causal graph:** observations and candidate causes are organized for search and verification.
- **Knowledge graph + context graph:** entity-level cases and subsystem dependencies are retrieved into an LLM prompt.

## Typical Architecture

```text
operational documents / incident records / expert labels
→ structured knowledge representation
→ retrieval and context selection
→ tool/check or LLM reasoning
→ evidence-backed diagnosis
→ human feedback and controlled update
```

## Example

LLMGuard compiles TSGs into an SOP Checking Tree and uses verified binary checks. KAT stores error/context/solution paths and a TBSS subsystem graph, then updates cases using expert feedback. Comfey adds a production triage variant: historical incidents, team-authored TSGs, local enrichment, and a shared routing table guide ownership decisions, while transfer evidence and engineer outcomes feed later routing. These are knowledge-grounded, but they emphasize different interfaces—deterministic checks, interpretable retrieval/evolution, or decentralized team routing (Sources: [LLMGuard note](../../papers/aiops/llmguard/notes.md), Sec. IV; [KAT note](../../papers/aiops/kat/notes.md), Sec. IV–VI; [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 3.3–3.7).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Production Evaluation](production-evaluation.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Context Engineering](../../concepts/context-engineering.md)
- [Memory](../../concepts/memory.md)

## Representative Papers

- [LLMGuard](../../papers/aiops/llmguard/notes.md) — TSG/SOP digitization, verified tools, deterministic checking.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — expert rules, product modules, anomaly graph, and verification.
- [KAT](../../papers/aiops/kat/notes.md) — troubleshooting knowledge graph, subsystem context, and continuous improvement.
- [Comfey](../../papers/aiops/comfey/notes.md) — team-local enrichment, TSG/historical matching, shared routing statistics, and human feedback for production incident triage.

## Advantages

- Makes local system semantics and known procedures explicit.
- Supports interpretable retrieval, evidence chains, and safer action gating.
- Allows domain knowledge and operator feedback to improve a system without assuming immediate parameter training.

## Limitations

- Knowledge construction and maintenance are expensive.
- Stale, incomplete, contradictory, or biased knowledge can systematically mislead diagnosis.
- Closed SOP leaves may miss unknown faults; open-ended LLM expansion may hallucinate unsupported causes.
- A persistent knowledge base is not automatically Agent memory, and retrieval is not automatically causal reasoning.

## My Understanding

Operational knowledge is a bridge between raw observations and actionable diagnosis. The key design question is not simply whether a system uses a knowledge base, but how knowledge is selected, grounded in current evidence, verified, updated, and retired.

## Open Questions

- How can network operational knowledge be versioned with topology and configuration changes?
- How should conflicting operator feedback and stale troubleshooting rules be resolved?
- What evidence threshold should be required before retrieved knowledge can authorize remediation?
