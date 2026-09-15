# ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models

## 1. Metadata

- Title: ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models
- Authors: Binfeng Xu, Zhiyuan Peng, Bowen Lei, Subhabrata Mukherjee, Yuchen Liu, Dongkuan Xu
- Year: 2023
- Venue: Preprint under review; a formal venue is not stated in the local PDF
- URL / DOI: The local PDF does not explicitly provide an arXiv identifier or DOI. Code: https://github.com/billxbf/ReWOO
- Local File: [ReWOO.pdf](../../sources/papers/ReWOO.pdf)

## 2. One-Sentence Summary

ReWOO separates foreseeable language reasoning from tool observations with a Planner–Worker–Solver pipeline: the Planner writes a blueprint with evidence placeholders, Workers execute the corresponding tools, and the Solver combines plans with collected evidence.

**Source:** Abstract; Fig. 1; Sec. 2.1.

## 3. Problem

ReWOO 试图解决 augmented language model 中由 Thought–Action–Observation 交错产生的效率和鲁棒性问题。ReAct 风格的系统每完成一个工具调用，就把历史 prompt、示例、thought、action 和 observation 再次放入下一次 LLM 调用；随着 trajectory 变长，输入中会重复大量 token。

论文将这种结构描述为 observation-dependent reasoning：模型必须停止当前生成，等待工具结果，再根据包含全部历史的 context 生成下一步。这样既带来随步骤增长的 token redundancy，也会使工具失败或过长 context 影响后续 reasoning。（Source: Abstract; Sec. 1; Sec. 2.2; Appendix A）

ReWOO 的目标不是证明所有观察都不重要，而是把其中一部分可以预先推断的 reasoning 从 tool feedback 中解耦出来，在工具执行前先形成一组有依赖关系的计划，再集中处理 evidence。（Source: Sec. 1; Sec. 2.1）

## 4. Motivation

论文对三种相关范式的分工可以这样理解：

- **Direct Prompt：** 不显式使用多步 reasoning 或工具，成本低但无法稳定获得外部证据。
- **CoT：** 可以生成 verbal reasoning，但不调用外部工具；面对需要最新知识或精确计算的问题会受限。
- **ReAct / observation-interleaved ALM：** 能根据中间 Observation 调整下一步，但每一步都重复上下文并等待工具，带来 token 和 latency 成本。
- **ReWOO：** 把可预见的 reasoning 先生成成 blueprint；Worker 再执行工具并收集 evidence，Solver 最后基于完整 plans/evidence 作答。

论文还指出，Toolformer 的独立 API sampling 对多步工具使用并不可靠，而仅把完整 Thought–Action–Observation 轨迹用于微调也不一定能泛化到新任务和工具集。ReWOO 的模块化结构为 Planner 的 specialization 和 Solver / Worker 的独立优化提供了接口。（Source: Sec. 2.3）

## 5. Core Idea

用自己的语言解释，ReWOO 把一次 augmented reasoning 拆成三个相对独立的阶段：

1. **Planner：** 只看任务、工具描述和示例，生成连续的 Plan，并为每个需要外部证据的步骤分配一个 evidence variable，例如 #E1。后续 Plan 可以引用较早的 evidence。
2. **Worker：** 按每个 evidence variable 执行对应工具调用，收集 evidence；Worker 不负责重新组织完整 reasoning blueprint。
3. **Solver：** 将原问题、Planner 生成的 plans 和 Worker 收集的 evidence 一起读入，谨慎解决任务并输出答案。

最核心的解耦是：Planner 在生成 blueprint 时不等待具体 tool observation；工具结果在后续由 Worker 批量或按计划填充，最后由 Solver 将预先推理与实际证据对齐。它不是“完全不使用 Observation”，而是“在 Planner 阶段不依赖 Observation”，并把 evidence integration 延迟到 Solver。（Source: Abstract; Fig. 1–2; Sec. 2.1）

## 6. Architecture / Workflow

ReWOO 的主流程可以表示为：

