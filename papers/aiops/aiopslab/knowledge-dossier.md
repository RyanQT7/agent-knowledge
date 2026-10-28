# Knowledge Dossier — AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds

## 1. Basic Information

- **English title**: AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds
- **中文译名**：AIOpsLab：用于自主云运维 Agent 评估的整体框架
- **Authors**: Yinfang Chen, Manish Shetty, Gagan Somashekar, Minghua Ma, Yogesh Simmhan, Jonathan Mace, Chetan Bansal, Rujia Wang, Saravan Rajmohan
- **Venue / year / CCF**: MLSys 2025 / 2025 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: [aiopslab_mlsys2025.pdf](../../../sources/papers/llm-microservice-anomaly-generation/aiopslab_mlsys2025.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://aka.ms/aiopslab-repo
- **Research area**: 运行时云运维 Agent 基准与故障注入测试床
- **Method tags**: AIOps, agent-evaluation, fault-injection, live-microservices, metrics-logs-traces, benchmark

## 2. Research Scenario

作者关注自主云运维 Agent 的系统级评估：真实生产事故多样且难重放，离线问答无法测试 Agent 对运行系统观测、工具调用、诊断和缓解的完整能力。框架在可部署微服务平台中注入故障、运行负载并提供 Metrics、Logs、Traces、配置 / 拓扑等工具；Agent 接收任务描述后调查和操作环境，评估器对照内部故障配置与任务期望判断结果。（PDF §§1–2, pp.1–3）

测试床含 DeathStarBench HotelReservation、SocialNetwork、OpenTelemetry Astronomy Shop 和自定义 TiDB 场景。问题表示 P=<T,C,S>，其中任务 T 配有上下文 C=<E,I>（环境、相关信息）；任务层次覆盖 detection、localization、RCA、mitigation。输入为任务及 Agent 可访问的 API / 环境信息，交互过程中 Agent 可查询 telemetry、执行动作；输出可能是检测 / 定位 / 根因结论或缓解行动。

## 3. Research Problem

如何建立可重放、可计分且能覆盖 Agent–工具–云环境闭环的 AIOps 评估，而不是只在静态问答中评估根因回答？

## 4. Core Challenges

1. **离线数据缺乏真实工具反馈**：静态 benchmark 无法体现调用链、运行状态和干预后的效果。
2. **故障表象与根因差异**：CPU / 网络等资源症状可直接观测，而配置错误、代码问题等功能故障可能在传播后才产生下游异常；只评表面异常无法考察诊断深度。（§2）
3. **Agent 评估需要统一接口和可复现真值**：若不同环境工具不一致、故障标签不明确，Agent 之间比较难复现。
4. **正常状态识别同样重要**：Agent 不能把每个任务都强行诊断成故障；论文包含 no-op / 正常任务并报告误报。（§3.6.4）

## 5. Limitations of Existing Methods

### A. Live cloud testbed and fault generation

框架可启动微服务基准、工作负载生成器和故障注入器。故障分 symptomatic 与 functional 两大类：前者包括 CPU / 资源 / 网络压力或服务崩溃；后者可由配置错误、认证 / 权限、代码 bug 等机制触发，更要求沿服务交互诊断和缓解。任务配置包含目标、故障类型、时间窗口及答案标签；框架也支持自定义故障。（PDF §§2.1–2.3, Table 1）

### B. Agent–Cloud Interface

Orchestrator 通过标准 API 向 Agent 暴露任务、系统信息和行动接口；Agent 可查询 Prometheus 指标、Jaeger trace、日志链路（kubectl / Filebeat / Logstash）、代码 / 配置和集群信息。返回的 Observation 是部署系统中的实际遥测或工具结果，而非由 LLM 生成的对话片段。任务执行轨迹被记录供评价与复盘。（§2.4, Fig. 2）

### C. Ground truth and evaluation

框架内部知道工作负载 / 故障注入配置、作用对象和期望动作，可将其作为隐藏真值；Agent 接口只开放任务完成所需信息。检测、定位、RCA、mitigation 有各自任务级判断及完成条件。实验考虑不同语言模型与 Agent 交互模式，评估是否成功处理代表性问题。（§2.5, §3）

**重要版本区别**：MLSys 正式版概览提到框架包含 100 个问题，但受评测成本影响，实验只选取 48 个代表性问题；不要将早期 arXiv 版本的评测口径直接套用到正式版。（§3.1）

## 6. Core Idea

通过微服务测试床和可控故障 / 工作负载生成环境数据，再用统一 Agent–Cloud API、遥测工具和隐藏配置 oracle 执行 / 评分任务。

## 7. Technical Innovations

- 统一的 Agent–Cloud Interface：任务、信息、工具观察和动作的 API。
- 将 symptomatic 资源故障和 functional 配置 / 代码类故障纳入问题设计。
- 组合检测 / 定位 / RCA / mitigation 任务和运行轨迹记录；正式版框架 100 问题、受评估成本限制实验选 48。

## 8. Methodology

典型执行过程：

任务说明 → Agent 查询环境 / 指标 / 日志 / Trace → Orchestrator 执行工具并返回观察 → Agent 继续调查或执行运维动作 → 输出答案 / 缓解 → 评估器依据故障真值和任务完成条件评分。

框架中的工作负载和真实故障动作由实验控制器确定，不是 LLM 在自然语言里虚构故障样本。LLM 负责推理、选择工具和行动；具体是否有显式 Planner / long-term memory 取决于被测 Agent 配置，不能当成 AIOpsLab 固有模块。

## 9. Experimental Evidence

- **系统 / 数据**：多个真实部署的微服务基准和可配置问题；观测包括 metrics、logs、traces、配置 / 集群信息。框架设计支持故障生成、遥测收集与交互轨迹记录。（§2.1–2.5）
- **评估范围**：100 问题框架中选 48 个代表场景运行实验；比较 GPT-4-W-Shell、GPT-3.5-W-Shell、ReAct、Flash 等 Agent / 交互基线。（§3.1–3.4）
- **正式版表 3**：所报告 all-problem accuracy 为 GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%。数字对应论文定义的问题完成准确率，不等同异常检测器 F1。（Table 3）
- **正常 no-op 任务**：在两个要求不采取故障操作的检测任务中，只有 GPT-4-W-Shell 识别正常工作负载；其他 Agent 将正常状态误报为异常。（§3.6.4, p.9）
- **支持范围**：说明 live testbed 能测端到端 Agent 运维交互，并暴露正常 / 故障判断难点；不证明生成的故障覆盖生产真实分布，也不评价某种检测模型的数据增强收益。

## 10. Limitations

### A. Author-stated limitations

- 论文未以独立小节列出可明确归属的作者局限；相关适用边界在方法 / 实验范围中说明。

### B. Reasoned inference

- 代表性故障和应用有限；运行时注入遥测是真实环境观测，但不覆盖全部生产故障分布。
- 问题完成率不直接测量 Metric / Trace 合成或 anomaly detector 增益。

### C. Evidence gaps

- 正常业务高峰、扩缩容、发布与真实故障并发的困难评估任务仍需专门覆盖。

## 11. Research Implications

**本知识库分析**：是验证真实微服务运行中 Agent / 诊断的可复现环境参照，不应与离线 LLM 数值生成器混为一谈。

## 12. Related Papers

与 [Synthetic Time Series](../synthetic-cloud-microservices/notes.md)互补，后者聚焦采集数据集；[TraceLLM](../tracellm/notes.md)生成离线 DAG；TSAD [CAPMix](../../capmix/notes.md)评测 KPI 检测器增强。

## 13. Evidence References

| 论断 | 原文定位 |
| --- | --- |
| 任务表示、系统组成和微服务环境 | PDF §§2.1–2.3, pp.2–4, Table 1 |
| Agent–Cloud API、工具与遥测 | PDF §2.4, pp.4–5, Fig. 2 |
| 评分和实验设置 | PDF §§2.5, 3.1–3.5 |
| 正式版 48 场景评估和 Table 3 | PDF §3, Table 3 |
| no-op / 正常工作负载误报 | PDF §3.6.4, p.9 |
| 框架并非样本合成器 | 论文任务定义与 §2；本知识库分析 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "aiopslab",
  "title_en": "AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds",
  "title_zh": "AIOpsLab：用于自主云运维 Agent 评估的整体框架",
  "authors": [
    "Yinfang Chen",
    "Manish Shetty",
    "Gagan Somashekar",
    "Minghua Ma",
    "Yogesh Simmhan",
    "Jonathan Mace",
    "Chetan Bansal",
    "Rujia Wang",
    "Saravan Rajmohan"
  ],
  "year": 2025,
  "venue": "MLSys 2025",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/aiopslab_mlsys2025.pdf",
  "reading_note_path": "papers/aiops/aiopslab/notes.md",
  "knowledge_card_path": "papers/aiops/aiopslab/knowledge-card.md",
  "code_url": "https://aka.ms/aiopslab-repo",
  "research_area": "运行时云运维 Agent 基准与故障注入测试床",
  "method_tags": [
    "AIOps",
    "agent-evaluation",
    "fault-injection",
    "live-microservices",
    "metrics-logs-traces",
    "benchmark"
  ],
  "research_scenario": "部署中的微服务云环境评估 Agent 对检测、定位、RCA、缓解等任务的调查与动作；系统向 Agent 暴露真实工具查询结果和运行遥测。",
  "research_problem": "如何建立可重放、可计分且能覆盖 Agent–工具–云环境闭环的 AIOps 评估，而不是只在静态问答中评估根因回答？",
  "core_challenges": [
    "真实事故难复现 / 有可靠真值（§2）。",
    "症状型和功能型故障需要不同诊断深度。",
    "Agent 必须交互取证，且 benchmark 要评价完成状态与过程。",
    "正常 no-op 也需要正确判为无需故障操作（§3.6.4）。"
  ],
  "existing_method_limits": [
    "静态日志 / 问答缺少服务环境、工具反馈和操作结果；普通准确率不反映 Agent 的工具交互。此为论文动机，不代表所有既有基准缺失所有能力。"
  ],
  "core_idea": "通过微服务测试床和可控故障 / 工作负载生成环境数据，再用统一 Agent–Cloud API、遥测工具和隐藏配置 oracle 执行 / 评分任务。",
  "technical_innovations": [
    "统一的 Agent–Cloud Interface：任务、信息、工具观察和动作的 API。",
    "将 symptomatic 资源故障和 functional 配置 / 代码类故障纳入问题设计。",
    "组合检测 / 定位 / RCA / mitigation 任务和运行轨迹记录；正式版框架 100 问题、受评估成本限制实验选 48。"
  ],
  "methodology": {
    "architecture": "基准微服务应用 + 负载生成器 + 故障控制器 + Orchestrator/API + 指标 / 日志 / Trace / 配置工具 + 隐藏故障真值和评分器。",
    "data_processing": "使用 DeathStarBench HotelReservation / SocialNetwork、OpenTelemetry Astronomy Shop、自定义 TiDB 场景；Prometheus metrics、Jaeger traces、kubectl / Filebeat / Logstash logs，并提供代码 / 配置 / 集群信息。",
    "modules": [
      "问题描述 P=<T,C,S>，上下文 C=<E,I>。",
      "Orchestrator 管理服务部署、负载 / 故障、Agent API 和观察返回。",
      "故障器支持资源 / 网络症状故障和配置 / 认证 / 代码功能故障。",
      "Oracle 根据隐藏注入配置与任务完成条件评估 Agent 结果并记录轨迹。"
    ],
    "key_formulas": [
      "Problem tuple P=<T,C,S>; C=<E,I> 为任务、环境 / 信息上下文的表示（§2）。"
    ],
    "training": "AIOpsLab 是评测框架，不训练一个统一的 Agent；论文替换不同 LLM / workflow 配置作实验。",
    "inference": "Agent 接收任务，循环查询遥测 / 系统信息、观察返回、继续分析或缓解，输出结果。不同 Agent 的规划 / memory 并非框架固有能力。",
    "end_to_end": "服务部署 / 工作负载 → 控制器注入真实故障 → Agent 通过工具调查 → 执行动作 / 输出诊断 → 隐藏 oracle 自动评分。"
  },
  "experimental_evidence": {
    "datasets": [
      "HotelReservation / SocialNetwork (DeathStarBench), Astronomy Shop, custom TiDB; 100 benchmark problems, 48 selected for formal evaluation."
    ],
    "baselines": [
      "GPT-4-W-Shell",
      "GPT-3.5-W-Shell",
      "ReAct",
      "Flash"
    ],
    "metrics": [
      "任务完成 accuracy / success rates；不是 detector F1。"
    ],
    "main_results": [
      "正式版 Table 3 all-problem accuracy：GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%。",
      "两个 no-op 检测问题中，只有 GPT-4-W-Shell 识别正常工作负载；其余 Agent 有误报（§3.6.4, p.9）。"
    ],
    "ablations": [
      "比较不同 Agent / 模型配置和问题类别；核心是系统性 benchmark 评估，不是异常生成器消融。"
    ],
    "robustness_generalization": [
      "覆盖若干微服务应用与故障类别；不代表生产事故分布、Agent 跨云泛化或生成样本真实性。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [],
    "reasoned_inference": [
      "代表性故障和应用有限；运行时注入遥测是真实环境观测，但不覆盖全部生产故障分布。",
      "问题完成率不直接测量 Metric / Trace 合成或 anomaly detector 增益。"
    ],
    "evidence_gaps": [
      "正常业务高峰、扩缩容、发布与真实故障并发的困难评估任务仍需专门覆盖。"
    ]
  },
  "research_implications": [
    "可作为生成异常数据之后的运行时因果反馈 / 检测环境，但要额外构造无故障正常波动和多因共现测试（本知识库分析）。"
  ],
  "related_papers": [
    "synthetic-cloud-microservices",
    "tracellm",
    "modify",
    "capmix"
  ],
  "evidence_references": [
    "PDF §§2.1–2.5, pp.2–5, Fig.2：环境 / 故障 / API / 评估器。",
    "PDF §3.1, §3.6.4, Table 3, p.9：48 场景评测和 no-op。"
  ],
  "provenance": {
    "pdf_sha256": "ea8af2dc2bb1409b8d29ef0f571a3e4a22806cf32c81934367695da277b7d9f5",
    "reading_note_sha256": "e299a9dc92b108c6f17e376a48d1ad464cc02cee6b7ce412df15bb397e9d345e",
    "knowledge_card_sha256": "4362010b291bc2b67b5912820158d55fb4aa8a6abfdeb1b44ce8e635b5993e7e",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->
