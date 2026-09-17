---
Status: evolving
---

# Agent Runtime

## Definition

Agent Runtime 是把 Agent 的模型、指令、工具、状态和控制规则变成可执行过程的运行时。它负责调用模型、执行工具、把结果放回上下文、决定继续/转交/暂停/结束，并处理错误、限制和可观测性。

## Why It Matters

只描述“LLM + tools”无法回答：谁执行工具、谁保存状态、何时停止、如何审批副作用操作、失败后是否重试。源码学习显示，Agent 配置对象与 Runtime 可以是同一个对象，也可以由独立 Runner 或 Workflow 负责。

## Core Mechanism

```text
Agent configuration
  + model / instructions / tools
        ↓
Runtime prepares context
        ↓
Model turn
        ↓
Decision: final / tool / handoff / interrupt
        ↓
Runtime executes, validates, records, and continues
```

## Typical Architecture

- smolagents：`MultiStepAgent` 自己拥有主要 loop、`AgentMemory` 和工具执行。
- LangGraph ReAct：Graph state、model node、`ToolNode` 和条件边共同拥有 loop。
- OpenAI Agents SDK：`Agent` 保存配置，`Runner` 和 `run_internal` 拥有 turn transitions、handoff、guardrail 与 interruption。
- Microsoft Agent Framework：Agent/client/provider 处理 chat boundary，Workflow/`RunnerImpl` 处理 typed executor graph、events、checkpoint 和 request。

## Example

Network RCA Runtime 可以让 deterministic detection、candidate pruning 和 telemetry tools 先工作，再把有界调查交给 Agent，并在配置变更工具前要求 approval 和 recovery verification。

## Related Concepts

- [Agent](agent.md)
- [Agent Loop](agent-loop.md)
- [Tool Use](tool-use.md)
- [Memory](memory.md)
- [MCP](mcp.md)
- [Context Engineering](context-engineering.md)

## Representative Systems / Code

- [smolagents source notes](../code/agent-frameworks/smolagents.md)
- [LangGraph ReAct source notes](../code/agent-frameworks/langgraph-react-agent.md)
- [OpenAI Agents SDK source notes](../code/agent-frameworks/openai-agents-sdk.md)
- [Microsoft Agent Framework source notes](../code/agent-frameworks/microsoft-agent-framework.md)

## Advantages

- 把执行控制、工具权限和停止规则从模型输出中分离出来。
- 可以统一处理 tracing、approval、retry、checkpoint 和 human input。
- 让 Paper/Prompt 中的 Agent 概念落到可定位的代码路径。

## Limitations

- Runtime 的安全边界不等于诊断结论正确；仍需领域验证和证据 provenance。
- 不同框架对“loop”“session”“memory”“workflow”的命名不同，不能只按类名比较。
- Provider 或模型客户端可能拥有部分 tool loop；必须追踪真实调用链后再下结论。

## My Understanding

Agent 是面向目标的决策系统；Agent Runtime 是让这个系统可以受控执行的控制平面。对生产 AIOps 来说，Runtime 的价值往往不在让模型更会说，而在让每一次模型决策都经过工具边界、状态记录、预算、验证和权限控制。

## Open Questions

- AIOps Agent Runtime 应该把 candidate state、evidence provenance 和 conversation state 如何分层？
- 哪些状态必须 checkpoint，哪些只应存在于当前 investigation context？
