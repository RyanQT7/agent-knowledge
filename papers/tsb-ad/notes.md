# The Elephant in the Room: Towards A Reliable Time-Series Anomaly Detection Benchmark

## 1. Metadata

- **Authors**: Qinghua Liu, John Paparrizos
- **Year / Venue**: 2024 / NeurIPS Datasets and Benchmarks Track（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/NeurIPS/The_Elephant_in_the_Room_Towards_A_Reliable_Time_Series_Anomaly_Detection_Benchmark.pdf)
- **Proceedings**: [NeurIPS 2024 paper page](https://proceedings.neurips.cc/paper_files/paper/2024/hash/c3f3c690b7a99fba16d0efd35cb83b2c-Abstract-Datasets_and_Benchmarks_Track.html)
- **Code and benchmark**: [TSB-AD](https://github.com/TheDatumOrg/TSB-AD)（论文 p.1）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

TSB-AD 将数据集筛查与人工复核、多类异常检测器辅助的标签检查、十种 point/range 评价指标以及统一调参结合，发布 1,070 条来自 40 个数据集的单变量和多变量序列，并用基准实验展示：数据质量、指标和调参协议都会影响 TSAD 的方法排序，复杂神经网络并非在所有设置下占优。

## 3. Background and Problem Definition

作者把 TSAD 领域的问题归为三组：公开数据可能含误标、run-to-failure 偏差或不现实的异常密度；逐点指标忽略时间区间结构，point adjustment（PA）又可能奖励噪声分数；不同论文使用的数据、预处理、检测器和调参预算不同，导致结果难以复核或横向比较。（§1, pp.1–3）

TSB-AD 的目标不是提出新的 detector，而是提供统一基准：较大且经过筛查的序列集合、涵盖传统统计 / 数据挖掘、神经网络和 foundation model 的 detector，以及适用于 point 与 interval anomaly 的评测指标。作者把数据集标记分为 TSB-AD-U（univariate）和 TSB-AD-M（multivariate）。终稿包含 870 条 UTS、200 条 MTS，共 1,070 条、40 个来源数据集；U 子集含 23 个来源，M 子集含 17 个来源。（Abstract, §4.1, Table 2 / Fig. 3, pp.1, 5–6, 19）

## 4. Core Challenges

1. **Ground truth 并不天然可靠**：以“每条序列只含一个异常”为目标会排除其他真实异常，也可能引入截断或遗漏；run-to-failure 序列中时间位置与故障严重度相关，容易让模型利用时间趋势而非故障特征。（§3.1, pp.3–4）
2. **类别不平衡及序列结构影响指标**：AUC-ROC 在大量 true negatives 下可能显得很高；standard F1 把各时间点独立计算，对轻微 detection lag 敏感；PA-F1 对区间任一点命中后整段回填，会放大随机或嘈杂 score 的效果。（§3.2, pp.4–5, Fig. 2）
3. **benchmark protocol 造成额外偏差**：方法未在相同数据集运行、预处理不统一、只在单个合成集调参，或仅因运行时间限制而删去方法，都可能影响比较。（§1, §2.2, pp.2–3）
4. **算法表现与 anomaly type 有关**：point anomaly、sequence anomaly、单一 / 多个异常及异常比例不同，可能分别偏好不同方法；全数据集均值掩盖了这种条件性。（§5.2.3, pp.9–10; Appendix D.2）

## 5. Benchmark Construction and Label Curation

### 5.1 收集范围与构建路径

TSB-AD 汇集先前 benchmark 与不同应用领域的数据。构建概览见 Fig. 3（p.5）；附录 B.1 的 Table 2 列出来源集合及数量（PDF p.19）。一些 UTS 是从 MTS 的单一 channel 派生出来的，因此“1,070 条序列”不等于 1,070 个完全独立的原始采集过程。作者另外对 UCR、YAHOO 和 WSD 的大集合抽样，以避免少数来源在整体评价中占过高权重。（§4.1.1; Appendix B.1, pp.5–6, 19）

### 5.2 人工感知与算法辅助标签检查

论文将人工 perception 和 detector-based algorithm test 组合，而不是把单个 detector 的输出来当作真值。Fig. 4（p.6）给出流程；§4.1 与 Appendix B.2 描述了迭代判定：

1. 对已有异常标签运行多种 detector，检查是否至少一个模型能在标签范围内定位异常，并在某个阈值下避免明显的 false positive / false negative。
2. 若算法没有成功定位，先放宽为至多两个 false negatives 与两个 false positives，再检查 detector 标记区域是否靠近已有标签；若接近，适当扩展标签以减少边界偏差。
3. 若仍无法可靠识别，检查相似模式是否在其他位置重复出现；若出现，则可能表示标签质量差并排除该序列；若未出现，则结合上下文判断它是难检测异常还是上下文不足。
4. 由四位有经验的标注人员跨构建环节检查数据并形成共识；明显误标、不完整或缺少上下文的序列被修订、分段或排除。

这套流程是“人工 + 算法辅助的 curated benchmark”，不表示每个 anomaly 都具有可观测的物理根因或完全客观标签。算法可检测性参与筛查，因此需留意潜在的可检测性选择偏差；这是阅读者对流程的风险分析，不是作者证明的偏差结论。（§4.1.2, pp.5–6; Appendix B.2）

## 6. Metrics and Evaluation Protocol

### 6.1 十种指标

TSB-AD 统一实现十项评价指标（§4.3, pp.7–9）：

- **Point-based**：AUC-ROC、AUC-PR、standard F1、PA-F1。
- **Range-aware / event-aware**：Event-F1、R-based-F1、Affiliation-F1、VUS-ROC、VUS-PR、PATE。

指标的容忍区间、事件奖励、前后边界权重等设定不同，不能把指标名称都看作同一事件级目标。论文用合成场景分析滞后敏感度及对随机 score 的偏好（Figs. 5–6, pp.7–8）。作者认为 VUS-PR 在其设计的情境中表现较稳健，并建议作为有用的主要比较指标；这不是对所有任务都成立的数学保证。PATE 提供另一种可调的事件评价，但计算复杂度较高。（§4.3, §5.2.1, pp.7–9）

### 6.2 超参数调优与比较范围

- 对每个 dataset 留出 15% 的 time series 用于 hyperparameter tuning，余下序列用于评估；算法配置搜索依据原论文或公开实现设计。搜索涉及 450 余种算法变体。（§4.2, pp.6–7; Appendix B.3）
- 主结果涵盖 40 类检测算法：Table 1 按统计方法、神经网络和 foundation models 分组（p.2）；具体算法和搜索空间见 Tables 3–4 / Appendix C。个别 UTS 方法通过滑窗将算法改造成 subsequence 版本。（Appendix C）
- Benchmark 的主评估使用固定随机种子；附录 checklist 指出随机 baseline 运行五次。单次主实验不足以描述训练随机性与排名的稳定区间。（Appendix checklist, p.17）

因此，15% tuning protocol 的前提是 benchmark 提供相应可用序列；它不等价于无标签部署条件，也不代表每篇已有研究原本遵循相同切分。对每条论文结果仍应检查其适用的数据拆分和 tuning protocol。（§4.2）

## 7. Experimental Evidence

### 7.1 指标可靠性

Fig. 5 以构造的异常 score 场景对比指标对时滞、区间命中及噪声的反应；Fig. 6 量化 lag robustness 与 random-score bias（pp.7–8）。结果显示 standard point metrics 对短时 lag 会改变结果；PA-F1 可将 interval 内单点命中扩张为全段命中。作者据此推荐重点报告 VUS-PR，并搭配多指标观察，而不是只报 PA-F1。（§5.2.1, pp.8–9）

### 7.2 Benchmark 上的 detector 排序

- **TSB-AD-U**：主分析 32 个算法、23 个来源 dataset。补充 Table 5 / Fig. 11 显示 Sub-PCA 的平均 VUS-PR 排名最高；CD diagram 中 Sub-POLY 的平均名次最高，两种汇总口径并不完全相同。（Appendix D.1, pp.9–10, 28）
- **TSB-AD-M**：CNN 类方法表现突出。没有任何算法在所有 dataset 上稳定第一；有的方法在部分序列较强，在另一些序列上会失败。（§5.2.2; Appendix D.1, pp.9–10, 28）
- **按异常类型拆分**：TimesFM / Chronos 在 point anomalies 上较强；POLY、Sub-PCA、Series2Graph 等统计方法在 sequence anomalies 上表现较好；单异常和多异常场景的相对表现也有变化。（§5.2.3; Appendix D.2, p.28）
- **按数据类型观察**：统计方法在部分 UTS 上强，CNN / OmniAnomaly 等神经模型在部分 MTS 上有竞争力。PA-F1 下 neural methods 的分数常进一步上升，作者将其作为该指标偏差的例证，而不能简单解读为模型在真实区间定位上的提升。（§5.2.2; Appendix D.1）

### 7.3 Foundation model contamination 案例

作者比较 MOMENT 在 TSB-AD 与其专门评估集 MOMENT-Eval 上的表现，观察到在专门评估集上的性能明显下降；对 MOMENT fine-tuning 与 zero-shot 变体的 pairwise comparison 显示 fine-tuning 可减小分布差异。（Appendix D.3–D.4, pp.28–29）这是一个数据污染风险案例，不能据此量化所有 foundation model 的污染程度。

本文研究对象是数据集、指标和 benchmark protocol，不是包含可拆分网络模块的单一 detector；因此没有传统意义上的 detector component ablation。其对应实验分析是 synthetic score / lag / random-score 指标测试、异常类型子集比较、detector 排名及 MOMENT-Eval 污染案例（§§4–5; Appendix D）。

## 8. Technical Contributions and Reproduction Value

1. 提供 40 个来源数据集、1,070 条 curated UTS/MTS 序列，既覆盖人工筛选也包含算法辅助审查。（Abstract; §4.1）
2. 集成十种指标并以 synthetic score 对指标滞后和随机偏差做受控分析。（§4.3; §5.2.1）
3. 在统一软件接口下调参并比较统计、神经和 foundation-model detectors；提供数据、算法和指标实现及更新计划。（§4.2; §5; [TSB-AD repository](https://github.com/TheDatumOrg/TSB-AD)）
4. 结果提示复杂模型收益依数据集、异常类型和指标而变，简单模型和统计方法应纳入 baseline。（§5.2）

复现价值高：代码公开，包含 dataset loader、算法实现、超参数配置及评估。使用结果时要记录版本、数据划分、随机种子、被抽样的子集、阈值选择与主指标；benchmark 更新也可能改变排序。论文描述主设置每个数据集随机划分 tuning/evaluation 序列，并报告一次主随机种子，因此复现者应额外测量 seed stability。（§4.2; checklist p.17）

## 9. Limitations and Critical Reading

- **作者明确指出**：人工审核由有限的有经验人员完成，数据集不是完美或最终版本，会持续扩充；该项目提供可迭代 testbed，而不是宣称 ground truth 无误。（§6, p.10）
- **实验协议局限**：主结果固定随机种子，不能单独支持随机性稳健结论；从时间序列派生的 channel 子集也有依赖性。（Appendix checklist p.17; §4.1）
- **我们分析的潜在选择偏差**：多种 detector 参与筛选，并用可检测性指导标签修订；这可能让最终基准更偏向可被现有方法识别的 anomaly，但论文没有证明偏差的方向或程度。（§4.1.2）
- benchmark 汇聚多个数据源，其场景语义和异常定义不统一；它不提供统一的 workload、release、Trace 或服务状态标签，也没有专门控制“正常负载变化与真实故障同时发生”。这一点是根据数据和输入范围作出的证据边界判断，不是作者声称 benchmark 无效。
- VUS-PR 的推荐来自本文构造的可靠性分析场景；新任务仍需检验指标是否与实际业务代价和 detection latency 对齐。（§5.2.1）
- 本文是 benchmark 工作，不直接解决在动态正常状态下建立条件化 normal model 的建模问题。

## 10. Related Papers

- **Quo Vadis (ICML 2024)**：以少量简洁 baseline 和实验协议批判复杂模型比较；TSB-AD 将 baseline、调参、更多 detector 和评测指标扩成系统 benchmark。两篇都强调 PA-F1 与测试阈值的解释边界。
- **CAPMix、Fortifying Time Series、CAROTS**：方法贡献各异，但横向比较前应在 TSB-AD 风格协议下统一数据、阈值和区间指标；其自有实验数字不能直接混成排名。
- **MOMENT / 时间序列基础模型**：TSB-AD 增加 foundation models 评测，并用 MOMENT-Eval 案例讨论训练数据污染。
- **TFMAE / MACE / TFC**：模型分别使用 temporal-frequency masking、多 pattern spectrum 和 temporal-frequency-curvature view；TSB-AD 的结果可帮助将其定位到统一 evaluation concern，但需留意各原论文使用的 dataset / metric / threshold 差异。

## 11. Questions for Further Reading

1. 人工复核、算法辅助与领域上下文能否形成可追踪的标注 provenance 和不确定性，而不是单一硬标签？
2. 按异常类型与运行状态分别划分时，TSB-AD 上的方法排名是否保持？
3. detector-assisted curation 是否对特定模型族或容易检测异常产生 selection bias？需通过保留的未筛选候选集和独立标注者验证。
4. 如何补充带 workload、deployment、业务周期、Trace 和故障注入标签的基准，并处理负载变化与故障并发？
5. 相较 VUS-PR，真实 on-call 场景的误报频率、事件级 recall、检测延迟和告警合并策略如何共同影响模型选择？

## 12. Key Terms

- **TSB-AD-U / TSB-AD-M**：TSB-AD 的 univariate / multivariate benchmark 部分。
- **PA-F1**：point adjustment 后的 F1；一个标注异常段内任一点命中可能将整个段回填为命中。
- **VUS-PR**：对阈值和异常区间容忍范围做 volume-based 汇总的 PR 指标；本文评估中对部分 lag 场景较稳健。
- **Detector-assisted curation**：通过多类检测器检查候选标签与序列，再由人工审查上下文并确认或修订。

## 13. Tags

`TSAD` `benchmark` `dataset quality` `evaluation metrics` `VUS-PR` `point adjustment` `foundation models` `reproducibility`
