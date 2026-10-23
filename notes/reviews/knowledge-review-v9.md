# Knowledge Review v9：TSAD batch 7 — LLM 表示蒸馏、零样本提示与统计证据强化

## Scope and Evidence Labels

本次覆盖第 19–21 篇，累计 **21/33** 篇实际 PDF 全文精读：

- [AnomalyLLM](../../papers/anomalyllm/notes.md)：GPT-2 teacher / prototype student 表示蒸馏。
- [Delving into LLMs for TSAD](../../papers/delving-llm-tsad/notes.md)：failure analysis、去季节分解与 index-aware prompting。
- [AnomSeer](../../papers/anomseer/notes.md)：GT-derived expert trace、OT reasoning reward 与 TimerPO。

以下区分**作者主张**、**实验实际支持**和**本知识库分析推断**。不同 benchmark、样本、threshold 和 event metrics 不统一，表内数字只在各自协议内比较，不跨论文排总名次。此 Review 仍是 21 篇范围内的阶段性综合，不是最后研究空白结论。

## 1. 本批机制对比

| 方法 | LLM 的角色 | 训练 / 输入机制 | 异常证据与输出 | 主要实验边界 |
| --- | --- | --- | --- | --- |
| AnomalyLLM (IJCAI 2024) | 预训练 GPT-2 是时序表示 teacher | 冻结大部分 GPT-2；student 用逐变量 prototypes；局部 synthetic anomaly 拉开两侧表示 | $\|z-c\|^2$ 窗口 score | 9 个 UCR domain groups + 6 MTS datasets；UCR AF1、其他表 adjusted F1；prototype 32 / 48 口径不一 |
| Delving (NeurIPS 2025) | 冻结零样本 LLM / MLLM 是提示式 detector | ACF dominant-period de-seasonalization；index-value text + plot image；不 fine-tune | 模型直接生成 anomaly intervals / labels | 21 prompts、AnomLLM；TSB-AD-U 只选 8 个较短类别；高 latency；context case 为少量 qualitative examples |
| AnomSeer (ICML 2026) | Qwen2.5-VL 是生成式分类 / 定位 / 解释模型 | GT class / interval 生成 ExpCoT；OT alignment advantage + orthogonalized TimerPO RL | 输出 `<class>`、`<answer>` 和 `<think>` trace | 3,200 个 labeled synthetic train instances；AnomLLM / VisualTimeAnomaly / TSB-UAD；Affinity metrics；主要实验仍以 univariate 为主 |

## 2. 各论文的直接证据

### 2.1 AnomalyLLM

- **[作者方法]** 原始训练窗让 teacher / student 靠近，局部 jittering / scaling / warping 视图让两者远离；另将 teacher 两视图拉近（Eqs. 5–7）。student 按 channel 选择 prototype 并把它作为 Transformer attention context。（§3.2–3.4, pp.3–5）
- **[实验支持]** UCR aggregate accuracy / AF1 .820 / .858，NCAD .663 / .767；多变量 Table 4 报告 adjusted F1，WaQ / SWAN Table 5 为 .620 / .804。（Tables 3–5, pp.6）
- **[需保留的不一致]** prototype 主设置写 32，敏感性文字说 48 最好；Table 5 列是 WaQ，正文一处把 62% / 47% 结果称为 GECCO。按表格记录，不更正原文。（§4.2–4.4）
- **[范围]** few-shot / zero-shot F1 展示在 PowerDemand 单一案例，不是广泛跨域验证；PDF 未提供 code repository。（Table 6, p.7）

### 2.2 Delving into LLMs for TSAD

- **[作者方法]** 将序列理解与 anomaly localization 分开测试；dominant ACF period 进入 additive decomposition，仅去 seasonal $s_t$；显式给文本值附位置 index。（§2–3, Eqs. 1–2, pp.3–6）
- **[实验支持]** AnomLLM 上 GPT-4o / Qwen text+vision standard F1 70.04 / 67.56，优于其 0-shot vision prompt 42.03 / 46.65；去 index 的消融平均损失 23.36 F1 points，去 de-seasonalization 损失 5.64。（Tables 1–3, pp.7–8）
- **[实验支持]** TSB-AD-U Table 9 中 GPT-4o standard F1 34.20、Affiliation F1 74.64、140.63 秒 / sample；SR + MAD 为 30.57、75.94、约 0.02 秒。指标排行不一，延迟成本明显。（§5.1; Appendix Table 9）
- **[范围]** context filtering 是 ETTh2 / Electricity 小规模实验：挑传统 detector 常报警片段并给模拟的 domain descriptions；没有运行平台 workload / release / Trace 的完整评估。（§5.2, Appendix D.6）

### 2.3 AnomSeer

