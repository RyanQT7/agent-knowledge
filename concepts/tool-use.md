Status: evolving

# Tool Use

## Definition

Tool Use 是模型向外部能力发出任务相关请求，并利用返回结果继续完成任务的机制。ReAct 展示了一个文本化、由语言模型主动选择查询时机和参数的 tool-use 闭环。

## Why It Matters

工具让模型能够取得内部参数中没有、过时或需要验证的信息，也让 Agent 能够改变环境。ReAct 强调工具调用不是任务末尾的附加步骤，而可以被 reasoning 持续规划和纠正。

## Core Mechanism

```text
Thought → Action(tool/API) → Observation → Thought
```

ReAct 中的工具 Action 可以是查询、定位信息或结束任务；Action 的结果被追加到上下文，下一轮 LLM 再决定继续查询、改写查询还是结束。关键不在具体命令名称，而在于“调用—观察—再决定”的循环。

## Typical Architecture

```text
LLM Policy → Text Action → Tool / Environment → Observation → LLM Context
```

论文中的 Action 主要是 prompt 中的文本格式，不是现代 API function-calling schema；工具执行和模型生成之间由实验环境连接。

## Example

当任务需要外部证据时，ReAct 先用 Thought 分解检索目标，调用工具，发现结果不足后改写或细化查询，最后结合多条 Observation 输出答案。

## Related Concepts

- [Agent](agent.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)
- [RAG](rag.md)
- [MCP](mcp.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 让 reasoning 指导工具动作，并让工具 Observation 参与后续 reasoning。

## Representative Systems / Code

## Advantages

- 可主动获取外部事实并减少纯内部知识的幻觉。
- 查询目标由 reasoning 指定，能够根据反馈改写。
- 同一模式可用于知识库、文本环境和网页交互。

## Limitations

- 工具能力和返回质量受 task-specific action space 限制；ReAct 的实验说明，一个简单文本 API 足以验证闭环，但不能代表强检索器或通用工具系统。
- Search 可能为空或无信息，模型也可能无法从错误中恢复。
- 文本 Action 没有展示 schema 验证、权限、参数类型和通用执行错误处理。
- 连接真实外部环境会带来隐私和有害行动风险。

## My Understanding

ReAct 把 Tool Use 变成“查询—观察—再推理”的循环。工具是否有用，不只取决于调用能力，还取决于模型是否能从目标推导出合适的查询、理解 Observation，并在失败时重新规划。

## Open Questions

- 如何让工具接口既保持语言灵活性，又具有结构化校验和安全边界？
- 工具返回冲突、过时或恶意信息时，Agent 应如何判断其可信度？
- ReAct 的文本 Action 如何系统地迁移到现代 tool calling / MCP？
