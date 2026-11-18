# OpsAgent 专题

本目录的 **OpsAgent** 是知识库采用的研究分类：利用 LLM/Agent 完成云、微服务、网络、HPC 等 IT 基础设施运维。它同时也是 NKU 一篇具体论文的系统名称，见 [OpsAgent 系统论文笔记](../../papers/opsagent/opsagent-system.md)。专题名和系统专名必须分清。

本专题重点研究 incident handling、证据查询、RCA、运维记忆、工作流、受约束工具调用、修复安全和恢复验证。分类是本知识库的工作划分，不代表所有作者/论文都使用相同术语。

## 专题入口

- [论文清单与阅读状态](paper-inventory.md)
- [方向与代表工作](research-directions.md)
- [研究缺口](research-gaps.md)
- [OpsAgent Knowledge Review v1](reviews/opsagent-review-v1.md)
- [与 AgentOps 的关系](../guides/agentops-vs-opsagent.md)
- [课程 Lesson 2](../lessons/lesson-02-advanced-agent-systems.md)

## 研究问题

如何把传统 AIOps 的候选生成、拓扑约束、时序/日志/Trace 证据，与 Agent 的动态调查、工具选择和知识更新结合，同时保证每一步可审计、受权限控制，且根因和恢复结果能被独立验证？

## 对照已有知识

复用 [Hybrid RCA Architecture](../aiops/reviews/network-aiops-architecture-synthesis-v1.md)、[AIOps Review v4](../aiops/reviews/aiops-knowledge-review-v4.md)、[Evidence Provenance](../../concepts/aiops/evidence-provenance.md)、[Candidate Space](../../concepts/aiops/candidate-space.md)、[Verification](../../concepts/aiops/verification.md)、[Agentic Incident Management](../../concepts/aiops/agentic-incident-management.md)，避免复制已有方法和概念。
