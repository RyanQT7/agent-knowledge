# Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy

## 1. Metadata

- **Authors**: Tian Lan, Hao Duong Le, Jinbo Li, Wenjun He, Meng Wang, Chenghao Liu, Chen Zhang
- **Year / Venue**: 2026 / ICML（CCF A，依已人工确认清单）
- **Method name**: TimeRCD
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2026/ICML/Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf)
- **Proceedings**: [PMLR 306 paper page](https://proceedings.mlr.press/v306/lan26b.html)
- **Code**: [TimeRCD repository](https://github.com/thu-sail-lab/Time-RCD)
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

TimeRCD 以 Relative Context Discrepancy（RCD）为目标：Transformer 在一条待测序列的长上下文中比较局部 token 与其余时间结构，而不是把训练域学到的固定全局 normality 或 reconstruction error 当异常定义；通过 2.5B 点、含上下文依赖标签的纯合成语料预训练，推理只用 anomaly head， masked reconstruction 仅作训练期密集表示学习辅助。（§§2–3, Fig. 3–4, pp.3–6）

## 3. Background and Problem Definition

任务是 zero-shot TSAD：给定从未用于目标域训练的多变量序列 $X\in\mathbb{R}^{n\times d}$，输出每个时间点是否异常，不能在该目标数据集上继续训练或调参。（§2.1, p.3）

作者指出，reconstruction-error detection 存在目标不一致：平滑的细微异常可能被重建得很好而漏检；未见过的复杂正常模式也可能重建误差高而误报。另一方面，依靠目标训练域固定 normal distribution 的 discrepancy 方法在 zero-shot 时会遇到 representation conflict：相同形态在一个序列中可能是 dominant normal，在另一个上下文中反而是 anomaly。作者因此将“形态本身是否异常”改写成“该局部形态与当前序列已建立关系是否不一致”。（§1–2.1, pp.1–3, Fig. 1–2）

## 4. Core Challenges

1. **跨域 normality 不固定**：source-domain 同一形状的标签不能直接迁移到 target-domain；正常基线需由当前序列语境确定。（§2.1）
2. **短视野 detector 看不到长程规律**：contextual / periodic anomaly 需要观察远处的重复和既有结构。（§2.1–2.2）
3. **标签稀少且形态增强不够**：jitter / masking 等可扩大局部形态，但未必切断“某种外观 = normal/anomaly”的语义耦合。（§1–2）
4. **合成 supervision 必须教授相对性**：若同一个 waveform 在合成数据里总是同类，模型仍会背形状，不能学到 context-conditional 判别。（§2.1–2.3）
5. **长上下文的计算与窗口污染**：更长序列能建立稳定语境，但 attention 成本上升，且异常密集窗口可能污染语境参照。（§3.3; Appendix E.3, G, H）

## 5. Architecture Overview

```text
预训练：2.5B synthetic time-series points
  ├─ 随机 trend + multi-wave seasonality + heteroscedastic noise
  ├─ DAG + lagged ARX 建立 multivariate normal relations
  ├─ temporal / structural / causal anomalies 打破局部或跨变量 context
  └─ 给 root-cause segment 与 lagged descendants 生成 token labels

模型：instance-normalized multivariate series
  → non-overlapping variate-window patches（patch length 16）
  → flatten channel-window tokens
  → encoder-only Transformer（8 layers / 8 heads）
  ├─ masked reconstruction head（15% patched mask；训练辅助）
  └─ token-level anomaly head（训练与 inference 的 detector）

Inference：长上下文窗口（主结果固定 5,000）→ anomaly head 概率
```

（§2–3, Fig. 3–4, pp.3–5; Appendix C.4–D.5）

## 6. Method in Detail

### 6.1 RCD 的语境相对定义

RCD 认为 token $x_t$ 的异常性来自它与本序列上下文建立的关系，而非一个跨域固定的逐点取值分布。作者用 square-wave 与 spike 例子说明：在一种序列中 square wave 是主导正常节律，spike 偏离它；另一个序列中 spike 是 baseline，square wave 才是 contextual deviation。模型需同时看到足够多的重复结构形成 normal reference，并在训练中见到同一 morphological pattern 在不同上下文对应不同标签。（§2.1, Fig. 2, p.3）

在形式上，论文用 pairwise relation function $f(X_j,X_t)$ 表示 token $t$ 与上下文 token $j$ 的关系，并用 aggregation $g$ 得到 context-conditioned embedding $\mathrm{embedding}_{X_t}=g(\{f(X_j,X_t)\}_j)$；若 query token 与正常的 relational pattern 不一致，其 context embedding 会落在正常表示之外。作者将 self-attention 作为该 relation / aggregation 的实现直觉：$q_t=X_tW_Q, k_j=X_jW_K, v_j=X_jW_V$，attention weight 由 $q_t^\top k_j/\sqrt{d_k}$ 归一化。（Appendix C.1–C.3, pp.21–22）

### 6.2 变量-窗口 tokenization 和 encoder

输入各变量先做 instance normalization。将长度 $n$、$d$ 个 channel 的矩阵切成非重叠时间窗，窗长 $W=16$；每个 channel 的每个 window 经 projection 得到一个 token。flatten 所有 channel-window tokens 后送入标准 encoder-only Transformer。这样不只同一 channel 的长程 self-attention，也可建模 channel 间关系；模型无需专门的图结构模块。（§2.2, Fig. 3, pp.3–4）

主设置 8 层 Transformer、8 个 attention heads、$d_{model}=512$，投影维度 256；使用 AdamW、学习率 $5\times10^{-4}$、weight decay $10^{-5}$，最多 50 epochs，动态 batch size 从 64 起、验证 7 epochs 无改善 early stop。预训练样本以 patch/token 标签监督 anomaly head。（Appendix D.5）

### 6.3 Dual heads：训练时 reconstruction、推理时 anomaly

对 15% patch 做 mask，避免相邻时间点直接泄漏被 mask 的值；Masked reconstruction head 对 masked 输入位置重建值，为 encoder 提供密集 temporal dynamics 训练信号。Anomaly head 对每个 token 的 context embedding 输出 anomaly logit / probability。联合目标为：

$$\mathcal{L}=\lambda\,\|M\odot(X_{rec}-X)\|_2^2+\operatorname{BCE}(\sigma(X_{ano}),y),$$

其中 $M$ 是 mask、$y$ 是逐 token 标签；损失权重按论文默认设置。推理时完全移除 reconstruction head，也不计算 reconstruction error，只使用 anomaly head 的 sigmoid 概率作为分数。作者解释 reconstruction 是优化 anomaly head 的 training scaffold，不是最终 anomaly criterion。（§2.2, Eq. 1, pp.4–5; Appendix C.4）

### 6.4 Context-dependent synthetic corpus

论文构造四段数据 pipeline，目标是将 pattern morphology 与 label 拆开：

1. **建立单变量变化背景**：$x^{base}(t)=T(t)+S(t)+\epsilon(t)$。trend 混合确定性与 stochastic drift；seasonality $S(t)=\sum_k A_kw_k(2\pi f_kt+\phi_k;\theta_k)$，随机抽正弦、方波、小波等 wave atom、频率、相位；噪声含局部 volatility burst。随机参数避免所有序列共享一个固定周期。（§2.3, p.4; Appendix B）
2. **建立多变量正常关系**：先抽 DAG $G=(V,E)$，再用有滞后父变量的 ARX dynamics $z_i[t]=a_i z_i[t-1]+\sum_{j\in P(i)}b_{ij}x_j[t-\ell_{ij}]+c_i$ 生成潜在 causal process，最后把 baseline 与 causal process 混合。正常性因此还包括变量间及其 lagged dependency。（§2.3, p.5）
3. **破坏时间或关系 context**：超过 20 种注入包括 local shape outlier、频率 / 相位 / pattern replacement；endogenous anomaly 在混合前扰动根 channel baseline，使 deviation 沿 ARX 结构传播，保留结构连贯性但破坏跨变量一致性。（§2.3, p.5; Appendix B.4）
4. **生成标注**：exogenous anomaly 标记干预窗口；endogenous anomaly 标 root interval 并按 DAG lag 把受影响后代 channel 时段也打为正样本。（§2.3）

这种合成设计直接提供作者需要的 contextual supervision，不依赖公开真实 anomaly 标注；但生成器的趋势、季节、因果拓扑及异常操作族也是学到的监督范围。（分析边界）

### 6.5 预训练规模和推理协议

预训练只使用其自建 synthetic data，总量 2.5B time-series points；支持长度变化至 10k、不同 channel 数（1、8、12、16、20）。不是从目标评测集继续训练的 conventional “zero-shot adaptation”。主表固定 context window 5,000，严格 zero-shot 推理；Appendix E.3 的 1k–13k 是敏感性实验，不用于主表挑选每个数据集的最佳窗口。（Appendix D.5, E.1, E.3）

## 7. Experimental Design and Evidence

### 7.1 数据、baseline 和 metric

评测 16 个公开 benchmark：11 个 univariate（IOPS、MGAB、NAB、NEK、Power、SED、Stock、TODS、UCR、WSD、YAHOO）和 5 个 multivariate（MSL、PSM、SMAP、SMD、SWaT）。Zero-shot baselines 包含 DADA、MOMENT、TimesFM、Chronos、TimeMOE 等 foundation model，并纳入简单 moving-window variance detector MovingVar；full-shot 对照包括 TranAD、USAD、OmniAnomaly、Sub-PCA、DCdetector、TF-MAE、LOF、IForest 等按目标集训练的基线。论文注明可能有预训练泄漏的模型在相应比较中排除。（§3.1; Appendix D.1–D.3）

指标为 Affiliation-F1、F1-T、Standard F1、VUS-PR。主结果同一固定 5k context，不对目标数据微调。（§3.1）

### 7.2 零样本和 full-shot 比较

16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）

这些是 rank counts，不代表每个 dataset、每个 metric 都绝对领先；不同基线可用目标训练数据，Zero-shot / full-shot 结果应分别阅读。论文排除有潜在泄漏的 foundation models 后才汇总对应排名。（Table 1, Appendix D.3）

### 7.3 contextual anomaly 专门测试与窗口敏感性

作者用未参与预训练的 synthetic test suite 区分纯 point 与 contextual anomaly。对 contextual anomaly 的 Standard-F1，TimeRCD 为 0.827，而其它 zero-shot competitor 在该 split 明显下降；point anomaly 上则与其它强模型有竞争力。该试验控制了 anomaly 类型，支持长上下文有助于识别相对既有周期 / pattern 的偏离，但测试数据仍由同一框架的 generator 生成，不是完全独立来源的真实域外 context。（§3.3; Appendix E.2, Table 10）

窗口 1k–13k 敏感性显示最佳长度依任务而变：UCR、Power、SMAP、SMD 等长程结构数据整体受益于较长 context；天然短序列 YAHOO 近乎平坦。推论是 5k 是固定实验协议，不是所有数据的普适最优配置。（§3.3; Appendix E.3, Fig. 7 / Table 11）

### 7.4 合成数据与 inference head 消融

- 预训练数据消融中，context-dependent synthetic anomaly corpus 相较 synthetic normal + DADA anomaly injection 和 real + DADA 的加权平均表现更好；作者给出的核心加权指标约为 Aff-F 0.878、F1-T 0.569、Standard-F1 0.523、VUS-PR 0.478（Table 2, p.8）。它支持训练监督和异常语义质量重要，不单是加数据量。
- 350M、700M 到 2.5B 数据点的 scaling 整体上升，但并非每 dataset / metric 单调；2.5B 在 36 项 univariate 对比中拿 24 个第一名，不能从此推断已达到 scaling saturation。（Appendix E.4）
- 在 UCR 上的任务头 / inference ablation：joint reconstruction + anomaly head 且用 anomaly head inference 的 VUS-PR 33.57；相同训练但改用 reconstruction-error inference 为 4.08；reconstruction-only 约 3.35；anomaly-only 约 5.90；先预训练 reconstruction 再冻结 / 训练 anomaly head 26.11。结果支持“重建可辅助训练，但不能把重建误差当本方法推理分数”，且 joint fine-tuning 有作用。（Appendix E.5, Table 3）

## 8. Technical Contribution and Limitations

### 技术贡献

1. 将 zero-shot anomaly criterion 从固定 global normality 改为当前序列中的 contextual relational inconsistency。（§2.1）
2. 以任务特定的 context-dependent synthetic corpus 让相同局部形态在不同 context 中取得不同标签，并生成 causal lag propagation 标注。（§2.3）
3. 采用普通 Transformer + token anomaly head，masked reconstruction 作为训练目标但不以重建误差打分。（§2.2, Appendix C.4）
4. 在 16 datasets、4 metrics 的固定零样本协议中取得较多排名第一 / 第二，并对 contextual anomaly 提供专门测试。（§3）

### 作者指出或实验显示的限制

- 作者在讨论中指出：若推理窗口内 anomaly 比例太高，异常模式可能进入局部 normal context，Stock 上频繁 outlier 会被吸收，RCD 也会漏检。（§3.3 / Discussion）
- 一个固定 5k context 不是所有任务最佳；window sensitivity 显示最优长度随序列和异常范围改变。（Appendix E.3）
- 作者承认 reconstruction scaffold 的理论作用仍值得进一步解释，standard Transformer 在 very long sequence 下的计算效率也是限制。（Discussion; Appendix G）
- synthetic supervised task 由生成器结构定义；不同真实服务的合法状态、负载、版本 / 发布、故障关系未作为标签条件，也没有真实 Trace 或业务 event 输入。（方法和数据设置；分析边界）
- contextual anomaly 定量专题使用同一 synthetic framework 创建的测试族；它不等于在真实未知域证明上下文理解。（Appendix E.2）
- MovingVar 在部分场景有竞争力；增加复杂模型前仍需与简单统计规则做同协议比较。（§3.2）
- context 越长，整序列 token 自注意力和显存会增加；profile 在 15k 内可用，但不能外推到无界生产流。（Appendix G）

## 9. Reproduction and Reuse Value

论文提供 [TimeRCD code](https://github.com/thu-sail-lab/Time-RCD)，并完整说明合成生成流程、模型 / 优化器设置、4 项指标及固定 5k zero-shot protocol。复现时应分开记录主协议与 Appendix 的长度敏感性，不能用目标集选窗口后再称主表 strict zero-shot；也要确认 foundation-model training data 的 benchmark leakage 过滤是否一致。2.5B synthetic points 的生成与训练成本高，公开 code 并不消除硬件 / 时间需求。本次只阅读论文和附录，没有训练或跑复现实验。

## 10. Related Work

- **IMPACT**：两者都从局部样本相对关系重设 TSAD，但 TimeRCD 是 zero-shot、以整序列上下文作 normal reference；IMPACT 是 open-set supervised、以少量异常和 validation-risk influence 学习。
- **When Model Meets New Normals**：都针对 normality / context shift；TimeRCD 在一个输入序列内做 contextual comparison，后者通过 test-time adaptation 更新 detector 到新正常状态。
- **CAPMix**：更偏 KPI 噪声 / 动态运行条件与 normal behavior 建模，适合比较 synthetic context prior 和业务条件化先验。
- **CrossAD / MACE / Graph-MoE**：已有 cross-window、频域多模式和 memory/reference 思路；TimeRCD 的差异在于纯合成 context supervision 与固定 zero-shot inference。
- **TSB-AD / Quo Vadis**：评测协议背景；零样本排名应和运行点、阈值、标注与数据泄漏设置一起解读。
