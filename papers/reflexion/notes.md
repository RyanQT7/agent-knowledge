# Reflexion: Language Agents with Verbal Reinforcement Learning

## 1. Metadata

- Title: Reflexion: Language Agents with Verbal Reinforcement Learning
- Authors: Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, Shunyu Yao
- Year: 2023
- Venue: 37th Conference on Neural Information Processing Systems (NeurIPS 2023)
- URL / DOI: Code repository: https://github.com/noahshinn024/reflexion; DOI: Unclear / Not explicitly stated in the paper
- Local File: [Reflexion.pdf](../../sources/papers/Reflexion.pdf)

## 2. One-Sentence Summary

Reflexion 在不更新模型参数的前提下，让 Actor 根据一次 trajectory 的任务反馈生成语言化 reflection，把它保存到跨尝试的 episodic memory，并在下一次尝试时作为额外 context 使用，从而实现一种 verbal reinforcement loop。（Source: Abstract; Sec. 1; Sec. 3）

## 3. Problem

论文要解决的问题不是“让 LLM 产生一次更长的答案”，而是让语言 Agent 能够根据失败或低分的任务反馈改进后续尝试。传统 reinforcement learning 往往需要大量交互样本和昂贵的模型微调；而仅仅重新运行同一个 Actor，并不会自动把失败轨迹转化为下一次可执行的经验。（Source: Abstract; Sec. 1）

Reflexion 因此关注一个跨尝试的问题：

> 给定一次 trajectory、稀疏的成功/失败或标量反馈，以及有限的后续 context，Agent 如何形成能指导下一次尝试的经验？

这里的“学习”是推理时的语言反馈和上下文适应，不是把反馈通过梯度写回模型权重。（Source: Abstract; Sec. 1; Sec. 3）

## 4. Motivation

下面的对照用于解释论文动机；它不是论文在所有任务上统一实现的三种 baseline。

| 方式 | 能做什么 | 跨尝试的不足 |
| --- | --- | --- |
| Reasoning-only，例如 CoT | 在一次生成中展开中间推理；在有 ground-truth context 时可以隔离推理能力 | 如果没有额外机制把失败原因写回下一次输入，重新尝试不一定会变好。HotPotQA 中 CoT-only 和 CoT(GT)-only 在失败任务上没有显示出跨 trial 的概率性改进。（Source: Sec. 4.2） |
| Action-only 或无 reflection 的重试 | 可以执行动作并在失败后 reset 环境 | 只 reset 并不会总结“哪一步错了、下次应怎样改”。ALFWorld 的无 reflection baseline 会重新开始，但 ReAct-only 的改进在第 6–7 次 trial 间趋于停滞。（Source: Sec. 4.1） |
| ReAct | 在单条 trajectory 内交错 Thought、Action 和 Observation，使动作受到环境反馈约束 | ReAct 解决的是单次运行时的 reasoning–acting 闭环；Reflexion 进一步加入 evaluator、reflection 和跨 trial memory，把一条失败轨迹转成下一次的提示。这里的边界是基于两篇论文的综合理解，不应写成“ReAct 本身没有任何重试能力”。（Source: ReAct paper note; Sec. 3; Sec. 4） |

论文的关键动机是：如果不能或不希望更新参数，可以把稀疏 reward 转成自然语言的、与当前任务相关的经验。作者把这种语言反馈类比为一种 “semantic gradient signal”，但这个比喻不等于 gradient-based training。（Source: Sec. 1）

## 5. Core Idea

**Paper states:** Reflexion 的核心是一个外层的“评估—反思—记忆—再尝试”循环：

1. Actor 完成一次任务尝试并产生 trajectory。
2. Evaluator 根据任务反馈给出成功/失败或分数。
3. Self-Reflection model 读取 trajectory、反馈和已有 memory，生成一段语言化的经验。
4. 这段 reflection 被追加到 memory。
5. 下一次 Actor 在生成 trajectory 时读取 memory，从而改变行动、推理或实现。

（Source: Sec. 3.1; Sec. 3.2; Algorithm 1）

