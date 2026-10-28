# LLM 微服务异常生成与 Metric–Trace 联合建模：最小验证实验计划

## 1. 实验目标与先决条件

本计划用小规模、受控、可复现的实验检验三件事：

1. 正常业务负载上涨是否能在服务健康的前提下造成显著 KPI 变化；
2. 同一负载下添加真实故障时，Metric 与 Trace 是否出现能被独立确认的服务退化信号；
3. LLM 规划或由其引导的数据增强，是否比规则 / 模板增强提升真实故障检测，同时不增加健康高负载误报。

本次只设计，不启动训练、GPU 或故障注入。开始实施前需确认数据 schema、测试环境授权、隔离性、观测覆盖和事件标注能力。知识库目前没有国网项目 Metric / Trace 数据字典，因此本计划不假定该数据一定包含服务 ID、span 结构、故障标签或业务负载字段。

## 2. 数据要求与事件 schema

### 必须具备或可在测试床补采的字段

| 类别 | 最低字段 / 属性 | 用途 |
| --- | --- | --- |
| Metric | timestamp、canonical service / instance、metric name、value、unit、sampling interval | 窗口化、服务映射、负载分层 |
| Trace | trace ID、span ID、parent span ID、service / instance、start / end 或 duration、status / error | 请求级延迟、错误和拓扑链分析 |
| Topology | 服务节点、允许调用边、版本 / 生效时间 | span 合法性与故障传播路径 |
| Workload | 请求量 / 到达率、请求类别或业务 mix、时间计划 | 配对健康 / 故障负载条件 |
| Health oracle | 端到端交易成功率、错误率、可用性和 latency SLO / 探测器 | 确认正常或观察到退化 |
| Action / incident | fault type、目标服务 / 实例、注入成功状态、start / end、执行器日志 | 根因和注入标签 |
| Observability | Trace sampling rate、采集缺失、时间同步 / skew 信息、schema 版本 | 评估 Trace 证据质量及对齐误差 |

所有样本应记录数据来源和 split group。使用事件级或 incident 级切分，不能把同一 incident 中相邻重叠窗口随机分到训练和测试。

## 3. 最小情景矩阵

设计四类必选情景，并为需求变化和健康状态分别打标签：

| ID | 业务需求 | 故障动作 | 期望事件标签 | 对照要点 |
| --- | --- | --- | --- | --- |
| N0 稳定健康 | 固定或低波动的 baseline workload | 无 | demand_shift=0；action=0；degradation=0 | 基础正常分布 |
| N1 健康负载上涨 | 逐级增加请求量 / 改变业务 mix | 无 | demand_shift=1；action=0；degradation=0，只有当健康 oracle 通过才成立 | 观察 KPI 变化但事务与 SLO 保持健康 |
| F1 下游调用延迟 | 与 N1 相同 workload / 请求种类 | 在下游目标服务注入延迟 | demand_shift 与 N1 匹配；action=1；degradation 按 oracle 确认 | 形成相同负载下的 matched healthy / fault pair；观察下游和上游 span / latency |
| F2 资源竞争 | 与 N0 或 N1 匹配的 workload | CPU / memory / I/O 资源竞争 | action=1；degradation 另行确认 | 区分资源压力与高请求量造成的平滑增长 |
| F3 下游 timeout / error propagation | 与 N1 匹配的 workload | 注入 timeout / 网络错误 / 下游错误 | action=1；degradation 另行确认 | 检查下游错误、重试 / span 状态和上游 error / latency 变化 |

表中的四个必选故障类型是用户指定的最小覆盖范围；稳定健康和健康负载上涨是必要负样本。F1、F3 尽量对同一 workload 与调用类型复现实验，形成 paired episode。若环境无法完全相同，应记录请求速率、请求 mix、版本、拓扑、运行时状态等差异，并把差异纳入分析。

### 健康和故障标签不要混为一类

