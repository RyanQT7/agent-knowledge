# Benchmark 论文清单、身份与证据状态

核验日期：2026-11-26。本专题论文范围固定为六篇；没有纳入同名或主题相近替代项。六篇均已基于本地 PDF/全文解析材料完成正文精读，按单篇笔记中列明的章节定位复核机制、案例、结果与局限；不表示所有论文都拥有可运行源码。

| # | 论文身份及发表信息 | 论文 / 官方来源 | 本地材料与阅读范围 |
| --- | --- | --- | --- |
| 1 | **Rethinking the Evaluation of Microservice RCA with a Fault Propagation-Aware Benchmark**（RCABench）；Aoyang Fang et al.; arXiv:2510.04711 v2，FSE 2026 | [论文](https://arxiv.org/abs/2510.04711) · [项目](https://operationspai.github.io/revisiting-rca-evaluation/) · [Aegis](https://github.com/OperationsPAI/aegis) | `sources/papers/benchmark/RCABench_2510.04711.pdf/.txt`；正文、图表与附录精读；Aegis 现行源码静态分析，非论文实验快照 |
| 2 | **A Network Arena for Benchmarking AI Agents on Network Troubleshooting**（NIKA）；Zhihao Wang et al.; arXiv:2512.16381 v1，2025-12-18 | [论文](https://arxiv.org/abs/2512.16381) · [官方项目](https://github.com/sands-lab/nika) | `NIKA_2512.16381.pdf/.txt`；正文/任务和实验附录精读；NIKA 当前源码静态分析，640 个论文配置与当前 release 数量分开 |
| 3 | **OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?**；Junjielong Xu et al.; ICLR 2025 | [正式论文](https://proceedings.iclr.cc/paper_files/paper/2025/file/d29b8d53678015079e1d245c023e49d2-Paper-Conference.pdf) · [项目页](https://microsoft.github.io/OpenRCA/) · [代码](https://github.com/microsoft/OpenRCA) | `OpenRCA_ICLR2025.pdf/.txt`；正文、实验与附录 case/prompt 说明精读；静态检查 generate/evaluate/Agent 路径，未下载约 68 GB 数据 |
| 4 | **Constructing Large-Scale Real-World Benchmark Datasets for AIOps**；Li Zeyan et al.; *ZTE Communications* 2026, 24(3):59–69；DOI `10.12142/ZTECOM.202603008` | [DOI](https://doi.org/10.12142/ZTECOM.202603008) · [官方 PDF](https://www.zte.com.cn/content/dam/zte-site/res-www-zte-com-cn/mediares/magazine/publication/com_en/article/en202603/20260308.pdf) | `Constructing_Large_Scale_Real_World_Benchmark_Datasets_AIOps_ZTECOM_202603008.pdf/.txt`；三数据集正文与表格精读；更正 Dataset A 来源并记录“7 KPI / 26 series”歧义；静态分析引用的 iops evaluator |
| 5 | **A Multi-Dataset Benchmark for Evaluating LLM Agents in Microservice Failure Diagnosis**（AgenticOpsEval）；Yuanhong Cai et al.; arXiv:2606.29193 v1，2026-06-28 | [论文](https://arxiv.org/abs/2606.29193) · [官方数据/项目页](https://www.aiops.cn/gitlab/aiops-live-benchmark/agenticopseval) | `AgenticOpsEval_2606.29193.pdf/.txt`；正文与附录评分、案例精读；GitLab 克隆可见 README/数据目录，但未找到 scorer 源文件，公式为论文级分析 |
| 6 | **CTBench: Evaluating Troubleshooting Capabilities of AI Agents in Realistic Telecom Network Operations**；Xingyu Yan et al.; arXiv:2608.12002 v2，2026-10-21 | [论文](https://arxiv.org/abs/2608.12002) · [HF 数据卡](https://huggingface.co/datasets/netop/CTBench) | `CTBench_2608.12002.pdf/.txt`；正文及指标、任务案例附录精读；数据文件受使用条件控制，本轮未下载；未核验独立官方源码库/scorer |

## 全文与复用边界

- 已有 PDF、文本和源码优先复用；未重新下载或运行故障注入，也未重新研究 MemFolder。当前工具列表没有 GitHub MCP，因此官方仓库版本身份通过此前保留的只读本地克隆、Git commit 和官方项目链接交叉确认。
- 本轮对 OpenRCA 和 ZTE 的本地 PDF/提取文本及官方论文页面作定向核验；其余论文使用本地 PDF/完整文本。各笔记将事实、推断和 Not Reported 分开。
- `papers/aiops/rcagentbench/` 是 **RCAgentBench**，与 RCABench 不是同一工作。
- 早前 Phase 1.5 Engine 的 NIKA/CTBench 选段任务留在 `evolution/runs/benchmark-20261125/` 作为历史运行记录；它的 partial Findings/Judge 停止状态不代表本次主会话精读结果，也不重复作为本次研究执行流程。
- 当前挑战赛原始样本、数据字典、注入脚本、标签规范和评估代码未在知识库发现；对本地数据的所有差异判断保持待补证据。

## 源码—论文对应表

| 论文 | 实际检查的源码 | 已确认内容 | 版本/访问边界 |
| --- | --- | --- | --- |
| RCABench | `aegis/rcabench-platform` 的 temporal validator、SLI sampler、evaluation；AegisLab README | 传播边时间校验、trace 聚合、当前 datapack→RCA 流程 | `OperationsPAI/aegis` SHA `979ae7011d06d21925001ce517ed40cedca529b0`；归档旧平台 SHA `a55646d66fef51c3cd11e67ccebfae5d62ac6f9b`；没有找到论文 SLI 注入筛选机制的当前直接实现，不运行 |
| NIKA | `src/nika/problems/base.py`、RCA models/scoring、`link_down.yaml` | scenario/failure/GT 分开建模、canonical resource ID、当前集合 P/R/F1 | `sands-lab/nika` SHA `7324960044f7c524d86e4859a07f260a664f79ac`；当前代码已演进，不等同于论文 evaluator |
| OpenRCA | `main/generate.py`、`main/evaluate.py`、`rca/run_agent_standard.py`、Controller/Executor | 七种标签子集任务、结构化输出评价、按需 Python 查询工作流 | `microsoft/OpenRCA` SHA `2a481ae63cb045c3eadbeca9eddaa10ec1151979`；当前有沙箱相关演进；数据未下载 |
| ZTE | `iops/evaluation/evaluation.py`；AIOps Challenge 2020 data README | delay-window onset 评分、按时间间隔补缺失标签、全局拼接 F1；独立数据包的组成 | evaluator SHA `ad962c2187d73b1a14971b255a2bd87212f896f2`；数据 README SHA `5dcea9688794f3787a9b7e4a8931c6e70fa0ec78`；没有克隆/验证 Dataset B/C 的全套生成脚本 |
| AgenticOpsEval | 当前公开 GitLab 克隆 README/目录 | 公开可见内容与论文描述之间的 scorer 可见性差异 | SHA `69cf36430b43024d02530c610b1a4738b5c9a7fb`；未发现 scorer/runner，未逐行复核或运行 |
| CTBench | 数据卡、论文提供的交互和指标说明 | replay、黄金动作、答案和覆盖率定义来自论文描述 | 没有独立代码仓库已核验；数据需接受 Hugging Face 使用条件，未下载 |

所有外部源码均只读静态分析；没有安装复杂依赖或执行第三方代码。
