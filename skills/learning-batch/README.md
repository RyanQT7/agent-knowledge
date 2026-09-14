# learning-batch

## Purpose

Orchestrate a small, sequential batch of new paper PDFs and integrate the resulting knowledge into the Markdown knowledge base.

## When to use

Use after placing several new PDFs in sources/papers/ and asking to process a new batch, for example:

~~~text
处理新的一批论文
对 sources/papers/ 下尚未处理的论文执行一个学习批次
处理刚放进去的 3 篇 Memory 论文
~~~

## Detection and batch size

The Skill compares sources/papers/, papers/, INDEX.md, and notes/learning-log.md. It identifies PDFs without a corresponding completed paper note and formal INDEX entry, using title-page metadata when names differ. A normal inferred batch is about 2–5 related papers; a much larger set is split into a coherent subset and the remainder is reported.

## Workflow

1. Detect the scope and likely focus.
2. Run [paper-reading](../paper-reading/SKILL.md) one paper at a time.
3. Commit and push each successful paper before starting the next.
4. Run [knowledge-review](../knowledge-review/SKILL.md) on at least two successful, related papers.
5. Commit and push the batch Review, then report the outcome.

Single-paper reading and cross-paper consolidation remain owned by their respective Skills.

## Git behavior

After quality checks pass, each successful paper and the batch Review are automatically committed and pushed to origin main. Failed or insufficiently grounded work is not pushed; no force-push or history rewrite is used.

## Dependencies

- Markdown knowledge-base structure
- Existing paper-reading Skill
- Existing knowledge-review Skill
- Git remote origin configured for the knowledge base
