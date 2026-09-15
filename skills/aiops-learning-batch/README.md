# aiops-learning-batch

## Purpose

Research-question-driven orchestration for a coherent batch of AIOps, infrastructure, or Network Operations papers. It selects literature based on current knowledge gaps, delegates each paper to [aiops-paper-reading](../aiops-paper-reading/SKILL.md), and coordinates an AIOps-specific cross-paper Review.

## Difference from generic learning-batch

The generic [learning-batch](../learning-batch/SKILL.md) coordinates a small set of new papers. This Skill first asks which unanswered Research Question or architecture gap the papers can address; unread PDFs are only a candidate pool, not an automatic reading list.

## Typical workflow

~~~text
Research Question / Gap
→ Select about 3–5 complementary papers
→ Serial aiops-paper-reading
→ Per-paper quality check, commit, and push
→ AIOps Knowledge Review
→ Update gaps, questions, inventory, literature map, and roadmap
→ Review commit and push
~~~

The AIOps paper Skill owns single-paper analysis. The batch Review is created only when at least two papers succeed and provide meaningful cross-paper evidence. A batch may include different surface topics when they serve one Research Question.

## When to use

~~~text
使用 aiops-learning-batch 处理下一批 AIOps 论文。
~~~

~~~text
使用 aiops-learning-batch，围绕 open-set RCA 选择并处理下一批论文。
~~~

The usual batch size is about 3–5 papers. The workflow may choose fewer when the available, relevant literature is limited and reports skipped or remaining papers.

## Research maintenance

After a successful batch, the AIOps Review is research-question-driven and distinguishes paper facts, synthesis, hypotheses, and open questions. It may strengthen, reframe, or challenge the current Hybrid RCA architecture. It updates AIOps Research Gaps, Questions, the inventory, literature map, and reading roadmap without deleting historical records.

## Git behavior

Each successful paper has its own non-empty commit and push. A passing AIOps Review gets one additional commit and push to `origin main`. No force-push, history rewrite, empty commit, or automatic next batch is allowed; failures and unresolved Source Grounding issues are not pushed.
