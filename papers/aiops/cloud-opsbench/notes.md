Status: Full Reading: Completed

# Freezing the Crime Scene: A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation

## 1. Metadata

- Title: Freezing the Crime Scene: A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation
- Authors: Guangba Yu, Yilun Wang, Michael R. Lyu
- Year: 2026
- Venue: FSE Companion 2026
- URL / DOI: https://doi.org/10.1145/3803437.3806092
- Local File: [Cloud-OpsBench PDF](<../../../sources/papers/AIOps_papers/FSE26-Freezing the Crime Scene- A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation.pdf>)
- Paper ID: `cloud-opsbench`

## 2. One-Sentence Summary

Cloud-OpsBench proposes freezing cloud operational state into a deterministic snapshot with a mocked operational interface so Agentic SRE systems can be evaluated on both diagnostic outcomes and the quality of their investigation trajectories.

## 3. Problem Setting

### Paper states

The paper identifies a tension between ecological validity and reproducibility. Static telemetry benchmarks remove the interactive information-seeking part of SRE work, while live-cluster evaluations expose agents to stochastic runtime effects such as network jitter, self-healing, and deployment overhead. Outcome-only metrics can also reward an agent that reaches the correct answer through unsupported reasoning (Source: Sec. 1.1–1.3, pp. 1–2).

The proposed State Snapshot Paradigm separates a frozen operational state from the runtime that executes diagnostic commands. It is intended as an evaluation infrastructure and a prototype direction, not as a new RCA algorithm (Source: Sec. 1.3; Sec. 2, pp. 2–3).

### My interpretation

Cloud-OpsBench addresses the evaluation layer of the Hybrid RCA architecture. Its central question is: can a diagnostic Agent acquire and use evidence through operational interfaces in a reproducible way, and can the process be judged rather than only its final text? It does not establish a general network RCA method or a production remediation system.

## 4. AIOps Task

- Detection: **Not the primary task.** Fault injection is monitored to confirm that an intended anomaly has manifested before the snapshot is taken, but the benchmark does not evaluate an independent detector (Source: Sec. 2.1, p. 2).
- Anomaly Detection: **Scenario construction only.** Closed-loop telemetry monitoring verifies the injected symptom; it is not the agent task (Source: Sec. 2.1).
- Incident Detection: No.
- Localization: **Evaluation target.** The agent investigation is expected to locate or diagnose the incident, but the paper does not define a complete location-prediction algorithm or a universal root-label schema (Source: Sec. 2.4, pp. 3–4).
- Root Cause Analysis: **Yes, as a process-evaluation target.** The expert trajectory is reverse-engineered from the causal logic of the injected fault, and the agent trajectory is compared with it (Source: Sec. 2.4).
- Diagnosis: **Yes, as the operational behavior being evaluated.** The paper evaluates evidence-seeking and diagnostic procedure rather than proposing the diagnosis model itself.
- Classification: No standalone fault-classification task is specified.
- Explanation: **Indirectly.** The trajectory of Thoughts, Actions, and Observations is assessed; a separate natural-language explanation score is not defined.
- Prediction: No.
- Remediation: **No.** The mocked interface is explicitly read-only and the paper concerns fault diagnosis/evaluation, not state-changing repair (Source: Sec. 2.3, p. 3).
- Recovery Verification: No.
- Incident Management: **Only as an evaluation context for SRE diagnosis.**
- Knowledge Update: Future roadmap only; golden trajectories may later support fine-tuning or reinforcement learning, but those experiments are not reported (Source: Sec. 3, p. 4).

The task boundary is therefore:

```text
injected failure
→ reproducible operational state
→ interactive evidence gathering
→ trajectory/process evaluation
```

It should not be reported as an end-to-end detection, RCA, and remediation system.

## 5. Failure / Incident Setting

The proposed benchmark uses knowledge-driven fault injection. Unstructured sources such as issue reports or Stack Overflow material are translated into executable fault-reproduction plans. A closed-loop monitor checks that the injected fault produces an observable anomaly before the state is frozen, which is intended to avoid cases masked by self-healing systems such as Kubernetes rescheduling (Source: Sec. 2.1, p. 2).

The incidents are simulated or injected cloud-native failures. The paper does not claim that Cloud-OpsBench is deployed in a live production environment, and it does not evaluate historical operator-confirmed network incidents.

## 6. Data Modalities

