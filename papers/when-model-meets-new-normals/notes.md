# When Model Meets New Normals：无监督时序异常检测的测试时适应

## 1. Metadata

- Title: When Model Meets New Normals: Test-Time Adaptation for Unsupervised Time-Series Anomaly Detection
- Authors: Dongmin Kim, Sunghyun Park, Jaegul Choo
- Year / Venue: 2024 / AAAI
- CCF: A（采用已人工确认的论文清单等级）
- Local PDF: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/AAAI/When_Model_Meets_New_Normals_Test_Time_Adaptation_for_Unsupervised_Time_Series_Anomaly_Detection.pdf)
- Publisher: [AAAI proceedings PDF](https://ojs.aaai.org/index.php/AAAI/article/download/29210/30283)
- Code: 论文正文和附录未提供本文实现仓库链接；给出了 Anomaly Transformer、OmniAnomaly、Telemanom 等基线/数据来源链接。
- Knowledge Card: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

本文在冻结的无监督异常检测器上增加两个测试时组件：先用指数移动平均跟踪并去除输入趋势，再仅以检测器预测为正常的点做在线重构训练，使模型可以顺应测试流中出现的新正常状态，同时降低旧正常模型持续误报的风险。（PDF pp.1–4, Method, Eqs. (2)–(4), Algorithm 1）

## 3. Problem Definition

输入为多变量序列 $D=\{X_1,\dots,X_N\}$，每个 $X_t\in\mathbb R^F$；异常检测器为每点输出异常分数 $A(X_t)$，分数大于阈值 $\tau$ 时告警。无监督训练先从训练序列学习正常分布 $P_{train}$，再面对连续到来的测试序列。作者将 $P_{train}\ne P_{test}$、且测试期正常数据分布本身改变的情形称为 **new normal problem**。仅依赖历史训练集的检测器可能把测试期合法的新状态当异常，造成连续误报。（PDF pp.1, 3, Introduction / Problem Statement）

每个时点以长度 (w) 的窗口表示：

\[
X_{w,t}=[X_{t-w+1},\ldots,X_t],\qquad
Y_{w,t}=[y_{t-w+1},\ldots,y_t].
\]

论文实验主要使用重构型异常检测器，具体主干是 MLP autoencoder；测试时以窗口内逐点重构误差产生分数和二元预测。方法作为测试阶段的趋势归一化与参数更新模块提出，作者表示可接到其他检测器上，但主要完整对比实验采用 MLP。（PDF pp.3–5）

## 4. Motivation and Technical Challenge

训练正常状态会随负载、运行条件和时间变化。固定模型常会在均值/趋势转变后持续产生较大的重构误差；Fig. 1 用 SWaT 展示训练与测试分布差异及误报现象。作者用 NeurIPS-TS-UNI 合成趋势突变说明：即使底层动态没有变化，单独的趋势跳变也可能让观测看起来异常。另一方面，Yahoo-A1-R20 的训练/测试差异不只是趋势，故只减去趋势不能捕捉全部动态变化，需要模型更新。（PDF pp.1–3, Figs. 1–2）

挑战在于测试流没有标签且可能含真实异常：若把全部测试点用于自适应，异常样本可能污染模型。作者据此采用两种互补筛选逻辑：趋势 EMA 使用每个输入窗口的观测均值；参数更新只使用模型预测为正常的点。方法的前提是测试流中的正常点占多数、初始检测器有能力筛掉一部分明显异常。（PDF pp.3–4, § Method, Eq. (4)）

## 5. Existing Methods and Their Limitations

- **冻结的重构、聚类与预测检测器**：正常性模型由训练数据定义，遇到分布漂移时误差分数会因合法的新趋势而增加；模型“留在过去”。（PDF pp.1–3, Introduction, Fig. 1）
- **单纯趋势归一化**：可抵消均值/趋势位移，却不能学习趋势以外的动态结构变化；Fig. 2(b) 以 Yahoo-A1-R20 说明这一点。（PDF p.3, Fig. 2）
- **将测试样本全部用于 TTA**：本文认为在异常检测中不安全，异常可能反过来破坏检测器；因此用预测标签筛选参数更新样本。（PDF pp.2–4, Related Works / Method）
- **历史缓存型流式更新**：作者将自己的方案与依赖历史数据窗口的 FITNESS 区分，主张本方法只保留参数和趋势状态、即时处理后即可淘汰当前输入。（PDF p.2, Related Works）
- **阈值与标签定义**：逐场景异常标准并不统一；测试分布里“与训练不同”的点可能是新正常，也可能是真异常，单靠分布差异无法判定。（PDF p.7, Discussion and Limitation）

## 6. Core Idea and Architecture

```text
已用训练正常数据拟合的重构检测器 fθ
       ↓ 测试流窗口 Xw,t
EMA 估计当前趋势 μt ← 窗口均值更新
       ↓
输入去趋势 Xw,t − μt → 重构 → 加回 μt → 逐点异常分数 A(Xw,t)
       ↓ 与阈值 τ 比较得到预测掩码 Ŷw,t
仅保留预测正常位置的重构损失 → 在线梯度更新 θ
       ↓
处理下一个窗口（保留 θ、μt；不需要训练数据或标签）
```

这是加在已有模型**推理路径**上的适配策略，不是新的检测器结构。每个窗口先计算异常分数，随后才用预测掩码选择可训练位置更新参数；分数是更新前模型在当前窗口上的预测。（PDF pp.3–4, Fig. 3, Algorithm 1）

## 7. Method: Components and Training/Inference

### 7.1 趋势估计与去趋势输入（DT）

窗口经验均值为：

\[
\hat\mu_t=\frac{1}{w}\sum_{i=t-w+1}^{t} X_i.
\]

趋势以 EMA 递推：

\[
\mu_t=\gamma\mu_{t-w}+(1-\gamma)\hat\mu_t, \tag{2}
\]

\(\gamma\) 控制历史趋势保留和对新窗口的响应速度。模型处理去趋势窗口 $X_{w,t}-\mu_t$，重构输出再加回估计趋势。作者把这解释为均值调整形式的非平稳趋势消除，目标是处理均值/趋势迁移并保持模型输入数值较稳定。（PDF pp.3–4, Fig. 3, Eq. (2)）

趋势估计阶段使用整个观测窗口的均值；论文认为这样即使新状态偏离较大，也可以及时跟踪趋势。窗口里若混入异常，该均值也会受到影响，这是由该更新规则直接带来的风险。（PDF p.4）

### 7.2 基于预测正常点的自监督参数更新（TTA）

模型参数按在线梯度下降更新：

\[
\theta\leftarrow\theta-\eta\nabla_\theta
\mathcal L(X_{w,t},\hat Y_{w,t},\mu_t,\tau), \tag{3}
\]

其中 \(\eta\) 是测试时学习率，\(\hat Y_{w,t}\) 是检测器当前预测的逐点正常/异常标签。重构型检测器的掩码损失写为：

\[
\mathcal L=(1-\hat Y_{w,t})^\top(\hat X_{w,t}-X_{w,t})^2. \tag{4}
\]

逐点预测正常的位置贡献重构损失，预测异常的位置被屏蔽，因此不用测试真值标签；更新使用的是在线 SGD（无 momentum）。Algorithm 1 的顺序是：更新 EMA → 计算分数 → 用 \(\tau\) 生成异常掩码 → 掩掉异常点 → 梯度下降更新参数。作者让趋势状态从全体窗口更新、让参数仅从预测正常位置更新，目的分别是跟随总体趋势和避免直接用异常训练。（PDF pp.4, 10, Eq. (3)–(4), Algorithm 1）

### 7.3 推理数据流和假设

主文设测试窗口顺序到达；实验按数据集用非重叠窗口或相应步幅。输入处理后可淘汰，在线保留模型参数及趋势估计状态。阈值 \(\tau\) 决定更新掩码，故误报和漏报都会影响学习样本：误报会阻止新正常进入参数更新；漏报会让异常样本参与更新。算法依赖“测试集中正常数据更多”的假设，而不是经人工确认的伪标签。（PDF pp.2, 4, 10–11, Algorithm 1, Table 4）

## 8. Experimental Setup

### 8.1 数据集

主实验选取九个数据/实体，目标是覆盖分布漂移明显和较小的场景：SWaT、WADI、SMD 的 M-1-4 与 M-2-1、MSL P-15、SMAP T-3、CreditCard、Yahoo A1-R20 与 A1-R55。训练集与测试集按原数据切分；Yahoo 每个序列前 400 点训练、其余测试；SMD 以机器序列前后半段拆分。CreditCard 的 PCA 特征已匿名化。作者把 CreditCard 作为分布漂移较小的对照。详细样本数、窗口、步幅和特征数列在 Appendix Table 4 / Table 6。（PDF pp.4–5, 11, Experiment Setups / Appendix）

### 8.2 基线、指标和复现设置

检测器基线为 MLP autoencoder、LSTM encoder-decoder、USAD、THOC 与 Anomaly Transformer。除 Anomaly Transformer 使用官方实现外，LSTM、USAD、THOC 按原论文结构重实现。测试时的完整方法主要包在 MLP autoencoder 上。五次独立运行报告均值，补充材料给出置信区间。（PDF pp.4–7, 16, Table 1, Table 13）

指标包括逐点 F1、point-adjusted F1（F1-PA）、AUROC、AUPRC。作者提醒 F1-PA 将连续异常段内任何命中都算作整段检出，会高估逐点分类效果，因此同时提供逐点指标和阈值无关曲线面积。（PDF p.5, Evaluation Metrics）

阈值选择是比较中的重要细节：作者主张线上阈值应仅从训练分数统计确定，不应使用完整测试集找“最佳”阈值；附录详细表则将基线的 \(Q^*\)（用测试标签最大化 F1）与本文方法基于训练分数分位数的阈值并列报告。因此 Table 1 的跨模型结果需连同这一协议差异理解，不是完全统一阈值规则下的部署比较。（PDF pp.7, 11, Appendix Detailed Results）

另在 AnoShift 基准上测试 NEAR（2011–2013）与 FAR（2014–2015）时间划分，按 AUROC、以 inlier 为正类的 AUPRC-in 和以 outlier 为正类的 AUPRC-out 比较，侧重长期时间漂移鲁棒性。（PDF p.6, Table 2）

## 9. Main Results and Ablations

### 9.1 主结果

Table 1 显示，完整策略相对 MLP 基线在多个强漂移数据集有较大提升：

| 数据集 | 指标 | MLP | MLP + 本文方法 | 观察 |
|---|---|---:|---:|---|
| SWaT | F1 / AUROC | 0.765 / 0.832 | 0.784 / 0.892 | 提升有限但两个指标改善；AT 的 F1-PA 更高 |
| SMD M-1-4 | F1 / AUPRC | 0.273 / 0.169 | 0.463 / 0.354 | 逐点和不平衡指标均改善 |
| MSL P-15 | F1 / AUPRC | 0.263 / 0.061 | 0.440 / 0.575 | AUPRC 增益最大的一组之一 |
| Yahoo A1-R20 | F1 / AUROC | 0.067 / 0.367 | 0.678 / 0.971 | 新正常漂移下提升很大 |
| Yahoo A1-R55 | F1 / AUROC | 0.366 / 0.916 | 0.633 / 0.958 | 检测分数排序及 F1 改善 |
| CreditCard | F1 / AUROC | 0.127 / 0.943 | 0.135 / 0.943 | 漂移较小时收益很小 |
| WADI | F1 / AUPRC | 0.131 / 0.052 | 0.148 / 0.081 | 有改善但绝对 F1 / AUPRC 仍低，且与 USAD 等的比较受阈值协议影响 |

来源：PDF pp.5–6, Table 1。结果支持作者关于新正常场景适应有用的主张，但不足以说明无论状态和基线都占优：例如 SWaT 的 F1-PA 上 Anomaly Transformer 得分更高；CreditCard 收益近乎没有；WADI 仍然困难。

AnoShift 上，MLP + 本文方法相对 MLP 在 NEAR 与 FAR 的 AUROC 分别增加 0.194、0.216；FAR 的 AUPRC-in / out 分别增加 0.173 / 0.081。结果与“漂移越严重，适应价值越明显”的解释一致，但不是生产业务变更与故障共现的验证。（PDF p.6, Table 2）

### 9.2 消融：趋势与模型更新互补

Table 3 比较 MLP、MLP+DT、MLP+TTA、MLP+DT+TTA。完整方法在三个展示数据集的主要指标上最好或接近最好：MSL P-15 的 F1 从 MLP 0.263、DT-only 0.221、TTA-only 0.019 提升到 0.440；AUPRC 从 0.061 提升到 0.575。TTA-only 在 MSL 上显著退化，说明缺少趋势跟踪时，参数更新可能被旧趋势/不适当样本牵制；DT 处理可预测的均值/趋势项，TTA 学习剩余动态变化，二者组合更可靠。SMD M-2-1 完整方案 F1 0.249、F1-PA 0.974、AUROC 0.764、AUPRC 0.280；各单模块提升并不完全一致，收益依数据集而异。（PDF pp.6–7, Table 3, Figs. 7–8）

### 9.3 阈值和异常段表现

作者指出，测试标签调阈值不符合真实无监督部署；Supplement 的逐点混淆矩阵也显示 point-adjusted 指标可把一段内部分命中扩展为整段命中。比如 SWaT 的完整方法在某训练分数阈值下逐点 F1 为 0.783、point-adjusted F1 为 0.902。应分开看排序质量（AUROC/AUPRC）、阈值选择与事件级宽容指标。（PDF pp.5, 7, 15, Table 12）

**来源数字内部不一致：** Appendix p.10 的 WADI 文字称误报从 102,824 降至 75,076（并称降低 73%），真阳性从 8,122 增至 3,248（并称增加 28%）；数字之间百分比不成立，TP 数值方向也与“增加”相反。Appendix Table 12 的 MLP $Q^*$ 行确有 FP=102,824、TP=8,122；本文方法 Q99.9 行则为 FP=27,748、TP=3,248。文字中的 75,076 与此行不符。此处保留原文并标为不可调和的报告问题，不用推测值替换。（PDF pp.10, 15, Appendix visualization discussion / Table 12）

## 10. Contributions and Strengths

- 明确把测试期正常分布漂移抽象成 TSAD 的“新正常问题”，并通过趋势可视化和时间分割基准展现其影响。（PDF pp.1–3, 6）
- 把快速均值/趋势跟踪与在线参数学习拆成两个组件，机制简单，且可挂接已有重构检测器。（PDF pp.3–4）
- 更新掩码只使用模型预测正常的点，不需要测试标签或训练数据；消融显示趋势单独与 TTA 单独的短板及组合收益。（PDF pp.4, 7）
- 同时报告 F1、F1-PA、AUROC、AUPRC、多个漂移强度及补充混淆矩阵，讨论阈值和点调整指标偏差。（PDF pp.5–7, 11–17）

## 11. Limitations and Reproduction Value

### 作者明确讨论

- **测试阈值仍困难**：固定阈值要从训练分数选，合适工作点会影响真实告警表现；作者建议按训练统计选阈值，仍未解决应用成本相关的校准。（PDF p.7, Discussion and Limitation）
- **正常/异常标准存在不一致**：远离训练分布的测试状态未必就是异常；作者假设测试流中正常点较多，建议探索对部分数据做主动标注。（PDF p.7）
- **新正常和上下文异常纠缠**：附录认为 SMD M-1-4、MSL P-15 和 Yahoo 的测试异常在可视化中与测试正常难区分；模型适应可降低误报，但 WADI 的真阳性/误报权衡需要结合业务代价解释。（PDF p.10）

### 基于方法与实验的分析

- 参数更新以自身预测为伪标签：漏掉的异常会进入训练集，错误告警的正常状态则被排除；若错误预测连续发生，可能形成自我强化或适应迟滞。实验没有给异常污染率、误报率与适应稳定性的系统曲线。
- EMA 对全窗口观测更新，突发故障或工作负载激增会直接改变趋势状态；模型更新只靠异常阈值屏蔽，两条更新路径对同一异常的容忍策略不同。论文没有专门测试“负载变化与故障同时发生”或延迟异常的安全边界。
- 该方法能学习变化后的统计正常形态，但不读取部署、负载、业务周期、Trace 或事件日志；它没有解释波动来源，也不做故障归因。
- 测试时 \(\eta,\gamma\) 和阈值分位数按数据集设定，补充表中的 \(\gamma\) 从 0.1 到 0.99999，\(\eta\) 从 0.001 到 1.0。需预先选择适合流长和动态速度的参数，自动选参及跨环境迁移未验证。（PDF pp.11–13, Tables 4, 6）
- 论文没有报告完整方法在不同吞吐/硬件下的在线延迟、更新成本或长期遗忘评估；其计算成本表比较的是基础检测器。（PDF p.12, Table 5）
- 数据集描述有一个需核实处：正文 p.4 写 SMAP 有 55 个通道、MSL 有 27 个；补充 Table 4 对选取的 MSL P-15 / SMAP T-3 分别列 55 / 25 个特征，可能是总数据描述与子序列预处理口径差异，文中未解释。

### 复现价值

算法只有 EMA、推理分数掩码和一次 SGD 更新，概念实现门槛低；附录提供数据窗口/步幅、各数据集 \(\eta,\gamma\)、基线超参数及详细结果。限制是 PDF 未提供作者仓库，基线里部分实现是重写，且阈值协议与 WADI 报告数字需先澄清。应先固定数据切分和阈值协议，再复现 DT/TTA 消融，避免把测试标签选阈值的结果误认为真实在线效果。（PDF pp.4–7, 11–17）

## 12. Relationship to Other Knowledge

- 与 CAPMix 的互补关系：CAPMix 在训练期处理合成异常的标签可信度和判别边界；本文在测试期处理正常分布漂移，通过 EMA 与伪正常在线更新跟随新状态。二者分别作用于训练监督和部署后模型状态，仍都主要依赖 KPI/序列自身形态而不解释业务变更来源。（CAPMix PDF pp.3–6；本文 PDF pp.3–4）
- 与 FITNESS（Sankararaman et al., ICML 2022）的关系：都处理流数据漂移，但本文强调不需历史滑动缓存，以趋势状态和当前参数适应。（PDF p.2）
- 与后续阅读的 CAROTS：待完整阅读后比较是否显式条件化正常状态或引入更结构化的时间上下文；目前不预判方法结论。

## 13. My Understanding

本文的重要判断是：训练集正常不代表服务永远只有同一套正常状态。趋势 EMA 把低频/均值变化显式分离出来，在线更新再学去趋势后仍变化的动态。这个分解对处理正常状态漂移有清楚作用路径；但“由 detector 判正常”本身不等于可信标签，且 EMA 会看见所有窗口。如果监控器把实际故障当成新正常，系统可能为了适应而降低对此类异常的敏感度。将负载、发布事件等上下文引入正常状态判断，是与本文相关但尚未由其验证的方向。

## 14. Questions

1. 阈值和伪标签如何在不同正常比例、不同异常持续时间下共同校准？检测器连续漏报后，如何避免异常污染参数？
2. 能否对 EMA 更新和模型梯度更新使用不同的稳健统计量，降低尖峰故障对趋势估计的影响？
3. 多种业务状态如何区分为已知正常模式、状态切换和真实故障？加入 workload、发布、Trace 等上下文能否减少自我强化误差？
4. 在固定告警成本、不访问测试标签及跨服务迁移时，性能是否仍成立？在线更新的延迟、回滚和遗忘边界如何量化？
5. WADI 附录文字与 Table 12 的 TP/FP 计数分别对应什么阈值及口径？正文和附录对 MSL/SMAP 特征数的口径是否不同？

## 15. Related Work

- USAD、Anomaly Transformer、THOC、LSTM encoder-decoder：本文复用/对比的无监督序列检测器。（PDF pp.4–6）
- FITNESS：流式漂移适应相关工作，本文强调不访问历史缓存。（PDF p.2）
- AnoShift：本文采用其 NEAR/FAR 划分测试时间漂移鲁棒性。（PDF p.6）
- CAPMix：本知识库中训练期合成异常与软标签鲁棒化的对照路线，链接见上节。

## 16. Tags

`TSAD` `test-time-adaptation` `distribution-shift` `new-normal` `EMA` `detrending` `online-learning` `reconstruction` `thresholding` `contextual-anomaly`
