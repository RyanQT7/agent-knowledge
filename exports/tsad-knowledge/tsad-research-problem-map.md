# TSAD 研究问题地图：33 篇论文中的已有路线与证据边界

## 范围与阅读方式

本地图依据 33 篇精读笔记、知识档案及批次 Review v3–v13 整理。它归纳的是本集合中的证据，不声称穷尽 TSAD 文献。不同论文的数据、异常标签、阈值、切分与指标并不统一，不能把各自分数拼成同协议排行榜。

- **作者主张**：作者提出的问题、机制或解释。
- **实验支持**：论文实际报告的数据、对比、消融或失败案例；结论限于该设置。
- **跨论文分析**：本知识库的综合解释和可证伪研究假设，不是论文已证明的事实。

每个链接指向随本文件一起打包的独立知识档案。档案第 13 节列出 PDF 文件名、章节、页码、公式和表图定位；本地图不依赖服务器内 PDF 才能理解主要结论。

## 1. 多种正常状态建模

**已有工作与方案**

- [MACE](knowledge-dossiers/mace.md) 在服务级别筛出常见 Fourier bases，构造服务条件的频域正常子空间；它主要处理服务间差异。
- [CAPMix](knowledge-dossiers/capmix.md) 以训练窗的均值中心和 DTW 距离修订合成异常标签；单中心能处理形态距离，但并不是显式的多业务状态库。
- [CrossAD](knowledge-dossiers/crossad.md) 用粗到细尺度关系、子序列 query 和 EMA 原型表示不同时间片段的常见形态；[Graph-MoE](knowledge-dossiers/graph-moe.md) 以多层图专家与潜在 memory routing 表示实体间及历史依赖。
- [CAROTS](knowledge-dossiers/carots.md) 用因果保持增强产生数值不同但关系一致的正例；[TeamWork](knowledge-dossiers/teamwork.md) 按 ERI 统计量拆分 dominant / auxiliary 通道；二者分别描述关系变化和变量角色，并未给出带业务名称的运行状态分类器。
- [When Model Meets New Normals](knowledge-dossiers/when-model-meets-new-normals.md) 对测试流中的预测正常点做在线适配；[TimeRCD](knowledge-dossiers/time-rcd.md) 和 [VLM4TS](knowledge-dossiers/vlm4ts.md) 用同序列上下文比较目标片段；[Conditional Normalizing Flows](knowledge-dossiers/cnf-latent-dynamics.md) 则把正常性写成规定的潜变量动态统计假设。

**实验支持与边界**

这些工作各自报告基准性能、组件消融或新模式 / context 相关实验，支持相应机制能改变检测分数或特定设置下的指标。它们没有共同验证：被学到的 prototype、memory、频谱或 latent dynamics 是否对应已核实的 workload、发布、租户或业务时段。WMMNN 的伪正常更新、TimeRCD 的 context 污染风险、TeamWork 的静态 role、MACE 的静态服务基和 CNF 的归纳偏置匹配条件均见相应档案方法与局限章节。

**尚未充分解决的问题**

多原型、适配、相对上下文和动态分布已经是已有路线，不能把“首次建模多正常性”笼统宣称为空白。更具体的证据缺口是合法低频状态的误报安全、未见但合法状态迁移、状态变化与故障并发时的检测召回，以及在线更新是否把漏检故障吸收到 normal memory。

**跨论文分析假设**

在按时间隔离的实验中，分别留出常见正常态、罕见正常态、未见合法状态、仅故障、状态切换加故障五类测试段。如果状态条件化记忆确实提升多正常态覆盖，应在降低每状态误报的同时保持并发故障召回，并且不会随状态频率降低而系统性恶化。需报告每状态 FPR、故障召回、检测延迟和 memory 更新前后误差。

## 2. 正常业务波动与真实故障区分

**已有工作与方案**

- [CAROTS](knowledge-dossiers/carots.md) 的作者动机明确区分“变量值变了但关系仍正常”和“关系受损”；CPA 生成因果保持正例，CDA 生成因果破坏负例。
- [When Model Meets New Normals](knowledge-dossiers/when-model-meets-new-normals.md) 以测试时适配降低新正常导致的偏差；它依赖模型预测正常的伪标签。
- [MACE](knowledge-dossiers/mace.md) 按服务正常频率模式建立参照；[CAPMix](knowledge-dossiers/capmix.md) 以 KPI 形态、DTW 和合成扰动训练分类边界。CAPMix 的 Kuaishou 案例报告对日志轮转、采集扰动等监控伪影与 memory leak 等持续故障的不同响应。
- [COGNOS](knowledge-dossiers/cognos.md) 用 residual null / NIS 检测统计结构改变；[CNF latent dynamics](knowledge-dossiers/cnf-latent-dynamics.md) 检验 whitened latent 是否符合规定动态；这些方法检测相对统计参照的偏离。

