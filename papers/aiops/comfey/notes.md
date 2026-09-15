# An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure

## 1. Metadata

- Title: An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure
- Authors: Yuhan Yao, Yuxuan Jiang, Minghua Ma, Madhura Vaidya, Jieren Deng, Yigong Hu, Chetan Bansal, Ze Li, and Murali Chintalapati
- Year: 2026
- Venue: FSE Companion '26
- URL / DOI: https://doi.org/10.1145/3803437.3805228
- Local File: [Source PDF](../../../sources/papers/AIOps_papers/FSE26-An%20Agentic%20Framework%20for%20Triaging%20Incidents%20in%20Production%20Cloud%20Infrastructure.pdf)
- Paper ID: comfey

## 2. One-Sentence Summary

Comfey deploys lightweight, team-scoped agents in Azure that enrich an incident locally, decide whether to accept it, and otherwise route it using troubleshooting guides, historical precedents, and a shared statistical routing table; the production evaluation targets incident ownership and triage speed rather than complete root-cause localization.

## 3. Problem Setting

The paper addresses the difficulty of assigning a production cloud incident to the team that can investigate or mitigate it. Initial reports are often incomplete, the relevant evidence is distributed across team-owned systems, teams differ in maturity, and an incident may cross several service boundaries. A wrong initial assignment delays both diagnosis and mitigation. The motivating example is a VM-creation failure caused by stale compute knowledge about storage-node decommissioning; the compute team initially receives the signal but the storage team owns the actionable cause (Source: Sec. 1, Fig. 1).

This is primarily an **incident triage / ownership-routing** problem. It is upstream of full RCA: an agent may attach diagnostic information and mitigation suggestions after accepting an incident, but the evaluated target is whether the incident reaches the appropriate owning team, not whether a complete causal explanation is recovered (Source: Sec. 2.1, Sec. 4.5).

## 4. AIOps Task

- Detection: **No; assumed upstream.** Incidents originate from monitors or user reports (Source: Sec. 2.1, Sec. 3.3).
- RCA: **Partial / support.** The system gathers evidence and may provide diagnostic information, but triage ownership is the measured task.
- Localization: **Yes, organizational/service-team localization.** It selects or routes toward the responsible engineering team.
- Diagnosis: **Limited.** TSG and historical matching support a team decision; a fault type or causal chain is not the primary output.
- Prediction: No.
- Remediation: **Support, and conditional integration.** Comfey can redirect to an existing mitigation engine when a TSG links one; the paper does not present Comfey as an unrestricted repair agent (Source: Sec. 4.4).

## 5. Failure / Incident Setting

The setting is large-scale Azure cloud infrastructure with interacting compute, control, storage, and networking services. Incidents can involve multiple teams and can evolve as teams accept, reject, or transfer responsibility. The empirical study found that incidents commonly involve 5–30 teams, 85% of examined reports had duplicate or near-duplicate reports assigned to different teams, and 12.1% of Azure incidents in one month were initially accepted and later escalated or transferred (Source: Sec. 2.2).

Comfey is placed after ordinary team procedures: simple incidents may be handled by the initially assigned team, while complex or ambiguous cases are escalated to Comfey (Source: Sec. 4.1).

## 6. Data Modalities

- Metrics: Yes; time-series metrics can be collected by the enrichment pipeline.
- Logs: Yes; error logs and general logs are supported.
- Traces: **Unclear.** The paper explicitly mentions stack traces, which are not the same as distributed request traces.
- Alarms: Yes; monitor-generated incident signals are an input source.
- Topology: **Indirect / organizational and service-operation structure.** The paper does not define a physical network topology graph.
- Traffic: Unclear / not explicitly stated in the paper.
- NetFlow: Unclear / not explicitly stated in the paper.
- Configuration: Recent change records and resource/node health are supported; exact configuration schema is not specified.
- Tickets: Yes; incident reports and tickets are central to the workflow.
- Other: Stack traces, engineer discussion threads, troubleshooting guides (TSGs), historical incidents, and team routing history.

**Single-modal / Multi-modal:** Multi-source and operationally heterogeneous, but not presented as feature-level multimodal fusion. The local enrichment pipeline combines text reports with logs, stack traces, time-series metrics, change records, resource/node health, and discussion data (Source: Sec. 3.3–3.4).

## 7. Dataset and System Setting

