# Knowledge Dossier — CAPMix: Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments

## 1. Basic Information

- **English title**: CAPMix: Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments
- **中文译名**：面向噪声与动态环境的 AIOps 鲁棒 KPI 异常检测
- **Authors**: Xudong Mou, Rui Wang, Tiejun Wang, Zexin Wu, Fangda Guo, Jie Sun, Shiru Chen, Penghao Zhang, Tiezi Zhang, Tianyu Wo, Hao Peng, Chunming Hu, Xudong Liu, Renyu Yang
- **Venue / year / CCF**: ASE 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/alsike22/CAPMix
- **Research area**: AIOps KPI 多变量异常检测与鲁棒半监督学习
- **Method tags**: TSAD KPI AIOps normal-fluctuation anomaly-augmentation label-noise DTW mixup robustness production

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** AIOps 的多变量 KPI 异常检测；服务指标噪声大、非平稳，自动扩缩容、发布和采集活动会带来正常波动，训练数据也可能污染。（PDF §1, §5）
- **[实验支持]** 除 AIOps / ASD / SMD / Exathlon 外，作者还在 UCR、SWaT、WADI、ESA 测试迁移性。（Table 2）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文关注 AIOps 中的 KPI 时间序列异常检测：输入是按时间排序、每步有 $d$ 个 KPI 的多变量序列；模型将长度为 $t$ 的滑动窗口判为正常或异常，并输出异常分数。真实服务中的 KPI 具有时间依赖、非平稳性和跨指标相关性；部署、自动扩缩容、采集抖动、日志轮转等正常运维活动也会产生尖峰或短时变化。训练集还可能含未充分标注的真实异常。

作者把合成异常与真实故障模式不匹配称为 **Anomaly Shift**，区分两个方向：

1. **低区分度**：合成异常过于接近正常波动，却被赋予确定异常标签，模型因错误监督而把正常抖动当成故障。
2. **过高区分度**：合成异常过于夸张（如不现实的突变或极端尖峰），模型学到只对夸张模式敏感的边界，漏掉细微但重要的真实异常。

这和“正常性假设”方法的弱点互补：仅拟合正常数据的检测器容易受含噪或污染的训练集影响；只靠合成异常训练则依赖注入模式与真实故障足够匹配。（PDF pp.1–3, §1–3.2）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 合成异常存在 Anomaly Shift：过于像正常波动的样本被错误硬标为异常；过于夸张的样本则离真实故障过远。（§1, §3.3.2–3.3.3）
- **[作者主张]** 训练集中的潜在异常、正常抖动和稀疏/不可靠标签会共同扭曲边界。（§1, §5.2）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 正常性假设检测器在含噪污染数据上容易对 benign fluctuation 过敏；异常假设检测器则依赖模拟模式覆盖真实故障且强度校准。（§1–2）
- **[分析推断]** 这些路线虽强调动态环境，但模型仍以 KPI 窗口本身为主要证据，没有明确解释负载、发布或依赖变化导致的波动来源。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：5. Core Idea

不是把所有注入样本都视为同等可信的异常，而是将“伪异常像不像正常”和“伪异常离真实数据流形是否过远”分别处理：DTW 距离近的注入样本获得软标签；输入和特征空间 Mixup 则让模型看到正常与异常之间的连续样本和标签，降低对单一人工模式的过拟合。论文用轻量三块 TCN 学习时序表示和二分类概率。（PDF pp.3–6, §3.2–3.4）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 合成异常存在 Anomaly Shift：过于像正常波动的样本被错误硬标为异常；过于夸张的样本则离真实故障过远。（§1, §3.3.2–3.3.3）
- **C2（第4节挑战）**：[作者主张] 训练集中的潜在异常、正常抖动和稀疏/不可靠标签会共同扭曲边界。（§1, §5.2）

### 7.1 CutAddPaste 片段替换及可控趋势扰动

- **作者技术描述**：**[作者主张]** CutAddPaste 片段替换及可控趋势扰动，构造形状/相关、季节、趋势、全局与上下文异常。（§3.3.1, Fig. 3）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“8.1 窗口表示与 CutAddPaste”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 以均值正常中心及 $\mu_d+\gamma\sigma_d$ DTW 阈值确定软标签 $1/\gamma$ 或硬标签 1

- **作者技术描述**：**[作者主张]** 以均值正常中心及 $\mu_d+\gamma\sigma_d$ DTW 阈值确定软标签 $1/\gamma$ 或硬标签 1。（§3.3.2, Eqs. (2)–(4)）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“8.2 DTW Label Revision（LR）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 在输入与 TCN 中间表示上混合样本和标签

