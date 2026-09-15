# code-reading

## Purpose

Read a pinned paper repository as static evidence and explain how the paper’s method is implemented, including entry points, data flow, prompts, tools, algorithms, evaluation, and paper–code differences.

## When to use

Use after [paper-code-discovery](../paper-code-discovery/SKILL.md) has established a trustworthy repository identity and full commit SHA.

## Output

- Agent/LLM notes: code/<paper-id>/notes.md
- AIOps notes: code/aiops/<paper-id>/notes.md
- Relative Paper ↔ Code links.
- Updated code/repository-index.md.

## Safety

READ-ONLY STATIC ANALYSIS. Do not run repository code, install dependencies, download models, call cloud APIs, execute remediation, or commit external source. Commit only the resulting Markdown knowledge.
