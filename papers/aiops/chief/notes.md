Status: Full Reading: Completed

# From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems

## 1. Metadata

- Title: From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems
- Authors: Yawen Wang, Wenjie Wu, Junjie Wang, Qing Wang
- Year: 2026
- Venue: arXiv preprint, arXiv:2602.23701v1
- URL / DOI: https://arxiv.org/abs/2602.23701
- Local File: [CHIEF PDF](<../../../sources/papers/AIOps_papers/From_flat_logs_to_causal_graphs_Hierarchical_failure_attribution_for_llm-based_multi-agent_systems.pdf>)
- Paper ID: `chief`

## 2. One-Sentence Summary

CHIEF converts failed multi-agent execution logs into a hierarchical graph, uses subtask-specific virtual oracles and coarse-to-fine backtracking to shrink the agent-step candidate space, and applies counterfactual attribution to identify the earliest decisive failure.

## 3. Problem Setting

### Paper states

The paper studies failures in LLM-based multi-agent systems (MAS), where a flat execution log can contain many observations, thoughts, actions, tool results, inter-agent messages, and downstream errors. The goal is to answer both **who** caused the failure and **when** in the trajectory the decisive failure occurred (Source: Abstract; Sec. 1; Sec. 3).

CHIEF is an offline failure-attribution method. It does not diagnose a live cloud or network incident, and it does not propose an AIOps telemetry detector or a remediation executor (Source: Sec. 3–6).

### My interpretation

The main contribution is to the candidate-space and attribution layers of the Hybrid RCA architecture for Agent systems. It makes the candidate explicit as an agent-step pair, reduces it hierarchically, and tests responsibility with counterfactual reasoning. The graph is useful for execution-trace causality, but it must not be reinterpreted as a physical network causal graph.

## 4. AIOps Task

- Detection: No.
- Anomaly Detection: No.
- Incident Detection: No. A failed trajectory is supplied.
- Localization: **Yes, at Agent and step granularity.**
- Root Cause Analysis: **Yes, for a single decisive failure in an LLM-based MAS trajectory.**
- Diagnosis: **Yes, as failure attribution and planning/control/data-flow responsibility analysis.**
- Classification: **Partly.** The method classifies responsibility patterns such as upstream/local, planner/executor, or data-flow corruption, but it is not a general fault-type classifier.
- Explanation: **Yes, through the hierarchical graph, oracle evidence, and attribution rationale.**
- Prediction: No.
- Remediation: No.
- Recovery Verification: No.
- Incident Management: No; the setting is Agent-system failure analysis rather than operational incident response.
- Knowledge Update: The method retrieves examples to build decomposition/oracle context, but does not define a production knowledge-update lifecycle.

The task boundary is:

```text
failed MAS trajectory
→ structured execution graph
→ hierarchical candidate backtracking
→ counterfactual responsibility attribution
→ faulty agent and decisive step
```

It should not be reported as online Network RCA, even though its terminology uses failure attribution and causal graphs.

## 5. Failure / Incident Setting

The failures come from the Who&When benchmark for LLM-based multi-agent systems. The paper uses two sources: 126 algorithm-generated failure logs from 126 diverse architectures built with CaptainAgent, and 58 hand-crafted failure logs from Magnetic-One, for a total of 184 failure logs. Human experts provide multi-round consensus annotations (Source: Sec. 5.1).

These are Agent-trajectory failures, not infrastructure incidents. The paper does not establish production deployment, real network faults, real telemetry, or operator repair records.

## 6. Data Modalities

