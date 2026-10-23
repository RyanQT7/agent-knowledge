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

## 2026-09-15

- Date: 2026-09-15
- Paper: ChatRCA: A Root Cause Analysis Method via LLMs-based Multi-Agent with Human-in-the-Loop
- Core takeaway: ChatRCA uses role-specialized agents to collect multimodal evidence, add architecture/domain context, iterate hypotheses, and place human checks at data-ticket and root-cause decisions; it is human-gated RCA, not autonomous remediation.
- New concepts: agentic RCA with evidence work orders; multi-agent role specialization; human verification versus textual explanation quality.
- Open questions: how to scale human arbitration, validate open-set network RCA, and isolate multi-agent value from added context and review.
- Next step: complete AIOps Knowledge Review v2 for the Agentic Incident Management batch.

## 2026-09-15 — AIOps Knowledge Review v2

- Scope: Comfey, AIM, StepFly, TSGen, ChatRCA.
- Main conceptual change: separated operational-knowledge generation, incident routing, plan-to-act, DAG-constrained execution, and human-gated multi-agent RCA; established a cautious capability-based Agentic AIOps working model.
- Most important open questions: network-specific multimodal evidence and physical topology, independent value/cost of multi-agent workflows, and safe verified remediation with a complete memory/knowledge lifecycle.
- Next step: study network-specific multimodal/open-set RCA, Agent tool reliability and remediation safety, and production-oriented Agent evaluation.

## 2026-09-15 — Network AIOps Architecture Synthesis v1

- Scope: Ten completed AIOps papers and Knowledge Reviews v1/v2.
- Main conceptual change: formed a cautious hybrid RCA architecture in which deterministic/statistical/graph modules handle alignment, candidate space, topology, and safety; LLM/Agents handle bounded evidence synthesis and investigation; verification and human gates remain explicit.
- Most important open questions: network Evidence Provenance, physical plus dynamic topology, open-set/multi-root candidate pruning, and safe recovery evaluation.
- Next step: read a focused network multimodal or topology-aware RCA batch; do not assume the synthesis is an implemented system.

## 2026-09-15 — Cloud-OpsBench

- Date: 2026-09-15
- Paper: Freezing the Crime Scene: A State Snapshot Paradigm for Reproducible Agentic SRE Evaluation
- Core takeaway: deterministic snapshots and native-shaped mocked tools can make Agent investigation reproducible and expose process failures that final-answer metrics hide; this is an evaluation paradigm, not a production RCA or remediation system.
- New concepts: state-snapshot evaluation; process-centric Agent diagnosis metrics.
- Open questions: how to preserve network entity/time provenance and valid alternative investigation paths in replay, and how to connect snapshot results to live safety and recovery.
- Next step: read Cloud Intelligence/AIOps 2.0 for knowledge anchoring and bounded operational execution.

## 2026-09-15 — Cloud Intelligence/AIOps 2.0

- Date: 2026-09-15
- Paper: Cloud Intelligence/AIOps 2.0: Knowledge-Anchored Agentic AIOps
- Core takeaway: operational knowledge should be a versioned, owned, anchored artifact with evidence points, safety boundaries, validation status, and an evolution loop; the paper is a vision, not a standalone empirical RCA result.
- New concepts: Operational Knowledge Artifact contract; knowledge anchor and drift/governance boundary.
- Open questions: how to bind an OKA to physical network entities, validate its evidence preconditions, detect staleness, and connect its version to remediation audit/recovery.
- Next step: read CHIEF for hierarchical candidate construction and attribution.

## 2026-09-15 — CHIEF

- Date: 2026-09-15
- Paper: From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems
- Core takeaway: defining the candidate as an Agent-step pair and narrowing subtask → Agent → step makes failure attribution more explicit; its execution graph and counterfactual checks are not physical network causality.
- New concepts: candidate-space contract; hierarchical attribution; trace-level counterfactual verification.
- Open questions: how to represent network hierarchy, open-set/multi-root causes, safe counterfactuals, and independent checks for LLM-generated graphs/oracles.
- Next step: read FlowFixer for symbolic verification and repair validation.

## 2026-09-15 — FlowFixer

- Date: 2026-09-15
- Paper: Diagnosis-Driven Automatic Repair for Agentic Workflow via Symbolic Inference
- Core takeaway: FlowFixer separates workflow diagnosis, scoped patch generation, pre-execution checks, dynamic execution, and retry; passing workflow tests is not the same as safe network recovery.
- New concepts: layered verification; workflow repair versus operational remediation.
- Open questions: how to add rollback, human approval, independent recovery signals, and topology/permission-aware validation to network actions.
- Next step: compare the four Batch 3 papers in AIOps Knowledge Review v3.

## 2026-09-15 — AIOps Knowledge Review v3

