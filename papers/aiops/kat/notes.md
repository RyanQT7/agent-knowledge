Status: Full Reading: Completed

# KAT: Knowledge-Context Augmentation for Evolving LLM-Based Telecom Troubleshooting

## 1. Metadata

- Title: KAT: Knowledge-Context Augmentation for Evolving LLM-Based Telecom Troubleshooting
- Authors: Kai Qian, Feng Lyu, Hao Wu, Jing Gao, Shucheng Li, Fan Wu, Qiong Luo, Bowen Chen, Fengyuan Xu
- Year: 2026
- Venue: IEEE International Conference on Computer Communications (INFOCOM) 2026
- URL / DOI: https://doi.org/10.1109/INFOCOM59046.2026.11571301
- Local File: [KAT PDF](../../../sources/papers/AIOps_papers/INFOCOM26-KAT_Knowledge-Context_Augmentation_for_Evolving_LLM-Based_Telecom_Troubleshooting.pdf)
- Paper ID: `kat`

## 2. One-Sentence Summary

KAT combines a troubleshooting knowledge graph, cross-subsystem context retrieval, and feedback-driven continuous improvement to help an LLM diagnose evolving telecom business-support errors and recommend actionable solutions in a commercial deployment.

## 3. Problem Setting

### Paper states

KAT targets troubleshooting in a Telecom Business Support System (TBSS). The system contains many interacting subsystems and changing error patterns: the paper describes roughly 4,000 error types and more than 100 root causes, while a user's report often provides only partial context (Source: Abstract; Sec. I, pp. 1–3).

The paper motivates structured knowledge because direct LLM prompting lacks domain context and embedding-only retrieval is sensitive to noisy, entity-rich descriptions. Its goal is to retrieve interpretable cases, recover the relevant cross-subsystem context, and adapt to newly appearing errors (Source: Sec. I–II, pp. 1–4; Sec. IX-B, p. 9).

### My interpretation

KAT is primarily a knowledge-grounded troubleshooting and diagnosis system. It is not a conventional raw-telemetry anomaly detector, and its paper evidence does not establish a full multi-step autonomous Agent loop. Its central challenge is incomplete, evolving operational context rather than action selection in an external environment.

## 4. AIOps Task

- Detection: **No separate detection method is evaluated.** A user-reported error or system error order triggers troubleshooting.
- RCA: **Yes, in an operational diagnosis sense.** The generated response identifies a root cause or responsible subsystem and recommends a solution (Source: Sec. V, pp. 5–6; Sec. VIII, p. 8).
- Localization: **Partly.** Context and solution paths identify relevant TBSS subsystems, but the paper does not define a device/interface/link localization metric.
- Diagnosis: **Yes.** The system maps error descriptions and context to root causes and solution steps (Source: Abstract; Sec. III–V, pp. 4–6).
- Prediction: No.
- Remediation: **Recommendation/support.** KAT returns recommended solution steps; the paper evaluates troubleshooting quality and deployment outcomes, not autonomous execution of network repair actions.

The task is:

```text
user/system error report
→ entity extraction and knowledge-graph retrieval
→ cross-subsystem context enhancement
→ LLM root-cause and solution generation
→ user/operator feedback
→ knowledge/model update
```

The input error is already an incident signal. Finding an abnormal event and diagnosing its root are not the same operation here.

## 5. Failure / Incident Setting

The setting is a commercial TBSS serving telecom business operations. The paper describes subsystems including CRM, Orchestration Center, Resource Center, Control Center, Network Elements, and Operations Scheduling Center (Source: Sec. I, Fig. 1, p. 1; Table I, p. 2).

The system handles diverse user-reported and system-generated error orders, including cross-subsystem activation or resource errors. Figure 9 gives an example in which an IP/network-management order fails because of an address conflict or mismatch and KAT recommends checks across the relevant operational systems (Source: Fig. 9, p. 9).

## 6. Data Modalities

