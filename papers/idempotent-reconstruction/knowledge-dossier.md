# Knowledge Dossier — Multivariate Time Series Anomaly Detection with Idempotent Reconstruction

## 1. Basic Information

- **English title**: Multivariate Time Series Anomaly Detection with Idempotent Reconstruction
- **中文译名**：基于幂等重建的多变量时间序列异常检测
- **Authors**: Xin Sun, Heng Zhou, Chao Li
- **Venue / year / CCF**: NeurIPS 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/ProEcho1/Idempotent-Generation-for-Anomaly-Detection-IGAD
- **Research area**: 重建流形约束与多变量异常检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督 MTS 重建式异常检测，处理训练污染 / decoder capacity 导致异常也重建，以及噪声鲁棒性与微小异常敏感性的折衷。（§1, p.1）
- **[实验支持]** 四个真实数据集、15 个重建模型适配实验。（§4.1）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文关注无监督多变量 TSAD：训练点没有标签，通常均视作正常数据，用 encoder-decoder 学习重建。作者将异常低重建误差的“过度泛化”归纳为两个来源：训练集混入异常，使模型学到异常模式；或 decoder 表达能力过强，以至于异常也可以被重建。（§1, p.1; Appendix A）

此外检测需在鲁棒性和敏感性间折衷：噪声扰动的正常点不应大量误报，但微小异常又应及时暴露。作者从 manifold 视角提出正常数据应落在映射不变的目标集合：$M_{target}=\{x_i:f(x_i)=x_i\}$，并通过幂等映射约束与空间收紧避免异常点也落入可重建区域。（§2–3, pp.2–3）这是论文理论抽象，实际模型对输入样本 / 窗口与增强样本计算映射。

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 异常映射进正常 target manifold 会导致 residual 不可分；噪声又会引起误报。（§§1–2）
- **[分析推断]** 合成噪声鲁棒性与合法业务状态切换、真实故障并发之间仍有外推差距。

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** contamination 和过强 decoder 导致 reconstruction over-generalization。（Appendix A）
- **[分析推断]** 常规重建改造未必能表达正常状态语义或解释波动来源。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. 一句话总结

IGAD 不替换既有重建模型，而在训练时加入频域采样增强、幂等一致性与 target-manifold tightness 三类约束：让正常样本附近映射到固定点、避免模型扩张到异常区域，并收紧异常点可被重建的空间；推理仍使用基础模型重建误差及其可选辅助分数。（§§3.1–3.3, Eqs. 1–14, pp.3–7）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 异常映射进正常 target manifold 会导致 residual 不可分；噪声又会引起误报。（§§1–2）
- **C2（第4节挑战）**：[分析推断] 合成噪声鲁棒性与合法业务状态切换、真实故障并发之间仍有外推差距。

### 7.1 频域增强

- **作者技术描述**：**[作者主张] 频域增强**：channel-wise FFT 后对实 / 虚部独立按均值方差采样，再 IFFT。（§3.1, Eqs. 3–5）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.1 基础重建损失与频域数据增强”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 固定点幂等

- **作者技术描述**：**[作者主张] 固定点幂等**：$D(f(z),f'(f(z)))$，使用冻结模型副本约束当前模型。（§3.2.1, Eq. 7）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Tightness

- **作者技术描述**：**[作者主张] Tightness**：反向优化 $D(f'(z),f(f'(z)))$，经 $\tanh(L_{tight}/(\alpha L_{recon}))$ 平滑后纳入总 loss。（§3.2.2–3.3, Eqs. 8–11）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.3 Tightness：收紧可重建的目标区域”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 轻量推理

- **作者技术描述**：**[作者主张] 轻量推理**：融合重建误差与基础辅助分数，MinMaxScaler 后以 $\mu+3\sigma$ 阈值。（§3.4, Eqs. 12–14）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.4 训练 / 推理差别”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. 架构与训练流程

