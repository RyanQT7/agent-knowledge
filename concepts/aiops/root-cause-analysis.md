Status: evolving

# Root Cause Analysis in AIOps

## Definition

Root Cause Analysis (RCA) identifies the component, condition, or fault mechanism that best explains an observed incident. It is not synonymous with detecting that something is abnormal: detection says that a signal violates a normal pattern, while RCA asks which cause initiated or best accounts for the incident.

## Why It Matters

An incident can produce many downstream symptoms. A useful RCA system must separate symptoms from candidate causes, use evidence from the relevant time window, and report enough support for an operator to verify the result.

## Core Mechanism

A general RCA workflow can be viewed as:

```text
incident / anomaly signal
→ evidence extraction
→ candidate root-cause generation
→ structural or causal constraints
→ candidate ranking / verification
→ root cause and diagnosis
→ explanation or remediation
```

The exact stages vary. Some systems receive an already detected incident; others include anomaly extraction. Candidate roots may be services, pods, nodes, metric variables, anomaly nodes, or operational knowledge entries. Therefore, RCA results are meaningful only together with a clear candidate-space definition and ground truth.

## Task Boundaries

- **Detection:** identify that a signal or system state is abnormal.
- **Localization:** identify where the fault is, such as a service, device, or metric variable.
- **Diagnosis:** identify the fault type or mechanism.
- **Explanation:** provide evidence and a causal or operational account.
- **Remediation:** take or recommend an action that addresses the cause.

These tasks can be composed, but a high detection score does not imply correct RCA.

## Evidence and Structure

Evidence may come from metrics, logs, traces, alerts, topology, tickets, knowledge bases, or tools. A dependency graph, call graph, anomaly graph, causal graph, or troubleshooting tree can all constrain reasoning, but they do not have the same semantics. A graph should not be called a physical causal model unless the paper establishes that claim.

## Representative Papers

- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — multimodal tools and process-level agent RCA evaluation.
- [StaR](../../papers/aiops/star/notes.md) — stateful dynamic-graph causal discovery and root ranking.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — anomaly-graph reasoning for long-tail and cascading incidents.

## Advantages

- Makes symptom-versus-cause reasoning explicit.
- Supports top-k localization, diagnosis, evidence, and operational evaluation separately.
- Can combine heterogeneous evidence with system structure.

## Limitations

- Ground truth is difficult for real incidents, especially with multiple causes and delayed effects.
- Candidate spaces are domain-dependent and may be closed, open, or only implicitly defined.
- A structural dependency or predictive relation is not automatically physical causality.
- Missing, delayed, or noisy telemetry can make a plausible explanation wrong.

## My Understanding

In the current knowledge base, RCA is best treated as an evidence-grounded decision problem whose output should state both *where/what* the root cause is and *why* the evidence supports it. The papers also show that RCA quality depends on the observation interface, candidate space, and evaluation protocol—not only on the reasoning model.

StaR adds a caution that a model can rank root variables using predictive, state-aware relationships without proving that those variables are physical causes. RCA claims should therefore name the semantics of the graph and evidence being used (Source: [StaR paper note](../../papers/aiops/star/notes.md), Sec. 5).

CAUSALDX adds a different candidate-space pattern: select among observed anomaly nodes, expand open-set hypotheses, and verify them with independent observations/tools before accepting a diagnosis. This makes candidate generation and verification explicit rather than treating RCA as a closed-set label lookup (Source: [CAUSALDX paper note](../../papers/aiops/causaldx/notes.md), Sec. 4.3).

## Open Questions

- How should open-set and multi-root RCA be evaluated in network infrastructure?
- How can detection evidence be handed to RCA without hiding false negatives or uncertain observations?
- How should physical network causality be distinguished from dependency, correlation, and predictive usefulness?