- Metrics: No.
- Logs: **Yes, in the sense of Agent execution logs and failure trajectories.**
- Traces / Spans: **Yes, as ordered Agent-step trajectories, not distributed-service traces.**
- Alerts: No.
- Events: **Partly.** Agent actions, observations, results, and inter-agent messages are event-like records.
- Topology: **Yes, as an execution structure.** The hierarchical causal graph has subtask, agent, and step nodes/edges; it is not physical infrastructure topology (Source: Sec. 4.1).
- Configuration: **Partly.** Task/Agent architecture and behavior context are present; a network or service configuration stream is not used.
- Traffic: No.
- NetFlow: No.
- Packets: No.
- Tickets: No.
- Text / Documents: **Yes.** Task descriptions, prompt content, and retrieved examples are used.
- Knowledge Graph: No explicit operational knowledge graph. A RAG knowledge base supplies task-decomposition examples (Source: Appendix A).
- SOP: **Partly.** Virtual oracles contain subtask goals, preconditions, key evidence, and acceptance criteria, but they are diagnostic specifications rather than operational SOPs.
- Historical Incidents: No; the benchmark contains failed Agent trajectories.
- Other: OTAR records—Observation, Thought, Action, Result—and inter-agent communication.

**Multi-source execution trace, not multimodal telemetry fusion.** The method combines structured and textual elements of an Agent trajectory. It does not perform metrics/logs/traces feature fusion or multimodal network evidence alignment.

## 7. Dataset and System Setting

- Public / Private: **A public Who&When benchmark is used according to the paper; exact release scope is not independently checked beyond the local paper.**
- Production / Synthetic: **Benchmark failures from algorithm-generated and hand-crafted Agent trajectories; not production infrastructure incidents.**
- Observation duration: Per-trajectory step sequence; wall-clock incident windows are not applicable.
- Number of incidents: 184 failure logs: 126 algorithm-generated and 58 hand-crafted (Source: Sec. 5.1).
- Number of devices / services / nodes: Not applicable; the relevant entities are MAS subtasks, Agents, and execution steps.
- Topology: Hierarchical execution graph plus inter-agent/data-flow edges; no physical network topology.
- Production dataset: No evidence established.
- Production-scale evaluation: No.
- Production deployment: No.
- Benchmark architectures: 126 diverse algorithm-generated architectures plus Magnetic-One hand-crafted cases; details vary by benchmark subset (Source: Sec. 5.1).

## 8. Core Method

### Formal failure target

The paper models an MAS as `M = <N, S, A, P>`, where agents operate over states, actions, and policies. A trajectory is represented as ordered agent-step events. For a candidate pair `(i, t)`, the method considers a counterfactual trajectory in which the decisive error at that pair is corrected. The indicator `δ(i,t)` is positive when correcting the candidate changes the final outcome from failure to success. The root cause is defined as the earliest decisive error among such candidates (Source: Sec. 3).

This formalization makes an important assumption explicit: the target is a **single decisive root** under the paper’s counterfactual criterion. It does not establish multi-root attribution.

### Hierarchical Causal Graph (HCG)

CHIEF constructs a graph with:

- `SubtaskNode` nodes describing decomposed subtasks;
- `AgentNode` nodes for the agents involved; and
- step-level nodes representing concrete behavior.

Subtask edges, agent/inter-agent edges, and step/data-flow edges organize task structure, communication, and execution dependencies. Agent behavior is normalized to OTAR: Observation, Thought, Action, and Result (Source: Sec. 4.1; Appendix B–C).

Task decomposition is generated with retrieved examples from GAIA and AssistantBench. A trajectory-aligned reflection step checks whether generated subtask ranges agree with the raw log. This use of reflection is a graph/specification construction check, not a cross-attempt Agent memory loop (Source: Sec. 4.1; Appendix A).

### Virtual oracles

For each subtask, CHIEF generates a virtual oracle:

```text
Oracle = Goal + Preconditions + KeyEvidence + AcceptanceCriteria
```

The oracle is synthesized from the task, previous oracles, later unprocessed trajectory content, and retrieved examples, then subjected to consistency checks. It provides local expectations against which Agent and step behavior can be compared (Source: Sec. 4.2; Appendix D).

### Hierarchical backtracking and attribution

The method first evaluates subtask candidates in reverse topological order, then narrows to Agent candidates, and finally to step candidates. Semantic matching against oracle preconditions, key evidence, and acceptance criteria prunes the scope. Counterfactual attribution then distinguishes:

- local versus upstream responsibility;
- planner/control responsibility versus executor responsibility;
- data-flow corruption; and
- recoverable deviations versus the later irrecoverable point.

