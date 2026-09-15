# Learning Log

记录每次学习的日期、材料、主要收获、概念更新和后续行动。

建议格式：

```markdown
## YYYY-MM-DD

- Materials:
- What I learned:
- Concepts updated:
- New questions:
- Next steps:
```

## 2026-09-14

- Date: 2026-09-14
- Paper: ReAct: Synergizing Reasoning and Acting in Language Models
- Core takeaway: ReAct 将不改变环境但能更新 context 的 language thought，与会产生 Observation 的外部 Action 交错起来，形成 reasoning 与 acting 的闭环。
- New concepts: interleaved reasoning/action、Observation grounding、language-mediated planning、working-memory-like context（解释性说法）。
- Open questions: Thought 是否忠实反映 internal state，以及这种 plan-like behavior 如何扩展为长期 Memory 和结构化 tool use。
- Next step: 对比 ReAct 与现代 tool calling、planning 和 memory 系统的边界。

## 2026-09-14

- Date: 2026-09-14
- Paper: Toolformer: Language Models Can Teach Themselves to Use Tools
- Core takeaway: Toolformer 用候选 API 执行结果带来的 future-token loss 降低作为自监督信号，让 LM 学会何时、如何调用文本工具；这与 ReAct 的运行时 Thought/Action/Observation 闭环不同。
- New concepts: loss-based call filtering、inline textual API result、tool-augmented LM 与完整 Agent 的边界。
- Open questions: 如何把 learned call policy 迁移到 structured tool calling / MCP，以及如何支持可靠的链式、交互式调用。
- Next step: 比较更多 tool-use 方法，区分训练得到的调用策略与运行时 Agent trajectory。

## 2026-09-14

- Date: 2026-09-14
- Paper: Reflexion: Language Agents with Verbal Reinforcement Learning
- Core takeaway: Reflexion 用 Evaluator feedback 生成 verbal reflection，保存为受限的跨 attempt episodic memory；它改变下一次 context，而不是模型参数。
- New concepts: verbal reinforcement、reflection loop、episodic memory、Evaluator–Actor separation。
- Open questions: 错误 reflection 如何传播，以及 task-local memory 如何扩展为可靠的 persistent memory。
- Next step: 比较 reflection、critic 和其他 self-correction 方法。

## 2026-09-14 — Knowledge Review v1

- Scope: ReAct、Toolformer、Reflexion。
- Main conceptual changes: 将三篇论文分别定位为 runtime interaction、learned tool-use policy 和 cross-attempt feedback adaptation；明确区分 reasoning、planning、reflection、context 与 memory。
- Top open questions: Agent 与 tool-augmented LM 的边界；如何构造 explicit planning；如何让 feedback / memory 在错误累积下仍可靠。
- Next learning priorities: Explicit Planning and Replanning、Memory Architectures、Structured Tool Calling、Reflection / Critic / Self-Correction、Context Engineering。

## 2026-09-14

- Date: 2026-09-14
- Paper: LLM+P: Empowering Large Language Models with Optimal Planning Proficiency
- Core takeaway: LLM+P 将自然语言到 PDDL 的翻译与 classical planner 的显式计划搜索分开，说明 explicit planning 不等同于语言 Thought 中的 plan-like reasoning。
- New concepts: solver-backed planning、PDDL problem representation、LLM–planner boundary。
- Open questions: 如何验证 LLM 生成的 PDDL，以及如何把静态计划与执行中的 Observation 和 replanning 结合。
- Next step: 比较搜索式 world model planning 与 planner–executor / plan-first 架构。

## 2026-09-14

- Date: 2026-09-14
- Paper: RAP: Reasoning with Language Model is Planning with World Model
- Core takeaway: RAP 将 reasoning trajectory 组织为 state/action 搜索，用 prompted LLM 预测 imagined state，并由 reward 与 MCTS 选择候选路径。
- New concepts: world model、search-based reasoning、inference-time planning。
- Open questions: imagined state 如何由真实 Observation 校验，及搜索成本如何扩展到长任务。
- Next step: 比较 plan-first、world-model search 与 runtime observation loop 的组合方式。

## 2026-09-14

