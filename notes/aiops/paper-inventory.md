# AIOps Paper Inventory

Status: Preliminary

Scan date: 2026-09-15

Scope: all PDF files currently under `sources/papers/AIOps_papers/`.

This is a first-stage inventory and lightweight triage, not a set of formal paper-reading notes. The records below use the title page, PDF metadata, abstract, and only the introduction or overview material needed for classification. Any uncertain field is marked explicitly and must be verified during full-paper reading.

## Overview

- Total PDFs: 18
- Successfully identified: 18
- Unreadable: 0
- Duplicate content: 0 (all 18 files had distinct hashes)
- Suspicious files: 0
- Formal paper notes created in this pass: 5 (RCAgentBench, StaR, CAUSALDX, LLMGuard, KAT)
- Original PDFs: retained under `sources/papers/AIOps_papers/` and ignored by Git

The batch spans the AIOps chain from detection to root-cause analysis, diagnosis, incident management, and remediation. It also contains a separate group of agent reliability and evaluation papers. The most direct gaps for the current research are multimodal telemetry, topology-aware RCA, production diagnosis, and the connection between detection evidence and LLM/agent-based diagnosis.

## Paper Inventory

| # | Title | File | Authors | Year / Venue | Main task | Modalities / type | Method family | LLM / Agent | Production / data | Relevance | Priority | Batch |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [LLMGuard](../../papers/aiops/llmguard/notes.md) | [PDF](<../../sources/papers/AIOps_papers/DSN26-LLMGuard_Multi-Agent_Fault_Diagnosis_for_Reliable_Language-Model-as-a-Service.pdf>) | Yuedong Zhong et al. | 2026 / DSN | Diagnosis, RCA, mitigation support | Logs, alerts, SOP/TSG text, runtime state; multi-source | Deterministic multi-agent workflow; SOP checking tree; evidence verification | LLM: Yes; Agent: Yes, multi-agent | Production LMaaS; private industrial data; large scale | High | P0 | Batch 1; **Full Reading: Completed** |
| 2 | Diagnosis-Driven Automatic Repair for Agentic Workflow via Symbolic Inference | [PDF](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>) | Xuyan Ma et al. | 2026 / arXiv | Failure attribution, RCA, diagnosis, repair | Agent traces, workflow/configuration, prompts, variables, tool interactions; multi-source | Symbolic execution traces/specifications; verification; repair patch generation | LLM: Yes; Agent: target is agentic workflow; standalone Agent status unclear | Production: unclear; data/scale: unclear; open source: unclear | Medium | P2 | Batch 3 |
| 3 | An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure | [PDF](<../../sources/papers/AIOps_papers/FSE26-An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure.pdf>) | Yuhan Yao et al. | 2026 / FSE Companion | Incident triage, routing, diagnosis support | Incident reports, tickets, historical incidents, routing metadata; multi-source text-centric | Decentralized team-local agents; accept/reject/transfer negotiation | LLM: Yes; Agent: Yes, decentralized multi-agent | Production Azure; real incidents; private data; large scale | High | P1 | Batch 2 |
| 4 | Cloud Intelligence/AIOps 2.0: Knowledge-Anchored Agentic AIOps | [PDF](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>) | Dongmei Zhang et al. | 2026 / FSE Companion | Incident management, RCA, remediation architecture | Logs, metrics, incidents, docs/TSGs, dependencies, operational signals; multi-source/multimodal | Operational Knowledge Artifacts; anchored retrieval; bounded execution and escalation | LLM: Yes; Agent: Yes, proposed architecture | Production validation: unclear; operational/private setting; scale unclear | High | P2 | Batch 3 |
| 5 | Freezing the Crime Scene: A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation | [PDF](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>) | Guangba Yu, Yilun Wang, Michael R. Lyu | 2026 / FSE Companion | Agentic SRE evaluation; RCA/evidence workflow evaluation | Metrics, logs, Kubernetes configuration, runtime state, mocked interfaces; multimodal | Deterministic state snapshots / digital twins; process-oriented benchmark | LLM: Yes; Agent: Yes, evaluation target | Prototype/testbed; incidents are simulated or injected; data/scale unclear | High | P1 | Batch 3 |
| 6 | Leveraging LLMs for Alert Summarization and Mitigation Plan Generation | [PDF](<../../sources/papers/AIOps_papers/FSE26-Leveraging LLMs for Alert Summarization and Mitigation Plan Generation.pdf>) | Komal Sarda et al. | 2026 / FSE Companion | Alert summarization, RCA, mitigation/remediation | Metrics, logs, traces, alerts; explicit multimodal telemetry | Agentic Plan→Act; in-context exemplar retrieval; code/script generation | LLM: Yes; Agent: Yes, Plan→Act workflow | Testbed and datasets; injected faults; public/private status unclear; small/medium scale | High | P1 | Batch 2 |
| 7 | StepFly: Agentic Troubleshooting Guide Automation for Incident Diagnosis | [PDF](<../../sources/papers/AIOps_papers/FSE26-StepFly- Agentic Troubleshooting Guide Automation for Incident Diagnosis.pdf>) | Jiayi Mao et al. | 2026 / FSE | Incident diagnosis, triage, mitigation support | TSG/docs, incident history, plugin/tool outputs; telemetry details partly unclear | TSG-to-DAG compilation; scheduler/executor; structured plugin memory; parallel execution | LLM: Yes; Agent: Yes | 92 real-world TSGs; code and synthesized data public; production execution unclear | High | P1 | Batch 2 |
| 8 | TSGen: Automated Troubleshooting Guide Generation | [PDF](<../../sources/papers/AIOps_papers/FSE26-TSGen- Automated Troubleshooting Guide Generation.pdf>) | Yi Xiao et al. | 2026 / FSE Companion | TSG generation and maintenance; incident management support | Incident tickets/reports/conversations and operational text; text-centric multi-source | LLM pipeline for filtering, classification, and structured guide generation | LLM: Yes; Agent: No / unclear | Historical incidents likely; production/data/open-source status unclear | High | P2 | Batch 2 |
| 9 | From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws | [PDF](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>) | Mengzhuo Chen et al. | 2026 / arXiv | Agent failure attribution, diagnosis, repair | Agent trajectories/traces, prompts, tool specifications, configuration, verification artifacts; multi-source | Harness Trace and Inference Record; failure attribution; scoped repair operators | LLM: Yes; Agent: target agent harness; exact framework role unclear | Production/real incidents/data/scale unclear; open source unclear | Medium | P2 | Batch 3 |
| 10 | From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems | [PDF](<../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>) | Yawen Wang et al. | 2026 / arXiv | Failure attribution and RCA for multi-agent systems | MAS logs/trajectories, thoughts, actions, observations, tool results, inter-agent messages; multi-source | Causal graph construction and hierarchical attribution | LLM: Yes; Agent: Yes, multi-agent system | Production/real incidents/scale unclear; code link shown, dataset status unclear | Medium | P2 | Batch 3 |
| 11 | [KAT](../../papers/aiops/kat/notes.md) | [PDF](<../../sources/papers/AIOps_papers/INFOCOM26-KAT_Knowledge-Context_Augmentation_for_Evolving_LLM-Based_Telecom_Troubleshooting.pdf>) | Kai Qian et al. | 2026 / INFOCOM | Telecom troubleshooting, fault diagnosis, remediation support | Error descriptions/events, cross-subsystem runtime state, structured knowledge/docs; multi-source, classical telemetry detail unclear | Knowledge/context augmentation and continual adaptation | LLM: Yes; Agent: No / unclear | Commercial telecom deployment; real errors; private data; large scale | High | P0 | Batch 1; **Full Reading: Completed** |
| 12 | [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) | [PDF](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>) | Hengyue Jiang et al. | 2026 / IWQoS | RCA, localization, explanation benchmark | Metrics, logs, traces; explicit multimodal | Agent-oriented benchmark; standardized diagnostic tools and process evaluation | LLM: Yes; Agent: Yes, benchmarked agent workflows | Microservice benchmark/testbed; public code; production/real incident status unclear | High | P0 | Batch 1; **Full Reading: Completed** |
| 13 | Foundation Models for Time Series Analysis: Concepts, Methodologies, and Applications | [PDF](<../../sources/papers/AIOps_papers/KDD26-Foundation Models for Time Series Analysis- Concepts,Methodologies, and Applications.pdf>) | Yuxuan Liang et al. | 2026 / KDD tutorial | Time-series forecasting and anomaly-detection background | Generic time series; single-modal for this triage | Foundation-model tutorial and application overview | LLM/FM: discussed; Agent: No | Tutorial; no AIOps production evaluation; dataset/scale/open-source N/A | Medium | P2 | Batch 4 |
| 14 | Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion | [PDF](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>) | Hang Cui et al. | 2026 / KDD | Anomaly detection | Multivariate time series; single-modal | Temporal, frequency, and curvature fusion with multi-scale evidence | LLM: No; Agent: No | Public benchmark datasets; no production evidence in triage; medium/unclear scale | High | P1 | Batch 4 |
| 15 | [StaR](../../papers/aiops/star/notes.md) | [PDF](<../../sources/papers/AIOps_papers/KDD26-StaR- Stateful Dynamic-Graph Root Cause Analysis throughMemory-Enhanced Causality Discovery.pdf>) | Haiyu Huang et al. | 2026 / KDD | RCA, fault localization, causal discovery | Multivariate time series plus dynamic topology/graph; multi-source | Dynamic-graph causal discovery with stateful, memory-enhanced effects | LLM: No; Agent: No; model memory is not Agent memory | Public code/datasets; production/real incident status unclear; scale unclear | High | P0 | Batch 1; **Full Reading: Completed** |
| 16 | [CAUSALDX](../../papers/aiops/causaldx/notes.md) | [PDF](<../../sources/papers/AIOps_papers/TKDE26-CAUSALDX- Diagnosing Long-Tail and Cascading Cloud Incidents with LLM-Guided Causal Reasoning.pdf>) | Zhuo Chang et al. | 2026 / IEEE TKDE | RCA, fault diagnosis, explanation | Anomaly observations/records, causal graph, expert knowledge; exact telemetry breakdown unclear | Anomaly-granular causal graph; LLM-guided causal reasoning; observation verification | LLM: Yes; Agent: Yes, LLM-agent component | Tencent cloud incidents; real/private data; large/unclear scale | High | P0 | Batch 1; **Full Reading: Completed** |
| 17 | TFT-GCN: A Time-Frequency Based Model for Time Series Anomaly Detection | [PDF](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>) | Zhenchang Xia et al. | 2026 / IEEE TKDE | Anomaly detection | Multivariate time series; single-modal | Temporal/spectral modules, frequency attention, cross-variable GCN, multi-scale attention | LLM: No; Agent: No | Public benchmark datasets and code; no production evidence in triage; medium/unclear scale | Medium | P2 | Batch 4 |
| 18 | ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop | [PDF](<../../sources/papers/AIOps_papers/TOSEM26-CharRCA-Wanglu.pdf>) | Mingxuan Hui et al. | 2026 / ACM TOSEM | RCA, diagnosis, explanation | Operational signals plus architecture/operation knowledge and human feedback; exact telemetry breakdown unclear | Specialized multi-agent roles with human-in-the-loop and uncertainty handling | LLM: Yes; Agent: Yes, multi-agent | Enterprise context; production evaluation/data/scale unclear; likely private | High | P1 | Batch 2 |

