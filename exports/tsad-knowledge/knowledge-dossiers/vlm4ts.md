# Knowledge Dossier — Harnessing Vision-Language Models for Time Series Anomaly Detection

## 1. Basic Information

- **English title**: Harnessing Vision-Language Models for Time Series Anomaly Detection
- **中文译名**：利用视觉语言模型进行时间序列异常检测
- **Authors**: Zelin He, Sarah Alnegheimish, Matthew Reimherr
- **Venue / year / CCF**: AAAI 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/ZLHe0/VLM4TS
- **Research area**: 视觉语言模型的零样本候选筛查与验证
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 在不使用目标时序训练的条件下，对单变量序列输出异常 interval；两阶段视觉方法先找局部候选，再以 VLM 结合整个序列核验。（§3, pp.3–5）
- **[实验支持]** 在 MSL、SMAP、Yahoo A1–A4、NAB 五组共 11 个 benchmark 上评价；主线是 univariate。（§4; Appendix C）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文针对 univariate time series interval detection：给定 $x_{1:T}$，输出未知数量的异常时间区间 $A=\{(t_s,t_e)_i\}$。作者强调，一个高值是否异常不能只看幅度：若它在该序列历史中反复出现可能是正常波动；缓慢 drift 也可能偏离已建立趋势而异常。传统数值 detector 依赖特定数据训练或归纳偏置，直接将 VLM 用于时序又会面临输入分辨率、时间上下文和 token 成本之间的冲突。（§1、§3, pp.1, 3）

核心设计目标是把局部细节检测与整个序列的上下文解释分开：第一阶段高召回筛候选，第二阶段跨模态模型用全局趋势校验候选并补漏。（§3, Fig. 3）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **时间跨度与视觉分辨率冲突**：一张图很难同时显示长序列全局规律和尖峰的精确位置；滚动小窗又缺少长程背景。（§3, pp.3–4）
2. **视觉预训练和时序图的域差异**：CLIP 的图像预训练并非时序专用，如何在 patch 级别利用其视觉特征检测线图异常并不显然。（§3.1）
3. **异常位置的候选筛选**：没有目标域训练标签时，需要从大量正常窗口形成参照，利用异常相对稀少的假设发现局部偏离。（§3.1）
4. **VLM 推理费用**：对每个局部窗口逐一询问多模态模型会造成高 token 消耗，也会让每个判断看不到整个序列。（§1, §3.2）
5. **异常密集时稀有性假设失效**：作者观察到 Yahoo A3/A4 的密集合成异常容易被模型解释成较大模式中的 fluctuation。（§4, p.6；Appendix D）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 传统数值 detector 常依赖目标域训练与特定假设；naive VLM prompting 的准确率及 token 成本不理想。（§1–2）
- **[分析推断]** 全局趋势语境只来自曲线图，不含业务状态、发布、负载或 Trace；不能当作业务语义理解的实证。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

VLM4TS 将无轴、统一尺度的滑窗折线图交给预训练 CLIP 进行多尺度跨窗口 patch 匹配，先产生局部 anomaly candidate，再把全序列图和候选区间交给 GPT-4o 按全局趋势核验，从而在不进行时序域训练的条件下结合局部定位与长程视觉语境。（§§3–4, Fig. 3, pp.3–6）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：时间跨度与视觉分辨率冲突：一张图很难同时显示长序列全局规律和尖峰的精确位置；滚动小窗又缺少长程背景。（§3, pp.3–4）
- **C2（第4节挑战）**：视觉预训练和时序图的域差异：CLIP 的图像预训练并非时序专用，如何在 patch 级别利用其视觉特征检测线图异常并不显然。（§3.1）
- **C3（第4节挑战）**：异常位置的候选筛选：没有目标域训练标签时，需要从大量正常窗口形成参照，利用异常相对稀少的假设发现局部偏离。（§3.1）
- **C4（第4节挑战）**：VLM 推理费用：对每个局部窗口逐一询问多模态模型会造成高 token 消耗，也会让每个判断看不到整个序列。（§1, §3.2）
- **C5（第4节挑战）**：异常密集时稀有性假设失效：作者观察到 Yahoo A3/A4 的密集合成异常容易被模型解释成较大模式中的 fluctuation。（§4, p.6；Appendix D）

