Status: evolving

# Planning

## Definition

Planning 是将目标分解为步骤或子目标、安排执行顺序，并在新信息出现时调整路径的过程。ReAct 把这种 planning 主要表达为语言 Thought，而不是独立的规划器。

## Evidence Boundary

当前资料能支持的是 plan-like reasoning、task decomposition、动作顺序选择和基于反馈的策略修正。ReAct 没有独立 Planner；Reflexion 的 reflection 可以提出下一次不同的动作顺序或策略，但也没有定义 Planner–Executor 接口、计划状态或计划验证器。Toolformer 的核心是 API-use policy learning，不提供本 Concept 所需的 planning evidence。（Source: [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md); [Reflexion paper note](../papers/reflexion/notes.md)）

## Why It Matters

长时程 Agent 不能只预测下一步动作，还需要知道当前完成到哪里、下一子目标是什么，以及失败后是否需要重规划。ReAct 的交互任务实验显示，稀疏但有针对性的计划性 Thought 可能改善动作执行。

## Core Mechanism

ReAct 的 Thought 可以：

- 分解高层目标。
- 选择检索或探索顺序。
- 跟踪子目标完成情况。
- 根据 Observation 处理异常并修改计划。

计划信息保存在当前 trajectory context 中，并通过后续 Action 实现；论文没有单独搜索、评分或验证计划的 Planner 算法。

## Typical Architecture

```text
Goal → Language Plan / Subgoals → Action → Observation
       ↑                         ↓
       └────── revise / track ───┘
```

## Example

例如在“把处理好的物体放到指定位置”的长时程任务中，ReAct Thought 可以先规划“找到并拿取物体 → 完成处理 → 放置”，再在每个子目标完成后决定下一步。只保留 Action 的模型更容易丢失子目标顺序并陷入重复。

## Related Concepts

- [Agent](agent.md)
- [Reasoning](reasoning.md)
- [Tool Use](tool-use.md)
- [Memory](memory.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 展示语言化的目标分解、子目标跟踪和动态调整。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — reflection 可以跨 attempt 提议不同的动作顺序或策略，但论文没有定义独立的 Planner architecture。（Source: Sec. 3; Appendix B）

## Representative Systems / Code

## Advantages

- 计划与具体 Observation 相连，可以边执行边修正。
- 在 ReAct 的 prompt 范式中，可以不新增独立规划器接口就表达任务计划。
- 计划本身可读，便于人类检查和修改。

## Limitations

- 语言 Thought 中出现计划，不等于计划一定稳定、可执行或被模型忠实遵循。
- 长轨迹会受到 context length、重复循环和错误 Observation 的影响。
- 如果只看最终任务成功率，很难把 planning quality 与 reasoning、tool use 和执行质量完全分离。

## My Understanding

ReAct 把 planning 变成一种由 LLM 生成、由环境反馈约束的过程。它证明了“在轨迹中说出下一步计划”有用，但没有证明这已经构成了形式化规划；更准确地说，这是 language-mediated, feedback-driven planning behavior。

## Open Questions

- 如何区分计划质量、推理质量和动作执行质量？
- 什么时候应重新规划，什么时候只需重试或改写工具调用？
- 能否把自然语言子目标编译成可验证的计划状态？
- 哪些显式 Planner / Planner–Executor 机制能在长时程任务中稳定优于 plan-like language behavior？
