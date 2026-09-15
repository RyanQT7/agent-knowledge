Status: Full Reading: Completed

# RCAgentBench: An Agent-Oriented Benchmark for Multimodal Root Cause Analysis in Microservices

## 1. Metadata

- Title: RCAgentBench: An Agent-Oriented Benchmark for Multimodal Root Cause Analysis in Microservices
- Authors: Hengyue Jiang, Zexin Wang, Xiaohui Nie, Di Gao, Jingjing Li, Changhua Pei
- Year: 2026
- Venue: IEEE/ACM IWQoS 2026
- URL / DOI: https://doi.org/10.1109/IWQoS70441.2026.11661026
- Local File: [RCAgentBench PDF](../../../sources/papers/AIOps_papers/IWQOS26-RCAgentBench_An_Agent-Oriented_Benchmark_for_Multimodal_Root_Cause_Analysis_in_Microservices.pdf)
- Paper ID: `rcagentbench`

## 2. One-Sentence Summary

RCAgentBench provides a public, tool-bounded benchmark for comparing single- and multi-agent root-cause-analysis workflows over metrics, logs, and traces, while evaluating both the final diagnosis and the diagnostic process.

## 3. Problem Setting

### Paper states

The paper argues that existing microservice RCA research lacks diverse labelled cases, standardized diagnostic tools, and systematic evaluation of agent patterns. Many existing methods focus on a final root-cause label or a graph model, while the intermediate reasoning and evidence-gathering process are not evaluated consistently (Source: Abstract; Sec. I, pp. 1–2).

The benchmark gives an agent a natural-language query containing a case UUID and an anomalous time window. The agent must retrieve and interpret monitoring evidence instead of receiving a pre-filtered root-cause feature set. It returns a structured JSON result containing the diagnosed component, a reason, and a reasoning trace (Source: Sec. II-A, p. 2; Sec. IV-A, p. 4).

### My interpretation

The primary problem is not anomaly detection alone. It is evaluation of evidence-grounded RCA under a common interaction interface: which component is faulty, what type of fault occurred, which observations support the answer, and how much diagnostic interaction was required.

## 4. AIOps Task

