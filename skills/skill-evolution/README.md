# skill-evolution

Creates immutable Skill candidates under `evolution/skill-proposals/`, saves a diff and baseline hash, and provides static/retrospective evaluation plus explicit approve, apply, reject, and hash-guarded rollback commands through `scripts/evolution/skill_evolution.py`.

No proposal is applied automatically. The evaluation reports `Inconclusive` unless the candidate is identical (`Equivalent`) or fails a deterministic check (`Regressed`); it does not infer improvement from the optimizer's own opinion.
