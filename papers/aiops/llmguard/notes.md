Status: Full Reading: Completed

# LLMGuard: Multi-Agent Fault Diagnosis for Reliable Language-Model-as-a-Service

## 1. Metadata

- Title: LLMGuard: Multi-Agent Fault Diagnosis for Reliable Language-Model-as-a-Service
- Authors: Yuedong Zhong, Guangba Yu, Yujie Huang, QunChao Fu, Rui Ren, Cong Feng, Yongqiang Yang, Michael R. Lyu
- Year: 2026
- Venue: IEEE International Conference on Dependable Systems and Networks (DSN) 2026
- URL / DOI: https://doi.org/10.1109/DSN69566.2026.00018
- Local File: [LLMGuard PDF](../../../sources/papers/AIOps_papers/DSN26-LLMGuard_Multi-Agent_Fault_Diagnosis_for_Reliable_Language-Model-as-a-Service.pdf)
- Paper ID: `llmguard`

## 2. One-Sentence Summary

LLMGuard digitizes validated troubleshooting guides into a structured SOP Checking Tree and uses LLMs for semantic parsing, retrieval, plan synthesis, and summarization while keeping online diagnosis deterministic, evidence-backed, and human-gated for high-stakes actions.

## 3. Problem Setting

### Paper states

The paper addresses fault diagnosis in large-scale language-model-as-a-service (LMaaS) infrastructure. Conventional conversational diagnosis agents can be non-deterministic, repeatedly inspect expensive raw logs, hallucinate unsupported causes, and fail to satisfy production time-to-insight requirements. The target environment contains hardware, network, configuration, and workload failures in large accelerator deployments (Source: Abstract; Sec. I–III, pp. 1–4).

The paper argues that useful production diagnosis must make observations reproducible and the evidence chain auditable, while reducing unnecessary LLM loops and observation cost (Source: Sec. III, pp. 2–4; Sec. V-D, p. 7).

### My interpretation

LLMGuard is primarily a diagnosis-and-evidence orchestration system, not a new anomaly detector. Its central design choice is to move much of runtime control from free-form LLM action selection into a structured troubleshooting procedure whose checks have deterministic Boolean outcomes.

## 4. AIOps Task

- Detection: **Trigger-based rather than a new detector.** Alerts or symptoms initiate diagnosis; the paper does not present a standalone anomaly-detection model (Source: Sec. III–IV, pp. 2–6).
- RCA: **Yes.** The system identifies the fault/root cause represented by a leaf in the checking tree (Source: Sec. IV-C–D, pp. 4–6).
- Localization: **Yes, operationally.** It narrows the failing check and associated subsystem/hardware/network condition; the paper evaluates location accuracy (Source: Sec. V-A, pp. 6–7).
- Diagnosis: **Yes.** Fault type and failure explanation are generated from SOP checks and evidence (Source: Sec. IV-D, p. 6).
- Prediction: No.
- Remediation: **Support with human gating.** The diagnosis summary provides a root cause and evidence; high-stakes mitigation is validated by an SRE rather than autonomously executed by the paper's workflow (Source: Sec. V-D and Fig. 6, pp. 7–8).

The boundary is:

```text
alert / symptom
→ retrieve relevant troubleshooting guides
→ synthesize a structured checking tree
→ execute verified checks deterministically
→ prune/backtrack through candidate paths
→ identify root-cause leaf
→ summarize evidence and request human action when needed
```

## 5. Failure / Incident Setting

The system targets LMaaS training and inference failures, including accelerator hardware issues, network/link problems, configuration errors, and workload/runtime failures. The paper reports SOP examples involving `ping`/`dmesg`, accelerator utilization, AI Core frequency, HCCS links, HCCL environment variables, CUDA mismatch, and KV-cache conditions (Source: Sec. IV-A–B, pp. 4–5; Fig. 6, p. 8).

The evaluation uses 84 real incidents from Company H's production LMaaS environment over three months: 46 training incidents and 38 inference incidents. Senior SRE post-mortems and troubleshooting guides provide the root-cause ground truth (Source: Sec. V-A, p. 6).

## 6. Data Modalities