### 7.1 ViT4TS

- **作者技术描述**：**[作者主张] ViT4TS**：224 点滑窗、56 步长、统一全序列 y 轴；CLIP ViT-B/16 patch map 经 1×1、2×2、3×3 pooling 后，与同序列其它窗口做最近 cosine patch 匹配，跨窗 median 聚合。（§3.1, pp.3–4）
- **对应挑战**：C4、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 ViT4TS：跨窗口、多尺度 patch 匹配”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 多尺度 score fusion

- **作者技术描述**：**[作者主张] 多尺度 score fusion**：上采样后 harmonic 融合不同尺度差异图，以 patch-row quantile 汇聚到时间分数，并阈值化为候选 interval。（§3.1; Appendix B.3）
- **对应挑战**：C5（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 ViT4TS：跨窗口、多尺度 patch 匹配”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 VLM4TS

- **作者技术描述**：**[作者主张] VLM4TS**：把整序列图、ViT 候选区间交给 GPT-4o，要求拒绝与全局走势不符候选、补充明显遗漏，并输出 JSON、confidence 和简短理由；过滤 confidence 1。（§3.2; Appendix B.4）
- **对应挑战**：C5、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 VLM4TS：以全局时间上下文核验”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：6.1 输入图像与滑窗；6.2 ViT4TS：跨窗口、多尺度 patch 匹配。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 输入图像与滑窗

阶段一主要使用单变量输入。以长度 $L_w$ 的窗口沿序列滚动，步长 $L_s=\lfloor L_w/4\rfloor$；默认输入边长为 224、步长 56。每窗绘制成正方形干净折线图，隐藏轴刻度、图例等非信息元素；所有局部图共用从整条序列得到的 $[\min_t x_t,\max_t x_t]$ y 轴范围，让不同窗口的幅度可以直接比较。（§3.1, pp.3–4）

对每张图使用 OpenCLIP 的 CLIP ViT-B/16 视觉编码器提取 patch-level penultimate feature map $F\in\mathbb{R}^{P\times P\times D}$。论文采用公开 LAION-400M 预训练视觉模型，不在目标 TSAD 数据集训练视觉 encoder。窗口不重叠地抽取会降低计算，但论文默认用四分之一窗长步长以留出重叠定位。（§3.1; Appendix C）

#### 6.2 ViT4TS：跨窗口、多尺度 patch 匹配

短尖峰通常只占少数 patch，趋势改变、持续跳变等则跨越多个 patch。ViT4TS 因而在基础 patch map 上使用 $k\times k$、stride 1 的平均池化构造尺度集合（主设置含 $k=1,2,3$）。池化特征保留细节与邻域上下文的不同折衷。（§3.1, Eq. 1, pp.3–4）

在每个尺度 $k$，将窗口 $i$ 的 patch map flatten 为 $L_i^{(k)}$。窗口 $i$ 中 patch $p$ 对其他窗口 $j\ne i$ 的最接近 patch 做 cosine similarity 搜索，得到跨窗距离：

$$U_{i,j}^{(k)}[p]=\min_r\{1-\cos(L_i^{(k)}[p],L_j^{(k)}[r])\}.$$

再对所有其他窗口的距离取 median，形成参考差异图：

$$S_i^{(k)}[p]=\operatorname{median}_{j\ne i}U_{i,j}^{(k)}[p].$$

直觉是：在其他时间窗中可以找到相似视觉模式的 patch 倾向于正常；若当前局部结构很难在同一序列的其他窗口找到近邻，则偏离较大。median 对少数异常参考窗比均值稳健。作者还比较由全部 patch 共同形成参考的 memory-intensive 变体；按 patch 取 median 是主方法，便于内存扩展。（§3.1; Appendix C.2）