~~~text
Task + Context + Exemplars
→ Planner: Plan 1 → #E1, Plan 2 → #E2, ...
→ Worker: execute tools for #E1, #E2, ...
→ Evidence: E1, E2, ...
→ Solver: combine Task + Plans + Evidence
→ Final Answer
~~~

与 ReAct 的核心差异是，ReWOO 的 Planner 先输出完整的 foreseeable reasoning blueprint；它不会在每一个 Plan 后暂停等待 observation，再决定下一个 Plan。Worker 负责工具执行，Solver 负责在 evidence 到来后解释、纠正或补偿 Planner / Worker 的错误。（Source: Fig. 1–2; Sec. 2.1; Appendix B）

后续 Plan 可以引用前面生成的 evidence variable，因此 ReWOO 不是简单地把所有工具调用无序并行化。它保留了计划内部的依赖表达；但真正的 evidence 只有在 Worker 执行后才产生。（Source: Sec. 2.1; Appendix B）

论文没有把 Planner 明确定义为独立的 formal planner 或 classical planning solver。Planner 输出的是自然语言 plans 与 evidence placeholders，计划是否充分、可执行和正确仍取决于语言模型、工具结果与 Solver。（Cross-paper interpretation; Source: Sec. 2.1–2.2）

## 7. Key Concepts

- [Planning](../../concepts/planning.md)
- [Reasoning](../../concepts/reasoning.md)
- [Tool Use](../../concepts/tool-use.md)
- [Agent](../../concepts/agent.md)
- [Context Engineering](../../concepts/context-engineering.md)

## 8. Method

### 8.1 Plan–Work–Solve

Planner 输出若干连续的 Plan–evidence variable 对。特殊变量 #E 表示 Worker 要填入的 evidence；后续 Plan 可以使用之前的 #E。Worker 根据变量对应的自然语言请求调用 Wikipedia、Google、WolframAlpha、LLM、Calculator、SearchDoc 等工具。Solver 最后读取 plans 与 evidence，论文要求 Solver 对 evidence 保持谨慎，因为结果可能无关、过长或不能支持 Planner 的预期。（Source: Sec. 2.1; Sec. 3.1; Appendix B）

Solver 的 prompt 允许它处理简单问题，也在一定程度上补偿 Planner 或 Worker 的失败。但这种补偿是语言模型的后处理能力，不是形式化的 plan verifier 或 evidence prover。（Source: Sec. 2.1; Appendix B）

### 8.2 Decoupling foreseeable reasoning

ReWOO 把 Planner 能够在工具响应前预见的部分推理先执行。这个设计适合任务结构和需要查询的对象大致可预测的场景；如果必须先观察环境才能知道下一步要查询什么，Planner 就需要枚举大量可能计划，效率优势会下降。（Source: Sec. 2.3; Sec. 4 Limitations）

因此，foreseeable reasoning 不是所有 reasoning，也不是“没有 Observation 的完整 Agent reasoning”。它是相对于当前任务和工具信息而言，可以在 evidence 到来前写出的计划部分。（Cross-paper interpretation; Source: Sec. 2.1; Sec. 4）

### 8.3 Token complexity

论文分析了重复 context 对 token 的影响。ReAct 在 k 个 Thought–Action–Observation steps 中反复携带 context、exemplars、question 和历史 T/A/O；ReWOO 的 Planner 主要一次携带问题、context 和示例，Solver 再读取 plans 与 evidence。论文据此认为 ReAct 的重复 T/A/O 项导致随步骤增长的二次开销，而 ReWOO 的主要计划和证据项更接近线性累积。（Source: Sec. 2.2; Appendix A, Fig. 7）

实验中的 token 统计包含 LLM-based tools 消耗的 token；因此 token 数和 dollar cost 反映的是整个 augmented system，不只是 Planner 的输出长度。（Source: Sec. 3.1; Table 2）

### 8.4 Fine-tuning and specialization

论文使用 text-davinci-003 从 HotpotQA、TriviaQA 和 GSM8K 生成约 4000 个 Plan–evidence blueprint，并过滤出约 2000 个正确样本。先用 Alpaca 52k instruction data 得到 Alpaca 7B，再在 Planner 数据上进一步微调得到 Planner 7B。

