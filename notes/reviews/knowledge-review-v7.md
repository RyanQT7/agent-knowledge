# Knowledge Review v7：TSAD batch 5 — 评测可信度与跨视图频率证据

## Scope and Evidence Labels

本次 Review 覆盖第 13–15 篇及之前 12 篇已读论文，共 **15/33** 篇：

- [Position: Quo Vadis](../../papers/quo-vadis/notes.md)：简洁 baseline、阈值和时间序列指标批判。
- [The Elephant in the Room / TSB-AD](../../papers/tsb-ad/notes.md)：curated benchmark、多指标分析和 detector comparison。
- [TFMAE](../../papers/tfmae/notes.md)：时间—频域遮盖、自监督跨视图 discrepancy 和 adversarial objective。

本综述区分：**论文事实**（正文/附录明确内容）、**跨论文综合**（对方法的并列归纳）、**本轮已读范围内的证据缺口**（后 18 篇仍可能改变结论）和**分析推断**（建议由后续实验检验）。不同数据拆分、threshold、point adjustment 和指标结果不是同一排行榜。

## 1. 本批提供的证据

### 1.1 论文事实

- **Quo Vadis**：用 sensor range、L2、1-NN、PCA residual、浅层神经模型建立简洁 baseline；point、range-wise F1 与 PA-F1 对噪声 / 区间命中的反应差异显著。随机 score 在 SWaT 的 PA-F1 为 .963，standard F1 / range F1 约 .218 / .217；PCA 在作者的 SWaT、WADI 和 SMD 设置中很有竞争力。（§§3–4, Tables 2–5, PDF pp.3–9）同一论文 F1 threshold 取 test set best threshold，作者称其为沿用文献协议；因此结果是 protocol-specific oracle ceiling，不是无标签部署阈值。（§3.5, p.6）
- **TSB-AD**：包含 1,070 条序列（870 UTS / 200 MTS），来自 40 个数据集；由人工感知和算法辅助审查整合，覆盖十种指标与 40 类 detector，并搜索 450+ variants。（§4, Tables 1–2, PDF pp.2, 5–7, 19）作者用合成 score tests 比较 lag tolerance 和 random-score bias，推荐 VUS-PR 作为他们评估情境中较可靠的主指标；结果显示 UTS 上 Sub-PCA 的平均 VUS-PR 领先、MTS 上 CNN 表现突出，但没有模型在每个 dataset 都最优。（§5.2, Table 5, Figs. 5–7, pp.7–10）主 benchmark 使用固定随机种子；作者说明少数专家人工审查有限，benchmark 会继续更新。（checklist p.17; §6, p.10）
- **TFMAE**：用局部 CV 最高的 temporal observations mask、每变量 DFT 幅值最低的 frequency bins mask；两路 Transformer view 的逐点 score 为双向 KL 之和。训练以 adversarial min-max 目标降低正常表示差异并保留异常差异。（§§III–IV, Eqs. 1–17, PDF pp.3–8）作者在五个真实集上平均 point-adjusted F1 报 96.04%，并用消融支持 adversarial objective / mask view 的贡献。（Table III–V, pp.9–11）主结果仅报告经 PA 的 P/R/F1；阈值在 validation set 按预设异常比例确定。（§V-A, pp.8–9）

### 1.2 三种不同贡献不能混成一个方向

| 论文 | 主要对象 | 提供的证据 | 不能据此推出 |
| --- | --- | --- | --- |
| Quo Vadis | baseline、score normalization、point / range metric、阈值 protocol | 简单基线在其指定数据与协议下有竞争力；PA-F1 对 random score 可能过度奖励 | PCA 在所有 TSAD 场景都充分；测试标签 oracle F1 等于线上能力 |
| TSB-AD | 数据集质量、metric behavior、unified detector tuning | 多种 metric 会给出不同视角；模型排名随数据与 anomaly type 改变 | curated label 完全客观；VUS-PR 对所有真实业务代价普适最优 |
| TFMAE | temporal/frequency masked-view representation discrepancy | 在其数据与 PA protocol 下具备高 F1；组件消融和单个 shift 案例支持方法动机 | 对合法负载状态变化具备语义辨别；在非 PA / 事件延迟协议下仍保持同等排名 |

