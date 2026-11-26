# OpenRCA：大规模企业遥测中的 LLM 根因分析

## 论文身份、来源与阅读范围

- **标题：** *OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?*
- **作者：** Junjielong Xu, Qinan Zhang, Zhiqing Zhong, Shilin He, Chaoyun Zhang, Qingwei Lin, Dan Pei, Pinjia He, Dongmei Zhang, Qi Zhang。
- **发表：** ICLR 2025。[正式论文 PDF](https://proceedings.iclr.cc/paper_files/paper/2025/file/d29b8d53678015079e1d245c023e49d2-Paper-Conference.pdf) · [项目页](https://microsoft.github.io/OpenRCA/) · [官方代码](https://github.com/microsoft/OpenRCA)
- **本地材料：** [PDF](../../../sources/papers/benchmark/OpenRCA_ICLR2025.pdf) 与同目录抽取文本；论文 PDF、正文和附录均已阅读。仓库静态检查快照为 `2a481ae63cb045c3eadbeca9eddaa10ec1151979`。
- **边界：** 未下载约 68 GB 数据、未安装依赖、未运行 Agent。当前代码已迭代，以下论文结果与当前代码分别说明。

## 1. 研究问题：如何让 RCA 任务接近真实维护工作

OpenRCA 关注软件系统上线后的故障诊断。作者认为，既有 LLM 工作更多研究代码生成，而 RCA 需要从长时间窗、多系统、多模态遥测中找出导致故障的组件、时间或原因。论文贡献不是新的 RCA 算法，而是将企业历史故障整理为统一数据集、把不同 RCA 输出形式转成受控问题，并比较直接采样与工具型 Agent。

该设计回答“LLM 能否在这些经过整理的企业案例上定位根因”，并不直接回答“Agent 能否在任意生产环境自主排障”：输入已经关联到一个失败记录和给定时间窗，部分实验还给出组件/原因候选空间。

## 2. 数据集：从挑战赛故障记录到可回答任务

### 2.1 来源、规模与模态

数据来自历届 AIOps Challenge 的三个企业软件系统。Telecom 提供 metrics 和 traces，Bank 与 Market 另有 logs（Appendix A.1–A.2、Table 5）。Table 1 给出 335 个保留案例：Telecom 51，Bank 136，Market 148；合计约 68.5 GB，包含 metrics、logs、traces。论文报告系统中 73 个不同根因组件和 28 类原因；三个系统分别约 17.6、26.4、24.5 GB，原始行数分别约 154M、248M、121M。不同系统在服务/Pod 数、故障类别数和冗余容错机制方面不同，不能把“335”理解成均匀覆盖的独立故障类型样本。（§2，Table 1）

论文从 1,753 条较大的故障记录池开始构造数据。先按系统及记录条件筛选，再进行抽样以控制规模差异；从 1,753 条平衡抽样至 412 条，之后三位有经验工程师校准标签与数据，去除遥测缺失、根因不可追溯、故障时间与异常信号不匹配的案例，最终保留 335 条。这个校准提高了可诊断性，也使评测对象成为“经过工程师筛选的可用故障”，而不是线上事件总体的无偏样本。（§2.4，Figs. 2–3 与 Appendix A.5）

校准先统一遥测与标签命名，再根据已有根因记录定向查看根因组件和对应原因所指的信号。时间校准检查标签附近的观测点是否为异常段的首个点。Appendix A.5 的 Fig. 10 用 frontend-2 磁盘读 I/O 的尖峰对齐标签，Fig. 11 展示不匹配而剔除的例子。工程师各自检查再交叉复核，412 例中 8 例初始有分歧，经讨论达成共识。流程有助于提高直接证据的可核查性，也可能降低只凭下游症状可推断的故障占比。论文没有量化这个选择偏差，或给出与 RCABench 的直接对照。

### 2.2 Ground Truth 与任务生成

根因由三个可组合元素表示：

1. **component**：组件/服务/Pod 等实体；
2. **time**：根因发生时间；
3. **reason**：故障原因。

论文把每条记录转为七种任务之一，分别询问三个元素的所有非空子集。任务给出约 30 分钟的分析时间窗和窗口内故障数量，输出只要求对应元素。GPT‑4o 根据结构化任务规格生成更自然的问题，再由人工核验；因此生成的是自然语言表述，目标元素和答案仍锚定在原始故障记录中。（§2.4、Appendix A.6）

**具体任务例子：** 某个云服务在指定半小时内发生故障，问题只要求指出根因组件。评测器只应按组件字段判分；模型即使在解释中另猜一个故障原因，也不能将那段文字视为“原因回答已验证”。论文的案例分析也显示，答案字段、模型叙述和数据集根因字段必须分开核对。（Appendix C.3）

候选组件和原因集合出现在任务/提示协议中，降低了答案格式的歧义，但将任务变成一定程度的闭集选择。论文每个任务最多涉及窗口内多个失败记录；多故障时，输出应逐个对应，不可只取最显著异常。时间答案使用与标注点 ±1 分钟的容差。多个合理根因解释及标签不确定度没有作为普遍字段发布，因而不能假定数据已完整表达生产现场的因果争议。（§2.4，Appendix A.7）

## 3. 方法：采样基线与 RCA-Agent

```mermaid
flowchart LR
  A[失败记录 + 30 分钟窗口] --> B[选择任务所需根因元素]
  B --> C[筛选或下采样多模态遥测]
  C --> D[LLM 直接分析 / RCA-Agent 查询]
  D --> E[JSON 根因元素]
  E --> F[元素级和查询级评分]
```

### 3.1 三种遥测读取方式

- **Balanced sampling：** 每分钟仅取首条观测，各模态共用这个初步降采样步骤；逐指标文件随机轮取不重复的 KPI 类型，直到数量与 Oracle 一致。跑三次取中位数，以减小上下文并降低高频指标对输入的支配。
- **Oracle sampling：** 利用 Ground Truth 中已知的相关 KPI，把候选从约 1,263 项缩到 53 项。由于特征筛选使用答案信息，它是上界式诊断设置，不是可部署的公平发现流程。
- **RCA-Agent：** 不把所有遥测文本一次塞进提示，而由 Controller 逐步选取调查方向，Python Executor 在状态化分析环境中执行代码、读取全量关联文件并把查询结果反馈给 Controller。

RCA-Agent 的论文流程先看 Metrics，再依据发现扩展到 Traces、最后查 Logs；Controller 负责规划和归纳，Executor 负责在数据上运行代码。这样把模型上下文从原始遥测全集缩减为按需查询结果，同时也引入新的变量：生成代码是否执行成功、错误反馈是否可用、Agent 是否真正覆盖其他模态。论文未把每条分析代码或每个证据引用作为单独的正确性标签。（§3，Fig. 4）

Controller 将数据目录、schema 和调查指令传给 Executor。后者在同一问题内复用生成代码和 Python kernel 变量，成功结果返回 Controller 决定下一次查询，异常堆栈供 Executor 修订，空结果也可触发改查。§5 Table 4 的执行失败子集中 Gemini 从总体 2.69% 对照到 0.85%，作者观察 Claude、GPT 更常利用空结果或异常恢复。该子集并非随机干预，误差容忍是有证据支持的解释，仍可能有问题难度等混杂。（§3 Fig. 4、Appendix B）

## 4. 评分：答案完整性与多元素难度

Table 2 报告 **Correct**（所问字段全部正确的查询比例）和 **Partial**（至少有一个所需字段正确的比例）。Partial 包含正确完整的答案，不能理解为与 Correct 互斥的类别。

| 模型 | Balanced Correct | Oracle Correct | RCA-Agent Correct | RCA-Agent Partial |
| --- | ---: | ---: | ---: | ---: |
| Claude 3.5 Sonnet | 3.88% | 5.37% | 11.34% | 17.31% |
| GPT-4o | 3.28% | 6.27% | 8.96% | 17.91% |
| Gemini 1.5 Pro | 6.27% | 7.16% | 2.69% | 6.87% |
| Llama 3.1 Instruct | 2.99% | 3.88% | 3.28% | 5.67% |

简单算例（解释性示例）：若任务问 component 和 reason，预测组件正确、原因错误，则该查询可计入 Partial，但不计入 Correct；若任务只问 component，相同预测则可能属于完全正确。比较不同数据集或模型时，任务所需字段数会改变“完全正确”的门槛。

Easy/Mid/Hard 分组分别要求 1、2、3 个根因元素。Table 3 中多个模型从 1 个字段增加到 2 个字段时准确率显著下降；三字段任务在表列方法中为 0%。因此平均准确率既受推理能力影响，也受任务字段组合构成影响。Oracle 高于 Balanced 是预期现象，因为其使用真实根因指导信号筛选；RCA-Agent 对 Claude/GPT 有提升，但对 Gemini 下降，不能笼统说 Agent 总是更好。（§4.1–4.2、§5，Tables 2–3）

Appendix D Table 8 按论文的随机猜测口径，Reason、Component、Time 基线分别为 11.06%、4.92%、3.33%。用绝对正确率减随机基线后，Claude Agent 三字段增益分别为 8.61、13.08、10.90 个百分点，解释了为何 Reason 原始正确率较高仍更难改善。Time 的 1/30 保留为论文基线设定。实验选择六个支持至少 128K 上下文的模型，具体 checkpoint 见 Appendix C.1；开放模型预算下仅 Llama 比较 Agent。采样提示约 100K Token。

## 5. 案例与实验含义

附录给出 cloudbed-1 案例：任务只问某半小时内的根因组件。GPT‑4o 原始提示答对 `productcatalogservice`，而 CoT 提示生成了大量服务、容器、节点指标分析，叙述中把多个同时异常的组件混在一起。该例说明“更长的逐步解释”不等于证据更准确，也可能带来虚构或混淆；应按输出字段与原始指标逐项核查，而不以解释篇幅当质量。（Appendix C.3）


模型在较简单的 Telecom 案例上通常优于 Bank/Market；论文将差异联系到 telemetry 规模、根因类型数、Pod 数以及容错机制。三字段任务表现差，支持“多字段诊断更难”的结论；但低准确率也可能受候选空间、切分和不均衡影响，不能单独当作模型生产能力的测量。论文主要评价最终答案，不提供独立的证据充分性、工具效率、延迟或修复安全分数。（§5、Fig. 5、Tables 2–4）

Fig. 7（§6）的 Bank 窗口为 23:00–23:30。Claude 先按 KPI 找持续异常，沿 trace 的高频调用依赖缩到 Tomcat01，再由日志的 TCP 波动推测丢包。真值是 Tomcat01、23:18、network latency；任务只要求组件，因此组件正确、reason 被忽略，尽管预测 packet loss 与标签不一致。§5 Fig. 6 的长调查轨迹相关性和 Appendix C 的 CoT 提示对照针对不同机制：在固定采样证据上多写分析无法补齐缺失观测，多轮查询可以获得新证据，但增加调用与执行错误机会。

## 6. 数据质量、Shortcut 与外部效度

### 论文实际采取的措施

- 工程师确认根因记录与遥测是否可对齐；缺失数据和无法追溯案例被排除。
- 时间窗内事件数和所需输出字段写入任务规格。
- 多系统数据提供不同规模和故障类别覆盖。
- 使用自然语言任务生成，并对任务作人工校验。

### 需要谨慎看待的风险（分析，不是论文已证实的缺陷）

- 提供候选组件/原因及已知时间窗使任务更接近闭集搜索，可能掩盖开放世界的候选发现能力。
- Oracle sampling 直接利用 GT 筛指标，是上界而非常规推理条件。
- 故障时间落在已知 30 分钟窗口内，时间定位任务并非从无边界全时序发现事件。
- 数据经人工筛选后更可解，但筛选比例、被排除类别分布和不确定标签的公开程度会影响外推。
- 多模态最终答案正确不能说明模型依据了正确模态；论文没有标准化的证据引用或过程因果评分。

## 7. 官方源码静态分析

本地代码位于 `sources/code/benchmark/openrca/`，SHA `2a481ae63cb045c3eadbeca9eddaa10ec1151979`；只读静态检查，未运行。

- `main/generate.py`：从故障记录及任务规格生成查询，按可回答元素构造任务并处理时间窗/碰撞；它连接结构化标签到自然语言任务。
- `main/evaluate.py`：读取结构化预测并比较要求的 root-cause elements。当前实现包含多预测排列与 component/reason 精确匹配、时间容差和元素分数；论文 Table 2 的查询级 Correct/Partial 汇总不可与实现内部逐元素分数混为一谈。
- `rca/run_agent_standard.py` 与 `rca/baseline/rca_agent/{controller.py,executor.py}`：对应 Controller 规划、Python Executor 执行查询、输出反馈并记录轨迹的 Agent 工作流；当前版本还包含安全执行边界及相关测试。
- `rca/run_sampling_balanced.py`、`rca/run_sampling_oracle.py`：对应两种采样协议；Oracle 实现使用工程师确定的答案相关 KPI 集合，复现实验时必须标记为 oracle 条件。
- 数据需通过项目发布路径另行取得，本轮未下载。

## 8. 对 AIOps Benchmark 的启发

OpenRCA 展示如何把原始事件字段拆成可组合任务，形成明确难度阶梯，也展示工程师校准在真实系统遥测中的价值。若用于 Agent 基准，应额外记录执行了哪些查询、查询结果如何支持答案、实际输入/输出 Token、耗时、工具错误与证据定位；不要只给模型一组由标签产生的候选。对多个根因字段应同时报告字段级正确率和整例 exact-match，并公开人工筛选、无法判断与被剔除样本的谱系。

关联：[RCABench](../rcabench/notes.md) 的有效故障门禁、[AgenticOpsEval](../agenticopseval/notes.md) 的证据标签及[综合比较](../../../notes/benchmark/benchmark-comparison.md)。