- Public / Private: Private Azure operational data.
- Production / Synthetic: Real production incidents.
- Observation duration: Comfey ran from early 2024; the paper reports 22 months of production operation and historical records from March 2024 to January 2026 (Source: Abstract, Sec. 2.2, Sec. 4.1).
- Number of incidents: Approximately 19,500 newly emerged incidents triaged by Comfey; approximately 75,000 historical incidents used for matching; about 16,000 incidents had verified ground-truth labels for the accuracy evaluation (Source: Sec. 4.1, Sec. 4.5).
- Number of devices / services / nodes: The deployment spans 15 engineering teams, tens of services across compute, control, storage, and networking, and millions of hosts. The paper does not give a single candidate-node count for triage (Source: Sec. 2.2, Sec. 4.1).
- Topology: No explicit physical or service dependency graph is specified. The operational structure is represented through team ownership, incident paths, TSG routing rules, and a Global Routing Table.

## 8. Core Method

Comfey chooses a decentralized design rather than a centralized “God Agent.” Each participating engineering team runs a team-scoped agent with a common interface but local data, domain knowledge, scripts, and TSGs. The design has three durable choices:

1. Local enrichment keeps team-owned observability and data sovereignty local.
2. A shared Global Routing Table records successful historical routing paths, allowing agents to coordinate indirectly through stigmergic/statistical traces rather than a complex real-time negotiation protocol.
3. Expensive LLM-based enrichment and summarization are local, while global routing is a lightweight statistical operation (Source: Sec. 3.1–3.2).

The decision logic first checks team-authored TSG rules. If no rule matches, it retrieves similar historical incidents in two stages—TF-IDF followed by embedding cosine similarity—and asks an LLM Reasoning Service whether the precedent supports accepting the current incident. A rejection is followed by next-team selection using TSGs or the Global Routing Table (Source: Sec. 3.5–3.6, Algorithm 1).

## 9. Architecture / Workflow

The actual workflow is:

```text
Incident report / monitor signal
→ Initial team assignment
→ Team-local data enhancement
→ Context cleanup and semantic distillation
→ TSG matching
→ Historical-incident retrieval and LLM comparison (if needed)
→ Accept incident OR reject and select next team
→ Forward enriched evidence and rejection rationale
→ Repeat at the next team
→ Owning team diagnosis / mitigation
```

The multi-agent interaction can be summarized as:

```text
Incident
→ Team Agent: enrich → decide
→ Accept: diagnostic context / mitigation suggestion
→ Reject: routing table / TSG selects next team
→ Next Team Agent: reuse accumulated attachments
→ Human owning team / mitigation system
```

Each agent retains collected enrichment data, evaluation results, and rejection rationale as structured attachments, so later agents can inspect the transfer path (Source: Sec. 3.2–3.3, Fig. 4–5). This is a runtime routing loop, but it is not an explicit Planner–Executor architecture and the paper does not define an independent replanning module.

## 10. Detection Method

Detection is outside the main contribution. Monitor or user reports create the incident; Comfey is invoked for incidents that remain complex or ambiguous after standard procedures (Source: Sec. 2.1, Sec. 4.1). It therefore does not establish a new anomaly detector or evaluate detection recall.

## 11. RCA / Localization Method

Comfey localizes **responsibility** rather than directly ranking all physical or service root causes. The candidate set is the set of participating engineering teams reachable through TSG routing or the Global Routing Table. A team accepts when a relevant TSG rule or a similar previously accepted incident supports ownership; otherwise it rejects and sends the case to the next likely team (Source: Sec. 3.5–3.6).

The routing table is a frequency map from a distilled incident semantic signature to historically successful final owners and is updated from successful incident paths. It is a routing prior, not a causal graph or proof that the selected team is the physical root cause (Source: Sec. 3.6.1).

Candidate pruning is therefore operational and staged:

- TSG rules can terminate the search immediately.
- Historical retrieval narrows the precedent set through TF-IDF and embeddings.
- The Global Routing Table ranks likely next teams.
- Current-path teams are filtered to avoid cycles, with configurable visits for intentional TSG loops.
- A configurable hop limit routes unresolved cases to a human investigation queue. Section 3.6 describes a default hop limit of 10; the deployment reliability discussion describes routing after 5 consecutive rejections, so the configured value is not uniform across the paper (Source: Sec. 3.6.2–3.6.3, Sec. 4.7).

## 12. Diagnosis / Classification Method

The classification target is accept versus reject for the current team. In the paper’s evaluation, “positive” means rejecting an incident that should be rejected, while “negative” means accepting it; precision, recall, and F1 therefore describe reject-decision classification, not root-cause type classification (Source: Sec. 4.5).

The accepted incident can receive a concise anomaly/team/transfer summary and mitigation suggestions, but the paper does not define a standardized fault-type label, root-node label, or causal-chain output.

