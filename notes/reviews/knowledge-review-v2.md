# Knowledge Review v2

## Scope

本次 Review 聚焦本批次新增的三篇 Planning 论文：

- [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../../papers/llm-p/notes.md)
- [RAP: Reasoning with Language Model is Planning with World Model](../../papers/rap/notes.md)
- [ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models](../../papers/rewoo/notes.md)

背景资料是前三篇已经完成的 [ReAct](../../papers/react/notes.md)、[Toolformer](../../papers/toolformer/notes.md)、[Reflexion](../../papers/reflexion/notes.md) 以及 [Knowledge Review v1](knowledge-review-v1.md)。本次优先使用已经完成 Source Grounding 的 paper notes，没有重新大规模解析原始 PDF。

下文明确区分：

- **Paper-backed fact：** 能在对应论文笔记中追溯到 Section、Table、Figure 或 Appendix 的事实。
- **Cross-paper synthesis / current interpretation：** 基于多个 paper notes 形成的当前 mental model，不应归为任何单篇论文的正式定义。

## 1. What I Understand So Far

### Paper-backed fact

三篇新论文把 planning 放在不同层次：

- LLM+P 让 LLM 把自然语言问题翻译为 PDDL problem，再让 classical planner 在形式化 domain、state、action 和 goal 上搜索计划。（Source: [LLM+P note](../../papers/llm-p/notes.md), Sec. II–III）
- RAP 将 reasoning 过程表示为 task-specific state/action trajectory，用 prompted LLM 预测 next state，用 reward 和 MCTS 进行 inference-time search。（Source: [RAP note](../../papers/rap/notes.md), Sec. 3.1–3.3; Appendix A）
- ReWOO 让 Planner 先生成带 evidence placeholders 的 language blueprint，Worker 执行工具，Solver 最后组合 plans 与 evidence。（Source: [ReWOO note](../../papers/rewoo/notes.md), Sec. 2.1）

### Cross-paper synthesis / current interpretation

Planning 可以暂时理解为：围绕目标组织多个未来行动、子目标、依赖或候选路径，并在存在状态、约束或反馈时决定是否继续、修正或重新组织这些行动。它不是单一实现：

- 可以是 ReAct 中由 Thought 表达的 plan-like runtime behavior。
- 可以是 LLM+P 中有形式化状态和独立 solver 的 explicit planning。
- 可以是 RAP 中由 world model、reward 和 MCTS 支持的 search-based planning。
- 可以是 ReWOO 中先组织 foreseeable reasoning、再交给 Worker 和 Solver 的 plan-first workflow。

因此，看到一段多步语言输出时，仍要分别检查：是否有明确计划表示、是否有独立搜索或 solver、反馈何时可见、计划是否被执行验证、失败后是否会修改计划。

## 2. Cross-Paper Relationships

这不是三个摘要的并列，而是按 Agent 系统中的不同问题组织关系：

| Paper | 主要解决的层次 | 计划或推理的表示 | 反馈 / Observation 来源 | 主要执行或选择机制 |
| --- | --- | --- | --- | --- |
| ReAct | runtime reasoning–acting interaction | Thought、Action、Observation trajectory | 外部环境或工具在每一步返回的 Observation | LLM 决定下一步；没有独立 Planner |
| LLM+P | natural language 到 formal planning 的接口 | PDDL domain/problem 与 symbolic plan | 主要是已知初始状态和目标表示 | classical planner 搜索并求解 |
| RAP | inference-time search-based reasoning | task state、action、imagined state | prompted world model 的预测状态与 reward | MCTS 的 selection、expansion、simulation、backpropagation |
| ReWOO | observation 与 reasoning 的模块化调度 | language blueprint、evidence placeholders | Worker 执行工具后产生 evidence | Planner–Worker–Solver；没有 MCTS 或 formal solver |
| Toolformer | learned tool-use policy | 文本化 API call / result token | API execution result 进入 token context | training-time future-token loss filtering |
| Reflexion | cross-attempt adaptation | reflection 与 episodic experience | Evaluator 对上一 attempt 的 feedback | reflection 写入 memory，影响下一次 Actor |

**Cross-paper synthesis / current interpretation：** 这些论文不是同一条 Agent architecture 的逐步升级。ReAct 主要处理运行时的 observation-grounded interaction；LLM+P 主要处理语言与形式化规划求解之间的接口；RAP 主要处理候选 reasoning path 的推理时搜索；ReWOO 主要处理 foreseeable reasoning、tool execution 和 evidence integration 的调度。Toolformer 与 Reflexion 则分别从训练期 tool-use policy 和跨 attempt feedback adaptation 提供背景维度。

