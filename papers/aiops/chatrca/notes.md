# ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop

## 1. Metadata

- Title: ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop
- Authors: Mingxuan Hui, Lu Wang, Qingshan Li, Luyan Zhang, Zhongliang Bai, Jingzhao Hu, Hao Li, Ren Yang, Fei YueSong, Yimian Wang, Tao Sun, and Liwen Luo
- Year: 2026
- Venue: ACM Transactions on Software Engineering and Methodology (TOSEM)
- URL / DOI: https://doi.org/10.1145/3842744
- Local File: [Source PDF](../../../sources/papers/AIOps_papers/TOSEM26-CharRCA-Wanglu.pdf)
- Paper ID: chatrca

## 2. One-Sentence Summary

ChatRCA decomposes cloud incident RCA into specialized Manager, Observation, Architecture, Operation, and domain Expert roles, shares a conversation context through AutoGen, and inserts human verification at data-ticket and root-cause checkpoints; it improves service/component localization and root-cause-category prediction, but does not execute autonomous remediation (Source: Abstract; Sec. 3–5).

## 3. Problem Setting

Cloud incident RCA must combine large and heterogeneous evidence, dynamic service dependencies, domain-specific expertise, and repeated hypothesis checking. The authors' empirical study with experienced operations personnel finds that real RCA is iterative and interdependent rather than a simple linear sequence: engineers collect data, analyze it, exchange domain knowledge, form hypotheses, and confirm conclusions across roles (Source: Sec. 2–3).

The paper targets the gap between a monolithic LLM prompt and the collaborative, cautious workflow used by cloud operations teams. It asks how specialized LLM roles and targeted human feedback can improve localization, root-cause category prediction, and explanation quality. ChatRCA is an RCA workflow, not a new anomaly detector, universal causal model, or automatic repair system (Source: Sec. 1, Sec. 3.2, Sec. 4.1).

## 4. AIOps Task

- Detection: **Upstream / not the main contribution.** ChatRCA receives an abnormal incident or alert and collects evidence; it does not propose an anomaly detector (Source: Sec. 2.1, Sec. 4.2).
- RCA: **Yes.** It synthesizes multi-source evidence and domain analyses into a root-cause report.
- Localization: **Yes.** It ranks faulty services/components with Top-1 and Top-3 evaluation.
- Diagnosis: **Yes.** It predicts a predefined root-cause category and produces a natural-language RCA explanation.
- Prediction: **No future-failure prediction.** Root-cause category prediction is a diagnosis output, not forecasting.
- Remediation: **No direct execution.** The output can support a human mitigation decision, but ChatRCA does not invoke a repair or configuration-changing action in the evaluated workflow.

The note keeps these outputs separate: locating a suspicious service/component, assigning a fault category, and generating an explanation are related but not equivalent claims (Source: Sec. 5.4–5.5).

## 5. Failure / Incident Setting

The motivating enterprise example comes from the Panji Cloud Platform of China Mobile. The incident workflow includes an alert, data collection, observations of latency/throughput and resource state, cross-role hypotheses, and a final conclusion that a middleware/database timestamp issue caused distributed-query failure; the example was resolved by reverting a component version. This illustrates the human workflow that inspired ChatRCA, not an autonomous repair performed by ChatRCA (Source: Sec. 2.1, Fig. 2).

The operational process described by the 20 interviewed experts has three broad, interdependent activities:

```text
Data collection
→ comprehensive analysis / drill-down
→ root-cause hypothesis and confirmation
↺ collect more evidence or involve another domain when needed
```

The paper reports that 95% of participants emphasized metric and log collection, 45% mentioned trace collection, and 60% mentioned step-by-step drill-down analysis (Source: Sec. 3.2, Fig. 4).

## 6. Data Modalities

