# Knowledge Dossier — Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection

## 1. Basic Information

- **English title**: Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection
- **中文译名**：因果感知对比学习：鲁棒多变量时间序列异常检测
- **Authors**: HyunGi Kim, Jisoo Mok, Dongjun Lee, Jaihyun Lew, Sungjae Kim, Sungroh Yoon
- **Venue / year / CCF**: ICML 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/kimanki/CAROTS
- **Research area**: 多变量异常检测与 Granger 因果对比学习
- **Method tags**: TSAD MTSAD causal-discovery Granger-causality contrastive-learning normal-variation synthetic-anomaly one-class-learning robustness context

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 多变量时序异常检测；异常可能不是单变量幅值偏离，而是变量间正常预测性因果关系被破坏。（PDF pp.1–4, §1–3）
- **[实验支持]** SWaT、WADI、PSM、SMD、MSL 五类真实数据和 VAR / Lorenz96 两类显式因果合成系统。（PDF pp.6–8, 13–15）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

多变量时序异常检测（MTSAD）要识别多个相互作用变量中的异常。作者从**预测性 / Granger 因果关系**出发：若变量 $x_i$ 的过去能改善对 $x_j$ 的预测，则把 $x_i$ 视作 $x_j$ 的原因。邻接矩阵 $A\in\{0,1\}^{N\times N}$ 中 $A_{i,j}=1$ 表示 $x_i\to x_j$；因果发现器同时学习图 $A$ 与各变量的因果预测函数 $f_i$。（PDF p.3, §3.1）

因果视角下，训练正常期的跨变量关系在正常运行时保持相对稳定；异常可能使某些变量偏离由其过去和原因变量所预测的值。论文将异常概念化为至少一变量的因果预测残差超过 \(\delta\)：

\[
\exists x_t^i:\left|x_t^i-f_i(x^i_{<t},Pa(x^i)_{<t})\right|>\delta. \tag{2}
\]

这提供了“正常波动可能幅度大，但仍符合系统联动；故障可能幅度小，却破坏变量之间响应关系”的判别角度。作者用热浪导致空调运行更久作为保持因果关系的正常变化，与空调故障后不再随温度启动的因果关系破坏作对比。（PDF pp.1, 4, Introduction / §3.2）

核心假设是正常状态的因果矩阵 $A$ 及映射 $\{f_i\}$ 随时间基本不变。该假设适用于因果机制稳定的系统；发布、切换运行模式、外部控制介入等导致因果机制改变时，现成图可能过时。（PDF p.4, §3.2；Appendix §D）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 正常工况变化可以大幅改变变量值，但保留驱动—响应关系；仅凭值域/重构误差容易将其误报为异常。（热浪—空调示例，PDF pp.1–2）
- **[作者主张]** 对比学习的单一正常簇会压缩共享因果关系但语义不同的正常模式。（PDF p.5, §4.2）
- **[作者假设]** 正常期的因果图与预测机制基本时间不变。（PDF p.4, §3.2）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：4. Existing Methods and Their Limitations

- **仅学习重构误差 / 数值分布的检测器**：重构或预测模型可能因大幅但合理的操作变化产生高误差；单凭观测值偏离正常训练分布，不足以区分保持正常因果结构的变化与关系破坏。（作者论述，PDF pp.1–2）
- **通用对比式 MTSAD**：负样本通常依赖通用增强；若增强只产生表面数值扰动，没有利用跨变量因果结构，容易把正常相关变化和真实关系破坏混在一起。（作者论述，PDF pp.2–3）
- **普通单类对比损失**：将所有正常正样本挤进同一簇，会抹去共享正常因果关系、但语义模式不同的多个子簇，例如相同空调—温度关系下不同风量设置。CAROTS 认为这会压缩正常变化的表示空间。（作者论述，PDF p.5, §4.2）
- **因果发现不等于异常识别**：已有研究关注从时间序列恢复因果结构；CAROTS 的目标是把估计结构用作正常变化和故障扰动的训练依据。（PDF p.3, §2.2）

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

CAROTS 先从正常多变量序列学习 Granger 因果结构和预测器，再沿因果边生成保持因果关系的正常增强与破坏因果关系的伪异常，用带相似度筛选的单类对比损失学习表示，最后融合正常嵌入中心距离与因果预测残差进行检测。（PDF pp.1–6, Fig. 1, Eqs. (1)–(7)）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 正常工况变化可以大幅改变变量值，但保留驱动—响应关系；仅凭值域/重构误差容易将其误报为异常。（热浪—空调示例，PDF pp.1–2）
- **C2（第4节挑战）**：[作者主张] 对比学习的单一正常簇会压缩共享因果关系但语义不同的正常模式。（PDF p.5, §4.2）
- **C3（第4节挑战）**：[作者假设] 正常期的因果图与预测机制基本时间不变。（PDF p.4, §3.2）

### 7.1 CPA

- **作者技术描述**：**[作者主张] CPA**：加扰动到抽样原因变量历史，以因果预测器更新其后果变量值，产生新的正常变化。（PDF pp.4–5, Eq. (3), Fig. 2）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 CPA：沿正常因果关系生成多样正例”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 CDA

- **作者技术描述**：**[作者主张] CDA**：沿估计因果图 DFS 选不同子图，扰动变量值以破坏预测关系。（PDF pp.4–5, Fig. 2）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 CDA：沿子图扰动制造因果破坏负例”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 SOC

