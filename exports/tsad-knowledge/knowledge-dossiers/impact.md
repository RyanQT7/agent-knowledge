# Knowledge Dossier — IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection

## 1. Basic Information

- **English title**: IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection
- **中文译名**：IMPACT：面向开放集时间序列异常检测的影响建模
- **Authors**: Xiaohui Zhou, Yijie Wang, Hongzuo Xu, Weixuan Liang, Xiaoli Li, Guansong Pang
- **Venue / year / CCF**: ICML 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/mala-lab/IMPACT
- **Research area**: 少量已知异常监督下的开放集污染鲁棒检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** Open-set supervised TSAD：有少量 labeled seen anomalies，nominal-normal training pool 含未标记 anomaly contamination，测试需识别 seen + unseen anomaly classes。（§3, p.3）
- **[实验支持]** 4 个单类与 4 个多类 benchmark，含 SMD / ASD / PSM telemetry、ECG、EEG；2% 主设置污染，另有 2%–10% 分析。（§4.1; Appendix E, H.3）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

作者讨论的不是纯 zero-shot 或完全无标签 TSAD。训练集合 $D=D_n\cup D_a$，其中 $D_a$ 是少量已标记 seen anomaly，$D_n$ 被当成 normal 但允许含少量误标的真实 anomaly contamination。测试时既可能出现已见 anomaly，也要检测未见 anomaly class。实际设置的重要约束是：已有少量异常标记可利用，但未标记训练池不保证干净。（§3, p.3）

论文指出现有 open-set anomaly detection 常把余下训练数据默认作 normal，污染会把异常规律学成正常；同时，伪异常生成多来自 image augmentation 或手工 time-series transformations，不能确保产生符合时序结构且覆盖未见类的 pattern。（§1–2, pp.1–3）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **Unlabeled pool contamination**：少量未识别 anomaly 以 normal label 参与有监督学习，会把决策边界推向错误方向。（§1）
2. **seen anomaly few-shot 过拟合**：有限异常标签提供先验但种类少，模型容易围绕 seen classes 学边界，难泛化 unseen classes。（§1–3）
3. **伪异常是否有用难保证**：固定 jitter、mixup、segment swapping 等规则可能制造不自然或仍靠近已知 pattern 的特征。（§2）
4. **训练样本影响方向不均等**：有些被视为 normal 的样本提高验证 risk，有些稀有或形态多样的 normal 反而是重要参照，需区别 harmful contamination 与 helpful normality。（§3.1）
5. **开集评估需区分 seen / unseen**：仅报告混合测试集总分会掩盖模型是识别了已知异常还是泛化到未知类别。（§4, Appendix H.1）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** Open-set baselines 常默认未标记池干净；固定 augmentation 不保证生成有用的 unseen anomaly。（§1–2）
- **[分析推断]** 需 validation labels / reliable risk estimate 的条件较强；valid rare subpopulation 也可能因组间差异而被错误剔除或翻标。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

IMPACT 面向带少量 seen anomaly labels、且 unlabeled normal training pool 可能污染的 open-set TSAD：以 validation-risk influence 找出有害训练样本并翻转其标签，再把最不利于降低 risk 的边界 normal embedding 沿 influence 方向扰动为 unseen pseudo anomalies，最后联合 seen / unseen heads、reference-feature distance 与 multi-channel deviation score 检测。（§§3–4, Eqs. 1–21, pp.3–6）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：Unlabeled pool contamination：少量未识别 anomaly 以 normal label 参与有监督学习，会把决策边界推向错误方向。（§1）
- **C2（第4节挑战）**：seen anomaly few-shot 过拟合：有限异常标签提供先验但种类少，模型容易围绕 seen classes 学边界，难泛化 unseen classes。（§1–3）
- **C3（第4节挑战）**：伪异常是否有用难保证：固定 jitter、mixup、segment swapping 等规则可能制造不自然或仍靠近已知 pattern 的特征。（§2）
- **C4（第4节挑战）**：训练样本影响方向不均等：有些被视为 normal 的样本提高验证 risk，有些稀有或形态多样的 normal 反而是重要参照，需区别 harmful contamination 与 helpful normality。（§3.1）
- **C5（第4节挑战）**：开集评估需区分 seen / unseen：仅报告混合测试集总分会掩盖模型是识别了已知异常还是泛化到未知类别。（§4, Appendix H.1）

### 7.1 TIS

- **作者技术描述**：**[作者主张] TIS**：multi-channel Gaussian deviation score / margin loss，使用 influence function 估算训练样本对 validation risk 的影响。（§3.1, Eqs. 1–7）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 TIS 的 multi-channel deviation loss”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 RADG decontamination

- **作者技术描述**：**[作者主张] RADG decontamination**：对 $I_L(z_i)>0$ 的 $D_n$ 样本做 0→1 label flip；作者给出一阶 risk 下降表达式。（§3.2, Eqs. 8–13）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 RADG：risk-guided unseen pseudo anomaly”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Feature-space pseudo anomaly

