Status: evolving

# World Model

## Definition

World Model 是用于表示或预测环境状态、行动及其可能后果的模型，使系统能够在真实执行前模拟未来、比较候选行动或评估状态变化。它可以是显式动力学模型、学习到的预测模型，也可以是被提示来预测任务状态的语言模型。

当前资料中，RAP 使用同一个 LLM 通过不同 prompt 预测 action 后的 imagined state；这属于 inference-time、task-conditioned 的 world-model 用法，不应直接等同于真实环境的可靠 dynamics model。（Source: [RAP paper note](../papers/rap/notes.md); Sec. 3.1）

## Why It Matters

如果系统只能看到当前状态和下一步动作，就很难比较不同未来。World model 可以为 planning 提供状态转移、lookahead、候选路径评估和错误分支回溯的基础；但错误预测也可能把搜索引向一致而错误的未来。

## Core Mechanism

一个最小的 world-model planning 闭环包含：

1. 从任务中抽取当前 state。
2. 提出候选 action。
3. 预测 action 后的 next state 或 observation。
4. 根据目标、reward 或约束评估结果。
5. 继续搜索、执行或修正。

RAP 中的预测由 LLM 生成，state、action 和 reward 都按任务定义。其 predicted state 是搜索条件，不是已经由外部 environment 验证的 observation。（Source: [RAP paper note](../papers/rap/notes.md); Sec. 3.1–3.3）

## Typical Architecture

~~~text
Current State
→ Candidate Action
→ World Model Prediction
→ Predicted Next State
→ Reward / Constraint Evaluation
→ Search, Execute, or Replan
~~~

world model 可以放在 planner 内部服务候选路径评估，也可以和真实 environment 交互形成 model-predictive control；当前知识库的 RAP 证据主要覆盖前一种 inference-time search。

## Example

在 Blocksworld 中，world model 根据积木当前配置和 STACK / UNSTACK 等 action 预测下一种配置。MCTS 再利用这些预测状态探索多个动作序列。这个过程不等于真的移动了积木；真实执行仍需要另一个 environment 或 executor。（Source: [RAP paper note](../papers/rap/notes.md); Sec. 4.1）

## Related Concepts

- [Planning](planning.md)
- [Reasoning](reasoning.md)
- [Agent](agent.md)
- [Tool Use](tool-use.md)
- [Memory](memory.md)

## Representative Papers

- [RAP: Reasoning with Language Model is Planning with World Model](../papers/rap/notes.md) — 使用 prompting 的 LLM world model 与 MCTS 进行 inference-time planning。

## Representative Systems / Code

## Advantages

- 支持在执行前进行 lookahead 和候选路径比较。
- 可以把中间状态显式放入搜索节点，而不只保留一条线性 token trace。
- 与不同的 search、reward 或 planner 结合时具有模块化潜力。

## Limitations

- predicted state 可能错误，world model 的流畅性不等于环境预测正确性。
- 状态表示、action space 和 reward 往往需要任务特定设计。
- 深度和分支数增加会带来大量模型调用和搜索成本。
- 模拟状态不自动提供真实环境 Observation、执行结果、权限或副作用信息。
- 当前 RAP 资料不足以判断这种 world model 是否能可靠支持开放环境、部分可观测任务或长期运行 Agent。

## My Understanding

World model 是 planning 的预测基础，不是 planning 本身，也不是 memory。它回答“执行某个 action 后可能到哪里”，而 planner / search 负责“比较哪些路径”，environment 负责“实际发生了什么”。RAP 的贡献是证明 LLM 可以在一定任务表示下承担前两者之间的预测接口，但其可靠性边界仍需要真实反馈验证。

## Open Questions

- 如何用真实 environment feedback 校准或纠正语言模型 world model？
- predicted state 与实际 Observation 不一致时，系统应如何检测、回溯和 replanning？
- world model 应保存完整状态、局部状态还是不确定性分布？
- 何时应使用 learned world model，何时应使用 symbolic simulator 或 classical planner？
