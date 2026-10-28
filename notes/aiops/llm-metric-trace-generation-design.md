# LLM 规划微服务故障与 Metric–Trace 建模：候选技术方案

## 1. 设计目标和边界

目标是比较三条可行路线，为后续研究选择一条最小且可证伪的技术路径。本文件是方案论证，不是已实现架构，也不声称创新性已经成立。

目标研究问题：在微服务架构、正常业务负载和运行状态已知或可估计时，如何构造由真实故障机制支持、Metric 与 Trace 时间 / 服务 / 调用结构相互一致的训练场景，使检测器能够区分“健康但波动的业务状态”和“相似背景下发生服务退化”的事件。

建议避免把 LLM 直接当作数值模拟器。LLM-AP 用提示让 LLM 改写局部数值窗口，TraceLLM 用 LLM 生成调用图；前者不含微服务故障机制，后者的图结构生成不含根因计划。（TraceLLM §§3–4；LLM-AP §§3–4）结构化故障计划更容易审核、编译、复现和与实测真值对齐。

## 2. 统一的场景表示

三种方案可共用一份结构化场景记录。字段缺失时显式标为 unknown，不由模型臆测：

~~~yaml
scenario_id: stable identifier
environment:
  application: service deployment / version
  topology_version: observed dependency graph identifier
  workload_state: arrival rate, mix, tenant or business period if available
root_cause:
  service_or_instance: canonical id
  fault_family: allowlisted action family
  action: executable action or generation constraint
  severity: calibrated ordinal or measurable parameter
  start_time: event-time anchor
  duration: bounded interval
propagation_hypothesis:
  reachable_services: topology-constrained list
  expected_metric_effects: probabilistic expectations, not guaranteed labels
  expected_trace_effects: span / error / latency hypotheses
controls:
  healthy_workload_match: reference scenario id
  service_health_checks: transaction, availability, latency or SLO checks
labels:
  demand_shift: true / false / unknown
  injected_action: true / false
  observed_service_degradation: true / false / unknown
provenance:
  plan_generator: LLM / template / operator
  executor_and_version: rule engine / testbed / conditional model
  raw_event_ids: references only
~~~

该 schema 是本报告建议的研究数据合同，不是任一相关论文的现成标准。训练和评测应区分“注入动作标签”“业务负载标签”和“实际服务退化标签”。高负载可能健康，也可能因容量不足造成性能退化；不能只依据负载变化将样本标成正常。

## 3. 共同流水线

~~~text
架构 / 遥测 schema / 允许故障动作 / workload 条件
                 ↓
结构化故障计划：LLM planner 或无 LLM 模板 baseline
                 ↓
计划校验：schema、服务 ID、拓扑可达性、动作白名单、资源预算
                 ↓
执行层：规则注入（A）/ 条件生成模型（B）/ 真实测试床（C）
                 ↓
事件时间对齐 + service / instance 映射 + missingness mask
                 ↓
一致性校验：确定性结构约束 + 校准后的统计关系
                 ↓
健康状态与故障状态双轴标注 → detector 训练与独立测试
~~~

架构输入至少要包括服务依赖图、服务与实例的 canonical identity、Metric 名称和单位、Trace span schema、时间戳语义、故障动作与 workload 状态。若缺少这些字段，先做数据可行性盘点，不能让 LLM 自行补齐。

## 4. 跨模态一致性：硬约束与统计约束

### 4.1 可作为确定性校验的关系

下列约束主要用于检查样本结构或受控实验事实：

1. **身份约束**：服务 ID、实例 ID 与服务目录一致；span 指向的服务确实存在于本次拓扑版本；同一实例别名映射唯一。
2. **Span 结构约束**：trace ID / span ID 唯一；父 span 存在；父子关系形成该追踪器允许的结构；调用边属于已观察或配置的允许依赖集合。若系统允许动态 RPC / 服务发现，使用版本化的边白名单，不应固定为过时的静态拓扑。
3. **时间约束**：开始时间 ≤ 结束时间；父 span 与 child span 的时间范围在预设 clock-skew 容差下兼容；事件时间落在相应观测 / 故障窗口中。跨主机时钟偏移和异步执行可能使严格包含关系不成立，应使用已测量的容差，而不是强行假设零时钟误差。
4. **执行真值**：实验控制器记录的动作目标、动作开始 / 结束时间、动作结果与标签引用一致；从根服务到预期影响服务的路径必须在对应拓扑可达。
5. **聚合对齐**：Metric 窗口由事件时间和明确的采样 / 聚合规则构造；Trace span 使用同一时钟基准归窗；服务 / 实例维度的聚合映射可追溯。

