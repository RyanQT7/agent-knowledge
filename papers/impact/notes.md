# IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection

## 1. Metadata

- **Authors**: Xiaohui Zhou, Yijie Wang, Hongzuo Xu, Weixuan Liang, Xiaoli Li, Guansong Pang
- **Year / Venue**: 2026 / ICML（CCF A，依已人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2026/ICML/IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf)
- **Proceedings**: [PMLR 306 paper page](https://proceedings.mlr.press/v306/zhou26as.html)
- **Code**: [IMPACT repository](https://github.com/mala-lab/IMPACT)（PDF p.1）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

IMPACT 面向带少量 seen anomaly labels、且 unlabeled normal training pool 可能污染的 open-set TSAD：以 validation-risk influence 找出有害训练样本并翻转其标签，再把最不利于降低 risk 的边界 normal embedding 沿 influence 方向扰动为 unseen pseudo anomalies，最后联合 seen / unseen heads、reference-feature distance 与 multi-channel deviation score 检测。（§§3–4, Eqs. 1–21, pp.3–6）

## 3. Background and Problem Definition

作者讨论的不是纯 zero-shot 或完全无标签 TSAD。训练集合 $D=D_n\cup D_a$，其中 $D_a$ 是少量已标记 seen anomaly，$D_n$ 被当成 normal 但允许含少量误标的真实 anomaly contamination。测试时既可能出现已见 anomaly，也要检测未见 anomaly class。实际设置的重要约束是：已有少量异常标记可利用，但未标记训练池不保证干净。（§3, p.3）

论文指出现有 open-set anomaly detection 常把余下训练数据默认作 normal，污染会把异常规律学成正常；同时，伪异常生成多来自 image augmentation 或手工 time-series transformations，不能确保产生符合时序结构且覆盖未见类的 pattern。（§1–2, pp.1–3）

## 4. Core Challenges

1. **Unlabeled pool contamination**：少量未识别 anomaly 以 normal label 参与有监督学习，会把决策边界推向错误方向。（§1）
2. **seen anomaly few-shot 过拟合**：有限异常标签提供先验但种类少，模型容易围绕 seen classes 学边界，难泛化 unseen classes。（§1–3）
3. **伪异常是否有用难保证**：固定 jitter、mixup、segment swapping 等规则可能制造不自然或仍靠近已知 pattern 的特征。（§2）
4. **训练样本影响方向不均等**：有些被视为 normal 的样本提高验证 risk，有些稀有或形态多样的 normal 反而是重要参照，需区别 harmful contamination 与 helpful normality。（§3.1）
5. **开集评估需区分 seen / unseen**：仅报告混合测试集总分会掩盖模型是识别了已知异常还是泛化到未知类别。（§4, Appendix H.1）

## 5. Architecture Overview

```text
输入：少量 labeled seen anomalies + nominally-normal pool D_n（含污染）+ validation set V
  Phase I / initial multi-channel deviation model
    → TCN feature extractor φ + multi-channel head h
    → influence of each sample on V risk (TIS)
  Phase II / RADG
    ├─ I_L(z_i)>0: 候选 contamination，label 0→1
    ├─ I_L(z_i)<0: 保留有帮助的 clean normals / reference D_ref
    └─ 取最不利于 risk 降低的 k 个正常点，feature 沿 I_per^T 扰动并标为 unseen anomaly
  Phase III / retraining
    → shared feature + seen head h + unseen head h'
Inference: multi-channel max abnormality + distance-to-normal-reference
```

（Fig. 2, §§3.1–3.3, pp.3–6; Algorithm 1, Appendix G, p.19）

## 6. Method in Detail

### 6.1 TIS 的 multi-channel deviation loss

初始模型为 feature extractor $\phi(x;\theta_\phi)$ 与 $r$ 通道学习头 $h(\phi;\theta_h)$。multi-channel 输出向量相对各向同性 Gaussian normal-score prior 的 deviation 写为：

$$\operatorname{dev}(x_i)=\sqrt{(f(x_i,\theta)-\mu_r)^\top\Sigma_r^{-1}(f(x_i,\theta)-\mu_r)}. \tag{1}$$

normal 样本的各通道 score 被拉向 normal reference $\mu_r$；anomaly 则需离开该参考至少 margin $a$。论文定义逐通道 deviation loss：

$$\mathcal L(z_i,\theta)=\frac1r\sum_{j=1}^{r}\left[(1-y_i)\operatorname{dev}(x_i)_j+y_i\max(0,a-\operatorname{dev}(x_i)_j)\right]. \tag{2}$$

作者用多视角 / 多通道几何解释：normal 应在所有维度贴近参考，anomaly 只要有某视角偏离就可能突出。Theorem 1 说明在 score latent distribution 假设 $S\sim\mathcal N(\mu,\sigma^2 I)$ 下，熵 $H(S)=\frac r2[1+\log(2\pi\sigma^2)]\propto\log\sigma^2$，并将向 isotropic Gaussian prior 靠近解释为 normal latent score 的 entropy / variance 收缩。（§3.1, Eqs. 1–3, p.4; Appendix A）

### 6.2 Influence function 与 contamination 识别

对训练样本 $z_i$ 权重做 infinitesimal perturbation $\epsilon_i$，最优参数的一阶变化为：

$$I_\theta(z_i)=-H_{\hat\theta}^{-1}\nabla_\theta\mathcal L(z_i,\hat\theta),\quad H_{\hat\theta}=\frac1N\sum_n\nabla^2_\theta\mathcal L(z_n,\hat\theta). \tag{4}$$

它在 validation point $z_t$ 上产生的 loss change 为：

$$I_L(z_i,z_t)=-\nabla_\theta\mathcal L(z_t,\hat\theta)^\top H^{-1}_{\hat\theta}\nabla_\theta\mathcal L(z_i,\hat\theta), \tag{5}$$

再对 validation set $V$ 聚合 $I_L(z_i)=\sum_{z_t\in V}I_L(z_i,z_t)$（Eqs. 6–7）。若 $I_L(z_i)>0$，减轻 / 移除样本会降低 validation risk，故把 $D_n$ 中此样本选入 suspected contaminated set $D_{con}$；若 $I_L(z_i)<0$，保留为有益 normal 候选。最小 influence 的 $k$ 个样本作为 helpful normal reference $D_{ref}$；剩余形成 clean set。（§3.1, pp.4–5）

实际实现用对角 empirical Fisher 近似 Hessian inversion（Eq. 8 / implementation details），降低二阶计算负担，但也令 influence direction 依赖该近似、初始模型和 validation loss。作者理论以一阶 influence estimate 论证风险方向，不等于对有限次参数更新的精确保证。（§3.1; Appendix F–G；后句为方法边界分析）

### 6.3 RADG：污染 label flip

对疑似 contamination $z_i=(x_i,0)$ 改为 $z_i^1=(x_i,1)$。作者分析 label perturbation 对参数 / validation loss 的影响（Eqs. 8–12），在简化单通道 loss 且 $\mu=0,\Sigma=I$ 条件下得到翻转后 risk 近似变化：

$$\mathcal L(V,\hat\theta^{\epsilon_1})-\mathcal L(V,\hat\theta)\approx-\frac{2}{N|D_{con}|}\sum_{z_i\in D_{con}}I_L(z_i)<0. \tag{13}$$

因此论文把误标异常从“有害 normal data”改造成额外的 supervised anomaly examples $D'_{con}$。理论结论依赖影响分数正确识别污染、损失局部线性近似等前提；若正常稀有群体也有正 influence，则它也可能被翻成 anomaly。（§3.2, pp.5; Appendix B）

### 6.4 RADG：risk-guided unseen pseudo anomaly

对 clean normal 中仍有负 influence 的样本，选择 influence 值最大的前 $k$ 个 $D_{per}$（这些分数虽为负，但对降低 risk 帮助最少），假设它们接近 normal/anomaly boundary、较易偏移。设 $\phi_i=\phi(x_i)$，作者对 feature perturbation $\zeta_i$ 的测试风险影响写为 Eqs. 14–15，并按能最大提高 validation risk 的方向构造：

$$\phi_i^{\zeta}=\phi_i+\alpha I_{per}(w_i)^\top,\qquad (\phi_i^{\zeta},1)\in W'_{per}. \tag{15–16}$$

$\alpha>0$ 为扰动强度。作者的 Theorem 3 试图说明该扰动产生与原 normal feature distribution 有差异的分布；Theorem 4 给出引入这些 pseudo labels 后 validation risk 一阶近似下降：

$$\Delta \mathcal L_V\approx-\frac{\alpha}{N|W_{per}|}\sum_{w_i\in W_{per}}\|I_{per}(w_i)\|_2^2<0. \tag{16}$$

需注意这里产生的是 feature-space pseudo anomaly，而非对原始 waveform 生成可直接解释的时间域 anomaly。它是否对应真实可发生的时间形态，主要由 held-out anomaly experiment 间接验证。（§3.2, pp.5–6; Appendix C–D）

### 6.5 Seen / unseen learning 与 inference score

主训练集合并 label-flipped samples、normal reference 与其余 clean data，优化 seen abnormality loss $L_{seen}$。另一个 unseen head $h'$ 在 helpful normal 集合及 $W'_{per}$ 上优化 $L_{unseen}$：

$$\mathcal L_{re}=\mathcal L_{seen}+\lambda\mathcal L_{unseen}. \tag{19}$$

推理时将 seen / unseen heads 的 multi-channel 输出按通道组合后取最大，得到 $s_m$；再计算当前 feature 与 $D_{ref}$ 平均 normal feature 的 L2 distance $s_f$，最终 anomaly score $s=s_m+s_f$（Eqs. 20–21）。于是预测同时编码监督 head 的 seen / unseen abnormality 与 reference-normal feature deviation。（§3.3, p.6）

### 6.6 训练协议和实现

训练初始阶段先在含少量 contaminated nominal pool 与 labeled anomaly 的数据上拟合；算法对 mini-batch 的 $D_n$ 计算 influence、label flip 正 influence 样本，并按负 influence 排序选 $D_{ref}$ / $D_{per}$，生成 feature pseudo anomaly 后重训（Algorithm 1, p.19）。实现使用一层 TCN feature extractor、两层 ReLU MLP heads，默认隐藏和 feature dimension 64；$k=5$、$\alpha=0.02$、$\lambda=1$。总计 10 epochs：初始 / 主训练 9 epoch，重训 1 epoch；batch 64、learning rate $3\times10^{-4}$。作者从 training set 随机抽 20% 作 validation 来估计 sample influence。（Appendix E–G, pp.17–19）

## 7. Experimental Design and Evidence

### 7.1 Datasets / protocols / baselines

8 个 benchmark：单一 anomaly class 的 UCR、ASD、PSM、SMD；含多 anomaly classes 的 character trajectory CT、spoken Arabic digits SAD、PTB-XL ECG、TUSZ EEG。每个时间区间作为一个 sample；附录列出 interval 长度分别为 93–1,000、维数为 1–38。数据覆盖 UCR 异质单变量、服务 / cluster telemetry、语音与医疗波形。（§3, §4.1; Appendix E, pp.17–18）

两类主 setting：unsupervised baseline 只看 nominal training；open-set general protocol 从可用 anomaly classes 随机抽 labeled examples；hard setting 对多类数据只以一个 anomaly class 的标签训练，测试时需泛化到其余 unseen classes。两个 open-set setting 默认每个用于监督的类别只用 10 个 anomaly examples。训练数据额外注入 2% test anomalies 作为 contamination；这些污染样本从最终 test set 排除，以避免 train-test leakage。作者用 AUC、五次独立运行报告 mean ± std。（§4.1; Appendix E）

Open-set comparison 包含 DevNet、DSAD、NCAD、DRA、MOSAD、InvAD、WSAD-DT；unsupervised 有 TCN-AE、THOC、TranAD、DCdetector、GPT4TS、COUTA、DADA。（§4.1）

### 7.2 主结果

Table 1 general setting 下 IMPACT 八数据集 AUC：UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91（%）。作者报告相对竞争方法 6.37%–44.52% 的平均提升。（Table 1, p.7）

Hard setting Table 2 的四组 mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。作者报告平均较七个 competitor 高 10.52%–42.83%。在见过的异常类之外，对每个 unseen class 的分析也显示较平衡表现；但 SOTA 优势的范围仍限于这些 benchmark、抽样协议与 AUC 指标。（Table 2, p.8; Appendix H.1）

### 7.3 组件 ablation

Table 3 支持多模块互补：

- 去掉 label-flipped $D'_{con}$ 后多数一般 / hard 结果下降，说明 contamination correction 对当前注入设置有贡献。
- 去掉 $L_{seen}$ 影响较大，例如 general TUSZ 从 82.91 降至 70.91；少量已知异常确实提供有效监督。
- 去掉 $L_{unseen}$ 在 hard TUSZ 从 75.70 降至 60.92，显示 unseen head / pseudo anomaly 对缺失异常类泛化尤为重要。
- 去掉 $s_f$ 也使若干 set 降低，说明参考特征距离提供补充分数。
- 随机选 reference、随机 flip label、随机 Gaussian feature noise 均弱于 influence-guided 设计；hard TUSZ 随机 feature perturbation 为 62.87。（Table 3, p.9）

敏感性实验中 $\lambda=1$、$k=5$ 是论文默认选择；增加 $k$ 过多可将原本属于 normal distribution 的形态人为伪装为 anomaly，引入偏差。（§4.4, p.9, Fig. 3）

### 7.4 鲁棒性、生成质量与其它指标

- 在 2%–10% contamination rate 的敏感性图中，IMPACT 随污染增加表现相对稳定；ASD、SMD 某些点随污染率升高反而改善，作者将其解释为把污染改造成额外异常监督。该实验污染来源为测试 anomaly 且从最终测试剔除。（Appendix H.3, pp.20–22）
- 与 COE、WMix、COE-WMix、CutAddPaste 替换比较时，IMPACT hard setting 较稳定；feature distribution KLD 报告比基线 augmentation 平均低 64.13%（范围 0.03–0.32 vs. 0.15–1.53），并展示 t-SNE。KLD / t-SNE 仅说明该协议下合成 feature 与 unseen feature 分布较接近，不证明生成时序可解释或因果真实。（Appendix H.4, pp.22–24）
- 多通道数敏感性显示 3–5 channels 通常兼顾信息量和抗噪；通道过多可降低表现。（Appendix H.6, p.25）
- 额外 point-level evaluation 在 UCR / ASD / PSM / SMD 将测试序列以 stride 1 滑窗切成连续 intervals，再把每窗分数赋到其末端时间点；报告 Affiliation-F1 与 VUS-ROC。IMPACT 对 Affiliation-F1 在前三个数据集第一、PSM 第二，对 VUS-ROC 四集第一。（Appendix H.7, p.26）
- 作者给 influence computation 的复杂度论断 $O(MP)$（$M$ nominal samples，$P$ parameters），并以合成规模对比报告近似随样本量线性增长；实际开销仍依赖参数维度、Hessian/Fisher 近似和实现。（Appendix H.8, pp.26–28）

## 8. Technical Contribution and Limitations

### 技术贡献

1. 把 influence analysis 合并用于污染检测 / label flipping 与 unseen pseudo anomaly generation。（§3）
2. 用 multi-channel deviation loss 及验证风险方向选择样本，而非只按 training loss 或手写 augmentation 决定哪些样本污染 / 如何注入。（§3.1–3.2）
3. 以 seen / unseen 双 head + reference-feature distance 同时处理已见异常和潜在未见类别。（§3.3）
4. 在四个多类数据的 hard open-set 设置、多个污染率以及 augmentation alternatives 上提供拆分证据。（§4; Appendix H）

### 作者指出与分析的限制

- **作者指出的 group failure mode**：可能把与其它正常群体语义重叠少的 rare normal subpopulation 错认成异常；作者提出 future work 可引入 group-aware validation / subpopulation discovery。（Appendix I, p.28）
- **监督边界**：不是 unsupervised / label-free；训练依赖 labeled seen anomaly、validation loss 和小规模特定 benchmark 的异常类结构。验证集若没有可靠标签，影响方向是否可靠尚未解决。（§4.1; Appendix E）
- **label-flip 风险**：若 valid rare state 对 validation risk 有害，influence rule 也可能把它错误翻为 anomaly；需要检查 false-positive / group robustness，而不能将 influence sign 当无误 contamination oracle。（Appendix I; 分析推断）
- **pseudo anomaly realism**：扰动在 latent feature space，不还原为 waveform、业务事件或根因可解释注入；KLD / t-SNE 与 benchmark AUC 是有限旁证。（§3.2; Appendix H.4）
- **实验抽象**：将 test-set anomaly 子集搬入 train 作 2%–10% contamination、再从 test 剔除，有利于已知 anomaly distribution 的受控实验；生产里的未知污染生成机制未必相同。（Appendix E、H.3；分析推断）
- **操作指标**：主表 AUC 不对应某个运行阈值或固定 false-alarm budget；主文没有系统报告在线告警延迟与每样本计算预算。（§4.1；分析边界）
- **情境范围**：虽然 ASD / PSM / SMD 是服务 telemetry，IMPACT 输入是窗口内时间序列特征与标签，不使用 workload / release / Trace / service graph context；尚未检验正常负载切换与真实故障并发。（数据 / 方法设置；分析推断）

## 9. Reproduction and Reuse Value

论文提供 [IMPACT code](https://github.com/mala-lab/IMPACT)，并在 Appendix E–H 描述八数据集、2% contamination、每类十个标注、TCN/MLP 架构、训练设置、不同 seen / unseen 划分和污染率。复现时要保留训练 contamination 来源从测试集取样但排除最终 test 的控制、20% validation 的使用方式、hard/general class protocol、每轮五次 seeds 和 AUC 计算，不能与常见无污染 open-set 设置直接混合。务必再单独检查 validation labels 的可获得性、rare-normal 错误翻转以及 Hessian approximation 对排序的影响。本次没有运行代码或复现实验。

## 10. Related Work

- **TimeRCD**：纯 synthetic pretraining、zero-shot context-relative normality；IMPACT 依赖 few-shot seen anomalies 与 validation-risk influence，是 supervised open-set 路线。
- **CAPMix / When Model Meets New Normals**：关注 KPI 噪声 / dynamic normality 与新正常状态；IMPACT 识别的是 validation-risk harmful data，不含业务状态语义。
- **DRA / MOSAD / InvAD / WSAD-DT**：open-set anomaly baselines；IMPACT 的核心差异是 influence 同时作 decontamination 与伪异常指导。
- **Fortifying Time Series**：robustness focus 在输入扰动与认证；IMPACT 的 robustness focus 是训练集污染和未见类别，需要区分输入 adversarial robustness 与 label contamination。
- **AnomSeer / PCRTA**：都通过辅助构造信号改善异常泛化；IMPACT 生成 feature-space pseudo anomaly，AnomSeer 对齐专家 trace，PCRTA 从扰动 views 学 contrastive representations。
