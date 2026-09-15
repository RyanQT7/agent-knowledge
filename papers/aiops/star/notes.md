Status: Full Reading: Completed

# StaR: Stateful Dynamic-Graph Root Cause Analysis through Memory-Enhanced Causality Discovery

## 1. Metadata

- Title: StaR: Stateful Dynamic-Graph Root Cause Analysis through Memory-Enhanced Causality Discovery
- Authors: Haiyu Huang, Man Tik Ng, Jiewei Lyu, Yujie Huang, Guangba Yu, Yilun Wang, Michael R. Lyu
- Year: 2026
- Venue: ACM SIGKDD 2026
- URL / DOI: https://doi.org/10.1145/3770855.3817863
- Local File: [StaR PDF](../../../sources/papers/AIOps_papers/KDD26-StaR- Stateful Dynamic-Graph Root Cause Analysis throughMemory-Enhanced Causality Discovery.pdf)
- Paper ID: `star`

## 2. One-Sentence Summary

StaR adds persistent temporal state and dynamic message passing to a Granger-style causal-discovery model so that root-cause localization can account for changing dependencies and delayed, stateful effects in multivariate system metrics.

## 3. Problem Setting

### Paper states

The paper targets RCA for multivariate time-series systems. It identifies two weaknesses in prior approaches: static causal relationships do not represent changing system topology, and short, stateless windows miss delayed effects such as slow accumulation or memory-leak-like behavior (Source: Abstract; Sec. 1, pp. 1–2; Figs. 1–2, pp. 1–2).

StaR formulates a stateful structural causal model in which a metric depends on past observations, a previous memory state, and an exogenous innovation. An anomaly is treated as an intervention or deviation in the exogenous term; variables with sufficiently large state-aware deviations become root-cause candidates (Source: Sec. 3.1, p. 3).

### My interpretation

The core problem is not multimodal evidence collection or LLM reasoning. It is how to make metric-based causal localization sensitive to both changing graph structure and system history. The paper therefore provides a complementary, non-LLM baseline for the topology/temporal layer of an AIOps RCA pipeline.

## 4. AIOps Task

- Detection: **Not a standalone anomaly detector.** The method estimates exogenous deviations from a model of normal data and uses their magnitude for RCA. The incident/anomaly is effectively represented by an intervention or abnormal deviation (Source: Sec. 3.1 and Sec. 3.4, pp. 3, 6).
- RCA: **Yes.** It ranks variables that best explain the abnormal exogenous innovation (Source: Sec. 3.4, p. 6).
- Localization: **Yes.** Root causes are metric variables or associated system components; AC@K evaluates whether true roots occur in the top K (Source: Sec. 4.1, p. 6; Appendix A.4, p. 11).
- Diagnosis: **Limited.** The method localizes anomalous/root variables, but it does not primarily classify a human-readable fault mechanism. A general fault-type output is **Unclear / Not explicitly stated in the paper**.
- Prediction: **Auxiliary model function, not the evaluated task.** State-aware reconstruction/prediction is used to obtain innovations for RCA.
- Remediation: No.

The main task boundary is:

```text
normal multivariate time series
→ state-aware causal reconstruction
→ exogenous innovation / anomaly evidence
→ root-variable ranking
```

This is different from a system that first detects an incident and then invokes an Agent to query logs or tools.

## 5. Failure / Incident Setting

The paper evaluates synthetic systems with static and dynamic causal structures, plus public real-world datasets including SWaT, MSDS, and SMD (Source: Sec. 4.2, p. 6; Table 1, p. 6).

The dynamic synthetic settings are designed to test changing connections and stateful propagation. `RandomConnection` uses a changing connection structure, while `SlowAccum` represents gradual fault propagation in a chain (Source: Sec. 4.2, p. 6; Appendix A.2, p. 11).

The paper does not report a live production deployment or operator-confirmed incident investigation. The real datasets are public benchmark data, not evidence of production deployment by StaR.

## 6. Data Modalities