这些规则证明“结构合法”或“动作记录一致”，不自动证明动作造成服务故障。

### 4.2 应以统计或概率方式表达的关系

CPU 饱和与延迟、错误率与超时、吞吐量与服务时延、重试与 span 数、下游延迟与上游尾延迟之间的关系依应用、负载、缓存、批处理、重试策略、采样和观测窗口而变化。它们适合写成条件分布、校准范围、分层相关性或概率预测，不宜当作通用硬规则。例如，CPU 上升不必然导致 latency 上升；某些下游错误会被熔断器隔离，未必在上游产生长尾。

建议按 application、service、workload bin、故障类型和窗口长度，从真实健康 / 注入事件数据估计容差与关系。若显式定义一致性分数，可写为：

    L_consistency = λ_top L_topology + λ_time L_temporal + λ_id L_identity + λ_stat L_conditional-statistics

其中前三项对应可审计约束或违反惩罚；统计项只能作为参考 / 学习目标，需独立校准。若直接训练生成模型，不能把“最小化 L_consistency”解释成恢复了真实因果机制。

## 5. 方案 A：LLM 结构化规划 + 规则异常注入

### 5.1 架构和模块

1. **计划生成器**：输入服务图、运维故障词表、workload 状态和目标覆盖矩阵；LLM 输出 schema 中的根因服务、故障类型、动作参数范围、持续时间和传播假设。
2. **无 LLM 对照计划器**：按相同故障本体、拓扑、覆盖预算和约束，用枚举 / 随机组合 / 人工模板生成计划。该 baseline 与 LLM 接收同一事实信息，避免把知识更多误当成语言模型能力。
3. **计划校验器**：用 JSON schema、服务身份解析、调用图可达性、动作白名单和预算限制拒绝不可执行或越权计划。
4. **Metric 注入器**：在健康背景窗口上按故障动作参数改写相应服务 / 指标；同时保留未改写背景和可追溯 mask。可采用明确规则，例如局部资源压力使 CPU / run queue 在动作期内按校准范围变化，但避免固定写死跨系统“CPU 一定升高”。
5. **Trace 注入器**：从实测健康 Trace 模板抽取请求树，按计划修改目标服务的 span latency、timeout / error、retry 或缺失行为；所有变换遵守 schema 与拓扑、时间规则。仅在确有原始字段时生成错误类型，不能凭空添加未被系统支持的语义。
6. **一致性与健康检查**：结构约束逐样本核验；统计关系对照真实注入集的分层置信区间；执行 / 健康标签不满足条件时标为 invalid 或 uncertain。

### 5.2 输入、输出和训练数据

输入是健康遥测窗口、服务拓扑、实例映射、采样规则、业务负载和故障模板。输出是背景保持的成对或三元 Metric–Trace 样本及 plan/action/effect 标签。LLM planner 可不训练，只作受约束提示；规则生成器和下游 detector 可在 CPU 试验，但本轮不实施。

### 5.3 优点、成本与风险

- 工程和算力最低，数据逐项可解释，便于建立 MVP 和生成器 baseline。
- 规则使结构约束可控，场景覆盖矩阵容易设计。
- 主要风险是人工注入形状、人为 latency / error 痕迹被 detector 记住；不一致规则会把 KPI 变化强加到实际并不受影响的服务。
- LLM 可能给出看似合理但超出系统能力的动作 / 根因；必须拒绝 schema 外字段并允许“无法生成”。
- 仅靠固定模板难以覆盖未知交互，但加入 LLM 也不保证拓展有效。

### 5.4 创新空间

单独“LLM 生成参数 + 人工规则改指标”与现有规则增强相邻，创新空间弱。较强、但仍需实验证明的贡献可以是：故障计划有可执行 provenance；在同一业务负载背景下建立健康与故障匹配对照；显式验证 Metric 与 Trace 的拓扑 / 时间 / 统计关系；再用未参与注入规则开发的真实事件验证 detector transfer。

