# Knowledge Review v1

Review date: 2026-09-14

## Scope

本次 Review 只整合知识库中已经完成来源核对的三篇论文笔记：

- [ReAct: Synergizing Reasoning and Acting in Language Models](../../papers/react/notes.md)
- [Toolformer: Language Models Can Teach Themselves to Use Tools](../../papers/toolformer/notes.md)
- [Reflexion: Language Agents with Verbal Reinforcement Learning](../../papers/reflexion/notes.md)

这不是三篇论文摘要的拼接，也不是对原始 PDF 的重新全文阅读。目标是检查现有 Concepts 的边界，提取三篇论文之间可以长期复用的关系，并明确当前知识仍然没有覆盖的部分。

## 1. What I Understand About Agents So Far

### 一个暂时的工作定义

**这是本次跨论文后的抽象，不是三篇论文共同给出的正式定义：**

Agent 是一个围绕目标持续进行决策的系统。它至少需要把任务目标、当前可用状态和下一步行动联系起来，并能在行动或工具调用产生状态、Observation 或 feedback 时利用它，再决定继续、修正或结束。系统是否还包含独立 Planner、Memory、Evaluator 或多个模型，需要由具体架构单独判断。

因此，Agent 的关键不在于“输出了很长的文本”或“调用过一次 API”，而在于是否存在有目标的、可被状态或反馈改变的持续决策过程。

### 四个容易混淆的层次

| 层次 | 当前理解 | 三篇论文中的对应证据 |
| --- | --- | --- |
| LLM | 负责生成 token、Thought、Action、API call 或 reflection 的模型。模型本身不自动拥有环境、执行器或持久记忆。 | 三篇论文都把语言模型作为核心生成器，但没有把“模型”本身等同于完整系统。 |
| Tool-augmented LLM | 能够在生成中发出 API / tool call，并把结果纳入后续文本或 context；可以没有持续环境循环。 | Toolformer 明确关注 LM 如何学习 API 使用，并把自己定位为 LM。 |
| Agent | 有目标的运行时闭环：决策 → action/tool → environment 或 service → observation/feedback → 下一次决策。 | ReAct 最直接展示了单条 trajectory 的 interaction loop；Reflexion 又增加了跨 attempt 的反馈循环。 |
| Agentic workflow | 由外部程序或人为编排多个步骤、模型、工具和检查器的工作流；是否自治取决于它是否能基于状态持续作出决定。 | 这是当前知识库的系统抽象，三篇论文没有给出统一术语或完整分类。 |

当前最稳妥的边界是：

- **Tool use 是能力或接口，不是 Agent 的充分条件。**
- **ReAct 更接近 Agent interaction loop**，因为 Action 后的 Observation 会影响同一条 trajectory 中的下一次决策。
- **Reflexion 体现跨 attempt adaptation**，因为 Evaluator feedback 经过 reflection 后会改变下一次尝试的 context。
- **Toolformer 更适合作为 tool-augmented LM / learned tool-use policy 来理解**。论文证据不足以要求把它称为完整 Agent。

这个定义仍保持 `Status: evolving`：目前只有三篇论文，尚不足以覆盖 Planner、长期 Memory、复杂执行器、Multi-Agent 或安全边界的完整情况。

## 2. Reasoning vs Planning vs Reflection

三者都可能以语言形式出现，但作用时间和控制对象不同。

| 概念 | 主要发生位置 | 主要输入 | 主要输出 | 当前论文证据 |
| --- | --- | --- | --- | --- |
| Reasoning | 当前 attempt / 当前 step | 任务、context、Observation | Thought、推导、查询或下一步行动依据 | ReAct 将 Thought 与 Action、Observation 交错；Toolformer 的生成也会消费 API result。 |
| Planning | 当前或跨 step 的目标组织 | 目标、子目标、状态和约束 | 步骤、顺序、重规划建议 | ReAct 和 Reflexion 都支持 plan-like behavior，但没有显式 Planner component 或可验证计划状态。 |
| Reflection | 一次 trajectory 评估之后、下一次 attempt 之前 | trajectory、Evaluator feedback、已有 memory | 对错误的诊断、经验和下一次修正建议 | Reflexion 明确定义了 Self-Reflection → memory → next attempt。 |
| Internal model state | 模型内部、不可直接由文本等同推断 | 隐藏激活和模型状态 | 不等同于某一段生成文本 | 三篇论文都不足以证明 Thought 或 reflection 就是模型真实 hidden state。 |