- Detection: **Partly included, but not the primary task.** The incident and anomaly window are provided by the query. The metrics tool performs threshold-based evidence extraction, including a three-sigma comparison against a baseline (Source: Sec. II-A, p. 2; Sec. IV-B, p. 5).
- RCA: **Yes.** The agent must identify the faulty component and fault type from the available evidence (Source: Sec. II-A, p. 2).
- Localization: **Yes.** Root-cause location is evaluated with LA-Top1 and LA-Top5 (Source: Sec. V-A, p. 5).
- Diagnosis: **Yes.** Fault-type accuracy is evaluated separately from component localization (Source: Sec. V-A, pp. 5–6).
- Prediction: No.
- Remediation: No. The benchmark evaluates diagnosis and explanation; it does not evaluate an automatic repair action (Source: Sec. IV and Sec. V; the paper's stated limitations in Sec. VIII, p. 9).

The important boundary is:

```text
given incident window
→ evidence extraction / anomaly interpretation
→ component localization
→ fault-type diagnosis
→ explanation
```

Detection output is therefore an input or intermediate signal for RCA, not the same task as RCA.

## 5. Failure / Incident Setting

The benchmark is built from the HipsterShop microservice application and faults injected with Chaos-Mesh at service, pod, and node levels. The fault catalogue covers network delay, packet loss and corruption, CPU and memory stress, JVM and I/O faults, DNS and port misconfiguration, node/pod failures, and code errors (Source: Sec. III, p. 3; Table I, p. 3).

The cases are controlled fault-injection cases rather than confirmed historical production incidents. The paper presents a high-fidelity microservice testbed, but does not claim production deployment of the benchmark itself (Source: Sec. III, p. 3).

## 6. Data Modalities

- Metrics: **Yes.** Prometheus time-series metrics such as CPU, memory, latency, and error-related KPIs; the standardized tool compares recent values with a prior baseline (Source: Sec. II-B, p. 2; Sec. IV-B, p. 5).
- Logs: **Yes.** Elasticsearch logs are filtered within the incident window and grouped by pod; unique error messages and first occurrences are returned (Source: Sec. II-B, p. 2; Sec. IV-B, p. 5).
- Traces: **Yes.** Jaeger traces expose end-to-end spans, call relationships, latency, and request-ratio anomalies (Source: Sec. II-B, pp. 2–3; Sec. IV-B, p. 5).
- Alarms: No separate alarm modality is defined; the query supplies an anomalous case and time window.
- Topology: **Yes, as structural system information.** The service call chain, service/pod relationships, and system information are available to support diagnosis (Source: Sec. III, p. 3; Sec. V-D, Fig. 6, p. 9).
- Traffic: Not explicitly stated as a traffic telemetry modality.
- NetFlow: No.
- Configuration: **Partly.** The fault catalogue includes configuration faults such as DNS/port misconfiguration, and system information is supplied as context, but configuration is not a separately evaluated telemetry stream (Source: Table I, p. 3; Table V, p. 8).
- Tickets: No.
- Other: Fault metadata and the benchmark query window.

**Multi-modal.** The paper explicitly targets the joint use of metrics, logs, and traces. The fusion is not a learned early feature-fusion network: separate tools return modality-specific evidence, and the selected agent workflow integrates that evidence during reasoning (Source: Abstract; Sec. IV-B, p. 5).

## 7. Dataset and System Setting

- Public / Private: **Public code and dataset are stated by the paper.** Code: `https://github.com/CSTCloudOps/RCAgentBench`; the dataset is referred to as `RCAgentDataset` (Source: Abstract, p. 1; Sec. III, p. 3).
- Production / Synthetic: **Controlled, realistic testbed with injected faults.** It is not a production deployment study (Source: Sec. III, p. 3).
- Observation duration: The query supplies an anomaly start/end window. The metrics tool additionally uses the preceding 30 minutes as its default baseline; an exact common window length for every case is not stated in the available paper (Source: Sec. II-A, p. 2; Sec. IV-B, p. 5).
- Number of incidents: 400 fault cases (Source: Sec. III, p. 3).
- Number of devices / services / nodes: 10 core microservices, three pods per service, distributed across eight VMs; three TiDB components share the VMs (Source: Sec. III, p. 3).
- Topology: Kubernetes/microservice dependencies and service call chains. The paper uses these as system context and as part of diagnostic evidence, not as a learned physical network topology (Source: Sec. III, p. 3; Fig. 6, p. 9).

## 8. Core Method

RCAgentBench standardizes three things: the multimodal diagnostic environment, the tool interface, and a set of single- and multi-agent workflow patterns. It then runs the patterns with different language models and scores both diagnosis quality and process-level behavior (Source: Sec. IV, pp. 4–6; Fig. 3, p. 4).

The standard case schema contains the UUID, time range, fault category/type, instance type, service and instance, source/destination when relevant, key observations, key metrics, and a fault description (Source: Table II, p. 4).

The paper evaluates single-agent ReAct, CoT, Reflection, Plan-Execute, and Workflow patterns, plus multi-agent RMAgent, DJAgent, and PDAgent. These are benchmarked patterns, not evidence that all patterns share one canonical Agent architecture (Source: Sec. IV-A, pp. 4–5; Fig. 3, p. 4).

## 9. Architecture / Workflow

The common interaction loop can be written as:

```text
Case UUID + anomaly window
→ agent chooses a diagnostic tool
→ metrics / logs / traces are queried
→ returned observations are added to the current context
→ agent reasons or coordinates with other roles
→ component, fault type, and explanation are emitted as JSON
```

For a ReAct-like pattern, the runtime shape is approximately:

```text
Task
→ reasoning
→ tool action
→ observation
→ reasoning
→ ...
→ final diagnosis
```

For the multi-agent patterns, the work is divided into roles such as data collection, diagnosis, validation, review, judging, or planning. For example, RMAgent uses DataCollector → Diagnostic → Validator → Reviewer, while PDAgent uses Planner → Diagnostic (Source: Sec. IV-A, pp. 4–5; Fig. 3, p. 4).

`Observation` is operational evidence returned by a tool. It grounds later reasoning in the selected time window and can expose relationships that a single metric cannot, such as a service call chain or an error message tied to a pod (Source: Sec. IV-B, p. 5; Fig. 6, p. 9).

## 10. Detection Method

The benchmark does not evaluate a standalone incident detector. The query gives the anomaly interval. Within that interval, the metrics tool compares observations to the previous 30-minute baseline using a default three-sigma rule; optional thresholds or plugins are possible. The logs tool applies error/failure/exception keyword filtering, and the traces tool checks latency and request-ratio deviations against baseline (Source: Sec. IV-B, p. 5).

Thus, detection-like operations are tool-level evidence extraction. The final RCA still has to determine which component and fault type explain the case.

## 11. RCA / Localization Method

The RCA pipeline is:

```text
raw metrics / logs / traces
→ standardized per-modality tool query
→ anomaly or error evidence
→ agent-specific reasoning / role collaboration
→ component localization and fault-type ranking
→ explanation with supporting observations
```

Candidate roots are system components at service, pod, node, or related fault levels. The agent is not given a fixed pre-filtered root-cause list; tools are called against the case window and the workflow reasons over the returned evidence (Source: Sec. II-A, p. 2; Sec. III, p. 3).

**Candidate space and pruning:** The paper does not state one fixed numeric candidate-space size or a separate candidate-pruning algorithm. The system has 10 services, 30 pods, and node-level fault cases, but the exact number of possible diagnostic candidates under every fault level is **Unclear / Not explicitly stated in the paper**. Workflow structure, system information, and tool evidence constrain the search informally. Fault-level hierarchy is an important prior: removing it sharply degrades localization (Source: Sec. V-D, Table V, p. 8).

## 12. Diagnosis / Classification Method

Diagnosis has two separable outputs:

1. **Location:** which component is faulty.
2. **Type:** what fault category or fault mechanism occurred.

The type score first uses keyword matching against annotated metric keywords; otherwise it uses semantic similarity from `all-mpnet-base-v2`. The type score is halved when component localization is wrong, which makes the metric penalize a plausible fault description attached to the wrong component (Source: Sec. V-A, pp. 5–6).

Explainability is scored by matching the agent's cited observations to the annotated observations. Metrics use binary keyword matching, while logs and traces use proportional keyword matches (Source: Sec. V-A, p. 6).

## 13. LLM / Agent Role

- LLM: **Yes.** Multiple language models are used as the reasoning backbones; the exact model and pattern combinations are reported in Tables III and IV (Source: Sec. V-B, pp. 6–8).
- Tool-augmented LLM: **Yes.** The agent calls standardized metric, log, and trace tools rather than reasoning over a static prompt only (Source: Sec. IV-B, p. 5).
- Agent: **Yes, for the benchmarked workflows.** The workflows select actions, receive observations, and in multi-agent settings coordinate diagnostic roles. The benchmark evaluates this behavior rather than asserting that every LLM call is an Agent.
- Planning: **Pattern-dependent.** Plan-Execute and PDAgent include an explicit planning role; ReAct and Workflow use different runtime organizations. The benchmark does not establish one universal planner architecture (Source: Sec. IV-A, pp. 4–5).
- Memory: The current case trajectory and tool observations remain in the task context. A persistent or long-term Agent memory system is **Unclear / Not explicitly stated in the paper**.
- Reflection: A Reflection pattern is included among benchmark configurations, but the paper does not make reflection a universal component of every workflow (Source: Sec. IV-A, p. 4).

## 14. Ground Truth

Ground truth is represented in the annotated case schema: fault category/type, instance type, service, instance, source/destination where applicable, key observations, key metrics, and a fault description (Source: Table II, p. 4).

The incidents are injected with Chaos-Mesh, so the fault mechanism and affected component are controlled by the benchmark construction. The paper does not describe these as operator-labelled historical production incidents (Source: Sec. III, p. 3).

Ground-truth units include a component or instance, a fault type, and modality-specific evidence. Whether every case supports multiple simultaneous roots is **Unclear / Not explicitly stated in the paper**.

## 15. Baselines

The benchmark compares multiple agent patterns, including single-agent ReAct, CoT, Reflection, Plan-Execute, Workflow and multi-agent RMAgent, DJAgent, and PDAgent (Source: Sec. IV-A, pp. 4–5; Table III, p. 7).

It also varies the language model backbone, including Qwen3-4B/8B/32B, DeepSeek-V3, GPT-4o mini, and Claude Sonnet 4 in the reported comparisons (Source: Sec. V-B, Table III, p. 7; Table IV, p. 8).

These are primarily workflow/model baselines rather than a broad comparison with conventional graph-RCA or deep time-series RCA systems. The scope of alternative ML/deep diagnostic tools is listed as a limitation (Source: Sec. VIII, p. 9).

## 16. Metrics

- **Root Cause Location Accuracy (LA):** whether the predicted faulty component is correct; reported as LA-Top1 and LA-Top5 (Source: Sec. V-A, p. 5).
- **Root Cause Type Accuracy (TA):** whether the predicted fault type matches the annotated fault evidence, using keyword or semantic matching and penalizing wrong localization (Source: Sec. V-A, pp. 5–6).
- **Explainability:** the fraction of annotated key observations matched by the explanation, scored by modality-specific matching (Source: Sec. V-A, p. 6).
- **Average Path Length (APL):** average number of diagnostic call steps for cases whose root location is successfully found; it measures interaction cost, not answer quality alone (Source: Sec. V-A, p. 6).

The metric set therefore separates correctness, evidence coverage, and diagnostic effort.

## 17. Main Results

The reported results show that no single workflow dominates every metric or model size.

- With Qwen3-8B, ReAct reports LA-Top1 38.75, LA-Top5 58.25, TA 59.35, Explainability 24.00, and APL 2.2775. RMAgent has lower localization but higher explainability in the same table (LA-Top1 22.50, LA-Top5 32.25, TA 49.08, Explainability 40.59, APL 12.3825) (Source: Table III, p. 7).
- With Qwen3-32B, the workflow and multi-agent results remain mixed; Workflow reports LA-Top1 39.25 and RMAgent 40.50, while RMAgent's explanation score is 34.72 versus Workflow's 29.78 (Source: Table III, p. 7).
- With DeepSeek-V3, PDAgent reports LA-Top1 43.00, LA-Top5 56.25, TA 58.05, Explainability 32.57, and APL 10.185 (Source: Table III, p. 7).
- Across model backbones, the paper reports no monotonic improvement from simply increasing model size. Its interpretation is that tool design and diagnostic process constraints remain important bottlenecks (Source: Sec. V-B, Table IV, p. 8).
- Removing the fault-level hierarchy reduces Qwen3-8B ReAct LA-Top1 from 38.75 to 11.00 and LA-Top5 from 58.25 to 20.75, demonstrating that hierarchical system information is a useful structural prior (Source: Sec. V-D, Table V, p. 8).
- Tool ablations suggest that metrics can add noisy or less directly localizing evidence, while logs and traces can support more direct localization in some cases; metrics still improve explanation or robustness in relevant settings (Source: Sec. V-C, Fig. 4, pp. 7–8; Fig. 5, p. 9).

The results support the value of standardized multimodal interaction and process evaluation. They do not establish that one agent architecture is universally best, nor that larger LLMs alone solve RCA.

## 18. Scalability / Deployment

The evaluated system contains 10 services, 30 pods, and eight VMs, with 400 injected cases (Source: Sec. III, p. 3). This is useful benchmark scale but not evidence of hyperscale production deployment. The paper does not report sustained online deployment, production SLOs, or a network-infrastructure-scale experiment.

The benchmark is public and designed to standardize future comparisons. Its scalability beyond the supplied microservice testbed and the cost of richer tools are **Unclear / Not explicitly stated in the paper**.

## 19. Strengths

- Evaluates metrics, logs, and traces through a common tool interface rather than treating RCA as a static label-prediction task.
- Includes several single- and multi-agent workflow patterns, making orchestration choices visible.
- Scores localization, fault type, evidence coverage, and path length separately.
- Provides controlled fault types and structured evidence annotations, which improve experiment reproducibility.
- Makes the distinction between final answer quality and diagnostic process measurable.

## 20. Limitations

### Paper states

The paper identifies limited diversity of diagnostic tools and limited comparison with alternative ML/deep diagnostic tools. It suggests future work on Agentic RL, which is not implemented in this benchmark (Source: Sec. VIII, p. 9).

The testbed relies on injected microservice faults, so historical production incident diversity, unknown root causes, and operational noise are not fully represented (Source: Sec. III, p. 3; this is also a limitation of the experimental setting).

### My interpretation

The benchmark's standardized tools improve comparability but also define what an agent can observe. A result may therefore measure both model/workflow ability and the coverage and semantics of the supplied tools. This interpretation is consistent with the model-size and tool-ablation observations, but is not itself a direct author claim.

## 21. Reproducibility

- Code available? **Yes, stated:** `https://github.com/CSTCloudOps/RCAgentBench` (Source: Abstract, p. 1).
- Dataset available? **Yes, stated:** `RCAgentDataset` is linked/referred to by the paper (Source: Abstract, p. 1; Sec. III, p. 3).
- Benchmark available? **Yes, as the paper's public benchmark framing.**
- Prompt available? Workflow patterns and tool interfaces are described; the exact full prompt package is not reproduced in the paper and may require the repository.
- Model/API specified? **Yes, for the reported model comparisons** (Source: Sec. V-B, Tables III–IV, pp. 7–8).
- Hyperparameters? Partly; exact reproduction of all model/tool settings is **Unclear / Not explicitly stated in the paper**.
- Enough detail to reproduce? **Medium–High**, assuming the public repository and dataset are available; exact prompt and implementation details should be checked in the repository in a later code-reading task.

## 22. Relationship to Existing AIOps Knowledge

This paper is the most direct formal support in the current AIOps line for treating RCA as multimodal evidence gathering plus a diagnosable interaction process. It gives concrete examples of the following durable distinctions:

- Detection or evidence extraction is not the same as root-cause localization.
- Topology/call-chain context can constrain reasoning without being a learned causal model.
- Tool-based multimodal integration differs from feature-level multimodal fusion.
- Agent evaluation should include evidence coverage and action cost, not only the final label.

Related concepts:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md)
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md)
- [Agent](../../../concepts/agent.md)
- [Tool Use](../../../concepts/tool-use.md)
- [Planning](../../../concepts/planning.md)
- [Reasoning](../../../concepts/reasoning.md)

