# Knowledge Dossier — Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy

## 1. Basic Information

- **English title**: Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy
- **中文译名**：面向零样本时间序列异常检测基础模型：合成数据与相对上下文差异
- **Authors**: Tian Lan, Hao Duong Le, Jinbo Li, Wenjun He, Meng Wang, Chenghao Liu, Chen Zhang
- **Venue / year / CCF**: ICML 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf](../../sources/papers/tsad-2024-2026/2026/ICML/Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/thu-sail-lab/Time-RCD
- **Research area**: 合成数据预训练的零样本上下文异常检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 对未见目标数据集的 univariate / multivariate series 做 strict zero-shot、point-level TSAD；模型从当前序列内部推断 normality，不用目标集训练。（§2.1, p.3）
- **[实验支持]** 以 2.5B 点 synthetic-only 语料预训练，在 16 个公开 benchmark 上与 zero-shot foundation model 及 per-dataset full-shot baseline 比较。（§3.1; Appendix D.5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

任务是 zero-shot TSAD：给定从未用于目标域训练的多变量序列 $X\in\mathbb{R}^{n\times d}$，输出每个时间点是否异常，不能在该目标数据集上继续训练或调参。（§2.1, p.3）

作者指出，reconstruction-error detection 存在目标不一致：平滑的细微异常可能被重建得很好而漏检；未见过的复杂正常模式也可能重建误差高而误报。另一方面，依靠目标训练域固定 normal distribution 的 discrepancy 方法在 zero-shot 时会遇到 representation conflict：相同形态在一个序列中可能是 dominant normal，在另一个上下文中反而是 anomaly。作者因此将“形态本身是否异常”改写成“该局部形态与当前序列已建立关系是否不一致”。（§1–2.1, pp.1–3, Fig. 1–2）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **跨域 normality 不固定**：source-domain 同一形状的标签不能直接迁移到 target-domain；正常基线需由当前序列语境确定。（§2.1）
2. **短视野 detector 看不到长程规律**：contextual / periodic anomaly 需要观察远处的重复和既有结构。（§2.1–2.2）
3. **标签稀少且形态增强不够**：jitter / masking 等可扩大局部形态，但未必切断“某种外观 = normal/anomaly”的语义耦合。（§1–2）
4. **合成 supervision 必须教授相对性**：若同一个 waveform 在合成数据里总是同类，模型仍会背形状，不能学到 context-conditional 判别。（§2.1–2.3）
5. **长上下文的计算与窗口污染**：更长序列能建立稳定语境，但 attention 成本上升，且异常密集窗口可能污染语境参照。（§3.3; Appendix E.3, G, H）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 常见 reconstruction-error inference 与训练目标不一致；依赖固定 source-domain global normal distribution 的 discrepancy 方法也难适应 zero-shot concept shift。（§1–2）
- **[分析推断]** 时间序列内的相对 pattern 不会自动识别 workload、release、用户行为等外部语义状态。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

TimeRCD 以 Relative Context Discrepancy（RCD）为目标：Transformer 在一条待测序列的长上下文中比较局部 token 与其余时间结构，而不是把训练域学到的固定全局 normality 或 reconstruction error 当异常定义；通过 2.5B 点、含上下文依赖标签的纯合成语料预训练，推理只用 anomaly head， masked reconstruction 仅作训练期密集表示学习辅助。（§§2–3, Fig. 3–4, pp.3–6）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：跨域 normality 不固定：source-domain 同一形状的标签不能直接迁移到 target-domain；正常基线需由当前序列语境确定。（§2.1）
- **C2（第4节挑战）**：短视野 detector 看不到长程规律：contextual / periodic anomaly 需要观察远处的重复和既有结构。（§2.1–2.2）
- **C3（第4节挑战）**：标签稀少且形态增强不够：jitter / masking 等可扩大局部形态，但未必切断“某种外观 = normal/anomaly”的语义耦合。（§1–2）
- **C4（第4节挑战）**：合成 supervision 必须教授相对性：若同一个 waveform 在合成数据里总是同类，模型仍会背形状，不能学到 context-conditional 判别。（§2.1–2.3）
- **C5（第4节挑战）**：长上下文的计算与窗口污染：更长序列能建立稳定语境，但 attention 成本上升，且异常密集窗口可能污染语境参照。（§3.3; Appendix E.3, G, H）

### 7.1 RCD

- **作者技术描述**：**[作者主张] RCD**：token 与长时上下文建立 pairwise relation，经 Transformer self-attention 聚合；contextual relational deviation 交 anomaly head 分类。（Appendix C.1–C.4, pp.21–22）
- **对应挑战**：C5（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 RCD 的语境相对定义”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Variate-window Transformer

- **作者技术描述**：**[作者主张] Variate-window Transformer**：instance-normalized multivariate series 切成 patch 16，flatten 各 channel-window tokens，使 attention 可跨时间 / channel 建模；8 层、8 heads。（§2.2; Appendix D.5）
- **对应挑战**：C5（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 合成语料

- **作者技术描述**：**[作者主张] 合成语料**：随机 trend + multi-wave seasonality + volatility → DAG / lagged ARX 多变量关系 → 20+ temporal 与 causal violations → root / descendants token labels。（§2.3, p.5; Appendix B）
- **对应挑战**：C5（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 双头分工

- **作者技术描述**：**[作者主张] 双头分工**：15% patch masking 的 reconstruction 作训练 scaffold；联合 BCE anomaly supervision；inference 移除 reconstruction head，仅用 anomaly head。（§2.2, Eq. 1; Appendix C.4）
- **对应挑战**：C5（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：6.2 变量-窗口 tokenization 和 encoder。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 RCD 的语境相对定义

RCD 认为 token $x_t$ 的异常性来自它与本序列上下文建立的关系，而非一个跨域固定的逐点取值分布。作者用 square-wave 与 spike 例子说明：在一种序列中 square wave 是主导正常节律，spike 偏离它；另一个序列中 spike 是 baseline，square wave 才是 contextual deviation。模型需同时看到足够多的重复结构形成 normal reference，并在训练中见到同一 morphological pattern 在不同上下文对应不同标签。（§2.1, Fig. 2, p.3）

在形式上，论文用 pairwise relation function $f(X_j,X_t)$ 表示 token $t$ 与上下文 token $j$ 的关系，并用 aggregation $g$ 得到 context-conditioned embedding $\mathrm{embedding}_{X_t}=g(\{f(X_j,X_t)\}_j)$；若 query token 与正常的 relational pattern 不一致，其 context embedding 会落在正常表示之外。作者将 self-attention 作为该 relation / aggregation 的实现直觉：$q_t=X_tW_Q, k_j=X_jW_K, v_j=X_jW_V$，attention weight 由 $q_t^\top k_j/\sqrt{d_k}$ 归一化。（Appendix C.1–C.3, pp.21–22）

#### 6.2 变量-窗口 tokenization 和 encoder

输入各变量先做 instance normalization。将长度 $n$、$d$ 个 channel 的矩阵切成非重叠时间窗，窗长 $W=16$；每个 channel 的每个 window 经 projection 得到一个 token。flatten 所有 channel-window tokens 后送入标准 encoder-only Transformer。这样不只同一 channel 的长程 self-attention，也可建模 channel 间关系；模型无需专门的图结构模块。（§2.2, Fig. 3, pp.3–4）

主设置 8 层 Transformer、8 个 attention heads、$d_{model}=512$，投影维度 256；使用 AdamW、学习率 $5\times10^{-4}$、weight decay $10^{-5}$，最多 50 epochs，动态 batch size 从 64 起、验证 7 epochs 无改善 early stop。预训练样本以 patch/token 标签监督 anomaly head。（Appendix D.5）

#### 6.3 Dual heads：训练时 reconstruction、推理时 anomaly

对 15% patch 做 mask，避免相邻时间点直接泄漏被 mask 的值；Masked reconstruction head 对 masked 输入位置重建值，为 encoder 提供密集 temporal dynamics 训练信号。Anomaly head 对每个 token 的 context embedding 输出 anomaly logit / probability。联合目标为：

$$\mathcal{L}=\lambda\,\|M\odot(X_{rec}-X)\|_2^2+\operatorname{BCE}(\sigma(X_{ano}),y),$$

其中 $M$ 是 mask、$y$ 是逐 token 标签；损失权重按论文默认设置。推理时完全移除 reconstruction head，也不计算 reconstruction error，只使用 anomaly head 的 sigmoid 概率作为分数。作者解释 reconstruction 是优化 anomaly head 的 training scaffold，不是最终 anomaly criterion。（§2.2, Eq. 1, pp.4–5; Appendix C.4）

#### 6.4 Context-dependent synthetic corpus

论文构造四段数据 pipeline，目标是将 pattern morphology 与 label 拆开：

1. **建立单变量变化背景**：$x^{base}(t)=T(t)+S(t)+\epsilon(t)$。trend 混合确定性与 stochastic drift；seasonality $S(t)=\sum_k A_kw_k(2\pi f_kt+\phi_k;\theta_k)$，随机抽正弦、方波、小波等 wave atom、频率、相位；噪声含局部 volatility burst。随机参数避免所有序列共享一个固定周期。（§2.3, p.4; Appendix B）
2. **建立多变量正常关系**：先抽 DAG $G=(V,E)$，再用有滞后父变量的 ARX dynamics $z_i[t]=a_i z_i[t-1]+\sum_{j\in P(i)}b_{ij}x_j[t-\ell_{ij}]+c_i$ 生成潜在 causal process，最后把 baseline 与 causal process 混合。正常性因此还包括变量间及其 lagged dependency。（§2.3, p.5）
3. **破坏时间或关系 context**：超过 20 种注入包括 local shape outlier、频率 / 相位 / pattern replacement；endogenous anomaly 在混合前扰动根 channel baseline，使 deviation 沿 ARX 结构传播，保留结构连贯性但破坏跨变量一致性。（§2.3, p.5; Appendix B.4）
4. **生成标注**：exogenous anomaly 标记干预窗口；endogenous anomaly 标 root interval 并按 DAG lag 把受影响后代 channel 时段也打为正样本。（§2.3）

这种合成设计直接提供作者需要的 contextual supervision，不依赖公开真实 anomaly 标注；但生成器的趋势、季节、因果拓扑及异常操作族也是学到的监督范围。（分析边界）

#### 6.5 预训练规模和推理协议

预训练只使用其自建 synthetic data，总量 2.5B time-series points；支持长度变化至 10k、不同 channel 数（1、8、12、16、20）。不是从目标评测集继续训练的 conventional “zero-shot adaptation”。主表固定 context window 5,000，严格 zero-shot 推理；Appendix E.3 的 1k–13k 是敏感性实验，不用于主表挑选每个数据集的最佳窗口。（Appendix D.5, E.1, E.3）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.3 Dual heads：训练时 reconstruction、推理时 anomaly；6.5 预训练规模和推理协议；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.3 Dual heads：训练时 reconstruction、推理时 anomaly；6.5 预训练规模和推理协议及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

TimeRCD 以 Relative Context Discrepancy（RCD）为目标：Transformer 在一条待测序列的长上下文中比较局部 token 与其余时间结构，而不是把训练域学到的固定全局 normality 或 reconstruction error 当异常定义；通过 2.5B 点、含上下文依赖标签的纯合成语料预训练，推理只用 anomaly head， masked reconstruction 仅作训练期密集表示学习辅助。（§§2–3, Fig. 3–4, pp.3–6）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 数据、baseline 和 metric

评测 16 个公开 benchmark：11 个 univariate（IOPS、MGAB、NAB、NEK、Power、SED、Stock、TODS、UCR、WSD、YAHOO）和 5 个 multivariate（MSL、PSM、SMAP、SMD、SWaT）。Zero-shot baselines 包含 DADA、MOMENT、TimesFM、Chronos、TimeMOE 等 foundation model，并纳入简单 moving-window variance detector MovingVar；full-shot 对照包括 TranAD、USAD、OmniAnomaly、Sub-PCA、DCdetector、TF-MAE、LOF、IForest 等按目标集训练的基线。论文注明可能有预训练泄漏的模型在相应比较中排除。（§3.1; Appendix D.1–D.3）

指标为 Affiliation-F1、F1-T、Standard F1、VUS-PR。主结果同一固定 5k context，不对目标数据微调。（§3.1）

#### 7.2 零样本和 full-shot 比较

16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）

这些是 rank counts，不代表每个 dataset、每个 metric 都绝对领先；不同基线可用目标训练数据，Zero-shot / full-shot 结果应分别阅读。论文排除有潜在泄漏的 foundation models 后才汇总对应排名。（Table 1, Appendix D.3）

#### 7.3 contextual anomaly 专门测试与窗口敏感性

作者用未参与预训练的 synthetic test suite 区分纯 point 与 contextual anomaly。对 contextual anomaly 的 Standard-F1，TimeRCD 为 0.827，而其它 zero-shot competitor 在该 split 明显下降；point anomaly 上则与其它强模型有竞争力。该试验控制了 anomaly 类型，支持长上下文有助于识别相对既有周期 / pattern 的偏离，但测试数据仍由同一框架的 generator 生成，不是完全独立来源的真实域外 context。（§3.3; Appendix E.2, Table 10）

窗口 1k–13k 敏感性显示最佳长度依任务而变：UCR、Power、SMAP、SMD 等长程结构数据整体受益于较长 context；天然短序列 YAHOO 近乎平坦。推论是 5k 是固定实验协议，不是所有数据的普适最优配置。（§3.3; Appendix E.3, Fig. 7 / Table 11）

#### 7.4 合成数据与 inference head 消融

- 预训练数据消融中，context-dependent synthetic anomaly corpus 相较 synthetic normal + DADA anomaly injection 和 real + DADA 的加权平均表现更好；作者给出的核心加权指标约为 Aff-F 0.878、F1-T 0.569、Standard-F1 0.523、VUS-PR 0.478（Table 2, p.8）。它支持训练监督和异常语义质量重要，不单是加数据量。
- 350M、700M 到 2.5B 数据点的 scaling 整体上升，但并非每 dataset / metric 单调；2.5B 在 36 项 univariate 对比中拿 24 个第一名，不能从此推断已达到 scaling saturation。（Appendix E.4）
- 在 UCR 上的任务头 / inference ablation：joint reconstruction + anomaly head 且用 anomaly head inference 的 VUS-PR 33.57；相同训练但改用 reconstruction-error inference 为 4.08；reconstruction-only 约 3.35；anomaly-only 约 5.90；先预训练 reconstruction 再冻结 / 训练 anomaly head 26.11。结果支持“重建可辅助训练，但不能把重建误差当本方法推理分数”，且 joint fine-tuning 有作用。（Appendix E.5, Table 3）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

作者承认 reconstruction scaffold 的理论作用仍值得进一步解释，standard Transformer 在 very long sequence 下的计算效率也是限制。（Discussion; Appendix G）

### B. 基于方法与实验的分析推断

精读笔记未单独归类；分析推断需依据第 8–9 节的方法假设和实验范围，不能表述为已证实缺陷。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

作者在讨论中指出：若推理窗口内 anomaly 比例太高，异常模式可能进入局部 normal context，Stock 上频繁 outlier 会被吸收，RCD 也会漏检。（§3.3 / Discussion）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

一个固定 5k context 不是所有任务最佳；window sensitivity 显示最优长度随序列和异常范围改变。（Appendix E.3）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

synthetic supervised task 由生成器结构定义；不同真实服务的合法状态、负载、版本 / 发布、故障关系未作为标签条件，也没有真实 Trace 或业务 event 输入。（方法和数据设置；分析边界）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

contextual anomaly 定量专题使用同一 synthetic framework 创建的测试族；它不等于在真实未知域证明上下文理解。（Appendix E.2）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

MovingVar 在部分场景有竞争力；增加复杂模型前仍需与简单统计规则做同协议比较。（§3.2）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 作者指出或实验显示的限制

context 越长，整序列 token 自注意力和显存会增加；profile 在 15k 内可用，但不能外推到无界生产流。（Appendix G）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 研究 context 污染检测、多个 reference state / robust consensus，使长窗中 anomaly 密集时不把故障吸收入 normality。
- **[分析推断]** 在真实业务的 workload / release context 下比较“序列内相对模式”与“业务状态条件化 normality”，测试负载变化与故障并发。
- **[分析推断]** 对合成机制做 generator-held-out、拓扑-held-out 和真实 Trace / fault injection 外部验证。
- **[分析推断]** 固定 5k 主协议下补充业务 false-alarm budget、事件延迟、显存 / latency 预算与 threshold calibration。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **IMPACT**：两者都从局部样本相对关系重设 TSAD，但 TimeRCD 是 zero-shot、以整序列上下文作 normal reference；IMPACT 是 open-set supervised、以少量异常和 validation-risk influence 学习。
- **When Model Meets New Normals**：都针对 normality / context shift；TimeRCD 在一个输入序列内做 contextual comparison，后者通过 test-time adaptation 更新 detector 到新正常状态。
- **CAPMix**：更偏 KPI 噪声 / 动态运行条件与 normal behavior 建模，适合比较 synthetic context prior 和业务条件化先验。
- **CrossAD / MACE / Graph-MoE**：已有 cross-window、频域多模式和 memory/reference 思路；TimeRCD 的差异在于纯合成 context supervision 与固定 zero-shot inference。
- **TSB-AD / Quo Vadis**：评测协议背景；零样本排名应和运行点、阈值、标注与数据泄漏设置一起解读。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §1–2.1, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.1–2.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §1–2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.1–2.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.3 | 精读笔记保留的原文定位 |
| Method / formulas | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2–3, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.1, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.2, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.2, Eq. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §2.3 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.2, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.3, Table 10 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.3, Fig. 7 / Table 11 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | Table 3 | 精读笔记保留的原文定位 |
| Limitations | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.3 | 精读笔记保留的原文定位 |
| Limitations | Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf | §3.2 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "time-rcd",
  "title_en": "Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy",
  "title_zh": "面向零样本时间序列异常检测基础模型：合成数据与相对上下文差异",
  "authors": [
    "Tian Lan",
    "Hao Duong Le",
    "Jinbo Li",
    "Wenjun He",
    "Meng Wang",
    "Chenghao Liu",
    "Chen Zhang"
  ],
  "year": 2026,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ICML/Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
  "reading_note_path": "papers/time-rcd/notes.md",
  "code_url": "https://github.com/thu-sail-lab/Time-RCD",
  "research_area": "合成数据预训练的零样本上下文异常检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] 对未见目标数据集的 univariate / multivariate series 做 strict zero-shot、point-level TSAD；模型从当前序列内部推断 normality，不用目标集训练。（§2.1, p.3） - [实验支持] 以 2.5B 点 synthetic-only 语料预训练，在 16 个公开 benchmark 上与 zero-shot foundation model 及 per-dataset full-shot baseline 比较。（§3.1; Appendix D.5）",
  "research_problem": "任务是 zero-shot TSAD：给定从未用于目标域训练的多变量序列 $X\\in\\mathbb{R}^{n\\times d}$，输出每个时间点是否异常，不能在该目标数据集上继续训练或调参。（§2.1, p.3） 作者指出，reconstruction-error detection 存在目标不一致：平滑的细微异常可能被重建得很好而漏检；未见过的复杂正常模式也可能重建误差高而误报。另一方面，依靠目标训练域固定 normal distribution 的 discrepancy 方法在 zero-shot 时会遇到 representation conflict：相同形态在一个序列中可能是 dominant normal，在另一个上下文中反而是 anomaly。作者因此将“形态本身是否异常”改写成“该局部形态与当前序列已建立关系是否不一致”。（§1–2.1, pp.1–3, Fig. 1–2）",
  "core_challenges": [
    "跨域 normality 不固定：source-domain 同一形状的标签不能直接迁移到 target-domain；正常基线需由当前序列语境确定。（§2.1）",
    "短视野 detector 看不到长程规律：contextual / periodic anomaly 需要观察远处的重复和既有结构。（§2.1–2.2）",
    "标签稀少且形态增强不够：jitter / masking 等可扩大局部形态，但未必切断“某种外观 = normal/anomaly”的语义耦合。（§1–2）",
    "合成 supervision 必须教授相对性：若同一个 waveform 在合成数据里总是同类，模型仍会背形状，不能学到 context-conditional 判别。（§2.1–2.3）",
    "长上下文的计算与窗口污染：更长序列能建立稳定语境，但 attention 成本上升，且异常密集窗口可能污染语境参照。（§3.3; Appendix E.3, G, H）"
  ],
  "existing_method_limits": [
    "[作者主张] 常见 reconstruction-error inference 与训练目标不一致；依赖固定 source-domain global normal distribution 的 discrepancy 方法也难适应 zero-shot concept shift。（§1–2）",
    "[分析推断] 时间序列内的相对 pattern 不会自动识别 workload、release、用户行为等外部语义状态。"
  ],
  "core_idea": "TimeRCD 以 Relative Context Discrepancy（RCD）为目标：Transformer 在一条待测序列的长上下文中比较局部 token 与其余时间结构，而不是把训练域学到的固定全局 normality 或 reconstruction error 当异常定义；通过 2.5B 点、含上下文依赖标签的纯合成语料预训练，推理只用 anomaly head， masked reconstruction 仅作训练期密集表示学习辅助。（§§2–3, Fig. 3–4, pp.3–6）",
  "technical_innovations": [
    {
      "name": "RCD",
      "author_claim": "**[作者主张] RCD**：token 与长时上下文建立 pairwise relation，经 Transformer self-attention 聚合；contextual relational deviation 交 anomaly head 分类。（Appendix C.1–C.4, pp.21–22）",
      "challenge_ids": [
        "C5"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 RCD 的语境相对定义",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] RCD**：token 与长时上下文建立 pairwise relation，经 Transformer self-attention 聚合；contextual relational deviation 交 anomaly head 分类。（Appendix C.1–C.4, pp.21–22）"
    },
    {
      "name": "Variate-window Transformer",
      "author_claim": "**[作者主张] Variate-window Transformer**：instance-normalized multivariate series 切成 patch 16，flatten 各 channel-window tokens，使 attention 可跨时间 / channel 建模；8 层、8 heads。（§2.2; Appendix D.5）",
      "challenge_ids": [
        "C5"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Variate-window Transformer**：instance-normalized multivariate series 切成 patch 16，flatten 各 channel-window tokens，使 attention 可跨时间 / channel 建模；8 层、8 heads。（§2.2; Appendix D.5）"
    },
    {
      "name": "合成语料",
      "author_claim": "**[作者主张] 合成语料**：随机 trend + multi-wave seasonality + volatility → DAG / lagged ARX 多变量关系 → 20+ temporal 与 causal violations → root / descendants token labels。（§2.3, p.5; Appendix B）",
      "challenge_ids": [
        "C5"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 合成语料**：随机 trend + multi-wave seasonality + volatility → DAG / lagged ARX 多变量关系 → 20+ temporal 与 causal violations → root / descendants token labels。（§2.3, p.5; Appendix B）"
    },
    {
      "name": "双头分工",
      "author_claim": "**[作者主张] 双头分工**：15% patch masking 的 reconstruction 作训练 scaffold；联合 BCE anomaly supervision；inference 移除 reconstruction head，仅用 anomaly head。（§2.2, Eq. 1; Appendix C.4）",
      "challenge_ids": [
        "C5"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 双头分工**：15% patch masking 的 reconstruction 作训练 scaffold；联合 BCE anomaly supervision；inference 移除 reconstruction head，仅用 anomaly head。（§2.2, Eq. 1; Appendix C.4）"
    }
  ],
  "methodology": {
    "architecture": "text 预训练：2.5B synthetic time-series points ├─ 随机 trend + multi-wave seasonality + heteroscedastic noise ├─ DAG + lagged ARX 建立 multivariate normal relations ├─ temporal / structural / causal anomalies 打破局部或跨变量 context └─ 给 root-cause segment 与 lagged descendants 生成 token labels 模型：instance-normalized multivariate series → non-overlapping variate-window patches（patch length 16） → flatten channel-window tokens → encoder-only Transformer（8 layers / 8 heads） ├─ masked reconstruction head（15% patched mask；训练辅助） └─ token-level anomaly head（训练与 inference 的 detector） Inference：长上下文窗口（主结果固定 5,000）→ anomaly head 概率 （§2–3, Fig. 3–4, pp.3–5; Appendix C.4–D.5）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 RCD 的语境相对定义",
      "6.2 变量-窗口 tokenization 和 encoder",
      "6.3 Dual heads：训练时 reconstruction、推理时 anomaly",
      "6.4 Context-dependent synthetic corpus",
      "6.5 预训练规模和推理协议"
    ],
    "key_formulas": [
      "Eq. (1)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "TimeRCD 以 Relative Context Discrepancy（RCD）为目标：Transformer 在一条待测序列的长上下文中比较局部 token 与其余时间结构，而不是把训练域学到的固定全局 normality 或 reconstruction error 当异常定义；通过 2.5B 点、含上下文依赖标签的纯合成语料预训练，推理只用 anomaly head， masked reconstruction 仅作训练期密集表示学习辅助。（§§2–3, Fig. 3–4, pp.3–6）"
  },
  "experimental_evidence": {
    "datasets": [
      "评测 16 个公开 benchmark：11 个 univariate（IOPS、MGAB、NAB、NEK、Power、SED、Stock、TODS、UCR、WSD、YAHOO）和 5 个 multivariate（MSL、PSM、SMAP、SMD、SWaT）。Zero-shot baselines 包含 DADA、MOMENT、TimesFM、Chronos、TimeMOE 等 foundation model，并纳入简单 moving-window variance detector MovingVar；…",
      "16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）",
      "这些是 rank counts，不代表每个 dataset、每个 metric 都绝对领先；不同基线可用目标训练数据，Zero-shot / full-shot 结果应分别阅读。论文排除有潜在泄漏的 foundation models 后才汇总对应排名。（Table 1, Appendix D.3）",
      "- 预训练数据消融中，context-dependent synthetic anomaly corpus 相较 synthetic normal + DADA anomaly injection 和 real + DADA 的加权平均表现更好；作者给出的核心加权指标约为 Aff-F 0.878、F1-T 0.569、Standard-F1 0.523、VUS-PR 0.478（Table 2, p.8）。它支持训练监督和异常语义质量重要，不单是加数据量。 - 350M、700M 到 2.5B 数据点的 scaling 整体上升，但并非每 dataset / metric 单调；…"
    ],
    "baselines": [
      "### 7.1 数据、baseline 和 metric",
      "评测 16 个公开 benchmark：11 个 univariate（IOPS、MGAB、NAB、NEK、Power、SED、Stock、TODS、UCR、WSD、YAHOO）和 5 个 multivariate（MSL、PSM、SMAP、SMD、SWaT）。Zero-shot baselines 包含 DADA、MOMENT、TimesFM、Chronos、TimeMOE 等 foundation model，并纳入简单 moving-window variance detector MovingVar；…",
      "16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）"
    ],
    "metrics": [
      "### 7.1 数据、baseline 和 metric",
      "指标为 Affiliation-F1、F1-T、Standard F1、VUS-PR。主结果同一固定 5k context，不对目标数据微调。（§3.1）",
      "16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）",
      "这些是 rank counts，不代表每个 dataset、每个 metric 都绝对领先；不同基线可用目标训练数据，Zero-shot / full-shot 结果应分别阅读。论文排除有潜在泄漏的 foundation models 后才汇总对应排名。（Table 1, Appendix D.3）"
    ],
    "main_results": [
      "指标为 Affiliation-F1、F1-T、Standard F1、VUS-PR。主结果同一固定 5k context，不对目标数据微调。（§3.1）",
      "16 datasets × 4 metrics 共 64 个 zero-shot case 中，TimeRCD 38 次第 1、14 次第 2；与目标集 full-shot baseline 对比则 35 次第 1、3 次第 2。作者也承认 MovingVar 在 variance shift 与异常定义对齐的数据集上有竞争力，因此结果不能归结为“神经模型总优于简单统计量”。（Table 1, pp.6–7; §3.2）",
      "这些是 rank counts，不代表每个 dataset、每个 metric 都绝对领先；不同基线可用目标训练数据，Zero-shot / full-shot 结果应分别阅读。论文排除有潜在泄漏的 foundation models 后才汇总对应排名。（Table 1, Appendix D.3）",
      "作者用未参与预训练的 synthetic test suite 区分纯 point 与 contextual anomaly。对 contextual anomaly 的 Standard-F1，TimeRCD 为 0.827，而其它 zero-shot competitor 在该 split 明显下降；point anomaly 上则与其它强模型有竞争力。该试验控制了 anomaly 类型，支持长上下文有助于识别相对既有周期 / pattern 的偏离，但测试数据仍由同一框架的 generator 生成，不是完全独立来源的真实域外 context。（§3.3; Appendix E.2, Table 10）",
      "窗口 1k–13k 敏感性显示最佳长度依任务而变：UCR、Power、SMAP、SMD 等长程结构数据整体受益于较长 context；天然短序列 YAHOO 近乎平坦。推论是 5k 是固定实验协议，不是所有数据的普适最优配置。（§3.3; Appendix E.3, Fig. 7 / Table 11）"
    ],
    "ablations": [
      "### 7.3 contextual anomaly 专门测试与窗口敏感性",
      "窗口 1k–13k 敏感性显示最佳长度依任务而变：UCR、Power、SMAP、SMD 等长程结构数据整体受益于较长 context；天然短序列 YAHOO 近乎平坦。推论是 5k 是固定实验协议，不是所有数据的普适最优配置。（§3.3; Appendix E.3, Fig. 7 / Table 11）",
      "### 7.4 合成数据与 inference head 消融",
      "- 预训练数据消融中，context-dependent synthetic anomaly corpus 相较 synthetic normal + DADA anomaly injection 和 real + DADA 的加权平均表现更好；作者给出的核心加权指标约为 Aff-F 0.878、F1-T 0.569、Standard-F1 0.523、VUS-PR 0.478（Table 2, p.8）。它支持训练监督和异常语义质量重要，不单是加数据量。 - 350M、700M 到 2.5B 数据点的 scaling 整体上升，但并非每 dataset / metric 单调；…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "作者承认 reconstruction scaffold 的理论作用仍值得进一步解释，standard Transformer 在 very long sequence 下的计算效率也是限制。（Discussion; Appendix G）"
    ],
    "reasoned_inference": [
      "见档案 §10.B；保持为分析而非已证实结论"
    ],
    "evidence_gaps": [
      "作者在讨论中指出：若推理窗口内 anomaly 比例太高，异常模式可能进入局部 normal context，Stock 上频繁 outlier 会被吸收，RCD 也会漏检。（§3.3 / Discussion）",
      "一个固定 5k context 不是所有任务最佳；window sensitivity 显示最优长度随序列和异常范围改变。（Appendix E.3）",
      "synthetic supervised task 由生成器结构定义；不同真实服务的合法状态、负载、版本 / 发布、故障关系未作为标签条件，也没有真实 Trace 或业务 event 输入。（方法和数据设置；分析边界）",
      "contextual anomaly 定量专题使用同一 synthetic framework 创建的测试族；它不等于在真实未知域证明上下文理解。（Appendix E.2）",
      "MovingVar 在部分场景有竞争力；增加复杂模型前仍需与简单统计规则做同协议比较。（§3.2）",
      "context 越长，整序列 token 自注意力和显存会增加；profile 在 15k 内可用，但不能外推到无界生产流。（Appendix G）"
    ]
  },
  "research_implications": [
    "- [分析推断] 研究 context 污染检测、多个 reference state / robust consensus，使长窗中 anomaly 密集时不把故障吸收入 normality。 - [分析推断] 在真实业务的 workload / release context 下比较“序列内相对模式”与“业务状态条件化 normality”，测试负载变化与故障并发。 - [分析推断] 对合成机制做 generator-held-out、拓扑-held-out 和真实 Trace / fault injection 外部验证。 - [分析推断] 固定 5k 主协议下补充业务 false-alarm budget、事件延迟、显存 / latency 预算与 threshold calibration。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "crossad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "graph-moe",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "impact",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "time-rcd",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§1–2.1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.1–2.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.1–2.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§3.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2–3, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.1, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.2, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf",
      "locator": "§2.2, Eq. 1",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "741be6e8a93e9813fcee118c3f9d51336c576b4cb4c9991ff22c6c73edbd13d5",
    "reading_note_sha256": "6adedae8af9676307f36dc09460c9cdfed33ebc7674d8ece734931b0063ce85d",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "e087ccddf42eae7b68d73c756846f2d2309e1288b715c3f2f321bbda0b62af2a"
  },
  "knowledge_card_path": "papers/time-rcd/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
