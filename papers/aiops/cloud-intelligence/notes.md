Status: Full Reading: Completed

# Cloud Intelligence/AIOps 2.0: Knowledge-Anchored Agentic AIOps

## 1. Metadata

- Title: Cloud Intelligence/AIOps 2.0: Knowledge-Anchored Agentic AIOps
- Authors: Dongmei Zhang, Qingwei Lin, Si Qin, Liqun Li, Lianbin Chi, Dawei Song, Biao Cheng, Chaoyun Zhang, Yingnong Dang, Samia Khalid, Saravan Rajmohan, Sitaram Lanka
- Year: 2026
- Venue: FSE Companion 2026
- URL / DOI: https://doi.org/10.1145/3803437.3806091
- Local File: [Cloud Intelligence / AIOps 2.0 PDF](<../../../sources/papers/AIOps_papers/FSE26-Cloud Intelligence_AIOps 2.0- Knowledge-Anchored Agentic AIOps.pdf>)
- Paper ID: `cloud-intelligence`

## 2. One-Sentence Summary

This position paper proposes Operational Knowledge Artifacts (OKAs)—versioned, owned, semi-structured, and anchored to operational signals—as a governed substrate for LLM/Agent-based AIOps execution, validation, escalation, and continual evolution.

## 3. Problem Setting

### Paper states

Operational knowledge is fragmented across tools, dashboards, documents, troubleshooting guides, and individual experience. Although operational systems expose logs, traces, metrics, tickets, and other signals, constructing the right context for each incident is itself a major bottleneck. The paper argues that simply placing knowledge in bespoke prompts or isolated workflows recreates this fragmentation (Source: Sec. 1, pp. 1–2).

The paper presents **Cloud Intelligence/AIOps 2.0** as a vision or conceptual framework. It does not present a standalone benchmark, a new RCA ranking algorithm, or a complete production system evaluation (Source: title/abstract; Sec. 1–2; Sec. 5).

### My interpretation

The primary contribution is to the operational-knowledge and governance layers of the Hybrid RCA architecture. It asks how knowledge can become a maintained, identifiable, executable, and auditable system artifact rather than an opaque prompt fragment. It does not by itself prove that an Agent can correctly identify a physical root cause or safely repair a network.

## 4. AIOps Task

- Detection: No standalone detector.
- Anomaly Detection: No.
- Incident Detection: **Trigger/context assumed from operational signals or control points.**
- Localization: **Not directly defined.**
- Root Cause Analysis: **A supported use case for the proposed execution layer, not an evaluated RCA method.**
- Diagnosis: **Supported as a knowledge-grounded workflow activity.**
- Classification: No standalone classification method.
- Explanation: **Yes, as one possible output of knowledge-grounded execution, with explicit uncertainty and risk boundaries (Source: Sec. 3).**
- Prediction: No.
- Remediation: **Proposed as bounded checks, mitigations, and actions, with escalation when knowledge is incomplete; no independent remediation experiment is reported (Source: Sec. 3.2, Sec. 4.1).**
- Recovery Verification: **Proposed as part of validation/evolution, not operationally evaluated.**
- Incident Management: **Yes, used as the main illustrative setting.**
- Knowledge Update: **Yes.** Knowledge curation and continued evolution are first-class loops.

The paper therefore defines an architecture for organizing operational decisions rather than an end-to-end task benchmark. Detection, candidate generation, physical RCA, and repair correctness remain outside its direct empirical scope.

## 5. Failure / Incident Setting

The paper discusses recurring operational situations in cloud services, including incident management, release/change operations, and capacity/efficiency operations. It uses existing Troubleshooting Guides (TSGs) and incident-management practice as an illustrative instance of the proposed OKA lifecycle (Source: Sec. 3.1 and Sec. 4.2).

The paper does not provide a fixed incident corpus, a fault-injection protocol, a root-cause annotation scheme, or a network-failure testbed. The StepFly material is presented as an illustrative manifestation of the vision, not as a replacement for direct evaluation of the Cloud Intelligence proposal (Source: Sec. 3.1).

## 6. Data Modalities

