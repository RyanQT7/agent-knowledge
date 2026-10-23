# CAROTS：面向鲁棒多变量时序异常检测的因果感知对比学习

## 1. Metadata

- Title: Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection
- Authors: HyunGi Kim, Jisoo Mok, Dongjun Lee, Jaihyun Lew, Sungjae Kim, Sungroh Yoon
- Year / Venue: 2025 / ICML（PMLR 267, pp. 30591–30608）
- CCF: A（采用已人工确认的论文清单等级）
- Local PDF: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2025/ICML/Causality_Aware_Contrastive_Learning_for_Robust_Multivariate_Time_Series_Anomaly_Detection.pdf)
- Publisher: [PMLR proceedings](https://proceedings.mlr.press/v267/kim25aa.html)
- Code: [作者公开实现 CAROTS](https://github.com/kimanki/CAROTS)（论文首页 / Abstract）
- Knowledge Card: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

CAROTS 先从正常多变量序列学习 Granger 因果结构和预测器，再沿因果边生成保持因果关系的正常增强与破坏因果关系的伪异常，用带相似度筛选的单类对比损失学习表示，最后融合正常嵌入中心距离与因果预测残差进行检测。（PDF pp.1–6, Fig. 1, Eqs. (1)–(7)）

## 3. Problem Definition and Motivation

多变量时序异常检测（MTSAD）要识别多个相互作用变量中的异常。作者从**预测性 / Granger 因果关系**出发：若变量 $x_i$ 的过去能改善对 $x_j$ 的预测，则把 $x_i$ 视作 $x_j$ 的原因。邻接矩阵 $A\in\{0,1\}^{N\times N}$ 中 $A_{i,j}=1$ 表示 $x_i\to x_j$；因果发现器同时学习图 $A$ 与各变量的因果预测函数 $f_i$。（PDF p.3, §3.1）

因果视角下，训练正常期的跨变量关系在正常运行时保持相对稳定；异常可能使某些变量偏离由其过去和原因变量所预测的值。论文将异常概念化为至少一变量的因果预测残差超过 \(\delta\)：

\[
\exists x_t^i:\left|x_t^i-f_i(x^i_{<t},Pa(x^i)_{<t})\right|>\delta. \tag{2}
\]

这提供了“正常波动可能幅度大，但仍符合系统联动；故障可能幅度小，却破坏变量之间响应关系”的判别角度。作者用热浪导致空调运行更久作为保持因果关系的正常变化，与空调故障后不再随温度启动的因果关系破坏作对比。（PDF pp.1, 4, Introduction / §3.2）

核心假设是正常状态的因果矩阵 $A$ 及映射 $\{f_i\}$ 随时间基本不变。该假设适用于因果机制稳定的系统；发布、切换运行模式、外部控制介入等导致因果机制改变时，现成图可能过时。（PDF p.4, §3.2；Appendix §D）

## 4. Existing Methods and Their Limitations

- **仅学习重构误差 / 数值分布的检测器**：重构或预测模型可能因大幅但合理的操作变化产生高误差；单凭观测值偏离正常训练分布，不足以区分保持正常因果结构的变化与关系破坏。（作者论述，PDF pp.1–2）
- **通用对比式 MTSAD**：负样本通常依赖通用增强；若增强只产生表面数值扰动，没有利用跨变量因果结构，容易把正常相关变化和真实关系破坏混在一起。（作者论述，PDF pp.2–3）
- **普通单类对比损失**：将所有正常正样本挤进同一簇，会抹去共享正常因果关系、但语义模式不同的多个子簇，例如相同空调—温度关系下不同风量设置。CAROTS 认为这会压缩正常变化的表示空间。（作者论述，PDF p.5, §4.2）
- **因果发现不等于异常识别**：已有研究关注从时间序列恢复因果结构；CAROTS 的目标是把估计结构用作正常变化和故障扰动的训练依据。（PDF p.3, §2.2）

## 5. Overall Architecture

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

## 6. Method: Modules and Equations

### 6.1 因果发现器：拟合正常跨变量预测关系

对 $N$ 个变量的连续多变量序列 $x_t\in\mathbb R^N$ 以窗口长度 $w$ 切分，得到 $X_t\in\mathbb R^{w\times N}$。预测器 $F_{\theta,A}$ 用过去值及因果父节点预测当前变量。训练目标为预测均方误差加图稀疏惩罚：

\[
\hat\theta,\hat A=\arg\min_{\theta,A}\;\mathbb E_{X_t}\big[\operatorname{MSE}(F_{\theta,A}(X_{<t}),x_t)+\lambda\lVert A\rVert_1\big]. \tag{1}
\]

作者采用 CUTS+ 作为主因果发现器。因果矩阵按其方法从训练数据恢复，后续 CPA / CDA 将 $A$ 作为变换操作的图结构；$F_{\theta,A}$ 亦可输出相应时间点的因果预测值和 $A_{CD}$。（PDF pp.3–4, §3.1–4.1）

**语义边界：** 这里的因果边基于时间先后与预测增益的 Granger 意义，由观察数据训练模型得到；论文没有为所有边提供干预实验验证，因此不应把估计图等同于已经证实的物理因果图。（PDF pp.3–4, §3.1–3.2；此处为解释边界）

### 6.2 CPA：沿正常因果关系生成多样正例

Causality-Preserving Augmentor（CPA）输入一个多变量窗口 $X_t$，随机选择 $M<N$ 个原因变量 $C$，取其直接影响到的变量集合 $E$（由 $A$ 得到）。对原因变量过去值加小幅高斯噪声 $z\sim\mathcal N(0,\sigma^2)$，构成扰动后的历史 $X'_{<t}$；再用 $F_{\theta,A}(X'_{<t})$ 预测受影响变量当前值，并用这些预测替换原窗口中 $E$ 对应值。输出样本仍按已学因果机制联动，但具有不同取值，作为**正常变化正例**。（PDF pp.4–5, §4.1, Eq. (3), Fig. 2(a-1)）

补充实现中主实验 $M=1$，噪声标准差 \(\sigma=0.2\)，加在原因变量历史的最后一个时间点上。SWaT 上对 \(\sigma\) 从 0 到 0.4 的测试显示结果变化较小。（PDF pp.15–17, Appendix B, Table 11）

### 6.3 CDA：沿子图扰动制造因果破坏负例

Causality-Disturbing Augmentor（CDA）同样从随机原因变量 $C$ 出发，在因果图 $A$ 上做深度优先搜索（DFS），以截止概率 $p$ 结束扩展，抽取大小不同的有向子图；之后向子图所含变量注入与因果关系无关的随机偏置，破坏因果关系，作为**伪异常负例**。（PDF pp.4–5, §4.1, Fig. 2(a-2)）

附录给出的偏置候选值为 \(-0.5,-0.4,\dots,-0.1,0.1,\dots,0.5\)，在每个变量随机选取的 50% 时间点上施加；DFS 截止概率 $p=0.1$。作者将 CDA 应用于 $G_1$ 和 $G_2$，分别形成 $G_3$ 与 $G_4$，扩展负例对同一原始因果模式及其保持型变体均有效。（PDF pp.15–16, Appendix B）

### 6.4 SOC：逐渐容纳语义不同的正常正例

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

### 6.5 两类因果感知分数融合

- **对比嵌入分数 $A_{CL}$**：求训练期正例（原始 $G_1$ 和因果保持 $G_2$）嵌入质心 \(\mu_P\)，测试样本嵌入到质心的距离越大，越不像因果保持正常样本。
- **因果预测分数 $A_{CD}$**：预测器根据过去和父变量关系预测当前值，预测 MSE 越大，越不符合训练期学得的关系。

分别用训练分数均值与标准差做 z-score 标准化，再相加：

\[
A(X_t)=A^{norm}_{CL}(X_t)+A^{norm}_{CD}(X_t),\quad
A_{CL}(X_t)=D(E_\phi(X_t),\mu_P),\quad
A_{CD}(X_t)=\operatorname{MSE}(F_{\theta,A}(X_{<t}),x_t). \tag{7}
\]

CAROTS$^{\dagger}$ 是消融名，表示只用 $A_{CL}$、不做两分数融合。距离默认用 L2，WADI 和 VAR 使用余弦距离。（PDF pp.6, 14–16, §4.3, Eq. (7), Appendix B）

## 7. Experimental Setup

### 7.1 数据集和异常类型

作者评估五类真实数据：SWaT、WADI、PSM、SMD、MSL（实验使用 SMD 2-1 / 3-7、MSL P-14 / P-15 子序列），以及两个有明确因果机制的合成数据：非线性 Lorenz96 和线性 VAR。Lorenz96 / VAR 测试集注入 Point Global（PG）、Point Contextual（PC）、Collective Trend（CT）、Collective Global（CG）四类异常，用于检查不同局部/上下文、点/片段变化。合成数据 $N=128$，长 40,000 点，按 16,000 / 4,000 / 20,000 分训练、验证、测试；仅测试集注入异常，比例 0.01，10 个变量随机受影响，难度因子 \(\lambda=2\)（CG 例外）。SWaT、WADI 为计算效率下采样 5 倍。（PDF pp.6, 13–15, 16）

Appendix Table 7 给出变量数、训练 / 测试点数、异常率与 ADF 检验。例如 SWaT 51 变量，WADI 123，PSM 25，SMD 38，MSL 子序列 55；SWaT / WADI / MSL 及 SMD 3-7 等部分子集的 ADF p 值较高。该分析支持所选数据有非平稳性，但它本身不验证因果机制确实稳定。（PDF p.13, Table 7）

### 7.2 基线、训练和评价

重构类基线：Anomaly Transformer、TimesNet、USAD；对比学习类：SimCLR、SSD、CSI、CTAD、CARLA。CAROTS 主要采用一层 LSTM 编码器。训练 / 验证 / 测试用滑动窗；训练集均值和标准差用于标准化；训练数据中 20% 留作验证；默认窗口 10、batch 256、30 epochs，温度 \(\tau=0.1\)，\(\alpha\) 从 0.5 线性升到 0.9；三随机种子报告均值。（PDF pp.6, 13–16）

Appendix B 给出 Adam、梯度裁剪范数 1、5 epoch warm-up 后 cosine 学习率调度，按验证损失选模型；报告 AUROC、AUPRC 和 best F1，不报告 point-adjusted F1，因为其可能高估逐点检测能力。best F1 的阈值取得方式在正文未完全说明，是比较阈值敏感指标时的复现注意事项。（PDF pp.6, 16）

## 8. Results and Ablations

### 8.1 真实数据

Table 1 中 CAROTS 在 SWaT 上 AUROC 0.852、AUPRC 0.764、F1 0.791；在 PSM 上为 0.783 / 0.595 / 0.603。相对多种对比与重构基线，几组数据上表现较强；但并非所有数据或指标都占优。特别是完整融合模型在 WADI 上 AUROC / AUPRC / F1 为 **0.502 / 0.056 / 0.143**，而只用 $A_{CL}$ 的 CAROTS$^{\dagger}$ 为 **0.622 / 0.260 / 0.391**；Table 10 消融复现相同排序，说明因果预测误差融合可能在某些数据集上拖累检测。（PDF pp.7–8, Table 1, Table 4, Appendix Table 10）

论文称 CAROTS$^{\dagger}$ 在 WADI、MSL P-15 等困难数据上已强于其他方法，但 Table 1 / Appendix Table 10 的 WADI 数值显示其相对完整模型提升很大，完整 CAROTS 也低于 CTAD 的 WADI AUROC 0.599、AUPRC 0.327、F1 0.374。后续比较应按具体数据和分数版本解读，而不能照搬“几乎所有指标和数据集最佳”的概括。（PDF pp.2, 7–8, 17, Tables 1, 10）

### 8.2 合成因果数据

在显式因果系统中，Lorenz96 上 CAROTS 对 PG / PC / CT / CG 的 AUROC 分别为 **0.998 / 0.975 / 0.874 / 0.788**，平均 0.909；VAR 上为 **0.612 / 0.648 / 0.963 / 0.997**，平均 0.805。强点包括 Lorenz96 点异常、VAR collective anomalies；VAR 的 PG / PC 仍较难。Fig. 3 调低 \(\lambda\) 加大注入难度时，作者称多数方法下降，而 CAROTS 对一些困难等级仍有效。结论支持在**按所设生成机制构造**的合成场景里使用因果结构有益，但不同异常类型间的效果差异很大。（PDF pp.6, 8, Table 2, Fig. 3）

### 8.3 组件消融

SWaT Table 4 的 AUROC / AUPRC / F1：完整模型 **0.852 / 0.764 / 0.792**；去 CPA 为 0.850 / 0.721 / 0.775；去 CDA 为 0.842 / 0.740 / 0.786；去相似度筛选为 0.819 / 0.733 / 0.769；去 $A_{CL}$ 为 0.814 / 0.722 / 0.769；去 $A_{CD}$（CAROTS$^{\dagger}$）为 0.861 / 0.760 / 0.789。支持 CPA、CDA 与 SOC 有贡献，尤其 SOC 去除后 AUROC 降低；但在 SWaT，去 $A_{CD}$ 的 AUROC 反而更高、F1 接近完整模型，说明“融合必然更优”并未得到本表支持。（PDF p.8, Table 4）

Appendix Table 10 将消融扩展到 7 个现实子集和 2 个合成数据；例如 WADI 去 $A_{CD}$ AUROC 0.622，完整为 0.502；MSL P-15 的 AUROC 则从去掉 $A_{CD}$ 时的 0.683 提升到完整模型的 0.701，说明该分数的作用依数据集而异。这进一步说明组件贡献存在场景差异。（PDF p.17, Table 10）

### 8.4 鲁棒性、可视化与成本

- Table 3 测试温度 \(\tau\) 与 batch 大小：SWaT 表现稳定；PSM 在高温度下 AUROC/AUPRC/F1 会下降（如 \(\tau=0.2\) 为 0.76 / 0.56 / 0.57，\(\tau=1.6\) 为 0.61 / 0.44 / 0.46），故“对超参数鲁棒”的证据并非每个数据集同等强。（PDF p.8, Table 3）
- Table 5 将因果发现器替换成 NGC、CUTS、CUTS+：各自在哪套数据最好不一，但结果相近，说明框架可兼容多种图估计器；不能据此证明学得的因果图与真实因果图相同。（PDF p.8, Table 5）
- Table 6 比较 LSTM、GRU、iTransformer 编码器，在 SWaT 与 PSM 差距较小、GRU 部分指标最好，显示并非绑定单一编码器。（PDF p.8, Table 6）
- Table 9 的 \(\alpha\) 固定值和线性调度对 SWaT 有影响；Table 11 中 CPA 的 \(\sigma\) 取 0–0.4 结果变化不大。（PDF pp.16–17）
- t-SNE Fig. 4 显示正例与负例逐渐分离且正例可形成多个语义簇，属于定性可视化，不是因果结构或簇分离的形式检验。（PDF p.9, Fig. 4）
- Table 13 报训练时间 CAROTS 25 分钟、Anomaly Transformer 12、TimesNet 56、USAD/SimCLR/SSD 6；但比较**排除了因果发现器预训练时间**，不代表端到端总成本。（PDF p.18, Table 13）

## 9. Contributions and Strengths

- 以 Granger 预测结构区分“变量值改变但系统联动仍正常”与“变量间响应关系受损”，正面处理正常波动不应一概当异常的问题。（PDF pp.1–4）
- CPA 通过因果预测补足受影响变量，构造超出原观测值范围但仍保持机制的正例；CDA 在图上选子图扰动制造结构化负例，增强方案有明确语义依据。（PDF pp.4–5, Fig. 2）
- SOC 避免将语义差异大的所有正常样本强行压成一点，并用相似度阈值逐步放宽正例范围。（PDF pp.5–6, Eq. (6), Fig. 2）
- 公开代码，提供因果发现器替换、编码器替换、增强噪声、阈值调度和分数融合等多组消融；合成 VAR / Lorenz96 为因果假设提供受控验证。（PDF pp.1, 8, 15–18）

## 10. Limitations and Reproduction Value

### 作者明确讨论

- 假设正常因果结构基本时间不变；真实系统可能因条件演化或外部干预而发生渐进或突发因果变化。（Appendix §D, PDF p.17）
- 只聚焦直接因果关系，未显式处理隐藏混杂变量；外生变量会影响观察到的结构，作者建议引入领域知识和辅助数据。（Appendix §D, PDF p.17）

### 基于论文证据的分析

- 因果图从训练数据中的预测依赖估计，CPA / CDA 的语义正确性取决于图和 $F_{\theta,A}$ 是否可靠；合成数据上有明确因果生成机制，但现实数据没有真实因果图 ground truth。Table 12 仅显示按时间分块重新学习的图相似度高（SWaT 0.911–0.981、WADI 0.959–0.978、PSM 0.898–0.955），证明一致性而非因果正确性。（PDF p.18, Table 12）
- CAROTS 用自身分数与训练得分统计做异常排序/阈值评估，但业务上下文没有作为外生条件输入；热浪例子说明的是因果保持变化的概念，不能等同于在真实业务负载跃迁与故障共现下验证了鲁棒性。（PDF pp.1, 6–8）
- 关系变化本身可能是正常业务模式切换，也可能是真故障；因果静态假设在这个关键边界上仍需上下文或在线图更新支持。若正常负载变化改变系统调度/控制机制，可能被固定图当异常；反之，故障若不破坏估计图也可能漏检。
- 完整分数 $A_{CL}+A_{CD}$ 不总是比 $A_{CL}$ 单项好，WADI 尤其明显；使用 z-score 相加仍需检测器 / 数据集级校准。结果没有证明该融合在不平衡、故障代价和线上阈值约束下普遍更佳。（PDF pp.7–8, 17）
- 运行成本表排除因果发现器预训练时间；真实数据结果以 best F1 等离线指标为主，且没有业务状态切换的在线延迟 / 误报成本验证。SOC 主实验需按数据集处理窗口长度、距离形式等配置，复现时要对齐附录实现。（PDF pp.6, 14, 18）
- Table 1 / Table 10 对 WADI 中完整模型与 CAROTS$^{\dagger}$ 的差异十分显著，和论文概括性主张存在张力；复核应报告逐数据集表格结果，不应只记 overall claim。（PDF pp.7–8, 17）

### 复现价值

作者提供 GitHub 实现；关键实现参数、基线列表、三随机种子、多种消融及数据构造细节可作为复现依据。优先核查数据窗、标准化、因果发现器预训练、CPA/CDA 的时间点与变量掩码、SOC 的正负配对方式和阈值协议；记录端到端成本（含 causal discovery），不要把论文 Table 13 的对比时间误当全流水线成本。本文只要求精读与知识提取，本笔记未进行代码复现或模型训练。

## 11. Relationship to Existing Knowledge

- 与 CAPMix：两者都把训练期异常增强用于改进正常变化覆盖。CAPMix 按 DTW 距离软化形态伪异常标签；CAROTS 用估计的跨变量预测图生成因果保持正常与因果破坏伪异常。后者能表达变量联动，但依赖因果模型假设和训练图质量。（[CAPMix 笔记](../capmix/notes.md)）
- 与 When Model Meets New Normals：后者在测试时以 EMA + 预测正常样本更新模型，处理训练 / 测试 $P$ 漂移；CAROTS 主要在训练阶段建固定因果机制与表示，假设测试期关系保持稳定。两者互补，但 CAROTS 没有在线适应结构变化。（[When Model Meets New Normals 笔记](../when-model-meets-new-normals/notes.md)）
- 与后续 CrossAD：待完整阅读其跨尺度关联及跨窗口建模机制后比较；目前不把相关性直接称作因果关系。
- 与该清单中的 GCAD、Structured Temporal Causality、Cluster-Aware Causal Mixer：均涉及因果信息的 MTSAD 方向；后续逐篇读完后再比较图学习方式、时间变化假设及证据覆盖。

## 12. My Understanding

CAROTS 把“正常”定义得比正常值域更结构化：一组变量可以一起大幅变化，只要这些变化仍符合训练期学得的驱动—响应关系，就可以在 CPA 中作为正常正例。CDA 则针对性破坏图上关系。这比单纯加入数值噪声更贴近某些工业系统的变量联动。但其“因果”首先是预测数据估计出来的 Granger 依赖；真实系统的外生变量、工作模式、控制策略和因果机制变化，都会改变图或预测关系。CAROTS 给出了一个解释型信号来源和可审查的假设，不等于已经识别业务波动原因或证明因果发现正确。

## 13. Questions

1. 当业务负载、控制策略或部署改变导致因果机制合法切换时，CAROTS 如何区分新模式与真实故障？
2. 能否把业务负载、发布记录、Trace 或领域知识作为外生变量纳入 $F_{\theta,A}$，减少遗漏变量造成的伪因果边？
3. 如何在不提供真实故障标签时验证因果图及 CPA / CDA 的语义保真度，而不只是检查图相似度和下游 AUROC？
4. $A_{CL}$ 与 $A_{CD}$ 的分数融合在 WADI 显著弱于只用 $A_{CL}$，是否需要按场景学习校准或门控机制？
5. 若异常保留训练期因果结构（例如同一因果链上的整体负载拥塞），而正常工况切换破坏旧结构，如何扩展故障定义？
6. 真实服务上端到端训练 / 更新 / 推理成本、在线阈值和逐事件误报代价如何测量？

## 14. Related Work

- CUTS+：CAROTS 主实验的预测式因果图 / 变量预测器。（PDF pp.3–4）
- CTAD、CARLA、SimCLR 等：对比学习 MTSAD 基线；CAROTS 的差异在于按因果结构设计正负增强。（PDF pp.2–3, 6–8）
- GCAD、GCFormer、Structured Temporal Causality：因果信息用于时间序列异常检测的相关路线，需与本集合后续笔记比较。（PDF pp.3, 11）
- CAPMix、When Model Meets New Normals：知识库中已完成的训练期增强与测试时新正常适应笔记，交叉链接见上节。

## 15. Tags

`TSAD` `MTSAD` `causal-discovery` `Granger-causality` `contrastive-learning` `normal-variation` `synthetic-anomaly` `one-class-learning` `robustness` `context`