## Detailed Triage Records

The records below capture the minimum research interpretation needed for prioritization. They are not substitutes for full-paper notes.

### 1. LLMGuard (`llmguard`)

- **Research problem:** Diagnose complex, non-deterministic failures in large-scale language-model-as-a-service infrastructure while reducing hallucinated or inefficient diagnosis.
- **Method family:** A deterministic multi-agent workflow compiles standard operating procedures into a unified SOP Checking Tree, then verifies and prunes candidate diagnoses while preserving an evidence chain.
- **AIOps category:** Production LLM/Agent fault diagnosis, RCA, and mitigation support.
- **Data and evidence status:** Logs, alerts, SOP/TSG text, and runtime state are indicated; exact metrics/traces are not confirmed. The paper reports deployment in a production LMaaS setting with more than 10,000 accelerators and private industrial data.
- **Potentially useful idea:** Structured SOP execution and auditable evidence chains can constrain agent diagnosis.
- **Assumption that may not transfer:** The approach may depend on high-quality SOP coverage and LMaaS-specific failure modes.
- **Source / uncertainty:** Title page, Abstract, and Sec. I–II; exact modality breakdown and broader evaluation details need full-paper verification.
- **Full reading status:** Completed. See [formal AIOps note](../../papers/aiops/llmguard/notes.md). Full-paper review confirms 84 real production incidents over three months in an LMaaS environment exceeding 10,000 accelerators, with SOPCT-based deterministic diagnosis and SRE human gating (Source: Sec. V, pp. 6–8).

