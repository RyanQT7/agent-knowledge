# code-reading

## Purpose

Read a pinned paper repository or independent Agent framework as static evidence and explain its real implementation, including entry points, data flow, prompts, tools, algorithms, evaluation, and paper/documentation–code differences.

## When to use

Use after [paper-code-discovery](../paper-code-discovery/SKILL.md), or after an explicit framework URL has been verified and pinned to a full commit SHA.

## Output

- Agent/LLM notes: code/<paper-id>/notes.md
- AIOps notes: code/aiops/<paper-id>/notes.md
- Framework notes: code/agent-frameworks/<framework-id>.md
- Relative Paper ↔ Code or Framework ↔ Code links.
- Updated code/repository-index.md.

## Safety

READ-ONLY STATIC ANALYSIS. Do not run repository code, install dependencies, download models, call cloud APIs, execute remediation, or commit external source. Commit only the resulting Markdown knowledge.