多个尺度的差异图上采样到统一位置后用 harmonic fusion 合并，减轻一个尺度被异常值主导的影响；每个时间位置对应一列视觉 patch，论文再以 patch-row 方向的 $q=0.25$ quantile 汇聚成 timestamp score。随后对连续 timestamp 分数平滑并使用 Gaussian threshold $\mu+z_\alpha\sigma$ 形成候选片段；阈值按 $z_\alpha\in\{0.1,0.01,0.001\}$ 等候选值评估，合并相邻正区间。（§3.1; Appendix B.3, C.3）

#### 6.3 VLM4TS：以全局时间上下文核验

阶段二把整条序列另绘为含坐标轴刻度的全局图，并将 ViT4TS 的候选开始 / 结束位置一并提供给 GPT-4o（论文报告 API 模型版本 2024-08-06）。提示要求模型：检查每个候选是否与全局趋势、周期和其它时间范围一致；拒绝只是正常 fluctuation 的候选；找出视觉或统计上显著但第一阶段遗漏的异常；为每段给出 1–3 置信度、简短理由，并按 JSON 输出 interval。（§3.2, pp.4–5; Appendix B.4）

置信度为 1 的区间会被舍弃，2 或 3 的区间保留。VLM 的角色因此不是给每个时间点打分，而是对候选区间做高层筛选、边界修订和漏检补充。全序列视图为其提供跨窗上下文，但这些上下文是单变量曲线，不包含负载、部署、业务事件或 trace 元数据。（§3.2）

#### 6.4 评估协议与指标

原始序列先 min-max 到 $[0,1]$ 并移除 least-squares linear trend；Yahoo A4 另在已知 change point 前后分别标准化。对连续分数再按 exponential moving average 平滑，以 Gaussian quantile threshold $\tau_\alpha=\mu+z_\alpha\sigma$ 扫描 $z_\alpha$，其中 $\alpha\in\{0.10,0.01,0.001\}$，报告 unweighted contextual F1 与其最大值 F1-max；binary-label 方法按默认输出评价。A4 的分段标准化和 F1-max 都是比较协议的一部分，不能直接解读成固定误报预算下的运行表现。（§4, p.5; Appendix C.5）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

VLM4TS 将无轴、统一尺度的滑窗折线图交给预训练 CLIP 进行多尺度跨窗口 patch 匹配，先产生局部 anomaly candidate，再把全序列图和候选区间交给 GPT-4o 按全局趋势核验，从而在不进行时序域训练的条件下结合局部定位与长程视觉语境。（§§3–4, Fig. 3, pp.3–6）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Datasets / baselines

实验使用 11 个 benchmark：MSL、SMAP；Yahoo A1–A4；NAB Art、AWS、AdEx、Traf、Tweets。包含航天器传感器、web / production traffic、Twitter mentions 等；评测重点是 univariate。基线覆盖 ARIMA、LSTM-DT、LSTM-AE、VAE、TadGAN、AER、Anomaly Transformer、UniTS、TimesFM / TimesFM2、SigLLM、TAMA 等。（§4; Appendix C.1）

#### 7.2 主结果与成本

Table 1 的平均 F1-max：ViT4TS 为 $0.612\pm0.116$，VLM4TS 为 $0.659\pm0.127$，第二名 LSTM-DT 为 $0.529\pm0.200$；VLM4TS 在 11 项中 9 项领先。Table 2 中 VLM4TS 的宏平均 F1-max 约 0.665，较 TAMA 提高 13.3%；单序列平均约 1,212 tokens、14.68 秒。作者将成本优势表述为较朴素 rolling-window VLM prompting 平均 36× 更省 token；主文另有“相比最佳 baseline 24.6%”的描述，二者比较对象不同。（Tables 1–2, pp.6–7; Appendix D.1）

较大的真实 contextual anomaly 增益主要见 NAB；Yahoo A3/A4 的高密度人工注入异常中，VLM4TS 结果低于单纯 ViT4TS / 一些 forecasting baseline，例如 A3：0.497 对 0.614，A4：0.474 对 0.565。作者将其归因于稀有异常假设导致 VLM 更保守，呈现为 precision 上升但 recall 下降。（§4, p.6; Appendix D.4）