**实验支持与边界**

CAROTS 在合成因果系统、真实基准和模块消融中展示结构化增强的作用；CAPMix 的线上案例提供操作性示例；COGNOS / CNF 展示统计假设拒绝的检测证据。这些证据并未构成统一的业务状态标签与故障真值对照。偏离训练分布、预测关系、白噪声 null 或 latent law 可以表明变化，却不能单独证明变化来源是故障而不是合法负载 / 发布 / 扩缩容。

**尚未充分解决的问题**

没有系统的正常状态切换、单独故障、状态切换加故障并发矩阵，也缺少将 Metric 异常分数与真实 incident、Trace 路径或发布事件进行来源归因验证的统一协议。CAPMix 案例是有价值的生产证据，但不能代表 33 篇论文均已验证业务语义区分。

**跨论文分析假设**

建立受控四格评估：正常稳定、仅合法状态切换、仅故障、状态切换加故障；再按负载强度和故障起始时间做分层。比较纯数值 detector、关系 detector 和上下文条件模型，并同时报告固定 validation FPR 下的并发故障召回、告警延迟、误报持续时间和状态识别准确性。若只提升 aggregate F1 而并发故障召回下降，不能称为解决了波动 / 故障区分。

## 3. 噪声与异常数据污染

**已有工作与方案**

- [CAPMix](knowledge-dossiers/capmix.md) 针对合成异常与真实异常的 Anomaly Shift，用 CutAddPaste、DTW label revision 和 dual-space Mixup；[IMPACT](knowledge-dossiers/impact.md) 用 validation-risk influence 处理标签污染与 open-set anomaly。
- [PCRTA](knowledge-dossiers/pcrta.md) 用多种人工扰动和伪标签对比表示；[Fortifying Time Series](knowledge-dossiers/fortifying-time-series.md) 给出针对 DTW 威胁集合的随机平滑认证；两者威胁模型不同。
- [COGNOS](knowledge-dossiers/cognos.md) 将 MSE residual 约束为近 Gaussian white noise，再用 ARKS / NIS 处理背景噪声；[KAN-AD](knowledge-dossiers/kan-ad.md) 用 Fourier 平滑函数抑制不规则局部波动；[IGAD](knowledge-dossiers/idempotent-reconstruction.md) 以幂等一致性和 target-manifold tightness 约束重建。

**实验支持与边界**

CAPMix 报告合成污染强度测试和生产案例；IMPACT 报告多污染 / open-set 设置；Fortifying 报告指定 DTW 半径下的证书与覆盖率；PCRTA、KAN-AD、IGAD 使用各自设计的扰动 / 污染实验；COGNOS 报告多 backbone 与模块消融且不同指标有回退。认证稳定不等于原预测正确，合成扰动覆盖不等于真实故障覆盖，某指标整体提升也不等于所有威胁均鲁棒。

**尚未充分解决的问题**

不同工作采用不同污染比例、扰动类型、时间扭曲、阈值与指标，难以比较鲁棒程度。异方差、跨变量相关噪声、数据采集故障、合法状态漂移及稀有正常状态未在同一个协议下评估。

**跨论文分析假设**

用共同数据切分，分别控制测量噪声、异方差、相关噪声、时间扭曲、训练标签污染、状态漂移和稀有正常态；报告每个威胁下的检测指标、固定误报预算表现、阈值稳定性和计算成本。将 certified invariance 与经验鲁棒结果分列，不把不同威胁下的“鲁棒”合并成单一标签。

## 4. 分布漂移与新正常状态

**已有工作与方案**