更具体地说：

- **ReAct reasoning** 面向当前 trajectory：Thought 解释 Observation、分解目标、改写查询，并为下一次 Action 提供条件。
- **Reflexion reflection** 面向下一次 trajectory：它在当前尝试结束后读取结果，试图总结错误和改法。
- **Planning** 关注行动组织和子目标顺序。Reflection 可能产生重规划建议，但“建议了下一步”仍然不等于存在独立 Planner。
- **Reasoning trace** 是显式生成的语言产物；它可能有用、可读、可被反馈约束，但不能被当作 internal state 的透明窗口。

因此，目前 Concept 中应保留：

~~~text
Reasoning trace ≠ Internal model state
Plan-like behavior ≠ Explicit Planner architecture
Reflection ≠ Another name for within-step reasoning
~~~

## 3. Tool Use

当前知识库应把 Tool Use 视为一条可分开设计和评估的接口链，而不是某个单一算法：

~~~text
Tool selection
→ Invocation / serialization
→ Argument generation and validation
→ Tool execution
→ Observation / result integration
→ Continue, retry, chain, or finish
~~~

其中还存在一个跨层的 **tool-use policy**：模型或系统如何学会、被提示或被规划为在合适时机调用合适工具。

- **ReAct** 主要展示 runtime policy：模型在当前 context 中生成文本 Thought 和 Action，执行 Action 后读取 Observation，再继续 reasoning / acting。它的重点是工具或环境结果如何参与连续交互。
- **Toolformer** 主要展示 learned policy：候选 API call 被执行，以 future-token loss reduction 过滤有用调用，再通过自监督微调让 LM 学会生成 API 标记和参数。它的重点是调用行为如何被训练进模型，而不是提供完整的 runtime Agent。
- **Reflexion** 不是第三种 tool-selection 算法。它可以包裹使用 ReAct 或 Wikipedia API 的 Actor；它新增的是 trajectory 结束后的 Evaluator → Reflection → Episodic Memory，作用在跨 attempt adaptation 层。

因此，下面两种说法都不准确：

- “只要模型会调用 API，它就是 Agent。”
- “ReAct、Toolformer、Reflexion 都是在做同一种 Tool Use。”

更准确的拆分是：ReAct 研究运行时交互组织，Toolformer 研究训练得到的 API-use behavior，Reflexion 研究如何利用任务反馈改变后续尝试。三者可以在系统中组合，但当前论文没有验证一个统一的组合算法。

## 4. Observation, Feedback, and Grounding

### Observation

Observation 是当前 Action 或 tool execution 后返回给 Agent 的外部结果。它通常属于当前 trajectory，作用是让下一次 reasoning 不只依赖模型原有知识。ReAct 的核心闭环正是：

~~~text
Thought → Action → Observation → next Thought
~~~

Observation 可能改变环境状态，也可能只是提供外部信息；它不自动等于正确事实，仍可能为空、错误、冲突或被污染。

### Feedback

Feedback 是对一次行为或 trajectory 的结果信号，可以是成功 / 失败、标量、exact match、heuristic、编译结果、unit-test 结果或另一个模型的判断。它回答的首先是“结果如何”，未必直接回答“下一次应怎样做”。

Reflexion 把这种 feedback 交给 Self-Reflection，才把结果转成可供下一次使用的语言经验。因此：

