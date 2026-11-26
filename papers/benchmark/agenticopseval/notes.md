# AgenticOpsEval：把证据与因果链纳入微服务 Agent 诊断评分

## 论文身份与证据边界

- **论文标题：** *A Multi-Dataset Benchmark for Evaluating LLM Agents in Microservice Failure Diagnosis*（项目名 AgenticOpsEval）。
- **作者/版本：** Yuanhong Cai, Xiaohui Nie, Kanglin Yin, Changhua Pei, Yongqian Sun, Shenglin Zhang, Haibin Liu, Guiyang Liu, Xidao Wen, Fang Situ, Dan Pei；arXiv:2606.29193v1，2026-06-28。[论文](https://arxiv.org/abs/2606.29193) · [官方数据页](https://www.aiops.cn/gitlab/aiops-live-benchmark/agenticopseval)
- **本地材料：** [PDF](../../../sources/papers/benchmark/AgenticOpsEval_2606.29193.pdf) 与完整 HTML 派生文本；本轮已完整阅读正文。该 v1 没有独立附录。
- **代码状态：** 论文称评分代码随项目提供；当前可取得的 GitLab 仓库快照为 `69cf36430b43024d02530c610b1a4738b5c9a7fb`，树内可见 README 和数据目录，但本次克隆的版本未包含 scorer/runner 源码。因此下面的评分机制来自论文原文，不是代码复现结论。没有下载数据或执行代码。

## 1. 动机与双数据集设计

最终答案指标无法区分“碰巧答对”与“查到了与结论一致的证据”。AgenticOpsEval 的设计主张是把诊断的过程证据纳入可计算评价：先判断定位实体和故障类型，再检查轨迹是否覆盖预期观察点，最后对正确答案上的推理长度进行有限惩罚。

论文提供两组互补数据：AIOps2025 以轻量的逐模态 key evidence 标注为主；RCA100 进一步将 cause→propagation→impact 链逐步标注，并要求与数值 checkpoints 对应。前者适合大规模比较，后者提供更细的因果链约束。它们不是相同标签精度下的两个子集，分数不可直接横比。

## 2. AIOps2025：大规模逐模态证据

### 环境、故障与观测

- HipsterShop 部署于 8 台 VM，共 33 pods，包含 10 个应用服务及 TiDB/Redis 组件。
- 400 个案例、18 种故障类型、9 个故障类别、3 个注入层级（service 195 / pod 123 / node 82）。注入使用 Chaos Mesh 等受控机制；参数在规定范围内变化。
- 18 天数据约 11.9 GB、2,835 个 Parquet 文件、2.69 亿行；指标来自 Prometheus/APM 与节点/TiDB 监控，日志来自 Filebeat，trace 来自 Jaeger。hour/day/modality 分区使使用者可仅读取目标时间段。
- Metrics、Logs、Traces 用 service/pod 标识关联。统计标注显示 250/400（62.5%）案例至少需要两种模态，124/400（31%）需要三种模态；这说明数据有跨模态证据需求，但并不证明某次 Agent 决策确实使用了它们。（§4.1–4.5，Tables 2–3）

在原有应用层之下加入 TiDB 与 Redis 的资源、I/O 和网络扰动，目的是让故障可以从持久化或缓存层经依赖传播到应用服务，检验 Agent 是否停留在上层症状。§6.1 将不合格注入分为三类：重试/降级/扩缩容将故障吸收；有告警但痕迹不足以支撑专家复原；故障实际行为偏离意图，例如 CPU 压力诱发 OOM kill。两套集合从更大的注入池保留可追查的观测足迹。这可能改变困难样本分布，论文未给出完整剔除分布。

### 标签如何建立

1. 多模态异常检测器从原始指标、日志、trace 提议候选观察点；
2. 三名 SRE 分别独立确认/修订每个案例的候选证据；
3. 高级 SRE 仲裁分歧；
4. 每个故障场景重复注入多次后才纳入数据。

最终标注包含故障 `(category, type, instance)`、定位字段、各模态 `key_observations`、必须命中的 `key_metrics`，以及语义等价的故障表述 `fault_description`。这将注入目标与“专家认为观测中可见的内容”区分开。示例为 `emailservice` 的 service-level CPU stress：标签同时列 `pod_processes`、响应时间和 `pod_cpu_usage` 观察，并要求覆盖 CPU 指标；故障类型可由“CPU saturation”等等价说法匹配。（Fig. 4）

### 评分定义

四个维度构成总分：

\[
\mathrm{Final}_A=100(0.4\,LA+0.4\,TA+0.1\,Exp+0.1\,Eff)
\]

- **Location Accuracy (LA)：** 预测组件与标注实体严格匹配比例。服务名不等于具体 pod；pod fault 要精确到 pod。网络故障有针对性例外：命中源或目的端实体都可计定位。
- **Type Accuracy (TA)：** 先匹配预定义故障同义描述关键词；无命中时再做 embedding 相似度回退。模型的 reason 字段只取前 20 个词，避免堆同义词刷分。
- **Explainability (Exp)：** \(E_m/E_t\)，其中 \(E_t\) 是 key metrics 与 key observations 的并集，\(E_m\) 是轨迹输出中通过严格名称/关键词/trace 节点匹配命中的预期证据。每条 observation 只检查前 20 个字符。
- **Efficiency (Eff)：** 在 LA 正确案例上的平均轨迹长度 APL：\(\min(1,\exp(-(APL-5)/5))\)。只在定位正确案例上计长度，减少“很短但答错”策略的奖励。

简例：如果 expected evidence 有 CPU、延迟、trace 三项，Agent 只报告 CPU 和延迟，则 Exp=2/3；但即便最后的故障标签猜对，仍只有部分证据覆盖。反过来，覆盖很多证据也不能抵消定位与类型两个各占 40% 的答案维度。

**指标限制：** APL 是 `reasoning_trace` 长度的代理，不是实际 token、工具调用次数、墙钟时间或 API 花费。证据项基于字符/关键词匹配，并不确认 Agent 的因果推理真的使用了该证据。AIOps2025 的 Final_A 中过程分占 20%，仍有 80% 是结论字段。（§4.4）

## 3. RCA100：类型化传播链与数值证据

### 环境与案例

RCA100 含 103 个 Chaos Drill 故障事件，部署在 Alibaba Cloud ACK 的 OpenTelemetry Demo Store 上，配合托管 RDS、Redis、消息总线；约 12 个多语言微服务。使用 OpenTelemetry + ARMS Agent 收集 signals，Aliyun UModel 把 APM、Kubernetes、云资源里的实体统一到可比较的 entity ID。

包含 28 种根因类型、6 个语义大类；约 3.4 GB / 1.16 亿行，含 Metrics、Logs、Traces、Events、Alerts、Topology。90 个案例从单个 alert entity 开始，另外 13 个 composite case 不给单一告警实体，避免所有题都暗示“只查这个实体”。论文称标注实体与拓扑参考一致性 98.06%，跨模态来源引用完整性 100%。（§5.1–5.5，Table 6）

### 根因、传播与 checkpoint

标签包含：故障类型、根因 UModel entity、按 cause→propagation→impact 排列的链步骤、每步的可观测性检查点。91 个是 3-step，12 个是 4-step；共 661 个 checkpoint，约每案 6.42 个，99.5% 带有 comparator/value/unit 数值约束。

论文 Fig. 6 的真实标注例：`payment → checkout → checkout::PlaceOrder`。第一步 payment 要达到特定 error_count/error_rate 条件；第二步 checkout 有对应错误增长；最后一步的 PlaceOrder 操作也有错误阈值。它比“日志提到 payment 出错”的文本标签更可判定：只说对服务名而没有满足数值条件，不能算完整的证据路径。

Fig. 6 的 HTTP 5xx 案例中，payment 是 cause（error_count≥8,829、error_rate≥0.50），checkout 是 propagation（error_count≥8,828、error_rate≥0.50），checkout::PlaceOrder 是 impact（error_count≥8,828）。Fig. 6 示例数值按原图记录。661 个 checkpoints 中 98.2% 落在 Metrics，但 92.2% 的链涉及至少两类实体，20/103 跨 APM/K8s，要用 Events 的生命周期信息和 Topology 的实体映射；每例平均触及 4.02/6 模态。计数分布与调查时其他证据的重要性并不相同（§5.3、§5.5）。

### 评分

\[
\mathrm{Final}_B=100(0.4\,Entity+0.3\,Fault+0.3\,Process)
\]

Entity 评价 UModel 实体定位，邻接拓扑实体有部分信用；Fault 对 28 类类型评分；Process 联合考察因果链节点与观测 checkpoint。论文未把 Process 的全部边界情况简化成公开代码可核验公式；在当前项目未能读取 scorer 的情况下，不推测节点与 checkpoint 的内部权重。

常见信号是 request count（204 checkpoints）、平均 latency（178）、error count（97）等。RCA100 的 103 案例中约 95 个涉及两种以上实体类型传播；约 20 个跨 APM 与 Kubernetes 实体类型。Top 4 故障类型占 44.7%，其余类别仍有长尾，整体指标需与类别明细一起看。（§5.3–5.6）

权重鼓励先找到可操作的对象和类型，再用证据或链佐证。AIOps2025 只有正确定位的题参与 APL，能抑制错误短轨迹，却使效率条件化于各系统自己的命中子集。RCA100 相邻节点有部分分，能区分近错，却可能使拓扑近邻成为保守猜测；Process 对参考链的覆盖无法单独验证替代证据或因果使用。后两项是待检验的指标激励，未发现可复核 scorer 支持更细公式。

## 4. Agent 交互与实验结论

AIOps2025 以结构化多模态文件和任务提示供 Agent 调查；RCA100 用告警/实体、拓扑及六模态观测支持因果链核验。论文重点评价答案字段和标注证据，不等同于 NIKA 那样对动态网络工具调用、环境反馈和业务影响作完整协议评价，也没有安全修复任务。

AIOps2025 进入 2025 CCF AIOps Challenge，CCF 有 561 队；RCA100 对应 Tianchi 赛道，有 5,532 队；6,093 是两项赛事合计。论文未提供完整多模型性能对照。参与规模证明协议可实际运行，不是单独的科学有效性证据。两数据集在故障集、输入入口和过程标签颗粒度不同，不能把成绩当作同一排行榜。

## 5. 数据质量、捷径风险与论文局限

### 论文明确承认

- 两个 demo 系统约十余个服务，真实生产规模迁移未验证；
- Chaos 注入较干净，生产常见并发故障、间歇性波动、长期累积退化覆盖有限；
- 专家主参考路径可能遗漏合法替代诊断路径，进而低估得到正确结论的 Agent；
- AIOps2025 的效率是轨迹长度代理，未体现实际 Token、端到端延迟和工具成本。

### 基于设计的待测风险（非论文已证实的泄漏）

- 固定故障模板和实例选择可能让模型记住标签—实体关联；
- key evidence 受检测器提议影响，即便专家修订，也需检查候选生成是否遗漏反例；
- 关键词/embedding 类型匹配、前 20 词截断有明确刷分控制，但仍未证明文本解释与因果推理一致；
- RCA100 checkpoint 数值证据更精细，但数值阈值也可能成为可记忆签名。

§6.2 建议将源数据库和厂商 API 的异构转换放在统一工具层。AIOps2025 用服务/pod 名对齐，RCA100 用 UModel 对齐 APM、K8s、云资源的别名和对象关系；数据分片、时间戳、空值、类型的标准化使按事件读取可行。§6.4 提出的后续用途包括多模态 TSAD、带链与拓扑的因果发现、专家/Agent 轨迹偏差分析及学习。这些是复用方向，论文未对其效果作统一实验验证。

## 6. 开放性与实现核对

论文描述已释放数据与评分代码；本次公开 GitLab 克隆只有数据页面/README 和目录信息，未发现评分/执行代码文件，因此不能验证论文分数的具体字符串匹配、阈值或 checkpoint 聚合实现。未下载约 15 GB 数据，也未运行基准。需要后续获取带 scorer 的正式 release 并固定版本，才能做到 line-level 代码复核。

RCA100 §5.1 将答案放在独立 answer-key 包，公开任务契约不含答案。论文报告跨模态引用完整性 100% 和实体—拓扑对齐率 98.06%，两者是结构检查，不是证据充分性。RCA100 资料正文标注 CC BY-NC-SA 4.0，公开仓库 README 将 AIOps2025 标注为 CC BY-NC 4.0，实际复用仍需按对应数据包的许可确认；论文 arXiv 许可与数据许可分开。

## 7. 对数据集论文的启发

对传统 RCA 和 Agent 共享一个数据集时，应明确分开：最终根因标签、每模态证据、因果传播路径、工具调查轨迹、真实执行成本。AIOps2025 展示以较轻标注支持大量案例；RCA100 展示对少量事件做更深的链和数值证据标注。两层标签可以用于不同成本的任务，但要分别报告。

若采用过程指标，应同时记录可替代证据路线，避免精确复现单一 reference route 成为隐式目标。效率至少报告实测 tokens、请求/工具数和时间，避免把输出长度误认为成本。真实案例数量、专家校验和比赛规模不能替代对故障族、部署模板与拓扑的留出评测。

关联：[CTBench](../ctbench/notes.md) 的专家命令路线、[OpenRCA](../openrca/notes.md) 的历史企业遥测，以及[数据集设计启发](../../../notes/benchmark/dataset-design-insights.md)。