- [When Model Meets New Normals](knowledge-dossiers/when-model-meets-new-normals.md) 是本集合中直接面向 test-time new normal 的代表：EMA 去趋势加上预测正常点筛选的参数更新。
- [IMPACT](knowledge-dossiers/impact.md) 研究少量已知异常监督下的 open-set 检测与标签污染；[TimeRCD](knowledge-dossiers/time-rcd.md) 以合成上下文差异预训练零样本 detector；[VLM4TS](knowledge-dossiers/vlm4ts.md) 由同一序列窗口提出候选并用全局视觉语言模型核验。
- [MACE](knowledge-dossiers/mace.md) 的服务条件频率基、[TeamWork](knowledge-dossiers/teamwork.md) 的静态通道角色、[CNF](knowledge-dossiers/cnf-latent-dynamics.md) 的规定 latent dynamics 代表不同静态或显式参照；它们不等同在线状态迁移处理。

**实验支持与边界**

WMMNN 展示测试时适应在其选择的分布漂移场景中改善检测并报告趋势 / TTA 消融；其核心风险是错误伪正常样本污染更新。IMPACT 的污染标签与 unseen 设置支持所提 open-set 方案在相应基准下的结果；TimeRCD 的 contextual synthetic split 支持其特定上下文任务；VLM4TS 的 benchmark 结果不证明稠密异常、业务 metadata 或真实服务迁移场景同样适用。

**尚未充分解决的问题**

新正常并不总是可由 anomaly score 低的点安全识别；长期遗忘、回滚、故障吸收、持续漂移与突发切换尚缺统一比较。统计或模型适配后的“分数下降”也不等于系统正确识别出一个合法业务态。

**跨论文分析假设**

在连续在线流中按阶段安排正常状态切换、未知合法状态、短暂故障、长期故障与故障恢复；仅允许模型按其原文规则更新。记录每次更新的候选比例、故障样本被纳入 normal memory 的比例、回滚代价和跨状态误报。对比冻结、趋势归一化、WMMNN 式更新、open-set 和外部状态条件化方案。

## 5. 上下文感知异常检测

**已有工作与方案**

- [MACE](knowledge-dossiers/mace.md) 使用 service identity 选择服务级正常频率 bases；这是实体条件，不是实时业务负载上下文。
- [When Model Meets New Normals](knowledge-dossiers/when-model-meets-new-normals.md) 使用当前测试流趋势和预测正常 mask；[TimeRCD](knowledge-dossiers/time-rcd.md) 用同序列时间 / 跨变量相对关系；[VLM4TS](knowledge-dossiers/vlm4ts.md) 使用同序列其他窗口的图形上下文。
- [Delving into LLMs for TSAD](knowledge-dossiers/delving-llm-tsad.md) 将数值和图像转为 index-aware prompt，并试验有限文字背景；[AnomSeer](knowledge-dossiers/anomseer.md) 输出类别、区间与 reasoning trace，但生成解释需独立验证忠实性。

**实验支持与边界**

上述实验分别支持服务条件、当前数值流或构造文本 / 视觉提示对所测 benchmark 的影响。当前证据不等于在真实生产中使用了完整的 workload、版本发布、租户、服务拓扑或 span 级上下文，也没有统一评估上下文错误、缺失和延迟到达时的安全行为。

**尚未充分解决的问题**

contextual anomaly 的模型内部相对上下文，与业务外生 context 是不同信息源。把同一序列其他片段、语言模型提示或实体 ID 称为“上下文感知”，不能据此推断模型解释了负载 / 发布引起的变化。

**跨论文分析假设**

将外生 context 分层注入：只用 Metric、Metric + workload、Metric + release、Metric + Trace、全量组合；再分别做 context 缺失、错误、时间错位与跨环境迁移。检验条件化模型是否在合法状态切换时降低误报，同时不遮蔽同一切换期间的真实故障，并单独测量 context 来源归因的正确率。

## 6. 多指标关系与因果结构

**已有工作与方案**

- [CAROTS](knowledge-dossiers/carots.md) 通过 Granger 预测图生成因果保持 / 破坏增强，并融合 embedding 距离与因果预测残差。
- [GCAD](knowledge-dossiers/gcad.md) 用 forecasting loss 对输入的梯度作为 Granger predictive-influence proxy；[OracleAD](knowledge-dossiers/oraclead.md) 组合逐点残差和 contextual structural deviation；[SARAD](knowledge-dossiers/sarad.md) 关注前后半窗 association progression。
- [CCM-TAD](knowledge-dossiers/ccm-tad.md) 用静态 channel profile clusters 和 causal temporal mask；[Graph-MoE](knowledge-dossiers/graph-moe.md) 组合多层关系专家和 memory routing；[TeamWork](knowledge-dossiers/teamwork.md) 以 ERI 统计变量角色分支；[ScatterAD](knowledge-dossiers/scatterad.md) 的图节点是时间点及其滞后关系。

