# TSGen: Automated Troubleshooting Guide Generation

## 1. Metadata

- Title: TSGen: Automated Troubleshooting Guide Generation
- Authors: Yi Xiao, Hongyu Zhang, Daniel Genkin, Chaoyun Zhang, Rujia Wang, Chetan Bansal, Bhala Ranganathan, Saravan Rajmohan, and Minghua Ma
- Year: 2026
- Venue: FSE Companion '26
- URL / DOI: https://doi.org/10.1145/3803437.3805239
- Local File: [Source PDF](../../../sources/papers/AIOps_papers/FSE26-TSGen-%20Automated%20Troubleshooting%20Guide%20Generation.pdf)
- Paper ID: tsgen

## 2. One-Sentence Summary

TSGen turns historical incident reports and discussions into filtered, distilled, and structured troubleshooting guides (TSGs), representing their diagnostic paths as decision-tree/DAG knowledge and updating them as new incidents arrive; it is an offline operational-knowledge generation pipeline rather than a runtime RCA or remediation Agent (Source: Abstract; Sec. 1, Sec. 4, Sec. 7.3).

## 3. Problem Setting

Site Reliability Engineers and on-call engineers use TSGs to encode symptoms, diagnostic checks, expected outcomes, root-cause clues, mitigations, and follow-up actions. In the studied Microsoft setting, guides are often missing, unstructured, stale, or difficult to execute. Historical incident-management records contain useful operational knowledge, but it is distributed across metadata, summaries, and chronological engineer discussions mixed with acknowledgements, automated enrichment, and other noise (Source: Sec. 1–3).

TSGen addresses the problem of **creating and maintaining structured troubleshooting knowledge from historical incidents**. It does not introduce a detector, define a universal root-cause candidate space, or execute a live repair. Its output is a human-reviewable TSG/DAG that can later support incident investigation and, as a proposed extension, Agent Skills (Source: Sec. 1, Sec. 4, Sec. 7.3).

## 4. AIOps Task

- Detection: **No new detection method.** The pipeline filters incidents selected from an incident-management system and targets monitors or on-call teams; it does not detect anomalies online (Source: Sec. 3–4).
- RCA: **Indirect knowledge support.** Generated guides organize symptom, diagnostic, root-cause clue, and mitigation relations, but TSGen does not perform runtime root-cause ranking for a new incident (Source: Sec. 4.4–4.5).
- Localization: **Not a standardized localization task.** A guide branch may point to a service, condition, or responsible path, but the paper does not define a universal node/device candidate space or a root-node metric.
- Diagnosis: **Procedural / operational diagnosis support.** The generated workflow is intended to help engineers diagnose incidents and retrieve the appropriate guide; it is not evaluated as an autonomous diagnosis executor (Source: Sec. 5).
- Prediction: No.
- Remediation: **Knowledge representation only.** TSGs preserve mitigation steps and queries/scripts as guide content. The pipeline does not execute repairs; the paper discusses adapting generated TSGs to Agent Skills as future groundwork (Source: Sec. 4.5, Sec. 7.3).

## 5. Failure / Incident Setting

The source records are Microsoft incident-management records for cloud services. An incident contains structured metadata such as title, severity, state, timestamps, and owner, plus optional summaries and chronological human-authored discussion logs. These discussions include symptoms, diagnostic hypotheses, troubleshooting steps, root-cause clues, team transfers, mitigations, and final resolution, but also contain automatic enrichment and other irrelevant entries (Source: Sec. 2, Sec. 3.2–3.3, Fig. 2).

TSGen scopes generation by monitor or on-call team. It first identifies monitors with many important incidents lacking TSG coverage, then learns a guide from historical incidents within the selected scope. This is an operational-knowledge coverage problem, not an end-to-end incident detection benchmark (Source: Sec. 3.1, Sec. 4.1).

## 6. Data Modalities

