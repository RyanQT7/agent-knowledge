---
name: research-discovery
description: Discover and screen incremental research papers and source repositories from the knowledge base's open questions, research gaps, roadmaps, reviews, and configurable watchlist; use before paper reading, not as a paper-reading substitute.
metadata:
  short-description: Incremental research and source discovery
---

# Research Discovery

## Purpose

Turn a research question or knowledge gap into a small, deduplicated, source-grounded candidate queue. This Skill discovers metadata and links; it does not claim to understand a paper from its abstract, create a formal paper note, or update Concepts.

```text
Questions / Research Gaps / Roadmap / Reviews / Watchlist
→ Query deltas
→ Verify metadata
→ Normalize identities and versions
→ Score relevance
→ Candidate queue + cursor + run record
```

## Read first

Work from the repository root. Read `INDEX.md`, `notes/questions.md`, the relevant `notes/**/research-gaps.md`, `notes/**/reading-roadmap.md`, recent scoped Reviews, relevant Concepts, and `evolution/config/watchlist.yaml`. Watchlists are editable starting points; include an explicit user topic even when it is outside the current list.

For an automatic focus, compare open/partially answered Questions and high-confidence Research Gaps with roadmap priorities. Select one coherent question first; do not search every topic in the watchlist in one run. For a specified topic, preserve the user scope.

## Sources and fallback

Use independent source queries where available: arXiv, OpenAlex, Crossref, Semantic Scholar, the GitHub repository API or read-only Git metadata, and the NKU AIOps home/publications pages (`https://nkcs.iops.ai/`, `https://nkcs.iops.ai/publications/`). Use GitHub MCP when exposed in the current session. If it is unavailable, use narrow public GitHub pages/API or `git ls-remote`; record which source succeeded, failed, or was unavailable. A failure in one provider must not stop other providers.

Do not place API keys in URLs, logs, or state. If an authenticated API requires a missing credential, mark that source unavailable and continue with public sources.

## Run

Start a durable run through the orchestrator:

```bash
python3 -m scripts.evolution.run start --mode proposal --topic agent-memory
python3 -m scripts.evolution.run start --mode proposal --query "recent research on agent belief-state revision"
python3 -m scripts.evolution.run start --mode proposal --auto
```

For discovery only, use:

```bash
python3 -m scripts.evolution.discovery --topic agent-memory --json
python3 -m scripts.evolution.discovery --query "AgentOps trajectory failure attribution" --source arxiv --source openalex --json
```

The runner persists a per-source, per-topic/query cursor with an overlap window. It writes normalized records to `evolution/inbox/candidates.jsonl` before advancing successful cursors. Failed queries retain their prior cursor. An interrupted run can be continued with:

```bash
python3 -m scripts.evolution.run resume <RUN_ID>
```

## Metadata verification and identity

Before marking a candidate `queued`, verify enough metadata from a primary publisher/registry page to avoid acronym and title collisions. Prefer DOI, arXiv base ID, official repository URL, then normalized title plus authors. Treat a newer arXiv version as a version event on the same candidate. Relate an arXiv record to a DOI/publisher record when title/authors and the source record support the match. Treat a GitHub search hit as a repository candidate; do not call it official until `paper-code-discovery` verifies it.

Candidate records are JSON Lines objects (JSON is valid YAML 1.2) with at least:

```yaml
candidate_id: cand-...
title: ...
authors: []
publication_date: YYYY-MM-DD
publication_status: preprint | published | repository | unknown
venue: null
doi: null
arxiv_id: null
source_url: ...
source_version: ...
discovered_at: ...
research_topic: ...
related_questions: []
related_concepts: []
official_repository: null
novelty_reason: ...
relevance_reason: ...
priority: 0
status: discovered
```

The script records a metadata-only relevance rationale and a tentative local-identity comparison; these do not establish research novelty or paper quality. During screening, replace or qualify them with a human-readable decision reason and evidence. Candidate statuses are `discovered`, `screened`, `queued`, `reading`, `read`, `duplicate`, `deferred`, `rejected`, and `blocked`. Preserve a reason and source evidence for duplicate, deferred, rejected, and blocked decisions.

## Limits and handoff

Default to at most 20 screened candidates and 3 full paper reads per complete iteration. Metadata retrieval can return more records; the script stores all safely fetched records and screens only the configured limit. Never select a paper just to fill the quota. Include existing papers in the match check before queuing. Do not store full papers or duplicate paper bodies in `evolution/`; full notes remain under `papers/` in a candidate worktree.

Pass the candidate IDs, primary source links, version, dedup result, relevance explanation, and unresolved identity questions to `knowledge-audit` and then to `paper-reading`, `aiops-paper-reading`, or `paper-code-discovery` as appropriate.
