# Trial by Trace: Benchmarking AI Agent Harnesses for Reliability and Failure Attribution

## Bibliographic record

- Authors: The paper uses the group author TraceLite AI, affiliated with Institute of Automation, CAS; Zhongguancun Academy; Institute of Information Engineering, CAS; Tsinghua University; and Beijing Institute of Technology.
- Status at 2026-11-17: arXiv:2610.32285, submitted October 2026; no peer-reviewed venue listed at cutoff.
- Sources: [arXiv paper](https://arxiv.org/abs/2610.32285), [project page](https://tracelite.ai/trial-by-trace.html), [repository](https://github.com/TraceLite-AI/TraceTrial-Bench).
- Local PDF: ../../sources/papers/agentops/trial-by-trace.pdf (ignored).
- Reading status: Full 50-page text, protocol, selected appendices, and case studies.
- Official repository: Project page links the repository; repository identifies benchmark/paper.

## Research question and benchmark

An agent’s behavior depends on the harness—the runtime managing context, tool interfaces, policy, delegation, execution, and trace collection—as well as the model. Task success alone can credit a harness for model success while hiding runtime failures. Trial by Trace evaluates the two layers separately.

It defines seven harness dimensions: Context, Execution, Governance, Lifecycle, Observability, Tools, and Verification. The benchmark has 95 mechanism-oriented tasks and evaluates four harnesses (Claude Code, Codex, DeepSeek Harness, OpenClaw) with nine model groups, reporting 3,420 selected runs (Secs. 1–3, Table 1).

## Measurement pipeline

Native run → trajectory tracing → normalized Trace IR plus raw artifacts → Agent score plus Harness score → candidate mechanism links.

- Trajectory Tracing collects available context, message, tool, execution, lifecycle, policy, subagent, and token records while retaining raw artifacts.
- Multi-source Evidence Acquisition selects evidence and probes for each criterion and separates observable facts from semantic judgments.
- Agent criteria assess task behavior/output; Harness criteria assess runtime behavior. Evidence-integrity apparatus is not a third system score.
- Failure Attribution activates predeclared mechanism links when both endpoints fail and their conditions hold. Activation identifies a candidate explanation; it does not validate causal propagation.

(Secs. 3–4, Tables 4–5, App. D.)

## Findings and limitations

- Reported macro harness scores range from 59.8% to 72.0%; 31.1% of selected runs pass task criteria but fail at least one harness criterion (Abstract, Sec. 5).
- The 3,420 results are one selected run per task–model–harness cell, with no within-cell repeated-run variance. Task revisions, budgets, and some model/harness pairings vary. Scores are descriptive of this protocol, not a universal ranking (Secs. 4.3, 6).
- The paper says 49.5% of 1,700 joint-failure cases activate a predeclared harness-to-agent mechanism. This is not precision of validated causal links. Corpus-level selector recall, candidate-link precision, and independent judge agreement for every semantic judgment are not reported (Secs. 4–5, App. D).
- Verification has only one task in the suite. Expert mechanism tasks are stress tests, not a representative sample of production incidents (Sec. 6).
- Agent success and harness reliability are distinct; neither proves an incident was correctly diagnosed or safely recovered.

## Structured answers

| Dimension | Finding |
| --- | --- |
| Failure taxonomy | Seven harness dimensions, with task and harness criteria scored separately. |
| Trajectory | Normalized events include sequence, timestamp, run ID, event type, calls/results, model inputs/outputs and available lifecycle, subagent, policy, and token records. Raw artifacts retained where available. |
| Attribution | Mechanism links are candidates; activation is not ground-truth causality. |
| LLM | Semantic criteria use evidence-selected judgments; deterministic rules cover programmatic checks. |
| Agent/Multi-Agent | Studies agents and harnesses; multiple agents are not required per task. Delegation is a harness lifecycle dimension. |
| Planning/memory | Measures context preservation, compaction, delegation; not a planning or memory-learning algorithm. |
| Tools/state | Adapters capture calls/results and runtime evidence, subject to each harness’s observability. |
| Recovery | Some tasks exercise recovery properties; aggregate scores are not a general recovery-success rate. No production remediation claimed. |
| Network AIOps | Separate operational outcome from reliability of the runtime mediating tools, policies, context, and state; build new operational criteria. |

## Code analysis record

| Field | Record |
| --- | --- |
| Repository | [TraceLite-AI/TraceTrial-Bench](https://github.com/TraceLite-AI/TraceTrial-Bench) |
| Official status/evidence | Confirmed Official: paper front matter and project page link the repository. |
| Commit SHA | 98a381307184fa4212db3466b21b4c92a031940b |
| License | MIT, LICENSE |
| Core modules | harness_tracer/writer.py appends run-scoped, sequence-numbered, timestamped events and supports value redaction. verifier/trace_ir.py defines harness profiles/backends and normalized accessors. verifier/ contains deterministic and semantic criterion evaluation. |
| Paper-code mapping | Event writer/adapters map to TT; evidence selectors and criterion scoring map to MEA/layered evaluation. |
| Static analysis | Inspected README, event writer, trace normalization and verifier interfaces. No tests, benchmarks, harnesses, or model calls were run. |

## Research value

The benchmark expands AgentOps from diagnosing an agent decision to separating model behavior from the runtime that mediated it. Reusable measurement lessons: record each criterion’s evidence source, distinguish missing observation from measured zero, and separate task success from harness reliability. Candidate mechanism chains still require validation and representative production distributions.

## Links

- [AgentRx](agentrx.md): evidence-grounded failure step and category.
- [TraJudger](trajudger.md): graph-constrained cross-agent attribution.
- [PROBE](probe.md): diagnosis-derived guidance and retry outcomes.
- [Agent System Operations](agent-system-operations.md): lifecycle framework.
