Status: evolving

# Reflection

## Definition

Reflection 是在一次输出或 trajectory 被评估之后，生成对错误、原因和下一步修正的语言反馈，并把反馈提供给后续生成的机制。它首先改变后续 inference 的 context，不等于模型参数更新，也不自动等于模型真实的 hidden internal state。

## Why It Matters

成功 / 失败或稀疏 reward 只告诉 Agent 结果，通常没有直接说明下一次应该改变哪一步。Reflection 尝试把结果转换成可执行的经验，使 Agent 能在有限的连续尝试中进行 credit assignment、错误恢复和策略调整。

## Core Mechanism

通用抽象是：

~~~text
Attempt / Trajectory
→ Evaluator / Task Feedback
→ Verbal Reflection
→ Context or Episodic Memory
→ Next Attempt
~~~

Reflection 的质量取决于三件事：Evaluator 是否识别了真正的问题，生成的反馈是否包含可操作的修正，以及下一次 Actor 是否在合适的位置读取并遵循该反馈。Reflexion 将 reflection 作为 Self-Reflection model 的输出，并把它追加到受限的 task memory 中。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3）

## Typical Architecture

~~~text
Actor → Trajectory → Evaluator
  ↑                     ↓
  └── Episodic Memory ← Reflection
~~~

Evaluator 可以是 exact-match、规则、测试程序、另一个 LLM，或其他外部反馈接口；Reflection 也可以由外部 feedback 或内部模拟 feedback 产生。Reflection layer 可以包裹 ReAct 等单次执行范式，但不是所有 Agent 都必须有独立的 reflection 模块。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3.1; Sec. 4）

## Example

在 Reflexion 的 decision-making 例子中，第一次 trajectory 因错误的动作顺序失败；reflection 指出应先寻找 lamp，再处理 mug；下一次 Actor 读取该经验并按不同顺序行动，最终成功。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Appendix B, Fig. 5）

## Related Concepts

- [Agent](agent.md)
- [Reasoning](reasoning.md)
- [Memory](memory.md)
- [Planning](planning.md)
- [Tool Use](tool-use.md)

## Representative Papers

- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — 将 evaluator feedback 转化为语言化 episodic experience，并用于下一次尝试。

## Representative Systems / Code

## Advantages

- 比单一的 success / failure 标签包含更多可执行信息。
- 可以在不更新模型权重的情况下影响后续尝试。
- 反馈文本便于检查错误归因、修正建议和 Agent 的诊断过程。
- 可与 ReAct、CoT 或工具执行器组合，而不必把 reflection 与某一种 Actor 范式绑定。

## Limitations

- 错误的 evaluator 或错误的 self-reflection 可能把 Agent 引向错误方向。
- 语言反馈不保证 faithful 地描述模型真正的内部过程。
- memory 容量、context length 和压缩方式会决定经验能否被保留。
- 当前一次尝试的改进不等于参数层面的永久学习，也不自动产生跨任务或跨会话的 persistent memory。

## My Understanding

Reflection 是连接“已经发生的行为”和“下一次应该如何改变”的中间层。它不是把模型内部状态读出来，而是由模型或系统显式生成一段新的语言条件；因此更准确的说法是 verbal feedback、episodic adaptation 或 context-level self-correction。Reflexion 的贡献在于把这层反馈接入 evaluator、memory 和 next-attempt loop，并在多个任务中验证其可用性。

## Open Questions

- 如何判定 reflection 的错误归因是否正确，而不只看下一次是否成功？
- Reflection 与 critic、self-correction、verbal reinforcement 的边界应如何定义？
- 如何压缩和检索大量 reflection，避免旧经验、错误经验或重复经验污染后续 context？
- 什么样的任务反馈最适合生成稳定、可迁移的 reflection？
