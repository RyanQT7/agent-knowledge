# Knowledge Dossier — SARAD: Spatial Association-Aware Anomaly Detection and Diagnosis for Multivariate Time Series

## 1. Basic Information

- **English title**: SARAD: Spatial Association-Aware Anomaly Detection and Diagnosis for Multivariate Time Series
- **中文译名**：面向多变量时间序列异常检测与诊断的空间关联感知方法
- **Authors**: Zhihao Dai, Ligang He, Shuang-Hua Yang, Matthew Leeke
- **Venue / year / CCF**: NeurIPS 2024 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/daidahao/SARAD/
- **Research area**: 多变量变量关联演进与异常诊断
- **Method tags**: TSAD multivariate association-reduction attention spatial-progression anomaly-diagnosis NeurIPS-2024

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督多变量时序检测和特征级诊断，重点捕获异常时变量间空间关联下降（Spatial Association Reduction, SAR）。（§§1, 3, PDF pp.2–4）
- **[作者定义]** spatial 指 multivariate feature/channel 维度，不指地理空间。（§2, PDF p.4）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

SARAD 面向无监督 multivariate time-series anomaly detection（MTSAD）和 feature-level diagnosis。作者指出，常见 temporal detectors 主要根据预测 / 重建残差测量时间新颖性，却可能遗漏跨变量依赖变化；仅考虑多变量相关性的图模型也可能把预测误差作为唯一检测证据。论文提出观察：异常期间原本存在的空间关联（作者定义为多变量特征维度上的关联，不是地理空间）可能减弱，称为 **Spatial Association Reduction (SAR)**。（PDF pp.2–4, §§1–3）

检测目标为每时刻异常标签 $y_t$；诊断目标为时刻 $t$ 的异常特征集合 $g_t\subseteq[N]$。（PDF p.4, §3）

需要保留定义边界：模型读取 Transformer 的 attention association map，并将其变化视作 learned reconstruction association reduction。该 map 是模型内部信息流 / 重建依赖，不等于 ground-truth Pearson correlation、Granger graph、已知系统拓扑或干预因果图；诊断是基于检测分数得到 feature ranking。（PDF pp.5–6, §§3.2–3.3, Eq. 6）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **异常空间位置与时间位置并不相同**：异常点可以由受影响少数变量引起，纯时间建模难以定位通道。（PDF pp.3–4, §2）
2. **正常也会出现 association reduction**：若直接把注意力关系下降全判异常，会将无害变化计入；SARAD 以 progression reconstruction residual 对“常见下降”做正常性建模。（PDF p.6, §3.3）
3. **短异常与窗口聚合冲突**：使用半窗口前后比较有利于检测关系演进，但长窗口会稀释短异常。（PDF pp.7, 21, Appendix E.2 / H）
4. **诊断标签不完整**：SMD 有 forensic feature labels；SWaT、HAI 多标攻击来源而不是完整异常变量集合，诊断指标受标注语义影响。（PDF p.8, §4.2; Appendix E.3, p.21）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 纯 temporal 方法可能缺少跨变量关联，单独使用 GDN 式 prediction error 也无法充分利用 spatial 信息。（§§1–2, PDF pp.2–4）
- **[分析推断]** attention map 是网络内部关联 / 重建依赖，不能直接解释为真实相关、Granger 因果、系统拓扑或故障根因。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

SARAD 将多变量窗口分成前后两个子序列，经 encoder-only Transformer 读取变量维（论文称 spatial）的 MHSA 关联矩阵，提取关联随时间下降的 column-wise progression；用 MLP 重建该 progression 以过滤正常下降，再将数据重建误差和 progression 重建误差标准化后相加，兼做异常检测与变量级候选诊断。

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：异常空间位置与时间位置并不相同：异常点可以由受影响少数变量引起，纯时间建模难以定位通道。（PDF pp.3–4, §2）
- **C2（第4节挑战）**：正常也会出现 association reduction：若直接把注意力关系下降全判异常，会将无害变化计入；SARAD 以 progression reconstruction residual 对“常见下降”做正常性建模。（PDF p.6, §3.3）
- **C3（第4节挑战）**：短异常与窗口聚合冲突：使用半窗口前后比较有利于检测关系演进，但长窗口会稀释短异常。（PDF pp.7, 21, Appendix E.2 / H）
- **C4（第4节挑战）**：诊断标签不完整：SMD 有 forensic feature labels；SWaT、HAI 多标攻击来源而不是完整异常变量集合，诊断指标受标注语义影响。（PDF p.8, §4.2; Appendix E.3, p.21）

### 7.1 Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association

- **作者技术描述**：**[作者主张]** Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association maps。（§3.2, Eq. 1）
- **对应挑战**：C4、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Association progression extraction”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 前后子窗关联图的非负差 $S_h^l=ReLU

