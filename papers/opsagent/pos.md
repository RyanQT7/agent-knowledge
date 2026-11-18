# Beyond Memory: Harnessing Long-Horizon Agents with Explicit Belief States

## Bibliographic record

- **Authors:** Yu Luo, Jiamin Jiang, Yimin Zuo, Xidao Wen, Rongchen Gao, Yongqian Sun, Shenglin Zhang, Guiyang Liu, Cheng Zhang, Fang Situ, Qi Zhou, Dan Pei.
- **Status at 2026-11-17:** arXiv:2610.01415v1, submitted 2026-10-01; author page explicitly labels it an arXiv preprint. No conference/journal acceptance was verified by the cutoff.
- **Primary sources:** [arXiv full text](https://arxiv.org/html/2610.01415v1), [author project page](https://luoyu100.github.io/projects/progression-of-states/project/), [official GitHub](https://github.com/luoyu100/PoS).
- **Local full text:** `sources/papers/opsagent/pos.pdf` (ignored by Git).
- **Repository inspected:** SHA `6818cfa6434dbc91fcf67f0b3eb12a91db47433f`, MIT.
- **Reading status:** Full paper read (Sections 1–5, experiments and analysis); source inspected statically.

## Problem and method

The paper asks why longer context and memory do not necessarily create reliable long-horizon agents. A history can preserve past evidence while mixing obsolete conditions, inferences, and unresolved requirements. PoS is an inference-time framework that represents what the agent currently believes about the world and what remains unknown or unachieved.

**Belief representation (Section 3.1, Figure 2):** `B_t = (W_t, G, ΔE_t, ΔA_t)`. `W_t` is a task-relevant entity/state/relation model with provenance, confidence, and evidence; `G` is the goal; `ΔE` contains epistemic gaps (what must be learned); `ΔA` achievement gaps (what must change). An active gap focuses the next action without discarding the rest of the belief.

**Pipeline (Sections 3.2–3.3):** Task Agent chooses action based on current belief + active gap → environment returns observation → model proposes an updated belief → Belief Sentinel audits consistency/support against history and reports issues → task agent revises and commits validated belief → progress health tracks persistent gaps, stagnation, and recurrence → on trapping, factorized diagnosis identifies dynamics (static, cycle, drift) and blocked gap type → recovery constraints steer later actions away from repeated/off-gap actions → continue or terminate under benchmark/tool conditions.

- **LLM and agent roles:** Task Agent acts in environment; Sentinel checks belief updates and progress. LLMs produce candidate beliefs, audit findings, and progress assessments; code handles state storage, schemas, gap identity, distance/recurrence scoring, and recovery constraint assembly. This is inference-time control, not finetuned continual learning.
- **Planning:** belief-guided reactive decisions and constrained recovery are explicit. The paper does not claim a globally optimal planner or arbitrary search. A fixed, verified workflow can still be better when actions are known and risk controls are strong.
- **Memory:** belief is a structured current state, not a transcript summary or cross-incident LTM. PoS stores raw trajectory alongside it for provenance, but action selection depends on validated belief and active unresolved requirement.
- **Recovery/verification:** it redirects task policy with constraints; `compose_recovery_instruction` explicitly says it composes constraints “without selecting or executing an action.” Environment task success is evaluated; no production service repair or automatic rollback is included.

## Evaluation and limitations

**Paper evidence (Section 4, Tables 1–2, Figures 3–4):** four benchmarks span execution (ALFWorld, LOCA-Bench) and diagnosis (RCA-100, ClinDiag), with three evaluated backbones (Qwen3.7-Plus, Kimi-K3, GLM-5.3). The paper reports PoS has the highest overall score for each benchmark/backbone combination; relative gains over strongest same-backbone baselines peak at 22.68% ALFWorld, 7.53% LOCA-Bench, 37.89% RCA-100 joint accuracy, and 11.31% ClinDiag. These are benchmark results in the submitted paper, not an independently verified SOTA designation.

On RCA-100 with Qwen3.7-Plus, joint accuracy rises 24.27%→38.83% versus Raw Trajectory, but total tokens increase about 5.06× because Sentinel/belief maintenance consumes extra tokens. Removing consistency or trapping recovery degrades results. A generic “recover” prompt is weaker than factorized recovery. These support the value of structured state checks within tested tasks, while highlighting significant runtime cost and model-based evaluator/monitor dependence. The conclusion itself lists reducing overhead as future work.

**Not established:** formal truth of LLM-created beliefs, generalization to arbitrary enterprise environments, safe real-world mutation, long-term cross-session memory, or a universal rule that explicit state beats all memory designs. Consistency audit may miss unsupported claims or reject correct but novel state. The benchmark test signals are narrower than production operations.

## Code reading: paper → repository → behavior

| Paper component | Static source | Observed implementation |
|---|---|---|
| Entry/benchmark execution | `main.py`, `benchmarks/` | Config-driven benchmark adapter and run orchestration. |
| Belief schema | `belief/beliefStates.py`, `belief/worldStates.py` | Typed goals, world state, epistemic/achievement gaps, health and recovery records. |
| Belief maintenance | `belief/manager.py` | Candidate creation, validation, state commit, progress and recovery lifecycle. |
| Consistency/progress sentinel | `belief/beliefSentinel.py` | Model-produced structured audit/progress findings are schema/evidence-target checked; invalid outputs fail/raise rather than silently count as validated. This is model-assisted validation, not a formal proof. |
| Trapping and recovery | `belief/trappingDetection.py`, `belief/recoveryPlanning.py` | Measures persistence/stagnation/recurrence; composes constraints for static/cycle/drift and active gap. It does not select/execute actions itself. |

No task environment, model, or code was executed; no dependency installed.

## Relation to OpsAgent and AgentOps

PoS and GoS both make beliefs inspectable. GoS focuses on coarse-to-fine abductive hypothesis search with causal support/refutation; PoS broadens the state to dynamic world facts plus epistemic/achievement requirements and explicitly diagnoses stalls. OpsMem's STM represents incident-local diagnostic belief while LTM adds reusable experiences. OpsAgent's evidence reports and cross-review could benefit from similar explicit task state, provenance, and progress tests, but transferring PoS to an actual operations agent would require permission-bounded actions and service-level recovery checks. This intersection remains a research hypothesis. Cross-link [Memory](../../concepts/memory.md), [World model](../../concepts/world-model.md), [Planning](../../concepts/planning.md), and [Agent runtime](../../concepts/agent-runtime.md).
