# ReAct Agent Implementation

这是一份源码学习文档：先用一个最小循环理解 ReAct，再对照两个真实项目。
论文背景见 [ReAct paper notes](../../papers/react/notes.md)；源码证据见
[原始 ReAct 仓库笔记](../../code/react/notes.md)、[smolagents](../../code/agent-frameworks/smolagents.md) 和 [LangGraph ReAct](../../code/agent-frameworks/langgraph-react-agent.md)。

## 1. ReAct 是什么

ReAct 是把 **Reasoning（当前任务上的语言推理）** 和 **Acting（对外部环境或工具采取动作）** 放到同一条运行轨迹中。模型不是只想完再给答案，而是可以：先说明下一步意图，调用工具，读取结果，再决定下一步。

```text
Task → Thought → Action → Observation → Thought → ... → Final Answer
```

这里的 Thought 是生成出来的语言轨迹，不是模型真实隐藏的 internal state；Action 是运行时可执行的动作；Observation 是动作之后从外界返回的结果。

## 2. Thought / Action / Observation

- **Thought：** 模型生成的、用于组织当前问题和下一步行为的语言内容。它可能帮助分解任务，但不等于完整 Planner，也不等于隐藏状态。
- **Action：** 发送给外部环境或工具的结构化/文本化请求，例如搜索、查询或执行某个动作。
- **Observation：** 环境或工具对 Action 的返回，例如搜索结果、错误、数据或执行状态；它是下一轮模型输入的 grounding 边界。

## 3. ReAct 在真实代码中如何实现

最小实现通常需要三个接口：

1. 模型根据当前 state 产生回答或动作。
2. Runtime 解析动作并调用对应 tool/environment。
3. Runtime 把结果追加到 state/context，再次调用模型，直到 final 或达到预算。

最小伪代码：

```python
while not finished:
    decision = model(state)

    if decision.tool_call:
        observation = tool(...)
        state.append(observation)
    else:
        return decision.answer
```

生产代码还需要：工具 schema 和参数校验、错误结果、权限、超时、重复调用检测、step limit、verification 和 human gate。

## 4. while-loop ReAct：smolagents

在 [smolagents 源码笔记](../../code/agent-frameworks/smolagents.md) 所固定的 commit `30bb1161095dbae2271e6bc3cc4c219cc3897a57` 中：

```text
MultiStepAgent.run()
  → MultiStepAgent._run_stream()
  → optional _generate_planning_step()
  → subclass _step_stream()
  → model.generate()
  → process_tool_calls()/execute_tool_call()
  → ActionStep / AgentMemory
  → next iteration or final_answer
```

真实位置：

- `src/smolagents/agents.py:MultiStepAgent.run()` 初始化任务、state 和 memory。
- `src/smolagents/agents.py:MultiStepAgent._run_stream()` 是有界的多步 while-loop。
- `src/smolagents/agents.py:ToolCallingAgent._step_stream()` 请求模型生成 tool calls。
- `src/smolagents/agents.py:process_tool_calls()` 与 `execute_tool_call()` 执行工具并记录结果/错误。
- `src/smolagents/memory.py:AgentMemory` 保存 `TaskStep`、`ActionStep`、Observation 等轨迹；`ActionStep.to_messages()` 将其转换回模型消息。
- `src/smolagents/prompts/toolcalling_agent.yaml` 将 tool result 定义为 `Observation`，以 `final_answer` 作为终止工具。

smolagents 的关键不是某个神秘 Agent 类，而是一个可见的状态转移：`model → action → executor → observation → memory → model`。`max_steps` 默认提供基本循环上限。

## 5. graph-based ReAct：LangGraph

在 [LangGraph ReAct 源码笔记](../../code/agent-frameworks/langgraph-react-agent.md) 所固定的 commit `9bbd82d84905acc37f527b1f372dae841016f3b4` 中：

```text
START
  → call_model
  → route_model_output
      ├─ no tool_calls → END
      └─ tool_calls → ToolNode(TOOLS)
                         → state.messages update
                         → call_model
```

真实位置：

- `src/react_agent/graph.py:call_model()` 将系统消息和 `state.messages` 交给绑定了工具的模型。
- `src/react_agent/graph.py:route_model_output()` 根据最后一条 `AIMessage.tool_calls` 选择 `__end__` 或 `tools`。
- `src/react_agent/graph.py:builder = StateGraph(...)`、`add_node()`、条件边和 `builder.compile()` 定义控制图。
- `src/react_agent/tools.py:search()` 是当前示例中的工具。
- `src/react_agent/state.py:InputState/State` 保存消息和 last-step 预算状态。

