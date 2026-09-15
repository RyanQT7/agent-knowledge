---
name: aiops-paper-reading
description: Read one AIOps, infrastructure-operations, or network-operations paper PDF end to end and integrate grounded task, telemetry, RCA, Agent, production, and Network AIOps findings into this knowledge base. Use for one formal AIOps paper, not batch processing or lightweight triage.
---

# AIOps Paper Reading

## Purpose and boundary

Use this Skill for one formal full-paper reading task involving AIOps, infrastructure operations, cloud operations, network operations, fault management, or a closely related LLM/Agent system.

The workflow is:

~~~text
Locate one source PDF
→ Read the paper as completely as the local tools allow
→ Write an AIOps-structured paper note
→ Ground facts in sections, tables, figures, or appendices
→ Update only durable AIOps or Agent Concepts
→ Add meaningful cross-references, questions, inventory, map, log, and INDEX entries
→ Check research relevance and Network AIOps transferability
→ Run quality checks
→ Commit and push the completed knowledge task
~~~

This Skill specializes the generic [paper-reading Skill](../paper-reading/SKILL.md); it does not replace or duplicate its general principles. It is a single-paper workflow. Do not use it to process a batch, perform a literature survey, create a new AIOps Skill, or start a Knowledge Review. Use the existing learning-batch and knowledge-review workflows only when the user separately requests those tasks.

Do not download other material, use Web by default, install dependencies, introduce RAG/vector infrastructure, modify experiment code, or process another paper.

## Work from the knowledge-base root

Use /home/xieqitong/agent-knowledge or the current repository root as the working directory. Before editing, inspect the relevant source directory, existing papers/aiops/ notes, INDEX.md, notes/aiops/, and current Concepts.

Raw PDFs belong under:

~~~text
sources/papers/AIOps_papers/
~~~

Formal notes belong under:

~~~text
papers/aiops/<paper-id>/notes.md
~~~

Do not put the source PDF in papers/, and do not move or delete source files merely to fit a naming convention. If a PDF is supplied elsewhere inside the knowledge base and the correspondence is clear, it may be organized into the AIOps source directory; preserve originals outside the knowledge base.

Use a short, stable, lowercase <paper-id> based on the commonly used title or abbreviation. Resolve an explicit path first. If it is missing, search only the knowledge-base root, sources/papers/, and papers/ for one obvious same-paper match, ignoring harmless case, spacing, and filename differences. If no clear match exists, stop with NEEDS REVIEW; do not invent a paper or use unsupported memory.

If a complete note already exists and the user has not explicitly asked for a revision, do not create a duplicate note. Report that the paper is already processed.

## Full-paper reading

Read the complete local PDF as far as available tools permit. Do not produce the note from only the abstract, introduction, or conclusion. Inspect the parts that materially determine the contribution:

- Title page, metadata, abstract, and introduction.
- Background, problem setting, method, architecture, algorithms, and workflow.
- Data, incident or failure setting, ground truth, candidate construction, and topology.
- Experiment setup, baselines, metrics, tables, figures, ablations, case studies, and scalability.
- Production/deployment claims, limitations, reproducibility information, and useful appendix material.

Use local PDF extraction or rendering tools without installing packages for the ordinary workflow. If extraction is incomplete, use another available local method or render affected pages. Do not print the entire PDF or completed note to the terminal.

Maintain a small evidence map while reading. Important facts must carry a nearby source marker such as:

~~~text
Source: Sec. 3
Source: Fig. 2
Source: Table 4
Source: Appendix A
~~~

When the local paper does not establish a value or claim, write:

~~~text
Unclear / Not explicitly stated
~~~

Do not fill missing facts from model memory or external searches.

## Paper note

Use the [AIOps paper template](../../templates/aiops-paper-note.md) as the structural basis. Never modify that template. Create or update only papers/aiops/<paper-id>/notes.md and the explicitly relevant knowledge-base files.

The note must explain the paper in its own words and answer:

