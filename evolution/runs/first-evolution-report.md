# First Evolution Report — Agent Memory and Self-Evolving Agents

- **Run ID:** `first-evolution-20261125-v2`
- **Date:** 2026-11-25
- **Mode:** proposal (bounded discovery, full-paper reading, static-source discovery, semantic audit, draft proposals)
- **Main branch knowledge changes:** none. Paper notes and Concept updates exist only on local branch `knowledge-pilot/first-evolution`; the matching proposals are drafts and are not applied.

## 1. Research questions

1. How does Agent Memory progress from passive storage toward dynamic update and reuse?
2. How do Context, Memory, Belief State, and Skill differ?
3. How can past execution results become reusable experience?
4. How can memory updates avoid spreading erroneous or stale knowledge?
5. How does Knowledge Evolution differ from Skill Evolution?

The first four questions were scoped to Agent Memory. Skill Evolution was audited as a boundary question only; no Skill was edited or optimized.

## 2. Discovery and candidate screening

The first broad provider pass exposed a search-quality bug: it imported 119 off-topic or future-dated records. The query and relevance/date gates were corrected, the erroneous rows were marked `rejected` with reasons, and the focused run was repeated. These 119 rejected records are retained as run history, not eligible reading candidates.

The corrected run discovered 28 metadata records; 20 candidates passed the per-run screen limit and 8 were deferred by ranking. There were **0 duplicate identities** in the corrected run. The queue decision was: two full reads, one targeted section review without marking it fully read, and the rest deferred rather than read merely to meet a quota.

| Rank | Candidate | ID | Decision |
|---:|---|---|---|
| 1 | EvoDisco: Strategy Discovery for Evolving Agent Memory | 2611.22102v1 | Full paper read |
| 2 | MemFolder: Structure-Guided Memory Folding for Efficient Agent Memory Management | 2611.26427v1 | Deferred |
| 3 | Improving the Improver: Semantic PID Control for Medical Agent Self-Improvement | 2611.28680v2 | Deferred; domain-specific |
| 4 | Grounding Collaborative Agents in Group Cognition | 2611.29036v1 | Deferred; collaboration scope |
| 5 | FORGETMENOT: Auditing Memory Driven Privacy Risks in Commercial AI Agents | 2611.29804v1 | Deferred; privacy scope |
| 6 | BRAG: Bayesian Retrieval Augmented Generation | 2611.31656v1 | Deferred; retrieval scope |
| 7 | Multi-Agent Memory Inconsistency: Where Factual Conflicts Disappear in LLM Agents | 2611.22245v2 | Deferred; direct conflict follow-up |
| 8 | Surfacing Disagreement Beats Resolving It: Provenance-Weighted Memory for Multi-Agent Debate | 2611.22461v1 | Deferred; debate scope |
| 9 | NoeVera: Can Knowledge Guide Experiments and Experiments Refine Knowledge? | 2611.29255v1 | Deferred; experiment-loop scope |
| 10 | Leto: Utility-Centric Agent Memory | 2611.33005v1 | Full paper read |
| 11 | Forget Freely, Grep Later: Lossless, Index-Free Memory for Long-Horizon LLM Agents | 2611.25123v1 | Deferred |
| 12 | Resolution as Attention for Efficient Agent Memory Perception | 2611.24422v1 | Deferred; perception scope |
| 13 | MemoSync: Co-Managing Developer-Agent Metamemory Across Contexts | 2611.24165v1 | Deferred; developer-context scope |
| 14 | Evolve Where It Matters: Coverage-Guided Self-Evolution of Agent Skills | 2611.25429v1 | Deferred to future Skill Evolution review |
| 15 | AstronautBench: Measuring Agent Self-Improvement Across Episodes | 2611.26910v1 | Deferred; evaluation scope |
| 16 | How Much Should an Agent Remember? Deployment Lessons from Self-Distilled Memory | 2611.26361v1 | Deferred; deployment scope |
| 17 | Demystifying the Autoresearch Harness: How Context and Skills Shape Self-Evolving Agents | 2611.28244v1 | Deferred to future Skill Evolution review |
| 18 | DoppelVet: Comparative Safety Verification for Self-Evolving Agents | 2611.29306v1 | Deferred; safety-evaluation scope |
| 19 | Self-Evolving Evaluation Environments for Computer-Use Agents | 2611.30962v1 | Deferred; environment-evolution scope |
| 20 | LEDGER: Auditable Agent Memory Under Change | 2611.20927v1 | Targeted review of Sections III-C–III-E and Limitations; full read deferred |

