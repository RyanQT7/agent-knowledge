# TSAD 知识库检索与使用指南（33 篇）

## 入口

1. 从根目录 [INDEX.md](../../INDEX.md#papers) 进入全部 TSAD 论文笔记、卡片和 Knowledge Reviews。
2. 先看 [TSAD final synthesis](../reviews/tsad-final-synthesis.md) 了解 33 篇方法全景、证据边界与研究问题；再看对应的批次 Review（v3–v13）了解机制比较。
3. 选定论文后打开 `papers/<paper-id>/knowledge-card.md` 快速定位，再读 `papers/<paper-id>/notes.md` 的方法、公式、实验和局限。单篇笔记顶部链接到该论文实际 PDF。
4. 源文件清单 / 下载状态仍以 [download_report.md](../../sources/papers/tsad-2024-2026/download_report.md) 为准；PDF 不进 Git，使用本地已整理文件。

## 按研究问题检索

| 关注问题 | 建议先读 | 可继续比较 |
| --- | --- | --- |
| 新的合法正常状态、漂移与在线适应 | [When Model Meets New Normals](../../papers/when-model-meets-new-normals/knowledge-card.md)、[CAPMix](../../papers/capmix/knowledge-card.md)、[IMPACT](../../papers/impact/knowledge-card.md) | [MACE](../../papers/mace/knowledge-card.md)、[CrossAD](../../papers/crossad/knowledge-card.md)、[Graph-MoE](../../papers/graph-moe/knowledge-card.md)、[TimeRCD](../../papers/time-rcd/knowledge-card.md)、[TeamWork](../../papers/teamwork/knowledge-card.md)；重点对照状态标签、伪标签污染和 rare-normal false alarm。 |
| 因果 / 通道关系与结构变化 | [CAROTS](../../papers/carots/knowledge-card.md)、[GCAD](../../papers/gcad/knowledge-card.md)、[OracleAD](../../papers/oraclead/knowledge-card.md) | [SARAD](../../papers/sarad/knowledge-card.md)、[CCM-TAD](../../papers/ccm-tad/knowledge-card.md)、[TeamWork](../../papers/teamwork/knowledge-card.md)、[ScatterAD](../../papers/scatterad/knowledge-card.md)；核对“图 / causal / dominant”实际指什么对象，以及有无物理拓扑或根因 ground truth。 |
| 时间、频率、多尺度、曲率证据 | [MACE](../../papers/mace/knowledge-card.md)、[CrossAD](../../papers/crossad/knowledge-card.md)、[TFC](../../papers/tfc/knowledge-card.md) | [TFMAE](../../papers/tfmae/knowledge-card.md)、[TriAD](../../papers/triad/knowledge-card.md)、[FlowFuse](../../papers/flowfuse/knowledge-card.md)、[AnoMamba](../../papers/anomamba/knowledge-card.md)、[TeamWork](../../papers/teamwork/knowledge-card.md)；区分 feature fusion、score fusion、masking 和全局依赖学习。 |
| 鲁棒性、训练污染和噪声 | [Fortifying Time Series](../../papers/fortifying-time-series/knowledge-card.md)、[CAPMix](../../papers/capmix/knowledge-card.md)、[PCRTA](../../papers/pcrta/knowledge-card.md) | [IMPACT](../../papers/impact/knowledge-card.md)、[IGAD](../../papers/idempotent-reconstruction/knowledge-card.md)、[KAN-AD](../../papers/kan-ad/knowledge-card.md)、[COGNOS](../../papers/cognos/knowledge-card.md)；先对齐威胁模型：DTW 扰动、异常标签污染、随机噪声和 residual noise 不等价。 |
| 重建与预测为何会过拟合异常 | [KAN-AD](../../papers/kan-ad/knowledge-card.md)、[RTdetector](../../papers/rtdetector/knowledge-card.md)、[IGAD](../../papers/idempotent-reconstruction/knowledge-card.md) | [Sub-Adjacent Transformer](../../papers/sub-adjacent-transformer/knowledge-card.md)、[AnoMamba](../../papers/anomamba/knowledge-card.md)、[CrossAD](../../papers/crossad/knowledge-card.md)、[COGNOS](../../papers/cognos/knowledge-card.md)；比较输出分数、重构约束、趋势 / residual 处理和局限。 |
| 统计正常性、分数融合与校准 | [COGNOS](../../papers/cognos/knowledge-card.md)、[FlowFuse](../../papers/flowfuse/knowledge-card.md)、[Conditional Normalizing Flows](../../papers/cnf-latent-dynamics/knowledge-card.md) | [TSB-AD](../../papers/tsb-ad/knowledge-card.md)、[Quo Vadis](../../papers/quo-vadis/knowledge-card.md)；检查假设诊断、阈值来源、window / dimension 对检验效力的影响。 |
| LLM/VLM 是否提供语义解释 | [AnomalyLLM](../../papers/anomalyllm/knowledge-card.md)、[Delving into LLMs](../../papers/delving-llm-tsad/knowledge-card.md) | [AnomSeer](../../papers/anomseer/knowledge-card.md)、[VLM4TS](../../papers/vlm4ts/knowledge-card.md)、[TimeRCD](../../papers/time-rcd/knowledge-card.md)；分别追踪 teacher、prompt、生成式监督、patch visual verification 与相对上下文，不把 reasoning trace 直接当作经过验证的根因。 |
| 指标协议和 benchmark 可信度 | [Quo Vadis](../../papers/quo-vadis/knowledge-card.md)、[TSB-AD](../../papers/tsb-ad/knowledge-card.md) | 再读每篇目标论文的实验设置；核对 test-best threshold、point adjustment、Aff-F、VUS、event delay 与固定误报预算。 |

## 用现有 Skills 的建议路径

- **单篇复习 / 溯源**：使用 `knowledge-query` Skill。默认只读本地 Markdown，先查 final synthesis / Reviews，再打开具体 paper note；只有关键论断不清楚或用户要求原文数字时才回看本地 PDF。若本库没有足够证据，应明确指出缺失点，不用常识补齐。
- **跨论文比较**：使用 `knowledge-query` 先按问题选小范围；已有的批次级整合位于 `notes/reviews/knowledge-review-v3.md` 至 `v13.md`。如需把新的阅读结果写回，再明确转到 `knowledge-review`。
- **新增论文**：单篇用 `paper-reading`，一组新 PDF 用 `learning-batch` 管理顺序；先检查 INDEX / 现有 notes 避免重复。`learning-batch` 不替代逐篇 PDF 阅读和 Review。
- **AIOps 专题扩展**：`aiops-learning-batch` 仅在任务转向 AIOps / RCA 文献批次时使用；这 33 篇 TSAD 资料不需要另建 AIOps 子库或 Skill。

## 建议的问法

问题最好指定比较维度与 evidence requirement，例如：

- “只用本地知识库比较 WMMNN、TimeRCD、CNF 如何定义新正常；分别指出更新污染风险和原文证据位置。”
- “总结使用频域 normality 的论文，并区分 learned spectrum、frequency mask 和 temporal-frequency score fusion。”
- “列出对因果 / 关系有主张的论文；标明每篇关系对象是变量、时间点还是跨窗口原型，以及是否有真实图 ground truth。”
- “基于论文实验，哪些方法报告了 event delay / fixed FPR？若没有足够证据请标记未报告。”
- “正常负载变化和故障并发的研究空白有哪些已有先行方法？请不要把 online adaptation 或 context modeling 本身称为新方向。”

## 证据使用规则

回答时区分三层：

1. **论文主张**：作者说要解决什么、为什么设计该模块。
2. **实验支持**：具体数据集、协议、表格 / 图 / 消融实际支持什么；指出数据范围和反例。
3. **综合分析**：多篇之间的关系、推断或研究机会；注明尚未被实验验证。

重要数字应回到笔记中记录的 Section、Table、Figure 或 Appendix，并按需查看已链接 PDF。不能只凭平均排名声称普适优势，也不能把 prototype、attention、association score、flow likelihood 或 latent GOF 自动解释为业务根因。

## 当前已知边界

- 所有 33 篇都有逐篇精读笔记与知识卡片；未完成模型训练、代码复现或新 benchmark。
- 综合报告中明确区分 benchmark 证据与跨论文分析；normal-state / fault concurrency 和真实 workload–Trace-conditioned evaluation 仍是开放问题。
- `knowledge-query` 是本地知识检索与解释流程，不会自动写入或更新本库。要保存新增结论，需要明确使用 review / batch 工作流。
