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
