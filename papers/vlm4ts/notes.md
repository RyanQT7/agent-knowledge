# Harnessing Vision-Language Models for Time Series Anomaly Detection

## 1. Metadata

- **Authors**: Zelin He, Sarah Alnegheimish, Matthew Reimherr
- **Year / Venue**: 2026 / AAAI（CCF A，依已人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2026/AAAI/Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf)
- **Public source**: [AAAI PDF](https://ojs.aaai.org/index.php/AAAI/article/download/39319/43280)
- **Code**: [VLM4TS repository](https://github.com/ZLHe0/VLM4TS)（论文 PDF p.1）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

VLM4TS 将无轴、统一尺度的滑窗折线图交给预训练 CLIP 进行多尺度跨窗口 patch 匹配，先产生局部 anomaly candidate，再把全序列图和候选区间交给 GPT-4o 按全局趋势核验，从而在不进行时序域训练的条件下结合局部定位与长程视觉语境。（§§3–4, Fig. 3, pp.3–6）

## 3. Background and Problem Definition

论文针对 univariate time series interval detection：给定 $x_{1:T}$，输出未知数量的异常时间区间 $A=\{(t_s,t_e)_i\}$。作者强调，一个高值是否异常不能只看幅度：若它在该序列历史中反复出现可能是正常波动；缓慢 drift 也可能偏离已建立趋势而异常。传统数值 detector 依赖特定数据训练或归纳偏置，直接将 VLM 用于时序又会面临输入分辨率、时间上下文和 token 成本之间的冲突。（§1、§3, pp.1, 3）

核心设计目标是把局部细节检测与整个序列的上下文解释分开：第一阶段高召回筛候选，第二阶段跨模态模型用全局趋势校验候选并补漏。（§3, Fig. 3）

## 4. Core Challenges

1. **时间跨度与视觉分辨率冲突**：一张图很难同时显示长序列全局规律和尖峰的精确位置；滚动小窗又缺少长程背景。（§3, pp.3–4）
2. **视觉预训练和时序图的域差异**：CLIP 的图像预训练并非时序专用，如何在 patch 级别利用其视觉特征检测线图异常并不显然。（§3.1）
3. **异常位置的候选筛选**：没有目标域训练标签时，需要从大量正常窗口形成参照，利用异常相对稀少的假设发现局部偏离。（§3.1）
4. **VLM 推理费用**：对每个局部窗口逐一询问多模态模型会造成高 token 消耗，也会让每个判断看不到整个序列。（§1, §3.2）
5. **异常密集时稀有性假设失效**：作者观察到 Yahoo A3/A4 的密集合成异常容易被模型解释成较大模式中的 fluctuation。（§4, p.6；Appendix D）

## 5. Architecture Overview

```text
univariate series x[1:T]
  ├─ Stage 1 / ViT4TS
  │    rolling windows (Lw=224, stride=56)
  │    → clean line plots (shared full-series y limits)
  │    → CLIP ViT-B/16 patch features
  │    → 1×1 / 2×2 / 3×3 multi-scale pooling
  │    → cross-window nearest-patch dissimilarity + median reference
  │    → harmonic scale fusion → timestamp score map
  │    → Gaussian score thresholds → candidate intervals
  └─ Stage 2 / VLM4TS
       full-series plot with axes + candidate intervals
       → GPT-4o integrates full-series trend and candidate evidence
       → JSON intervals / confidence / rationale
       → discard confidence-1 proposals
```

（§§3.1–3.2, Fig. 3, pp.3–5; Appendix B, pp.10–12）

## 6. Method in Detail

### 6.1 输入图像与滑窗

阶段一主要使用单变量输入。以长度 $L_w$ 的窗口沿序列滚动，步长 $L_s=\lfloor L_w/4\rfloor$；默认输入边长为 224、步长 56。每窗绘制成正方形干净折线图，隐藏轴刻度、图例等非信息元素；所有局部图共用从整条序列得到的 $[\min_t x_t,\max_t x_t]$ y 轴范围，让不同窗口的幅度可以直接比较。（§3.1, pp.3–4）

对每张图使用 OpenCLIP 的 CLIP ViT-B/16 视觉编码器提取 patch-level penultimate feature map $F\in\mathbb{R}^{P\times P\times D}$。论文采用公开 LAION-400M 预训练视觉模型，不在目标 TSAD 数据集训练视觉 encoder。窗口不重叠地抽取会降低计算，但论文默认用四分之一窗长步长以留出重叠定位。（§3.1; Appendix C）

### 6.2 ViT4TS：跨窗口、多尺度 patch 匹配

短尖峰通常只占少数 patch，趋势改变、持续跳变等则跨越多个 patch。ViT4TS 因而在基础 patch map 上使用 $k\times k$、stride 1 的平均池化构造尺度集合（主设置含 $k=1,2,3$）。池化特征保留细节与邻域上下文的不同折衷。（§3.1, Eq. 1, pp.3–4）

在每个尺度 $k$，将窗口 $i$ 的 patch map flatten 为 $L_i^{(k)}$。窗口 $i$ 中 patch $p$ 对其他窗口 $j\ne i$ 的最接近 patch 做 cosine similarity 搜索，得到跨窗距离：

$$U_{i,j}^{(k)}[p]=\min_r\{1-\cos(L_i^{(k)}[p],L_j^{(k)}[r])\}.$$

再对所有其他窗口的距离取 median，形成参考差异图：

$$S_i^{(k)}[p]=\operatorname{median}_{j\ne i}U_{i,j}^{(k)}[p].$$

直觉是：在其他时间窗中可以找到相似视觉模式的 patch 倾向于正常；若当前局部结构很难在同一序列的其他窗口找到近邻，则偏离较大。median 对少数异常参考窗比均值稳健。作者还比较由全部 patch 共同形成参考的 memory-intensive 变体；按 patch 取 median 是主方法，便于内存扩展。（§3.1; Appendix C.2）

多个尺度的差异图上采样到统一位置后用 harmonic fusion 合并，减轻一个尺度被异常值主导的影响；每个时间位置对应一列视觉 patch，论文再以 patch-row 方向的 $q=0.25$ quantile 汇聚成 timestamp score。随后对连续 timestamp 分数平滑并使用 Gaussian threshold $\mu+z_\alpha\sigma$ 形成候选片段；阈值按 $z_\alpha\in\{0.1,0.01,0.001\}$ 等候选值评估，合并相邻正区间。（§3.1; Appendix B.3, C.3）

### 6.3 VLM4TS：以全局时间上下文核验

阶段二把整条序列另绘为含坐标轴刻度的全局图，并将 ViT4TS 的候选开始 / 结束位置一并提供给 GPT-4o（论文报告 API 模型版本 2024-08-06）。提示要求模型：检查每个候选是否与全局趋势、周期和其它时间范围一致；拒绝只是正常 fluctuation 的候选；找出视觉或统计上显著但第一阶段遗漏的异常；为每段给出 1–3 置信度、简短理由，并按 JSON 输出 interval。（§3.2, pp.4–5; Appendix B.4）

置信度为 1 的区间会被舍弃，2 或 3 的区间保留。VLM 的角色因此不是给每个时间点打分，而是对候选区间做高层筛选、边界修订和漏检补充。全序列视图为其提供跨窗上下文，但这些上下文是单变量曲线，不包含负载、部署、业务事件或 trace 元数据。（§3.2）

### 6.4 评估协议与指标

原始序列先 min-max 到 $[0,1]$ 并移除 least-squares linear trend；Yahoo A4 另在已知 change point 前后分别标准化。对连续分数再按 exponential moving average 平滑，以 Gaussian quantile threshold $\tau_\alpha=\mu+z_\alpha\sigma$ 扫描 $z_\alpha$，其中 $\alpha\in\{0.10,0.01,0.001\}$，报告 unweighted contextual F1 与其最大值 F1-max；binary-label 方法按默认输出评价。A4 的分段标准化和 F1-max 都是比较协议的一部分，不能直接解读成固定误报预算下的运行表现。（§4, p.5; Appendix C.5）

## 7. Experimental Design and Evidence

### 7.1 Datasets / baselines

实验使用 11 个 benchmark：MSL、SMAP；Yahoo A1–A4；NAB Art、AWS、AdEx、Traf、Tweets。包含航天器传感器、web / production traffic、Twitter mentions 等；评测重点是 univariate。基线覆盖 ARIMA、LSTM-DT、LSTM-AE、VAE、TadGAN、AER、Anomaly Transformer、UniTS、TimesFM / TimesFM2、SigLLM、TAMA 等。（§4; Appendix C.1）

### 7.2 主结果与成本

Table 1 的平均 F1-max：ViT4TS 为 $0.612\pm0.116$，VLM4TS 为 $0.659\pm0.127$，第二名 LSTM-DT 为 $0.529\pm0.200$；VLM4TS 在 11 项中 9 项领先。Table 2 中 VLM4TS 的宏平均 F1-max 约 0.665，较 TAMA 提高 13.3%；单序列平均约 1,212 tokens、14.68 秒。作者将成本优势表述为较朴素 rolling-window VLM prompting 平均 36× 更省 token；主文另有“相比最佳 baseline 24.6%”的描述，二者比较对象不同。（Tables 1–2, pp.6–7; Appendix D.1）

较大的真实 contextual anomaly 增益主要见 NAB；Yahoo A3/A4 的高密度人工注入异常中，VLM4TS 结果低于单纯 ViT4TS / 一些 forecasting baseline，例如 A3：0.497 对 0.614，A4：0.474 对 0.565。作者将其归因于稀有异常假设导致 VLM 更保守，呈现为 precision 上升但 recall 下降。（§4, p.6; Appendix D.4）

### 7.3 消融与敏感性

- 去掉 ViT4TS 只让 VLM 看全局图，平均性能明显降低；Yahoo 组尤其明显（Table 3, p.7）。这支持粗粒度视觉推理需要一个高分辨率局部 proposal stage。
- patch-level 特征、cross-patch matching、multi-scale 特征均有正贡献；移除 patch-level 信息在部分 Yahoo 集上造成大幅下降。（Table 3; Appendix D.2）
- 将 rolling window 从默认 224 调小到 28 后，短而密集的 Yahoo A3 F1-max 从 0.614 提高到 0.906，A4 从 0.565 提高到 0.844；代价是更多 windows / 计算与上下文碎片化风险。（Appendix D.4, Fig. 8）
- 换视觉 backbone、pooling、patch aggregation 等有实验，但总体表现随数据组而异，不能认为自然图像 CLIP 对所有 TSAD 都更优。（Appendix D.2–D.5）

### 7.4 多变量补充结果

主方法集中于单变量。附录给出 MSL 多变量绘图扩展：每个通道独立 screening，再以 subplot 和候选文字交给 VLM；该有限实验的最大 F1 从逐通道约 0.619 上升到多变量融合约 0.660。它支持多通道图可能补充证据，但不构成多变量关系 / 因果建模的系统评价。（Appendix D.3）

## 8. Technical Contribution and Limitations

### 技术贡献

1. 把预训练视觉 patch 表征用于同一序列的跨窗正常参照，定位局部候选，而不训练目标域的时序模型。（§3.1）
2. 以多尺度视觉匹配平衡窄尖峰与较长模式变化的识别。（§3.1）
3. 用一个全局 VLM call 融合 candidate intervals 与整序列走势，降低逐窗问答的 token 成本，并尝试提高区间精度。（§3.2, Table 2）

### 局限与证据边界

- **作者明确范围**：方法主要为单变量设计；多变量只是附录扩展。对于异常不稀有的 A3/A4，作者观察到 detector 会把成簇异常当成 pattern fluctuation。（§3, §4）
- **评测范围**：11 个基准、contextual F1-max 扫阈值。没有固定业务 false-positive rate、在线延迟预算、真实告警负担或跨服务迁移实验。（§4；分析边界）
- **预训练域差异**：CLIP 面向自然图像；线图纹理能否承载所有量纲、单位、窗口采样含义并未一般性验证。作者用 ablation 证明特定基准有效，不等于已解释语义。（分析推断）
- **y 轴范围依赖全序列极值**：每个局部图用 full-series min/max；极端值可能压扁其它波动，这是由绘图方案推得、论文未专门测试的潜在敏感性。（§3.1；分析推断）
- **上下文的边界**：VLM 看到的是曲线全局形状，不是 workload、release、业务活动、Trace 或根因信息；因此不能把其“上下文核验”直接等同于业务状态识别或故障来源解释。（分析推断）
- **阈值和置信过滤**：F1-max 是 oracle threshold protocol；confidence 1–3 由提示模型自行产出，未见独立校准为概率的证据。（§4, Appendix B；分析推断）
- **运行成本**：约 14.68 秒 / 序列的 GPT-4o 路径更适合离线或 human-in-the-loop，未被证明适合高频实时告警。（Appendix D.1）

## 9. Reproduction and Reuse Value

论文提供 [VLM4TS code](https://github.com/ZLHe0/VLM4TS)。若复用，需关注 CLIP backbone / patch grid 与输入边长是否一致；阈值参数、跨窗候选区间生成、相邻区间合并、完整 VLM prompt 和 API version 都会影响结果。代码与公开数据能支持复现论文 benchmark，但 GPT-4o API、模型版本和成本会随服务更新而变化。论文的两阶段结构适合作为候选生成 + 全局语境核验的 baseline；需要在部署环境另行测定 latency、token budget、误报率和 dense-anomaly behavior。本次只阅读 PDF，没有运行代码或复现实验。

## 10. Related Work

- **Delving into LLMs for TSAD**：两者都先修复输入 / 定位瓶颈再调用大模型；Delving 用数值序列文本与显式 index，VLM4TS 用图像 patch proposal 与全局视觉核验。
- **AnomSeer**：也以时间序列图像交给多模态模型；AnomSeer 训练 MLLM 产生类别 / 区间 / explanation，VLM4TS 主要保持 zero-shot 并将模型限制在候选复核。
- **TimeRCD**：以合成监督学会上下文相对异常，但以数值 Transformer 建模；可对照视觉上下文与序列内 relational context。
- **TFC / TFMAE / MACE**：频域与多视图方法给出数值特征路线，可比较其与视觉 plot features 的异常分辨能力。
- **When Model Meets New Normals / CAPMix**：关注新正常状态和业务噪声；VLM4TS 的全局曲线参考并未显式建模合法状态语义。