~~~text
Feedback ≠ Reflection
Evaluation produces or interprets feedback
Reflection turns feedback into a possible next-attempt lesson
~~~

三篇论文形成了一个有用的 grounding 层次：

- ReAct 的 Observation grounding 约束**当前 trajectory**中的下一步。
- Reflexion 的 Evaluator feedback 约束**下一次 attempt**可能采用的策略。
- Toolformer 的 API result 被线性化并纳入文本生成；它可以帮助训练或继续预测，但论文明确没有解决可靠的 chained / interactive tool use。

这说明“结果进入 context”只是接口动作，不保证模型已经正确理解、验证或利用了结果。

## 5. Memory and State

### 当前可支持的层次

| 层次 | 保存什么 | 生命周期 | 当前论文证据 |
| --- | --- | --- | --- |
| Environment state | 外部环境中被 Action 改变的状态 | 由环境决定 | ReAct 的环境交互依赖它，但环境状态不是模型 Memory。 |
| Current context / trajectory history | 当前 attempt 的 Thought、Action、Observation 和状态历史 | 当前 trajectory / trial | ReAct 明确展示；Reflexion 也把 trajectory 视为 short-term memory。 |
| Working-memory-like context | 模型在当前 context 中可继续使用的任务事实、进度和子目标 | 当前输入窗口 | 是对 context 行为的解释，不是独立数据库或持久化模块。 |
| Episodic memory | 从一次经历总结出的 reflection / lesson | 跨 consecutive attempts；容量受限 | Reflexion 把 Self-Reflection 存入 memory 并在下一次 Actor generation 中读取。 |
| Persistent memory | 跨任务、跨会话且由外部存储保证的可检索信息 | 长期 / durable | 三篇论文没有实现或验证完整的 persistent memory architecture。 |
| Model parameters | 训练后固化的能力和调用倾向 | 训练生命周期 | Toolformer 通过微调改变 LM；Reflexion 明确不更新权重。参数变化不是运行时 episodic memory。 |
| Hidden internal state | 模型内部激活或未显式输出的状态 | 推理过程内部 | 不能由 Thought、Action 或 reflection 文本直接等同推断。 |

### 当前最重要的结论

有历史 context 不等于有 long-term memory。Reflexion 的 memory 进一步证明了“跨 attempt 保存语言经验”是一个有用的 episodic layer，但它仍然是 task-local、bounded 的机制，不等于现代完整 Agent 的存储、检索、压缩、冲突处理和生命周期管理。

需要同时区分：

- **State**：环境当前是什么状态。
- **Context**：本次生成看到了什么文本。
- **Memory**：哪些信息被专门保留并在后续阶段重新读取。
- **Internal state**：模型内部发生了什么，论文笔记不能从语言 trace 直接证明。

## 6. ReAct vs Toolformer vs Reflexion

三篇论文最适合被看作三个不同层次的贡献，而不是同一条方法的连续版本：

~~~text
Training layer:
Toolformer-like learned API-use behavior

Runtime inner loop:
ReAct-like reasoning ↔ action ↔ observation

Cross-attempt outer loop:
Reflexion-like evaluation → reflection → episodic memory
~~~

这张图是本次 Review 的跨论文抽象，不是任何一篇论文明确提出的组合架构。各自的边界是：

1. **ReAct** 解决如何把 reasoning 和 acting 放回环境交互中。它关心当前 trajectory 的决策如何被 Observation grounding。
2. **Toolformer** 解决 LM 如何从候选 API 调用和 future-token loss 中学习调用行为。它证明了 tool-augmented LM 的一种训练路线，但没有因此得到 Planner、persistent Memory 或完整 Agent runtime。
3. **Reflexion** 解决一次尝试得到任务反馈后，如何生成语言经验并影响下一次尝试。它不是把 ReAct 简单加上一个 Memory，而是新增了 Evaluator、Self-Reflection 和跨 attempt 的时间尺度。

