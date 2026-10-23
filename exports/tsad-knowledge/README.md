# TSAD 33 篇论文科研知识包

本导出包汇集 2024–2026 年 TSAD 论文 33 篇的结构化知识档案。每篇档案基于对应的完整精读笔记整理；关键公式、机制、实验数值和争议保留 PDF 文件名及章节 / 页码 / 表图定位。内容区分作者主张、实验实际支持和本知识库分析。

## 文件说明

- `tsad-33-paper-knowledge-full.md`：33 篇逐篇档案正文，含完整目录、详细方法与原文证据定位。
- `tsad-33-paper-knowledge-overview.md`：横向比较表及跨论文方法关系。
- `tsad-paper-knowledge.jsonl`：每篇一条 JSON 记录，含稳定 ID、PDF / 精读笔记 / 知识卡片来源哈希和结构化研究信息。
- `tsad-research-problem-map.md`：按研究问题组织的方案、证据边界和可证伪假设。
- `knowledge-dossiers/`：33 份独立档案副本，便于单篇阅读和程序检索。
- `TSAD-knowledge-export.zip`：上述 Markdown、JSONL 和独立档案的分享包；不含 PDF。
- `progress.json`：批量处理进度与稳定论文 ID 清单。

## 证据和可移植性

档案保留原始 PDF 文件名、章节、页码、公式 / 表 / 图编号，主要方法和实验文字无需访问服务器内部链接即可阅读。原始 PDF、详细精读笔记和知识卡片仍在知识库中；三类来源路径及 SHA-256 记录用于追溯和增量更新。本包研究空白判断限于所列 33 篇，不代表穷尽 TSAD 全部文献。

## 研究问题入口

问题地图重点覆盖多正常状态、正常业务波动与故障区分、噪声和污染、分布漂移、上下文、指标关系、Metric / Trace / Log、多数据异常与业务异常、服务性能退化。每项假设均标为跨论文分析，并给出需要补充的实验证据。

## Skill 验证

新增的 `skills/paper-knowledge-extraction/` 工作流先在方法差异明显的 FlowFuse（多视角分数与 coupling flow）和 Conditional Normalizing Flows（潜动态与 goodness-of-fit）上试运行。两份档案通过章节、JSON、PDF / 精读笔记 / 知识卡片哈希和 PDF-free ZIP 检查；随后 33 篇集合全部通过 exporter 校验。

## 处理进度

- 状态：完成，33 / 33。
- 待处理：无。
- 原始 PDF 保留于 `sources/papers/tsad-2024-2026/`，遵循现有 .gitignore，不通过 Git 同步。