- Metrics: **Yes.** The input is multivariate time-series measurements from system variables or sensors (Source: Sec. 3.1, p. 3; Sec. 4.2, p. 6).
- Logs: No.
- Traces: No.
- Alarms: No separate alarm stream is described.
- Topology: **Yes, as a dynamic graph or causal/dependency structure.** The model can use a time-varying adjacency mask in dynamic settings, and can also infer relationships through message passing when an adjacency graph is not supplied (Source: Sec. 3.3.1, pp. 4–5; Sec. 4.2, p. 6).
- Traffic: No.
- NetFlow: No.
- Configuration: Not explicitly used as an input modality.
- Tickets: No.
- Other: Persistent latent temporal state and exogenous innovation variables.

**Single telemetry modality plus graph structure.** It is not multimodal in the usual metrics/logs/traces sense. The graph and memory augment metric time series, but the paper does not fuse heterogeneous operational data sources.

## 7. Dataset and System Setting

- Public / Private: **Public datasets and code are reported.** The paper provides a Zenodo dataset reference and a GitHub implementation link (Source: Sec. 4.2, p. 6; Appendix A.5, p. 11).
- Production / Synthetic: Mixed synthetic and public real-world benchmark data; no production deployment is claimed.
- Observation duration: The model uses a sliding/look-back window `w` and a persistent memory state. The default is `w=1` for most datasets and `w=10` for RandomConnection; sensitivity tests use `w ∈ {1, 5, 10, 15, 20}` (Source: Appendix A.5, p. 11; Sec. 4.4, p. 9).
- Number of incidents: Table 1 reports 100 test sequences for the synthetic and SWaT/other benchmark entries where specified; exact semantic “incident” counts for each real dataset are not uniform and should not be equated with the 100 synthetic test sequences (Source: Table 1, p. 6).
- Number of devices / services / nodes: RandomConnection has five services in its dynamic synthetic configuration. Dataset variable counts otherwise differ; a unified infrastructure-node count is **Unclear / Not explicitly stated in the paper** (Source: Appendix A.2, p. 11; Table 1, p. 6).
- Topology: Static causal graphs for several synthetic systems; a changing connection graph for RandomConnection; a chain-like propagation setting for SlowAccum. Real datasets do not provide complete ground-truth causal graphs (Source: Sec. 4.2, p. 6; Appendix A.2, p. 11).

Selected Table 1 dataset details are:

- Linear and Nonlinear: 5,000 training and 100 test sequences, average length 500; average root counts 3.75 and 5.25.
- Lotka–Volterra: 40,000 training and 100 test sequences, average length 2,000; average root count 3.75.
- Lorenz96: 200,000 training and 100 test sequences, average length 2,000; average root count 15.75.
- RandomConnection: 60,000 training and 100 test sequences, average length 4,000; average root count 1.40.
- SlowAccum: 50,000 training and 100 test sequences, average length 3,000; average root count 3.75.
- SWaT: 49,580 training and 20 test sequences, average length 511; average root count 3.35.
- MSDS: 29,268 training and 4,255 test sequences, average length 213; average root count 3.06.
- SMD: 12,000 training and 150 test sequences, average length 80; average root count 2.50.