The resulting output is a single faulty Agent-step pair, with attribution category and supporting graph/oracle reasoning (Source: Sec. 4.2–4.3; Appendix E–F).

## 9. Architecture / Workflow

The actual offline pipeline is:

```text
Failed MAS trajectory
→ task decomposition and HCG construction
→ OTAR parsing and subtask/agent/step edges
→ subtask virtual-oracle generation
→ reverse-topological hierarchical backtracking
→ candidate Agent/step narrowing
→ counterfactual and deviation-aware attribution
→ faulty Agent + decisive step
```

There is no live:

```text
tool invocation → environment observation → next action
```

loop in the CHIEF system itself. The observations and actions are historical records being analyzed. Therefore, the HCG’s `Observation` node is evidence in an offline trace, not a newly acquired environment Observation.

## 10. Detection Method

No detection model is evaluated. The input is already a failed trajectory. The method detects/attributes a decisive error retrospectively, but this should not be confused with detecting an infrastructure incident or detecting an anomaly in raw telemetry.

## 11. RCA / Localization Method

CHIEF’s RCA-like task is failure attribution over Agent-step candidates:

```text
flat failed log
→ hierarchical execution representation
→ oracle-based candidate pruning
→ counterfactual responsibility check
→ earliest decisive Agent-step root
```

### Candidate space

The candidate is explicitly `(agent, step)`. The implicit universe contains the Agent-step events in the failed trajectory; the paper does not give one fixed numeric candidate count across all 184 logs. It does not search all possible infrastructure components or fault classes.

Candidate pruning is explicit and hierarchical:

```text
all relevant subtasks
→ suspicious subtasks
→ suspicious Agents
→ suspicious steps
→ decisive Agent-step pair
```

The hierarchy is an execution/task hierarchy, not a physical network or fault taxonomy. It reduces reasoning scope and makes responsibility attribution more tractable, but it does not by itself prove that the graph edges are physical causal edges.

### Open-set and multi-root status

- Open-set unknown failure: **Not established.** The output is constrained to a trajectory candidate and benchmark annotation setting.
- Multiple simultaneous roots: **Not supported by the stated root definition.** The paper focuses on the earliest single decisive error; cumulative minor deviations are listed as future work (Source: Sec. 7).
- Ground-truth granularity: Agent and exact step, aligned with the candidate output.

## 12. Diagnosis / Classification Method

The method diagnoses responsibility through four attribution perspectives:

1. **Local attribution:** distinguish a local error from an upstream error that contaminated the current step.
2. **Planning-control attribution:** attribute repeated semantically equivalent decisions despite error signals to a planner/control component, or abnormal execution after a valid strategy shift to an executor.
3. **Data-flow attribution:** identify the earliest step that corrupts data needed by downstream steps.
4. **Deviation-aware attribution:** give minimal or no responsibility to deviations that are later self-corrected, and select the later irrecoverable point when appropriate (Source: Sec. 4.3; Appendix F).

These categories are useful for Agent reliability analysis. They are not a general operational fault taxonomy, and they do not directly classify network faults such as link failure, optical degradation, or routing misconfiguration.

## 13. LLM / Agent Role

- LLM used: **Yes.** DeepSeek-V3.2 thinking is the base model in the reported implementation; LLMs generate task decompositions, parse behavior, synthesize virtual oracles, evaluate candidates, and support attribution (Source: Sec. 5.4; Sec. 4; Appendices A–E).
- Tool use: **No operational tool execution.** The method uses a RAG knowledge base for retrieved task-decomposition examples, but it does not query telemetry or change an environment (Source: Appendix A).
- Multi-step interaction: **Offline multi-stage analysis, not live Agent interaction.**
- Observation: **Historical OTAR observation records.**
- Autonomous next-action selection: No.
- Planning: **Analyzed as a failure responsibility category.** CHIEF does not introduce a runtime planner that executes a plan.
- Replanning: No.
- Memory: Previous virtual oracles are supplied sequentially as “internal memory” in the oracle prompt, but this is bounded analysis context, not a demonstrated persistent or long-term Agent memory (Source: Appendix D).
- Feedback loop: **Counterfactual and consistency checks over a recorded trajectory; no live repair feedback loop.**
- Environment interaction: No.
- Verification: **Yes, in the attribution sense.** Oracle consistency, hierarchical checks, and counterfactual analysis test responsibility; they do not verify physical operational state.
- Human gate: Human consensus provides benchmark annotation; no runtime human approval loop is implemented.

