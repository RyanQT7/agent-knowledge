# AIOps Literature Map

Status: Batch 1 and Batch 2 formal notes completed; AIOps Knowledge Review v2 pending

This map is a navigation skeleton for the AIOps literature. It is organized by problem and system role, not by presumed algorithmic similarity. Formal notes replace source-PDF links as papers complete full reading; source PDFs remain in the inventory.

## Detection / Anomaly Detection

- [TFC — temporal–frequency–curvature fusion](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>) — multivariate time-series anomaly detection.
- [TFT-GCN](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>) — temporal/frequency modeling with cross-variable graph structure.
- [Foundation Models for Time Series](<../../sources/papers/AIOps_papers/KDD26-Foundation Models for Time Series Analysis- Concepts,Methodologies, and Applications.pdf>) — background on forecasting and anomaly-detection applications.

## Root Cause Analysis / Fault Localization / Diagnosis

- [StaR](../../papers/aiops/star/notes.md) — dynamic topology and stateful causal discovery.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — long-tail and cascading cloud incidents with LLM-guided causal reasoning.
- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — multimodal RCA and agent-oriented evaluation.
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — production LMaaS diagnosis with SOPs and evidence verification.
- [KAT](../../papers/aiops/kat/notes.md) — evolving telecom troubleshooting and diagnosis.
- [Comfey](../../papers/aiops/comfey/notes.md) — production team-ownership triage; not direct physical RCA.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — role-specialized multimodal RCA with RAG and human verification/adjudication.

## Incident Management / Triage / Operational Knowledge

- [Comfey](<../../sources/papers/AIOps_papers/FSE26-An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure.pdf>) — decentralized incident triage and routing.
- [TSGen](../../papers/aiops/tsgen/notes.md) — filtering, distillation, structured generation, and iterative maintenance of troubleshooting guides.
- [StepFly](../../papers/aiops/stepfly/notes.md) — executable troubleshooting-guide workflows with DAG-constrained scheduling, QPPs, and structured working memory.
- [Cloud Intelligence / AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>) — knowledge-anchored agentic AIOps proposal.

## Remediation / Automatic Repair

- [AIM](../../papers/aiops/aim/notes.md) — prompt-level multimodal alert interpretation, mitigation planning, and constrained Ansible execution.
- [StepFly](<../../sources/papers/AIOps_papers/FSE26-StepFly- Agentic Troubleshooting Guide Automation for Incident Diagnosis.pdf>) — TSG execution that can support mitigation.
- [FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>) — symbolic diagnosis and repair of agentic workflows.
- [HARNESSFIX](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>) — diagnosis and repair of agent harness flaws.

## Evaluation / Reproducibility

- [RCAgentBench](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>) — benchmark with multimodal evidence, diagnostic tools, and process evaluation.
- [Cloud-OpsBench / State Snapshot](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>) — reproducible state-snapshot evaluation for agentic SRE.

## LLM / Agent for AIOps

The presence of an LLM does not by itself establish an Agent architecture. The following are grouped by the first-stage evidence:

- **Explicit or proposed agentic workflow:** LLMGuard, Comfey, AIM, StepFly, Cloud-OpsBench, RCAgentBench, CAUSALDX, and ChatRCA. Comfey provides a deployed bounded team-routing loop; AIM provides a plan-to-act workflow with controlled execution but no demonstrated live replanning; ChatRCA provides role-specialized evidence collection and human-gated RCA, without autonomous remediation.
- **LLM with Agent status unclear or not established:** KAT, TSGen, and Cloud Intelligence/AIOps 2.0 (the latter is a proposed architecture, not a fully validated system in this triage). TSGen is more specifically an LLM-assisted operational-knowledge curation pipeline; its proposed Agent Skills adaptation is downstream future work.
- **Agent-system reliability, not infrastructure AIOps:** FlowFixer, HARNESSFIX, and hierarchical failure attribution.
- **LLM/foundation-model background without an Agent workflow:** Foundation Models for Time Series.

## Data Modality Map

- **Metrics / time series:** AIM (prompt-level aligned context), RCAgentBench, Cloud-OpsBench, StaR, TFC, TFT-GCN; several cloud papers mention operational signals without a complete modality breakdown.
- **Logs:** AIM, RCAgentBench, Cloud-OpsBench, ChatRCA, and agent-system trace papers; exact use in LLMGuard and CAUSALDX needs full-paper verification.
- **Traces / spans:** AIM and RCAgentBench explicitly; agent trajectory traces occur in FlowFixer, HARNESSFIX, and hierarchical failure attribution.
- **Alerts / events / tickets:** LLMGuard, Comfey, AIM, KAT, TSGen, and the incident-management papers. TSGen's “logs” are primarily incident discussions/records, not confirmed raw telemetry logs.
- **Topology / architecture / dependencies:** StaR, CAUSALDX, ChatRCA, Cloud Intelligence, and Cloud-OpsBench. ChatRCA uses service/deployment dependencies as context, not a physical causal graph.
- **Configuration / runtime state / tools:** Cloud-OpsBench, FlowFixer, HARNESSFIX, StepFly, and LLMGuard.
- **Traffic / NetFlow / packets:** not confirmed by the first-stage scan.

## Relation to the Current Research Direction

The most direct path is to connect a conventional telemetry layer (metrics, logs, traces, topology, and possibly traffic) to an RCA/diagnosis layer and then study whether LLMs or agents add value in evidence organization, explanation, or safe remediation. The current inventory contains strong candidates for each part, but not yet a demonstrated unified network-specific pipeline.

## Formal Notes Completed

- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — explicit multimodal metrics/logs/traces and agent-process evaluation; a service-topology context rather than a physical causal graph.
- [StaR](../../papers/aiops/star/notes.md) — stateful dynamic-graph RCA over metric streams; predictive causal structure rather than proven physical causality.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — anomaly-graph causal search with open-set expansion and tool verification.
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — SOP-tree diagnosis with deterministic checks, evidence chains, and production human gating.
- [KAT](../../papers/aiops/kat/notes.md) — graph-grounded telecom troubleshooting with cross-subsystem context and feedback-driven updates.
- [Comfey](../../papers/aiops/comfey/notes.md) — team-local enrichment, TSG/historical matching, and statistical cross-team routing in Azure production.
- [AIM](../../papers/aiops/aim/notes.md) — prompt-level multimodal context, adaptive exemplar retrieval, and plan-to-code execution.
- [StepFly](../../papers/aiops/stepfly/notes.md) — guide-derived DAG control, typed query plugins, executor scheduling, and structured evidence exchange.
- [TSGen](../../papers/aiops/tsgen/notes.md) — historical-incident filtering, diversity-aware distillation, structured TSG/DAG generation, and human-reviewed iterative updates.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — specialized multi-agent evidence collection, domain hypotheses, RAG, and two-stage human verification.