- Metrics: **Yes, through verified infrastructure checks.** Examples include hardware utilization and accelerator/link state; the paper does not define one standardized metric-stream fusion model (Source: Sec. IV-B, pp. 4–5).
- Logs: **Yes.** Log checks and system diagnostics such as `dmesg` are represented in SOP steps and evidence (Source: Sec. IV-B, p. 5; Sec. V-D, p. 7).
- Traces: No separate distributed-trace modality is described.
- Alarms: **Yes.** Alerts/symptoms trigger retrieval and diagnosis (Source: Sec. III–IV, pp. 2–5).
- Topology: **Not an explicit graph input.** Checks can inspect network/hardware links and environment relationships, but the paper does not construct or learn a service/network topology graph.
- Traffic: **Operational network checks are present**, but traffic/NetFlow is not used as a formal telemetry modality.
- NetFlow: No.
- Configuration: **Yes.** Environment variables, CUDA/HCCL configuration, and binding/interface settings can be checked by verified tools (Source: Sec. IV-B, p. 5; Fig. 6, p. 8).
- Tickets: Historical TSGs/post-mortems and incident descriptions are used as operational knowledge; raw ticket schema is not separately defined.
- Other: Troubleshooting guides (TSGs), standard operating procedures, live scripts, hardware state, and tool outputs.

**Multi-source operational evidence.** This is not classical metrics+logs+traces feature fusion. The primary integration mechanism is SOP/tool-based: structured checks invoke modality- or subsystem-specific tools and record their binary results plus detailed evidence.

## 7. Dataset and System Setting

- Public / Private: **Private industrial data and tools.** Company H's production environment, TSGs, and verified scripts are not released in the paper.
- Production / Synthetic: **Real production data and production deployment.** The evaluation uses real incidents and the paper describes live use with SRE human-in-the-loop (Source: Sec. V-A, pp. 6–7; Sec. V-D, p. 7).
- Observation duration: Diagnosis assumes the infrastructure state is quasi-static during a short checking procedure. An exact universal time window is **Unclear / Not explicitly stated in the paper** (Source: Sec. III-D, p. 4).
- Number of incidents: 84 real incidents over three months; 46 training and 38 inference (Source: Sec. V-A, p. 6).
- Number of devices / services / nodes: More than 10,000 accelerators in the production environment; the paper also reports workloads involving more than 1,000 accelerators (Source: Sec. I, p. 1; Sec. V-D, p. 7).
- Topology: LMaaS hardware/network environment and validated SOP procedure structure. A physical topology graph is **Unclear / Not explicitly stated in the paper**.

## 8. Core Method

LLMGuard has an offline knowledge-digitization phase and an online diagnosis phase.

### Offline knowledge digitization

An SOPAgent parses narrative TSGs into atomic linear SOP chains. A step contains a trigger, an operation and arguments, and an expected root-cause outcome. Natural-language checks are mapped to verified binary tools by dense retrieval and parameter resolution; if no verified tool exists, the gap is escalated to a human (Source: Sec. IV-A–B, pp. 4–5).

### Online diagnosis

The PlanAgent retrieves relevant SOPs for the alert and synthesizes an SOP Checking Tree (SOPCT). Prefix merging shares common checks so that repeated evidence collection is performed once. The CheckAgent traverses the tree through deterministic true/false transitions, backtracking or pruning as checks fail, and stops at an identified leaf. The SummaryAgent compiles the root cause, failing checks, and evidence chain (Source: Sec. IV-C–D, pp. 4–6; Figs. 3–4, pp. 5–6).

## 9. Architecture / Workflow

```text
historical TSG / SOP
→ SOPAgent parses atomic steps
→ verified tool registry + retrieval
→ PlanAgent builds SOP Checking Tree
→ CheckAgent runs binary checks and prunes/backtracks
→ leaf root cause
→ SummaryAgent produces evidence chain
→ SRE validates mitigation when high stakes
```

The online loop is not an unconstrained ReAct trajectory. The LLM helps construct and interpret the tree, but each runtime check follows the tree's deterministic transition. This is a deliberate separation between semantic flexibility and execution reliability (Source: Sec. IV-C–D, pp. 4–6; Sec. V-B, p. 7).

`Observation` is the output of a verified diagnostic tool. A Boolean result controls which branch remains possible, while the raw/detail evidence is retained for the final explanation. Thus observation is both a candidate-pruning signal and an auditable evidence record.

## 10. Detection Method

LLMGuard assumes an alert or symptom has already triggered diagnosis. It does not train or evaluate a separate metric/log anomaly detector. Some SOP checks can identify an abnormal hardware/network state, but this is part of diagnosis and candidate pruning rather than an independently scored detection stage (Source: Sec. III–IV, pp. 2–6).

This means its location/type scores should not be compared directly with a detector's F1. The system starts from a known operational complaint and measures how effectively it verifies a supported root.

## 11. RCA / Localization Method

The RCA pipeline is:

```text
alert-matched SOP candidates
→ prefix-merged SOP Checking Tree
→ verified check execution
→ true/false branch traversal
→ failed check and leaf candidate
→ root cause + evidence chain
```

### Candidate space