## 2. 评测比较与协议边界

### Threshold / metrics / random baseline

- **Quo Vadis 的警示也适用于自身数字**：作者以 test-set best threshold 计算多种 F1，并同时展示 PA-F1 的随机 score 结果。这使论文可以展示协议影响，却不代表其报告的最佳点就是可部署阈值。（Quo Vadis §3.5, p.6; Table 2, p.7）
- **TSB-AD 扩大了指标集合**：其 VUS-PR、Event-F1、Affiliation-F1、PATE 等都包含不同的区间容忍、事件奖励或边界偏好；论文基于 synthetic scenarios 对 lag / random score 进行检查。作者推荐 VUS-PR 是有证据支撑的 task-level recommendation，仍应与实际告警预算、延迟和事件成本一起验证。（TSB-AD §4.3, §5.2.1, pp.7–9）
- **TFMAE 主结果的可比范围有限**：PA 后 F1 将区间内单点命中扩展至整段，且 threshold 依 validation score 和给定异常比例。不能把 .9604 与 TSB-AD VUS-PR 或 Quo Vadis range-F1 直接排序。（TFMAE §V-A, Table III; TSB-AD §§3.2, 4.3）
- **跨论文最低报告要求（本库工作规范）**：数据预处理 / entity split、score aggregation、threshold 来源、测试标签是否参与 threshold、PA / label adjustment、point 与 event/range 指标、seed 数及运行点告警成本均应同时记录。

### Benchmark reliability is ongoing work

TSB-AD 通过人工 + 算法辅助筛查解决部分旧问题；其作者仍称数据集不完美且会持续更新。因为 detector assisted curation 本身将“是否被已有 detector 找到”用作证据之一，**我们的风险推断**是它可能改变异常难度构成；是否实际偏向某类 detector，需要未筛选候选集、独立复核和标注 provenance 才能验证。（TSB-AD §4.1, §6）此外，部分 UTS 是 MTS 单个 channel，因此统计序列数不等于独立原始场景数；主结果固定随机种子也限制方差估计。（TSB-AD Table 2 / Appendix checklist）

## 3. 对正常状态与波动区分问题的当前认识

### 多种正常运行状态如何建模？

**已读机制**：MACE 以服务身份检索静态频率子空间；CrossAD 使用跨窗 prototype；Graph-MoE 使用 latent memory 路由；WMMNN 在测试期适应新正常；TFMAE 学习同一序列的 temporal/frequency view agreement。它们分别建模跨服务差异、窗口模式、历史 latent 模式、在线更新或视图一致性，不能统一称为同一种 multi-normal-state method。（对应单篇 notes §§3–6）

**15 篇范围内判断：Partially Answered。** 有多种正常参照的不同实现，但尚未由 workload、release、autoscaling、业务周期等可解释状态标签标识同一服务的合法状态，并在状态切换时证明保持故障敏感度。TFMAE 的同序列双视图一致性不等于按运行态条件化 normality。

### 正常业务波动和真实故障如何区分？

**已有线索**：形态伪异常（CAPMix）、测试时适应（WMMNN）、因果增强 / 关系变化（CAROTS、GCAD、OracleAD）、attention progression（SARAD）、频谱（MACE、TFMAE）、跨尺度（CrossAD）、曲率和顺序证据（TFC、CCM-TAD）及 robust decision certificate（Fortifying）都已提出；其统计对象和威胁模型各异。

**分析边界**：TFMAE 的高-CV temporal masking 可能遇到合法业务峰谷，low-amplitude frequency masking 也不代表筛到业务无关信号；单独的两视图一致性没有解释波动成因。上述是输入 / 目标函数的机制分析，尚不能据此断言实际线上误报。（TFMAE Eqs. 1–10, 14–16; dataset / experiment scope §V）

**15 篇范围内判断：Partially Answered。** 存在多种互补 statistical evidence，但没有系统构造“仅状态变化 / 仅故障 / 状态变化+故障 / 未见合法状态”实验矩阵，报告固定运行点的事件召回、误报时长和延迟。

