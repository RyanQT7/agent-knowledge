# Claim and Evidence Records

Phase 1 stores one JSON object per line in `claims.jsonl`. JSON is a subset of YAML 1.2. This avoids a database while keeping stable claim IDs and deterministic validation.

```yaml
claim_id: agent-memory.reflexion.001
statement: Reflexion places evaluator-derived verbal reflections in a bounded task-local memory for later attempts.
claim_type: paper_fact # paper_fact | code_fact | cross_source_synthesis | interpretation | learner_signal | execution_observation
scope: Reflexion's tested within-task attempt loop
status: active # active | needs_review | contested | superseded | retracted
evidence:
  - source_id: arxiv:2303.11366
    source_version: arxiv:2303.11366v1
    source_uri: https://arxiv.org/abs/2303.11366
    locator: Sec. 3.1 and Algorithm 1
    relation: supports # supports | qualifies | contradicts | supersedes | related_to
    accessed_at: 2026-11-25
    source_hash: null
related_claims: []
supersedes: []
last_reviewed_at: 2026-11-25
```

Rules:

- Claims describe one checkable statement with explicit scope. Split compound claims.
- Keep source facts, code behavior, synthesis, interpretation, learning signals, and execution observations distinct.
- Include one evidence item per source/locator. A Claim can have multiple evidence entries.
- Similarity only proposes links; it never proves support.
- A direct conflict remains `contested` until its definitions, scope, assumptions, and versions have been compared.
- `qualifies` narrows a claim; it is not itself a contradiction. `supersedes` must link the old claim and mark the old record `superseded`.
- Keep retracted and superseded records for history. Never reuse a claim ID for a different statement.
