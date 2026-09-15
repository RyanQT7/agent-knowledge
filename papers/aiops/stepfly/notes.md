# StepFly: Agentic Troubleshooting Guide Automation for Incident Diagnosis

## 1. Metadata

- Title: StepFly: Agentic Troubleshooting Guide Automation for Incident Diagnosis
- Authors: Jiayi Mao, Liqun Li, Yanjie Gao, Zegang Peng, Shilin He, Chaoyun Zhang, Si Qin, Samia Khalid, Qingwei Lin, Saravan Rajmohan, Sitaram Lanka, and Dongmei Zhang
- Year: 2026
- Venue: Proceedings of the ACM on Software Engineering, FSE, Article FSE136
- URL / DOI: https://doi.org/10.1145/3808143
- Local File: [Source PDF](../../../sources/papers/AIOps_papers/FSE26-StepFly-%20Agentic%20Troubleshooting%20Guide%20Automation%20for%20Incident%20Diagnosis.pdf)
- Paper ID: stepfly

## 2. One-Sentence Summary

StepFly turns semi-structured troubleshooting guides into quality-checked execution DAGs and query-preparation plugins, then uses a scheduler, step-limited executors, structured external memory, and operational plugins to execute diagnosis reliably and in parallel.

## 3. Problem Setting

Site Reliability Engineers (SREs) rely on Troubleshooting Guides (TSGs), which describe actions, expected outcomes, conditions, and next steps for incident diagnosis. In practice, TSGs are long, ambiguous, data-intensive, and often contain implicit dependencies or complex query templates. Manual execution is slow and error-prone; a generic LLM agent can skip steps, generate invalid queries, or lose control-flow state (Source: Sec. 1–2.2, Fig. 1).

StepFly addresses **TSG execution for incident diagnosis**, not the creation of a new anomaly detector or a general-purpose autonomous remediation system. It also studies TSG quality and preprocessing because the reliability of online execution depends on the guide and its executable representation.

## 4. AIOps Task

- Detection: **No new detector.** The agent is triggered by an incoming incident and a corresponding TSG.
- RCA: **Diagnosis support.** It follows operational procedures that can identify a likely cause or responsible upstream team.
- Localization: **Limited / procedure-dependent.** The TSG conclusion may identify a service or issue path, but StepFly does not define a universal candidate-root space.
- Diagnosis: **Yes, procedural diagnosis.** The final execution path and conclusion are compared with a human-labeled diagnostic conclusion.
- Prediction: No.
- Remediation: **Primarily support.** The studied operations are read-only queries and analysis; conclusions are sent to SREs, who review them before mitigation (Source: Sec. 7).

## 5. Failure / Incident Setting

The paper studies online-service incidents handled with TSGs, including service-availability degradation, latency issues, pipeline failures, and request-volume anomalies. A representative guide queries trending exceptions, checks known issues and code changes, retrieves exception stacks, examines dependent-service availability/correlation, and either recommends a rollback, transfers the ticket, or escalates to an SRE (Source: Sec. 2.2, Fig. 1).

The setting is operationally realistic and uses guides from multiple service teams, but the main controlled comparison is over a selected set of guides and incidents. It should not be confused with a closed-form physical network RCA benchmark.

## 6. Data Modalities

- Metrics: Yes; metric retrieval and service availability/latency checks are common.
- Logs: Yes; service log queries, exception types, and exception stacks are central.
- Traces: **No distributed traces identified.** The paper’s “execution history” and exception stack are not distributed request traces.
- Alarms: Incident triggers are present, but a separate alarm modality is not formally evaluated.
- Topology: **Indirect / dependency references.** TSGs can inspect upstream dependent services, but no general topology graph is modeled.
- Traffic: Unclear / not explicitly stated as an input modality.
- NetFlow: Unclear / not explicitly stated in the paper.
- Configuration: DevOps checks include ongoing deployments, pull requests, and code changes; a general configuration model is not defined.
- Tickets: Incident reports/IDs and incident-management-system outputs are used.
- Other: TSG documentation, KQL query templates, DevOps data, code interpreter results, and execution-DAG state.

