# Knowledge Review v13：TSAD batch 11 — 全局依赖、多视角分数与潜动态合规

## Scope and Evidence Labels

本次完成第 31–33 篇实际 PDF 精读，累计 **33/33**：

- [AnoMamba](../../papers/anomamba/notes.md)：global step-size reweighting 约束 Mamba 重建依赖。
- [FlowFuse](../../papers/flowfuse/notes.md)：四视角 detector score 的 coupling-flow 联合融合。
- [Conditional Normalizing Flows](../../papers/cnf-latent-dynamics/notes.md)：latent dynamics 与 MV-KS goodness-of-fit (GOF) 合规检验。

本文将**作者主张**、**实验支持**与**跨论文分析**分开。不同数据集、标签规则及评估指标不构成可直接比较的排行榜；页码均可回到单篇 PDF 笔记查核。

## 1. 三种 normality 定义与检测位置

| 论文 | 正常行为参照 | 检测证据放置位置 | 主要适用假设 |
| --- | --- | --- | --- |
| AnoMamba | 训练序列可由包含全局依赖的 Mamba 重建；跨 patch GSR 权重受 multi-scale long-tail prior 约束 | 重建误差；隐藏状态展开的 attention map 用于分析依赖 | patch/global dependency 可从训练数值序列学习；重建误差能分开正常与异常（§§3–5.8, Eqs. 13–23） |
| FlowFuse | 训练期正常窗口的四路 score 联合分布 | flow likelihood 的经验百分位，再做 ensemble average / 可选 learned routing | 四个 detector view 中至少有互补信息，训练 score pattern 足以代表测试 normality（§§3.3–3.5, Eqs. 1–9） |
| Conditional NF | CNF latent trajectory 符合规定的 latent dynamical distribution；实验实例 LG-LDM | whitened latent window 的 MV-KS GOF，拒绝统计合规即判异常 | CNF 训练能满足 prescribed bias，且该 bias 与数据相符；检验有足够样本和维度 power（§§3.1–3.2, Eqs. 1–12） |

三者分别把约束放在**表示重建关系、检测器分数融合、潜状态统计动力学**。它们不是一种方法的不同实现：AnoMamba 保持 reconstruction residual score；FlowFuse 通过分数组合补足 detector 覆盖；CNF 则可在 observation likelihood 高时仍以 latent temporal compliance 检测结构异常。

## 2. 实验支持与边界

### AnoMamba

- **[实验支持]** 8 个基准上 F1-AF 有 7 个第一、VUS-ROC 有 6 个第一；UTS 平均 .7830/.7739，MTS .7900/.7973。（§5.4, Tables 1–2）
- **[消融支持]** 去掉 GSR，UTS F1-AF 从 .7830 降至 .6547，VUS-ROC 从 .7739 降至 .7425；MTS 的提升较小但仍有贡献。（Table 3）
- **[边界]** 固定 window 100 与 SPOT threshold；hidden attention 案例说明输入贡献变化，不验证 attention 对业务原因或因果结构忠实。（§§5.3, 5.8）

### FlowFuse

- **[实验支持]** 18 个基准多数表现最佳或具竞争力，四种 view 的融合在四个代表集消融中相对简单平均约提高 8.0% Aff-F1。（§§4.2–4.3, Tables 3, 5）
- **[实验支持]** 方法类型在六类异常间有明显偏差，mixed anomalies 仍然困难；C=8–32 较稳、E=4 后收益饱和。（§4.4, Figs. 2–3）
- **[边界]** Ensemble 分歧是 variance proxy，不是已校准不确定性；四路共同失败时 flow 没有独立新证据。window/score distribution 的稳定性以及负载切换+故障没有单独控制实验。（分析推断）

### Conditional Normalizing Flows

- **[实验支持]** 合成四维 $w=64$ 例中，MV-KS 相对 NLL 的 AUC-PR 为 82.1 vs 78.8、VUS-PR 96.0 vs 92.8、Aff-F1 92.6 vs 85.0；NLL 漏掉高 likelihood amplitude anomalies。（§4.2, Fig. 1, Table 2）
- **[实验支持]** 1080 条 TSB-AD 序列的 leaderboard 上 NLL 排 UTS 第 7、KS 第 17；MITDB latent FIT 低时 NLL 与 KS 都退化，说明 FIT 是关键门槛。（§4.2, Tables 3–5）
- **[作者明确边界]** GOF power 受 sample size / dimension 影响；较长窗口会稀释 point anomaly。CNF capacity 与 context 敏感，LG-LDM 不是所有数据的合适 inductive bias。（§5）

