# Network AIOps Architecture Synthesis v1

Status: evolving

## Scope

This is a research architecture synthesis based on the ten AIOps papers that have completed formal full-paper reading:

- [RCAgentBench](../../../papers/aiops/rcagentbench/notes.md)
- [StaR](../../../papers/aiops/star/notes.md)
- [CAUSALDX](../../../papers/aiops/causaldx/notes.md)
- [LLMGuard](../../../papers/aiops/llmguard/notes.md)
- [KAT](../../../papers/aiops/kat/notes.md)
- [Comfey](../../../papers/aiops/comfey/notes.md)
- [AIM](../../../papers/aiops/aim/notes.md)
- [StepFly](../../../papers/aiops/stepfly/notes.md)
- [TSGen](../../../papers/aiops/tsgen/notes.md)
- [ChatRCA](../../../papers/aiops/chatrca/notes.md)

It also uses [AIOps Knowledge Review v1](aiops-knowledge-review-v1.md) and [AIOps Knowledge Review v2](aiops-knowledge-review-v2.md). It does not re-read all source PDFs or process Batch 3.

## Evidence Convention

- **Paper-backed evidence:** a mechanism, result, or limitation reported in a completed paper note with Section, Figure, Table, or Appendix grounding.
- **Cross-paper synthesis:** a relationship or abstraction derived from several papers.
- **Design hypothesis:** a proposed architecture for Network AIOps that is informed by the literature but not proven by these papers.

The architecture below is therefore a working design model, not a standard proposed by any single paper.

## Executive Synthesis

The current evidence favors a **hybrid Network AIOps RCA architecture**:

~~~text
Deterministic / ML Front-end
        ↓
Event and Evidence Layer
        ↓
Topology-constrained Candidate Generator
        ↓
LLM / Agent Investigation Layer
        ↓
Verified RCA and Diagnosis
        ↓
Human-gated Recommendation or Remediation
        ↓
Recovery Observation and Knowledge Update
~~~

This division follows a practical boundary:

- deterministic and statistical components are better at enumeration, arithmetic, schema checks, time alignment, topology constraints, and safety conditions;
- graph and topology algorithms are better at representing admissible relationships and reducing candidate space;
- LLMs are useful for heterogeneous evidence interpretation, hypothesis synthesis, and explanations when their inputs and outputs are structured;
- Agents are useful only when an incident requires repeated evidence collection, observation-dependent next-step selection, verification, escalation, or bounded replanning;
- Tools provide the controlled interface to current telemetry and system state;
- humans should retain authority at high-impact, low-confidence, contradictory, open-set, and state-changing points.

This is a **design hypothesis**, not a claim that the ten papers have already validated one optimal architecture.

## 1. Working Network AIOps RCA Pipeline

The following is the current cross-paper working pipeline:

~~~text
Incident / Failure
        ↓
Telemetry Collection
        ↓
Evidence Normalization and Alignment
        ↓
Detection / Event Formation
        ↓
Candidate Space Construction
        ↓
Candidate Pruning
        ↓
Topology / Dependency Constraint
        ↓
Evidence Retrieval
        ↓
RCA Ranking / Reasoning
        ↓
Verification
        ↓
Diagnosis / Explanation
        ↓
Remediation Recommendation
        ↓
Human Approval / Safe Execution
        ↓
Recovery Verification
        ↓
Knowledge Update
~~~

The ten papers implement different subsets:

- RCAgentBench, StaR, and CAUSALDX make candidate, structural, or causal reasoning explicit.
- LLMGuard, KAT, TSGen, and StepFly show different ways to use operational knowledge and procedures.
- Comfey adds production incident ownership routing.
- AIM separates alert context, plan generation, and controlled plan-to-act execution.
- ChatRCA adds role-specialized evidence collection and human adjudication.

No paper validates this complete physical-network pipeline from raw telemetry through safe recovery. The complete flow is therefore a synthesis.

## 2. Who Should Perform Each Stage?

The assignments below are **current design recommendations**. The evidence column records why each boundary is consistent with the completed literature.