The links to Agent, Tool Use, Planning, and Reasoning are deliberately limited: the paper benchmarks patterns that use these ideas, but does not make its benchmark a general theory of Agents.

## 23. Relevance to My Research

### Similarities

- The paper directly studies fault localization and RCA under multiple operational evidence sources.
- Its metrics/logs/traces setting is close to a multimodal infrastructure diagnosis problem.
- Its hierarchical component levels and call-chain context are relevant to topology-aware diagnosis.
- Its explicit process metrics provide a useful way to evaluate an LLM/Agent RCA system beyond answer text.

### Differences

- The environment is a microservice application, not a network infrastructure with devices, interfaces, links, optical modules, traffic, or NetFlow.
- Faults are injected and the candidate environment is relatively controlled; real network incidents may have missing, delayed, or contradictory telemetry.
- The benchmark does not establish a network-specific topology representation or traffic-centric evidence path.

### Potentially Useful Ideas

- Define modality-specific tools with explicit time windows and output semantics.
- Evaluate Top-1/Top-k localization together with fault type, evidence coverage, and diagnostic path length.
- Use hierarchical infrastructure context to reduce or structure candidate root causes.
- Preserve an auditable reasoning/evidence trace rather than evaluating only a final natural-language answer.
- Compare tool/workflow choices separately from the language-model backbone.

