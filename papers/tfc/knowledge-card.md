# 知识卡片：TFC（Temporal–Frequency–Curvature Fusion）

> 标签：**[作者主张]** 为作者提出的观点 / 结论；**[实验支持]** 为实际表格、消融或数据设置支持的内容；**[分析推断]** 为知识库的解释与研究判断。

## 1. Research Scenario

- **[作者主张]** 检测数值范围正常、但局部形状、趋势弯折或周期驱动力已变化的 pattern-wise 时序异常。（PDF §§1–2）
- **[实验支持]** 六个基准 AIOPS、WSD、Yahoo、NAB、UCR、TODS；模型按每条单变量序列分别训练。（PDF §4; Appendix B–C）

## 2. Core Challenges

- **[作者主张]** 平滑型 prediction / reconstruction 容易削弱低幅度形态变化；异常时长多尺度；二阶曲率也会对 benign oscillation 和高频噪声敏感。（PDF p.2, §1）

## 3. Existing Limitations

- **[作者主张]** 单看 point residual 可能漏掉连续值合理的斜率 / 轨迹机制变化；固定 receptive field 难同时适配尖峰、shapelet 与慢趋势。（PDF §§1–2）
- **[分析推断]** 状态空间动机引入外生变量 $u_t$，但模型只使用单变量观测信号，不验证 business context 或机制来源。

## 4. Core Idea

- **[作者主张]** 将 TSAD 证据拆为 temporal value、frequency spectrum、second-difference curvature；曲率多跨度读取后先与频率 cross-attend，再由逐时 expert router 与 temporal embedding 融合。（PDF §§2–3.4, Eqs. 5–19）

## 5. Technical Innovations

1. **[作者主张]** 离散二阶差分放大斜率变化点，并具有 $-4\sin^2(\omega/2)$ 的频率响应。（Propositions 2.1–2.3, Eqs. 7–9）
2. **[作者主张]** FFT 频谱切成 $K$ 带，经 mask / IFFT 形成分带时间表示，再由 MHA 混合。（§3.1, Eqs. 10–11）
3. **[作者主张]** Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度。（§3.2, Eqs. 12–16）
4. **[作者主张]** 两阶段融合：$H_{fc}=\mathrm{CrossAttention}(F,C)$，再 $\hat Y=\alpha(x)H_{fc}+(1-\alpha(x))H_t$。（§3.4, Eqs. 18–19）

## 6. Key Mechanisms

- **[作者主张]** frequency cues 用于校准曲率对正常周期波动的误报敏感性；MSA 保留局部 shape / trend 变化；router 按输入调整 pattern 与 temporal 分支比例。
- **[分析推断]** “动态视角”表示变化几何的信号表征，并非动态识别 workload 状态或给出变化的业务成因。
- **[证据边界]** 论文未明确 score / loss 的最终映射公式；$κ_t$ 用中心差分要访问 $t+1$，temporal Transformer 也未描述 causal mask，不能假定零前视在线检测。（§§3–4, Eqs. 12, 17）

## 7. Experimental Evidence

- **[实验支持]** Table 1 的 TFC F1 / Event-F1：AIOPS .9406/.8235，NAB .9987/.9308，TODS .9481/.9231，UCR .8996/.6289，WSD .9883/.9315，Yahoo .9741/.9618。（PDF p.6, Table 1）
- **[实验支持]** Event-F1 六列领先；AIOPS 普通 F1 .9406 低于 POLY .9550，故不能说每个数据集每个指标都第一。（Table 1）
- **[实验支持]** Table 2 中 CP w/o MSA / CP / TFC with MHA / TFC 的消融整体支持多视角与 MSA 作用；Table 2 TODS TFC 为 .9258/.9155，与 Table 1 .9481/.9231 不一致，引用时需注明表号。（PDF pp.7–8, Table 2）
- **[实验支持]** 五随机种子、窗口敏感性、单个 AIOPS 约 140k 样本推理成本测试；固定阈值线上误报和 workload 与故障并发没有评测。（Appendix C; §§4.6–4.7）

## 8. Limitations

- **[作者未单列]** 正文没有 Limitations 章节。
- **[分析推断]** 曲率同样会增强正常振荡 / 噪声；frequency cross-attention 不等于识别振荡的业务来源。
- **[方法边界]** 独立单变量模型不利用跨指标依赖、Trace / release / workload；state-space 外生驱动只在动机中定义。
- **[在线边界]** centered second difference 依赖下一点；模型因果性与告警延迟未被说明。
- **[复现边界]** Main paper 未写出精确 scoring / training loss / threshold 机制；Best-F1 需阈值优化，缺少无标签固定门限的告警成本结果。

## 9. Research Opportunities

- **[分析推断]** 加入负载、发布和 Trace 条件，验证“波形机制变了”是否能进一步区分合法业务变化与故障。
- **[分析推断]** 将 causal / one-sided curvature 与中心差分、离线 Transformer 对照，量化前视延迟对在线告警的影响。
- **[分析推断]** 构造正常周期切换与并发故障的受控数据，测试 frequency branch 是否校准掉真实异常证据。
- **[分析推断]** 公开固定阈值、PR-AUC、Event-F1、误报周期和事件时延，核验 Best-F1 优势能否转成运行收益。

## 10. Related Papers

- **MACE / TFMAE / Tri-domain solution**：都使用时频证据；TFC 的突出点是额外显式建模二阶曲率并做曲率—周期跨注意力。
- **TShape**：也聚焦 shapelet 异常，TFC 以二阶差分与 span attention 表示形状，不是同一种形状原型方法。
- **CrossAD**：CrossAD 学粗到细尺度重构映射，TFC 多视角属于同一信号的时 / 频 / 几何表征。
- **CCM-TAD**：CCM-TAD 做多变量通道聚类和时间因果 mask；TFC 是逐序列 univariate 且未来点使用边界值得关注。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[TFC PDF](../../sources/papers/tsad-2024-2026/2026/KDD/KDD26-Rethinking%20Time%20Series%20Anomaly%20Detection%20from%20a%20DynamicPerspective-%20Temporal–Frequency–Curvature%20Fusion.pdf)
