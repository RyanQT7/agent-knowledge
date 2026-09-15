---
name: aiops-learning-batch
description: Orchestrate research-question-driven batches of AIOps, infrastructure, or network-operations papers by selecting a coherent scope, delegating single-paper analysis, consolidating grounded findings, and synchronizing validated knowledge.
---

# AIOps Learning Batch

## Purpose and boundary

Use this Skill to coordinate a research-driven batch of AIOps literature after a knowledge gap or research question has been identified. It is an orchestration layer, not another PDF reader, paper template, or literature-survey generator.

The responsibilities are:

~~~text
Research Question / Knowledge Gap
→ Select a coherent paper batch
→ Run aiops-paper-reading serially
→ Commit and push each successful paper
→ Run an AIOps-specific cross-paper Review
→ Update gaps, questions, inventory, map, and roadmap
→ Commit and push the Review
~~~

Keep these boundaries explicit:

- [aiops-paper-reading](../aiops-paper-reading/SKILL.md) owns one paper’s full reading, AIOps fields, Source Grounding, Concept integration, and paper-level quality checks.
- [learning-batch](../learning-batch/SKILL.md) is the generic batch coordinator; this Skill specializes selection around AIOps research questions and architecture gaps.
- AIOps Review is a research-question-driven consolidation of the successful batch, not a second paper-reading pass. Use the existing AIOps Review conventions and create an AIOps review file; do not call the generic Review by default.
- [knowledge-query](../knowledge-query/SKILL.md) is for reading and teaching from accumulated knowledge, not ingestion or batch mutation.

Do not download papers, use Web by default, install dependencies, create a batch database, process unrelated PDFs, or start the next batch automatically. Do not create another AIOps Skill as part of a batch.

## Working knowledge context

Before selecting papers, treat these as the current but revisable working model:

~~~text
Deterministic / ML Detection
→ Evidence Provenance
→ Candidate Space
→ Topology / Dependency Constraints
→ Bounded LLM / Agent Investigation
→ Verification
→ Human-gated Remediation
→ Recovery Verification
~~~

Use the latest knowledge-base material rather than hard-coding this architecture as truth. A new batch may strengthen, modify, or challenge it. Current research questions commonly include multimodal evidence alignment, evidence provenance, large or hierarchical candidate spaces, open-set and multi-root RCA, physical topology plus dynamic dependency, Agent verification, safe remediation, recovery verification, and production evaluation. Read the latest files to determine which questions currently have highest priority.

## Inputs and source priority

Support all of these forms:

~~~text
处理下一批 AIOps 论文
围绕 candidate space 处理下一批 AIOps 论文
Research Question: 如何验证 Network RCA evidence？
处理 Paper A、Paper B、Paper C
~~~

For an explicit paper or scope, honor it exactly. For “next batch” without a focus, inspect, in this order as appropriate:

~~~text
notes/aiops/research-gaps.md
notes/aiops/questions.md
notes/aiops/reading-roadmap.md
notes/aiops/reviews/
concepts/aiops/
notes/aiops/paper-inventory.md
INDEX.md
~~~

Use those files to identify the highest-value unanswered question. The source PDFs under `sources/papers/AIOps_papers/` are a candidate pool, not an instruction to read everything. A lightweight look at title-page metadata, abstract, or introduction is allowed for selection; formal reading belongs to `aiops-paper-reading`.

## Select a research-driven batch

1. Resolve each candidate PDF to a stable lowercase `paper-id` and inspect whether `papers/aiops/<paper-id>/notes.md` is already complete and indexed. Do not repeat completed papers. Resolve filename/title differences using local metadata or the paper’s title page.
2. For each unread candidate, assess the evidence available without full reading:
   - relevance to the active Research Question or Knowledge Gap;
   - contribution to an architecture layer such as Detection, Evidence, Candidate Space, Topology, RCA, Agent Investigation, Verification, Remediation, Recovery, or Evaluation;
   - transferability to Network AIOps;
   - ability to fill a current gap;
   - complementarity with other candidates;
   - apparent evidence strength and expected knowledge gain.
3. Select a coherent batch of about 3–5 papers. Surface topics may differ when the papers jointly answer one Research Question. Network transferability is an important lens, not a hard filter: benchmark, hierarchy, repair, verification, or operational-knowledge abstractions may still be valuable.
4. Before reading, establish internally (and record in the roadmap or batch Review when appropriate):

~~~text
Batch Focus
Primary Research Question(s)
Expected Knowledge Gain
Selected Papers
Why each paper is included
~~~

Do not silently expand an explicit scope. If many unread candidates remain, choose a manageable coherent subset and report the remainder. Do not select randomly or by directory order.

## Serial paper processing

Process papers one at a time. Choose an order that lets later papers benefit from earlier Concepts, normally starting with the paper that best establishes the active question or candidate mechanism.

For each selected paper:

1. Read and follow [aiops-paper-reading](../aiops-paper-reading/SKILL.md) for the complete single-paper workflow. It owns the AIOps template, task boundaries, modalities, candidate space, topology, ground truth, LLM/Agent classification, verification, production semantics, and Network AIOps relevance.
2. Re-read relevant current Concepts and AIOps notes after the previous paper’s commit so this paper works from the latest knowledge.
3. Require the paper task to pass Notes quality, Source Grounding, AIOps field completeness, Concept integration, cross-links, and research relevance before treating it as successful.
4. Let the single-paper workflow create one paper-specific commit and push it to `origin main`. Do not make a duplicate batch commit for the same paper.
5. Confirm the push and a clean or intentionally scoped worktree before starting the next paper.