**My interpretation:** Reflexion 不把失败压缩成一个只有正负号的 reward，而是把它转成对“哪里出错、错误如何导致后续失败、下一次应该尝试什么不同动作或策略”的语言经验。语言 feedback 由模型在下一次推理时消费，因此它改变的是可见的 task context / episodic experience，而不是模型参数。（Source: Sec. 1; Sec. 3; Appendix B; Appendix D）

## 6. Architecture / Workflow

### 6.1 Outer loop

~~~text
Task / Environment
→ Actor generates trajectory τ_t
→ Evaluator produces feedback r_t
→ Self-Reflection generates sr_t
→ Append sr_t to memory
→ Actor starts the next trial with memory
→ Success or trial limit
~~~

在论文的算法描述中，先生成初始 trajectory、评估并得到初始 reflection；随后每个 trial 都重新生成 trajectory、评估、生成 reflection 并追加 memory，直到 Evaluator 判定通过或达到试验上限。（Source: Sec. 3.2; Algorithm 1）

### 6.2 Inner trajectory

当 Actor 使用 ReAct 时，一次 trajectory 内的流程可以写成：

~~~text
Task
→ Thought / Reasoning
→ Action
→ Observation
→ Thought / Reasoning
→ Action
→ ...
→ Final Answer or Completed Action
~~~

- **Thought / Reasoning**：把当前目标、已知事实、错误迹象或下一步计划表达为语言，并为下一次 action 提供条件。
- **Action**：向环境或工具执行动作；它可能改变环境状态，也可能请求外部信息。
- **Observation**：动作执行后的外部返回值。它是下一轮 reasoning 的 grounding，而不是 reflection memory 本身。
- **Final Answer / Completion**：结束当前 trajectory，随后由 Evaluator 判断是否成功。

因此 Reflexion 和 ReAct 不是同一层的机制：ReAct 描述一次 trajectory 内如何交错 reasoning 和 acting；Reflexion 描述 trajectory 结束后如何利用反馈影响下一次 attempt。（Source: ReAct paper note; Sec. 3; Sec. 4.1–4.2）

### 6.3 Reflection 的来源、内容和作用

**来源。** Reflection 由任务反馈触发，但反馈并不只有一种形式。论文允许使用外部或内部模拟的 feedback，可为 binary / scalar reward；具体实验中 Evaluator 包括 exact-match、手写 heuristic、LLM 评估，以及编译器、解释器和 unit tests。（Source: Abstract; Sec. 3.1; Sec. 4.1–4.3）

**内容。** Reflection 不是固定的数值标签，而是与 trajectory 和 feedback 相关的自然语言经验。它可以包含：

- 对错误步骤或错误答案的诊断。
- 对后续失败的因果归因或 credit assignment。
- 下一次应改变的动作、查询、顺序、实现或答案范围。
- 对任务目标和已观察事实的提醒。

例如 Appendix B 的 decision-making 例子中，reflection 指出应先找到 lamp 再处理 mug；Appendix D 的例子中，reflection 修正了错误的搜索对象或答案范围。（Source: Appendix B, Fig. 5; Appendix D）

**作用。** Reflection 被追加到 memory，Actor 在下一次尝试时读取它。它不是在当前 action 之后直接替代 Observation，也不是模型的隐藏 internal state；它是显式生成的语言 trace / experience，作为下一次生成的 context。（Source: Sec. 3.1; Sec. 3.2）

### 6.4 Three-model view

论文把方法拆成三个角色：

| 角色 | 作用 |
| --- | --- |
| Actor | 给定状态观察和 memory，生成行动或 reasoning trajectory。论文在不同任务中使用 CoT 或 ReAct 等 Actor。 |
| Evaluator | 对 Actor trajectory 评分。Reasoning 任务可用 exact match，decision-making 可用 heuristic，编程任务可用 LLM、compiler、interpreter 或 tests。 |
| Self-Reflection | 读取 trajectory、反馈和已有 memory，生成可供后续 trial 使用的 verbal reinforcement。 |

这些是论文用于描述方法的三个功能角色；具体 Evaluator 的实现会随任务改变。（Source: Sec. 3.1; Sec. 4）

