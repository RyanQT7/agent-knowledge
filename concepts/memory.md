Status: evolving

# Memory

## Definition

Memory 是保存信息，并在后续步骤、任务或 episode 中按需获取和使用的机制。ReAct 提供的是历史信息留在当前 context 中的短期机制；将其称为 working-memory-like behavior 是本知识库的解释，不是论文提出的独立 Memory 架构。

## Why It Matters

Agent 需要记住已经观察到的事实、已完成的子目标和当前计划，否则长轨迹中的动作会失去上下文。ReAct 通过 trajectory context 和 Thought 把这些信息显式放回下一轮模型输入。

## Core Mechanism

ReAct 的当前上下文包含历史 Observation、Action 和 Thought；Thought 还可以把进度、计划和异常转成语言，帮助模型在后续步骤中继续使用。论文没有定义跨 episode 存储、检索、压缩或长期更新机制。

## Typical Architecture

```text
History: Thought / Action / Observation
→ Current Context
→ Next Thought / Action
```

这是一种上下文内的短期 working-context / working-memory-like behavior，不应直接等同于 persistent memory 或独立的 memory retrieval 模块。

## Example

在多步环境任务中，Thought “已经找到并拿到物体，下一步完成处理”可以帮助模型保留子目标状态；在多跳知识任务中，历史查询 Observation 可以支持后续证据链。

## Related Concepts

- [Agent](agent.md)
- [Context Engineering](context-engineering.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 将 trajectory context 与 language thought 用作任务内工作记忆。

## Representative Systems / Code

## Advantages

- 信息沿当前轨迹保留，便于连续推理和子目标跟踪。
- Thought 能把隐式进度转成可读的上下文内容。

## Limitations

- context 会随轨迹增长，可能受到输入长度和噪声影响。
- 没有跨任务持久化、自动检索、遗忘或冲突解决机制。
- 历史 Thought 可能本身错误，因此“记住”不等于“记住了正确状态”。

## My Understanding

ReAct 让我看到 memory 的一个最小形态：只要历史 Thought、Action 和 Observation 持续进入 context，LLM 就能在单个任务内获得工作记忆。但这只是 context-based memory；长期 Agent 还需要解决保存什么、何时检索、如何更新以及错误记忆如何纠正。

## Open Questions

- ReAct trajectory 应如何压缩，才能支持更长的任务？
- Thought、Observation 和外部检索结果应如何分别存储和信任？
- 如何从 task-time context 过渡到安全的 persistent memory？
