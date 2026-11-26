# CTBench — Telecom Troubleshooting Agent Benchmark

## Identity and evidence status

- **Title:** *CTBench: Evaluating Troubleshooting Capabilities of AI Agents in Realistic Telecom Network Operations*
- **Authors:** Xingyu Yan, Tingting Dai, Antonio De Domenico, Mohamed Sana, Nicola Piovesan, Changchang Li, Bowen Liu, Kun Jiang, Mengjie Zhang, Dingcheng Shan, Jing-Cheng Pang, Chenwei Wu, Sijie Wu, Lianying Chao, Haoran Cai, Jiantao Ye, Xubin Li, Simon Mark Lucas, Xin Chen.
- **Version / venue:** arXiv:2608.12002v2 (2026-10-21); no venue listed on arXiv. [Paper](https://arxiv.org/abs/2608.12002)
- **Official dataset:** [Hugging Face netop/CTBench](https://huggingface.co/datasets/netop/CTBench). No separate official code repository was verified.
- **Local source:** [`CTBench_2608.12002.pdf`](../../../sources/papers/benchmark/CTBench_2608.12002.pdf). Engine selected it for section-level analysis (`sections_only`); Judge did not complete. This note is not independently Judge-accepted.

## Motivation, environment, and task

CTBench targets telecom troubleshooting under partial observability, vendor heterogeneity, multi-hop propagation, and operational safety constraints. Its 234 expert-curated tasks consist of 126 RCA tasks and 108 path-restoration tasks. Sources are sanitized maintenance cases and recorded CLI outputs from multi-vendor network devices. A replay backend presents recorded outputs; this is more realistic than a static question but is not a live network or a dynamic repair environment.

Task metadata captures observability, topology/protocol complexity, propagation and fault multiplicity. Input modalities are principally device CLI observations and network/topology context; the paper does not present a standardized metrics/logs/traces corpus comparable to OpenRCA’s or AgenticOpsEval’s.

## Ground truth and quality control

Fifteen senior telecom experts authored candidate tasks. Independent experts blindly solved and reviewed answer, completeness, consistency, and reference actions without seeing ground truth/routes. Of 359 candidates, 234 were retained; 154 required revision during curation. RCA truth is a normalized `(node, object, cause)` tuple; path restoration truth is an ordered path. Golden evidence actions define a reference route. This review process strengthens task solvability and answer quality, while the benchmark remains expert-curated and may not capture all legitimate operational paths.

## Agent process and evaluation

The agent interacts with a tool interface that replays pre-collected CLI responses. The paper separates final task accuracy/localization/path metrics from **golden-action coverage** and reports latency, interaction rounds, and tokens. The paper’s experiments show that agents can answer correctly while missing many expert reference actions. However, the replay interface intentionally excludes alternative commands that might yield equivalent evidence. Exact route coverage therefore measures adherence to one reference evidence path, not proof that the agent’s answer was unsupported or that it failed to observe equivalent evidence.

Each task receives one Pass@1 execution and a 3,600-second timeout. The paper imposes no per-task cap on tool steps, interaction rounds, or cumulative tokens. Thus reported resource descriptors are not a bounded-cost deployment guarantee. The benchmark evaluates diagnosis and path recovery answers, not dynamic network repair or safe remediation.

## Data quality and shortcut risks

**Author-reported limitations:** fixed replay does not model changing live state or dynamic repair; golden routes are specific reference paths; the system is sanitized. **Further risks to test:** CLI output templates may reveal task identity; fixed commands/recorded responses may reward route memorization; expert route coverage may penalize valid alternate workflows. Use held-out devices, vendors, protocol families, and task templates; permit semantically equivalent evidence while separately recording the route.

## Code and openness

The paper and public dataset card expose task data and evaluation description. A standalone official source repository was not verified; scorer source-level analysis and local execution were not performed. The benchmark uses a mock/replay backend and has no dynamic production environment in the paper.

## Relevance

CTBench’s strongest contribution is to make diagnostic process visible and attach task difficulty metadata. Its route metric should be interpreted narrowly. A network benchmark for our use should preserve multi-hop topology reasoning but score evidence sufficiency and equivalent diagnostic paths separately from exact command matching. See [NIKA](../nika/notes.md) and [dataset design insights](../../../notes/benchmark/dataset-design-insights.md).
