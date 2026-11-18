# OpsAgent 研究方向

## 当前研究图

```text
Incident / Request
  → Telemetry + Runtime State
  → Candidate Space Constraint
  → Agent Investigation + Tool Use
  → Diagnosis / Workflow / Action Proposal
  → Independent Verification + Human Gate
  → Bounded Remediation
  → Recovery Evidence + Memory Update
```

这是一张综合分析图，不是任何一篇论文的完整实现。每篇研究的范围见对应论文笔记。

## 热点与成熟度

| 方向 | 研究问题与重要性 | 代表论文 / 技术 | 进展和当前局限 | 研究价值 |
|---|---|---|---|---|
| 结构化候选空间和拓扑剪枝 | 如何在数千服务/指标里保住高召回同时避免穷举？ | KRCA：API dependency drilldown、top service、metric causal skeleton | 对微服务拓扑有明确结构；未知拓扑、同步多根因、异步传播和打开世界候选仍弱 | 把网络拓扑、路由/配置依赖、告警源和流量路径纳入可更新的候选图 |
| 工具边界与 Agentic RCA | 应让工具返回原始观测、异常证据还是直接给候选？ | ToolRCA：L1 metric access / L2 evidence analysis / L3 diagnosis；OpsAgent preprocess；KRCA MCP | 2026 年活跃新问题：工具添加可能改善故障类型却降低服务定位；模型和系统都影响效用；当前仅 Qwen 与 metric benchmark | 设计带 provenance、反证、校准置信度与成本约束的 Network RCA 工具层 |
| 多源证据融合 | 如何联合 Metrics、Logs、Traces、Tickets、Topology/Config？ | OpsAgent M/L/T 共同文本；KnowLution runtime + KB；已有多模态 RCA 工作 | 多模态输入有益但不自动保证因果定位；很多新 Agent 研究仍为 metric-only | 记录时间窗、实体、来源、采样和因果/相关语义，防止摘要抹去依赖 |
| 动态规划与受控工作流 | 哪些任务用固定 SOP，哪些需要动态 replanning？ | FlowXpert Planner/Scorer；KnowLution route→plan→execute；ToolRCA ReAct tool selection | 固定 workflow 在常见步骤可审计；开放故障需要重新选择证据。生成出的自然语言步骤不等于可执行且安全 | 分层执行：确定性步骤先跑，证据触发的分支才允许规划器展开 |
| 运行时状态与 belief | Agent 如何知道目前真实状态和待解决问题？ | GoS causal belief graph/FSM；OpsMem STM；PoS world state + epistemic/achievement gaps | 显式状态有助于回溯/防漂移，但 LLM 更新可引入无证据状态；PoS 推理开销高，仍是 preprint benchmark 评估 | 版本化 belief state 与数据 provenance、置信区间、过期/冲突处理结合 |
| Operational memory | 何时把历史经验用于当前事故，怎样防止陈旧经验误导？ | OpsMem cross-memory resonance：pattern/case/procedure；FlowXpert hybrid KB | 当前证据刷新检索比一次性 RAG 更贴合迭代诊断；私有数据集限制复现，memory update 有人工审批 | 网络设备/协议/配置版本作为记忆上下文；对经验有效期和迁移条件建模 |
| 进度监控与恢复 | 如何发现 Agent 持续操作但无实际进展？ | PoS trapping：persistent gaps、stagnation、recurrence；FlowXpert terminal workflow | PoS 给出 benchmark 上按停滞类型约束下一步；恢复约束并不自动执行恢复，更不等同 service recovery | 让 Recovery 同时由 AgentOps（轨迹）和 OpsAgent（服务状态）进行校验 |
| 安全操作和执行治理 | 怎样控制代理权限、参数、前置条件、写操作和回滚？ | KnowLution sandbox + permission check + human confirm；FlowXpert AI Executor | 部分 HPC 研究明确安全门；多数 RCA 系统只给 report，现实 remediation/evaluation 仍不足 | Read-only default、typed tools、policy check、two-phase change、rollback and canary |
| 人机协作与持续改进 | 人类确认怎样形成可检验的学习信号？ | OpsAgent OCE-confirmed mitigation + offline PPO/Reflection；FlowXpert OCE workflow acceptance | 生产部署能证明可用性，但观察性数据不自动证明自演化造成改善；反馈 selection bias 大 | 保留模型/工具/数据版本，做 shadow、回放、反事实与 drift-aware 学习 |
| 生产评测与可复现 | 如何超越单次 QA accuracy？ | OpsAgent Lenovo、KRCA Kuaishou、OpsMem Huawei、KnowLution Tianhe；ToolRCA/RCAEval | 同时报有生产使用的系统与 benchmark prototype；指标、label、比较组差异大，公开可复现往往有限 | 同时报告 localization、type、evidence support、cost/latency、unsafe action、recovery time 与失败标签 |

## 较成熟、2026 活跃、仍未解决

- **相对成熟工程机制：** 规则化 anomaly filtering、拓扑/候选缩小、运行手册、只读查询、schema 验证、人工批准、确定性后置检查。这些通常比开放式 Agent 自由度低，也更易审计。
- **2026 活跃的新研究：** 显式 belief/state、短期诊断状态与长期操作记忆共振、Agent 工具抽象/组合对照、超大系统的拓扑剪枝、执行前的权限/状态约束。
- **核心未解问题：** 因果 root attribution 与传播区分；真正未知/多根因事件；模型改变工具输出后仍能正确融合；ground truth、误报和恢复状态一致性；安全闭环修复；私有生产数据下独立复现。

## 阅读建议

先读 [Hybrid RCA Architecture](../aiops/reviews/network-aiops-architecture-synthesis-v1.md) 与 [Evidence Provenance](../../concepts/aiops/evidence-provenance.md)，然后顺序读 [KRCA](../../papers/opsagent/krca.md) → [ToolRCA](../../papers/opsagent/toolrca.md) → [OpsMem](../../papers/opsagent/opsmem.md) → [KnowLution](../../papers/opsagent/knowlution.md)。若研究长时程任务，再读 [GoS](../../papers/opsagent/graph-of-states.md) 和 [PoS](../../papers/opsagent/pos.md)。