- Metrics: **Yes.** Historical time-series telemetry leading to the failure is included in the snapshot (Source: Sec. 2.2, p. 3).
- Logs: **Yes.** Historical logs leading to failure are included (Source: Sec. 2.2).
- Traces / Spans: **Unclear / Not explicitly stated in the paper.**
- Alerts: **Unclear / Not explicitly stated.**
- Events: **Unclear / Not explicitly stated.**
- Topology: **Not explicitly specified as a separately modeled topology.** The setting is Kubernetes/cloud-native and the runtime state can contain object relationships, but a physical or dependency-graph RCA method is not defined.
- Configuration: **Yes.** Control-plane configuration such as Kubernetes manifests is frozen (Source: Sec. 2.2).
- Traffic: No explicit traffic telemetry.
- NetFlow: No.
- Packets: No.
- Tickets: Source material may guide fault injection, but tickets are not the evaluated telemetry modality.
- Text / Documents: **Yes, for knowledge-driven fault injection and knowledge context.**
- Knowledge Graph: No explicit knowledge graph.
- SOP: **Yes, as expert diagnostic ground truth.** The canonical trajectory is derived from the causal logic of the injection and represents a standard operating procedure (Source: Sec. 2.4).
- Historical Incidents: **Not established as the benchmark data source.**
- Other: Instantaneous data-plane state, such as pod lists and conditions, and pre-recorded tool responses (Source: Sec. 2.2–2.3).

**Multi-source operational state, but not feature-level multimodal fusion.** The paper combines telemetry, control-plane configuration, and instantaneous runtime state in an immutable snapshot. It does not propose early, representation, or late fusion of metrics/logs/traces for an RCA model; the agent integrates the sources through tool queries and context.

## 7. Dataset and System Setting

- Public / Private: **Unclear / Not explicitly stated for a released benchmark dataset.** The paper presents the Cloud-OpsBench initiative and a prototype direction; a complete public incident corpus is not established in the local paper.
- Production / Synthetic: **Prototype/testbed with knowledge-driven injected faults.**
- Observation duration: A frozen spatio-temporal window includes a failure-time state and a lookback interval, but the exact standard duration is **Unclear / Not explicitly stated** (Source: Sec. 2.2, p. 3).
- Number of incidents: **Unclear / Not explicitly stated in this five-page paper.**
- Number of devices / services / nodes: **Unclear / Not explicitly stated.** The paper targets a Kubernetes/cloud-native environment but does not report a validated benchmark scale.
- Topology: A Kubernetes operational context is assumed; a physical network topology or formal service dependency graph is **Unclear / Not explicitly stated**.
- Production dataset: No.
- Production-scale evaluation: No evidence in this paper.
- Production deployment: No.

## 8. Core Method

The paper proposes three linked design choices:

1. **Knowledge-driven fault injection:** synthesize a fault reproduction plan and monitor telemetry until the intended symptom is confirmed.
2. **Immutable digital twin:** freeze historical telemetry, control-plane configuration, and instantaneous data-plane state into a spatio-temporal snapshot.
3. **Mocked operational interface:** map standard diagnostic commands to deterministic snapshot responses while preserving native command syntax and realistic errors (Source: Sec. 2.1–2.3, pp. 2–3).

This makes state storage independent from tool interaction. The same valid query should produce the same result on every run, while an invalid query can still expose syntax or parameter errors. The result is a controlled environment for process-centric Agent evaluation, not evidence that the Agent has solved real-time operational diagnosis.

## 9. Architecture / Workflow

The actual proposed workflow is:

```text
Operational knowledge / fault source
→ executable fault-reproduction plan
→ fault injection
→ telemetry confirmation
→ freeze telemetry + control plane + data plane
→ expose read-only standard tools
→ agent queries snapshot
→ deterministic Observation
→ continued investigation
→ trajectory and diagnosis evaluation
```

At evaluation time, the Agent trajectory is treated as a sequence of:

```text
Thought → Action → Observation → Thought → ... → final diagnosis
```

`Observation` is the exact state or error response returned by a mocked operational command. It provides the grounding signal for the next decision and makes invalid, redundant, or unsupported investigation steps measurable (Source: Sec. 1.3; Sec. 2.3–2.4; Figs. 1–2).

The paper does not define an independent candidate generator, LLM planner, remediation executor, or recovery loop.

## 10. Detection Method