- Scope: Cloud-OpsBench, Cloud Intelligence/AIOps 2.0, CHIEF, and FlowFixer, with earlier AIOps batches as background.
- Main conceptual change: separated evidence provenance, candidate-space semantics, target-specific verification, workflow repair, and physical recovery; strengthened the Hybrid RCA architecture while marking network hierarchy, open-set/multi-root handling, rollback, and recovery as hypotheses or gaps.
- Most important open questions: a network Evidence Ticket, hierarchical/open-set/multi-root candidate evaluation, and independent recovery verification for human-gated remediation.
- Next step: pursue the research-question-driven network batch; do not treat this synthesis as a proven end-to-end system.

## 2026-10-23 — CAPMix

- Date: 2026-10-23
- Paper: CAPMix: Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments
- Core takeaway: DTW 软化正常邻域内的伪异常标签，双空间 Mixup 限制夸张注入模式对 KPI 判别边界的偏置；收益因数据集而异。
- New concepts: Anomaly Shift；DTW-based label revision；dual-space mixup for anomaly augmentation。
- Open questions: 单一正常均值如何处理多种工作状态；业务负载与故障并发时能否区分；训练异常标签来源及固定阈值表现。
- Next step: 阅读 When Model Meets New Normals，比较训练增强与测试时适应对新正常状态的处理。


## 2026-10-23 — When Model Meets New Normals

- Date: 2026-10-23
- Paper: When Model Meets New Normals: Test-Time Adaptation for Unsupervised Time-Series Anomaly Detection
- Core takeaway: EMA 去趋势适应整体水平变化，预测正常点上的在线重构更新学习剩余动态；两者需要配合，但伪标签漏检可污染更新。
- New concepts: new normal problem；趋势估计 + 预测正常掩码的测试时适应。
- Open questions: 业务负载与故障并发如何安全适应；不同数据集的阈值/EMA/学习率能否自动确定；WADI 附录的 TP/FP 报告数字为何不一致。
- Next step: 阅读 CAROTS，比较在线适应与上下文/因果增强。


## 2026-10-23 — CAROTS

- Date: 2026-10-23
- Paper: Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection (CAROTS)
- Core takeaway: CPA/CDA 按估计 Granger 图生成因果保持正常与因果破坏伪异常，SOC 保留多种正常语义模式；固定因果机制是假设，WADI 上双分数融合弱于对比分数单项。
- New concepts: causality-preserving / causality-disturbing augmentation；similarity-filtered one-class contrastive loss；causal forecast + latent centroid ensemble。
- Open questions: 因果结构变化的正常切换如何处理；如何验证估计因果图真实可靠；业务上下文和外生变量如何接入。
- Next step: 完成前三篇的跨论文 Review；继续 CrossAD。


## 2026-10-23 — Knowledge Review v3: TSAD batch 1

- Scope: CAPMix, When Model Meets New Normals, and CAROTS.
- Main conceptual change: 将正常性证据分为窗口形态、测试时分布状态、跨变量预测关系；训练期增强、在线适应和因果建模互补但假设不同。
- Most important open questions: 负载变化与故障并发、上下文/Trace 使用、因果图正确性、在线伪标签污染和无标签阈值校准。
- Next themes: CrossAD、Fortifying Time Series、以及多模式正常性建模。


## 2026-10-23 — CrossAD

- Date: 2026-10-23
- Paper: CrossAD: Time Series Anomaly Detection with Cross-scale Associations and Cross-window Modeling
- Core takeaway: 通过粗尺度条件下的细尺度重建检测尺度映射失配，并将周期路由的子序列表示聚合到窗口间原型上下文；该上下文表示统计模式，不提供业务状态语义或波动归因。
- New concepts: cross-scale reconstruction；scale-independent / cross-scale attention masks；period-aware sub-series query；EMA global multi-scale prototypes。
- Open questions: 多种业务正常状态与故障并发时的状态识别；原型推理期是否更新；业务上下文是否能解释原型；SWAN VUS-ROC 与消融增益表文不一致。
- Next step: 阅读 Fortifying Time Series，比较 DTW 鲁棒性认证的威胁模型、扰动范围和业务时序变化。


## 2026-10-23 — Fortifying Time Series

- Date: 2026-10-23
- Paper: Fortifying Time Series: DTW-Certified Robust Anomaly Detection
- Core takeaway: 用 randomized percentile smoothing 先给 anomaly score 得到 ℓ2 决策证书，再经 Keogh DTW 下界转换成对抗时间扭曲半径；证书是决策不变保证，不是原判定正确或业务状态可解释保证。
- New concepts: DTW-certified radius；percentile smoothing for unbounded anomaly scores；Keogh envelope slack；certified confusion matrix under evasion / availability.
- Open questions: DTW 扰动是否符合业务语义；Keogh 的保守性与零证书 coverage；推理多次采样的成本；新正常在线适应后认证边界。
- Next step: 阅读 Learning Multi-Pattern Normalities in the Frequency Domain，比较显式多模式表示与统计平滑 / 证书路线。


