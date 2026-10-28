# Open Questions

记录学习过程中尚未解决、需要验证或值得进一步研究的问题。

## Knowledge Review v1: Consolidated Status

以下是前三篇论文复盘后的当前状态。历史阅读记录仍保留在本文件后续各节；本节作为去重后的导航，不把暂时理解误写成最终结论。

| Question | Status | Current understanding |
| --- | --- | --- |
| Agent 的边界是什么？ | Partially Answered | 需要目标驱动的持续决策和状态 / feedback loop；Tool Use 本身不是充分条件，Agentic workflow 的边界仍开放。 |
| Tool-augmented LM 与 Agent 的边界是什么？ | Partially Answered | Toolformer 提供 LM-level tool-use evidence，ReAct 提供 runtime interaction evidence，但当前资料还不足以形成统一判据。 |
| Reasoning 与 Planning 如何区分？ | Answered for Current Scope | 当前可以区分局部中间推导与多步行动组织；LLM+P、RAP、ReWOO 分别提供 formal solver、search-based 和 plan-first 边界案例，但这仍是可演化的 working distinction。 |
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

## Knowledge Review v2: Planning Batch

以下状态是本次 Review 在当前 scope 下的判断，不删除此前的历史问题；未来论文可能继续改变这些结论。

| Question | Status | Current understanding |
| --- | --- | --- |
| 什么是 plan-like reasoning？ | Answered for Current Scope | Thought、subgoal、未来步骤或 language blueprint 可以体现计划性，但不自动包含形式化状态、搜索、验证或执行保证。 |
| 什么情况下才应称为 explicit planning？ | Partially Answered | 当前至少需要可区分的计划对象 / state / goal 与明确的计划组织、搜索、solver 或验证过程；LLM+P 和 RAP 是不同强度的例子，统一最低标准仍开放。 |
| Planning 是否一定意味着 search？ | Answered for Current Scope | 不一定。RAP 使用 MCTS，LLM+P 使用 classical planner search，而 ReWOO 的 plan-first blueprint 没有 MCTS；是否称为完整 planning 仍要看计划表示和验证边界。 |
| Planner 和 Executor 为什么要解耦？ | Partially Answered | 解耦有利于模块优化、成本控制、权限隔离和错误定位，但可能失去运行时 Observation；是否有益取决于环境的可预测性和 replanning 机制。 |
| Search-based reasoning 与 Planning 有什么关系？ | Partially Answered | Search 可以把多个候选 reasoning path 外化为状态、分支和价值比较，从而支持 planning；但 search 不是 reasoning 或 planning 的同义词。 |
| World Model 在 Planning 中扮演什么角色？ | Partially Answered | RAP 说明它可预测 action 后的 imagined state，供 lookahead 和 MCTS 使用；预测可靠性、校准和真实 Observation 的关系仍开放。 |
| Observation 在 plan 前、执行中还是 plan revision 时发挥作用？ | Partially Answered | ReAct 主要在执行中使用，RAP 核心搜索使用 simulated state，ReWOO 在 Planner 后由 Worker 提供 evidence，LLM+P 的在线 revision 未系统说明。 |
| Static plan 与 replanning 有什么区别？ | Partially Answered | 静态计划通常先生成后执行；replanning 要在新状态或失败后改变计划并重新验证。当前三篇新论文都没有完整展示开放环境中的统一 replanning loop。 |
| Planning 与 Tool Use 的关系是什么？ | Partially Answered | 工具可以是计划中的执行或 evidence 阶段，但 tool invocation policy、计划组织、结果验证和 replanning 仍是不同职责。 |
| 如何避免错误 Observation、evidence 或 imagined state 累积？ | Open | 现有资料分别暴露了错误反馈、工具失败和 world-model prediction error，但没有统一的 provenance、校准、淘汰和恢复机制。 |

### 本次 Review 新增的具体后续问题

- 如何根据环境可预测性自动在 plan-first、search-based 和 runtime observation-first 模式之间切换？
- imagined state、formal state、evidence 和真实 Observation 不一致时，谁负责校准与重规划？
- 如何独立评估 blueprint 的可执行性、MCTS path 的有效性和 ReAct trajectory 的适应性？

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

## From CAPMix reading

### 论文明确留下或未充分回答的问题

