# AIOps Questions

Status: evolving

This file contains AIOps-specific questions raised during formal reading. Statuses are scoped to the current evidence and should not be treated as permanent answers.

## Questions from RCAgentBench

1. **How should the candidate root-cause space be defined for network incidents?**
   Status: Open. RCAgentBench provides controlled service/pod/node levels but does not specify a general numeric candidate-space protocol for heterogeneous network components.

2. **How should metrics, logs, traces, topology, and traffic evidence be aligned when their time windows and provenance differ?**
   Status: Open. RCAgentBench exposes separate tools and windows, but does not solve the general network telemetry alignment problem.

3. **How much of an Agent RCA result comes from the model versus tool design, hierarchy, and available evidence?**
   Status: Partially Answered. Tool and hierarchy ablations show that the observation interface and structural prior materially affect results (Source: RCAgentBench, Sec. V-C–D, pp. 7–9).

4. **Can service-call topology benefits transfer to physical network topology without treating dependency as physical causality?**
   Status: Open.

5. **How should unknown, multiple, or correlated network root causes be evaluated?**
   Status: Open. The controlled benchmark does not establish an open-set, multi-root network protocol.

## Cross-paper Questions for Batch 1

6. **What is the common boundary between detection, localization, RCA, diagnosis, explanation, and remediation?**
   Status: Partially Answered. RCAgentBench makes localization, fault type, explanation, and path length separate metrics; later papers will test whether this separation holds across production systems.

7. **Which topology semantics are actually supported by a given method?**
   Status: Open. A service graph, dynamic causal graph, anomaly graph, SOP tree, and physical network graph should not be treated as equivalent.

8. **Does a graph used by an RCA method represent physical causality, predictive dependency, or an operational reasoning structure?**
   Status: Open.

9. **Can process-level metrics such as evidence coverage and diagnostic path length be made comparable across LLM, classical, and human-guided RCA?**
   Status: Open.

10. **What ground truth can support production-scale RCA when incidents have delayed effects, multiple causes, or incomplete repair records?**
    Status: Open.

11. **Does adding an LLM improve root-cause correctness, or mainly evidence organization and explanation?**
    Status: Open.

12. **How should a network RCA system handle erroneous, missing, delayed, or contradictory telemetry without accumulating a misleading explanation?**
    Status: Open.

## Questions from StaR

13. **When does a stateful learned graph represent predictive dependency rather than physical network causality?**
    Status: Partially Answered. StaR explicitly warns that Granger-style predictive usefulness is not proof of physical causality; a network-specific validation protocol is still open (Source: StaR, Sec. 5).

14. **How should root ranking handle delayed faults and downstream propagation in network telemetry?**
    Status: Partially Answered. StaR uses persistent temporal state and subtracts expected endogenous effects, but its assumptions need testing with network incidents (Source: StaR, Sec. 3.3–3.4).

15. **How should graph state be updated when topology changes, telemetry is missing, or concept drift occurs?**
    Status: Open.

16. **Can a metric-variable candidate space be mapped safely to device/interface/link/module candidates?**
    Status: Open.

## Questions from CAUSALDX

17. **How can open-set candidate expansion find unknown network faults without overwhelming operators with unsupported hypotheses?**
    Status: Open.

18. **What independent observation or tool evidence is sufficient to verify a network root cause?**
    Status: Partially Answered. CAUSALDX makes verification a separate action and uses external/product tools, but its sufficiency criteria are domain-specific (Source: CAUSALDX, Sec. 4.3–4.4).

19. **How should anomaly dependency graphs preserve temporal order and evidence provenance?**
    Status: Open.

20. **Can root-set precision/recall and hierarchical top-k localization be evaluated together?**
    Status: Open.

## Questions from LLMGuard

21. **How can deterministic SOP execution represent continuous, uncertain, or contradictory network evidence?**
    Status: Open.

22. **How should an RCA system recognize that its SOP/knowledge coverage is insufficient for an unknown root cause?**
    Status: Partially Answered. LLMGuard escalates missing verified-tool coverage to a human, but a general unknown-cause detector remains open (Source: LLMGuard, Sec. IV-A–B).