### Assumptions That May Not Transfer

- Service/pod/node hierarchy may not map cleanly to physical network device/interface/link/module hierarchies.
- A three-sigma metric baseline and keyword extraction may be insufficient for bursty traffic, protocol counters, or NetFlow distributions.
- Injected faults may not represent correlated failures, unknown fault types, or operator workarounds.
- A service call chain is not automatically the same as a physical or causal network topology.

### Experiments Worth Considering

- Build a network analogue of the benchmark with metrics, syslog, traces where available, topology, and traffic/NetFlow as separately auditable tools.
- Compare flat candidates with hierarchical device/interface/link candidates and measure both localization and candidate-pruning cost.
- Test whether evidence coverage and APL remain useful when telemetry is missing or arrives out of order.
- Compare runtime tool-driven reasoning with a topology-constrained non-LLM baseline before attributing gains to LLM reasoning.

### Transferability to Network AIOps

**Medium.** The benchmark and evaluation design transfer well; the microservice fault taxonomy, service graph, and injected-data assumptions do not transfer directly to network infrastructure.

## 24. My Understanding

RCAgentBench is valuable less because it proposes one new RCA model and more because it makes the Agent RCA setting concrete. An agent receives a case window, chooses among evidence tools, observes metrics/logs/traces, and must produce a localized and typed diagnosis with support. The benchmark shows that a workflow can be better at evidence explanation while worse at localization, and that model size alone is not a sufficient explanation of performance.

