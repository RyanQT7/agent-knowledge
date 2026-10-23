# Knowledge Review v5：TSAD batch 3 — 潜在历史状态、通道分组与动力学证据

## Scope and Evidence Labels

本次 Review 比较第三批三篇全文，并结合此前六篇已读笔记：

- [Graph-MoE](../../papers/graph-moe/notes.md)：多层图专家与 memory-augmented router
- [CCM-TAD](../../papers/ccm-tad/notes.md)：聚类感知多嵌入、时间因果 mixer、顺序异常分数
- [TFC](../../papers/tfc/notes.md)：时间 / 频率 / 曲率的多视角检测
- 上批综述：[Knowledge Review v4](knowledge-review-v4.md)

标记含义：

- **Paper-backed fact**：可由特定论文的章节、公式、表格或附录核对。
- **Cross-paper synthesis**：对多篇机制的归纳比较，不表示作者共同提出了统一定义。
- **Research gap within nine-paper scope**：已读九篇没有充分验证的问题；必须在其余 24 篇读完后再确定是否属于最终全库空白。

## 1. What This Batch Adds

### Paper-backed facts

- **Graph-MoE** 保留多个 GNN 深度的表示，以每层 expert 做 attention 对齐，再通过 MAR 的历史记忆和门控生成层权重。它使用 dynamic attention graph，但图边是模型学得的当前窗口关联，不是显式 service topology 或 Granger 因果图。（§3, Eqs. 5–16; Figs. 2–3）
- **CCM-TAD** 用训练数据 correlation profiles 静态聚类通道、cluster-wise embedding；causal mask 仅限制时间 mixer 的未来信息流。其 p-value / sequential evidence 评分可以只使用当前及过去测试观测，但论文 Best-F1 报告同时在 ground truth 上搜索 $\alpha,h$。（§§3.2–3.4; Appendix F, Eq. 24; Appendix L–M）
- **TFC** 使用中心二阶差分和 Multi-Span Attention 放大曲线弯折 / 多跨度局部变化；频率与曲率先 cross-attend，之后与 temporal embedding 路由融合。（§§2–3.4, Eqs. 7–19）算法按每条 univariate series 分别训练，state-space 动机里的外生驱动 $u_t$ 并未成为模型输入。（Appendix C）
- **TFC** 的中心二阶差分显式使用 $t+1$，Transformer 公式没有说明因果 mask；论文没有声明严格在线能力。**CCM-TAD** 则提供了明确的 future-free 在线评分流程和一项 WADI ADD–false-alarm-period 比较。（TFC Eqs. 12, 17; CCM-TAD Appendix L, Fig. 8）

### Cross-paper synthesis

前三批目前形成六种互不等价的正常性 / 异常证据：

1. CAPMix 的 synthetic anomaly soft label 和 DTW 形态边界；
2. WMMNN 的测试期新正常适应；
3. CAROTS 的跨变量预测 / Granger 关系偏离；
4. CrossAD 的粗到细尺度映射与跨窗原型；
5. MACE 的跨服务静态频谱子空间；
6. Graph-MoE / CCM-TAD / TFC 分别补充潜在历史图层路由、静态通道分组与顺序证据、单变量曲率和周期证据。

因此，“多正常模式”不能作为一个统一机制概括。其状态参照可能是服务身份、在线模型当前分布、跨窗原型、latent memory、静态 channel correlation cluster，或信号内生频带；它们可分别在不同层次工作，也不天然提供业务状态语义。

## 2. Nine-Paper Comparison by Normality Reference

| Method | 主要正常性参照 / 单元 | 时间变化机制 | 跨变量 / 外部上下文 | 主要评价证据 | 关键边界 |
| --- | --- | --- | --- | --- | --- |
| CAPMix | 单训练均值中心、合成窗口形态 | 训练期 CutAddPaste / soft label | 不用 workload / Trace | Best RPA-F1、污染实验 | 多态中心和标签阈值边界 |
| WMMNN | 趋势与预测正常 mask | 测试时 EMA / 在线 SGD | 不使用发布 / 负载语义 | F1 / 点级报警 | 伪标签与在线污染风险 |
| CAROTS | 训练正常期 Granger 预测关系 | CPA / CDA 合成增强；关系相对固定 | 多变量预测关系；外生变量未用 | AUROC、F1 / 消融 | 真实图无真值，WADI 分数项作用不一致 |
| CrossAD | 粗细尺度正常映射、统计原型 | EMA 更新跨窗 prototypes 的边界需核实 | 跨尺度 / 窗口统计上下文 | F1、VUS | 原型不等于业务态，表文指标有差异 |
| Fortifying | 原分类决策在 DTW 半径扰动下的稳定性 | 对抗随机平滑，不是漂移状态更新 | 不用业务变量 | certified radius / coverage | 保证不翻转，不保证原判对 |
| MACE | 按服务 / 子集的常见 Fourier bases | 静态服务条件频率基 | 静态 entity identity | F1、效率、跨组测试 | 对同服务动态负载状态未建模 |
| Graph-MoE | 多层图传播表示与潜在 memory | MAR 随窗口迭代更新 memory | 窗口动态图 attention，不接业务 context | 窗口 AUROC | memory 未命名 / 未做异常写入分析；SWaT split 需注意 |
| CCM-TAD | 训练期相关 profile clusters 与 validation loss reference | 分数顺序累积；cluster / reference 静态 | 静态通道统计，不做 Granger | Best-F1、PR-AUC、VUS、ADD-FAP | causal 仅时间遮罩；Best-F1 对测试标签调参 |
| TFC | 分带频率、中心曲率、temporal embedding | 每窗口特征路由，没有已说明在线更新 | 单变量；不接动机中的 $u_t$ | Best-F1、Event-F1 | score / loss 未明确；中心差分可能前视 |