- Metrics: **No direct input modality confirmed for the current pipeline.** Metrics may be mentioned in incident context, but TSGen currently processes incident records and discussions as text.
- Logs: **Yes, in the paper's incident-record sense.** Chronological discussion/comments and incident logs are classified; these are not necessarily raw machine telemetry logs.
- Traces: No distributed traces identified.
- Alarms: **Indirectly.** Monitor- and alert-associated incident metadata are used to select the scope, but alarm streams are not separately modeled.
- Topology: No explicit service-dependency, network, or physical topology graph.
- Traffic: No.
- NetFlow: No.
- Configuration: Not a primary modality; configuration/state details can appear in incident discussions but are not represented as a dedicated structured input.
- Tickets: **Yes.** Incident reports/tickets and their metadata are the primary records.
- Other: Human discussion, incident summaries, monitor/team metadata, TSGs, embeddings, and generated decision-tree/DAG artifacts.

**Single-modal / Multi-modal:** **Text-centric, multi-source rather than feature-level multimodal telemetry.** The current system combines structured incident metadata and unstructured operational text. The paper explicitly identifies metrics, traces, and images as future modalities rather than evaluated inputs (Source: Sec. 7.4).

## 7. Dataset and System Setting

- Public / Private: **Private.** The data come from Microsoft's incident-management system. No public dataset or code repository is explicitly established in the paper.
- Production / Synthetic: **Real historical operational data.** The generated artifacts are produced offline; no synthetic incident generator is the basis of the reported main experiment.
- Observation duration: The empirical study examines incidents from several months; the main experimental corpus uses the most recent year. Exact day-level observation duration is not stated (Source: Sec. 3.1, Sec. 5.1).
- Number of incidents: The empirical setting spans incidents from about 80 services and nearly 50,000 monitors; the main experiment uses more than 20,000 incidents across approximately 30 monitors (Source: Sec. 3.1, Sec. 5.1).
- Number of devices / services / nodes: About 80 services and nearly 50,000 monitors in the broader empirical study; the experiment is scoped to about 30 monitors. A physical device/node count is not given (Source: Sec. 3.1, Sec. 5.1).
- Topology: No explicit infrastructure topology. Monitor/team scope and incident discussion structure provide organizational/operational grouping, not a dependency graph.

The paper also reports deployment to a Microsoft service-runtime team. It generated 53 TSGs, of which 38 were accepted and published after engineering review. This is evidence of operational use and human acceptance, not evidence of autonomous runtime remediation (Source: Sec. 7.2).

## 8. Core Method

TSGen has three main stages, followed by iterative maintenance:

1. **Incident filtering and semantic labeling.** A rule-based filter removes low-severity, fully automated, or noise-heavy incidents. An LLM labels discussion entries as `symptom`, `rootcause`, `troubleshootingstep`, `mitigation`, `enrichment`, or `other irrelevant`.
2. **Core-incident distillation.** Incidents are clustered using SentenceTransformer embeddings and Ward hierarchical clustering. A medoid is selected from each cluster, with a default maximum of `K=12`, so the generation prompt receives diverse representative cases instead of the entire historical corpus.
3. **Information distillation and guide generation.** An LLM rewrites each sampled incident into a fixed three-section representation—Incident Title, Basic Information, and Workflow—and then generates a decision tree and a structured TSG. The extracted DAG records decisive actions/branch points and sequential, conditional, escalation, or mitigation edges.
4. **Iterative update.** New incidents pass through the same filtering and distillation stages. The LLM checks whether a pattern is already represented, groups genuinely new patterns by proposed DAG changes, selects a representative incident, and updates one path at a time. A validator limits each update cycle to one path being added or altered to preserve structural integrity and reduce hallucinated structural drift (Source: Sec. 4.1–4.5).

## 9. Architecture / Workflow

The end-to-end pipeline is:

```text
Monitor / Team Scope
→ Retrieve historical incidents with metadata filters
→ Rule-based quality and severity filtering
→ LLM semantic labels for discussion entries
→ Cluster incidents and select medoids
→ Distill actionable chronological workflows
→ Generate decision tree + structured TSG/DAG
→ Human / engineering review and publication
→ New incidents
→ Re-filter and compare with existing patterns
→ Add or modify at most one DAG path per update cycle
→ Updated operational guide
```

