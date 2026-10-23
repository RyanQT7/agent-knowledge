# Knowledge Review v4：TSAD batch 2 — 多模式、尺度关系与认证鲁棒性

## Scope and Evidence Labels

本次 Review 对比第二批三篇已完成全文阅读的论文，并结合第一批三篇笔记回答用户关心的问题：

- [CrossAD](../../papers/crossad/notes.md) — 跨尺度关联与跨窗口上下文
- [Fortifying Time Series](../../papers/fortifying-time-series/notes.md) — DTW 对抗鲁棒认证
- [MACE](../../papers/mace/notes.md) — 服务条件的多模式频域正常性

跨论文判断均限定为已读的六篇论文，不代表对后续 27 篇或整个 TSAD 文献的完整检索结论。本文用：

- **Paper-backed fact**：可追溯到单篇 PDF 的章节、公式或图表。
- **Cross-paper synthesis**：对多篇论文证据的组织和比较，不是作者共同提出的定义。
- **Research gap within current scope**：当前已读材料没有充分验证的问题；需待其余论文完成后再判断是否是全库研究空白。

## 1. What This Batch Adds

### Paper-backed fact

- **CrossAD** 把正常性表述为跨采样尺度的映射：以粗尺度和全局原型上下文重建细尺度，用重构残差检测映射失配。子序列 query 和原型在不同窗口间共享重复形态，但没有业务状态语义。（CrossAD §§3.2–3.4, Eqs. 1–12, Tables 1–4）
- **Fortifying Time Series** 不新增异常表示模型，而是给被保护模型外接 Gaussian percentile smoothing，再将 $\ell_2$ 认证经 Keogh lower bound 转为 DTW 认证半径。其定理保证攻击球内分类决策不变，证书不保证原始分类正确。（Fortifying §§3.1–3.3, Theorem 3.3; Appendix E）
- **MACE** 按服务 / 子集建立由频繁 top-$k$ Fourier bases 组成的静态 normal-pattern subspace，并共享检测网络；DualisticConv 在时域扩展短异常，在频域让高变化频谱更难重构。论文所称多模式首先是跨服务异质性。（MACE §§IV–V, Eqs. 2, 10–11, Tables V–IX）

### Cross-paper synthesis

这三篇把研究焦点从上一批的形态增强、测试时适应和因果预测关系进一步扩展为三种互不等价的机制：

1. **时间尺度关系（CrossAD）**：一条序列的粗到细映射是否符合训练期规律。
2. **样本周边决策保证（Fortifying）**：检测器对指定 DTW 扰动是否保持当前判定。
3. **服务条件的频率先验（MACE）**：样本能否由对应服务常见频率基重构。

这三者分别回答“序列关系是否异常”“判定会否被攻击者翻转”“相对于哪个服务正常谱偏离”。它们都不能单独回答“业务为什么变化”。

## 2. Comparison Across Six Papers

| Paper | 正常性的主要参照 | 上下文 / 状态机制 | 论文想解决的问题 | 关键证据边界 |
| --- | --- | --- | --- | --- |
| CAPMix | 单一训练均值中心、DTW 形态、注入标签 | 训练期伪异常和 dual-space Mixup | 合成异常偏离真实故障或过于接近正常 | 训练标签与单中心假设；阈值扫描 Best RPA-F1；业务原因未条件化 |
| When Model Meets New Normals | EMA 趋势与模型重构模式 | 测试期预测正常 mask 和在线 SGD | 旧模型遇到新正常时的误报 | 多数点正常假设和伪标签污染；WADI 附录存在数字口径问题 |
| CAROTS | 训练正常期的 Granger 预测图和嵌入关系 | CPA / CDA 增强、SOC 保留多样正例 | 变量联动变化中检测因果预测关系破坏 | 固定图假设；现实图无真值；WADI 上加入因果分数不一定有益 |
| CrossAD | 粗尺度到细尺度正常映射 | 子序列 query + EMA 全局原型 | 跨尺度关联被异常破坏、窗口缺少全局上下文 | 原型非业务状态标签；推理时更新边界不明；SWAN VUS-ROC 例外于全文主张 |
| Fortifying | 预训练模型的平滑分数与 DTW 半径 | 高斯 percentile smoothing + Keogh 证书 | 白盒时间扭曲攻击翻转预测 | 只证决策不变；Keogh 保守；覆盖率、检测效用和推理成本权衡明显 |
| MACE | 服务正常训练窗口中常见的 Fourier bases | 服务身份选择静态频率子空间 | 一模型跨多个服务模式共享，同时提高点异常灵敏度 | 未明确未见服务的基来源；跨服务模式不等于单服务动态业务状态 |

**Cross-paper synthesis：** “多模式正常性”至少有三个层级，阅读时应分开：