- **作者技术描述**：**[作者主张] SOC**：按与 anchor 的相似度阈值筛掉低相似正样本，并随训练逐渐扩大正例范围，保留语义多样的正常模式。（PDF pp.5–6, Eq. (6)）
- **对应挑战**：C2、C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 SOC：逐渐容纳语义不同的正常正例”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** 去掉 SOC 后 SWaT AUROC 0.852→0.819；去掉 $A_{CL}$ 后降至 0.814。去掉 $A_{CD}$ 反而升至 0.861，反映跨数据集融合风险。（PDF p.8, Table 4）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 双分数

- **作者技术描述**：**[作者主张] 双分数**：正例嵌入到正常质心的距离 $A_{CL}$ 与因果预测残差 $A_{CD}$ 各自用训练统计 z-normalize 后求和。（PDF p.6, Eq. (7)）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.5 两类因果感知分数融合”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Overall Architecture

```text
正常训练序列
   ├─ CUTS+ 因果发现器：预测历史 → 当前值，学习 A 与 Fθ,A
   └─ 滑动窗口原始批 G1
         ├─ CPA：扰动原因变量 + 用因果预测补算受影响变量 → G2（因果保持正例）
         ├─ CDA(G1)：沿因果图 DFS 取子图并加偏置 → G3（因果破坏负例）
         └─ CDA(G2) → G4（增强正常变体上的因果破坏负例）
                  ↓
      LSTM 编码器 + SOC 相似度过滤单类对比损失
                  ↓
    推理分数 = 正常正例中心距离 A_CL + 因果预测误差 A_CD（各自 z-normalize）
```

四组数据拼成 $4B$ 个增强 batch。原始数据 $G_1$ 和 CPA 生成的因果保持样本 $G_2$ 为正例集合 $G_P$；CDA 处理两者所得 $G_3,G_4$ 为负例 $G_N$。这样让模型既见到原始正常，也见到训练集未覆盖但沿已学因果机制变化的合成正常，以及多种关系破坏型合成异常。（PDF pp.3–6, Fig. 1, Eqs. (3)–(5)）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method: Modules and Equations

#### 6.1 因果发现器：拟合正常跨变量预测关系

对 $N$ 个变量的连续多变量序列 $x_t\in\mathbb R^N$ 以窗口长度 $w$ 切分，得到 $X_t\in\mathbb R^{w\times N}$。预测器 $F_{\theta,A}$ 用过去值及因果父节点预测当前变量。训练目标为预测均方误差加图稀疏惩罚：

\[
\hat\theta,\hat A=\arg\min_{\theta,A}\;\mathbb E_{X_t}\big[\operatorname{MSE}(F_{\theta,A}(X_{<t}),x_t)+\lambda\lVert A\rVert_1\big]. \tag{1}
\]

作者采用 CUTS+ 作为主因果发现器。因果矩阵按其方法从训练数据恢复，后续 CPA / CDA 将 $A$ 作为变换操作的图结构；$F_{\theta,A}$ 亦可输出相应时间点的因果预测值和 $A_{CD}$。（PDF pp.3–4, §3.1–4.1）

**语义边界：** 这里的因果边基于时间先后与预测增益的 Granger 意义，由观察数据训练模型得到；论文没有为所有边提供干预实验验证，因此不应把估计图等同于已经证实的物理因果图。（PDF pp.3–4, §3.1–3.2；此处为解释边界）

#### 6.2 CPA：沿正常因果关系生成多样正例

Causality-Preserving Augmentor（CPA）输入一个多变量窗口 $X_t$，随机选择 $M<N$ 个原因变量 $C$，取其直接影响到的变量集合 $E$（由 $A$ 得到）。对原因变量过去值加小幅高斯噪声 $z\sim\mathcal N(0,\sigma^2)$，构成扰动后的历史 $X'_{<t}$；再用 $F_{\theta,A}(X'_{<t})$ 预测受影响变量当前值，并用这些预测替换原窗口中 $E$ 对应值。输出样本仍按已学因果机制联动，但具有不同取值，作为**正常变化正例**。（PDF pp.4–5, §4.1, Eq. (3), Fig. 2(a-1)）

补充实现中主实验 $M=1$，噪声标准差 \(\sigma=0.2\)，加在原因变量历史的最后一个时间点上。SWaT 上对 \(\sigma\) 从 0 到 0.4 的测试显示结果变化较小。（PDF pp.15–17, Appendix B, Table 11）

#### 6.3 CDA：沿子图扰动制造因果破坏负例

Causality-Disturbing Augmentor（CDA）同样从随机原因变量 $C$ 出发，在因果图 $A$ 上做深度优先搜索（DFS），以截止概率 $p$ 结束扩展，抽取大小不同的有向子图；之后向子图所含变量注入与因果关系无关的随机偏置，破坏因果关系，作为**伪异常负例**。（PDF pp.4–5, §4.1, Fig. 2(a-2)）

附录给出的偏置候选值为 \(-0.5,-0.4,\dots,-0.1,0.1,\dots,0.5\)，在每个变量随机选取的 50% 时间点上施加；DFS 截止概率 $p=0.1$。作者将 CDA 应用于 $G_1$ 和 $G_2$，分别形成 $G_3$ 与 $G_4$，扩展负例对同一原始因果模式及其保持型变体均有效。（PDF pp.15–16, Appendix B）

#### 6.4 SOC：逐渐容纳语义不同的正常正例

