# AIOps Reading Roadmap

Status: Research-question-driven re-ranking added; 10 papers fully read and 8 papers remain triage-only

This roadmap turns the inventory into thematic full-paper batches. Each batch is intentionally small enough for paper-level notes and a subsequent cross-paper review. The order is based on relevance to network/infrastructure diagnosis and on the knowledge dependencies between topics, not on a claim about paper quality.

## Batch 1 — Multimodal, Topology-aware, and Production RCA

**Papers:**

- [RCAgentBench](<../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf>)
- [StaR](<../../sources/papers/AIOps_papers/KDD26-StaR- Stateful Dynamic-Graph Root Cause Analysis throughMemory-Enhanced Causality Discovery.pdf>)
- [CAUSALDX](<../../sources/papers/AIOps_papers/TKDE26-CAUSALDX- Diagnosing Long-Tail and Cascading Cloud Incidents with LLM-Guided Causal Reasoning.pdf>)
- [LLMGuard](<../../sources/papers/AIOps_papers/DSN26-LLMGuard_Multi-Agent_Fault_Diagnosis_for_Reliable_Language-Model-as-a-Service.pdf>)
- [KAT](<../../sources/papers/AIOps_papers/INFOCOM26-KAT_Knowledge-Context_Augmentation_for_Evolving_LLM-Based_Telecom_Troubleshooting.pdf>)

**Why this batch:** It gives a direct comparison between multimodal RCA evaluation, dynamic topology/causal modeling, long-tail cloud diagnosis, deterministic production agents, and telecom knowledge/context augmentation.

**Expected knowledge gain:** A first evidence-based picture of how telemetry, topology, causal reasoning, operational knowledge, and LLM/agent workflows can meet in infrastructure diagnosis.

## Batch 2 — Agentic Incident Management, Troubleshooting, and Human Assistance

**Papers:**

- [Comfey](<../../sources/papers/AIOps_papers/FSE26-An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure.pdf>)
- [AIM](<../../sources/papers/AIOps_papers/FSE26-Leveraging LLMs for Alert Summarization and Mitigation Plan Generation.pdf>)
- [StepFly](<../../sources/papers/AIOps_papers/FSE26-StepFly- Agentic Troubleshooting Guide Automation for Incident Diagnosis.pdf>)
- [TSGen](<../../sources/papers/AIOps_papers/FSE26-TSGen- Automated Troubleshooting Guide Generation.pdf>)
- [ChatRCA](<../../sources/papers/AIOps_papers/TOSEM26-CharRCA-Wanglu.pdf>)

**Why this batch:** These papers cover the operational path from incident routing and alert summarization to guide generation, guide execution, mitigation, and human-in-the-loop RCA.

**Expected knowledge gain:** A clearer separation between diagnosis, operational knowledge, execution, remediation, and human escalation.

## Batch 3 — Knowledge Anchoring, Agent Reliability, and Reproducible Evaluation

**Papers:**

- [Cloud Intelligence / AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>)
- [Cloud-OpsBench](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>)
- [FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>)
- [HARNESSFIX](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>)
- [Hierarchical Failure Attribution](<../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>)

**Why this batch:** It studies how operational knowledge, state snapshots, traces, causal structure, and repair operators can make agentic systems safer and more diagnosable.

**Expected knowledge gain:** Better vocabulary for distinguishing infrastructure faults from agent/harness faults and for evaluating process reliability.

## Batch 4 — Time-series and Metric Anomaly Detection Foundations

**Papers:**

- [TFC](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>)
- [TFT-GCN](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>)
- [Foundation Models for Time Series](<../../sources/papers/AIOps_papers/KDD26-Foundation Models for Time Series Analysis- Concepts,Methodologies, and Applications.pdf>)

**Why this batch:** It provides the detection and time-series background needed to understand what evidence an RCA system receives before any LLM/agent reasoning begins.

**Expected knowledge gain:** A more precise bridge from anomaly signals and multivariate temporal structure to downstream incident diagnosis.