- Metrics: **Yes.** Monitoring indicators are used by the Observation Agent and appear in the datasets.
- Logs: **Yes.** The Observation Agent extracts relevant log segments; D1–D3 include log evidence where available.
- Traces: **Yes where available.** TrainTicket and GAIA expose traces; the private CMCC dataset explicitly has no trace data (Source: Sec. 5.2).
- Alarms: **Yes / incident triggers.** Alerts and abnormal incident inputs initiate the workflow.
- Topology: **Yes, as architecture/dependency context.** The Architecture Agent retrieves static service dependencies and dynamic node, container, pod, IP, and affiliation information. This is not a learned physical topology RCA graph.
- Traffic: **Not separately evaluated.** Network-related metrics may appear, but traffic/packet/flow telemetry is not defined as an independent modality.
- NetFlow: No.
- Configuration: **Limited / indirect.** Service and deployment state are supplied as architecture context; a general configuration-diff pipeline is not defined.
- Tickets: **Yes.** The Observation Agent produces a structured data ticket, and enterprise incidents contain descriptions and RCA records.
- Other: Historical incident cases, postmortems, domain knowledge, service status, pod/container information, and human feedback.

**Single-modal / Multi-modal:** **Multi-source and multimodal when traces are available.** ChatRCA uses metrics, logs, traces, service status, dependency information, and incident text through separate role/tool interfaces rather than a single feature-level fusion model. The D2 private CMCC setting is metric/log based because traces are unavailable (Source: Sec. 4.2, Sec. 5.2).

## 7. Dataset and System Setting