## 2026-10-23 — MACE

- Date: 2026-10-23
- Paper: Learning Multi-Pattern Normalities in the Frequency Domain for Efficient Time Series Anomaly Detection
- Core takeaway: 按服务从训练正常频谱抽取高频 Fourier bases，以服务条件子空间统一多服务模式；时域双卷积突出短异常，频域双卷积抑制高方差异常谱的重构。该“多模式”主要是跨服务差异，不代表同服务的动态业务状态已经建模。
- New concepts: service-conditioned normal frequency subspace；context-aware DFT / IDFT；time / frequency dualistic convolution；sparse Fourier basis KL gap。
- Open questions: unseen service 的 basis 来源；业务上下文与多运行态；异常频谱假设范围；表格 F1 的阈值可复现性；负载变化与故障并发。
- Next step: 完成第二批三篇 TSAD Knowledge Review；随后进入第三批，按主题安排剩余论文。


## 2026-10-23 — Knowledge Review v4: TSAD batch 2

- Scope: CrossAD, Fortifying Time Series, MACE，与首批三篇作对照。
- Main synthesis: 区分服务频谱先验、跨尺度 / 跨窗统计模式和 DTW 对抗决策证书；确认这些分别处理跨服务异质性、重构关联和攻击不变性，不等于识别业务运行语义。
- Most important open questions: 同服务动态多状态、业务上下文 / Trace、负载与故障并发、异常安全更新、无标签阈值及鲁棒性成本。
- Next step: 阅读下一批主题论文；完成其余 33 篇后再判断全库研究空白并生成综合报告。


## 2026-10-23 — Graph-MoE

- Date: 2026-10-23
- Paper: Graph Mixture of Experts and Memory-augmented Routers for Multivariate Time Series Anomaly Detection
- Core takeaway: 把各 GNN 深度编码的不同邻域范围作为 experts，并以记忆增强路由器结合当前及历史特征加权；其 memory 是潜在历史摘要，并未被证明对应可解释的业务态。
- New concepts: window-dynamic entity attention graph；layer-wise expert alignment；gated memory router；conditional normalizing flow scoring。
- Open questions: memory 跨窗口和 train/test 重置、安全更新方式；SWaT 测试再切分协议；业务上下文对齐及负载变化与故障并发。
- Next step: 完成本批另外两篇动态 / 因果上下文方法，再做第三批跨论文 Review。


## 2026-10-23 — CCM-TAD

- Date: 2026-10-23
- Paper: Cluster-Aware Causal Mixer for Online Anomaly Detection in Multivariate Time Series
- Core takeaway: CCM-TAD 将静态相关 profile clustering、时间维 causal mask 和验证误差尾概率累积组合成在线检测器；论文所称 causality 是时间信息流约束，不是 Granger / 跨通道因果发现。
- New concepts: correlation-profile spectral clustering；cluster-specific embedding；masked causal temporal mixer；empirical p-value sequential evidence；boundary correction。
- Open questions: test-label Best-F1 阈值与无标签线上阈值差距；静态关系簇应对动态业务状态的迁移；负载与故障并发下的事件延迟和边界修正。
- Next step: 阅读 TFC 完成第三批，再综合 Graph-MoE、CCM-TAD 与已有动态 normality / 多关系方法。


## 2026-10-23 — TFC

- Date: 2026-10-23
- Paper: Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion
- Core takeaway: TFC 以二阶差分显式放大轨迹弯折，以 MSA 读取多跨度曲率模式，并用频率 cross-attention 抑制正常周期震荡误报；其实现仍是逐条 univariate 表征，没有使用动机方程中的外生业务驱动。
- New concepts: discrete curvature evidence；multi-span masked attention；frequency–curvature calibration；temporal / pattern expert routing；Event-F1。
- Open questions: 逐点 score / loss 的精确公式、中心差分的在线前视、无标签 threshold 结果、正常业务周期切换与故障并发、Table 1 / 2 TODS 数值差异。
- Next step: 将 Graph-MoE、CCM-TAD、TFC 与前六篇整合为 batch 3 Knowledge Review，并据主题安排后续阅读。


## 2026-10-23 — Knowledge Review v5: TSAD batch 3

- Scope: Graph-MoE、CCM-TAD、TFC，与首两批六篇交叉比较。
- Main synthesis: 区分潜在历史图层路由、静态相关 profile 分组 + 顺序证据、以及单变量曲率 / 频带证据；三者均比原始点值提供更多结构，但仍不等于业务状态识别或波动成因解释。
- Most important open questions: workload / release / Trace 条件化、正常负载与故障并发、在线 memory / prototype / model 更新污染、测试标签 oracle threshold 与无标签运行点、流式前视延迟。
- Next step: 批次 4 阅读 GCAD、Structured Temporal Causality、SARAD，比较图因果、结构化时间因果与空间关联诊断。


