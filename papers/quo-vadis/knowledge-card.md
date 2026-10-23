# 知识卡片：Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?

> 标签：**[作者主张]** 作者立场或解释；**[实验支持]** 数据、表格、消融直接支持；**[分析推断]** 本知识库判断。页码均为论文 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 评估无监督 TSAD 方法是否在合理数据、指标和简单 baseline 上表现出真实增益。（§1, PDF pp.1–2）
- **[实验支持]** 研究 SWaT、WADI、SMD 与 4 个 UCR/InternalBleeding trace；附录还报告 MSL / SMAP baseline 比较。（§4, Appendices A.2–A.3）

## 2. Core Challenges

- **[作者主张]** 复杂 architecture 的效用常缺少简单对照，point adjustment 会奖励 noisy / random prediction，跨文献 dataset / sensor / metric 不统一。（§§1, 4）
- **[实验支持]** 随机 baseline 的 PA-F1 在 SWaT 可达 .963，但标准 F1/range F1 约 .218/.217。（Table 2, PDF p.7）

## 3. Existing Limitations

- **[作者主张]** 仅与旧 SOTA 对照不足以证明复杂模型有必要，point-wise F1 也无法表示 interval localization。（§§1, 3.5）
- **[分析推断]** 本文自身也用 test-set best threshold 计算 F1/F1T；其方法展示适合作为 baseline / 评测警示，不是无标签部署结果。（PDF p.6）

## 4. Core Idea

- **[作者主张]** 建立无训练复杂度、易解释的 baseline 家族：sensor range / L2 / 1-NN / PCA residual，以及一个线性 MLP、单块 Mixer、单块 Transformer、单层 GCN-LSTM；与复杂 detector 在多个 metric 下比较。（§§3–4）

## 5. Technical Innovations

1. **[作者主张]** PCA projection residual $E=\hat X-\hat XU^TU$ 作为线性子空间距离 baseline。（§3.2, PDF pp.3–4）
2. **[作者主张]** multivariate residual 按 mean–std 或 median–IQR 标准化，最后 $L_\infty$ 聚合 feature scores。（§3.1）
3. **[作者主张]** 为 univariate signals 构造 current + past 4-point embedding，再用 NN / PCA 检查 subsequence anomaly。（§3.4）
4. **[作者主张]** 用 1-layer perceptron 蒸馏 deep detector 的预测映射，检验 anomaly score 是否仍可线性近似。（§4.3, Table 4）

## 6. Key Mechanisms

- **[实验支持]** PCA residual 在主表四组 multivariate split 的 standard F1 / range F1 均有很强结果；小型网络 baseline 在多个数据也接近 / 超过复杂模型。（Table 2, PDF p.7）
- **[实验支持]** 多个 deep model 经线性蒸馏后 SWaT / WADI-112 point F1 接近原模型。（Table 4, PDF p.8）
- **[分析推断]** 该证据支持“应设简单 baseline”和“当前数据上的模型决策可简单近似”，不能推出 PCA 足以建模所有动态正常状态 / 多变量根因。

## 7. Experimental Evidence

- **[实验支持]** 随机预测 PA-F1 极高而标准 F1 / $F1_T$ 低；PCA residual 在 SWaT、WADI-127/112、SMD 多项 standard / range F1 强。（Table 2）
- **[实验支持]** PCA dimensions、score normalization 和 reconstruction vs forecast 有敏感性 / 对照；median-IQR 对部分 noisy WADI 有帮助。（Tables 5–6, Figs. 3, PDF pp.8–9, 14）
- **[实验支持]** 28 机器 SMD 的 per-machine 结果取均值；WADI-127 与 WADI-112 说明 sensor subset 会影响分数。（Table 1, PDF p.6）
- **[协议边界]** F1 threshold 在 test labels 上优化；PA-F1 使用真值后处理；不能直接视作部署门限表现。（§3.5, p.6）

## 8. Limitations

- **[实验支持]** 主文多变量范围集中在 SWaT/WADI/SMD；UCR/IB 含人为 sine/random injected anomalies；MSL / SMAP baseline 的 SOTA 比较部分引用既有结果。（§4; Appendix A.3）
- **[分析推断]** 浅层模型优势对本文所选 dataset、preprocessing、threshold 和 F1 protocol 有条件；数据不含显式负载 / release / Trace context，不能单独回答正常业务波动与真实故障来源。
- **[评测边界]** linear distillation 的证据只涉及部分模型、两个数据集、point-wise F1，不能概括所有能力。

## 9. Research Opportunities

- **[分析推断]** 在每篇新方法的同一数据预处理下添加 PCA、1-NN、线性 MLP 与小网络基线；同时报告时间和空间成本。
- **[分析推断]** 统一 sensor split / entity split / threshold / point 与 interval metrics，拆分 test oracle ceiling 和实际 validation threshold。
- **[分析推断]** 用含负载、发布和故障并发标注的 benchmark 检验简单统计基线的失效边界，并衡量复杂方法的新增解释能力。

## 10. Related Papers

- **The Elephant in the Room / TSB-AD**：Quo Vadis 以朴素 baseline 和线性蒸馏实证；TSB-AD 扩至 40 datasets / 40 algorithms 并系统分析多种 metric。
- **TFMAE、MACE、TFC**：都是频域 TSAD 方法；本 paper 的贡献为基线和评估立场，不是频谱 detector。
- **其他已读 TSAD**：精读比较时需显式注明各文是否使用 test-label Best-F1、point adjustment、VUS / event score，并增加简单 baseline 对照。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[Quo Vadis PDF](../../sources/papers/tsad-2024-2026/2024/ICML/Position_Quo_Vadis_Unsupervised_Time_Series_Anomaly_Detection.pdf)
- PMLR 页面：[paper page](https://proceedings.mlr.press/v235/sarfraz24a.html)
