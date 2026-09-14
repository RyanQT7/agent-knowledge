---
name: knowledge-review
description: Consolidate a defined set of existing paper notes into a grounded cross-paper review, clarify concept boundaries, update questions and indexes, and synchronize validated changes to Git; use after papers are read, not for first-time paper reading or a literature survey.
---

# Knowledge Review

## Purpose and boundaries

Use this Skill for a stage-level review after several related papers have already been read. Its job is to turn existing paper notes into cross-paper understanding:

~~~text
Paper Notes
→ Cross-paper Comparison
→ Concept Consolidation
→ Boundary Clarification
→ Question Review
→ Review Document
→ Next Learning Priorities
~~~

This is not a paper summarizer, PDF extractor, batch-processing script, or complete literature survey. Do not download or search for new material by default, re-read every PDF from scratch, analyze code, create a large number of Concepts, or modify the paper-reading Skill. Only use the current knowledge base unless the user explicitly expands the scope.

## Scope and input

Support:

- a named group such as “review ReAct, Toolformer, and Reflexion”;
- explicit paths such as `papers/react/notes.md`; or
- a clearly identifiable recent group of completed paper notes.

For an inferred scope, inspect `INDEX.md`, `notes/learning-log.md`, and `notes/reviews/`. Prefer a small, related group that has not already been reviewed. If the scope is ambiguous, do not silently expand to the whole repository; report that the scope needs review.

Work from the knowledge-base root. Read the selected paper notes first, then the relevant files under `concepts/`, `notes/questions.md`, `notes/learning-log.md`, `INDEX.md`, and prior files under `notes/reviews/`. Keep historical Reviews and Questions.

## Source policy

Paper notes are the default evidence source because they have already passed Source Grounding. Do not re-parse the source PDFs by default. Inspect only the matching PDF under `sources/papers/` when a key claim is ambiguous, a source is missing, or paper notes conflict. Do not use Web or download other sources unless the user explicitly requests it.

In the Review, label the difference between:

- `Paper-backed fact`: a claim supported by one or more selected notes, with the note’s Section, Table, Figure, Appendix, or other source locator when available;
- `Cross-paper synthesis / current interpretation`: a comparison or mental model derived during this Review.

If sources conflict, state the conflict and its scope. Do not force an unsupported reconciliation or fill missing facts from memory. Use `Unclear / Not explicitly stated in the paper` when a paper note does not establish a claim.

## Workflow

### 1. Establish the review scope

Record the exact paper-note paths and the Review version. Determine the next version from existing files under `notes/reviews/`; never overwrite a previous Review. Default to `notes/reviews/knowledge-review-v<N>.md` with the next available number.

### 2. Compare papers as a system of relationships

For each selected paper, identify the layer or problem it addresses, then synthesize:

- whether the papers solve the same problem or different layers;
- relationships, differences, complementarity, and incompatible assumptions;
- which mechanisms are explicit in a paper and which are only part of the cross-paper abstraction.

Do not produce three independent paper summaries joined together.

### 3. Consolidate Concepts

Inspect relevant `concepts/*.md` files for duplication, overly broad or narrow definitions, paper-specific details, and boundary confusion. Update a Concept only when the result is durable across sources. Keep `Status: evolving` where the knowledge is provisional.

Concept files should retain definitions, mechanisms, examples, boundaries, and representative sources—not benchmark numbers, paper-specific experiment tables, or a paper abstract. Create a new Concept only when the idea has independent cross-source value and is genuinely missing. Add only meaningful links in both directions.

### 4. Clarify boundaries

Actively check the following distinctions when relevant to the scope:

- LLM, tool-augmented LLM, Agent, and agentic workflow; tool use alone does not establish that a system is an Agent.
- Reasoning, planning, and reflection; a reasoning trace is not the model’s hidden internal state, and plan-like behavior is not necessarily an explicit Planner or Planner–Executor architecture.
- Tool selection, invocation/serialization, argument generation, execution, observation/result integration, continuation, and the tool-use policy.
- Current context, trajectory history, working-memory-like context, episodic memory, and persistent/long-term memory; historical context is not automatically long-term memory, and a reflection record is not automatically a complete memory architecture.

When the scope includes ReAct, Toolformer, or Reflexion, preserve these working distinctions:

