# Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?

## 1. Metadata

- **Authors**: M. Saquib Sarfraz, Mei-Yen Chen, Lukas Layer, Kunyu Peng, Marios Koulakis
- **Year / Venue**: 2024 / ICML, PMLR 235（CCF A，依照人工确认清单）
- **Paper type**: position paper + empirical comparison of simple baselines; it does not propose a new deep architecture.
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/ICML/Position_Quo_Vadis_Unsupervised_Time_Series_Anomaly_Detection.pdf)
- **Official paper page**: [PMLR](https://proceedings.mlr.press/v235/sarfraz24a.html)
- **Code**: [QuoVadisTAD](https://github.com/ssarfraz/QuoVadisTAD)（PDF p.2）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

论文主张 TSAD 领域应先用朴素统计 / 最近邻 / PCA 和单块神经网络建立强基线、报告 point-wise 与 range-wise 指标并谨慎解释阈值；作者发现多种复杂 detector 在其选定数据与评估协议上未持续超过 PCA / 小型模型，且将部分模型蒸馏为线性映射后仍保留相近点级 F1。

## 3. Background and Problem Definition

论文质疑三个实践问题：广泛使用的 point-adjusted F1 可能奖励 noisy scores；文献之间常用不同数据子集或未明确传感器选择；复杂 deep model 的新增组件没有通过简洁 baseline 充分证明效用。（PDF pp.1–3, §1）

形式上，正常训练集 $X\in\mathbb R^{T\times F}$ 只包含 nominal timestamps，测试序列 $\hat X$ 有 point labels $\hat y$。模型从训练数据得到误差向量 $E=err_\theta(\hat X)\in\mathbb R^{\hat T\times F}$；有些方法需按 feature normalization，再把每时刻向量聚合成 anomaly score。作者认为跨传感器规模差异下，归一化选择会显著改变结果；本文常用聚合是 $L_\infty$，即取标准化后各 feature absolute residual 的最大值。（PDF pp.3–4, §3.1）

这篇是以评测 / 基线实践为主的立场论文。其结论是对本文选定数据、检测器和协议的实证观察，不是对未来所有复杂模型的理论否定。作者也指出深度模型或许对 forecasting 有用，但现有 TSAD 数据上的复杂度收益没有充分显示。（PDF pp.2, 9）

## 4. Core Challenges

1. **基线不足**：如果新架构只和旧式 SOTA 比，而没有 PCA / nearest neighbor / one-block model，提升未必来自创新组件。（PDF pp.2–4）
2. **误差向量尺度不同**：跨 feature 残差尺度不一致，mean–std / median–IQR normalization 会影响最终 score。（§3.1, §4.4）
3. **数据集与传感器子集不一致**：同一 WADI benchmark 有完整 127 sensor 版本和先前工作采用的 112 sensor 子集；文献常未明确具体 sensors。（§4, PDF p.6）
4. **point adjustment 的噪声偏置**：只要某个 anomaly interval 有一点预测命中，就把整段预测改为正确；random score 也可获得很高分。（§3.5, §4.2）
5. **点级与事件级目标不一致**：标准 F1 不表达检测区间的定位质量；range metric 才以事件段为单元。（§3.5）

## 5. Proposed Baselines and Mechanisms

### 5.1 简洁统计 / distance baseline

- **Sensor range deviation**：若某个测试 feature 值超出正常训练期观察到的逐传感器范围，记异常；只给出最低门槛式 OOD baseline，不建模连续时间动态。（PDF p.3, §3.2）
- **L2 norm**：以每个多变量样本向量 $\|\hat x_t\|_2$ 为分数；便宜但依赖值尺度和中心化。（§3.2）
- **1-NN distance**：逐时刻测试向量到正常训练向量的最近邻距离，越远越异常；在多变量数据上表现接近较强模型。（§3.2）
- **PCA reconstruction error**：以训练集均值中心化后拟合 PCA 子空间 $U$，投影 $\tilde X=\hat XU^TU$，残差 $E=\hat X-\tilde X$。等价于训练集上的线性 autoencoder 或样本到低维线性子空间的垂直距离。（PDF pp.3–4, Eq. / §3.2）

### 5.2 简洁神经网络 baseline

作者采用 architecture building blocks 的小版本，以检查深层组合是否必要：

1. 无激活函数的单隐藏层 linear MLP autoencoder；
2. 一个标准 MLP-Mixer block，含 token-mixing 与 channel-mixing 子层；
3. 单头 attention 的一个 Transformer block + 全连接预测头；
4. 单层 GCN + LSTM + regression output，用 GCN 混合跨变量关系、LSTM 建模时序。（PDF pp.4–5, Fig. 1, §3.3）

这些 NN baseline 主要用 forecasting 模式训练，同时在 Appendix A.2.2 对照 reconstruction；输入 multivariate forecasting window 长度为 5，90/10 train-validation split 用于 early stopping，Adam lr=.001、batch 512。特定隐藏维度：MLP 32；Mixer / Transformer embedding 128；GCN 输出 10、LSTM hidden 64。（PDF pp.6–7, §4.1, Appendix A.2）

### 5.3 Univariate 序列表示

将每个时刻表示为当前值及前 $w$ 个值组成的 $w+1$ 维滑动向量；用 $w=4$ 形成五维表示，之后可用于 1-NN 或 PCA。作者在 UCR/InternalBleeding 样本中观察到 window 4–5 已足够，进一步增大通常无额外收益。（PDF p.5, §3.4; Appendix A.2.1, p.14）

### 5.4 Residual normalization and score aggregation

每时刻误差向量可不归一化、按训练期均值 / 标准差归一化，或按 median / IQR 稳健归一化；最后以 $L_\infty$ 取最大 feature residual 作为 score。作者在 SWaT 与 WADI 比较三种设置，显示最佳选择依数据和模型而变；median-IQR 在较 noisy WADI 结果中常有帮助。（PDF pp.3–4, 8–9, Table 5）

## 6. Metrics and Evaluation Protocol

### 6.1 三种主要 F1 口径

- **Standard point-wise F1**：按逐点真值计算；选择使测试 F1 最大的 threshold。（§3.5）
- **PA-F1**：若预测区间在一个标注异常 segment 中命中至少一点，就将整段预测设为异常；论文也评估该 flawed protocol 以显示随机预测效应。（§3.5）
- **Time-series range-wise F1 ($F1_T$)**：使用 Wagner et al. 校正的 interval-level precision / recall，考虑预测区间与真实异常区间的重叠、重复命中惩罚，而非把所有 timestamp 独立平均。（§3.5）
- 作者另外报告 AUPRC，认为仅用最佳阈值 F1 不足以说明部署时行为。（PDF p.6）

### 6.2 关键协议边界

论文明确说明 F1 阈值取 test set 上的最佳值，且把它用于 precision / recall；作者为对齐既有文献采用这一协议，同时强调阈值调优并非理想部署设置。（PDF p.6）因此 Table 2 / 3 的 F1 不是无标签部署门限结果。PA-F1 更额外依赖 ground-truth interval 后处理，不适合作为唯一性能结论。

### 6.3 数据集和实现

- 主文 Table 1：四个 UCR/IB synthetic traces；SWaT；WADI-127；WADI-112；SMD（38 sensors / 28 machines）。例如 SWaT train/test 47,520/44,991；WADI-127 118,750/17,280；SMD 每机器平均 25,300/25,300。（PDF p.6）
- UCR/IB 异常含人工叠加 sine wave 或随机数字，具有可控标签，但不等于真实生产业务状态变化。（§4, pp.6–8）
- 主文 Table 2 比较六个 SOTA：MERLIN、DAGMM、OmniAnomaly、USAD、GDN、TranAD、Anomaly Transformer，以及简单统计和 NN baselines；主文优先讨论三组多变量数据，附录追加 MSL / SMAP。（PDF pp.6–8）
- 特征用 train split 缩放到 [0,1]；PCA 多变量设置 50+ sensors 取 30 PCs，10–50 取 10；univariate 取 2 PCs、窗口 5。SOTA 按原论文配置；WADI-112 的 GDN 使用已公开 checkpoint 而非重训。（PDF p.7）

## 7. Main Experimental Findings

### 7.1 简单方法与 deep SOTA

Table 2 的 standard F1 / range-wise $F1_T$ 中，PCA residual 在 SWaT、WADI-127、WADI-112 和 SMD 均达到或超过大多数对照；例：SWaT .833/.574，WADI-127 .501/.557，WADI-112 .655/.699，SMD .572/.580。1-NN / L2 在一些数据也接近对照。（PDF p.7, Table 2）作者的证据是“在这些 benchmark 上简单方法足够强”，不能外推成所有工业数据集都应使用 PCA。

随机二值输出在 SWaT PA-F1 达 .963、WADI-127 .783、WADI-112 .907、SMD .894，但 standard F1 / range F1 仅 .218/.217、.101/.106、.101/.106、.080/.080；这直接显示 PA-F1 将随机 interval hit 放大。（Table 2, p.7）

### 7.2 Univariate 与动态波形示例

在四个 UCR/InternalBleeding traces 上，PCA / 1-NN 常接近 MERLIN；例如 IB-19 的 PCA point / range F1 为 1/1，IB-17 约 .974/.974。图 2 显示生理周期相位 / 幅度正常变化可被一些方法当作异常，而 PCA Error baseline 在示例中区分较好。（PDF p.8, Table 3, Fig. 2）这些是 synthetic/internal-bleeding traces 的结果，不提供 workload context，也不等同于线上业务周期实验。

### 7.3 复杂模型可线性近似

作者把已训练复杂模型的输入—预测映射作为 teacher 输出，再用 1-layer perceptron 线性 student 学其预测；在 SWaT/WADI-112 的 point-wise F1 多数接近原模型：Mixer .780→.770 / .497→.500；Transformer .787→.772 / .534→.521；GCN-LSTM .829→.794 / .596→.587；TranAD .799→.800 / .511→.572；GDN .810→.808 / .571→.543。（PDF p.8, Table 4）这表明这些场景中的 anomaly discrimination 可被线性近似，但只测两个 dataset 和 point-F1，不能证明 deep internal dynamics 在其他任务都没有价值。

### 7.4 消融与附录结果

- Score normalization 对模型的最优结果影响显著，尤其 WADI；选择 mean/std 还是 median/IQR 会改变 F1 和 AUPRC。（PDF pp.8–9, Table 5）
- PCA dimension 改变 SWaT / WADI 结果；较高维投影对 127 sensor WADI 可能有利，需 validation 选择。（PDF p.9, Fig. 3）
- 重建与预测两种 NN baseline 模式在若干数据上的性能差异并不稳定；作者认为所测数据中预测训练无明显统一优势。（Appendix A.2.2, p.14, Table 6）
- 附录用 anomaly interval overlap IoU 在多种 hit-ratio threshold 下比较模型 agreement；模型彼此同意程度高于与 ground truth 同意程度，PCA Error / GDN 与标签吻合度相对较高。（Appendix A.1, pp.13–14, Fig. 4）
- 附录把实验从主文的 SWaT、WADI、SMD 扩到 MSL / SMAP 时，简单 PCA / 1-NN 的 SOTA 对照值引用既有 Kim et al. 2022，而非全部 baseline 重训；阅读 Table 8 应保留此来源差别。（Appendix A.3, p.15）

## 8. Contributions and Reproduction Value

### Contributions

1. 用多类统计和浅层神经模型建立强 baseline，包括 PCA residual、1-NN、线性 MLP、单块 Mixer / Transformer 和 GCN-LSTM。（§§3–4）
2. 用 point-wise、range-wise、PA-F1 及随机基线展示指标口径会重排性能；讨论 AUPRC 与 normalization。（§§3.5, 4）
3. 以线性 student 对 deep model function 做简易 distillation，发现多个模型的 point-F1 接近。（§4.3）
4. 强调复核数据、传感器子集和 anomaly labels，而非单纯累积新模型组件。（§5）

### Reproduction value

- Code 公开；特征 scaling、窗口、train-validation、主要 hidden dimension 和 PCA PCs 均报告。（PDF pp.6–7）
- 主要局限是不同方法并非统一重选阈值：作者按 test labels 选 F1 threshold；SOTA 按原论文 config，对部分方法可能使用已训练 checkpoint；MSL / SMAP SOTA 参考先前公开数值。（PDF pp.6–7, 15）
- 主文 NN baseline 使用固定基本超参，意在展示 baseline strength；而 SOTA 参数按论文设置，比较并非重新在同一优化预算下严格匹配。（§4.1）

## 9. Limitations and Critical Reading

### 作者主张及其自身实验边界

- 作者选择部分已被批评的 SMAP / MSL 在附录而非主文重点报告；认为某些标签可能 trivial / mislabelled / anomaly ratio 不真实。（PDF p.6, Appendix A.3, p.15）
- 主数据规模有限，multivariate 主文重点为 SWaT、两个 WADI 传感器版本和 SMD；UCR InternalBleeding 含合成注入异常。
- 本文 F1 / F1T 的 best threshold 在 test set 上选择，虽然作者将其作为对齐文献的展示方式，也说明了这一局限。（PDF p.6）
- Linear distillation 只在两类 multivariate 数据和 point-wise F1 上进行；不证明非线性结构对事件定位、无标签 threshold、domain transfer 或业务解释均无益。（PDF p.8）

### 分析推断

- “某 benchmark 上简单 baseline 强”是可靠的 model-selection 提醒，不等于简单 PCA 能表达动态正常业务态，也不解决 workload 与故障并发、跨实体 regime shift 或关系变化。
- 训练 / 测试最佳标签 threshold 的比较可能高估实际 operating point；公平 benchmark 还需固定 validation protocol、事件级代价和可部署 threshold。
- 许多官方 MTS 数据的切片、sensor 子集、point adjustment 和标签语义并不一致；需要结合 The Elephant in the Room 的统一 benchmark 批判，以及每篇算法实际 preprocessing 核验。

## 10. Related Papers

- **The Elephant in the Room / TSB-AD**：两者均主张 benchmark 与指标比复杂模型设计更需严谨；TSB-AD 增大曲库并分析 10 个 metrics，Quo Vadis 用较少数据和更直接 baseline 展示简单模型强度。
- **Knowledge Review v1–v6 中的 TSAD 方法**：各论文 F1、PA-F1、range F1、VUS 与 threshold policy 必须按本笔记提醒分开比较；不得只比较表内最高 F1。
- **TFMAE、MACE、TFC**：均用频域证据；Quo Vadis 提供的是评测立场，不是 frequency-based detector。
- **Fortifying Time Series**：其 robust certificate 对 score threshold / DTW perturbation 的决策稳定性提问，与本文 test-optimal F1 的可部署 threshold 问题互补，但 threat model 不同。

## 11. Questions for Further Reading

1. PCA / 1-NN 的优势在数据经多实体归一化、工作负载切换或 feature interdependence 时是否仍保留？
2. 怎样同时报告无标签 fixed threshold、validation-selected threshold、测试 oracle ceiling 与 event-level false alarm cost？
3. 新论文是否在自己的复杂组件之外报告 Quo Vadis 类型的 PCA、nearest-neighbor、单 block network baseline？
4. multivariate benchmarks 中哪些通道的变化是业务上下文/状态，哪些是明确根因故障？现成 benchmark 是否能检验这个问题？
5. 训练—测试 entity / time / sensor split 是否避免选择偏差；公开代码与正文 protocol 是否能逐项对齐？

## 12. Tags

`TSAD` `benchmarking` `simple-baselines` `PCA` `nearest-neighbor` `evaluation-metrics` `point-adjustment` `ICML-2024`
