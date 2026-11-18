# AgentOps research gaps

## Ground truth is more than a final error marker

Useful attribution labels distinguish earliest unrecoverable root step, responsible agent, fault type, enabling condition, propagation steps, terminal symptom, and uncertainty. AgentRx separates critical failure from earlier recoverable errors; TraJudger separates root steps from conduits. Annotation still needs expert judgment and can miss hidden state.

**Opportunity:** adjudicated, evidence-linked causal traces with recoverability labels, annotator disagreement, and abstention.

## Observability contracts remain incomplete

Plain logs omit which context the model saw, tool schema/version, shared state, compaction, delegation dependencies, environment state, and verification result. Trial by Trace scores harness evidence separately; AgentRx adapters demonstrate that normalized IR cannot recover uncaptured facts.

**Opportunity:** event schema with provenance/visibility, privacy redaction, missing-vs-zero semantics, and criterion-linked evidence.

## Semantic judgments need calibrated evidence

LLM judges can prefer a fluent unsupported narrative, anchor on downstream symptoms, conflate failure types, or lose dependencies in long context. TraJudger adds specialists and graph constraints; AgentRx supplies violation evidence and an inconclusive option; PROBE gates guidance.

**Opportunity:** calibration, evidence ablation, blind adjudication, selective prediction, and source-span support. Include false attribution on successful runs.

## Detection and attribution are often conflated

Starting from known failed runs enables retrospective diagnosis without measuring when failure could have been detected. Detection delay, false positives, cost, and prevention of propagation remain undermeasured.

**Opportunity:** sequential evaluation revealing evidence only as it arrives, with cost-sensitive detection and intervention metrics.

## Diagnosis is not recovery

PROBE reports 65.37% Top-1 diagnosis versus 21.79% one-retry recovery in its protocol. TraJudger reports human prompt/schema refinements. AgentRx does not repair. A retry can repeat actions, change state, or claim success without restoring service.

**Opportunity:** external verification, regression/repeated-action measures, preconditions, rollback, and comparisons among advice, retry, workflow change, and human approval.

## Benchmarks and governance

AgentRx labels 170 trajectories; Trial by Trace uses mechanism tasks and one selected run per cell. These are valuable controlled assets but not a production-frequency sample with drift, harness upgrades, or changing policies.

**Opportunity:** repeated cross-model/harness/domain evaluations with uncertainty, representative and stress splits, versioned artifacts, privacy-conscious capture, review, canary, rollback, and post-change monitoring.

## Promising combinations

- AgentRx’s checkable constraints + TraJudger’s explicit propagation graph.
- Trial by Trace’s Agent/Harness separation + sequential AgentRx-style attribution.
- PROBE’s bounded guidance gate + external verification and rollback from operational RCA.
