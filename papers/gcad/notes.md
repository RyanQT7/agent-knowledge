# GCAD：从 Granger 因果模式变化检测多变量时序异常

## 1. Metadata

- Title: GCAD: Anomaly Detection in Multivariate Time Series from the Perspective of Granger Causality
- Authors: Zehao Liu, Mengzhou Gao, Pengfei Jiao
- Year / Venue: 2025 / AAAI
- CCF: A（按已人工确认清单）
- Official source: [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/34096)
- Local PDF: [GCAD PDF](../../sources/papers/tsad-2024-2026/2025/AAAI/GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf)
- Code: 正文未给出 GCAD 专属代码仓库链接；六个 baseline 的公开实现用于对照。（PDF pp.5–6）
- Knowledge Card: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

GCAD 用一个预测型 Mixer 作为梯度生成器，对每个目标通道的预测误差分别回传到各输入通道历史窗口，以预测损失梯度幅值近似动态非线性 Granger 影响，再消除对称相似性并与训练正常窗口的平均因果图比较，得到关系偏离与自时序偏离分数。

## 3. Background and Task

GCAD 研究多变量传感器时序异常检测。作者的核心动机是，常见动态图 / GNN detector 虽构图，但通常仍以 prediction / reconstruction error 告警，不能直接说明变量关系怎样影响演化。作者提出：某变量异常时，除值 / 预测误差变化外，跨变量 Granger 依赖模式也可能偏离正常参考；例如进水压力提升时出水压力原应同步变化，若管路泄漏，既有预测关系可能被破坏。（PDF pp.1–3, §§1–2）

输入按最大滞后 $\tau$ 滑动成多变量窗口。模型最终对每个窗口输出 abnormality 判断 / score。方法未用 Trace、service topology、业务负载或事件语义；其“因果”是基于可预测性的 Granger operational definition，不等于结构因果模型、干预效应或物理根因自动识别。（PDF pp.2–4, §3）

## 4. Architecture Overview

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

## 5. Method in Detail

### 5.1 Prediction-based Gradient Generator

一个窗口的历史输入 $X_{t-1}=\{x_{t-\tau},\ldots,x_{t-1}\}\in\mathbb R^{N\times\tau}$，预测当前向量 $\hat y_t=f(X_{t-1})$。GCAD 用 $L$ 层 Mixer predictor；每层交替 temporal mixing MLP 和 feature mixing MLP，前者跨时间混合，后者跨变量混合，skip connections 后经 fully-connected layer 输出各通道当前点预测。训练只用 MSE：

$$L_{train}=\operatorname{MSE}(\hat y_t,y_t).$$

为区分不同目标变量的误差来源，定义目标通道 $j$ 的独立平方预测误差：

$$L_{t,j}=(\hat y_{t,j}-y_{t,j})^2.\tag{1}$$

对每个 $L_{t,j}$ 反传，可得其对每个输入通道 $i$、滞后时刻 $\phi$ 的梯度；合并为 $G_t\in\mathbb R^{N\times N\times\tau}$。这样 $G_{t, i,j,\phi}$ 描述改变输入变量 $i$ 的过去值时，目标 $j$ 的预测误差在当前预测器局部如何变化。（PDF pp.3–4, §3, Eq. 1, Fig. 1）

### 5.2 用 loss 梯度量化非线性 Granger 影响

原始 Granger 关系定义为：若替换变量 $i$ 的过去历史会改变变量 $j$ 的预测 $f_j$，则 $i$ Granger-causes $j$（Definition 1, Eq. 2）。作者在输入点附近引入扰动 $x^*_{t',i}=x_{t',i}+\Delta$（Eq. 3），并以小扰动下预测误差变化的局部导数近似：

