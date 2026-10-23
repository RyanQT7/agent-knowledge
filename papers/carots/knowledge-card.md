# 知识卡片：CAROTS

> 根据本地论文 PDF 全文与附录。标记：**[作者主张]** 是原文观点；**[实验支持]** 是实际表格/实验支撑；**[分析推断]** 是本知识库推导。页码指本地 18 页 PDF。

## 1. Research Scenario

- **[作者主张]** 多变量时序异常检测；异常可能不是单变量幅值偏离，而是变量间正常预测性因果关系被破坏。（PDF pp.1–4, §1–3）
- **[实验支持]** SWaT、WADI、PSM、SMD、MSL 五类真实数据和 VAR / Lorenz96 两类显式因果合成系统。（PDF pp.6–8, 13–15）

## 2. Core Challenges

- **[作者主张]** 正常工况变化可以大幅改变变量值，但保留驱动—响应关系；仅凭值域/重构误差容易将其误报为异常。（热浪—空调示例，PDF pp.1–2）
- **[作者主张]** 对比学习的单一正常簇会压缩共享因果关系但语义不同的正常模式。（PDF p.5, §4.2）
- **[作者假设]** 正常期的因果图与预测机制基本时间不变。（PDF p.4, §3.2）

## 3. Existing Limitations

- **[作者主张]** 通用重构和对比方法多依据取值或分布，不显式刻画变量间因果机制；常见对比增强也不以因果保持 / 破坏为原则。（PDF pp.1–3）
- **[分析推断]** 图从有限正常训练序列估计，若负载、控制策略或环境机制切换，静态图可能误判新正常；观察数据得到的 Granger 边不自动等于物理因果事实。

## 4. Core Idea

- **[作者主张]** 用 CUTS+ 在正常训练数据上发现因果预测关系；CPA 在扰动原因后重算受影响值生成因果保持正例，CDA 选择图子结构并加随机偏置生成关系破坏负例；SOC 对比学习再融合嵌入正常中心距离与因果预测误差。（PDF pp.3–6, Eqs. (1)–(7)）

## 5. Technical Innovations

1. **[作者主张] CPA**：加扰动到抽样原因变量历史，以因果预测器更新其后果变量值，产生新的正常变化。（PDF pp.4–5, Eq. (3), Fig. 2）
2. **[作者主张] CDA**：沿估计因果图 DFS 选不同子图，扰动变量值以破坏预测关系。（PDF pp.4–5, Fig. 2）
3. **[作者主张] SOC**：按与 anchor 的相似度阈值筛掉低相似正样本，并随训练逐渐扩大正例范围，保留语义多样的正常模式。（PDF pp.5–6, Eq. (6)）
4. **[作者主张] 双分数**：正例嵌入到正常质心的距离 $A_{CL}$ 与因果预测残差 $A_{CD}$ 各自用训练统计 z-normalize 后求和。（PDF p.6, Eq. (7)）

## 6. Key Mechanisms

- **[分析推断]** CPA 编码“变化幅值可大，但因果联动一致”；CDA 编码“变化违反正常依赖”。SOC 避免把所有合法正常状态压成一个很窄的簇。
- **[作者主张]** CAROTS 的估计图用于指导增强和分数，非依赖精确恢复真图的直接监督。（PDF pp.3–6）
- **[实验支持]** 完整评分不是所有数据都优于只用对比分数；WADI 上 CAROTS AUROC/AUPRC/F1 为 0.502/0.056/0.143，CAROTS†（无 $A_{CD}$）为 0.622/0.260/0.391。（PDF pp.7–8, 17, Tables 1, 10）

## 7. Experimental Evidence

- **[实验支持]** SWaT full CAROTS 得 AUROC 0.852、AUPRC 0.764、F1 0.791；PSM 得 0.783/0.595/0.603。（PDF p.7, Table 1）
- **[实验支持]** Lorenz96 上 PG/PC AUROC 0.998/0.975；VAR 上 CT/CG 为 0.963/0.997。不同异常类型表现差异明显。（PDF p.8, Table 2）
- **[实验支持]** 去掉 SOC 后 SWaT AUROC 0.852→0.819；去掉 $A_{CL}$ 后降至 0.814。去掉 $A_{CD}$ 反而升至 0.861，反映跨数据集融合风险。（PDF p.8, Table 4）
- **[证据边界]** 按时间分块估计图的余弦相似度较高，证明估计结构一致性，不证明图本身因果正确。（PDF p.18, Table 12）

## 8. Limitations

- **[作者明确讨论]** 假设因果结构随时间稳定；未显式处理混杂变量和外生因素；建议研究动态因果图、混杂和辅助上下文。（Appendix §D, PDF p.17）
- **[实验支持]** 端到端训练时间表排除了因果发现器预训练成本；现实基准没有因果图真值。（PDF pp.13, 18）
- **[分析推断]** 业务模式切换可能改变合法因果关系；单纯加入 causal score 未证明能解释波动来源。WADI 上 $A_{CD}$ 融合明显降低结果，不能概括“融合普遍更好”。

## 9. Research Opportunities

- **[分析推断]** 将 workload、发布、Trace、控制策略作为外生上下文，建模多种运行状态下的机制变化，测试负载变化与故障同时发生的样例。
- **[分析推断]** 用干预、故障注入或领域专家图评估因果图与增强保真度，而不只比较嵌入/检测分数。
- **[证据缺口]** 研究动态因果图与可信的在线切换机制，同时衡量变化适应速度、误报、异常吸收和部署成本。

## 10. Related Papers

- CAPMix：训练期注入形态伪异常并以 DTW 调整标签；CAROTS 用图结构区分因果保持 / 破坏增强。（[CAPMix 笔记](../capmix/notes.md)）
- When Model Meets New Normals：测试时 EMA 和伪正常在线更新；CAROTS 学训练期静态因果结构。（[笔记](../when-model-meets-new-normals/notes.md)）
- GCAD、Structured Temporal Causality、Cluster-Aware Causal Mixer：同一集合中的因果 MTSAD 路线，待各篇读后比较。

## Links

- 详细精读笔记：[notes.md](notes.md)
- 原始 PDF：[CAROTS PDF](../../sources/papers/tsad-2024-2026/2025/ICML/Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf)
- 作者代码：[CAROTS GitHub](https://github.com/kimanki/CAROTS)