#### 7.3 消融与敏感性

- 去掉 ViT4TS 只让 VLM 看全局图，平均性能明显降低；Yahoo 组尤其明显（Table 3, p.7）。这支持粗粒度视觉推理需要一个高分辨率局部 proposal stage。
- patch-level 特征、cross-patch matching、multi-scale 特征均有正贡献；移除 patch-level 信息在部分 Yahoo 集上造成大幅下降。（Table 3; Appendix D.2）
- 将 rolling window 从默认 224 调小到 28 后，短而密集的 Yahoo A3 F1-max 从 0.614 提高到 0.906，A4 从 0.565 提高到 0.844；代价是更多 windows / 计算与上下文碎片化风险。（Appendix D.4, Fig. 8）
- 换视觉 backbone、pooling、patch aggregation 等有实验，但总体表现随数据组而异，不能认为自然图像 CLIP 对所有 TSAD 都更优。（Appendix D.2–D.5）

#### 7.4 多变量补充结果

主方法集中于单变量。附录给出 MSL 多变量绘图扩展：每个通道独立 screening，再以 subplot 和候选文字交给 VLM；该有限实验的最大 F1 从逐通道约 0.619 上升到多变量融合约 0.660。它支持多通道图可能补充证据，但不构成多变量关系 / 因果建模的系统评价。（Appendix D.3）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**预训练域差异**：CLIP 面向自然图像；线图纹理能否承载所有量纲、单位、窗口采样含义并未一般性验证。作者用 ablation 证明特定基准有效，不等于已解释语义。（分析推断）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**y 轴范围依赖全序列极值**：每个局部图用 full-series min/max；极端值可能压扁其它波动，这是由绘图方案推得、论文未专门测试的潜在敏感性。（§3.1；分析推断）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**上下文的边界**：VLM 看到的是曲线全局形状，不是 workload、release、业务活动、Trace 或根因信息；因此不能把其“上下文核验”直接等同于业务状态识别或故障来源解释。（分析推断）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**阈值和置信过滤**：F1-max 是 oracle threshold protocol；confidence 1–3 由提示模型自行产出，未见独立校准为概率的证据。（§4, Appendix B；分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**作者明确范围**：方法主要为单变量设计；多变量只是附录扩展。对于异常不稀有的 A3/A4，作者观察到 detector 会把成簇异常当成 pattern fluctuation。（§3, §4）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**评测范围**：11 个基准、contextual F1-max 扫阈值。没有固定业务 false-positive rate、在线延迟预算、真实告警负担或跨服务迁移实验。（§4；分析边界）

#### 精读笔记原章节：8. Technical Contribution and Limitations — 局限与证据边界