The paper's “topology-aware” content should be read as structural service/call-chain context. It is not evidence that the benchmark learns a physical causal graph. Likewise, its Agent patterns should not be collapsed into one architecture: ReAct, Plan-Execute, Workflow, and the multi-agent patterns differ in when they decide, collect evidence, validate, and review.

## 25. Questions

- How should candidate root causes be defined when a network incident can involve multiple devices, interfaces, links, and fault types at once?
- How much of RCAgentBench's process-level metrics remains reliable when network telemetry is delayed, missing, or inconsistent across modalities?
- Can a learned or supplied network topology provide the same benefit as the paper's service hierarchy without being mistaken for physical causality?
- How much improvement comes from the tool definitions and fault-level hierarchy versus the LLM workflow itself?
- What evaluation protocol can cover unknown or previously unseen network fault types rather than only injected categories?

## 26. Source Grounding

Primary grounding used for this note:

- Abstract and Sec. I: motivation, benchmark scope, and public-resource claim.
- Sec. II-A–B, pp. 2–3: query format, task setting, and definitions of metrics/logs/traces.
- Sec. III, p. 3; Table I: HipsterShop environment, fault injection, and case scale.
- Sec. IV-A–B, pp. 4–5; Fig. 3: workflow patterns and diagnostic tools.
- Table II, p. 4: case annotation schema.
- Sec. V-A, pp. 5–6: LA, TA, explainability, and APL definitions.
- Table III, p. 7; Table IV, p. 8: model/workflow results and model-size comparison.
- Fig. 4–6, pp. 7–9; Table V, p. 8: tool, case, and fault-level-hierarchy analyses.
- Sec. VIII, p. 9: stated limitations and future direction.

The exact fixed size of the diagnostic candidate set, a production deployment claim, and a persistent Agent memory mechanism are **Unclear / Not explicitly stated in the paper**.

## 27. Tags

`AIOps` `RCA` `fault-localization` `multimodal-telemetry` `metrics` `logs` `traces` `microservices` `topology-context` `LLM` `Agent-evaluation` `tool-use`

## Code / Implementation

- Repository: [CSTCloudOps/RCAgentBench](https://github.com/CSTCloudOps/RCAgentBench)
- Official status: Confirmed Official
- Read at commit: `ab14bba1948202416535803825e1d58cfab391bd`
- Code notes: [RCAgentBench source-code notes](../../../code/aiops/rcagentbench/notes.md)
- Implementation coverage: Multimodal data tools, several agent variants, the three-phase workflow, and shared evaluation infrastructure.