### 2. FlowFixer (`flowfixer`)

- **Research problem:** Attribute and repair failures in agentic workflows whose LLM outputs, node dependencies, and heterogeneous tools make trajectory-level feedback too coarse.
- **Method family:** Converts workflow executions into symbolic traces/specifications with node correctness, temporal dependencies, and causal relations; verifies failures and generates repair patches.
- **AIOps category:** Agent workflow reliability, failure attribution, RCA, and automatic repair.
- **Data and evidence status:** Agent traces, workflow configuration, prompts, variables, and tool interactions; a classical infrastructure telemetry setting is not established. Evaluated on failures from Dify, Coze, and n8n; production status is unclear.
- **Potentially useful idea:** Symbolic trace constraints may make failure localization and repair more targeted than undifferentiated trajectory feedback.
- **Assumption that may not transfer:** Workflow graphs and repair operators may not map directly to distributed infrastructure faults.
- **Source / uncertainty:** Title page, Abstract, and Sec. I; dataset openness, scale, and production realism need full-paper verification.

### 3. Comfey (`comfey`)

- **Research problem:** Route incomplete and fragmented production cloud incident reports to the right team when team maturity and observability differ.
- **Method family:** Decentralized team-local agents accept, reject, or transfer incidents and use a shared routing table through a stigmergic negotiation process.
- **AIOps category:** Production incident triage and routing; diagnosis/mitigation support rather than a complete RCA system.
- **Data and evidence status:** Incident reports, tickets, historical incidents, and routing metadata are central; the exact use of raw logs, metrics, or traces is not confirmed. The paper reports more than one year and roughly 19,500 Azure production incidents with private data.
- **Potentially useful idea:** Team-local agents can support incremental adoption and preserve local operational knowledge.
- **Assumption that may not transfer:** Routing accuracy and organizational ownership may be more central than root-cause correctness in this setting.
- **Source / uncertainty:** Title page, Abstract, and Sec. I; production statistics are reported in the introduction; detailed observability inputs need full-paper verification.

