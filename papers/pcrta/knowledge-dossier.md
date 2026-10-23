# Knowledge Dossier — Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection

## 1. Basic Information

- **English title**: Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection
- **中文译名**：扰动引导的时间序列异常检测对比表征学习
- **Authors**: Liaoyuan Tang, Zheng Wang, Guanxiong He, Rong Wang, Feiping Nie
- **Venue / year / CCF**: IJCAI 2024 / CCF B
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf](../../sources/papers/tsad-2024-2026/2024/IJCAI/Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: 扰动伪标签引导的对比式异常检测
- **Method tags**: TSAD perturbation contrastive learning pseudo-labels TCN LOF multi-view best-F1 threshold

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督多变量 TSAD：用扰动类别识别的伪标签改善对比学习的正 / 负样本构造。（§§1, 3）
- **[实验支持]** WaQ、DSADS、Epilepsy、ASD、SMD、SWaT 六个 benchmark。（Table 1, p.5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文关注 self-supervised contrastive TSAD 的两个薄弱环节：time-series augmentation 的语义影响不清楚，以及正 / 负样本选择若将同类样本误配为负，会造成 class collapse 或低效表示。作者提出的核心假设是：若一个真实异常受某种 perturbation 影响，其“perturbation type”相较正常行为更容易被分类器混淆；分类器输出的扰动伪标签因此可以辅助识别困难的异常相关表示。（§§1–2, pp.1–3）

形式上，多变量序列 $X=\langle x_1,\dots,x_N\rangle$ 中 $x_t\in\mathbb R^D$。先用长度 $l$、stride $r$ 划为 subsequences $s_t$；训练 stride 用 $r$，推理 stride 为 1。每个推理窗口得到一个 score 并赋给该窗口最后时刻，最开始 $l-1$ 个时间点补零。（§3.1, p.3）

PCRTA 是无监督表示学习 + LOF outlier scoring；它不直接输出经校准的概率，也不对 anomaly type 做人工监督分类。（§3.1, §4.2）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **augmentation 与异常语义重叠**：随机噪声、尺度 / 片段变形可能本身构造出类似真实异常的观测，不能假设增强结果仍是等价正常 positive。（§3.3, p.4）
2. **高维距离 / 分布几何使近邻选样不稳**：高维样本更可能呈 hyper-ellipsoidal 而非 hyper-spherical 分布，直接按嵌入距离构造同类正例会误配。（Proposition 1, §3.4, p.4）
3. **人工 anomaly class labels 不可得**：真实标签缺乏；必须从自动生成的扰动及其分类混淆中形成伪标签。（§3.3–3.4）
4. **点级 anomaly score 与事件检测不同**：窗口分数对应最后时点，检测 F1 还需选 threshold；异常区间连续性由评估 protocol 决定。（§3.1, §4.1）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 现有 contrastive TSAD 对扰动影响与正负样本选择缺少明确建模。（§§1–2）
- **[分析推断]** 六类固定 perturbation 偏向 point / contextual / collective 人工模式，未覆盖业务负载切换、慢漂移或 topology change。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

PCRTA 先以六种人工设计的 point / contextual / collective perturbation 训练 7 类扰动识别器，再将其预测伪标签用于同类 top-k 正样本和异类负样本选择，借助 TCN + projection network 学习表征；推理时用 LOF 分别评价原序列及六种扰动 view 的 embedding，取平均作为 anomaly score。（§3, Eqs. 1–9, PDF pp.3–6）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：augmentation 与异常语义重叠：随机噪声、尺度 / 片段变形可能本身构造出类似真实异常的观测，不能假设增强结果仍是等价正常 positive。（§3.3, p.4）
- **C2（第4节挑战）**：高维距离 / 分布几何使近邻选样不稳：高维样本更可能呈 hyper-ellipsoidal 而非 hyper-spherical 分布，直接按嵌入距离构造同类正例会误配。（Proposition 1, §3.4, p.4）
- **C3（第4节挑战）**：人工 anomaly class labels 不可得：真实标签缺乏；必须从自动生成的扰动及其分类混淆中形成伪标签。（§3.3–3.4）
- **C4（第4节挑战）**：点级 anomaly score 与事件检测不同：窗口分数对应最后时点，检测 F1 还需选 threshold；异常区间连续性由评估 protocol 决定。（§3.1, §4.1）

### 7.1 六种局部异常扰动

- **作者技术描述**：**[作者主张] 六种局部异常扰动**：point 极值替换、contextual offset、collective 片段替换，各有两个数值变体。（§3.3, Eq. 2, p.4）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Perturbation classifier

- **作者技术描述**：**[作者主张] Perturbation classifier**：TCN representation 上学原始 + 6 扰动类型 cross-entropy。（Eqs. 1–3）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 TCN temporal encoder 与 perturbation classifier”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 低维 projection 与 class-guided pairs

- **作者技术描述**：**[作者主张] 低维 projection 与 class-guided pairs**：same pseudo-class top-5 cosine positives、different pseudo-class negatives。（Eqs. 5–8, pp.4–5）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 Projection 与伪标签指导的 contrastive selection”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 多 view LOF

- **作者技术描述**：**[作者主张] 多 view LOF**：原始及六类 transform embeddings 分别算局部密度异常分数并取均值。（Eq. 9, p.6）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 Inference：7 个 view 的 LOF average”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：6.5 训练和数据参数。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 六类人工设计 perturbation

作者先将时序数据归一化至 $[0,1]$，定义 $\Omega$ 为“原始输入 $\delta_0$ + 六个 perturbation”，从 point / contextual / collective 三种基础异常构造中取变体（Eq. 2, p.4）：

1. **Point anomaly** $\delta_{I,\gamma}$：修改输入窗口最后一个时刻，随机选中维度值替换成全局极值 $\gamma=+2$ 或 $-2$。
2. **Contextual anomaly** $\delta_{II,\gamma}$：将最后观测的部分维度，按前 $k=10$ 个值均值施加偏移 $\gamma=+0.5$ 或 $-0.5$，令其相对局部上下文改变。
3. **Collective anomaly** $\delta_{III,\gamma}$：在窗口中一个片段内随机挑维度，以 $\gamma=0$ 或 $1.0$ 替换，形成联合 / 区间型偏离。

这些参数是作者实现的通用扰动设计，不是由每个数据集估计出的 anomaly distribution。训练时原始窗口标签为 class 0，六种 transformed samples 标签分别对应 class 1–6。扰动识别器用已知 transform ID 做交叉熵训练（Eq. 3）。（§3.3, Eqs. 2–3, pp.3–4）

#### 6.2 TCN temporal encoder 与 perturbation classifier

先用 temporal modeling network $\phi$（TCN）提取窗口时序表示，捕捉变量内 / 变量间时间上下文；作者选择 TCN 以并行卷积替代 RNN 的逐步递归。扰动分类网络以这些表示判定原始 / augmentation 类型，交叉熵为：

$$\mathcal L_{mul}=-\frac1N\sum_i\sum_j y_{ij}\log p_{ij}. \tag{3}$$

训练分类器时监督标签来自合成 augmentation 的类别。随后模型对这些 view 给出的类别输出 / pseudo-label $\Pi$ 被送入 contrastive network，决定正 / 负 pair，不使用真实 anomaly labels 来筛 pair。（§3.2–3.3, pp.3–4）

#### 6.3 Projection 与伪标签指导的 contrastive selection

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

#### 6.4 Inference：7 个 view 的 LOF average

训练完成后，对每个 test window 生成原始 embedding 与六个增强 embedding，分别计算 LOF score，最后对七个分数取平均：

$$s_i=\frac1C\sum\mathrm{LOF}(z_{aug}). \tag{9}$$

（正文记为 $C$ 个 representation；实现 view 为 6 augmentations + original。）分数高表示在 embedding neighbor distribution 中更离群。由于推理也包含多种 perturbation view，这一步比单次 encoder + LOF 更重；论文未提供完整 latency / memory 对照。（§4.2, p.6）

#### 6.5 训练和数据参数

- TCN：kernel size 2、单 hidden layer、16 neural units。
- window length $l$ 与数据集 / 方法设置有关；多变量推理 stride 1；部分大数据 SWaT / WaQ 使用训练 stride 100 / 5。
- 最多 100 epochs，默认 $\alpha=.2$、positive top-$k=5$。
- 多数据集实验在 Intel Xeon Gold 6248R + NVIDIA Titan Xp 10GB、Ubuntu 20.04 上运行。（§4.1, PDF pp.5–6）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (2)、Eq. (3)、Eq. (5)、Eq. (7)、Eq. (8)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.5 训练和数据参数；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.4 Inference：7 个 view 的 LOF average及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

PCRTA 先以六种人工设计的 point / contextual / collective perturbation 训练 7 类扰动识别器，再将其预测伪标签用于同类 top-k 正样本和异类负样本选择，借助 TCN + projection network 学习表征；推理时用 LOF 分别评价原序列及六种扰动 view 的 embedding，取平均作为 anomaly score。（§3, Eqs. 1–9, PDF pp.3–6）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Dataset / baseline / metric

- **6 个数据集**：WaQ、DSADS、Epilepsy、ASD、SMD、SWaT；SMD 只保留 3 台机器（3-1、3-9、3-11），作者依据数据质量分析排除其他 entity。（Table 1, p.5）
- **13 个对照**：OCSVM、GOAD、ECOD、LSTM-ED、TCN-ED、DSVDD、MSCRED、OmniAnomaly、USAD、GDN、NeuTraL、TranAD、COUTA。（§4.1）
- **指标**：F1 与 AUC-PR。论文枚举 timestamp score thresholds 计算 Precision/Recall，采用 test labels 可得的 best F1；AUC-PR 提供阈值曲线平均值。（§4.1）因此 best F1 是 benchmark best-case，不是固定 threshold 的运行点。

#### 7.2 主结果

Table 2（PDF pp.6–7）报告 F1 / AUC-PR mean±std。PCRTA 数值：WaQ .784 / .794，DSADS .943 / .960，Epilepsy .934 / .964，ASD .927 / .933，SMD .987 / .988，SWaT .978 / .996。作者称在五个数据集排名第一、ASD 排第二；Epilepsy 相对 COUTA 的提升约 13% F1 / 17% AUC-PR。（§4.2, Table 2, pp.6–7）

#### 7.3 Representation、generalization 和 ablation

- **Epilepsy t-SNE**：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。
- **Synthetic mixed-anomaly case**：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。
- **Ablation（Table 3, p.7）**：在 WaQ / DSADS / Epilepsy 上，完整 PCRTA F1 为 .78 / .94 / .93；替换 pseudo-label 为 ground-truth augmentation class 为 .73 / .93 / .89；去掉 $L_{mul}$ 为 .67 / .61 / .92；去掉 $L_{con}$ 为 .74 / .90 / .87。三种组件大多提供增益，但贡献依数据集而变，Epilepsy 去掉分类损失后指标变化较小。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations and Critical Reading

**扰动覆盖假设**：六种固定扰动 / 幅度不能覆盖所有领域异常。真实异常可能是缓慢状态转换、负载峰值、周期变化或跨通道依赖变化，而不一定降低扰动分类正确率。（§3.3）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Classifier pseudo-label coupling**：同一学习到的分类边界既提供伪标签，又组织 contrastive positives/negatives；如果分类器系统性混淆合法正常模式，contrastive network 可能放大误分结构。（Eq. 1, §§3.3–3.4，分析推断）

#### 精读笔记原章节：9. Limitations and Critical Reading

**检测分数仍由 LOF 决定**：分类误差 / perturbation confusion 不是最终 anomaly score 的直接组成；最终 score 是七种 representation 的平均 LOF。（Eq. 9）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Threshold protocol**：best F1 通过遍历阈值取得，含测试标签 oracle 选择；不能将报告 F1 当作不依赖标签的线上告警结果。（§4.1）

#### 精读笔记原章节：9. Limitations and Critical Reading

**事件结构**：subsequence score 被赋给窗口末端，前 $l-1$ 时点补零；窗口 length / stride 会影响边界和检测延迟。（§3.1, §4.1）

#### 精读笔记原章节：9. Limitations and Critical Reading

**外部上下文缺失**：输入为数值时序窗口，未使用 workload、release、Trace 或正常业务状态标签，无法解释偏离来自新正常还是故障。

#### 精读笔记原章节：9. Limitations and Critical Reading

**复现透明度**：论文正文没有代码链接；已给定配置之外的 transform 随机参数、LOF 配置等仍需从 implementation / supplementary source 获取。

### C. 仍缺乏证据的问题

未做的实验只标记为证据边界，不解释为方法不具备该能力。具体未充分验证项见上方原精读笔记限制章节。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 以真实业务事件 / workload-conditioned perturbation 验证“分类困难度”是否跟故障相关。
- **[分析推断]** 对 rare-but-normal operating regime 作专门 hard negative tests，避免被扰动负样本机制当作异常。
- **[分析推断]** 评估 classifier calibration、pseudo-label noise、top-$k$ 和 LOF views 对 event-level detection latency / false-alert rate 的影响。
- **[分析推断]** 加入变量关系型扰动，检验跨通道故障而非逐变量值替换。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **TriAD**：都将 augmentation 看作异常线索；TriAD 用 augmented view 作为同域负例，且用三域相似度提名异常窗口 + MERLIN；PCRTA 用 perturbation classifier pseudo-label 组织 positives/negatives，最后由 LOF 聚合多-view score。
- **CAPMix**：都构造合成异常；CAPMix 用形状特征与伪异常训练决策边界，PCRTA 用离散 perturbation class 改善表征近邻结构。扰动语义 / threat model 不同。
- **TFMAE**：同属 self-supervised multi-view；TFMAE 依赖 temporal/frequency mask discrepancy，PCRTA 依赖 augmentation type classification 与 LOF。
- **Quo Vadis / TSB-AD**：都提醒 test-best F1 与 point-adjusted scores 会夸大可部署结论；PCRTA 的 best-F1 threshold 需要按此理解。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §§1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.1, §4.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §§1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | Table 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.3–3.4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.1, §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §§1–2 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §§3.2–3.4, Eqs. 1–9, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | Eq. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.3, Eq. 3, Eqs. 2–3 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.2–3.3 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | Eq. 7, Eq. 8 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.4, Eqs. 5–8 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §3.2, §4.1 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §4.2 | 精读笔记保留的原文定位 |
| Method / formulas | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | PDF pp.5–6, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | PDF pp.6–7, §4.2, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | Fig. 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf | §4.4, Fig. 4 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "pcrta",
  "title_en": "Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection",
  "title_zh": "扰动引导的时间序列异常检测对比表征学习",
  "authors": [
    "Liaoyuan Tang",
    "Zheng Wang",
    "Guanxiong He",
    "Rong Wang",
    "Feiping Nie"
  ],
  "year": 2024,
  "venue": "IJCAI",
  "ccf_level": "B",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2024/IJCAI/Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/pcrta/notes.md",
  "code_url": null,
  "research_area": "扰动伪标签引导的对比式异常检测",
  "method_tags": [
    "TSAD perturbation contrastive learning pseudo-labels TCN LOF multi-view best-F1 threshold"
  ],
  "research_scenario": "- [作者主张] 无监督多变量 TSAD：用扰动类别识别的伪标签改善对比学习的正 / 负样本构造。（§§1, 3） - [实验支持] WaQ、DSADS、Epilepsy、ASD、SMD、SWaT 六个 benchmark。（Table 1, p.5）",
  "research_problem": "论文关注 self-supervised contrastive TSAD 的两个薄弱环节：time-series augmentation 的语义影响不清楚，以及正 / 负样本选择若将同类样本误配为负，会造成 class collapse 或低效表示。作者提出的核心假设是：若一个真实异常受某种 perturbation 影响，其“perturbation type”相较正常行为更容易被分类器混淆；分类器输出的扰动伪标签因此可以辅助识别困难的异常相关表示。（§§1–2, pp.1–3） 形式上，多变量序列 $X=\\langle x1,\\dots,xN\\rangle$ 中 $xt\\in\\mathbb R^D$。先用长度 $l$、stride $r$ 划为 subsequences $st$；训练 stride 用 $r$，推理 stride 为 1。每个推理窗口得到一个 score 并赋给该窗口最后时刻，最开始 $l-1$ 个时间点补零。（§3.1, p.3） PCRTA 是无监督表示学习 + LOF outlier scoring；它不直接输出经校准的概率，也不对 anomaly type 做人工监督分类。（§3.1, §4.2）",
  "core_challenges": [
    "augmentation 与异常语义重叠：随机噪声、尺度 / 片段变形可能本身构造出类似真实异常的观测，不能假设增强结果仍是等价正常 positive。（§3.3, p.4）",
    "高维距离 / 分布几何使近邻选样不稳：高维样本更可能呈 hyper-ellipsoidal 而非 hyper-spherical 分布，直接按嵌入距离构造同类正例会误配。（Proposition 1, §3.4, p.4）",
    "人工 anomaly class labels 不可得：真实标签缺乏；必须从自动生成的扰动及其分类混淆中形成伪标签。（§3.3–3.4）",
    "点级 anomaly score 与事件检测不同：窗口分数对应最后时点，检测 F1 还需选 threshold；异常区间连续性由评估 protocol 决定。（§3.1, §4.1）"
  ],
  "existing_method_limits": [
    "[作者主张] 现有 contrastive TSAD 对扰动影响与正负样本选择缺少明确建模。（§§1–2）",
    "[分析推断] 六类固定 perturbation 偏向 point / contextual / collective 人工模式，未覆盖业务负载切换、慢漂移或 topology change。"
  ],
  "core_idea": "PCRTA 先以六种人工设计的 point / contextual / collective perturbation 训练 7 类扰动识别器，再将其预测伪标签用于同类 top-k 正样本和异类负样本选择，借助 TCN + projection network 学习表征；推理时用 LOF 分别评价原序列及六种扰动 view 的 embedding，取平均作为 anomaly score。（§3, Eqs. 1–9, PDF pp.3–6）",
  "technical_innovations": [
    {
      "name": "六种局部异常扰动",
      "author_claim": "**[作者主张] 六种局部异常扰动**：point 极值替换、contextual offset、collective 片段替换，各有两个数值变体。（§3.3, Eq. 2, p.4）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 六种局部异常扰动**：point 极值替换、contextual offset、collective 片段替换，各有两个数值变体。（§3.3, Eq. 2, p.4）"
    },
    {
      "name": "Perturbation classifier",
      "author_claim": "**[作者主张] Perturbation classifier**：TCN representation 上学原始 + 6 扰动类型 cross-entropy。（Eqs. 1–3）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 TCN temporal encoder 与 perturbation classifier",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Perturbation classifier**：TCN representation 上学原始 + 6 扰动类型 cross-entropy。（Eqs. 1–3）"
    },
    {
      "name": "低维 projection 与 class-guided pairs",
      "author_claim": "**[作者主张] 低维 projection 与 class-guided pairs**：same pseudo-class top-5 cosine positives、different pseudo-class negatives。（Eqs. 5–8, pp.4–5）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 Projection 与伪标签指导的 contrastive selection",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 低维 projection 与 class-guided pairs**：same pseudo-class top-5 cosine positives、different pseudo-class negatives。（Eqs. 5–8, pp.4–5）"
    },
    {
      "name": "多 view LOF",
      "author_claim": "**[作者主张] 多 view LOF**：原始及六类 transform embeddings 分别算局部密度异常分数并取均值。（Eq. 9, p.6）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 Inference：7 个 view 的 LOF average",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 多 view LOF**：原始及六类 transform embeddings 分别算局部密度异常分数并取均值。（Eq. 9, p.6）"
    }
  ],
  "methodology": {
    "architecture": "text 多变量序列 → 滑动窗口 S ├─ augmentation pool Ω: 原始 + point / contextual / collective 共 6 个局部扰动 ├─ TCN φ 建模窗口时间关联 ├─ perturbation classifier：学习 7 类扰动标签，交叉熵 Lmul → 预测伪标签 Π ├─ projection Ψ：压缩高维表示 z，按 Π 选同类 top-k cosine positives / 异类 negatives └─ L = Lmul + α Lcon，更新分类、TCN / projection 表示 推理：原始窗口及 6 个 perturbation view → embedding → 7 次 LOF score → 平均为窗口异常分数 （Fig. 2, Eqs. 1–9, §§3.2–3.4, pp.3–6）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 六类人工设计 perturbation",
      "6.2 TCN temporal encoder 与 perturbation classifier",
      "6.3 Projection 与伪标签指导的 contrastive selection",
      "6.4 Inference：7 个 view 的 LOF average",
      "6.5 训练和数据参数"
    ],
    "key_formulas": [
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (5)",
      "Eq. (7)",
      "Eq. (8)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "PCRTA 先以六种人工设计的 point / contextual / collective perturbation 训练 7 类扰动识别器，再将其预测伪标签用于同类 top-k 正样本和异类负样本选择，借助 TCN + projection network 学习表征；推理时用 LOF 分别评价原序列及六种扰动 view 的 embedding，取平均作为 anomaly score。（§3, Eqs. 1–9, PDF pp.3–6）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Dataset / baseline / metric",
      "- 6 个数据集：WaQ、DSADS、Epilepsy、ASD、SMD、SWaT；SMD 只保留 3 台机器（3-1、3-9、3-11），作者依据数据质量分析排除其他 entity。（Table 1, p.5） - 13 个对照：OCSVM、GOAD、ECOD、LSTM-ED、TCN-ED、DSVDD、MSCRED、OmniAnomaly、USAD、GDN、NeuTraL、TranAD、COUTA。（§4.1） - 指标：F1 与 AUC-PR。论文枚举 timestamp score thresholds 计算 Precision/Recall，采用 test labels 可得的 best F1；…",
      "Table 2（PDF pp.6–7）报告 F1 / AUC-PR mean±std。PCRTA 数值：WaQ .784 / .794，DSADS .943 / .960，Epilepsy .934 / .964，ASD .927 / .933，SMD .987 / .988，SWaT .978 / .996。作者称在五个数据集排名第一、ASD 排第二；Epilepsy 相对 COUTA 的提升约 13% F1 / 17% AUC-PR。（§4.2, Table 2, pp.6–7）",
      "- Epilepsy t-SNE：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。 - Synthetic mixed-anomaly case：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。…"
    ],
    "baselines": [
      "### 7.1 Dataset / baseline / metric"
    ],
    "metrics": [
      "### 7.1 Dataset / baseline / metric",
      "- 6 个数据集：WaQ、DSADS、Epilepsy、ASD、SMD、SWaT；SMD 只保留 3 台机器（3-1、3-9、3-11），作者依据数据质量分析排除其他 entity。（Table 1, p.5） - 13 个对照：OCSVM、GOAD、ECOD、LSTM-ED、TCN-ED、DSVDD、MSCRED、OmniAnomaly、USAD、GDN、NeuTraL、TranAD、COUTA。（§4.1） - 指标：F1 与 AUC-PR。论文枚举 timestamp score thresholds 计算 Precision/Recall，采用 test labels 可得的 best F1；…",
      "Table 2（PDF pp.6–7）报告 F1 / AUC-PR mean±std。PCRTA 数值：WaQ .784 / .794，DSADS .943 / .960，Epilepsy .934 / .964，ASD .927 / .933，SMD .987 / .988，SWaT .978 / .996。作者称在五个数据集排名第一、ASD 排第二；Epilepsy 相对 COUTA 的提升约 13% F1 / 17% AUC-PR。（§4.2, Table 2, pp.6–7）",
      "- Epilepsy t-SNE：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。 - Synthetic mixed-anomaly case：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。…"
    ],
    "main_results": [
      "- 6 个数据集：WaQ、DSADS、Epilepsy、ASD、SMD、SWaT；SMD 只保留 3 台机器（3-1、3-9、3-11），作者依据数据质量分析排除其他 entity。（Table 1, p.5） - 13 个对照：OCSVM、GOAD、ECOD、LSTM-ED、TCN-ED、DSVDD、MSCRED、OmniAnomaly、USAD、GDN、NeuTraL、TranAD、COUTA。（§4.1） - 指标：F1 与 AUC-PR。论文枚举 timestamp score thresholds 计算 Precision/Recall，采用 test labels 可得的 best F1；AUC-PR 提供阈值曲线平均值。（§4.1）因此 best F1 是 benchmark best-case，…",
      "### 7.2 主结果",
      "Table 2（PDF pp.6–7）报告 F1 / AUC-PR mean±std。PCRTA 数值：WaQ .784 / .794，DSADS .943 / .960，Epilepsy .934 / .964，ASD .927 / .933，SMD .987 / .988，SWaT .978 / .996。作者称在五个数据集排名第一、ASD 排第二；Epilepsy 相对 COUTA 的提升约 13% F1 / 17% AUC-PR。（§4.2, Table 2, pp.6–7）",
      "- Epilepsy t-SNE：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。 - Synthetic mixed-anomaly case：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。 - Ablation（Table 3, p.7）：在 WaQ / DSADS / Epilepsy 上，…"
    ],
    "ablations": [
      "### 7.3 Representation、generalization 和 ablation",
      "- Epilepsy t-SNE：normal activity 与 seizure representations 大体分开，仍有少数异常点靠近 normal cluster（Fig. 3, p.7）；这是 embedding 视觉案例，不是全量分类校准。 - Synthetic mixed-anomaly case：论文将不同异常类型放入一条合成序列，比较 OCSVM、COUTA 等；作者观察 PCRTA 对不同 perturbation effects 的 score 变化更稳定（§4.4, Fig. 4, p.7）。该实验依赖合成模式与设定的 perturbation family。…"
    ],
    "robustness_generalization": [
      "### 7.3 Representation、generalization 和 ablation"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "扰动覆盖假设：六种固定扰动 / 幅度不能覆盖所有领域异常。真实异常可能是缓慢状态转换、负载峰值、周期变化或跨通道依赖变化，而不一定降低扰动分类正确率。（§3.3）",
      "Classifier pseudo-label coupling：同一学习到的分类边界既提供伪标签，又组织 contrastive positives/negatives；如果分类器系统性混淆合法正常模式，contrastive network 可能放大误分结构。（Eq. 1, §§3.3–3.4，分析推断）",
      "检测分数仍由 LOF 决定：分类误差 / perturbation confusion 不是最终 anomaly score 的直接组成；最终 score 是七种 representation 的平均 LOF。（Eq. 9）",
      "Threshold protocol：best F1 通过遍历阈值取得，含测试标签 oracle 选择；不能将报告 F1 当作不依赖标签的线上告警结果。（§4.1）",
      "事件结构：subsequence score 被赋给窗口末端，前 $l-1$ 时点补零；窗口 length / stride 会影响边界和检测延迟。（§3.1, §4.1）",
      "外部上下文缺失：输入为数值时序窗口，未使用 workload、release、Trace 或正常业务状态标签，无法解释偏离来自新正常还是故障。",
      "复现透明度：论文正文没有代码链接；已给定配置之外的 transform 随机参数、LOF 配置等仍需从 implementation / supplementary source 获取。"
    ],
    "evidence_gaps": [
      "未报告的环境属于证据不足，不等于方法能力不足"
    ]
  },
  "research_implications": [
    "- [分析推断] 以真实业务事件 / workload-conditioned perturbation 验证“分类困难度”是否跟故障相关。 - [分析推断] 对 rare-but-normal operating regime 作专门 hard negative tests，避免被扰动负样本机制当作异常。 - [分析推断] 评估 classifier calibration、pseudo-label noise、top-$k$ 和 LOF views 对 event-level detection latency / false-alert rate 的影响。 - [分析推断] 加入变量关系型扰动，检验跨通道故障而非逐变量值替换。"
  ],
  "related_papers": [
    {
      "paper_id": "triad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfmae",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
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
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, §4.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "Table 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.3–3.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, §4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§3.2–3.4, Eqs. 1–9, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "Eq. 2",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "8a1319ac26078345482d2cf48b5f88b08d63bec757b9f448e3c41a02d9146669",
    "reading_note_sha256": "4517675b76d5af1e0aa2ab398849ed4789eefccaa2f9bb003991757aa41dbf78",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "f211185b1469207df2404325a757da99b002a04689315112812ff6e91fb14e43"
  },
  "knowledge_card_path": "papers/pcrta/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