- **作者技术描述**：**[作者主张]** 在输入与 TCN 中间表示上混合样本和标签；三块 TCN 加 MLP/softmax 与 BCE 训练。（§3.3.3–3.4, Eqs. (5), (7)）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“8.3 TCN 与 Dual-Space Mixup（DS）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：6. Architecture / Workflow

```text
KPI 序列 → 标准化及滑动窗口
          → CutAddPaste 结构化注入伪异常
          → 与训练正常序列计算 DTW 距离并修正伪异常标签
          → 原始与注入样本混合
          → TCN 输入空间 / 中间表示空间 Mixup
          → MLP 投影头 + softmax + BCE 联合训练
          → 测试窗口的异常概率 p 作为 score，按阈值 τ 转为告警
```

训练伪代码（Algorithm 1）分三阶段：

1. **Adaptive Data Augmentation**：逐窗口采样源片段、目标粘贴位置及若干特征维度，按设定趋势斜率扰动后粘贴。
2. **Label Revision & Refinement**：从合成集合抽取 $vN$ 个样本，用原始训练集估计正常中心和 DTW 距离阈值，把目标标签从硬标签修成软/硬标签；再与原样本合并。
3. **Joint Optimization**：在 mini-batch 上执行 DS-Mixup，按 BCE 训练 TCN 与投影头直至收敛。

训练阶段使用已标记的原始样本标签（论文写明 $Y^r$ 包含专家标注原始标签及伪异常标签）；本方法虽强调不要求训练数据必须包含异常，但“原始标签在具体基准上是否可用、污染样本如何标注”没有在主文中逐数据集交代清楚，见 §11。（PDF pp.5–6, Algorithm 1, §3.4）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：8.1 窗口表示与 CutAddPaste。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：8. Method

#### 8.1 窗口表示与 CutAddPaste

§3.1 将长度 $t$ 的多变量窗口写为 $X\in\mathbb{R}^{t\times d}$，每条长序列以步幅 δ 切成窗口。作者用结构分解 $X=\Gamma(2\pi\omega T)+\Theta(T)$ 描述形状函数、季节性和趋势；跨维度相关性可由协方差表示。这个分解是解释合成扰动类型的表示，并非模型另行估计的潜变量。

CutAddPaste 从目标窗 $X^i$ 与随机源窗 $X^j$ 取片段，随机选择长度 $r\ge\zeta$、源位置和粘贴位置；在选择的 $e$ 个变量上可加趋势项 $V_{trend}=\rho mR$，其中斜率向量 $m$ 的分量在 $(-1,1)$ 内采样。之后将片段覆盖目标窗口对应区间（§3.3.1, Eq. (1), Algorithm 1）。

注入目标覆盖论文讨论的结构变化：A1 子序列扰动（正文把形状变化与跨变量相关性变化分别展开）、A2 季节性、A3 趋势，以及 A4/A5 全局和上下文点异常。Table 1 将覆盖类型概括为 global、contextual、shape、seasonal、trend；正文对 A1 的 shape/correlation 细分比表格缩写更细，不能据此把两种标记强行视作完全相同的五类定义。（PDF pp.3–4, Table 1, Fig. 3）

#### 8.2 DTW Label Revision（LR）

作者先假定训练序列的大多数窗口正常，以窗口均值序列构建正常中心：

\[
C_n=\frac{1}{N}\sum_{i=1}^{N}X_i. \tag{2}
\]

对注入样本 $X^a$ 计算 $d(X^a,C_n)$。用原始训练窗口到 $C_n$ 的距离均值 μ_d 和标准差 σ_d 设置阈值 μ_d+γσ_d（Eq. (3)）。若合成样本距离不超过阈值，则判为模糊、赋软异常标签 $y^r=1/\gamma$；超出则赋硬标签 $y^r=1$（Eq. (4)）。γ 因而同时控制模糊区宽度和软标签幅度。原文写 γ≥0，但 Eq. (4) 的 1/γ 在 γ=0 时无定义；若软标签要落在 [0,1]，还需 γ≥1。论文未在正文明确这一边界及各数据集取值，复现时需核对配置。作者没有采用距离比例作为连续标签，理由是额外计算和对距离尺度敏感。

解释边界：它按与**单一均值中心**的 DTW 距离修正，不是从标注的真实故障类别估计异常置信度；均值中心以及“大多数训练窗口正常”的假设可能不适合强多模态正常状态或严重污染数据。（PDF pp.4–5, §3.3.2, Eqs. (2)–(4)）

