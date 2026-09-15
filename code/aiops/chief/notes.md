# CHIEF — Source-Code Reading Notes

Paper: [From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems](../../../papers/aiops/chief/notes.md)

## Repository Identity

- Repository: [Mr-Capybara/CHIEF](https://github.com/Mr-Capybara/CHIEF)
- Official status: Likely Official
- Evidence: The README identifies the exact paper and implementation; the direct repository URL was not present in the local paper note, so status remains conservative.
- Local path: `sources/code/aiops/chief/CHIEF`
- Read at commit: `2b47170c41913c8bdea34397f7d52c65360dcef9`
- Branch: `main`
- License: No top-level `LICENSE` was observed in the clone.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

CHIEF analyzes failed LLM-based multi-agent trajectories and attributes the
decisive error to an agent and step. It transforms flat conversation logs into
a hierarchical structure, generates candidate error locations, and predicts a
final attribution. It is not a telemetry-driven network RCA system; its
primary object is responsibility within an Agent trajectory.

## 2. Repository Architecture

```text
multi-agent conversation trace + task/ground-truth context
        ↓
subtask ranges and virtual-oracle descriptions
        ↓
subtask dependency / data-transfer graph
        ↓
agent-level edges and failure modes
        ↓
candidate error subtasks / agents / steps
        ↓
final agent-and-step attribution
```

The repository also contains optional FAISS/sentence-transformer retrieval of
examples from GAIA and AssistantBench. That retrieval supplies examples for
the analysis prompt; it is not operational telemetry memory.

## 3. Entry Points

- `CHIEF.py:process_sample` is the sample-level pipeline.
- `step1_generate_subtasks` through `step4_generate_agents_edges` construct the hierarchical graph.
- `step5_predict_candidate_set` identifies candidate error locations.
- `step6_predict_final_answer` produces final attribution.
- `rag/rag_search.py:RAGRetriever` loads example indexes/records.
- `tools/` contains result/progress and recovery utilities.

## 4. Main Execution Flow

The code first parses a conversation and asks an LLM to create contiguous,
non-overlapping subtasks with ranges, oracle descriptions, evidence, and loop
metadata. It then asks for consecutive subtask edges, agent/data-flow details,
and within-subtask agent edges. Step 5 asks for at least five candidate error
steps using loop, data, and irrecoverability rules; Step 6 selects the final
agent/step attribution. `process_sample` serializes all intermediate outputs
for evaluation.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Hierarchical Causal Graph (HCG) | `CHIEF.py:step1_generate_subtasks`–`step4_generate_agents_edges` | LLM-generated subtask, dependency, agent-edge, and data-flow structures | Parsed from strict text formats; graph quality depends on LLM output. |
| Virtual oracle | `step1_generate_subtasks` | Per-subtask “The Oracle” text | In the inspected prompts, the task ground truth is also supplied. |
| Candidate localization | `step5_predict_candidate_set` | Candidate subtasks/agents/steps with loop/data/irrecoverability fields | Requires at least five candidate steps. |
| Counterfactual/irrecoverability reasoning | Step 5 prompt rules and downstream final prediction | Screens responsibility by propagation/recoverability ideas | The code represents much of this as LLM-produced structured text. |
| Final attribution | `step6_predict_final_answer` | Agent/step answer parsed into result | Target is trace responsibility, not infrastructure root node. |
| Example retrieval | `rag/rag_search.py:RAGRetriever` | FAISS similarity over GAIA/AssistantBench examples | This is few-shot/example retrieval. |

## 6. Core Modules

- `CHIEF.py`: prompts, parsers, graph construction, candidate prediction, and sample processing.
- `rag/`: prebuilt FAISS indexes, knowledge-base JSON, and retrieval code.
- `data/`: multi-agent traces and benchmark records.
- `baseline_method/`: one-shot, step-by-step, binary-search, and related baselines.
- `tools/`: result analysis and recovery scripts.

## 7. Important Classes / Functions

- `step1_generate_subtasks`, `step2_generate_subtasks_edges`, `step3_generate_agents`, `step4_generate_agents_edges`.
- `step5_predict_candidate_set` and `step6_predict_final_answer`.
- `process_sample`.
- `RAGRetriever.search`.

## 8. Data Flow

```text
trace JSON
  → parsed text/history
  → hierarchical subtask/agent graph
  → candidate error steps
  → final attribution
  → JSONL result and accuracy analysis
```

The graph fields include step IDs, agent names, data items, transformations,
correctness/confidence fields, loop metadata, and impact. These are useful
trace provenance fields, but they are generated interpretations of a log, not
raw telemetry provenance guaranteed by an instrumentation system.

## 9. LLM Usage

LLMs perform all major graph reconstruction, edge interpretation, candidate
generation, and final attribution steps. The code's main architecture is a
multi-stage LLM analysis pipeline, not a live Agent choosing operational tools.

## 10. Prompt Design

Each step has a strict plain-text schema and explicit parsing regexes. Step 1
asks for subtask ranges/oracles/evidence; later prompts ask for data transfer,
agent edges, and failure modes. The prompts include the task's correct answer
in the inspected path, corresponding to the repository's ground-truth-aware
evaluation modes. This is important when interpreting performance as an
analysis setting rather than deployment behavior.

## 11. Tool System

The main CHIEF pipeline has no operational telemetry tool loop. Its optional
RAG retriever is an offline example lookup; utility scripts analyze results.
There is no network command/configuration/remediation tool in the inspected
core path.

## 12. Planning / Orchestration

The six analysis stages form a fixed orchestration. They are not a runtime
Planner choosing the next tool based on new environment observations. The
hierarchy is a representation and search strategy over a completed trajectory.

## 13. Memory / Context

Conversation history and intermediate HCG structures are prompt context for one
sample. The FAISS indexes provide retrieved examples. Neither establishes
episodic memory of operational incidents or a cross-run Agent memory lifecycle.

## 14. Retrieval / RAG

`RAGRetriever` loads sentence-transformer embeddings and FAISS indexes and
returns top examples/text from GAIA and AssistantBench. This is a genuine
vector retrieval component in the repository, but its role is reference
example augmentation, not the system's causal graph or long-term operational
memory.

## 15. Graph / Topology / Algorithms

The HCG is a hierarchical trace/data-dependency graph. Its edges represent
subtask/agent/data dependencies inferred from conversation logs. It is not a
physical topology, service dependency graph, or proven causal graph of a
Network AIOps environment.

## 16. Verification

Final attributions are evaluated against benchmark labels, and the prompts
include loop/data/irrecoverability checks. No independent telemetry, execution,
or recovery verifier was found. A second LLM-generated graph is a structured
analysis layer, not automatically independent verification.

## 17. Evaluation

The README reports Who&When agent-/step-level accuracy and token consumption
across hand-crafted and algorithm-generated traces, with baselines. Code
utilities bucket/inspect result accuracy. These metrics measure attribution on
trace datasets, not root-cause recovery, repair success, or network safety.

## 18. Configuration

`.env`/model settings, data directories, prebuilt RAG resources, and debug
limits configure execution. The README documents dependencies and API setup;
no secret was read and no command was run.

## 19. Deterministic vs LLM Components

- Deterministic: file loading, prompt formatting, regex parsing, candidate-field serialization, result aggregation, and metric bucketing.
- LLM: subtask/edge/agent graph inference, candidate error reasoning, and final attribution.
- Retrieval: embedding/FAISS example lookup.

## 20. Paper vs Code Differences

The repository README presents a causal attribution pipeline, while the code
implements graph construction and attribution largely through successive LLM
prompts and regex parsers. The RAG data is general-agent benchmark material,
not AIOps telemetry. The use of ground-truth context in the inspected prompts
also means “with ground truth” and “without ground truth” modes must not be
collapsed when interpreting the method.

## 21. Reproducibility

Reproducibility is **Medium** for the benchmark pipeline: data, prompts,
parsers, and RAG resources are present, but model/API settings and heavy RAG
dependencies are needed. No execution was attempted.

## 22. What I Learned from the Code

CHIEF offers a useful abstraction for separating where an error appears from
where it becomes consequential: trace structure, data transfer, propagation,
and recoverability are explicit fields. For Network RCA, this suggests a
possible analogue for evidence/cause propagation, but the current code does
not validate physical causality and should not be transplanted unchanged.

## 23. Open Questions

- Can CHIEF-style irrecoverability attribution be grounded in fresh telemetry and physical topology?
- How sensitive are candidate steps and final attribution to LLM graph-construction errors?
- What would an independent counterfactual verifier look like for a live Network RCA investigation?

## Paper ↔ Code

Paper notes: [CHIEF paper notes](../../../papers/aiops/chief/notes.md)

