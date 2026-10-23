# CCM-TAD：面向在线多变量异常检测的聚类感知因果混合器

## 1. Metadata

- Title: Cluster-Aware Causal Mixer for Online Anomaly Detection in Multivariate Time Series
- Authors: Md Mahmuddun Nabi Murad, Yasin Yilmaz
- Year / Venue: 2026 / ICML (PMLR 306)
- CCF: A（按已人工确认的清单）
- Official source: [PMLR paper page](https://proceedings.mlr.press/v306/murad26a.html)
- Code: [CCM-TAD](https://github.com/Secure-and-Intelligent-Systems-Lab/CCM-TAD)
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local PDF: [CCM-TAD PDF](../../sources/papers/tsad-2024-2026/2026/ICML/Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf)

## 2. One-Sentence Summary

CCM-TAD 先根据训练数据的跨通道相关性 profile 做 spectral clustering，并给每组通道单独 embedding；再以严格下三角时间掩码的 MLP mixer 重建当前点，最后将重构误差对训练内验证误差转成经验 p-value，累积逐时异常证据并回溯修正事件起止边界。

## 3. Research Problem and Motivation

论文讨论多变量时间序列在线异常检测，目标是只利用当前及历史观测逐点重建最新观测并产生分数。作者归纳三个问题：（1）普通 MLP-Mixer 的 temporal mixing 可在窗口任意时点间混合，可能把未来数据泄露到较早时刻的表示；（2）所有通道由一个 embedding 联合表示时，相关结构差异可能造成伪相关；（3）逐点重构误差没有利用异常往往连续成段这一时间连续性。（PDF pp.1–3, §§1, 3）

论文中特别限定“causality”含义：它约束**时间维信息流**，不做 Granger 因果发现，也不估计跨通道因果图 / 根因通道。作者以多变量重构模型为基础，假设训练数据以正常样本为主；虽然文献习惯称 unsupervised TSAD，训练污染仍可能损伤模型。（PDF pp.2–3, §3 opening; Appendix M, p.25）

## 4. Overall Architecture

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

## 5. Detailed Method

### 5.1 Input and cluster-aware multi-embedding

给定 look-back 窗口 $X^L\in\mathbb R^{L\times C}$（$C$ 个通道），作者先用训练集 Pearson 相关矩阵 $\Phi\in[-1,1]^{C\times C}$，再取绝对值 $\Phi^{abs}$。通道 $i$ 的 correlation profile 是矩阵第 $i$ 行 $\phi_i\in[0,1]^C$，表示它与所有通道的相关性分布。常量通道产生的 NaN 相关系数置零；全零 profile 通道单独归为第 $M$ 组。（PDF pp.3–4, §3.2.1）

对其余通道，构造 profile 间 cosine similarity：

$$w_{ij}=\begin{cases}\frac{(\phi'_i)^\top\phi'_j}{\|\phi'_i\|\|\phi'_j\|}, & i\ne j,\\0,&i=j.\end{cases}\tag{6}$$

随后以 $L_n=I-D^{-1/2}WD^{-1/2}$ 构造 normalized graph Laplacian（Eq. 7），取最小非零特征值对应的前 $M'=M-1$ 个 eigenvectors $V$，以 $U=D^{-1/2}V$ 做归一化，再对 $U$ 各行 K-Means 得 cluster index（Eqs. 8–9）。这个流程基于完整相关 profile 的相似性，而不是单独按 $|\Phi_{ij}|$ 强弱把直接高相关通道放一起。（PDF p.4, §3.2.1, Eqs. 6–9）

得到 $M$ 个通道组后，每组各有 embedding layer，并按组通道数 $C_i$ 分配维度 $d_i$：前 $M-1$ 组用 $\lfloor C_i d/C\rfloor$，最后一组取余，确保 $\sum_i d_i=d$（Eq. 10）。拼接后维度为 $d$。作者推导在簇规模近似均匀时，参数量从单层 $O(Cd)$ 变为总计约 $O(Cd/M)$；但该复杂度收益取决于通道组的分布与实现。（PDF pp.4–5, §3.2.2, Eq. 10）

**作用解释：** 通道被分组的根据是其与其他通道“相关 profile 的形状”相似，而不是原始值相关性正负方向，也不是业务拓扑。各组独立编码的假设是减少异质相关模式在同一投影中的纠缠；其监督证据主要来自下游分数和 representation separability 消融。

### 5.2 Causal temporal mixer 与 embedding mixer

嵌入表示经 BatchNorm 后进入若干 mixer blocks。时间 mixer 输入转置到 $d\times L$。对线性层权重 $\Theta^c\in\mathbb R^{L\times L}$ 乘上上三角掩码 $\Gamma$：

$$\gamma_{i,j}=\begin{cases}1/j,&i\le j,\\0,&i>j,\end{cases}\quad\Theta^u=\Gamma\odot\Theta^c.\tag{11–12}$$

第 $k$ 个 embedding feature 的时间映射为 $x^{(k)}_{c1}=x^{(k)}_c\Theta^u+b$（Eq. 13），之后接 GELU 与第二个同类因果线性层。按论文约定，输出时间位置 $j$ 只能依赖输入位置 $i\le j$，因此因果掩码禁止 future-to-past 依赖；$1/j$ 缩放用于稳定不同位置可累积历史长度不同造成的优化动态。正文从矩阵索引方向解释掩码，读公式时应按其文字定义理解三角方向。（PDF pp.5–6, §3.3.1, Eqs. 11–13; Appendix J.4）

时间 mixer 后有残差和 BatchNorm。embedding mixer 在每个时间位置沿特征维用两层标准线性层 $d\to d d_f\to d$，中间 GELU；再与时间 mixer 输出和初始嵌入做残差相加、BatchNorm（Eqs. 1–5）。重复多个 blocks 后，head 映射回 $C$ 通道，并只输出 look-back 窗口最后时刻的重构 $\hat x_t$。（PDF pp.3–5, §3.1, §3.3.2, Eqs. 1–5）

作者用梯度图验证 causality：对 $t=15,c=19$ 的重构损失回传，普通 mixer 对未来位置梯度非零，causal mixer 对 $\tau>15$ 的梯度为零（Fig. 3）。但附录说明，掩码是 mixer 内部信息流约束，不是跨变量结构因果，也非从观察数据识别 intervention 因果效应。（PDF pp.8–9, §4.2.5, Fig. 3; Appendix K, p.25）

### 5.3 从重构误差到 sequential anomaly evidence

模型训练目标是正常训练窗口的 MSE。训练数据分为 model-train 子集 $X^N_1$ 与 validation 子集 $X^N_2$；验证窗口误差升序形成参考分布 $E$。测试当前点重构误差 $g_t$ 相对验证误差的经验尾概率为：

$$p_t=\frac{\#\{e\in E:e\ge g_t\}}{\#E},\qquad \beta_t=\log\frac{\alpha}{p_t+\epsilon}.\tag{14}$$

当误差超过验证损失的高分位、$p_t$ 很小时，$\beta_t$ 可为正，表示当前点提供异常证据；低损失点的证据为负。顺序累计量：

$$s_t=\begin{cases}\max(s_{t-1}+\beta_t,0),&\neg\bigl(\bigwedge_{i=1}^{\delta}(\beta_{t-i}<0)\bigr),\\0,&\text{otherwise},\end{cases}\quad s_0=0.\tag{15}$$

连续 $\delta$ 个负证据触发清零（实验固定 $\delta=5$）；当 $s_t>h$ 时判为异常。其意图类似单侧累积证据：持续的多个中等异常可以累计越阈，连续低异常证据则重置。它对噪声的平滑是靠序列证据整合完成，不是单纯平滑原始 KPI。（PDF pp.5–6, §3.4, Eqs. 14–15）

对初始异常区间 $[t_a,t_b]$ 再做边界校正：

$$t_a^*=\arg\max\{t\le t_a:s_t=0\},\qquad t_b^*=\arg\max\{t_a\le t\le t_b:\beta_t>0\}.\tag{16–17}$$

作者解释 onset 回溯到累计证据离开零的时刻，offset 用异常段中最后一个正证据附近的位置。Boundary correction (BC) 的作用是修正累计阈值导致的延迟和边界；但它依赖已观察到的起止信息，端点逻辑具体应以论文伪代码 / 实现核对，不能把它解读成模型发现了故障物理起止。（PDF p.6, §3.4, Eqs. 16–17）

### 5.4 在线性与阈值协议的关键区分

作者声明 score 在时刻 $t$ 只依赖当前重构误差、过去证据 / 累计分数及部署前 validation statistics，不用未来 test observations；网络只重建窗口最后点，故是因果在线推理。（Appendix G.2, L; pp.24–25）但论文 Best-F1 定义为联合 threshold sweep $\max_{\alpha,h}F1(\hat y(\alpha,h),y)$（Appendix F, Eq. 24），其中 $y$ 是 ground truth。**因此模型可在线计算不等于表格里最佳 F1 的阈值在部署时可无标签获得。** 复现或应用时要明确分开：固定阈值 / validation 校准结果和测试标签上最佳阈值的 oracle 上界。（PDF pp.16–17, Appendix F; Appendix L）

## 6. Experiments

### 6.1 Datasets and baselines

- **数据集**：SWaT（51 通道）、WADI（123）、PSM（25）、SMD（28 entities / 38 channels）、MSL（27 / 55）、SMAP（55 / 25）；Table 1 列各自 train / test 点数和异常比例。（PDF p.6, Table 1）
- **对照**：23 项，覆盖 AE / RNN / flow / graph / transformer / mixer / classical；含 CAROTS、CATCH、xLSTMAD、SensitiveHUE。基线表中的部分结果从原论文转载、部分使用公开代码重跑；需留意结果来源不同，Appendix E Table 8 罗列来源。（PDF pp.6–7, §4; Appendix E）
- **多实体比较协议**：i) 单模型跨 entities；ii) 每 entity 单独模型后 entity-wise F1 平均；iii) 每 entity 模型后合并 prediction 再算 F1。除非特别说明，多实体主结果是协议 iii。（PDF p.6, §4; Appendix G）
- **训练**：每个数据训练集留 20% 验证；look-back $L=24$、$\delta=5$、Adam、MSE，PyTorch 2.5.1 / CUDA 11.8、RTX 4090；用 Optuna 搜 $M,d,d_f,\alpha$ 等。（PDF pp.17–18, Appendix G）

### 6.2 Main results

Table 2 的 Best-F1：单实体 PSM .716、SWaT .883、WADI .761；相对表中其它结果，WADI / PSM 增益突出。多实体各协议结果：

| Dataset | Protocol i | Protocol ii | Protocol iii |
| --- | ---: | ---: | ---: |
| MSL | .370 | .613 | .638 |
| SMD | .300 | .612 | .602 |
| SMAP | .389 | .529 | .551 |

作者称模型在多数表格数据集领先，并观察 per-entity 训练通常优于单一跨实体模型，认为实体差异显著。（PDF p.7, Table 2, §4.1）

Table 3 PR-AUC 补充了阈值无关的排序证据：CCM-TAD 在 SWaT .911、WADI .720；PSM .558 未优于 xLSTMAD .598；在 multi-entity 数据下也有与主 F1 排名不同的情形。附录 Table 10 显示 CCM-TAD VUS-ROC 并非全面领先（例如 SWaT .749 < SensitiveHUE online .819，PSM .546 < .668），而 VUS-PR 多数表现较好。此差异提示评价结论依赖指标与数据不平衡特征。（PDF pp.8, 18–19, Tables 3, 10）

### 6.3 Sequential score 和模块消融

- **顺序分数 / BC**：Table 4 在 SWaT、PSM、WADI、MSL、SMD 上比较 point-based、Seq w/o BC、Seq w/ BC。加入累计与 BC 后 F1 / PR-AUC 多数上升；如 PSM 从 point .657 / .536 到 seq+BC .716 / .558，MSL .557 / .339 到 .638 / .610，SMD .562 / .509 到 .602 / .587。（PDF p.8, Table 4）
- **结构消融**：Table 5 十种组合对比 clustering、regular / causal / no temporal mixer、embedding mixer。完整 Case 10 得 SWaT .883 / PSM .716。Causal mixer 并不在所有相同配置下都单调优于其它项（如 Case 4 SWaT .861 低于 Case 1 .866），完整组合作用应看整表而非只看单独模块叙述。（PDF pp.8, Table 5）
- **表示可分性**：Table 6 的 NN-sep 从无 clustering 到 clustering，SWaT 65.63→91.30（+39.11%）、WADI 12.01→12.47（+3.83%）、PSM 66.74→66.78（+0.06%）。效果明显依数据而异，PSM 的距离指标几乎没变。（PDF p.8, Table 6）
- **cluster 变体**：profile spectral clustering 在 PSM .716、SWaT .883；相较 cosine-similarity graph / absolute-correlation graph / direct K-Means profile，优势大小不一且 SWaT 最后一种 .881 已接近 .883。（PDF p.8, Table 7）
- **在线与延迟**：Table 12 与 SensitiveHUE Online 五次种子比，CCM-TAD 在多数 F1 / PR-AUC / VUS-PR 更好，但 VUS-ROC 偶有较低值；WADI 的 ADD–false-alarm-period 曲线显示相似误报周期下平均 detection delay 更低。Table 13 中 GFLOPs 较少，但参数量依数据有高有低，推理延迟反而高于 SensitiveHUE Online，不过绝对仍为毫秒级。（PDF pp.19–20, Figs. 8, Tables 12–13）

## 7. Contributions and Strengths

- 把相关 profile 相似性与聚类感知 embedding 联合，针对跨通道表示混杂。
- 在 MLP-Mixer 时间维加权重掩码以保证当前输出不引用窗口未来点，并以梯度图检验。
- 用验证正常误差的经验 tail probability 做单点证据，累积并通过 reset / backtracking 输出连续告警片段。
- 论文给出在线 future-free 评分说明、跨实体评估协议、PR-AUC / VUS / ADD-FAP 和计算量，不仅报一个 AUROC。

## 8. Limitations and Reproduction Value

### 作者明确写出的边界

- 作者仅研究 temporal causality；不发现 Granger / inter-channel causality，也不定位导致异常的具体通道。（Appendix M, p.25）
- 多嵌入依赖多通道；论文不适用于 univariate TSAD。（Appendix M, p.25）
- 默认训练数据 predominant clean；污染训练数据会降低性能。（PDF p.3）

### 实验 / 方法边界

- Best-F1 通过在测试 ground-truth 上联合扫 $\alpha,h$ 得到；它是 benchmark 选择阈值后的分数，不等同无标签部署性能。（Appendix F, Eq. 24）
- 在线推理依赖固定 validation loss reference 与选定的 $\alpha,h$。验证集分布若不能代表部署正常态，经验 p-value 会失准；长期 concept drift 的 recalibration / reference update 未被展开。（Appendix G, L）
- 聚类来自训练期静态相关 profile；附录 J.5 仅用训练前 40% 与全训练数据所得聚类比较 SWaT / WADI，分数近似，不能概括为任意剧烈相关机制漂移都鲁棒。（Appendix J.5, pp.24–25）
- 各 ablation 单独重新调参，模块增益可能包含参数搜索差异；Table 6 的 clustering separability 在 PSM 几乎没有改善。（PDF p.7 §4.2; p.8 Tables 5–6）
- 数据集涵盖工业控制、服务器、航天器等多通道，但没有同时输入负载、Trace、发布或业务操作上下文；在线识别不等于解释业务波动原因。

### 复现价值

作者提供公开代码、完整 Appendix、超参数范围、运行硬件和 gradient / cluster ablation，复现材料相对充分。优先核验：best-F1 sweep 是否只用于 oracle 汇报、在线 h 如何选；p-value 大小样本行为；窗口起点、缺测 / padding；validation 是否与时间顺序隔离；特征归一化和每 entity 独立模型协议。（Code; Appendix F–G）

## 9. Relationship to Other Papers

- **CAROTS**：两者都讨论变量关系，但 CAROTS 使用估计 Granger 图并构造因果保持 / 破坏增强及预测关系分数；CCM-TAD 明确不做 inter-channel causal discovery，cluster 按相关 profile 分组。
- **Graph-MoE**：Graph-MoE 的自注意力建窗口动态图、按 GNN 深度路由；CCM-TAD 训练期静态聚类再分组 embedding。前者图聚合多跳表示，后者减少跨相关型通道的共享嵌入干扰。
- **When Model Meets New Normals**：WMMNN 用测试时更新追随新正常；CCM-TAD 的在线 scoring 固定验证误差 reference，不做模型在线适配。
- **TFC**：TFC 将 curvature / frequency / temporal 三类 univariate 信号融合；CCM-TAD 的核心是 multivariate channel grouping 和 online event evidence accumulation。
- **CAPMix**：CAPMix 用合成异常和软标签学习分类边界；CCM-TAD 是 clean-dominant normal reconstruction + 经验尾概率证据。

## 10. Questions

1. 若系统由多个运行态引起的跨通道相关性变化本身合法，静态 correlation profile clustering 如何处理？
2. 如何使用业务负载 / Trace / release 语义区分合法联动变化和伴随联动故障？
3. 以 test label 同时调 $\alpha,h$ 的 Best-F1 与严格部署前固定阈值结果之间差多少？
4. 连续负证据 reset 和边界回溯在低频、间歇故障及负载峰谷转换下的告警延迟 / 合并行为如何？
5. 当异常已开始但低重构误差被 reference 吸收时，顺序积分能否补救？异常污染 validation 后如何诊断？
6. causal temporal mask 如何扩展到不等采样、多个观测时延及跨变量机制解释？

## 11. Useful Definitions

- **Correlation profile**：某通道与所有通道的绝对 Pearson 相关向量，用其形状相似度而非单一 pairwise correlation clustering。
- **Temporal causal mixer**：时间线性映射权重被三角掩码，以当前位置输出只读取当前及过去窗口点；不表示变量间因果发现。
- **Sequential anomaly evidence**：重构误差对比验证误差得到尾概率后取 log evidence，并做带 reset 的累积和事件边界回溯。

## 12. Tags

`TSAD` `multivariate` `online-detection` `causal-temporal-mask` `channel-clustering` `MLP-Mixer` `empirical-p-value` `sequential-scoring` `event-boundary` `ICML-2026`
