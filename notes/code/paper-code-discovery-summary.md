# Paper–Code Discovery Summary

## Scope and Method

本次检查覆盖当前知识库中已经完成全文阅读的 20 篇论文：6 篇 Agent / LLM
论文和 14 篇 AIOps 论文。目标是确认论文与 GitHub repository 的关系，并对
可靠的公开仓库做固定 commit 的只读静态阅读。

当前会话的工具列表没有暴露独立的 GitHub MCP 搜索方法，因此仓库发现使用了
论文/项目页、公开 GitHub 页面和 repository README 作为受限回退。对于无法从
论文或作者证据确认身份的结果，保守标记，没有为了提高覆盖率而克隆。

## Discovery Counts

| Category | Count | Meaning |
|---|---:|---|
| Papers inspected | 20 | 已有完整 paper notes 的论文 |
| Confirmed Official | 8 | ReAct、Reflexion、ReWOO、LLM+P、RAP、RCAgentBench、StaR、StepFly |
| Likely Official | 2 | Cloud-OpsBench、CHIEF |
| Author-Endorsed Implementation | 2 | AIM、ChatRCA |
| Third-party only | 1 | Toolformer；只发现复现，不克隆 |
| No repository found | 7 | CAUSALDX、LLMGuard、KAT、Comfey、TSGen、Cloud Intelligence、FlowFixer |
| Reliable repositories cloned | 12 | 只克隆 Confirmed/Likely/Author-Endorsed 仓库 |
| Repositories statically code-read | 12 | 每个都有固定 SHA 的代码笔记 |

## Repository Classes

### Agent / LLM repositories analyzed

- [ReAct code notes](../../code/react/notes.md)
- [Reflexion code notes](../../code/reflexion/notes.md)
- [ReWOO code notes](../../code/rewoo/notes.md)
- [LLM+P code notes](../../code/llm-p/notes.md)
- [RAP code notes](../../code/rap/notes.md)

### AIOps repositories analyzed

- [RCAgentBench code notes](../../code/aiops/rcagentbench/notes.md)
- [StaR code notes](../../code/aiops/star/notes.md)
- [AIM code notes](../../code/aiops/aim/notes.md)
- [StepFly code notes](../../code/aiops/stepfly/notes.md)
- [ChatRCA code notes](../../code/aiops/chatrca/notes.md)
- [Cloud-OpsBench code notes](../../code/aiops/cloud-opsbench/notes.md)
- [CHIEF code notes](../../code/aiops/chief/notes.md)

### Benchmark / evaluation-oriented repositories

- [RCAgentBench](../../code/aiops/rcagentbench/notes.md): multimodal RCA tools, agent variants, and benchmark/evaluation support.
- [Cloud-OpsBench](../../code/aiops/cloud-opsbench/notes.md): frozen snapshots, interaction harness, process labels, and evidence-pattern evaluation.
- [CHIEF](../../code/aiops/chief/notes.md): Who&When trace-attribution benchmark, parsers, and accuracy analysis.

这些仓库不应被概括为同一种“完整生产系统”。它们分别强调数据/工具
benchmark、可复现交互、轨迹归因等不同层面。

## Code Reading Status

完整的 Paper → Repository → fixed commit → code notes 映射位于
[repository-index.md](../../code/repository-index.md)。每个已克隆仓库都记录了
默认分支、观察到的 license、固定 SHA 和代码阅读状态。外部源码位于被忽略的
`sources/code/`，不会进入本知识库 Git history。

## Common Paper–Code Patterns

以下结论只来自本次实际静态阅读，不是预先假设：