- Date: 2026-09-14
- Paper: ReWOO: Decoupling Reasoning from Observations for Efficient Augmented Language Models
- Core takeaway: ReWOO 用 Planner–Worker–Solver 将 foreseeable reasoning、工具执行和 evidence solving 分开，以减少 observation-interleaved context 的重复。
- New concepts: foreseeable reasoning、evidence placeholder、plan-first tool workflow、context efficiency。
- Open questions: 如何在 Planner 看不到未来 Observation 时判断是否需要 replanning，以及如何验证 evidence。
- Next step: 综合三篇 Planning 论文，明确 plan-like reasoning、explicit planning、search 和 replanning 的边界。

## 2026-09-14 — Knowledge Review v2

- Scope: LLM+P、RAP、ReWOO；以 ReAct、Toolformer、Reflexion 和 Knowledge Review v1 为背景。
- Main conceptual changes: 将 Planning 区分为 plan-like、formal solver-backed、search-based 和 plan-first workflow；明确 Observation、imagined state、evidence 与 replanning 的边界。
- Top open questions: 如何校准 world model 和真实 Observation；何时在 plan-first 与 runtime interaction 间切换；如何验证并修正动态环境中的计划。
- Next learning priorities: Replanning and feedback-grounded planning、Planner–Executor 与 structured plans、World Models、planning-aware tool use / context engineering、Planning evaluation。

## 2026-09-15

- Date: 2026-09-15
- Paper: RCAgentBench: An Agent-Oriented Benchmark for Multimodal Root Cause Analysis in Microservices
- Core takeaway: RCA 应把 metrics/logs/traces 的证据获取、组件定位、故障类型、解释覆盖和诊断路径成本分开评估；工具和层级结构本身会显著影响 Agent 结果。
- New concepts: AIOps RCA task boundaries、multimodal telemetry、topology-aware RCA、process-level RCA evaluation。
- Open questions: 网络场景的候选根因空间、跨模态时间对齐、物理拓扑与服务调用图的可迁移性。
- Next step: 阅读 StaR，检查动态拓扑与 stateful causal RCA 如何定义候选根因和时间信息。

## 2026-09-15

- Date: 2026-09-15
- Paper: StaR: Stateful Dynamic-Graph Root Cause Analysis through Memory-Enhanced Causality Discovery
- Core takeaway: StaR 用时序模型状态和动态消息传递处理变化依赖与延迟传播；它的 memory 是模型 temporal state，不是 Agent memory，且 Granger-style predictive relation 不等于物理因果。
- New concepts: stateful causal RCA、dynamic graph semantics、innovation-based root ranking。
- Open questions: 学习到的动态图如何与网络物理拓扑对齐，metric-variable candidates 如何映射到设备/接口/链路。
- Next step: 阅读 CAUSALDX，比较 anomaly graph、LLM causal reasoning 与 observation verification。

## 2026-09-15

- Date: 2026-09-15
- Paper: CAUSALDX: Diagnosing Long-Tail and Cascading Cloud Incidents with LLM-Guided Causal Reasoning
- Core takeaway: CAUSALDX 将初始 anomaly observations 与 select→expand→verify 的开放候选搜索分开，并用外部工具验证根因；其 anomaly graph 是诊断依赖结构，不自动等于物理因果图。
- New concepts: open-set RCA、anomaly dependency graph、verification-grounded diagnosis。
- Open questions: 网络场景如何校准候选扩展、定义独立验证证据，以及统一 root-set 与层级 top-k 评价。
- Next step: 阅读 LLMGuard，比较生产环境中 SOP tree、确定性执行和 Agentic RCA 的边界。

## 2026-09-15

- Date: 2026-09-15
- Paper: LLMGuard: Multi-Agent Fault Diagnosis for Reliable Language-Model-as-a-Service
- Core takeaway: LLMGuard 用 LLM 做 SOP 解析、检索、树规划和总结，但让在线检查沿确定性的 SOP Checking Tree 执行；生产 RCA 的关键约束是知识覆盖、工具验证、证据链、延迟和人工升级。
- New concepts: production evaluation axes、SOP-based diagnosis、deterministic Agent workflow。
- Open questions: 网络场景如何表达连续/不确定证据，以及如何发现 SOP 覆盖不足的未知根因。
- Next step: 阅读 KAT，比较知识图谱、跨子系统上下文和持续更新在真实电信排障中的作用。

## 2026-09-15

