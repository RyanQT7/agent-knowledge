# GenIAS：Generator for Instantiating Anomalies in Time Series

## 1. Metadata

- **Authors**: Zahra Zamanzadeh Darban, Mike Wang, Geoffrey I. Webb, Shirui Pan, Charu C. Aggarwal, Mahsa Salehi（按 arXiv v2 首页）
- **Version / year**: arXiv:2502.08262v2, 2026-02-05；本次核验版本为预印本，未标注会议录用信息
- **arXiv**: https://arxiv.org/abs/2502.08262
- **Local PDF**: [arXiv v2](../../../sources/papers/llm-microservice-anomaly-generation/genias_arxiv2502.08262.pdf)
- **Code**: 未从论文 / 官方元数据核验作者实现地址
- **Paper ID**: genias
- **Tags**: TSAD; synthetic-anomaly; VAE; latent-perturbation; patching; diversity

## 2. One-Sentence Summary

GenIAS 用 TCN-VAE 学习正常序列的紧致潜空间，按可学习的逐维扰动扩展潜变量产生候选异常，再仅替换与原序列偏差超过范围阈值的维度；它是无需 LLM 的通用数值异常生成器，在多类数据上评估样本代表性、多样性及若干检测器收益，不建模微服务故障语义或多模态关系。

## 3. Research Scenario and Problem

无监督 TSAD 常缺少真实异常标签，监督检测器和异常增强研究需要大量异常样本，但规则注入容易与真实异常不相似、潜在多样性不足。GenIAS 学习正常训练时间序列及其潜在分布，生成具有可控偏离程度的异常窗口，并作为合成数据支持检测器训练。输入为单变量或多变量原始时间序列窗口；输出是局部修改后的异常时间序列。该问题是通用 TSAD 数据增强，不是在线故障模拟或微服务异常诊断。（PDF §§1–3, pp.1–3）

## 4. Core Challenges

1. **候选异常需要兼具偏离和合理性**：潜变量必须从正常区分开，又不能被任意拉远到不符合数据尺度的区域。
2. **多变量异常需选择性发生**：若每个变量都同时被修改，合成样本会失去局部性和正常上下文；若统一扰动强度，数据中各变量的动态范围差异会导致注入失衡。
3. **单个模式难覆盖异常多样性**：使用固定噪声 / 规则扰动可能集中在狭窄异常形态。论文以 ARP 和 EDI 分别衡量与真实异常的表征接近度及生成样本差异性。（§3–4）
4. **潜空间生成不能自动等同异常语义**：若训练异常或真实故障原因未参与建模，潜在偏离仅表示相对所学正常分布的变化，不包含因果标签。

## 5. Existing Methods and Core Idea

现有合成方法包括规则型点 / 区间注入、GAN / VAE 生成，以及在潜空间中随机扰动。作者强调既有方法常难同时控制偏离幅度、生成样本可信度和多样性。GenIAS 不另行训练异常类别生成器，而是在正常编码分布周围学习哪些潜维度应变化、变化多少；再把候选异常投影回与原始样本相连的局部 patch 中，保留未显著变化的变量轨迹。

## 6. Methodology

### A. 正常潜变量学习

使用 TCN 编码器 / 解码器处理窗口 x。编码器输出均值 μ 和标准差 σ，按重参数化取得正常潜样本：

z = μ + σ ⊙ ε，ε ~ N(0,I)。

与通常 VAE 相比，GenIAS 使用标准差小于 1 的紧致先验标准差 σ_prior，KL 项推动正常表示集中在更紧的区域，便于将可控偏离表示成候选异常。（§3.1, Eq. 1–2）

### B. 潜空间扰动生成

候选异常潜变量为：

z̃ = μ + ψ ⊙ (σ ⊙ ε)。

ψ 是可学习的逐维扰动尺度，均值 μ 固定，扩张 / 重标定标准差贡献。扰动损失 L_perturb 用 triplet 风格的距离约束，让生成潜变量与正常重构的距离至少达到 δ_min，同时不超过 δ_max，兼顾偏离和可行性。零维扰动惩罚 L_zero-perturb 鼓励保留部分潜维度不变，增加潜维度选择性。紧致 KL 项 L_comp-KL 收缩正常表示；重构项 L_recon 保持 VAE 对原始窗口的表达能力。总损失：

L = α L_recon + β L_perturb + γ L_zero-perturb + ζ L_comp-KL。

符号 δ_min / δ_max 为偏离边界，α、β、γ、ζ 控制重构、异常扰动、维度稀疏与紧致先验项的权重。损失中的异常候选不是有真实故障标签的生成监督，而是针对潜空间几何的目标。（§3.2, Eqs. 3–6）

### C. 原始空间逐维 patching

