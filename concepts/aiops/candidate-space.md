Status: evolving

# Candidate Space in AIOps RCA

## Definition

The candidate space is the explicitly defined set of entities, faults, or hypotheses that an RCA system may consider as possible roots. It includes both the candidate **granularity**—for example device, interface, link, service, metric, component, or fault type—and the rules that determine which candidates are eligible.

## Why It Matters

RCA correctness cannot be interpreted without knowing what the system was allowed to predict. Candidate granularity affects Top-k scores, pruning affects search cost and recall, and a mismatch between candidate labels and ground truth can make a result look correct or incorrect for the wrong reason. A closed candidate set also differs fundamentally from open-set or unknown-cause diagnosis.

## Core Mechanism

A candidate-space workflow is:

```text
domain/entity universe
→ candidate representation and granularity
→ structural or evidence-based pruning
→ candidate ranking / hypothesis testing
→ root attribution with aligned ground truth
```

Important dimensions are:

- **Universe:** what entities or fault types exist in scope.
- **Granularity:** whether the output is a device, interface, link, service, step, metric, or cause chain.
- **Constraints:** topology, dependency, hierarchy, temporal order, or operational knowledge.
- **Pruning:** how a large universe is reduced, and what recall assumptions this introduces.
- **Root multiplicity:** single-root, multi-root, or an explicit unknown/abstain outcome.
- **Evaluation alignment:** whether the prediction unit matches the ground-truth unit.

## Typical Architecture

```text
raw evidence
→ map evidence to entities / fault hypotheses
→ construct or enumerate candidates
→ apply hierarchy, topology, or dependency constraints
→ rank and verify candidates
→ report root, uncertainty, and unsupported/unknown status
```

## Example

The current papers show that candidate space is domain-specific:

- RCAgentBench considers service/pod/node and fault-type diagnosis in a microservice benchmark.
- CAUSALDX selects and expands anomaly-node hypotheses.
- LLMGuard prunes a guide-covered SOP tree toward root leaves.
- CHIEF narrows from subtask to Agent to exact step and outputs one Agent-step pair, with counterfactual attribution.
- FlowFixer attributes a failed agentic workflow to a workflow node and a finite failure taxonomy.

These are structurally related but not one common candidate protocol (Sources: [RCAgentBench note](../../papers/aiops/rcagentbench/notes.md), Sec. III–V; [CAUSALDX note](../../papers/aiops/causaldx/notes.md), Sec. 4; [LLMGuard note](../../papers/aiops/llmguard/notes.md), Sec. IV; [CHIEF note](../../papers/aiops/chief/notes.md), Sec. 3–4; [FlowFixer note](../../papers/aiops/flowfixer/notes.md), Sec. III–IV).

## Related Concepts

- [Root Cause Analysis](root-cause-analysis.md)
- [Topology-aware RCA](topology-aware-rca.md)
- [Evidence Provenance](evidence-provenance.md)
- [Production Evaluation](production-evaluation.md)

## Representative Papers

- [CHIEF](../../papers/aiops/chief/notes.md) — hierarchical subtask/Agent/step candidate reduction and counterfactual attribution.
- [FlowFixer](../../papers/aiops/flowfixer/notes.md) — workflow-node attribution with a finite failure taxonomy.
- [RCAgentBench](../../papers/aiops/rcagentbench/notes.md) — component/fault-type localization with hierarchy context.
- [CAUSALDX](../../papers/aiops/causaldx/notes.md) — anomaly-node selection, expansion, and verification.
- [LLMGuard](../../papers/aiops/llmguard/notes.md) — SOP-tree candidate pruning.

## Advantages

- Makes search cost and output semantics explicit.
- Supports coarse-to-fine reasoning instead of unconstrained generation.
- Helps align RCA metrics with the actual root granularity.
- Provides a place to represent unknown, ambiguous, and multi-root outcomes.

## Limitations

- Pruning can remove the true root and create hidden recall loss.
- Hierarchy is not automatically topology, and a candidate relation is not automatically causal.
- Closed taxonomies underrepresent novel or compound faults.
- Large or changing infrastructure inventories require versioned entity mappings and efficient retrieval.

## My Understanding

Candidate space is the contract that connects evidence to an evaluable RCA output. For Network AIOps, a useful space may need multiple linked levels—device, interface, optical module, link, path, and fault type—rather than forcing all cases into one label. A physical topology may constrain which candidates are possible, while dynamic dependencies and telemetry can provide softer ranking evidence. This combined network design remains a research hypothesis, not a conclusion established by the current papers.

## Open Questions

- How should device/interface/link/module/path candidates be represented together?
- How can pruning preserve open-set and multi-root recall?
- How should Top-k be evaluated across hierarchy levels?
- What evidence is sufficient to add an unknown candidate rather than force a closed label?
