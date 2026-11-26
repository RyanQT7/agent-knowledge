# Benchmark 论文清单与来源核验

核验日期：2026-11-25。固定范围共六篇；没有将相近名称工作替换进来。

| # | 论文身份、作者、发表信息 | 论文来源 | 官方项目 / 数据 / 代码 | 本地来源与阅读状态 |
| --- | --- | --- | --- | --- |
| 1 | **Rethinking the Evaluation of Microservice RCA with a Fault Propagation-Aware Benchmark**（RCABench）；Aoyang Fang, Songhan Zhang, Yifan Yang, Haotong Wu, Junjielong Xu, Xuyang Wang, Rui Wang, Manyi Wang, Qisheng Lu, Pinjia He；arXiv:2510.04711 v2，2025-12-23；arXiv 页面标注 FSE'26 接收 | [arXiv](https://arxiv.org/abs/2510.04711)；[项目页](https://operationspai.github.io/revisiting-rca-evaluation/) | 官方项目现指向 [OperationsPAI/aegis](https://github.com/OperationsPAI/aegis)，含 `aegislab/` 平台与 `rcabench-platform/` 评估框架 | PDF 与 arXiv HTML 派生文本在 `sources/papers/benchmark/`；专题新增单篇笔记。Engine 本轮未选中；专题按论文相关段落分析，不计全文精读 |
| 2 | **A Network Arena for Benchmarking AI Agents on Network Troubleshooting**（NIKA）；Zhihao Wang, Alessandro Cornacchia, Alessio Sacco, Franco Galante, Marco Canini, Dingde Jiang；arXiv:2512.16381 v1，2025-12-18；页面未列会议发表信息 | [arXiv](https://arxiv.org/abs/2512.16381) | [sands-lab/nika](https://github.com/sands-lab/nika)，当前网站说明当前 release | 本地 PDF/HTML；Engine Planner 选中。Executor 读取 §3.3.3、§4.1–4.2、§5 等章节，标记 `sections_only`。独立 Judge 因预算停止未完成 |
| 3 | **OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?**；Junjielong Xu, Qinan Zhang, Zhiqing Zhong, Shilin He, Chaoyun Zhang, Qingwei Lin, Dan Pei, Pinjia He, Dongmei Zhang, Qi Zhang；ICLR 2025 | [ICLR 正式论文](https://proceedings.iclr.cc/paper_files/paper/2025/file/d29b8d53678015079e1d245c023e49d2-Paper-Conference.pdf)；[OpenRCA 项目](https://microsoft.github.io/OpenRCA/) | [microsoft/OpenRCA](https://github.com/microsoft/OpenRCA) | 本地 PDF 与官方 PDF 文本；Engine 未处理；使用论文、项目 README 与核心工作流描述分析，未计 Engine 全文精读 |
| 4 | **Constructing Large-Scale Real-World Benchmark Datasets for AIOps**；Li Zeyan, Han Jing, Zhao Nengwen, Zhang Shenglin, Sun Yongqian, Chen Pengfei, Wen Xidao, Ma Minghua, Pei Dan；ZTE Communications 2026, Vol. 24 No. 3, pp. 59–69；online 2026-09-03；DOI `10.12142/ZTECOM.202603008` | [DOI](https://doi.org/10.12142/ZTECOM.202603008)；[期刊 PDF](https://www.zte.com.cn/content/dam/zte-site/res-www-zte-com-cn/mediares/magazine/publication/com_en/article/en202603/20260308.pdf) | 论文引用 [KPI anomaly detection](https://github.com/netmanaiops/kpi-anomaly-detection)、[MultiDimension-Localization](https://github.com/NetManAIOps/MultiDimension-Localization)、[AIOps Challenge 2020 data](https://github.com/NetManAIOps/AIOps-Challenge-2020-Data)；评估实现还引用 [iopsai/iops/evaluation](https://github.com/iopsai/iops/tree/master/evaluation) | 本地 PDF 与官方期刊 PDF 的选段文本；Engine 未处理；单篇分析明确分开 Dataset A/B/C，并记录论文表述中的范围差异 |
| 5 | **A Multi-Dataset Benchmark for Evaluating LLM Agents in Microservice Failure Diagnosis**（AgenticOpsEval）；Yuanhong Cai, Xiaohui Nie, Kanglin Yin, Changhua Pei, Yongqian Sun, Shenglin Zhang, Haibin Liu, Guiyang Liu, Xidao Wen, Fang Situ, Dan Pei；arXiv:2606.29193 v1，2026-06-28 | [arXiv](https://arxiv.org/abs/2606.29193) | [官方数据/项目页](https://www.aiops.cn/gitlab/aiops-live-benchmark/agenticopseval)；论文报告提供 scoring code | 本地 PDF/完整 arXiv HTML 派生文本；Engine 未处理。分析含 AIOps2025 与 RCA100。GitLab 项目文件无法展开，未声称逐文件检查评分代码 |
| 6 | **CTBench: Evaluating Troubleshooting Capabilities of AI Agents in Realistic Telecom Network Operations**；Xingyu Yan, Tingting Dai, Antonio De Domenico, Mohamed Sana, Nicola Piovesan, Changchang Li, Bowen Liu, Kun Jiang, Mengjie Zhang, Dingcheng Shan, Jing-Cheng Pang, Chenwei Wu, Sijie Wu, Lianying Chao, Haoran Cai, Jiantao Ye, Xubin Li, Simon Mark Lucas, Xin Chen；arXiv:2608.12002 v2，2026-10-21 | [arXiv](https://arxiv.org/abs/2608.12002) | [Hugging Face 数据集](https://huggingface.co/datasets/netop/CTBench)；未核验到独立官方代码仓库 | 本地 PDF/完整 arXiv HTML 派生文本；Engine Planner 选中并读取 §3.2–3.3、§4.1–4.3、§5.1、§7 与 Appendix D.3 等，标记 `sections_only`。Judge 未完成 |

## 阅读边界

- `papers/aiops/rcagentbench/notes.md` 及同名 PDF 是 **RCAgentBench**，标题、任务和 Benchmark 均不同于此处 RCABench，故只在名称辨析中提及。
- Engine 只产生 NIKA/CTBench 五条候选 Findings；四条单篇 Findings 的来源/版本/locator 可由确定性检查核验。跨论文 Finding 的复合 `source_id` 与单源 schema 不匹配，确定性门禁失败；Judge 被预算停止，五条均未被 Engine 接受为 Claim。
- 本轮 Engine 对六篇的 `full_text` 计数为 0。专题文档以“论文相关章节分析”描述，不把摘要检索或部分 PDF 页面当作全文精读。
- AIOps challenge 的实际数据文件、数据字典、注入脚本和标签定义未在当前知识库发现。本文对该数据集只能基于用户列出的风险作待核查问题，不称为已证实的真实案例。

逐篇的 Benchmark 设计、Ground Truth、数据质量、任务/指标及源码可见范围见 [`papers/benchmark/`](../../papers/benchmark/) 下六份笔记。

## 核心源码范围映射

| 论文 | 可检查的官方实现单元 | 这轮可确认的机制 | 未做的事 |
| --- | --- | --- | --- |
| RCABench | `aegislab/` 注入—采集平台；`rcabench-platform/` Python SDK/评估器 | 当前 Aegis README 说明 fault injection → telemetry datapack（带 ground truth）→ RCA runner/scoring 的流水线；与论文时期代码/版本差异需要按 release/SHA 进一步锁定 | 未拉取或运行平台、K8s、Chaos Mesh、评估代码；当前仓库是项目后续整合形态 |
| NIKA | `src/`、`benchmark/`、`config/`、Agent Access Layer；创建任务文档 | 论文定义 `(network scenario, issue, traffic)` 与 task goal；Orchestrator 复现故障，AAL 暴露结构化 MCP 工具并记录调用/状态，goal-specific evaluator 评估 | 本轮 Executor 未做逐文件源码读取；当前主分支已演进，README 当前任务数不是论文任务数 |
| OpenRCA | `main.generate`、`main.evaluate`、`rca.run_agent_standard`、`rca/baseline/rca_agent` | 任务生成从七种 root-cause-element 子集选择目标、结合时间窗并生成人类式 query；评估以要求元素完全匹配为准；RCA-agent 用 Controller + Python Executor 保留全局数据查询能力 | 当前 GitHub 主分支增加容器沙箱；不等同于论文实验 commit。未运行代理、安装依赖或下载数据 |
| ZTE 三数据集 | 论文引用的 KPI detection、MultiDimension-Localization、AIOps 2020 data；`iops/evaluation` | Dataset B 的 GRE + 噪声合成和两项 Shortcut 检查；Dataset C 七类注入、记录故障标签；Dataset A 评估延迟约束 | 没有将三个 repo 当成一个系统；未克隆或运行数据/挑战评估 |
| AgenticOpsEval | 官方 GitLab 项目；论文提供 JSON 标注与三个维度评分协议 | AIOps2025 每模态 key evidence；RCA100 按 cause→propagation→impact 的链步骤与 evidence checkpoint 计分 | GitLab 当前不能从阅读工具展开，未宣称源码逐文件核查；未运行评分脚本 |
| CTBench | HF 数据集任务、metadata、golden actions、答题输出及评分说明 | RCA tuple/path answer 与 expert action/evidence coverage 分开计算；路径 coverage 是对一条指定 reference route 的代理指标 | 未下载任务数据、未核验每个文件版本或运行 scorer；论文明确说 replay backend 非动态修复 |

源码来源均为公开项目文档和论文对实现的说明；本轮未执行第三方代码。为避免把当前 `main` 错当成论文实验版本，项目数据规模、评估方式和代码状态分别在各单篇笔记中注明。
