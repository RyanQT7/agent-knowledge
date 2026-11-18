# Lesson 2：Agent 的状态、决策、规划与多智能体协作

> 本课承接[第一课：LLM Agent 的工作过程](lesson-01-llm-agent.md)。第一课介绍了任务、工具、观察、循环和运行时；本课进一步理解 Agent 如何表示状态、选择行动、调整计划，多个 Agent 如何协作，以及怎样诊断它们自身的故障。

**贯穿案例：** 某个微服务的请求延迟突然上升。以下数值都是教学示例，不代表论文实验结果。

## 全局图

~~~text
Task + constraints → State → Decision / Planning → Action / Tool
                     ↑                              ↓
                     └──── Observation / State Update
                              ↓
                   Coordination / Verification
                              ↓
                Continue / Stop / Escalate / Recover
~~~

一次模型回答只是生成结果。Agent Runtime 还需要管理状态、权限、工具执行、观察回填、协作交接、验证和终止。多个 Agent 增加了多个决策主体和共享状态，也增加了新的失败路径。本课的分层是教学模型，不是行业统一标准。

关联概念：[Agent Loop](../../concepts/agent-loop.md)、[Agent Runtime](../../concepts/agent-runtime.md)、[Memory](../../concepts/memory.md)、[Planning](../../concepts/planning.md)、[World Model](../../concepts/world-model.md)、[Evidence Provenance](../../concepts/aiops/evidence-provenance.md)、[Verification](../../concepts/aiops/verification.md)。

---

# Part 1 — 从 Agent Loop 到真正的 Agent Runtime

## 1. 循环中的对象

| 对象 | 含义 | 延迟案例 |
| --- | --- | --- |
| Task | 目标与成功条件 | 找出延迟上升原因，并给出证据 |
| State | 任务和环境的当前可用表示 | 时间窗、已查结果、候选服务、待验证假设 |
| Observation | 工具或环境返回的观察 | P95、错误率、日志片段、拓扑关系 |
| Decision | 根据当前状态选择下一步 | 查连接池而不是再查 CPU |
| Action | 发出的动作请求 | 查询服务过去 30 分钟的连接等待 |
| Tool | Runtime 能执行的外部接口 | 指标、日志、拓扑查询 |
| State Update | 将动作结果写入任务状态 | 记录连接等待证据及来源 |
| Termination | 完成、超预算、升级或无法判断 | 根因证据足够，或交给工程师 |

模型可以提出 Action，但 Runtime 检查工具是否存在、参数是否符合 schema、调用是否获准、预算是否用完。工具成功返回不等于结论正确。

## 2. Agent 为什么不只是反复调用 LLM？

运行时还要解析模型输出是最终答复、工具调用、交接、暂停还是错误；校验参数与权限；执行工具；把结果关联到 Agent 和步骤；更新可恢复状态；限制重试、步数、成本和副作用；记录可审计事件；依据外部条件结束或升级。

~~~text
state = initialize(task, constraints)
while not terminal(state):
    context = build_model_view(state)
    proposal = model_decide(context)
    decision = parse(proposal)

    if decision is final:
        return verify_or_escalate(decision, state)

    if decision is handoff:
        state = record_handoff(state, decision)
        continue

    action = validate_schema_permission_budget(decision.action, state)
    if action is rejected:
        state = record_rejection(state, action)
        continue

    observation = execute_allowed_tool(action)
    state = update_state(state, action, observation)
    state = record_trace(state, action, observation)

return stop_with_reason(state)
~~~

框架可能把这些职责放在 Runner、图执行器或 Agent 对象中；它们不一定是独立服务。参见 [Agent Runtime Concept](../../concepts/agent-runtime.md) 与 [Agent Loop Concept](../../concepts/agent-loop.md)。

**关键结论：** Agent 的决策能力来自模型和运行时共同工作。循环不保证正确；状态、动作边界、反馈和停止条件决定错误会否被限制或放大。

---

# Part 2 — Agent 的 State

## 1. 六种经常混淆的状态