- 单一训练窗口均值中心能否表达多种正常业务状态，还是会把稀有但合法的状态当作偏离？（PDF §3.3.2；[CAPMix 笔记](../papers/capmix/notes.md#14-questions)）
- KPI 与负载、发布或扩缩容变化同时出现时，如何区分正常业务变化与真实故障？本文提到这些波动，但未显式使用业务上下文作为模型条件。（PDF §1, §5）
- Benchmarks 中原始异常标签是否逐数据集可用于训练，以及无标签污染样本如何处理？（PDF §3.4, §4.1；[CAPMix 笔记](../papers/capmix/notes.md#11-limitations)）

### 基于 CAPMix 进一步产生的问题

- 在不扫描测试标签选最佳阈值的前提下，CAPMix 的告警成本、误报率和检出率是否仍有优势？


## From When Model Meets New Normals reading

- 检测器漏报的异常样本进入在线更新时，如何检测并阻止自我强化污染？（PDF pp.4, 7；[精读笔记](../papers/when-model-meets-new-normals/notes.md#14-questions)）
- 负载跃迁、发布与故障同时出现时，如何让趋势状态只吸收合法的新正常？本文没有使用 workload 或运维上下文。（PDF pp.3–4；[精读笔记](../papers/when-model-meets-new-normals/notes.md#11-limitations-and-reproduction-value)）
- 在线阈值如何在不查看测试标签时兼顾逐点检出与事件级误报成本？（PDF pp.5, 7）
- Appendix 对 WADI 的 FP/TP 数值与变化方向为何不一致；Table 12 的计数使用什么阈值口径？（PDF pp.10, 15）


## From CAROTS reading

- 因果保持的正常负载变化、故障和因果机制切换如何区分？静态训练图在运维模式变化后何时过期？（PDF pp.1, 4, 17；[CAROTS 笔记](../papers/carots/notes.md#13-questions)）
- 如何验证 CUTS+ 得到的因果图与 CPA/CDA 的语义保真度，而不只看图相似度和下游分数？（PDF pp.15–18）
- 为什么 (A_{CD}) 在 WADI 与 SWaT 等数据集贡献不同；是否需要上下文门控或独立校准？（PDF pp.8, 17）
- 业务负载、发布、Trace 等外生上下文能否改善因果图在多种正常工作模式间的迁移？（Appendix §D）


## From CrossAD reading

- query 库和全局多尺度原型是否对应稳定、可解释的正常运行状态，还是仅为统计子序列聚类？（PDF pp.6–7, 22–25）
- 负载 / 发布变化导致跨尺度映射改变时，如何识别合法的新正常；若异常同时发生，如何防止原型更新吸收故障？（PDF §§3.2–3.3; Appendix A）
- 原型上下文是否在测试阶段更新？正文聚焦训练更新，而 Algorithm 1 写“每个新窗口”，需核实代码及具体推理流程。（PDF p.7; p.21）
- 主文声称全数据集 VUS 指标领先，但 SWAN VUS-ROC 表格低于 TimesNet；Table 3 消融增幅文字与表值计算也不完全一致，差异来源是什么？（PDF pp.8–10, Tables 1, 3）
- 跨尺度重构与 CAROTS 跨变量预测关系能否联合，以区分局部—全局形态变化和变量联动变化？目前尚无组合实验。（CrossAD §§3–4; CAROTS note）


## From Fortifying Time Series reading

- DTW 半径及 warping window 是否在具体业务领域代表语义保持变化，还是会把某些真实故障（如延迟 / 时间偏移）纳入同一等价类？（PDF §§3.1–3.2）
- Keogh lower bound 产生的零证书样本在经验 DTW 攻击下是否稳定；更紧下界可提高多少可认证覆盖率？（PDF §3.2, Theorem 3.3; Appendix F）
- 如何在不看测试标签的情况下联合选择平滑噪声 $\sigma$、序列长度 $T$、DTW 窗口 $w$、告警阈值和线上时延预算？（PDF §§4–5）
- 认证后分类仍可能是错误的旧决策；如何将正确性、事件级代价及多种正常运行状态纳入安全声明？（PDF §§3–4）
- 本地 PDF 的 NeurIPS 2025 标记与 2026 arXiv v1 标记对应哪个公开版本，会议终稿是否一致？（PDF p.1）


## From MACE reading

- 未见服务在 Table VIII 的 context-aware DFT bases 从何处获得？结果是否需要目标服务的未标注正常窗口，或确为无需目标样本的 zero-shot？（PDF §§IV-C, V-B）
- 如何把静态 service-specific pattern subspace 扩展为同一服务随 workload、时段、发布及扩缩容切换的多种正常运行态？（PDF §§I, IV-C）
- 频谱高方差 / 正向 i.i.d. amplitude shift 假设是否适用于低能量、相位型和跨变量关系型故障？（PDF pp.5–8, Theorems 1–2）
- F1 使用的阈值协议、reconstruction norm 和测试期标签使用能否从 supplementary code 明确复现？（PDF §§III, V）
- 负载变化和故障同时发生时，静态服务正常谱基如何避免把短期故障并入常见模式？论文尚无该并发场景实验。（PDF §§IV–V）


## From Graph-MoE reading

- Graph-MoE 的 memory 在实体、窗口、训练 / 测试边界间如何初始化和重置？异常窗口是否会进入 memory？（PDF pp.4–5, Eqs. 12–16）
- 动态 attention graph 能否与真实 service topology、Trace 或已知业务状态对齐？潜在相关结构不能直接当作因果依赖。（PDF pp.3–4, Eqs. 5–6）
- SWaT 原测试序列再拆为 train / validation / test 后，严格独立测试、固定阈值和事件级结果是否仍保有提升？（PDF p.5, Implementation Details）
- 记忆路由能否区分正常负载变化和同一时间段叠加的故障？论文没有该并发场景实验。（PDF §§3–4）


## From CCM-TAD reading

- 当业务负载切换导致跨通道相关 profile 改变时，训练期静态 cluster 如何迁移？何时需要重建 cluster？（PDF §3.2; Appendix J.5）
- causal temporal mask 能保证时间位置的信息流方向，但能否与 workload / Trace 结合识别业务语义和真实通道因果机制？（Appendix M）
- Best-F1 通过测试标签联合搜索 $\alpha,h$；部署前固定阈值的真实在线分数与该 oracle 值差距多大？（Appendix F, Eq. 24）
- 累积分数与边界校正在间歇故障、低强度持续波动及负载峰谷并发时的延迟 / 合并率如何？（PDF §3.4, Eqs. 14–17）
- 相关 profile clustering 对 PSM 的 NN-sep 几乎无增益，什么数据条件决定聚类表示真正有用？（PDF §4.2.3, Table 6）


## From TFC reading

- TFC 如何将融合输出 $\\hat Y$ 转成逐点异常分数并定义训练 loss？论文主文 / 附录没有给出精确映射。（PDF §§3–4）
- 状态空间动机中的外生驱动 $u_t$ 如何进入实际算法？模型逐条单变量训练，未使用 workload / Trace / release 条件。（PDF Eq. 4; Appendix C）
- 曲率中心差分依赖 $t+1$，temporal Transformer 也未描述 causal mask；逐点在线告警延迟如何定义？（PDF Eq. 12, §3.3）
- 正常周期变化和真实故障并发时，frequency branch 是否会校准掉故障证据？论文没有该并发情景实验。（PDF §3.4）
- Table 2 的 TFC TODS F1 / Event-F1 (.9258/.9155) 与 Table 1 (.9481/.9231) 不一致，差异来自何种 run / protocol？（PDF pp.6–8, Tables 1–2）


## Knowledge Review v4: TSAD batch 2 status update

本节基于 CAPMix、When Model Meets New Normals、CAROTS、CrossAD、Fortifying Time Series、MACE 六篇已完成笔记；更多 TSAD 论文尚待读，结论可继续变化。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | MACE 学习跨服务频率子空间，CAROTS 通过 SOC 保留共享因果关系下的多样正例，CrossAD 用跨窗原型，WMMNN 在线跟随分布；尚未证实能识别并命名同一服务的动态业务状态。 |
| 正常波动和真实故障如何区分？ | Partially Answered | 已有形态、趋势、因果依赖、跨尺度映射、服务频谱等证据，但尚无 workload / release 外部核验和负载—故障并发实验。 |
| 是否利用 Metric、Trace、业务负载与运行上下文？ | Open | 六篇均以时序为主；MACE 用服务身份作静态条件，CAROTS 将外生变量列为未来方向，未见成套 Trace / workload / release 条件化验证。 |
| 检测机制能否解释波动来源？ | Partially Answered | CAROTS、CrossAD、MACE 引入变量关系、尺度关系或频率模式，但没有业务事件根因解释链。 |
| 如何处理正常负载变化与真实故障并发？ | Open | 六篇没有系统构造这类测试；更新污染、静态正常参考失配、因果结构切换和窗口原型安全性仍待研究。 |
| 哪些技术方向已有先行工作？ | Partially Answered | 多服务 normality、online drift adaptation、multi-scale、causal TSAD、DTW attacks / smoothing 均已出现；创新性需定位到明确机制与新增实验。 |
| 哪些实验结论需谨慎解释？ | Partially Answered | 阈值、point adjustment、WADI / SWAN 表文差异、MACE 未见模式基来源、DTW certificate coverage 与在线成本都有限制。 |

详细分析见 [Knowledge Review v4](reviews/knowledge-review-v4.md)。


## Knowledge Review v5: TSAD batch 3 status update

本节基于 CAPMix、When Model Meets New Normals、CAROTS、CrossAD、Fortifying Time Series、MACE、Graph-MoE、CCM-TAD、TFC 九篇已完成精读；后续 24 篇可能更新结论。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有按服务静态频率子空间、测试时模型适应、跨窗原型、latent memory、训练期相关 profile clustering 等不同粒度；尚未证明可解释 workload / release 状态建模。 |
| 正常业务波动与故障如何区分？ | Partially Answered | 形态、趋势、因果 / 相关依赖、尺度、频谱、曲率、顺序证据均已提出；尚无外部业务状态核验或负载—故障并发矩阵。 |
| 是否使用 Metric、Trace、workload、release 上下文？ | Open | 生产数据源不等于多模态输入；九篇算法主要使用时序本身、服务身份或相关统计，未见成套 Trace / workload / release 条件验证。 |
| 异常分数是否解释波动来源？ | Partially Answered | Graph / causal / scale / frequency / curvature 让检测参照更结构化，但没有形成业务变更—指标变化—根因事件链。 |
| 正常负载变化和真实故障同时发生怎么办？ | Open | 九篇没有系统并发测试；在线更新、latent memory / prototype 写入和静态参照在此情形的风险尚未量化。 |
| 哪些机制已经提出？ | Partially Answered | 在线 normal adaptation、跨服务 / 跨窗多模式、关系建模、因果 TSAD、曲率异常、顺序告警均有具体论文，不应笼统称为全新空白。 |
| 哪些实验结果不宜直接外推？ | Partially Answered | Best-F1 的 test-label 阈值选择、窗口 AUROC、SWaT split、TFC 中心差分前视、表格数值差异及跨论文指标不统一需要保留。 |

详细比较见 [Knowledge Review v5](reviews/knowledge-review-v5.md)。


## Knowledge Review v3: TSAD batch 1

本表只汇总 CAPMix、When Model Meets New Normals 和 CAROTS 三篇提供的证据；状态可由后续论文更新。原始逐篇问题见上文。

| Question | Status | Current understanding |
| --- | --- | --- |
| 如何区分正常业务波动与真实故障？ | Partially Answered | 形态伪标签、测试时趋势适应和因果关系偏离分别提供线索，但缺少负载变化与真实故障并发的系统实验。（[Review v3](reviews/knowledge-review-v3.md#8-open-questions)） |
| 多种合法运行状态如何建模？ | Partially Answered | CAROTS 用因果保持增强和 SOC 纳入多样正例；WMMNN 学新状态但不命名模式；CAPMix 的单一均值中心可能受限。 |
| 检测分数能否解释波动来源？ | Partially Answered | CAROTS 增加跨变量预测关系证据，但不做业务事件或根因归因；其余两篇主要调整检测边界 / 状态。 |
| 是否显式利用 Metric、Trace、业务负载和运行上下文？ | Open | 三篇以时序指标为主，未形成 workload、Trace、发布事件的上下文校准；CAROTS 将外生变量列为未来方向。 |
| 负载变化与故障同时发生时如何安全处理？ | Open | 在线伪正常更新可能吸收漏检故障，固定因果图可能不适应机制切换，现有实验没有系统验证并发情形。 |
| 哪些方向已经有方法提出，哪些仍有证据空白？ | Partially Answered | 合成异常增强、测试期漂移适应、Granger / 因果异常检测均已有方法；创新点需超出既有机制并经全批 33 篇复核。 |
| 关键结论有哪些实验缺口？ | Partially Answered | 线上阈值与告警成本、因果图真值、在线污染稳定性、跨组织迁移及波动来源解释均缺充分证据；WADI 数字口径需要复核。 |


## From GCAD reading

- 单一正常因果图均值如何区分合法负载 / 控制阶段切换与故障导致的关系变化？高阶交互和多故障并发怎样表达？（PDF §§3, Conclusion；[GCAD 笔记](../papers/gcad/notes.md)）
- loss-gradient 得到的 Granger influence 是否与真实拓扑、干预或故障传播一致？如何评估图边语义，而非只看 anomaly AUROC？（PDF Eqs. 2–6）
- Table 1 若干数据点数与常用全量规模不同，预处理 / 子集划分以及窗口标签对齐的具体实现是什么？（PDF p.5）
- 正常负载切换与故障同时出现时，静态 $A_{norm}$ 的偏差能否归因；无代码公开下怎样精确复现 $P$ 积分、抽样数和 $h,\beta$？


## From OracleAD reading

- 多个正常运行状态下，epoch 平均的单一 SLS 是否会混成并不存在的中间结构？能否用状态条件 / 多模板 SLS，且避免负载—故障并发时错误更新？（PDF §§3.2, I；[OracleAD 笔记](../papers/oraclead/notes.md)）
- 对称 latent-distance deviation 与真实 service topology、Trace、故障注入根因的关系如何验证？偏差矩阵的变量排序是否在全测试集而非精选案例上有效？（PDF §4.3, Appendix G）
- prediction score × deviation score 是否会压低仅存在于单一分量的异常证据？窗口延迟和恢复期拖尾如何影响事件级报警？（PDF §§3.4, 4.3）
- 测试标签 oracle threshold 对 F1 的提升有多大；主文与 ablation 中 SMD 子集口径差异应如何复现？（PDF Tables 1–2, Appendix D.3）


## From SARAD reading

- workload / 控制状态切换导致的 attention association reduction 与故障 SAR 如何区分？负载和真实故障并发时 progression autoencoder 会过滤哪类证据？（PDF §§3.3–3.4；[SARAD 笔记](../papers/sarad/notes.md)）
- attention map 是否跨初始化稳定，并对应已知传感器拓扑、Trace 或干预关系？progression detection 对物理根因的解释效度如何验证？（PDF §§3.2–3.3）
- $2W=100$ 的前后窗对短异常产生多大稀释 / 延迟；多尺度窗口如何在 feature 数增加时保持 $O(N^2)$ 计算可控？（PDF §4, Appendices H, N）
- 当前主诊断分数用 data reconstruction residual，空间 progression 的变量归因贡献有无全量 forensic ground truth 验证？SWaT / HAI attack-origin labels 如何影响诊断结论？（PDF Eq. 6; Appendix E.3）


## Knowledge Review v9: TSAD batch 7 status update

本节合并 21 篇已完成的 PDF 精读结果。AnomalyLLM、Delving、AnomSeer 的跨论文分析见 [Knowledge Review v9](reviews/knowledge-review-v9.md)。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有 per-channel prototypes、多服务 / 窗口 / 频谱 memory、测试时 adaptation、周期分解与多视图机制；多数按形状、关系或周期表达，尚未证明用 workload / release 语义安全识别并更新合法状态。 |
| 正常业务波动和真实故障如何区分？ | Partially Answered | Delving 展示少量文本背景过滤已知可解释变化；AnomalyLLM 用 prototype discrepancy，AnomSeer 用 label-matched statistics。没有在真实业务 context 下联合测状态变化 / 故障 / 并发 / 未见状态。 |
| 方法是否只抑制噪声，或能解释波动来源？ | Partially Answered | AnomalyLLM 输出表示距离；Delving 可按模拟背景过滤；AnomSeer 能输出统计推理 trace。但尚未将说明与真实 event、Trace、拓扑或 fault cause 核验。 |
| 是否使用 Metric、Trace、workload、release context？ | Open | 数值 metrics 是主要输入；Delving 有 ETTh2 / Electricity 的 simulated natural-language context case，但本批没有系统利用真实 workload、release、Trace 数据。 |
| 正常负载变化与故障同时出现时如何处理？ | Open | 21 篇都未建立受控的并发状态变化 / 故障评估矩阵。prototype、memory、online adaptation、context filtering 的更新 / 抑制安全性均待检验。 |
| 哪些方法已有类似思路？ | Partially Answered | Prototype normal references、seasonal decomposition、index-aware localization、synthetic perturbation、统计 probe trace、OT reasoning alignment 都已有论文实现；新研究需逐一定位差异。 |
| 哪些研究问题缺少充分实验？ | Partially Answered | context filter 是否伤害未知故障 recall、ExpCoT explanation faithfulness、GT trace supervision 外推、真实上下文输入、固定误报预算 / 延迟、短边界事件仍需证据。 |

### From AnomalyLLM reading

- 每个变量的 prototype pool 如何覆盖多个合法 workload / release 状态？prototype 在线更新时如何避免把漏检故障吸收为 normal？（PDF §3.2）
- prototype discrepancy 与 GPT-2 teacher discrepancy 各自贡献多少；在 validation-only threshold / 固定告警预算下少样本收益是否仍在？（PDF §§3–4）
- synthetic jittering、scaling、warping 与真实故障和合法大幅业务波动的对应关系是什么？（PDF §3.4）
- 原文主设置 prototypes=32、敏感性结论偏好 48；WaQ / GECCO 的 Table 5 文字差异应由代码 / 作者配置如何解释？（PDF §§4.2–4.4, Tables 5–6）

### From Delving into LLMs for TSAD reading

- ACF dominant-period 分解在多周期、周期漂移、节假日 / 发布状态切换中是否会减弱真正频率故障？（PDF §3.1, Table 3）
- 如何用真实 workload、发布事件、Metric / Trace 产生可审计 context；模型过滤“已知可解释波动”时，未知故障 recall 是否下降？（PDF §5.2, Appendix D.6）
- 全量 TSB-AD、validation-only threshold 与统一事件延迟下，LLM 对 SR / 常规 detector 的准确率—成本曲线如何？（PDF §5.1, Appendix Table 9）
- Index-aware 在 GT localization-only setting 的增益如何映射到端到端检测，长序列 prompt length / API version 变化时是否保留？（PDF §4.2, Table 4）

### From AnomSeer reading

- ExpCoT 用 GT class / interval 构造并在 conclusion 中保留 GT 区间；移除定位答案信息、改用弱监督 / 无标签 references 后性能如何？（PDF Appendix B.2）
- 可以怎样独立验证生成解释的事实准确性与忠实性，而非只测其 embedding 更接近 ExpCoT？（PDF §5.3, Appendix D.3）
- 在同一服务多状态、负载与真实故障并发、未知异常类型时，统计 ExpCoT probe 会支持哪个假设？（PDF §§4–6）
- 真实 multivariate dependency、Trace / topology 和固定 false-alarm budget / streaming delay 下的效果、计算量如何？（PDF §6, Appendix D.4）


## Knowledge Review v6: TSAD batch 4 status update

本节汇总前四批 12 篇已完成精读；之后 21 篇尚可能改变当前结论。GCAD、OracleAD、SARAD 已分别增加逐篇问题，交叉比较见 [Knowledge Review v6](reviews/knowledge-review-v6.md)。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | WMMNN 测试时适应、MACE 服务条件频谱、CrossAD 原型、Graph-MoE memory、CAROTS 多样因果增强已提出；GCAD/OracleAD 的全局关系 reference 与 SARAD progression 均未使用业务状态语义。 |
| 正常业务波动和故障如何区分？ | Partially Answered | 形态、趋势、频谱、曲率、尺度与关系变化均有检测机制；尚无受控“状态变化 × 故障并发”矩阵。 |
| 是否利用 Metric、Trace、业务负载与运行上下文？ | Open | 目前主要学习指标序列及其统计 / latent 关系；MACE 用静态 service identity，未见 workload、Trace、release 的条件化验证。 |
| 方法是否解释波动来源？ | Partially Answered | 因果 proxy、latent structure 和 attention association 增加可视结构，但都未充分与真实 topology、Trace 或 fault-injection cause 对齐。 |
| 如何处理正常负载与故障并发？ | Open | 12 篇无系统并发测试；在线适应污染、固定关系模板误报、prototype / memory 更新安全仍需验证。 |
| 哪些方向已被提出？ | Partially Answered | online adaptation、跨服务 / 跨窗正常模式、causal augmentation / graph、关系变化、曲率和顺序检测已有具体机制；需明确新贡献边界。 |
| 关键评测还有何不足？ | Partially Answered | 测试标签 Best-F1、诊断标签不完整、不同 split / window / range metrics、GT 因果关系验证、在线延迟与告警成本均需逐篇留意。 |

#### 下一批计划（第 13–15 篇）

Quo Vadis、The Elephant in the Room、Temporal-Frequency Masked Autoencoders；先核对评测规范与 benchmark 证据，再和 MACE / TFC 的频域方法比较。


## Knowledge Review v7: TSAD batch 5 status update

本节综合 15 篇已完成全文精读的证据；后续 18 篇仍可能改变结论。Quo Vadis、TSB-AD 和 TFMAE 的单篇问题见下文；跨论文比较见 [Knowledge Review v7](reviews/knowledge-review-v7.md)。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有服务条件频谱、跨窗 prototype、latent memory、test-time adaptation、因果保持增强与 TFMAE 双视图一致性；尚未证明能按 workload / release 语义标记同一实体状态并在切换时保持故障敏感度。 |
| 正常业务波动和真实故障如何区分？ | Partially Answered | 已有形态、趋势、关系、频谱、跨尺度和曲率等统计证据；15 篇仍缺“仅状态变化 / 仅故障 / 并发 / 未见合法状态”控制矩阵及固定运行点告警评估。 |
| 是否利用 Metric、Trace、负载和运行上下文？ | Open | 本批三篇主要研究评测或数值时间序列，没有把 workload、release、Trace 作为检测输入并做条件验证。 |
| 方法是否解释波动来源？ | Partially Answered | TFMAE 的视图 discrepancy 是偏离分数，TSB-AD 是 benchmark；不解释业务来源。早先关系方法增加结构证据，但尚未充分与 Trace / topology / fault cause 对齐。 |
| 如何处理正常负载与故障并发？ | Open | 15 篇均没有系统并发测试；局部 CV mask、静态 reference、在线适应和关系更新在此条件下的作用未量化。 |
| 哪些技术方向已被提出？ | Partially Answered | 简洁统计 baseline、curated multi-metric benchmark、frequency masking、多视图对比、multi-pattern spectral reference 和 test-time adaptation 均已有具体方法。 |
| 关键评测还有何不足？ | Partially Answered | Quo Vadis 展示 test-label Best-F1 / PA 风险；TSB-AD 提供十指标与 VUS-PR 分析但主结果固定 seed；TFMAE 主表使用 PA-F1 且依异常率阈值。数字不可跨协议直接排名。 |

### From Quo Vadis reading

- 哪些公开数据和预处理设定下，PCA / 1-NN 的强结果会失效？是否由非线性关系、状态条件变换或事件级诊断提供额外收益？（PDF §§3–4, Tables 2–5）
- test-set best threshold 与 validation-only、normal-only calibration 的差距多大？主文 point / range / PA 指标的排序在统一 entity split 后是否保留？（PDF §3.5, p.6）
- 线性 student 在两个多变量 benchmark 上近似 deep model，是否能扩展到其他 anomaly type、事件定位及真实 streaming setting？（PDF §4.3, Table 4）

### From TSB-AD reading

- detector-assisted curation 是否改变最终异常难度或模型族表现？需要 detector-blind holdout、独立标注者与标注 uncertainty 检验。（PDF §4.1.2）
- UTS channel derived from MTS 的依赖性，以及主结果单 seed 对 detector rank 的影响应如何量化？（PDF Table 2; checklist p.17）
- 如何以 workload、release、Trace 和故障并发标注扩展 benchmark，并将 VUS / event metrics 与告警成本和检测延迟对齐？（PDF §§4–5）

### From TFMAE reading

- 局部 high-CV 的合法业务峰谷和真实故障如何区别；频域低幅值 mask 是否可能遮盖弱但关键的周期模式？（PDF Eqs. 1–10; Table V）
- adversarial symmetric-KL 是否跨随机种子和不同正常状态稳定？新状态与故障并发时 discrepancy 的变化是什么？（PDF Eqs. 14–16; Fig. 9）
- anomaly-rate threshold 错配、无标签正常 calibration、非 PA interval metric 和事件延迟下的表现如何？（PDF §V-A, Table III）


## Knowledge Review v8: TSAD batch 6 status update

本节整合 18 篇已完成全文精读；后续 15 篇仍可能改变结论。TriAD、PCRTA、Sub-Adjacent Transformer 的逐篇问题见下文，交叉比较见 [Knowledge Review v8](reviews/knowledge-review-v8.md)。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有 periodic residual / 多域表示、perturbation pseudo-label、sub-adjacent temporal context、test-time adaptation、频谱和 memory 等，但未按业务运行状态语义建模并验证状态迁移。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | 已有频域、局部扰动、窗口离群、关系与重建上下文等 statistical evidence；没有状态变化 / 故障 / 并发 / 未见状态的统一控制实验。 |
| 是否使用 Metric、Trace、workload、release context？ | Open | TriAD、PCRTA、Sub-Adjacent 均从数值时序及变换视图构造分数，没有引入业务上下文或 Trace。 |
| 方法是否解释波动来源？ | Partially Answered | TriAD 定位候选时窗、PCRTA 学扰动类别、Sub-Adjacent 显示低 attention contribution；这些证据不等于业务原因或根因归因。 |
| 如何处理正常负载变化与真实故障并发？ | Open | 18 篇没有系统并发矩阵；单事件 top-1 window、fixed perturbation family、fixed sub-adjacent band 均需检验。 |
| 哪些方向已有先行机制？ | Partially Answered | 多域 contrast、synthetic anomaly perturbations、LOF representation scoring、局部上下文 attention constraint、variable-length discord search 均已有具体实现。 |
| 哪些结果不可直接外推？ | Partially Answered | TriAD 假设每条 test series 一个 anomaly event；PCRTA 和 Sub-Adjacent 用 test-best F1；Sub-Adjacent 还用 point adjustment 与 pooled/per-entity 混合比较。 |

### From TriAD reading

- 每条测试序列 $Z=1$、top-1 candidate window 对多事件 / 持续故障 / 状态切换的表现如何？（PDF §§III-D, IV-A）
- periodic residual 的估计实现和 period estimation error 会怎样影响频率 / residual ranking？（PDF §III-B, code）
- vote threshold、MERLIN candidate intervals 和异常窗口 fallback 如何在固定误报预算、无 PA event metric 下校准？（PDF §III-D, IV-B, IV-G）

### From PCRTA reading

- 六种固定 synthetic perturbation 是否覆盖真实领域异常？能否将其和正常业务峰值、release、慢漂移作受控对照？（PDF §III-C, Table 1）
- pseudo-label 分类混淆是否跨 seed 稳定；若合法的新正常类别也难判，contrastive objective 是否放大误分？（PDF §§III-C–D, Table 3）
- validation-only threshold 与 test-best F1 的差距、七个 LOF view 的端到端时延和边界对齐怎样报告？（PDF §§III.1, IV）

### From Sub-Adjacent Transformer reading

- sub-adjacent distance band 能否随采样率、period、运行负载状态自适应？循环窗口边界是否带来不真实的首尾关系？（PDF §3.2, Eqs. 1–4）
- 局部状态切换和长持续异常是否同样无法从 sub-adjacent neighborhood 重建？怎样与真实故障区分？（PDF §§3.2–3.3）
- test-best threshold / point adjustment / pooled-vs-per-entity protocol 对主表增益影响多大？（PDF §§4.2–4.4, Tables 2–8）


## Knowledge Review v10: TSAD batch 8 status update

本节汇总 24 篇已完成 PDF 精读；第 8 批三篇跨论文比较见 [Knowledge Review v10](reviews/knowledge-review-v10.md)。

| Question | Current status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | Prototype / memory / spectrum / adaptation、同序列 visual reference 与 RCD context、IMPACT reference normals 均已有机制；business-state 语义和安全切换仍未解决。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | 有 visual trend verification、context-relative discrepancy、text filtering、因果依赖和 risk influence；没有真实状态改变 + 故障并发控制矩阵。 |
| 只抑噪声还是解释波动来源？ | Partially Answered | 有 relational / visual / influence evidence，但未系统对齐 workload、release、Trace 或根因 ground truth。 |
| 是否利用 Metric、Trace、workload、release？ | Open | 主要为数值 metric；少数模拟文本 context；没有系统真实 Trace / release-conditioned evaluation。 |
| 正常负载变化和真实故障同时发生时怎样处理？ | Open | TimeRCD context contamination、VLM4TS dense anomaly recall、IMPACT rare-normal flips 都暴露相关安全问题，但未形成统一并发实验。 |
| 哪些机制已经被提出？ | Partially Answered | Patch visual verification、synthetic RCD pretraining、influence-guided open-set cleaning、prototypes / memory / online adaptation 均已有具体方法。 |
| 哪些关键结论缺实验支持？ | Partially Answered | Generator-held-out、真实业务 context safety、rare-group robustness、rationale fidelity、validation-only calibration 和固定运行点仍不足。 |

### From Harnessing VLMs for TSAD reading

- Yahoo A3/A4 dense anomaly setting 下，如何同时提升召回并避免把真实重复异常压成 broader visual pattern？window size / threshold 是否应根据序列状态自适应？（PDF §4; Appendix D.4）
- confidence 1–3 是否校准；full-series min/max plot scaling 对极端值和合法幅值切换是否敏感？（PDF §§3.1–3.2）
- 真实 workload / release / Trace 作为 VLM context 后，哪些过滤是 benign fluctuation、哪些会误删未知故障？API latency / fixed FPR 下表现如何？（PDF §3.2, Table 2）

### From TimeRCD reading

- context window 含高比例 anomaly 时，怎样避免错误更新 / 污染序列内 normal reference；是否需要 context quality gate 或多状态 reference？（PDF §3.3）
- 同一 generator family 上 train / held-out contextual test 能否外推到 generator-held-out 及真实业务状态？（PDF §2.3; Appendix E.2）
- 固定 5k context、严格不调 target 的优势在 validation-only calibration、固定误报预算、在线流式延迟下如何？（PDF §3.1–3.3）

### From IMPACT reading

- validation influence 是否能区分 contamination 与 rare but valid normal group；组别 / workload 条件化 validation 是否降低错误翻标？（PDF Appendix I）
- 如果不允许从 test anomaly 抽样构造污染，或 validation 标签不完备，影响排序与 label flipping 还能否成立？（PDF §4.1; Appendix E, H.3）
- feature-space synthetic anomalies 能否映射到可解释的 temporal / causal fault patterns；AUC 结论在 fixed false-alarm thresholds 下是否保留？（PDF §§3.2–3.3, Appendix H.4）


## Knowledge Review v11: TSAD batch 9 status update

本节汇总 27 篇已完成 PDF 精读；第 9 批跨论文机制与证据边界见 [Knowledge Review v11](reviews/knowledge-review-v11.md)。

| Question | Status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 除多原型、频谱、适配和上下文参照外，已有 Fourier 平滑函数、统计趋势恢复及 fixed-point manifold；均未充分证明有业务状态语义和安全切换。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | 平滑、趋势、重建、关系、视觉、影响分数提供不同证据；三篇未用 workload / release 真值与并发矩阵验证来源区分。 |
| 方法是否只抑噪，是否解释波动来源？ | Partially Answered | 检测机制已超出简单抑噪，但分数 / attention / fixed-point 仍不等于业务来源归因。 |
| 是否使用 Metric、Trace、workload、release？ | Open | 27 篇 TSAD 以数值序列为主；尚无系统真实 Trace / release-conditioned 比较。 |
| 正常负载变化与故障并发时如何处理？ | Open | 训练污染、Gaussian noise、非平稳 benchmark 分别覆盖有限情形，不能替代并发控制测试。 |
| 哪些机制已经提出？ | Partially Answered | 多模式 prototypes / memory、频谱 normality、TTA、context-relative scoring、open-set influence、平滑预测、趋势重建、幂等流形均已有具体方案。 |
| 哪些研究空白有论文依据？ | Partially Answered | rare-normal 错分、模块回退、各类鲁棒 protocol 不可比、score / normalization 细节、固定 FPR 与延迟在所读论文中均有证据边界。 |

### From KAN-AD / RTdetector / IGAD

- Fourier 截断在局部真实故障与随机噪声并存时的召回 / 误报如何变化？（KAN-AD §§3–4, Fig. 7）
- RTdetector 的 Eq. (3) 反归一化括号在官方代码中如何实现；非重叠窗口下的事件边界和延迟是什么？（RTdetector §3.2, Eq. 3; §4）
- IGAD 的高斯频域采样是否破坏相位 / 谱相关；无需逐模型调参时能否保留收益？（IGAD §3.1; Appendix E.3）
- tightness / 平滑先验是否排斥稀有但合法的业务状态？需按状态组报告误报率，并注入同时发生的故障。（IGAD §3.2; KAN-AD §3; IMPACT Appendix I）
- 三篇能否在统一 validation-only threshold、固定 FPR、event delay 和真实负载变化 / 故障并发矩阵下比较？（Knowledge Review v11 §5–6）


## Knowledge Review v12: TSAD batch 10 status update

当前共完成 30/33 篇 PDF 精读；第 10 批跨论文差异和证据边界见 [Knowledge Review v12](reviews/knowledge-review-v12.md)。

| Question | Status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 多中心 / memory、context、统计趋势、动态适配、变量角色和 residual noise null 已提出；业务状态语义与安全迁移缺少统一实证。 |
| 正常业务波动和真实故障如何区分？ | Partially Answered | scattering、NIS、ERI 和 reconstruction score 提供 statistical departure evidence，但不能说明波动来自负载还是故障。 |
| 方法是否只抑噪，是否解释来源？ | Partially Answered | 结构化分数、通道作用和统计检验增强检测依据；尚无与 Trace / release / 注入根因的忠实性验证。 |
| 是否使用 Metric、Trace、workload、release？ | Open | 30 篇 TSAD 论文主要用数值时间序列，真实运行上下文 / Trace conditioned comparison 仍不足。 |
| 正常状态变化和故障并发如何处理？ | Open | 无完整真实控制矩阵；静态 ERI、全局散布中心、fixed R / NIS 对状态切换的行为需测。 |
| anomaly onset 和持续区间是否同一优化目标？ | Partially Answered | COGNOS 明确偏 onset；ScatterAD Aff-F 对小偏移敏感；需统一 delay、coverage、boundary tolerance、固定 FPR。 |
| 图、变量角色是否能解释因果？ | Open | ScatterAD 图节点是时间步、TeamWork ERI 是统计依赖；二者都不直接证明 service topology / causal driver。 |

### From ScatterAD / COGNOS / TeamWork

- ScatterAD Eq. (10) 的 reciprocal distance 在代码中如何定义 / 归一化；随机 center 和 EMA seed 是否可复现？（ScatterAD §§3.3–3.4）
- ScatterAD 强噪声下的异常散布反转是否在其他高维 / rare-normal 数据出现？如何避免把正常群体判为异常？（Appendix D, Table 7）
- COGNOS NIS circuit breaker 对合法 workload / release transition 是否报警；持续状态的分数衰减会不会漏掉后续故障？（COGNOS §4.2; Limitations）
- COGNOS 在 heteroscedastic、相关通道噪声下需要何种 covariance-aware filter；global quantile calibration 如何无标签选择？（Appendix A.2; D.2）
- TeamWork ERI rankings 在不同 operating stages 是否稳定；若变量角色随状态变化，在线更新如何避免异常污染？（TeamWork Limitations, p.14）
- 三篇在“仅正常状态切换 / 仅故障 / 并发 / 未见合法状态”协议下的 event delay、区间覆盖和 group-wise FPR 如何比较？（Knowledge Review v12 §§4–7）


## Knowledge Review v13: TSAD completion status (33/33)

以下是 33 篇实际 PDF 精读完成后的工作状态；整体比较见 [Knowledge Review v13](reviews/knowledge-review-v13.md)，完整证据综合见 [TSAD final synthesis](reviews/tsad-final-synthesis.md)。

| Question | Status | Evidence summary |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有 prototypes / memory / frequency patterns / context-relative reference / test-time adaptation / latent dynamics / dynamic roles / global dependencies；但各自正常状态多由训练分布或模型内部统计表征，业务 workload / release 语义与安全切换缺少统一验证。 |
| 正常业务波动和真实故障如何区分？ | Open | 33 篇包含统计异常、上下文偏离、重建误差、鲁棒性、OOD 与 latent GOF；对真实业务 source 的区分仍需 workload / release / Trace 或 controlled injection 证据。 |
| 方法是否仅抑制噪声，是否解释波动来源？ | Partially Answered | 多数方法提供结构化偏离证据而非纯去噪，但 score / attention / flow / latent test 仍不等于已验证的业务因果归因。 |
| 是否利用 Metric、Trace、业务负载和运行上下文？ | Open | 已读 TSAD 论文主体仍以数值序列、频谱、图表示或人工构造上下文为主；未形成基于真实 Metric–Trace–release–workload 的统一条件检测比较。 |
| 如何处理负载变化与故障同时发生？ | Open | 未发现跨 33 篇统一控制“仅状态切换 / 仅故障 / 同时发生 / 未见合法状态”的实验矩阵。WMMNN、TimeRCD、IMPACT、CNF 等给出相关机制或风险，但不等于已解决并发区分。 |
| 哪些思路已经被提出？ | Partially Answered | 多模式原型 / memory、test-time adaptation、context reference、因果 / 关联结构、open-set cleaning、robustness certificate、residual null、multi-view score fusion、latent GOF 均有论文实例；每类适用假设和运行语义需逐篇对照。 |
| 哪些结论缺少充分实验？ | Partially Answered | 主要缺口包括合法 rare-state group FPR、state transition × fault 并发、context attribution fidelity、uncertainty calibration、validation-only fixed-FPR、event delay 与区间覆盖，以及跨数据源 / generator 外推。具体论文证据见综合报告 §5。 |

### From AnoMamba / FlowFuse / Conditional Normalizing Flows

- GSR hidden attention 能否在 workload / release 干预下忠实反映真实依赖，而不是只解释 reconstruction attribution？（AnoMamba §5.8, Figs. 6–7）
- FlowFuse 的 ensemble disagreement 是否校准；当四个 base views 在状态漂移时相关性失败，融合能否识别共同盲点？（FlowFuse §§3.4–4.4）
- CNF 的 FIT 在目标线上环境是否能预测 false alarm / event recall；如何把单一 LG-LDM 扩展到多个合法动态而不吸收故障？（CNF §§3.2, 4.2, 5）
- 对三类方法建立统一的 context-shift × fault concurrency protocol 后，其 benchmark 增益能否在固定 FPR、event delay、duration coverage 和 group-wise false alarm 下保留？（Knowledge Review v13 §§3–4）

## AIOps Knowledge Review v4: LLM-Driven Microservice Anomaly Generation

专题论文比较见 [AIOps Knowledge Review v4](aiops/reviews/aiops-knowledge-review-v4.md)。下列状态只表示当前六篇全文阅读所覆盖的证据范围。

| Question | Status | Current understanding |
| --- | --- | --- |
| 生成数据真实性需要哪些彼此独立的验证层？ | Partially Answered | 当前材料区分格式 / 结构、局部统计或表征、下游任务收益、运行时故障干预和多模态诊断；没有单一通用真实性指标。 |
| 正常业务变化与真实故障能否按来源可靠区分？ | Open | 有正常负载曲线、少量 no-op 任务和现有 TSAD 新正常 / 鲁棒增强方法；缺少覆盖正常变化、故障及两者并发的统一微服务验证。 |
| 生成 Metric、Trace、Log 是否在同一故障机制下保持一致？ | Open | TraceLLM、LLM-AP、GenIAS 分别是单类生成；运行环境可共同产生多模态观察，但尚无本专题已读生成器做同根因联合合成并检验一致性。 |
| LLM 生成是否优于传统生成？ | Partially Answered | TraceLLM 在若干图任务和 LLM-AP 在部分 NAB detector 有效；GenIAS 作为 VAE 对照也有效。没有统一真实微服务数据、相同验证与下游预算下的比较。 |
| 合成样本上的指标增益是否迁移到真实微服务故障？ | Open | TraceLLM 有图任务 synthetic-train / real-test；LLM-AP 和 GenIAS 缺少真实微服务故障评估；两个 live testbed 论文未做生成增强收益测量。 |
| AMulSys 的增强 / 混合图机制是什么？ | Open | 已确认出版元数据但未取得全文；摘要预览不够支持机制结论。 |
