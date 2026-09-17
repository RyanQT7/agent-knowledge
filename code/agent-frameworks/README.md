# Agent Framework Source Learning

这些文档来自对指定开源 Agent framework / SDK / runtime 的只读静态源码分析。外部源码保存在被 `.gitignore` 忽略的 `sources/code/agent-frameworks/`，知识库只保留固定 commit、源码路径和实现理解。

## Framework Notes

- [smolagents](smolagents.md) — 小型、多步、ToolCallingAgent 与 CodeAgent。
- [LangGraph ReAct](langgraph-react-agent.md) — 用 StateGraph 表达 ReAct 循环。
- [OpenAI Agents SDK](openai-agents-sdk.md) — Agent、Runner、Tool、Handoff、Guardrail、Session 与 Tracing。
- [Microsoft Agent Framework](microsoft-agent-framework.md) — Agent、Provider、Workflow、Executor、Checkpoint 与 MCP。
- [横向比较](comparison.md)

## Reading Boundary

当前内容是 source-backed static analysis，不代表已运行这些项目或完成 reproduction。每份笔记记录了读到的 commit；如果源码更新，应重新固定版本并复核对应结论。
