# Knowledge Dossier — Cluster-Aware Causal Mixer for Online Anomaly Detection in Multivariate Time Series

## 1. Basic Information

- **English title**: Cluster-Aware Causal Mixer for Online Anomaly Detection in Multivariate Time Series
- **中文译名**：用于多变量时间序列在线异常检测的聚类感知因果混合器
- **Authors**: Md Mahmuddun Nabi Murad, Yasin Yilmaz
- **Venue / year / CCF**: ICML 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf](../../sources/papers/tsad-2024-2026/2026/ICML/Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/Secure-and-Intelligent-Systems-Lab/CCM-TAD
- **Research area**: 因果时间遮罩与聚类通道建模的在线 MTSAD
- **Method tags**: TSAD multivariate online-detection causal-temporal-mask channel-clustering MLP-Mixer empirical-p-value sequential-scoring event-boundary ICML-2026

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 多变量时序在线异常检测：用当前 / 历史窗口重建最新观测，并把重构误差转换为顺序告警证据。（PDF §§3.1, 3.4）
- **[实验支持]** SWaT、WADI、PSM、SMD、MSL、SMAP 六个基准；作者仅面向 multivariate，不适用于单变量。（Table 1; Appendix M）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文讨论多变量时间序列在线异常检测，目标是只利用当前及历史观测逐点重建最新观测并产生分数。作者归纳三个问题：（1）普通 MLP-Mixer 的 temporal mixing 可在窗口任意时点间混合，可能把未来数据泄露到较早时刻的表示；（2）所有通道由一个 embedding 联合表示时，相关结构差异可能造成伪相关；（3）逐点重构误差没有利用异常往往连续成段这一时间连续性。（PDF pp.1–3, §§1, 3）

论文中特别限定“causality”含义：它约束**时间维信息流**，不做 Granger 因果发现，也不估计跨通道因果图 / 根因通道。作者以多变量重构模型为基础，假设训练数据以正常样本为主；虽然文献习惯称 unsupervised TSAD，训练污染仍可能损伤模型。（PDF pp.2–3, §3 opening; Appendix M, p.25）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 普通 MLP mixer 时间维全窗口混合可造成未来信息泄漏；统一 embedding 会混合不同相关结构；逐点分数忽略异常持续性。（PDF §§1, 3）
- **[作者主张]** 在线异常评分既需避免未来 test observations，也需要聚合连续的异常证据与校正边界。（§3.4; Appendix L）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** MLP mixer 缺少时间因果掩码；多通道若相关性异质，联合投影可能引入伪相关；单点阈值分类忽略前后时间联系。（PDF §§1, 3）
- **[作者明确限定]** 本文所谓因果仅为时间信息流因果，不发现 Granger / 通道间因果或根因变量。（Appendix M）

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

CCM-TAD 先根据训练数据的跨通道相关性 profile 做 spectral clustering，并给每组通道单独 embedding；再以严格下三角时间掩码的 MLP mixer 重建当前点，最后将重构误差对训练内验证误差转成经验 p-value，累积逐时异常证据并回溯修正事件起止边界。

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 普通 MLP mixer 时间维全窗口混合可造成未来信息泄漏；统一 embedding 会混合不同相关结构；逐点分数忽略异常持续性。（PDF §§1, 3）
- **C2（第4节挑战）**：[作者主张] 在线异常评分既需避免未来 test observations，也需要聚合连续的异常证据与校正边界。（§3.4; Appendix L）

### 7.1 以相关 profile cosine graph 的 Laplacian 谱聚类通道

- **作者技术描述**：**[作者主张]** 以相关 profile cosine graph 的 Laplacian 谱聚类通道；零相关 profile 通道单独成簇。（§3.2.1, Eqs. 6–9）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 每簇独立 embedding

- **作者技术描述**：**[作者主张]** 每簇独立 embedding，并按通道数分配总维度。（§3.2.2, Eq. 10）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.2 Causal temporal mixer 与 embedding mixer”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 两层 temporal linear mixer 均用三角掩码

- **作者技术描述**：**[作者主张]** 两层 temporal linear mixer 均用三角掩码，并以 $1/j$ 调整累积输入数；feature mixer 仍为标准两层 MLP。（§3.3, Eqs. 11–13）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.2 Causal temporal mixer 与 embedding mixer”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 validation error empirical p-value → $\beta_t=\log

- **作者技术描述**：**[作者主张]** validation error empirical p-value → $\beta_t=\log(\alpha/(p_t+\epsilon))$ → 带连续负证据 reset 的累积 $s_t$ → onset/offset backtracking。（§3.4, Eqs. 14–17）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. Overall Architecture

```text
训练序列计算 Pearson correlation profiles
  → profile cosine-similarity graph + spectral clustering 得 M 组通道
  → 每组通道独立线性 embedding，拼成 d 维表示
  → causal temporal mixer（两层受掩码线性变换 + GELU）
  → embedding mixer（两层线性层 + GELU）及残差 / BatchNorm
  → 线性 head 只重建 look-back 窗口的最后一个时点
  → MSE 重构误差 g_t
  → 与 validation loss 序列比较成经验 p-value p_t 和证据 β_t
  → 累积证据 s_t 超阈值 h 时告警，之后回溯修正边界
```

架构由“正常表示拆分”“因果时间建模”“事件级分数整理”三部分构成。前两部分改变重构网络和数据表示；第三部分不重训网络，而对已经产生的重构误差用验证集正常误差校准、顺序累积和边界回溯。（PDF pp.3–5, Fig. 1, §§3.1–3.4）

所有数据以训练集统计量做 min–max scaling；作者假设训练以正常数据为主，并明确指出污染可能降低检测表现。（PDF p.3, §3 opening）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. Detailed Method

#### 5.1 Input and cluster-aware multi-embedding

给定 look-back 窗口 $X^L\in\mathbb R^{L\times C}$（$C$ 个通道），作者先用训练集 Pearson 相关矩阵 $\Phi\in[-1,1]^{C\times C}$，再取绝对值 $\Phi^{abs}$。通道 $i$ 的 correlation profile 是矩阵第 $i$ 行 $\phi_i\in[0,1]^C$，表示它与所有通道的相关性分布。常量通道产生的 NaN 相关系数置零；全零 profile 通道单独归为第 $M$ 组。（PDF pp.3–4, §3.2.1）

对其余通道，构造 profile 间 cosine similarity：

$$w_{ij}=\begin{cases}\frac{(\phi'_i)^\top\phi'_j}{\|\phi'_i\|\|\phi'_j\|}, & i\ne j,\\0,&i=j.\end{cases}\tag{6}$$

随后以 $L_n=I-D^{-1/2}WD^{-1/2}$ 构造 normalized graph Laplacian（Eq. 7），取最小非零特征值对应的前 $M'=M-1$ 个 eigenvectors $V$，以 $U=D^{-1/2}V$ 做归一化，再对 $U$ 各行 K-Means 得 cluster index（Eqs. 8–9）。这个流程基于完整相关 profile 的相似性，而不是单独按 $|\Phi_{ij}|$ 强弱把直接高相关通道放一起。（PDF p.4, §3.2.1, Eqs. 6–9）

得到 $M$ 个通道组后，每组各有 embedding layer，并按组通道数 $C_i$ 分配维度 $d_i$：前 $M-1$ 组用 $\lfloor C_i d/C\rfloor$，最后一组取余，确保 $\sum_i d_i=d$（Eq. 10）。拼接后维度为 $d$。作者推导在簇规模近似均匀时，参数量从单层 $O(Cd)$ 变为总计约 $O(Cd/M)$；但该复杂度收益取决于通道组的分布与实现。（PDF pp.4–5, §3.2.2, Eq. 10）

**作用解释：** 通道被分组的根据是其与其他通道“相关 profile 的形状”相似，而不是原始值相关性正负方向，也不是业务拓扑。各组独立编码的假设是减少异质相关模式在同一投影中的纠缠；其监督证据主要来自下游分数和 representation separability 消融。

#### 5.2 Causal temporal mixer 与 embedding mixer

嵌入表示经 BatchNorm 后进入若干 mixer blocks。时间 mixer 输入转置到 $d\times L$。对线性层权重 $\Theta^c\in\mathbb R^{L\times L}$ 乘上上三角掩码 $\Gamma$：

$$\gamma_{i,j}=\begin{cases}1/j,&i\le j,\\0,&i>j,\end{cases}\quad\Theta^u=\Gamma\odot\Theta^c.\tag{11–12}$$

第 $k$ 个 embedding feature 的时间映射为 $x^{(k)}_{c1}=x^{(k)}_c\Theta^u+b$（Eq. 13），之后接 GELU 与第二个同类因果线性层。按论文约定，输出时间位置 $j$ 只能依赖输入位置 $i\le j$，因此因果掩码禁止 future-to-past 依赖；$1/j$ 缩放用于稳定不同位置可累积历史长度不同造成的优化动态。正文从矩阵索引方向解释掩码，读公式时应按其文字定义理解三角方向。（PDF pp.5–6, §3.3.1, Eqs. 11–13; Appendix J.4）

时间 mixer 后有残差和 BatchNorm。embedding mixer 在每个时间位置沿特征维用两层标准线性层 $d\to d d_f\to d$，中间 GELU；再与时间 mixer 输出和初始嵌入做残差相加、BatchNorm（Eqs. 1–5）。重复多个 blocks 后，head 映射回 $C$ 通道，并只输出 look-back 窗口最后时刻的重构 $\hat x_t$。（PDF pp.3–5, §3.1, §3.3.2, Eqs. 1–5）

作者用梯度图验证 causality：对 $t=15,c=19$ 的重构损失回传，普通 mixer 对未来位置梯度非零，causal mixer 对 $\tau>15$ 的梯度为零（Fig. 3）。但附录说明，掩码是 mixer 内部信息流约束，不是跨变量结构因果，也非从观察数据识别 intervention 因果效应。（PDF pp.8–9, §4.2.5, Fig. 3; Appendix K, p.25）

#### 5.3 从重构误差到 sequential anomaly evidence

模型训练目标是正常训练窗口的 MSE。训练数据分为 model-train 子集 $X^N_1$ 与 validation 子集 $X^N_2$；验证窗口误差升序形成参考分布 $E$。测试当前点重构误差 $g_t$ 相对验证误差的经验尾概率为：

$$p_t=\frac{\#\{e\in E:e\ge g_t\}}{\#E},\qquad \beta_t=\log\frac{\alpha}{p_t+\epsilon}.\tag{14}$$

当误差超过验证损失的高分位、$p_t$ 很小时，$\beta_t$ 可为正，表示当前点提供异常证据；低损失点的证据为负。顺序累计量：

$$s_t=\begin{cases}\max(s_{t-1}+\beta_t,0),&\neg\bigl(\bigwedge_{i=1}^{\delta}(\beta_{t-i}<0)\bigr),\\0,&\text{otherwise},\end{cases}\quad s_0=0.\tag{15}$$

连续 $\delta$ 个负证据触发清零（实验固定 $\delta=5$）；当 $s_t>h$ 时判为异常。其意图类似单侧累积证据：持续的多个中等异常可以累计越阈，连续低异常证据则重置。它对噪声的平滑是靠序列证据整合完成，不是单纯平滑原始 KPI。（PDF pp.5–6, §3.4, Eqs. 14–15）

对初始异常区间 $[t_a,t_b]$ 再做边界校正：

$$t_a^*=\arg\max\{t\le t_a:s_t=0\},\qquad t_b^*=\arg\max\{t_a\le t\le t_b:\beta_t>0\}.\tag{16–17}$$

作者解释 onset 回溯到累计证据离开零的时刻，offset 用异常段中最后一个正证据附近的位置。Boundary correction (BC) 的作用是修正累计阈值导致的延迟和边界；但它依赖已观察到的起止信息，端点逻辑具体应以论文伪代码 / 实现核对，不能把它解读成模型发现了故障物理起止。（PDF p.6, §3.4, Eqs. 16–17）

#### 5.4 在线性与阈值协议的关键区分

作者声明 score 在时刻 $t$ 只依赖当前重构误差、过去证据 / 累计分数及部署前 validation statistics，不用未来 test observations；网络只重建窗口最后点，故是因果在线推理。（Appendix G.2, L; pp.24–25）但论文 Best-F1 定义为联合 threshold sweep $\max_{\alpha,h}F1(\hat y(\alpha,h),y)$（Appendix F, Eq. 24），其中 $y$ 是 ground truth。**因此模型可在线计算不等于表格里最佳 F1 的阈值在部署时可无标签获得。** 复现或应用时要明确分开：固定阈值 / validation 校准结果和测试标签上最佳阈值的 oracle 上界。（PDF pp.16–17, Appendix F; Appendix L）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (6)、Eq. (7)、Eq. (8)、Eq. (10)、Eq. (11)、Eq. (13)、Eq. (14)、Eq. (16)、Eq. (24)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

CCM-TAD 先根据训练数据的跨通道相关性 profile 做 spectral clustering，并给每组通道单独 embedding；再以严格下三角时间掩码的 MLP mixer 重建当前点，最后将重构误差对训练内验证误差转成经验 p-value，累积逐时异常证据并回溯修正事件起止边界。

## 9. Experimental Evidence

#### 精读笔记原章节：6. Experiments

#### 6.1 Datasets and baselines

- **数据集**：SWaT（51 通道）、WADI（123）、PSM（25）、SMD（28 entities / 38 channels）、MSL（27 / 55）、SMAP（55 / 25）；Table 1 列各自 train / test 点数和异常比例。（PDF p.6, Table 1）
- **对照**：23 项，覆盖 AE / RNN / flow / graph / transformer / mixer / classical；含 CAROTS、CATCH、xLSTMAD、SensitiveHUE。基线表中的部分结果从原论文转载、部分使用公开代码重跑；需留意结果来源不同，Appendix E Table 8 罗列来源。（PDF pp.6–7, §4; Appendix E）
- **多实体比较协议**：i) 单模型跨 entities；ii) 每 entity 单独模型后 entity-wise F1 平均；iii) 每 entity 模型后合并 prediction 再算 F1。除非特别说明，多实体主结果是协议 iii。（PDF p.6, §4; Appendix G）
- **训练**：每个数据训练集留 20% 验证；look-back $L=24$、$\delta=5$、Adam、MSE，PyTorch 2.5.1 / CUDA 11.8、RTX 4090；用 Optuna 搜 $M,d,d_f,\alpha$ 等。（PDF pp.17–18, Appendix G）

