# Knowledge Dossier — LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation

## 1. Basic Information

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

## 2. Research Scenario

作者研究真实单变量时间序列异常检测中标注异常不足、类型长尾，以及已有合成增强可能产生失真数值窗口的问题。输入为一维连续值序列、已标注的异常区间和检测模型；输出为通过验证的额外异常窗口及增强后的训练集，最终任务是检验增强是否提升检测器 F1。NAB 的 47 条真实时间序列涵盖五类领域；不是微服务专用 KPI，也不含调用 Trace、日志和根因标签。（PDF §§1–3, §4.1）

### 核心挑战

1. **异常类型要贴合数据**：固定注入可能产生数据里没有的异常形态。LLM-AP 先从已有标注归纳 6 种异常子类型，仅生成数据中实际出现的类型。（§3.2）
2. **语言模型容易返回不可解析 / 长度不符的数据**：结构化提示和 JSON 输出仍不能保证数值可靠，需要长度修复及非有限值检查。（§3.3.1）
3. **异常要有可检测信号，又不能脱离上下文**：过弱变化没有检测意义，过强或局部结构不匹配的序列不真实。作者使用距离上、下界和类型规则筛选。（§3.3.2–3.3.5）
4. **检测指标提升不能只来自合成标签数量**：需要对比增强前后、验证 / 未验证样本，以及多种检测器。（§4）

## 3. Research Problem

在异常稀少的单变量真实序列中，如何依据本序列已有异常类型生成长度、形态和变化强度都合理的数值异常窗口，并通过检测结果验证其增益？

## 4. Core Challenges

作者认为传统规则 / 统计扰动难以构造多样且与原始上下文相容的异常，而未约束的 LLM 输出也可能有长度、数值和形态缺陷。核心思想是让 LLM 负责“依据上下文改写数值”，由一套可重复的自动筛选管线负责“判断是否保留”。LLM 不被微调，只以 zero-shot / few-shot 方式接收任务说明、正常样本与少量异常示例。

## 5. Limitations of Existing Methods

### A. 异常类型与窗口构造

预处理器沿每个异常时间点寻找一个最近的滑动窗口，避免一个异常点因半径扩张而重复标出大量窗口。作者按启发式阈值先识别异常子类型，若阈值不稳定则用归一化特征分数回退。六类包括 local spike、level shift、variance change、trend change、gradual drift、slow degradation。每一类只在当前序列确有实例时进入生成；提示样例最多含 2 个正常窗口和最多 2 个异常窗口，每个窗口最多 40 个点。数据集 / 文件名用于自动给出领域背景，而非人工逐序列设计提示。（§3.1–3.2）

### B. LLM 数值窗口生成

将窗口转为结构化文本 / JSON 形式，提示模型保留正常上下文并按目标类型修改可变数值和趋势。候选模型是冻结的 GPT-3.5-turbo 与 GPT-4o，做零样本 / 少样本提示，不进行针对数据集的微调；模型输出转回数值窗口。论文给出 Append（追加生成样本）与 Replace（替换选定原始异常样本）的增强方式。（§3.2–3.3）

### C. 五阶段样本验证

1. **格式与长度**：解析 JSON 和期望字段；若长度偏差不超过 5%，按线性插值修正；NaN / Inf 或严重长度不匹配则拒绝。
2. **RelDTW 距离下限**：根据相对动态时间规整距离判断是否有足够变化；小于 0.05 视为信息不足。
3. **异常存在性**：点异常检查 z-score 最大值是否大于 3，且 spike 数在 1–3；集体异常用 CUSUM，阈值 h=4σ。
4. **子类型匹配**：利用转折尖锐度、变化后稳定度、方差比例、单调性等形态特征，和 200 对正常窗口校准的阈值比较，确认候选符合目标类型（Table 2）。
5. **真实性距离上限**：RelDTW 大于 10 则视为偏离过大并丢弃。

任一检查失败时，Self-Refine 将错误代码、失败指标和目标类型反馈给 LLM，最多重试 3 次；某类型连续 15 次生成失败则停止该类型。RelDTW 在此被用作过滤信号；它不是生成数据与真实异常分布一致的完整度量。（§3.3, Eqs. 1–12, Table 2）

### D. 训练 / 推理端到端

1. 解析训练序列中的异常点和子类型。
2. 选取正常 / 异常上下文窗口并形成结构化提示。
3. GPT 返回新数值序列。
4. 依序做解析、距离、异常性、子类型、距离上限检查；必要时反馈重试。
5. 将保留样本追加或替换到数据集。
6. 训练 TimesNet、PatchTST、Transformer 或 Autoformer 等检测器；原文未规定独立的新检测模型。

