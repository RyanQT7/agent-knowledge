# Skills

这里逐渐加入用于辅助知识库维护的 Skill：

Skill 层次：

- paper-reading — single-paper workflow
- learning-batch — batch orchestration
- aiops-paper-reading — AIOps single-paper research analysis
- aiops-learning-batch — research-question-driven AIOps batch orchestration
- paper-code-discovery — paper-to-repository provenance and implementation discovery
- code-reading — read-only paper implementation analysis
- agent-framework-learning — source-first learning of open-source Agent frameworks and runtimes
- knowledge-review — generic cross-paper consolidation
- knowledge-query — retrieve / learn from accumulated knowledge

- [paper-reading](paper-reading/SKILL.md) — 阅读单篇学术论文 PDF 并整合到知识库。`Status: v1 / validated with ReAct workflow`
- [knowledge-review](knowledge-review/SKILL.md) — 跨论文知识整合与阶段性复盘。`Status: v1 / validated with ReAct + Toolformer + Reflexion`
- `code-reading`
- `literature-review`
- `concept-updating`
- `research-comparison`

其他 Skill 当前只保留规划项，不实现复杂 Skill。

- [aiops-paper-reading](aiops-paper-reading/SKILL.md) — AIOps / Infrastructure / Network Operations 单篇论文的专题全文分析。`Status: v1 / validated through AIOps Batch 1 + Batch 2 + Batch 3`

- [aiops-learning-batch](aiops-learning-batch/SKILL.md) — 研究问题驱动的 AIOps 批次选择、串行论文阅读与专题 Review 编排。`Status: v1 / validated from AIOps Batch 1–3`

- [paper-code-discovery](paper-code-discovery/SKILL.md) — 验证论文对应的官方、作者背书或第三方源码仓库，并记录版本证据。`Status: v1 / validated on the current 20-paper inventory`
- [code-reading](code-reading/SKILL.md) — 对论文实现仓库进行只读静态分析，建立 Paper ↔ Code 映射。`Status: v1 / validated on 12 static repository analyses`
- [agent-framework-learning](agent-framework-learning/SKILL.md) — 从开源 Agent Framework、SDK 和 Runtime 源码中提取真实执行路径与可复用设计模式。`Status: v1 / initial capability`

当前职责层次：

~~~text
paper-reading
= generic research paper reading

learning-batch
= generic paper batch orchestration

aiops-paper-reading
= AIOps single-paper research analysis

aiops-learning-batch
= research-question-driven AIOps batch orchestration

paper-code-discovery
= paper-to-repository provenance discovery

code-reading
= static paper-implementation analysis

agent-framework-learning
= source-first Agent framework / SDK / runtime learning

knowledge-review
= generic cross-paper consolidation

knowledge-query
= retrieve / learn from accumulated knowledge
~~~

- [knowledge-query](knowledge-query/SKILL.md) — 基于已积累知识进行检索、教学、比较和来源追溯；默认只读。`Status: v1`

- [learning-batch](learning-batch/SKILL.md) — 串行编排新论文批次，并调用 paper-reading 与 knowledge-review。`Status: v1 / validated from Planning Batch`

正式的知识库维护 Skill 默认在任务完成并通过自检后执行 `git add`、`git commit` 和 `git push origin main`。遇到失败、冲突、来源核对未通过、远程或认证异常，或用户明确禁用同步时，保留本地状态并停止 push。