There is no evaluated detection model. The injection harness continuously checks telemetry to confirm that the intended fault has become observable before creating a snapshot. This is a validity check for benchmark scenario construction, not a claim about online anomaly-detection accuracy (Source: Sec. 2.1).

## 11. RCA / Localization Method

Cloud-OpsBench does not rank root causes itself. It evaluates whether an Agent follows an expert diagnostic path derived from the causal logic of the fault injection. The benchmark can therefore expose unsupported guessing, missing essential checks, redundant actions, and malformed tool calls even when the final diagnosis happens to be correct (Source: Sec. 2.4, pp. 3–4).

**Candidate space:** A numeric candidate universe, root granularity, candidate pruning method, open-set policy, and multi-root policy are **Unclear / Not explicitly stated**. The snapshot gives the Agent access to system state and tools, but the paper does not prescribe a topology-constrained set such as all devices, interfaces, or links. The expert trajectory functions as a procedural reference, not as a formal candidate list.

## 12. Diagnosis / Classification Method

The diagnosis output is assessed through the process that leads to it. The paper defines three types of procedural adherence:

- **Strict Sequential Identity:** exact match to the expert action order.
- **Logical Subsequence Consistency:** essential expert actions appear in the same relative order, allowing non-destructive exploration.
- **Functional Completeness:** all necessary diagnostic actions are performed regardless of order (Source: Sec. 2.4.1, p. 4).

These measures evaluate diagnostic behavior, not fault-type classification accuracy. The paper does not provide a standard output schema for device, interface, link, fault type, or cause chain.

## 13. LLM / Agent Role

- LLM used: **Yes, as the class of systems being evaluated / future trained.** The paper frames the target as an Agentic SRE, but does not report a comparative LLM experiment in this paper.
- Tool use: **Yes.** Standard operational commands are exposed through the mocked interface (Source: Sec. 2.3).
- Multi-step interaction: **Yes.** Active perception and multi-step investigation are central to the proposal.
- Observation: **Yes.** Tool responses are deterministic observations.
- Autonomous next-action selection: **Intended evaluation capability.**
- Planning: **Unclear.** A trajectory may contain plan-like reasoning, but the paper does not require an explicit Planner component.
- Replanning: **Unclear / Not explicitly evaluated.**
- Memory: **Context-only for the current trajectory, at most.** The frozen snapshot is environment state, not persistent Agent memory.
- Feedback loop: **Yes for benchmark interaction; no operational remediation loop.**
- Environment interaction: **Yes, through a read-only mocked environment.**
- Verification: **Process and tool-use auditing.** It is not an independent truth check of every root cause.
- Human gate: Not part of the implemented evaluation interface.

**Paper terminology:** Agentic SRE, active perception, knowledge grounding, deductive reasoning.

**Knowledge-base interpretation:** This is a proposed deterministic benchmark for tool-augmented Agent workflows. It evaluates agentic interaction, but it is not itself a production Agent, and the paper does not justify treating every participant model or every future training use as a complete autonomous Agent.

## 14. Ground Truth

Ground truth is derived from the causal logic of the fault injection and used to construct an expert diagnostic trajectory / SOP for the specific incident. The paper also uses successful fault manifestation as a prerequisite for snapshot creation (Source: Sec. 2.1 and Sec. 2.4).

The exact root-label granularity, whether multiple simultaneous roots are represented, and whether a formal time-interval label is released are **Unclear / Not explicitly stated**. The available ground truth is primarily procedural and scenario-specific rather than a general network RCA annotation protocol.

## 15. Baselines

Table 1 compares benchmark paradigms rather than reporting competing RCA model scores. Static telemetry benchmarks are described as lacking interaction and providing only outcome-focused evaluation; dynamic environments provide interaction but suffer from stochasticity; the proposed State Snapshot approach combines standard tool use, knowledge context, reproducibility, and outcome-plus-process evaluation (Source: Table 1, p. 3).

There is no conventional RCA baseline table with accuracy, Top-k, or MRR results in this paper.

## 16. Metrics

The proposed process metrics measure different properties:

- **Strict Sequential Identity:** exact procedural match.
- **Logical Subsequence Consistency:** preservation of essential causal order.
- **Functional Completeness:** coverage of necessary diagnostic actions.
- **Tool Relevance / Precision:** fraction of tool calls aligned with expert practice.
- **Tool Coverage / Recall:** fraction of expert-defined tools successfully used.
- **Invalid Action Count (IAC):** malformed schemas, parameters, or protocol actions.
- **Redundant Action Rate (RAR):** repetitive calls that add no new context.
- **Zero-Tool Diagnosis Rate (ZTDR):** final diagnosis without valid investigation (Source: Sec. 2.4.1–2.4.3, pp. 3–4).

