# Agent / LLM / Skill / AIOps 学习 Guide

这是一份面向当前阶段的入口文档。目标是先建立整体地图，再逐步进入
Reasoning、Planning、Tool Use、Memory、Verification 和 Network AIOps RCA。
它使用当前知识库已经完成的论文笔记、代码静态阅读和阶段性 Review；不会把
未运行的代码、未找到源码的论文或当前研究假设写成已经证明的事实。

## 如何阅读这份 Guide

文中尽量区分四种内容：

- **Paper-backed**：可以在论文笔记中追溯的论文事实。
- **Code-backed**：在固定 repository commit 的源码静态阅读中看到的实现事实。
- **Cross-paper synthesis**：把多个来源放在一起后形成的当前阶段理解。
- **Research hypothesis / engineering understanding**：面向 Network AIOps 的设计假设或本知识库自身的工程经验，仍需实验验证。

相关入口：[论文—仓库索引](../../code/repository-index.md)、[代码阅读总结](../code/paper-code-discovery-summary.md)、[Network AIOps 架构综合](../aiops/reviews/network-aiops-architecture-synthesis-v1.md)。

# Part 1 — 一张图理解 LLM Agent

## 1. 先看整体直觉

**LLM（Large Language Model，大语言模型）** 是根据输入生成文字或结构化
输出的模型。它本身可以回答问题，但它不会因为“会生成文字”就自动拥有环境、
工具、目标状态或长期记忆。

**Agent（智能体）** 是围绕一个目标持续做决定、执行动作、读取外界结果并
决定下一步的系统。它通常包含一个 LLM，但 Agent 不等于 LLM 本身。

一个最小的 working mental model 是：

```text
用户任务
   ↓
LLM 理解当前情况并形成推理
   ↓
决定下一步
   ↓
调用 Tool 或执行 Action
   ↓
获得 Observation
   ↓
更新当前 Context / State
   ↓
继续、调整、验证或结束
   ↓
结果
```

这里的 **Tool（工具）** 是 Agent 可以调用的外部能力，例如搜索、查询
指标、读取日志、执行代码或访问数据库。

**Observation（观察结果）** 是动作完成后从外界得到的结果，例如搜索结果、
命令输出、指标变化或执行失败信息。

**Environment（环境）** 是 Agent 所处并可被观察或影响的外部对象，例如
Wikipedia、代码测试环境、Kubernetes 快照或网络运维系统。

这张图是跨论文综合后的工作模型，不是某篇论文规定的统一标准。它最重要的
含义是：Agent 的关键不在于“用了一个很大的模型”，而在于是否存在目标驱动
的状态—行动—反馈循环。

## 2. 一个简单例子：规划三天旅行

任务是：“帮我规划一次三天旅行。”

一个普通 LLM 可能直接生成一份看起来合理的行程。一个 Agent 可能经历：

```text
理解：目的地、日期、预算和兴趣是什么？
  ↓
Planning：先安排交通、住宿，再安排每天的活动
  ↓
Tool：查询天气、交通和开放时间
  ↓
Observation：发现第二天景点闭馆，或火车时间冲突
  ↓
Reasoning：调整安排并解释为什么调整
  ↓
Verification：检查日期、时间和预算是否一致
  ↓
最终行程
```

如果用户后来反馈“我不喜欢长途步行”，系统还可以产生一次 **Reflection
（反思）**：总结之前方案的问题，并改变下一版行程。Reflection 在这里是
针对已有尝试和反馈的复盘，不是普通的每一步推理。

## 3. Agent 从接到任务到完成任务，究竟发生了什么？

可以按六个问题理解：

1. **任务是什么？** 把自然语言目标变成当前需要完成的结果。
2. **现在知道什么？** 读取当前 context、历史轨迹和已有证据。
3. **下一步做什么？** 可能只是思考，也可能选择工具或行动。
4. **行动后发生了什么？** 读取 observation，不能把猜测当成事实。
5. **是否需要调整或验证？** 新结果可能推翻原来的假设。
6. **什么时候结束？** 结果满足条件，或需要交给人处理。

在 ReAct 里，前四步以很直接的 Thought → Action → Observation 形式出现；
在 StepFly 里，较大的步骤结构来自 PlanDAG，LLM 负责步骤内的动作；在
Cloud-OpsBench 里，每次 action、参数、observation 和 step budget 都能被
记录和评估。[ReAct 代码笔记](../../code/react/notes.md)、[StepFly 代码笔记](../../code/aiops/stepfly/notes.md)、[Cloud-OpsBench 代码笔记](../../code/aiops/cloud-opsbench/notes.md)
分别展示了这三种落地方式。

# Part 2 — 最核心术语

下面每个术语第一次出现都先给出简单中文解释。术语之间的边界是当前知识库
的 working distinction，后续论文可能继续修正。

## LLM

**是什么？** 根据上下文生成下一个 token（文本片段）的模型。

**为什么需要？** 它擅长语言理解、非结构化文本处理、假设生成和自然语言
交互。

**流程中哪里出现？** 可以负责理解任务、生成推理、选择动作、总结证据或写
解释。

**容易混淆的概念：** LLM 是模型，不是完整 Agent；模型没有自动获得工具、
环境、验证器或持久 Memory。

## Agent

**是什么？** 围绕目标持续接收状态或反馈、选择动作并推进任务的系统。

**为什么需要？** 任务需要多步调查、动态工具选择、状态维护或中间验证时，
一次性生成文本通常不够。

**流程中哪里出现？** 它包住整个循环：任务、决策、行动、观察、调整和结束。

**容易混淆的概念：** 调用一次 API 或生成一次 JSON 不足以证明是 Agent；要
看是否有目标、状态、行动和后续反馈。

## Agentic Workflow

**是什么？** 把模型、工具、规则和检查器按步骤编排起来的工作流。

**为什么需要？** 它可以让复杂任务有明确的阶段、边界和审计记录。

**流程中哪里出现？** 可以包围多个 LLM 调用，也可以在固定流程的某一步放
一个 Agent loop。

**容易混淆的概念：** 固定工作流不一定具备真正的动态自主性。StepFly 的
PlanDAG 加 Executor 是受约束的 agentic workflow；AIM 的生成和评估路径
更接近 LLM-assisted workflow。[StepFly 代码笔记](../../code/aiops/stepfly/notes.md)、[AIM 代码笔记](../../code/aiops/aim/notes.md)

## Tool

**是什么？** Agent 可以调用的外部能力，例如查询指标、搜索日志、访问拓扑、
执行测试或修改配置。