**实验支持与边界**

论文报告关联、结构异常或组件消融结果；CAROTS 还用合成因果系统作受控评估。各方法的 causal / graph / dominant 表述对象不同。预测性 Granger 关系、attention、latent graph、变量互信息或时间滞后图本身不是物理服务拓扑、干预因果或根因证明。多数工作缺少真实 topology、Trace path 或 fault injection ground truth 的忠实性评估。

**尚未充分解决的问题**

状态条件化因果结构、外生混杂、反馈环、共同驱动和关系随合法工况变化等问题尚缺充分证据。关系分数可帮助发现结构变化，但未自动回答“哪个服务故障导致了哪些 KPI 变化”。

**跨论文分析假设**

在已知服务拓扑与可控 fault injection 的系统中，同时记录模型学到的变量关系、真实调用路径和干预目标；分开评估异常检测、边 / 路径恢复和根因排序。更换 workload 与发布状态后，测试结构是否稳定或应条件化；报告边精确率、top-k cause、跨状态稳定性与 detection delay。

## 7. Metric、Trace、Log 多模态检测

**已有工作与方案**

- 本集合的绝大多数方法以单变量或多变量数值序列为输入。 [CAPMix](knowledge-dossiers/capmix.md) 和 [MACE](knowledge-dossiers/mace.md) 与云服务 KPI / metrics 场景联系最直接。
- [AnomalyLLM](knowledge-dossiers/anomalyllm.md) 将冻结 LLM 表征作为时序 teacher；[Delving](knowledge-dossiers/delving-llm-tsad.md)、[AnomSeer](knowledge-dossiers/anomseer.md) 与 [VLM4TS](knowledge-dossiers/vlm4ts.md) 使用文本、图像或多模态模型，但其模型输入形式不自动等于生产 Metric–Trace–Log 联合观测。
- [TimeRCD](knowledge-dossiers/time-rcd.md) 的 synthetic contextual labels 主要表示时间和跨变量关系，与真实 Trace/span 语义不同。

**实验支持与边界**

这些论文分别报告 numeric benchmark 上的 teacher 表征、prompt、视觉候选或合成训练收益。综合笔记未发现对真实 Metric、分布式 Trace/span、Log 模板、release 事件和 service topology 做同一时间轴对齐并验证因果来源的统一实验。这里的结论限于本 33 篇范围。

**尚未充分解决的问题**

跨模态对齐、采样频率不一致、缺失模态、日志高基数、Trace 成本与延迟、以及同一 incident 下证据冲突，均不是现有单一 benchmark 分数可以回答的。将数值图像输入 VLM 也不应误记为已融合真实运维多模态数据。

**跨论文分析假设**

以事件时间为基准建立 Metric–Trace–Log 数据集，比较各模态单独、两两、全量融合和模态缺失设置；用 incident / release / injected fault 标签分开测检测、服务定位和原因解释。做跨环境留出，避免同一 incident 的近重复样本跨训练与测试。

## 8. 数据异常与业务异常

**已有工作与方案**

- [TSB-AD](knowledge-dossiers/tsb-ad.md) 与 [Quo Vadis](knowledge-dossiers/quo-vadis.md) 研究数据集质量、标签、指标、阈值和评测协议，提醒 benchmark label 与检测分数不是无误的业务真值。
- [CAPMix](knowledge-dossiers/capmix.md) 的生产案例讨论采集扰动、日志轮转、负 CPU 等监控伪影与持续 memory leak 故障；[COGNOS](knowledge-dossiers/cognos.md) 把异常证据定义在 reconstruction residual 的统计结构上。
- 其它检测器多以分数偏离训练参照作为 anomaly evidence，没有显式输出“数据采集错误 / 监控系统故障 / 业务服务故障”的分层分类。

**实验支持与边界**

TSB-AD 对 benchmark 数据进行人工与算法辅助检查并分析指标偏差；CAPMix 案例给出具体监控伪影案例。这些结果支持需要检查数据与标签质量，也说明某些异常分数可对监控伪影有不同响应；但没有在 33 篇范围内形成跨论文统一的数据质量异常 vs 业务故障分类基准。

**尚未充分解决的问题**

无效传感器、采集缺口、时钟漂移、Metric exporter 改版和真实服务性能退化可能同时出现。若数据质量变化污染输入，单纯提升 detector 对数值异常的分数，不一定能判断告警对象应归给监控链路还是服务本身。

