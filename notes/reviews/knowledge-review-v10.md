# Knowledge Review v10：TSAD batch 8 — 视觉全局核验、相对上下文 foundation model 与 open-set influence

## Scope and Evidence Labels

本次覆盖第 22–24 篇，累计 **24/33** 篇实际 PDF 精读：

- [Harnessing Vision-Language Models for TSAD](../../papers/vlm4ts/notes.md)：ViT4TS 跨窗视觉 proposal + GPT-4o global verification。
- [TimeRCD](../../papers/time-rcd/notes.md)：context-dependent synthetic pretraining + Relative Context Discrepancy。
- [IMPACT](../../papers/impact/notes.md)：few-shot open-set supervision + influence-guided contamination / pseudo anomaly handling。

本 Review 区分**作者主张**、**实验直接支持**、**分析推断**。数据、task definition 和 metric 不同，不按表格数字给三篇做简单总排名。

## 1. 方法与监督设定对照

| Paper | normality reference | training / labels | detection mechanism | evidence boundary |
| --- | --- | --- | --- | --- |
| VLM4TS (AAAI 2026) | 同序列其它 windows 的 CLIP patch embedding；VLM 再看整序列走势 | 不训练目标 TSAD；CLIP / GPT-4o zero-shot | 多尺度 patch nearest-match difference → interval proposals → LLM contextual filtering | 11 个 benchmark 的 univariate contextual F1-max；异常密集 Yahoo A3/A4 下稀有性假设会降低 recall；真实业务 metadata 未输入 |
| TimeRCD (ICML 2026) | 当前 inference series 内长程 temporal / cross-variate relationships | 仅 2.5B synthetic points 预训练；根因 / lag descendants 有合成 token labels | anomaly head 直接预测 contextual relational discrepancy；reconstruction 是 train scaffold | 16 数据、4 metrics、固定 context=5k；专门 contextual split 由同框架 synthetic generator 生成；较密 anomaly 可能污染 context |
| IMPACT (ICML 2026) | validation-risk influence + helpful normal reference embeddings | 每个异常类 10 个 labeled examples；nominal pool 注入 2% contamination | influence sign 翻标可疑污染；risk direction 扰动 features；seen / unseen heads + reference distance | open-set general / hard settings、8 datasets、AUC 五次运行；training contamination 从 test anomalies 抽取并排除最终 test，仍依赖 validation signal |

三者解决的是不同层次的问题：VLM4TS 把视觉模型放在局部 candidate verifier；TimeRCD 学通用 context-relative detector；IMPACT 学有 seen anomaly supervision 时如何整理训练样本并推广到 unseen classes。它们不能统称为无监督“context-aware TSAD”。

## 2. 三篇的直接实验支持

### 2.1 VLM4TS

- **[实验支持]** ViT4TS 平均 F1-max 0.612，VLM4TS 0.659，LSTM-DT 0.529；VLM4TS 在 11 datasets 中 9 个领先。（Table 1, p.6）
- **[实验支持]** 较 TAMA 提高 13.3%；表中约 1,212 tokens、14.68 秒 / series；作者宣称较 naive rolling-window prompting 平均 token 用量低约 36×。（Table 2; §3.2）
- **[失败证据]** Yahoo A3/A4 密集 synthetic anomalies 中，VLM4TS F1-max 0.497 / 0.474，低于 ViT4TS 的 0.614 / 0.565；作者指出“异常稀少”的策略在高密度下偏保守。（§4; Appendix D.4）
- **[消融支持]** 全序列 VLM 单阶段无法替代局部 patch screening；A3/A4 将窗口缩至 28 后 F1-max 升至 0.906 / 0.844，但这不是默认 224 点结果。（Table 3; Appendix D.4）

### 2.2 TimeRCD

- **[实验支持]** 64 个零样本 dataset-metric case 中 38 次第一、14 次第二；对 dataset-specific full-shot baselines 是 35 次第一、3 次第二。（Table 1）
- **[实验支持]** 专门 contextual anomaly test Standard-F1 = 0.827，领先 zero-shot competitors；该测试集是 pretraining 未见但仍由相同合成框架生成。（§3.3; Appendix E.2）
- **[消融支持]** UCR 上联合训练、anomaly-head inference VUS-PR 33.57；把 inference 改回 reconstruction error 得 4.08。说明“训练期重建”和“重建分数作为异常判据”应区分。（Appendix E.5）
- **[限制证据]** 长 context 长度最优值随 dataset 而变；作者报告异常频繁的 Stock 样本可能被吸收为 context pattern。MovingVar 在若干数据 / 指标仍有竞争力。（§3.2–3.3; Appendix E.3）

### 2.3 IMPACT

