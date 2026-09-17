Status: evolving

# Memory

## Definition

Memory 是保存信息，并在后续步骤、任务或 episode 中按需获取和使用的机制。分析 Agent memory 时，需要区分当前 trajectory 的 working context、跨尝试保留的 episodic memory，以及由外部存储保证的 persistent / durable long-term memory。

## Why It Matters

Agent 需要记住已经观察到的事实、已完成的子目标、失败原因和可复用经验，否则长轨迹或多次尝试会反复犯同一个错误。Memory 的价值不只在“保存”，还在于决定保存什么、何时读取、如何压缩、如何处理错误和冲突。

## Core Mechanism

### Working context / short-term memory

当前 trajectory 中的 Thought、Action、Observation 和状态历史会被放入下一轮模型输入。它支撑单个 trial 内的连续推理和动作选择。ReAct 主要展示了这种 context-based memory；将其称为 working-memory-like behavior 是分析性说法，不是一个独立的持久化 Memory 模块。（Source: [ReAct paper note](../papers/react/notes.md)）

### Episodic memory

一次 attempt 结束后，系统可以把 trajectory 和 feedback 总结成经验，并在后续 attempt 中读取。Reflexion 的 Self-Reflection 就是这种跨 trial 的语言化 episodic memory：保存的是 reflection summary，而不是要求完整保存所有原始 trajectory。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3.1）

### External structured working memory

StepFly provides a narrower memory boundary: its metric/log plugins write typed values such as lists, dictionaries, DataFrames, or ndarrays to a key-value store, and later steps retrieve them by key. This is external structured working memory for one TSG execution; the paper does not establish cross-incident episodic learning, memory selection, forgetting, or long-term Agent adaptation (Source: [StepFly paper note](../papers/aiops/stepfly/notes.md), Sec. 4.4.4).

TSGen shows a different durable-storage boundary: historical incident records, clustering caches, and generated TSG/DAG artifacts persist so that operational knowledge can be generated, retrieved, and updated. They are useful knowledge infrastructure, but the paper does not define a runtime Agent memory read/write policy, episodic attempt memory, forgetting mechanism, or cross-task memory semantics (Source: [TSGen paper note](../papers/aiops/tsgen/notes.md), Sec. 4.1–4.5, Sec. 7.2).

ChatRCA retrieves historical incident cases and postmortems through a RAG skill, while AutoGen shares the current GroupChat context. This is external operational knowledge plus working context: the paper does not define automatic episodic write-back, forgetting, stale-case retirement, or a persistent Agent memory policy across incidents (Source: [ChatRCA paper note](../papers/aiops/chatrca/notes.md), Sec. 4.2, Sec. 5.2).

### Persistent / durable long-term memory

如果 memory 跨任务、跨会话保存，并由文件、数据库或其他外部存储保证其生命周期，才更接近 persistent / durable long-term memory。Reflexion 论文使用 long-term memory 描述 self-reflections，但其实际实现是 task-local、bounded 的跨 attempt memory；论文没有证明跨会话持久化系统。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3.1; Sec. 5）

跨领域模型中的“memory”需要单独标注语义。StaR 的 per-variable persistent temporal state 是时序/图模型为预测和因果重构保存的隐状态，不是 Agent 读取的自然语言 episodic memory，也不自动构成外部 persistent memory architecture。（Source: [StaR paper note](../papers/aiops/star/notes.md); Sec. 3.3）

## Typical Architecture

~~~text
Current trajectory
  Thought / Action / Observation
        ↓
  Working context
        ↓
Evaluator feedback → Reflection summary
                              ↓
                     Episodic memory window
                              ↓
                    Next attempt / Actor context
~~~

更完整的长期系统还需要外部存储、检索、更新、压缩、过期和冲突处理；这些不应从 ReAct 或 Reflexion 自动推断出来。

## Example