### 4. Cloud Intelligence / AIOps 2.0 (`aiops-2`)

- **Research problem:** Operational knowledge is scattered, fragile, and inconsistent, making agentic AIOps difficult to ground and evolve safely.
- **Method family:** Proposes Operational Knowledge Artifacts anchored to operational signals and control points, with curation, knowledge-grounded execution, risk boundaries, and escalation.
- **AIOps category:** Knowledge-anchored agentic AIOps; incident management, RCA, and remediation architecture.
- **Data and evidence status:** The proposal refers to logs, metrics, historical incidents, TSGs, service dependencies, and operational signals. This is a short conceptual/position paper; production validation and data scale are unclear.
- **Potentially useful idea:** Treating operational knowledge as anchored, executable artifacts makes provenance and bounded action explicit.
- **Assumption that may not transfer:** The architecture is a vision and may require substantial curation and control-plane integration before it is operational.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–3; StepFly is presented as an illustrative manifestation, not a substitute for direct evaluation of the proposal.

### 5. Cloud-OpsBench / State Snapshot (`cloud-opsbench`)

- **Research problem:** Live-cluster evaluation is stochastic and static telemetry lacks interaction, making agentic SRE evaluation hard to reproduce.
- **Method family:** Captures operational state snapshots as deterministic digital twins, including telemetry, control-plane configuration, data-plane state, and mocked operational interfaces.
- **AIOps category:** Agentic SRE benchmark and evaluation infrastructure.
- **Data and evidence status:** Metrics, logs, Kubernetes manifests, pod conditions/lists, and mocked tools; multimodal. The setting is a prototype/testbed with simulated or injected incidents; production status is unclear.
- **Potentially useful idea:** Separating operational state from runtime can enable repeatable comparison of both outcomes and diagnostic process.
- **Assumption that may not transfer:** Snapshot fidelity and mocked interfaces may not represent live permissions, latency, and evolving infrastructure.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; benchmark scale and data release status need full-paper verification.

### 6. AIM (`aim`)

- **Research problem:** Turn heterogeneous alerts into useful summaries, diagnoses, and executable mitigation plans without relying on proprietary SOPs.
- **Method family:** An agentic Plan→Act workflow retrieves relevant exemplars through adaptive in-context learning; a planning component summarizes/diagnoses and an acting component produces remediation scripts.
- **AIOps category:** Multimodal alert management, RCA, mitigation, and remediation.
- **Data and evidence status:** Metrics, logs, traces, and alerts are explicitly named; multimodal. Evaluation uses MicroSS/MSDS and a Robot Shop fault-injection testbed; production status is unclear.
- **Potentially useful idea:** Separating plan generation from executable action provides a concrete boundary for safety and evaluation.
- **Assumption that may not transfer:** Testbed fault representations, scripts, and available exemplars may differ from production network operations.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–3; exact public/private dataset status and scale need full-paper verification.

### 7. StepFly (`stepfly`)

