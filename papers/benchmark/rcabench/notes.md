# RCABench — Fault Propagation-Aware Microservice RCA Benchmark

## Identity and evidence status

- **Title:** *Rethinking the Evaluation of Microservice RCA with a Fault Propagation-Aware Benchmark*
- **Authors:** Aoyang Fang, Songhan Zhang, Yifan Yang, Haotong Wu, Junjielong Xu, Xuyang Wang, Rui Wang, Manyi Wang, Qisheng Lu, Pinjia He.
- **Version / venue:** arXiv:2510.04711v2 (2025-12-23); the arXiv record identifies acceptance at FSE 2026. [Paper](https://arxiv.org/abs/2510.04711)
- **Official project:** [revisiting-rca-evaluation](https://operationspai.github.io/revisiting-rca-evaluation/), now linked to [OperationsPAI/Aegis](https://github.com/OperationsPAI/aegis).
- **Local source:** [`RCABench_2510.04711.pdf`](../../../sources/papers/benchmark/RCABench_2510.04711.pdf), derived text alongside it. This was not selected by the Engine; this note synthesizes the paper text and official project material, not an Engine-certified full read or independent Judge result.

## Why this benchmark

The authors argue that common microservice RCA benchmarks make the root-cause service unusually prominent in telemetry, allowing simple correlation or rules to match sophisticated RCA methods. Their preliminary comparison reports rule-based methods at or above model performance on four existing benchmarks. RCABench targets this evaluation gap by retaining failures with observable user-facing impact and representing propagation beyond the injected component.

## Data, system, and faults

- **Environment:** TrainTicket, a 50-microservice benchmark application; injected failures run under generated, changing workloads. This is a controlled testbed, not production incidents.
- **Construction:** the framework explores 31 fault types across six categories and executes 9,152 injection experiments. It retains 1,430 validated failure cases, covering 25 fault types in six categories. The difference between attempted and retained cases is intentional: an injected fault is not automatically an operationally meaningful failure.
- **Modalities:** metrics, logs, traces, service/call topology, workload context, and user-facing SLIs are used in the generation and validation pipeline. The public paper does not provide one uniform modality-completeness guarantee per case in its summary statistics.
- **Duration / recovery:** the paper describes isolated collection cycles and environment redeployment; a single universal fault duration is **Not Reported**. Fault injection is not equivalent to recovery/remediation evaluation.

## Ground truth and propagation

Labels are hierarchical: the injection/code-level cause maps to the affected service and downstream failures along the dependency structure. The framework validates that retained cases cause a discernible SLI anomaly, filtering inert injections and cases without relevant user impact. This creates an important distinction between **injection intent** and **observed failure/impact**. The paper’s retained labels are grounded in controlled injection and system structure; they do not represent human uncertainty or competing root-cause explanations in production incidents.

## Tasks and evaluation

The paper evaluates RCA localization, including top-k service accuracy, against 11 baseline methods. It reports that performance degrades on the harder benchmark (average Top@1 0.21; best 0.37) and runtime can rise from seconds to hours. It diagnoses scalability issues, observability blind spots, and modeling bottlenecks. This is a conventional algorithm benchmark: no LLM agent tool-use, investigation trajectory, token budget, or action-safety score is defined.

## Data quality, shortcuts, and interpretation

**Reported by the authors:** weak or unreachable injection locations, injection intensity, and simple symptom patterns can make benchmarks either trivial or non-operational; 84.4% of initial attempts were classified as “No Anomaly.” SLI-based filtering and richer propagation seek to reduce those defects.

**Additional risks to test, not findings established by this paper:** a model may exploit fault-type-specific telemetry signatures, workload artifacts, or fixed injection/label associations. Random train/test splits could leak service or injection templates unless split by fault family, target, workload, or topology. Those are proposed checks, not claims that RCABench has those leaks.

## Code and reproducibility

The current official project is [Aegis](https://github.com/OperationsPAI/aegis). Its public project description maps the workflow to `aegislab/` for environment/fault/telemetry generation and `rcabench-platform/` for the Python SDK, runners, and scoring. That is a repository-level map, not a commit-pinned source audit; no code, cluster, or injection was run. The paper describes public framework, data, and baseline implementations. Reproduction still depends on matching the paper-era data and software versions rather than assuming the current repository is identical.

## Relevance to this knowledge base

RCABench supports impact-driven inclusion, explicit injection-attempt accounting, hierarchical cause-to-impact labels, and testing whether propagation makes symptoms less trivially correlated with the root. It is relevant to Network AIOps and RCA benchmark construction, but does not by itself address agent evidence quality or live remediation. Compare with [NIKA](../nika/notes.md), [OpenRCA](../openrca/notes.md), and the [dataset-design analysis](../../../notes/benchmark/dataset-design-insights.md).
