# Knowledge Dossier — GCAD: Anomaly Detection in Multivariate Time Series from the Perspective of Granger Causality

## 1. Basic Information

- **English title**: GCAD: Anomaly Detection in Multivariate Time Series from the Perspective of Granger Causality
- **中文译名**：从 Granger 因果视角检测多变量时间序列异常
- **Authors**: Zehao Liu, Mengzhou Gao, Pengfei Jiao
- **Venue / year / CCF**: AAAI 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf](../../sources/papers/tsad-2024-2026/2025/AAAI/GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: 基于非线性 Granger 影响变化的多变量异常检测
- **Method tags**: TSAD multivariate Granger-causality gradient-sensitivity dynamic-causal-graph normal-graph-template causal-deviation AAAI-2025

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 多变量 TSAD 中，异常除了改变数值 / 预测误差，也可能使变量间 Granger predictive dependency 发生变化。（§§1–3, PDF pp.2–5）
- **[实验支持]** 在 SWaT、SMD、MSL、SMAP、PSM 上用窗口级图相对正常图模板的偏差检测异常。（Tables 1–3, PDF pp.5–6）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

GCAD 研究多变量传感器时序异常检测。作者的核心动机是，常见动态图 / GNN detector 虽构图，但通常仍以 prediction / reconstruction error 告警，不能直接说明变量关系怎样影响演化。作者提出：某变量异常时，除值 / 预测误差变化外，跨变量 Granger 依赖模式也可能偏离正常参考；例如进水压力提升时出水压力原应同步变化，若管路泄漏，既有预测关系可能被破坏。（PDF pp.1–3, §§1–2）

输入按最大滞后 $\tau$ 滑动成多变量窗口。模型最终对每个窗口输出 abnormality 判断 / score。方法未用 Trace、service topology、业务负载或事件语义；其“因果”是基于可预测性的 Granger operational definition，不等于结构因果模型、干预效应或物理根因自动识别。（PDF pp.2–4, §3）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 基于图的 detector 常以 prediction error 作为唯一检测准则，未把关系结构变化直接作为异常证据。（§1）
- **[分析推断]** 真实故障、正常业务阶段切换都可能改变预测依赖；需要区分结构变化来源。

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 传统线性 Granger 对非线性时序有限；常用相似性图可能对称，不符合有向预测关系。（§2–3）
- **[作者明确限制]** 仅建模 pairwise binary causal relationships，无法直接表达高阶多变量交互。（Conclusion, PDF p.7）
- **[分析推断]** 预测 loss 梯度只是模型局部敏感度 proxy，并非干预验证的真实 causal graph。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

GCAD 用一个预测型 Mixer 作为梯度生成器，对每个目标通道的预测误差分别回传到各输入通道历史窗口，以预测损失梯度幅值近似动态非线性 Granger 影响，再消除对称相似性并与训练正常窗口的平均因果图比较，得到关系偏离与自时序偏离分数。

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 基于图的 detector 常以 prediction error 作为唯一检测准则，未把关系结构变化直接作为异常证据。（§1）
- **C2（第4节挑战）**：[分析推断] 真实故障、正常业务阶段切换都可能改变预测依赖；需要区分结构变化来源。

### 7.1 以每个目标通道 $j$ 的平方预测误差 $L_{t

- **作者技术描述**：**[作者主张]** 以每个目标通道 $j$ 的平方预测误差 $L_{t,j}$ 构造独立 backward pass。（Eq. 1）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 通过 $|\partial L_{t

- **作者技术描述**：**[作者主张]** 通过 $|\partial L_{t,j}/\partial x_{\phi,i}|$ 对滞后和输入值分布积分，形成 $a_{i,j}$。（Eqs. 2–5）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 用 $\tilde A_{ij}=\max

- **作者技术描述**：**[作者主张]** 用 $\tilde A_{ij}=\max(0,A_{ij}-A_{ji})$ 去除对称关系，再以阈值 $h$ 稀疏化；不保证 DAG。（Eq. 6）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 对正常训练窗口抽样并求平均图 $A_{norm}$

- **作者技术描述**：**[作者主张]** 对正常训练窗口抽样并求平均图 $A_{norm}$；测试时计算因果关系相对偏差 $S_c$、时间对角偏差 $S_t$，最终 $S=S_c+\beta S_t$。（Eqs. 7–12）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. Architecture Overview

```text
普通窗口 X_{t-1} → Mixer prediction network → 预测 ŷ_t
                                   ↓ 对每个目标 j 单独构造平方误差 L_{t,j}
                对所有输入通道 i、滞后 φ 回传 ∂L_{t,j}/∂x_{φ,i}
                                   ↓ 积分 / 汇总梯度幅值为 A_{i,j}
                eA_ij = max(0, A_ij − A_ji)，再阈值 sparsify
                                   ↓
训练正常窗口随机抽样求均值 A_norm；测试窗口各得 eA_test
                                   ↓
因果图相对偏差 S_c + β × 对角自时序偏差 S_t → anomaly score
```

可分成四部分：预测器、基于梯度的 Granger graph、因果图稀疏化、正常因果模板偏差打分。Mixer 是工具性梯度生成器；论文新意主要是把预测 loss 对输入各通道的敏感度映射成窗口级有向关系，再检测 graph pattern shift。（PDF p.3, Fig. 1, §3）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. Method in Detail

#### 5.1 Prediction-based Gradient Generator

一个窗口的历史输入 $X_{t-1}=\{x_{t-\tau},\ldots,x_{t-1}\}\in\mathbb R^{N\times\tau}$，预测当前向量 $\hat y_t=f(X_{t-1})$。GCAD 用 $L$ 层 Mixer predictor；每层交替 temporal mixing MLP 和 feature mixing MLP，前者跨时间混合，后者跨变量混合，skip connections 后经 fully-connected layer 输出各通道当前点预测。训练只用 MSE：

$$L_{train}=\operatorname{MSE}(\hat y_t,y_t).$$

为区分不同目标变量的误差来源，定义目标通道 $j$ 的独立平方预测误差：

$$L_{t,j}=(\hat y_{t,j}-y_{t,j})^2.\tag{1}$$

对每个 $L_{t,j}$ 反传，可得其对每个输入通道 $i$、滞后时刻 $\phi$ 的梯度；合并为 $G_t\in\mathbb R^{N\times N\times\tau}$。这样 $G_{t, i,j,\phi}$ 描述改变输入变量 $i$ 的过去值时，目标 $j$ 的预测误差在当前预测器局部如何变化。（PDF pp.3–4, §3, Eq. 1, Fig. 1）

#### 5.2 用 loss 梯度量化非线性 Granger 影响

原始 Granger 关系定义为：若替换变量 $i$ 的过去历史会改变变量 $j$ 的预测 $f_j$，则 $i$ Granger-causes $j$（Definition 1, Eq. 2）。作者在输入点附近引入扰动 $x^*_{t',i}=x_{t',i}+\Delta$（Eq. 3），并以小扰动下预测误差变化的局部导数近似：

$$\lim_{\Delta\to0}|L_{t,j}-L^*_{t,j}|=\left|\frac{\partial L_{t,j}}{\partial x_{t',i}}\right||\Delta|.\tag{4}$$

从最大 lag 中汇聚绝对梯度，并对兴趣输入分布 $P$ 积分，形成因果权重：

$$a_{i,j}=\int_{t-\tau}^{t-1}\left|\frac{\partial L_{t,j}}{\partial x_{\phi,i}}\right|P(x_{\phi,i})\,dx_{\phi,i}.\tag{5}$$

所有 $a_{i,j}$ 组成窗口关系矩阵 $A$。作者指出 predictor 可微，因此局部梯度可计算；简化下 $P$ 可取 uniform。实际要特别区分：论文把预测误差的输入梯度作为 Granger causality proxy。它衡量局部 predictive sensitivity，梯度会随 predictor 拟合、输入位置、误差残差而变；不等同于真实系统因果图的观测或干预验证。（PDF pp.4–5, §3 Granger Causality Discovery, Eqs. 2–5）

#### 5.3 Causality Graph Sparsification

作者认为 cosine 等对称相似性常会在 $A_{ij}$ 和 $A_{ji}$ 两方向同时出现，而有向 Granger 关系不应对称；据此定义：

$$\tilde A_{i,j}=\max(0,A_{i,j}-A^\top_{i,j}),\quad i\ne j;\qquad \tilde A_{i,i}=A_{i,i}.\tag{6}$$

再对小于稀疏阈值 $h$ 的项置零。该差分去除对称共性并保留净方向性，阈值过滤小权重噪声。它不能保证所得图是 DAG；论文明确说非线性图难以严格保证无环。对角线保留，表示变量自身历史对自身预测误差的敏感度。（PDF p.5, §3 Causality Graph Sparsification, Eq. 6）

#### 5.4 Normal causal template and anomaly score

预测器训练后，从 normal training windows 按 Bernoulli 参数 $p$ 抽样，计算稀疏图 $\tilde A_{norm,i}$，均值作为总体正常关系模板：

$$A_{norm}=\frac1n\sum_{i=1}^{n}\tilde A_{norm,i}.\tag{7–8}$$

对每个测试窗口计算 $\tilde A_{test,i}$（Eq. 9）。关系偏差定义为逐项相对偏差求和：

$$S^c_i=\sum\frac{|\tilde A_{test,i}-A_{norm}|}{|A_{norm}|+\epsilon}.\tag{10}$$

作者进一步取对角元素偏差形成 time-pattern score $S^t_i$（Eq. 11），然后合并：

$$S_i=S^c_i+\beta S^t_i.\tag{12}$$

由于 $S^c$ 本身已包含主对角，$\beta=0$ 时仍有自历史模式信息；$\beta$ 是对额外 diag emphasis 的超参数。分数的参照是训练所有 normal windows 的平均因果图，因而是一个静态、全局正常模板；论文没有展示先按业务态聚类或条件化再比较。（PDF pp.5–6, §§3 Causal Deviation Scoring, Eqs. 7–12）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (6)、Eq. (7)、Eq. (9)、Eq. (11)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：5.2 用 loss 梯度量化非线性 Granger 影响；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.4 Normal causal template and anomaly score及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

GCAD 用一个预测型 Mixer 作为梯度生成器，对每个目标通道的预测误差分别回传到各输入通道历史窗口，以预测损失梯度幅值近似动态非线性 Granger 影响，再消除对称相似性并与训练正常窗口的平均因果图比较，得到关系偏离与自时序偏离分数。

## 9. Experimental Evidence

#### 精读笔记原章节：6. Experiments

#### 6.1 Data, metrics, baseline protocol

- **Datasets**：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1）
- Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，不应直接把这些行当作原始全量规模。（PDF p.5, Table 1）
- **Baselines**：DAGMM、USAD、GDN、Anomaly Transformer、GANF、MEMTO 六种。（PDF p.5, §Experimental Setup）
- **训练 / 验证**：normal unlabeled data 的 80% 用于训练，20% 验证；含标签异常数据作为测试。报告 AUROC / AUPRC，10 次实验求均值。（PDF pp.5–6, Implementation Details）
- 不报告点级 F1 / threshold selection / Event-F1 或线上 false alarm period；AUPRC 能部分应对异常不平衡，但仍是离线 benchmark 排序指标。（PDF p.5）

#### 6.2 Main results

Table 2 的 AUROC / AUPRC（模型：ROC / PR）：

| Dataset | GCAD AUROC | GCAD AUPRC | 表内比较边界 |
| --- | ---: | ---: | --- |
| SWaT | .8690 | .7758 | 两项均高于所列对照 |
| SMD | .9533 | .7502 | 两项均高于所列对照 |
| MSL | .7658 | .3679 | 两项均高于表内结果，异常率很低 |
| SMAP | .7273 | .4555 | ROC 高；PR 略低于 GANF .5259 |
| PSM | .7618 | .6136 | 表内高于列出的 baseline |

作者总结大多数指标 / 数据集达最佳；但 SMAP AUPRC 是 GANF .5259 高于 GCAD .4555。MSL / SMAP 异常率分别仅 .74% / 2.14%，PR 值低，需谨慎解释排序成绩。（PDF pp.5–6, Tables 1–2）

#### 6.3 Ablations and graph example

- **去掉 sparsification**：SWaT ROC / PR .8690/.7758→.8559/.7676；SMD .9533/.7502→.9531/.6915，说明稀疏化对 PR / noise reduction 有帮助，但 SMD AUROC 变化很小。（PDF p.6, Table 3）
- **去掉因果关系 GC**：SWaT .8478/.7513，SMD .9405/.6424，特别是 SMD AUPRC 大降；支持关系结构比预测误差单项有增益。（Table 3）
- **去掉时间对角 TC**：SWaT .8400/.7558，SMD .9498/.6748；作者据此指出非对角因果依赖与自历史偏差互补。（Table 3）
- **Lag $\tau$ 与 threshold $h$**：Fig. 2 显示二者有非单调权衡：lag 太短只见近邻关系，lag 长可捕获复杂影响但对短异常不敏感；$h$ 太低引入噪声边，太高丢掉弱但有用的因果信息。（PDF p.6, Fig. 2）
- **案例**：SWaT 化学泵 P203/P205 被关停后，AIT202 / AIT501、FIT301 / FIT503 的因果偏差图变化；矩阵与物理系统文字描述具有对应关系，帮助解释分数。（PDF p.7, Figs. 3–5）但这是一个 case study，不是系统性故障变量 localization 定量基准。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. Limitations and Reproduction Value — 分析推断

如果正常业务负载改变了预测依赖（例如开关服务 / 控制回路）但仍符合合法操作，单一 $A_{norm}$ 无法自动区分“新正常机制”与故障关系破坏。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 分析推断

分数表示因果预测结构偏离，可作为定位线索；从预测依赖直接称为实际根因还需要物理图 / 操作记录验证。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 分析推断

当前定义逐变量两两评分；多故障共同改变预测关系时可能表现为若干 pair 边差异，无法表示高阶协同机制，作者对此限制有所承认。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确说明（归属未明确）

**只建模变量对变量的 binary causal pairs**，不能直接表示多变量组合因果关系；Conclusion 将此列为限制与 future work。（PDF p.7）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确说明（归属未明确）

论文解释 Granger causality 是预测可提升关系，不是完整物理因果。Sparsification 不保证 DAG。（PDF pp.4–5）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 证据边界

$A_{norm}$ 是训练 normal windows 的均值单模板，没有条件化负载、时段、控制阶段或服务版本。合法多模态状态切换导致因果图变化时也可能升高异常分数；论文未用已知业务态做对照。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 证据边界

梯度对预测误差求导是模型局部敏感度；它受预测器是否学好、loss 残差和输入分布影响。论文没有通过真实 cause graph ground truth 测量边识别准确率，也没有比较 intervention / operator logs。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 证据边界

threshold-independent AUROC / AUPRC 提供 score 排序证据，但没有固定 FPR 下报警数、事件时延、diagnosis precision 或成本；仅 SWaT 定性案例说明物理关系。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 证据边界

Table 1 中部分 train/test 样本数显著小于标准公开数据常用规模；复现应确认其拆分 / 重采样流程及 Table 2 是否基于完全相同 pipeline。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 证据边界

正文未报告代码仓库，且训练细节较简略；重现需确认 $P$ 近似、梯度积分数值实现、Bernoulli 样本数、threshold $h$ / $\beta$ 搜索、滑窗标签回填以及起点 / 末端的 graph 计算。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 以状态条件图模板 / 图混合模型表示多种正常负载状态，检查均值模板是否构成不存在的中间关系图。
- **[分析推断]** 将梯度图和真实 topology、故障注入、operator event / Trace 对齐，区分 predictive sensitivity 与可验证因果关系。
- **[分析推断]** 构造正常负载变化与故障并发测试，量化图模板切换与在线更新的污染风险。
- **[分析推断]** 加入高阶交互图、固定 FPR 的运行点、事件级时延和跨实体迁移评测。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **CAROTS**：同属 Granger / causal prediction relation TSAD。GCAD 直接由 predictor 的 loss gradient 构造窗口图并比较模板；CAROTS 以估计 Granger 图设计 causal-preserving / causal-disturbing augmentation 与预测异常分数。两者都未将业务 context / Trace 作为正常变化条件。
- **CCM-TAD**：其 causal temporal mask 只限制 future leakage；GCAD 才尝试估计跨变量 Granger predictive dependency。不能混为同类因果主张。
- **Graph-MoE**：窗口 attention graph 与层级路由用于条件 density；GCAD 用窗口因果图相对正常图偏差作为检测 score。
- **OracleAD / Structured Temporal Causality**：OracleAD 将每变量历史预测表示经 MHSA 转到 latent space，再比较 pairwise distance SLS；结构可解释但不是显式 Granger graph。
- **SARAD**：检测 attention association下降与空间 progression；它衡量 feature reconstruction association shift，不声称变量间 causality。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.1–3, §§1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.2–4, §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.2–5, §§1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.5–6 | 精读笔记保留的原文定位 |
| Challenges / prior methods | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | §1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | §2–3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.7 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.3, §3, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.3–4, §3, Eq. 1, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | Eq. 2, Eq. 3 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.4–5, §3, Eqs. 2–5 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.5, §3, Eq. 6 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | Eq. 9 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | Eq. 11 | 精读笔记保留的原文定位 |
| Method / formulas | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.5–6, §§3, Eqs. 7–12 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.5, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.5 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF pp.5–6 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.6, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.6, Fig. 2 | 精读笔记保留的原文定位 |
| Experimental evidence | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.7 | 精读笔记保留的原文定位 |
| Limitations | GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf | PDF p.7 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "gcad",
  "title_en": "GCAD: Anomaly Detection in Multivariate Time Series from the Perspective of Granger Causality",
  "title_zh": "从 Granger 因果视角检测多变量时间序列异常",
  "authors": [
    "Zehao Liu",
    "Mengzhou Gao",
    "Pengfei Jiao"
  ],
  "year": 2025,
  "venue": "AAAI",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/AAAI/GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
  "reading_note_path": "papers/gcad/notes.md",
  "code_url": null,
  "research_area": "基于非线性 Granger 影响变化的多变量异常检测",
  "method_tags": [
    "TSAD multivariate Granger-causality gradient-sensitivity dynamic-causal-graph normal-graph-template causal-deviation AAAI-2025"
  ],
  "research_scenario": "- [作者主张] 多变量 TSAD 中，异常除了改变数值 / 预测误差，也可能使变量间 Granger predictive dependency 发生变化。（§§1–3, PDF pp.2–5） - [实验支持] 在 SWaT、SMD、MSL、SMAP、PSM 上用窗口级图相对正常图模板的偏差检测异常。（Tables 1–3, PDF pp.5–6）",
  "research_problem": "GCAD 研究多变量传感器时序异常检测。作者的核心动机是，常见动态图 / GNN detector 虽构图，但通常仍以 prediction / reconstruction error 告警，不能直接说明变量关系怎样影响演化。作者提出：某变量异常时，除值 / 预测误差变化外，跨变量 Granger 依赖模式也可能偏离正常参考；例如进水压力提升时出水压力原应同步变化，若管路泄漏，既有预测关系可能被破坏。（PDF pp.1–3, §§1–2） 输入按最大滞后 $\\tau$ 滑动成多变量窗口。模型最终对每个窗口输出 abnormality 判断 / score。方法未用 Trace、service topology、业务负载或事件语义；其“因果”是基于可预测性的 Granger operational definition，不等于结构因果模型、干预效应或物理根因自动识别。（PDF pp.2–4, §3）",
  "core_challenges": [
    "[作者主张] 基于图的 detector 常以 prediction error 作为唯一检测准则，未把关系结构变化直接作为异常证据。（§1）",
    "[分析推断] 真实故障、正常业务阶段切换都可能改变预测依赖；需要区分结构变化来源。"
  ],
  "existing_method_limits": [
    "[作者主张] 传统线性 Granger 对非线性时序有限；常用相似性图可能对称，不符合有向预测关系。（§2–3）",
    "[作者明确限制] 仅建模 pairwise binary causal relationships，无法直接表达高阶多变量交互。（Conclusion, PDF p.7）",
    "[分析推断] 预测 loss 梯度只是模型局部敏感度 proxy，并非干预验证的真实 causal graph。"
  ],
  "core_idea": "GCAD 用一个预测型 Mixer 作为梯度生成器，对每个目标通道的预测误差分别回传到各输入通道历史窗口，以预测损失梯度幅值近似动态非线性 Granger 影响，再消除对称相似性并与训练正常窗口的平均因果图比较，得到关系偏离与自时序偏离分数。",
  "technical_innovations": [
    {
      "name": "以每个目标通道 $j$ 的平方预测误差 $L_{t",
      "author_claim": "**[作者主张]** 以每个目标通道 $j$ 的平方预测误差 $L_{t,j}$ 构造独立 backward pass。（Eq. 1）",
      "challenge_ids": [
        "C1",
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
      "source_locator": "**[作者主张]** 以每个目标通道 $j$ 的平方预测误差 $L_{t,j}$ 构造独立 backward pass。（Eq. 1）"
    },
    {
      "name": "通过 $|\\partial L_{t",
      "author_claim": "**[作者主张]** 通过 $|\\partial L_{t,j}/\\partial x_{\\phi,i}|$ 对滞后和输入值分布积分，形成 $a_{i,j}$。（Eqs. 2–5）",
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
      "source_locator": "**[作者主张]** 通过 $|\\partial L_{t,j}/\\partial x_{\\phi,i}|$ 对滞后和输入值分布积分，形成 $a_{i,j}$。（Eqs. 2–5）"
    },
    {
      "name": "用 $\\tilde A_{ij}=\\max",
      "author_claim": "**[作者主张]** 用 $\\tilde A_{ij}=\\max(0,A_{ij}-A_{ji})$ 去除对称关系，再以阈值 $h$ 稀疏化；不保证 DAG。（Eq. 6）",
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
      "source_locator": "**[作者主张]** 用 $\\tilde A_{ij}=\\max(0,A_{ij}-A_{ji})$ 去除对称关系，再以阈值 $h$ 稀疏化；不保证 DAG。（Eq. 6）"
    },
    {
      "name": "对正常训练窗口抽样并求平均图 $A_{norm}$",
      "author_claim": "**[作者主张]** 对正常训练窗口抽样并求平均图 $A_{norm}$；测试时计算因果关系相对偏差 $S_c$、时间对角偏差 $S_t$，最终 $S=S_c+\\beta S_t$。（Eqs. 7–12）",
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
      "source_locator": "**[作者主张]** 对正常训练窗口抽样并求平均图 $A_{norm}$；测试时计算因果关系相对偏差 $S_c$、时间对角偏差 $S_t$，最终 $S=S_c+\\beta S_t$。（Eqs. 7–12）"
    }
  ],
  "methodology": {
    "architecture": "text 普通窗口 X{t-1} → Mixer prediction network → 预测 ŷt ↓ 对每个目标 j 单独构造平方误差 L{t,j} 对所有输入通道 i、滞后 φ 回传 ∂L{t,j}/∂x{φ,i} ↓ 积分 / 汇总梯度幅值为 A{i,j} eAij = max(0, Aij − Aji)，再阈值 sparsify ↓ 训练正常窗口随机抽样求均值 Anorm；测试窗口各得 eAtest ↓ 因果图相对偏差 Sc + β × 对角自时序偏差 St → anomaly score 可分成四部分：预测器、基于梯度的 Granger graph、因果图稀疏化、正常因果模板偏差打分。Mixer 是工具性梯度生成器；论文新意主要是把预测 loss 对输入各通道的敏感度映射成窗口级有向关系，再检测 graph pattern shift。（PDF p.3, Fig. 1, §3）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 Prediction-based Gradient Generator",
      "5.2 用 loss 梯度量化非线性 Granger 影响",
      "5.3 Causality Graph Sparsification",
      "5.4 Normal causal template and anomaly score"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (9)",
      "Eq. (11)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "GCAD 用一个预测型 Mixer 作为梯度生成器，对每个目标通道的预测误差分别回传到各输入通道历史窗口，以预测损失梯度幅值近似动态非线性 Granger 影响，再消除对称相似性并与训练正常窗口的平均因果图比较，得到关系偏离与自时序偏离分数。"
  },
  "experimental_evidence": {
    "datasets": [
      "- Datasets：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1） - Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，…",
      "| Dataset | GCAD AUROC | GCAD AUPRC | 表内比较边界 | | --- | ---: | ---: | --- | | SWaT | .8690 | .7758 | 两项均高于所列对照 | | SMD | .9533 | .7502 | 两项均高于所列对照 | | MSL | .7658 | .3679 | 两项均高于表内结果，异常率很低 | | SMAP | .7273 | .4555 | ROC 高；PR 略低于 GANF .5259 | | PSM | .7618 | .6136 | 表内高于列出的 baseline |",
      "作者总结大多数指标 / 数据集达最佳；但 SMAP AUPRC 是 GANF .5259 高于 GCAD .4555。MSL / SMAP 异常率分别仅 .74% / 2.14%，PR 值低，需谨慎解释排序成绩。（PDF pp.5–6, Tables 1–2）"
    ],
    "baselines": [
      "### 6.1 Data, metrics, baseline protocol",
      "- Datasets：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1） - Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，…",
      "| Dataset | GCAD AUROC | GCAD AUPRC | 表内比较边界 | | --- | ---: | ---: | --- | | SWaT | .8690 | .7758 | 两项均高于所列对照 | | SMD | .9533 | .7502 | 两项均高于所列对照 | | MSL | .7658 | .3679 | 两项均高于表内结果，异常率很低 | | SMAP | .7273 | .4555 | ROC 高；PR 略低于 GANF .5259 | | PSM | .7618 | .6136 | 表内高于列出的 baseline |"
    ],
    "metrics": [
      "### 6.1 Data, metrics, baseline protocol",
      "- Datasets：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1） - Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，…",
      "作者总结大多数指标 / 数据集达最佳；但 SMAP AUPRC 是 GANF .5259 高于 GCAD .4555。MSL / SMAP 异常率分别仅 .74% / 2.14%，PR 值低，需谨慎解释排序成绩。（PDF pp.5–6, Tables 1–2）"
    ],
    "main_results": [
      "- Datasets：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1） - Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，不应直接把这些行当作原始全量规模。…",
      "### 6.2 Main results",
      "Table 2 的 AUROC / AUPRC（模型：ROC / PR）：",
      "作者总结大多数指标 / 数据集达最佳；但 SMAP AUPRC 是 GANF .5259 高于 GCAD .4555。MSL / SMAP 异常率分别仅 .74% / 2.14%，PR 值低，需谨慎解释排序成绩。（PDF pp.5–6, Tables 1–2）",
      "- 去掉 sparsification：SWaT ROC / PR .8690/.7758→.8559/.7676；SMD .9533/.7502→.9531/.6915，说明稀疏化对 PR / noise reduction 有帮助，但 SMD AUROC 变化很小。（PDF p.6, Table 3） - 去掉因果关系 GC：SWaT .8478/.7513，SMD .9405/.6424，特别是 SMD AUPRC 大降；支持关系结构比预测误差单项有增益。（Table 3） - 去掉时间对角 TC：SWaT .8400/.7558，SMD .9498/.6748；作者据此指出非对角因果依赖与自历史偏差互补。…"
    ],
    "ablations": [
      "### 6.3 Ablations and graph example",
      "- 去掉 sparsification：SWaT ROC / PR .8690/.7758→.8559/.7676；SMD .9533/.7502→.9531/.6915，说明稀疏化对 PR / noise reduction 有帮助，但 SMD AUROC 变化很小。（PDF p.6, Table 3） - 去掉因果关系 GC：SWaT .8478/.7513，SMD .9405/.6424，特别是 SMD AUPRC 大降；支持关系结构比预测误差单项有增益。（Table 3） - 去掉时间对角 TC：SWaT .8400/.7558，SMD .9498/.6748；作者据此指出非对角因果依赖与自历史偏差互补。…"
    ],
    "robustness_generalization": [
      "- 去掉 sparsification：SWaT ROC / PR .8690/.7758→.8559/.7676；SMD .9533/.7502→.9531/.6915，说明稀疏化对 PR / noise reduction 有帮助，但 SMD AUROC 变化很小。（PDF p.6, Table 3） - 去掉因果关系 GC：SWaT .8478/.7513，SMD .9405/.6424，特别是 SMD AUPRC 大降；支持关系结构比预测误差单项有增益。（Table 3） - 去掉时间对角 TC：SWaT .8400/.7558，SMD .9498/.6748；作者据此指出非对角因果依赖与自历史偏差互补。…"
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
      "如果正常业务负载改变了预测依赖（例如开关服务 / 控制回路）但仍符合合法操作，单一 $A{norm}$ 无法自动区分“新正常机制”与故障关系破坏。",
      "分数表示因果预测结构偏离，可作为定位线索；从预测依赖直接称为实际根因还需要物理图 / 操作记录验证。",
      "当前定义逐变量两两评分；多故障共同改变预测关系时可能表现为若干 pair 边差异，无法表示高阶协同机制，作者对此限制有所承认。"
    ],
    "evidence_gaps": [
      "只建模变量对变量的 binary causal pairs，不能直接表示多变量组合因果关系；Conclusion 将此列为限制与 future work。（PDF p.7）",
      "论文解释 Granger causality 是预测可提升关系，不是完整物理因果。Sparsification 不保证 DAG。（PDF pp.4–5）",
      "$A{norm}$ 是训练 normal windows 的均值单模板，没有条件化负载、时段、控制阶段或服务版本。合法多模态状态切换导致因果图变化时也可能升高异常分数；论文未用已知业务态做对照。",
      "梯度对预测误差求导是模型局部敏感度；它受预测器是否学好、loss 残差和输入分布影响。论文没有通过真实 cause graph ground truth 测量边识别准确率，也没有比较 intervention / operator logs。",
      "threshold-independent AUROC / AUPRC 提供 score 排序证据，但没有固定 FPR 下报警数、事件时延、diagnosis precision 或成本；仅 SWaT 定性案例说明物理关系。",
      "Table 1 中部分 train/test 样本数显著小于标准公开数据常用规模；复现应确认其拆分 / 重采样流程及 Table 2 是否基于完全相同 pipeline。",
      "正文未报告代码仓库，且训练细节较简略；重现需确认 $P$ 近似、梯度积分数值实现、Bernoulli 样本数、threshold $h$ / $\\beta$ 搜索、滑窗标签回填以及起点 / 末端的 graph 计算。"
    ]
  },
  "research_implications": [
    "- [分析推断] 以状态条件图模板 / 图混合模型表示多种正常负载状态，检查均值模板是否构成不存在的中间关系图。 - [分析推断] 将梯度图和真实 topology、故障注入、operator event / Trace 对齐，区分 predictive sensitivity 与可验证因果关系。 - [分析推断] 构造正常负载变化与故障并发测试，量化图模板切换与在线更新的污染风险。 - [分析推断] 加入高阶交互图、固定 FPR 的运行点、事件级时延和跨实体迁移评测。"
  ],
  "related_papers": [
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
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.1–3, §§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.2–4, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.2–5, §§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.5–6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "§2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF p.7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF p.3, §3, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.3–4, §3, Eq. 1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "Eq. 2, Eq. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF pp.4–5, §3, Eqs. 2–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf",
      "locator": "PDF p.5, §3, Eq. 6",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "76de300623a174b32be75962649ba420cca1189fe066a1751f10c1c87f51ce19",
    "reading_note_sha256": "d87a4553d27366e86d8064d828a1b5fab9fe22de9a272ad9a7564a52edc58920",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "341d567196d1de6b6b68dcdac2612d80fa4c13e0f3866d021ab2357986ac1bc4"
  },
  "knowledge_card_path": "papers/gcad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
