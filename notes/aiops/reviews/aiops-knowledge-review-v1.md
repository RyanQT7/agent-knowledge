Status: completed

# AIOps Knowledge Review v1

## Scope

- [RCAgentBench](../../../papers/aiops/rcagentbench/notes.md)
- [StaR](../../../papers/aiops/star/notes.md)
- [CAUSALDX](../../../papers/aiops/causaldx/notes.md)
- [LLMGuard](../../../papers/aiops/llmguard/notes.md)
- [KAT](../../../papers/aiops/kat/notes.md)

Focus: **Multimodal / Topology-aware / Production RCA**

This review uses the five formal AIOps paper notes. It does not redo the individual full-paper readings or add external literature.

## Evidence Convention

- **Paper-backed fact:** directly reported by a paper and traceable through its formal note to a section, table, figure, or appendix.
- **Cross-paper synthesis:** an abstraction made by comparing the five papers; it is not a standard architecture proposed jointly by them.
- **Current interpretation / open question:** a useful working view that remains subject to revision as the AIOps line grows.

## 1. What I Understand So Far

### Paper-backed facts

The five papers do not solve one identical RCA task:

- RCAgentBench evaluates agent workflows that query metrics, logs, and traces to localize and type injected microservice faults, with process-level metrics (Source: RCAgentBench, Sec. II–V, pp. 2–8).
- StaR learns a stateful dynamic graph from multivariate time series and ranks variables using state-aware exogenous innovations; it has no LLM/Agent loop (Source: StaR, Sec. 3–5, pp. 3–9).
- CAUSALDX starts from rule-generated anomaly observations and performs anomaly-graph `select → expand → verify` search for long-tail and cascading cloud incidents (Source: CAUSALDX, Sec. 3–5, pp. 4–12).
- LLMGuard compiles validated troubleshooting guides into an SOP Checking Tree, then performs deterministic tool checks and evidence-backed diagnosis in a production LMaaS environment (Source: LLMGuard, Sec. IV–V, pp. 4–8).
- KAT retrieves error/context/solution paths from a troubleshooting knowledge graph, adds cross-subsystem context, and generates solutions with an LLM in a commercial telecom deployment (Source: KAT, Sec. IV–VIII, pp. 4–9).

### Cross-paper synthesis

The most useful current abstraction is not “LLM for RCA.” It is:

```text
incident signal
→ evidence and context construction
→ candidate root-cause space
→ structural constraint / search / verification
→ localization and diagnosis
→ explanation or action recommendation
→ feedback and knowledge update where supported
```

The five systems occupy different points in this pipeline. Their differences in input, candidate definition, graph semantics, feedback, and evaluation are as important as their shared use of the word RCA.

## 2. Cross-Paper Relationships

| Paper | Primary layer | Evidence input | Candidate root representation | Structure / constraint | LLM / Agent role | Production claim |
| --- | --- | --- | --- | --- | --- | --- |
| RCAgentBench | Multimodal agent RCA and evaluation | Metrics, logs, traces, system context | Service/pod/node/component and fault type | Call chain, hierarchy, tool outputs | Benchmark contains ReAct, Plan-Execute, Workflow, and multi-agent patterns | Public injected-fault testbed; no production deployment |
| StaR | Metric-based dynamic causal localization | Multivariate time series plus graph/message structure | Metric variables with abnormal exogenous innovations | Dynamic graph, state, causal coefficients | No LLM or Agent | Synthetic/public benchmark; no deployment claim |
| CAUSALDX | Long-tail/cascading diagnosis | Rule-derived anomalies, logs/metrics/tools, expert knowledge | Anomaly nodes plus expandable root hypotheses | Anomaly dependency graph and recursive search | Helper/Module Agents with tools, planning, verification, mitigation | Private production records and human feedback; deployment mode qualified |
| LLMGuard | Production procedure-grounded diagnosis | Alerts, SOP/TSG text, logs, metrics, hardware/network/config checks | Retrieved SOP leaves | SOP Checking Tree and Boolean branch pruning | Multi-role LLM workflow; deterministic online CheckAgent | Production deployment; 84 incidents; >10,000 accelerators |
| KAT | Knowledge-grounded telecom troubleshooting | User/system error text, cases, entities, subsystem context | Retrieved cases/solution paths; no explicit fixed root set | Troubleshooting KG and TBSS subsystem graph | LLM generation; full Agent loop not established | Commercial telecom deployment and longitudinal outcomes |

