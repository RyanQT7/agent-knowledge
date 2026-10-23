# Knowledge Dossier — Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution

## 1. Basic Information

- **English title**: Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution
- **中文译名**：解开时间序列异常检测中的“异常”：自监督三域方法
- **Authors**: Yuting Sun, Guansong Pang, Guanhua Ye, Tong Chen, Xia Hu, Hongzhi Yin
- **Venue / year / CCF**: ICDE 2024 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/pseudo-Skye/TriAD
- **Research area**: 三域自监督异常检测与窗口级定位
- **Method tags**: TSAD self-supervised learning tri-domain frequency domain contrastive learning discord discovery PA%K UCR

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 自监督、单变量 TSAD：面对不同异常长度与形状，用 temporal、frequency 和 residual 线索先找候选窗，再用 variable-length discord search 定位。（§§I, III, pp.1–7）
- **[实验支持]** UCR Archive 250 个 test series，每个数据集含一个 anomaly event。（§IV-A, p.7）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文讨论两个问题。其一，传统时序 augmentation（jittering、scaling、crop 等）未必保持正常模式，增强结果本身可能像异常；若简单把原样本与增强样本当作正对，会把异常样式拉近正常表征。其二，重建模型能学会连续异常片段，导致异常也被良好重建；discord discovery 可覆盖不同 anomaly length，但全序列多长度搜索成本高。（§I, pp.1–3）

作者将周期序列写成 Fourier 周期项与非周期残差之和（Eq. 1, p.3），并按 seasonality、shapelet 和 residual 讨论不同异常形态。定义中异常可表现为这些成分与预期 normal behavior 的相似度越过阈值；这是问题动机，不意味着算法获得真实业务上下文或已知的周期标签。（§II-A）

TriAD 的应用假设尤其重要：其 UCR Archive 中每个 test series 有一个 anomaly event，模型为每一条数据集单独训练 / 使用；推理阶段也将每域最异常窗口数设为 $Z=1$。因此任务不是任意多事件的持续流式检测。（§IV-A, PDF pp.7–8）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **augmentation 可能模拟异常而非不变视图**：异常检测的 representation learning 不应无条件将每个增强视作正例。（§I, §III-A）
2. **异常长度与形状跨度很大**：单一窗口 residual 可能漏掉连续异常；全序列 discord search 虽可变长，但耗时。（§I, §III-D）
3. **一元波形异常可落在不同统计域**：有些变化主要是频率 / 周期变化，有些表现为残差或局部时域变化。（§II-A, §III-B）
4. **基准 / 指标会放大方法优势**：PA 对区间内单点命中整段回填，random score 也可能得到高 PA-F1；需同时审视数据质量、PA%K 与事件距离指标。（§II-B, pp.3–4）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 不恰当正样本 augmentation 与单一 temporal residual 难覆盖 anomaly diversity；discord 搜索需降低范围。（§§I, III）
- **[分析推断]** test-set single-event 先验使其 top-1 窗口选择不自然适用于多事件 streaming TSAD。（§III-D; §IV-A）

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

TriAD 为单变量测试序列分别提取 temporal、Fourier amplitude/phase/power 和 detrended residual 表示，用 jittering / magnitude-warping 片段构造合成异常并进行域内 / 域间 contrastive representation learning；推理时先从每域找最异常窗口，再与正常训练窗比较选出候选区域，最后调用 MERLIN 搜索不同长度的 discord 并把窗口 / discord 命中投票成点分数。（§III, Eqs. 1–10, PDF pp.3–7）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：augmentation 可能模拟异常而非不变视图：异常检测的 representation learning 不应无条件将每个增强视作正例。（§I, §III-A）
- **C2（第4节挑战）**：异常长度与形状跨度很大：单一窗口 residual 可能漏掉连续异常；全序列 discord search 虽可变长，但耗时。（§I, §III-D）
- **C3（第4节挑战）**：一元波形异常可落在不同统计域：有些变化主要是频率 / 周期变化，有些表现为残差或局部时域变化。（§II-A, §III-B）
- **C4（第4节挑战）**：基准 / 指标会放大方法优势：PA 对区间内单点命中整段回填，random score 也可能得到高 PA-F1；需同时审视数据质量、PA%K 与事件距离指标。（§II-B, pp.3–4）

