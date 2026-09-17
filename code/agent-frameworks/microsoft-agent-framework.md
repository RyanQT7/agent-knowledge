# Microsoft Agent Framework — Source Code Learning Notes

Related framework: [microsoft/agent-framework](https://github.com/microsoft/agent-framework)

## Repository Identity

- Repository: `microsoft/agent-framework`
- URL: <https://github.com/microsoft/agent-framework>
- Official status: User-specified upstream project; identity is direct from the requested URL.
- Local path: `sources/code/agent-frameworks/agent-framework`
- Read branch: `main`
- Read at commit: `999dda7970fe969c0901d524365ce34ecbda6227`
- Clone note: shallow clone; the commit is fixed, but local history is intentionally limited.
- License: `LICENSE` is present.
- Analysis mode: Read-only static analysis of the Python core; no dependency installation or code execution.

## Project Purpose and Category

This is a broad, multi-package Agent framework with Python, .NET, and Go
implementations. The Python core combines chat Agents with context providers,
middleware, sessions, tools, MCP, telemetry, and a typed workflow runtime. It
is substantially larger than the focused examples above, so this note follows
the core Python path rather than claiming complete repository coverage.

## What the Repository Implements

The Python core under `python/packages/core/agent_framework/` provides:

- `BaseAgent`, `RawAgent`, and `Agent` abstractions;
- provider-backed chat clients and normalized message/response types;
- function tools with schema validation, parsing, middleware, approval/security hooks;
- sessions and context/history providers;
- MCP client/tool adapters;
- a workflow graph with Executors, edges, routing, events, checkpoints, and a runner;
- telemetry/observability and integrations in separate packages.

The framework therefore has two related control surfaces: an Agent run delegates
to a chat client and tool-capable model, while a Workflow composes Agents and
Executors into a typed event-driven graph.

## Core Source Map

| Concept | File | Class/Function | Purpose |
|---|---|---|---|
| Agent base | `python/packages/core/agent_framework/_agents.py` | `BaseAgent`, `RawAgent`, `Agent` | Agent identity, client, tools, providers, middleware, and `run()` API. |
| Agent entry | `_agents.py` | `RawAgent.run()` / `Agent.run()` | Prepares session/context and calls the chat client. |
| Tool | `_tools.py` | `FunctionTool`, `FunctionTool.invoke()` | Validates arguments, invokes callable, parses result into `Content`. |
| Session | `_sessions.py` | `AgentSession`, `SessionStore` | Holds IDs and mutable provider-scoped state; can be serialized/stored. |
| Context provider | `_sessions.py` | `ContextProvider`, `HistoryProvider` | Adds context before a run and persists/updates after a run. |
| Workflow builder | `_workflows/_workflow_builder.py` | `WorkflowBuilder` | Connects Executors/Agents, sets outputs, iterations, and checkpoints. |
| Workflow | `_workflows/_workflow.py` | `Workflow`, `Workflow.run()` | Runs a compiled executor graph and returns events/results. |
| Executor | `_workflows/_executor.py` | `Executor` | Typed node with handler(s) in a workflow. |
| Workflow context | `_workflows/_workflow_context.py` | `WorkflowContext` | Sends messages, yields output, requests input, and accesses workflow state. |
| Workflow state | `_workflows/_state.py` | `State` | Base state abstraction for workflow components. |
| Checkpoint | `_workflows/_checkpoint.py` | `CheckpointStorage`, `FileCheckpointStorage` | Persists workflow execution state when configured. |
| MCP | `_mcp.py` | `MCPTool` | Discovers/calls remote MCP tools and normalizes their results. |
| Telemetry | `_telemetry.py`, `observability.py` | feature marks/spans | Framework feature and workflow/agent observability. |

## Agent Execution Path

The simple Agent path is:

```text
user messages
  → Agent.run()
  → RawAgent._prepare_run_context()
  → session/history/context providers before_run
  → normalize tools and build chat options
  → BaseChatClient.get_response()
  → provider returns assistant text, structured output, or tool calls
  → response parsed into AgentResponse
  → session/context providers after_run
  → return or stream result
```

The inspected `_agents.py` path is an Agent/client boundary. Tool-loop behavior
can be provided by the selected chat client and its function-invocation options,
or by placing an Agent inside a Workflow. It should not be described as a
single hard-coded ReAct `while` loop without tracing the provider/client path.

The workflow path is:

```text
WorkflowBuilder(start_executor=...)
  → add Executor/Agent nodes and edges
  → build Workflow
  → Workflow.run(input)
  → RunnerImpl schedules edge runners and executor handlers
  → executor sends messages / yields output / requests input
  → routed successors execute
  → events and final state returned
```

## Tool Calling

`FunctionTool` derives or accepts an input model/schema, validates arguments,
invokes sync or async Python functions, and normalizes the result to `Content`
unless raw parsing is explicitly requested. Middleware can inspect or alter
invocation context; approval/security providers can prevent unsafe execution.

`Agent` also accepts MCP servers. `MCPTool` discovers remote tools, creates
local callable wrappers, forwards structured arguments, captures result
metadata, and converts text/media/resource/tool results into framework content.
This is a concrete example of an external protocol becoming a local tool
surface; it is not memory by itself.

## Memory / State

`AgentSession` is a lightweight state container with a session ID, optional
service-managed conversation ID, and mutable provider state. `HistoryProvider`
and other `ContextProvider`s decide how messages or external context are
assembled and persisted. `SessionStore` copies sessions in memory; callers can
provide durable backends.

Workflows add another state layer: Executors communicate through typed events,
workflow context, and optional checkpoint storage. This is more explicit than
plain prompt history, but static source reading does not establish that every
stored value is useful semantic memory. Persistence, retrieval policy, and
forgetting remain application concerns.

## Prompt / Instructions

Instructions are appended/normalized in run-context preparation and passed to
the client together with session messages, tools, and chat options. Context
providers can inject additional information before the model call. This makes
context assembly a middleware/provider pipeline rather than one fixed prompt
template.

## Model Abstraction

`BaseChatClient` and provider-specific clients isolate model request/response
formats. The Agent prepares a `ChatOptions`/tool context and delegates the
actual model call to `get_response()`. The framework can therefore host agents
using different model providers while retaining shared tools, sessions, and
workflow integration.

## Agent Loop and Stop Condition

At the Agent layer, the core source exposes one `run()` boundary and relies on
the chat client/function invocation path for the model response and any tool
continuation semantics. At the Workflow layer, control is explicit:

- `WorkflowBuilder` validates a connected graph;
- `max_iterations` bounds convergence;
- edge runners schedule successors, fan-out, fan-in, or switch cases;
- a workflow becomes idle, completes, errors, or waits for request information;
- optional checkpoints enable resumption.

This is a key design difference from a minimal while-loop: the framework can
represent multi-node orchestration, typed events, pauses, and resumption.

## Error Handling and Reliability

Tool argument/schema validation, middleware, security providers, MCP error
parsing, workflow graph validation, max iterations, cancellation, status/error
events, and checkpointing are explicit framework concerns. The presence of
these controls does not make an RCA correct; an AIOps application still needs
domain-specific candidate validation, evidence provenance, recovery checks,
and human policy for high-impact actions.

## Planning / Handoff / Multi-Agent

The workflow package supports composing Agents and Executors, edges, fan-out,
fan-in, switch cases, sub-workflows, request information, and orchestration
packages. This provides a runtime substrate for planner/worker or multi-agent
designs, but a graph or multiple executors is not automatically dynamic
planning. The selected edges and handlers define the actual control policy.

## MCP / RAG / Code Execution

- MCP is implemented as a first-class remote tool adapter in `_mcp.py`.
- Context providers and optional vector/integration packages can support
  retrieval, but retrieval is not automatically Agent memory.
- The core framework has filesystem/sandbox-related modules and integrations,
  but this static pass did not verify a single canonical code-execution path;
  treat it as `Unclear / not traced in this note` rather than infer it.

## Tracing / Observability

Agent and workflow code imports telemetry/observability helpers, emits feature
usage and workflow spans/events, and includes status timelines in
`WorkflowRunResult`. The framework is oriented toward inspectable execution,
but application-level evidence provenance must still be designed explicitly.

## Reusable Design Patterns

1. **Agent/client separation:** an Agent prepares context and capabilities;
   provider clients own model protocol details.
2. **Provider pipeline:** context and history providers create a controlled
   before/after boundary for context injection and persistence.
3. **Typed workflow graph:** Executors, edges, events, and validation make
   orchestration explicit and resumable.
4. **Checkpointed execution:** a workflow can persist control state without
   pretending that all state is semantic memory.
5. **Protocol-to-tool adapter:** MCP discovery/results become local typed tools
   while preserving metadata and telemetry hooks.
6. **Security at invocation:** schema validation, middleware, approval, and
   security state are close to the side-effect boundary.

## Paper / Documentation vs Code Boundaries

The framework's scale and documentation expose many integrations, but this note
only claims paths observed in the Python core. `Agent.run()` is real; the exact
model-side tool loop can vary by client/options. `Workflow` is a real event and
edge runtime; it should not be reduced to “an Agent prompt” or inflated into a
universal autonomous planner.

## AIOps Relevance

Microsoft Agent Framework is a useful reference for the control plane around a
Network RCA Agent: typed tools, provider-injected evidence context, workflow
nodes, checkpoints, request-for-human-input, MCP adapters, events, and bounded
iterations. A design can keep detection and candidate construction
deterministic, put bounded investigation in an Agent/Workflow node, and require
approval plus recovery evidence before side-effecting tools run.

## Recommended Files for Further Reading

- `python/packages/core/agent_framework/_agents.py`
- `python/packages/core/agent_framework/_tools.py`
- `python/packages/core/agent_framework/_sessions.py`
- `python/packages/core/agent_framework/_mcp.py`
- `python/packages/core/agent_framework/_workflows/_workflow_builder.py`
- `python/packages/core/agent_framework/_workflows/_workflow.py`
- `python/packages/core/agent_framework/_workflows/_runner.py`
- `python/packages/core/agent_framework/_workflows/_executor.py`
- `python/packages/core/agent_framework/_workflows/_checkpoint.py`
- `python/samples/`

## What I Learned

The framework separates three concerns that are often collapsed in diagrams:
the Agent-facing chat invocation, the provider/session context boundary, and
the workflow execution runtime. That separation is valuable for production
systems because it lets a workflow pause, validate, checkpoint, and resume
without making the LLM the sole owner of control state.

## Open Questions

- Which chat clients own automatic function invocation, and where should an application put a domain-specific tool loop?
- How should workflow checkpoints distinguish control state from evidence and semantic memory?
- What is the smallest Microsoft workflow configuration that supports a safe, human-gated Network RCA action?