The relationship is complementary rather than additive in a simple formula. For example, StaR could provide a metric/topology candidate ranking layer for an Agent workflow, but nothing in the five papers proves that the systems can be composed without reworking labels, time semantics, and evidence interfaces.

## 3. Current AIOps RCA Pipeline

### Cross-paper synthesis

A cautious common pipeline is:

```text
Incident / alert / user error / anomaly window
             ↓
Telemetry, knowledge, or tool evidence collection
             ↓
Anomaly or evidence extraction
             ↓
Candidate root-cause generation
             ↓
Topology / dependency / causal / SOP constraint
             ↓
Candidate ranking, search, or verification
             ↓
Root-cause localization
             ↓
Fault diagnosis and explanation
             ↓
Human-gated remediation or solution recommendation
             ↓
Feedback, graph/SOP update, or model adaptation
```

This is not a standard architecture proposed by the papers. Stages can be absent or combined:

- RCAgentBench receives an anomaly window and focuses on evidence tools plus RCA.
- StaR couples state-aware anomaly innovation with root ranking.
- CAUSALDX receives anomaly observations and performs causal search/verification.
- LLMGuard starts from alerts and uses a guide-covered checking procedure.
- KAT starts from an error report and retrieves operational context and solutions.

## 4. Detection, Localization, RCA, Diagnosis, Explanation, and Remediation

### Working distinctions

- **Detection:** determine that a signal, event, or system state is abnormal.
- **Localization:** determine where the fault is, such as a service, node, device, interface, or metric variable.
- **RCA:** determine which candidate cause best explains the incident and its symptoms.
- **Diagnosis:** determine the fault type/mechanism or operational condition.
- **Explanation:** provide evidence and a causal/operational account for the result.
- **Remediation:** recommend or perform an action intended to address the cause.

### Paper-backed comparison

- RCAgentBench separates location accuracy, fault-type accuracy, explanation coverage, and path length; its supplied anomaly window means it is not a standalone detector (Source: Sec. II-A, IV-B, V-A).
- StaR uses state-aware innovations as root evidence, but primarily evaluates causal discovery and root localization, not a general fault-type classifier (Source: Sec. 3.4 and Sec. 4.1).
- CAUSALDX relies on rule-generated initial anomaly observations, then performs RCA/diagnosis and mitigation support; its rules are not the same as the final root-cause decision (Source: Sec. 2.1, 3.1, 4.3).
- LLMGuard is triggered by alerts/symptoms and evaluates diagnosis from SOP checks, not an independent anomaly detector (Source: Sec. III–IV).
- KAT starts from user/system error reports and evaluates solution-answer quality, not detection or physical root-node localization (Source: Sec. V–VII).

### Current interpretation

The most dangerous evaluation error is to treat “detected an abnormal signal” as “identified the root cause.” Batch 1 consistently supports keeping these stages separate, even when a method internally uses anomaly scores as RCA evidence.

## 5. Candidate Root-Cause Definitions

