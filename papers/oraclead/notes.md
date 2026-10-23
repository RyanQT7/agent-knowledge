# Structured Temporal Causality / OracleAD：结构化时间因果多变量时序异常检测

## 1. Metadata

- **Paper title**: Structured Temporal Causality for Interpretable Multivariate Time Series Anomaly Detection
- **Method name**: OracleAD
- **Authors**: Dongchan Cho, Jiho Han, Keumyeong Kang, Minsang Kim, Honggyu Ryu, Namsoon Jung
- **Year / Venue**: 2025 / NeurIPS（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Structured_Temporal_Causality_for_Interpretable_Multivariate_Time_Series_Anomaly_Detection.pdf)
- **Official paper**: [NeurIPS proceedings page](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5565ab682d6c7f8d9da34ba0919974b0-Abstract-Conference.html)
- **Code**: 论文未提供 OracleAD 自身的代码链接；Appendix C.2 列出的是基线实现仓库，不应误认作 OracleAD 实现。（PDF p.19）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

OracleAD 为每个通道独立编码历史并预测下一点，通过跨通道注意力形成上下文嵌入，再以训练期每轮平均的 pairwise latent distance matrix（Stable Latent Structure, SLS）约束结构稳定性；测试时将预测误差与相对 SLS 的结构偏差相乘，实现点级异常检测并以偏差矩阵提供变量定位线索。

## 3. Background and Problem Definition

论文讨论多变量时序中的两类证据：单通道随时间的动态是否异常，以及通道之间的潜在关系是否偏离。作者指出，只按 reconstruction / prediction error 检测可能漏掉原始值变化很小、但变量关系发生变化的异常；联合多变量建模也可能把异质通道的独立动态混在一起，降低局部异常敏感度和可解释性。（PDF pp.3–4, §§2.1–3.1）

令窗口为 $X=[x^1,\dots,x^L]\in\mathbb R^{N\times L}$，其中 $N$ 为变量数、$L$ 为窗口长度。模型用前 $L-1$ 个时刻编码，重构历史并预测最后向量 $x^L$，判断该末时刻是否异常。（PDF p.4, Eqs. 1–2）

题名中的 “causality” 应按论文内部操作定义理解：每通道 LSTM 的历史编码被称为 causal embedding；其后又以跨变量 MHSA 融合相关表示。SLS 实际保存的是对称的潜在嵌入距离，不是有向 Granger 图、干预效应或物理因果图；它也不单独识别故障根因。（PDF pp.4–6, Eqs. 3–12）

## 4. Core Challenges

1. **异质通道的时间规律**：不同变量的基线、周期、响应速度不同，单个共享时序模型可能使其表示相互干扰。作者以独立 encoder–decoder 分支处理每个变量。（PDF p.4, §3.1）
2. **跨变量结构证据**：只有逐通道预测残差可能看不到正常值域中的关联结构变化。OracleAD 把多个变量的 latent embeddings 做 MHSA，并比较其距离结构。（PDF pp.4–6）
3. **结构评分的时序覆盖与局部精度**：单点 prediction score 灵敏但短；关系偏差能在窗口内持续，却有窗口滞后和恢复期残留。乘积融合意在兼顾两者，但会受任一分量偏小的抑制。（PDF pp.9–10, Fig. 2）
4. **评测可信度**：作者明确讨论 point-adjusted F1 等指标的局限；然而其自己的二值 F1 使用依赖测试真值的最优阈值，部署阈值问题仍未解决。（PDF pp.3, 8; Appendix D.3, p.22）

## 5. Architecture Overview

```text
多变量窗口 X（L=10）
  ├─ 每通道独立 LSTM encoder：前 L−1 点 → 隐状态序列
  │    └─ 时间注意力池化 → 每变量 temporal / “causal” embedding c_i
  ├─ 沿通道维堆叠 C → MHSA → 上下文表示 c*_i
  ├─ 每通道 LSTM decoder → 重构历史 + 预测末点
  ├─ pairwise L2 距离矩阵 D_t 与训练期 SLS 比较 → deviation score
  └─ prediction score × deviation score → final anomaly score
```