| 名称 | 回答的问题 | 例子 |
| --- | --- | --- |
| Context | 这一轮模型实际看到了什么？ | 当前问题、最近工具结果、压缩后的历史 |
| Memory | 哪些信息会被保留并在以后取用？ | 以前的事故案例、操作步骤 |
| Belief State | Agent 暂时相信世界是什么状态？依据和不确定性是什么？ | “连接池耗尽”有证据，但配置变化未查 |
| World State | 外部系统实际处于什么状态？ | 真实连接数、配置和部署版本 |
| Task State | 目标、约束、子目标和完成条件是什么？ | 只读调查、还需检查发布记录 |
| Execution State | Runtime 正在执行到哪一步？ | 工具等待、超时、重试次数、checkpoint |

Context 是本轮模型可见内容；Memory 是以后可取用的信息。Belief 是对世界的暂时判断，World State 才是外部实际状态。Task State 表示目标与未完成条件；Execution State 记录 Runtime 真实执行进度。模型说“已经查过”不是执行状态证据。

### 保存全部聊天记录为何不等于理解环境？

聊天历史可能包含过期指标、矛盾说法、未经工具证实的推测、被 Runtime 拒绝的动作，也可能没明确记录安全约束和未完成目标。因此长上下文不自动构成正确、最新且带来源的世界状态。

## 2. 论文中的状态设计

- [OpsMem](../../papers/opsagent/opsmem.md) 把当前事故诊断放在短期状态中，并用跨事件的长期经验辅助诊断；短期假设变化时重新激活相关经验。检索到旧案例不代表它是当前根因。
- [Graph of States（GoS）](../../papers/opsagent/graph-of-states.md) 用假设/状态图及证据支持和反驳进行溯因推理。图便于比较候选，但模型更新仍可能漏证或写入无依据节点。
- [PoS（Progression of States）](../../papers/opsagent/pos.md) 显式表示信念、待解决缺口和停滞，管理长程任务。其恢复机制给后续行动施加约束，不等于自动执行 IT 修复。

~~~text
Task:
  goal = "解释 checkout 延迟升高"
  constraints = ["只读", "时间窗=过去 30 分钟"]

Belief:
  hypothesis = "数据库连接等待"
  support = [evidence_12, evidence_17]
  counterevidence = []
  unresolved = ["连接池配置何时变化？"]

Execution:
  completed = ["查询 P95", "查询请求 trace"]
  pending = ["查发布记录"]
  rejected_actions = []
~~~

状态里的置信标签不能替代校准统计值；支持和反证应链接到带时间、实体、来源的证据。

**关键结论：** Context、Memory、Belief、World、Task 和 Execution State 回答不同问题。Agent 需要结构化、可更新且有来源的状态，而不只是聊天记录。

---

# Part 3 — Reasoning 与 Planning

## 1. 六个概念

- **Reasoning（推理）：** 用已有状态和证据得出判断，例如“CPU 正常让计算饱和假设变弱”。
- **Planning（规划）：** 选择面向目标的未来动作，例如“定位慢请求后检查连接池”。
- **Plan Execution（计划执行）：** Runtime 调用工具、接收结果并记录进度。
- **Replanning（重规划）：** 新 Observation 让原计划不合适时，改选后续动作。
- **Search（搜索）：** 比较多个潜在行动或状态路径。
- **Verification（验证）：** 按判据检查观察、假设、动作或恢复结果是否成立。

写计划不等于执行计划；执行计划不等于系统恢复；模型自评不等于独立验证。

## 2. 常见控制形态

| 形态 | 行为特点 | 适用场景 | 风险 |
| --- | --- | --- | --- |
| Reactive Agent | 每轮根据当前 Observation 选一步 | 下一步依赖实时结果 | 短视、重复查询 |
| Plan-first Agent | 先列多步计划，再执行 | 步骤稳定 | 早期误判会污染后续步骤 |
| Planner–Executor | Planner 生成计划，Executor 调工具落实 | 语言计划需受限执行 | 计划可能不可执行或不能适应变化 |
| State-aware Agent | 显式读写任务、信念、执行状态 | 长任务、协作、需审计场景 | 状态可能过时或写错 |