- **作者技术描述**：**[作者主张] Feature-space pseudo anomaly**：取最 less-helpful 的 k 个 normals，在 $I_{per}^\top$ 方向加扰动，并标为 unseen anomaly。（§3.2, Eqs. 14–16）
- **对应挑战**：C5、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 RADG：risk-guided unseen pseudo anomaly”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 双头训练与 score

- **作者技术描述**：**[作者主张] 双头训练与 score**：seen / unseen head 联合 loss，加 multi-channel max abnormality 与到 $D_{ref}$ 平均 embedding 的 L2 distance。（§3.3, Eqs. 17–21）
- **对应挑战**：C5、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.6 训练协议和实现”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 TIS 的 multi-channel deviation loss

初始模型为 feature extractor $\phi(x;\theta_\phi)$ 与 $r$ 通道学习头 $h(\phi;\theta_h)$。multi-channel 输出向量相对各向同性 Gaussian normal-score prior 的 deviation 写为：

$$\operatorname{dev}(x_i)=\sqrt{(f(x_i,\theta)-\mu_r)^\top\Sigma_r^{-1}(f(x_i,\theta)-\mu_r)}. \tag{1}$$

normal 样本的各通道 score 被拉向 normal reference $\mu_r$；anomaly 则需离开该参考至少 margin $a$。论文定义逐通道 deviation loss：

$$\mathcal L(z_i,\theta)=\frac1r\sum_{j=1}^{r}\left[(1-y_i)\operatorname{dev}(x_i)_j+y_i\max(0,a-\operatorname{dev}(x_i)_j)\right]. \tag{2}$$

作者用多视角 / 多通道几何解释：normal 应在所有维度贴近参考，anomaly 只要有某视角偏离就可能突出。Theorem 1 说明在 score latent distribution 假设 $S\sim\mathcal N(\mu,\sigma^2 I)$ 下，熵 $H(S)=\frac r2[1+\log(2\pi\sigma^2)]\propto\log\sigma^2$，并将向 isotropic Gaussian prior 靠近解释为 normal latent score 的 entropy / variance 收缩。（§3.1, Eqs. 1–3, p.4; Appendix A）

#### 6.2 Influence function 与 contamination 识别

对训练样本 $z_i$ 权重做 infinitesimal perturbation $\epsilon_i$，最优参数的一阶变化为：

$$I_\theta(z_i)=-H_{\hat\theta}^{-1}\nabla_\theta\mathcal L(z_i,\hat\theta),\quad H_{\hat\theta}=\frac1N\sum_n\nabla^2_\theta\mathcal L(z_n,\hat\theta). \tag{4}$$

它在 validation point $z_t$ 上产生的 loss change 为：

$$I_L(z_i,z_t)=-\nabla_\theta\mathcal L(z_t,\hat\theta)^\top H^{-1}_{\hat\theta}\nabla_\theta\mathcal L(z_i,\hat\theta), \tag{5}$$

再对 validation set $V$ 聚合 $I_L(z_i)=\sum_{z_t\in V}I_L(z_i,z_t)$（Eqs. 6–7）。若 $I_L(z_i)>0$，减轻 / 移除样本会降低 validation risk，故把 $D_n$ 中此样本选入 suspected contaminated set $D_{con}$；若 $I_L(z_i)<0$，保留为有益 normal 候选。最小 influence 的 $k$ 个样本作为 helpful normal reference $D_{ref}$；剩余形成 clean set。（§3.1, pp.4–5）

实际实现用对角 empirical Fisher 近似 Hessian inversion（Eq. 8 / implementation details），降低二阶计算负担，但也令 influence direction 依赖该近似、初始模型和 validation loss。作者理论以一阶 influence estimate 论证风险方向，不等于对有限次参数更新的精确保证。（§3.1; Appendix F–G；后句为方法边界分析）

#### 6.3 RADG：污染 label flip

对疑似 contamination $z_i=(x_i,0)$ 改为 $z_i^1=(x_i,1)$。作者分析 label perturbation 对参数 / validation loss 的影响（Eqs. 8–12），在简化单通道 loss 且 $\mu=0,\Sigma=I$ 条件下得到翻转后 risk 近似变化：

$$\mathcal L(V,\hat\theta^{\epsilon_1})-\mathcal L(V,\hat\theta)\approx-\frac{2}{N|D_{con}|}\sum_{z_i\in D_{con}}I_L(z_i)<0. \tag{13}$$

因此论文把误标异常从“有害 normal data”改造成额外的 supervised anomaly examples $D'_{con}$。理论结论依赖影响分数正确识别污染、损失局部线性近似等前提；若正常稀有群体也有正 influence，则它也可能被翻成 anomaly。（§3.2, pp.5; Appendix B）

#### 6.4 RADG：risk-guided unseen pseudo anomaly

