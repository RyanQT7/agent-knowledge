# Self-Evolving Knowledge Base — Lightweight Default and Optional Engine

This directory stores discovery metadata, Claim/Evidence relations, audit reports, reviewable proposals, run manifests, compact Experience Memory, feedback schemas, and incremental state. Full paper text remains in the existing `sources/papers/` (ignored PDFs) and `papers/` note locations. Do not copy a paper body into `evolution/`.

The default research path is the current Codex main session plus the existing Skills and knowledge files. The full multi-role Evolution Engine remains available as an opt-in experiment; it is not the normal entrypoint. See the [lightweight research agreement](../notes/guides/lightweight-research-workflow.md).

## Default lightweight entrypoints

Start ordinary research in the current Codex session:

```text
按知识库的轻量研究约定完成这个任务：先读取最相关的已有 SKILL.md，检索最多五条相关 Experience Memory，复用已有论文、源码和知识笔记；由当前主会话规划并直接完成研究，不启动完整 Evolution Engine。任务结束时总结新增知识、未解决问题和值得保存的经验。主题/任务：<填写任务>
```

Select task Skills explicitly when useful:

```text
使用 paper-reading 精读这篇论文，并复用本地来源与已有相关笔记：<论文>
使用 aiops-paper-reading 分析这篇 AIOps 论文：<论文>
使用 paper-code-discovery 和 code-reading 核对论文官方源码并静态追踪核心调用路径：<论文或仓库>
使用 knowledge-review 综合这些已完成的论文笔记：<专题>
```

Discovery and read-only audit remain available on demand:

```text
使用 research-discovery，检索最近 30 天与 OpsAgent 相关的新论文。
使用 knowledge-audit，检查 Multi-Agent 和 Agent Memory 知识是否存在冲突或过时内容。
```

Use `experience-memory` at task start to retrieve a few applicable lessons, and at task end only when there is durable feedback or a reusable execution lesson. History guides the process; it is not evidence for a current research claim. For commands and feedback scope, see [Experience Memory](experience/README.md) and the Skill instructions.

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

## Optional Phase 1 scripts: discovery, audit, and proposals

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

## Optional experimental mode: full Evolution Engine

Use this mode only when a task explicitly benefits from resumable multi-round autonomous research, state checkpoints, and separate Planner / Executor / Evaluator / Reflector calls. It is not the default path. The Python controller reuses discovery, Claim, audit, and Proposal code. Its model prompts refer to existing Skill protocols and include selected rules, but the Engine does not automatically load or dispatch the repository's `SKILL.md` workflows; for direct reuse of paper-reading and code-reading Skills, use the lightweight main-session path above. Codex CLI is the current replaceable backend; it uses the already configured login, `codex exec --ephemeral --json`, strict output schemas, and role-specific sandbox settings. No API key is copied or required by the engine.

Start a run from the repository root. An explicit focus is resolved against watchlist titles, groups, and keywords; unmatched themes become a temporary query with their own discovery cursor. With no focus, the engine selects a watchlist topic from current Questions, Research Gaps, Roadmaps, and Reviews:

```bash
python3 scripts/evolution/evolve.py run
python3 scripts/evolution/evolve.py run --focus "AgentOps trajectory failure attribution" --max-rounds 3 --max-model-calls 12
python3 scripts/evolution/evolve.py run --max-rounds 3 --max-model-calls 12
```

Inspect, stop, or resume a run:

```bash
python3 scripts/evolution/evolve.py status
python3 scripts/evolution/evolve.py status <RUN_ID>
python3 scripts/evolution/evolve.py stop <RUN_ID>
python3 scripts/evolution/evolve.py resume <RUN_ID>
```

`status` reads saved state. `stop` requests a cooperative stop and terminates an active model task at its next safe boundary. `resume` reuses completed, schema-checked role outputs and continues only unfinished stages. It explicitly retries a `FAILED` stage within the original call/attempt budgets; `NEEDS_REVIEW`, `BLOCKED`, and other terminal outcomes are not silently restarted. The run refuses to resume if its Goal, engine configuration, or base Git commit changed. Use a new run ID for a new experiment after other terminal outcomes.

