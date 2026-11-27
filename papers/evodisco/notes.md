# EvoDisco: Strategy Discovery for Evolving Agent Memory

## 1. Metadata

- **Authors:** Mingyang Liu, Qingcan Kang, Shixiong Kai, Kaichao Liang, Xiaojin Fu, Tao Zhong, and Linqi Song
- **Year:** 2026
- **Venue:** arXiv preprint, cs.AI; v1 submitted 2026-11-17
- **URL / DOI:** [arXiv HTML v1](https://arxiv.org/html/2611.22102v1); arXiv:2611.22102v1
- **Local File:** No PDF downloaded. The complete official arXiv HTML v1 was read on 2026-11-25; no local PDF extraction utility was available.
- **Code:** The paper page does not link a repository. Exact-title and arXiv-ID public GitHub searches did not confirm an official implementation. No third-party code was run.
- **Reading status:** Full paper, method, experiment tables, ablations, transfer analysis, and conclusion read.

## 2. One-Sentence Summary

EvoDisco keeps the language model frozen and learns a small policy that chooses which fixed semantic operator to apply to a persistent memory graph, when to apply it, and how to instantiate it, using retrieval and task-history feedback at two timescales.

## 3. Problem

Persistent agent memory may accumulate redundant, overloaded, weakly connected, or poorly organized records. Existing systems can write and retrieve memories while keeping their update operators and schedules fixed. EvoDisco asks whether the memory transformation strategy itself can adapt from experience, rather than applying one hand-authored operator schedule to every graph and task. (Source: Sec. 1; Sec. 3.1)

The target is the organization and reuse of a memory graph. The paper does not treat every graph node as a validated fact, and it does not establish source truth, temporal validity, or a general conflict-resolution policy. Those require separate evidence and governance mechanisms. (Source: Sec. 3; Sec. 5)

## 4. Motivation

A useful graph edit depends on the current memory structure and recent task experience. A fixed schedule may abstract too early, refine the wrong node, connect unrelated areas, or repeatedly privilege one operation. EvoDisco therefore conditions operator choice and its parameters on a state representation that combines graph, retrieval, outcome, and recent strategy statistics. (Source: Sec. 3.1–3.4)

## 5. Core Idea

EvoDisco has two learning signals. An **immediate utility** scores an individual graph transformation using a historical-query retrieval-quality proxy minus a graph-complexity penalty. A **strategic efficacy** signal summarizes the policy's performance across a window of recent transformation attempts and guides updates to the operator-selection policy. The paper calls this bi-level feedback because the signals operate at different timescales; it clarifies that this is not an exact nested optimization procedure. (Source: Sec. 3.3)

The feedback is not a direct measure of truth. The immediate signal re-scores cached queries on the graph before and after an edit; it is explicitly distinguished from the population task objective. The policy can learn to improve this proxy and observed benchmark behavior without proving that every node or edge is correct. (Source: Sec. 3.1, Eq. 1; Sec. 3.3, Eqs. 4–7)

## 6. Architecture / Workflow

```text
Task episode
  → write extracted memory units and candidate relations to graph
  → retrieve a query-centered subgraph for the task
  → collect task outcome and update graph / retrieval statistics
  → at a scheduled or heuristic evolution trigger:
       encode memory graph + recent history as state
       policy selects operator + candidate graph region + parameters
       executor applies the selected transformation
       score immediate retrieval/complexity change
       periodically update policy from window-level strategic efficacy
  → after the online stream, freeze memory for held-out evaluation
```

The backbone LLM remains frozen. A lightweight policy learns operator selection; frozen LLM calls instantiate selected semantic transformations. In the reported protocol, ordinary memory writes continue after the evolution window closes, but evolution is disabled for held-out evaluation. (Source: Sec. 3; Sec. 4.1; Appendix A.1, A.9)

## 7. Key Concepts

- [Memory](../../concepts/memory.md): persistent graph organization can evolve independently of model parameters.
- [Skill](../../concepts/skill.md): a stored procedure node is not the same as a Codex `SKILL.md`; EvoDisco does not independently validate or revise instruction Skills.
- **Retrieval utility:** graph edits can improve a retrieval proxy without proving factual correctness.
- **Candidate pruning:** the executor proposes a bounded set of editable graph regions and masks operations with no candidates; this is not the same as evidence validation.

## 8. Method

### 8.1 Memory graph and state

The memory is a directed, multi-relational graph. Nodes may represent facts, episode summaries, procedures, or concepts. Nodes store embeddings, timestamps, confidence, and retrieval counts; typed edges record relations such as `causes`, `precedes`, `analogous-to`, `is-a`, and `generalizes`, with strength and evidence-recency fields. An LLM-based extractor writes memory units and candidate relations; query-centered spreading activation retrieves a subgraph for context. (Source: Sec. 3.1)

At an evolution event, the state includes graph statistics, retrieval statistics, recent outcomes, and recent operator/strategy statistics. An action selects an operator, a candidate graph region, and instantiation parameters. Candidate generation is built into fixed executor rules and is distinct from the learned policy. (Source: Sec. 3.1–3.2, Eqs. 2–3)

### 8.2 Fixed operator library, learned strategy

- **Abstract:** condense a related neighborhood into a higher-level concept or procedure and connect it to supporting memories; optional pruning may remove redundancy.
- **Refine:** decompose an overloaded memory along a temporal, causal, or categorical dimension.
- **Bridge:** connect weakly linked graph regions using a typed relation and a short linking note.
- **Reframe:** reorient relations along an existing reasoning path; node text stays unchanged.

The policy learns among these four operators and their instantiation choices. It does not invent new operator categories. The executor creates at most eight candidates per operator using graph rules and masks operators without candidates. (Source: Sec. 3.2; Appendix A.8)

### 8.3 Immediate and strategic feedback

Immediate utility is `Uᵢ = α·ΔQᵢ − β·ΔCᵢ`. `ΔQᵢ` is the change in retrieval quality on cached queries observed before the attempted edit; quality is computed from the mean of the top three spreading-activation scores. `ΔCᵢ` penalizes graph complexity. The paper explicitly says this graph-local proxy is not an estimate of the population task-score change in Eq. 1. (Source: Sec. 3.3, Eqs. 4–7)

Strategic efficacy aggregates recent operator regret, utility-prediction error, and selection diversity. A two-layer MLP policy is updated periodically with a score-function / REINFORCE-style update. A separate utility predictor is supervised from recorded transformation scores, and positive-utility state/action pairs can be replayed. The event history includes attempts even when they do not commit a graph edit; the paper states that utility-based rollback is not performed. (Source: Sec. 3.3–3.4; Appendix A.10–A.11)

### 8.4 Trigger and evaluation boundary

Evolution is triggered by a scheduled interval or a moving-average score decline; the trigger itself is not learned. Evolution is enabled only over the first 80% of the online stream. For same-benchmark held-out evaluation, the graph is frozen and both writes and evolution are disabled. A separate cross-benchmark experiment freezes the learned policy while constructing a new target-domain graph. These protocols test different kinds of transfer. (Source: Sec. 4.1; Appendix A.1, A.9)

## 9. Experiments

All methods use a frozen GPT-5-mini backbone. The four evaluated environments are ALFWorld, WebShop, and LifelongAgentBench for system administration (OS) and database manipulation (DB). Success rate is measured over a one-pass online stream and a held-out split with frozen memory. (Source: Sec. 4.1; Appendix A.2–A.4)

- **Main results:** Table 1 reports the highest observed online and frozen-transfer success rate for EvoDisco in each of the four settings. On ALFWorld it reaches 77.7% online and 88.6% transfer, compared with MemP's 68.9% and 75.7%. On WebShop the transfer margin over MemP is 1.0 point; on DB it is 0.8 points. The paper cautions that these small numerical margins are not evidence of statistical significance. (Source: Sec. 4.2; Table 1)
- **Ablation:** On ALFWorld, removing outer fitness lowers transfer from 88.6% to 80.7%; removing inner fitness lowers it to 79.3%; removing the cognitive operators lowers it to 82.1%. These are results in the paper's protocol, not proof of causal generality across tasks or backbones. (Source: Sec. 4.3; Table 2)
- **Policy transfer:** An ALFWorld-trained frozen policy trails the target-trained policy by 4.0 points on WebShop, 2.0 on OS, and 4.4 on DB. This shows a transfer gap in the tested settings, not successful universal transfer. (Source: Sec. 4.4.1; Table 3)
- **Cost:** Evolution can require graph-statistic computation, policy updates, and LLM calls for selected operations. Cost depends on how often edits are triggered and which operators are selected; it is not eliminated by freezing the backbone. (Source: Sec. 4.4.2)

## 10. Strengths

- Separates memory transformation strategy from the frozen language model's parameters.
- Makes the operator library, candidate-generation rules, feedback windows, and evaluation protocol explicit.
- Uses both a local edit signal and a longer-window strategy signal, and includes ablations for each.
- Freezes the resulting graph for held-out testing, separating online adaptation from reuse of the accumulated memory.

## 11. Limitations

- The operator library is fixed at four transformations; the trigger is scheduled or heuristic rather than learned.
- The study uses one backbone and one source benchmark for the cross-benchmark policy-transfer experiment.
- Immediate utility is a cached-query retrieval proxy regularized by graph complexity, not a direct estimate of task success, evidence truth, or source reliability.
- The approach does not supply general version, provenance, contradiction, or deletion governance for factual claims.
- The paper states that attempted edits may leave the graph unchanged and that utility-based rollback is not used; a separate review or independent test gate is needed before adopting risky transformations.
- Small differences on some benchmark columns should not be treated as statistically established improvements.

(Source: Sec. 3–5; Sec. 4.2–4.4; Conclusion)

## 12. Relationship to Existing Knowledge

The existing [Memory Concept](../../concepts/memory.md) describes Reflexion's bounded episodic memory and OpsAgent's distinction between current diagnostic state and reusable experience. EvoDisco adds a method for adapting **how a graph is reorganized** from observed retrieval/task signals; it does not collapse graph memory, validated belief, and procedural Skill into one object.

[Leto](../leto/notes.md) focuses on retaining source-backed facts and prioritizing what memory is served for future task utility. EvoDisco focuses on selecting structural operators and their parameters. The methods share a utility motivation but optimize different decisions and use different feedback signals. [LEDGER](https://arxiv.org/abs/2611.20927) addresses source policy, temporal validity, supersession, and deletion. These dimensions can complement adaptive organization, but none of the three by itself provides all three layers: retrieval utility, factual evidence governance, and independent validation of reusable procedures.

## 13. My Understanding

EvoDisco is a policy-learning layer over a predetermined memory editing toolkit. It makes strategy selection adaptive, but the available operations and the local quality proxy are still designed by the researchers. A useful integration would therefore keep evidence/provenance and validity fields outside the operator policy, constrain which graph edits can touch accepted claims, evaluate candidates on held-out tasks and independent evidence checks, and retain rollback history.

## 14. Questions

- Can the trigger learn to abstain when evidence is weak or the graph change is high-risk?
- How does an operator policy behave when task distribution, backbone, source reliability, or user preferences change?
- What independent check catches an Abstract or Bridge operation that combines unrelated or contradictory claims?
- How should graph reorganization be evaluated separately from factual claim updates, forgetting, or Skill revision?
- What is the cost / quality trade-off under a fixed token and LLM-call budget?

## 15. Related Work

The paper compares graph and agentic-memory approaches including A-Mem, G-Memory, MemP, and MemRL, as well as RAG baselines. Leto supplies a task-utility perspective; LEDGER supplies source/valid-time policy; Reflexion provides bounded verbal feedback across attempts. These systems address different update and evidence layers.

## 16. Useful Definitions

- **Memory evolution event:** a triggered operator-selection attempt; it can occur without a committed graph edit. (Source: Sec. 3.1; Appendix A.10)
- **Immediate utility:** retrieval-quality proxy change minus structural-complexity change. It is not the population task objective. (Source: Sec. 3.3, Eqs. 4–7)
- **Strategic efficacy:** a multi-event signal used to update the operator policy from regret, prediction error, and selection diversity. (Source: Sec. 3.3)

## 17. Tags

`agent-memory`, `memory-evolution`, `strategy-learning`, `retrieval`, `evaluation-gate`, `preprint`