The eight lower-ranked candidates were MemDoctor, Jetriever, ARISE, RAG in a Trenchcoat, Double Counting in LLM Evidence Fusion, Query Obfuscation with EON, `dreamor/MemVault`, and `macro-inc/macro`. The last two are generic GitHub projects surfaced by keyword metadata; neither was identified as an official implementation of a selected paper.

## 3. Sources and retrieval results

- **arXiv:** two successful focused queries; returned 20 Agent Memory and 6 Self-Evolving Agent paper records. The selected paper identities and versions were checked against their official arXiv pages.
- **OpenAlex and Crossref:** two queries each succeeded, but the 20 top results per query were future-dated relative to 2026-11-25 and were excluded before enqueueing.
- **GitHub search fallback:** the environment did not expose a callable GitHub MCP tool. Public GitHub API/search fallback was used. Two generic repositories passed metadata relevance on the Agent Memory query; none was accepted as a paper's official implementation. A separate tracked-repository poll successfully checked A-Mem and SkillOpt commit versions; SkillHone returned HTTP 403 rate limit.
- **Semantic Scholar:** both queries returned HTTP 429 after the configured bounded retry; their cursors were not advanced.
- **NKU AIOps pages:** not queried for this Agent Memory focus; those pages are configured for the OpsAgent/AIOps topics.
- **Paper identity:** Leto is arXiv:2611.33005v1, submitted 2026-11-24; EvoDisco is arXiv:2611.22102v1, submitted 2026-11-17; LEDGER is arXiv:2611.20927v1, submitted 2026-11-16. Each was cited with a version-pinned HTML URL.

The corrected source state is in [`discovery.json`](../state/discovery.json), the metadata-only [`candidate queue`](../inbox/candidates.jsonl), and the per-source cursor snapshots in the run manifest. Failed Semantic Scholar queries retained their prior cursor state.

## 4. Existing knowledge audit

The semantic audit reviewed ten bounded pages: `concepts/memory.md`, `concepts/skill.md`, Reflexion, OpsMem, PoS, Graph of States, Questions, AgentOps Research Gaps, AgentOps Review v1, and OpsAgent Research Gaps. The structured results are in [the semantic audit](../audits/first-evolution-20261125-v2-semantic.md).

- No direct contradiction or superseded core conclusion was found. Reflexion's bounded episodic memory, OpsMem's incident STM plus reusable LTM, GoS/PoS belief state, Leto's persistent source-linked memory, and EvoDisco's adaptive graph restructuring have different scopes.
- The current Memory Concept already warns that stored experience may be wrong and lists conflict/expiry as open needs. It does not yet explicitly separate evidence validity, serving utility, and retention/deletion state.
- The Skill Concept remains a placeholder. The design report documents SkillOpt and SkillHone mechanisms, but the core concept has not yet been synthesized.
- Existing AgentOps / OpsAgent reviews already require provenance, independent verification, version/scope, approval, and stale-memory checks. Those gaps remain open; this pilot does not claim to resolve them.
- Deterministic audit: **58 findings across 358 Markdown files**: 52 pre-existing broken local links, two paper README entries not reachable from INDEX, one Toolformer note lacking a detectable stable paper identifier/primary URL, two `needs_review` claims with a `qualifies` relation, and one summary finding for open/partially answered questions. Markdown links inside fenced or inline code examples are excluded. No duplicate paper identity, invalid claim schema, invalid candidate schema/status, or unprocessed candidate was found after screening. This tool reports potential issues; no existing note was rewritten to suppress them.

Most broken-link findings point into the local `sources/papers/AIOps_papers/` directory where destinations in legacy notes do not match current filenames. One OpsAgent note also has a relative link that appears to target the wrong subdirectory. Source assets and old notes were left untouched; these findings need a separate repair review.

## 5. Full-paper and source findings

### Leto

The complete official arXiv HTML v1 was read because no local PDF text-extraction utility was available; no dependency was installed. Leto retains conversations and indexes atomic facts to source spans, keeps revised facts with history, composes a profile/task state, and updates a serving-utility index from signals after memories are used. Its formal objective is response outcome with versus without served memory (Sec. 3, Eq. 1); its per-item update is a weighted heuristic on shared outcomes (Sec. 4.3, Eq. 2). A memory can help a response without being true, and a per-item score is not causal credit.

Evidence: PrefEval 60.5% versus 44.2% strongest compared memory baseline (Table 1); the lexical detector found preferences in 84% of Leto contexts but the agent followed a detected preference in 64% (Sec. 5.2, Fig. 3). MemoryArena reports 32.01% progress and 18.33% success (Sec. 5.3, Table 2). LoCoMo / LongMemEval-S report 71.82% / 73.20%, with opposite comparisons to raw-history RAG across the two benchmarks (Sec. 5.4, Table 3). This is evidence across tested benchmarks, not a universal ranking.

### EvoDisco

