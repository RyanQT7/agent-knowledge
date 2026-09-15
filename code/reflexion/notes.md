# Reflexion — Source-Code Reading Notes

Paper: [Reflexion: Language Agents with Verbal Reinforcement Learning](../../papers/reflexion/notes.md)

## Repository Identity

- Repository: [noahshinn/reflexion](https://github.com/noahshinn/reflexion)
- Official status: Confirmed Official
- Evidence: The README identifies the exact paper and its authors; the current repository URL is the resolved form of the older URL in the local paper note.
- Local path: `sources/code/agent/reflexion/reflexion`
- Read at commit: `218cf0ef1df84b05ce379dd4a8e47f17766733a0`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

The repository contains programming and WebShop/ALFWorld-style runs for
iterative attempts. A failed attempt produces textual feedback; the model
generates a reflection; a later attempt receives the prior implementation or
reflection. The code demonstrates verbal feedback carried across attempts,
not gradient-based parameter updates in the run loop.

## 2. Repository Architecture

```text
task / initial attempt
        ↓
executor or environment feedback
        ↓
reflection generation on failure
        ↓
text memory / previous implementation
        ↓
next model attempt
        ↓
evaluation and optional next trial
```

## 3. Entry Points

- `programming_runs/reflexion.py:run_reflexion` is the clearest programming loop.
- `webshop_runs/generate_reflections.py:update_memory` creates and appends reflections after unsuccessful trials.
- `webshop_runs/env_history.py` injects memory and history into the next prompt.
- `webshop_trial.py` performs per-step environment interaction and limits the retained text history.
- `main.py` orchestrates trial-level memory updates when enabled.

## 4. Main Execution Flow

In `programming_runs/reflexion.py`, the generator creates an implementation,
the executor runs tests, and a failure leads to `gen.self_reflection(...)`.
The next `gen.func_impl(...)` receives the previous implementation, feedback,
and reflection. Tests are run again and a real-test check can terminate the
attempt. Reflections, implementations, feedback, and solution status are
written to JSONL. In WebShop, `update_memory` uses the failed environment log
and at most the last three memory items to prompt a new reflection, then
appends it to the environment configuration.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Actor / attempt | `programming_runs/reflexion.py:run_reflexion` | Generator creates a function implementation | The exact generator internals are in other modules. |
| Evaluator feedback | `programming_runs/reflexion.py` | `exe.execute` and real-test checks return feedback | This is an external task signal, not merely model self-opinion. |
| Reflection | `gen.self_reflection(...)`; `webshop_runs/generate_reflections.py:_generate_reflection_query` | Text analysis of the failed attempt/feedback | It is stored as language, not weights. |
| Next attempt | `gen.func_impl(... prev_func_impl, feedback, self_reflection)` | New implementation conditioned on prior attempt and reflection | This is in-context/episodic adaptation. |
| Cross-trial memory | `env_configs[i]['memory']`, `env_history.py` | Reflection strings injected into future prompts | Retrieval is bounded to recent items in WebShop. |
| Trial trajectory | `webshop_trial.py:EnvironmentHistory` | Actions and observations become prompt history | Current trajectory context is distinct from reflection memory. |

## 6. Core Modules

- `programming_runs/reflexion.py`: iterative generate–execute–reflect loop.
- `webshop_runs/generate_reflections.py`: failed-trial reflection generation and memory append.
- `webshop_runs/env_history.py`: prompt construction with task, memory, and history.
- `webshop_trial.py`: environment-step loop and prompt history truncation.
- `README.md`: supported strategies including `NONE`, `LAST_ATTEMPT`, `REFLEXION`, and `LAST_ATTEMPT_AND_REFLEXION`.

## 7. Important Classes / Functions

- `run_reflexion`: controls attempts and feedback/reflection flow.
- `gen.self_reflection`: generates verbal feedback for the next attempt.
- `gen.func_impl`: creates a revised implementation using previous artifacts.
- `update_memory`: appends reflections only for failed WebShop trials.
- `_get_base_query`: inserts memory into the next task prompt.

## 8. Data Flow

```text
attempt code / action trajectory
  → tests or environment
  → failure feedback
  → reflection prompt
  → reflection text
  → next-attempt prompt
  → new code / actions
```

## 9. LLM Usage

The model is used to generate implementations/actions and to write the verbal
reflection. The repository supports multiple strategies, so not every run is
necessarily Reflexion. The code does not update model parameters during
`run_reflexion`; any training or model initialization outside this loop is not
treated as part of the observed memory mechanism.

## 10. Prompt Design

Reflection prompts combine the failed attempt/environment log with existing
memory examples. The next-generation prompt includes the previous artifact,
feedback, and self-reflection. In WebShop the retrieval policy limits the
reflection memory presented to the last three entries.

## 11. Tool System

Programming tests/executors and WebShop environment steps are the external
feedback interfaces. The inspected code does not expose a general named tool
registry comparable to modern function calling; task executors provide the
environment boundary.

## 12. Planning / Orchestration

The orchestration is an attempt loop rather than an explicit multi-step
planner. A reflection can change the next trajectory, but the code does not
make the reflection a formal plan or expose a planner–executor graph.

## 13. Memory / Context

There are three useful layers:

1. Current action/history context in `EnvironmentHistory`.
2. Attempt-local feedback and previous implementation.
3. Cross-trial textual reflection memory in `env_configs[i]['memory']`.

The third layer is persistent for the configured experiment state, but it is
not a vector store or a general long-term memory architecture. WebShop reads
only a bounded recent slice, and the programming loop records artifacts in
logs rather than building a retrieval service.

## 14. Retrieval / RAG

No embedding/vector retrieval is used in the inspected Reflexion memory path.
Memory is selected by recency in WebShop. Any task-specific data access is an
environment operation, not automatically RAG.

## 15. Graph / Topology / Algorithms

Not applicable to the inspected programming/WebShop implementation.

## 16. Verification

Programming verification is test execution: internal tests, followed by real
tests when the implementation appears to pass. WebShop uses task/environment
outcomes. Reflection itself is not an independent verifier; it is a generated
hypothesis about what went wrong.

## 17. Evaluation

The repository logs feedback, reflections, implementations, and solution
status. Task success is evaluated by the programming tests or environment
outcome. No universal reflection-quality metric or production safety metric
was found in the inspected paths.

## 18. Configuration

Task-specific YAML, prompt JSON, run scripts, and strategy flags configure the
experiments. API/model credentials are external; no secrets were read.

## 19. Deterministic vs LLM Components

- Deterministic: attempt counters, memory slicing, prompt assembly, test execution, environment stepping, JSONL logging, and success checks.
- LLM: implementation/action generation and verbal reflection generation.
- External feedback: tests or environment results.

## 20. Paper vs Code Differences

The paper describes a general language-agent framework. The repository offers
task-specific implementations and several baselines/strategies. The concrete
memory policy is simple textual append plus bounded retrieval in WebShop; it
should not be generalized into a complete persistent-memory architecture.

## 21. Reproducibility

Reproducibility is **Medium** for understanding the workflow and **Lower** for
running it without the task environments, model/API access, and dependencies.
The exact code was pinned above, but no execution was attempted.

## 22. What I Learned from the Code

The implementation makes “learning from failure” operationally precise:
feedback changes a language artifact that is inserted into the next attempt.
This is useful even without parameter updates, but it also means an incorrect
reflection can become a misleading future context item. Memory selection and
retention are therefore part of reliability, not merely storage.

## 23. Open Questions

- How robust is the reflection memory when the failure signal is incomplete or ambiguous?
- Which reflection content should be retained when many trials accumulate?
- How should a production agent verify that a reflection improved the causal diagnosis rather than merely changing behavior?

## Paper ↔ Code

Paper notes: [Reflexion paper notes](../../papers/reflexion/notes.md)