- **跨实体正常模式**：MACE 在已知服务 / 子集之间建立条件频率基，最直接处理实体异质性。
- **实体内随时间变化的状态**：WMMNN 通过 EMA 和测试时更新追随新分布；MACE 没有显式命名这种状态，CrossAD 的原型是重复子序列统计簇，并非状态语义。
- **状态内结构关系**：CAROTS 关注跨变量预测依赖是否保留，CrossAD 关注跨时间分辨率映射；二者的“关系”对象不同。

CAPMix 的单均值中心与 MACE 的按服务频率子空间也不是一类正常模式模型：前者根据合成样本到总体中心的 DTW 距离软化伪异常监督；后者以实体标识选择频域基础。二者都没有充分说明同一服务不同负载模式的动态切换。

## 3. User Questions: Current Evidence

### 多种正常运行状态如何建模？

**Paper-backed fact：** MACE 在每个服务训练期选择常见频率 bases；CAROTS 的 CPA + SOC 保留共享因果关系下的语义多样正样本；CrossAD 用 query / 原型聚合多尺度子序列；WMMNN 可在测试流更新以跟随新状态。（MACE §IV-C; CAROTS §§3–4; CrossAD §3.3; WMMNN §3–4）

**Cross-paper synthesis：** 这些方法已经覆盖服务差异、重复子序列、同因果结构变体、连续测试分布更新等技术路线；因此不能把“多模式正常建模”整体说成未被研究。当前已读论文仍未证明可以识别并解释“同一服务的低负载、高峰、扩缩容、发布期”等业务态，并在状态间切换时安全地检出叠加故障。

### 正常业务波动和真实故障如何区分？

**Paper-backed fact：** CAPMix 用形态相似度修正伪异常标签；WMMNN 用趋势与预测正常 mask 适应新分布；CAROTS 将因果保持变化与因果破坏变化用于增强和检测；CrossAD 观察多尺度关系；MACE 参照服务正常谱；Fortifying 把扰动定义成白盒 DTW attacker 的预算。（各 note §§3–6）

**Cross-paper synthesis：** 这些是不同形式的时序证据，均不是业务真值。尤其 Fortifying 的扰动预算和分类稳定证书不提供负载语义；MACE 的 service ID 不是 workload；CrossAD 原型没有命名状态；CAROTS 的预测因果关系也不等同发布或业务事件归因。

### 现有方法是否只是抑制噪声，没有解释波动来源？

已读方法不只是平滑噪声：CAROTS 提供变量间预测依赖；CrossAD 提供尺度映射证据；MACE 提供服务参照频谱；Fortifying 提供攻击鲁棒保证。但这些机制说明的是偏离何种统计 / 结构参照或对哪类扰动稳定，尚未把业务负载、Trace、发布、扩缩容和根因事件连成解释链。**异常证据更结构化，不等于来源已解释。**

### 是否利用 Metric、Trace、业务负载和运行上下文？

**Paper-backed fact：** 六篇都以时间序列本身为主要输入。MACE 显式按服务 / 子集选择频率基，是有限的静态实体上下文；CAROTS 在局限中提及外生变量；当前笔记未见任一篇将 Trace、deployment / release 或 workload 作为成套条件输入并评估。（MACE §IV-C; CAROTS Appendix D; 其余 notes §§4–6）

**Current status：Open。** 当前尚不能判断 33 篇全部如此；后续要逐篇核对多模态或业务上下文路线。

### 如何处理正常负载变化与故障同时发生？

**Research gap within current scope：** 六篇没有系统构造“合法负载变化与真实故障同步”的测试矩阵。WMMNN 的预测正常更新可能吸收漏报故障；MACE 静态子空间可能将状态切换视为偏离；CrossAD 原型 / CAROTS 图的稳定或更新条件也没有这种并发验证。CAPMix 的生产案例和 CAROTS 的因果保持例子不是受控并发实验。（CAPMix §5; WMMNN §4; CAROTS §4; CrossAD §4; MACE §5）

### 哪些思路已被提出？

- 多服务 / 多 normality 建模：MACE 已明确提出频域服务子空间；CVPR 2020 的 memory-guided normality 也被 MACE 引为先行研究，故“用记忆表达正常模式”不可直接宣称全新。（MACE §§II, IV-C, ref. [10]）
- 在线新正常适应：WMMNN 不是唯一在线学习背景；其相关工作讨论 drift adaptation，具体机制是 EMA + 预测正常掩码。（WMMNN §§2, 4）
- 跨尺度异常检测：CrossAD 对跨尺度映射和 query/context 的组合有具体新设计，但 multi-scale 本身以及相关尺度模型已存在；论文参考文献包含 TimeMixer / TimesNet 等。（CrossAD §§2–3）
- 因果 / Granger 关系异常检测：CAROTS 的增强和评分有具体机制，但因果 TSAD 不是空白领域，需把新意限定在 CPA/CDA/SOC 等可对照细节。（CAROTS §§2–4）
- $\ell_p$ 随机平滑认证和 DTW 攻击此前已有工作；Fortifying 的贡献是特定的 percentile smoothing + Keogh lower bound 认证桥接，不宜将“认证鲁棒性”整体标为首次。（Fortifying §§2–3）

