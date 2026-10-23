# AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling

## 1. Metadata

- **Authors**: Junqi Chen, Xu Tan, Jie Chen, Susanto Rahardja
- **Year / venue**: 2026 / IJCAI (CCF B，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2026/IJCAI/AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf)
- **Proceedings**: [IJCAI 2026 paper](https://www.ijcai.org/proceedings/2026/0276.pdf)
- **Code**: 论文 PDF 中未列出代码仓库。
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

AnoMamba 用 channel-independent patch embedding 压缩局部冗余，再通过 Global Step-size Reweighting Mamba (GSRMamba) 以全局上下文重新加权 Mamba S6 的输入 step-size，并用随机采样的多尺度 long-tail prior 正则化重加权系数；目标是使无监督重建学习到真正正常的全局依赖，而不是只拟合局部片段。（§§3–4.6, Eqs. 1–23, pp.3–6）

## 3. 背景与问题定义

重建式 TSAD 依赖“正常序列可重建、异常序列重建误差较大”的假设。作者指出，缺少异常标签时，最小化 MSE 会偏向容易拟合的局部依赖，因此异常也可能被重建得很好；重建目标就没有对齐“学正常行为”的检测目标。（§1, Fig. 1, pp.1–2）

一种自然做法是鼓励全局依赖，但此前方案可能预先指定固定 attention 区域或依赖非端到端的频域 / 多尺度预处理。真实序列中 global vs local 依赖会随时间和上下文变化，难以固定定义。（§1–2, pp.2–3）AnoMamba 把问题表述为：如何在无异常监督下动态选择对正常行为重要的远程依赖，同时保留局部上下文。（§1–3）

## 4. 总体架构

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

## 5. 方法细节

### 5.1 Patch Embedding

长度为 $P$、步长为 $S$ 的 patch $s_n=x_{(t+nS):(t+nS+P)}$ 逐通道构造，经 1D convolution 映射为 $e_n\in\mathbb R^{D_m}$（Eq. 12, §4.1, p.4）。作者认为 patch 内已编码局部变化，后续 Mamba 可将容量用于 patch 间长程依赖。channel-independent patchify 先分别嵌入通道；跨通道信息在后续 FFN channel mixing 汇合。

### 5.2 Mamba S6 与 global step-size

Mamba 的 S6 以输入相关 $\Delta_t$ 控制状态更新：

$$h_t=A_t\odot h_{t-1}+B_t x_t,\quad y_t=C_t^T h_t,$$
$$\Delta_t=\operatorname{Softplus}(W_Dx_t),\quad A_t=\exp(\Delta_t A). \tag{1–7}$$

小 step-size 会抑制当前输入、更多保留历史；大 step-size 提高当前输入影响。（§3.2, Eqs. 1–7, p.3）原始 S6 的 $\Delta_n$ 只依赖当前 patch 表示，作者认为无监督时容易继续偏向局部拟合。

GSRMamba 先经 causal conv / SiLU 得 $u_n$，再由 global reweighting 计算 $\omega_{1:N}$：

$$F_1=\operatorname{FFN}_1(u_{1:N})+u_{1:N},\quad F_2=\operatorname{FFN}_2(F_1^T)^T+F_1,$$
$$\omega_{1:N}=\operatorname{Sigmoid}(W_4F_2),\quad \Delta_n^{GSR}=\Delta_n\odot\omega_n. \tag{13–19}$$

$FFN_1$、$FFN_2$ 分别利用 patch 维度 / 转置后维度建模全局上下文，生成每个 patch 的重权系数；经重权后的 step-size 输入 S6，再与 gate 分支 $g_n$ 逐元素相乘投影输出。（§4.2–4.3, pp.4–5）

### 5.3 Multi-scale Long-tail Priors

为避免 GSR 只强化极局部、或完全丢弃局部信息，作者对重加权系数施加 long-tail prior：

$$P(n)=(n+\alpha)^\alpha\exp(-n),\quad \alpha\ge1. \tag{20}$$

作者解释希望 global dependencies 使用较大的 step-size、local dependencies 保留较小但非零 step-size；多尺度通过每个 training iteration 随机抽 $\alpha\in[1,T]$ 实现，避免手工选一个全局尺度。KL loss 比较每层各 feature 的 $\omega$ 与 $P(n)$。（§4.4, p.5）原文称其为 Gamma-like long-tail family；具体分布归一化 / 索引约定复现时应对照实现。

### 5.4 重建目标、推理和 hidden attention

最终重建头融合 channel 表示、展平并线性投影得到 $\hat x_t$（Eqs. 21–22）。训练：

$$L=L_{rec}+\lambda L_{KL},\qquad L_{rec}=\operatorname{MSE}(x_t,\hat x_t). \tag{23}$$

测试异常分数仍是 reconstruction error。论文还将 Mamba state update 展开为输入历史对当前输出的加权和，构造 hidden attention map，观察 GSR 是否把权重从 trivial local patterns 移向全局关系（§3.3, Eqs. 8–11; §5.8, Figs. 6–7）。它是模型内部输入贡献的可视化，不是业务事件来源 / 因果解释。

## 6. 实验设计与证据

### 6.1 数据、基线、指标

8 个真实 benchmark：UCR 单变量 ECG、EPG、Gait、NASA；TSB-AD 多变量 LTDB、MITDB、SVDB、SMD。比较 MLP、CNN、RNN、Transformer 和 Mamba 方法，包括 DLinear、TimeMixer、TimesNet、MICN、ModernTCN、OmniAnomaly、Autoformer、Anomaly Transformer、PatchTST、RTdetector、SST、MS-Mamba、DMamba 等。（§5.1–5.2, pp.5–6）

评价 F1-AF（Affiliation F1）和 VUS-ROC，窗口大小统一设 100，所有阈值用 SPOT；AnoMamba model size 16、state size 8、3 blocks，五随机种子均值。（§5.3）因此结果避免某些 point-adjustment 指标，但仍依赖 SPOT 阈值与给定 window setting。

### 6.2 主结果

- **[实验支持]** AnoMamba 在 8 集中 F1-AF 7 集第一、VUS-ROC 6 集第一。（§5.4）
- **[实验支持]** UTS 平均 F1-AF / VUS-ROC 为 .7830 / .7739；MTS 平均为 .7900 / .7973。（Tables 1–2, pp.6–7）
- **[比较边界]** TimeMixer 在 Gait、NASA 等部分集表现强，MS-Mamba 在 MTS 相对更好但 UTS 较弱；所以平均优势不表示每种数据形态均领先。（§5.4）

### 6.3 消融、敏感性、效率与解释可视化

- **GSR**：去掉 GSR，UTS 平均 F1-AF .7830→.6547、VUS-ROC .7739→.7425；MTS F1-AF .7900→.7764、VUS-ROC .7973→.7701，说明全局 step-size reweighting 在 UTS / contextual anomalies 上贡献更大。（Table 3, p.6）
- **Prior**：固定 $\alpha=5,9,13$ 仍接近完整方法；作者用此支持多尺度 prior 不过度依赖某个精确先验值。（Table 3）
- **超参**：$\lambda<0.1$ 时较稳定，过大时 F1-AF 急剧下降；patch size 变化仍在合理区间，实验选 8。（§5.6, Fig. 4, p.7）
- **效率**：MITDB 上训练时间 / 显存对比显示优于多尺度 TimeMixer / MS-Mamba 与 Autoformer，接近多数 CNN；慢于 DLinear。（§5.7, Fig. 5）
- **解释案例**：GP711MarkerLFM5z1 上 hidden attention 展示有 GSR 时能用全局“大峰→小峰”关系重建异常缺失小峰，而无 GSR 会局部过拟合并产生 false negative。（§5.8, Figs. 6–7）这是案例说明，不是 attention 因果忠实度测试。

## 7. 贡献、局限与复现价值

### 贡献

1. 将 Mamba input-dependent step-size 从当前点控制扩展为全局上下文重加权，用来缓解 unsupervised reconstruction 的局部过拟合。（§4.2–4.3）
2. 以随机多尺度 long-tail prior 指导 global / local dependency 平衡，而非硬编码固定 attention positions。（§4.4）
3. 在 UTS / MTS 上用 F1-AF、VUS-ROC、五 seed，并辅以消融、效率和 hidden attention 可视化。（§5）

### 局限与分析

- 论文未列出专门的 limitation section；从实验边界看，数据仅 8 集，阈值统一用 SPOT，无法据此证明任意线上 operating point 的性能。
- 方法仍基于 reconstruction error；若异常与正常共用同样全局依赖，或关键故障只呈局部强尖峰，GSR 引导的全局关系未必能提高可分性。（分析推断）
- hidden attention map 提供模型输入贡献线索，但不等于真实业务依赖或故障来源忠实解释。（§3.3; 分析推断）
- 运行上下文如 workload、release、Trace 未输入模型；GSR 学到的是数值序列范围的关系。（§5; 分析推断）
- 固定 window 100、SPOT 阈值与少数主超参需要跨 entity / state 验证。

### 开源与复现

本 PDF 未列官方代码库；可用 IJCAI 论文页追踪。复现需实现 Mamba S6 的 GSR reweighting、patch / channel 操作、long-tail prior 的归一化 / 索引、KL 权重 $\lambda$、SPOT 及相同 window；用固定 FPR、事件延迟和 state-change/fault concurrency 另行评估。本次仅阅读 PDF，未训练或复现。

## 8. 相关论文

- **KAN-AD / RTdetector / IGAD**：都改造 reconstruction / prediction 以降低过拟合；AnoMamba 特别面向 Mamba 的 global dependency selection。
- **When Model Meets New Normals / CCM-TAD**：处理新状态或在线动态；AnoMamba 从历史上下文学习全局关系，但没有显式 state identification / online adaptation。
- **CrossAD / Sub-Adjacent Transformer**：通过多尺度或非相邻上下文约束重建；AnoMamba 的依赖跨度由 GSR 动态选择。
- **TFC / ScatterAD**：多视角 / 关系表征异常证据；AnoMamba 保持单一 Mamba reconstruction score。
