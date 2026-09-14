# Open Questions

记录学习过程中尚未解决、需要验证或值得进一步研究的问题。

## Knowledge Review v1: Consolidated Status

以下是前三篇论文复盘后的当前状态。历史阅读记录仍保留在本文件后续各节；本节作为去重后的导航，不把暂时理解误写成最终结论。

| Question | Status | Current understanding |
| --- | --- | --- |
| Agent 的边界是什么？ | Partially Answered | 需要目标驱动的持续决策和状态 / feedback loop；Tool Use 本身不是充分条件，Agentic workflow 的边界仍开放。 |
| Tool-augmented LM 与 Agent 的边界是什么？ | Partially Answered | Toolformer 提供 LM-level tool-use evidence，ReAct 提供 runtime interaction evidence，但当前资料还不足以形成统一判据。 |
| Reasoning 与 Planning 如何区分？ | Partially Answered | 可以区分当前推导与多步行动组织；LLM+P 提供 explicit planner / solver，RAP 提供 search-based planning 的边界案例，但 plan-like reasoning、形式化规划和在线 replanning 的统一判据仍开放。 |
| Reasoning 与 Reflection 有什么差别？ | Partially Answered | Reasoning 主要推进当前 step / attempt，Reflection 主要把评估结果转成下一次 attempt 的语言条件；与 critic 的边界仍开放。 |
| Feedback 如何转化为有效 Reflection？ | Open | Evaluator 可靠性、错误归因、语言反馈的可执行性和迁移性仍未解释。 |
| Memory 应该保存什么、保存多久、何时读取？ | Partially Answered | 已区分 current context、working-memory-like context 和 task-local episodic memory；persistent memory 的检索、压缩和冲突处理仍开放。 |
| 如何避免错误 Observation / Reflection 累积？ | Open | 现有论文展示了部分失败恢复，但没有通用的验证、provenance、淘汰或安全更新机制。 |
| Tool-use policy 应通过 prompt、training 还是 planning 获得？ | Partially Answered | ReAct、Toolformer、Reflexion 分别提供 runtime、training 和 feedback-driven 证据；ReWOO 增加了 Planner blueprint 驱动 Worker 的模块化路径；成本、迁移和组合关系仍开放。 |
| 如何可靠支持 chained tool use 和 interactive search？ | Open | Toolformer 和 ReAct 的笔记都暴露了这个缺口，当前资料没有统一解决方案。 |

详细的跨论文推理见 [Knowledge Review v1](reviews/knowledge-review-v1.md)。

## From the ReAct reading

### 论文明确暴露或留下的问题

- ReAct 的重复 thought/action 循环是否主要来自 greedy decoding、prompt 结构，还是状态表示不足？（Source: Sec. 3.3）
- 如何在非信息性 Search 结果之后有效改写查询并恢复推理？（Source: Sec. 3.3）
- 更多高质量人工轨迹、multi-task training 和 reinforcement learning 能否改善长时程、大 action space 任务？（Source: Sec. 6）

### 本次阅读进一步产生的问题

- ReAct 是否真正具有 planning，还是只表现出计划性的语言行为？
- Reasoning trace 是否等价于 Agent 的 internal state？
- ReAct 的文本 Action 如何演化为现代 structured tool calling / MCP 接口？
- ReAct trajectory 中的历史信息与现代 Agent memory 有什么区别？
- 错误、冲突或过时的 Observation 如何影响后续 Agent trajectory？

