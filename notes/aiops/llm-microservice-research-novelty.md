# LLM 微服务 Metric–Trace 异常生成：创新性边界与候选贡献

## 1. 结论边界

本文件判断基于知识库中已精读的 33 篇 TSAD 论文与 6 篇 LLM / 微服务专题论文，并对 RedLamp 公开 KDD ’25 原文做方法级定点核验。AMulSys 只有出版方公开摘要可用，方法细节仍未核实。该资料范围足以识别明显的研究重合，但不足以支持“全领域首次”的结论。提交论文前需补充针对 microservice fault generation、trace synthesis、multimodal AIOps、chaos engineering / fault injection 和 LLM planning 的最新系统检索。

创新判断使用三种标签：

- **已被相邻工作覆盖**：不能作为独立新颖性主张。
- **尚未由当前证据确认**：当前精读集未见完整能力；不等于全领域无人研究。
- **候选贡献**：可以设计可证伪实验，只有实验支持后才能写成贡献。

## 2. 已经被覆盖或不能单独声称创新的内容

| 拟议主张 | 已有对应工作与证据 | 判断 |
| --- | --- | --- |
| 用 LLM 生成异常数值时间序列 | LLM-AP 使用冻结 GPT-3.5 / GPT-4o 对单变量异常窗口直接生成数值，并通过 5 阶段验证；NAB 上部分 detector 提升、Autoformer 下降。（LLM-AP PDF §§3–4, Table 8） | 已覆盖。创新不能写成“首次用 LLM 生成时序异常”。 |
| 用 LLM 生成微服务 Trace | TraceLLM 用 Llama-2 7B + LoRA 生成条件化微服务调用图，并验证图结构与部分下游图任务。（TraceLLM PDF §§3–4, Eq. 1, Figs. 3–7） | 已覆盖 Trace 结构生成。其生成图不包含故障根因或 Metric 对齐。 |
| 使用多种合成异常训练检测器 | CAPMix、GenIAS、RedLamp、CAROTS 和其他 TSAD 论文已经研究形态增强、潜空间扰动、多类伪异常、因果关系保持 / 破坏以及相应训练目标。 | 已覆盖。只替换成 LLM 或加入标准 augmentation 组合不足以构成强创新。 |
| 在微服务环境注入故障并记录 Metric | Synthetic Time Series 在 AWS EKS 中结合动态 Locust workload 与 FIS 注入并收集 470 项 Metric；AIOpsLab 通过测试床运行 workload / fault，并提供 Metrics、Logs、Traces 与内部真值。（各自 PDF §3、Algorithms 1–2；AIOpsLab §§2–3） | 已覆盖基本测试床和遥测获取。需与其区分的应是配对矩阵、计划层比较、独立检测验证。 |
| 多模态 Metric–Trace–Log 检测 / 诊断 | MODIFy 使用三模态进行检测和服务级定位，含特征对齐、融合和调用图；AMulSys 摘要描述三模态图与类别先验多模态 Mixup。 | 已有检测融合路线；不能声称“首次联合 Metric 与 Trace”。AMulSys 全文不在当前证据内。 |
| 处理 KPI 动态和多种正常模式 | CAPMix 研究 noisy / dynamic KPI；MACE 表示多个频域正常模式；When Model Meets New Normals 做测试时适应；TimeRCD 用序列相对 context；CAROTS 使用变量关系结构。 | 已有相邻机制。可以研究真实业务上下文语义及变化与故障并发，不能笼统声称首次建模多正常。 |
| 给合成异常加真实性过滤 | LLM-AP 用统计 / 形态过滤；TraceLLM 校验图约束；GenIAS 报告 ARP / EDI；多篇 TSAD 工作测 detector gain。 | 已有局部有效性 / 分布 / 下游效用验证。可贡献之处是独立执行真值、跨模态机制一致和真实故障 holdout，而非“增加验证器”本身。 |
| LLM 负责故障语义，所以数据真实 | AIOpsLab 中 LLM 是 Agent；故障动作由控制器执行。TraceLLM 与 LLM-AP 的 LLM 输出也没有微服务根因执行 oracle。 | 当前证据不支持。语言可读的故障描述不等于真实机制、动作执行或业务退化。 |

## 3. 当前知识库未能确认的能力组合

以下是当前 39 篇完成精读资料的边界：

