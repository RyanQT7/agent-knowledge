Status: evolving

# Context Engineering

## Definition

Context Engineering 是围绕模型上下文的选择、组织、分阶段注入、压缩和更新来支持任务执行的方法。它关注的不只是 prompt 文案，还包括哪些历史、工具结果、计划和状态在什么时间进入哪个模型模块。

## Why It Matters

LLM 的行为受输入上下文中的任务、示例、历史轨迹和外部结果共同影响。上下文重复会带来 token、延迟和成本；上下文缺失或混杂又会使模型无法利用关键状态。ReAct、Toolformer 和 ReWOO 说明，context 的组织方式本身会改变 reasoning、tool use 和系统效率。

## Core Mechanism

一个可分析的 context engineering 问题至少包含：

- 选择：保留哪些 task、state、trajectory、tool result 和 memory。
- 编排：以什么顺序、格式和模块边界提供给模型。
- 时机：哪些信息在 reasoning、tool execution、reflection 或 solving 前可见。
- 压缩：如何减少重复历史，同时保留对决策有用的证据。
- 更新：新 Observation、feedback 或 plan revision 如何替换、追加或校验旧内容。

ReWOO 是一个清晰例子：Planner 只看任务、工具说明和示例生成 blueprint，Worker 产生 evidence，Solver 再读取 plans 与 evidence；通过把 foreseeable reasoning 与 observation 分阶段组织，减少 ReAct 式重复上下文。（Source: [ReWOO paper note](../papers/rewoo/notes.md); Sec. 2.1–2.2）

## Typical Architecture

~~~text
Task / State / Memory
→ Context selection and formatting
→ Module-specific prompt
→ Model reasoning or action
→ Tool result / Observation / Feedback
→ Context update, compression, or handoff
~~~

不同模块不一定共享完全相同的 context。ReWOO 的 Planner、Worker 和 Solver 就是按职责分开读取计划、工具输入和 evidence。

## Example

ReAct 把每轮 Thought、Action 和 Observation 追加到 trajectory context 中，便于运行时 grounding，但会重复历史。ReWOO 把计划提前写出，把 evidence 延迟到 Solver，降低重复；代价是 Planner 在生成 blueprint 时看不到后续工具结果，不能自然地按每个 Observation 改写计划。（Source: [ReAct paper note](../papers/react/notes.md); [ReWOO paper note](../papers/rewoo/notes.md)）

## Related Concepts

- [Agent](agent.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)
- [Tool Use](tool-use.md)
- [Memory](memory.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 运行时把 Thought、Action 和 Observation 组织成 trajectory context。
- [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](../papers/rewoo/notes.md) — 通过 Planner–Worker–Solver 分阶段组织 plans、tool evidence 和 solving context。

## Representative Systems / Code

## Advantages

- 让不同模块只接收与职责相关的信息。
- 降低重复 prompt、历史 trajectory 和工具结果带来的 token 成本。
- 通过格式、顺序和模块边界提高信息可读性与可诊断性。

## Limitations

- 压缩或提前规划可能丢失需要实时 Observation 才能决定的信息。
- 结果进入 context 不等于已经验证；错误、冲突和过时 evidence 仍可能污染后续生成。
- context 的 token 优化可能与 grounding、可解释性、完整历史和恢复能力发生 trade-off。
- 当前资料不足以给出通用的 context compression、provenance 或跨会话持久化方案。

## My Understanding

Context engineering 是 Agent 的信息流设计层。它决定模型在某一步能看到什么、哪些信息被延迟、哪些历史被压缩，以及不同模块如何交接。ReWOO 说明减少观察依赖和重复 token 可以提升效率，但也暴露出 plan-first 方法在动态、观察依赖任务中的边界。

## Open Questions

- 如何在不丢失关键状态和证据的情况下压缩长 trajectory？
- 什么时候应该把信息保留在当前 context，什么时候写入 episodic / persistent memory？
- 如何为 tool result、reflection 和 plan 建立 provenance、可信度和冲突处理？
- Planner 看不到未来 Observation 时，如何自动判断哪些 reasoning 足够 foreseeable？