| Stage | Preferred mechanism | Why this boundary is useful | Current evidence and limit |
| --- | --- | --- | --- |
| Incident ingestion and event formation | Deterministic / rule-based plus statistical/ML | Preserve timestamps, identifiers, alert semantics, and deduplication | Most reviewed systems receive an alert, error, anomaly window, or incident first; the batch does not establish a unified detector |
| Telemetry collection | Deterministic adapters and Tools; bounded Agent selection | Query interfaces can enforce schemas, permissions, time ranges, and audit logs | RCAgentBench, LLMGuard, StepFly, and ChatRCA expose tool/procedure-based evidence collection; tool coverage remains domain-specific |
| Evidence normalization and alignment | Deterministic / statistical | Time, entity, unit, missingness, and provenance should be reproducible | AIM aligns service/time context before prompting; a complete network alignment protocol is not yet shown |
| Detection and anomaly scoring | Statistical / ML / rule-based | Numerical deviation and delay are measurable and repeatable | StaR and the Batch 1 anomaly/RCA papers show model-based or rule-based evidence; LLMs are not the default detector in this scope |
| Candidate universe construction | Graph / topology algorithm plus deterministic domain rules | Enumerate physically admissible devices, interfaces, links, modules, paths, and fault types | Existing papers use services, pods, metric variables, anomaly nodes, SOP leaves, or teams; no common network candidate universe exists |
| Candidate pruning | Graph / topology algorithm plus statistical/ML scores | Reduce cost and prevent unconstrained LLM generation over a huge space | CAUSALDX uses select/expand/verify; RCAgentBench uses hierarchy/context; the network pruning protocol remains a design hypothesis |
| Topology / dependency constraint | Graph / topology algorithm; learned dependencies as soft priors | Structural validity and learned temporal dependence have different meanings | StaR provides stateful dynamic graph evidence; RCAgentBench, CAUSALDX, KAT, and ChatRCA use different non-equivalent structures |
| Evidence retrieval | Tools, deterministic filters, Knowledge Base/RAG, optionally an Agent | Retrieve only relevant windows, cases, SOPs, and topology context with provenance | KAT, LLMGuard, AIM, TSGen, and ChatRCA show knowledge/context retrieval; retrieval is not itself memory or remediation |
| RCA ranking and reasoning | Hybrid: graph/statistical ranking plus bounded LLM synthesis | Algorithms can score structure; LLMs can compare heterogeneous evidence and formulate hypotheses | CAUSALDX and StaR provide structured reasoning contrasts; LLM outputs still need candidate and evidence constraints |
| Verification | Deterministic checks, re-query, topology consistency, independent model, cross-modal corroboration, and human | The verifier should rely on evidence other than the answer’s own wording | LLMGuard, CAUSALDX, AIM, StepFly, and ChatRCA show partial forms; no universal physical-causality verifier exists |
| Diagnosis and explanation | Structured taxonomy plus LLM explanation; human for ambiguous cases | Keep fault type, root entity, evidence, and uncertainty separate | ChatRCA separates category, reasoning, and evidence consistency; text similarity is not physical RCA correctness |
| Remediation recommendation | Tool-augmented LLM under policy and typed action schema | LLM may translate verified diagnosis into options, but should not own safety policy | AIM demonstrates plan-to-code feasibility in a testbed; the papers do not establish safe production autonomy |
| Action execution | Deterministic action tool plus human gate | Permissions, preconditions, rollback, and auditability must be explicit | Batch 2 has no complete production repair/recovery loop |
| Recovery verification | Deterministic telemetry re-query plus independent checks and human escalation | Verify system state changed as intended, not merely that a script ran | Recovery verification is a major gap across the ten-paper slice |
| Knowledge update | Versioned operational-knowledge pipeline plus human review | New guides and cases need provenance, validity, conflict handling, and retirement | TSGen, KAT, Comfey, and StepFly show pieces of this lifecycle but not one complete policy |

## 3. What Should Remain Deterministic?

The following functions should normally remain deterministic, statistical, or explicitly constrained:

- candidate enumeration and identifier mapping;
- topology lookup, neighbor/path computation, and interface-to-link mapping;
- metric calculations, aggregation, thresholding, and anomaly windows;
- timestamp and entity alignment;
- schema, type, unit, namespace, and configuration validation;
- tool argument validation and permission checks;
- candidate pruning based on topology, scope, and observable constraints;
- action preconditions, safety policies, rollback conditions, and recovery checks;
- logging of tool calls, evidence provenance, state transitions, and human decisions.

This does not mean these components must be perfect or rule-only. Statistical models and graph methods can be probabilistic. The important property is that their assumptions, outputs, and failure modes are inspectable and independently testable.

The literature supports this separation in different ways: StaR uses a non-LLM stateful dynamic graph; LLMGuard uses a deterministic SOP Checking Tree at runtime; StepFly compiles guides into DAG and query interfaces; and AIM validates generated execution artifacts before testbed action (Source: [StaR note](../../../papers/aiops/star/notes.md), Sec. 3–5; [LLMGuard note](../../../papers/aiops/llmguard/notes.md), Sec. IV–V; [StepFly note](../../../papers/aiops/stepfly/notes.md), Sec. 4.2–4.4; [AIM note](../../../papers/aiops/aim/notes.md), Sec. 3.4, Sec. 4.4.6).

