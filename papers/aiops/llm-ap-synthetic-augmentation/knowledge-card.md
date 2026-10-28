# LLM-AP 知识卡片

1. **Research Scenario**：NAB 五领域的单变量连续时间序列异常样本不足；用生成窗口增强检测器训练。
2. **Core Challenges**：生成格式、窗口长度、异常类型和统计幅度必须可控，且不能因过弱 / 过强而无用 / 失真。
3. **Existing Limitations**：规则扰动多样性 / 上下文有限；未筛选的 LLM 输出不可靠。（作者动机，PDF §§1–3）
4. **Core Idea**：冻结 GPT-3.5 / GPT-4o 将上下文窗口转成结构化提示并改写数值，再用自动验证与反馈剔除失败窗口。
5. **Technical Innovations**：六类异常模板；RelDTW 距离上下界、z-score / CUSUM、子类型规则的五阶段验证；Self-Refine 最多 3 次。
6. **Key Mechanisms**：一个异常点对齐一个窗口；每提示至多 2 个正常 + 2 个异常例；失败时反馈格式 / 距离 / 类型原因。
7. **Experimental Evidence**：47 条 NAB 中 45 条生成成功；TimesNet / PatchTST / Transformer 有小幅 F1 收益，Autoformer 反而下降；验证样本优于未验证样本。（Table 8）
8. **Limitations**：单变量、无微服务语义；慢漂移可变成简单 ramp；规则验证并非真实异常机制或分布验证。
9. **Research Opportunities**：增加领域故障约束、跨模态一致性和 train-synthetic/test-real；补充 TimeGAN / VAE 基线。
10. **Related Papers**：[GenIAS](../genias/notes.md)潜空间异常注入；[CAPMix](../../capmix/notes.md)形态伪异常置信度；[TraceLLM](../tracellm/notes.md)生成图结构 Trace。

**证据分层**：特定检测器 / NAB F1 是实验支持；向微服务故障或多变量场景迁移仅为研究假设。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/llm-ap_applied-sciences-2026.pdf)