1. **论文中的 Agent，代码里常常是一个受约束的循环。** ReAct、Cloud-OpsBench、StepFly 和 ChatRCA 都把 Agent 落成 prompt、工具分发、结果回填和停止条件；“Agent”并不意味着没有确定性控制。
2. **Planning 的实现差异很大。** LLM+P 把 LLM 放在自然语言到 PDDL 的接口，Fast Downward 负责正式规划；RAP 用 MCTS 和世界模型搜索；ReWOO 的 PWS 则先生成计划，再顺序执行 Worker。它们都不能直接等同于 AIOps 中的动态调查 Agent。
3. **AIOps 代码往往把关键数值处理留给确定性或神经算法。** RCAgentBench 的时间窗口/异常工具、StaR 的时序与 Granger 层、Cloud-OpsBench 的快照查询，都是 LLM 之外的核心组件。
4. **“Memory”不是单一实现。** Reflexion 的跨尝试文本 reflection、StepFly 的 session-scoped MongoDB 数据/会话状态、StaR 的时序模型状态，以及 ReAct 的 trajectory context 分属不同层次，不能因变量名相似而统一称为长期记忆。
5. **Tool use 不自动带来 verification。** Cloud-OpsBench 对工具调用和观察进行可接受模式匹配，LLM+P/ RAP 可调用形式验证器，但 AIM、ChatRCA 等路径的最终文本/专家汇总仍没有独立 recovery 验证。
6. **RAG/检索的作用依赖具体代码。** CHIEF 的 FAISS 资源用于 GAIA/AssistantBench 示例增强，ReWOO 的搜索 Worker 将结果写入当前 worker log；二者都不等于 Agent memory，也不等于 AIOps telemetry provenance。
7. **输出结构化不等于结论正确。** ChatRCA、AIM、Cloud-OpsBench 都有 JSON/字段约束，但结构化 schema 需要与 ground truth、独立检查、执行反馈或人工审核结合。
8. **论文的系统边界经常比代码更宽。** 多个仓库包含 baseline、demo、评估器或任务特定实现；代码笔记因此分别记录“实现了什么”和“没有看到什么”，没有把缺失模块补成架构。

## Important Paper–Code Differences

- **ReWOO**：论文的解耦思想在代码中是 `Planner → Worker → Solver`，但核心路径没有 observation-interleaved replanning。
- **LLM+P**：代码把正式 planner 和 validator 放在外部可执行程序中；它不是带工具和长期记忆的通用 Agent。
- **RAP**：代码实际维护 MCTS 树、symbolic state 和 LLM world-model 更新；这与生成多个“看起来像计划”的文本不同。
- **Reflexion**：代码的 failure learning 是 reflection/feedback 写入下一次 prompt 或实现，运行循环没有参数更新。
- **RCAgentBench**：多模态工具和 ReAct evidence loop 存在，但 inspected workflow 没有一个独立的 root-cause verifier 或物理网络 topology。
- **StaR**：`TemporalMemory` 是时序模型内部状态，不能直接理解为 Agent episodic memory；`star_gc.py` 与 flexible variant 还存在静态可见的聚合位置差异，未通过执行验证。
- **AIM**：代码生成 mitigation plan 并做规则/语义/LLM 安全评分，但没有看到真实 remediation executor、rollback 或 recovery loop。
- **StepFly**：PlanDAG 是显式固定工作流；LLM 在步骤内选择动作。MongoDB 提供 session-scoped operational state，但代码没有证明长期跨 session 记忆策略。
- **ChatRCA**：角色化 AutoGen group chat 和 telemetry functions 形成多 Agent 工作流，但没有看到动态 Planner、持久记忆、repair executor 或 recovery verification。
- **Cloud-OpsBench**：代码将 Agent 调查固定在 snapshot-backed tools 和封闭诊断输出契约中；它适合测交互过程的可复现性，不等于 live production Network AIOps。
- **CHIEF**：代码用多次 LLM prompt 重建 HCG、候选错误步骤和最终归因；其 FAISS 资源是通用 Agent 任务示例，不是网络 operational knowledge。

## Repositories Not Cloned

- Toolformer：发现了第三方复现，但没有可靠官方仓库证据，因此没有克隆或把复现当原始实现。
- CAUSALDX、LLMGuard、KAT、Comfey、TSGen、Cloud Intelligence / AIOps 2.0、FlowFixer：本次限定范围内未确认可靠公开 repository。

