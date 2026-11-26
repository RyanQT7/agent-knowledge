# GALA: Graph-Augmented LLM Agents for Root Cause Analysis and Incident Response in Microservices

## Bibliographic record and version identity

- **Authors:** Yifang Tian, Yaming Liu, Zichun Chong, Zihang Huang, Yiran Li, Hans-Arno Jacobsen.
- **Publication:** Proceedings of the 41st IEEE/ACM International Conference on Automated Software Engineering (ASE ’26), Research Track, October 12–16, 2026, Munich, pp. 55–67. DOI: [10.1145/3832783.3834335](https://doi.org/10.1145/3832783.3834335).
- **Primary version read:** [arXiv:2608.08968v1](https://arxiv.org/abs/2608.08968), submitted 2026-08-10; 13 physical PDF pages. Its title is the ASE title above, while the framework described in the abstract and method is named **GALA+**.
- **Related earlier preprint:** [arXiv:2508.12472](https://arxiv.org/abs/2508.12472), “GALA: Can Graph-Augmented Large Language Model Agentic Workflows Elevate Root Cause Analysis?” (submitted 2025-08-17; five listed authors). The author [project page](https://msrg.github.io/publications/gala-graph-augmented-llm-agents-for-root-cause-analysis-and-incident-response-in-microservices/) identifies it as the earlier preprint and describes the ASE paper as updated GALA+ work. The ASE paper cites old GALA as a baseline and reports changed components. Treat these as a research lineage, not interchangeable PDFs or a title-only rename.
- **Source PDF:** sources/papers/opsagent/gala-ase26.pdf (local, Git-ignored).
- **Extracted full text:** sources/papers/opsagent/gala-ase26.txt (layout-oriented text with physical-page boundaries; local, Git-ignored).
- **Official artifact repository:** [EvanTian233/GALA-for-RCA](https://github.com/EvanTian233/GALA-for-RCA), inspected at commit 24d1329d20fb9139f7899a1bed9e8d0bdaf00be0.
- **Reading status:** Full local PDF read end to end, including evaluation, case study, threats, conclusion, and references. Core implementation was not publicly available. The supplementary one-page technical report and released output/annotation artifacts were read statically; no code or benchmark was run.

## Research-session provenance

- **Workflow:** Lightweight research by the current Codex main session; no Evolution Engine or child model sessions.
- **Paper-reading guide:** Frozen candidate skill-paper-reading-20261126t110225z-ed765d, used without modification; also followed aiops-paper-reading and knowledge-review.
- **Experience Memory used as process guidance:** exp-311316848c9f (explain mechanisms, concrete cases, results, and locators); exp-4018148873bb (pin exact source version and do not infer implementation from a README); exp-77ed5c77884f (coverage matters more than note length); exp-8da9d9cb732b (bind claims to version, locator, and denominator). These records are not evidence for GALA claims.
- **Model:** Codex main-session model identifier is not exposed by the available runtime tools; recorded as unavailable rather than inferred.
- **Runtime:** Research completed 2026-11-26 12:38:22–13:05:14 UTC (26m52s; Git wrap-up excluded).
- **Token use:** The current-session runtime does not expose input/output token totals; unavailable.
- **Original-page visual verification:** The local image viewer actually opened the main-paper physical pages 3, 4, 5, 8, 9, and 10 and supplementary-report physical page 1. This covered Figure 2, the STRIX scoring/RRF formulas and context assembly, Algorithm 1/Figure 3, Tables 1–3, Figure 4/Table 4, Table 5, Figure 5, the Figure 6 case study, and the AegisLab table. Renders are in /home/xieqitong/.cache/agent-knowledge/paper-pdf/gala-ase26/ and /home/xieqitong/.cache/agent-knowledge/paper-pdf/gala-tech-report/; they are local cache, not repository artifacts. Physical pages, not printed pagination, are used below.
- **Materials limit:** The paper is arXiv v1 and ASE bibliographic identity is corroborated by the PDF and author page. No separate publisher PDF or core GALA source was available for a second-version diff. Exact LLM prompts, SURE-Score checklist, scorer, and industrial telemetry were not released.

## One-sentence summary

GALA+ uses a metrics-based BARO ranking and a trace/dependency-graph-based STRIX ranking to seed an LLM consolidation step, then investigates a bounded neighborhood around high-ranked services with localized metrics, logs, and trace context before producing a ranked diagnosis, incident narrative, and three time-horizon remediation recommendations.

## Problem and contribution

The paper targets microservice incidents where an alerted or visibly slow service may be a downstream victim rather than the fault origin. A useful response needs more than a ranked service: it should explain a symptom-to-root-cause chain and provide operationally specific next steps. The authors argue that single-modality ranking misses complementary signals, unconstrained agent exploration can drift or hallucinate, and conventional text-similarity metrics cannot assess whether an RCA narrative is evidence-grounded and actionable. (Abstract; §§1–2, PDF pp. 1–2.)

The contributions are:

1. **Dual-signal hypothesis generation.** BARO analyzes metrics, while STRIX derives a service ranking from trace latency and dependency structure. A consolidation agent handles their asymmetric outputs rather than averaging incomparable scores.
2. **Graph-guided investigation.** Investigator agents inspect candidate-specific telemetry and, when local evidence is insufficient, expand to neighboring services in batches, subject to confidence and neighborhood bounds.
3. **Incident response and report evaluation.** The system emits a final ranking, incident summary, and immediate/permanent/preventative recommendations. SURE-Score evaluates report quality against four RCA-specific dimensions with LLM graders and SRE review. (§3–5, PDF pp. 2–9.)

The causal language needs care. BARO constructs a metric-derived causal DAG; STRIX’s graph is a service-call dependency graph recovered from distributed traces. A dependency edge is structural evidence, not by itself an identified physical causal relation.

## Task boundary and outputs

- **Tasks:** Root-cause ranking/localization, diagnosis and explanation, incident summarization, and recommendation generation.
- **Not implemented as reported:** live alert detection, executing repair commands, validating that a repair restored service, or updating durable operational knowledge.
- **Input:** metrics M, logs L, traces T around an incident. The paper defines the root cause as a pod plus failure mode that, when addressed, resolves the incident.
- **Candidate space:** services/pods in the deployment; the ranking metric is evaluated at pod level. The exact mapping from service-level STRIX nodes to pod-level candidates is not fully specified.
- **Output:** ranked candidates, an incident summary, and three recommendations: immediate mitigation, permanent fix, and prevention.
- **Modalities:** metrics, logs, and distributed traces; each retains a distinct representation in the diagnostic bundle. This is structured prompt/context fusion rather than a learned shared embedding. Topology constrains where agents inspect.

### End-to-end workflow

1. **Metric ranking:** BARO applies Bayesian online change-point detection, builds a metric-derived DAG, and scores candidate services based on causal influence on observed anomalies.
2. **Trace ranking:** STRIX builds a weighted service dependency graph from spans and ranks nodes using instability, centrality, and impact.
3. **Consolidation:** an LLM agent joins the two candidate lists, prioritizes cross-signal agreement, infers fault type for trace-only candidates, and retains metric-only candidates at lower confidence.
4. **Context synthesis:** for each pod, it packages per-second metrics in a window around the alert, a one-hop dependency subgraph, and timestamp-sorted/distilled logs.
5. **Graph-guided investigation:** up to k initial candidates are investigated in parallel. Each investigation produces a confidence, evidence summary, causal explanation, and supporting/contradicting factors. If confidence is below θ, direct predecessors and successors are sampled in batches; a batch containing a high-confidence candidate ends that branch.
6. **Evidence synthesis:** a synthesis agent reconciles branch results, anchors local confidence to the initial ranking, and requires the selected candidate’s causal narrative to explain symptoms in other investigated branches.
7. **Report generation:** the final agent emits an incident summary and the three staged recommendations for an SRE. The paper does not report executing those actions or checking recovery.

Figure 2 (PDF physical p. 3) shows four phases: initial hypothesis generation, pod-centric context synthesis, graph-guided investigation, and diagnostic synthesis/incident response. Algorithm 1 (PDF physical p. 5) is important for interpreting “bounded graph exploration”: as printed, it investigates the initial top-k services and their direct predecessor/successor sets; the neighbor loop calls the Investigator on each neighbor and does not visibly recurse into that neighbor’s neighbors. The prose calls expansion depth-bounded, but the released implementation is unavailable to resolve whether runtime follows a deeper variant.

## Core method

### BARO and STRIX

BARO is used as the metrics-side initial ranking. The paper notes two limitations of metric causal discovery: edge direction can be misidentified, and routine fluctuations can be confused with genuine anomalies. It therefore adds a trace-side structural ranking instead of treating the metric DAG as sufficient. (§3.1.1, PDF p. 3.)

STRIX (Structural Trace Ranking via Intermodal eXploration) aggregates span data into a directed service-call graph. Nodes/edges carry call volume and latency statistics including mean, P50, P95, P99, maximum, standard deviation, and cumulative latency. Its three scores are:

- **Instability:** φ₁(v) = P99(v) / P50(v). The intuition is that contention may create a long latency tail while the median is relatively stable.
- **Centrality:** φ₂(v) = PageRank(v) × (1 + in-degree(v)) / (1 + out-degree(v)). This combines global reachability with a fan-in/fan-out heuristic.
- **Impact:** φ₃(v) = TotalLatency(v) × max(0, 1 − max over outgoing callees u of AvgLatency(u) / AvgLatency(v)). This discounts time plausibly spent waiting for a slow callee, then scales remaining self-time by cumulative span volume.

The final STRIX ordering uses Reciprocal Rank Fusion, not a weighted sum of raw values: RRF(v) = Σⱼ 1 / (60 + rank(v, φⱼ)). This is scale-insensitive, but it does not make the three ranking heuristics causal evidence. In particular, the impact term assumes the slowest outgoing callee is a useful approximation for downstream wait; the paper does not establish that this decomposition recovers causal delay under all fan-out or concurrency patterns. (§3.1.2, PDF pp. 3–4.)

### Consolidation and localized context

The two rankings are intentionally not symmetric. BARO can provide service/fault-type pairs, while STRIX provides service order but no fault type. The LLM consolidation step uses agreement as stronger evidence, infers a plausible type for a trace-only candidate, and downweights a metric-only candidate with no trace corroboration. It returns confidence and provenance, but no deterministic confidence formula or calibration study is reported. (§3.1.3, PDF p. 4.)

The context bundle preserves modality boundaries:

- Per-second metric values for each monitoring metric in [τ−Δτ, τ+Δτ], where τ comes from the alert and the numeric window Δτ is not reported.
- A one-hop graph of the candidate and direct predecessors/successors with edge attributes.
- Error/exception logs, sorted by time and deduplicated by message. If too many remain, a representative sample is selected; if few remain, some non-error logs are added to distinguish silent failure from mere log absence.

The metrics are serialized as timestamped JSON rather than earlier Base64 line charts; the authors report lower token use and better diagnosis but do not give a controlled numeric result for that representation change. The log budget and sampling method are not specified in enough detail to reproduce. (§3.2, PDF p. 4.)

### Investigation state and stopping

The reported defaults are k=6 parallel initial branches, θ=0.6, and batch size b=2. A branch stops when its local assessment reaches θ; otherwise, it examines direct incoming/outgoing neighbors in uniformly random batches and stops when any member of a batch reaches θ or all neighbors are exhausted. Structured assessments go into shared investigation memory M. The final synthesis is constrained by two principles: **signal anchoring** (do not let a locally persuasive branch override stronger initial evidence) and **chain coherence** (the leading candidate should explain downstream symptoms in other explored branches). The output includes support and contradiction fields, which is stronger than a bare rank, but the paper does not show a calibrated probability model or an externally verified evidence locator per claim. (§3.3–3.4; Algorithm 1, PDF pp. 4–5.)

The worst-case bound stated by the paper is O(kΔ), with maximum graph degree Δ, because each of k branches can inspect at most a local neighborhood. This is a bound on the described search shape, not a guarantee of end-to-end wall time or token cost; each investigation is LLM-driven and cost depends on evidence volume and model latency.

## Paper-grounded case

Figure 6 (PDF physical p. 10) follows a CPU-hog case in TrainTicket’s order-service. BARO places the true service fifth and STRIX seventh; the consolidation agent moves it to second. Investigation finds a 3–4× CPU rise without error logs and assigns confidence 0.9. Other explored candidates are rejected with localized evidence: station-service has stable memory despite high structural score (0.85), auth-service has moderate CPU without spikes (0.75), and config-service has stable latency near 9.27 ms and no log anomaly (0.3). The synthesis promotes order-service to rank one. The example illustrates why an anomaly score alone is insufficient: a highly ranked neighbor can be a victim or irrelevant structural hub, while silent saturation may have no error log.

The figure demonstrates a diagnosis path and candidate rejection, not actual repair execution or measured recovery. Its caption reports five investigated candidates while §5.1’s default is k=6; this appears to be a case-specific setup or figure-text mismatch, and the paper does not explain it.

## Data and experimental setup

| Setting | Online Boutique (OB) | TrainTicket (TT) |
|---|---|---|
| Application | E-commerce; 17 services | Ticket-booking system; 69 microservices |
| Reported fault scenarios | 90 | 90 |
| Fault types | CPU hog, memory leak, disk I/O stress, network delay, socket errors, packet loss | Same six |
| Fault generation | Injected faults; paper says three independent repetitions | Injected faults; paper says three independent repetitions |
| Modalities | Metrics, logs, traces | Metrics, logs, traces |
| Target services / observation period / exact Δτ | OB says scenarios span five target services; observation period and numeric Δτ not reported | Target-service count, observation period, and numeric Δτ not reported |

The paper evaluates on RCAEval’s OB and TT microservice benchmarks and additionally reports 100 sampled AegisLab cases covering 25 fault types. The experimental VM is Ubuntu 22.04, 8 physical CPU cores, 16 GB RAM, 500 GB SSD, Python 3.10.12, no GPU. LLM temperature is 1.0. GPT-4.1-mini is the default for main results; seven models are compared on OB. The paper says results average three runs and uses per-incident majority outcomes across three runs for the McNemar comparison. It does not fully clarify how the dataset’s “three independent repetitions” relate to these model-run repetitions. (§5.1–5.3, PDF pp. 6–10.)

## Evaluation design and results

### Root-cause ranking

AC@1 is the share of incidents whose top-ranked pod is the labeled faulty pod; AC@3 checks whether that pod appears in the top three; MRR averages the reciprocal rank of that pod. The paper explicitly says these metrics compare the pod only and do not require the fault type to match, although its problem definition names both pod and failure mode. This is an important task/metric boundary: headline ranking results do not establish fault-type classification accuracy.

Table 1 (PDF physical p. 8; visually checked) reports:

| Dataset | GALA+ AC@1 / AC@3 / MRR | Best non-LLM AC@1 | Best prior LLM AC@1 | Time / total tokens |
|---|---|---:|---:|---|
| OB | 74.44% / 98.89% / 0.854 | CIRCA 66.67% | Flow-of-Action 48.35% | 52.87 s / 32.7K |
| TT | 73.33% / 85.56% / 0.801 | BARO 66.67% | Flow-of-Action 47.78% | 63.16 s / 90.4K |

Thus, the roughly 26-point improvement is against the strongest prior **LLM** baseline; against the strongest non-LLM baseline the AC@1 gains are 7.77 points on OB and 6.66 on TT. GALA+ is not universally cheap: it uses more tokens than Flow-of-Action and can be costly on the larger TT graph, though it uses fewer tokens than RCA-Agent in the OB comparison. These are per-incident paper measurements; token accounting and input/output split are not described.

Table 5 varies the backbone on OB. GPT-4.1-mini yields 74.4% AC@1, 98.9% AC@3, 0.854 MRR, 32.7K tokens, 52.9 s, and $0.022/incident. Llama-4-Maverick yields 77.8%, 97.8%, 0.872, 32.0K, 37.4 s, and $0.003; GPT-4.1 reaches the highest AC@1 (78.9%) and MRR (0.873) but costs $0.110/incident. These reported API costs are experiment-time/provider-specific, not stable current pricing. The authors choose GPT-4.1-mini as the reproducibility default, so the paper does not simply select the highest-accuracy model.

For GALA+ versus Flow-of-Action, the authors report McNemar tests over majority-vote outcomes from three runs: OB has 27 incidents correct only for GALA+ versus 4 only for Flow-of-Action; TT has 35 versus 12; one-sided exact p<0.001. This supports a paired ranking difference on those datasets, not generalization to production or all microservice RCA settings.

### Component and parameter experiments

- Removing STRIX lowers AC@1 from 74.44% to 35.56% on OB and from 73.33% to 68.89% on TT; the gain is dataset-dependent, much larger on OB.
- STRIX alone reaches 51.14% OB and 50.00% TT AC@1. In its internal ablation, dropping instability is most damaging: STRIX AC@1 falls from 51.14% to 18.18% on OB and from 50.00% to 9.09% on TT.
- Replacing the consolidation agent with reciprocal-rank fusion lowers OB AC@1 from 74.44% to 63.33%; replacing the evidence-synthesis agent with threshold-count aggregation also lowers AC@1 to 63.33% and MRR to 0.790. These single-dataset ablations suggest LLM agents contribute beyond simple aggregation on OB, but they are not a broad controlled study of every agent component.
- On TT parameter sweeps, the paper says moderate k, θ around 0.6, and b around 2 perform best. Random neighbor sampling is compared with STRIX-ranked expansion on a 30-case OB subset across five seeds: random achieves AC@1 0.76±0.03, AC@3 0.97±0.02, MRR 0.87±0.02; STRIX-ordering gives 0.72±0.04, 0.98±0.02, and 0.85±0.02. Reusing the same STRIX signal for seed ranking and neighbor expansion may reinforce one bias. (Fig. 4–5, Table 4; PDF pp. 9–10.)

### Report-quality evaluation: SURE-Score

SURE-Score evaluates **generated summaries and recommendations**, not root-cause ranking itself. Its four dimensions are:

1. Evidence Groundedness: reasoning claims supported by observed metrics/logs/traces; penalize unsupported claims.
2. Operational Feasibility: whether actions are concrete and implementable for the system.
3. Diagnostic Precision: specific service/pod names and quantitative impact, not placeholders.
4. Triage Logic: symptoms → pivot evidence → root cause, with a coherent professional investigation order.

Eight Company A SREs (4–10 years’ experience) and four LLMs independently perform think-aloud attribute generation; Qwen3 merges and deduplicates those into binary checklists. A reference report for each case is first generated from the known faulty pod, failure mode, onset, system description, and SRE-authored examples, then manually checked by SREs. Qwen3 and Llama-4-Maverick assess each report against the checklist; criterion positives are aggregated by dimension and rescaled to 1–5. Three SREs separately score 540 reports (90 incidents × 3 methods × 2 datasets).

The paper reports strong ranking agreement but evaluator calibration differs: Qwen3 gives GALA+ overall 3.3 (OB) and 3.0 (TT), while Llama-4-Maverick gives 4.5 and 4.4. Evidence Groundedness diverges especially sharply (Qwen3 1.8/1.4 versus Llama 5.0/4.9); the authors say the former favors explicit telemetry values and the latter accepts paraphrases. Inter-evaluator association is Kendall τ=0.68 and Spearman ρ=0.84 (n=50); automated-vs-human mean scores correlate at ρ=0.92 (n=20). These correlations support ranking/association in the tested report set; they do not prove the checklist’s criteria are complete or scores are calibrated as absolute quality.

The exact final checklist, criterion weighting/rescaling formula, prompts, and SURE scorer were not found in the released repository. The paper describes the process but does not provide enough detail to independently reproduce exact scores. The human reference is built using known ground truth and then expert-reviewed; it is not a second incident-level observation source.

### AegisLab result discrepancy

The main paper says GALA+ is evaluated on 100 AegisLab cases and reports MRR 0.48 and AC@3 0.62 versus Flow-of-Action’s 0.38 and 0.52; it says AC@1 is 30 vs 28 and not statistically significant. The one-page supplementary technical report in the official repository also reports 30/100 versus 28/100 and explicitly says the AC@1 gap is not significant, but labels the method row **GALA**, not GALA+. Until the authors clarify whether this is a naming shorthand or an older system result, the AegisLab result should not be used as definitive evidence for the GALA+ variant. It is a broader-fault-type sample, not evidence that the system solves concurrent or open-set incidents.

## Official artifact repository: static source analysis

The inspected repository README explicitly says the industrial agreement precludes release of the core GALA source. At commit 24d1329d20fb9139f7899a1bed9e8d0bdaf00be0, the repository contains a technical report, annotated evaluation data, sample outputs, and third-party baselines; the system implementation, SURE-Score evaluator, and Flow-of-Action code are not exposed. No code was executed and no benchmark dataset was downloaded.

Available artifacts clarify the paper’s interfaces:

- sample_output/ts-order-service_cpu_1.json shows the initial metric ranking output shape.
- sample_output/ts-order-service_cpu_1_STRIX_output.json contains per-service RRF score, three metric values, and ordinal ranks.
- sample_output/ts-order-service_cpu_1_history_2026-02-27_00-18-33.json records branch candidates, depth, confidence, evidence summary, causal reasoning, supporting factors, and contradictions.
- sample_output/ts-order-service_cpu_1_summarization_recommendation_2026-02-27_00-18-33.json stores the incident summary and three actions. This sample aligns with Figure 6’s order-service CPU case, but sample JSON is not implementation or scorer verification.
- annotation_guidelines.md instructs generation of reference summaries and three recommendations, including “simulate the expected impact” with example CPU/latency/error values. That may introduce unsupported quantitative detail unless every generated reference is subsequently checked against raw telemetry.
- A limited spot-check of the first five rows in data/annotated_dataset.csv found RE2 records whose columns identify Sock Shop/checkoutservice while the summary text says “Train Ticket.” This is an observed artifact inconsistency, not a full dataset audit. The paper says SREs verify reference reports, but the public artifact does not expose a per-row verification trace that resolves this mismatch.
- The repo’s baseline code is vendored third-party implementation and does not reveal GALA’s internal ranking, agent prompts, threshold logic, or SURE scoring.

The repository’s top-level MIT license applies to the published artifact repository; vendored baselines carry their own license notices. The core implementation’s absence means reported system behavior cannot be independently traced to exact executable code.

## Limitations and interpretation

**Authors’ stated limits:** controlled fault injection and predefined fault types may not represent concurrent or complex production failures; all three telemetry modalities are required; dataset-specific prompts need adaptation; cost grows with candidate services and exploration. Future work includes concurrent multi-fault diagnosis and better evidence grounding. (§8–9, PDF p. 11.)

**Reading-based implications, not author claims:**

- The traced service graph bounds exploration but encodes invocation dependency. STRIX centrality and latency heuristics are ranking signals; neither alone establishes causal direction.
- Confidence controls stopping and branch expansion, yet confidence construction/calibration is not specified. A false high-confidence answer may terminate search early.
- Graph-guided reasoning improves localization but does not report tool calls against a live system, executable remediation, or independent post-action recovery checks.
- Report-quality evaluation has useful human involvement, but cross-model score divergence, an undisclosed checklist/scorer, and a spot-checked public-data mismatch limit independent replication.
- AC@k/MRR assess pod match, not the complete pod-plus-failure-mode target definition. Accuracy and report quality are separate outcomes.
- OB/TT provide controlled injected-fault coverage; AegisLab adds fault variety but only a 100-case sample with an unresolved GALA/GALA+ label discrepancy in released materials.

## Relationship to OpsAgent research

- **KRCA:** both use topology to reduce candidate search; GALA+ first fuses independent metrics/trace rankings and adds localized LLM evidence review, whereas KRCA’s staged drilldown uses its own causal skeleton and specialist execution.
- **ToolRCA:** GALA+ supports bounded investigations as a cost/precision trade-off, while ToolRCA’s controlled results caution that tool/query design and model behavior interact. GALA+ does not publish full prompts/tools for direct comparison.
- **OpsAgent and OpsMem:** GALA+’s shared M is temporary within-incident investigation state, not cross-incident operational memory or persistent skill learning.
- **Graph of States:** both expose support/contradiction evidence and synthesis, but GALA+’s paper does not report explicit belief-state lifecycle or backtracking when new evidence invalidates a branch.
- **KnowLution / FlowXpert:** GALA+’s actions are recommendations for SREs; it does not demonstrate the permission checks, execution, or recovery loop described in those operational systems.

This is a useful middle point in the OpsAgent map: richer than static ranking and report generation, more constrained than open-ended tool use, but not a verified autonomous remediation system.

## Relevance to Network AIOps

Potentially transferable:

- Keep candidate generation and investigation separate; fuse metric and trace evidence with explicit provenance instead of flattening every modality into one score.
- Use physical/logical topology to bound candidate expansion, but preserve direction, alternate paths, and support/contradiction evidence. Do not equate network adjacency with causality.
- Preserve evidence in its native representation and connect each explanation claim to a time window and source record.
- Evaluate diagnosis separately from report quality and action safety. Report evidence support, recommendation feasibility, and recovery verification as distinct outcomes.

Not directly transferable without new evidence: PageRank fan-in/fan-out assumptions on network topology, service-trace self-time decomposition, injected single-fault labels, and remediation recommendations evaluated on microservice architectures.

## Open questions

1. What is the mapping between service-level graph nodes, pod-level RCA labels, and fault-type output during final ranking?
2. How are consolidation/investigator confidence values produced and calibrated, and how do prompts constrain the model?
3. Does the actual implementation expand only one hop, as Algorithm 1 appears to show, or recurse beyond the printed pseudocode?
4. What is the SURE-Score checklist, rescaling formula, and scorer implementation? Can another team reproduce its scores?
5. Why does the supplementary AegisLab table label the result GALA while the main text attributes it to GALA+?
6. Were the public reference reports corrected for the observed RE2 service-name mismatch and simulated impact values?
7. How does GALA+ behave with missing traces/logs, cyclic dependencies, multiple simultaneous root causes, or an unknown fault type?
8. Do recommendations reduce MTTR or improve recovery when safely executed, rather than only scoring well as text?

## Source grounding map

| Topic | Primary locator |
|---|---|
| Problem, contribution, root-cause definition | Abstract and §§1–2, PDF pp. 1–2 |
| Four-phase architecture | Figure 2, PDF p. 3 |
| BARO and STRIX scores / RRF | §3.1, PDF pp. 3–4 |
| Telemetry context construction | §3.2, PDF p. 4 |
| Graph investigation and final synthesis | §§3.3–3.4 and Algorithm 1, PDF pp. 4–5 |
| SURE-Score framework | Figure 3 and §4, PDF pp. 5–6 |
| Data, baselines, models, and metrics | §§5.1–5.2, PDF pp. 6–7 |
| Ranking and SURE results | Tables 1–3, PDF pp. 8–9 |
| Ablations | Figure 4 and Table 4, PDF p. 9 |
| LLM, cost, parameters, case | Table 5 and Figures 5–6, PDF p. 10 |
| Validity threats and data availability | §§8–9, PDF p. 11 |
| Public artifacts and annotation procedure | Official repository README, annotation_guidelines.md, data/annotated_dataset.csv, and sample_output/ at the commit above |

## Tags

AIOps · OpsAgent · microservice RCA · metrics/logs/traces · dependency graph · STRIX · agentic diagnosis · SURE-Score · incident response · evidence grounding
