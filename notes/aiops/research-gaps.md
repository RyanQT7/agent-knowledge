# Preliminary AIOps Research Gaps

Status: Preliminary; informed by AIOps Batch 1 and Batch 2 formal reading

These began as first-stage observations from lightweight triage of 18 PDFs. The Batch 1 and Batch 2 reassessments below add formal-paper evidence, but the gaps remain hypotheses for research planning, not established novelty claims.

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

## Batch 1 Reassessment

Status: Preliminary, informed by formal reading of RCAgentBench, StaR, CAUSALDX, LLMGuard, and KAT. This section does not turn the observations into proven novelty claims.

| Gap | Batch 1 evidence | Confidence | Remaining verification |
|---|---|---|---|
| Telemetry alignment and evidence provenance | RCAgentBench exposes metrics/logs/traces as separate tools; CAUSALDX, LLMGuard, and KAT use different observation/context paths rather than a shared alignment protocol. | Medium | Network clocks, missingness, entity mapping, and contradictory evidence need experiments. |
| Dynamic topology plus causal RCA | StaR handles dynamic/stateful graph relationships; RCAgentBench, CAUSALDX, and KAT use service/anomaly/subsystem structures with different semantics. | Medium | Physical network topology and learned predictive graphs need direct comparison. |
| Long-tail, cascading, and multi-root incidents | CAUSALDX explicitly evaluates long-tail/cascading cases; StaR includes multi-root synthetic settings; the other systems use different closed or annotated spaces. | Medium | Network fault labels and unknown-root evaluation remain absent. |
| Detection-to-remediation continuity | Most papers assume an alert, anomaly window, rule observation, or user error; KAT/LLMGuard/CAUSALDX recommend or gate actions but do not share an end-to-end protocol. | High | A network study must connect detection uncertainty to RCA and safe remediation. |
| Operational knowledge lifecycle | LLMGuard shows SOP digitization/execution, CAUSALDX uses rules/modules/memory, and KAT provides graph retrieval plus expert feedback/update. | High | Versioning, contradiction handling, freshness, and forgetting need formal evaluation. |
| Agent evaluation under production constraints | RCAgentBench measures process and evidence in a public testbed; LLMGuard and KAT report deployment; CAUSALDX reports production records and human feedback. Their tasks and metrics differ. | High | A common network protocol should separate correctness, evidence, latency, cost, safety, and human effort. |
| Network-specific traffic evidence | None of the five formal papers establishes a complete RCA method over traffic/NetFlow/packets plus physical topology. | High | Full reading of later traffic/network papers is required. |
| Separating model, orchestration, and tool failures | RCAgentBench tool/workflow ablations, CAUSALDX verification, and LLMGuard SOP/evidence ablations indicate that non-model components affect results. | Medium | Need controlled network ablations and failure attribution. |

These reassessments are linked to the [AIOps Knowledge Review v1](reviews/aiops-knowledge-review-v1.md); remaining AIOps PDFs in the inventory are still triage-only and are not evidence for a completed gap claim.

## Batch 2 Reassessment: Agentic Incident Management

Status: Preliminary, informed by formal reading of Comfey, AIM, StepFly, TSGen, and ChatRCA and consolidated in [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md).

| Gap | Batch 2 evidence | Confidence | Remaining verification |
|---|---|---|---|
| Agent boundary and autonomy evaluation | The batch spans LLM-assisted knowledge curation, fixed/plan-to-act workflows, bounded DAG execution, production routing, and human-gated multi-agent RCA; labels such as “agentic” do not imply the same loop or action authority. | High | Define and validate capability-based criteria on additional systems and matched experiments. |
| Multi-agent necessity and cost | Comfey and ChatRCA use role/team specialization; StepFly uses homogeneous executors; AIM and TSGen use staged pipelines. Existing ablations do not match token, tool, latency, or human-review budgets. | High | Controlled single-agent versus multi-agent comparisons with equal context, tools, cost, and intervention. |
| Verification and evidence correctness | ChatRCA separates category, reasoning, and evidence consistency; AIM uses code/testbed checks; StepFly and TSGen use guide/engineering checks. None supplies a common physical-causality verifier. | High | Network evidence provenance, independent checks, abstention, and root-node validation. |
| Operational knowledge versus Agent memory | TSGs, SOPs, routing tables, RAG cases, caches, and StepFly key-value data have different lifecycles. Cross-incident write, selection, conflict, freshness, compression, and forgetting remain underspecified. | High | Formal memory/knowledge lifecycle and drift experiments. |
| Safe remediation and recovery feedback | AIM executes constrained Ansible in a testbed; Comfey can connect to mitigation; StepFly and ChatRCA are read-oriented; no Batch 2 system demonstrates a complete production repair/rollback/recovery loop. | High | Permission, approval, rollback, recovery observation, and failure-cost evaluation in a realistic network environment. |
| Open-set and multi-root Agentic RCA | The workflows use guide coverage, service/component candidates, ownership teams, or closed labels; out-of-coverage behavior and physical multi-root diagnosis are not established. | High | Network incidents with unknown, cascading, and multiple simultaneous roots. |
| Network-specific multimodal Agent interfaces | The batch contains cloud/microservice telemetry and operational text, but no complete protocol for physical topology, syslog, traffic/NetFlow, configuration, and time/entity alignment. | High | Network-specific benchmark and evidence-ticket design. |
| Production Agent evaluation | Comfey and StepFly provide operational deployment evidence, while AIM and ChatRCA provide controlled or private evaluations and TSGen deploys knowledge curation. There is no shared measure of correctness, cost, latency, safety, and human effort. | High | A common lifecycle evaluation across offline, shadow, and permissioned online modes. |

These are strengthened gaps, not claims that no prior work exists. Later full-paper batches may narrow, merge, or invalidate them.