## 6. 方案 B：LLM 故障计划 + 条件生成模型

### 6.1 架构和模块

1. LLM 和无 LLM 模板器共同输出标准场景 plan。
2. 场景编码器把 workload、拓扑、根因服务、动作类型、严重度、时间长度和传播目标映射为条件向量。
3. Metric 生成器以健康背景窗口与 plan condition 生成 KPI 残差或未来窗口，尽量保持未受影响指标 / 服务背景。
4. Trace 生成器以请求 DAG、服务拓扑、业务请求类型和相同 plan condition 生成 span / error / latency。
5. 联合约束层检查服务身份、调用边、span 时间和 Metric 聚合关系；可使用共享 latent、跨模态判别分数或对比目标，但只有在成对实测数据充分时才有训练依据。
6. 质量门控输出样本、生成概率和违反项；统计分布 / detector 收益仅用于不同于训练事件的 holdout。

这里可以是两个联合条件的模型，也可以是一个共享 latent 的多模态模型。“两个模型使用同一个 plan”仍不代表生成结果一致；必须显式测量两模态的一致性。若只有 Metric 数据或 Trace 未与事件时间戳对齐，联合 generator 不具备必要监督。

### 6.2 训练数据与训练目标

至少需要成对的正常 / 故障 Metric–Trace 片段、已版本化拓扑、负载 / 请求量条件、故障动作或人工核验 incident 标签、统一的事件时间基准及缺失 / 采样标记。公开工作已有分别生成数值或生成 Trace、以及实测多模态数据的相邻部件，但本知识库的论文没有提供上述对齐的 joint generation 数据集。

可考察的目标项包括：

    L = L_metric + L_trace + λ_c L_consistency + λ_bg L_background-preservation + λ_cond L_scenario-condition

这些是待研究的损失设计选项，并非论文已验证的公式。下游 detector 的训练收益不能与生成器拟合损失混为一谈。需按 incident / service / fault plan 分割训练、验证和测试，以减少同一背景窗口或同一注入模板泄漏。

### 6.3 优点、成本与风险

- 可以在一定程度上学习真实 KPI、Trace 边属性和噪声分布，输出比手写规则更平滑或多样的样本。
- 具备研究共享 latent、对齐损失或条件传播关系的空间。
- 需要最多的成对数据和训练成本；异常事件稀少、服务版本变化和 Trace sampling 会让条件标签稀疏。
- 生成器可能拟合故障模板而非故障机理；metric 与 trace 可能分别逼真却相互矛盾。
- 分布距离指标或判别器容易被生成器自身伪影主导；如果验证集来自相同生成器 / 故障模板，结果不具有独立性。
- 高维 Trace 图与低频聚合 Metric 的不匹配会让单一生成时间步定义不自然。

### 6.4 创新空间

本知识库没有发现完成了故障计划条件化 Metric–Trace 联合生成及一致性验证的工作，因此这个方向存在候选空间；但“没有出现在现有 39 篇精读集合”不是全面文献新颖性证明。必须先补检索领域外最新文献，并用方案 C 的真实注入或可信的独立事件给方案 B 作评估锚点。现阶段不推荐把 B 作为第一个实现目标。

## 7. 方案 C：LLM 规划 + 真实故障注入平台

### 7.1 架构和模块

1. **计划层**：LLM 或模板器基于架构与允许故障动作输出结构化场景。
2. **安全编译层**：计划转换为 Chaos / FIS / 测试平台允许的动作。仅支持 allowlist 中动作、范围和目标；由独立 validator 审核权限、资源预算和拓扑。
3. **实验控制层**：克隆健康应用状态，固定或记录版本、数据快照、workload profile、实例和拓扑版本；执行健康 control、负载-only、fault-only 和 workload+fault 场景。
4. **遥测采集层**：从 Prometheus / OpenTelemetry 等实际 exporter 采集 Metrics / Trace（需要时 Log）；保存 event time、采样率、时钟偏移、span parent-child、service/instance mapping 和注入器 action log。
5. **oracle / health layer**：动作是否执行与服务是否实际退化分开。用端到端事务结果、错误码、成功率、SLO、故障控制器状态和人工复核确认效果。
6. **事件化样本层**：按同一 scenario ID 关联 plan、workload、action、Metric、Trace、健康检查及多轴标签。
7. **训练 / 评测层**：固定下游 detector、用历史生成样本训练，按 incident / 服务 / workload / 故障类型留出真实注入事件。