| Paper | What counts as a candidate? | Candidate pruning / expansion | What is not established |
| --- | --- | --- | --- |
| RCAgentBench | Faulty service, pod, node, or component plus fault type in injected cases | Tool evidence, system information, and fault-level hierarchy constrain reasoning; no fixed universal count or explicit pruning algorithm | Open-set and multi-root network candidate protocol |
| StaR | Every modeled metric variable; high state-aware exogenous deviation becomes a root candidate | Ranking by robust innovation score; sparse graph regularization; no separate discrete pruning stage | Direct mapping from metric variables to physical network faults |
| CAUSALDX | Initial anomaly nodes, then newly hypothesized root causes | `Select` narrows attention; `Expand` grows an open-set hypothesis space; `Verify` rejects unsupported candidates | Universal candidate count and complete physical causal graph |
| LLMGuard | Leaves of retrieved, validated SOPs/TSGs | Retrieval, prefix merging, and Boolean checks prune/backtrack | Open-set root discovery outside guide coverage |
| KAT | Retrieved error/context/solution cases and generated solution paths | Entity traversal, path scoring, Top-K selection, and subsystem-neighbor selection reduce context | An explicit numeric root-cause candidate set and root-node ranking protocol |

### Cross-paper synthesis

Candidate-space design is a hidden but central part of RCA. A “root cause” can mean a metric variable, a component, an anomaly node, an SOP leaf, or a retrieved solution case. Accuracy numbers cannot be compared until the candidate universe, multiple-root policy, unknown-root policy, and ground-truth unit are aligned.

## 6. Topology and Graph Semantics

| Paper | What the graph/structure is | Role in the method | Causal status |
| --- | --- | --- | --- |
| RCAgentBench | Microservice call chains, service/pod relationships, fault-level hierarchy | Context, structural prior, and tool/reasoning constraint | Dependency/call structure; not established as a physical causal graph |
| StaR | Dynamic variable graph and learned/message-passing relationships | Model input/scaffold, dynamic causal coefficients, and stateful propagation | Granger-style predictive causal utility; paper explicitly warns this is not automatically physical causality |
| CAUSALDX | Anomaly dependency/causal graph | Organizes select/expand/verify search and back-propagation | Operational anomaly causality; physical causal semantics are not established |
| LLMGuard | SOP Checking Tree | Executable diagnostic procedure and Boolean pruning | Procedural check structure, not a topology graph |
| KAT | TBSS subsystem property graph plus TKG relations | Retrieves directly interacting subsystem context and solution paths | Operational dependency/context, not physical network causality |

### Answer to “what is topology here?”

“Topology-aware” is not one method family in this batch. It may mean a graph-model input, a learned dynamic dependency, a candidate constraint, an anomaly search graph, or a knowledge/context graph. The first question for a new paper should be: *what are the nodes and edges, and what do they do to candidate generation or evidence verification?*

## 7. Multimodal Telemetry and Evidence Fusion

### Paper-backed facts

- RCAgentBench is the only Batch 1 paper that explicitly presents metrics, logs, and traces as a multimodal RCA input and gives each modality a diagnostic tool (Source: Sec. II-B and IV-B, pp. 2–5).
- StaR uses multivariate metric time series and graph structure; this is not conventional heterogeneous telemetry fusion (Source: Sec. 3–4).
- CAUSALDX uses anomaly observations from operational records and product tools including logs/metrics/workload-trace evidence, but does not define one early/feature-level fusion module (Source: Sec. 2.1, Table 3, Sec. 4.3).
- LLMGuard combines alerts, SOP text, log/system checks, hardware/network state, and configuration checks procedurally; the evidence enters through verified tools rather than a single multimodal encoder (Source: Sec. IV).
- KAT combines error text/entities with graph-structured operational knowledge and subsystem context; raw metrics/logs/traces are not explicitly specified as its main input (Source: Sec. IV–V).

### Current synthesis

At least four integration points must be distinguished:

1. **Feature/representation fusion:** heterogeneous telemetry is combined before prediction.
2. **Graph fusion:** telemetry is connected to dependency/topology structure.
3. **Prompt/context augmentation:** retrieved knowledge and context are inserted into an LLM input.
4. **Tool-based fusion:** a workflow queries different sources at runtime and integrates observations.

The current batch mostly gives evidence for tool-based fusion, graph/context augmentation, or metric-plus-graph modeling. It does not yet provide a network-specific multimodal protocol that aligns metrics, syslog, traces, topology, traffic, and NetFlow.