对 clean normal 中仍有负 influence 的样本，选择 influence 值最大的前 $k$ 个 $D_{per}$（这些分数虽为负，但对降低 risk 帮助最少），假设它们接近 normal/anomaly boundary、较易偏移。设 $\phi_i=\phi(x_i)$，作者对 feature perturbation $\zeta_i$ 的测试风险影响写为 Eqs. 14–15，并按能最大提高 validation risk 的方向构造：

$$\phi_i^{\zeta}=\phi_i+\alpha I_{per}(w_i)^\top,\qquad (\phi_i^{\zeta},1)\in W'_{per}. \tag{15–16}$$

$\alpha>0$ 为扰动强度。作者的 Theorem 3 试图说明该扰动产生与原 normal feature distribution 有差异的分布；Theorem 4 给出引入这些 pseudo labels 后 validation risk 一阶近似下降：

$$\Delta \mathcal L_V\approx-\frac{\alpha}{N|W_{per}|}\sum_{w_i\in W_{per}}\|I_{per}(w_i)\|_2^2<0. \tag{16}$$

需注意这里产生的是 feature-space pseudo anomaly，而非对原始 waveform 生成可直接解释的时间域 anomaly。它是否对应真实可发生的时间形态，主要由 held-out anomaly experiment 间接验证。（§3.2, pp.5–6; Appendix C–D）

#### 6.5 Seen / unseen learning 与 inference score

主训练集合并 label-flipped samples、normal reference 与其余 clean data，优化 seen abnormality loss $L_{seen}$。另一个 unseen head $h'$ 在 helpful normal 集合及 $W'_{per}$ 上优化 $L_{unseen}$：

$$\mathcal L_{re}=\mathcal L_{seen}+\lambda\mathcal L_{unseen}. \tag{19}$$

推理时将 seen / unseen heads 的 multi-channel 输出按通道组合后取最大，得到 $s_m$；再计算当前 feature 与 $D_{ref}$ 平均 normal feature 的 L2 distance $s_f$，最终 anomaly score $s=s_m+s_f$（Eqs. 20–21）。于是预测同时编码监督 head 的 seen / unseen abnormality 与 reference-normal feature deviation。（§3.3, p.6）

#### 6.6 训练协议和实现

训练初始阶段先在含少量 contaminated nominal pool 与 labeled anomaly 的数据上拟合；算法对 mini-batch 的 $D_n$ 计算 influence、label flip 正 influence 样本，并按负 influence 排序选 $D_{ref}$ / $D_{per}$，生成 feature pseudo anomaly 后重训（Algorithm 1, p.19）。实现使用一层 TCN feature extractor、两层 ReLU MLP heads，默认隐藏和 feature dimension 64；$k=5$、$\alpha=0.02$、$\lambda=1$。总计 10 epochs：初始 / 主训练 9 epoch，重训 1 epoch；batch 64、learning rate $3\times10^{-4}$。作者从 training set 随机抽 20% 作 validation 来估计 sample influence。（Appendix E–G, pp.17–19）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (6)、Eq. (8)、Eq. (14)、Eq. (20)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.1 TIS 的 multi-channel deviation loss；6.6 训练协议和实现；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.5 Seen / unseen learning 与 inference score及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

IMPACT 面向带少量 seen anomaly labels、且 unlabeled normal training pool 可能污染的 open-set TSAD：以 validation-risk influence 找出有害训练样本并翻转其标签，再把最不利于降低 risk 的边界 normal embedding 沿 influence 方向扰动为 unseen pseudo anomalies，最后联合 seen / unseen heads、reference-feature distance 与 multi-channel deviation score 检测。（§§3–4, Eqs. 1–21, pp.3–6）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Datasets / protocols / baselines

8 个 benchmark：单一 anomaly class 的 UCR、ASD、PSM、SMD；含多 anomaly classes 的 character trajectory CT、spoken Arabic digits SAD、PTB-XL ECG、TUSZ EEG。每个时间区间作为一个 sample；附录列出 interval 长度分别为 93–1,000、维数为 1–38。数据覆盖 UCR 异质单变量、服务 / cluster telemetry、语音与医疗波形。（§3, §4.1; Appendix E, pp.17–18）

两类主 setting：unsupervised baseline 只看 nominal training；open-set general protocol 从可用 anomaly classes 随机抽 labeled examples；hard setting 对多类数据只以一个 anomaly class 的标签训练，测试时需泛化到其余 unseen classes。两个 open-set setting 默认每个用于监督的类别只用 10 个 anomaly examples。训练数据额外注入 2% test anomalies 作为 contamination；这些污染样本从最终 test set 排除，以避免 train-test leakage。作者用 AUC、五次独立运行报告 mean ± std。（§4.1; Appendix E）

Open-set comparison 包含 DevNet、DSAD、NCAD、DRA、MOSAD、InvAD、WSAD-DT；unsupervised 有 TCN-AE、THOC、TranAD、DCdetector、GPT4TS、COUTA、DADA。（§4.1）