### 7.1 三域输入

- **作者技术描述**：**[作者主张] 三域输入**：raw temporal；frequency amplitude / phase / power 三通道；周期趋势去除 residual。（§II-A, III-B, Table I）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** frequency/general encoder 与 intra-domain contrast 对本 benchmark 更重要；residual encoder ablation 贡献较小。（Fig. 9, p.10）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 局部合成异常

- **作者技术描述**：**[作者主张] 局部合成异常**：random segment jitter / Butterworth magnitude warping，而不是把增强数据当正常正例。（§III-A, Eqs. 3–4）
- **对应挑战**：C1、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 片段级合成扰动”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 双对比目标

- **作者技术描述**：**[作者主张] 双对比目标**：same-domain original positives / augmented negatives；inter-domain 保留 domain-specific cues。（§III-C, Eqs. 5–7）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 Domain 间 contrastive loss与总目标”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Candidate-window + discord pipeline

- **作者技术描述**：**[作者主张] Candidate-window + discord pipeline**：每域 top-1 异常窗，经 normal-train comparison 选窗，再做局部多长度 MERLIN。（§III-D）
- **对应挑战**：C2、C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.5 窗口筛选、discord search 与 anomaly votes”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：6.5 窗口筛选、discord search 与 anomaly votes。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 片段级合成扰动

把训练序列切成长度 $L$ 的滑动窗口 $X_{i,L}$，再随机选择位置、长度和形状，用两类已有 augmentation 模拟异常型扭曲：

- **Jittering**：向窗口中的随机局部片段各时间点加随机噪声 $\epsilon$（Eq. 3）。
- **Magnitude warping**：用 Butterworth filter 产生平滑幅度变化（Eq. 4），再将变换片段嵌回原 window。

作者的区别在于：这些局部变换不被视作保持正常语义的正样本，而是训练阶段的 potential-anomaly negatives。窗口内扰动减少了整序列 augmentation 把所有上下文同时改变的问题。（§III-A, Fig. 5, pp.4–5）

#### 6.2 三个表征域

1. **Temporal domain**：直接以原始窗口作单通道输入，保留时间形状。
2. **Frequency domain**：对窗口作 DFT，按每个频率保留 amplitude、phase 和 power 三类 feature，合为三通道输入（Definition 2, Table I）。
3. **Residual domain**：去除底层周期 / seasonal trend 后的残差作为单通道输入，强调非周期偏移。（§III-B, pp.3, 5）

三域各自过专用的 dilated CNN residual encoder：每个 residual block 有两层 same-padded convolution，block 间 dilation rate 递增（翻倍）以扩展感受野；之后经共享 dense layers 将 $h\in\mathbb R^{L\times h_d}$ 压成时序 embedding $r\in\mathbb R^L$。temporal/residual encoder 输入一通道，frequency encoder 输入三通道。（§III-B, pp.5–6）

主文描述 residual 为“去除底层周期趋势”，但方法段没有把趋势估计器、拟合窗口和超参数说到与 Fourier feature 同等可直接复现的程度；复现时应核对官方实现中的精确预处理。（§III-B）

#### 6.3 Domain 内 contrastive loss

对同一 domain $d$，原始未增强窗口 representation $r_{i,d}$ 与 batch 内其他原始窗口 representation 组成 normal positive candidates；perturbed representations $r'_{j,d}$ 作为 negatives。式 (5) 用点积指数相似度计算 positive numerator 与 augmented-negative denominator：

