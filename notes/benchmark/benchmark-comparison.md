# AIOps Benchmark 论文比较：原六篇与 NetArena

范围包括原专题六篇和本次新增的 NetArena。NetArena 是动态、可执行的网络 Agent Benchmark，与离线 AIOps/RCA 数据集不是同一任务类型。数据身份与阅读状态见[论文清单](paper-inventory.md)；逐篇机制详见 [`papers/benchmark/`](../../papers/benchmark/)。`Not Reported` 表示对应论文未在可核对版本明确给出，不能用当前仓库 README 或另一篇论文补齐。

## 数据来源、环境与 Ground Truth

| 论文 | 环境与规模 | 数据模态 / 故障构造 | Ground Truth 与质量控制 | Not Reported / 主要盲区 |
| --- | --- | --- | --- | --- |
| [RCABench](../../papers/benchmark/rcabench/notes.md) | TrainTicket 50 微服务；9,152 次注入尝试筛成 1,430 个有效案例、25 类 | Prometheus metrics、traces、关联 logs、L4/L7 与调用拓扑；六类故障、资源/网络/应用等注入 | 注入位置形成细粒度层级标签；user-facing success-rate/latency SLI 验证影响。84.4% 初次注入未有可辨异常 | 只用 service 级标签对比主方法；多根因分布、生产环境外推和 Agent/修复评价：**Not Reported / 未评** |
| [NIKA](../../papers/benchmark/nika/notes.md) | Kathará；5 场景、54 issue 类、640 个任务配置；论文实验使用 150 incidents；4 类拓扑平均约 11/27/101 节点 | 网络配置、流量、主动/被动观测；`tc`、`stress-ng` 等注入；工具结果和运行状态 | 注入 issue/目标实体提供可重复标签；Detection、Localization、RCA 目标逐步增加要求 | 专家标注一致性、生产真值和修复安全：**Not Reported / 未评**；仿真不是生产网络 |
| [OpenRCA](../../papers/benchmark/openrca/notes.md) | 三个企业系统 335 cases（Telecom 51 / Bank 136 / Market 148），约 68.5 GB、5.23 亿行；28 种原因 | 历届 AIOps Challenge；Bank/Market 含 metrics、logs、traces，Telecom 无 logs；GPT‑4o 将根因元素子集变成任务问句 | 从 1,753 条记录池出发，工程师去除遥测缺失/根因不可追溯/时间错配；component/time/reason 为组合标签 | 标注者间一致性、每案证据真值、Agent 的逐步正确性/实测成本：**Not Reported**；闭集候选与给定时间窗限制开放搜索 |
| [Constructing Large-Scale](../../papers/benchmark/constructing-aiops-benchmark/notes.md) | 三套独立基准：A 多公司 KPI 26 series / 4.82M points / 60–207 days；B 400 结构化案例、5 属性维，定位平均每分钟订单数异常的属性组合；C sysA 一个月 169 注入事件、7 类 | A 五公司生产 KPI；B Suning 交易记录上以 GRE + 噪声构造多维异常；C China Mobile Zhejiang sysA 的 traces/KPIs/metrics 与数据库/容器/网络注入 | A 工程师标签与延迟评分；B 根因属性组合并过滤不可区分/非目标异常；C 注入时间和目标实体标签 | Dataset A 正文“7 KPI”与初版表格“26 series”口径不清；B/C 逐个生成脚本版本、Agent 评价：**Not Reported / 未评** |
| [AgenticOpsEval](../../papers/benchmark/agenticopseval/notes.md) | AIOps2025：HipsterShop 400；RCA100：Demo Store 103；总约 15.3 GB | 前者 Metrics/Logs/Traces、18 faults/9 categories；后者再含 Events/Alerts/Topology、28 faults/6 groups；Chaos drills | 多模态证据由检测器提议、3 位 SRE 独立改标、高级专家裁决并重注入；RCA100 按链步骤给数值 checkpoint | 统一 tool-call API/每任务调用预算和动态修复：**Not Reported / 未评**；公开 GitLab 快照未找到 scorer 源码 |
| [CTBench](../../papers/benchmark/ctbench/notes.md) | 359 候选筛至 234（126 RCA / 108 path）；脱敏多厂商电信 CLI 维护案例 | 命令输出 replay 与拓扑/协议元数据；5 类 RCA 故障和多个独立根因；无实时状态演化 | 15 位资深专家编题；盲解/复核可解性、答案完整性、gold actions 和元数据；争议不收录 | live device、动态状态变更、修复/回滚与独立官方 scorer：**Not Reported / 未提供**；单一精确命令路线使等价证据被低估 |
| [NetArena](../../papers/benchmark/netarena/notes.md) | 三类任务：5,493 节点/6,424 边的 CP 图模拟；Mininet Routing；11 服务/13 网络策略的 Online Boutique K8s；大评估合计 9,250 queries | 动态图/配置、模拟器状态、命令结果、PingAll 与服务连通性；随机参数化任务和故障注入 | constructive 由动作序列执行得到目标态；reactive 隐藏注入、以恢复健康态为真值；安全约束逐步检查 | 模板/模拟器之外的生产泛化、生成器偏差、查询独立性和统一跨应用 latency：**Not Reported / 未证实** |

## 任务、交互、指标和源码

