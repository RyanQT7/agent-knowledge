# AIOps Agent Architecture From Open Source

这份文档将四个开源 Agent runtime 的代码理解映射到当前 Network AIOps RCA 研究。它是 **cross-project synthesis / engineering hypothesis**，不是任一仓库的标准架构。AIOps 背景见 [Network AIOps Architecture Synthesis v1](../aiops/reviews/network-aiops-architecture-synthesis-v1.md)，源码证据见 [framework comparison](../../code/agent-frameworks/comparison.md)。

## 1. Reference architecture

```text
Incident / Alert
      ↓
Deterministic preprocessing and detection
      ↓
Evidence normalization + provenance
      ↓
Topology-constrained candidate space
      ↓
Bounded RCA Agent loop
  ├── Metrics Tool
  ├── Logs / Syslog Tool
  ├── Topology Tool
  ├── Traffic / NetFlow Tool
  ├── Knowledge Tool
  └── Historical Incident Tool
      ↓
Evidence-backed hypothesis update
      ↓
Independent validation
      ↓
Root cause + fault classification
      ↓
Human-gated recommendation / remediation
      ↓
Controlled execution → recovery verification
```

这张图把开源框架中的 runtime 能力和当前 AIOps 论文中已有的 evidence、candidate、verification 认识组合起来。它不表示所有框架都实现了所有层。

## 2. Why not put everything in an LLM

LLM 擅长理解异构文本、生成调查假设、选择有限的 read-only tools 和解释证据；但以下工作更需要确定性或可复核机制：

- metrics 计算、异常阈值和时间对齐；
- device/interface/link 等 candidate 枚举；
- physical topology 查询和硬约束；
- schema、权限、超时和 tool execution；
- candidate/ground-truth 粒度转换；
- 安全检查、rollback 条件和 recovery signal。

smolagents 的代码说明 Agent loop 可以很小；OpenAI SDK 和 Microsoft Framework 进一步说明安全、session、workflow、approval、checkpoint 和 tracing 是 runtime 层问题。它们不能替代 Network RCA 的领域验证。

## 3. What each open-source project contributes

### smolagents

可借鉴最小完整 loop：`run → step → model → tool/code → observation → memory → next step`。它适合把 AIOps 的 metrics/log/topology 查询先包装成受限工具。`CodeAgent` 同时提醒我们：code-as-action 比 read-only query 具有更大副作用，需要独立 sandbox 和权限。

### LangGraph ReAct

可借鉴显式 state graph：把 model node、tool node、routing、state update 和 end 条件拆开。AIOps 可以将 `candidate_pruner`、`evidence_validator`、`human_approval`、`recovery_check` 作为确定性或人工节点，而不是让模型自由跳过。

### OpenAI Agents SDK

可借鉴 Agent/Runner 分离：Agent 保存 instructions、model、tools、handoffs 和输出约束；Runner 管理 tool continuation、handoff、guardrail、approval、max turns 和 tracing。对高风险 Network remediation，这种 separation 比“一个 prompt 驱动全部动作”更容易审计。

### Microsoft Agent Framework

可借鉴大规模 control plane：typed Executor、Workflow edges、events、request information、checkpoint、ContextProvider 和 MCP adapter。它适合未来需要可暂停/恢复、多阶段诊断或人机协同时的架构参考，但当前不应因项目复杂而直接引入全部组件。

## 4. Constrained ReAct design

推荐的最小调查 loop：

```text
Incident context
  → deterministic candidate set
  → Agent chooses one allowed read-only query
  → Tool validates arguments and executes
  → returns structured evidence ticket
  → Agent updates hypothesis within candidate set
  → policy decides: more evidence / verify / escalate / finish
```

其中允许模型做的是“在有限选择中决定下一步调查”，不是随意创建设备、跳过工具或调用变更配置的 command。

## 5. Tool interface

参考四个框架中的 schema/adapter/Executor 边界，Network tool 至少应描述：

```text
name
purpose
input schema
allowed entities
time range
read-only or side-effecting
timeout
result schema
source / query id
```

建议工具：

- `query_metrics(entity, start, end, signals)`
- `query_syslog(device, start, end, filters)`
- `query_topology(entity, relation, version)`
- `query_flow(src, dst, start, end, dimensions)`
- `get_configuration(device, version)`
- `retrieve_knowledge(fault_type, topology_context)`
- `retrieve_historical_incidents(signature)`
- `requery_evidence(ticket_id)`
- `validate_candidate(candidate, evidence_set)`

真实实现中，检索工具、验证工具和 remediation tool 必须分开；一个能返回资料的 tool 不应因此拥有修改系统的权限。

## 6. State should save what

当前调查 state 不应只是聊天文本。至少保存：

```text
incident id
current time window
candidate set and candidate granularity
hypotheses and status
tool calls and arguments
evidence tickets
observed errors / missing data
verification results
step / token / latency budget
approval status
```

smolagents 的 `AgentMemory.steps`、LangGraph 的 `State.messages`、OpenAI 的 session/context 以及 Microsoft 的 session/workflow/checkpoint 表明“保存轨迹”有多种实现。但当前框架代码也说明：session/checkpoint 是状态承载，不自动解决 memory selection、语义压缩、过期和跨 incident 学习。

## 7. Evidence-backed RCA

每个 Evidence Ticket 建议包含：

```text
source: metric / syslog / flow / topology / config / knowledge
tool/query: exact operation
entity: device/interface/link/module/path
timestamp or interval
observation: normalized value or event
transformation: aggregation / filtering / alignment
freshness
confidence
candidate relation
version / provenance id
```

没有这些字段，LLM 可以生成很流畅的 diagnosis，但很难回答“这条结论来自哪个设备、哪个时间窗口、哪次查询”，也很难由 verifier 或 operator 重查。