- **Research problem:** Manual execution of troubleshooting guides is slow and error-prone, especially when guides contain branching, data-intensive queries, and parallelizable steps.
- **Method family:** Preprocesses TSGs into execution DAGs and uses a scheduler/executor plus structured plugin data and parallel execution.
- **AIOps category:** Agentic incident diagnosis, troubleshooting, triage, and mitigation support.
- **Data and evidence status:** TSGs, incident history, and plugin/tool outputs; examples refer to metrics, deployment, and code data, but exact telemetry coverage needs verification. Study includes 92 real-world TSGs; code and synthesized data are reported as public.
- **Potentially useful idea:** Explicit dependency graphs and a scheduler can make operational troubleshooting observable and parallelizable.
- **Assumption that may not transfer:** The value depends on guide quality, plugin availability, and permission to execute operational queries.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–4; whether execution was production-facing needs full-paper verification.

### 8. TSGen (`tsgen`)

- **Research problem:** Generate and maintain structured troubleshooting guides from historical incident reports when guides are missing, stale, or unstructured.
- **Method family:** An LLM pipeline filters and classifies historical tickets and generates structured TSG content.
- **AIOps category:** Operational knowledge curation and incident-management support.
- **Data and evidence status:** Incident tickets, reports, conversations, and operational text; text-centric and multi-source. Historical real incidents are suggested, but production deployment, scale, and openness are unclear.
- **Potentially useful idea:** Converting historical resolution narratives into maintainable operational artifacts may improve later diagnosis workflows.
- **Assumption that may not transfer:** Ticket quality and historical resolution bias can be inherited by generated guides; direct telemetry reasoning is not established.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1; dataset and validation details need full-paper verification.

### 9. HARNESSFIX (`harnessfix`)

- **Research problem:** Diagnose and repair flaws in the runtime harness around LLM agents, including context/memory, tools, orchestration, observability, verification, and governance.
- **Method family:** Normalizes failed trajectories into a trace record aligned with static harness artifacts, attributes failures, and applies scoped repair operators.
- **AIOps category:** Agent infrastructure observability, failure diagnosis, and repair.
- **Data and evidence status:** Agent trajectories/traces, prompts, tool specs, configurations, adapters, instrumentation, and verification scripts; multi-source but not classical network telemetry. Production evidence and scale are unclear.
- **Potentially useful idea:** Mapping runtime evidence back to harness artifacts can separate model errors from orchestration or tool-integration flaws.
- **Assumption that may not transfer:** Agent-harness failure classes are not equivalent to service or network faults.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1; benchmark/data details need full-paper verification.

### 10. Hierarchical Failure Attribution (`hierarchical-failure-attribution`)

- **Research problem:** Flat logs obscure causal structure in LLM-based multi-agent systems because thoughts, actions, observations, tool results, and inter-agent communication are intertwined.
- **Method family:** Builds causal graphs and performs hierarchical attribution across the multi-agent execution structure.
- **AIOps category:** Agent-system failure attribution and RCA.
- **Data and evidence status:** MAS logs/trajectories, tool executions, observations, thoughts/actions/results, and inter-agent messages; multi-source. Production incidents and scale are unclear; a code link is shown in the paper, but data status needs verification.
- **Potentially useful idea:** Hierarchical causal attribution may transfer as a way to avoid treating every event in a long agent trace as equally causal.
- **Assumption that may not transfer:** MAS execution logs differ from infrastructure telemetry and may not expose physical service causality.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1; repository/data details need full-paper verification.

### 11. KAT (`kat`)

- **Research problem:** Diagnose evolving telecom errors despite diverse descriptions, cross-subsystem dependencies, and newly appearing error types.
- **Method family:** Combines structured knowledge, context augmentation, and continual adaptation for LLM-based troubleshooting.
- **AIOps category:** Production telecom troubleshooting, fault diagnosis, and remediation support.
- **Data and evidence status:** Error descriptions/events, cross-subsystem runtime state, and structured knowledge/documents; multi-source, while exact raw metrics/logs/traces are not confirmed. The paper reports deployment in a commercial TBSS with private telecom data and large user/error volume.
- **Potentially useful idea:** Evolving knowledge and cross-subsystem context are direct design concerns for network diagnosis.
- **Assumption that may not transfer:** Telecom business/service context and private operational knowledge may be difficult to reproduce in another network environment.
- **Source / uncertainty:** Title page, Abstract, and Sec. I–II; detailed telemetry and open-source status need full-paper verification.
- **Full reading status:** Completed. See [formal AIOps note](../../papers/aiops/kat/notes.md). Full-paper review confirms a private commercial TBSS deployment, a 54,537-case expert-labelled corpus, a troubleshooting knowledge graph, subsystem context enhancement, and feedback-driven updates; it does not establish a full multi-step Agent or physical topology RCA protocol (Source: Sec. IV–VIII).

