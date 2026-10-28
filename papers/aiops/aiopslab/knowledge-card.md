# AIOpsLab 知识卡片

1. **Research Scenario**：可运行微服务云环境中评估 Agent 的异常检测、定位、RCA 和缓解任务。
2. **Core Challenges**：离线问答无法反馈真实工具结果；需故障真值、可控环境、标准 Agent 接口和完整流程评价。
3. **Existing Limitations**：静态问答 / 单一数据集不能覆盖运维 Agent 与环境交互。（作者动机）
4. **Core Idea**：微服务部署 + 工作负载 / 故障控制 + Metric / Log / Trace / 配置 API + 隐藏 oracle 评测。
5. **Technical Innovations**：Agent–Cloud 接口、症状型 / 功能型故障、统一任务表示和自动评估；Agent 推理方式可替换。
6. **Key Mechanisms**：Agent 查询真实运行时观察并行动，Orchestrator 记录轨迹；正式版 100 个框架问题中评估 48 个代表任务。
7. **Experimental Evidence**：正式版 Table 3 all-problem accuracy：GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%；两个 no-op 任务中除 GPT-4-W-Shell 外均有正常误报。
8. **Limitations**：不是异常样本生成器；基准应用 / 故障有限；任务准确率不能说明样本分布真实性或检测器增益。
9. **Research Opportunities**：把 no-op、正常工作负载变化、真实故障共现纳入评测；此为后续验证方向，不是本文已完成能力。
10. **Related Papers**：[Synthetic Time Series](../synthetic-cloud-microservices/notes.md)面向受控数据采集；[TraceLLM](../tracellm/notes.md)离线生成 Trace；[CAPMix](../../capmix/notes.md)检测增强。

**证据分层**：运行时遥测和故障注入由测试床实现；“Agent 已学会区分波动与故障”不受有限 no-op 任务支持。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/aiopslab_mlsys2025.pdf)