## 7. Key Concepts

- [Agent](../../concepts/agent.md)：Actor、Evaluator 和环境反馈构成跨尝试的 Agent loop；但论文中的“language agent”不应被理解为模型单独拥有所有外部能力。
- [Reasoning](../../concepts/reasoning.md)：reflection 是 trajectory 之后的语言反馈层，帮助后续 reasoning 使用失败经验。
- [Memory](../../concepts/memory.md)：当前 trajectory 是短期 context，self-reflection 被保存为跨 trial 的 episodic memory；论文称后者为 long-term memory，但实现是有容量上限的任务内记忆。
- [Reflection](../../concepts/reflection.md)：论文提供了一个 evaluator → verbal feedback → next attempt 的具体闭环。
- [Planning](../../concepts/planning.md)：reflection 可以建议不同的动作顺序或策略，但这不等于存在显式 Planner。
- [Tool Use](../../concepts/tool-use.md)：Reflexion 可以包裹使用 ReAct 或 Wikipedia API 的 Actor；其核心增量是反馈和 memory，不是学习何时调用工具。

## 8. Method

### 8.1 Policy without parameter update

论文将 Actor 的行为表示为依赖当前 observation 和 memory 的 policy。每次 trial 结束后，Evaluator 给出反馈，Self-Reflection 生成一条反思并放入 memory；下一次 Actor 的输入因此发生变化。作者把这个过程称为通过 verbal experience 进行 policy optimization。（Source: Sec. 3.1; Sec. 3.2）

这里需要明确区分两种“学习”：

| 机制 | Reflexion 中是否发生 |
| --- | --- |
| 通过 loss、backpropagation 或 RL 更新模型参数 | **不发生**。论文明确强调不更新模型权重。（Source: Abstract; Sec. 1） |
| 通过语言 feedback 改变下一次 inference 的输入和行为 | **发生**。reflection 被写入 memory，并在下一次 Actor generation 中被读取。（Source: Sec. 3.1–3.2） |

所以 “verbal reinforcement” 更接近 in-context adaptation / episodic feedback，而不是普通的 gradient-based training。它可以让同一个冻结的模型在当前任务的连续尝试中改变行为，但不代表模型从此永久学会了该技能。

### 8.2 Memory lifecycle

论文对 memory 做了明确的短期—长期区分：

- **Working context / short-term memory**：当前 trajectory 的历史，包括状态、动作、观察和 reasoning。它支撑当前 trial 内的连续决策。
- **Episodic memory**：Self-Reflection 输出的经验，跨越当前 trial 保存，并在下一次尝试前提供给 Actor。
- **Persistent / durable long-term memory**：如果指跨任务、跨会话、由外部存储保证的持久记忆，论文并没有建立这样的系统。论文把反思称为 long-term memory，但实际通常只保留最近 1–3 条；编程实验使用 1 条，HotPotQA 使用 3 条，ALFWorld 截断为最近 3 条。（Source: Sec. 3.1; Sec. 4.1–4.3）

生命周期可以概括为：

~~~text
Current trajectory
→ Evaluator feedback
→ Self-Reflection summary
→ Append to task memory
→ Read by Actor on next trial
→ Drop when the bounded memory window is exceeded
~~~

（Source: Sec. 3.1; Algorithm 1; Sec. 5）

**My interpretation:** Reflexion 证明的是 task-local、bounded、跨 attempt 的 episodic context 能够影响后续行为；它没有证明一个跨用户、跨任务或跨会话的 persistent memory system，也没有说明如何进行向量检索、冲突解决或长期压缩。

### 8.3 Task-specific evaluators

Evaluator 不是一个固定的通用 critic。它可以使用：

- reasoning 任务的 exact-match grading；
- decision-making 任务的 LLM binary classification 或手写 heuristic；
- 编程任务的 compiler / interpreter / unit tests，并在部分设置中使用 LLM 评价代码。

这使得 Reflexion 能把不同形式的任务反馈转换为相同的语言 memory 接口，但也意味着改进质量依赖 evaluator 是否能识别真正的错误。（Source: Sec. 3.1; Sec. 4.1–4.3）