#### 6.2 Main results

Table 2 的 Best-F1：单实体 PSM .716、SWaT .883、WADI .761；相对表中其它结果，WADI / PSM 增益突出。多实体各协议结果：

| Dataset | Protocol i | Protocol ii | Protocol iii |
| --- | ---: | ---: | ---: |
| MSL | .370 | .613 | .638 |
| SMD | .300 | .612 | .602 |
| SMAP | .389 | .529 | .551 |

作者称模型在多数表格数据集领先，并观察 per-entity 训练通常优于单一跨实体模型，认为实体差异显著。（PDF p.7, Table 2, §4.1）

Table 3 PR-AUC 补充了阈值无关的排序证据：CCM-TAD 在 SWaT .911、WADI .720；PSM .558 未优于 xLSTMAD .598；在 multi-entity 数据下也有与主 F1 排名不同的情形。附录 Table 10 显示 CCM-TAD VUS-ROC 并非全面领先（例如 SWaT .749 < SensitiveHUE online .819，PSM .546 < .668），而 VUS-PR 多数表现较好。此差异提示评价结论依赖指标与数据不平衡特征。（PDF pp.8, 18–19, Tables 3, 10）

#### 6.3 Sequential score 和模块消融

- **顺序分数 / BC**：Table 4 在 SWaT、PSM、WADI、MSL、SMD 上比较 point-based、Seq w/o BC、Seq w/ BC。加入累计与 BC 后 F1 / PR-AUC 多数上升；如 PSM 从 point .657 / .536 到 seq+BC .716 / .558，MSL .557 / .339 到 .638 / .610，SMD .562 / .509 到 .602 / .587。（PDF p.8, Table 4）
- **结构消融**：Table 5 十种组合对比 clustering、regular / causal / no temporal mixer、embedding mixer。完整 Case 10 得 SWaT .883 / PSM .716。Causal mixer 并不在所有相同配置下都单调优于其它项（如 Case 4 SWaT .861 低于 Case 1 .866），完整组合作用应看整表而非只看单独模块叙述。（PDF pp.8, Table 5）
- **表示可分性**：Table 6 的 NN-sep 从无 clustering 到 clustering，SWaT 65.63→91.30（+39.11%）、WADI 12.01→12.47（+3.83%）、PSM 66.74→66.78（+0.06%）。效果明显依数据而异，PSM 的距离指标几乎没变。（PDF p.8, Table 6）
- **cluster 变体**：profile spectral clustering 在 PSM .716、SWaT .883；相较 cosine-similarity graph / absolute-correlation graph / direct K-Means profile，优势大小不一且 SWaT 最后一种 .881 已接近 .883。（PDF p.8, Table 7）
- **在线与延迟**：Table 12 与 SensitiveHUE Online 五次种子比，CCM-TAD 在多数 F1 / PR-AUC / VUS-PR 更好，但 VUS-ROC 偶有较低值；WADI 的 ADD–false-alarm-period 曲线显示相似误报周期下平均 detection delay 更低。Table 13 中 GFLOPs 较少，但参数量依数据有高有低，推理延迟反而高于 SensitiveHUE Online，不过绝对仍为毫秒级。（PDF pp.19–20, Figs. 8, Tables 12–13）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

