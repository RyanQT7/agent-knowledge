# smolagents — Source Code Learning Notes

Related framework: [Hugging Face smolagents](https://github.com/huggingface/smolagents)

## Repository Identity

- Repository: `huggingface/smolagents`
- URL: <https://github.com/huggingface/smolagents>
- Official status: User-specified upstream project; repository identity is direct from the requested URL.
- Local path: `sources/code/agent-frameworks/smolagents`
- Read branch: `main`
- Read at commit: `30bb1161095dbae2271e6bc3cc4c219cc3897a57`
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis; no dependency installation or code execution.

## Project Purpose and Category

smolagents is a relatively small Python framework for building tool-using
agents. Its central abstraction is a `MultiStepAgent`; `ToolCallingAgent`
represents structured tool calls, while `CodeAgent` represents code-as-action.
The project is useful for learning a complete Agent loop because the model,
memory, action step, tool execution, observation, and stop condition are all
visible in one package.

## What the Repository Implements

The core implementation is in `src/smolagents/`. The repository supports:

- model adapters through `models.py`;
- typed or schema-described `Tool` objects;
- a shared multi-step runtime;
- function-style tool calls in `ToolCallingAgent`;
- Python code as an action in `CodeAgent`;
- optional planning steps and managed sub-agents;
- MCP and remote executor adapters.

It is a framework runtime, not just a prompt collection.

## Core Source Map

| Concept | File | Class/Function | Purpose |
|---|---|---|---|
| Agent base | `src/smolagents/agents.py` | `MultiStepAgent` | Owns model, tools, state, memory, step counter, and shared run loop. |
| Entry point | `src/smolagents/agents.py` | `MultiStepAgent.run()` | Initializes task/state/memory and consumes the execution stream. |
| Loop | `src/smolagents/agents.py` | `MultiStepAgent._run_stream()` | Repeats planning and action steps until final answer or `max_steps`. |
| Per-step specialization | `src/smolagents/agents.py` | `MultiStepAgent._step_stream()` | Subclasses translate model output into an action. |
| Tool-calling agent | `src/smolagents/agents.py` | `ToolCallingAgent._step_stream()` | Requests model tool calls and processes them. |
| Tool execution | `src/smolagents/agents.py` | `process_tool_calls()`, `execute_tool_call()` | Validates and invokes tools, records observations and errors. |
| Code agent | `src/smolagents/agents.py` | `CodeAgent._step_stream()` | Parses model-generated code and sends it to an executor. |
| Runtime memory | `src/smolagents/memory.py` | `AgentMemory` | Stores `TaskStep`, `PlanningStep`, `ActionStep`, and final answer steps. |
| Step serialization | `src/smolagents/memory.py` | `ActionStep.to_messages()` | Converts action/observation history into future model messages. |
| Tool schema | `src/smolagents/tools.py` | `Tool` | Defines name, description, inputs, output type, validation, and invocation. |
| Model abstraction | `src/smolagents/models.py` | `Model.generate()` | Common interface for model generation and tool-call parsing. |
| Tool prompt | `src/smolagents/prompts/toolcalling_agent.yaml` | system prompt | Defines tool-call, observation, and final-answer protocol. |
| Code prompt | `src/smolagents/prompts/code_agent.yaml` | system prompt | Defines Thought → Code → Observation behavior. |

## Agent Execution Path

The main static path is:

```text
user task
  → MultiStepAgent.run()
  → TaskStep and initial memory
  → _run_stream()
  → optional _generate_planning_step()
  → ToolCallingAgent._step_stream()
  → model.generate(..., tools_to_call_from=...)
  → parse tool calls
  → execute_tool_call()
  → tool result / error becomes observation
  → ActionStep is appended to AgentMemory
  → ActionStep.to_messages() exposes history to the next model call
  → another step or final_answer
```

`_run_stream()` continues while there is no final answer and
`step_number <= max_steps`. The default `max_steps` is 20, and exceeding it
is handled explicitly rather than becoming an unbounded loop.

For `CodeAgent`, the action branch is:

```text
model.generate()
  → parse code blob
  → synthetic python_interpreter ToolCall
  → LocalPythonExecutor / remote executor
  → logs and output become observation
  → next code step or final_answer
```

## Tool Calling

`Tool` is a runtime object with a name, description, input schema, output type,
validation, and callable implementation. `ToolCallingAgent` asks the model for
one or more calls, checks names and arguments, invokes them (the implementation
can use a thread pool for multiple calls), and records the returned value or
error as a model-visible observation.

The tool prompt treats a tool result as `Observation:` and reserves
`final_answer` as the terminal action. This is structured at the Python
boundary, although the model-facing protocol is still prompt/tool-call based;
it is not evidence of a universal semantic validation layer.

## Memory / State

`AgentMemory.steps` is an ordered in-process trajectory. It includes task,
planning, action, observations, tool calls, errors, code logs, and token usage.
`write_memory_to_messages()` serializes it for model context. The constructor
also exposes a mutable `state` dictionary for runtime values and executor
sharing.

This is strong task-local working context. It is not automatically persistent,
semantic, or cross-session memory. A caller would need to persist and select
state outside this loop to obtain durable memory behavior.

## Prompt / Instructions

The YAML prompts define the behavioral contract: use available tools, treat
tool output as observation, repeat until enough evidence is available, and use
`final_answer` to terminate. The instructions are a protocol boundary, not a
separate planning engine. `PlanningStep` is optional and is controlled by
`planning_interval`.

## Model Abstraction

`src/smolagents/models.py:Model` exposes `generate()` and tool-call parsing.
Concrete adapters cover several model providers. The Agent runtime does not
need to know provider-specific request details; it receives model output and
turns it into an action or tool call.

## Agent Loop and Stop Condition

The loop is a bounded while-loop in `_run_stream()`. It stops when:

- a step produces a final answer;
- a final-answer call is handled;
- an error handler terminates the run; or
- `max_steps` is reached.

Optional planning steps occur at configured intervals. This makes planning an
extension of the loop rather than a mandatory independent `Planner` object.

## Error Handling and Reliability

Tool-name and argument validation happen before execution. Tool exceptions are
captured into agent errors and can be surfaced to the model for another step.
The step budget is a basic reliability boundary. The code also has final-answer
checks, monitoring, token accounting, and executor abstractions. Static reading
does not show that every external tool is safe, idempotent, or independently
verified.

## Planning / Handoff / Multi-Agent

`_generate_planning_step()` can produce a plan-like language step at intervals.
Managed agents are exposed through the same tool surface, so delegation is
represented as a callable capability rather than a separate universal
multi-agent protocol. The inspected core does not require a Planner–Executor
architecture or dynamic replanning beyond the next model step.

## MCP / RAG / Code Execution

- `ToolCollection` can load tools from Hub or MCP adapters; MCP is an external
  tool-connection mechanism, not Agent memory.
- No general RAG memory architecture is required by the core loop.
- `CodeAgent` uses code-as-action and `LocalPythonExecutor` or remote executor
  adapters. That executor boundary is materially different from ordinary
  read-only function tools and deserves stronger sandboxing in production.

## Tracing / Observability

`monitoring.py`, the logger, step records, token accounting, and executor
interfaces provide observability hooks. The trajectory itself makes the
runtime inspectable, but static code inspection does not establish a complete
distributed tracing or audit system for arbitrary tools.

## Reusable Design Patterns

1. **Shared loop, specialized step:** keep lifecycle and budget in
   `MultiStepAgent`, and let subclasses decide how model output becomes an
   action.
2. **Explicit trajectory objects:** retain structured step data first, then
   serialize it into model messages.
3. **Schema at the tool boundary:** validate name and arguments before running
   a callable.
4. **Code-as-action:** make generated code an explicit action with an executor
   and observation, rather than silently executing arbitrary text.
5. **Bounded continuation:** `max_steps`, final-answer checks, and error paths
   prevent a model from owning an infinite loop.

## Paper / Documentation vs Code Boundaries

No paper is required for this framework-learning task. The project README and
prompt names describe a tool-using Agent, but the durable implementation facts
come from `agents.py`, `memory.py`, `tools.py`, and `models.py`. Calling the
`AgentMemory` object “long-term memory” would overstate what the code shows.

## AIOps Relevance

smolagents is a useful prototype model for a bounded Network RCA loop:
deterministic metric/log/topology tools can be exposed as typed tools, while
the Agent handles bounded evidence selection and synthesis. AIOps should keep
candidate enumeration, time/entity alignment, permissions, and verification
outside unconstrained code generation. `CodeAgent` is a useful warning: code
execution expands action power and therefore needs a stricter sandbox and
human gate than read-only telemetry tools.

## Recommended Files for Further Reading

- `src/smolagents/agents.py`
- `src/smolagents/memory.py`
- `src/smolagents/tools.py`
- `src/smolagents/models.py`
- `src/smolagents/prompts/toolcalling_agent.yaml`
- `src/smolagents/prompts/code_agent.yaml`
- `src/smolagents/local_python_executor.py`
- `src/smolagents/mcp_client.py`

## What I Learned

The smallest complete Agent is not just an LLM plus a prompt. It needs a
bounded loop, an action representation, an executor, an observation channel,
and a way to reinsert the trajectory into the next model call. smolagents
makes those boundaries explicit while still keeping the architecture small.

## Open Questions

- Which parts of `AgentMemory` should be retained or summarized for long AIOps incidents?
- How should tool results carry entity, timestamp, provenance, and confidence metadata?
- When should a planning step be trusted, and when should deterministic candidate constraints override it?
