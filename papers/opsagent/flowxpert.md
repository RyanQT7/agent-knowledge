# FlowXpert: Expertizing Troubleshooting Workflow Orchestration with Knowledge Base and Multi-Agent Coevolution

## Bibliographic record

- **Authors:** Binpeng Shi, Yu Luo, Jingya Wang, Yongxin Zhao, Shenglin Zhang, Bowen Hao, Chenyu Zhao, Yongqian Sun, Zhi Zhang, Ronghua Sun, Haihua Li, Wei Song, Xiaolong Chen, Jingbo Miao, Dan Pei.
- **Status:** ACM SIGKDD ’25, Proceedings V.2, pp. 4839–4850, DOI [10.1145/3711896.3737221](https://doi.org/10.1145/3711896.3737221).
- **Primary sources:** [NKU camera-ready PDF](https://nkcs.iops.ai/wp-content/uploads/2025/06/adsb0028_FlowXpert_camera_ready.pdf), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local full text:** `sources/papers/opsagent/flowxpert.pdf` (ignored by Git).
- **Official code:** Not publicly found from the paper/lab materials checked. No repository SHA/license to report.
- **Reading status:** Full 12-page paper read (Sections 1–7 and appendices relevant to data, scoring, deployment, and validity threats).

## Problem, mechanism, and workflow

FlowXpert targets the labor-intensive production work of writing domain-specific troubleshooting workflows. It is an OpsAgent-adjacent system, but its primary research object is **workflow generation and evaluation**, not live RCA itself.

**Pipeline (Sections 3–5; Figures 2–4):** operational documents and incident material → hybrid vector/graph KB with incident-aware ontology nodes → query/context retrieval → Planner generates N candidate workflows → Scorer assesses relevance, coverage, accuracy, coherence, conciseness → best-scored workflow returned for operator use → an AI Executor can interpret the workflow steps and call operational tools.

- **Knowledge:** vector chunks plus a graph organized around incident indicators, root causes, and mitigations. Construction includes incident extraction, node filling, cross-chunk merging, and refinement.
- **Agent roles:** Planner and Scorer are two LLM roles. They are not operationally independent incident investigators. Best-of-N sampling uses the Scorer to select among Planner outputs.
- **Learning:** offline PPO optimizes Planner using multi-dimensional Scorer feedback; contextual-richness-controlled preference pairs train the Scorer with DPO. This is the paper's coevolution mechanism. It is not online self-modification while handling an incident.
- **Planning/tools/state:** generated workflow contains process, decision, and terminal steps. The Executor sequentially interprets steps, extracts parameters, invokes tools, evaluates decisions, and passes responses forward. The paper's workflow text can include actions that are not executable APIs.
- **Verification/recovery:** Scorer judges workflow quality; production OCEs accept or refine workflows. A human-checked workflow is used by the Executor in five frequent incident categories. This does not establish automated root-cause truth or end-to-end verified recovery.

## Evidence and boundaries

**Paper evidence (Section 5, Tables 1–2; Section 6, Figures 5–6; Appendix A/C):** OpsFlowBench has 252 query/workflow pairs (148 train, 104 test) across Hardware, Interface, Network, and TOP scenarios. STEPScore compares generated steps with manually curated steps using embedding similarity/precision/recall; it explicitly does not measure real execution pass rate offline. The paper reports an average F1 around 71.8 at the first coevolution iteration with Qwen2.5-7B (Table 1); additional iteration gains vary by seed model.

Production use is reported in Huawei Cloud DCN: workflows were generated for 189 incident types; a workflow counted as acceptable when it recalled at least 75% of core steps. From 2024-10-21 to 2024-12-29, the paper reports about 80% acceptance across 34,488 incident tickets. Generation averaged 22.1 seconds versus a historical estimate of seven on-call engineers taking about seven hours to build a workflow. An AI Executor powered by Pangu-7B handled five frequent incident categories after operator verification/refinement. This is meaningful deployment evidence, but the acceptance metric measures alignment to workflow process and operator use, not root-cause correctness or recovery causality.

**Limits stated by the authors (Section 6.3):** entirely novel incidents still need manual handling and KB updates; natural-language descriptions do not guarantee executable APIs; synthetic preference quality and scorer reliability limit coevolution. **Our reading:** FlowXpert's workflow generation is complementary to OpsAgent/KRCA/KnowLution diagnosis, not a substitute for evidence acquisition, candidate localization, or post-action recovery verification.

## Research value

For Network AIOps, this supports converting validated runbooks into explicit, reviewable workflows with branch conditions, but network commands need typed parameters, permissions, preconditions, rollback, and state-aware postconditions. A textual “workflow” should not be counted as a safely executable remediation plan. Compare with existing [FlowFixer](../aiops/flowfixer/notes.md) and [Hybrid RCA architecture](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md) before starting a duplicate concept.
