# Self-Evolving Knowledge Base — Phase 1

This directory stores discovery metadata, Claim/Evidence relations, audit reports, reviewable proposals, run manifests, feedback schemas, and incremental state. Full paper text remains in the existing `sources/papers/` (ignored PDFs) and `papers/` note locations. Do not copy a paper body into `evolution/`.

## One-line Codex entrypoints

Start a complete, bounded run around the highest-ranked open question/gap:

```text
使用 knowledge-evolution，围绕当前最高优先级知识缺口执行一轮迭代。
```

Start a scoped AgentOps run:

```text
使用 knowledge-evolution，围绕 AgentOps 最新研究执行一轮知识迭代。
```

Read-only checks:

```text
使用 knowledge-audit，检查 Multi-Agent 和 Agent Memory 知识是否存在冲突或过时内容。
使用 research-discovery，检索最近 30 天与 OpsAgent 相关的新论文。
```

The Codex Skill controls semantic reading and invokes the existing reading Skills. Scripts do deterministic retrieval, state management, structural audit, candidate normalization, and proposal checks.

## Layout

- `config/watchlist.yaml`: enabled research topics, keywords, priorities, mapped questions, preferred sources, author/project fields, and explicit repository watches. Files use JSON-compatible YAML so the scripts need no YAML package.
- `config/limits.yaml`: per-run candidate, full-read, audit-page, retry, timeout, overlap, and proposal caps.
- `inbox/candidates.jsonl`: metadata-only candidates and source/version events. Statuses: `discovered`, `screened`, `queued`, `reading`, `read`, `duplicate`, `deferred`, `rejected`, `blocked`.
- `claims/claims.jsonl`: pilot-scope stable claims and evidence; see `claims/README.md`.
- `audits/`: deterministic JSON/Markdown reports plus bounded semantic findings written by the Skill.
- `proposals/`: JSON proposals with unified diffs, base hashes, evidence, uncertainty, approval, and apply status. No automatic apply/commit/push.
- `runs/`: per-run JSON manifests and research reports. `first-evolution-report.md` is the first completed pilot report.
- `feedback/`: a redacted, minimal schema for future reproducible execution failures; raw chat histories are not collected.
- `state/discovery.json`: per-topic/source/query cursors, repository version checks, and last successful query timestamps. Failure does not move a cursor.

## Run, inspect, approve, reject, resume, roll back

```bash
python3 -m scripts.evolution.run start --mode audit-only --auto
python3 -m scripts.evolution.run start --mode proposal --topic agent-memory
python3 -m scripts.evolution.discovery --topic agent-memory --json
python3 -m scripts.evolution.audit --json
python3 -m scripts.evolution.run resume <RUN_ID>
```

Use the run manifest, candidate queue, and `audits/` to inspect the current state. A candidate is not a completed paper. Mark a duplicate, defer, reject, or queue decision in the candidate record with a reason and evidence. The Codex Skill records later stages and creates one proposal per bounded update.

Proposal review:

```bash
python3 -m scripts.evolution.proposals check evolution/proposals/<PROPOSAL_ID>.json
python3 -m scripts.evolution.proposals approve evolution/proposals/<PROPOSAL_ID>.json --approved-by "<reviewer>" --note "<explicit approval scope>"
python3 -m scripts.evolution.proposals apply evolution/proposals/<PROPOSAL_ID>.json --approved-by "<reviewer>" --note "<explicit approval scope>"
```

Approval is a deliberate user action, not an automatic stage. `apply` only applies the named validated patch to a clean target file set; it does not commit, push, or merge. After an approved commit, roll back with `git revert <commit>`; before commit, use the recorded base revision and restore only the approved files. If a base hash changes, regenerate and review the proposal.

## Default limits and sources

Initial budgets: screen up to 20 candidates, read at most 3 full papers, semantically audit at most 10 relevant pages, and change at most 3 files per proposal. Each metadata API request has a finite timeout and at most one retry. One run stops after discovery/audit/proposal review; it never loops. Values live in `config/limits.yaml` and should be adjusted from run telemetry.

Enabled connectors: arXiv, OpenAlex, Crossref, Semantic Scholar, GitHub public API, NKU AIOps home/publications pages, plus explicitly tracked repositories. GitHub MCP is used when available. Provider failures are reported independently. No source API keys are stored here.

## Formal knowledge and Git boundary

`audit-only` is read-only outside `evolution/audits`, `evolution/inbox`, `evolution/state`, and the run manifest. `proposal` can add Claim records, reports, and proposal files; it does not change `papers/`, `concepts/`, Questions, Reviews, Lessons, Skills, or INDEX without user approval. Candidate paper notes stay on an isolated local worktree/branch because existing reading Skills normally sync to `main`. Do not stage ignored PDFs or user files. No scheduler is enabled.
