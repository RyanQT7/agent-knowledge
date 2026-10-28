# MODIFy：A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices

## 1. Metadata

- **Authors**: Wujian Zhang, Ruyue Xin, Peng Chen, Xi Li, Ang Bian, Yibin Zhao, Zhiming Zhao
- **Year / venue**: 2026, Journal of Systems and Software 237, article 112844
- **DOI / source**: https://doi.org/10.1016/j.jss.2026.112844 ; [作者公开存档](https://zenodo.org/records/19016326)
- **Local PDF**: [JSS 论文 PDF](../../../sources/papers/llm-microservice-anomaly-generation/modify_jss-2026.pdf)
- **Code**: https://github.com/WuFengXueYing/MODIFy（论文项目地址）
- **Paper ID**: modify
- **Tags**: microservices; multimodal-diagnosis; metric-trace-log; diffusion-denoising; adaptive-fusion; GAT; RCA

## 2. One-Sentence Summary

MODIFy 从日志、指标与 Trace 提取并对齐特征，对 Trace 延迟序列做扩散式加噪 / 去噪训练，再用多尺度通道自适应门控融合和调用图 GAT，共享表示联合完成系统异常检测与服务级根因定位；它是多模态诊断模型，不生成异常样本、不使用 LLM，也未验证业务负载上下文下的正常波动区分。

## 3. Research Scenario and Problem

论文以微服务请求沿调用链传播为场景：网络拥塞可能引发 Trace 重试和延迟突刺，但 Metric 仅轻微变化且仍在 SLO 内，日志只出现警告而非明确错误。单模态因此各自提供不完整证据：Trace 对故障敏感但稀疏、采样缺失、重试噪声高；Metric 连续但语义不明；Log 有事件语义但覆盖有限。研究问题是在这类不完整且噪声异质的日志、指标、Trace 下，如何提升异常检测并把异常定位至服务节点。（PDF §1, p.2, Fig. 1）

输入是按时间窗口对齐后的服务级日志事件强度、指标序列和 Trace 延迟特征，以及历史 Trace 中抽取的服务调用依赖图；输出是样本是否异常及候选根因微服务排名。不是事件级故障生成或 Metric–Trace 合成。

## 4. Core Challenges and Existing Methods

1. **Trace 噪声 / 缺失**：分布式请求驱动的 Trace 不连续，低流量窗口稀疏，重试造成长尾突刺；直接编码可能把噪声误当故障传播。（§1, §4.1C）
2. **模态采样频率不一致**：Metric 固定周期采集、Trace 毫秒级事件、Log 事件流，需要统一时间参照与聚合。（§4.2）
3. **模态贡献依上下文而变**：简单拼接 / 平均分配权重可能丢失互补关系，无法在特定时间和通道突出关键证据。（作者动机，§1–2）
4. **检测和定位两阶段传递误差**：先检测再另跑 RCA 的管线可能把前段噪声传播至定位，且重复编码原始遥测。（§4.3）

作者将既有工作归为单模态检测 / 定位、图关系分析、多模态融合与联合学习等路线；论文以 Eadro、AMuLSys、MicroIRC 等作基线。论文声称浅层融合和序贯诊断存在限制；其实验比较显示其对 Eadro 等基线有优势，但并未单独证明所有传统方法都存在噪声放大。

## 5. Core Idea and Architecture

总体是三阶段：

输入日志 / Metric / Trace
→ 单模态编码和时间对齐
→ MSCA-CGFM 自适应多尺度融合 + 调用图 GAT
→ 共享系统表示
→ 异常二分类 + 服务根因排序

Trace 的扩散模块是训练期特征去噪 / 鲁棒表示机制：随机将 Trace 表示加高斯噪声，再学习去噪；不是生成新故障样本，也不是采样出真实 Trace 序列。

## 6. Methodology

### A. 单模态特征

**Log**：Drain3 将非结构化日志解析成模板；按窗口统计模板事件序列，用 Hawkes 自激点过程得到每类模板的强度向量。事件 l 的强度形式为 λ*l(t)=μl(t)+Σ(τ<t)φl(t−τ)，激发核 φl(·)=αlβ exp(−βt)，t>0。μ 初始化为 0.2 并通过最大似然学习；向量 Λ 经全连接层映射为日志表示。意图是捕捉错误日志不明显时事件频率 / 触发模式变化。（§4.1A, Eq. 1）