#### 8.3 TCN 与 Dual-Space Mixup（DS）

编码器有三个 temporal convolutional block；每块依次使用 Conv1D、BatchNorm、ReLU、MaxPool1D，第一块另加 Dropout，将 $t$ 长度窗口映射为固定表示 $z_i$。另有一层隐藏层的 MLP 投影器，包含 BN 与 ReLU，将表示映射到二维 $q_i$，再用 softmax 输出正常/异常概率。（PDF p.5, §3.3.3–3.4）

在可配置深度 $l$ 做 Mixup：

\[
X^{(l)}_{mix}=\lambda f^{(l)}(X_i)+(1-\lambda)f^{(l)}(X_j),\quad
y^{(l)}_{mix}=\lambda y_i^{(l)}+(1-\lambda)y_j^{(l)}. \tag{5}
\]

$l=0$ 时是原始输入空间 Mixup；在中间层则是在 TCN 特征空间插值。标签同步插值，避免混合输入仍被硬标成一类。论文把这一对设计合称 DS-Mixup。主文描述 α 为 mixup ratio 的控制超参数，但未在文字中说明 λ 的采样分布、确切默认层位或逐数据集设置，不能补写常见的 Beta 分布作为论文事实。

#### 8.4 目标函数与测试

投影器通过 softmax 得到 $[1-p_i,p_i]$，其中 $p_i$ 是异常概率；以 BCE 训练：

\[
\mathcal{L}=-\frac{1}{N}\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)]. \tag{7}
\]

测试时 $S_i=p_i\in[0,1]$，按预设阈值 τ 产生二元标签（Eq. (8)）。文中提到实际部署可用 POT 等无监督方法从分数得到告警阈值；主要实验报告的 Best RPA-F1 则是扫阈值所得，二者不是同一设置。（PDF pp.6–7, §3.4, §4.1.2）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (4)、Eq. (8)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：8.4 目标函数与测试及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

CAPMix 以 CutAddPaste 生成可控时序伪异常，再用 DTW 距离修正“看起来仍正常”的伪异常标签，并在输入空间与 TCN 潜在空间做 Mixup，以降低训练污染、正常波动和合成异常失真对 KPI 判别边界的影响。

## 9. Experimental Evidence

#### 精读笔记原章节：9. Experiments

#### 9.1 数据、基线与指标

Table 2 共评估八套数据，含 KPI 与跨领域数据；Tra-Ano 表示训练集异常比例：

| 数据集 | 场景 | 实体数 / 变量数 | 点数 | Tra-Ano |
|---|---|---:|---:|---:|
| AIOps | Cloud KPI | 29 / 1 | 203,316 | 3.86% |
| ASD | Application | 12 / 19 | 154,171 | 0% |
| SMD | Server | 28 / 38 | 608,342 | 0% |
| Exathlon | Spark | 8 / 19 | 141,074 | 0% |
| UCR | 多领域 | 250 / 1 | 1,383,502 | 0% |
| SWaT | Waterworks | 1 / 51 | 63,441 | 0% |
| WADI | Waterworks | 1 / 127 | 61,993 | 0% |
| ESA | Satellite | 1 / 6 | 24,547,200 | 0.6% |

基线覆盖传统方法（OC-SVM、IF、RRCF、SR、DAMP）、正常性假设深度检测器（LSTM-ED、Deep SVDD、Anomaly Transformer、MixMamba、MTSCAD、SHUE、CATCH、MOC、RoCA、AOC、TCC）及异常增强方法（NCAD、AnomalyBert、RedLamp、CutAddPaste）。指标为 Revised Point-Adjusted F1（RPA-F1）；AIOps 和 UCR 的跨子集分数按异常数加权。论文报告阈值扫描得到的 Best RPA-F1，并提醒点调整会改变事件与点级误差的权衡。（PDF pp.6–7, §4.1, Table 2）

#### 9.2 主结果

Table 3 为 10 次运行的均值与标准差。CAPMix 平均 Best RPA-F1 为 **60.69%**，CutAddPaste 为 **40.02%**，表中第二高总体方法；CAPMix 并非每个数据集都最好：