## 4. Where Can LLMs Help?

LLMs are most promising where the input is heterogeneous, partly textual, and difficult to normalize into one fixed feature representation:

- interpret logs, syslog, tickets, SOPs, configuration changes, and incident narratives;
- synthesize evidence from multiple already-structured modalities;
- formulate and compare hypotheses over a bounded candidate set;
- select among well-defined tools when the next query depends on current evidence;
- convert verified findings into an operator-readable diagnosis and explanation;
- use historical incidents or operational knowledge as contextual evidence.

The main risk is that language fluency can hide missing evidence, incorrect causal claims, or an invalid action. LLM use therefore requires candidate constraints, evidence provenance, structured outputs, independent checks, and abstention.

The papers support several distinct roles rather than one universal LLM role: RCAgentBench evaluates tool-using reasoning processes; CAUSALDX uses LLM-guided candidate expansion and verification; LLMGuard uses LLMs around a deterministic SOP tree; KAT grounds generation in a troubleshooting graph; AIM uses prompt-level multimodal context and plan generation; and ChatRCA distributes evidence and hypotheses across role-specific agents (Source: the corresponding formal notes and [Knowledge Review v1](aiops-knowledge-review-v1.md)).

## 5. Candidate Space for Network RCA

### 5.1 Candidate universe

Network RCA should not start with an untyped list of strings. A useful candidate universe may contain several levels:

~~~text
device
→ chassis / card
→ interface / port
→ optical module
→ link
→ path / segment
→ service or dependent system
→ fault type
~~~

This hierarchy is a **design hypothesis**. A particular incident may use only a subset, and the correct root can be a set rather than one item.

Candidate records should preserve at least:

~~~text
(entity, entity level, fault type, time interval, causal role, evidence references)
~~~

The causal role should distinguish:

- initiating fault;
- affected component;
- downstream symptom;
- suspected propagation intermediary;
- unknown candidate.

This prevents a downstream alarm or an affected interface from being silently treated as the initiating root.

### 5.2 Candidate construction and pruning

A cautious pipeline is:

1. Enumerate entities from the current physical and logical topology.
2. Restrict to the incident time interval and affected region.
3. Map telemetry evidence to entities with explicit identifier confidence.
4. Remove candidates that violate hard physical or administrative constraints.
5. Add or up-rank neighboring, upstream, downstream, and path-related candidates.
6. Use statistical or learned dependency scores as soft evidence.
7. Preserve an unknown and a multiple-root option.
8. Ask the LLM to compare a bounded candidate set and cite evidence.

This combines the explicit candidate and verification patterns in CAUSALDX, the hierarchy/process emphasis in RCAgentBench, and the structural constraints in StaR and the operational workflows (Source: [CAUSALDX note](../../../papers/aiops/causaldx/notes.md), Sec. 3–5; [RCAgentBench note](../../../papers/aiops/rcagentbench/notes.md), Sec. IV–V; [StaR note](../../../papers/aiops/star/notes.md), Sec. 3–5).

### 5.3 Why not let an LLM search the entire candidate set?

Direct free-form generation over a very large candidate space can:

- omit valid entities without a reproducible search process;
- mix device, link, interface, and fault-type granularities;
- produce plausible but nonexistent identifiers;
- ignore physical reachability and temporal constraints;
- force an unknown fault into a known label;
- make multi-root reasoning difficult to audit;
- increase token cost and latency without improving evidence quality.

The conclusion is not that an LLM can never choose a root. It should choose or rank roots **after** deterministic/graph candidate construction and pruning, with an explicit unknown option and evidence references. Direct LLM root prediction may be reasonable only when the candidate set is small, well-defined, the ground truth has matching granularity, and independent verification exists.

### 5.4 Ground-truth alignment

Evaluation should specify whether the target is:

- a device, card, interface, optical module, link, path, service, or fault type;
- one root or a root set;
- an onset time or an interval;
- an initiating cause or a downstream symptom;
- a known label or an open-set unknown.

Top-k localization, diagnosis accuracy, causal explanation, and remediation success should be reported separately. This follows the distinctions already made in RCAgentBench, CAUSALDX, ChatRCA, and AIM notes.

## 6. Topology Responsibilities

### 6.1 Different topology semantics