Initial candidates are historical/operational SOPs retrieved for the alert. The root-cause candidates are the leaves encoded by those SOPs. The paper does not provide a fixed numeric candidate count for an incident or for the full production system; this is **Unclear / Not explicitly stated in the paper**.

### Candidate pruning

Pruning is explicit and procedural:

- retrieval narrows the SOP set;
- prefix merging avoids repeated common checks;
- a false check prunes a branch and can trigger backtracking;
- a true check advances toward a leaf.

The candidate space is therefore mostly closed over known TSG coverage. An unknown fault or missing guide can end in a review/escalation path rather than open-ended root-cause expansion. This closed-world property is an interpretation of the described SOP tree and escalation design, not a claim that all production faults are known (Source: Sec. IV-A–D, pp. 4–6).

## 12. Diagnosis / Classification Method

Diagnosis maps the final verified leaf to a root-cause location and type, then summarizes the failed check and supporting evidence. The paper reports location accuracy (LA), type accuracy (TA), and average path length (APL) for training and inference incidents (Source: Sec. V-A, pp. 6–7).

It is not a generic fault classifier over an unrestricted label space. The type vocabulary and diagnostic coverage are strongly shaped by validated TSGs, tools, and historical post-mortems.

## 13. LLM / Agent Role

- LLM: **Yes.** LLMs parse TSG text, retrieve/resolve semantic checks, synthesize SOPCTs, and produce summaries (Source: Sec. IV-A–D, pp. 4–6).
- Tool-augmented LLM: **Yes.** Verified scripts and infrastructure checks are first-class runtime tools (Source: Sec. IV-B and IV-D, pp. 4–6).
- Agent: **Yes, as a multi-role workflow.** The paper names SOPAgent, PlanAgent, CheckAgent, and SummaryAgent. However, the online CheckAgent's traversal is deliberately deterministic rather than a free-form autonomous loop.
- Planning: **Yes, explicitly.** PlanAgent produces an SOP Checking Tree, but this is guide compilation and branch organization, not necessarily open-ended optimal planning.
- Memory: The SOP/TSG repository and current evidence/tree state act as operational knowledge and execution state. A modern Agent episodic or long-term memory architecture is **Unclear / Not explicitly stated in the paper**.
- Reflection: No independent Reflexion-style post-attempt verbal reinforcement mechanism is described.

The paper therefore supports a useful boundary: an Agent can include deterministic execution and bounded tools; Agentic behavior does not require unconstrained LLM selection at every step.

## 14. Ground Truth

Senior SRE post-mortems and TSGs provide the labelled root causes for 84 real incidents. Historical TSGs are used before evaluation to avoid leakage from the evaluation incidents (Source: Sec. V-A, p. 6).

Ground truth includes the diagnosed location/type associated with an incident. Whether each record includes a complete causal chain, exact onset/repair interval, multiple roots, or all relevant telemetry evidence is **Unclear / Not explicitly stated in the paper**.

## 15. Baselines

The paper compares LLMGuard with CoT, ReAct, RCA-Copilot, and Flow of Action-style baselines. It also includes ablations removing the SOP Checking Tree or evidence handling (Source: Sec. V-A–B, pp. 6–7; Tables I–II, p. 7).

The comparison is primarily about diagnostic orchestration, determinism, and evidence use in the same LMaaS setting; it is not a comparison with classical time-series RCA or graph-causal models.

## 16. Metrics

- **Location Accuracy (LA):** fraction of incidents for which the faulty component/location is correctly identified.
- **Type Accuracy (TA):** fraction for which the fault type is correctly diagnosed.
- **Average Path Length (APL):** average number of diagnostic checks/actions in the path; lower values indicate less procedural effort, provided correctness is maintained (Source: Sec. V-A, p. 6).
- **Diagnosis latency / time-to-diagnosis:** elapsed operational time from triggering diagnosis to a useful result; it measures responsiveness rather than correctness (Source: Sec. V-D, p. 7).
- **Token cost and resource use:** efficiency measures for production operation; they do not establish RCA accuracy (Source: Sec. V-D, p. 7).

## 17. Main Results

### Training incidents

Table I reports for the DeepSeek-V3 setting: LLMGuard LA 76.0, TA 84.7, APL 7.9. The best Flow of Action baseline reports LA 65.4, TA 72.1, and APL 15.2. Removing SOPCT gives LA 64.1, TA 71.5, and APL 15.0 in the same table (Source: Table I, p. 7).

### Inference incidents

Table II reports for DeepSeek-V3: LLMGuard LA 81.2, TA 85.3, and APL 8.2. The other baselines are lower in the reported setting, while a raw ReAct comparison has validity/efficiency problems on training cases and performs worse in inference comparisons (Source: Table II, p. 7; Sec. V-B, p. 7).