- **作者技术描述**：**[作者主张]** 前后子窗关联图的非负差 $S_h^l=ReLU(A^l_{1,h}-A^l_{2,h})$ 提取关联下降。（§3.3, Eq. 2）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 聚合最终层每个 attention head 的 column sum

- **作者技术描述**：**[作者主张]** 聚合最终层每个 attention head 的 column sum，形成 $S\in\mathbb R^{H\times N}$，统计某个 source feature 对其他特征重建贡献的下降。（§3.3, Eq. 3）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 用两层 MLP 重建 $S$

- **作者技术描述**：**[作者主张]** 用两层 MLP 重建 $S$；训练目标 $L=\|\hat X-X\|^2+\lambda_{LS}\|\hat S-S\|^2$，stop-gradient 防止 progression loss 改写 association representation。（§3.4, Eq. 4）
- **对应挑战**：C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.5 检测分数为验证集标准化的 data residual 与 progression residual 之和

- **作者技术描述**：**[作者主张]** 检测分数为验证集标准化的 data residual 与 progression residual 之和；主诊断公式是 per-feature data reconstruction residual。（Eqs. 5–6）
- **对应挑战**：C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Association progression extraction”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**证据边界**：主诊断分数为 per-feature data reconstruction error，空间 progression 主要参与全局检测分数；它不是 attention edge causality-based diagnosis。（Eq. 6）

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
输入窗口 X ∈ R^(2W×N)
  ├─ 沿时间一分为二：X1、X2
  ├─ 每个子窗转置为变量为 token：Linear(Xiᵀ) + learnable feature embedding M
  ├─ Encoder-only Transformer 沿变量维 MHSA 编码 / 重构
  │    └─ 各层各头输出 association map A^l_{i,h}
  ├─ 最后一层两子窗：S^l_h = ReLU(A^l_{1,h} − A^l_{2,h})
  ├─ 每个 head 对 association progression 做 column sum → S ∈ R^(H×N)
  ├─ MLP 重构 S → Ŝ，用 ||S−Ŝ||² 量化罕见关联下降
  └─ 标准化 data reconstruction error r 和 progression error p 后相加 → s