- Metrics: **Yes, named as operational signals/examples.**
- Logs: **Yes.**
- Traces / Spans: **Yes, named as available operational data.**
- Alerts: **Yes, as a natural anchoring surface for OKAs.**
- Events: **Yes, in the operational-signal context.**
- Topology: **Partly.** Service hierarchy, dependencies, monitors, pipelines, rollout stages, and quality gates are discussed as operational touchpoints; no formal topology-aware RCA model is defined.
- Configuration: **Partly.** Control points, scope, preconditions, and safe actions are part of the OKA contract, but a telemetry/configuration fusion algorithm is not given.
- Traffic: Unclear / Not explicitly stated.
- NetFlow: No.
- Packets: No.
- Tickets: **Yes, as examples of fragmented operational knowledge and incident history.**
- Text / Documents: **Yes.** TSGs, documents, prior incidents, and expert input are central knowledge sources.
- Knowledge Graph: No explicit knowledge graph requirement.
- SOP: **Yes, in the broader sense of troubleshooting guides and operational procedures.**
- Historical Incidents: **Yes, as a source for knowledge curation and feedback.**
- Other: Operational control points, monitor identities, rollout stages, quality gates, and human expertise.

**Multi-source operational context.** The paper does not specify early/feature-level/late fusion. It organizes heterogeneous signals and documents by attaching a relevant knowledge artifact to a stable operational touchpoint, then retrieving the artifact when that context is activated (Source: Sec. 2.2–2.3).

## 7. Dataset and System Setting

- Public / Private: **Not applicable for a standalone evaluated dataset.**
- Production / Synthetic: **Operational motivation and examples; standalone empirical setting is not specified.**
- Observation duration: Not applicable / not specified.
- Number of incidents: Not applicable / not specified for the proposal.
- Number of devices / services / nodes: Not specified.
- Topology: Service hierarchy and operational dependencies are discussed conceptually; physical network topology is not modeled.
- Production dataset: **Unclear for Cloud Intelligence itself.**
- Production-scale evaluation: **Not established.**
- Production deployment: **Not established for the proposed framework.**
- StepFly example: The paper describes StepFly as an illustrative deployed manifestation and reports its operational usage and mitigation improvement in that example. Those claims belong to StepFly, not to an independent Cloud Intelligence experiment (Source: Sec. 3.1).

## 8. Core Method

The paper introduces **Operational Knowledge Artifacts (OKAs)** as the unit of operational knowledge. An OKA is intended to be:

- versioned and owned;
- scoped to a concrete operational situation;
- expressed in semi-structured natural language so humans can maintain it and Agents can interpret it;
- rich enough to contain diagnostic steps, decision points, safe actions, and escalation guidance; and
- attached to a stable operational signal or control point (Source: Sec. 2.1–2.2).

The minimum contract includes stable identity and ownership, scope and preconditions, evidence and decision points, bounded/auditable actions with safety constraints, and lifecycle metadata such as version, validation status, and drift signals (Source: Sec. 2.3).

The architecture has three coupled loops:

1. **Knowledge curation:** synthesize knowledge from prior incidents, logs, documents, and expert input; refactor it into an agent-readable artifact and anchor it.
2. **Knowledge-grounded execution:** retrieve the anchored OKA and drive tool-using checks, evidence gathering, mitigations, and explanations with uncertainty/risk boundaries.
3. **Continued evolution:** use execution feedback—what worked, was missing, unsafe, or obsolete—to update the OKA and its anchor (Source: Sec. 3).

When an OKA is incomplete, the Agent should expose the gap, propose risk-annotated next steps, and escalate rather than executing unspecified actions (Source: Sec. 3).

## 9. Architecture / Workflow

The proposed lifecycle can be represented as:

```text
Operational signals / control points
→ retrieve anchored OKA
→ inspect scope and preconditions
→ collect evidence through bounded tools
→ reach decision points
→ explain, recommend, or apply bounded action
→ validate outcome and record feedback
→ update, version, or retire the OKA/anchor
```

