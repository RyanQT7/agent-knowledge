---
name: skill-evolution
description: Turn evidence-backed, reusable task experience into a small reviewable Skill proposal, assess it lightly, and wait for explicit approval before applying.
metadata:
  short-description: Propose and review Skill improvements
---

# Skill Evolution

Improve task quality, clarity, scope, and cost from real experience. A failure does not automatically mean a Skill defect: first distinguish environment, Controller, model, evidence, and Skill causes. Check whether the Skill already contains the needed rule. Do not patch a Skill for a resolved Controller bug or an environment condition. One explicit high-impact user correction may justify a proposal; weak or one-off evidence should stay in Experience Memory.

Improvements can add, clarify, simplify, remove, reorder, or replace instructions. Do not grow the Skill by default. Keep one proposal focused on one reusable problem. Never change Controller code, approval rules, or formal Skills in the proposal-generation stage.

## Review flow

1. Retrieve a few relevant records with `experience-memory`.
2. Read the target Skill and its current Git version. Check whether the instruction already exists and whether the issue belongs to that Skill's scope.
3. If the issue is covered, belongs elsewhere, or lacks evidence, record `No Skill Update Needed` or leave the case for observation.
4. Draft the smallest complete candidate in a temporary file. Do not edit the formal Skill.
5. Create and evaluate the candidate:

```bash
python3 scripts/evolution/skill_evolution.py draft \
  --skill paper-reading --experience <EXPERIENCE_ID> --candidate /tmp/paper-reading-candidate.md
python3 scripts/evolution/skill_evolution.py list
python3 scripts/evolution/skill_evolution.py show <PROPOSAL_ID>
python3 scripts/evolution/skill_evolution.py evaluate <PROPOSAL_ID>
```

The evaluator performs static checks and labels historical reasoning as retrospective. It does not claim a measured improvement without comparable execution results. A candidate with a mismatched Skill name, invalid frontmatter, a stale target hash, or substantial unexplained text growth is marked regressed.

## Approval and rollback

Proposal creation and evaluation never edit the formal Skill. A user must explicitly approve:

```bash
python3 scripts/evolution/skill_evolution.py approve <PROPOSAL_ID> --note "Reviewed diff and evidence"
python3 scripts/evolution/skill_evolution.py apply <PROPOSAL_ID>
```

Application checks the saved base hash and evaluated candidate hash. It preserves the original Skill, candidate, and diff in the proposal directory. If the Skill has changed after application, rollback refuses to overwrite later work:

```bash
python3 scripts/evolution/skill_evolution.py rollback <PROPOSAL_ID>
```

Reject or defer a candidate without applying it:

```bash
python3 scripts/evolution/skill_evolution.py reject <PROPOSAL_ID> --note "Not reusable across tasks"
```

Static review and retrospective analysis are not blind benchmarks. Use an independent evaluator or a small comparable task only when the expected value justifies the model calls.
