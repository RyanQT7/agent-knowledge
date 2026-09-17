# smolagents Agent Execution Path

> 版本：`huggingface/smolagents` @ `30bb1161095dbae2271e6bc3cc4c219cc3897a57`。这是基于静态源码的 Framework ↔ Code 路径，不是运行结果。

## Main path

```text
User task
  ↓
src/smolagents/agents.py:436 — MultiStepAgent.run()
  ↓ 初始化 task、state、system prompt、AgentMemory、TaskStep
src/smolagents/agents.py:540 — MultiStepAgent._run_stream()
  ↓ while: step_number <= max_steps
  ├─ 可选：agents.py:639 — _generate_planning_step()
  └─ agents.py:1276 — ToolCallingAgent._step_stream()
       ↓ memory/context
       ↓ models.py:Model.generate()
       ↓ model output: tool_calls 或文本协议
       ↓ models.py:Model.parse_tool_calls()（需要时）
    agents.py:1361 — process_tool_calls()
       ↓ agents.py:1453 — execute_tool_call()
       ↓ Tool / managed agent 的 callable
       ↓ ToolOutput.observation
       ↓ ActionStep.tool_calls / observations
    memory.py:92 — ActionStep.to_messages()
       ↓ Observation 重新进入下一轮模型上下文
  ↓ final_answer 或达到 max_steps
src/smolagents/agents.py:609 — FinalAnswerStep
  ↓
最终 output / RunResult
```

## Stage-by-stage mapping

| Stage | Real source | Class / function | What changes |
|---|---|---|---|
| Input and setup | `src/smolagents/agents.py:436` | `MultiStepAgent.run()` | Sets `task`, merges `state`, resets or keeps memory, appends `TaskStep`. |
| Runtime loop | `src/smolagents/agents.py:540` | `MultiStepAgent._run_stream()` | Owns step counter, optional planning, error boundary, final-answer flag, and max-step stop. |
| Optional plan | `src/smolagents/agents.py:639` | `_generate_planning_step()` | Calls the model for an initial/update plan when `planning_interval` is configured. |
| Context build | `src/smolagents/agents.py:758` | `write_memory_to_messages()` | Serializes system prompt and ordered memory steps into model messages. |
| Model decision | `src/smolagents/agents.py:1276` | `ToolCallingAgent._step_stream()` | Calls `Model.generate()` with tools and parses the returned action. |
| Tool dispatch | `src/smolagents/agents.py:1361` | `process_tool_calls()` | Converts provider calls to runtime calls, executes one or more, and collects outputs. |
| Validation/execution | `src/smolagents/agents.py:1453` | `execute_tool_call()` | Checks tool existence, substitutes state references, validates arguments, then calls the capability. |
| Observation write-back | `src/smolagents/agents.py:1390` | nested `process_single_tool_call()` | Converts the result into an observation and returns `ToolOutput`. |
| Context feedback | `src/smolagents/memory.py:92` | `ActionStep.to_messages()` | Emits `Calling tools:` and `Observation:` messages for the next model call. |
| Termination | `src/smolagents/agents.py:582`, `609` | `ActionOutput`, `FinalAnswerStep` | A `final_answer` tool call or final action ends the loop; `max_steps` is the fallback boundary. |

## CodeAgent branch

`CodeAgent` reuses `MultiStepAgent._run_stream()` but overrides the single-step
implementation at `agents.py:1638`. Its path is:

```text
memory context
  → CodeAgent._step_stream()
  → Model.generate()
  → parse_code_blobs() / structured code
  → ToolCall(name="python_interpreter")
  → self.python_executor(code_action)
  → execution logs/output as observation
  → next step or final answer
```

This is code-as-action, not the same boundary as a normal function `Tool`; the
executor therefore deserves stronger sandboxing and approval in a real system.

## Important boundaries

- `run()` is an orchestration entry point; the repeated behavior lives in `_run_stream()`.
- `ToolCallingAgent._step_stream()` decides how to interpret the model output, but `execute_tool_call()` owns the actual call boundary.
- `AgentMemory` is an in-process ordered trajectory. The path does not by itself provide persistent or long-term memory.
- `max_steps` is a runtime stop condition, not a guarantee that the model's reasoning is correct.