## 13. LLM / Agent Role

### Paper terminology

The paper calls Comfey a decentralized agentic triage framework and describes a set of team-scoped agents. It positions the system within multi-agent coordination, specifically contrasting statistical/stigmergic routing with negotiation-based frameworks (Source: Abstract, Sec. 3.1, Sec. 5).

### Capability analysis

- LLM Used: **Yes.** GPT-4.1 and GPT-4o-mini are used for reasoning, summarization, and enrichment; an embedding model is used for retrieval (Source: Sec. 4.9).
- Tool Use: **Yes.** Team scripts, Kusto queries, monitoring APIs/query endpoints, and custom telemetry backends are registered for local enrichment (Source: Sec. 3.3, Sec. 3.8).
- Multi-step interaction: **Yes.** An incident may traverse multiple team agents, carrying structured evidence and rejection rationales.
- Planning: **Implicit / workflow-level.** The system chooses the next team, but no independent Planner or explicit multi-step plan representation is defined.
- Memory: **Persistent operational records, not a generic Agent memory architecture.** Historical incidents, TSGs, routing statistics, and current transfer attachments are reused. The Global Routing Table is a shared blackboard-like routing memory, not an unrestricted episodic trajectory store.
- Feedback loop: **Yes.** Engineers provide ground-truth outcomes, refresh historical data, and refine TSGs/enrichment and matching pipelines (Source: Sec. 3.7).
- Environment interaction: **Limited.** Agents query production observability and incident systems; the paper’s primary action is routing, not arbitrary environment manipulation.
- Autonomous next-action selection: **Bounded.** Agent decisions select accept/reject and a next team, subject to TSG rules, statistical routing, loop prevention, hop limits, and human fallback.
- Agent classification: **Agentic workflow / decentralized multi-agent system**, with bounded team-local agents. This classification is supported by goal-directed local decisions, cross-agent transfer, shared state, and feedback, but it should not be generalized to every LLM component in Comfey.

Comfey is stronger than an LLM-only summarizer because it repeatedly makes ownership decisions and changes the incident’s route. It is also narrower than a general autonomous RCA/remediation Agent: the target is team routing, and the final mitigation remains owned by engineers or an existing mitigation engine.

## 14. Ground Truth

Ground truth is inferred from the final owning team in the operational workflow. On-call engineers are instructed to maintain queues and ensure transfers reflect actual ownership; rare incorrect inferences can be manually tagged (Source: Sec. 4.5). Thus the label is an organizational ownership label, not independently verified physical causality, fault type, or root-node truth.

## 15. Baselines

- Manual triage before deployment, using approximately 2,400 pre-Comfey incidents as a triage-time baseline (Source: Sec. 4.3).
- Manual handling for mitigation-time comparison over the same incident population (Source: Sec. 4.4).
- COMET, an automated centralized approach using an AutoExtractor, log filtering, and an LLM for keyword extraction (Source: Sec. 4.8).
- A naive random-neighbor agent negotiation mechanism in the ablation of the Global Routing Table (Source: Sec. 4.6).

## 16. Metrics

- Triage time: duration from ticket creation until transfer to the correct team.
- Mitigation time: duration from transfer to the correct mitigating team until full resolution.
- Classification metrics: accuracy, precision, recall, and F1 for accept/reject triage decisions.
- Component ablations: accuracy and triage latency changes when semantic distillation, TSG matching, or the Global Routing Table is removed.
- Operational cost: setup and per-triage token/cost estimates.

These metrics evaluate routing correctness, operational speed, mitigation outcome, and efficiency. They do not measure root-cause accuracy or causal explanation quality.

## 17. Main Results

- In production, Comfey triaged approximately 19,500 incidents over 22 months across 15 teams and tens of services, covering millions of hosts (Source: Abstract, Sec. 4.1).
- It achieved average triage speedup of 6× versus manual triage and average mitigation speedup of 4.3× in the reported comparisons (Source: Abstract, Sec. 4.3–4.4, Fig. 7–8).
- On approximately 16,000 incidents with verified ownership labels, it achieved 91.5% accuracy, 64.3% precision, 62.1% recall, and 63.1% F1 for the accept/reject formulation (Source: Sec. 4.5).
- On an ablation set of approximately 1,300 incidents, removing semantic distillation increased triage latency by 40.8% without a significant accuracy change; removing TSG matching reduced accuracy by 12.33%; replacing the Global Routing Table with naive random-neighbor negotiation reduced accuracy by 40% (Source: Sec. 4.6).
- Against COMET, the paper reports about 7.55% higher triage accuracy, 4.38× lower average triage time, and 2.91× lower average mitigation time (Source: Sec. 4.8).
- Runtime estimates are about 265,260 tokens and $3.85 to index 1,000 historical incidents, and about 5,804 tokens and $0.02 per new triage call averaged over roughly 500 calls (Source: Sec. 4.9).