```text
基础重建器 f + 可选原始辅助分数
  ├─ 正常区间 / channel FFT → 频域统计采样 → IFFT，得增强 z
  ├─ Lrecon: 原始样本 x 重建
  ├─ frozen copy f' 与可训练 f 的交叉映射
  │    ├─ Lidem: f(z) 与 f'(f(z)) 对齐（抑制 expansion path）
  │    └─ Ltight: f'(z) 与 f(f'(z)) 拉开（收紧目标流形）
  └─ 平滑后的 Ltight + 重建 / 可选辅助 loss 联合优化
推理：基础 reconstruction error + 原模型 auxiliary score；固定阈值 μ+3σ
```

IGAD 声称不增加可训练参数，也不改变推理图中的基础模型映射次数；它把附加计算集中在训练期。（§3, Fig. 2, pp.3–4）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：5.1 基础重建损失与频域数据增强。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. 技术机制详解

#### 5.1 基础重建损失与频域数据增强

基础重建损失为：

$$L_{recon}=\frac1N\sum_i\|x_i-f(x_i)\|_2^2. \tag{1}$$

频域增强以正常区间、通道为单位做 FFT，分别统计实部和虚部的均值 / 标准差，从对应高斯分布抽样 $z_{real},z_{imag}$，组合后做逆 FFT，取实部生成增强序列 $z$（Eqs. 3–5）。其意图是在保留总体谱模式的同时引入随机变化，让幂等约束作用于正常数据附近的扰动。它不是任意 waveform jitter，也不保证保留频率间相关性 / 相位关系；后一点是由独立分布采样方式推导出的风险。（§3.1, Eqs. 3–5, pp.3–4；分析推断）

#### 5.2 Idempotent consistency：压制映射扩张

幂等目标要求二次映射不再改变第一次输出：$f(f(z))\approx f(z)$。论文用 MAE 距离定义 $D_{idem}(f(z),f(f(z)))$（Eq. 6）。但若同一个可训练模型连续映射，模型可能沿着 expansion path 把局部输入扩展到别处，无法把增强正常样本附近的 target manifold 锚定稳定。为此引入当前模型的 frozen copy $f'$，替换成：

$$L_{idem}=D_{idem}(f(z),f'(f(z))). \tag{7}$$

$f'$ 在相关优化阶段冻结，$f$ 更新；该交叉约束旨在让输出留在目标映射集合附近。此处 $f'$ 是训练期权重副本，不额外增加可训练参数。（§3.2.1, Eqs. 6–7, pp.4–5）

#### 5.3 Tightness：收紧可重建的目标区域

仅鼓励幂等仍可能使过宽的输入区域成为 fixed point。论文加入 tightness 项：

$$L_{tight}=D_{tight}(f'(z),f(f'(z))). \tag{8}$$

该项在总目标中取负号，让可训练映射 $f$ 最大化这一差异，从而收紧 target manifold、减少潜在异常落入正常固定点集合的机会。过度拉开也会排斥正常样本，因此对 tightness 进行平滑裁剪：

$$L^*_{tight}=\tanh\!\left(\frac{L_{tight}}{\alpha L_{recon}}\right)\alpha L_{recon}. \tag{10}$$

$\alpha$ 控制 tightness 相对重建误差的饱和尺度；小尺度可降低 tightness 极端值主导训练的风险。总目标：

$$L=\lambda_{rec}L_{recon}+\lambda_{idem}L_{idem}+\lambda_{tight}L^*_{tight}+\lambda_{aux}L_{aux}. \tag{11}$$

其中 $L_{aux}$ 仅在被包装的基础方法提供辅助损失时使用。作者建议对幂等 / tightness 用 MAE；损失组合消融显示二者互补。（§3.2.2–3.3, Eqs. 8–11, pp.5–6）

#### 5.4 训练 / 推理差别