## 2026-10-23 — GCAD

- Paper: *Anomaly Detection in Multivariate Time Series from the Perspective of Granger Causality* (AAAI 2025).
- Core takeaway: 按目标通道对 Mixer prediction loss 回传，聚合历史输入梯度形成窗口级 Granger predictive-influence 图，再与训练期正常均值图比较；图变化作为检测证据，不是干预因果图。
- Evidence: 五数据集 AUROC/AUPRC、关系 / 对角 / sparsification ablation 和一个 SWaT 案例；pairwise 限制，SMAP AUPRC 不领先，运行阈值和因果图真值验证不足。
- Open questions: 多种正常负载下图模板如何条件化；loss-gradient 与真实因果机制如何对照；正常负载与故障并发；数据规模口径与复现参数。
- Progress: 完成第 10/33 篇的完整 PDF 精读、笔记和知识卡片；本批剩 OracleAD、SARAD。


## 2026-10-23 — OracleAD / Structured Temporal Causality

- Paper: *Structured Temporal Causality for Interpretable Multivariate Time Series Anomaly Detection* (NeurIPS 2025), model OracleAD.
- Core takeaway: 逐通道 LSTM 编码 + 通道 MHSA 构造 latent relations，以每轮训练的平均 pairwise L2 distance matrix（SLS）作模板；预测误差乘结构偏差进行检测。
- Evidence: PSM/SMD/SWaT 多指标、ablation 与 SMD localization case；SLS 是对称 latent 结构而非 causal graph，推理模板静态，F1 阈值按测试真值选取且 SMD 表间口径需核对。
- Open questions: 多模态正常 SLS、结构与物理根因对照、负载—故障并发、窗口拖尾、无标签阈值。
- Progress: 完成第 11/33 篇完整 PDF 精读、笔记和卡片；同批第三篇为 SARAD。


## 2026-10-23 — SARAD

- Paper: *SARAD: Spatial Association-Aware Anomaly Detection and Diagnosis for Multivariate Time Series* (NeurIPS 2024).
- Core takeaway: Transformer 读取变量维 association，比较窗口两半的 MHSA map，column-sum aggregation 得到 SAR progression；MLP 重建该 progression，和 data residual 联合检测。
- Evidence: SMD/PSM/SWaT/HAI range AUC/VUS、诊断指标与模块消融；作者代码公开。短异常可能被半窗口稀释，attention association 不等于物理因果，SWaT/HAI 诊断标签并非完整故障 feature labels。
- Open questions: 业务状态切换与故障并发；attention 对齐外部 topology / Trace；短异常延迟与多尺度；低成本扩展。
- Progress: 批次 4 完成，累计 12/33 篇。下一步写 Knowledge Review v6 并按正常状态 / 鲁棒性 / 基准方法主题选择第 13–15 篇。


## 2026-10-23 — Knowledge Review v6: TSAD batch 4

- Scope: GCAD、Structured Temporal Causality / OracleAD、SARAD，与前 9 篇对比。
- Main synthesis: 区分 loss-gradient predictive Granger proxy、对称 latent-distance SLS、MHSA association reduction progression；结构异常证据不等于运维根因解释。
- Current gaps in 12-paper scope: 动态业务状态语义、状态变化与故障并发、多源运行 context、关系与真实拓扑 / Trace 对照、在线更新污染、无标签运行点与事件成本。上述判断仍待后续 21 篇复核。
- Progress: 12/33 完成，已逐篇提交三份详细笔记 / 卡片并完成本批 Review。
- Next batch (13–15): Quo Vadis; The Elephant in the Room; Temporal-Frequency Masked Autoencoders.


## 2026-10-23 — Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?

- Paper: *Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?* (ICML 2024).
- Core takeaway: PCA / 1-NN / 浅层网络是必要强 baseline；PA-F1 可奖励噪声，point、range 与阈值协议应一起报告。
- Evidence: 论文在 SWaT / WADI / SMD 等数据上报告 PCA 等简洁方法的竞争力；随机预测在 SWaT PA-F1 .963，但标准 / range F1 约 .218 / .217。该文自身使用 test-set best threshold，数字不是部署阈值结果。
- Progress: 完成第 13/33 篇全文精读、详细笔记和知识卡片；已 commit/push `026cb4e`。


## 2026-10-23 — The Elephant in the Room / TSB-AD

- Paper: *The Elephant in the Room: Towards A Reliable Time-Series Anomaly Detection Benchmark* (NeurIPS 2024 Datasets and Benchmarks Track).
- Core takeaway: 结合人工与算法辅助复核，整理 1,070 条 UTS/MTS，统一 40 类 detector 与十种指标；作者推荐 VUS-PR 的结论限定于其 reliability tests。
- Evidence: 1,070 sequences / 40 datasets，450+ model variants；没有 detector 在所有数据集领先；固定主随机种子，benchmark 作者承认人工复核有限且会持续更新。
- Progress: 完成第 14/33 篇全文精读、详细笔记和知识卡片；已 commit/push `bb470c5`。


