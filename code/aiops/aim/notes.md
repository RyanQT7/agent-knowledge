# AIM — Source-Code Reading Notes

Paper: [Leveraging LLMs for Alert Summarization and Mitigation Plan Generation](../../../papers/aiops/aim/notes.md)

## Repository Identity

- Repository: [aimframework-sudo/AIM](https://github.com/aimframework-sudo/AIM)
- Official status: Author-Endorsed Implementation
- Evidence: The paper notes provide the URL, but the cloned README contains placeholder/template wording; official implementation coverage is therefore not asserted.
- Local path: `sources/code/aiops/aim/AIM`
- Read at commit: `202bead6ee8a3ed0f0c367d4f235c647bebbc7a5`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

AIM is an LLM-assisted alert summarization and mitigation-plan generation
pipeline. It builds a few-shot or zero-shot prompt from alert/log/metric/
hostname text, asks an LLM for structured JSON, and evaluates relevance,
actionability, consistency, safety, factuality, and cost. It does not expose a
multi-step investigation Agent or execute remediation in the inspected path.

## 2. Repository Architecture

```text
alert + logs/metrics/hostname + examples
        ↓
prompt construction
        ↓
LLM JSON: alert_summary + mitigation_plan
        ↓
QAGS / LLM evaluation / safety scoring
        ↓
quality and cost reports
```

## 3. Entry Points

- `src/prompt_utils.py:build_prompt` and `build_prompt_zero_shot` construct prompts.
- `src/evaluation.py` selects examples, queries models, parses output, and computes metrics.
- `src/llm_eval.py` implements LLM scoring and QAGS factual-consistency evaluation.
- `MicroSS_AIM.py` contains adaptive example selection and hybrid mitigation-safety checks.

## 4. Main Execution Flow

The test instance and few-shot examples are converted into a prompt requiring
`{"alert_summary": ..., "mitigation_plan": ...}`. `query_model` performs the
LLM request with retries; the response is parsed and scored. Adaptive examples
use text/metric similarity and MMR. Safety combines rule-based, embedding
semantic, and LLM signals; no action executor is called after the plan is
generated.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Alert summarization | `src/prompt_utils.py` | Few-shot/zero-shot LLM prompt | Output is free text inside a JSON field. |
| Mitigation plan generation | `src/prompt_utils.py` | Same LLM response contains advisory plan | Generation is not execution. |
| Example adaptation | `src/evaluation.py`, `MicroSS_AIM.py` | Similarity/MMR selection | This is context selection, not persistent Agent memory. |
| Factuality check | `src/llm_eval.py` | QAGS-style question generation/answer comparison | Evaluation of text consistency, not operational recovery. |
| Safety | `MicroSS_AIM.py:mitigation_safety` | Regex/rule, embedding, and LLM scores | Hybrid safety score is a gate/metric, not a repair executor. |

## 6. Core Modules

- `src/prompt_utils.py`: prompt and JSON contract.
- `src/evaluation.py`: model invocation and aggregate metrics.
- `src/llm_eval.py`: LLM judge/QAGS.
- `MicroSS_AIM.py`: example selection, safety checks, token/cost tracking.

## 7. Important Classes / Functions

- `build_prompt`, `build_prompt_zero_shot`, and `query_model`.
- `mitigation_safety`, `rule_based_score`, `semantic_safety_score`, and `llm_safety_score`.
- Evaluation functions that calculate relevance/actionability/consistency/safety and cost.

## 8. Data Flow

```text
alert record
  → selected examples
  → structured prompt
  → LLM response
  → JSON fields
  → quality/safety/factuality metrics
```

The code passes heterogeneous alert information as prompt text. A formal
evidence object carrying source/entity/time/provenance was not found.

## 9. LLM Usage

The LLM is the summarizer and mitigation-plan writer. It is not shown choosing
tools, observing a changed environment, planning a sequence, or updating
memory across incidents. Current knowledge-base classification: **LLM-assisted
workflow**, not Agentic workflow.

## 10. Prompt Design

Prompts explicitly request factual summaries and advisory/technical plans in
JSON. Few-shot examples are selected using similarity, while zero-shot omits
examples. Structured output improves parsing but does not guarantee factual or
operational validity.

## 11. Tool System

No runtime diagnostic or remediation tool registry was found in the inspected
path. Similarity, embedding, and LLM evaluators are processing/evaluation
components, not incident investigation tools.

## 12. Planning / Orchestration

Not applicable as dynamic planning. The model generates a plan-shaped text
field, but the code has no Planner–Executor loop or replanning after
observations.

## 13. Memory / Context

Past examples are selected into the prompt for the current instance. This is
few-shot context/example retrieval, not persistent episodic memory. The code
does not show a cross-incident write/retrieve lifecycle for operational memory.

## 14. Retrieval / RAG

Similarity-based example selection is context retrieval. It should not be
called RAG or Agent memory without a documented knowledge corpus and retrieval
semantics; the inspected code uses examples/data frames rather than a general
operational knowledge service.

## 15. Graph / Topology / Algorithms

Not applicable in the inspected implementation.

## 16. Verification

QAGS and LLM scoring assess summary factuality/quality; rule/semantic/LLM
safety scores assess the proposed text. There is no fresh telemetry re-query,
controlled change, rollback, or recovery verification.

## 17. Evaluation

The code records relevance, actionability, consistency, safety, QAGS-like
factuality, and token/cost-related measures. These evaluate generated advice,
not whether an executed mitigation actually restored a service.

## 18. Configuration

Model/API settings, data files, and evaluator parameters configure execution.
The clone's README includes placeholder repository wording, which is why this
identity is kept conservative. No key was read.

## 19. Deterministic vs LLM Components

- Deterministic: prompt assembly, JSON parsing, similarity/MMR example selection, regex safety checks, metric aggregation, and cost bookkeeping.
- Embedding model: semantic-safety/example-similarity components.
- LLM: summary, mitigation text, QAGS/judge, and one safety signal.

## 20. Paper vs Code Differences

The paper's mitigation plan is represented in code as an advisory JSON string.
The inspected repository does not demonstrate action execution, rollback, or
post-repair recovery, so it should not be labeled autonomous remediation.

## 21. Reproducibility

Reproducibility is **Medium-Low**: prompt/evaluation code is visible, but
models, data, API configuration, and the repository's implementation coverage
need verification. No execution was attempted.

## 22. What I Learned from the Code

A safety score around a generated plan is useful, but it is not the same as a
safety-controlled actuator. In a Network AIOps system, AIM-like generation
could sit before a deterministic validator and human gate; it should not be
mistaken for the remediation lifecycle itself.

## 23. Open Questions

- Does the repository contain the exact data/evaluation path used in the paper?
- How would a generated mitigation plan be mapped to typed network actions and rollback conditions?
- Which factuality checks correlate with successful recovery rather than text quality?

## Paper ↔ Code

Paper notes: [AIM paper notes](../../../papers/aiops/aim/notes.md)

