# TraJudger: Structure-Guided Failure Attribution for LLM-Powered Multi-Agent Systems

## Bibliographic record

- Authors: Yongxin Zhao, Shenglin Zhang, Wenwei Gu, Zijing Que, Weiwen Qian, Yongqian Sun, Li Shi, Wei Li, Liping Zhang, Dan Pei.
- Publication: USENIX ATC ’26, accepted paper; checked against the NKU publication listing, conference program, and PDF.
- Sources: [NKU-hosted PDF](https://nkcs.iops.ai/wp-content/uploads/2026/09/atc26-paper471.pdf), [NKU publications](https://nkcs.iops.ai/publications/), [USENIX ATC](https://www.usenix.org/conference/atc26).
- Local PDF: ../../sources/papers/agentops/trajudger.pdf (Git-ignored).
- Reading status: Full 21-page text, including method, experiments, deployment, cases, and limitations.
- Official code: Not publicly found at the cutoff.

## Problem and method

An LLM multi-agent system can make an upstream error and carry it forward through natural-language messages. The final wrong answer, or the last agent that emitted it, may be only a symptom. A monolithic LLM judge may also invent a plausible causal story or confuse failure types. TraJudger performs post-hoc attribution on already failed MAS trajectories. It does not detect incidents online, diagnose infrastructure root causes, or autonomously repair an agent.

The authors analyze 121 production trajectories from a four-agent system (Clarifier, Leader, Coder, Web-Searcher), with 2–47 interaction steps; 45.5% of annotated propagation chains span at least three steps. A second dataset has 126 algorithm-generated cases (Sec. 2, Tables 1–2).

The Hierarchical Cognitive Graph (HCG) pipeline:

1. Create static nodes for task constraints, agent roles/prompts, and available tools.
2. Parse each trajectory step into dynamic intention and action nodes with source spans.
3. Connect execution/dependency edges and cross-layer relations such as compliance, following, and invocation.
4. Run four parallel specialists: Constraint/Role Compliance, Logic/Cognitive, Execution/Flow, and Collaboration/Context.
5. Merge findings by step/category. An LLM proposes non-adjacent data-dependency links.
6. Starting at a terminal failure, traverse backwards. Deterministic graph traversal distinguishes faulty root steps from correct conduit steps that only propagate an earlier error. Candidate causes are ranked using severity, confidence, and downstream impact.

The LLM parses intent/action and proposes semantic dependency edges; it does not establish an edge as causal ground truth. Source-span grounding and a typed graph constrain later attribution (Secs. 3.1–3.4, Figs. 3–5).

## Failure taxonomy and evidence

Table 1 groups ten modes into four families: constraint/role violations (task-constraint deviation, role deviation); logic/cognitive errors (hallucination, logical inconsistency, overconfidence); execution/flow breakdowns (looping, premature termination, tool error); collaboration/context failures (unclear communication, context ignorance).

The evaluation labels responsible agent, root-cause step, failure type, and, where applicable, a propagation chain. A late terminal symptom is not automatically the initiating fault. Humans decide and implement prompt/schema or system changes (Secs. 2–3, Table 1).

## Results, limits, and recovery boundary

- Best reported GPT-5.4 configurations reach agent/step accuracy of 0.884/0.843 and 0.786/0.691 on D1/D2; the paper also reports type accuracy and sub-minute diagnosis at about $0.03–$0.06 per case. These are offline attribution results, not online alert quality (Sec. 4, Tables 4–6).
- Error-chain correctness is 83/102 (81.4%) only among cases where both agent and root step were correct. This conditional denominator matters (Sec. 5.5).
- Production evaluation covers 63 trajectories over more than a month, with 52 correct attributions. Reported time-to-attribution fell from about 30 minutes to under one minute. Operators made 17 self-directed refinements; suggested fixes included five prompts and nine tool schemas. The system did not execute or verify those repairs (Sec. 6.1).
- Offline sets contain known failed runs, so they do not establish detection delay, false alarms, or performance on successful trajectories.
- D1 comes from one deployed MAS; D2 is generated algorithmically. Hidden/shared-memory channels and other role systems may behave differently.
- Missing implicit context edges and long-context limits are major sources of incorrect chains (Secs. 5.5–6.3). Ground-truth annotation must distinguish causal step, chain, and terminal symptom.

## Structured answers

| Dimension | Finding |
| --- | --- |
| Trajectory | Failed-run agent steps and communications; agent identity and order are present. A standard timestamp/state-update schema is not the contribution. |
| Responsible agent/root step | Specialists plus reverse HCG traversal; conduit steps can be exonerated. |
| LLM role | Semantic parsing, category-specific judgments, proposed dependency edges. |
| Planning/memory | No online planner or persistent agent memory; the graph is retrospective. |
| Tools/state | Tool nodes and invocation edges are represented; tool telemetry informs error classification. |
| Recovery | Human prompt/schema changes are reported; no automatic retry or verified state restoration. |
| Verification | Span grounding and graph constraints support attribution but do not prove causality. |
| Network AIOps transfer | HCG may represent semantic agent dependencies; service telemetry, topology, and causal links need additional evidence. |

## Paper-code record

- Repository and status: Not publicly found. NKU paper/publication pages link the PDF but no GitHub source.
- Commit SHA, license, entry point: Not applicable; no verified public implementation.
- Paper-code mapping: The paper describes a NetworkX directed graph and about 3.4k lines, but the source was not found; this is not independently code-verified.

## Related knowledge

- [AgentRx](agentrx.md) adds programmatic and semantic validation evidence.
- Existing [CHIEF](../aiops/chief/notes.md) offers hierarchical attribution and should be compared, not duplicated.
- [Evidence provenance](../../concepts/aiops/evidence-provenance.md), [Verification](../../concepts/aiops/verification.md), and the [Agent System Operations survey](agent-system-operations.md) provide context.