The results support production usefulness for triage and routing. They do not by themselves establish that the LLM performs better causal RCA than deterministic rules, retrieval, or organizational routing structure.

## 18. Scalability / Deployment

Comfey has been deployed on Azure Kubernetes Service with automatic scaling and fault tolerance. Team-local deployment parallelizes incident processing and preserves local data sovereignty. A self-onboarding platform lets teams install the package, register existing scripts and query templates, and configure an agent with fewer than ten CLI commands; the paper reports roughly two hours of familiarization and minutes for repeated setup (Source: Sec. 3.8, Sec. 4.1–4.2).

The production scale is unusually strong for this batch, but “large-scale” here means teams, services, hosts, incident volume, and concurrent triage—not a demonstrated search over a large physical network root-cause candidate graph.

## 19. Strengths

- Uses real production incidents and an operational workflow over 22 months.
- Respects fragmented observability and team data sovereignty instead of requiring a centralized global context.
- Makes routing decisions auditable through TSG rules, historical precedents, attachments, and routing statistics.
- Uses deterministic/statistical routing for scale and reserves more expensive LLM processing for local enrichment and reasoning.
- Includes human feedback, an unresolved-case fallback, and operational latency/cost measurements.

## 20. Limitations

### Paper-supported limitations / qualifications

- Initial incident reports and cross-team data are fragmented; this is a central deployment constraint rather than a solved data-integration problem (Source: Sec. 2.2–2.3).
- Incorrect or stale TSG rules can cause sustained mis-routing; the paper accepts this auditability trade-off and relies on operational alerts and team correction (Source: Sec. 3.6.3).
- The approach assumes useful historical incidents, team-authored guides, and a meaningful notion of final team ownership.
- The measured task is triage, so the results do not establish complete RCA correctness or autonomous repair.

### Further questions from this reading

- Whether the Global Routing Table remains reliable under topology, ownership, or service-boundary changes is not evaluated as a network-specific problem.
- It is unclear how routing statistics behave when multiple teams jointly own a fault or when the physical root cause differs from the mitigating team.
- The paper gives strong operational outcomes, but does not isolate the contribution of GPT reasoning from retrieval, TSG rules, routing statistics, and existing mitigation infrastructure.

## 21. Reproducibility

- Code available: **Unclear / Not explicitly stated in the paper.** A self-onboarding platform and interfaces are described, but no public repository is identified.
- Dataset available: **No; private Azure data.**
- Benchmark available: **No public benchmark stated.**
- Prompt available: **Unclear / Not explicitly stated in the paper.**
- Model/API specified: **Partly yes.** GPT-4.1, GPT-4o-mini, and `text-embedding-ada-002` are named (Source: Sec. 4.9).
- Hyperparameters: **Partly specified.** Retrieval and routing procedures are described, but the full deployment configuration is not reproduced.
- Enough detail to reproduce: **Low for production replication; medium for the abstract workflow.** The system design is clear, but private data, team rules, internal APIs, and production routing state are unavailable.

## 22. Relationship to Existing AIOps Knowledge

Comfey adds a distinct **incident-triage layer** to the current RCA knowledge. It shows that an AIOps system may need to resolve “which team should own this case?” before attempting detailed root-cause localization. Its candidate space is organizational/service teams, not necessarily devices, metrics, or causal nodes. This reinforces the distinction between detection, triage, localization, diagnosis, explanation, and remediation in [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md).

The local enrichment plus structured handoff pattern extends [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md), but it is procedural multi-source collection rather than a learned early/feature-level fusion model. TSGs, historical incidents, and engineer feedback are examples of [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md) whose provenance and update path affect routing quality.

At the Agent level, Comfey provides a production example of a bounded decentralized multi-agent workflow: each local agent observes its permitted evidence, takes an accept/reject/transfer action, and passes an auditable state to the next team. It therefore supports the current [Agent](../../../concepts/agent.md) distinction without implying that every LLM-assisted AIOps component is a general autonomous Agent.

## 23. Relevance to My Research

### Similarities

- It targets infrastructure operations with metrics, logs, changes, node/resource health, incident reports, and team/service boundaries.
- It treats incomplete evidence, cross-domain ownership, historical cases, and time-to-mitigation as first-class operational concerns.
- Its local enrichment and structured evidence attachments are relevant to network devices, interfaces, links, and optical modules whose telemetry is often owned by different operational domains.

