# How to Read an Agent from Source

这是一份源码学习方法指南。目标不是先看完整项目，而是先找出一条真实的
执行路径：用户任务怎样进入 Agent，模型怎样决定动作，工具结果怎样回来，
状态怎样更新，以及什么条件让它停止。

本例使用固定版本的 [Hugging Face smolagents](../../code/agent-frameworks/smolagents.md)：
`30bb1161095dbae2271e6bc3cc4c219cc3897a57`。

## 1. 先画最小路径

先把问题压缩成这条线：

```text
run()
  ↓
循环
  ↓
step()
  ↓
模型
  ↓
action / tool call
  ↓
tool
  ↓
observation
  ↓
memory / context
  ↓
停止
```

这里的几个词先用简单含义理解：

- **Model**：根据当前消息生成下一步文本或结构化动作的模型。
- **Tool**：Agent 可以调用的外部能力，例如查询、计算或代码执行。
- **Observation**：动作执行后从外部世界得到的结果。
- **Context**：本轮模型调用能看到的消息和历史信息。
- **Memory**：保存并重新提供这些历史的机制；本例主要是任务内 trajectory，不自动等于长期记忆。
- **Stop condition**：决定何时不再继续循环的条件。

## 2. smolagents 的真实调用链

从 `src/smolagents/agents.py:436` 的 `MultiStepAgent.run()` 开始：

```text
MultiStepAgent.run()
  → 初始化 task、state、system prompt 和 AgentMemory
  → 追加 TaskStep
  → MultiStepAgent._run_stream()
```

然后在 `agents.py:540`：

```text
_run_stream()
  → 检查 interrupt 和 max_steps
  → 按配置插入 _generate_planning_step()
  → 创建 ActionStep
  → 调用子类 _step_stream()
  → 保存 step
  → final answer 或继续下一步
```

对 `ToolCallingAgent`，`agents.py:1276` 的单步路径是：

```text
write_memory_to_messages()
  → model.generate(..., tools_to_call_from=...)
  → parse_tool_calls()
  → process_tool_calls()
  → execute_tool_call()
  → ToolOutput / observation
```

下一次循环时，`memory.py:92` 的 `ActionStep.to_messages()` 将模型输出、
tool call 和 `Observation:` 消息重新放进上下文，所以 observation 能影响下一次决策。

## 3. 为什么 `run()` 不是一次 LLM 调用

`run()` 只负责启动并消费运行流。真正的重复发生在 `_run_stream()` 的
bounded while-loop 中。每个 action step 都可能：

1. 调用模型；
2. 请求一个或多个工具；
3. 把工具结果写入当前 `ActionStep`；
4. 继续下一轮，或者通过 `final_answer` 结束。

因此，Agent 的“自主性”不是一个神秘属性，而是 runtime 是否允许模型根据
新 observation 选择下一步，以及 runtime 是否真正执行并记录这一步。

## 4. `step()` 与 `_step_stream()` 的关系

`MultiStepAgent._step_stream()` 在 `agents.py:772` 是抽象接口。它不规定
具体 action 长什么样，只规定子类要完成一次模型-动作交互。

- `ToolCallingAgent._step_stream()`：把模型输出解释为 function-style tool call。
- `CodeAgent._step_stream()`：把模型输出解析成代码，再交给 `python_executor`。

两者共享 `MultiStepAgent._run_stream()`，所以“主循环”与“单步 action
表示”被分开了。这是阅读框架源码时很值得寻找的设计边界。

## 5. while-loop 与 graph-based ReAct 的阅读方法

smolagents 将循环直接写在 `_run_stream()`：状态变化和停止判断集中在一个
while-loop 中，适合先学清楚基本机制。

LangGraph ReAct 则把相似过程拆成 graph 的 node 和 routing：模型 node、tool
node、state update 和 END 条件分别可见。阅读 graph-based 实现时，问题仍然
相同：找入口、找 state、找模型 node、找 tool node、找条件边和 END。图只是
另一种表达控制流的方式，不自动意味着更强的 planning。

## 6. 代码阅读检查清单

对任何 Agent 项目，可以按以下顺序搜索：

```text
入口：run / invoke / execute
主循环：while / stream / step / runner
模型：generate / chat / completion
动作：tool_call / action / code block
执行器：dispatch / executor / call
结果：observation / tool result / error
状态：state / memory / messages
停止：final / done / END / max_steps
可靠性：retry / timeout / guardrail / validation
```

每找到一个符号，记录：

```text
caller → callee
输入 → 输出
修改了什么状态
下一个节点是什么
失败时走哪条分支
```

## 7. 当前验证产物

- [smolagents annotated core excerpts](../../annotations/smolagents/30bb1161095dbae2271e6bc3cc4c219cc3897a57/annotated/agents.py.md)
- [smolagents memory and tools annotations](../../annotations/smolagents/30bb1161095dbae2271e6bc3cc4c219cc3897a57/annotated/memory-and-tools.py.md)
- [execution path](../../annotations/smolagents/30bb1161095dbae2271e6bc3cc4c219cc3897a57/EXECUTION_PATH.md)
- [code guide](../../annotations/smolagents/30bb1161095dbae2271e6bc3cc4c219cc3897a57/CODE_GUIDE.md)

这些文件是固定 commit 的教学派生材料。原始 checkout 仍在被忽略的
`sources/code/`，没有被修改。
