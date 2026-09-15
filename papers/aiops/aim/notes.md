# Leveraging LLMs for Alert Summarization and Mitigation Plan Generation

## 1. Metadata

- Title: Leveraging LLMs for Alert Summarization and Mitigation Plan Generation
- Authors: Komal Sarda, Honggeun Ji, Amr M. Zaki, Marin Litoiu, Larisa Shwartz, and Ian Watts
- Year: 2026
- Venue: FSE Companion '26
- URL / DOI: https://doi.org/10.1145/3803437.3805255
- Local File: [Source PDF](../../../sources/papers/AIOps_papers/FSE26-Leveraging%20LLMs%20for%20Alert%20Summarization%20and%20Mitigation%20Plan%20Generation.pdf)
- Paper ID: aim

## 2. One-Sentence Summary

AIM uses time-aligned metrics, logs, traces, and alerts plus adaptive in-context exemplars to generate an alert summary, root-cause category indication, and mitigation plan, then explores translating the plan into Ansible code; its controlled evaluation shows useful language and plan quality but only limited actual remediation success.

## 3. Problem Setting

Cloud-native microservices emit large volumes of logs, metrics, traces, and alerts. Alert storms can leave SREs with redundant or fragmented context, while static SOPs do not always provide actionable recovery steps for changing systems. AIM tries to unify alert summarization, RCA-oriented interpretation, mitigation planning, and a partial plan-to-code path in one privacy-aware workflow (Source: Sec. 1–3).

The paper’s problem is broader than alert detection but narrower than a fully autonomous incident-management system. It assumes labeled anomalous intervals and focuses on interpreting the resulting alert context, producing summaries and plans, and testing whether plans can become executable remediation scripts (Source: Sec. 3.1, Sec. 4.1–4.3).

## 4. AIOps Task

- Detection: **No new detector.** Alerts are synthesized from labeled anomalous windows using rule-based threshold representations (Source: Sec. 3.1–3.2).
- RCA: **Yes, category-level inference.** The study measures alignment with root-cause categories rather than a general open-set root-node search.
- Localization: **Unclear / not the primary reported output.** The output is a summary, fault-category signal, and plan; exact component localization is not defined as the main metric.
- Diagnosis: **Partial.** The model reasons over fault context and labels/mentions root-cause categories.
- Prediction: No.
- Remediation: **Plan generation and controlled execution feasibility.** Ansible playbooks are generated and run in a Robot Shop testbed, but fully autonomous remediation is explicitly outside the original scope (Source: Sec. 3, Sec. 3.4, Sec. 4.4.6).

## 5. Failure / Incident Setting

The setting is cloud-native microservice applications with anomalies such as CPU or memory saturation, login errors, and other labeled fault categories. AIM treats an alert as a compact operational trigger derived from multimodal observations. It is evaluated on MicroSS and MSDS data and on a Robot Shop microservice testbed for plan execution (Source: Sec. 4.1, Sec. 4.4.6).

The paper uses realistic or public data sources, but its execution evaluation is controlled and fault-injected. It does not report deployment in a live production incident workflow (Source: Sec. 4.3, Sec. 6).

## 6. Data Modalities

- Metrics: Yes; fixed-interval KPIs such as CPU and response time are aggregated and thresholded.
- Logs: Yes; timestamps, levels, and message content are parsed, with high-severity entries emphasized.
- Traces: Yes; traces are synchronized with service timestamps and summarized using status-code frequency and maximum response time.
- Alarms: Yes; alerts are synthesized from anomalous intervals and included in the prompt.
- Topology: **Unclear / not explicit.** Service identifiers and dependencies are present in the data description, but no topology graph or topology-based constraint is defined.
- Traffic: Unclear / not explicitly stated in the paper.
- NetFlow: Unclear / not explicitly stated in the paper.
- Configuration: Used indirectly in mitigation plans and Ansible execution; a complete configuration-observation modality is not defined.
- Tickets: Unclear / not a named primary input.
- Other: Root-cause labels, SRE-written summaries and mitigation plans, historical prompt-summary-mitigation exemplars.