这个实验把 ReWOO 的模块边界用于能力迁移：可以将 foreseeable reasoning 从大模型中蒸馏或 specialization 到较小 Planner，而不必让小模型承担全部工具响应处理。（Source: Sec. 2.3; Sec. 3.3; Fig. 4–6）

## 9. Experiments

- Datasets: HotpotQA、TriviaQA、SportsUnderstanding、StrategyQA、GSM8K、PhysicsQuestions，以及作者构造的 State of the Union 2023 question answering dataset（SOTUQA）和餐厅推荐、股票、绘图等 curated tasks。（Source: Sec. 3.1）
- Baselines: Direct Prompt、CoT、ReAct；工具描述附加到 prompt 以进行 zero-shot evaluation。（Source: Sec. 3.1）
- Tools: Wikipedia、Google、WolframAlpha、LLM、Calculator、SearchDoc；curated tasks 还使用 Location、Stock、Twitter、Yelp、Email、TradeStock、Draw 等工具。（Source: Sec. 3.1; Table 1）
- Metrics: exact match、character-level F1、GPT-4 semantic accuracy、总 token usage、reasoning steps 和每 1000 次 query 的 USD cost。CoT / ReAct 的 steps 按 thoughts 计算，ReWOO 的 steps 按 plans 加一个 Solver 计算。（Source: Sec. 3.1; Table 2 footnote）
- Fine-tuning: 7B LLaMA-based models 使用 LoRA，在单张 RTX4090 上训练。（Source: Sec. 3.1; Appendix）

### Main prompting comparison

Table 2 的结果如下。不同数据集的 Acc、F1、EM 可用指标不同；下表保留论文原表中的主要数值，并明确标示 token 和 cost。

| Dataset | Method | Acc | F1 | EM | Tokens | Steps | USD / 1k |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| HotpotQA | Direct | 37.8 | 36.2 | 28.0 | 55.5 | 1.00 | 0.11 |
| HotpotQA | CoT | 41.6 | 30.8 | 22.4 | 481.9 | 1.79 | 0.96 |
| HotpotQA | ReAct | 40.8 | 39.6 | 32.2 | 9795.1 | 4.97 | 19.59 |
| HotpotQA | ReWOO | 42.4 | 40.1 | 30.4 | 1986.2 | 4.45 | 3.97 |
| TriviaQA | ReAct | 59.4 | 53.2 | 47.4 | 4212.9 | 5.21 | 8.43 |
| TriviaQA | ReWOO | 66.6 | 60.6 | 51.8 | 1340.9 | 3.55 | 2.68 |
| GSM8K | CoT | 67.4 | 62.7 | — | 495.6 | 3.45 | 0.99 |
| GSM8K | ReAct | 62.0 | 37.3 | — | 1874.3 | 2.86 | 3.75 |
| GSM8K | ReWOO | 62.4 | 36.2 | — | 1089.3 | 3.21 | 2.18 |
| StrategyQA | ReAct | 64.6 | 64.6 | 64.6 | 1686.3 | 2.58 | 3.37 |
| StrategyQA | ReWOO | 66.6 | 66.6 | 66.6 | 1287.1 | 3.20 | 2.57 |
| PhysicsQA | ReAct | 64.1 | 16.2 | — | 2163.3 | 2.77 | 4.33 |
| PhysicsQA | ReWOO | 66.0 | 14.0 | — | 1225.7 | 2.56 | 2.45 |
| SportsUnderstanding | ReAct | 58.6 | 51.9 | 49.3 | 1720.0 | 2.64 | 3.44 |
| SportsUnderstanding | ReWOO | 61.3 | 55.8 | 55.3 | 854.2 | 3.04 | 1.71 |
| SOTUQA | ReAct | 64.8 | 42.7 | — | 1840.3 | 2.43 | 3.68 |
| SOTUQA | ReWOO | 70.2 | 44.8 | — | 1048.8 | 2.24 | 2.09 |