1. TraceLLM 生成 Trace DAG，但没有同一故障计划下的 Metric 生成。
2. LLM-AP / GenIAS / CAPMix / RedLamp 生成或编辑数值伪异常，但没有按服务拓扑执行故障动作或生成 Trace。
3. Synthetic Time Series / AIOpsLab 从真实运行环境观察共同来源遥测，但不是用同一 plan 学习并联合生成 Metric–Trace 的生成器。
4. MODIFy / AMulSys（仅摘要级）消费多模态输入进行检测 / 诊断或增强；未由已核全文确认样本级跨模态异常合成。
5. AIOpsLab 只有两个 no-op 正常任务报告特定 Agent 对正常 workload 的误报；Synthetic Time Series 分别构造动态负载和基础设施故障，但当前资料没有给出负载匹配、服务健康 oracle 共同确认的统一四格检测实验。
6. 现有方法未在本知识库范围内完成“合成训练 → 不同服务 / 故障模板 / generator 的独立实测故障测试 → 健康高负载误报”完整链路。

谨慎表述应为：“在本文已检查的文献集合中，尚未找到同时做到上述各项的工作。”不应写“现有研究都没有”或“首次”。

## 4. 三个较有潜力的研究切入点

### 候选一：负载变化 × 服务退化的匹配事件与多轴标注

**已有重合**：Synthetic Time Series 有动态正常负载、负载变化和 fault injection，但没有证明一个同负载 matched healthy / fault detector benchmark；AIOpsLab 具有 no-op 正常任务，但数量有限；CAPMix 与 MACE 等从数值分布层面处理 dynamic normality。

**潜在差异**：在同一应用版本、调用 mix、时间尺度和 workload 曲线下形成成对 episodes：健康负载上涨、同负载下游延迟、资源竞争、timeout/error，以及负载加故障并发；分别记录需求变化、动作执行、用户可见服务退化三个标签。健康标签由事务 / SLO 通过条件确认，而不是“没有注入”推断。

**研究价值**：直接回答系统是否能把 KPI 变动解释为合法需求波动、负载造成的自然过载或下游故障，并报告 N1 健康波动误报与 matched fault 召回。

**风险**：若高负载本身引起 SLO 退化，不能将它简单标成 normal；需要把“需求原因”和“服务健康结果”作为两轴，必要时区分容量过载故障。

**验证方法**：paired-run 设计；event-level / service-level 分组切分；在真实实测 holdout 上报告 benign-workload FPR、故障 recall、检测延迟和 workload 泛化。

**判断**：三项中最适合优先形成明确实验问题，可能是数据集 / 评测基准贡献；尚非已确认算法创新。

### 候选二：可执行故障计划到可追溯遥测的语义链路

**已有重合**：TraceLLM 有条件化 DAG 生成；LLM-AP 直接数值生成；AIOpsLab 和 Synthetic Time Series 有故障动作执行与 runtime telemetry。它们分别覆盖生成 / 执行环节。

**潜在差异**：由 LLM 将架构与受限知识源转成结构化 plan，并与无 LLM 规则计划器比较；编译器将合法 plan 转成 fault-injection action；实际注入器 / health oracle 记录动作是否执行和是否引发退化；最终样本保留从 plan、target service、时间、影响路径到 Metric / Trace 事件的 provenance。

**研究价值**：使 LLM 的价值可测而不靠“文本合理”：比较可编译率、组合覆盖、冗余率、执行成功率和相同执行预算下的实测检测收益。

**风险**：模型可能只是复述故障本体；若模板库很丰富，LLM 不一定增益；由 LLM 产生的 scenario 可能超出执行平台能力。

**验证方法**：规则 / 模板 baseline 接收同一服务图、动作白名单、domain notes 与场景预算；盲化评审解释性；生成计划必须通过确定性 validator 和真实执行器。

**判断**：可能构成 LLM 场景规划的明确研究贡献，但只有在 LLM 带来有效覆盖 / detector gain 时才有意义。

### 候选三：Metric–Trace 一致性定义、验证和下游效用

**已有重合**：MODIFy 在 6 秒时间聚合后融合观测模态；AMulSys 摘要称三模态异构图与多模态增强；TraceLLM 生成 Trace 结构。这些说明“多模态模型”“图表示”本身不新。

**潜在差异**：把约束拆成三类：身份 / 拓扑 / span 时间等结构约束；跨主机时钟和聚合窗的时间约束；Latency、timeout、error、retry、资源与 workload 的条件统计约束。用真实 fault-injection episodes 校准统计容差，并报告数据缺失 / Trace sampling 下的一致性置信度。