## 8. How to reduce repeated tool calls and hallucination

- 由 deterministic layer 提供候选和合法 entity IDs；
- 对时间窗口、实体、字段和参数做 schema 校验；
- 将 tool call 与 observation 写入 state，检测完全重复调用；
- 给每类工具设置次数、延迟和 token budget；
- 让返回值包含 provenance，不把原始大 payload 无限制塞进 prompt；
- 对缺失/冲突/过时 evidence 显式标记，而不是让模型自行填空；
- 在结论前调用独立 validation/re-query 节点；
- 对 open-set 或 multi-root 结果允许 abstain / escalate；
- remediation 只暴露经过审批的窄接口，并提供 rollback/recovery 检查。

## 9. Verification

Verification 应分层：

```text
schema / argument validation
  → evidence freshness and provenance check
  → topology consistency
  → cross-modal corroboration
  → independent candidate/root-cause checker
  → human confirmation for uncertain/high-impact case
  → execution feedback
  → recovery verification
```

LLM 自己重复说“我确认了”只是 weak self-check。OpenAI SDK 的 guardrail/approval 和 Microsoft 的 workflow request/checkpoint 主要控制 runtime 是否继续；它们并不单独证明 root cause 真确。真正的 RCA verification 仍需要 fresh telemetry、独立算法、ground truth 或人审。

## 10. Remediation lifecycle

```text
Root cause / diagnosis
  → proposed action
  → deterministic safety check
  → human approval
  → controlled execution
  → observe fresh telemetry
  → recovery verification
  → rollback / escalation if failed
```

Recommendation、execution 和 recovery 是三个不同事件。当前开源 Agent runtime 最有价值的可迁移经验是把 approval、interruption、tool boundary、trace 和 checkpoint 做成运行时控制点，而不是把修复命令写进 prompt。

## 11. What should be deterministic vs LLM/Agent

| Layer | Preferred mechanism | Reason |
|---|---|---|
| Detection and numerical aggregation | deterministic / ML | 可重复、延迟和指标定义明确。 |
| Entity/time alignment | deterministic | 错位会污染所有后续推理。 |
| Candidate enumeration/pruning | topology/graph/rules | 避免模型在巨大全集上自由编造。 |
| Evidence retrieval | typed tools | 保留权限、查询和 provenance。 |
| Hypothesis synthesis | bounded LLM | 适合整合异构证据，但输出要带 evidence links。 |
| Next read-only investigation step | Agent runtime + policy | 需要根据 observation 选择有限工具。 |
| Root ranking | hybrid | LLM 可辅助解释/排序，独立算法或规则应校验。 |
| Remediation proposal | LLM + deterministic templates | 生成建议与安全 schema 分离。 |
| Remediation execution | approved tool/runtime | 不应由开放式文本直接执行。 |
| Recovery verification | fresh telemetry + deterministic checks + human policy | 必须观察真实结果，而不是读取生成文本。 |

## 12. Skill and Runtime relationship

当前知识库中的 Skill 是可重复执行的 instructions、SOP、输入输出约定和质量检查。例如 `aiops-paper-reading` 规定如何读 AIOps 论文，`knowledge-query` 规定如何只读检索和教学。

源码中的 Agent Runtime 则负责：调用 LLM、暴露 Tool、更新 State、继续 loop、处理失败、guardrail、handoff、tracing 和 stop condition。

```text
Skill = what procedure / constraints should be followed
Tool = what external capability can be called
Runtime = how execution is controlled
Agent = goal-directed system using model + context + capabilities
```

Skill 可以被 Runtime 动态加载，影响 instructions、tool selection、state schema 和 quality checks，但 `SKILL.md` 本身不是 Agent，也不是模型能力。

## 13. Current research interpretation

基于已有 AIOps 论文与四个源码项目，当前最稳妥的方向不是“把 GPT 放到 RCA 中”，而是把 LLM/Agent 放在**受约束的调查层**：让确定性模块负责事实、候选和安全边界，让 Agent 负责在证据工具之间导航、形成假设和解释，再由独立机制验证。

这是一项当前研究设计假设。它仍需要在 Network AIOps 的 device/interface/link/optical module、physical topology、metrics、syslog、traffic/NetFlow 和真实生产规模上验证。

## 14. Next experiments to consider later

这里只记录方向，不修改现有实验代码：

1. 比较开放式 ReAct 与 topology-constrained ReAct 在候选有效率、tool calls、RCA Top-k 和成本上的差异。
2. 用 Evidence Ticket 与纯文本 prompt 比较多模态 grounding、重复查询和 verification 成功率。
3. 比较 device/interface/link 不同 candidate 粒度下的评价一致性。
4. 构造错误、缺失、延迟和冲突 telemetry，测试 Agent 是否能 abstain 或请求 re-query。
5. 对建议、人工批准、执行、恢复验证分别统计成功率和错误 remediation 成本。

## Sources in this knowledge base

- [Agent Framework Source Code Comparison](../../code/agent-frameworks/comparison.md)
- [smolagents notes](../../code/agent-frameworks/smolagents.md)
- [LangGraph ReAct notes](../../code/agent-frameworks/langgraph-react-agent.md)
- [OpenAI Agents SDK notes](../../code/agent-frameworks/openai-agents-sdk.md)
- [Microsoft Agent Framework notes](../../code/agent-frameworks/microsoft-agent-framework.md)
- [AIOps evidence provenance concept](../../concepts/aiops/evidence-provenance.md)
- [AIOps candidate space concept](../../concepts/aiops/candidate-space.md)
- [AIOps verification concept](../../concepts/aiops/verification.md)