### 哪些研究结论仍缺实验？

- 多模式正常状态是否与业务负载 / 发布 / 调度语义一致，以及负载变化与故障同时发生时的误报 / 漏报。
- WMMNN 长时运行中异常污染在线更新后的恢复机制；CrossAD / MACE 上下文模式在动态新状态中的来源与更新安全性。
- CAROTS 真实因果图的 ground truth 可靠性；跨尺度映射、因果依赖和外部 workload 的组合是否有独立增益。
- 无标签阈值和告警成本：现有 Best F1、point adjustment 或 SPOT 阈值结果不能直接视为线上目标下保证。
- Fortifying 的证书在业务认可的 DTW 半径下覆盖率、效用、时延；certificate 保持的是决策，不是决策正确。

## 4. Evidence Issues to Preserve

- CrossAD 主表中 SWAN 的 VUS-ROC 为 .9499，略低于 TimesNet .9515；这与文中“所有数据集 VUS 指标均优于”的概括不符。（CrossAD Table 1）
- CrossAD Table 3 的文字增益和平均表值直接计算略有差异，引用时保留原始表格口径。（CrossAD §4.3, Table 3）
- Fortifying §4 Settings 称七个 benchmark datasets，Table 4 列八行；Table 1 还有 CREDITCARD + COUTA 的 F1 .192→.003 / ROC-AUC .900→.300，不能概括为所有设置只有轻微性能损失。（Fortifying §4, Tables 1, 4）
- Fortifying 的本地 PDF 有 NeurIPS 2025 与 arXiv:2605.07690v1 (2026-05-08) 双版本标记，来源版本需要核实。（Fortifying p.1）
- MACE 正常模式实验正文称四个真实数据集，但同时列出 SMD、J-D1、J-D2、SMAP、MC；Table VIII 的 held-out group 模式基获取流程、F1 threshold protocol 和 Table IX 的 J-D2 反常消融结果值得复查。（MACE §§V-A–E, Tables V–IX）
- 第一批既有的 CAROTS WADI full model 弱于去掉因果分数、WMMNN WADI 附录数字和方向不一致、CAPMix 原 PDF 模板元数据问题继续保留在各单篇笔记；不为“统一叙述”抹去这些边界。（CAPMix / WMMNN / CAROTS notes）

## 5. Current Open-Question Status

| Question | Status after six papers | Evidence-based understanding |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | MACE 明确表示跨服务频域 normality；WMMNN 适应测试时新分布；CAROTS SOC 保留共享关系下的多样正例；CrossAD 汇聚跨窗子序列模式。但同服务内业务语义状态切换未充分命名和验证。 |
| 正常波动与真实故障如何区分？ | Partially Answered | 形态、趋势、变量依赖、尺度映射、服务频谱均提供判别证据；缺少对负载 / 变更语义的外部核验及并发事件系统实验。 |
| 是否利用 Metric、Trace、workload、发布等上下文？ | Open | 当前以时序为主；MACE 使用服务身份，CAROTS 把外生变量列为未来问题。没有成套 Trace / deployment / workload 条件评估。 |
| 证据是否解释波动来源？ | Partially Answered | CAROTS、CrossAD、MACE 让分数依赖结构关系，但均不建立业务事件根因解释链。 |
| 正常负载变化与真实故障同时发生如何处理？ | Open | 六篇均缺受控并发实验；在线污染、静态频率 / 因果结构变化、上下文原型安全更新仍是关注点。 |
| 哪些创新方向不可直接称为新空白？ | Partially Answered | 频域多 normality、在线 drift adaptation、multi-scale、因果 TSAD、DTW attacks / smoothing 均有前序研究；新主张应限定可复现的机制差异。 |
| 结论的证据有哪些薄弱处？ | Partially Answered | 已记录阈值协议、数据集口径、子空间来源、表文不一致、测试时更新阶段、效率外推与在线业务代价等问题。 |

原始问题和按论文归档的问题见 [notes/questions.md](../questions.md)。本 Review 更新当前判断，不删除旧批次历史。

## 6. Next Batch Priorities

前六篇已完成。后续按照研究主题组织剩余论文，优先验证：

1. 是否存在显式模式聚类、条件生成或 workload-aware normality；它们建模的是跨服务差异还是服务内动态状态。
2. 是否用日志、Trace、发布、业务负载或控制信号校准时序告警；有没有负载变化与故障同步样本。
3. 鲁棒 / 认证工作如何定义语义保持威胁模型、真实攻击覆盖率和业务成本。
4. 比较新方法前先核对先行文献和 ablation；将“表示可解释”与“波动根因已解释”分开。

在 33 篇全部检查前，以上是阶段性证据地图，不是最终研究空白清单。