对含 $4B$ 样本的 batch，令 $G_P=G_1\cup G_2$、$G_N=G_3\cup G_4$，分别有 $2B$ 个正例和负例。编码器 $E_\phi$ 得到嵌入；$S_{i,j}$ 是第 $i,j$ 个样本嵌入余弦相似度除以温度参数 \(\tau\)。对每个正例 anchor (i)，只保留高于阈值 \(\alpha/\tau\) 的正例：

\[
P_i=\{j\in\{1,\dots,2B\}\mid S_{i,j}\ge\alpha/\tau\},\qquad
N_i=\{j+2B\mid j\in P_i\}.
\]

SOC 损失为：

\[
\mathcal L=\frac{1}{2B}\sum_{i=1}^{2B}\frac{1}{|P_i|}\sum_{j\in P_i}
-\log\frac{\exp(S_{i,j})}{\exp(S_{i,j})+\sum_{k\in N_i}\exp(S_{i,k})}. \tag{6}
\]

低相似正例暂不参与当前 anchor 的损失；随着训练进行，表示逐步聚合，高相似度条件会放进更广的样本，因此模型先学习局部相似结构，再扩大到共享因果关系但语义模式不同的正例。主实验 \(\alpha\) 从 0.5 线性升到 0.9、温度 \(\tau=0.1\)；消融显示 \(\alpha\) 调度能改善 SWaT 的 AUPRC / F1。（PDF pp.5–6, §4.2, Eq. (6), Fig. 2(b), Appendix Table 9）

#### 6.5 两类因果感知分数融合

- **对比嵌入分数 $A_{CL}$**：求训练期正例（原始 $G_1$ 和因果保持 $G_2$）嵌入质心 \(\mu_P\)，测试样本嵌入到质心的距离越大，越不像因果保持正常样本。
- **因果预测分数 $A_{CD}$**：预测器根据过去和父变量关系预测当前值，预测 MSE 越大，越不符合训练期学得的关系。

分别用训练分数均值与标准差做 z-score 标准化，再相加：

\[
A(X_t)=A^{norm}_{CL}(X_t)+A^{norm}_{CD}(X_t),\quad
A_{CL}(X_t)=D(E_\phi(X_t),\mu_P),\quad
A_{CD}(X_t)=\operatorname{MSE}(F_{\theta,A}(X_{<t}),x_t). \tag{7}
\]

CAROTS$^{\dagger}$ 是消融名，表示只用 $A_{CL}$、不做两分数融合。距离默认用 L2，WADI 和 VAR 使用余弦距离。（PDF pp.6, 14–16, §4.3, Eq. (7), Appendix B）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (3)、Eq. (6)、Eq. (7)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

CAROTS 先从正常多变量序列学习 Granger 因果结构和预测器，再沿因果边生成保持因果关系的正常增强与破坏因果关系的伪异常，用带相似度筛选的单类对比损失学习表示，最后融合正常嵌入中心距离与因果预测残差进行检测。（PDF pp.1–6, Fig. 1, Eqs. (1)–(7)）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Setup

#### 7.1 数据集和异常类型

作者评估五类真实数据：SWaT、WADI、PSM、SMD、MSL（实验使用 SMD 2-1 / 3-7、MSL P-14 / P-15 子序列），以及两个有明确因果机制的合成数据：非线性 Lorenz96 和线性 VAR。Lorenz96 / VAR 测试集注入 Point Global（PG）、Point Contextual（PC）、Collective Trend（CT）、Collective Global（CG）四类异常，用于检查不同局部/上下文、点/片段变化。合成数据 $N=128$，长 40,000 点，按 16,000 / 4,000 / 20,000 分训练、验证、测试；仅测试集注入异常，比例 0.01，10 个变量随机受影响，难度因子 \(\lambda=2\)（CG 例外）。SWaT、WADI 为计算效率下采样 5 倍。（PDF pp.6, 13–15, 16）

Appendix Table 7 给出变量数、训练 / 测试点数、异常率与 ADF 检验。例如 SWaT 51 变量，WADI 123，PSM 25，SMD 38，MSL 子序列 55；SWaT / WADI / MSL 及 SMD 3-7 等部分子集的 ADF p 值较高。该分析支持所选数据有非平稳性，但它本身不验证因果机制确实稳定。（PDF p.13, Table 7）

#### 7.2 基线、训练和评价

重构类基线：Anomaly Transformer、TimesNet、USAD；对比学习类：SimCLR、SSD、CSI、CTAD、CARLA。CAROTS 主要采用一层 LSTM 编码器。训练 / 验证 / 测试用滑动窗；训练集均值和标准差用于标准化；训练数据中 20% 留作验证；默认窗口 10、batch 256、30 epochs，温度 \(\tau=0.1\)，\(\alpha\) 从 0.5 线性升到 0.9；三随机种子报告均值。（PDF pp.6, 13–16）

Appendix B 给出 Adam、梯度裁剪范数 1、5 epoch warm-up 后 cosine 学习率调度，按验证损失选模型；报告 AUROC、AUPRC 和 best F1，不报告 point-adjusted F1，因为其可能高估逐点检测能力。best F1 的阈值取得方式在正文未完全说明，是比较阈值敏感指标时的复现注意事项。（PDF pp.6, 16）

#### 精读笔记原章节：8. Results and Ablations

#### 8.1 真实数据

Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 **0.502 / 0.056 / 0.143**，而只用 $A_{CL}$ 的 CAROTS$^{\dagger}$ 为 **0.622 / 0.260 / 0.391**；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。（PDF pp.7–8, Table 1, Table 4, Appendix Table 10）