The paper’s illustrative incident-management workflow treats a TSG as an OKA: learn/curate → execute → validate → evolve/share. StepFly is used to show how a TSG can be transformed into an executable DAG and run with a scheduler-executor, but this is an example of the vision rather than a Cloud Intelligence experiment (Source: Sec. 3.1).

`Evidence` is not only raw telemetry. It is one explicit part of an OKA’s decision contract and execution trace. `Knowledge` supplies procedures, preconditions, and action boundaries; it should not be silently treated as current telemetry or as proof that a root cause is true.

## 10. Detection Method

No detection method is proposed or evaluated. Monitors and alerts are described as anchoring surfaces that activate the appropriate OKA. The paper does not specify anomaly thresholds, detector training, detection delay, or how alert quality is measured.

## 11. RCA / Localization Method

The paper does not define a candidate root-cause universe, a candidate-pruning algorithm, a topology-constrained ranking algorithm, or an RCA metric. In the proposed execution loop, an OKA can provide checks and decision points that help an Agent investigate an incident, but the framework does not establish whether the final explanation identifies the physical initiating cause.

**Candidate space:** Not applicable as an implemented RCA candidate space. The OKA’s scope and decision points constrain an operational procedure, but they are not equivalent to enumerating devices, interfaces, links, fault types, or causal paths. Open-set and multi-root behavior are not specified.

## 12. Diagnosis / Classification Method

Diagnosis is treated as one operational decision activity inside a knowledge-grounded workflow. The paper does not report a diagnosis label schema, root-node ground truth, fault-type classifier, Top-k metric, or independent causal validation. It requires explicit uncertainty and escalation when the knowledge artifact does not cover the situation (Source: Sec. 3).

## 13. LLM / Agent Role

- LLM used: **Yes, as the proposed interpretation/execution layer for semi-structured OKAs.**
- Tool use: **Yes, proposed.** Agents may run checks, gather evidence, apply mitigations, and produce explanations (Source: Sec. 3).
- Multi-step interaction: **Yes, in the proposed knowledge-grounded workflow.**
- Observation: **Implied through evidence gathered from tools and operational signals.**
- Autonomous next-action selection: **Bounded by OKA scope, preconditions, decision points, and safety constraints.**
- Planning: **Proposed interpretation of OKAs, not a separately evaluated Planner.**
- Replanning: Unclear / Not explicitly specified.
- Memory: **Not Agent memory by default.** Versioned OKAs and execution feedback are operational knowledge artifacts with ownership and lifecycle governance.
- Feedback loop: **Yes, through continued evolution of OKAs based on execution outcomes.**
- Environment interaction: **Proposed; concrete implementation depends on the illustrative system.**
- Verification: **Proposed through validation status, regression/drift checks, and operational feedback; no common verification experiment is reported.**
- Human gate: **Yes, proposed for incomplete knowledge and high-risk actions.**

**Paper terminology:** Knowledge-Anchored Agentic AIOps and AIOps 2.0.

**Knowledge-base interpretation:** This is a proposed knowledge-anchored agentic architecture. It is more than a one-shot LLM summary because it specifies activation, bounded tool-using execution, escalation, and artifact evolution; however, the paper does not empirically establish a production Agent or a physical RCA capability.

## 14. Ground Truth

No standalone ground-truth protocol is provided. The proposal discusses validation status, execution outcomes, drift signals, and incident feedback as governance inputs, but does not define how a root node, fault type, causal chain, or remediation success would be annotated.

Ground truth for the illustrative StepFly results belongs to StepFly’s own evaluation and is not specified as a Cloud Intelligence benchmark (Source: Sec. 3.1).

## 15. Baselines

No standalone baselines are reported. The paper is a position/framework paper and compares the OKA framing conceptually with fragmented documents, private prompts, and unstructured workflows (Source: Sec. 1–2).

## 16. Metrics

No empirical metrics are reported for Cloud Intelligence itself. The paper suggests that future evaluation should measure coverage of validated anchored OKAs, maintainability under drift, auditability, reproducibility, and learning over time (Source: Sec. 4.3). These are evaluation directions, not results.