**为什么需要？** LLM 的上下文里没有实时系统状态；Tool 提供新的证据或执行
能力。

**流程中哪里出现？** 通常在“决定下一步”之后执行，结果再以 Observation
返回。

**容易混淆的概念：** Tool 是能力接口，不是 Agent；Tool 返回结果也不等于
verification，更不等于 remediation 成功。

## Skill

**是什么？** 一套可重复执行的 workflow instructions、约束、输入输出约定
和质量检查。

**为什么需要？** 它把一次成功的工作方法固化下来，使之后的任务有稳定规范。

**流程中哪里出现？** Skill 可以规定如何定位资料、调用哪些步骤、检查哪些
质量项，但实际执行仍需要 Agent/运行器/人。

**容易混淆的概念：** Skill 不是 Tool，不是 Prompt，也不是模型能力本身，
更不是 Agent 本身。当前知识库中的 [paper-reading](../../skills/paper-reading/SKILL.md)、[knowledge-review](../../skills/knowledge-review/SKILL.md)、[learning-batch](../../skills/learning-batch/SKILL.md)、[knowledge-query](../../skills/knowledge-query/SKILL.md)、[aiops-paper-reading](../../skills/aiops-paper-reading/SKILL.md)、[aiops-learning-batch](../../skills/aiops-learning-batch/SKILL.md)、[paper-code-discovery](../../skills/paper-code-discovery/SKILL.md) 和 [code-reading](../../skills/code-reading/SKILL.md) 是这个工程含义的实例。

## MCP

**是什么？** 一种把模型应用与外部工具、资源或提示连接起来的标准化协议。

**为什么需要？** 它可以统一外部能力的描述和调用边界，减少每个应用都为每
个服务定制连接代码。

**流程中哪里出现？** MCP 位于 Agent/应用与具体 Tool 或 resource 之间；例
如当前 Codex 可以通过 GitHub MCP 访问 repository 能力。

**容易混淆的概念：** MCP 不是 Agent、Skill、Knowledge Base 或 Memory；它
更像外部能力的连接方式。当前 [MCP Concept](../../concepts/mcp.md) 仍是
evolving，具体协议能力应以实际连接器文档为准。

关系可以先记成：

```text
Agent / 应用
    ↓ 使用
Skill：规定可重复流程
    ↓ 选择或描述
Tool：提供具体外部能力
    ↓ 可能通过
MCP：标准化连接方式
    ↓ 访问
外部服务 / 数据 / 资源
```

## Prompt

**是什么？** 给模型的任务说明、上下文、格式和行为约束。

**为什么需要？** 它告诉模型当前目标、可用信息和输出边界。

**流程中哪里出现？** 几乎每次 LLM 调用前都会构造 prompt。

**容易混淆的概念：** Prompt 是一次调用的输入；Skill 可以包含 prompt 模板，
但 Skill 还包括流程、检查和失败处理。

## Context

**是什么？** 当前一次模型调用能够看到的信息。

**为什么需要？** 模型只能根据提供给它的上下文决策；没有当前证据就只能猜。

**流程中哪里出现？** 在每次 reasoning、tool selection 或 final answer 前构造。

**容易混淆的概念：** Context 是“这次看到了什么”，Memory 是“以后要保存并
重新利用什么”；两者可能重叠，但不等价。

## Memory

**是什么？** 保存并在之后重新利用信息的机制。

**为什么需要？** 长任务、跨尝试或跨会话不能把所有历史都依赖当前窗口。

**流程中哪里出现？** 可能在尝试结束时写入，在下一次任务/attempt 开始或中
间 retrieval。

**容易混淆的概念：** trajectory history、模型内部状态、RAG 文档库和完整
persistent memory architecture 不是一回事。Reflexion 的文本 reflection、
StaR 的 temporal state、StepFly 的 session database 属于不同实现。[Memory Concept](../../concepts/memory.md)

## RAG

**是什么？** Retrieval-Augmented Generation，即先从外部资料检索相关内容，
再把内容放进模型上下文生成回答。

**为什么需要？** 让模型使用较新的、领域相关的资料，而不是只依赖参数中的
知识。

**流程中哪里出现？** 通常发生在生成前：query → retrieval → context → LLM。

**容易混淆的概念：** RAG 是知识检索增强，不等于 Agent memory；vector database
只是可能的存储/检索组件，不等于 memory architecture。[RAG Concept](../../concepts/rag.md)

## Reasoning

**是什么？** 针对当前问题解释信息、比较假设并决定下一步的推理过程。

**为什么需要？** 复杂任务不能只靠固定映射，需要把当前证据连接到动作或结论。

**流程中哪里出现？** 可以发生在每次 action 前，也可以发生在最终归纳前。

**容易混淆的概念：** 生成的 Thought/reasoning trace 是显式语言轨迹，不等于
模型真实隐藏 internal state。[Reasoning Concept](../../concepts/reasoning.md)

## Planning

**是什么？** 提前组织未来若干步骤、子目标或行动顺序。

**为什么需要？** 当任务有多个依赖步骤时，计划可以减少盲目尝试。

**流程中哪里出现？** 可能在执行前一次生成，也可能在执行中不断修订。

**容易混淆的概念：** reasoning about the next step 不一定是 explicit planning；
planning 也不一定使用 search。LLM+P、RAP、ReWOO 和 StepFly 展示了不同层次
的 planner、formal planner、search 或固定 DAG。[Planning Concept](../../concepts/planning.md)

## Reflection

**是什么？** 基于已有 trajectory、结果或失败反馈，对过去尝试做语言化复盘。

**为什么需要？** 复盘可以把失败转换成下一次尝试可使用的经验。

**流程中哪里出现？** 通常在一次 attempt 结束后、下一次 attempt 开始前。

**容易混淆的概念：** Reflection 不等于当前 step 的 reasoning，也不等于参数
更新或 evaluator 本身。Reflexion 的代码把 reflection 文本放入下一次 context，
运行循环没有因此变成 gradient-based training。[Reflexion 代码笔记](../../code/reflexion/notes.md)

## Observation

**是什么？** Action 后从环境或工具获得的实际结果。

**为什么需要？** 它把推理从纯猜测拉回到外部事实。

**流程中哪里出现？** 每次 tool/action 后，作为下一次决策输入。

**容易混淆的概念：** Observation 是结果，不是模型的 Thought；Observation 也
不自动说明结果正确，需要 provenance 或 verification。

## Verification