## 2026-10-23 — TFMAE

- Paper: *Temporal-Frequency Masked Autoencoders for Time Series Anomaly Detection* (ICDE 2024).
- Core takeaway: 以局部高-CV 时间 mask 与低幅值频率 mask 构造双视图，通过 adversarial symmetric-KL discrepancy 检测，而不直接使用 reconstruction residual。
- Evidence: 主表五个真实集平均 point-adjusted F1 96.04%；组件 / mask ablations 支持其设计；阈值依 validation score 和预设 anomaly ratio，SMAP shift evidence 是单个 CDF case study。业务 workload / Trace 未输入。
- Progress: 完成第 15/33 篇全文精读、详细笔记和知识卡片；已 commit/push `42ffe7d`。


## 2026-10-23 — Knowledge Review v7: TSAD batch 5

- Scope: Quo Vadis、TSB-AD、TFMAE，与前 12 篇交叉比较。
- Main synthesis: 区分 baseline / protocol critique、benchmark + metric reliability、temporal-frequency masked view discrepancy；明确 Best-F1、PA-F1、VUS-PR 和 validation anomaly-rate threshold 的边界。
- Current gaps in 15-paper scope: workload / Trace / release 条件化、正常状态切换与故障并发、固定告警运行点、benchmark curation selection effect、双视图机制在业务高波动下的稳定性。
- Progress: 15/33 完成，三篇各自笔记 / 卡片和 Review 已更新知识索引及问题列表。
- Next batch (16–18): Unraveling the “Anomaly” (tri-domain); Perturbation Guiding Contrastive Representation; Sub-Adjacent Transformer.


## 2026-10-23 — TriAD

- Paper: *Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution* (ICDE 2024).
- Core takeaway: temporal / frequency / periodic-residual embedding 加入域内与域间 contrastive loss；每域 top-1 window 缩小搜索区域，再由 MERLIN 做多长度 discord 定位。
- Evidence: 250 个 UCR 单事件数据集、PA%K / affiliation；62 个最短数据上的 MERLIN++ 对比有更高准确度和更低时间。主假设是单 test event；vote 权重未校准，residual extraction 需核对代码。
- Progress: 完成第 16/33 篇全文精读、详细笔记和知识卡片；已 commit/push `d1d689a`。


## 2026-10-23 — PCRTA

- Paper: *Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection* (IJCAI 2024).
- Core takeaway: 以六种 point / contextual / collective perturbations 训练扰动识别器，用其 pseudo-label 选同类 top-k positives / 异类 negatives，训练后对七类 view 的 embedding 做 LOF average。
- Evidence: 六集 F1 / AUC-PR 上五集第一、ASD 第二；三集 ablation 支持 classifier / contrastive 模块。best F1 通过 threshold enumeration 获得，需按 test-oracle protocol 理解。
- Progress: 完成第 17/33 篇全文精读、详细笔记和知识卡片；已 commit/push `3c2d094`。


## 2026-10-23 — Sub-Adjacent Transformer

- Paper: *Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods* (IJCAI 2024).
- Core takeaway: attention 只聚合离目标时间点 $[k_1,k_2]$ 距离的 sub-adjacent contexts，使紧邻复制更难；score 结合低 contribution 和高重建误差。
- Evidence: 六真实集 + NeurIPS-TS；mapping、band、window 和 loss ablation。主 F1 使用 point adjustment 且 threshold 为 test best-F1；multi-entity comparison 有 pooled / per-entity protocol 差异。
- Progress: 完成第 18/33 篇全文精读、详细笔记和知识卡片；已 commit/push `2cd50c1`。


## 2026-10-23 — Knowledge Review v8: TSAD batch 6

- Scope: TriAD、PCRTA、Sub-Adjacent Transformer，与前 15 篇综合对照。
- Main synthesis: 区分 augmentation hard negatives、扰动分类伪标签 + LOF、非紧邻 reconstruction constraint；同时标出 triad single-event、best-F1 threshold、point adjustment 和运行 context 缺口。
- Progress: 18/33 完成；三篇笔记 / 卡片、Review、INDEX、questions 均更新并同步。
- Next batch (19–21): Large Language Model Guided Knowledge Distillation; Delving into Large Language Models for Effective TSAD; AnomSeer.


## 2026-10-23 — AnomalyLLM

