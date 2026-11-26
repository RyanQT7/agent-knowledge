# AIOps Benchmark 专题

本专题比较 AIOps 与 Agent Benchmark 如何构造故障、建立 Ground Truth、处理数据质量和评价诊断过程。原专题包含六篇论文；本次增加 NetArena 作为独立的泛化阅读案例，当前索引共七篇。

## 阅读入口

- [论文清单、全文状态与源码边界](paper-inventory.md)
- [论文横向比较](benchmark-comparison.md)
- [对本地 AIOps 挑战赛数据集建设的启发](dataset-design-insights.md)
- [研究缺口](research-gaps.md)
- [Benchmark Knowledge Review v1](reviews/benchmark-review-v1.md)
- [独立反馈处理与 Skill 候选评估](reviews/reading-feedback-resolution.md)
- Benchmark 论文写作与实验设计：[逐篇写作分析](writing-study/paper-writing-analysis.md) · [实验比较与贡献—证据映射](writing-study/experiment-design-comparison.md) · [Network Benchmark 写作指南](writing-study/network-benchmark-writing-guide.md)
- 单篇精读：[`papers/benchmark/`](../../papers/benchmark/)
- 新增：[NetArena 精读](../../papers/benchmark/netarena/notes.md) · [官方源码静态分析](../../code/benchmark/netarena.md)

## 证据边界

原六篇均已由此前 Codex 主会话精读；NetArena 在本次独立泛化阅读中完成正式版正文和附录阅读。只对有官方代码且可访问的范围做静态阅读，未执行故障注入或大型基准。各论文当前源码可能早于或晚于论文实验版，源码索引明确记录版本差异。

本地挑战赛样本、数据字典、注入脚本、标签规范和评估器当前缺失。因此有关 inode/process count/fd、时间边界、角色绑定、长尾、传播范围的具体判断都是待核查假设。

## 历史 Engine 运行

`evolution/runs/benchmark-20261125/` 保存此前一次 Phase 1.5 Engine 试运行。它只对 NIKA 和 CTBench 进行选段分析，发生高输入消耗，Judge/后续 Planner 未完成。该工件作为历史记录保留，不与本轮主会话完成的六篇全文研究混为同一次执行，也没有重新启动 Engine 或额外研究批次。

本轮没有自动批准或写入正式 Claim/Concept/Skill。研究笔记与专题报告是本任务产物；若需要改变既有正式知识或 Skill，则另经 Proposal 审阅。Skill Evolution 的 `paper-reading` 候选及回顾性评价存放于 `evolution/skill-proposals/`。