## 9. Experiments

### 9.1 ALFWorld

- **Dataset / Environment:** 134 个环境，覆盖 hidden objects、moving objects 和 manipulating objects 六类任务设置。（Source: Sec. 4.1）
- **Actor:** 使用 ReAct action generator。
- **Evaluator / feedback:** LLM 自然语言二分类和手写 heuristic。Heuristic 在相同 action 和 response 循环超过 3 次，或 action 数超过 30 时触发 reflection。（Source: Sec. 4.1）
- **Baseline:** reflection 被建议时跳过 reflection、reset 环境并开始新 trial。
- **Metric:** 任务完成 / success。
- **Main result:** ReAct + Reflexion 在简单 heuristic 下完成 130/134 个环境；在 12 次连续 trial 中还能学习额外任务。ReAct-only 的性能提升在第 6–7 次 trial 间停止，失败分析中其 hallucination rate 收敛到 22%，没有长期恢复。（Source: Sec. 4.1）

这个实验说明，Reflection 可以把“我错误地认为已经拥有物体”这类失败模式提炼成下一次的 self-hint；它并不说明每一种环境错误都能被语言反思修复。（Source: Sec. 4.1）

### 9.2 HotPotQA

- **Dataset:** 约 113k 个多跳问题，需要跨 supporting documents 推理。（Source: Sec. 4.2）
- **Baselines / settings:** CoT 使用 6-shot，ReAct 和 self-reflection prompt 使用 2-shot；另设带 ground-truth context 的 CoT(GT) 作为控制设置，并用 Wikipedia API 支持 ReAct。（Source: Sec. 4.2）
- **Metric:** exact-match；失败任务在后续 trial 重试，memory size 为 3；实验还报告 temperature 0.7 下无 reflection baseline 的跨 trial 表现。（Source: Sec. 4.2）
- **Main result:** Reflexion 在没有 ground-truth answer context 的情况下将准确率提升 14%；加入 episodic memory 但不做标准 reflection 的 ablation 之后，reflection 仍带来额外 8 个百分点的提升。（Source: Sec. 4.2; Fig. 4）
- **Context control:** CoT(GT) 因为直接得到 ground-truth context 表现更高，但仍有 39% 的问题无法推断出正确答案；Reflection 可以在没有该 ground-truth context 的设置中改善结果。（Source: Sec. 4.2）

Appendix A 的 Table 5 进一步报告了不同模型和 Actor 的 before → after 结果，例如 CoT(GT)+text-davinci-003 为 0.60 → 0.77，ReAct+gpt-4 为 0.39 → 0.51；这些数值说明提升依赖模型和设置，不能概括成一个与模型无关的固定增益。（Source: Appendix A, Table 5）

### 9.3 Code generation

- **Benchmarks:** HumanEval、MBPP、Leetcode Hard Gym；覆盖 Python 和 Rust，Rust 使用 MultiPL-E。Leetcode Hard Gym 包含 40 个 hard questions。（Source: Sec. 4.3）
- **Feedback mechanism:** compiler / interpreter 和自动生成的 diverse unit tests。测试通过 AST 过滤语法有效样本，最多采样 6 个；Actor prompt 读取上一版实现、unit-test 结果和 reflection，只输出改进后的 function body。（Source: Sec. 4.3; Appendix C）
- **Main results:** Table 1 报告 HumanEval Python 91.0% vs GPT-4 80.1%，MBPP Python 77.1% vs GPT-4 80.1%，HumanEval Rust 68.0% vs 60.0%，MBPP Rust 75.4% vs 70.9%，Leetcode Hard Python 15.0% vs 7.5%。论文说明除 MBPP Python 外，Reflexion 在列出的 Python / Rust benchmark 上超过对应 GPT-4 对照。（Source: Sec. 4.3; Table 1）
- **Test-quality result:** Table 2 把 TP、FN、FP、TN 定义为测试是否通过与 solution 是否真正通过的组合；MBPP Python 的 false-positive rate 为 16.3%，HumanEval Python 为 1.4%，这帮助解释了 MBPP Python 中 reflection 的效果较弱。（Source: Sec. 4.3; Table 2）
- **Ablation:** 在 50 个最难的 HumanEval Rust 问题上，Table 3 报告 test generation 和 reflection 同时开启时为 0.68；两者都关闭为 0.60；只开 reflection 为 0.52；只开 test generation 为 0.60。作者据此说明，缺少测试时 Agent 难以判断正确性，而缺少 reflection 时即使测试发现错误，实现也不一定能利用这些指示修复。（Source: Sec. 4.3; Table 3）