The StepFly example includes operational outcomes, but they should not be attributed to a separate Cloud Intelligence implementation (Source: Sec. 3.1).

## 17. Main Results

The supported contribution is conceptual: operational knowledge should be a first-class, anchored, governed artifact that can be curated, executed, validated, and evolved. The paper does not prove an accuracy improvement, RCA improvement, remediation success rate, or production-scale result for AIOps 2.0 itself (Source: Abstract; Sec. 2–5).

Its strongest concrete design implications are:

- a stable identity and anchor are needed to connect a procedure to an operational context;
- action scope, preconditions, safety boundaries, and ownership should be explicit;
- incomplete knowledge should trigger escalation rather than unconstrained action; and
- execution feedback should update the artifact and expose drift.

## 18. Scalability / Deployment

- Conceptual scalability goal: **Yes.** The paper is concerned with avoiding team-local fragmentation and enabling system-level reuse.
- Production dataset: **Unclear for the proposed framework.**
- Production-scale evaluation: **Not reported.**
- Production deployment: **Not reported for Cloud Intelligence itself.**
- StepFly deployment example: **Reported as an illustrative manifestation**, not as a direct validation of the full proposal (Source: Sec. 3.1).

The proposal recognizes ownership, drift, consistency, regression tests, approval gates, and provenance as prerequisites for scale (Source: Sec. 4.1–4.3), but these remain an agenda rather than a demonstrated network deployment.

## 19. Strengths

- Defines an operational knowledge unit with identity, ownership, scope, preconditions, evidence, actions, and lifecycle metadata.
- Places knowledge anchoring at monitors and control points rather than leaving it in an untraceable per-alert prompt.
- Connects curation, execution, validation, and evolution into one lifecycle.
- Makes uncertainty, escalation, safety boundaries, drift, and provenance part of the architecture.
- Offers a useful bridge between human-maintained procedures and bounded Agent/tool execution.

## 20. Limitations

### Paper-backed limitations / boundaries

- The paper is a short position/framework paper and does not provide a standalone benchmark or end-to-end empirical validation (Source: Sec. 1–5).
- It does not specify a network telemetry schema, candidate root-cause protocol, topology algorithm, or open-set/multi-root evaluation.
- The proposed governance and lifecycle mechanisms are described as future engineering/research needs rather than measured capabilities.

### Current interpretation

- An OKA is operational knowledge, not automatically a memory record, a RAG index, or proof of a diagnosis.
- Anchoring an artifact to an alert or monitor provides context identity, but does not guarantee that the current evidence matches the artifact’s assumptions.
- A bounded action contract can reduce risk, but it does not replace independent telemetry verification, rollback, recovery observation, or human approval for high-impact network changes.

## 21. Reproducibility

- Code available: No standalone implementation specified.
- Dataset available: No standalone dataset.
- Benchmark available: No.
- Prompt available: No complete prompt set.
- Tools described: **Conceptually.**
- Model/API specified: No.
- Hyperparameters: Not applicable.
- Fault injection available: No standalone protocol.
- Reproducibility: **Low for empirical results.** The OKA contract and lifecycle are described, but no complete implementation, dataset, prompt/tool package, or independent Cloud Intelligence evaluation is provided.

## 22. Relationship to Existing AIOps Knowledge

This paper extends [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md) from a collection of TSGs, SOPs, and cases into a governed artifact model with stable anchors and lifecycle metadata. It complements [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md): an anchor/version/owner can identify which knowledge artifact guided an action, but it does not replace source/entity/time provenance for telemetry.

It also connects to [Agentic Incident Management](../../../concepts/aiops/agentic-incident-management.md) and [Production Evaluation](../../../concepts/aiops/production-evaluation.md). The proposed loop has the right architectural boundaries—bounded tools, uncertainty, escalation, validation, and knowledge evolution—but the paper does not provide the production evidence needed to confirm those boundaries work at network scale.

Related concepts:

- [Operational Knowledge](../../../concepts/aiops/operational-knowledge.md)
- [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md)
- [Agentic Incident Management](../../../concepts/aiops/agentic-incident-management.md)
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md)
- [Agent](../../../concepts/agent.md)
- [Tool Use](../../../concepts/tool-use.md)
- [Planning](../../../concepts/planning.md)
- [Memory](../../../concepts/memory.md)

