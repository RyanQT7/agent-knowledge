# Agent Research Directions 2026

**截止：2026-11-17。** 这是本知识库按阅读论文所作的研究地图，不是领域官方分类或 SOTA 排名。成熟度表示这些材料中机制/证据的状态；2026 年发表本身不构成领先性证明。预印本与同行评审论文在各自笔记中分开标注。

## 方向地图

### 1. Agentic Reasoning

- **研究问题：** 如何让模型根据不断到来的证据形成、更新并比较假设，而不是只生成一段可信解释？
- **为什么重要：** 运维、软件工程和长程任务有部分可观测、矛盾信息与高代价错误。
- **代表论文：** [Graph of States](../../papers/opsagent/graph-of-states.md)、[ReAct](../../papers/react/notes.md)、[RAP](../../papers/rap/notes.md)、[OpsAgent](../../papers/opsagent/opsagent-system.md)。
- **核心技术：** 假设图、支持/反驳证据、tool observation、回溯和结构化输出。
- **最新进展：** GoS 将 abduction 表达为状态/假设图并允许层级回溯；OpsAgent 将多模态摘要与角色化分析组成 incident workflow。
- **当前局限：** 假设图由模型维护仍可能漏证或过度自信；流畅解释不等于因果正确。
- **研究价值：** 把 hypothesis、证据来源、反证与弃权变成可校验的状态对象。

### 2. Planning

- **研究问题：** 何时先生成完整计划，何时根据新 Observation 逐步选择行动？
- **为什么重要：** 固定步骤容易审计，开放故障需要适应；错误的早期计划会级联浪费预算。
- **代表论文：** [ReAct](../../papers/react/notes.md)、[LLM+P](../../papers/llm-p/notes.md)、[RAP](../../papers/rap/notes.md)、[ReWOO](../../papers/rewoo/notes.md)、[FlowXpert](../../papers/opsagent/flowxpert.md)。
- **核心技术：** 显式 planner、计划图、搜索、工具执行和分支调度。
- **最新进展：** 从提示内规划扩展到 workflow 生成/评分及受约束执行；ToolRCA 的实证显示工具抽象层和组合会改变 RCA 质量/延迟，规划能力不应与工具设计割裂。
- **当前局限：** 计划文本不一定可执行；静态计划没有自动验证执行后的状态；动态重规划可能增加调用成本和风险。
- **研究价值：** 在确定性 SOP 与证据触发的动态分支之间建立边界清晰的混合策略。

### 3. Long-horizon Agent