**是什么？** 用独立或可检查的依据判断 evidence、假设、诊断、修复或恢复是否
成立。

**为什么需要？** LLM 能生成看似合理的内容，也可能错误调用 Tool 或重复确认
自己的错误。

**流程中哪里出现？** 可以在诊断后、执行修复前和执行修复后分别出现。

**容易混淆的概念：** LLM self-check 只是较弱的检查；fresh telemetry、规则、
受控执行结果和 recovery observation 通常提供更强证据。[AIOps Verification Concept](../../concepts/aiops/verification.md)

## Human-in-the-loop

**是什么？** 在关键步骤由人查看、批准、纠正或接管系统。

**为什么需要？** 高影响操作、证据冲突和 open-set 故障不能默认交给不受约束
的模型。

**流程中哪里出现？** 可以在 incident 确认、诊断复核、remediation approval、
rollback 或 knowledge update。

**容易混淆的概念：** 有一个 UserProxy 或人工入口不等于每个高风险动作都经过
人工审批；需要查看实际执行位置。

# Part 3 — 为什么需要 Agent，以及论文如何补齐能力

## 1. 什么时候普通 LLM 就够了？

一次性文本生成、简单分类、固定格式转换，以及有成熟确定性算法的问题，通常
不需要 Agent。引入循环和工具会增加延迟、成本、失败面和审计复杂度。

## 2. 什么时候 Agent 更有意义？

当任务需要下面任意几项时，Agent loop 才更有价值：

- 多轮读取不同来源的证据；
- 根据新 Observation 改变下一步；
- 动态选择工具或调查路径；
- 持续维护任务状态；
- 验证中间结果；
- 失败后重试、换路径或升级给人。

## 3. 用已读论文看不同能力

| 论文 | 先记住的直觉 | 主要补充的能力 | 不能过度推出 |
|---|---|---|---|
| [ReAct](../../papers/react/notes.md) | 边思考边行动 | Reasoning–Action–Observation 运行时循环 | 不自带 persistent memory 或完整 Planner |
| [Toolformer](../../papers/toolformer/notes.md) | 学会何时、怎样插入 API 调用 | learned tool-use policy | 不等于完整 Agent；本知识库没有可靠官方源码 |
| [Reflexion](../../papers/reflexion/notes.md) | 失败后总结经验再试 | feedback、verbal reflection、跨 attempt context | 不等于参数更新或“ReAct + memory”这一简单公式 |
| [ReWOO](../../papers/rewoo/notes.md) | 先画蓝图，再由 Worker 执行，最后 Solver 汇总 | Planner–Worker–Solver 解耦 | 主代码路径没有标准的 observation-driven replanning |
| [LLM+P](../../papers/llm-p/notes.md) | LLM 翻译问题，formal planner 负责计划 | LLM 与确定性 planner 的接口分工 | 不是通用 tool-using Agent |
| [RAP](../../papers/rap/notes.md) | 在世界模型中搜索未来分支 | MCTS、search、world-model planning | 搜索树不是现实环境，也不自动是 Agent memory |

这些论文共同告诉我们：Agent 不是一个单一算法名，而是一组可以组合的机制。

# Part 4 — 加入代码之后：Agent 到底长什么样？

## 1. Paper Concept → Code Module → Runtime Behavior

### ReAct

论文中的 Action 在 `wikienv.py:WikiEnv.step` 里变成字符串协议：`search[]`、
`lookup[]`、`think[]`、`finish[]`。`HistoryWrapper` 把 Action/Observation 交替
写回下一次 prompt。代码揭示：最小 Agent loop 需要环境 `step`、动作解析、
Observation 和历史序列化；Thought 不是隐藏状态。[ReAct 代码笔记](../../code/react/notes.md)

### ReWOO

`algos/PWS.py:PWS.run` 明确把 Planner、Worker 和 Solver 串起来；`#E1` 等变量
把 Worker 输出传给后续 Worker/Solver。代码也揭示了主路径是计划后顺序执行，
不是每次 Observation 后重新规划。[ReWOO 代码笔记](../../code/rewoo/notes.md)

### LLM+P 与 RAP

LLM+P 的 `Planner` 让 LLM 输出 PDDL，再调用 Fast Downward；RAP 的 `MCTS` 维持
搜索树，`blocksworld_mcts.py` 用 LLM 评分动作和预测状态变化。二者分别说明：
“显式 planner”可以是外部 formal solver，也可以是 search tree；不能只看 prompt
里是否出现“plan”。[LLM+P 代码笔记](../../code/llm-p/notes.md)、[RAP 代码笔记](../../code/rap/notes.md)

### Reflexion

`programming_runs/reflexion.py` 把测试反馈传给 `self_reflection`，再把 reflection
和上一版实现传给下一次生成。WebShop 路径把最近的 reflection 文本放入 memory，
并限制读取数量。代码支持“语言反馈改变后续 trajectory”，不支持把 Thought 解释
成真实 internal state。[Reflexion 代码笔记](../../code/reflexion/notes.md)

## 2. AIOps 代码揭示的不同事实

- **RCAgentBench**：指标、日志、trace 的确定性分析函数被放在 Tool 后面，ReAct
  只负责选择证据收集动作；它没有在 inspected workflow 中提供独立 RCA verifier。
- **StaR**：`TemporalMemory` 是时序模型内部状态；它不是 Agent 的 episodic memory。
  Granger 层和残差/阈值计算仍是 RCA 的核心。[StaR 代码笔记](../../code/aiops/star/notes.md)
- **StepFly**：PlanDAG、Scheduler、Executor、插件和 MongoDB 共同组成系统；LLM
  在图约束步骤内选动作，PlanDAG 不是由 LLM 任意生成的全局计划。
- **ChatRCA**：AutoGen 的角色、函数注册和结构化 `EvidenceItem` 形成多 Agent
  工作流，但 inspected code 没有证明动态 Planner、持久记忆或 recovery loop。
- **Cloud-OpsBench**：`CaseState`、`StepRecord`、严格 Action parser、snapshot
  tools 和 process-label evaluator 让 Agent 行为可测量；快照环境仍不是 live
  production cluster。[Cloud-OpsBench 代码笔记](../../code/aiops/cloud-opsbench/notes.md)
- **CHIEF**：HCG、data-flow、candidate error step 等结构由多个 LLM prompt 和
  parser 构造；它归因的是多 Agent 轨迹中的错误责任，不是网络设备 root cause。

更多身份、固定 SHA 和代码覆盖范围见[代码发现总结](../code/paper-code-discovery-summary.md)。