### Evidence roles

- **Metrics:** quantitative deviation, trend, magnitude, and resource state; often useful for detection but not sufficient by themselves for causal explanation.
- **Logs / syslog:** textual error semantics, component context, and event detail; they may identify a fault mechanism but can be noisy or duplicated.
- **Traces:** request path, span timing, and service relationships; they can expose propagation and call-chain context.
- **Topology / knowledge:** constraints and context about which components can interact; not direct evidence unless tied to current observations.

These are working interpretations, not claims that every paper uses each modality in this exact way.

## 8. Causal Reasoning: Strictness and Limits

### Paper-backed facts

StaR explicitly discusses Granger-style predictive causality and states that predictive usefulness is not the same as physical causality; hidden confounders and instantaneous coupling remain limitations (Source: StaR, Sec. 5, p. 9).

CAUSALDX calls its anomaly graph causal and uses it to search and verify operational diagnoses, but the paper does not establish a physical causal identification procedure for every edge (Source: CAUSALDX, Sec. 3.1 and Sec. 4.3).

RCAgentBench uses service call chains and hierarchy as structural context, KAT uses subsystem dependencies for context retrieval, and LLMGuard uses SOP procedures. None should be silently promoted to a physical causal model (Source: the corresponding formal notes, Sec. III–V).

### Current interpretation

The word “causal” in AIOps papers may refer to:

- predictive precedence in time series;
- dependency or propagation structure;
- anomaly-level diagnostic explanation;
- an operational procedure that tests a hypothesis;
- physical mechanism.

The paper must establish the last meaning before a note can claim physical causal discovery. For network research, a learned graph should be compared against known topology and event order, but disagreement with topology is not automatically proof that either side is wrong.

## 9. LLM and Agent Roles

### Paper-backed comparison

- **RCAgentBench:** explicit benchmarked Agent workflows select tools, consume observations, and emit component/type/reasoning outputs. It compares patterns rather than proposing one universal Agent architecture (Source: Sec. IV–V).
- **CAUSALDX:** explicit Helper/Module Agent workflow with planning, product tools, recursive search, verification, and mitigation. This meets the current knowledge-base working distinction for an Agentic RCA workflow (Source: Sec. 4.1–4.4).
- **LLMGuard:** multi-role workflow with SOPAgent, PlanAgent, CheckAgent, and SummaryAgent; runtime checking is deterministic and bounded. It is Agentic without being free-form at every step (Source: Sec. IV).
- **KAT:** LLM-based graph-grounded troubleshooting; it retrieves context and generates a solution, but the paper does not establish a multi-step environment-facing Agent loop. LLM use and knowledge retrieval are insufficient to label it a full Agent (Source: Sec. IV–VII).
- **StaR:** no LLM or Agent; it provides a useful non-LLM structural/temporal RCA contrast.

### Current synthesis

The useful Agent boundary remains:

```text
goal-driven state
→ choose or follow an action/check
→ receive observation or feedback
→ update the next decision
```

An LLM, tool, graph, retrieved context, or multiple named roles may support this loop, but none alone is a sufficient condition. In production AIOps, deterministic execution and human escalation can be part of an Agentic workflow rather than evidence against it.

## 10. Production Data, Scale, and Deployment

| Paper | Production data | Production-scale evidence | Production deployment |
| --- | --- | --- | --- |
| RCAgentBench | No; controlled Chaos-Mesh injections | 10 services, 30 pods, 8 VMs, 400 cases | Not established |
| StaR | Public synthetic/benchmark data | Reports up to 1,000-node latency tests | Not established |
| CAUSALDX | 1,148 private Tencent production incident records, 287 held-out evaluation records | Product/domain scope and workflow cost are reported; Spark-focused | Industrial use/feedback and human-gated mitigation; exact continuous deployment mode unclear |
| LLMGuard | 84 real Company H LMaaS incidents over three months | More than 10,000 accelerators; >1,000-accelerator workloads; latency/cost targets | Yes, live human-on-the-loop production workflow |
| KAT | 54,537 expert-labelled cases plus 3,612 real test errors | Commercial TBSS serving about 35M users and high monthly error volume | Yes, commercial deployment from March 2024 with longitudinal outcomes |

