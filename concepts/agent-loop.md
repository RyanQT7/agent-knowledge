---
Status: evolving
---

# Agent Loop

## Definition

Agent Loop 是 Agent 反复执行“读取当前上下文 → 让模型做决策 → 执行动作或返回结果 → 更新状态”的控制循环。

## Why It Matters

一次模型调用只能产生一次输出；当任务需要工具、外部 Observation、重试、handoff 或验证时，循环才提供继续行动的结构。循环的终止条件和预算是可靠性的一部分。

## Core Mechanism

```text
Context / State
  → Model decision
  → Final answer? ─ yes → Stop
  → Tool / action
  → Observation / result
  → State update
  → step budget / guardrail check
  → next turn
```

## Typical Architecture

- **While-loop：** smolagents 的 `MultiStepAgent._run_stream()` 直接循环到 final answer 或 `max_steps`。
- **State graph：** LangGraph ReAct 用 `call_model → route_model_output → ToolNode → call_model` 的边表达循环。
- **Runtime state machine：** OpenAI Runner 将 final output、tool continuation、handoff 和 interruption 区分为不同 next-step 状态。
- **Workflow graph：** Microsoft Agent Framework 用 Executor、edge runner、event 和 `max_iterations` 运行更大的有向流程。

## Example

AIOps Agent 先查询接口 metrics；Observation 显示链路两端不一致时，下一步可以查 syslog 和 topology，而不是从初始 prompt 直接给出结论。

## Related Concepts

- [Agent](agent.md)
- [Agent Runtime](agent-runtime.md)
- [Reasoning](reasoning.md)
- [Planning](planning.md)
- [Tool Use](tool-use.md)
- [Verification](aiops/verification.md)

## Representative Systems / Code

- [smolagents loop](../code/agent-frameworks/smolagents.md)
- [LangGraph graph loop](../code/agent-frameworks/langgraph-react-agent.md)
- [OpenAI Runner loop](../code/agent-frameworks/openai-agents-sdk.md)
- [Microsoft workflow runner](../code/agent-frameworks/microsoft-agent-framework.md)

## Advantages

- 可以由 Observation 驱动下一步行为，而不是把所有步骤预先写死。
- 可以把失败、审批、重试和验证变成显式控制状态。
- Graph 或 typed state 能提升可视性和可恢复性。

## Limitations

- 循环本身不保证推理正确；错误 Observation 可能被反复放大。
- 过多工具和过宽状态会带来成本、延迟、重复调用和上下文噪声。
- 没有 stop condition、step limit 或副作用门禁时，循环可能失控。

## My Understanding

ReAct 是一种最容易理解的 Agent Loop；框架的主要差异在于谁拥有循环和如何表达转移。对 Network AIOps，循环应被约束在确定性 candidate/evidence/verification 边界内。

## Open Questions

- 如何为 investigation loop 定义“足够证据”而不只依赖模型自报完成？
- 哪些循环转移应由模型决定，哪些应由 deterministic policy 强制决定？