**Paper terminology:** hierarchical causal graph, virtual oracle, hierarchical failure attribution, counterfactual attribution.

**Knowledge-base interpretation:** CHIEF is an LLM-assisted offline Agent-trace attribution system. It has a structured candidate and verification procedure, but it is not an online Agentic AIOps workflow and should not be classified as a network RCA Agent merely because it uses “causal” graphs and multi-agent logs.

## 14. Ground Truth

The Who&When benchmark supplies expert annotations produced through multi-round human consensus. The paper’s formal criterion defines a root as the earliest decisive error whose correction changes the counterfactual outcome to success. The output is evaluated at Agent level and exact step level (Source: Sec. 3; Sec. 5.1–5.3).

The ground-truth unit is therefore:

```text
one Agent + one exact trajectory step
```

not a device, service, metric, time interval, or physical root cause. The paper’s use of corrected counterfactual outcomes should be read within the MAS benchmark setting and not assumed to be available for live network incidents.

## 15. Baselines

CHIEF is compared with:

- Random;
- All-at-once;
- Step-by-step;
- BinarySearch;
- ECHO;
- FAMAS; and
- AgenTracer / GraphTracer.

These cover random, sequential, binary-search, and prior trace/graph attribution strategies (Source: Sec. 5.2). The paper also reports ablations of its own modules: HCG alone, HCG plus oracle/backtracking, HCG plus counterfactual attribution, and the full method (Source: Sec. 6.4, Table 4).

## 16. Metrics

- **Agent-level accuracy:** whether the responsible Agent is identified correctly.
- **Exact step-level accuracy:** whether the exact responsible Agent-step pair is identified correctly.
- **Top-1 setting:** the reported outputs are single best attributions, not a network-style Top-k root ranking.
- **Token cost:** reported separately to expose analysis cost; it is not a correctness metric (Source: Sec. 5.3; Table 2).

These metrics fit the paper’s Who&When task, but do not measure tool correctness, evidence provenance completeness, operational latency, repair safety, recovery, or human effort in a production RCA setting.

## 17. Main Results

On the hand-crafted subset, CHIEF with access to task ground truth (`w/G`) reports **77.59% Agent-level accuracy** and **29.31% exact step-level accuracy**; without that access (`w/o G`) it reports **72.41%** and **29.31%**, respectively. On the algorithm-generated subset, it reports **76.80% / 52.00%** with ground-truth access and **68.80% / 45.60%** without it (Source: Table 1, Sec. 6.1).

The paper reports that CHIEF outperforms the listed baselines overall, with one minor exception in the detailed comparison. The gap between Agent-level and exact step-level accuracy shows that identifying the responsible Agent is materially easier than locating the decisive step (Source: Sec. 6.1; Table 1).

The ablation in Table 4 supports complementary roles for the modules: HCG alone can overload attribution, hierarchical oracle/backtracking prunes the search, and counterfactual attribution improves responsibility checking. The full system reports the same headline values above; the ablation demonstrates component contribution within this benchmark rather than general network RCA validity (Source: Sec. 6.4; Table 4).

The paper reports token cost of about **55,085** for hand-crafted cases and **19,504** for algorithm-generated cases in the ground-truth-access condition (Source: Table 2). This reinforces that structured narrowing has an efficiency dimension, though the paper does not provide a production cost/latency protocol.

## 18. Scalability / Deployment

- Benchmark scale: 184 failed trajectories from two benchmark sources (Source: Sec. 5.1).
- Production dataset: No evidence established.
- Production-scale evaluation: No.
- Production deployment: No.
- Physical infrastructure scale: Not applicable.

The method may reduce the number of candidate steps considered in a long Agent trace, but the paper does not evaluate very long online traces, high-throughput incident streams, physical network topology, or concurrent multi-root failures.

