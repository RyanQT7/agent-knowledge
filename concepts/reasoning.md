Status: evolving

# Reasoning

## Definition

Reasoning 是从当前信息、目标和约束出发形成中间推导，以支持结论或行动的过程。ReAct 关注的是可与外部 Action 交错的 language reasoning trace。

## Why It Matters

如果 reasoning 能产生新的查询目标、解释 Observation 并修正下一步行动，它就不只是答案前的静态文字，而是 Agent 闭环中的控制信号。ReAct 的结果也说明 grounding 与 reasoning flexibility 之间存在实际 trade-off。

## Core Mechanism

ReAct 中的 Thought 可以分解任务、提取观察事实、进行 commonsense / arithmetic reasoning、改写查询、跟踪进度和综合答案。Thought 本身不改变 environment；外部 Action 的 Observation 会反过来约束和更新后续 Thought。

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

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 研究 reasoning trace 与 action-observation 交错的效果和代价。

## Representative Systems / Code

## Advantages

- 外部 Observation 可以减少纯 CoT 的事实幻觉。
- Thought 可以让动作选择、查询改写和高层目标更容易检查。
- 内部知识与外部知识可以通过组合策略互补。

## Limitations

- 交错结构可能降低自由推理能力；ReAct 的实验也观察到 grounding 与 reasoning flexibility 之间的 trade-off。
- Thought 仍可能 hallucinate 或重复生成，不能自动保证 faithful reasoning。
- 无信息的 Observation、错误的工具返回和过长 context 会继续污染推理。

## My Understanding

ReAct 的关键变化是把 reasoning 放回行动循环：Thought 既是对已有上下文的推导，也是下一次 Action 的条件；Observation 则提供外部校验。它提高的是“可被反馈约束的推理”，不等于证明了自然语言 Thought 就是模型真实内部推理。

## Open Questions

- 如何评价一条 reasoning trace 的 faithfulness，而不仅是最终答案是否正确？
- 何时应该 dense reasoning，何时应该 sparse reasoning？
- 如何让 reasoning 在 grounding 与灵活性之间自动切换？
