# Preliminary AIOps Research Gaps

Status: Preliminary

These are first-stage observations from lightweight triage of 18 PDFs. They are hypotheses for prioritizing full-paper reading, not established literature conclusions.

| Possible gap | Why it may matter | Papers suggesting it | Needs full-paper verification |
|---|---|---|---|
| Telemetry alignment and evidence grounding | Explicit multimodal inputs appear in some papers, but the provenance, time alignment, missingness, and handoff from detection evidence to RCA are not consistently visible. | AIM, RCAgentBench, StaR, CAUSALDX, LLMGuard, ChatRCA | Yes |
| Dynamic topology plus causal RCA | Dynamic-graph reasoning addresses changing dependencies, while production LLM systems often depend on operational knowledge; their combination with noisy telemetry is not clear. | StaR, CAUSALDX, KAT, LLMGuard | Yes |
| Long-tail and cascading incidents | Root causes and downstream symptoms can be confused, especially when anomalies arrive in bursts; robust labels, uncertainty, and verification remain central. | CAUSALDX, LLMGuard, RCAgentBench | Yes |
| Detection-to-remediation continuity | Time-series detectors and agentic diagnosis/remediation systems appear as mostly separate families; common ground truth and end-to-end safety metrics are not yet apparent. | TFC, TFT-GCN, AIM, StepFly, RCAgentBench | Yes |
| Operational knowledge lifecycle | Retrieval, guide generation, execution, freshness, provenance, contradiction handling, and update/forgetting are treated from different angles rather than as one validated lifecycle. | KAT, TSGen, StepFly, Cloud Intelligence, LLMGuard | Yes |
| Agent evaluation under production constraints | Benchmarks can standardize tools and processes, while deployments expose permissions, latency, cost, and escalation constraints; a common evaluation view is not yet visible. | RCAgentBench, Cloud-OpsBench, Comfey, ChatRCA | Yes |
| Network-specific traffic evidence | No paper in this batch clearly confirms NetFlow, packet, or traffic-centric inputs, leaving a direct connection to network traffic research unestablished. | None confirmed; compare KAT, StaR, RCAgentBench during full reading | Yes |
| Separating model, orchestration, and tool failures | Agent traces contain failures from the model, harness, tools, and environment, but attribution may require different evidence and repair actions. | FlowFixer, HARNESSFIX, hierarchical failure attribution, RCAgentBench | Yes |

## How to Use These Gaps

For each gap, full-paper reading should verify the exact data, task definition, ground truth, evaluation protocol, and deployment assumptions before turning it into a research claim. A gap may disappear when the papers are read in detail, or it may become a candidate experiment after comparison.