## Recommended First Batch

Start with **Batch 1**. The five papers are the most aligned with the current research direction because they combine:

- multimodal telemetry or operational evidence;
- topology and causal structure;
- production cloud or telecom settings;
- LLM/agent diagnosis with explicit limits and evaluation concerns.

Do not treat all five as one algorithmic family. The value of the batch is the contrast between classical causal modeling, benchmark design, production knowledge grounding, and agentic reasoning.

## Priority Summary

- **P0:** LLMGuard, KAT, RCAgentBench, StaR, CAUSALDX.
- **P1:** Comfey, AIM, StepFly, Cloud-OpsBench, TFC, ChatRCA.
- **P2:** Cloud Intelligence/AIOps 2.0, TSGen, FlowFixer, HARNESSFIX, hierarchical failure attribution, Foundation Models for Time Series, TFT-GCN.
- **P3:** None for this first pass; the P2 papers remain useful background or specialized follow-up material rather than being discarded.

## Research-question-driven Roadmap

The original Batch 1–4 plan above is retained as the historical triage plan. The section below is the current reading plan after mapping the eight unread papers to the working Hybrid RCA architecture and the three research questions. It supersedes the old P0–P3 labels for future scheduling.

### Current Hybrid RCA architecture

This is a cross-paper working architecture, not a standard pipeline established by any one paper:

```text
Deterministic / ML Detection
→ Evidence Provenance
→ Topology-constrained Candidate Space
→ Bounded LLM / Agent Investigation
→ Independent Verification
→ Human-gated Remediation
→ Recovery Verification
```

For the re-triage below, the architecture layers are:

- **A.** Telemetry / evidence collection
- **B.** Evidence alignment / provenance
- **C.** Detection
- **D.** Candidate-space construction
- **E.** Candidate pruning
- **F.** Physical topology
- **G.** Dynamic dependency / causality
- **H.** RCA ranking / reasoning
- **I.** LLM / Agent investigation
- **J.** Verification
- **K.** Remediation
- **L.** Recovery verification
- **M.** Production evaluation

### Current research questions

- **RQ1 — Multimodal Evidence Alignment:** How can metrics, syslog, traffic/NetFlow, configuration, and physical topology be aligned, provenance-preserving, and verifiable?
- **RQ2 — Candidate Space:** How can Network RCA support large-scale, open-set, and multi-root candidate spaces?
- **RQ3 — Verified Remediation:** How can agentic remediation be verifiable, reversible, and human-gated?

### Re-triage of the eight remaining papers

The judgments below are lightweight and remain provisional. They use the existing inventory plus the PDF title page, abstract, introduction, and necessary method overview; none of these papers has received a formal full-paper note yet.

