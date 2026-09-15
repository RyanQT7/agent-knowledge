# paper-code-discovery

## Purpose

Find and verify the repository associated with an already-read paper, distinguishing official implementations from author-endorsed, third-party, and merely related projects.

## When to use

Use it after a paper has a grounded note and you want to locate its implementation. It can handle one paper or a defined set of completed paper notes.

## Main output

- Repository classification and evidence.
- Metadata in code/repository-index.md.
- Optional read-only checkout under sources/code/, pinned to a full commit SHA.

GitHub MCP search is preferred when available. If no reliable implementation is found, record No Repository Found rather than guessing.

## Safety

Cloned source stays under the ignored sources/code/ directory. Do not install dependencies, run repository code, expose credentials, create submodules, or commit external source.
