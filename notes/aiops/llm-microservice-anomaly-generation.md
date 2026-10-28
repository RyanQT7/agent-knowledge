# LLM-Driven Microservice Anomaly Generation

Status: 6 papers full-text read and documented; AMulSys metadata recorded, full text pending.

## Scope and evidence policy

This topic examines LLM-generated samples, microservice fault mechanisms, Metric / Trace / Log relations, fault injection and validation of generated data. It is deliberately broader than “LLM anomaly generator”: several included papers are runtime testbeds or multimodal detectors, not generators. The original 33-paper collection at sources/papers/tsad-2024-2026 remains separate and unchanged.

Claims are separated as:

- **Paper fact**: method / result reported by the paper, referenced by section, page, figure, equation, or table.
- **Experiment evidence**: what the reported evaluation actually measured.
- **Knowledge-base analysis**: scope boundaries or potential transfer questions; not an author conclusion.

## Paper inventory and reading status

| ID | Paper | Publication | Source / full-text status | Note | Card | Dossier |
| --- | --- | --- | --- | --- | --- | --- |
| tracellm | Large Language Models as Realistic Microservice Trace Generators | EMNLP 2025 | ACL Anthology PDF; read | [Note](../../papers/aiops/tracellm/notes.md) | [Card](../../papers/aiops/tracellm/knowledge-card.md) | [Dossier](../../papers/aiops/tracellm/knowledge-dossier.md) |
| llm-ap-synthetic-augmentation | LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation | Applied Sciences 16(14), 6851 (2026) | Open publisher PDF; read | [Note](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md) | [Card](../../papers/aiops/llm-ap-synthetic-augmentation/knowledge-card.md) | [Dossier](../../papers/aiops/llm-ap-synthetic-augmentation/knowledge-dossier.md) |
| synthetic-cloud-microservices | Synthetic Time Series for Anomaly Detection in Cloud Microservices | MLDS 2024 paper; arXiv:2408.00006 | Author PDF; read | [Note](../../papers/aiops/synthetic-cloud-microservices/notes.md) | [Card](../../papers/aiops/synthetic-cloud-microservices/knowledge-card.md) | [Dossier](../../papers/aiops/synthetic-cloud-microservices/knowledge-dossier.md) |
| amulsys | Anomaly Detection for Microservice System via Augmented Multimodal Data and Hybrid Graph Representations | Information Fusion 118, 103017 (2025) | Publisher full text paywalled; pending, no method-level reading claimed | [Availability record](../../papers/aiops/amulsys/availability.md) | — | — |
| genias | GenIAS: Generator for Instantiating Anomalies in Time Series | arXiv:2502.08262v2 (2026-02-05) | Public preprint; read | [Note](../../papers/aiops/genias/notes.md) | [Card](../../papers/aiops/genias/knowledge-card.md) | [Dossier](../../papers/aiops/genias/knowledge-dossier.md) |
| modify | A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices | JSS 237, 112844 (2026) | JSS-associated author PDF; read | [Note](../../papers/aiops/modify/notes.md) | [Card](../../papers/aiops/modify/knowledge-card.md) | [Dossier](../../papers/aiops/modify/knowledge-dossier.md) |
| aiopslab | AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds | MLSys 2025 | Official proceedings PDF; read | [Note](../../papers/aiops/aiopslab/notes.md) | [Card](../../papers/aiops/aiopslab/knowledge-card.md) | [Dossier](../../papers/aiops/aiopslab/knowledge-dossier.md) |

Original metadata and PDF acquisition record: [CSV](../../sources/papers/llm-microservice-anomaly-generation/papers.csv) · [download report](../../sources/papers/llm-microservice-anomaly-generation/download_report.md).

## Comparison: generation target, realism, and evidence

