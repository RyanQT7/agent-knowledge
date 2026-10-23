# 知识卡片：CAPMix

> 卡片基于完整本地 PDF 阅读。标记约定：**[作者主张]** 为论文表达的机制或结论；**[实验支持]** 为数据、消融或案例实际提供的证据；**[分析推断]** 为本知识库的解释或待验证方向。

## 1. Research Scenario

- **[作者主张]** AIOps 的多变量 KPI 异常检测；服务指标噪声大、非平稳，自动扩缩容、发布和采集活动会带来正常波动，训练数据也可能污染。（PDF §1, §5）
- **[实验支持]** 除 AIOps / ASD / SMD / Exathlon 外，作者还在 UCR、SWaT、WADI、ESA 测试迁移性。（Table 2）

## 2. Core Challenges

- **[作者主张]** 合成异常存在 Anomaly Shift：过于像正常波动的样本被错误硬标为异常；过于夸张的样本则离真实故障过远。（§1, §3.3.2–3.3.3）
- **[作者主张]** 训练集中的潜在异常、正常抖动和稀疏/不可靠标签会共同扭曲边界。（§1, §5.2）

## 3. Existing Limitations

- **[作者主张]** 正常性假设检测器在含噪污染数据上容易对 benign fluctuation 过敏；异常假设检测器则依赖模拟模式覆盖真实故障且强度校准。（§1–2）
- **[分析推断]** 这些路线虽强调动态环境，但模型仍以 KPI 窗口本身为主要证据，没有明确解释负载、发布或依赖变化导致的波动来源。

## 4. Core Idea

- **[作者主张]** 用结构化异常增强获得判别监督，DTW Label Revision 软化贴近正常中心的合成异常标签，Dual-Space Mixup 限制合成模式过度偏离；由 TCN 学习分类边界。（§3）

## 5. Technical Innovations

1. **[作者主张]** CutAddPaste 片段替换及可控趋势扰动，构造形状/相关、季节、趋势、全局与上下文异常。（§3.3.1, Fig. 3）
2. **[作者主张]** 以均值正常中心及 $\mu_d+\gamma\sigma_d$ DTW 阈值确定软标签 $1/\gamma$ 或硬标签 1。（§3.3.2, Eqs. (2)–(4)）
3. **[作者主张]** 在输入与 TCN 中间表示上混合样本和标签；三块 TCN 加 MLP/softmax 与 BCE 训练。（§3.3.3–3.4, Eqs. (5), (7)）

## 6. Key Mechanisms

- **[分析推断]** LR 主要处理“正常邻域附近的伪异常标签可信度”；DS-Mixup 主要处理“过于离群的合成样本导致边界过尖”。两者互补，而非两种相同的数据增强。
- **[作者主张]** 测试 score 是异常类 softmax 概率，固定阈值 $\tau$ 转告警；生产可配 POT，但主实验用 best threshold 报 RPA-F1。（§3.4, §4.1.2）

## 7. Experimental Evidence

- **[实验支持]** 八数据集、10 次运行；平均 Best RPA-F1：CAPMix 60.69%，CutAddPaste 40.02%。（Table 3）
- **[实验支持]** CAPMix 在 AIOps、Exathlon、UCR、SWaT、ESA 五组得分领先；SMD（27.42% vs AOC 60.85%）、ASD（61.30% vs RedLamp 69.59%）、WADI（34.08% vs SHUE 35.57%）落后。（Table 3）
- **[实验支持]** 平均消融分：NoAug 29.14、CAP 46.26、CAP-LR 47.34、CAP-Mix 57.49、完整 CAPMix 60.69。（Table 4）
- **[实验支持]** AIOps 人工加污染实验中，高污染下 CAPMix 相较 CAP 保持更高 F1 / precision；生产案例报告 RPA precision 0.80、F1 0.79、PR-AUC 0.87、NAB 0.76。（Fig. 5, Table 5）

## 8. Limitations

- **[作者未明确给出]** 论文没有独立的局限性章节。
- **[分析推断]** 均值中心对多模式正常状态可能失真；伪异常种类覆盖未知故障的能力尚未由实验充分证明；Best RPA-F1 的阈值扫描不能等同线上阈值效果；KPI 判别不提供业务上下文或故障原因。
- **[未充分说明]** 主文称训练标签含专家标记，也称无需训练异常，逐数据集标签可用性和 contaminated sample 处理仍需代码/补充材料核实。

## 9. Research Opportunities

- **[分析推断]** 用负载、发布、扩缩容及服务调用等上下文条件化正常状态与伪异常置信度，检验同时发生负载变化与故障时的可分性。
- **[分析推断]** 将单均值中心改成可校准的多正常状态模型，并报告状态覆盖、未知模式和误报成本。
- **[分析推断]** 在固定无监督阈值、事件级成本及跨集群部署下复验，以弥补最佳阈值和单生产案例的证据边界。

## 10. Related Papers

- CutAddPaste 是本文的基础增强算法；RedLamp、NCAD、AnomalyBert 是异常增强或伪标签相关对照。（Table 1, Table 3）
- 与批内 When Model Meets New Normals、CAROTS 的正式关系待各自完整精读后比较；当前只提出问题，不宣称方法结论。

## Links

- 完整精读笔记：[notes.md](notes.md)
- 原始 PDF：[CAPMix PDF](../../sources/papers/tsad-2024-2026/2026/ASE/CAPMix_Robust_KPI_Anomaly_Detection_for_AIOps_in_Noisy_and_Dynamic_Environments.pdf)