**Metric**：对每个服务节点的指标作 Z-score 标准化，切成 K 个连续固定窗口，形成 X∈R^(K×N×T×M)；Transformer encoder 用多头注意力抽取全局时间依赖并输出 metric embedding。（§4.1B）

**Trace**：按 span 的服务 ID、父子关系、时间戳和 duration 提取调用链 / 拓扑；按服务在固定窗内平均 latency 构造序列。给定原特征 Fτ0，按随机扩散步 t 加噪：

Fτ = √αt Fτ0 + √(1−αt) ε，ε~N(0,I)。

累积保留系数 αt 控制原始信息和噪声比例；堆叠 1D 卷积 + ReLU 去噪网络学习恢复特征，然后 Transformer 编码器抽取时间表示。（§4.1C, Eq. 2, Fig. 3）作者试过把扩散用于 Log / Metric，效果不理想；给出的解释是离散文本与稳定 Metric 的噪声分布不适合该扰动，而 Trace latency 的外界波动更适合这一处理。（§4.1C）

### B. 对齐与 MSCA-CGFM

先将不同模态时间戳映射到统一时间轴，用固定 6 秒窗口同步：Trace span 聚合为服务平均延迟，Metric 重采样，Log 按窗形成 Hawkes 强度向量。三种 embedding 沿通道拼接；另从 Trace 父子 span 构建有向服务调用图 G=(V,E)。（§4.2）

增强 CGLU 把拼接表示投影并切为 H1 特征支路和 H2 门控支路：

[H1,H2] = split(Wf[FL || FM || FT])。

H1 并行通过 3×3 与 5×5 depthwise separable convolution，按可学习 w1+w2=1 加权：

H1dw = w1·DWConv3×3(H1) + w2·DWConv5×5(H1)。

再用 sigmoid(H2) 门控，随后 SE 模块以全局平均池化、两层全连接与 sigmoid 产生通道权重 sc，并逐通道重标定：

sc = σ(W2·ReLU(W1·(1/N)Σi hi))；
HS = SE(H1dw ⊙ σ(H2))。

输入是每服务的三模态嵌入，输出为适配上下文的融合表示。多尺度捕捉局部与较宽邻域，SE 调节通道权重；其效果在消融中评估。（§4.2, Eqs. 3–6, Fig. 4）

### C. 调用图 GAT 与联合检测 / 定位

融合节点特征放入调用图，经 GATv2Conv 学习服务间依赖注意力；多头结果在通道方向 max-pooling，随后全局 attention 聚合系统状态 HG=Σi αi hi。（§4.2, Eqs. 7–8）

共享 HG 输入两个监督分支：异常检测二分类器输出正常 / 异常概率；根因定位分支对服务节点输出 softmax 分布并排序。联合损失为 L=αL1+(1−α)L2，其中 L1 是二分类交叉熵，L2 是根因服务交叉熵；实验默认 α=.5。训练数据有系统异常标签与 root-service 标签。推理先给系统状态异常概率，再输出服务候选根因排名；正常样本不应解释为已确认故障。（§4.3, Eqs. 9–11）

### D. 训练与预处理配置

在 SocialNetwork 与 TrainTicket 的处理后多模态数据上按时间段 7:3 切分训练 / 测试，再独立滑窗，窗口为 6 秒。使用 Adam，初始学习率 .001、batch 256、70 epochs；Transformer 两层、4 头；各模态模型设为轻量单层；GAT 隐藏维度 128、4 头；扩散 100 步、噪声范围 1e-5–1e-2。（§5.1, §5.3）

## 7. Experiments

