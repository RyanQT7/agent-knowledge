# Source Manifest

## Repository

- Repository: `huggingface/smolagents`
- URL: <https://github.com/huggingface/smolagents>
- Owner / organization: `huggingface`
- Branch read: `main`
- Commit read: `30bb1161095dbae2271e6bc3cc4c219cc3897a57`
- License: Apache License 2.0 (`sources/code/agent-frameworks/smolagents/LICENSE`)
- Generated date: `2026-09-17`
- Mode: General Source Annotation
- Paper-aware mapping: Not generated; this validation targets the independent framework repository, not a selected paper implementation.

## Paths

- Original path: `sources/code/agent-frameworks/smolagents/`
- Annotated path: `annotations/smolagents/30bb1161095dbae2271e6bc3cc4c219cc3897a57/`
- Existing source-learning note: [`code/agent-frameworks/smolagents.md`](../../../code/agent-frameworks/smolagents.md)

## Annotated files

- [`annotated/agents.py.md`](annotated/agents.py.md) — selected excerpts from `src/smolagents/agents.py`, covering `run`, `_run_stream`, context serialization, `ToolCallingAgent`, tool dispatch, and `CodeAgent` action execution.
- [`annotated/memory-and-tools.py.md`](annotated/memory-and-tools.py.md) — selected excerpts from `src/smolagents/memory.py` and `src/smolagents/tools.py`, covering action-to-message conversion, `AgentMemory`, and `Tool` declaration/validation.

## Selection reasons

The files were selected because they are the smallest useful set for tracing:

```text
task entry → bounded runtime loop → model decision → tool execution
→ observation → memory/context feedback → final answer
```

Provider adapters, UI/monitoring code, remote executor details, and unrelated
utilities were intentionally omitted. `CodeAgent` is included only at the action
boundary to compare function-style tool calls with code-as-action.

## Provenance and safety

- The external checkout remains under ignored `sources/code/`; it is not copied into Git history.
- The original checkout was not edited. The annotation artifacts add teaching comments around selected source statements and preserve the original line ranges in their headings.
- The annotation files are deliberately marked as excerpts and should not be imported as replacement modules.
- No dependency installation, model download, repository execution, benchmark run, or executor/remediation action was performed.
