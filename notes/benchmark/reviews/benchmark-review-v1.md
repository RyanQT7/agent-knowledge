# Benchmark Knowledge Review v1 — 从可诊断数据到 Agent 过程评价

## 范围与证据

本 review 综合用户固定的六篇论文。六者不是同一数据集/方法的排名，而是分别检验传统 RCA 难度、网络交互诊断、历史企业遥测、多类型 AIOps 数据建设、证据过程和电信专家排障流程。论文、数据和代码当前版本分列核对；正式笔记见[清单](../paper-inventory.md)和[横向比较](../benchmark-comparison.md)。本轮使用主会话和现有 Skills 完成原文精读与源码静态检查，没有用 Engine 多会话数据冒充六篇论文的研究结果。

## Benchmark 演进的核心：不只是更多数据，而是明确测什么

### 1. 有效样本先于注入数量

RCABench 的 9,152 次注入尝试仅形成 1,430 个 SLI 有效案例，84.4% 尝试未产生用户可见异常。它揭示“脚本返回成功”不等于有效故障。NIKA 通过明确仿真情景和可重放 issue 提高控制性，但注入规格本身仍是模拟标签。ZTE Dataset C 记录受控注入，Dataset A 是多公司生产 KPI，Dataset B 是生产属性分布上的合成异常；三者外部效度不同。OpenRCA 从历史故障中经工程师过滤，改进证据可用性但会选择可解样本。CTBench 用脱敏历史维护任务与命令回放，保持专家工作语境却不模拟动态网络。

因此“真实数据”要拆成来源、运行系统、故障生成/触发、业务影响、标签确认、在线状态变化六个问题。论文写作应把每个层级证据说清，而非仅使用 Real‑world 标签。

### 2. Ground Truth 是一条证据链，不是一列 root cause

这六篇的真值方式构成互补谱系：

- **注入与影响门禁：** RCABench 把根因配置关联到服务层级，再用 user-facing SLI 验证故障可感；NIKA 用 scenario/issue/target 支持可复现定位。
- **历史标签校准：** OpenRCA 将 component/time/reason 组合并由工程师检查遥测与时间可追溯；不过多个合理原因与不确定度表达较少。
- **构造型标签：** ZTE Dataset B 由选定属性组合生成根因，并过滤其它组合不可区分或非目标指标也异常的案例；要进一步排除模型记住生成器。
- **观测证据与因果链：** AgenticOpsEval 从各模态 key observations 延伸到 RCA100 的 cause→propagation→impact 与数值 checkpoints。
- **参考操作路径：** CTBench 对可解性、答案和专家命令路线盲审，并排除不能达成共识的任务；其路径可重复但不是唯一合理路径。

较好的数据模型应分开保存触发/注入、根因、首个可观测异常、传播节点、症状、业务影响、恢复和标签证据。每个字段有来源、时间范围、置信/争议状态及版本。注入目标可以是根因候选，但只有当遥测/影响证据与定义匹配时才升级成有效事件真值。

### 3. Shortcut 风险需要反证协议

RCABench 用简单 baseline 发现根因服务的显著异常可能使复杂方法没有优势；OpenRCA 的 Oracle Sampling（从 1,263 个 KPI 缩为 53 个）明确依赖真值，应视为上界；ZTE Dataset B 通过属性混淆筛选；AgenticOpsEval 由多模态检测器产生证据候选、专家复核；CTBench 的 CLI/replay 与单一 reference route 则有新的模板/路线偏置风险。

这些不是对所有论文或本地数据泄漏的证明。Benchmark 应报告独立事件数、按故障族/模板/实体/拓扑/时间分组的切分、朴素规则和单特征基线、模态/可疑字段消融、标签错配负对照及排除原因。随机窗口切分不能替代独立故障事件的外推测试。

### 4. Agent 过程质量有多种不同构念

- NIKA 的 tool calls、工具错误、响应时间、网络 SLO 变化是实际行动/系统开销；它有交互状态与仿真反馈。
- OpenRCA 的 Controller/Python Executor 是节约上下文的长遥测查询机制，但论文并未为过程证据逐条打分。
- AgenticOpsEval 的 evidence coverage 评价轨迹是否命中专家标出的观察点，APL efficiency 只以轨迹长度作代理。
- CTBench 的 golden-action coverage 是 exact-device/exact-command route recall；route 之外的等价证据可能被漏计。
- RCABench 与 ZTE 的主要对照是离线方法输出，不能因其有多模态输入就称为 Agent benchmark。