$$\lim_{\Delta\to0}|L_{t,j}-L^*_{t,j}|=\left|\frac{\partial L_{t,j}}{\partial x_{t',i}}\right||\Delta|.\tag{4}$$

从最大 lag 中汇聚绝对梯度，并对兴趣输入分布 $P$ 积分，形成因果权重：

$$a_{i,j}=\int_{t-\tau}^{t-1}\left|\frac{\partial L_{t,j}}{\partial x_{\phi,i}}\right|P(x_{\phi,i})\,dx_{\phi,i}.\tag{5}$$

所有 $a_{i,j}$ 组成窗口关系矩阵 $A$。作者指出 predictor 可微，因此局部梯度可计算；简化下 $P$ 可取 uniform。实际要特别区分：论文把预测误差的输入梯度作为 Granger causality proxy。它衡量局部 predictive sensitivity，梯度会随 predictor 拟合、输入位置、误差残差而变；不等同于真实系统因果图的观测或干预验证。（PDF pp.4–5, §3 Granger Causality Discovery, Eqs. 2–5）

### 5.3 Causality Graph Sparsification

作者认为 cosine 等对称相似性常会在 $A_{ij}$ 和 $A_{ji}$ 两方向同时出现，而有向 Granger 关系不应对称；据此定义：

$$\tilde A_{i,j}=\max(0,A_{i,j}-A^\top_{i,j}),\quad i\ne j;\qquad \tilde A_{i,i}=A_{i,i}.\tag{6}$$

再对小于稀疏阈值 $h$ 的项置零。该差分去除对称共性并保留净方向性，阈值过滤小权重噪声。它不能保证所得图是 DAG；论文明确说非线性图难以严格保证无环。对角线保留，表示变量自身历史对自身预测误差的敏感度。（PDF p.5, §3 Causality Graph Sparsification, Eq. 6）

### 5.4 Normal causal template and anomaly score

预测器训练后，从 normal training windows 按 Bernoulli 参数 $p$ 抽样，计算稀疏图 $\tilde A_{norm,i}$，均值作为总体正常关系模板：

$$A_{norm}=\frac1n\sum_{i=1}^{n}\tilde A_{norm,i}.\tag{7–8}$$

对每个测试窗口计算 $\tilde A_{test,i}$（Eq. 9）。关系偏差定义为逐项相对偏差求和：

$$S^c_i=\sum\frac{|\tilde A_{test,i}-A_{norm}|}{|A_{norm}|+\epsilon}.\tag{10}$$

作者进一步取对角元素偏差形成 time-pattern score $S^t_i$（Eq. 11），然后合并：

$$S_i=S^c_i+\beta S^t_i.\tag{12}$$

由于 $S^c$ 本身已包含主对角，$\beta=0$ 时仍有自历史模式信息；$\beta$ 是对额外 diag emphasis 的超参数。分数的参照是训练所有 normal windows 的平均因果图，因而是一个静态、全局正常模板；论文没有展示先按业务态聚类或条件化再比较。（PDF pp.5–6, §§3 Causal Deviation Scoring, Eqs. 7–12）

## 6. Experiments

### 6.1 Data, metrics, baseline protocol

- **Datasets**：SWaT、SMD、MSL、SMAP、PSM 五个真实世界 benchmark。Table 1 记录 channel / train / test / anomaly ratio，例如 SWaT 51 / 47,520 / 44,991 / 12.20%，SMD 38 / 28,479 / 28,479 / 9.46%，PSM 25 / 132,481 / 87,841 / 27.76%。（PDF p.5, Table 1）
- Table 1 的 SWaT / SMD 窗口点数与标准全量数据集通常引用规模不同；需核对其预处理、单实体切分或降采样实现。论文在正文表中未逐项写明为何采用这些长度，不应直接把这些行当作原始全量规模。（PDF p.5, Table 1）
- **Baselines**：DAGMM、USAD、GDN、Anomaly Transformer、GANF、MEMTO 六种。（PDF p.5, §Experimental Setup）
- **训练 / 验证**：normal unlabeled data 的 80% 用于训练，20% 验证；含标签异常数据作为测试。报告 AUROC / AUPRC，10 次实验求均值。（PDF pp.5–6, Implementation Details）
- 不报告点级 F1 / threshold selection / Event-F1 或线上 false alarm period；AUPRC 能部分应对异常不平衡，但仍是离线 benchmark 排序指标。（PDF p.5）

### 6.2 Main results

Table 2 的 AUROC / AUPRC（模型：ROC / PR）：

| Dataset | GCAD AUROC | GCAD AUPRC | 表内比较边界 |
| --- | ---: | ---: | --- |
| SWaT | .8690 | .7758 | 两项均高于所列对照 |
| SMD | .9533 | .7502 | 两项均高于所列对照 |
| MSL | .7658 | .3679 | 两项均高于表内结果，异常率很低 |
| SMAP | .7273 | .4555 | ROC 高；PR 略低于 GANF .5259 |
| PSM | .7618 | .6136 | 表内高于列出的 baseline |

作者总结大多数指标 / 数据集达最佳；但 SMAP AUPRC 是 GANF .5259 高于 GCAD .4555。MSL / SMAP 异常率分别仅 .74% / 2.14%，PR 值低，需谨慎解释排序成绩。（PDF pp.5–6, Tables 1–2）

### 6.3 Ablations and graph example

- **去掉 sparsification**：SWaT ROC / PR .8690/.7758→.8559/.7676；SMD .9533/.7502→.9531/.6915，说明稀疏化对 PR / noise reduction 有帮助，但 SMD AUROC 变化很小。（PDF p.6, Table 3）
- **去掉因果关系 GC**：SWaT .8478/.7513，SMD .9405/.6424，特别是 SMD AUPRC 大降；支持关系结构比预测误差单项有增益。（Table 3）
- **去掉时间对角 TC**：SWaT .8400/.7558，SMD .9498/.6748；作者据此指出非对角因果依赖与自历史偏差互补。（Table 3）
- **Lag $\tau$ 与 threshold $h$**：Fig. 2 显示二者有非单调权衡：lag 太短只见近邻关系，lag 长可捕获复杂影响但对短异常不敏感；$h$ 太低引入噪声边，太高丢掉弱但有用的因果信息。（PDF p.6, Fig. 2）
- **案例**：SWaT 化学泵 P203/P205 被关停后，AIT202 / AIT501、FIT301 / FIT503 的因果偏差图变化；矩阵与物理系统文字描述具有对应关系，帮助解释分数。（PDF p.7, Figs. 3–5）但这是一个 case study，不是系统性故障变量 localization 定量基准。

## 7. Contributions

1. 利用可微 nonlinear predictor 的 channel-specific error gradients 形成按窗口变化的 Granger influence estimate。
2. 用 $(A-A^T)_+$ 去除对称相似性，再做幅值稀疏化。
3. 用正常窗口平均图为参照，同时评分跨变量有向关系变化和对角自时序变化。
4. 在五个真实数据集给 AUROC / AUPRC、去组件 ablation、lag / threshold 敏感性和一个 SWaT 物理系统案例。

## 8. Limitations and Reproduction Value

### 作者明确说明

- **只建模变量对变量的 binary causal pairs**，不能直接表示多变量组合因果关系；Conclusion 将此列为限制与 future work。（PDF p.7）
- 论文解释 Granger causality 是预测可提升关系，不是完整物理因果。Sparsification 不保证 DAG。（PDF pp.4–5）

### 实验 / 证据边界

- $A_{norm}$ 是训练 normal windows 的均值单模板，没有条件化负载、时段、控制阶段或服务版本。合法多模态状态切换导致因果图变化时也可能升高异常分数；论文未用已知业务态做对照。
- 梯度对预测误差求导是模型局部敏感度；它受预测器是否学好、loss 残差和输入分布影响。论文没有通过真实 cause graph ground truth 测量边识别准确率，也没有比较 intervention / operator logs。
- threshold-independent AUROC / AUPRC 提供 score 排序证据，但没有固定 FPR 下报警数、事件时延、diagnosis precision 或成本；仅 SWaT 定性案例说明物理关系。
- Table 1 中部分 train/test 样本数显著小于标准公开数据常用规模；复现应确认其拆分 / 重采样流程及 Table 2 是否基于完全相同 pipeline。
- 正文未报告代码仓库，且训练细节较简略；重现需确认 $P$ 近似、梯度积分数值实现、Bernoulli 样本数、threshold $h$ / $\beta$ 搜索、滑窗标签回填以及起点 / 末端的 graph 计算。

### 分析推断

- 如果正常业务负载改变了预测依赖（例如开关服务 / 控制回路）但仍符合合法操作，单一 $A_{norm}$ 无法自动区分“新正常机制”与故障关系破坏。
- 分数表示因果预测结构偏离，可作为定位线索；从预测依赖直接称为实际根因还需要物理图 / 操作记录验证。
- 当前定义逐变量两两评分；多故障共同改变预测关系时可能表现为若干 pair 边差异，无法表示高阶协同机制，作者对此限制有所承认。

## 9. Relationship to Other Papers

- **CAROTS**：同属 Granger / causal prediction relation TSAD。GCAD 直接由 predictor 的 loss gradient 构造窗口图并比较模板；CAROTS 以估计 Granger 图设计 causal-preserving / causal-disturbing augmentation 与预测异常分数。两者都未将业务 context / Trace 作为正常变化条件。
- **CCM-TAD**：其 causal temporal mask 只限制 future leakage；GCAD 才尝试估计跨变量 Granger predictive dependency。不能混为同类因果主张。
- **Graph-MoE**：窗口 attention graph 与层级路由用于条件 density；GCAD 用窗口因果图相对正常图偏差作为检测 score。
- **OracleAD / Structured Temporal Causality**：OracleAD 将每变量历史预测表示经 MHSA 转到 latent space，再比较 pairwise distance SLS；结构可解释但不是显式 Granger graph。
- **SARAD**：检测 attention association下降与空间 progression；它衡量 feature reconstruction association shift，不声称变量间 causality。

## 10. Questions

1. 如果一个正常业务阶段切换改变 $A$，如何判定这是合法上下文条件而非 causal anomaly？
2. loss-gradient 是否等价于对预测输出 $\hat y_j$ 做 Granger sensitivity？训练残差接近零时是否会低估真实预测依赖？
3. 正常模板用均值会否把多个合法图结构平均成不存在的“中间图”，并把两个正常状态都判异常？
4. 如何用有向 ground-truth topology / intervention / 控制流程日志验证因果边，而不只用 detection AUROC？
5. 高阶交互和多个变量共同故障如何表示；正常负载改变与故障并发时的 graph update / scoring 如何校准？
6. 使用 Table 1 所列样本长度复现时，数据子采样 / channel split / label windowing 的确切脚本在哪里？

## 11. Useful Definitions

- **Gradient-derived Granger influence**：目标 $j$ 的预测误差对输入通道 $i$ 历史值的局部梯度，经滞后和输入分布汇聚得到的窗口权重 $a_{i,j}$。
- **Graph sparsification**：减去关系矩阵转置的非负部分，保留方向差异，再用阈值 $h$ 删弱边。
- **Causal deviation score**：测试因果图相对训练期平均因果图的归一化逐边偏差总量，另加可调自时序偏差。

## 12. Tags

`TSAD` `multivariate` `Granger-causality` `gradient-sensitivity` `dynamic-causal-graph` `normal-graph-template` `causal-deviation` `AAAI-2025`