| Structure | Meaning | Appropriate role | Current caution |
| --- | --- | --- | --- |
| Physical network topology | Devices, interfaces, links, modules, and reachability | Hard constraint, candidate generator, path context, recovery check | Must reflect version and current state |
| Logical topology | VLAN, routing, overlay, service or control relationships | Candidate scope, path reasoning, context | May differ from physical reachability |
| Service dependency / call graph | Application interaction | Propagation context and service candidate ranking | Not a physical network graph |
| Learned dynamic dependency | Temporal or predictive relation in observed signals | Soft ranking prior, anomaly propagation evidence | Predictive usefulness is not physical causality |
| Causal graph | Explicit causal hypothesis/model | Search, intervention or verification structure | The word causal needs method-specific evidence |
| Anomaly dependency graph | Relations among abnormal observations | Candidate expansion and diagnostic backtracking | Not automatically a topology graph |
| Knowledge graph / subsystem graph | Operational concepts, symptoms, procedures, and solutions | Retrieval and context organization | Knowledge relation is not necessarily a runtime causal edge |

These distinctions synthesize StaR, CAUSALDX, RCAgentBench, KAT, LLMGuard, and ChatRCA. The existing [Topology-aware RCA concept](../../../concepts/aiops/topology-aware-rca.md) should retain this semantic separation.

### 6.2 Physical topology plus dynamic dependency

**Research hypothesis:** combine physical topology as an admissibility constraint with dynamic dependency and traffic-derived relations as uncertain, time-varying evidence.

One possible pattern is:

~~~text
Physical graph
→ admissible candidates and paths

Dynamic dependency / traffic evidence
→ soft scores, temporal ordering, and propagation hypotheses

Evidence verification
→ retain, reject, or downgrade the combined hypothesis
~~~

The two structures should not be merged into one undifferentiated graph. Each edge should carry type, timestamp/version, confidence, and provenance. A learned relation can help rank a physical candidate without being presented as proof that the edge is physically causal.

## 7. Telemetry and Evidence Layer

### 7.1 Evidence roles

- **Metrics:** deviation, trend, magnitude, utilization, counters, resource state, and time-local change.
- **Syslog and logs:** event semantics, error codes, component clues, configuration messages, and operator language.
- **Traces/spans:** request path, span timing, service propagation, and latency relationships where tracing exists.
- **Traffic and NetFlow:** flow volume, direction, path changes, drops, bursts, fan-in/fan-out, and communication anomalies.
- **Configuration:** intended state, recent changes, policy, routing, interface settings, and mismatch with observed state.
- **Physical topology and interface state:** adjacency, link state, port errors, module health, reachability, and possible propagation boundaries.
- **Tickets, documents, SOPs, and historical incidents:** operational context, known procedures, prior hypotheses, and mitigation guidance.

No one modality is the root cause by default. Metrics may detect a deviation but not explain it; logs may identify a mechanism but be duplicated or stale; traffic can expose propagation but not identify the initiating fault without topology and configuration context.

The reviewed literature does not yet provide a complete Network AIOps protocol that jointly handles metrics, syslog, traffic/NetFlow, configuration, physical topology, and hardware/optical evidence. This remains a research gap rather than a solved architecture.

### 7.2 Evidence Ticket / Evidence Provenance

The ten-paper slice supports a reusable evidence handoff pattern. ChatRCA makes a data ticket explicit; RCAgentBench exposes modality-specific tools and process traces; LLMGuard preserves evidence chains; CAUSALDX verifies candidate observations; and AIM aligns selected context before generation.

A proposed evidence object is:

~~~text
Evidence
  source
  modality
  entity
  time window
  observation
  value or summary
  confidence
  provenance / query
  freshness
  missingness or conflict state
  related candidate(s)
~~~

This is a **design hypothesis**, but it has enough cross-paper support to be maintained as the [Evidence Provenance concept](../../../concepts/aiops/evidence-provenance.md). It can help:

- align heterogeneous telemetry without hiding the original source;
- provide bounded context to an LLM or Agent;
- allow a verifier or human to re-query the same evidence;
- distinguish evidence quality from diagnosis quality;
- audit why a candidate was generated, promoted, or rejected.

The evidence ticket should not become a free-text summary only. It should preserve structured fields and links back to raw or reproducible queries.

## 8. Where the LLM Should Sit

