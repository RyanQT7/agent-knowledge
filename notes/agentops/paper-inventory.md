# AgentOps paper inventory

**Cutoff:** 2026-11-17. Publication state checked against publisher/conference or author pages where available. “Full read” means the accessible full paper was read, not that the system was independently reproduced.

| Paper | Status / identity check | Problem and contribution | Read status / decision | Code |
| --- | --- | --- | --- | --- |
| [Agent System Operations](../../papers/agentops/agent-system-operations.md) | arXiv:2606.01581v2; full text says accepted by IEEE TSE. Authors verified in arXiv. | Anomaly taxonomy and monitoring → detection → localization → resolution framework. Survey, not a unified implementation. | **Full read.** Foundational map; review search through about Aug 2026. | Not applicable. |
| [TraJudger](../../papers/agentops/trajudger.md) | USENIX ATC ’26 accepted; NKU page, ATC program, and PDF agree. | HCG, specialist diagnosis, and conduit-aware backward attribution across MAS steps. | **Full read.** High-priority causal localization and production case study. | Not publicly found. |
| [Debugging the Debuggers / PROBE](../../papers/agentops/probe.md) | arXiv:2605.08717v2; no venue listed at cutoff; authors checked in paper. | Converts telemetry into evidence, diagnosis, and gated guidance for a subsequent attempt. | **Full read.** Diagnosis-to-recovery bridge; one-retry evaluation. | Anonymous artifact linked in paper; no named GitHub source confirmed. |
| [AgentRx](../../papers/agentops/agentrx.md) | Findings of EMNLP 2026; ACL Anthology metadata/DOI verified. | Normalized traces, static/dynamic constraints, checker evidence, judge selects first unrecoverable step/category. | **Full read.** Method and benchmark; not a repair system. | Confirmed official Microsoft repository; static analysis complete. |
| [Trial by Trace](../../papers/agentops/trial-by-trace.md) | arXiv:2610.32285; TraceLite AI group author/affiliations; no peer-reviewed venue at cutoff. | Separates task-agent score from harness reliability across seven dimensions. | **Full read.** High-priority benchmark; descriptive results, not universal ranking. | Confirmed official project repository; static analysis complete. |
| [A Survey for LLM Agent Trajectory Analysis](../../papers/agentops/trajectory-survey.md) | IEEE TSE Early Access, DOI 10.1109/TSE.2026.3717765, published 2026-07-28; eight authors checked at publisher. | Reviews 55 papers across five dimensions, from attribution to enhancement. Overlaps with survey and empirical methods. | Publisher metadata/abstract only; full text inaccessible. **Supplementary; not a full read.** | No paper implementation. Author-curated list is not implementation code. |
| [Taming Uncertainty via Automation](../../papers/agentops/taming-uncertainty.md) | ASE 2025 NIER; IBM Research and arXiv metadata checked. | Early vision for observation, metrics, detection, RCA, recommendation, optimization. | **Full text read; vision/framework only.** | No implementation reported. |
| Seeing the Whole Elephant / TraceElephant | ACL 2026 Long Paper; authors: Mengzhuo Chen, Junjie Wang, Fangwen Mu, Yawen Wang, Zhe Liu, Huanxiang Feng, Qing Wang. [ACL](https://aclanthology.org/2026.acl-long.912/), [arXiv](https://arxiv.org/abs/2604.22708). | Full execution traces and reproducible MAS environments; reports full observability improves attribution over partial traces. Complementary to AgentRx constraints and TraJudger causal graph. | Publisher metadata/abstract triage; **recommended next full read**. | Author project [TraceElephant](https://github.com/TraceElephant/TraceElephant); not yet cloned/analyzed. |
| [CHIEF](../../papers/aiops/chief/notes.md) | Existing knowledge-base full-read note. | Hierarchical agent/step attribution for multi-agent traces. | Reuse, do not duplicate; compare with TraJudger and AgentRx. | Existing note. |
| [FlowFixer](../../papers/aiops/flowfixer/notes.md) | Existing knowledge-base full-read note. | Diagnosis-driven repair of agent workflows. | Reuse as workflow-level recovery. | Existing note. |

## Reading order

1. AgentRx → TraJudger: compare constraint evidence with graph-structured propagation.
2. PROBE → FlowFixer: compare bounded retry guidance with workflow repair.
3. Trial by Trace → TraceElephant: inspect harness reliability and trace completeness.
4. Read the full trajectory-analysis survey when accessible.

AgentOps is an organizing label used in this repository; it is not a universal field taxonomy.
