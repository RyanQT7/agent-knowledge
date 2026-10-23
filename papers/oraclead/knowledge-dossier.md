# Knowledge Dossier — Structured Temporal Causality / OracleAD：结构化时间因果多变量时序异常检测

## 1. Basic Information

- **English title**: Structured Temporal Causality / OracleAD：结构化时间因果多变量时序异常检测
- **中文译名**：结构化时间因果：可解释的多变量时间序列异常检测
- **Authors**: Dongchan Cho, Jiho Han, Keumyeong Kang, Minsang Kim, Honggyu Ryu, Namsoon Jung
- **Venue / year / CCF**: NeurIPS 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: 结构化时间关系的可解释多变量异常检测
- **Method tags**: TSAD multivariate latent-structure LSTM MHSA stable-latent-structure prediction-error NeurIPS-2025

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 多变量时序异常检测同时考察变量自身的时间动态和变量间关系偏移。（§3, Eqs. 1–2, PDF pp.4–5）
- **[实验支持]** 在 PSM、SMD、SWaT 仅用正常训练数据学习，再对测试时刻给出分数；窗口长度 $L=10$。（§4.1, PDF p.7）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文讨论多变量时序中的两类证据：单通道随时间的动态是否异常，以及通道之间的潜在关系是否偏离。作者指出，只按 reconstruction / prediction error 检测可能漏掉原始值变化很小、但变量关系发生变化的异常；联合多变量建模也可能把异质通道的独立动态混在一起，降低局部异常敏感度和可解释性。（PDF pp.3–4, §§2.1–3.1）

令窗口为 $X=[x^1,\dots,x^L]\in\mathbb R^{N\times L}$，其中 $N$ 为变量数、$L$ 为窗口长度。模型用前 $L-1$ 个时刻编码，重构历史并预测最后向量 $x^L$，判断该末时刻是否异常。（PDF p.4, Eqs. 1–2）

题名中的 “causality” 应按论文内部操作定义理解：每通道 LSTM 的历史编码被称为 causal embedding；其后又以跨变量 MHSA 融合相关表示。SLS 实际保存的是对称的潜在嵌入距离，不是有向 Granger 图、干预效应或物理因果图；它也不单独识别故障根因。（PDF pp.4–6, Eqs. 3–12）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **异质通道的时间规律**：不同变量的基线、周期、响应速度不同，单个共享时序模型可能使其表示相互干扰。作者以独立 encoder–decoder 分支处理每个变量。（PDF p.4, §3.1）
2. **跨变量结构证据**：只有逐通道预测残差可能看不到正常值域中的关联结构变化。OracleAD 把多个变量的 latent embeddings 做 MHSA，并比较其距离结构。（PDF pp.4–6）
3. **结构评分的时序覆盖与局部精度**：单点 prediction score 灵敏但短；关系偏差能在窗口内持续，却有窗口滞后和恢复期残留。乘积融合意在兼顾两者，但会受任一分量偏小的抑制。（PDF pp.9–10, Fig. 2）
4. **评测可信度**：作者明确讨论 point-adjusted F1 等指标的局限；然而其自己的二值 F1 使用依赖测试真值的最优阈值，部署阈值问题仍未解决。（PDF pp.3, 8; Appendix D.3, p.22）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 现有统一时空模型可能混合异质变量动态；只看预测 / 重建误差可能缺少结构异常线索。（§§2.1, 3.1）
- **[分析推断]** OracleAD 的 SLS 是对称 latent distance 模板，不能等同于方向性因果图或物理根因证据；推理期固定模板也未条件化 workload / operating mode。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

OracleAD 为每个通道独立编码历史并预测下一点，通过跨通道注意力形成上下文嵌入，再以训练期每轮平均的 pairwise latent distance matrix（Stable Latent Structure, SLS）约束结构稳定性；测试时将预测误差与相对 SLS 的结构偏差相乘，实现点级异常检测并以偏差矩阵提供变量定位线索。

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：异质通道的时间规律：不同变量的基线、周期、响应速度不同，单个共享时序模型可能使其表示相互干扰。作者以独立 encoder–decoder 分支处理每个变量。（PDF p.4, §3.1）
- **C2（第4节挑战）**：跨变量结构证据：只有逐通道预测残差可能看不到正常值域中的关联结构变化。OracleAD 把多个变量的 latent embeddings 做 MHSA，并比较其距离结构。（PDF pp.4–6）
- **C3（第4节挑战）**：结构评分的时序覆盖与局部精度：单点 prediction score 灵敏但短；关系偏差能在窗口内持续，却有窗口滞后和恢复期残留。乘积融合意在兼顾两者，但会受任一分量偏小的抑制。（PDF pp.9–10, Fig. 2）
- **C4（第4节挑战）**：评测可信度：作者明确讨论 point-adjusted F1 等指标的局限；然而其自己的二值 F1 使用依赖测试真值的最优阈值，部署阈值问题仍未解决。（PDF pp.3, 8; Appendix D.3, p.22）