- Metrics: Not explicitly stated as a raw input modality for the main method.
- Logs: Not explicitly stated as a raw input modality for the main method.
- Traces: Not explicitly stated as a distributed-trace modality.
- Alarms: System error orders/events act as incident triggers, but a formal alarm stream is not separately defined.
- Topology: **Yes, as a TBSS subsystem dependency/property graph.** It represents functions and relationships among business-support subsystems, not a physical network topology (Source: Sec. V, pp. 5–6).
- Traffic: No.
- NetFlow: No.
- Configuration: Cross-subsystem context may describe system state, but a standalone configuration telemetry stream is **Unclear / Not explicitly stated in the paper**.
- Tickets: **Yes in the broad operational-report sense.** User-reported errors, cases, and O&M records form the knowledge and evaluation corpus (Source: Sec. IV-A, p. 4; Sec. VII, p. 7).
- Other: Free-text error descriptions, extracted entities, troubleshooting knowledge graph, solution rules, subsystem context, expert labels, user-satisfaction feedback, and model-update data.

**Structured text plus graphs, not classical multimodal telemetry.** KAT combines text/entity information with two graph-based knowledge/context structures. The paper does not present metrics+logs+traces feature fusion. Its augmentation happens at retrieval and prompt/context level.

## 7. Dataset and System Setting

- Public / Private: **Private commercial telecom data and system context.** The paper does not state a public release of the TBSS corpus, graphs, or code.
- Production / Synthetic: **Real production data and production deployment.** The system was deployed in a commercial TBSS environment and evaluated on real user-reported errors (Source: Sec. VIII, p. 8; Figs. 9–10, p. 9).
- Observation duration: There is no fixed per-incident telemetry window described for KAT. The paper does report longitudinal feedback and deployment periods; a diagnosis time-window definition is **Unclear / Not explicitly stated in the paper**.
- Number of incidents: The labelled corpus contains 54,537 cases; the held-out test set contains 3,612 real user-reported errors (Source: Sec. VII, p. 7).
- Number of devices / services / nodes: The TBSS subsystem graph contains 957 context nodes, 1,776 error nodes, and 935 solution nodes in the TKG; the number of physical network devices is not reported (Source: Sec. IV-B, p. 5).
- Topology: A directed property graph of TBSS subsystem/function relationships, plus the TKG's error-context-solution relations (Source: Sec. IV and V, pp. 4–6).

The production context is large in users and operational volume: the paper reports a commercial system serving about 35 million users and more than 80,000 system errors per month in the introduction. It also reports deployment/test growth, satisfaction, and resolution-time changes (Source: Sec. I, pp. 1–3; Sec. VIII, p. 8).

## 8. Core Method

KAT has three main components:

1. **Troubleshooting Knowledge Graph (TKG):** stores entities and relations among errors, contexts, and solutions.
2. **TBSS Context Enhancement:** retrieves the directly interacting subsystems relevant to an error so the LLM sees more complete but bounded context.
3. **Efficient Continuous Improvement:** uses user feedback and expert relabeling to refine the graph and adapt the model (Source: Sec. III, p. 4; Sec. IV–VI, pp. 4–7; Fig. 3, p. 4).

The TKG contains 957 context nodes, 1,776 error nodes, and 935 solution nodes. The authors manually label 712 solution nodes where references are missing and construct 2,426 high-quality troubleshooting rules, each containing one to four steps (Source: Sec. IV-B, p. 5).

## 9. Architecture / Workflow

```text
user-reported error
→ entity extraction
→ TKG entity-centric forward/backward traversal
→ ranked error/context/solution cases
→ retrieve directly interacting TBSS subsystems
→ prompt LLM with cases + enhanced context + user error
→ root cause and recommended solution
→ satisfaction / expert feedback
→ graph refinement and LoRA or in-context adaptation
```

