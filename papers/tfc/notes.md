# TFC：从动态轨迹视角融合时间、频率与曲率的异常检测

## 1. Metadata

- Title: Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion
- Authors: Hang Cui, Zexin Wang, Changhua Pei, Juncheng Hu, Haotian Si, Quan Zhou, Cenjie Hu, Jingjing Li, Dan Pei, Gaogang Xie
- Year / Venue: 2026 / ACM SIGKDD (KDD ’26)
- CCF: A（按已人工确认的清单）
- DOI: [10.1145/3770855.3817936](https://doi.org/10.1145/3770855.3817936)
- Code: [TFC GitHub](https://github.com/CSTCloudOps/TFC)
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local PDF: [TFC PDF](../../sources/papers/tsad-2024-2026/2026/KDD/KDD26-Rethinking%20Time%20Series%20Anomaly%20Detection%20from%20a%20DynamicPerspective-%20Temporal–Frequency–Curvature%20Fusion.pdf)

## 2. One-Sentence Summary

TFC 将时间值、频域周期结构与二阶差分曲率并行编码，以多跨度注意力保留曲率的短、中、长局部形状证据，再用 frequency–curvature cross-attention 校准周期引起的曲率响应，最后逐时路由 pattern evidence 与 temporal evidence。

## 3. Background and Problem Definition

作者认为点值残差擅长识别突变尖峰，却可能漏掉仍处于合理数值范围内的形态改变：连续信号斜率转折、缓慢趋势弯曲、周期驱动力变化。预测 / 重构深网常依赖平滑、聚合或频域重构压制噪声；这些操作也会削弱细小的局部几何变化。作者因此把时序看作演化系统产生的轨迹，写出：

$$x_{t+1}=f_\theta(x_t,u_t)+w_t,\qquad y_t=h(x_t)+v_t.\tag{4}$$

其中 $u_t$ 是外生驱动，异常可能来自转移机制 $f_\theta$ 或 forcing 统计改变，而非观测值 $y_t$ 的立即大幅越界。（PDF pp.1–3, §§1–2）

这里需注意方法与动机的边界：TFC 的 state-space 方程用于说明“机制变化可能不表现为明显点异常”，论文实现是**逐条单变量序列**的表示模型，并没有将真实 workload / 外生驱动 $u_t$ 作为模型输入或估计系统转移机制。（PDF p.4, §3; Appendix C, p.11）

## 4. Three Technical Challenges

1. **Mechanism shift ≠ value shift**：有限窗口内可能存在数值都合理、但演化规律不同的序列；仅在观测空间逐点拟合不易区分。（PDF p.2, §1）
2. **动力学异常支持多尺度**：尖峰与 shapelet 局部，趋势弯曲中程，季节变化长程；单一窗口可能错配。（PDF p.2, §1）
3. **曲率灵敏度与误报的权衡**：二阶差分会放大高频变化，因此也容易放大正常震荡和噪声；需要其他证据进行校准。（PDF p.2, §1）

## 5. Architecture Overview

```text
univariate input window X
  ├─ Temporal encoder：2 层 Transformer → temporal prediction / embedding H_t
  ├─ Frequency encoder：FFT → K 个频带掩码 → IFFT 频带序列 → MHA / projection → F_fusion
  └─ Curvature encoder：second difference κ_t → per-head span-masked attention → C_fusion
                 ↓
    CrossAttention(F_fusion, C_fusion) → H_fc （周期证据校准曲率形态）
                 ↓
    α(x) 逐时 router：Ŷ = α(x)H_fc + (1−α(x))H_t
```

三个分支分别偏向点 / 上下文异常、周期 / 趋势偏离、局部曲线形状变化；两阶段融合先融合频率与曲率，再与时间表征自适应融合。作者把这一结构称为 temporal–frequency–curvature fusion。（PDF pp.4–6, Fig. 3, §§3.1–3.4）

## 6. Method Details

### 6.1 三类证据及二阶差分依据

对离散序列 $y_t$，曲率 proxy 为：

$$a_t=\frac{y_{t+1}-2y_t+y_{t-1}}{\Delta t^2}.\tag{2, 5}$$

作者给出三项理论说明：

- 若连续信号 $y\in C^4$ 且采样间隔足够小，中心二阶差商近似 $y''(t)+O(\Delta t^2)$（Proposition 2.1, Eq. 7）。
- 若分段线性曲线在采样点 $t_0$ 发生斜率从 $m_1$ 到 $m_2$ 的转折，二阶差分在该点为 $(m_2-m_1)/\Delta t$，其他网格位置为零（Proposition 2.2, Eq. 8）。
- 二阶差分的 DTFT 传递函数是 $H(\omega)=e^{j\omega}-2+e^{-j\omega}=-4\sin^2(\omega/2)$，所以频率越高幅度越大，低频极限约为 $\omega^2$（Proposition 2.3, Eq. 9）。

这些命题解释曲率对转折点和高频形变灵敏的原因，也说明高频正常震荡 / 测量噪声会被同样放大，因此论文需要频率分支校准。它们是算子性质，不是“曲率变化即故障”的统计保证。（PDF pp.2–4, Eqs. 2, 5, 7–9）

论文还定义 temporal evidence $y_t$ 本身，以及对过去 $L$ 个观测计算的频谱摘要 $p_t=\Phi(y_{t-L+1:t})$（Eq. 6）。模型未将摘要中的业务驱动变量 / Trace 加进 $\Phi$；周期频谱是观测信号内生证据。（PDF p.3, §2.1, Eqs. 5–6）

### 6.2 Frequency perspective：分带 FFT 表示

对输入序列 $X$ 做 FFT，将频谱划分为 $K$ 个区间。第 $k$ 个二进制频带 mask $M_k$ 仅保留其索引区间，得到：

$$C_k=\mathcal F^{-1}(\mathcal F(X)\odot M_k).\tag{10}$$

各 $C_k$ 通过 concatenation 和上下投影后由 Multi-Head Attention 混合：

$$\hat F=\operatorname{MHA}(\operatorname{Concat}(C_1,\ldots,C_K)W_{up})W_{down}.\tag{11}$$

这一路让模型表达不同频带 / 周期尺度的信号；作者认为频域信息能帮助识别周期性偏离，并与曲率交叉注意力减少正常周期振荡引起的误报。（PDF p.4, §3.1, Eqs. 10–11）

### 6.3 Curvature perspective：Multi-Span Attention (MSA)

计算二阶差分 $\kappa_t=(X_{t+1}-2X_t+X_{t-1})/\Delta t^2$（Eq. 12），对曲率序列生成各注意力头的 $Q_r,K_r,V_r$，内积注意力 logits 为 $Q_rK_r^\top/\sqrt{d_k}$（Eq. 13）。与普通全局 attention 不同，MSA 给每个 head 分配一个动态跨度 $r$，使用相对位置 mask：

$$\phi(r,\delta)=\begin{cases}e_r(\delta)w_r,&|\delta|\le 2^r,\\-\infty,&\text{otherwise},\end{cases}\quad
A^r_{ij}=\operatorname{Softmax}\bigl(A_{ij}+\phi(r,|i-j|)\bigr).\tag{14–15}$$

其中 $e_r$ 是可学习相对位置 embedding，$w_r$ 为跨度相关可学习标量。越界位置 softmax 前设成 $-\infty$，各 head 因而只关注自身局部范围；不同 $r$ 的并行 heads 覆盖不同跨度，输出 $A^rV_r$ 拼接后线性映射为 curvature feature $C_{fusion}$（Eqs. 16 及 Fig. 3）。这一分支试图避免全局 attention 混合后局部弯折证据被稀释。（PDF pp.4–5, §3.2, Eqs. 12–16）

### 6.4 Temporal perspective 与两阶段融合

temporal encoder 是 2 层 Transformer block，每层包含 self-attention、残差 / Dropout / LayerNorm 和两层 ReLU FFN；线性投影得到 temporal prediction $H_t$（Eq. 17）。正文公式未显示 causal mask；因而不能仅凭“trajectory / dynamics-aware”将模型称为流式 causal detector。（PDF p.5, §3.3）

**第一阶段：Frequency–Curvature Cross-Attention。**

$$H_{fc}=\operatorname{CrossAttention}(F_{fusion},C_{fusion}).\tag{18}$$

设计意图是以周期线索调制容易对周期正常振荡过敏的 curvature 表征，保留细微形态变化并减小伪异常响应。（PDF p.5, §3.4）

**第二阶段：Expert Routing with Temporal Integration。**

$$\hat Y=\alpha(x)H_{fc}+(1-\alpha(x))H_t,\qquad \alpha(x)=\operatorname{MLP}(x).\tag{19}$$

routing 根据输入 $x$ 动态分配 pattern embedding 和 temporal embedding 的贡献，目标是使点型异常与形态异常可由不同证据权衡。论文给出结构与融合消融，但没有将 $\alpha$ 解释成概率校准值或具体运行状态分类器。（PDF p.5, §3.4, Eq. 19）

### 6.5 训练目标、异常分数与可复现细节

作者把 TFC 说成预测下一个 token 的无监督模型，提供了编码 / 融合公式和训练数据划分说明；主文与附录未明确写出最终 point-wise anomaly score 的精确公式、损失函数形式、如何由 $\hat Y$ 生成 score 和实际告警阈值策略。它应属于复现时查代码的项目，不在笔记中臆测成常见 MSE / 残差定义。（PDF pp.4–6, §§3–4; Appendix C–D）

### 6.6 因果在线性与中心差分的边界

虽然 Eq. 6 的短时频谱可用截至当前的窗口，二阶差分 Eq. 12 明确依赖 $X_{t+1}$，而 temporal Transformer 也未在论文中说明 causal attention mask。因此在逐时间点在线告警下，曲率支路可能需要未来采样点，整体 TFC 不应假定为零前视延迟 / strict online。其论文重点是检测分数而非在线部署。（PDF pp.3–5, Eqs. 6, 12, 17）

## 7. Experiments

### 7.1 Datasets, baselines, metrics

- **六个数据集**：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11）
- **使用方式**：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。（Appendix C, p.11）
- **Baselines**：17 项，包括 KANAD、AR、TShape、LSTMAD，统计 SubLOF / MatrixProfile / SAND，重构 AE / EncDecAD / TranAD / FCVAE 等。（PDF p.6, §4.1）
- **指标**：Best F1 与 Event F1（F1-E）。后者把连续异常区间当事件单元；Best F1 本身需调阈值，不能作为无标签线上点的直接保证。（PDF pp.5–6, §4.1, Table 1; Appendix D）
- **训练**：每序列 batch=128、初始 lr=.001、最多 100 epochs early stopping；UCR 原训练样本留 20% validation，其余数据采用 train:validation:test=4:1:5；五个随机 seed。（Appendix C, p.11）

### 7.2 主结果

Table 1 报告 TFC 的 F1 / Event-F1：

| Dataset | F1 | Event F1 |
| --- | ---: | ---: |
| AIOPS | .9406 | .8235 |
| NAB | .9987 | .9308 |
| TODS | .9481 | .9231 |
| UCR | .8996 | .6289 |
| WSD | .9883 | .9315 |
| Yahoo | .9741 | .9618 |

作者声称平均 Best-F1 和 Event-F1 达 SOTA、相对强 baseline 平均提升 10.8%。逐格 Table 1 中 TFC 的 Event-F1 六列均最高；普通 F1 的 AIOPS 为 .9406，低于 POLY 的 .9550，因此不能说每项数据、每个指标都领先。该表只展示一组数值，虽然 Appendix C 提到五个随机种子，却未在 Table 1 展开标准差。应把作者的平均领先结论与逐数据集结果区分开。（PDF pp.6–7, Table 1; Abstract; Appendix C）

### 7.3 视角消融和融合设计

Table 2 比较完整 TFC、把 MSA 换成 MHA 的 TFC with MHA、仅 Curvature Perspective (CP)、以及 CP w/o MSA。完整 TFC 的表列结果分别为 AIOPS .9405/.8235、NAB .9987/.9307、TODS .9258/.9155、UCR .8995/.6288、WSD .9883/.9315、Yahoo .9741/.9617（依次为 F1 / Event-F1）。**TODS 的 Table 2 值 .9258/.9155 与 Table 1 的 .9481/.9231 不一致**，论文没有解释差异，引用时应注明表号。消融支持多视角与 MSA 总体有益，但 CP 在个别事件指标上接近完整模型，不能推断每个数据每个指标都由所有模块提高。（PDF pp.7–8, Fig. 4, Table 2, §§4.3–4.4）

Figure 6 对比不同融合次序、直接 concat-MLP、固定线性权重等，作者报告所提两阶段策略整体较好；该处主要以图为证，没有逐项数值表。（PDF pp.7–8, §4.5, Fig. 6）

### 7.4 窗口敏感性、速度和误报图

- Figure 7 在五种窗口设置上比较六种方法的跨数据集平均 F1 / F1-E；作者报告 TFC 更稳定。但属于固定实验基准上的窗口敏感性分析，不等于训练部署后对任意未知业务频率均无需校准。（PDF p.8, §4.6）
- Figure 8 将 AIOPS 一个约 140,000 样本序列的推理时间、平均主指标和磁盘模型大小作图；TFC 位于高分低时延区域。原文没有给出一个跨硬件 / 长期流量负载的具体 SLA 延迟保证。（PDF p.8, §4.7, Fig. 8）
- Figure 2 逐异常类型展示方法检测分数和案例；Figure 5 分别展示单分支输出。它们支持形态差异的可视化解释，但不是对真实故障机制或业务根因的验证。（PDF pp.2–3, 7）

## 8. Contributions, Limitations and Reproduction

### Contributions

1. 将二阶差分曲率引入 TSAD 表征，针对传统平滑方法容易遗漏的 shapelet 转折 / 趋势变化。
2. 用 span mask 并行读局部不同跨度的曲率模式，控制全局 attention 对局部几何信号的稀释。
3. 先 cross-attend frequency 与 curvature，再逐时路由到 temporal evidence，以兼顾周期鲁棒性和形态灵敏度。
4. 在六个基准、17 个基线、单分支 / 融合消融、窗口敏感性与延迟图上验证；代码公开。

### Limitations and evidence boundaries

- **作者未单列 Limitations 章节**：Conclusion 宣称有益未来多视角建模方向；正文没有系统局限清单。（PDF p.8, §5）
- **不使用作者引入的外生驱动 $u_t$**：state-space motivation 强调机制 / forcing 改变，但算法输入仍是单变量 KPI / signal。因而 detector 可能辨识形态变化，却不说明变化是负载、发布、环境变化还是故障导致。（PDF pp.2–5; Appendix C）
- **高频噪声也被曲率放大**：频率 cross-attention 的目标是缓解周期振荡误报，但实验没有用已知物理 / 业务驱动说明哪些振荡是合法，也没有压力测试低信噪曲率。（PDF pp.2–5, §3.4）
- **中心差分及 temporal self-attention 的在线性不明**：$kappa_t$ 需 $t+1$，Transformer 未给 causal mask；因此无法从论文断定 timestamp $t$ 可无延迟在线评分。（PDF pp.4–5, Eqs. 12, 17）
- **阈值与训练目标公开细节不足**：主文未写清最终异常 score 与 loss 计算式；Best-F1 使用阈值校准，部署前固定阈值成绩需要独立验证。（PDF §§3–4, Appendix C–D）
- **逐序列独立训练**：跨指标相关性、不同 KPI 的共同故障模式和多实体状态关联未被模型利用；AIOPS / WSD 场景的数据来源不等于系统实际使用了 Trace / release context。（Appendix B–C）
- **评估结论边界**：数据和人工标注模式不一定覆盖真实生产中业务高峰与真实故障并发；Table 1 的 AIOPS F1 并非表中第一，尽管平均与 Event-F1 声称领先；没有公开该 benchmark 的告警人力成本 / 固定阈值精确度。（Table 1; §§4.1–4.7）

### 复现价值

有代码仓库和方法方程，可据官方实现核验 anomaly score / loss、padding、FFT normalization、各 head span 取值、中心二阶差分的首末点处理、阈值校准协议和五种子汇总口径。本文阅读未执行代码或实验，暂不替作者补全未写出的 score / loss 公式。

## 9. Relationship to Other Papers

- **MACE / TFMAE / Tri-domain ICDE work**：共同利用时频表示，但 TFC 新增显式二阶几何证据和 curvature–frequency cross-attention；频率表示本身不是首创。
- **TShape**：TShape 关注 shapelet / 形状匹配；TFC 以曲率二阶变化形成分支，并用多跨度 attention 汇聚局部几何证据。两者都覆盖 pattern-wise anomalies，但可比较的表示单元不同。
- **CrossAD**：CrossAD 用跨采样尺度粗到细映射失配；TFC 的 frequency bands / curvature spans 是同一输入内的视角与时间跨度，不能等同跨尺度正常映射。
- **CCM-TAD**：CCM-TAD 对多变量通道做静态相关聚类并使用因果时间 mask；TFC 为逐条 univariate 模型，反而存在中心差分未来点依赖问题。
- **CAPMix / When Model Meets New Normals**：前者校准合成异常边界，后者在线适应新正常；TFC 增加形状变化灵敏度，但没有在线新态安全更新或外因归因机制。

## 10. Questions

1. TFC 的 $\hat Y$ 如何形成 point-wise score 和优化 loss？多视角编码对应残差、预测误差还是其它判别目标？
2. 如果不使用 $u_t$，论文所称“mechanism shift inference”具体到什么程度？如何对照 workload / release / Trace 证明变化来源？
3. 中心差分需要下一采样点，temporal branch 未给 causal mask；真实流式场景的前视延迟和告警时刻如何定义？
4. 面对合法周期变更 / 业务高峰与故障同时出现，frequency branch 是否会把故障校准掉，curvature branch 是否仍能保留独立证据？
5. Event-F1、Best-F1 的阈值是否使用测试标签；无标签 validation 阈值下的 Event-F1 和 false alarm period 是多少？
6. 高频测量噪声下，curvature 放大与周期校准如何定量区分随机噪声、周期波动和机制改变？

## 11. Useful Definitions

- **Curvature evidence**：以中心二阶差分作为局部离散曲率 proxy；对转折 / 高阶结构敏感，也放大高频噪声。
- **Multi-Span Attention (MSA)**：多个 head 用不同相对距离 mask 读取曲率序列，形成多局部跨度的 pattern representation。
- **Two-stage fusion**：先由频率特征 cross-attend 曲率特征，再以输入条件路由权重融合 pattern embedding 与时间 embedding。
- **Event F1 (F1-E)**：把连续异常区间作为 event 计算的指标，与逐点 Best-F1 不同。

## 12. Tags

`TSAD` `univariate` `curvature` `second-difference` `frequency-domain` `multi-span-attention` `pattern-anomaly` `event-F1` `KDD-2026`