- Date: 2026-09-15
- Paper: KAT: Knowledge-Context Augmentation for Evolving LLM-Based Telecom Troubleshooting
- Core takeaway: KAT 用 troubleshooting knowledge graph、跨子系统 context enhancement 和反馈驱动更新处理演化中的电信错误；真实部署很强，但它是知识增强 LLM troubleshooting，不足以直接称为完整 Agent 或物理拓扑 RCA。
- New concepts: operational knowledge lifecycle、graph-grounded context、production outcome versus RCA correctness。
- Open questions: 如何把知识图谱连接到原始网络 telemetry 与物理 topology，并处理知识过期、冲突和安全验证。
- Next step: 综合五篇论文，完成 AIOps Knowledge Review v1，形成 multimodal/topology/production RCA 的统一但谨慎的 mental model。

## 2026-09-15 — AIOps Knowledge Review v1

- Scope: RCAgentBench、StaR、CAUSALDX、LLMGuard、KAT。
- Main conceptual changes: 将 AIOps RCA 拆成 detection、candidate generation、topology/dependency constraint、ranking/verification、localization、diagnosis、explanation 和 remediation；明确五类 graph/candidate semantics 并区分 production data、scale 与 deployment。
- Top open questions: 网络多模态 telemetry 与 traffic/NetFlow 对齐、物理 topology 与 learned dependency 的关系、unknown/multi-root ground truth、LLM 相对 tools/knowledge 的独立价值。
- Next learning priorities: network-specific multimodal RCA、dynamic physical topology、open-set/multi-root diagnosis、可靠 tool/knowledge-grounded Agent、production remediation safety。

## 2026-09-15

- Date: 2026-09-15
- Paper: Comfey: An Agentic Framework for Triaging Incidents in Production Cloud Infrastructure
- Core takeaway: Comfey demonstrates a production, decentralized team-routing loop: local agents enrich and accept/reject incidents, while TSGs, historical cases, and a shared routing table guide transfer; its labels measure team ownership, not physical root cause.
- New concepts: production incident triage as a separate AIOps layer; team-local evidence sovereignty; statistical routing memory.
- Open questions: how to map ownership routing to network device/link RCA, detect stale routing knowledge, and isolate LLM value from rules and routing statistics.
- Next step: read AIM and compare multimodal alert-to-mitigation planning with Comfey’s triage boundary.

## 2026-09-15

- Date: 2026-09-15
- Paper: AIM: Leveraging LLMs for Alert Summarization and Mitigation Plan Generation
- Core takeaway: AIM aligns multimodal telemetry at prompt level, retrieves relevant historical exemplars, and separates mitigation planning from constrained Ansible execution; language/category alignment is substantially easier than reliable remediation.
- New concepts: prompt-level multimodal fusion; plan-to-act boundary; remediation success versus plan quality.
- Open questions: how to align imperfect network telemetry, verify generated actions, and measure physical RCA rather than category/text alignment.
- Next step: read StepFly to compare executable TSG DAGs with AIM’s generated plan/code path.

## 2026-09-15

- Date: 2026-09-15
- Paper: StepFly: Agentic Troubleshooting Guide Automation for Incident Diagnosis
- Core takeaway: StepFly compiles TSGs into DAGs and typed query plugins, then uses bounded scheduler/executors and external structured working memory to execute and parallelize documented diagnosis steps.
- New concepts: executable operational knowledge; DAG-constrained Agent workflow; structured tool-data memory.
- Open questions: how to detect out-of-coverage faults, update procedures under system drift, and retain/forget memory across incidents.
- Next step: read TSGen to compare generating operational guides with executing them.

## 2026-09-15

- Date: 2026-09-15
- Paper: TSGen: Automated Troubleshooting Guide Generation
- Core takeaway: TSGen filters and distills historical incident discussions into structured, human-reviewed TSG/DAG knowledge; it generates operational guidance but does not itself perform runtime RCA or remediation.
- New concepts: historical-incident knowledge curation; guide coverage versus RCA correctness; persistent operational knowledge versus Agent memory.
- Open questions: how to combine network multimodal telemetry, detect stale/out-of-coverage guides, and validate a generated guide before execution.
- Next step: read ChatRCA and compare generated operational knowledge with a human-in-the-loop multi-agent RCA workflow.
