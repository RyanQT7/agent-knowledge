# NetArena 官方源码阅读

## 仓库身份与版本

- 论文：[NetArena: Dynamic Benchmarks for AI Agents in Network Automation](../../papers/benchmark/netarena/notes.md)，ICLR 2026。
- 官方仓库：[Froot-NetSys/NetArena](https://github.com/Froot-NetSys/NetArena)。论文和仓库 README 均指向该项目。
- 阅读分支：`main`，commit `aefbd457497768a9504cfc1c6b0988a626cf082a`；本地忽略克隆：`../../sources/code/NetArena/`。
- 版本边界：仓库当前默认 `a2a-agentx` 用于 Docker/A2A leaderboard；README 指示直接本地、非 Docker 运行使用 `main`。本文按 `main` 静态阅读，不等同于论文实验时的不可变快照。
- 范围：只读任务生成、模拟器/执行入口、状态检查和评分实现；未安装依赖、执行代码、启动 Mininet/kind、连接模型端点或运行故障注入。
- 许可：此次克隆快照根目录未观察到 LICENSE 文件；不得由公开仓库推定其所有内容可再分发。

## 代码结构与论文映射

该分支按三类应用提供独立实现，没有一个已确认的通用 `src/netarena` runtime。共同理念在论文中抽象为 state/action/execution，但代码以各应用的生成器和 evaluator 落地。

| 论文任务 | 关键源码 | 静态确认的职责 |
| --- | --- | --- |
| Datacenter Capacity Planning | `app-malt/dy_query_generation.py`; `solid_step_helper.py`; `malt_env.py`; `error_check.py`; `eval_with_sem_err.py` | 从基础图操作组合 query 与 Ground Truth 函数；执行 Agent 生成的图操作代码；检查节点/边类型、层级、孤立节点、端口和带宽；按任务汇总正确性、安全和执行时间。 |
| Routing Misconfiguration | `app-route/advanced_error_function.py`; `main.py`; `prompt_agent.py`; `safety_check.py`; `parallel_ping.py` | 生成多类单/复合网络错误；组织 Mininet episode；用命令与 pingall 反馈进行多轮诊断；包含命令安全检查。 |
| K8s Policy Troubleshooting | `app-k8s/inject_errors.py`; `run_workflow.py`; `correctness_check.py`; `command_validation.py`; `llm_agent.py` | 生成 policy 变更；部署 Online Boutique network policy；向 Agent 返回 connectivity mismatch；抽取/检查并执行 Kubernetes 命令；通过 debug container 的 `nc` 连通性矩阵核验。 |

## 实现观察

### MALT / capacity planning

`QueryGenerator` 把 add/count/update/remove/list/rank 的小操作组合成 level-based 查询，并为相同操作合成 Ground Truth 处理函数。`malt_env.py` 的 evaluator 对 Agent 输出与 Ground Truth 执行比较；`SafetyChecker` 验证图结构不变量。安全和正确性独立保存，因此一个结构上安全但结果错误的操作可以与“结果正确但结构违规”区分。动态 query 复用固定拓扑 schema 和操作模板，并非任意数据中心业务逻辑生成器。

### Routing

`advanced_error_function.py` 提供 IP forwarding、interface、IP address、traffic filtering 和 routing table 等错误操作与参数化细节；入口可将错误组合后注入拓扑。`main.py` 负责环境运行与 Agent 交互，PingAll 作为环境反馈/恢复检查。静态代码说明“错误类别 → 环境配置 → Agent 命令 → 连通性复核”的闭环，但没有在本轮实测任何拓扑或判定其对生产配置的覆盖率。

### Kubernetes

`inject_errors.py` 生成并写入网络策略错误；`run_workflow.py` 部署策略，按轮次执行 Agent 命令并调用 connectivity checker；`correctness_check.py` 在 debug container 中用 `nc` 检查期望源/目标/端口矩阵，生成 expected/actual mismatch 给下一轮。对输入中“本应不通”的组合也做检查，因此单纯放宽策略可能恢复部分可用性却造成安全失败。该指标仍以论文列出的期望矩阵为准，不等于完整的 K8s 安全审计。

## 复现边界

- README 列出不同的 Conda 环境；Routing/K8s 需要 Mininet 或 Docker/kind，MALT 依赖 Python 图/仿真流程，模型运行还需要相应端点或本地模型。源码公开不代表依赖和基础设施已随仓库复现。
- 论文实验模型、query 数、训练数据和源码分支需要分别对齐；本文只确认选定 commit 的代码路径，没有复现论文数字。
- GitHub 仓库变更较活跃，任何后续复现都应重新固定 commit，并确认具体 app 和论文版本匹配。

## 相关入口

- [NetArena 精读笔记](../../papers/benchmark/netarena/notes.md)
- [论文—源码总索引](../repository-index.md)