ReWOO 论文报告：在六个 public benchmarks 上平均减少 64% token usage，并相对 ReAct 获得 4.4% absolute accuracy gain；在 SOTUQA 上比 ReAct 高 8% absolute accuracy，同时少用 43% tokens。表中 HotpotQA 的具体 Acc 是 ReAct 40.8、ReWOO 42.4，不能把 abstract 中的总体“4% accuracy improvement”直接当作 HotpotQA 的单项差值。（Source: Table 2; Sec. 3.2.1; Abstract）

### Extraneous tools

作者在 HotpotQA 中逐步增加额外工具。Figure 5 显示，Google 等有用工具可能短暂提高准确率，但一般趋势是工具越多，ALM 性能越容易下降。20 个 ReWOO 成功但 7-tool 失败的案例中，有 17 条轨迹涉及 tool misuse，例如用 Yelp 搜索名人。（Source: Sec. 3.2.1; Fig. 5）

这个结果说明，工具集合越大并不自动产生更强的 Agent；tool selection 和 tool representation 本身仍是能力瓶颈。（Cross-paper interpretation; Source: Sec. 3.1; Fig. 5）

### Tool failure

Table 3 强制所有工具返回 No evidence found。正常 HotpotQA 设置下，ReAct 的 Acc、Tokens、Cost 为 40.8、9795.1、21.29，ReWOO 为 42.4、1986.2、3.97。工具失败时，表中报告 ReAct 的 Acc 变化为 -40.8、token 变化为 +851.1、cost 变化为 +1.70；ReWOO 的 Acc 变化为 -29.2、token 变化为 -110.8、cost 变化为 -0.22。

这些是论文 Table 3 的“变化”列，不能把 -40.8 / -29.2 解读为工具失败后的绝对准确率。论文据此认为 ReWOO 在该人为设置的工具失败条件下相对更不脆弱且成本更低；它并没有证明 ReWOO 能可靠诊断所有错误 evidence。（Source: Table 3; Sec. 3.2.1）

### Fine-tuning and specialization

Figure 6 比较 GPT-3.5、Alpaca 7B 和 Planner 7B 作为 ReWOO Planner 的效果。论文报告 Planner 7B 在 HotpotQA、TriviaQA 和 StrategyQA 上可以匹配 25 倍更大的 GPT-3.5，并且在只用 Wikipedia / LLM 工具训练后，配合工具描述也能处理 Google / Calculator。这个结果支持模块 specialization 的潜力，但不等于 7B 模型已具备普遍的 planner 能力。（Source: Sec. 3.3; Fig. 4; Fig. 6）

## 10. Strengths

- 通过 Planner–Worker–Solver 模块把 foreseeable reasoning、tool execution 和 evidence interpretation 分离，结构边界清晰。
- 减少 observation-interleaved trajectory 中反复发送历史 prompt、示例和工具结果的 token redundancy。
- 对工具失败相对更不敏感，因为 Planner 的 blueprint 不依赖每个中间 response 才能继续生成；Solver 仍可以处理缺失 evidence。
- Planner 可以独立 specialization 或蒸馏到较小模型，为模块化系统优化提供接口。
- 计划和 evidence 分离后，便于分析是 reasoning、tool execution 还是 final solving 出错。（Source: Sec. 2–3; Appendix A）

## 11. Limitations

### Paper-stated limitations

- 当 environment context 很少、必须先观察才能知道目标对象或下一步时，完全依赖 foreseeable reasoning 不现实。论文用 AlfWorld 中从 27 个物体寻找 vase 的例子说明 Planner 可能需要枚举大量潜在计划。（Source: Sec. 4）
- 作者建议更 robust 的 ALM 不应是 singleton，而应把不同 LLM、tools 和 sub-models 连接成 DAG；tool representation learning、节点 specialization 和 graph optimization 被列为 future work。（Source: Sec. 4）
- ReWOO 的 Planner 只在 evidence 到来前生成 blueprint，因此无法像 ReAct 一样自然地根据每个真实 Observation 改写后续计划。（Source: Sec. 2.1; Sec. 4）

### Limitations visible from the method and experiments