[ReAct](../../papers/react/notes.md) 展示推理与行动交错；[LLM+P](../../papers/llm-p/notes.md) 将问题转换为形式化规划；[RAP](../../papers/rap/notes.md) 用 world model 与 MCTS 比较模拟路径；[ReWOO](../../papers/rewoo/notes.md) 解耦 Planner、Worker 和 Solver。出现 Planner 这个模块名，不足以证明系统有 Observation 驱动的重规划。

## 3. 为什么固定 Workflow 有时更可靠？

固定流程能保证必做的安全检查、约束工具范围、保留分支记录，并容易测试和回退。动态 Planning 则适合新证据改变调查方向或 SOP 覆盖不了的故障。

一种混合方式是：确定性流程规定安全边界和必经步骤；Agent 只在允许的分支中选择下一查询；证据不足、候选冲突或超出权限时停止并升级。

**关键结论：** 规划越自由不代表越好。控制方式应由风险、未知程度、反馈质量和可验证性决定。

---

# Part 4 — 从 Single Agent 到 Multi-Agent

多 Agent 增加任务拆分、角色分配、委派、通信、共享状态、协调、冲突解决、终止控制和复核。它可能带来互补信息、并行效率、专门工具或独立复核；若只是用不同提示重复同一推理，可能只增加成本、延迟和一致性错觉。

| 架构 | 组织方式 | 主要风险 |
| --- | --- | --- |
| Centralized Coordinator | 一个协调者拆分、分派、汇总并决定停止 | 协调者错误影响全部分支，或成为瓶颈 |
| Planner–Worker–Reviewer | Planner 计划，Worker 执行，Reviewer 检查 | Reviewer 可能共享原错误，重复执行开销高 |
| Decentralized Collaboration | Agent 直接交换发现、协商或竞争假设 | 冲突和共享上下文难追踪，容易循环 |
| Hierarchical Multi-Agent | 上层拆目标，下层按服务/领域继续拆 | 错误跨层传播，层级越深越难归因 |

这些是架构选项，不表示每个角色必须是独立模型或进程。

**关键结论：** 是否采用 Multi-Agent，要看分工产生了什么互补证据、并行收益和独立检查，以及这些收益能否抵过协调开销。

---

# Part 5 — Multi-Agent 的真实运行过程：微服务延迟上升

假设 checkout 请求 P95 从约 200 ms 升到 1.2 s，CPU 未明显升高，部分请求等待数据库连接。以上数值仅作示例。

## Single Agent

~~~text
接收事件和只读边界
→ 查询 P95、错误率、资源使用
→ 观察到数据库连接等待
→ 查询慢请求 trace 与连接池指标
→ 查最近部署/配置变化
→ 建立根因假设并记录缺少的证据
→ 用新观察核对假设
→ 结束、继续调查或升级给人
~~~

优点是上下文简单、协调成本低；风险是同一决策者既选查询又解释结果还评价自己，单点错误可能贯穿全程。

## Multi-Agent 分工

- **Coordinator 接收：** 事件 ID、影响服务、时间窗、告警摘要、权限边界、预算和完成条件。它把“告警”当调查入口，不把它当根因结论。
- **Metric Agent 查询：** P95、错误率、CPU、连接池使用和等待时序；返回参数、实体、时间窗、结果及来源。
- **Log Agent 查询：** checkout 与数据库连接相关错误、超时和重试；返回过滤条件、时间、服务及采样限制。
- **Topology Agent 查询：** checkout → order → database 依赖、最近部署和配置关系；返回版本及有效时间。
- **RCA Agent 比较：** 连接池耗尽、SQL 变慢、上游调用变慢等候选；列出支持、反证和缺失证据。
- **Verifier 检查：** 重新查询关键指标/trace，核对实体、时间窗和因果顺序；返回独立工具、判据、结果和不确定性。

Coordinator 接收结构化结果与出处，而不只是“我觉得 DB 是根因”。结果冲突时，补充调查、保留冲突或升级给人。

