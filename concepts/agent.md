Status: evolving

# Agent

## Definition

Agent 是根据任务上下文接收 Observation、选择 Action 并与 environment 交互以完成目标的系统。ReAct 增加的一个重要视角是：language thought 可以作为增强 action space 中的显式语言动作；它不改变环境，但会更新后续决策所使用的 context。

## Why It Matters

ReAct 使 Agent 的基本闭环变得清晰：外部 Action 取得或改变环境状态，Observation 反馈给模型，Thought 在上下文中解释当前状态并决定下一步。Agent 不只是一次性生成答案，而是在轨迹中持续决策。

## Core Mechanism

ReAct 用 `\hat{A} = A ∪ L` 扩展动作空间，其中 `A` 是环境动作，`L` 是语言空间。环境动作产生 Observation；语言 thought 不产生环境反馈，但追加到 trajectory context 中。

## Typical Architecture

```text
Task / Observation → Thought → Action → Observation → ... → Finish
```

论文没有把 Planner、Executor 和 Memory 实现为独立模块；这些功能主要由 LLM、trajectory context 和环境接口共同承担。

## Example

在需要外部证据的任务中，Agent 可以先用 Thought 分解查询，再调用工具，根据 Observation 修正查询并最终结束。在长时程环境任务中，Agent 也可以用 Thought 跟踪“找到物体 → 拿取 → 处理 → 放置”等子目标。

## Related Concepts

- [Reasoning](reasoning.md)
- [Tool Use](tool-use.md)
- [Planning](planning.md)
- [Memory](memory.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 将 reasoning trace 与外部 action 交错放入 Agent 闭环。

## Representative Systems / Code

## Advantages

- 可以在行动前显式组织目标和子目标。
- 可以通过外部 Observation 获取内部知识之外的信息。
- 轨迹便于人检查、诊断和在线干预。

## Limitations

- Agent 的行为仍依赖模型、prompt、action space 和 Observation 的质量。
- 如果规划、状态记录和执行都依赖同一个上下文，语言 thought 可能循环或 hallucinate；不应假定它自动保证计划、状态或事实正确。
- ReAct 的示范没有提供持久化 Memory、通用工具权限或执行错误处理机制；这些是更完整 Agent 系统仍需补足的边界。

## My Understanding

ReAct 让我把 Agent 理解为一个闭环 policy，而不是“带有一个 prompt 的 LLM”。Thought 是用于组织 context 的显式语言动作，Action 是与外部世界交换信息或改变状态的动作；两者交替才形成 Agent 的任务执行能力。

## Open Questions

- 如何分别测量 Agent 的 reasoning、planning、tool use 和 environment recovery 能力？
- Thought 是否是可控的内部状态接口，还是仅仅是生成出来的语言轨迹？