推理阶段检测器仍在新测试窗口上输出异常分数 / 标签；生成器不参与在线推理，除非后续工作另行设计。

## 6. Core Idea

让冻结 GPT 按结构化提示改写数值窗口，再由格式、异常存在、类型匹配、相似距离等规则筛选；模型生成能力和可信度验证明确分开。

## 7. Technical Innovations

- 从标注窗口识别六类异常并仅生成已出现类型，降低任意类型迁移；证据为类型构造流程，不代表类别识别完美（§3.1–3.2）。
- 五阶段验证：格式 / 长度、RelDTW 下界、z-score / CUSUM 异常性、形态子类型、RelDTW 上界；Table 8 显示验证样本优于未验证样本。
- Self-Refine：反馈具体失败指标最多三轮，连续 15 次失败时停止该类型；提升通过率，但不能证明分布真实性。

## 8. Methodology

- **数据 / Baseline**：NAB 47 条真实数据，45 条可成功生成，2 条失败（AWS EC2 disk writes 数据大多为零值突发；keystroke 序列近似二元）。对比无增强、jitter / scaling 和未验证合成样本；检测器 TimesNet、PatchTST、Transformer、Autoformer。（§4.1–4.3）
- **设置**：两 GPT 版本、temperature 0.5 / 1.0，Append / Replace。GPT-3.5 通过验证 1541 个窗口，GPT-4o 1604 个；目标异常占比 10%。（§4.2）
- **结果**：TimesNet 上 GPT-4o、temperature=1、Append 得到 F1 0.7238±0.001，对照 0.6893±0.002；PatchTST 最佳 0.7024，对照 0.6929；Transformer 最佳 0.6948，对照 0.6858。Autoformer 反而全部低于其无增强对照，例如 GPT-3.5、temperature=1、Replace 为 0.2753 对 0.6071。（Table 8）
- **验证消融**：对 TimesNet / PatchTST / Transformer，验证后样本在所有比较配置中优于未验证样本；未验证合成样本的收益不高于基线。Autoformer 是例外，所有增强配置均降低性能。（Table 8）
- **支持范围**：结果支持“经过目标形态 / 统计检查后，LLM 生成可为部分检测器增益”。不支持生成异常可普遍迁移、适用于多变量系统或反映微服务故障原因。

## 9. Experimental Evidence

**作者明确讨论**：慢漂移和缓慢退化难保留复杂局部上下文；LLM 有时把振荡序列改写为简单单调 ramp，虽通过部分统计规则但形态语义可能失真。未来方向包括与 TimeGAN / VAE 比较、微调 LLM、改进模式保留与结构验证。（§5–6）

**本知识库分析**：五步检查关注局部统计、异常类型和窗口距离，不等于真实异常机制真实性；无 train-on-synthetic/test-on-real 分布泛化评估，无 Metric / Trace / Log、故障知识或因果约束。只评估单变量 NAB，尚不能推断在业务负载跃迁和真实故障共现时有用。仅和 jitter / scaling 比，缺少强生成模型作为基线。

**专题关系**：LLM-AP 是本组中真正让 LLM 直接改写数值序列的一篇；与 `GenIAS` 的 VAE 潜空间注入、`CAPMix` 的形态扰动 + 软标签可信度构成生成机制对比。与 `Synthetic Time Series` / `AIOpsLab` 不同，它不在运行系统中执行故障。与 `TraceLLM` 相比，生成目标分别是数值窗口和调用 DAG，均未建立跨模态一致性。

## 10. Limitations

### A. Author-stated limitations

- 慢漂移 / 慢退化可损失原有局部结构，振荡上下文可能变成单调 ramp；作者计划改进保型和结构验证，并比较 TimeGAN / VAE（§§5–6）。

### B. Reasoned inference

- 五阶段规则不是跨数据分布真实性度量；效果只覆盖单变量 NAB 和部分检测器。
- 无微服务 / 故障知识 / 多模态标签；不能据此推断实际故障语义。

### C. Evidence gaps

- 没有 train-on-synthetic/test-on-real 的跨域验证。
- 未评估多变量 KPI、Trace / Log 或正常业务波动与故障共现。

## 11. Research Implications

**本知识库分析**：可作为 LLM 数值异常增强路线参照；应明确区分“通过检测规则”和“真实机制 / 分布真实”。

## 12. Related Papers

`GenIAS`是潜空间生成对照；TSAD `CAPMix`用 DTW 修订伪异常置信度；`TraceLLM`目标是调用 DAG。

## 13. Evidence References



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
