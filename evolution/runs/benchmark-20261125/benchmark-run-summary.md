# Benchmark Research Run Summary

**Focus:** AIOps Benchmark Design, Dataset Construction and Agent Evaluation
**Fixed scope:** RCABench, NIKA, OpenRCA, *Constructing Large-Scale Real-World Benchmark Datasets for AIOps*, AgenticOpsEval, CTBench
**Base:** `1547688`
**Engine run:** `benchmark-20261125`
**Status:** `PARTIAL`

## Execution and stopping reason

The fixed-candidate queue was accepted. Discovery and full-worktree audit were disabled for this narrowly scoped run. Planner call 1 autonomously chose NIKA and CTBench for the first round because they best exposed the process-evaluation gap. Executor call 2 completed section-level analysis of those papers. Its reported input usage was **570,961 tokens**, above the task’s 300K target; the run was stopped before further work. Evaluator/Judge call 3 had started but was interrupted and returned no usable result. No Reflector-produced research feedback or second-round Planner decision exists.

| Stage | Result | Recorded usage |
| --- | --- | ---: |
| Planner | Completed; chose NIKA + CTBench | 29,259 input / 1,054 output |
| Executor | Completed, selected sections only | 570,961 input / 12,265 output |
| Evaluator / Judge | Interrupted before structured result | unavailable |
| Reflector | Runtime fallback only, not semantic research reflection | no model usage |

The manifest records **3 calls started**, **600,220 input / 13,319 output tokens reported**, with the Judge usage unavailable and therefore not included. API cost and model name were unavailable. Run wall time was approximately 5m34s (16:56:31–17:02:05 UTC, 2026-11-25). The total may exceed the reported token sum because the interrupted Judge did not report usage.

## First-round findings

Executor produced four single-paper findings with valid source identity/locator records and one cross-paper synthesis. Deterministic evaluation found a source/schema failure in the synthesis finding: it used a combined source URI absent from the reviewed-paper list. The Judge was interrupted before returning a decision, so no findings became accepted Claims; the batch-wide gate also treated the one Finding error as a batch failure. The gate has since been changed so source/schema failures attach to individual Findings: the cross-paper synthesis is rejected while independently valid Findings remain eligible for Judge review. This repair does not retroactively accept or verify any Benchmark finding.

The useful research observations preserved in [`round_01/artifacts/research-memo.md`](round_01/artifacts/research-memo.md) are:

- NIKA reports answer quality, investigation time/resources, and diagnosis-time network/SLO impact as distinct dimensions; it does not yet evaluate mitigation safety.
- CTBench separates answer metrics from golden-action coverage and resource descriptors. Coverage is adherence to a constrained reference route, not proof that evidence was used.
- CTBench used expert review to retain 234 tasks from 359 candidates, but its recorded-output backend does not test dynamic repair/live state.
- A cross-benchmark scorecard should keep final correctness, evidence/process, resource cost, and operational safety separate. This synthesis still needs independent evidence review.

## Six-paper research products

The repository now contains six Benchmark-category paper notes, the identity/source inventory, a comparison matrix, dataset-design insights, research gaps, and Review v1. All six papers had local PDFs and derived text available. The Engine itself records **0 full-text reads**: NIKA and CTBench received selected-section analysis; the other four were outside the first-round queue. The six-note synthesis is not represented as six Engine full reads or Judge-verified findings.

Official implementation checks were read-only and bounded to public project documentation/path maps and paper-described entrypoints. The review records that the current Aegis and NIKA repositories may have changed from paper snapshots; OpenRCA’s `main.generate`, `main.evaluate`, and `rca.run_agent_standard` are identified from project documentation; ZTE links separate dataset/evaluation repositories; AgenticOpsEval GitLab source files could not be inspected; CTBench has a public dataset card but no separately verified code repository. No code was executed, no dataset downloaded, and no failure injected.

## Knowledge and approval boundary