The pipeline contains staged LLM transformations and a feedback-like knowledge-update loop, but it does not contain a runtime `Observation → autonomous next action → new Observation` control loop. Its “memory” is the persistent incident/TSG knowledge and caches used by the generation pipeline, not a per-attempt Agent memory that drives online action selection (Source: Sec. 4, Sec. 7.2–7.4).

## 10. Detection Method

TSGen does not detect incidents or learn an anomaly score. The empirical study first filters machine-raised incidents and targets monitors with high incident volume and missing TSG coverage. The selected monitor/incident stream is an input to knowledge generation, not an output of TSGen (Source: Sec. 3.1, Sec. 4.1).

## 11. RCA / Localization Method

TSGen organizes evidence into guide branches. Each branch is anchored to a symptom or pattern and can contain troubleshooting actions, root-cause clues, escalation, and mitigation steps. This improves the retrievability and procedural coverage of operational knowledge, but it is not a causal graph over services, devices, metrics, or faults.

The candidate space is therefore the set of patterns and workflow branches present in the filtered historical incidents. The paper does not report:

- a fixed set of all possible root services/devices/components;
- a root-node or root-set ranking procedure for a new incident;
- a candidate-pruning evaluation in the conventional RCA sense; or
- a universal physical-causality claim.

The practical “candidate reduction” happens earlier by scope selection, rule-based filtering, semantic log labeling, clustering, and medoid selection. It reduces the generation context; it is not equivalent to ranking root-cause candidates at runtime (Source: Sec. 3–5).

## 12. Diagnosis / Classification Method

The LLM classifies discussion entries into operational categories and rewrites incidents into structured workflows. The output classifies **knowledge units and guide content**, not incident root causes under a benchmark fault taxonomy.

The generated TSG can express relations such as:

```text
symptom / pattern
→ diagnostic check
→ evidence or condition
→ root-cause clue / escalation
→ mitigation or follow-up
```

The paper evaluates coverage of incident discussions and guide retrieval, plus human judgments of generated-guide quality. It does not establish that a generated branch is physically causal or that a text diagnosis is correct for every future incident (Source: Sec. 5.2–5.4, Sec. 6).

## 13. LLM / Agent Role

### Paper terminology

TSGen describes the generated TSGs as possible groundwork for adapting troubleshooting knowledge to `AgentSkills`. This is a downstream proposal; the evaluated TSGen pipeline itself is not presented as a complete autonomous Agent (Source: Sec. 7.3).

### Capability analysis

- LLM Used: **Yes.** LLMs label discussion entries, distill incident workflows, generate the decision tree/TSG, compare new incidents with existing patterns, and propose incremental updates (Source: Sec. 4).
- Tool Use: **Limited / pipeline-side.** The system retrieves incident records, computes text embeddings and clusters incidents, and uses a vector database for retrieval evaluation. These are data-processing and retrieval operations, not an online Agent freely selecting operational tools.
- Multi-step interaction: **Pipeline stages and iterative updates: Yes.** Runtime environment interaction for troubleshooting: **No.** The steps are executed over stored historical records and guide artifacts.
- Planning: **Explicit artifact generation, not runtime planning.** The decision tree/DAG organizes future troubleshooting paths, but the paper does not define an online Planner that selects arbitrary actions or replans after live observations.
- Memory: **Persistent operational knowledge and caches, not Agent memory.** Historical incidents and generated TSGs are retained for later guide generation/retrieval; the clustering label caches improve engineering efficiency. The paper does not specify episodic memory selection, cross-attempt Agent memory, forgetting, or a memory-read policy for live diagnosis.
- Feedback loop: **Knowledge-update loop, yes.** New incidents and engineering acceptance update the TSG. This is different from an action-observation feedback loop in which an Agent changes its next tool/action during the same incident.
- Environment interaction: **No direct live environment action.** The pipeline consumes incident-management records and is deployed to assist a service-runtime team; it does not query live telemetry or execute remediation in the reported method.
- Autonomous next-action selection: **No for TSGen.** The generated guide may later be used by an Agent Skill, but that downstream system is not evaluated here.
- Agent classification: **LLM-assisted operational-knowledge curation / document-generation pipeline; not a demonstrated Agent.** If the paper’s proposed Agent Skills extension is discussed, it should be labeled as a future integration rather than a measured capability.