| Placement | Strength | Main risk | Required grounding and verification |
| --- | --- | --- | --- |
| Direct root-cause prediction | Simple interface and low orchestration overhead | Large/open candidate spaces, hallucinated identifiers, mixed granularity, weak provenance | Small aligned candidate set, structured output, topology checks, independent evidence |
| Candidate ranking | Can compare heterogeneous clues and express uncertainty | Ranking may reflect language plausibility rather than causal support | Candidate IDs, evidence references, calibrated scores, deterministic constraints |
| Evidence synthesis | Handles logs, tickets, SOPs, and cross-modal summaries well | Context overload, lost source provenance, plausible unsupported synthesis | Evidence Ticket, source links, time/entity alignment, contradiction handling |
| Tool orchestration | Can choose the next query when the path depends on observations | Wrong arguments, loops, over-querying, permission violations | Typed tools, allowlist, budgets, termination, retries, audit trace, human escalation |
| Explanation | Produces useful operator-facing summaries and hypotheses | Fluent explanation can be unfaithful or overconfident | Every claim linked to evidence; separate explanation quality from RCA correctness |

### Conditional conclusion

The LLM should not be unconditionally responsible for the root-cause decision. A more defensible arrangement is:

~~~text
deterministic / graph candidate set
→ LLM evidence synthesis and bounded ranking
→ independent verification
→ structured diagnosis with uncertainty
→ human or policy gate for high-impact actions
~~~

The LLM may make the final selection in a low-risk, well-bounded setting if the candidate space, evidence, and verifier are explicit. For open-set or high-impact network incidents, it should be able to abstain and request more evidence or human review.

## 9. When Is an Agent Loop Necessary?

A one-shot pipeline is sufficient when:

~~~text
normalized evidence
→ bounded classifier or ranker
→ verified result
~~~

An Agent loop becomes justified when the system must:

- decide which telemetry or topology tool to query next;
- use an observation to expand, prune, or revise candidates;
- test a hypothesis with a new independent observation;
- handle missing or conflicting evidence;
- route the case to another role or domain;
- stop, retry, abstain, escalate, or request approval based on state.

The Batch 2 systems illustrate different strengths:

- Comfey selects a next owning team after local enrichment and rejection.
- StepFly advances a guide-derived DAG based on plugin results and dependencies.
- ChatRCA selects roles and requests further evidence around hypotheses.
- AIM has plan generation and controlled execution but no demonstrated continuous live replanning.
- TSGen generates operational knowledge offline and is not a runtime Agent.

Thus an Agent is justified by observation-dependent continuation and action authority, not by using an LLM or several prompts. The loop should be bounded by tool permissions, candidate space, time/token budgets, and verification conditions.

## 10. Network AIOps Tool Taxonomy

Tools should be typed by what they observe or change:

### Telemetry tools

- Query metrics and counters.
- Search syslog and structured logs.
- Query traces and spans.
- Query traffic, NetFlow, packets, drops, and flow summaries.
- Read interface, hardware, and optical state.

### Topology tools

- Neighbor and adjacency lookup.
- Path and reachability query.
- Device/interface/link mapping.
- Logical dependency lookup.
- Topology version and change lookup.

### Configuration and state tools

- Read interface, routing, policy, and device configuration.
- Compare intended and observed state.
- Query recent changes and maintenance events.

### Evidence and knowledge tools

- Retrieve historical incidents.
- Retrieve SOPs, TSGs, and knowledge-graph paths.
- Reconstruct the source and provenance of an evidence item.

### Verification tools

- Re-query telemetry after a hypothesis.
- Check cross-modal consistency.
- Validate topology reachability or dependency constraints.
- Compare against an independent detector or ranker.
- Check candidate/ground-truth schema and confidence thresholds.

### Action tools

- Generate a remediation proposal.
- Apply a permitted change.
- Roll back a change.
- Trigger a controlled diagnostic or recovery operation.

Retrieval tools, read-only observation tools, and state-changing action tools should have separate permissions and evaluation. AIM’s Ansible path and the read-oriented tools in StepFly/ChatRCA show why “tool use” is too broad a category for safety analysis (Source: [AIM note](../../../papers/aiops/aim/notes.md), Sec. 3.4; [StepFly note](../../../papers/aiops/stepfly/notes.md), Sec. 4.3–4.4; [ChatRCA note](../../../papers/aiops/chatrca/notes.md), Sec. 4.2).

## 11. Verification Layer

### 11.1 Verification types