### 12. RCAgentBench (`rcagentbench`)

- **Research problem:** Evaluate multimodal root-cause analysis agents in microservices with standardized diagnostic tools, models, and process-level outcomes.
- **Method family:** Agent-oriented benchmark over metrics, logs, and traces, with tools for metric anomaly detection, log pattern analysis, and span analysis.
- **AIOps category:** Multimodal RCA/localization benchmark and agent evaluation.
- **Data and evidence status:** Metrics, logs, and traces are explicitly multimodal. The benchmark/testbed and code are public according to the paper; production/real-incident status and scale are unclear.
- **Potentially useful idea:** Separating tool capabilities from agent reasoning makes the diagnostic process and evidence use measurable.
- **Assumption that may not transfer:** Benchmark distributions and standardized tools may not reflect the noise, access limits, and topology of a production network.
- **Source / uncertainty:** Title page, Abstract, and Sec. I–II; exact dataset construction and incident realism need full-paper verification.

### 13. Foundation Models for Time Series (`ts-foundation-models`)

- **Research problem:** Summarize concepts, methods, implementation choices, and applications of foundation models for time-series analysis.
- **Method family:** Tutorial/overview rather than a single AIOps method; anomaly detection and forecasting are relevant applications.
- **AIOps category:** Time-series background for metric/traffic forecasting and anomaly detection.
- **Data and evidence status:** Generic time series; single-modal for this triage. AIOps is an application context, not a demonstrated production system in the short tutorial.
- **Potentially useful idea:** Foundation-model pretraining and transfer may provide a background lens for telemetry modeling.
- **Assumption that may not transfer:** Generic time-series results do not establish gains on operational metrics, logs, or network traffic.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; tutorial scope means detailed AIOps evidence is not expected.

### 14. TFC (`tfc`)

- **Research problem:** Detect time-series anomalies whose evidence can appear as changes in temporal behavior, frequency patterns, or local curvature.
- **Method family:** Temporal–frequency–curvature fusion with multi-scale evidence and dynamic-perspective anomaly modeling.
- **AIOps category:** Metric/time-series anomaly detection.
- **Data and evidence status:** Multivariate time series; single-modal. The abstract reports six benchmark datasets; production/real-incident evidence is not established in this triage.
- **Potentially useful idea:** Combining complementary temporal and frequency/shape evidence may help detect different telemetry anomaly types.
- **Assumption that may not transfer:** Generic benchmark patterns and labels may not transfer to noisy, changing network telemetry.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; detailed datasets and deployment properties need full-paper verification.
- **Full reading status:** Completed. See [formal AIOps note](../../papers/aiops/rcagentbench/notes.md). Full-paper review confirms 400 Chaos-Mesh fault cases over metrics, logs, and traces; this is a controlled microservice benchmark rather than a production deployment study (Source: Sec. III, p. 3).

### 15. StaR (`star`)

- **Research problem:** Static topology assumptions fail under changing systems, while stateful anomalies such as memory leaks can cause delayed downstream effects.
- **Method family:** Dynamic-graph causal discovery enhanced with state/history to model changing dependencies and delayed effects.
- **AIOps category:** Topology-aware RCA, fault localization, and causal discovery.
- **Data and evidence status:** Multivariate time series plus dynamic topology/graph; multi-source. Code and datasets are reported as public; production and real-incident status are unclear.
- **Potentially useful idea:** Combining topology change with stateful causal evidence is directly relevant to evolving infrastructure diagnosis.
- **Assumption that may not transfer:** Causal assumptions and benchmark graph quality may not hold for incomplete or noisy production topology.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; exact scale and telemetry mapping need full-paper verification.
- **Full reading status:** Completed. See [formal AIOps note](../../papers/aiops/star/notes.md). Full-paper review confirms stateful dynamic-graph causal discovery over synthetic and public metric datasets; no LLM/Agent or production deployment is claimed (Source: Sec. 3–5).

### 16. CAUSALDX (`causaldx`)