- Paper: *Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection* (IJCAI 2024).
- Core takeaway: frozen GPT-2 time-series teacher + per-channel prototype student；synthetic local distortions create student–teacher discrepancy, teacher consistency stabilizes its response to perturbation.
- Evidence: UCR aggregate accuracy / AF1 .820 / .858; adjusted F1 on four common MTS sets .958 / .956 / .965 / .997; WaQ / SWAN .620 / .804. Recorded prototype 32 vs sensitivity 48 and WaQ / GECCO table-text mismatch instead of silently resolving them.
- Progress: 完成第 19/33 篇 PDF 精读及笔记 / 卡片；`86be981` 已 push。PDF 不纳入 Git。


## 2026-10-23 — Delving into LLMs for TSAD

- Paper: *Delving into Large Language Models for Effective Time-Series Anomaly Detection* (NeurIPS 2025).
- Core takeaway: 将 LLM TSAD 拆为 temporal understanding 与 localization；ACF de-seasonalization 处理季节遮挡，index-aware text 把隐式计数变成区间索引检索。
- Evidence: AnomLLM 上去索引平均 F1 降 23.36 points；Qwen 的 GT localization diagnostic index-aware F1 60.16 / 6.45s vs index-free 20.33 / 29.79s。TSB-AD-U GPT-4o 每样本约 140.63s；模拟 context case 尚未证明真实业务 context 安全过滤未知故障。
- Progress: 完成第 20/33 篇 PDF 精读及笔记 / 卡片；`d1e0d23` 已 push。代码链接已入库。


## 2026-10-23 — AnomSeer

- Paper: *AnomSeer: Reinforcing Multimodal LLMs to Reason for Time-Series Anomaly Detection* (ICML 2026).
- Core takeaway: GT-derived statistical ExpCoT 通过 token-level OT reasoning reward 和 advantage-space orthogonalization 进入 Qwen2.5-VL 的 TimerPO 训练，输出检测、类别与文本解释。
- Evidence: AnomLLM mean Affinity F1 为 TimeMaster-3B 71.9、AnomSeer-3B 79.3、7B 84.4；OT / orthogonalization 有 ablation。ExpCoT 从 GT 类型与时间区间生成，因此 pure RL 不等于 label-free；appendix 仍有末端短异常漏检。
- Progress: 完成第 21/33 篇 PDF 精读及笔记 / 卡片；`d12960d` 已 push。未执行训练或复现实验。


## 2026-10-23 — Knowledge Review v9: TSAD batch 7

- Scope: AnomalyLLM、Delving、AnomSeer，与前 18 篇已读论文交叉比较。
- Main synthesis: 区分 LLM teacher 的表示蒸馏、零样本输入预处理 / prompt 结构、MLLM 的 GT-derived expert-trace RL；多种形态表示还不等于业务状态语义，文本解释也不等于根因来源验证。
- Research evidence gaps: context-conditioned state / fault concurrency、真实 workload / release / Trace 输入、context filtering 对未知故障召回的影响、GT trace 的解释忠实性、固定误报预算与延迟。
- Progress: 21/33 完成；三篇笔记 / 卡片、Review v9、INDEX、questions 已更新。每篇和 Review 均按规范单独 commit/push；PDF 仍被 `.gitignore` 排除。
- Next batch (22–24): Harnessing Vision-Language Models for TSAD; Towards Foundation Models for Zero-Shot TSAD; IMPACT: Influence Modeling for Open-Set TSAD。


## 2026-10-23 — Harnessing Vision-Language Models for TSAD

- Paper: *Harnessing Vision-Language Models for Time Series Anomaly Detection* (AAAI 2026).
- Core takeaway: CLIP patch-level multi-scale cross-window screening proposes local intervals; GPT-4o verifies against a full-series plot and can add missed candidates.
- Evidence: ViT4TS / VLM4TS mean F1-max 0.612 / 0.659; VLM4TS leads 9/11. Yahoo A3/A4 dense anomalies reduce performance; max-F1 protocol and roughly 14.68-second per-series VLM latency bound interpretation.
- Progress: 完成第 22/33 篇 PDF 精读及笔记 / 卡片；`8482c21` 已 push。


## 2026-10-23 — TimeRCD

- Paper: *Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy* (ICML 2026).
- Core takeaway: 2.5B synthetic points teach a Transformer to classify local relational discrepancy from long input context; reconstruction is a training scaffold, inference uses anomaly head only.
- Evidence: 64 zero-shot dataset-metric cases rank first 38 / second 14; dedicated synthetic contextual anomaly Standard-F1 0.827. Fixed 5k context is not universally optimal and anomaly-dense contexts can be contaminated.
- Progress: 完成第 23/33 篇 PDF 精读及笔记 / 卡片；`fe5efc1` 已 push。


## 2026-10-23 — IMPACT

- Paper: *IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection* (ICML 2026).
- Core takeaway: validation-risk influence guides contamination label-flipping and feature-space pseudo anomaly generation for seen / unseen open-set heads.
- Evidence: strong AUC under general / hard protocols and 2–10% injected contamination; hard TUSZ drops 75.70→60.92 without unseen loss. The contamination is sampled from test anomalies then excluded from final test; rare normal subpopulations are an explicit risk.
- Progress: 完成第 24/33 篇 PDF 精读及笔记 / 卡片；`bb6fe73` 已 push。


