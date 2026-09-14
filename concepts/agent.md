Status: evolving

# Agent

## Definition

Agent 是根据任务上下文接收 Observation、选择 Action 并与 environment 交互以完成目标的系统。ReAct 增加的一个重要视角是：language thought 可以作为增强 action space 中的显式语言动作；它不改变环境，但会更新后续决策所使用的 context。

LLM+P 补充了一个重要边界：系统可以包含显式的 classical planner 和机器人 executor，却仍主要是一条自然语言到结构化计划的求解 pipeline。是否称为 Agent 不能只看是否出现 planner 或工具，还要看系统是否在目标驱动的运行时循环中持续接收状态、执行行动并调整后续行为。（Source: [LLM+P paper note](../papers/llm-p/notes.md); Sec. III; Sec. V.D）

RAP 论文把 LLM 称为 reasoning agent，并让它在 MCTS 中提出 action；但其核心任务主要在模型内部用 world model 模拟 state transition，没有因此定义一个必须面向真实 environment 的通用 Agent。这个角色命名应与系统边界分开记录。（Source: [RAP paper note](../papers/rap/notes.md); Sec. 1; Sec. 3.1）

ReWOO 的 Planner、Worker 和 Solver 形成了一个有目标的 augmented LM workflow，但论文的核心是模块化 reasoning、tool execution、solving 与效率，而不是给出通用 Agent 定义。是否把一个具体 ReWOO 部署称为 Agent，仍取决于它是否有持续的 environment state、执行反馈和后续决策循环。（Source: [ReWOO paper note](../papers/rewoo/notes.md); Sec. 2.1; Sec. 4）

Reflexion 进一步展示了一个跨 attempt 的 Agent loop：一次 trajectory 由 Evaluator 评估，Self-Reflection 把结果转成语言经验，下一次 Actor 再读取这段 experience。这个外层反馈机制是可选的 Agent 组成部分，不是 Agent 定义本身。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3）

## System Boundary

下面是本知识库当前的工作区分，不是三篇论文共同给出的正式 taxonomy：

- **LLM：** 负责生成 token、Thought、Action、API call 或 reflection 的模型。模型本身不自动拥有环境、执行器或持久记忆。
- **Tool-augmented LLM：** 能发出工具调用并消费结果，但不一定存在目标驱动的持续运行时闭环。Toolformer 是这个层次的重要例子；论文将其定位为 LM。
- **Agent：** 围绕目标持续决策，能够根据可用状态行动，并在 Action / tool invocation 产生 Observation 或 feedback 时利用它，再决定继续、修正或结束的系统。
- **Agentic workflow：** 由外部程序或人为编排多个模型、工具和检查器的工作流；只有在它能依据状态持续调整行为时，才更接近 Agent interaction loop。

所以，Tool Use 是 Agent 可能拥有的能力，不是判定 Agent 的充分条件；是否存在目标、状态、持续决策和反馈闭环，比是否调用过 API 更关键。（Source: [ReAct paper note](../papers/react/notes.md); [Toolformer paper note](../papers/toolformer/notes.md); [Reflexion paper note](../papers/reflexion/notes.md)）

## Why It Matters

ReAct 使 Agent 的基本闭环变得清晰：外部 Action 取得或改变环境状态，Observation 反馈给模型，Thought 在上下文中解释当前状态并决定下一步。Agent 不只是一次性生成答案，而是在轨迹中持续决策。

## Core Mechanism

在跨 attempt 场景中，Agent 还可以把完整 trajectory 交给 Evaluator，再把 verbal reflection 写入 episodic memory，作为下一次 Actor 的 context：

~~~text
Attempt → Evaluate → Reflect → Memory → Next Attempt
~~~

这是一种反馈增强的外层 loop，不意味着所有 Agent 都有独立 Planner、Evaluator 或 persistent Memory。（Source: [Reflexion paper note](../papers/reflexion/notes.md); Sec. 3）

ReAct 用 `\hat{A} = A ∪ L` 扩展动作空间，其中 `A` 是环境动作，`L` 是语言空间。环境动作产生 Observation；语言 thought 不产生环境反馈，但追加到 trajectory context 中。

## Typical Architecture

```text
Task / Observation → Thought → Action → Observation → ... → Finish
```

论文没有把 Planner、Executor 和 Memory 实现为独立模块；这些功能主要由 LLM、trajectory context 和环境接口共同承担。

RAP 可以用另一种推理时结构表示：

~~~text
Task → State → MCTS
             ↙   ↘
      Action / World Model
             ↓
        Reward / Search
             ↓
       Selected Reasoning Path
~~~

这是一种 inference-time planning loop；如果没有真实执行器和环境 Observation，它不等同于完整的 environment-facing Agent loop。（Source: [RAP paper note](../papers/rap/notes.md); Sec. 3）