The complete official arXiv HTML v1 was read. It learns a policy over four fixed graph operators—Abstract, Refine, Bridge, and Reframe—while leaving the backbone frozen. Immediate feedback measures cached-query retrieval quality change minus graph complexity; a separate window-level signal updates the strategy policy. The paper explicitly distinguishes its retrieval proxy from the population task objective (Sec. 3.1, Sec. 3.3, Eqs. 4–7). On ALFWorld, transfer success is 88.6% versus MemP's 75.7%; on WebShop and DB the transfer margins are only 1.0 and 0.8 points. Removing inner / outer fitness reduces ALFWorld transfer by 9.3 / 7.9 points (Sec. 4.2–4.3, Tables 1–2). Cross-benchmark transfer has a 2.0–4.4 point gap from target-trained policies (Sec. 4.4.1, Table 3). Its fixed operator library, heuristic/scheduled trigger, single backbone, proxy reward, and lack of utility-based rollback are material limits.

### LEDGER (targeted sections; not a full-paper read)

Sections III-C–III-E and Limitations were read as supporting comparison only. The paper uses explicit source ranking, valid-time intervals, supersession, and deletion tombstones; source ordering depends on stated assumptions and can fail outside their intended domain. The abstract reports a synthetic coding-agent workload plus 210 LongMemEval questions; the paper itself cautions about synthetic evaluation and confidence overlap. Its code pointer is an anonymous artifact, not a confirmed official GitHub repository. No code was run.

No paper-specific official GitHub repository was confirmed for Leto or EvoDisco. There was no code repository to pass to the existing `code-reading` Skill for these two papers. The research-design report's prior static analysis of A-Mem, SkillOpt, and SkillHone remains the current source-code evidence for those projects.

## 6. Claim candidates

Three structured Claims were added with status `needs_review`, not `active`:

1. `agent-memory.leto.utility-feedback-1` — the per-memory index is updated from shared outcomes and does not identify each memory's causal contribution.
2. `agent-memory.evodisco.retrieval-proxy-1` — immediate transformation fitness is cached-query retrieval proxy minus complexity, not the task-population objective.
3. `agent-memory.ledger.source-policy-1` — explicit source ranking and valid time are policy mechanisms whose assumptions are scoped.

Each has version-pinned HTML evidence, section/equation locators, and a review date in [`claims.jsonl`](../claims/claims.jsonl). They do not replace or supersede existing Concepts.

## 7. Proposed updates

Two draft proposals were generated from the isolated candidate branch. Together they change four files, but neither proposal exceeds the three-file limit:

1. **`pilot-agent-memory-notes-20261125`** — add the Leto and EvoDisco paper notes. Two new files, with ABSENT base hashes.
2. **`pilot-agent-memory-concept-20261125`** — add a short Memory Concept boundary for utility versus evidence/validity and index both notes. Two existing files, with exact base hashes.

Both proposals include source-version locators, uncertainty, before-content/hash, candidate branch/commit, a reviewable unified diff, and rollback guidance. They remain `draft`; no approved update has been applied. Review and apply proposal 1 before proposal 2 so the paper links exist when INDEX is updated. If any target hash changes, regenerate and review the diff.

## 8. Current knowledge correction

No existing conclusion needs to be silently replaced. The evidence **qualifies** how a future memory architecture should be modeled: utility, truth/provenance, validity time, current belief, and Skill quality are separate dimensions. Existing open questions remain open. The candidate Concept edit is additive and preserves the earlier Reflexion/ OpsMem/PoS distinctions.

## 9. Unresolved questions

- How to estimate an individual memory's causal contribution without unsafe omission or excessive counterfactual replay.
- How to tell false fact correction from a legitimate later change in preference or operating state.
- How to independently validate memory facts and procedure memories before they become beliefs or Skills.
- How source priorities and utility estimates transfer across agents, tasks, domains, and versions.
- How to prevent operator-driven graph edits from merging contradictory or unrelated claims.
- How to gate a potentially harmful graph edit and roll it back using an independent evaluator.

## 10. Execution cost and next run

- The discovery runner used bounded metadata requests and one configured retry. Two Semantic Scholar queries were rate-limited; one SkillHone repository poll was rate-limited. Provider details and cursors are in the run manifest.
- Token use and API monetary cost were not exposed by the available tools and are recorded as unavailable. No API key was added to the repository.
- No third-party repository code was executed; no software, vector database, or scheduler was installed or enabled.
- Next run: fully read LEDGER, then compare it with Multi-Agent Memory Inconsistency and EvoDisco only if their full texts add evidence to the unresolved error-propagation questions. Run a separate structural repair review for legacy broken links and the Toolformer source identity. Keep Skill Evolution and curriculum changes disabled.