**Single-modal / Multi-modal:** Explicitly multi-modal over metrics, logs, traces, and alerts. The paper performs preprocessing and timestamp/service-identifier alignment, then combines the representations at prompt/context level rather than presenting a feature-level neural fusion model (Source: Sec. 3.1–3.2).

## 7. Dataset and System Setting

- Public / Private: MicroSS and MSDS are described as publicly available research datasets; the on-premise IBM incident data / fine-tuning data are proprietary and not released. The paper also uses a Robot Shop testbed (Source: Sec. 4.1–4.2, Sec. 6).
- Production / Synthetic: Historical or curated incident data plus injected faults in a controlled microservice testbed; not a live production deployment.
- Observation duration: MicroSS covers two weeks; the observation duration for MSDS and the Robot Shop experiments is not explicitly stated in the local paper (Source: Sec. 4.1).
- Number of incidents: The controlled evaluation selects 50 samples from each dataset, with 13 ICL training incidents and 37 test incidents per dataset, for 100 total samples (Source: Sec. 4.3). The full source corpora are larger, but their incident count is not reported here.
- Number of devices / services / nodes: MicroSS includes five named services plus ZooKeeper; a comparable MSDS service/node count is not explicitly stated (Source: Sec. 4.1).
- Topology: Service identifiers and dependencies are part of the microservice context, but no explicit graph size or graph-based RCA mechanism is reported.

## 8. Core Method

AIM has three main stages:

1. **Data Integration and Mapping:** clean, synchronize, and serialize metrics, logs, traces, and alerts; aggregate KPIs and represent severity with robust percentile thresholds.
2. **Prompt Engineering:** include task instructions, selected KPI deviations, alert descriptions, and relevant log/trace snippets. Low-severity KPIs are omitted to reduce noise and tokens.
3. **Adaptive In-Context Generation:** encode historical prompt-summary-mitigation triplets, retrieve semantically similar examples, and let a controller choose the number/order/template of exemplars before invoking an LLM.

The generated output is a JSON-like alert summary plus mitigation plan. In the plan-to-code extension, a separate code-generation LLM translates the plan into an Ansible playbook, which receives lightweight YAML and namespace validation before controlled execution (Source: Sec. 3.1–3.4).

## 9. Architecture / Workflow

The paper frames the system with MAPE-K and an Observe–Analyze–Plan–Act flow:

```text
Raw metrics / logs / traces
→ time and service alignment
→ KPI extraction and rule-based severity alerts
→ adaptive retrieval of historical exemplars
→ LLM alert summary + RCA-category interpretation + mitigation plan
→ code-generation LLM
→ Ansible playbook validation
→ controlled Robot Shop execution
→ pre/post metric observation
```

The “Plan” component generates a plan and the “Act” component generates/exercises code. This is a plan-first, planner–executor-like decomposition. However, the paper does not show a repeated observation → replanning → action loop for a live incident; execution is a feasibility extension in a controlled environment (Source: Sec. 3, Fig. 1, Sec. 3.4, Sec. 4.4.6).

## 10. Detection Method

AIM does not propose a new anomaly detector. It converts labeled anomalous intervals into alert inputs and applies rule-based KPI thresholding: values below the 25th percentile are low, values between the 25th and 75th percentiles are medium, and values above the 75th percentile are high. Only medium/high-severity KPIs are placed in the prompt (Source: Sec. 3.1–3.2).

This makes the alert representation a symbolic prior for the LLM, but alert generation and RCA evaluation remain separate: a threshold violation is not itself a root-cause finding.

## 11. RCA / Localization Method

The model receives a time-aligned, prompt-level representation of logs, metrics, traces, and alert semantics. It is asked to infer root-cause categories and to express the relevant operational context in a summary and mitigation plan. The evaluation uses Precision Alignment (PA), exact matching against predefined root-cause labels, and Token Alignment (TA), token-level overlap with the intended fault terminology (Source: Sec. 4.3–4.4.3).

The candidate space is the set of labeled root-cause categories represented in the selected datasets. The paper does not define a candidate list of all services, devices, interfaces, or causal nodes, nor does it report candidate generation/pruning or topology-based root ranking. Therefore, its RCA result should not be read as a general physical root-cause localization protocol.