所以，正确答案、证据引用、参考路线、真实工具使用、实际资源成本和动作安全必须分别报告。引用一个真指标不保证模型将它用于因果推理；没执行参考命令也不等于没有获得等价观察。效率不能用解释长度替代实测 Tokens、调用和端到端耗时。

### 5. 对传统算法、LLM 与 Agent 的共同协议

同一事件集可服务多个 track：传统 AD 评异常起止/检测延迟；传统 RCA 评根因排序/多根因；LLM 评结构化回答和证据定位；Agent 额外评工具选择、证据覆盖、冗余与系统影响。需要统一数据切分和底层 GT，但允许不同输出任务。公开 model/harness 版本、可见信息、最大步数/时间/Token、重试与失败处理。

同一公式不能解决所有任务。Top‑k、IoU、Exact match、F1、evidence recall、SLO impact 回答不同问题；报告分层值，不将若干维度压成不可解释的单分。需要置信区间时明确其随机来源；CTBench 的 Pass@1 标准误是跨任务变化，不是模型重复运行方差。

## 对网络 AIOps 数据集的启发

若自有数据确实包含多模态遥测、网络故障和复杂角色关系，可借鉴：RCABench 的可感知影响门禁、NIKA 的任务/拓扑/工具状态、OpenRCA 的人工标签校准、ZTE 的多任务数据谱系与构造混淆检查、AgenticOpsEval 的证据和传播标签、CTBench 的盲解可解性与难度元数据。不要一套标签或单一排行榜覆盖 AD、RCA 和 Agent troubleshooting。

目前本地缺少挑战赛样本、数据字典、注入脚本、标签规范、切分及 evaluator。因此 inode/process count/fd、时间边界、类别—角色关联、长尾、传播及公开程度仍是待验证问题；本轮没有修改数据或实验。应先固定这些材料及版本，再讨论和六篇论文相比有哪些事实性差异。

## 与现有 Concepts 的关系

- [Evidence Provenance](../../../concepts/aiops/evidence-provenance.md)：把观测来源/实体/时间与论文所评 evidence coverage、gold action 区分开；本轮提出了一个待审批的跨论文补充。
- [Verification](../../../concepts/aiops/verification.md)：注入是否成功、是否产生影响、标签是否可追溯，是不同验证层。
- [Candidate Space](../../../concepts/aiops/candidate-space.md)：OpenRCA 的候选组件/原因和 Oracle Sampling 会改变开放/闭集难度。
- [Topology-aware RCA](../../../concepts/aiops/topology-aware-rca.md)：RCABench/NIKA/CTBench 对服务图、网络拓扑与运维参考路径使用不同语义。
- [Production Evaluation](../../../concepts/aiops/production-evaluation.md)：历史遥测、受控注入、仿真和回放分别支持不同外部效度。
- [AgentOps](../../../concepts/agentops/README.md) 与 [OpsAgent](../../../concepts/opsagent/README.md)：前者关注轨迹与执行证据，后者关注诊断对象/运维动作；Benchmark 的过程分不能替代实际运行可靠性。

## 研究缺口与潜在投稿方向

值得进一步研究的问题是：(1) 如何统一根因—传播—影响—证据并保留不确定标签；(2) 如何用跨模板/节点/拓扑切分验证对故障机制的泛化；(3) 怎样让 Agent 的证据路径可比且允许等价查询；(4) 如何在同一事件集分轨比较传统方法、LLM 与 Agent 的质量、成本和安全；(5) 公开数据/代码是否真正涵盖生成、标注和评分全链条。

这些属于论文阅读后形成的研究假设，不是已验证创新声明。可能的贡献方向只有在本地数据完整性、基线和分组实验支持后才能确定。具体可测试假设见[Research Gaps](../research-gaps.md)。

## 本轮 Skill Evolution 反思

历史反馈指出上一轮 Benchmark 笔记不够深入。本次逐篇笔记补充了执行过程、真实论文案例、指标解释、实验差异、章节定位和源码—论文版本边界。这是对现有方法的实践性加强，不是受控旧版/候选版对照实验；不能据此声称 Skill 已被证明提升。待审批候选针对 `paper-reading` 的“完整精读深度契约”提出最小补充，状态与评估见对应 Proposal。正式 Skill 未被自动修改。