### Key distinction

Production data, production-scale evaluation, and production deployment are three different claims. A large benchmark is not a live deployment; a production dataset does not automatically imply a continuously deployed system; user satisfaction does not equal physical RCA correctness.

## 11. Evaluation Protocol Differences

- **RCAgentBench:** LA-Top1/Top5 for component localization, TA for fault type, explanation coverage, and APL for diagnostic path length (Source: Sec. V-A, pp. 5–6).
- **StaR:** F1/AUC/Hamming for synthetic causal graph recovery, AC@K/AC*@K for root localization, and latency for efficiency (Source: Sec. 4.1 and Appendix A.4/A.7).
- **CAUSALDX:** set-valued root precision/recall, G-Eval explanation dimensions, action/token/latency cost, and operator feedback (Source: Sec. 5.1–5.3).
- **LLMGuard:** location/type accuracy, APL, diagnosis latency, token cost, and resource use; includes SOP/evidence ablations (Source: Sec. V).
- **KAT:** lexical and semantic answer similarity—Jaccard, BLEU, EM, ROUGE-L, BERT-P/R/F1—plus satisfaction and resolution-time outcomes (Source: Sec. VII–VIII).

These metrics measure different objects. A BERT-F1 score for a solution text is not interchangeable with AC@1 for a root variable, and a user satisfaction rate is not an RCA precision score. A future network benchmark should report task-aligned technical correctness, evidence quality, time/cost, and operator safety separately.

## 12. Answers to the Batch Review Questions

### 1. What is the typical AIOps RCA pipeline?

**Cross-paper synthesis:** A defensible working pipeline is `incident trigger → evidence extraction → candidate generation → structural/topological constraint → ranking/search/verification → localization → diagnosis/explanation → human-gated action → feedback`. The five papers implement different subsets and orderings; this is not a standard architecture.

### 2. How are Detection, Localization, RCA, and Diagnosis different?

**Current working definition:** Detection finds abnormality; localization identifies where; RCA identifies the cause that explains it; diagnosis identifies the fault mechanism/type. The papers support keeping these outputs separate, especially RCAgentBench's LA/TA/Explainability split and the alert/anomaly assumptions in StaR, CAUSALDX, LLMGuard, and KAT.

### 3. What are the candidate root causes in the five papers?

**Paper-backed comparison:** RCAgentBench uses injected service/pod/node/component faults; StaR uses metric variables; CAUSALDX uses anomaly nodes plus expanded hypotheses; LLMGuard uses SOP leaves; KAT retrieves cases/solution paths rather than defining an explicit root set. No common candidate universe exists.

### 4. What are the different uses of topology?

**Cross-paper synthesis:** Topology/structure can be a graph-model input, dynamic learned dependency, anomaly search graph, ranking prior, context graph, or procedure tree. The node/edge semantics and role must be recorded before comparing methods.

### 5. How is multimodal telemetry fused?

**Paper-backed answer:** RCAgentBench performs runtime tool-based integration of metrics/logs/traces. CAUSALDX and LLMGuard integrate multiple operational evidence sources through anomaly/tool or SOP workflows; KAT performs graph/context augmentation; StaR uses metrics plus graph state. The batch does not establish one common early/feature-level fusion method.

### 6. What evidence do metrics, logs, and traces provide?

**Current synthesis:** Metrics provide quantitative deviation; logs provide textual/component/fault clues; traces provide path and timing relationships. Their value depends on time alignment, entity mapping, missingness, and provenance. These roles should be tested rather than assumed to be universally complementary.

### 7. Which methods depend on anomaly detection?

