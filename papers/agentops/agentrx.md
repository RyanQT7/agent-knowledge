# AgentRx: Diagnosing AI Agent Failures from Execution Trajectories

## Bibliographic record

- Authors: Shraddha Barke, Arnav Goyal, Alind Khare, Avaljot Singh, Suman Nath, Chetan Bansal.
- Publication: Findings of EMNLP 2026, pp. 12610–12639, DOI 10.18653/v1/2026.findings-emnlp.598 (ACL Anthology).
- Sources: [ACL Anthology](https://aclanthology.org/2026.findings-emnlp.598/), [arXiv versions](https://arxiv.org/abs/2602.02475), [official dataset](https://huggingface.co/datasets/microsoft/AgentRx).
- Local PDF: ../../sources/papers/agentops/agentrx.pdf (ignored).
- Reading status: Full 30-page v2 text, including annotation protocol, ablations, qualitative failures, and appendices.
- Official repository: [microsoft/agentrx](https://github.com/microsoft/agentrx).

## Problem and central idea

Agent evaluation often reports terminal task success but does not explain where a run first became unrecoverable or why. AgentRx turns a failed trajectory into constraint violations with evidence, then asks a judge to select a critical step and category.

The benchmark contains 170 trajectories across 11 settings and distinguishes the first unrecoverable critical failure from earlier recoverable mistakes, first observed failure, or terminal symptom. Manual annotation records each failure and the critical one; mean inter-annotator Cohen’s kappa is 0.89 on the annotated sample. The paper reports about 62.5 annotator-hours (Secs. 2–3, App. A).

## Pipeline

Raw logs → normalized Trajectory IR → static and dynamic constraints → checker → evidence log → LLM judge → diagnosis.

1. Domain adapters normalize Tau-bench, Flash, Magentic-One, and other traces.
2. Static constraints derive from tool schemas, policy, task requirements, and workflow structure.
3. Dynamic constraints encode per-prefix expectations based on current task and prior observations.
4. The checker runs programmatic and semantic checks and records step-indexed violations with evidence.
5. The judge uses violation evidence and a taxonomy checklist to select a critical step/category, with an inconclusive option.

The paper compares one-shot and prefix-by-prefix constraint generation. Prefix-specific constraints can reduce context dilution on long traces but cost more. The checker, not the judge, produces the auditable violation record (Secs. 3–4, Figs. 1–2, Table 4).

## Taxonomy and evaluation

The taxonomy has nine substantive classes plus Inconclusive: Instruction/Plan Adherence; Invention of New Information; Invalid Invocation; Misinterpretation of Tool Output/Handoff; Intent–Plan Misalignment; Underspecified User Intent; Intent Not Supported; Guardrails Triggered; System Failure; Inconclusive.

Invalid invocation, infrastructure failure, and access/policy refusal are different operational causes. A malformed argument is not endpoint unavailability or a safety block. The target is the earliest unrecoverable cause, not simply the last visible error.

Evaluation includes Tau-bench, Flash, Magentic-One, and RelWork, with three runs per main judge configuration. Metrics include exact step accuracy, distance/tolerance, and category accuracy against critical, any, earliest, and terminal labels (Sec. 4.1, Tables 3–7). Long Magentic-One/RelWork traces remain more difficult than shorter Flash traces. Violation evidence helps some datasets/categories more than others; noisy downstream checks can mislead the judge. A Magentic-One example is distracted by a late guardrail event rather than an earlier hallucinated assumption (Secs. 4.3, 4.7).

Under paper GPT-5 pricing assumptions, one-shot AgentRx costs about $0.18/trajectory versus $0.05 for a judge-only baseline. Prefix-based checks improve some long traces but cost more (Sec. 4.4). Applying the method to 1,022 MAST traces yields profiles, not gold-label accuracy, because MAST does not provide ground truth for this critical-cause task (Sec. 4.2). Labels are expensive and cannot eliminate ambiguity, hidden state, or missing telemetry.

## Structured answers

| Dimension | Finding |
| --- | --- |
| Failure location | Step and category; responsible agent for multi-agent trajectories. |
| Propagation | Labels distinguish recoverable early errors from the first unrecoverable event; no full causal graph like TraJudger. |
| Trace fields | Ordered messages/tool events are normalized; a universal timestamp, memory-update, delegation-dependency, or verification schema is not claimed for every dataset. |
| LLM role | Generate semantic constraints, interpret semantic checks, and judge evidence. |
| Why LLM? | Schemas/policies permit deterministic checks, but task intent and semantic output interpretation need flexible judgments. |
| Why Agent? | AgentRx diagnoses agents; it is not an autonomous operations agent. |
| Multi-Agent/planning/memory | Supports MAS traces but is not a diagnostic multi-agent team; no planning or persistent memory. |
| Tool/state | Domain adapters normalize recorded events; constraints compare calls and observations with expected behavior. |
| Recovery/verification | Diagnoses only; does not evaluate recovery. Evidence supports diagnosis but cannot prove environment restoration. |
| Network AIOps transfer | Flash provides direct incident-management relevance; transfer needs domain trace adapters, operational constraints, and validated failure labels. |

## Code analysis record

| Field | Record |
| --- | --- |
| Repository | [github.com/microsoft/agentrx](https://github.com/microsoft/agentrx) |
| Official status/evidence | Confirmed Official: Microsoft Research project; README names exact title/arXiv ID and links the Microsoft dataset. |
| Commit SHA | 7a18c79708e7671be15124460f4f7296107c2a55 |
| License | MIT, LICENSE.txt |
| Core files | agentrx/cli.py; IR in agentrx/ir/trajectory_ir.py; checks in agentrx/invariants/checker.py; static/dynamic generators in agentrx/invariants/; judge in agentrx/judge/judge.py. |
| Paper-code mapping | README stages map to IR → constraints → checker → judge → reports. Checker output retains step, invariant, check type, severity, and evidence. |
| Static analysis | Read README, IR, checker/generator interfaces, and judge flow. No dependencies installed and no source code executed. |

The repository supports both programmatic checks and natural-language checks and records check telemetry before judging. IR is an adapter, not a guarantee that all original traces contain timestamps, state snapshots, or delegation dependencies. Taxonomy labels are diagnosis vocabulary; invariants are checks that may provide evidence for one or more labels. This is source inspection, not a reproduction.

## Links

- [Agent System Operations survey](agent-system-operations.md)
- [TraJudger](trajudger.md)
- [PROBE](probe.md)
- [Trajectory survey](trajectory-survey.md), metadata-only because full publisher text was inaccessible.
