# Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution

## 1. Metadata

- **Authors**: Yuting Sun, Guansong Pang, Guanhua Ye, Tong Chen, Xia Hu, Hongzhi Yin
- **Year / Venue**: 2024 / ICDE（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/ICDE/Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf)
- **DOI**: [10.1109/ICDE60146.2024.00080](https://doi.org/10.1109/icde60146.2024.00080)
- **Code**: [TriAD repository](https://github.com/pseudo-Skye/TriAD)（PDF p.1）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

TriAD 为单变量测试序列分别提取 temporal、Fourier amplitude/phase/power 和 detrended residual 表示，用 jittering / magnitude-warping 片段构造合成异常并进行域内 / 域间 contrastive representation learning；推理时先从每域找最异常窗口，再与正常训练窗比较选出候选区域，最后调用 MERLIN 搜索不同长度的 discord 并把窗口 / discord 命中投票成点分数。（§III, Eqs. 1–10, PDF pp.3–7）

## 3. Background and Problem Definition

论文讨论两个问题。其一，传统时序 augmentation（jittering、scaling、crop 等）未必保持正常模式，增强结果本身可能像异常；若简单把原样本与增强样本当作正对，会把异常样式拉近正常表征。其二，重建模型能学会连续异常片段，导致异常也被良好重建；discord discovery 可覆盖不同 anomaly length，但全序列多长度搜索成本高。（§I, pp.1–3）

作者将周期序列写成 Fourier 周期项与非周期残差之和（Eq. 1, p.3），并按 seasonality、shapelet 和 residual 讨论不同异常形态。定义中异常可表现为这些成分与预期 normal behavior 的相似度越过阈值；这是问题动机，不意味着算法获得真实业务上下文或已知的周期标签。（§II-A）

TriAD 的应用假设尤其重要：其 UCR Archive 中每个 test series 有一个 anomaly event，模型为每一条数据集单独训练 / 使用；推理阶段也将每域最异常窗口数设为 $Z=1$。因此任务不是任意多事件的持续流式检测。（§IV-A, PDF pp.7–8）

## 4. Core Challenges

1. **augmentation 可能模拟异常而非不变视图**：异常检测的 representation learning 不应无条件将每个增强视作正例。（§I, §III-A）
2. **异常长度与形状跨度很大**：单一窗口 residual 可能漏掉连续异常；全序列 discord search 虽可变长，但耗时。（§I, §III-D）
3. **一元波形异常可落在不同统计域**：有些变化主要是频率 / 周期变化，有些表现为残差或局部时域变化。（§II-A, §III-B）
4. **基准 / 指标会放大方法优势**：PA 对区间内单点命中整段回填，random score 也可能得到高 PA-F1；需同时审视数据质量、PA%K 与事件距离指标。（§II-B, pp.3–4）

## 5. Architecture Overview

```text
训练时：正常训练窗口 X_i,L
  ├─ 取 temporal raw、频域 amplitude/phase/power、周期趋势去除后的 residual
  ├─ 对窗口随机选一小段做 jittering 或 magnitude warping → synthetic perturbed views X'_i,L
  ├─ 三个 domain encoder：dilated residual CNN → dense projection → r_i,d ∈ R^L
  └─ L_total = α L_inter + (1−α) L_intra

推理时：测试序列分窗
  ├─ 每个域按窗口间 embedding dissimilarity 各提名 top-1（最多三个候选）
  ├─ 与正常训练窗口比对，选最不相似候选窗
  ├─ 在该窗附近执行多长度 MERLIN discord search
  └─ 候选窗 + 被 discord 命中的区间累加 votes，按正票均值 threshold 输出点标签
```

（Fig. 4, §§III–IV, Eqs. 3–10, pp.4–8）

## 6. Method in Detail

### 6.1 片段级合成扰动

把训练序列切成长度 $L$ 的滑动窗口 $X_{i,L}$，再随机选择位置、长度和形状，用两类已有 augmentation 模拟异常型扭曲：

- **Jittering**：向窗口中的随机局部片段各时间点加随机噪声 $\epsilon$（Eq. 3）。
- **Magnitude warping**：用 Butterworth filter 产生平滑幅度变化（Eq. 4），再将变换片段嵌回原 window。

作者的区别在于：这些局部变换不被视作保持正常语义的正样本，而是训练阶段的 potential-anomaly negatives。窗口内扰动减少了整序列 augmentation 把所有上下文同时改变的问题。（§III-A, Fig. 5, pp.4–5）

### 6.2 三个表征域

1. **Temporal domain**：直接以原始窗口作单通道输入，保留时间形状。
2. **Frequency domain**：对窗口作 DFT，按每个频率保留 amplitude、phase 和 power 三类 feature，合为三通道输入（Definition 2, Table I）。
3. **Residual domain**：去除底层周期 / seasonal trend 后的残差作为单通道输入，强调非周期偏移。（§III-B, pp.3, 5）

三域各自过专用的 dilated CNN residual encoder：每个 residual block 有两层 same-padded convolution，block 间 dilation rate 递增（翻倍）以扩展感受野；之后经共享 dense layers 将 $h\in\mathbb R^{L\times h_d}$ 压成时序 embedding $r\in\mathbb R^L$。temporal/residual encoder 输入一通道，frequency encoder 输入三通道。（§III-B, pp.5–6）

主文描述 residual 为“去除底层周期趋势”，但方法段没有把趋势估计器、拟合窗口和超参数说到与 Fourier feature 同等可直接复现的程度；复现时应核对官方实现中的精确预处理。（§III-B）

### 6.3 Domain 内 contrastive loss

对同一 domain $d$，原始未增强窗口 representation $r_{i,d}$ 与 batch 内其他原始窗口 representation 组成 normal positive candidates；perturbed representations $r'_{j,d}$ 作为 negatives。式 (5) 用点积指数相似度计算 positive numerator 与 augmented-negative denominator：

$$\ell_{intra}^{(i,d)}=-\log\frac{\mathrm{sim}(r_{i,d},r^+_{i,d})}{\mathrm{sim}(r_{i,d},r^+_{i,d})+\sum_{j\in B}\exp(r_{i,d}^{\top}r'_{j,d})}. \tag{5}$$

目标是让未经扰动训练窗口共享的模式更紧密，同时使扰动窗口的表示远离原始窗口。其核心前提是 perturbation 能覆盖若干真实异常特征；若变换不符合领域异常或正常模式也容易被变换，positive/negative 语义就会变弱。（§III-C.1, Eq. 5, p.6）

### 6.4 Domain 间 contrastive loss与总目标

仅用**未增强原始窗口**做 inter-domain contrast：same-domain representation 保留为 positive，其他 domain 的同一窗口表示作为 negatives，鼓励表示学习保留各域特有模式，降低三个域塌缩为相同 trivial feature 的风险（Eq. 6）。

$$\ell_{total}^{(i,d)}=\alpha\ell_{inter}^{(i,d)}+(1-\alpha)\ell_{intra}^{(i,d)}. \tag{7}$$

作者使用 $\alpha=0.4$，即 domain-level contrast 与域内 contrast 平衡。实验 ablation 发现 intra-domain 项贡献更大，说明 synthetic augmentation / hard-negative 作用在该 benchmark 上更明显。（§III-C, §IV-D, Eq. 7, Figs. 8–9）

### 6.5 窗口筛选、discord search 与 anomaly votes

推理先按周期长度分窗，计算每个域内窗口表示之间的 similarity；每个域各选相似度最异常的 top $Z$ 窗，设 $Z=1$，因此候选最多三个。由于每域的异常响应不同，某异常可能只在频域或 residual 域显著。之后将三个候选窗分别与正常训练序列中对应长度的滑窗比较，保留与训练 normal windows 差异最大的一个。（§III-D.1）

对选出的窗在附近做可变长度的 MERLIN discord discovery，不再扫描全 test series。每个点 $x_n$ 获得：若落在候选窗内，加一票 $s_{TriAD}(x_n)=1[x_n\in X_{t,L}]$；每当落入一个被 MERLIN 标出的长度候选 discord，再加一票 $s_{dd}(x_n)=\sum_l1[x_n\in\hat X_{t,dd,l}]$。总分为 $s=s_{TriAD}+s_{dd}$（Eq. 8）。论文的简单阈值取有至少一票点的平均 vote；作者展示阈值提高至 vote 的 90th percentile 会提高 precision。（§III-D.2–3, Eq. 8, pp.6–7; Fig. 13）

这里有两个设计约束：test series 假定单个 event；一个候选 window 可能覆盖远多于实际异常的上下文，而两个 vote 未作 normalization / 权重标定。作者明确把更好的 normalization / weight 作为 future work。（§III-D.3, p.7）

## 7. Experimental Design and Evidence

### 7.1 Datasets, baselines, metrics

- **数据**：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7）
- **训练设置**：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；6 residual blocks、$h_d=32$、$\alpha=.4$。（§IV-A, pp.7–8）
- **Deep baselines**：random / trained LSTM-AE、USAD、TS2Vec、Anomaly Transformer、MTGFlow、DCdetector；另与 MERLIN++ 做事件检出与效率比较。（§IV-B, pp.8–9）
- **指标**：point-wise F1、PA-F1、PA%K-F1（对 $K=1\ldots100$ 的曲线面积）、Affiliation event precision/recall/F1；正文说明在统一预测输入上先移除既有 PA，再计算优化后的指标。（§IV-B.1, pp.8–9）

### 7.2 主结果和 MERLIN 比较

- **250 UCR series**：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。
- **MERLIN++**：只在按长度排序后的 62 个最短 UCR datasets 比较，MERLIN++ 29/62 检出，accuracy .424、14.5 min；TriAD tri-window .681、0.99 min，single-window .623、1.01 min（Table IV, p.9）。这是与该实验设定下结果的比较，不代表所有长度、硬件或 discord implementation 的固定加速比。
- TriAD 提供的 search window 平均约是 MERLIN 全序列搜索区域的 1/20（Fig. 7），以先缩小候选区再多长度搜索来降低成本。（§IV-B.2, pp.9–10）

### 7.3 Ablation、参数与 case studies

- **Ablation**：temporal / general encoder 与 frequency encoder重要，residual encoder较弱；intra-domain contrastive learning 通常比 inter-domain 更关键（Fig. 9, p.10）。这只说明当前 UCR 异常类型与扰动设定中的贡献次序。
- **参数敏感度**：6 CNN blocks 略优，$h_d=32$ 更适合，过大 embedding 有过拟合迹象；$\alpha$ 需平衡两项损失（Fig. 8, p.10）。
- **UCR 025 case**：27-point 的微妙异常缺失正常波形的次峰；TriAD 的频率和 residual 表示都把第 39 窗标为最不相似，之后 MERLIN 的不同长度 search 集中在实际异常附近。（Figs. 10–12, pp.10–11）
- **多类异常可视化**：Fig. 16 展示 noise-like、duration、seasonal、trend、level-shift、contextual anomalies，报告长度约 20–200 points 的案例；属于精选可视化，不等于每类都有单独受控鲁棒性结果。（§IV-F, pp.11–12）
- **Discord failure case**：若候选窗里异常数据占多数，discord 算法可能把正常重复模式认作异常，漏掉异常；实现加 fallback：若没有找到 discord，则将 TriAD 指定窗口所有点标异常。（§IV-G, p.11）

## 8. Contributions and Reproduction Value

1. 把时域、频域 amplitude/phase/power 与 periodic-trend residual 合并到三路 representation，支持不同异常形态。（§III-B）
2. 将 augmentation 看作潜在异常 negative，并以 intra-domain / inter-domain loss 组合构造 self-supervised embedding。（§III-A, C）
3. 将窗口级 representation discrepancy 用作候选定位，再让 MERLIN 只在候选邻域做可变长度 discord search，降低搜索范围。（§III-D; §IV-B.2）
4. 在 250 个 UCR 单事件数据上使用 PA%K 与 affiliation，并以 5 seeds 报告 Deep model 比较，回应传统 PA 评价争议。（§IV）

官方代码公开（PDF p.1），窗口、训练轮次、batch、学习率、alpha 与 CNN 深度均有说明。复现还要核对周期估计 / residual extraction、MERLIN 搜索长度和 padding、vote threshold 与各指标实现；主流程利用“每个 test set 只有一个异常事件”的数据假设。（§IV-A; repo）

## 9. Limitations and Critical Reading

- **单 event 假设**：候选数 $Z=1$、每域 top-1、最后只选一个 window，难以直接支持多个事件、持续异常或异常与状态变化同时出现。（§III-D; §IV-A）
- **residual 细节不足**：正文称移除 periodic trend，复现需核对官方实现确定周期估计和 residual calculation；这也意味着 residual branch 的技术先验并非完全由主文刻画。（§III-B）
- **test-time candidate ranks**：与同一 test set 的窗口互相比，默认 test series 有一个离群 event；如果整段运行状态变化或多窗口异常，这个相对离群分布会改变。（§III-D）
- **投票阈值未成为线上 operating point**：论文给出平均正票与 threshold sensitivity，但指标汇总对 PA%K 做 $K$ 曲线面积并用 event metric；没有提供跨状态固定 false-alert budget 下的完整流式延迟结果。（§III-D; §IV-B）
- **benchmark 语义**：UCR 覆盖多领域单变量序列，未使用多变量 topology、workload、release 或 Trace。其多域波形线索不解释波动成因。
- **人工阈值 / assumption**：主要 F1 与按单异常设定的窗口候选相互关联；真实系统若允许多 event 或异常率未知，需要重新评估候选提名和阈值。（§IV）
- 作者指出 vote score 可进一步加入 normalization / weighting；discord search 也会遇到异常区间压过正常区间的失败情景。（§III-D.3, §IV-G）

## 10. Related Papers

- **TFMAE**：同样用 temporal/frequency views；TFMAE 比较同一序列两种 mask views 的逐点 KL，而 TriAD 以 embedding 窗口的跨域/域内对比提名全序列的异常候选窗，再做 discord search。
- **TFC**：temporal-frequency-curvature 多路得分；TriAD 的第三域是去季节 residual，且依赖 UCR 单事件 + MERLIN 定位。
- **Perturbation Guiding / PCRTA**：都把 perturbation 用作潜在异常知识；TriAD 把增强当对比负例，PCRTA 学扰动类别并以其伪标签选正负样本。
- **Quo Vadis / TSB-AD**：基准与评价问题相同；TriAD 对 PA-F1 的批判与 PA%K / affiliation 改造需同这两篇一起读。
- **Sub-Adjacent Transformer**：都用局部窗口异常线索，TriAD 先候选窗+多长度 discord，Sub-Adjacent 强制模型不能用紧邻点重建目标。

## 11. Questions for Further Reading

1. TriAD 是否能扩展为一个 test series 多事件、多状态变更及连续流式预测，而不用提前设 $Z=1$？
2. 周期估计误差会怎样改变频域 / residual branch 的窗口 ranking？三域对不同采样率是否稳定？
3. synthetic jitter / warping 哪些情况下代表真实异常，哪些会把合法正常波动当作 negative？
4. 一个 window-level vote 是否覆盖事件边界过多？如何定义业务成本与 normalization / weighting？
5. TriAD 的 window similarity / discord 候选能否解释由负载、业务阶段或故障传播造成的变化来源？
6. 250 个单事件 UCR 数据上的 detector ranking 是否在多变量工业指标与多事件标签上成立？

## 12. Key Terms

- **Tri-domain representation**：temporal raw、频域特征和 periodic-trend residual 三路表示。
- **Intra-domain contrast**：以原始窗口为正候选、局部增强窗口为负例的同域对比。
- **Inter-domain contrast**：保留域内相似、推远跨域 representation 的对比项。
- **Discord discovery**：寻找与自身近邻形态距离最大的可变长度子序列，作为异常候选。
- **PA%K**：在点级 F1 与 point adjustment 间按覆盖比例 $K$ 做评估曲线的汇总，降低直接区间回填的强度。

## 13. Tags

`TSAD` `self-supervised learning` `tri-domain` `frequency domain` `contrastive learning` `discord discovery` `PA%K` `UCR`
