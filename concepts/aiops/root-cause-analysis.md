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
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — guide-covered deterministic diagnosis with evidence verification.
- [KAT](../../papers/aiops/kat/notes.md) — graph-grounded telecom troubleshooting and solution generation.
- [AIM](../../papers/aiops/aim/notes.md) — separates root-cause-category alignment, summary/plan quality, and actual remediation execution; it does not establish physical root-node RCA.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — separates service/component localization, root-cause category prediction, explanation, evidence consistency, and human adjudication.
- [Evidence Provenance](evidence-provenance.md) — preserves source, time, entity, and query context for candidate reasoning and verification.

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

LLMGuard shows the complementary closed-world pattern: retrieval narrows the SOP set and deterministic checks prune a tree of guide-covered root leaves, with escalation when trusted coverage is missing. This is operationally reliable but not the same as open-set causal discovery (Source: [LLMGuard paper note](../../papers/aiops/llmguard/notes.md), Sec. IV).

The ten-paper architecture synthesis adds an interface requirement between telemetry and RCA: candidate decisions should carry an Evidence Ticket or provenance-bearing evidence object. This does not make the evidence true, but it allows an LLM, verifier, or operator to re-check source, entity, time, freshness, and conflicts before treating a candidate as a root cause (Source: [Evidence Provenance concept](evidence-provenance.md); [Network AIOps Architecture Synthesis v1](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md)).

CHIEF reinforces that RCA outputs are meaningful only after the candidate unit is defined. Its candidate is an Agent-step pair narrowed through subtask, Agent, and step levels; this is a transferable coarse-to-fine pattern, but not a network candidate protocol. This strengthens the general rule that candidate universe, granularity, pruning, root multiplicity, and ground-truth alignment must be reported separately from the ranking model (Source: [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 3–4).

KAT adds a knowledge-grounded troubleshooting pattern: retrieve error/context/solution paths and relevant subsystem context, then generate a diagnosis and solution. This can improve operational diagnosis without establishing an explicit multi-step Agent loop or a physical root-node localization protocol (Source: [KAT paper note](../../papers/aiops/kat/notes.md), Sec. IV–VIII).

## Open Questions

- How should open-set and multi-root RCA be evaluated in network infrastructure?
- How can detection evidence be handed to RCA without hiding false negatives or uncertain observations?
- How should physical network causality be distinguished from dependency, correlation, and predictive usefulness?
