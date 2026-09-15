# AIOps Knowledge Review v3

Status: Completed for the stated scope; conclusions remain evolving

## Scope

**Focus:** Evidence-grounded, candidate-constrained, verifiable RCA for operational and agentic systems.

This review consolidates:

- [Cloud-OpsBench](../../../papers/aiops/cloud-opsbench/notes.md)
- [Cloud Intelligence/AIOps 2.0](../../../papers/aiops/cloud-intelligence/notes.md)
- [CHIEF](../../../papers/aiops/chief/notes.md)
- [FlowFixer](../../../papers/aiops/flowfixer/notes.md)

[AIOps Knowledge Review v1](aiops-knowledge-review-v1.md), [AIOps Knowledge Review v2](aiops-knowledge-review-v2.md), and [Network AIOps Architecture Synthesis v1](network-aiops-architecture-synthesis-v1.md) provide background. This document does not re-read or re-summarize the earlier batches; it uses them where they clarify the current architecture.

## Evidence Convention

- **Paper-backed fact:** reported or explicitly qualified in a paper note, with a section, table, figure, or appendix marker.
- **Cross-paper synthesis:** a comparison or abstraction derived from multiple paper notes.
- **Current interpretation / research hypothesis:** a working design for Network AIOps that the current papers do not yet prove.

The four papers do not constitute one unified system. Cloud-OpsBench is an evaluation paradigm, Cloud Intelligence is a position/framework paper, CHIEF is offline Agent-trace attribution, and FlowFixer is agentic-workflow repair. Their value for Network AIOps is therefore architectural and methodological, not evidence that a complete network RCA system already exists.

## 1. What the Four Papers Add

### Paper-backed facts