关联笔记：[ReAct 论文笔记](../papers/react/notes.md#14-questions)。

### Tool Use 相关问题的状态补充

- 对“ReAct 的文本 Action 如何演化为现代 structured tool calling / MCP 接口？”：**部分回答**。Toolformer 证明了模型可以通过自监督方式学习文本 API 的调用时机、工具名和参数，并在生成中插入文本结果；但它没有给出 schema、权限、错误处理或 MCP 映射方案。因此“能否迁移到现代接口”仍未解决。
- 对“ReAct trajectory 中的历史信息与现代 Agent memory 有什么区别？”：**仍未解决**。Toolformer 的 API result 是当前 token context 的一部分，也没有 persistent / long-term memory。
- 对“错误、冲突或过时的 Observation 如何影响后续 Agent trajectory？”：**仍未解决**。Toolformer 的论文没有系统研究错误或恶意工具返回值的识别与恢复。

## From the Toolformer reading

### 已由论文部分回答的问题

- 模型可以通过 self-supervised future-token loss filtering 学习“何时调用哪个工具、传入什么参数”，但这个训练信号衡量的是对后续文本的预测帮助，不等于普遍的任务正确性或安全性。（Source: Sec. 2）
- Toolformer 的调用表示和结果注入是文本化的：`<API> name(input) ! result </API>`，实际使用 `[`, `]`, `->` token 序列；这回答了一个具体表示方式，但没有回答现代 structured tool calling / MCP 应如何实现。（Source: Sec. 2 and footnote 1）
- ReAct 与 Toolformer 都涉及外部工具，但 ReAct 以运行时 Thought/Action/Observation 闭环为核心，Toolformer 以自监督微调获得的 API token-generation policy 为核心；它们不应被视作同一种 Agent 架构。（Source: ReAct note; Toolformer Sec. 2, Sec. 5–6）
- Toolformer 在论文中被定位为 LM；它具有模型驱动的 API 选择，但没有足够证据证明其具有完整 Agent 所需的显式 Planner、持久化 Memory 或多步 Environment runtime。（Source: Abstract; Sec. 2; Sec. 7）

### 论文明确留下的问题

- 如何通过迭代式数据增强学习可靠的 chained tool use？（Source: Sec. 6）
- 如何让模型交互式浏览搜索结果、改写 query 并根据中间结果继续调用？（Source: Sec. 6）
- 如何提高 calculator 等工具的调用样本效率，并把工具计算成本纳入调用决策？（Source: Sec. 6）

### 基于两篇论文进一步产生的问题

- loss-based filtering 与真实任务 utility、事实 grounding 和 calibration 的关系是什么？
- Toolformer 学到的调用策略能否迁移到训练增强语料中未出现的新 API？
- Toolformer 的 inline API result 与 ReAct 的 Observation trajectory 能否组合成稳定的多步交互 Agent？

关联笔记：[Toolformer 论文笔记](../papers/toolformer/notes.md#14-questions)。

## From the Reflexion reading

### 已补充回答的问题

- 对“ReAct trajectory 中的历史信息与现代 Agent memory 有什么区别？”：**得到部分回答**。Reflexion 明确区分当前 trajectory 的 short-term memory 与跨 trial 保存的 self-reflection；其实际 memory 通常只保留最近 1–3 条，属于 task-local、bounded episodic memory，并没有证明跨会话的 persistent memory。（Source: [Reflexion 论文笔记](../papers/reflexion/notes.md#82-memory-lifecycle); Sec. 3.1; Sec. 5）
- 对“错误、冲突或过时的 Observation 如何影响后续 Agent trajectory？”：**得到部分回答**。Evaluator 和 reflection 可以把失败转成下一次的错误诊断与修正建议，但错误反馈也可能被写入 memory；Reflexion 没有系统解决错误 evaluator、冲突 Observation 或错误 reflection 的检测与恢复。（Source: [Reflexion 论文笔记](../papers/reflexion/notes.md#83-task-specific-evaluators); Sec. 5）
- 对“ReAct 是否真正具有 planning？”：**得到部分回答**。Reflexion 的 reflection 能提出替代动作顺序或策略，显示 plan-like correction；但论文没有定义独立 Planner 或可验证计划状态，因此仍不能把语言化分解直接等同于完整 planning architecture。（Source: [Reflexion 论文笔记](../papers/reflexion/notes.md#12-relationship-to-existing-knowledge)）
- 对“Reasoning trace 是否等价于 Agent 的 internal state？”：**进一步确认否定**。Thought、trajectory 和 reflection 都是显式语言条件；它们能影响后续行为，但不能据此断言它们就是模型真实 hidden internal state。（Source: [Reflexion 论文笔记](../papers/reflexion/notes.md#12-relationship-to-existing-knowledge)）

### 论文明确留下的问题

- 自然语言 policy optimization 如何避免非最优 local minima？（Source: Sec. 5）
- 如何把当前有限的 sliding-window memory 扩展为更大且可靠的可检索 memory？（Source: Sec. 5）
- 如何在高多样性、需要探索的环境中让 reflection 真正提供有效指导？（Source: Appendix B.1）
- 在非确定性、带副作用、依赖硬件或并发的代码任务中，如何获得可靠的 evaluator feedback？（Source: Sec. 5）

### 基于 Reflexion 进一步产生的问题

- 错误 reflection 是否会造成后续 trajectory 的反馈回路，使 Agent 越来越偏？
- 为什么自然语言 reflection 能够在部分任务中充当有效的 credit-assignment signal？
- Reflection 与 critic、self-correction 或其他 verbal feedback 方法有什么本质区别？
- 长期运行的 Agent 应保存原始 trajectory、reflection summary，还是可验证的压缩结果？
- 如何分别评估 Actor、Evaluator、Self-Reflection 和 Memory 的贡献？

关联笔记：[Reflexion 论文笔记](../papers/reflexion/notes.md#14-questions)。

## From the LLM+P reading

### 已补充回答的问题

- 对“ReAct 是否真正具有 planning？”：**得到更清晰的边界**。LLM+P 具有 PDDL 状态、动作、目标和 classical planner，因此是 explicit planning 的边界案例；ReAct 的 Thought 更谨慎地称为 plan-like reasoning，不能仅凭多步语言输出断言存在独立 Planner。（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#13-my-understanding)）
- 对“Agent 的边界是什么？”：**得到部分回答**。存在外部 planner 或 executor 不足以单独定义 Agent；还要检查是否有目标驱动的持续状态交互、执行和反馈调整。（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#12-relationship-to-existing-knowledge)）

### 论文明确留下的问题

- 如何自动判断自然语言请求是否适合 LLM+P，并选择合适的 planning domain？（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#11-limitations)）
- 如何降低对人工 domain PDDL 和 problem/PDDL demonstration 的依赖？（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#11-limitations)）
- 如何验证 LLM 生成的 PDDL，避免遗漏初始条件或错误 predicate 进入 solver？（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#11-limitations)）
- 如何把执行期间的 Observation、环境变化和 action failure 纳入静态计划的 revision / replanning？（Source: [LLM+P 论文笔记](../papers/llm-p/notes.md#14-questions)）

### 基于 LLM+P 进一步产生的问题

- explicit planning 的最低要求是形式化状态、动作和目标，还是还需要独立搜索或验证过程？
- Planner–Executor 解耦在开放环境、部分可观测状态和连续动作中应如何实现？
- formal planner 的正确性保证如何与上游自然语言翻译错误和下游真实执行失败组合？

## From the ReWOO reading

### 已补充回答的问题

- 对“ReAct 式 runtime interaction 与 plan-first 架构有什么区别？”：**得到部分回答**。ReAct 在每轮 Action 后读取 Observation，再决定下一步；ReWOO 先生成 foreseeable blueprint，再由 Worker 执行工具、由 Solver 整合 evidence。前者更适合 observation-dependent interaction，后者减少重复 context，但 Planner 不能直接利用后续 Observation。（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#12-relationship-to-existing-knowledge)）
- 对“Planning 和 Tool Use 如何组合？”：**得到部分回答**。ReWOO 用 evidence variables 表达计划中的工具依赖，说明 tool invocation 可以作为计划模块的执行阶段；但它没有给出动态环境中的通用 Planner–Worker replanning 机制。（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#8-method)）

### 论文明确留下的问题

- 如何判断哪些 reasoning 是 foreseeable，哪些必须等待 Observation？（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#11-limitations)）
- 如何处理错误、冲突或副作用 evidence，并在必要时触发 replanning？（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#14-questions)）
- 如何学习工具表示、工具相似性和安全的 tool selection？（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#11-limitations)）
- 如何在多模块或 DAG workflow 中管理依赖、并发和错误传播？（Source: [ReWOO 论文笔记](../papers/rewoo/notes.md#14-questions)）

### 基于 ReWOO 进一步产生的问题

- plan-first、search-based planning 和 runtime observation-first 是否应根据环境可预测性自动切换？
- evidence placeholder 能否编译成结构化 tool call、依赖图和可验证执行计划？
- Solver 的语言补偿何时足够，何时必须加入独立的 evidence verifier 或 critic？

## From the RAP reading

### 已补充回答的问题

- 对“ReAct 是否真正具有 planning？”：**得到更清晰的层次区分**。RAP 说明 planning 可以通过任务相关 state、world model、reward 和 MCTS 形成显式 search-based inference；ReAct 的 Thought 仍是 plan-like、runtime 的决策机制，不能简单与 RAP 的搜索树等同。（Source: [RAP 论文笔记](../papers/rap/notes.md#12-relationship-to-existing-knowledge)）
- 对“Observation 在 planning 中扮演什么角色？”：**部分回答**。RAP 的核心实验使用 LLM 预测 imagined state 作为搜索条件，而不是外部执行后的真实 Observation；因此 model-based simulation 与 observation-grounded interaction 是不同反馈来源。（Source: [RAP 论文笔记](../papers/rap/notes.md#6-architecture--workflow)）

### 论文明确留下的问题

- 如何自动定义跨任务可靠的 state、action 和 reward？（Source: [RAP 论文笔记](../papers/rap/notes.md#11-limitations)）
- 如何验证 world model 的 state transition prediction，并识别错误的 imagined state？（Source: [RAP 论文笔记](../papers/rap/notes.md#14-questions)）
- MCTS 的分支、深度和 LLM 调用成本如何扩展到更长任务？（Source: [RAP 论文笔记](../papers/rap/notes.md#14-questions)）
- 如何将真实 Observation、external tools 和 online replanning 与 RAP 结合？（Source: [RAP 论文笔记](../papers/rap/notes.md#14-questions)）

### 基于 RAP 进一步产生的问题

- Planning 是否一定需要 search，还是可以通过单一路径的可验证计划生成完成？
- world model 预测的 imagined state 何时足以替代真实 Observation，何时必须由环境或 symbolic simulator 校验？
- Planner 的 reward 与 Agent 任务真实效用不一致时，如何检测 search-induced error？