- **Research problem:** Diagnose long-tail and cascading cloud incidents where many downstream anomalies create overload and obscure the initiating cause.
- **Method family:** Anomaly-granular causal graphs, expert rules plus LLM-guided causal reasoning, and observation-based self-verification.
- **AIOps category:** Production cloud RCA, fault diagnosis, explanation, and causal reasoning.
- **Data and evidence status:** Anomaly records/observations, causal graphs, and expert knowledge; exact metrics/logs/traces breakdown is unclear. The abstract reports real Tencent TEG cloud incidents and private operational data.
- **Potentially useful idea:** Separating anomaly generation from causal verification may reduce symptom-chasing and hallucinated explanations.
- **Assumption that may not transfer:** Expert rules and verification assumptions may be domain-specific and require trustworthy observations.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; detailed datasets, scale, and telemetry provenance need full-paper verification.
- **Full reading status:** Completed. See [formal AIOps note](../../papers/aiops/causaldx/notes.md). Full-paper review confirms 1,148 private Tencent production incident records, anomaly-graph select/expand/verify search, and human-gated mitigation; it does not establish a physical topology or unattended autonomous deployment (Source: Sec. 3–6).

### 17. TFT-GCN (`tft-gcn`)

- **Research problem:** Detect anomalies in multivariate time series while modeling both temporal/frequency behavior and cross-variable interactions.
- **Method family:** Temporal and spectral modules, frequency attention, cross-variable GCN, and multi-scale attention.
- **AIOps category:** Metric/time-series anomaly detection.
- **Data and evidence status:** Multivariate time series; single-modal. The paper reports seven benchmark datasets and public code; production/real-incident status is not established in this triage.
- **Potentially useful idea:** Jointly modeling frequency structure and variable interactions may be useful for correlated telemetry.
- **Assumption that may not transfer:** Cross-variable graph structure and benchmark assumptions may not match dynamic network dependencies.
- **Source / uncertainty:** Title page, Abstract, and Sec. I–II; detailed dataset characteristics need full-paper verification.

### 18. ChatRCA (`chatrca`)

- **Research problem:** Improve cloud RCA when a monolithic LLM misses structured workflow and automated reasoning lacks calibrated uncertainty or expert oversight.
- **Method family:** Specialized Manager, Observation, Architecture, Operation, and Expert agents with human-in-the-loop feedback.
- **AIOps category:** LLM/multi-agent RCA, diagnosis, explanation, and human-assisted operations.
- **Data and evidence status:** Anomalous operational signals, architecture/operation knowledge, and human feedback; exact metrics/logs/traces are not confirmed. Enterprise context is evident, but production evaluation, data access, and scale are unclear.
- **Potentially useful idea:** Role decomposition plus human review gives explicit places to inject domain knowledge and uncertainty handling.
- **Assumption that may not transfer:** Human availability and carefully separated operational roles may be difficult to maintain at high incident volume.
- **Source / uncertainty:** Title page, Abstract, and Sec. 1–2; concrete telemetry and deployment details need full-paper verification. The filename says `CharRCA`, while the title page says `ChatRCA`.

## Taxonomy

The first taxonomy is driven by the observed papers rather than by a requirement that every possible category be populated.

### AIOps task taxonomy

- **Detection / Anomaly Detection:** [TFC](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>), [TFT-GCN](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>), and the time-series foundation-model tutorial.
- **RCA / Fault Localization / Diagnosis:** [StaR](<../../sources/papers/AIOps_papers/KDD26-StaR- Stateful Dynamic-Graph Root Cause Analysis throughMemory-Enhanced Causality Discovery.pdf>), [CAUSALDX](<../../sources/papers/AIOps_papers/TKDE26-CAUSALDX- Diagnosing Long-Tail and Cascading Cloud Incidents with LLM-Guided Causal Reasoning.pdf>), [RCAgentBench](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>), [LLMGuard](<../../sources/papers/AIOps_papers/DSN26-LLMGuard_Multi-Agent_Fault_Diagnosis_for_Reliable_Language-Model-as-a-Service.pdf>), [KAT](<../../sources/papers/AIOps_papers/INFOCOM26-KAT_Knowledge-Context_Augmentation_for_Evolving_LLM-Based_Telecom_Troubleshooting.pdf>), and [ChatRCA](<../../sources/papers/AIOps_papers/TOSEM26-CharRCA-Wanglu.pdf>).
- **Incident Management / Triage / Knowledge:** [Comfey](<../../sources/papers/AIOps_papers/FSE26-An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure.pdf>), [TSGen](<../../sources/papers/AIOps_papers/FSE26-TSGen- Automated Troubleshooting Guide Generation.pdf>), [StepFly](<../../sources/papers/AIOps_papers/FSE26-StepFly- Agentic Troubleshooting Guide Automation for Incident Diagnosis.pdf>), and [Cloud Intelligence/AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>).
- **Remediation / Repair:** [AIM](<../../sources/papers/AIOps_papers/FSE26-Leveraging LLMs for Alert Summarization and Mitigation Plan Generation.pdf>), [StepFly](<../../sources/papers/AIOps_papers/FSE26-StepFly- Agentic Troubleshooting Guide Automation for Incident Diagnosis.pdf>), [FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>), and [HARNESSFIX](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>).
- **Evaluation:** [RCAgentBench](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>) and [Cloud-OpsBench](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>).

