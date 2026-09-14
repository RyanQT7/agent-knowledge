# knowledge-review

## Purpose

阶段性整合已经完成的论文笔记，形成跨论文比较、Concept 边界、开放问题和下一步学习方向。

## When to use

当一组相关论文已经阅读完成、Concept 开始累积且需要复盘时使用。推荐每完成约 3–5 篇相关论文后执行一次，但不是硬性限制。

## Input

可以提供论文名称、论文笔记路径，或明确的 Review scope。例如：

~~~text
对 ReAct、Toolformer、Reflexion 做一次 Knowledge Review
~~~

## Output

- `notes/reviews/knowledge-review-v<N>.md`
- 必要的 Concept、Questions、Learning Log 和 INDEX 更新
- 质量检查通过后的 Git commit 与 `origin/main` 同步

## Typical cadence

以相关论文形成一个可比较的小批次为单位；范围不明确时不自动扩展到整个知识库。

## Git behavior

质量检查、Source Integrity 和 Markdown 链接检查全部通过且存在实际变更后，默认自动 commit 并 push 到 `origin main`。不创建空 commit，不 force push；失败、冲突、认证异常或用户禁用同步时保留本地状态并报告问题。