## 12. Diagnosis / Classification Method

Diagnosis is implicit in joint summary and plan generation. The system uses structured alerts, high-severity KPI context, and retrieved historical examples to help the LLM reproduce the relevant root-cause category in the summary and propose an action sequence. DeepSeek-V3 reaches 77.42% PA / 95.16% TA on MSDS and 56.67% PA / 78.33% TA on MicroSS under the reported adaptive setting; GPT-4o is lower on PA in that comparison (Source: Table 3, Sec. 4.4.3).

These scores indicate label/term alignment, not proof that the generated explanation identifies a unique causal root. The paper also measures lexical and semantic similarity of summaries/plans, which should be interpreted as output alignment rather than direct RCA correctness.

## 13. LLM / Agent Role

### Paper terminology

The paper calls the framework **Agentic Incident Mitigation (AIM)** and describes an agentic Plan→Act workflow within a MAPE-K framing (Source: Abstract, Sec. 3).

### Capability analysis

- LLM Used: **Yes.** GPT-4o, DeepSeek-V3, LLaMA-3-70B, and IBM WatsonX/on-premise models are evaluated or discussed (Source: Abstract, Sec. 4.2, Sec. 7).
- Tool Use: **Limited / execution-oriented.** Historical exemplar retrieval uses a SentenceTransformer embedding search; the plan-to-code stage emits Ansible playbooks, which are validated and run in the Robot Shop testbed. The LLM is not shown autonomously selecting a diverse set of live telemetry query tools.
- Multi-step interaction: **Pipeline-level yes; runtime interaction unclear.** Data preparation, generation, code validation, and execution are sequential, but a repeated tool-observation dialogue is not established.
- Planning: **Explicit plan generation.** A step-by-step mitigation plan is generated and then handed to a separate code-generation/execution stage. This is plan-first orchestration, not evidence of dynamic replanning.
- Memory: **Context/example retrieval, not established Agent memory.** The historical prompt-summary-mitigation corpus is encoded and retrieved for adaptive ICL. The paper does not define episodic memory writes, cross-incident memory policy, forgetting, or long-term state.
- Feedback loop: **Partial.** Pre/post execution metrics, LLM-as-a-judge scoring, and human SRE evaluation provide feedback for evaluation; an online controller that revises its plan from new observations is not shown.
- Environment interaction: **Yes, but controlled and partial.** Generated Ansible scripts execute in the Robot Shop fault-injection environment; fully autonomous remediation is outside the stated scope.
- Autonomous next-action selection: **Limited.** The system selects/retrieves exemplars adaptively and generates a plan, but script execution is constrained by validation and testbed setup; human-in-the-loop operational approval is not specified as an automated control protocol.
- Agent classification: **Agentic workflow / Tool-augmented LLM with a plan-to-act extension.** It is more than an LLM-only summarizer, but the local evidence supports a bounded plan-generation and execution pipeline rather than a general autonomous incident Agent with continuous observation, replanning, and safe production control.

The paper’s “agentic” label is useful for its Plan→Act organization, but the knowledge-base distinction requires separating this workflow label from the stronger claim of an autonomous Agent operating a live environment (see [Agent](../../../concepts/agent.md), [Planning](../../../concepts/planning.md), and [Tool Use](../../../concepts/tool-use.md)).

## 14. Ground Truth

The datasets contain root-cause labels, and the study selects samples to cover all root-cause categories in the ICL subset. SRE-written alert summaries and mitigation plans are used as reference outputs; five experienced SREs assess a subset for correctness and readability (Source: Sec. 4.1, Sec. 4.3, Sec. 4.4.5).

The plan-to-code experiment uses execution outcomes in the Robot Shop testbed as practical evidence. The paper does not define a universal physical root-node ground truth or a multi-root labeling protocol. Human judgments are not the same as independently verified root-cause truth.

## 15. Baselines