可能的系统组合是：一个 learned tool-use policy 生成调用，运行在 ReAct-like 的交互轨迹中，失败后再由 Reflexion-like outer loop 处理反馈。但这只是合理的组合假设，不是当前三篇论文共同验证的结论。

## 7. Emerging Agent Architecture

### 跨论文后的最小抽象

~~~text
Task / Goal
    ↓
Current state
(environment observations + task context + optional memory)
    ↓
Reasoning / Decision
    ↓
Action / Tool invocation
    ↓
Environment / External service
    ↓
Observation / Tool result
    └──────────────→ updated trajectory context → next decision

End of attempt
    ↓
Evaluator / Feedback
    ↓
Optional Reflection
    ↓
Episodic memory
    ↓
Next attempt
~~~

### 哪些来自论文，哪些是抽象

- **来自 ReAct：** Thought、Action、Observation 的交错，以及 Observation 对下一步决策的 grounding。
- **来自 Toolformer：** tool selection / argument / textual API result 可以通过训练增强数据和 loss filtering 学习。
- **来自 Reflexion：** Evaluator、Self-Reflection、跨 attempt memory 和不更新参数的 verbal reinforcement。
- **跨论文抽象：** 将它们放进同一张两时间尺度图，以及把 tool-use policy 拆成 selection、invocation、execution、integration 的接口链。
- **尚未由当前资料证明：** 独立 Planner、统一 Executor、可靠权限系统、persistent memory、跨任务学习、Multi-Agent 协作和完整安全模型。

## 8. Common Misconceptions

### Thought = internal state

不成立。Thought 是显式生成的 reasoning trace，可以影响后续 context；它不是模型隐藏激活的直接报告。Reflection 也同样如此。（依据：[Reasoning](../../concepts/reasoning.md)、[ReAct note](../../papers/react/notes.md)、[Reflexion note](../../papers/reflexion/notes.md)）

### Tool use = Agent

不成立。Tool Use 只是外部能力接口。Toolformer 说明 LM 可以学习 API-use behavior，但论文并没有因此定义完整 Agent runtime。是否构成 Agent，还要看目标、持续决策、状态和反馈闭环。

### ReAct = explicit planning architecture

不成立。ReAct 的 Thought 可以表现出分解、顺序选择和下一步计划，但论文没有独立 Planner、计划验证器或 Planner-Executor 接口。当前应称为 plan-like reasoning / language-mediated planning behavior。

### Trajectory context = long-term memory

不成立。Trajectory history 主要是当前 context / short-term working context。Reflexion 的 episodic reflection 可以跨 attempt 保存，但仍有任务范围和容量边界；三篇论文都没有验证完整 persistent memory。

### Reflexion = gradient-based RL

不成立。Reflexion 使用 Evaluator feedback 生成语言经验并改变下一次 context，不更新模型参数。它借用 reinforcement 的反馈思想，但不是普通的 backpropagation 或参数级 RL。

### Reflexion = ReAct + memory

不够准确。Reflexion 的关键是 Evaluator → Self-Reflection → next attempt 的反馈转换机制；memory 只是承载 reflection 的一部分。它可以使用 ReAct 作为 Actor，但不要求所有 Reflexion 都是 ReAct，也不能把两者简单相加。

### All feedback = reflection

不成立。Observation、scalar reward、exact-match、test result 和 evaluator judgement 都是不同形式的反馈；只有经过特定的语言生成或总结步骤，才成为 reflection。Reflection 的质量还依赖 evaluator 和下一次 Actor 是否使用它。

## 9. What These Three Papers Do Not Yet Explain

