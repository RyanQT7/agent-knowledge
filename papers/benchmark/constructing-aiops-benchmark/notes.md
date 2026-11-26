# Constructing Large-Scale Real-World Benchmark Datasets for AIOps

## Identity and evidence status

- **Title:** *Constructing Large-Scale Real-World Benchmark Datasets for AIOps*
- **Authors:** Li Zeyan, Han Jing, Zhao Nengwen, Zhang Shenglin, Sun Yongqian, Chen Pengfei, Wen Xidao, Ma Minghua, Pei Dan.
- **Publication:** ZTE Communications, 2026, Vol. 24 No. 3, pp. 59–69; published online 2026-09-03. DOI [10.12142/ZTECOM.202603008](https://doi.org/10.12142/ZTECOM.202603008); [official PDF](https://www.zte.com.cn/content/dam/zte-site/res-www-zte-com-cn/mediares/magazine/publication/com_en/article/en202603/20260308.pdf).
- **Related official code/data:** [KPI anomaly detection](https://github.com/netmanaiops/kpi-anomaly-detection), [MultiDimension-Localization](https://github.com/NetManAIOps/MultiDimension-Localization), [AIOps Challenge 2020 data](https://github.com/NetManAIOps/AIOps-Challenge-2020-Data), [evaluation code](https://github.com/iopsai/iops/tree/master/evaluation).
- **Local source:** [`Constructing_Large_Scale_Real_World_Benchmark_Datasets_AIOps_ZTECOM_202603008.pdf`](../../../sources/papers/benchmark/Constructing_Large_Scale_Real_World_Benchmark_Datasets_AIOps_ZTECOM_202603008.pdf). Engine did not select this paper; note reflects local text and the official article, not an Engine full read.

## Contribution and three distinct datasets

The paper’s main contribution is a construction account spanning three AIOps challenge datasets, not one unified multimodal corpus. It argues that public, reusable operational data is scarce and that competition use can test whether a dataset supports reproducible comparison.

### Dataset A — production KPI anomaly detection

The data comes from five company sources (Sogou, eBay, Tencent, Suning, and China Mobile Zhejiang). The preliminary release table reports 26 KPI series, 4,821,526 points, series lasting 60–207 days, and highly imbalanced anomaly ratios; evaluation includes delayed alarm detection. The prose also refers to seven KPIs with engineer labels, leaving a scope/count ambiguity between KPI concepts and released series. Preserve that ambiguity rather than resolving it by assumption. Best competition F1 reported by the paper is 0.8216.

### Dataset B — multidimensional root-cause localization

This comprises 400 labeled cases built from structured production-style measures. The paper describes an explicit synthesis pipeline: choose root-cause attribute combinations, inject anomalies at smooth time points, modify aggregate measures with a GRE-based procedure, add Gaussian noise, and filter cases where attributes become indistinguishable or unaffected measures become abnormal. This is a valuable example of screening synthetic data for confounding, but its causal validity depends on whether the constructed relationships match operational mechanisms.

### Dataset C — failure discovery and diagnosis

Dataset C uses China Mobile Zhejiang’s sysA service environment, with service/OSB/database/container/OS components and metrics, KPIs, traces, and fine-grained measures. The paper describes 169 injected failures across seven injection types, including database close/session limits and container/node CPU, delay, and loss faults. Labels include fault time and root causes; scripts/operational steps are part of its reproducibility story. The publication does not establish that every failure type models the full range of production faults.

## Ground truth, tasks, and evaluation

Dataset A uses experienced-engineer anomaly labels and delayed-alarm constraints. Dataset B defines injected root-cause attribute combinations and evaluates localization with F1. Dataset C ties diagnosis labels to controlled injection and observed system behavior; its evaluation distinguishes valid submissions and uses precision thresholds with time/F0.5-based ranking in the competition protocol. These tasks are different and should not be collapsed into a single “AIOps score.”

The paper presents repeated challenge use (2018–2020, 400+ participating teams across competitions) as evidence of practical utility and reproducibility. Participation is not itself evidence that labels are causally complete or that shortcut learning is absent.

## Data quality and risks

**Author-described methods:** real-system KPI sources; expert labels; synthetic-case filtering; controlled failure injection; release of data/code; challenge evaluation.

**Analysis risks, not confirmed defects:** engineered attributes and injected signatures may identify a class without learning causal behavior; event-time placement can leak labels; classes and component roles may correlate; long-tail categories can make aggregate metrics misleading. Use group splits by event family, host/service, time, and injection template. Report class-level coverage and uncertainty. The paper’s scope ambiguity for Dataset A is a documentation issue, not proof that its labels are wrong.

## Code and openness

The paper cites separate repositories for KPI detection, multidimensional localization, challenge data, and evaluation. Their scopes differ; they are not one executable benchmark platform. The article and repository links were inspected, but the repositories were not cloned or run and no fault injection was executed. Reproduction requires identifying the correct dataset release and evaluator for each task.

## Relevance

This paper is most useful for dataset lineage, synthetic confounder screening, event-time/latency-aware evaluation, and separating anomaly detection from localization and diagnosis. Its data lineage does not establish that our challenge data has the same characteristics. Compare with [RCABench](../rcabench/notes.md) for impact validation and [dataset design insights](../../../notes/benchmark/dataset-design-insights.md).