~~~text
Incident + scope + read-only policy
                 ↓
            Coordinator
        ┌────────┼──────────┐
        ↓        ↓          ↓
   Metric Agent Log Agent Topology Agent
        └────────┼──────────┘
                 ↓ 带时间、实体、来源的 Observation
              RCA Agent
                 ↓ 候选 + 支持/反证 + 未解问题
              Verifier
                 ↓ fresh query / topology & time check
        ┌────────┴──────────┐
        ↓                   ↓
通过且满足条件           冲突/证据不足
        ↓                   ↓
总结、停止             再调查或升级给人
~~~

停止条件不应只是“已经写出答案”。可以要求影响范围确定、关键证据可重查、首选假设经独立检查、关键反证已处理；否则说明缺口并升级。

**关键结论：** 多 Agent 带来分工和协作边界，不会自动带来正确性；证据和验证结果都要可追溯。

---

# Part 6 — Multi-Agent 为什么会失败？

~~~text
Coordinator 误解任务
→ 错误委派
→ 错实体/时间窗工具调用
→ 错误 Observation 写入共享状态
→ RCA Agent 把症状当根因
→ Reviewer 复述同一错误
→ 过早结束并给出错误结论
~~~

| 失败 | 表现 | 传播原因 |
| --- | --- | --- |
| 任务理解错误 | 忽略时间范围、权限或完成条件 | Coordinator 的错误影响所有分支 |
| 错误委派 | 让日志角色回答只有拓扑查询才能回答的问题 | 子任务拆分造成证据空白 |
| 错误工具调用 | 参数指向错误服务或时间窗 | 下游把返回值当真 |
| 错误结果传播 | 摘要丢掉实体/时间，或把推测写成事实 | 下游看不到原始来源 |
| Context Drift | 共享假设偏离原目标 | handoff 改变约束或含义 |
| Premature Termination | 首选假设出现就停止查反证 | 替代假设没机会验证 |
| Hallucinated Verification | Reviewer 只读摘要就通过 | 角色不同但信息不独立 |
| Repeated Actions | 多角色查同一数据或循环重试 | 协调成本、延迟和副作用增加 |

[AgentRx](../../papers/agentops/agentrx.md) 规范化轨迹并用约束 checker 生成证据，辅助定位首个不可恢复错误步骤；它诊断失败，不负责修复。[TraJudger](../../papers/agentops/trajudger.md) 根据任务、角色、工具和交互依赖构图，再沿传播关系回溯；末尾输出错误的 Agent 不一定是根因。[PROBE](../../papers/agentops/probe.md) 用证据诊断后提供有界的下一次尝试指导；其 retry 实验不证明长期生产恢复安全。

**关键结论：** 多 Agent 增加了错误传播路径。评估应记录任务拆分、Agent 身份、工具、输入输出、状态更新、委派依赖和验证证据。

---

# Part 7 — AgentOps 为什么出现？

传统日志、指标和分布式 Trace 对基础设施重要，但通常不回答：哪个 Agent 选了工具？它用了什么参数、收到了什么？是否把猜测写入共享状态？错误在哪一步首次出现？哪些依赖传播了错误？验证查了什么？Runtime 是否压缩了上下文或漏掉交接？

AgentOps 增加的观察对象可包括：

~~~text
Agent Identity
+ Trajectory（逐步轨迹）
+ Action / Observation Dependency
+ Failure Step 与 Responsible Agent
+ Verification Evidence
+ Recovery Result
~~~

轨迹可能记录 identity、时间、输入输出、tool call/result、observation、state update、delegation、dependencies 和 verification。实际系统不一定完整具备这些字段；敏感上下文还需要隐私保护和访问控制。

要区分三件事：

1. **Detection：** 发现执行可能有异常；
2. **Attribution / Diagnosis：** 解释错误发生在哪里、如何传播；
3. **Recovery：** 采取措施后，用独立观察确认系统回到目标状态。

建议不等于已执行，诊断不等于恢复。

**关键结论：** 轨迹让语义决策与错误传播可关联、解释和检查。AgentOps 不是简单多存日志。

---