- 如何构造有独立状态、可验证计划和重规划边界的 Planner-Executor architecture。
- 如何支持可靠的 structured tool calling、schema validation、权限、安全执行、成本控制和 chained / interactive use。
- 如何在大量任务和跨会话场景中存储、检索、压缩、遗忘并校验 episodic / semantic memory。
- 如何检测错误 Observation、错误 evaluator 或错误 reflection，避免错误经验在 trajectory 中累积。
- 为什么某些语言 reflection 有效、某些环境如高多样性 WebShop 无效，以及如何预测这种差异。
- 如何区分 reasoning、planning、reflection 对最终成功率的独立贡献。
- Multi-Agent 的角色分工、通信协议、共享 memory 和协作失败处理。
- Context Engineering 如何系统地控制长 trajectory、工具结果、reflection 和 token budget。
- Agent 的统一评测：如何分别测量调用决策、参数正确性、grounding、计划质量、反馈利用和长期恢复。

## 10. Open Questions

下面是本次 Review 的去重后状态；历史问题仍保留在 [notes/questions.md](../questions.md) 的原有阅读记录中。

1. **Agent 的边界是什么？**
   Status: Partially Answered。当前可用的工作定义要求目标驱动的持续决策和状态 / 反馈闭环；但 Agentic workflow 与 Agent 的边界仍需要更多架构论文。

2. **Tool-augmented LM 与 Agent 的边界是什么？**
   Status: Partially Answered。Tool use 不是充分条件；Toolformer 提供 LM-level evidence，ReAct 提供 runtime interaction evidence，但还没有统一判据。

3. **Reasoning 与 Planning 如何区分？**
   Status: Partially Answered。当前可以区分“中间推导”与“步骤组织”，但三篇论文没有显式 Planner，因此需要 Planner 类论文进一步补充。

4. **Reasoning 与 Reflection 有什么本质差别？**
   Status: Partially Answered。当前按时间尺度区分：reasoning 服务当前 step，reflection 服务下一次 attempt；与 critic、self-correction 的边界仍开放。

5. **Feedback 如何转化为有效 Reflection？**
   Status: Open。Evaluator 的可靠性、错误归因、语言反馈的可执行性和可迁移性还没有被独立解释。

6. **Memory 应该保存什么、保存多久、何时读取？**
   Status: Partially Answered。当前已有 working context 与 task-local episodic memory 的区分，但 persistent / long-term memory 的检索、压缩和冲突处理仍开放。

7. **Agent 如何避免错误 Observation / Reflection 累积？**
   Status: Open。现有论文展示了失败恢复，但没有给出通用的 provenance、验证、淘汰或安全更新机制。

8. **Tool-use policy 应该通过 prompt、training 还是 planning 获得？**
   Status: Partially Answered。ReAct 代表 runtime prompting / trajectory，Toolformer 代表 training-time learned policy，Reflexion 是反馈后的外层修正；三者的成本、迁移和组合关系仍未解决。

9. **如何可靠支持 chained tool use 和 interactive search？**
   Status: Open。Toolformer 和 ReAct 的笔记都指出了相关边界，但当前资料没有给出统一解决方案。

10. **如何评估一个 Agent 真正学到了什么？**
    Status: Open。需要把 Actor、tool policy、Evaluator、Reflection、Memory 和环境执行质量拆开评估，而不是只看最终成功率。

## 11. Next Learning Priorities

基于当前缺口，下一阶段优先学习以下四个主题；这里只确定方向，不提前加入论文：

1. **Explicit Planning and Replanning**：Planner–Executor、层级子目标、计划验证、失败后的重规划和计划质量评估。
2. **Memory Architectures**：working context、episodic / semantic memory、检索、压缩、持久化、冲突和错误记忆治理。
3. **Structured Tool Calling and Execution**：schema、参数校验、权限、错误恢复、交互式 / 链式工具调用和成本感知。
4. **Reflection, Critic, and Self-Correction**：区分 feedback、evaluation、critic、reflection，研究语言反馈何时有效以及如何防止错误放大。
5. **Context Engineering for Agents**：长 trajectory、工具结果、memory、reflection 的编排、裁剪和 token budget 管理。

Multi-Agent 和更完整的 Agent Architecture 暂放在上述单 Agent 基础之后，避免在当前概念尚未稳定时过早扩展范围。