精读笔记未单独归类；分析推断需依据第 8–9 节的方法假设和实验范围，不能表述为已证实缺陷。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确写出的边界

作者仅研究 temporal causality；不发现 Granger / inter-channel causality，也不定位导致异常的具体通道。（Appendix M, p.25）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确写出的边界

多嵌入依赖多通道；论文不适用于 univariate TSAD。（Appendix M, p.25）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确写出的边界

默认训练数据 predominant clean；污染训练数据会降低性能。（PDF p.3）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 方法边界

Best-F1 通过在测试 ground-truth 上联合扫 $\alpha,h$ 得到；它是 benchmark 选择阈值后的分数，不等同无标签部署性能。（Appendix F, Eq. 24）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 方法边界

在线推理依赖固定 validation loss reference 与选定的 $\alpha,h$。验证集分布若不能代表部署正常态，经验 p-value 会失准；长期 concept drift 的 recalibration / reference update 未被展开。（Appendix G, L）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 方法边界

聚类来自训练期静态相关 profile；附录 J.5 仅用训练前 40% 与全训练数据所得聚类比较 SWaT / WADI，分数近似，不能概括为任意剧烈相关机制漂移都鲁棒。（Appendix J.5, pp.24–25）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 方法边界

各 ablation 单独重新调参，模块增益可能包含参数搜索差异；Table 6 的 clustering separability 在 PSM 几乎没有改善。（PDF p.7 §4.2; p.8 Tables 5–6）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验 / 方法边界

