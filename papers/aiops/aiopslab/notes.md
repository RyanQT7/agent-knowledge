# AIOpsLab：A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds

## 1. Metadata

- **Authors**: Yinfang Chen, Manish Shetty, Gagan Somashekar, Minghua Ma, Yogesh Simmhan, Jonathan Mace, Chetan Bansal, Rujia Wang, Saravan Rajmohan
- **Year / venue**: 2025, MLSys 2025 proceedings
- **Official version**: [MLSys Proceedings](https://proceedings.mlsys.org/paper_files/paper/2025/file/d1f9e4a9f109b6e8b75ed362736f22ec-Paper-Conference.pdf) ; [arXiv](https://arxiv.org/abs/2501.06706)
- **Local PDF**: [MLSys formal version](../../../sources/papers/llm-microservice-anomaly-generation/aiopslab_mlsys2025.pdf)
- **Code**: https://aka.ms/aiopslab-repo（正式论文给出的项目地址）
- **Paper ID**: aiopslab
- **Tags**: AIOps; agent-evaluation; cloud-testbed; fault-injection; metrics-logs-traces; benchmark

## 2. One-Sentence Summary

AIOpsLab 提供可部署微服务、可控工作负载 / 故障生成、统一 Agent–Cloud API 和自动评分的云运维 Agent 评测框架；它让受控故障在真实运行系统中产生相应遥测，不是 LLM 异常样本生成器，也没有生成合成 Metric / Trace 数据。

## 3. Research Scenario and Problem

作者关注自主云运维 Agent 的系统级评估：真实生产事故多样且难重放，离线问答无法测试 Agent 对运行系统观测、工具调用、诊断和缓解的完整能力。框架在可部署微服务平台中注入故障、运行负载并提供 Metrics、Logs、Traces、配置 / 拓扑等工具；Agent 接收任务描述后调查和操作环境，评估器对照内部故障配置与任务期望判断结果。（PDF §§1–2, pp.1–3）

测试床含 DeathStarBench HotelReservation、SocialNetwork、OpenTelemetry Astronomy Shop 和自定义 TiDB 场景。问题表示 P=<T,C,S>，其中任务 T 配有上下文 C=<E,I>（环境、相关信息）；任务层次覆盖 detection、localization、RCA、mitigation。输入为任务及 Agent 可访问的 API / 环境信息，交互过程中 Agent 可查询 telemetry、执行动作；输出可能是检测 / 定位 / 根因结论或缓解行动。

## 4. Core Challenges

1. **离线数据缺乏真实工具反馈**：静态 benchmark 无法体现调用链、运行状态和干预后的效果。
2. **故障表象与根因差异**：CPU / 网络等资源症状可直接观测，而配置错误、代码问题等功能故障可能在传播后才产生下游异常；只评表面异常无法考察诊断深度。（§2）
3. **Agent 评估需要统一接口和可复现真值**：若不同环境工具不一致、故障标签不明确，Agent 之间比较难复现。
4. **正常状态识别同样重要**：Agent 不能把每个任务都强行诊断成故障；论文包含 no-op / 正常任务并报告误报。（§3.6.4）

## 5. Framework Architecture

### A. Live cloud testbed and fault generation

框架可启动微服务基准、工作负载生成器和故障注入器。故障分 symptomatic 与 functional 两大类：前者包括 CPU / 资源 / 网络压力或服务崩溃；后者可由配置错误、认证 / 权限、代码 bug 等机制触发，更要求沿服务交互诊断和缓解。任务配置包含目标、故障类型、时间窗口及答案标签；框架也支持自定义故障。（PDF §§2.1–2.3, Table 1）

### B. Agent–Cloud Interface

Orchestrator 通过标准 API 向 Agent 暴露任务、系统信息和行动接口；Agent 可查询 Prometheus 指标、Jaeger trace、日志链路（kubectl / Filebeat / Logstash）、代码 / 配置和集群信息。返回的 Observation 是部署系统中的实际遥测或工具结果，而非由 LLM 生成的对话片段。任务执行轨迹被记录供评价与复盘。（§2.4, Fig. 2）

### C. Ground truth and evaluation

框架内部知道工作负载 / 故障注入配置、作用对象和期望动作，可将其作为隐藏真值；Agent 接口只开放任务完成所需信息。检测、定位、RCA、mitigation 有各自任务级判断及完成条件。实验考虑不同语言模型与 Agent 交互模式，评估是否成功处理代表性问题。（§2.5, §3）

**重要版本区别**：MLSys 正式版概览提到框架包含 100 个问题，但受评测成本影响，实验只选取 48 个代表性问题；不要将早期 arXiv 版本的评测口径直接套用到正式版。（§3.1）

## 6. Agent Interaction and Experimental Workflow

典型执行过程：

任务说明 → Agent 查询环境 / 指标 / 日志 / Trace → Orchestrator 执行工具并返回观察 → Agent 继续调查或执行运维动作 → 输出答案 / 缓解 → 评估器依据故障真值和任务完成条件评分。

框架中的工作负载和真实故障动作由实验控制器确定，不是 LLM 在自然语言里虚构故障样本。LLM 负责推理、选择工具和行动；具体是否有显式 Planner / long-term memory 取决于被测 Agent 配置，不能当成 AIOpsLab 固有模块。

## 7. Experimental Evidence

- **系统 / 数据**：多个真实部署的微服务基准和可配置问题；观测包括 metrics、logs、traces、配置 / 集群信息。框架设计支持故障生成、遥测收集与交互轨迹记录。（§2.1–2.5）
- **评估范围**：100 问题框架中选 48 个代表场景运行实验；比较 GPT-4-W-Shell、GPT-3.5-W-Shell、ReAct、Flash 等 Agent / 交互基线。（§3.1–3.4）
- **正式版表 3**：所报告 all-problem accuracy 为 GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%。数字对应论文定义的问题完成准确率，不等同异常检测器 F1。（Table 3）
- **正常 no-op 任务**：在两个要求不采取故障操作的检测任务中，只有 GPT-4-W-Shell 识别正常工作负载；其他 Agent 将正常状态误报为异常。（§3.6.4, p.9）
- **支持范围**：说明 live testbed 能测端到端 Agent 运维交互，并暴露正常 / 故障判断难点；不证明生成的故障覆盖生产真实分布，也不评价某种检测模型的数据增强收益。

## 8. Limitations and Relevance

**本知识库分析**：故障注入机制和组件级真值提高了实验可解释性，但测试床只代表所选应用、故障模板和配置。Agent 任务分数不等同于多模态生成数据的分布真实性。框架中从故障动作产生的 Metric / Trace / Log 属于环境测量结果，不是逐模态合成器，也未提供对真实生产事故的外部验证。

正常 no-op 任务具有重要意义：异常检测要容纳无事故的正常状态，评估器应把“无异常”作为有效结果。它仍没有把正常业务高峰、扩缩容或发布过程系统化标成困难负样本，且只报告有限正常任务表现；所以不能直接推断模型已学会区分正常波动与真实故障。

## 9. Relationship to This Topic

与 [Synthetic Time Series](../synthetic-cloud-microservices/notes.md) 都使用云微服务环境和可控故障注入；前者面向产生指标 / 数据集，AIOpsLab 面向 Agent 任务与工具反馈。与 [TraceLLM](../tracellm/notes.md) 不同，它从真实服务运行时采集 Trace，而非离线生成 Trace DAG。与 [LLM-AP](../llm-ap-synthetic-augmentation/notes.md) / [GenIAS](../genias/notes.md) 不同，它不直接生成异常数值样本。与 TSAD [CAPMix](../../capmix/notes.md) 可形成互补：前者支持真实可控遥测 / 任务构造，后者在 KPI 序列做增强并评估检测。

## 10. Evidence Map

| 论断 | 原文定位 |
| --- | --- |
| 任务表示、系统组成和微服务环境 | PDF §§2.1–2.3, pp.2–4, Table 1 |
| Agent–Cloud API、工具与遥测 | PDF §2.4, pp.4–5, Fig. 2 |
| 评分和实验设置 | PDF §§2.5, 3.1–3.5 |
| 正式版 48 场景评估和 Table 3 | PDF §3, Table 3 |
| no-op / 正常工作负载误报 | PDF §3.6.4, p.9 |
| 框架并非样本合成器 | 论文任务定义与 §2；本知识库分析 |