- What operational problem is solved, and which task boundary does it have?
- What are the input evidence, candidate space, intermediate state, and final output?
- How does the real pipeline run, and which claimed stages are absent?
- What do the experiments actually establish?
- What remains unproven, unclear, or dependent on the paper’s assumptions?
- What is useful for the current Network AIOps research direction?

## Mandatory AIOps analysis

### Task boundary

Classify the actual scope, using multiple labels when needed:

~~~text
Detection
Anomaly Detection
Incident Detection
Localization
Root Cause Analysis
Diagnosis
Classification
Explanation
Prediction
Remediation
Recovery Verification
Incident Management
Knowledge Update
Other
~~~

Keep these distinct:

~~~text
Detection ≠ Localization ≠ RCA ≠ Diagnosis ≠ Explanation ≠ Remediation
~~~

Explain how an upstream detection or alert becomes RCA evidence, if it does. Do not claim root-cause correctness merely because an anomaly was detected or a diagnosis paragraph was generated.

### Actual pipeline

Extract only stages the paper defines or implements. When applicable, describe:

~~~text
Incident / Failure
→ Telemetry / Evidence
→ Detection
→ Candidate Generation
→ Topology / Dependency Constraint
→ Ranking / Reasoning
→ Localization
→ Diagnosis
→ Verification
→ Recommendation / Remediation
→ Recovery / Knowledge Update
~~~

State explicitly:

- What enters the system.
- What the candidate root causes are.
- How candidates are generated, pruned, ranked, or searched.
- What the final output represents.
- Which stages are assumed upstream, optional, simulated, or absent.

### Data modalities and fusion

Record all relevant modalities:

~~~text
Metrics
Logs
Traces / Spans
Alerts
Events
Topology
Configuration
Traffic
NetFlow
Packets
Tickets
Text / Documents
Knowledge Graph
SOP
Historical Incidents
Other
~~~

Mark Single-modal or Multi-modal. For multimodal work, describe the actual mechanism rather than only listing data:

~~~text
Feature fusion
Graph fusion
Prompt / context fusion
Evidence-level fusion
Tool-based retrieval
Late fusion
Other
~~~

If the paper does not use a named fusion strategy, say what is actually done. Do not impose a taxonomy that the evidence does not support.

### Candidate space

For RCA or diagnosis, identify whether candidates are services, pods, hosts, devices, interfaces, links, components, metrics, fault types, cause chains, or something else. Record:

- Candidate universe and approximate size, if stated.
- Candidate granularity and whether it matches the ground truth.
- Candidate pruning, its mechanism, and its assumptions.
- Whether the task is closed-set, open-set, single-root, or multi-root.
- Not applicable when the paper has no candidate concept.

### Topology and graph semantics

Do not write only topology-aware. Identify the structure:

~~~text
Service dependency
Call graph
Physical network topology
Logical topology
Host/service mapping
Dependency graph
Causal graph
Knowledge graph
Dynamic graph
Other
~~~

Explain whether it is used as an input feature, candidate constraint, propagation path, message-passing structure, ranking signal, search space, LLM context, verification source, or hard constraint.

Preserve:

~~~text
Dependency graph ≠ Physical Causal Graph
~~~

If causal language is used, record whether the paper demonstrates causal identification, uses a predictive/dependency graph, or leaves the semantics unclear.

### Ground truth and evaluation

Record how ground truth is obtained:

~~~text
Fault injection
Incident ticket
Repair record
Human label
Operator diagnosis
Synthetic ground truth
Benchmark annotation
Known root node
Known fault type
Other
~~~

Record its granularity: root node, service, device, interface, link, component, fault type, time interval, cause chain, or multiple roots.

For traditional evaluation, record what each metric measures:

~~~text
Precision, Recall, F1, Accuracy, Top-k, MRR, Hit Rate, Detection Delay
~~~

For an Agentic system, also check:

~~~text
Task success
Tool correctness
Number of tool calls
Steps
Latency
Token usage
API cost
Hallucination rate
Human effort
Recovery success
Safety
~~~