论文称 CAROTS$^{\dagger}$ 在 WADI、MSL P-15 等困难数据上已强于其他方法，但 Table 1 / Appendix Table 10 的 WADI 数值显示其相对完整模型提升很大，完整 CAROTS 也低于 CTAD 的 WADI AUROC 0.599、AUPRC 0.327、F1 0.374。后续比较应按具体数据和分数版本解读，而不能照搬“几乎所有指标和数据集最佳”的概括。（PDF pp.2, 7–8, 17, Tables 1, 10）

#### 8.2 合成因果数据

在显式因果系统中，Lorenz96 上 CAROTS 对 PG / PC / CT / CG 的 AUROC 分别为 **0.998 / 0.975 / 0.874 / 0.788**，平均 0.909；VAR 上为 **0.612 / 0.648 / 0.963 / 0.997**，平均 0.805。强点包括 Lorenz96 点异常、VAR collective anomalies；VAR 的 PG / PC 仍较难。Fig. 3 调低 \(\lambda\) 加大注入难度时，作者称多数方法下降，而 CAROTS 对一些困难等级仍有效。结论支持在**按所设生成机制构造**的合成场景里使用因果结构有益，但不同异常类型间的效果差异很大。（PDF pp.6, 8, Table 2, Fig. 3）

#### 8.3 组件消融

SWaT Table 4 的 AUROC / AUPRC / F1：完整模型 **0.852 / 0.764 / 0.792**；去 CPA 为 0.850 / 0.721 / 0.775；去 CDA 为 0.842 / 0.740 / 0.786；去相似度筛选为 0.819 / 0.733 / 0.769；去 $A_{CL}$ 为 0.814 / 0.722 / 0.769；去 $A_{CD}$（CAROTS$^{\dagger}$）为 0.861 / 0.760 / 0.789。支持 CPA、CDA 与 SOC 有贡献，尤其 SOC 去除后 AUROC 降低；但在 SWaT，去 $A_{CD}$ 的 AUROC 反而更高、F1 接近完整模型，说明“融合必然更优”并未得到本表支持。（PDF p.8, Table 4）

Appendix Table 10 将消融扩展到 7 个现实子集和 2 个合成数据；例如 WADI 去 $A_{CD}$ AUROC 0.622，完整为 0.502；MSL P-15 的 AUROC 则从去掉 $A_{CD}$ 时的 0.683 提升到完整模型的 0.701，说明该分数的作用依数据集而异。这进一步说明组件贡献存在场景差异。（PDF p.17, Table 10）

#### 8.4 鲁棒性、可视化与成本

- Table 3 测试温度 \(\tau\) 与 batch 大小：SWaT 表现稳定；PSM 在高温度下 AUROC/AUPRC/F1 会下降（如 \(\tau=0.2\) 为 0.76 / 0.56 / 0.57，\(\tau=1.6\) 为 0.61 / 0.44 / 0.46），故“对超参数鲁棒”的证据并非每个数据集同等强。（PDF p.8, Table 3）
- Table 5 将因果发现器替换成 NGC、CUTS、CUTS+：各自在哪套数据最好不一，但结果相近，说明框架可兼容多种图估计器；不能据此证明学得的因果图与真实因果图相同。（PDF p.8, Table 5）
- Table 6 比较 LSTM、GRU、iTransformer 编码器，在 SWaT 与 PSM 差距较小、GRU 部分指标最好，显示并非绑定单一编码器。（PDF p.8, Table 6）
- Table 9 的 \(\alpha\) 固定值和线性调度对 SWaT 有影响；Table 11 中 CPA 的 \(\sigma\) 取 0–0.4 结果变化不大。（PDF pp.16–17）
- t-SNE Fig. 4 显示正例与负例逐渐分离且正例可形成多个语义簇，属于定性可视化，不是因果结构或簇分离的形式检验。（PDF p.9, Fig. 4）
- Table 13 报训练时间 CAROTS 25 分钟、Anomaly Transformer 12、TimesNet 56、USAD/SimCLR/SSD 6；但比较**排除了因果发现器预训练时间**，不代表端到端总成本。（PDF p.18, Table 13）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

精读笔记未单独归类；分析推断需依据第 8–9 节的方法假设和实验范围，不能表述为已证实缺陷。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：10. Limitations and Reproduction Value — 作者明确讨论（归属未明确）

假设正常因果结构基本时间不变；真实系统可能因条件演化或外部干预而发生渐进或突发因果变化。（Appendix §D, PDF p.17）

#### 精读笔记原章节：10. Limitations and Reproduction Value — 作者明确讨论（归属未明确）

只聚焦直接因果关系，未显式处理隐藏混杂变量；外生变量会影响观察到的结构，作者建议引入领域知识和辅助数据。（Appendix §D, PDF p.17）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：12. My Understanding

