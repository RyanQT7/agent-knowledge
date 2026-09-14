# Skills

这里逐渐加入用于辅助知识库维护的 Skill：

Skill 层次：

- paper-reading — single-paper workflow
- knowledge-review — cross-paper consolidation
- learning-batch — batch orchestration

- [paper-reading](paper-reading/SKILL.md) — 阅读单篇学术论文 PDF 并整合到知识库。`Status: v1 / validated with ReAct workflow`
- [knowledge-review](knowledge-review/SKILL.md) — 跨论文知识整合与阶段性复盘。`Status: v1 / validated with ReAct + Toolformer + Reflexion`
- `code-reading`
- `literature-review`
- `concept-updating`
- `research-comparison`

其他 Skill 当前只保留规划项，不实现复杂 Skill。

- [learning-batch](learning-batch/SKILL.md) — 串行编排新论文批次，并调用 paper-reading 与 knowledge-review。`Status: v1 / validated from Planning Batch`

正式的知识库维护 Skill 默认在任务完成并通过自检后执行 `git add`、`git commit` 和 `git push origin main`。遇到失败、冲突、来源核对未通过、远程或认证异常，或用户明确禁用同步时，保留本地状态并停止 push。