The default limits in `config/engine.yaml` are three research rounds, twelve total model calls across all roles and retries, two retries per task, two consecutive rounds without useful gain, twenty candidates screened per round, two full-paper reads, four web-search calls for an Executor task and two for an Evaluator task, one model process at a time, a 20-minute hard task timeout (with shorter role-specific timeouts), and a one-hour run timeout. CLI values may lower (but cannot raise) the configured round and call caps. Model name and reasoning effort can be set in that file or passed with `--model` / `--reasoning-effort`; a null model uses the installed Codex CLI default. Actual token use is recorded only when returned by the CLI; call, search, and time caps remain enforced if the CLI does not expose token usage.

Each `evolution/runs/<RUN_ID>/` folder holds the frozen Goal and config, manifest/state, append-only events, baseline and per-round audits, model task prompts/results, candidate memos, independent evaluations, reflections, knowledge-gain records, and final report. Model task logs and run state are created with owner-only filesystem permissions. The separate detached worktree is used only for Executor output and is checked against a fixed list of allowed paths.

### Reusing local paper sources

Original PDFs remain in the existing `sources/papers/` tree and are ignored by Git; paper notes under `papers/<paper-id>/notes.md` link to those originals. There are currently no general parsed-text sidecars. The engine uses a small identity matcher over source IDs, DOI/arXiv IDs, titles, note metadata, and local-file links. It passes matching absolute paths to the Executor for selected candidates and to the Judge for each reported paper. Paths are references only: PDFs are not copied into run folders, and no extraction cache is created.

The Executor is instructed to use a local PDF or parsed-text file first and record precise locators. The Judge receives the same source paths independently and checks only the relevant sections, pages, figures, or tables for the specific Findings. A prior `full_text` record prevents another full read; the Judge should make a targeted evidence check. Paper notes are orientation, not primary evidence. If a path is not readable in the active Codex sandbox, the role must report that and use bounded primary-source retrieval only when needed. Matching is heuristic and may miss files; a missing local match does not mean the paper is unavailable.

The latest MemFolder continuation remains review-only: the Judge accepted candidate Finding `r01-f04` as a scoped interpretation, while `r01-f01`, `r01-f02`, `r01-f03`, and `r01-a02-f01` remain unverified because their saved excerpts were insufficient. Proposal `phase15-phase15-memfolder-cont-20261125-a3a68a8` remains a draft. The next Planner chose a saved-record evidence check with zero full reads, but that task has not been executed. No formal knowledge or Skill was changed.

### Opt-in full Engine run

From the repository root, explicitly start the experimental multi-round mode with:

```bash
python3 scripts/evolution/evolve.py run --focus "Agent Memory and Self-Evolving Agents" --max-rounds 3 --max-model-calls 12
```

`--focus` sets the run scope, watchlist topic IDs, discovery query terms, related Questions/Concepts/Research Gaps, and the topic boundary available to Planner and later rounds. Unmatched user topics use the watchlist's default sources and a stable custom-topic cursor. `--max-rounds` and `--max-model-calls` lower the configured limits and cannot raise them. Without `--focus`, selection follows the existing gap/question ranking. The engine does not schedule recurring runs.

### Review boundary

A normal run can write discovery metadata to the inbox/cursor, audit records to its run folder, and a `draft` Proposal containing `needs_review` Claim candidates after deterministic and independent checks pass. It never edits formal Concepts, Paper notes, Questions, Reviews, Lessons, INDEX, existing Claims, or Skills. It never approves/applies a Proposal, commits, pushes, or changes scheduling. Candidate knowledge gain is reported separately from approved formal knowledge gain.

Review a generated draft by reading its Proposal JSON, evidence locators, candidate memo, and independent evaluation. Approve or reject only the exact reviewed scope. Phase 1's `scripts.evolution.proposals` `check`, `approve`, and `apply` commands are the explicit path for a deliberate human-approved change; re-check immediately before apply because changed file hashes invalidate the old review. `apply` modifies only the named validated files and does not commit or push. Roll back an already committed approved change with `git revert <commit>`; before commit, restore only the exact files named by that Proposal and verify the resulting diff.