将生成潜变量经解码器得到候选序列 X̃。针对原始变量 d，计算与原始输入 X_d 的 L2 距离；若

||X_d − X̃_d||₂ > τ × (max(X_d) − min(X_d))

则以生成轨迹替换该变量，否则保留原始轨迹。τ 控制相对于变量动态范围的选择门槛。这个机制是按整条变量维度保留 / 替换，不是按单个时间点剪贴。Algorithm 1–2 描述候选生成和 patching。（§3.3）

### D. 训练、生成与检测

1. 用训练集正常窗口优化 TCN-VAE 和上述联合目标。
2. 从正常窗口潜分布采样 z，再用 ψ 产生 z̃。
3. 解码成多维候选序列。
4. 依据逐维距离 / 动态范围阈值保留变化明显的轨迹，其余沿用原窗口。
5. 用合成样本与已有训练数据训练下游检测模型。

原文的生成评价使用学习到的深度表征；训练异常样本生成器并不需要把正常 / 异常类型以语言形式输入。下游异常评分是检测器自身实现的，GenIAS 不限定唯一检测器。

## 7. Experimental Evidence

- **数据集**：MSL、SMAP、SMD、SWaT、GECCO、SWAN、UCR、Yahoo-A1、KPI；六个多变量、三个单变量。默认窗口 T=200，MTS 潜维 100、UTS 潜维 50；Adam 1e-4、1000 epochs；α=1、β=.1、γ 在 UTS / MTS 设为 0 / .01、ζ=.1。（§4.1, Appendix）
- **生成质量**：ARP 用 DeepSVDD 表征空间评估生成异常与真实标注异常的接近程度；EDI 测多样性。平均排名分别为 ARP 1.78、EDI 1.22（越好排名更低），报告在比较的异常增强方法中表现强。（§4.2, Table 1）
- **检测收益**：GenIAS 与 CARLA 配合的平均 F1 为 .557，对比 CARLA .509；MSL .579 vs .523，SMAP .620 vs .529，Yahoo-A1 .811 vs .749。（Table 2）结果表明所选基准和检测器配置下可提高若干指标，不证明对所有系统 / 真实故障都有效。
- **Patching 消融**：MSL .579/.529、SMAP .620/.467、Yahoo .811/.794（F1/AUPR）；无 patch 时分别 .535/.466、.533/.425、.755/.776。（Table 3）
- **潜空间紧致性**：比较不同先验标准差，σ_prior=.5 得到较好结果；逐维扰动与 patching 对合成质量和部分检测结果有贡献。（§4.5–4.8, Tables 3–4）
- **证据限制**：ARP 使用真实测试异常表征作为质量参照，不能把“接近真实异常”解读为真实根因标签 / 机制匹配；检测实验不含微服务 Trace 与调用拓扑。

## 8. Limitations and Research Relevance

**作者提到的后续方向**：自适应扰动 / patching 和变量间相关性的进一步建模。（Conclusion）

**本知识库分析**：当前模型直接操作原始多维时序，但没有业务上下文、告警标签、服务调用机制或 Metric–Trace 联合约束。扰动学习的是正常潜在分布外扩方向，而不是已知故障机制；生成样本可信度依赖于 ARP / EDI 选取的表征和数据集异常标签。泛化到新负载状态的能力未由专门的动态业务状态实验支持。

## 9. Relationship to This Topic

GenIAS 是 [LLM-AP](../llm-ap-synthetic-augmentation/notes.md) 的非 LLM 生成对照：前者从正常潜在分布扰动，后者让 LLM 直接改写数值窗口并做显式规则过滤。与 TSAD [CAPMix](../../capmix/notes.md) 相比，GenIAS 是 VAE 潜空间候选生成 + 变量级 patch，CAPMix 则使用 CutAddPaste 并以 DTW 相似度修订伪标签、在输入和 TCN 潜空间做 Mixup。与 [CAROTS](../../carots/notes.md) 相比，GenIAS 不注入因果关系先验。与 [Synthetic Time Series](../synthetic-cloud-microservices/notes.md) / [AIOpsLab](../aiopslab/notes.md) 相比，GenIAS 在数据空间增强，不执行服务级故障注入。

## 10. Evidence Map

| 论断 | 原文定位 |
| --- | --- |
| VAE 重参数化与紧致先验 | PDF §3.1, Eqs. 1–2 |
| 潜空间扰动及联合损失 | PDF §3.2, Eqs. 3–6 |
| 变量级 patching | PDF §3.3, Algorithms 1–2 |
| 数据、参数和 ARP / EDI | PDF §4.1–4.2, Table 1 |
| 下游检测与消融 | PDF §§4.3–4.8, Tables 2–4 |
| 作者未来方向 | PDF Conclusion |