# Part 8 — OpsAgent 如何用于 AIOps？

~~~text
Traditional AIOps
       ↓
LLM-assisted AIOps
       ↓
Tool-augmented AIOps
       ↓
Agentic AIOps
       ↓
Multi-Agent AIOps
~~~

| 阶段 | 增加的能力 | 仍缺什么 |
| --- | --- | --- |
| Traditional AIOps | 规则/统计告警、拓扑或因果 RCA、工单路由 | 灵活自然语言和开放式调查可能有限 |
| LLM-assisted AIOps | 读日志/工单、摘要和解释模型结果 | 一次调用通常无实时闭环，不能验证摘要 |
| Tool-augmented AIOps | 查询监控、日志、拓扑、知识库 | 有工具不等于有状态、重规划或结果正确 |
| Agentic AIOps | 持续调查并根据 Observation 调整下一步 | 需要权限、验证、预算和人工升级 |
| Multi-Agent AIOps | 按模态/服务/职责并行汇总 | 需治理共同偏差、冲突、重复查询和传播 |

这是教学模型，不代表所有系统都按此路线发展。固定 SOP 若能覆盖任务，可能比动态 Agent 更可靠；多 Agent 要由证据证明分工有收益。

关联：[Agentic Incident Management](../../concepts/aiops/agentic-incident-management.md)、[AIOps Review v3](../../notes/aiops/reviews/aiops-knowledge-review-v3.md)、[Network AIOps Architecture Synthesis](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md)。

**关键结论：** Agentic 程度取决于系统能否基于观察调整行动，不取决于是否使用了 LLM、RAG、工具或多个角色。

---

# Part 9 — 为什么需要 Verification？

## 为什么自我检查不足以证明 RCA 正确？

模型自检仍使用同一模型和输入，可能共享错误假设、看不到时间/实体/采样限制、把流畅解释当证据，或把工具请求成功误认为系统恢复。Reviewer 如果只看 Worker 摘要，也可能继承共同错误。独立性在于数据源、判据或检查方法是否真正独立，而不在角色名字。

## 哪些检查可由确定性程序完成？

- schema、必填字段、参数类型、时间窗、实体 ID；
- 步数、权限、速率、重复动作、预算；
- 证据来源、时间戳、新鲜度、查询是否成功；
- 已知拓扑约束、配置版本、候选成员关系；
- 操作前置条件、审批记录、执行结果码；
- 阈值、服务健康状态和恢复观察窗口。

它们只能检查定义范围内的属性，不会自动发现所有新因果关系。

## 哪些需要新观察或人工判断？

- 根因是否解释了多源证据的变化；
- 新证据是否支持或反驳候选因果链；
- 是否有未观测依赖、未知故障或多根因；
- 高风险变更是否符合现场背景、业务窗口和流程。

~~~text
证据有效性
→ 候选/图一致性
→ RCA 结论
→ 动作安全性
→ 动作执行结果
→ 服务恢复状态
~~~

每一级都要有判据。修复前的安全检查不能代替修复后的恢复确认；恢复需用独立健康信号和观察窗口确认，必要时回滚或升级。

**关键结论：** Verification 是带有对象、判据、来源和失败处置的检查，不是“再问一次 LLM”。风险越高，证据越应独立且贴近环境。

---

# Part 10 — 更深入的框架理解：一个工程分层模型

下图是教学模型，不是普遍标准，也不要求每层由不同服务实现。

~~~text
┌────────────────────────────────────────────┐
│ Governance：权限、审批、审计、预算、回滚 │
├────────────────────────────────────────────┤
│ Verification：证据、候选、动作、恢复检查 │
├────────────────────────────────────────────┤
│ Observability：轨迹、事件、状态、依赖记录 │
├────────────────────────────────────────────┤
│ Execution：循环、调度、重试、checkpoint   │
├────────────────────────────────────────────┤
│ Tool：查询/执行接口、schema、参数、结果    │
├────────────────────────────────────────────┤
│ Planning / Orchestration：规划与协作       │
├────────────────────────────────────────────┤
│ State / Memory：上下文、belief、任务、经验 │
├────────────────────────────────────────────┤
│ Model：理解、候选、推理与动作提议          │
└────────────────────────────────────────────┘
                  ↕ 外部系统与人