| 数据集 | CAPMix | 表中最佳非 CAPMix | 结果解读 |
|---|---:|---:|---|
| AIOps | 80.45±0.43 | CutAddPaste 77.44±0.86 | CAPMix 略优 |
| SMD | 27.42±12.50 | AOC 60.85±0.29 | 明显落后 |
| ASD | 61.30±1.96 | RedLamp 69.59±1.33 | 落后 |
| Exathlon | 78.89±1.61 | CutAddPaste 73.73±4.72 | CAPMix 优 |
| UCR | 71.89±1.89 | CutAddPaste 69.98±1.44 | CAPMix 略优 |
| SWaT | 47.04±2.70 | CutAddPaste 43.43±4.86 | CAPMix 优 |
| WADI | 34.08±6.67 | SHUE 35.57±0.84 | 略落后 |
| ESA | 84.46±5.50 | AOC 55.90±2.64 | CAPMix 优 |

这些结果支持“跨八套数据的平均分较强”和“不同机制收益依数据集而变”，但不支持“在各数据集均优于现有方法”。尤其 SMD 的大标准差和与 AOC 的差距，值得后续核查不同训练设定的可比性。（PDF pp.7–8, Table 3）

#### 9.3 消融与鲁棒性

Table 4（10 次运行）报告平均分：无增强 TCN 29.14；加入 CutAddPaste（CAP）46.26；在 CAP 上加 LR 为 47.34；用 CAP + Mixup（不含 LR）为 57.49；完整模型 60.69。该表显示 Mixup 在该实验组合中的平均增益大于 LR，但不意味着 LR 无效：CAP-LR 在 AIOps、SMD、ASD 上提高，且两模块分别处理不同方向的 Anomaly Shift。UMAP 图（Fig. 4）显示伪异常与真实异常簇更接近、与正常区域重叠较少；这是可视化证据，不是分布距离的正式统计检验。（PDF pp.7–8, §4.3, Table 4, Fig. 4）

污染鲁棒性实验在 AIOps 上逐步把训练异常量增加至 0.5×–8×。Fig. 5 显示高污染时 CAPMix 的 F1 和 precision 比原始 CAP 更稳定；正文未给每个污染率的数值。超参数图 Fig. 6 比较 γ 与 α：AIOps 对 γ 更敏感，WADI 对 α 更敏感，支持“标签容忍度与 Mixup 对不同数据结构的作用不同”。（PDF pp.8–9, §4.4–4.5, Figs. 5–6）

#### 9.4 生产案例

作者在 Kuaishou 的 KAIOps 集群系统集成 CAPMix；数据包含 16 天、每分钟采样的七节点 KPI，节点级信号包括 CPU、内存、I/O、网络，另有 API latency、pending tasks、pod restarts 等集群指标。Table 5 报告测试集 3,029 点、1,117 个异常点 / 145 个异常事件；案例表中 RPA precision 0.80、F1 0.79、PR-AUC 0.87、NAB 0.76。Fig. 8 对比指出日志轮转、采集扰动及负 CPU 等监控伪影会触发基线，而 CAPMix 分数较低；持续故障如 memory leak 则获得持续响应。作者还描述用操作员确认的误报和真故障反馈周期性修正 LR，但没有给出反馈策略、更新频率及独立对照实验细节。（PDF pp.9–10, §5, Table 5, Fig. 8）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

精读笔记未单独归类；分析推断需依据第 8–9 节的方法假设和实验范围，不能表述为已证实缺陷。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：11. Limitations — 作者明确讨论 / 本文未明确讨论（归属未明确）

论文没有单独的“Limitations”章节，也没有给出完整的局限清单。它通过超参数分析指出 γ 和 α 对不同数据集的重要性不同（§4.5），并在生产章节强调标签稀疏、不可靠、计算延迟和正常事件高度多样（§5.2）。

#### 精读笔记原章节：11. Limitations — 作者明确讨论 / 本文未明确讨论（归属未明确）

正文用阈值扫描报告 Best RPA-F1；该指标适合比较分数可分性，但不是无标签线上阈值下的实际告警精度。部署中的 POT 被提及，未见与固定阈值/校准方案的系统对比。

#### 精读笔记原章节：11. Limitations — 作者明确讨论 / 本文未明确讨论（归属未明确）

主文写 $Y^r$ 包含专家标注的原始标签，但又强调不要求训练集含异常；训练异常在每个基准上是否带标签、标签缺失时如何训练 contaminated samples，未明确到足以完全复现。

#### 精读笔记原章节：11. Limitations — 作者明确讨论 / 本文未明确讨论（归属未明确）

本地 PDF 扉页有正式出版信息占位符；阅读对象的内容与题名相符，但版本元数据需依 DOI / 会议记录核对。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：13. My Understanding