**Paper-backed answer:** RCAgentBench receives an anomaly window but performs tool-level anomaly evidence extraction; StaR derives root evidence from model innovations; CAUSALDX receives rule-derived anomalies; LLMGuard starts from alerts and checks; KAT starts from error reports. None of the five gives a complete, common detection-to-RCA end-to-end evaluation.

### 8. Which methods use causal reasoning, and is “causal” strict?

**Paper-backed answer:** StaR has the clearest formal time-series causal-discovery formulation but qualifies it as predictive rather than necessarily physical. CAUSALDX uses anomaly causal/dependency reasoning for diagnosis. RCAgentBench, LLMGuard, and KAT use structural or operational relations. “Causal” is therefore not a uniform guarantee across the batch.

### 9. What role does the LLM play?

**Paper-backed answer:** It can select tools and explain evidence (RCAgentBench), orchestrate search and verification (CAUSALDX), parse/plan/summarize around deterministic checks (LLMGuard), or generate a graph-grounded troubleshooting answer (KAT). StaR has no LLM. Gains cannot be attributed to reasoning alone when tools, rules, graphs, and knowledge also change.

### 10. Which papers are truly Agentic RCA?

**Current working classification:** RCAgentBench's evaluated workflows, CAUSALDX's Helper/Module loop, and LLMGuard's multi-role check workflow are Agentic under the current knowledge-base distinction, with different degrees of runtime freedom. KAT is LLM-based troubleshooting with Agent status not established. StaR is not Agentic. The classification is a working interpretation, not a universal paper taxonomy.

### 11. How should production data/evaluation/deployment be distinguished?

**Paper-backed answer:** RCAgentBench and StaR are controlled/public evaluation; CAUSALDX uses private production records and human feedback; LLMGuard reports live production diagnosis with SRE gating; KAT reports commercial deployment and longitudinal operational outcomes. The three axes must be reported separately.

### 12. What are the evaluation differences?

**Paper-backed answer:** The batch spans component top-k accuracy, fault-type accuracy, causal-edge recovery, root-set precision/recall, explanation quality, answer semantic similarity, path length, latency, cost, and user outcomes. They are not directly comparable without task/candidate/ground-truth normalization.

### 13. Which methods are most transferable to network infrastructure RCA?

**Current interpretation:** LLMGuard's verified tools, deterministic branching, evidence chain, and human gating; CAUSALDX's long-tail/cascade framing and verification; StaR's stateful/dynamic dependency modeling; RCAgentBench's modality/process evaluation; and KAT's evolving operational knowledge/context retrieval are all useful. No method transfers as-is.

### 14. Which microservice or domain assumptions do not transfer?

**Paper-backed/current interpretation:** service/pod/call-chain assumptions, Spark/HDFS/YARN product rules, LMaaS SOP coverage and quasi-static checks, TBSS subsystem graphs and reference solutions, injected-fault distributions, Granger assumptions, and private expert labels all require validation or redesign for devices, interfaces, links, optical modules, traffic, and NetFlow.

### 15. What are the largest current gaps relative to my research?

**Current interpretation:** The largest gaps are a network-specific multimodal evidence protocol, physical/dynamic topology semantics, traffic/NetFlow integration, open-set and multi-root ground truth, isolation of LLM value from tools/knowledge, and safe end-to-end evaluation from detection through human-gated remediation.

## 13. Implications for My Research

### Ideas worth learning from

- Use explicit candidate-space and ground-truth definitions before comparing RCA methods.
- Treat topology as a typed, potentially uncertain structure rather than a generic graph feature.
- Separate evidence collection from candidate ranking and verification.
- Preserve source-specific evidence and an auditable reasoning/action trace.
- Combine technical metrics with latency, cost, path length, escalation, and operator usefulness.
- Make unknown coverage and human review explicit rather than forcing every case into a known label.
- Treat operational knowledge as a lifecycle: retrieve, ground, verify, update, and retire.