它们可以在更大的系统中组合，例如先由 Planner 生成候选计划、用 world model 或 classical solver 检查，再由 ReAct 式执行器根据真实 Observation 继续行动；但目前这些论文没有共同证明这种组合是标准方案。

## 3. Concept Boundaries

### Reasoning vs Planning

**Paper-backed fact：** ReAct 的 Thought 服务于当前 trajectory 的下一步；LLM+P 有独立的 symbolic planner；RAP 用状态、reward 和 MCTS 组织候选 reasoning path；ReWOO 将 foreseeable reasoning 写入 blueprint。（Source: 各论文 notes 的 Method / Workflow sections）

**Cross-paper synthesis / current interpretation：**

- Reasoning 更偏向从当前信息和约束形成中间推导，支持当前结论或动作。
- Planning 更偏向组织未来多个 step、子目标、依赖和行动顺序，并考虑执行或修正。
- 二者可以由同一个 LLM 共同完成，但功能角色不同。
- 一段 Thought 可以包含 plan-like reasoning，却不自动证明存在 explicit Planner。

### What is plan-like reasoning?

plan-like reasoning 是语言模型在当前上下文中提到未来步骤、分解子目标、选择行动顺序或根据 Observation 调整方向的行为。ReAct 和 Reflexion 提供了这类证据，ReWOO 的 language blueprint 也有一定计划组织作用。

它不自动意味着：

- 有可验证的状态和动作语义；
- 有独立的 Planner component；
- 计划已经被 solver 检查；
- 模型拥有多个未来状态的 hidden internal representation；
- 计划一定会被执行或在失败后重规划。

### When is planning explicit?

当前可采用的谨慎判据是：计划对象、状态或目标至少有可区分的表示，并且系统有明确的计划组织、搜索、求解或验证过程。

- LLM+P 是最强的当前边界案例：PDDL 和 classical planner 使状态、动作、目标和搜索职责显式。
- RAP 也是显式的 inference-time planning / search：state、world model、reward 和 MCTS 共同组织候选路径，但 predicted state 不是现实环境事实。
- ReWOO 有显式 Planner 模块和 blueprint，但其计划是自然语言加 evidence placeholders，不具有 LLM+P 的形式化约束或 solver 保证。
- ReAct 主要表现为 runtime plan-like behavior，而不是独立 Planner architecture。

这仍是本知识库的 working distinction，不是永久的通用定义。

### Planning and Agent boundary

有 planner、tool 或 executor 都不是 Agent 的充分条件。当前工作定义仍要求检查：是否有任务目标、状态或 context 的持续更新、行动 / 工具执行、Observation / feedback，以及基于这些信息的后续决策。

RAP 论文称 LLM 为 reasoning agent，ReWOO 称自己为 augmented language model，LLM+P 是 solver-backed pipeline；这些论文的命名不能直接替代系统边界分析。（Source: [Agent concept](../../concepts/agent.md)）

## 4. Key Mechanisms

### 4.1 Planner and Executor decoupling

Planner–Executor 解耦的价值在于：

- reasoning、搜索、工具执行和结果解释可以分别优化；
- Planner 可以生成一次计划，避免每轮重复完整 context；
- Executor 可以专注于动作、工具权限、失败和副作用；
- 组件可以单独评估或 specialization。

但解耦也可能丢失实时 feedback。LLM+P 的 formal planner 依赖正确的 PDDL；ReWOO 的 Planner 看不到后续 evidence；RAP 的 world model 可能在错误 imagined state 上继续搜索。因此，解耦不是无条件优于交错执行。（Source: [LLM+P note](../../papers/llm-p/notes.md); [RAP note](../../papers/rap/notes.md); [ReWOO note](../../papers/rewoo/notes.md)）

### 4.2 Search and planning

Search 是实现 planning 的一种方式，不是 planning 的同义词：

- RAP 直接用 MCTS 搜索候选 reasoning paths。
- LLM+P 使用 classical planner 的搜索求解，但论文的重点还包括 PDDL 表示与形式化约束。
- ReWOO 的主流程组织 blueprint 和 evidence，不包含 MCTS 或显式树搜索。
- ReAct 的下一步决策是运行时生成，不等于已经对多个未来分支进行系统搜索。

Search-based reasoning 可以被看作：把多个候选推理路径外化成节点和分支，并用 reward、目标或约束选择路径。只有当 state、transition 和 value 的语义足够清楚时，这种 search 才更接近可分析的 planning。（Source: [RAP note](../../papers/rap/notes.md), Sec. 3.1–3.3）