**跨论文分析假设**

建立分层标签：measurement / instrumentation issue、合法业务状态变化、服务故障、混合事件；分别注入单一与并发事件，比较 CAPMix / residual null / relation / context 方法。评价需要区分检测命中、问题所属层级和来源解释正确性，不能只报点级 F1。

## 9. 故障导致的服务性能退化

**已有工作与方案**

- [CAPMix](knowledge-dossiers/capmix.md) 直接面向 AIOps KPI，并报告一项 Kuaishou KAIOps 集群系统案例；其输入包含 CPU、内存、I/O、网络、API latency、pending tasks 和 pod restarts 等 KPI。
- [MACE](knowledge-dossiers/mace.md) 面向云服务、机器和传感器子集，按服务 normal spectrum 建模；[CAROTS](knowledge-dossiers/carots.md)、[GCAD](knowledge-dossiers/gcad.md)、[OracleAD](knowledge-dossiers/oraclead.md)、[SARAD](knowledge-dossiers/sarad.md) 等从多变量关系侧提供可能用于服务性能退化分析的数值证据。
- [FlowFuse](knowledge-dossiers/flowfuse.md)、[COGNOS](knowledge-dossiers/cognos.md) 与 [CNF](knowledge-dossiers/cnf-latent-dynamics.md) 分别融合多个 detector score、检验 residual 统计假设或 latent dynamics；检测输出本身仍不等于服务影响范围和故障根因。

**实验支持与边界**

CAPMix 的生产案例报告事件级指标和运维伪影对照，是本集合直接运维证据之一；MACE 报告云服务 / 多实体数据实验。其它工作大多在公开 benchmark、合成数据或数值序列上验证。没有充分证据说明这些检测机制已可靠量化用户影响、传播路径、SLO 违约或服务退化根因。

**尚未充分解决的问题**

检测一个 KPI 的变化与评估服务是否受影响并不相同。缺少将异常时间、服务依赖路径、请求 / span 延迟、错误率、部署事件和业务损失共同对照的系统研究；缺少正常负载增长与资源瓶颈故障并发的标准场景。

**跨论文分析假设**

围绕服务级 incident 构建时间对齐的 KPI、Trace、拓扑、发布和 SLO 数据；将检测、影响服务定位、根因候选、影响用户范围分别作为任务。比较数值-only、图关系、运行上下文和多模态方法，并用独立 incident review 或故障注入核验归因。统一报告告警延迟、SLO 影响覆盖、top-k 根因和误报成本。

## 证据结论汇总

| 问题 | 33 篇范围内的状态 | 有证据的结论 | 仍需补充的证据 |
| --- | --- | --- | --- |
| 多种正常状态如何建模？ | 部分回答 | 多原型、频谱基、online adaptation、上下文参照、变量角色、残差 null 与 latent dynamics 均已提出。 | 业务状态语义、rare-normal 安全、状态切换加故障并发、memory 更新污染。 |
| 正常波动如何与故障区分？ | 未解决 | 已有值、关系、频谱、重建、统计和相对 context 多类偏离证据；CAROTS 与 CAPMix 提供针对性动机 / 案例。 | 统一状态与故障真值矩阵、真实上下文因果归因。 |
| 方法是否只是在抑噪？ | 部分回答 | 多数路线利用关系、频域、多视角、open-set 或 latent dynamics，而非只做平滑。 | 更丰富的偏离证据是否解释变化来源，尚未由外部 cause ground truth 普遍验证。 |
| 是否使用真实 Metric、Trace、Log？ | 未解决 | KPI / 数值时序是主流；少量工作使用 service ID、prompt、图像或合成 context。 | 真实 Metric–Trace–Log–release 联合对齐与缺失 / 错误模态实验。 |
| 如何处理状态切换与故障同时发生？ | 未解决 | 有新正常适配、关系保持增强和 open-set 路线。 | 缺统一并发矩阵、固定 FPR、per-state recall 与恢复时间评测。 |
| 哪些结论是研究假设？ | 待验证 | 文中各假设均标为跨论文分析，并附可执行对照实验。 | 实验结果出现前，不应宣称这些方案已有效或研究空白已经被填补。 |

更宽的技术比较见 [完整论文总览](tsad-33-paper-knowledge-overview.md)；逐篇方法、实验和页码证据见 [完整合并档案](tsad-33-paper-knowledge-full.md)。