# Part 5 — Skill、Tool、MCP 的工程关系

## 1. Skill 到底解决什么问题？

Tool 解决“我能做什么”；Skill 解决“面对一类任务，我应该按什么规范做”。

例如：

```text
paper-code-discovery
  输入：已读论文
  流程：搜索候选仓库 → 验证身份 → 固定 SHA → 记录证据

code-reading
  输入：可靠源码
  流程：找入口 → 追执行路径 → 做 Paper ↔ Code mapping → 记录差异
```

Skill 不是模型突然学会了某项事实。它是可复用的外部约束和工作流程；真正
执行时仍要读取文件、调用工具、判断证据并做质量检查。

## 2. Skill 与 Prompt 的区别

Prompt 通常服务于一次模型调用。Skill 可以包含多个 prompt、工具顺序、失败
处理、输出模板、source grounding、质量检查和 Git 行为。

## 3. Skill 与 Agent Workflow 的区别

Skill 是规范；Agent workflow 是运行中的流程实例。一个 Skill 可以规定一个
workflow 应该怎么运行，但 Skill 自己没有环境状态，也不会自动行动。

## 4. Skill 与 MCP 的区别

MCP 解决连接标准，Skill 解决任务规范。一个 Skill 可以使用经由 MCP 暴露的
GitHub search 或 repository resource，但不需要把 MCP 误写成知识、记忆或 Agent。

# Part 6 — AIOps 是什么？

## 1. 先建立 AIOps 总图

**AIOps（Artificial Intelligence for IT Operations，智能运维）** 是用算法、
机器学习、知识和自动化处理运行系统故障与运维任务。

**Telemetry（遥测数据）** 是系统运行时产生的观测数据，包括指标、日志、trace、
流量、事件和配置等。

```text
Metrics / Logs / Traces / Traffic / NetFlow / Topology / Configuration / Alerts
                                      ↓
                                  AIOps
                                      ↓
Detection
  ↓
Localization
  ↓
RCA
  ↓
Diagnosis
  ↓
Recommendation / Remediation
  ↓
Recovery Verification
```

**Detection（检测）** 是判断是否出现异常；**Localization（定位）** 是缩小到
可能异常的实体；**RCA（Root Cause Analysis，根因分析）** 是判断最可能导致
事件的原因；**Diagnosis（诊断）** 是给出故障类别、对象或状态解释；
**Remediation（修复/缓解）** 是提出或执行改变系统状态的动作。

这些不是同一个任务：检测到异常不等于找到了 root cause，生成修复建议也不等于
修复已经成功。[AIOps RCA Concept](../../concepts/aiops/root-cause-analysis.md)

## 2. AIOps 最难的地方

| 问题 | 是什么 | 传统方法擅长什么 | LLM/Agent 可能帮助什么 | 新风险 |
|---|---|---|---|---|
| 数据异构 | 不同来源格式、含义和粒度不同 | 每种模态的专用特征/模型 | 统一解释日志、工单、SOP 和结果 | 把不同字段的相似文字误当成同一 evidence |
| 时间对齐 | 不同系统时钟、延迟和窗口不同 | windowing、统计聚合 | 解释跨时间的事件链 | 把后发生的症状误判为原因 |
| 实体对齐 | device/interface/link/service 名称不一致 | schema/映射表 | 处理别名和非结构化描述 | 证据被绑定到错误对象 |
| 大 candidate space | 可能的设备、接口、链路、模块、故障类型很多 | 枚举、图约束、排序 | 对有限候选做语义比较 | 让 LLM 在全网自由猜，难审计且难评估 |
| Topology | 系统对象之间存在物理或依赖关系 | 图算法、传播模型 | 解释路径和证据关系 | 把 dependency graph 当 physical causal graph |
| Long-tail/open-set | 新故障或未知故障少见 | 异常检测、拒识 | 生成未知假设和调查路径 | hallucination、无依据的未知原因 |
| Multi-root | 一个事件可能有多个同时原因 | 多标签/因果模型 | 组织多个假设和冲突证据 | Top-k 与 ground truth 粒度不一致 |
| Ground truth | 真实根因常要靠维修记录/专家标注 | 离线评估 | 帮助整理标注和证据 | 文本说得好不等于 root cause 对 |
| Production | 实时、规模、权限和安全限制 | 低延迟模块和硬约束 | 跨模态解释、调查和交互 | token cost、latency、错误操作 |
| Knowledge staleness | SOP、历史事件和拓扑会变旧 | 版本和生命周期管理 | 通过文本更新/归纳知识 | 旧知识被当成当前事实 |

当前 AIOps 论文的阶段性整合见 [Knowledge Review v1](../aiops/reviews/aiops-knowledge-review-v1.md)、[v2](../aiops/reviews/aiops-knowledge-review-v2.md)、[v3](../aiops/reviews/aiops-knowledge-review-v3.md)。

# Part 7 — 为什么 AIOps 使用 LLM，又为什么还需要 Agent？

## 1. LLM 的合理位置

传统 Rule、统计模型和图算法并没有“过时”。它们通常更适合：

- 数值计算、阈值、时间窗口和异常分数；
- 候选枚举、集合运算和硬约束；
- 拓扑查询、路径计算和一致性检查；
- schema 验证、权限控制、rollback 条件和恢复信号。

LLM 可能更适合：

- 理解日志、工单、SOP 和配置文本；
- 把多个已结构化的 evidence 综合成假设；
- 在有限工具集合中选择调查顺序；
- 解释候选之间的差异；
- 与 operator 交互，说明还缺什么证据。

“复杂”不等于“应该交给 LLM”。在 Network RCA 中，候选生成和拓扑硬约束
若完全依赖自然语言生成，会牺牲可控性和可评估性。

## 2. 一次输入、一次输出什么时候够？

如果问题是：

```text
已给定整理好的 evidence
→ 输出一个解释
```

LLM-assisted workflow 可能已经足够。如果问题是：

```text
先查指标
→ 结果异常，再查 syslog
→ 发现某接口相关，再查物理拓扑
→ 形成两个候选
→ 重新查询验证
→ 冲突时换调查路径或交给人
```

这才需要真正的 Agent loop，因为下一步依赖 Observation。

## 3. 当前 AIOps 论文中的 LLM / Agent 角色

下表是基于论文笔记和已读代码的当前工作判断；作者称呼和知识库判断特意分开。

