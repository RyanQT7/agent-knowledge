Status: evolving

# Verification in AIOps and Agentic Operations

## Definition

Verification is an explicit check of whether an evidence item, candidate, diagnosis, tool result, repair, or recovery outcome satisfies independent or predefined criteria. It is not a synonym for an LLM producing a second confident explanation.

## Why It Matters

Operational systems can reach a plausible answer for the wrong reason, use stale or incomplete evidence, select the wrong candidate, or apply an unsafe action. Separating what is being verified and who verifies it makes RCA and remediation claims auditable and prevents a testbed patch or textual self-check from being mistaken for production recovery.

## Core Mechanism

Verification has multiple possible targets:

```text
evidence validity
→ candidate / graph consistency
→ RCA or diagnosis
→ proposed action / repair
→ execution outcome
→ recovery state
```

It also has multiple possible verifiers:

```text
deterministic rule or schema
→ topology/dependency check
→ fresh telemetry or tool re-query
→ independent algorithm / critic
→ controlled execution result
→ human approval or adjudication
```

The required strength depends on the target and operational risk. A verification result should retain its source, criteria, time, and uncertainty.

## Typical Architecture

```text
claim / candidate / action
→ specify acceptance criteria
→ run an independent or fresh check
→ compare observed result with criteria
→ accept, reject, retry, abstain, escalate, or rollback
```

For a state-changing operation, a cautious lifecycle is:

```text
diagnosis
→ safety/precondition check
→ human gate when needed
→ controlled execution
→ fresh observation
→ recovery verification
→ rollback or knowledge update
```

## Example

The current papers verify different objects:

- Cloud-OpsBench verifies diagnostic process properties such as tool relevance, coverage, invalid actions, redundancy, and zero-tool guessing in a deterministic snapshot environment.
- CAUSALDX and LLMGuard use observation/tool or SOP checks to constrain candidate diagnosis.
- CHIEF verifies offline Agent-step attribution through virtual-oracle consistency, hierarchical backtracking, and counterfactual analysis.
- FlowFixer checks workflow patches structurally and semantically before dynamically executing them on test inputs.
- ChatRCA places humans at data-ticket and root-cause adjudication points.

These mechanisms are complementary, not interchangeable. None of them alone establishes an independent network recovery protocol (Sources: [Cloud-OpsBench note](../../papers/aiops/cloud-opsbench/notes.md), Sec. 2.4; [CAUSALDX note](../../papers/aiops/causaldx/notes.md), Sec. 4.3; [LLMGuard note](../../papers/aiops/llmguard/notes.md), Sec. IV; [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 4; [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. III; [ChatRCA note](../../papers/aiops/chatrca/notes.md), Sec. 4.2).

## Related Concepts

- [Evidence Provenance](evidence-provenance.md)
- [Candidate Space](candidate-space.md)
- [Root Cause Analysis](root-cause-analysis.md)
- [Operational Knowledge](operational-knowledge.md)
- [Agentic Incident Management](agentic-incident-management.md)
- [Production Evaluation](production-evaluation.md)

## Representative Papers

- [FlowFixer](../../papers/aiops/flowfixer/notes.md) — symbolic pre-checks and dynamic workflow execution.
- [Cloud-OpsBench](../../papers/aiops/cloud-opsbench/notes.md) — process-centric trajectory and tool-use auditing.
- [CHIEF](../../papers/aiops/chief/notes.md) — oracle, graph, and counterfactual attribution checks.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — candidate observation verification.
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — SOP-tree and evidence-chain checking.
- [ChatRCA](../../papers/aiops/chatrca/notes.md) — human verification and adjudication.

## Advantages

- Separates plausible generation from accepted operational claims.
- Supports rejection, retry, abstention, escalation, and rollback.
- Makes evidence, tool use, actions, and outcomes auditable.
- Allows verification strength to be matched to risk.

## Limitations

- A check can validate only the criteria and state it observes.
- LLM-generated criteria, graphs, or critics can inherit the same model errors as the claim.
- Controlled test execution may not predict live recovery under drift, delay, or side effects.
- Independent verification can increase latency, cost, and human workload.

## My Understanding

Verification is a layered contract, not a single “self-check” step. For RCA, it may validate evidence freshness, candidate/graph consistency, or a diagnosis against an independent observation. For remediation, it must additionally validate permissions and safety before action, observe the actual result, and independently verify recovery afterward. The current literature supports pieces of this chain, but not a complete physical Network AIOps protocol.

A useful working strength ordering is:

```text
LLM self-check
< independent critic/model
< deterministic consistency check
< fresh tool/telemetry re-query
< controlled execution with observed outcome
< post-action recovery signal plus appropriate human gate
```

This is a cross-paper working synthesis, not a universal standard; a weaker check may be sufficient for a low-risk informational claim, while a high-impact action needs stronger evidence.

## Open Questions

- What is the minimum independent evidence for accepting a network root cause?
- How should evidence, candidate, repair, and recovery verification be composed?
- How should verification handle missing, delayed, conflicting, open-set, or multi-root evidence?
- Which recovery signals are independent enough from the repair generator?
- When should a human gate be mandatory?
