Status: evolving

# Agentic Incident Management in AIOps

## Definition

Agentic Incident Management 是围绕事件目标，把观测、证据收集、分析、角色/工具选择、验证和后续决策组织成可持续推进的 AIOps workflow。这里的“agentic”强调系统是否能依据当前状态或 Observation 选择下一步并继续完成任务，而不是是否使用了 LLM、RAG 或多个 prompt。

这是当前知识库的 working concept，不是论文界已经统一的标准定义。

## Why It Matters

真实事件处理通常不止一个文本生成步骤：系统需要确定事件范围，收集相关证据，缩小候选原因，判断证据是否足够，必要时请求更多数据或其他领域经验，并在高风险节点交给人审核。把这些步骤的边界、权限、证据和反馈显式化，有助于区分：

- LLM 只是在 workflow 中生成摘要或计划；
- LLM 通过固定工具接口执行有限调查；
- Agent 根据 Observation 选择后续步骤；以及
- 系统是否真正能安全地执行和验证 remediation。

## Core Mechanism

一个谨慎的 AIOps incident workflow 可以抽象为：

```text
Incident / Alert
→ Context and Evidence Collection
→ Candidate / Hypothesis Generation
→ Tool or Role Selection
→ Observation
→ Ranking / Diagnosis
→ Verification or Human Gate
→ Recommendation / Remediation
→ Recovery Feedback and Knowledge Update
```

不同系统只实现其中一部分：

- **TSGen** 把历史事件生成结构化 TSG，是知识生成前端，不是在线 Agent。
- **AIM** 生成 mitigation plan 并在 Robot Shop 测试床进行受限 Ansible 执行，属于 plan-to-act workflow，但没有展示持续在线 replanning。
- **StepFly** 用 TSG-derived DAG、Scheduler、Executor 和插件执行受约束的诊断步骤；工具结果可以触发分支、重试和下一步。
- **Comfey** 让团队本地 agent 依据事件证据进行 enrich、accept/reject 和 transfer，形成有边界的生产路由循环。
- **ChatRCA** 让角色化 agents 收集观察、提供架构/领域上下文、形成假设并请求更多证据，在数据工单和根因判断处加入人审。

## Typical Architecture

```text
Alert / Incident
      ↓
Evidence adapters and context builder
      ↓
Candidate / hypothesis manager
      ↓
Role or tool selection
      ↓
Read-only investigation tools
      ↓
Observation normalization and provenance
      ↓
Diagnosis / explanation
      ↓
Verification, escalation, or human approval
      ↓
Recommendation or gated remediation
      ↓
Outcome and knowledge update
```

这只是跨论文抽象，不是任何一篇论文提出的标准架构。实际系统还必须说明候选空间、权限、终止条件、失败恢复、人工介入和结果验证。

## Example

在网络事件中，一个受约束的系统可以先把告警、指标、syslog、流量和拓扑转换成带时间范围和实体标识的数据工单；然后由网络、设备和资源角色分别查询证据，生成候选根因；系统再要求独立检查或人工确认，最后只生成或执行经过批准的动作。这里，查询工具、RCA、解释和修复执行是不同步骤，不能因为它们出现在同一个对话里就视为一个能力。

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Topology-aware RCA](topology-aware-rca.md)
- [Operational Knowledge](operational-knowledge.md)
- [Production Evaluation](production-evaluation.md)
- [Agent](../../concepts/agent.md)
- [Planning](../../concepts/planning.md)
- [Tool Use](../../concepts/tool-use.md)
- [Memory](../../concepts/memory.md)
- [Context Engineering](../../concepts/context-engineering.md)

## Representative Papers

- [Comfey](../../papers/aiops/comfey/notes.md) — production team-local incident triage and bounded transfer decisions.
- [AIM](../../papers/aiops/aim/notes.md) — alert interpretation, plan generation, and constrained plan-to-act execution.
- [StepFly](../../papers/aiops/stepfly/notes.md) — DAG-constrained, tool-using diagnostic execution with structured working data.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — role-specialized, human-gated multi-agent RCA.
- [TSGen](../../papers/aiops/tsgen/notes.md) — the upstream knowledge-curation boundary; an LLM pipeline that should not automatically be classified as an Agent.
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — production SOP-grounded diagnosis with deterministic checks and human gating.
- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — agent-oriented multimodal RCA process evaluation.

## Advantages

- 将证据收集、决策、工具权限和验证节点显式化。
- 可以把确定性规则、历史知识、LLM reasoning 和人工判断组合起来。
- 允许按风险把 read-only investigation、recommendation 和 state-changing remediation 分开。
- 通过记录 Observation、工具调用、角色交接和人工决定，提高可追溯性。

## Limitations

- 多步骤和多角色会增加 token、延迟、工具失败和协调成本。
- 历史知识、TSG、RAG case 或 topology 可能过时、冲突或覆盖不足。
- 角色化 prompt、固定 DAG 和闭集分类可能提高受控 benchmark 表现，却无法保证 open-set 事件上的因果正确性。
- 人工检查能够降低风险，但其时间、吞吐和触发策略必须被评估。
- 当前 Batch 2 没有证明可以在网络基础设施中安全地自主执行并验证 remediation。

## My Understanding

Agentic Incident Management 的核心不在“让一个更大的模型写出更长的 RCA 文本”，而在于把事件处理变成有目标、有状态、有证据、有边界的决策过程。当前资料最可靠地支持的是受约束的调查和人机协同：系统可以选择下一项查询、角色或分支，但仍需要独立验证、人工升级和明确的安全边界。

因此，Agentic 程度与是否多 Agent、是否有 RAG、是否有 memory 并不等价。一个固定 DAG 可以是有用的 agentic workflow；一个使用 RAG 的一次性 LLM 也可能不是 Agent；一个能生成 remediation script 的系统仍可能只停留在 recommendation 或 testbed execution。

## Open Questions

- 什么样的 Observation-driven next-action loop 才足以称为 Agentic AIOps？
- 如何在不把所有工作交给 LLM 的情况下组合确定性候选缩减、工具调用、假设验证和人工裁决？
- 如何以统一协议评估 RCA correctness、evidence correctness、tool correctness、human effort、cost、latency 和 remediation safety？
- 网络物理拓扑、流量/NetFlow、syslog 和时序指标如何接入可验证的数据工单与 Agent 工具接口？
- 如何检测 open-set、multi-root、stale-knowledge 和 unsafe-remediation 情况？