| # | Paper | Architecture mapping | RQ1 | RQ2 | RQ3 | Evidence Provenance | Candidate-space | Verification / remediation | Network transfer | New priority | Research-driven batch |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 1 | [Diagnosis-Driven Automatic Repair / FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>) | **Primary:** J Verification, K Remediation. **Secondary:** D/E workflow-failure attribution, H/I diagnosis. | **Medium** — It normalizes heterogeneous workflow execution traces and binds assertions to workflow nodes, but does not align network telemetry. | **Medium** — It localizes responsible workflow nodes and filters repair candidates, but this is not a large or open-set infrastructure root-cause universe. | **High** — Symbolic specifications, pre-execution feasibility checks, dynamic verification, and targeted repair directly address verified changes. | **Medium** — The symbolic trace and node assertions provide structured evidence, but provenance is confined to the workflow/harness setting. | **Medium** — It has a failure-node space and repair-candidate filtering, not device/interface/link enumeration. | **High** — Repair is coupled to static constraints and dynamic verification; rollback and network recovery are not established. | **Low** — The diagnosis/repair discipline may transfer to agent or configuration validation, but the workflow nodes and tools are not network entities. | **R0** | **Research-driven Batch 3** |
| 2 | [Cloud Intelligence / AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>) | **Primary:** B Evidence / knowledge anchoring, I investigation. **Secondary:** J verification, K bounded action, M governance/evolution. | **High** — Operational Knowledge Artifacts are anchored to operational signals and control points with scope, evidence, versioning, and lifecycle metadata; the paper is conceptual. | **Medium** — Preconditions, decision points, and service hierarchy can bound an investigation, but no explicit candidate-generation or pruning algorithm is given. | **High** — It explicitly proposes bounded/auditable actions, safety constraints, validation, drift handling, and escalation, but provides no independent empirical proof in this paper. | **High** — Anchors, ownership, versions, evidence/decision points, and execution provenance are central to the proposal. | **Medium** — It can constrain candidate and action scope through knowledge artifacts, but does not define a root-cause candidate space. | **High** — Validation and governed action are first-class, while actual remediation success remains unclear. | **Medium** — The knowledge-anchor and governance ideas can generalize to network operations, but the examples assume cloud-service monitors, dependencies, and runbooks. | **R0** | **Research-driven Batch 3** |
| 3 | [Cloud-OpsBench / State Snapshot](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>) | **Primary:** M Production Evaluation, J process verification. **Secondary:** A/B frozen evidence state, I tool-mediated investigation. | **High** — Immutable snapshots preserve historical metrics/logs together with control-plane and data-plane state and deterministic tool responses; this supports evidence reproducibility rather than alignment itself. | **Low** — It evaluates interactive information seeking but does not define a Network RCA candidate universe or pruning method. | **High** — Process-centric trajectory auditing and deterministic tool feedback make grounding and verification measurable, although the proposed scope is read-only diagnosis rather than remediation. | **High** — The frozen state, mocked interface, and trajectory record provide explicit evidence context and repeatable provenance for evaluation. | **Low** — Candidate-space construction is outside the paper’s main contribution. | **High** — It strongly supports verification/evaluation of investigation behavior, not actual repair, rollback, or recovery. | **Medium** — Snapshot/replay and process metrics are portable, but Kubernetes state and mocked interfaces may miss network permissions, latency, and physical effects. | **R0** | **Research-driven Batch 3** |
| 4 | [From Flat Logs to Causal Graphs / CHIEF](<../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>) | **Primary:** G Dynamic dependency / causality, H RCA reasoning. **Secondary:** D/E hierarchical candidate pruning, J attribution verification. | **Medium** — It parses observation/thought/action/result traces and explicit data dependencies, but its evidence is multi-agent logs rather than metrics/syslog/traffic alignment. | **High** — A hierarchical causal graph, oracle-guided backtracking, and counterfactual screening explicitly reduce a failure-attribution search space; the candidates are agent-step pairs, not network entities. | **Medium** — Virtual oracles and counterfactual checks verify attribution, but the paper does not establish remediation, rollback, or recovery verification. | **Medium** — The graph preserves step-level and dependency evidence, but source/entity/time provenance is not the Network telemetry problem. | **High** — Hierarchy, top-down search, and causal screening are directly relevant to structured candidate reduction. | **Medium** — Attribution verification is substantial; remediation is outside the stated scope. | **Medium** — Hierarchical causal attribution could inform network RCA, but multi-agent execution assumptions and counterfactual action semantics may not transfer. | **R0** | **Research-driven Batch 3** |
| 5 | [From Failed Trajectories to Reliable LLM Agents / HARNESSFIX](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>) | **Primary:** B runtime-evidence alignment, J verification. **Secondary:** I harness investigation, K scoped repair. | **Medium** — HTIR aligns trajectory steps and links with harness artifacts, which is useful provenance discipline but not cross-modal infrastructure telemetry. | **Medium** — It attributes failures to steps and harness layers and scopes repair operators; it does not enumerate physical/network root causes. | **High** — Scoped repair, regression-aware validation, and governance-oriented harness layers provide a strong reliability reference. | **High** — HTIR explicitly connects runtime evidence to editable implementation artifacts and records step-level effects. | **Medium** — Failure-step/layer attribution is a bounded candidate problem, but not a Network RCA candidate space. | **High** — Validation and regression checks are central; autonomous operational remediation is not evaluated. | **Low** — The method can transfer to the agent-control-plane portion of Network AIOps, but not directly to device/link diagnosis. | **R1** | Later reliability batch |
| 6 | [TFC — Temporal–Frequency–Curvature Fusion](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>) | **Primary:** C Detection. **Secondary:** A metric-evidence extraction. | **Medium** — It supplies complementary temporal, frequency, and curvature evidence for metric detection, but is single-modal and has no cross-source provenance. | **Low** — It produces anomaly scores/labels rather than RCA candidates or open-set/multi-root hypotheses. | **None** — The paper does not address verification or remediation. | **Medium** — Derived evidence channels are explicit, but evidence source, entity binding, and audit provenance are not its focus. | **Low** — No candidate root-cause construction or pruning is presented. | **Low** — Detection evaluation is useful upstream, but it is not RCA/remediation verification. | **Medium** — The detection front-end may transfer to network metrics, while benchmark patterns and labels may not represent operational network faults. | **R1** | Later detection batch |
| 7 | [TFT-GCN](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>) | **Primary:** C Detection. **Secondary:** A metric-evidence extraction, G-like learned cross-variable dependency. | **Medium** — Temporal/spectral features and cross-variable associations may improve metric evidence, but the model does not align heterogeneous telemetry sources. | **Low** — A learned cross-variable graph is not a root-cause candidate universe or pruning procedure. | **None** — No remediation or independent RCA verification is addressed. | **Medium** — It exposes time/frequency/cross-variable representations, without operational provenance or conflict handling. | **Low** — Candidate enumeration and RCA are outside scope. | **Low** — Benchmark detection metrics do not verify a root cause or action. | **Medium** — Multivariate network metrics are a plausible target, but the learned graph is not necessarily physical topology or causality. | **R1** | Later detection batch |
| 8 | [Foundation Models for Time Series](<../../sources/papers/AIOps_papers/KDD26-Foundation Models for Time Series Analysis- Concepts,Methodologies, and Applications.pdf>) | **Primary:** A/C time-series representation and detection background. **Secondary:** possible modality-fusion background. | **Medium** — The tutorial covers time-series foundation-model pipelines and modality fusion at a survey level, but not concrete operational evidence alignment. | **Low** — It does not define RCA candidates or pruning. | **None** — It is a tutorial/overview, not a verification or remediation workflow. | **Low** — Provenance, entity alignment, and auditability are not the focus. | **Low** — No candidate-space mechanism. | **None** — No agentic verification or remediation evidence. | **Medium** — It may inform metric/traffic representation choices, but generic time-series coverage does not establish Network RCA value. | **R2** | Later background batch |