### 是否解释波动来源，是否用 Metric / Trace / context？

TSB-AD 解决 benchmark / measure 问题；TFMAE 的 score 量化两路表示差异；Quo Vadis 讨论 baseline 和评价边界。三篇都没有用 workload、deployment / release、Trace 作为 detection input，也不从 score 恢复业务变更来源。前 12 篇已读的方法提供 causal / graph / latent / association 指标，但尚未充分与真实拓扑或 Trace 根因对齐。（三篇 §§3–7；前序 Review v6 §2）

**15 篇范围内判断：Open。** 本批未加入运行上下文 evidence。数据源来自服务器或生产监控不代表算法使用业务上下文。

## 4. 已有机制与审慎表述

- “简单方法不应缺席 baseline”已有 Quo Vadis 实证和 TSB-AD 的广泛比较支撑；新方法应说明对 PCA / nearest-neighbor / shallow models 的增益。（Quo Vadis §§3–4; TSB-AD §5）
- “复杂模型普遍优于统计方法”不受 TSB-AD 的整体结果支持；其观察是优势因数据集、异常类型和指标而变，而不是 neural models 无效。（TSB-AD §5.2）
- “使用多视角 / 频域”不是单独的新空白：MACE、TFC 和 TFMAE 已分别提出多频率 normal subspaces、多域融合、masked frequency view。新贡献要说明它解决的状态语义、shift 类型或并发条件。（v4–v7 Review）
- “缓解 distribution shift”也有不同机制：WMMNN 直接 test-time adaptation，TFMAE 用两视图 discrepancy 案例支持阈值分布稳定；二者都未充分证明对正常状态变化 + 真实故障并发的安全区分。（WMMNN note §6; TFMAE Fig. 9）
- “更可靠 metric”不是孤立结论：VUS-PR 在 TSB-AD synthetic reliability tests 中表现较稳健，但还需和告警成本、事件延迟、状态切换任务的业务效用校准。（TSB-AD §5.2.1）

## 5. 仍缺乏充分验证的研究问题

1. **状态迁移与故障并发**：带 workload / release / scale change 标签并独立注入故障；测量条件误报、事件 recall、延迟和适应污染率。
2. **运行上下文增益**：严格对照仅 Metric、Metric+业务负载、Metric+Trace / release；防止上下文仅与异常标签泄漏相关。
3. **阈值部署性**：对比 test oracle Best-F1、validation anomaly-rate threshold、正常-only calibration、固定告警预算与跨实体校准。
4. **metric–utility 关系**：VUS / range / PA 与 on-call 告警数量、重复告警合并、边界延迟和漏检代价的相关性。
5. **curation 选择效应**：独立标注者、模糊标签、不确定性和 detector-blind holdout，判断 detector-assisted curation 是否系统改变测试难度。
6. **双视图语义**：测量 TFMAE 的正常高波动、低能量关键模式、动态周期变化与多通道关系异常，而非只在固定 benchmark 上比较 F1。
7. **重复性与成本**：多个 seed、数据版本、预处理版本、threshold 运行点、长序列内存与在线延迟的联合报告。

这些是**当前已读 15 篇的证据缺口**，后 18 篇仍需继续复核；不据此声明全领域 novelty。

## 6. 下批阅读计划

第 16–18 篇聚焦 2024 年的表示、跨域与增强方法，先安排：

1. **Unraveling the “Anomaly” in Time Series Anomaly Detection: A Self-supervised Tri-domain Solution**（ICDE 2024）— 核对三域构造、损失和异常 score；与 TFMAE / TFC 的多视图差别。
2. **Perturbation Guiding Contrastive Representation Learning for Time Series Anomaly Detection**（IJCAI 2024）— 核对扰动生成、正负对构造及 robustness claim。
3. **Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods**（IJCAI 2024）— 对照局部邻域重建和现有窗口 / 多尺度 normal references。

LLM / VLM TSAD 将和 2025–2026 对应论文按主题组成后续批次；完整 33 篇结束前不对其有效性或 novelty 下结论。