| Paper | Modality / output | Uses LLM? | What is generated / built | Fault knowledge | Cross-modal consistency | Normal variation | Realism check and downstream evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TraceLLM | Trace call DAG | Yes, Llama-2 7B + LoRA | Structured invocation graph; can condition edge count, depth, rare communication, latency | No explicit fault cause or injection action | No Metric / Log output | Not explicitly modeled as normal business state | DAG / condition validity, distribution distances, and downstream graph-task utility; does not establish fault realism or detector gain |
| LLM-AP | Univariate numeric window | Yes, frozen GPT-3.5 / GPT-4o | Rewrites numeric values to target anomaly type | No microservice or causal fault knowledge | No | Context windows are retained as prompt examples; not workload-state semantics | RelDTW / z-score / CUSUM / subtype gates; F1 gain on some NAB detectors, decline on Autoformer; no train-synthetic/test-real validation |
| Synthetic Time Series | Live metrics and collected logs in two cloud applications | No | Generates workload and injects CPU / memory / network / I/O / pod faults; telemetry is measured from running services | Yes, configured fault action and target; not necessarily business cause | Co-occurring telemetry follows a shared live system, but no Metric–Trace generator or cross-modal consistency metric; Trace not reported | Yes: trend, multiple periodic components, and noise; load anomalies separately multiplier-injected | Injection-to-metric examples and explicit time labels; no detector comparison or synthetic realism score |
| AMulSys | Claimed multimodal + hybrid graph, details unknown | Unknown | Unknown pending lawful full text | Unknown | Unknown | Unknown | No knowledge claim beyond bibliographic metadata / title-level relevance |
| GenIAS | Univariate and multivariate numeric windows | No; TCN-VAE | Perturbs normal latent space, decodes candidate anomalies, patches selected variable dimensions | No operational fault semantics | No | Learns normal sequence distribution but not explicit business state / workload context | ARP / EDI plus detector F1 on 9 benchmarks; no microservice or causal validation |
| MODIFy | Log + Metric + Trace as detector inputs | No | No anomaly samples generated; consumes aligned telemetry for detection and root-cause ranking | Supervised anomaly and service-root labels, but no generated fault mechanism | Consumes aligned modalities; does not generate jointly | No explicit workload / release condition | Detection / localization metrics and injected-noise robustness; does not validate synthetic data |
| AIOpsLab | Live metrics, logs, traces, configuration and tool observations | LLM agents are evaluated, not a generator | Deploys workloads and injects actual faults into testbed services | Yes, controlled fault configs / oracle labels incl. symptomatic and functional cases | Modalities are observed from a shared running environment, not synthesized independently | Includes two no-op normal tasks; limited evidence for complex normal fluctuation | Task success and Agent interaction; two no-op tasks reveal false positives; not sample-generation or detector-gain evaluation |

The table distinguishes generated call structure, generated numerical values, controlled live fault execution and multimodal diagnosis. Calling all four “LLM anomaly generation” would obscure the papers’ different outputs and proof targets.

## Cross-paper mechanisms and evidence boundaries

### 1. Direct numeric generation versus Trace structure versus runtime fault injection

- **Direct numeric changes**: LLM-AP is the only included work in which an LLM edits continuous-valued anomaly windows. GenIAS does numerical generation too, but via VAE latent perturbation rather than LLM.
- **Trace structure generation**: TraceLLM predicts service invocation graph structures and attributes. A rare or high-latency call condition does not by itself represent an injected fault.
- **Fault action in a live service**: Synthetic Time Series and AIOpsLab apply controlled system / workload actions and collect resulting runtime observations. They do not let an LLM freely invent correlated Metric / Trace / Log samples.
- **Multimodal diagnosis**: MODIFy aligns and fuses observed Metric, Trace and Log. Its diffusion component is a Trace feature denoising / robustness mechanism, not a sample generator. AMulSys may be a related multimodal detector, but this collection cannot state its method until the full text is available.

### 2. What “realistic” is checked to mean

Validation strength is target-specific:

1. **Output format / structure**: TraceLLM checks graph validity and structural conditions; LLM-AP checks parseability, length and anomaly pattern.
2. **Local statistical or representation similarity**: LLM-AP uses RelDTW and rule features; GenIAS uses ARP / EDI. Passing such tests does not establish causal or domain-mechanism fidelity.
3. **Task utility**: TraceLLM tests downstream call-graph tasks; LLM-AP and GenIAS report gains for some anomaly detectors. LLM-AP’s Autoformer regression shows detector dependence.
4. **Mechanism-grounded system response**: Synthetic Time Series and AIOpsLab execute known fault actions and observe resulting service telemetry. This provides a stronger link between intervention and measurements than isolated sequence editing, but the selected testbeds do not prove production-wide coverage.
5. **Multimodal diagnosis utility**: MODIFy tests detection and service localization on paired multimodal datasets, but it measures classifier performance / noise sensitivity rather than consistency of generated cross-modal samples.

No one validation level substitutes for the others. In particular, detector F1 uplift does not independently prove a generated sample corresponds to a real root cause.

### 3. Normal business variation and faults

**Paper facts**:

- Synthetic Time Series explicitly builds trends, multiple periodic load components and noise into normal workload; its “load anomaly” is a separate interval-wise demand multiplier. It also separately injects infrastructure faults (PDF §§3.2–3.4).
- AIOpsLab has two no-op tasks where an Agent should not identify a fault. Only GPT-4-W-Shell recognizes the normal workload in those tasks; other tested Agents produce false positives (PDF §3.6.4, p.9). The number and type of normal tasks are limited.
- LLM-AP uses local normal context windows and anomaly subtype filters, but does not label workload transitions or operational causes.
- MODIFy’s robustness tests add noise to test data; that is not an evaluation of legitimate business state changes.
- In the existing TSAD collection, [When Model Meets New Normals](../../papers/when-model-meets-new-normals/notes.md) adapts to new normal distributions, [CAPMix](../../papers/capmix/notes.md) addresses noisy / dynamic KPI settings and pseudo-anomaly label reliability, and [CAROTS](../../papers/carots/notes.md) contrasts causality-preserving and causality-breaking augmentations. These are complementary mechanisms, not proof of source-aware microservice load-vs-fault discrimination.

