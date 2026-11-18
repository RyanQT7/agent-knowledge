# AgentOps Knowledge Review v1

**Scope:** Operations for LLM agent and multi-agent systems themselves. This review synthesizes full reads of Agent System Operations, AgentRx, TraJudger, PROBE, Trial by Trace, and Taming Uncertainty, with existing CHIEF and FlowFixer notes. The IEEE trajectory-analysis survey was publisher-record/abstract only and is not treated as a full read.

## Mental model

AgentOps is an evidence loop: agent + harness + tools + environment → observable trajectory → detection/abstention → root step + responsible agent + evidence → bounded response or human decision → independent outcome verification → updated monitoring.

Its outputs are distinct: **observed**, **detected**, **attributed**, **acted on**, and **verified recovered**. A diagnosis is not a repair; a retry is not proof of recovery.

## 1. Why do agent systems need dedicated operations methods?

An agent’s behavior depends on probabilistic language decisions, task context, changing tool schemas, external observations, dynamic plans, and sometimes other agents’ messages. Ordinary metrics and logs can identify latency, exceptions, or a failed RPC, but may not show that a model misunderstood a tool result, followed an invalid plan, or propagated an unsupported assumption. Agent System Operations organizes these concerns as monitoring, anomaly detection, root-cause localization, and resolution (Secs. II–VII). Trial by Trace adds a separate question: did the harness preserve and mediate the interaction correctly?

## 2. How are agent failures different from traditional software failures?

Traditional failures often map to code, process, resource, or dependency behavior. Agent failures include semantically wrong but syntactically valid actions; plan drift; unsupported claims; context loss; invalid tool use; premature termination; and coordination errors. They can be stateful and recoverable: an early search failure may be harmless if the agent switches tools, while a later invented assumption may make the run unrecoverable. AgentRx therefore annotates the first **unrecoverable critical failure**, not simply the first odd step or last error.

## 3. What should runtime observability record?

At minimum: run/task identity, agent identity, parent/delegation relation, timestamps and ordered steps; model-visible input/context and output with version/hash and privacy controls; tool name/schema version/arguments/result/errors/retries and environment state; memory/state updates, context compaction, plan changes, handoffs, termination; evaluator/verifier results, evidence sources, and whether the agent observed each result.

This list is a synthesis, not one paper’s standard schema. Trial by Trace measures what harnesses expose; AgentRx normalizes available traces. Neither can recover evidence never captured.

## 4. Why are execution trajectories important?

A terminal response compresses away the causal path. A trajectory shows when intent changed, which observation led to a decision, whether a tool result was misread, and whether a failure was corrected or propagated. It enables step-level evaluation and replay. Full traces still do not guarantee correct attribution: context may be hidden, dependency edges implicit, or the evaluator wrong.

## 5. Single-agent and multi-agent failure modes

A single agent can fail in input understanding, reasoning, planning, tool selection/arguments, tool-result interpretation, memory/context, verification, or termination. MAS add role violations, task decomposition errors, wrong delegation, ambiguous handoffs, ignored corrections, conflicting shared state, and premature coordinator termination.

| Stage | Example failure |
| --- | --- |
| Input understanding | Misread goal or omitted constraint |
| Reasoning | Unsupported claim or invalid inference |
| Planning | Wrong objective/order or skipped step |
| Tool selection | Wrong tool or unavailable capability |
| Tool arguments | Schema-invalid or semantically wrong payload |
| Tool execution | Timeout, refusal, or environmental error |
| Memory/context | Lost, stale, or misapplied observation |
| Coordination | Bad delegation, role drift, ambiguous handoff |
| Verification | Missing/wrong check or ungrounded pass |
| Termination | Stops early, loops, or falsely reports done |

This matrix is a knowledge-base synthesis, not one paper’s taxonomy. AgentRx distinguishes infrastructure failure from malformed invocation and policy/access blocks; TraJudger adds coordination/context modes.

## 6. How do errors propagate between agents?

An upstream agent may supply an incorrect but confident finding. A coordinator turns it into a plan; a specialist performs locally valid work using the false premise; a reviewer repeats it. Later steps look coherent and become the terminal symptom. TraJudger addresses this with a Hierarchical Cognitive Graph: intention/action nodes, typed links, category specialists, and backward traversal from terminal failure. Correct intermediate steps that carry earlier faulty information are conduits, not new roots (Secs. 3–5).