CAROTS 把“正常”定义得比正常值域更结构化：一组变量可以一起大幅变化，只要这些变化仍符合训练期学得的驱动—响应关系，就可以在 CPA 中作为正常正例。CDA 则针对性破坏图上关系。这比单纯加入数值噪声更贴近某些工业系统的变量联动。但其“因果”首先是预测数据估计出来的 Granger 依赖；真实系统的外生变量、工作模式、控制策略和因果机制变化，都会改变图或预测关系。CAROTS 给出了一个解释型信号来源和可审查的假设，不等于已经识别业务波动原因或证明因果发现正确。

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 将 workload、发布、Trace、控制策略作为外生上下文，建模多种运行状态下的机制变化，测试负载变化与故障同时发生的样例。
- **[分析推断]** 用干预、故障注入或领域专家图评估因果图与增强保真度，而不只比较嵌入/检测分数。
- **[证据缺口]** 研究动态因果图与可信的在线切换机制，同时衡量变化适应速度、误报、异常吸收和部署成本。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- 与 CAPMix：两者都把训练期异常增强用于改进正常变化覆盖。CAPMix 按 DTW 距离软化形态伪异常标签；CAROTS 用估计的跨变量预测图生成因果保持正常与因果破坏伪异常。后者能表达变量联动，但依赖因果模型假设和训练图质量。（[CAPMix 笔记](capmix.md)）
- 与 When Model Meets New Normals：后者在测试时以 EMA + 预测正常样本更新模型，处理训练 / 测试 $P$ 漂移；CAROTS 主要在训练阶段建固定因果机制与表示，假设测试期关系保持稳定。两者互补，但 CAROTS 没有在线适应结构变化。（[When Model Meets New Normals 笔记](when-model-meets-new-normals.md)）
- 与后续 CrossAD：待完整阅读其跨尺度关联及跨窗口建模机制后比较；目前不把相关性直接称作因果关系。
- 与该清单中的 GCAD、Structured Temporal Causality、Cluster-Aware Causal Mixer：均涉及因果信息的 MTSAD 方向；后续逐篇读完后再比较图学习方式、时间变化假设及证据覆盖。

