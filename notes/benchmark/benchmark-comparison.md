# 六篇 AIOps Benchmark 论文比较

核验范围仅限用户指定的六篇论文。数值按论文版本记载，未在原文明确报告的字段写 **Not Reported**；当前代码仓库的后续版本不与论文实验版本混用。单篇身份与来源见[论文清单](paper-inventory.md)，逐篇分析见 [`papers/benchmark/`](../../papers/benchmark/)。

## 数据与任务设计

| 论文 | 研究对象 / 环境 | 规模与数据模态 | 故障及构造方式 | Ground Truth 与质量控制 | 传播 / 多根因 | 主要任务与指标 |
| --- | --- | --- | --- | --- | --- | --- |
| [RCABench](../../papers/benchmark/rcabench/notes.md) | TrainTicket 测试床，50 个微服务，动态负载 | 1,430 个有效失败；9,152 次注入尝试；metrics、logs、traces、拓扑/调用关系、SLI | 六类故障；31 种候选故障类型中筛出 25 种有效类型；控制注入位置/强度并收集遥测 | 注入代码/服务层级标签，并要求 user-facing SLI 有可辨异常；报告 84.4% 初始注入未产生异常而被排除 | 核心是层级传播标签与复杂依赖；同时多根因任务：Not Reported | 传统 RCA 定位；Top@1/Top-k 与运行时间，11 个基线；不测 Agent 工具过程或修复安全 |
| [NIKA](../../papers/benchmark/nika/notes.md) | Kathará 仿真的网络场景与拓扑 | 5 个场景、54 种 issue、640 个配置；实验用 150 个 incident；公开 900+ traces；拓扑均值约 11/27/101 节点；网络配置、主动测量、流量/遥测 | 以场景、issue、traffic 组合任务；注入网络/主机故障、资源竞争等 | 由场景和注入 issue specification 给定；可复现但不是盲标的生产根因 | 复合故障可扩展，论文基线主要按单个 issue 任务评测；传播链标签：Not Reported | Detection/localization/RCA；正确率、检测时间、token、工具调用/错误、流延迟、丢包、SLO。MCP AAL 记录调用和状态；不评测 mitigation |
| [OpenRCA](../../papers/benchmark/openrca/notes.md) | 三个企业软件系统的清理后故障遥测 | 335 failures；>68 GB metrics/logs/traces；Telecom 51、Bank 136、Market 148 | 历史真实失败记录，不是统一故障注入；问句从 RCA 元素组合生成并人工检查 | 工程师校准可追溯性、遥测存在性、时间/标签对应；问答覆盖所需根因元素 | RCA 元素可由多个字段组成；因果传播步骤标签：Not Reported | LLM RCA；完全匹配和部分正确率，比较 sampling 与 RCA-agent。Agent 用 Python Executor 查询数据，不执行修复 |
| [Constructing Large-Scale](../../papers/benchmark/constructing-aiops-benchmark/notes.md) | 三套任务独立：多公司生产 KPI、合成多维指标、China Mobile sysA 失败注入 | A：表格称 26 series / 4,821,526 points、60–207 days（正文提 7 KPI，范围有歧义）；B：400 案例；C：169 injected failures。模态从 KPI/结构化指标到 traces、细粒度 measures | A 为生产异常；B 用根因属性组合、GRE 聚合修改、噪声与过滤生成；C 为七类数据库/容器/节点故障注入 | A 有经验人员标签与延迟报警约束；B 标签来自构造的根因属性组合并筛除混淆；C 记录注入故障时间和根因 | C 有组件/服务关联；显式多跳传播标签：Not Reported | 异常检测 F1/延迟、根因定位 F1、失败发现/诊断及挑战赛排名；不支持 Agent 过程评价 |
| [AgenticOpsEval](../../papers/benchmark/agenticopseval/notes.md) | HipsterShop 与 OpenTelemetry Demo Store 两类微服务测试环境 | 503 cases、约 15.3 GB；AIOps2025 400、约 11.9 GB；RCA100 103、约 3.4 GB。metrics/logs/traces/events/alerts/topology（完整六模态在 RCA100） | AIOps2025 用 Chaos Mesh；RCA100 用故障演练；覆盖资源、网络、运行时、中间件/数据库、应用逻辑等 | 专家标注和复核；RCA100 标签含 fault type、实体、cause→propagation→impact 与数值证据 checkpoints | 明确传播链；RCA100 含 13 个 composite cases；AIOps2025 的多根因定义：Not Reported | LLM Agent 的 Localization/Identification/Reason；实体/类型/证据覆盖与推理长度。后者不是实际 Token/成本；未发现可审阅的 agent tool-use runner |
| [CTBench](../../papers/benchmark/ctbench/notes.md) | 脱敏电信维护案例及多厂商设备 CLI 回放 | 234 tasks：126 RCA、108 path restoration；CLI 观察、设备/拓扑/协议 metadata | 历史维护任务与记录命令输出，由专家整理；mock backend 重放，不动态注入/修复 | 15 位资深专家编写，独立专家盲解并审查；359 候选保留 234；gold answer 为 (node, object, cause) 或有序路径 | metadata 表达多跳传播、部分可观测、复合故障；golden action trajectory 表示参考证据路线 | Task accuracy、IoU/path 指标、golden-action coverage、latency/rounds/tokens；单次 Pass@1，1h timeout，无每任务 token/tool 步数上限 |

