# Debugging the Debuggers: Failure-Anchored Structured Recovery for Software Engineering Agents

## Bibliographic record

- Authors: Chenyu Zhao, Shenglin Zhang, Yihang Lin, Wenwei Gu, Zhimin Chen, Yongqian Sun, Dan Pei, Chetan Bansal, Saravan Rajmohan, Minghua Ma.
- Status at 2026-11-17: arXiv:2605.08717, revised 2026-06-05; no conference/journal venue listed on the arXiv record at cutoff.
- Sources: [arXiv record](https://arxiv.org/abs/2605.08717), [PDF](https://arxiv.org/pdf/2605.08717), [anonymous artifact linked by paper](https://anonymous.4open.science/r/6114a1c7/README.md).
- Local PDF: ../../sources/papers/agentops/debugging-the-debuggers.pdf (ignored).
- Reading status: Full 12-page paper including prototype contract, evaluation, and limitations.
- GitHub source: Not publicly found; the paper provides an anonymous artifact link.

## Problem and contribution

Observability systems expose runs and diagnosis methods can localize errors, but that diagnosis is often not translated into bounded, actionable guidance for a subsequent attempt. PROBE proposes a post-failure loop: failed run → telemetry bundle → structured evidence → structured diagnosis → gated guidance → one repair attempt.

Unlike AgentRx and TraJudger, which focus on localization/attribution, PROBE’s contribution is to give grounded guidance to a later attempt. It is not an online monitor and does not autonomously execute production remediation (Secs. 1, 3, Fig. 2).

## Pipeline and LLM role

- Telemetry Layer captures boundary events, tool calls/results, evaluator outcomes, and environment-side evidence.
- Diagnosis Layer localizes failure signals, fuses evidence, and produces a structured diagnosis: failure anchor, primary cause, behavioral mistake, contributing factors, evidence summary, and confidence.
- Guidance Gate checks grounding, actionability, and intervention scope. Guidance specifies target, operation, verification signal, and boundary condition.
- The same subject agent receives the bounded hint for one repair attempt, with task/tools/evaluator/budget fixed.

LLMs interpret heterogeneous evidence and generate text; deterministic gates constrain its use. The paper explicitly says confidence is an uncalibrated support estimate, not a probability (Secs. 3.2–3.4, Fig. 3).

## Experiments and limits

The initially unresolved set has 257 cases across SWE-bench (102), EnterpriseOps-Gym (106), and AIOpsLab (49). PROBE achieves 65.37% Top-1 diagnosis and 21.79% one-retry recovery overall. By setting, diagnosis/recovery are 83.33%/28.43% on SWE-bench, 57.55%/11.32% on EnterpriseOps-Gym, and 44.90%/30.61% on AIOpsLab. Table 2 compares outcome-only and AgentOps/LangSmith trace summaries. The larger diagnosis gain than recovery gain exposes a diagnosis–recovery gap (Sec. 4.2, Table 2).

An AIOpsLab case combines logs showing nginx-to-user-service connection refusal with environment state showing a targetPort mismatch. PROBE guides the next attempt to inspect/correct the mapping, re-test connectivity, and avoid submission until verification succeeds. This is guidance for a later attempt, not proof of live cluster repair (Sec. 4.3, Fig. 4).

The Microsoft IcM section describes a deployment-oriented prototype boundary. It does not replace triage, mitigation execution, escalation, or human approval, and does not report measured impact on live incidents (Sec. 5, Table 4).

The protocol permits at most one repair attempt; this is an evaluation choice, not a framework limit. Diagnosis-model capability is not isolated. Median feedback-generation latency is 210.43 seconds. The paper does not measure false alarms on successful runs or a full online detection system (Secs. 4.4, 6). Correct diagnosis is necessary but not sufficient: external constraints and strategy changes can prevent recovery (Sec. 4.3, Table 3).

## Structured answers

| Dimension | Finding |
| --- | --- |
| Failure types | Insufficient validation; tool/subprocess handling; state/workflow error; patch/submission workflow; retry/no-progress loop; runtime/environment handling (Table 3). |
| Trajectory | Boundary events, spans, calls, outcomes, logs, tool/environment state; no universal timestamp/delegation schema claimed. |
| LLM/Multi-Agent | LLM interprets evidence and creates diagnosis/guidance; PROBE is not itself a multi-agent system. |
| Planning/memory | No dynamic planner or persistent memory; guidance conditions the next attempt. |
| Verification | Guidance must name a verification signal; the subsequent task evaluator checks resolution. |
| Recovery | One retry is experimentally evaluated; sidecar does not autonomously execute remediation. |
| Network AIOps | AIOpsLab and the service-mitigation example are directly relevant, but not a production safety case. |

## Paper-code record

- Repository: Anonymous artifact at https://anonymous.4open.science/r/6114a1c7/README.md; no identifiable GitHub repository confirmed.
- Official status/evidence: Linked directly by Data Availability (Sec. 8).
- Commit SHA, license, module mapping: Not established from a named GitHub project. Stable artifact identity/license require separate inspection.
- Code analyzed: No; stable identifiable source tree not confirmed.

## Links

- [AgentRx](agentrx.md) generates step-level validation evidence; PROBE uses operational evidence for recovery guidance.
- [TraJudger](trajudger.md) reconstructs cross-agent dependencies.
- The existing [AIOps Knowledge Review v3](../../notes/aiops/reviews/aiops-knowledge-review-v3.md) and [Hybrid Network RCA synthesis](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md) already require provenance, constrained candidate spaces, and independent verification.