模块依次解决通道自身的历史摘要、通道间 latent 交互、正常关系参照学习、末点检测及偏差可视化。训练和推理中的 SLS 都在 latent 表征上；它不是输入数据的 Pearson correlation matrix，也不是显式邻接矩阵。（PDF pp.4–7, Fig. 1, §§3.1–3.4）

## 6. Method in Detail

### 6.1 通道级时间编码与注意力池化

对每个变量 $i$，独立 LSTM encoder 接收 $x_i^{1:L-1}$，得到隐状态 $h_i^1,\dots,h_i^{L-1}\in\mathbb R^d$（Eq. 3）。通过线性打分 $f(h_i^\ell)=w^\top h_i^\ell+b$ 和沿时间轴 softmax 得到权重 $\alpha_i^\ell$，再加权汇聚为

$$c_i=\sum_{\ell=1}^{L-1}\alpha_i^\ell h_i^\ell. \tag{5}$$

$\alpha$ 让模型在完整历史窗口中选择对末点预测有用的时间信息；它不是异常分数或经人工标注的因果权重。编码器按通道独立，但结构训练及后续解码并非完全无跨通道信息。（PDF pp.4–5, Eqs. 3–5）

### 6.2 跨变量注意力与双任务解码

将 $c_i$ 堆叠为 $C\in\mathbb R^{N\times d}$，使用多头 self-attention 得到 $C^*=[c_1^*,\dots,c_N^*]$（Eqs. 6–8）。每个变量 embedding 作为 query，同时以所有变量 embedding 构造 key/value；因此 $c_i^*$ 可吸收其他通道线索，论文称其捕获 soft / dynamic dependencies。这里的 attention 是学习到的表示交互，不应直接当成真实因果边。

对应通道 decoder $Dec_i$ 从 $c_i^*$ 输出历史重构 $\hat x_i^{1:L-1}$ 和下一点预测 $\hat x_i^L$（Eq. 9）。Fig. 1 标明 decoder 初始输入为全零向量。把各通道末点拼接成 $\hat x^L$（Eq. 10）。重构分支用于约束潜在表征保留窗口内动态；预测分支提供精确的末点变化证据。（PDF pp.4–5, Fig. 1, Eqs. 6–10）

### 6.3 Stable Latent Structure（SLS）

对训练窗口 $k$ 的上下文 embedding 计算两两欧氏距离：

$$D_{ij}^{(k)}=\|c_i^{*(k)}-c_j^{*(k)}\|_2,\quad D^{(k)}\in\mathbb R^{N\times N}.\tag{11}$$

论文选 L2 距离，并在 Appendix E.4 比较 cosine / L1。每个 epoch 将该 epoch 的 $M$ 个训练窗口距离矩阵取均值：

$$SLS=\frac1M\sum_{k=1}^{M}D^{(k)}.\tag{12}$$

第一轮开始时没有先验 SLS；首个 epoch 结束后建立，第二轮起作为训练结构正则项。训练中它约束变量间距离接近累计的正常结构；推理时直接用训练得到的 SLS，不在测试过程中动态更新。（PDF pp.5–6, §3.2, Eqs. 11–13）

这是一种全局平均 latent-distance 模板。多种合法正常机制若映射到不同 latent geometry，简单均值可能削弱状态间区别；训练期模型还可能把污染或罕见正常纳入均值。论文没有按 workload / operating mode 建立多模板，也没有外部事件变量来命名各结构。

### 6.4 Training objective

每轮得到当前 batch/window 的结构距离 $D^{(k)}$，用 prediction loss、历史 reconstruction loss 与当前距离对 SLS 的 deviation regularizer 联合优化：

$$L=L_{pred}+\lambda_{recon}L_{recon}+\lambda_{dev}L_{dev}.\tag{14}$$

其中 prediction 与 reconstruction 项为相应平方 $L_2$ 误差；结构项为当前 pairwise distance 与 SLS 的均方偏差。默认 $\lambda_{recon}=0.1$、$\lambda_{dev}=3$（PDF §3.3, Appendix D.2）。首个 epoch 尚无稳定模板，SLS 约束从第二轮起应用。训练仅用 normal training data；标准化参数由训练集 StandardScaler 拟合。（PDF p.6; Appendix C.1, p.19; Appendix D.1, p.20）

