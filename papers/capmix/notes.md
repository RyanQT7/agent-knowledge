# CAPMix：面向噪声与动态环境的鲁棒 KPI 异常检测

## 1. Metadata

- Title: CAPMix: Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments
- Authors: Xudong Mou, Rui Wang, Tiejun Wang, Zexin Wu, Fangda Guo, Jie Sun, Shiru Chen, Penghao Zhang, Tiezi Zhang, Tianyu Wo, Hao Peng, Chunming Hu, Xudong Liu, Renyu Yang
- Year / Venue: 2026 / ASE（按本地论文清单及 DOI 元数据）
- CCF: A（采用已确认的论文清单等级）
- DOI: [10.1145/3832783.3834487](https://doi.org/10.1145/3832783.3834487)
- Code / data: [CAPMix code](https://github.com/alsike22/CAPMix); [AIClusterKPI dataset](https://doi.org/10.5281/zenodo.19926114)
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local File: [CAPMix PDF](../../sources/papers/tsad-2024-2026/2026/ASE/CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf)
- 元数据核对说明：本地 PDF 扉页仍有 ACM 模板占位信息（如 “Conference acronym XX”、2018 和空 DOI），与文件所对应的 ASE 2026 / ACM DOI 不一致。论文主题和方法来自该 PDF；正式会议元数据采用本地清单与 DOI，不把扉页占位项当作正式出版信息。原始汇总 CSV 缺失，无法回查其原始条目。

## 2. One-Sentence Summary

CAPMix 以 CutAddPaste 生成可控时序伪异常，再用 DTW 距离修正“看起来仍正常”的伪异常标签，并在输入空间与 TCN 潜在空间做 Mixup，以降低训练污染、正常波动和合成异常失真对 KPI 判别边界的影响。

## 3. Problem

论文关注 AIOps 中的 KPI 时间序列异常检测：输入是按时间排序、每步有 $d$ 个 KPI 的多变量序列；模型将长度为 $t$ 的滑动窗口判为正常或异常，并输出异常分数。真实服务中的 KPI 具有时间依赖、非平稳性和跨指标相关性；部署、自动扩缩容、采集抖动、日志轮转等正常运维活动也会产生尖峰或短时变化。训练集还可能含未充分标注的真实异常。

作者把合成异常与真实故障模式不匹配称为 **Anomaly Shift**，区分两个方向：

1. **低区分度**：合成异常过于接近正常波动，却被赋予确定异常标签，模型因错误监督而把正常抖动当成故障。
2. **过高区分度**：合成异常过于夸张（如不现实的突变或极端尖峰），模型学到只对夸张模式敏感的边界，漏掉细微但重要的真实异常。

这和“正常性假设”方法的弱点互补：仅拟合正常数据的检测器容易受含噪或污染的训练集影响；只靠合成异常训练则依赖注入模式与真实故障足够匹配。（PDF pp.1–3, §1–3.2）

## 4. Motivation

论文以生产监控中的误报为动机：§1 报告某生产环境任务级失败率为 19.3%，并展示 OC-SVM 会把正常 KPI 波动持续误报；作者举例说，5 分钟采样下这类误报可持续一整天。对 anomaly-assumption 方法，作者认为“注入异常”不自动解决问题：异常生成的强度与模式空间需要校准，而真实故障类型异质、标签稀缺，难以保证合成分布覆盖真实故障。

CAPMix 的设计因此拆成两件事：给合成样本更可信的置信度（Label Revision），并限制合成样本把边界推向不现实的极端（Dual-Space Mixup）。

## 5. Core Idea

不是把所有注入样本都视为同等可信的异常，而是将“伪异常像不像正常”和“伪异常离真实数据流形是否过远”分别处理：DTW 距离近的注入样本获得软标签；输入和特征空间 Mixup 则让模型看到正常与异常之间的连续样本和标签，降低对单一人工模式的过拟合。论文用轻量三块 TCN 学习时序表示和二分类概率。（PDF pp.3–6, §3.2–3.4）

## 6. Architecture / Workflow

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

## 7. Key Concepts

- **Anomaly Shift**：合成异常与真实异常分布不匹配，既可能太像正常也可能偏离真实范围。
- **Prior-guided anomaly injection**：从真实窗口中截取片段并控制趋势扰动，构造结构化模式，而非只加入独立随机噪声。
- **DTW label revision**：按时序形态距离对伪异常监督做软化。
- **Dual-space Mixup**：输入时序和隐藏表示层分别插值，以同时改变可见样本及学习表示。
- 与已有知识的关系：属于“异常增强 + 鲁棒判别边界”的检测路线，不是在线自适应或故障根因定位系统；它学习 KPI 窗口标签，不显式建模服务依赖图、因果关系或 workload 上下文。

## 8. Method

### 8.1 窗口表示与 CutAddPaste

§3.1 将长度 $t$ 的多变量窗口写为 $X\in\mathbb{R}^{t\times d}$，每条长序列以步幅 δ 切成窗口。作者用结构分解 $X=\Gamma(2\pi\omega T)+\Theta(T)$ 描述形状函数、季节性和趋势；跨维度相关性可由协方差表示。这个分解是解释合成扰动类型的表示，并非模型另行估计的潜变量。

CutAddPaste 从目标窗 $X^i$ 与随机源窗 $X^j$ 取片段，随机选择长度 $r\ge\zeta$、源位置和粘贴位置；在选择的 $e$ 个变量上可加趋势项 $V_{trend}=\rho mR$，其中斜率向量 $m$ 的分量在 $(-1,1)$ 内采样。之后将片段覆盖目标窗口对应区间（§3.3.1, Eq. (1), Algorithm 1）。

注入目标覆盖论文讨论的结构变化：A1 子序列扰动（正文把形状变化与跨变量相关性变化分别展开）、A2 季节性、A3 趋势，以及 A4/A5 全局和上下文点异常。Table 1 将覆盖类型概括为 global、contextual、shape、seasonal、trend；正文对 A1 的 shape/correlation 细分比表格缩写更细，不能据此把两种标记强行视作完全相同的五类定义。（PDF pp.3–4, Table 1, Fig. 3）

### 8.2 DTW Label Revision（LR）

作者先假定训练序列的大多数窗口正常，以窗口均值序列构建正常中心：

\[
C_n=\frac{1}{N}\sum_{i=1}^{N}X_i. \tag{2}
\]

对注入样本 $X^a$ 计算 $d(X^a,C_n)$。用原始训练窗口到 $C_n$ 的距离均值 μ_d 和标准差 σ_d 设置阈值 μ_d+γσ_d（Eq. (3)）。若合成样本距离不超过阈值，则判为模糊、赋软异常标签 $y^r=1/\gamma$；超出则赋硬标签 $y^r=1$（Eq. (4)）。γ 因而同时控制模糊区宽度和软标签幅度。原文写 γ≥0，但 Eq. (4) 的 1/γ 在 γ=0 时无定义；若软标签要落在 [0,1]，还需 γ≥1。论文未在正文明确这一边界及各数据集取值，复现时需核对配置。作者没有采用距离比例作为连续标签，理由是额外计算和对距离尺度敏感。

解释边界：它按与**单一均值中心**的 DTW 距离修正，不是从标注的真实故障类别估计异常置信度；均值中心以及“大多数训练窗口正常”的假设可能不适合强多模态正常状态或严重污染数据。（PDF pp.4–5, §3.3.2, Eqs. (2)–(4)）

### 8.3 TCN 与 Dual-Space Mixup（DS）

编码器有三个 temporal convolutional block；每块依次使用 Conv1D、BatchNorm、ReLU、MaxPool1D，第一块另加 Dropout，将 $t$ 长度窗口映射为固定表示 $z_i$。另有一层隐藏层的 MLP 投影器，包含 BN 与 ReLU，将表示映射到二维 $q_i$，再用 softmax 输出正常/异常概率。（PDF p.5, §3.3.3–3.4）

在可配置深度 $l$ 做 Mixup：

\[
X^{(l)}_{mix}=\lambda f^{(l)}(X_i)+(1-\lambda)f^{(l)}(X_j),\quad
y^{(l)}_{mix}=\lambda y_i^{(l)}+(1-\lambda)y_j^{(l)}. \tag{5}
\]

$l=0$ 时是原始输入空间 Mixup；在中间层则是在 TCN 特征空间插值。标签同步插值，避免混合输入仍被硬标成一类。论文把这一对设计合称 DS-Mixup。主文描述 α 为 mixup ratio 的控制超参数，但未在文字中说明 λ 的采样分布、确切默认层位或逐数据集设置，不能补写常见的 Beta 分布作为论文事实。

### 8.4 目标函数与测试

投影器通过 softmax 得到 $[1-p_i,p_i]$，其中 $p_i$ 是异常概率；以 BCE 训练：

\[
\mathcal{L}=-\frac{1}{N}\sum_i[y_i\log p_i+(1-y_i)\log(1-p_i)]. \tag{7}
\]

测试时 $S_i=p_i\in[0,1]$，按预设阈值 τ 产生二元标签（Eq. (8)）。文中提到实际部署可用 POT 等无监督方法从分数得到告警阈值；主要实验报告的 Best RPA-F1 则是扫阈值所得，二者不是同一设置。（PDF pp.6–7, §3.4, §4.1.2）

## 9. Experiments

### 9.1 数据、基线与指标

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

### 9.2 主结果

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

### 9.3 消融与鲁棒性

Table 4（10 次运行）报告平均分：无增强 TCN 29.14；加入 CutAddPaste（CAP）46.26；在 CAP 上加 LR 为 47.34；用 CAP + Mixup（不含 LR）为 57.49；完整模型 60.69。该表显示 Mixup 在该实验组合中的平均增益大于 LR，但不意味着 LR 无效：CAP-LR 在 AIOps、SMD、ASD 上提高，且两模块分别处理不同方向的 Anomaly Shift。UMAP 图（Fig. 4）显示伪异常与真实异常簇更接近、与正常区域重叠较少；这是可视化证据，不是分布距离的正式统计检验。（PDF pp.7–8, §4.3, Table 4, Fig. 4）

污染鲁棒性实验在 AIOps 上逐步把训练异常量增加至 0.5×–8×。Fig. 5 显示高污染时 CAPMix 的 F1 和 precision 比原始 CAP 更稳定；正文未给每个污染率的数值。超参数图 Fig. 6 比较 γ 与 α：AIOps 对 γ 更敏感，WADI 对 α 更敏感，支持“标签容忍度与 Mixup 对不同数据结构的作用不同”。（PDF pp.8–9, §4.4–4.5, Figs. 5–6）

### 9.4 生产案例

作者在 Kuaishou 的 KAIOps 集群系统集成 CAPMix；数据包含 16 天、每分钟采样的七节点 KPI，节点级信号包括 CPU、内存、I/O、网络，另有 API latency、pending tasks、pod restarts 等集群指标。Table 5 报告测试集 3,029 点、1,117 个异常点 / 145 个异常事件；案例表中 RPA precision 0.80、F1 0.79、PR-AUC 0.87、NAB 0.76。Fig. 8 对比指出日志轮转、采集扰动及负 CPU 等监控伪影会触发基线，而 CAPMix 分数较低；持续故障如 memory leak 则获得持续响应。作者还描述用操作员确认的误报和真故障反馈周期性修正 LR，但没有给出反馈策略、更新频率及独立对照实验细节。（PDF pp.9–10, §5, Table 5, Fig. 8）

## 10. Strengths

- 把合成异常不匹配拆成欠区分与过区分两种错误来源，并分别用软标签与两空间插值处理，机制对应关系清楚。
- 消融、污染强度变化和真实运维案例相互补充；生产案例明确区分了采集/运维引起的正常尖峰与 memory leak 等故障。
- 不要求每套训练数据都有真实异常；在无异常训练集上也能靠合成样本学习判别器。代码和 AIClusterKPI 数据公开声明降低了后续复查门槛。
- TCN 架构较轻，部署叙述包含实际监控工作流，而非只报告离线基准分数。

## 11. Limitations

### 作者明确讨论 / 本文未明确讨论

- 论文没有单独的“Limitations”章节，也没有给出完整的局限清单。它通过超参数分析指出 γ 和 α 对不同数据集的重要性不同（§4.5），并在生产章节强调标签稀疏、不可靠、计算延迟和正常事件高度多样（§5.2）。
- 正文用阈值扫描报告 Best RPA-F1；该指标适合比较分数可分性，但不是无标签线上阈值下的实际告警精度。部署中的 POT 被提及，未见与固定阈值/校准方案的系统对比。
- 主文写 $Y^r$ 包含专家标注的原始标签，但又强调不要求训练集含异常；训练异常在每个基准上是否带标签、标签缺失时如何训练 contaminated samples，未明确到足以完全复现。
- 本地 PDF 扉页有正式出版信息占位符；阅读对象的内容与题名相符，但版本元数据需依 DOI / 会议记录核对。

### 我的分析 / 尚待验证

- $C_n$ 使用训练窗口均值，无法天然表达多种模式的正常工作态；不同业务负载、发布阶段或昼夜周期若平均后形成“中间态”，DTW 近邻判定可能同时误伤正常模式并软化真实异常。
- 注入模板来自切片、趋势斜率及设定的点/上下文异常；当故障由依赖传播、长时间累积或业务语义变化产生时，合成覆盖可能不足。作者的 UMAP 图不足以证明对未知故障类型的分布覆盖。
- 输入仍是 KPI 窗口。生产数据提到资源利用率和集群级指标，但没有明确将 deployment、业务负载、trace、调用关系或故障工单作为条件变量建模；模型可压低波动告警，却没有解释波动由何种业务操作产生。
- 真实生产结果来自单一企业 / 集群案例，且总数据点、train/test 点数及事件数在 Table 5 中口径不完全透明；尚需独立场景复验。

## 12. Relationship to Existing Knowledge

CAPMix 与常见“只建模正常模式”的检测器相比，主动构造伪异常并学习监督边界；与纯 CutAddPaste 相比，它校准近正常伪异常的标签并把过度显著样本向训练分布插值。相较于后续阅读中的 test-time adaptation 路线，它主要在训练阶段改善表示和边界，不依赖连续测试时更新。它解决的是“窗口级异常识别”，不等于对告警归因、故障定位或运维动作的端到端 AIOps 系统。

批内待比较：与 When Model Meets New Normals 的“顺应新正常”相比，CAPMix 能否在不改阈值/在线模型的情况下处理运行状态漂移；与 CAROTS 的因果增强相比，CAPMix 的先验注入是否仅靠形态覆盖；这些问题留待三篇笔记完成后在批次 Review 中统一判断。

## 13. My Understanding

CAPMix 最有价值的抽象不是“多做几种数据增强”，而是把增强样本本身当作带不确定性的伪监督：一个合成片段可能确实破坏了形态，也可能只是正常的工作负载变化；其异常标签需要按相似度降低置信度。Mixup 再限制模型不要把某一类夸大的注入形状当成唯一的故障边界。这个思路对生产监控有用，但它仍然把判别依据主要放在窗口形态和训练标签上，缺少“为什么业务负载变了”的外部证据。

## 14. Questions

1. 在多模态正常状态下，单一均值中心 $C_n$ 是否会落在任何真实运行态都不常见的位置？作者没有报告按状态聚类或多中心敏感性分析。
2. 训练异常标签来源是什么、缺标签时污染窗口如何进入 BCE？需从代码或作者的补充材料核实。
3. 业务负载、发布/扩缩容事件与 KPI 同时变化时，如何区分正常变更和真实故障？只看 KPI 形态是否足够？
4. Best RPA-F1 的优势在无标签、固定阈值和告警成本约束下是否仍成立？

## 15. Related Work

- CutAddPaste：CAPMix 使用的基础时序异常注入方法（参考文献 [11]，KDD 2024）。
- RedLamp：异常增强和伪异常标签修订路线，CAPMix 在 Table 3 中纳入比较。
- RoCA / AOC / SHUE：分别代表污染鲁棒对比、一类边界融合及正常模式敏感性增强等基线；其结果显示不同数据集上不存在单一机制全面占优。
- 本批其他论文链接将在对应笔记完成后通过批次 Review 补齐，避免先写入未核对的交叉结论。

## 16. Useful Quotes / Definitions

- **Anomaly Shift**：合成异常与真实故障模式存在可区分性不足或偏离过大的错位。（意译自 §1、§3.3）
- **Label Revision**：按合成窗口到正常中心的 DTW 距离，把模糊伪异常的 one-hot 异常标签降为软异常标签。（§3.3.2）
- **Dual-Space Mixup**：在原始输入与中间特征空间进行样本及标签插值。（§3.3.3, Eq. (5)）

## 17. Tags

`TSAD` `KPI` `AIOps` `normal-fluctuation` `anomaly-augmentation` `label-noise` `DTW` `mixup` `robustness` `production`