## 2026-10-23 — Knowledge Review v10: TSAD batch 8

- Scope: Harnessing VLMs, TimeRCD, IMPACT，与前 21 篇交叉比较。
- Main synthesis: 区分 same-series visual reference、synthetic-pretrained relative context、validation-risk influence 三类 reference / supervision；它们分别对应 candidate verification、zero-shot contextual TSAD、few-shot open-set contamination handling。
- Evidence gaps: 真实 workload / release / Trace context、状态变化与故障并发、rare-normal group robustness、generator-held-out validation、rationale fidelity 和固定告警预算。
- Progress: 24/33 完成；3 篇笔记 / 卡片、Review v10、INDEX、questions 已更新。逐篇提交并 push；PDF 仍被 `.gitignore` 排除。
- Next batch (25–27): KAN-AD; RTdetector; Idempotent Reconstruction。


## 2026-10-23 — KAN-AD

- Paper: *KAN-AD: Time Series Anomaly Detection with Kolmogorov-Arnold Networks* (ICML 2025).
- Core takeaway: 有限 Fourier 平滑函数替换局部 B-spline，配合一阶差分、周期索引和轻量卷积进行下一点预测。
- Evidence: 四个单变量集平均 Event F1 .7798；CTE / Fourier / 组合输入均有消融。TODS 10–40% 污染仅为有限合成协议；主文未明确最终 anomaly-score 方程。
- Progress: 完成第 25/33 篇实际 PDF 精读，已生成详细笔记和知识卡片；未运行代码或训练。


## 2026-10-23 — RTdetector

- Paper: *RTdetector: Deep Transformer Networks for Time Series Anomaly Detection Based on Reconstruction Trend* (IJCAI 2025).
- Core takeaway: 首轮重建误差作为第二路 decoder 的 focus，RTE 恢复原始统计趋势，RT-Attention 注入均值 / 方差信息。
- Evidence: UCR / MBA / SMD 表现强但 SMAP 低于 DCdetector；去掉 RTE / RT-Attention 后 UCR F1 下降。Eq. (3) 反归一化括号与常见形式不同，需核对实现。
- Progress: 完成第 26/33 篇实际 PDF 精读，已生成详细笔记和知识卡片；未运行代码或训练。


## 2026-10-23 — Idempotent Reconstruction / IGAD

- Paper: *Multivariate Time Series Anomaly Detection with Idempotent Reconstruction* (NeurIPS 2025).
- Core takeaway: 频域扰动正常样本，以冻结副本构造幂等和 manifold tightness 目标，推理沿用原重建分数。
- Evidence: 15×4 model-dataset 组合中 52/60 VUS-PR 提升、8 个回退；Gaussian 测试噪声和 loss ablation 提供支持，但按数据集调参且作者报告方差 / 成本限制。
- Progress: 完成第 27/33 篇实际 PDF 精读，已生成详细笔记和知识卡片；未运行代码或训练。


## 2026-10-23 — Knowledge Review v11: TSAD batch 9

- Scope: KAN-AD、RTdetector、IGAD，与此前 24 篇综述证据交叉对照。
- Main synthesis: 区分函数表达平滑、原分布趋势恢复、自条件残差放大和训练期 fixed-point manifold 约束；这些改善拟合 / 重建证据，但不自动识别业务状态语义或波动来源。
- Evidence gaps: 状态变化与故障并发、rare-normal safety、统一鲁棒性 protocol、固定 FPR / 延迟和可复现 score 细节。
- Progress: 27/33 完成；3 篇精读笔记 / 知识卡片、Review v11、INDEX 与问题进度已更新。
- Next batch (28–30): ScatterAD、COGNOS、TeamWork。


## 2026-10-23 — ScatterAD

- Paper: *ScatterAD: Temporal-Topological Scattering Mechanism for Time Series Anomaly Detection* (NeurIPS 2025).
- Core takeaway: 每个时刻作图节点，因果卷积 + GAT，结合 latent scattering、时间一致性和 EMA 双 encoder；score 合并中心偏离及邻时刻变化。
- Evidence: 24 个主表设置中作者报告 15 项第一；SWAN Aff-F 对 1 timestep 偏移极敏感，WADI 强 Gaussian noise 下散布比反转；Eq. (10) score 方向需核代码。
- Progress: 完成第 28/33 篇实际 PDF 精读和笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — COGNOS

- Paper: *COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing* (ICML 2026).
- Core takeaway: GWNR 让 MSE residual 近似 Gaussian white noise；ARKS 用 per-channel calibration 与 NIS circuit breaker 抑噪并快速响应突变。
- Evidence: 多 backbone / 数据总体提升，但 KAN-AD PSM 的 range / VUS 指标有回退；作者明确固定 noise R、MSE residual 适用范围和 onset-vs-coverage 限制。
- Progress: 完成第 29/33 篇实际 PDF 精读和笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — TeamWork