- Planner 的预期可能错误：它可能错误假设某个人或事实会出现在 Wikipedia 结果中，即使 Worker 返回了相关 evidence，Solver 仍可能给出错误答案。（Source: Appendix A）
- ReWOO 不等于静态计划一定可执行。Plans 是自然语言和 evidence placeholders，不具有 LLM+P 那样的 formal precondition、state transition 或 solver-backed optimality。
- Worker 得到 evidence 后，主 Planner 没有明确的在线 replanning 阶段；Solver 的后处理不能自动替代基于新状态的计划修订。（Cross-paper interpretation; Source: Sec. 2.1; Appendix B）
- 工具越多，tool misuse 和无关结果可能越严重；把结果送进 Solver 不等于结果被验证。（Source: Fig. 5; Appendix A）
- Abstract 的 5× token efficiency 和 4% accuracy improvement 是论文的总体概括；具体优势依数据集、指标和 token accounting 而变化，不能脱离 Table 2 泛化。

## 12. Relationship to Existing Knowledge

### ReAct

ReAct 在运行时交错生成 Thought、Action 和 Observation：工具结果直接决定下一轮 Thought/Action。ReWOO 把 Planner 的 foreseeable reasoning 提前完成，再由 Worker 执行 tools，最后由 Solver 读取 evidence。前者更适合观察依赖的交互和在线改写，后者更适合可预见的多步查询并减少重复 context。（Cross-paper synthesis; [ReAct paper note](../react/notes.md); [Planning](../../concepts/planning.md)）

ReWOO 不是 ReAct 的简单优化实现：它改变了 observation 与 reasoning 的耦合位置、模块边界和执行顺序，代价是 Planner 无法在生成 blueprint 阶段利用实时 evidence。（Source: Sec. 1–2.2）

### RAP

RAP 在 inference time 使用 world model 预测状态，并用 MCTS 搜索多个候选 reasoning path；ReWOO 的 Planner 输出自然语言 blueprint 和 evidence placeholders，但不使用 MCTS 或 world model 来搜索状态树。RAP 的 search 关注候选未来的 reward，ReWOO 的解耦关注工具调用前后的 token 与模块效率。（Cross-paper synthesis; [RAP paper note](../rap/notes.md); [Planning](../../concepts/planning.md)）

### LLM+P

LLM+P 让 LLM 将自然语言任务翻译成 PDDL，再交给 classical planner 求解；ReWOO 的 Planner 虽然名字相同，但输出的是 language blueprint，而不是具有形式化 preconditions、effects 和 goals 的 planning problem。两者都体现了 reasoning 与执行 / 求解模块的解耦，但 explicit planning 的强度和验证机制不同。（Cross-paper synthesis; [LLM+P paper note](../llm-p/notes.md); [Planning](../../concepts/planning.md)）

### Toolformer

Toolformer 关注通过训练让 LM 学会何时、如何插入 API call；ReWOO 主要是 runtime 的 Planner–Worker–Solver 组织方式，并没有用 future-token loss filtering 学习通用 API-use policy。ReWOO 的 Worker 工具调用仍依赖 Planner 的自然语言计划和工具描述。（Cross-paper synthesis; [Toolformer paper note](../toolformer/notes.md); [Tool Use](../../concepts/tool-use.md)）

### Reflexion

Reflexion 的 reflection 是基于一次 attempt 的 feedback，影响下一次 attempt 的 context；ReWOO 的 Solver 是同一次任务中 plans 与 evidence 的后处理，不是跨 attempt 的 reflection memory。ReWOO 也没有引入 persistent 或 episodic memory architecture。（Cross-paper synthesis; [Reflexion paper note](../reflexion/notes.md); [Memory](../../concepts/memory.md)）

### Concepts

ReWOO 给 [Planning](../../concepts/planning.md) 增加了 plan-first、Planner–Worker–Solver 解耦和 foreseeable reasoning 的边界；给 [Tool Use](../../concepts/tool-use.md) 增加了 tool result integration、tool failure 与 extraneous tool 的系统性证据；给 [Context Engineering](../../concepts/context-engineering.md) 增加了通过减少重复 prompt / trajectory token 来设计上下文的例子。它不提供新的 memory 机制，也不应被概括为完整 Agent architecture。（Source: Sec. 2–4）