- New Benchmark-category research notes/reports were created as requested; no existing Concept, Claim, Lesson, or Skill was overwritten.
- No Claim/Evidence record was accepted, no knowledge Proposal was generated, and no existing Proposal was approved.
- No existing Skill was modified. Skill Evolution assessment: **No Skill Update Needed** on the current evidence; the incomplete run is insufficient evidence for changing paper-reading Skills.
- Local AIOps challenge source data, dictionary, labels, injection scripts, and experiment records were not found. The inode/process-count/fd and other user-listed risks remain questions to investigate, not verified dataset defects.

## Experience Memory

The saved Planner and Executor prompts contain the five relevant Experience IDs for local-source reuse, proportional validation, retry preservation, Finding/Claim separation, and primary-source evidence. The Judge prompt contains the three evidence/controller experiences relevant to verification. Thus Experience Memory was actually injected into the Engine roles; it was not only retrieved by the surrounding Codex task. `manifest.json`'s empty `experience_ids` means this run collected no new experience records at termination; the field does not represent retrieved/injected IDs. The Reflector used a deterministic runtime fallback and had no model prompt in this run.

One new active efficiency experience was recorded as `exp-8bd076219cec`, linked to this run’s usage manifest. It captures the observed 570,961-token Executor stage and recommends smaller role context and per-stage budgets that preserve Judge/Reflector capacity.

## Workflow and token diagnosis

The Executor's 570,961 input tokens came from one section-analysis call for NIKA and CTBench, not six complete paper reads. The saved CLI event log contains 11 distinct shell invocations (22 in-progress/completed event records) and about 162,970 bytes of captured command output. Broad `rg` commands account for about 120,639 bytes (74%); repeated targeted reads overlap by 92 lines for each paper, and the Executor also read its 4,322-byte memo back after writing it. These are strong sources of avoidable context, but the CLI does not provide a precise per-command token attribution, so they cannot be mapped exactly to the 570,961 tokens.

The Executor prompt was about 45 KB. It included a 27 KB serialized Goal with the full six-paper fixed queue and research context, while task memory repeated portions of that context; the active plan selected only NIKA and CTBench. This duplicated prompt context, broad shell output, and overlapping source ranges are more plausible contributors to the high input total than complete rereads of all six papers.

The Engine did not load or invoke the repository's `paper-reading`, `aiops-paper-reading`, `paper-code-discovery`, or `code-reading` Skill files. Its prompt named these protocols and embedded a short set of evidence rules, but the Executor wrote one `research-memo.md` rather than canonical per-paper notes. The ordinary Codex workflow separately created the six Benchmark paper notes and synthesis. It reused the Engine memo for NIKA/CTBench, so the work was not six full duplicate reads, but findings and notes overlapped and were created by separate flows. The Engine's Judge is already designed to reuse merged Executor findings and inspect only cited source sections; Reflector and Knowledge Evolution also consume the Executor result rather than doing their own full research.

`learning-batch` and `aiops-learning-batch` were not invoked in this Engine run. Their batch-planning scope overlaps conceptually with the Controller's round planning, budget, retry, and checkpoint responsibilities; they should remain standalone entry points for ordinary Codex work rather than being nested under the Engine. The Engine and ordinary Codex share the repository's committed Skills and knowledge files, while the Engine executes in a detached worktree at its frozen base commit; uncommitted work in the main checkout is not automatically visible there.

For the currently preferred lightweight direction, reusable components are the existing Skills, Experience Memory retrieval, local source manifest, Claim/Proposal checks, and optional independent Judge / Skill Evolution. No new lightweight workflow was implemented as part of this diagnostic repair.

## Remaining work

Independent Judge verification, semantic Reflector feedback, and feedback-driven rounds 2–3 remain unexecuted. The paper comparison is useful as a source-grounded research draft, but it should not be treated as a fully Engine-validated six-paper review. A future bounded continuation should limit each Executor payload to a smaller paper/source subset and reserve calls for Judge/Reflector before execution; do not repeat completed local discovery or source acquisition.
