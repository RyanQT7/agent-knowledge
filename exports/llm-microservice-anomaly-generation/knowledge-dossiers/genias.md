# Knowledge Dossier — GenIAS: Generator for Instantiating Anomalies in Time Series

## 1. Basic Information

- **English title**: GenIAS: Generator for Instantiating Anomalies in Time Series
- **中文译名**：GenIAS：时间序列异常实例化生成器
- **Authors**: Zahra Zamanzadeh Darban, Mike Wang, Geoffrey I. Webb, Shirui Pan, Charu C. Aggarwal, Mahsa Salehi
- **Venue / year / CCF**: arXiv:2502.08262v2, 2026-02-05（预印本） / 2026 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `genias_arxiv2502.08262.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: null
- **Research area**: 无监督 TSAD 异常样本合成与增强
- **Method tags**: TSAD, VAE, latent-perturbation, synthetic-anomaly, patching

## 2. Research Scenario

无监督 TSAD 常缺少真实异常标签，监督检测器和异常增强研究需要大量异常样本，但规则注入容易与真实异常不相似、潜在多样性不足。GenIAS 学习正常训练时间序列及其潜在分布，生成具有可控偏离程度的异常窗口，并作为合成数据支持检测器训练。输入为单变量或多变量原始时间序列窗口；输出是局部修改后的异常时间序列。该问题是通用 TSAD 数据增强，不是在线故障模拟或微服务异常诊断。（PDF §§1–3, pp.1–3）

## 3. Research Problem

如何只依赖正常序列学习可控潜变量偏离，并生成同时区别于正常、保持数据合理性和变量级局部性的异常样本？

## 4. Core Challenges

1. **候选异常需要兼具偏离和合理性**：潜变量必须从正常区分开，又不能被任意拉远到不符合数据尺度的区域。
2. **多变量异常需选择性发生**：若每个变量都同时被修改，合成样本会失去局部性和正常上下文；若统一扰动强度，数据中各变量的动态范围差异会导致注入失衡。
3. **单个模式难覆盖异常多样性**：使用固定噪声 / 规则扰动可能集中在狭窄异常形态。论文以 ARP 和 EDI 分别衡量与真实异常的表征接近度及生成样本差异性。（§3–4）
4. **潜空间生成不能自动等同异常语义**：若训练异常或真实故障原因未参与建模，潜在偏离仅表示相对所学正常分布的变化，不包含因果标签。

## 5. Limitations of Existing Methods

现有合成方法包括规则型点 / 区间注入、GAN / VAE 生成，以及在潜空间中随机扰动。作者强调既有方法常难同时控制偏离幅度、生成样本可信度和多样性。GenIAS 不另行训练异常类别生成器，而是在正常编码分布周围学习哪些潜维度应变化、变化多少；再把候选异常投影回与原始样本相连的局部 patch 中，保留未显著变化的变量轨迹。

## 6. Core Idea

先把正常表示压缩为紧致潜空间，再以可学习逐维 ψ 扰动标准差产生候选异常；解码后只替换相对原输入变化超过动态范围阈值的变量。

## 7. Technical Innovations

- 上下界 triplet-style 潜扰动损失，在潜空间要求异常偏离落在 δmin / δmax 区间（§3.2, Eq.3）。
- 零维惩罚与 compact-KL 共同控制扰动稀疏性和正常空间紧致性（Eqs.2,4）。
- 动态范围阈值 patching，按变量级 L2 差异选择是否替换，而不是整样本覆盖（§3.3, Algorithms 1–2）。

## 8. Methodology

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

## 9. Experimental Evidence

- **数据集**：MSL、SMAP、SMD、SWaT、GECCO、SWAN、UCR、Yahoo-A1、KPI；六个多变量、三个单变量。默认窗口 T=200，MTS 潜维 100、UTS 潜维 50；Adam 1e-4、1000 epochs；α=1、β=.1、γ 在 UTS / MTS 设为 0 / .01、ζ=.1。（§4.1, Appendix）
- **生成质量**：ARP 用 DeepSVDD 表征空间评估生成异常与真实标注异常的接近程度；EDI 测多样性。平均排名分别为 ARP 1.78、EDI 1.22（越好排名更低），报告在比较的异常增强方法中表现强。（§4.2, Table 1）
- **检测收益**：GenIAS 与 CARLA 配合的平均 F1 为 .557，对比 CARLA .509；MSL .579 vs .523，SMAP .620 vs .529，Yahoo-A1 .811 vs .749。（Table 2）结果表明所选基准和检测器配置下可提高若干指标，不证明对所有系统 / 真实故障都有效。
- **Patching 消融**：MSL .579/.529、SMAP .620/.467、Yahoo .811/.794（F1/AUPR）；无 patch 时分别 .535/.466、.533/.425、.755/.776。（Table 3）
- **潜空间紧致性**：比较不同先验标准差，σ_prior=.5 得到较好结果；逐维扰动与 patching 对合成质量和部分检测结果有贡献。（§4.5–4.8, Tables 3–4）
- **证据限制**：ARP 使用真实测试异常表征作为质量参照，不能把“接近真实异常”解读为真实根因标签 / 机制匹配；检测实验不含微服务 Trace 与调用拓扑。

## 10. Limitations

### A. Author-stated limitations

- 结论提出自适应扰动 / patching 和变量间相关性作为后续方向。

### B. Reasoned inference

- 没有故障类型、业务上下文或多模态服务图；潜空间偏离不是故障语义。
- ARP 依赖 DeepSVDD 表征及基准异常标签，不能视为生产故障机制验证。

### C. Evidence gaps

- 没有服务系统真实故障注入、Trace / Log 一致性或动态正常状态专门实验。

## 11. Research Implications

**本知识库分析**：适合作为经典深度生成路线与 LLM-AP 的方法对照；用多变量 patching 保留正常维度的思路需要在服务上下文下重新验证。

## 12. Related Papers

`LLM-AP`直接提示 LLM 改写；`CAROTS`显式用因果结构增强；`Synthetic Time Series`使用运行时故障注入。

## 13. Evidence References

| 论断 | 原文定位 |
| --- | --- |
| VAE 重参数化与紧致先验 | PDF §3.1, Eqs. 1–2 |
| 潜空间扰动及联合损失 | PDF §3.2, Eqs. 3–6 |
| 变量级 patching | PDF §3.3, Algorithms 1–2 |
| 数据、参数和 ARP / EDI | PDF §4.1–4.2, Table 1 |
| 下游检测与消融 | PDF §§4.3–4.8, Tables 2–4 |
| 作者未来方向 | PDF Conclusion |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "genias",
  "title_en": "GenIAS: Generator for Instantiating Anomalies in Time Series",
  "title_zh": "GenIAS：时间序列异常实例化生成器",
  "authors": [
    "Zahra Zamanzadeh Darban",
    "Mike Wang",
    "Geoffrey I. Webb",
    "Shirui Pan",
    "Charu C. Aggarwal",
    "Mahsa Salehi"
  ],
  "year": 2026,
  "venue": "arXiv:2502.08262v2, 2026-02-05（预印本）",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/genias_arxiv2502.08262.pdf",
  "reading_note_path": "papers/aiops/genias/notes.md",
  "knowledge_card_path": "papers/aiops/genias/knowledge-card.md",
  "code_url": null,
  "research_area": "无监督 TSAD 异常样本合成与增强",
  "method_tags": [
    "TSAD",
    "VAE",
    "latent-perturbation",
    "synthetic-anomaly",
    "patching"
  ],
  "research_scenario": "通用单变量 / 多变量时间序列训练数据不足时，生成候选异常窗口供下游 detector 训练；不是微服务遥测或故障 RCA。",
  "research_problem": "如何只依赖正常序列学习可控潜变量偏离，并生成同时区别于正常、保持数据合理性和变量级局部性的异常样本？",
  "core_challenges": [
    "潜空间异常应保持适中距离（§3.2）。",
    "多变量各维范围不同，注入不应破坏所有变量（§3.3）。",
    "生成质量同时涉及真实性与差异性（§4.2）。"
  ],
  "existing_method_limits": [
    "固定噪声 / 规则增强不能适应变量潜在分布；任意 VAE 潜变量偏移可能过远且整段修改原始序列；论文通过潜空间约束和逐维 patching 处理这些风险。"
  ],
  "core_idea": "先把正常表示压缩为紧致潜空间，再以可学习逐维 ψ 扰动标准差产生候选异常；解码后只替换相对原输入变化超过动态范围阈值的变量。",
  "technical_innovations": [
    "上下界 triplet-style 潜扰动损失，在潜空间要求异常偏离落在 δmin / δmax 区间（§3.2, Eq.3）。",
    "零维惩罚与 compact-KL 共同控制扰动稀疏性和正常空间紧致性（Eqs.2,4）。",
    "动态范围阈值 patching，按变量级 L2 差异选择是否替换，而不是整样本覆盖（§3.3, Algorithms 1–2）。"
  ],
  "methodology": {
    "architecture": "TCN-VAE 编码正常窗口 → ψ 重标定潜分布噪声 → 解码候选异常 → 按维度差异阈值 patch → 生成增强集 → 训练 detector。",
    "data_processing": "UTS / MTS 窗口；默认 T=200，MTS latent=100、UTS=50；六个多变量与三个单变量基准。",
    "modules": [
      "正常 VAE：z=μ+σ⊙ε，学习正常潜分布和重构。",
      "异常扰动：z̃=μ+ψ⊙σ⊙ε，固定均值并学习逐维扰动。",
      "联合目标：重构、扰动边界、零维扰动、紧致 KL。",
      "Patching：若||Xd−X̃d||₂>τ·range(Xd)则替换整条变量轨迹，否则保留。"
    ],
    "key_formulas": [
      "z=μ+σ⊙ε；z̃=μ+ψ⊙(σ⊙ε)（Eqs.1,3）。",
      "L=αLrecon+βLperturb+γLzero-perturb+ζLcomp-KL（Eq.6）。",
      "维度替换判据||Xd−X̃d||₂>τ(max(Xd)−min(Xd))（§3.3）。"
    ],
    "training": "TCN-VAE 在正常训练窗优化重构、KL 与可学习潜扰动相关损失；默认 Adam 1e-4、1000 epochs，α=1 β=.1 γ=0/.01（UTS/MTS）ζ=.1。",
    "inference": "离线由正常窗采样生成候选并 patch；下游 detector 独立输出异常分数，论文未限定一个统一检测推理公式。",
    "end_to_end": "正常序列 → VAE 潜表征 → 有边界的潜空间扰动 → 解码 → 变量级 patch → 增强 detector 训练。"
  },
  "experimental_evidence": {
    "datasets": [
      "MSL, SMAP, SMD, SWaT, GECCO, SWAN, UCR, Yahoo-A1, KPI。"
    ],
    "baselines": [
      "异常生成 / 增强基线及 CARLA detector 配置；精确完整方法名见论文 Table 1。"
    ],
    "metrics": [
      "ARP（真实异常表征接近性）",
      "EDI（多样性）",
      "下游 F1 / AUPR"
    ],
    "main_results": [
      "ARP / EDI 平均排名 1.78 / 1.22（Table 1）。",
      "GenIAS + CARLA 平均 F1 .557 vs CARLA .509；MSL .579 vs .523、SMAP .620 vs .529、Yahoo .811 vs .749（Table 2）。"
    ],
    "ablations": [
      "有 patch：MSL F1/AUPR .579/.529 vs no-patch .535/.466；SMAP .620/.467 vs .533/.425；Yahoo .811/.794 vs .755/.776（Table 3）。"
    ],
    "robustness_generalization": [
      "9 个基准多场景评测；未验证微服务、业务漂移或跨模态生成。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [
      "结论提出自适应扰动 / patching 和变量间相关性作为后续方向。"
    ],
    "reasoned_inference": [
      "没有故障类型、业务上下文或多模态服务图；潜空间偏离不是故障语义。",
      "ARP 依赖 DeepSVDD 表征及基准异常标签，不能视为生产故障机制验证。"
    ],
    "evidence_gaps": [
      "没有服务系统真实故障注入、Trace / Log 一致性或动态正常状态专门实验。"
    ]
  },
  "research_implications": [
    "作为非 LLM 时序异常合成 baseline，与 LLM 数值改写及系统级故障注入进行区分；潜变量机制可以作为对照而非真实性结论。"
  ],
  "related_papers": [
    "llm-ap-synthetic-augmentation",
    "capmix",
    "carots",
    "synthetic-cloud-microservices"
  ],
  "evidence_references": [
    "PDF §3.1–3.3, Eqs.1–6, Algorithms 1–2：模型与损失。",
    "PDF §4.1–4.8, Tables 1–4：数据、质量、下游结果和消融。",
    "PDF Conclusion：适应与变量相关性方向。"
  ],
  "provenance": {
    "pdf_sha256": "8c3e6800591915b34f00f3c3a20aa82f9050175b978f495f81be2cef847584fb",
    "reading_note_sha256": "dfcd4b417839298c1479e5bbf57e621980a16c7e41b92a1d9e19dd2911791795",
    "knowledge_card_sha256": "05aff1f9ec733a19c4037e61fbe7ace4dcf343cafbf459ca4ced9290bfb702fb",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->
