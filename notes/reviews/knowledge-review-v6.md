# Knowledge Review v6：TSAD batch 4 — 三种关系变化证据与因果边界

## Scope and Evidence Labels

本次完成的三篇论文：

- [GCAD](../../papers/gcad/notes.md)：梯度派生 Granger predictive-influence 图与正常图偏差。
- [Structured Temporal Causality / OracleAD](../../papers/oraclead/notes.md)：预测分数与 Stable Latent Structure（SLS）距离偏差。
- [SARAD](../../papers/sarad/notes.md)：MHSA association reduction progression 的重建残差。

综述同时参考首三批九篇完整精读笔记。总范围为 12/33；以下研究空白均表示“在已读 12 篇中未得到充分验证”，不是对整个 TSAD 文献的绝对新颖性结论。

- **Paper-backed fact**：论文正文或附录的定义、实验、作者限制，可按页码 / 公式 / 表复核。
- **Cross-paper synthesis**：基于不同论文机制的并列归纳，不表示论文作者提出了共同分类。
- **Research gap in 12-paper scope**：已读范围的证据缺口，后续 21 篇仍可能已有直接工作。
- **Analysis inference**：从方法假设推导的风险或研究建议，须通过新实验检验。

## 1. What the Fourth Batch Adds

### 1.1 Paper-backed facts

- **GCAD** 对 Mixer 的每个目标通道预测误差分别反传到输入通道历史，以梯度绝对值近似窗口级非线性 Granger influence；再以 $\max(0,A-A^T)$ 去除对称共性并稀疏化，最后与训练期平均正常图比较。（§3, Eqs. 1–12, PDF pp.3–6）作者明确承认仅有 pairwise binary relationships，不能表达高阶交互。（Conclusion, p.7）
- **OracleAD** 每变量 LSTM 编码历史，沿变量维用 MHSA 融合；SLS 是训练期窗口 pairwise latent L2 距离矩阵的 epoch 均值。推理 score 为点级预测误差乘以 SLS deviation Frobenius norm。（§§3.1–3.4, Eqs. 3–17, PDF pp.4–7）作者将结构 deviation 用作变量定位线索，但论文 SLS 是对称 latent distance，不是有向因果图。
- **SARAD** 将窗口切成两半，比较 Transformer 对两半得到的 feature association map，取 $ReLU(A_1-A_2)$ 并做最终层 column sum；progression MLP 重建该量，joint score 是 validation-normalized data residual 与 progression residual 之和。（§§3.2–3.4, Eqs. 1–6, PDF pp.5–7）主文诊断公式仍是逐变量 data reconstruction error（Eq. 6）。
- 这三篇均用关系 / 结构线索增强 anomaly evidence，但被度量对象不同：预测损失敏感度、潜在向量距离、attention 重建依赖变化。将它们统一称为“因果检测”会丢失关键语义差别。
- 三篇都没有用 workload、release、Trace 或明确 operating-state labels 来解释 relation change。GCAD 和 OracleAD 使用全局训练期正常参考；SARAD 以训练正常 progression autoencoder 表示可接受的 association descent。（对应各论文 §§3–4）

### 1.2 Cross-paper synthesis

| Method | 结构证据实际含义 | 正常性参照 | 与其他关系方法的差别 | 直接观察到的边界 |
|---|---|---|---|---|
| GCAD | 目标 prediction loss 对历史输入通道的梯度敏感度；Granger predictive proxy | 稀疏图的训练正常均值 | 唯一显式有向 pairwise predictive-influence 图 | 没有图真值 / intervention 核验；高阶交互缺失；模板不按运行态条件化 |
| OracleAD | MHSA contextual embedding 间对称 L2 距离 | epoch 平均 SLS；推理固定 | 不估计方向边；用点级预测×结构偏差 | 结构分数有滑窗延迟和恢复期拖尾；F1 用测试 oracle threshold |
| SARAD | 前后半窗 MHSA 重建 association 的非负下降 | progression autoencoder 对正常下降的重建能力 | 关注变化方向 / progression，而非静态全局图偏差 | 半窗会稀释短异常；空间复杂度随 channel 数二次增长 |
| CAROTS | 估计 Granger 图上的因果保持 / 破坏增强与预测分数 | 因果结构 + 多视图正常对比 | 结构主要用于训练增强、因果 forecast / score ensemble | 静态图在机制切换下的可靠性和真实图语义待验证 |
| Graph-MoE | 窗口 attention graph 及不同 GNN 深度表示 | latent memory-conditioned expert routing | 图主要服务表示和密度路由，不直接等同 Granger causal edge | memory 生命周期与异常写入 / 工作负载语义未验证 |
| CCM-TAD | 训练期 channel correlation profiles | 静态聚类 embedding + 顺序 p-value score | “causal”是时间 future mask，不是 channel causality | cluster 不随业务态变化；Best-F1 有测试标签联合搜索 |
| CrossAD | 粗细尺度重构映射与跨窗子序列原型 | 多尺度模式 / prototype context | 关系对象是时间分辨率与窗口，不是因果通道图 | 原型对业务状态的语义与测试期更新边界待核实 |
| MACE | 按服务构造的常见 Fourier basis 子空间 | 静态服务条件频率 normality | 关系并非 channel graph；服务身份是静态 context | 同一服务的动态负载状态未细分 |
| WMMNN | 当前趋势与预测正常 mask | 推理期新正常模型适配 | 适应 distribution shift，不生成结构原因解释 | 伪正常更新可被漏检故障污染 |
| TFC | 时间、频率与二阶曲率几何证据 | 信号内部 pattern / frequency cues | 解释波形变化线索，不识别业务波动来源 | 外生 workload 未用；在线未来点 / 阈值机制不明 |

