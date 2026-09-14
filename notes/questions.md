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
