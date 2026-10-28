# Knowledge Dossier — Large Language Models as Realistic Microservice Trace Generators

## 1. Basic Information

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

## 2. Research Scenario

研究场景是微服务系统的分布式调用 Trace。单条样本被表示为有向无环调用图（DAG）：边关联源服务、目标服务、通信类型、开始/结束时间等属性，并保留层级 / 调用关系。作者使用 Alibaba 2022 微服务调用图语料，约 136 万条图记录、约 11 亿 token。生成器的输入是自然语言指令或结构条件（例如图深度、边数、稀有通信、延迟条件），输出是一个序列化的新调用图。目标用途是补充 Trace 数据、下游任务训练及在指定结构条件下生成数据，而不是在线检测或根因诊断。（PDF pp.1–3, §2–3）

论文把“真实”主要操作化为结构约束、字段分布、调用模式及下游任务可用性。它没有把异常根因作为生成标签，也没有生成与 Trace 同步的 Metric / Log。

## 3. Research Problem

在真实调用图量大、层级深且必须满足 DAG / 边数 / 深度条件时，如何生成结构有效、字段统计合理且对特定下游任务有用的微服务调用图？

## 4. Core Challenges

**研究问题**：在真实调用图数据量大、结构化且需要满足 DAG 和调用条件的情况下，如何利用预训练语言模型生成字段与关系都有效、可按条件控制、并对下游任务仍有用的微服务 Trace？

1. **图结构约束难**：自由文本语言模型容易违反边数、深度、调用父子关系、起止时间或 DAG 结构。无约束生成导致无法直接被 Trace 工具或下游任务使用。（作者动机，§1–2）
2. **长结构依赖难**：调用图可能包含多层、多个同层子调用；平铺文本容易在长输出中丢失全局条件或重复节点。普通逐 token 生成没有明确的“逐调用层生成”机制。（§3.2）
3. **条件可控性与自然度冲突**：只按观测频率拟合容易生成常见图，却难以遵循稀有通信类型、延迟或指定规模条件。硬规则控制又可能造成不自然的组合。（§3.3–3.4）
4. **统计相似不等于下游有效**：仅报告边 / 节点频率无法说明合成 Trace 是否保留任务相关结构；因此作者还测试生成数据训练、真实数据测试的迁移设置。（§4）

## 5. Limitations of Existing Methods

作者比较了概率图 / 规则方法、表格数据生成模型（如 TVAE、GReaT）和基础 LLM。传统概率方法对结构组合和长尾条件的表达受限；一般表格生成器关注行级字段分布，未必保留调用图递归依赖；直接提示通用 LLM 则可能不遵守图约束。核心思路是把 Trace 视作一种有层次的结构化语言：先把图字段文本化，再把图分解为按父节点组织的层，模型每轮接收当前条件、生成当前层边及下一层条件，逐层扩大图；指令微调显式教模型推算剩余边数、深度等约束。

## 6. Core Idea

将调用图转为层级文本，按父节点 / 调用层递归生成边；把边数、深度等约束状态显式纳入条件和指令微调，使模型既学习领域字段又可控地扩展 DAG。

## 7. Technical Innovations

- 递归 DAG 文本生成：每轮生成一层边和下一层条件，针对长结构约束；相较单次扁平输出，困难边数 / 深度下有效率更高（§3.2, Eq.1; §4.1）。
- 约束推理指令微调：将剩余边数 / 深度等中间算术状态纳入序列，训练损失不预测初始条件文本；相较仅递归消融，报告约 23%–36%条件准确率提升（§3.3–4.1）。
- 领域继续预训练 + LoRA：在约 1.36M 图 / 1.1B tokens 上学习微服务字段分布；这是领域适配基础，不等于故障机制学习（§3.1）。

## 8. Methodology

### A. 表示与领域预训练

每条调用边被转换为文本字段。论文随机打乱字段次序，降低模型将固定字段位置当成语义的风险。图级条件包括深度、边数、延迟等统计属性；训练时对条件顺序打乱并随机丢弃部分条件，使模型能适应不同条件组合。（§3.1）

作者用 Llama-2 7B 做领域继续预训练，并用 LoRA 进行参数高效适配。领域语料为 Alibaba 微服务调用图，约 1.36M 图、1.1B tokens。预训练让模型学习服务名、调用关系和属性值的领域语言分布；这一步本身不教故障因果知识。（§3.1）

### B. 递归分层生成

给定父服务或当前图层，模型在同一父节点下生成一组边；每条边包含服务标识、通信类型、时间 / 延迟字段。下一层待生成条件随后传给下一次调用，直到达到深度或边数条件。概率分解写为：