| 论文 | 任务与答案 | 过程 / 成本评价 | 源码与复现状态 |
| --- | --- | --- | --- |
| RCABench | 传统微服务根因 Top@K、MRR、耗时；论文保存方法级/容器/服务等标签，主表按可比 service label | 无 Agent trajectory、Token、工具或恢复评价 | [Aegis](https://github.com/OperationsPAI/aegis) 当前是整合后版本；静态分析当前 temporal validator、SLI sampler、GT/evaluator；未找到可直接还原论文 SLI 注入门禁的当前实现，未执行 |
| NIKA | Detection / Localization / RCA；检测、目标实体及故障类型逐步增加答案要求 | 论文报告时间、Token、步骤、工具数量和错误；框架另可记录流时延/丢包和 SLO，未评修复 | [sands-lab/nika](https://github.com/sands-lab/nika) 当前源码 task/fault 模型、root-cause IDs、scoring 静态分析；论文按候选 mask 导出混淆矩阵 accuracy，当前集合 F1 另计 |
| OpenRCA | 从七种 component/time/reason 字段组合中出题；Correct 要所问字段全对，Partial 至少一项对；±1 min 时间容差 | RCA-Agent 用 Controller + Python 查询 metrics→traces→logs；未有标准化证据质量/工具成本指标 | [microsoft/OpenRCA](https://github.com/microsoft/OpenRCA) 的 generate/evaluate/Controller/Executor 静态阅读；未装环境/下载外部数据 |
| Constructing Large-Scale | A KPI 异常检测，B 多维属性定位，C 失败发现/诊断，分别使用 F1、延迟或竞赛规则 | 主要离线算法/竞赛评价，不含 Agent 工具过程 | `iops/evaluation/evaluation.py` 静态确认缺失时间补零、异常段 early detection 处理及全局 F1；数据集与生成/评分仓库分散，未跑实验 |
| AgenticOpsEval | AIOps2025 是实体 LA、故障 TA、evidence coverage 和 trace-length efficiency；RCA100 是 entity/fault/process | 显式检查所需证据/因果 chain，但 APL 不是实际 Tokens/费用/时延 | 论文描述公开 scorer；当前 GitLab clone `69cf364…` 仅有 README/数据，未能核对评分代码实现 |
| CTBench | RCA 以实体/故障集合 IoU；路径有 endpoint IoU 与 directed-edge IoU；另报 exact answer | Golden-action coverage 是特定专家路线命令 recall；另报真实 Tokens、时延、交互轮次，附录分析 Evidence F1、结构一致性与固定模型 Harness 敏感性；Pass@1、3600 秒超时 | [Hugging Face 数据卡](https://huggingface.co/datasets/netop/CTBench)，文件需接受访问条件；未发现独立官方代码仓库/可读 scorer，未下载/运行 |
| NetArena | Constructive capacity planning 与 reactive routing/K8s，评价最终系统状态 | Correctness、每步 Safety；latency 在 CP 是代码执行时间（不含模型生成），Routing/K8s 主要是修复轮数，不能直接横向比较 | [Froot-NetSys/NetArena](https://github.com/Froot-NetSys/NetArena) `main` 分支静态阅读；见[源码笔记](../../code/benchmark/netarena.md)，未执行 |

## 对照解读

1. **“真实”要拆成可检验属性。** OpenRCA 的历史企业遥测、ZTE Dataset A 的公司 KPI、Dataset B 的真实分布加合成干预、Dataset C/RCABench 的测试床注入、NIKA 的网络仿真、CTBench 的脱敏 CLI 回放，提供的是不同外部效度，不构成线性真实性排序。
2. **注入、影响、症状与根因不能等同。** RCABench 以 user-facing SLI 排除未产生影响的注入；AgenticOpsEval 复注入后让专家确认实际证据；NIKA 的 injection specification 易复现但不等于独立生产根因证据；CTBench 把维护记录和参考动作核验分开。
3. **标签颗粒度不同。** Root-cause entity、fault category、时间、传播链、关键证据、专家动作分别回答不同问题。OpenRCA 的字段 exact match 不与 RCABench Top@K 数值直接对比；AgenticOpsEval 的过程分和 CTBench route recall 也不是同一构念。
4. **过程评价有多层。** NIKA 记录真实工具调用和网络状态影响；AgenticOpsEval 用标注 evidence 与 chain；CTBench 用精确命令路线；OpenRCA 的 Agent 是数据查询机制，但没有对每条过程证据做评分。阅读轨迹、命中参考路线和使用正确因果证据不能互相替代。
5. **效率必须测实际资源。** Reasoning path length 可能只是代理；只有 NIKA/CTBench 类协议直接报告实际 Token/时间/调用，但口径仍需统一。Benchmark 不应把短解释当低成本，也不应将计算成本与诊断质量合成不透明总分。
6. **数据公开不是完全复现。** 源码可见、数据可访问、数据可再分发、评分可运行是四件事。当前 CTBench 数据访问有条件；AgenticOpsEval scorer 未在可见 clone；ZTE 的多套项目不是一体化平台。每个结论须固定论文/数据/代码版本。
7. **动态生成不是自动消除偏差。** NetArena 的随机查询减轻固定题目记忆并可放大评估样本，但实例仍来自指定拓扑、操作模板、故障族和环境执行器。应按生成模板/参数/拓扑分组检查 shortcut，并验证随机查询的统计独立性；这是后续审计问题，不是论文已证实的缺陷。

## 适用场景简表

- 传统微服务 RCA 是否过度依赖显著症状：RCABench。
- Agent 在交互式网络仿真中如何调查并影响网络：NIKA。
- 企业多模态历史遥测的闭集/字段组合诊断：OpenRCA。
- KPI、属性维度和故障诊断数据集谱系/竞赛：ZTE 三数据集。
- 大规模 Agent 多模态 evidence labels 与较深 causal checkpoint：AgenticOpsEval。
- 电信设备部分可观测 CLI 排障及参考调查路线：CTBench。
- 可执行状态转换上的动态网络自动化、最终态正确性与逐步安全：NetArena。

更深的跨论文结论见 [Benchmark Review v1](reviews/benchmark-review-v1.md)；面向本地挑战赛的建议见[数据集设计启发](dataset-design-insights.md)。
