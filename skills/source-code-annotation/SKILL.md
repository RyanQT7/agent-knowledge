---
name: source-code-annotation
description: Create a Chinese teaching annotation of the smallest core source path needed to understand an open-source project, with optional paper-to-code mapping, while leaving the original source untouched.
---

# Source Code Annotation

## Purpose and boundary

Use this Skill when a repository has already been obtained and the goal is to make
its important implementation path easier to learn. It supports two modes:

- **General Source Annotation:** local source or repository → traced execution path,
  Chinese annotated core excerpts, and a reading guide.
- **Paper-Aware Source Annotation:** paper + repository → the same artifacts plus
  evidence-based Paper Concept ↔ Source File ↔ Symbol mapping.

This is a source-learning and teaching transformation, not a code formatter,
refactor, bug fix, reproduction workflow, or repository copier. It is independent
from `paper-reading` and `agent-framework-learning`; it can be called after
`code-reading` or `agent-framework-learning` when an annotated teaching artifact
is useful.

## Source safety and storage

- Treat `sources/` and external checkouts as read-only. Never edit, reformat, or
  repair third-party originals.
- Prefer an existing local checkout. Otherwise use the repository identity supplied
  by `paper-code-discovery` or `agent-framework-learning`, clone only the approved
  public repository, and pin the exact full commit SHA before reading.
- Keep external source under the repository's ignored `sources/code/` convention.
  Do not vendor it, make a submodule, or stage it in the knowledge-base Git history.
- Put derived annotations under `annotations/<project>/<full-commit-sha>/`. A new
  source commit gets a new directory; never overwrite an older annotation.

## Workflow

### 1. Resolve and record identity

Record repository/project name, URL, owner, branch, license, original path, full
commit SHA, and whether the source is a paper implementation. If the source is not
already pinned, resolve the SHA using read-only Git metadata. Do not silently mix
versions.

### 2. Trace before annotating

Read the README/docs only to orient yourself, then follow real callers and callees.
Start from the smallest useful path:

```text
Input / User
→ program entry
→ main class or function
→ main loop / algorithm
→ model, tool, or operation
→ observation / result
→ state or memory update
→ stop / output
```

Also inspect the important error, retry, timeout, and termination branches. For a
large repository, do not enumerate or annotate everything. Choose only files and
symbols that are necessary to explain the path and record omitted areas.

### 3. Produce Chinese teaching annotations

Copy only selected source excerpts or core files into the versioned `annotated/`
directory. Keep the executable source statements unchanged; add Chinese comments,
docstrings, and clearly marked reading separators only. Comments must explain WHY,
WHAT, HOW, and the component's place in the path, including:

- class/function responsibility and caller/callee;
- inputs, outputs, state changes, and important branches;
- model/prompt/tool/observation behavior;
- memory or context updates;
- asynchronous execution, retry, and stopping conditions.

If an excerpt is not independently runnable, label it as a teaching excerpt rather
than presenting it as a replacement module. Preserve the project's license notice
and identify the original file and line range.

### 4. Build required guides

Create the following in the versioned annotation directory:

```text
EXECUTION_PATH.md
CODE_GUIDE.md
SOURCE_MANIFEST.md
```

`EXECUTION_PATH.md` must name the real file, class, and function at every available
stage. `CODE_GUIDE.md` must give a beginner-friendly starting point, reading order,
core symbols, skipped areas, and the final understanding target. `SOURCE_MANIFEST.md`
must include URL, branch, full SHA, license, original/annotated paths, generation
date, annotated files, selection reasons, and whether the source was paper-aware.

### 5. Paper-aware mapping, only when applicable

First ground the paper concept in the existing paper note or the relevant paper
section, then locate its real implementation. Create `PAPER_CODE_MAPPING.md` only
in Paper-Aware mode. Use exactly these mapping types:

```text
DIRECT
STRONG_INFERENCE
POSSIBLE
NOT_FOUND
```

Use a table with `Paper Concept`, `Paper Location`, `Source File`,
`Class / Function`, `Mapping Type`, and `Explanation`. Never fill a row merely to
make the table complete. Explain `Paper says X / Code implements Y` differences.

### 6. Validate and integrate

Check that the original checkout is unchanged, all source paths and symbols exist,
the annotation contains no accidental algorithm/import/control-flow edits, and
the selected code excerpts correspond to the pinned SHA. For suitable complete
Python copies, use compile/AST checks; for teaching excerpts, use exact source
line-range or fingerprint checks and explicitly mark them non-runnable. Do not run
untrusted repository code, install dependencies, download models, call APIs, or
execute tools/remediation.

Add links from annotation guides to the source-learning note or paper note when
available. Update `code/repository-index.md` only with annotation status when that
index is in scope. Update Concepts only for durable cross-project lessons, never
with project-specific code dumps.

## Required artifact shape

```text
annotations/<project>/<full-commit-sha>/
├── annotated/
│   └── <core-file>.py.md
├── EXECUTION_PATH.md
├── CODE_GUIDE.md
├── SOURCE_MANIFEST.md
└── PAPER_CODE_MAPPING.md   # Paper-Aware mode only
```

Use a short project directory only when it is stable and unambiguous. Keep the
full SHA in both the directory and manifest when version traceability matters.

## Quality check and Git

Before reporting completion, inspect the diff and verify:

- the original `sources/` checkout is untouched and still at the recorded SHA;
- annotations are a small, justified core selection, not a repository copy;
- Chinese comments teach execution and design rather than narrating syntax;
- every execution-path claim has a path-level source anchor;
- Paper mappings are conservative and uncertainties are explicit;
- license and provenance are preserved;
- relative Markdown links work and no secrets or external source are staged.

Run:

```bash
git diff --check
git status --short
git diff --stat
git diff
```

For a completed, passing knowledge task, stage knowledge files only and save one
scoped commit, then push `origin main` according to the knowledge-base default. Do
not create an empty commit, force-push, rewrite history, or push external source.
If validation or source identity remains unresolved, leave the incomplete work
uncommitted and report the blocker.