- ReAct：历史 Thought、Action 和 Observation 持续留在当前 context 中，帮助 Agent 跟踪子目标和证据链。
- Reflexion：Evaluator 判断一次 trajectory 失败，Self-Reflection 总结错误动作或答案范围，下一次 Actor 读取该 summary 并尝试不同策略；论文的不同任务都使用有容量上限的 memory window。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 4.1–4.3）

## Related Concepts

- [Agent](agent.md)
- [Context Engineering](context-engineering.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)
- [Reflection](reflection.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 展示当前 trajectory context 作为任务内 working context。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — 展示把 verbal reflection 保存为受限的跨 attempt episodic memory。
- [StepFly: Agentic Troubleshooting Guide Automation for Incident Diagnosis](../papers/aiops/stepfly/notes.md) — 展示外部 key-value structured working memory 在工具之间传递大数据 payload，而不是跨事件经验学习。
- [TSGen: Automated Troubleshooting Guide Generation](../papers/aiops/tsgen/notes.md) — 展示把历史事件持久化为可更新的 operational knowledge；不应把 TSG/缓存自动称为 Agent episodic memory。
- [ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop](../papers/aiops/chatrca/notes.md) — 展示 RAG 历史案例和共享会话 context 支持 RCA；不等于完整 Agent memory。

## Representative Systems / Code

## Advantages

- Working context 能支持单条 trajectory 内的连续推理和状态跟踪。
- Episodic reflection 能把一次失败转成下一次可读取的经验，而不必立即更新模型参数。
- 显式语言 memory 便于检查内容、来源和错误归因。

## Limitations

- context 和 memory window 受输入长度、噪声和容量上限影响。
- 历史 Thought、Observation 或 reflection 可能错误；保存信息不等于保存了正确状态。
- bounded task memory 不提供跨任务持久化、自动检索、遗忘或冲突解决。
- 过度保存原始 trajectory 会增加噪声，过度压缩又可能丢失错误发生的关键证据。

## Common Confusions

- 当前 context 或 trajectory history 只有在后续阶段被专门保留和读取时，才可称为跨 attempt memory；它不自动是 long-term memory。
- Reflexion 的 long-term memory 是受限的 task-local episodic memory，不等于跨任务、跨会话的 durable memory architecture。
- Environment state、context、episodic memory 和 hidden internal state 是不同对象；Action 改变环境不等于模型“记住”了改变。
- 保存 reflection summary 不保证错误归因正确，也不代表原始 trajectory 的全部证据仍然可恢复。

## My Understanding

ReAct 展示 memory 的最小形态：历史信息只要持续进入 context，就能形成单任务内的 working context。Reflexion 在其上增加了一个跨 attempt 的 episodic layer：保存的是由反馈产生的语言经验，并在下一次 Actor generation 时读取。它让“从失败中学习”成为 context-level adaptation，但不应被称为已经解决了 persistent long-term memory。

## Open Questions

- 如何在不丢失关键因果信息的情况下压缩长 trajectory 和 reflection？
- 应该优先保存原始 trajectory、错误摘要、可验证事实，还是它们的组合？
- 如何检测和纠正错误、冲突、过时或被污染的 memory？
- task-local episodic memory 如何安全扩展到跨任务、跨会话的 persistent memory？

## Framework Code Boundary

四个源码项目进一步说明了几种容易混淆的对象：

- smolagents 的 `AgentMemory.steps` 是结构化任务轨迹，并由 `to_messages()` 重新放入模型 context。
- LangGraph ReAct 的 `State.messages` 是图运行状态；当前小仓库没有观察到独立语义 memory store。
- OpenAI Agents SDK 的 `Session`/`SQLiteSession` 可以保存 conversation history；持久化 history 不自动等于语义 memory。
- Microsoft Agent Framework 的 `AgentSession`、ContextProvider 和 Workflow checkpoint 可以持久化不同类型的控制/上下文状态，但仍需应用定义 retrieval、selection、compression 和 forgetting。

因此，源码中的 `memory`、`session`、`state`、`checkpoint` 不能只按名字归为同一个 Memory 概念。参见 [framework comparison](../code/agent-frameworks/comparison.md)。
