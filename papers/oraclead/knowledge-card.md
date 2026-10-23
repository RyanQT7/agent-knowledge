# 知识卡片：OracleAD（Structured Temporal Causality）

> 证据标签：**[作者主张]** 表示作者提出的动机或解释；**[实验支持]** 表示表格、消融或案例直接支持；**[分析推断]** 表示本知识库的比较判断。页码均指论文 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 多变量时序异常检测同时考察变量自身的时间动态和变量间关系偏移。（§3, Eqs. 1–2, PDF pp.4–5）
- **[实验支持]** 在 PSM、SMD、SWaT 仅用正常训练数据学习，再对测试时刻给出分数；窗口长度 $L=10$。（§4.1, PDF p.7）

## 2. Core Challenges

- **[作者主张]** 不同变量时间规律异质；单独 prediction error 可能漏掉数值正常但通道关系已变的异常。（§§2.1, 3.1）
- **[实验支持]** prediction score 响应尖锐但可能只覆盖异常起点；结构偏差能持续但有窗口滞后和恢复期残留。（§4.3, Fig. 2, PDF pp.9–10）

## 3. Existing Limitations

- **[作者主张]** 现有统一时空模型可能混合异质变量动态；只看预测 / 重建误差可能缺少结构异常线索。（§§2.1, 3.1）
- **[分析推断]** OracleAD 的 SLS 是对称 latent distance 模板，不能等同于方向性因果图或物理根因证据；推理期固定模板也未条件化 workload / operating mode。

## 4. Core Idea

- **[作者主张]** 每通道独立 LSTM 编码历史，通道 embedding 经 MHSA 融合；以训练期平均 latent pairwise distance（SLS）作为正常结构参照，将预测误差与结构偏差相乘。（§§3.1–3.4, Eqs. 3–17, PDF pp.4–7）

## 5. Technical Innovations

1. **[作者主张]** 学习每变量时间摘要 $c_i$：LSTM hidden states 经时间注意力加权池化。（§3.1, Eqs. 3–5）
2. **[作者主张]** 对 $[c_1,\ldots,c_N]$ 沿变量维使用 MHSA，形成有上下文的 $c_i^*$。（§3.1, Eqs. 6–8）
3. **[作者主张]** 每变量 decoder 同时重构历史、预测末点，组合 prediction、reconstruction 与 SLS deviation loss。（§3.1, §3.3, Eqs. 9–14）
4. **[作者主张]** 每 epoch 平均训练窗口的 L2 latent-distance matrix，得 SLS；测试时使用 $\|D_t-SLS\|_F$ 作为关系偏差。（§3.2, Eqs. 11–13, §3.4 Eq. 16）
5. **[作者主张]** 最终异常分数为 $P_t^{score}\times D_t^{score}$；偏差矩阵可按行 / 列聚合候选变量。（§3.4, Eq. 17; §4.3, Fig. 3）

## 6. Key Mechanisms

- **[作者主张]** prediction score 锚定局部时刻，SLS deviation 补充持续结构变化；乘积希望抑制仅单侧偏高的误报并补偿漏检。（§4.3, PDF pp.9–10）
- **[实验支持]** 乘积 full model 多数指标整体平衡，但 deviation-only 在 SWaT 的 F1 略高于 full；不是逐项绝对最佳。（Table 2, PDF pp.9–10）
- **[分析推断]** 任何单项分数过低都会降低乘积；静态均值 SLS 可能把不同合法状态混合，并可能将合法结构切换判为异常。
- **[证据边界]** “causal embedding”是作者给历史表示的命名；SLS 由对称 L2 距离构成，不含方向或干预验证。（§§3.1–3.2）

## 7. Experimental Evidence

- **[实验支持]** Table 1（五 seed 均值，%）OracleAD 在 PSM / SMD / SWaT 的 F1 为 65.85 / 43.03 / 76.50，AUC-ROC 为 84.78 / 83.56 / 82.71，VUS-PR 为 68.17 / 47.52 / 74.16。（Table 1, PDF p.8）
- **[实验支持]** Table 1 中 SWaT VUS-ROC SARAD 为 86.30，高于 OracleAD 82.42；SWaT R-F1 OmniAnomaly 为 38.72，高于 OracleAD 28.15。作者报告的是多数而非所有指标领先。（Table 1）
- **[实验支持]** 去掉重构 loss 后 Table 2 的 PSM F1/V-ROC/V-PR 从 full 65.85/84.24/68.17 降到 58.03/74.56/54.40；结构分数及 prediction 分数单独使用时优势随数据集不同。（Table 2, PDF pp.9–10）
- **[实验支持]** Appendix G 在若干 SMD 代表性异常点比较 top-3 候选变量与标注；这是案例量化，不是全数据集 root-cause accuracy。（Table S10, PDF p.30）
- **[评测限制]** 标准化仅拟合训练集、无 validation split、5 seeds；二值 F1 阈值按测试 ground truth 最优化（200 个候选阈值），需与无标签部署门限区分。（Appendix C.1, p.19; D.3, p.22）

## 8. Limitations

- **[作者明确指出]** Appendix I：全局 SLS 假设变量关系稳定且输入连续；异构或混合类型传感器（如 SWaT）可能使偏差失去区分力。作者提出变量类型无关建模和动态 SLS 作为未来工作。（PDF p.31）
- **[实验支持]** 结构分数会有窗口进入延迟，并可能在恢复期残留；定位分析主要是 SMD 示例，不能证明物理根因。（§4.3, Figs. 2–3; Appendix G）
- **[分析推断]** 未评测业务负载、发布、扩缩容状态及其与故障并发；测试标签 oracle threshold 限制部署解释。主表和 ablation 的 SMD 结果口径也应谨慎核对。（Table 1 vs Table 2; Appendix D.3）

## 9. Research Opportunities

- **[分析推断]** 比较单一 SLS、多模板 SLS 与 context-conditioned SLS，并以负载 / 发布标注核验合法状态切换。
- **[分析推断]** 设计“正常负载切换 + 同时注入故障”的控制实验，评估结构更新的污染、回滚及检测延迟。
- **[分析推断]** 将偏差矩阵与已知拓扑、Trace、故障注入根因做定量验证，避免把 latent relation 等同于因果解释。
- **[分析推断]** 比较乘积、校准加和或门控融合在单侧异常证据场景下的漏报风险，并使用独立 validation / 固定门限报告运行代价。

## 10. Related Papers

- **GCAD / CAROTS**：均关注跨变量结构；GCAD 估计有向 Granger predictive influence，CAROTS 以 Granger 图引导增强；OracleAD 的 pairwise latent distance 对称且非因果图。
- **SARAD**：检测 attention map 中 feature association 的时间下降，并重构 progression；OracleAD 比较 latent-distance 模板。
- **CCM-TAD**：其 causal 表示时间遮罩 / 防未来泄漏；OracleAD 的 causal embedding 是逐通道历史表示。
- **Graph-MoE**：memory router 选择不同 GNN 深度的潜在专家；OracleAD 以静态 SLS 做结构偏差评分。
- **When Model Meets New Normals**：显式测试时适应；OracleAD 推理期冻结 SLS，动态模板只是作者 future work。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始论文 PDF：[Structured Temporal Causality / OracleAD](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf)
