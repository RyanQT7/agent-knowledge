# 知识卡片：SARAD（Spatial Association-Aware Anomaly Detection and Diagnosis）

> 标签：**[作者主张]** 作者提出的观点；**[实验支持]** 表格、消融或案例直接支持；**[分析推断]** 本知识库的比较判断。页码均为论文 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 无监督多变量时序检测和特征级诊断，重点捕获异常时变量间空间关联下降（Spatial Association Reduction, SAR）。（§§1, 3, PDF pp.2–4）
- **[作者定义]** spatial 指 multivariate feature/channel 维度，不指地理空间。（§2, PDF p.4）

## 2. Core Challenges

- **[作者主张]** temporal reconstruction / prediction error 可能遗漏变量间结构变化，且常难指出异常特征。（§§1–2）
- **[实验支持]** association progression 本身也会包含正常下降，故作者增加 progression reconstruction 以滤除可重建的常见模式。（§3.3, Eq. 4, PDF p.6）
- **[实验支持]** 半窗口对比会稀释 SMD、PSM 等较短异常；窗口长度需权衡空间证据和短异常保留。（Appendix E.2, H, PDF pp.21–22）

## 3. Existing Limitations

- **[作者主张]** 纯 temporal 方法可能缺少跨变量关联，单独使用 GDN 式 prediction error 也无法充分利用 spatial 信息。（§§1–2, PDF pp.2–4）
- **[分析推断]** attention map 是网络内部关联 / 重建依赖，不能直接解释为真实相关、Granger 因果、系统拓扑或故障根因。

## 4. Core Idea

- **[作者主张]** 将 $X\in\mathbb R^{2W\times N}$ 分成前后两半，对两半 MHSA map 计算 $ReLU(A_1-A_2)$，按列和聚合为 spatial progression $S$，用 MLP 重建 $S$，再与数据重建残差共同评分。（§§3.2–3.4, Eqs. 1–5, PDF pp.5–7）

## 5. Technical Innovations

1. **[作者主张]** Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association maps。（§3.2, Eq. 1）
2. **[作者主张]** 前后子窗关联图的非负差 $S_h^l=ReLU(A^l_{1,h}-A^l_{2,h})$ 提取关联下降。（§3.3, Eq. 2）
3. **[作者主张]** 聚合最终层每个 attention head 的 column sum，形成 $S\in\mathbb R^{H\times N}$，统计某个 source feature 对其他特征重建贡献的下降。（§3.3, Eq. 3）
4. **[作者主张]** 用两层 MLP 重建 $S$；训练目标 $L=\|\hat X-X\|^2+\lambda_{LS}\|\hat S-S\|^2$，stop-gradient 防止 progression loss 改写 association representation。（§3.4, Eq. 4）
5. **[作者主张]** 检测分数为验证集标准化的 data residual 与 progression residual 之和；主诊断公式是 per-feature data reconstruction residual。（Eqs. 5–6）

## 6. Key Mechanisms

- **[作者主张]** Association autoencoder 旨在区分异常关联下降与可重建的正常下降；joint score 兼顾数据空间新颖性和 association-space 新颖性。（§§3.3–3.4）
- **[实验支持]** 去掉 ReLU 后多个 range metrics 下降；no-sum aggregation 在 SMD 显著退化；直接把 $S$ 当异常分数在多数数据集弱于重建误差。（Table 5, PDF p.10）
- **[分析推断]** 即使 learned association 在变化，也没有直接说明下降来源；合法控制 / 负载状态切换也可能产生 SAR。
- **[证据边界]** 主文诊断 Eq. 6 用数据 residual，而不是 progression residual 或 causal edge attribution。（PDF p.7）

## 7. Experimental Evidence

- **[实验支持]** Table 3 的 AUROC/AUPRC/VUS-ROC/VUS-PR（%）：SMD 79.97/15.09/79.67/15.02；PSM 61.87/41.06/61.77/41.01；SWaT 88.29/72.90/87.52/70.68；HAI 96.87/67.78/96.17/64.70。（PDF p.8）
- **[实验支持]** 作者报告 SMD VUS-ROC 比 MAD-GAN 高 15.51 点，HAI 比 DiffAD 高 9.92 点；PSM 比 GDN 低 1.36，SWaT 比 DIF 低 0.36，说明不同数据集优势不一。（§4.2）
- **[实验支持]** HR@150 / NDCG@150 / IPS@150：SMD 71.93/69.78/76.44，SWaT 12.83/11.65/54.34，HAI 12.10/10.16/14.07。（Table 4, PDF p.9）
- **[标注边界]** SMD 有 forensic anomalous-feature labels；SWaT / HAI 标签多是攻击来源，不保证攻击源异常或标签覆盖完整异常变量。（§4.2; Appendix E.3）
- **[复现证据]** 4 数据集、5 seeds、range AUC 与 VUS metrics；window=100、8 attention heads、attention dim=512、FFN=2048、progression hidden=64、3 epochs。代码公开。（Appendix F–G, PDF p.22）

## 8. Limitations

- **[作者明确指出]** attention 的空间计算对特征数为二次复杂度；超大监控系统开销可能显著。Feature-level forensic labels 也稀少。（Appendix B, PDF p.16）
- **[实验支持]** 半窗口关联差会稀释短异常；诊断效果依赖不完整 / 不同语义标签；HAI 推理 .39ms/样本与训练 32min 是特定硬件和规模数据。（Appendix E.2; §4.2; Appendix N）
- **[分析推断]** 未使用 workload、Trace、release 或运行状态上下文；association reduction 不解释波动成因，也没有针对正常状态切换与故障并发的控制实验。

## 9. Research Opportunities

- **[分析推断]** 增加 workload / control-state / deployment event 条件，比较合法 SAR 与故障 SAR，并测试两者并发。
- **[分析推断]** 以物理拓扑、Trace 和故障注入 ground truth 验证 attention associations 的稳定性及定位语义。
- **[分析推断]** 针对短持续异常设计可变长 / 多尺度 subseries progression，报告 detection delay、事件召回和固定误报率。
- **[分析推断]** 扩展主诊断分数，在 feature residual、association progression 和领域标注间做受控比较。
- **[分析推断]** 使用分层 channel cluster 降低 $O(N^2)$ 成本，同时验证跨 cluster 的故障传播是否仍被保留。

## 10. Related Papers

- **OracleAD**：比较当前 latent distance matrix 与稳定模板；SARAD 比较窗口两半的 attention association drop。两者都是关系证据，但不是同类因果图。
- **GCAD**：梯度估计有向 Granger predictive influence；SARAD attention map 表示模型重建依赖，不声称 Granger causality。
- **CAROTS**：以估计 Granger 图做因果增强；SARAD 直接建模 association progression。
- **Graph-MoE**：动态图与历史 memory 路由；SARAD 则把 MHSA 的关联减少重建误差作为检测器。
- **CrossAD**：学习跨尺度映射与跨窗原型；SARAD关注窗口前后变量关联的时间演进。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[SARAD PDF](../../sources/papers/tsad-2024-2026/2024/NeurIPS/SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf)
- NeurIPS 页面：[paper page](https://proceedings.neurips.cc/paper_files/paper/2024/hash/56ad264ac7448239145606cf4106042f-Abstract-Conference.html)