P(t | c) = ∏(k=1…l) P(c^(k+1), t^k | c^k)

其中 t^k 是第 k 层生成的边文本，c^k 是本层条件，c^(k+1) 是递归传下去的下一层条件。递归拆解把“整个长图一次生成”改成“按调用层逐步生成”，降低全局约束丢失风险。（§3.2, Eq. 1）

### C. 指令微调与约束推理

监督微调样本包含自然语言约束和目标 Trace 层。训练损失不对初始条件文本计算，而对模型应生成的图层和下一步条件计算。作者还在输入/输出中加入中间的算术、逻辑步骤，例如当前已用边数与剩余边数、深度状态，让模型在生成时跟踪约束，而不只是模仿字段表面格式。（§3.3, Fig. 2）

推理可指定边数、深度、通信类型比例或高延迟条件。稀有通信被定义为频次低于 10% 的类型；高延迟条件按真实数据第 90 百分位阈值设定。模型据此输出 Trace DAG。解析失败或约束违例的过滤细节并非所有部署场景都明确规定，使用者需要自行验证生成图。

### D. 训练与端到端流程

1. 从真实 Trace 提取图边字段与图级统计条件。
2. 对字段文本化并扰动顺序 / 条件可见性，形成领域语料和指令数据。
3. 在 Llama-2 7B 上做领域继续预训练，再做 LoRA 指令微调。
4. 推理时给出条件，按图层递归生成。
5. 解析输出并检查 DAG / 条件满足度；将图用于结构分布评估或下游任务。

检测器不是 TraceLLM 的组成部分；论文的下游任务是外部验证，不应把它描述成端到端异常检测器。（§3–4）

## 9. Experimental Evidence

- **数据**：Alibaba 2022 微服务 Trace 图；真实样本另用于合成训练 / 真实测试的下游实验。
- **比较方法**：概率生成、TVAE、GReaT、基础 Llama / 指令基线、递归生成和有无指令微调的消融。
- **结构有效性**：检查有效 DAG、指定深度和边数、边属性 / 时间约束。递归+指令微调在大图条件下显著优于基线：边数超过 15 时，基线有效率低于 25%；深度超过 4 时接近 0。递归和指令微调在这些困难范围可提高约 30% / 35%（论文分别报告的条件有效率增益），指令微调相对仅递归再提升约 23%–36%；温度 1 下性能约提升 10%。（§4.1, Fig. 3–4；指标描述按论文报告）
- **统计分布**：热门调用 KL 约为 TraceLLM 0.16、GReaT 0.11、概率方法 3.84、TVAE 0.74，说明 TraceLLM 大幅优于概率 / TVAE，但不是该项最优。热门调用 Top-K 准确率在 K≤50 时超过 90%，K=500 时约 65%。（§4.2, Fig. 5）
- **下游迁移**：用 5K 合成调用图训练、2K 真实图测试。FIRM SVM 的准确率距真实数据训练约 1.5 个百分点；对照生成方法的差距报告为 6–81 个百分点。该结果支持 Trace 在特定调用图预测任务上的效用，不证明异常根因真实性。（§4.3, Fig. 6）
- **条件遵循 / 补全**：稀有通信预测约 76.8%，高于 Llama-2 基线 60.6% 和 Llama-3.1 405B ICL 45.6%；缺失字段补全准确率超过 70%，相对基线提高约 30–40 个百分点。（§4.4–4.5, Fig. 7）
- **真实性边界**：实验验证结构、统计及选定下游任务；没有真实故障注入标签、与 Metric / Log 的同步生成或面向故障检测收益的实验。

## 10. Limitations

### A. Author-stated limitations

- 论文未以独立小节列出可明确归属的作者局限；相关适用边界在方法 / 实验范围中说明。

### B. Reasoned inference

- 训练语料来自单一 Alibaba 系统，可能有服务 / 拓扑域偏移。
- 结构与统计相似不证明故障因果机制真实；稀有通信或高延迟条件不等于故障注入。

### C. Evidence gaps

- 没有故障根因语义标签或真实异常检测收益实验。
- 未生成与 Metric / Log 同步的多模态事件，也没有跨模态因果一致性检验。

## 11. Research Implications

**本知识库分析**：用于结构化 Trace 生成基线；与真实故障注入器联合时，需补充故障根因、Metric / Trace / Log 一致性和真实数据收益验证。

## 12. Related Papers

同专题 `Synthetic Time Series` 和 `AIOpsLab`提供运行系统 / 故障注入对照；`LLM-AP`生成数值窗口。TSAD `CAPMix`处理 KPI 伪异常。

## 13. Evidence References

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
