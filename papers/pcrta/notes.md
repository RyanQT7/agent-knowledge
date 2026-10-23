# Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection

## 1. Metadata

- **Authors**: Liaoyuan Tang, Zheng Wang, Guanxiong He, Rong Wang, Feiping Nie
- **Year / Venue**: 2024 / IJCAI（CCF B，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf)
- **Proceedings PDF**: [IJCAI 2024, paper 0548](https://www.ijcai.org/proceedings/2024/0548.pdf)
- **Model name**: PCRTA（Perturbation-guided Contrastive Representation Learning for Time-series Anomaly detection）
- **Code**: 论文正文未给出代码仓库链接；已披露核心网络和主要训练超参。
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

PCRTA 先以六种人工设计的 point / contextual / collective perturbation 训练 7 类扰动识别器，再将其预测伪标签用于同类 top-k 正样本和异类负样本选择，借助 TCN + projection network 学习表征；推理时用 LOF 分别评价原序列及六种扰动 view 的 embedding，取平均作为 anomaly score。（§3, Eqs. 1–9, PDF pp.3–6）

## 3. Background and Problem Definition

论文关注 self-supervised contrastive TSAD 的两个薄弱环节：time-series augmentation 的语义影响不清楚，以及正 / 负样本选择若将同类样本误配为负，会造成 class collapse 或低效表示。作者提出的核心假设是：若一个真实异常受某种 perturbation 影响，其“perturbation type”相较正常行为更容易被分类器混淆；分类器输出的扰动伪标签因此可以辅助识别困难的异常相关表示。（§§1–2, pp.1–3）

形式上，多变量序列 $X=\langle x_1,\dots,x_N\rangle$ 中 $x_t\in\mathbb R^D$。先用长度 $l$、stride $r$ 划为 subsequences $s_t$；训练 stride 用 $r$，推理 stride 为 1。每个推理窗口得到一个 score 并赋给该窗口最后时刻，最开始 $l-1$ 个时间点补零。（§3.1, p.3）

PCRTA 是无监督表示学习 + LOF outlier scoring；它不直接输出经校准的概率，也不对 anomaly type 做人工监督分类。（§3.1, §4.2）

## 4. Core Challenges

1. **augmentation 与异常语义重叠**：随机噪声、尺度 / 片段变形可能本身构造出类似真实异常的观测，不能假设增强结果仍是等价正常 positive。（§3.3, p.4）
2. **高维距离 / 分布几何使近邻选样不稳**：高维样本更可能呈 hyper-ellipsoidal 而非 hyper-spherical 分布，直接按嵌入距离构造同类正例会误配。（Proposition 1, §3.4, p.4）
3. **人工 anomaly class labels 不可得**：真实标签缺乏；必须从自动生成的扰动及其分类混淆中形成伪标签。（§3.3–3.4）
4. **点级 anomaly score 与事件检测不同**：窗口分数对应最后时点，检测 F1 还需选 threshold；异常区间连续性由评估 protocol 决定。（§3.1, §4.1）

## 5. Architecture Overview

```text
多变量序列 → 滑动窗口 S
  ├─ augmentation pool Ω: 原始 + point / contextual / collective 共 6 个局部扰动
  ├─ TCN φ 建模窗口时间关联
  ├─ perturbation classifier：学习 7 类扰动标签，交叉熵 L_mul → 预测伪标签 Π
  ├─ projection Ψ：压缩高维表示 z，按 Π 选同类 top-k cosine positives / 异类 negatives
  └─ L = L_mul + α L_con，更新分类、TCN / projection 表示

推理：原始窗口及 6 个 perturbation view → embedding → 7 次 LOF score → 平均为窗口异常分数
```

（Fig. 2, Eqs. 1–9, §§3.2–3.4, pp.3–6）

## 6. Method in Detail

### 6.1 六类人工设计 perturbation

作者先将时序数据归一化至 $[0,1]$，定义 $\Omega$ 为“原始输入 $\delta_0$ + 六个 perturbation”，从 point / contextual / collective 三种基础异常构造中取变体（Eq. 2, p.4）：

1. **Point anomaly** $\delta_{I,\gamma}$：修改输入窗口最后一个时刻，随机选中维度值替换成全局极值 $\gamma=+2$ 或 $-2$。
2. **Contextual anomaly** $\delta_{II,\gamma}$：将最后观测的部分维度，按前 $k=10$ 个值均值施加偏移 $\gamma=+0.5$ 或 $-0.5$，令其相对局部上下文改变。
3. **Collective anomaly** $\delta_{III,\gamma}$：在窗口中一个片段内随机挑维度，以 $\gamma=0$ 或 $1.0$ 替换，形成联合 / 区间型偏离。

这些参数是作者实现的通用扰动设计，不是由每个数据集估计出的 anomaly distribution。训练时原始窗口标签为 class 0，六种 transformed samples 标签分别对应 class 1–6。扰动识别器用已知 transform ID 做交叉熵训练（Eq. 3）。（§3.3, Eqs. 2–3, pp.3–4）

### 6.2 TCN temporal encoder 与 perturbation classifier

先用 temporal modeling network $\phi$（TCN）提取窗口时序表示，捕捉变量内 / 变量间时间上下文；作者选择 TCN 以并行卷积替代 RNN 的逐步递归。扰动分类网络以这些表示判定原始 / augmentation 类型，交叉熵为：

$$\mathcal L_{mul}=-\frac1N\sum_i\sum_j y_{ij}\log p_{ij}. \tag{3}$$

训练分类器时监督标签来自合成 augmentation 的类别。随后模型对这些 view 给出的类别输出 / pseudo-label $\Pi$ 被送入 contrastive network，决定正 / 负 pair，不使用真实 anomaly labels 来筛 pair。（§3.2–3.3, pp.3–4）

### 6.3 Projection 与伪标签指导的 contrastive selection

作者将高维 TCN representation $\phi(\Omega(S))$ 投影到低维空间：

$$Z=\{z_1,z_2,\ldots\}=\Psi(\phi(\Omega(S))). \tag{5}$$

对每个 anchor $z_i$，先按其 pseudo-label $\pi_c$ 找同类 embedding，再计算 cosine normalized dot product：

$$d_{ji}=\frac{z_i^Tz_j}{\|z_i\|\|z_j\|},\quad z_i,z_j\in\pi_c. \tag{6}$$

同类里 similarity top-$k$（默认 $k=5$）构成 positive set $Z_i^+$（Eq. 7）；其他类别表示全部作 negatives。Eq. 8 用 temperature $\tau$ 控制 exponential similarity 的 softmax / contrastive separation：

$$\mathcal L_{con}=-\frac1C\sum_c\sum_{z_i,z_n}\log\frac{\sum_{z_i^+\in Z_i^+}\exp(z_i^Tz_i^+/\tau)}{\sum_{z_i^+\in Z_i^+}\exp(z_i^Tz_i^+/\tau)+\sum_{z_n}\exp(z_i^Tz_n/\tau)}. \tag{8}$$

作者的机制解释：若真实 anomaly view 难以被分类为正确扰动类别，预测 pseudo-label 会不同于部分正常 view；contrastive network 由此将跨伪类表示推远，并学习更有区分度的 embedding。该“分类混淆—异常相关性”是方法假设，不能把 classifier confidence 当作直接的真异常概率。（§3.4, Proposition 1, Eqs. 5–8, pp.4–5）

联合训练目标：

$$\mathcal L=\mathcal L_{mul}+\alpha\mathcal L_{con}, \tag{1}$$

默认 $\alpha=.2$。（§3.2, §4.1, p.5）

### 6.4 Inference：7 个 view 的 LOF average

训练完成后，对每个 test window 生成原始 embedding 与六个增强 embedding，分别计算 LOF score，最后对七个分数取平均：

$$s_i=\frac1C\sum\mathrm{LOF}(z_{aug}). \tag{9}$$

（正文记为 $C$ 个 representation；实现 view 为 6 augmentations + original。）分数高表示在 embedding neighbor distribution 中更离群。由于推理也包含多种 perturbation view，这一步比单次 encoder + LOF 更重；论文未提供完整 latency / memory 对照。（§4.2, p.6）

### 6.5 训练和数据参数

- TCN：kernel size 2、单 hidden layer、16 neural units。
- window length $l$ 与数据集 / 方法设置有关；多变量推理 stride 1；部分大数据 SWaT / WaQ 使用训练 stride 100 / 5。
- 最多 100 epochs，默认 $\alpha=.2$、positive top-$k=5$。
- 多数据集实验在 Intel Xeon Gold 6248R + NVIDIA Titan Xp 10GB、Ubuntu 20.04 上运行。（§4.1, PDF pp.5–6）

## 7. Experimental Design and Evidence

### 7.1 Dataset / baseline / metric

- **6 个数据集**：WaQ、DSADS、Epilepsy、ASD、SMD、SWaT；SMD 只保留 3 台机器（3-1、3-9、3-11），作者依据数据质量分析排除其他 entity。（Table 1, p.5）
- **13 个对照**：OCSVM、GOAD、ECOD、LSTM-ED、TCN-ED、DSVDD、MSCRED、OmniAnomaly、USAD、GDN、NeuTraL、TranAD、COUTA。（§4.1）
- **指标**：F1 与 AUC-PR。论文枚举 timestamp score thresholds 计算 Precision/Recall，采用 test labels 可得的 best F1；AUC-PR 提供阈值曲线平均值。（§4.1）因此 best F1 是 benchmark best-case，不是固定 threshold 的运行点。

### 7.2 主结果

Table 2（PDF pp.6–7）报告 F1 / AUC-PR mean±std。PCRTA 数值：WaQ .784 / .794，DSADS .943 / .960，Epilepsy .934 / .964，ASD .927 / .933，SMD .987 / .988，SWaT .978 / .996。作者称在五个数据集排名第一、ASD 排第二；Epilepsy 相对 COUTA 的提升约 13% F1 / 17% AUC-PR。（§4.2, Table 2, pp.6–7）

### 7.3 Representation、generalization 和 ablation

- **Epilepsy t-SNE**：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。
- **Synthetic mixed-anomaly case**：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。
- **Ablation（Table 3, p.7）**：在 WaQ / DSADS / Epilepsy 上，完整 PCRTA F1 为 .78 / .94 / .93；替换 pseudo-label 为 ground-truth augmentation class 为 .73 / .93 / .89；去掉 $L_{mul}$ 为 .67 / .61 / .92；去掉 $L_{con}$ 为 .74 / .90 / .87。三种组件大多提供增益，但贡献依数据集而变，Epilepsy 去掉分类损失后指标变化较小。

## 8. Contributions and Reproduction Value

1. 针对 point / contextual / collective anomaly 设计局部 perturbation family，并让 classifier 学扰动 class。（§3.3）
2. 将 classifier 的预测伪标签用于高维 projection space 中的 positive / negative sample selection，和 cross-entropy 联合训练。（§3.4, Eqs. 5–8）
3. 用 7 个原始 / augmentation embeddings 的平均 LOF 作为最终窗口分数。（§4.2, Eq. 9）
4. 在六个多元 / 传感器数据集上与 13 个模型比较，并有 t-SNE、mixed-anomaly visualization 和三项 ablation。（§4）

主要公式、扰动幅度、窗口选择、TCN 参数和指标均有说明，适合复现论文核心思路。论文正文未提供官方代码地址；需要自行核实 transform sampling、训练 test split、LOF 对七组 embeddings 的调用细节和 threshold 选择。最重要的 protocol caveat 是 test-best F1。（§§3–4）

## 9. Limitations and Critical Reading

- **扰动覆盖假设**：六种固定扰动 / 幅度不能覆盖所有领域异常。真实异常可能是缓慢状态转换、负载峰值、周期变化或跨通道依赖变化，而不一定降低扰动分类正确率。（§3.3）
- **Classifier pseudo-label coupling**：同一学习到的分类边界既提供伪标签，又组织 contrastive positives/negatives；如果分类器系统性混淆合法正常模式，contrastive network 可能放大误分结构。（Eq. 1, §§3.3–3.4，分析推断）
- **检测分数仍由 LOF 决定**：分类误差 / perturbation confusion 不是最终 anomaly score 的直接组成；最终 score 是七种 representation 的平均 LOF。（Eq. 9）
- **Threshold protocol**：best F1 通过遍历阈值取得，含测试标签 oracle 选择；不能将报告 F1 当作不依赖标签的线上告警结果。（§4.1）
- **事件结构**：subsequence score 被赋给窗口末端，前 $l-1$ 时点补零；窗口 length / stride 会影响边界和检测延迟。（§3.1, §4.1）
- **外部上下文缺失**：输入为数值时序窗口，未使用 workload、release、Trace 或正常业务状态标签，无法解释偏离来自新正常还是故障。
- **复现透明度**：论文正文没有代码链接；已给定配置之外的 transform 随机参数、LOF 配置等仍需从 implementation / supplementary source 获取。

## 10. Related Papers

- **TriAD**：都将 augmentation 看作异常线索；TriAD 用 augmented view 作为同域负例，且用三域相似度提名异常窗口 + MERLIN；PCRTA 用 perturbation classifier pseudo-label 组织 positives/negatives，最后由 LOF 聚合多-view score。
- **CAPMix**：都构造合成异常；CAPMix 用形状特征与伪异常训练决策边界，PCRTA 用离散 perturbation class 改善表征近邻结构。扰动语义 / threat model 不同。
- **TFMAE**：同属 self-supervised multi-view；TFMAE 依赖 temporal/frequency mask discrepancy，PCRTA 依赖 augmentation type classification 与 LOF。
- **Quo Vadis / TSB-AD**：都提醒 test-best F1 与 point-adjusted scores 会夸大可部署结论；PCRTA 的 best-F1 threshold 需要按此理解。

## 11. Questions for Further Reading

1. perturbation classifier 的混淆是否能在真实异常与合法业务峰值间保持区分？不同操作系统 / workload 的 transfer 结果如何？
2. 只用 anomaly-like transforms 作 negatives，是否导致异常型训练样本与正常稀有模式被错误分离？
3. pseudo-label 的置信度、不同 classifier seed 与 top-$k$ 对最终 LOF 排名的影响有多大？
4. 固定 threshold calibration 与 event-level metrics 下，平均七个 LOF view 是否仍优于原始 embedding？
5. 多变量依赖型故障若各通道 marginal perturbation 都看似正常，模型能否发现？
6. 工作负载 / release / Trace condition 能否帮助选择合适 perturbation family，避免正常状态改变被当作负样本？

## 12. Key Terms

- **Perturbation classifier**：对原始 / 手工增强窗口进行多分类的网络，输出 augmentation type predictions。
- **Pseudo-label-guided contrastive learning**：以 classifier 预测类别组织同类 top-$k$ positive 和异类 negative representation。
- **Collective anomaly**：多个连续时间点或多个维度共同异常的片段型变化。
- **LOF score**：以局部邻居密度偏低表示 embedding 离群；此处对原始及 6 种 perturbed views 求均值。

## 13. Tags

`TSAD` `perturbation` `contrastive learning` `pseudo-labels` `TCN` `LOF` `multi-view` `best-F1 threshold`
