Status: evolving

# Tool Use

## Definition

Tool Use 是模型向外部能力发出任务相关请求、接收返回结果，并把结果用于后续生成或决策的机制。它至少包含四个可分别设计和评估的接口：

1. **调用决策**：是否调用、何时调用、调用哪个工具。
2. **调用表示**：工具名、参数和结束标记如何序列化。
3. **执行与结果**：外部工具如何运行，结果以什么形式返回。
4. **上下文整合**：结果如何进入模型后续的 context，以及模型是否能继续交互、重试或链式调用。

有 Tool Use 能力的 LM 不自动等于完整 Agent；还需要根据目标、环境状态、执行器、记忆和持续决策等边界判断系统形态。

## Why It Matters

语言模型的参数化知识和生成能力并不天然适合精确计算、最新事实、外部状态或专门服务。工具可以补充这些能力，但工具接入的价值取决于模型是否能在合适时机发出有效调用、正确解析结果，并在结果无用或错误时继续处理。

ReAct 和 Toolformer 共同说明，工具调用不一定是回答末尾的一次固定检索：它可以受到当前 context 驱动，并影响后续生成。但两者也说明“会调用工具”仍然可能对应完全不同的训练方式和运行时架构。

## Review Synthesis

Tool Use 应拆成以下接口和决策层，而不是用“会调用工具”概括全部能力：

1. **Tool selection：** 是否调用、何时调用、选择哪个工具。
2. **Invocation / serialization：** 工具名、调用协议、结束标记和调用格式如何表示。
3. **Argument generation and validation：** 参数如何生成、解析、校验和修正。
4. **Tool execution：** 执行器、权限、超时、失败和副作用如何处理。
5. **Observation / result integration：** 返回值如何规范化、验证并进入后续 context。
6. **Continuation / termination：** 是否重试、链式调用、改写参数或结束任务。

贯穿这些接口的是 **tool-use policy**：模型或系统通过 prompt、训练或更高层规划决定何时、如何调用工具。ReAct 主要提供 runtime interaction evidence，Toolformer 主要提供 training-time learned policy evidence，Reflexion 主要提供 feedback-driven adaptation evidence；三者不是一个统一算法。（Source: [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md); [Reflexion paper note](../papers/reflexion/notes.md)）

## Core Mechanism

Reflexion 可以把使用 ReAct 或 Wikipedia API 的 Actor 放进外层反馈循环；它的新增机制是 evaluator → reflection → episodic memory，而不是学习何时调用工具，因此与 Toolformer 的 learned call policy 属于正交层次。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3; Sec. 4.2）

LLM+P 提供了一个外部规划器作为模块的边界案例：LLM 生成 PDDL problem，classical planner 执行结构化搜索，之后结果再被翻译或交给机器人 executor。把 planner 接到系统中属于外部能力调用，但它不是 Toolformer 式的 learned API-use policy，也不自动构成 Agent。（Source: [LLM+P paper note](../papers/llm-p/notes.md); Sec. III）

ReWOO 把工具调用放在 Planner–Worker–Solver 流程中：Planner 先生成带 evidence placeholders 的请求，Worker 执行工具，Solver 最后整合 evidence。它说明 tool invocation、result integration 和 reasoning scheduling 可以由不同模块承担，但不代表 Planner 已经学习了通用 API-use policy，也没有自动提供验证或 replanning。（Source: [ReWOO paper note](../papers/rewoo/notes.md); Sec. 2.1–2.2）

AIM 提供了 AIOps 中的另一种边界：历史 exemplar retrieval 是 context retrieval，Ansible playbook 执行才是具有副作用潜力的 action/tool path。它在 YAML 与 namespace 层面做轻量验证并在 Robot Shop 测试床执行，但没有展示 LLM 在生产环境中自主选择、校验和重试多种 telemetry 工具。因此，检索、脚本生成、脚本执行和 remediation success 仍应分别评估。（Source: [AIM paper note](../papers/aiops/aim/notes.md); Sec. 3.3–3.4; Sec. 4.4.6）

StepFly 把工具接口进一步拆开：QPP 负责用参数填充既有查询模板，数据库/DevOps/指标插件负责执行，结果写入结构化 memory，Executor 只消费引用或摘要。它减少了复杂查询的自由生成错误，但仍不等于模型学会了通用工具选择或具备 unrestricted remediation。（Source: [StepFly paper note](../papers/aiops/stepfly/notes.md), Sec. 4.3–4.4.3）

