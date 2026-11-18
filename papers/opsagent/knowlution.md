# KnowLution: A Multi-Agent Framework for Execution-Oriented Autonomous Operations in Production Supercomputers

## Bibliographic record

- **Authors:** Yuqi Li, Liquan Xiao, Yongqian Sun, Xiuhong Tan, Aiwen Yu, Jinghua Feng, Lei Tao, Tongqing Zhou, Yuan Yuan.
- **Status:** Listed by NKU as IEEE ISSRE 2026. The paper's six-page camera-ready PDF is linked from the [NKU publications page](https://nkcs.iops.ai/publications/); the program entry places it in the ISSRE Operations / Industry program. No arXiv record was found in the author/lab materials checked.
- **Primary sources:** [NKU PDF](https://nkcs.iops.ai/wp-content/uploads/2026/08/2026289015.pdf), [NKU publications](https://nkcs.iops.ai/publications/).
- **Local PDF:** `sources/papers/opsagent/knowlution.pdf` (ignored by Git).
- **Official code:** Not publicly found; no repository SHA/license identified.
- **Reading status:** Full six-page paper read.

## System and operating workflow

KnowLution handles execution-oriented HPC operations such as jobs, software, resource scheduling, and failures. Unlike a diagnosis-only agent, it explicitly models runtime state, workflow routing, execution constraints, and tool orchestration.

**Pipeline (Sections III–V; Figure 2):** request/alert → Task Parsing Agent extracts intent, workflow type, and parameters or rejects out-of-scope work → maps request to a predefined operational workflow → System Awareness Agent queries live state and logs/metrics → Anomaly Analysis Agent assesses evidence → Strategy Planning Agent creates ordered, parameterized tool steps → Operation Execution Agent orchestrates commands/tools under capability, dependency, permission, and risk constraints → Report/Summarization Agent records results and updates the knowledge base. State-aware retrieval combines runtime state, O&M documents, and request context.

- **Multi-Agent roles:** Task Parsing, System Awareness, Anomaly Analysis, Strategy Planning, Operation Execution, Report Generation/Summarization are separate named roles in the design. It is centralized/shared-state collaboration, not evidence that six independent LLM agents are all necessary. The paper's ablation isolates workflow routing, state-aware retrieval, and tool orchestration, not the marginal value of each role.
- **Planning and tools:** workflow templates provide structure; strategy planning chooses tools and ordering while enforcing parameter completeness, dependencies, capability, permissions, and risk limits. Write actions require sandbox verification and explicit human confirmation. This is constrained execution planning, not open-ended autonomous remediation.
- **Memory:** dialogue/context plus operational documents, cases, configurations, and runtime state. Outputs feed a KB update path. The paper does not specify a cross-incident memory update validation protocol in the same depth as OpsMem.
- **Verification/recovery:** tools return execution results; a final report closes the task. Write operations are gated by human approval. The study's task-success metric and illustrative cases do not provide a large-scale independently audited recovery-verification measure.

## Evidence and limitations

**Paper evidence (Sections IV–V, Tables I–III):** 200 anonymized production-derived tasks across ten categories, compared with LLM-only, RAG, ReAct, EasyTool, and MetaGPT. Reported task success rate is 85%, BLEU-4 25.7, mean latency 28.47 seconds, and tool execution success 70/76 (92%). Removing tool orchestration lowers TSR from 85% to 54%; removing routing to 72%; removing state-aware retrieval to 78%. The authors also report deployment inside the Tianhe-NG intranet, with write operations requiring confirmation and operator feedback. Their job failure case ends successfully after changing a configuration, but the paper's aggregate deployment results are primarily feedback/perception measures.

The benchmark is production-derived rather than a public live-system replay; task counts are modest and data/tool environments are proprietary. BLEU-4 is a weak proxy for operational correctness. Tool-success rate has attempted calls as denominator and does not itself establish safe action or recovered service. No public code/data release was found, so independent reproduction is limited.

## Research value

KnowLution is a strong complementary paper for operational execution safety, especially against diagnosis-only systems. It emphasizes permission/precondition validation and human confirmation. For Network AIOps, translate its state-aware planner into read-only diagnostic stages first, then controlled change proposals, with topology/configuration evidence, rollback, and deterministic recovery checks. See [Agentic Incident Management](../../concepts/aiops/agentic-incident-management.md), [Verification](../../concepts/aiops/verification.md), and [Operational Knowledge](../../concepts/aiops/operational-knowledge.md).