- **Deterministic validation:** schema, type, unit, namespace, syntax, permission, and precondition checks.
- **Telemetry re-query:** obtain a new observation or check whether the same signal persists.
- **Topology consistency:** test reachability, adjacency, path, dependency, or state constraints.
- **Independent algorithm:** compare with a detector, graph ranker, statistical model, or causal check not generated by the same answer path.
- **Cross-modal corroboration:** require consistent support from independent metrics, logs, traces, traffic, configuration, or topology.
- **Second model or critic:** useful as a supplementary check, but not automatically independent if it sees the same flawed context.
- **Human confirmation:** operator judgment for ambiguous, high-impact, or out-of-coverage cases.
- **Execution feedback:** inspect actual action result and resulting state.
- **Recovery verification:** confirm service/network state has recovered after remediation.

LLM self-confirmation is not independent verification.

### 11.2 What should be verified

| Target | Suitable checks |
| --- | --- |
| Candidate localization | Entity validity, topology consistency, time alignment, independent detector/ranker, evidence coverage |
| Root-cause hypothesis | New telemetry, competing candidate comparison, causal/dependency semantics, cross-modal corroboration, operator review |
| Diagnosis category | Taxonomy/schema validation and ground-truth evaluation; do not confuse category match with physical causality |
| Explanation | Evidence-linked claims, consistency with observations, operator review; text similarity alone is insufficient |
| Remediation proposal | Preconditions, policy, permissions, blast radius, rollback plan, human approval |
| Executed remediation | Tool result, state diff, safety logs, telemetry re-query, recovery, rollback if needed |

The current literature provides partial versions of these checks, but no paper validates all of them for physical network RCA.

## 12. Human Gate

| Operating mode | Human role | Appropriate use |
| --- | --- | --- |
| Human-in-the-loop | Human must approve or edit the next decision/action | High-impact diagnosis, remediation, rollback, or knowledge publication |
| Human-on-the-loop | System runs within preapproved bounds; human monitors and can intervene | Low-risk read-only investigation and bounded routine procedures |
| Fully autonomous | No immediate human approval | Only after strong evidence of bounded scope, verification, recovery, safety, and operational reliability; not established by this literature slice |

Human gates should be triggered by:

- high-impact configuration or state change;
- low confidence or competing root causes;
- conflicting, missing, delayed, or stale telemetry;
- open-set or multi-root incidents;
- candidate/ground-truth granularity mismatch;
- topology or configuration drift;
- failed verification or failed recovery;
- new or materially changed operational knowledge.