### Cross-cutting method and system taxonomy

- **Topology-aware / causal AIOps:** StaR, CAUSALDX, and the hierarchical failure-attribution paper.
- **Multimodal telemetry:** AIM and RCAgentBench explicitly combine multiple telemetry modalities; Cloud-OpsBench combines telemetry with configuration/runtime state; StaR combines time series with topology.
- **Knowledge-anchored operations:** KAT, StepFly, TSGen, LLMGuard, and Cloud Intelligence/AIOps 2.0.
- **LLM / agentic AIOps:** LLMGuard, Comfey, AIM, StepFly, KAT, RCAgentBench, CAUSALDX, ChatRCA, Cloud-OpsBench, and the agent-reliability papers. TSGen uses an LLM but is not established as an Agent architecture in this triage.
- **Metric / time-series foundations:** TFC, TFT-GCN, and the time-series foundation-model tutorial.
- **Agent-system reliability rather than infrastructure AIOps:** FlowFixer, HARNESSFIX, and hierarchical failure attribution.
- **Traffic / NetFlow / packet-centric AIOps:** not confirmed in this batch.

## Recommended Reading Batches

See the detailed [reading roadmap](reading-roadmap.md). The proposed order favors direct relevance to network/infrastructure RCA, then operational agent workflows, then agent evaluation/reliability, and finally time-series detection foundations.

## Recommended First Batch

1. [RCAgentBench](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>) — a direct entry point for multimodal RCA and agent/tool evaluation.
2. [StaR](<../../sources/papers/AIOps_papers/KDD26-StaR- Stateful Dynamic-Graph Root Cause Analysis throughMemory-Enhanced Causality Discovery.pdf>) — covers dynamic topology and stateful causal effects without adding LLM-specific confounders.
3. [CAUSALDX](<../../sources/papers/AIOps_papers/TKDE26-CAUSALDX- Diagnosing Long-Tail and Cascading Cloud Incidents with LLM-Guided Causal Reasoning.pdf>) — focuses on long-tail/cascading cloud incidents and LLM-guided causal reasoning.
4. [LLMGuard](<../../sources/papers/AIOps_papers/DSN26-LLMGuard_Multi-Agent_Fault_Diagnosis_for_Reliable_Language-Model-as-a-Service.pdf>) — production-scale, deterministic multi-agent diagnosis and evidence constraints.
5. [KAT](<../../sources/papers/AIOps_papers/INFOCOM26-KAT_Knowledge-Context_Augmentation_for_Evolving_LLM-Based_Telecom_Troubleshooting.pdf>) — directly connects evolving operational knowledge with telecom troubleshooting.

Together these papers should establish a first comparison across multimodal evidence, dynamic topology, production constraints, causal RCA, knowledge grounding, and the boundary between an LLM workflow and an Agent system.

## Observed Research Themes

- Production systems need operational knowledge, permissions, uncertainty handling, and escalation in addition to model accuracy.
- RCA increasingly combines heterogeneous evidence: metrics, logs, traces, alerts, topology, configuration, documents, and incident history.
- Topology and causal structure are used to reduce symptom-chasing, but dynamic dependencies and delayed effects remain difficult.
- Agentic systems add tools, planning/execution, multi-agent roles, or human review; not every LLM pipeline is an Agent.
- Detection models and RCA/agent systems are represented mostly as separate stages; an end-to-end evidence chain is not yet visible from this inventory.
- Production evaluation and reproducibility are recurring concerns, addressed differently by operational deployments and benchmark proposals.

## Initial Research Gaps

See [research gaps](research-gaps.md). These are preliminary observations from triage, not research conclusions.

## Notes / Uncertainties

- The inventory uses lightweight evidence and should not be treated as a substitute for full-paper verification.
- Several PDFs are 2026 papers or author versions; venue, data release, and production details may require checking during formal reading.
- `TOSEM26-CharRCA-Wanglu.pdf` has a filename typo/variant; the title page identifies the paper as **ChatRCA**.
- No paper in this batch clearly confirms use of NetFlow, packets, or traffic traces. Their absence from this inventory is not evidence that the papers never contain such data; it means the first-stage material did not establish it.
- Existing `.gitignore` rules already cover `sources/papers/**/*.pdf`; no broad `*.pdf` rule was added.
