# KRCA: An Efficient Root Cause Analysis System in Hyper-scale Microservice Systems via Agentic AI

## Bibliographic record

- **Authors:** Jiamin Jiang, Jingfei Feng, Yu Luo, Qingliang Zhang, Yongqian Sun, Wenwei Gu, Shenglin Zhang, Tianyu Cui, Yao Wu, Jielong Huang, Nan Qi, Dan Pei.
- **Status at 2026-11-17:** ASE 2026 research paper (DOI: [10.1145/3832783.3834468](https://doi.org/10.1145/3832783.3834468)); arXiv:2607.01788v3, revised 2026-08-02. NKU lists it as ASE ’26. This is a published paper, not only an arXiv preprint.
- **Primary sources:** [arXiv full text](https://arxiv.org/html/2607.01788v3), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local full text:** `sources/papers/opsagent/krca.pdf` (ignored by Git).
- **Official repository:** **Not publicly found** as of the cutoff after checking the paper/project links and targeted repository searches. No code commit or license can be recorded.
- **Reading status:** Full paper read (Sections 1–7, tables/figures, production discussion); no repository available for code analysis.

## Problem and core method

KRCA addresses RCA when microservice topology, services, and metrics change rapidly and the candidate universe is enormous. Its central idea is to reduce the search space using the system's hierarchy and then let agents reason over a constrained causal skeleton. This is materially different from sending all alerts and metric names to an LLM.

**Pipeline (Sections 3–4; Figures 2–6):** incident alert → follow API/dependency graph and score failure rate/latency to drill down toward suspicious services → keep top-three candidate services → detect anomalous metrics within candidates → create a high-recall, skeleton-based causal graph over metric anomalies → Main Agent delegates causal-edge verification and missing-link search to domain subagents such as Traffic, CPU, and GPU specialists → memory retrieval informs analysis → report service, failure type, and supporting causal relations to SRE.

- **Candidate pruning:** API-level drill-down narrows service candidates; the paper reports that coarse service-level search can involve more than ten services in 56.7% of cases, while API-level drill-down reduces this to 36.3%. Within a service there may still be hundreds of metrics (the paper describes >400 in a typical service). Structural prior limits pairwise causal search; experiments report unconstrained causal relation accuracy around 30% in the high-dimensional setting versus above 60% with the constrained approach. The skeleton is intended for high recall, with agent verification refining it.
- **Evidence:** primary evidence is service/API topology and time-series metrics (latency, failure rate and anomalous metric series). This is not a multimodal logs/traces/tickets ingestion paper; the authors explicitly argue that direct LLM analysis of raw high-volume time-series is not scalable.
- **Agent roles and planning:** Main Agent coordinates domain-specific Sub Agents that inspect/verify candidate causal relations. This is a real agent decomposition. The overall staged drilldown is planned, while local edge verification is delegated. It is not evidence that unrestricted multi-agent conversation is beneficial; candidate reduction and shared graph are core.
- **Memory and tools:** a three-tier memory has Working, Factual, and Experiential components to retain current reasoning, domain facts, and prior cases. MCP exposes data/query tools. The output is an RCA report, not a change plan.
- **Recovery and verification:** the causal skeleton is checked by subagents and the diagnosis report is evaluated against labels/SRE judgment; this does not verify a production remediation. SREs act on findings. No autonomous rollback or post-change recovery monitor is described.

## Evaluation and evidence boundaries

**Paper evidence (Section 4, Tables 1–3; Section 5.1–5.3, Figure 8):** a dataset of 300 production incidents sampled from Kuaishou (Oct 2025–Mar 2026), across business lines and nine failure categories; five SREs with >5 years' experience establish service/type labels. The paper evaluates multiple model combinations and reports best AC@1 of 0.88 for root-cause service and 0.79 for failure type (Claude Opus 4.6 + GPT-5.1), around 146.59 seconds per case. The dataset is private. The SRE utility check uses a 30-case sample and subjective report ratings.

The paper also reports deployment on Kuaishou's Tianwen monitoring platform (Oct 2025–Mar 2026), support for >2,000 alerts/day, 483 system emergency incidents and 82% joint service/type correctness by postmortem labels. Mean diagnosis time is reported as 52 minutes before deployment versus 11.8 minutes after (77.3% lower). These are observational before/after operational results, not a randomized or matched counterfactual. Paper-reported failure cases include missing availability signals and simultaneous cascading anomalies, which expose the difficulty of separating propagation from correlation.

**Authors' claim:** efficient, production-ready RCA at hyper-scale. **Mechanism:** topology-informed pruning plus metric-level causal prior and agent review. **Experiment support:** label-based RCA accuracy and reported deployed use/time reduction. **Not established:** open-set root causes, calibrated uncertainty, multi-root attribution across concurrent incidents, generalization outside Kuaishou, or that the final report caused the entire MTTR change. No remediation execution is evaluated.

## AgentOps and AIOps analysis

- **Failure taxonomy:** possible errors include alert interpretation, wrong API branch, missed anomaly, false skeleton edge, missed true edge, subagent/tool failure, memory mismatch, or overconfident final report. The paper does not evaluate step-level localization of these errors.
- **Attribution:** the service-level ground truth identifies a target component/type, but it is not a per-agent or per-action causal trace. The last subagent to report is not necessarily the root of a wrong answer.
- **Ground truth:** postmortem labels from responsible SREs are a meaningful operational target, but can conceal competing root causes and uncertain/cascading labels. Need explicit multi-root/unknown labels and evidence provenance.
- **LLM judge:** where used for report/usability assessment, it cannot substitute for SRE ground truth; wording similarity may reward plausible-but-wrong reports. Preserve component/type exactness separately from relevance.
- **Network AIOps transfer:** topology-aware search and hierarchical pruning are directly relevant to network RCA. Replace API/service hierarchy with device/interface/route/flow/topology/configuration layers; add multi-root and open-world candidates, temporal dependencies, and intervention evidence.

## Code discovery and reproduction

| Field | Result |
|---|---|
| Paper | KRCA, ASE 2026 |
| Repository / official status / evidence | Not publicly found; the author/lab listing links the paper, but no code link or paper-linked repo was identified. |
| Commit SHA / license | N/A |
| Code coverage / entry point / modules | N/A; do not infer an implementation from the paper architecture. |
| Paper-code mapping | Not possible until an author-designated repository is released. |

## Reading conclusion

KRCA's strongest transferable design is to use deterministic/structured operational topology to shrink the candidate space before asking an LLM to assess ambiguous causal evidence. This complements [Candidate Space](../../concepts/aiops/candidate-space.md), [Topology-aware RCA](../../concepts/aiops/topology-aware-rca.md), and the existing [Hybrid RCA architecture synthesis](../../notes/aiops/reviews/network-aiops-architecture-synthesis-v1.md). It should be tested against missing topology, stale dependencies, unknown fault types, and simultaneous roots before adopting the paper's production claims as a general rule.