#### 7.2 主结果

Table 1 general setting 下 IMPACT 八数据集 AUC：UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91（%）。作者报告相对竞争方法 6.37%–44.52% 的平均提升。（Table 1, p.7）

Hard setting Table 2 的四组 mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。作者报告平均较七个 competitor 高 10.52%–42.83%。在见过的异常类之外，对每个 unseen class 的分析也显示较平衡表现；但 SOTA 优势的范围仍限于这些 benchmark、抽样协议与 AUC 指标。（Table 2, p.8; Appendix H.1）

#### 7.3 组件 ablation

Table 3 支持多模块互补：

- 去掉 label-flipped $D'_{con}$ 后多数一般 / hard 结果下降，说明 contamination correction 对当前注入设置有贡献。
- 去掉 $L_{seen}$ 影响较大，例如 general TUSZ 从 82.91 降至 70.91；少量已知异常确实提供有效监督。
- 去掉 $L_{unseen}$ 在 hard TUSZ 从 75.70 降至 60.92，显示 unseen head / pseudo anomaly 对缺失异常类泛化尤为重要。
- 去掉 $s_f$ 也使若干 set 降低，说明参考特征距离提供补充分数。
- 随机选 reference、随机 flip label、随机 Gaussian feature noise 均弱于 influence-guided 设计；hard TUSZ 随机 feature perturbation 为 62.87。（Table 3, p.9）

敏感性实验中 $\lambda=1$、$k=5$ 是论文默认选择；增加 $k$ 过多可将原本属于 normal distribution 的形态人为伪装为 anomaly，引入偏差。（§4.4, p.9, Fig. 3）

#### 7.4 鲁棒性、生成质量与其它指标

- 在 2%–10% contamination rate 的敏感性图中，IMPACT 随污染增加表现相对稳定；ASD、SMD 某些点随污染率升高反而改善，作者将其解释为把污染改造成额外异常监督。该实验污染来源为测试 anomaly 且从最终测试剔除。（Appendix H.3, pp.20–22）
- 与 COE、WMix、COE-WMix、CutAddPaste 替换比较时，IMPACT hard setting 较稳定；feature distribution KLD 报告比基线 augmentation 平均低 64.13%（范围 0.03–0.32 vs. 0.15–1.53），并展示 t-SNE。KLD / t-SNE 仅说明该协议下合成 feature 与 unseen feature 分布较接近，不证明生成时序可解释或因果真实。（Appendix H.4, pp.22–24）
- 多通道数敏感性显示 3–5 channels 通常兼顾信息量和抗噪；通道过多可降低表现。（Appendix H.6, p.25）
- 额外 point-level evaluation 在 UCR / ASD / PSM / SMD 将测试序列以 stride 1 滑窗切成连续 intervals，再把每窗分数赋到其末端时间点；报告 Affiliation-F1 与 VUS-ROC。IMPACT 对 Affiliation-F1 在前三个数据集第一、PSM 第二，对 VUS-ROC 四集第一。（Appendix H.7, p.26）
- 作者给 influence computation 的复杂度论断 $O(MP)$（$M$ nominal samples，$P$ parameters），并以合成规模对比报告近似随样本量线性增长；实际开销仍依赖参数维度、Hessian/Fisher 近似和实现。（Appendix H.8, pp.26–28）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制

**作者指出的 group failure mode**：可能把与其它正常群体语义重叠少的 rare normal subpopulation 错认成异常；作者提出 future work 可引入 group-aware validation / subpopulation discovery。（Appendix I, p.28）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制

**label-flip 风险**：若 valid rare state 对 validation risk 有害，influence rule 也可能把它错误翻为 anomaly；需要检查 false-positive / group robustness，而不能将 influence sign 当无误 contamination oracle。（Appendix I; 分析推断）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制

**实验抽象**：将 test-set anomaly 子集搬入 train 作 2%–10% contamination、再从 test 剔除，有利于已知 anomaly distribution 的受控实验；生产里的未知污染生成机制未必相同。（Appendix E、H.3；分析推断）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制

**情境范围**：虽然 ASD / PSM / SMD 是服务 telemetry，IMPACT 输入是窗口内时间序列特征与标签，不使用 workload / release / Trace / service graph context；尚未检验正常负载切换与真实故障并发。（数据 / 方法设置；分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制（归属未明确）

**监督边界**：不是 unsupervised / label-free；训练依赖 labeled seen anomaly、validation loss 和小规模特定 benchmark 的异常类结构。验证集若没有可靠标签，影响方向是否可靠尚未解决。（§4.1; Appendix E）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制（归属未明确）

**pseudo anomaly realism**：扰动在 latent feature space，不还原为 waveform、业务事件或根因可解释注入；KLD / t-SNE 与 benchmark AUC 是有限旁证。（§3.2; Appendix H.4）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出与分析的限制（归属未明确）

