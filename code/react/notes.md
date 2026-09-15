# ReAct — Source-Code Reading Notes

Paper: [ReAct: Synergizing Reasoning and Acting in Language Models](../../papers/react/notes.md)

## Repository Identity

- Repository: [ysymyth/ReAct](https://github.com/ysymyth/ReAct)
- Official status: Confirmed Official
- Evidence: The ReAct project page links to this repository; its README names the exact ICLR 2023 paper.
- Local path: `sources/code/agent/react/ReAct`
- Read at commit: `6bdb3a1fd38b8188fc7ba4102969fe483df8fdc9`
- Branch: `master`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; code was not executed.

## 1. What the Repository Implements

This repository is the paper's prompting and environment code for text-based
tasks. It contains task notebooks for HotpotQA, FEVER, ALFWorld, and WebShop,
plus a Wikipedia-style environment and wrappers for trajectory history and
task evaluation. It is an experiment repository, not a general-purpose Agent
runtime library.

## 2. Repository Architecture

```text
task notebook / prompt
        ↓
WikiEnv or task environment
        ↓
text action parser
        ↓
search / lookup / think / finish
        ↓
observation and trajectory wrapper
        ↓
EM/F1 or task success evaluation
```

The model-facing prompt construction is distributed between notebooks,
prompt JSON files, and wrappers rather than exposed as one reusable Agent
class.

## 3. Entry Points

- `hotpotqa.ipynb`, `FEVER.ipynb`, `alfworld.ipynb`, and `WebShop.ipynb` are the experiment entrypoints.
- `wikienv.py:WikiEnv` implements the text environment used by the knowledge-search setting.
- `wrappers.py:HistoryWrapper`, `HotPotQAWrapper`, `FeverWrapper`, and `LoggingWrapper` add history and evaluation behavior.

## 4. Main Execution Flow

For the Wikipedia-style path, `WikiEnv.reset()` returns instructions for
`search[]`, `lookup[]`, and `finish[]`. `WikiEnv.step(action)` parses one text
action, performs a search or lookup, returns an observation, and marks the
episode done on `finish[...]` (`wikienv.py:20-160`). The history wrapper then
serializes alternating actions and observations into the next model-facing
text (`wrappers.py:23-39`). The task wrappers score a finished answer with
exact match/F1 where applicable (`wrappers.py:80-134`).

## 5. Paper-to-Code Mapping

| Paper component | Code location | Implementation | Notes |
|---|---|---|---|
| Reasoning trace / thought | Task notebooks and prompt files; `wikienv.py:153-154` accepts `think[...]` | Thought is represented as text sent through the environment protocol | The environment returns a generic “Nice thought.” observation; it is not a hidden-state API. |
| Action | `wikienv.py:124-160` | Parses `search`, `lookup`, `finish`, and `think` strings | The action schema is textual, not structured function calling. |
| Observation | `WikiEnv.search_step`, lookup branch in `step` | Page summaries, matching sentences, or error text | Search uses a live Wikipedia HTTP request if the notebook is run. |
| Interaction history | `wrappers.py:23-39` | Rebuilds prompt from initial observation and action/observation pairs | This is task-local context, not persistent memory. |
| Trajectory logging | `wrappers.py:200-237` | Stores observations/actions and writes JSON | Useful for experiment inspection. |
| Evaluation | `HotPotQAWrapper`, `FeverWrapper` | EM/F1 or label match at `finish` | ALFWorld/WebShop evaluation is in their notebooks/environments. |

## 6. Core Modules

- `wikienv.py`: text action environment, Wikipedia search, lookup state, step counter, and answer termination.
- `wrappers.py`: task selection, history serialization, trajectory logging, and metric calculation.
- `prompts/`: task-specific prompt material.
- Notebooks: experiment-specific model calls and orchestration.

## 7. Important Classes / Functions

- `WikiEnv.reset`, `WikiEnv.step`, `WikiEnv.search_step`, and `WikiEnv.construct_lookup_list` implement the environment interaction.
- `HistoryWrapper.observation` turns environment history into a prompt.
- `HotPotQAWrapper.get_metrics` and the FEVER wrapper compute task-level outcomes.

## 8. Data Flow

```text
Question / claim
  → model emits text action
  → WikiEnv parses action
  → HTTP page/search or local lookup state
  → text observation
  → HistoryWrapper appends Action/Observation
  → model emits next action
  → finish answer
  → task wrapper computes score
```

## 9. LLM Usage

The README states that the notebooks use GPT-3 prompting and require an
OpenAI API key. The repository does not expose a general model abstraction in
the inspected Python files; model calls and prompt loops are largely in the
notebooks. No API call was made during this reading.

## 10. Prompt Design

The key protocol is the text action vocabulary supplied at reset and the
task-specific prompt files. The code accepts free-form text only after
prefix/suffix checks, so malformed outputs become an invalid-action
observation rather than a typed tool error.

## 11. Tool System

`search[...]` and `lookup[...]` behave as external information operations, while
`think[...]` is an explicit no-op-like trace action and `finish[...]` terminates
the episode. The repository therefore demonstrates a runtime tool loop, but
not a modern schema-validated tool registry.

## 12. Planning / Orchestration

No separate Planner or plan data structure was found in the core Python code.
The next action is selected by the model from the current prompt/history.
This is consistent with a ReAct-style runtime reasoning–action loop, not an
explicit planner–executor architecture.

## 13. Memory / Context

`HistoryWrapper` retains the current trajectory in the prompt. `LoggingWrapper`
persists trajectories to files for analysis. Neither is evidence of
cross-task persistent or long-term memory in this repository.

## 14. Retrieval / RAG

The Wikipedia search/lookup path is task-time retrieval. It is not a vector
database RAG pipeline in the inspected implementation.

## 15. Graph / Topology / Algorithms

Not applicable to this repository's task environments.

## 16. Verification

Verification is task evaluation after `finish`: answer normalization and
EM/F1/label matching in wrappers. There is no independent reasoning verifier
or evidence provenance layer in the inspected core code.

## 17. Evaluation

The README reports task metrics for HotpotQA, FEVER, ALFWorld, and WebShop;
the Python wrappers implement HotpotQA EM/F1 and FEVER label scoring. Notebook
details were not exhaustively mapped in this static pass.

## 18. Configuration

`base_config.yaml`, prompt JSON files, task data, and notebook cells provide
configuration. The README requires an `OPENAI_API_KEY`; no secret was read or
stored.

## 19. Deterministic vs LLM Components

- Deterministic: action parsing, environment state transitions, lookup, history serialization, answer normalization, and metric calculation.
- LLM: natural-language reasoning and next-action selection in the experiment notebooks.
- External side effect: the search action can issue an HTTP request when executed.

## 20. Paper vs Code Differences

The paper presents a general prompting pattern across several tasks. The
repository concretely provides task notebooks and a small text environment;
it does not expose one universal Agent implementation, formal memory layer,
or structured tool-calling interface. Notebook internals were not treated as
fully mapped because this pass remained static and focused on reusable code.

## 21. Reproducibility

Reproducibility is **Medium** for the provided prompting examples: task data,
prompts, wrappers, and environment code are present, but model/API access and
some external environments are required. Exact notebook execution was not
attempted.

## 22. What I Learned from the Code

The paper's abstract loop becomes ordinary software through three small
interfaces: a text action protocol, an environment `step`, and a history
serializer. The observation is the concrete grounding boundary; without it,
the next model call has no new environment information. The code also makes
clear that “trajectory memory” here means prompt/history retention, not a
separate long-term memory subsystem.

## 23. Open Questions

- How do the notebook prompt loops differ across the four tasks?
- Which implementation details were used for the reported PaLM/GPT-3 numbers but are not represented in the reusable Python files?
- How would this text protocol map to typed tool calls while preserving ReAct's observation loop?

## Paper ↔ Code

Paper notes: [ReAct paper notes](../../papers/react/notes.md)