TKG retrieval creates context-to-error-to-solution paths and error-to-solution paths. The paper weights the error-centred path more strongly (`α=1`, `β=2` in the described scoring), then deduplicates and ranks candidate cases for the prompt (Source: Sec. IV-C, p. 5; Fig. 5, p. 5).

Context enhancement uses a directed property graph of TBSS subsystems. Rather than inserting every subsystem, it retrieves the directly interacting subsystems associated with the error-throwing subsystem, which keeps the prompt bounded while adding cross-layer context (Source: Sec. V, pp. 5–6).

There is no separately described Planner, Executor, tool loop, or environment observation loop. The LLM generates a troubleshooting response from retrieved and enhanced context. Therefore, the paper supports “LLM-based troubleshooting” more strongly than “full Agentic RCA.”

## 10. Detection Method

KAT assumes a user or system has already produced an error report/order. Entity extraction and graph traversal determine which known cases and contexts may explain the report, but the paper does not train/evaluate an independent detector for whether the underlying system is abnormal.

The online inference task is consequently diagnosis and solution generation conditioned on an incident description, not detection from raw time-series telemetry.

## 11. RCA / Localization Method

The practical diagnosis path is:

```text
free-text error / entities
→ retrieve related TKG paths
→ identify relevant TBSS subsystem interactions
→ augment LLM context
→ generate root cause + solution steps
```

### Candidate space

KAT retrieves reference cases and solution paths rather than defining a fixed explicit set of root-cause candidates. The LLM produces the final root-cause/solution text. The exact number of root-cause candidates considered for each query is **Unclear / Not explicitly stated in the paper**.

### Candidate pruning

Traversal, path scoring, deduplication, Top-K case selection, and direct-neighbor subsystem retrieval reduce the context before LLM generation (Source: Sec. IV-C and Sec. V, pp. 5–6). This is retrieval/context pruning, not a formal causal candidate-ranking algorithm.

## 12. Diagnosis / Classification Method

The output is a natural-language root-cause explanation and actionable troubleshooting solution. Evaluation compares generated solutions with reference answers using lexical and semantic text metrics, rather than a dedicated device/fault-type classification protocol (Source: Sec. VII, pp. 7–8).

Exact match is low because equivalent troubleshooting steps may use different wording; the paper therefore emphasizes semantic BERT-based metrics for answer quality (Source: Sec. VII, p. 7).

## 13. LLM / Agent Role

- LLM: **Yes.** KAT uses an LLM to generate the root cause and solution from the user error, retrieved cases, and enhanced TBSS context (Source: Sec. V, pp. 5–6; Sec. VII, p. 7).
- Tool-augmented LLM: **Not established.** The system retrieves graph context, but the paper does not describe a multi-step runtime tool-calling loop that queries live telemetry.
- Agent: **No / unclear.** The paper presents an LLM-based troubleshooting system and does not establish a Planner–Executor or repeated environment interaction architecture. This should not be labelled a full Agent merely because it retrieves knowledge and produces an action recommendation.
- Planning: Not explicitly established. Solution steps are generated as an answer, but a separate plan representation or planner is not described.
- Memory: The TKG and refined cases are persistent operational knowledge, not necessarily Agent memory. The graph stores domain facts/cases and can be updated; it is closer to a knowledge base / structured retrieval layer than a task trajectory memory.
- Reflection: User satisfaction and expert relabeling drive continuous improvement, but this is system/data/model updating, not Reflexion-style verbal feedback within an Agent attempt.

The useful boundary is:

```text
retrieval + context augmentation + LLM generation
≠
multi-step Agent interaction with tools and environment
```

## 14. Ground Truth

Fifteen O&M experts label a corpus of 54,537 troubleshooting cases. The reported test set contains 3,612 real user-reported errors, with reference troubleshooting solutions used for evaluation (Source: Sec. VII, p. 7).

The ground truth is primarily a reference answer/solution and associated error/context entities. The paper does not present a complete physical root-cause graph, exact fault onset interval, or a multi-root label protocol. Those details are **Unclear / Not explicitly stated in the paper**.