ReWOO 的模块化流程可以表示为：

~~~text
Task → Planner blueprint → Worker tools
                         ↓
                   Evidence → Solver → Answer
~~~

它有计划、工具和求解步骤，但 Planner 在主流程中不依赖逐步 Observation 重新生成 blueprint；因此它是 Agentic workflow 的一个候选组织方式，而不是仅凭模块名字即可判定为完整 Agent。（Source: [ReWOO paper note](../papers/rewoo/notes.md); Sec. 2.1）

若加入 Reflexion 的跨尝试机制，功能结构可扩展为：

~~~text
Actor trajectory → Evaluator → Self-Reflection → Episodic Memory
                                                          ↓
                                                    Next Actor attempt
~~~

## Example

在需要外部证据的任务中，Agent 可以先用 Thought 分解查询，再调用工具，根据 Observation 修正查询并最终结束。在长时程环境任务中，Agent 也可以用 Thought 跟踪“找到物体 → 拿取 → 处理 → 放置”等子目标。

## Related Concepts

- [Reasoning](reasoning.md)
- [Tool Use](tool-use.md)
- [Planning](planning.md)
- [Memory](memory.md)
- [Reflection](reflection.md)

## Representative Papers

- [ReAct: Synergizing Reasoning and Acting in Language Models](../papers/react/notes.md) — 将 reasoning trace 与外部 action 交错放入 Agent 闭环。
- [Toolformer: Language Models Can Teach Themselves to Use Tools](../papers/toolformer/notes.md) — 展示 tool-augmented LM 的 learned API-use policy，但不自动等同于完整 Agent。
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../papers/reflexion/notes.md) — 在单次 trajectory 之外加入 evaluator、verbal reflection 和跨 attempt memory。
- [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../papers/llm-p/notes.md) — 作为 explicit planner / executor pipeline 的边界案例；论文没有据此给出通用 Agent 定义。
- [RAP: Reasoning with Language Model is Planning with World Model](../papers/rap/notes.md) — 作为 LLM reasoning agent、world model 和 MCTS 的推理时规划案例；不自动等同于完整环境 Agent。
- [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](../papers/rewoo/notes.md) — 作为 Planner–Worker–Solver 的 augmented LM workflow；不自动等同于持续环境 Agent。

## Representative Systems / Code

## Advantages

- 可以在行动前显式组织目标和子目标。
- 可以通过外部 Observation 获取内部知识之外的信息。
- 轨迹便于人检查、诊断和在线干预。

## Limitations

- Agent 的行为仍依赖模型、prompt、action space 和 Observation 的质量。
- 如果规划、状态记录和执行都依赖同一个上下文，语言 thought 可能循环或 hallucinate；不应假定它自动保证计划、状态或事实正确。
- ReAct 的示范没有提供持久化 Memory、通用工具权限或执行错误处理机制；这些是更完整 Agent 系统仍需补足的边界。
- Reflexion 的语言反馈依赖 Evaluator 和 memory 容量；它能改变后续 context，但不等于参数学习、跨会话持久化或完整 Planner-Executor 架构。

## My Understanding

ReAct 让我把 Agent 理解为一个闭环 policy，而不是“带有一个 prompt 的 LLM”。Thought 是用于组织 context 的显式语言动作，Action 是与外部世界交换信息或改变状态的动作；两者交替才形成 Agent 的任务执行能力。

结合 Reflexion，我会把 Agent 的能力再分成两个时间尺度：单次 trajectory 内由 Observation 驱动的决策，以及跨 attempt 由 Evaluator、reflection 和 episodic memory 驱动的行为修正。后者是可选的外层机制，不能被简化成一个自动拥有长期记忆的 LLM。

## Common Confusions

- 只会调用 API 的模型不必然是 Agent；需要检查它是否有目标驱动的持续决策和状态 / feedback loop。
- Agent 也不必然包含独立 Planner、Memory 或多个模型；这些是架构选项，不是定义条件。
- Toolformer 的 learned API-use behavior 与 ReAct 的 runtime interaction loop 属于不同层次。
- 拥有外部 planner 或 executor 也不自动使整个系统成为 Agent；仍需检查目标驱动的状态交互和持续决策边界。
- 论文把模型称为 reasoning agent，不等于该模型已经具备真实环境感知、执行反馈或持久记忆。
- Planner–Worker–Solver 的模块化和工具调用不自动证明存在跨状态的 Agent loop；要检查是否支持执行后 Observation、replanning 和终止控制。

## Open Questions

- 如何分别测量 Agent 的 reasoning、planning、tool use 和 environment recovery 能力？
- Thought 是否是可控的内部状态接口，还是仅仅是生成出来的语言轨迹？
