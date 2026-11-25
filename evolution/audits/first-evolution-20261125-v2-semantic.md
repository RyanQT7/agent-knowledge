# First Evolution Pilot — Bounded Semantic Audit

- **Run:** `first-evolution-20261125-v2`
- **Date:** 2026-11-25
- **Pages inspected:** 10 (limit 10)
- **Scope:** Agent Memory, evidence/validity, belief state, and procedural Skill boundaries.
- **Mode:** Read-only semantic review. No formal knowledge file was edited by this audit.
- **Evidence distinction:** These are human-reviewed findings from existing notes and the cited papers; deterministic link/schema findings are in the paired JSON audit.

## Pages inspected

1. `concepts/memory.md`
2. `concepts/skill.md`
3. `papers/reflexion/notes.md`
4. `papers/opsagent/opsmem.md`
5. `papers/opsagent/pos.md`
6. `papers/opsagent/graph-of-states.md`
7. `notes/questions.md`
8. `notes/agentops/research-gaps.md`
9. `notes/agentops/reviews/agentops-review-v1.md`
10. `notes/opsagent/research-gaps.md`

## Findings

### Finding 1

- **Affected file:** `concepts/memory.md`
- **Affected claim:** Memory value is not only retention; it also depends on selecting and reusing information.
- **Evidence:** The existing Concept already distinguishes working context, episodic experience, and durable memory, and warns that a stored reflection may be wrong. Leto Sec. 3 Eq. 1 and Sec. 4.3 Eq. 2 distinguish task-relative response utility from a shared-outcome heuristic per-memory index. EvoDisco Sec. 3.3 distinguishes a cached-query retrieval proxy from the task-score objective.
- **Issue type:** Missing distinction / underspecified evidence attributes.
- **Impact:** High. A system could promote a frequently useful but unsupported memory into an accepted fact if utility, source validity, and evidence correctness share one score.
- **Confidence:** High.
- **Suggested action:** Add separate fields for source evidence, validity time, retrieval utility, retention/deletion, and acceptance status. Keep all new wording in reviewable proposals; do not infer truth from a utility score.

### Finding 2

- **Affected file:** `papers/reflexion/notes.md`; `concepts/memory.md`
- **Affected claim:** Reflexion demonstrates evaluator-to-reflection feedback stored for later attempts.
- **Evidence:** Reflexion Sec. 3.1 and Sec. 5 describe a bounded task-local memory; its evaluator/reflection limitations already note that faulty feedback can be preserved. Leto describes source-linked facts and retained revisions (Secs. 4.1–4.3); this is a different persistence and utility mechanism.
- **Issue type:** Scope difference, not contradiction.
- **Impact:** Medium. Describing both as one generic “long-term memory” would hide different write policies, lifetimes, and evidence guarantees.
- **Confidence:** High.
- **Suggested action:** Preserve both descriptions and state their distinct scopes. Do not replace Reflexion's bounded episodic claim with Leto's cross-session design.

### Finding 3

- **Affected file:** `papers/opsagent/opsmem.md`; `papers/opsagent/pos.md`; `papers/opsagent/graph-of-states.md`; `concepts/memory.md`
- **Affected claim:** OpsMem's current incident STM, reusable LTM, GoS's diagnostic belief graph, and PoS's explicit belief/gap state are distinct state objects.
- **Evidence:** OpsMem Sections III–V and its source mapping separate diagnostic STM from cross-incident cases/procedures; GoS Sec. 3 uses a causal hypothesis graph and state machine; PoS Secs. 3.1–3.3 makes a current belief and epistemic/achievement gaps explicit.
- **Issue type:** Scope difference; no conflict found.
- **Impact:** Medium. Merging these into a single “memory” claim would incorrectly imply that retained history is a validated current belief.
- **Confidence:** High.
- **Suggested action:** Keep the existing separate mechanisms and add cross-links only where the interfaces are useful.

### Finding 4

- **Affected file:** `notes/questions.md`; `concepts/memory.md`
- **Affected claim:** Existing questions about erroneous, conflicting, or stale memory remain open or partially answered.
- **Evidence:** `notes/questions.md` marks memory persistence/conflict handling partially answered and records that Reflexion does not systematically resolve erroneous reflection. Leto Limitations identify shared-outcome credit, unserved memories, and agent/task specificity; LEDGER Sec. III and Limitations add source policy and valid-time mechanisms but state bounded evaluation assumptions.
- **Issue type:** Unresolved research question; partial evidence only.
- **Impact:** High. New mechanisms do not settle whether a record is true or whether an update should be accepted.
- **Confidence:** High.
- **Suggested action:** Keep these questions open. Add narrower questions on item-level attribution, source-policy portability, and independent verification after a proposal is approved.

### Finding 5