### 9.4 Additional examples and negative result

- Appendix B 的 decision-making example 展示：第一次先找到 mug、再错误使用 desklamp；reflection 提议先找到 lamp，第二次按该顺序成功。（Source: Appendix B, Fig. 5）
- Appendix D 的 ReAct + Reflexion example 展示错误搜索对象被 reflection 修正；CoT + Reflexion 和 CoT(GT) + Reflexion examples 展示 reflection 也可以修正答案范围或问题所要求的抽象层级。（Source: Appendix D）
- WebShop 的 100 个环境实验中，2-shot ReAct + Reflexion 在最多 4 个 trial 后没有显著超过 ReAct；论文将原因归因于高多样性环境中的探索困难和 reflection 无法提供足够帮助。（Source: Appendix B.1）

## 10. Strengths

- **把稀疏反馈变成可操作经验。** Reflection 不只保存 success / failure，而是尝试描述错误原因和下一次修正方向。（Source: Sec. 1; Sec. 3; Appendix B）
- **不依赖参数更新。** 同一个冻结模型可以在连续 trial 中利用 task-specific context 改变行为，降低了传统 RL 微调的门槛。（Source: Abstract; Sec. 1）
- **接口具有任务通用性。** Evaluator 可以提供 binary、scalar 或其他任务反馈，Self-Reflection 再把它们统一成语言 memory；论文在环境决策、知识问答和代码生成上验证了这一点。（Source: Abstract; Sec. 3; Sec. 4）
- **错误过程相对可诊断。** 生成的 reflection 是显式文本，作者在 broader impact 中认为它有助于 interpretability / diagnosability，也可用于监控 Agent 的 tool intent；这属于作者的主张，不能扩大为已证明的 faithful explanation。（Source: Sec. 6）

## 11. Limitations

### 论文作者明确指出的限制

- 自然语言 policy optimization 可能落入非最优 local minima。（Source: Sec. 5）
- 当前 long-term memory 是 sliding window，容量有限；作者提出未来可以研究 vector embedding database 或 SQL database。（Source: Sec. 5）
- 代码测试对 nondeterministic generators、impure API functions、hardware-dependent outputs 以及 parallel / concurrent behavior 覆盖不足。（Source: Sec. 5）
- WebShop 的高多样性和探索需求使 reflection 没有带来显著收益。（Source: Appendix B.1）
- 为了可复现和安全，论文强调 autonomous code-writing 应隔离执行环境，因为生成代码在执行前没有被完全验证。（Source: Sec. 8）

### 基于论文的进一步判断

- Reflection 的质量依赖 Evaluator 和 Self-Reflection model；错误的 evaluator feedback 可能产生错误的经验，但论文没有给出一个独立、通用的 reflection faithfulness 评估。
- “long-term memory”在本文实现中是有容量上限的 task-local episodic memory；它不等于跨任务、跨会话的 durable memory。
- 语言 reflection 改变的是下一次 context 中的条件，不等于模型已经获得参数层面的新能力；要把这种短期改进迁移到新任务，论文证据不足。
- Reflection 可以表现出纠错和 plan-like behavior，但论文没有定义一个独立的 Planner、可验证计划状态或显式执行器，因此不能把 Reflexion 直接等同于 Planner-Executor 架构。

## 12. Relationship to Existing Knowledge

### 12.1 ReAct vs Reflexion