**Cross-paper synthesis**: Current evidence contains pieces of the distinction—normal load dynamics, no-fault tasks, dynamic-normal adaptation, noisy augmentation and causal-relationship perturbation—but the set does not report one controlled matrix that separates normal demand shift, infrastructure failure, both together, and unknown but valid operating modes using workload / topology / trace ground truth.

### 4. Cross-modal consistency

Synthetic Time Series and AIOpsLab let several telemetry streams arise from a shared running application and a controlled injection. MODIFy shows that aligned Metric / Log / Trace features support detection and localization in two benchmarks. TraceLLM generates only call structure; LLM-AP and GenIAS generate only numeric series. Thus, within the available evidence, **no included generative model is shown to jointly produce Metric, Trace and Log conditioned on the same fault mechanism and verify that the modalities agree**. This is a bounded observation about this collection, not a claim about all published literature.

## Reading routes

### By mechanism

1. [Synthetic Time Series](../../papers/aiops/synthetic-cloud-microservices/notes.md): live fault and load construction.
2. [AIOpsLab](../../papers/aiops/aiopslab/notes.md): testbed, fault oracle and Agent evaluation.
3. [TraceLLM](../../papers/aiops/tracellm/notes.md): LLM-generated call graphs.
4. [LLM-AP](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md) and [GenIAS](../../papers/aiops/genias/notes.md): direct numeric sequence generation, LLM versus VAE.
5. [MODIFy](../../papers/aiops/modify/notes.md): multimodal detection / diagnosis, not generation.

### Cross-topic comparators

- [CAPMix](../../papers/capmix/notes.md): synthetic KPI perturbation, soft pseudo-label revision, input / latent mixup, and a dynamic AIOps deployment case.
- [CAROTS](../../papers/carots/notes.md): causal-preserving normal versus causal-breaking pseudo-anomaly augmentation.
- [When Model Meets New Normals](../../papers/when-model-meets-new-normals/notes.md): test-time adaptation under normal distribution shift.
- [TSAD 33-paper synthesis](../reviews/tsad-final-synthesis.md) and [TSAD query guide](../guides/tsad-knowledge-query-guide.md): wider anomaly-modeling, robustness and evaluation context.

## Knowledge-query entry

Start with this topic map, then follow each paper’s detailed note and dossier. For exact numerical results or author-stated limitations, use the evidence locations in the paper note and the original PDF path in the dossier. The dossiers also provide structured records for export and scripted retrieval. Query prompts that fit this collection:

- Which papers generate numeric anomalies, which generate traces, and which inject real service faults?
- Which evaluations test structure, statistical resemblance, downstream detector gain, or mechanism-grounded realism?
- What evidence distinguishes business load variation from infrastructure fault?
- Which work jointly generates multiple observability modalities, and what is still unknown?

## Research proposal analysis

For analysis of LLM-planned microservice faults, Metric–Trace consistency, and separation of healthy workload variation from service degradation, use:

- [Self-contained research overview](llm-microservice-research-overview.md)
- [Literature survey and novelty overlap](llm-microservice-anomaly-generation-survey.md)
- [Candidate technical designs and recommendation](llm-metric-trace-generation-design.md)
- [Minimum experiment plan](llm-metric-trace-experiment-plan.md)
- [Novelty boundaries and candidate contributions](llm-microservice-research-novelty.md)

These reports synthesize this topic with the 33-paper TSAD collection. They distinguish paper facts, experiment evidence, and research hypotheses. The current knowledge base has no verified schema document for the State Grid project’s Metric / Trace data; its data-field status is therefore recorded as unknown, not missing.

## Export package

Standalone knowledge export: [README](../../exports/llm-microservice-anomaly-generation/README.md), [full knowledge Markdown](../../exports/llm-microservice-anomaly-generation/llm-microservice-anomaly-generation-knowledge.md), [overview](../../exports/llm-microservice-anomaly-generation/llm-microservice-anomaly-generation-knowledge-overview.md), [JSONL](../../exports/llm-microservice-anomaly-generation/llm-microservice-anomaly-generation.jsonl), [cross-paper comparison](../../exports/llm-microservice-anomaly-generation/comparison.md).