- “无注入动作”不自动等于健康：高负载可能使系统自然过载。
- “注入成功”不自动等于故障影响真实发生：目标动作可能被隔离、无效或被重试掩盖。
- 因此至少维护三个标签：需求变化、注入动作、观察到的服务退化。
- N1 只有在交易探针成功率、服务 SLO 和系统健康检查通过时才可标成健康波动；若负载上涨导致 SLO 违规，应归为真实性能退化 / 过载，而不能当作正常负样本。
- 故障样本要同时记录动作是否执行、目标范围、时间、用户可见影响和是否达到预设退化标准；对“执行了但没有可见影响”的事件保留独立类别。

## 4. 样本构造及 Metric–Trace 对齐

1. 先运行干净 baseline，记录版本化拓扑、Metric / Trace schema、实例映射、事件时间和 workload。
2. 选取未发生故障且健康 oracle 通过的背景片段；相邻窗口按 incident / run 分组，避免跨 split 复用背景。
3. 对 N1、F1、F3 配对安排 workload：同一请求曲线和请求 mix 条件下，一轮不注入，另一轮在随机化的时间点注入故障。F2 同样在匹配 workload 下执行。
4. 保留原始事件时间。不要先按各模态独立切分再强行配对。Metric 按其原采样率保留；Trace span 按统一的服务和窗口聚合，窗口宽度由检测延迟目标和实际采样频率确定，并在验证集选择。
5. 保存实例到服务的版本化映射、trace sampling rate、缺失值 mask 和 clock-skew 测量。若无法对齐实例层级，则只在服务层评估并声明粒度损失。
6. 以预注册的 deterministic validator 检查 ID 唯一、父子 span、拓扑边、start/end、故障时间和 Metric 聚合区间。使用容差解决跨主机 clock skew。
7. 统计一致性分数按 service × workload × fault family 分层计算，避免把条件相关性写成普遍规则。对低 Trace 覆盖、高丢失或低请求量事件单独分析。

## 5. 生成器与检测器基线

为确认每个部件的增量贡献，使用固定的下游 detector 结构和训练预算：

### 数据生成 / 增强 baseline

1. **No augmentation**：只用原始可用训练事件。
2. **Rule / template generation**：非 LLM 规则计划器 + 规则注入器；是核心强 baseline。
3. **LLM planner + same rule executor**：与 baseline 使用同样知识、allowlist、执行器和预算，仅替换计划器；这是识别 LLM 边际价值的关键比较。
4. **CAPMix**：KPI 形态增强、DTW 伪标签可信度和 mixup，作为现有 AIOps KPI 增强路线。
5. **GenIAS**：TCN-VAE 潜空间扰动与变量级 patch，作为数值生成路线。
6. **RedLamp**：多类别时序增强与软标签，作为 pseudo-anomaly / contamination 鲁棒路线；它不编码微服务故障机理。
7. **LLM-AP**：可作为单指标数值生成的专项参照；NAB 上验证过的统计过滤不能假设直接适用于 KPIs。
8. **Conditional generator（方案 B）**：只有在获得足够训练事件后才加入，不能在样本不足时先把它当成默认模型。

### 检测器 / 融合 baseline

- 固定一套可重现的单模态 Metric detector 和一套 Trace detector。
- 比较 Metric-only、Trace-only、无约束 Metric–Trace fusion、带一致性校验 / 约束的 fusion。
- 可选 MODIFy 做多模态检测 / 定位参考实现或机制对照，但要确保数据适配、训练样本和阈值协议一致。MODIFy 原论文的 Trace diffusion 是去噪表示而非异常生成；不能把它列作生成 baseline。（MODIFy PDF §§4–5, Eqs. 1–17）
- 如研究重点是生成器，而非 detector 架构，主比较中必须固定 detector capacity 和调参预算。

## 6. 数据真实性和跨模态一致性评价

### 6.1 真实性评价

真实性至少分四类，不以一个距离或生成器判别器代替：

