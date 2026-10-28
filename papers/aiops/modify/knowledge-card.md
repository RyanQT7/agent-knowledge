# MODIFy 知识卡片

1. **Research Scenario**：SocialNetwork / TrainTicket 中融合日志、Metric、Trace，完成窗口级系统异常检测和服务级根因排序。
2. **Core Challenges**：Trace 稀疏 / 噪声，模态采样不同，浅层融合难以适配，串行检测与 RCA 可能重复编码。
3. **Existing Limitations**：单模态视角不完整；简单拼接 / 平均融合不显式建模动态通道关系。（作者动机）
4. **Core Idea**：扩散式 Trace 去噪表征 + 多尺度通道门控融合 + 调用图 GAT + 检测 / 定位共享表示的联合监督。
5. **Technical Innovations**：DNR-FE 只用于 Trace；MSCA-CGFM 含 3×3 / 5×5 深度卷积与 SE；GAT 聚合服务依赖；双任务联合损失。
6. **Key Mechanisms**：6 秒对齐；Hawkes Log 强度；Metric Transformer；Trace 高斯前向扰动与 1D CNN 去噪；交叉熵联合训练。
7. **Experimental Evidence**：两数据集平均 F1 .883、HR@1 .847；移除任何模态性能下降；移除 diffusion 平均 F1 降 3.5%，抗噪图比较较 Eadro 平缓。
8. **Limitations**：非异常生成 / 非 LLM；静态图假设、监督标签依赖、仅服务级定位、两基准；没单独验证上下文负载区分。
9. **Research Opportunities**：可把故障注入 / 故障知识作为条件，但本论文未这样做；需评估动态图和多根因。
10. **Related Papers**：[AMulSys](../amulsys/availability.md)是论文基线但全文待获取；[AIOpsLab](../aiopslab/notes.md)是运行测试床；[CAROTS](../../carots/notes.md)学习因果图结构。

**证据分层**：F1 / HR、消融和噪声测试是作者报告结果；跨负载状态鲁棒性没有被该实验确立。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/modify_jss-2026.pdf)