TSGen 中的 incident-record retrieval、embedding/clustering 和 vector-database retrieval evaluation 属于知识处理或检索基础设施，不是运行时排障工具执行。它没有证明 LLM 自主选择 telemetry query、读取 live Observation 或执行 remediation；因此应把“检索历史事件”和“调用改变环境的工具”分开记录。（Source: [TSGen paper note](../papers/aiops/tsgen/notes.md), Sec. 4, Sec. 5.2–5.3）

## Planning Boundary

Tool Use 与 Planning 可以组合，但职责不同：Tool Use 关心是否调用、如何序列化参数、如何执行及如何整合结果；Planning 关心未来多个步骤、子目标、依赖和可能的修正。ReWOO 的 evidence placeholder 把工具请求嵌入计划，LLM+P 的 classical planner 也可以被系统视为外部求解模块，但两者都不因此自动获得 learned API-use policy 或完整 Agent loop。（Cross-paper synthesis; [LLM+P paper note](../papers/llm-p/notes.md); [ReWOO paper note](../papers/rewoo/notes.md)）

一个与具体论文无关的最小抽象是：

~~~
Context
→ Decide whether / when / which tool
→ Serialize tool call
→ Execute tool
→ Serialize and insert result
→ Continue, retry, chain, or finish
~~~

其中：

- **ReAct** 在运行时通过 few-shot trajectory 生成 Thought 和文本 Action；外部 Action 后的 Observation 进入下一轮 context，形成 `Thought → Action → Observation → ...` 的反馈闭环。
- **Toolformer** 在训练时让 LM 采样 API call，执行调用，并保留能降低 future-token loss 的 call/result；微调后，模型在普通 token generation 中生成 API 标记，外部结果作为线性化文本进入 context。
- 两者都使用文本形式的接口，但文本接口本身不等于现代 structured function calling，也不自动提供 schema、权限、安全或错误恢复。

**Source:** [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md).

## Typical Architecture

~~~
LM / Policy
→ Call decision
→ Tool adapter / executor
→ External capability
→ Result normalization
→ LM context
~~~

实际系统还需要处理：

- 参数校验、认证和权限边界。
- 超时、空结果、错误结果、冲突结果和重试。
- 结果是否可信、是否需要引用或二次验证。
- 多次调用之间的状态、成本和终止条件。
- 结果是临时 context，还是被保存到可检索的 Memory。

这些是 Tool Use 系统的通用设计问题，不应从某一篇论文的文本 API 自动推断出来。

## Cross-Paper Distinctions

| 维度 | ReAct | Toolformer |
| --- | --- | --- |
| 调用决策在哪里形成 | 主要在推理时由 prompt 示范和当前 trajectory context 产生；ReAct 论文也另行探索了轨迹微调。 | 训练时由候选调用的 future-token loss 过滤，推理时成为 token-generation 行为。 |
| 调用如何表示 | 文本化的 `Search`、`Lookup`、`Finish` 等 Action。 | `<API> name(input) ! result </API>`；实际使用 `[`, `]`, `->` token 序列。 |
| 工具结果如何进入 context | Action 之后作为 Observation，直接成为下一次 Thought/Action 的外部反馈。 | 作为 API call 内部的文本 response，插入后继续预测原始文本或后续 token。 |
| 是否以运行时交互闭环为核心 | 是，可根据 Observation 继续行动、改写查询或结束。 | 当前方法的重点是训练工具调用能力；作者明确指出不支持可靠的 chained / interactive use。 |
| 是否是完整 Agent 架构 | 研究 agent-environment interaction，但没有独立 Planner/Memory 模块。 | 论文主要把它定位为 LM；有 API 选择不等于完整 Agent runtime。 |

这个比较的结论是：ReAct 主要改变运行时的 reasoning/acting 组织方式；Toolformer 主要改变 LM 如何通过自监督微调学会插入和使用 API call。两者可以组合，但不应描述成同一种 Agent 架构。

ReWOO 提供了第三种当前资料中的组织方式：它不在每次 tool call 后让 Planner 继续生成，而是先完成 foreseeable blueprint，再让 Worker 填充 evidence，最后由 Solver 统一读取。这样降低了重复 context 和工具失败对计划生成的即时影响，但也牺牲了 Planner 对实时 Observation 的直接适应能力。（Cross-paper synthesis; [ReWOO paper note](../papers/rewoo/notes.md); Sec. 2.1–2.2）

**Source:** [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md).

## Example

