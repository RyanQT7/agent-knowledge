# Rethinking Tool Design for Agentic RCA: A Controlled Empirical Study (ToolRCA)

## Bibliographic record

- **Authors:** Yu Luo, Rongchen Gao, Zhenhui Zhou, Changchang Liu, Yuliang You, Yongqian Sun, Shenglin Zhang, Qiuai Fu, Shijie Wang, Dan Pei.
- **Status at 2026-11-17:** arXiv:2610.05009v1, submitted 2026-10-04. No peer-reviewed venue listed at cutoff; do not call it published/SOTA.
- **Primary sources:** [arXiv full text](https://arxiv.org/html/2610.05009v1), [author project page](https://luoyu100.github.io/projects/toolrca/project/), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local PDF:** `sources/papers/opsagent/toolrca.pdf` (ignored by Git).
- **Official code:** Not publicly found; author page links the preprint and study, not a repository. No commit/license.
- **Reading status:** Full paper read (Sections 1–7, tables, trajectory analyses, validity threats).

## Question and system

This study isolates an often-hidden design decision in agentic RCA: how much of analysis belongs inside tools versus the agent's own reasoning. It introduces four tool levels (Section 3.2, Table 1): L0 gives the agent a Python analysis interface; L1 exposes metric samples, summaries, ownership/topology; L2 returns statistical evidence such as anomalies, change points, temporal features, and evidence relations; L3 returns ranked root-cause candidates and explanations. Across L1–L3 it implements 24 callable interfaces. These are independent selectable interfaces; L2/L3 can access case data directly and do not require a lower-level call first.

**Pipeline (Sections 3.1–3.5):** one ReAct-style agent receives an incident and one configuration of tool interfaces → selects/calls tools within step/output limits → integrates observations and submits ranked root causes plus fault type or times out → scores localization, type, completion, calls/tokens/cost/latency. No multi-agent collaboration, durable memory, operational repair, or recovery loop is evaluated.

- **Why an agent:** selection and interpretation of tools are part of the object under study. LLM reasoning matters in connecting evidence and deciding whether to accept a candidate. The paper does not show that multi-agent delegation is needed.
- **Planning/state/memory:** the agent performs reactive tool selection under a shared ReAct harness and interaction budget. It has per-case context/trajectory, not a structured world model or cross-case memory. It does not implement dynamic plan synthesis beyond choosing calls.
- **Verification:** diagnosis is scored against known injected service/type labels. There is no live incident verification or remediation. L3 is a recommendation source, not ground truth; the agent may keep or override it.

## Evidence and experiments

**Paper evidence (Section 4, Tables 3–6, Figures 3–9):** 375 RCAEval-RE1 failure cases: 125 each from Online Boutique (12 services), Sock Shop (15), and Train Ticket (64; 198–238 metrics/case). Five injected failure types are represented. Qwen3.7-Plus was tested under all eight configurations; three Qwen models were tested on a shared four-configuration subset. Only metric evidence is used; no production incidents/logs/traces are in scope.

For Qwen3.7-Plus, L0 has 85.4% AC@1 and 41.4% failure-type accuracy (TA); L3 has 82.8% AC@1 and 45.6% TA at 35.8 sec / 22.8K tokens per case versus L0's 88.6 sec / 50.4K tokens. L1+L2+L3 yields 78.0% AC@1 but 49.0% TA. Tool composition therefore changes localization and fault typing differently. The 8B model invokes L3 in only 0.8% of trajectories and drops 13.9 percentage points when L3 is added; larger tested models benefit more. Effects vary by environment: adding L2 to L3 helps Online Boutique but reduces AC@1 in Sock Shop and Train Ticket.

Trajectory analysis (Section 5.1; Figures 5, 8–9) finds that the agent often considered the correct cause and sometimes received a correct L3 candidate but changed its final answer after seeing an anomalous, propagated symptom. An anomaly ranking can be mistaken for causal attribution; additional evidence can cause confirmation-seeking rather than hypothesis testing. The authors argue for counter-evidence and discriminative evidence tools, not just more analysis.

## Limits and evidential calibration

**Authors' claim:** tool abstractions and compositions have different utility by target, model, and system. **Mechanism tested:** fixed sets of metric-only tools in one shared ReAct harness. **Supported:** point-estimate contrasts on this benchmark and the trajectory-level examples of recommendation override. **Not established:** statistical significance of small rank changes, generalization to other model families, real production or multimodal RCA, multi-root/open-set diagnosis, or the causal effect of service count. The paper does not report repeat counts, seeds, or uncertainty intervals in its manuscript; conclusions about small differences should remain provisional. It also notes that its tools cover only representative capabilities and do not isolate every interface's contribution (Section 5.2).

## Relation to other work and Network AIOps

This study explains why an OpsAgent architecture needs to choose tool boundaries deliberately: high-level pruning can make search cheaper, while an LLM can undo good recommendations when it confuses correlation, propagated symptoms, and source faults. Compared with KRCA, ToolRCA isolates metric tool abstraction on a public benchmark but lacks KRCA's real production deployment and topology-grounded hyper-scale scenario. Compared with OpsAgent, it tests neither M/L/T normalization nor cross-review/self-evolution. In Network AIOps, a promising design is L1 safe topology/counter reads, L2 deterministic change-point/causal evidence, and L3 candidate ranking—with the agent required to query counter-evidence and preserve provenance. This is a hypothesis to test, not a direct conclusion of the paper.