### 4.3 World Model

World model 的作用是预测“执行某个 action 后可能出现什么 state”，以便 planner / search 在执行前进行 lookahead。RAP 中的 world model 是通过 prompting 复用的 LLM，预测 imagined state；它不是已由真实环境验证的 Observation，也不是 memory。（Source: [World Model concept](../../concepts/world-model.md); [RAP note](../../papers/rap/notes.md), Sec. 3.1）

一个重要风险是模型可以在错误状态上进行连贯搜索。真实环境 Observation、symbolic simulator 或独立 verifier 可以承担校准作用，但三篇新论文没有给出统一解决方案。

### 4.4 Observation timing and replanning

Observation 的位置决定了规划范式：

- ReAct：Observation 在每个 Action 后进入 trajectory，直接影响下一次 Thought / Action。
- LLM+P：主流程先从自然语言生成问题表示，再由 planner 求解；执行中环境变化和 online replanning 没有被系统展示。
- RAP：核心 benchmark 主要使用 LLM 预测的 imagined state；MCTS 在模拟树内回溯，但不等同于真实环境执行后的 Observation。
- ReWOO：Planner 先生成 blueprint，Worker 后产生 evidence，Solver 再整合；主流程没有定义 Worker 后 Planner 自动重生成。

因此，拥有 Observation 不足以说明支持 replanning；还要检查 Observation 是否能改变当前计划、谁负责修改、修改后是否重新验证。

### 4.5 Direct answers to the ten planning questions

1. **Reasoning 和 Planning 的区别：** reasoning 主要形成当前推导，planning 主要组织未来多个 step；二者可由同一模型完成，但不是同义词。
2. **Plan-like reasoning：** Thought 或 blueprint 中出现未来步骤、子目标和行动顺序，但没有因此获得形式化状态、搜索或执行保证。
3. **Explicit planning：** 当前更有力的证据是可区分的计划对象 / state / goal，加上明确的计划组织、搜索、求解或验证过程；LLM+P 和 RAP 是不同强度的例子。
4. **Planner 与 Executor 解耦：** 这样可以分别优化 reasoning、执行、权限和错误处理，也能降低重复 context；代价是计划可能失去实时反馈。
5. **Planning 是否一定搜索：** 不一定。RAP 使用 MCTS；ReWOO 组织 plan-first blueprint 但没有树搜索；形式化计划是否可验证仍需单独判断。
6. **Search-based reasoning 与 Planning：** search 可以把候选 reasoning path 外化为分支、状态和价值比较，从而支持 planning；search 本身不是 planning 的完整定义。
7. **World Model 的角色：** 它预测 action 后的可能 state，为 lookahead 和路径评估提供中间模型；RAP 的预测 state 是 imagined state，不是现实 Observation。
8. **Observation 的时机：** ReAct 在执行中使用，RAP 在核心实验中主要用模拟状态，ReWOO 在 Planner 后由 Worker 提供 evidence；只有明确改变计划并重新验证时才构成 replanning。
9. **Static plan 与 replanning：** static plan 先生成后执行；replanning 在新状态或失败后改变并重新检查计划。当前三篇新论文都没有给出开放环境中的统一 replanning loop。
10. **ReAct 与 plan-first：** ReAct 更适合 observation-dependent、需要在线改写的交互，但有重复 context 和调用成本；plan-first 更适合 foreseeable、多模块执行并可提高效率，但对意外状态更脆弱。

## 5. Common Misconceptions

- **Thought = internal state：** Thought、blueprint 和 reflection 都是显式生成的语言产物；不能据此断言模型真实 hidden state。
- **Tool use = Agent：** Toolformer 和 ReWOO 都说明模型可以调用或编排工具，但是否存在持续目标驱动的 interaction loop 仍需单独判断。
- **ReAct = explicit planning architecture：** ReAct 有 plan-like reasoning 和 runtime adjustment，但没有 LLM+P 那样的 formal planner，也没有 RAP 的 MCTS。
- **生成多个未来步骤 = 完整 Planner：** 多步文本可能只是语言化分解；需要继续检查计划表示、搜索 / 验证机制和执行闭环。
- **Planning = search：** RAP 采用 MCTS，但 ReWOO 的 plan-first blueprint 没有树搜索；search 是可选实现路径。
- **World model = real environment：** RAP 的 predicted state 是 imagined state，可能错误；它不是执行结果。
- **Trajectory context = long-term memory：** ReAct 的历史 context 是任务内上下文，Reflexion 的 bounded episodic experience 也不自动等于跨会话 persistent memory。
- **Reflexion = gradient-based RL：** Reflexion 的当前改善主要来自 feedback、verbal reflection 和下一次 context，不是每次 attempt 都更新模型参数。
- **Reflexion = ReAct + memory：** Reflexion 新增了 evaluator、reflection 和 cross-attempt adaptation；其目标与 ReAct 的单次 runtime interaction 不同。
- **所有 feedback = reflection：** Observation、reward、evaluator feedback 和 reflection 处于不同阶段；reflection 是对 trajectory / feedback 的语言化分析，不是所有结果输入都叫 reflection。