- **[作者方法]** ExpCoT 先观察 global distribution、smoothed gradients / FFT 与 local Matrix Profile，再由 GT anomaly type 选 numerical probe；reference trace 的最终结论保留 GT anomaly interval。（§4.1; Appendix B.2）
- **[作者方法]** TimerPO 计算 generated trace 与 ExpCoT 的 token cosine cost / optimal transport $W_i$，用 $e^{-W_i/\tau}$ 形成 reasoning reward；把其 group-normalized advantage 对 task advantage 正交投影后用于 clipped RL objective。（§4.2, Eqs. 1–8）
- **[实验支持]** 平均 Affinity F1：TimeMaster-3B 71.9、AnomSeer-3B 79.3、7B 84.4；TimerPO 对 weighted-sum / PCGrad 和 cosine / CLIP alignment 的消融均更高。（Table 1; Appendix Table 6）
- **[标签边界]** pure-RL 指训练算法没先做 SFT，不等于 label-free：ExpCoT 从 GT type 和 interval 构造，训练 3,200 个 synthetic annotated samples。（§5; Appendix B.2）
- **[限制]** 主线是 univariate；附录 multivariate 是扩展实验。末端 short anomaly `[998,1000]` 仍漏检；作者也将更复杂 multivariate dependency 留作方向。（§6; Appendix D.4 / D.7）

## 3. 正常状态、业务波动与故障证据

### 多种正常运行状态如何建模？

- **AnomalyLLM：** 每通道 prototype bank 可以保存多个重复出现的典型形状；这是可学习多模板，但不带“低负载、扩容、促销、发布”等状态语义。它依赖训练中出现的窗口代表正常形态。（§3.2）
- **Delving：** 统计分解剥除一种主要、稳定重复的 seasonality；这可以减少季节项遮蔽，但不是多业务状态识别，也不等同自适应 normal-state memory。（§3.1）
- **AnomSeer：** 用 anomaly taxonomy 指定 global / contextual / trend / frequency / shapelet probe；它对异常类别分工具，不是在运行中的多个合法状态之间建立条件 normal model。（§4.1）

**综合判断 [分析推断]：** 本批新增“形状 prototypes”“主周期分解”“跨异常类别的统计探针”，尚未看到按 workload / release / service state 条件化的一组可更新正常模型。它们扩大时间形态覆盖的方式不同，不能统称为 dynamic normal-state modeling。与前 18 篇中的 CrossAD prototypes、Graph-MoE memory、MACE service-conditioned spectra、When Model Meets New Normals test-time adaptation 等方法也应分开比较：前者在 embedding / frequency / online adaptation 层面提供 normal references，不自动提供业务语义。

### 正常业务波动和真实故障如何区分？

- **已出现的 mechanisms：** prototype discrepancy（AnomalyLLM）、seasonal decomposition 和用户 context filtering（Delving）、与 GT anomaly type 匹配的统计异常 probe（AnomSeer）。这些都是值得区分的证据路线。
- **真实业务 context 的证据：** 仅 Delving 显示 LLM 可以响应文本 context、过滤作者视为可解释的已知片段；然而 context 是模拟描述，样本是共同 detector 报警片段，非真实 event log / load / release label。它没有量化过滤误报时对未知故障召回的代价。
- **AnomSeer 的 evidence vs source：** trace 可包含 gradient、period、discord、outlier 数值并提高 benchmark 定位 / 分类结果；但它依据 GT type / interval 生成，并不追踪异常为何由业务或系统变化产生。

**综合判断 [分析推断]：** 这三篇说明“对模式做表示”“去除稳定周期”“按上下文重定义哪些变化值得报警”“以统计量写解释”是不同能力。尚无一篇把真实业务背景、负载突变、异常注入和二者同时发生纳入受控 matrix，再检验状态判断、故障证据、解释和漏报风险。

### 是否只抑制噪声，是否解释波动来源？

AnomalyLLM 用一致性 / prototype 限定表示，输出距离；Delving 的去周期步骤抑制 seasonal background，context 可做语义过滤，但主 detector 输出仍是区间；AnomSeer 产生较细粒度 reasoning text 与统计证据。三者不是单纯平滑器，但只有把观测与统计探针串起来，尚没有将波动归因到 workload、release、service dependency、Trace 或 fault injection cause 的独立证据链。**文本解释不是来源归因的同义词。**

## 4. 多论文方法演进与对 18 篇 prior work 的关系

1. **通用先验进入表示学习（2024）**：AnomalyLLM 将语言预训练参数当成 frozen sequence teacher，以 normal prototypes 向 student 注入领域形状先验；依赖训练 / 增强构造分离分数。
2. **零样本输入结构纠偏（2025）**：Delving 不把“LLM 理解时间序列”当默认事实，用 diagnostic isolation 找出理解与定位瓶颈，再以可解释统计预处理 / 索引格式辅佐模型；其 context value 是额外的 interactive filtering route。
3. **专家信号进入生成目标（2026）**：AnomSeer 将 classical detector probes 转成 labeled trace，token-level OT 令语言生成过程向该 trace 对齐，再以正交 advantage 控制辅助奖励。

与前 18 篇方法的关系：