## Agent 交互与过程评价

| 论文 | Agent 可见信息 / 工具 | 动态调查与反馈 | 是否评价过程 | 成本、安全与主要边界 |
| --- | --- | --- | --- | --- |
| RCABench | 传统算法输入的遥测和拓扑 | 非 Agent 任务 | 否 | 评价计算耗时；无工具/Token/修复安全协议 |
| NIKA | 场景拓扑、配置、主动测量工具，30+ MCP interfaces | 是；工具请求可返回环境状态，系统记状态快照 | 是，记录工具轨迹、耗时和服务影响 | 报 token/调用等，但不是安全修复基准；未支持 mitigation 评价 |
| OpenRCA | 关联 telemetry、候选 RCA 元素、时间窗；Agent 通过 Python 查询 | 迭代查询，有反馈；无外部状态变更 | 有 Agent 方法比较，未提供逐步诊断正确性/证据使用的独立标准 | 论文强调数据上下文成本；不评 remediation 风险 |
| Constructing Large-Scale | 按数据集和竞赛协议提供指标/案例 | 主要离线任务，不是 Agent 环境 | 否 | 检测延迟可计入排名；无 Agent token/工具预算 |
| AgenticOpsEval | 自托管服务 telemetry、告警/描述及结构化证据标签 | 评价 reasoning/evidence 结果；逐任务工具 API 协议细节：Not Reported | 是，证据覆盖/因果链加最终答案 | APL 是路径长度代理，不是实际成本；无行动安全评估 |
| CTBench | 设备/CLI 回放工具和结构化任务接口 | 顺序调查；输入读取得到预存输出，状态不动态演进 | 是，golden action route coverage | exact route 会排除等价替代命令；无每任务 Token/步数预算；不评动态维修 |

## 设计思想及适用场景

1. **难度和运行语境（RCABench）**：适合研究传统 RCA 是否真正学到传播与因果，而不是追随最显眼的异常；SLI 验证能排除“注入成功但用户无感”的空案例。
2. **可控网络交互（NIKA）**：适合比较网络 Agent 的工具调用、探测策略、调查成本和诊断期间的服务影响。它提供的是可复现的仿真，不代表生产外部效度或修复安全。
3. **大规模异构真实遥测（OpenRCA）**：适合衡量多模态、长上下文根因分析；代价是历史标签、候选答案和受控采样影响任务开放性。
4. **数据集谱系与不同任务分轨（ZTE paper）**：说明 KPI 检测、根因定位、故障发现不能被一个标签/指标代表；综合多轮挑战使用提供了复现和社区对比基础。
5. **标记中间证据（AgenticOpsEval）**：适合评估 Agent 是否覆盖诊断证据和传播链；最终答案、证据和实际成本需要分开评分。
6. **专家流程与部分可观测（CTBench）**：适合检查 Agent 是否沿着可解释的设备调查路线工作；固定路线 coverage 只适合作为 reference-route proxy，不能等同于因果推理质量。

总体上，这六项工作并非简单地从“传统”升级到“Agent”。它们测量不同对象：受控算法定位、网络工具交互、历史企业 RCA、独立数据集挑战、显式证据轨迹和专家设备命令流程。跨论文比较应先对齐任务边界、答案空间和标签来源，再比较分数。特别是 AgenticOpsEval 的 reasoning-length、CTBench 的 reference-route coverage 与 NIKA 的实际工具调用/资源描述不是同一种过程指标。

## 本次实际研究深度

本轮 Engine Planner 仅自主选择 NIKA 与 CTBench，Executor 对两篇做选段分析，且输入消耗超出目标。Judge 未完成；Reflector/后续 Planner 未执行。因此这份横向比较是基于六篇本地原文/官方材料的受限专题综合，不能宣称六篇都被 Engine 完整精读并通过独立评估。代码侧只核对公开项目说明和入口/目录映射，没有克隆运行大型系统或故障注入。
