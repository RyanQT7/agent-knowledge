# AIOps Questions

Status: evolving

This file contains AIOps-specific questions raised during formal reading. Statuses are scoped to the current evidence and should not be treated as permanent answers.

## Questions from RCAgentBench

1. **How should the candidate root-cause space be defined for network incidents?**
   Status: Open. RCAgentBench provides controlled service/pod/node levels but does not specify a general numeric candidate-space protocol for heterogeneous network components.

2. **How should metrics, logs, traces, topology, and traffic evidence be aligned when their time windows and provenance differ?**
   Status: Open. RCAgentBench exposes separate tools and windows, but does not solve the general network telemetry alignment problem.

3. **How much of an Agent RCA result comes from the model versus tool design, hierarchy, and available evidence?**
   Status: Partially Answered. Tool and hierarchy ablations show that the observation interface and structural prior materially affect results (Source: RCAgentBench, Sec. V-C–D, pp. 7–9).

4. **Can service-call topology benefits transfer to physical network topology without treating dependency as physical causality?**
   Status: Open.

5. **How should unknown, multiple, or correlated network root causes be evaluated?**
   Status: Open. The controlled benchmark does not establish an open-set, multi-root network protocol.

## Cross-paper Questions for Batch 1

6. **What is the common boundary between detection, localization, RCA, diagnosis, explanation, and remediation?**
   Status: Partially Answered. RCAgentBench makes localization, fault type, explanation, and path length separate metrics; later papers will test whether this separation holds across production systems.

7. **Which topology semantics are actually supported by a given method?**
   Status: Open. A service graph, dynamic causal graph, anomaly graph, SOP tree, and physical network graph should not be treated as equivalent.

8. **Does a graph used by an RCA method represent physical causality, predictive dependency, or an operational reasoning structure?**
   Status: Open.

9. **Can process-level metrics such as evidence coverage and diagnostic path length be made comparable across LLM, classical, and human-guided RCA?**
   Status: Open.

10. **What ground truth can support production-scale RCA when incidents have delayed effects, multiple causes, or incomplete repair records?**
    Status: Open.

11. **Does adding an LLM improve root-cause correctness, or mainly evidence organization and explanation?**
    Status: Open.

12. **How should a network RCA system handle erroneous, missing, delayed, or contradictory telemetry without accumulating a misleading explanation?**
    Status: Open.