| Paper | Problem | LLM role | Current classification | Tools / evidence | Verification / remediation |
|---|---|---|---|---|---|
| RCAgentBench | multimodal microservice RCA / Agent benchmark | 选择证据工具、汇总结果、输出组件诊断 | bounded Agent variants / benchmark | metrics、logs、traces、system context | benchmark evaluation；无 inspected recovery executor |
| CAUSALDX | long-tail/cascading incident diagnosis | causal reasoning / candidate analysis | LLM-guided workflow，完整 Agent loop 仍需谨慎 | telemetry/causal evidence，具体以论文笔记为准 | tool/check 机制；非自动修复 |
| LLMGuard | LMaaS fault diagnosis | 多 Agent diagnosis 与确定性检查配合 | Agentic diagnosis workflow | service/runtime evidence | deterministic guard/check 是重要部分；不等于 remediation |
| KAT | telecom troubleshooting | knowledge-context augmentation | LLM + knowledge workflow；完整 Agent status 未充分确立 | knowledge graph / operational context | 主要是诊断增强，不自动推出执行修复 |
| Comfey | production cloud incident triage | incident understanding / team routing | production triage agent，目标不是完整 physical RCA | incident context / operational data | routing/triage，不等于 network repair |
| AIM | alert summarization / mitigation plan | 生成 summary 与 advisory mitigation plan | LLM-assisted workflow | alert 中的 logs、metrics、hostname | QAGS/质量/安全评分；代码未见真实 repair execution |
| StepFly | troubleshooting-guide execution | Scheduler/Executor 步骤内动作选择 | fixed PlanDAG + bounded agentic workflow | TSG、SQL、插件和诊断工具 | node/edge status、retry/timeout；恢复验证仍需补强 |
| TSGen | troubleshooting-guide generation | 从历史 incident 生成 TSG | knowledge curation pipeline | historical incidents / guide content | 不是已验证的运行时 Agent |
| ChatRCA | multimodal RCA | Observation、Architecture、Resource、Network 等角色分析 | role-based Multi-Agent workflow | data、metric、log、trace、architecture functions | human proxy 可用；未见独立 recovery verification |
| Cloud-OpsBench | reproducible Agentic SRE evaluation | 下一工具选择和结构化 diagnosis | bounded single-agent ReAct benchmark | frozen snapshot tools | process/evidence evaluation；没有 live remediation |
| CHIEF | multi-agent trace failure attribution | 重建 HCG、候选错误步骤和最终归因 | LLM analysis pipeline，不是 ops Agent | completed trajectory + example RAG | benchmark attribution，不是 network recovery |
| FlowFixer | diagnosis-driven repair of agentic workflow | 诊断/生成 repair 的一部分 | workflow repair architecture；当前无可靠 clone | workflow trace/specification | validation/repair lifecycle 是重点，真实网络执行需另证 |

这张表最重要的结论是：**LLM 在 AIOps 中可以负责理解和组织，但 Agent 身份、
工具闭环、验证和修复执行必须逐篇看真实流程。**

# Part 8 — 当前 Hybrid Network AIOps Framework

以下是基于 10 篇 AIOps 全文论文、代码静态阅读和 Architecture Synthesis 形成的
**cross-paper synthesis / research architecture hypothesis**，不是某篇论文的标准
框架，也没有被当前材料证明为唯一最优设计。

## 1. Working pipeline

```text
Incident / Failure
        ↓
Telemetry Collection
        ↓
Evidence Normalization and Time/Entity Alignment
        ↓
Detection / Event Formation
        ↓
Evidence Provenance
        ↓
Candidate Space Construction
        ↓
Topology / Dependency / Causal Constraint
        ↓
Candidate Pruning
        ↓
Bounded LLM / Agent Investigation
        ↓
Independent Verification
        ↓
Diagnosis / Explanation
        ↓
Proposed Remediation
        ↓
Safety Check + Human Approval
        ↓
Controlled Execution
        ↓
Recovery Verification
        ↓
Knowledge / Memory Update
```

## 2. 每一层更适合谁来做？

| 阶段 | 首选机制 | 原因 | LLM/Agent 的合理参与 |
|---|---|---|---|
| Telemetry collection | deterministic collectors / read-only Tools | 需要稳定、可追踪、低延迟 | 选择有限查询，不直接伪造数据 |
| Time/entity alignment | deterministic schema、映射和聚合 | 对齐错误会污染所有后续结论 | 解释别名或提出待确认映射 |
| Detection | statistical / ML / rule | 数值模式更可重复 | 解释异常或组合多个检测结果 |
| Evidence provenance | deterministic data contract | 必须保留 source/entity/time/query | LLM 读取，不负责凭空补字段 |
| Candidate universe | topology / hierarchy / deterministic enumeration | 需要覆盖、可评估、可约束 | 在已定义候选中比较 |
| Candidate pruning | graph / score / causal / rule hybrid | 缩小搜索空间并保留召回率 | 解释 pruning 或处理语义 evidence |
| Investigation | bounded Agent + read-only Tools | 下一步可能依赖新 observation | 选择调查顺序、提出假设 |
| RCA ranking | hybrid algorithm + grounded LLM | 兼顾数值、结构和异构文本 | 在候选与证据边界内排名/解释 |
| Verification | independent rule/tool/fresh observation | 自我复述不够独立 | 生成验证计划，不能替代验证器 |
| Remediation proposal | LLM + deterministic action schema | 文本知识可帮助生成建议 | 只能输出受约束 proposal |
| Remediation execution | deterministic executor + permission + human gate | 有实际系统副作用 | 默认不直接掌握高影响权限 |
| Recovery verification | fresh telemetry / health signal / rollback | 需要观察结果而非生成文本 | 解释恢复证据和异常残留 |
| Knowledge update | versioned human-reviewed process | 防止 stale/hallucinated knowledge 累积 | 起草摘要，不能无审核写入生产规则 |

## 3. 为什么 Detection 不一定交给 LLM？

检测通常需要扫描大量数值流、计算阈值、处理窗口和控制延迟。传统/ML 模块
可以给出稳定分数；LLM 更适合解释“哪些异常可能相关”或决定后续查询。把所有
原始 time series 塞进 prompt 会同时造成 token、延迟、数值精度和 provenance 问题。

## 4. 为什么 Candidate Space 要显式？

**Candidate Space（候选空间）** 是允许成为根因的对象或故障类型集合，例如：

```text
device
├── interface
├── optical module
└── configuration
link
path
fault type
```

显式候选空间的价值是：