~~~

- **Model Layer：** 理解、分类、摘要、候选生成或动作提议。
- **State / Memory Layer：** 保存当前任务、Belief、执行进度及可检索的跨任务经验，附来源、时间和版本。
- **Planning / Orchestration Layer：** 选工具、拆任务、处理 handoff、合并结果和重规划。
- **Tool Layer：** 提供受约束的观察/操作接口，声明输入、输出、权限和副作用。
- **Execution Layer：** 调用模型和工具，管理状态转移、错误处理、预算和 checkpoint。
- **Observability Layer：** 记录决策输入、动作、Observation、状态变化、依赖边和版本。
- **Verification Layer：** 分别检查证据、候选、结论、变更和恢复。
- **Governance Layer：** 最小权限、审批、人类升级、审计、风险策略和回滚。

读论文或代码时逐项追问：这层是否真的存在？由谁实现？是模型提议还是程序强制？实验覆盖了吗？

**关键结论：** 分层便于定位可靠性缺口，但层数多不代表系统安全；要看边界和数据流能否验证。

---

# Part 11 — 论文与代码对应：从设计看到实现

以下仓库经论文或作者项目页面确认，仅做静态源代码阅读；代码存放在忽略目录，没有安装依赖、运行脚本或执行实际运维操作。

## 1. AgentRx：轨迹规范化与约束证据