## 19. Strengths

- Defines the output candidate precisely as an Agent-step pair.
- Uses a hierarchical representation to avoid treating every log event as an equally likely root.
- Separates task/Agent/step structure from local, planning-control, and data-flow attribution.
- Uses virtual-oracle expectations and counterfactual logic instead of only asking an LLM to summarize a failed trace.
- Reports both agent-level and exact-step correctness, ablations, and token cost.
- Provides appendix prompts and formal details that make the attribution procedure inspectable.

## 20. Limitations

### Paper states

The method depends on the fidelity of the HCG and virtual oracles; hallucinated graph edges or incorrect oracles can propagate errors. The evaluation uses only the Who&When public benchmark and focuses on a single decisive root, leaving cumulative minor deviations for future work (Source: Sec. 7).

### Current interpretation

- The “causal graph” is a structured execution/dependency graph combined with counterfactual attribution. It is not evidence of physical causality in a network.
- Ground-truth access (`w/G`) provides a useful ablation but is not available in a live incident; results with and without it should remain distinct.
- Exact step accuracy is low relative to Agent accuracy in the reported subsets, indicating that coarse localization can conceal uncertainty about the decisive event.
- The method assumes a failure can be attributed to a candidate in the recorded trajectory; open-set causes outside the trajectory and simultaneous independent roots are not established.

## 21. Reproducibility

- Code available: **A repository link is reported by the paper; release completeness is not independently checked here.**
- Dataset available: **Who&When is treated as a public benchmark in the paper; exact release contents are not re-verified here.**
- Benchmark available: Yes, through Who&When as described.
- Prompt available: **Partly.** Appendices provide prompts for OTAR parsing, edge construction, oracle generation, and backtracking.
- Tools described: RAG/example retrieval and LLM analysis; no operational tools.
- Model/API specified: **Yes.** DeepSeek-V3.2 thinking is reported for implementation.
- Hyperparameters available: **Partly.** The paper provides implementation details, but LLM-dependent prompts and generation behavior remain sensitive.
- Fault injection available: Not applicable.
- Reproducibility: **Medium.** The benchmark, formal definitions, prompts, model, baselines, and ablations are described, but graph/oracle generation is LLM-dependent and the use of ground-truth context materially changes the setting.

## 22. Relationship to Existing AIOps Knowledge

CHIEF adds a distinct candidate-space pattern to [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md): the candidate is not a service or metric but an Agent-step pair, and a hierarchy narrows from subtask to Agent to step before final attribution. It complements [RCAgentBench](../rcagentbench/notes.md), which evaluates multimodal operational diagnosis processes, but CHIEF diagnoses the Agent workflow itself rather than the infrastructure.

The HCG is related to [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md) only at the level of structural reasoning. Its subtask/agent/step edges are execution and data-flow relations; they are not physical topology, and the counterfactual attribution does not establish device/link causality.

CHIEF also strengthens the cross-paper need for an explicit [Candidate Space](../../../concepts/aiops/candidate-space.md): RCA evaluation is meaningful only after specifying candidate entities, granularity, pruning, root multiplicity, and ground-truth alignment. Its oracle and OTAR records are also relevant to [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md), but they are provenance for Agent traces rather than for network telemetry.

Related concepts:

- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Candidate Space](../../../concepts/aiops/candidate-space.md)
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md)
- [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md)
- [Agent](../../../concepts/agent.md)
- [Reasoning](../../../concepts/reasoning.md)
- [Planning](../../../concepts/planning.md)
- [Reflection](../../../concepts/reflection.md)

## 23. Relevance to My Research

### Similarities

The paper addresses a large structured attribution space, noisy/flat execution records, hierarchical narrowing, data-flow relationships, and verification of a proposed root. These are method-level parallels to Network RCA, where candidate entities and evidence chains also need explicit structure.

### Differences

CHIEF works on failed LLM multi-agent trajectories. Its candidate is an Agent-step pair, its graph is an execution graph, and its ground truth is a single decisive step. The current research concerns network devices, interfaces, links, optical modules, physical topology, metrics, syslog, traffic/NetFlow, configuration, and possibly multiple physical causes.

