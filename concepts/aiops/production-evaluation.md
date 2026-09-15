Status: evolving

# Production Evaluation in AIOps

## Definition

Production evaluation distinguishes whether a method uses real operational data, is evaluated at production-like scale, or is actually deployed in a live operational workflow. These are separate claims.

## Why It Matters

RCA systems face permissions, latency, tool cost, changing topology, missing evidence, privacy constraints, and operator escalation in production. A benchmark on injected faults or a retrospective dataset can measure correctness without measuring those operational constraints.

## Core Mechanism

Record at least three axes separately:

- **Production data:** real incidents or telemetry collected from an operating system.
- **Production-scale evaluation:** the experiment exercises a system size, incident volume, or latency target representative of operations.
- **Production deployment:** the method is integrated into a live workflow and its outputs affect or support real operators.

Also distinguish injected/synthetic faults from historical incidents, and root-cause labels from operator usefulness or remediation success.

## Typical Architecture

```text
offline benchmark / retrospective records
→ correctness and evidence evaluation
→ latency / cost / scale evaluation
→ human-in-the-loop operational trial
→ monitored deployment with escalation
```

The stages may not all be present in one paper.

## Example

LLMGuard reports 84 real LMaaS incidents and deployment in an environment with more than 10,000 accelerators, with SRE validation for high-stakes mitigation. Comfey reports 22 months of live Azure operation and about 19,500 triaged incidents, so it provides stronger deployment evidence for triage than for causal RCA. RCAgentBench has public injected-fault cases in a microservice testbed but does not demonstrate production deployment. These should not receive the same “production” label (Sources: [LLMGuard note](../../papers/aiops/llmguard/notes.md), Sec. V; [Comfey note](../../papers/aiops/comfey/notes.md), Sec. 4.1–4.5; [RCAgentBench note](../../papers/aiops/rcagentbench/notes.md), Sec. III).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Multimodal Telemetry](multimodal-telemetry.md)
- [Topology-aware RCA](topology-aware-rca.md)

## Representative Papers

- [LLMGuard](../../papers/aiops/llmguard/notes.md) — production LMaaS deployment, latency, cost, and human gating.
- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — controlled public benchmark and process metrics.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — production records and human feedback, with deployment mode requiring qualification.
- [KAT](../../papers/aiops/kat/notes.md) — commercial telecom deployment and operational outcome metrics.
- [Comfey](../../papers/aiops/comfey/notes.md) — 22-month Azure deployment with triage ownership labels, latency, mitigation, cost, and fallback measurements; not a direct physical-RCA evaluation.
- [AIM](../../papers/aiops/aim/notes.md) — controlled 100-sample, fault-injected/testbed evaluation with human judgments and plan-to-code execution; no live production deployment.

## Advantages

- Prevents inflated claims about “real-world” validity.
- Encourages reporting operational cost, latency, scale, intervention, and coverage.
- Makes benchmark-to-deployment gaps visible.

## Limitations

- Production data are often private and labels may be incomplete or operator-dependent.
- Large scale alone does not show causal correctness or generalization.
- Human-in-the-loop usefulness does not equal autonomous remediation success.

## My Understanding

“Production” is a vector of evidence, not a binary badge. A strong AIOps paper should state which axis it supports and which remains unknown.

The first five-paper batch demonstrates the distinction: RCAgentBench is a public injected-fault testbed; StaR uses synthetic/public benchmark data; CAUSALDX uses private production records with human feedback; LLMGuard reports production deployment and real incidents; KAT reports commercial deployment and longitudinal operational outcomes. These claims are not interchangeable.

## Open Questions

- How can network RCA papers report privacy-preserving but reproducible production evaluation?
- What common metrics combine correctness, time-to-diagnosis, evidence quality, safety, and operator effort?
