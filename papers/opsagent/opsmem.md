# OpsMem: Dual-Memory Reasoning with Cross-Memory Resonance for Failure Diagnosis

## Bibliographic record

- **Authors:** Yongqian Sun, Rongchen Gao, Yu Luo, Wenwei Gu, Shenglin Zhang, Qingyi Guo, Qiuai Fu, Yaoliang Wu, Dan Pei.
- **Status at 2026-11-17:** ISSRE 2026 Industry Track (project/README); arXiv:2607.11357v1. The NKU record lists ISSRE 2026. The arXiv version remains a preprint record; publication is attributed to the ISSRE Industry Track based on the authors' venue materials.
- **Primary sources:** [author project page](https://luoyu100.github.io/projects/opsmem/project/), [arXiv full text](https://arxiv.org/html/2607.11357), [official GitHub](https://github.com/gaorch85/OpsMem), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local full text:** `sources/papers/opsagent/opsmem.pdf` (ignored by Git).
- **Repository inspected:** `gaorch85/OpsMem`, SHA `a22580297251ff7b5a24ce1fdab649b7df189e22`, Apache-2.0.
- **Reading status:** Full paper read (Sections II–V, tables, ablations, memory construction and limitations); source statically inspected.

## Problem and framework

OpsMem studies how current incident state and accumulated operational experience can jointly guide diagnosis. A static RAG result may be relevant to an initial symptom but become stale as hypotheses/evidence change. OpsMem therefore refreshes long-term-memory activation after each short-term diagnostic-state update.

**Pipeline (Sections III-A–D; Figures 2–4):** alert → construct graph STM with symptoms, evidence, hypotheses and derive/refine/support/refute edges → normalize current observables into query signals → match LTM pattern signals by embedding similarity → activate high-alignment/high-coverage patterns and propagate to cases/procedures → CentralAgent plans tasks for ExpertAgents → tool queries for logs/metrics/shell evidence → reports update STM → check convergence or repeat resonance/diagnosis → after incident resolution, propose LTM changes subject to feedback/approval.

- **Agent roles:** CentralAgent plans and updates shared state; ExpertAgents query diagnostic tools and summarize results; MetaAgent and memory-specific workers handle offline consolidation. Roles correspond to separate code objects/prompts. They are orchestrated in rounds, not a decentralized society.
- **LLM role:** natural-language signal normalization, planning, tool use, evidence interpretation, graph update proposals, and memory consolidation. Similarity search/ranking and graph bookkeeping are conventional code. LLM is useful for semantic alignment and flexible investigation; deterministic checks can constrain schema and state transitions.
- **Planning:** iterative task planning and evidence acquisition exist. The paper does not promise arbitrary replanning across changing tool inventories; the action loop has bounded rounds.
- **Memory:** STM is an incident-local graph; LTM stores patterns, cases, and procedures with weighted relations. Cross-Memory Resonance (CMR) has signal coupling, pattern activation, and propagation. Paper reports BGE-M3 embeddings, cosine similarity, thresholds, and top-three pattern/case/procedure context. It re-runs when STM changes.
- **State, failure, and recovery:** STM state transition/convergence is based on hypothesis support and a GoS-like state machine. System diagnosis ends with a prediction/report. LTM consolidation is post-resolution; it does not autonomously repair the service. Memory updates require accepted incident feedback and an approval workflow in the public implementation.
- **Verification:** tool outputs become evidence, STM relation structure is checked, convergence has explicit thresholds, and memory proposals go through review/approval. None proves the external root cause or a repaired service without operational ground truth.

## Evaluation and limitations

**Paper evidence (Section IV, Tables I–III):** 120 Huawei production incidents, with metrics, logs, and shell snapshots; on-call engineers establish labels through post-incident analysis. LTM is built from interviews, questionnaires, and operational documents, with all 120 test incidents excluded. Qwen3.5-27B LLM-as-a-Judge uses five independent votes and majority aggregation plus expert sampling. The public project page reports 78.33% Match / 85.83% Relevant for the described Qwen setting; improvements of 46.88% and 18.39% are relative gains over the strongest baseline, not percentage-point gains. Ablations evaluate STM, LTM, CMR, and consolidation. Sequential-window performance is suggestive of improvement, but each window has only 30 cases.

**Authors' claim:** joint dynamic memory makes diagnosis more accurate and allows reusable knowledge to improve. **Mechanism actually present:** graph STM/LTM, LLM normalization, embedding and weighted activation, bounded agent loop, post-resolution proposal and approval. **Experiments support:** relative benchmark improvement against selected agent/RAG baselines and component ablation. **Not established:** independent public replication, reduction in live MTTR from an automated intervention, causal impact of learned updates under distribution shift, or multi-root/open-set accuracy. Full Huawei corpus and LTM are not released; public code includes one sanitized case and a small seed KB. `Resolved` is externally supplied, not an agent-proven recovery outcome.

## Code reading: paper → repository → behavior

| Paper component | Static source inspected | What code does |
|---|---|---|
| Entry / diagnostic loop | `code/main.py`, `code/pipeline.py`, `code/agents/central_agent.py` | Pipeline creates shared graph and agents; CentralAgent runs plan → acquire → analyze → update STM, checks convergence, and repeats within a bounded session. |
| STM / frontier / state | `code/stm/graph.py`, `code/stm/short_term_memory.py`, `code/stm/fsm.py` | Typed nodes/edges, evidence updates, graph snapshots, candidate/frontier management and gap/support-based state transition. |
| CMR | `code/cmr/cross_memory_resonance.py` | LLM standardizes observables; embedding similarities couple signals; code computes pattern alignment and coverage, applies thresholds/top-k, then propagates to cases/procedures. |
| LTM | `code/ltm/runtime.py`, `code/ltm/store/` | Loads persistent graph store; public seed data is deliberately small/sanitized. |
| Expert tool loop | `code/agents/expert_agent.py`, `code/tools/` | Expert calls configured metric/log/shell diagnostic tools and exports traces. |
| Consolidation / approval | `code/consolidation/consolidator.py` and `workflow/` | Collects case feedback; if accepted, generates a pending update bundle and invokes an approval provider before writing. |

Static analysis only; no dependencies or scripts were run. The repository license at the recorded SHA is Apache-2.0. Public code is not equivalent to public-data reproducibility.

## Structured diagnosis and transfer

- **Candidate space:** STM hypotheses represent a local diagnostic space; this is not the same as KRCA's broad topology-based pruning. CMR narrows retrieved historical patterns and procedures, but retrieval relevance is not causal proof.
- **Failure attribution:** diagnosis ground truth is incident-level. The paper does not supply step-level labels for which agent, tool, or memory retrieval introduced an incorrect hypothesis.
- **LLM judge:** majority voting reduces single-call instability but shares model-family and rubric bias; expert sampling improves confidence but is not a public full human evaluation.
- **Network AIOps:** useful for combining current flow/topology evidence with historical fault procedures, but the LTM must encode network-specific versions, device scope, counter semantics, and safe actions. Stale runbooks and topology drift are key risks; memory activation needs provenance and expiry.

## Follow-up questions

Measure whether each memory item helps under changing topology; record retrieval provenance; compare embedding activation with topology/causal constraints; separate “resolved by engineer” from verified recovery; and evaluate unknown/multiple root causes. Cross-link [Operational knowledge](../../concepts/aiops/operational-knowledge.md), [Evidence provenance](../../concepts/aiops/evidence-provenance.md), and [Agent state / memory](../../concepts/memory.md).