Do not process selected papers in parallel and do not combine multiple papers into one paper commit.

## Failure handling

If a PDF is damaged, missing material, ambiguous, or cannot be grounded:

- record the paper as failed or skipped with the concrete reason;
- do not commit or push an incomplete note, speculative Concept, or unsupported claim;
- continue with independent selected papers when the worktree can be kept consistent;
- exclude the failed paper from the AIOps Review scope.

If a local correction can restore reliable reading without inventing evidence, repair it and rerun the single-paper checks. If the failed attempt leaves unclear uncommitted changes, preserve user work and resolve the scope before staging; never force a commit merely to keep the batch moving.

When at least two selected papers complete successfully, have enough grounded overlap, and their paper commits are pushed, create the batch’s AIOps Review. With fewer than two successful papers, skip the Review and report why.

## AIOps Knowledge Review

Create the next unused file under:

~~~text
notes/aiops/reviews/aiops-knowledge-review-v<N>.md
~~~

Never overwrite a historical Review. Use the successful papers from this batch as the primary scope; earlier papers and Reviews may provide background without silently expanding the scope to the entire repository.

The Review must be driven by the batch Research Question, not by concatenated paper summaries. Compare relationships, complementary mechanisms, incompatible assumptions, and architecture-layer contributions. Distinguish visibly:

~~~text
Paper-backed fact
Cross-paper synthesis
Research hypothesis
Open question
~~~

When relevant, reassess:

- Evidence provenance and multimodal alignment;
- candidate universe, pruning, hierarchy, open-set, and multi-root behavior;
- physical topology, dynamic dependency, causality, and graph semantics;
- bounded LLM/Agent investigation, Tool use, planning, and verification;
- remediation, recovery verification, safety, and human gates;
- production realism, evaluation units, cost, latency, and reproducibility.

The Review may explicitly strengthen, modify, challenge, weaken, or leave speculative the current Hybrid RCA architecture. Do not treat the architecture as a standard established by any one paper.

## Knowledge-base maintenance after the Review

Update only what the batch genuinely supports:

- `notes/aiops/research-gaps.md`: strengthen, weaken, reframe, or resolve a gap for the current scope; include evidence and confidence. Do not manufacture a new gap for every batch.
- `notes/aiops/questions.md`: preserve history and use `Open`, `Partially Answered`, `Answered for Current Scope`, or `Reframed`.
- `notes/aiops/reading-roadmap.md`: record the completed batch, the Research Question and expected gain, re-rank remaining papers, and define later priorities. Preserve the original triage history.
- `notes/aiops/paper-inventory.md`: mark successful papers `Full Reading: Completed` and let grounded full-reading results correct triage labels.
- `notes/aiops/literature-map.md`: record relationships among methods, Research Questions, and architecture layers rather than only adding names.
- `INDEX.md` and `notes/learning-log.md` as required by the delegated paper and Review workflows.

Do not delete historical Questions or Reviews. Do not create many new Concepts simply because the batch has a theme. Update an AIOps or generic Concept only when the knowledge remains useful across sources; otherwise keep the synthesis in the Review. Do not invoke generic `knowledge-review` unless the batch produces a material, general Agent/LLM concept change that warrants it.

## Quality and Git synchronization

After each successful paper, and again after the AIOps Review, verify the intended changes with:

~~~bash
git diff --check
git status --short
git diff --stat
git diff
~~~

Before staging, confirm the branch is `main`, `origin` is the configured knowledge-base repository, and no source PDF, secret, credential, token, or unrelated user change is included. Run `git diff --cached --check` after staging.

The normal successful sequence is:

~~~text
paper quality PASS
→ git diff --check
→ git add intended knowledge files
→ paper-specific git commit
→ git push origin main

Review quality PASS
→ git diff --check
→ git add intended knowledge files
→ Review git commit
→ git push origin main
~~~

Use one non-empty commit per successful paper and one for the batch Review. Do not force-push, rewrite history, create empty commits, or push to another remote. If quality, Source Grounding, conflict resolution, Git, remote, or authentication fails, do not push the affected work; preserve it and report the blocker. Stop after the selected papers, Review (if justified), and roadmap updates are complete.

## Completion report

Do not print full notes or the Review. Report:

~~~text
AIOps Learning Batch:
PASS / PARTIAL / NEEDS FIX

Research Focus:

Research Questions:

Selected papers:
1. ...
2. ...
3. ...

Processed successfully:
...

Failed / skipped:
...

Paper commits:
- ...

AIOps Knowledge Review:
PASS / SKIPPED / NEEDS FIX

Review file:
...

Main knowledge gained:
- ...

Current architecture changes:
Strengthened:
Modified:
Challenged:
Still speculative:

Concepts created:
Concepts updated:

Research gaps:
Strengthened:
Weakened:
Reframed:

Top remaining questions:

Roadmap updated:
YES / NO

Review commit:
...

Git push:
SUCCESS / PARTIAL / FAILED

Git status:
CLEAN / ...

Recommended next research focus:
...
~~~