| 维度 | ReAct | Reflexion |
| --- | --- | --- |
| 核心作用域 | 单条 trajectory 内交错 Thought、Action、Observation。 | 在 trajectory 外增加评估、语言 reflection、memory 和下一次 attempt。 |
| 主要反馈 | Action 后立即得到 Observation，约束下一步 reasoning / action。 | 当前 trial 结束后得到 evaluator feedback，生成可跨 trial 使用的经验。 |
| 信息保存 | 当前 trajectory context 中的历史 Thought、Action、Observation。 | 在此基础上保存 Self-Reflection；论文把 trajectory 称为 short-term、reflection 称为 long-term，但实际容量通常只有 1–3。 |
| 是否更新参数 | ReAct 基础方法不要求参数更新。 | 明确不更新模型权重；通过 context / memory 改变后续 inference。 |
| 架构结论 | 是一种 reasoning–acting 运行时范式，不自动包含独立 Planner 或 persistent Memory。 | 是一种可包裹在 Actor 外层的 verbal reinforcement loop，不应简化为 ReAct + Memory。 |

因此，ReAct 与 Reflexion 的关系更准确地说是：Reflexion 可以把 ReAct 当作 Actor 的单次 trajectory 生成方式，再在其外面增加“评估—反思—再尝试”；它的新增机制是跨 attempt 的反馈利用，而不是把 ReAct 的 Thought 改名为 reflection。（Source: ReAct paper note; Sec. 3; Sec. 4.1–4.2）

### 12.2 Toolformer vs Reflexion

| 维度 | Toolformer | Reflexion |
| --- | --- | --- |
| 核心问题 | 模型如何学习何时调用哪个 API、传入什么参数，并把结果插入生成。 | 一次尝试失败或得分后，如何生成语言 feedback 并改进下一次尝试。 |
| 学习信号 | 候选 API call 执行后带来的 future-token loss reduction，用于自监督筛选和微调。 | Evaluator 的任务反馈、trajectory 和 memory 生成 verbal reinforcement。 |
| 调用 / 反馈表示 | 文本化 API 标记和 inline result。 | Self-Reflection 文本写入 memory；如果 Actor 使用工具，工具 Observation 仍属于内层 trajectory。 |
| 时间尺度 | 主要在训练阶段学习 call policy，推理时生成 learned API tokens。 | 主要在推理时跨 consecutive trials 使用 episodic feedback，不更新参数。 |
| Agent 边界 | 论文将其定位为 LM；会调用 API 不足以证明完整 Agent runtime。 | 论文称 language agents，但具体系统依赖 Actor、Evaluator、环境和 memory；不能把模型单独等同于完整自治 Agent。 |

两者可以组合，但不是同一种 Agent 架构：Toolformer 解决 tool-use policy 的学习，Reflexion 解决基于任务反馈的后续行为改进。（Source: Toolformer paper note; Toolformer Sec. 2, Sec. 5–6; Reflexion Sec. 3）

### 12.3 Agent、planning、memory 和 internal state 的边界

- 论文使用 “language agents” 描述整体方法；有 Actor、Evaluator、Self-Reflection、memory 和环境的组合时，可以称为一种 Agent architecture / loop。仅凭一个 LLM 生成 reflection，不能推出它独立拥有环境执行、持久记忆或完整规划能力。（Source: Abstract; Sec. 3）
- Reflection 可能提出替代动作、查询、顺序或答案范围，因此表现出 plan-like correction；这不是显式 Planner architecture。相关边界见 [Planning](../../concepts/planning.md)。
- Thought、trajectory 和 reflection 都是显式生成或拼接到 context 的语言内容；它们可以影响行为，但不等价于模型真实的 hidden internal state。（Source: Sec. 3; Appendix D）
- 本文的 memory 是跨 trial 的受限 episodic context，不应因为论文使用 long-term 一词就直接归类为 persistent long-term memory。（Source: Sec. 3.1; Sec. 5）

## 13. My Understanding

我把 Reflexion 理解为一个位于 Agent 单次执行 loop 之上的“语言化错误回放层”。ReAct 让 Agent 在一次任务轨迹中通过 Observation 及时修正下一步；Reflexion 则等一次尝试结束，要求系统把 trajectory 和结果压缩成一条可复用的经验，再把这条经验带入下一次尝试。

