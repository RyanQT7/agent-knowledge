---
name: paper-reading
description: Read one local academic paper PDF and integrate its grounded findings into this Markdown knowledge base, including paper notes, Concepts, cross-references, questions, learning log, INDEX, and Git checks. Use for single-paper reading tasks, not generic PDF extraction or bulk literature processing.
---

# Paper Reading

## Purpose

Use this skill when the user asks Codex to read one academic paper PDF and add durable knowledge to the current Markdown knowledge base. The desired result is understanding and knowledge integration, not an abstract-only summary or a PDF conversion.

The normal flow is:

```text
Locate source
→ Read the full paper
→ Write a grounded paper note
→ Update only useful cross-paper Concepts
→ Add meaningful cross-references
→ Record open questions
→ Update the learning log and INDEX
→ Run quality and Git checks
→ Commit and push the completed knowledge task when all checks pass
```

Work inside the current knowledge-base root. Do not read a second paper, download unrelated material, install dependencies, build RAG/vector infrastructure, or implement an Agent/Skill unless the user separately requests it.

## Input and source location

Accept either a direct PDF path or a request that names one PDF, for example:

```text
阅读 sources/papers/react.pdf
阅读这篇论文：sources/papers/xxx.pdf
```

1. Resolve an explicitly provided path first.
2. If it does not exist, search only the knowledge-base root and its likely paper locations (`sources/papers/`, `papers/`) for a same-name or clearly corresponding PDF. Ignore case and minor filename differences when there is one obvious match. Do not scan unrelated directories.
3. If there is no clear source, report the ambiguity or missing input as `NEEDS REVIEW`; do not invent a paper or use unsupported memory.

Keep the original PDF under:

```text
sources/papers/<paper-file>.pdf
```

Keep reading notes under:

```text
papers/<paper-id>/notes.md
```

Use a short, stable, lowercase `<paper-id>`, preferably the commonly used paper abbreviation (`react`, `reflexion`, etc.). Never leave the original PDF in the root of `papers/`. If a supplied PDF is inside this knowledge base but outside `sources/papers/`, move it into the source directory only when the correspondence is clear; preserve any original outside the knowledge base and never delete it. Record the final source path in the note.

The `Local File` link in a note at `papers/<paper-id>/notes.md` should resolve to:

```text
../../sources/papers/<paper-file>.pdf
```

Ensure source PDFs are ignored by focused rules such as:

```gitignore
sources/papers/*.pdf
sources/papers/**/*.pdf
```

Do not use a broad `*.pdf` rule. Do not stage, commit, or push the original PDF.

## Full-paper reading

Read as much of the complete PDF as the available local tools allow. Do not generate the note from only the Abstract, Introduction, or Conclusion. Inspect, when present:

- Method, architecture, algorithms, and workflow.
- Experiments, benchmarks, baselines, metrics, tables, and figures.
- Appendix details, prompts, examples, trajectories, ablations, and implementation settings that materially affect understanding.

Use available local PDF text extraction or rendering tools. If a preferred utility is unavailable, use another available local method; do not install packages just to complete the ordinary workflow. Do not print the full extracted paper or the completed note to the terminal.

While reading, maintain a small evidence map of claims to `Sec.`, `Fig.`, `Table`, or `Appendix` locations. Pay particular attention to:

```text
Problem
Motivation
Core idea
Architecture / workflow
Component interactions
Experimental design
What the results support
What the paper does not establish
Author-stated limitations
```

## Paper note

Use [the paper-note template](../../templates/paper-note.md) as the structural basis. Never modify the template itself. Create or update only:

```text
papers/<paper-id>/notes.md
```

The note must explain the paper in your own words rather than reproduce a section-by-section abstract. It must answer:

- What problem is being solved, and why are existing approaches insufficient?
- What is the central idea and how does the complete workflow run?
- How do the important components interact?
- What do the experiments actually demonstrate?
- What remains unproven or unclear?
- Why does the paper matter for the knowledge base?

For agentic or interactive papers, make the loop explicit when applicable:

```text
Task → Thought / Reasoning → Action → Observation → Thought → ... → Final Answer
```

Explain the role of each step, especially how observations or external feedback affect later reasoning and action. Do not assume that every paper has a Planner, Executor, Memory, Environment, or Tool module; name only components the paper defines or clearly implements.

## Evidence and interpretation boundaries

Ground key facts directly in the paper. Add source markers near important methods, numbers, conclusions, and limitations:

```text
Source: Sec. 3
Source: Table 2
Source: Fig. 1
Source: Appendix B.1
```

Never fill missing experimental values from model memory. Use this exact marker when necessary:

```text
Unclear / Not explicitly stated in the paper
```

Keep two layers separate:

```text
Paper states / Paper observes
My interpretation / Further question
```

Be especially cautious with these common overinterpretations:

- A generated reasoning trace is an explicit language trace, not automatically the model's true hidden internal state.
- Decomposition or plan-like behavior is not automatically an explicit Planner architecture.
- History kept in a trajectory or context is not automatically persistent, long-term, or external Memory.
- Tool/API interaction is not automatically RAG, structured function calling, or MCP.
- Interpretability claims should be attributed to the paper and bounded by what it actually evaluates.

## Concept integration

After writing the paper note, inspect the existing `concepts/` files and decide whether the paper adds durable, cross-paper knowledge.

Keep in Concepts:

- General mechanisms that remain meaningful beyond this paper.
- Reusable distinctions, trade-offs, interfaces, or failure patterns.
- A concise explanation of what this paper adds to the concept.

Keep in the paper note instead:

- Per-paper benchmark details, table numbers, prompt text, and experiment-specific scores.
- A paper abstract or detailed experiment narrative.
- Claims that apply only to this paper's implementation or dataset.

Do not edit a Concept merely to show that the skill ran. It is valid to leave Concepts unchanged. If a genuinely important new concept is missing, create it from [the concept template](../../templates/concept-note.md), retain `Status: evolving` at the top, and explain why the new file is warranted.

When a Concept is updated, preserve its general definition and make the paper's contribution explicit without turning the file into a ReAct-specific summary. Add the paper under `Representative Papers` or another appropriate section.

## Cross-references

Link only concepts that are materially used by the paper. From `papers/<paper-id>/notes.md`, use paths of the form:

```markdown
[Concept](../../concepts/concept-file.md)
```

From a Concept file, link back to:

```markdown
[Paper](../papers/<paper-id>/notes.md)
```

Check that the links resolve. Do not link every concept or add a link solely to create a graph-like appearance.

## Questions, log, and index

Update `notes/questions.md` only with questions that can plausibly be answered by a later paper, code reading, experiment, or official documentation. Keep separate headings for:

- Questions the paper leaves unresolved or identifies as limitations.
- Further questions generated by the knowledge-base author's interpretation.

Merge duplicates and avoid vague reactions.

Add one short entry to `notes/learning-log.md` with exactly the useful fields:

```text
Date
Paper
Core takeaway
New concepts
Open questions
Next step
```

Do not copy the paper note into the log. Add one concise entry to the `Papers` section of `INDEX.md` linking to `papers/<paper-id>/notes.md`; keep the index simple.

## Completion checks

Before handing off, inspect the resulting files and correct problems directly. Check:

1. The source PDF is under `sources/papers/` and no PDF remains in the root of `papers/`.
2. `Local File` and other paper-path references resolve to the final source location.
3. The paper note follows the template without changing the template and covers method, workflow, experiments, limitations, and personal understanding.
4. Important numbers, benchmarks, baselines, metrics, and claims have `Sec.`, `Table`, `Fig.`, or `Appendix` grounding; unknown details are marked explicitly.
5. Paper facts and personal interpretation are visibly distinct.
6. Concept edits are cross-paper and concise; relevant paper-to-concept and concept-to-paper links work.
7. Open questions are non-duplicative and actionable.
8. The learning log is brief and the INDEX points to the paper note.
9. Source PDFs match the focused `.gitignore` rule and are not tracked.

Run these self-checks from the knowledge-base root:

```bash
git status --short
git diff --stat
git diff
```

Also inspect a concise file list when useful:

```bash
find papers sources/papers -maxdepth 2 -type f | sort
```

The diff is for self-checking only; follow the Git commit behavior below after all checks pass. Do not dump the complete paper note in the user-facing response.

## Git commit and push behavior

After the paper note, Concept updates, cross-links, questions, learning log, INDEX, and source-grounding checks all pass, save and synchronize the completed knowledge task automatically:

1. Run `git diff --check` before staging.
2. Run `git add .`.
3. Create a concise, paper-specific commit, for example:

   ```text
   Add Reflexion paper notes and memory concepts
   Add Toolformer paper notes and related concepts
   ```

4. Confirm the current branch is `main` and `origin` points to the configured knowledge-base repository.
5. Run `git push origin main`.
6. Run `git status` and confirm the commit and push result.

Do not create an empty commit when there are no actual changes. Do not force push, rewrite history, or push to an unexpected remote. Do not commit or push when the task failed, Source Grounding is `NEEDS REVIEW`, the knowledge base has an unresolved conflict, GitHub authentication or remote checks fail before synchronization, or the user explicitly asked not to commit or push. If a local commit has already been created and the push fails, preserve the commit and report the synchronization failure. The source PDF must remain governed by the focused `.gitignore` rules and must not be staged.

## User-facing completion format

After one paper is processed, report only a concise handoff in this shape:

```text
Paper:
Reading status:

Created:
Modified:

Core contribution:

Concepts updated:

Main open questions:

Source grounding:
PASS / NEEDS REVIEW

Knowledge integration:
PASS / NEEDS REVIEW

Git status:
```
