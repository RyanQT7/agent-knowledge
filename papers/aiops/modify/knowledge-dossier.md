# Knowledge Dossier — A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices

## 1. Basic Information

- **English title**: A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices
- **中文译名**：MODIFy：扩散增强自适应融合的微服务多模态异常诊断框架
- **Authors**: Wujian Zhang, Ruyue Xin, Peng Chen, Xi Li, Ang Bian, Yibin Zhao, Zhiming Zhao
- **Venue / year / CCF**: Journal of Systems and Software 237, 112844 (2026) / 2026 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: [modify_jss-2026.pdf](../../../sources/papers/llm-microservice-anomaly-generation/modify_jss-2026.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/WuFengXueYing/MODIFy
- **Research area**: 微服务多模态异常检测及服务级根因定位
- **Method tags**: microservices, logs-metrics-traces, diffusion-denoising, adaptive-fusion, GAT, root-cause-localization

## 2. Research Scenario

论文以微服务请求沿调用链传播为场景：网络拥塞可能引发 Trace 重试和延迟突刺，但 Metric 仅轻微变化且仍在 SLO 内，日志只出现警告而非明确错误。单模态因此各自提供不完整证据：Trace 对故障敏感但稀疏、采样缺失、重试噪声高；Metric 连续但语义不明；Log 有事件语义但覆盖有限。研究问题是在这类不完整且噪声异质的日志、指标、Trace 下，如何提升异常检测并把异常定位至服务节点。（PDF §1, p.2, Fig. 1）

输入是按时间窗口对齐后的服务级日志事件强度、指标序列和 Trace 延迟特征，以及历史 Trace 中抽取的服务调用依赖图；输出是样本是否异常及候选根因微服务排名。不是事件级故障生成或 Metric–Trace 合成。

## 3. Research Problem

在 Trace 稀疏 / 噪声、指标异常幅度小且日志无显式错误的微服务环境中，如何融合互补观测并同时检测系统异常、定位服务根因？

## 4. Core Challenges

1. **Trace 噪声 / 缺失**：分布式请求驱动的 Trace 不连续，低流量窗口稀疏，重试造成长尾突刺；直接编码可能把噪声误当故障传播。（§1, §4.1C）
2. **模态采样频率不一致**：Metric 固定周期采集、Trace 毫秒级事件、Log 事件流，需要统一时间参照与聚合。（§4.2）
3. **模态贡献依上下文而变**：简单拼接 / 平均分配权重可能丢失互补关系，无法在特定时间和通道突出关键证据。（作者动机，§1–2）
4. **检测和定位两阶段传递误差**：先检测再另跑 RCA 的管线可能把前段噪声传播至定位，且重复编码原始遥测。（§4.3）

作者将既有工作归为单模态检测 / 定位、图关系分析、多模态融合与联合学习等路线；论文以 Eadro、AMuLSys、MicroIRC 等作基线。论文声称浅层融合和序贯诊断存在限制；其实验比较显示其对 Eadro 等基线有优势，但并未单独证明所有传统方法都存在噪声放大。

## 5. Limitations of Existing Methods

总体是三阶段：

输入日志 / Metric / Trace
→ 单模态编码和时间对齐
→ MSCA-CGFM 自适应多尺度融合 + 调用图 GAT
→ 共享系统表示
→ 异常二分类 + 服务根因排序

Trace 的扩散模块是训练期特征去噪 / 鲁棒表示机制：随机将 Trace 表示加高斯噪声，再学习去噪；不是生成新故障样本，也不是采样出真实 Trace 序列。

## 6. Core Idea

针对 Trace 单独使用训练期扩散式去噪；将三模态以 6 秒窗对齐并经多尺度门控 / SE 融合，结合服务调用 GAT 得系统表示，再共享给检测和根因排序分支。

## 7. Technical Innovations

- DNR-FE：在 Trace 特征随机采样扩散步加噪并用 1D CNN 去噪，旨在提升噪声鲁棒；去除模块平均 F1 / HR@1 / HR@5 降约 3.5% / 3.1% / 6.2%（§5.7）。
- MSCA-CGFM：3×3、5×5 depthwise conv 多尺度分支 + gate + SE 通道重标定；消融去掉模块下降最大（Fig.5）。
- 图注意力后的共享表示联合检测 / 定位；减少重复编码，联合监督效果由整体对比支持，但无法单独证明所有串行流程均有噪声放大。

## 8. Methodology

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

## 9. Experimental Evidence

- **数据**：SocialNetwork（21 服务，98,510 窗口）；TrainTicket（41 服务，445,584 窗口）。每者含 CPU hog、network delay、network loss；两数据集服务数、样本规模不同。Metric 每服务 7 个维度：CPU 三项、内存两项、接收 / 发送字节。日志异常模板 SN 为 6 类已知 + 1 未知，TT 为 59 类已知 + 1 未知。预处理后 SN 有 119,664 metrics、94,365 logs、48,296 traces；TT 有 2,007,801 metrics、111,275 logs、126,384 traces。（§5.1, Table 2）
- **Baselines**：DeepLog、LogRobust、TraceAnomaly、MultimodalTrace、DeepTraLog、TraceGra、AMuLSys、Eadro；定位另含 CloudRanger、MonitorRank、DyCause、DejaVu、MicroIRC。（§5.2）
- **指标**：检测 Precision / Recall / F1；定位 HR@1/3/5、NDCG@3/5。（§5.4）
- **主结果**：F1：SN .925、TT .841，平均 .883；Eadro 分别 .904 / .834。HR@1：SN .878、TT .816，平均 .847；Eadro .810 / .757。NDCG@5 为 .921 / .917。（Tables 4–5）
- **消融**：去掉任何模态，SN HR@1 下降约 8.9%–19.2%、F1 下降 10.1%–14.0%；TT HR@1 降 10.1%–19.3%、F1 降 9.3%–14.7%，去 Trace 影响最大。移除 Trace diffusion 平均 F1 降 3.5%、HR@1 降 3.1%、HR@5 降 6.2%；去多尺度通道门控损失最大。噪声注入测试中 MODIFy 相比 Eadro 下降较缓；Fig. 8 支持测试噪声鲁棒性，但不等于对业务状态漂移稳健。（§5.7, Fig. 5; §5.12, Fig. 8）
- **显著性 / 成本**：对 Eadro 的 10 次配对检验，F1 与 HR@1 的多个差异报告 p<.05。推理 1.578 ms/sample（SN）、1.872 ms/sample（TT）；完整训练约 40 分钟 / 3 小时，GPU memory .899 / 2.011GB。（§5.10–5.11, Tables 6–7）

## 10. Limitations

### A. Author-stated limitations

- 固定 / 已知依赖拓扑；两公开数据集；依赖监督故障类型；服务级定位，不支持实例 / 容器；未观测基础设施异常可能漏检；benchmarks 多为单一主因；未来考虑动态图、部署效率和 LLM 解释（§6, pp.18–20）。

### B. Reasoned inference

- 6 秒窗口和固定拓扑对其他采样 / 动态服务环境的外推仍待验证。
- 模型融合实测模态而非联合生成；扩散是降噪训练机制，不是异常样本生成。

### C. Evidence gaps

- 没有业务负载 / 发布上下文输入或正常高峰困难负样本专项评估。
- 多根因标注及动态拓扑实验不足。

## 11. Research Implications

**本知识库分析**：用于多模态诊断对照；其对 Trace 降噪和服务级图融合可以作为数据生成验证的下游组件，但论文自身不生成故障数据。

## 12. Related Papers

MODIFy 直接对比 [AMuLSys](../amulsys/availability.md)，但本知识库因全文未获取不复述其方法；[AIOpsLab](../aiopslab/notes.md)提供可运行注入环境；[CAROTS](../../carots/notes.md)使用因果图生成伪异常。

## 13. Evidence References

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

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "modify",
  "title_en": "A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices",
  "title_zh": "MODIFy：扩散增强自适应融合的微服务多模态异常诊断框架",
  "authors": [
    "Wujian Zhang",
    "Ruyue Xin",
    "Peng Chen",
    "Xi Li",
    "Ang Bian",
    "Yibin Zhao",
    "Zhiming Zhao"
  ],
  "year": 2026,
  "venue": "Journal of Systems and Software 237, 112844 (2026)",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/modify_jss-2026.pdf",
  "reading_note_path": "papers/aiops/modify/notes.md",
  "knowledge_card_path": "papers/aiops/modify/knowledge-card.md",
  "code_url": "https://github.com/WuFengXueYing/MODIFy",
  "research_area": "微服务多模态异常检测及服务级根因定位",
  "method_tags": [
    "microservices",
    "logs-metrics-traces",
    "diffusion-denoising",
    "adaptive-fusion",
    "GAT",
    "root-cause-localization"
  ],
  "research_scenario": "SocialNetwork / TrainTicket 的多模态可观测数据；输入是对齐的 Log / Metric / Trace 和历史调用图，输出窗口级异常标签与服务级根因排名。",
  "research_problem": "在 Trace 稀疏 / 噪声、指标异常幅度小且日志无显式错误的微服务环境中，如何融合互补观测并同时检测系统异常、定位服务根因？",
  "core_challenges": [
    "Trace latency 受采样稀疏、重试和长尾异常值影响（PDF §1, p.2; §4.1C）。",
    "Log / Metric / Trace 采样粒度不同，需统一时间基准（§4.2）。",
    "浅层融合不随上下文动态调节通道贡献（作者主张，§1–2）。",
    "检测与定位串行会重复处理并传播前级错误（作者主张，§4.3）。"
  ],
  "existing_method_limits": [
    "单模态日志 / 指标 / Trace 方法观察有限；多模态浅拼接或加权融合未显式建模多尺度与通道重要性。本文与 Eadro、AMuLSys 等比较，但全局性“传统方法会噪声放大”主要是作者动机而非逐类消融结论。"
  ],
  "core_idea": "针对 Trace 单独使用训练期扩散式去噪；将三模态以 6 秒窗对齐并经多尺度门控 / SE 融合，结合服务调用 GAT 得系统表示，再共享给检测和根因排序分支。",
  "technical_innovations": [
    "DNR-FE：在 Trace 特征随机采样扩散步加噪并用 1D CNN 去噪，旨在提升噪声鲁棒；去除模块平均 F1 / HR@1 / HR@5 降约 3.5% / 3.1% / 6.2%（§5.7）。",
    "MSCA-CGFM：3×3、5×5 depthwise conv 多尺度分支 + gate + SE 通道重标定；消融去掉模块下降最大（Fig.5）。",
    "图注意力后的共享表示联合检测 / 定位；减少重复编码，联合监督效果由整体对比支持，但无法单独证明所有串行流程均有噪声放大。"
  ],
  "methodology": {
    "architecture": "Drain3 / Hawkes 日志编码 + Metric Transformer + Trace diffusion / Transformer → 6秒窗口对齐 → MSCA-CGFM → 静态服务调用图 GAT → 检测器与根因定位器联合学习。",
    "data_processing": "Metric Z-score；Log 按模板 / 时间事件序列建模；Trace 从父子 span 重建服务依赖并聚合服务延迟。6 秒固定窗口，对 Metric 重采样、Trace 平均、Log 聚合 Hawkes intensity。",
    "modules": [
      "Log：Drain3 模板 + Hawkes 点过程强度向量。",
      "Metric：四维窗口张量进入 Transformer encoder。",
      "Trace DNR-FE：Fτ=√αtFτ0+√(1−αt)ε；1D CNN / ReLU 去噪后由 Transformer 表征。",
      "MSCA-CGFM：CGLU 特征 / 门控支路，3×3/5×5 多尺度深度卷积加权并用 SE 通道注意力。",
      "GATv2Conv：按调用边传递注意力特征并全局聚合。",
      "联合分类 / 定位：系统二分类和服务 root softmax 排名，联合交叉熵。"
    ],
    "key_formulas": [
      "Trace 前向扩散 Eq.2：Fτ=√αtFτ0+√(1−αt)ε。",
      "MSCA 公式 Eqs.3–6：split 特征、加权多尺度卷积、SE 权重及 HS=SE(H1dw⊙σ(H2))。",
      "系统图聚合 Eq.8；总损失 Eq.11：L=αL1+(1−α)L2，L1检测交叉熵、L2根因交叉熵。"
    ],
    "training": "监督训练，数据含异常标签和根因服务标签。Adam lr=.001、batch 256、70 epochs；扩散 100 步 / 噪声 1e-5–1e-2；联合损失默认 α=.5。",
    "inference": "对一个同步时间窗计算多模态节点表示，融合 / GAT 得全局向量；检测分支给异常概率，定位分支按服务概率排序。根因是服务级，不等于容器 / 实例级。",
    "end_to_end": "在线遥测 → 特征抽取 / 6秒对齐 → Trace 去噪和跨模态融合 → 调用图注意力 → 异常判别 + 服务根因排序。"
  },
  "experimental_evidence": {
    "datasets": [
      "SocialNetwork：21 services, 98,510 windows；TrainTicket：41 services, 445,584 windows。分别包含 CPU hog、network delay、network loss。"
    ],
    "baselines": [
      "DeepLog, LogRobust, TraceAnomaly, MultimodalTrace, DeepTraLog, TraceGra, AMuLSys, Eadro；定位另含 CloudRanger, MonitorRank, DyCause, DejaVu, MicroIRC。"
    ],
    "metrics": [
      "Precision / Recall / F1",
      "HR@1/3/5",
      "NDCG@3/5"
    ],
    "main_results": [
      "F1 .925 (SN), .841 (TT)，平均 .883；Eadro .904 / .834（Table 4）。",
      "HR@1 .878 / .816，平均 .847；NDCG@5 .921 / .917（Table 5）。",
      "扩散模块移除平均 F1 / HR@1 / HR@5 分别降 3.5% / 3.1% / 6.2%；去任意模态都降分，去 Trace 影响最大（§5.7, Fig.5）。",
      "噪声注入测试对比 Eadro 降幅更缓（§5.12, Fig.8）；两数据集上的运行时分别 1.578 / 1.872ms 每样本，训练约 40min / 3h（Table 6）。"
    ],
    "ablations": [
      "模态去除、Transformer 改 dilated causal conv、去 Trace diffusion、MSCA-CGFM 改标准 GLU；另比较扩散步数、卷积核数量、GAT 层数和 α（§§5.7–5.8）。"
    ],
    "robustness_generalization": [
      "测试集逐渐增加噪声，和 Eadro 对比；这是人工噪声鲁棒性，不等同业务负载漂移鲁棒性。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [
      "固定 / 已知依赖拓扑；两公开数据集；依赖监督故障类型；服务级定位，不支持实例 / 容器；未观测基础设施异常可能漏检；benchmarks 多为单一主因；未来考虑动态图、部署效率和 LLM 解释（§6, pp.18–20）。"
    ],
    "reasoned_inference": [
      "6 秒窗口和固定拓扑对其他采样 / 动态服务环境的外推仍待验证。",
      "模型融合实测模态而非联合生成；扩散是降噪训练机制，不是异常样本生成。"
    ],
    "evidence_gaps": [
      "没有业务负载 / 发布上下文输入或正常高峰困难负样本专项评估。",
      "多根因标注及动态拓扑实验不足。"
    ]
  },
  "research_implications": [
    "可用作 Metric–Trace–Log 融合诊断 baseline；在使用它评估增强数据前应保持任务边界一致（本知识库分析）。"
  ],
  "related_papers": [
    "amulsys",
    "aiopslab",
    "synthetic-cloud-microservices",
    "tracellm",
    "carots"
  ],
  "evidence_references": [
    "PDF §1, p.2, Fig.1：拥塞在三模态中的差异表现。",
    "PDF §§4.1–4.3, pp.7–10, Eqs.1–11 / Figs.2–4：完整架构、损失、融合与定位。",
    "PDF §§5.1–5.8, pp.11–15, Tables 2–5 / Fig.5：数据、结果和消融。",
    "PDF §§5.10–6, pp.16–20, Tables 6–7 / Fig.8：成本、抗噪和作者局限。"
  ],
  "provenance": {
    "pdf_sha256": "3d00001f633dd5e6421420906e0581010090aa4b8878dbbcacac9cf520e4a15b",
    "reading_note_sha256": "34fd1cbaf835b95954c3030e2cb321ae1ab9113dd734db90efd34549dfbbb89f",
    "knowledge_card_sha256": "52a4237397cd4d5fb02138acb8c381390a048d8f44e220a5d400fe87c5c8fc79",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->