各论文的完整配置与证据页码见链接笔记。分数、阈值、数据拆分和标签方案不同，表中不构成模型排名。

## 2. Twelve-Paper Synthesis Around the Research Questions

### 多种正常运行状态如何建模？

**Paper-backed facts：** 已读方法覆盖多个层次，但“多模式”具体含义不相同：MACE 用服务身份选择静态 frequency basis；WMMNN 在测试阶段在线适应新正常；CrossAD 汇聚跨窗多尺度原型；Graph-MoE 用潜在 memory 路由图层专家；CAROTS 用共享因果关系约束的多样正常增强；OracleAD 建立全局单一 SLS；GCAD 建立全局平均因果图；SARAD 学习可重建的 association progression。（各论文对应 §3–4；本综述表格链接到单篇 notes）

**Cross-paper synthesis：** “已有多模式方法”不等于“已识别业务状态”。已有机制分别将服务、窗口、历史潜向量、测试时适应或频谱表示用作正常参考，但 12 篇中没有充分显示用可解释 workload / release / autoscaling / business context 命名同一实体的多种正常状态，并在状态切换时保持故障敏感度。

**Current status：Partially Answered。** 已有统计模式、潜在模式和在线适应机制；状态语义与受控切换证据仍缺。

### 正常业务波动与真实故障如何区分？

**Paper-backed facts：** CAPMix 用形态扰动产生 pseudo anomaly；WMMNN 适应 drift / new normal；CAROTS 将 Granger-preserving 与 causality-disturbing augmentations 分开；CrossAD 比较跨尺度关系；MACE 使用服务频谱先验；GCAD / OracleAD / SARAD 分别加入 predictive, latent, attention-association 结构证据；TFC 组合频率与曲率；CCM-TAD 用顺序误差证据增强区间检测。它们提供的是不同统计异常线索，不同于外部业务事件真值。（单篇 notes §§2–6）

**Analysis inference：** 若高峰、发布、扩缩容和故障都造成可观测依赖变化，仅凭误差或 latent / attention 关系偏差无法确定变化来源。WMMNN 的自适应可能吸收漏检故障；GCAD / OracleAD 的静态结构 reference 可能把合法切换报警；SARAD 的 progression 正常性只取决于训练数据中是否见过该变化。

**Current status：Partially Answered。** 已有统计区分线索，但 12 篇没有系统构造“正常状态变化 × 故障是否同时发生”的受控测试矩阵并报告事件召回、误报、延迟和运行成本。

### 现有方法是否只是抑制噪声，是否解释波动来源？

**Paper-backed facts：** 结构化方法确实不止噪声抑制：CAROTS 以变量预测关系、CrossAD 以尺度映射、GCAD 以预测依赖图、OracleAD 以 latent pairwise structure、SARAD 以 association progression、Graph-MoE 以动态图和 memory、TFC 以曲率—频率交互构造额外证据。

**Boundary：** 这些表示能让“哪里或哪类统计结构偏离”更可见，但 12 篇没有形成由业务变更事件 / workload 到指标波动再到经过外部拓扑或 trace 核验的完整原因解释链。GCAD 的 Granger proxy、OracleAD 的“causal embedding”、SARAD 的 attention association 都不能在没有验证时称为物理根因。

**Current status：Partially Answered。** 有结构化证据；波动来源归因未得到充分验证。

### 是否使用 Metric、Trace、业务负载与运行上下文？

**Paper-backed facts：** 这批 GCAD、OracleAD、SARAD 都以时序窗口建模；首三批也以时序数据、服务身份、latent memory 或统计关系为主。MACE 用静态服务身份作为选择基的条件，不能等同于动态业务负载 / release / Trace。当前已读范围没有见到将 metric、Trace、业务负载和部署事件统一建模，并通过真实业务状态标签验证其增益的工作。

**Current status：Open within the 12-paper scope。** 后续 21 篇，尤其 LLM / multimodal / foundation-model 工作仍需检查其文本或多视图输入是否真正引入运行上下文，而非只把数值序列转换成其他表示。

### 如何处理正常负载变化与真实故障并发？

**Research gap within 12-paper scope：** 没有系统化的并发测试。WMMNN、prototype、memory、SLS 或 normal-template 方法的更新 / 固定策略均需要专门压力测试；静态 reference 的偏离可能同时包括状态切换和故障信号。