### 6.5 Inference score and localization

对时刻 $t$ 的末点定义预测误差：

$$P_t^{score}=\frac1N\sum_{i=1}^{N}|x_i^t-\hat x_i^t|.\tag{15}$$

当前窗口内 latent pairwise distance 为 $D_t$，结构偏差分数为

$$D_t^{score}=\|D_t-SLS\|_F.\tag{16}$$

最终检测分数为

$$A_t^{score}=P_t^{score}\times D_t^{score}.\tag{17}$$

prediction score 使单点突变显著；deviation score 可能在异常进入窗口后延迟升高，并在输入窗口仍含异常恢复样本时继续偏高。作者认为乘积可以压低“结构偏差高但预测误差低”的误报，并以结构偏差补充 prediction-only 漏报；但乘积也意味着任何一个分量接近零都会压低总分，效果取决于数据集及两分量标定。（PDF pp.7, 9–10, §§3.4, 4.3, Fig. 2）

用于解释时，作者展示矩阵 $D_t^{matrix}=|D_t-SLS|$，聚合行 / 列异常强度以对变量排序。Fig. 3 的热图帮助检查 SMD 案例；Appendix G 的 Table S10 对部分代表性异常时间报告 top-3 变量与标注变量的比较。此处是候选变量定位，不等于由模型验证的物理根因；SWaT / PSM 没有同等完备的 forensic feature ground truth。（PDF pp.8–9, Fig. 3; Appendix G, pp.29–30）

## 7. Experimental Design and Evidence

### 7.1 Datasets, baselines, metrics

- **Datasets**：PSM（25 variables）、SMD（38）、SWaT（51）；SMD 按机器划分子集，报告 subset-average。（PDF p.7, §4.1; Appendix A）
- **训练协议**：只用 normal train split；输入以训练集 StandardScaler 标准化；没有单独 validation set；window length $L=10$，测试序列前 $L-1$ 个点不计入评价；五个随机种子均值。（PDF p.7; Appendix C.1, p.19; Appendix D, p.20）
- **Baselines**：AE、OmniAnomaly、Anomaly Transformer、PatchTST、TimesNet、DLinear、NLinear、DCdetector、iTransformer、ModernTCN、SARAD、CATCH。（PDF p.7, §4.1）
- **Metrics**：point-wise F1、R-F1、Aff-F1、AUC-ROC、AUC-PR、VUS-ROC、VUS-PR。AUC / VUS 不依赖选定单一阈值；F1 系列则受阈值策略影响。（PDF p.7, §4.1）
- **Threshold caveat**：Appendix D.3 根据目标评价指标对给定候选阈值集最大化 F1 等分数，使用对应 ground-truth $y$；具体候选阈值为 score range 上 $N=200$ 等分。故表中二值 F1 属测试标签 oracle threshold 结果，不能视作部署前无标签阈值性能；AUROC / AUPRC / VUS 指标不受该二值门限选择影响。（PDF p.22, Appendix D.3）

### 7.2 Main results

Table 1 报告 OracleAD 主要值如下（%，五 seed 平均）：

| Dataset | F1 | R-F1 | Aff-F1 | AUC-ROC | AUC-PR | VUS-ROC | VUS-PR |
|---|---:|---:|---:|---:|---:|---:|---:|
| PSM | 65.85 | 54.66 | 78.07 | 84.78 | 68.11 | 84.24 | 68.17 |
| SMD | 43.03 | 38.88 | 84.73 | 83.56 | 44.83 | 69.57 | 47.52 |
| SWaT | 76.50 | 28.15 | 71.97 | 82.71 | 72.39 | 82.42 | 74.16 |

（PDF p.8, Table 1）

作者称大部分指标最优，并强调 VUS-PR。表中并非每个指标均第一：例如 SWaT VUS-ROC 的 SARAD 为 86.30，高于 OracleAD 82.42；SWaT R-F1 的 OmniAnomaly 38.72 高于 28.15。OracleAD 在多项 threshold-independent 指标有竞争力，但不能将其结果概括为所有指标均全面领先。论文也指出 Aff-F1 在若干弱模型上仍偏高，需结合定位更严格的指标解读。（PDF p.8, Table 1, §4.2）