- 明确“模型究竟在选择什么”；
- 让 Top-k、MRR 或 hit rate 有清楚的定义；
- 可以加入物理拓扑、层次和权限约束；
- 支持候选覆盖率、pruning recall 和 unknown 拒答评估。

让 LLM 在 `10^4` 或 `10^5` 个网络对象中自由生成 root cause，可能漏掉正确
对象、产生不存在的对象、混淆粒度，且很难验证。更稳妥的研究假设是：

```text
Candidate universe
→ hierarchy / physical topology / dynamic evidence pruning
→ bounded candidate set
→ LLM reasoning / ranking
```

这仍然需要实验回答：过度 pruning 会不会删除真正的 root cause？

## 5. Topology 不只是一个 Graph

当前资料至少要区分：

- **Physical topology**：设备、接口、链路、光模块等真实连接。
- **Logical topology**：路由、路径、服务或虚拟网络关系。
- **Dependency graph**：一个服务或组件依赖另一个组件。
- **Dynamic dependency**：关系随时间、流量或状态变化。
- **Causal graph**：用于表达因果假设或因果发现的图。
- **Knowledge graph**：把实体、规则、文档和关系组织起来。

它们可能承担不同角色：

```text
candidate generator
hard constraint
propagation path
ranking prior
evidence organizer
LLM context
verification check
```

不要把“变量名叫 graph”就写成 physical causal graph。StaR 的动态图/Granger
关系、CHIEF 的轨迹 HCG、StepFly 的 PlanDAG 和 Network physical topology 是
不同对象。[Topology-aware RCA Concept](../../concepts/aiops/topology-aware-rca.md)

## 6. Evidence Ticket 与 Provenance

**Evidence Provenance（证据来源链）** 记录一条 evidence 从哪里来、描述哪个
实体、对应什么时间、经过什么处理、支持或反驳哪个候选。

一个 Network Evidence Ticket 可以暂时设计为：

```text
source:
  metric query / syslog / NetFlow / configuration / topology tool
tool/query:
  exact operation and parameters
entity:
  device / interface / link / module / path
timestamp:
  event time, collection time, window and timezone
observation:
  value, text, event or derived feature
transformation:
  aggregation, normalization, anomaly rule or model version
freshness:
  data delay and validity window
confidence:
  measurement/model confidence
candidate relation:
  supports / contradicts / unrelated / unknown
provenance:
  source record ID, query ID, schema/version
```

这样做的意义是：

```text
Evidence → source/entity/time → candidate relation → reasoning → verification → audit
```

没有 provenance，就很难回答“这个数是谁查的、什么时候的、对应哪个接口、是否
被聚合过、为什么支持这个 root”。[Evidence Provenance Concept](../../concepts/aiops/evidence-provenance.md)

## 7. LLM 应该放在哪里？

| 放置位置 | 优点 | 主要风险 | 必要条件 |
|---|---|---|---|
| 直接预测 root cause | 简单、端到端 | 超大候选、幻觉、粒度不一致 | 明确候选、校准、独立验证 |
| candidate ranking | 让算法先缩空间 | 可能受输入候选偏差影响 | candidate recall + provenance |
| evidence synthesis | 适合异构文本和跨模态解释 | 把相关性说成因果 | 结构化 evidence + source links |
| tool orchestration | 能根据结果动态调查 | 错误参数、循环、成本失控 | typed tools、budget、stop/fallback |
| explanation | 便于 operator 理解 | 解释可能是事后编造 | 只允许引用已记录 evidence |

条件化结论是：LLM 可以参与 root-cause decision，但不应成为唯一的对象枚举、
硬约束、执行和验证来源。更安全的形式是“bounded decision + independent check”。

## 8. Agent 什么时候真正有价值？

当 Network RCA 需要：

```text
查询 metrics
→ 根据异常接口查询 syslog
→ 沿物理拓扑查邻居/链路
→ 对比 traffic/NetFlow 时间窗口
→ 形成候选
→ 重新查询验证
→ 证据冲突时换路径或请求人工
```

这类 Observation-dependent investigation 才体现 Agent 的价值。如果所有输入
已经是整理好的固定表格，且流程固定为三个函数调用，普通 workflow 可能更可控。

## 9. Verification 为什么不能只靠 Agent 自己说“已确认”？

可以按强度形成一个当前 working hierarchy：

```text
弱：LLM self-check / 改写自己的答案
  ↓
较强：独立 model / critic
  ↓
更强：deterministic schema/rule/topology consistency
  ↓
更强：fresh telemetry re-query / cross-modal corroboration
  ↓
强：controlled execution + observed outcome
  ↓
高影响动作最强：recovery signal + human gate + rollback path
```

这里的“强”不是绝对真理；不同故障需要不同验证。root cause 可以用新鲜
telemetry、拓扑一致性和独立算法交叉检查；remediation 则还需要安全检查、受控
执行、结果观察和回滚条件。

## 10. Remediation 的三层

```text
Diagnosis
  ↓
Proposed Action（建议做什么）
  ↓
Safety Check（是否允许做）
  ↓
Human Approval（是否由人批准）
  ↓
Controlled Execution（实际执行）
  ↓
Observe（重新采集）
  ↓
Recovery Verification（确认恢复）
  ↓
Rollback if needed（必要时回滚）
```

“输出 `reset interface`”是 recommendation；“真正调用配置/操作接口”是
execution；“错误消失且服务恢复”才接近 recovery。AIM 的代码主要停留在文本
计划与安全评分，StepFly 有插件/步骤执行但 inspected path 尚未证明完整的网络
恢复验证；因此不能把任意 mitigation plan 叫作 autonomous remediation。

# Part 9 — Traditional AIOps、LLM AIOps 与 Agentic AIOps

| 形态 | 典型流程 | 优势 | 限制 |
|---|---|---|---|
| Traditional / Algorithmic | telemetry → rule/ML/graph → score | deterministic、低延迟、规模化、易测 | 异构文本、未知模式和跨源解释较弱 |
| LLM-assisted | structured evidence → LLM → summary/diagnosis | 文本理解、综合和解释强 | 一次输出可能无调查闭环，容易幻觉 |
| Tool-augmented LLM | LLM → tool → result → answer | 能获得实时外部信息 | 工具选择/参数/权限/验证仍需控制 |
| Fixed Agentic Workflow | scheduler/DAG → LLM steps + tools | 阶段、权限和审计较清晰 | 对新路径和异常分支适应有限 |
| Agent | state → next action → observation → next action | 动态调查、失败恢复、路径选择 | 成本、延迟、循环、安全和评估更难 |
| Multi-Agent | 多角色/多模型共享证据和消息 | 专门化角色、分工、并行意见 | 通信成本、责任边界和错误传播更复杂 |

