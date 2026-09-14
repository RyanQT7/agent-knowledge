Status: evolving

# Planning

## Definition

Planning 是围绕目标组织未来行动序列、子目标和约束，并在必要时根据状态或反馈调整行动的过程。它可以由语言推理表现出来，也可以由显式的状态表示、搜索或 Planner 组件实现。

LLM+P 提供了当前知识库中的一个更强边界案例：LLM 负责把自然语言问题翻译成 PDDL problem，独立的 classical planner 负责在形式化状态、动作和目标上搜索计划。因此，planning 不应仅由是否出现语言化 Thought 来定义。

## Evidence Boundary

当前资料能支持几种不同强度的 planning 证据：

- ReAct 支持 plan-like reasoning、task decomposition、动作顺序选择和基于 Observation 的策略修正，但没有独立 Planner。
- Reflexion 可以根据反馈和 reflection 影响下一次 attempt 的策略，但没有定义 Planner–Executor 接口、计划状态或计划验证器。
- LLM+P 具有明确的形式化规划后端：PDDL 表示状态、动作和目标，classical planner 负责搜索；这是 explicit planning 的实例。
- RAP 具有显式的 inference-time search：LLM 预测 imagined state，MCTS 使用 reward 在候选路径间探索；这是 search-based planning，但不等同于真实环境中的在线执行闭环。
- Toolformer 的核心是 API-use policy learning，不提供本 Concept 所需的 planning evidence。

（Source: [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md); [Reflexion paper note](../papers/reflexion/notes.md); [LLM+P paper note](../papers/llm-p/notes.md); [RAP paper note](../papers/rap/notes.md)）

## Why It Matters

长时程 Agent 不能只预测下一步动作，还需要知道当前完成到哪里、下一子目标是什么，以及失败后是否需要重规划。现有资料说明这些能力可以分布在不同组件中：ReAct 让模型在运行时结合 Observation 决定下一步，LLM+P 把结构化搜索交给 solver，后续的 planning 方法还可能引入搜索或 world model。它们不能被压缩为同一种架构。

## Core Mechanism

ReAct 的 Thought 可以：

- 分解高层目标。
- 选择检索或探索顺序。
- 跟踪子目标完成情况。
- 根据 Observation 处理异常并修改计划。

计划信息保存在当前 trajectory context 中，并通过后续 Action 实现；论文没有单独搜索、评分或验证计划的 Planner 算法。LLM+P 则把 domain/problem PDDL 和 classical planner 作为显式的计划表示与求解层，计划结果在交给执行器前已经由 solver 组织出来。（Source: [LLM+P paper note](../papers/llm-p/notes.md), Sec. II–III）

RAP 则把 planning 表达为对多个候选 state/action 分支的 inference-time 搜索：world model 预测 next state，reward 提供分支评价，MCTS 负责 exploration、simulation 和 backpropagation。它的计划节点是模型模拟出来的 imagined state，不能直接当成真实环境 Observation。（Source: [RAP paper note](../papers/rap/notes.md), Sec. 3.1–3.3）

## Typical Architecture

```text
Goal → Language Plan / Subgoals → Action → Observation
       ↑                         ↓
       └────── revise / track ───┘
```

## Example

在显式符号规划中，可以使用另一种结构：

~~~text
Natural-language task
→ Problem representation
→ Explicit planner / solver
→ Plan
→ Executor
~~~

这表示 explicit planner 的存在，但不自动说明系统具备持续感知、跨 attempt memory 或完整 Agent architecture。

在 search-based planning 中，可以进一步出现：

~~~text
State
→ Candidate Actions
→ World Model / Simulator
→ Search and Reward
→ Selected Plan or Next Action
→ Execute and Observe when an environment exists
~~~

搜索是实现 planning 的一种方式，但 planning 不必然要求 MCTS 或穷举搜索；LLM+P 的 classical planner、RAP 的 MCTS 和 ReAct 的 runtime decision loop 具有不同的状态与反馈来源。

例如在“把处理好的物体放到指定位置”的长时程任务中，ReAct Thought 可以先规划“找到并拿取物体 → 完成处理 → 放置”，再在每个子目标完成后决定下一步。只保留 Action 的模型更容易丢失子目标顺序并陷入重复。

## Related Concepts

- [Agent](agent.md)
- [Reasoning](reasoning.md)
- [Tool Use](tool-use.md)
- [Memory](memory.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 展示语言化的目标分解、子目标跟踪和动态调整。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — reflection 可以跨 attempt 提议不同的动作顺序或策略，但论文没有定义独立的 Planner architecture。（Source: Sec. 3; Appendix B）
- [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../papers/llm-p/notes.md) — 以 PDDL 与 classical planner 展示 solver-backed explicit planning。（Source: Sec. II–III）
- [RAP: Reasoning with Language Model is Planning with World Model](../papers/rap/notes.md) — 以 prompting 的 world model、reward 和 MCTS 展示 search-based inference-time planning。（Source: Sec. 3; Appendix A）

## Representative Systems / Code

## Advantages

- 计划与具体 Observation 相连，可以边执行边修正。
- 在 ReAct 的 prompt 范式中，可以不新增独立规划器接口就表达任务计划。
- 计划本身可读，便于人类检查和修改。

## Limitations

- 语言 Thought 中出现计划，不等于计划一定稳定、可执行或被模型忠实遵循。
- LLM+P 的显式 planner 也不消除自然语言到 PDDL 翻译错误；形式化 solver 的保证依赖输入表示正确。
- RAP 的搜索结果也不自动等于可靠计划；world model 的 imagined-state 错误和 reward 偏差会被搜索结构放大。
- 长轨迹会受到 context length、重复循环和错误 Observation 的影响。
- 如果只看最终任务成功率，很难把 planning quality 与 reasoning、tool use 和执行质量完全分离。

## My Understanding

ReAct 把 planning 变成一种由 LLM 生成、由环境反馈约束的过程。它证明了“在轨迹中说出下一步计划”有用，但没有证明这已经构成了形式化规划；更准确地说，这是 language-mediated, feedback-driven planning behavior。LLM+P 则说明，当计划具有显式状态、动作、目标和 solver 时，planning 可以从语言 reasoning 中解耦出来；RAP 进一步说明，world model 和 search 可以在没有真实执行的情况下支持候选未来比较。三者的 planning evidence 强度和反馈来源不同，不能归并为一种方法。

## Open Questions

- 如何区分计划质量、推理质量和动作执行质量？
- 什么时候应重新规划，什么时候只需重试或改写工具调用？
- 能否把自然语言子目标编译成可验证的计划状态？
- 哪些显式 Planner / Planner–Executor 机制能在长时程任务中稳定优于 plan-like language behavior？
- 当外部环境在执行中改变时，PDDL solver 产生的静态计划应如何与 Observation 和 replanning 结合？
- explicit planning 的最低要求是形式化状态/动作/目标，还是也需要独立的搜索或验证机制？
- 语言模型预测的 imagined state 何时足以支持 search-based planning，何时必须由真实 Observation 或 symbolic simulator 校验？
- planning 是否一定需要 search，还是可以由可验证的单一路径计划生成与执行组成？
