# 知识卡片：MACE

> 根据本地 ICDE 2024 PDF 全文整理。标记：**[作者主张]** 原文结论；**[实验支持]** 表格 / 实验支撑；**[分析推断]** 知识库分析。PDF 页码为本地 PDF 页序。

## 1. Research Scenario

- **[作者主张]** 面向云服务、机器、传感器等不同实体的无监督多变量时序异常检测；目标是一个统一模型适配不同服务正常频率模式并兼顾点异常灵敏度和效率。（PDF pp.1–4, §§I, IV）
- **[实验支持]** SMD、JumpStarter 的 J-D1/J-D2、SMAP，以及附加的云监控数据 MC；按每十个子集组成 group 训练统一模型。（PDF pp.8–12, Tables V–VIII）

## 2. Core Challenges

- **[作者主张]** 服务间正常分布异质；一服务一模型成本高，统一无条件模型可能只拟合少量主导正常模式。（PDF pp.1–3, §I, Fig. 1）
- **[作者主张]** 短时异常可能被 encoder-decoder 平滑，频域计算希望利用稀疏性和并行性降低流量压力。（PDF pp.1–6）
- **[分析推断]** 论文的“多模式”侧重跨服务 / 子集模式差异，尚未显式处理同一服务内业务负载变化形成的动态状态。

## 3. Existing Limitations

- **[作者主张]** 针对单服务训练的模型难以扩展到海量云服务；普通全谱处理更昂贵，标准卷积可能弱化短时偏差。（PDF pp.1–3, 5–7）
- **[分析推断]** 静态服务频率基不能自动识别何时发生了合法业务状态切换；service identity 是上下文条件，不等同 workload / release / Trace 上下文。

## 4. Core Idea

- **[作者主张]** 按每个服务 normal training windows 中高频出现的 top-$k$ Fourier bases 建立 normal-pattern subspace；输入投影到相应子空间，用 dualistic convolution 同时放大时域短异常和增加频域异常可重构难度。（PDF pp.4–7, Fig. 2, §IV）

## 5. Technical Innovations

1. **时域 DualisticConv**：peak / valley 两路分别突出向上 / 向下偏差，stride 1 使异常影响扩展到 kernel 长度附近，随后逐点平均。（PDF pp.4–5, Eq. 2, Fig. 3）
2. **Context-aware DFT / IDFT**：依服务从正常训练窗口统计 top-$k$ 强 Fourier bases 出现次数，仅用相应子集投影与还原。（PDF pp.6–7, §IV-C）
3. **Frequency Characterization**：频谱投影系数加显式 sin / cos Fourier bases，形成三通道卷积输入。（PDF p.7, Fig. 4(b)）
4. **频域 dual convolution**：peak / valley 卷积以 kernel-length stride 近似选择每段频谱最大 / 最小值，分别让异常谱更难重构。（PDF pp.5–6, §IV-B）
5. **Theoretical sparse basis argument**：截断归一化频谱的异常—正常 KL 重构误差 gap 为 $\log[\sum_{i=1}^{k}q^N(\omega_i)/\sum_{i=1}^{k}q^A(\omega_i)]$；完整频谱归一化质量均为 1，gap 为 0。（PDF pp.7–8, Theorem 2, Corollary 1）
6. **双支路分数**：时域扩增后进入模式投影与频域自编码，IDFT 后取 peak / valley 两支路中逐点较大的重构误差。（PDF pp.4–5, Fig. 2）

## 6. Key Mechanisms

- **[作者主张]** pattern subspace 让 detector 判断样本与“该服务自身的正常频率模式”关联程度，而不是只用跨服务共享的单一正常分布。（PDF pp.2, 6–7）
- **[作者假设]** 频域异常通常有更强 signal / 更高幅值方差；理论部分假设异常幅值是正常幅值上加期望为正的 i.i.d. shift。（PDF pp.5–8, Table II, Assumption 1）
- **[分析推断]** 此机制对跨服务静态异质性有针对性；未证明能识别单个服务的实时负载状态切换或波动成因。

## 7. Experimental Evidence