- Paper: *TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling* (ICML 2026).
- Core takeaway: ERI 选 dominant / auxiliary channels，前三周期分别做 point / segment / period masking，role-aware gate 融合后重建。
- Evidence: 8 个 benchmark 和 16 个基线；移除角色、交互或不同粒度 masking 都有消融下降。作者指出静态角色和全局 FFT 对动态 / 弱周期信号的边界。
- Progress: 完成第 30/33 篇实际 PDF 精读和笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — Knowledge Review v12: TSAD batch 10

- Scope: ScatterAD、COGNOS、TeamWork，与此前 27 篇综述 evidence 交叉比较。
- Main synthesis: 区分 latent scattering、Gaussian residual null + filtering、ERI channel-role modeling；数值关系 / statistical reference 不自动构成业务拓扑、因果或状态语义。
- Evidence gaps: 动态状态与故障并发、异常起点和区间覆盖、异方差 / 跨变量噪声、rare-normal safety、业务上下文 source attribution。
- Progress: 30/33 完成；3 篇笔记 / 卡片、Review v12、INDEX 与问题列表已更新。
- Next batch (31–33): AnoMamba; Multi-View Ensemble via Coupling Flows; Conditional Normalizing Flows。


## 2026-10-23 — AnoMamba

- Paper: *AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling* (IJCAI 2026).
- Core takeaway: channel-independent patch embedding 加 GSRMamba，以全局 patch context 重加权 S6 step-size；KL multi-scale long-tail prior 约束重建依赖。
- Evidence: 8 个基准 F1-AF 7/8、VUS-ROC 6/8 第一；移除 GSR 时 UTS F1-AF .7830 降至 .6547。实验使用 window=100、SPOT；hidden attention 不是因果解释。
- Progress: 完成第 31/33 篇 PDF 精读并生成笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — FlowFuse

- Paper: *Multi-View Ensemble for Time Series Anomaly Detection via Coupling Flows* (IJCAI 2026).
- Core takeaway: 时域 / 频域 × 聚类 / 重建四路分数，经交替 coupling flows 学 normal score joint density；ensemble disagreement 可引导有限标签路由。
- Evidence: 18 个基准；四个代表集消融中 flow 融合相对简单平均约 +8.0% Aff-F1；mixed anomalies 仍较难。
- Progress: 完成第 32/33 篇 PDF 精读并生成笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — Conditional Normalizing Flows

- Paper: *Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows* (UAI 2026).
- Core takeaway: CNF 将序列映射到具有显式 latent dynamics 的空间，以 whitened latent 的 MV-KS GOF 检验偏离，并用 FIT 检查训练假设是否满足。
- Evidence: synthetic 4D、w=64 时 KS 优于 NLL 的若干指标；TSB-AD leaderboard 上 NLL UTS 第 7、KS 第 17。作者明确指出窗口 / 维度、模型容量与 LG-LDM 适配问题。
- Progress: 完成第 33/33 篇 PDF 精读并生成笔记 / 卡片；未运行代码或训练。


## 2026-10-23 — Knowledge Review v13: TSAD batch 11

- Scope: AnoMamba、FlowFuse、Conditional Normalizing Flows，并关联前三十篇跨论文证据。
- Main synthesis: 三者分别把 normality 约束置于重构依赖、异质 detector score 联合分布、latent temporal compliance；全局依赖、ensemble 或统计检验都不自动说明变化源自合法负载还是故障。
- Evidence gaps: 真实 workload/release/Trace 条件化、合法状态切换与故障并发、statistical / ensemble uncertainty calibration、固定 FPR 与 event delay。
- Progress: **33/33** 完成；33 篇均已生成详细笔记与知识卡片；第 11 批 Review、INDEX 和问题状态已更新。
- Next step: 完成 33 篇全景对比、方法演进、正常波动与故障专题、证据化研究空白及知识检索指南。


## 2026-10-23 — TSAD final synthesis

- Scope: 2024–2026 33 篇 TSAD 论文，依据逐篇 PDF 笔记和 Knowledge Reviews v3–v13。
- Main synthesis: normality 已有 prototypes / memory、频域、在线适配、相对上下文、因果关系、残差统计、score fusion 和 latent dynamics 等路线；真实业务状态语义、负载变化与故障并发、Trace / release 归因与统一部署评测仍缺充分证据。
- Documents: [TSAD final synthesis](reviews/tsad-final-synthesis.md)；[TSAD knowledge query guide](guides/tsad-knowledge-query-guide.md)。
- Progress: 33/33 实际 PDF 精读、33 份详细笔记与 33 张知识卡片完成；未训练或复现模型。