23. **Which production metrics should be reported together with RCA correctness?**
    Status: Partially Answered. LLMGuard adds path length, latency, token cost, resource use, and human gating; a common network-AIOps protocol is still open (Source: LLMGuard, Sec. V).

24. **Can an executable SOP tree and a learned dynamic causal graph cooperate safely?**
    Status: Open.

## Questions from KAT

25. **How can a troubleshooting graph connect free-text errors with raw metrics, syslog, traces, traffic, and physical topology while preserving provenance?**
    Status: Open.

26. **How should stale or contradictory operational knowledge be detected before it changes an LLM diagnosis?**
    Status: Open.

27. **Can graph-grounded context retrieval improve root-node localization, not only semantic solution similarity?**
    Status: Open.

28. **What update and forgetting policy is appropriate when network error patterns or topology change?**
    Status: Open.

29. **How should user satisfaction and resolution-time improvements be separated from true root-cause correctness?**
    Status: Open.

## Questions from Comfey

30. **How should team ownership routing be separated from physical root-cause localization in network incidents?**
    Status: Partially Answered. Comfey makes team ownership its explicit target, while the existing RCA papers use component, metric-variable, anomaly-node, or SOP-leaf candidates; a network mapping remains open (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 4.5; [Root Cause Analysis concept](../../concepts/aiops/root-cause-analysis.md)).

31. **How should decentralized local agents share evidence without violating data sovereignty or duplicating noisy context?**
    Status: Open. Comfey passes structured enrichment and rejection rationale through the incident, but does not establish a general network telemetry provenance protocol (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 3.1–3.4).

32. **When should a historical routing table be invalidated after service, ownership, or topology changes?**
    Status: Open. Comfey refreshes historical data and permits TSG refinement, but a drift-detection or forgetting policy is not established (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 3.6–3.7).

33. **How much of a production triage improvement comes from LLM reasoning versus rules, retrieval, statistical routing, and parallel execution?**
    Status: Open. The paper reports component ablations but does not isolate the LLM contribution against all other system factors (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 4.6–4.9).

## Questions from AIM

34. **Can prompt-level alignment of metrics, logs, traces, and alerts preserve provenance when network telemetry is missing, delayed, or contradictory?**
    Status: Open. AIM filters missing timestamps and evaluates a controlled sample, but does not establish a network-specific alignment or conflict protocol (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 3.1, Sec. 6).

35. **Do root-cause category/text-alignment metrics measure physical RCA correctness?**
    Status: Partially Answered. AIM’s PA/TA scores measure alignment with predefined category labels and terminology; the paper does not define a physical root-node candidate space or causal verification protocol (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 4.4.3).

36. **What independent checks are needed before an LLM-generated mitigation plan becomes executable network action?**
    Status: Open. AIM checks YAML correctness and namespace consistency and reports execution outcomes, but does not provide a production safety, permission, rollback, or human-approval protocol (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 3.4, Sec. 4.4.6).

37. **How should plan quality, tool/code correctness, and actual remediation success be evaluated separately?**
    Status: Partially Answered. AIM reports language metrics, human judgments, TCR, data-collection success, and binary remediation success, but these remain difficult to compare across infrastructure domains (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 4.3–4.4.6).

## Questions from StepFly

38. **How can an executable TSG/DAG detect that it is out of coverage instead of reaching an inappropriate termination point?**
    Status: Open. StepFly can terminate at guide-defined points and send conclusions to SREs, but it does not establish a general unknown-fault detector (Source: [StepFly note](../../papers/aiops/stepfly/notes.md), Sec. 2.2, Sec. 4.4).

39. **How should structured working memory retain, compress, or forget large telemetry payloads across incident executions?**
    Status: Open. StepFly specifies key-value exchange within an execution, but not cross-incident retention, selection, forgetting, or memory correctness policies (Source: [StepFly note](../../papers/aiops/stepfly/notes.md), Sec. 4.4.4).