- AnomalyLLM prototype bank 与 CrossAD / Graph-MoE 的 normal prototypes / memory 同属“重复形态参照”，但 TSAD score 和训练目标不同。
- Delving de-seasonalization 与 MACE / TFC / TFMAE 的频率建模有交集；Delving 将频率处理做成统计前置工具，而非 learner 内部表示，也须评估 seasonal-removal 是否抹弱频率故障。
- AnomSeer 的 HBOS / FFT / gradient / Matrix Profile 对应 TFC、TriAD、PCRTA 等已用的统计结构证据；新贡献是将它们转成可生成的 reference trace + OT reward，而不是发现这些检测统计量本身。
- Context filtering 与 CAROTS / causal relations、GCAD / OracleAD / SARAD 的结构变化 evidence 不同：前者用文本定义“是否值得告警”，后者用序列依赖结构计算偏离；两者都还需与真实业务状态和故障根因核验。

## 5. 研究空白与需要的证据

以下都是 **21 篇已读范围内的证据缺口**，不是未经检索的全领域优先权判断：

1. **正常状态语义化**：已读方法有 prototype、memory、谱模式、周期项和 test-time adaptation，但目前证据没有展示同一 service 的多 workload / release state 如何被命名、选择与更新。实验需包含仅状态变化、仅故障、两者并发、未见合法状态，并报告状态切换后的 false alarms 与故障召回。（前述方法；Knowledge Reviews v3–v9）
2. **context filtering 的安全性**：Delving 是本批唯一以自然语言 context 定性过滤变化的证据，但它没有同测“known explainable event”和“未知故障 / 同时发生”。后续需以真实业务元数据或可靠合成上下文检查 context 是否抑制新故障。（Delving §5.2）
3. **波动来源解释验证**：AnomSeer 证明 statistical probe trace 可改善合成 benchmark 分类 / localization；还需独立专家 review、证据重算、反事实扰动和真实 topology / Trace 对齐来判断说明是否忠实、是否只是复述 label。（AnomSeer §4–5 / Appendix B.2）
4. **状态变化 / 故障并发下的在线更新安全**：本批 AnomalyLLM prototype 训练、Delving 输入变换、AnomSeer RL 都未验证运行期状态更新与故障污染；问题与之前在线适应、memory / reference 方法一并保留。（前 21 篇）
5. **操作运行点**：LLM text generation 的实际 latency 很高，index formatting 会影响解码长短；许多 detector 结果又依赖 best threshold / Affinity / adjusted F1。需统一 fixed false-alarm budget、validation-only calibration、event delay、CPU/GPU cost 和 unresolved review burden。（Delving Table 4 / Appendix Table 9; prior reviews）
6. **synthetic trace / perturbation 到真实领域的落差**：AnomalyLLM 的三种局部变换和 AnomSeer 的 AnomLLM trace generator 都需要跨 generator、真实 anomaly type 和合法高波动 normal 做外推验证；“新形状 benchmark 表现好”尚不证明新业务状态鲁棒。

## 6. TSAD 问题进度（当前 21 篇范围）

| 研究问题 | 状态 | 21 篇范围内当前证据 |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | prototypes、service spectra、memory、test-time adaptation、周期拆分、contrast views 等已有机制；还未证明面向 workload / release 语义的安全状态识别与迁移。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | 有形态 / 时间 / 频率 / 关系偏差及 Delving 的文本 context filtering；尚无真实 context + fault concurrency matrix。 |
| 只抑噪声还是解释来源？ | Partially Answered | 方法可抑制特定 view / 周期干扰；AnomSeer trace 给 numerical evidence，但没有经外部 cause ground truth 确认来源归因。 |
| 是否利用 Metric、Trace、workload、release context？ | Open | Delving 仅用少量文字化模拟背景；其余本批主要是数值窗口 / plot / synthetic trace。未系统输入与评估真实 Trace / workload / release。 |
| 正常负载变化与故障同时发生时怎样处理？ | Open | 本批三篇和此前 18 篇均无受控并发实验。 |
| 哪些方向已被提出？ | Partially Answered | 形态 prototypes、周期分解、index-aware localization、context-based exclusion、统计解释轨迹与 RL OT alignment 已有明确方法；任何新提案应对比这些已有机制。 |
| 哪些结论缺少实验支持？ | Partially Answered | real context filter safety、rationale faithfulness、合法状态 / 故障并发、online threshold、真实多变量结构解释和固定成本运行点仍缺足够验证。 |

## 7. 下一批阅读方向

第 22–24 篇先沿“zero-shot / multimodal / open-set 泛化”方向梳理：

1. **Harnessing Vision-Language Models for Time Series Anomaly Detection**（AAAI 2026）
2. **Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy**（ICML 2026）
3. **IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection**（ICML 2026）

阅读时继续核对其是否仅换输入 / 预训练模型，还是显式建模未见 anomaly、合法状态、上下文来源；后续批次可据论文方法结构再调整分组。