**Single-modal / Multi-modal:** Multi-source operational evidence, centered on logs, metrics, DevOps/change data, and TSG instructions. The paper does not present feature-level multimodal telemetry fusion; it presents a workflow that queries and combines sources through plugins (Source: Sec. 3.2, Sec. 4.4.3).

## 7. Dataset and System Setting

- Public / Private: The source TSGs and production incidents originate from Microsoft; the paper states that code and synthesized incident data are publicly available at [microsoft/StepFly](https://github.com/microsoft/StepFly). The original operational corpus is not presented as fully public (Source: Sec. 1, Sec. 10).
- Production / Synthetic: Real-world TSGs and incidents are used; the released incident data are synthesized for reproducibility, and the controlled experiment is not a live intervention study.
- Observation duration: Not explicitly stated for the 80-incident evaluation. The TSG study covers guides applied frequently in recent months.
- Number of incidents: The main experiment uses 80 real incidents; the broader empirical study analyzes 92 TSGs from 9 teams; the preprocessing evaluation uses 15 TSGs and 86 query templates (Source: Sec. 3, Sec. 5.1–5.3).
- Number of devices / services / nodes: The paper does not provide a single infrastructure node count. The 92 TSGs cover high-traffic online services across 9 teams.
- Topology: No explicit graph-size or physical topology description. Dependency relationships are encoded in TSG control-flow and data-flow conditions.

## 8. Core Method

StepFly has three stages:

1. **TSG quality improvement:** TSG Mentor uses an LLM, guidelines, examples, and vector-nearest TSG examples to identify clarity, control-flow, data-flow, database-instruction, and presentation issues. Human authors retain readability and review responsibility.
2. **Offline preprocessing:** an LLM extracts a lightweight execution DAG from each TSG and extracts Query Preparation Plugins (QPPs) from query templates. The DAG captures step dependencies and conditional transitions; a QPP fills query parameters and returns a valid query to the database client.
3. **Online execution:** a Scheduler follows the DAG, allocates one or more step-specific Executors, passes data through a structured key-value memory, and invokes plugins. Independent nodes can run concurrently.

The design moves control-flow and query composition out of unconstrained per-step LLM generation. The LLM still reasons about an assigned step and interprets tool results, but the scheduler constrains which step is legal next (Source: Sec. 4, Fig. 5–8).

## 9. Architecture / Workflow

The end-to-end workflow is:

```text
Incident ID
→ Load relevant TSG + execution DAG + QPPs
→ Scheduler enables ready DAG node(s)
→ Executor receives incident, guide, current node/edges, plugins, and history
→ Executor reasons over the assigned instruction
→ Plugin / QPP retrieves logs, metrics, DevOps data, or runs analysis
→ Result is stored as structured memory and the Executor updates outgoing edges
→ Scheduler enables conditional successors or retries failed nodes
→ Reach End / no enabled nodes
→ Send diagnostic conclusion and structured execution log to SRE
```

For parallelizable guides:

```text
Scheduler
→ independent Executor 1
→ independent Executor 2
→ independent Executor 3
→ join / early termination / fallback according to DAG
```

This is a fixed, explicit execution workflow with observation-dependent branch transitions. It is not a free-form Planner that invents a new plan at every step, and the paper does not define a separate online replanning phase. The DAG is prepared offline; the scheduler reacts to completion/failure and conditional outcomes within that DAG (Source: Sec. 4.2, Sec. 4.4.1–4.5).

## 10. Detection Method

Incident detection is upstream. StepFly is activated by an incident ID and loads the corresponding TSG. It does not learn thresholds, anomaly scores, or an incident detector. In the example, monitoring may have already exposed an availability issue, after which the TSG performs diagnostic checks (Source: Sec. 2.1–2.2, Sec. 4).

## 11. RCA / Localization Method

StepFly does not search an unrestricted root-cause candidate space. The candidate branches and termination points are supplied by the TSG. A node represents a guide step, not a service/device root candidate; the final diagnosis is the conclusion reached by the executed guide path.

The execution DAG provides:

- control-flow constraints and conditional branches;
- prerequisite and data dependencies;
- termination and fallback paths;
- a basis for parallelizing independent checks.

The scheduler tracks `unknown`, `enabled`, and `disabled` states for nodes and edges. Successful node outcomes enable or disable outgoing edges; failed nodes are retried up to a configurable limit and then disable downstream execution (Source: Sec. 4.2, Sec. 4.4.1).

## 12. Diagnosis / Classification Method

The paper’s primary online output is a TSG execution conclusion, not a standardized fault taxonomy. In the experiment, an execution is successful only when both the executed path and the diagnostic conclusion align with a human ground-truth label (Source: Sec. 5.4).

The paper also evaluates preprocessing artifacts:

- DAG extraction at node, edge, and condition levels.
- QPP extraction by functional equivalence against manually annotated templates.

These are representations of executable procedure structure, not root-cause classification metrics.

## 13. LLM / Agent Role

### Paper terminology

The paper calls StepFly an LLM-powered agent framework and describes a scheduler-executor agent system (Source: Abstract, Sec. 4.4).

### Capability analysis

- LLM Used: **Yes.** LLMs are used for TSG Mentor, DAG/QPP preprocessing, and Executor reasoning; the experiments use GPT-4.1, GPT-4.1-mini, GPT-4o, and Grok-3 (Source: Sec. 4.1, Sec. 5.4).
- Tool Use: **Yes.** Log retrieval, DevOps, metric retrieval, code interpreter, and TSG-specific QPP plugins are executed.
- Multi-step interaction: **Yes.** Steps produce observations/results, update DAG state, and activate subsequent steps.
- Planning: **Explicit workflow representation.** The offline execution DAG and online Scheduler determine legal next steps. This is structured orchestration rather than an LLM freely generating a plan at runtime.
- Memory: **Yes, external structured working memory.** Plugins write arbitrary typed values under keys; other plugins or Executors retrieve them by reference. The implementation uses MongoDB, abstracted behind a memory interface (Source: Sec. 4.4.4).
- Feedback loop: **Within execution, yes.** Plugin results and step success/failure affect edge state, retries, and subsequent branches. Cross-incident learning/update is not the main mechanism.
- Environment interaction: **Yes, read-oriented.** The system queries logs/metrics/DevOps sources and runs code analysis; the studied implementation avoids destructive remediation actions.
- Autonomous next-action selection: **Bounded.** The Scheduler selects ready nodes according to the preprocessed DAG; an Executor reasons over its assigned step. It cannot invent arbitrary workflow edges.
- Agent classification: **Agentic workflow / scheduler–executor system.** Multiple executor processes exist, but the paper emphasizes homogeneous step executors under a shared scheduler, not independent negotiating Agents. It is stronger than a one-shot LLM because it observes tool results and advances a stateful execution graph, while its autonomy is bounded by TSG/DAG rules.

The difference from a ReAct baseline is important: ReAct relies on online reasoning to navigate the guide, whereas StepFly uses the guide’s explicit DAG to constrain execution and uses memory to pass large structured data without putting all payloads into the conversation (Source: Sec. 5.4–5.5).

## 14. Ground Truth

For DAG extraction, manually annotated DAGs are initially generated by an LLM and corrected by experienced SREs. Node/edge metrics compare extracted structure to this annotation; condition semantics are judged for alignment (Source: Sec. 5.3).

For QPP extraction, 86 query templates from 15 TSGs are manually annotated, and functional equivalence—not textual identity—is used as the criterion. For online execution, the 80 historical incidents have known human diagnostic conclusions, and success requires both path and conclusion agreement (Source: Sec. 5.1, Sec. 5.3–5.4).

The paper does not establish a universal physical root-cause label, multi-root ground truth, or independent causal verification protocol.

## 15. Baselines

- **ReAct:** a single-agent Thought–Action–Observation loop using online reasoning to navigate TSG steps.
- **TaskWeaver:** a Planner agent plus Code Interpreter agent for data-intensive tasks.
- **StepFly w/o QPP:** the same framework without extracted query-preparation plugins.
- **StepFly:** the complete DAG-guided scheduler/executor, memory, plugins, and QPP path.

The main comparison shares the system prompt and plugin set where possible; the key distinction is that StepFly and its ablation use explicit QPPs while ReAct and TaskWeaver generate queries online (Source: Sec. 5.4).

## 16. Metrics

- TSG Mentor recall, precision, and F1 for issue-category detection.
- DAG extraction precision, recall, F1, and accuracy at node, edge, and condition levels.
- QPP functional extraction success rate.
- Execution success rate: both path and diagnostic conclusion match the human label.
- Execution latency: time from TSG invocation to final termination.
- Total token consumption: aggregate input/output tokens.
- Parallel execution time reduction with different numbers of Executors.
- Operational prototype median incident-mitigation-time change.

These metrics separately evaluate documentation analysis, workflow representation, tool/query preparation, diagnosis-path correctness, cost, and speed. Execution success is not identical to root-cause correctness outside the TSG’s coverage.

## 17. Main Results

- In the 92-TSG quality study, the most common issue categories are Clarity and Precision (37.4%), Database Instruction (27.2%), Data Flow (20.4%), Control Flow (5.1%), and Presentation/Structure (9.9%) (Source: Sec. 3.3, Fig. 4).
- TSG Mentor achieves recall 0.78, precision 0.85, and F1 0.81 under leave-one-out evaluation (Source: Sec. 4.1).
- Across 15 TSGs, overall DAG extraction reaches 94.89% F1; node-level performance exceeds 99% for the reported metrics, edge-level F1 is 93.47%, and condition-level semantic accuracy is 91.78% (Source: Table 2, Sec. 5.3).
- QPP extraction succeeds in 251 of 258 attempts, or 97.3%; the reported failures are associated with escape-character mistakes (Source: Sec. 5.3).
- In Table 3, complete StepFly execution reaches 94.38% success with GPT-4.1, 84.38% with GPT-4.1-mini, 92.5% with GPT-4o, and 88.75% with Grok-3. ReAct and TaskWeaver are lower in each reported model setting (Source: Table 3, Sec. 5.4).
- Under GPT-4.1, StepFly’s median time consumption is reported as 88% of ReAct and 38% of TaskWeaver; median token consumption is 71% of ReAct and 61% of TaskWeaver (Source: Sec. 5.4, Fig. 10).
- Seven of the 15 evaluated TSGs are identified as parallelizable. With five Executors, the mean execution-time reduction is 51.31%; the paper reports 70.4% for one example and 32.9% for another in the aggregate discussion, while the detailed TSG6 case reports 70.6% (Source: Sec. 5.5–5.6, Fig. 11). This small numerical inconsistency should be retained for later verification rather than silently normalized.
- The operational prototype is described as being triggered hundreds of times weekly by over 170 monitors from more than 70 teams, with a 34% reduction in median incident mitigation time (Source: Sec. 7). This is practical deployment evidence, while the controlled experiment evaluates 80 incidents.

## 18. Scalability / Deployment

StepFly is implemented as a 6,698-line Python prototype excluding prompts. Executors run as individual processes, and the Scheduler can allocate several to independent DAG nodes. The system’s plugin interface is intended to extend to new domains such as network appliances and database clusters without changing the core scheduler/executor design (Source: Sec. 5, Sec. 7).

The paper reports a real-world operational prototype and broad monitor/team usage, but the controlled dataset is selected and guide-dependent. Parallelism improves wall-clock time only when the DAG exposes genuine independent work; it can increase token consumption when early sequential termination would otherwise have avoided unnecessary branches (Source: Sec. 5.5, Sec. 7).

## 19. Strengths

- Makes a previously implicit operational procedure executable and auditable.
- Uses an explicit DAG to constrain control flow and separate legal execution from free-form LLM planning.
- Extracts query templates into QPPs, reducing complex query generation errors and token overhead.
- Stores large typed plugin outputs outside the prompt, preserving structured values for later analysis.
- Supports parallel independent diagnostics and logs the full execution for SRE review.
- Reports both controlled incident evaluation and operational prototype usage.

## 20. Limitations

### Paper-supported limitations / qualifications

- Most existing TSGs contain clarity, data-flow, control-flow, database-instruction, or presentation problems; automation quality depends on guide quality (Source: Sec. 3.3–4.1).
- DAG and QPP extraction still involves human review, and parallelization requires domain experts to determine true independence (Source: Sec. 4.2, Sec. 4.5).
- LLM-generated decisions remain nondeterministic; fixed model/temperature settings and DAG constraints mitigate but do not eliminate this threat (Source: Sec. 6).
- Evaluation covers selected frequently used TSGs and service domains; specialized procedures, external dependencies, and cases requiring human judgment may not generalize (Source: Sec. 6).
- Current safety behavior is mainly read-only diagnosis; SREs review conclusions before mitigation (Source: Sec. 7).

### Further questions from this reading

- A TSG/DAG can constrain procedure execution, but it may be unable to represent unknown faults or a new causal path outside guide coverage.
- The paper does not isolate how much success comes from the DAG, QPPs, structured memory, executor prompting, or the choice of LLM.
- The execution conclusion is guide-dependent; agreement with a historical human label does not guarantee physical root-cause correctness.
- The lifetime, retention, forgetting, and cross-incident reuse policy of the MongoDB memory store are not specified.

## 21. Reproducibility

- Code available: **Yes.** The paper provides the [microsoft/StepFly repository](https://github.com/microsoft/StepFly) (Source: Sec. 1, Sec. 10).
- Dataset available: **Partly.** Synthesized incident data are released; the original 92-TSG/80-incident operational material is not presented as wholly public.
- Benchmark available: **Partly.** The evaluation protocol and selected data are described, but broad independent reproduction with private TSGs is not guaranteed.
- Prompt available: **Unclear / partly.** Prompt-based extraction and execution are described, but the complete prompt set is not established as public.
- Model/API specified: **Yes for evaluation models.** GPT-4.1, GPT-4.1-mini, GPT-4o, and Grok-3 are named.
- Hyperparameters: **Partly.** Three-run evaluation, model settings, executor counts, and success criteria are described; all operational configuration is not reproduced.
- Enough detail to reproduce: **Medium.** Public code and synthesized data help, but private TSGs, plugins, prompts, and production interfaces limit full reproduction.

## 22. Relationship to Existing AIOps Knowledge

StepFly adds an executable-procedure branch to [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md): candidate paths and conclusions can be constrained by a TSG rather than generated as an open-ended RCA search. It reinforces that an execution success metric is not automatically root-cause correctness.

Its QPP and plugin design extends [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md): a TSG is not only text, but can be compiled into checked control-flow metadata and parameterized actions. Its MongoDB key-value store gives [Memory](../../../concepts/memory.md) a concrete systems boundary—external structured working memory used to exchange large data within one execution, not demonstrated long-term episodic learning.

For [Planning](../../../concepts/planning.md), StepFly supplies a useful distinction: an explicit execution DAG can provide plan structure and legal transitions without an LLM Planner continuously inventing a plan. For [Tool Use](../../../concepts/tool-use.md), QPPs show that argument/template preparation can be moved into a deterministic interface rather than regenerated by the model on every call. The framework’s bounded scheduler/executor loop is relevant to [Agent](../../../concepts/agent.md), but its autonomy remains guide- and permission-constrained.

## 23. Relevance to My Research

### Similarities

- It targets infrastructure incident diagnosis using logs, metrics, incident tickets, code/deployment information, and operational procedures.
- It treats query generation, evidence transfer, control flow, failure handling, and execution latency as first-class system concerns.
- Its plugin interface and read-only safety posture are relevant to network telemetry and configuration inspection.

### Differences

- The method assumes an existing TSG and a guide-defined decision tree; it does not solve open-set network RCA when no procedure covers the incident.
- The evaluated service domains are online/cloud services; network devices, interfaces, links, optical modules, traffic, NetFlow, and syslog semantics are not directly evaluated.
- The “topology” is procedure/dependency structure, not a physical network topology or learned causal graph.
- The final action in the studied implementation is diagnosis output for SRE review, not autonomous network remediation.

### Potentially Useful Ideas

- Compile network troubleshooting procedures into explicit DAGs with preconditions, branches, termination, and fallback.
- Wrap complex KQL-like or network queries in typed parameterized plugins to avoid free-form query generation.
- Store large metric/traffic/log payloads as structured references and expose schema/sample views to the LLM.
- Use a scheduler to enforce dependency order, retry limits, early termination, and bounded parallelism.
- Log every query, observation, branch decision, and conclusion for later verification and operator review.

### Assumptions That May Not Transfer

- Network incidents may have no complete TSG, multiple simultaneous causes, or dependencies that are not safely represented by a static DAG.
- Parallel checks may compete for device rate limits or observe changing state, so independence must include temporal and operational constraints.
- A query plugin that is safe/read-only in a cloud data explorer may be expensive or disruptive on network devices.
- Historical TSG conclusions may encode team practice rather than physical causal truth.

### Experiments Worth Considering

- Compare free-form ReAct, DAG-constrained execution, and hybrid open-set fallback on network incident diagnosis.
- Measure the effect of typed query plugins and structured memory on tool errors, token cost, latency, and evidence provenance.
- Test parallel diagnosis under device rate limits, asynchronous telemetry, topology changes, and early termination.
- Add explicit unknown-coverage detection and human escalation when no TSG branch can justify a conclusion.

### Transferability to Network AIOps

**Medium-High for workflow infrastructure; Medium-Low for direct RCA.** The scheduler, typed tool interface, structured evidence store, audit log, and human gating transfer well. The dependence on guide coverage, cloud-service procedures, and read-only DevOps data limits direct transfer to open-set physical network RCA.

## 24. My Understanding

StepFly’s main contribution is not “an LLM that can troubleshoot.” It is the decision to make the operational procedure explicit before runtime: improve the guide, extract its control-flow DAG, extract safe query interfaces, and then let a bounded executor reason only about the current step. This turns a vague Agent trajectory into an auditable state machine with tools and structured data exchange.

The memory system is important precisely because it is narrow. A metric query can write a DataFrame to external storage and return only a key/schema/sample; a later code interpreter can read the value by key. That is a strong context-engineering and working-memory mechanism for large payloads, but the paper does not show that the system learns reusable episodic experiences across incidents. The strongest claim is reliable execution of documented workflows; the weaker claim is general autonomous RCA beyond documented workflows.

## 25. Questions

### Paper leaves unresolved

- How can StepFly detect that a TSG is out of coverage rather than confidently reaching an inappropriate termination point?
- How should DAGs and QPPs be updated when services, query schemas, permissions, or dependencies change?
- How should parallel execution handle changing state, rate limits, and dependencies that are only conditionally independent?
- How much does external structured memory improve correctness independently of DAG constraints and QPPs?

### Further questions for the knowledge base

- Can a network troubleshooting DAG combine deterministic known-fault branches with open-set candidate generation without losing auditability?
- What retention and forgetting policy should an operational memory store use if it later crosses incident boundaries?
- Which network actions should remain read-only plugins, and which require human approval, rollback, or a stronger safety contract?

## 26. Source Grounding

- TSG problem, structure, and example workflow: Sec. 1–2.2, Fig. 1.
- TSG empirical study and issue taxonomy: Sec. 3.1–3.3, Fig. 2–4, Table 1.
- Three-stage StepFly design: Sec. 4, Fig. 5.
- Quality improvement and TSG Mentor: Sec. 4.1.
- DAG extraction and QPP extraction: Sec. 4.2–4.3, Fig. 6–7.
- Scheduler, Executor, plugins, and structured memory: Sec. 4.4.1–4.4.4, Fig. 8.
- Parallelization: Sec. 4.5, Fig. 9.
- Dataset and ground-truth setup: Sec. 5.1–5.3.
- Baselines, success definition, latency, and token results: Sec. 5.4, Table 3, Fig. 10.
- Parallel execution results: Sec. 5.5, Fig. 11.
- Case studies: Sec. 5.6.
- Threats, operational prototype, safety, and extensibility: Sec. 6–7.
- Data availability and repository: Sec. 10.

## 27. Tags

`AIOps` `incident-diagnosis` `TSG` `execution-DAG` `scheduler-executor` `QPP` `tool-use` `structured-working-memory` `parallel-execution` `human-in-the-loop` `network-transferability`

## Code / Implementation

- Repository: [microsoft/StepFly](https://github.com/microsoft/StepFly)
- Official status: Confirmed Official
- Read at commit: `a6229192a69dd2eebc58d9b8f754dbc396029c4e`
- Code notes: [StepFly source-code notes](../../../code/aiops/stepfly/notes.md)
- Implementation coverage: Scheduler/executor loops, TSG and PlanDAG loading, tools/plugins, MongoDB session memory, and status updates.