(Source: Table 1, p. 6. The table's “root count” is a dataset statistic and should not be read as a universal candidate-space size.)

## 8. Core Method

StaR embeds a Temporal Graph Network (TGN)-style state mechanism into Granger causal discovery. Each variable has a persistent memory state. Messages aggregate information from other variables, and the resulting dynamic causal coefficients can change with the current state (Source: Sec. 3.3.1, pp. 4–5; Fig. 3, p. 4).

The framework has two complementary paths:

1. An abductive encoder estimates exogenous innovations from observations and persistent state.
2. A deductive decoder reconstructs observations using the inferred innovations and an observation-driven path.

The joint reconstruction objective is regularized for a sparse causal graph, smoothness, memory behavior, and an exogenous distribution prior (Source: Sec. 3.3.2–3.3.3, pp. 5–6).

The important use of “memory” here is a model-internal temporal state used to carry information across time steps. It is not an Agent's natural-language episodic memory, external knowledge store, or persistent record of past troubleshooting episodes.

## 9. Architecture / Workflow

Training and online analysis can be summarized as:

```text
normal multivariate time series
→ graph/message encoder with persistent state
→ state-aware exogenous innovation inference
→ dual-path reconstruction
→ learn dynamic causal coefficients
→ online robust score of exogenous deviations
→ rank root variables
```

At each time step, a variable receives messages from other variables (or from neighbors selected by a supplied adjacency mask), updates its memory with a GRU-like mechanism, and contributes to the dynamic graph representation (Source: Sec. 3.3.1, pp. 4–5).

At inference time, the method computes a robust Z-score from the exogenous innovation using training medians and median absolute deviations. The highest scores are treated as the most likely root causes. Expected endogenous effects are subtracted so that downstream consequences do not dominate the root ranking (Source: Sec. 3.4, p. 6; Eq. 12).

There is no LLM Planner, Executor, Tool, or Agent loop in this workflow. “Online” means streaming model inference, not an interactive Agent repeatedly acting on an environment.

## 10. Detection Method

StaR is trained on normal data and uses state-aware prediction/reconstruction errors to expose exogenous deviations. The same deviation score supports root ranking. The paper's experiments therefore focus on causal discovery and RCA rather than reporting a separate precision/recall detector followed by a separate RCA stage (Source: Sec. 3.2–3.4, pp. 3–6; Sec. 4.1, p. 6).

This creates an important boundary: an abnormal innovation is evidence for a root variable under the model, not proof that the system has already identified a physical fault or a fault type.

## 11. RCA / Localization Method

The paper's RCA path is:

```text
multivariate metric stream
→ state-aware causal reconstruction
→ exogenous innovation for each variable
→ robust deviation score
→ root-cause candidate ranking
→ AC@K evaluation
```

### Candidate space

The candidate set is the set of metric variables in the modeled system. In a network interpretation, this could be metrics attached to devices or components, but the paper does not define a network device/interface/link candidate hierarchy.

The exact fixed candidate count varies by dataset and is not presented as one universal number. Table 1 reports average root counts, while the number of modeled variables is dataset-specific. Therefore, a generic candidate-space size is **Unclear / Not explicitly stated in the paper**.

### Candidate pruning

There is no separate discrete candidate-pruning stage. Sparse L1 regularization encourages a sparse causal structure, and innovation scores rank variables. In the supplied dynamic graph setting, an adjacency mask can restrict message passing; otherwise the method can treat all variables as neighbors and learn relationship strengths (Source: Sec. 3.3.1, pp. 4–5; Sec. 3.3.3, p. 6).

## 12. Diagnosis / Classification Method

StaR primarily localizes root variables. It does not output a general taxonomy such as link flap, congestion, interface failure, or hardware fault. Fault-type diagnosis and natural-language explanation are **Unclear / Not explicitly stated in the paper**.

The method's causal-discovery metrics evaluate graph recovery on synthetic data; RCA metrics evaluate whether true roots are near the top of a ranking. These are not equivalent to a supervised fault-classification score (Source: Sec. 4.1, p. 6; Appendix A.4, p. 11).

## 13. LLM / Agent Role

- LLM: No.
- Tool-augmented LLM: No.
- Agent: No. The method is a learned time-series/graph model, not an interactive Agent workflow.
- Planning: No explicit planning mechanism.
- Memory: **Yes, but as model temporal state.** Per-variable persistent state helps represent history and delayed effects. It should not be merged with the knowledge base's Agent Memory concept.
- Reflection: No.

The paper is useful precisely because it isolates a causal/time-series mechanism without adding LLM or Agent orchestration.

## 14. Ground Truth

Synthetic datasets have known generating graphs, interventions, and root causes, so causal-discovery and root-localization ground truth are available for those experiments (Source: Sec. 4.2, p. 6; Appendix A.2, p. 11).

For real datasets such as SWaT, MSDS, and SMD, the paper evaluates RCA but does not provide a complete physical causal graph. The ground-truth construction and whether every label represents a single root, multiple roots, a time interval, or an incident-level label vary by dataset and are **Unclear / Not explicitly stated in the paper** beyond the reported dataset statistics (Source: Sec. 4.2, p. 6; Table 1, p. 6).

The synthetic root count can be multi-root—for example, RandomConnection reports 70% single-root and 30% dual-root cases (Source: Appendix A.2, p. 11).

## 15. Baselines

For causal discovery, the paper compares against methods including VAR, cMLP, cLSTM, TCDF, eSRU, PCMCI, PCMCI+, GVAR, CUTS, and AERCA (Source: Sec. 4.3, p. 6; Table 2, p. 7).

For RCA, it compares with approaches such as n-Diagnosis, RCD, CIRCA, and AERCA, with exact dataset/method coverage shown in Table 3 (Source: Sec. 4.3, p. 6; Table 3, p. 8).

The baselines are primarily causal discovery and time-series RCA methods, not LLM/Agent systems. That makes the comparison useful for the non-LLM structural layer but not a direct comparison of Agent reasoning.

## 16. Metrics

- **Causal-discovery F1:** balance of recovered causal edges against synthetic ground-truth edges.
- **AUC-PR / AUC-ROC:** ranking quality of predicted causal links under the corresponding precision-recall or receiver-operating-characteristic view.
- **Hamming distance:** edge-level disagreement between the predicted and true graph; used for synthetic graph evaluation (Source: Sec. 4.1, p. 6).
- **AC@K:** fraction of ground-truth root causes appearing in the top K ranked variables; AC@1 is the strictest localization setting (Source: Sec. 4.1, p. 6; Appendix A.4, p. 11).
- **Avg@10:** average number or quality of recovered roots among the top 10 according to the paper's RCA evaluation definition (Source: Appendix A.4, p. 11).
- **AC*@K:** a time-step-aware RCA variant that accounts for whether a predicted root is correct at the relevant time step (Source: Appendix A.7, p. 12).

Latency is also measured in the efficiency experiments, but it is a system-cost metric rather than RCA correctness (Source: Sec. 4.5, p. 9; Table 4, p. 9).

## 17. Main Results

### Accuracy and dynamic settings

- On dynamic `RandomConnection`, StaR improves AC@1 over AERCA from 0.028 to 0.584 in the reported comparison.
- On dynamic `SlowAccum`, StaR improves AC@1 from 0.121 to 0.920.
- On real MSDS, StaR reports AC@1 0.752 versus 0.381 for the comparison baseline shown in Table 3.
- On SWaT, StaR reports AC@1 0.300 versus 0.200; on SMD both methods report 1.000 in the cited comparison.

(Source: Abstract; Table 3, p. 8; Sec. 4.4, p. 8. Exact values are dataset- and baseline-specific; they should not be read as a universal improvement guarantee.)

The paper reports strong performance on several static synthetic datasets and especially large gains on dynamic/stateful settings. This supports the value of persistent state and dynamic relationships for the tested distributions, not a claim that the learned graph is a physical causal model in every deployment.

### Ablation and state

Removing memory hurts dynamic causal discovery and RCA. The cold-start ablation shows that lack of an initial memory state does not always catastrophically fail, but can reduce performance—for example, the paper reports differences for RandomConnection under different connection probabilities and for MSDS (Source: Sec. 4.4, Table 5, p. 9).

### Efficiency and scale

StaR's reported CPU latencies are 0.193 ms, 0.079 ms, 0.202 ms, and 0.769 ms for the listed RandomConnection, MSDS, SWaT, and SMD settings, respectively, compared with the corresponding AERCA values in Table 4. The paper reports that processing up to 500 nodes takes under one second and 1,000 nodes under ten seconds, and that pooled memory gives about a 2.2× speedup with little degradation (Source: Sec. 4.5, p. 9; Table 4, p. 9).

### Window sensitivity

On RandomConnection, the paper reports AC@1 0.907 and latency 0.059 ms at `w=1`, versus AC@1 0.709 and latency 0.290 ms at `w=20` (Source: Sec. 4.5, p. 9). This illustrates that a longer input window does not automatically improve RCA when persistent state already carries temporal information.

### Implementation note

Appendix A.8 documents a discrepancy between the paper equation and the code for the KL term. The authors state that the code implementation is mathematically correct and that all reported results use the corrected implementation (Source: Appendix A.8, p. 12). This should be preserved as a reproducibility caution.

## 18. Scalability / Deployment

The paper evaluates dataset-scale streams and reports node-count latency up to 1,000 nodes, but does not demonstrate a live production deployment. Its own limitations note that TGN/memory complexity may become difficult at hyperscale and may require sampling or hierarchical processing (Source: Sec. 4.5, p. 9; Sec. 5, p. 9).

The real datasets support realistic benchmark evaluation, not the stronger claim that StaR ran continuously in a production network. Concept drift and dependence on normal training data are also deployment concerns (Source: Sec. 5, p. 9).

## 19. Strengths

- Separates dynamic relationship modeling from LLM/Agent effects.
- Represents delayed and stateful effects instead of assuming a stateless short window.
- Provides both graph-recovery metrics and root-localization metrics.
- Includes synthetic dynamic settings that directly test changing connections and gradual propagation.
- Reports latency, memory ablations, and window sensitivity rather than accuracy alone.

## 20. Limitations

### Paper states

The paper notes memory/TGN complexity at hyperscale, dependence on normal data and possible concept drift, and the limits of Granger-style causal discovery. Predictive usefulness does not prove physical causality; hidden confounders and instantaneous coupling can also affect interpretation (Source: Sec. 5, p. 9).

### My interpretation

For network AIOps, the most important risk is semantic: a learned dynamic graph may be an effective predictor or ranking structure while remaining incomplete or physically non-causal. It should be used as evidence/constraint with uncertainty, not presented as a definitive topology or causal explanation without additional validation.

## 21. Reproducibility

- Code available? **Yes, reported by the paper** through a GitHub implementation link (Source: Sec. 4.2, p. 6; Appendix A.5, p. 11).
- Dataset available? **Yes for the provided synthetic/public benchmark package**, with a Zenodo reference reported by the paper (Source: Sec. 4.2, p. 6).
- Benchmark available? The synthetic settings and public real datasets are described; the exact release packaging should be checked in a future code-reading task.
- Prompt available? Not applicable.
- Model/API specified? Not applicable; architecture and training settings are described.
- Hyperparameters? Key settings such as memory dimension 64 and window choices are described; exact reproduction details should be checked in the code (Source: Appendix A.5 and A.9, p. 12).
- Enough detail to reproduce? **Medium–High**, subject to verifying the code/data release and resolving the documented KL implementation discrepancy.

## 22. Relationship to Existing AIOps Knowledge

StaR adds a different kind of structure to the current AIOps knowledge base:

- It treats a metric variable as the initial candidate root rather than a service-level natural-language answer.
- It uses a dynamic graph as a learned/message-passing causal structure, unlike RCAgentBench's service call-chain context.
- It uses persistent temporal model state to capture delayed effects, but this is not the same as ReAct trajectory context or Reflexion episodic memory.
- It demonstrates why “causal” must be qualified: the paper itself relates its method to Granger predictive causality and states that predictive utility is not physical causation.

Related concepts:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md)
- [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md)
- [Memory](../../../concepts/memory.md) — only for the cross-domain distinction between model temporal state and Agent memory.

