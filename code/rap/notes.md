# RAP — Source-Code Reading Notes

Paper: [RAP: Reasoning with Language Model is Planning with World Model](../../papers/rap/notes.md)

## Repository Identity

- Repository: [Ber666/RAP](https://github.com/Ber666/RAP)
- Official status: Confirmed Official
- Evidence: The repository is author-controlled and identifies RAP; the paper's older `Ber666/llm-reasoners` URL was unavailable, so the URL/version discrepancy is retained rather than silently mapped to a related library.
- Local path: `sources/code/agent/rap/RAP`
- Read at commit: `774817c228b3d5ddfc18de2318f3476128ecf6eb`
- Branch: `main`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

The repository implements reasoning-as-planning for Blocksworld-like tasks.
It uses Monte Carlo Tree Search (MCTS)—a search method that expands and
evaluates alternative future action sequences—together with an LLM world model
and symbolic state updates.

## 2. Repository Architecture

```text
initial symbolic state + goal
        ↓
valid action enumeration
        ↓
MCTS selects / expands candidate reasoning branches
        ↓
LLM scores action continuations (world-model likelihood)
        ↓
LLM predicts state change
        ↓
symbolic state update + progress reward
        ↓
tree backpropagation
        ↓
best terminal trajectory / plan
```

## 3. Entry Points

- `run_blocksworld.py:ReasoningTasks.run_mcts` starts the task-level experiment.
- `rap/blocksworld_mcts.py:reasoning_mcts_search` supplies generation and reward callbacks to MCTS.
- `rap/mcts.py:MCTS` implements generic rollout, selection, expansion, simulation, and backpropagation.
- `run_blocksworld.py:validate_plan` invokes the external VAL validator when used.

## 4. Main Execution Flow

`reasoning_mcts_search` creates a root prompt with goal/state, enumerates valid
symbolic actions, scores action continuations using the language model, asks a
world-model prompt for the state change, applies that change symbolically, and
returns a reward based on goal progress. MCTS repeats rollouts and selects
high-value terminal trajectories. `run_blocksworld.py` can validate a final
plan using VAL.

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Search/planning | `rap/mcts.py:MCTS` | Tree rollout, UCT selection, expansion, simulation, backpropagation | This is the explicit planning/search component. |
| Action generation | `blocksworld_mcts.py:gen_fn` | `generate_all_actions(last_state)` creates valid symbolic choices | Candidate actions are constrained by the symbolic state. |
| World model | `blocksworld_mcts.py:r1_fn` | LLM predicts a `[CHANGE]`, then `apply_change` updates state | The LLM is used as a learned transition model. |
| Reward/value | `ReasoningMCTSNode.reward`, `r1_fn` | Combines progress and model signals | This is not a task-external observation tool. |
| Plan validation | `run_blocksworld.py:validate_plan` | VAL external validator | Validation is separate from language-model scoring. |

## 6. Core Modules

- `rap/mcts.py`: generic MCTS state and statistics.
- `rap/blocksworld_mcts.py`: Blocksworld node, action generation, world-model update, reward, and search wrapper.
- `rap/utils/blocksworld.py`: symbolic action/state utilities.
- `run_blocksworld.py`: model loading, experiment loop, and validation.

## 7. Important Classes / Functions

- `MCTS.rollout` and tree statistics `Q`, `N`, `M`.
- `ReasoningMCTSNode.find_children`, `is_terminal`, and `reward`.
- `reasoning_mcts_search`, nested `gen_fn`, and `r1_fn`.
- `apply_change` and `generate_all_actions`.

## 8. Data Flow

```text
symbolic state
  → valid action candidates
  → prompt/action histories
  → LLM log-likelihood scores
  → selected action branch
  → LLM world update
  → symbolic next state
  → goal-progress reward
  → MCTS statistics
```

## 9. LLM Usage

The code loads a LLaMA checkpoint and uses it both for action continuation
scoring and for world-state update predictions. The model is a component of
the search procedure, not a free-form tool-using Agent.

## 10. Prompt Design

Prompts encode `[GOAL]`, `[STATE n]`, `[ACTION n]`, and world-update templates.
The output is parsed for a state change and then applied to a symbolic state.
This text protocol is tightly coupled to the Blocksworld task.

## 11. Tool System

No general external tool registry is used in the inspected search path. VAL is
an external plan validator, and the LLM checkpoint is a local model resource.

## 12. Planning / Orchestration

This is search-based planning with an explicit MCTS tree and a learned world
model. It is stronger than merely producing a plan-like text trace, but it is
not a Planner–Executor Agent interacting with a live operational environment.

## 13. Memory / Context

The tree stores branch prompts and states for one search. This is search state,
not persistent Agent memory. No cross-task memory or retrieval layer was
identified.

## 14. Retrieval / RAG

Not applicable to the inspected RAP implementation.

## 15. Graph / Topology / Algorithms

The central algorithm is MCTS over symbolic task states. The tree is a search
structure, not a physical or service topology.

## 16. Verification

VAL can check whether a produced formal plan is valid. This is an independent
formal check of plan legality, but it does not validate the learned world
model's causal assumptions or a real-world system's safety.

## 17. Evaluation

The code tracks MCTS trajectories/tree snapshots and validates plans for the
Blocksworld benchmark. Model checkpoints, distributed GPU setup, and VAL are
external requirements. Exact paper result numbers remain in the paper notes.

## 18. Configuration

LLaMA checkpoint/tokenizer paths, distributed model-parallel settings,
prompt JSON, environment variables, and VAL path configure execution. No
checkpoint was downloaded and no command was run.

## 19. Deterministic vs LLM Components

- Deterministic: MCTS bookkeeping, valid action enumeration, symbolic state update, goal checks, and plan validation.
- LLM: action likelihood scoring and language-model world-state update.
- External: local checkpoint/GPU runtime and VAL validator.

## 20. Paper vs Code Differences

The implementation is a task-specific research prototype: it supplies a
Blocksworld symbolic transition function and a language world model. It should
not be generalized to a network topology model or operational Agent without
new state, observation, and safety interfaces.

## 21. Reproducibility

Reproducibility is **Low-Medium** without the LLaMA checkpoint, distributed
GPU environment, task benchmark, and VAL. The algorithmic path is visible,
but no execution was attempted.

## 22. What I Learned from the Code

RAP clarifies that “search” is not just generating several thoughts: the
implementation maintains a tree, evaluates branches, and backpropagates value.
It also shows why a world model matters—without a predicted state transition,
search cannot estimate what a candidate action would lead to. For Network
AIOps, analogous use would require a trustworthy operational transition model,
not just renaming topology data as a world model.

## 23. Open Questions

- How should uncertain or partially observed transitions be represented in an operational world model?
- How can MCTS scale to large network candidate spaces without unsafe simulated assumptions?
- What independent evidence should replace symbolic Blocksworld validation in Network RCA?

## Paper ↔ Code

Paper notes: [RAP paper notes](../../papers/rap/notes.md)

