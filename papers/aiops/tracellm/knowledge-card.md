# TraceLLM 知识卡片

1. **Research Scenario**：Alibaba 2022 微服务系统的结构化调用 DAG 数据，生成 Trace 图用于结构条件控制和下游任务数据扩充；输出调用边和属性，而非故障样本。（PDF §§2–4）
2. **Core Challenges**：保持长图 DAG / 深度 / 边数约束；同时匹配长尾调用分布和条件控制。（PDF §3）
3. **Existing Limitations**：概率 / 表格生成器对结构依赖与组合约束有限；直接提示 LLM 易违反图结构。（作者动机，§1–3）
4. **Core Idea**：将 Trace 图序列化为层级文本，递归逐调用层生成，并用指令微调跟踪剩余约束。
5. **Technical Innovations**：领域继续预训练 + LoRA；DAG 分层递归生成；加入边数 / 深度中间推理。价值来自结构化生成设计，不是 LLM 本身。
6. **Key Mechanisms**：P(t|c)=∏k P(c^(k+1),t^k|c^k)；条件随机打乱 / 丢弃；图结构和属性验证。
7. **Experimental Evidence**：结构条件大图下基线有效率快速下降；合成数据训练 FIRM、真实图测试与真实数据训练准确率相差约 1.5pp；KL 和热门调用结果显示并非所有统计指标都最优。（§4, Figs. 3–7）
8. **Limitations**：未生成故障语义或 Metric / Log；单一系统域；统计或结构真实性不能证明故障机制真实性。（后两点为本知识库分析）
9. **Research Opportunities**：需要故障标签条件、运行时因果约束、跨模态 Metric–Trace–Log 一致性及真实故障检测收益验证。
10. **Related Papers**：[Synthetic Time Series](../synthetic-cloud-microservices/notes.md) 及 [AIOpsLab](../aiopslab/notes.md)提供真实运行 / 注入遥测对照；[LLM-AP](../llm-ap-synthetic-augmentation/notes.md)生成的是数值窗口；[CAPMix](../../capmix/notes.md)是 KPI 伪异常增强。

**证据分层**：结构化 Trace 生成和下游任务可用性是论文实验支持；“对真实微服务故障有用”尚未验证；语义真实与跨模态一致性缺口是本知识库分析。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/tracellm_emnlp2025.pdf)
