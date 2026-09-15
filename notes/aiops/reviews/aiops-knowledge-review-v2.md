# AIOps Knowledge Review v2

## Scope

**Focus:** Agentic Incident Management

This review consolidates the second AIOps full-paper batch:

- [Comfey](../../../papers/aiops/comfey/notes.md)
- [AIM](../../../papers/aiops/aim/notes.md)
- [StepFly](../../../papers/aiops/stepfly/notes.md)
- [TSGen](../../../papers/aiops/tsgen/notes.md)
- [ChatRCA](../../../papers/aiops/chatrca/notes.md)

[AIOps Knowledge Review v1](aiops-knowledge-review-v1.md) is used as background for the earlier detection/RCA, topology, evidence, and production-evaluation distinctions. This document does not repeat Batch 1 as a second full-paper reading.

## Evidence Convention

- **Paper-backed fact:** a claim reported or explicitly qualified in an individual paper note, with the relevant section, table, or figure recorded there.
- **Cross-paper synthesis:** a comparison or abstraction made from several paper notes.
- **Current interpretation:** a cautious working model for this knowledge base, or a question that the current papers do not settle.

The terms **Agent**, **agentic**, **memory**, **planning**, **RCA**, and **production** are therefore not treated as interchangeable paper labels.

## 1. What I Understand So Far

### Paper-backed facts

- **Comfey** addresses production incident triage and team-ownership routing. Team-local agents enrich an incident, decide accept/reject, and transfer it through TSG rules or a Global Routing Table. Its evaluated label is the responsible team, not a physical root node or a complete causal explanation (Source: [Comfey note](../../../papers/aiops/comfey/notes.md), Sec. 2.1, Sec. 3.3–3.6, Sec. 4.5).
- **AIM** aligns metrics, logs, traces, and alerts into prompt context, retrieves historical exemplars, generates a mitigation plan, and has a separate plan-to-code path that validates and runs Ansible in the Robot Shop testbed. It does not demonstrate a continuously observing production Agent with online replanning (Source: [AIM note](../../../papers/aiops/aim/notes.md), Sec. 3.1–3.4, Sec. 4.4.6).
- **StepFly** turns troubleshooting guides into quality-controlled execution DAGs and query-preparation plugins. A Scheduler and Executors use plugin observations, dependencies, retries, and branches to run documented diagnosis paths; the reported implementation is read-oriented and uses external structured data exchange (Source: [StepFly note](../../../papers/aiops/stepfly/notes.md), Sec. 4.2–4.4, Sec. 5.4, Sec. 7).
- **TSGen** is an offline pipeline that filters and distills historical incident discussions, generates decision-tree/DAG troubleshooting guides, and updates them with human review. It creates operational knowledge for a later workflow; it does not itself query a live environment, perform runtime RCA, or execute remediation (Source: [TSGen note](../../../papers/aiops/tsgen/notes.md), Sec. 4, Sec. 7.2–7.3).
- **ChatRCA** uses role-specialized LLM agents to collect observations, retrieve architecture context and historical cases, exchange hypotheses, request more evidence, and place human checks at the data-ticket and root-cause decision points. It does not perform state-changing repair in the evaluated workflow (Source: [ChatRCA note](../../../papers/aiops/chatrca/notes.md), Sec. 4.1–4.3, Sec. 5.7–5.8).

### Cross-paper synthesis

The five papers are not five versions of one Agent architecture. They cover different layers of an incident-management stack:

1. **Create operational knowledge:** TSGen.
2. **Route an incident to the right owner:** Comfey.
3. **Interpret alerts and generate a mitigation plan:** AIM.
4. **Execute a documented diagnostic procedure:** StepFly.
5. **Conduct collaborative, human-gated RCA:** ChatRCA.

The most useful common structure is not “LLM in, root cause out.” It is a bounded process in which the system has an incident goal, receives evidence, makes one or more decisions, invokes a permitted operation or role, and is subject to a termination, verification, or human-escalation condition.

## 2. Cross-Paper Relationships