这不是另一种语义上的 ReAct；它是把同一个闭环从 Python while-loop 改写成可编译的状态图。Graph 的价值是让 state schema、routing、termination 和后续可插入的节点更明显。

## 6. Tool Calling 和 ReAct 的关系

ReAct 是一种运行时组织方式：Action 之后获得 Observation，再继续决策。Tool Calling 是一种让模型表示 Action、让 runtime 调用工具的接口。

二者可以组合，但不等价：

```text
Tool calling without continuation:
  model → one tool → result → answer

ReAct with tool calling:
  model → tool → observation → model → tool/answer → ...
```

原始 ReAct 仓库使用 `search[...]`、`lookup[...]`、`finish[...]` 等文本协议；LangGraph 使用绑定工具和 `ToolNode`；smolagents 在 Python 边界执行 schema/参数校验。接口形式不同，但是否形成 ReAct 关键看是否存在 Observation-driven continuation。

## 7. Memory / State 在 ReAct 中的作用

ReAct 至少需要一个当前运行 state，保存任务、已经采取的动作和工具结果。它让下一次模型调用知道“已经试过什么、得到什么”。

- 原始 ReAct：`HistoryWrapper` 将动作和 observation 序列化到当前 prompt；这是 task-local context。
- smolagents：`AgentMemory.steps` 是结构化 trajectory，再通过 `to_messages()` 注入 context。
- LangGraph：`State.messages` 是图状态，工具结果以消息形式返回。

这些都不是自动的 long-term memory。持久 session、语义检索、跨 incident episodic memory 需要额外设计。

## 8. Stopping condition

常见停止条件有：

- 模型返回 final answer；
- 模型调用专门的 `final_answer`/finish 工具；
- 没有 tool call，图路由到 `END`；
- 达到最大 step/recursion limit；
- 工具或 guardrail 发生不可继续的错误；
- 需要 human approval 或 input，运行暂停等待恢复。

停止条件必须由 runtime 控制，不能完全依赖模型自己说“完成了”。

## 9. 为什么 Agent 会死循环

常见原因包括：模型重复生成相同工具调用；Observation 没有提供新信息；工具错误被无限重试；状态没有记录已经尝试过的路径；工具返回格式无法被模型理解；没有清晰的 final action；或者图路由始终把模型输出送回工具节点。

## 10. 如何限制 Agent loop

至少需要：

- `max_steps` / recursion limit / `max_turns`；
- 重复调用检测和每工具调用预算；
- 工具超时、错误分类和有限重试；
- final answer schema 和明确 stop action；
- candidate/evidence 的 deterministic constraints；
- 高风险工具 approval、权限和 rollback；
- 记录每次 tool call、observation、cost 和 trace。

OpenAI Agents SDK 的 `Runner`/`max_turns`、smolagents 的 `max_steps`、LangGraph 的 last-step/recursion state，以及 Microsoft Agent Framework 的 workflow `max_iterations` 都体现了不同的 runtime 限制方式。

## 11. ReAct 在 AIOps RCA 中如何使用

可以让 Agent 在一个受约束的调查空间内：先读 incident 摘要，查询 metrics，再根据 observation 查询 syslog、topology 或 traffic，形成候选根因并请求验证。

```text
Incident
  → query metrics
  → observation: interface anomaly
  → query syslog + topology
  → observation: neighbor/link inconsistency
  → rank bounded candidates
  → independent verification
  → evidence-backed RCA
```

但检测、时间/实体对齐、candidate enumeration、topology hard constraint、权限、验证和 remediation gate 不应全部交给开放式语言循环。

## 12. 为什么 AIOps 更适合 constrained ReAct

Network RCA 的候选可能是 device、interface、link、optical module、path 或 fault type，全集规模很大且需要物理一致性。完全开放的 ReAct 可能产生不存在的设备、跳过关键证据、反复查询或直接建议危险操作。

因此更合适的是：

```text
Deterministic detection / candidate space
  → bounded ReAct investigation
  → provenance-rich observations
  → deterministic / independent verification
  → human-gated remediation
```

这是当前知识库的跨项目 engineering synthesis，不是某个单一框架的标准架构。

## 当前应记住

1. ReAct 的核心是 Observation 驱动的运行时闭环。
2. Thought 是显式语言轨迹，不是 hidden internal state。
3. Tool Calling 是接口，ReAct 是循环组织；可以组合但不等价。
4. while-loop 和 graph-based loop 表达相同基本闭环，但控制权和可观察性不同。
5. state/context 支持当前轨迹，不自动等于 long-term memory。
6. 没有预算、停止条件和验证，Agent loop 可能循环或失控。
7. Network AIOps 应优先采用 constrained ReAct。