These metrics measure process grounding, efficiency, and operational robustness. They do not measure physical root-cause accuracy, repair success, latency in a live system, token cost, or recovery.

## 17. Main Results

The paper is a proposal/prototype vision and does not report a completed benchmark result table with incident-level accuracy or Agent comparisons. Its main supported result is methodological: a state snapshot plus deterministic mocked tools can, in principle, preserve interaction while making runs reproducible, and process metrics can expose failure modes hidden by outcome-only scoring (Source: Abstract; Sec. 1.3; Sec. 2.3–2.4; Sec. 4).

Claims about future fine-tuning, reinforcement learning, and standardized operational trust are roadmap proposals, not experiments completed in this paper (Source: Sec. 3, p. 4).

## 18. Scalability / Deployment

- Prototype/testbed: **Yes.**
- Production dataset: **No evidence established.**
- Production-scale evaluation: **No evidence established.**
- Production deployment: **No.**
- Scale: **Unclear / Not explicitly stated.**

The paradigm may reduce repeated environment setup and evaluation noise, but the paper does not prove that its snapshots scale to large physical network topologies, high-rate NetFlow, long telemetry histories, or permissions and latency found in live operations.

## 19. Strengths

- Makes active information seeking part of the evaluation rather than handing an Agent an unrealistically complete prompt.
- Separates operational-state fidelity from runtime stochasticity.
- Preserves native tool syntax and realistic invalid-command behavior.
- Evaluates diagnostic process, redundant investigation, and unsupported guessing in addition to final outcome.
- Offers a possible safe sandbox for later policy training without executing destructive actions.

## 20. Limitations

### Paper-backed limitations / boundaries

- The paper presents a paradigm and prototype direction rather than a completed, broadly validated benchmark (Source: Sec. 3–4).
- The read-only interface does not evaluate state-changing actions, remediation safety, rollback, or recovery.
- A frozen snapshot cannot reproduce all live-system effects, permissions, latency, self-healing, or evolving topology.

### Current interpretation

- A trajectory matching score can reward conformity to one expert path; it should not automatically be treated as proof that the path is the only valid or physically causal path.
- Snapshot reproducibility is not the same as evidence correctness. The snapshot preserves what the benchmark recorded, but does not by itself prove entity mapping, timestamp alignment, or causal truth.
- The cloud-native/Kubernetes setting leaves physical network entities, packet paths, device state, and open-set/multi-root network failures untested.

## 21. Reproducibility

- Code available: **Unclear / Not explicitly stated as a released repository in this paper.**
- Dataset available: **Unclear.**
- Benchmark available: **Prototype / initiative described; release status unclear.**
- Prompt available: **Unclear.**
- Tools described: **Partly.** Standard command semantics and mocked-interface principles are described.
- Model/API specified: **No completed comparative experiment to reproduce.**
- Hyperparameters: **Not applicable / not reported.**
- Fault injection available: **Design described; implementation availability unclear.**
- Reproducibility: **Medium.** The architecture and process metrics are specified conceptually, but a complete public corpus, implementation, and result table are not established in the local paper.

## 22. Relationship to Existing AIOps Knowledge

Cloud-OpsBench complements [RCAgentBench](../rcagentbench/notes.md). RCAgentBench provides a concrete multimodal microservice benchmark with tools and outcome/process metrics; Cloud-OpsBench focuses on how to freeze the operational state and preserve deterministic interactive behavior for reproducible Agent evaluation. Both support process-aware evaluation, but neither establishes physical network RCA or production remediation.

It also connects to [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md) and [Production Evaluation](../../../concepts/aiops/production-evaluation.md): a snapshot provides repeatable state provenance and query replay, while the benchmark’s process metrics expose whether an Agent actually used the available evidence. This is narrower than a complete provenance schema and not equivalent to a live production record.

Related concepts:

- [Agentic Incident Management](../../../concepts/aiops/agentic-incident-management.md)
- [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md)
- [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md)
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md)
- [Agent](../../../concepts/agent.md)
- [Tool Use](../../../concepts/tool-use.md)