| Paper | Primary layer | Observation / action | Planning or orchestration | Knowledge / state | Verification, human role, and remediation |
| --- | --- | --- | --- | --- | --- |
| Comfey | Production triage and team routing | Team-local queries and enrichment; accept, reject, or transfer | Implicit next-team decision using TSGs, routing statistics, hop limits, and fallback | Historical incidents, TSGs, routing table, and transfer attachments | Ownership outcome and human fallback; can connect to an existing mitigation engine, but is not physical RCA or unrestricted repair |
| AIM | Alert interpretation, RCA-category alignment, and mitigation planning | Prompt-level multimodal context; generated Ansible is executed only in a controlled Robot Shop testbed | Explicit plan-first Plan to Act path; no demonstrated online replanning | Retrieved exemplars and prompt context; no specified episodic memory policy | YAML/namespace checks, testbed outcome, SRE judgments; no production autonomous remediation |
| StepFly | Execution of documented incident diagnosis | Typed query plugins and code analysis produce observations; DAG state drives branches, retries, and parallel steps | Explicit TSG-derived DAG plus Scheduler and Executors; bounded orchestration, not free-form planning | Per-execution key-value store for typed data; TSG/QPP are durable procedures | SRE-corrected guide/DAG/QPP annotations and path/conclusion checks; mainly read-only |
| TSGen | Operational-knowledge generation and maintenance | Processes historical records rather than a changing live environment | Generates a decision-tree/DAG artifact offline; no runtime Planner | Persistent TSGs, incident records, and caches; operational knowledge rather than Agent memory | Human engineering review and publication; no runtime remediation |
| ChatRCA | Multimodal RCA, localization, diagnosis, and explanation | Observation and Architecture roles query evidence; Experts retrieve cases and request more data | Manager chooses roles and Experts iterate hypotheses; no formal Planner interface | Shared GroupChat context plus a 147-case RAG store; no specified episodic write-back | Human verifies data tickets and adjudicates root cause; no autonomous repair or recovery loop |

The table is a cross-paper synthesis. Each row is grounded in the corresponding formal note; the common columns are an analysis framework, not a shared design proposed by the five papers.

## 3. What Should Count as Agentic AIOps?

### Working definition

For the current knowledge base, **Agentic AIOps** means an incident-oriented system that has a goal or task state, consumes observations or feedback, selects among bounded next operations or roles, and continues, terminates, escalates, or changes its route based on the resulting state. The system must expose enough of its action boundary to distinguish evidence collection, diagnosis, recommendation, and state-changing remediation.

This is a **working definition**, not an accepted industry standard. An LLM, a tool, a RAG store, or several prompts may be part of such a system, but none is sufficient by itself.

### Boundary between common labels

- **LLM-assisted AIOps:** an LLM generates a summary, label, guide, explanation, or plan inside a mostly predetermined pipeline. TSGen is the clearest Batch 2 example.
- **Tool-augmented LLM:** an LLM can receive results from a defined retrieval or execution interface. AIM, StepFly, and ChatRCA contain tool-using paths, but their degrees of runtime choice differ.
- **Agentic workflow:** the workflow carries state across steps and allows observations or outcomes to determine a bounded next step. StepFly, Comfey, and ChatRCA fit this description; AIM fits it more narrowly through its Plan to Act organization and controlled execution extension.
- **Agent:** a stronger implementation-level claim: a goal-directed component has an action space, state/observation handling, decision authority, and a loop or termination condition. The paper’s use of “Agent” still requires checking those properties.
- **Multi-Agent:** more than one role or component has a distinct objective/capability and communicates or hands off state in a way that matters to the task. Multiple prompts around one serial call are not sufficient evidence.

### Batch 2 classification

- **Comfey:** the paper calls it a decentralized multi-agent framework; the current interpretation is a bounded agentic triage workflow with team-local agents, not a physical-RCA Agent.
- **AIM:** a bounded agentic Plan to Act or tool-augmented LLM workflow; its paper label is stronger than the demonstrated evidence for a continuously autonomous production Agent.
- **StepFly:** a bounded scheduler-executor agentic workflow. Its action space is constrained by a guide-derived DAG and plugins; its Executors are not shown as independent negotiating Agents.
- **TSGen:** an LLM-assisted operational-knowledge curation pipeline, not a demonstrated runtime Agent.
- **ChatRCA:** a bounded multi-agent investigative RCA workflow with shared context, distinct role capabilities, iterative evidence collection, and human gates; not an autonomous remediation Agent.

## 4. Agentic Incident Lifecycle

The following is a **cross-paper synthesis**:

Incident or Alert
→ Context and Evidence Collection
→ Candidate or Hypothesis Generation
→ Tool or Role Selection
→ Tool Execution and Observation
→ Diagnosis, Ranking, or Explanation
→ Verification or Human Gate
→ Recommendation or Gated Remediation
→ Outcome Feedback and Knowledge Update

The papers cover this lifecycle unevenly:

| Lifecycle stage | What Batch 2 supports |
| --- | --- |
| Observe / Detect | All five mostly assume an incident, alert, or historical incident record. AIM constructs alert inputs from labeled anomalous intervals; Comfey and ChatRCA receive incidents; none is a complete new detector in this batch. |
| Context and evidence | AIM performs time/entity alignment; Comfey performs team-local enrichment; StepFly runs typed query plugins; ChatRCA creates a data ticket and architecture context; TSGen selects historical text for knowledge generation. |
| Candidate or hypothesis generation | Comfey narrows possible owning teams; AIM produces root-cause categories and plans; StepFly follows guide-defined paths; ChatRCA creates and tests hypotheses; TSGen creates guide branches rather than live incident candidates. |
| Tool or role selection | Comfey chooses a next team; StepFly’s Scheduler chooses ready DAG nodes; ChatRCA’s Manager/AutoGen chooses roles; AIM retrieves exemplars and hands a plan to code generation; TSGen has no live selection loop. |
| Observation and feedback | StepFly has within-execution plugin results and edge state; ChatRCA can request more evidence and receive human edits; Comfey transfers structured evidence and rejection rationale; AIM has testbed outcomes; TSGen has later incident and engineering-update feedback. |
| Verification | ChatRCA has explicit data-ticket and root-cause human checkpoints; AIM has lightweight code validation and testbed outcomes; StepFly and TSGen rely on guide/annotation/engineering checks; Comfey has ownership feedback and human fallback. |
| Remediation | AIM is the only Batch 2 paper with a reported state-changing execution path, and that path is constrained to a testbed. Comfey can connect to an existing mitigation engine. StepFly and ChatRCA are read-oriented in the evaluated workflows; TSGen only produces knowledge. |
| Recovery and learning | No paper demonstrates a complete observe-repair-verify-recover loop in live network infrastructure. Comfey and TSGen update operational records/guides, but that is not the same as a general Agent policy or memory-learning loop. |

An important boundary is that **retrieval**, **tool execution**, **diagnosis**, and **remediation** are separate capabilities. A system can retrieve a runbook without executing it, execute a read-only query without repairing anything, or generate a convincing explanation without locating the physical root cause.

## 5. Planning and Orchestration

### What the five papers show

- **Comfey:** the next-team choice is a stateful routing decision. It has plan-like progression through teams, but no independently represented multi-step plan or Planner component.
- **AIM:** the mitigation plan is explicitly generated before the code/execution stage. This is genuine plan generation, but the paper does not show that new live observations cause a Planner to revise the plan.
- **StepFly:** the TSG-derived DAG is an explicit execution structure. Scheduler decisions, branches, retries, and parallelism are planning-adjacent control, but the legal steps and edges are compiled from the guide rather than freely invented at runtime.
- **TSGen:** a generated decision tree/DAG organizes future troubleshooting actions. It is an offline operational artifact, not evidence of an online Planner.
- **ChatRCA:** Manager role selection and Expert hypothesis iteration organize an investigation. They are prompt-driven orchestration and a bounded hypothesis loop, not a separately evaluated formal Planner.

### Working distinctions

- **Reasoning about the next step** asks what evidence or action is useful now.
- **Task decomposition** breaks a goal into smaller subproblems.
- **Plan generation** represents an ordered or conditional set of future steps.
- **Explicit Planner** is a separately identifiable component or procedure whose output is a plan consumed by an execution component.
- **Replanning** changes the future plan because new observations invalidate or alter the previous one.
- **Workflow orchestration** may select steps using fixed rules, a DAG, role protocols, or a scheduler without generating a new plan.

Therefore, a multi-step workflow is not automatically an explicit Planner architecture. Batch 2 gives evidence for plan-first execution and constrained orchestration, but limited evidence for robust online replanning.

### Planning is not search

Planning can use search, but does not require MCTS, exhaustive enumeration, or a world model. Conversely, retrieval over historical cases or selecting the next role is not automatically search-based planning. None of the five Batch 2 papers establishes a general search-based planner over a large physical network state space. The earlier Planning Review covers LLM+P and RAP as distinct search/solver examples; they are background, not part of this AIOps batch.