40. **When are TSG steps genuinely independent enough for parallel execution in changing network state?**
    Status: Partially Answered. StepFly uses data/control dependencies and SRE expertise to identify independent branches, but network rate limits, asynchronous observations, and state changes require further validation (Source: [StepFly note](../../papers/aiops/stepfly/notes.md), Sec. 4.5, Sec. 7).

41. **Can typed query plugins and DAG constraints improve open-set network RCA without freezing the system to outdated procedures?**
    Status: Open. StepFly reduces query-generation and control-flow errors, while its guide coverage and update boundaries remain a limitation (Source: [StepFly note](../../papers/aiops/stepfly/notes.md), Sec. 4.2–4.4, Sec. 6).

## Questions from TSGen

42. **How can a generated TSG distinguish a historically frequent pattern from a genuinely causal and currently valid root-cause path?**
    Status: Open. TSGen evaluates incident-discussion coverage, guide retrieval, human quality, and acceptance, but does not establish physical causal correctness for a new incident (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 5–6).

43. **How should network metrics, syslog, traces, traffic/NetFlow, topology, and incident text be aligned before generating troubleshooting knowledge?**
    Status: Open. TSGen currently processes text-centric incident records and identifies multimodal telemetry as future work; network-specific temporal and entity alignment is not addressed (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 6, Sec. 8.4).

44. **How should generated troubleshooting knowledge detect out-of-coverage or stale procedures after topology, configuration, or firmware changes?**
    Status: Open. The paper identifies stale medoid selection and external-validity risks, but does not provide a general coverage or freshness detector (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 4.5, Sec. 8.1, Sec. 8.4).

45. **What validation and provenance are required before a generated TSG is compiled into an executable Agent Skill or network remediation workflow?**
    Status: Open. Agent Skills are proposed as a downstream adaptation, while the reported system uses engineering review and publication rather than autonomous action validation (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 7.2–7.3).

46. **How should TSG versions, conflicting incident evidence, retention, and retirement be managed as operational knowledge rather than Agent memory?**
    Status: Open. TSGen updates guides incrementally and uses caches, but does not define a complete versioning, conflict-resolution, forgetting, or memory-read policy (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 4.5, Sec. 8.4).

## Questions from ChatRCA

47. **What is the minimum evidence for calling a role-specialized AIOps workflow genuinely multi-agent rather than a multi-role prompt around one model?**
    Status: Open. ChatRCA gives roles distinct prompts and capabilities and uses AutoGen communication, but the role ablations do not isolate independent-agent effects from added context and human intervention (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.1–4.2, Sec. 5.6).

48. **How should a network RCA workflow create a verifiable data ticket across metrics, syslog, traces, traffic/NetFlow, topology, and configuration?**
    Status: Open. ChatRCA validates a data ticket, but its D2 setting lacks traces and the paper does not define network-specific timestamp/entity alignment or provenance (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.2).

49. **How can multi-agent RCA detect open-set or multi-root incidents instead of forcing a closed root-cause category?**
    Status: Open. ChatRCA evaluates closed labeled categories and service/component candidates; it does not establish open-set or multi-root diagnosis (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 5.2–5.4).

50. **When should human consensus or arbitration be triggered in high-volume network operations?**
    Status: Partially Answered. ChatRCA places humans at data-ticket verification and root-cause adjudication and reports 14.38% arbitration across 146 cases, but it does not measure intervention time or define confidence/impact thresholds (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.8.3, Sec. 6).

51. **Does multi-agent role specialization remain beneficial after matching single-agent context, tool calls, token cost, and human review effort?**
    Status: Open. ChatRCA's role ablations show incremental task gains, but a compute-, context-, and intervention-matched comparison is not provided (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 5.6).

## Status after AIOps Knowledge Review v1