- Public / Private: D1 TrainTicket and D3 GAIA are open-source datasets; D2 is a private China Mobile enterprise-cloud dataset. The paper also states that implementation code and empirical-study data are available at [leocache/ChatRCA](https://github.com/leocache/ChatRCA), while also saying the materials will be made open-source in the future; current availability should be verified separately (Source: Sec. 5.2, Sec. 9).
- Production / Synthetic: D1 and D3 are benchmark/fault-injection settings. D2 contains 100 real incidents and 20 active fault-injection drill incidents collected from an enterprise cloud platform; the D2 evaluation retains 60 cases after filtering (Source: Sec. 5.2).
- Observation duration: D2 incidents are collected from the past year. The exact per-incident observation window is described as fixed around the event but its duration is not explicitly stated (Source: Sec. 4.2, Sec. 5.2).
- Number of incidents: D1 has 45 fault instances; D2 starts with 120 candidate incidents, retains 60; D3 is evaluated on 41 cases with three root-cause categories. Human disagreement analysis covers 146 cases across the three datasets (Source: Sec. 5.2, Sec. 5.8.3).
- Number of devices / services / nodes: D1 has 41 microservices. D2 has 43 master host nodes in two regions, 140 services, 311 pods, and 382 containers. D3 uses 10 service instances in MicroSS (Source: Sec. 5.2).
- Topology: D1/D2 use service dependency and architecture information; D2 also has node/container/pod relationships. No physical network topology, interface/link graph, or topology versioning protocol is evaluated.

The paper reports deployment feedback from a cloud operations department, but it does not provide a separate controlled analysis of online traffic volume, duration, intervention latency, or autonomous remediation success. Production data, deployment/usefulness feedback, and production automation should therefore remain separate claims.

## 8. Core Method

ChatRCA uses six role types:

1. **Manager Agent:** coordinates the speaking order and selects which role should contribute next based on the current context and environment observations.
2. **Observation Agent:** queries observability sources, extracts and processes metrics, logs, and traces around the incident, and produces a standardized data ticket. Human verification is requested for this ticket.
3. **Architecture Agent:** retrieves static service dependencies and dynamic node/container/pod details to give other roles architecture context.
4. **Expert Agents:** represent domain specialists such as network, resource, middleware, database, or other operational domains. Each can decide whether historical cases/knowledge are needed, retrieve them through a RAG skill, form a hypothesis, and assess whether current data support it.
5. **Operation Agent:** organizes expert analyses, cross-validates conflicts, and produces the root-cause report containing location and fault type/category.
6. **Human Agent:** a pass-through interface that returns engineer edits or adjudication decisions; it is not an LLM role.

The roles are configured with an OCRS prompt structure—Objective, Context, Response, and Skills—and use AutoGen GroupChat so messages and intermediate outputs are visible in a shared conversation thread (Source: Sec. 4.1–4.2, Fig. 5).

## 9. Architecture / Workflow

The actual workflow can be summarized as:

```text
Alert / incident input
→ Observation Agent queries metrics, logs, traces, and produces data ticket
→ Human verifies data-ticket completeness and relevance
→ Architecture Agent supplies service dependencies and current infrastructure context
→ Manager selects relevant Expert roles and coordinates discussion
→ Expert retrieves historical cases/knowledge when useful
→ Expert forms a domain hypothesis and checks whether evidence is sufficient
→ Request more observations or another domain when evidence is incomplete
→ Operation Agent compares analyses and writes location/category/root-cause report
→ Human engineers adjudicate the candidate root cause
→ Final RCA report / explanation
```

The paper's illustrative case shows the Manager/Operation role asking Architecture, Observation, Network Expert, and Resource Expert to contribute; additional evidence and domain reasoning narrow the conclusion (Source: Sec. 4.3, Fig. 7).

This is a genuine multi-step information-gathering and decision workflow, but its actions are primarily queries, role selection, hypothesis generation, and human requests for more evidence. It does not change the cloud environment and then verify recovery. Therefore it has a bounded investigation loop, not a demonstrated autonomous remediation loop.

## 10. Detection Method

ChatRCA assumes an incident or anomalous input is already available. The Observation Agent responds to alerts or expert inquiries and selects relevant evidence for a fixed incident period; detection thresholds and anomaly scoring are outside the proposed method (Source: Sec. 4.2).

## 11. RCA / Localization Method

ChatRCA separates evidence collection, architecture context, domain analysis, and final operation-level synthesis. The candidate output is evaluated at two different levels:

- **Service/component localization:** the actual faulty service/component should occur in the top-ranked candidates.
- **Root-cause category prediction:** the expert-confirmed category should occur in the top-ranked categories.

The Architecture Agent's service dependencies and node/container information function as context and structural prior. The paper does not describe a formal graph algorithm that computes a causal ranking over all nodes. Expert agents instead generate and compare hypotheses, while the Operation Agent checks whether the analyses and evidence support a final report.

The candidate space is dataset-specific:

- D1 has four reported fault types, including return failure, network delay, exception, and CPU contention.
- D2 has six expert-confirmed categories: web-cluster CPU, app-cluster CPU, chaos-mesh-induced memory, abnormal online-web service-node status, online-web CPU, and frequent FullGC.
- D3 has three categories: login failure, memory anomalies, and file-moving program.

This is a closed, labeled evaluation space. It does not establish open-set root-cause discovery, multiple-root handling, or ranking over physical network devices/interfaces/links (Source: Sec. 5.2, Sec. 5.4).

## 12. Diagnosis / Classification Method

The Operation Agent produces a structured root-cause identification report containing the incident, participating roles, analyses, root cause, and postmortem summary. The final outputs include:

- service/component location;
- root-cause category/fault type; and
- free-form diagnostic explanation with supporting evidence.

The human evaluation usefully shows these outputs are not interchangeable: on the 60 CMCC incidents, 52 category predictions were correct, but only 50 reasoning processes were fully consistent and 48 had fully consistent supporting evidence (Source: Sec. 5.7.1, Table 8). A correct category can therefore coexist with incomplete reasoning or incomplete evidence.

## 13. LLM / Agent Role

### Paper terminology

The paper explicitly presents ChatRCA as an LLM-based multi-agent RCA framework and implements it with AutoGen GroupChat (Source: Abstract, Sec. 4.1, Sec. 5.1).

### Capability analysis

- LLM Used: **Yes.** All roles except the Human Agent are LLM-driven with role-specific prompts; GPT-3.5 Turbo and GPT-4o are evaluated (Source: Sec. 4.1, Sec. 5.1).
- Tool Use: **Yes.** Observation queries observability data; Architecture retrieves dependency/node/container information; Expert roles invoke RAG when needed. The paper also uses Chroma/OpenAI embeddings in a retrieval baseline, which should not be confused with ChatRCA's role workflow.
- Multi-step interaction: **Yes.** Agents exchange messages, retrieve evidence, generate hypotheses, request more data, and iteratively refine the analysis.
- Planning: **Prompt-driven orchestration / implicit planning.** The Manager dynamically selects the next speaking role and the Expert follows a hypothesis-and-verification procedure. There is no separately evaluated Planner that emits a formal plan, and no explicit planner–executor interface.
- Memory: **Knowledge retrieval plus shared context, not a complete Agent memory architecture.** Expert agents retrieve from a database of 147 real-world incident cases and postmortems when they decide it is useful; AutoGen shares the conversation thread. The paper does not specify episodic write-back, forgetting, cross-session memory policy, or automatic update of the case database.
- Feedback loop: **Yes, bounded investigation feedback.** Retrieved observations, human data-ticket edits, and root-cause adjudication can trigger further evidence collection or alter the conclusion. There is no environment-state recovery feedback because remediation is outside the method.
- Environment interaction: **Read-oriented.** The workflow queries observability and architecture sources; it does not execute a state-changing repair action.
- Autonomous next-action selection: **Limited / yes within role orchestration.** AutoGen's auto-speaking mode selects the next role, and experts can decide whether to retrieve knowledge or continue hypothesis analysis. The action space is constrained to predefined roles/tools and human checkpoints.
- Agent classification: **Agent / multi-agent Agentic RCA workflow.** Unlike a one-shot LLM or retrieval-only pipeline, ChatRCA has specialized role agents, shared state, iterative evidence collection, role selection, and human-mediated decisions. Its Agent autonomy is bounded and investigation-oriented; the paper does not establish fully autonomous production operation or remediation.

The “multi-agent” claim is supported more strongly than a mere multi-role prompt because the implementation gives roles distinct prompts/capabilities and allows repeated communication through a GroupChat. Nevertheless, the ablation does not prove that independent model instances or unrestricted agent negotiation are necessary; it measures the value of role settings and human feedback under this implementation (Source: Sec. 4.1–4.2, Sec. 5.6).

## 14. Ground Truth

- D1 contains known fault instances in the TrainTicket microservice benchmark.
- D2 uses expert-confirmed root-cause descriptions and labels after filtering incomplete or overly simple cases.
- D3 supplies service/component and root-cause category labels from GAIA.
- Human engineers independently review the 60 D2 outputs for category correctness, reasoning-process consistency, and supporting-evidence consistency.
- The root-cause adjudication checkpoint hides the ground-truth answer from the reviewing engineers; they judge the evidence and competing hypotheses rather than simply copying the label (Source: Sec. 5.2, Sec. 5.7.1, Sec. 5.8.2).

The paper does not provide independent physical-causality ground truth for every explanation, a universal open-set candidate space, or a repair-success label. Category and localization labels are stronger evidence for those particular tasks than BLEU/BERTScore are for causal validity.

## 15. Baselines

### Service/component localization

- **MicroRCA:** metric anomalies plus service dependencies, followed by PageRank over an anomaly subgraph.
- **PDiagnose:** heterogeneous metrics, traces, and logs converted to time-series representations and voted to identify suspicious components.

### Root-cause category prediction

- **FastText:** text classification over incident descriptions, log summaries, and anomaly summaries.
- **XGBoost:** classification over manually constructed metric, log, and incident features.

### LLM / retrieval baselines

- **GPT-3.5 Turbo / GPT-4o Prompted:** direct prompting with the available incident evidence.
- **GPT-4oEmbed:** retrieves similar historical cases from a Chroma vector store using OpenAI embeddings, then asks GPT-4o to generate the result.

The baselines distinguish structured role-based RCA from direct prompting and historical-case retrieval, but they do not perfectly isolate the contributions of multi-agent messaging, role specialization, human feedback, and the underlying backbone model (Source: Sec. 5.3).

## 16. Metrics

- **Service/component Top-1 and Top-3 accuracy:** whether the expert-confirmed faulty service/component is ranked first or appears in the top three.
- **Root-cause-category Top-1 and Top-3 accuracy:** whether the expert-confirmed category is ranked first or appears in the top three. D3 reports only Top-1 because it has three total categories.
- **BLEU-4:** lexical n-gram overlap between the generated CMCC explanation and the expert-written RCA report.
- **BERTScore:** contextual semantic similarity between generated and reference RCA text.
- **Instance-level human evaluation:** category correctness; reasoning-process consistency; and supporting-evidence consistency, each with appropriate positive/partial/negative labels.
- **Similarity rating:** 15 operations engineers rate consistency with the expert root cause on a five-level scale.
- **Interaction satisfaction:** the same users rate the human-in-the-loop experience on a five-level satisfaction scale.
- **HITL disagreement frequency:** fraction of cases requiring third-engineer arbitration after two engineers fail to reach consensus. This is an ambiguity/intervention measure, not an accuracy metric (Source: Sec. 5.4, Sec. 5.7–5.8).

## 17. Main Results

- With GPT-4o, ChatRCA's service/component localization reaches D1 **73.33% / 77.78%**, D2 **76.67% / 83.33%**, and D3 **68.29% / 75.61%** for Top-1 / Top-3 (Source: Table 4, Sec. 5.5.1).
- With GPT-4o, root-cause-category prediction reaches D1 **91.11% / 95.56%**, D2 **86.67% / 88.33%**, and D3 **87.80% Top-1** (Source: Table 5, Sec. 5.5.2).
- On D2, generated explanations obtain **BLEU-4 63.45** and **BERTScore 86.92**. These measure similarity to expert reports, not independent physical-causality correctness (Source: Table 5, Sec. 5.5.2).
- Role ablations show cumulative gains. For service/component localization, the full workflow improves over Operation-only from D1 **44.44% / 64.44%** to **73.33% / 77.78%**, and over the corresponding D2 **43.33% / 61.67%** to **76.67% / 83.33%**. Observation, domain experts, and human feedback each add to the reported result (Source: Table 6, Sec. 5.6).
- For category prediction, the full workflow reaches D1 **91.11% / 95.56%**, D2 **86.67% / 88.33%**, and D3 **87.80% Top-1**, while the Operation-only setting is lower at D1 **44.44% / 73.33%**, D2 **43.33% / 76.67%**, and D3 **75.61% Top-1** (Source: Table 7, Sec. 5.6).
- In instance-level D2 human evaluation, 52/60 categories are correct (**86.67%**), 50/60 reasoning processes are fully consistent (**83.33%**), and 48/60 supporting-evidence sets are fully consistent (**80.00%**); partial consistency occurs for 6 reasoning and 8 evidence cases (Source: Table 8, Sec. 5.7.1).
- In the separate user study, 80% of ratings are at the two highest root-cause-consistency levels and 87% are at the two highest interaction-satisfaction levels (Source: Fig. 10, Sec. 5.7.2).
- Across 146 cases, 125 (**85.62%**) are resolved by two-engineer consensus and 21 (**14.38%**) require third-engineer arbitration. D2 has the highest arbitration rate at 16.67%, consistent with its more complex enterprise incidents (Source: Table 10, Sec. 5.8.3).

The results support the value of structured roles and targeted human intervention for the evaluated localization/category/explanation tasks. They do not show that ChatRCA executes safer repairs, reduces end-to-end incident resolution time, or generalizes to open-world network faults.

## 18. Scalability / Deployment

The evaluated D2 system is nontrivial in size—43 master nodes, 140 services, 311 pods, and 382 containers—but the paper does not report a large-scale online throughput, cost, latency, or permission study for the multi-agent workflow. The role design can be configured for different cloud domains, yet the number and expertise of agents are manually tailored to the system setting (Source: Sec. 5.2, Sec. 6).

The paper reports practical deployment feedback from a cloud operations department and uses enterprise incidents. It does not claim that ChatRCA autonomously changes system state, executes rollback, or verifies recovery. Human intervention is part of the design, not an incidental fallback.

## 19. Strengths

- Grounds role decomposition in an empirical study of real RCA collaboration rather than only inventing agent roles.
- Separates data-ticket verification from final root-cause adjudication, placing human oversight at high-impact checkpoints.
- Uses distinct observation, architecture, domain-expert, and operation responsibilities to reduce the burden on one LLM prompt.
- Evaluates localization, category diagnosis, explanation similarity, process consistency, evidence consistency, and user experience separately.
- Includes both public benchmark settings and a private enterprise-cloud setting, with a clear caution about dataset differences.
- Shows that a correct category does not necessarily imply complete reasoning or complete evidence, which is important for RCA reliability.

## 20. Limitations

### Paper-supported limitations / qualifications

- Human-in-the-loop intervention time and operational cost are not quantitatively measured; the proposed consensus/arbitration process may be difficult to scale (Source: Sec. 6).
- Performance may vary across unseen cloud systems, incident distributions, and LLM backbones; role configuration is domain-dependent (Source: Sec. 6).
- Public benchmark incidents may have exposure risk in general-purpose LLM pretraining, although the private CMCC dataset reduces this concern (Source: Sec. 6).
- Top-N accuracy evaluates candidate inclusion but not reasoning quality; BLEU-4/BERTScore evaluate text similarity but cannot establish technical correctness, logical sufficiency, or actionability. Human evaluation only partially closes this gap (Source: Sec. 6).
- The paper does not evaluate autonomous remediation, rollback, safety constraints, recovery verification, token/API cost, or detailed latency under production load.

### Further questions from this reading

- Role ablations conflate added agents, added context, and added human intervention; a controlled compute/cost-matched single-agent comparison is still needed.
- A RAG case database and a shared GroupChat provide evidence access, but the paper does not specify a durable memory update, conflict-resolution, or stale-case retirement policy.
- Human adjudication can resolve ambiguity, but the workflow still needs an explicit abstention/out-of-coverage signal for incidents with no reliable hypothesis.

## 21. Reproducibility

- Code available: **Claimed by the paper; current repository state should be verified.** The paper gives [leocache/ChatRCA](https://github.com/leocache/ChatRCA) and says implementation code and empirical-study data are available / will be open-sourced.
- Dataset available: **Partly.** D1 and D3 are public; D2 and its expert-confirmed reports are private.
- Benchmark available: **Partly.** The evaluation settings, baselines, and metrics are specified, but exact enterprise reproduction is impossible without D2.
- Prompt available: **Unclear / partly described.** OCRS role structure and capabilities are documented, but complete prompt/version/configuration release is not confirmed here.
- Model/API specified: **Yes at backbone level.** GPT-3.5 Turbo and GPT-4o are named; the exact model versions and all API settings are not fully established in this note.
- Hyperparameters: **Partly.** Dataset splits, role settings, baselines, and evaluation metrics are described; complete AutoGen and retrieval configurations require repository verification.
- Enough detail to reproduce: **Medium for the public benchmark, Low to Medium overall.** D2 privacy, deployment context, prompts, and human procedures limit exact reproduction.

## 22. Relationship to Existing AIOps Knowledge

ChatRCA extends the current AIOps pipeline with a role-specialized evidence and adjudication layer:

```text
Incident / Alert
→ Observation ticket
→ Human data verification
→ Architecture / dependency context
→ Domain hypotheses and historical-case retrieval
→ Cross-role synthesis
→ Human root-cause adjudication
→ RCA report
```

The relationship to existing notes is:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md): ChatRCA explicitly separates localization, category diagnosis, explanation, and evidence consistency.
- [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md): metrics, logs, traces, architecture, and incident text are collected through role-specific interfaces; this is procedural multimodal integration, not feature-level fusion.
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md): service dependencies and dynamic pod/container information provide context, but the paper does not establish a physical or causal topology graph.
- [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md): historical incidents and postmortems are retrieved as domain evidence. The RAG knowledge base is not automatically Agent memory.
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md): D2 gives private real incidents and deployment feedback, while the public benchmark and human-in-the-loop process provide different evidence axes.
- [Agent](../../../concepts/agent.md): this is a stronger Agentic workflow example than a one-shot LLM because it includes role interaction, tools, observations, and bounded next-role decisions; it remains human-gated and read-oriented.
- [Tool Use](../../../concepts/tool-use.md): observation/architecture queries and RAG retrieval should be separated from state-changing remediation tools.
- [Memory](../../../concepts/memory.md): shared GroupChat context and retrieved historical cases are context/knowledge mechanisms; no complete episodic or persistent Agent memory policy is defined.
- [Planning](../../../concepts/planning.md): the Manager coordinates role order and Experts follow a hypothesis loop, but no explicit formal Planner or planner–executor plan is evaluated.