This boundary is important when comparing TSGen with StepFly: TSGen **generates and maintains** guide knowledge, whereas StepFly **executes** a preprocessed guide through a bounded Scheduler–Executor workflow. TSGen’s ReAct baseline is an Agent baseline; it is not evidence that TSGen itself is a ReAct Agent (Source: Sec. 5.2, Sec. 7.3).

## 14. Ground Truth

The source of supervision and evaluation is primarily historical operational evidence and human review:

- Incident discussion entries receive semantic labels used by the pipeline; the paper describes the labels and filtering process, but the full independent annotation protocol is not completely specified.
- Existing human-crafted TSGs provide a reference for comparison and retrieval evaluation.
- Chronological train/validation/test splits are used within monitors: 60% training, 20% validation, and the most recent 20% test (Source: Sec. 5.1).
- OCE/SRE human evaluators assess factual accuracy, completeness, logical coherence, and clarity.
- Engineering acceptance/publication provides an operational usefulness signal.

The paper does not define a universal root-node label, root-cause set, fault type taxonomy, or independent causal ground truth. `MatchingRate` and guide retrieval measure agreement with incident discussions/guide content, not necessarily physical root-cause correctness (Source: Sec. 5.2–5.4, Sec. 6).

## 15. Baselines

- **GPT-4o direct summarization:** direct summarization without TSGen’s filtering, distillation, or structured generation process.
- **ReAct agent:** an Agent that autonomously queries the incident database, identifies patterns, and constructs a guide step by step. This is a baseline for comparison, not TSGen’s architecture (Source: Sec. 5.2).
- **Rule-based clustering / keyword-template method:** a non-LLM structured baseline.
- **Human-crafted TSG:** a reference/pseudo-baseline representing existing manually authored guides.

The comparison is mainly about guide coverage, order, retrieval usefulness, and human quality—not about online RCA success or remediation safety.

## 16. Metrics

- **MatchingRate / Coverage:** aligns generated TSG steps with incident discussions; full matches count as 1 and partial matches as 0.5, then the weighted coverage is normalized by the number of guide steps. It measures how much incident-discussion content is represented, not root-cause accuracy.
- **OrderConsistency:** measures whether the relative order of matched steps agrees with the incident discussion order.
- **RetrievalAccuracy, Hit@3, and MRR:** evaluate whether a generated guide is retrieved for a query built from the incident title and early or complete discussions. These measure guide retrieval, not diagnosis correctness.
- **Human evaluation:** OCE/SRE ratings from 1–5 for factual accuracy, completeness, logical coherence, and clarity (Source: Sec. 5.2–5.3).
- **AcceptanceRate:** fraction of generated TSGs accepted and published after engineering review; this is an operational adoption/usefulness signal, not autonomous remediation success.
- **Efficiency:** generation time and token consumption; the paper also reports the cost per generated TSG under the stated GPT-4o pricing (Source: Sec. 5.5, Sec. 7.2).

## 17. Main Results