- **Affected file:** `concepts/skill.md`
- **Affected claim:** The Concept is currently a placeholder; the engineering interpretation only says that Skills are reusable instructions/SOPs whose execution depends on the runtime.
- **Evidence:** The file has empty Definition-adjacent sections for Why It Matters, Core Mechanism, Architecture, examples, strengths, and limitations. The existing Skills catalog contains operational Skills but no consolidated cross-paper Skill concept.
- **Issue type:** Knowledge gap / incomplete Concept.
- **Impact:** Medium. It limits a future comparison between procedure memory, agent Skills, and tested Skill revisions.
- **Confidence:** High.
- **Suggested action:** Leave it untouched in Phase 1. In a later review, synthesize Reflexion, SkillOpt, and SkillHone with separate execution-trace, candidate-edit, and independent-test evidence.

### Finding 6

- **Affected file:** `notes/agentops/research-gaps.md`; `notes/agentops/reviews/agentops-review-v1.md`
- **Affected claim:** Execution traces can reveal recoverable failures and memory/context propagation, but only when the runtime recorded the relevant evidence.
- **Evidence:** The review requires model-visible context, state/memory updates, tool results, and verifier outcomes to be captured; it explicitly warns that missing trace evidence cannot be reconstructed by an LLM judge. The Research Gaps document calls for privacy-conscious event provenance and independent recovery verification.
- **Issue type:** No contradiction; existing claim is appropriately qualified.
- **Impact:** Medium. A future Skill learner cannot safely infer reusable lessons from a terminal pass/fail label alone.
- **Confidence:** High.
- **Suggested action:** Use redacted, minimal, reproducible feedback records with source spans and a test case; do not ingest full chat logs.

### Finding 7

- **Affected file:** `notes/opsagent/research-gaps.md`
- **Affected claim:** Operational experience can become stale as service/device versions, environment, and failure conditions change.
- **Evidence:** Existing gap 6 requests version, scope, source, approval, expiry/confidence, replay, and stale-memory-harm measurement. LEDGER's valid-time and deletion mechanisms are relevant, while its source hierarchy is explicitly assumption-dependent.
- **Issue type:** Open gap with a qualifying research example.
- **Impact:** High for operational deployment; a false transfer can affect diagnosis or remediation safety.
- **Confidence:** High.
- **Suggested action:** Retain the gap and treat validity/provenance mechanisms as candidates for a controlled pilot, not as a proven general solution.

### Finding 8

- **Affected file:** `concepts/memory.md`; `concepts/skill.md`
- **Affected claim:** A procedural item in memory is not automatically a validated executable Skill.
- **Evidence:** EvoDisco Sec. 3.2 can create or reorganize procedure nodes, but its evaluation scores memory graph retrieval/task performance. SkillOpt and SkillHone in the design report require candidate-version evaluation; SkillHone additionally binds a failure issue to a reproducing test and protects held-out checks.
- **Issue type:** Missing boundary / scope distinction.
- **Impact:** High for future automated edits. A helpful retrieved procedure may still be wrong, inapplicable, or unsafe as an instruction.
- **Confidence:** High.
- **Suggested action:** Keep Phase 1 Skills read-only. Require a versioned candidate, isolated reproducible tests, independent holdout, regression threshold, reviewer approval, and rollback before any future Skill update.

### Finding 9

- **Affected file:** `papers/opsagent/opsmem.md`; `papers/opsagent/pos.md`
- **Affected claim:** Memory refresh, belief revision, and operational remediation are different lifecycle steps.
- **Evidence:** OpsMem proposes cross-incident memory updates through feedback/approval; PoS validates candidate belief updates and composes recovery constraints, but its recovery instruction does not itself execute an action. The notes already preserve these boundaries.
- **Issue type:** Version / mechanism difference, not contradiction.
- **Impact:** Medium. A memory-update proposal or belief-state consistency check does not prove a service was repaired.
- **Confidence:** High.
- **Suggested action:** Keep approval and independent external outcome verification as separate gates.

### Finding 10

- **Affected file:** `concepts/memory.md`; `notes/questions.md`
- **Affected claim:** Context, Memory, Belief State, and Skill are related but not interchangeable.
- **Evidence:** Existing memory notes distinguish context and persistent storage; GoS/PoS define explicit belief structures; `concepts/skill.md` describes reusable instructions. Leto's profile/task state is a memory summary and EvoDisco's graph may hold facts or procedures, but neither paper claims that every stored item is a verified belief or tested Skill.
- **Issue type:** Missing cross-concept association; not a conflict.
- **Impact:** Medium. The same record may be wrongly treated as current truth or executable procedure.
- **Confidence:** High.
- **Suggested action:** Add a short boundary statement to the Memory Concept and retain the corresponding open questions rather than closing them.

## Summary

No true contradiction or superseded core conclusion was found in the ten-page semantic scope. The papers address separate layers: episodic feedback, graph reorganization, task utility, source/valid-time policy, and explicit belief state. The actionable knowledge gain is to represent these as separate evidence dimensions and keep Skills outside the memory-utility acceptance path. Findings 1, 8, and 10 are represented by the pending review proposals; no audited source page was rewritten.