- **Candidate-space semantics:** Partially Answered. The batch shows at least five patterns—component hierarchy, metric variables, anomaly nodes, SOP leaves, and retrieved knowledge cases—but there is no common network candidate protocol.
- **Topology semantics:** Partially Answered. The papers distinguish service/call graphs, learned dynamic graphs, anomaly dependency graphs, SOP procedures, and TBSS subsystem graphs. Whether each is causal, predictive, or operational remains a per-system question.
- **Detection versus RCA:** Partially Answered. Several systems receive an incident, alert, or anomaly observation first; RCAgentBench and StaR make the downstream localization task explicit. A unified end-to-end protocol remains open.
- **LLM contribution:** Open. The batch shows gains associated with tools, knowledge, verification, and orchestration, but does not isolate LLM reasoning from those factors in a common experiment.
- **Production truth and evaluation:** Partially Answered. LLMGuard and KAT provide strong production evidence, while RCAgentBench and StaR provide controlled/public evaluation and CAUSALDX provides private production records; their labels and metrics remain non-comparable without task alignment.
- **Network-specific evidence:** Open. No Batch 1 paper establishes a complete RCA protocol over physical topology plus syslog, metrics, traffic/NetFlow, and device/interface/link ground truth.
- **Comfey triage boundary:** Partially Answered. Production incident ownership routing is a distinct upstream task; its strong triage and mitigation outcomes should not be reported as physical RCA correctness (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 4.3–4.5).

## Status after AIOps Knowledge Review v2

The following statuses summarize what Batch 2 answers for the current scope. Historical questions above are retained.

