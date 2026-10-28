# LLM-AP：LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation

## 1. Metadata

- **Authors**: Geunho Lee, Jieun Lee, Tae-yong Kim, Jongpil Jeong
- **Year / venue**: 2026, Applied Sciences 16(14), Article 6851（期刊论文，不标为 CCF 会议论文）
- **DOI / official source**: https://doi.org/10.3390/app16146851 ; https://www.mdpi.com/2076-3417/16/14/6851
- **Local PDF**: [MDPI 正式开放版](../../../sources/papers/llm-microservice-anomaly-generation/llm-ap_applied-sciences-2026.pdf)
- **Code**: 未在核验的论文正文 / 官方页面确认作者代码库
- **Paper ID**: llm-ap-synthetic-augmentation
- **Tags**: LLM; univariate-TSAD; synthetic-anomaly; prompt; validation; NAB

## 2. One-Sentence Summary

LLM-AP 将正常窗口和目标异常类型描述为结构化文本提示，让冻结的 GPT-3.5-turbo / GPT-4o 改写数值窗口，再用五阶段格式、形态、类型和距离验证 + Self-Refine 筛选样本；它是通用单变量异常增强，不使用微服务知识，也没有生成 Metric–Trace–Log 联合数据。

## 3. Research Scenario and Problem

作者研究真实单变量时间序列异常检测中标注异常不足、类型长尾，以及已有合成增强可能产生失真数值窗口的问题。输入为一维连续值序列、已标注的异常区间和检测模型；输出为通过验证的额外异常窗口及增强后的训练集，最终任务是检验增强是否提升检测器 F1。NAB 的 47 条真实时间序列涵盖五类领域；不是微服务专用 KPI，也不含调用 Trace、日志和根因标签。（PDF §§1–3, §4.1）

### 核心挑战

1. **异常类型要贴合数据**：固定注入可能产生数据里没有的异常形态。LLM-AP 先从已有标注归纳 6 种异常子类型，仅生成数据中实际出现的类型。（§3.2）
2. **语言模型容易返回不可解析 / 长度不符的数据**：结构化提示和 JSON 输出仍不能保证数值可靠，需要长度修复及非有限值检查。（§3.3.1）
3. **异常要有可检测信号，又不能脱离上下文**：过弱变化没有检测意义，过强或局部结构不匹配的序列不真实。作者使用距离上、下界和类型规则筛选。（§3.3.2–3.3.5）
4. **检测指标提升不能只来自合成标签数量**：需要对比增强前后、验证 / 未验证样本，以及多种检测器。（§4）

## 4. Existing Methods and Core Idea

作者认为传统规则 / 统计扰动难以构造多样且与原始上下文相容的异常，而未约束的 LLM 输出也可能有长度、数值和形态缺陷。核心思想是让 LLM 负责“依据上下文改写数值”，由一套可重复的自动筛选管线负责“判断是否保留”。LLM 不被微调，只以 zero-shot / few-shot 方式接收任务说明、正常样本与少量异常示例。

## 5. Methodology

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

## 6. Experimental Evaluation

- **数据 / Baseline**：NAB 47 条真实数据，45 条可成功生成，2 条失败（AWS EC2 disk writes 数据大多为零值突发；keystroke 序列近似二元）。对比无增强、jitter / scaling 和未验证合成样本；检测器 TimesNet、PatchTST、Transformer、Autoformer。（§4.1–4.3）
- **设置**：两 GPT 版本、temperature 0.5 / 1.0，Append / Replace。GPT-3.5 通过验证 1541 个窗口，GPT-4o 1604 个；目标异常占比 10%。（§4.2）
- **结果**：TimesNet 上 GPT-4o、temperature=1、Append 得到 F1 0.7238±0.001，对照 0.6893±0.002；PatchTST 最佳 0.7024，对照 0.6929；Transformer 最佳 0.6948，对照 0.6858。Autoformer 反而全部低于其无增强对照，例如 GPT-3.5、temperature=1、Replace 为 0.2753 对 0.6071。（Table 8）
- **验证消融**：对 TimesNet / PatchTST / Transformer，验证后样本在所有比较配置中优于未验证样本；未验证合成样本的收益不高于基线。Autoformer 是例外，所有增强配置均降低性能。（Table 8）
- **支持范围**：结果支持“经过目标形态 / 统计检查后，LLM 生成可为部分检测器增益”。不支持生成异常可普遍迁移、适用于多变量系统或反映微服务故障原因。

## 7. Limitations and Research Relevance

**作者明确讨论**：慢漂移和缓慢退化难保留复杂局部上下文；LLM 有时把振荡序列改写为简单单调 ramp，虽通过部分统计规则但形态语义可能失真。未来方向包括与 TimeGAN / VAE 比较、微调 LLM、改进模式保留与结构验证。（§5–6）

**本知识库分析**：五步检查关注局部统计、异常类型和窗口距离，不等于真实异常机制真实性；无 train-on-synthetic/test-on-real 分布泛化评估，无 Metric / Trace / Log、故障知识或因果约束。只评估单变量 NAB，尚不能推断在业务负载跃迁和真实故障共现时有用。仅和 jitter / scaling 比，缺少强生成模型作为基线。

**专题关系**：LLM-AP 是本组中真正让 LLM 直接改写数值序列的一篇；与 [GenIAS](../genias/notes.md) 的 VAE 潜空间注入、[CAPMix](../../capmix/notes.md) 的形态扰动 + 软标签可信度构成生成机制对比。与 [Synthetic Time Series](../synthetic-cloud-microservices/notes.md) / [AIOpsLab](../aiopslab/notes.md) 不同，它不在运行系统中执行故障。与 [TraceLLM](../tracellm/notes.md) 相比，生成目标分别是数值窗口和调用 DAG，均未建立跨模态一致性。

## 8. Evidence Map

| 论断 | 原文定位 |
| --- | --- |
| 六类异常、上下文窗口和提示 | PDF §§3.1–3.2 |
| 生成步骤、模型与 Append / Replace | PDF §3.2–3.3 |
| 五阶段验证及 RelDTW / CUSUM 规则 | PDF §§3.3.1–3.3.5, Eqs. 1–12, Table 2 |
| NAB 结果、生成量、失败序列 | PDF §§4.1–4.3 |
| 检测器结果和验证消融 | PDF Table 8 |
| 慢漂移结构失真及未来方向 | PDF §§5–6 |