The continuous-improvement stage uses expert relabeling for unsatisfactory cases. SentenceTransformer embeddings and DBSCAN cluster reference cases, representative cases are selected, and remaining cases receive automatic labels based on nearest in-cluster representatives (Source: Sec. VI-A, p. 6; Fig. 6, p. 7).

## 15. Baselines

The paper compares KAT with BM25, AMIE, MiniLM, Qwen-7B-Chat without the full KAT context, GPT-3.5-turbo, GPT-4o, and NetLLM (Source: Sec. VII, p. 7; Table II, p. 7).

The comparison includes lexical retrieval, embedding/relation methods, general LLMs, and a networking-oriented LLM baseline. It is primarily an answer-generation/troubleshooting comparison, not a topology-aware RCA benchmark with common root-cause labels.

## 16. Metrics

- **Jaccard:** overlap between generated and reference answer sets/terms.
- **BLEU:** n-gram precision-oriented similarity to the reference solution.
- **Exact Match (EM):** whether the generated answer exactly matches the reference; strict and sensitive to wording.
- **ROUGE-L:** longest-common-subsequence based overlap, reflecting sequence similarity.
- **BERT-Precision / Recall / F1:** semantic similarity between generated and reference answers; the paper emphasizes BERT-F1 for semantically equivalent solution wording (Source: Sec. VII, p. 7; Table II, p. 7).

These metrics measure answer similarity and semantic adequacy. They do not directly measure physical fault localization, causal correctness, or whether a recommended action is safe.

## 17. Main Results

### Main comparison

The full KAT system reports Jaccard 11.70, BLEU 11.71, EM 11.27, ROUGE-L 27.53, BERT-Precision 86.02, BERT-Recall 87.54, and BERT-F1 86.53 (Source: Table II, p. 7).

The paper reports improvements over the best baseline of 10.92, 10.93, 10.49, 13.81, 6.84, 2.52, and 5.14 respectively for those metrics (Source: Table II, p. 7). Because exact-match-style metrics remain low while semantic metrics are high, the result should be read as improved troubleshooting-answer quality rather than exact root-cause label accuracy.

### Generalization and compression

Figure 7 compares same, new, and incomplete error descriptions; KAT maintains higher semantic BERT-F1 across the reported conditions, although exact numeric values are not given in the text (Source: Fig. 7, p. 8).

The representative-case experiment reports that `R=2` representatives are close to peak BERT-F1 with a compression ratio around 10 (Source: Sec. VII, Fig. 8, p. 8). This is evidence for a compact reference-case strategy in the tested corpus, not a general guarantee that two examples suffice for another domain.

### Ablation

The ablation in Table III shows that removing entity/context enhancement, knowledge-graph retrieval, or context enhancement degrades the result, and the LLM-only condition is much worse. The exact module-row values are in Table III, p. 8; the durable conclusion is that the graph, context, and LLM components are complementary rather than interchangeable.

## 18. Scalability / Deployment

KAT reports actual commercial deployment. The paper states that it was deployed in a real-world telecom environment, with production use beginning in March 2024. It reports growth from roughly 5–6 thousand calls per month to more than 27 thousand by December 2024, deployments across 15 provinces/cities, and 10–20 thousand monthly invocations in deeper collaborations that handled about 25% of error orders (Source: Sec. VIII, p. 8; Figs. 9–10, p. 9).

The introduction also reports a commercial TBSS serving about 35 million users and more than 80,000 system errors per month. Over the deployment/testing period, average error duration fell from 51.4 hours to 5.9 hours and user satisfaction rose from 47% to about 97–99% (Source: Sec. I, pp. 1–3; Sec. VIII, p. 8; Fig. 9, p. 9).

These are production deployment and operational outcome claims, not merely offline evaluation. They do not by themselves prove that every generated root cause is physically correct; the reported quality metrics compare answers with reference solutions.

## 19. Strengths