## 23. Relevance to My Research

### Similarities

The paper treats telemetry, configuration, runtime state, tool access, evidence seeking, and diagnostic process as first-class parts of operational RCA evaluation. This is directly relevant to the current goal of measuring more than a final root label.

### Differences

Its environment is cloud-native/Kubernetes and read-only. The current research concerns network devices, interfaces, links, optical modules, physical topology, syslog, traffic/NetFlow, and potentially state-changing remediation. Cloud-OpsBench does not establish those entities, modalities, or deployment conditions.

### Potentially Useful Ideas

- Build immutable incident snapshots containing aligned metrics, syslog, traffic/NetFlow, configuration versions, interface/device state, and topology.
- Expose typed, read-only network diagnostic tools whose invalid actions are recorded rather than hidden.
- Evaluate both final RCA and process measures such as tool relevance, coverage, redundant queries, invalid calls, and zero-tool guessing.
- Use fault-injection confirmation before admitting a synthetic case to a benchmark, while clearly labelling injected rather than historical incidents.

### Assumptions That May Not Transfer

- Exact replay may not model live device permissions, telemetry delay, clock skew, changing topology, rate limits, or side effects.
- A single expert trajectory may not capture multiple valid network investigation paths.
- Kubernetes object state is not a substitute for physical topology or packet-level evidence.
- Read-only diagnosis does not validate safe remediation.

### Experiments Worth Considering

- Compare static-prompt, live-testbed, and immutable-snapshot evaluation on the same network incidents.
- Measure RCA correctness together with evidence provenance coverage, tool validity, query redundancy, latency, and operator effort.
- Test whether a topology-aware snapshot lets an Agent identify an interface/link root without granting unconstrained access to the full candidate universe.
- Add a separate controlled execution phase for approved actions and an independent recovery signal.

### Transferability to Network AIOps

**Medium.** The benchmark and process-evaluation abstractions transfer well; the snapshot fidelity, tool semantics, physical topology, and remediation safety require a network-specific design.

## 24. My Understanding

Cloud-OpsBench’s contribution is to make the *investigation process* observable and repeatable. A correct diagnosis is not enough if the Agent never queried evidence, issued invalid commands, or repeatedly made unsupported guesses. Freezing state and replaying standard tools gives researchers a controlled way to measure those behaviors.

For Network AIOps, the useful transfer is not “use a Kubernetes digital twin.” It is the separation of an evidence state from the interaction engine, plus an explicit audit trail. A network version would still need entity/time provenance, physical and dynamic topology semantics, candidate definitions, and a separate safety/recovery protocol.

## 25. Questions

- How should a frozen network snapshot represent delayed, missing, or conflicting telemetry without making replay unrealistically clean?
- How many valid expert trajectories should be allowed when a network incident has multiple safe investigation paths?
- How should process metrics be calibrated when the candidate space contains devices, interfaces, links, modules, and fault types at different levels?
- What is the minimum live or controlled execution evidence needed before snapshot-based results predict production Agent behavior?

## 26. Source Grounding

- State Snapshot motivation and Agentic SRE competencies: Sec. 1.1–1.3, pp. 1–2.
- Knowledge-driven injection and anomaly confirmation: Sec. 2.1, p. 2.
- Frozen spatio-temporal state, telemetry/control/data-plane dimensions: Sec. 2.2, p. 3.
- Mocked operational interface and read-only behavior: Sec. 2.3, p. 3.
- Trajectory matching, process dimensions, and robustness metrics: Sec. 2.4–2.4.3, pp. 3–4; Fig. 2.
- Paradigm comparison: Table 1, p. 3.
- Future fine-tuning/RL/trust roadmap and implementation boundary: Sec. 3–4, p. 4.

## 27. Tags

`AIOps` `Agentic-SRE` `benchmark` `state-snapshot` `digital-twin` `tool-use` `process-evaluation` `RCA` `reproducibility` `Network-AIOps`

## Code / Implementation

- Repository: [LLM4Ops/Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench)
- Official status: Likely Official
- Read at commit: `54bcec7c7faba390549bda833c175178a7513812`
- Code notes: [Cloud-OpsBench source-code notes](../../../code/aiops/cloud-opsbench/notes.md)
- Implementation coverage: Snapshot-backed tools, ReAct/Skill agent harnesses, strict diagnosis contracts, trace logging, and process/evidence evaluators.