## 6. Tool, Knowledge, and Memory Boundaries

### Tool roles

- **Comfey:** local scripts, Kusto queries, monitoring APIs, and telemetry backends enrich an incident; the main action is routing.
- **AIM:** exemplar retrieval is context retrieval; Ansible generation and execution form the potentially state-changing path.
- **StepFly:** log, metric, DevOps, code-interpreter, and QPP plugins execute typed queries and pass results to later steps.
- **ChatRCA:** Observation and Architecture roles query telemetry/dependency data; Experts can retrieve historical cases through RAG.
- **TSGen:** retrieval, embeddings, clustering, and vector-store operations process historical records offline; they are not runtime troubleshooting tools.

### Knowledge and RAG are not automatically memory

The papers show several kinds of durable or semi-durable information:

| Information | What it is in this batch | What it is not established to be |
| --- | --- | --- |
| Historical incidents, TSGs, SOPs, routing tables | Operational knowledge used for matching, guidance, or execution | A universal episodic Agent memory |
| AIM exemplars and ChatRCA historical cases | Retrieved evidence or examples supplied to a prompt | A write/update/forget memory policy |
| StepFly key-value payloads | External structured working data within an execution | Cross-incident long-term memory |
| ChatRCA GroupChat | Current shared working context | Persistent memory across incidents |
| TSGen caches and published guides | Persistent knowledge-generation infrastructure | Runtime Agent state |

The central synthesis is:

**RAG answers “which stored knowledge should be brought into this context?” Memory additionally requires a defined lifecycle for what is written, when it is retrieved, how it is updated, and when it is forgotten or invalidated.**

### Memory lifecycle in the five systems

- **Comfey:** operational records and routing statistics persist and are refreshed from outcomes. The paper does not define general episodic selection, conflict resolution, or forgetting.
- **AIM:** historical examples are read for adaptive prompting. Episodic write-back, cross-incident retention policy, and stale-example retirement are not specified.
- **StepFly:** plugin outputs are written under keys and read by downstream steps during one execution. Cross-incident retention, compression, and forgetting are not established.
- **TSGen:** historical records and TSGs are retained and incrementally updated after engineering review. This is an operational-knowledge lifecycle, not a demonstrated runtime Agent memory lifecycle.
- **ChatRCA:** the current GroupChat is working context and the 147-case store is retrieved knowledge. Automatic case write-back, stale-case retirement, and cross-session episodic memory are not specified.

The Batch 2 papers also do not implement a Reflexion-style evaluator → language reflection → next-attempt episodic loop. Human feedback and guide updates are related feedback mechanisms, but **feedback is not automatically reflection, and reflection is not memory itself**.

## 7. RCA, Diagnosis, Explanation, and Remediation

These labels are often used broadly in AIOps papers, but they represent different outputs:

- **Localization:** which node, service, component, or other candidate is implicated?
- **RCA:** what causal or root-cause explanation accounts for the incident?
- **Diagnosis:** what fault type or condition is present?
- **Explanation:** how does the system justify or verbalize its conclusion?
- **Remediation:** what action should be taken, or was a repair actually executed and verified?

| Paper | Main evaluated output | What must not be overclaimed |
| --- | --- | --- |
| Comfey | Team ownership accept/reject and routing efficiency | Routing to the right team is not physical root-cause localization |
| AIM | Alert summary, root-cause category/token alignment, plan quality, and testbed task completion | Text/category alignment is not unique causal RCA; generated code is not production autonomous repair |
| StepFly | Guide/DAG/QPP quality, diagnostic path and conclusion agreement, execution efficiency | Executing a documented path is not proof of open-set causal correctness |
| TSGen | Incident-discussion coverage, retrieval usefulness, guide quality, and guide acceptance | Guide coverage/retrieval is not online RCA accuracy |
| ChatRCA | Service/component Top-k localization, fault-category prediction, explanation consistency, and human agreement | A correct category or similar explanation is not sufficient evidence of physical causality or safe action |

This distinction matters for future Network AIOps evaluation: a model that names the right fault category but the wrong interface, link, or device should not receive the same credit as one that localizes and verifies the physical root cause.

## 8. Verification, Reliability, and Human Control

### What counts as verification