- Addresses evolving, noisy, entity-rich telecom troubleshooting rather than only a static benchmark.
- Uses interpretable graph paths and cross-subsystem context instead of relying on embedding similarity alone.
- Includes a feedback-driven update process for cases, graph knowledge, and model adaptation.
- Demonstrates commercial deployment, operational volume, user satisfaction, and resolution-time outcomes.
- Uses representative-case selection to control prompt/context growth.

## 20. Limitations

### Paper states

The paper's related-work and conclusion discussion identifies high construction/maintenance cost of domain knowledge, insufficient cross-system context in prior approaches, and limited adaptation to new errors as motivating issues. KAT still depends on expert labels, graph maintenance, and a private TBSS environment (Source: Sec. IX, p. 9; Sec. IV–VI, pp. 4–7).

The evaluation uses a commercial setting and does not provide a public physical network dataset or open benchmark. The paper does not claim autonomous repair or a complete live telemetry diagnosis loop.

### My interpretation

KAT's knowledge graph can be persistent and updateable without being Agent memory. It is also retrieval/context augmentation rather than proof that the LLM performs causal inference. Its success may depend substantially on the quality of entity extraction, graph construction, reference solutions, and expert feedback.

## 21. Reproducibility

- Code available? **Not stated as publicly available.**
- Dataset available? **No; the TBSS corpus and graph are private.**
- Benchmark available? No independent public benchmark is described.
- Prompt available? Prompt contents and context fields are described, but the complete prompt/configuration is not released.
- Model/API specified? Qwen-7B-Chat is used for the prototype; GPT-3.5/4o appear as baselines (Source: Sec. VII, p. 7).
- Hyperparameters? Important graph/retrieval settings and representative-case details are described, but full production configuration is not public.
- Enough detail to reproduce? **Low–Medium.** The component design is understandable, but private data, TBSS graph, expert labels, and deployment context prevent direct reproduction.

## 22. Relationship to Existing AIOps Knowledge

KAT adds a knowledge-centered diagnosis pattern to the current batch:

- Unlike RCAgentBench, it does not explicitly fuse metrics, logs, and traces through runtime tools.
- Unlike StaR, it does not learn a temporal causal graph or rank metric variables.
- Unlike CAUSALDX, it does not perform an explicit select–expand–verify causal search over anomaly nodes.
- Unlike LLMGuard, it does not compile a deterministic SOP Checking Tree for runtime tool execution.
- It shows how a persistent, interpretable operational knowledge graph and evolving context can improve an LLM answer without thereby creating a full Agent architecture.

Related concepts:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md)
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md)
- [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md)
- [Agent](../../../concepts/agent.md)
- [Memory](../../../concepts/memory.md)
- [Context Engineering](../../../concepts/context-engineering.md)

The graph is a knowledge/context store, not automatically a memory module in the Agent sense; the subsystem graph is operational dependency context, not physical network topology.

## 23. Relevance to My Research

### Similarities

- It is directly situated in telecom/network operations and handles cross-subsystem failures.
- It addresses evolving errors, incomplete user context, and the need for interpretable operational knowledge.
- It reports a real deployment with large user/error volume and outcome metrics.
- Its entity/context/solution representation is relevant to connecting network symptoms with domain-specific diagnosis actions.

### Differences

- The main input is user/system error text and structured troubleshooting knowledge, not raw metrics, syslog, traces, traffic, or NetFlow.
- The topology is a TBSS business/subsystem dependency graph, not a physical network topology of devices, interfaces, links, or optical modules.
- Evaluation is answer similarity and user/service outcomes, not root-node top-k accuracy or causal-edge correctness.
- The paper does not establish a multi-step Agent that actively queries live telemetry or executes remediation.

### Potentially Useful Ideas