## 23. Relevance to My Research

### Similarities

- Directly studies cloud/infrastructure RCA using metrics, logs, traces, incident descriptions, architecture/dependency information, and operational experts.
- Includes network expertise as one domain and evaluates a private enterprise-cloud setting with substantial service/node/container scale.
- Treats evidence completeness, cross-domain collaboration, uncertainty, and human verification as part of RCA rather than only measuring a final label.

### Differences

- The main topology is service/deployment architecture; it is not a physical network topology over routers, interfaces, links, optical modules, or NetFlow paths.
- D2 has no traces, and traffic/NetFlow/packet evidence is not a dedicated input. The evidence window and entity alignment are not specified at the level needed for network telemetry.
- The root-cause candidate space is closed and category-driven in the evaluation; it does not test open-set or multi-root network incidents.
- The output is diagnosis/reporting with human adjudication, not autonomous network remediation or recovery verification.

### Potentially Useful Ideas

- Treat evidence collection as an explicit work order/data ticket and verify completeness before high-level reasoning.
- Use separate agents or modules for network observation, topology context, resource signals, and operational synthesis, while keeping their evidence provenance visible.
- Let domain specialists form hypotheses and request additional evidence rather than forcing one model to consume every telemetry source at once.
- Place human review at data completeness and high-impact root-cause decision checkpoints; use consensus/arbitration selectively for ambiguous cases.
- Evaluate category correctness, candidate localization, reasoning completeness, evidence correctness, and operator effort separately.

