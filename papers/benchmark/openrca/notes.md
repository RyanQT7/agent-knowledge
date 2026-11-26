# OpenRCA — LLM Root-Cause Analysis of Software Failures

## Identity and evidence status

- **Title:** *OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?*
- **Authors:** Junjielong Xu, Qinan Zhang, Zhiqing Zhong, Shilin He, Chaoyun Zhang, Qingwei Lin, Dan Pei, Pinjia He, Dongmei Zhang, Qi Zhang.
- **Publication:** ICLR 2025. [Proceedings paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/d29b8d53678015079e1d245c023e49d2-Paper-Conference.pdf)
- **Official resources:** [project page](https://microsoft.github.io/OpenRCA/), [Microsoft/OpenRCA](https://github.com/microsoft/OpenRCA).
- **Local source:** [`OpenRCA_ICLR2025.pdf`](../../../sources/papers/benchmark/OpenRCA_ICLR2025.pdf). This paper was not selected by the Phase 1.5 Engine; this note uses the local paper and public project/source descriptions and is not an Engine-certified full read.

## Motivation and data

OpenRCA targets post-development software maintenance, where root-cause diagnosis must combine long, heterogeneous telemetry. It contains 335 failures from three enterprise systems and over 68 GB of metrics, logs, and traces: Telecom (51 cases), Bank (136), and Market (148). The paper reports system-specific data volumes of approximately 17.6, 26.4, and 24.5 GB, respectively. The benchmark draws on real operational systems, but its data is curated and filtered; it is not an unfiltered stream of production incidents.

The paper’s construction pipeline starts from a larger pool (1,753 records), samples/balances candidate cases, and applies engineer calibration before retaining 335. Review checks whether the label is traceable, telemetry is available, and the failure time/label aligns with the evidence. These filters improve usability but also mean reported results apply to selected cases.

## Ground truth, task, and evaluation

RCA questions are synthesized from combinations of root-cause elements, with a failure time window and a candidate set. GPT-4-assisted question synthesis is checked by humans. The task asks an LLM to identify all required root-cause elements from associated telemetry; exact-match correctness requires the complete answer, while partial accuracy is reported separately. The candidate list constrains the answer space, which aids controlled evaluation but can create a closed-set shortcut and differs from open-world diagnosis.

The dataset records failure windows and root-cause labels; the question includes a 30-minute analysis window in the described setup. Labels are tied to enterprise RCA records and engineering review rather than a controlled fault-injection script. The paper does not provide uncertainty distributions or multiple accepted causal explanations for every incident.

## Agent method and benchmark findings

The RCA-agent uses a Controller and Python Executor to iteratively generate queries over metrics, then traces and logs, keeping access to the full data while avoiding injection of all raw telemetry into the model context. The system is an analysis agent, not an environment-changing agent: no remediation/tool safety benchmark is defined. The paper reports Claude 3.5 with the RCA-agent at 11.34% fully solved cases, showing that long multimodal context and exact multi-element diagnosis remain difficult.

The paper also compares balanced and oracle sampling. Oracle sampling uses ground-truth information and must be treated as an upper-bound/proxy setting, not a fair deployable method. In one analysis, curated golden KPIs reduce the search space from 1,263 to 53; that convenience may understate the difficulty of discovering relevant signals.

## Quality, shortcut, and applicability

The paper’s engineer filtering is a useful explicit quality-control step, and multi-system telemetry better reflects operational heterogeneity than a single synthetic testbed. Risks include human-label incompleteness, answer-space leakage from supplied candidates, time-window leakage, and KPI-selection leakage in oracle settings. These are evaluation risks to audit, not proof that every reported experiment exploits them.

## Code and reproducibility

The official repository describes workflows around `main.generate`, `main.evaluate`, and `rca.run_agent_standard`; the paper-era RCA agent maps to a Controller/Python Executor workflow. The current repository includes a hardened container sandbox that may postdate the paper experiments; code version must be pinned before attempting replication. The dataset is distributed externally (the project describes external download), and this task did not download it, install dependencies, or execute code.

## Relevance

OpenRCA illustrates the value and cost of large real-system telemetry, human calibration, and compositional root-cause labels. For an Agent benchmark, add evidence/trajectory labels and actual tool/resource accounting; avoid giving the agent a candidate set unless the result is explicitly labeled closed-world. Compare to [AgenticOpsEval](../agenticopseval/notes.md) and [dataset insights](../../../notes/benchmark/dataset-design-insights.md).
