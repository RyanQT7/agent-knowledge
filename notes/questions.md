# Open Questions

记录学习过程中尚未解决、需要验证或值得进一步研究的问题。

## From the ReAct reading

### 论文明确暴露或留下的问题

- ReAct 的重复 thought/action 循环是否主要来自 greedy decoding、prompt 结构，还是状态表示不足？（Source: Sec. 3.3）
- 如何在非信息性 Search 结果之后有效改写查询并恢复推理？（Source: Sec. 3.3）
- 更多高质量人工轨迹、multi-task training 和 reinforcement learning 能否改善长时程、大 action space 任务？（Source: Sec. 6）

### 本次阅读进一步产生的问题

- ReAct 是否真正具有 planning，还是只表现出计划性的语言行为？
- Reasoning trace 是否等价于 Agent 的 internal state？
- ReAct 的文本 Action 如何演化为现代 structured tool calling / MCP 接口？
- ReAct trajectory 中的历史信息与现代 Agent memory 有什么区别？
- 错误、冲突或过时的 Observation 如何影响后续 Agent trajectory？

关联笔记：[ReAct 论文笔记](../papers/react/notes.md#14-questions)。

### Tool Use 相关问题的状态补充

- 对“ReAct 的文本 Action 如何演化为现代 structured tool calling / MCP 接口？”：**部分回答**。Toolformer 证明了模型可以通过自监督方式学习文本 API 的调用时机、工具名和参数，并在生成中插入文本结果；但它没有给出 schema、权限、错误处理或 MCP 映射方案。因此“能否迁移到现代接口”仍未解决。
- 对“ReAct trajectory 中的历史信息与现代 Agent memory 有什么区别？”：**仍未解决**。Toolformer 的 API result 是当前 token context 的一部分，也没有 persistent / long-term memory。
- 对“错误、冲突或过时的 Observation 如何影响后续 Agent trajectory？”：**仍未解决**。Toolformer 的论文没有系统研究错误或恶意工具返回值的识别与恢复。

## From the Toolformer reading

### 已由论文部分回答的问题

- 模型可以通过 self-supervised future-token loss filtering 学习“何时调用哪个工具、传入什么参数”，但这个训练信号衡量的是对后续文本的预测帮助，不等于普遍的任务正确性或安全性。（Source: Sec. 2）
- Toolformer 的调用表示和结果注入是文本化的：`<API> name(input) ! result </API>`，实际使用 `[`, `]`, `->` token 序列；这回答了一个具体表示方式，但没有回答现代 structured tool calling / MCP 应如何实现。（Source: Sec. 2 and footnote 1）
- ReAct 与 Toolformer 都涉及外部工具，但 ReAct 以运行时 Thought/Action/Observation 闭环为核心，Toolformer 以自监督微调获得的 API token-generation policy 为核心；它们不应被视作同一种 Agent 架构。（Source: ReAct note; Toolformer Sec. 2, Sec. 5–6）
- Toolformer 在论文中被定位为 LM；它具有模型驱动的 API 选择，但没有足够证据证明其具有完整 Agent 所需的显式 Planner、持久化 Memory 或多步 Environment runtime。（Source: Abstract; Sec. 2; Sec. 7）

### 论文明确留下的问题

- 如何通过迭代式数据增强学习可靠的 chained tool use？（Source: Sec. 6）
- 如何让模型交互式浏览搜索结果、改写 query 并根据中间结果继续调用？（Source: Sec. 6）
- 如何提高 calculator 等工具的调用样本效率，并把工具计算成本纳入调用决策？（Source: Sec. 6）

### 基于两篇论文进一步产生的问题

- loss-based filtering 与真实任务 utility、事实 grounding 和 calibration 的关系是什么？
- Toolformer 学到的调用策略能否迁移到训练增强语料中未出现的新 API？
- Toolformer 的 inline API result 与 ReAct 的 Observation trajectory 能否组合成稳定的多步交互 Agent？

关联笔记：[Toolformer 论文笔记](../papers/toolformer/notes.md#14-questions)。
