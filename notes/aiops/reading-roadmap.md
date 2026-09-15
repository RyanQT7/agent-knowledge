# AIOps Reading Roadmap

Status: Preliminary

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

## Full-reading Checklist

For each later paper-reading task, verify the lightweight claims against the method, figures, tables, appendices, ground truth, and deployment sections. Create formal notes under `papers/aiops/<paper-id>/notes.md` only after that full-paper task.
