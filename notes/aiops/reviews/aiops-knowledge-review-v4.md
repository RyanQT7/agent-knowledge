# AIOps Knowledge Review v4 — LLM-Driven Microservice Anomaly Generation

Status: Completed for the six papers with accessible full text; AMulSys remains metadata-only / pending.

## Scope

Formal notes reviewed:

- [TraceLLM](../../../papers/aiops/tracellm/notes.md)
- [LLM-AP](../../../papers/aiops/llm-ap-synthetic-augmentation/notes.md)
- [Synthetic Time Series for Anomaly Detection in Cloud Microservices](../../../papers/aiops/synthetic-cloud-microservices/notes.md)
- [GenIAS](../../../papers/aiops/genias/notes.md)
- [MODIFy](../../../papers/aiops/modify/notes.md)
- [AIOpsLab](../../../papers/aiops/aiopslab/notes.md)

[AMulSys](../../../papers/aiops/amulsys/availability.md) was identified as relevant by title and bibliographic metadata but its full text was not legally accessible from the verified publisher route. It is excluded from method-level conclusions.

## Evidence convention

- **Paper-backed fact** names a method or result reported in the full paper and cites its section / figure / table / equation.
- **Experiment support** states only what the evaluation measured.
- **Cross-paper synthesis** compares several notes.
- **Knowledge-base analysis** is an interpretation or untested transfer question, not an author claim.

## 1. What the papers actually do

| Paper | Main task | Generated object / system output | Evidence scope |
| --- | --- | --- | --- |
| TraceLLM | Conditional microservice call-graph generation | Hierarchical Trace DAG and edge attributes | Structure / condition validity, selected graph distributions and downstream graph-task utility (PDF §§3–4, Figs. 3–7) |
| LLM-AP | Univariate TS anomaly augmentation | Continuous-valued windows edited by frozen GPT models | Rule-filter pass counts and F1 on NAB detector configurations; no cross-domain real-fault evaluation (PDF §§3–4, Table 8) |
| Synthetic Time Series | Cloud microservice dataset construction | Dynamic workload, configured load anomaly / FIS fault, measured telemetry | 470 metrics, time-aligned injection labels and illustrative effects; no detector benchmark (PDF §§3–5, Tables 1–3, Figs. 5–6) |
| GenIAS | General TS anomaly augmentation | VAE-generated latent perturbations patched into numeric windows | ARP / EDI and downstream detector results on nine benchmarks (PDF §§3–4, Tables 1–4) |
| MODIFy | Multimodal detection and service RCA | Anomaly score and service-root ranking | F1 / HR / NDCG on SocialNetwork and TrainTicket, module ablations and added-noise robustness (PDF §§5.6–5.12, Tables 4–7, Figs. 5, 8) |
| AIOpsLab | Live cloud Agent evaluation | Executed tasks and operational observations | Task accuracy across selected 48 scenarios; two normal no-op tasks expose false positives (PDF §3, Table 3, §3.6.4) |

The central boundary is that **generation, injection, detection, diagnosis and Agent evaluation are distinct tasks**. A paper can contribute to the research environment without being an anomaly generator.

## 2. Cross-paper relationships

### LLM versus classical generators

**Paper facts:** TraceLLM uses Llama-2 7B, domain continued pretraining and LoRA to generate structured Trace graphs. LLM-AP prompts frozen GPT-3.5 / GPT-4o to revise single-variable numeric windows. GenIAS uses a TCN-VAE latent perturbation generator. Synthetic Time Series and AIOpsLab configure workloads / faults in running services without using an LLM as the sample generator.

**Synthesis:** The phrase “LLM-driven anomaly generation” applies narrowly to LLM-AP for numerical anomalies, and more broadly to TraceLLM only if “Trace generation” is counted as operational-data generation. TraceLLM’s call graph does not encode a fault by default. GenIAS is a direct method comparator for numerical synthesis, while live fault injection is a different form of sample acquisition.

### Direct value generation versus fault mechanism realization

LLM-AP directly outputs a numeric sequence; GenIAS decodes latent perturbations into sequence values. Neither conditions on a microservice root-cause action. Synthetic Time Series and AIOpsLab instead act on system components (for example CPU stress, network delay / loss, process or configuration changes) and observe the resulting service behavior. Their injected label identifies a controlled action / target, not every possible production cause.

This distinction matters because a plausible-looking KPI window can still fail to correspond to a realizable fault, and a real injected fault may have a narrow observable footprint in a specific testbed.

### Single-modal versus multimodal generation / use

- TraceLLM outputs Trace structure only.
- LLM-AP and GenIAS output numeric time-series windows only.
- Synthetic Time Series collects multiple operational signals from one running testbed but does not generate a joint synthetic Trace–Metric–Log tuple or measure modality agreement; its 2024 paper reports metrics / logs and no Trace dataset.
- AIOpsLab gathers multimodal observations in a shared runtime environment, but its purpose is Agent task evaluation.
- MODIFy consumes aligned logs, metrics, and traces. Its 6-second aggregation and MSCA-CGFM are feature alignment / fusion, not multimodal generation (PDF §§4.1–4.3).

No full-text-read paper in this batch demonstrates a generative model that jointly produces Metric, Trace and Log from the same fault mechanism and then verifies cross-modal agreement.

### Statistical resemblance versus mechanism fidelity

Validation targets form separate layers:

1. **Syntax / structure** — TraceLLM checks valid DAG and requested size / depth; LLM-AP checks JSON, length and subtype rules.
2. **Local pattern / distribution** — LLM-AP uses RelDTW plus z-score, CUSUM and shape rules; GenIAS uses ARP and EDI. These measure selected similarity / diversity properties, not causal truth.
3. **Downstream utility** — TraceLLM’s synthetic graph training is close to real-data training on a specific call-graph task; LLM-AP improves some NAB detectors but hurts Autoformer; GenIAS improves several benchmark scores. Utility is model- and dataset-dependent.
4. **Intervention-grounded behavior** — the cloud dataset and AIOpsLab induce controlled changes in live services and associate observations with configured actions. This is stronger evidence of a realizable intervention than independent waveform editing, but still limited to benchmark systems / fault templates.
5. **Cross-modal diagnosis** — MODIFy shows multimodal observed features help detection / localization in its two datasets; it does not test the realism of generated multimodal samples.

Consequently, no single validation score in this group should be called “realism” without specifying its target.

## 3. Normal business variation and real faults

### Paper-backed facts

- Synthetic Time Series generates normal service demand from piecewise trends, multiple periodic terms and noise (PDF §3.2, Eqs. 1–2). It separately applies interval-wise load multipliers as load anomalies and uses FIS for infrastructure faults (PDF §§3.3–3.4, Algorithms 1–2).
- AIOpsLab includes two no-op normal-workload tasks. Only GPT-4-W-Shell recognizes them as normal; other evaluated Agents false-positive them (PDF §3.6.4, p.9). This is evidence of a specific failure in a very small normal-task slice, not a general rate estimate.
- LLM-AP conditions on local normal / anomaly windows and six shape classes, but does not encode the business reason for a change (PDF §§3.1–3.2).
- MODIFy injects noise in the test set to evaluate robustness. That is not a workload / release change experiment (PDF §5.12, Fig. 8).
- In the existing TSAD corpus, When Model Meets New Normals studies test-time adaptation to new normal distributions; CAPMix studies robust KPI detection in noisy / dynamic settings and softens uncertain synthetic labels; CAROTS creates causality-preserving and causality-breaking augmentations. Their assumptions and evidence are described in their respective notes and TSAD reviews.

### Current synthesis

The papers include useful components—normal workload curves, no-op labels, dynamic-normal adaptation, causal-preserving augmentation and robustness-to-noise tests—but they do not establish a complete source-aware separation of legitimate business changes from faults. A key evaluation gap **within the evidence reviewed here** is a controlled comparison of: normal workload/state shift only; fault only; both together; and a valid but previously unseen normal state, with service-context / telemetry ground truth.

This is an evidence gap in the reviewed set, not proof that no published system addresses it.

## 4. What is not established

1. A high structure or shape validity score establishes fault-mechanism realism.
2. LLM-generated Trace calls encode causal propagation or correspond to a known injected incident.
3. A detector F1 increase in NAB / UTS establishes gains on true microservice incidents.
4. Metric–Trace–Log records from separate generators are temporally and causally consistent.
5. Noise robustness establishes robustness to a legitimate deployment, workload or topology transition.
6. Detection / RCA gains on SocialNetwork and TrainTicket imply production deployment readiness or multi-root localization.
7. AIOpsLab task accuracy evaluates the realism of generated samples; its target is Agent task completion.
8. AMulSys method details can be reconstructed from its abstract or MODIFy’s baseline table; the full text remains pending.

## 5. Current mental model

The following is a cross-paper abstraction, not a shared architecture:

Real workload context + service topology
→ choose either a numeric / structural generator or a runtime fault intervention
→ collect / construct the target telemetry
→ validate syntax, time alignment, distribution, fault mechanism and cross-modal agreement separately
→ evaluate downstream detection / localization on held-out real observations and an appropriate live testbed.

Existing papers cover different parts of this chain. No single paper in the completed set covers all stages.

## 6. Open questions

1. Can workload and release context be used to annotate a change as an expected state transition without incorrectly masking a concurrent fault?
2. What evidence is needed to establish that generated Metric / Trace / Log reflect the same injected service-level mechanism?
3. How much of LLM-AP’s detector gain survives under train-synthetic / test-real separation, fixed false-positive budgets and multivariate KPI settings?
4. Can TraceLLM’s conditional graph generation be grounded in a real testbed’s known topology and checked against injected fault propagation?
5. How should “normal no-op” coverage scale beyond two tasks, across benign demand changes and unknown valid modes?
6. Does MODIFy’s feature denoising help under real sampling loss and traffic shifts, or only under the tested injected-noise levels?
7. Which AMulSys augmentation / graph mechanisms and data splits are documented in the full paper? Await the lawful full text before answering.

## 7. Next learning priorities

1. Obtain lawful AMulSys full text, then compare its augmentation and hybrid graph mechanisms with MODIFy.
2. Use the existing [TSAD 33-paper synthesis](../../reviews/tsad-final-synthesis.md) and its linked notes for evidence on new-normal adaptation, noisy augmentation, causality and open-set behavior.
3. Keep data-generation work distinct from the later model / experiment design stage; this review reports existing capabilities and evidence only.

## Sources

See the six formal notes above for per-claim PDF section and page references. Topic inventory and AMulSys access status are in [the topic map](../llm-microservice-anomaly-generation.md) and [source download report](../../../sources/papers/llm-microservice-anomaly-generation/download_report.md).