“No repository found”不表示论文没有代码，只表示本次没有足够证据把某个
公开仓库安全地归属于该论文。

## Safety and Reproducibility Boundaries

- 所有外部仓库仅作静态阅读；没有安装依赖、运行训练/benchmark、下载模型、调用云 API 或执行 remediation。
- `sources/code/` 被 `.gitignore` 忽略；不会把外部源码 vendor 到知识库。
- 代码笔记中的 repository identity、固定 SHA 和 Paper ↔ Code 链接是当前可复核边界；仓库未来变化时应重新固定版本后再读。
- 由于没有运行代码，笔记中的“source-level discrepancy”不是 runtime bug 报告。

## Next Code-Reading Priorities

1. 为 Network AIOps 建立可审计的 evidence/provenance 数据结构，并寻找能公开 telemetry、candidate 和验证接口的 benchmark。
2. 对 Cloud-OpsBench、RCAgentBench 和 ChatRCA 进一步比较工具调用、候选约束、ground truth 与 verification 的可测量接口。
3. 对 StepFly、ReWOO、LLM+P 和 RAP 比较固定 DAG、plan-first、formal planner 与 search 在动态 Network environment 中的适用边界。
4. 只有在需要复现实验或解决关键歧义时，才考虑依赖安装和受控运行；那将是独立任务，不属于本次静态阅读。

## Independent Agent Framework Learning

本次另外对四个不依赖具体论文的 Agent framework / SDK / runtime 做了源码学习：

| Repository | Category | Status | Read at commit | Code notes |
|---|---|---|---|---|
| `huggingface/smolagents` | minimal tool-calling/code Agent framework | Cloned and statically read | `30bb1161095dbae2271e6bc3cc4c219cc3897a57` | [smolagents](../../code/agent-frameworks/smolagents.md) |
| `langchain-ai/react-agent` | graph-based ReAct example | Cloned and statically read | `9bbd82d84905acc37f527b1f372dae841016f3b4` | [LangGraph ReAct](../../code/agent-frameworks/langgraph-react-agent.md) |
| `openai/openai-agents-python` | Agent SDK/runtime | Cloned and statically read | `d59fdb8a789a54aff77ce61e503a04797355fc03` | [OpenAI Agents SDK](../../code/agent-frameworks/openai-agents-sdk.md) |
| `microsoft/agent-framework` | Agent runtime/typed workflow | Shallow-cloned and statically read | `999dda7970fe969c0901d524365ce34ecbda6227` | [Microsoft Agent Framework](../../code/agent-frameworks/microsoft-agent-framework.md) |

四个外部源码目录均在 `sources/code/`，没有进入知识库 Git history。配置的工具列表在本次运行中没有暴露专用 GitHub MCP 搜索方法；由于用户给出了明确仓库 URL，身份和版本使用 clone 的 remote、Git metadata、README 和源码树核对，并保留了这一限制。

### Framework code patterns observed

1. Agent loop 可以是 smolagents 的 while-loop、LangGraph 的 state graph、OpenAI SDK 的 Runner state machine，或 Microsoft 的 typed workflow runner。
2. Agent object 和 runtime 可以分离；OpenAI SDK 的 `Agent` 主要保存配置，`Runner` 才推进 turns、tools、handoffs 和 interruptions。
3. `memory`、`session`、`state` 和 `checkpoint` 都可能保存信息，但不自动等于 semantic long-term memory。
4. Tool 的可靠边界包括 schema、参数验证、执行、结果规范化、错误、approval 和 tracing；MCP 是一种接入外部 tool 的协议/适配层。
5. 代码执行是高风险 action；smolagents 的 `CodeAgent` 明确经过 interpreter/executor 边界，不能和 read-only telemetry query 使用相同安全假设。

更完整的横向比较见 [Agent Framework Source Code Comparison](../../code/agent-frameworks/comparison.md)。