### Ideas that probably do not transfer directly

- Microservice call graphs and service/pod fault levels as a substitute for physical network topology.
- Spark/LMaaS/TBSS-specific rules, SOP leaves, and solution labels.
- A metric-variable learned graph as an automatically correct physical causal graph.
- Text-answer similarity as a standalone measure of network root-cause correctness.
- Injected fault distributions as a proxy for the full diversity of field incidents.

### Evaluation designs worth adopting

- Hierarchical Top-1/Top-k localization for device/interface/link/module levels.
- Set-valued precision/recall for multiple and unknown roots.
- Modality-specific evidence coverage and provenance checks.
- Diagnostic path length, time-to-diagnosis, token/tool cost, and escalation rate.
- Separate detection, localization, diagnosis, explanation, and remediation outcomes.
- Human-gated safety evaluation for any action recommendation.

### Missing capabilities in the current literature slice

- A network-specific benchmark combining physical topology, metrics, syslog, traces where available, traffic/NetFlow, and configuration.
- A shared protocol for telemetry time alignment, missingness, conflicting evidence, and candidate provenance.
- Ground truth that distinguishes physical initiating faults from predictive root variables and downstream symptoms.
- A common ablation isolating LLM reasoning from tool coverage, expert rules, graph quality, and retrieval context.
- Evaluation of safe unknown-root escalation and remediation under changing topology.

### Potential research opportunities

These are hypotheses for later investigation, not conclusions established by this batch:

1. Topology- and evidence-grounded open-set RCA for network infrastructure.
2. Stateful temporal reasoning combined with physical topology and traffic evidence.
3. Deterministic or verifiable tool orchestration around an LLM for high-stakes diagnosis.
4. A production-oriented network RCA benchmark with process, evidence, and safety metrics.

## 14. Common Misconceptions Corrected

- **Detection = RCA:** false. An anomaly or alert can be the starting observation; the root cause is a separate output.
- **Topology = physical causality:** false. Service, anomaly, learned predictive, SOP, and subsystem graphs have different semantics.
- **LLM = Agent:** false. KAT uses an LLM without establishing the full Agent loop; StaR has no LLM/Agent.
- **Tool use = Agent:** false. A tool can be called in a static or bounded workflow; target-driven state/observation/decision behavior matters.
- **Every multimodal label means feature fusion:** false. RCAgentBench uses runtime tool integration; KAT and LLMGuard use different context/procedure integration.
- **Production data = production deployment:** false. CAUSALDX, LLMGuard, and KAT support different combinations of these claims.
- **StaR memory = Agent memory:** false. StaR's state is model temporal state for time-series reconstruction and causal ranking.
- **Anomaly graph causal = physical causal:** not established. CAUSALDX's graph is an operational diagnostic structure.
- **KAT's persistent graph = Agent memory:** false. It is persistent operational knowledge/context and update state, not automatically episodic Agent memory.
- **Human satisfaction = root-cause correctness:** false. Operational usefulness and technical correctness are related but distinct outcomes.

## 15. Current Mental Model

### Cross-paper synthesis

The current working mental model for network-oriented AIOps RCA is:

```text
Incident / alert / user report
        ↓
Evidence collection and provenance
(metrics, syslog/logs, traces, topology, traffic, knowledge, tools)
        ↓
Detection or anomaly extraction
(may be upstream, assumed, or integrated)
        ↓
Candidate root-cause space
(component, metric, anomaly, procedure leaf, or open hypothesis)
        ↓
Typed structure and constraints
(physical topology, dependency, causal evidence, SOP, knowledge graph)
        ↓
Ranking / search / verification
(model score, Agent reasoning, deterministic checks, human review)
        ↓
Root localization and fault diagnosis
        ↓
Explanation and evidence chain
        ↓
Safe, human-gated remediation or recommendation
        ↓
Feedback and controlled knowledge/model update
```

