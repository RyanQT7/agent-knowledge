---
name: learning-batch
description: Orchestrate a small sequential batch of new local paper PDFs by delegating single-paper reading to paper-reading and cross-paper consolidation to knowledge-review. Use for requests to process several new papers, not for reading one paper or writing a standalone literature survey.
metadata:
  short-description: Orchestrate sequential paper-learning batches
---

# Learning Batch

## Purpose

Use this skill as the orchestration layer for a small batch of new papers in the current Markdown knowledge base. It coordinates, but does not replace:

- [paper-reading](../paper-reading/SKILL.md) — the complete workflow for one paper.
- [knowledge-review](../knowledge-review/SKILL.md) — cross-paper consolidation after several papers succeed.

The resulting flow is:

~~~text
Discover new PDFs
→ Establish scope and focus
→ Run paper-reading sequentially
→ Quality check, commit, and push each successful paper
→ Run knowledge-review on the successful batch when meaningful
→ Commit and push the batch Review
→ Report batch status and remaining work
~~~

Do not implement a second paper template, Concept policy, Review algorithm, database, PDF service, RAG system, or Python helper here.

## Work from the knowledge-base root

Use the repository root as the working directory. Before changing files, inspect:

- sources/papers/
- papers/
- INDEX.md
- notes/learning-log.md
- notes/reviews/

The source PDFs are raw inputs and remain under sources/papers/. Paper notes belong under papers/<paper-id>/notes.md. Follow the existing focused PDF ignore rules and never stage source PDFs, credentials, tokens, or unrelated files.

## 1. Establish the batch scope

Honor an explicit user scope exactly, such as:

~~~text
处理这 3 篇：A、B、C
处理 sources/papers/ 下尚未处理的论文
~~~

For an unspecified request such as “处理新的一批论文”:

1. List PDFs only in sources/papers/.
2. Match each PDF to a stable, lowercase papers/<paper-id>/notes.md using the title page or metadata when filename, case, spacing, abbreviation, or title differ.
3. Check INDEX.md and existing notes so completed papers are not repeated. A PDF is a candidate only when it has no corresponding complete note and is not already formally indexed.
4. Identify the likely common focus from titles, abstracts, and existing Concepts. Use a neutral General Agent Learning Batch when no reliable common theme exists.

Treat roughly 2–5 related papers as one normal batch. If an inferred candidate set is substantially larger, choose one coherent, manageable subset without asking, and report the remaining unprocessed PDFs. Do not silently process the whole repository.

If a supplied path is missing, search only the knowledge-base root, sources/papers/, and papers/ for an obvious same-paper match. Do not use Web or download material by default.

## 2. Process papers strictly sequentially

Determine an order that makes later papers benefit from earlier Concept updates, normally by foundational method first and comparison or application papers later. Then, for each selected paper:

1. Invoke [paper-reading](../paper-reading/SKILL.md) with only that paper as the active paper scope.
2. Let that Skill perform full reading, Source Grounding, paper notes, Concept decisions, cross-links, questions, learning log, INDEX update, and its quality checks.
3. Confirm the result is complete and the worktree contains no unresolved issue.
4. Confirm the current branch is main and the remote is the configured origin.
5. After a passing paper task, preserve the paper-specific commit and push to origin main before starting the next paper.
6. Re-read the relevant current notes and Concepts before the next paper so it sees the latest committed knowledge.

Do not process papers in parallel and do not combine several paper notes into one paper commit. Do not manually duplicate paper-reading instructions in this Skill.

## 3. Handle paper failures independently

If a paper is damaged, substantially incomplete, ambiguous, or cannot pass Source Grounding:

- Record it as failed or skipped with the concrete reason.
- Do not commit or push an incomplete note or speculative Concept change for that paper.
- Continue with other independent papers when doing so is safe.
- Exclude the failed paper from the batch Review scope.

If a failed paper can be corrected locally without inventing evidence, fix it and rerun the single-paper quality checks before continuing. Do not force a commit to preserve a failed attempt.

## 4. Run the batch Review only when justified

After all selected papers have been attempted, invoke [knowledge-review](../knowledge-review/SKILL.md) only when:

- at least two new papers completed successfully;
- their notes passed Source Grounding and were committed and pushed;
- they share enough topic or mechanism overlap for a useful consolidation.

The Review scope is the successful papers from this batch. Historical papers and earlier Reviews may be cited as background, but do not expand the scope to the whole repository. Pass the detected focus and exact paper-note paths to the Review Skill. Determine the next available notes/reviews/knowledge-review-v<N>.md version without overwriting history.

If fewer than two papers succeed, skip the batch Review and explain that there is not enough new, grounded material for a meaningful cross-paper synthesis. The successful paper commits still stand.

Do not perform Concept consolidation, question merging, or Review writing a second time in this orchestration layer. Let knowledge-review own those decisions.

## 5. Git synchronization

This knowledge base defaults to automatic synchronization on the main branch:

~~~text
Successful paper
→ git diff --check
→ git add intended knowledge files
→ paper-specific commit
→ git push origin main

Successful batch Review
→ git diff --check
→ git add intended knowledge files
→ one Review commit
→ git push origin main
~~~

Use one clear commit per successful paper and one clear commit for the batch Review. Do not create empty commits, force-push, rewrite history, or push to an unexpected remote. Before staging, confirm no source PDF or secret is included. After each push, confirm git status and that main tracks origin/main.

Do not commit or push when the corresponding task failed, Source Grounding is not passing, a material knowledge conflict remains unresolved, Git or remote authentication fails, or the user explicitly disables synchronization. Preserve local work and report the blocker. A later successful paper may still be processed if its scope is independent.

## 6. Batch state and reporting

Do not create a batch database or separate state file. Use paper notes, INDEX.md, learning-log.md, prior Reviews, and Git history to determine what is complete. The per-paper Skill owns the normal log and index entries; the Review Skill owns the Review entry and consolidation log.

Keep the final report concise and include:

~~~text
Learning Batch:
PASS / PARTIAL / NEEDS FIX

Focus:

New papers detected:
...

Processed successfully:
...

Failed / skipped:
...

Paper commits:
- ...

Knowledge Review:
PASS / SKIPPED / NEEDS FIX

Review file:
...

Review commit:
...

Concepts updated:
...

Main distinctions learned:
...

Questions still open:
...

Git push:
SUCCESS / PARTIAL / FAILED

Git status:
CLEAN / ...

Remaining unprocessed papers:
...
~~~

Do not print complete paper notes or the complete Review.