## 23. Relevance to My Research

### Similarities

- Directly studies root-cause localization from operational time series.
- Makes dynamic dependencies and delayed propagation first-class concerns.
- Provides top-k localization and latency measurements relevant to infrastructure RCA.

### Differences

- The input is metric/time-series data, not a heterogeneous network evidence set containing logs/syslog, traffic/NetFlow, packets, and topology.
- The causal graph is learned or supplied at the variable level; network physical topology and interface/link semantics are not modeled explicitly.
- The experiments are synthetic/public benchmarks rather than live network incidents or production deployment.

### Potentially Useful Ideas

- Maintain a stateful representation for slowly accumulating faults and delayed propagation.
- Let topology/dependency structure vary over time rather than treating it as permanently static.
- Rank root candidates using a state-aware innovation score and evaluate at multiple K values.
- Separate structural/causal discovery quality from final RCA localization quality.
- Measure latency and memory overhead as graph size grows.

### Assumptions That May Not Transfer

- Granger-predictive dependence may not represent physical network causality.
- Normal-data training and stable variable identity may be difficult under changing network configurations.
- Complete or reliable graph masks may not exist; hidden confounders and simultaneous faults are common concerns.
- Metric-only evidence cannot explain many protocol, configuration, or traffic symptoms.

### Experiments Worth Considering