表中机制均以各单篇笔记对应的 PDF 章节 / 表格为依据。不同论文的数据集、阈值规则、窗口协议不一致，不能把表格中的分数横向当作公平总排名。

## 3. User Questions: Current Evidence

### 多种正常运行状态如何建模？

**Paper-backed facts：** MACE 的 normal subspace 是按服务静态选择；WMMNN 在线跟随新的输入分布；CrossAD 汇聚重复跨窗子序列表示；Graph-MoE 用历史 latent memory 选图层；CCM-TAD 对训练相关 profile 类似的通道共享独立 embedding；CAROTS 用共享因果结构下的多样正例增强。TFC 并不建立状态簇，而是为每条单变量序列加多个信号视角。（MACE §IV-C; WMMNN §§3–4; CrossAD §3.3; Graph-MoE §3; CCM-TAD §3.2; CAROTS §§3–4; TFC §3）

**Cross-paper synthesis：** 这些设计已提出跨服务、跨窗口、按 latent 历史、按通道关系和在线分布变化等不同正常模式表征，不能把“多模式建模”整体视作未研究。当前九篇尚未证明模型可以利用可解释的业务 load / release / autoscaling context，主动识别同一服务的低负载、高峰和发布期等运行状态，并安全处理叠加故障。

### 正常业务波动和真实故障如何区分？

**Paper-backed facts：** TFC 通过曲率 / 频率互补提高机制形变灵敏度，但没有估计外因；Graph-MoE 的 history / graph attention 会影响 likelihood，却没有业务事件语义；CCM-TAD 将连续 reconstruction residual 转为 p-value 并累积段证据；此前方法使用形态、趋势、因果依赖、频率子空间或尺度映射作为统计参照。（对应各 note 的 §§3–6）

**Cross-paper synthesis：** 这些机制能回答“与何种统计或结构规律不一致”，通常无法单独回答“是合法业务高峰、发布改变、指标采样噪声还是故障造成”。输出异常证据结构化，不等于已解释波动来源。

### 现有方法是否仅仅抑制噪声？

不完全是：CAROTS 的预测关系、CrossAD 的尺度映射、MACE 的实体条件频率基、Graph-MoE 的层级图表示、CCM-TAD 的跨通道分组和事件累积、TFC 的二阶几何特征都引入了更结构化的参照。可是只有表示 / 关系的名字并不能替代外部状态真值：已读方法没有形成从 workload / Trace / change event 到告警解释的完整证据链。

### 是否利用 Metric、Trace、业务负载和运行上下文？

**Paper-backed facts：** TFC 即使使用来自 AIOPS / WSD 的 signals，也按单变量序列训练；论文动机中的 $u_t$ 未实现。Graph-MoE 用监测序列构造图，不接 Trace / 业务 topology；CCM-TAD 按训练期 channel correlation profile 聚类；MACE 使用服务标识匹配静态频率子空间。此前六篇同样主要处理指标数据，未见成套 Trace / release / workload 条件化验证。（各 note 的 §4–6）

**Current status: Open。** 九篇尚未提供一个明确使用多源运维上下文并在负载—故障并发矩阵上验证的统一证据；其余 24 篇仍要检查是否有语义 / 多模态路线。

### 如何处理正常负载变化与真实故障并发？

**Research gap within nine-paper scope：** 没有系统受控测试“合法负载或业务周期变化与真实故障同时间发生”。WMMNN 需评估误吸收，MACE / CCM-TAD 有静态正常参照或分组，Graph-MoE 的 memory / router 更新安全性未测，TFC 只有周期频率线索而无外部驱动标注。现有单数据集分数不足以回答该并发问题。

### 哪些技术方向已经被提出？

- Service-conditioned multi-normality：MACE 的静态服务 Fourier subspace；不要笼统称“首次用多正常模式”。
- Online normal adaptation：WMMNN 已明确更新模型以适配新正常；Graph-MoE 的 memory 不等于参数适应。
- 多粒度关系：CrossAD 跨时间分辨率 / 窗口；Graph-MoE 跨 GNN 深度；TFC 跨频带和曲率注意力跨度；三者的 multi-scale 单元不同。
- 因果机制：CAROTS 通过 Granger 结构生成增强；CCM-TAD 的 causal 是防 future leakage；不能混称因果检测。
- 顺序告警：CCM-TAD 已用 validation p-value 统计证据累积及边界回溯；“事件级连贯分数”不是空白，但其 threshold oracle 与无标签部署需拆分。
- 曲率检测：TFC 明确引入二阶差分；未来工作不应把“把二阶差分加入异常分数”当作未经检索的新方向，而应定位到 context conditioning、因果在线性或并发故障评估。

