# AIOps Benchmark 专题

本专题比较 AIOps 与 Agent Benchmark 如何构造故障、建立 Ground Truth、处理数据质量和评价诊断过程。当前固定研究范围为六篇论文。

## 阅读入口

- [论文清单、全文状态与源码边界](paper-inventory.md)
- [六篇论文横向比较](benchmark-comparison.md)
- [对本地 AIOps 挑战赛数据集建设的启发](dataset-design-insights.md)
- [研究缺口](research-gaps.md)
- [Benchmark Knowledge Review v1](reviews/benchmark-review-v1.md)
- 六篇单篇精读：[`papers/benchmark/`](../../papers/benchmark/)

## 证据边界

六篇均已由本轮 Codex 主会话完整精读，复用已有 PDF/全文和源码材料；只对有官方代码且可访问的范围做静态阅读，未执行故障注入或大型基准。各论文当前源码可能早于或晚于论文实验版，源码索引明确记录版本差异。

本地挑战赛样本、数据字典、注入脚本、标签规范和评估器当前缺失。因此有关 inode/process count/fd、时间边界、角色绑定、长尾、传播范围的具体判断都是待核查假设。

## 历史 Engine 运行

`evolution/runs/benchmark-20261125/` 保存此前一次 Phase 1.5 Engine 试运行。它只对 NIKA 和 CTBench 进行选段分析，发生高输入消耗，Judge/后续 Planner 未完成。该工件作为历史记录保留，不与本轮主会话完成的六篇全文研究混为同一次执行，也没有重新启动 Engine 或额外研究批次。

本轮没有自动批准或写入正式 Claim/Concept/Skill。研究笔记与专题报告是本任务产物；若需要改变既有正式知识或 Skill，则另经 Proposal 审阅。Skill Evolution 的 `paper-reading` 候选及回顾性评价存放于 `evolution/skill-proposals/`。
