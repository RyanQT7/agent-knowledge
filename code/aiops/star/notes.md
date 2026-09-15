# StaR — Source-Code Reading Notes

Paper: [StaR: Stateful Dynamic-Graph Root Cause Analysis through Memory-Enhanced Causality Discovery](../../../papers/aiops/star/notes.md)

## Repository Identity

- Repository: [huanghy95/StaR](https://github.com/huanghy95/StaR)
- Official status: Confirmed Official
- Evidence: The public artifact page links the author repository and the exact paper.
- Local path: `sources/code/aiops/star/StaR`
- Read at commit: `b1f079f9aa5599f68bc079eb1045152404603a87`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

StaR extends an AERCA-style multivariate time-series RCA model with temporal
memory, graph message passing, and a neural Granger-causality layer. It is an
algorithmic AIOps implementation, not an LLM or Agent system.

## 2. Repository Architecture

```text
multivariate time-series window
        ↓
encoder / decoder with StaRGC
        ↓
temporal node memory + message passing
        ↓
Granger coefficient / prediction structure
        ↓
reconstruction and residual scores
        ↓
thresholding / top-k root-cause nodes
        ↓
causal-graph and RCA metrics
```

## 3. Entry Points

- `main.py` trains/evaluates the AERCA model and runs causal/RCA tests.
- `main_star.py` is the StaR-specific training/evaluation entrypoint.
- `models/star.py:StaR` composes encoder/decoder and root-cause evaluation.
- `models/star_gc.py:StaRGC`, `TemporalMemory`, and `GrangerCausalityLayer` implement the core model.
- `datasets/aiops.py` contains the local synthetic AIOps generator.

## 4. Main Execution Flow

The model receives windows of node variables, learns reconstruction and causal
signals, estimates thresholds from validation data, and turns residual/latent
scores into root-cause rankings. With connection history, evaluation can also
apply dynamic-graph metrics such as GAAC and TDS. This is offline model
inference over arrays, not interactive evidence collection.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Stateful memory | `models/star_gc.py:TemporalMemory` | Per-node memory vector and last-update state | Internal temporal model state, not Agent long-term memory. |
| Dynamic graph message passing | `models/star_gc.py:StaRGC.forward` | Node messages and GRU-style memory update | The graph is learned/model-defined, not automatically physical topology. |
| Causal discovery | `GrangerCausalityLayer` | Per-lag coefficient networks and predictions | Coefficients are used as causal-structure estimates under the method's assumptions. |
| Root-cause scoring | `models/star.py:_compute_root_cause_metrics` | Residual/latent scores, thresholds, top-k metrics | Candidate nodes are the modeled variables. |
| Dynamic connectivity evaluation | `utils/utils.py` | GAAC/TDS and connection-history processing | Evaluation context may include time-varying graph information. |

## 6. Core Modules

- `models/star.py`: model composition, training thresholds, RCA metrics, causal tests.
- `models/star_gc.py`: temporal memory, messages, GRU update, Granger layer.
- `models/star_gc_flexible.py`: flexible variants and corrected inner-loop aggregation.
- `datasets/aiops.py`: synthetic node-level fault propagation example.
- `utils/utils.py`: POT thresholds, top-k and graph-aware metrics.

## 7. Important Classes / Functions

- `StaR.forward`, `_get_recon_threshold`, and `_compute_root_cause_metrics`.
- `TemporalMemory.forward`, `MessageFunction`, and `GrangerCausalityLayer.forward`.
- `StaRGC.forward` and `get_causal_graph`.
- `eval_causal_structure`, `topk`, `compute_gaac`, and TDS routines.

## 8. Data Flow

```text
time-series tensor
  → window encoder
  → temporal node messages/memory
  → reconstruction and causal coefficients
  → residual / z-score arrays
  → threshold and top-k node ranking
  → RCA / graph metrics
```

The synthetic AIOps generator creates correlated neighboring nodes and 1–3
root nodes, but this is a local synthetic setting rather than evidence of a
production network deployment.

## 9. LLM Usage

Not applicable. No LLM, prompt, tool-calling, or Agent loop is used in the
inspected implementation.

## 10. Prompt Design

Not applicable.

## 11. Tool System

Not applicable. Data loading and numerical processing are direct program
operations.

## 12. Planning / Orchestration

Not applicable. The model has temporal recurrence and graph computation, but
these are not planning or action selection.

## 13. Memory / Context

`TemporalMemory` stores learned per-node temporal state and update timing for
the model's sequence processing. It is a strong example of algorithmic
statefulness, but it is not episodic Agent memory, a knowledge base, or an
external retrieval store.

## 14. Retrieval / RAG

Not applicable.

## 15. Graph / Topology / Algorithms

The implementation learns/uses dynamic causal coefficients and optional
adjacency masks. The graph represents modeled variable relationships; the code
does not establish that it is a physical network topology or a strict causal
graph in the interventionist sense.

## 16. Verification

Thresholds, reconstruction scores, causal-structure metrics, and RCA metrics
provide evaluation checks. There is no post-diagnosis telemetry re-query,
repair execution, or human gate in the inspected code.

## 17. Evaluation

The repository reports AC@k/AC*@k/Avg@k, GAAC, TDS, F1/AUROC/AUPRC, Hamming,
SHD, FDR, and TPR through code paths in `models/star.py` and `utils/utils.py`.
These measure numerical anomaly/RCA/causal-graph quality, not Agent tool
correctness or remediation success.

## 18. Configuration

`main.py`, `main_star.py`, dataset/config files, thresholds, and model-manager
artifacts configure training/evaluation. No training or inference was run.

## 19. Deterministic vs LLM Components

- Neural/statistical: encoder-decoder, temporal memory update, Granger coefficient networks, reconstruction/residual scoring.
- Deterministic: windowing, threshold application, top-k ranking, metric calculation, and file management.
- LLM/Agent: Not present.

## 20. Paper vs Code Differences

The code includes `star_gc.py` and `star_gc_flexible.py` variants. Their outer
message-aggregation placement differs: the flexible implementation places the
assignment inside the node loop, while the inspected original file places it
outside. This is a source-level discrepancy observed statically, not an
execution-verified bug.

## 21. Reproducibility

Reproducibility is **Medium** for code structure and datasets/configuration,
but exact results require the data, Python dependencies, training resources,
and selected variant. No execution was attempted.

## 22. What I Learned from the Code

StaR shows a different meaning of “memory”: state can improve temporal causal
modeling without being retrievable human-readable experience. For Network
AIOps, this distinction matters when deciding whether a temporal model state
should feed an Agent, serve as a candidate-ranking signal, or be called
memory at all.

## 23. Open Questions

- How well do learned dynamic causal edges align with physical links and device dependencies?
- How should multi-root and open-set faults be represented when the node-variable universe is fixed?
- Can temporal model state be converted into evidence with provenance without losing uncertainty?

## Paper ↔ Code

Paper notes: [StaR paper notes](../../../papers/aiops/star/notes.md)