### 7.1 学习每变量时间摘要 $c_i$

- **作者技术描述**：**[作者主张]** 学习每变量时间摘要 $c_i$：LSTM hidden states 经时间注意力加权池化。（§3.1, Eqs. 3–5）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 跨变量注意力与双任务解码”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 对 $[c_1

- **作者技术描述**：**[作者主张]** 对 $[c_1,\ldots,c_N]$ 沿变量维使用 MHSA，形成有上下文的 $c_i^*$。（§3.1, Eqs. 6–8）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 每变量 decoder 同时重构历史、预测末点

- **作者技术描述**：**[作者主张]** 每变量 decoder 同时重构历史、预测末点，组合 prediction、reconstruction 与 SLS deviation loss。（§3.1, §3.3, Eqs. 9–14）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 跨变量注意力与双任务解码”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** 去掉重构 loss 后 Table 2 的 PSM F1/V-ROC/V-PR 从 full 65.85/84.24/68.17 降到 58.03/74.56/54.40；结构分数及 prediction 分数单独使用时优势随数据集不同。（Table 2, PDF pp.9–10）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 每 epoch 平均训练窗口的 L2 latent-distance matrix

- **作者技术描述**：**[作者主张]** 每 epoch 平均训练窗口的 L2 latent-distance matrix，得 SLS；测试时使用 $\|D_t-SLS\|_F$ 作为关系偏差。（§3.2, Eqs. 11–13, §3.4 Eq. 16）
- **对应挑战**：C3、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.5 最终异常分数为 $P_t^{score}\times D_t^{score}$

- **作者技术描述**：**[作者主张]** 最终异常分数为 $P_t^{score}\times D_t^{score}$；偏差矩阵可按行 / 列聚合候选变量。（§3.4, Eq. 17; §4.3, Fig. 3）
- **对应挑战**：C3、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.5 Inference score and localization”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
多变量窗口 X（L=10）
  ├─ 每通道独立 LSTM encoder：前 L−1 点 → 隐状态序列
  │    └─ 时间注意力池化 → 每变量 temporal / “causal” embedding c_i
  ├─ 沿通道维堆叠 C → MHSA → 上下文表示 c*_i
  ├─ 每通道 LSTM decoder → 重构历史 + 预测末点
  ├─ pairwise L2 距离矩阵 D_t 与训练期 SLS 比较 → deviation score
  └─ prediction score × deviation score → final anomaly score
```

模块依次解决通道自身的历史摘要、通道间 latent 交互、正常关系参照学习、末点检测及偏差可视化。训练和推理中的 SLS 都在 latent 表征上；它不是输入数据的 Pearson correlation matrix，也不是显式邻接矩阵。（PDF pp.4–7, Fig. 1, §§3.1–3.4）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 通道级时间编码与注意力池化

对每个变量 $i$，独立 LSTM encoder 接收 $x_i^{1:L-1}$，得到隐状态 $h_i^1,\dots,h_i^{L-1}\in\mathbb R^d$（Eq. 3）。通过线性打分 $f(h_i^\ell)=w^\top h_i^\ell+b$ 和沿时间轴 softmax 得到权重 $\alpha_i^\ell$，再加权汇聚为

$$c_i=\sum_{\ell=1}^{L-1}\alpha_i^\ell h_i^\ell. \tag{5}$$

$\alpha$ 让模型在完整历史窗口中选择对末点预测有用的时间信息；它不是异常分数或经人工标注的因果权重。编码器按通道独立，但结构训练及后续解码并非完全无跨通道信息。（PDF pp.4–5, Eqs. 3–5）

#### 6.2 跨变量注意力与双任务解码

将 $c_i$ 堆叠为 $C\in\mathbb R^{N\times d}$，使用多头 self-attention 得到 $C^*=[c_1^*,\dots,c_N^*]$（Eqs. 6–8）。每个变量 embedding 作为 query，同时以所有变量 embedding 构造 key/value；因此 $c_i^*$ 可吸收其他通道线索，论文称其捕获 soft / dynamic dependencies。这里的 attention 是学习到的表示交互，不应直接当成真实因果边。

对应通道 decoder $Dec_i$ 从 $c_i^*$ 输出历史重构 $\hat x_i^{1:L-1}$ 和下一点预测 $\hat x_i^L$（Eq. 9）。Fig. 1 标明 decoder 初始输入为全零向量。把各通道末点拼接成 $\hat x^L$（Eq. 10）。重构分支用于约束潜在表征保留窗口内动态；预测分支提供精确的末点变化证据。（PDF pp.4–5, Fig. 1, Eqs. 6–10）

#### 6.3 Stable Latent Structure（SLS）

对训练窗口 $k$ 的上下文 embedding 计算两两欧氏距离：

$$D_{ij}^{(k)}=\|c_i^{*(k)}-c_j^{*(k)}\|_2,\quad D^{(k)}\in\mathbb R^{N\times N}.\tag{11}$$

论文选 L2 距离，并在 Appendix E.4 比较 cosine / L1。每个 epoch 将该 epoch 的 $M$ 个训练窗口距离矩阵取均值：

$$SLS=\frac1M\sum_{k=1}^{M}D^{(k)}.\tag{12}$$

第一轮开始时没有先验 SLS；首个 epoch 结束后建立，第二轮起作为训练结构正则项。训练中它约束变量间距离接近累计的正常结构；推理时直接用训练得到的 SLS，不在测试过程中动态更新。（PDF pp.5–6, §3.2, Eqs. 11–13）

这是一种全局平均 latent-distance 模板。多种合法正常机制若映射到不同 latent geometry，简单均值可能削弱状态间区别；训练期模型还可能把污染或罕见正常纳入均值。论文没有按 workload / operating mode 建立多模板，也没有外部事件变量来命名各结构。

#### 6.4 Training objective

每轮得到当前 batch/window 的结构距离 $D^{(k)}$，用 prediction loss、历史 reconstruction loss 与当前距离对 SLS 的 deviation regularizer 联合优化：

$$L=L_{pred}+\lambda_{recon}L_{recon}+\lambda_{dev}L_{dev}.\tag{14}$$

其中 prediction 与 reconstruction 项为相应平方 $L_2$ 误差；结构项为当前 pairwise distance 与 SLS 的均方偏差。默认 $\lambda_{recon}=0.1$、$\lambda_{dev}=3$（PDF §3.3, Appendix D.2）。首个 epoch 尚无稳定模板，SLS 约束从第二轮起应用。训练仅用 normal training data；标准化参数由训练集 StandardScaler 拟合。（PDF p.6; Appendix C.1, p.19; Appendix D.1, p.20）

#### 6.5 Inference score and localization

对时刻 $t$ 的末点定义预测误差：

$$P_t^{score}=\frac1N\sum_{i=1}^{N}|x_i^t-\hat x_i^t|.\tag{15}$$

当前窗口内 latent pairwise distance 为 $D_t$，结构偏差分数为

$$D_t^{score}=\|D_t-SLS\|_F.\tag{16}$$

最终检测分数为

$$A_t^{score}=P_t^{score}\times D_t^{score}.\tag{17}$$

prediction score 使单点突变显著；deviation score 可能在异常进入窗口后延迟升高，并在输入窗口仍含异常恢复样本时继续偏高。作者认为乘积可以压低“结构偏差高但预测误差低”的误报，并以结构偏差补充 prediction-only 漏报；但乘积也意味着任何一个分量接近零都会压低总分，效果取决于数据集及两分量标定。（PDF pp.7, 9–10, §§3.4, 4.3, Fig. 2）

用于解释时，作者展示矩阵 $D_t^{matrix}=|D_t-SLS|$，聚合行 / 列异常强度以对变量排序。Fig. 3 的热图帮助检查 SMD 案例；Appendix G 的 Table S10 对部分代表性异常时间报告 top-3 变量与标注变量的比较。此处是候选变量定位，不等于由模型验证的物理根因；SWaT / PSM 没有同等完备的 forensic feature ground truth。（PDF pp.8–9, Fig. 3; Appendix G, pp.29–30）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (3)、Eq. (6)、Eq. (9)、Eq. (10)、Eq. (11)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.4 Training objective；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.5 Inference score and localization及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

OracleAD 为每个通道独立编码历史并预测下一点，通过跨通道注意力形成上下文嵌入，再以训练期每轮平均的 pairwise latent distance matrix（Stable Latent Structure, SLS）约束结构稳定性；测试时将预测误差与相对 SLS 的结构偏差相乘，实现点级异常检测并以偏差矩阵提供变量定位线索。

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Datasets, baselines, metrics

- **Datasets**：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A）
- **训练协议**：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19; Appendix D, p.20）
- **Baselines**：AE、OmniAnomaly、Anomaly Transformer、PatchTST、TimesNet、DLinear、NLinear、DCdetector、iTransformer、ModernTCN、SARAD、CATCH。（PDF p.7, §4.1）
- **Metrics**：point-wise F1、R-F1、Aff-F1、AUC-ROC、AUC-PR、VUS-ROC、VUS-PR。AUC / VUS 不依赖选定单一阈值；F1 系列则受阈值策略影响。（PDF p.7, §4.1）
- **Threshold caveat**：Appendix D.3 根据目标评价指标对给定候选阈值集最大化 F1 等分数，使用对应 ground-truth $y$；具体候选阈值为 score range 上 $N=200$ 等分。故表中二值 F1 属测试标签 oracle threshold 结果，不能视作部署前无标签阈值性能；AUROC / AUPRC / VUS 指标不受该二值门限选择影响。（PDF p.22, Appendix D.3）

#### 7.2 Main results

Table 1 报告 OracleAD 主要值如下（%，五 seed 平均）：

| Dataset | F1 | R-F1 | Aff-F1 | AUC-ROC | AUC-PR | VUS-ROC | VUS-PR |
|---|---:|---:|---:|---:|---:|---:|---:|
| PSM | 65.85 | 54.66 | 78.07 | 84.78 | 68.11 | 84.24 | 68.17 |
| SMD | 43.03 | 38.88 | 84.73 | 83.56 | 44.83 | 69.57 | 47.52 |
| SWaT | 76.50 | 28.15 | 71.97 | 82.71 | 72.39 | 82.42 | 74.16 |

（PDF p.8, Table 1）

作者称大部分指标最优，并强调 VUS-PR。表中并非每个指标均第一：例如 SWaT VUS-ROC 的 SARAD 为 86.30，高于 OracleAD 82.42；SWaT R-F1 的 OmniAnomaly 38.72 高于 28.15。OracleAD 在多项 threshold-independent 指标有竞争力，但不能将其结果概括为所有指标均全面领先。论文也指出 Aff-F1 在若干弱模型上仍偏高，需结合定位更严格的指标解读。（PDF p.8, Table 1, §4.2）

#### 7.3 Ablations and qualitative analysis

Table 2 中去掉 reconstruction loss 后，PSM 的 F1 / VUS-ROC / VUS-PR 从 full 的 65.85 / 84.24 / 68.17 降到 58.03 / 74.56 / 54.40；该表 SMD 的 no-reconstruction 行为 56.47 / 75.59 / 54.29，full 行为 60.19 / 80.81 / 56.63；SWaT no-reconstruction 为 76.61 / 82.92 / 71.95，full 为 76.50 / 82.42 / 74.16。（PDF pp.8–10, Tables 1–2）需要注意，Table 1 的 SMD full 行为 43.03 / 69.57 / 47.52，而 Table 2 标注 SMD 为四个子集均值，二者报告口径不一致；不应直接用不同表格计算 ablation 差值，复现时需核对 subset protocol。

- 仅用 deviation score 在 SWaT 的 F1 76.92 高于 full 76.50，但 PSM/SMD 有明显差距；单独使用 prediction score 也在不同指标 / 数据集各有强弱。Full model 并非逐格最优，作者的论证是双分数总体更平衡。（PDF pp.9–10, Table 2）
- 可视化显示短促 prediction 峰和持续 deviation 段覆盖不同异常时相；结构偏差出现窗口延迟及恢复期残留，是方法可观察的时序代价。（PDF pp.9–10, Fig. 2）
- SMD Table S10 展示多个代表性区间 top-3 排名；仅覆盖少量精选案例，且不构成全测试集的 root-cause accuracy。（Appendix G, pp.29–30）
- Appendix E 给出种子标准差，Appendix D 给出窗口长度、batch size、$\lambda_{dev}$、encoder/decoder 深度敏感性；默认 batch=1024、$\lambda_{dev}=3$、encoder/decoder 两层。窗口 10 / 20 多数表现稳定，过大窗口可能稀释局部异常。（Appendix D.2, pp.20–21）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：9. Limitations — 作者明确指出

作者在 Appendix I 指出，SLS 假设连续值输入下存在全局稳定的变量关系；异构子系统或混合连续 / 离散传感器（如 SWaT）可能削弱偏差矩阵的区分能力。未来工作包括变量类型无关方法与推理时动态更新 SLS。（PDF p.31, Appendix I）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

全局固定 SLS 对动态负载、发布、扩缩容切换的合法结构变化可能报高分；论文提出动态 SLS future work，但未将业务上下文作为条件变量，也没有测其与故障并发时的安全更新策略。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

SLS 的对称 latent distance 与 MHSA 依赖提供结构偏离提示，但它既没有方向性也不验证干预关系；用 “root cause” 需限定为候选变量排序。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

乘积融合抑制单侧误差也可能压制单模态有效信号：若关系异常时预测误差很小，或正常关系偶然变化时预测分数较小，偏差证据可能被压低；该风险宜通过可控合成实验检验。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

若正常状态呈多模态分布，单一均值距离矩阵会丢失模式条件；可比较状态条件 SLS / 多模板、在线变点门控与固定模板，并控制异常污染。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：9. Limitations — 论文实验支持的限制

deviation score 需要异常先进入长度 $L$ 的窗口，因而有 detection lag；窗口包含异常恢复历史时可在恢复期产生 false positive。（PDF pp.9–10）

#### 精读笔记原章节：9. Limitations — 论文实验支持的限制

诊断案例量有限，SMD 是代表性变量定位分析；注意力与 latent distance 不足以证明根因因果。（PDF p.8, Fig. 3; Appendix G）

#### 精读笔记原章节：9. Limitations — 论文实验支持的限制

SMD Table 1 / Table 2 的点值结果来自不同报告口径，不能从不同表格直接对比 ablation 变化。（PDF pp.8–10）

#### 精读笔记原章节：9. Limitations — 论文实验支持的限制

F1 最优阈值基于测试真值选出；部署时阈值如何在无标签条件下定标并未回答。（Appendix D.3）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 比较单一 SLS、多模板 SLS 与 context-conditioned SLS，并以负载 / 发布标注核验合法状态切换。
- **[分析推断]** 设计“正常负载切换 + 同时注入故障”的控制实验，评估结构更新的污染、回滚及检测延迟。
- **[分析推断]** 将偏差矩阵与已知拓扑、Trace、故障注入根因做定量验证，避免把 latent relation 等同于因果解释。
- **[分析推断]** 比较乘积、校准加和或门控融合在单侧异常证据场景下的漏报风险，并使用独立 validation / 固定门限报告运行代价。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **GCAD**：都比较测试期结构证据与正常结构参照；GCAD 是从逐目标预测误差梯度导出的有向 Granger predictive influence 图，OracleAD 是对称的 MHSA latent pairwise distance。两者不能统称为同一种 causal graph。
- **CAROTS**：按估计 Granger 图构造因果保持 / 破坏增强及预测分数；OracleAD 的 attention latent relation 不承担图真值或干预语义。
- **SARAD**：从 attention map 的空间关联下降及其时间 progression 检测，显式解释通道贡献；OracleAD 检测 latent distance template 偏移。两者均使用关系证据，但所观察对象、聚合方式和 anomaly score 不同。
- **CCM-TAD**：其 “causal” 指时间 mixer 的 future mask；OracleAD 则以历史编码和下一点预测建模时间依赖，再对通道 latent 距离建模结构。
- **Graph-MoE**：Graph-MoE 用图卷积层级表示与 memory router；OracleAD 的 SLS 是全局 pairwise distance baseline，而非历史状态路由器。
- **When Model Meets New Normals**：后者推理期适应新 normal；OracleAD 推理时冻结 SLS，动态结构更新仅列为 future work。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.3–4, §§2.1–3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.4, Eqs. 1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–6, Eqs. 3–12 | 精读笔记保留的原文定位 |
| Research problem / scenario | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–5, §3, Eqs. 1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.7, §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.4, §3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–6 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.9–10, Fig. 2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | §§2.1 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–7, §§3.1–3.4, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | Eq. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–5, Eqs. 3–5 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | Eqs. 6–8 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–5, Eq. 9, Eq. 10, Eqs. 6–10, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.5–6, §3.2, Eqs. 11–13 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.6, §3.3 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.7, §§3.4, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.8–9, Fig. 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.7, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.7 | 精读笔记保留的原文定位 |
| Experimental evidence | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.22 | 精读笔记保留的原文定位 |
| Experimental evidence | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.8, Table 1 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "oraclead",
  "title_en": "Structured Temporal Causality / OracleAD：结构化时间因果多变量时序异常检测",
  "title_zh": "结构化时间因果：可解释的多变量时间序列异常检测",
  "authors": [
    "Dongchan Cho",
    "Jiho Han",
    "Keumyeong Kang",
    "Minsang Kim",
    "Honggyu Ryu",
    "Namsoon Jung"
  ],
  "year": 2025,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/NeurIPS/Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/oraclead/notes.md",
  "code_url": null,
  "research_area": "结构化时间关系的可解释多变量异常检测",
  "method_tags": [
    "TSAD multivariate latent-structure LSTM MHSA stable-latent-structure prediction-error NeurIPS-2025"
  ],
  "research_scenario": "- [作者主张] 多变量时序异常检测同时考察变量自身的时间动态和变量间关系偏移。（§3, Eqs. 1–2, PDF pp.4–5） - [实验支持] 在 PSM、SMD、SWaT 仅用正常训练数据学习，再对测试时刻给出分数；窗口长度 $L=10$。（§4.1, PDF p.7）",
  "research_problem": "论文讨论多变量时序中的两类证据：单通道随时间的动态是否异常，以及通道之间的潜在关系是否偏离。作者指出，只按 reconstruction / prediction error 检测可能漏掉原始值变化很小、但变量关系发生变化的异常；联合多变量建模也可能把异质通道的独立动态混在一起，降低局部异常敏感度和可解释性。（PDF pp.3–4, §§2.1–3.1） 令窗口为 $X=[x^1,\\dots,x^L]\\in\\mathbb R^{N\\times L}$，其中 $N$ 为变量数、$L$ 为窗口长度。模型用前 $L-1$ 个时刻编码，重构历史并预测最后向量 $x^L$，判断该末时刻是否异常。（PDF p.4, Eqs. 1–2） 题名中的 “causality” 应按论文内部操作定义理解：每通道 LSTM 的历史编码被称为 causal embedding；其后又以跨变量 MHSA 融合相关表示。SLS 实际保存的是对称的潜在嵌入距离，不是有向 Granger 图、干预效应或物理因果图；它也不单独识别故障根因。（PDF pp.4–6, Eqs. 3–12）",
  "core_challenges": [
    "异质通道的时间规律：不同变量的基线、周期、响应速度不同，单个共享时序模型可能使其表示相互干扰。作者以独立 encoder–decoder 分支处理每个变量。（PDF p.4, §3.1）",
    "跨变量结构证据：只有逐通道预测残差可能看不到正常值域中的关联结构变化。OracleAD 把多个变量的 latent embeddings 做 MHSA，并比较其距离结构。（PDF pp.4–6）",
    "结构评分的时序覆盖与局部精度：单点 prediction score 灵敏但短；关系偏差能在窗口内持续，却有窗口滞后和恢复期残留。乘积融合意在兼顾两者，但会受任一分量偏小的抑制。（PDF pp.9–10, Fig. 2）",
    "评测可信度：作者明确讨论 point-adjusted F1 等指标的局限；然而其自己的二值 F1 使用依赖测试真值的最优阈值，部署阈值问题仍未解决。（PDF pp.3, 8; Appendix D.3, p.22）"
  ],
  "existing_method_limits": [
    "[作者主张] 现有统一时空模型可能混合异质变量动态；只看预测 / 重建误差可能缺少结构异常线索。（§§2.1, 3.1）",
    "[分析推断] OracleAD 的 SLS 是对称 latent distance 模板，不能等同于方向性因果图或物理根因证据；推理期固定模板也未条件化 workload / operating mode。"
  ],
  "core_idea": "OracleAD 为每个通道独立编码历史并预测下一点，通过跨通道注意力形成上下文嵌入，再以训练期每轮平均的 pairwise latent distance matrix（Stable Latent Structure, SLS）约束结构稳定性；测试时将预测误差与相对 SLS 的结构偏差相乘，实现点级异常检测并以偏差矩阵提供变量定位线索。",
  "technical_innovations": [
    {
      "name": "学习每变量时间摘要 $c_i$",
      "author_claim": "**[作者主张]** 学习每变量时间摘要 $c_i$：LSTM hidden states 经时间注意力加权池化。（§3.1, Eqs. 3–5）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 跨变量注意力与双任务解码",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 学习每变量时间摘要 $c_i$：LSTM hidden states 经时间注意力加权池化。（§3.1, Eqs. 3–5）"
    },
    {
      "name": "对 $[c_1",
      "author_claim": "**[作者主张]** 对 $[c_1,\\ldots,c_N]$ 沿变量维使用 MHSA，形成有上下文的 $c_i^*$。（§3.1, Eqs. 6–8）",
      "challenge_ids": [
        "C2",
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
      "source_locator": "**[作者主张]** 对 $[c_1,\\ldots,c_N]$ 沿变量维使用 MHSA，形成有上下文的 $c_i^*$。（§3.1, Eqs. 6–8）"
    },
    {
      "name": "每变量 decoder 同时重构历史、预测末点",
      "author_claim": "**[作者主张]** 每变量 decoder 同时重构历史、预测末点，组合 prediction、reconstruction 与 SLS deviation loss。（§3.1, §3.3, Eqs. 9–14）",
      "challenge_ids": [
        "C1",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 跨变量注意力与双任务解码",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** 去掉重构 loss 后 Table 2 的 PSM F1/V-ROC/V-PR 从 full 65.85/84.24/68.17 降到 58.03/74.56/54.40；结构分数及 prediction 分数单独使用时优势随数据集不同。（Table 2, PDF pp.9–10）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 每变量 decoder 同时重构历史、预测末点，组合 prediction、reconstruction 与 SLS deviation loss。（§3.1, §3.3, Eqs. 9–14）"
    },
    {
      "name": "每 epoch 平均训练窗口的 L2 latent-distance matrix",
      "author_claim": "**[作者主张]** 每 epoch 平均训练窗口的 L2 latent-distance matrix，得 SLS；测试时使用 $\\|D_t-SLS\\|_F$ 作为关系偏差。（§3.2, Eqs. 11–13, §3.4 Eq. 16）",
      "challenge_ids": [
        "C3",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 每 epoch 平均训练窗口的 L2 latent-distance matrix，得 SLS；测试时使用 $\\|D_t-SLS\\|_F$ 作为关系偏差。（§3.2, Eqs. 11–13, §3.4 Eq. 16）"
    },
    {
      "name": "最终异常分数为 $P_t^{score}\\times D_t^{score}$",
      "author_claim": "**[作者主张]** 最终异常分数为 $P_t^{score}\\times D_t^{score}$；偏差矩阵可按行 / 列聚合候选变量。（§3.4, Eq. 17; §4.3, Fig. 3）",
      "challenge_ids": [
        "C3",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.5 Inference score and localization",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 最终异常分数为 $P_t^{score}\\times D_t^{score}$；偏差矩阵可按行 / 列聚合候选变量。（§3.4, Eq. 17; §4.3, Fig. 3）"
    }
  ],
  "methodology": {
    "architecture": "text 多变量窗口 X（L=10） ├─ 每通道独立 LSTM encoder：前 L−1 点 → 隐状态序列 │ └─ 时间注意力池化 → 每变量 temporal / “causal” embedding ci ├─ 沿通道维堆叠 C → MHSA → 上下文表示 ci ├─ 每通道 LSTM decoder → 重构历史 + 预测末点 ├─ pairwise L2 距离矩阵 Dt 与训练期 SLS 比较 → deviation score └─ prediction score × deviation score → final anomaly score 模块依次解决通道自身的历史摘要、通道间 latent 交互、正常关系参照学习、末点检测及偏差可视化。训练和推理中的 SLS 都在 latent 表征上；它不是输入数据的 Pearson correlation matrix，也不是显式邻接矩阵。（PDF pp.4–7, Fig. 1, §§3.1–3.4）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 通道级时间编码与注意力池化",
      "6.2 跨变量注意力与双任务解码",
      "6.3 Stable Latent Structure（SLS）",
      "6.4 Training objective",
      "6.5 Inference score and localization"
    ],
    "key_formulas": [
      "Eq. (3)",
      "Eq. (6)",
      "Eq. (9)",
      "Eq. (10)",
      "Eq. (11)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "OracleAD 为每个通道独立编码历史并预测下一点，通过跨通道注意力形成上下文嵌入，再以训练期每轮平均的 pairwise latent distance matrix（Stable Latent Structure, SLS）约束结构稳定性；测试时将预测误差与相对 SLS 的结构偏差相乘，实现点级异常检测并以偏差矩阵提供变量定位线索。"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets, baselines, metrics",
      "- Datasets：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A） - 训练协议：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19;…",
      "| Dataset | F1 | R-F1 | Aff-F1 | AUC-ROC | AUC-PR | VUS-ROC | VUS-PR | |---|---:|---:|---:|---:|---:|---:|---:| | PSM | 65.85 | 54.66 | 78.07 | 84.78 | 68.11 | 84.24 | 68.17 | | SMD | 43.03 | 38.88 | 84.73 | 83.56 | 44.83 | 69.57 | 47.52 | | SWaT | 76.50 | 28.15 | 71.97 | 82.71 | 72.39 | 82.42 | 74.16 |",
      "- 仅用 deviation score 在 SWaT 的 F1 76.92 高于 full 76.50，但 PSM/SMD 有明显差距；单独使用 prediction score 也在不同指标 / 数据集各有强弱。Full model 并非逐格最优，作者的论证是双分数总体更平衡。（PDF pp.9–10, Table 2） - 可视化显示短促 prediction 峰和持续 deviation 段覆盖不同异常时相；结构偏差出现窗口延迟及恢复期残留，是方法可观察的时序代价。（PDF pp.9–10, Fig. 2） - SMD Table S10 展示多个代表性区间 top-3 排名；仅覆盖少量精选案例，…"
    ],
    "baselines": [
      "### 7.1 Datasets, baselines, metrics",
      "- Datasets：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A） - 训练协议：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19;…"
    ],
    "metrics": [
      "### 7.1 Datasets, baselines, metrics",
      "- Datasets：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A） - 训练协议：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19;…",
      "| Dataset | F1 | R-F1 | Aff-F1 | AUC-ROC | AUC-PR | VUS-ROC | VUS-PR | |---|---:|---:|---:|---:|---:|---:|---:| | PSM | 65.85 | 54.66 | 78.07 | 84.78 | 68.11 | 84.24 | 68.17 | | SMD | 43.03 | 38.88 | 84.73 | 83.56 | 44.83 | 69.57 | 47.52 | | SWaT | 76.50 | 28.15 | 71.97 | 82.71 | 72.39 | 82.42 | 74.16 |",
      "作者称大部分指标最优，并强调 VUS-PR。表中并非每个指标均第一：例如 SWaT VUS-ROC 的 SARAD 为 86.30，高于 OracleAD 82.42；SWaT R-F1 的 OmniAnomaly 38.72 高于 28.15。OracleAD 在多项 threshold-independent 指标有竞争力，但不能将其结果概括为所有指标均全面领先。论文也指出 Aff-F1 在若干弱模型上仍偏高，需结合定位更严格的指标解读。（PDF p.8, Table 1, §4.2）"
    ],
    "main_results": [
      "### 7.2 Main results",
      "Table 1 报告 OracleAD 主要值如下（%，五 seed 平均）：",
      "（PDF p.8, Table 1）",
      "作者称大部分指标最优，并强调 VUS-PR。表中并非每个指标均第一：例如 SWaT VUS-ROC 的 SARAD 为 86.30，高于 OracleAD 82.42；SWaT R-F1 的 OmniAnomaly 38.72 高于 28.15。OracleAD 在多项 threshold-independent 指标有竞争力，但不能将其结果概括为所有指标均全面领先。论文也指出 Aff-F1 在若干弱模型上仍偏高，需结合定位更严格的指标解读。（PDF p.8, Table 1, §4.2）",
      "Table 2 中去掉 reconstruction loss 后，PSM 的 F1 / VUS-ROC / VUS-PR 从 full 的 65.85 / 84.24 / 68.17 降到 58.03 / 74.56 / 54.40；该表 SMD 的 no-reconstruction 行为 56.47 / 75.59 / 54.29，full 行为 60.19 / 80.81 / 56.63；SWaT no-reconstruction 为 76.61 / 82.92 / 71.95，full 为 76.50 / 82.42 / 74.16。（PDF pp.8–10, Tables 1–2）需要注意，Table 1 的 SMD full 行为 43.03 / 69.57 / 47.52，…"
    ],
    "ablations": [
      "### 7.3 Ablations and qualitative analysis",
      "Table 2 中去掉 reconstruction loss 后，PSM 的 F1 / VUS-ROC / VUS-PR 从 full 的 65.85 / 84.24 / 68.17 降到 58.03 / 74.56 / 54.40；该表 SMD 的 no-reconstruction 行为 56.47 / 75.59 / 54.29，full 行为 60.19 / 80.81 / 56.63；SWaT no-reconstruction 为 76.61 / 82.92 / 71.95，full 为 76.50 / 82.42 / 74.16。（PDF pp.8–10, Tables 1–2）需要注意，…",
      "- 仅用 deviation score 在 SWaT 的 F1 76.92 高于 full 76.50，但 PSM/SMD 有明显差距；单独使用 prediction score 也在不同指标 / 数据集各有强弱。Full model 并非逐格最优，作者的论证是双分数总体更平衡。（PDF pp.9–10, Table 2） - 可视化显示短促 prediction 峰和持续 deviation 段覆盖不同异常时相；结构偏差出现窗口延迟及恢复期残留，是方法可观察的时序代价。（PDF pp.9–10, Fig. 2） - SMD Table S10 展示多个代表性区间 top-3 排名；仅覆盖少量精选案例，…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "- Datasets：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A） - 训练协议：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19;…"
    ]
  },
  "limitations": {
    "author_stated": [
      "作者在 Appendix I 指出，SLS 假设连续值输入下存在全局稳定的变量关系；异构子系统或混合连续 / 离散传感器（如 SWaT）可能削弱偏差矩阵的区分能力。未来工作包括变量类型无关方法与推理时动态更新 SLS。（PDF p.31, Appendix I）"
    ],
    "reasoned_inference": [
      "全局固定 SLS 对动态负载、发布、扩缩容切换的合法结构变化可能报高分；论文提出动态 SLS future work，但未将业务上下文作为条件变量，也没有测其与故障并发时的安全更新策略。",
      "SLS 的对称 latent distance 与 MHSA 依赖提供结构偏离提示，但它既没有方向性也不验证干预关系；用 “root cause” 需限定为候选变量排序。",
      "乘积融合抑制单侧误差也可能压制单模态有效信号：若关系异常时预测误差很小，或正常关系偶然变化时预测分数较小，偏差证据可能被压低；该风险宜通过可控合成实验检验。",
      "若正常状态呈多模态分布，单一均值距离矩阵会丢失模式条件；可比较状态条件 SLS / 多模板、在线变点门控与固定模板，并控制异常污染。"
    ],
    "evidence_gaps": [
      "deviation score 需要异常先进入长度 $L$ 的窗口，因而有 detection lag；窗口包含异常恢复历史时可在恢复期产生 false positive。（PDF pp.9–10）",
      "诊断案例量有限，SMD 是代表性变量定位分析；注意力与 latent distance 不足以证明根因因果。（PDF p.8, Fig. 3; Appendix G）",
      "SMD Table 1 / Table 2 的点值结果来自不同报告口径，不能从不同表格直接对比 ablation 变化。（PDF pp.8–10）",
      "F1 最优阈值基于测试真值选出；部署时阈值如何在无标签条件下定标并未回答。（Appendix D.3）"
    ]
  },
  "research_implications": [
    "- [分析推断] 比较单一 SLS、多模板 SLS 与 context-conditioned SLS，并以负载 / 发布标注核验合法状态切换。 - [分析推断] 设计“正常负载切换 + 同时注入故障”的控制实验，评估结构更新的污染、回滚及检测延迟。 - [分析推断] 将偏差矩阵与已知拓扑、Trace、故障注入根因做定量验证，避免把 latent relation 等同于因果解释。 - [分析推断] 比较乘积、校准加和或门控融合在单侧异常证据场景下的漏报风险，并使用独立 validation / 固定门限报告运行代价。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "carots",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "gcad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "oraclead",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "sarad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "ccm-tad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "graph-moe",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–4, §§2.1–3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.4, Eqs. 1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–6, Eqs. 3–12",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–5, §3, Eqs. 1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.7, §4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.4, §3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.9–10, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–7, §§3.1–3.4, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "Eq. 3",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "32cb0c53382bb0b8137382d04413a68135d5d6f583f4f1dd9674a6e976e9e305",
    "reading_note_sha256": "453e0ec475ca792557410003363a7e3f72a09e9e2e7359d1d76c86d74dc071af",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "2893ebe9470c5dd61f5668aa4e07abf34155d8571f266f0b364954268adea711"
  },
  "knowledge_card_path": "papers/oraclead/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