## 7. What is ground truth for Agent RCA?

Ground truth is a reviewed account, not an LLM explanation. Identify root-cause step, responsible agent, failure type, evidence available at that point, recoverable earlier failures, propagation chain, terminal symptom, and uncertainty. Experts may use task policy, tool results, environment state, and expected workflow. Multi-agent labels are expensive and ambiguous; record agreement and allow inconclusive outcomes.

## 8. Why can LLM-as-a-Judge misattribute?

The judge may prefer a fluent story over supported evidence; anchor on a conspicuous downstream error; conflate failure categories; lose dependencies in a long context; or treat correlation as cause. TraJudger reports weaker monolithic-judge results on longer traces and unsupported explanations. AgentRx documents noisy checks distracting a judge. A final response alone is weak evidence.

## 9. How can attribution be structurally constrained?

Normalize traces while retaining raw evidence/provenance; run deterministic schema, policy, return-code, state-transition and evaluator checks; ask semantic models narrow questions with source spans and abstention; represent step/agent dependencies; distinguish direct fault from conduit; traverse candidate causes backwards from the terminal symptom; compare chains with independently adjudicated labels.

AgentRx contributes constraint violations; TraJudger contributes HCG and backward traversal; Trial by Trace contributes evidence selectors and separate Agent/Harness scores. Combining them remains a research proposal.

## 10. How does diagnosis become recovery?

Detection → attribution → diagnosis → recommendation → retry/repair → outcome verification are separate. PROBE connects evidence/diagnosis to gated guidance (target, operation, verification signal, boundary) and tests one later attempt. Its 21.79% recovery rate despite 65.37% Top-1 diagnosis shows diagnosis does not guarantee an executable fix (Sec. 4, Table 2). TraJudger’s refinements were human actions. Recovery needs an external evaluator or environment-state check.

## 11. What can AgentOps and traditional AIOps learn from each other?

Traditional AIOps contributes topology, metric/log/trace correlation, candidate-space pruning, incident history, evidence provenance, deterministic verification, and safety gates. AgentOps contributes semantic trajectory inspection, identity/delegation, plan/context state, tool traces, and attribution of language-mediated propagation. OpsAgent must preserve operational evidence and candidate constraints; AgentOps cannot infer service causality from narrative plausibility alone.

See existing [AIOps Review v3](../../aiops/reviews/aiops-knowledge-review-v3.md), [Hybrid Network RCA synthesis](../../aiops/reviews/network-aiops-architecture-synthesis-v1.md), and [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md).

## 12. Most valuable current gaps

1. Full, privacy-conscious trace capture with a stable evidence contract.
2. Better root-cause and propagation ground truth, including uncertainty/recoverability.
3. Online detection-delay and false-alarm evaluation, not only offline diagnosis.
4. Causal attribution under long context and implicit shared state.
5. Recovery evaluation against independent environment truth, with safe retries, rollback, and human approval.
6. Repeated, representative cross-harness and cross-domain benchmarks.

## Comparison of reviewed mechanisms

| Work | Primary target | Mechanism | What is evaluated |
| --- | --- | --- | --- |
| AgentRx | Failed trajectories | Constraint evidence + LLM judge | Step/category attribution; not repair |
| TraJudger | Failed MAS | HCG, specialists, backward attribution | Offline attribution + limited production human workflow; not autonomous recovery |
| PROBE | Failed software/operations runs | Telemetry → diagnosis → gated guidance | One guided retry in three settings; no live production impact claim |
| Trial by Trace | Harness reliability | Trace IR, layered scores, candidate links | 95 mechanism tasks; selected-run descriptive scores |
| Agent System Operations | Research field | Taxonomy/lifecycle survey | Literature synthesis, not system evaluation |

## Reading links

- [Agent System Operations](../../../papers/agentops/agent-system-operations.md)
- [AgentRx](../../../papers/agentops/agentrx.md)
- [TraJudger](../../../papers/agentops/trajudger.md)
- [PROBE](../../../papers/agentops/probe.md)
- [Trial by Trace](../../../papers/agentops/trial-by-trace.md)
- Existing [CHIEF](../../../papers/aiops/chief/notes.md) and [FlowFixer](../../../papers/aiops/flowfixer/notes.md)
- [AgentOps research gaps](../research-gaps.md)
