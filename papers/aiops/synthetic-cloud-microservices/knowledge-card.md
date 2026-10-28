# Synthetic Time Series 知识卡片

1. **Research Scenario**：AWS EKS 上的两个电商微服务应用，构造正常需求曲线、负载异常与基础设施故障指标数据。
2. **Core Challenges**：微服务正常负载非平稳；真实故障难复现；需将注入事件时间与受影响指标对齐。
3. **Existing Limitations**：固定平稳背景 / 数值尖峰难模拟业务周期及系统级传播。（作者动机，PDF §1–3）
4. **Core Idea**：把 Locust 负载曲线生成、AWS FIS 故障注入与多层遥测采集串成可控数据构建流程。
5. **Technical Innovations**：多趋势 / 周期正常负载函数；独立负载异常注入；Pod / 节点资源与网络故障注入，提供 470 项节点、Pod、服务指标及时间标签。
6. **Key Mechanisms**：N(t) 含 base load、piecewise trend、ΣᵢAᵢ[sin²(2πt/Tᵢ)+noise]；故障标签来自 FIS 注入配置和时间区间。
7. **Experimental Evidence**：Fig. 5–6 展示故障对延迟、错误和资源指标的效应；论文没有检测器基线、F1、真实性度量或合成数据迁移实验。
8. **Limitations**：应用 / 故障覆盖有限，负载异常由乘数生成而非语义根因；无本版本 Trace 数据；未验证真实检测收益。
9. **Research Opportunities**：将此类可控故障事件与 TraceLLM 生成结构对齐；覆盖业务高峰和故障共现，检验根因标签可分性。
10. **Related Papers**：[AIOpsLab](../aiopslab/notes.md)扩展到 Agent 工具交互评测；[TraceLLM](../tracellm/notes.md)生成调用 DAG；[CAPMix](../../capmix/notes.md)做 KPI 训练增强。

**证据分层**：负载构造和 FIS 遥测是论文实际方法；“更贴近生产”只能限定为受控云实验，不等于生产分布代表性。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/synthetic-cloud-microservices-arxiv2408.00006.pdf)
