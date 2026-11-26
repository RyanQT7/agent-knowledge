# Benchmark Knowledge Review v1 — AIOps 数据与 Agent 评价

## Review 范围

本 review 综合固定六篇论文：RCABench、NIKA、OpenRCA、*Constructing Large-Scale Real-World Benchmark Datasets for AIOps*、AgenticOpsEval、CTBench。它们并非同一数据集或同一任务的六个可直接排名版本。Engine 的首次轮次只对 NIKA 与 CTBench 进行选段分析，未完成 Judge 和后续反馈规划；其他论文依据本地全文/官方公开材料补充专题分析。没有把这一轮标成六篇都经过 Engine 精读和独立核验。详细身份和阅读状态见[清单](../paper-inventory.md)。

## Benchmark 的研究发展

这组工作呈现的变化不只是规模增加，而是评价对象逐步展开：

- 从数据集能否区分 RCA 算法（RCABench），转向数据是否具有用户可感知影响、挑战算法是否真正需要传播/因果建模。
- 从静态答案题转向工具和场景交互（NIKA），同时记录诊断轨迹、工具成本和诊断期间服务影响。
- 从规模化异构遥测与历史事件（OpenRCA）转向每条诊断应依赖哪些证据（AgenticOpsEval）。
- 从终态答案转向专家在部分可见、多厂商 CLI 环境中的调查步骤（CTBench）。
- ZTE 论文将 KPI 异常、结构化根因定位与故障诊断分成不同数据集，提示“一个大型综合数据集”并不等于一个无差别任务。

因此，Benchmark 的可信度取决于研究问题、样本生成、标签和 evaluator 是否对齐，而非单纯样本数或模态数。

## 真实系统、测试床与回放

六篇论文的“真实”含义不同。OpenRCA 使用企业系统历史故障遥测，但做了筛选和工程校准；ZTE 的数据集同时包含多企业生产 KPI、算法可控合成案例和 China Mobile sysA 故障演练；RCABench 在 TrainTicket 测试床注入故障，并按 user-facing SLI 验证；NIKA 在可配置网络仿真器中生成可重复场景；AgenticOpsEval 在 HipsterShop 和 OpenTelemetry Demo Store 测试系统中构造注入案例；CTBench 从脱敏维护案例和实际设备命令记录构造固定回放。

这些证据各有边界：生产遥测不保证标签因果完整；注入故障不代表生产分布；合成数据可控但可能暴露模板；命令回放可重复但不包含状态变化。论文应把证据来源分层写清，不能用“real-world”一个词把这些设置混为一谈。

## Ground Truth 与数据质量

至少有四类 Ground Truth：

1. **注入规范型**：NIKA、RCABench 和部分 AgenticOpsEval 把配置/脚本作为根因真值。它易于重复，但应验证故障是否可观测、是否影响用户，以及注入点是否等同实际最早影响点。
2. **历史事件/工程记录型**：OpenRCA 与 ZTE 的部分数据依靠企业 RCA 和工程师校准。它更接近运维，但可能缺少竞争原因、不确定性、边界精度和标签一致性。
3. **专家任务与动作型**：CTBench 盲解题并审查答案、可解性和参考动作；AgenticOpsEval 标记关键证据和因果链。它揭示了任务路线和证据要求，但专家 route 未必是唯一正确路径。
4. **构造属性型**：ZTE Dataset B 从根因属性组合生成标签，并过滤不可区分组合或噪声异常。它适于可控实验，但要用跨模板/反事实测试检验模型是否学到构造规则。

可靠流程应将根因实体、故障类型、起止时间、传播边、影响范围、业务后果和证据来源分开记录；保留多根因、Unknown、范围区间和争议，而不是无痕压成单一标签。RCABench 的有效注入率说明注入尝试、实际遥测异常和业务影响是不同状态。

## Shortcut 与评估可信度

RCABench 的核心观察是浅显的根因显著性会使简单方法超过复杂方法；ZTE 对合成数据进行混淆筛查；OpenRCA 的 oracle sampling 和候选集说明答案空间可见性会改变难度；AgenticOpsEval 主张把证据标签纳入评测；CTBench 将 gold route 计分，但其固定接口刻意排除替代命令。这些设计共同说明，越精细的标签并不自动消除 Shortcut。

可信的 Benchmark 应预先明确泄漏威胁模型，使用按故障族、模板、节点、拓扑、时间分组的测试集；公布简单规则和单变量基线；提供去字段、时间错位、拓扑扰动等负对照；报告每类样本量、数据剔除链路和标注不确定性。论文作者报告的问题与我们提出的风险推测要分别标注。

## 传统 RCA 与 Agent Benchmark

传统算法主要测异常/根因答案：事件级 precision/recall、F1、Top-k、延迟和资源。Agent 任务多了调查过程：可见工具、动作空间、状态反馈、证据引用和资源边界。NIKA 可观察 MCP 调用、状态与诊断时服务影响；AgenticOpsEval 提供证据覆盖和因果链；CTBench 提供专家动作路线；OpenRCA 的数据查询 Agent 展示长上下文检索机制。

它们的过程指标构念不同。Token/调用数是成本；golden action coverage 是参考路线覆盖；证据点覆盖表示引用/命中标注证据；它们均不能单独证明因果理解。最终正确、证据充分、调查有效率、资源费用和动作安全应分开报告。对可变状态环境还应评价 stop/continue 判断、错误恢复以及安全拒绝。

## 对网络 AIOps 数据集的启发

有价值的方向是把网络拓扑传播、故障时间边界、多模态关联和证据可追溯性纳入同一事件格式，同时用分组切分和负对照控制 Shortcut。传统异常/定位模型、一次性 LLM 和 Agent 应使用相同事件标签，但各自报告不同任务指标；Agent 还需有工具调用与安全预算。用户提到的 inode、process count、fd、故障角色绑定和长尾现象目前在本知识库没有对应原始数据或统计，不能作为本文已验证发现。

## 研究缺口与潜在论文方向

- **统一事件本体**：记录注入/真实触发、根因、传播节点、症状、影响、边界和证据，并允许多根因、Unknown 与置信范围。
- **传播感知且抗 Shortcut 的切分**：跨故障族/节点/拓扑/时间，并附公开的特征泄漏和简单基线审计。
- **Agent 过程可比评价**：允许等价调查路径，分别度量证据充分性、工具效率、资源成本和安全性。
- **跨基准外部效度**：同一模型/方法在仿真、回放、注入测试床和真实事件上的迁移误差。
- **可复现数据版本链**：数据、脚本、标签、工具接口和 scorer 固定到可追溯版本。

这些是可研究方向，不是已经证明的新颖性。对本地数据的实际创新主张需等数据字典、样本、标签、评估器和现有基线资料补齐后再立项。具体问题见[Research Gaps](../research-gaps.md)；数据集对照边界见[设计启发](../dataset-design-insights.md)。

## Skill Evolution 结论

本轮六篇对 Benchmark 维度有明显价值，但 Engine 发生超预算，独立 Judge 和跨轮反馈未完成。现有 paper-reading、AIOps reading、paper-code-discovery 与 code-reading 的工作流并未出现足以支持修改 Skill 的、经独立确认的重复缺陷。**No Skill Update Needed**；若后续多篇任务持续漏掉 Ground Truth/Shortcut 或 Agent 过程指标，再依据复现记录提出最小候选。
