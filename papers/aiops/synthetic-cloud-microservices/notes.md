# Synthetic Time Series for Anomaly Detection in Cloud Microservices

## 1. Metadata

- **Authors**: Mohamed Allam, Noureddine Boujnah, Noel E. O’Connor, Mingming Liu
- **Year / venue**: 2024；论文说明被 10th International Conference on Machine Learning, Optimization and Data Science（MLDS 2024）接收。本文本地版本为 arXiv:2408.00006，不标注为 CCF 会议论文。
- **arXiv**: https://arxiv.org/abs/2408.00006
- **Local PDF**: [作者公开版](../../../sources/papers/llm-microservice-anomaly-generation/synthetic-cloud-microservices-arxiv2408.00006.pdf)
- **Code / dataset**: https://github.com/Mohamed164/AD-microservice-app（论文公开的项目地址）
- **Paper ID**: synthetic-cloud-microservices
- **Tags**: cloud-microservices; fault-injection; metric-dataset; workload-synthesis; ground-truth

## 2. One-Sentence Summary

本文搭建 AWS EKS 上的电商微服务工作负载与故障注入流程，分别合成具有趋势 / 周期 / 噪声的正常业务负载、突变负载异常和基础设施故障，并用 Prometheus / CloudWatch 等采集 470 项指标及标签；它提供的是数据构造与采集方案，不提出或比较异常检测器，也不生成 Trace。

## 3. Research Scenario and Problem

研究面向云端微服务监控数据获取：真实线上故障难以反复触发，异常标签稀少，单纯数学合成的时间序列缺少系统运行背景。作者希望在可控云环境中形成包含正常服务需求变化、负载异常和基础设施故障响应的带标签数据。测试床部署于 AWS EKS，使用 Sock-Shop 与 Online Boutique 两个电商应用；Locust 产生用户流量，Istio / Prometheus、CloudWatch 和 Fluent Bit 等采集系统指标、服务指标和日志。（PDF §§3.1–3.5, pp.3–8）

输入包括用户到达 / 请求负载参数以及 FIS 故障注入模板；输出包括带时间戳的节点、Pod、服务指标序列和独立的负载 / 基础设施故障标签。论文的主要可观测序列为指标，不包含本版本的分布式 Trace 数据；日志被采集组件列出，但主要量化数据集清单是指标。异常标签来自注入计划和时间区间，因此偏向实验可控的窗口 / 时间点异常标注，而不是人工确认的生产事故根因。

## 4. Challenges and Existing Limitations

1. **正常负载并非平稳常数**：业务需求会有趋势和多周期变化。若只用恒定背景，检测器容易把常见日常峰谷错判为故障。（§3.2, Eq. 1）
2. **数学异常不等于系统故障**：直接在指标上加尖峰不能复现 CPU 压力、网络延迟、Pod 删除等系统机制引发的联动变化。作者用云环境故障注入将“故障动作”与被观测影响联系起来。（§3.3–3.4）
3. **负载异常与资源故障需分开标注**：请求突变可能是业务侧需求异常；CPU hog 或网络损失则是基础设施故障，两者影响路径不同。论文分别生成负载异常与 FIS 故障，但没有证明某一检测器能可靠区分所有并发情形。
4. **规模与观测成本**：云资源和多服务采集成本让实际故障样本难以大量构造。受控实验牺牲了生产环境的复杂度和多样性。（§3, §5）

## 5. Core Idea and Data Generation

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

## 6. Training / Inference

本文没有训练检测模型。完整数据生成流程为：

1. 在 EKS 部署服务应用并设定基线负载与趋势 / 周期参数。
2. 由 Locust 按生成的需求曲线发起请求；监控组件记录正常状态遥测。
3. 按实验计划生成负载异常或触发 FIS 基础设施故障，并记录精确开始 / 结束时间与对象。
4. 同步收集节点、Pod、服务指标及日志；对异常标签进行时间区间对齐。
5. 形成可供后续检测器研究的数据集。论文没有提出推理阶段异常打分流程；检测算法评价被列为未来工作。

因此，本文所说“适合异常检测研究”的主要支持来自可控生成、指标覆盖和故障效应图，而非检测准确率提升实验。

## 7. Experimental Evidence

- **环境 / 模态**：AWS EKS、Sock-Shop 和 Online Boutique；主要为 470 项指标并采集日志。没有报告本数据集中的 Trace 采集与 Trace 样本。
- **故障类型**：计算、内存、网络延迟、网络丢包、I/O、Pod / 节点中断，以及独立的负载突变。
- **证据**：Fig. 4 展示监控设置；Figs. 5–6 展示注入前后指标 / 服务行为变化，支持故障注入能触发可观测影响。论文描述数据集提供负载与 FIS 独立标签，可用于后续分析。
- **不存在的实验**：无检测器 Baseline、无 Precision / Recall / F1 / AUPRC 结果、无合成数据训练与真实数据测试、无合成真实性打分或专家评审、无跨应用迁移对照。作者将检测性能评价列为后续方向。（§4–5, Conclusion）

## 8. Contributions, Limits, and Relevance

**贡献**：构建带动态业务需求、可配置负载异常、真实云端注入故障及多层指标标签的实验数据获取流程。重要之处是将“正常负载生成”与“故障注入”区分，并可把已知注入区间与遥测反应对齐。

**作者明确边界**：数据来自电商微服务应用，覆盖范围和异常类型有限；检测算法的系统比较留待后续。（§5, Conclusion）

**本知识库分析**：系统级故障注入比直接对数字加噪更接近真实故障影响，但它不能自动验证生成样本是否覆盖真实生产中的复杂故障语义。负载异常只由乘数变化控制，尚未充分解释变化来源；在“促销流量 + 某个后端故障”同时发生时，标签是否能拆分业务需求与系统根因，论文没有给出混合故障实验。指标为主，缺少与 Trace 的一致性生成。

## 9. Relationship to This Topic

与 [AIOpsLab](../aiopslab/notes.md) 同属运行系统里的可控故障注入，但本文聚焦数据采集 / 指标数据集，AIOpsLab 评估 Agent 端到端运维任务和工具交互。与 [TraceLLM](../tracellm/notes.md) 互补：一个生成结构化调用 Trace，一个在真实微服务环境触发故障并观测指标；二者尚无联合因果校验。与 [LLM-AP](../llm-ap-synthetic-augmentation/notes.md) 比较，后者可直接改造数值窗口，但不包含服务拓扑或故障注入。与 TSAD [CAPMix](../../capmix/notes.md) / [CAROTS](../../carots/notes.md) 比较，后两者增强学习样本，而本文提供负载 / 故障生成基础设施。

## 10. Evidence Map

| 主张 | 原文定位 |
| --- | --- |
| AWS / 微服务环境与监控组件 | PDF §3.1, Fig. 1 |
| 正常业务负载公式 | PDF §3.2, Eqs. 1–2 |
| 负载异常生成 | PDF §3.3, Algorithm 1 |
| FIS 故障类型与流程 | PDF §3.4, Algorithm 2 |
| 指标数量、采集和样例配置 | PDF §3.5, Tables 1–3 |
| 注入引起的可观察效应 | PDF Figs. 5–6 |
| 检测效果尚未验证 | PDF Conclusion / Future Work |