### Re-ranked priority

The new order is based on research-question coverage and architectural leverage, not on the papers’ original triage batch or title-level popularity.

#### R0 — Read next

- [Cloud-OpsBench / State Snapshot](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>) — strongest immediate bridge from evidence state and tool interaction to reproducible verification.
- [Cloud Intelligence / AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>) — gives a knowledge/provenance and governance lens for bounded operational agents, with the caveat that it is a position paper.
- [CHIEF / Hierarchical Failure Attribution](<../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>) — most directly useful for hierarchical candidate reduction and causal attribution, while remaining outside physical Network RCA.
- [FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>) — provides a concrete verification-to-repair pattern for the RQ3 reliability boundary.

#### R1 — Read after R0

- [HARNESSFIX](<../../sources/papers/AIOps_papers/From_Failed_Trajectories_to_Reliable_LLM_Agents_Diagnosing_and_Repairing_Harness_Flaws.pdf>) — deepens evidence-to-runtime-artifact alignment and regression-aware agent reliability.
- [TFC](<../../sources/papers/AIOps_papers/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf>) — strengthens the detection/evidence front-end that supplies downstream RCA.
- [TFT-GCN](<../../sources/papers/AIOps_papers/TKDE26-TFT-GCN_A_Time-Frequency_Based_Model_for_Time_Series_Anomaly_Detection.pdf>) — adds a related multivariate temporal/spectral and learned cross-variable perspective; read after TFC unless network-metric detection becomes urgent.

