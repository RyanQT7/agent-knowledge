# OpsAgent: An Evolving Multi-agent System for Incident Management in Microservices

## Bibliographic record

- **Authors:** Yu Luo, Jiamin Jiang, Jingfei Feng, Lei Tao, Qingliang Zhang, Xidao Wen, Yongqian Sun, Shenglin Zhang, Tong Liu, Wenjie Zhang, Dan Pei (camera-ready project page, 11 authors). The arXiv v3 list has 9 and omits Tong Liu and Wenjie Zhang; the NKU publication entry also lists 9. This discrepancy is preserved rather than silently normalized.
- **Status at 2026-11-17:** ASE 2026 Companion Proceedings, Industry Showcase (per the author project page / paper); arXiv:2510.24145v3, revised 2026-05-12. Do not read the arXiv category as the publication venue.
- **Primary sources:** [author project page](https://luoyu100.github.io/projects/opsagent/project/), [arXiv v3 full text](https://arxiv.org/html/2510.24145v3), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local full text:** `sources/papers/opsagent/opsagent.pdf` (ignored by Git).
- **Official repository:** [Johnn13/OpsAgent](https://github.com/Johnn13/OpsAgent), verified from the author project and paper; inspected at `6d61b8bb9c6bc9de6347601562c644fade324765`. No repository license file was present at that commit.
- **Reading status:** Full paper read (Sections 1–7, tables, deployment discussion, and case study); source inspected statically.

## Problem and contribution

The paper targets incident management across anomaly detection (AD), failure triage (FT), and root-cause localization (RCL) when evidence is heterogeneous and systems change. Its motivation is that learned AIOps models often need system-specific retraining and are hard to audit, while direct LLM use on raw telemetry is costly, brittle, and weak at accumulating experience.

The concrete system combines (1) a training-free metric/log/trace processor, (2) three task-oriented specialist agents with orchestrated peer cross-review, and (3) two offline evolution paths: PPO updates to agent parameters and reflection-derived external experience retrieved for later cases. The main contribution is this deployable pipeline and its operational evaluation, not a new general-purpose planning algorithm.

## Mechanism and operational workflow

**Paper pipeline (Sections 3.1–3.4; Figures 1–5):** ticket/query → intent interpreter extracts time window and requested AD/FT/RCL tasks → orchestrator obtains metric/log/trace evidence and normalizes it → Anomaly Sentinel, Failure Diagnoser, and Root Detective reason in parallel over the shared evidence → each specialist reviews the other two outputs → specialists refine → root-cause report → on-call engineer inspects and applies mitigation → a validated case can enter offline reflection/training.

- **Evidence:** metrics become ranked anomalies (paper uses a 3σ criterion, shape labels, top-five pods/metrics); logs are keyword-filtered, Drain3-parsed, ranked by TF–IDF and deduplicated; traces use per-call-type high-latency thresholds and summarize callees/call paths. These transformations are designed to retain salient cues while reducing input volume. The modalities are normalized into a shared text representation; agents are not split by modality.
- **Roles:** Intent Interpreter and Orchestrator are control components; the three named specialists are distinct agents corresponding to diagnostic tasks. Cross-review is peer critique over answers and rationales. It is not an independent verification agent or a formal evidence checker.
- **LLM and planning:** a local 14B model performs semantic interpretation and open-ended diagnostic reasoning. The work does need language understanding across differently formatted evidence, but the paper does not establish that every subtask requires an LLM. The workflow is largely fixed and task-triggered; it is not a general dynamic planner that discovers arbitrary tools or rewrites the operational graph.
- **Memory and execution state:** per-agent MessagePool/ReviewPool hold current collaboration; reflection vectors hold external experience for retrieval; PPO provides offline parameter updates. The report contains rationale/evidence, but the paper does not define a complete event schema for timestamps, dependency IDs, or state transitions.
- **Recovery and verification:** the system returns diagnoses, not automated remediation. The engineer executes and validates mitigation. Case feedback can be used for evolution. Thus detection, diagnosis, human remediation, and outcome feedback are present; autonomous repair and machine-verified service recovery are not.

## Evidence, evaluation, and claims

**Paper evidence (Section 4, Tables 1–3; Section 5, Figures 6–7):** OPENRCA has 335 cases from Telecom, Bank, and Market, with over 68 GB telemetry; three experienced engineers calibrated labels. A random 60/40 split and five repetitions are reported. The paper’s strict `Correct` means every requested subtask is right; `Partial` means at least one is right. With Qwen2.5-14B-Instruct-1M the reported average is 16.54% Correct / 41.35% Partial and 71.18 seconds per case. The 60% evolution budget is compared with 0%; self-evolution improves the benchmark metric, but the reported procedure does not amount to autonomous online weight updates during a live incident.

The Lenovo deployment is reported as 10,492 incidents over 53 days across about 25,000 infrastructure instances. The paper reports 84.09% overall diagnosis accuracy based on OCE-confirmed root-cause reason and component, with 126 seconds average diagnosis time; approximately 70% of incidents were routine/localized and reached 97% accuracy, while difficult cross-component/incomplete-evidence cases reached 54% after up to three re-analysis rounds. Three on-call engineers rated 150 reports (Section 5.3). Engineers applied mitigation; the paper does not report an automated repair success rate or a controlled counterfactual comparison. This production slice has richer alert context and recurring incidents than the benchmark.

**Authors' claims:** generalizability, interpretability, cost efficiency, and sustained self-evolution. **Mechanism actually implemented:** shared evidence text, role-specific prompting, cross-review/refinement, offline PPO and retrieval of validated reflections. **What experiments support:** reported benchmark gains, expert-rated report usefulness, and observational deployment outcomes. **Not established:** unbiased causal attribution to each component in production, generalization beyond the three benchmark systems, or safe autonomous recovery.

## Code reading: paper → repository → behavior

| Paper component | Static source inspected | Observed implementation |
|---|---|---|
| Entry and task orchestration | `main.py`; `agents/orchestrator.py:process_task` | `execute` parses the request; orchestrator processes data, instantiates all three specialists, calls `think`, cross-review, then `refine`. |
| Shared evidence preprocessing | `utils/data_processer.py:extract_metric_features`, `extract_log_features`, `extract_trace_features` | Metric features, keyword/template filtering, trace descriptions. Repository defaults/settings should be checked against the paper when reproducing: trace helper has a `q=0.98` default while the paper describes a 95th-percentile per-call threshold. |
| Roles and peer review | `agents/ad_agent.py`, `ft_agent.py`, `rcl_agent.py`, `agents/orchestrator.py` | Distinct task agents use common blackboard/evidence and message/review pools; the orchestrator drives peer critique. No separate verifier module was found. |
| Evolution | `fine_tuning.py`, `reflection/` (repository tree) | Offline training and retrieval assets are provided. A deployment outcome still requires external confirmation before becoming validated experience, consistent with the paper’s workflow. |

**Reproducibility:** code and prompts are public, but license is unspecified; benchmark/production data are not fully public. Core orchestration can be mapped, but end-to-end reproduction requires model weights, data, configuration, and dependencies not bundled as a ready reproducible package. Static analysis only; no dependency installation, code execution, or operational tool use.

## Structured diagnostic checklist

- **Failure taxonomy:** pipeline can expose preprocessing/interpretation, AD, FT, RCL, review, and termination errors. The paper does not supply a complete taxonomy for Agent-runtime failures.
- **Responsible agent / root step / propagation / symptom:** report records agent reasoning, but no ground-truth per-step causal labels; last incorrect specialist should not be equated with the root cause.
- **Candidate space:** OPENRCA labels are drawn from each system's component/failure-type universe. The method does not describe topology-constrained, hierarchical candidate pruning comparable to KRCA.
- **Ground truth and judge risk:** benchmark labels are engineer-calibrated; production labels use OCE-confirmed mitigation. Automated judge/evaluator details and label uncertainty limit direct comparison. LLM peer review can repeat shared model biases.
- **Network AIOps transfer:** useful shared M/L/T representation and human-auditable diagnostic workflow transfer conceptually. Network transfer would need flow/packet counters, topology/configuration, routing events, protocol state, and explicit candidate constraints; microservice results do not demonstrate that transfer.

## Questions to carry forward

The most useful next study is not “add another reviewer,” but instrument the collaboration as a versioned event graph: who read which evidence, which hypothesis/edge changed, why, which verifier checked it, what human action followed, and whether service-level recovery actually occurred. This would align OpsAgent's diagnostic loop with [AgentOps trajectory attribution](../../agentops/README.md) and [AIOps verification](../../concepts/aiops/verification.md).