CAPMix 最有价值的抽象不是“多做几种数据增强”，而是把增强样本本身当作带不确定性的伪监督：一个合成片段可能确实破坏了形态，也可能只是正常的工作负载变化；其异常标签需要按相似度降低置信度。Mixup 再限制模型不要把某一类夸大的注入形状当成唯一的故障边界。这个思路对生产监控有用，但它仍然把判别依据主要放在窗口形态和训练标签上，缺少“为什么业务负载变了”的外部证据。

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 用负载、发布、扩缩容及服务调用等上下文条件化正常状态与伪异常置信度，检验同时发生负载变化与故障时的可分性。
- **[分析推断]** 将单均值中心改成可校准的多正常状态模型，并报告状态覆盖、未知模式和误报成本。
- **[分析推断]** 在固定无监督阈值、事件级成本及跨集群部署下复验，以弥补最佳阈值和单生产案例的证据边界。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

CAPMix 与常见“只建模正常模式”的检测器相比，主动构造伪异常并学习监督边界；与纯 CutAddPaste 相比，它校准近正常伪异常的标签并把过度显著样本向训练分布插值。相较于后续阅读中的 test-time adaptation 路线，它主要在训练阶段改善表示和边界，不依赖连续测试时更新。它解决的是“窗口级异常识别”，不等于对告警归因、故障定位或运维动作的端到端 AIOps 系统。

批内待比较：与 When Model Meets New Normals 的“顺应新正常”相比，CAPMix 能否在不改阈值/在线模型的情况下处理运行状态漂移；与 CAROTS 的因果增强相比，CAPMix 的先验注入是否仅靠形态覆盖；这些问题留待三篇笔记完成后在批次 Review 中统一判断。