它真正改变的是下一次推理的输入条件：Actor 看到了一条新生成的、任务相关的语言提示，所以可能选择不同动作、改变搜索顺序、修正答案粒度或修改代码。模型参数没有变化，reflection 也不是模型隐藏状态的直接读出。因而“从失败中学习”在这里应理解为 bounded in-context / episodic adaptation，而不是永久的 parameter learning。

这篇论文对 Agent 知识体系的价值在于把几个经常混淆的层次拆开：

~~~text
Within one attempt:
Reasoning → Action → Observation

Across attempts:
Trajectory + Feedback → Reflection → Episodic Memory → Next Attempt
~~~

它还显示，是否有效不只取决于 Actor 会不会推理或调用工具，也取决于 Evaluator 能否发现错误、Reflection 能否提出可执行的修正、Memory 能否在有限 context 中保留最有用的经验。

## 14. Questions

### 论文未解决或明确暴露的问题

- 自然语言 policy optimization 如何避免非最优 local minima？（Source: Sec. 5）
- 更大的、可检索的 memory 如何替代当前 sliding-window memory？（Source: Sec. 5）
- 在 nondeterministic、impure、hardware-dependent 或并发代码任务中，如何获得可靠 feedback？（Source: Sec. 5）
- 为什么 Reflexion 在 WebShop 的高多样性探索中没有显著超过 ReAct？（Source: Appendix B.1）

### 基于论文进一步产生的问题

- 错误的 reflection 是否会造成后续 trajectory 的反馈回路，使 Agent 越来越偏？
- 为什么自然语言 reflection 能在某些任务中充当有效的 credit-assignment signal？它与 critic、self-correction 或其他 verbal feedback 方法的本质差异是什么？
- 在长期运行的 Agent 中，应该保存原始 trajectory、reflection summary，还是二者的可验证压缩形式？
- 如何把本文 task-local episodic memory 扩展到跨任务、跨会话的 persistent memory，同时控制错误传播？
- 能否分别评估 Actor、Evaluator、Self-Reflection 和 Memory 的贡献，而不把它们的效果混成一个最终成功率？

这些问题已同步到 [Open Questions](../../notes/questions.md)；论文事实与进一步解释在其中分开记录。

## 15. Related Work

- [ReAct: Synergizing Reasoning and Acting in Language Models](../react/notes.md)：Reflexion 可以使用 ReAct 作为 Actor 的单次 reasoning–acting trajectory，并在外层增加跨 trial 的 feedback loop。
- [Toolformer: Language Models Can Teach Themselves to Use Tools](../toolformer/notes.md)：两者都讨论 LLM 与外部能力的结合，但 Toolformer 的核心是学习 API call policy，Reflexion 的核心是利用任务反馈改进下一次行为。
- Chain-of-Thought：论文用 CoT 作为部分任务的 Actor / baseline，用于比较 reasoning-only 与带 reflection 的跨 trial 改进。（Source: Sec. 4.2–4.3）
- 传统 reinforcement learning：Reflexion 借用 reinforcement 的“根据反馈改进行为”视角，但把更新载体从参数梯度换成自然语言经验。（Source: Sec. 1; Sec. 3）

## 16. Useful Quotes / Definitions

- “verbal reinforcement”：论文对方法的核心命名；指把任务反馈转成自然语言经验，而非直接更新权重。（Source: Title; Abstract）
- “semantic gradient signal”：作者对 reflection 作用的类比；应理解为帮助下一次 policy 方向选择的语言提示，不是数学意义上的 gradient。（Source: Sec. 1）
- **Trajectory / short-term memory：** 当前尝试中累积的历史状态、动作、观察和 reasoning。（Source: Sec. 3.1）
- **Self-Reflection / long-term memory：** 从 trajectory 与反馈生成并跨 trial 保存的语言化经验；本文实现受 sliding-window 容量限制。（Source: Sec. 3.1; Sec. 5）

## 17. Tags

reflexion, verbal-reinforcement, reflection, episodic-memory, in-context-adaptation, agent, reasoning, feedback, error-recovery, tool-use