- 在 ReAct 式任务中，模型先生成一个检索 Action，读取 Observation，发现证据不足后改写查询，再继续行动。
- 在 Toolformer 式任务中，模型在普通文本中生成一个 API call；执行器返回文本结果，结果被放回 API 序列，模型继续预测后续文本。当前论文的训练方式没有可靠教会模型把一个工具的结果作为另一个工具输入。

## Related Concepts

- [Agent](agent.md)
- [LLM](llm.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)
- [Memory](memory.md)
- [RAG](rag.md)
- [MCP](mcp.md)
- [Context Engineering](context-engineering.md)
- [Reflection](reflection.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 展示运行时 Thought、Action、Observation 的交错闭环。
- [Toolformer: Language Models Can Teach Themselves to Use Tools](../papers/toolformer/notes.md) — 展示通过候选调用、工具执行和 future-token loss filtering 自监督学习 API 使用。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — 展示工具型 Actor 外层的反馈、reflection 和跨 attempt memory；核心不是工具调用策略学习。
- [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../papers/llm-p/notes.md) — 展示把 PDDL 与 classical planner 接入自然语言模型的 solver-backed 外部模块边界。
- [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](../papers/rewoo/notes.md) — 展示 Planner–Worker–Solver 中的工具执行与 evidence integration。
- [AIM: Leveraging LLMs for Alert Summarization and Mitigation Plan Generation](../papers/aiops/aim/notes.md) — 展示自适应 exemplar retrieval、计划生成与受限 Ansible 执行之间的边界。
- [TSGen: Automated Troubleshooting Guide Generation](../papers/aiops/tsgen/notes.md) — 展示历史事件检索/聚类用于 operational-knowledge 生成，而不是在线 Agent tool execution。

## Representative Systems / Code

## Advantages

- 能访问模型参数中没有、过时或需要精确计算的外部信息。
- 可以把专门能力封装成可复用的接口，而不必把所有能力都重新训练进基础模型。
- 如果结果进入后续 context，模型可以基于外部反馈继续生成，而不是只能一次性决定答案。
- Toolformer 表明，调用时机和参数选择可以由模型自身的预测反馈学习；ReAct 表明，运行时反馈可以约束后续 reasoning 和 action。

## Limitations

- 文本协议灵活但容易产生解析歧义；它不自动提供结构化校验、权限控制或安全执行。
- 工具结果可能错误、冲突、过时或包含恶意指令；“进入 context”不等于已经被验证。
- 调用成本、延迟、失败恢复和终止条件会影响系统是否真正有用。
- 单次或独立调用机制不能自动支持 chained use、交互式搜索或复杂多步任务。
- 工具调用的训练信号可能是代理目标：Toolformer 的 loss reduction 衡量结果是否帮助预测后续文本，不等于普遍的任务效用、事实正确性或安全性。
- 运行时 trajectory 中保留历史不等于 persistent memory；工具使用能力也不等于显式 Planner 或完整 Agent。

## My Understanding

Tool Use 不是一个单一组件，而是一条从“决定调用”到“把结果纳入下一次决策”的接口链。比较 ReAct 和 Toolformer 后，最重要的区分是：ReAct 把工具结果组织成运行时的 Observation feedback loop；Toolformer 把有用的 API call/result 模式学习进 LM 的 token prediction。前者强调可交互的任务轨迹，后者强调训练得到的调用策略；调用格式相似并不能抹平这个差异。

## Common Confusions

- Tool result 进入 context 不等于结果已经被验证，也不等于系统拥有 persistent memory。
- Tool-use policy 不等于 Planner；前者决定调用行为，后者组织更长时程的目标和步骤。
- Reflexion 的 reflection 是工具型 Actor 外层的反馈机制，不是新的 tool-selection 算法。
- 文本 API、ReAct Action 和现代 structured function calling / MCP 不能仅凭名字视为同一种接口。

## Open Questions

- 如何让语言灵活的调用接口同时具有 schema 校验、权限边界和安全执行？
- 工具返回冲突、过时、错误或恶意信息时，模型如何判断可信度并恢复？
- future-token loss reduction 与真实任务 utility、正确性和 calibration 的关系是什么？
- 如何让模型可靠地进行工具链式调用、交互式查询和失败后的重试？
- Toolformer 的 learned call policy 如何迁移到新 API、structured tool calling 或 MCP？
- ReAct 的 runtime trajectory 与 Toolformer 的训练增强语料能否组合成既会选择工具又能稳定多步交互的 Agent？