数据集涵盖工业控制、服务器、航天器等多通道，但没有同时输入负载、Trace、发布或业务操作上下文；在线识别不等于解释业务波动原因。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 将 correlation profile 分组与外部 workload / service graph / Trace 一起建模，判断合法状态切换与因果结构故障的差别。
- **[分析推断]** 固定部署前阈值报告 PR-AUC、事件 F1、告警延迟与误报周期，并对 test-label threshold sweep 单独作为 oracle 上界。
- **[分析推断]** 测试间歇性、低强度及与高峰负载并发的故障，量化累积证据的延迟 / 段合并效应。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **CAROTS**：两者都讨论变量关系，但 CAROTS 使用估计 Granger 图并构造因果保持 / 破坏增强及预测关系分数；CCM-TAD 明确不做 inter-channel causal discovery，cluster 按相关 profile 分组。
- **Graph-MoE**：Graph-MoE 的自注意力建窗口动态图、按 GNN 深度路由；CCM-TAD 训练期静态聚类再分组 embedding。前者图聚合多跳表示，后者减少跨相关型通道的共享嵌入干扰。
- **When Model Meets New Normals**：WMMNN 用测试时更新追随新正常；CCM-TAD 的在线 scoring 固定验证误差 reference，不做模型在线适配。
- **TFC**：TFC 将 curvature / frequency / temporal 三类 univariate 信号融合；CCM-TAD 的核心是 multivariate channel grouping 和 online event evidence accumulation。
- **CAPMix**：CAPMix 用合成异常和软标签学习分类边界；CCM-TAD 是 clean-dominant normal reconstruction + 经验尾概率证据。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.1–3, §§1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.2–3, §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | §§3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | Table 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | §§1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | §3.4 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.3–5, §§3.1–3.4, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.3, §3 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.3–4, §3.2.1 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.4, §3.2.1, Eq. 7, Eqs. 8–9, Eqs. 6–9 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.4–5, §3.2.2, Eq. 10 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.5–6, §3.3.1, Eq. 13, Eqs. 11–13 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.3–5, §3.1, §3.3.2, Eqs. 1–5 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.8–9, §4.2.5, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.5–6, §3.4, Eqs. 14–15 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.6, §3.4, Eqs. 16–17 | 精读笔记保留的原文定位 |
| Method / formulas | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.16–17, Eq. 24 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.6, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.6–7, §4, Table 8 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.6, §4 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.17–18 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF p.7, §4.1, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf | PDF pp.8, Table 3, Table 10 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "ccm-tad",
  "title_en": "Cluster-Aware Causal Mixer for Online Anomaly Detection in Multivariate Time Series",
  "title_zh": "用于多变量时间序列在线异常检测的聚类感知因果混合器",
  "authors": [
    "Md Mahmuddun Nabi Murad",
    "Yasin Yilmaz"
  ],
  "year": 2026,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ICML/Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
  "reading_note_path": "papers/ccm-tad/notes.md",
  "code_url": "https://github.com/Secure-and-Intelligent-Systems-Lab/CCM-TAD",
  "research_area": "因果时间遮罩与聚类通道建模的在线 MTSAD",
  "method_tags": [
    "TSAD multivariate online-detection causal-temporal-mask channel-clustering MLP-Mixer empirical-p-value sequential-scoring event-boundary ICML-2026"
  ],
  "research_scenario": "- [作者主张] 多变量时序在线异常检测：用当前 / 历史窗口重建最新观测，并把重构误差转换为顺序告警证据。（PDF §§3.1, 3.4） - [实验支持] SWaT、WADI、PSM、SMD、MSL、SMAP 六个基准；作者仅面向 multivariate，不适用于单变量。（Table 1; Appendix M）",
  "research_problem": "论文讨论多变量时间序列在线异常检测，目标是只利用当前及历史观测逐点重建最新观测并产生分数。作者归纳三个问题：（1）普通 MLP-Mixer 的 temporal mixing 可在窗口任意时点间混合，可能把未来数据泄露到较早时刻的表示；（2）所有通道由一个 embedding 联合表示时，相关结构差异可能造成伪相关；（3）逐点重构误差没有利用异常往往连续成段这一时间连续性。（PDF pp.1–3, §§1, 3） 论文中特别限定“causality”含义：它约束时间维信息流，不做 Granger 因果发现，也不估计跨通道因果图 / 根因通道。作者以多变量重构模型为基础，假设训练数据以正常样本为主；虽然文献习惯称 unsupervised TSAD，训练污染仍可能损伤模型。（PDF pp.2–3, §3 opening; Appendix M, p.25）",
  "core_challenges": [
    "[作者主张] 普通 MLP mixer 时间维全窗口混合可造成未来信息泄漏；统一 embedding 会混合不同相关结构；逐点分数忽略异常持续性。（PDF §§1, 3）",
    "[作者主张] 在线异常评分既需避免未来 test observations，也需要聚合连续的异常证据与校正边界。（§3.4; Appendix L）"
  ],
  "existing_method_limits": [
    "[作者主张] MLP mixer 缺少时间因果掩码；多通道若相关性异质，联合投影可能引入伪相关；单点阈值分类忽略前后时间联系。（PDF §§1, 3）",
    "[作者明确限定] 本文所谓因果仅为时间信息流因果，不发现 Granger / 通道间因果或根因变量。（Appendix M）"
  ],
  "core_idea": "CCM-TAD 先根据训练数据的跨通道相关性 profile 做 spectral clustering，并给每组通道单独 embedding；再以严格下三角时间掩码的 MLP mixer 重建当前点，最后将重构误差对训练内验证误差转成经验 p-value，累积逐时异常证据并回溯修正事件起止边界。",
  "technical_innovations": [
    {
      "name": "以相关 profile cosine graph 的 Laplacian 谱聚类通道",
      "author_claim": "**[作者主张]** 以相关 profile cosine graph 的 Laplacian 谱聚类通道；零相关 profile 通道单独成簇。（§3.2.1, Eqs. 6–9）",
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
      "source_locator": "**[作者主张]** 以相关 profile cosine graph 的 Laplacian 谱聚类通道；零相关 profile 通道单独成簇。（§3.2.1, Eqs. 6–9）"
    },
    {
      "name": "每簇独立 embedding",
      "author_claim": "**[作者主张]** 每簇独立 embedding，并按通道数分配总维度。（§3.2.2, Eq. 10）",
      "challenge_ids": [
        "C1",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.2 Causal temporal mixer 与 embedding mixer",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 每簇独立 embedding，并按通道数分配总维度。（§3.2.2, Eq. 10）"
    },
    {
      "name": "两层 temporal linear mixer 均用三角掩码",
      "author_claim": "**[作者主张]** 两层 temporal linear mixer 均用三角掩码，并以 $1/j$ 调整累积输入数；feature mixer 仍为标准两层 MLP。（§3.3, Eqs. 11–13）",
      "challenge_ids": [
        "C1",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.2 Causal temporal mixer 与 embedding mixer",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 两层 temporal linear mixer 均用三角掩码，并以 $1/j$ 调整累积输入数；feature mixer 仍为标准两层 MLP。（§3.3, Eqs. 11–13）"
    },
    {
      "name": "validation error empirical p-value → $\\beta_t=\\log",
      "author_claim": "**[作者主张]** validation error empirical p-value → $\\beta_t=\\log(\\alpha/(p_t+\\epsilon))$ → 带连续负证据 reset 的累积 $s_t$ → onset/offset backtracking。（§3.4, Eqs. 14–17）",
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
      "source_locator": "**[作者主张]** validation error empirical p-value → $\\beta_t=\\log(\\alpha/(p_t+\\epsilon))$ → 带连续负证据 reset 的累积 $s_t$ → onset/offset backtracking。（§3.4, Eqs. 14–17）"
    }
  ],
  "methodology": {
    "architecture": "text 训练序列计算 Pearson correlation profiles → profile cosine-similarity graph + spectral clustering 得 M 组通道 → 每组通道独立线性 embedding，拼成 d 维表示 → causal temporal mixer（两层受掩码线性变换 + GELU） → embedding mixer（两层线性层 + GELU）及残差 / BatchNorm → 线性 head 只重建 look-back 窗口的最后一个时点 → MSE 重构误差 gt → 与 validation loss 序列比较成经验 p-value pt 和证据 βt → 累积证据 st 超阈值 h 时告警，之后回溯修正边界 架构由“正常表示拆分”“因果时间建模”“事件级分数整理”三部分构成。前两部分改变重构网络和数据表示；第三部分不重训网络，而对已经产生的重构误差用验证集正常误差校准、顺序累积和边界回溯。（PDF pp.3–5, Fig. 1, §§3.1–3.4） 所有数据以训练集统计量做 min–max scaling；作者假设训练以正常数据为主，并明确指出污染可能降低检测表现。（PDF p.3, §3 opening）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 Input and cluster-aware multi-embedding",
      "5.2 Causal temporal mixer 与 embedding mixer",
      "5.3 从重构误差到 sequential anomaly evidence",
      "5.4 在线性与阈值协议的关键区分"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)",
      "Eq. (10)",
      "Eq. (11)",
      "Eq. (13)",
      "Eq. (14)",
      "Eq. (16)",
      "Eq. (24)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "CCM-TAD 先根据训练数据的跨通道相关性 profile 做 spectral clustering，并给每组通道单独 embedding；再以严格下三角时间掩码的 MLP mixer 重建当前点，最后将重构误差对训练内验证误差转成经验 p-value，累积逐时异常证据并回溯修正事件起止边界。"
  },
  "experimental_evidence": {
    "datasets": [
      "### 6.1 Datasets and baselines",
      "- 数据集：SWaT（51 通道）、WADI（123）、PSM（25）、SMD（28 entities / 38 channels）、MSL（27 / 55）、SMAP（55 / 25）；Table 1 列各自 train / test 点数和异常比例。（PDF p.6, Table 1） - 对照：23 项，覆盖 AE / RNN / flow / graph / transformer / mixer / classical；含 CAROTS、CATCH、xLSTMAD、SensitiveHUE。基线表中的部分结果从原论文转载、部分使用公开代码重跑；需留意结果来源不同，Appendix E Table 8 罗列来源。…",
      "| Dataset | Protocol i | Protocol ii | Protocol iii | | --- | ---: | ---: | ---: | | MSL | .370 | .613 | .638 | | SMD | .300 | .612 | .602 | | SMAP | .389 | .529 | .551 |",
      "作者称模型在多数表格数据集领先，并观察 per-entity 训练通常优于单一跨实体模型，认为实体差异显著。（PDF p.7, Table 2, §4.1）"
    ],
    "baselines": [
      "### 6.1 Datasets and baselines"
    ],
    "metrics": [
      "- 数据集：SWaT（51 通道）、WADI（123）、PSM（25）、SMD（28 entities / 38 channels）、MSL（27 / 55）、SMAP（55 / 25）；Table 1 列各自 train / test 点数和异常比例。（PDF p.6, Table 1） - 对照：23 项，覆盖 AE / RNN / flow / graph / transformer / mixer / classical；含 CAROTS、CATCH、xLSTMAD、SensitiveHUE。基线表中的部分结果从原论文转载、部分使用公开代码重跑；需留意结果来源不同，Appendix E Table 8 罗列来源。…",
      "Table 2 的 Best-F1：单实体 PSM .716、SWaT .883、WADI .761；相对表中其它结果，WADI / PSM 增益突出。多实体各协议结果：",
      "Table 3 PR-AUC 补充了阈值无关的排序证据：CCM-TAD 在 SWaT .911、WADI .720；PSM .558 未优于 xLSTMAD .598；在 multi-entity 数据下也有与主 F1 排名不同的情形。附录 Table 10 显示 CCM-TAD VUS-ROC 并非全面领先（例如 SWaT .749 < SensitiveHUE online .819，PSM .546 < .668），而 VUS-PR 多数表现较好。此差异提示评价结论依赖指标与数据不平衡特征。（PDF pp.8, 18–19, Tables 3, 10）",
      "- 顺序分数 / BC：Table 4 在 SWaT、PSM、WADI、MSL、SMD 上比较 point-based、Seq w/o BC、Seq w/ BC。加入累计与 BC 后 F1 / PR-AUC 多数上升；如 PSM 从 point .657 / .536 到 seq+BC .716 / .558，MSL .557 / .339 到 .638 / .610，SMD .562 / .509 到 .602 / .587。…"
    ],
    "main_results": [
      "- 数据集：SWaT（51 通道）、WADI（123）、PSM（25）、SMD（28 entities / 38 channels）、MSL（27 / 55）、SMAP（55 / 25）；Table 1 列各自 train / test 点数和异常比例。（PDF p.6, Table 1） - 对照：23 项，覆盖 AE / RNN / flow / graph / transformer / mixer / classical；含 CAROTS、CATCH、xLSTMAD、SensitiveHUE。基线表中的部分结果从原论文转载、部分使用公开代码重跑；需留意结果来源不同，Appendix E Table 8 罗列来源。（PDF pp.6–7, §4;…",
      "### 6.2 Main results",
      "Table 2 的 Best-F1：单实体 PSM .716、SWaT .883、WADI .761；相对表中其它结果，WADI / PSM 增益突出。多实体各协议结果：",
      "作者称模型在多数表格数据集领先，并观察 per-entity 训练通常优于单一跨实体模型，认为实体差异显著。（PDF p.7, Table 2, §4.1）",
      "Table 3 PR-AUC 补充了阈值无关的排序证据：CCM-TAD 在 SWaT .911、WADI .720；PSM .558 未优于 xLSTMAD .598；在 multi-entity 数据下也有与主 F1 排名不同的情形。附录 Table 10 显示 CCM-TAD VUS-ROC 并非全面领先（例如 SWaT .749 < SensitiveHUE online .819，PSM .546 < .668），而 VUS-PR 多数表现较好。此差异提示评价结论依赖指标与数据不平衡特征。（PDF pp.8, 18–19, Tables 3, 10）"
    ],
    "ablations": [
      "### 6.3 Sequential score 和模块消融",
      "- 顺序分数 / BC：Table 4 在 SWaT、PSM、WADI、MSL、SMD 上比较 point-based、Seq w/o BC、Seq w/ BC。加入累计与 BC 后 F1 / PR-AUC 多数上升；如 PSM 从 point .657 / .536 到 seq+BC .716 / .558，MSL .557 / .339 到 .638 / .610，SMD .562 / .509 到 .602 / .587。…"
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
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "见档案 §10.B；保持为分析而非已证实结论"
    ],
    "evidence_gaps": [
      "作者仅研究 temporal causality；不发现 Granger / inter-channel causality，也不定位导致异常的具体通道。（Appendix M, p.25）",
      "多嵌入依赖多通道；论文不适用于 univariate TSAD。（Appendix M, p.25）",
      "默认训练数据 predominant clean；污染训练数据会降低性能。（PDF p.3）",
      "Best-F1 通过在测试 ground-truth 上联合扫 $\\alpha,h$ 得到；它是 benchmark 选择阈值后的分数，不等同无标签部署性能。（Appendix F, Eq. 24）",
      "在线推理依赖固定 validation loss reference 与选定的 $\\alpha,h$。验证集分布若不能代表部署正常态，经验 p-value 会失准；长期 concept drift 的 recalibration / reference update 未被展开。（Appendix G, L）",
      "聚类来自训练期静态相关 profile；附录 J.5 仅用训练前 40% 与全训练数据所得聚类比较 SWaT / WADI，分数近似，不能概括为任意剧烈相关机制漂移都鲁棒。（Appendix J.5, pp.24–25）",
      "各 ablation 单独重新调参，模块增益可能包含参数搜索差异；Table 6 的 clustering separability 在 PSM 几乎没有改善。（PDF p.7 §4.2; p.8 Tables 5–6）",
      "数据集涵盖工业控制、服务器、航天器等多通道，但没有同时输入负载、Trace、发布或业务操作上下文；在线识别不等于解释业务波动原因。"
    ]
  },
  "research_implications": [
    "- [分析推断] 将 correlation profile 分组与外部 workload / service graph / Trace 一起建模，判断合法状态切换与因果结构故障的差别。 - [分析推断] 固定部署前阈值报告 PR-AUC、事件 F1、告警延迟与误报周期，并对 test-label threshold sweep 单独作为 oracle 上界。 - [分析推断] 测试间歇性、低强度及与高峰负载并发的故障，量化累积证据的延迟 / 段合并效应。"
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
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "ccm-tad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "graph-moe",
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
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.1–3, §§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.2–3, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "§§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "Table 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "§§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "§3.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.3–5, §§3.1–3.4, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF p.3, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.3–4, §3.2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF p.4, §3.2.1, Eq. 7, Eqs. 8–9, Eqs. 6–9",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.4–5, §3.2.2, Eq. 10",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf",
      "locator": "PDF pp.5–6, §3.3.1, Eq. 13, Eqs. 11–13",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "5832f4246e78629638c80a41d1a4c8cb87ec7f636c45f89d94c5c48ef814ecd7",
    "reading_note_sha256": "30b681aa826ce1b450f93742c0c6b6255a5b74fc975028c88d561cee6bea9afc",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "b75df1c048581a7107a6bec467c1011007ad63fee0820e3c69192c41f02dbd89"
  },
  "knowledge_card_path": "papers/ccm-tad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