## 13. My Understanding

我把 ReWOO 理解成“先写查询与推理蓝图，再执行证据收集，最后统一求解”的 augmented LM 架构。它真正优化的是 reasoning 与 observation 的耦合方式：Planner 可以先完成 foreseeable 部分，Worker 只负责把计划中的 evidence 位置填上，Solver 再面对真实结果。

这使 ReWOO 与 ReAct 的差异不只是 token 数量差异。ReAct 的优势是每一步都能把 Observation 作为下一次决策的直接条件；ReWOO 的优势是能把不依赖具体 response 的 reasoning 一次完成，减少重复上下文和等待。两者之间是对环境可预测性的取舍。

我不会把 ReWOO 的 Planner 自动当成 LLM+P 中的 formal planner，也不会把 Planner–Worker–Solver 自动称为完整 Agent。它有目标、计划、工具和求解模块，但论文的核心是 augmented language model 的 prompt / module organization；是否构成面向环境持续决策的 Agent，要看具体执行边界和是否存在基于新状态的循环。

## 14. Questions

### Questions left by the paper

- 如何自动判断一部分 reasoning 是否 foreseeable，并在不可预见时切换到 observation-dependent execution？（Source: Sec. 4）
- Planner、Worker 和 Solver 如何在存在冲突 evidence、工具副作用或动态环境时进行验证与 replanning？（Source: Sec. 4; Appendix A）
- 如何学习通用的 tool representation、工具相似性和安全的 tool selection？（Source: Sec. 4–5）
- 如何在 DAG 化的模块系统中做并发、依赖管理和错误传播控制？（Source: Sec. 4）

### Further questions from my interpretation

- ReWOO 的 evidence placeholder 是否可以编译成 structured tool calls、依赖图或可验证的 execution plan？
- 什么时候应使用 ReWOO 式 plan-first，什么时候应使用 ReAct 式 observation-first，什么时候需要两者混合？
- Solver 的语言补偿能力如何与显式 evidence verifier、critic 或 world model 结合？
- Planner 输出的 plan quality、Worker 的 tool correctness 和 Solver 的 answer quality 应如何独立评估？

## 15. Related Work

论文讨论了 tool-augmented LLM、ReAct、Toolformer、机器人 API、Calculator / code interpreter、efficient LLM、LoRA、Alpaca 和模块化系统。它还提到将多个 LLM、tools 和 sub-models 连接成 DAG 的未来方向；LangChain 只在 related-work footnote 中被提及，不是本文的实现重点。（Source: Sec. 5; Sec. 4）

## 16. Useful Quotes / Definitions

- ReWOO 的模块名称是 Planner、Worker、Solver，核心流程为 Plan–Work–Solve。（Source: Sec. 2.1; Fig. 1）
- Planner 使用 evidence variables 表达工具结果依赖，后续计划可以引用先前 evidence。（Source: Sec. 2.1; Appendix B）
- 论文将方法概括为 decoupling reasoning from tool feedback and observations。（Source: Abstract; Sec. 6）
- 在六个 public benchmarks 上，论文报告相对 ReAct 平均减少 64% token usage，并获得 4.4% absolute accuracy gain。（Source: Sec. 3.2.1; Table 2）

## 17. Tags

ReWOO, planning, foreseeable-reasoning, planner-worker-solver, tool-use, observation-decoupling, context-engineering, augmented-language-model, token-efficiency

## Code / Implementation

- Repository: [billxbf/ReWOO](https://github.com/billxbf/ReWOO)
- Official status: Confirmed Official
- Read at commit: `9cd0283043ff4be0c9d614fda2789d143ca6ffd1`
- Code notes: [ReWOO source-code notes](../../code/rewoo/notes.md)
- Implementation coverage: Plan–Worker–Solver pipeline, worker registry, evidence-variable substitution, and cost logging.