- Compare a dynamic topology/causal prior with a static physical topology on network incidents involving link or interface changes.
- Test stateful models on delayed failures and slow degradation, using time-aware root labels.
- Add logs/syslog and traffic/NetFlow as separate evidence channels without assuming the learned metric graph is physical truth.
- Evaluate uncertainty and false root ranking when topology is incomplete or stale.
- Report AC@1/AC@K alongside time-to-diagnosis, evidence coverage, and detection-to-RCA handoff quality.

### Transferability to Network AIOps

**Medium.** The stateful temporal and dynamic-dependency ideas are relevant, but the paper's metric-variable causal assumptions and benchmark graph semantics do not directly solve network device/interface/link RCA.

## 24. My Understanding

StaR is a causal/time-series RCA model, not an Agent. Its “memory” is a learned temporal state that carries information across observations so the model can represent delayed effects. The model ranks variables whose exogenous deviations are least explained by the learned endogenous dynamics. The dynamic graph is useful structure, but the paper explicitly warns that Granger-style predictive relations are not automatically physical causes.

This makes StaR a useful contrast to RCAgentBench. RCAgentBench asks an Agent to collect multimodal evidence through tools and explain a component/fault type; StaR learns a stateful graph from metric streams and ranks root variables. The two can be complementary layers in a future system, but they are not the same RCA architecture.

