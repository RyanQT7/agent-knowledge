# Paper–Code Repository Index

This index records repository discovery for papers that already have completed
reading notes. External repositories are kept outside the knowledge-base Git
history under `sources/code/`; this file records only identity, provenance, and
the status of our static reading.

## Status Levels

- **Confirmed Official**: the paper, project page, or an author-controlled repository directly identifies the implementation.
- **Likely Official**: the repository clearly identifies the paper and appears author-controlled, but the direct paper-to-repository link is not fully confirmed in the local notes.
- **Author-Endorsed Implementation**: the paper points to the repository, but the repository identity or implementation coverage needs caution.
- **Third-party Reproduction**: related code found, but not treated as the paper's official implementation.
- **No Repository Found**: no sufficiently reliable public repository was identified during the scoped search.

## Paper-to-Repository Inventory

| Paper | Area | Repository | Official status | Evidence | Local path | Read at commit | Code reading | Notes |
|---|---|---|---|---|---|---|---|---|
| [ReAct](../papers/react/notes.md) | Agent / LLM | [ysymyth/ReAct](https://github.com/ysymyth/ReAct) | Confirmed Official | Project page Code link; README cites the exact ICLR paper | [`sources/code/agent/react/ReAct`](../sources/code/agent/react/ReAct) | `6bdb3a1fd38b8188fc7ba4102969fe483df8fdc9` | Completed | Environment wrappers and task notebooks |
| [Reflexion](../papers/reflexion/notes.md) | Agent / LLM | [noahshinn/reflexion](https://github.com/noahshinn/reflexion) | Confirmed Official | README cites the exact paper and authors; current repository URL supersedes the older local-note URL | [`sources/code/agent/reflexion/reflexion`](../sources/code/agent/reflexion/reflexion) | `218cf0ef1df84b05ce379dd4a8e47f17766733a0` | Completed | Programming and WebShop implementations |
| [ReWOO](../papers/rewoo/notes.md) | Agent / LLM | [billxbf/ReWOO](https://github.com/billxbf/ReWOO) | Confirmed Official | Paper notes provide the repository URL | [`sources/code/agent/rewoo/ReWOO`](../sources/code/agent/rewoo/ReWOO) | `9cd0283043ff4be0c9d614fda2789d143ca6ffd1` | Completed | Planner–Worker–Solver implementation |
| [LLM+P](../papers/llm-p/notes.md) | Agent / LLM | [Cranial-XIX/llm-pddl](https://github.com/Cranial-XIX/llm-pddl) | Confirmed Official | Paper arXiv page identifies the code repository | [`sources/code/agent/llm-p/llm-pddl`](../sources/code/agent/llm-p/llm-pddl) | `f5f897ccabfb19d5158e5a7ac4cb36517cd4c2e0` | Completed | LLM-to-PDDL and Fast Downward adapter |
| [RAP](../papers/rap/notes.md) | Agent / LLM | [Ber666/RAP](https://github.com/Ber666/RAP) | Confirmed Official | Author-controlled repository cites RAP; paper's older `llm-reasoners` URL is recorded as a URL/version discrepancy | [`sources/code/agent/rap/RAP`](../sources/code/agent/rap/RAP) | `774817c228b3d5ddfc18de2318f3476128ecf6eb` | Completed | MCTS with language-model world-model scoring |
| [Toolformer](../papers/toolformer/notes.md) | Agent / LLM | No official repository identified; [conceptofmind/toolformer](https://github.com/conceptofmind/toolformer) is related | Third-party Reproduction | Exact-title search found reproductions, not a paper-linked official repository | — | — | Not performed | No third-party clone by default |
| [RCAgentBench](../papers/aiops/rcagentbench/notes.md) | AIOps | [CSTCloudOps/RCAgentBench](https://github.com/CSTCloudOps/RCAgentBench) | Confirmed Official | Paper notes provide the repository URL | [`sources/code/aiops/rcagentbench/RCAgentBench`](../sources/code/aiops/rcagentbench/RCAgentBench) | `ab14bba1948202416535803825e1d58cfab391bd` | Completed | Benchmark and agent evaluation implementation |
| [StaR](../papers/aiops/star/notes.md) | AIOps | [huanghy95/StaR](https://github.com/huanghy95/StaR) | Confirmed Official | Public artifact page links the author repository and exact paper | [`sources/code/aiops/star/StaR`](../sources/code/aiops/star/StaR) | `b1f079f9aa5599f68bc079eb1045152404603a87` | Completed | Stateful dynamic-graph RCA implementation |
| [AIM](../papers/aiops/aim/notes.md) | AIOps | [aimframework-sudo/AIM](https://github.com/aimframework-sudo/AIM) | Author-Endorsed Implementation | Paper notes provide the URL; repository README has placeholder/template wording, so official coverage is not asserted | [`sources/code/aiops/aim/AIM`](../sources/code/aiops/aim/AIM) | `202bead6ee8a3ed0f0c367d4f235c647bebbc7a5` | Completed | LLM alert summary and mitigation evaluation |
| [StepFly](../papers/aiops/stepfly/notes.md) | AIOps | [microsoft/StepFly](https://github.com/microsoft/StepFly) | Confirmed Official | Microsoft repository README identifies the paper/project | [`sources/code/aiops/stepfly/StepFly`](../sources/code/aiops/stepfly/StepFly) | `a6229192a69dd2eebc58d9b8f754dbc396029c4e` | Completed | Scheduler, PlanDAG, executors, tools, MongoDB memory |
| [ChatRCA](../papers/aiops/chatrca/notes.md) | AIOps | [leocache/ChatRCA](https://github.com/leocache/ChatRCA) | Author-Endorsed Implementation | Paper points to the repository; implementation identity is treated conservatively | [`sources/code/aiops/chatrca/ChatRCA`](../sources/code/aiops/chatrca/ChatRCA) | `448c2714047a1cf05371937b811dfe75ca8394d6` | Completed | Role-based multi-agent RCA with tool functions |
| [Cloud-OpsBench](../papers/aiops/cloud-opsbench/notes.md) | AIOps | [LLM4Ops/Cloud-OpsBench](https://github.com/LLM4Ops/Cloud-OpsBench) | Likely Official | README identifies the exact benchmark and state-snapshot paper; author-control link not fully established in local notes | [`sources/code/aiops/cloud-opsbench/Cloud-OpsBench`](../sources/code/aiops/cloud-opsbench/Cloud-OpsBench) | `54bcec7c7faba390549bda833c175178a7513812` | Completed | Snapshot benchmark, tools, harness, evaluators |
| [CHIEF](../papers/aiops/chief/notes.md) | AIOps | [Mr-Capybara/CHIEF](https://github.com/Mr-Capybara/CHIEF) | Likely Official | README identifies the exact paper and implementation; direct URL was not present in the local paper note | [`sources/code/aiops/chief/CHIEF`](../sources/code/aiops/chief/CHIEF) | `2b47170c41913c8bdea34397f7d52c65360dcef9` | Completed | HCG, oracle-guided attribution, counterfactual analysis |
| [CAUSALDX](../papers/aiops/causaldx/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [LLMGuard](../papers/aiops/llmguard/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [KAT](../papers/aiops/kat/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [Comfey](../papers/aiops/comfey/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [TSGen](../papers/aiops/tsgen/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [Cloud Intelligence / AIOps 2.0](../papers/aiops/cloud-intelligence/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |
| [FlowFixer](../papers/aiops/flowfixer/notes.md) | AIOps | No sufficiently reliable repository found | No Repository Found | No exact paper-linked repository identified in the scoped public search | — | — | Not performed | — |

## Independent Agent Framework Inventory

These are framework-learning targets rather than paper implementations. The
requested URLs are the repository identity evidence; no paper is required.

| Framework | Category | Repository | URL | Branch | Read at commit | License | Local path | Static reading |
|---|---|---|---|---|---|---|---|---|
| [smolagents](agent-frameworks/smolagents.md) | Minimal / tool-calling / code agent framework | `huggingface/smolagents` | [GitHub](https://github.com/huggingface/smolagents) | `main` | `30bb1161095dbae2271e6bc3cc4c219cc3897a57` | Present | `sources/code/agent-frameworks/smolagents` | Completed |
| [LangGraph ReAct](agent-frameworks/langgraph-react-agent.md) | Graph-based ReAct agent | `langchain-ai/react-agent` | [GitHub](https://github.com/langchain-ai/react-agent) | `main` | `9bbd82d84905acc37f527b1f372dae841016f3b4` | Present | `sources/code/agent-frameworks/react-agent` | Completed |
| [OpenAI Agents SDK](agent-frameworks/openai-agents-sdk.md) | Production-oriented Agent SDK | `openai/openai-agents-python` | [GitHub](https://github.com/openai/openai-agents-python) | `main` | `d59fdb8a789a54aff77ce61e503a04797355fc03` | Present | `sources/code/agent-frameworks/openai-agents-python` | Completed |
| [Microsoft Agent Framework](agent-frameworks/microsoft-agent-framework.md) | Agent runtime / typed workflow / orchestration | `microsoft/agent-framework` | [GitHub](https://github.com/microsoft/agent-framework) | `main` | `999dda7970fe969c0901d524365ce34ecbda6227` | Present | `sources/code/agent-frameworks/agent-framework` | Completed; shallow clone |

The configured tool list did not expose a dedicated GitHub MCP search method in
this run. Because the four URLs were explicit, identity and source evidence
were verified from each clone's Git metadata, README, and source tree. A later
run with GitHub MCP available can add API-level metadata without changing these
fixed source SHAs.

## Cloned Repository Metadata

The following values are recorded from the local clone. Stars and forks are
intentionally not used as quality evidence and were not required for static
analysis.

| Repository | Owner / name | Read branch | License observed | Last local commit date | Stars / forks |
|---|---|---|---|---|---|
| ReAct | `ysymyth/ReAct` | `master` | Present | 2023-07-14 | Unknown / Unknown |
| Reflexion | `noahshinn/reflexion` | `main` | Present | 2025-01-13 | Unknown / Unknown |
| ReWOO | `billxbf/ReWOO` | `main` | Present | 2023-07-28 | Unknown / Unknown |
| LLM+P | `Cranial-XIX/llm-pddl` | `main` | Not observed at top level | 2023-09-27 | Unknown / Unknown |
| RAP | `Ber666/RAP` | `main` | Present | 2023-08-25 | Unknown / Unknown |
| RCAgentBench | `CSTCloudOps/RCAgentBench` | `main` | Not observed at top level | 2026-02-16 | Unknown / Unknown |
| StaR | `huanghy95/StaR` | `main` | Present | 2026-05-31 | Unknown / Unknown |
| AIM | `aimframework-sudo/AIM` | `main` | Present | 2025-10-27 | Unknown / Unknown |
| StepFly | `microsoft/StepFly` | `main` | Present | 2026-06-01 | Unknown / Unknown |
| ChatRCA | `leocache/ChatRCA` | `master` | Present | 2026-08-17 | Unknown / Unknown |
| Cloud-OpsBench | `LLM4Ops/Cloud-OpsBench` | `main` | Present | 2026-09-12 | Unknown / Unknown |
| CHIEF | `Mr-Capybara/CHIEF` | `main` | Not observed at top level | 2026-07-09 | Unknown / Unknown |

## Discovery Notes

- The configured tool list did not expose a dedicated GitHub MCP search method in this run. Public GitHub pages and paper/project links were used as a restricted fallback; repository identity was kept conservative.
- The old RAP paper link `Ber666/llm-reasoners` was unavailable, while the author-controlled `Ber666/RAP` repository identified the exact method. This is recorded as a version/URL discrepancy rather than silently treating a related library as the paper repository.
- Toolformer has related third-party implementations, but no sufficiently reliable official repository was identified and none was cloned.
- Repositories with no reliable identity were not cloned. No external repository source is tracked in the knowledge-base Git history.

## AgentOps and OpsAgent repositories

These entries were statically inspected for this research batch. Local clones are ignored by Git; only the paper-to-code mapping is committed. No dependencies were installed and no source code or operational script was executed.

| Paper | Repository | Official status and evidence | Commit SHA | License | Code coverage and entry/modules | Paper-code mapping |
|---|---|---|---|---|---|---|
| [GALA / GALA+](../papers/opsagent/gala.md) | [EvanTian233/GALA-for-RCA](https://github.com/EvanTian233/GALA-for-RCA) · local clone at ../sources/code/GALA-for-RCA/ | Confirmed official by the author project page and paper; repository README states core GALA is withheld under the industrial agreement | 24d1329d20fb9139f7899a1bed9e8d0bdaf00be0 | MIT for the released artifact repository; vendored baselines retain their own licenses | README, annotation_guidelines.md, annotated_dataset.csv, sample_output JSON, one-page technical report; no GALA runner or SURE-Score scorer | Public artifacts show output fields and annotation intent, not the internals of STRIX/Agents or scoring. Static only; no code/data run. |
| [AgentRx](../papers/agentops/agentrx.md) | [microsoft/agentrx](https://github.com/microsoft/agentrx) · [local clone](../sources/code/agentrx/) | Confirmed official; Microsoft Research README names exact title/arXiv ID and linked dataset | 7a18c79708e7671be15124460f4f7296107c2a55 | MIT | CLI agentrx/cli.py; trajectory IR, invariant generators/checker, judge, reports | Raw logs → normalized IR → constraints/checker evidence → Judge → diagnosis report; diagnoses failures, no repair |
| [Trial by Trace](../papers/agentops/trial-by-trace.md) | [TraceLite-AI/TraceTrial-Bench](https://github.com/TraceLite-AI/TraceTrial-Bench) · [local clone](../sources/code/trace-trial-bench/) | Confirmed official; paper front matter and project page link repository | 98a381307184fa4212db3466b21b4c92a031940b | MIT | harness_tracer/writer.py; verifier/trace_ir.py, backend adapters and criteria evaluators | Event writer/adapters produce trace evidence; normalized evidence and criterion evaluation implement harness measurement |
| [NKU OpsAgent system](../papers/opsagent/opsagent-system.md) | [Johnn13/OpsAgent](https://github.com/Johnn13/OpsAgent) · [local clone](../sources/code/opsagent-system/) | Confirmed official; author project page and paper identify the repository | 6d61b8bb9c6bc9de6347601562c644fade324765 | No license file observed | Entry main.py; agents/orchestrator.py; utils/data_processer.py; AD/FT/RCL agents, prompts, reflection/training assets | Preprocess M/L/T → specialist task agents → cross-review/refinement → offline evolution; no independent verifier module found |
| [OpsMem](../papers/opsagent/opsmem.md) | [gaorch85/OpsMem](https://github.com/gaorch85/OpsMem) · [local clone](../sources/code/opsmem/) | Confirmed official; author project page and paper link repository | a22580297251ff7b5a24ce1fdab649b7df189e22 | Apache-2.0 | code/main.py, pipeline.py; STM graph/FSM, CMR, expert/central agents, consolidation | Current diagnostic graph → refreshed LTM activation → agent evidence/updates → feedback-gated memory proposal; public data is a small sanitized subset |
| [Graph of States](../papers/opsagent/graph-of-states.md) | [gaorch85/Graph-of-States](https://github.com/gaorch85/Graph-of-States) · [local clone](../sources/code/graph-of-states/) | Confirmed official; PMLR/NKU research page and paper identify author project | 0f28c2e11b55f3dccf8e249b63286bd83b8edd35 | MIT | main.py; belief/graph.py, belief/fsm.py; central/expert agents; IT diagnosis runner | Hypothesis/evidence graph → expert tool evidence → support/refutation updates → expansion/backtracking; no remediation implementation found |
| [PoS / Beyond Memory](../papers/opsagent/pos.md) | [luoyu100/PoS](https://github.com/luoyu100/PoS) · [local clone](../sources/code/pos/) | Confirmed official; author project page and paper link repository | 6818cfa6434dbc91fcf67f0b3eb12a91db47433f | MIT | main.py; belief state/manager/sentinel, trapping detection, recovery planning | Agent proposes state → sentinel audits → progress/stagnation checks → recovery constraints; recovery module guides later action but does not execute IT repair |

Official-source searches did not identify named public implementations for [TraJudger](../papers/agentops/trajudger.md), [PROBE](../papers/agentops/probe.md), or [KRCA](../papers/opsagent/krca.md) by the cutoff. PROBE's anonymous artifact is not recorded as a verified named GitHub source. Other paper-code limitations and commit-specific inspection details are in each paper note.

## AIOps Benchmark repositories

These repositories were checked for the Benchmark reading batch. Clones are local research sources and remain ignored/untracked; the knowledge-base commit contains only this paper-to-code map. No third-party code, injection, benchmark, or scorer was executed.

| Paper | Repository / local source | Read commit | Static code reviewed | What the reviewed code establishes / boundary |
|---|---|---|---|---|
| [RCABench](../papers/benchmark/rcabench/notes.md) | [OperationsPAI/aegis](https://github.com/OperationsPAI/aegis) · `../sources/code/benchmark/aegis/`; archived [AegisLab](https://github.com/OperationsPAI/AegisLab) | `979ae7011d06d21925001ce517ed40cedca529b0`; archive `a55646d66fef51c3cd11e67ccebfae5d62ac6f9b` | `temporal_validator.py`, `sdk/samplers/metrics_sli.py`, `sdk/evaluation/{ground_truth,evaluator,graph_match}.py`, READMEs | Current version checks evidence/time consistency and aggregates SLI features. Did not find the paper's injection-acceptance SLI gate in the inspected path; current repo is later integrated platform, not paper experiment snapshot. |
| [NIKA](../papers/benchmark/nika/notes.md) | [sands-lab/nika](https://github.com/sands-lab/nika) · `../sources/code/benchmark/nika/` | `7324960044f7c524d86e4859a07f260a664f79ac` | `benchmark/working/pool/dc_clos/link_down.yaml`, `src/nika/problems/base.py`, `problems/rca/models.py`, `evaluator/scoring.py` | Scenario/injection/GT fields are separated; root-cause resources have canonical IDs; current scorer uses detection and resource/type set metrics. Current branch has evolved beyond paper's 640 configurations/150 experiments. |
| [OpenRCA](../papers/benchmark/openrca/notes.md) | [microsoft/OpenRCA](https://github.com/microsoft/OpenRCA) · `../sources/code/benchmark/openrca/` | `2a481ae63cb045c3eadbeca9eddaa10ec1151979` | `main/generate.py`, `main/evaluate.py`, `rca/run_agent_standard.py`, `rca/baseline/rca_agent/{controller,executor}.py`, sampling entrypoints | Query generation maps seven requested label subsets; evaluator normalizes/compares structured predictions; Agent uses Controller plus Python Executor. Current source includes sandbox hardening not necessarily used in ICLR experiments. |
| [Constructing Large-Scale](../papers/benchmark/constructing-aiops-benchmark/notes.md) | [iops evaluation](https://github.com/iopsai/iops/tree/master/evaluation) · `../sources/code/benchmark/iops/`; [2020 data](https://github.com/NetManAIOps/AIOps-Challenge-2020-Data) | `ad962c2187d73b1a14971b255a2bd87212f896f2`; data README `5dcea9688794f3787a9b7e4a8931c6e70fa0ec78` | `evaluation/evaluation.py`, dataset README | Evaluator reconstructs missing timeline points, allows early hits within an anomaly range, then computes concatenated F1. The three cited dataset families are separate; B/C generator coverage was not verified. |
| [AgenticOpsEval](../papers/benchmark/agenticopseval/notes.md) | [official project/data page](https://www.aiops.cn/gitlab/aiops-live-benchmark/agenticopseval) · `../sources/code/benchmark/agenticopseval/` | `69cf36430b43024d02530c610b1a4738b5c9a7fb` | README and available project tree only | Paper defines LA/TA/evidence/efficiency and RCA100 chain metrics. Current cloned tree did not expose scorer/runner source despite paper's release statement; formulas therefore have not been verified against implementation. |
| [CTBench](../papers/benchmark/ctbench/notes.md) | [HF dataset card](https://huggingface.co/datasets/netop/CTBench) | No code SHA | Paper's task interface, gold-action and metric descriptions; no source tree | Dataset access is subject to Hugging Face terms; no independently verifiable official code/scorer repository was identified or run. |
| [NetArena](../papers/benchmark/netarena/notes.md) | [Froot-NetSys/NetArena](https://github.com/Froot-NetSys/NetArena) `main` · [`sources/code/NetArena/`](../sources/code/NetArena/) | `aefbd457497768a9504cfc1c6b0988a626cf082a` | `app-malt/` query/Ground Truth/evaluator; `app-route/` fault generation and safety; `app-k8s/` policy injection, interaction and connectivity checks | Static analysis only; no installation or execution. `main` is the direct local-run branch identified by README; current default `a2a-agentx` is a different integration path. No root LICENSE observed. See [code note](benchmark/netarena.md). |

Current source snapshots are evidence for the inspected files only. They must not be silently treated as the exact paper-era commit or used to reproduce the reported paper numbers without a version match.