- **论文设计：** 将不同 Agent 日志转成 Trajectory IR；静态/动态约束 checker 生成证据；Judge 定位首个不可恢复步骤和错误类型。
- **官方源码：** [microsoft/agentrx](https://github.com/microsoft/agentrx)，固定 SHA、许可见 [AgentRx 笔记](../../papers/agentops/agentrx.md)。
- **核心实现：** agentrx/cli.py 是入口；agentrx/ir/trajectory_ir.py 定义轨迹；agentrx/invariants/checker.py 与 invariants 目录检查约束；agentrx/judge/judge.py 做诊断。
- **执行链：** 原始 trace → 统一 IR → 约束检查 → Evidence Log → Judge → 诊断记录。
- **边界：** 诊断不自动修复，且依赖输入轨迹完整性。

## 2. NKU OpsAgent：微服务事件的多 Agent 流程

- **论文设计：** 预处理 Metrics/Logs/Traces，执行 anomaly detection、fault tracing、root-cause localization；结论经过交叉评阅，人类反馈用于离线演化。
- **官方源码：** [Johnn13/OpsAgent](https://github.com/Johnn13/OpsAgent)，SHA 和许可见 [OpsAgent 系统笔记](../../papers/opsagent/opsagent-system.md)。
- **核心实现：** utils/data_processer.py 预处理多模态信号；Agent/task 模块串接 AD、FT、RCL 和评审流程。交叉评阅不是完全独立的外部 verifier。
- **执行链：** evidence preprocess → anomaly/fault agents → RCA/localization → cross-review / 人类反馈 → 离线更新。
- **边界：** 论文报告生产使用与人类执行缓解，不应写成 Agent 自动安全修复。静态阅读发现 trace helper 的默认分位数与论文描述不一致，复现时应核对。

## 3. OpsMem：短期状态与长期经验

- **论文设计：** STM 保存当前事故诊断状态，LTM 保存跨事件模式、案例和流程；短期状态更新后刷新相关经验。
- **官方源码：** [gaorch85/OpsMem](https://github.com/gaorch85/OpsMem)，SHA、Apache-2.0 和模块见 [OpsMem 笔记](../../papers/opsagent/opsmem.md)。
- **核心实现：** code/main.py、pipeline.py 组织流程；stm/graph.py、short_term_memory.py、fsm.py 管当前状态；cmr/cross_memory_resonance.py 联结记忆；agents/ 承载角色；consolidation/consolidator.py 管经验整理。
- **执行链：** 诊断图变化 → 刷新长期记忆关联 → 专家角色产出判断 → 更新短期状态 → 反馈门控的经验整理。
- **边界：** 公开运维数据和长期记忆规模有限；记忆共振不保证迁移正确。

## 4. Graph of States：状态图溯因

- **论文设计：** 用图表示假设/状态扩展和回溯，依据证据支持与反驳推进诊断。
- **官方源码：** [gaorch85/Graph-of-States](https://github.com/gaorch85/Graph-of-States)，SHA 和 MIT 许可见 [GoS 笔记](../../papers/opsagent/graph-of-states.md)。
- **核心实现：** main.py 组织推理；belief/graph.py、belief/fsm.py 管图与状态转移；central/expert agents 扩展候选；Run/FailureDiagnosis_IT.py 提供 IT 诊断。
- **执行链：** 假设/证据 → 展开可能原因 → 调证据工具 → 更新支持/反证 → 扩图或回溯。
- **边界：** 这是诊断系统，不是生产修复执行器；候选图依赖输入证据和状态更新。

完整论文—仓库身份、SHA、许可和覆盖见 [Paper–Code Repository Index](../../code/repository-index.md) 及论文笔记。源码随时间变化，本课引用本轮记录的 commit。

**关键结论：** 应把论文图中的机制和代码入口、状态对象、执行路径逐项对应。文件名不证明论文所称机制已完整实现。

---

# Part 12 — 学习检查

先自行作答，再看下方答案。

## 五个理解题

1. Context、Memory、Belief State、World State、Task State、Execution State 分别回答什么问题？为什么聊天记录不能取代它们？
2. Reasoning、Planning、Plan Execution、Replanning、Verification 有什么区别？用延迟案例举例。
3. Multi-Agent 比 Single Agent 增加哪些能力与故障面？怎样证明协作有价值？
4. 为什么最终输出错误的 Agent 不一定是根因 Agent？轨迹需要记录什么才能分析传播链？
5. 哪些 RCA 检查能由确定性程序完成？为什么模型自检不能证明服务已恢复？

## 两个小型架构设计题

1. 设计一个只读诊断 Agent，可查 Metrics、Logs、Traces 和拓扑但不得修改服务。画出状态字段、工具、候选管理、停止条件、验证和人工升级路径；说明哪些决策由模型提出、哪些由 Runtime 强制。
2. 为六个微服务设计最小 Multi-Agent 方案。说明是否需要拆分；若需要，如何分工、共享状态、处理冲突和避免重复查询；怎样与 Single Agent 基线比较成本和准确度。

## 一个 Multi-Agent 失败分析题

Coordinator 把“过去 30 分钟 checkout 延迟升高”错委派成“查 payment 最近 24 小时 CPU”。Metric Agent 返回“CPU 正常”；Coordinator 将其记作 checkout 证据。RCA Agent 据此排除数据库，Reviewer 没有重新查询环境就通过。请指出：

- 最早错误步骤；
- 错误如何传播；
- 根因、贡献因素和终端症状；
- 至少三条应记录到 Trajectory 的信息；
- 不依赖同一模型自评的验证方案；
- 是否可以宣称恢复成功。

---

## 参考答案

### 理解题

1. Context 是模型当前可见输入；Memory 是可跨回合取用的信息；Belief 是对外部世界的暂时判断；World State 是环境实际状态；Task State 是目标/约束/未完成子目标；Execution State 是 Runtime 的运行和工具状态。聊天记录可能过期、矛盾、缺来源或遗漏执行事件。
2. Reasoning 是推断；Planning 选目标导向的动作；执行由 Runtime 落实；Replanning 根据新观察改变剩余计划；Verification 按判据检查主张或结果。例如由连接等待推断数据库池可能耗尽是推理；安排查连接池是计划；调用查询是执行；发现配置未变后转查请求依赖是重规划；新 trace 核对等待位置是验证。
3. 增加任务拆分、并行、专业角色/工具和复核；也增加错误委派、共享状态污染、冲突、重复查询、提前终止和传播。通过 Single Agent 对照、消融、成本/延迟、互补证据、失败定位和恢复指标评估净收益。
4. 最终 Agent 可能只是消费上游错误 Observation。需要记录 Agent/任务 ID、时间、输入输出、工具及参数、原始结果、状态写入、委派依赖、验证判据和环境结果。
5. schema、时间窗、实体、权限、阈值、已知拓扑和工具执行结果可由确定性程序检查。自检可能共享同一错误；恢复还需修复后重新查询独立健康信号，单纯说“已恢复”不足为证。

### 架构设计题参考思路

1. 由 Runtime 强制只读权限；分开保存 Task、候选、Evidence Provenance、工具调用和执行进度；模型可从允许清单选择查询，但不能扩大权限；证据附实体、时间、来源和新鲜度；冲突、超预算、证据不足时 abstain/escalate；Verifier 重新查询关键数据并校验时间和实体。
2. 先建立单 Agent 基线。仅当日志/指标/拓扑任务能并行且信息互补时，拆 Metric、Log、Topology 角色并设 Coordinator；共享带来源的 Evidence Ticket，不只传自由文本；用唯一查询键去重；RCA 和 Verifier 尽量使用独立数据。用相同事件、工具和预算比较准确度、证据质量、延迟、成本和人工时间。

### 失败分析题

最早错误是 Coordinator 将目标实体和时间窗改成 payment/24 小时。Metric Agent 的结果对错误查询可能是局部正确；Coordinator 把它错映射为 checkout 证据；RCA 据此排除数据库；Reviewer 未独立检查，形成验证失效；错误结论是终端症状。应记录原始范围、委派任务、工具参数、返回实体和时间、证据映射者、RCA 依据及 Reviewer 的查询来源。Runtime 可校验实体/时间窗，Verifier 用正确 checkout 范围重新查指标和 trace，并核对拓扑/时间。没有执行修复和修复后观测，不能宣称恢复成功。

---

## 知识库连接

- **基础概念：** [Agent](../../concepts/agent.md)、[Agent Loop](../../concepts/agent-loop.md)、[Agent Runtime](../../concepts/agent-runtime.md)、[Reasoning](../../concepts/reasoning.md)、[Planning](../../concepts/planning.md)、[Memory](../../concepts/memory.md)、[World Model](../../concepts/world-model.md)、[Tool Use](../../concepts/tool-use.md)、[Reflection](../../concepts/reflection.md)。
- **AgentOps：** [AgentOps Review v1](../../notes/agentops/reviews/agentops-review-v1.md)、[AgentRx](../../papers/agentops/agentrx.md)、[TraJudger](../../papers/agentops/trajudger.md)、[PROBE](../../papers/agentops/probe.md)、[Trial by Trace](../../papers/agentops/trial-by-trace.md)。
- **OpsAgent：** [OpsAgent Review v1](../../notes/opsagent/reviews/opsagent-review-v1.md)、[OpsMem](../../papers/opsagent/opsmem.md)、[Graph of States](../../papers/opsagent/graph-of-states.md)、[PoS](../../papers/opsagent/pos.md)、[KRCA](../../papers/opsagent/krca.md)。
- **AIOps：** [Candidate Space](../../concepts/aiops/candidate-space.md)、[Evidence Provenance](../../concepts/aiops/evidence-provenance.md)、[Verification](../../concepts/aiops/verification.md)、[Network AIOps Architecture Synthesis](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md)。
- **跨主题：** [AgentOps vs OpsAgent](../../notes/guides/agentops-vs-opsagent.md)、[Agent Research Directions 2026](../../notes/guides/agent-research-directions-2026.md)、[ReAct](../../papers/react/notes.md)、[Toolformer](../../papers/toolformer/notes.md)、[Reflexion](../../papers/reflexion/notes.md)、[ReWOO](../../papers/rewoo/notes.md)、[LLM+P](../../papers/llm-p/notes.md)、[RAP](../../papers/rap/notes.md)。

**学完后应能解释：** 一个 Agent 如何把状态转成决策，多个 Agent 怎样传递任务和证据，以及如何通过轨迹、候选、独立验证和外部状态检查诊断自身故障。
