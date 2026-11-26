# NIKA — A Network Arena for Agent Troubleshooting

## Identity and evidence status

- **Title:** *A Network Arena for Benchmarking AI Agents on Network Troubleshooting*
- **Authors:** Zhihao Wang, Alessandro Cornacchia, Alessio Sacco, Franco Galante, Marco Canini, Dingde Jiang.
- **Version / venue:** arXiv:2512.16381v1, 2025-12-18; the arXiv record does not list a conference venue. [Paper](https://arxiv.org/abs/2512.16381)
- **Official project:** [sands-lab/nika](https://github.com/sands-lab/nika).
- **Local source:** [`NIKA_2512.16381.pdf`](../../../sources/papers/benchmark/NIKA_2512.16381.pdf). The Engine selected NIKA and read selected sections (`sections_only`); its independent Judge was stopped before producing a result. This note therefore does not claim independent acceptance.

## Motivation and system

NIKA addresses the lack of accessible, standardized environments for evaluating agents that investigate network faults through tools. Rather than score a static diagnostic answer only, it orchestrates a simulated network, issue injection, traffic, observability, agent-facing tools, and evaluation. The paper uses Kathará-based emulation, not live production networks.

The paper benchmark defines five network scenarios and 54 issue types, yielding 640 incident configurations. Four scenarios support small, medium, and large topologies averaging approximately 11, 27, and 101 nodes. The paper’s experiments use a 150-incident subset; it reports releasing more than 900 reasoning traces. The current repository has since grown and its present README counts must not be substituted for the paper’s versioned numbers.

## Tasks, evidence, and ground truth

An incident is organized around `(network scenario, issue, traffic)` and can ask for detection, localization, or root-cause analysis. Scenarios supply topology, device/protocol configuration, traffic generation, injected issue, telemetry instrumentation, and diagnosis tools. Root-cause truth is tied to the injected issue specification and its affected device/component; the paper does not describe blinded production-incident adjudication. The injection specification is reproducible ground truth for the emulated task, but is not automatically proof of real-world causal validity.

The Agent Access Layer (AAL) exposes 30+ MCP tools for active measurement and diagnostic operations. It records tool inputs, timestamps, responses, and snapshots of network state at each call, enabling trajectory inspection. This makes observed evidence and tool use auditable, although a logged observation does not prove it informed the final answer.

## Evaluation and agent-specific design

Goal-specific evaluators score detection, localization, and RCA. The paper also reports time-to-detection, input/output/reasoning tokens, tool invocations and tool errors. During diagnosis it tracks flow latency, packet loss, and violations of user-defined SLOs. These are distinct measurements: diagnosis accuracy, investigation cost, and the effect of investigation on network service should not be compressed into one number.

Agents perform interactive, multi-step diagnosis through tools in a configured scenario. The benchmark records trajectories and state feedback. It does **not** evaluate remediation actions: the paper explicitly leaves correctness and safe/non-disruptive mitigation for future work. AAL runtime access controls do not substitute for a repair-safety benchmark.

## Data quality and shortcut risks

**Paper-reported:** incident diversity spans network scenarios and topology sizes; increasing topology size degrades localization/RCA and raises context/token cost. Structured MCP interfaces can themselves affect tool errors and agent performance.

**Risks to test, not proven leakage:** agents may infer issue labels from scenario templates, injected configuration artifacts, or deterministic task wording; a fixed topology/issue split may expose repeated patterns. Run held-out issue, location, topology, and traffic tests before interpreting accuracy as general troubleshooting capability. The paper’s ground truth is injection-grounded and therefore should not be described as independently verified production ground truth.

## Code and openness

The [official repository](https://github.com/sands-lab/nika) documents `src/`, `benchmark/`, `config/`, `docs/`, and `tests/`, with network emulation, an agent sandbox, and MCP access. The current repository is an evolving release and differs from the paper snapshot. This task inspected paper and project documentation, not a pinned checkout or executable code; no dependencies were installed and no incident was run.

## Relevance

NIKA is the clearest of these six for agent investigation traces, tool-call/resource accounting, and service impact while diagnosing. It complements CTBench’s expert-route criteria and AgenticOpsEval’s evidence labels. A benchmark for our network data could adopt trajectory observability but should add explicit evidence sufficiency, safe intervention tests, hidden fault/topology splits, and realistic uncertainty. See [comparison](../../../notes/benchmark/benchmark-comparison.md).