## 25. Questions

- How can a stateful metric model incorporate delayed syslog, traffic, and packet evidence without losing time provenance?
- When a learned dynamic graph disagrees with known physical topology, how should candidates and explanations be combined?
- What ground truth can distinguish a predictive root variable from the physical initiating network fault?
- How should AC@K be extended to multiple components at different hierarchy levels, such as device, interface, link, and optical module?
- How robust is the persistent state under topology changes, missing data, and concept drift in a long-running network?

## 26. Source Grounding

Primary grounding used for this note:

- Abstract and Sec. 1, pp. 1–2: dynamic topology, stateful anomalies, and motivation.
- Sec. 3.1, p. 3: stateful structural causal model and root candidate formulation.
- Sec. 3.2–3.3, pp. 3–6; Fig. 3: encoder/decoder, message passing, dynamic coefficients, memory, and loss.
- Sec. 3.4, p. 6; Eq. 12: robust innovation score and root ranking.
- Sec. 4.1–4.2, p. 6: evaluation metrics and datasets.
- Table 1, p. 6: dataset sizes, sequence lengths, and average root counts.
- Tables 2–3, pp. 7–8; Sec. 4.4: causal-discovery and RCA results.
- Table 4, p. 9; Sec. 4.5: latency, node-count, memory-pooling, and window-sensitivity results.
- Table 5, p. 9; Appendix A.5, A.7–A.9, pp. 11–12: memory/cold-start, time-aware evaluation, implementation discrepancy, and sensitivity details.
- Sec. 5, p. 9: stated limitations.

The exact real-dataset root-label construction, one universal candidate count, a fault-type classifier, and production deployment are **Unclear / Not explicitly stated in the paper**.

## 27. Tags

`AIOps` `RCA` `fault-localization` `time-series` `dynamic-graph` `causal-discovery` `Granger-causality` `stateful-model` `memory-not-Agent-memory` `network-transfer`