以上纠正主要由六篇已读论文的 notes 支持；没有证据的地方仍保留为开放问题。

## 6. What Current Papers Explain Well

- LLM-only 的语言生成与形式化 solver、外部工具或搜索之间可以进行明确分工。
- Observation-grounded runtime interaction 与 plan-first / search-based inference 是不同控制方式。
- 状态表示、reward、tool evidence 和 context 组织会实质影响多步任务表现。
- Planner、Worker、Solver、world model、evaluator 等模块可以作为分析维度，但模块名称不自动带来正确性保证。
- 规划效果不能只看最终答案；还需要分析计划表示、搜索成本、工具失败、预测状态错误和执行反馈。

## 7. What These Papers Do Not Yet Explain

- 没有统一的 Agent、Planner、world model 或 plan 的正式定义，能覆盖所有六篇论文。
- 没有系统解决开放环境、部分可观测状态、真实副作用和长时间在线 replanning。
- 没有证明语言 Thought、blueprint 或 self-evaluation faithfully 表示模型内部状态或真实任务价值。
- 没有给出跨任务可靠的 reward、state abstraction、tool selection 和 plan verification 方法。
- 没有建立 plan quality、reasoning quality、tool correctness、world-model accuracy 和 execution recovery 的独立评测协议。
- 没有解释如何把 search、formal planning、runtime loop、reflection memory 和 structured tool calling 组合成稳定的长期 Agent。

## 8. Open Questions

当前最重要的问题已同步到 [notes/questions.md](../questions.md)。本 Review 只把它们按 Planning 主题重新组织：

1. explicit planning 的最低要求是形式化 state/action/goal，还是还需要独立 search、solver 或 verification？
2. 如何自动判断一个 reasoning step 是 foreseeable，还是必须等待真实 Observation？
3. imagined state、formal state 和真实 Observation 不一致时，谁负责检测、校准和 replanning？
4. Planner–Executor 解耦在何种环境可预测性下优于 ReAct 式 runtime interaction？
5. 如何把 tool evidence、rewards 和 evaluator feedback 转换成可信的计划修正，而不是错误累积？
6. ReWOO 的 evidence placeholders 能否编译为 structured tool calls、依赖图和可验证 execution plan？
7. 如何在长任务中控制 MCTS、工具调用和上下文维护的成本？

这些问题的状态仍是 Open 或 Partially Answered；本 Review 不把它们永久标记为已解决。

## 9. Current Mental Model

以下是跨论文后的当前抽象，不是任何一篇论文明确提出的标准 Agent 架构：

~~~text
Task + Current State / Context
→ Choose control mode
   ├─ Runtime interaction: ReAct
   ├─ Plan-first interface: LLM+P or ReWOO
   └─ Search-based inference: RAP
→ Reasoning / Plan / Candidate Path
→ Tool, Solver, or Environment Execution
→ Observation / Evidence / Predicted State / Evaluator Feedback
→ Context or Memory Update
→ Continue, Replan, Retry, Reflect, or Finish
~~~

这张图的关键不是把所有系统压成一条流程，而是提醒我先判断四件事：

- 当前的 state 是真实 Observation、形式化 state、imagined state，还是语言 context？
- 计划是 Thought、PDDL、search tree、blueprint，还是 reflection？
- 谁负责选择和验证下一步？
- 新信息能否真正改变计划，还是只能被 Solver / final answer 解释？

## 10. Next Learning Priorities

根据本批次暴露的缺口，下一阶段优先学习：

1. **Replanning and feedback-grounded planning：** 研究动态环境、执行失败、部分可观测状态下的计划修正。
2. **Planner–Executor and structured plans：** 进一步区分 formal planner、language planner、executor、verifier 和 hybrid architecture。
3. **World models and model-based planning：** 学习预测状态、不确定性、simulator 与真实 Observation 的校准。
4. **Planning-aware tool use and context engineering：** 研究 structured tool calls、evidence dependency、上下文压缩和模块间信息交接。
5. **Planning evaluation：** 分离 plan validity、search cost、tool correctness、execution success 和 recovery quality。
