# Agent Framework Source Code Comparison

## Scope and evidence

本比较基于以下四个仓库的指定 commit 静态阅读：

- [smolagents](smolagents.md)
- [LangGraph ReAct](langgraph-react-agent.md)
- [OpenAI Agents SDK](openai-agents-sdk.md)
- [Microsoft Agent Framework](microsoft-agent-framework.md)

“实现事实”来自源码；“适合学习 / 生产取向”等判断是当前知识库的综合解释，不是项目官方排名。四个源码目录都位于被忽略的 `sources/code/`。

## Feature comparison

| Feature | smolagents | LangGraph ReAct | OpenAI Agents SDK | Microsoft Agent Framework |
|---|---|---|---|---|
| Agent abstraction | `MultiStepAgent` 把模型、工具、memory、状态和循环放在一个可继承对象中。 | 小型示例没有重型 Agent 类，核心是 `StateGraph` + model node + `ToolNode`。 | `Agent` 主要是配置/能力对象；`Runner` 承担执行。 | `Agent`/`BaseAgent` 面向 chat client、context providers、middleware；`Workflow` 承担更广编排。 |
| Main loop | `MultiStepAgent._run_stream()` 的有界 while-loop。 | 图边表示 `model → tools → model`。 | `Runner`/`run_loop.py` 将一次 turn 解析为 final/handoff/tool/interrupt，再继续。 | Agent run 由 client/provider 边界完成；Workflow 用 `RunnerImpl` 调度 Executors 和 edges。 |
| ReAct | ToolCallingAgent 或 CodeAgent 以 action/observation 继续。 | 最直接的实现：`route_model_output()` 在 `__end__` 与 `tools` 间路由。 | 可通过模型 tool calls 和 Runner continuation 实现，但 SDK 不强制 ReAct prompt。 | 可由 Agent + Workflow 组合，但不是核心单一 ReAct 实现。 |
| Tool calling | `Tool` schema + `execute_tool_call()`；支持多个调用和错误 observation。 | `bind_tools()` + `ToolNode`，结果写回 messages。 | `FunctionTool` schema/validation + `execute_tools_and_side_effects()`。 | `FunctionTool.invoke()`、middleware、approval/security、MCP adapter。 |
| State | Agent mutable `state` 与结构化 `AgentMemory.steps`。 | `InputState/State`，消息是主状态。 | Runner 上下文、current agent、session、next-step/interruption state。 | AgentSession/provider state；Workflow event/context/state/checkpoint 多层状态。 |
| Memory | 主要是当前 trajectory 的 context；不是自动持久 memory。 | 当前 graph message state；本 repo 未观察到 memory store。 | Session 可保存 conversation history；仍不等于 semantic memory。 | Session/context providers 和可选 checkpoint 提供持久边界；语义 memory 仍需应用设计。 |
| Code execution | `CodeAgent` 将代码转成 `python_interpreter` action，通过 local/remote executor。 | 本项目未实现。 | 不是核心 Agent 定义，需要外部 tool/sandbox。 | 有相关 filesystem/sandbox 模块，但本次未追踪出一个 canonical code-execution path。 |
| Graph | 不是核心控制结构。 | 核心控制结构，节点/边/编译直接可见。 | 主要是内部 next-step state machine，不要求用户定义 graph。 | WorkflowBuilder + typed edges，支持 fan-out/fan-in/switch/sub-workflow。 |
| Handoff | managed agents 以工具/能力方式暴露。 | 本示例未观察到。 | 一等 `Handoff`，是模型可见的 typed transfer，Runner 改变 active Agent。 | 可通过 workflow/executor/orchestration 组合；本次核心路径未将它压缩成一个固定 Handoff API。 |
| Multi-agent | managed agents 可被调用，但不是独立通用协议。 | 本 repo 未观察到。 | handoff、多个 Agent 和 shared/session context 支持多 Agent。 | Workflow、Executors、sub-workflows 和 orchestration 包支持更广编排。 |
| MCP | ToolCollection / MCP client adapter 可把 MCP tools 接入。 | 本 repo 未观察到。 | `AgentBase.mcp_servers` 将 MCP tools 纳入 Agent。 | `_mcp.py:MCPTool` 负责发现、调用和结果规范化。 |
| Tracing | logger、monitoring、step/token records。 | 主要依赖外围 runtime；项目源码没有专门 tracing layer。 | 一等 tracing，关联 model/tool/handoff/run。 | telemetry、workflow spans、events 和 status timeline。 |
| Guardrails / safety | tool argument checks、step budget、executor boundary；领域安全需另建。 | recursion/last-step 边界，域安全很少。 | input/output/tool guardrails、tripwire、approval、timeouts、max turns。 | schema validation、middleware、security、request input、checkpoint 和迭代上限。 |
| Stop condition | final answer / error / `max_steps`。 | no tool call → `END`，并受 last-step/recursion limit 约束。 | final output、terminal tool behavior、handoff completion、guardrail/interruption、`max_turns`。 | final client response，或 workflow idle/complete/error/request；`max_iterations`。 |
| Learning difficulty | 最容易看懂完整最小 Agent loop。 | 最容易看懂 graph 化 ReAct，但需要理解 graph runtime。 | 适合学习工程化 control plane 和安全边界。 | 最适合研究大型 runtime 能力边界，但初学者负担最高。 |
| Production orientation | 小而清晰，代码执行需严格 sandbox。 | 教学/模板性质较强，当前 repo 很小。 | 强调 runtime policy、approvals、sessions、handoff、tracing。 | 强调 typed workflow、provider ecosystem、checkpoint、MCP 和多语言/多包集成。 |

