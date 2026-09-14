# knowledge-query

## Purpose

Answer questions, teach concepts, compare methods, review learning, generate quizzes, identify knowledge gaps, and trace conclusions to the accumulated Markdown knowledge base.

## When to use

Use for requests such as:

~~~text
基于我的知识库解释 Planning 和 Reasoning。
比较 ReAct 和 ReWOO。
给我复习当前 Agent 基础。
根据当前知识库出 10 道题考我。
我还有哪些 Agent 知识缺口？
为什么 Tool Use 不等于 Agent？
~~~

## Knowledge source priority

Read relevant local sources in this order:

1. concepts/
2. notes/reviews/
3. papers/<paper-id>/notes.md
4. notes/questions.md
5. notes/learning-log.md
6. INDEX.md

Use source PDFs only to resolve a material ambiguity or confirm an exact paper fact. Do not use Web or download material by default.

## Default behavior

Knowledge queries are read-only. They do not modify Concepts, notes, Reviews, paper notes, or the INDEX, and they do not create Git commits or pushes.

## Supported modes

- Concept explanation and teaching
- Grounded paper comparison
- Source tracing
- Review and revision
- Quiz generation and grading
- Knowledge-gap analysis

Answers distinguish paper-backed facts, cross-paper synthesis, and current interpretation or open questions.

## Write-back behavior

Only an explicit request to save, record, or update knowledge permits repository changes. After a grounded write-back passes checks, commit and push to origin main using the knowledge base Git rules.
