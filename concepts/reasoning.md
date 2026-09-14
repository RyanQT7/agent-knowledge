Status: evolving

# Reasoning

## Definition

Reasoning 是从当前信息、目标和约束出发形成中间推导，以支持结论或行动的过程。ReAct 关注的是可与外部 Action 交错的 language reasoning trace。LLM+P 则展示了另一种分工：语言模型负责把自然语言任务转换为 PDDL，后续的状态转移和计划搜索由 classical planner 处理。（Source: [LLM+P paper note](../papers/llm-p/notes.md); Sec. II–III）

Reflexion 增加了 trajectory 之后的语言 feedback：模型或系统根据 Evaluator 的结果生成对错误和修正方向的解释，再作为下一次 reasoning 的 context。这个显式 feedback 不是模型隐藏 internal state 的直接读出。

## Distinctions

当前三篇论文支持的边界可以这样记录：

| 对象 | 面向的时间尺度 | 主要作用 |
| --- | --- | --- |
| Reasoning trace / Thought | 当前 step 或当前 attempt | 解释 context、处理 Observation、分解任务并决定下一步。 |
| Planning | 多个 step 的组织 | 安排子目标、顺序和重规划；既可能表现为 plan-like reasoning，也可能由显式表示和 solver 组织。 |
| Reflection | 当前 attempt 结束后、下一次 attempt 之前 | 根据 Evaluator feedback 归纳错误和修正建议。 |
| Internal model state | 模型内部 | 不能从上述任一段语言文本直接等同推断。 |

Reasoning 与 reflection 都可能是语言生成，但前者主要服务当前 trajectory 的推进，后者主要服务下一次 trajectory 的条件更新。（Source: [ReAct paper note](../papers/react/notes.md); [Reflexion paper note](../papers/reflexion/notes.md)）

## Why It Matters

如果 reasoning 能产生新的查询目标、解释 Observation 并修正下一步行动，它就不只是答案前的静态文字，而是 Agent 闭环中的控制信号。ReAct 的结果也说明 grounding 与 reasoning flexibility 之间存在实际 trade-off。

## Core Mechanism

在跨 trial 的层次，Reflexion 让 Evaluator feedback 经由 Self-Reflection 变成可复用的语言经验。它可以提供错误归因、credit assignment 或下一次的修正建议，并通过 episodic memory 改变后续 reasoning；它不通过 gradient 更新模型参数。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3）

ReAct 中的 Thought 可以分解任务、提取观察事实、进行 commonsense / arithmetic reasoning、改写查询、跟踪进度和综合答案。Thought 本身不改变 environment；外部 Action 的 Observation 会反过来约束和更新后续 Thought。

在 LLM+P 中，部分 reasoning 任务被拆成语言到符号表示的翻译，部分计划求解则由外部 classical planner 完成。这个例子说明，文本中的推导、显式计划搜索和模型隐藏状态是不同层次，不能因为它们都支持最终行动就互相等同。（Source: [LLM+P paper note](../papers/llm-p/notes.md); Sec. II.A–III.C）

## Typical Architecture

```text
Context → Thought → External Action → Observation → Updated Context → Thought
```

这是一种 interleaved、grounded reasoning，而不是只在模型内部连续展开的 CoT。

## Example

在需要多跳证据的任务中，模型可以先推断需要搜索的实体，再根据结果决定下一次查询；若结果不足，就改写查询。在长时程环境中，Thought 可以记录子目标完成情况，并决定下一子目标。

## Related Concepts

- [Agent](agent.md)
- [Tool Use](tool-use.md)
- [Planning](planning.md)
- [Memory](memory.md)
- [Reflection](reflection.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 研究 reasoning trace 与 action-observation 交错的效果和代价。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — 研究如何把 trajectory feedback 变成下一次 reasoning 可读取的 verbal experience。
- [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../papers/llm-p/notes.md) — 展示语言翻译与形式化计划搜索之间的解耦。

## Representative Systems / Code

## Advantages

- 外部 Observation 可以减少纯 CoT 的事实幻觉。
- Thought 可以让动作选择、查询改写和高层目标更容易检查。
- 内部知识与外部知识可以通过组合策略互补。

## Limitations

- 交错结构可能降低自由推理能力；ReAct 的实验也观察到 grounding 与 reasoning flexibility 之间的 trade-off。
- Thought 仍可能 hallucinate 或重复生成，不能自动保证 faithful reasoning。
- 无信息的 Observation、错误的工具返回和过长 context 会继续污染推理。
- Reflection 可以帮助后续 reasoning，但其错误归因会被写入 context；Evaluator、reflection prompt 和 memory window 的质量会限制纠错效果。

## My Understanding

ReAct 的关键变化是把 reasoning 放回行动循环：Thought 既是对已有上下文的推导，也是下一次 Action 的条件；Observation 则提供外部校验。它提高的是“可被反馈约束的推理”，不等于证明了自然语言 Thought 就是模型真实内部推理。

Reflexion 让我进一步区分“当前轨迹中的 reasoning”和“轨迹结束后的 reasoning feedback”：前者直接服务于下一步 action，后者服务于下一次 attempt。两者都是语言条件，但都不能直接当成模型真实 internal state。

## Common Confusions

- reasoning trace 是显式语言产物，不是模型 hidden state 的透明窗口。
- 产生了计划性的 Thought 不等于使用了显式 Planner。
- Reflection 不是把 reasoning 再生成一遍；它需要有 trajectory feedback，并以改变后续 attempt 为目标。
- 生成多步动作或子目标只能说明可能存在 plan-like reasoning；是否为 explicit planning 还要检查是否有明确的计划表示、规划过程或独立 Planner / solver。

## Open Questions

- 如何评价一条 reasoning trace 的 faithfulness，而不仅是最终答案是否正确？
- 何时应该 dense reasoning，何时应该 sparse reasoning？
- 如何让 reasoning 在 grounding 与灵活性之间自动切换？