### 哪些研究问题目前缺少充分实验？

- workload / release / deployment 变化和真实故障同步发生时，特异度、召回、事件时延及人力成本。
- 在线参数 / memory / prototype 更新遇到漏报异常时如何检测污染、恢复和回滚。
- 外部状态 context 能否带来跨服务、跨负载、跨组织提升，是否比单纯隐空间路由稳定。
- Best-F1 阈值来自测试标签 sweep 与真正部署前无标签固定阈值的性能差距。
- score 对应的关系 / 曲率证据是否与根因事件、服务拓扑或业务执行记录一致。
- 图动态、相关聚类、频域、曲率的异常机制是否同时有效；各工作多以分别 ablation 为主，没有统一因子控制的组合实验。

## 4. Evidence Issues to Preserve

- Graph-MoE 的 SWaT 文字写明把原测试数据再分为 train / validation / test；与标准严格 held-out 协议的关系要复查。（Graph-MoE p.5, Implementation Details）
- Graph-MoE 主指标为 any-positive window AUROC；不能直接与逐点 Best-F1 / Event-F1 作性能排名。（Graph-MoE p.5）
- CCM-TAD 的在线生成机制不要求未来测试观测，但 Appendix F 的 Best-F1 明确联合 sweep $\alpha,h$ 最大化 ground-truth F1；报告时需标注阈值来源。（CCM-TAD Appendix F Eq. 24; Appendix L）
- CCM-TAD Appendix M 明确其 causality 不涉及 Granger / channel causality；静态 correlation clustering 也不是因果图。（CCM-TAD Appendix M）
- TFC Table 1 与 Table 2 的 TODS 完整模型结果不一致（.9481/.9231 vs .9258/.9155）；Table 1 AIOPS F1 (.9406) 低于 POLY (.9550)，所以平均 / Event-F1 优势不能概括成每格全面胜出。（TFC Tables 1–2）
- TFC 使用中心差分和未说明 causal mask 的 Transformer，也未在 main text / appendices 精确定义 score / loss；复现需查代码，线上推理时的前视与 threshold 需单独核实。（TFC Eqs. 12, 17; Appendix C–D）
- 延续 v4 的证据问题：CrossAD 的 SWAN VUS-ROC / Table 3 文字差异；Fortifying 的分类决策不等于正确性、benchmark row count 与版本标记；MACE held-out group frequency base 来源和 J-D2 ablation；CAPMix / WMMNN / CAROTS 的各自数据与阈值问题均保留在单篇笔记。

## 5. Current Open-Question Status

| Question | Status after nine papers | Evidence-based understanding |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | 已有跨服务频率先验、在线模型更新、跨窗原型、latent memory、相关 profile channel clusters 等路线；未显示可解释 workload state / deployment state 并安全路由。 |
| 正常波动与真实故障如何区分？ | Partially Answered | 统计形态、趋势、关系、尺度、频率、曲率及 sequential evidence 可提高判别；尚无外部业务原因核验。 |
| 是否利用 Metric、Trace、workload 与运行上下文？ | Open | 部分数据来自生产环境，但模型输入仍以时序指标为主；当前尚未见成套 Trace / release / workload condition and test。 |
| 模型是否解释波动来源？ | Partially Answered | 变量 / 图 / 尺度 / 曲率证据丰富了异常分数，却不构成业务根因或事件解释链。 |
| 正常负载与故障并发如何处理？ | Open | 九篇都缺少系统并发测试矩阵；尤其在线更新与静态 / latent normal reference 的污染及安全性。 |
| 哪些方向已由先行方法覆盖？ | Partially Answered | 多态参照、漂移适应、多尺度、因果 TSAD、图关系、曲率和顺序评分已有工作；新颖性要落到具体未覆盖机制及实验证据。 |
| 哪些结果需谨慎外推？ | Partially Answered | 测试标签选阈值、window-level metric、SWaT split、TFC score / future dependence、表格差异和跨数据可比性。 |

## 6. Next Batch Priorities

下一批按“跨通道因果 / 关联与可解释检测”组织，和 CCM-TAD、CAROTS、Graph-MoE 对照：

1. GCAD：Granger-causality perspective；核对其因果图如何学习、异常分数是否关系条件化以及实验真值。
2. Structured Temporal Causality for Interpretable Multivariate TSAD：阅读结构化时间因果和解释输出，并与“temporal causal mask”明确区分。
3. SARAD：空间关联与诊断；检查 anomaly localization / diagnosis 是否具有根因证据，以及动态正常关联如何处理。

以上优先级只是学习安排。全库研究空白要等 33 篇全部完成后再判断。