ChatRCA’s data-ticket verification and root-cause adjudication illustrate explicit human checkpoints; LLMGuard and StepFly show engineering/SRE checks around procedures; AIM’s testbed execution should not be mistaken for a production approval protocol (Source: [ChatRCA note](../../../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.7–5.8; [LLMGuard note](../../../papers/aiops/llmguard/notes.md), Sec. IV–V; [StepFly note](../../../papers/aiops/stepfly/notes.md), Sec. 7; [AIM note](../../../papers/aiops/aim/notes.md), Sec. 4.4.6).

## 13. Remediation Boundary

The most cautious working remediation workflow is:

~~~text
Verified diagnosis
→ Proposed action
→ Deterministic safety and permission checks
→ Human approval when impact is material
→ Controlled action tool
→ Observe resulting state
→ Recovery verification
→ Rollback or escalation if needed
→ Versioned knowledge update after review
~~~

This keeps three outcomes separate:

~~~text
Recommendation ≠ Execution ≠ Recovery Verification
~~~

A generated script is a recommendation or an executable artifact until it is actually run under permission and safety controls. A successful execution is not recovery until the system state and incident symptoms are independently checked. The ten papers do not establish a complete autonomous production remediation loop.

## 14. Traditional RCA versus Agentic RCA

| Dimension | Traditional / model-based RCA | Agentic RCA | Hybrid implication |
| --- | --- | --- | --- |
| Determinism | Usually high for a fixed model and input | Varies with prompts, tools, and path choices | Keep critical constraints and scoring inspectable |
| Interpretability | Model features, graph edges, rules, or scores can be inspected | Natural-language traces are readable but not necessarily faithful | Store structured evidence and action traces beside explanations |
| Candidate handling | Efficient when the universe and model are defined | Flexible but can drift or hallucinate candidates | Use algorithms to enumerate/prune; let LLM compare bounded candidates |
| Heterogeneous evidence | Requires feature engineering or separate models | Stronger at text and cross-source synthesis | Normalize sources first, then use LLM for synthesis |
| Dynamic investigation | Often fixed inference path | Can query, branch, retry, and escalate | Use a bounded Agent loop over typed Tools |
| Tool use | Usually external to the model | First-class runtime interaction | Keep tool interfaces deterministic and permissioned |
| Verification | Can be built into rules, graph checks, or evaluation | Often incomplete if the Agent judges itself | Use independent checks and human gates |
| Cost and latency | Easier to budget | More calls, tokens, and coordination | Set budgets and measure path/tool cost |
| Safety | Explicit policies are easier to enforce | Natural-language actions can be unsafe | Do not let the LLM bypass action policy |
| Open-set capability | May be limited by training/candidate space | Can propose unknowns, but may hallucinate them | Preserve unknown/multi-root outputs and verify them |

The likely future is hybrid because the failure modes are complementary: pure traditional methods may struggle with heterogeneous text and changing procedures, while pure Agent approaches struggle with candidate scale, reproducibility, grounding, cost, and safety. This is a synthesis-based design conclusion, not a proof that every hybrid system will outperform either alternative.

## 15. Proposed Hybrid Network AIOps Architecture

This is the current **research design hypothesis**:

~~~text
┌──────────────────────────────────────────────────────────────┐
│ Deterministic / ML Front-end                                 │
│ detection, event correlation, aggregation, time/entity map   │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Evidence Layer                                                │
│ modality adapters, Evidence Tickets, provenance, confidence  │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Candidate and Topology Layer                                  │
│ physical enumeration, pruning, dynamic soft dependencies     │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ LLM / Agent Investigation Layer                               │
│ bounded tool choice, hypothesis comparison, query/retry      │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Verification and Diagnosis Layer                              │
│ re-query, cross-modal checks, independent ranker, uncertainty │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Human-gated Action Layer                                      │
│ recommendation, approval, controlled execution, rollback     │
└──────────────────────────────────────────────────────────────┘
                              ↓
┌──────────────────────────────────────────────────────────────┐
│ Recovery and Knowledge Lifecycle                              │
│ state verification, incident record, update, version, retire │
└──────────────────────────────────────────────────────────────┘
~~~

The architecture should support a read-only mode first. Action permissions should be introduced only after evidence, verification, and recovery evaluation are established.

## 16. Mapping to My Current Research

This is a high-level mapping to the research direction recorded in the AIOps knowledge base. It does not claim that an existing experiment system already implements any listed capability.

| Research concern | Hybrid architecture location | Immediate design question |
| --- | --- | --- |
| Fault detection | Deterministic / ML front-end | How should detection uncertainty and alert delay be passed to RCA? |
| RCA and fault localization | Candidate and topology layer plus LLM/Agent investigation | What is the root entity level: device, interface, link, module, path, or set? |
| Fault classification / diagnosis | Diagnosis layer | How should category, mechanism, root entity, and uncertainty be represented separately? |
| Metrics and syslog | Modality adapters and Evidence Layer | How should numeric deviations and textual events share entity/time provenance? |
| Traffic / NetFlow | Modality adapters, path tools, and candidate layer | Can flow/path change narrow the physical candidate space without being mistaken for causality? |
| Physical topology | Candidate and topology layer | Which relations are hard constraints, soft priors, or merely context? |
| Large candidate space | Candidate construction/pruning | How can thousands of entities be reduced reproducibly before LLM reasoning? |
| LLM / Agent RCA | Bounded investigation layer | Which tools should the Agent select, and when should it abstain or escalate? |
| Production evaluation | Verification, human, action, and recovery layers | How should correctness, latency, cost, safety, human effort, and recovery be measured together? |

The most direct research opportunity is therefore not to replace the existing detection or RCA algorithms with an unconstrained Agent. It is to define a verifiable interface between telemetry/candidate algorithms and a bounded evidence-grounded investigation layer.

## 17. Top Research Questions

### P0 — Network multimodal evidence alignment

- **Why it matters:** misaligned timestamps, entity names, and missingness can make a coherent LLM explanation factually wrong.
- **Evidence from current literature:** AIM performs prompt-level metric/log/trace/alert alignment; RCAgentBench and ChatRCA expose multimodal evidence through tools/roles; the reviews identify no complete network protocol.
- **Current gap:** no validated Evidence Ticket schema and benchmark covering metrics, syslog, traffic/NetFlow, configuration, topology, and hardware state.

### P0 — Physical topology plus dynamic dependency

- **Why it matters:** physical reachability can eliminate impossible causes, while dynamic dependency can expose temporal propagation.
- **Evidence from current literature:** StaR provides stateful dynamic graph evidence; other papers use service, anomaly, subsystem, or knowledge graphs with different semantics.
- **Current gap:** how to combine hard physical constraints with uncertain dynamic/traffic relations without claiming false causality.

### P0 — Large, open-set, and multi-root candidate spaces

- **Why it matters:** network incidents may involve many devices and simultaneous causes, and forcing an unknown fault into a closed label is unsafe.
- **Evidence from current literature:** CAUSALDX addresses candidate expansion; RCAgentBench and ChatRCA evaluate bounded candidate settings; Batch 2 exposes guide/category coverage limits.
- **Current gap:** hierarchical root-set ground truth, unknown handling, candidate pruning, and evaluation aligned with physical network entities.

### P1 — Verified Agentic investigation

- **Why it matters:** Agents are useful only when evidence collection must adapt to observations, missingness, or competing hypotheses.
- **Evidence from current literature:** StepFly, CAUSALDX, Comfey, and ChatRCA show bounded loops with different action spaces; no shared capability/evaluation protocol exists.
- **Current gap:** when to use a fixed workflow, when to allow replanning, and how to attribute failures to the model, tool, orchestration, or environment.

### P1 — Safe human-gated remediation

- **Why it matters:** a wrong network action may create a larger outage than a wrong diagnosis.
- **Evidence from current literature:** AIM shows controlled plan-to-code execution; ChatRCA and LLMGuard demonstrate human or SRE checks; a complete production repair/rollback/recovery loop is absent.
- **Current gap:** permission, blast radius, approval threshold, rollback, recovery observation, and failure-cost evaluation.

### P1 — Operational knowledge and memory lifecycle

- **Why it matters:** stale SOPs, routing tables, RAG cases, and generated TSGs can bias diagnosis.
- **Evidence from current literature:** TSGen, KAT, Comfey, StepFly, and ChatRCA each expose different knowledge/context persistence patterns.
- **Current gap:** provenance, versioning, conflict handling, compression, invalidation, forgetting, and the boundary between operational knowledge and Agent memory.

### P1 — Production Agent evaluation

- **Why it matters:** accuracy alone does not show operational value.
- **Evidence from current literature:** production deployment, controlled testbeds, process metrics, cost, latency, human effort, and acceptance are measured differently across the ten papers.
- **Current gap:** a matched evaluation that separates detection, localization, diagnosis, explanation, tool correctness, cost, safety, human effort, remediation, and recovery.

## 18. What This Synthesis Does Not Establish

- It does not establish that a hybrid architecture is optimal.
- It does not prove that an LLM improves physical root-cause correctness after controlling for tools, graphs, rules, and candidate pruning.
- It does not prove that Multi-Agent systems outperform a single Agent under equal context, tool, token, latency, and human-review budgets.
- It does not provide a complete Network AIOps benchmark or physical causal ground truth.
- It does not define a production-safe autonomous remediation policy.
- It does not claim that the current research system already implements the proposed layers.

## 19. Source Grounding

The synthesis uses the completed notes as the default evidence layer:

- [RCAgentBench note](../../../papers/aiops/rcagentbench/notes.md) — multimodal tools, candidate hierarchy, process evaluation, and benchmark limits.
- [StaR note](../../../papers/aiops/star/notes.md) — stateful dynamic graphs, temporal evidence, and predictive-versus-physical causality.
- [CAUSALDX note](../../../papers/aiops/causaldx/notes.md) — candidate select/expand/verify, long-tail/cascading diagnosis, and tool verification.
- [LLMGuard note](../../../papers/aiops/llmguard/notes.md) — SOP Checking Tree, deterministic checks, evidence chains, production diagnosis, and human gating.
- [KAT note](../../../papers/aiops/kat/notes.md) — troubleshooting knowledge graph, cross-subsystem context, and operational knowledge updates.
- [Comfey note](../../../papers/aiops/comfey/notes.md) — local evidence enrichment, ownership routing, production constraints, and human fallback.
- [AIM note](../../../papers/aiops/aim/notes.md) — prompt-level multimodal context, plan-to-act separation, validation, and controlled execution.
- [StepFly note](../../../papers/aiops/stepfly/notes.md) — guide-derived DAGs, typed query plugins, scheduler/executor control, and structured working data.
- [TSGen note](../../../papers/aiops/tsgen/notes.md) — historical operational-knowledge generation, guide updates, and human acceptance.
- [ChatRCA note](../../../papers/aiops/chatrca/notes.md) — role-specialized evidence collection, RAG context, human checkpoints, and RCA evaluation.

The pipeline, mechanism-to-stage assignments, Evidence Ticket schema, hybrid architecture, and priority questions are cross-paper synthesis or design hypotheses. They should be revised when later full-paper evidence conflicts with them.
