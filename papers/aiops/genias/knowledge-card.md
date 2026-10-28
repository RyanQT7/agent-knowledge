# GenIAS 知识卡片

1. **Research Scenario**：通用 UTS / MTS 无监督 TSAD 的离线异常样本生成和训练增强。
2. **Core Challenges**：合成样本要偏离正常分布但仍可信；多变量样本需选择性注入；还需兼顾多样性。
3. **Existing Limitations**：固定规则扰动缺少数据适配；任意潜变量偏移可能过远；原始空间整段修改容易破坏正常上下文。
4. **Core Idea**：学紧致正常潜空间，按维度学习扰动尺度，再只替换偏差足够大的变量轨迹。
5. **Technical Innovations**：带 δ_min / δ_max 的 triplet 扰动；零维惩罚；紧致 KL；基于动态范围阈值的逐维 patching。
6. **Key Mechanisms**：z=μ+σ⊙ε；z̃=μ+ψ⊙σ⊙ε；合并重构、扰动、稀疏与紧致损失。
7. **Experimental Evidence**：9 个数据集；ARP / EDI 排名领先；GenIAS+CARLA 平均 F1 .557 vs .509，MSL / SMAP / Yahoo 改善；patch 消融支持维度保留机制。
8. **Limitations**：无 LLM、故障知识、业务上下文、服务拓扑或 Metric–Trace；ARP 不等于机制真实。
9. **Research Opportunities**：研究正常状态 / 因果约束能否使潜扰动更符合特定故障机制；需单独验证跨域真实性。
10. **Related Papers**：[LLM-AP](../llm-ap-synthetic-augmentation/notes.md)直接语言模型改写数值；[CAROTS](../../carots/notes.md)基于因果结构增强；[Synthetic Time Series](../synthetic-cloud-microservices/notes.md)在服务环境注入故障。

**证据分层**：ARP / EDI 与下游 F1 为基准实验支持；“微服务故障真实性”当前无证据。

**链接**：[精读笔记](notes.md) · [知识档案](knowledge-dossier.md) · [原始 PDF](../../../sources/papers/llm-microservice-anomaly-generation/genias_arxiv2502.08262.pdf)
