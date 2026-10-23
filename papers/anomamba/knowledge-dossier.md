# Knowledge Dossier — AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling

## 1. Basic Information

- **English title**: AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling
- **中文译名**：AnoMamba：通过选择性全局依赖建模使重建与时间序列异常检测对齐
- **Authors**: Junqi Chen, Xu Tan, Jie Chen, Susanto Rahardja
- **Venue / year / CCF**: IJCAI 2026 / CCF B
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf](../../sources/papers/tsad-2024-2026/2026/IJCAI/AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: 选择性全局依赖的重构式无监督异常检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督重建式 TSAD 中局部依赖易拟合、异常也被重建；希望学习 global normal behavior。（§1）
- **[实验支持]** 4 个 UCR UTS + 4 个 TSB-AD MTS benchmarks。（§5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

重建式 TSAD 依赖“正常序列可重建、异常序列重建误差较大”的假设。作者指出，缺少异常标签时，最小化 MSE 会偏向容易拟合的局部依赖，因此异常也可能被重建得很好；重建目标就没有对齐“学正常行为”的检测目标。（§1, Fig. 1, pp.1–2）

一种自然做法是鼓励全局依赖，但此前方案可能预先指定固定 attention 区域或依赖非端到端的频域 / 多尺度预处理。真实序列中 global vs local 依赖会随时间和上下文变化，难以固定定义。（§1–2, pp.2–3）AnoMamba 把问题表述为：如何在无异常监督下动态选择对正常行为重要的远程依赖，同时保留局部上下文。（§1–3）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 固定位置 prior / window 无法适配随上下文变化的 global dependencies。（§1–2）
- **[分析推断]** 学得全局关系仍不保证是业务状态或故障因果关系。

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** MSE-only reconstruction 会偏向简单局部模式；Mamba 原 step-size 只依当前输入，难以充分选择长程信息。（§1–2）
- **[分析推断]** reconstruction residual、SPOT 阈值仍限制实际告警点表现。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. 一句话总结

AnoMamba 用 channel-independent patch embedding 压缩局部冗余，再通过 Global Step-size Reweighting Mamba (GSRMamba) 以全局上下文重新加权 Mamba S6 的输入 step-size，并用随机采样的多尺度 long-tail prior 正则化重加权系数；目标是使无监督重建学习到真正正常的全局依赖，而不是只拟合局部片段。（§§3–4.6, Eqs. 1–23, pp.3–6）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 固定位置 prior / window 无法适配随上下文变化的 global dependencies。（§1–2）
- **C2（第4节挑战）**：[分析推断] 学得全局关系仍不保证是业务状态或故障因果关系。

### 7.1 Patch embedding

- **作者技术描述**：**[作者主张] Patch embedding**：通道独立分 patch、Conv 编码。（§4.1, Eq. 12）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.1 Patch Embedding”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 GSR

- **作者技术描述**：**[作者主张] GSR**：$\Delta_n^{GSR}=\Delta_n\odot\omega_n$，$\omega$ 由两级 FFN 的跨 patch 上下文产生。（§§4.2–4.3, Eqs. 13–19）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.2 Mamba S6 与 global step-size”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[消融支持]** 去 GSR 后 UTS 平均 F1-AF .7830→.6547；MTS VUS-ROC .7973→.7701。（Table 3）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Multi-scale prior

- **作者技术描述**：**[作者主张] Multi-scale prior**：$P(n)=(n+\alpha)^\alpha e^{-n}$，每步随机采样 $\alpha\in[1,T]$，用 KL regularize。（§4.4, Eqs. 20, 23）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.3 Multi-scale Long-tail Priors”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Hidden attention

- **作者技术描述**：**[作者主张] Hidden attention**：由 SSM 展开式显示输入点对 reconstruction 的贡献。（§3.3, Eqs. 8–11）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.4 重建目标、推理和 hidden attention”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. 总体架构

```text
输入窗口 X
  ├─ Channel-independent patchify + Conv：提取局部 patch 表示、降低点级冗余
  ├─ GSRMamba block × 3
  │    ├─ Mamba S6：输入相关 step-size Δn 控制当前 / 历史信息
  │    ├─ GSR model：跨 patch 生成 ωn，全局重加权 step-size ΔGSR=Δ⊙ω
  │    └─ multi-scale prior：KL 正则 ω，避免只保留易拟合局部关系
  ├─ FFN channel mixing
  └─ flatten + projection 重建窗口
训练：MSE reconstruction + λ·KL(GSR weights || long-tail prior)
推理：重建误差；SPOT 阈值
```

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. 方法细节

#### 5.1 Patch Embedding

长度为 $P$、步长为 $S$ 的 patch $s_n=x_{(t+nS):(t+nS+P)}$ 逐通道构造，经 1D convolution 映射为 $e_n\in\mathbb R^{D_m}$（Eq. 12, §4.1, p.4）。作者认为 patch 内已编码局部变化，后续 Mamba 可将容量用于 patch 间长程依赖。channel-independent patchify 先分别嵌入通道；跨通道信息在后续 FFN channel mixing 汇合。

#### 5.2 Mamba S6 与 global step-size

Mamba 的 S6 以输入相关 $\Delta_t$ 控制状态更新：

$$h_t=A_t\odot h_{t-1}+B_t x_t,\quad y_t=C_t^T h_t,$$
$$\Delta_t=\operatorname{Softplus}(W_Dx_t),\quad A_t=\exp(\Delta_t A). \tag{1–7}$$

小 step-size 会抑制当前输入、更多保留历史；大 step-size 提高当前输入影响。（§3.2, Eqs. 1–7, p.3）原始 S6 的 $\Delta_n$ 只依赖当前 patch 表示，作者认为无监督时容易继续偏向局部拟合。

GSRMamba 先经 causal conv / SiLU 得 $u_n$，再由 global reweighting 计算 $\omega_{1:N}$：

$$F_1=\operatorname{FFN}_1(u_{1:N})+u_{1:N},\quad F_2=\operatorname{FFN}_2(F_1^T)^T+F_1,$$
$$\omega_{1:N}=\operatorname{Sigmoid}(W_4F_2),\quad \Delta_n^{GSR}=\Delta_n\odot\omega_n. \tag{13–19}$$

$FFN_1$、$FFN_2$ 分别利用 patch 维度 / 转置后维度建模全局上下文，生成每个 patch 的重权系数；经重权后的 step-size 输入 S6，再与 gate 分支 $g_n$ 逐元素相乘投影输出。（§4.2–4.3, pp.4–5）

#### 5.3 Multi-scale Long-tail Priors

为避免 GSR 只强化极局部、或完全丢弃局部信息，作者对重加权系数施加 long-tail prior：

$$P(n)=(n+\alpha)^\alpha\exp(-n),\quad \alpha\ge1. \tag{20}$$

作者解释希望 global dependencies 使用较大的 step-size、local dependencies 保留较小但非零 step-size；多尺度通过每个 training iteration 随机抽 $\alpha\in[1,T]$ 实现，避免手工选一个全局尺度。KL loss 比较每层各 feature 的 $\omega$ 与 $P(n)$。（§4.4, p.5）原文称其为 Gamma-like long-tail family；具体分布归一化 / 索引约定复现时应对照实现。

#### 5.4 重建目标、推理和 hidden attention

最终重建头融合 channel 表示、展平并线性投影得到 $\hat x_t$（Eqs. 21–22）。训练：

$$L=L_{rec}+\lambda L_{KL},\qquad L_{rec}=\operatorname{MSE}(x_t,\hat x_t). \tag{23}$$

测试异常分数仍是 reconstruction error。论文还将 Mamba state update 展开为输入历史对当前输出的加权和，构造 hidden attention map，观察 GSR 是否把权重从 trivial local patterns 移向全局关系（§3.3, Eqs. 8–11; §5.8, Figs. 6–7）。它是模型内部输入贡献的可视化，不是业务事件来源 / 因果解释。

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (8)、Eq. (12)、Eq. (21)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.4 重建目标、推理和 hidden attention及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

AnoMamba 用 channel-independent patch embedding 压缩局部冗余，再通过 Global Step-size Reweighting Mamba (GSRMamba) 以全局上下文重新加权 Mamba S6 的输入 step-size，并用随机采样的多尺度 long-tail prior 正则化重加权系数；目标是使无监督重建学习到真正正常的全局依赖，而不是只拟合局部片段。（§§3–4.6, Eqs. 1–23, pp.3–6）

## 9. Experimental Evidence

#### 精读笔记原章节：6. 实验设计与证据

#### 6.1 数据、基线、指标

8 个真实 benchmark：UCR 单变量 ECG、EPG、Gait、NASA；TSB-AD 多变量 LTDB、MITDB、SVDB、SMD。比较 MLP、CNN、RNN、Transformer 和 Mamba 方法，包括 DLinear、TimeMixer、TimesNet、MICN、ModernTCN、OmniAnomaly、Autoformer、Anomaly Transformer、PatchTST、RTdetector、SST、MS-Mamba、DMamba 等。（§5.1–5.2, pp.5–6）

评价 F1-AF（Affiliation F1）和 VUS-ROC，窗口大小统一设 100，所有阈值用 SPOT；AnoMamba model size 16、state size 8、3 blocks，五随机种子均值。（§5.3）因此结果避免某些 point-adjustment 指标，但仍依赖 SPOT 阈值与给定 window setting。

#### 6.2 主结果

- **[实验支持]** AnoMamba 在 8 集中 F1-AF 7 集第一、VUS-ROC 6 集第一。（§5.4）
- **[实验支持]** UTS 平均 F1-AF / VUS-ROC 为 .7830 / .7739；MTS 平均为 .7900 / .7973。（Tables 1–2, pp.6–7）
- **[比较边界]** TimeMixer 在 Gait、NASA 等部分集表现强，MS-Mamba 在 MTS 相对更好但 UTS 较弱；所以平均优势不表示每种数据形态均领先。（§5.4）

#### 6.3 消融、敏感性、效率与解释可视化

- **GSR**：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6）
- **Prior**：固定 $\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3）
- **超参**：$\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。（§5.6, Fig. 4, p.7）
- **效率**：MITDB 上训练时间 / 显存对比显示优于多尺度 TimeMixer / MS-Mamba 与 Autoformer，接近多数 CNN；慢于 DLinear。（§5.7, Fig. 5）
- **解释案例**：GP711MarkerLFM5z1 上 hidden attention 展示有 GSR 时能用全局“大峰→小峰”关系重建异常缺失小峰，而无 GSR 会局部过拟合并产生 false negative。（§5.8, Figs. 6–7）这是案例说明，不是 attention 因果忠实度测试。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：7. 贡献、局限与复现价值 — 局限与分析

方法仍基于 reconstruction error；若异常与正常共用同样全局依赖，或关键故障只呈局部强尖峰，GSR 引导的全局关系未必能提高可分性。（分析推断）

#### 精读笔记原章节：7. 贡献、局限与复现价值 — 局限与分析

hidden attention map 提供模型输入贡献线索，但不等于真实业务依赖或故障来源忠实解释。（§3.3; 分析推断）

#### 精读笔记原章节：7. 贡献、局限与复现价值 — 局限与分析

运行上下文如 workload、release、Trace 未输入模型；GSR 学到的是数值序列范围的关系。（§5; 分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：7. 贡献、局限与复现价值 — 局限与分析

论文未列出专门的 limitation section；从实验边界看，数据仅 8 集，阈值统一用 SPOT，无法据此证明任意线上 operating point 的性能。

#### 精读笔记原章节：7. 贡献、局限与复现价值 — 局限与分析

固定 window 100、SPOT 阈值与少数主超参需要跨 entity / state 验证。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 将 GSR 与业务上下文 / 动态状态适配结合，测负载变化和故障并发。
- **[分析推断]** 检验 hidden attention 与真实 topology / injected cause 的忠实性。
- **[分析推断]** 固定 FPR、point / event delay 和多 entity 外推下比较 local/global trade-off。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **KAN-AD / RTdetector / IGAD**：都改造 reconstruction / prediction 以降低过拟合；AnoMamba 特别面向 Mamba 的 global dependency selection。
- **When Model Meets New Normals / CCM-TAD**：处理新状态或在线动态；AnoMamba 从历史上下文学习全局关系，但没有显式 state identification / online adaptation。
- **CrossAD / Sub-Adjacent Transformer**：通过多尺度或非相邻上下文约束重建；AnoMamba 的依赖跨度由 GSR 动态选择。
- **TFC / ScatterAD**：多视角 / 关系表征异常证据；AnoMamba 保持单一 Mamba reconstruction score。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §1, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §1–2, §1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §1 | 精读笔记保留的原文定位 |
| Research problem / scenario | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5 | 精读笔记保留的原文定位 |
| Challenges / prior methods | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §4.1, Eq. 12 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §3.2, Eqs. 1–7 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §4.2–4.3 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §4.4 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | Eqs. 21–22 | 精读笔记保留的原文定位 |
| Method / formulas | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §3.3, §5.8, Eqs. 8–11 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.1–5.2 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.3 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.4 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.6, Fig. 4 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.7, Fig. 5 | 精读笔记保留的原文定位 |
| Experimental evidence | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5.8 | 精读笔记保留的原文定位 |
| Limitations | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §3.3 | 精读笔记保留的原文定位 |
| Limitations | AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf | §5 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "anomamba",
  "title_en": "AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling",
  "title_zh": "AnoMamba：通过选择性全局依赖建模使重建与时间序列异常检测对齐",
  "authors": [
    "Junqi Chen",
    "Xu Tan",
    "Jie Chen",
    "Susanto Rahardja"
  ],
  "year": 2026,
  "venue": "IJCAI",
  "ccf_level": "B",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/IJCAI/AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
  "reading_note_path": "papers/anomamba/notes.md",
  "code_url": null,
  "research_area": "选择性全局依赖的重构式无监督异常检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] 无监督重建式 TSAD 中局部依赖易拟合、异常也被重建；希望学习 global normal behavior。（§1） - [实验支持] 4 个 UCR UTS + 4 个 TSB-AD MTS benchmarks。（§5）",
  "research_problem": "重建式 TSAD 依赖“正常序列可重建、异常序列重建误差较大”的假设。作者指出，缺少异常标签时，最小化 MSE 会偏向容易拟合的局部依赖，因此异常也可能被重建得很好；重建目标就没有对齐“学正常行为”的检测目标。（§1, Fig. 1, pp.1–2） 一种自然做法是鼓励全局依赖，但此前方案可能预先指定固定 attention 区域或依赖非端到端的频域 / 多尺度预处理。真实序列中 global vs local 依赖会随时间和上下文变化，难以固定定义。（§1–2, pp.2–3）AnoMamba 把问题表述为：如何在无异常监督下动态选择对正常行为重要的远程依赖，同时保留局部上下文。（§1–3）",
  "core_challenges": [
    "[作者主张] 固定位置 prior / window 无法适配随上下文变化的 global dependencies。（§1–2）",
    "[分析推断] 学得全局关系仍不保证是业务状态或故障因果关系。"
  ],
  "existing_method_limits": [
    "[作者主张] MSE-only reconstruction 会偏向简单局部模式；Mamba 原 step-size 只依当前输入，难以充分选择长程信息。（§1–2）",
    "[分析推断] reconstruction residual、SPOT 阈值仍限制实际告警点表现。"
  ],
  "core_idea": "AnoMamba 用 channel-independent patch embedding 压缩局部冗余，再通过 Global Step-size Reweighting Mamba (GSRMamba) 以全局上下文重新加权 Mamba S6 的输入 step-size，并用随机采样的多尺度 long-tail prior 正则化重加权系数；目标是使无监督重建学习到真正正常的全局依赖，而不是只拟合局部片段。（§§3–4.6, Eqs. 1–23, pp.3–6）",
  "technical_innovations": [
    {
      "name": "Patch embedding",
      "author_claim": "**[作者主张] Patch embedding**：通道独立分 patch、Conv 编码。（§4.1, Eq. 12）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.1 Patch Embedding",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Patch embedding**：通道独立分 patch、Conv 编码。（§4.1, Eq. 12）"
    },
    {
      "name": "GSR",
      "author_claim": "**[作者主张] GSR**：$\\Delta_n^{GSR}=\\Delta_n\\odot\\omega_n$，$\\omega$ 由两级 FFN 的跨 patch 上下文产生。（§§4.2–4.3, Eqs. 13–19）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.2 Mamba S6 与 global step-size",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[消融支持]** 去 GSR 后 UTS 平均 F1-AF .7830→.6547；MTS VUS-ROC .7973→.7701。（Table 3）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] GSR**：$\\Delta_n^{GSR}=\\Delta_n\\odot\\omega_n$，$\\omega$ 由两级 FFN 的跨 patch 上下文产生。（§§4.2–4.3, Eqs. 13–19）"
    },
    {
      "name": "Multi-scale prior",
      "author_claim": "**[作者主张] Multi-scale prior**：$P(n)=(n+\\alpha)^\\alpha e^{-n}$，每步随机采样 $\\alpha\\in[1,T]$，用 KL regularize。（§4.4, Eqs. 20, 23）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.3 Multi-scale Long-tail Priors",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Multi-scale prior**：$P(n)=(n+\\alpha)^\\alpha e^{-n}$，每步随机采样 $\\alpha\\in[1,T]$，用 KL regularize。（§4.4, Eqs. 20, 23）"
    },
    {
      "name": "Hidden attention",
      "author_claim": "**[作者主张] Hidden attention**：由 SSM 展开式显示输入点对 reconstruction 的贡献。（§3.3, Eqs. 8–11）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.4 重建目标、推理和 hidden attention",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Hidden attention**：由 SSM 展开式显示输入点对 reconstruction 的贡献。（§3.3, Eqs. 8–11）"
    }
  ],
  "methodology": {
    "architecture": "text 输入窗口 X ├─ Channel-independent patchify + Conv：提取局部 patch 表示、降低点级冗余 ├─ GSRMamba block × 3 │ ├─ Mamba S6：输入相关 step-size Δn 控制当前 / 历史信息 │ ├─ GSR model：跨 patch 生成 ωn，全局重加权 step-size ΔGSR=Δ⊙ω │ └─ multi-scale prior：KL 正则 ω，避免只保留易拟合局部关系 ├─ FFN channel mixing └─ flatten + projection 重建窗口 训练：MSE reconstruction + λ·KL(GSR weights || long-tail prior) 推理：重建误差；SPOT 阈值",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 Patch Embedding",
      "5.2 Mamba S6 与 global step-size",
      "5.3 Multi-scale Long-tail Priors",
      "5.4 重建目标、推理和 hidden attention"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (8)",
      "Eq. (12)",
      "Eq. (21)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "AnoMamba 用 channel-independent patch embedding 压缩局部冗余，再通过 Global Step-size Reweighting Mamba (GSRMamba) 以全局上下文重新加权 Mamba S6 的输入 step-size，并用随机采样的多尺度 long-tail prior 正则化重加权系数；目标是使无监督重建学习到真正正常的全局依赖，而不是只拟合局部片段。（§§3–4.6, Eqs. 1–23, pp.3–6）"
  },
  "experimental_evidence": {
    "datasets": [
      "8 个真实 benchmark：UCR 单变量 ECG、EPG、Gait、NASA；TSB-AD 多变量 LTDB、MITDB、SVDB、SMD。比较 MLP、CNN、RNN、Transformer 和 Mamba 方法，包括 DLinear、TimeMixer、TimesNet、MICN、ModernTCN、OmniAnomaly、Autoformer、Anomaly Transformer、PatchTST、RTdetector、SST、MS-Mamba、DMamba 等。（§5.1–5.2, pp.5–6）"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 6.1 数据、基线、指标",
      "评价 F1-AF（Affiliation F1）和 VUS-ROC，窗口大小统一设 100，所有阈值用 SPOT；AnoMamba model size 16、state size 8、3 blocks，五随机种子均值。（§5.3）因此结果避免某些 point-adjustment 指标，但仍依赖 SPOT 阈值与给定 window setting。",
      "- [实验支持] AnoMamba 在 8 集中 F1-AF 7 集第一、VUS-ROC 6 集第一。（§5.4） - [实验支持] UTS 平均 F1-AF / VUS-ROC 为 .7830 / .7739；MTS 平均为 .7900 / .7973。（Tables 1–2, pp.6–7） - [比较边界] TimeMixer 在 Gait、NASA 等部分集表现强，MS-Mamba 在 MTS 相对更好但 UTS 较弱；所以平均优势不表示每种数据形态均领先。（§5.4）",
      "- GSR：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6） - Prior：固定 $\\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3） - 超参：$\\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。…"
    ],
    "main_results": [
      "### 6.2 主结果",
      "- [实验支持] AnoMamba 在 8 集中 F1-AF 7 集第一、VUS-ROC 6 集第一。（§5.4） - [实验支持] UTS 平均 F1-AF / VUS-ROC 为 .7830 / .7739；MTS 平均为 .7900 / .7973。（Tables 1–2, pp.6–7） - [比较边界] TimeMixer 在 Gait、NASA 等部分集表现强，MS-Mamba 在 MTS 相对更好但 UTS 较弱；所以平均优势不表示每种数据形态均领先。（§5.4）",
      "- GSR：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6） - Prior：固定 $\\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3） - 超参：$\\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。…"
    ],
    "ablations": [
      "### 6.3 消融、敏感性、效率与解释可视化",
      "- GSR：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6） - Prior：固定 $\\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3） - 超参：$\\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。…"
    ],
    "robustness_generalization": [
      "### 6.3 消融、敏感性、效率与解释可视化",
      "- GSR：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6） - Prior：固定 $\\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3） - 超参：$\\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。…"
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
      "方法仍基于 reconstruction error；若异常与正常共用同样全局依赖，或关键故障只呈局部强尖峰，GSR 引导的全局关系未必能提高可分性。（分析推断）",
      "hidden attention map 提供模型输入贡献线索，但不等于真实业务依赖或故障来源忠实解释。（§3.3; 分析推断）",
      "运行上下文如 workload、release、Trace 未输入模型；GSR 学到的是数值序列范围的关系。（§5; 分析推断）"
    ],
    "evidence_gaps": [
      "论文未列出专门的 limitation section；从实验边界看，数据仅 8 集，阈值统一用 SPOT，无法据此证明任意线上 operating point 的性能。",
      "固定 window 100、SPOT 阈值与少数主超参需要跨 entity / state 验证。"
    ]
  },
  "research_implications": [
    "- [分析推断] 将 GSR 与业务上下文 / 动态状态适配结合，测负载变化和故障并发。 - [分析推断] 检验 hidden attention 与真实 topology / injected cause 的忠实性。 - [分析推断] 固定 FPR、point / event delay 和多 entity 外推下比较 local/global trade-off。"
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
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "ccm-tad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomamba",
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
      "paper_id": "sub-adjacent-transformer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "kan-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§1–2, §1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§4.1, Eq. 12",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§3.2, Eqs. 1–7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§4.2–4.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§4.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "Eqs. 21–22",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§3.3, §5.8, Eqs. 8–11",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Experimental evidence",
      "pdf_file": "AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf",
      "locator": "§5.1–5.2",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "25bf8df061b9553bdd8ad33ffb93a3eb4cb50a241d8dd22ccf87aa6d20204edc",
    "reading_note_sha256": "9119899c3fbdd1241670630afbc541ec647f50c5914e4583d70d855b5d950f6b",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "c4411b4f48a9764bde9e8a3b1870ef06966e17c0d890a757dfac47f84436accb"
  },
  "knowledge_card_path": "papers/anomamba/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