1. **结构有效**：schema 合法率、服务映射合法率、Trace 父子关系 / 拓扑违规、span 时间违规、采样与缺失行为是否合理。
2. **分布 / 条件保真**：Metric 分位数、相关 / 自相关、条件时延分布、每服务 Trace span 数、trace depth / fan-out、status code / duration 分布；在 workload 与故障条件下分别比较，而不是跨条件汇总。
3. **机制可追溯**：action execution 记录、作用目标和时间与计划一致；真实服务健康 oracle 是否显示预期退化；影响服务是否在有效传播路径内。
4. **盲测审查**：由不知道生成来源的运维人员 / 研究者对场景描述、实际信号合理性和错误传播路径作结构化评价；报告一致率，不能用主观打分替代机器可测真值。

只训练 real-vs-synthetic discriminator 可用于发现 artifacts，不足以证明真实性：判别器可能利用时间戳格式、采样器或环境元数据等捷径。

### 6.2 Metric–Trace 一致性评价

- **拓扑**：Trace call edge 是否在当前版本依赖图内；故障服务到影响服务是否存在可达路径。
- **时序**：fault start / end、目标 span 时间、Metric 响应窗口是否满足预定义先后 / overlap 容差。
- **服务粒度**：Metric 服务 / 实例和 Trace 的 service / instance ID 对应是否正确。
- **机制条件统计**：按 workload、服务、注入严重度校准 latency、error、retry、throughput、resource 的条件关系；输出一致性分数及置信区间。
- **缺失 / 采样敏感性**：分别按 Trace sampling 与字段缺失率分层；报告 Trace 缺失时性能下降，不能将无证据理解为健康。
- **一致性消融**：比较无约束生成、仅结构规则、结构 + 时间约束、结构 + 时间 + 统计关系。测试一致性约束是否改善真实 holdout detector，而不只让 validator 得分更高。

## 7. 训练、验证和独立测试

推荐按照事件 / 服务 / 故障模板分组，而不是随机切滑窗：

- 训练集：部分故障事件、服务与负载区间；可使用训练集背景和其生成样本。
- 验证集：独立 incident 或独立运行，用于阈值、窗口宽度及超参数选择。
- 测试集：未参与生成器 / 规则构造的真实注入事件，尽量留出服务、故障模板、应用版本或业务负载区间。
- 另设 generator-held-out 测试：不使用训练中出现的生成方法 / 模板生成测试标签；优先测试真实运行观测。

若数据量不足以留出多个维度，先选最重要的一个 holdout 维度并报告限制，不得将同一 fault run 的近邻窗口分散到训练和测试。阈值只能在验证集设置，测试集不调参。所有方法使用同一个 test incidents 和同一 label policy。

## 8. 下游评价指标

点级 F1 可能掩盖事件级误报和过早 / 延迟问题。建议至少报告：

| 目标 | 指标 |
| --- | --- |
| 服务故障检测 | event precision / recall / F1、PR-AUC、每小时 / 每运行误报数 |
| 健康负载误报 | N1 健康波动下的 FPR、SLO-preserving workload 分层 FPR |
| 同负载故障发现 | N1 vs F1 / F3 matched pairs 的 detection recall、相对差异及配对置信区间 |
| 及时性 | 首次告警相对动作 / 真实退化的检测延迟、预警窗口 |
| 跨状态稳定性 | 跨 workload、service、version、fault family 的 macro 平均和最差组结果 |
| Trace 增量 | Metric-only 对 Metric+Trace 的固定 FPR recall 增益；按采样率和影响路径分层 |
| 检测成本 | 单窗口延迟、吞吐、缺失模态时退化情况 |
| 可选根因能力 | service top-k accuracy / MRR，独立于检测分数报告 |

如参考 TSAD benchmark 的 point-adjusted F1 或 RPA-F1，应与未调整的事件级指标并列，不把各自协议下分数直接拼成跨论文排名。

## 9. 消融实验

