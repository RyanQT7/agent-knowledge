# Knowledge Dossier — Synthetic Time Series for Anomaly Detection in Cloud Microservices

## 1. Basic Information

- **English title**: Synthetic Time Series for Anomaly Detection in Cloud Microservices
- **中文译名**：面向云微服务异常检测的合成时间序列
- **Authors**: Mohamed Allam, Noureddine Boujnah, Noel E. O’Connor, Mingming Liu
- **Venue / year / CCF**: MLDS 2024（按论文正文所述接收）；本地版本 arXiv:2408.00006 / 2024 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `synthetic-cloud-microservices-arxiv2408.00006.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/Mohamed164/AD-microservice-app
- **Research area**: 云微服务数据集构建、负载合成与真实故障注入
- **Method tags**: microservices, fault-injection, load-synthesis, metrics, ground-truth

## 2. Research Scenario

研究面向云端微服务监控数据获取：真实线上故障难以反复触发，异常标签稀少，单纯数学合成的时间序列缺少系统运行背景。作者希望在可控云环境中形成包含正常服务需求变化、负载异常和基础设施故障响应的带标签数据。测试床部署于 AWS EKS，使用 Sock-Shop 与 Online Boutique 两个电商应用；Locust 产生用户流量，Istio / Prometheus、CloudWatch 和 Fluent Bit 等采集系统指标、服务指标和日志。（PDF §§3.1–3.5, pp.3–8）

输入包括用户到达 / 请求负载参数以及 FIS 故障注入模板；输出包括带时间戳的节点、Pod、服务指标序列和独立的负载 / 基础设施故障标签。论文的主要可观测序列为指标，不包含本版本的分布式 Trace 数据；日志被采集组件列出，但主要量化数据集清单是指标。异常标签来自注入计划和时间区间，因此偏向实验可控的窗口 / 时间点异常标注，而不是人工确认的生产事故根因。

## 3. Research Problem

在缺少真实故障标注、难以重复触发生产事故时，如何构造包含动态正常负载、负载异常、基础设施故障及可对齐指标标签的微服务数据？

## 4. Core Challenges

1. **正常负载并非平稳常数**：业务需求会有趋势和多周期变化。若只用恒定背景，检测器容易把常见日常峰谷错判为故障。（§3.2, Eq. 1）
2. **数学异常不等于系统故障**：直接在指标上加尖峰不能复现 CPU 压力、网络延迟、Pod 删除等系统机制引发的联动变化。作者用云环境故障注入将“故障动作”与被观测影响联系起来。（§3.3–3.4）
3. **负载异常与资源故障需分开标注**：请求突变可能是业务侧需求异常；CPU hog 或网络损失则是基础设施故障，两者影响路径不同。论文分别生成负载异常与 FIS 故障，但没有证明某一检测器能可靠区分所有并发情形。
4. **规模与观测成本**：云资源和多服务采集成本让实际故障样本难以大量构造。受控实验牺牲了生产环境的复杂度和多样性。（§3, §5）

## 5. Limitations of Existing Methods

### A. 正常业务负载

用户到达负载由基线、缓慢趋势、多周期分量和随机扰动构成：

N(t) = (1 + trend(t)) × base_load + Σᵢ Aᵢ[(sin(2πt/Tᵢ))² + wnᵢ(t)]

其中 trend(t) 由分段斜率形成；每个趋势区间有概率 p=0.01 出现突变；Tᵢ 和 Aᵢ 控制多个周期和振幅，wnᵢ(t) 为噪声。Locust 的 spawn rate 按相邻负载点左右导数的对称平均调节，使生成负载随时间曲线变化。（§3.2, Eqs. 1–2）

### B. 负载异常

Algorithm 1 以概率 p 选择持续时长 U(a,b)，对选定区间的用户负载乘以从 U(c,d) 采样的因子。该操作构造的是突增 / 突降式业务流量异常，而非某种明确根因（例如促销、爬虫、排队瓶颈）。基础正常负载和异常流量形态被分别控制与打标。（§3.3, Algorithm 1）

### C. 基础设施故障注入

使用 AWS Fault Injection Simulator 模板 / 注入程序，执行 Pod 或节点 CPU 压力、内存压力、网络延迟、丢包、I/O 压力、Pod 删除 / 节点重启等操作。Algorithm 2 随机选取目标资源和故障模板；标签由故障注入开始和持续时间产生。图示展示故障对指标的传播反应，例如网络丢包可推高尾延迟和错误率，CPU / 内存压力影响相应资源指标，Pod 删除导致服务重新调度。（§3.4, Algorithm 2, Figs. 4–6）

### D. 系统与数据

EKS 上运行 Sock-Shop、Online Boutique；Istio 负责服务网格，Locust 负载驱动。采集包括 25 个节点级指标 × 5 节点 = 125、18 个 Pod 指标 × 14 Pods = 252、9 个服务级指标 × 10 服务 = 90，总计 470 项指标。系统指标 / 服务指标的覆盖数量反映本实验部署，并非每种应用拓扑必然固定如此。（§3.1, Table 1）

论文示例运行持续 7 天并覆盖多种周期负载。故障参数示例包括 CPU 压力 100% 持续 4 分钟、内存压力 100% 持续 4 分钟、400ms 网络延迟 5 分钟、40% 丢包 2 分钟、I/O 压力 80% 持续 5 分钟；这些是实验配置示例，不应等同于生产事故严重程度。（§3.4–3.5, Tables 2–3）

## 6. Core Idea

将正常业务负载函数、Locust 请求驱动、AWS FIS 故障注入与 Prometheus / CloudWatch 多层监控组成可复现的数据生成 / 采集管线。

## 7. Technical Innovations

- 多趋势、多周期、噪声的正常负载函数 N(t)（§3.2, Eqs.1–2）。
- 用 Algorithm 1 以区间概率和负载倍率生成负载异常，将需求变化标签与基础设施故障标签分开。
- 用 AWS FIS 注入 CPU / memory / network delay / packet loss / I/O / pod / node 故障，并采集 470 项 node/pod/service 指标（§3.4–3.5）。

## 8. Methodology

本文没有训练检测模型。完整数据生成流程为：

1. 在 EKS 部署服务应用并设定基线负载与趋势 / 周期参数。
2. 由 Locust 按生成的需求曲线发起请求；监控组件记录正常状态遥测。
3. 按实验计划生成负载异常或触发 FIS 基础设施故障，并记录精确开始 / 结束时间与对象。
4. 同步收集节点、Pod、服务指标及日志；对异常标签进行时间区间对齐。
5. 形成可供后续检测器研究的数据集。论文没有提出推理阶段异常打分流程；检测算法评价被列为未来工作。

因此，本文所说“适合异常检测研究”的主要支持来自可控生成、指标覆盖和故障效应图，而非检测准确率提升实验。

## 9. Experimental Evidence

- **环境 / 模态**：AWS EKS、Sock-Shop 和 Online Boutique；主要为 470 项指标并采集日志。没有报告本数据集中的 Trace 采集与 Trace 样本。
- **故障类型**：计算、内存、网络延迟、网络丢包、I/O、Pod / 节点中断，以及独立的负载突变。
- **证据**：Fig. 4 展示监控设置；Figs. 5–6 展示注入前后指标 / 服务行为变化，支持故障注入能触发可观测影响。论文描述数据集提供负载与 FIS 独立标签，可用于后续分析。
- **不存在的实验**：无检测器 Baseline、无 Precision / Recall / F1 / AUPRC 结果、无合成数据训练与真实数据测试、无合成真实性打分或专家评审、无跨应用迁移对照。作者将检测性能评价列为后续方向。（§4–5, Conclusion）

## 10. Limitations

### A. Author-stated limitations

- 数据面向有限电商应用和配置；检测算法评估留待后续（§5, Conclusion）。

### B. Reasoned inference

- 负载异常按倍率调整，未描述需求变化的业务语义或根因。
- 日志虽被采集，主要数据规模与测量结果是指标；Trace 没有纳入该版多模态数据。

### C. Evidence gaps

- 没有合成数据真实性 / 专家评估。
- 无真实生产测试、无合成训练对真实测试、无负载变化与故障同时发生的区分实验。

## 11. Research Implications

**本知识库分析**：适合做真实系统反馈与故障标签构造基准；需要把业务上下文、Trace 和并发事件加入数据覆盖。

## 12. Related Papers

`AIOpsLab`提供 Agent 与工具交互任务；`TraceLLM`生成调用 DAG；TSAD `CAPMix`处理窗口级训练增强。

## 13. Evidence References

| 主张 | 原文定位 |
| --- | --- |
| AWS / 微服务环境与监控组件 | PDF §3.1, Fig. 1 |
| 正常业务负载公式 | PDF §3.2, Eqs. 1–2 |
| 负载异常生成 | PDF §3.3, Algorithm 1 |
| FIS 故障类型与流程 | PDF §3.4, Algorithm 2 |
| 指标数量、采集和样例配置 | PDF §3.5, Tables 1–3 |
| 注入引起的可观察效应 | PDF Figs. 5–6 |
| 检测效果尚未验证 | PDF Conclusion / Future Work |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "synthetic-cloud-microservices",
  "title_en": "Synthetic Time Series for Anomaly Detection in Cloud Microservices",
  "title_zh": "面向云微服务异常检测的合成时间序列",
  "authors": [
    "Mohamed Allam",
    "Noureddine Boujnah",
    "Noel E. O’Connor",
    "Mingming Liu"
  ],
  "year": 2024,
  "venue": "MLDS 2024（按论文正文所述接收）；本地版本 arXiv:2408.00006",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/synthetic-cloud-microservices-arxiv2408.00006.pdf",
  "reading_note_path": "papers/aiops/synthetic-cloud-microservices/notes.md",
  "knowledge_card_path": "papers/aiops/synthetic-cloud-microservices/knowledge-card.md",
  "code_url": "https://github.com/Mohamed164/AD-microservice-app",
  "research_area": "云微服务数据集构建、负载合成与真实故障注入",
  "method_tags": [
    "microservices",
    "fault-injection",
    "load-synthesis",
    "metrics",
    "ground-truth"
  ],
  "research_scenario": "AWS EKS 上的 Sock-Shop / Online Boutique 电商服务；合成动态用户需求，并执行 CPU / memory / network / I/O / pod 故障，采集多层指标及故障时间标签。",
  "research_problem": "在缺少真实故障标注、难以重复触发生产事故时，如何构造包含动态正常负载、负载异常、基础设施故障及可对齐指标标签的微服务数据？",
  "core_challenges": [
    "正常需求趋势 / 多周期变化不能简化为平稳常数（§3.2）。",
    "数值尖峰无法复现系统故障动作到遥测响应的链路（§3.4）。",
    "业务侧负载突变与基础设施故障影响机制不同，需独立控制和标注。"
  ],
  "existing_method_limits": [
    "纯人工 / 规则数值合成缺少真实云服务反馈；实际生产故障受风险与成本制约。论文提供受控实验环境，但未证明其覆盖生产分布。"
  ],
  "core_idea": "将正常业务负载函数、Locust 请求驱动、AWS FIS 故障注入与 Prometheus / CloudWatch 多层监控组成可复现的数据生成 / 采集管线。",
  "technical_innovations": [
    "多趋势、多周期、噪声的正常负载函数 N(t)（§3.2, Eqs.1–2）。",
    "用 Algorithm 1 以区间概率和负载倍率生成负载异常，将需求变化标签与基础设施故障标签分开。",
    "用 AWS FIS 注入 CPU / memory / network delay / packet loss / I/O / pod / node 故障，并采集 470 项 node/pod/service 指标（§3.4–3.5）。"
  ],
  "methodology": {
    "architecture": "部署微服务应用和 Istio → Locust 施加动态正常 / 异常负载 → AWS FIS 触发目标故障 → Prometheus / CloudWatch / Fluent Bit 收集遥测 → 将注入事件时间对齐到数据标签。",
    "data_processing": "正常负载 N(t)=(1+trend(t))base_load+Σi Ai[sin²(2πt/Ti)+wni(t)]；piecewise trend 有每段 p=.01 的突变概率。负载异常随机选时段和乘数。470 指标由 25×5 节点、18×14 Pod、9×10 服务项组成。",
    "modules": [
      "正常负载生成：基线 + 分段趋势 + 多周期 + 噪声；spawn rate 按负载导数调整。",
      "负载异常生成：Algorithm 1 对随机区间乘负载因子。",
      "基础设施故障注入：Algorithm 2 随机选择目标和 FIS 模板，按计划记录注入窗口。",
      "遥测采集：节点、Pod、服务指标以及日志；本文未采集 / 报告 Trace 序列。"
    ],
    "key_formulas": [
      "N(t)=(1+trend(t))×base_load+Σᵢ Aᵢ[(sin(2πt/Tᵢ))²+wnᵢ(t)]（Eq.1）。",
      "负载导数 / Locust spawn rate 关系见 Eq.2。"
    ],
    "training": "论文无待训练异常检测器。运行环境通过 Locust 和故障注入模板生成负载 / 故障，监控组件同步收集并生成时间标签。",
    "inference": "本文没有检测模型或检测推理阶段；作者将检测算法性能评价列为后续方向。",
    "end_to_end": "负载与服务配置 → 微服务在线运行 → 正常需求 / 负载异常 / FIS 故障 → 真实采集指标和日志 → 与注入计划对齐的带标签数据。"
  },
  "experimental_evidence": {
    "datasets": [
      "Sock-Shop 与 Online Boutique on AWS EKS；总计 470 项节点 / Pod / 服务指标。"
    ],
    "baselines": [],
    "metrics": [
      "数据构造与标签覆盖；没有 detector metrics。"
    ],
    "main_results": [
      "7 天示例运行涵盖多周期负载。故障示例：CPU 100% 4min、memory 100% 4min、400ms 网络延迟 5min、40% 丢包 2min、I/O 80% 5min（§3.4–3.5, Tables 2–3）。",
      "Fig.5–6 展示注入后尾延迟 / 错误和资源指标变化；没有 F1 / AUPRC 或下游 detector 结果。"
    ],
    "ablations": [
      "未报告对检测模型或生成算法的消融。"
    ],
    "robustness_generalization": [
      "通过不同故障配置和负载条件采集；无跨应用检测器泛化实验。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [
      "数据面向有限电商应用和配置；检测算法评估留待后续（§5, Conclusion）。"
    ],
    "reasoned_inference": [
      "负载异常按倍率调整，未描述需求变化的业务语义或根因。",
      "日志虽被采集，主要数据规模与测量结果是指标；Trace 没有纳入该版多模态数据。"
    ],
    "evidence_gaps": [
      "没有合成数据真实性 / 专家评估。",
      "无真实生产测试、无合成训练对真实测试、无负载变化与故障同时发生的区分实验。"
    ]
  },
  "research_implications": [
    "可作为受控真实运行故障 / 负载基准，支持外部生成器的遥测效应校验；将它称作生成管线而非检测方法（本知识库分析）。"
  ],
  "related_papers": [
    "aiopslab",
    "tracellm",
    "llm-ap-synthetic-augmentation",
    "capmix",
    "carots"
  ],
  "evidence_references": [
    "PDF §§3.1–3.2, Eqs.1–2, Fig.1：EKS / 工作负载 / 正常负载。",
    "PDF §§3.3–3.5, Algorithms 1–2, Tables 1–3：异常注入与指标采集。",
    "PDF Figs.5–6, Conclusion：注入效果与评估边界。"
  ],
  "provenance": {
    "pdf_sha256": "d75d18d66929feb72b25763a5b56e2e014380a14f1292cd130213398e1a91214",
    "reading_note_sha256": "f1b90bd934aed761eaae7edeffbd44ed99013454f52de32c718f987ee25172e1",
    "knowledge_card_sha256": "bfb9c191b8e721eb7404bc64335440feb7bad924d9593ff4a315ecfd1b6f22ec",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->