### Ablation and model dependence

Removing SOPCT drops LA by about 11.9 percentage points and increases APL from 7.9 to 15.0 in the reported training setting. Removing the evidence mechanism lowers TA by about 11.9 points (Source: Sec. V-B, p. 7; Table I, p. 7).

The paper reports that LLMGuard's location gap between its smallest and strongest tested Qwen3 models is about 13.0%, while the smallest Qwen3 model with LLMGuard still outperforms larger baseline configurations such as CoT and RCA-Copilot in the cited comparison (Source: Sec. V-C, p. 7). This supports an orchestration/knowledge effect, not a claim that model size is irrelevant.

### Efficiency and production case

The paper reports median diagnosis time of about 45 seconds, roughly 75% lower average latency than baselines above 180 seconds, more than 99% of paths within a three-minute target, and about 48% lower token cost. The online service uses eight CPU cores and 16 GB RAM in the reported deployment configuration (Source: Sec. V-D, p. 7; Fig. 5, p. 7).

In the case study, a 512-accelerator training job suffered about 40% throughput degradation. The checking tree inspected hardware/network evidence and identified `HCCL_SOCKET_IFNAME` binding to a low-bandwidth management interface instead of a high-speed RoCE interface, reportedly locating the issue in two minutes (Source: Fig. 6 and accompanying text, p. 8).

## 18. Scalability / Deployment

The paper reports deployment in Company H's production LMaaS environment with more than 10,000 accelerators and workloads spanning more than 1,000 accelerators. It evaluates 84 real incidents over three months and describes a live human-on-the-loop operating model in which SREs validate high-stakes mitigation (Source: Sec. I, p. 1; Sec. V-A and V-D, pp. 6–8).

The claimed scale is demonstrated through production environment size, incident evaluation, latency, and resource cost. It is not evidence that every possible network or hardware failure is covered. The paper explicitly identifies SOP quality and coverage, observation cost, and maintenance effort as important constraints (Source: discussion around Fig. 6, p. 8).

## 19. Strengths

- Uses real production incidents and a large LMaaS deployment.
- Converts narrative operational knowledge into executable, inspectable checks.
- Separates semantic LLM work from deterministic runtime traversal.
- Preserves a detailed evidence chain and supports human escalation.
- Measures accuracy, path length, latency, token cost, and resource requirements.
- Shows that orchestration and SOP quality can matter as much as the language-model backbone.

## 20. Limitations

### Paper states

The paper identifies knowledge debt and SOP curation as bottlenecks, determinism/coverage trade-offs, nontrivial observation cost for heavy probes, and a shift of SRE effort toward maintaining troubleshooting guides and verified tools (Source: Sec. V-D, p. 8).

The system also assumes a quasi-static infrastructure state during a short diagnosis window, validated historical patterns, and deterministic binary checks (Source: Sec. III-D, p. 4).

### My interpretation

LLMGuard is strong for known or guide-covered faults, but its tree is not an open-set causal discovery method. Unknown faults, stale SOPs, ambiguous check outputs, and rapidly changing network state may require an explicit uncertainty/escalation design beyond the reported tree.

## 21. Reproducibility

- Code available? **Not stated as publicly available.**
- Dataset available? **No; production incidents and SOPs are private.**
- Benchmark available? No public benchmark is described.
- Prompt available? The agent roles and workflow are described, but full prompts are not included.
- Model/API specified? Tested model families and configurations are reported at a high level.
- Hyperparameters? Some system settings are reported; the complete SOP compiler, tool registry, and production configuration are not public.
- Enough detail to reproduce? **Low–Medium.** The architecture is clear, but private data, verified scripts, TSGs, and production tool semantics prevent direct reproduction.

## 22. Relationship to Existing AIOps Knowledge

LLMGuard adds a production-oriented pattern that is distinct from the earlier papers:

- Unlike RCAgentBench, it does not expose a broad free-form multimodal tool search benchmark; it compiles validated procedures and executes a deterministic tree.
- Unlike StaR, it does not learn a dynamic causal graph from metric time series.
- Unlike CAUSALDX, it does not primarily expand unknown causal hypotheses; it searches the coverage of retrieved SOP leaves and escalates gaps.
- It demonstrates that “Agent” and “autonomous free-form LLM loop” are not synonyms.

Related concepts:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md)
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md)
- [Agent](../../../concepts/agent.md)
- [Planning](../../../concepts/planning.md)
- [Tool Use](../../../concepts/tool-use.md)
- [Context Engineering](../../../concepts/context-engineering.md)
- [Memory](../../../concepts/memory.md)

