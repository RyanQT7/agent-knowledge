# Llm Microservice Anomaly Generation Knowledge

## Contents

- [Paper 01 — TraceLLM：大语言模型驱动的真实微服务调用轨迹生成](#paper-01-tracellm)
- [Paper 02 — LLM-AP：基于合成时间序列增强的大语言模型异常检测](#paper-02-llm-ap-synthetic-augmentation)
- [Paper 03 — 面向云微服务异常检测的合成时间序列](#paper-03-synthetic-cloud-microservices)
- [Paper 04 — GenIAS：时间序列异常实例化生成器](#paper-04-genias)
- [Paper 05 — MODIFy：扩散增强自适应融合的微服务多模态异常诊断框架](#paper-05-modify)
- [Paper 06 — AIOpsLab：用于自主云运维 Agent 评估的整体框架](#paper-06-aiopslab)

<a id="paper-01-tracellm"></a>
## Paper 01 — TraceLLM：大语言模型驱动的真实微服务调用轨迹生成

## Knowledge Dossier — Large Language Models as Realistic Microservice Trace Generators

### 1. Basic Information

- **English title**: Large Language Models as Realistic Microservice Trace Generators
- **中文译名**：TraceLLM：大语言模型驱动的真实微服务调用轨迹生成
- **Authors**: Donghyun Kim, Sriram Ravula, Taemin Ha, Alexandros G. Dimakis, Daehyeok Kim, Aditya Akella
- **Venue / year / CCF**: EMNLP 2025 / 2025 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `tracellm_emnlp2025.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/ldos-project/TraceLLM
- **Research area**: 微服务 Trace 结构化生成与生成式系统数据
- **Method tags**: microservice-trace, LLM-generation, DAG, recursive-generation, structured-data

### 2. Research Scenario

研究场景是微服务系统的分布式调用 Trace。单条样本被表示为有向无环调用图（DAG）：边关联源服务、目标服务、通信类型、开始/结束时间等属性，并保留层级 / 调用关系。作者使用 Alibaba 2022 微服务调用图语料，约 136 万条图记录、约 11 亿 token。生成器的输入是自然语言指令或结构条件（例如图深度、边数、稀有通信、延迟条件），输出是一个序列化的新调用图。目标用途是补充 Trace 数据、下游任务训练及在指定结构条件下生成数据，而不是在线检测或根因诊断。（PDF pp.1–3, §2–3）

论文把“真实”主要操作化为结构约束、字段分布、调用模式及下游任务可用性。它没有把异常根因作为生成标签，也没有生成与 Trace 同步的 Metric / Log。

### 3. Research Problem

在真实调用图量大、层级深且必须满足 DAG / 边数 / 深度条件时，如何生成结构有效、字段统计合理且对特定下游任务有用的微服务调用图？

### 4. Core Challenges

**研究问题**：在真实调用图数据量大、结构化且需要满足 DAG 和调用条件的情况下，如何利用预训练语言模型生成字段与关系都有效、可按条件控制、并对下游任务仍有用的微服务 Trace？

1. **图结构约束难**：自由文本语言模型容易违反边数、深度、调用父子关系、起止时间或 DAG 结构。无约束生成导致无法直接被 Trace 工具或下游任务使用。（作者动机，§1–2）
2. **长结构依赖难**：调用图可能包含多层、多个同层子调用；平铺文本容易在长输出中丢失全局条件或重复节点。普通逐 token 生成没有明确的“逐调用层生成”机制。（§3.2）
3. **条件可控性与自然度冲突**：只按观测频率拟合容易生成常见图，却难以遵循稀有通信类型、延迟或指定规模条件。硬规则控制又可能造成不自然的组合。（§3.3–3.4）
4. **统计相似不等于下游有效**：仅报告边 / 节点频率无法说明合成 Trace 是否保留任务相关结构；因此作者还测试生成数据训练、真实数据测试的迁移设置。（§4）

### 5. Limitations of Existing Methods

作者比较了概率图 / 规则方法、表格数据生成模型（如 TVAE、GReaT）和基础 LLM。传统概率方法对结构组合和长尾条件的表达受限；一般表格生成器关注行级字段分布，未必保留调用图递归依赖；直接提示通用 LLM 则可能不遵守图约束。核心思路是把 Trace 视作一种有层次的结构化语言：先把图字段文本化，再把图分解为按父节点组织的层，模型每轮接收当前条件、生成当前层边及下一层条件，逐层扩大图；指令微调显式教模型推算剩余边数、深度等约束。

### 6. Core Idea

将调用图转为层级文本，按父节点 / 调用层递归生成边；把边数、深度等约束状态显式纳入条件和指令微调，使模型既学习领域字段又可控地扩展 DAG。

### 7. Technical Innovations

- 递归 DAG 文本生成：每轮生成一层边和下一层条件，针对长结构约束；相较单次扁平输出，困难边数 / 深度下有效率更高（§3.2, Eq.1; §4.1）。
- 约束推理指令微调：将剩余边数 / 深度等中间算术状态纳入序列，训练损失不预测初始条件文本；相较仅递归消融，报告约 23%–36%条件准确率提升（§3.3–4.1）。
- 领域继续预训练 + LoRA：在约 1.36M 图 / 1.1B tokens 上学习微服务字段分布；这是领域适配基础，不等于故障机制学习（§3.1）。

### 8. Methodology

#### A. 表示与领域预训练

每条调用边被转换为文本字段。论文随机打乱字段次序，降低模型将固定字段位置当成语义的风险。图级条件包括深度、边数、延迟等统计属性；训练时对条件顺序打乱并随机丢弃部分条件，使模型能适应不同条件组合。（§3.1）

作者用 Llama-2 7B 做领域继续预训练，并用 LoRA 进行参数高效适配。领域语料为 Alibaba 微服务调用图，约 1.36M 图、1.1B tokens。预训练让模型学习服务名、调用关系和属性值的领域语言分布；这一步本身不教故障因果知识。（§3.1）

#### B. 递归分层生成

给定父服务或当前图层，模型在同一父节点下生成一组边；每条边包含服务标识、通信类型、时间 / 延迟字段。下一层待生成条件随后传给下一次调用，直到达到深度或边数条件。概率分解写为：

P(t | c) = ∏(k=1…l) P(c^(k+1), t^k | c^k)

其中 t^k 是第 k 层生成的边文本，c^k 是本层条件，c^(k+1) 是递归传下去的下一层条件。递归拆解把“整个长图一次生成”改成“按调用层逐步生成”，降低全局约束丢失风险。（§3.2, Eq. 1）

#### C. 指令微调与约束推理

监督微调样本包含自然语言约束和目标 Trace 层。训练损失不对初始条件文本计算，而对模型应生成的图层和下一步条件计算。作者还在输入/输出中加入中间的算术、逻辑步骤，例如当前已用边数与剩余边数、深度状态，让模型在生成时跟踪约束，而不只是模仿字段表面格式。（§3.3, Fig. 2）

推理可指定边数、深度、通信类型比例或高延迟条件。稀有通信被定义为频次低于 10% 的类型；高延迟条件按真实数据第 90 百分位阈值设定。模型据此输出 Trace DAG。解析失败或约束违例的过滤细节并非所有部署场景都明确规定，使用者需要自行验证生成图。

#### D. 训练与端到端流程

1. 从真实 Trace 提取图边字段与图级统计条件。
2. 对字段文本化并扰动顺序 / 条件可见性，形成领域语料和指令数据。
3. 在 Llama-2 7B 上做领域继续预训练，再做 LoRA 指令微调。
4. 推理时给出条件，按图层递归生成。
5. 解析输出并检查 DAG / 条件满足度；将图用于结构分布评估或下游任务。

检测器不是 TraceLLM 的组成部分；论文的下游任务是外部验证，不应把它描述成端到端异常检测器。（§3–4）

### 9. Experimental Evidence

- **数据**：Alibaba 2022 微服务 Trace 图；真实样本另用于合成训练 / 真实测试的下游实验。
- **比较方法**：概率生成、TVAE、GReaT、基础 Llama / 指令基线、递归生成和有无指令微调的消融。
- **结构有效性**：检查有效 DAG、指定深度和边数、边属性 / 时间约束。递归+指令微调在大图条件下显著优于基线：边数超过 15 时，基线有效率低于 25%；深度超过 4 时接近 0。递归和指令微调在这些困难范围可提高约 30% / 35%（论文分别报告的条件有效率增益），指令微调相对仅递归再提升约 23%–36%；温度 1 下性能约提升 10%。（§4.1, Fig. 3–4；指标描述按论文报告）
- **统计分布**：热门调用 KL 约为 TraceLLM 0.16、GReaT 0.11、概率方法 3.84、TVAE 0.74，说明 TraceLLM 大幅优于概率 / TVAE，但不是该项最优。热门调用 Top-K 准确率在 K≤50 时超过 90%，K=500 时约 65%。（§4.2, Fig. 5）
- **下游迁移**：用 5K 合成调用图训练、2K 真实图测试。FIRM SVM 的准确率距真实数据训练约 1.5 个百分点；对照生成方法的差距报告为 6–81 个百分点。该结果支持 Trace 在特定调用图预测任务上的效用，不证明异常根因真实性。（§4.3, Fig. 6）
- **条件遵循 / 补全**：稀有通信预测约 76.8%，高于 Llama-2 基线 60.6% 和 Llama-3.1 405B ICL 45.6%；缺失字段补全准确率超过 70%，相对基线提高约 30–40 个百分点。（§4.4–4.5, Fig. 7）
- **真实性边界**：实验验证结构、统计及选定下游任务；没有真实故障注入标签、与 Metric / Log 的同步生成或面向故障检测收益的实验。

### 10. Limitations

#### A. Author-stated limitations

- 论文未以独立小节列出可明确归属的作者局限；相关适用边界在方法 / 实验范围中说明。

#### B. Reasoned inference

- 训练语料来自单一 Alibaba 系统，可能有服务 / 拓扑域偏移。
- 结构与统计相似不证明故障因果机制真实；稀有通信或高延迟条件不等于故障注入。

#### C. Evidence gaps

- 没有故障根因语义标签或真实异常检测收益实验。
- 未生成与 Metric / Log 同步的多模态事件，也没有跨模态因果一致性检验。

### 11. Research Implications

**本知识库分析**：用于结构化 Trace 生成基线；与真实故障注入器联合时，需补充故障根因、Metric / Trace / Log 一致性和真实数据收益验证。

### 12. Related Papers

同专题 `Synthetic Time Series` 和 `AIOpsLab`提供运行系统 / 故障注入对照；`LLM-AP`生成数值窗口。TSAD `CAPMix`处理 KPI 伪异常。

### 13. Evidence References

| 论断 | 原文定位 |
| --- | --- |
| 训练语料与图表示 | PDF §§2–3.1, pp.2–3 |
| 递归分层生成及概率分解 | PDF §3.2, Eq. 1, Fig. 2 |
| LoRA 指令微调与约束状态推理 | PDF §3.1–3.3 |
| 结构约束有效率 | PDF §4.1, Figs. 3–4 |
| 分布及下游迁移 | PDF §§4.2–4.3, Figs. 5–6 |
| 条件遵循与字段补全 | PDF §§4.4–4.5, Fig. 7 |
| 故障/多模态能力边界 | PDF §4 与论文整体任务定义；本知识库分析 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "tracellm",
  "title_en": "Large Language Models as Realistic Microservice Trace Generators",
  "title_zh": "TraceLLM：大语言模型驱动的真实微服务调用轨迹生成",
  "authors": [
    "Donghyun Kim",
    "Sriram Ravula",
    "Taemin Ha",
    "Alexandros G. Dimakis",
    "Daehyeok Kim",
    "Aditya Akella"
  ],
  "year": 2025,
  "venue": "EMNLP 2025",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/tracellm_emnlp2025.pdf",
  "reading_note_path": "papers/aiops/tracellm/notes.md",
  "knowledge_card_path": "papers/aiops/tracellm/knowledge-card.md",
  "code_url": "https://github.com/ldos-project/TraceLLM",
  "research_area": "微服务 Trace 结构化生成与生成式系统数据",
  "method_tags": [
    "microservice-trace",
    "LLM-generation",
    "DAG",
    "recursive-generation",
    "structured-data"
  ],
  "research_scenario": "给定图级自然语言或结构条件，生成由服务调用边构成的 DAG；服务 Trace 作为离线结构化数据供下游建模。生成对象不是故障标签、数值 Metric、Log 或在线异常判断。",
  "research_problem": "在真实调用图量大、层级深且必须满足 DAG / 边数 / 深度条件时，如何生成结构有效、字段统计合理且对特定下游任务有用的微服务调用图？",
  "core_challenges": [
    "长图生成容易违反 DAG、深度、边数等结构条件（PDF §§1–3）。",
    "长序列逐 token 生成容易丢失层级和全局约束（PDF §3.2）。",
    "模仿高频分布难覆盖稀有通信 / 延迟条件（PDF §§3.3–4.1）。"
  ],
  "existing_method_limits": [
    "规则 / 概率生成难表达复杂条件组合；表格生成器不能自然保留调用图递归结构；未经约束的通用 LLM 可能输出无效图。以上是作者动机，论文实验证据集中在所选 Alibaba 图语料和图任务。"
  ],
  "core_idea": "将调用图转为层级文本，按父节点 / 调用层递归生成边；把边数、深度等约束状态显式纳入条件和指令微调，使模型既学习领域字段又可控地扩展 DAG。",
  "technical_innovations": [
    "递归 DAG 文本生成：每轮生成一层边和下一层条件，针对长结构约束；相较单次扁平输出，困难边数 / 深度下有效率更高（§3.2, Eq.1; §4.1）。",
    "约束推理指令微调：将剩余边数 / 深度等中间算术状态纳入序列，训练损失不预测初始条件文本；相较仅递归消融，报告约 23%–36%条件准确率提升（§3.3–4.1）。",
    "领域继续预训练 + LoRA：在约 1.36M 图 / 1.1B tokens 上学习微服务字段分布；这是领域适配基础，不等于故障机制学习（§3.1）。"
  ],
  "methodology": {
    "architecture": "Alibaba Trace 图字段文本化 → Llama-2 7B 领域继续预训练 → LoRA 指令微调 → 条件化递归生成 DAG 层 → 解析和图约束验证。",
    "data_processing": "图边字段包括 Src / Dest / communication type / start / finish 等；随机打乱字段顺序，并随机打乱 / 丢弃条件属性；图级条件含深度、边数、时延、通信类型。训练语料约 136 万图、11 亿 token。",
    "modules": [
      "字段序列化：一条边编码为结构化文本；随机字段顺序降低位置捷径。",
      "递归生成器：输入当前层条件 c^k，输出本层文本 t^k 与下一层条件 c^(k+1)，按父节点分层扩展。",
      "指令约束模块：中间状态描述剩余边数和深度；生成后验证 DAG、时间和条件。"
    ],
    "key_formulas": [
      "P(t|c)=∏(k=1…l)P(c^(k+1),t^k|c^k)（Eq.1）；t^k 表示第 k 层边文本，c^k 表示该层条件。"
    ],
    "training": "先在 Alibaba 2022 调用图语料上继续预训练 Llama-2 7B，再用 LoRA 指令微调。微调样本由约束与分层 Trace 构成；损失针对生成层 / 下一步条件，而非初始条件本身。故障根因不是训练监督标签。",
    "inference": "给定边数、深度、通信频率或延迟条件，逐层生成直到满足终止条件；解析输出并检查结构 / 字段约束。论文实验报告有效性，但通用部署的解析失败回退规则未完全说明。",
    "end_to_end": "真实 Trace DAG → 文本化及条件抽取 → 领域适配 LLM → 递归生成 → 结构 / 分布 / 条件验证 → 合成 Trace 用于图任务。"
  },
  "experimental_evidence": {
    "datasets": [
      "Alibaba 2022 Microservice Call Graph，约 1.36M graphs / 1.1B tokens。"
    ],
    "baselines": [
      "概率生成模型",
      "TVAE",
      "GReaT",
      "基础 Llama / 指令基线",
      "递归 / 指令微调消融"
    ],
    "metrics": [
      "DAG / 条件有效率",
      "popular-call KL / Top-K accuracy",
      "下游 FIRM 准确率",
      "条件跟随与属性补全准确率"
    ],
    "main_results": [
      "边数 >15 时基线结构有效率低于 25%，深度 >4 时接近 0；递归与指令机制在困难条件下提升有效率（§4.1, Figs.3–4）。",
      "热门调用 KL：TraceLLM .16，GReaT .11，概率方法 3.84，TVAE .74；TraceLLM 并非每项统计最佳（§4.2, Fig.5）。",
      "5K 合成训练 / 2K 真实测试，FIRM SVM 准确率距真实训练约 1.5 个百分点；其他生成基线差距报告为 6–81pp（§4.3, Fig.6）。",
      "稀有通信预测 76.8%，高于 Llama-2 60.6% 与 Llama-3.1 405B ICL 45.6%；补全准确率 >70%（§§4.4–4.5, Fig.7）。"
    ],
    "ablations": [
      "去递归 / 去指令微调会降低大深度 / 大边数条件有效率；递归和指令微调分别贡献，见 Fig.3–4。"
    ],
    "robustness_generalization": [
      "以温度、条件规模和下游训练测试图评估生成鲁棒性；不是跨云平台故障迁移测试。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [],
    "reasoned_inference": [
      "训练语料来自单一 Alibaba 系统，可能有服务 / 拓扑域偏移。",
      "结构与统计相似不证明故障因果机制真实；稀有通信或高延迟条件不等于故障注入。"
    ],
    "evidence_gaps": [
      "没有故障根因语义标签或真实异常检测收益实验。",
      "未生成与 Metric / Log 同步的多模态事件，也没有跨模态因果一致性检验。"
    ]
  },
  "research_implications": [
    "可作为调用 DAG 合成方法参照；若应用于故障数据，应额外把故障动作、受影响边和外部遥测条件化并单独验证（本知识库分析）。"
  ],
  "related_papers": [
    "synthetic-cloud-microservices",
    "aiopslab",
    "llm-ap-synthetic-augmentation",
    "capmix"
  ],
  "evidence_references": [
    "PDF §§2–3.1, pp.2–3：图表示与领域数据。",
    "PDF §3.2, Eq.1, Fig.2：递归生成。",
    "PDF §§4.1–4.5, Figs.3–7：结构、统计、下游和指令实验。"
  ],
  "provenance": {
    "pdf_sha256": "4d34ad1dff644e65d1d0fd6ca816cba9664747ccc46c45f405a019eef2cd9c26",
    "reading_note_sha256": "191df22ec708b5b1367d5bee70d5cff3f154d2e14a0ef64ed5a37c645e54a862",
    "knowledge_card_sha256": "8735c34a8a104db759f78844afe00ef9254e37341c1fed3745552d9bdde042f9",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->

---

<a id="paper-02-llm-ap-synthetic-augmentation"></a>
## Paper 02 — LLM-AP：基于合成时间序列增强的大语言模型异常检测

## Knowledge Dossier — LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation

### 1. Basic Information

- **English title**: LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation
- **中文译名**：LLM-AP：基于合成时间序列增强的大语言模型异常检测
- **Authors**: Geunho Lee, Jieun Lee, Tae-yong Kim, Jongpil Jeong
- **Venue / year / CCF**: Applied Sciences 16(14), 6851 (2026) / 2026 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `llm-ap_applied-sciences-2026.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: null
- **Research area**: LLM 数值序列生成与单变量 TSAD 数据增强
- **Method tags**: LLM, univariate-TSAD, synthetic-anomaly, prompting, validation, NAB

### 2. Research Scenario

作者研究真实单变量时间序列异常检测中标注异常不足、类型长尾，以及已有合成增强可能产生失真数值窗口的问题。输入为一维连续值序列、已标注的异常区间和检测模型；输出为通过验证的额外异常窗口及增强后的训练集，最终任务是检验增强是否提升检测器 F1。NAB 的 47 条真实时间序列涵盖五类领域；不是微服务专用 KPI，也不含调用 Trace、日志和根因标签。（PDF §§1–3, §4.1）

#### 核心挑战

1. **异常类型要贴合数据**：固定注入可能产生数据里没有的异常形态。LLM-AP 先从已有标注归纳 6 种异常子类型，仅生成数据中实际出现的类型。（§3.2）
2. **语言模型容易返回不可解析 / 长度不符的数据**：结构化提示和 JSON 输出仍不能保证数值可靠，需要长度修复及非有限值检查。（§3.3.1）
3. **异常要有可检测信号，又不能脱离上下文**：过弱变化没有检测意义，过强或局部结构不匹配的序列不真实。作者使用距离上、下界和类型规则筛选。（§3.3.2–3.3.5）
4. **检测指标提升不能只来自合成标签数量**：需要对比增强前后、验证 / 未验证样本，以及多种检测器。（§4）

### 3. Research Problem

在异常稀少的单变量真实序列中，如何依据本序列已有异常类型生成长度、形态和变化强度都合理的数值异常窗口，并通过检测结果验证其增益？

### 4. Core Challenges

作者认为传统规则 / 统计扰动难以构造多样且与原始上下文相容的异常，而未约束的 LLM 输出也可能有长度、数值和形态缺陷。核心思想是让 LLM 负责“依据上下文改写数值”，由一套可重复的自动筛选管线负责“判断是否保留”。LLM 不被微调，只以 zero-shot / few-shot 方式接收任务说明、正常样本与少量异常示例。

### 5. Limitations of Existing Methods

#### A. 异常类型与窗口构造

预处理器沿每个异常时间点寻找一个最近的滑动窗口，避免一个异常点因半径扩张而重复标出大量窗口。作者按启发式阈值先识别异常子类型，若阈值不稳定则用归一化特征分数回退。六类包括 local spike、level shift、variance change、trend change、gradual drift、slow degradation。每一类只在当前序列确有实例时进入生成；提示样例最多含 2 个正常窗口和最多 2 个异常窗口，每个窗口最多 40 个点。数据集 / 文件名用于自动给出领域背景，而非人工逐序列设计提示。（§3.1–3.2）

#### B. LLM 数值窗口生成

将窗口转为结构化文本 / JSON 形式，提示模型保留正常上下文并按目标类型修改可变数值和趋势。候选模型是冻结的 GPT-3.5-turbo 与 GPT-4o，做零样本 / 少样本提示，不进行针对数据集的微调；模型输出转回数值窗口。论文给出 Append（追加生成样本）与 Replace（替换选定原始异常样本）的增强方式。（§3.2–3.3）

#### C. 五阶段样本验证

1. **格式与长度**：解析 JSON 和期望字段；若长度偏差不超过 5%，按线性插值修正；NaN / Inf 或严重长度不匹配则拒绝。
2. **RelDTW 距离下限**：根据相对动态时间规整距离判断是否有足够变化；小于 0.05 视为信息不足。
3. **异常存在性**：点异常检查 z-score 最大值是否大于 3，且 spike 数在 1–3；集体异常用 CUSUM，阈值 h=4σ。
4. **子类型匹配**：利用转折尖锐度、变化后稳定度、方差比例、单调性等形态特征，和 200 对正常窗口校准的阈值比较，确认候选符合目标类型（Table 2）。
5. **真实性距离上限**：RelDTW 大于 10 则视为偏离过大并丢弃。

任一检查失败时，Self-Refine 将错误代码、失败指标和目标类型反馈给 LLM，最多重试 3 次；某类型连续 15 次生成失败则停止该类型。RelDTW 在此被用作过滤信号；它不是生成数据与真实异常分布一致的完整度量。（§3.3, Eqs. 1–12, Table 2）

#### D. 训练 / 推理端到端

1. 解析训练序列中的异常点和子类型。
2. 选取正常 / 异常上下文窗口并形成结构化提示。
3. GPT 返回新数值序列。
4. 依序做解析、距离、异常性、子类型、距离上限检查；必要时反馈重试。
5. 将保留样本追加或替换到数据集。
6. 训练 TimesNet、PatchTST、Transformer 或 Autoformer 等检测器；原文未规定独立的新检测模型。

推理阶段检测器仍在新测试窗口上输出异常分数 / 标签；生成器不参与在线推理，除非后续工作另行设计。

### 6. Core Idea

让冻结 GPT 按结构化提示改写数值窗口，再由格式、异常存在、类型匹配、相似距离等规则筛选；模型生成能力和可信度验证明确分开。

### 7. Technical Innovations

- 从标注窗口识别六类异常并仅生成已出现类型，降低任意类型迁移；证据为类型构造流程，不代表类别识别完美（§3.1–3.2）。
- 五阶段验证：格式 / 长度、RelDTW 下界、z-score / CUSUM 异常性、形态子类型、RelDTW 上界；Table 8 显示验证样本优于未验证样本。
- Self-Refine：反馈具体失败指标最多三轮，连续 15 次失败时停止该类型；提升通过率，但不能证明分布真实性。

### 8. Methodology

- **数据 / Baseline**：NAB 47 条真实数据，45 条可成功生成，2 条失败（AWS EC2 disk writes 数据大多为零值突发；keystroke 序列近似二元）。对比无增强、jitter / scaling 和未验证合成样本；检测器 TimesNet、PatchTST、Transformer、Autoformer。（§4.1–4.3）
- **设置**：两 GPT 版本、temperature 0.5 / 1.0，Append / Replace。GPT-3.5 通过验证 1541 个窗口，GPT-4o 1604 个；目标异常占比 10%。（§4.2）
- **结果**：TimesNet 上 GPT-4o、temperature=1、Append 得到 F1 0.7238±0.001，对照 0.6893±0.002；PatchTST 最佳 0.7024，对照 0.6929；Transformer 最佳 0.6948，对照 0.6858。Autoformer 反而全部低于其无增强对照，例如 GPT-3.5、temperature=1、Replace 为 0.2753 对 0.6071。（Table 8）
- **验证消融**：对 TimesNet / PatchTST / Transformer，验证后样本在所有比较配置中优于未验证样本；未验证合成样本的收益不高于基线。Autoformer 是例外，所有增强配置均降低性能。（Table 8）
- **支持范围**：结果支持“经过目标形态 / 统计检查后，LLM 生成可为部分检测器增益”。不支持生成异常可普遍迁移、适用于多变量系统或反映微服务故障原因。

### 9. Experimental Evidence

**作者明确讨论**：慢漂移和缓慢退化难保留复杂局部上下文；LLM 有时把振荡序列改写为简单单调 ramp，虽通过部分统计规则但形态语义可能失真。未来方向包括与 TimeGAN / VAE 比较、微调 LLM、改进模式保留与结构验证。（§5–6）

**本知识库分析**：五步检查关注局部统计、异常类型和窗口距离，不等于真实异常机制真实性；无 train-on-synthetic/test-on-real 分布泛化评估，无 Metric / Trace / Log、故障知识或因果约束。只评估单变量 NAB，尚不能推断在业务负载跃迁和真实故障共现时有用。仅和 jitter / scaling 比，缺少强生成模型作为基线。

**专题关系**：LLM-AP 是本组中真正让 LLM 直接改写数值序列的一篇；与 `GenIAS` 的 VAE 潜空间注入、`CAPMix` 的形态扰动 + 软标签可信度构成生成机制对比。与 `Synthetic Time Series` / `AIOpsLab` 不同，它不在运行系统中执行故障。与 `TraceLLM` 相比，生成目标分别是数值窗口和调用 DAG，均未建立跨模态一致性。

### 10. Limitations

#### A. Author-stated limitations

- 慢漂移 / 慢退化可损失原有局部结构，振荡上下文可能变成单调 ramp；作者计划改进保型和结构验证，并比较 TimeGAN / VAE（§§5–6）。

#### B. Reasoned inference

- 五阶段规则不是跨数据分布真实性度量；效果只覆盖单变量 NAB 和部分检测器。
- 无微服务 / 故障知识 / 多模态标签；不能据此推断实际故障语义。

#### C. Evidence gaps

- 没有 train-on-synthetic/test-on-real 的跨域验证。
- 未评估多变量 KPI、Trace / Log 或正常业务波动与故障共现。

### 11. Research Implications

**本知识库分析**：可作为 LLM 数值异常增强路线参照；应明确区分“通过检测规则”和“真实机制 / 分布真实”。

### 12. Related Papers

`GenIAS`是潜空间生成对照；TSAD `CAPMix`用 DTW 修订伪异常置信度；`TraceLLM`目标是调用 DAG。

### 13. Evidence References



<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "llm-ap-synthetic-augmentation",
  "title_en": "LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation",
  "title_zh": "LLM-AP：基于合成时间序列增强的大语言模型异常检测",
  "authors": [
    "Geunho Lee",
    "Jieun Lee",
    "Tae-yong Kim",
    "Jongpil Jeong"
  ],
  "year": 2026,
  "venue": "Applied Sciences 16(14), 6851 (2026)",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/llm-ap_applied-sciences-2026.pdf",
  "reading_note_path": "papers/aiops/llm-ap-synthetic-augmentation/notes.md",
  "knowledge_card_path": "papers/aiops/llm-ap-synthetic-augmentation/knowledge-card.md",
  "code_url": null,
  "research_area": "LLM 数值序列生成与单变量 TSAD 数据增强",
  "method_tags": [
    "LLM",
    "univariate-TSAD",
    "synthetic-anomaly",
    "prompting",
    "validation",
    "NAB"
  ],
  "research_scenario": "NAB 五领域 47 个真实单变量连续序列；输入已有异常区间及正常 / 异常窗口，输出增强样本供检测器训练，不含微服务遥测或根因信息。",
  "research_problem": "在异常稀少的单变量真实序列中，如何依据本序列已有异常类型生成长度、形态和变化强度都合理的数值异常窗口，并通过检测结果验证其增益？",
  "core_challenges": [
    "数据集异常类型不同，统一随机扰动可能不匹配本序列（§3.1）。",
    "LLM 可能给出格式、长度、数值范围错误（§3.3.1）。",
    "候选需既可检测又不脱离局部模式；单一距离阈值不能完整代表真实性（§3.3）。"
  ],
  "existing_method_limits": [
    "固定规则增强可控但难兼顾异常多样性 / 上下文；无约束 LLM 输出需经验证。实验基线主要是 jitter / scaling，尚未与强 GAN / VAE 生成器充分比较。"
  ],
  "core_idea": "让冻结 GPT 按结构化提示改写数值窗口，再由格式、异常存在、类型匹配、相似距离等规则筛选；模型生成能力和可信度验证明确分开。",
  "technical_innovations": [
    "从标注窗口识别六类异常并仅生成已出现类型，降低任意类型迁移；证据为类型构造流程，不代表类别识别完美（§3.1–3.2）。",
    "五阶段验证：格式 / 长度、RelDTW 下界、z-score / CUSUM 异常性、形态子类型、RelDTW 上界；Table 8 显示验证样本优于未验证样本。",
    "Self-Refine：反馈具体失败指标最多三轮，连续 15 次失败时停止该类型；提升通过率，但不能证明分布真实性。"
  ],
  "methodology": {
    "architecture": "训练序列标注 / 窗口抽取 → 结构化 few-shot prompt → 冻结 GPT-3.5-turbo / GPT-4o 生成数值 → 五阶段验证及修正 → Append / Replace 增强 → 多种检测器评估。",
    "data_processing": "按异常点提取一个最近窗口；检测 6 类：spike、level shift、variance change、trend change、gradual drift、slow degradation。提示最多 2 正常 + 2 异常样本，每个最多 40 点；自动从文件名推断领域；仅生成现有数据中出现的类别。",
    "modules": [
      "LLM 生成：输入结构化窗口 / 类型说明，生成同长度数值序列；不微调 GPT。",
      "格式与长度检查：JSON 解析；长度偏差 ≤5% 时线性插值，否则拒绝 NaN / Inf 或严重偏差。",
      "有效异常检查：RelDTW <.05 拒绝；点异常要求 max z>3 且 spike 1–3 个；集体异常用 CUSUM h=4σ。",
      "类别与真实性过滤：由转折尖锐度、变化后稳定度、方差比、单调性等与 200 对正常窗口校准阈值匹配；RelDTW>10 拒绝。",
      "Self-Refine：失败原因反馈模型，最多 3 次；单一类型连续 15 次失败后停止。"
    ],
    "key_formulas": [
      "RelDTW：论文 Eq.1–2 的相对动态时间规整距离，用于设定下界 .05 / 上界 10。",
      "集体异常 CUSUM：阈值 h=4σ；完整递推形式见 PDF Eqs.3–8。"
    ],
    "training": "GPT-3.5-turbo / GPT-4o 冻结 zero-shot / few-shot 推理；每类示例和提示针对输入序列构造。不存在生成器参数训练；下游检测器另行训练。",
    "inference": "生成阶段离线筛选并将窗口 Append 或 Replace。实际测试期仅检测器运行；模型推理时异常分数由 TimesNet / PatchTST / Transformer / Autoformer 等给出，论文未提出统一分数公式。",
    "end_to_end": "单变量序列 + 异常标注 → 类型 / 窗口抽取 → GPT 改写 → 规则验证 / Self-Refine → 数据增强 → 检测器训练和 NAB 测试。"
  },
  "experimental_evidence": {
    "datasets": [
      "NAB 47 real-world univariate series, five domains; 45 successful, 2 failed."
    ],
    "baselines": [
      "无增强",
      "jitter / scaling",
      "验证前 LLM 样本；TimesNet、PatchTST、Transformer、Autoformer 检测器"
    ],
    "metrics": [
      "F1（均值±标准差）",
      "生成通过数和异常比例"
    ],
    "main_results": [
      "GPT-3.5 1541、GPT-4o 1604 个验证窗口，目标异常比例 10%（§4.2）。",
      "TimesNet GPT-4o temp=1 Append F1 .7238±.001 vs .6893±.002；PatchTST .7024 vs .6929；Transformer .6948 vs .6858（Table 8）。",
      "Autoformer 所有增强设置低于 baseline；GPT-3.5 temp=1 Replace .2753 vs .6071（Table 8）。"
    ],
    "ablations": [
      "验证 vs 未验证：验证样本在 TimesNet / PatchTST / Transformer 配置中更优；Autoformer 例外，所有增强均降分（Table 8）。Append / Replace、温度和 LLM 版本也被比较。"
    ],
    "robustness_generalization": [
      "45/47 NAB 序列成功；两失败对象为 AWS EC2 disk writes（近零值突发）与 keystroke（近二元），说明数据形态适用性有限。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [
      "慢漂移 / 慢退化可损失原有局部结构，振荡上下文可能变成单调 ramp；作者计划改进保型和结构验证，并比较 TimeGAN / VAE（§§5–6）。"
    ],
    "reasoned_inference": [
      "五阶段规则不是跨数据分布真实性度量；效果只覆盖单变量 NAB 和部分检测器。",
      "无微服务 / 故障知识 / 多模态标签；不能据此推断实际故障语义。"
    ],
    "evidence_gaps": [
      "没有 train-on-synthetic/test-on-real 的跨域验证。",
      "未评估多变量 KPI、Trace / Log 或正常业务波动与故障共现。"
    ]
  },
  "research_implications": [
    "LLM 候选生成和独立样本验证的职责划分可复用；规则验证结果应作为筛选信号而非真实性证明（本知识库分析）。"
  ],
  "related_papers": [
    "genias",
    "tracellm",
    "synthetic-cloud-microservices",
    "capmix"
  ],
  "evidence_references": [
    "PDF §§3.1–3.3, Eqs.1–12, Table 2：窗口生成及五阶段验证。",
    "PDF §§4.1–4.3, Table 8：数据、检测器结果及消融。",
    "PDF §§5–6：结构保持问题与未来方向。"
  ],
  "provenance": {
    "pdf_sha256": "834536d5ab3c8095c4b27aeda10f9f0587d544d7c9c24061fff52489085fbef3",
    "reading_note_sha256": "30b36e8191bffe3ca0c9e804f7f3d56248afae30ecce7b09880276baa87ce51e",
    "knowledge_card_sha256": "1e9aa3b7748d5c2d1a36e36d705f2951074c83746ee4d58f33bf83bb2d3dbd27",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->

---

<a id="paper-03-synthetic-cloud-microservices"></a>
## Paper 03 — 面向云微服务异常检测的合成时间序列

## Knowledge Dossier — Synthetic Time Series for Anomaly Detection in Cloud Microservices

### 1. Basic Information

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

### 2. Research Scenario

研究面向云端微服务监控数据获取：真实线上故障难以反复触发，异常标签稀少，单纯数学合成的时间序列缺少系统运行背景。作者希望在可控云环境中形成包含正常服务需求变化、负载异常和基础设施故障响应的带标签数据。测试床部署于 AWS EKS，使用 Sock-Shop 与 Online Boutique 两个电商应用；Locust 产生用户流量，Istio / Prometheus、CloudWatch 和 Fluent Bit 等采集系统指标、服务指标和日志。（PDF §§3.1–3.5, pp.3–8）

输入包括用户到达 / 请求负载参数以及 FIS 故障注入模板；输出包括带时间戳的节点、Pod、服务指标序列和独立的负载 / 基础设施故障标签。论文的主要可观测序列为指标，不包含本版本的分布式 Trace 数据；日志被采集组件列出，但主要量化数据集清单是指标。异常标签来自注入计划和时间区间，因此偏向实验可控的窗口 / 时间点异常标注，而不是人工确认的生产事故根因。

### 3. Research Problem

在缺少真实故障标注、难以重复触发生产事故时，如何构造包含动态正常负载、负载异常、基础设施故障及可对齐指标标签的微服务数据？

### 4. Core Challenges

1. **正常负载并非平稳常数**：业务需求会有趋势和多周期变化。若只用恒定背景，检测器容易把常见日常峰谷错判为故障。（§3.2, Eq. 1）
2. **数学异常不等于系统故障**：直接在指标上加尖峰不能复现 CPU 压力、网络延迟、Pod 删除等系统机制引发的联动变化。作者用云环境故障注入将“故障动作”与被观测影响联系起来。（§3.3–3.4）
3. **负载异常与资源故障需分开标注**：请求突变可能是业务侧需求异常；CPU hog 或网络损失则是基础设施故障，两者影响路径不同。论文分别生成负载异常与 FIS 故障，但没有证明某一检测器能可靠区分所有并发情形。
4. **规模与观测成本**：云资源和多服务采集成本让实际故障样本难以大量构造。受控实验牺牲了生产环境的复杂度和多样性。（§3, §5）

### 5. Limitations of Existing Methods

#### A. 正常业务负载

用户到达负载由基线、缓慢趋势、多周期分量和随机扰动构成：

N(t) = (1 + trend(t)) × base_load + Σᵢ Aᵢ[(sin(2πt/Tᵢ))² + wnᵢ(t)]

其中 trend(t) 由分段斜率形成；每个趋势区间有概率 p=0.01 出现突变；Tᵢ 和 Aᵢ 控制多个周期和振幅，wnᵢ(t) 为噪声。Locust 的 spawn rate 按相邻负载点左右导数的对称平均调节，使生成负载随时间曲线变化。（§3.2, Eqs. 1–2）

#### B. 负载异常

Algorithm 1 以概率 p 选择持续时长 U(a,b)，对选定区间的用户负载乘以从 U(c,d) 采样的因子。该操作构造的是突增 / 突降式业务流量异常，而非某种明确根因（例如促销、爬虫、排队瓶颈）。基础正常负载和异常流量形态被分别控制与打标。（§3.3, Algorithm 1）

#### C. 基础设施故障注入

使用 AWS Fault Injection Simulator 模板 / 注入程序，执行 Pod 或节点 CPU 压力、内存压力、网络延迟、丢包、I/O 压力、Pod 删除 / 节点重启等操作。Algorithm 2 随机选取目标资源和故障模板；标签由故障注入开始和持续时间产生。图示展示故障对指标的传播反应，例如网络丢包可推高尾延迟和错误率，CPU / 内存压力影响相应资源指标，Pod 删除导致服务重新调度。（§3.4, Algorithm 2, Figs. 4–6）

#### D. 系统与数据

EKS 上运行 Sock-Shop、Online Boutique；Istio 负责服务网格，Locust 负载驱动。采集包括 25 个节点级指标 × 5 节点 = 125、18 个 Pod 指标 × 14 Pods = 252、9 个服务级指标 × 10 服务 = 90，总计 470 项指标。系统指标 / 服务指标的覆盖数量反映本实验部署，并非每种应用拓扑必然固定如此。（§3.1, Table 1）

论文示例运行持续 7 天并覆盖多种周期负载。故障参数示例包括 CPU 压力 100% 持续 4 分钟、内存压力 100% 持续 4 分钟、400ms 网络延迟 5 分钟、40% 丢包 2 分钟、I/O 压力 80% 持续 5 分钟；这些是实验配置示例，不应等同于生产事故严重程度。（§3.4–3.5, Tables 2–3）

### 6. Core Idea

将正常业务负载函数、Locust 请求驱动、AWS FIS 故障注入与 Prometheus / CloudWatch 多层监控组成可复现的数据生成 / 采集管线。

### 7. Technical Innovations

- 多趋势、多周期、噪声的正常负载函数 N(t)（§3.2, Eqs.1–2）。
- 用 Algorithm 1 以区间概率和负载倍率生成负载异常，将需求变化标签与基础设施故障标签分开。
- 用 AWS FIS 注入 CPU / memory / network delay / packet loss / I/O / pod / node 故障，并采集 470 项 node/pod/service 指标（§3.4–3.5）。

### 8. Methodology

本文没有训练检测模型。完整数据生成流程为：

1. 在 EKS 部署服务应用并设定基线负载与趋势 / 周期参数。
2. 由 Locust 按生成的需求曲线发起请求；监控组件记录正常状态遥测。
3. 按实验计划生成负载异常或触发 FIS 基础设施故障，并记录精确开始 / 结束时间与对象。
4. 同步收集节点、Pod、服务指标及日志；对异常标签进行时间区间对齐。
5. 形成可供后续检测器研究的数据集。论文没有提出推理阶段异常打分流程；检测算法评价被列为未来工作。

因此，本文所说“适合异常检测研究”的主要支持来自可控生成、指标覆盖和故障效应图，而非检测准确率提升实验。

### 9. Experimental Evidence

- **环境 / 模态**：AWS EKS、Sock-Shop 和 Online Boutique；主要为 470 项指标并采集日志。没有报告本数据集中的 Trace 采集与 Trace 样本。
- **故障类型**：计算、内存、网络延迟、网络丢包、I/O、Pod / 节点中断，以及独立的负载突变。
- **证据**：Fig. 4 展示监控设置；Figs. 5–6 展示注入前后指标 / 服务行为变化，支持故障注入能触发可观测影响。论文描述数据集提供负载与 FIS 独立标签，可用于后续分析。
- **不存在的实验**：无检测器 Baseline、无 Precision / Recall / F1 / AUPRC 结果、无合成数据训练与真实数据测试、无合成真实性打分或专家评审、无跨应用迁移对照。作者将检测性能评价列为后续方向。（§4–5, Conclusion）

### 10. Limitations

#### A. Author-stated limitations

- 数据面向有限电商应用和配置；检测算法评估留待后续（§5, Conclusion）。

#### B. Reasoned inference

- 负载异常按倍率调整，未描述需求变化的业务语义或根因。
- 日志虽被采集，主要数据规模与测量结果是指标；Trace 没有纳入该版多模态数据。

#### C. Evidence gaps

- 没有合成数据真实性 / 专家评估。
- 无真实生产测试、无合成训练对真实测试、无负载变化与故障同时发生的区分实验。

### 11. Research Implications

**本知识库分析**：适合做真实系统反馈与故障标签构造基准；需要把业务上下文、Trace 和并发事件加入数据覆盖。

### 12. Related Papers

`AIOpsLab`提供 Agent 与工具交互任务；`TraceLLM`生成调用 DAG；TSAD `CAPMix`处理窗口级训练增强。

### 13. Evidence References

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

---

<a id="paper-04-genias"></a>
## Paper 04 — GenIAS：时间序列异常实例化生成器

## Knowledge Dossier — GenIAS: Generator for Instantiating Anomalies in Time Series

### 1. Basic Information

- **English title**: GenIAS: Generator for Instantiating Anomalies in Time Series
- **中文译名**：GenIAS：时间序列异常实例化生成器
- **Authors**: Zahra Zamanzadeh Darban, Mike Wang, Geoffrey I. Webb, Shirui Pan, Charu C. Aggarwal, Mahsa Salehi
- **Venue / year / CCF**: arXiv:2502.08262v2, 2026-02-05（预印本） / 2026 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `genias_arxiv2502.08262.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: null
- **Research area**: 无监督 TSAD 异常样本合成与增强
- **Method tags**: TSAD, VAE, latent-perturbation, synthetic-anomaly, patching

### 2. Research Scenario

无监督 TSAD 常缺少真实异常标签，监督检测器和异常增强研究需要大量异常样本，但规则注入容易与真实异常不相似、潜在多样性不足。GenIAS 学习正常训练时间序列及其潜在分布，生成具有可控偏离程度的异常窗口，并作为合成数据支持检测器训练。输入为单变量或多变量原始时间序列窗口；输出是局部修改后的异常时间序列。该问题是通用 TSAD 数据增强，不是在线故障模拟或微服务异常诊断。（PDF §§1–3, pp.1–3）

### 3. Research Problem

如何只依赖正常序列学习可控潜变量偏离，并生成同时区别于正常、保持数据合理性和变量级局部性的异常样本？

### 4. Core Challenges

1. **候选异常需要兼具偏离和合理性**：潜变量必须从正常区分开，又不能被任意拉远到不符合数据尺度的区域。
2. **多变量异常需选择性发生**：若每个变量都同时被修改，合成样本会失去局部性和正常上下文；若统一扰动强度，数据中各变量的动态范围差异会导致注入失衡。
3. **单个模式难覆盖异常多样性**：使用固定噪声 / 规则扰动可能集中在狭窄异常形态。论文以 ARP 和 EDI 分别衡量与真实异常的表征接近度及生成样本差异性。（§3–4）
4. **潜空间生成不能自动等同异常语义**：若训练异常或真实故障原因未参与建模，潜在偏离仅表示相对所学正常分布的变化，不包含因果标签。

### 5. Limitations of Existing Methods

现有合成方法包括规则型点 / 区间注入、GAN / VAE 生成，以及在潜空间中随机扰动。作者强调既有方法常难同时控制偏离幅度、生成样本可信度和多样性。GenIAS 不另行训练异常类别生成器，而是在正常编码分布周围学习哪些潜维度应变化、变化多少；再把候选异常投影回与原始样本相连的局部 patch 中，保留未显著变化的变量轨迹。

### 6. Core Idea

先把正常表示压缩为紧致潜空间，再以可学习逐维 ψ 扰动标准差产生候选异常；解码后只替换相对原输入变化超过动态范围阈值的变量。

### 7. Technical Innovations

- 上下界 triplet-style 潜扰动损失，在潜空间要求异常偏离落在 δmin / δmax 区间（§3.2, Eq.3）。
- 零维惩罚与 compact-KL 共同控制扰动稀疏性和正常空间紧致性（Eqs.2,4）。
- 动态范围阈值 patching，按变量级 L2 差异选择是否替换，而不是整样本覆盖（§3.3, Algorithms 1–2）。

### 8. Methodology

#### A. 正常潜变量学习

使用 TCN 编码器 / 解码器处理窗口 x。编码器输出均值 μ 和标准差 σ，按重参数化取得正常潜样本：

z = μ + σ ⊙ ε，ε ~ N(0,I)。

与通常 VAE 相比，GenIAS 使用标准差小于 1 的紧致先验标准差 σ_prior，KL 项推动正常表示集中在更紧的区域，便于将可控偏离表示成候选异常。（§3.1, Eq. 1–2）

#### B. 潜空间扰动生成

候选异常潜变量为：

z̃ = μ + ψ ⊙ (σ ⊙ ε)。

ψ 是可学习的逐维扰动尺度，均值 μ 固定，扩张 / 重标定标准差贡献。扰动损失 L_perturb 用 triplet 风格的距离约束，让生成潜变量与正常重构的距离至少达到 δ_min，同时不超过 δ_max，兼顾偏离和可行性。零维扰动惩罚 L_zero-perturb 鼓励保留部分潜维度不变，增加潜维度选择性。紧致 KL 项 L_comp-KL 收缩正常表示；重构项 L_recon 保持 VAE 对原始窗口的表达能力。总损失：

L = α L_recon + β L_perturb + γ L_zero-perturb + ζ L_comp-KL。

符号 δ_min / δ_max 为偏离边界，α、β、γ、ζ 控制重构、异常扰动、维度稀疏与紧致先验项的权重。损失中的异常候选不是有真实故障标签的生成监督，而是针对潜空间几何的目标。（§3.2, Eqs. 3–6）

#### C. 原始空间逐维 patching

将生成潜变量经解码器得到候选序列 X̃。针对原始变量 d，计算与原始输入 X_d 的 L2 距离；若

||X_d − X̃_d||₂ > τ × (max(X_d) − min(X_d))

则以生成轨迹替换该变量，否则保留原始轨迹。τ 控制相对于变量动态范围的选择门槛。这个机制是按整条变量维度保留 / 替换，不是按单个时间点剪贴。Algorithm 1–2 描述候选生成和 patching。（§3.3）

#### D. 训练、生成与检测

1. 用训练集正常窗口优化 TCN-VAE 和上述联合目标。
2. 从正常窗口潜分布采样 z，再用 ψ 产生 z̃。
3. 解码成多维候选序列。
4. 依据逐维距离 / 动态范围阈值保留变化明显的轨迹，其余沿用原窗口。
5. 用合成样本与已有训练数据训练下游检测模型。

原文的生成评价使用学习到的深度表征；训练异常样本生成器并不需要把正常 / 异常类型以语言形式输入。下游异常评分是检测器自身实现的，GenIAS 不限定唯一检测器。

### 9. Experimental Evidence

- **数据集**：MSL、SMAP、SMD、SWaT、GECCO、SWAN、UCR、Yahoo-A1、KPI；六个多变量、三个单变量。默认窗口 T=200，MTS 潜维 100、UTS 潜维 50；Adam 1e-4、1000 epochs；α=1、β=.1、γ 在 UTS / MTS 设为 0 / .01、ζ=.1。（§4.1, Appendix）
- **生成质量**：ARP 用 DeepSVDD 表征空间评估生成异常与真实标注异常的接近程度；EDI 测多样性。平均排名分别为 ARP 1.78、EDI 1.22（越好排名更低），报告在比较的异常增强方法中表现强。（§4.2, Table 1）
- **检测收益**：GenIAS 与 CARLA 配合的平均 F1 为 .557，对比 CARLA .509；MSL .579 vs .523，SMAP .620 vs .529，Yahoo-A1 .811 vs .749。（Table 2）结果表明所选基准和检测器配置下可提高若干指标，不证明对所有系统 / 真实故障都有效。
- **Patching 消融**：MSL .579/.529、SMAP .620/.467、Yahoo .811/.794（F1/AUPR）；无 patch 时分别 .535/.466、.533/.425、.755/.776。（Table 3）
- **潜空间紧致性**：比较不同先验标准差，σ_prior=.5 得到较好结果；逐维扰动与 patching 对合成质量和部分检测结果有贡献。（§4.5–4.8, Tables 3–4）
- **证据限制**：ARP 使用真实测试异常表征作为质量参照，不能把“接近真实异常”解读为真实根因标签 / 机制匹配；检测实验不含微服务 Trace 与调用拓扑。

### 10. Limitations

#### A. Author-stated limitations

- 结论提出自适应扰动 / patching 和变量间相关性作为后续方向。

#### B. Reasoned inference

- 没有故障类型、业务上下文或多模态服务图；潜空间偏离不是故障语义。
- ARP 依赖 DeepSVDD 表征及基准异常标签，不能视为生产故障机制验证。

#### C. Evidence gaps

- 没有服务系统真实故障注入、Trace / Log 一致性或动态正常状态专门实验。

### 11. Research Implications

**本知识库分析**：适合作为经典深度生成路线与 LLM-AP 的方法对照；用多变量 patching 保留正常维度的思路需要在服务上下文下重新验证。

### 12. Related Papers

`LLM-AP`直接提示 LLM 改写；`CAROTS`显式用因果结构增强；`Synthetic Time Series`使用运行时故障注入。

### 13. Evidence References

| 论断 | 原文定位 |
| --- | --- |
| VAE 重参数化与紧致先验 | PDF §3.1, Eqs. 1–2 |
| 潜空间扰动及联合损失 | PDF §3.2, Eqs. 3–6 |
| 变量级 patching | PDF §3.3, Algorithms 1–2 |
| 数据、参数和 ARP / EDI | PDF §4.1–4.2, Table 1 |
| 下游检测与消融 | PDF §§4.3–4.8, Tables 2–4 |
| 作者未来方向 | PDF Conclusion |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "genias",
  "title_en": "GenIAS: Generator for Instantiating Anomalies in Time Series",
  "title_zh": "GenIAS：时间序列异常实例化生成器",
  "authors": [
    "Zahra Zamanzadeh Darban",
    "Mike Wang",
    "Geoffrey I. Webb",
    "Shirui Pan",
    "Charu C. Aggarwal",
    "Mahsa Salehi"
  ],
  "year": 2026,
  "venue": "arXiv:2502.08262v2, 2026-02-05（预印本）",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/genias_arxiv2502.08262.pdf",
  "reading_note_path": "papers/aiops/genias/notes.md",
  "knowledge_card_path": "papers/aiops/genias/knowledge-card.md",
  "code_url": null,
  "research_area": "无监督 TSAD 异常样本合成与增强",
  "method_tags": [
    "TSAD",
    "VAE",
    "latent-perturbation",
    "synthetic-anomaly",
    "patching"
  ],
  "research_scenario": "通用单变量 / 多变量时间序列训练数据不足时，生成候选异常窗口供下游 detector 训练；不是微服务遥测或故障 RCA。",
  "research_problem": "如何只依赖正常序列学习可控潜变量偏离，并生成同时区别于正常、保持数据合理性和变量级局部性的异常样本？",
  "core_challenges": [
    "潜空间异常应保持适中距离（§3.2）。",
    "多变量各维范围不同，注入不应破坏所有变量（§3.3）。",
    "生成质量同时涉及真实性与差异性（§4.2）。"
  ],
  "existing_method_limits": [
    "固定噪声 / 规则增强不能适应变量潜在分布；任意 VAE 潜变量偏移可能过远且整段修改原始序列；论文通过潜空间约束和逐维 patching 处理这些风险。"
  ],
  "core_idea": "先把正常表示压缩为紧致潜空间，再以可学习逐维 ψ 扰动标准差产生候选异常；解码后只替换相对原输入变化超过动态范围阈值的变量。",
  "technical_innovations": [
    "上下界 triplet-style 潜扰动损失，在潜空间要求异常偏离落在 δmin / δmax 区间（§3.2, Eq.3）。",
    "零维惩罚与 compact-KL 共同控制扰动稀疏性和正常空间紧致性（Eqs.2,4）。",
    "动态范围阈值 patching，按变量级 L2 差异选择是否替换，而不是整样本覆盖（§3.3, Algorithms 1–2）。"
  ],
  "methodology": {
    "architecture": "TCN-VAE 编码正常窗口 → ψ 重标定潜分布噪声 → 解码候选异常 → 按维度差异阈值 patch → 生成增强集 → 训练 detector。",
    "data_processing": "UTS / MTS 窗口；默认 T=200，MTS latent=100、UTS=50；六个多变量与三个单变量基准。",
    "modules": [
      "正常 VAE：z=μ+σ⊙ε，学习正常潜分布和重构。",
      "异常扰动：z̃=μ+ψ⊙σ⊙ε，固定均值并学习逐维扰动。",
      "联合目标：重构、扰动边界、零维扰动、紧致 KL。",
      "Patching：若||Xd−X̃d||₂>τ·range(Xd)则替换整条变量轨迹，否则保留。"
    ],
    "key_formulas": [
      "z=μ+σ⊙ε；z̃=μ+ψ⊙(σ⊙ε)（Eqs.1,3）。",
      "L=αLrecon+βLperturb+γLzero-perturb+ζLcomp-KL（Eq.6）。",
      "维度替换判据||Xd−X̃d||₂>τ(max(Xd)−min(Xd))（§3.3）。"
    ],
    "training": "TCN-VAE 在正常训练窗优化重构、KL 与可学习潜扰动相关损失；默认 Adam 1e-4、1000 epochs，α=1 β=.1 γ=0/.01（UTS/MTS）ζ=.1。",
    "inference": "离线由正常窗采样生成候选并 patch；下游 detector 独立输出异常分数，论文未限定一个统一检测推理公式。",
    "end_to_end": "正常序列 → VAE 潜表征 → 有边界的潜空间扰动 → 解码 → 变量级 patch → 增强 detector 训练。"
  },
  "experimental_evidence": {
    "datasets": [
      "MSL, SMAP, SMD, SWaT, GECCO, SWAN, UCR, Yahoo-A1, KPI。"
    ],
    "baselines": [
      "异常生成 / 增强基线及 CARLA detector 配置；精确完整方法名见论文 Table 1。"
    ],
    "metrics": [
      "ARP（真实异常表征接近性）",
      "EDI（多样性）",
      "下游 F1 / AUPR"
    ],
    "main_results": [
      "ARP / EDI 平均排名 1.78 / 1.22（Table 1）。",
      "GenIAS + CARLA 平均 F1 .557 vs CARLA .509；MSL .579 vs .523、SMAP .620 vs .529、Yahoo .811 vs .749（Table 2）。"
    ],
    "ablations": [
      "有 patch：MSL F1/AUPR .579/.529 vs no-patch .535/.466；SMAP .620/.467 vs .533/.425；Yahoo .811/.794 vs .755/.776（Table 3）。"
    ],
    "robustness_generalization": [
      "9 个基准多场景评测；未验证微服务、业务漂移或跨模态生成。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [
      "结论提出自适应扰动 / patching 和变量间相关性作为后续方向。"
    ],
    "reasoned_inference": [
      "没有故障类型、业务上下文或多模态服务图；潜空间偏离不是故障语义。",
      "ARP 依赖 DeepSVDD 表征及基准异常标签，不能视为生产故障机制验证。"
    ],
    "evidence_gaps": [
      "没有服务系统真实故障注入、Trace / Log 一致性或动态正常状态专门实验。"
    ]
  },
  "research_implications": [
    "作为非 LLM 时序异常合成 baseline，与 LLM 数值改写及系统级故障注入进行区分；潜变量机制可以作为对照而非真实性结论。"
  ],
  "related_papers": [
    "llm-ap-synthetic-augmentation",
    "capmix",
    "carots",
    "synthetic-cloud-microservices"
  ],
  "evidence_references": [
    "PDF §3.1–3.3, Eqs.1–6, Algorithms 1–2：模型与损失。",
    "PDF §4.1–4.8, Tables 1–4：数据、质量、下游结果和消融。",
    "PDF Conclusion：适应与变量相关性方向。"
  ],
  "provenance": {
    "pdf_sha256": "8c3e6800591915b34f00f3c3a20aa82f9050175b978f495f81be2cef847584fb",
    "reading_note_sha256": "dfcd4b417839298c1479e5bbf57e621980a16c7e41b92a1d9e19dd2911791795",
    "knowledge_card_sha256": "05aff1f9ec733a19c4037e61fbe7ace4dcf343cafbf459ca4ced9290bfb702fb",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->

---

<a id="paper-05-modify"></a>
## Paper 05 — MODIFy：扩散增强自适应融合的微服务多模态异常诊断框架

## Knowledge Dossier — A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices

### 1. Basic Information

- **English title**: A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices
- **中文译名**：MODIFy：扩散增强自适应融合的微服务多模态异常诊断框架
- **Authors**: Wujian Zhang, Ruyue Xin, Peng Chen, Xi Li, Ang Bian, Yibin Zhao, Zhiming Zhao
- **Venue / year / CCF**: Journal of Systems and Software 237, 112844 (2026) / 2026 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `modify_jss-2026.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/WuFengXueYing/MODIFy
- **Research area**: 微服务多模态异常检测及服务级根因定位
- **Method tags**: microservices, logs-metrics-traces, diffusion-denoising, adaptive-fusion, GAT, root-cause-localization

### 2. Research Scenario

论文以微服务请求沿调用链传播为场景：网络拥塞可能引发 Trace 重试和延迟突刺，但 Metric 仅轻微变化且仍在 SLO 内，日志只出现警告而非明确错误。单模态因此各自提供不完整证据：Trace 对故障敏感但稀疏、采样缺失、重试噪声高；Metric 连续但语义不明；Log 有事件语义但覆盖有限。研究问题是在这类不完整且噪声异质的日志、指标、Trace 下，如何提升异常检测并把异常定位至服务节点。（PDF §1, p.2, Fig. 1）

输入是按时间窗口对齐后的服务级日志事件强度、指标序列和 Trace 延迟特征，以及历史 Trace 中抽取的服务调用依赖图；输出是样本是否异常及候选根因微服务排名。不是事件级故障生成或 Metric–Trace 合成。

### 3. Research Problem

在 Trace 稀疏 / 噪声、指标异常幅度小且日志无显式错误的微服务环境中，如何融合互补观测并同时检测系统异常、定位服务根因？

### 4. Core Challenges

1. **Trace 噪声 / 缺失**：分布式请求驱动的 Trace 不连续，低流量窗口稀疏，重试造成长尾突刺；直接编码可能把噪声误当故障传播。（§1, §4.1C）
2. **模态采样频率不一致**：Metric 固定周期采集、Trace 毫秒级事件、Log 事件流，需要统一时间参照与聚合。（§4.2）
3. **模态贡献依上下文而变**：简单拼接 / 平均分配权重可能丢失互补关系，无法在特定时间和通道突出关键证据。（作者动机，§1–2）
4. **检测和定位两阶段传递误差**：先检测再另跑 RCA 的管线可能把前段噪声传播至定位，且重复编码原始遥测。（§4.3）

作者将既有工作归为单模态检测 / 定位、图关系分析、多模态融合与联合学习等路线；论文以 Eadro、AMuLSys、MicroIRC 等作基线。论文声称浅层融合和序贯诊断存在限制；其实验比较显示其对 Eadro 等基线有优势，但并未单独证明所有传统方法都存在噪声放大。

### 5. Limitations of Existing Methods

总体是三阶段：

输入日志 / Metric / Trace
→ 单模态编码和时间对齐
→ MSCA-CGFM 自适应多尺度融合 + 调用图 GAT
→ 共享系统表示
→ 异常二分类 + 服务根因排序

Trace 的扩散模块是训练期特征去噪 / 鲁棒表示机制：随机将 Trace 表示加高斯噪声，再学习去噪；不是生成新故障样本，也不是采样出真实 Trace 序列。

### 6. Core Idea

针对 Trace 单独使用训练期扩散式去噪；将三模态以 6 秒窗对齐并经多尺度门控 / SE 融合，结合服务调用 GAT 得系统表示，再共享给检测和根因排序分支。

### 7. Technical Innovations

- DNR-FE：在 Trace 特征随机采样扩散步加噪并用 1D CNN 去噪，旨在提升噪声鲁棒；去除模块平均 F1 / HR@1 / HR@5 降约 3.5% / 3.1% / 6.2%（§5.7）。
- MSCA-CGFM：3×3、5×5 depthwise conv 多尺度分支 + gate + SE 通道重标定；消融去掉模块下降最大（Fig.5）。
- 图注意力后的共享表示联合检测 / 定位；减少重复编码，联合监督效果由整体对比支持，但无法单独证明所有串行流程均有噪声放大。

### 8. Methodology

#### A. 单模态特征

**Log**：Drain3 将非结构化日志解析成模板；按窗口统计模板事件序列，用 Hawkes 自激点过程得到每类模板的强度向量。事件 l 的强度形式为 λ*l(t)=μl(t)+Σ(τ<t)φl(t−τ)，激发核 φl(·)=αlβ exp(−βt)，t>0。μ 初始化为 0.2 并通过最大似然学习；向量 Λ 经全连接层映射为日志表示。意图是捕捉错误日志不明显时事件频率 / 触发模式变化。（§4.1A, Eq. 1）

**Metric**：对每个服务节点的指标作 Z-score 标准化，切成 K 个连续固定窗口，形成 X∈R^(K×N×T×M)；Transformer encoder 用多头注意力抽取全局时间依赖并输出 metric embedding。（§4.1B）

**Trace**：按 span 的服务 ID、父子关系、时间戳和 duration 提取调用链 / 拓扑；按服务在固定窗内平均 latency 构造序列。给定原特征 Fτ0，按随机扩散步 t 加噪：

Fτ = √αt Fτ0 + √(1−αt) ε，ε~N(0,I)。

累积保留系数 αt 控制原始信息和噪声比例；堆叠 1D 卷积 + ReLU 去噪网络学习恢复特征，然后 Transformer 编码器抽取时间表示。（§4.1C, Eq. 2, Fig. 3）作者试过把扩散用于 Log / Metric，效果不理想；给出的解释是离散文本与稳定 Metric 的噪声分布不适合该扰动，而 Trace latency 的外界波动更适合这一处理。（§4.1C）

#### B. 对齐与 MSCA-CGFM

先将不同模态时间戳映射到统一时间轴，用固定 6 秒窗口同步：Trace span 聚合为服务平均延迟，Metric 重采样，Log 按窗形成 Hawkes 强度向量。三种 embedding 沿通道拼接；另从 Trace 父子 span 构建有向服务调用图 G=(V,E)。（§4.2）

增强 CGLU 把拼接表示投影并切为 H1 特征支路和 H2 门控支路：

[H1,H2] = split(Wf[FL || FM || FT])。

H1 并行通过 3×3 与 5×5 depthwise separable convolution，按可学习 w1+w2=1 加权：

H1dw = w1·DWConv3×3(H1) + w2·DWConv5×5(H1)。

再用 sigmoid(H2) 门控，随后 SE 模块以全局平均池化、两层全连接与 sigmoid 产生通道权重 sc，并逐通道重标定：

sc = σ(W2·ReLU(W1·(1/N)Σi hi))；
HS = SE(H1dw ⊙ σ(H2))。

输入是每服务的三模态嵌入，输出为适配上下文的融合表示。多尺度捕捉局部与较宽邻域，SE 调节通道权重；其效果在消融中评估。（§4.2, Eqs. 3–6, Fig. 4）

#### C. 调用图 GAT 与联合检测 / 定位

融合节点特征放入调用图，经 GATv2Conv 学习服务间依赖注意力；多头结果在通道方向 max-pooling，随后全局 attention 聚合系统状态 HG=Σi αi hi。（§4.2, Eqs. 7–8）

共享 HG 输入两个监督分支：异常检测二分类器输出正常 / 异常概率；根因定位分支对服务节点输出 softmax 分布并排序。联合损失为 L=αL1+(1−α)L2，其中 L1 是二分类交叉熵，L2 是根因服务交叉熵；实验默认 α=.5。训练数据有系统异常标签与 root-service 标签。推理先给系统状态异常概率，再输出服务候选根因排名；正常样本不应解释为已确认故障。（§4.3, Eqs. 9–11）

#### D. 训练与预处理配置

在 SocialNetwork 与 TrainTicket 的处理后多模态数据上按时间段 7:3 切分训练 / 测试，再独立滑窗，窗口为 6 秒。使用 Adam，初始学习率 .001、batch 256、70 epochs；Transformer 两层、4 头；各模态模型设为轻量单层；GAT 隐藏维度 128、4 头；扩散 100 步、噪声范围 1e-5–1e-2。（§5.1, §5.3）

### 9. Experimental Evidence

- **数据**：SocialNetwork（21 服务，98,510 窗口）；TrainTicket（41 服务，445,584 窗口）。每者含 CPU hog、network delay、network loss；两数据集服务数、样本规模不同。Metric 每服务 7 个维度：CPU 三项、内存两项、接收 / 发送字节。日志异常模板 SN 为 6 类已知 + 1 未知，TT 为 59 类已知 + 1 未知。预处理后 SN 有 119,664 metrics、94,365 logs、48,296 traces；TT 有 2,007,801 metrics、111,275 logs、126,384 traces。（§5.1, Table 2）
- **Baselines**：DeepLog、LogRobust、TraceAnomaly、MultimodalTrace、DeepTraLog、TraceGra、AMuLSys、Eadro；定位另含 CloudRanger、MonitorRank、DyCause、DejaVu、MicroIRC。（§5.2）
- **指标**：检测 Precision / Recall / F1；定位 HR@1/3/5、NDCG@3/5。（§5.4）
- **主结果**：F1：SN .925、TT .841，平均 .883；Eadro 分别 .904 / .834。HR@1：SN .878、TT .816，平均 .847；Eadro .810 / .757。NDCG@5 为 .921 / .917。（Tables 4–5）
- **消融**：去掉任何模态，SN HR@1 下降约 8.9%–19.2%、F1 下降 10.1%–14.0%；TT HR@1 降 10.1%–19.3%、F1 降 9.3%–14.7%，去 Trace 影响最大。移除 Trace diffusion 平均 F1 降 3.5%、HR@1 降 3.1%、HR@5 降 6.2%；去多尺度通道门控损失最大。噪声注入测试中 MODIFy 相比 Eadro 下降较缓；Fig. 8 支持测试噪声鲁棒性，但不等于对业务状态漂移稳健。（§5.7, Fig. 5; §5.12, Fig. 8）
- **显著性 / 成本**：对 Eadro 的 10 次配对检验，F1 与 HR@1 的多个差异报告 p<.05。推理 1.578 ms/sample（SN）、1.872 ms/sample（TT）；完整训练约 40 分钟 / 3 小时，GPU memory .899 / 2.011GB。（§5.10–5.11, Tables 6–7）

### 10. Limitations

#### A. Author-stated limitations

- 固定 / 已知依赖拓扑；两公开数据集；依赖监督故障类型；服务级定位，不支持实例 / 容器；未观测基础设施异常可能漏检；benchmarks 多为单一主因；未来考虑动态图、部署效率和 LLM 解释（§6, pp.18–20）。

#### B. Reasoned inference

- 6 秒窗口和固定拓扑对其他采样 / 动态服务环境的外推仍待验证。
- 模型融合实测模态而非联合生成；扩散是降噪训练机制，不是异常样本生成。

#### C. Evidence gaps

- 没有业务负载 / 发布上下文输入或正常高峰困难负样本专项评估。
- 多根因标注及动态拓扑实验不足。

### 11. Research Implications

**本知识库分析**：用于多模态诊断对照；其对 Trace 降噪和服务级图融合可以作为数据生成验证的下游组件，但论文自身不生成故障数据。

### 12. Related Papers

MODIFy 直接对比 AMuLSys，但本知识库因全文未获取不复述其方法；`AIOpsLab`提供可运行注入环境；`CAROTS`使用因果图生成伪异常。

### 13. Evidence References

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

---

<a id="paper-06-aiopslab"></a>
## Paper 06 — AIOpsLab：用于自主云运维 Agent 评估的整体框架

## Knowledge Dossier — AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds

### 1. Basic Information

- **English title**: AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds
- **中文译名**：AIOpsLab：用于自主云运维 Agent 评估的整体框架
- **Authors**: Yinfang Chen, Manish Shetty, Gagan Somashekar, Minghua Ma, Yogesh Simmhan, Jonathan Mace, Chetan Bansal, Rujia Wang, Saravan Rajmohan
- **Venue / year / CCF**: MLSys 2025 / 2025 / 本专题不标注 CCF 等级
- **CCF provenance**：未在本次专题确认 CCF 等级；期刊与预印本按各自出版类型记录。
- **Original PDF**: `aiopslab_mlsys2025.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://aka.ms/aiopslab-repo
- **Research area**: 运行时云运维 Agent 基准与故障注入测试床
- **Method tags**: AIOps, agent-evaluation, fault-injection, live-microservices, metrics-logs-traces, benchmark

### 2. Research Scenario

作者关注自主云运维 Agent 的系统级评估：真实生产事故多样且难重放，离线问答无法测试 Agent 对运行系统观测、工具调用、诊断和缓解的完整能力。框架在可部署微服务平台中注入故障、运行负载并提供 Metrics、Logs、Traces、配置 / 拓扑等工具；Agent 接收任务描述后调查和操作环境，评估器对照内部故障配置与任务期望判断结果。（PDF §§1–2, pp.1–3）

测试床含 DeathStarBench HotelReservation、SocialNetwork、OpenTelemetry Astronomy Shop 和自定义 TiDB 场景。问题表示 P=<T,C,S>，其中任务 T 配有上下文 C=<E,I>（环境、相关信息）；任务层次覆盖 detection、localization、RCA、mitigation。输入为任务及 Agent 可访问的 API / 环境信息，交互过程中 Agent 可查询 telemetry、执行动作；输出可能是检测 / 定位 / 根因结论或缓解行动。

### 3. Research Problem

如何建立可重放、可计分且能覆盖 Agent–工具–云环境闭环的 AIOps 评估，而不是只在静态问答中评估根因回答？

### 4. Core Challenges

1. **离线数据缺乏真实工具反馈**：静态 benchmark 无法体现调用链、运行状态和干预后的效果。
2. **故障表象与根因差异**：CPU / 网络等资源症状可直接观测，而配置错误、代码问题等功能故障可能在传播后才产生下游异常；只评表面异常无法考察诊断深度。（§2）
3. **Agent 评估需要统一接口和可复现真值**：若不同环境工具不一致、故障标签不明确，Agent 之间比较难复现。
4. **正常状态识别同样重要**：Agent 不能把每个任务都强行诊断成故障；论文包含 no-op / 正常任务并报告误报。（§3.6.4）

### 5. Limitations of Existing Methods

#### A. Live cloud testbed and fault generation

框架可启动微服务基准、工作负载生成器和故障注入器。故障分 symptomatic 与 functional 两大类：前者包括 CPU / 资源 / 网络压力或服务崩溃；后者可由配置错误、认证 / 权限、代码 bug 等机制触发，更要求沿服务交互诊断和缓解。任务配置包含目标、故障类型、时间窗口及答案标签；框架也支持自定义故障。（PDF §§2.1–2.3, Table 1）

#### B. Agent–Cloud Interface

Orchestrator 通过标准 API 向 Agent 暴露任务、系统信息和行动接口；Agent 可查询 Prometheus 指标、Jaeger trace、日志链路（kubectl / Filebeat / Logstash）、代码 / 配置和集群信息。返回的 Observation 是部署系统中的实际遥测或工具结果，而非由 LLM 生成的对话片段。任务执行轨迹被记录供评价与复盘。（§2.4, Fig. 2）

#### C. Ground truth and evaluation

框架内部知道工作负载 / 故障注入配置、作用对象和期望动作，可将其作为隐藏真值；Agent 接口只开放任务完成所需信息。检测、定位、RCA、mitigation 有各自任务级判断及完成条件。实验考虑不同语言模型与 Agent 交互模式，评估是否成功处理代表性问题。（§2.5, §3）

**重要版本区别**：MLSys 正式版概览提到框架包含 100 个问题，但受评测成本影响，实验只选取 48 个代表性问题；不要将早期 arXiv 版本的评测口径直接套用到正式版。（§3.1）

### 6. Core Idea

通过微服务测试床和可控故障 / 工作负载生成环境数据，再用统一 Agent–Cloud API、遥测工具和隐藏配置 oracle 执行 / 评分任务。

### 7. Technical Innovations

- 统一的 Agent–Cloud Interface：任务、信息、工具观察和动作的 API。
- 将 symptomatic 资源故障和 functional 配置 / 代码类故障纳入问题设计。
- 组合检测 / 定位 / RCA / mitigation 任务和运行轨迹记录；正式版框架 100 问题、受评估成本限制实验选 48。

### 8. Methodology

典型执行过程：

任务说明 → Agent 查询环境 / 指标 / 日志 / Trace → Orchestrator 执行工具并返回观察 → Agent 继续调查或执行运维动作 → 输出答案 / 缓解 → 评估器依据故障真值和任务完成条件评分。

框架中的工作负载和真实故障动作由实验控制器确定，不是 LLM 在自然语言里虚构故障样本。LLM 负责推理、选择工具和行动；具体是否有显式 Planner / long-term memory 取决于被测 Agent 配置，不能当成 AIOpsLab 固有模块。

### 9. Experimental Evidence

- **系统 / 数据**：多个真实部署的微服务基准和可配置问题；观测包括 metrics、logs、traces、配置 / 集群信息。框架设计支持故障生成、遥测收集与交互轨迹记录。（§2.1–2.5）
- **评估范围**：100 问题框架中选 48 个代表场景运行实验；比较 GPT-4-W-Shell、GPT-3.5-W-Shell、ReAct、Flash 等 Agent / 交互基线。（§3.1–3.4）
- **正式版表 3**：所报告 all-problem accuracy 为 GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%。数字对应论文定义的问题完成准确率，不等同异常检测器 F1。（Table 3）
- **正常 no-op 任务**：在两个要求不采取故障操作的检测任务中，只有 GPT-4-W-Shell 识别正常工作负载；其他 Agent 将正常状态误报为异常。（§3.6.4, p.9）
- **支持范围**：说明 live testbed 能测端到端 Agent 运维交互，并暴露正常 / 故障判断难点；不证明生成的故障覆盖生产真实分布，也不评价某种检测模型的数据增强收益。

### 10. Limitations

#### A. Author-stated limitations

- 论文未以独立小节列出可明确归属的作者局限；相关适用边界在方法 / 实验范围中说明。

#### B. Reasoned inference

- 代表性故障和应用有限；运行时注入遥测是真实环境观测，但不覆盖全部生产故障分布。
- 问题完成率不直接测量 Metric / Trace 合成或 anomaly detector 增益。

#### C. Evidence gaps

- 正常业务高峰、扩缩容、发布与真实故障并发的困难评估任务仍需专门覆盖。

### 11. Research Implications

**本知识库分析**：是验证真实微服务运行中 Agent / 诊断的可复现环境参照，不应与离线 LLM 数值生成器混为一谈。

### 12. Related Papers

与 `Synthetic Time Series`互补，后者聚焦采集数据集；`TraceLLM`生成离线 DAG；TSAD `CAPMix`评测 KPI 检测器增强。

### 13. Evidence References

| 论断 | 原文定位 |
| --- | --- |
| 任务表示、系统组成和微服务环境 | PDF §§2.1–2.3, pp.2–4, Table 1 |
| Agent–Cloud API、工具与遥测 | PDF §2.4, pp.4–5, Fig. 2 |
| 评分和实验设置 | PDF §§2.5, 3.1–3.5 |
| 正式版 48 场景评估和 Table 3 | PDF §3, Table 3 |
| no-op / 正常工作负载误报 | PDF §3.6.4, p.9 |
| 框架并非样本合成器 | 论文任务定义与 §2；本知识库分析 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "aiopslab",
  "title_en": "AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds",
  "title_zh": "AIOpsLab：用于自主云运维 Agent 评估的整体框架",
  "authors": [
    "Yinfang Chen",
    "Manish Shetty",
    "Gagan Somashekar",
    "Minghua Ma",
    "Yogesh Simmhan",
    "Jonathan Mace",
    "Chetan Bansal",
    "Rujia Wang",
    "Saravan Rajmohan"
  ],
  "year": 2025,
  "venue": "MLSys 2025",
  "ccf_level": null,
  "ccf_provenance": "本专题不核定或标注 CCF 等级；按已核验的出版类型与来源记录。",
  "pdf_path": "sources/papers/llm-microservice-anomaly-generation/aiopslab_mlsys2025.pdf",
  "reading_note_path": "papers/aiops/aiopslab/notes.md",
  "knowledge_card_path": "papers/aiops/aiopslab/knowledge-card.md",
  "code_url": "https://aka.ms/aiopslab-repo",
  "research_area": "运行时云运维 Agent 基准与故障注入测试床",
  "method_tags": [
    "AIOps",
    "agent-evaluation",
    "fault-injection",
    "live-microservices",
    "metrics-logs-traces",
    "benchmark"
  ],
  "research_scenario": "部署中的微服务云环境评估 Agent 对检测、定位、RCA、缓解等任务的调查与动作；系统向 Agent 暴露真实工具查询结果和运行遥测。",
  "research_problem": "如何建立可重放、可计分且能覆盖 Agent–工具–云环境闭环的 AIOps 评估，而不是只在静态问答中评估根因回答？",
  "core_challenges": [
    "真实事故难复现 / 有可靠真值（§2）。",
    "症状型和功能型故障需要不同诊断深度。",
    "Agent 必须交互取证，且 benchmark 要评价完成状态与过程。",
    "正常 no-op 也需要正确判为无需故障操作（§3.6.4）。"
  ],
  "existing_method_limits": [
    "静态日志 / 问答缺少服务环境、工具反馈和操作结果；普通准确率不反映 Agent 的工具交互。此为论文动机，不代表所有既有基准缺失所有能力。"
  ],
  "core_idea": "通过微服务测试床和可控故障 / 工作负载生成环境数据，再用统一 Agent–Cloud API、遥测工具和隐藏配置 oracle 执行 / 评分任务。",
  "technical_innovations": [
    "统一的 Agent–Cloud Interface：任务、信息、工具观察和动作的 API。",
    "将 symptomatic 资源故障和 functional 配置 / 代码类故障纳入问题设计。",
    "组合检测 / 定位 / RCA / mitigation 任务和运行轨迹记录；正式版框架 100 问题、受评估成本限制实验选 48。"
  ],
  "methodology": {
    "architecture": "基准微服务应用 + 负载生成器 + 故障控制器 + Orchestrator/API + 指标 / 日志 / Trace / 配置工具 + 隐藏故障真值和评分器。",
    "data_processing": "使用 DeathStarBench HotelReservation / SocialNetwork、OpenTelemetry Astronomy Shop、自定义 TiDB 场景；Prometheus metrics、Jaeger traces、kubectl / Filebeat / Logstash logs，并提供代码 / 配置 / 集群信息。",
    "modules": [
      "问题描述 P=<T,C,S>，上下文 C=<E,I>。",
      "Orchestrator 管理服务部署、负载 / 故障、Agent API 和观察返回。",
      "故障器支持资源 / 网络症状故障和配置 / 认证 / 代码功能故障。",
      "Oracle 根据隐藏注入配置与任务完成条件评估 Agent 结果并记录轨迹。"
    ],
    "key_formulas": [
      "Problem tuple P=<T,C,S>; C=<E,I> 为任务、环境 / 信息上下文的表示（§2）。"
    ],
    "training": "AIOpsLab 是评测框架，不训练一个统一的 Agent；论文替换不同 LLM / workflow 配置作实验。",
    "inference": "Agent 接收任务，循环查询遥测 / 系统信息、观察返回、继续分析或缓解，输出结果。不同 Agent 的规划 / memory 并非框架固有能力。",
    "end_to_end": "服务部署 / 工作负载 → 控制器注入真实故障 → Agent 通过工具调查 → 执行动作 / 输出诊断 → 隐藏 oracle 自动评分。"
  },
  "experimental_evidence": {
    "datasets": [
      "HotelReservation / SocialNetwork (DeathStarBench), Astronomy Shop, custom TiDB; 100 benchmark problems, 48 selected for formal evaluation."
    ],
    "baselines": [
      "GPT-4-W-Shell",
      "GPT-3.5-W-Shell",
      "ReAct",
      "Flash"
    ],
    "metrics": [
      "任务完成 accuracy / success rates；不是 detector F1。"
    ],
    "main_results": [
      "正式版 Table 3 all-problem accuracy：GPT-4-W-Shell 49.15%、GPT-3.5-W-Shell 15.25%、ReAct 55.93%、Flash 59.32%。",
      "两个 no-op 检测问题中，只有 GPT-4-W-Shell 识别正常工作负载；其余 Agent 有误报（§3.6.4, p.9）。"
    ],
    "ablations": [
      "比较不同 Agent / 模型配置和问题类别；核心是系统性 benchmark 评估，不是异常生成器消融。"
    ],
    "robustness_generalization": [
      "覆盖若干微服务应用与故障类别；不代表生产事故分布、Agent 跨云泛化或生成样本真实性。"
    ],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [],
    "reasoned_inference": [
      "代表性故障和应用有限；运行时注入遥测是真实环境观测，但不覆盖全部生产故障分布。",
      "问题完成率不直接测量 Metric / Trace 合成或 anomaly detector 增益。"
    ],
    "evidence_gaps": [
      "正常业务高峰、扩缩容、发布与真实故障并发的困难评估任务仍需专门覆盖。"
    ]
  },
  "research_implications": [
    "可作为生成异常数据之后的运行时因果反馈 / 检测环境，但要额外构造无故障正常波动和多因共现测试（本知识库分析）。"
  ],
  "related_papers": [
    "synthetic-cloud-microservices",
    "tracellm",
    "modify",
    "capmix"
  ],
  "evidence_references": [
    "PDF §§2.1–2.5, pp.2–5, Fig.2：环境 / 故障 / API / 评估器。",
    "PDF §3.1, §3.6.4, Table 3, p.9：48 场景评测和 no-op。"
  ],
  "provenance": {
    "pdf_sha256": "ea8af2dc2bb1409b8d29ef0f571a3e4a22806cf32c81934367695da277b7d9f5",
    "reading_note_sha256": "e299a9dc92b108c6f17e376a48d1ad464cc02cee6b7ce412df15bb397e9d345e",
    "knowledge_card_sha256": "4362010b291bc2b67b5912820158d55fb4aa8a6abfdeb1b44ce8e635b5993e7e",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->

---


## Appendix — AMulSys full text pending

Anomaly Detection for Microservice System via Augmented Multimodal Data and Hybrid Graph Representations. Information Fusion 118 (2025), article 103017. DOI: https://doi.org/10.1016/j.inffus.2025.103017.

The publisher route currently requires purchase and direct PDF access returned 403. No legal full-text copy was verified, so this paper has no completed reading note, card, or method dossier. The title / abstract preview is not used to infer the method. See the source download report in the knowledge base for details.
