# MACE：在频域学习多模式正常性以实现高效时序异常检测

## 1. Metadata

- Title: Learning Multi-Pattern Normalities in the Frequency Domain for Efficient Time Series Anomaly Detection
- Authors: Feiyi Chen, Yingying Zhang, Zhen Qin, Lunting Fan, Renhe Jiang, Yuxuan Liang, Qingsong Wen, Shuiguang Deng
- Year / Venue: 2024 / ICDE
- CCF: A（采用已人工确认的论文清单等级）
- DOI: [10.1109/ICDE60146.2024.00047](https://doi.org/10.1109/ICDE60146.2024.00047)
- Code: 论文 NeurIPS/ICDE-style checklist 称 supplementary material 提供代码和环境文件；本地索引没有可核验的稳定代码 URL。
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local File: [MACE PDF](../../sources/papers/tsad-2024-2026/2024/ICDE/Learning_Multi_Pattern_Normalities_in_the_Frequency_Domain_for_Efficient_Time_Series_Anomaly_Detection.pdf)

## 2. One-Sentence Summary

MACE 通过为每个服务 / 子集提取一组静态正常频率基，将样本投影到相应“正常模式子空间”，再以时域扩展短异常、频域阻碍高变化谱重构的双向 dualistic convolution 扩大正常与异常的重构差异；它缓解跨服务正常模式差异，但没有显式命名同一服务内部的业务运行状态。

## 3. Problem and Motivation

论文关注云服务监控中多服务的无监督异常检测。实际集群中的服务、机器或传感器正常分布各异：对一种正常模式而言是异常的形状，可能是另一服务的正常模式。为每个服务维护单独模型成本高；把所有服务塞进一个通用模型又可能只学到少数主导模式。作者另指出高流量实时性、RNN 难并行，以及 encoder-decoder 容易忽略短时点异常。（PDF pp.1–3, §I, Fig. 1）

MACE 的正常模式定义带有频域假设：对于每个服务，可从其正常训练窗口的 Fourier 频谱中找出若干经常出现、能覆盖主要正常性的 dominant bases；相对该子空间的重构偏差可用于识别异常。该机制按**服务 / 子集**选择参考，不等于显式利用 workload、deployment、业务日历或在线识别某服务当下处于何种状态。（PDF pp.4–7, §IV-C）

## 4. Core Idea and Architecture

```text
多服务 / 多子集监控窗口
  → 时域 DualisticConv：分别扩大上偏差 / 下偏差，再逐点平均
  → 按服务正常训练数据统计高频率 Fourier bases，建立正常频率子空间
  → Context-aware DFT 投影 + [谱系数, sin 基, cos 基] 频域表示
  → 双支路频域卷积自编码器（Peak / Valley DualisticConv）
  → Context-aware IDFT 还原为时间序列
  → 对两支路的逐点重构误差取最大值作为 anomaly score
  → SGD 最小化训练窗口重构误差，测试分数超过阈值判异常
```

论文把方法概括为四阶段：时域异常增强、时间到频率表示、频域自编码重构、逆变换回时域。其关键设计是“按正常模式决定频率基”和“上下偏差采用不同的对偶卷积”，频域稀疏性还减少需要处理的频率分量。（PDF pp.4–7, Fig. 2, §IV）

## 5. Method in Detail

### 5.1 Dualistic Convolution：同一算子在时域与频域承担不同作用

对长度 $L$ 的局部窗口，论文定义参数化卷积：

$$\operatorname{DualisticConv}_{\gamma}(x)=\left[\operatorname{Conv}_{1\times L}\!\left(\frac{x^{\gamma}}{\sigma},s\right)\right]^{1/\gamma},\quad \gamma\in\{2g+1:g\in\mathbb Z, g\ne0\},\;\sigma>0.\tag{2}$$

当 $\gamma>1$ 时为 peak convolution，令较大正偏差在汇总中更占主导；当 $\gamma<-1$ 时为 valley convolution，强调下偏差。$|\gamma|$ 越大，对窗口极端偏离越敏感；$\sigma$ 是防梯度爆炸的 scale 参数。原文将 $\gamma=1$ 视作退化到标准卷积。（PDF pp.4–5, §IV-B, Eq. 2, Fig. 3）

- **时域**：stride $s=1$。同一异常点进入多个相邻卷积窗后，会把异常影响扩散到接近 kernel length 的范围，从而突出易被 autoencoder 平滑掉的短时异常。上偏差和下偏差分别由 peak / valley 分支扩大，然后逐点平均后送往后续模式提取网络。它主要改变局部响应，不是给异常添加类别监督。（PDF pp.4–5, §IV-B, Fig. 3(b)）
- **频域**：stride 设为 kernel size，分段卷积近似从每段频谱幅值选取 max 或 min 组成 latent vector。作者假设异常谱有更高变化 / 更强长尾，极端幅值被选中后偏离频谱主体，导致异常 latent 更难重建；正常谱幅值相近，表示仍接近主体。（PDF pp.5–6, §IV-B, Figs. 3(c), 4(a)）

Table II 支持“所测异常振幅方差高于正常”的经验前提：SMD 为 4.55 vs 3.36，J-D1 为 12.38 vs 11.74，J-D2 为 15.64 vs 14.13。但差异大小因数据而变，也不代表所有真实故障的频谱都一定高方差。（PDF p.6, Table II）

理论 Theorem 1 假定频谱幅值联合服从高斯 $\mathcal N(\mu,\Sigma)$，讨论 dualistic convolution latent 到原窗口幅值的期望重构 gap 上界。作者推导上界主要受协方差对角项 / 振幅方差影响，正常幅值变化较小因而更容易从 latent 重构，异常变化大则重构更难。这个推理依赖高斯联合分布、双侧峰谷参数与异常/正常方差差异，不能当作对任意分布的普遍保证。（PDF pp.5–6, §IV-B, Definition 1, Theorem 1）

### 5.2 Context-aware DFT / IDFT：每个服务保留常见正常基

预处理时，作者对每个服务的训练窗口计算频谱，统计每个 Fourier base 出现在各窗口“前 $k$ 强信号”中的次数，再按出现频率选出 $k$ 个 base，形成该服务的 normal-pattern subspace。训练与测试阶段的 context-aware DFT 仅用对应子空间的 bases 线性组合输入；逆变换也使用相应子集。它既省计算，也让检测分数和服务自己的正常频率结构关联，而不是无条件套一套全局完整频谱。（PDF pp.6–7, §IV-C, Fig. 4）

频率表征把 context-aware DFT 系数与明确标记的 Fourier sin / cos bases 拼接，组成三通道张量，再由 three-channel convolution 学习频域表示。这个显式加入基频信息的模块称 frequency characterization。（PDF p.7, §IV-C, Fig. 4(b)）

**频率子集理论。** 将正常频谱幅值归一化为 $q^N(\omega_i)$，异常频谱归一化为 $q^A(\omega_i)$。仅保留正常模式 top-$k$ bases 并重归一化所得频谱记 $\bar q$；context-aware DFT 的谱重构误差以 $KL(\bar q\Vert q)$ 定义。Theorem 2 给出异常与正常重构误差差：

$$KL(\bar q^A\Vert q^A)-KL(\bar q^N\Vert q^N)=\log\frac{\sum_{i=1}^{k}q^N(\omega_i)}{\sum_{i=1}^{k}q^A(\omega_i)}.\tag{11}$$

在 Corollary 1 的条件 $\sum_{i=1}^k q^N(\omega_i)>k/n$ 下，正常重构误差小于异常。论文假定异常频谱是正常幅值上加期望为正的 i.i.d. shift，并用大数定律说明正常 top-$k$ 质量可能高于异常。完整谱 $k=n$ 时两边归一化质量都为 1，理论 gap 为 0；因此存在合适的 $k<n$ 时可增加区分性。该结论建立在其幅值 shift 假设上，不自动覆盖相位异常、低能量上下文异常或幅值分布变化不符合假设的故障。（PDF pp.7–8, §IV-C, Definitions 2–3, Assumption 1, Theorem 2, Corollary 1, Eqs. 10–11）

### 5.3 四阶段重构、异常分数与训练

1. **扩大局部异常**：对每个输入时间窗分别应用时域 peak / valley DualisticConv，逐位置平均两路输出。
2. **抽取服务正常模式**：Context-aware DFT 投影到服务特定基子空间，Frequency Characterization 拼上 sin / cos 基通道。
3. **重构频谱**：频域 autoencoder 用 peak / valley DualisticConv 代替标准卷积，形成两个重构分支，以便分别增强上 / 下谱偏差造成的重构困难。
4. **回到时间域**：两路分别 context-aware IDFT 还原；按每个时间点比较两路残差并取较大值，作为最终重构 / anomaly score。（PDF pp.4–7, Fig. 2, §§IV-A–C）

训练文字说用 SGD 最小化 Stage 4 得到的 reconstruction error；测试时 score 超阈值判异常，可用 POT 等阈值策略。论文 §III Eq. (1) 用“异常重构误差大于正常重构误差”的目标概括 reconstruction detector，但没有将该式展开为 MACE 的逐数据点监督分类损失；可确认的是重构训练，没有证据表明需要故障类别标签。具体实现中的重构范数 / 优化批次细节需要代码确认，笔记不补写常见 MSE 设定。（PDF pp.3–4, §III Eq. 1; pp.4–5, §IV-A）

## 6. Experiments

### 6.1 数据、分组与对照

论文按服务 / 机器 / 传感器子集区分正常模式，每十个子集为一组，训练统一模型并在组内子集测试。主要表格涵盖 SMD、JumpStarter 的 J-D1 / J-D2、SMAP；附加实验给出私有云监控数据 MC。正文摘要说四个 real-world datasets，但把 J-D1、J-D2 分开列表、MC 也单独列出，口径上是四类 benchmark/source 而表格细分为五个名称。（PDF pp.8–9, §V-A; Tables V–VIII）

- **SMD**：28 台机器、约 5 周，异常率 4.16%；作者称其服务间正常模式差异最大。
- **J-D1 / J-D2**：来自头部互联网公司的 30 个服务、每个服务 19 个 metrics；异常率分别 5.25% / 20.26%；J-D2 正常模式彼此更相似。
- **SMAP**：航天器遥测，异常率 13.13%，作者报告点异常占比较高。
- **MC**：某大型云服务商 25 个服务、15 天，异常率 3.6%，包含较多点异常；论文未在本地版本给出公开下载链接。

比较方法：DCdetector、Anomaly Transformer、DVGCRN、JumpStarter、OmniAnomaly、MSCRED、TranAD、ProS 和 VAE。统一模型实验中 JumpStarter 不适用，因其 signal-based 模式不能按相同多模式协议训练。指标主要是 Precision、Recall、F1；预备部分提到 POT，但具体各数据集阈值 / 测试标签选择协议在主文不够完整。（PDF pp.8–10, §V-A–B, Eqs. 12–14）

### 6.2 多模式统一模型结果

Table V 将每十个服务的一个统一 MACE 与统一训练的 baseline 比较。MACE 的 P/R/F1 为：SMD 0.964/0.870/0.910，J-D1 0.893/0.984/0.934，J-D2 0.938/0.989/0.961，SMAP 0.958/1.000/0.977。作者报告相比最强 baseline，平均 F1 提高 8.7%；提升明显，尤其 SMD 模式差异最大时。（PDF pp.9–10, Table V, Fig. 5）

Table VI 把“单一 MACE 服务组模型”与每个服务单独训练的 baseline 比较。它说明 MACE 的效率收益可用性能竞争力换取，但并非所有数据都与单服务专用模型齐平：SMD MACE F1 .910，TranAD 专模可达 .961；J-D1 MACE .934，接近 JumpStarter .933；J-D2 MACE .961，略低于 JumpStarter .968；SMAP MACE .977，高于该表最强对照 .970。对差异最大的 SMD，单服务特化模型仍有优势。（PDF pp.10–11, Table VI）

Table VII 的 MC 数据中 MACE F1=.941，强于对比中次高的 AnomalyTransformer .923。这个数据集有现实来源价值，但是否可公开获取未说明。（PDF p.11, Table VII）

### 6.3 未见模式与传递

Table VIII 报告跨 group 测试：在一个 group 训练、另一个 group 测试。MACE F1 为 SMD .863、J-D1 .885、J-D2 .964、SMAP .973，在该表四数据集均为最佳；差异较大的 SMD 较低，模式相似的 J-D2 / SMAP 接近同组结果。它支持“实验设置下跨组泛化较好”，但论文没有充分解释：测试未见服务对应的 service-specific Fourier subspace 从哪份数据得到、是否使用待测服务正常样本。因此不能无条件把结果称为不需要目标域数据的 zero-shot。（PDF pp.11–12, §V-B, Table VIII）

### 6.4 效率、消融与敏感性

作者摘要称 MACE 约快 4 倍；效率图以 SMD 的一个服务组进行训练计时 / profiling，使用 32 核 Xeon E5-2620 和 2×K80 GPU。文字结论是 MACE 比深度网络 baseline 计算和内存开销更低，但内存高于浅层 VAE / ProS；这里的图表数字不在文本中可直接读出，因此不展开成精确的全库吞吐保证。（PDF pp.1–2, p.11, Fig. 6(a), §V-C）

Table IX 消融总体支持 DualisticConv、pattern extraction、context-aware DFT/IDFT 与 frequency characterization：在 SMD 上去掉 Pattern Extraction 后 F1 .910→.696，去掉频域双卷积后降至 .184，去掉时域双卷积后降至 .084；SMAP 完整模型 .977，去时域双卷积降至 .720。但模块收益并非每个数据集单调：J-D2 上完整 F1 .961，去 Frequency Characterization 后 .975；说明“模块在所有数据集上均提升”的泛化解读不成立。（PDF p.12, Table IX）

超参数图 Fig. 6 显示：$\gamma_t,\gamma_f$ 增大可先提高结果，但过大可能梯度爆炸；$\sigma$ 变化相对稳定；时域 kernel 增大先提升再下降，过大失真；基数 $k$ 增大也先升后降。Table IV 给出默认 basis count 20、window 40、kernel 5、learning rate .001；$\gamma$ 按数据集从 7–13、$\sigma$ 多取 5–7。具体网格包括 $\gamma$、scale、kernel 与 basis count 多组组合。（PDF pp.8–9, Table IV; pp.11–13, Figs. 6(b)–(f), §V-E）

## 7. Contributions and Strengths

- 用服务 / 子集对应的频域正常子空间统一多个服务的模型，减少“一服务一个模型”的成本。
- 同时在时域扩展短异常、在频域利用幅值变化操纵可重构性；peak / valley 两路处理上、下方向的偏差。
- 不只把频域当成转换表示，还给出选取正常 top-$k$ Fourier bases 的理论解释与组件消融。
- 评测跨服务统一模式、专属模型对照、held-out group、内部云数据和效率，覆盖用户关注的多个正常模式与短时异常。

## 8. Limitations and Reproduction Value

### 作者讨论及实验明确显示

- 没有单独的 Limitations 章节；敏感性实验显示 $k$、时域 kernel 和 $\gamma$ 有非单调作用，过大参数会引起梯度爆炸 / 时序扭曲。（PDF pp.12–13, §V-E）
- 多模式之间仍有性能差距：最异质 SMD 上，单个服务专属 baseline 可胜过统一 MACE；作者在 Table VI 及讨论中承认此情形。（PDF pp.10–11）
- 在 J-D2 上删掉 frequency characterization 的 F1 反而略高于完整模型；消融不支持每个模块在所有数据集都有效。（PDF p.12, Table IX）

### 方法与证据边界

- **“多模式”主要指跨服务、跨机器 / 传感器子集异质性。** 频率基按服务 normal pattern 静态建立，没有显式识别同一服务内部的峰谷负载、日夜、发布 / 扩缩容等动态运行状态，也没有使用 workload 或 Trace 语义。
- Context-aware DFT 依赖服务身份和对应正常子空间。对一个训练中未见的服务，基如何匹配或获取的文本说明不足；Table VIII 的 held-out group 不足以自行证明严格 zero-shot。
- 双卷积频域解释依赖异常幅值更强 / 频谱方差更高；Theorem 2 还假设异常是正常 spectrum 上的正向 i.i.d. amplitude shift。对低能量异常、相位 / 因果关系异常、缓慢概念漂移，证据不足。
- 仅报告 Precision / Recall / F1，阈值构造及可能的标签使用细节没有充分逐数据集公开；缺少面向告警时延、事件误报成本的系统评测。
- MC 是来自云厂商的非公开数据；关键系统使用场景有吸引力，但独立复现受数据访问限制。版本中虽称代码/环境随 supplementary 提供，本地清单未链接到独立稳定仓库。
- “快约 4 倍”的结果来自一组 SMD 测试和指定旧硬件，不是对所有云流量场景的端到端延迟 / 吞吐承诺。

### 我的分析推断

- MACE 的“正常模式上下文”比单一无条件重构更明确：将已知服务的常见频率基作为条件。但这相当于把正常状态先验编码在 service-conditioned spectrum 中，不等于系统能从实时负载和运维上下文判断业务波动的来源。
- 如果同一服务因为合法的高流量、版本发布或日周期而切换频谱，而模型仍使用静态基，变化可能抬高 reconstruction error；现有实验没有把这类新正常切换与真实故障并发来验证。
- 若待测 service 的正常基由该服务测试前的正常数据统计得到，那么“未见模式泛化”可能包含目标数据适配；若基仅由训练服务得到，则其选择策略需说明。来源不清是理解该主张的关键复现点。
- MACE 关注“哪些频率常见、样本是否可由对应子空间重构”，不直接产生时间变化的业务解释或根因候选。

## 9. Relationship to Other Papers

- **CrossAD**：CrossAD 在单条序列内学习粗到细跨尺度映射，并用跨窗口查询 / 原型共享子序列；MACE 按服务选择稀疏正常 Fourier bases，突出跨服务正常模式异质性。二者都是重构路线，但关联对象分别是时间尺度和服务条件频谱。
- **CAROTS**：CAROTS 用跨变量 Granger 预测关系区分因果保持变化和关系破坏；MACE 用静态频率基和谱幅值变化。两者都希望超越逐点幅值，但尚未结合 workload / 业务事件。
- **When Model Meets New Normals**：WMMNN 在推理期在线适应新分布；MACE 预先构造服务正常基和统一模型，未展示安全的连续状态更新。
- **CAPMix**：CAPMix 通过合成异常及软标签校准训练边界；MACE 直接重构正常模式，不依靠伪异常标签。
- **Fortifying Time Series**：DTW-certified defense 提供对抗扰动下的决策稳定性证书；MACE 的 robustness 主要指多服务模式适应和时域短异常灵敏度，不是 formal adversarial certification。

## 10. My Understanding

MACE 提供了本批第一个明确以“多种正常模式”作为核心问题的 TSAD 方法，但它的状态划分单位是已知服务 / 子集：每个服务用出现频繁的正常频率基作为参照，共享一个重构模型。它说明“跨实体正常模式不同”可以用 context-aware 子空间和参数共享处理；不等于已经解决“单个业务随负载变化动态切换正常状态”。对研究正常流量波动，最值得延伸的问题是让这些频谱模式受动态 workload / release context 条件化，并验证上下文状态与真实异常共现时的误报和漏报。

## 11. Questions

1. Context-aware DFT 对 unseen normal group 的对应服务子空间是如何获得的？Table VIII 是否使用了未标注目标服务 / 测试正常窗口做基提取？
2. 多模式子空间能否从服务级静态划分扩展到同一服务内由业务负载、时间、版本、扩缩容触发的动态状态？
3. 当异常由低能量或相位变化造成，或频谱变化并非正向 i.i.d. amplitude shift 时，Theorem 2 和频域双卷积还有何判别能力？
4. 与 POT 或其它固定运行阈值相比，论文表格的 F1 如何选择 threshold、是否在测试标签上调参？
5. 业务高峰和局部故障同时出现时，服务特定参考频谱会否将故障混入常见模式？是否有上下文条件对照实验？
6. 统一模型与 per-service model 的总体资源 / 误报代价，能否在公开的独立云 KPI 数据上复现？

## 12. Useful Definitions

- **Service normal-pattern subspace**：按训练服务频谱 top-$k$ basis 的出现频率建立的频率基集合，作为该服务窗口的 DFT / IDFT 条件。（§IV-C）
- **Dualistic convolution**：用奇数幂 $\gamma$ 的广义卷积突出局部极值；正大 $\gamma$ 形成 peak，负 $\gamma$ 形成 valley。（§IV-B, Eq. 2）
- **Frequency characterization**：把投影频谱系数与对应 Fourier sin / cos basis 标记组成三通道输入，再由卷积网络学习谱表示。（§IV-C, Fig. 4(b)）

## 13. Tags

`TSAD` `AIOps` `multi-normality` `service-conditioned` `frequency-domain` `context-aware-DFT` `dualistic-convolution` `short-term-anomaly` `efficiency` `ICDE-2024`