- CUTS+：CAROTS 主实验的预测式因果图 / 变量预测器。（PDF pp.3–4）
- CTAD、CARLA、SimCLR 等：对比学习 MTSAD 基线；CAROTS 的差异在于按因果结构设计正负增强。（PDF pp.2–3, 6–8）
- GCAD、GCFormer、Structured Temporal Causality：因果信息用于时间序列异常检测的相关路线，需与本集合后续笔记比较。（PDF pp.3, 11）
- CAPMix、When Model Meets New Normals：知识库中已完成的训练期增强与测试时新正常适应笔记，交叉链接见上节。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.3, §3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.1, §3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.4, §3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.1–4, §1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.6–8 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.1–2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.5, §4.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.4, §3.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.2–3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.3, §2.2 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.3–6, Eqs. (3), Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.3–4, §3.1–4.1 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.3–4, §3.1–3.2 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–5, §4.1, Eq. (3), Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.15–17, Table 11 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.4–5, §4.1, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.15–16 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.5–6, §4.2, Eq. (6), Fig. 2, Table 9 | 精读笔记保留的原文定位 |
| Method / formulas | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.6, §4.3, Eq. (7) | 精读笔记保留的原文定位 |
| Experimental evidence | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.6 | 精读笔记保留的原文定位 |
| Experimental evidence | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF p.13, Table 7 | 精读笔记保留的原文定位 |
| Experimental evidence | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.7–8, Table 1, Table 10, Table 1, Table 4 | 精读笔记保留的原文定位 |
| Experimental evidence | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.2, Table 1, Table 10 | 精读笔记保留的原文定位 |
| Experimental evidence | Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf | PDF pp.6, Fig. 3, Table 2, Fig. 3 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "carots",
  "title_en": "Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection",
  "title_zh": "因果感知对比学习：鲁棒多变量时间序列异常检测",
  "authors": [
    "HyunGi Kim",
    "Jisoo Mok",
    "Dongjun Lee",
    "Jaihyun Lew",
    "Sungjae Kim",
    "Sungroh Yoon"
  ],
  "year": 2025,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/ICML/Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/carots/notes.md",
  "code_url": "https://github.com/kimanki/CAROTS",
  "research_area": "多变量异常检测与 Granger 因果对比学习",
  "method_tags": [
    "TSAD MTSAD causal-discovery Granger-causality contrastive-learning normal-variation synthetic-anomaly one-class-learning robustness context"
  ],
  "research_scenario": "- [作者主张] 多变量时序异常检测；异常可能不是单变量幅值偏离，而是变量间正常预测性因果关系被破坏。（PDF pp.1–4, §1–3） - [实验支持] SWaT、WADI、PSM、SMD、MSL 五类真实数据和 VAR / Lorenz96 两类显式因果合成系统。（PDF pp.6–8, 13–15）",
  "research_problem": "多变量时序异常检测（MTSAD）要识别多个相互作用变量中的异常。作者从预测性 / Granger 因果关系出发：若变量 $xi$ 的过去能改善对 $xj$ 的预测，则把 $xi$ 视作 $xj$ 的原因。邻接矩阵 $A\\in\\{0,1\\}^{N\\times N}$ 中 $A{i,j}=1$ 表示 $xi\\to xj$；因果发现器同时学习图 $A$ 与各变量的因果预测函数 $fi$。（PDF p.3, §3.1） 因果视角下，训练正常期的跨变量关系在正常运行时保持相对稳定；异常可能使某些变量偏离由其过去和原因变量所预测的值。论文将异常概念化为至少一变量的因果预测残差超过 \\(\\delta\\)： \\[ \\exists xt^i:\\left|xt^i-fi(x^i{<t},Pa(x^i){<t})\\right|>\\delta. \\tag{2} \\] 这提供了“正常波动可能幅度大，但仍符合系统联动；故障可能幅度小，却破坏变量之间响应关系”的判别角度。作者用热浪导致空调运行更久作为保持因果关系的正常变化，与空调故障后不再随温度启动的因果关系破坏作对比。（PDF pp.1, 4, Introduction / §3.2） 核心假设是正常状态的因果矩阵 $A$ 及映射 $\\{fi\\}$ 随时间基本不变。该假设适用于因果机制稳定的系统；发布、切换运行模式、外部控制介入等导致因果机制改变时，现成图可能过时。（PDF p.4, §3.2；Appendix §D）",
  "core_challenges": [
    "[作者主张] 正常工况变化可以大幅改变变量值，但保留驱动—响应关系；仅凭值域/重构误差容易将其误报为异常。（热浪—空调示例，PDF pp.1–2）",
    "[作者主张] 对比学习的单一正常簇会压缩共享因果关系但语义不同的正常模式。（PDF p.5, §4.2）",
    "[作者假设] 正常期的因果图与预测机制基本时间不变。（PDF p.4, §3.2）"
  ],
  "existing_method_limits": [
    "仅学习重构误差 / 数值分布的检测器：重构或预测模型可能因大幅但合理的操作变化产生高误差；单凭观测值偏离正常训练分布，不足以区分保持正常因果结构的变化与关系破坏。（作者论述，PDF pp.1–2）",
    "通用对比式 MTSAD：负样本通常依赖通用增强；若增强只产生表面数值扰动，没有利用跨变量因果结构，容易把正常相关变化和真实关系破坏混在一起。（作者论述，PDF pp.2–3）",
    "普通单类对比损失：将所有正常正样本挤进同一簇，会抹去共享正常因果关系、但语义模式不同的多个子簇，例如相同空调—温度关系下不同风量设置。CAROTS 认为这会压缩正常变化的表示空间。（作者论述，PDF p.5, §4.2）",
    "因果发现不等于异常识别：已有研究关注从时间序列恢复因果结构；CAROTS 的目标是把估计结构用作正常变化和故障扰动的训练依据。（PDF p.3, §2.2）"
  ],
  "core_idea": "CAROTS 先从正常多变量序列学习 Granger 因果结构和预测器，再沿因果边生成保持因果关系的正常增强与破坏因果关系的伪异常，用带相似度筛选的单类对比损失学习表示，最后融合正常嵌入中心距离与因果预测残差进行检测。（PDF pp.1–6, Fig. 1, Eqs. (1)–(7)）",
  "technical_innovations": [
    {
      "name": "CPA",
      "author_claim": "**[作者主张] CPA**：加扰动到抽样原因变量历史，以因果预测器更新其后果变量值，产生新的正常变化。（PDF pp.4–5, Eq. (3), Fig. 2）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 CPA：沿正常因果关系生成多样正例",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] CPA**：加扰动到抽样原因变量历史，以因果预测器更新其后果变量值，产生新的正常变化。（PDF pp.4–5, Eq. (3), Fig. 2）"
    },
    {
      "name": "CDA",
      "author_claim": "**[作者主张] CDA**：沿估计因果图 DFS 选不同子图，扰动变量值以破坏预测关系。（PDF pp.4–5, Fig. 2）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 CDA：沿子图扰动制造因果破坏负例",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] CDA**：沿估计因果图 DFS 选不同子图，扰动变量值以破坏预测关系。（PDF pp.4–5, Fig. 2）"
    },
    {
      "name": "SOC",
      "author_claim": "**[作者主张] SOC**：按与 anchor 的相似度阈值筛掉低相似正样本，并随训练逐渐扩大正例范围，保留语义多样的正常模式。（PDF pp.5–6, Eq. (6)）",
      "challenge_ids": [
        "C2",
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 SOC：逐渐容纳语义不同的正常正例",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** 去掉 SOC 后 SWaT AUROC 0.852→0.819；去掉 $A_{CL}$ 后降至 0.814。去掉 $A_{CD}$ 反而升至 0.861，反映跨数据集融合风险。（PDF p.8, Table 4）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] SOC**：按与 anchor 的相似度阈值筛掉低相似正样本，并随训练逐渐扩大正例范围，保留语义多样的正常模式。（PDF pp.5–6, Eq. (6)）"
    },
    {
      "name": "双分数",
      "author_claim": "**[作者主张] 双分数**：正例嵌入到正常质心的距离 $A_{CL}$ 与因果预测残差 $A_{CD}$ 各自用训练统计 z-normalize 后求和。（PDF p.6, Eq. (7)）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.5 两类因果感知分数融合",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 双分数**：正例嵌入到正常质心的距离 $A_{CL}$ 与因果预测残差 $A_{CD}$ 各自用训练统计 z-normalize 后求和。（PDF p.6, Eq. (7)）"
    }
  ],
  "methodology": {
    "architecture": "text 正常训练序列 ├─ CUTS+ 因果发现器：预测历史 → 当前值，学习 A 与 Fθ,A └─ 滑动窗口原始批 G1 ├─ CPA：扰动原因变量 + 用因果预测补算受影响变量 → G2（因果保持正例） ├─ CDA(G1)：沿因果图 DFS 取子图并加偏置 → G3（因果破坏负例） └─ CDA(G2) → G4（增强正常变体上的因果破坏负例） ↓ LSTM 编码器 + SOC 相似度过滤单类对比损失 ↓ 推理分数 = 正常正例中心距离 ACL + 因果预测误差 ACD（各自 z-normalize） 四组数据拼成 $4B$ 个增强 batch。原始数据 $G1$ 和 CPA 生成的因果保持样本 $G2$ 为正例集合 $GP$；CDA 处理两者所得 $G3,G4$ 为负例 $GN$。这样让模型既见到原始正常，也见到训练集未覆盖但沿已学因果机制变化的合成正常，以及多种关系破坏型合成异常。（PDF pp.3–6, Fig. 1, Eqs. (3)–(5)）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 因果发现器：拟合正常跨变量预测关系",
      "6.2 CPA：沿正常因果关系生成多样正例",
      "6.3 CDA：沿子图扰动制造因果破坏负例",
      "6.4 SOC：逐渐容纳语义不同的正常正例",
      "6.5 两类因果感知分数融合"
    ],
    "key_formulas": [
      "Eq. (3)",
      "Eq. (6)",
      "Eq. (7)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "CAROTS 先从正常多变量序列学习 Granger 因果结构和预测器，再沿因果边生成保持因果关系的正常增强与破坏因果关系的伪异常，用带相似度筛选的单类对比损失学习表示，最后融合正常嵌入中心距离与因果预测残差进行检测。（PDF pp.1–6, Fig. 1, Eqs. (1)–(7)）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 数据集和异常类型",
      "Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 0.502 / 0.056 / 0.143，而只用 $A{CL}$ 的 CAROTS$^{\\dagger}$ 为 0.622 / 0.260 / 0.391；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。…",
      "论文称 CAROTS$^{\\dagger}$ 在 WADI、MSL P-15 等困难数据上已强于其他方法，但 Table 1 / Appendix Table 10 的 WADI 数值显示其相对完整模型提升很大，完整 CAROTS 也低于 CTAD 的 WADI AUROC 0.599、AUPRC 0.327、F1 0.374。后续比较应按具体数据和分数版本解读，而不能照搬“几乎所有指标和数据集最佳”的概括。（PDF pp.2, 7–8, 17, Tables 1, 10）",
      "Appendix Table 10 将消融扩展到 7 个现实子集和 2 个合成数据；例如 WADI 去 $A{CD}$ AUROC 0.622，完整为 0.502；MSL P-15 的 AUROC 则从去掉 $A{CD}$ 时的 0.683 提升到完整模型的 0.701，说明该分数的作用依数据集而异。这进一步说明组件贡献存在场景差异。（PDF p.17, Table 10）"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "作者评估五类真实数据：SWaT、WADI、PSM、SMD、MSL（实验使用 SMD 2-1 / 3-7、MSL P-14 / P-15 子序列），以及两个有明确因果机制的合成数据：非线性 Lorenz96 和线性 VAR。Lorenz96 / VAR 测试集注入 Point Global（PG）、Point Contextual（PC）、Collective Trend（CT）、Collective Global（CG）四类异常，用于检查不同局部/上下文、点/片段变化。合成数据 $N=128$，长 40,000 点，按 16,000 / 4,000 / 20,000 分训练、验证、测试；仅测试集注入异常，比例 0.01，…",
      "Appendix B 给出 Adam、梯度裁剪范数 1、5 epoch warm-up 后 cosine 学习率调度，按验证损失选模型；报告 AUROC、AUPRC 和 best F1，不报告 point-adjusted F1，因为其可能高估逐点检测能力。best F1 的阈值取得方式在正文未完全说明，是比较阈值敏感指标时的复现注意事项。（PDF pp.6, 16）",
      "Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 0.502 / 0.056 / 0.143，而只用 $A{CL}$ 的 CAROTS$^{\\dagger}$ 为 0.622 / 0.260 / 0.391；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。…",
      "论文称 CAROTS$^{\\dagger}$ 在 WADI、MSL P-15 等困难数据上已强于其他方法，但 Table 1 / Appendix Table 10 的 WADI 数值显示其相对完整模型提升很大，完整 CAROTS 也低于 CTAD 的 WADI AUROC 0.599、AUPRC 0.327、F1 0.374。后续比较应按具体数据和分数版本解读，而不能照搬“几乎所有指标和数据集最佳”的概括。（PDF pp.2, 7–8, 17, Tables 1, 10）"
    ],
    "main_results": [
      "Appendix Table 7 给出变量数、训练 / 测试点数、异常率与 ADF 检验。例如 SWaT 51 变量，WADI 123，PSM 25，SMD 38，MSL 子序列 55；SWaT / WADI / MSL 及 SMD 3-7 等部分子集的 ADF p 值较高。该分析支持所选数据有非平稳性，但它本身不验证因果机制确实稳定。（PDF p.13, Table 7）",
      "Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 0.502 / 0.056 / 0.143，而只用 $A{CL}$ 的 CAROTS$^{\\dagger}$ 为 0.622 / 0.260 / 0.391；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。（PDF pp.7–8, Table 1, Table 4, Appendix Table 10）",
      "论文称 CAROTS$^{\\dagger}$ 在 WADI、MSL P-15 等困难数据上已强于其他方法，但 Table 1 / Appendix Table 10 的 WADI 数值显示其相对完整模型提升很大，完整 CAROTS 也低于 CTAD 的 WADI AUROC 0.599、AUPRC 0.327、F1 0.374。后续比较应按具体数据和分数版本解读，而不能照搬“几乎所有指标和数据集最佳”的概括。（PDF pp.2, 7–8, 17, Tables 1, 10）",
      "在显式因果系统中，Lorenz96 上 CAROTS 对 PG / PC / CT / CG 的 AUROC 分别为 0.998 / 0.975 / 0.874 / 0.788，平均 0.909；VAR 上为 0.612 / 0.648 / 0.963 / 0.997，平均 0.805。强点包括 Lorenz96 点异常、VAR collective anomalies；VAR 的 PG / PC 仍较难。Fig. 3 调低 \\(\\lambda\\) 加大注入难度时，作者称多数方法下降，而 CAROTS 对一些困难等级仍有效。结论支持在按所设生成机制构造的合成场景里使用因果结构有益，但不同异常类型间的效果差异很大。（PDF pp.6, 8, Table 2, Fig. 3）",
      "SWaT Table 4 的 AUROC / AUPRC / F1：完整模型 0.852 / 0.764 / 0.792；去 CPA 为 0.850 / 0.721 / 0.775；去 CDA 为 0.842 / 0.740 / 0.786；去相似度筛选为 0.819 / 0.733 / 0.769；去 $A{CL}$ 为 0.814 / 0.722 / 0.769；去 $A{CD}$（CAROTS$^{\\dagger}$）为 0.861 / 0.760 / 0.789。支持 CPA、CDA 与 SOC 有贡献，尤其 SOC 去除后 AUROC 降低；但在 SWaT，去 $A{CD}$ 的 AUROC 反而更高、F1 接近完整模型，说明“融合必然更优”并未得到本表支持。（PDF p.8, Table 4）"
    ],
    "ablations": [
      "Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 0.502 / 0.056 / 0.143，而只用 $A{CL}$ 的 CAROTS$^{\\dagger}$ 为 0.622 / 0.260 / 0.391；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。…",
      "### 8.3 组件消融",
      "Appendix Table 10 将消融扩展到 7 个现实子集和 2 个合成数据；例如 WADI 去 $A{CD}$ AUROC 0.622，完整为 0.502；MSL P-15 的 AUROC 则从去掉 $A{CD}$ 时的 0.683 提升到完整模型的 0.701，说明该分数的作用依数据集而异。这进一步说明组件贡献存在场景差异。（PDF p.17, Table 10）"
    ],
    "robustness_generalization": [
      "作者评估五类真实数据：SWaT、WADI、PSM、SMD、MSL（实验使用 SMD 2-1 / 3-7、MSL P-14 / P-15 子序列），以及两个有明确因果机制的合成数据：非线性 Lorenz96 和线性 VAR。Lorenz96 / VAR 测试集注入 Point Global（PG）、Point Contextual（PC）、Collective Trend（CT）、Collective Global（CG）四类异常，用于检查不同局部/上下文、点/片段变化。合成数据 $N=128$，长 40,000 点，按 16,000 / 4,000 / 20,000 分训练、验证、测试；仅测试集注入异常，比例 0.01，…",
      "### 8.4 鲁棒性、可视化与成本",
      "- Table 3 测试温度 \\(\\tau\\) 与 batch 大小：SWaT 表现稳定；PSM 在高温度下 AUROC/AUPRC/F1 会下降（如 \\(\\tau=0.2\\) 为 0.76 / 0.56 / 0.57，\\(\\tau=1.6\\) 为 0.61 / 0.44 / 0.46），故“对超参数鲁棒”的证据并非每个数据集同等强。（PDF p.8, Table 3） - Table 5 将因果发现器替换成 NGC、CUTS、CUTS+：各自在哪套数据最好不一，但结果相近，说明框架可兼容多种图估计器；不能据此证明学得的因果图与真实因果图相同。…"
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
      "见档案 §10.B；保持为分析而非已证实结论"
    ],
    "evidence_gaps": [
      "假设正常因果结构基本时间不变；真实系统可能因条件演化或外部干预而发生渐进或突发因果变化。（Appendix §D, PDF p.17）",
      "只聚焦直接因果关系，未显式处理隐藏混杂变量；外生变量会影响观察到的结构，作者建议引入领域知识和辅助数据。（Appendix §D, PDF p.17）"
    ]
  },
  "research_implications": [
    "CAROTS 把“正常”定义得比正常值域更结构化：一组变量可以一起大幅变化，只要这些变化仍符合训练期学得的驱动—响应关系，就可以在 CPA 中作为正常正例。CDA 则针对性破坏图上关系。这比单纯加入数值噪声更贴近某些工业系统的变量联动。但其“因果”首先是预测数据估计出来的 Granger 依赖；真实系统的外生变量、工作模式、控制策略和因果机制变化，都会改变图或预测关系。CAROTS 给出了一个解释型信号来源和可审查的假设，不等于已经识别业务波动原因或证明因果发现正确。",
    "- [分析推断] 将 workload、发布、Trace、控制策略作为外生上下文，建模多种运行状态下的机制变化，测试负载变化与故障同时发生的样例。 - [分析推断] 用干预、故障注入或领域专家图评估因果图与增强保真度，而不只比较嵌入/检测分数。 - [证据缺口] 研究动态因果图与可信的在线切换机制，同时衡量变化适应速度、误报、异常吸收和部署成本。"
  ],
  "related_papers": [
    {
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
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
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.3, §3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.1, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.4, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–4, §1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.6–8",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.5, §4.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.4, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.3, §2.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–6, Eqs. (3), Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–4, §3.1–4.1",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "b9c8de2e1f517e0df614ae88bb8f3e1a6b1f065e2952cbfd0cd19c67b4e5b568",
    "reading_note_sha256": "4880bfac7c9fab8840eacc42510ee04e77e457870f4c52aa77e1d3efa39e0d60",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "5822dc3e2d5ea1d9b01023c4a9c85795c44f50726f60b8b579c5207d26e463a8"
  },
  "knowledge_card_path": "papers/carots/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
