# OpsAgent 研究缺口

## 1. Diagnosis 结果缺少可验证的恢复闭环

**GALA+ 补充证据：** 它生成 immediate mitigation、permanent fix、preventative measure 三类建议，但没有报告实际执行动作或独立恢复核验。因此，建议质量仍与恢复效果分开评价。

多数论文的“成功”是预测与事后标签一致，或者工具调用成功；这不等于服务实际恢复。OpsAgent、KRCA、OpsMem、GoS 都由人或外部处置恢复，KnowLution/FlowXpert 有有限生产执行展示，但恢复的归因、SLO 回归和回滚证据尚不统一。

**机会：** 分开记录 `Diagnosis → Approved Action → Change Result → Service Recovery Evidence`，以独立指标/探测、告警清除、请求成功率及稳定时间窗定义恢复。对未恢复或反弹明确编码。

## 2. Root cause、传播节点、异常症状常被混淆

**GALA+ 补充证据：** STRIX 的 trace graph 表示服务调用依赖，另一个 metric-derived BARO 图才被作者描述为 causal DAG。图约束调查和支持/反证字段有助于区分候选，但论文未给出置信度校准；Algorithm 1 展示的是对起始候选直接检查邻居，不能把 dependency edge 或高置信候选本身解释成因果证明。

ToolRCA 的轨迹分析显示 L2 的异常证据可能把 Agent 从正确 L3 候选引向传播受害服务；KRCA 也报告同时级联异常和信号缺失错误。纯异常分数不足以构成因果根因。

**机会：** 以干预、变更日志、传播时序、拓扑约束、反证工具区分源头和下游症状；为候选保留支持/反驳证据和替代解释。

## 3. 工具组合与模型能力的交互尚不稳定

**GALA+ 补充证据：** 七个 LLM 的 OB 结果显示准确率、延迟和每例成本并不单调对应；邻居扩展的随机采样在作者的 30-case、五 seed 子集上略胜 STRIX 排序，但这不足以普遍确定最佳策略。缺少完整系统源码和 prompt，使这些模型/调查配置难以独立复现。

ToolRCA 在 375 个公开注入故障上发现不同 Qwen 模型对 L1/L2/L3 取舍不同；Qwen3-8B 几乎不调用 L3，而强模型有时推翻正确推荐。统计不确定性和工具参数披露不足，且缺少其它模型家族/真实多模态事故。

**机会：** 预先登记对照、重复种子和置信区间；单独评估工具选择、参数正确、输出理解和决定保留率。扩到日志、Trace、NetFlow、拓扑，验证真实故障迁移。

## 4. 生产 Ground Truth 和评测口径不可直接比较

**GALA+ 补充证据：** SURE-Score 将 evidence groundedness、operational feasibility、diagnostic precision 和 triage logic 分开评估，并有三位 SRE 评价；但公开仓库未提供最终 checklist / scorer。两个 LLM grader 的 Evidence Groundedness 分数差异明显。补充 AegisLab 表又将方法标为 GALA，主文则写 GALA+。官方公开标注样例的有限抽查还发现 RE2 行的系统名与摘要文本不一致；这些都应作为复现/标签可靠性待核验项，而非泛化结论。

OpsAgent 的生产准确率按 OCE 确认的原因和组件；KRCA 按 SRE postmortem 组件/type；OpsMem 用 LLM-as-a-Judge + 五次投票和专家抽样；KnowLution 用 task success/BLEU/tool success。benchmark 常限定候选集与 injected fault。

**机会：** 标注范围、时间粒度、候选全集、unknown/multi-root、判定人、争议处理和外部修复结果；分别报告服务、类型、证据质量、人工采纳与恢复率。

## 5. Agent 运行时的可审计事件链不足

**GALA+ 补充证据：** 公开 sample history 有候选、confidence、depth、证据摘要、因果解释和正反因素字段，说明可留存调查轨迹；但核心 runner 不公开，样例也没有可核对的原始遥测 locator，无法验证完整事件链与证据 provenance。

现有 AIOps logs 有输入输出和报告，但不一定留下工具依赖、状态版本、Agent 的证据可见集、委派、审查意见、最终覆盖早期建议的原因、核验结果。无法回答“谁在哪一步改错、谁传播了错误”。

**机会：** 定义与 [AgentOps](../agentops/README.md) 兼容的有向事件 schema：incident → observation → tool call/result → hypothesis/state update → agent review → decision → verification → human action。跨 Agent 共享 trace ID、时间戳、输入摘要、证据 provenance、依赖 edge 和模型版本。

## 6. 经验记忆可信度与时效

OpsMem 的 pattern/case/procedure 能重用经验，但私有 LTM 不公开，历史案例的 topology/版本适用范围与记忆漂移尚难审查。FlowXpert 和 OpsAgent 的反馈改善可能受重复事件与反馈选择偏差影响。

**机会：** 每条经验记录系统/服务/设备版本、环境与失效条件、数据来源、人工批准、expiry/confidence；上线前 replay 与对照记忆检索，测量 stale memory harm。

## 7. 从自然语言计划到可执行、安全、可逆的变更

FlowXpert 指出 API 无法覆盖全部专家处置，很多 workflow 是自然语言步骤；KnowLution 更明确地在执行前约束权限、依赖、参数并要求人工确认。可执行性与风险之间仍缺一致契约。

**机会：** 采用分层权限：观察、建议、预检、受控写；用 typed operations、dry-run、scope/TTL、two-person approval、rollback plan、canary 和恢复后置条件。Agent 自述“检查成功”不等于独立验证。

## 8. Network AIOps 特有的证据和安全外推

微服务工作常依赖服务/API topology 和指标；网络故障还涉及流量/NetFlow、路由协议状态、ACL/策略、配置变更、跨层设备与时延/丢包传播。直接套用服务 RCA 架构会错置候选空间，也可能让修复影响范围变大。

**机会：** 以设备—接口—链路—路由/策略—业务流层次建立动态图，支持多路径与多根因；把生产/控制平面视图、采集时间和配置版本放进 evidence provenance；在网络仿真/影子环境验证后再 human-gated rollout。

## 优先级排序

1. 轨迹级证据溯源和独立验证（与 AgentOps 结合）。
2. 候选空间缩减 + 传播/根因辨析（KRCA/Hybrid RCA）。
3. 基于模型能力和故障目标的工具选择（ToolRCA）。
4. 网络专属动态候选图和多源证据标准化。
5. 修复许可、回滚和服务恢复标签。

这些是从现有论文边界推导的研究假设，不是既有系统已证明的结果。
