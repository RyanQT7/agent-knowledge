# Leto: Utility-Centric Agent Memory

## 1. Metadata

- **Authors:** Shuguang Chen and Salman Paracha
- **Year:** 2026
- **Venue:** arXiv preprint, cs.CL; v1 submitted 2026-11-24
- **URL / DOI:** [arXiv HTML v1](https://arxiv.org/html/2611.33005v1); arXiv:2611.33005v1
- **Local File:** No PDF downloaded. The complete official arXiv HTML v1 was read; no local PDF extraction utility was available.
- **Code:** No paper-linked repository is listed on the arXiv page. Exact-title and arXiv-ID public GitHub searches did not confirm an official repository. Code reading: not applicable; no third-party code was run.
- **Reading status:** Full paper, including method, tables, limitations, and conclusion, read on 2026-11-25.

## 2. One-Sentence Summary

Leto retains conversation sources behind an atomic-fact index, composes profile and task context for later sessions, and uses outcome feedback to prioritize which memories to serve, treating memory utility as a prediction about future task outcomes rather than as fidelity to the past.

## 3. Problem

The paper separates two failures. A **memorization gap** occurs when information needed later is absent from the stored representation. A **serving gap** occurs when useful information exists but is not supplied to the agent for the current request. A summary can faithfully cover a conversation yet omit a detail whose future importance was not apparent; similarity retrieval can miss a standing constraint that the new request does not repeat. (Source: Sec. 1; Sec. 3)

Leto defines task-relative utility for request `x` and served memory `M` as `U(x,M) = y(x,M) - y(x,∅)`, where `y` is the graded task outcome with or without memory. This definition is an evaluation objective. It is not the same quantity as a memory's factual accuracy, provenance, or intrinsic truth. (Source: Sec. 3, Eq. 1)

## 4. Motivation

Most memory systems in the comparison optimize or evaluate some form of conversation coverage, evidence recall, or retrieval similarity. These metrics can show that a record preserves or retrieves past content, but do not alone establish that supplying it improves a later response. Leto therefore treats both what to retain and what to serve as decisions whose value is known only after the later task outcome. (Source: Sec. 1–3)

## 5. Core Idea

Leto separates **retention** from **serving priority**. It keeps source conversations available behind extracted facts, so a low predicted utility does not cause immediate deletion. When a request arrives, it combines request-relevant retrieval with standing user profile and current task state. After the response, observed interaction or task signals update a utility index used to rank later serving decisions. (Source: Sec. 4.1–4.3)

The utility index is a heuristic. Leto explicitly says that outcomes are shared by all memories served in the same response, so the update does not isolate the causal contribution of each memory. A useful memory can be penalized, an unnecessary one rewarded, and a never-served memory receives no observation. The utility index also does not certify that the memory is true. (Source: Sec. 4.3, Eq. 2; Limitations)

## 6. Architecture / Workflow

```text
Conversation ends
  → retain source conversation and index extracted atomic facts
  → link each fact to its originating source span
  → consolidate revised facts while retaining prior versions
  → rewrite standing user profile and task state

Next conversation starts
  → load profile and task state
  → retrieve facts and their source spans for the request
  → filter / rank served memories by utility index and token budget
  → agent responds
  → collect lexical interaction signals or a graded task outcome
  → update utility indices for served memories
```

This is a memory-management loop around the task agent. It does not by itself define a planner, an independent fact verifier, or a verified procedure for changing the external environment. (Source: Sec. 4; Algorithm 1)

## 7. Key Concepts

- [Memory](../../concepts/memory.md): Leto distinguishes retained source material, indexed facts, profile/task summaries, and the subset served to the agent.
- [Context Engineering](../../concepts/context-engineering.md): profile, task state, retrieved source spans, and token-budget selection determine what the agent can use on a turn.
- **Evidence validity:** source spans preserve qualifications, but the utility score is not a truth score or provenance check.
- **Belief state:** the paper's fact index and task state are memory structures; the paper does not claim that every extracted fact is independently verified belief.
- **Skill:** reusable procedures may be stored as memory, but Leto does not independently test or revise the agent's instruction Skills.

## 8. Method

### 8.1 Memory indexing

Leto retains conversations and extracts atomic facts as retrieval keys. Each key points to the adjacent source span from which it was extracted, rather than serving the extracted fact alone. This can restore source wording and qualifications that fact extraction omitted. When a fact revises an earlier fact, the new version supersedes the old one without deleting the historical record. Each session also receives a short summary. (Source: Sec. 4.1)

### 8.2 Memory replay

Between conversations, Leto rewrites a concise user profile from current facts and session summaries. When a task is declared, it also creates task state containing current entity attributes and ordered summaries of earlier sessions. These standing contexts are prepared before the next request, so they can supply preferences or task progress the request leaves implicit. The summaries can still misstate the source; their presence is not independent validation. (Source: Sec. 4.2; Limitations)

### 8.3 Utility loop

Each new memory receives an initial index `u₀(m)`. When it is served, Leto looks for lexical positive / negative interaction signals, or records a graded task outcome when available. With `n` observations and initial forecast weight `k`, it updates the memory index as `u(m) = (k·u₀(m) + Σᵢ oᵢ)/(k+n)`. A threshold gates serving, and higher-index memories are favored when the context budget is exceeded. A low score does not delete the underlying memory source. (Source: Sec. 4.3, Eq. 2)

The paper distinguishes this serving heuristic from Eq. 1's counterfactual task utility: an observed outcome is shared across the set of memories supplied, while true per-memory contribution would require a comparison against the same request and agent without that item. The paper does not make that attribution. (Source: Sec. 3, Eq. 1; Sec. 4.3; Limitations)

## 9. Experiments

The paper compares Leto with six memory systems and several baselines over five benchmarks in personalization, long-horizon tasks, and long-context understanding. The results are benchmark-specific evidence, not a general guarantee that utility-ranked memory will improve every agent. (Source: Sec. 5.1)

- **PrefEval:** Table 1 reports 60.5% preference-following accuracy for Leto versus 44.2% for the strongest compared memory system, a 16.3 percentage-point difference. A lexical detector finds a preference in 84% of Leto's served contexts, but the agent follows a detected preference in 64% of those cases. Availability therefore does not ensure use. (Source: Sec. 5.2; Table 1; Fig. 3)
- **PERMA:** Table 1 reports results separately for clean single-domain and multi-domain tasks. The advantage is not uniform across all task slices; results depend on the benchmark's memory scope and task type. (Source: Sec. 5.2; Table 1)
- **MemoryArena:** Leto reports 32.01% average progress score and 18.33% success rate over five environments. Gains over no memory increase at later positions in tested shopping and search chains, but not every baseline or task favors the same design. (Source: Sec. 5.3; Table 2; Fig. 4)
- **LoCoMo / LongMemEval-S:** Leto reports 71.82% and 73.20% accuracy. It is 2.79 points below raw-history RAG on LoCoMo and 6.80 points above RAG on LongMemEval-S, while RAG serves more tokens. The mixed comparison argues against reading one benchmark as a universal ranking. (Source: Sec. 5.4; Table 3)

The paper uses lexical overlap as a proxy for whether a preference appeared in context; that is not semantic verification. Benchmark task scores evaluate the system/agent combination, not the truth of individual memory records. (Source: Sec. 5.2; Sec. 5.4)

## 10. Strengths

- Separates retaining information from deciding what to serve; a low serving score need not destroy the only source.
- Preserves source spans behind extracted facts, allowing later retrieval of omitted qualifications.
- Evaluates personalization, dependent task chains, and long-context questions separately.
- Makes the gap between memory availability and the agent's use of memory measurable.

## 11. Limitations

- Fact extraction coverage still limits which retained details can be reached through the index.
- Profile and task summaries can misstate what the original sessions established.
- Shared outcome feedback cannot identify which served memory caused success or failure; lexical interaction signals are coarse.
- Memories never served receive no feedback, and utility estimates are specific to the agent and task distribution observed.
- A memory can be useful to a response without being factually grounded; useful context can also be ignored by the agent.
- The paper's benchmark results do not establish that its memory policy transfers unchanged to other agents, domains, or operational settings.

(Source: Limitations; Sec. 6)

## 12. Relationship to Existing Knowledge

The existing [Memory Concept](../../concepts/memory.md) distinguishes working context, episodic experience, and durable external memory, and already warns that stored reflection can be wrong. Leto adds a separate distinction between **memory utility** and **evidence validity**: response benefit is task- and agent-relative, while truth and source reliability require their own evidence checks.

Leto's source-linked facts and retained revisions complement the existing [Reflexion note](../reflexion/notes.md), which describes bounded cross-attempt verbal experience but does not establish persistent fact versioning. Existing OpsAgent work also distinguishes current incident belief from reusable cross-incident memory: [OpsMem](../opsagent/opsmem.md) and [PoS](../opsagent/pos.md) should not be collapsed into one generic memory mechanism.

Two useful comparisons, reviewed during this pilot, are [EvoDisco](https://arxiv.org/abs/2611.22102) and [LEDGER](https://arxiv.org/abs/2611.20927). EvoDisco learns which of four fixed graph-reorganization operators to select using a graph-local retrieval proxy and a multi-event strategic score; those proxies do not certify factual truth. LEDGER explicitly models source policy, valid time, supersession, and deletion, but its source hierarchy is an assumption that can fail outside its stated setting. These sources qualify the design space; neither establishes a universal memory policy.

## 13. My Understanding

Leto changes the optimization question from “did the memory store a faithful record?” to “did the information supplied for this task help this agent?” That is a useful operational objective, but it should sit beside separate fields for evidence, source, validity interval, and correction history. A task outcome is a feedback signal about the complete context presented, not proof that each recalled item is correct or individually beneficial.

## 14. Questions

- How can an online memory system estimate the contribution of one item without expensive counterfactual replay or unsafe omission?
- How should the system distinguish a correction to a false fact from a preference change that is valid only from a later date?
- What independent checks prevent a high-utility but unsupported memory from becoming a trusted belief or Skill?
- How do utility and validity transfer when the agent, task distribution, or user changes?

## 15. Related Work

See the paper's Sec. 2 and the pilot's comparisons with A-Mem, EvoDisco, LEDGER, Reflexion, OpsMem, and PoS. These systems address different layers: associative links, adaptive graph operators, evidence / validity policies, bounded verbal feedback, operational experience, and explicit task beliefs.

## 16. Useful Definitions

- **Task-relative utility:** `U(x,M) = y(x,M) - y(x,∅)`. This is the paper's counterfactual objective, not the per-memory heuristic index. (Source: Sec. 3, Eq. 1)
- **Utility index:** an updated serving priority based on an initial forecast and observed outcomes for served memories. It is not an item-level causal effect or a truth score. (Source: Sec. 4.3, Eq. 2; Limitations)

## 17. Tags

`agent-memory`, `memory-evolution`, `utility`, `evidence-provenance`, `long-horizon-agent`, `preprint`
