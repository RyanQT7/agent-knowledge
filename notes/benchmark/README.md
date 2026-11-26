# AIOps Benchmark 专题

本目录以 Benchmark 设计为分类主线，比较故障数据如何构造、Ground Truth 如何建立、 shortcut 如何控制，以及传统 RCA 与 Agent 评估如何对齐。

## 入口

- [六篇论文清单与身份核验](paper-inventory.md)
- [六篇 Benchmark 横向比较](benchmark-comparison.md)
- [对本地 AIOps 挑战赛数据集的设计启发](dataset-design-insights.md)
- [未解决问题](research-gaps.md)
- [Benchmark Knowledge Review v1](reviews/benchmark-review-v1.md)
- 单篇笔记：`../../papers/benchmark/`
- 运行摘要：[Phase 1.5 benchmark run](../../evolution/runs/benchmark-20261125/benchmark-run-summary.md)

## 范围与证据状态

本专题严格限定用户指定的六篇论文。RCABench 指 arXiv:2510.04711 的 fault-propagation-aware microservice RCA 论文；本地已有的 **RCAgentBench** 是另一项工作，不计入本专题。

Phase 1.5 Engine 首轮由 Planner 选择 NIKA 和 CTBench，Executor 只阅读了相关章节。它因单次 Executor 输入达 570,961 tokens 而超过本轮 300K 目标；Judge 被停止，Reflector 仅产生运行时故障回退，后续 Planner 未执行。下列专题材料综合了已保存的局部自动研究产物、六篇论文现有的本地来源文本、官方论文页面及公开项目说明；它们不是六篇论文均经 Engine 全文精读及独立 Judge 验收后的结论。阅读状态见 [paper inventory](paper-inventory.md)。

纸面报告中的数据规模来自原论文或官方项目；论文未报告的字段标记为 **Not Reported**。项目当前版本的数据规模与论文版本分开记载。Challenge 数据集的本地原始数据和实验记录未找到，因此相关横向比较不推断其规模、效果或新颖性。

## 研究工作流记录

- Run: `evolution/runs/benchmark-20261125/`（中断状态，保留作恢复材料）
- 首轮重点：NIKA / CTBench Agent 过程、诊断正确性、资源代价、安全边界
- 本轮未批准或自动写入正式 Claim、Concept、Lesson、Skill；没有生成已通过 Judge 的 Knowledge Proposal。
- Phase 1.5 在首轮消耗 600,220 个已报告输入 tokens 后停止；Judge 使用量不可得。该运行只用于验证固定候选队列与第一轮研究，后续 Planner 反馈规划未通过验证。细节见运行摘要。