### Assumptions That May Not Transfer

- Service dependency graphs and cloud pod/container relationships do not automatically represent physical network causality or propagation through links/interfaces.
- A small predefined fault-category space can make category accuracy look strong; network incidents may be open-set, multi-root, or hierarchical.
- Historical RAG cases may be stale after topology, configuration, firmware, or traffic changes, and the paper does not define case freshness/retirement.
- Human consensus among three operations engineers is useful for high-risk RCA but may be too expensive for high-volume alerts unless triggered by confidence/impact.

### Experiments Worth Considering

- Replace cloud architecture context with versioned network topology, device/interface/link mappings, and temporal traffic/NetFlow/syslog evidence.
- Compare a role-specialized network RCA workflow with a single LLM and deterministic RCA baselines under matched tool calls, context, and cost.
- Measure data-ticket completeness, evidence correctness, candidate localization, fault classification, explanation sufficiency, human time, and abstention on unknown faults separately.
- Test whether human verification at evidence collection and root-cause adjudication reduces unsafe conclusions more efficiently than post-hoc review.
- Evaluate open-set, multi-root, delayed-propagation, and conflicting-telemetry incidents rather than only closed categories.

**Transferability to Network AIOps:** **Medium.** The role decomposition, evidence work order, topology-context interface, hypothesis/verification loop, and human checkpoints are transferable. The cloud service dependency assumptions, closed fault categories, missing traffic/NetFlow and physical topology, and lack of autonomous recovery limit direct transfer.