#### R2 — Useful background, not current bottleneck

- [Foundation Models for Time Series](<../../sources/papers/AIOps_papers/KDD26-Foundation Models for Time Series Analysis- Concepts,Methodologies, and Applications.pdf>) — useful for representation and transfer context, but the short tutorial does not directly close RQ1–RQ3.

#### R3 — Temporarily retain

None. Every remaining paper has a plausible later use, but the R2 tutorial should not delay the research-driven Batch 3.

### Recommended Research-driven Batch 3

**Focus: Evidence-grounded, candidate-constrained, and verifiable RCA for operational/agentic systems**

Read these four papers together:

1. [Cloud-OpsBench / State Snapshot](<../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>)
2. [Cloud Intelligence / AIOps 2.0](<../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>)
3. [CHIEF / Hierarchical Failure Attribution](<../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>)
4. [FlowFixer](<../../sources/papers/AIOps_papers/Diagnosis-Driven_Automatic_Repair_for_Agentic_Workflow_via_Symbolic_Inference.pdf>)

This batch is intentionally complementary rather than homogeneous: Cloud-OpsBench contributes reproducible state and process evaluation; Cloud Intelligence contributes anchored operational knowledge and bounded governance; CHIEF contributes hierarchical causal candidate reduction; and FlowFixer contributes symbolic diagnosis, repair scoping, and verification. Together they cover the current architecture gap from trustworthy evidence and candidate control to verified action, while leaving physical network transfer as an explicit question.

**Reading this batch should help answer:**

- **RQ1:** What must be frozen, anchored, structured, and audited before an LLM/Agent can consume operational evidence reliably?
- **RQ2:** How can hierarchical, dependency-aware, or symbolically constrained candidate spaces prevent unconstrained root-cause guessing?
- **RQ3:** Which checks belong before action, during verification, and after a proposed repair, and where should human approval remain mandatory?

### Later research-driven batches

#### Later Batch A — Network telemetry detection and relational evidence

**Papers:** TFC, TFT-GCN

**Why:** These papers can clarify how temporal, spectral, curvature, and cross-variable evidence should be made stronger before it enters the RCA candidate pipeline. They do not by themselves solve multimodal alignment, physical topology, or root-cause attribution.

#### Later Batch B — Time-series foundation-model background

**Paper:** Foundation Models for Time Series

**Why:** Read for representation, pretraining, transfer, and modality-fusion vocabulary after the more direct RQ1–RQ3 papers. Its tutorial status means conclusions about Network AIOps should remain modest.

### Uncertainties to resolve during full reading

- **Cloud Intelligence / AIOps 2.0** is a position paper; its knowledge-anchor and governance mechanisms are architectural proposals, not a complete empirical validation of Network RCA.
- **Cloud-OpsBench** presents a state-snapshot evaluation paradigm and prototype direction; snapshot fidelity, benchmark scale, and remediation coverage require full-paper verification.
- **CHIEF, FlowFixer, and HARNESSFIX** operate on agent/workflow traces rather than physical network telemetry. Their transfer value is methodological and must not be treated as evidence that they solve RQ1 or RQ2 in network settings.
- **TFC, TFT-GCN, and the time-series tutorial** inform the upstream detection/representation layer, but none should be read as an RCA, topology, or remediation method without further evidence.

All eight papers remain `Full Reading: Pending` in the inventory. This roadmap update does not create formal paper notes, modify Concepts, or change the research-gaps file.

## Full-reading Checklist

For each later paper-reading task, verify the lightweight claims against the method, figures, tables, appendices, ground truth, and deployment sections. Create formal notes under `papers/aiops/<paper-id>/notes.md` only after that full-paper task.