- **数据**：SocialNetwork（21 服务，98,510 窗口）；TrainTicket（41 服务，445,584 窗口）。每者含 CPU hog、network delay、network loss；两数据集服务数、样本规模不同。Metric 每服务 7 个维度：CPU 三项、内存两项、接收 / 发送字节。日志异常模板 SN 为 6 类已知 + 1 未知，TT 为 59 类已知 + 1 未知。预处理后 SN 有 119,664 metrics、94,365 logs、48,296 traces；TT 有 2,007,801 metrics、111,275 logs、126,384 traces。（§5.1, Table 2）
- **Baselines**：DeepLog、LogRobust、TraceAnomaly、MultimodalTrace、DeepTraLog、TraceGra、AMuLSys、Eadro；定位另含 CloudRanger、MonitorRank、DyCause、DejaVu、MicroIRC。（§5.2）
- **指标**：检测 Precision / Recall / F1；定位 HR@1/3/5、NDCG@3/5。（§5.4）
- **主结果**：F1：SN .925、TT .841，平均 .883；Eadro 分别 .904 / .834。HR@1：SN .878、TT .816，平均 .847；Eadro .810 / .757。NDCG@5 为 .921 / .917。（Tables 4–5）
- **消融**：去掉任何模态，SN HR@1 下降约 8.9%–19.2%、F1 下降 10.1%–14.0%；TT HR@1 降 10.1%–19.3%、F1 降 9.3%–14.7%，去 Trace 影响最大。移除 Trace diffusion 平均 F1 降 3.5%、HR@1 降 3.1%、HR@5 降 6.2%；去多尺度通道门控损失最大。噪声注入测试中 MODIFy 相比 Eadro 下降较缓；Fig. 8 支持测试噪声鲁棒性，但不等于对业务状态漂移稳健。（§5.7, Fig. 5; §5.12, Fig. 8）
- **显著性 / 成本**：对 Eadro 的 10 次配对检验，F1 与 HR@1 的多个差异报告 p<.05。推理 1.578 ms/sample（SN）、1.872 ms/sample（TT）；完整训练约 40 分钟 / 3 小时，GPU memory .899 / 2.011GB。（§5.10–5.11, Tables 6–7）

## 8. Limitations and Topic Relevance

**作者明确限制**：图拓扑在预处理阶段由历史 Trace 建立，实验假设静态已知服务节点 / 边；只在两个公开基准评估，难覆盖大型生产系统和稀有复杂故障；监督检测依赖训练异常类型；仅服务级定位，不支持实例 / 容器级根因；未观测到运行时信号的基础设施问题可能漏检；多数 benchmark 标注单一主根因，难评多根因。后续考虑动态图、自适应部署、LLM 增强解释。（§6, pp.18–20）

**本知识库分析**：对多模态同步的确是特征级联合，而非由统一故障机制条件生成；扩散处理的是噪声鲁棒性，不是异常合成。6 秒固定窗口可能对低频/突发业务或不同采样制度不普适，作者未报告窗口粒度迁移。没有明确将业务负载、发布、扩缩容作为上下文输入，因此不能据此声称区分正常负载高峰和故障。

## 9. Relationship to This Topic

MODIFy 是 [TraceLLM](../tracellm/notes.md) 和 [Synthetic Time Series](../synthetic-cloud-microservices/notes.md) 的下游诊断补充：它消费真实对齐遥测，不生成异常。论文直接将 [AMuLSys](../amulsys/availability.md) 纳入检测对照，但本知识库尚未获取 AMuLSys 全文，不能据此写其增强算法细节。与 [AIOpsLab](../aiopslab/notes.md) 相比，MODIFy 是固定任务的监督模型，AIOpsLab 是 Agent 评测测试床。与 [CAROTS](../../carots/notes.md) 的因果结构伪异常不同，MODIFy 的 GAT 注意力建模图依赖，但没有把注意力解释成已识别的因果效应。

## 10. Evidence Map

| 论断 | 原文定位 |
| --- | --- |
| 网络拥塞多模态表现与研究挑战 | PDF §1, p.2, Fig. 1 |
| 三阶段整体架构 | PDF §4, pp.6–7, Fig. 2 |
| Hawkes Log 与 Metric encoder | PDF §4.1A–B, p.7, Eq. 1 |
| Trace diffusion、6 秒对齐 | PDF §4.1C–§4.2, pp.7–8, Eqs. 2–3, Fig. 3 |
| MSCA-CGFM、GAT、联合损失 | PDF §4.2–4.3, pp.8–10, Eqs. 3–11, Fig. 4 |
| 数据与训练配置 | PDF §§5.1–5.4, pp.11–12, Table 2 |
| 检测 / 定位结果和消融 | PDF §§5.6–5.7, pp.13–15, Tables 4–5, Fig. 5 |
| 噪声、成本、局限和未来方向 | PDF §§5.10–6, pp.16–20, Tables 6–7, Fig. 8 |