**运行成本**：约 14.68 秒 / 序列的 GPT-4o 路径更适合离线或 human-in-the-loop，未被证明适合高频实时告警。（Appendix D.1）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 评估多变量 joint context、动态 scale / y-range 对极值与高波动状态的鲁棒性。
- **[分析推断]** 在合法业务状态切换、故障、以及二者同时出现的测试矩阵中测量 context verification 对未知故障的漏报代价。
- **[分析推断]** 固定误报预算下报告区间质量、检测延迟、VLM latency 和 token cost，并校准置信度。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **Delving into LLMs for TSAD**：两者都先修复输入 / 定位瓶颈再调用大模型；Delving 用数值序列文本与显式 index，VLM4TS 用图像 patch proposal 与全局视觉核验。
- **AnomSeer**：也以时间序列图像交给多模态模型；AnomSeer 训练 MLLM 产生类别 / 区间 / explanation，VLM4TS 主要保持 zero-shot 并将模型限制在候选复核。
- **TimeRCD**：以合成监督学会上下文相对异常，但以数值 Transformer 建模；可对照视觉上下文与序列内 relational context。
- **TFC / TFMAE / MACE**：频域与多视图方法给出数值特征路线，可比较其与视觉 plot features 的异常分辨能力。
- **When Model Meets New Normals / CAPMix**：关注新正常状态和业务噪声；VLM4TS 的全局曲线参考并未显式建模合法状态语义。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §1, §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3, Fig. 3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §1, §3.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §§3.1–3.2, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3.1 | 精读笔记保留的原文定位 |
| Method / formulas | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3.1, Eq. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3.2 | 精读笔记保留的原文定位 |
| Method / formulas | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Experimental evidence | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Experimental evidence | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | Table 1, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | Fig. 8 | 精读笔记保留的原文定位 |
| Limitations | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3, §4 | 精读笔记保留的原文定位 |
| Limitations | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §4 | 精读笔记保留的原文定位 |
| Limitations | Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf | §3.1 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "vlm4ts",
  "title_en": "Harnessing Vision-Language Models for Time Series Anomaly Detection",
  "title_zh": "利用视觉语言模型进行时间序列异常检测",
  "authors": [
    "Zelin He",
    "Sarah Alnegheimish",
    "Matthew Reimherr"
  ],
  "year": 2026,
  "venue": "AAAI",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/AAAI/Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/vlm4ts/notes.md",
  "code_url": "https://github.com/ZLHe0/VLM4TS",
  "research_area": "视觉语言模型的零样本候选筛查与验证",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] 在不使用目标时序训练的条件下，对单变量序列输出异常 interval；两阶段视觉方法先找局部候选，再以 VLM 结合整个序列核验。（§3, pp.3–5） - [实验支持] 在 MSL、SMAP、Yahoo A1–A4、NAB 五组共 11 个 benchmark 上评价；主线是 univariate。（§4; Appendix C）",
  "research_problem": "论文针对 univariate time series interval detection：给定 $x{1:T}$，输出未知数量的异常时间区间 $A=\\{(ts,te)i\\}$。作者强调，一个高值是否异常不能只看幅度：若它在该序列历史中反复出现可能是正常波动；缓慢 drift 也可能偏离已建立趋势而异常。传统数值 detector 依赖特定数据训练或归纳偏置，直接将 VLM 用于时序又会面临输入分辨率、时间上下文和 token 成本之间的冲突。（§1、§3, pp.1, 3） 核心设计目标是把局部细节检测与整个序列的上下文解释分开：第一阶段高召回筛候选，第二阶段跨模态模型用全局趋势校验候选并补漏。（§3, Fig. 3）",
  "core_challenges": [
    "时间跨度与视觉分辨率冲突：一张图很难同时显示长序列全局规律和尖峰的精确位置；滚动小窗又缺少长程背景。（§3, pp.3–4）",
    "视觉预训练和时序图的域差异：CLIP 的图像预训练并非时序专用，如何在 patch 级别利用其视觉特征检测线图异常并不显然。（§3.1）",
    "异常位置的候选筛选：没有目标域训练标签时，需要从大量正常窗口形成参照，利用异常相对稀少的假设发现局部偏离。（§3.1）",
    "VLM 推理费用：对每个局部窗口逐一询问多模态模型会造成高 token 消耗，也会让每个判断看不到整个序列。（§1, §3.2）",
    "异常密集时稀有性假设失效：作者观察到 Yahoo A3/A4 的密集合成异常容易被模型解释成较大模式中的 fluctuation。（§4, p.6；Appendix D）"
  ],
  "existing_method_limits": [
    "[作者主张] 传统数值 detector 常依赖目标域训练与特定假设；naive VLM prompting 的准确率及 token 成本不理想。（§1–2）",
    "[分析推断] 全局趋势语境只来自曲线图，不含业务状态、发布、负载或 Trace；不能当作业务语义理解的实证。"
  ],
  "core_idea": "VLM4TS 将无轴、统一尺度的滑窗折线图交给预训练 CLIP 进行多尺度跨窗口 patch 匹配，先产生局部 anomaly candidate，再把全序列图和候选区间交给 GPT-4o 按全局趋势核验，从而在不进行时序域训练的条件下结合局部定位与长程视觉语境。（§§3–4, Fig. 3, pp.3–6）",
  "technical_innovations": [
    {
      "name": "ViT4TS",
      "author_claim": "**[作者主张] ViT4TS**：224 点滑窗、56 步长、统一全序列 y 轴；CLIP ViT-B/16 patch map 经 1×1、2×2、3×3 pooling 后，与同序列其它窗口做最近 cosine patch 匹配，跨窗 median 聚合。（§3.1, pp.3–4）",
      "challenge_ids": [
        "C4",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 ViT4TS：跨窗口、多尺度 patch 匹配",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] ViT4TS**：224 点滑窗、56 步长、统一全序列 y 轴；CLIP ViT-B/16 patch map 经 1×1、2×2、3×3 pooling 后，与同序列其它窗口做最近 cosine patch 匹配，跨窗 median 聚合。（§3.1, pp.3–4）"
    },
    {
      "name": "多尺度 score fusion",
      "author_claim": "**[作者主张] 多尺度 score fusion**：上采样后 harmonic 融合不同尺度差异图，以 patch-row quantile 汇聚到时间分数，并阈值化为候选 interval。（§3.1; Appendix B.3）",
      "challenge_ids": [
        "C5"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 ViT4TS：跨窗口、多尺度 patch 匹配",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 多尺度 score fusion**：上采样后 harmonic 融合不同尺度差异图，以 patch-row quantile 汇聚到时间分数，并阈值化为候选 interval。（§3.1; Appendix B.3）"
    },
    {
      "name": "VLM4TS",
      "author_claim": "**[作者主张] VLM4TS**：把整序列图、ViT 候选区间交给 GPT-4o，要求拒绝与全局走势不符候选、补充明显遗漏，并输出 JSON、confidence 和简短理由；过滤 confidence 1。（§3.2; Appendix B.4）",
      "challenge_ids": [
        "C5",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 VLM4TS：以全局时间上下文核验",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] VLM4TS**：把整序列图、ViT 候选区间交给 GPT-4o，要求拒绝与全局走势不符候选、补充明显遗漏，并输出 JSON、confidence 和简短理由；过滤 confidence 1。（§3.2; Appendix B.4）"
    }
  ],
  "methodology": {
    "architecture": "text univariate series x[1:T] ├─ Stage 1 / ViT4TS │ rolling windows (Lw=224, stride=56) │ → clean line plots (shared full-series y limits) │ → CLIP ViT-B/16 patch features │ → 1×1 / 2×2 / 3×3 multi-scale pooling │ → cross-window nearest-patch dissimilarity + median reference │ → harmonic scale fusion → timestamp score map │ → Gaussian score thresholds → candidate intervals └─ Stage 2 / VLM4TS full-series plot with axes + candidate intervals → GPT-4o integrates full-series trend and candidate evidence → JSON intervals / confidence / rationale → discard confidence-1 proposals （§§3.1–3.2, Fig. 3, pp.3–5; Appendix B, pp.10–12）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 输入图像与滑窗",
      "6.2 ViT4TS：跨窗口、多尺度 patch 匹配",
      "6.3 VLM4TS：以全局时间上下文核验",
      "6.4 评估协议与指标"
    ],
    "key_formulas": [
      "Eq. (1)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "VLM4TS 将无轴、统一尺度的滑窗折线图交给预训练 CLIP 进行多尺度跨窗口 patch 匹配，先产生局部 anomaly candidate，再把全序列图和候选区间交给 GPT-4o 按全局趋势核验，从而在不进行时序域训练的条件下结合局部定位与长程视觉语境。（§§3–4, Fig. 3, pp.3–6）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets / baselines",
      "实验使用 11 个 benchmark：MSL、SMAP；Yahoo A1–A4；NAB Art、AWS、AdEx、Traf、Tweets。包含航天器传感器、web / production traffic、Twitter mentions 等；评测重点是 univariate。基线覆盖 ARIMA、LSTM-DT、LSTM-AE、VAE、TadGAN、AER、Anomaly Transformer、UniTS、TimesFM / TimesFM2、SigLLM、TAMA 等。（§4; Appendix C.1）"
    ],
    "baselines": [
      "### 7.1 Datasets / baselines",
      "Table 1 的平均 F1-max：ViT4TS 为 $0.612\\pm0.116$，VLM4TS 为 $0.659\\pm0.127$，第二名 LSTM-DT 为 $0.529\\pm0.200$；VLM4TS 在 11 项中 9 项领先。Table 2 中 VLM4TS 的宏平均 F1-max 约 0.665，较 TAMA 提高 13.3%；单序列平均约 1,212 tokens、14.68 秒。作者将成本优势表述为较朴素 rolling-window VLM prompting 平均 36× 更省 token；主文另有“相比最佳 baseline 24.6%”的描述，二者比较对象不同。（Tables 1–2, pp.6–7;…",
      "较大的真实 contextual anomaly 增益主要见 NAB；Yahoo A3/A4 的高密度人工注入异常中，VLM4TS 结果低于单纯 ViT4TS / 一些 forecasting baseline，例如 A3：0.497 对 0.614，A4：0.474 对 0.565。作者将其归因于稀有异常假设导致 VLM 更保守，呈现为 precision 上升但 recall 下降。（§4, p.6; Appendix D.4）"
    ],
    "metrics": [
      "Table 1 的平均 F1-max：ViT4TS 为 $0.612\\pm0.116$，VLM4TS 为 $0.659\\pm0.127$，第二名 LSTM-DT 为 $0.529\\pm0.200$；VLM4TS 在 11 项中 9 项领先。Table 2 中 VLM4TS 的宏平均 F1-max 约 0.665，较 TAMA 提高 13.3%；单序列平均约 1,212 tokens、14.68 秒。作者将成本优势表述为较朴素 rolling-window VLM prompting 平均 36× 更省 token；主文另有“相比最佳 baseline 24.6%”的描述，二者比较对象不同。（Tables 1–2, pp.6–7;…",
      "较大的真实 contextual anomaly 增益主要见 NAB；Yahoo A3/A4 的高密度人工注入异常中，VLM4TS 结果低于单纯 ViT4TS / 一些 forecasting baseline，例如 A3：0.497 对 0.614，A4：0.474 对 0.565。作者将其归因于稀有异常假设导致 VLM 更保守，呈现为 precision 上升但 recall 下降。（§4, p.6; Appendix D.4）",
      "- 去掉 ViT4TS 只让 VLM 看全局图，平均性能明显降低；Yahoo 组尤其明显（Table 3, p.7）。这支持粗粒度视觉推理需要一个高分辨率局部 proposal stage。 - patch-level 特征、cross-patch matching、multi-scale 特征均有正贡献；移除 patch-level 信息在部分 Yahoo 集上造成大幅下降。（Table 3; Appendix D.2） - 将 rolling window 从默认 224 调小到 28 后，短而密集的 Yahoo A3 F1-max 从 0.614 提高到 0.906，A4 从 0.565 提高到 0.844；…",
      "主方法集中于单变量。附录给出 MSL 多变量绘图扩展：每个通道独立 screening，再以 subplot 和候选文字交给 VLM；该有限实验的最大 F1 从逐通道约 0.619 上升到多变量融合约 0.660。它支持多通道图可能补充证据，但不构成多变量关系 / 因果建模的系统评价。（Appendix D.3）"
    ],
    "main_results": [
      "### 7.2 主结果与成本",
      "Table 1 的平均 F1-max：ViT4TS 为 $0.612\\pm0.116$，VLM4TS 为 $0.659\\pm0.127$，第二名 LSTM-DT 为 $0.529\\pm0.200$；VLM4TS 在 11 项中 9 项领先。Table 2 中 VLM4TS 的宏平均 F1-max 约 0.665，较 TAMA 提高 13.3%；单序列平均约 1,212 tokens、14.68 秒。作者将成本优势表述为较朴素 rolling-window VLM prompting 平均 36× 更省 token；主文另有“相比最佳 baseline 24.6%”的描述，二者比较对象不同。（Tables 1–2, pp.6–7; Appendix D.1）",
      "- 去掉 ViT4TS 只让 VLM 看全局图，平均性能明显降低；Yahoo 组尤其明显（Table 3, p.7）。这支持粗粒度视觉推理需要一个高分辨率局部 proposal stage。 - patch-level 特征、cross-patch matching、multi-scale 特征均有正贡献；移除 patch-level 信息在部分 Yahoo 集上造成大幅下降。（Table 3; Appendix D.2） - 将 rolling window 从默认 224 调小到 28 后，短而密集的 Yahoo A3 F1-max 从 0.614 提高到 0.906，A4 从 0.565 提高到 0.844；代价是更多 windows / 计算与上下文碎片化风险。…"
    ],
    "ablations": [
      "### 7.3 消融与敏感性",
      "- 去掉 ViT4TS 只让 VLM 看全局图，平均性能明显降低；Yahoo 组尤其明显（Table 3, p.7）。这支持粗粒度视觉推理需要一个高分辨率局部 proposal stage。 - patch-level 特征、cross-patch matching、multi-scale 特征均有正贡献；移除 patch-level 信息在部分 Yahoo 集上造成大幅下降。（Table 3; Appendix D.2） - 将 rolling window 从默认 224 调小到 28 后，短而密集的 Yahoo A3 F1-max 从 0.614 提高到 0.906，A4 从 0.565 提高到 0.844；…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "实验使用 11 个 benchmark：MSL、SMAP；Yahoo A1–A4；NAB Art、AWS、AdEx、Traf、Tweets。包含航天器传感器、web / production traffic、Twitter mentions 等；评测重点是 univariate。基线覆盖 ARIMA、LSTM-DT、LSTM-AE、VAE、TadGAN、AER、Anomaly Transformer、UniTS、TimesFM / TimesFM2、SigLLM、TAMA 等。（§4; Appendix C.1）"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "预训练域差异：CLIP 面向自然图像；线图纹理能否承载所有量纲、单位、窗口采样含义并未一般性验证。作者用 ablation 证明特定基准有效，不等于已解释语义。（分析推断）",
      "y 轴范围依赖全序列极值：每个局部图用 full-series min/max；极端值可能压扁其它波动，这是由绘图方案推得、论文未专门测试的潜在敏感性。（§3.1；分析推断）",
      "上下文的边界：VLM 看到的是曲线全局形状，不是 workload、release、业务活动、Trace 或根因信息；因此不能把其“上下文核验”直接等同于业务状态识别或故障来源解释。（分析推断）",
      "阈值和置信过滤：F1-max 是 oracle threshold protocol；confidence 1–3 由提示模型自行产出，未见独立校准为概率的证据。（§4, Appendix B；分析推断）"
    ],
    "evidence_gaps": [
      "作者明确范围：方法主要为单变量设计；多变量只是附录扩展。对于异常不稀有的 A3/A4，作者观察到 detector 会把成簇异常当成 pattern fluctuation。（§3, §4）",
      "评测范围：11 个基准、contextual F1-max 扫阈值。没有固定业务 false-positive rate、在线延迟预算、真实告警负担或跨服务迁移实验。（§4；分析边界）",
      "运行成本：约 14.68 秒 / 序列的 GPT-4o 路径更适合离线或 human-in-the-loop，未被证明适合高频实时告警。（Appendix D.1）"
    ]
  },
  "research_implications": [
    "- [分析推断] 评估多变量 joint context、动态 scale / y-range 对极值与高波动状态的鲁棒性。 - [分析推断] 在合法业务状态切换、故障、以及二者同时出现的测试矩阵中测量 context verification 对未知故障的漏报代价。 - [分析推断] 固定误报预算下报告区间质量、检测延迟、VLM latency 和 token cost，并校准置信度。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfmae",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "time-rcd",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomseer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "vlm4ts",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§§3.1–3.2, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, Eq. 1",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "71a88d513e561c4ebfc843b7628c0904f59e711e7d4821a546763a61a9329167",
    "reading_note_sha256": "144ca86b0d8679010210406101384f2b3e6f858b7920f17280725f79a98c4735",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "619b0d9766758c928048e50ff9f3d7587491689a18da2373134f8999f4b29646"
  },
  "knowledge_card_path": "papers/vlm4ts/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