Verification means an independent check against evidence, structure, execution outcome, or a human decision. The LLM merely stating that its conclusion is “confirmed” is not independent verification.

Batch 2 provides several different levels:

- **Comfey:** final ownership feedback, transfer history, hop limits, and human fallback constrain routing. They verify organizational handling more than physical causality.
- **AIM:** YAML and namespace checks plus Robot Shop execution outcomes test whether a generated action can run in the controlled environment. They do not establish production safety, rollback, or network permissions.
- **StepFly:** SRE-corrected DAG/QPP annotations and path/conclusion checks validate guide execution. They are strong structural checks within guide coverage, not universal causal checks.
- **TSGen:** engineering review and publication acceptance validate the usefulness of generated guides. Acceptance does not prove every future branch is causally correct.
- **ChatRCA:** humans verify the data ticket and later adjudicate root-cause conclusions. The paper also separates category correctness from reasoning-process and evidence consistency; this is stronger than text-quality scoring, but still not a complete physical-world verifier.

### Reliability risks

Across the papers, unresolved risks include incomplete or contradictory telemetry, stale TSG/RAG knowledge, wrong tool arguments, closed candidate spaces, hallucinated explanations, unclear out-of-coverage behavior, human-review cost, and unsafe state-changing actions. The papers use different safeguards, so no common reliability claim can yet be made.

Human-in-the-loop should be viewed as a control design, not merely as an admission that the Agent failed. The relevant question is where human review is most valuable: evidence completeness, high-impact diagnosis, permission to change state, recovery verification, or knowledge publication.

## 9. Multi-Agent: What Is Actually Added?

ChatRCA provides the strongest explicit Batch 2 example: Manager, Observation, Architecture, Operation, Expert, and Human roles have distinct objectives, prompts, capabilities, and communication responsibilities. The system can request further evidence and use human adjudication (Source: [ChatRCA note](../../../papers/aiops/chatrca/notes.md), Sec. 4.1–4.3).

Comfey also has decentralized team-local agents with local evidence access and transfer decisions, but its core benefit is organizational decentralization and data sovereignty rather than a general multi-agent reasoning theory (Source: [Comfey note](../../../papers/aiops/comfey/notes.md), Sec. 3.1–3.8).

StepFly has multiple Executor processes, but they are homogeneous bounded workers under a shared Scheduler. This is not evidence that independent Agents must negotiate. AIM separates plan and action stages, but the paper does not establish that each stage is an independent Agent. TSGen is not a runtime multi-agent system.

ChatRCA ablations show gains when roles, observation, experts, and human feedback are added, but they do not match single-agent and multi-agent systems for context length, tool calls, tokens, latency, or human effort. Thus the current conclusion is:

**Role specialization is useful in the evaluated settings; the minimum necessary conditions and general advantage of multi-agent execution remain open.**

## 10. Production and Evaluation

Production claims need three separate questions:

1. Was the data collected from production?
2. Was the system evaluated at production-like scale?
3. Was the Agent actually deployed online with permissions to affect production state?

The answers differ:

- **Comfey** reports 22 months of Azure production operation, about 19,500 triaged incidents, 15 teams, and millions of hosts. This is strong evidence for production triage and routing, not for autonomous physical RCA or repair (Source: [Comfey note](../../../papers/aiops/comfey/notes.md), Sec. 4.1–4.5).
- **AIM** evaluates 100 selected samples and a Robot Shop fault-injection testbed. It provides a controlled plan-to-code execution result, not a live production deployment (Source: [AIM note](../../../papers/aiops/aim/notes.md), Sec. 4.1–4.4.6).
- **StepFly** evaluates 80 incidents and reports a prototype triggered hundreds of times weekly by more than 170 monitors and 70 teams, with a reported median mitigation-time reduction. The prototype remains guide- and permission-constrained and mainly read-only (Source: [StepFly note](../../../papers/aiops/stepfly/notes.md), Sec. 5, Sec. 7).
- **TSGen** uses large private historical records and reports 53 generated TSGs, of which 38 were accepted/published after engineering review. This is operational deployment of knowledge curation, not deployment of an autonomous incident Agent (Source: [TSGen note](../../../papers/aiops/tsgen/notes.md), Sec. 5, Sec. 7).
- **ChatRCA** evaluates public benchmark settings plus a private CMCC collection of real and drill incidents, including 43 master nodes, 140 services, 311 pods, and 382 containers. It reports operational feedback, but not online throughput, cost, or autonomous recovery deployment (Source: [ChatRCA note](../../../papers/aiops/chatrca/notes.md), Sec. 5–6).

