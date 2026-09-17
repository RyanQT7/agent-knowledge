# smolagents 源码阅读指南

## 1. 项目解决什么问题

smolagents 用 Python 提供一个相对小而完整的 tool-using Agent runtime。它把
模型、提示、工具、运行时状态、trajectory memory、单步动作和停止条件组合起来。
本次重点是理解一个 Agent 如何从 `run()` 进入循环，再把工具 observation 送回模型。

相关已有笔记：[smolagents framework note](../../../code/agent-frameworks/smolagents.md)。

## 2. 从哪里开始读

推荐顺序：

1. `src/smolagents/agents.py:268` — `MultiStepAgent` 的构造函数：看它持有什么状态。
2. `src/smolagents/agents.py:436` — `run()`：看任务如何初始化并进入 runtime。
3. `src/smolagents/agents.py:540` — `_run_stream()`：看真正的 bounded while-loop。
4. `src/smolagents/agents.py:758` — `write_memory_to_messages()`：看历史如何变成模型输入。
5. `src/smolagents/agents.py:1215` — `ToolCallingAgent`：看结构化 tool action 如何接入。
6. `src/smolagents/agents.py:1276`、`:1361`、`:1453`：依次看生成、dispatch、校验和执行。
7. `src/smolagents/memory.py:41`、`:92`、`:214`：看 step 数据结构和 observation 回流。
8. `src/smolagents/tools.py:106` — `Tool`：看工具的名字、描述、schema、验证和 callable 边界。
9. `src/smolagents/models.py:452` — `Model`：看 runtime 与具体模型 provider 如何解耦。
10. `src/smolagents/agents.py:1505`、`:1638`：最后比较 `CodeAgent` 的 code-as-action 分支。

本次的注释摘录见同目录的 [`annotated/agents.py.md`](annotated/agents.py.md) 和
[`annotated/memory-and-tools.py.md`](annotated/memory-and-tools.py.md)。

## 3. 核心对象

| 对象 | 真实位置 | 学习重点 |
|---|---|---|
| `MultiStepAgent` | `agents.py:268` | 共享运行时、state、memory、tools、step budget。 |
| `ToolCallingAgent` | `agents.py:1215` | 把模型 tool call 变成一次 action，并接收 observation。 |
| `CodeAgent` | `agents.py:1505` | 把模型生成代码交给 Python executor。 |
| `AgentMemory` | `memory.py:214` | 保存有序 `steps`，支持重放和消息重建。 |
| `ActionStep` | `memory.py:51` | 保存模型输出、tool calls、observation、error 和 final 标志。 |
| `Tool` | `tools.py:106` | 描述工具 schema 并提供可调用实现。 |
| `Model` | `models.py:452` | 提供 `generate()` 和 tool-call parsing 抽象。 |

## 4. 读完应该理解什么

目标不是记住 API，而是能够用真实符号解释：

```text
task
→ run()
→ _run_stream()
→ write_memory_to_messages()
→ model.generate()
→ process_tool_calls()
→ execute_tool_call()
→ ActionStep.observations
→ ActionStep.to_messages()
→ next step / final_answer
```

这条路径显示：Agent 不是一次 LLM 调用；它是一个由 runtime 控制的循环。
模型负责提出下一步动作，runtime 负责工具边界、状态记录、错误处理和停止。

## 5. 可以暂时跳过的内容

第一次阅读可以跳过 provider-specific model adapters、logging UI、Hub/MCP
加载器、remote executor 细节以及非主路径的工具包装。理解主循环后，再回看
`prompts/toolcalling_agent.yaml`、`prompts/code_agent.yaml` 和 executor 代码，
可以看出提示协议如何约束模型输出。

## 6. 本次没有做什么

没有运行 repository、安装依赖、调用模型或执行 Python executor。注释版是固定
commit 的静态教学摘录，不是可安装模块，也不替换原始 source。