AIOpsLab 已展示 live testbed 中 Agent 获得真实工具观察并由内部真值评价；Synthetic Time Series 已展示动态 workload 与基础设施注入数据构造。C 的候选贡献应聚焦研究数据配对、计划可执行性、健康对照与 generator-independent detector evaluation，而不能泛称“首次 fault injection”。（AIOpsLab §§2–3；Synthetic Time Series §§3.1–3.5）

### 7.2 数据、难度和成本

需要可复现测试服务、隔离集群、故障注入权限、监控 / Trace 采集、健康交易、故障控制器日志和多轮重复运行。大型 GPU 不是必要依赖；成本主要来自集群资源、故障复现、环境重置、日志存储和测试自动化。真实运行会产生自然噪声和更可信的服务响应，但也会遇到 testbed 与生产偏移、故障不触发业务退化、agentic executor 不稳定等问题。

### 7.3 创新空间

潜在论文贡献可以是：

- 结构化、可编译、可审计的故障场景计划和其相对规则模板的增益分析；
- 由同一工作负载派生的 matched healthy / fault / concurrent episodes；
- Metric–Trace 跨模态一致性与执行 / 健康双 oracle；
- 生成样本训练后，在未参加 plan / generator 构造的真实故障事件上检验检测收益和正常波动 FPR。

将 AIOpsLab 用作 testbed / baseline 相关工作，不要把其实验 Agent 得分当成 detector 效果。TraceLLM 的离线图生成、MODIFy 的观测融合可作为相邻路线，但不覆盖此 execution loop。

## 8. 三种方案比较与推荐

| 维度 | A：规则异常注入 | B：条件生成模型 | C：真实故障注入 |
| --- | --- | --- | --- |
| 场景语义来源 | LLM / 规则计划，但执行为人工写的扰动 | 同左；条件模型学习数据映射 | 可执行计划 + 实际应用响应 |
| Metric–Trace 联动 | 需手工同步规则与时间轴 | 需 joint condition / shared latent / explicit consistency | 由同一次运行自然产生，仍需对齐及校验 |
| 训练数据要求 | 健康背景窗、结构化拓扑、故障扰动规则 | 大量对齐正常 / 故障样本，条件标签丰富 | 可逐事件采集；无需先训练遥测生成器 |
| 计算成本 | 低；主要是规则与测试运行 | 高；训练与调参成本最高 | 中高；集群和反复运行主导 |
| 真实性证据 | 注入规则内部一致，外部真实性较弱 | 取决于真实 holdout 验证 | 可记录真实执行及服务效应，强于离线形状改写 |
| 最大风险 | 人工伪迹与规则偏差 | 拟合分布而非机制，模态矛盾 | testbed 偏差和故障 / 健康标注难 |
| 与已有工作重合 | CutAddPaste / RedLamp / LLM-AP 的增强路线；已有 fault injection 工作 | GenIAS / LLM-AP / TraceLLM 的生成技术与 MODIFy 的融合相邻 | Synthetic Time Series / AIOpsLab 已有平台路线 |
| 可辩护贡献 | 高可控 paired baseline、规则对照和验证规范 | 条件化联合生成与经实测验证的一致性收益 | 可复现多轴标注数据与执行 / 健康双真值、独立检测测试 |

### 推荐：先采用 C 作为真实性锚点，A 作为强且可解释的生成 baseline

三者中，优先选择**方案 C 的验证环境**，用**方案 A 作为最小样本构造和无 LLM / 有 LLM 对照**。原因是本研究的核心主张涉及真实故障机制与跨模态一致，只有数值 / 图像距离无法验证这一点。第一阶段不训练条件生成器；先在小规模服务上建立可信 matched episodes，验证健康判定、Metric–Trace schema 和 detector 的固定评测。

LLM 仅在它能比规则模板带来可测量的 scenario coverage / composition / valid compilation 增益时保留。之后，若获得充足且受控的成对数据，再把 B 作为规模化生成路线，并用 C 的事件保留集评估。如此不必把“使用 LLM”预设成研究贡献，也避免在数据监督不足时先训练 joint generator。