- TSGen reports **54.8% incident coverage** and approximately **three-times higher retrieval accuracy than the comparison methods** in the abstract and main evaluation (Source: Abstract, Table 4).
- In Table 4, TSGen obtains coverage **0.548** and order consistency **0.941**. For the first-discussion retrieval query it reports accuracy **0.476**, Hit@3 **0.978**, and MRR **0.708**; for the all-discussions query the corresponding values are **0.482**, **0.981**, and **0.711** (Source: Table 4, Sec. 5.3).
- In the Table 5 ablation, removing filtering reduces coverage to **0.278** (a reported 49.3% decrease) and retrieval accuracy to **0.262**. Removing distillation has a smaller effect on coverage (**0.523**), while removing structured generation reduces retrieval accuracy to **0.031**. These ablations support the importance of noise filtering and structured guide generation for this task; they do not isolate an LLM’s causal value in a runtime RCA setting (Source: Table 5, Sec. 5.4).
- The paper reports that caching reduces generation time by approximately **11.5%** and token consumption by **95%**; the exact comparison direction should be read with the cache experiment context (Source: Sec. 5.5).
- Iterative updates increase coverage over the one-shot guide, reaching a reported **53.3%** at one of the later update points versus **42.3%** after one-shot generation; the paper reports no observed error accumulation or hallucination drift in its validation sequence (Source: Fig. 4, Sec. 5.6). This is a bounded experimental observation, not a general guarantee for long-term knowledge maintenance.
- In human evaluation, TSGen’s mean score is reported as **4.3**, compared with **3.3** for existing human-crafted TSGs; the paper describes more severe hallucination for the ReAct baseline but does not establish an exact ReAct mean here (Source: Fig. 5, Sec. 5.7).
- In deployment, **53 TSGs were generated and 38 accepted/published** after engineering review (Source: Sec. 7.2). The reported team statement of an approximately 80% success rate is operational feedback and should not be conflated with Table 4 coverage or retrieval accuracy.

## 18. Scalability / Deployment

The broader study covers roughly 80 services and nearly 50,000 monitors, while the main evaluation uses more than 20,000 incidents across about 30 monitors with chronological splits. The pipeline therefore demonstrates processing at a large organizational data scale, but the paper does not provide a physical network-node or topology scale (Source: Sec. 3.1, Sec. 5.1).

TSGen was deployed to a Microsoft service-runtime team to generate guides for engineering review and publication. This is **production data plus operational deployment of a knowledge-generation aid**. It is not production deployment of an autonomous RCA Agent or autonomous remediation system. The method does not directly execute queries or change system state in the reported deployment (Source: Sec. 7.2–7.3).

## 19. Strengths

- Uses historical operational evidence rather than asking an LLM to invent troubleshooting procedures from scratch.
- Separates noise filtering, semantic selection, diversity-oriented incident distillation, and structured guide generation.
- Makes the resulting knowledge more retrievable and more explicit about symptom, check, branch, root-cause clue, and mitigation relations.
- Supports incremental updates from new incidents and constrains each update to one path to reduce structural drift.
- Reports both automated coverage/retrieval metrics, human quality evaluation, and an engineering acceptance signal.
- Establishes a useful upstream/downstream boundary: generated TSGs can become input to a later executable workflow such as StepFly or a proposed Agent Skill.

## 20. Limitations

### Paper-supported limitations / qualifications

- The current modality is text-centric; metrics, traces, images, and other multimodal sources are identified as future extensions (Source: Sec. 7.4).
- The data come from one large provider and its incident-management conventions; external validity to other organizations and network environments is uncertain (Source: Sec. 8.1).
- LLM hallucination and incorrect guidance remain risks. DAG constraints and path-limited updates mitigate structural errors but do not prove factual or causal correctness (Source: Sec. 8.2).
- Automated metrics are proxies for guide coverage/retrieval, and LLM-based judgments may introduce their own bias; human evaluation helps but does not remove this issue (Source: Sec. 8.3).
- Medoid sampling can select stale incidents. The paper identifies temporal weighting and better handling of evolving knowledge as future directions (Source: Sec. 8.4).
- The paper does not evaluate live telemetry querying, online replanning, autonomous diagnosis, or actual repair execution.

### Further questions from this reading

- A generated guide may preserve historical procedure patterns while failing on an open-set fault or a changed topology; the current evaluation does not quantify out-of-coverage detection.
- “Coverage” and “retrieval accuracy” do not establish that the guide’s causal explanation is correct or safe to execute.
- The paper does not isolate how much improvement comes from filtering, clustering, structured generation, retrieval infrastructure, or the underlying LLM.
- A guide’s update loop is a knowledge-maintenance loop, not necessarily a memory policy; retention, conflict resolution, versioning, and retirement rules remain underspecified.

## 21. Reproducibility

