# LLM-Driven Microservice Anomaly Generation — Cross-Paper Comparison

Evidence scope: six papers with full-text notes. AMulSys is included only as a pending metadata row.

| Paper | Modality / output | LLM? | Generation / system mechanism | Fault knowledge | Cross-modal consistency | Normal variation | Reality / utility evidence | Main boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TraceLLM | Call-graph Trace DAG | Yes, Llama-2 7B + LoRA | Recursive conditional generation of graph layers and edge fields | No explicit fault root cause or injection plan | No Metric / Log | No explicit business-state model | DAG / condition validity, distribution distances, downstream call-graph task | Structured Trace generation is not fault generation |
| LLM-AP | Univariate continuous numeric windows | Yes, frozen GPT-3.5 / GPT-4o | Prompt-based window rewriting plus five-stage checks and refinement | No microservice / causal fault knowledge | None | Local normal examples only; no workload semantics | NAB F1 uplift for some detector backbones; Autoformer decline | Local shape rules are not causal authenticity |
| Synthetic Time Series | Runtime metrics and collected logs | No | Locust dynamic demand plus AWS FIS system fault injection | Configured fault target and action | Some modalities are observed from shared runtime; no joint generation or consistency metric; Trace absent | Trends, periodic demand, noise; separate multiplier load anomaly | Injection-aligned labels and example metric effects; no detector comparison | Realistic within a controlled testbed, but limited application / fault coverage |
| AMulSys | Multimodal / hybrid-graph claim from title and metadata only | Unknown | Not assessed; full text pending | Unknown | Unknown | Unknown | No full-text evidence reviewed | Do not infer method details from abstract or cited baseline |
| GenIAS | UTS / MTS numeric sequence | No | TCN-VAE latent perturbation and variable-level patching | No operational mechanism labels | None | Learns sequence normality, no explicit workload state | ARP / EDI and detector results across nine benchmarks | Potentially useful anomaly samples are not microservice fault traces |
| MODIFy | Log + Metric + Trace input | No | Trace diffusion denoising, MSCA-CGFM, service-call GAT, joint detection / localization | Supervised anomaly and root-service labels; no sample generation | Fuses observed modalities; does not synthesize them | No workload / release condition | F1 / HR / NDCG, ablations, added-noise robustness on two systems | Detection / diagnosis is not generation; no source-aware workload test |
| AIOpsLab | Live multimodal cloud observations | Evaluates LLM Agents; not a generator | Deploys workloads and injects faults into running services | Controlled symptomatic / functional faults and hidden oracle | Modalities come from shared environment observations | Two no-op normal tasks; limited normal-state coverage | Agent task accuracy; normal false positives on two tasks except GPT-4-W-Shell | Task benchmark, not synthetic-sample validation |

## Capability boundary

1. **LLM versus classical generation**: TraceLLM generates structured invocation DAGs; LLM-AP directly edits univariate values. GenIAS uses a VAE, while Synthetic Time Series / AIOpsLab trigger configured actions in a live service.
2. **Numbers versus mechanisms**: A sequence can be numerically plausible without a known cause. Live fault injection links an action and target to measured observations, but does not establish coverage of all production behavior.
3. **One modality versus multiple modalities**: No fully read generator here is shown jointly producing Metric, Trace and Log from a shared fault mechanism and verifying agreement. MODIFy fuses measured modalities; that is a downstream diagnostic task.
4. **Statistical realism versus causal / operational realism**: RelDTW, ARP / EDI, DAG validity and detector F1 test different properties. A shared runtime intervention is stronger mechanism evidence, but remains testbed-bounded.
5. **Normal changes versus faults**: Synthetic Time Series includes dynamic baseline demand and separate fault injections; AIOpsLab tests two no-op tasks; LLM-AP / GenIAS have no explicit business semantics. Existing TSAD papers offer normal adaptation and robust augmentation, but do not by themselves settle microservice workload-change / fault concurrency.

## Evidence references

- TraceLLM: note §§3–7; PDF §§3–4, Eqs. 1, Figs. 3–7.
- LLM-AP: note §§3–7; PDF §§3–4, Eqs. 1–12, Table 8.
- Synthetic Time Series: note §§3–7; PDF §3, Eqs. 1–2, Algorithms 1–2, Tables 1–3, Figs. 5–6.
- GenIAS: note §§3–7; PDF §3, Eqs. 1–6, Algorithms 1–2, Tables 1–4.
- MODIFy: note §§3–7; PDF §§4–5, Eqs. 1–17, Tables 2–7, Figs. 2–9.
- AIOpsLab: note §§3–7; MLSys PDF §§2–3, Table 3, §3.6.4.
- AMulSys: metadata only; see the pending-full-text record in the topic source report.
