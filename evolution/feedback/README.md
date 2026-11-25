# Execution Feedback Record

Phase 1 defines a minimal, redacted schema for later Skill Evolution. It does not collect full Codex chat history or edit any existing Skill.

```yaml
feedback_id: feedback-...
task_type: paper-code-discovery
skill_name: paper-code-discovery
skill_version: <git SHA or content hash>
failure_signature: wrong-paper-repository-match
expected_behavior: distinguish a related repository from an implementation of the exact paper
observed_behavior: ...
evidence: <short redacted trace excerpt or file/line reference>
user_correction: ...
reproducibility: repeatable | intermittent | unknown
suspected_cause: ...
status: recorded | triaged | candidate | resolved | rejected
recorded_at: YYYY-MM-DD
```

Persist only the smallest reproducible evidence needed to explain the failure. Remove credentials, personal data, and unrelated conversation text. One failure is not sufficient evidence to automatically change a Skill.