The evaluation protocols are not directly comparable. They mix routing accuracy, category and localization Top-k, guide coverage, retrieval accuracy, human consistency, task completion, mitigation time, and operational acceptance. Batch 2 does not yet provide a common Agent evaluation suite covering diagnosis correctness, evidence correctness, tool correctness, steps, latency, token/API cost, safety, human effort, remediation success, and recovery.

## 11. Common Misconceptions

- **LLM or tool use equals Agent:** false. An LLM can generate a summary, and a tool can return evidence, without any goal-directed next-action loop.
- **RAG equals Agent memory:** false. RAG retrieves stored knowledge; memory additionally needs a lifecycle and task-state semantics.
- **Multi-role prompt equals Multi-Agent:** not sufficient. Distinct role capabilities, communication, state handoff, and measured task relevance matter.
- **A plan equals an explicit Planner:** false. A plan may be a generated artifact, a fixed DAG, or a guide. A separate Planner and an execution interface are stronger evidence.
- **Planning equals search:** false. Search is one possible implementation; fixed workflow planning and DAG scheduling do not require search.
- **Retrieval equals tool execution:** false. Looking up a document or case is different from running a telemetry query or changing system state.
- **Generated remediation script equals autonomous remediation:** false. AIM executes in a controlled testbed and does not demonstrate safe production autonomy.
- **A correct fault category equals RCA correctness:** false. ChatRCA’s category, reasoning consistency, and evidence consistency are separately evaluated; AIM’s category/token alignment is also a proxy.
- **Production data equals production deployment:** false. TSGen and ChatRCA use production or enterprise data without demonstrating autonomous state-changing online operation.
- **Feedback equals reflection:** false. Outcome feedback, human edits, guide updates, and Reflexion-style verbal reflection are different mechanisms.
- **A topology or dependency context is automatically a causal graph:** false. Service dependencies and organizational routing structures constrain reasoning but do not by themselves prove causality.

## 12. What These Papers Explain Well

The current batch gives useful evidence for:

1. Separating operational knowledge generation, incident routing, evidence collection, diagnosis, and remediation.
2. Making tool boundaries and structured evidence handoffs explicit.
3. Using fixed guides, DAGs, routing constraints, or role protocols to bound LLM behavior.
4. Treating human verification and escalation as part of the system design.
5. Evaluating text quality, diagnosis/category correctness, path correctness, operational outcomes, and deployment impact as different dimensions.
6. Showing that an apparently “Agentic” system can be meaningful without being a fully autonomous repair system.

## 13. What These Papers Do Not Yet Explain

The five papers leave the following capabilities insufficiently answered:

- Robust dynamic planning and replanning for changing, open-world incidents.
- A common definition and evaluation of Agentic AIOps autonomy.
- Whether multi-agent role separation still helps after matching context, tool calls, token cost, latency, and human review.
- A memory lifecycle covering write, retrieval, selection, compression, update, conflict handling, invalidation, and forgetting.
- How to distinguish historical frequency or guide coverage from physical causal correctness.
- Safe state-changing remediation with permissions, rollback, recovery observation, and failure containment.
- A common protocol for missing, delayed, or contradictory multimodal telemetry.
- Open-set, multi-root, and uncertain root-cause ground truth.
- Network-specific evidence over devices, interfaces, links, optical modules, syslog, traffic, NetFlow, and physical topology.

## 14. Required Questions for This Review

1. **What should be called Agentic AIOps?**
   **Current interpretation:** a bounded incident workflow that uses state/observations to select subsequent roles, tools, branches, escalation, or actions. The definition is evolving and is not a paper-standard threshold.

2. **How are LLM-assisted AIOps, tool-augmented LLM, agentic workflow, Agent, and Multi-Agent different?**
   **Cross-paper synthesis:** they form increasing claims about stateful decision authority and interaction. Tool access and multiple prompts are ingredients, not sufficient evidence of the stronger labels.

3. **Which Batch 2 systems have an observation → decision → action → new observation loop?**
   StepFly has the clearest within-execution query-result-to-next-step loop. ChatRCA can request more evidence after hypotheses and human data-ticket feedback. Comfey changes routing after local enrichment and rejection. AIM has controlled execution outcomes but no demonstrated live replanning. TSGen has no live loop.