- Build an entity-centric graph linking network error descriptions, context, components, root causes, and solution steps.
- Retrieve directly interacting subsystems/components to enrich incomplete incident reports without flooding the context.
- Separate stable knowledge graph updates from model adaptation and use expert feedback for difficult cases.
- Use representative-case compression to control context growth.
- Track user/operator feedback, resolution time, and satisfaction together with technical correctness.

### Assumptions That May Not Transfer

- Free-text telecom business reports may be richer or poorer than raw network telemetry depending on the incident path.
- A subsystem dependency graph cannot substitute for dynamic physical topology or traffic paths.
- Reference solutions and expert labels may encode local operational policy rather than universally correct root causes.
- Text-semantic metrics can hide an unsafe or physically incorrect recommendation.
- Private graph maintenance and expert feedback may be difficult to reproduce in a new network environment.

### Experiments Worth Considering

- Construct a network troubleshooting graph linking syslog/error entities to devices, interfaces, links, topology context, and verified actions.
- Compare text-only, graph-retrieval, and graph-plus-live-telemetry context for the same incidents.
- Evaluate new/unknown/incomplete error descriptions with hierarchical root localization and semantic solution quality separately.
- Test representative-case compression under changing fault types and measure stale-knowledge effects.
- Add safety review and operator acceptance metrics for generated remediation recommendations.

### Transferability to Network AIOps

**Medium.** The knowledge/context lifecycle and telecom operational setting transfer well; raw telemetry, physical topology, traffic evidence, and direct root-cause evaluation require additional design.

## 24. My Understanding

KAT solves a context problem. It takes an incomplete error report, walks an interpretable graph of errors, contexts, and solutions, adds only the relevant cross-subsystem context, and asks an LLM to produce a root cause and solution. Its continuous-improvement loop uses feedback and expert relabeling to update the graph and model.

The system should be described carefully: it is an LLM-based, graph-grounded troubleshooting workflow deployed in telecom operations, but the paper does not demonstrate a full Planner–Tool–Observation Agent loop. Its TKG is persistent operational knowledge, not automatically Agent memory; its subsystem graph is contextual dependency, not a physical causal network topology; and its answer metrics are not the same as RCA localization metrics.

## 25. Questions

- How can a troubleshooting graph connect free-text errors with raw metrics, syslog, traces, traffic, and physical topology while preserving provenance?
- How should stale or contradictory graph knowledge be detected before it changes an LLM diagnosis?
- Can KAT-style context retrieval improve root-node localization, not only semantic solution similarity?
- What is the right update/forgetting policy when a telecom error pattern or network configuration changes?
- How should a graph-grounded recommendation be verified before it becomes a remediation action?
- How can user satisfaction and resolution-time improvements be separated from true fault-cause correctness?

## 26. Source Grounding

Primary grounding used for this note:

- Abstract and Sec. I–II, pp. 1–4: TBSS problem, evolving errors, cross-subsystem context, and motivation.
- Sec. III–IV, pp. 4–5; Fig. 3 and Fig. 5: KAT overview, TKG construction, nodes/edges, traversal, and retrieval.
- Sec. V, pp. 5–6: TBSS context enhancement through subsystem graph.
- Sec. VI, pp. 6–7; Fig. 6: continuous improvement, expert feedback, clustering, and graph/model updates.
- Sec. VII, pp. 7–8; Tables II–III; Figs. 7–8: dataset, baselines, metrics, results, generalization, compression, and ablation.
- Sec. VIII, p. 8; Figs. 9–10, p. 9: deployment, usage, satisfaction, resolution time, and provincial expansion.
- Sec. IX–X, pp. 9–10: related work limitations and conclusion.

The exact per-incident telemetry window, root-cause candidate count, physical topology representation, public code/data release, and autonomous remediation evaluation are **Unclear / Not explicitly stated in the paper**.

## 27. Tags

`AIOps` `telecom` `troubleshooting` `fault-diagnosis` `RCA` `knowledge-graph` `context-augmentation` `continual-improvement` `production-deployment` `LLM` `not-necessarily-Agent` `operational-knowledge`