## 24. My Understanding

ChatRCA is a genuine multi-agent investigation workflow because different LLM-driven roles have distinct objectives, context, response formats, and skills; they communicate through a shared thread, query evidence, and can trigger further analysis. Its core innovation is not simply “use several prompts,” but aligning role boundaries and human checkpoints with an observed enterprise RCA process.

At the same time, the paper’s autonomy is narrower than its title might suggest. The system gathers and organizes evidence, chooses the next diagnostic role, forms and checks hypotheses, and asks humans to verify data and adjudicate root causes. It does not execute a repair, observe recovery, or learn a durable policy from the incident. The RAG case store is external operational knowledge, while the GroupChat is shared working context; neither should automatically be described as a complete Agent memory architecture.

## 25. Questions

- What is the minimum evidence needed to call a role-specialized AIOps workflow genuinely multi-agent rather than a multi-role prompt around one model?
- How should network topology, syslog, metrics, traces, traffic, and NetFlow be converted into a verifiable data ticket with aligned timestamps and entities?
- How can a ChatRCA-like workflow signal open-set or multi-root incidents instead of forcing a closed category prediction?
- How should historical RCA cases be updated, versioned, invalidated, or forgotten when network topology and configuration change?
- What confidence, impact, or ambiguity policy should trigger human consensus/arbitration in high-volume network operations?
- Does the benefit of expert roles remain after matching single-agent context, tool calls, token cost, and human review effort?