- **[实验支持]** 统一模型 Table V 的 F1：SMD .910、J-D1 .934、J-D2 .961、SMAP .977；作者报告相对最强 baseline 平均提升 8.7%。（PDF pp.9–10, Table V）
- **[实验支持]** 对照单服务专模，MACE 在 J-D1 .934 vs JumpStarter .933、J-D2 .961 vs .968、SMAP .977 vs .970；但最异质 SMD .910 低于 TranAD .961。（PDF pp.10–11, Table VI）
- **[实验支持]** 跨 group 测试 F1：SMD .863、J-D1 .885、J-D2 .964、SMAP .973。（PDF pp.11–12, Table VIII）
- **[实验支持]** SMD 去掉 Pattern Extraction 后 F1 .910→.696；去掉时域双卷积后 .910→.084。J-D2 去掉 Frequency Characterization 后 .961→.975，显示模块收益随数据集不同。（PDF p.12, Table IX）
- **[作者主张 / 局部评估]** 摘要宣称约 4×更快；效率图只在 SMD 单组、特定服务器配置下 profiling，不能当作所有生产负载的固定吞吐保证。（PDF pp.1–2, 11, Fig. 6(a)）

## 8. Limitations

- **[实验边界]** 论文仅报告 Precision / Recall / F1；阈值策略提到 POT，但各数据集完整阈值选择协议不清晰。（PDF pp.3, 9–10）
- **[方法边界]** top Fourier bases 按服务正常训练频谱静态建立；未显式建模同服务内的高低负载、发布、扩缩容和日周期状态。（PDF §IV-C）
- **[作者未充分讨论 / 证据缺口]** 未见 service unseen 的子空间来源细节；因此 Table VIII 不足以证明严格 zero-shot，不清楚是否需目标服务正常校准数据。（PDF pp.11–12）
- **[分析推断]** 上下偏差可被 DualisticConv 突出，但理论频谱假设聚焦高幅值 / 高方差异常；低能量、相位或跨变量因果异常可能不符合假设。
- **[复现边界]** MC 来自云厂商且未提供本地公开链接；效率图只覆盖单配置，F1 阈值 / reconstruction norm 细节需通过补充代码核实。

## 9. Research Opportunities

- **[分析推断]** 把 workload、业务时段、部署版本与服务身份联合条件化，区分同一服务的多种正常态和真实故障。
- **[证据缺口]** 在负载变化与真实故障同时发生时评估误报 / 漏报，追踪 service-basis 更新及新正常吸收风险。
- **[分析推断]** 用相位、跨指标因果关系或质量校准补充幅值频谱假设，覆盖低能量异常与关系型异常。
- **[证据缺口]** 明确 held-out service 的 base 构建信息来源，使用无目标标签、无目标正常校准和少样本正常校准三种协议分开比较。
- **[证据缺口]** 在开放 KPI / 多组织 workload 上同步报告 detection metrics、阈值代价、吞吐、内存和 per-service 模型维护成本。

## 10. Related Papers

- [CrossAD](../crossad/notes.md)：CrossAD 学习单序列不同时间尺度的映射及跨窗口子序列原型；MACE 学服务条件频域基，均利用重构但条件信息不同。
- [CAROTS](../carots/notes.md)：跨变量 Granger 预测关系与因果增强；MACE 的核心是单服务频率子空间。
- [When Model Meets New Normals](../when-model-meets-new-normals/notes.md)：在线适应新测试态；MACE 使用训练预处理的静态服务模式。
- [CAPMix](../capmix/notes.md)：伪异常与软标签鲁棒训练；MACE 是正常模式重构路线。
- [Fortifying Time Series](../fortifying-time-series/notes.md)：形式化 DTW 对抗稳定证书；MACE 没有对抗认证机制。

## Links

- 详细精读笔记：[notes.md](notes.md)
- 原始 PDF：[MACE PDF](../../sources/papers/tsad-2024-2026/2024/ICDE/Learning_Multi_Pattern_Normalities_in_the_Frequency_Domain_for_Efficient_Time_Series_Anomaly_Detection.pdf)
- 论文 DOI：[ICDE 2024](https://doi.org/10.1109/ICDE60146.2024.00047)