### Differences

- The evaluated output is responsible-team triage, not root-node RCA, fault classification, or diagnosis at device/interface/link/module granularity.
- The operational “topology” is mostly service/team routing structure; no physical network topology, traffic, NetFlow, or packet evidence is modeled explicitly.
- Ground truth is final ownership, which may differ from the physical causal origin or a multi-root fault set.

### Potentially Useful Ideas

- Domain-local evidence collectors with a stable interface and explicit provenance.
- Candidate-space reduction before expensive LLM reasoning.
- A shared, auditable routing prior learned from verified historical paths.
- Passing both evidence and rejection rationale across stages rather than resetting context.
- Human feedback and safe escalation when the system cannot establish ownership.
- Separating local expensive enrichment from global lightweight coordination.

### Assumptions That May Not Transfer

- Network RCA may not have a single owning team; a link fault can affect several services and teams.
- Team routing statistics cannot substitute for physical dependency or causal evidence.
- TSG coverage and historical recurrence may be weaker for rare optical, hardware, or open-set network faults.
- Internal Azure query APIs and permission boundaries may not match the telemetry and control interfaces available in a network environment.

### Experiments Worth Considering

- Compare a deterministic topology-based candidate router, a learned routing prior, and an LLM-assisted router under changing network ownership/topology.
- Measure whether structured evidence handoff reduces candidate search and diagnosis latency without losing provenance.
- Evaluate escalation and abstention on multi-root, unknown, and conflicting telemetry cases.
- Separate team/asset localization accuracy from physical root-cause and fault-type accuracy.

### Transferability to Network AIOps

**Medium.** The decentralized operational workflow, local data ownership, evidence provenance, candidate pruning, and human fallback transfer well. The team-ownership target, service-centric routing assumptions, and lack of physical topology/traffic reasoning limit direct transfer to network RCA.

## 24. My Understanding

Comfey is best understood as a production incident-routing system with bounded agents, not as a complete root-cause Agent. Its important design move is organizational decomposition: let each team reason over data it can actually access, then coordinate through a small shared record of successful routes. A current team does not need to know the whole cloud; it only needs to decide whether its evidence and operational knowledge justify accepting the incident or forwarding it.

The system’s “memory” is distributed across historical incidents, TSGs, routing statistics, and the current transfer attachments. These records persist across incidents, but they are operational knowledge and routing state rather than proof that the LLM has a general episodic or long-term memory. The strongest evidence in the paper is production scale and latency improvement; the weaker, unproven claim for my research is direct physical RCA correctness.

## 25. Questions

### Paper leaves unresolved

- How should a routing table be invalidated or retrained when team ownership, service dependencies, or network topology changes?
- How should responsibility be represented when an incident has multiple owners or when the mitigating team is not the physical root cause?
- What is the correct trade-off between a TSG rule treated as ground truth and a learned or LLM-generated alternative when the rule is stale?
- How much of the reported gain comes from LLM enrichment versus TSG matching, historical retrieval, routing statistics, and parallel deployment?

### Further questions for the knowledge base

- Can the team-routing candidate space be composed with a device/interface/link candidate space without conflating ownership with causality?
- What provenance and confidence signals should a downstream network RCA Agent receive after several local agents have rejected or enriched an incident?
- When does a shared routing table become useful persistent operational memory, and when does it become a stale shortcut?

## 26. Source Grounding

- Problem and production motivation: Sec. 1–2.3, Fig. 1.
- Decentralized architecture and team-scoped workflow: Sec. 3.1–3.3, Fig. 3–4.
- Semantic distillation and LLM summarization: Sec. 3.4, p. 6.
- TSG/historical decision logic: Sec. 3.5, Algorithm 1.
- Global Routing Table, candidate selection, loops, and hop-limit fallback: Sec. 3.6, Fig. 5.
- Human feedback and onboarding: Sec. 3.7–3.8.
- Production scale and integration: Sec. 4.1–4.2, Fig. 6.
- Triage and mitigation time: Sec. 4.3–4.4, Fig. 7–8.
- Ground truth and classification results: Sec. 4.5.
- Ablation and failure handling: Sec. 4.6–4.7.
- COMET comparison and multi-agent positioning: Sec. 4.8.
- Model, token, and cost estimates: Sec. 4.9.
- Conclusion and scope: Sec. 6.

## 27. Tags

`AIOps` `incident-triage` `team-routing` `production-cloud` `multi-agent` `LLM` `operational-knowledge` `human-in-the-loop` `candidate-pruning` `network-transferability`
