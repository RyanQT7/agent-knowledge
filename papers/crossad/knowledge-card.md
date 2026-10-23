# 知识卡片：CrossAD

> 根据本地 27 页 NeurIPS 2025 PDF 全文和附录整理。标记含义：**[作者主张]** 原文提出的动机或结论；**[实验支持]** 表格、消融或实验直接支持的结果；**[分析推断]** 本知识库的跨论文解释或待验证判断。

## 1. Research Scenario

- **[作者主张]** 无监督多变量时间序列异常检测，目标是在多种时间分辨率下检测点异常和子序列异常。（PDF pp.1–4, §§1, 3）
- **[实验支持]** SMD、MSL、SMAP、SWaT、PSM、GECCO、SWAN 七个测试集；另有 UCR 250 子集和 TSB-AD 补充基准。（PDF pp.7–9, 21, 24–25）

## 2. Core Challenges

- **[作者主张]** 多尺度方法常分别建模或简单融合，不显式学习粗粒度到细粒度的正常映射；固定滑窗限制窗口外上下文。（PDF pp.2–3, Fig. 1）
- **[作者假设]** 正常期的跨尺度映射可从训练序列学习，异常会因各尺度敏感性不同而破坏这种映射。（PDF pp.4–5, §3.2）

## 3. Existing Limitations

- **[作者主张]** 独立尺度建模、特征融合与局部滑窗使已有模型难以捕捉跨尺度关联和窗口间共享上下文。（PDF pp.2–3）
- **[分析推断]** 原型上下文记住重复子序列的统计相似性，不自动提供模式含义，也不区分高负载业务波动和故障。

## 4. Core Idea

- **[作者主张]** 从粗尺度重建细尺度来拟合正常的跨尺度关系；从每个窗口用周期感知 query 抽取多尺度子序列表示，聚合成全局原型并在 decoder 中提供窗口外上下文。（PDF pp.4–7, §§3.2–3.3）

## 5. Technical Innovations

1. **Cross-scale reconstruction**：目标为所有尺度的平方重构误差和；用更粗尺度条件预测更细尺度。（Eq. 1, Eqs. 4–6）
2. **Scale-Independent Mask**：encoder 的 attention mask 为块对角矩阵，只允许同一尺度内部注意力。（PDF p.5, Eqs. 2–3）
3. **Cross-scale Mask decoder**：尺度对齐后按粗到细关系解码，避免将跨尺度关系留给隐式 feature fusion。（PDF pp.5–6, Fig. 2, Eqs. 4–6）
4. **Period-aware query router**：保留 Fourier 幅度 top-k 成分，逆变换后经 MLP 和 Gumbel-Softmax 激活 learnable sub-series queries。（PDF pp.6–7, Eqs. 7–9）
5. **Global multi-scale prototypes**：将窗口表示分配到最近欧氏距离原型并用 EMA 更新，作为 decoder 全局上下文。（PDF p.7, Eqs. 10–11; Appendix A）
6. **Multi-scale score fusion**：每个尺度的平方残差插值回原时间轴并取平均；采用 SPOT 阈值。（PDF p.7, §3.4, Eq. 12）

## 6. Key Mechanisms

- **[分析推断]** 异常信号不是单纯“值离正常范围远”，而是细粒度观测无法由正常粗粒度上下文映射出来。
- **[作者主张]** 不同窗口中相似子序列可由查询库抽取并汇入原型，缓解窗口边界造成的上下文缺失。（§3.3）
- **[证据边界]** 正文强调训练期原型更新；附录 Algorithm 1 写“每个新窗口”，测试时是否更新未明确，不能据此断言它提供安全在线适应。（PDF p.7; p.21）

## 7. Experimental Evidence

- **[实验支持]** 主表 VUS-ROC/VUS-PR：SMD 0.8580/0.2344、MSL 0.8091/0.3144、SWaT 0.7865/0.4767、PSM 0.7302/0.5596、GECCO 0.9948/0.6211；SWAN VUS-PR 0.9171 高于 TimesNet 0.9160，但 VUS-ROC 0.9499 略低于 TimesNet 0.9515。（PDF pp.8–9, Table 1）
- **[实验支持]** 消融平均 VUS-PR：单尺度 0.3665，多尺度 0.3962，加跨尺度重构 0.4326，加由 encoder 表示更新的上下文 0.4597，完整模型 0.4984。（PDF p.9, Table 3）
- **[实验支持]** Fig. 4–5 展示跨尺度残差在 shapelet、seasonal、trend 等模式下比传统重构更稳定；属于可视化案例，不是因果归因或显著性检验。（PDF pp.10–11）
- **[实验支持]** 查询数 / 原型数的最优值随数据集变化；单一统一设定不是所有数据的最优值。（PDF pp.22–24, Tables 7–8）
- **[作者主张与数据差异]** 正文声称主实验所有数据集 VUS 指标全面领先；SWAN 的 VUS-ROC 表格值并非领先，应按具体表项引用。消融增幅文字和表值重算也有小幅差异。（PDF pp.8–10, Tables 1, 3）

## 8. Limitations

- **[作者明确讨论]** 查询库大小与全局原型数量的最优值随数据集变化，但论文使用统一参数。（PDF p.25, Appendix G）
- **[实验 / 方法边界]** MSL/SMAP 只用首个连续维度；主实验未显式把 workload、发布、Trace 或运维事件作为条件输入。（PDF p.7, §4.1）
- **[分析推断]** 原型是潜在多尺度统计模式，并未被标注为业务运行状态；重构异常也没有解释波动来源。跨尺度映射变化时，新正常可能升高分数。
- **[证据边界]** SPOT 自动阈值结果未等于按告警成本评估的线上效果；正文 / 附录对原型更新发生阶段的描述存在歧义。（PDF pp.7, 21）

## 9. Research Opportunities

- **[分析推断]** 在多负载、多运行模式及故障叠加数据中，显式提供 workload / deployment / trace 上下文，验证模式原型能否识别合法状态切换。
- **[证据缺口]** 比较冻结、延迟更新和带置信校验的在线原型更新，测量新正常适应速度、故障吸收率、误报成本和恢复能力。
- **[分析推断]** 与 CAROTS 的跨变量依赖建模组合，分离“跨时间尺度映射被破坏”和“跨变量预测关系被破坏”的贡献。
- **[证据缺口]** 将查询和原型与可审计业务状态标签对齐，验证其可解释性，而非仅用检测分数验证聚类效果。

## 10. Related Papers

- [CAPMix](../capmix/notes.md)：训练期伪异常形态增强 + DTW 软标签；CrossAD 以无监督重构学习尺度映射。
- [When Model Meets New Normals](../when-model-meets-new-normals/notes.md)：测试期 EMA 与伪正常更新；CrossAD 的窗口原型不能直接视为 TTA。
- [CAROTS](../carots/notes.md)：建模跨变量 Granger 预测依赖；CrossAD 建模单序列跨时间尺度映射，关系对象不同。
- **待读**：Learning Multi-Pattern Normalities in the Frequency Domain；重点比较其“多模式正常性”是否具有状态语义，与 CrossAD 的频域路由和统计原型如何区分。

## Links

- 详细精读笔记：[notes.md](notes.md)
- 原始 PDF：[CrossAD PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf)
- 作者代码：[CrossAD GitHub](https://github.com/decisionintelligence/CrossAD)