### 7.3 Ablations and qualitative analysis

Table 2 中去掉 reconstruction loss 后，PSM 的 F1 / VUS-ROC / VUS-PR 从 full 的 65.85 / 84.24 / 68.17 降到 58.03 / 74.56 / 54.40；该表 SMD 的 no-reconstruction 行为 56.47 / 75.59 / 54.29，full 行为 60.19 / 80.81 / 56.63；SWaT no-reconstruction 为 76.61 / 82.92 / 71.95，full 为 76.50 / 82.42 / 74.16。（PDF pp.8–10, Tables 1–2）需要注意，Table 1 的 SMD full 行为 43.03 / 69.57 / 47.52，而 Table 2 标注 SMD 为四个子集均值，二者报告口径不一致；不应直接用不同表格计算 ablation 差值，复现时需核对 subset protocol。

- 仅用 deviation score 在 SWaT 的 F1 76.92 高于 full 76.50，但 PSM/SMD 有明显差距；单独使用 prediction score 也在不同指标 / 数据集各有强弱。Full model 并非逐格最优，作者的论证是双分数总体更平衡。（PDF pp.9–10, Table 2）
- 可视化显示短促 prediction 峰和持续 deviation 段覆盖不同异常时相；结构偏差出现窗口延迟及恢复期残留，是方法可观察的时序代价。（PDF pp.9–10, Fig. 2）
- SMD Table S10 展示多个代表性区间 top-3 排名；仅覆盖少量精选案例，且不构成全测试集的 root-cause accuracy。（Appendix G, pp.29–30）
- Appendix E 给出种子标准差，Appendix D 给出窗口长度、batch size、$\lambda_{dev}$、encoder/decoder 深度敏感性；默认 batch=1024、$\lambda_{dev}=3$、encoder/decoder 两层。窗口 10 / 20 多数表现稳定，过大窗口可能稀释局部异常。（Appendix D.2, pp.20–21）

## 8. Contributions and Reproduction Value

### Technical contributions

1. 将每通道历史摘要与跨变量 latent self-attention 结合，避免静态输入关系图先验。（PDF §§3.1–3.2）
2. 建立训练期更新的平均 pairwise latent-distance template SLS，并将其作为结构正则项及推理异常参照。（PDF §3.2, Eqs. 11–13）
3. 组合点级 prediction error 与窗口级 structural deviation，提供互补分数与可视化候选变量排名。（PDF §3.4, Eqs. 15–17; §4.3）
4. 对 PSM、SMD、SWaT 报告多种点级 / 区间 / 阈值独立指标、消融和敏感性结果。（PDF §4; Appendices D–G）

### Reproduction value and boundaries

- **Positive**：损失、默认窗口长度、阈值候选数、标准化、随机种子及多项敏感性在论文和附录中给出；评测指标多于单一 F1。（PDF §4; Appendices C–E）
- **Missing**：没有发现 OracleAD 自身公开代码链接；基线仓库不能替代模型实现。需要自行核对 SLS 每轮聚合的精确数据遍历、批量距离实现、测试窗口的 score 对齐和候选变量排序细节。
- **Metric distinction**：测试标签用于选二值分数阈值的 F1 结果存在乐观偏差；重现应另报无监督选出的部署门限与 threshold-independent metrics。
- **Protocol detail**：主表与 ablation 对 SMD 报告口径出现不同 subset-average 结果，复现和横向比较应明确表、子集与聚合方法。

## 9. Limitations

### 作者明确指出

作者在 Appendix I 指出，SLS 假设连续值输入下存在全局稳定的变量关系；异构子系统或混合连续 / 离散传感器（如 SWaT）可能削弱偏差矩阵的区分能力。未来工作包括变量类型无关方法与推理时动态更新 SLS。（PDF p.31, Appendix I）

### 论文实验支持的限制