## How the implementations differ

### Same conceptual loop, different ownership

四个项目都可以解释为：模型得到上下文，产生回答或动作，工具执行产生结果，再决定继续还是停止。但 ownership 不同：

```text
smolagents:
  Agent object owns most of the loop and trajectory.

LangGraph ReAct:
  graph state + node/edge routing own the loop.

OpenAI Agents SDK:
  Agent declares capabilities; Runner owns turn transitions.

Microsoft Agent Framework:
  Agent/client/providers handle chat invocation;
  Workflow/RunnerImpl owns larger typed orchestration and persistence boundaries.
```

### Tool is not just a function

smolagents shows a compact schema/validation/call boundary. OpenAI SDK adds
strict schemas, guardrails, approval and tool behavior. Microsoft adds
middleware, security state, normalized `Content`, MCP metadata and invocation
context. LangGraph keeps the example intentionally simple with `ToolNode`.
For AIOps this suggests that a telemetry tool should include not only a
callable, but also argument schema, permissions, provenance, timeout and result
normalization.

### State and memory are separate design choices

Message accumulation in LangGraph, `AgentMemory.steps` in smolagents, OpenAI
sessions, and Microsoft sessions/checkpoints all preserve information, but
they do not mean the same thing. The code supports an important working
distinction:

```text
runtime state / trajectory
≠
durable conversation history
≠
retrievable semantic memory
```

### Graph versus loop

A graph makes legal transitions and state schemas explicit; a while-loop keeps
the minimal runtime easy to inspect. OpenAI's next-step state machine and
Microsoft's workflow runner sit between these extremes: the user need not
write every low-level loop, but runtime states, limits, interruptions and
handoffs remain explicit.

## Learning recommendation

For Agent fundamentals, start with **smolagents**, then read the **LangGraph
ReAct** graph to learn how the same loop becomes explicit state routing. Read
the **OpenAI Agents SDK** next for runtime boundaries, handoffs, approvals and
tracing. Use **Microsoft Agent Framework** last to understand how typed
workflows, providers, checkpoints, MCP, and larger orchestration systems expand
the control plane.

For a Network AIOps prototype, the best starting reference is **OpenAI Agents
SDK** for the Agent/Runner/tool/approval/tracing separation, combined with the
**LangGraph ReAct** pattern for visible state routing. If the prototype needs
typed multi-stage workflows, resumable human requests, and checkpointed
orchestration, Microsoft Agent Framework is the stronger architectural
reference. These are design-fit judgments, not claims that one project is
universally best.
