# AIOps Concepts

Status: evolving

This directory is reserved for cross-paper AIOps concepts that emerge from formal full-paper reading. The current pass creates navigation and scope only; it does not create a collection of empty concept files or turn lightweight triage observations into settled definitions.

## Planned Areas

- Anomaly Detection
- Fault Detection and Incident Detection
- Root Cause Analysis and Fault Localization
- Fault Diagnosis and Classification
- Failure Prediction
- Remediation
- Metrics, Logs, Traces, Alarms, and Events
- Multi-modal AIOps
- Topology-aware and Causal AIOps
- Traffic / NetFlow / Packet-based AIOps
- LLM / Agent for AIOps
- Operational Knowledge and Troubleshooting Guides
- Evaluation and Production Deployment

## Maintenance Rules

Concept files should contain knowledge that remains useful across multiple papers, codebases, or documents. They should not become copies of paper abstracts, benchmark tables, or single-system implementation notes. Each new concept should be created only when full-paper reading shows a stable cross-source idea.

For the current inventory and preliminary taxonomy, see [AIOps paper inventory](../../notes/aiops/paper-inventory.md). Formal notes will be created under [AIOps paper notes](../../papers/aiops/) after full-paper reading, using the [AIOps paper template](../../templates/aiops-paper-note.md).

## Current Formal Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Topology-aware RCA](topology-aware-rca.md)
- [Production Evaluation](production-evaluation.md)
- [Operational Knowledge](operational-knowledge.md)
- [Agentic Incident Management](agentic-incident-management.md)
- [Evidence Provenance](evidence-provenance.md)
- [Candidate Space](candidate-space.md)
- [Verification](verification.md)

The first five-paper formal batch is recorded in [AIOps Knowledge Review v1](../../notes/aiops/reviews/aiops-knowledge-review-v1.md). Concepts remain evolving and should be updated only when later sources add durable cross-paper evidence. Batch 2 adds [Comfey](../../papers/aiops/comfey/notes.md) for production incident triage, [AIM](../../papers/aiops/aim/notes.md) for prompt-level multimodal alert interpretation and plan-to-act, [StepFly](../../papers/aiops/stepfly/notes.md) for bounded TSG execution, [TSGen](../../papers/aiops/tsgen/notes.md) for historical-incident knowledge curation, and [ChatRCA](../../papers/aiops/chatrca/notes.md) for role-specialized human-gated RCA. Batch 3 adds [Cloud-OpsBench](../../papers/aiops/cloud-opsbench/notes.md) for reproducible process evaluation, [Cloud Intelligence/AIOps 2.0](../../papers/aiops/cloud-intelligence/notes.md) for knowledge-artifact governance, [CHIEF](../../papers/aiops/chief/notes.md) for hierarchical execution-trace attribution, and [FlowFixer](../../papers/aiops/flowfixer/notes.md) for symbolic workflow repair verification. Their cross-paper boundaries are consolidated in [AIOps Knowledge Review v2](../../notes/aiops/reviews/aiops-knowledge-review-v2.md) and [AIOps Knowledge Review v3](../../notes/aiops/reviews/aiops-knowledge-review-v3.md); these systems should not be generalized into a single physical-RCA or autonomous-Agent architecture without further evidence.