## 3. 正常状态、负载变化与故障

- AnoMamba 通过全局依赖重加权利用长程数值关联，但没有识别状态类别或学习 workload-conditioned 模型。全局依赖表达能力提高不等于多种业务状态被显式分开。（§§4–5）
- FlowFuse 学的是 detector scores 在训练集上的联合分布；新负载使 temporal / frequency view 同步改变时，可能整体进入低密度区域。论文没有用 release、Trace 或 workload 标签区分这种变化与故障。（§3–4；分析推断）
- CNF 将异常定义为相对某条预设动态的统计不合规，是三者中最明确声明 normality 假设并诊断训练是否实现它的方法。但一个 LG-LDM 的拒绝结果也不说明偏离来自故障还是合法状态迁移；若改用多状态 bias，需防止异常污染正常 dynamics。（§3.2, §5；分析推断）

**[跨论文分析]** 本批证明的层次是“检测器可依据全局关联、互补 score pattern 或 latent statistical dynamics 改变异常评分”。它们没有直接证明“系统识别了正常业务波动的来源”。只有 CNF 明确给出可检验的 inductive-bias hypothesis；hypothesis rejection 是统计证据，不是 workload / release / causal diagnosis。

## 4. 对全库问题的最终批次更新

| 问题 | 本批状态 | 可支持的结论 |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 多尺度依赖、多个 detector score view、预设 latent dynamics 是三种互异建模方向；本批未显式标注多个业务 operating states。 |
| 正常业务波动如何区别真实故障？ | Open | 本批检验相对训练分布 / latent law 的偏离，没有用真实负载或 release 语义区分变化来源。 |
| 方法是否只抑噪，是否解释波动来源？ | Partially Answered | FlowFuse 融合异质证据，CNF 检验假设，AnoMamba 学长程依赖；检测证据更丰富，但 none 提供经过业务因果真值验证的来源解释。 |
| 是否使用 Metric、Trace、workload、release？ | Open | 三篇输入仍为数值序列、频谱或其模型分数；无真实 Trace / release-conditioned evaluation。 |
| 正常负载变化和故障同时发生时如何处理？ | Open | 三篇均无完整并发控制矩阵；训练分布 / latent compliance 参照可能一起被新状态影响。 |
| 哪些研究问题缺少充分实验？ | Partially Answered | 状态切换+故障、holdout 新业务状态、ensemble uncertainty calibration、event delay / fixed FPR、FIT 与部署效用关系仍不足。 |

## 5. 与此前批次的联系

1. **normality reference 已多样化**：多原型/频谱（MACE、Graph-MoE、CAPMix）、context-relative（TimeRCD）、在线适配（WMMNN、CAROTS、CCM-TAD）、重建结构（AnoMamba、IGAD）、residual null（COGNOS）、latent law (CNF) 均已出现。其“正常”大多仍由训练样本、预设模型或统计参照定义；reference 变化是否代表合法业务状态，需要外部状态标签验证。
2. **利用全局信息不等同于因果解释**：CAROTS、GCAD、OracleAD、SARAD、TeamWork、ScatterAD 与 AnoMamba 都显式或间接使用关系结构，但关注点分别是因果增强、依赖图、跨时间节点、统计变量角色或状态记忆；这些结构的语义与真实 service topology / Trace 的对应性需独立验证。
3. **分数聚合 / 阈值的不确定性**：FlowFuse 的 train score percentile、CNF 的 sample-size critical value、COGNOS 的 calibration quantile、CAPMix 的 robust threshold 等均在不同假设下适用，不能把“无标签阈值”泛化成无需验证分布假设。
4. **异常检测与运维解释仍是两层任务**：AnoMamba attention、FlowFuse view score、CNF latent GOF、TFC cross-domain score 能告诉我们模型在哪些观测关系上偏离；要解释原因仍需业务上下文、拓扑、Trace、发布 / 负载记录或受控注入。

## 6. 全 33 篇收束

最后一批读完后，33 篇均有 PDF 驱动的详细笔记和知识卡片。跨论文全景与研究空白转入 [TSAD final synthesis](tsad-final-synthesis.md)，按问题检索和使用路径见 [TSAD knowledge query guide](../guides/tsad-knowledge-query-guide.md)。最终综合会对每一项研究空白附上论文证据与适用范围，不将经验性推断写成作者结论。
