# GALA: Graph-Augmented LLM Agents for Root Cause Analysis and Incident Response in Microservices

## 论文身份与版本

- **作者：** Yifang Tian、Yaming Liu、Zichun Chong、Zihang Huang、Yiran Li、Hans-Arno Jacobsen。
- **发表信息：** ASE 2026 Research Track，论文集第 55–67 页，DOI [10.1145/3832783.3834335](https://doi.org/10.1145/3832783.3834335)。
- **本次精读版本：** [arXiv:2608.08968v1](https://arxiv.org/abs/2608.08968)，2026-08-10 提交，共 13 个 PDF 物理页。论文题名与 ASE 发表题名一致，正文所描述的框架称为 **GALA+**。
- **较早的相关预印本：** [arXiv:2508.12472](https://arxiv.org/abs/2508.12472)，题为 “GALA: Can Graph-Augmented Large Language Model Agentic Workflows Elevate Root Cause Analysis?”，2025-08-17 提交，列有五位作者。作者[项目页](https://msrg.github.io/publications/gala-graph-augmented-llm-agents-for-root-cause-analysis-and-incident-response-in-microservices/)将它列为早期预印本，并将 ASE 论文描述为更新后的 GALA+。新论文也把旧 GALA 作为基线并指出若干设计变化，因此应视为研究版本演进，不能把两份 PDF 当作仅改题名的同一版本。
- **本地 PDF：** `sources/papers/opsagent/gala-ase26.pdf`（Git 忽略）。
- **全文解析：** `sources/papers/opsagent/gala-ase26.txt`（按物理页分段，Git 忽略）。
- **官方公开仓库：** [EvanTian233/GALA-for-RCA](https://github.com/EvanTian233/GALA-for-RCA)，静态检查 commit `24d1329d20fb9139f7899a1bed9e8d0bdaf00be0`。
- **阅读范围：** 完整阅读本地 PDF，包括实验、案例、威胁、结论和参考文献；静态检查一页技术报告、公开样例和标注材料。核心 GALA 实现未公开；没有运行代码或 Benchmark。

## 研究执行记录

- **方式：** 当前 Codex 主会话进行轻量研究；没有启动 Evolution Engine 或子模型会话。
- **使用的 paper-reading 版本：** 冻结候选 `skill-paper-reading-20261126t110225z-ed765d`，并结合 `aiops-paper-reading`、`knowledge-review`。
- **复用的 Experience（仅作过程指导）：** `exp-311316848c9f`（机制、案例、实验和定位）、`exp-4018148873bb`（固定源码版本并限制源码结论）、`exp-77ed5c77884f`（覆盖贡献比笔记长度重要）、`exp-8da9d9cb732b`（版本、定位、分母及评分口径）。这些经验不是 GALA 事实的证据。
- **模型：** 当前运行环境没有提供主会话模型标识，故记为不可得。
- **研究耗时：** 2026-11-26 12:38:22–13:05:14 UTC，26 分 52 秒（不含 Git 收尾）。
- **Token：** 当前运行环境不公开输入、输出 Token 统计；不可得，未估算。
- **原图核验：** 本地图像查看器实际查看主论文 PDF 物理页 3、4、5、8、9、10，以及技术报告物理页 1。涵盖 Figure 2、STRIX/RRF 公式和上下文构造、Algorithm 1/Figure 3、Tables 1–3、Figure 4/Table 4、Table 5、Figure 5、Figure 6 和 AegisLab 表。渲染文件留在 `/home/xieqitong/.cache/agent-knowledge/paper-pdf/gala-ase26/` 与 `.../gala-tech-report/`，不纳入仓库。
- **材料限制：** 未取得可供版本差异比较的出版商 PDF；精确提示词、SURE-Score 最终 checklist 与 scorer、工业遥测数据均未公开。

## 一句话概括

GALA+ 将指标侧候选排序与调用 Trace 的服务依赖排序作为互补假设，经 LLM 整合后，在候选周围受限检查指标、日志和拓扑邻居，再综合分支证据输出根因排序、事件说明及三类处置建议。

## 问题与贡献

微服务告警中，明显变慢的服务可能只是传播链上的受害者而非故障源。仅给出一个服务排名不足以支持处置，运维人员还需要能对应观测证据的诊断说明与可执行建议。作者认为，单一遥测模态会遗漏互补信号；无约束的 Agent 搜索可能漂移或产生无证据叙述；文本相似度指标则不能评价 RCA 说明是否有据、可执行。（Abstract、§§1–2，PDF 物理页 1–2。）

1. **双信号假设生成：** BARO 处理指标，STRIX 根据 Trace 延迟与服务依赖结构产生排序；Consolidation Agent 处理两侧输出不对称的问题，而非直接对原始分数求平均。
2. **图约束调查：** Investigator 对候选服务的局部遥测进行调查；证据不足时才分批检查邻居，搜索受到置信阈值和候选邻域限制。
3. **事件响应文本与评价：** 输出最终排序、事件摘要及即时缓解、永久修复、预防建议；SURE-Score 从 RCA 专属维度评价文本，并辅以 LLM grader 和 SRE 人工评审。（§§3–5，PDF 物理页 2–9。）

**关键术语边界：** GALA 正文将其指标侧 BARO 描述为对指标构造因果 DAG；STRIX 的图则是从分布式 Trace 恢复的服务调用依赖图。依赖边本身不等同于物理因果关系。更重要的是，BARO 原论文的公开方法与 GALA 对它的这一描述不一致，详见下文“BARO 方法引用差异”。

## 任务边界与工作流

- **处理任务：** 根因候选排序/定位、诊断解释、事件摘要及建议生成。
- **论文未报告的能力：** 在线检测真实告警、执行修复命令、验证服务恢复，或将结果写入持久运维知识。
- **输入：** 事件附近的 Metrics、Logs、Traces。论文把根因定义为“若解决则可消除事件”的 pod 与故障模式组合。
- **候选空间：** 部署中的服务/pod；AC@k 等排名指标实际比较 pod。服务级 STRIX 节点如何精确映射至 pod 级候选，论文没有充分交代。
- **输出：** 候选排名、事件说明、即时缓解措施、永久修复和预防建议。
- **模态融合：** 指标、日志、分布式 Trace 各保留独立结构后装入诊断上下文，属于结构化上下文融合，不是学习出的共享多模态 embedding；拓扑用于约束调查范围。

### 端到端流程

1. **指标排序：** GALA 正文称 Phase I 通过 BARO 检测异常服务、生成指标因果 DAG，并根据候选对已观测异常的因果影响排序。
2. **Trace 排序：** STRIX 从 span 构造加权服务依赖图，以不稳定性、中心性、影响力三个信号排名。
3. **假设整合：** LLM Consolidation Agent 提高双信号同时支持的候选；为仅出现在 Trace 排名中的服务推断故障类型；对缺少 Trace 佐证的指标候选降低置信度。
4. **上下文整理：** 为候选 pod 汇集告警附近逐秒指标、一跳依赖子图，以及按时间排序并去重/抽样的日志。
5. **图引导调查：** 最多并行调查排名前 k 个候选。每条分支记录置信度、证据摘要、因果解释和支持/反驳因素。若置信度低于 θ，按批次抽取直接前驱和后继；批次中出现高置信服务则终止该分支。
6. **证据综合：** Synthesis Agent 汇总调查记忆，以初始信号锚定局部结论，并要求最终候选能够解释其他调查分支中的症状。
7. **报告生成：** 形成事件摘要和三层建议供 SRE 处置；论文没有展示自动执行建议或验证恢复。

Figure 2（PDF 物理页 3）展示初始假设、pod 上下文整理、图引导调查、诊断综合/事件响应四阶段。Algorithm 1（PDF 物理页 5）对“受限图搜索”尤为重要：按印刷伪代码，算法调查初始 top-k 服务及其直接前驱/后继；邻居循环调用 Investigator，但没有显式递归到邻居的邻居。正文称扩展受深度限制，而核心实现不可见，无法确认运行代码是否采用更深的变体。

## 核心方法

### BARO 方法引用差异：GALA 描述与原论文不一致

GALA §3.1.1 将指标侧流程归于 BARO，并写道它通过 Bayesian online change-point detection 识别异常服务，随后在 Metrics 上构造因果 DAG `G_M`，以服务对观测异常的因果影响产生初始排名（PDF 物理页 3）。这应准确记录为 **GALA 论文对其指标侧模块的描述**。

定向核对被引原论文 [BARO: Robust Root Cause Analysis for Microservices via Multivariate Bayesian Online Change Point Detection，arXiv:2405.09330v1](https://arxiv.org/abs/2405.09330) 后，原方法为另一条明确流程：先以 **Multivariate Bayesian Online Change Point Detection (Multivariate BOCPD)** 检测异常并估计异常时间；再由 **RobustScorer** 对每条指标序列评分。RobustScorer 用估计异常时间前的数据学习中位数 `med` 和四分位距 `IQR`，随后计算异常阶段每个点的标准化偏离 `|x_t − med| / IQR`，并取最大偏离 `ρ` 排名。原论文把统计检验用作排序而非以 p-value 做接受/拒绝判定。BARO 原论文 §§3.3–3.4、Algorithm 1 描述的是 Multivariate BOCPD + RobustScorer，未报告构造因果 DAG；其异常检测重点使用 latency/error 指标，根因排名则对全体指标进行 RobustScorer 评分。

因此，GALA 的“BARO 构造因果 DAG”表述与原 BARO 论文方法存在**来源描述差异**。这可能是 GALA 对方法的扩展、改写或摘要不准确；由于 GALA 核心代码未公开，本次无法判断实际实现采用原版 BARO、修改版，还是额外的图模块。不能据此推断未公开的 GALA+ 内部实现。此差异也意味着 GALA 文字中关于 BARO 的因果边方向问题，不能自动视为原 BARO 算法本身的属性。

### STRIX：从 Trace 形成结构排序

STRIX（Structural Trace Ranking via Intermodal eXploration）从 span 汇总有向服务调用图。节点/边携带调用量，以及均值、P50、P95、P99、最大值、标准差和累计延迟等统计量。三个分数为：

- **不稳定性：** `φ₁(v) = P99(v) / P50(v)`。作者的直觉是资源争用或瞬态故障会拉长延迟尾部，而中位延迟仍相对稳定。
- **中心性：** `φ₂(v) = PageRank(v) × (1 + in-degree(v)) / (1 + out-degree(v))`。它把全图可达性与入度/出度启发式结合起来。
- **影响力：** `φ₃(v) = TotalLatency(v) × max(0, 1 − max_{u∈outgoing(v)} AvgLatency(u) / AvgLatency(v))`。该项试图扣除可能花在慢调用方的等待时间，再用受影响流量规模放大剩余 self-time。

STRIX 用 Reciprocal Rank Fusion，而不是直接加权求和不同量纲的原始分数：

`RRF(v) = Σⱼ 1 / (60 + rank(v, φⱼ))`

这样对分数尺度不敏感，但不等于三个启发式就是因果证据。特别是影响力项把最慢的直接 callee 延迟作为下游等待时间近似；论文没有证明它对所有并发、扇出与多调用情形都能恢复因果延迟。（§3.1.2，PDF 物理页 3–4；公式已对照原页。）

### 候选整合与局部上下文

两类排名的输出并不对称：BARO 可给出服务/故障类型对，STRIX 只给服务顺序而没有故障类型。整合步骤把两榜共同靠前的候选视为更强的共识；仅在 Trace 排名中的候选会被补充推断故障类型；仅由指标支持、缺乏 Trace 佐证的候选会被降低置信度。系统返回置信度和证据来源，但未报告确定性的置信度计算公式或校准实验。（§3.1.3，PDF 物理页 4。）

上下文保留模态差异：

- 每个监控指标的逐秒数值，窗口为 `[τ−Δτ, τ+Δτ]`；τ 来自告警，Δτ 的具体值未报告。
- 候选节点及直接前驱/后继构成的一跳子图，附带边属性。
- 按时间排序并按消息去重的 error/exception 日志。日志过多时抽样；日志较少时补入少量非错误日志，以区分“静默故障”和“没有日志”。

论文称时间戳 JSON 替代较早的 Base64 折线图表示后能降低 Token 并改善诊断，但没有给出此表示变更的受控数值对照。日志预算和抽样细节也不足以复现。（§3.2，PDF 物理页 4。）

### 调查停止与最终仲裁

默认设置为并行初始分支 `k=6`、剪枝阈值 `θ=0.6`、邻居批次 `b=2`。单条分支的局部置信度达到 θ 时停止扩展；否则随机批量检查直接邻居，直到批次中出现高置信节点或邻居耗尽。每个调查结果都写入共享记忆 `M`，包括局部置信度、证据摘要、因果说明、支持因素和反驳因素。最坏搜索复杂度写为 `O(kΔ)`，其中 Δ 是最大图度；这描述伪代码的邻域规模，不保证端到端时延或 Token 成本，因为每次调查由 LLM 执行。

局部分支停止与最终诊断是两个决定：达到阈值只表示该分支认为局部证据足够，**不表示该候选自动成为最终根因**。Evidence Synthesis 仍需在初始排名和所有已调查分支之间仲裁。论文称其遵循 **signal anchoring**（局部置信度不能轻易推翻较强的初始信号）和 **chain coherence**（最终候选应解释其他分支中的症状）。不过，置信度没有校准说明，也未给出每个证据主张可外部核验的遥测定位符。（§§3.3–3.4、Algorithm 1，PDF 物理页 4–5。）

## 论文中的调查案例：Figure 6

TrainTicket 的 order-service 发生 CPU hog。初始指标排名把 order-service 排在第 5，STRIX 排第 7；整合后，它升至第 2，station-service 则在前。Figure 6 展示并行调查 top-5（图中画出四条分支）：

- order-service 分支找到 **3–4 倍 CPU 上升且没有 error log**，认为是静默资源饱和，局部置信度 `0.9`。
- station-service 因中心性排名较高，但内存稳定且缺乏因果联系，局部置信度显示为 `0.85`。
- auth-service 约 15% 的中等 CPU、没有尖峰，被认为是正常处理负载，置信度 `0.75`。
- config-service 虽在指标初始排名第一，但延迟约 `9.27 ms` 且平稳、日志无异常，置信度 `0.3`，该分支继续做邻居扩展。

图中默认 `θ=0.6`，前三个分支的局部值均高于阈值，但 station-service 仍是假阳性候选；最终 Synthesis Agent 综合跨分支证据后认定 order-service 为唯一根因，并将其从融合排序第 2 调整到最终第 1。这正说明 **局部置信阈值负责控制分支扩展，不负责全局判根因**。同时，`0.85`、`0.9` 等数值来自 Agent 评估，论文没有证明它们是校准概率。图例描述的是诊断和候选排除，不是已执行修复或已测得恢复。图注称调查了 5 个候选，而 §5.1 默认 `k=6`；论文未解释这一区别，可能是个案设定或呈现差异。（Figure 6，PDF 物理页 10。）

## 数据与实验设置

| 设置 | Online Boutique（OB） | TrainTicket（TT） |
|---|---|---|
| 应用 | 电商系统，17 个服务 | 票务系统，69 个微服务 |
| 报告的故障场景 | 90 | 90 |
| 故障类型 | CPU hog、内存泄漏、磁盘 I/O 压力、网络延迟、socket 错误、丢包 | 相同六类 |
| 故障生成 | 注入故障；论文称每类独立重复三次 | 注入故障；论文称每类独立重复三次 |
| 数据模态 | Metrics、Logs、Traces | Metrics、Logs、Traces |
| 其他信息 | 五个目标服务；观测时长和 Δτ 数值未报告 | 目标服务数量、观测时长和 Δτ 数值未报告 |

论文使用 RCAEval 的 OB、TT 微服务基准，并另报告 AegisLab 中抽取的 100 个案例，覆盖 25 类故障。实验环境为 Ubuntu 22.04、8 个物理 CPU 核、16 GB RAM、500 GB SSD、Python 3.10.12，无 GPU。LLM temperature 为 1.0，主结果默认 GPT-4.1-mini，OB 上比较七个模型。论文称结果平均三次运行，并在 McNemar 检验中使用三次运行的逐事件多数结果；数据集所称的“三次独立重复”与模型重复运行的关系没有完全说明。（§§5.1–5.3，PDF 物理页 6–10。）

## 评价设计与实验结果

### 根因排序

AC@1 衡量首位 pod 是否命中标注故障 pod，AC@3 衡量前 3 名是否包含目标 pod，MRR 对目标 pod 的倒数名次求平均。作者明确指出这些排名指标比较的是 **pod**，不要求故障类型也匹配；因此，尽管任务定义涉及 pod 与故障模式，主排名结果不能单独证明故障分类准确率。（§5.2，PDF 物理页 7。）

Table 1（PDF 物理页 8，已视觉核验）：

| 数据集 | GALA+ AC@1 / AC@3 / MRR | 最佳非 LLM AC@1 | 最佳既有 LLM AC@1 | 时间 / 总 Token |
|---|---|---:|---:|---|
| OB | 74.44% / 98.89% / 0.854 | CIRCA 66.67% | Flow-of-Action 48.35% | 52.87 s / 32.7K |
| TT | 73.33% / 85.56% / 0.801 | BARO 66.67% | Flow-of-Action 47.78% | 63.16 s / 90.4K |

约 26 个百分点的提升是相对最强既有 **LLM** 基线；相对最佳非 LLM 基线，OB 和 TT 的 AC@1 分别高 7.77、6.66 个百分点。GALA+ 并非在所有场景成本都低：它比 Flow-of-Action 用更多 Token，TT 上每例达到 90.4K；表中未区分输入/输出 Token。

Table 5 在 OB 上比较骨干模型：GPT-4.1-mini 的 AC@1/AC@3/MRR 为 74.4%/98.9%/0.854，32.7K Token、52.9 秒、每例 `$0.022`；Llama-4-Maverick 为 77.8%/97.8%/0.872，32.0K Token、37.4 秒、`$0.003`；GPT-4.1 的 AC@1 和 MRR 最高（78.9%、0.873），但每例 `$0.110`。这些是论文实验时的供应商费用，不代表当前价格。作者选 GPT-4.1-mini 作为复现默认值，并非只选最高准确率模型。（Table 5，PDF 物理页 10。）

与 Flow-of-Action 比较时，作者根据三次运行的逐事件多数结果做 McNemar 检验：OB 有 27 个事件仅 GALA+ 正确、4 个仅 Flow-of-Action 正确；TT 分别为 35 与 12；单侧 exact `p<0.001`。这支持这两个数据集上的配对差异，不等于对生产事故或所有 RCA 场景的普遍结论。（§5.3.1，PDF 物理页 8。）

### Phase 消融与 STRIX 消融

- **移除 STRIX：** AC@1 在 OB 从 74.44% 降至 35.56%，在 TT 从 73.33% 降至 68.89%。STRIX 的初始 Trace/结构信号贡献明显依赖数据集，在 OB 上差异更大。
- **仅保留 STRIX：** AC@1 为 OB 51.14%、TT 50.00%。STRIX 内部移除不稳定性后，AC@1 分别降至 18.18% 和 9.09%；移除中心性或影响力也会降低表现，但幅度较小。
- **独立移除 Phase III：** Figure 4 单独报告“GALA+ w/o Phase III”，即保留前面的候选生成/整合，但拿掉图引导的多模态 Agent 调查。作者称其使根因排名变差；图中分别展示 OB、TT 的 AC@1、AC@3 和 MRR。该图没有在柱上标注精确数值，正文也未给该消融的逐项数表，故不从柱高臆读精确百分比。与移除 STRIX 不同，它考察的是初始候选形成之后，局部证据调查能否修正/细化候选排序；两者作用阶段不同，不能把贡献合并成“图很重要”这一单一结论。
- **替换 Agent 的规则消融：** 在 OB 上，以 RRF 替代 Consolidation Agent 后，AC@1 从 74.44% 降至 63.33%、AC@3 从 98.89% 降至 96.70%、MRR 从 .854 降至 .790；以阈值计数替代 Evidence Synthesis Agent 后，AC@1 也降至 63.33%、MRR 降至 .790。结果支持这两个 Agent 超出简单聚合规则的作用，但主要来自单数据集消融，不能推广为所有任务上 LLM 推理都优于确定性规则。
- **邻居扩展：** TT 参数实验显示中等 k、约 `θ=.6`、`b=2` 较好。OB 的 30 个案例、五个随机种子子集上，随机邻居采样 AC@1/AC@3/MRR 为 `.76±.03/.97±.02/.87±.02`；按 STRIX 排序扩展为 `.72±.04/.98±.02/.85±.02`。作者认为重复利用 STRIX 排序可能放大已有偏差，随机扩展可增加局部多样性；该小子集不足以确定普遍最优策略。（Figure 4–5、Table 4，PDF 物理页 9–10。）

### SURE-Score、人工评分与统计单位

SURE-Score 评价**生成的事件说明和建议文本**，不是根因排名本身，也不是修复后恢复率。四个维度为：

1. **Evidence Groundedness：** 推理主张是否有可观察的指标、日志或 Trace 支持，是否出现无依据内容。
2. **Operational Feasibility：** 行动建议是否具体且在目标系统中可实施。
3. **Diagnostic Precision：** 是否明确服务/pod 和量化影响，而非泛化占位描述。
4. **Triage Logic：** 是否以连贯顺序从症状、关键证据推进到根因。

八位 Company A SRE（4–10 年经验）和四种 LLM 分别用 Think-Aloud 方法提出评价属性；Qwen3 合并去重，形成逐项 Yes/No checklist。每个案例的参考报告由已知故障 pod、故障类型、起始时间、系统说明及 SRE 示例提示 LLM 生成，再由 SRE 检查诊断和行动是否可信。Qwen3、Llama-4-Maverick 分别依据 checklist 评分，维度内正项再映射到 1–5。论文没有公开最终 checklist、映射/权重公式和完整 scorer，不能精确复现 SURE 分数。（Figure 3、§4，PDF 物理页 5–6。）

**Table 3 人工 SRE 评分（PDF 物理页 9，原图核验）：** 三位有生产事件响应经验的 SRE 对 `90 incidents × 3 methods × 2 datasets = 540` 份报告独立评分，使用相同四维度和 1–5 标尺；表中是平均结果。`E/O/D/T/F` 分别为 Evidence Groundedness、Operational Feasibility、Diagnostic Precision、Triage Logic、Final（前四维的总体均值）。

| 数据集 | 方法 | E | O | D | T | F |
|---|---|---:|---:|---:|---:|---:|
| OB | BARO+LLM | 2.3 | 2.1 | 2.3 | 2.8 | 2.4 |
| OB | Flow-of-Action | 3.1 | 1.4 | 3.4 | 2.4 | 2.6 |
| OB | GALA+ | 4.2 | 4.4 | 4.6 | 4.5 | 4.4 |
| TT | BARO+LLM | 2.3 | 2.0 | 2.4 | 2.8 | 2.4 |
| TT | Flow-of-Action | 2.8 | 1.5 | 3.3 | 2.5 | 2.6 |
| TT | GALA+ | 3.8 | 4.6 | 4.4 | 4.0 | 4.2 |

作者报告 Qwen3 与 Llama-4-Maverick 的 pooled 评价相关系数为 Kendall `τ=.68`、Spearman `ρ=.84`（均 `p<.001, n=50`）；自动平均分与人工评分相关 `ρ=.92 (p<.001,n=20)`。**统计单位没有被充分定义：** 文中未解释 n=50、n=20 各自对应报告、方法×数据集×维度、评审聚合值还是其他样本构造。它们不能误读成 540 份报告或 540 名独立评分观察；Table 3 也只是聚合后的方法/数据集均值。因而这些相关性可作为作者报告的聚合评分一致性信号，但其独立观测单位和统计不确定性目前不能复算。

人工表中 Flow-of-Action 的 Operational Feasibility 只有 1.4–1.5。作者说明 Flow-of-Action **不输出修复建议**，所以在“建议是否可执行”维度天然缺少可得分内容，而 GALA+ 输出三层建议并超过 4.0。这揭示的是完整任务交付能力差异，若任务要求给出建议，这是有意义的端到端比较；但它并不能单独证明两者在“都生成建议”的前提下，GALA+ 的建议更可行。该评分差异将能力覆盖与输出质量混合在一起，应在解读跨系统质量排名时说明。（§§5.3.2–5.3.3，PDF 物理页 8–9。）

自动评分的绝对刻度也有明显差异：GALA+ 在 OB/TT 上，Qwen3 的 Final 为 3.3/3.0，Llama-4-Maverick 为 4.5/4.4；Evidence Groundedness 分别为 1.8/1.4 与 5.0/4.9。作者称 Qwen3 更偏好明确引用遥测数值，Llama 会接受转述。三位 SRE 的 Table 3 评分方向上支持 GALA+ 较高，但没有逐位评分或评分者间一致性数据供复核。作者还指出 checklist 由单一组织 Company A 的 SRE 与模型共同设计，存在跨组织泛化限制；跨组织、不同运维规程和不同故障类型下的构念效度仍待验证。（§7，PDF 物理页 11。）

### AegisLab 结果的命名差异

主文称在抽样的 100 个 AegisLab 案例上比较 GALA+ 与 Flow-of-Action：MRR 为 `.48` 对 `.38`，AC@3 为 `.62` 对 `.52`；AC@1 为 `30/100` 对 `28/100`，差异不显著。仓库的一页补充技术报告也报告 `30/100` 对 `28/100` 并称 AC@1 差异不显著，但表格方法行标为 **GALA** 而非 GALA+。在作者澄清前，不能把它作为 GALA+ 变体的确定性证据；它也不能证明系统已解决并发或开放集故障。（主文 §5.3.4，PDF 物理页 10；补充技术报告物理页 1。）

## 官方公开材料的静态分析

官方仓库 README 表示，受工业协议限制，GALA 核心代码无法公开。commit `24d1329d20fb9139f7899a1bed9e8d0bdaf00be0` 包含技术报告、标注数据、样例输出和第三方基线，但没有 GALA runner、核心实现、SURE-Score evaluator/scorer 或 Flow-of-Action 实现。本次没有运行代码，也没有下载 Benchmark 数据集。

- `sample_output/ts-order-service_cpu_1.json` 展示初始指标排名的输出形状。
- `sample_output/ts-order-service_cpu_1_STRIX_output.json` 包含各服务 RRF 分数、三个指标值和序位排名。
- `sample_output/ts-order-service_cpu_1_history_2026-02-27_00-18-33.json` 保存分支候选、深度、置信度、证据摘要、因果说明和支持/反驳因素。
- 对应的 `..._summarization_recommendation_...json` 保存事件摘要和三条建议。样例与 Figure 6 的 order-service CPU 案例相符，但样例 JSON 不能验证实现或 scorer。
- `annotation_guidelines.md` 要求生成参考说明和建议，并举例要求“模拟预期影响”的 CPU/延迟/错误数值。若这类量化数字未逐条用原始遥测复核，可能引入无证据细节；论文称 SRE 会审阅参考报告，但公开材料没有行级审计轨迹。
- 仅抽查 `data/annotated_dataset.csv` 前五行时，观察到 RE2 记录的列标为 Sock Shop/checkoutservice，而摘要写成 Train Ticket。这是有限抽查到的材料不一致，不代表对全数据集的审计结论。
- 仓库顶层 MIT 许可适用于公开 artifacts；vendor 的基线保留各自许可。公开材料不能证明论文中内部 Agent、阈值或评分代码与正文完全一致。

## 局限与解读

**作者说明的局限：** 受控注入与预定义故障不能代表并发或复杂生产故障；系统依赖三种遥测模态；Prompt 需要适配数据集 schema；成本随候选服务和扩展调查增加。未来工作包括并发多故障诊断和更好的证据 grounding。（§§7–9，PDF 物理页 11。）SURE-Score checklist 由 Company A 单一组织参与设计，也限制跨组织泛化。

**基于阅读的推论，不是作者已验证结论：**

- GALA 文中把 BARO 描述为因果 DAG，但被引 BARO 原论文呈现的是 Multivariate BOCPD + RobustScorer；缺少核心代码使该方法差异无法定因。
- STRIX 图表达调用依赖；中心性、延迟尾部和 self-time 启发式本身都不是因果识别。
- Agent 置信度控制分支停止，但没有校准说明。Figure 6 的 station-service 局部分支置信度 0.85 仍被最终判为假阳性；全局综合机制因此很关键。
- SURE-Score 引入人工设计与复核，但报告的相关性 n 的统计单位未说明；单组织 checklist、不可得 scorer 和 grader 绝对刻度差异限制独立复现。
- AC@k/MRR 评价 pod 排名，不评价 pod+fault type 的完整任务目标；文本质量评价又不同于真实故障修复及恢复验证。
- Flow-of-Action 缺少建议输出会影响 Operational Feasibility 比较。该结果可说明任务交付范围差异，不能等同于同类建议质量的纯比较。
- OB/TT 是受控注入场景；AegisLab 样例较广，但只有 100 个样本，且公开材料存在 GALA/GALA+ 标签差异。

## 与 OpsAgent 相关研究的关系

- **KRCA：** 两者都用拓扑缩小搜索；GALA+ 先融合指标/Trace 排名，再用局部多模态调查；KRCA 则用因果骨架和专门执行模块分阶段排查。
- **ToolRCA：** 两者关注受限调查与证据，但 ToolRCA 结果提示工具/query 设计会与模型能力交互。GALA+ 未公开完整 Prompt/工具，无法做直接复现实验对比。
- **OpsAgent、OpsMem：** GALA+ 的共享 `M` 是单次事件内的临时调查状态，不是跨事件持久运维记忆或技能学习。
- **Graph of States：** 两者都有支持/反驳线索和综合步骤；GALA+ 未报告显式的 belief 生命周期，或新证据推翻分支后的回溯机制。
- **KnowLution、FlowXpert：** GALA+ 给 SRE 处置建议，但未展示权限检查、动作执行或恢复闭环。

GALA+ 位于静态排名与开放式工具 Agent 之间：它用拓扑局部调查补充排序，但尚不是经验证的自治修复系统。

## 对 Network AIOps 的启发

- 将候选生成和证据调查分开；以可追溯来源融合指标与 Trace，而不是把不同模态压成无来源单分数。
- 用物理/逻辑拓扑限制候选扩展，但保留方向、替代路径、支持与反证；网络邻接不能直接视为因果。
- 维持证据原生结构，并让每条诊断主张绑定时间窗和来源记录。
- 分别评价诊断、报告质量、建议安全性与实际恢复；不以文本看似可行代替执行效果。

尚不能直接迁移的做法包括：在网络拓扑上使用微服务 PageRank 入/出度假设、基于服务 Trace 的 self-time 拆分、单故障注入标签，以及在微服务场景上评分的修复建议。

## 开放问题

1. 服务级节点、pod 级根因标签和最终故障类型输出如何映射？
2. Consolidation/Investigator 的置信度如何生成与校准？Prompt 如何约束判断？
3. 核心实现的实际扩展是否严格遵循 Algorithm 1 所示的一跳邻居？
4. BARO 原论文与 GALA 对 BARO 的因果 DAG 描述差异，是否源于 GALA+ 改版或论文方法描述问题？核心源码未公开，暂不能判断。
5. SURE-Score 最终 checklist、计分映射和 scorer 是什么？其 `n=50`、`n=20` 的相关性统计观察单位如何构成？
6. Flow-of-Action 没有建议输出时，如何设计能区分能力覆盖与建议质量的公平评分？
7. 单一 Company A 参与设计的 checklist 能否迁移到其他组织、SRE 群体和处置规范？
8. 为什么补充 AegisLab 表把方法记为 GALA，而主文写 GALA+？
9. 公共参考报告中的服务名不一致和“模拟预期影响”数值是否已用原始遥测逐条核对？
10. 缺失 Trace/日志、循环依赖、多根因或未知故障类型下表现如何？安全执行建议是否实际缩短 MTTR 并改善恢复？

## 原文定位索引

| 内容 | 原文定位 |
|---|---|
| 问题、贡献、根因定义 | Abstract、§§1–2，PDF 物理页 1–2 |
| 四阶段架构 | Figure 2，PDF 物理页 3 |
| GALA 对 BARO 的描述；STRIX 分数 | §3.1，PDF 物理页 3–4 |
| 原始 BARO 方法 | [BARO arXiv:2405.09330v1](https://arxiv.org/abs/2405.09330)，§§3.3–3.4、Algorithm 1 |
| 遥测上下文组织 | §3.2，PDF 物理页 4 |
| 图引导调查与最终综合 | §§3.3–3.4、Algorithm 1，PDF 物理页 4–5 |
| SURE-Score 构造 | Figure 3、§4，PDF 物理页 5–6 |
| 数据、基线、模型、指标 | §§5.1–5.2，PDF 物理页 6–7 |
| 排名与 SURE 结果 | Tables 1–3，PDF 物理页 8–9 |
| Phase/STRIX 消融 | Figure 4、Table 4，PDF 物理页 9 |
| 模型、成本、参数与个案 | Table 5、Figures 5–6，PDF 物理页 10 |
| 有效性威胁与数据可用性 | §§7–9，PDF 物理页 11 |
| 公开 artifacts | 仓库 README、`annotation_guidelines.md`、`data/annotated_dataset.csv`、`sample_output/`，commit `24d1329d20fb9139f7899a1bed9e8d0bdaf00be0` |

## 标签

AIOps · OpsAgent · 微服务 RCA · Metrics/Logs/Traces · 服务依赖图 · STRIX · Agentic Diagnosis · SURE-Score · Incident Response · Evidence Grounding
