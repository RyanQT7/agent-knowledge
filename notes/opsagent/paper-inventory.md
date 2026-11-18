# OpsAgent 论文清单（截至 2026-11-17）

“OpsAgent”在此处通常表示 **Agents for IT Operations** 研究分类；表内标成“系统专名”的论文指 NKU 的具体 OpsAgent 论文。状态区分 peer-reviewed venue、预印本、阅读全文与仅筛查。我们没有把 arXiv 自动视为会议发表。

## 正式全文阅读

| Paper | 年份 / 状态 | 对应问题 | 阅读和源码状态 | 笔记 |
|---|---|---|---|---|
| OpsAgent: An Evolving Multi-agent System for Incident Management in Microservices | ASE 2026 Companion Industry Showcase；arXiv v3 | M/L/T 标准化、AD/FT/RCL、交叉评阅、自演化 | 全文；官方 `Johnn13/OpsAgent` 静态阅读，SHA `6d61b8b`，无 LICENSE | [笔记](../../papers/opsagent/opsagent-system.md) |
| KRCA: An Efficient Root Cause Analysis System in Hyper-scale Microservice Systems via Agentic AI | ASE 2026；arXiv v3 | API/拓扑候选缩减、因果骨架、子 Agent 验边 | 全文；官方源码未找到 | [笔记](../../papers/opsagent/krca.md) |
| OpsMem: Dual-Memory Reasoning with Cross-Memory Resonance for Failure Diagnosis | ISSRE 2026 Industry Track；arXiv v1 | 事件 STM + 经验 LTM + 记忆共振 | 全文；官方 `gaorch85/OpsMem` 静态阅读，SHA `a225802`，Apache-2.0 | [笔记](../../papers/opsagent/opsmem.md) |
| Graph of States: Solving Abductive Tasks with Large Language Models | ICML 2026 / PMLR 306 | 假设图、证据支持/反驳、层级回溯 | 全文；官方 `gaorch85/Graph-of-States` 静态阅读，SHA `0f28c2e`，MIT | [笔记](../../papers/opsagent/graph-of-states.md) |
| Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States (PoS) | arXiv 2610.01415v1；未核实发表 venue | 显式世界状态、未解要求、停滞检测和约束恢复 | 全文；官方 `luoyu100/PoS` 静态阅读，SHA `6818cfa`，MIT | [笔记](../../papers/opsagent/pos.md) |
| FlowXpert: Expertizing Troubleshooting Workflow Orchestration with Knowledge Base and Multi-Agent Coevolution | KDD ’25 | 网络排障 Workflow 与 Generator/Evaluator 共演化 | 全文；论文/实验数据不开放，无官方代码链接 | [笔记](../../papers/opsagent/flowxpert.md) |
| KnowLution: A Multi-Agent Framework for Execution-Oriented Autonomous Operations in Production Supercomputers | ISSRE 2026 | 运行时状态 grounding、权限约束、工具执行 | 全文；论文/数据不公开，无官方代码链接 | [笔记](../../papers/opsagent/knowlution.md) |
| Rethinking Tool Design for Agentic RCA: A Controlled Empirical Study (ToolRCA) | arXiv 2610.05009v1；未核实发表 venue | 工具抽象层与组合对 Agent RCA 的影响 | 全文；作者项目页没有代码仓链接 | [笔记](../../papers/opsagent/toolrca.md) |

## 补充筛查与阅读队列

| Paper / 方向 | 状态与判断 | 值得读的原因 / 新颖性 | 决定 |
|---|---|---|---|
| Large Language Models for Agentic NetOps and AIOps: Architectures, Evaluation, and Safety | arXiv:2605.12729（2026-05-12）；截至截止日期按预印本引用。之后网页显示 2027 期刊出版，不能倒写到 2026 状态。未全文阅读 | 以 autonomy、tool scope、evidence trace、assurance contracts 组织 NetOps/AIOps；是横向综述，不是实现系统 | 保留为综述补读，暂不进入核心方法比较 |
| PAGE: Progress-Aware Reinforcement Learning with Hierarchical Advantage for Long-Horizon GUI Agents | NKU 列为 EMNLP 2026；补充筛查，未全文阅读 | 通过进度信号做长程 GUI policy 学习；对象是 GUI，不能据此声称运维 Agent 已实现相同方法 | 作为跨领域 Skill/进度学习队列，不纳入 AIOps 系统结论 |
| Prism: Knowledge Management for Root-Cause Analysis and Mitigation in Serverless Computing | NKU 列为 ISSRE 2026；官方会程列于 RCA and Failure Management / industry。截止检索未取得可读全文或代码链接 | Serverless 根因和缓解知识管理，有机会扩展 AIOps 从 diagnosis 到 mitigation | 补齐正式 PDF 后优先阅读；当前仅元数据核验 |
| Large Language Models for Agentic NetOps and AIOps 与 `Why Transformers? A Comprehensive Overview of Transformers in AI for IT Operations` | NKU/作者源列为综述；后者刊于 TOSEM 2026，前者截止日期按 arXiv | 对分类、评测、安全威胁提供全景，和本文逐篇方法评估互补 | 不把综述的 future directions 当作已实现方案 |
| OpsAgent 的其他相邻 2026 工作：MERA、票据+日志事故分流、FSE Aloha、ChainCraft、FoundRoot、FSE lag-aware RCA、ToolRCA | NKU/NetMan 官方发表清单核验标题/venue；除 ToolRCA 外未逐篇全文阅读 | 覆盖人工协同、工单/日志、因果约束和 delay-aware RCA；各自解决不同子任务 | 在当前范围之外，不因数量而无限扩张 |

## 去重与关系

- 复用现有 [CHIEF](../../papers/aiops/chief/notes.md) 的多级 Agent 归因分析和 [FlowFixer](../../papers/aiops/flowfixer/notes.md) 的工作流修复笔记。
- OpsMem 的 STM 吸收 GoS 的当前诊断假设图，并增加跨事件 LTM；不是同一系统。
- PoS 是 long-horizon 显式信念与停滞恢复框架；不是 OpsMem 的长期记忆，也不是 PoS 论文标题中的“存储全部 history”。
- FlowXpert 研究 workflow generation/evaluation；NKU OpsAgent 和 KRCA 研究 incident diagnosis；KnowLution 研究执行安全。功能重叠有限，不应合并为一种 Agent 架构。

## 发现数量口径

本库存有 8 篇全读笔记；其中首要指定论文 5 篇全部全文阅读，另外全文阅读 FlowXpert、KnowLution 和 ToolRCA。补充表另列 4 组正式核验但未进入全读的论文/方向。论文笔记均有 Section/Figure/Table 级依据；仅筛查条目明确标出未全文阅读。