Do not collapse text similarity, category alignment, localization, causal correctness, remediation success, and recovery into one score.

### Production semantics and reproducibility

Distinguish:

~~~text
Production data
Production-scale evaluation
Production deployment
~~~

Record real-data status, offline or online execution, duration, incident count, device/service/node scale, and whether the system had permission to change production state. Do not turn real-world data into production deployed.

Record:

- Code, dataset, benchmark, prompt, and tool availability.
- Model/API and hyperparameter details.
- Fault-injection or environment reproducibility.
- A concise High / Medium / Low reproducibility judgment with reasons.

### LLM and Agent boundary

When a paper uses LLMs or calls a system an Agent, record both:

~~~text
Paper terminology:
Knowledge-base interpretation:
~~~

Check:

- LLM used?
- Tool use and tool types?
- Multi-step interaction?
- Observation and result integration?
- Autonomous next-action selection?
- Explicit planning or runtime replanning?
- Memory, context, or operational knowledge?
- Feedback loop?
- Environment interaction?
- Verification and human gate?

Use a cautious classification:

~~~text
LLM only
LLM + Retrieval
Tool-augmented LLM
Fixed Agentic Workflow
Agent
Multi-Agent
Unclear
~~~

Do not infer Agent from GPT use, tool use, multiple prompts, or the paper title. Do not infer Multi-Agent from role names alone; inspect distinct objectives/capabilities, communication/state handoff, and decision authority.

### Planning, orchestration, memory, and knowledge

Classify multi-step control as appropriate:

~~~text
Fixed workflow
Rule-based orchestration
DAG-constrained execution
Prompt-driven orchestration
Plan-first
Planner–Executor
Runtime replanning
Multi-Agent delegation
Other
~~~

Do not equate a DAG, role sequence, or multi-step prompt with dynamic planning.

Keep separate:

~~~text
Context
Conversation history
Working memory
Episodic memory
Persistent memory
Operational knowledge
Knowledge Base
RAG
Historical incidents
SOP
~~~

Use these boundaries:

~~~text
RAG ≠ Memory
Knowledge Base ≠ Agent Memory
Context history ≠ Long-term Memory
Persistent storage ≠ Useful Memory
~~~

For any memory or knowledge claim, record what is written, when it is written, how it is selected/retrieved, how long it persists, whether it is updated or compressed, and whether it can be invalidated or forgotten. If those policies are absent, say so.

### Verification, reliability, and remediation

Identify how a conclusion is checked:

~~~text
Telemetry re-query
Tool verification
Rule validation
Topology consistency
Independent model
Second agent
Critic
Ground-truth check
Testbed execution
Human review
No verification
~~~

An LLM repeating its own answer is not independent verification.

Check whether the paper addresses missing, conflicting, or delayed telemetry; wrong tool calls; tool failure; hallucination; wrong diagnosis; closed-set assumptions; stale knowledge; open-set or multi-root incidents; and unsafe remediation. Record retries, fallback, abstention, confidence, guardrails, and human escalation.

Separate:

~~~text
Recommendation generation
Actual remediation execution
~~~

If state changes are executed, record approval, safety validation, rollback, recovery verification, and execution feedback. Do not call a generated script or testbed action Autonomous remediation without evidence of those boundaries.

## Network AIOps relevance

Complete the template’s Relevance to My Research section for:

~~~text
Fault Detection
RCA
Fault Classification / Diagnosis
Multimodal Telemetry
Topology-aware RCA
Network Infrastructure
Metrics
Syslog
Traffic / NetFlow
LLM / Agent RCA
Production-scale evaluation
~~~

Include:

- Similarities and differences with device, interface, link, optical-module, topology, traffic, NetFlow, syslog, metrics, and configuration settings.
- Potentially useful ideas and experiments, without changing experiment code.
- Assumptions that may not transfer from microservices, cloud applications, fixed fault classes, or organizational ownership.
- Transferability to Network AIOps: High / Medium / Low, with a reason.

## Concept and knowledge-base integration