- Zero-shot, one-shot, fixed few-shot, and adaptive few-shot prompting.
- General-purpose GPT-4o versus on-premise DeepSeek-V3 and LLaMA-3-70B / IBM models.
- Prompts with versus without structured rule-based alert representations (Source: Table 2).
- Fixed exemplar counts (`k=5` versus `k=10`) versus adaptive retrieval (Source: Table 1).
- Plan-to-code execution outcomes, rather than a separate fully automated remediation system.

## 16. Metrics

- ROUGE-1 and ROUGE-L: lexical overlap with reference summaries/plans.
- Cosine similarity: embedding-level semantic alignment.
- Precision Alignment (PA): exact word matching against root-cause labels.
- Token Alignment (TA): token-level overlap with intended fault terminology.
- Automated LLM-as-a-judge dimensions: Relevance, Actionability, Safety, Consistency, and QAGS/factuality-oriented scoring.
- Human SRE evaluation: Correctness and Readability on a 1–5 scale (five experienced SREs, subset of incidents).
- Task Completion Rate (TCR): fraction of tasks completed by the generated Ansible remediation playbook.
- Data collection success and binary remediation success in plan-to-code execution.

The metrics mix language similarity, category alignment, perceived operational quality, and executable task outcomes. They should not be collapsed into one “RCA accuracy” number.

## 17. Main Results

- Moderate temperature around 0.3 performs best overall in the reported temperature ablation; high temperature increases variability and hallucination risk, while temperature 0.0 is more repetitive (Source: Fig. 3, Sec. 4.4.1).
- Few-shot prompting improves over zero/one-shot settings, and adaptive exemplar retrieval generally outperforms fixed prompts while using fewer tokens. For example, Table 1 reports adaptive `k=5` results alongside fixed `k=5` and `k=10`; the exact gains are metric- and model-dependent (Source: Table 1, Sec. 4.4.2).
- Removing structured alert representations lowers semantic/lexical scores across the reported models and datasets (Source: Table 2, Sec. 4.4.2).
- DeepSeek-V3’s reported RCA-category alignment is 77.42% PA / 95.16% TA on MSDS and 56.67% PA / 78.33% TA on MicroSS; these are category/text alignment metrics (Source: Table 3, Sec. 4.4.3).
- Cross-dataset transfer is asymmetric: MicroSS→MSDS is reported as 0.8866 / 0.5648 / 0.4306 for the three summary metrics, while MSDS→MicroSS is 0.7788 / 0.4666 / 0.3119 (Source: Table 5, Sec. 4.4.4).
- In the plan-to-code feasibility study, TCR is 71.9% for MicroSS, 18% for MSDS, and 36.4% overall. Data collection succeeds in 91.3% of cases, but binary remediation success is only 25%; only one playbook achieves full remediation (Source: Sec. 4.4.6).
- Reported execution failures include shell-formatting errors and environment mismatches on MicroSS, and naming, type-coercion, and hallucinated-API errors on MSDS (Source: Sec. 4.4.6).

The evidence supports adaptive, structured prompting for better output alignment and a limited feasibility demonstration for plan-to-code. It does not support a claim of reliable autonomous production remediation.

## 18. Scalability / Deployment

The paper emphasizes privacy-preserving comparison between cloud-hosted and on-premise models and reports context-window settings for the evaluated models. The controlled study is intentionally limited to 100 representative samples because full prompt construction and execution are expensive (Source: Sec. 4.2–4.3).

There is no demonstrated live production deployment. The authors explicitly identify small dataset size, simulated faults, incomplete observability, dynamic configurations, and model variability as threats to validity and future deployment concerns (Source: Sec. 6).

## 19. Strengths

- Treats metrics, logs, traces, and alerts as a time-aligned operational context rather than isolated text.
- Makes structured alert semantics a visible interface between deterministic signals and LLM reasoning.
- Separates plan generation from code generation/execution, allowing executable outcomes to be measured.
- Compares cloud and on-premise models with adaptive in-context retrieval, cost, and privacy considerations.
- Includes both human-oriented evaluation and a controlled execution feasibility test.

## 20. Limitations

### Paper-supported limitations / qualifications