**研究价值**：检验受约束生成是否不仅减少 validator violation，而且改善在独立真实故障事件上的检测；衡量 Trace 在什么请求量 / 采样率 / 故障类型下提供增量证据。

**风险**：观测相关性不等于因果；规则约束可能错误排除真实复杂行为；多模态联合训练数据不足。

**验证方法**：比较 Metric-only、Trace-only、无约束融合、拓扑 + 时间约束、再加入校准统计关系；用未参与校准的 service / incident / fault type holdout，测固定 FPR 下召回和延迟；低采样率分层。

**判断**：三项中方法论文潜力较高，但依赖真实对齐数据和独立 oracle；不应只把损失项相加当创新。

## 5. 创新主张阶梯

| 当前可表达的主张 | 所需证据 | 未满足前的保守措辞 |
| --- | --- | --- |
| 提出一套故障场景结构化 schema | 与现有场景 / chaos schema 的比较及适用性 | “采用本研究的数据合同” |
| LLM 生成更多故障组合 | 计划合法、可编译、执行成功率和 coverage baseline | “LLM 候选计划可扩展场景枚举” |
| 生成 Metric–Trace 一致样本 | 结构、时间、身份、条件统计和实际运行 oracle | “实现样本结构 / 时间对齐检查” |
| 更好区分正常业务波动和真实故障 | 健康 load-only 与 matched fault 的独立测试 | “在所测 workload / fault set 上降低误报” |
| 生成数据能提升真实故障检测 | train-synth / test-real，事件级 holdout，跨 service / generator | “在指定真实测试集上有增益” |
| LLM 提供独特贡献 | 同知识、同预算的 no-LLM 对照及可重复效应 | 若无显著效果，避免将 LLM 写成贡献 |
| 已填补研究空白 / 首次工作 | 系统综述、相邻领域去重、同行基准比较 | 当前不能主张 |

## 6. 优先研究方案与决策门槛

建议以方案 C 作为真实性验证锚点、方案 A 作为规则 baseline；先建立小规模 matched workload / fault episodes，再决定是否训练方案 B。C 不是文献新颖性的保证，真正可能贡献的是事件配对、健康 / 故障标签、Metric–Trace 验证和独立 detector test。

在进入 B 前建议达到以下门槛：

1. 服务和实例映射、时间戳、Metric / span schema 均已确认；
2. 至少能重复执行目标故障并由 health oracle 确认服务退化；
3. 具有足够多的成对 Metric–Trace 事件，能将 incident / service / fault type 留出；
4. 规则 baseline 能生成符合结构的 paired samples，且 detector 没有仅识别人造标记；
5. LLM 对规则 baseline 的边际价值已量化，若无价值，可去掉 LLM。

若第 1–3 项不足，优先做受控数据 / benchmark 建设，不应在缺少配对监督时训练 joint generator。若仅有离线历史 Metric 而无 Trace / 负载 / 故障真值，研究问题应收窄至该数据实际支持的范围。

## 7. 证据来源

- 微服务 / LLM 论文边界：[专题 AIOps Review v4](reviews/aiops-knowledge-review-v4.md)、[专题对比表](../../exports/llm-microservice-anomaly-generation/comparison.md)。
- TSAD normality、因果、上下文与评测缺口：[TSAD 问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md)、[TSAD final synthesis](../reviews/tsad-final-synthesis.md)。
- 单篇证据：[TraceLLM](../../papers/aiops/tracellm/notes.md)、[LLM-AP](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md)、[Synthetic Time Series](../../papers/aiops/synthetic-cloud-microservices/notes.md)、[GenIAS](../../papers/aiops/genias/notes.md)、[AIOpsLab](../../papers/aiops/aiopslab/notes.md)、[MODIFy](../../papers/aiops/modify/notes.md)、[CAPMix](../../papers/capmix/notes.md)、[CAROTS](../../papers/carots/notes.md)。
- RedLamp 原文公开版本：[arXiv HTML](https://arxiv.org/html/2505.20765)，§§3.2–3.6、4.2–4.6。
- AMulSys 摘要级边界：[出版方页面](https://www.sciencedirect.com/science/article/pii/S1566253525000909)；[获取状态](../../papers/aiops/amulsys/availability.md)。
