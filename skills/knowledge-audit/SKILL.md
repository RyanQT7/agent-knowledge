---
name: knowledge-audit
description: Audit Markdown knowledge structure deterministically and review a bounded set of claims semantically for missing evidence, stale conclusions, conflicts, scope differences, and paper-code mismatches; always read-only.
metadata:
  short-description: Read-only knowledge integrity audit
---

# Knowledge Audit

## Purpose and boundaries

Find problems and produce traceable findings. Do not delete, rewrite, approve, or merge core knowledge. Distinguish deterministic checks from semantic judgements. A low-confidence semantic match is `needs_review`, not a fact.

## Deterministic audit

Run:

```bash
python3 -m scripts.evolution.audit --json
```

The script checks internal Markdown links, direct INDEX links for papers/Concepts, duplicate paper identities, short/placeholder paper notes, orphan Concepts, code-note repository/SHA fields, Claim schema and relation consistency, stale source versions when a newer version event is present, duplicate candidate/claim IDs, pending candidates, and open Questions. It scans Markdown and JSONL only; it does not execute source code or call an LLM.

Review `evolution/audits/<RUN_ID>.md` and `.json`. Confirm low-severity findings in context. Indexes may intentionally group detailed files, so a missing direct link is a suggestion, not an instruction to add noise.

## Bounded semantic review

Read no more than 10 relevant pages by default. Select using explicit links, the current candidate, source note, affected Concepts/Reviews, and Questions. Prefer 3–5 directly related pages; expand only when evidence requires it. Do not provide the whole vault to the model.

For each candidate, compare the paper/source evidence to existing claims and record:

```text
Finding:
Affected file:
Affected claim:
Evidence:
Issue type:
Impact:
Confidence:
Suggested action:
```

Issue types include `missing_evidence`, `potential_conflict`, `scope_difference`, `version_difference`, `stale_claim`, `paper_code_mismatch`, `unresolved_question`, `teaching_mismatch`, and `no_update_needed`.

For possible conflicts, compare definitions, scope, datasets, assumptions, methods, versions, and outcome measures. Distinguish a direct contradiction from a paper that narrows a previous claim. A newer publication date does not by itself invalidate earlier evidence. Do not infer a causal or universal claim from a benchmark-specific result.

For paper/code checks, use existing `paper-code-discovery` then `code-reading` with a pinned SHA. Compare the paper claim to the actual symbols and data path. Static source analysis only; never execute third-party code.

An `active` Claim needs source version, URI, locator, access date, and a declared relation. A semantic similarity hit is only a retrieval hint. `supports`, `qualifies`, `contradicts`, `supersedes`, and `related_to` mean different evidence relationships.

## Output and handoff

Save semantic findings as `evolution/audits/<RUN_ID>-semantic.md` and update the run manifest. If a finding is material, create a proposal through `knowledge-evolution`; never edit the affected core file from this audit. Preserve uncertainty and historical Questions.

If there is no worthwhile change, record `no_update_needed` and explain why. Normal completion with no proposal is valid.