- **[实验支持]** general-setting AUC 八数据分别为 UCR 59.21、ASD 65.76、PSM 64.24、SMD 75.97、CT 91.96、SAD 68.13、PTBXL 66.99、TUSZ 82.91；hard-setting CT / SAD / PTBXL / TUSZ mean 为 81.90 / 66.19 / 62.48 / 75.70。（Tables 1–2, pp.7–8）
- **[消融支持]** 去掉 unseen loss 后 hard TUSZ 75.70→60.92；用 random feature perturbation 后为 62.87。支持其 influence-guided unseen feature objective 在该 protocol 下有贡献。（Table 3, p.9）
- **[稳健性支持]** 2%–10% controlled contamination 下相对稳定；但污染由原 test anomaly 抽出并排除最终 test，所以是受控模拟，不等同任意真实污染分布。（Appendix E, H.3）
- **[作者指出的局限]** rare normal subpopulation 可能被判成 anomaly，作者提出 group-aware validation / subpopulation discovery 作为方向。（Appendix I, p.28）

## 3. 多种正常状态与正常业务波动

### 多种正常运行状态如何建模？

- **VLM4TS** 比较同一序列不同窗口的视觉相似 patch，并在全局图中提供整体走势；它能够用序列内频繁图形作参照，但未把图形分别命名成低负载、扩容、发布等业务状态。
- **TimeRCD** 让相同 shape 在 synthetic corpus 的不同 context 下有不同 normality labels，并通过长程 self-attention 得到序列条件参照。这是三篇中最显式的“局部形态 × 当前上下文”建模；但生成的是时序结构上下文，而不是有语义的服务运行状态模型。
- **IMPACT** 通过 influence-selected normals 和 reference embedding 表示有助于 validation risk 的 normal 样本。它同时明确暴露 group fairness 风险：少数合法 normal subpopulation 可能因 rare / dissimilar 被认为有害。

**[跨论文推断]** 已有多模板 prototype / memory（AnomalyLLM、CrossAD、Graph-MoE）、谱模式（MACE）、test-time update（When Model Meets New Normals）、序列内上下文（TimeRCD）、visual reference（VLM4TS）和 influence-selected normal reference（IMPACT）。因此“建立不止一个 normal reference”本身不是空白；更窄的待证问题是怎样将这些参照映射到可审计运行状态，且在状态切换时不把并发故障纳入新 normal。证据来源分别见对应 notes 与 Reviews v3、v4、v9、v10。

### 正常业务波动和真实故障如何区分？

- **已有机制**：VLM4TS 用全序列曲线拒绝和长程走势不一致的局部候选；TimeRCD 判断 pattern 是否违背序列 context；IMPACT 把对 validation risk 有害的 nominal samples 翻标；Delving 使用自然语言背景做模拟 context filtering；CAPMix / WMMNN 分别关注动态 KPI 与新正常。
- **证据限制**：VLM4TS 的 context 是线图；TimeRCD context labels 来自合成 generator；IMPACT 的 “harmful” 是对 validation objective 的影响，不等价于故障语义。现有结果都不能独立证明波动由正常 workload 变化或故障导致。
- **并发状态变化与故障**：三篇均未做受控“仅 workload/state change、仅 fault、二者同时、未见合法 state”矩阵。TimeRCD 有 context-violating anomaly 和跨变量 synthetic causal propagation，但没有真实业务状态/故障并发的因果对照；这可作为可复用的合成测试起点，而非已经解决并发问题的证据。

## 4. 噪声抑制、解释与数据来源

- VLM4TS 的视觉 proposal + VLM 全局 verify 能提升 benchmark interval F1，但置信度与 rationale 未独立 calibration / fidelity 核验。
- TimeRCD 的 anomaly head 对 relational discrepancy 输出分数；它摆脱重建误差，并不自然给出可读“为何业务波动”的解释。
- IMPACT 的 influence 解释样本对 validation risk 的作用；latent pseudo anomaly 不还原成 waveform 或真实故障 cause。
- **[综合推断]** 三篇提供了比平滑更丰富的 detection evidence（visual recurrence、context relation、risk influence），但“检测依据来自什么”与“业务波动的成因是什么”仍需区分。Metric 是输入；Trace、release、workload 与外部事件没有被这三篇系统纳入训练 / 测试对照。文本 rationale、attention / influence map 也不自动等于来源归因。

## 5. 方法演进与和已有论文的关系

1. **从候选视觉匹配到全局复核**：VLM4TS 将 CLIP 用作 same-series cross-window patch reference，再把昂贵 VLM 调用压缩为全局核验；与 AnomSeer 同属视觉曲线输入，但一个偏 zero-shot candidate verification，另一个用 GT-derived statistical trace 做 MLLM RL。
2. **从 global normality 到 context-relative labels**：TimeRCD 将“同一形状可在不同上下文异标签”写进 synthetic training objective，较单纯扩大形态 augmentation 更直接；与 When Model Meets New Normals 的 test-time adaptation、MACE 的服务条件谱模板、CrossAD 的 cross-window association 属不同机制。
3. **从 anomaly augmentation 到风险驱动样本选择**：IMPACT 以 validation influence 将 contamination correction 与 unseen pseudo anomaly generation 统一；与 DRA / MOSAD / InvAD / WSAD-DT 的 open-set 目标相邻，但监督前提更明确；与 Fortifying Time Series 不同，后者提供输入扰动 robustness / DTW certificate，而 IMPACT 针对训练池污染和未见类泛化。
4. **重建目标的区分**：TimeRCD 支持 reconstruction 可作为辅助表征目标，但 reconstruction error 并非其 detector score；与 TFMAE、Sub-Adjacent 等依赖多视图 / 结构残差的机制比较时需分清训练 pretext 与 inference score。

