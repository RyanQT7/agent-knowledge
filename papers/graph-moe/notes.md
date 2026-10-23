# Graph-MoE：以多层图专家和记忆路由建模多变量时序

## 1. Metadata

- Title: Graph Mixture of Experts and Memory-augmented Routers for Multivariate Time Series Anomaly Detection
- Authors: Xiaoyu Huang, Weidong Chen, Bo Hu, Zhendong Mao
- Year / Venue: 2025 / AAAI
- CCF: A（按已人工确认的清单）
- Official source: [AAAI paper](https://ojs.aaai.org/index.php/AAAI/article/view/33921)
- Code: [Graph-MoE](https://github.com/dearlexie1128/Graph-MoE)
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local PDF: [Graph-MoE PDF](../../sources/papers/tsad-2024-2026/2025/AAAI/Graph_Mixture_of_Experts_and_Memory_augmented_Routers_for_Multivariate_Time_Series_Anomaly_Detection.pdf)

## 2. One-Sentence Summary

Graph-MoE 保留 GNN 各层从近邻到远邻的层级表征，为每层配置一个以当前时序表征为 query 的图专家，再由带门控记忆的路由器依据历史全局特征加权融合，最后作为 GANF / MTGFlow 一类条件归一化流的条件表征进行无监督异常检测。

## 3. Problem Definition and Motivation

论文处理无监督多变量时序异常检测。输入由 $K$ 个实体（论文中的 entity 可理解为传感器 / 指标变量）组成，每个实体有长度为 $L$ 的观测序列；模型在滑动窗口中联合估计实体间依赖，并对窗口给出异常判断。作者指出，普通 GNN 多只使用最后一层输出；堆叠层逐步聚合不同距离的邻域，最后一层虽含更广的图信息，却可能弱化变量自身与局部邻居特征。因此只看最后一层会丢失浅层和中层关系。（PDF pp.1–3, §§1–3）

论文认为不同时间片、实体及关系尺度会偏好不同图深度：部分实体需要局部一跳信息，另一些实体需要更远邻居的全局依赖。固定地把同一层或所有层简单相加难以根据当前状态选择信息来源。方法由此分别处理两个维度：**层内**由 expert 对某一 GNN 层输出进行对齐 / 聚合；**层间**由 router 决定各层 expert 的权重。记忆模块再把当前窗口特征与历史全局特征一起纳入权重生成。（PDF pp.2–5, Fig. 2–3, §§3.1–3.3）

重要边界：标题里的 memory 表示模型隐状态，不是可读的业务状态标签；论文没有输入 workload、Trace、发布或服务事件，也没有声称从 memory 中恢复业务原因。

## 4. Architecture Overview

```text
多变量窗口 x_c
  → 每实体 LSTM / GRU 编码为 H
  → 当前窗口自注意力建动态实体图 A_c
  → 多层时空图卷积：近邻 / 远邻层级表征 H^1 … H^L
  → 每一层一个 global-guided entity-attention expert f_l(H^l | H)
  → MAR 把专家输出与历史记忆 M^{t-1} 融合并更新 M^t
  → R = Softmax(φ_R(M^t)) 产生层权重，C = Σ_l R_l H̄^l
  → 将 C 接入条件 normalizing flow（如 MTGFlow）并以密度 / 负对数似然评分
```

论文主实现以 MTGFlow 为基线。Graph-MoE 是对 GNN-based detector 的扩展 / 插件：flow 负责条件密度估计，Graph-MoE 提供增强的时空条件。作者进一步在 GANF、MTGFlow 和 USD 上给出插接实验。（PDF pp.3–7, §§3–4, Table 4）

## 5. Method in Detail

### 5.1 数据窗口与基础条件流

论文将 $K$ 个实体的观测记为 $x=(x_1,ldots,x_K)$，$x_i\in\mathbb R^L$。每个实体沿时间维做 z-score：

$$\bar{x}_i=\frac{x_i-\operatorname{mean}(x_i)}{\operatorname{std}(x_i)}.\tag{3}$$

再以窗口宽 $T$、步长 $S$ 切片。基础 conditional normalizing flow 通过可逆映射 $z=f_\theta(x\mid C)$ 把输入映到目标分布 $Z$，用 change-of-variables 计算条件密度，并以最大似然训练：

$$\log p_X(x)=\log p_Z(f_\theta(x\mid C))+\log\left|\det\frac{\partial f_\theta(x\mid C)}{\partial x^\top}\right|.\tag{1–2}$$

在此框架下，Graph-MoE 的输出 $C$ 提供条件信息；低密度样本可按负 log-likelihood 视作异常。这里的密度目标来自 flow 基线，本文的新增贡献是图层条件生成 / 聚合，而非新的 anomaly label supervision。（PDF p.3, §3 Preliminaries, Eqs. 1–3）

### 5.2 实体时序编码与逐窗动态关系图

先对每个实体单独运行 RNN：

$$H^t_k=\operatorname{RNN}(x^t_k,H^{t-1}_k),\tag{4}$$

其中作者使用 LSTM 或 GRU，所有实体表征组成初始时序特征 $H$。对于窗口 $c$，两组线性映射形成 query/key 特征，并以实体间点积构造关系：

$$e^c_{ij}=\phi^e_1(x^c_i)\,\phi^e_2(x^c_j)^\top,\qquad a^c_{ij}=\frac{\exp(e^c_{ij})}{\sum_j\exp(e^c_{ij})}.\tag{5–6}$$

得到的注意力矩阵 $A^c$ 作为当前窗口的加权邻接矩阵。它随窗口输入变化，因此这里的动态关系是模型对观测的注意力图，并非从已知 service topology / 业务依赖图读取，也不自动等价于因果图。（PDF pp.3–4, §3 Graph Construction, Eqs. 4–6）

### 5.3 多层时空图卷积与层内专家

第 $l$ 层融合同一时刻邻接聚合与上一时间步历史状态：

$$H^l_t=\operatorname{ReLU}(A^cH^{l-1}_tW_1+H^{l-1}_{t-1}W_2)W_3.\tag{7}$$

窗口内的 $H^l_t$ 沿时间拼接为第 $l$ 层条件 $H^l_c$。堆叠 GNN 层逐渐增加实体关系图中的邻域范围；作者把每层视作拥有不同感受野的专家候选。

对每一层，专家以当前 RNN 时序表示 $H$ 为 query、该层的图条件 $H^l$ 为 key/value 做交叉注意力和 LayerNorm：

$$\widetilde H^l=\operatorname{LN}(\operatorname{Attention}(H,H^l)),\qquad \bar H^l=\phi^l_2(\operatorname{ReLU}(\phi^l_1(\widetilde H^l))).\tag{9–10}$$

这里 attention 在层内把当前实体 / 时间信息与指定 GNN 深度对齐，FFN 再变换为可融合的 expert representation。作者对所有层分别计算，不是简单把最后一层图 embedding 送入异常分数头。（PDF pp.4–5, §3 Graph Mixture of Experts, Eqs. 7–11）

### 5.4 Memory-augmented Router（MAR）

对当前时刻，把各层专家对齐结果拼接为 $\widetilde H^t$。记忆矩阵 $M^{t-1}$ 作为 query，与当前专家结果拼为 key/value：

$$Y=[M^{t-1};\widetilde H^t],\quad Z=\operatorname{Attention}(M^{t-1},Y).\tag{12}$$

残差 MLP 形成候选记忆 $\widetilde M^t=\phi_M(Z+M^{t-1})+Z+M^{t-1}$（Eq. 13）。forget / input 门为：

$$G_f^t=\widetilde H^tW_f+\tanh(M^{t-1})U_f,\quad G_i^t=\widetilde H^tW_i+\tanh(M^{t-1})U_i.\tag{14–15}$$

两门平衡保留的旧记忆和新候选：

$$M^t=\sigma(G_f^t)\odot M^{t-1}+\sigma(G_i^t)\odot\tanh(\widetilde M^t).\tag{16}$$

路由器把更新后的记忆映射到层专家权重 $R=\operatorname{Softmax}(\phi_R(M^t))$；专家融合为：

$$C=\sum_{l=1}^{L}R_l f_l(H^l)=\sum_{l=1}^{L}R_l\bar H^l.\tag{8}$$

设计意图是让 router 按跨时间积累的全局特征动态选择局部 / 长距离图层信息。论文没有把各记忆槽对应到具体负载、业务态或实体语义，也没有展示显式异常隔离门；若记忆更新流经异常窗口，何种训练 / 推理策略防止异常写入需从代码或更多实验确认。（PDF pp.4–5, §3 Memory-augmented Routers, Eqs. 8, 12–16, Fig. 3）

### 5.5 训练与分数

方法按无监督条件密度估计训练，未依赖人工故障标签训练分类器。论文报告使用既有 flow blocks 和 Adam；窗口级检测，窗口只要包含一个时间点异常即视作异常；评价 AUROC。具体的窗口 anomaly score 沿用 flow 的 likelihood 设定，而不是本论文另行推导一个可解释的点级归因分数。（PDF pp.3, 5–6, §§3–4）

## 6. Experimental Evidence

### 6.1 数据、比较对象和实现协议

- **数据集**：SWaT（51 个 sensor）、WADI（123 个 sensor / actuator）、PSM（25 个特征）、MSL（55 维遥测）、SMD（38 维；包含 28 个子集）。（PDF p.5, §4）
- **指标**：AUROC；输入切窗后将点标签归到窗口级，异常窗口定义是其中任一点被标异常。没有 Event-F1 / 在线时延或运维成本主指标。（PDF p.5, §4）
- **实现**：窗口宽 60、stride 10、Adam、80 epochs。SWaT 用单个 flow block、batch 640、lr .005；WADI batch 320、lr .0035；其他数据两层 flow blocks、batch 256、lr .002。（PDF p.5, Implementation Details）
- **协议边界**：论文称 SWaT 的“original testing dataset”又按 60% training、20% validation、20% testing 切分，其他数据用训练 60%、测试 40%。该设置需要明确原始 benchmark 的 train/test 使用边界；按正文措辞，SWaT 测试序列被重新划给训练与验证，会令结果与严格留出测试协议不完全可比。（PDF p.5, Implementation Details）
- **Baselines**：包括 DeepSVDD、DAGMM、ALOCC、DROCC、DeepSAD、USAD、GANF、MTGFlow 等；部分为半监督，需留意监督信息口径。（PDF pp.5–6, §4, Table 1）

### 6.2 主结果

五次随机重复 AUROC 平均值（Table 1）：Graph-MoE 在 SWaT 87.2±1.3、WADI 94.2±0.8、PSM 88.0±0.7、MSL 72.1±1.1、SMD 93.3±5.6；相对 MTGFlow 的数值分别为 84.8、91.9、85.7、67.2、91.3。作者认为多层关系表示与路由改善条件流的判别力。SMD 标准差较大，作者解释为其 28 个子数据集的异质性与逐子集均值。（PDF p.6, Table 1）

这些结果支持在所测数据和协议下的 AUROC 增益，不能单独证明对未知业务负载、新服务态或在线故障污染鲁棒；AUROC 也不揭示固定阈值下的告警率。

### 6.3 消融、可插接性与定性结果

- **图层数 / 专家数**：SWaT、WADI 上 3 层最好；4 层降到 85.6 / 92.6，作者将其归因于过平滑。Table 2 中 1、2、3、4 个 expert 的结果显示 3 个专家为最优（SWaT 87.2、WADI 94.2）。（PDF pp.6–7, Table 2）
- **MoE 与 MAR**：仅基础图模块为 85.5 / 92.2；仅 MAR 为 86.2 / 92.9；仅 MoE 为 86.8 / 93.5；二者并用为 87.2 / 94.2（SWaT / WADI）。结果支持两者各有增益，且 MoE 单项增益更大。（PDF p.7, Table 3）
- **插件实验**：在 SWaT 上 Graph-MoE 将 GANF 79.8→82.6、MTGFlow 84.8→87.2、USD 90.2→92.3 AUROC；支持对这三种 graph-based baseline 的可插接改善，不代表任意 GNN 均无需改造即可收益。（PDF p.7, Table 4）
- **分数可视化**：Fig. 4 显示 Graph-MoE normal score 更集中、与 anomaly score 重叠较少；Fig. 5 显示 SWaT 时间曲线。它们是定性图，不提供类别 / 状态语义解释。（PDF p.7, Figs. 4–5）

## 7. Contributions

1. 不只使用 GNN 最后一层，而把不同 hop / 深度的表示视作专门专家。
2. 以 RNN 时序信息和各图层 cross-attention 形成每层对齐表征。
3. 用逐步更新的记忆结合当前及历史特征生成动态层权重。
4. 在五个多变量基准和三个基模型插接场景中提供 AUROC、组件消融和可视化证据。

## 8. Limitations and Reproduction Value

### 论文写明 / 由实验直接显示

- 没有独立的 Limitations 章节；主要分析图层数和过平滑，没有深入讨论流式部署、安全更新或业务状态解释。（全文 pp.1–9）
- 主指标是窗口级 AUROC；缺少固定运行点、事件级指标、告警延迟和跨状态并发故障评测。（PDF p.5, §4）
- SWaT 的测试集再划分协议需要在复现时澄清；不能与标准严格 held-out test 无条件等同。（PDF p.5, Implementation Details）
- 作者公开了 GitHub 代码，具有复现价值；复现时应核对 z-score 统计范围、异常窗口打标、memory 初始化 / 跨序列重置和 SWaT split 实现。

### 分析推断

- “记忆捕获全局历史”是 latent temporal summary，未证明可区分日夜、高峰、发布、扩缩容等**可命名的动态正常状态**。它更接近历史条件门控，不是带语义的模式库。
- 动态注意力图和 memory router 都可随输入改变，但没有直接建模 Trace / service topology / load context；检测到关联变化不等于解释了波动的业务来源。
- 如果 memory 在测试流持续更新，异常表示进入记忆的影响及其恢复边界是实际部署风险；论文未见专门污染实验，故这是待验证问题，不应写成已证实缺陷。
- 单次窗口内异常与合法负载改变同时出现时，路由是否选择异常掩盖模式并未测试。

## 9. Relationship to Other Papers

- **MACE**：MACE 以服务身份及静态 Fourier normal subspace 区分跨服务正常频谱；Graph-MoE 用动态实体图、多层邻域与潜在历史 memory。两者的“多模式”机制不同，后者没有显式服务级子空间。
- **CAROTS / Cluster-Aware Causal Mixer**：CAROTS 的目标是 Granger 预测依赖 / 因果关系异常；CCM-TAD 的“causal”是时间因果遮罩；Graph-MoE 的自注意力图是动态依赖结构，但并不等价因果发现。
- **CrossAD**：CrossAD 聚合跨分辨率与跨窗口子序列原型；Graph-MoE 聚合图传播深度层级，空间 / 实体关系为主要结构轴。
- **When Model Meets New Normals**：WMMNN 显式测试时更新追踪新分布；Graph-MoE 有历史 memory，但论文没有说明它以在线新正常适应为目标。

## 10. Questions

1. Graph-MoE 的 memory 在一个实体序列、多个窗口及训练 / 测试边界之间如何初始化和重置？异常窗口会否写入？
2. 动态 attention graph 对不同真实运行状态的边权变化是否可重复、可解释，并与外部服务依赖或 Trace 一致？
3. 在严格未见 SWaT test split 与固定阈值 / Event-F1 下，增益是否保持？
4. 异常和正常负载跃迁并发时，路由权重会怎样改变，是否需要外部 workload 作为条件？
5. 各层权重能否形成跨时间稳定的动态状态簇，或仅是任务内部权重？

## 11. Useful Definitions

- **Hierarchical graph representation**：不同 GNN 深度下聚合不同 hop 范围邻居的表征。
- **Graph-MoE expert**：以当前 RNN 时序特征 query 某一图层 key/value 后，经 FFN 对齐的层专属表征。
- **Memory-augmented router (MAR)**：以记忆状态融合当前多层专家输出，并据更新记忆计算各图层权重的门控模块。

## 12. Tags

`TSAD` `multivariate` `dynamic-graph` `GNN` `mixture-of-experts` `memory-router` `conditional-normalizing-flow` `AUROC` `AAAI-2025`