```

数据重建 Transformer 与 spatial progression MLP 端到端联合训练；stop-gradient 阻断 $S$ 的梯度回流数据模块。检测使用全局 scalar score；主文诊断公式使用逐特征数据 reconstruction residual。（PDF pp.5–7, Fig. 1, Table 1, Eqs. 1–6）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 Spatial data reconstruction

输入窗口 $X\in\mathbb R^{2W\times N}$，其中 $N$ 是特征数。先切成前后各 $W$ 点的 $X_1,X_2\in\mathbb R^{W\times N}$。每个 subseries 分别转置并线性投影：$E_i=Linear(X_i^T)\in\mathbb R^{N\times D}$，再叠加可学习 feature-level embedding $M=\{m_i\in\mathbb R^D\}$ 得到变量 token 表示。（PDF pp.5–6, §3.2）

多层 encoder-only Transformer 沿变量 token 做 MHSA。第 $l$ 层为

$$Z_i^l=LN(MHSA(X_i^{l-1})+X_i^{l-1}),\quad X_i^l=LN(MLP(Z_i^l)+Z_i^l).\tag{1}$$

每个 head 的 association map $A_{i,h}^l\in\mathbb R^{N\times N}$：行 $j$ 上对 key $k$ 的注意力权重描述第 $j$ 个特征表示从第 $k$ 个特征读取的信息；从重建角度看，作者将列 $k$ 理解为原始 feature $k$ 对所有 feature 重建的贡献。最终层输出线性投影并转置为重建序列 $\hat X_i\in\mathbb R^{W\times N}$，前后两部分拼成 $\hat X$。（PDF pp.5–6, §3.2, Eq. 1）

#### 6.2 Association progression extraction

对每个 Transformer 层 $l$、注意力 head $h$，定义前后子序列 attention map 的非负反向差：

$$S_h^l=ReLU(A_{1,h}^l-A_{2,h}^l).\tag{2}$$

该操作只保留“前半关联强于后半”的下降方向。作者观察异常可能瓦解已有空间关联，因此聚焦 reduction，而不把增加与下降对称看待。

只取最终编码层 $L$ 的 progression，之后按 head 做 column sum 得到 $S\in\mathbb R^{H\times N}$：

$$S=\left\{\sum_{j=1}^{N}S_{h,(j,k)}^L\mid h\in[H], k\in[N]\right\}.\tag{3}$$

每列对应输入特征 $k$ 对其他变量重建的贡献，列和近似该特征关联贡献下降总量。作者认为列聚合比行聚合更能凸显 anomalous-feature association dropout；Table 5 的替代行和实验总体支持此选择，但 PSM 的部分指标行和略高，不能说 column sum 对每个数据集 / 指标均优。（PDF pp.6, 10, §3.3, Table 5）

#### 6.3 Progression reconstruction filters benign reductions

将 $S$ 展平，输入两层 MLP 得到重构并 reshape 为 $\hat S\in\mathbb R^{H\times N}$。直观上，attention association reduction 本身不是异常标签；如果某种下降模式可由训练正常数据中的 progression autoencoder 重建，则其重构误差较小；罕见 / 异常下降可能产生较大 $\|\hat S-S\|^2$。（PDF p.6, §3.3）

#### 6.4 Joint objective and score

数据分支重构损失、progression 分支重构损失和联合目标为

$$L_R=\|\hat X-X\|_2^2,\quad L_S=\|\hat S-S\|_2^2,\quad L=L_R+\lambda_{LS}L_S.\tag{4}$$

从 $S$ 到 Transformer 数据模块的 gradient 被 stop，防止 progression loss 改写原始 association map 并发生表示塌缩。两个分支同步训练，分别学习原始数据重建和 association-progression normality。（PDF p.6, §3.4, Eq. 4）

输入窗口的检测分数由两种残差分别按验证集均值 / 标准差标准化，再相加：

$$r=\|\hat X-X\|_2^2,\quad p=\|\hat S-S\|_2^2,\quad s=\frac{r-\mu_r}{\sigma_r}+\frac{p-\mu_p}{\sigma_p}.\tag{5}$$

验证集用于 score 归一化（均值、标准差）和训练超参选择；论文并不把归一化后的分数称为概率。主文诊断 criterion 是第 $j$ 个变量在重建数据上的误差：

$$s_j=r_j=\|\hat X(j,\cdot)-X(j,\cdot)\|_2^2.\tag{6}$$

因此检测联合两类证据，主要诊断分数却不是 progression 的变量级 residual。Appendix D 测试 alternate joint diagnosis criterion（加上 progression）；未证明始终更好。（PDF p.7, Eqs. 5–6; Appendix D, pp.11–12）

#### 6.5 训练流程及配置

训练集均为 unlabeled normal data；训练集按时间切分 80% train / 20% validation。先对数据分支在 validation reconstruction loss 上用 TPE 选择 encoder 层数 $L\in\{3,5\}$ 和 learning rate $10^{-4}$ 到 $10^{-2}$；再用 TPE 选 $\lambda_{LS}\in[10^{-2},10^2]$。默认窗口 $2W=100$、每层 8 heads、attention dimension 512、FFN dimension 2048、progression hidden dimension 64；Adam，每 epoch 学习率减半，共 3 epochs。（Appendix F, PDF p.22）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (4)、Eq. (5)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.4 Joint objective and score；6.5 训练流程及配置；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.4 Joint objective and score及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

SARAD 将多变量窗口分成前后两个子序列，经 encoder-only Transformer 读取变量维（论文称 spatial）的 MHSA 关联矩阵，提取关联随时间下降的 column-wise progression；用 MLP 重建该 progression 以过滤正常下降，再将数据重建误差和 progression 重建误差标准化后相加，兼做异常检测与变量级候选诊断。

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Datasets and metrics

四个公开基准：SMD（38 features）、PSM（25）、SWaT（51）、HAI（79）。训练集只含无标签数据，测试集带异常 labels。Table 2 的训练 / 测试点数分别为 SMD 708,405 / 708,420，PSM 132,481 / 87,841，SWaT 496,800 / 449,919，HAI 921,603 / 402,005；异常比例 4.16%、27.73%、12.02%、2.23%。异常持续时间差异明显：中位长度 SMD 11、PSM 5、SWaT 447、HAI 162。（PDF pp.7, 21, Table 2; Appendix E.2）

Detection 报告 threshold-independent range-based AUC-ROC / AUC-PR 及 VUS-ROC / VUS-PR；五次 seed 平均。Baselines 包含 IF、DIF、USAD、GDN、MAD-GAN、DiffAD、TranAD、ATF-UAD、Anomaly Transformer、DCdetector。诊断在有标签数据集上使用 HR、NDCG 和 IPS；标注完整性因数据集而异。（PDF pp.7–9, §§4.1–4.2）

#### 7.2 Detection results

Table 3 的 SARAD 四指标（AUROC / AUPRC / VUS-ROC / VUS-PR，%）：

| Dataset | AUROC | AUPRC | VUS-ROC | VUS-PR |
|---|---:|---:|---:|---:|
| SMD | 79.97 | 15.09 | 79.67 | 15.02 |
| PSM | 61.87 | 41.06 | 61.77 | 41.01 |
| SWaT | 88.29 | 72.90 | 87.52 | 70.68 |
| HAI | 96.87 | 67.78 | 96.17 | 64.70 |

作者称 SMD 的 VUS-ROC 比 MAD-GAN 高 15.51 个百分点、HAI 比 DiffAD 高 9.92 点；PSM 比 GDN 低 1.36 点、SWaT 比 DIF 低 0.36 点，显示其为领先或相近而非全数据集完全领先。（PDF p.8, Table 3, §4.2）

Appendix E.2 说明 SMD、PSM 的异常较短，SARAD 半窗聚合可能稀释短异常；这和其使用空间关系而不是局部 temporal detector 的收益—代价相对应。（PDF pp.8, 21）

#### 7.3 Diagnosis results

Table 4 报告点级 HR@100/150、NDCG@100/150 和范围级 IPS@100/150。SARAD 的 HR@150 / NDCG@150 / IPS@150：SMD 71.93 / 69.78 / 76.44；SWaT 12.83 / 11.65 / 54.34；HAI 12.10 / 10.16 / 14.07。（PDF p.9, Table 4）

相对增益需结合标签含义看：SMD 为 forensic anomalous features；SWaT / HAI 只标攻击来源，有的攻击失败，攻击源也不一定呈现异常，且全体异常变量可能未标全。因此 SWaT / HAI 的低 HR/NDCG 既反映模型排序，也受监督标签不完整影响，不能只按数字归结为检测算法能力。（PDF p.8, §4.2; Appendix E.3, p.21）

#### 7.4 Ablations and operational cost

- Table 5：去掉 ReLU 后 SMD VUS-ROC/VUS-PR 从 79.67/15.02 降至 75.16/12.35，支持专注 association reduction；将 column sum 改 row sum 后部分性能小幅变动且并非所有指标都差；完全不聚合（no sum）会显著退化，例如 SMD AUROC / AUPRC 79.97/15.09 → 57.31/6.09。将 $S$ 直接作为异常证据（不经 MLP reconstruction）只在 SMD 部分项更好，在其余数据集多数变弱，符合 MLP 过滤常见 reduction 模式的设计动机。（PDF p.10, Table 5）
- Table 6 比较 data-only、progression-only 与 joint detection。作者总结联合分数总体更强；应查看逐 dataset 行，避免推成每个单项指标必胜。（PDF pp.10–11, Table 6）
- Appendix D 对 diagnosis score 比较 data-only 和 joint criterion；main paper 仍采用 data-only per-feature reconstruction。（Appendix D, pp.11–12）
- HAI 上报告训练约 32 分钟、单样本推理约 0.39ms；空间维 attention 的时间复杂度对特征数为 $O(N^2)$。作者指出大规模特征系统成本会增加，提出层级聚类扩展方向；同时指出 forensic diagnosis 标签稀少。（PDF pp.9, 16; Appendix N）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：9. Limitations — 作者明确指出

Appendix B 指出 attention 空间复杂度随特征数二次增长，在超大监控系统有计算代价；可探索按变量层级聚类。另一个限制是 forensic diagnosis labels 稀少，收集需要大量专业标注。（PDF p.16, Appendix B）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

合法 workload / control-state 切换也可能改变 MHSA associations；SARAD 只比较窗口前后关系并以训练正常 progression autoencoder 作参照，没有外部业务 context 判断该下降是否“正常状态变化”。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

association reduction 是模型 attention map 的变化；它提供检测证据，但不能单独解释关联为何变化，更不能替代 Trace / topology / intervention 的根因验证。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

窗口里正常状态切换与真实故障并发时，差分会混合二者；若状态切换本身产生普遍性 association dropout，progression MLP 是否会过滤它取决于训练样本是否覆盖该状态。

#### 精读笔记原章节：9. Limitations — 本知识库的分析推断

稀疏标签和攻击来源标签不完整，限制了对 feature localization 泛化能力的主张。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：9. Limitations — 实验支持的边界

短异常数据集 SMD / PSM 的半窗口机制可能稀释关联变化；窗口敏感性强调过大的窗口有计算代价并进一步稀释短异常。（Appendix E.2, H, PDF pp.21–22）

#### 精读笔记原章节：9. Limitations — 实验支持的边界

HAI 的 32min / .39ms 结果来自论文设定的硬件和数据规模，不能直接外推到超高维指标集。（Appendix N）

#### 精读笔记原章节：9. Limitations — 实验支持的边界

主诊断分数为 per-feature data reconstruction error，空间 progression 主要参与全局检测分数；它不是 attention edge causality-based diagnosis。（Eq. 6）

#### 精读笔记原章节：9. Limitations — 实验支持的边界

论文用验证集归一化并调超参，但主报告主要是阈值无关 AUC / VUS；在真实报警中固定 operating point 和告警成本未成为主结果。（§4.1）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 增加 workload / control-state / deployment event 条件，比较合法 SAR 与故障 SAR，并测试两者并发。
- **[分析推断]** 以物理拓扑、Trace 和故障注入 ground truth 验证 attention associations 的稳定性及定位语义。
- **[分析推断]** 针对短持续异常设计可变长 / 多尺度 subseries progression，报告 detection delay、事件召回和固定误报率。
- **[分析推断]** 扩展主诊断分数，在 feature residual、association progression 和领域标注间做受控比较。
- **[分析推断]** 使用分层 channel cluster 降低 $O(N^2)$ 成本，同时验证跨 cluster 的故障传播是否仍被保留。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **OracleAD / Structured Temporal Causality**：OracleAD 比较当前 latent pairwise-distance matrix 与 SLS；SARAD 比较两半 attention map 的下降并重构 progression。二者都从表示结构提取异常线索，但 SLS 是全局对称 latent-distance 模板，SARAD 则显式利用窗口内关联变化。
- **GCAD**：GCAD 根据各 target prediction loss 对输入通道的梯度近似窗口级有向 Granger influence；SARAD attention weights 是重建依赖，未主张 Granger 因果。
- **CAROTS**：用 Granger 图指导因果保持 / 破坏增强；SARAD 用 attention association progression 作为直接异常信号。
- **Graph-MoE**：Graph-MoE 学当前窗口图并用历史 memory 路由 GNN-depth experts；SARAD 从 Transformer attention 关系下降构造独立 progression detector。
- **CrossAD**：CrossAD 比较粗细时间尺度正常映射并用跨窗原型；SARAD 比较跨变量关系在窗口前后两半的变化。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.2–4, §§1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.4, §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.5–6, §§3.2–3.3, Eq. 6 | 精读笔记保留的原文定位 |
| Research problem / scenario | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.2–4, §§1 | 精读笔记保留的原文定位 |
| Research problem / scenario | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.4, §2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.3–4, §2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.6, §3.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.7 | 精读笔记保留的原文定位 |
| Challenges / prior methods | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.8, §4.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.2–4, §§1–2 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.5–7, Eqs. 1–6, Fig. 1, Table 1 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.5–6, §3.2 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.5–6, §3.2, Eq. 1 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.6, §3.3, Table 5 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.6, §3.3 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.6, §3.4, Eq. 4 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.7, Eqs. 5–6 | 精读笔记保留的原文定位 |
| Method / formulas | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.22 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.7, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.7–9, §§4.1–4.2 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.8, §4.2, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF pp.8 | 精读笔记保留的原文定位 |
| Experimental evidence | SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf | PDF p.9, Table 4 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "sarad",
  "title_en": "SARAD: Spatial Association-Aware Anomaly Detection and Diagnosis for Multivariate Time Series",
  "title_zh": "面向多变量时间序列异常检测与诊断的空间关联感知方法",
  "authors": [
    "Zhihao Dai",
    "Ligang He",
    "Shuang-Hua Yang",
    "Matthew Leeke"
  ],
  "year": 2024,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2024/NeurIPS/SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
  "reading_note_path": "papers/sarad/notes.md",
  "code_url": "https://github.com/daidahao/SARAD/",
  "research_area": "多变量变量关联演进与异常诊断",
  "method_tags": [
    "TSAD multivariate association-reduction attention spatial-progression anomaly-diagnosis NeurIPS-2024"
  ],
  "research_scenario": "- [作者主张] 无监督多变量时序检测和特征级诊断，重点捕获异常时变量间空间关联下降（Spatial Association Reduction, SAR）。（§§1, 3, PDF pp.2–4） - [作者定义] spatial 指 multivariate feature/channel 维度，不指地理空间。（§2, PDF p.4）",
  "research_problem": "SARAD 面向无监督 multivariate time-series anomaly detection（MTSAD）和 feature-level diagnosis。作者指出，常见 temporal detectors 主要根据预测 / 重建残差测量时间新颖性，却可能遗漏跨变量依赖变化；仅考虑多变量相关性的图模型也可能把预测误差作为唯一检测证据。论文提出观察：异常期间原本存在的空间关联（作者定义为多变量特征维度上的关联，不是地理空间）可能减弱，称为 Spatial Association Reduction (SAR)。（PDF pp.2–4, §§1–3） 检测目标为每时刻异常标签 $yt$；诊断目标为时刻 $t$ 的异常特征集合 $gt\\subseteq[N]$。（PDF p.4, §3） 需要保留定义边界：模型读取 Transformer 的 attention association map，并将其变化视作 learned reconstruction association reduction。该 map 是模型内部信息流 / 重建依赖，不等于 ground-truth Pearson correlation、Granger graph、已知系统拓扑或干预因果图；诊断是基于检测分数得到 feature ranking。（PDF pp.5–6, §§3.2–3.3, Eq. 6）",
  "core_challenges": [
    "异常空间位置与时间位置并不相同：异常点可以由受影响少数变量引起，纯时间建模难以定位通道。（PDF pp.3–4, §2）",
    "正常也会出现 association reduction：若直接把注意力关系下降全判异常，会将无害变化计入；SARAD 以 progression reconstruction residual 对“常见下降”做正常性建模。（PDF p.6, §3.3）",
    "短异常与窗口聚合冲突：使用半窗口前后比较有利于检测关系演进，但长窗口会稀释短异常。（PDF pp.7, 21, Appendix E.2 / H）",
    "诊断标签不完整：SMD 有 forensic feature labels；SWaT、HAI 多标攻击来源而不是完整异常变量集合，诊断指标受标注语义影响。（PDF p.8, §4.2; Appendix E.3, p.21）"
  ],
  "existing_method_limits": [
    "[作者主张] 纯 temporal 方法可能缺少跨变量关联，单独使用 GDN 式 prediction error 也无法充分利用 spatial 信息。（§§1–2, PDF pp.2–4）",
    "[分析推断] attention map 是网络内部关联 / 重建依赖，不能直接解释为真实相关、Granger 因果、系统拓扑或故障根因。"
  ],
  "core_idea": "SARAD 将多变量窗口分成前后两个子序列，经 encoder-only Transformer 读取变量维（论文称 spatial）的 MHSA 关联矩阵，提取关联随时间下降的 column-wise progression；用 MLP 重建该 progression 以过滤正常下降，再将数据重建误差和 progression 重建误差标准化后相加，兼做异常检测与变量级候选诊断。",
  "technical_innovations": [
    {
      "name": "Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association",
      "author_claim": "**[作者主张]** Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association maps。（§3.2, Eq. 1）",
      "challenge_ids": [
        "C4",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Association progression extraction",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** Transposed feature tokens + encoder-only Transformer 在多变量维学习 feature association maps。（§3.2, Eq. 1）"
    },
    {
      "name": "前后子窗关联图的非负差 $S_h^l=ReLU",
      "author_claim": "**[作者主张]** 前后子窗关联图的非负差 $S_h^l=ReLU(A^l_{1,h}-A^l_{2,h})$ 提取关联下降。（§3.3, Eq. 2）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 前后子窗关联图的非负差 $S_h^l=ReLU(A^l_{1,h}-A^l_{2,h})$ 提取关联下降。（§3.3, Eq. 2）"
    },
    {
      "name": "聚合最终层每个 attention head 的 column sum",
      "author_claim": "**[作者主张]** 聚合最终层每个 attention head 的 column sum，形成 $S\\in\\mathbb R^{H\\times N}$，统计某个 source feature 对其他特征重建贡献的下降。（§3.3, Eq. 3）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 聚合最终层每个 attention head 的 column sum，形成 $S\\in\\mathbb R^{H\\times N}$，统计某个 source feature 对其他特征重建贡献的下降。（§3.3, Eq. 3）"
    },
    {
      "name": "用两层 MLP 重建 $S$",
      "author_claim": "**[作者主张]** 用两层 MLP 重建 $S$；训练目标 $L=\\|\\hat X-X\\|^2+\\lambda_{LS}\\|\\hat S-S\\|^2$，stop-gradient 防止 progression loss 改写 association representation。（§3.4, Eq. 4）",
      "challenge_ids": [
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 用两层 MLP 重建 $S$；训练目标 $L=\\|\\hat X-X\\|^2+\\lambda_{LS}\\|\\hat S-S\\|^2$，stop-gradient 防止 progression loss 改写 association representation。（§3.4, Eq. 4）"
    },
    {
      "name": "检测分数为验证集标准化的 data residual 与 progression residual 之和",
      "author_claim": "**[作者主张]** 检测分数为验证集标准化的 data residual 与 progression residual 之和；主诊断公式是 per-feature data reconstruction residual。（Eqs. 5–6）",
      "challenge_ids": [
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Association progression extraction",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "主诊断分数为 per-feature data reconstruction error，空间 progression 主要参与全局检测分数；它不是 attention edge causality-based diagnosis。（Eq. 6）",
      "limitation_type": "证据边界",
      "source_locator": "**[作者主张]** 检测分数为验证集标准化的 data residual 与 progression residual 之和；主诊断公式是 per-feature data reconstruction residual。（Eqs. 5–6）"
    }
  ],
  "methodology": {
    "architecture": "text 输入窗口 X ∈ R^(2W×N) ├─ 沿时间一分为二：X1、X2 ├─ 每个子窗转置为变量为 token：Linear(Xiᵀ) + learnable feature embedding M ├─ Encoder-only Transformer 沿变量维 MHSA 编码 / 重构 │ └─ 各层各头输出 association map A^l{i,h} ├─ 最后一层两子窗：S^lh = ReLU(A^l{1,h} − A^l{2,h}) ├─ 每个 head 对 association progression 做 column sum → S ∈ R^(H×N) ├─ MLP 重构 S → Ŝ，用 ||S−Ŝ||² 量化罕见关联下降 └─ 标准化 data reconstruction error r 和 progression error p 后相加 → s 数据重建 Transformer 与 spatial progression MLP 端到端联合训练；stop-gradient 阻断 $S$ 的梯度回流数据模块。检测使用全局 scalar score；主文诊断公式使用逐特征数据 reconstruction residual。（PDF pp.5–7, Fig. 1, Table 1, Eqs. 1–6）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 Spatial data reconstruction",
      "6.2 Association progression extraction",
      "6.3 Progression reconstruction filters benign reductions",
      "6.4 Joint objective and score",
      "6.5 训练流程及配置"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (4)",
      "Eq. (5)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "SARAD 将多变量窗口分成前后两个子序列，经 encoder-only Transformer 读取变量维（论文称 spatial）的 MHSA 关联矩阵，提取关联随时间下降的 column-wise progression；用 MLP 重建该 progression 以过滤正常下降，再将数据重建误差和 progression 重建误差标准化后相加，兼做异常检测与变量级候选诊断。"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets and metrics",
      "Detection 报告 threshold-independent range-based AUC-ROC / AUC-PR 及 VUS-ROC / VUS-PR；五次 seed 平均。Baselines 包含 IF、DIF、USAD、GDN、MAD-GAN、DiffAD、TranAD、ATF-UAD、Anomaly Transformer、DCdetector。诊断在有标签数据集上使用 HR、NDCG 和 IPS；标注完整性因数据集而异。（PDF pp.7–9, §§4.1–4.2）",
      "| Dataset | AUROC | AUPRC | VUS-ROC | VUS-PR | |---|---:|---:|---:|---:| | SMD | 79.97 | 15.09 | 79.67 | 15.02 | | PSM | 61.87 | 41.06 | 61.77 | 41.01 | | SWaT | 88.29 | 72.90 | 87.52 | 70.68 | | HAI | 96.87 | 67.78 | 96.17 | 64.70 |",
      "作者称 SMD 的 VUS-ROC 比 MAD-GAN 高 15.51 个百分点、HAI 比 DiffAD 高 9.92 点；PSM 比 GDN 低 1.36 点、SWaT 比 DIF 低 0.36 点，显示其为领先或相近而非全数据集完全领先。（PDF p.8, Table 3, §4.2）"
    ],
    "baselines": [
      "Detection 报告 threshold-independent range-based AUC-ROC / AUC-PR 及 VUS-ROC / VUS-PR；五次 seed 平均。Baselines 包含 IF、DIF、USAD、GDN、MAD-GAN、DiffAD、TranAD、ATF-UAD、Anomaly Transformer、DCdetector。诊断在有标签数据集上使用 HR、NDCG 和 IPS；标注完整性因数据集而异。（PDF pp.7–9, §§4.1–4.2）"
    ],
    "metrics": [
      "### 7.1 Datasets and metrics",
      "Detection 报告 threshold-independent range-based AUC-ROC / AUC-PR 及 VUS-ROC / VUS-PR；五次 seed 平均。Baselines 包含 IF、DIF、USAD、GDN、MAD-GAN、DiffAD、TranAD、ATF-UAD、Anomaly Transformer、DCdetector。诊断在有标签数据集上使用 HR、NDCG 和 IPS；标注完整性因数据集而异。（PDF pp.7–9, §§4.1–4.2）",
      "Table 3 的 SARAD 四指标（AUROC / AUPRC / VUS-ROC / VUS-PR，%）：",
      "| Dataset | AUROC | AUPRC | VUS-ROC | VUS-PR | |---|---:|---:|---:|---:| | SMD | 79.97 | 15.09 | 79.67 | 15.02 | | PSM | 61.87 | 41.06 | 61.77 | 41.01 | | SWaT | 88.29 | 72.90 | 87.52 | 70.68 | | HAI | 96.87 | 67.78 | 96.17 | 64.70 |"
    ],
    "main_results": [
      "四个公开基准：SMD（38 features）、PSM（25）、SWaT（51）、HAI（79）。训练集只含无标签数据，测试集带异常 labels。Table 2 的训练 / 测试点数分别为 SMD 708,405 / 708,420，PSM 132,481 / 87,841，SWaT 496,800 / 449,919，HAI 921,603 / 402,005；异常比例 4.16%、27.73%、12.02%、2.23%。异常持续时间差异明显：中位长度 SMD 11、PSM 5、SWaT 447、HAI 162。（PDF pp.7, 21, Table 2; Appendix E.2）",
      "Table 3 的 SARAD 四指标（AUROC / AUPRC / VUS-ROC / VUS-PR，%）：",
      "作者称 SMD 的 VUS-ROC 比 MAD-GAN 高 15.51 个百分点、HAI 比 DiffAD 高 9.92 点；PSM 比 GDN 低 1.36 点、SWaT 比 DIF 低 0.36 点，显示其为领先或相近而非全数据集完全领先。（PDF p.8, Table 3, §4.2）",
      "Table 4 报告点级 HR@100/150、NDCG@100/150 和范围级 IPS@100/150。SARAD 的 HR@150 / NDCG@150 / IPS@150：SMD 71.93 / 69.78 / 76.44；SWaT 12.83 / 11.65 / 54.34；HAI 12.10 / 10.16 / 14.07。（PDF p.9, Table 4）",
      "- Table 5：去掉 ReLU 后 SMD VUS-ROC/VUS-PR 从 79.67/15.02 降至 75.16/12.35，支持专注 association reduction；将 column sum 改 row sum 后部分性能小幅变动且并非所有指标都差；完全不聚合（no sum）会显著退化，例如 SMD AUROC / AUPRC 79.97/15.09 → 57.31/6.09。将 $S$ 直接作为异常证据（不经 MLP reconstruction）只在 SMD 部分项更好，在其余数据集多数变弱，符合 MLP 过滤常见 reduction 模式的设计动机。…"
    ],
    "ablations": [
      "### 7.4 Ablations and operational cost",
      "- Table 5：去掉 ReLU 后 SMD VUS-ROC/VUS-PR 从 79.67/15.02 降至 75.16/12.35，支持专注 association reduction；将 column sum 改 row sum 后部分性能小幅变动且并非所有指标都差；完全不聚合（no sum）会显著退化，例如 SMD AUROC / AUPRC 79.97/15.09 → 57.31/6.09。将 $S$ 直接作为异常证据（不经 MLP reconstruction）只在 SMD 部分项更好，在其余数据集多数变弱，符合 MLP 过滤常见 reduction 模式的设计动机。…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "Appendix B 指出 attention 空间复杂度随特征数二次增长，在超大监控系统有计算代价；可探索按变量层级聚类。另一个限制是 forensic diagnosis labels 稀少，收集需要大量专业标注。（PDF p.16, Appendix B）"
    ],
    "reasoned_inference": [
      "合法 workload / control-state 切换也可能改变 MHSA associations；SARAD 只比较窗口前后关系并以训练正常 progression autoencoder 作参照，没有外部业务 context 判断该下降是否“正常状态变化”。",
      "association reduction 是模型 attention map 的变化；它提供检测证据，但不能单独解释关联为何变化，更不能替代 Trace / topology / intervention 的根因验证。",
      "窗口里正常状态切换与真实故障并发时，差分会混合二者；若状态切换本身产生普遍性 association dropout，progression MLP 是否会过滤它取决于训练样本是否覆盖该状态。",
      "稀疏标签和攻击来源标签不完整，限制了对 feature localization 泛化能力的主张。"
    ],
    "evidence_gaps": [
      "短异常数据集 SMD / PSM 的半窗口机制可能稀释关联变化；窗口敏感性强调过大的窗口有计算代价并进一步稀释短异常。（Appendix E.2, H, PDF pp.21–22）",
      "HAI 的 32min / .39ms 结果来自论文设定的硬件和数据规模，不能直接外推到超高维指标集。（Appendix N）",
      "主诊断分数为 per-feature data reconstruction error，空间 progression 主要参与全局检测分数；它不是 attention edge causality-based diagnosis。（Eq. 6）",
      "论文用验证集归一化并调超参，但主报告主要是阈值无关 AUC / VUS；在真实报警中固定 operating point 和告警成本未成为主结果。（§4.1）"
    ]
  },
  "research_implications": [
    "- [分析推断] 增加 workload / control-state / deployment event 条件，比较合法 SAR 与故障 SAR，并测试两者并发。 - [分析推断] 以物理拓扑、Trace 和故障注入 ground truth 验证 attention associations 的稳定性及定位语义。 - [分析推断] 针对短持续异常设计可变长 / 多尺度 subseries progression，报告 detection delay、事件召回和固定误报率。 - [分析推断] 扩展主诊断分数，在 feature residual、association progression 和领域标注间做受控比较。 - [分析推断] 使用分层 channel cluster 降低 $O(N^2)$ 成本，同时验证跨 cluster 的故障传播是否仍被保留。"
  ],
  "related_papers": [
    {
      "paper_id": "carots",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "crossad",
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
      "paper_id": "graph-moe",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.2–4, §§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF p.4, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.5–6, §§3.2–3.3, Eq. 6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.2–4, §§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF p.4, §2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.3–4, §2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF p.6, §3.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF p.8, §4.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.2–4, §§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.5–7, Eqs. 1–6, Fig. 1, Table 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.5–6, §3.2",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "e30a1a7742e773723d0e40c0b1ae5dff63cb413fc53c79bb0a7b27b5b303cf6b",
    "reading_note_sha256": "d34bfe2cd73aa383f3151f5f5f01467f65811a7e4977a7fb0c4f7f5eb7f6fae1",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "805269429739a6f12fe2813f00d6c2269187e7dc7e707c8c3a26a1634a08eec1"
  },
  "knowledge_card_path": "papers/sarad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