- **研究问题：** 如何在长任务中避免目标漂移、忘记约束、重复行动和假装完成？
- **为什么重要：** 长程任务的失败常来自多步累积，不只来自单次推理。
- **代表论文：** [PoS / Beyond Memory](../../papers/opsagent/pos.md)、[PAGE（补充筛查）](https://nkcs.iops.ai/publications/)。
- **核心技术：** 显式 belief state、未满足条件、进度/停滞检测、分层进度信号。
- **最新进展：** PoS 以状态中的知识缺口与停滞分类约束长任务的下一步选择；PAGE 面向 GUI 长程任务研究进度感知强化学习，当前仅元数据筛查。
- **当前局限：** PoS 是截至截止日未核实发表 venue 的预印本，状态更新和检查仍依赖模型；GUI 结果不能直接外推到 IT 运维。
- **研究价值：** 让系统判断“尚未完成什么、根据什么相信完成”，并由外部检查器确认进展。

### 4. Memory / Belief State

- **研究问题：** 如何分别保存短时事件上下文、跨事件经验和对外部世界的当前信念？
- **为什么重要：** 原样保留对话历史会混入过时、重复或互相矛盾的信息，也没有明确表示现实状态。
- **代表论文：** [OpsMem](../../papers/opsagent/opsmem.md)、[Graph of States](../../papers/opsagent/graph-of-states.md)、[PoS](../../papers/opsagent/pos.md)、[Reflexion](../../papers/reflexion/notes.md)。
- **核心技术：** STM/LTM 分层、经验检索、状态图、显式目标/信念与约束检查。
- **最新进展：** OpsMem 用事件内图与跨事件经验配合诊断；PoS 将长程状态与完成条件分开建模。
- **当前局限：** 记忆污染、过时经验、反馈偏差、来源丢失和状态写入错误；OpsMem 公开复现材料有限。
- **研究价值：** 将 memory item 版本化并附带来源、适用范围、时效和反证状态。

### 5. Skill Learning

- **研究问题：** Agent 如何从成功/失败尝试中获取可复用操作程序，并知道何时不适用？
- **为什么重要：** 每次重新探索成本高，但无条件复用会把旧环境的步骤套到新环境。
- **代表论文：** [OpsAgent](../../papers/opsagent/opsagent-system.md)、[FlowXpert](../../papers/opsagent/flowxpert.md)、[PAGE（GUI 相邻方向）](https://nkcs.iops.ai/publications/)。
- **核心技术：** 从工单/轨迹抽取 workflow，生成与评分器共演化，依据人工接受反馈更新。
- **最新进展：** FlowXpert 把生成工作流与可执行性/接受率评估关联；NKU OpsAgent 报告人工确认后的处置反馈与离线演化。
- **当前局限：** 选择偏差、环境漂移、错误技能传播与更新因果效应未充分隔离；接受不必然代表长期安全。
- **研究价值：** 技能需要版本、前置条件、证据、失败边界、回滚和失效检测。

### 6. Multi-Agent Coordination

- **研究问题：** 多角色分工何时带来互补证据，何时只是复制模型错误并增加通信？
- **为什么重要：** 复杂故障横跨服务、指标、日志、拓扑和组织边界，但协调本身也会引入失败。
- **代表论文：** [TraJudger](../../papers/agentops/trajudger.md)、[OpsAgent](../../papers/opsagent/opsagent-system.md)、[OpsMem](../../papers/opsagent/opsmem.md)、[KnowLution](../../papers/opsagent/knowlution.md)、[ChatRCA（已有笔记）](../../papers/aiops/chatrca/notes.md)。
- **核心技术：** Coordinator/worker、专业角色、共享状态、交叉审阅、显式委派与结构化 handoff。
- **最新进展：** 研究开始从“角色提示词”转向记录 delegation、依赖和错误传播链。
- **当前局限：** Agent 数量增加不证明系统更可靠；共享状态污染、重复工具调用、协调开销和共同偏差难评。
- **研究价值：** 通过 single-agent 控制组、消融、交互轨迹与责任归因量化真实协作增益。

### 7. Agent Self-Evolution

- **研究问题：** 如何安全地把反馈转换成提示、工具、工作流或记忆的改进？
- **为什么重要：** 人工审核成本高，自动更新又可能造成静默退化。
- **代表论文：** [NKU OpsAgent](../../papers/opsagent/opsagent-system.md)、[FlowXpert](../../papers/opsagent/flowxpert.md)、[PROBE](../../papers/agentops/probe.md)。
- **核心技术：** 反馈归档、反思、规则/工作流修订、离线排序或优化、下一次尝试指导。
- **最新进展：** 系统开始区分个案恢复与离线策略更新；PROBE 的范围是有证据门控的后续重试指导，不是自动修改运行中模型。
- **当前局限：** 缺乏归因更新收益、回归测试覆盖不足、生产反馈标签存在选择偏差。
- **研究价值：** 建立 shadow evaluation、版本对照、回放集和可回滚的更新门禁。

### 8. Agent Observability

- **研究问题：** 运行时至少记录什么才能重建模型“看到什么”、工具“做了什么”和状态“如何变化”？
- **为什么重要：** 传统服务 trace 记录请求跨进程传播，但通常不记录语义决策、共享 Agent 状态或委派因果关系。
- **代表论文：** [Trial by Trace](../../papers/agentops/trial-by-trace.md)、[TraceElephant（下一轮建议精读）](../../notes/agentops/paper-inventory.md)、[Taming Uncertainty](../../papers/agentops/taming-uncertainty.md)。
- **核心技术：** Agent identity、时间戳、prompt/context、工具调用/结果、状态快照、handoff、依赖、验证结果。
- **最新进展：** harness 被作为独立可靠性对象评测，完整轨迹和部分轨迹对归因质量的影响成为研究问题。
- **当前局限：** 隐藏/压缩上下文、缺失依赖、敏感信息、存储费用和不同框架 schema 不兼容。
- **研究价值：** 定义可重放、隐私受控、跨框架的 trace contract。

### 9. Failure Attribution

- **研究问题：** 如何找出首个造成失败的步骤和 Agent，并区分根因、传播、症状？
- **为什么重要：** 终端输出者可能只是继承了上游错误；修错位置会导致重试无效。
- **代表论文：** [AgentRx](../../papers/agentops/agentrx.md)、[TraJudger](../../papers/agentops/trajudger.md)、[CHIEF](../../papers/aiops/chief/notes.md)、[FlowFixer](../../papers/aiops/flowfixer/notes.md)。
- **核心技术：** 轨迹规范化、静态/动态约束、happened-before/conduit 图、反向依赖追踪、层级归因。
- **最新进展：** 从终点正确率转向 step-level、agent-level、failure type 和 propagation chain 评估。
- **当前局限：** Ground truth 昂贵且主观；轨迹部分缺失时因果边难确证；Judge 与被评系统可能共享偏差。
- **研究价值：** 用独立证据、多个标注者和不确定/多根因标签校准归因器。

### 10. Agent Verification

- **研究问题：** 如何验证证据、推断、工具副作用、修复与恢复各自成立？
- **为什么重要：** Agent 的自我检查是另一次模型输出，并不自然独立于原始错误。
- **代表论文：** [AgentRx](../../papers/agentops/agentrx.md)、[TraJudger](../../papers/agentops/trajudger.md)、[PoS](../../papers/opsagent/pos.md)、[KnowLution](../../papers/opsagent/knowlution.md)、[AIOps Verification Concept](../../concepts/aiops/verification.md)。
- **核心技术：** schema/不变量、运行时状态检查、新鲜工具查询、拓扑约束、人工审批、执行后恢复信号。
- **最新进展：** 诊断质量开始与 execution outcome、harness 事件和证据 provenance 分开讨论。
- **当前局限：** checker 只检查其观察到的状态；独立性、成本、延迟和人工吞吐仍是问题。
- **研究价值：** 把验证对象、判据、数据源和失败处置分别显式化。

### 11. Agent Safety

- **研究问题：** 如何约束 tool 权限、参数、数据泄露、重试副作用和生产变更？
- **为什么重要：** 诊断错误影响工作量，写操作错误可能造成停机或扩大事故。
- **代表论文：** [KnowLution](../../papers/opsagent/knowlution.md)、[Agent System Operations](../../papers/agentops/agent-system-operations.md)、[AIOps Verification](../../concepts/aiops/verification.md)。
- **核心技术：** read-only 默认、typed tool/schema、sandbox、最小权限、人工确认、前置条件、rollback。
- **最新进展：** 运维 Agent 论文开始描述执行权限和确认步骤；各系统的安全边界仍不同。
- **当前局限：** 通过沙箱或人工 gate 不代表故障诊断正确，也不自动证明恢复成功；安全测试集覆盖不足。
- **研究价值：** 以风险分级、不可绕过的 runtime policy 和可观测变更结果作为架构基础。

### 12. Agent Benchmarking / Harness Reliability

- **研究问题：** 如何把模型能力、任务难度、工具集、harness 和运行随机性分别评估？
- **为什么重要：** 最终正确率难指出失败属于 Agent、运行时、工具还是数据。
- **代表论文：** [Trial by Trace](../../papers/agentops/trial-by-trace.md)、[AgentRx](../../papers/agentops/agentrx.md)、[Cloud-OpsBench（已有 AIOps 知识）](../../papers/aiops/cloud-opsbench/notes.md)、[RCAgentBench](../../papers/aiops/rcagentbench/notes.md)。
- **核心技术：** 多维 harness 分数、step-level ground truth、确定性环境、工具轨迹、成本/延迟和恢复指标。
- **最新进展：** 评测开始要求记录轨迹与 harness 行为，而非只给 task success。
- **当前局限：** 数据集范围偏窄、标签质量不一、随机运行和生产分布漂移处理不足。
- **研究价值：** 报告多次运行、区间估计、工具/Agent/harness 消融、检测延迟、误报和独立恢复率。

## 阶段性归纳

- **工程上较成熟的组件：** 受限工具接口、明确循环终止、结构化 trace、schema/权限检查、固定 SOP 分支、人工审批。这些组件成熟不等于 Agent 整体自主可靠。
- **2026 年较活跃：** 长程显式状态、跨事件记忆、Agent harness 评测、轨迹级根因归因、工具抽象实证、从诊断到有界恢复。
- **仍未解决：** 可信因果 ground truth、部分轨迹下归因、open-set 与多根因、在线检测校准、独立 recovery verification、跨环境复现和安全自演化。

## 关联入口

- [AgentOps 专题与精读清单](../agentops/README.md)
- [OpsAgent 专题与精读清单](../opsagent/README.md)
- [AgentOps vs OpsAgent](agentops-vs-opsagent.md)
- [Advanced Lesson 2](../lessons/lesson-02-advanced-agent-systems.md)
- [Agent、Planning、Memory、World Model Concepts](../../concepts/README.md)