- Code available: **Unclear / not explicitly established in the local paper.**
- Dataset available: **No for the main corpus.** The incident records are private Microsoft data.
- Benchmark available: **Partly described, but not independently reproducible from public data.** The evaluation protocol and metrics are specified, while the source corpus is private.
- Prompt available: **Unclear.** The stages and task-specific uses are described, but a complete prompt release is not confirmed.
- Model/API specified: **Partly.** GPT-4o is named for the direct-summarization baseline and the paper describes LLM-based stages; all model/configuration details are not confirmed here.
- Hyperparameters: **Partly.** The filtering, clustering, `K=12` medoid setting, and chronological splits are described; complete deployment configuration is not public.
- Enough detail to reproduce: **Low to Medium.** The conceptual pipeline and metrics are reproducible, but private incidents, proprietary operational schema, prompts, and guide-review data limit exact reproduction.

## 22. Relationship to Existing AIOps Knowledge

TSGen adds an upstream layer to the current AIOps mental model:

```text
Historical incidents / operator discussions
→ operational-knowledge filtering and distillation
→ structured TSG / decision tree / DAG
→ retrieval, guide execution, or later Agent Skill
→ diagnosis / mitigation support
```

This complements, rather than duplicates, the current notes:

- [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md): TSGen shows how incident records become structured and incrementally maintained operational knowledge; the generated guide is not automatically Agent memory.
- [StepFly](../stepfly/notes.md): TSGen generates and updates TSG knowledge; StepFly compiles a TSG into an executable DAG/QPP workflow. The two can form a knowledge-generation-to-execution path, but neither alone establishes general autonomous RCA.
- [AIM](../aim/notes.md): AIM generates mitigation plans for selected alerts and evaluates constrained execution; TSGen generates reusable troubleshooting knowledge from historical incidents. Plan generation and operational knowledge curation are distinct.
- [Comfey](../comfey/notes.md): Comfey retrieves historical incidents and TSGs for production team routing; TSGen addresses how a reusable TSG may be constructed when coverage is missing.
- [Context Engineering](../../../concepts/context-engineering.md): filtering, semantic labeling, clustering, and medoid selection are context/data selection mechanisms that control what the LLM sees.
- [Memory](../../../concepts/memory.md): historical incident storage, caches, and TSG publication are durable knowledge infrastructure, not proof of episodic or long-term Agent memory.
- [Planning](../../../concepts/planning.md): a generated decision tree/DAG is a plan-like operational artifact, but TSGen does not provide a runtime Planner–Executor or search-based planning architecture.
- [Agent](../../../concepts/agent.md): the proposed Agent Skills adaptation is downstream future work; the measured TSGen pipeline is more cautiously classified as an LLM-assisted workflow.

## 23. Relevance to My Research

### Similarities

- The paper addresses operational incident knowledge, diagnosis workflows, failure evidence, and mitigation procedures, all relevant to AIOps and RCA.
- It treats noisy historical records, missing procedural coverage, evidence selection, temporal evolution, and human acceptance as first-class concerns.
- The generated guide/DAG representation may provide a structured interface between telemetry-derived evidence and later diagnosis or Agent execution.

### Differences

- The input is primarily incident-management text and metadata, not synchronized metrics, syslog, traces, traffic/NetFlow, or device/interface/link telemetry.
- The scope is monitor/team-oriented cloud operations; it does not model physical network topology or a root-cause candidate space over network devices, links, interfaces, or optical modules.
- The output is reusable troubleshooting knowledge, not a runtime fault classifier, ranked root cause, or autonomous repair action.
- Evaluation emphasizes guide coverage, retrieval, human quality, and acceptance rather than Top-k RCA, fault classification, repair success, or network-scale latency.

### Potentially Useful Ideas

- Use severity, human-authorship, and semantic categories to remove noisy operational records before reasoning.
- Distill many incidents into diverse representatives rather than placing an unbounded historical corpus into an LLM context.
- Represent troubleshooting procedures as explicit symptom-to-check-to-resolution paths, with versioned updates and provenance.
- Use a one-path-per-update constraint or analogous validation to limit knowledge-graph/guide drift.
- Measure knowledge coverage, retrieval usefulness, human acceptance, freshness, and operational cost separately from RCA correctness.