## 6. 有论文依据的研究空白

以下为已读 24 篇范围内的证据缺口，不外推为全领域优先权结论：

1. **状态语义与序列 context 的对齐**：TimeRCD、VLM4TS、CrossAD、memory / spectrum / adaptation 方法都提供不同 normal references，但未统一展示由 workload / release / business event 命名、选择和更新这些状态的可靠机制。需要同 service 多状态的真实或可审计上下文标签。（TimeRCD §2; VLM4TS §3; WMMNN / MACE / CrossAD notes）
2. **并发状态变化 / 故障的安全性**：既有 synthetic contextual / causal anomaly 可以生成测试样例，但未充分控制外部负载变化与真实故障同时发生；动态 context 可能吸收异常，或保守筛选会漏掉密集 / 未见故障。（TimeRCD §3.3; VLM4TS §4; IMPACT Appendix I）
3. **rare normal group robustness**：IMPACT 明确指出 rare normal group 会被 misidentify；多 prototype / memory 是否保护此类群体、如何在 group-wise false alarm 下校准，缺少同协议比较。（IMPACT Appendix I; AnomalyLLM / CrossAD / Graph-MoE notes）
4. **上下文核验的未知故障召回**：VLM4TS 的 VLM confirmation、Delving 的自然语言 context filter 可能降低假阳性，也可能过滤未解释的真实故障；目前缺少已知正常活动、未知故障、二者并发的召回代价实验。（VLM4TS §3.2; Delving §5.2）
5. **synthetic generalization 的独立验证**：TimeRCD 的训练和 contextual test 均由其 generator family 生成；IMPACT 的污染及 unseen 类实验也来自固定 benchmark sampling。需 generator-held-out、独立 real-world service、真实故障注入与正常状态变化共同验证。（TimeRCD Appendix B/E.2; IMPACT Appendix E/H）
6. **固定操作运行点**：VLM4TS 主要 F1-max，TimeRCD 报多指标但主表固定 context，IMPACT 主表 AUC；尚需共享 fixed false-alarm budget、validation-only calibration、event delay、审核队列与推理成本的跨方法对照。（各论文 §§4 / 3.1 / 4.1）
7. **证据 / 解释的来源忠实性**：视觉 rationale、RCD relation score、influence score各自提供可追踪线索，但没有统一用 Trace、topology、故障注入真因或专家盲审验证来源解释是否忠实。（三篇 notes）

## 7. TSAD 问题进度（当前 24 篇范围）

| 研究问题 | 状态 | 24 篇范围内的当前认识 |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | prototypes、memory、频谱、online adaptation、same-series visual / relational context、validation-selected reference 已出现；状态语义与安全更新仍不充分。 |
| 正常业务波动和真实故障如何区分？ | Partially Answered | 模式差异、序列相对上下文、文本 filtering、因果结构和 risk influence 都有机制；无真实状态 + fault concurrency matrix。 |
| 是否只抑制噪声 / 是否解释来源？ | Partially Answered | 已有 relational / visual / influence evidence，但不等于 workload、release、Trace 或 physical cause attribution。 |
| 是否用 Metric、Trace、workload、release？ | Open | 大多以指标序列为输入；Delving 有小规模模拟文字 context；没有系统的真实 Trace / release-conditioned TSAD comparison。 |
| 正常负载变化与故障同时发生时怎样处理？ | Open | 24 篇无受控端到端并发矩阵；RCD context contamination、LLM false-negative、rare-normal misclassification 是可检验风险。 |
| 哪些机制已经提出？ | Partially Answered | cross-window prototypes、context-relative synthetic pretraining、open-set influence decontamination、VLM verification、memory / spectrum / test-time adaptation 均已有实现。 |
| 哪些实验不足？ | Partially Answered | generator-held-out、真实 context safety、group robustness、explanation fidelity、validation-only calibration 和 fixed alert budget 仍缺证据。 |

## 8. 下一批阅读（第 25–27 篇）

按“模型架构与重建表征”分组：

1. **KAN-AD: Time Series Anomaly Detection with Kolmogorov-Arnold Networks**（ICML 2025）
2. **RTdetector: Deep Transformer Networks for Time Series Anomaly Detection Based on Reconstruction Trend**（IJCAI 2025）
3. **Multivariate Time Series Anomaly Detection with Idempotent Reconstruction**（NeurIPS 2025）

比较 KAN 表达形式、reconstruction trend 与 idempotent reconstruction 对 normality / reconstruction score 的不同假设，并继续核对损失、阈值及 benchmark protocol。
