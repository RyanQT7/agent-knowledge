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

The first five-paper formal batch is recorded in [AIOps Knowledge Review v1](../../notes/aiops/reviews/aiops-knowledge-review-v1.md). Concepts remain evolving and should be updated only when later sources add durable cross-paper evidence. The first Batch 2 paper, [Comfey](../../papers/aiops/comfey/notes.md), adds a production incident-triage and team-routing perspective; it should not be generalized into physical RCA without further evidence.