**操作指标**：主表 AUC 不对应某个运行阈值或固定 false-alarm budget；主文没有系统报告在线告警延迟与每样本计算预算。（§4.1；分析边界）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 用 group-aware / state-aware validation 区分 contamination 与稀有但合法的 normal state，报告 group-wise false-positive / recall。
- **[分析推断]** 在污染类别、发生机制、污染比例与验证标签质量之外做 held-out stress tests，并验证 influence ranking。
- **[分析推断]** 为 feature pseudo anomaly 加 temporal decoder / causal constraints，验证其是否可映射到真实故障形态。
- **[分析推断]** 在固定 false-alarm budget 下比较 AUC、event delay、审查负担和每轮 influence compute。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **TimeRCD**：纯 synthetic pretraining、zero-shot context-relative normality；IMPACT 依赖 few-shot seen anomalies 与 validation-risk influence，是 supervised open-set 路线。
- **CAPMix / When Model Meets New Normals**：关注 KPI 噪声 / dynamic normality 与新正常状态；IMPACT 识别的是 validation-risk harmful data，不含业务状态语义。
- **DRA / MOSAD / InvAD / WSAD-DT**：open-set anomaly baselines；IMPACT 的核心差异是 influence 同时作 decontamination 与伪异常指导。
- **Fortifying Time Series**：robustness focus 在输入扰动与认证；IMPACT 的 robustness focus 是训练集污染和未见类别，需要区分输入 adversarial robustness 与 label contamination。
- **AnomSeer / PCRTA**：都通过辅助构造信号改善异常泛化；IMPACT 生成 feature-space pseudo anomaly，AnomSeer 对齐专家 trace，PCRTA 从扰动 views 学 contrastive representations。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §1–3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §§3.1–3.3, Fig. 2, Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.1, Eqs. 1–3 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.1, Eqs. 6–7 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.1, Eq. 8 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Eqs. 8–12 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.2 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Eqs. 14–15 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3.3, Eqs. 20–21 | 精读笔记保留的原文定位 |
| Method / formulas | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Algorithm 1 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §3, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf | §4.4, Fig. 3 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "impact",
  "title_en": "IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection",
  "title_zh": "IMPACT：面向开放集时间序列异常检测的影响建模",
  "authors": [
    "Xiaohui Zhou",
    "Yijie Wang",
    "Hongzuo Xu",
    "Weixuan Liang",
    "Xiaoli Li",
    "Guansong Pang"
  ],
  "year": 2026,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ICML/IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/impact/notes.md",
  "code_url": "https://github.com/mala-lab/IMPACT",
  "research_area": "少量已知异常监督下的开放集污染鲁棒检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] Open-set supervised TSAD：有少量 labeled seen anomalies，nominal-normal training pool 含未标记 anomaly contamination，测试需识别 seen + unseen anomaly classes。（§3, p.3） - [实验支持] 4 个单类与 4 个多类 benchmark，含 SMD / ASD / PSM telemetry、ECG、EEG；2% 主设置污染，另有 2%–10% 分析。（§4.1; Appendix E, H.3）",
  "research_problem": "作者讨论的不是纯 zero-shot 或完全无标签 TSAD。训练集合 $D=Dn\\cup Da$，其中 $Da$ 是少量已标记 seen anomaly，$Dn$ 被当成 normal 但允许含少量误标的真实 anomaly contamination。测试时既可能出现已见 anomaly，也要检测未见 anomaly class。实际设置的重要约束是：已有少量异常标记可利用，但未标记训练池不保证干净。（§3, p.3） 论文指出现有 open-set anomaly detection 常把余下训练数据默认作 normal，污染会把异常规律学成正常；同时，伪异常生成多来自 image augmentation 或手工 time-series transformations，不能确保产生符合时序结构且覆盖未见类的 pattern。（§1–2, pp.1–3）",
  "core_challenges": [
    "Unlabeled pool contamination：少量未识别 anomaly 以 normal label 参与有监督学习，会把决策边界推向错误方向。（§1）",
    "seen anomaly few-shot 过拟合：有限异常标签提供先验但种类少，模型容易围绕 seen classes 学边界，难泛化 unseen classes。（§1–3）",
    "伪异常是否有用难保证：固定 jitter、mixup、segment swapping 等规则可能制造不自然或仍靠近已知 pattern 的特征。（§2）",
    "训练样本影响方向不均等：有些被视为 normal 的样本提高验证 risk，有些稀有或形态多样的 normal 反而是重要参照，需区别 harmful contamination 与 helpful normality。（§3.1）",
    "开集评估需区分 seen / unseen：仅报告混合测试集总分会掩盖模型是识别了已知异常还是泛化到未知类别。（§4, Appendix H.1）"
  ],
  "existing_method_limits": [
    "[作者主张] Open-set baselines 常默认未标记池干净；固定 augmentation 不保证生成有用的 unseen anomaly。（§1–2）",
    "[分析推断] 需 validation labels / reliable risk estimate 的条件较强；valid rare subpopulation 也可能因组间差异而被错误剔除或翻标。"
  ],
  "core_idea": "IMPACT 面向带少量 seen anomaly labels、且 unlabeled normal training pool 可能污染的 open-set TSAD：以 validation-risk influence 找出有害训练样本并翻转其标签，再把最不利于降低 risk 的边界 normal embedding 沿 influence 方向扰动为 unseen pseudo anomalies，最后联合 seen / unseen heads、reference-feature distance 与 multi-channel deviation score 检测。（§§3–4, Eqs. 1–21, pp.3–6）",
  "technical_innovations": [
    {
      "name": "TIS",
      "author_claim": "**[作者主张] TIS**：multi-channel Gaussian deviation score / margin loss，使用 influence function 估算训练样本对 validation risk 的影响。（§3.1, Eqs. 1–7）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 TIS 的 multi-channel deviation loss",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] TIS**：multi-channel Gaussian deviation score / margin loss，使用 influence function 估算训练样本对 validation risk 的影响。（§3.1, Eqs. 1–7）"
    },
    {
      "name": "RADG decontamination",
      "author_claim": "**[作者主张] RADG decontamination**：对 $I_L(z_i)>0$ 的 $D_n$ 样本做 0→1 label flip；作者给出一阶 risk 下降表达式。（§3.2, Eqs. 8–13）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 RADG：risk-guided unseen pseudo anomaly",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] RADG decontamination**：对 $I_L(z_i)>0$ 的 $D_n$ 样本做 0→1 label flip；作者给出一阶 risk 下降表达式。（§3.2, Eqs. 8–13）"
    },
    {
      "name": "Feature-space pseudo anomaly",
      "author_claim": "**[作者主张] Feature-space pseudo anomaly**：取最 less-helpful 的 k 个 normals，在 $I_{per}^\\top$ 方向加扰动，并标为 unseen anomaly。（§3.2, Eqs. 14–16）",
      "challenge_ids": [
        "C5",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 RADG：risk-guided unseen pseudo anomaly",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Feature-space pseudo anomaly**：取最 less-helpful 的 k 个 normals，在 $I_{per}^\\top$ 方向加扰动，并标为 unseen anomaly。（§3.2, Eqs. 14–16）"
    },
    {
      "name": "双头训练与 score",
      "author_claim": "**[作者主张] 双头训练与 score**：seen / unseen head 联合 loss，加 multi-channel max abnormality 与到 $D_{ref}$ 平均 embedding 的 L2 distance。（§3.3, Eqs. 17–21）",
      "challenge_ids": [
        "C5",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.6 训练协议和实现",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 双头训练与 score**：seen / unseen head 联合 loss，加 multi-channel max abnormality 与到 $D_{ref}$ 平均 embedding 的 L2 distance。（§3.3, Eqs. 17–21）"
    }
  ],
  "methodology": {
    "architecture": "text 输入：少量 labeled seen anomalies + nominally-normal pool Dn（含污染）+ validation set V Phase I / initial multi-channel deviation model → TCN feature extractor φ + multi-channel head h → influence of each sample on V risk (TIS) Phase II / RADG ├─ IL(zi)>0: 候选 contamination，label 0→1 ├─ IL(zi)<0: 保留有帮助的 clean normals / reference Dref └─ 取最不利于 risk 降低的 k 个正常点，feature 沿 Iper^T 扰动并标为 unseen anomaly Phase III / retraining → shared feature + seen head h + unseen head h' Inference: multi-channel max abnormality + distance-to-normal-reference （Fig. 2, §§3.1–3.3, pp.3–6; Algorithm 1, Appendix G, p.19）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 TIS 的 multi-channel deviation loss",
      "6.2 Influence function 与 contamination 识别",
      "6.3 RADG：污染 label flip",
      "6.4 RADG：risk-guided unseen pseudo anomaly",
      "6.5 Seen / unseen learning 与 inference score",
      "6.6 训练协议和实现"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (6)",
      "Eq. (8)",
      "Eq. (14)",
      "Eq. (20)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "IMPACT 面向带少量 seen anomaly labels、且 unlabeled normal training pool 可能污染的 open-set TSAD：以 validation-risk influence 找出有害训练样本并翻转其标签，再把最不利于降低 risk 的边界 normal embedding 沿 influence 方向扰动为 unseen pseudo anomalies，最后联合 seen / unseen heads、reference-feature distance 与 multi-channel deviation score 检测。（§§3–4, Eqs. 1–21, pp.3–6）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets / protocols / baselines",
      "8 个 benchmark：单一 anomaly class 的 UCR、ASD、PSM、SMD；含多 anomaly classes 的 character trajectory CT、spoken Arabic digits SAD、PTB-XL ECG、TUSZ EEG。每个时间区间作为一个 sample；附录列出 interval 长度分别为 93–1,000、维数为 1–38。数据覆盖 UCR 异质单变量、服务 / cluster telemetry、语音与医疗波形。（§3, §4.1; Appendix E, pp.17–18）",
      "Table 1 general setting 下 IMPACT 八数据集 AUC：UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91（%）。作者报告相对竞争方法 6.37%–44.52% 的平均提升。（Table 1, p.7）",
      "Hard setting Table 2 的四组 mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。作者报告平均较七个 competitor 高 10.52%–42.83%。在见过的异常类之外，对每个 unseen class 的分析也显示较平衡表现；但 SOTA 优势的范围仍限于这些 benchmark、抽样协议与 AUC 指标。（Table 2, p.8; Appendix H.1）"
    ],
    "baselines": [
      "### 7.1 Datasets / protocols / baselines",
      "两类主 setting：unsupervised baseline 只看 nominal training；open-set general protocol 从可用 anomaly classes 随机抽 labeled examples；hard setting 对多类数据只以一个 anomaly class 的标签训练，测试时需泛化到其余 unseen classes。两个 open-set setting 默认每个用于监督的类别只用 10 个 anomaly examples。训练数据额外注入 2% test anomalies 作为 contamination；这些污染样本从最终 test set 排除，…",
      "Open-set comparison 包含 DevNet、DSAD、NCAD、DRA、MOSAD、InvAD、WSAD-DT；unsupervised 有 TCN-AE、THOC、TranAD、DCdetector、GPT4TS、COUTA、DADA。（§4.1）"
    ],
    "metrics": [
      "两类主 setting：unsupervised baseline 只看 nominal training；open-set general protocol 从可用 anomaly classes 随机抽 labeled examples；hard setting 对多类数据只以一个 anomaly class 的标签训练，测试时需泛化到其余 unseen classes。两个 open-set setting 默认每个用于监督的类别只用 10 个 anomaly examples。训练数据额外注入 2% test anomalies 作为 contamination；这些污染样本从最终 test set 排除，…",
      "Table 1 general setting 下 IMPACT 八数据集 AUC：UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91（%）。作者报告相对竞争方法 6.37%–44.52% 的平均提升。（Table 1, p.7）",
      "Hard setting Table 2 的四组 mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。作者报告平均较七个 competitor 高 10.52%–42.83%。在见过的异常类之外，对每个 unseen class 的分析也显示较平衡表现；但 SOTA 优势的范围仍限于这些 benchmark、抽样协议与 AUC 指标。（Table 2, p.8; Appendix H.1）",
      "### 7.4 鲁棒性、生成质量与其它指标"
    ],
    "main_results": [
      "### 7.2 主结果",
      "Table 1 general setting 下 IMPACT 八数据集 AUC：UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91（%）。作者报告相对竞争方法 6.37%–44.52% 的平均提升。（Table 1, p.7）",
      "Hard setting Table 2 的四组 mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。作者报告平均较七个 competitor 高 10.52%–42.83%。在见过的异常类之外，对每个 unseen class 的分析也显示较平衡表现；但 SOTA 优势的范围仍限于这些 benchmark、抽样协议与 AUC 指标。（Table 2, p.8; Appendix H.1）",
      "Table 3 支持多模块互补：",
      "- 去掉 label-flipped $D'{con}$ 后多数一般 / hard 结果下降，说明 contamination correction 对当前注入设置有贡献。 - 去掉 $L{seen}$ 影响较大，例如 general TUSZ 从 82.91 降至 70.91；少量已知异常确实提供有效监督。 - 去掉 $L{unseen}$ 在 hard TUSZ 从 75.70 降至 60.92，显示 unseen head / pseudo anomaly 对缺失异常类泛化尤为重要。 - 去掉 $sf$ 也使若干 set 降低，说明参考特征距离提供补充分数。…"
    ],
    "ablations": [
      "### 7.3 组件 ablation",
      "- 去掉 label-flipped $D'{con}$ 后多数一般 / hard 结果下降，说明 contamination correction 对当前注入设置有贡献。 - 去掉 $L{seen}$ 影响较大，例如 general TUSZ 从 82.91 降至 70.91；少量已知异常确实提供有效监督。 - 去掉 $L{unseen}$ 在 hard TUSZ 从 75.70 降至 60.92，显示 unseen head / pseudo anomaly 对缺失异常类泛化尤为重要。 - 去掉 $sf$ 也使若干 set 降低，说明参考特征距离提供补充分数。…",
      "敏感性实验中 $\\lambda=1$、$k=5$ 是论文默认选择；增加 $k$ 过多可将原本属于 normal distribution 的形态人为伪装为 anomaly，引入偏差。（§4.4, p.9, Fig. 3）",
      "- 在 2%–10% contamination rate 的敏感性图中，IMPACT 随污染增加表现相对稳定；ASD、SMD 某些点随污染率升高反而改善，作者将其解释为把污染改造成额外异常监督。该实验污染来源为测试 anomaly 且从最终测试剔除。（Appendix H.3, pp.20–22） - 与 COE、WMix、COE-WMix、CutAddPaste 替换比较时，IMPACT hard setting 较稳定；feature distribution KLD 报告比基线 augmentation 平均低 64.13%（范围 0.03–0.32 vs. 0.15–1.53），并展示 t-SNE。…"
    ],
    "robustness_generalization": [
      "两类主 setting：unsupervised baseline 只看 nominal training；open-set general protocol 从可用 anomaly classes 随机抽 labeled examples；hard setting 对多类数据只以一个 anomaly class 的标签训练，测试时需泛化到其余 unseen classes。两个 open-set setting 默认每个用于监督的类别只用 10 个 anomaly examples。训练数据额外注入 2% test anomalies 作为 contamination；这些污染样本从最终 test set 排除，…",
      "- 去掉 label-flipped $D'{con}$ 后多数一般 / hard 结果下降，说明 contamination correction 对当前注入设置有贡献。 - 去掉 $L{seen}$ 影响较大，例如 general TUSZ 从 82.91 降至 70.91；少量已知异常确实提供有效监督。 - 去掉 $L{unseen}$ 在 hard TUSZ 从 75.70 降至 60.92，显示 unseen head / pseudo anomaly 对缺失异常类泛化尤为重要。 - 去掉 $sf$ 也使若干 set 降低，说明参考特征距离提供补充分数。…",
      "### 7.4 鲁棒性、生成质量与其它指标",
      "- 在 2%–10% contamination rate 的敏感性图中，IMPACT 随污染增加表现相对稳定；ASD、SMD 某些点随污染率升高反而改善，作者将其解释为把污染改造成额外异常监督。该实验污染来源为测试 anomaly 且从最终测试剔除。（Appendix H.3, pp.20–22） - 与 COE、WMix、COE-WMix、CutAddPaste 替换比较时，IMPACT hard setting 较稳定；feature distribution KLD 报告比基线 augmentation 平均低 64.13%（范围 0.03–0.32 vs. 0.15–1.53），并展示 t-SNE。…"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "作者指出的 group failure mode：可能把与其它正常群体语义重叠少的 rare normal subpopulation 错认成异常；作者提出 future work 可引入 group-aware validation / subpopulation discovery。（Appendix I, p.28）"
    ],
    "reasoned_inference": [
      "label-flip 风险：若 valid rare state 对 validation risk 有害，influence rule 也可能把它错误翻为 anomaly；需要检查 false-positive / group robustness，而不能将 influence sign 当无误 contamination oracle。（Appendix I; 分析推断）",
      "实验抽象：将 test-set anomaly 子集搬入 train 作 2%–10% contamination、再从 test 剔除，有利于已知 anomaly distribution 的受控实验；生产里的未知污染生成机制未必相同。（Appendix E、H.3；分析推断）",
      "情境范围：虽然 ASD / PSM / SMD 是服务 telemetry，IMPACT 输入是窗口内时间序列特征与标签，不使用 workload / release / Trace / service graph context；尚未检验正常负载切换与真实故障并发。（数据 / 方法设置；分析推断）"
    ],
    "evidence_gaps": [
      "监督边界：不是 unsupervised / label-free；训练依赖 labeled seen anomaly、validation loss 和小规模特定 benchmark 的异常类结构。验证集若没有可靠标签，影响方向是否可靠尚未解决。（§4.1; Appendix E）",
      "pseudo anomaly realism：扰动在 latent feature space，不还原为 waveform、业务事件或根因可解释注入；KLD / t-SNE 与 benchmark AUC 是有限旁证。（§3.2; Appendix H.4）",
      "操作指标：主表 AUC 不对应某个运行阈值或固定 false-alarm budget；主文没有系统报告在线告警延迟与每样本计算预算。（§4.1；分析边界）"
    ]
  },
  "research_implications": [
    "- [分析推断] 用 group-aware / state-aware validation 区分 contamination 与稀有但合法的 normal state，报告 group-wise false-positive / recall。 - [分析推断] 在污染类别、发生机制、污染比例与验证标签质量之外做 held-out stress tests，并验证 influence ranking。 - [分析推断] 为 feature pseudo anomaly 加 temporal decoder / causal constraints，验证其是否可映射到真实故障形态。 - [分析推断] 在固定 false-alarm budget 下比较 AUC、event delay、审查负担和每轮 influence compute。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "impact",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "time-rcd",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomseer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "pcrta",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "fortifying-time-series",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§3.1–3.3, Fig. 2, Algorithm 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, Eqs. 1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, Eqs. 6–7",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "1132b52bb5fca62fa62c952d0c76f6001dcb6acd6189215bfca7fa7f46ffde01",
    "reading_note_sha256": "086df04864a7bc930c7c670e6b2e2800d4a0858e46cc86690adec807e95f92f1",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "c202e74605044b22ca0329e62d9897e27881ef3729d91a72c58a6ec0bd6cb64b"
  },
  "knowledge_card_path": "papers/impact/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
