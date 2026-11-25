---
name: knowledge-evolution
description: Coordinate a bounded research-knowledge iteration from gaps/questions through discovery, audit, grounded paper/code reading, claims, and reviewable proposals; never publish unreviewed updates.
metadata:
  short-description: Evidence-based research knowledge iteration
---

# Knowledge Evolution

## Purpose

Run one bounded, resumable research iteration on top of the existing Markdown, Git, and Skills workflow. Reuse `paper-reading`, `learning-batch`, `knowledge-review`, `knowledge-query`, `aiops-paper-reading`, `aiops-learning-batch`, `paper-code-discovery`, and `code-reading`; do not reimplement their paper templates or reading rules.

```text
Load current state
→ Select a gap/question
→ Research Discovery
→ Deduplicate and screen
→ Knowledge Audit
→ Read up to 3 valuable papers / pinned repositories
→ Update pilot Claims
→ Draft a bounded evidence-backed Proposal
→ Review evidence and hashes
→ Wait for explicit approval before applying
→ Record outcome and stop
```

The only supported modes are `audit-only` and `proposal`. This Skill does not automatically improve Skills, rewrite lessons, start a scheduler, merge PRs, or publish unreviewed knowledge.

## Start and resume

Use a single run manifest and obey the configured limits:

```bash
python3 -m scripts.evolution.run start --mode audit-only --auto
python3 -m scripts.evolution.run start --mode proposal --topic agent-memory
python3 -m scripts.evolution.run start --mode proposal --query "recent research on agent belief-state revision"
python3 -m scripts.evolution.run resume <RUN_ID>
```

Inspect `evolution/runs/<RUN_ID>.json`, candidate queue, deterministic audit and cursors before any deeper work. The runner has already persisted each candidate batch before advancing successful cursors. On interruption, resume the same run. Candidate IDs and stable proposal IDs make re-entry idempotent.

## Select the research scope

Read the relevant Questions, Research Gaps, Reading Roadmap, most recent Review, INDEX, Concepts, and matching paper/code notes. Explain which gap the selected paper could close and how it differs from completed work. If there is no value, set `no_update_needed`, complete the run, and stop.

Use `research-discovery` with an explicit topic or its gap/question ranking. Screen at most 20 candidates and read at most 3 new papers. Prefer primary papers, author/project sources, and official code. Verify DOI/arXiv/version/repository identity. GitHub MCP is preferred when available; otherwise use a documented public page/API/read-only-Git fallback. Continue across source failures.

## Audit and read

Run `knowledge-audit` before reading. It must be read-only, bound the semantic context to at most 10 pages, and separate actual contradiction, scope qualification, version change, missing evidence, and no-update cases.

For a new paper, follow the full `paper-reading` or `aiops-paper-reading` source-grounding process, including methods, experiments, limitations, and source locators. For a batch, let `learning-batch` or `aiops-learning-batch` choose a coherent scope and `knowledge-review` synthesize only after enough papers succeed. For repositories, run `paper-code-discovery` and then `code-reading` at a pinned full SHA. Never infer the method from an abstract or README alone when full reading was requested.

### Candidate worktree boundary

The existing paper-reading/batch Skills normally commit and push successful work to `main`. When they are invoked as substeps of this Skill, use a dedicated local candidate branch/worktree so their default sync cannot publish unreviewed knowledge. Keep raw PDFs ignored and never stage them. Do not change or weaken the existing Skills. Once the user approves a proposal, apply only the named files, recheck base hashes and evidence, then follow the repository's ordinary commit/push rules for the approved change. Capability code/config commits may be committed separately from the research candidate.

## Claims and proposal

Add or update Claims only in `evolution/claims/claims.jsonl` during Phase 1. One JSON object per line is JSON-compatible YAML. Use the schema in `evolution/claims/README.md`; keep paper facts, code facts, cross-source synthesis, interpretations, learner signals, and execution observations distinct. A new source may support, qualify, contradict, supersede, or merely relate to an old claim.

For a worthwhile update, create a proposal JSON with `scripts.evolution.proposals` or the documented CLI. The proposal must include the affected paths, current file hashes, old content, unified diff, evidence source/version/URI/locator, related Questions/claims, uncertainty, impact, and rollback. Keep one proposal to at most 3 core files. Do not edit official pages to manufacture a diff.

Validate it:

```bash
python3 -m scripts.evolution.proposals check evolution/proposals/<PROPOSAL_ID>.json
```

If any target hash changed, the approval is stale: regenerate and review the diff. Applying requires an explicit user approval and a separate `approve`/`apply` call with reviewer and note. The script never commits, pushes, or merges.

## Run state and completion

Record at least: run ID/time/mode/focus, model if exposed, Skill hashes, queries/cursor before and after, candidate/duplicate/selection counts, paper/code reads, Claims reviewed, proposals, errors, status, and actual token/cost values only when the runtime provides them. Never invent cost values. Record stage transitions with `scripts.evolution.run stage`; finish with `scripts.evolution.run finish`.

Write the final run report to `evolution/runs/first-evolution-report.md` for the first run. Later runs use `evolution/runs/<RUN_ID>-report.md`. State what was read in full versus screened by metadata only. At least one proposal is not required when evidence does not justify a change.

## Git boundary

Stage only this capability work or separately approved knowledge paths. Never use `git add .`; never stage raw PDFs, credentials, user files, temporary caches, or external checkout contents. No force push, reset, or history rewrite. The existing commit/push convention applies after approval and review; the candidate branch is not merged automatically.