## 23. Relevance to My Research

### Similarities

The proposal directly addresses evidence context, operational knowledge, tool-grounded investigation, safe actions, human escalation, and lifecycle governance—all relevant to a Network AIOps RCA architecture.

### Differences

The paper is cloud/service-oriented and conceptual. It does not define physical network entities, syslog/traffic/NetFlow alignment, link/interface candidate spaces, or validated remediation outcomes.

### Potentially Useful Ideas

- Treat a network troubleshooting procedure as a versioned, owned artifact anchored to a device/interface/link alert or control point.
- Require scope, preconditions, evidence fields, permissions, blast radius, approval status, and validation status before a procedure can guide action.
- Record which OKA version, evidence, and tool calls were used for each investigation.
- Make out-of-coverage and stale-knowledge states explicit, with risk-annotated escalation.

### Assumptions That May Not Transfer

- Monitor/service anchors may not uniquely identify a physical network fault or a changing path.
- Semi-structured natural language may be insufficient for precise network configuration safety unless coupled with typed schemas and deterministic validators.
- The framework assumes organizational ownership and maintenance processes that may be difficult to establish for rapidly changing telemetry and topology.

### Experiments Worth Considering

- Compare unanchored runbook retrieval with versioned, alert/entity-anchored network OKAs on evidence selection and action safety.
- Measure stale-OKA detection after topology, configuration, or firmware changes.
- Evaluate whether explicit preconditions and provenance reduce unsupported LLM tool calls.
- Separate OKA quality, RCA correctness, recommendation quality, execution success, and recovery verification in a network testbed.

### Transferability to Network AIOps

**Medium.** The artifact, anchor, lifecycle, escalation, and governance abstractions transfer well; the paper does not validate the telemetry schema, physical topology semantics, or safety mechanisms required for network operations.

## 24. My Understanding

Cloud Intelligence/AIOps 2.0 contributes a way to think about operational knowledge as part of the system control plane. A useful procedure should have an identity, owner, scope, evidence requirements, safe action boundaries, validation status, and a way to evolve when the system changes. The Agent is an execution and learning layer around that artifact, not the sole source of operational truth.

For the current Hybrid RCA architecture, the most useful addition is a knowledge-governance boundary between evidence and action. An LLM may interpret a versioned OKA and choose among bounded checks, but current telemetry provenance, candidate constraints, independent verification, and human-gated remediation remain separate requirements.

## 25. Questions

- How should a network OKA anchor to a physical entity when alerts map to a path, interface, or shared device rather than one service?
- How can an OKA’s evidence preconditions be checked against delayed, missing, or contradictory telemetry?
- What regression tests are sufficient to detect that an OKA is stale after a topology, configuration, or firmware change?
- How should OKA version, evidence provenance, permission scope, and human approval be recorded in a remediation audit trail?

## 26. Source Grounding

- Position/vision and operational-knowledge fragmentation: title/abstract and Sec. 1, pp. 1–2.
- OKA definition and representation: Sec. 2.1, p. 2.
- Anchoring to monitors, alerts, pipelines, rollouts, and control points: Sec. 2.2, p. 2.
- OKA contract—identity, scope, evidence, bounded actions, lifecycle metadata: Sec. 2.3, p. 2.
- Curation, knowledge-grounded execution, continued evolution, and escalation on incomplete knowledge: Sec. 3, pp. 2–3.
- StepFly as illustrative manifestation and its lifecycle: Sec. 3.1, p. 3.
- Drift, governance, approval, blast radius, auditability, and provenance agenda: Sec. 4.1–4.3, pp. 3–4.
- Conceptual conclusion and lack of standalone empirical validation: Sec. 5, p. 4.

## 27. Tags

`AIOps` `Cloud-Intelligence` `AIOps-2.0` `operational-knowledge` `OKA` `agentic-workflow` `governance` `provenance` `tool-use` `human-gate` `Network-AIOps`