- CutAddPaste：CAPMix 使用的基础时序异常注入方法（参考文献 [11]，KDD 2024）。
- RedLamp：异常增强和伪异常标签修订路线，CAPMix 在 Table 3 中纳入比较。
- RoCA / AOC / SHUE：分别代表污染鲁棒对比、一类边界融合及正常模式敏感性增强等基线；其结果显示不同数据集上不存在单一机制全面占优。
- 本批其他论文链接将在对应笔记完成后通过批次 Review 补齐，避免先写入未核对的交叉结论。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.1–3, §1–3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §1, §5 | 精读笔记保留的原文定位 |
| Research problem / scenario | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | Table 2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §1, §3.3.2–3.3.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §1, §5.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.5–6, §11, §3.4, Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §3.1 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §3.3.1, Eq. (1), Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.3–4, Table 1, Table 1, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | Eq. (3), Eq. (4) | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.4–5, §3.3.2, Eqs. (2) | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF p.5, §3.3.3–3.4 | 精读笔记保留的原文定位 |
| Method / formulas | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.6–7, §3.4, §4.1.2, Eq. (8) | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.6–7, §4.1, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.7–8, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.7–8, §4.3, Table 4, Fig. 4, Table 4, Fig. 4 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.8–9, §4.4–4.5, Fig. 5, Fig. 6 | 精读笔记保留的原文定位 |
| Experimental evidence | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | PDF pp.9–10, §5, Table 5, Fig. 8, Table 5, Fig. 8 | 精读笔记保留的原文定位 |
| Limitations | CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf | §4.5, §5.2 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "capmix",
  "title_en": "CAPMix: Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments",
  "title_zh": "面向噪声与动态环境的 AIOps 鲁棒 KPI 异常检测",
  "authors": [
    "Xudong Mou",
    "Rui Wang",
    "Tiejun Wang",
    "Zexin Wu",
    "Fangda Guo",
    "Jie Sun",
    "Shiru Chen",
    "Penghao Zhang",
    "Tiezi Zhang",
    "Tianyu Wo",
    "Hao Peng",
    "Chunming Hu",
    "Xudong Liu",
    "Renyu Yang"
  ],
  "year": 2026,
  "venue": "ASE",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ASE/CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
  "reading_note_path": "papers/capmix/notes.md",
  "code_url": "https://github.com/alsike22/CAPMix",
  "research_area": "AIOps KPI 多变量异常检测与鲁棒半监督学习",
  "method_tags": [
    "TSAD KPI AIOps normal-fluctuation anomaly-augmentation label-noise DTW mixup robustness production"
  ],
  "research_scenario": "- [作者主张] AIOps 的多变量 KPI 异常检测；服务指标噪声大、非平稳，自动扩缩容、发布和采集活动会带来正常波动，训练数据也可能污染。（PDF §1, §5） - [实验支持] 除 AIOps / ASD / SMD / Exathlon 外，作者还在 UCR、SWaT、WADI、ESA 测试迁移性。（Table 2）",
  "research_problem": "论文关注 AIOps 中的 KPI 时间序列异常检测：输入是按时间排序、每步有 $d$ 个 KPI 的多变量序列；模型将长度为 $t$ 的滑动窗口判为正常或异常，并输出异常分数。真实服务中的 KPI 具有时间依赖、非平稳性和跨指标相关性；部署、自动扩缩容、采集抖动、日志轮转等正常运维活动也会产生尖峰或短时变化。训练集还可能含未充分标注的真实异常。 作者把合成异常与真实故障模式不匹配称为 Anomaly Shift，区分两个方向： 1. 低区分度：合成异常过于接近正常波动，却被赋予确定异常标签，模型因错误监督而把正常抖动当成故障。 2. 过高区分度：合成异常过于夸张（如不现实的突变或极端尖峰），模型学到只对夸张模式敏感的边界，漏掉细微但重要的真实异常。 这和“正常性假设”方法的弱点互补：仅拟合正常数据的检测器容易受含噪或污染的训练集影响；只靠合成异常训练则依赖注入模式与真实故障足够匹配。（PDF pp.1–3, §1–3.2）",
  "core_challenges": [
    "[作者主张] 合成异常存在 Anomaly Shift：过于像正常波动的样本被错误硬标为异常；过于夸张的样本则离真实故障过远。（§1, §3.3.2–3.3.3）",
    "[作者主张] 训练集中的潜在异常、正常抖动和稀疏/不可靠标签会共同扭曲边界。（§1, §5.2）"
  ],
  "existing_method_limits": [
    "[作者主张] 正常性假设检测器在含噪污染数据上容易对 benign fluctuation 过敏；异常假设检测器则依赖模拟模式覆盖真实故障且强度校准。（§1–2）",
    "[分析推断] 这些路线虽强调动态环境，但模型仍以 KPI 窗口本身为主要证据，没有明确解释负载、发布或依赖变化导致的波动来源。"
  ],
  "core_idea": "CAPMix 以 CutAddPaste 生成可控时序伪异常，再用 DTW 距离修正“看起来仍正常”的伪异常标签，并在输入空间与 TCN 潜在空间做 Mixup，以降低训练污染、正常波动和合成异常失真对 KPI 判别边界的影响。",
  "technical_innovations": [
    {
      "name": "CutAddPaste 片段替换及可控趋势扰动",
      "author_claim": "**[作者主张]** CutAddPaste 片段替换及可控趋势扰动，构造形状/相关、季节、趋势、全局与上下文异常。（§3.3.1, Fig. 3）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "8.1 窗口表示与 CutAddPaste",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** CutAddPaste 片段替换及可控趋势扰动，构造形状/相关、季节、趋势、全局与上下文异常。（§3.3.1, Fig. 3）"
    },
    {
      "name": "以均值正常中心及 $\\mu_d+\\gamma\\sigma_d$ DTW 阈值确定软标签 $1/\\gamma$ 或硬标签 1",
      "author_claim": "**[作者主张]** 以均值正常中心及 $\\mu_d+\\gamma\\sigma_d$ DTW 阈值确定软标签 $1/\\gamma$ 或硬标签 1。（§3.3.2, Eqs. (2)–(4)）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "8.2 DTW Label Revision（LR）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 以均值正常中心及 $\\mu_d+\\gamma\\sigma_d$ DTW 阈值确定软标签 $1/\\gamma$ 或硬标签 1。（§3.3.2, Eqs. (2)–(4)）"
    },
    {
      "name": "在输入与 TCN 中间表示上混合样本和标签",
      "author_claim": "**[作者主张]** 在输入与 TCN 中间表示上混合样本和标签；三块 TCN 加 MLP/softmax 与 BCE 训练。（§3.3.3–3.4, Eqs. (5), (7)）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "8.3 TCN 与 Dual-Space Mixup（DS）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 在输入与 TCN 中间表示上混合样本和标签；三块 TCN 加 MLP/softmax 与 BCE 训练。（§3.3.3–3.4, Eqs. (5), (7)）"
    }
  ],
  "methodology": {
    "architecture": "text KPI 序列 → 标准化及滑动窗口 → CutAddPaste 结构化注入伪异常 → 与训练正常序列计算 DTW 距离并修正伪异常标签 → 原始与注入样本混合 → TCN 输入空间 / 中间表示空间 Mixup → MLP 投影头 + softmax + BCE 联合训练 → 测试窗口的异常概率 p 作为 score，按阈值 τ 转为告警 训练伪代码（Algorithm 1）分三阶段： 1. Adaptive Data Augmentation：逐窗口采样源片段、目标粘贴位置及若干特征维度，按设定趋势斜率扰动后粘贴。 2. Label Revision & Refinement：从合成集合抽取 $vN$ 个样本，用原始训练集估计正常中心和 DTW 距离阈值，把目标标签从硬标签修成软/硬标签；再与原样本合并。 3. Joint Optimization：在 mini-batch 上执行 DS-Mixup，按 BCE 训练 TCN 与投影头直至收敛。 训练阶段使用已标记的原始样本标签（论文写明 $Y^r$ 包含专家标注原始标签及伪异常标签）；本方法虽强调不要求训练数据必须包含异常，但“原始标签在具体基准上是否可用、污染样本如何标注”没有在主文中逐数据集交代清楚，见 §11。（PDF pp.5–6, Algorithm 1, §3.4）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "8.1 窗口表示与 CutAddPaste",
      "8.2 DTW Label Revision（LR）",
      "8.3 TCN 与 Dual-Space Mixup（DS）",
      "8.4 目标函数与测试"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (8)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "CAPMix 以 CutAddPaste 生成可控时序伪异常，再用 DTW 距离修正“看起来仍正常”的伪异常标签，并在输入空间与 TCN 潜在空间做 Mixup，以降低训练污染、正常波动和合成异常失真对 KPI 判别边界的影响。"
  },
  "experimental_evidence": {
    "datasets": [
      "| 数据集 | 场景 | 实体数 / 变量数 | 点数 | Tra-Ano | |---|---|---:|---:|---:| | AIOps | Cloud KPI | 29 / 1 | 203,316 | 3.86% | | ASD | Application | 12 / 19 | 154,171 | 0% | | SMD | Server | 28 / 38 | 608,342 | 0% | | Exathlon | Spark | 8 / 19 | 141,074 | 0% | | UCR | 多领域 | 250 / 1 | 1,383,502 | 0% | | SWaT | Waterworks | 1 / 51 |…",
      "Table 3 为 10 次运行的均值与标准差。CAPMix 平均 Best RPA-F1 为 60.69%，CutAddPaste 为 40.02%，表中第二高总体方法；CAPMix 并非每个数据集都最好：",
      "| 数据集 | CAPMix | 表中最佳非 CAPMix | 结果解读 | |---|---:|---:|---| | AIOps | 80.45±0.43 | CutAddPaste 77.44±0.86 | CAPMix 略优 | | SMD | 27.42±12.50 | AOC 60.85±0.29 | 明显落后 | | ASD | 61.30±1.96 | RedLamp 69.59±1.33 | 落后 | | Exathlon | 78.89±1.61 | CutAddPaste 73.73±4.72 | CAPMix 优 | | UCR | 71.89±1.89 | CutAddPaste 69.98±1.44 |…",
      "这些结果支持“跨八套数据的平均分较强”和“不同机制收益依数据集而变”，但不支持“在各数据集均优于现有方法”。尤其 SMD 的大标准差和与 AOC 的差距，值得后续核查不同训练设定的可比性。（PDF pp.7–8, Table 3）"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 9.1 数据、基线与指标",
      "Table 2 共评估八套数据，含 KPI 与跨领域数据；Tra-Ano 表示训练集异常比例：",
      "基线覆盖传统方法（OC-SVM、IF、RRCF、SR、DAMP）、正常性假设深度检测器（LSTM-ED、Deep SVDD、Anomaly Transformer、MixMamba、MTSCAD、SHUE、CATCH、MOC、RoCA、AOC、TCC）及异常增强方法（NCAD、AnomalyBert、RedLamp、CutAddPaste）。指标为 Revised Point-Adjusted F1（RPA-F1）；AIOps 和 UCR 的跨子集分数按异常数加权。论文报告阈值扫描得到的 Best RPA-F1，并提醒点调整会改变事件与点级误差的权衡。（PDF pp.6–7, §4.1, Table 2）",
      "Table 3 为 10 次运行的均值与标准差。CAPMix 平均 Best RPA-F1 为 60.69%，CutAddPaste 为 40.02%，表中第二高总体方法；CAPMix 并非每个数据集都最好："
    ],
    "main_results": [
      "Table 2 共评估八套数据，含 KPI 与跨领域数据；Tra-Ano 表示训练集异常比例：",
      "基线覆盖传统方法（OC-SVM、IF、RRCF、SR、DAMP）、正常性假设深度检测器（LSTM-ED、Deep SVDD、Anomaly Transformer、MixMamba、MTSCAD、SHUE、CATCH、MOC、RoCA、AOC、TCC）及异常增强方法（NCAD、AnomalyBert、RedLamp、CutAddPaste）。指标为 Revised Point-Adjusted F1（RPA-F1）；AIOps 和 UCR 的跨子集分数按异常数加权。论文报告阈值扫描得到的 Best RPA-F1，并提醒点调整会改变事件与点级误差的权衡。（PDF pp.6–7, §4.1, Table 2）",
      "### 9.2 主结果",
      "Table 3 为 10 次运行的均值与标准差。CAPMix 平均 Best RPA-F1 为 60.69%，CutAddPaste 为 40.02%，表中第二高总体方法；CAPMix 并非每个数据集都最好：",
      "这些结果支持“跨八套数据的平均分较强”和“不同机制收益依数据集而变”，但不支持“在各数据集均优于现有方法”。尤其 SMD 的大标准差和与 AOC 的差距，值得后续核查不同训练设定的可比性。（PDF pp.7–8, Table 3）"
    ],
    "ablations": [
      "### 9.3 消融与鲁棒性"
    ],
    "robustness_generalization": [
      "### 9.3 消融与鲁棒性",
      "污染鲁棒性实验在 AIOps 上逐步把训练异常量增加至 0.5×–8×。Fig. 5 显示高污染时 CAPMix 的 F1 和 precision 比原始 CAP 更稳定；正文未给每个污染率的数值。超参数图 Fig. 6 比较 γ 与 α：AIOps 对 γ 更敏感，WADI 对 α 更敏感，支持“标签容忍度与 Mixup 对不同数据结构的作用不同”。（PDF pp.8–9, §4.4–4.5, Figs. 5–6）"
    ],
    "industrial_validation": [
      "### 9.4 生产案例"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "见档案 §10.B；保持为分析而非已证实结论"
    ],
    "evidence_gaps": [
      "论文没有单独的“Limitations”章节，也没有给出完整的局限清单。它通过超参数分析指出 γ 和 α 对不同数据集的重要性不同（§4.5），并在生产章节强调标签稀疏、不可靠、计算延迟和正常事件高度多样（§5.2）。",
      "正文用阈值扫描报告 Best RPA-F1；该指标适合比较分数可分性，但不是无标签线上阈值下的实际告警精度。部署中的 POT 被提及，未见与固定阈值/校准方案的系统对比。",
      "主文写 $Y^r$ 包含专家标注的原始标签，但又强调不要求训练集含异常；训练异常在每个基准上是否带标签、标签缺失时如何训练 contaminated samples，未明确到足以完全复现。",
      "本地 PDF 扉页有正式出版信息占位符；阅读对象的内容与题名相符，但版本元数据需依 DOI / 会议记录核对。"
    ]
  },
  "research_implications": [
    "CAPMix 最有价值的抽象不是“多做几种数据增强”，而是把增强样本本身当作带不确定性的伪监督：一个合成片段可能确实破坏了形态，也可能只是正常的工作负载变化；其异常标签需要按相似度降低置信度。Mixup 再限制模型不要把某一类夸大的注入形状当成唯一的故障边界。这个思路对生产监控有用，但它仍然把判别依据主要放在窗口形态和训练标签上，缺少“为什么业务负载变了”的外部证据。",
    "- [分析推断] 用负载、发布、扩缩容及服务调用等上下文条件化正常状态与伪异常置信度，检验同时发生负载变化与故障时的可分性。 - [分析推断] 将单均值中心改成可校准的多正常状态模型，并报告状态覆盖、未知模式和误报成本。 - [分析推断] 在固定无监督阈值、事件级成本及跨集群部署下复验，以弥补最佳阈值和单生产案例的证据边界。"
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
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "PDF pp.1–3, §1–3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§1, §5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "Table 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§1, §3.3.2–3.3.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§1, §5.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "Algorithm 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "PDF pp.5–6, §11, §3.4, Algorithm 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "§3.3.1, Eq. (1), Algorithm 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "PDF pp.3–4, Table 1, Table 1, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf",
      "locator": "Eq. (3), Eq. (4)",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "9e3d17c1965be987b1fa541edd9c1756cb6d9938c33ded5a1475d61f9a61abad",
    "reading_note_sha256": "f8b7a3d2b31dbe7bb9034d717de22ddcdca0f23ee19244dd14564516e4ecccde",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "823dcdbcd1ed3aa4b7a0644b97c1f7b5c19857ebfd43684849edf4dd398c4c60"
  },
  "knowledge_card_path": "papers/capmix/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