This is a cross-paper abstraction, not a standard architecture. A future network system may omit some stages, run them iteratively, or use different modules for metric ranking, tool execution, and explanation.

## 16. What These Papers Explain Well

- Why root-cause evaluation needs a clear candidate universe and ground truth.
- Why topology/graph semantics must be stated rather than inferred from a label.
- Why tool and knowledge coverage can dominate the apparent benefit of a larger LLM.
- Why state/history matters for delayed effects and why model state is not automatically Agent memory.
- Why production diagnosis requires latency, cost, evidence, escalation, and maintenance considerations.
- Why long-tail and cascading incidents need different handling from closed-set fault classification.

## 17. What They Do Not Yet Explain

- A unified network-specific pipeline over metrics, syslog, traces, topology, traffic, and NetFlow.
- Reliable physical-causality claims under incomplete, changing, and noisy topology.
- A common way to label multiple roots, unknown faults, onset intervals, and downstream symptoms.
- Whether LLMs improve root-cause correctness after controlling for tools, rules, retrieval, and graph quality.
- How to update, forget, or audit operational knowledge when network configuration and fault patterns evolve.
- Safe autonomous remediation with reproducible evidence and clear rollback semantics.

## 18. Open Questions

The detailed, non-deleted question history is maintained in [AIOps questions](../questions.md). After this review, the highest-priority open items are:

- How can a network candidate space cover device/interface/link/module levels, multiple roots, and unknown faults?
- How can physical topology, learned temporal dependency, and traffic paths be reconciled without conflating prediction with causality?
- How should heterogeneous evidence be time-aligned, attributed, and verified when modalities disagree?
- What common benchmark can isolate LLM reasoning from tool/knowledge/orchestration effects?
- How should stale, contradictory, or incomplete operational knowledge trigger escalation rather than silently change a diagnosis?
- Which technical and human-safety metrics should gate remediation recommendations?

## 19. Next Learning Priorities

Based on the observed gaps rather than popularity, the next priorities are:

1. **Network-specific multimodal evidence and time alignment:** metrics, syslog, traces, traffic/NetFlow, configuration, and provenance.
2. **Physical and dynamic topology-aware RCA:** mapping graph structure to device/interface/link semantics and handling topology changes.
3. **Open-set, multi-root diagnosis and ground truth:** unknown faults, cascading symptoms, and hierarchical evaluation.
4. **Reliable tool- and knowledge-grounded Agent RCA:** verified tools, structured plans, uncertainty, escalation, and safe execution.
5. **Production RCA evaluation and remediation safety:** correctness, evidence, latency, cost, operator effort, rollback, and deployment drift.

## 20. Source Grounding

This review is grounded in the formal notes and their cited local-paper locations:

- [RCAgentBench note](../../../papers/aiops/rcagentbench/notes.md): Sec. II–V and Table I–V, especially multimodal tools, hierarchy, LA/TA/Explainability/APL, and ablations.
- [StaR note](../../../papers/aiops/star/notes.md): Sec. 3–5, Tables 1–5, and Appendices A.2/A.4/A.5/A.7–A.9, especially dynamic graph, state, AC@K, latency, and causality limits.
- [CAUSALDX note](../../../papers/aiops/causaldx/notes.md): Sec. 2–6, Algorithm 1, Tables 4–8, and Figs. 10–12, especially anomaly graph, AGRCS, verification, production records, and feedback.
- [LLMGuard note](../../../papers/aiops/llmguard/notes.md): Sec. III–V and Figs. 3–6/Tables I–II, especially SOPCT, deterministic execution, 84 incidents, production scale, and latency/cost.
- [KAT note](../../../papers/aiops/kat/notes.md): Sec. IV–X, Tables II–III, and Figs. 7–10, especially TKG, subsystem context, continuous improvement, production deployment, and semantic-answer evaluation.

All quantitative comparisons above are scoped to the paper and table/figure cited in the corresponding formal note. Cross-paper conclusions are explicitly marked as synthesis or interpretation.