当前文献和代码共同支持的方向更像 **Hybrid RCA**：确定性/ML 处理数值和
结构边界，LLM/Agent 处理有限范围内的证据解释和调查，人控制高影响动作。

# Part 10 — 代表论文分别解决什么问题？

## Agent / LLM 基础

### ReAct

- **Problem**：让语言模型在推理和外部行动之间交互。
- **Main idea**：Thought、Action、Observation 交替形成 trajectory。
- **Why it matters**：定义了最直观的 runtime interaction loop。
- **Limitation**：没有自动提供长期 Memory、独立验证和安全执行。[论文笔记](../../papers/react/notes.md)

### Reflexion

- **Problem**：一次失败后如何改进下一次尝试。
- **Main idea**：Evaluator feedback → verbal reflection → next attempt context。
- **Why it matters**：把“从失败学习”与参数更新区分开。[论文笔记](../../papers/reflexion/notes.md)

### ReWOO、LLM+P、RAP

- ReWOO 展示 Planner–Worker–Solver 的模块解耦，但主代码是 plan-first 执行。
- LLM+P 展示 LLM 与 formal planner 的接口分工。
- RAP 展示 MCTS + world model 的 search-based planning。

它们共同帮助区分：next-step reasoning、显式计划、外部 formal planning、搜索
和 runtime Agent loop。[ReWOO 论文笔记](../../papers/rewoo/notes.md)、[LLM+P 论文笔记](../../papers/llm-p/notes.md)、[RAP 论文笔记](../../papers/rap/notes.md)

## AIOps 代表论文

### StaR：算法化时序 RCA

StaR 用 temporal state、dynamic graph、Granger-style causal discovery、重构
和 root-cause scoring 处理多变量时间序列。它说明 Network RCA 不一定需要 LLM；
时序模型、状态和图算法可能是 LLM 前面的强基础。

### RCAgentBench：让 Agent RCA 可测量

它把 metrics/logs/traces 和工具调用放入 Agent-oriented benchmark。代码中
`StepRecord`、快照工具、严格输出契约和 evidence matcher 说明：如果要研究
Agentic AIOps，必须评估过程证据，而不只是最终文本。

### ChatRCA：角色化多 Agent

它把 Observation、Architecture、Resource、Network 和最终 OperationEngineer
等角色组织到 group chat，并用结构化 Evidence/Diagnosis schema。它说明多角色能
组织证据，但不自动解决 candidate、verification 和 remediation safety。

### StepFly：固定图约束下的 Agent

它把 TSG/PlanDAG、Scheduler、Executor、工具和持久 session state 结合起来。它
说明一个生产倾向的系统可以把确定性流程图放在外层，把 LLM 灵活性限制在步骤内。

### Cloud-OpsBench：Agent benchmark 的边界

它冻结故障 snapshot，给 Agent 可重复的工具和严格诊断格式，并评估 trajectory。
它适合作为 Network benchmark 设计启发，但 frozen snapshot 不等于 live production
environment，closed label list 也不等于 open-set RCA。

### CHIEF / FlowFixer：错误归因与修复闭环

CHIEF 关注多 Agent trajectory 中“谁在什么时候引入关键错误”；FlowFixer 关注
workflow diagnosis-driven repair。二者启发我们把错误传播、修复验证和恢复反馈
单独建模，而不是把 final answer 当作完整 RCA。[CHIEF 代码笔记](../../code/aiops/chief/notes.md)

# Part 11 — Code-backed Insights

## What the Source Code Reveals

1. **Agent 通常是少数可组合模块的循环**：prompt builder、LLM、action parser、
tool executor、observation serializer、stop condition。
2. **确定性 preprocessing 可能比 LLM 更接近核心 RCA 能力**：RCAgentBench 的
模态工具、StaR 的时序模型、Cloud-OpsBench 的 snapshot query 都说明这一点。
3. **Planner 的名字不够**：LLM+P 的 formal planner、RAP 的 MCTS、ReWOO 的
plan-first PWS、StepFly 的固定 PlanDAG 是四种不同实现。
4. **Memory 变量名不够**：ReAct 是 trajectory context，Reflexion 是跨尝试文本
reflection，StaR 是 temporal neural state，StepFly 是 session-scoped MongoDB。
5. **结构化 JSON 不等于事实验证**：ChatRCA、AIM 和 Cloud-OpsBench 都有 schema，
但 schema 需要与证据、ground truth、独立检查或执行结果结合。
6. **RAG 的内容决定其意义**：CHIEF 的 FAISS 主要取 GAIA/AssistantBench 示例；
ReWOO 的 search worker 把结果写进当前 worker log；两者都不等于 Network memory。
7. **论文系统边界可能宽于公开代码**：多个 repository 同时包含 baseline、demo、
benchmark 或部分实现，不能把未看到的组件补进架构。

完整 repository 身份、SHA、license 观察和代码—论文差异见[发现总结](../code/paper-code-discovery-summary.md)。

# Part 12 — 这对我的 Network AIOps 研究意味着什么

当前研究关注：Detection、RCA、Fault Classification/Diagnosis、metrics、syslog、
traffic/NetFlow、topology、multimodal telemetry、large candidate space、LLM/Agent
和 production evaluation。

高层 mapping 可以先写成：

```text
metrics / syslog / traffic / NetFlow / configuration / topology
        → telemetry and evidence layer
        → time/entity alignment + provenance
        → detection and event formation
        → device/interface/link/module/path candidate hierarchy
        → physical + dynamic dependency constraints
        → bounded LLM/Agent investigation
        → independent verification
        → diagnosis / classification
        → human-gated network action
        → recovery verification
```

这不是说当前实验系统已经实现了全部模块；它是当前资料支持的研究 mapping。

真正的问题不是“怎么把 GPT 放进去”，而是：

> 哪些不确定、动态、需要多轮调查的步骤值得 Agent 参与，以及如何用
> deterministic constraints、evidence provenance、candidate space、tools、
> verification 和 human gates 保证它可靠？

## 1. 值得优先研究的 8 个问题

