---
name: experience-memory
description: Record, retrieve, and maintain concise reusable task experience and user feedback for this knowledge base without storing full conversations or treating past experience as current evidence.
metadata:
  short-description: Reuse task experience across work
---

# Experience Memory

Use the compact Experience Memory at `evolution/experience/records.jsonl`. Experiences describe how work went; they are not research Claims and cannot prove a current paper fact.

## Record useful experience

Use this Skill when a user asks to record feedback, or when a completed task contains a reusable method, repeated failure, a resolved Controller defect, an evidence gap, or a durable user preference. Do not record routine successful operations, full chat logs, credentials, personal data, entire model outputs, or paper text. Keep evidence references short and redacted.

Record a feedback message:

```bash
python3 scripts/evolution/experience.py add \
  --type user_feedback --task-type teaching --skill source-code-annotation \
  --message "Explain the real execution path with a concrete paper example."
```

Use `--persistent` only when the user explicitly says the preference should apply in future tasks. Without it, keep feedback scoped to the named task/topic. For more than one classification, repeat `--type`. Add `--source-ref` for a run, report, or brief task reference.

## Retrieve and use experience

```bash
python3 scripts/evolution/experience.py search \
  --task-type research --topic "AgentOps trajectory analysis" \
  --skill paper-reading --skill code-reading --limit 5
```

Use only the few returned lessons that match the task. Past outcomes can guide workflow choices, but do not reuse old findings as evidence. At task end, record only durable feedback or lessons; repeated submissions are merged.

Normal searches match Chinese and English keywords, keep a global persistent user preference near the top, and exclude Controller-specific / Evolution Engine runtime failures. Add `--include-engine` only when explicitly searching Engine execution history; do not inject those failures into ordinary paper-reading tasks.

View and maintain records:

```bash
python3 scripts/evolution/experience.py list
python3 scripts/evolution/experience.py status <EXPERIENCE_ID> needs_review
python3 scripts/evolution/experience.py status <EXPERIENCE_ID> superseded
```

Supported statuses: `active`, `needs_review`, `superseded`, and `rejected`. Prefer marking an experience out of date over silently deleting its history.
