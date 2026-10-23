# 知识卡片：When Model Meets New Normals

> 依据本地 PDF 全文与附录。标记：**[作者主张]** 为论文表述；**[实验支持]** 为实验/表格实际证据；**[分析推断]** 为本知识库推导。页码均指本地 17 页 PDF。

## 1. Research Scenario

- **[作者主张]** 无监督时序异常检测在测试期遇到正常分布变化 $P_{train}\ne P_{test}$；模型需要适应新正常状态而不依赖测试标签或训练数据。（PDF pp.1–4, Problem Statement）
- **[实验支持]** 在 SWaT、WADI、SMD、MSL、SMAP、Yahoo 等漂移场景，以及 CreditCard 小漂移对照上评估；另测 AnoShift 的 NEAR/FAR 时间切分。（Tables 1–2, Appendix Table 4）

## 2. Core Challenges

- **[作者主张]** 固定模型会将测试期正常趋势/动态变化产生的重构误差视作异常；仅去趋势仍学不到全部动态变化。（PDF pp.1–3, Figs. 1–2）
- **[作者主张]** 测试流可能含异常，全样本自适应会污染检测器；但只用训练正常状态又无法跟上新正常。（PDF pp.2–4）

## 3. Existing Limitations

- **[作者主张]** 冻结正常性模型对分布漂移敏感；趋势归一化不能表达趋势以外的动态变化；全测试样本 TTA 可能被异常破坏。（PDF pp.1–4）
- **[分析推断]** 以自身预测筛选“正常训练样本”仍会因误报/漏报而带来选择偏差和错误反馈。

## 4. Core Idea

- **[作者主张]** 先用 EMA 追踪窗口趋势并去趋势，再用当前模型预测为正常的点做自监督在线重构更新，联合处理均值迁移和更复杂的新正常动态。（PDF pp.3–4, Eqs. (2)–(4), Algorithm 1）

## 5. Technical Innovations

1. **[作者主张]** 对窗口均值做 EMA：\(\mu_t=\gamma\mu_{t-w}+(1-\gamma)\hat\mu_t\)，输入去趋势重构并在输出加回趋势。（PDF pp.3–4, Eq. (2), Fig. 3）
2. **[作者主张]** 用检测器分数与阈值形成预测掩码，只将预测正常位置的重构误差用于在线 SGD 更新。（PDF p.4, Eqs. (3)–(4), Algorithm 1）
3. **[作者主张]** 组件化测试时包装现有 detector；当前参数和趋势状态足以继续处理流，不需缓存原训练集。（PDF pp.2–4）

## 6. Key Mechanisms

- **[作者主张]** 趋势估计用全窗口数据以跟踪变化；梯度更新屏蔽预测异常点以减少异常污染。（PDF p.4）
- **[分析推断]** 漏检异常会被纳入在线学习，误报的新正常则无法参与更新；若分布变化与故障并发，EMA 和模型更新都可能受污染。
- **[作者主张]** 模型先输出当前窗口分数，再生成掩码、更新参数；阈值也决定学习数据的筛选。（PDF pp.4, 10, Algorithm 1）

## 7. Experimental Evidence

- **[实验支持]** Table 1 中 Yahoo A1-R20：F1 从 MLP 0.067 到 0.678、AUROC 从 0.367 到 0.971；MSL P-15：AUPRC 从 0.061 到 0.575；CreditCard 的 F1 仅从 0.127 到 0.135。（PDF pp.5–6）
- **[实验支持]** AnoShift FAR split 上，AUROC 从 MLP 0.208 提至 0.424（+0.216）。（PDF p.6, Table 2）
- **[实验支持]** 消融显示 MSL P-15 的 MLP+TTA-only F1 为 0.019，而 DT+TTA 为 0.440，说明趋势适配与模型更新组合比单独更新稳定。（PDF p.7, Table 3）
- **[证据边界]** CreditCard 漂移小、收益小；WADI 仍困难。F1-PA 与逐点 F1 不同；基线阈值用测试标签最优值、本文用训练分数阈值的比较口径并不完全一致。（PDF pp.5–7, Appendix pp.11, 15）

## 8. Limitations

- **[作者明确讨论]** 测试阈值选择困难；异常定义因场景而异；方法假设测试流中正常样本更多。作者提出可用主动学习获得部分标签。（PDF p.7）
- **[实验报告问题]** Appendix p.10 的 WADI TP/FP 数字、变化方向和百分比与 Table 12 不一致；不能据该段量化 WADI 的实际变化。（PDF pp.10, 15）
- **[分析推断]** 自训练反馈可能自我强化；没有显式 workload、发布、业务周期或 Trace 上下文，无法解释波动来源；数据集参数差异大、缺少长期遗忘/回滚和生产成本评估。

## 9. Research Opportunities

- **[分析推断]** 建立异常污染在线更新的稳定性测试，联合改变正常比例、故障持续时间、负载跃迁和阈值，测量适应速度、误报、漏报与遗忘。
- **[分析推断]** 用 workload、发布/扩缩容事件或 Trace 条件化多种正常模式，评估故障与负载变化共现时是否比纯 EMA/伪标签更新可靠。
- **[证据缺口]** 论文展示 t-SNE 与离线数据集结果，但未充分验证线上连续更新的延迟、回滚、跨服务迁移和高代价漏报情境。

## 10. Related Papers

- CAPMix：训练期合成异常、DTW 软标签和双空间 Mixup；本文在测试期以趋势与模型更新适应新正常。两者均未解释业务波动的外部原因。（[CAPMix 笔记](../capmix/notes.md)）
- FITNESS：流式概念漂移相关路线，本文强调不依赖历史窗口缓存。（PDF p.2）
- CAROTS：待完整精读后比较其上下文建模和因果增强主张。

## Links

- 详细精读笔记：[notes.md](notes.md)
- 原始 PDF：[When Model Meets New Normals PDF](../../sources/papers/tsad-2024-2026/2024/AAAI/When_Model_Meets_New_Normals_Test_Time_Adaptation_for_Unsupervised_Time_Series_Anomaly_Detection.pdf)