训练时需多个映射路径 $f(x), f(z), f'(z), f(f'(z)), f'(f(z))$；但推理仍复用原重建模型及其原辅助输出，不额外跑 IGAD manifold 迭代。论文将重建误差 $e_t=\|x_t-x_t^{rec}\|_2^2$ 与辅助分数 $a_t$ 融合，经 MinMaxScaler 归一化，固定阈值取 $\delta=\mu+3\sigma$（Eqs. 12–14, §3.4, p.6）。分数依赖基础模型实现；固定阈值也依赖校准区间及分数分布。

#### 5.5 理论论证边界

附录 A 分析含污染的 $P_{train}=(1-\eta)P_x+\eta P_a$ 与模型容量 / 正则化如何导致过度泛化；附录 B 在理想化映射与分布假设下给出 IGAD 向目标正常分布收敛的论证。（Appendix A–B, pp.25–28）应把它理解为机制合理性的理论分析，而不是对任意真实时序、所有优化器或污染比例的普适保证；正常分布与 target manifold 的可分性等前提可能不满足。（分析推断）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (3)、Eq. (6)、Eq. (8)、Eq. (12)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：5.1 基础重建损失与频域数据增强；5.4 训练 / 推理差别；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.4 训练 / 推理差别及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

IGAD 不替换既有重建模型，而在训练时加入频域采样增强、幂等一致性与 target-manifold tightness 三类约束：让正常样本附近映射到固定点、避免模型扩张到异常区域，并收紧异常点可被重建的空间；推理仍使用基础模型重建误差及其可选辅助分数。（§§3.1–3.3, Eqs. 1–14, pp.3–7）

## 9. Experimental Evidence

#### 精读笔记原章节：6. 实验设计与证据

#### 6.1 数据与模型覆盖

四个重处理的真实 MTS 数据集：SMD、MSL、PSM、SMAP。IGAD 包装 15 个重建模型 / 基础模型，包括 CATCH、M2N2、SARAD、AT、FGANomaly、CAE-M、MTAD-GAT、MSCRED、OmniAnomaly、DAGMM，以及 FITS、Peri-midFormer、ModernTCN、OFA、TimesNet 等 foundation / forecasting-based 方案（§4.1, Table 1）。五个随机种子报告均值与标准差，并用 Wilcoxon signed-rank test 比较。主要指标 VUS-PR，同时报告 AUC-PR、AUC-ROC、VUS-ROC，标准 F1 结果见附录。（§4.1, Appendix）

#### 6.2 主结果与回退案例

跨 15 个模型的各数据集平均 VUS-PR：SMD .1554→.1752（+12.71%）；MSL .0416→.0920（+120.89%）；PSM .1542→.1592（+3.28%）；SMAP .3223→.4056（+25.83%）。60 个模型-数据集组合有 52 个上升、8 个下降；作者报告 52 个正向提升中 49 个达到文中设定显著性标准。（Table 1, pp.7–9）平均增益掩盖了个别负向结果，例如 PSM 的 FGANomaly / MSCRED 及 MSL 的 MSCRED 下降；因此应同时审视每个基础模型和数据集。

#### 6.3 噪声鲁棒性与分布重叠

作者在测试数据注入 1%、5%、10%、15%、20% Gaussian noise，展示 SARAD/MSL、Anomaly Transformer/SMD 的 VUS-PR 变化，IGAD 曲线相对更稳定；CAE-M/SMD 的分数分布重叠指标从 .6713 降至 .4088，OmniAnomaly/SMAP 从 .1572 降至 .0757。（§4.2, Fig. 3–4, pp.9–10）此为合成高斯测试噪声与示例分数分布，不等于实际业务负载漂移、合法状态转换或噪声-故障同步的鲁棒性结论。

#### 6.4 消融与超参

跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L_{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\lambda_{idem},\lambda_{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。

#### 6.5 训练成本、可扩展性与局限

论文称增加的训练开销在多数模型每 epoch 小于 10 秒，但 OFA 可能明显更慢（PSM 示例增加约 200.5 秒），GPU 内存最多增约 8.5GB；尽管参数数和推理映射不增加，训练仍需要四条额外映射计算（Appendix efficiency tables, pp.42–48）。作者在 p.59 限制部分指出个别数据集表现下降、标准差变大及计算开销，计划探索降本方法。实验用单张 RTX 3090。不能将“无可训练参数 / 推理开销低”误解为训练无额外资源。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

频域 real/imag 独立高斯抽样可能破坏谱相关性 / 相位，并不必然对应真实正常状态扰动。（Eqs. 3–5；分析推断）

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

高斯测试噪声不是正常业务波动；没有对 workload / release / Trace 或负载转换叠加故障做对照。（§4.2；分析推断）

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

理论建立在较强理想条件；收紧“异常所在空间”需要正常与异常分布有可分性，强污染或合法稀有状态可能改变映射。（Appendix A–B；分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

作者明确报告部分组合退化与更大标准差；平均 VUS-PR 不能掩盖这类失败（p.59; Table 1）。

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

基础方法与数据集级网格搜索超参，推理阈值 $\mu+3\sigma$ 依赖校准分布；未证明跨域固定配置与固定误报预算。（§3.4, Appendix E.3）

#### 精读笔记原章节：7. 技术贡献、局限与复现价值 — 主要边界

训练时额外映射 / 显存成本对 OFA 等大型模型可能较重，需在部署前单独预算。（Appendix efficiency）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 对比 Gaussian、真实负载状态重采样与 release-conditioned augmentation，检验 manifold 是否覆盖合法新状态。
- **[分析推断]** 设正常状态改变、故障、二者并发三组；测量提高 tightness 对稀有 normal false positive 的影响。
- **[分析推断]** 降低训练映射开销，固定模型外推超参；报告固定 FPR、event delay 与 score calibration。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **RTdetector**：都处理重建过拟合；RTdetector 使用趋势增强和关注解码，IGAD 改造重建映射的幂等固定点与紧致性。
- **Fortifying Time Series**：关注输入扰动下的认证 / 鲁棒性；IGAD 的鲁棒证据主要是 Gaussian test noise 与训练目标正则，性质不同。
- **When Model Meets New Normals / CAPMix**：显式面向动态正常性 / KPI 噪声；IGAD 平滑噪声并约束重建，不识别状态语义。
- **MACE / TFC**：显式频率 / 多域模式；IGAD 用频域统计做增强，而不直接用频谱作为推理检测分数。
- **IMPACT**：用 influence 识别训练污染并生成 pseudo anomaly；IGAD 不依赖异常标签，依赖重建流形约束。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §2–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §§1–2 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3.1, Eqs. 3–5 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | Eq. 6 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3.2.1, Eqs. 6–7 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3.2.2–3.3, Eqs. 8–11 | 精读笔记保留的原文定位 |
| Method / formulas | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3.4, Eqs. 12–14 | 精读笔记保留的原文定位 |
| Experimental evidence | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §4.1, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §4.2, Fig. 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | Table 2 | 精读笔记保留的原文定位 |
| Limitations | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | Table 1 | 精读笔记保留的原文定位 |
| Limitations | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | Eqs. 3–5 | 精读笔记保留的原文定位 |
| Limitations | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §4.2 | 精读笔记保留的原文定位 |
| Limitations | Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf | §3.4 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "idempotent-reconstruction",
  "title_en": "Multivariate Time Series Anomaly Detection with Idempotent Reconstruction",
  "title_zh": "基于幂等重建的多变量时间序列异常检测",
  "authors": [
    "Xin Sun",
    "Heng Zhou",
    "Chao Li"
  ],
  "year": 2025,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/NeurIPS/Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
  "reading_note_path": "papers/idempotent-reconstruction/notes.md",
  "code_url": "https://github.com/ProEcho1/Idempotent-Generation-for-Anomaly-Detection-IGAD",
  "research_area": "重建流形约束与多变量异常检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] 无监督 MTS 重建式异常检测，处理训练污染 / decoder capacity 导致异常也重建，以及噪声鲁棒性与微小异常敏感性的折衷。（§1, p.1） - [实验支持] 四个真实数据集、15 个重建模型适配实验。（§4.1）",
  "research_problem": "论文关注无监督多变量 TSAD：训练点没有标签，通常均视作正常数据，用 encoder-decoder 学习重建。作者将异常低重建误差的“过度泛化”归纳为两个来源：训练集混入异常，使模型学到异常模式；或 decoder 表达能力过强，以至于异常也可以被重建。（§1, p.1; Appendix A） 此外检测需在鲁棒性和敏感性间折衷：噪声扰动的正常点不应大量误报，但微小异常又应及时暴露。作者从 manifold 视角提出正常数据应落在映射不变的目标集合：$M{target}=\\{xi:f(xi)=xi\\}$，并通过幂等映射约束与空间收紧避免异常点也落入可重建区域。（§2–3, pp.2–3）这是论文理论抽象，实际模型对输入样本 / 窗口与增强样本计算映射。",
  "core_challenges": [
    "[作者主张] 异常映射进正常 target manifold 会导致 residual 不可分；噪声又会引起误报。（§§1–2）",
    "[分析推断] 合成噪声鲁棒性与合法业务状态切换、真实故障并发之间仍有外推差距。"
  ],
  "existing_method_limits": [
    "[作者主张] contamination 和过强 decoder 导致 reconstruction over-generalization。（Appendix A）",
    "[分析推断] 常规重建改造未必能表达正常状态语义或解释波动来源。"
  ],
  "core_idea": "IGAD 不替换既有重建模型，而在训练时加入频域采样增强、幂等一致性与 target-manifold tightness 三类约束：让正常样本附近映射到固定点、避免模型扩张到异常区域，并收紧异常点可被重建的空间；推理仍使用基础模型重建误差及其可选辅助分数。（§§3.1–3.3, Eqs. 1–14, pp.3–7）",
  "technical_innovations": [
    {
      "name": "频域增强",
      "author_claim": "**[作者主张] 频域增强**：channel-wise FFT 后对实 / 虚部独立按均值方差采样，再 IFFT。（§3.1, Eqs. 3–5）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.1 基础重建损失与频域数据增强",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 频域增强**：channel-wise FFT 后对实 / 虚部独立按均值方差采样，再 IFFT。（§3.1, Eqs. 3–5）"
    },
    {
      "name": "固定点幂等",
      "author_claim": "**[作者主张] 固定点幂等**：$D(f(z),f'(f(z)))$，使用冻结模型副本约束当前模型。（§3.2.1, Eq. 7）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 固定点幂等**：$D(f(z),f'(f(z)))$，使用冻结模型副本约束当前模型。（§3.2.1, Eq. 7）"
    },
    {
      "name": "Tightness",
      "author_claim": "**[作者主张] Tightness**：反向优化 $D(f'(z),f(f'(z)))$，经 $\\tanh(L_{tight}/(\\alpha L_{recon}))$ 平滑后纳入总 loss。（§3.2.2–3.3, Eqs. 8–11）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.3 Tightness：收紧可重建的目标区域",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Tightness**：反向优化 $D(f'(z),f(f'(z)))$，经 $\\tanh(L_{tight}/(\\alpha L_{recon}))$ 平滑后纳入总 loss。（§3.2.2–3.3, Eqs. 8–11）"
    },
    {
      "name": "轻量推理",
      "author_claim": "**[作者主张] 轻量推理**：融合重建误差与基础辅助分数，MinMaxScaler 后以 $\\mu+3\\sigma$ 阈值。（§3.4, Eqs. 12–14）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.4 训练 / 推理差别",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 轻量推理**：融合重建误差与基础辅助分数，MinMaxScaler 后以 $\\mu+3\\sigma$ 阈值。（§3.4, Eqs. 12–14）"
    }
  ],
  "methodology": {
    "architecture": "text 基础重建器 f + 可选原始辅助分数 ├─ 正常区间 / channel FFT → 频域统计采样 → IFFT，得增强 z ├─ Lrecon: 原始样本 x 重建 ├─ frozen copy f' 与可训练 f 的交叉映射 │ ├─ Lidem: f(z) 与 f'(f(z)) 对齐（抑制 expansion path） │ └─ Ltight: f'(z) 与 f(f'(z)) 拉开（收紧目标流形） └─ 平滑后的 Ltight + 重建 / 可选辅助 loss 联合优化 推理：基础 reconstruction error + 原模型 auxiliary score；固定阈值 μ+3σ IGAD 声称不增加可训练参数，也不改变推理图中的基础模型映射次数；它把附加计算集中在训练期。（§3, Fig. 2, pp.3–4）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 基础重建损失与频域数据增强",
      "5.2 Idempotent consistency：压制映射扩张",
      "5.3 Tightness：收紧可重建的目标区域",
      "5.4 训练 / 推理差别",
      "5.5 理论论证边界"
    ],
    "key_formulas": [
      "Eq. (3)",
      "Eq. (6)",
      "Eq. (8)",
      "Eq. (12)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "IGAD 不替换既有重建模型，而在训练时加入频域采样增强、幂等一致性与 target-manifold tightness 三类约束：让正常样本附近映射到固定点、避免模型扩张到异常区域，并收紧异常点可被重建的空间；推理仍使用基础模型重建误差及其可选辅助分数。（§§3.1–3.3, Eqs. 1–14, pp.3–7）"
  },
  "experimental_evidence": {
    "datasets": [
      "四个重处理的真实 MTS 数据集：SMD、MSL、PSM、SMAP。IGAD 包装 15 个重建模型 / 基础模型，包括 CATCH、M2N2、SARAD、AT、FGANomaly、CAE-M、MTAD-GAT、MSCRED、OmniAnomaly、DAGMM，以及 FITS、Peri-midFormer、ModernTCN、OFA、TimesNet 等 foundation / forecasting-based 方案（§4.1, Table 1）。五个随机种子报告均值与标准差，并用 Wilcoxon signed-rank test 比较。主要指标 VUS-PR，同时报告 AUC-PR、AUC-ROC、VUS-ROC，…",
      "跨 15 个模型的各数据集平均 VUS-PR：SMD .1554→.1752（+12.71%）；MSL .0416→.0920（+120.89%）；PSM .1542→.1592（+3.28%）；SMAP .3223→.4056（+25.83%）。60 个模型-数据集组合有 52 个上升、8 个下降；作者报告 52 个正向提升中 49 个达到文中设定显著性标准。（Table 1, pp.7–9）平均增益掩盖了个别负向结果，例如 PSM 的 FGANomaly / MSCRED 及 MSL 的 MSCRED 下降；因此应同时审视每个基础模型和数据集。",
      "跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\\lambda{idem},\\lambda{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。",
      "论文称增加的训练开销在多数模型每 epoch 小于 10 秒，但 OFA 可能明显更慢（PSM 示例增加约 200.5 秒），GPU 内存最多增约 8.5GB；尽管参数数和推理映射不增加，训练仍需要四条额外映射计算（Appendix efficiency tables, pp.42–48）。作者在 p.59 限制部分指出个别数据集表现下降、标准差变大及计算开销，计划探索降本方法。实验用单张 RTX 3090。不能将“无可训练参数 / 推理开销低”误解为训练无额外资源。"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "四个重处理的真实 MTS 数据集：SMD、MSL、PSM、SMAP。IGAD 包装 15 个重建模型 / 基础模型，包括 CATCH、M2N2、SARAD、AT、FGANomaly、CAE-M、MTAD-GAT、MSCRED、OmniAnomaly、DAGMM，以及 FITS、Peri-midFormer、ModernTCN、OFA、TimesNet 等 foundation / forecasting-based 方案（§4.1, Table 1）。五个随机种子报告均值与标准差，并用 Wilcoxon signed-rank test 比较。主要指标 VUS-PR，同时报告 AUC-PR、AUC-ROC、VUS-ROC，…",
      "跨 15 个模型的各数据集平均 VUS-PR：SMD .1554→.1752（+12.71%）；MSL .0416→.0920（+120.89%）；PSM .1542→.1592（+3.28%）；SMAP .3223→.4056（+25.83%）。60 个模型-数据集组合有 52 个上升、8 个下降；作者报告 52 个正向提升中 49 个达到文中设定显著性标准。（Table 1, pp.7–9）平均增益掩盖了个别负向结果，例如 PSM 的 FGANomaly / MSCRED 及 MSL 的 MSCRED 下降；因此应同时审视每个基础模型和数据集。",
      "作者在测试数据注入 1%、5%、10%、15%、20% Gaussian noise，展示 SARAD/MSL、Anomaly Transformer/SMD 的 VUS-PR 变化，IGAD 曲线相对更稳定；CAE-M/SMD 的分数分布重叠指标从 .6713 降至 .4088，OmniAnomaly/SMAP 从 .1572 降至 .0757。（§4.2, Fig. 3–4, pp.9–10）此为合成高斯测试噪声与示例分数分布，不等于实际业务负载漂移、合法状态转换或噪声-故障同步的鲁棒性结论。",
      "跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\\lambda{idem},\\lambda{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。"
    ],
    "main_results": [
      "四个重处理的真实 MTS 数据集：SMD、MSL、PSM、SMAP。IGAD 包装 15 个重建模型 / 基础模型，包括 CATCH、M2N2、SARAD、AT、FGANomaly、CAE-M、MTAD-GAT、MSCRED、OmniAnomaly、DAGMM，以及 FITS、Peri-midFormer、ModernTCN、OFA、TimesNet 等 foundation / forecasting-based 方案（§4.1, Table 1）。五个随机种子报告均值与标准差，并用 Wilcoxon signed-rank test 比较。主要指标 VUS-PR，同时报告 AUC-PR、AUC-ROC、VUS-ROC，标准 F1 结果见附录。（§4.1, Appendix）",
      "### 6.2 主结果与回退案例",
      "跨 15 个模型的各数据集平均 VUS-PR：SMD .1554→.1752（+12.71%）；MSL .0416→.0920（+120.89%）；PSM .1542→.1592（+3.28%）；SMAP .3223→.4056（+25.83%）。60 个模型-数据集组合有 52 个上升、8 个下降；作者报告 52 个正向提升中 49 个达到文中设定显著性标准。（Table 1, pp.7–9）平均增益掩盖了个别负向结果，例如 PSM 的 FGANomaly / MSCRED 及 MSL 的 MSCRED 下降；因此应同时审视每个基础模型和数据集。",
      "作者在测试数据注入 1%、5%、10%、15%、20% Gaussian noise，展示 SARAD/MSL、Anomaly Transformer/SMD 的 VUS-PR 变化，IGAD 曲线相对更稳定；CAE-M/SMD 的分数分布重叠指标从 .6713 降至 .4088，OmniAnomaly/SMAP 从 .1572 降至 .0757。（§4.2, Fig. 3–4, pp.9–10）此为合成高斯测试噪声与示例分数分布，不等于实际业务负载漂移、合法状态转换或噪声-故障同步的鲁棒性结论。",
      "跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\\lambda{idem},\\lambda{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。"
    ],
    "ablations": [
      "### 6.4 消融与超参",
      "跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\\lambda{idem},\\lambda{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。"
    ],
    "robustness_generalization": [
      "### 6.3 噪声鲁棒性与分布重叠",
      "作者在测试数据注入 1%、5%、10%、15%、20% Gaussian noise，展示 SARAD/MSL、Anomaly Transformer/SMD 的 VUS-PR 变化，IGAD 曲线相对更稳定；CAE-M/SMD 的分数分布重叠指标从 .6713 降至 .4088，OmniAnomaly/SMAP 从 .1572 降至 .0757。（§4.2, Fig. 3–4, pp.9–10）此为合成高斯测试噪声与示例分数分布，不等于实际业务负载漂移、合法状态转换或噪声-故障同步的鲁棒性结论。",
      "跨模型平均 VUS-PR 中，使用幂等 + tightness 两项的 MAE 组合约 .208；两项都换 MSE 为 .1684。去掉 $L{idem}$ 为 .1914（相对下降约 7.98%），去掉平滑 tightness 为 .1822（下降约 12.40%），二者都移除为 .1684（下降约 19.04%）。（Table 2, pp.10–11）$\\lambda{idem},\\lambda{tight}$ 通过每个模型 / 数据集网格搜索；附录观察到较大的 tightness 可能排斥正常点，$\\alpha$ 增加后收益趋平（Appendix E.3）。因此性能是调参后的组合证据，跨域免调能力没有由此证明。"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "频域 real/imag 独立高斯抽样可能破坏谱相关性 / 相位，并不必然对应真实正常状态扰动。（Eqs. 3–5；分析推断）",
      "高斯测试噪声不是正常业务波动；没有对 workload / release / Trace 或负载转换叠加故障做对照。（§4.2；分析推断）",
      "理论建立在较强理想条件；收紧“异常所在空间”需要正常与异常分布有可分性，强污染或合法稀有状态可能改变映射。（Appendix A–B；分析推断）"
    ],
    "evidence_gaps": [
      "作者明确报告部分组合退化与更大标准差；平均 VUS-PR 不能掩盖这类失败（p.59; Table 1）。",
      "基础方法与数据集级网格搜索超参，推理阈值 $\\mu+3\\sigma$ 依赖校准分布；未证明跨域固定配置与固定误报预算。（§3.4, Appendix E.3）",
      "训练时额外映射 / 显存成本对 OFA 等大型模型可能较重，需在部署前单独预算。（Appendix efficiency）"
    ]
  },
  "research_implications": [
    "- [分析推断] 对比 Gaussian、真实负载状态重采样与 release-conditioned augmentation，检验 manifold 是否覆盖合法新状态。 - [分析推断] 设正常状态改变、故障、二者并发三组；测量提高 tightness 对稀有 normal false positive 的影响。 - [分析推断] 降低训练映射开销，固定模型外推超参；报告固定 FPR、event delay 与 score calibration。"
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
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "impact",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "rtdetector",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "idempotent-reconstruction",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "fortifying-time-series",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§3, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§3.1, Eqs. 3–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "Eq. 6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§3.2.1, Eqs. 6–7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§3.2.2–3.3, Eqs. 8–11",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§3.4, Eqs. 12–14",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Experimental evidence",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "§4.1, Table 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Experimental evidence",
      "pdf_file": "Multivariate_Time_Series_Anomaly_Detection_with_Idempotent_Reconstruction.pdf",
      "locator": "Table 1",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "b55937b2dbc9987aabbda31525f8aa776eeb6efbe70fa56662d499d77d0cc12e",
    "reading_note_sha256": "b56cde2e7dc869fc0e9502993b3918af20b8a98e922949bf1c340acbcf5d26d4",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "3c73822c1db187bf99c20e24a8d71afb9228b748503e7d6764dabdb19aa474f0"
  },
  "knowledge_card_path": "papers/idempotent-reconstruction/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