### Potentially Useful Ideas

- Define a hierarchy over network candidates, for example device → interface/module and path → link, before fine-grained attribution.
- Separate coarse candidate narrowing from fine-grained evidence verification.
- Represent candidate expectations with explicit preconditions, key evidence, and acceptance criteria.
- Use counterfactual or intervention-inspired checks where a controlled observation can test whether a candidate explains the incident.
- Track upstream/downstream data-flow responsibility rather than assigning every correlated symptom equal root status.

### Assumptions That May Not Transfer

- A single decisive root may not fit cascading, multi-root, or slowly evolving network faults.
- The network candidate universe may contain causes not present in the observed trajectory, unlike a trace-attribution task.
- LLM-generated graphs/oracles can hallucinate relationships; physical topology and deterministic telemetry should not be replaced by them.
- Correcting a network fault counterfactually is often unsafe or impossible to test directly.

### Experiments Worth Considering

- Compare flat candidate ranking with coarse-to-fine device/interface/link/module hierarchy.
- Measure whether candidate granularity aligned to ground truth changes Top-k RCA conclusions.
- Test physical-topology constraints and dynamic dependency evidence separately and together.
- Evaluate single-root versus multi-root and unknown-root cases with explicit abstention.
- Use independent re-query or controlled testbed evidence to validate candidates rather than relying on LLM-generated counterfactual narratives.

### Transferability to Network AIOps

**Medium.** The hierarchical candidate/pruning and attribution ideas are transferable; the graph semantics, counterfactual assumptions, telemetry modalities, and root-label granularity require a network-specific redesign.

## 24. My Understanding

CHIEF’s key lesson is that “find the cause in a long trace” is partly a candidate-space problem. It does not ask an LLM to judge every event at once. It first builds a structured execution graph, derives local expectations, narrows the search from coarse to fine, and then asks whether correcting a candidate would change the failure outcome.

For Network RCA, the transferable abstraction is:

```text
large structured candidate universe
→ hierarchy / constraints
→ smaller candidate set
→ evidence and counterfactual verification
```

The non-transferable shortcut would be to call the HCG a physical causal graph or to assume that one Agent-step root maps directly to one network root. CHIEF strengthens the need for explicit candidate definitions, but leaves open-set, multi-root, live verification, and physical causal semantics unresolved.

## 25. Questions

- How should a network candidate hierarchy combine device/interface/module ownership with link/path relationships?
- How can open-set and multi-root network faults be represented when no candidate appears in the observed trajectory?
- What is a safe network analogue of CHIEF’s counterfactual correction test?
- How can graph/oracle hallucinations be detected before they influence RCA ranking?
- How should Top-k evaluation handle candidates at different hierarchy levels?

## 26. Source Grounding

- Failure-attribution problem, trajectory model, decisive-error/root definition: Sec. 3, pp. 3–4.
- HCG construction, task decomposition, OTAR parsing, and edge semantics: Sec. 4.1, pp. 4–6; Appendices A–C.
- Virtual-oracle structure and hierarchical backtracking: Sec. 4.2, pp. 6–8; Appendices D–E.
- Counterfactual, planning-control, data-flow, and deviation-aware attribution: Sec. 4.3, pp. 8–10; Appendix F.
- Who&When data and benchmark construction: Sec. 5.1, p. 10.
- Baselines, metrics, implementation, and token-cost setup: Sec. 5.2–5.4, pp. 10–11.
- Main comparison and reported accuracy values: Sec. 6.1, Table 1, p. 11.
- Token cost: Sec. 6.2, Table 2, p. 12.
- Ablation and module contribution: Sec. 6.4, Table 4, p. 13.
- Limitations—oracle/graph fidelity, single benchmark, single decisive root: Sec. 7, p. 14.

## 27. Tags

`AIOps` `Agent-reliability` `failure-attribution` `candidate-space` `hierarchical-reasoning` `causal-graph` `counterfactual` `multi-agent` `RCA` `Network-AIOps`