Inspect concepts/aiops/ first, then relevant generic Concepts. Update a Concept only when the paper adds knowledge that remains useful across papers or systems. Do not copy the paper abstract, benchmark table, or single-system implementation into a Concept. Keep Status: evolving for provisional knowledge.

Link only Concepts materially used by the paper. From an AIOps paper note, use links such as:

~~~markdown
[Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
[Agent](../../../concepts/agent.md)
~~~

Add a paper under a Concept’s representative papers or related sources when the connection is meaningful. Preserve the distinctions:

~~~text
LLM ≠ Agent
Dependency ≠ physical causality
RAG ≠ Memory
Recommendation ≠ remediation execution
Production data ≠ production deployment
~~~

Update, when relevant:

- notes/aiops/questions.md for AIOps questions.
- notes/questions.md only when the question also has general Agent significance.
- notes/aiops/paper-inventory.md with full-reading status and corrections to triage.
- notes/aiops/literature-map.md with the paper’s actual role and relationships.
- notes/learning-log.md with one short paper entry.
- INDEX.md with one simple paper-note link.

Do not create many empty Concepts or run a Knowledge Review as part of this single-paper task.

## Quality check

Before committing, inspect the note and changed files. Verify:

1. The note uses templates/aiops-paper-note.md without changing the template.
2. All mandatory AIOps fields are completed or explicitly marked Unknown, Unclear, or Not applicable.
3. Detection, localization, RCA, diagnosis, explanation, remediation, and recovery are not conflated.
4. Modalities, fusion, candidate space, topology semantics, and ground truth are concrete.
5. LLM/Agent terminology is separated from the knowledge-base interpretation.
6. Planning is not inferred merely from multiple steps; memory is not inferred merely from storage or context.
7. Production data, scale, deployment, recommendation, and execution claims are separated.
8. Main numbers, benchmarks, baselines, methods, conclusions, and limitations have Section/Figure/Table/Appendix grounding.
9. Research relevance and Network AIOps transferability are specific rather than generic praise.
10. Concept changes are concise, cross-paper, and linked in both directions where appropriate.
11. AIOps questions are actionable and non-duplicative; history is preserved.
12. Relative Markdown links resolve.
13. No source PDF, secret, credential, unrelated change, or incomplete note is staged.

Run from the repository root:

~~~bash
git diff --check
git status --short
git diff --stat
git diff
~~~

Also check the expected note and source layout:

~~~bash
find papers/aiops sources/papers/AIOps_papers -maxdepth 2 -type f | sort
~~~

If Source Grounding or a material knowledge boundary is unresolved, do not commit or push the incomplete task. Preserve local work and report NEEDS REVIEW.

## Git synchronization

For a complete, passing single-paper task:

1. Run git diff --check.
2. Confirm the branch is main and origin is the configured RyanQT7/agent-knowledge repository.
3. Stage only intended knowledge files; never stage sources/papers/AIOps_papers/*.pdf, secrets, credentials, or unrelated changes.
4. Run git diff --cached --check.
5. Create one non-empty, paper-specific commit, for example:

~~~text
Add ChatRCA AIOps paper analysis
~~~

6. Push normally with git push origin main.
7. Confirm git status and git branch -vv; the expected result is a clean worktree tracking origin/main.

Do not create empty commits, force-push, rewrite history, or push to an unexpected remote. If the local commit succeeds but push fails, preserve the commit and report the synchronization failure. If the task fails, source grounding is not passing, a conflict remains unresolved, authentication fails, or the user explicitly disables Git synchronization, do not push.

## User-facing completion format

Do not print the complete paper note. Report only:

~~~text
Paper:
Reading:
Source grounding:

Main task:
Modalities:
Candidate space:
Topology role:
LLM / Agent classification:
Planning:
Memory / Knowledge:
Verification:
Remediation:
Production status:
Transferability to Network AIOps:

AIOps concepts updated:
Agent concepts updated:

Research relevance:

Commit:
Push:

Git status:
~~~
