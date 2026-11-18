# AgentOps 与 OpsAgent：两个方向、一个可靠性闭环

**知识库口径。** AgentOps 在本库中指 *Operations for Agent Systems*：诊断并改善 Agent 系统本身的运行可靠性。OpsAgent 指 *Agents for IT Operations*：让 Agent 执行 IT 运维调查、诊断和受控操作。这是便于组织研究的工作分类，不代表所有论文都沿用同一命名。标题为 *OpsAgent* 的 NKU 论文是具体系统，需与本库 OpsAgent 方向区分。

## 维度对照

| Dimension | AgentOps | OpsAgent |
| --- | --- | --- |
| Research Object | Agent、Multi-Agent、运行时与 harness | 云服务、微服务、网络、HPC 等 IT 基础设施 |
| Main Goal | 找出 Agent 为什么失败、错误从哪里开始、如何传播、如何验证修复 | 在真实或模拟 IT 环境中完成事件分流、证据收集、RCA、建议或操作 |
| Data | Agent 输入输出、tool call/result、状态更新、handoff、依赖、校验与环境结果 | Metrics、Logs、Traces、Tickets、拓扑、配置、运行手册、历史案例 |
| Failure Type | 理解、规划、工具选择/参数/执行、状态/记忆、协调、验证、终止、harness 错误 | 告警噪声、服务/设备/链路故障、性能退化、操作步骤错误、未知或多根因事件 |
| Candidate Space | 轨迹步骤、Agent、边、故障类型及传播链 | 服务、Pod、节点、API、设备、接口、链路、路径、配置或故障类型 |
| Root Cause | 触发错误的步骤/Agent 和使其扩散的依赖路径；终端症状不必是根因 | 引起当前服务症状的基础设施/配置/依赖实体及因果证据 |
| Tools | Trace 查询、运行时日志、schema/约束检查、重放、独立 verifier | 监控与日志查询、拓扑/配置查询、告警/工单、诊断程序、受控执行工具 |
| Verification | 验证轨迹重建、归因证据、修复补丁/重试和 Agent 状态 | 验证候选与观测一致、操作满足策略、服务状态确已恢复 |
| Recovery | 有界重试、工作流/提示/工具修复、回滚或交给人 | 继续调查、升级人工、建议变更、获批后修复并观察恢复 |
| Benchmarks | step/Agent attribution、trajectory completeness、harness reliability、recovery outcome | RCA localization/type、证据质量、tool efficiency、延迟/成本、修复安全与恢复率 |
| Deployment | 需接入 Agent runtime、trace 与模型/工具版本；生产数据带有隐私边界 | 需接入各类 IT telemetry、权限体系与变更治理；行业系统常有私有数据 |
| Research Gaps | 轨迹缺失下因果真值、在线误报、跨 harness 可比性、独立 recovery verification | open-set/multi-root、证据冲突、候选召回、跨域工具、生产级安全修复和可复现评测 |

该表是本库论文阅读后的综合；具体论文覆盖范围不同。例如 TraJudger 与 AgentRx 主要做诊断/归因，不能因为论文位于 AgentOps 方向就推断它们执行了恢复；OpsAgent、KRCA、OpsMem 也不能被当成相同系统。

## 双向闭环

~~~text
OpsAgent：用 Agent 调查 IT 事件
              ↓
工具、状态、协作或判断可能出错
              ↓
AgentOps：从运行轨迹定位责任步骤，验证诊断和恢复
              ↓
改进 OpsAgent 的工具边界、状态、计划、评测与治理
              ↺
~~~

OpsAgent 的成功率不只取决于根因模型。若查询过期、工具参数错误、某个 Agent 把猜测写入共享状态，后续 RCA 即使表面合理也可能错。AgentOps 因而能为 OpsAgent 提供运行时证据与故障反馈；OpsAgent 则为 AgentOps 提供更具后果、跨模态、受安全约束的实际任务。

**研究假设，尚未验证：** 将 AgentOps 的完整 trajectory、依赖图、结构化失败归因和独立恢复验证用于 OpsAgent，可把“根因答案正确”扩展为“工具/证据/决策/服务状态整条链可审计”。这需要比较完整轨迹与部分轨迹、模型裁判与确定性/新观测校验，并评测定位准确度、误报、延迟、成本和实际恢复；目前不能把该迁移写成已证实结论。

## 共用可靠性接口

一个可测试的交接对象可包含：

- 事件/任务 ID、Agent 与 harness 版本、当前计划或 workflow 节点；
- 原始输入、Observation、tool 名称/参数/返回值、状态变更与父子依赖；
- 操作者、权限、审批、时间戳、实体、证据来源和新鲜度；
- 当前候选、支持/反证、未解决问题、归因链及置信/弃权状态；
- 验证对象、判据、独立数据源与结果；
- 写操作的前置条件、实际执行结果、回滚状态和恢复证据。

这是面向研究的接口草案，不是论文共同采用的标准。它把 [Agent Runtime](../../concepts/agent-runtime.md)、[Agent Loop](../../concepts/agent-loop.md)、[Evidence Provenance](../../concepts/aiops/evidence-provenance.md)、[Candidate Space](../../concepts/aiops/candidate-space.md) 和 [Verification](../../concepts/aiops/verification.md) 接在一起。

## 知识库入口

- [AgentOps 专题](../agentops/README.md) · [研究 Review](../agentops/reviews/agentops-review-v1.md) · [研究缺口](../agentops/research-gaps.md)
- [OpsAgent 专题](../opsagent/README.md) · [研究 Review](../opsagent/reviews/opsagent-review-v1.md) · [研究缺口](../opsagent/research-gaps.md)
- [Agent Research Directions 2026](agent-research-directions-2026.md)
- [Advanced Lesson 2](../../lessons/agent-llm/lesson-02-advanced-agent-systems.md)
- [Network AIOps 架构综合](../aiops/reviews/network-aiops-architecture-synthesis-v1.md)

### 代表方法

- Agent 故障归因：[AgentRx](../../papers/agentops/agentrx.md)、[TraJudger](../../papers/agentops/trajudger.md)、[CHIEF（已有笔记）](../../papers/aiops/chief/notes.md)
- Agent 工作流恢复：[PROBE](../../papers/agentops/probe.md)、[FlowFixer（已有笔记）](../../papers/aiops/flowfixer/notes.md)
- IT 运维调查和状态：[NKU OpsAgent 系统](../../papers/opsagent/opsagent-system.md)、[KRCA](../../papers/opsagent/krca.md)、[OpsMem](../../papers/opsagent/opsmem.md)、[Graph of States](../../papers/opsagent/graph-of-states.md)、[PoS](../../papers/opsagent/pos.md)