- The evaluation uses only 100 selected samples, so it is not a statistically broad estimate over the full source datasets (Source: Sec. 4.3).
- Robot Shop faults and generated playbooks may not represent production incident noise, permissions, topology changes, or remediation safety constraints (Source: Sec. 4.4.6, Sec. 6).
- Automated metrics and LLM-as-a-judge scores are proxies; human review remains necessary for operational validation (Source: Sec. 4.4.5).
- Plan-to-code outputs have low binary remediation success and fail for formatting, environment, naming, type, and hallucinated-API reasons (Source: Sec. 4.4.6).
- The framework does not establish a continuous observation-driven replanning loop or unrestricted autonomous remediation.

### Further questions from this reading

- Whether prompt-level multimodal alignment remains reliable with missing or delayed network telemetry is not evaluated.
- PA/TA and summary similarity do not show whether a model selected the correct physical root; a topology-aware, open-set RCA protocol is absent.
- The paper does not isolate gains from alert representation, retrieved exemplars, model choice, and LLM reasoning in a single causal ablation.

## 21. Reproducibility

- Code available: **Yes, according to the paper.** The AIM source repository is identified as `https://github.com/aimframework-sudo/AIM` (Source: Sec. 1, reference [35]).
- Dataset available: **Partly.** Public MicroSS/MSDS are used and sample data are included; the on-premise fine-tuning dataset is confidential and not released (Source: Sec. 4.1, Sec. 1).
- Benchmark available: **Partly.** The Robot Shop testbed and experiment setup are described, but the complete production-like benchmark is not established.
- Prompt available: **Partly.** Prompt construction and adaptive retrieval are described; all prompt assets and proprietary examples may not be public.
- Model/API specified: **Yes, at the model-family level.** GPT-4o, DeepSeek-V3, LLaMA-3-70B, and IBM WatsonX models are named.
- Hyperparameters: **Partly.** Temperature, exemplar counts, split sizes, and context limits are reported; all generation and execution settings are not fully reproduced.
- Enough detail to reproduce: **Medium for the controlled summary/plan experiments; low-to-medium for the full plan-to-code path.** The code link and public datasets help, but proprietary data, testbed details, and model/API variation remain.

## 22. Relationship to Existing AIOps Knowledge

AIM extends the current [Multimodal Telemetry](../../../concepts/aiops/multimodal-telemetry.md) concept with a concrete prompt-level fusion pattern: align entity/time windows, derive symbolic alert severity, selectively include important KPIs, and pass modality-specific snippets into a shared context. This differs from StaR’s stateful graph modeling and RCAgentBench’s runtime tool queries; “multimodal” does not imply one common fusion algorithm.

It also adds a plan-to-act boundary to [Root Cause Analysis](../../../concepts/aiops/root-cause-analysis.md): category alignment, summary quality, mitigation-plan quality, and actual repair success are separate outputs. The historical prompt-summary-mitigation corpus is retrieved context, not automatically [Memory](../../../concepts/memory.md) or a persistent Agent state.

At the generic Agent level, AIM is a useful boundary case for [Agent](../../../concepts/agent.md), [Planning](../../../concepts/planning.md), and [Tool Use](../../../concepts/tool-use.md): it has explicit plan generation and constrained execution, but the paper does not demonstrate continuous autonomous observation, replanning, or production control.

## 23. Relevance to My Research

### Similarities

- Uses heterogeneous operational signals and addresses alert interpretation, RCA-oriented diagnosis, and mitigation planning.
- Exposes a practical interface for converting metrics, logs, traces, and alerts into structured evidence for an LLM.
- Reports failures in generated remediation artifacts, which is relevant to assessing reliability rather than only textual quality.

### Differences

- The evaluation is cloud microservice/testbed based and does not include network-device, interface, link, optical-module, traffic, NetFlow, or syslog-specific RCA.
- Root-cause evaluation is category/text alignment, not physical network candidate localization or multi-root diagnosis.
- The plan-to-code stage is controlled and not a live production autonomous remediation workflow.

### Potentially Useful Ideas

- Build modality-specific preprocessing and preserve timestamps/entity IDs before LLM context construction.
- Use rule-based severity and alert representations as a deterministic grounding layer.
- Retrieve a small number of semantically relevant incident examples instead of stuffing all history into context.
- Separate diagnosis/plan generation from executable action generation, with syntax, namespace, permission, and safety checks between them.
- Evaluate plan text, tool/data collection, and actual remediation success separately.

