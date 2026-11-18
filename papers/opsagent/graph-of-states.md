# Graph of States: Solving Abductive Tasks with Large Language Models

## Bibliographic record

- **Authors:** Yu Luo, Rongchen Gao, Lu Teng, Xidao Wen, Jiamin Jiang, Qingliang Zhang, Yongqian Sun, Shenglin Zhang, Jiasong Feng, Tong Liu, Wenjie Zhang, Dan Pei.
- **Status:** ICML 2026, PMLR volume 306, pp. 82294–82314 (official [PMLR paper page](https://proceedings.mlr.press/v306/luo26f.html)).
- **Primary sources:** [PMLR proceedings page](https://proceedings.mlr.press/v306/luo26f.html), [NKU publications](https://nkcs.iops.ai/publications/), [official GitHub](https://github.com/gaorch85/Graph-of-States).
- **Local full text:** `sources/papers/opsagent/graph-of-states.pdf` (ignored by Git).
- **Repository inspected:** SHA `0f28c2e11b55f3dccf8e249b63286bd83b8edd35`, MIT.
- **Reading status:** Full 21-page paper read, including method, medical/distributed-system experiments, ablation, error analysis and limitations; source inspected statically.

## Why this is relevant to OpsAgent

GoS is a general abductive reasoning framework, not a production AIOps deployment. Abduction asks which hypothesis best explains incomplete observations while seeking additional evidence. The paper argues that unconstrained CoT/ToT/graph-style reasoning can fabricate evidence, drift, fail to backtrack, or stop too early.

**Method (Section 3, Figures 2–4):** a cognitive layer (Central Agent plus role-aligned Expert Agents using ReAct tools) interacts bidirectionally with a symbolic layer. The symbolic belief state is a causal graph with symptom, evidence and hypothesis nodes; derive/refine/support/refute edges; and a state machine tracking hypothesis granularity. The graph selects the highest-confidence current focus. Agents investigate it and return observations; the central agent updates scores, instantiates nodes, and forms edges. If an ancestor is demoted, deeper descendants are pruned and search backtracks. Drill-down requires both a top-versus-second confidence gap and a minimum support count. The loop ends when the hypothesis is sufficiently fine-grained or a budget/terminal condition is reached.

- **Roles:** central application/physician agent plans and makes final decisions; domain experts retrieve evidence. On distributed diagnosis the paper configures ApplicationOperator with LinuxOperator, NetworkOperator, DatabaseOperator. These are actual role-specific agents in the framework/code, but results compare a whole design, not the isolated causal value of each role.
- **LLM and planning:** central LLM interprets, plans expert calls, reasons over graph; experts use ReAct tool calls. This gives dynamic evidence acquisition and a real coarse-to-fine search policy; the state machine is explicit control logic, not “the LLM made a plan.”
- **Memory and state:** current graph is the explicit belief; there is no cross-incident operational LTM in core GoS. The FSM records investigation depth, and graph edges preserve support/refutation. Tool/agent traces are shown but not proposed as a full AgentOps telemetry standard.
- **Verification/recovery:** evidence is linked to hypotheses; graph/FSM enforce support thresholds and backtracking. Recovery here means reasoning recovery from contradiction, not operational repair. The system diagnoses; it does not execute remediation or demonstrate recovery verification.

## Evaluation and limits

**Paper evidence (Section 4, Tables 1–3, Figure 6; Appendix D):** experiments cover interactive reformulated medical diagnosis and failure diagnosis in distributed systems, using GPT-5.1-2025-11-13. Medical results include a human-as-judge assessment because repeated LLM judgments were inconsistent and biased toward longer reports. For distributed systems, Table 3 reports 70.67% exact Match and 88.00% Relevant under LLM judge, at $0.10/case; the strongest Match baseline is much lower, while a multi-agent Forest baseline costs about $0.94/case. Ablations show large drops without focus, causal graph, or FSM. These results support the paper's framework on its evaluated settings, not general SOTA in all RCA or live operational use.

Evidence is partly hidden and accessed through configured diagnosis tools. The system uses a candidate hypothesis hierarchy and supporting evidence count, but the paper does not establish calibrated causal probabilities. The dataset's exact dimensions/uncertainty need to be read alongside the associated benchmark work, and human labels do not resolve all multi-root cases. Authors acknowledge only two domains and privacy limitations on broader authentic abductive datasets (Limitations). No dedicated open-set guarantee, multi-root protocol, remediation, MTTR field deployment, or recovery-success metric is presented.

## Code reading: paper → repository → behavior

| Paper component | Static source | Mapping |
|---|---|---|
| Entry/domain setup | `main.py`, `Run/FailureDiagnosis_IT.py` | Builds case state and the IT diagnosis setup. |
| Central loop / plans | `agents/central_agent.py:run`, `plan`, `act` | Iterates current frontier, plans expert calls, merges analyses, updates graph, backtracks, and asks whether to report/refine. |
| Expert tools | `agents/expert_agent.py`, `utils/IT_tools.py` | Specialist roles call configured diagnostic tools and return analyses. |
| Causal belief | `belief/graph.py` | Typed nodes and support/refute/refine/causal relations with scores/provenance. |
| Search control | `belief/fsm.py` | Enforces confidence-gap/support thresholds and state/budget transitions. |

**Operational distinction:** tools acquire evidence and restricted shell observations; no repair implementation was found in the core flow. The reported production-host case is an illustrative incident, not a controlled production deployment study. Static analysis only; no dependencies installed or code run.

## Relationship to other work

GoS supplies a causal-graph and FSM substrate later reused by OpsMem's incident STM, while OpsMem adds cross-incident memory. PoS generalizes the belief-state idea toward long-horizon execution/diagnosis and adds consistency/progress monitoring and recovery constraints. These are different systems and paper claims; the shared lab/project lineage does not make them one implementation.

For AgentOps, an analogous trajectory graph could link agent/action/tool/evidence/hypothesis updates and permit responsibility-aware backtracking. That is a research hypothesis, not something GoS evaluates. Cross-link [Planning](../../concepts/planning.md), [World model](../../concepts/world-model.md), [Agent runtime](../../concepts/agent-runtime.md), [Candidate Space](../../concepts/aiops/candidate-space.md), and [Verification](../../concepts/aiops/verification.md).