4. **Is planning real or just workflow orchestration?**
   AIM has explicit plan generation; StepFly has an explicit execution DAG; the others mainly have routing or role orchestration. None proves a general online Planner that revises an arbitrary plan in a live network.

5. **What does multi-agent add over a single Agent?**
   The papers suggest local expertise, capability separation, data ownership, and parallel or staged evidence work. They do not isolate the causal benefit of independent Agents from extra prompts, context, tools, or human review.

6. **What role do tools play in incident investigation?**
   They turn an LLM’s request into telemetry, architecture, log, metric, historical-case, or action evidence. Their value depends on interface typing, permissions, provenance, failure handling, and whether the tool is read-only or state-changing.

7. **How do Knowledge/RAG and Agent Memory differ?**
   RAG supplies selected stored knowledge to the current context. Memory additionally specifies write/read/update/retention semantics for state or experience. The Batch 2 systems mostly show operational knowledge or working context, not a complete persistent Agent memory architecture.

8. **How do RCA, diagnosis, explanation, and remediation connect?**
   A typical sequence is candidate localization and fault diagnosis, followed by a causal explanation, recommendation, optional action, and recovery verification. The stages can fail independently and must be evaluated independently.

9. **Why is verification important?**
   It tests whether the evidence, structure, diagnosis, or action is consistent with something outside the model’s own prose. ChatRCA’s separate evidence/reasoning/category checks and AIM’s testbed execution illustrate this separation.

10. **Which systems actually execute remediation?**
    AIM has a constrained Robot Shop Ansible execution path. Comfey may connect to an existing mitigation engine. StepFly and ChatRCA are read-oriented in the reported workflow; TSGen only generates guides.

11. **Where should humans remain involved?**
    At minimum, before high-impact state changes, when evidence is incomplete or contradictory, when confidence is low or the incident is out of coverage, and when a new operational guide or memory entry is published. ChatRCA demonstrates data-ticket and root-cause checkpoints.

12. **How should Agentic AIOps be evaluated beyond text quality?**
    Separate incident/task success, candidate and root-cause correctness, evidence correctness, tool-call correctness, path/step efficiency, latency, cost, safety, human effort, remediation success, and recovery verification.

13. **Should token cost, latency, tool calls, and safety be core metrics?**
    **Current interpretation:** yes for an operational Agent, because a diagnosis that is accurate but too slow, expensive, permission-unsafe, or intervention-heavy may not be useful. Batch 2 does not yet establish a shared measurement protocol.

14. **Which ideas transfer most easily to Network AIOps?**
    Typed read-only telemetry tools, evidence tickets with time/entity provenance, deterministic candidate pruning, topology-aware constraints, guide/DAG execution, explicit verification, and human-gated remediation are the strongest candidates. Physical network assumptions still require direct validation.

15. **What is the largest current Agentic AIOps gap?**
    **Current interpretation:** a reliable end-to-end evaluation and control loop that connects uncertain multimodal network evidence to candidate reduction, verifiable RCA, safe action, recovery feedback, and maintainable operational knowledge.

## 15. Current Agentic AIOps Mental Model

**Cross-paper synthesis, not a standard architecture:**

Incident / Alert
→ Evidence and context adapters
→ Candidate or hypothesis generation
→ Topology, dependency, guide, or knowledge constraints
→ Tool or role selection
→ Bounded execution
→ Observation normalization with provenance
→ Ranking, diagnosis, and explanation
→ Independent verification or human gate
→ Recommendation or permissioned remediation
→ Recovery observation
→ Knowledge update, retirement, or escalation

The five papers occupy different segments of this model. TSGen supplies knowledge upstream; Comfey supplies team routing; AIM supplies plan-to-act; StepFly supplies guide-constrained execution; ChatRCA supplies role-specialized investigative reasoning and human adjudication. A future network system should not assume that one LLM should own every segment.

## 16. Working Autonomy Taxonomy

This taxonomy is a **current knowledge-base interpretation**, not a recognized standard:

| Level | Working description | Batch 2 examples |
| --- | --- | --- |
| A0 | Text or artifact generation without runtime decision state | TSGen’s guide-generation stages; AIM’s summary-only path |
| A1 | Retrieval or knowledge augmentation for the current task | AIM exemplars, ChatRCA historical cases, TSGen knowledge retrieval |
| A2 | Fixed or bounded tool/workflow execution | AIM’s controlled Plan to Act path; guide-constrained portions of StepFly |
| A3 | Observation-driven selection among bounded next roles, tools, branches, or routes | Comfey routing, StepFly Scheduler transitions, ChatRCA’s role/hypothesis loop |
| A4 | Dynamic replanning plus independent verification over changing observations | Not established by Batch 2 |
| A5 | Permissioned state-changing remediation followed by recovery observation and closed-loop adaptation | Not established by Batch 2 |

The levels are not a score for paper quality. They separate demonstrated interaction capabilities from stronger autonomy claims. A system can be valuable at A2 or A3 without claiming A4/A5.

## 17. Implications for Network AIOps Research

### Ideas worth learning from

- Normalize metrics, syslog, traces, traffic/NetFlow, configuration, and topology into evidence objects with entity, time window, provenance, and freshness.
- Use deterministic anomaly aggregation and topology/candidate constraints before expensive LLM reasoning, especially when the candidate space contains thousands or more devices, interfaces, links, or modules.
- Expose read-only typed tools for metric, log, flow, configuration, and topology queries; distinguish retrieval, observation, action, and remediation permissions.
- Represent diagnosis procedures as auditable branches or DAGs when the procedure is known, while retaining an explicit unknown/out-of-coverage path.
- Place independent verification and human gates before high-impact actions or publication of new operational knowledge.

### Design boundaries

- **Topology as context:** provide dependencies or neighborhood information to help interpret evidence.
- **Topology as a hard constraint:** forbid or down-rank candidates that violate known reachability or dependency rules.
- **Topology as a tool:** allow the workflow to query current topology and version changes.
- **Topology as a causal claim:** require additional evidence; a dependency graph alone is not proof of causality.

The first three roles can coexist, but they should not be conflated with the fourth.

### Ideas that may not transfer directly

Microservice service graphs, team ownership, fixed fault categories, cloud-specific SOPs, and closed benchmark candidates may not map to physical devices, interfaces, optical modules, links, dynamic routing, NetFlow, or open-set multi-root incidents. Human review procedures that are feasible for dozens of cases may also be too expensive for high-volume network alerts.

## 18. Next Learning Priorities

1. **Network-specific multimodal evidence alignment:** time/entity alignment and provenance across metrics, syslog, traces, traffic/NetFlow, configuration, and physical topology.
2. **Open-set and multi-root topology-aware RCA:** candidate generation, causal versus dependency semantics, uncertainty, and ground truth for device/interface/link faults.
3. **Tool-grounded Agent reliability and safe remediation:** typed interfaces, permission boundaries, verification, rollback, recovery observation, and abstention.
4. **Operational knowledge and memory lifecycle:** guide/version management, retrieval selection, compression, stale/conflicting knowledge, retirement, and the boundary between memory and RAG.
5. **Agent evaluation under production constraints:** matched single/multi-agent comparisons, token/API cost, latency, tool calls, human effort, safety, and end-to-end incident outcomes.

These priorities are chosen from the current gaps, not from a complete literature survey. The next batch should remain focused rather than mixing all five themes at once.

## 19. Source Grounding

The paper-specific facts in this review are traceable to the completed notes:

- [Comfey note](../../../papers/aiops/comfey/notes.md), especially Sec. 2–4 for triage scope, local tools, routing, production setting, and limitations.
- [AIM note](../../../papers/aiops/aim/notes.md), especially Sec. 3–4 for multimodal context, Plan to Act, validation, testbed execution, and evaluation.
- [StepFly note](../../../papers/aiops/stepfly/notes.md), especially Sec. 4–7 for DAG/QPP execution, structured working data, guide coverage, and deployment.
- [TSGen note](../../../papers/aiops/tsgen/notes.md), especially Sec. 4–8 for knowledge curation, guide generation/update, deployment, and limitations.
- [ChatRCA note](../../../papers/aiops/chatrca/notes.md), especially Sec. 4–6 for role capabilities, tools, human checkpoints, evaluation, and deployment limits.

The quantitative claims retain the section/table references recorded in those notes. The Agent boundary, autonomy levels, lifecycle, mental model, and Network AIOps implications are explicitly cross-paper synthesis or current interpretation; they are not attributed to any single paper.