- deviation score 需要异常先进入长度 $L$ 的窗口，因而有 detection lag；窗口包含异常恢复历史时可在恢复期产生 false positive。（PDF pp.9–10）
- 诊断案例量有限，SMD 是代表性变量定位分析；注意力与 latent distance 不足以证明根因因果。（PDF p.8, Fig. 3; Appendix G）
- SMD Table 1 / Table 2 的点值结果来自不同报告口径，不能从不同表格直接对比 ablation 变化。（PDF pp.8–10）
- F1 最优阈值基于测试真值选出；部署时阈值如何在无标签条件下定标并未回答。（Appendix D.3）

### 本知识库的分析推断

- 全局固定 SLS 对动态负载、发布、扩缩容切换的合法结构变化可能报高分；论文提出动态 SLS future work，但未将业务上下文作为条件变量，也没有测其与故障并发时的安全更新策略。
- SLS 的对称 latent distance 与 MHSA 依赖提供结构偏离提示，但它既没有方向性也不验证干预关系；用 “root cause” 需限定为候选变量排序。
- 乘积融合抑制单侧误差也可能压制单模态有效信号：若关系异常时预测误差很小，或正常关系偶然变化时预测分数较小，偏差证据可能被压低；该风险宜通过可控合成实验检验。
- 若正常状态呈多模态分布，单一均值距离矩阵会丢失模式条件；可比较状态条件 SLS / 多模板、在线变点门控与固定模板，并控制异常污染。

## 10. Related Papers

- **GCAD**：都比较测试期结构证据与正常结构参照；GCAD 是从逐目标预测误差梯度导出的有向 Granger predictive influence 图，OracleAD 是对称的 MHSA latent pairwise distance。两者不能统称为同一种 causal graph。
- **CAROTS**：按估计 Granger 图构造因果保持 / 破坏增强及预测分数；OracleAD 的 attention latent relation 不承担图真值或干预语义。
- **SARAD**：从 attention map 的空间关联下降及其时间 progression 检测，显式解释通道贡献；OracleAD 检测 latent distance template 偏移。两者均使用关系证据，但所观察对象、聚合方式和 anomaly score 不同。
- **CCM-TAD**：其 “causal” 指时间 mixer 的 future mask；OracleAD 则以历史编码和下一点预测建模时间依赖，再对通道 latent 距离建模结构。
- **Graph-MoE**：Graph-MoE 用图卷积层级表示与 memory router；OracleAD 的 SLS 是全局 pairwise distance baseline，而非历史状态路由器。
- **When Model Meets New Normals**：后者推理期适应新 normal；OracleAD 推理时冻结 SLS，动态结构更新仅列为 future work。

## 11. Questions for Further Reading

1. 如果负载、发布或控制阶段切换产生合法新关系，何种证据允许建立新 SLS，而不将同期故障吸收为新正常？
2. 多模态合法运行状态是否需要 mixture / state-conditioned SLS，而不是每 epoch 单一矩阵平均？
3. 结构偏差矩阵与 service topology、Trace、故障注入因果真值之间的一致性如何量化？
4. 只有 structural deviation 或只有 prediction error 的场景下，乘积是否会系统性抑制真异常；是否需要带校准的加和或门控融合？
5. Appendix D.3 用 ground truth 选择阈值的结果，与独立 validation 或在线无标签阈值结果差多少？
6. 在事件级检测中，SLS 造成的窗口延迟 / 恢复拖尾如何权衡检出延迟与误报段长度？

## 12. Key Terms

- **Causal embedding（作者用语）**：每个通道由 LSTM 历史隐状态注意力池化得到的向量；不是对变量间真实干预因果的估计。
- **Stable Latent Structure (SLS)**：训练期各窗口跨变量 latent L2 距离矩阵的 epoch 级均值。
- **Deviation matrix**：当前窗口 pairwise latent distance 与 SLS 的绝对偏差矩阵。
- **Dual score**：prediction error 与 SLS deviation Frobenius norm 的乘积。

## 13. Tags

`TSAD` `multivariate` `latent-structure` `LSTM` `MHSA` `stable-latent-structure` `prediction-error` `NeurIPS-2025`
