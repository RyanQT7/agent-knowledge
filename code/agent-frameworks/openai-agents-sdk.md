# OpenAI Agents SDK — Source Code Learning Notes

Related framework: [openai/openai-agents-python](https://github.com/openai/openai-agents-python)

## Repository Identity

- Repository: `openai/openai-agents-python`
- URL: <https://github.com/openai/openai-agents-python>
- Official status: User-specified upstream project; identity is direct from the requested URL.
- Local path: `sources/code/agent-frameworks/openai-agents-python`
- Read branch: `main`
- Read at commit: `d59fdb8a789a54aff77ce61e503a04797355fc03`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; no dependency installation or code execution.

## Project Purpose and Category

This repository is an engineering-oriented Python Agent SDK. It separates an
`Agent` declaration from the `Runner` that executes turns, and adds typed
tools, handoffs, sessions, guardrails, approvals, tracing, and streaming.
Compared with a minimal ReAct loop, the main learning value is the runtime's
explicit control-plane states and safety boundaries.

## What the Repository Implements

The SDK models an Agent as configuration and capabilities: instructions or a
prompt, model, tools, handoffs, output type, guardrails, and hooks. `Runner`
owns the execution loop. A run can finish with output, execute tool calls and
continue, switch to another Agent through a handoff, pause for approval or
user input, or fail on a turn/guardrail limit.

## Core Source Map

| Concept | File | Class/Function | Purpose |
|---|---|---|---|
| Agent definition | `src/agents/agent.py` | `AgentBase`, `Agent` | Stores instructions, model, tools, handoffs, output/guardrail configuration. |
| Runtime entry | `src/agents/run.py` | `Runner.run()` | Starts a run and documents the final-output/tool/handoff loop. |
| Runtime implementation | `src/agents/run_internal/run_loop.py` | `run_single_turn()`, `run_single_turn_streamed()`, loop helpers | Resolves turns, updates current agent, handles next-step states and limits. |
| Tool execution | `src/agents/run_internal/turn_resolution.py` | `execute_tools_and_side_effects()` | Executes model-selected tools, approvals, tool guardrails, and side effects. |
| Tool schema | `src/agents/tool.py` | `FunctionTool`, `function_tool()` | Converts Python callables to JSON schemas and invokes them with validation. |
| Handoff | `src/agents/handoffs/__init__.py` | `Handoff` | Exposes agent transfer as a model-visible typed capability. |
| Guardrail | `src/agents/guardrail.py` | `InputGuardrail`, `OutputGuardrail` | Runs checks and raises a tripwire exception to halt execution. |
| Session | `src/agents/memory/session.py` | `Session`, `SQLiteSession` | Stores conversation history and continuation state when configured. |
| Model interface | `src/agents/models/interface.py` | model protocols/types | Separates provider responses and tool calls from runtime control. |
| Tracing | `src/agents/tracing/` | tracing processors/spans | Records run, model, tool, and handoff observability data. |

## Agent Execution Path

The non-streaming path is:

```text
user input
  → Runner.run()
  → prepare context/session and current Agent
  → run_single_turn()
  → model response
       ├── final output → execute final-output checks → return
       ├── handoff → execute handoff → set current Agent → next turn
       └── tool calls → execute_tools_and_side_effects()
                       → tool result / interruption
                       → append result to run context
                       → run the current Agent again
  → max_turns / guardrail / approval boundary
  → final result or interruption
```

`Runner.run()` explicitly describes this loop in `src/agents/run.py`. The
private run-loop module materializes it as next-step objects such as final
output, handoff, run-again, or interruption. This is more than a prompt loop:
the runtime owns the active Agent and the legal transitions.

## Tool Calling

`FunctionTool` contains a name, description, JSON parameter schema, async
invocation callback, strict schema option, input/output guardrails, timeout and
approval-related configuration. The `function_tool` decorator derives a tool
from a Python function's signature and docstring.

When the model emits tool calls, `execute_tools_and_side_effects()` builds the
execution plan, handles approval/deferred calls, invokes functions, collects
results, and feeds tool outputs back into the next model turn. A tool may be
read-only or side-effecting; approval and policy are runtime concerns rather
than properties guaranteed by the tool name.

## Memory / State

An Agent instance mainly holds reusable configuration, not a complete evolving
conversation. `Session` is the state carrier for conversation history and
service/session IDs; `SQLiteSession` can persist that history in a local SQLite
file, while the default can be in-memory. The SDK also supports context
providers and compaction paths.

This is a useful implementation distinction: session persistence makes history
durable, but it does not by itself create semantic memory, correct memory
selection, episodic summarization, or long-term knowledge management.

## Prompt / Instructions

`Agent.instructions` can be static or dynamically resolved; `prompt` and output
schemas add other model-facing contracts. The runtime assembles instructions,
session messages, tools, model settings, and context before calling the model.
Dynamic instructions therefore belong to context construction, while the
Runner still owns control flow.

## Model Abstraction

Model interfaces and provider implementations normalize model responses into
assistant output, tool calls, handoffs, and structured output. The runtime can
therefore handle tool execution and transitions without embedding one provider's
wire format in the Agent loop.

## Agent Loop and Stop Condition

The normal stop conditions are:

- a valid final output is produced;
- a configured tool behavior stops after a tool result or named terminal tool;
- a handoff transfers control to another Agent and eventually yields output;
- a guardrail tripwire halts the run;
- an approval/user-input interruption pauses the run; or
- `max_turns` is exceeded.

`tool_use_behavior="run_llm_again"` is the default continuation behavior after
tool calls. This makes stopping an explicit runtime policy rather than an
implicit property of the prompt.

## Error Handling and Reliability

The SDK has input/output guardrails, tool guardrails, approval requests,
timeouts, max-turn bounds, streamed/non-streamed interruption paths, and
structured result/error handling. These do not prove that a diagnosis is true:
they control whether a run may proceed and make failures visible. Domain
verification still requires an independent checker, fresh telemetry, execution
feedback, or human review.

## Planning / Handoff / Multi-Agent

The core SDK does not require an explicit Planner. Handoff is represented as a
tool-like model action which changes the active Agent, optionally filtering
history. This supports specialist delegation and multi-agent workflows, but a
set of Agents is not automatically a principled planner or independent model
ensemble. The actual benefit depends on role boundaries, data sharing, and
decision authority.

## MCP / RAG / Code Execution

- `AgentBase` can expose `mcp_servers`; MCP tools are incorporated into the
  Agent's tool set.
- Retrieval is possible through ordinary tools or integrations; the core
  runtime does not make every tool result a durable memory.
- Code execution is not the definition of the SDK Agent and should be treated
  as a high-risk tool with explicit approval/sandbox policy if added.

## Tracing / Observability

Tracing is a first-class SDK concern. The tracing package and run-loop spans
can associate model turns, tool calls, handoffs, and results with a run. This
is especially valuable for auditing AIOps investigation paths, although a trace
is not the same as evidence provenance or causal verification.

## Reusable Design Patterns

1. **Declarative Agent, imperative Runner:** keep Agent configuration reusable
   and make the runtime responsible for transitions.
2. **Typed next-step state:** represent final output, tool continuation, handoff,
   and interruption as distinct control outcomes.
3. **Approval as a runtime boundary:** defer execution until an explicit policy
   or human decision permits a side-effecting tool.
4. **Handoff as a typed capability:** make delegation model-visible but retain
   a runtime-controlled active-Agent transition.
5. **Session/context-provider separation:** make conversation history and
   contextual augmentation pluggable without conflating them with model state.
6. **Observability around every transition:** trace the runtime, not only the
   final answer.

## Paper / Documentation vs Code Boundaries

The SDK documentation advertises Agents, tools, handoffs, guardrails, sessions,
MCP, and tracing. The source confirms these as runtime components. It does not
claim that every configured Agent has autonomous planning, semantic memory, or
verified domain reasoning; those remain application-level design choices.

## AIOps Relevance

This SDK is a strong reference for a Network RCA runtime after deterministic
front-end processing. Read-only telemetry tools can run normally, while
configuration-change or remediation tools can require approval. Handoffs can
separate observation, diagnosis, and remediation roles, but the diagnosis must
still be grounded in provenance-rich evidence and independently checked.
`max_turns`, tool guardrails, tracing, and interruption/resume are directly
relevant to production incident handling.

## Recommended Files for Further Reading

- `src/agents/agent.py`
- `src/agents/run.py`
- `src/agents/run_internal/run_loop.py`
- `src/agents/run_internal/turn_resolution.py`
- `src/agents/tool.py`
- `src/agents/handoffs/__init__.py`
- `src/agents/guardrail.py`
- `src/agents/memory/session.py`
- `src/agents/tracing/`
- `docs/handoffs.md`, `docs/guardrails.md`, `docs/human_in_the_loop.md`, `docs/tracing.md`

## What I Learned

The main architectural lesson is that an Agent object need not own execution.
The Runner is the runtime that turns model outputs into legal next steps,
executes tools, switches agents, enforces limits, and pauses for approval. This
separation is a useful baseline for safe AIOps agents.

## Open Questions

- Which SDK session/context-provider boundaries are sufficient for evidence provenance?
- How should a high-impact AIOps tool express approval, rollback, and recovery evidence?
- How much of a handoff is genuinely independent reasoning versus role-specific prompt configuration?