The memory relation is operational: an SOP repository and current checking tree provide knowledge/state, but the paper does not establish a general persistent episodic Agent-memory architecture.

## 23. Relevance to My Research

### Similarities

- It diagnoses infrastructure failures involving network links, interfaces/configuration, hardware, and runtime state.
- It uses verified tools and evidence chains, which are directly relevant to safe network operations.
- It evaluates real incidents at a large production scale and reports latency/cost constraints.
- Its deterministic branching is relevant to preventing LLM hallucination in high-stakes RCA.

### Differences

- The domain is LMaaS accelerator infrastructure and validated SOPs, not a general network telemetry/RCA benchmark.
- It does not use NetFlow, packet data, or a learned physical network topology graph.
- Candidate root causes are primarily guide/SOP leaves rather than open-set device/interface/link hypotheses.
- The production evidence is procedure-driven; raw multimodal telemetry fusion is not the main experiment.

### Potentially Useful Ideas

- Compile network troubleshooting guides into a typed, executable checking graph/tree.
- Register verified diagnostic tools with explicit argument and result semantics.
- Use deterministic branch/prune behavior for high-risk checks and preserve raw evidence.
- Separate plan construction, check execution, and summary generation.
- Add escalation when no trusted tool or guide covers a candidate.
- Evaluate diagnosis time, path length, evidence coverage, and operator intervention in addition to accuracy.

### Assumptions That May Not Transfer

- Network conditions may change during diagnosis, violating the quasi-static-state assumption.
- A binary check may be insufficient for continuous traffic, congestion, or probabilistic telemetry.
- SOP coverage and correctness vary by vendor, device model, and network generation.
- Historical guide leaves may force a closed-world candidate space and miss novel multi-root incidents.

### Experiments Worth Considering

- Compare free-form Agent tool selection with a network SOP tree under identical alerts and tool access.
- Measure accuracy and latency when checks are noisy, stale, delayed, or expensive.
- Add an explicit `Review_Required` path for unknown root types and evaluate escalation quality.
- Test how much verified SOP coverage is needed before deterministic orchestration beats unconstrained ReAct.
- Evaluate network cases containing both a physical link fault and a traffic symptom to separate root and consequence.

### Transferability to Network AIOps

**Medium–High.** The operational workflow, verified tools, evidence chain, and human-gated production design transfer well; the LMaaS-specific SOP leaves and quasi-static/known-fault assumptions do not transfer directly.

## 24. My Understanding

LLMGuard treats an LLM as a compiler, retriever, planner, and summarizer around a trusted diagnostic execution substrate. The key runtime object is an SOP Checking Tree: shared checks are merged, Boolean observations prune paths, and the final leaf is tied to an evidence chain. This is still an Agentic workflow because multiple roles organize and execute task-specific actions, but it deliberately limits the LLM's freedom at the point where reliability matters most.

The paper's strongest AIOps lesson is that production RCA quality depends on knowledge coverage, tool verification, deterministic control, and latency—not only on a more capable model. Its main boundary is also clear: it is not a topology-learning method and not open-set causal discovery.

## 25. Questions

- How can an SOP tree represent continuous-valued or probabilistic network evidence instead of binary checks only?
- How should the tree adapt when topology or traffic conditions change during execution?
- How can unknown root causes be detected when the SOP repository has no matching leaf?
- What is the right unit for measuring verified-tool coverage and SOP freshness in network operations?
- Can a deterministic SOP path be combined with learned dynamic causal ranking without creating contradictory decisions?

## 26. Source Grounding

Primary grounding used for this note:

- Abstract and Sec. I–III, pp. 1–4: LMaaS problem, reliability requirements, assumptions, and production motivation.
- Sec. IV-A–D, pp. 4–6; Figs. 3–4: knowledge digitization, verified tools, SOPCT planning, deterministic checking, and summary.
- Sec. V-A, pp. 6–7; Tables I–II: incidents, baselines, LA/TA/APL results.
- Sec. V-B–C, p. 7: SOPCT/evidence ablations and model-dependence comparison.
- Sec. V-D, pp. 7–8; Fig. 5–6: latency, cost, scale, production case, and operational lessons.

The exact numeric candidate-set size, per-incident observation window, physical topology representation, public code/data status, and an autonomous remediation protocol are **Unclear / Not explicitly stated in the paper**.

## 27. Tags

`AIOps` `fault-diagnosis` `RCA` `LMaaS` `production` `SOP` `TSG` `deterministic-agent` `tool-verification` `evidence-chain` `human-in-the-loop` `network-infrastructure`
