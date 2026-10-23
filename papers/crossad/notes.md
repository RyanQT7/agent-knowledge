# CrossAD：跨尺度关联与跨窗口上下文的时序异常检测

## 1. Metadata

- Title: CrossAD: Time Series Anomaly Detection with Cross-scale Associations and Cross-window Modeling
- Authors: Beibu Li, Qichao Shentu（共同一作）, Yang Shu, Hui Zhang, Ming Li, Ning Jin, Bin Yang, Chenjuan Guo
- Year / Venue: 2025 / NeurIPS
- CCF: A（采用已人工确认的论文清单等级）
- DOI: [10.52202/085713-4605](https://doi.org/10.52202/085713-4605)
- Code: [CrossAD GitHub](https://github.com/decisionintelligence/CrossAD)
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local File: [CrossAD PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf)

## 2. One-Sentence Summary

CrossAD 不把不同分辨率的序列分开重构或简单融合，而是学习“粗尺度能否按正常映射重建细尺度”；再用周期感知查询和跨窗口原型上下文共享相似子序列模式，以多尺度重构误差作为逐点异常分数。

## 3. Problem and Motivation

论文研究无监督多变量时序异常检测：给定训练序列，测试时为未知序列的每个时间点产生异常分数 / 标签。异常的时长和形态不一：细粒度适合发现单点尖峰，粗粒度更容易呈现一段子序列的整体异常。已有多尺度路线往往独立编码各尺度或在特征层简单融合，未直接学习尺度之间的映射；同时常以固定长度窗口切分序列，使窗口只能访问局部数据。（PDF pp.1–3, §§1–2）

作者的关键假设是：训练正常序列中存在稳定的粗到细映射。正常时，较粗的整体趋势和上下文足以重建相应的细节；异常发生后，局部和整体变化对各尺度的影响不同，原有映射被破坏，因此细尺度重构误差上升。第二个假设是，不同窗口里会反复出现上下文相似的子序列，可通过共享的子序列表示和全局原型提供窗口外信息。（PDF pp.2–6, Fig. 1, §§3.1–3.3）

## 4. Core Idea and Architecture

```text
多变量序列 → 平均池化生成多分辨率序列 → patch embedding + positional encoding
          → 分尺度编码（Scale-Independent Mask）
          → 对齐尺度表示 → 以更粗尺度重建细尺度（Cross-scale Mask）
          ↘ 周期感知 Router 选择 learnable sub-series queries
             → 对当前窗口多尺度表示 cross-attention 得到子序列表示
             → 分配并 EMA 更新全局多尺度原型
          → Decoder cross-attend 全局原型并重建各尺度
          → 各尺度平方误差插值回原时间轴并平均 → SPOT 阈值
```

整体采用 channel-independent 处理。每个窗口先经过多尺度重构主干；跨窗口模块则从该窗口的多尺度编码中抽取代表性子序列，将相似模式累积为全局多尺度上下文，并在解码重构时将上下文提供给当前尺度。（PDF pp.3–6, Fig. 2, §§3.1–3.3）

## 5. Method in Detail

### 5.1 多尺度生成与尺度内编码

原序列记为 $X^m$，经不同核宽的平均池化形成从粗到细的 $X^0,\ldots,X^{m-1}$。各尺度分别切 patch，经 MLP 映射到统一隐藏维度并加入位置编码，随后拼接为总长度 $P=\sum_i P_i$ 的表示。论文把多尺度目标写为：

$$
\theta^*=\arg\min_\theta\sum_i\left\|X^i-\hat X^i\right\|_2^2,
\qquad \hat X^i=f(\{X^0,\ldots,X^{i-1}\};\theta).
\tag{1}
$$

这里的核心是每个尺度的重构条件由更粗尺度表示构成；异常分数来自尺度映射失败，而不是只看各尺度独立自编码误差。原文的尺度上下标说明略紧凑，阅读时宜按“粗到细”文字和 Fig. 2 理解。（PDF pp.4–5, §3.2, Eq. 1）

尺度内 Transformer 使用 mask attention：

$$\operatorname{MaskAttn}(Q,K,V,M)=\operatorname{softmax}\!\left(\frac{(QW_q)(KW_k)^\top}{\sqrt d}+M\right)(VW_v).\tag{2}$$

Scale-Independent Mask $M^1$ 是块对角矩阵：不同尺度之间的注意力设为 $-\infty$，同一尺度块设为 0。因而 encoder 在每个尺度内学习时间依赖，但不会在这一步提前混合尺度。每层以残差、LayerNorm 和 FeedForward 更新表示（Eq. 3）。（PDF p.5, §3.2, Eqs. 2–3, Fig. 2②）

### 5.2 Cross-scale decoder：以粗尺度为条件重建细尺度

Encoder 输出各尺度的 patch 表示后，先插值到相邻细尺度所需长度（Eq. 4）。Decoder 的 Cross-scale Mask $M^2$ 屏蔽不允许的细尺度到粗尺度访问，使某个目标尺度的重建只条件化于更粗的尺度表示。论文把该注意力层与全局上下文 cross-attention、前馈层串联：

$$\tilde Z^l=\operatorname{LN}(Z^{l-1}+\operatorname{MaskAttn}(Z^{l-1},Z^{l-1},Z^{l-1},M^2)),\tag{5}$$
$$\hat Z^l=\operatorname{LN}(\tilde Z^l+\operatorname{Attention}(\tilde Z^l,G',G')),\quad Z^l=\operatorname{LN}(\hat Z^l+\operatorname{FFN}(\hat Z^l)).\tag{6}$$

最后线性映射回原输入空间，得到每尺度的 $\hat X^i$。其作用不是把尺度差异直接当成异常，而是让模型拟合正常期的尺度间映射，再把映射被破坏的程度变成重构误差。（PDF pp.5–6, §3.2, Eqs. 4–6）

### 5.3 Period-aware Router、子序列查询与全局原型

固定窗口缺少窗口外上下文。作者维护可学习查询库 $Q=\{q^1,\ldots,q^n\}$，每个查询是长度 $S$、维数 $d$ 的子序列表示。Period-aware Router 对当前窗口做 Fourier transform，保留幅度最大的 $k$ 个频率分量并逆变换以滤除较弱频率；重构时保留相位 $\Phi$：

$$X^t_{period}=\mathcal F^{-1}(A^t_{top-k},\Phi).\tag{7}$$

将 $X^t_{period}$ 输入 MLP 得到路由向量 $u\in\mathbb R^n$，以带独立 Gumbel 噪声和温度 $\tau$ 的 Gumbel-Softmax 对查询加权 / 选择（Eq. 8）。选出的当前窗口查询 $q^t$ 对 encoder 的多尺度表示 $H^{L,t}$ 做 cross-attention：

$$R^t=\operatorname{CrossAttention}(q^t,H^{L,t},H^{L,t}).\tag{9}$$

$R^t$ 被送到 $K$ 个全局原型 $G=\{g_1,\ldots,g_K\}$ 中，以欧氏距离选最近原型，并用 EMA 更新：

$$d_i^t=\operatorname{distance}(R^t,g_i),\quad j=\arg\min_i d_i^t,\quad g_j\leftarrow \alpha g_j+(1-\alpha)R^t.\tag{10–11}$$

拼接原型成为 $G'$，供 Eq. (6) decoder cross-attention 使用。作者将此称为跨窗口全局上下文共享：学习的查询从当前窗口提取可复用的多尺度子序列表示，原型把不同窗口的相似表示聚在一起。（PDF pp.6–7, §3.3, Eqs. 7–11）

正文说在训练期间持续更新上下文；附录 Algorithm 1 写作“for each new window”，使用 $\alpha=0.95$。这段伪代码没有明确说明测试推理时是否也更新原型，故不把它记成已证实的测试时自适应机制。原型也没有业务状态标签，不能直接解释某个模式对应高峰、发布或扩容。（PDF p.7, §3.3; PDF p.21, Appendix A）

### 5.4 目标函数、异常分数与阈值

论文的训练目标为 Eq. (1) 各尺度重构平方误差之和，没有分类标签损失或对比损失。测试时，对各尺度误差进行插值，恢复到原序列长度并取平均：

$$\operatorname{AnomalyScore}(X^m)=\frac1m\sum_i\operatorname{interpolate}\!\left((X^i-f(\{X^0,\ldots,X^{i-1}\};\theta))^2\right).\tag{12}$$

分数超过 SPOT 自动阈值 $\delta$ 的点被标为异常。由此，CrossAD 输出的是与尺度重构不一致相联系的分数；公式本身不提供故障类型或业务原因。（PDF p.7, §3.4, Eq. 12）

### 5.5 训练与复现要点

附录配置：hidden dimension 128、attention dimension 32、4 heads、dropout 0.1、encoder/decoder 各 2 层、默认 5 个子序列查询、32 个上下文原型；按数据集使用非重叠滑窗；平均池化核从 $\{32,16,8,4,2\}$ 中选择；Adam、初始学习率 $10^{-4}$、batch size 128，推理时不 drop-last；用 PyTorch 和 NVIDIA A800-80GB。统计表给出各数据集窗口长度（96–192，UCR 不使用窗口）。（PDF p.21, Appendices B–C, Table 5）

论文主要是训练正常序列的无监督重构路线；没有使用告警根因标签训练。模型的超参数敏感性分析覆盖 patch size、window size、hidden size、尺度数、查询数与原型数；UCR 额外采用“排名靠前的分数是否击中标注异常区间”的定位式评估，和常规逐点异常分类指标不是同一个评估协议。（PDF pp.22–24, Appendix D–E.4）

## 6. Experiments

### 6.1 数据、Baseline 与指标

主实验用七个真实数据集 / 子集：SMD（服务器，38维）、MSL（航天器，保留第一个连续维度）、SMAP（同样仅保留第一个连续维度）、SWaT（水处理，31维）、PSM（eBay 服务器，25维）、NeurIPS-TS 的 GECCO（水处理，9维）及 SWAN（Space Weather，38维）。窗口长度分别为 96、128 或 192，训练/验证/测试拆分和异常率见 Appendix B Table 5。补充实验包括 UCR 250 个子数据集以及 TSB-AD-U / TSB-AD-M 40 数据集基准。（PDF pp.7–8, §4.1; pp.21, 24–25, Tables 5, 10）

18 个 baseline 覆盖 OCSVM、PCA、IForest、LODA、HBOS、LOF、AE、DAGMM、LSTM、CAE-Ensemble、OmniAnomaly、Anomaly Transformer、DCdetector、ModernTCN、GPT4TS、MtsCID、TimeMixer、TimesNet。主表重点报告 VUS-ROC / VUS-PR，并补充 AUC-ROC/PR、Standard-F1、Affiliation-F1 和 Range-AUC-ROC/PR；阈值由 SPOT 选取。作者指出 point adjustment 可能导致不公平或虚高，因此采用多种事件 / 阈值敏感指标。（PDF pp.7–9, §4.1, Tables 1–2; Appendix E.1）

### 6.2 主结果与证据边界

Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。（PDF pp.8–9, Table 1）

Table 2 对 ModernTCN、TimeMixer、TimesNet 做多指标比较。在 SMD、PSM、GECCO 的九项指标中，CrossAD 整体表现强；例如 PSM 的 VUS-PR 是 0.5596，TimesNet 是 0.4373。但指标和数据集有限，不宜推广成在所有 benchmark 上必然最好。（PDF pp.8–9, Table 2）

TSB-AD-U 附加表中 CrossAD 的 AUC-PR/AUC-ROC/VUS-PR/VUS-ROC/Standard-F1/PA-F1/Event-F1/R-based-F1/Affiliation-F1 分别为 0.44/0.78/0.45/0.84/0.47/0.81/0.68/0.41/0.89；作者称 TSB-AD-U/M 均表现优秀。UCR 附加测试采用 top-quantile 命中异常区间数及平均 quantile，与时间点分类结果不可直接等价。（PDF pp.24–25, Appendix E.3–E.4, Table 10, Figs. 8–9）

### 6.3 消融、可视化和效率

Table 3 在 PSM、MSL、GECCO 上逐步加入组件，平均 VUS-PR 从单尺度 0.3665 到多尺度 0.3962，再到多尺度 + cross-scale reconstruction 的 0.4326；继续用原型上下文（直接从 encoder 多尺度表示更新）为 0.4597；完整 CrossAD 为 VUS-ROC 0.8447 / VUS-PR 0.4984。该表支持多尺度、跨尺度映射和全局上下文均有贡献。正文称完整方法相较 Row 4 的提升为 3.18% / 10.4%，但用表中 Avg. 数值直接重算，VUS-ROC 相对增幅约 3.1%，VUS-PR 约 8.4%；笔记以表格可复核数值为准，保留此数字口径差异。（PDF pp.9–10, §4.3, Table 3）

Fig. 4 对点、shapelet、seasonal、trend 等五种形态可视化；作者观察到传统重构在 shapelet/seasonal/trend 情形下误差不稳定，而跨尺度残差更能揭示正常尺度映射被破坏。Fig. 5 显示单尺度响应可互补，合并多尺度分数更容易定位细微模式。可视化是案例证据，不是独立统计检验。（PDF pp.10–11, Figs. 4–5）

GECCO 5 epoch 效率对照表中 CrossAD 训练 270.75 秒、测试集推理 0.80 秒、0.93M 参数、VUS-PR 0.6211；Anomaly Transformer 训练 270.49 秒、推理 15.05 秒、4.74M 参数、VUS-PR 0.0278。该效率结果只覆盖 GECCO 和论文指定 batch/硬件，不代表跨数据集运行时保证；作者指出训练中持续更新全局上下文增加训练耗时。（PDF p.10, §4.3, Table 4）

### 6.4 参数敏感性

作者报告模型对 patch size（设为 1 时明显退化）、window size 和 hidden dimension 相对不敏感；增大尺度数量总体有帮助但会饱和。查询数过多可能引入噪声；上下文原型数的最优值依数据集变化。具体例子：默认查询数 5 在 MSL 上 VUS-PR 0.3144，n=7 为 0.3141；在 GECCO 上 n=7 比 n=5 略好。附录明确将“不同数据集所需的最优查询数和原型数不同，但使用统一参数”列为局限。（PDF pp.22–24, Appendix D, Tables 6–8; PDF p.25, Appendix G）

## 7. Contributions and Strengths

- 把多尺度异常检测从“每层各自看误差”推进到粗尺度条件下的细尺度重建，把尺度间正常映射当成显式建模对象。
- 通过可学习查询和原型共享窗口间重复的子序列表示，针对固定窗口局部性给出结构化方案，而不是简单拉长单个窗口。
- 有消融、多指标比较、参数敏感性、效率分析、UCR 与 TSB-AD 补充评估；局限中也承认原型/查询超参数跨数据集不统一。
- 公开代码仓库，附录给出主要模型配置和数据统计，具有较好的复查入口。

## 8. Limitations and Reproduction Value

### 作者明确说明

- 最优子序列查询数及全局上下文原型数随数据集变化；当前统一参数可能限制性能，未来可按数据特征自动调整。（PDF p.25, Appendix G）
- 全局上下文在训练期持续更新会增加训练成本。（PDF p.10, §4.3）

### 实验和方法的边界

- “全局多尺度上下文”是潜在模式原型，不含业务状态、负载、发布或根因标签；论文没有验证每个原型是否对应稳定、可解释的业务运行态。
- 论文用 reconstruction residual 判断关系失配，但没有解释造成失配的运维事件；重构失败是异常证据，不等同于根因解释。
- 主实验对 MSL/SMAP 仅保留一个连续维度，因而多变量关联价值不适用于所有数据集；其他数据集多变量结果也未配套外生上下文。
- 正文强调各数据集 VUS 指标全面领先，但 SWAN 的 VUS-ROC 表格值略低于 TimesNet；消融文字给出的相对提升亦与表格重算略有差别。引用结论时应以具体表格、指标和数据集为单位。
- 原型更新伪代码写“每个新窗口”，正文强调训练期间；测试时是否更新不够明确，复现时要核对代码，不能直接把 CrossAD 归类为已验证的 online test-time adaptation。
- SPOT 提供自动阈值，但没有据此展示生产告警成本、业务接受度或故障与工作负载共现的评估。UCR 的量化命中协议也依赖标注异常区间。

### 我的分析推断

- 查询和原型或能捕捉“经常重复的多尺度形态”，但不一定能区分由相同形态造成的“合法业务高峰”和“资源故障”。如果负载状态变换伴随尺度关系变化，模型反而可能把新正常映射当作异常；论文没有做这种机制切换的条件实验。
- CrossAD 的“跨尺度关联”是同一时间序列不同采样尺度之间的映射，不是 CAROTS 所建模的跨变量 Granger 因果依赖；两者证据轴不同。
- 若业务上下文随窗口共同进入 query/router 或原型更新，并以负载相近的不同状态和故障叠加做压力评估，才可检验“模式表示”能否从统计记忆提升为有语义的运行状态识别。这是待验证方向，不是本文结论。

## 9. Relationship to Other Papers

- **CAPMix**：CAPMix 通过合成伪异常与 DTW 软标签改善训练判别边界；CrossAD 是无监督多尺度重构路线，检验尺度关联能否重构。前者关注伪标签可信度，后者关注跨尺度映射失配。
- **When Model Meets New Normals**：后者利用测试流 EMA 和伪正常点在线适应；CrossAD 以训练得到的查询/原型提供窗口间上下文，不能在推理阶段持续自适应这一点上与之混同。
- **CAROTS**：CAROTS 以跨变量 Granger 预测依赖指导增强与分数；CrossAD 以单个序列的粗细尺度映射及跨窗重复子序列为主。CAROTS 的关系偏因果预测图，CrossAD 的关系偏时间分辨率映射。
- **待读方向**：与 Learning Multi-Pattern Normalities in the Frequency Domain 比较时，重点核对 CrossAD 的查询 / 原型是否显式代表多种正常模式，还是只共享可重用统计子序列。

## 10. My Understanding

CrossAD 的有价值之处是把异常看成“一个尺度无法按正常规律从另一个尺度生成”，并试图让模型看到跨窗口重复出现的相似片段。它扩充了重构误差中可检查的关系结构，且多尺度误差比单尺度更适合不同持续长度。可是这仍是序列内部的统计一致性：正常业务波动的来源没有被读取，原型语义也没有被命名。因此它能回答“当前观测是否偏离已学习的跨尺度模式”，还没有回答“这个变化是否由合法负载、发布或环境切换导致”。

## 11. Questions

1. 全局原型如何处理新出现但合法的负载 / 调度状态？是否冻结、延迟更新或可以安全地在线更新？正文与 Algorithm 1 的更新阶段边界需要通过代码核实。
2. CrossAD 的子序列 query、global prototype 是否对应可复现的语义运行态？能否用 workload 或发布上下文验证原型含义？
3. 粗细尺度映射在真实故障与负载变化同时发生时如何变化？现有消融和可视化未覆盖并发事件。
4. CrossAD 对 SWAN 的 VUS-ROC 低于 TimesNet，以及 Table 3 文字增益与表值差异是否来自排版、统计方式或报告错误？
5. 多变量数据的 channel-independent 处理是否错过跨指标互补信息；与 CAROTS 等跨变量关系建模组合后能否获得独立增益？

## 12. Useful Definitions

- **Cross-scale association**：同一原序列各时间分辨率间，可用粗粒度数据映射 / 重建细粒度数据的正常关系。（§1, Fig. 1, §3.2）
- **Cross-scale reconstruction**：decoder 以更粗尺度表示为条件，重建较细尺度，并将平方误差作为异常证据。（§3.2, Eqs. 1, 4–6）
- **Global multi-scale context**：经 query 提取的跨窗口多尺度子序列表示聚合到原型库，再作为 decoder 的 cross-attention 上下文。（§3.3, Eqs. 7–11）

## 13. Tags

`TSAD` `multivariate-time-series` `multi-scale` `cross-scale-reconstruction` `cross-window-context` `prototype` `sub-series-query` `reconstruction` `VUS-PR` `NeurIPS-2025`
