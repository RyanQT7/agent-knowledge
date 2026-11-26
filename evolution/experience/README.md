# Experience Memory

`records.jsonl` stores compact, redacted experiences about task execution and user feedback. It is separate from research Claims: experience can guide how a future task is carried out, but cannot serve as factual evidence for that task. `index.json` is a small derived count/ID index.

Retrieval matches English terms and Chinese character bigrams, returns only a small bounded set, and prioritizes global persistent user preferences. Ordinary searches omit Controller-specific and Evolution Engine runtime experiences; the Engine opts in to those records for its own roles. Retrieval updates use counts. New user feedback can be task-scoped or marked `persistent` only when the user explicitly requests a long-term preference. Records can be marked `needs_review`, `superseded`, or `rejected` when their applicability changes.

Do not store full chat history, full model output, credentials, personal data, or source-document bodies. Keep short `evidence_refs` to run reports, explicit user feedback, or versioned code. Duplicate lessons merge and retain source references.

Commands are documented in `skills/experience-memory/SKILL.md`; the six known Phase 1.5 experiences can be imported idempotently with:

```bash
python3 scripts/evolution/experience.py import-history
```

To explicitly include Engine/controller troubleshooting records in a manual search, add `--include-engine`. Ordinary paper-reading searches should leave that flag off.