- ReAct primarily demonstrates a runtime reasoning–action–observation interaction loop.
- Toolformer primarily addresses learned decisions about when and how to invoke APIs and integrate results; it is not automatically a complete Agent architecture.
- Reflexion uses task feedback and language-based reflection to influence later attempts; it is not automatically gradient-based training or merely “ReAct plus memory”.

These are current working distinctions, not permanent definitions. Revise them when later evidence requires it.

### 5. Write the Review document

Create `notes/reviews/knowledge-review-v<N>.md` with an adaptive version of:

~~~markdown
# Knowledge Review vN

## Scope

## 1. What I Understand So Far

## 2. Cross-Paper Relationships

## 3. Concept Boundaries

## 4. Key Mechanisms

## 5. Common Misconceptions

## 6. What Current Papers Explain Well

## 7. What They Do Not Yet Explain

## 8. Open Questions

## 9. Current Mental Model

## 10. Next Learning Priorities
~~~

The `Current Mental Model` must be identified as a cross-paper abstraction, not a standard architecture claimed by any one paper. A useful starting abstraction, when supported by the scope, is:

~~~text
Task
→ Reasoning / Decision
→ Action / Tool
→ Environment or Service
→ Observation / Feedback
→ Context / Memory
→ Next Decision
~~~

Keep optional outer evaluation, reflection, and cross-attempt memory separate unless the selected papers explicitly support them.

### 6. Review Questions

Read `notes/questions.md` and update only scope-related questions. Do not delete history. Use these statuses:

- `Status: Open`
- `Status: Partially Answered`
- `Status: Answered for Current Scope`

An answer should include a short current answer and its evidence or Review link. Merge obvious duplicates while preserving their historical origin. Prefer “Answered for Current Scope” over a permanent “Answered”.

### 7. Update the index and learning log

Add the new Review under `## Knowledge Reviews` in `INDEX.md` using a relative Markdown link. Keep the index simple.

Append a brief entry to `notes/learning-log.md` containing only the Review scope, the main conceptual change, the most important open questions, and the next learning themes. Do not copy the Review.

## Quality check

Before saving the task, check:

- cross-paper comparison is synthesis rather than parallel summaries;
- Concept edits are durable, consistent, and not paper-specific;
- reasoning, planning, reflection, tool use, Agent, and memory boundaries are not conflated;
- common misconceptions are corrected only where current sources support the correction;
- Paper-backed facts and current interpretations are visibly distinct;
- questions have statuses, history is preserved, and duplicates are not repeated;
- the new Review does not overwrite a historical Review;
- relative Markdown links resolve;
- `INDEX.md` and the learning log are updated;
- no source PDF, unrelated file, or existing knowledge was deleted or staged.

Run:

~~~bash
git diff --check
git status --short
git diff --stat
git diff
~~~

Fix clear issues before committing. Do not print the full Review to the user.

## Git synchronization

After all quality checks pass and there are actual intended changes:

1. Run `git diff --check`.
2. Confirm the current branch is `main` and `origin` is the configured knowledge-base repository.
3. If the worktree contains unrelated pre-existing changes, do not include them in this task. If it contains only this Review’s changes, `git add .` is acceptable; otherwise stage the intended paths explicitly.
4. Confirm the staged set contains no source PDFs, `.env` files, credentials, tokens, or keys, then run `git diff --cached --check`.
5. Create one concise, non-empty commit, for example `Add second cross-paper knowledge review` or `Consolidate memory concepts after knowledge review`.
6. Push normally with `git push origin main`.
7. Confirm with `git status` and `git branch -vv`.

Never create an empty commit, force-push, or rewrite history. If reading fails, source grounding is not sufficient, a material conflict remains unresolved, Git has a conflict, authentication or the remote fails, or the user disables synchronization, do not push. Preserve local work and report the issue. Source PDFs must remain governed by the existing `sources/papers/` ignore rules.

## Completion report

Normally report only:

~~~text
Knowledge Review:
PASS / NEEDS REVIEW

Scope:
...

Created:
...

Modified:
...

Main conceptual changes:
...

Questions:
...

Next learning priorities:
...

Source integrity:
PASS / NEEDS REVIEW

Git commit:
...

Git push:
SUCCESS / FAILED

Git status:
CLEAN / ...
~~~

Validation basis for v1: Knowledge Review v1 covering ReAct, Toolformer, and Reflexion.