### Assumptions That May Not Transfer

- Network telemetry often has missing, delayed, asynchronous, or device-specific signals, making timestamp filtering and fixed-window alignment insufficient.
- Ansible/Kubernetes actions and service-level fault labels do not map directly to network control-plane or physical-layer repair.
- Closed root-cause categories and a small selected sample may hide open-set or multi-root network incidents.
- LLM-generated scripts may have much higher safety cost in network infrastructure; a testbed TCR is not evidence of safe production actuation.

### Experiments Worth Considering

- Compare prompt-level fusion, modality-specific retrieval, and deterministic candidate extraction on aligned network metrics, syslog, traffic/NetFlow, topology, and configuration.
- Separate root-node localization, fault-type classification, explanation faithfulness, and remediation success in the evaluation.
- Measure how missing/delayed telemetry and conflicting modalities change plan quality and tool behavior.
- Evaluate human-gated versus fully simulated remediation with rollback, permission, cost, and safety metrics.

### Transferability to Network AIOps

**Medium.** The evidence-alignment, context selection, plan/action separation, and executable-evaluation ideas transfer. The microservice labels, Robot Shop environment, Ansible/Kubernetes assumptions, and lack of physical topology make direct method transfer limited.

## 24. My Understanding

AIM is most useful as a pipeline design lesson: first turn heterogeneous telemetry into a compact, time-coherent alert context; then ask an LLM for a summary and plan; only afterward translate the plan into constrained executable code. Its experiments show that the quality of the context and exemplars matters as much as the model name, and that language-level plan quality can be substantially better than actual repair reliability.

I would therefore classify AIM as an agentic Plan→Act workflow or tool-augmented LLM system with a controlled execution extension. It is not enough to say “AIM is an autonomous RCA Agent”: the paper’s RCA signal is mostly category alignment, its environment is a fault-injection testbed, and only 25% of evaluated cases achieve binary remediation success.

## 25. Questions

### Paper leaves unresolved

- How should the pipeline handle incomplete timestamps rather than filtering them out?
- How can a generated mitigation plan be verified against current topology, configuration, permissions, and safety constraints before execution?
- How much does each modality contribute to root-cause category alignment and plan correctness?
- How should adaptive exemplars be refreshed when historical remediation plans become stale?
- What online feedback mechanism should revise a plan after execution changes the system state?

### Further questions for the knowledge base

- Can prompt-level multimodal context scale to network telemetry without losing per-device/interface/link provenance?
- Should topology be included as context, exposed through a query tool, or used as a hard constraint on candidate generation?
- What is the minimum independent verification needed before an LLM-generated network remediation can be human-approved?

## 26. Source Grounding

- Motivation, contributions, and task scope: Abstract, Sec. 1–2.
- MAPE-K framing and Observe–Analyze–Plan–Act architecture: Sec. 3, Fig. 1.
- Data integration, timestamps, KPI thresholding, and prompt assembly: Sec. 3.1–3.2.
- Adaptive exemplar retrieval and LLM generation: Sec. 3.3, Fig. 2.
- Plan-to-code, validation, and controlled execution: Sec. 3.4.
- Datasets and sample selection: Sec. 4.1–4.3.
- Metrics and temperature/prompt studies: Sec. 4.3–4.4.2, Fig. 3–4, Tables 1–2.
- RCA category alignment and cross-dataset transfer: Sec. 4.4.3–4.4.4, Table 3 and Table 5.
- Human judgment and LLM-as-a-judge: Sec. 4.4.5, Table 4.
- Plan-to-code execution and failure analysis: Sec. 4.4.6.
- Threats to validity and deployment boundary: Sec. 6.
- Conclusions: Sec. 7.

## 27. Tags

`AIOps` `multimodal-telemetry` `alert-summarization` `RCA` `mitigation-planning` `plan-to-act` `adaptive-ICL` `tool-augmented-LLM` `Ansible` `human-in-the-loop` `network-transferability`