- **Cloud-OpsBench** freezes historical telemetry, control-plane configuration, and instantaneous data-plane state, then exposes read-only standard commands through deterministic mocked interfaces. It proposes process-centric measures for trajectory adherence, tool relevance/coverage, invalid actions, redundancy, and zero-tool diagnosis; it does not report a completed production or remediation evaluation (Source: [Cloud-OpsBench note](../../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.1–2.4, Sec. 3–4).
- **Cloud Intelligence/AIOps 2.0** proposes Operational Knowledge Artifacts (OKAs) with identity, ownership, scope, preconditions, evidence/decision points, bounded actions, safety constraints, versioning, validation status, and drift signals. It presents curation, knowledge-grounded execution, and continued evolution as coupled loops, but is a position/framework paper without standalone empirical RCA results (Source: [Cloud Intelligence note](../../../papers/aiops/cloud-intelligence/notes.md), Sec. 2–5).
- **CHIEF** represents failed multi-agent trajectories as a hierarchical graph over subtasks, Agents, and steps; virtual oracles provide goals, preconditions, key evidence, and acceptance criteria; hierarchical backtracking narrows the candidate from subtask to Agent to step; counterfactual attribution identifies the earliest decisive Agent-step error. Its Who&When benchmark contains 184 failure logs and focuses on one decisive root (Source: [CHIEF note](../../../papers/aiops/chief/notes.md), Sec. 3–5, Sec. 7).
- **FlowFixer** normalizes failed agentic workflows into symbolic traces, infers behavioral assertions, attributes a responsible workflow node and failure category, generates atomic patches, performs pre-execution checks, and dynamically re-executes the workflow. It reports 71.3% repair success, 84.4% failure-attribution accuracy, and 87.9% root-cause classification accuracy on its workflow benchmark; these are not network recovery metrics (Source: [FlowFixer note](../../../papers/aiops/flowfixer/notes.md), Sec. III–IV, Table II).

### Cross-paper synthesis

The new evidence strengthens four boundaries in the current Hybrid RCA architecture:

1. **Evidence must be identifiable and replayable.** A snapshot, an OKA anchor/version, an Agent trace, and a symbolic workflow record each preserve a different kind of identity or provenance.
2. **Candidate space must be explicit.** CHIEF makes an Agent-step candidate and its hierarchy explicit; FlowFixer makes a workflow-node/category output explicit. Cloud-OpsBench and Cloud Intelligence show what happens when the benchmark or knowledge artifact is the focus rather than a candidate-RCA algorithm: candidate semantics remain unspecified.
3. **Verification is layered.** Process compliance, graph/oracle consistency, symbolic patch checks, dynamic test execution, fresh telemetry, and recovery are different checks with different targets.
4. **Repair and recovery are separate claims.** FlowFixer validates a workflow patch in a controlled test input; Cloud Intelligence proposes bounded actions and governance; neither establishes safe, reversible, human-gated recovery of a physical network.

## 2. What Is Auditable RCA Evidence?

### Working definition

For the current knowledge base, **auditable RCA evidence** is an observation or derived fact that can be traced to its source, entity, time, transformation, and use in a candidate or diagnosis. It must be possible for a verifier or operator to determine what was observed, where it came from, whether it is fresh and applicable, and why it supports or contradicts a candidate.

### Minimum Evidence Provenance model

An evidence record for Network AIOps should contain, at minimum:

```text
source
modality
tool / query / operation
entity and entity level
time interval and clock basis
observation or derived value
transformation / aggregation
freshness and collection status
confidence / uncertainty
missingness or conflict state
related candidate(s) and causal role
knowledge / topology / configuration version when relevant
```

This is a **cross-paper synthesis and design hypothesis**, maintained in [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md), not a schema jointly specified by these papers.

### What each paper contributes

- Cloud-OpsBench gives a reproducible state/query boundary: the snapshot records telemetry, control-plane state, data-plane state, and deterministic command responses. It improves replayability but does not guarantee physical entity mapping or causal truth (Source: [Cloud-OpsBench note](../../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.2–2.4).
- Cloud Intelligence gives knowledge-side identity: an OKA has owner, version, validation status, drift signals, and an operational anchor. This identifies which procedure guided a decision, not whether a telemetry observation is true (Source: [Cloud Intelligence note](../../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.1–2.3).
- CHIEF gives execution-trace provenance: OTAR fields, subtask/Agent/step edges, oracle expectations, and data-flow relations make recorded Agent observations auditable. Its graph and oracle are themselves LLM-assisted and can be wrong (Source: [CHIEF note](../../../papers/aiops/chief/notes.md), Sec. 4.1–4.3, Sec. 7).
- FlowFixer gives workflow-trace provenance: node identity/type, input/output, status, configuration, parameters, and symbolic assertions connect an observed failure to a patch decision. It does not define network entity/time alignment (Source: [FlowFixer note](../../../papers/aiops/flowfixer/notes.md), Sec. III-A–III-B).

### Multimodal alignment point

The current evidence supports placing entity and time alignment **after modality-specific collection and before candidate generation or LLM reasoning**, while retaining links to raw observations and the transformations used. A second candidate-specific association can occur after candidate construction. This is a **current architecture hypothesis**: none of the four papers specifies a complete network alignment protocol over metrics, syslog, traffic/NetFlow, configuration, and physical topology.

Putting raw telemetry directly into a prompt would lose source identity, make conflicts hard to represent, and make independent re-query difficult. A structured Evidence Ticket can provide bounded context without replacing the underlying records.

## 3. Candidate Space for RCA

### Current cross-paper view

| Paper | Candidate unit | Constraint / reduction | Root and evaluation boundary |
| --- | --- | --- | --- |
| Cloud-OpsBench | Not explicitly defined; expert diagnostic trajectory is the process reference | Tool/process trajectory measures | No numeric candidate universe or network root schema is established |
| Cloud Intelligence | Not defined as an RCA candidate set; OKA scope and decision points constrain a procedure | Preconditions, evidence points, bounded actions | No root-label, open-set, or multi-root protocol |
| CHIEF | Agent-step pair, reached through subtask → Agent → step hierarchy | Virtual-oracle matching, reverse-topological backtracking, counterfactual attribution | One earliest decisive root; Agent and exact-step labels |
| FlowFixer | Workflow node + finite failure category | Symbolic assertions, propagation influence, scoped repair | Responsible-node/category labels; open-set and multi-root not established |

The table is a synthesis. It shows that “candidate” is not a universal object: it may be an infrastructure component, anomaly node, SOP leaf, Agent step, workflow node, or fault category depending on the paper (also see [Candidate Space](../../../concepts/aiops/candidate-space.md)).

### Network candidate model

**Research hypothesis:** a Network RCA candidate space should support several linked levels instead of forcing every incident into one flat label:

```text
device / chassis / card
→ interface / port / optical module
→ link / segment
→ path / service dependency
→ fault type or mechanism
→ unknown / multiple-root set
```

The exact hierarchy depends on the inventory and incident. A candidate record should include entity level, time interval, causal role, fault type, and evidence references. Initiating cause, affected component, downstream symptom, propagation intermediary, and unknown candidate should remain distinguishable.

### Candidate pruning

A cautious Network RCA sequence is:

```text
versioned entity universe
→ incident/time scope
→ evidence-to-entity mapping
→ physical/topological admissibility
→ hierarchy and dependency pruning
→ bounded candidate ranking
→ independent verification
```

CHIEF supports the general coarse-to-fine idea, but its hierarchy is an Agent execution hierarchy. FlowFixer supports node-scoped attribution, but its workflow graph is not a physical graph. Therefore, the network version remains a transfer hypothesis.

### Why candidate definition affects evaluation

Evaluation can be misleading when prediction and ground truth have different granularities. For example, a predicted interface and a device-level ground truth need an explicit mapping rule; otherwise a Top-k score can hide whether the system found the initiating entity or merely a related component. The evaluation contract should state:

- candidate universe and version;
- output granularity;
- root versus symptom semantics;
- single-root, multi-root, or unknown policy;
- time point versus time interval;
- mapping rules across hierarchy levels; and
- whether pruning excluded the true root.

## 4. Topology, Hierarchy, and Causality

### Distinct roles

- **Physical topology:** devices, interfaces, links, modules, reachability, and physical adjacency. A Network AIOps design may use it as an admissibility constraint, candidate generator, path context, or recovery consistency check.
- **Fault hierarchy:** a taxonomy or coarse-to-fine label organization such as device fault → interface fault → optical fault. It can reduce classification or attribution scope, but is not a graph of runtime propagation.
- **Dynamic dependency:** time-varying predictive or operational relations inferred from traffic, metrics, service behavior, or state. It can provide a soft ranking prior or propagation hypothesis.
- **Execution/dependency graph:** CHIEF’s HCG and FlowFixer’s workflow graph organize Agent/workflow behavior. They are not physical topology.
- **Causal graph:** a graph whose causal semantics depend on how it is identified and verified. CHIEF’s counterfactual trace attribution is not the same as physical intervention on a network.

### Physical topology plus dynamic dependency

**Research hypothesis:** use physical topology to define which candidates and paths are admissible, and use dynamic dependency/traffic evidence as time-dependent soft evidence. Keep edge type, version, timestamp, confidence, and provenance separate. A learned or predictive edge can raise a candidate’s rank without being declared a physical causal edge.

This formulation is more precise than calling every graph “topology-aware,” but it has not yet been validated on network data in the current knowledge base.

## 5. What Is Being Verified?

Verification should be decomposed by target:

| Target | Example acceptance question | Suitable evidence / verifier |
| --- | --- | --- |
| Evidence | Is this observation fresh, correctly mapped, and retrieved from the claimed source? | Schema/identity checks, timestamp checks, source re-query, conflict detection |
| Candidate | Is this entity eligible and consistent with topology, time, and evidence? | Deterministic inventory/topology rules, entity mapping, independent graph check |
| Root cause / diagnosis | Does the candidate explain the observations better than alternatives? | Fresh telemetry, cross-modal corroboration, independent algorithm, human adjudication |
| Tool result | Did the requested operation execute correctly and return the intended scope? | Tool schema/result validation, permission/error handling, repeat query |
| Repair proposal | Is the action structurally, semantically, and operationally safe before execution? | Policy/rule checks, configuration simulation, blast-radius and permission checks |
| Execution outcome | Did the intended action actually occur? | Tool acknowledgement plus observed system state |
| Recovery | Has the incident condition improved without introducing a new failure? | Fresh independent telemetry, topology/health checks, service/SLO signals, rollback criteria |

### Paper-backed verification patterns

- Cloud-OpsBench verifies diagnostic process behavior: tool relevance/coverage, invalid actions, redundant actions, and zero-tool diagnosis. It does not independently verify a physical root or recovery (Source: [Cloud-OpsBench note](../../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.4).
- Cloud Intelligence proposes OKA validation status, drift signals, consistency checks, regression tests, bounded actions, and escalation. These are governance requirements and agenda items, not a measured verification protocol (Source: [Cloud Intelligence note](../../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.3, Sec. 4.1–4.3).
- CHIEF uses graph/oracle consistency, hierarchical backtracking, and counterfactual attribution to verify responsibility within an Agent trajectory. This does not verify physical operational state (Source: [CHIEF note](../../../papers/aiops/chief/notes.md), Sec. 4.1–4.3).
- FlowFixer performs structural, semantic, behavioral, and offset checks before execution, then dynamically re-executes a repaired workflow and retries if needed. This validates a workflow patch on test inputs, not live network recovery (Source: [FlowFixer note](../../../papers/aiops/flowfixer/notes.md), Sec. III-D–III-E; Sec. VII-A).

### Verification strength

The following is a **working synthesis**, not a standard:

```text
LLM self-check
< independent critic/model
< deterministic consistency check
< fresh tool / telemetry re-query
< controlled execution with observed outcome
< post-action recovery signal + appropriate human gate
```

The ordering is not universally strict. It expresses increasing independence and operational relevance for a given claim. A low-risk explanation may need less than a configuration change; a high-impact action should not be accepted because the same LLM restated its own conclusion.

## 6. Repair, Remediation, and Recovery

The current working distinction is:

```text
recommendation
≠ repair proposal
≠ action execution
≠ recovery verification
```

FlowFixer’s RSR measures whether a repaired workflow passes dynamic verification on test inputs. That is stronger than generating a plausible patch, but weaker than demonstrating safe live remediation. Cloud Intelligence adds the concepts of bounded/auditable action, preconditions, approval, blast radius, ownership, and escalation, but does not test them as a complete system. Neither paper reports rollback or an independent post-action network recovery signal (Sources: [FlowFixer note](../../../papers/aiops/flowfixer/notes.md), Sec. III-D–III-E, Sec. VIII; [Cloud Intelligence note](../../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.3, Sec. 4.1).

A cautious Network remediation lifecycle is:

```text
verified diagnosis
→ proposed typed action
→ permission / precondition / blast-radius checks
→ human approval for high-impact or uncertain actions
→ controlled execution
→ fresh telemetry and topology observation
→ recovery verification
→ rollback, escalation, or knowledge update
```

This is a design hypothesis. The current papers support its separate boundaries, not the full live implementation.

## 7. Benchmark and Evaluation Implications

### What counts as success?

The success unit must be declared before comparing systems:

```text
correct evidence
correct candidate
correct root / fault type
successful investigation
correct tool use
safe repair proposal
successful execution
recovered system
human acceptance
```

Cloud-OpsBench contributes process metrics; CHIEF contributes Agent-level versus exact-step attribution; FlowFixer separates repair success, node attribution, and category classification; Cloud Intelligence calls for coverage, maintainability, auditability, and learning-over-time measures. These units cannot be collapsed into one “Agent success” score (Sources: the four formal notes, Sec. 16–17).

### Minimum benchmark dimensions for Network Agentic RCA

1. **RCA correctness:** root entity, fault type, root multiplicity, granularity, and uncertainty.
2. **Evidence grounding:** source/entity/time/provenance coverage, conflict handling, and re-query consistency.
3. **Candidate behavior:** candidate recall before pruning, pruning recall loss, ranking quality, unknown/multi-root handling.
4. **Tool behavior:** valid calls, scope correctness, relevance, coverage, retries, and failed-tool handling.
5. **Process behavior:** required investigative steps, redundant calls, latency, steps, tokens, and cost.
6. **Action safety:** permission checks, policy violations, blast radius, human interventions, rollback, and wrong-remediation cost.
7. **Recovery:** independent post-action signal, time to recovery, regressions, and recovery success.

No current Batch 3 paper covers this complete protocol. This is a central remaining evaluation gap.

## 8. Updated Hybrid RCA Mental Model

The following is a **cross-paper synthesis / current design hypothesis**, not a standard architecture from any one paper:

```text
Incident / Failure
        ↓
Telemetry and operational-state collection
        ↓
Evidence normalization, entity/time alignment, provenance
        ↓
Detection / incident formation
        ↓
Versioned candidate universe and ground-truth contract
        ↓
Physical-topology and hierarchy-constrained pruning
        ↓
Bounded LLM/Agent evidence investigation
        ↓
Candidate / diagnosis verification
        ↓
Explanation and confidence / abstention
        ↓
Human gate for uncertain or high-impact action
        ↓
Typed remediation proposal and safety validation
        ↓
Controlled execution
        ↓
Independent recovery verification
        ↓
Versioned knowledge / evidence / outcome update
```

### Division of labor

- **Deterministic/statistical/ML:** telemetry normalization, time alignment, anomaly/detection signals, entity mapping, candidate enumeration, schema validation, inventory checks, policy checks, and recovery signals.
- **Graph/topology algorithms:** physical admissibility, path/dependency constraints, candidate pruning, propagation priors, and consistency checks.
- **LLM:** bounded interpretation of heterogeneous evidence, comparison of a defined candidate set, hypothesis articulation, selection among well-defined read-only tools, and operator-readable explanation.
- **Agent:** only where the incident requires observation-dependent multi-step investigation, additional evidence requests, hypothesis testing, bounded replanning, escalation, or verification. A one-shot normalized-evidence classifier does not require an Agent loop merely because it uses an LLM.
- **Human:** adjudication under conflicting or incomplete evidence, open-set/low-confidence diagnosis, high-blast-radius changes, rollback decisions, and publication of consequential knowledge updates.

### Confirmed / strengthened

- Process-level evaluation is a real dimension in addition to final answer quality (Cloud-OpsBench).
- Knowledge identity, ownership, versioning, anchors, and bounded actions are useful governance primitives (Cloud Intelligence).
- Candidate hierarchy and coarse-to-fine attribution can reduce a large structured search (CHIEF, with domain caveats).
- Verification should be layered and target-specific; dynamic execution is stronger than plausibility alone but does not equal recovery (FlowFixer).
- Recommendation, execution, and recovery must remain separate claims.

### Modified

- “Topology-constrained candidate space” now includes an explicit candidate contract: entity granularity, hierarchy, root semantics, unknown/multi-root policy, version, and ground-truth mapping.
- “Independent verification” is not one stage with one method. It must identify whether it verifies evidence, candidate eligibility, diagnosis, tool output, repair, execution, or recovery.
- “Evidence Provenance” includes both telemetry-side provenance and knowledge/action-side identity, but those must not be conflated.

### Still speculative

- Physical topology as a hard constraint plus dynamic dependency as a soft prior for Network RCA.
- A network candidate hierarchy spanning device/interface/module/link/path/fault type.
- Robust open-set and multi-root candidate pruning.
- A reliable threshold for when an LLM/Agent adds value over a fixed hybrid workflow.
- A complete production protocol combining RCA verification, human-gated remediation, rollback, and recovery.

## 9. Cross-Paper Relationships

### Cloud-OpsBench and CHIEF

Cloud-OpsBench asks whether an Agent follows a grounded and efficient investigative process in a deterministic operational state. CHIEF asks which Agent-step in a recorded failed trajectory is responsible. The former evaluates process behavior in an interaction environment; the latter constructs an offline candidate graph for failure attribution. Neither is a physical-network RCA algorithm.

### Cloud Intelligence and FlowFixer

Cloud Intelligence defines what a governed operational knowledge artifact should contain and how it should evolve. FlowFixer shows a concrete workflow-level diagnosis → patch → validation → retry loop. Together they suggest that action knowledge needs identity, preconditions, validation, and feedback, while also showing that a concrete workflow test is not enough to claim safe production remediation.

### Relation to earlier AIOps batches

The earlier papers supply operational examples that make the Batch 3 abstractions useful: RCAgentBench separates multimodal tool/process behavior; CAUSALDX makes candidate expansion and observation verification explicit; LLMGuard shows SOP-tree pruning and human-gated diagnosis; AIM and ChatRCA distinguish plan/action and human adjudication. Batch 3 does not replace those mechanisms; it sharpens their evaluation, candidate, provenance, and repair boundaries.

## 10. Answers to the Review Questions

### 1. What counts as auditable RCA evidence?

An observation with source, entity, time, transformation, freshness, uncertainty, and use relation preserved so a verifier or operator can re-check it. A text explanation without this chain is not sufficient. This is the current synthesis, supported in parts by snapshots, OKAs, Agent traces, workflow traces, data tickets, and evidence chains.

### 2. What should Evidence Provenance minimally contain?

At minimum: source/tool/query, modality, entity and level, time interval/clock, observation or derived value, transformation, freshness/status, confidence, missing/conflict state, related candidate, and relevant topology/configuration/knowledge version. A network-specific schema remains open.

### 3. When should multimodal evidence be aligned?

After modality-specific collection and before candidate generation or LLM reasoning, with candidate-specific association and raw-source links retained. The four papers motivate this boundary but do not define the complete network implementation.

### 4. How should Candidate Space be defined for evaluable RCA?

Declare the versioned candidate universe, output granularity, root/symptom semantics, root multiplicity, unknown policy, time semantics, pruning rules, and ground-truth mapping before scoring. CHIEF and FlowFixer show why this matters in non-network domains.

### 5. What is the potential value of hierarchical candidates for Network RCA?

They can reduce a huge search by first narrowing affected regions or devices and then moving to interfaces, modules, links, paths, or fault types. They can also make multi-level labels explicit. They may lose recall if pruning is wrong; the network hierarchy is not yet validated.

### 6. How do physical topology, fault hierarchy, and dynamic dependency differ?

Physical topology defines physical admissibility and reachability. Fault hierarchy organizes labels or diagnosis granularity. Dynamic dependency describes time-varying predictive/operational relations. They can cooperate, but none should silently stand in for the others or be called physical causality without evidence.

### 7. Why do open-set and multi-root cases challenge closed-set RCA?

Closed-set systems assume the true cause is among known labels/candidates and often return one root. An unknown cause can be pruned away or forced into a familiar class; multiple causes cannot be represented by one top-1 label. CHIEF and FlowFixer do not establish solutions: CHIEF focuses one decisive root, and FlowFixer uses a finite workflow taxonomy.

### 8. What layers should verification cover?

At least evidence, candidate eligibility, diagnosis/root attribution, tool output, proposed repair, actual execution, and recovery. The required check depends on risk; no single critic or self-check covers every layer.

### 9. Why is LLM self-check insufficient?

The same model can repeat the same mistaken entity mapping, unsupported assumption, tool interpretation, or repair rationale. A stronger check must introduce an independent source, deterministic constraint, fresh observation, controlled outcome, or human decision appropriate to the claim.

### 10. What is the difference between repair recommendation and validated remediation?

Recommendation is a proposed action. Validated remediation requires precondition/safety checks, authorized execution, observed effect, and an independent recovery judgment. FlowFixer’s test-input workflow validation is evidence for a patch in that environment, not proof of network recovery.

### 11. Why should recovery verification be independent?

The component that generated or accepted a repair may share its assumptions and errors. A fresh post-action telemetry/topology/health signal tests the system outcome rather than the plausibility of the action text. This is a current safety principle; the four papers do not provide a complete network implementation.

### 12. What should a benchmark evaluate together?

It should report separate values for RCA/candidate correctness, evidence grounding, tool correctness, process quality, latency, tokens/cost, action safety, human effort, execution success, rollback, and independent recovery. A single text-quality or final-answer metric is insufficient for Agentic AIOps.

### 13. Which architecture layer is currently weakest in the literature for Network AIOps?

The weakest layer is the **end-to-end interface from provenance-bearing, multi-modal physical-network evidence through candidate-constrained diagnosis to independently verified and human-gated recovery**. Individual papers strengthen pieces, but none jointly validates entity/time alignment, physical candidate space, open-set/multi-root RCA, safe action, rollback, and recovery.

### 14. Which parts of the Hybrid RCA architecture are strengthened or still hypotheses?

Evidence/process auditability, explicit candidate contracts, layered verification, and separation of repair from recovery are strengthened. Physical-plus-dynamic topology fusion, network hierarchical candidate construction, open-set/multi-root handling, Agent value thresholds, and complete recovery/remediation loops remain hypotheses or open research problems.

## 11. Implications for Network AIOps Research

### Ideas worth transferring

- Immutable or replayable incident packages with explicit source and query provenance.
- Versioned operational knowledge artifacts anchored to network alerts/entities/control points.
- Hierarchical candidate spaces with deterministic admissibility and bounded LLM comparison.
- Structured trace/evidence records rather than unstructured prompts.
- Pre-execution validation, controlled action, fresh observation, recovery verification, and rollback boundaries.
- Process metrics that expose invalid, redundant, unsupported, or overly costly investigation.

### Ideas that do not transfer directly

- Kubernetes snapshots as a substitute for physical network state.
- CHIEF’s Agent-step root as a direct device/interface/link root.
- FlowFixer’s workflow test success as network remediation success.
- Cloud Intelligence’s conceptual OKA contract as an already validated production protocol.
- LLM-generated graph/oracle semantics as a replacement for authoritative topology or deterministic telemetry.

### Current design questions

- Should physical topology be supplied as a hard candidate constraint, a tool, or both?
- Should traffic/NetFlow-derived dynamic paths be evidence, a soft graph, or a candidate generator?
- Which evidence fields must be present before an LLM can rank candidates?
- Which actions can be fully automated, which require a human gate, and which should be prohibited?
- How should multi-root/open-set labels and recovery success be represented in a benchmark?

## 12. Remaining Open Questions

- What is the unique identity of a network evidence item when several collectors report the same event at different times or granularities?
- How should candidate hierarchy, physical reachability, and dynamic dependency be jointly updated under topology/configuration drift?
- How can a verifier detect that LLM-generated candidate explanations or graph edges are unsupported?
- What safe controlled intervention, if any, can provide counterfactual evidence for network RCA?
- How should recovery be judged when the original symptom disappears but a new degradation is introduced?
- What matched evaluation isolates value from LLM reasoning, tools, knowledge, graph constraints, and human review?
- How should knowledge/artifact versions and repair experiences be retired when device firmware, topology, or command semantics change?

## 13. Next Learning Priorities

1. **Network-specific multimodal evidence and provenance:** metrics, syslog, traffic/NetFlow, configuration, interface/hardware state, and physical topology alignment.
2. **Hierarchical, open-set, and multi-root Network RCA:** candidate contracts, pruning recall, label granularity, and unknown handling.
3. **Verified remediation and recovery:** action safety, human gates, rollback, independent post-action signals, and recovery cost.
4. **Operational knowledge governance:** versioned runbooks/OKAs, drift detection, evidence preconditions, and retirement/conflict handling.
5. **Agentic AIOps evaluation:** process traces, tool correctness, cost/latency, human effort, and benchmark realism.

These priorities follow the current gaps rather than claiming that the four papers establish a new method or a proven research novelty.

## 14. Source Grounding Summary

- Cloud-OpsBench: Sec. 1–4, Figs. 1–2, Table 1; state snapshot, mocked interface, process metrics, and future-work boundaries.
- Cloud Intelligence/AIOps 2.0: Sec. 1–5; OKA definition/contract, anchoring, three loops, governance, and position-paper status.
- CHIEF: Sec. 3–7 and Appendices A–F; trajectory/root definition, HCG, virtual oracles, backtracking, counterfactual attribution, Who&When, Tables 1–4, and limitations.
- FlowFixer: Sec. II–VIII, Tables II–III, Figs. 5–6; symbolic traces/specifications, attribution, patch operators, pre-execution/dynamic verification, ExperiencePool, benchmark, and limitations.

## 15. Review Conclusion

The four papers strengthen a cautious Hybrid Network AIOps direction:

```text
authoritative telemetry and topology
→ provenance-bearing evidence
→ explicit, hierarchical candidate space
→ bounded LLM/Agent investigation
→ target-specific independent verification
→ human-gated action
→ controlled execution and recovery verification
```

The strongest current conclusion is architectural: reliability depends on the interfaces and checks around an LLM, not on calling every multi-step workflow an autonomous RCA Agent. The complete physical-network version—especially evidence alignment, open-set/multi-root candidate space, rollback, and recovery—remains to be designed and tested.