**Required evidence：** 控制 workload / release / service scale，独立注入已知故障，至少覆盖“仅状态变化、仅故障、二者并发、未见合法状态”四格；报告事件级检测率、误报时长、延迟、根因排序、适应污染率与回滚成功率。该实验设计是本综述建议，不是已读论文中的实验证据。

### 哪些思路已经提出，不能再被笼统视作新空白？

- **多种 normal reference**：MACE 的跨服务频谱基、CrossAD 的跨窗 prototype、CAROTS 的多样因果保持正样本、Graph-MoE latent memory，已提供不同形式；需把创新落在状态条件语义、可验证迁移或并发故障鲁棒性。
- **在线新正常**：WMMNN 已明确测试时适应；“首次考虑 normal drift”不成立。需要比较安全准入、污染检测、回滚和状态确认机制。
- **跨变量结构证据**：CAROTS、GCAD、OracleAD、SARAD 已从 causal augmentation、梯度 Granger proxy、latent distance 和 attention association progression 等不同对象切入；新工作需明确关系定义与 external validation。
- **多尺度 / 多视角**：CrossAD 跨时间分辨率、Graph-MoE 跨 GNN depth、TFC 跨 temporal / frequency / curvature、SARAD 窗口两半 progression 已存在，机制单位不可混为同一种多尺度。
- **鲁棒性与异常增强**：CAPMix 合成形态异常，Fortifying 认证 DTW 扰动下决策不翻转；两者解决 threat model 不同，不等于业务状态漂移鲁棒性。
- **事件级和顺序评估**：CCM-TAD 使用 sequential evidence 与边界校正；CAROTS / TFC 等报告事件相关指标，但需分别核对阈值和在线延迟。事件级评价本身并非空白，部署可用运行点证据仍不足。

### 哪些实验结论或问题缺少充分验证？

1. 负载 / 发布变化与故障并发、未知合法状态迁移和跨实体迁移的控制评测。
2. detector 产生的 causal / association / latent relation 是否与真实 topology、Trace、故障注入 root cause 一致。
3. 在线参数、prototype、memory、normal graph / SLS 更新如何识别漏报污染、隔离异常与回滚。
4. 用测试标签搜索 Best-F1 的结果与仅用正常 validation / 无标签固定门限部署的差距；报告实际误报周期和事件延迟。
5. 对多种异常持续时间、状态切换位置、故障并发时，分数窗口化、回填和前视需求是否一致；统一区间协议的跨论文对照不足。
6. 高维场景中的 attention / graph 成本、稀疏 label 的 diagnosis 准确率与真实运维收益。
7. 各文论文中差异性的样本子集、test split 与表格口径：例如 GCAD 的 Table 1 点数需要确认预处理；OracleAD 主表与 ablation 的 SMD 汇总口径不一致；TFC 表间 TODS 结果不同。这些需逐篇复核，不应直接横向排名。

## 3. Evidence Issues and Cautions

- **关系名称不能替代关系语义**：GCAD 的 Granger 量是预测 loss 局部 sensitivity proxy；OracleAD 的 SLS 是对称 latent distance；SARAD 的关联图是 MHSA reconstruction map。因果、结构相关与 attention dependence 应分别表述。（GCAD Eqs. 2–6; OracleAD Eqs. 11–17; SARAD Eqs. 2–6）
- **正常参照粒度不同**：固定全局均值、静态服务子空间、训练 prototype、在线更新、history memory 与验证集统计 score normalization 不是同一机制。须记录参照是否静态、是否条件化、是否在测试中更新、是否可能被异常写入。
- **评分数字不是统一竞赛**：数据集预处理、实体拆分、窗口 / label backfill、point adjustment、range metric 和阈值来源不同。应先核对协议，再比较方向，不直接拼成一张总排名。
- **诊断结果受标签语义控制**：attack-source labels 不一定覆盖全部异常变量；attention / latent heatmap 可以提供候选解释，不是可靠 root-cause ground truth 的替代品。
- **静态/动态 context 边界**：把指标数据来自生产环境、或输入为多通道，不代表模型使用运行上下文。需要具体列明算法的真实输入及标签。

## 4. Next Reading Batch

下批 13–15 将按“评测可信度与协议 + 频域重建”主题阅读：

1. **Position: Quo Vadis, Unsupervised Time Series Anomaly Detection?** — 对近期 TSAD 方法、评测和研究方向的立场讨论。（2024 ICML）
2. **The Elephant in the Room: Towards A Reliable Time-Series Anomaly Detection Benchmark** — 基准可靠性、任务定义和评测协议。（2024 NeurIPS）
3. **Temporal-Frequency Masked Autoencoders for Time Series Anomaly Detection** — 与 MACE / TFC 的频域正常性证据进行方法对照。（2024 ICDE）

本批精读需区分立场论文的论据与 benchmark 的实证，特别核对异常区间标注、阈值选择和 metric 对方法排序的影响。完成 15/33 后再由下一次 Review 根据全文证据调整后续主题。