- **What should count as Agentic AIOps?**
  Status: **Partially Answered**. A working definition now requires a goal/task state, observations or feedback, bounded next-operation selection, and continuation, termination, or escalation; the threshold is not a field-wide standard (Source: [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 3).
- **Does multi-role orchestration equal Multi-Agent?**
  Status: **Partially Answered**. ChatRCA provides distinct role capabilities and communication, while StepFly’s Executors are homogeneous workers and AIM/TSGen are staged workflows; the independent benefit remains open (Source: [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.1–4.2; [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 9).
- **Is planning in Agentic AIOps different from workflow orchestration?**
  Status: **Partially Answered**. AIM has plan generation and StepFly has a guide-derived DAG, but Batch 2 does not demonstrate a general online Planner with robust replanning (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 3; [StepFly note](../../papers/aiops/stepfly/notes.md), Sec. 4.2–4.4).
- **What is the role of tools in incident investigation?**
  Status: **Partially Answered**. Tools collect telemetry, architecture, historical cases, or execute bounded actions; retrieval, observation, diagnosis, and remediation remain separate capabilities (Source: [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 6–7).
- **Are RAG and Knowledge Base the same as Agent Memory?**
  Status: **Partially Answered**. Batch 2 distinguishes RAG/operational knowledge/current context from memory with an explicit write, read, update, retention, and forgetting lifecycle; the lifecycle itself remains underspecified (Source: [TSGen note](../../papers/aiops/tsgen/notes.md), Sec. 7–8; [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2; [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 6).
- **Where should verification and human control appear?**
  Status: **Partially Answered**. Data completeness, high-impact diagnosis, state-changing action, recovery, and knowledge publication are plausible control points; confidence/impact thresholds and operational cost remain open (Source: [AIM note](../../papers/aiops/aim/notes.md), Sec. 3.4; [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.7–5.8).
- **Can these systems perform autonomous remediation?**
  Status: **Open**. AIM has constrained testbed execution, while the other Batch 2 workflows are routing, knowledge generation, diagnosis, or read-oriented investigation; no complete production repair/rollback/recovery loop is established (Source: [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 4, Sec. 7–8).
- **Do Agentic AIOps ideas transfer to physical Network AIOps?**
  Status: **Open**. Typed tools, evidence tickets, topology constraints, guide execution, and human gates appear transferable, but physical topology, traffic/NetFlow, open-set faults, and link/interface ground truth remain unvalidated (Source: [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 17).
- **How should Agentic AIOps be evaluated?**
  Status: **Partially Answered**. Evaluation should separate diagnosis/evidence/tool correctness, latency, cost, safety, human effort, remediation, and recovery; a common protocol is still missing (Source: [AIOps Knowledge Review v2](reviews/aiops-knowledge-review-v2.md), Sec. 10, Sec. 14).

## Status after Network AIOps Architecture Synthesis v1

- **What should the boundary be between telemetry algorithms and LLM/Agent RCA?**
  Status: **Partially Answered**. Deterministic/statistical/graph modules should enumerate, align, constrain, and verify; LLM/Agent modules can synthesize evidence and investigate within bounded tools. The optimal division is not yet experimentally established (Source: [Network AIOps Architecture Synthesis v1](reviews/network-aiops-architecture-synthesis-v1.md), Sec. 2–4).
- **How should a provenance-bearing Evidence Ticket be defined for network telemetry?**
  Status: **Open**. The current papers support data tickets, evidence chains, tool traces, and observation verification, but not a shared schema over physical network telemetry (Source: [Evidence Provenance concept](../../concepts/aiops/evidence-provenance.md), [Network AIOps Architecture Synthesis v1](reviews/network-aiops-architecture-synthesis-v1.md), Sec. 7).
- **Should physical topology be a hard constraint while dynamic dependency remains a soft prior?**
  Status: **Partially Answered**. This is the current design hypothesis; StaR supports stateful dynamic dependency and the other papers support distinct graph/context roles, but physical-network validation is still open (Source: [Topology-aware RCA concept](../../concepts/aiops/topology-aware-rca.md), [Network AIOps Architecture Synthesis v1](reviews/network-aiops-architecture-synthesis-v1.md), Sec. 6).
- **When does an AIOps task require an Agent loop rather than a fixed hybrid pipeline?**
  Status: **Partially Answered**. Observation-dependent tool choice, hypothesis testing, retry, escalation, or bounded replanning justify an Agent loop; one-shot normalized evidence does not. A reliable threshold remains open (Source: [Agentic Incident Management concept](../../concepts/aiops/agentic-incident-management.md), [Network AIOps Architecture Synthesis v1](reviews/network-aiops-architecture-synthesis-v1.md), Sec. 9).
- **How should RCA verification differ from remediation and recovery verification?**
  Status: **Partially Answered**. Candidate/evidence/topology checks are appropriate for RCA; permissions, rollback, execution feedback, and post-action telemetry are additionally required for remediation. A complete production protocol remains open (Source: [Network AIOps Architecture Synthesis v1](reviews/network-aiops-architecture-synthesis-v1.md), Sec. 11–13).

## Questions from Cloud-OpsBench

52. **How should a frozen network snapshot preserve entity, timestamp, freshness, and conflict provenance without making replay unrealistically clean?**
    Status: Open. Cloud-OpsBench freezes telemetry, configuration, and runtime state and returns deterministic tool observations, but does not define a physical-network provenance schema or live delay/permission model (Source: [Cloud-OpsBench note](../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.2–2.3).

53. **How should process-centric Agent evaluation handle multiple valid expert investigation paths?**
    Status: Open. Cloud-OpsBench proposes exact, in-order, and any-order trajectory measures, but a single expert-derived path may not represent all safe network investigations (Source: [Cloud-OpsBench note](../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.4).

54. **What controlled execution evidence is needed before a deterministic snapshot benchmark predicts production Agent behavior?**
    Status: Open. The paper establishes reproducible read-only evaluation, not production deployment, state-changing actions, or recovery outcomes (Source: [Cloud-OpsBench note](../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.3, Sec. 3–4).

## Questions from Cloud Intelligence/AIOps 2.0

55. **How should a Network Operational Knowledge Artifact anchor to a device, interface, link, path, or shared infrastructure alert?**
    Status: Open. Cloud Intelligence/AIOps 2.0 defines anchors conceptually around monitors and operational control points, but does not specify physical-network identity or topology changes (Source: [Cloud Intelligence note](../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.2).

56. **How can an OKA’s evidence preconditions be checked against delayed, missing, or contradictory network telemetry?**
    Status: Open. The paper requires explicit evidence and decision points, but does not provide a telemetry alignment or conflict-resolution algorithm (Source: [Cloud Intelligence note](../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.3, Sec. 4.1).

57. **What regression and drift tests are sufficient to retire or revise an operational procedure after topology, configuration, or firmware changes?**
    Status: Open. Versioning, validation status, drift signals, and regression checks are proposed governance requirements, not a measured protocol (Source: [Cloud Intelligence note](../../papers/aiops/cloud-intelligence/notes.md), Sec. 2.3, Sec. 4.1–4.3).

## Questions from CHIEF

58. **How should a Network RCA candidate hierarchy combine device/interface/module ownership with link/path relationships?**
    Status: Open. CHIEF demonstrates subtask → Agent → step narrowing for execution traces, but its hierarchy is not a physical network candidate space (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 4.1–4.2).

59. **How can open-set and multi-root network faults be represented when no single observed candidate explains the incident?**
    Status: Open. CHIEF defines an earliest single decisive error and lists cumulative deviations as future work; it does not establish open-set or multi-root attribution (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 3, Sec. 7).

60. **What is a safe network analogue of counterfactual correction for testing whether a candidate is causally decisive?**
    Status: Open. CHIEF uses counterfactual trajectory correction in an Agent benchmark, while applying an intervention to a live network fault may be unsafe or unavailable (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 3, Sec. 4.3).

61. **How can hallucinated graph edges or virtual-oracle expectations be detected before they affect RCA ranking?**
    Status: Open. CHIEF explicitly identifies HCG/oracle fidelity as a limitation; deterministic topology and independent telemetry checks are not supplied by the paper (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 7).

## Questions from FlowFixer

62. **What network behavioral specification is precise enough to validate a configuration change without pretending to model every physical effect?**
    Status: Open. FlowFixer uses inferred workflow assertions and semantic/structural checks, but does not model physical network behavior or vendor-specific safety constraints (Source: [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. III).

63. **What independent recovery signal should determine whether an executed network remediation succeeded?**
    Status: Open. FlowFixer dynamically reruns a workflow on test inputs, but does not provide post-action network recovery verification or rollback (Source: [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. III-D–III-E; Sec. VIII).

64. **How should repair experience be invalidated when topology, firmware, configuration, or tool semantics change?**
    Status: Open. FlowFixer’s ExperiencePool retrieves historical repair experience, but a complete freshness, conflict, and retirement policy is not established (Source: [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. III-E).

65. **How should a repair verifier handle open-set, multi-root, or partial-repair failures?**
    Status: Open. FlowFixer evaluates a finite workflow taxonomy and responsible node, without establishing unknown-cause or multi-root repair attribution (Source: [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. IV).

## Status after AIOps Knowledge Review v3

The following summary updates the current state without deleting the paper-specific question history above:

- **What is auditable RCA evidence?** Status: **Partially Answered.** Snapshots, OKA identity, Agent traces, workflow traces, data tickets, and evidence chains provide related pieces, but no shared network Evidence Ticket covers source, entity, time, transformation, conflict, candidate relation, and re-query semantics.
- **How should Network RCA candidate space be defined?** Status: **Partially Answered.** CHIEF demonstrates explicit hierarchical candidate reduction and FlowFixer demonstrates node/category alignment; physical network hierarchy, pruning recall, and ground-truth mapping remain open.
- **Can current methods handle open-set and multi-root RCA?** Status: **Open.** CHIEF focuses an earliest single decisive root and FlowFixer uses a finite workflow taxonomy; neither establishes network unknown/multi-root handling.
- **What does verification verify?** Status: **Partially Answered.** Current papers verify process behavior, graph/oracle consistency, candidate observations, workflow patches, and human decisions at different layers; a unified physical RCA-to-recovery protocol is absent.
- **Is repair validation the same as recovery verification?** Status: **Partially Answered.** FlowFixer separates pre-checks and dynamic workflow execution, strengthening the distinction; independent post-action network recovery and rollback remain open.
- **Which Hybrid RCA layer is weakest?** Status: **Partially Answered.** The missing end-to-end interface from provenance-bearing physical-network evidence through candidate-constrained diagnosis to safe, human-gated, independently verified recovery is now the clearest gap for the current scope.
- **How should benchmark success be measured?** Status: **Partially Answered.** Process, candidate, evidence, tool, diagnosis, action, cost, human, and recovery dimensions are identifiable, but no common Network AIOps protocol has been established.