## 26. Source Grounding

Key claims in this note are grounded as follows:

- Motivation, incident lifecycle, and motivating case: Sec. 1–2, Fig. 2.
- Empirical study participants, RCA process, roles, and human-feedback boundaries: Sec. 3, Fig. 3–4, Tables 1–2.
- ChatRCA roles, OCRS prompts, RAG skill, checkpoints, and AutoGen workflow: Sec. 4.1–4.3, Fig. 5–7, Table 3.
- Implementation, datasets, baselines, and system scales: Sec. 5.1–5.3.
- Metrics and main comparisons: Sec. 5.4–5.5, Tables 4–5, Fig. 9.
- Role ablations and human evaluation: Sec. 5.6–5.8, Tables 6–10, Fig. 10.
- Threats to validity, deployment qualification, code/data statement, and limitations: Sec. 6, Sec. 9.

The note distinguishes paper-backed accuracy/consistency results from the cross-paper interpretation of Agent boundaries, memory, planning, and network transfer. Text similarity and category accuracy are not treated as proof of physical causality or safe remediation.

## 27. Tags

`#AIOps` `#RCA` `#FaultLocalization` `#FaultDiagnosis` `#MultimodalTelemetry` `#MultiAgent` `#HumanInTheLoop` `#RAG` `#TopologyContext` `#NetworkAIOps`

## Code / Implementation

- Repository: [leocache/ChatRCA](https://github.com/leocache/ChatRCA)
- Official status: Author-Endorsed Implementation
- Read at commit: `448c2714047a1cf05371937b811dfe75ca8394d6`
- Code notes: [ChatRCA source-code notes](../../../code/aiops/chatrca/notes.md)
- Implementation coverage: AutoGen role agents, registered telemetry functions, structured evidence/final-diagnosis schemas, and group-chat setup.