$$\ell_{intra}^{(i,d)}=-\log\frac{\mathrm{sim}(r_{i,d},r^+_{i,d})}{\mathrm{sim}(r_{i,d},r^+_{i,d})+\sum_{j\in B}\exp(r_{i,d}^{\top}r'_{j,d})}. \tag{5}$$

目标是让未经扰动训练窗口共享的模式更紧密，同时使扰动窗口的表示远离原始窗口。其核心前提是 perturbation 能覆盖若干真实异常特征；若变换不符合领域异常或正常模式也容易被变换，positive/negative 语义就会变弱。（§III-C.1, Eq. 5, p.6）

#### 6.4 Domain 间 contrastive loss与总目标

仅用**未增强原始窗口**做 inter-domain contrast：same-domain representation 保留为 positive，其他 domain 的同一窗口表示作为 negatives，鼓励表示学习保留各域特有模式，降低三个域塌缩为相同 trivial feature 的风险（Eq. 6）。

$$\ell_{total}^{(i,d)}=\alpha\ell_{inter}^{(i,d)}+(1-\alpha)\ell_{intra}^{(i,d)}. \tag{7}$$

作者使用 $\alpha=0.4$，即 domain-level contrast 与域内 contrast 平衡。实验 ablation 发现 intra-domain 项贡献更大，说明 synthetic augmentation / hard-negative 作用在该 benchmark 上更明显。（§III-C, §IV-D, Eq. 7, Figs. 8–9）

#### 6.5 窗口筛选、discord search 与 anomaly votes

推理先按周期长度分窗，计算每个域内窗口表示之间的 similarity；每个域各选相似度最异常的 top $Z$ 窗，设 $Z=1$，因此候选最多三个。由于每域的异常响应不同，某异常可能只在频域或 residual 域显著。之后将三个候选窗分别与正常训练序列中对应长度的滑窗比较，保留与训练 normal windows 差异最大的一个。（§III-D.1）

对选出的窗在附近做可变长度的 MERLIN discord discovery，不再扫描全 test series。每个点 $x_n$ 获得：若落在候选窗内，加一票 $s_{TriAD}(x_n)=1[x_n\in X_{t,L}]$；每当落入一个被 MERLIN 标出的长度候选 discord，再加一票 $s_{dd}(x_n)=\sum_l1[x_n\in\hat X_{t,dd,l}]$。总分为 $s=s_{TriAD}+s_{dd}$（Eq. 8）。论文的简单阈值取有至少一票点的平均 vote；作者展示阈值提高至 vote 的 90th percentile 会提高 precision。（§III-D.2–3, Eq. 8, pp.6–7; Fig. 13）

这里有两个设计约束：test series 假定单个 event；一个候选 window 可能覆盖远多于实际异常的上下文，而两个 vote 未作 normalization / 权重标定。作者明确把更好的 normalization / weight 作为 future work。（§III-D.3, p.7）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (3)、Eq. (4)、Eq. (5)、Eq. (6)、Eq. (7)、Eq. (8)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.3 Domain 内 contrastive loss；6.4 Domain 间 contrastive loss与总目标；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

TriAD 为单变量测试序列分别提取 temporal、Fourier amplitude/phase/power 和 detrended residual 表示，用 jittering / magnitude-warping 片段构造合成异常并进行域内 / 域间 contrastive representation learning；推理时先从每域找最异常窗口，再与正常训练窗比较选出候选区域，最后调用 MERLIN 搜索不同长度的 discord 并把窗口 / discord 命中投票成点分数。（§III, Eqs. 1–10, PDF pp.3–7）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Datasets, baselines, metrics

- **数据**：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7）
- **训练设置**：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；6 residual blocks、$h_d=32$、$\alpha=.4$。（§IV-A, pp.7–8）
- **Deep baselines**：random / trained LSTM-AE、USAD、TS2Vec、Anomaly Transformer、MTGFlow、DCdetector；另与 MERLIN++ 做事件检出与效率比较。（§IV-B, pp.8–9）
- **指标**：point-wise F1、PA-F1、PA%K-F1（对 $K=1\ldots100$ 的曲线面积）、Affiliation event precision/recall/F1；正文说明在统一预测输入上先移除既有 PA，再计算优化后的指标。（§IV-B.1, pp.8–9）

#### 7.2 主结果和 MERLIN 比较

- **250 UCR series**：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。
- **MERLIN++**：只在按长度排序后的 62 个最短 UCR datasets 比较，MERLIN++ 29/62 检出，accuracy .424、14.5 min；TriAD tri-window .681、0.99 min，single-window .623、1.01 min（Table IV, p.9）。这是与该实验设定下结果的比较，不代表所有长度、硬件或 discord implementation 的固定加速比。
- TriAD 提供的 search window 平均约是 MERLIN 全序列搜索区域的 1/20（Fig. 7），以先缩小候选区再多长度搜索来降低成本。（§IV-B.2, pp.9–10）

#### 7.3 Ablation、参数与 case studies

- **Ablation**：temporal / general encoder 与 frequency encoder重要，residual encoder较弱；intra-domain contrastive learning 通常比 inter-domain 更关键（Fig. 9, p.10）。这只说明当前 UCR 异常类型与扰动设定中的贡献次序。
- **参数敏感度**：6 CNN blocks 略优，$h_d=32$ 更适合，过大 embedding 有过拟合迹象；$\alpha$ 需平衡两项损失（Fig. 8, p.10）。
- **UCR 025 case**：27-point 的微妙异常缺失正常波形的次峰；TriAD 的频率和 residual 表示都把第 39 窗标为最不相似，之后 MERLIN 的不同长度 search 集中在实际异常附近。（Figs. 10–12, pp.10–11）
- **多类异常可视化**：Fig. 16 展示 noise-like、duration、seasonal、trend、level-shift、contextual anomalies，报告长度约 20–200 points 的案例；属于精选可视化，不等于每类都有单独受控鲁棒性结果。（§IV-F, pp.11–12）
- **Discord failure case**：若候选窗里异常数据占多数，discord 算法可能把正常重复模式认作异常，漏掉异常；实现加 fallback：若没有找到 discord，则将 TriAD 指定窗口所有点标异常。（§IV-G, p.11）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：9. Limitations and Critical Reading

作者指出 vote score 可进一步加入 normalization / weighting；discord search 也会遇到异常区间压过正常区间的失败情景。（§III-D.3, §IV-G）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations and Critical Reading

**单 event 假设**：候选数 $Z=1$、每域 top-1、最后只选一个 window，难以直接支持多个事件、持续异常或异常与状态变化同时出现。（§III-D; §IV-A）

#### 精读笔记原章节：9. Limitations and Critical Reading

**residual 细节不足**：正文称移除 periodic trend，复现需核对官方实现确定周期估计和 residual calculation；这也意味着 residual branch 的技术先验并非完全由主文刻画。（§III-B）

#### 精读笔记原章节：9. Limitations and Critical Reading

**test-time candidate ranks**：与同一 test set 的窗口互相比，默认 test series 有一个离群 event；如果整段运行状态变化或多窗口异常，这个相对离群分布会改变。（§III-D）

#### 精读笔记原章节：9. Limitations and Critical Reading

**投票阈值未成为线上 operating point**：论文给出平均正票与 threshold sensitivity，但指标汇总对 PA%K 做 $K$ 曲线面积并用 event metric；没有提供跨状态固定 false-alert budget 下的完整流式延迟结果。（§III-D; §IV-B）

#### 精读笔记原章节：9. Limitations and Critical Reading

**benchmark 语义**：UCR 覆盖多领域单变量序列，未使用多变量 topology、workload、release 或 Trace。其多域波形线索不解释波动成因。

#### 精读笔记原章节：9. Limitations and Critical Reading

**人工阈值 / assumption**：主要 F1 与按单异常设定的窗口候选相互关联；真实系统若允许多 event 或异常率未知，需要重新评估候选提名和阈值。（§IV）

### C. 仍缺乏证据的问题

未做的实验只标记为证据边界，不解释为方法不具备该能力。具体未充分验证项见上方原精读笔记限制章节。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 放宽单事件先验，用 event count-free 候选筛选与多候选 NMS；测状态切换和多故障并发。
- **[分析推断]** 将业务周期 / workload context 与周期 residual 分解结合，检验合法周期切换是否误报。
- **[分析推断]** 校准三个 domain vote 及 MERLIN score，报告固定误报预算、event delay 和边界质量。
- **[分析推断]** 对照更丰富多变量工业指标、状态标签及 fault injection，验证不同域 representation 的外部语义。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **TFMAE**：同样用 temporal/frequency views；TFMAE 比较同一序列两种 mask views 的逐点 KL，而 TriAD 以 embedding 窗口的跨域/域内对比提名全序列的异常候选窗，再做 discord search。
- **TFC**：temporal-frequency-curvature 多路得分；TriAD 的第三域是去季节 residual，且依赖 UCR 单事件 + MERLIN 定位。
- **Perturbation Guiding / PCRTA**：都把 perturbation 用作潜在异常知识；TriAD 把增强当对比负例，PCRTA 学扰动类别并以其伪标签选正负样本。
- **Quo Vadis / TSB-AD**：基准与评价问题相同；TriAD 对 PA-F1 的批判与 PA%K / affiliation 改造需同这两篇一起读。
- **Sub-Adjacent Transformer**：都用局部窗口异常线索，TriAD 先候选窗+多长度 discord，Sub-Adjacent 强制模型不能用紧邻点重建目标。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | PDF pp.7–8 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eqs. 3–10, Fig. 4 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 4 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 5 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 5 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 6 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 7 | 精读笔记保留的原文定位 |
| Method / formulas | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Eq. 8, Fig. 13 | 精读笔记保留的原文定位 |
| Experimental evidence | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 6 | 精读笔记保留的原文定位 |
| Experimental evidence | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 7 | 精读笔记保留的原文定位 |
| Experimental evidence | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 9 | 精读笔记保留的原文定位 |
| Experimental evidence | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 8 | 精读笔记保留的原文定位 |
| Experimental evidence | Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf | Fig. 16 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "triad",
  "title_en": "Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution",
  "title_zh": "解开时间序列异常检测中的“异常”：自监督三域方法",
  "authors": [
    "Yuting Sun",
    "Guansong Pang",
    "Guanhua Ye",
    "Tong Chen",
    "Xia Hu",
    "Hongzhi Yin"
  ],
  "year": 2024,
  "venue": "ICDE",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2024/ICDE/Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
  "reading_note_path": "papers/triad/notes.md",
  "code_url": "https://github.com/pseudo-Skye/TriAD",
  "research_area": "三域自监督异常检测与窗口级定位",
  "method_tags": [
    "TSAD self-supervised learning tri-domain frequency domain contrastive learning discord discovery PA%K UCR"
  ],
  "research_scenario": "- [作者主张] 自监督、单变量 TSAD：面对不同异常长度与形状，用 temporal、frequency 和 residual 线索先找候选窗，再用 variable-length discord search 定位。（§§I, III, pp.1–7） - [实验支持] UCR Archive 250 个 test series，每个数据集含一个 anomaly event。（§IV-A, p.7）",
  "research_problem": "论文讨论两个问题。其一，传统时序 augmentation（jittering、scaling、crop 等）未必保持正常模式，增强结果本身可能像异常；若简单把原样本与增强样本当作正对，会把异常样式拉近正常表征。其二，重建模型能学会连续异常片段，导致异常也被良好重建；discord discovery 可覆盖不同 anomaly length，但全序列多长度搜索成本高。（§I, pp.1–3） 作者将周期序列写成 Fourier 周期项与非周期残差之和（Eq. 1, p.3），并按 seasonality、shapelet 和 residual 讨论不同异常形态。定义中异常可表现为这些成分与预期 normal behavior 的相似度越过阈值；这是问题动机，不意味着算法获得真实业务上下文或已知的周期标签。（§II-A） TriAD 的应用假设尤其重要：其 UCR Archive 中每个 test series 有一个 anomaly event，模型为每一条数据集单独训练 / 使用；推理阶段也将每域最异常窗口数设为 $Z=1$。因此任务不是任意多事件的持续流式检测。（§IV-A, PDF pp.7–8）",
  "core_challenges": [
    "augmentation 可能模拟异常而非不变视图：异常检测的 representation learning 不应无条件将每个增强视作正例。（§I, §III-A）",
    "异常长度与形状跨度很大：单一窗口 residual 可能漏掉连续异常；全序列 discord search 虽可变长，但耗时。（§I, §III-D）",
    "一元波形异常可落在不同统计域：有些变化主要是频率 / 周期变化，有些表现为残差或局部时域变化。（§II-A, §III-B）",
    "基准 / 指标会放大方法优势：PA 对区间内单点命中整段回填，random score 也可能得到高 PA-F1；需同时审视数据质量、PA%K 与事件距离指标。（§II-B, pp.3–4）"
  ],
  "existing_method_limits": [
    "[作者主张] 不恰当正样本 augmentation 与单一 temporal residual 难覆盖 anomaly diversity；discord 搜索需降低范围。（§§I, III）",
    "[分析推断] test-set single-event 先验使其 top-1 窗口选择不自然适用于多事件 streaming TSAD。（§III-D; §IV-A）"
  ],
  "core_idea": "TriAD 为单变量测试序列分别提取 temporal、Fourier amplitude/phase/power 和 detrended residual 表示，用 jittering / magnitude-warping 片段构造合成异常并进行域内 / 域间 contrastive representation learning；推理时先从每域找最异常窗口，再与正常训练窗比较选出候选区域，最后调用 MERLIN 搜索不同长度的 discord 并把窗口 / discord 命中投票成点分数。（§III, Eqs. 1–10, PDF pp.3–7）",
  "technical_innovations": [
    {
      "name": "三域输入",
      "author_claim": "**[作者主张] 三域输入**：raw temporal；frequency amplitude / phase / power 三通道；周期趋势去除 residual。（§II-A, III-B, Table I）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** frequency/general encoder 与 intra-domain contrast 对本 benchmark 更重要；residual encoder ablation 贡献较小。（Fig. 9, p.10）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 三域输入**：raw temporal；frequency amplitude / phase / power 三通道；周期趋势去除 residual。（§II-A, III-B, Table I）"
    },
    {
      "name": "局部合成异常",
      "author_claim": "**[作者主张] 局部合成异常**：random segment jitter / Butterworth magnitude warping，而不是把增强数据当正常正例。（§III-A, Eqs. 3–4）",
      "challenge_ids": [
        "C1",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 片段级合成扰动",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 局部合成异常**：random segment jitter / Butterworth magnitude warping，而不是把增强数据当正常正例。（§III-A, Eqs. 3–4）"
    },
    {
      "name": "双对比目标",
      "author_claim": "**[作者主张] 双对比目标**：same-domain original positives / augmented negatives；inter-domain 保留 domain-specific cues。（§III-C, Eqs. 5–7）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 Domain 间 contrastive loss与总目标",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 双对比目标**：same-domain original positives / augmented negatives；inter-domain 保留 domain-specific cues。（§III-C, Eqs. 5–7）"
    },
    {
      "name": "Candidate-window + discord pipeline",
      "author_claim": "**[作者主张] Candidate-window + discord pipeline**：每域 top-1 异常窗，经 normal-train comparison 选窗，再做局部多长度 MERLIN。（§III-D）",
      "challenge_ids": [
        "C2",
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.5 窗口筛选、discord search 与 anomaly votes",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Candidate-window + discord pipeline**：每域 top-1 异常窗，经 normal-train comparison 选窗，再做局部多长度 MERLIN。（§III-D）"
    }
  ],
  "methodology": {
    "architecture": "text 训练时：正常训练窗口 Xi,L ├─ 取 temporal raw、频域 amplitude/phase/power、周期趋势去除后的 residual ├─ 对窗口随机选一小段做 jittering 或 magnitude warping → synthetic perturbed views X'i,L ├─ 三个 domain encoder：dilated residual CNN → dense projection → ri,d ∈ R^L └─ Ltotal = α Linter + (1−α) Lintra 推理时：测试序列分窗 ├─ 每个域按窗口间 embedding dissimilarity 各提名 top-1（最多三个候选） ├─ 与正常训练窗口比对，选最不相似候选窗 ├─ 在该窗附近执行多长度 MERLIN discord search └─ 候选窗 + 被 discord 命中的区间累加 votes，按正票均值 threshold 输出点标签 （Fig. 4, §§III–IV, Eqs. 3–10, pp.4–8）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 片段级合成扰动",
      "6.2 三个表征域",
      "6.3 Domain 内 contrastive loss",
      "6.4 Domain 间 contrastive loss与总目标",
      "6.5 窗口筛选、discord search 与 anomaly votes"
    ],
    "key_formulas": [
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (5)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "TriAD 为单变量测试序列分别提取 temporal、Fourier amplitude/phase/power 和 detrended residual 表示，用 jittering / magnitude-warping 片段构造合成异常并进行域内 / 域间 contrastive representation learning；推理时先从每域找最异常窗口，再与正常训练窗比较选出候选区域，最后调用 MERLIN 搜索不同长度的 discord 并把窗口 / discord 命中投票成点分数。（§III, Eqs. 1–10, PDF pp.3–7）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets, baselines, metrics",
      "- 数据：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7） - 训练设置：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；…",
      "- 250 UCR series：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。…"
    ],
    "baselines": [
      "### 7.1 Datasets, baselines, metrics",
      "- 数据：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7） - 训练设置：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；…",
      "- 250 UCR series：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。…"
    ],
    "metrics": [
      "### 7.1 Datasets, baselines, metrics",
      "- 数据：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7） - 训练设置：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；…",
      "- 250 UCR series：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。…"
    ],
    "main_results": [
      "- 数据：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7） - 训练设置：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；6 residual blocks、$hd=32$、$\\alpha=.4$。…",
      "### 7.2 主结果和 MERLIN 比较",
      "- 250 UCR series：Table III 的 TriAD PA%K F1 为 .233 ± .009、Affiliation F1 为 .729 ± .014；point-wise F1 .237、PA-F1 .294。表中多个 deep baseline 的 PA-F1 明显高于 PA%K，展示原 PA 对点命中回填的膨胀。（§IV-B.1, Table III, p.9）作者称其 optimized point-wise F1 约为 SOTA deep models 的三倍；逐表比较还显示，模型间差异会随 metric 变化，需保留其 UCR / 单事件范围。 - MERLIN++：只在按长度排序后的 62 个最短 UCR datasets 比较，MERLIN++ 29/62 检出，…",
      "- Ablation：temporal / general encoder 与 frequency encoder重要，residual encoder较弱；intra-domain contrastive learning 通常比 inter-domain 更关键（Fig. 9, p.10）。这只说明当前 UCR 异常类型与扰动设定中的贡献次序。 - 参数敏感度：6 CNN blocks 略优，$hd=32$ 更适合，过大 embedding 有过拟合迹象；$\\alpha$ 需平衡两项损失（Fig. 8, p.10）。 - UCR 025 case：27-point 的微妙异常缺失正常波形的次峰；TriAD 的频率和 residual 表示都把第 39 窗标为最不相似，…"
    ],
    "ablations": [
      "### 7.3 Ablation、参数与 case studies",
      "- Ablation：temporal / general encoder 与 frequency encoder重要，residual encoder较弱；intra-domain contrastive learning 通常比 inter-domain 更关键（Fig. 9, p.10）。这只说明当前 UCR 异常类型与扰动设定中的贡献次序。 - 参数敏感度：6 CNN blocks 略优，$hd=32$ 更适合，过大 embedding 有过拟合迹象；$\\alpha$ 需平衡两项损失（Fig. 8, p.10）。 - UCR 025 case：27-point 的微妙异常缺失正常波形的次峰；…"
    ],
    "robustness_generalization": [
      "- 数据：UCR Time Series Anomaly Archive 的 250 个单变量 test series，每条含一个异常 event，长度 1–1,700 points；覆盖 health、industry、biology 等领域。（§IV-A, Fig. 6, p.7） - 训练设置：每个 dataset 单独训练模型；window 长度覆盖约 2.5 个周期，stride 为 window 的 1/4；10% training data 作 validation；batch 8、learning rate .001、20 epochs，5 个 seed；…",
      "- Ablation：temporal / general encoder 与 frequency encoder重要，residual encoder较弱；intra-domain contrastive learning 通常比 inter-domain 更关键（Fig. 9, p.10）。这只说明当前 UCR 异常类型与扰动设定中的贡献次序。 - 参数敏感度：6 CNN blocks 略优，$hd=32$ 更适合，过大 embedding 有过拟合迹象；$\\alpha$ 需平衡两项损失（Fig. 8, p.10）。 - UCR 025 case：27-point 的微妙异常缺失正常波形的次峰；…"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "作者指出 vote score 可进一步加入 normalization / weighting；discord search 也会遇到异常区间压过正常区间的失败情景。（§III-D.3, §IV-G）"
    ],
    "reasoned_inference": [
      "单 event 假设：候选数 $Z=1$、每域 top-1、最后只选一个 window，难以直接支持多个事件、持续异常或异常与状态变化同时出现。（§III-D; §IV-A）",
      "residual 细节不足：正文称移除 periodic trend，复现需核对官方实现确定周期估计和 residual calculation；这也意味着 residual branch 的技术先验并非完全由主文刻画。（§III-B）",
      "test-time candidate ranks：与同一 test set 的窗口互相比，默认 test series 有一个离群 event；如果整段运行状态变化或多窗口异常，这个相对离群分布会改变。（§III-D）",
      "投票阈值未成为线上 operating point：论文给出平均正票与 threshold sensitivity，但指标汇总对 PA%K 做 $K$ 曲线面积并用 event metric；没有提供跨状态固定 false-alert budget 下的完整流式延迟结果。（§III-D; §IV-B）",
      "benchmark 语义：UCR 覆盖多领域单变量序列，未使用多变量 topology、workload、release 或 Trace。其多域波形线索不解释波动成因。",
      "人工阈值 / assumption：主要 F1 与按单异常设定的窗口候选相互关联；真实系统若允许多 event 或异常率未知，需要重新评估候选提名和阈值。（§IV）"
    ],
    "evidence_gaps": [
      "未报告的环境属于证据不足，不等于方法能力不足"
    ]
  },
  "research_implications": [
    "- [分析推断] 放宽单事件先验，用 event count-free 候选筛选与多候选 NMS；测状态切换和多故障并发。 - [分析推断] 将业务周期 / workload context 与周期 residual 分解结合，检验合法周期切换是否误报。 - [分析推断] 校准三个 domain vote 及 MERLIN score，报告固定误报预算、event delay 和边界质量。 - [分析推断] 对照更丰富多变量工业指标、状态标签及 fault injection，验证不同域 representation 的外部语义。"
  ],
  "related_papers": [
    {
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "triad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfmae",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "pcrta",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "sub-adjacent-transformer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "PDF pp.7–8",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eqs. 3–10, Fig. 4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Fig. 5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Eq. 8, Fig. 13",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Experimental evidence",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Fig. 6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Experimental evidence",
      "pdf_file": "Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf",
      "locator": "Fig. 7",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "ec16fc5f060a5b2307e02a0d1a156e7a14bc17c538330a0e9d21186ba97f8809",
    "reading_note_sha256": "e2f1a886931ccb3da3b8128287cb00b75208636469d4fa856dc0cffa13ba0b79",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "4de897467bd1e8668fcedcf447146174596dd592ec5d89672a8202eb365ee2b9"
  },
  "knowledge_card_path": "papers/triad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