The deterministic Fake/Mock backends are for tests only and never provide research evidence. Use the default `codex-cli` backend for a real run. The engine does not schedule itself; a single `run` invocation stops when the Planner, evaluator, or a configured limit says to stop.

## Phase 2: Experience Memory and Skill Evolution

Experience Memory stores short execution lessons and user feedback in `evolution/experience/records.jsonl`. These records describe workflow behavior, not research facts or Claim evidence. The engine selects at most five relevant active records at run start and passes them as process guidance: Planner and Executor receive task-relevant lessons, Evaluator receives only evaluation-method lessons, and Reflector sees the same bounded context. Old findings are never treated as evidence for a new paper. At terminal run states, the Controller collects only useful evaluation, evidence, budget, or verified-success outcomes from structured run data; ordinary successful file operations are not stored.

Import the six known Phase 1.5/user-feedback records (repeat-safe), list or search records, and record scoped feedback:

```bash
python3 scripts/evolution/experience.py import-history
python3 scripts/evolution/experience.py list
python3 scripts/evolution/experience.py search --task-type research --topic "Agent Memory" --skill paper-reading --limit 5
python3 scripts/evolution/experience.py add --type user_feedback --task-type teaching --message "用真实论文案例解释执行过程"
python3 scripts/evolution/experience.py add --type user_feedback --task-type general --message "默认减少无实际收益的重复验证" --persistent
```

Use `--persistent` only for a preference the user explicitly wants to carry across future tasks. Add `--source-ref` for a report/run/feedback reference. Set stale items to `needs_review`, `superseded`, or `rejected`; similar records merge and preserve evidence references. For ordinary Codex tasks, retrieve a few relevant records at task start; record only durable feedback or a reusable lesson at task end. There is no global chat interception.

Skill Evolution does not edit a formal Skill while drafting or evaluating. The `skill-evolution` Skill reviews one experience-backed issue and produces a focused candidate under `evolution/skill-proposals/`. Evaluation is static and retrospective by default; it does not claim measured improvements without comparable execution. Review and operate a candidate with:

```bash
python3 scripts/evolution/skill_evolution.py list
python3 scripts/evolution/skill_evolution.py show <PROPOSAL_ID>
python3 scripts/evolution/skill_evolution.py evaluate <PROPOSAL_ID>
python3 scripts/evolution/skill_evolution.py approve <PROPOSAL_ID> --note "Reviewed diff and evidence"
python3 scripts/evolution/skill_evolution.py apply <PROPOSAL_ID>
python3 scripts/evolution/skill_evolution.py reject <PROPOSAL_ID> --note "Not reusable"
python3 scripts/evolution/skill_evolution.py rollback <PROPOSAL_ID>
```

Only an explicitly approved proposal can be applied. Apply checks the original Skill hash and the evaluated candidate hash; rollback restores the saved original only when the Skill still matches the applied version. Review its new diff and commit/push according to the normal repository workflow. The engine's bounded research flow does not auto-apply Skill proposals.

The implementation reuses the repository's prior static analysis of Reflexion, A-MEM, SkillOpt, and SkillHone in the [design report](../notes/guides/self-evolving-knowledge-base-design.md): retain bounded, source-linked experience; make small candidate edits; evaluate separately from the proposer; preserve accepted and rejected versions. This Phase 2 implementation is deliberately lighter than those research systems and adds no training, benchmark service, or automatic publishing.

### Phase 2 pilot

The imported Lesson 2 feedback points to more concrete teaching examples, annotated pseudocode, and a clear execution path. `source-code-annotation` already requires Chinese annotations, real caller/callee paths, and explanation of WHY/WHAT/HOW; its scope is source annotation, not general Lesson authoring. No matching Lesson-authoring Skill exists, so Phase 2 keeps this experience available for a suitable future task and records **No Skill Update Needed** rather than changing an unrelated Skill. The two pre-existing research proposals remain untouched.
