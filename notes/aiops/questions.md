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

## Status after AIOps Knowledge Review v1

- **Candidate-space semantics:** Partially Answered. The batch shows at least five patterns—component hierarchy, metric variables, anomaly nodes, SOP leaves, and retrieved knowledge cases—but there is no common network candidate protocol.
- **Topology semantics:** Partially Answered. The papers distinguish service/call graphs, learned dynamic graphs, anomaly dependency graphs, SOP procedures, and TBSS subsystem graphs. Whether each is causal, predictive, or operational remains a per-system question.
- **Detection versus RCA:** Partially Answered. Several systems receive an incident, alert, or anomaly observation first; RCAgentBench and StaR make the downstream localization task explicit. A unified end-to-end protocol remains open.
- **LLM contribution:** Open. The batch shows gains associated with tools, knowledge, verification, and orchestration, but does not isolate LLM reasoning from those factors in a common experiment.
- **Production truth and evaluation:** Partially Answered. LLMGuard and KAT provide strong production evidence, while RCAgentBench and StaR provide controlled/public evaluation and CAUSALDX provides private production records; their labels and metrics remain non-comparable without task alignment.
- **Network-specific evidence:** Open. No Batch 1 paper establishes a complete RCA protocol over physical topology plus syslog, metrics, traffic/NetFlow, and device/interface/link ground truth.
- **Comfey triage boundary:** Partially Answered. Production incident ownership routing is a distinct upstream task; its strong triage and mitigation outcomes should not be reported as physical RCA correctness (Source: [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 4.3–4.5).
