# AgenticOpsEval — Process-Aware Microservice Failure Diagnosis

## Identity and evidence status

- **Title:** *A Multi-Dataset Benchmark for Evaluating LLM Agents in Microservice Failure Diagnosis*
- **Authors:** Yuanhong Cai, Xiaohui Nie, Kanglin Yin, Changhua Pei, Yongqian Sun, Shenglin Zhang, Haibin Liu, Guiyang Liu, Xidao Wen, Fang Situ, Dan Pei.
- **Version / venue:** arXiv:2606.29193v1, 2026-06-28; no venue listed on the arXiv record. [Paper](https://arxiv.org/abs/2606.29193)
- **Official dataset/project:** [AgenticOpsEval page](https://www.aiops.cn/gitlab/aiops-live-benchmark/agenticopseval); paper reports scoring code.
- **Local source:** [`AgenticOpsEval_2606.29193.pdf`](../../../sources/papers/benchmark/AgenticOpsEval_2606.29193.pdf). The Engine did not select it. Paper and project-page metadata were reviewed; GitLab files were not accessible for direct source inspection, so scoring-code mechanisms below are from the paper rather than a code audit.

## Motivation and data

AgenticOpsEval argues that final-answer-only RCA metrics cannot distinguish evidence-grounded reasoning from keyword luck. It introduces two datasets totaling 503 cases and about 15.3 GB from two microservice systems. This is a benchmark for agent diagnosis over multimodal observability, not an online live-production repair environment.

### AIOps2025

400 cases on HipsterShop: 10 services plus TiDB components and Redis, deployed across 8 VMs and 33 pods. It covers 18 fault types across nine categories and three severity levels. The paper reports about 11.9 GB, 2,835 files, 269 million rows, and an 18-day collection period. Chaos Mesh is used for fault injection. Three SRE experts independently annotate cases and a senior expert adjudicates; detector proposals help locate candidate evidence. The paper reports competition validation, with 6,093 participating teams for this dataset.

### RCA100

103 OpenTelemetry Demo Store cases on Alibaba Cloud ACK, 28 fault types in six groups, approximately 3.4 GB and 116 million rows. It contains metrics, logs, traces, events, alerts, and topology. The labels cover fault type, UModel entities, cause→propagation→impact chains, and numeric evidence checkpoints. Paper-reported consistency checks include cross-modal evidence references resolving and high entity/topology alignment. The setup includes single-fault and composite cases; 13 are described as composite.

## Ground truth and scoring

For AIOps2025, the paper labels per-modality key evidence and expert-reviewed cause entities/types. Its score combines localization accuracy (0.4), type accuracy (0.4), explainability/evidence coverage (0.1), and efficiency (0.1). The efficiency term is based on reasoning-path length, not actual API cost or wall-clock resource consumption; it should not be read as a real token/cost budget.

RCA100 adds structured causal chains and evidence checkpoints. Its score weights entity localization (0.4), fault classification (0.3), and causal chain/evidence (0.3). The exact scoring details differ across the two datasets, so scores should not be compared as if they were identical tasks. Neither metric alone verifies that each cited observation actually drove a correct causal inference.

## Agent evaluation, shortcuts, and limitations

The task is agentic diagnosis on multimodal data, but the paper’s central process measure is labeled evidence coverage rather than open-ended safe tool interaction. AIOps2025 includes anomaly descriptions and key observations; RCA100 supplies structured alert inputs and expected chains/checkpoints. Potential shortcuts include repeated fault templates, known workload signatures, and curated candidate evidence. These are risks to test, not reported proof of leakage. Open-set split by fault type, service, time, and injection template is needed to establish generalization.

The two datasets have expert labels and competition exposure, but they remain testbed-derived microservice cases rather than a broad census of production incidents. The paper’s path-length efficiency proxy does not account for actual tokens, API spend, latency, or safety of action.

## Code and openness

The paper links a public data page and states that scoring code is provided. The public GitLab project could not be expanded to source files in this study. No line-level implementation or scorer was inspected, no dataset downloaded, and no benchmark run. The distinction between paper-defined scoring and current repository contents remains to be version-pinned.

## Relevance

AgenticOpsEval contributes explicit evidence labels and causal-chain checkpoints across two datasets, complementing NIKA’s tool/trajectory observability and CTBench’s expert action routes. For our dataset, evidence annotations should be independently auditable and evaluator outputs should report actual cost separately from reasoning length. See the [comparison](../../../notes/benchmark/benchmark-comparison.md).