| Priority | 问题 | 为什么重要 | 当前证据/缺口 |
|---:|---|---|---|
| 1 | 多模态 evidence 如何完成 entity/time alignment？ | 错位会使后续 RCA 全部失真 | 现有论文分模态处理较多，统一 Network schema 仍不足 |
| 2 | Evidence Ticket 的最小 provenance 字段是什么？ | 决定能否 audit、复查和 verification | ChatRCA/RCAgentBench/Cloud-OpsBench 提供局部启发，尚无统一协议 |
| 3 | 如何构造 hierarchical candidate space？ | 支持 device/interface/link/module 多粒度评估 | CHIEF 的 hierarchy 是轨迹归因，不是物理网络；迁移仍是 hypothesis |
| 4 | physical topology 与 dynamic dependency 如何结合？ | 静态连接和运行时传播各自不完整 | StaR/各类 dependency graph 不能直接替代 physical topology |
| 5 | 如何处理 open-set 与 multi-root RCA？ | closed-set Top-k 在真实网络中不够 | 当前 benchmark/论文常有固定标签或有限候选 |
| 6 | Agent investigation 的最小闭环是什么？ | 决定何时值得引入 Agent | 需要 observation→next action→verification 的受控接口 |
| 7 | 如何验证 diagnosis、repair 和 recovery？ | 文本正确不等于系统恢复 | 当前文献对 independent recovery signal 支持较弱 |
| 8 | 如何评估 production Agent？ | 只测 accuracy 会忽略 cost、latency、tool error、安全 | Cloud-OpsBench 提供过程评估启发，但 Network 场景需扩展 |

更多当前 gaps 和问题：[AIOps research gaps](../aiops/research-gaps.md)、[AIOps questions](../aiops/questions.md)。

# Part 13 — 现在先不用深入学习什么

当前目标是建立 Agent / AIOps 全局理解，以下内容先知道名字和大概作用即可：

- PDDL 的完整形式化规划语法；先理解它是让 LLM 接入 formal planner 的表示。
- MCTS 的数学细节；先理解它是通过搜索树比较未来分支的 planning 方法。
- World Model 的训练细节；先理解它是对行动后状态变化的模型化预测。
- 所有 Agent framework API；先理解 loop、tool、state、observation、verification
  的职责，再选具体框架。
- 向量数据库和 embedding 工程；先区分 RAG、Memory、Context，再决定是否需要。
- 复杂 Multi-Agent 通信协议；先问多个角色是否真正带来不同能力。

这些不是不重要，而是当前还不应遮住主线：**系统从任务到证据、决策、验证和
恢复是如何运行的。**

# Part 14 — Suggested Learning Roadmap

## Level 1 — Big Picture

先掌握：LLM、Agent、Tool、Observation、Environment、Context、Verification。
阅读：[Agent Concept](../../concepts/agent.md)、[AIOps Architecture Synthesis](../aiops/reviews/network-aiops-architecture-synthesis-v1.md)。

## Level 2 — Core Agent Concepts

顺序建议：ReAct → Toolformer → Reflexion → ReWOO。目标是区分 runtime loop、
learned tool use、跨 attempt feedback 和 plan-first workflow。

## Level 3 — Tools / Skills / MCP

先理解 Tool 与 Skill 的边界，再看 MCP 如何连接外部能力。可直接阅读当前
[Skills 总索引](../../skills/README.md) 和 [paper-code-discovery](../../skills/paper-code-discovery/SKILL.md)。

## Level 4 — Memory / Planning / Verification

用 Reflexion、LLM+P、RAP、ReWOO 对比 memory、reflection、formal planning、search
和 planner/executor；再用 AIOps verification concept 把“结论如何被证实”补上。

## Level 5 — AIOps + Agent

先掌握 Detection、Localization、RCA、Diagnosis、Evidence Provenance、Candidate
Space、Topology 和 Recovery Verification。阅读顺序可参考 [AIOps Review v1–v3](../aiops/reviews/)。

## Level 6 — Network AIOps Research

围绕 RQ1 evidence alignment/provenance、RQ2 hierarchical open-set/multi-root
candidate space、RQ3 verified human-gated remediation 选专题批次，优先关注能
补当前 Hybrid RCA architecture 缺口的论文和 benchmark。

# Part 15 — Glossary

- **LLM**：根据上下文生成语言或结构化输出的模型。
- **Agent**：围绕目标持续决策、行动、读取反馈并推进任务的系统。
- **Tool**：Agent 可调用的外部能力，如查询、搜索、执行或写入接口。
- **Skill**：规定一类任务如何执行的可复用流程、约束、模板和质量检查。
- **MCP**：连接模型应用与外部工具/资源的标准化协议。
- **Prompt**：一次模型调用使用的任务说明、上下文和输出约束。
- **Context**：当前模型调用能看到的信息。
- **Memory**：在之后仍能保存并重新利用的信息机制。
- **RAG**：先检索外部资料，再把资料放入上下文生成内容。
- **Reasoning**：针对当前问题解释证据并作出下一步判断。
- **Planning**：组织未来多个步骤或子目标的过程。
- **Reflection**：根据过去尝试和反馈进行复盘，并影响后续尝试。
- **Observation**：行动或工具执行后从外界得到的结果。
- **RCA**：Root Cause Analysis，寻找导致事件的最可能根因。
- **Telemetry**：系统运行过程中产生的指标、日志、trace、流量、事件等观测数据。
- **Topology**：对象之间的连接或依赖结构；物理、逻辑、动态和因果图不是同一对象。
- **Candidate Space**：允许被考虑为根因的对象或故障类型集合。
- **Evidence Provenance**：证据的来源、实体、时间、查询、处理过程和候选关系。
- **Verification**：用独立或可检查证据判断结论、动作或恢复是否成立。
- **Remediation**：改变系统状态以缓解或修复故障的建议或动作。
- **Recovery Verification**：执行修复后，用新的系统信号确认服务确实恢复。
- **Human-in-the-loop**：在关键阶段由人查看、批准、纠正或接管。

## 最后先记住这 7 条

1. LLM 是模型；Agent 是围绕目标运行的闭环系统。
2. Tool 是外部能力；Skill 是可复用的任务规范；MCP 是连接方式。
3. Reasoning、Planning、Reflection 都与“思考”有关，但发生时机和作用不同。
4. Thought 是显式语言轨迹，不等于模型真实 internal state。
5. Context、trajectory、RAG、persistent memory 不能混成一个概念。
6. AIOps 中 Detection、RCA、Diagnosis、Recommendation、Execution、Recovery 是不同阶段。
7. Network AIOps 更可能需要 Hybrid：确定性结构和验证 + 有边界的 LLM/Agent + 人工控制高风险动作。