1. **LLM 作用**：移除 LLM，改用相同知识输入和预算的规则 / 模板计划器；报告计划质量与下游 real-holdout 收益。
2. **故障知识**：保留同一生成器，移除 fault ontology / topology constraints；检查结构错误、执行失败和跨服务影响一致性。
3. **Trace 模态**：Metric-only、Trace-only、Metric+Trace；再按采样率 / 缺失情况拆分。
4. **跨模态一致性约束**：无约束、结构约束、结构 + 时间、结构 + 时间 + 条件统计。
5. **正常波动困难对照**：无 N1、加入健康负载上涨、加入同负载 fault pair、加入负载 + fault 并发。
6. **真实系统响应**：规则合成遥测与测试床实测遥测；训练可以混合，但 test 只用独立实测事件。
7. **根因与效果标签**：仅按动作打标签 vs 同时按 observed degradation 过滤 / 分层；分析“动作成功但无服务影响”事件。
8. **背景保留**：保持输入背景、只注入目标服务、允许拓扑邻居变化；检测是否依赖非目标服务的伪影。
9. **生成器迁移**：只在一种 augmentation 生成训练集、在另一种构造 / 真实故障测试，衡量生成器特定痕迹。

## 10. 假设与成功判据

以下是预注册前可调整的研究假设，不是既有实验结论：

- **H1：LLM 有用性**。相对同知识、同预算的规则模板，LLM 提高合法可执行的计划覆盖率，且在真实 holdout detector 上提供统计上可重复的增益。若仅提升语言多样性或计划数量而无 downstream effect，则不支持 H1。
- **H2：Trace 增量**。在下游传播可观测、Trace sampling 足够且 service identity 完整的事件中，Metric+Trace 相比 Metric-only 在相同健康负载 FPR 下提高故障 event recall 或降低 detection delay。若只在完整采样上有增益，应报告其运行条件。
- **H3：一致性价值**。加约束减少结构 / 时间 / 条件统计违反，并在未参与生成器拟合的故障事件上改善 detector；只降低生成 validator violation、不改善真实检测，不能证明任务价值。
- **H4：正常波动区分**。加入 N1 健康负载对照使 benign FPR 下降，同时 F1 / recall on matched faults 不出现不可接受下降。应预先设定业务允许的 FPR 和召回非劣界值。

应报告跨多个独立运行的置信区间和失败例，而不是只报单次最佳值。任何 benchmark 规模、阈值和最小效应量需在实际数据规模核查后确定，不在本计划中编造。

## 11. 主要风险与停止条件

- 没有 workload、service / instance mapping 或事件真值时，不能声称完成 Metric–Trace 一致性建模；先补 schema 或改为小型受控 testbed。
- 若低流量 / 严重采样导致 Trace 无法表示故障，应将 Trace 无效样本分层，不应通过规则虚造 span 来填满。
- 若 fault action 不产生用户可见退化，保留为执行无效 / 无影响样本，不可强制打成异常。
- 若 LLM planner 不优于规则基线，保留可执行场景构造框架价值，但收窄“LLM 创新”主张。
- 若仅合成测试收益、真实 holdout 不提高，结论应是检测器学到 synthetic artifact 或未能泛化，不应声称生成数据有效。

## 12. 相关证据

- 动态正常 workload 和独立 fault injection：Synthetic Time Series PDF §§3.2–3.5, Eqs. 1–2, Algorithms 1–2；[笔记](../../papers/aiops/synthetic-cloud-microservices/notes.md)。
- 测试床、遥测接口和有限 no-op 误报：AIOpsLab PDF §§2–3, §3.6.4；[笔记](../../papers/aiops/aiopslab/notes.md)。
- 三模态已有 detector、6 秒特征对齐和静态图限制：MODIFy PDF §§4–6, Eqs. 1–17；[笔记](../../papers/aiops/modify/notes.md)。
- TSAD 增强和评估参照： [CAPMix](../../papers/capmix/notes.md)、[GenIAS](../../papers/aiops/genias/notes.md)、[CAROTS](../../papers/carots/notes.md)、[RedLamp 原文](https://arxiv.org/html/2505.20765)。
- 正常状态 / 因果 / context 证据边界：[TSAD 研究问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md)。