### Assumptions That May Not Transfer

- Textual incident discussions may contain enough diagnostic detail in Microsoft cloud services; network faults may require high-rate time-series, syslog, traffic, physical topology, and temporal correlation that are absent here.
- Monitor/team scope and historical discussion similarity may not provide a safe candidate space for device/link-level RCA.
- A medoid incident may be stale after topology, firmware, configuration, or traffic-pattern changes.
- Human review and acceptance may be easier for a guide document than for a high-impact automated network remediation action.

### Experiments Worth Considering

- Build a network-specific incident-to-guide corpus with timestamps, topology/configuration versions, telemetry references, root-cause labels, and repair outcomes.
- Compare raw-incident prompting against severity/semantic filtering and diversity-aware incident distillation for downstream RCA or guide retrieval.
- Evaluate whether generated guide paths improve candidate generation or evidence selection without claiming that guide coverage equals RCA accuracy.
- Test temporal weighting, stale-guide detection, and one-path-at-a-time updates under topology and configuration changes.
- Compare a generated guide consumed by a deterministic workflow with a free-form LLM Agent, measuring diagnosis correctness, tool calls, latency, cost, human effort, and unsafe-action rate.

**Transferability to Network AIOps:** **Medium.** The data curation, evidence distillation, operational-knowledge representation, and human-acceptance ideas are transferable. The text-only cloud scope, lack of physical topology, and lack of online telemetry/RCA execution make direct transfer to network infrastructure diagnosis incomplete.

## 24. My Understanding

TSGen is best understood as a knowledge-engineering front end for AIOps. It mines historical incident conversations, removes noise, samples diverse cases, and turns them into a structured troubleshooting procedure that can be retrieved, reviewed, and updated. Its most important contribution for the current knowledge base is the distinction between **creating operational knowledge** and **executing an Agent loop**.

The paper uses LLMs in several sequential processing steps and reports a ReAct baseline, but TSGen itself does not choose live tools, observe a changing environment, or execute remediation. Its decision tree/DAG looks like a plan because it organizes future actions; however, it is a persistent guide artifact, not proof of an explicit runtime Planner. Likewise, stored incidents and caches are useful knowledge infrastructure, not automatically episodic memory.

## 25. Questions

- How should network incident records combine text, metrics, syslog, traces, traffic/NetFlow, and topology before guide generation?
- How can a generated TSG detect that a new incident is out of coverage rather than recommending a historically familiar but unsafe path?
- What provenance and validation are required before a generated guide can be compiled into executable network tools or remediation actions?
- How should guide freshness be measured when topology, configuration, firmware, or traffic behavior changes?
- Can generated TSGs improve physical root-cause candidate generation without hiding causal uncertainty behind fluent text?
- How should guide versioning, conflict resolution, forgetting, and retirement relate to [Agent memory](../../../concepts/memory.md)?

## 26. Source Grounding

Key claims in this note are grounded as follows:

- Problem, historical incident setting, and motivation: Sec. 1–3.
- Filtering, semantic labels, clustering, medoid selection, distillation, DAG generation, and iterative updates: Sec. 4.1–4.5.
- Baselines, chronological split, metrics, and evaluation protocol: Sec. 5.1–5.3.
- Main comparison and ablations: Table 4, Table 5, Sec. 5.3–5.5.
- Iterative coverage and human evaluation: Fig. 4, Fig. 5, Sec. 5.6–5.7.
- Deployment, acceptance, Agent Skills proposal, and future multimodal direction: Sec. 7.2–7.4.
- Threats and limitations: Sec. 8. The local 12-page PDF's final pages are references; no additional substantive appendix was used.

Facts about the paper are kept separate from the cross-paper synthesis and network-transfer interpretation above. `Coverage`, retrieval metrics, and acceptance are not treated as physical RCA correctness.

## 27. Tags

`#AIOps` `#OperationalKnowledge` `#TroubleshootingGuide` `#IncidentManagement` `#LLM` `#KnowledgeCuration` `#RCA` `#CloudOperations` `#AgentBoundary`
