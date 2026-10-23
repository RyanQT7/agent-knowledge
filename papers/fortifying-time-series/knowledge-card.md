# 知识卡片：Fortifying Time Series

> 根据本地 25 页论文及补充材料整理。标记：**[作者主张]** 原文结论；**[实验支持]** 表格 / 实验直接支持；**[分析推断]** 本知识库分析。PDF 同时标有 NeurIPS 2025 与 arXiv:2605.07690v1（2026-05-08），元数据版本见精读笔记。

## 1. Research Scenario

- **[作者主张]** 安全关键时序异常检测中的白盒对抗鲁棒性；覆盖 evasion（异常逃逸）和 availability（正常样本被误报）两类扰动。（PDF pp.1–4, §§1, 3.1）
- **[实验支持]** COUTA、TimesNet、DeepSVDDTS；SMAP、MSL、SMD、SWAN、CREDITCARD、WATER、UCR-1、UCR-2 表列基准。（PDF pp.7–8, 24）

## 2. Core Challenges

- **[作者主张]** 对时序数据，逐点 $\ell_p$ 范数不能表达时间移动、拉伸和压缩带来的形态相似性；已有 $\ell_p$ 认证防护对 DTW 攻击不充分。（PDF pp.1–3, Fig. 1）
- **[作者目标]** 为 anomaly score detector 提供 DTW 半径内的形式化分类不变性保证。（PDF pp.3–6, §3, Theorem 3.3）

## 3. Existing Limitations

- **[作者主张]** 经验防御可能被自适应攻击绕过；已有认证大多使用与时序形变不匹配的 $\ell_p$ 威胁模型。（PDF pp.2–3）
- **[分析推断]** DTW 认证解决的是对抗决策稳定性，不覆盖业务负载变化的合法性识别，也不自动证明原预测是正确的。

## 4. Core Idea

- **[作者主张]** 对任意预训练 anomaly score 做 Gaussian percentile smoothing，先从高斯平滑的分位边界得到 $\ell_2$ 半径 $r$，再用 Keogh DTW lower bound 得到认证半径 $e$。（PDF pp.4–6, Eqs. 4–10）
- **[分析推断]** 这是通用推理期 wrapper / safety certificate，不是新的 TSAD 表示学习模型。

## 5. Technical Innovations

1. **Percentile smoothing**：$h_p(x)=\sup\{u:P[f(x+\eta)\le u]\le p\}$，针对异常分数无界、高方差改用分位数而非均值平滑。（PDF p.4, Eq. 4）
2. **Monte Carlo confidence bounds**：排序 $n$ 次扰动分数，以二项分布 order-statistic 界估计分位上下界；实验置信度 $1-\alpha$，$\alpha=10^{-3}$。（PDF p.7, Eq. 11）
3. **Keogh bridge**：用 envelope $U_i,L_i$ 构造 DTW 下界，再将 $\ell_2$ 半径转换成 DTW radius。（PDF pp.5–6, Eqs. 6–10）
4. **Closed-form certificate**：若 $r\le R$，$e=0$；否则 $e=\sqrt{M^2+r^2-R^2}-M$，其中 $R$ 汇总包络 slack，$M$ 为最大逐点 slack。（PDF p.5, Theorem 3.3）
5. **Model-agnostic wrapper**：无需修改预训练 detector 的训练阶段；对噪声扰动分数求 percentile 并输出平滑预测和证书。（PDF pp.6–7, §3.3, Fig. 2）

## 6. Key Mechanisms

- **[作者主张]** 异常分数的分位 margin 越远离阈值，输入 $\ell_2$ 半径可能越大；再由 DTW lower bound 将该证书转为形态对齐距离。（PDF pp.4–6）
- **[实验支持]** 增大 $\sigma$ 通常提升证书半径和非零证书比例，但过大可能降低 F1 / AUC。（PDF pp.8–9, Table 3）
- **[证据边界]** Keogh 下界保守；包络 slack 可使 $r\le R$，此时可计算到的正 DTW 半径为 0。（PDF p.5, Eq. 10; Appendix B）

## 7. Experimental Evidence

- **[实验支持]** DTW 攻击预算 1.0 下，COUTA + DTW 防护比 $\ell_p$ certified defense 在 MSL F1 +0.112、UCR-1 +0.187、SMD +0.072、WATER +0.102；AUC 也更高。（PDF pp.8–9, Table 2）
- **[实验支持]** WATER + DeepSVDDTS 在 Table 1 中非零证书率 99.46%、平均半径 0.189，F1 / ROC-AUC 未下降。（PDF p.8, Table 1）
- **[实验支持]** 不能概括成性能无损：CREDITCARD + COUTA 的 F1 .192→.003、ROC-AUC .900→.300；不同 detector 和数据集影响很大。（PDF p.8, Table 1）
- **[实验支持]** $\sigma$ 从 .1 增到 2 时 SMD 非零证书率 52.42%→94.66%，F1 .504→.315，显示证书—效用权衡。（PDF p.9, Table 3）
- **[实验支持]** 在 SMD / COUTA 中，$T=50,w=4$ 非零证书率 77.99%，$T=200,w=4$ 降为 41.05%；较大 DTW warping 窗口也通常削弱证书。（PDF p.25, Appendix F, Table 7）

## 8. Limitations

- **[作者明确讨论]** Monte Carlo 推理开销高；未来方向包括高效采样、自适应噪声和更紧的 DTW lower bound。（PDF p.9, §5）
- **[实验 / 方法边界]** Table 1 对“minimal trade-offs”的总述不适用于所有行；存在严重 F1/AUC 下跌和低证书比例。（PDF p.8）
- **[分析推断]** 鲁棒证书保证平滑分类在指定 DTW 球内不变，不等于原判断正确，不解释异常来源，也不保证遇到新业务运行态仍然适应良好。
- **[范围边界]** DTW 扰动是否符合具体系统语义要按领域验证；时间偏移本身有时就是故障。主文没有 workload、Trace、发布 / 业务状态条件化实验。

## 9. Research Opportunities

- **[证据缺口]** 以真实业务时序事件验证 DTW 扰动语义，校准 $w$、半径和“时间形变仍语义等价”的假设。
- **[分析推断]** 联合报告 certificate coverage、正确性、误报成本、延迟、零证书比例，并按负载 / 工作状态分层，而不是只比较总体指标。
- **[证据缺口]** 评估新正常在线适应后能否重新认证；控制版本更新、训练 / 推理分布差异和阈值校准的证明边界。
- **[分析推断]** 使用更紧 DTW 下界减少 $e=0$ 样本，同时测算额外计算成本和实际攻击安全收益。

## 10. Related Papers

- [CrossAD](../crossad/notes.md)：学习正常跨尺度映射作为检测信号；本论文为检测器增加 DTW 对抗稳定证书。
- [CAPMix](../capmix/notes.md)：训练期合成异常与软标签处理边界鲁棒性；该论文在推理期通过随机平滑证明扰动不变性。
- [When Model Meets New Normals](../when-model-meets-new-normals/notes.md)：在线适应测试时正常分布；DTW certificate 是固定检测器的局部决策稳定性保证。

## Links

- 详细精读笔记：[notes.md](notes.md)
- 原始 PDF：[Fortifying Time Series PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf)
- 会议页面：[NeurIPS proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f2192666f094c0115f09162e8c66d67f-Abstract-Conference.html)