## 9. LLM 的独特能力假设及验证

### 候选能力

- 把事故文本、服务图或可读配置转换为结构化故障场景字段；
- 根据拓扑约束组合根因服务、下游路径、故障动作、负载状态和持续时间；
- 从已有计划中提出覆盖低频但允许的组合，形成候选 scenario；
- 给出可读的计划解释，供运维 / 研究者审查。

以上属于待验证能力，不代表 LLM 理解了真实物理机理。执行器和观测 oracle 才确认动作与服务影响。

### 最低比较协议

让 LLM planner 与规则 / 模板 planner 共享同一故障本体、架构、动作白名单、目标场景数和执行预算。比较：

1. schema 合法率、拓扑 / 参数校验通过率；
2. 可执行率、实际执行成功率、无效但“听起来合理”场景率；
3. action / service / workload 组合覆盖率、重复率、边际组合覆盖；
4. 执行后形成健康但有变化、真实退化及并发样本的数量；
5. 在相同真实执行数据预算下，增强训练后的固定 detector 是否提升 real-holdout 事件召回，并控制 benign-workload FPR。

如果 LLM 只增加描述多样性而未提高可执行组合覆盖或真实测试 detector 收益，则不应把它作为必需模块。

## 10. 数据可行性：当前知识库能确认的范围

本次只检查了 agent-knowledge 中可检索的 Markdown 数据字典 / 数据结构材料，没有找到标明国网项目 Metric / Trace 字段的 schema 文档。未读取或修改国网原始数据，也未将数据发往外部服务。

| 所需信息 | 国网数据当前状态 | 对研究的影响 |
| --- | --- | --- |
| KPI 名称、类型、单位、采样频率 | 尚未确认 | 不能确定归一化、业务含义或采样窗 |
| 服务 / 实例标识及映射 | 尚未确认 | 不能形成 service-level paired Metric–Trace |
| Trace / Span 字段、trace ID、parent span | 尚未确认 | 不能验证调用结构 / 请求路径 |
| Span start / end、duration、status / error | 尚未确认 | 不能对齐延迟传播或错误传播 |
| Metric / Trace 时间戳、时区和时钟偏移 | 尚未确认 | 不能定义共同事件时间轴 |
| 服务依赖拓扑及版本变化 | 尚未确认 | 不能做可达性约束或传播范围检查 |
| 故障注入 / incident 标签和根因 | 尚未确认 | 无法构造无泄漏的真实故障 holdout |
| 业务负载、请求量、调用类型或业务时段 | 尚未确认 | 无法定义“负载变化但健康”的条件 |
| 成功率、SLO / 交易健康检查 | 尚未确认 | 不能可靠确认某段是否健康或退化 |

“尚未确认”仅表示知识库可见资料中没有证据，不等于原始数据缺失。下一步若获得本地数据字典，应先只读核对字段覆盖和 join key，再评估能否开展离线历史分析；若没有健康状态或故障标签，应优先用隔离测试床补齐，而不是从 KPI 形态猜标签。

## 11. 设计依据与文献定位

- TraceLLM：Trace DAG 条件生成与结构校验，PDF §§3–4, Eq. 1, Figs. 3–7；[笔记](../../papers/aiops/tracellm/notes.md)。
- LLM-AP：数值提示生成与五阶段验证，PDF §§3–4, Eqs. 1–12, Table 8；[笔记](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md)。
- Synthetic Time Series：正常 workload、load anomaly 和 FIS action，PDF §§3.2–3.5, Eqs. 1–2, Algorithms 1–2, Tables 1–3；[笔记](../../papers/aiops/synthetic-cloud-microservices/notes.md)。
- AIOpsLab：工作负载、故障注入、真实遥测接口与任务 oracle，PDF §§2–3, Table 3, §3.6.4；[笔记](../../papers/aiops/aiopslab/notes.md)。
- MODIFy：Log / Metric / Trace 特征处理、6 秒对齐、融合和静态图边界，PDF §§4–6, Eqs. 1–17, Tables 2–7；[笔记](../../papers/aiops/modify/notes.md)。
- GenIAS、CAPMix、CAROTS、RedLamp 与动态正常态 / context 路线的差异见 [研究现状综述](llm-microservice-anomaly-generation-survey.md) 及 [TSAD 问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md)。
