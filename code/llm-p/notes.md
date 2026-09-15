# LLM+P — Source-Code Reading Notes

Paper: [LLM+P: Empowering Large Language Models with Optimal Planning Proficiency](../../papers/llm-p/notes.md)

## Repository Identity

- Repository: [Cranial-XIX/llm-pddl](https://github.com/Cranial-XIX/llm-pddl)
- Official status: Confirmed Official
- Evidence: The paper's arXiv record identifies this repository for code/results.
- Local path: `sources/code/agent/llm-p/llm-pddl`
- Read at commit: `f5f897ccabfb19d5158e5a7ac4cb36517cd4c2e0`
- Branch: `main`
- License: No top-level `LICENSE` was observed in the clone.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

The code is an adapter from natural-language planning tasks to formal PDDL
problems and an external classical planner. Its main LLM+P path asks an LLM
to generate a problem PDDL description, invokes Fast Downward to compute a
plan, and optionally translates the plan back to natural language. It also
contains direct LLM and step-by-step baselines plus a separate tree-of-thought
search baseline.

## 2. Repository Architecture

```text
natural-language task + domain/examples
        ↓
LLM generates problem PDDL
        ↓
Fast Downward classical planner
        ↓
formal plan file
        ↓
optional plan validation / translation
```

## 3. Entry Points

- `main.py:Planner` holds prompt construction and LLM query logic.
- `main.py:llm_ic_pddl_planner` is the main LLM+P path.
- `main.py:llm_planner`, `llm_stepbystep_planner`, and `llm_ic_planner` are comparison paths.
- `validate_plans.py` invokes the external validator for generated plans.
- `run.py`/task configuration selects domains and instances where present.

## 4. Main Execution Flow

`llm_ic_pddl_planner` creates output folders, prompts the LLM for a problem
PDDL (conditioned on example context), writes the result, runs Fast Downward
using `os.system`, and reads the generated plan. `validate_plans.py` can then
call the external `downward/validate` executable. This is a planner-in-the-
loop pipeline, not an observation-dependent Agent environment.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Natural-language-to-PDDL translation | `main.py:Planner.create_llm_ic_pddl_prompt` and `llm_ic_pddl_planner` | LLM generates a problem PDDL from task text/examples | The LLM supplies a formal problem representation, not the final action sequence directly. |
| Explicit planner | Fast Downward invocation around `main.py:464` | External `fast-downward.py` computes a plan | Deterministic/formal planner is outside the LLM. |
| Plan validation | `validate_plans.py` | External `downward/validate` subprocess | This validates formal plan legality. |
| Baseline comparison | `llm_planner`, `llm_stepbystep_planner`, `llm_ic_planner`, `tot_bfs` | Direct generation or LLM search alternatives | These are not all the LLM+P method. |
| Plan translation | `Planner` translation block near `main.py:410` | LLM can turn PDDL plan into behaviors | The inspected block is commented because of token-limit concerns. |

## 6. Core Modules

- `main.py`: Planner class, model calls, PDDL generation, planner invocation, result saving, and baselines.
- `validate_plans.py`: formal plan validation.
- Domain/instance directories: planning benchmarks such as Blocksworld, Barman, Floortile, and others.
- Configuration files: task/domain and output settings.

## 7. Important Classes / Functions

- `Planner.query`: OpenAI ChatCompletion request with retries/key rotation behavior.
- `Planner.create_llm_ic_pddl_prompt`.
- `llm_ic_pddl_planner`.
- `ReasoningTasks.compute_plan` in `run.py` for direct Fast Downward planning.
- `validate_plan` in `run.py` / `validate_plans.py`.

## 8. Data Flow

```text
task description
  → prompt with domain/context examples
  → LLM response containing PDDL
  → PDDL file
  → Fast Downward
  → plan file
  → validator / optional natural-language rendering
```

## 9. LLM Usage

The LLM is used at the representation boundary: it translates task language
to a formal planning problem. The formal planner then searches for an action
plan. The code uses OpenAI ChatCompletion and external model/planner resources;
no credentials or calls were used in this static analysis.

## 10. Prompt Design

Prompts require only the PDDL problem output and constrain the domain name and
format. The in-context variant supplies a task-description-to-PDDL example.
This is a structured output contract enforced mostly by downstream planner
parsing/validation rather than a typed API.

## 11. Tool System

Fast Downward and the plan validator are external executables, but they are
not Agent tools selected dynamically by the LLM. They are fixed components of
the workflow.

## 12. Planning / Orchestration

This repository demonstrates an explicit planner boundary and formal search.
The LLM does not act as a runtime Planner–Executor loop; it prepares the
problem, while Fast Downward computes the plan. A separate `tot_bfs` baseline
uses a priority queue over LLM-generated/value-scored candidates, but that is
not the same mechanism as the main LLM+P path.

## 13. Memory / Context

The in-context examples are prompt context for PDDL translation. They are not
persistent memory. Output files/logs preserve experiment artifacts but do not
form a memory retrieval architecture.

## 14. Retrieval / RAG

Not applicable to the main method. Example context is loaded for prompting;
no general retrieval service was identified.

## 15. Graph / Topology / Algorithms

Formal PDDL planning and Fast Downward search are central. No operational
topology or AIOps graph is implemented.

## 16. Verification

Formal plan validation is a meaningful independent check of plan legality.
It does not by itself validate that the LLM's PDDL translation captured the
user's intended task or that the plan is operationally safe.

## 17. Evaluation

The task suite includes standard planning domains and compares LLM/planner
variants. The inspected code records generated plans/results and invokes
external planning/validation tools. Exact aggregate numbers belong in the
paper notes; this code note focuses on implementation mapping.

## 18. Configuration

Task/domain files, output folders, environment variables such as
`FAST_DOWNWARD`, model/API settings, and checkpoint/tokenizer paths configure
execution. The repository can invoke shell commands; none were run.

## 19. Deterministic vs LLM Components

- LLM: natural-language-to-PDDL translation and optional rendering.
- Deterministic/formal: PDDL parsing, Fast Downward search, plan file handling, and validator.
- Experiment support: filesystem output and subprocess orchestration.

## 20. Paper vs Code Differences

The paper's claim is about empowering an LLM with optimal planning via an
external planner. The code makes this division explicit, but also contains
several baselines and commented/optional translation paths. It should not be
described as a general autonomous Agent with tools, memory, or replanning.

## 21. Reproducibility

Reproducibility is **Medium-Low** without the specified LLM checkpoints,
Fast Downward setup, PDDL dependencies, and environment variables. The
translation/planner boundary is clear, but no run was attempted.

## 22. What I Learned from the Code

The practical value of LLM+P is interface separation: the LLM handles a
messy language representation, while a formal planner handles legal
multi-step action generation. This is a useful design pattern for deciding
which part of a system should remain deterministic.

## 23. Open Questions

- How often do generated PDDL problems preserve all semantics of the natural-language task?
- How should formal planning be combined with changing observations or partial observability?
- Which parts of the LLM+P interface could represent Network AIOps constraints without pretending the network is a closed PDDL world?

## Paper ↔ Code

Paper notes: [LLM+P paper notes](../../papers/llm-p/notes.md)

