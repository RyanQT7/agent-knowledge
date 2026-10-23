# RTdetector: Deep Transformer Networks for Time Series Anomaly Detection Based on Reconstruction Trend

## 1. Metadata

- **Authors**: Xinhong Liu, Xiaoliang Li, Yangfan Li, Fengxiao Tang, Ming Zhao
- **Year / venue**: 2025 / IJCAI (CCF B，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2025/IJCAI/RTdetector_Deep_Transformer_Networks_for_Time_Series_Anomaly_Detection_Based_on_Reconstruction_Trend.pdf)
- **Proceedings**: [IJCAI-25 PDF](https://www.ijcai.org/proceedings/2025/0644.pdf)
- **Code**: [RTdetector repository](https://github.com/CSUFUNLAB/RTdetector)
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

RTdetector 将重建趋势显式用于 Transformer 的自条件重建：先以局部窗口稳定输入并重建，再利用首轮误差作为关注信号训练第二个解码结果，同时用 RT-Attention 将原序列均值 / 方差带回注意力，以期在非平稳变化下保留原始分布趋势并减少异常被拟合。（§§3.1–3.3, Eqs. 2–14, pp.2–5）

## 3. 背景与任务

论文研究无监督多变量时间序列异常检测。常见 reconstruction model 训练时把数据拟合为可重建模式，若训练污染或模型容量较大，异常也可能得到低重建误差。已有趋势辅助方法试图让模型从正常趋势发现异常，但作者认为数据非平稳时，预处理的稳定化会丢掉原始分布变化，且静态趋势学习可能把错误变化趋势复制到正常区间。（§1, pp.1–2）

问题因此被拆为两个挑战：一是重建后怎样恢复原始分布变化；二是模型结构怎样把异常重建误差用于进一步区分，而不是让第一轮重建直接定论。（§1–2, pp.1–2）该方法中的“trend”是统计分布均值 / 方差及重建曲线层面的趋势，不是由 workload、release 或业务事件标签解释的因果来源。（§3；分析推断）

## 4. 架构总览

```text
多变量输入序列
  ├─ 窗口分段 / 位置嵌入 / Transformer encoder
  ├─ 局部 mean / std 稳定化，进入 Self-conditioning Transformer
  │    ├─ Decoder 1 输出 O1 → 重建误差作为 focus
  │    └─ Decoder 2 接收 focus → O2 / 受 focus 强调的重建 Ô2
  ├─ RTE: 反归一化，恢复原始均值与尺度变化
  └─ RT-Attention: Q/K 的均值-方差修正，保留原始趋势影响
推理分数：第一路重建误差 + focus 后第二路重建误差；POT 估阈值
```

## 5. 方法细节

### 5.1 窗口化与 Reconstruction Trend Enhancement (RTE)

设输入窗口为 $W$，按变量估计均值 $\mu_x$ 与标准差 $\sigma_x$，先标准化：

$$x'_i=(x_i-\mu_x)/\sigma_x. \tag{2}$$

稳定化让模型更容易学习局部模式；RTE 再将输出转回原尺度，使变化趋势能参与后续误差判别。**公式核对备注**：PDF Eq. (3) 印为 $o_i=\sigma_x\odot(o'_i+\mu_x)$，此顺序与常见反标准化 $\sigma_x\odot o'_i+\mu_x$ 不同。精读记录保留论文印式，不自行改正；实现时须对照官方代码确认括号和运算顺序。（§3.2, Eqs. 2–3, pp.2–3）

RTE 不只是用于最终输出的尺度还原；论文将其嵌入自条件重建过程，目的是让下一阶段的模型在原始统计变化下计算预测 / 关注信息。（§3.2, Fig. 2, pp.2–3）

### 5.2 自条件双解码器

第一阶段输出 $O_1$、$O_2$，并有相应的 RTE 输出。初始化关注分数 $F=0$；先由 decoder 产生重建，再计算第一路与输入窗口的平方重建误差 $\|O_1-W\|_2^2$，将误差作为 focus 输入第二阶段，使其关注较难重建的时间位置。图示和 Eq. (4) 定义两个基础重建损失；实际优化采用 min-max 式目标：

$$\min_{D_1}\max_{D_2}\;\|\hat O_2-W\|_2^2. \tag{5}$$

$D_1$ 需改善正常模式重建，$D_2$ 在关注信号下学习与其不同的重建趋势；训练中两者的损失组合为：

$$L_1=\eta\|O_1-W\|^2+(1-\eta)\|\hat O_2-W\|^2,$$
$$L_2=\eta\|O_2-W\|^2-(1-\eta)\|\hat O_2-W\|^2. \tag{6}$$

其中 $\eta$ 控制基础重建和自条件关注项的权重。直观上第一解码器尽可能贴合输入，第二路则在 focus 下拉开与输入 / 另一重建路径的差异，让不易被正常模型解释的位置被放大。该博弈式训练也可能对分布偏移或噪声敏感，需结合消融及部署阈值验证。（§3.2, Fig. 2, Eqs. 4–6, pp.2–3）

### 5.3 RT-Attention：将原始趋势注入注意力

标准化输入的 Query / Key / Value 隐去了原序列位置的均值和尺度变化。RT-Attention 由标准化表征构造 $Q',K',V'$，并从原始窗口的统计量形成 $\tau=\sigma_x^2$ 和 $\Delta=K\mu_Q$，以：

$$\mathrm{softmax}\!\left(\frac{\tau Q'K'^\top+\mathbf1\Delta^\top}{\sqrt{d_k}}\right)V' \tag{13}$$

修正注意力分数。其意图是恢复原序列趋势对相关性计算的影响，而不是完全依赖去趋势后的标准化特征。（§3.3, Eq. 13, pp.4–5）

### 5.4 推理异常分数

Eq. (14) 将首轮重建残差和 focus 后的第二路重建残差平均，得到最终异常分数；随后用 POT（Peaks Over Threshold）确定阈值。多变量序列中，只要变量级异常分数达到标准，论文的判定可将该时间点 / 窗口标异常。（§3.4, Eq. 14, p.5）POT 的参数、训练阈值与部署误报成本应和重建模型本身分开记录。

## 6. 实验设计与结果

### 6.1 数据与基线

使用 UCR（InternalBleeding、ECG）、MBA、SMD（四个机器子集）和 SMAP 四类 benchmark；非重叠滑动窗口长度为 10。比较 11 个基线：OmniAnomaly、MSCRED、MAD-GAN、DAGMM、LSTM-NDT、USAD、CAE-M、GDN、TranAD、MERLIN、DCdetector。（§4.1, pp.5–6）指标为 precision、recall、AUC、F1，并使用 POT 设定阈值；具体结果需结合数据集实验协议，不把单一 F1 当成跨协议无条件排名。（§4.1）

### 6.2 主表与模块消融

Table 1 中 RTdetector 在 UCR、MBA、SMD 的 F1 分别为 0.9910、0.9865、0.9983；SMAP 为 0.9094，而 DCdetector 的 SMAP F1 为 0.9702。作者称除 SMAP 外整体表现最佳，并将 SMD 收益联系到非平稳性；但“非平稳性导致收益”是作者解释，表格本身仅展示关联。（§4.2, Table 1, pp.6–7）

消融 Table 2：完整模型在 UCR F1 为 0.9983；移除 RTE 降至 0.9877；移除 RT-Attention 降至 0.9868。两组件在该实验设置下分别带来收益。（§4.3, Table 2, p.7）窗口长度实验显示窗口超过 10 后 F1 下降，作者认为更长上下文会遮蔽异常；这也意味着窗口长度依赖数据集与异常尺度。（§4.3）

### 6.3 速度与证据范围

每 epoch 训练时间约 UCR 1.38s、MBA 8.42s、SMD 72.90s、SMAP 7.19s；TranAD 对应约 .84s、4.08s、43.56s、3.55s，故 RTdetector 并非所有比较中速度最快。作者称比大多数方法快 75% 以上，但表中具体比例依赖所选基线。（§4.4, Table 3, p.7）四个 benchmark、非重叠窗口和 POT 构成主要外推边界。

## 7. 贡献、局限与复现

### 贡献

1. 将重建趋势恢复与自条件重建结合，尝试防止异常被单一路径过拟合。（§3.2）
2. 以原序列统计量修正标准注意力，明确处理标准化丢失的均值 / 方差信息。（§3.3, Eq. 13）
3. 提供 RTE / RT-Attention 消融和窗口长度敏感性结果。（§4.3）

### 局限与分析

- **公式 / 实现核对**：Eq. (3) 反归一化的括号顺序值得核验；论文公式与通用写法不一致，笔记保留原文，不替作者修订。
- **数据覆盖**：四个 benchmark 不足以证明对多类工业负载状态、慢漂移和高维跨实体关系普遍适用。
- **归一化窗口的统计估计**：均值 / 方差可能受窗口内故障比例影响；负载跃迁与故障同时发生时，统计项是否把故障解释为分布趋势尚未验证。（分析推断）
- **检测语义**：趋势恢复不说明变化来源；没有把指标与 workload、Trace、release 或拓扑关联。（实验设置；分析推断）
- **操作性**：非重叠窗口可能带来边界 / 延迟问题；POT 的阈值稳定性、固定误报预算和在线处理成本没有形成完整部署验证。（分析推断）
- **基准表现并非全面领先**：SMAP 上低于 DCdetector，且较长窗口可退化。（Table 1; §4.3）

### 复现价值

官方 [RTdetector 代码](https://github.com/CSUFUNLAB/RTdetector) 可用于核对 Eq. (3)、RTE 两路输出、min-max 损失优化顺序及 POT 参数。复现时应固定预处理、窗口切分、阈值训练集、POT 配置和实体划分，并单独测量非重叠窗口产生的告警延迟。本次仅阅读论文，未运行代码或训练模型。

## 8. 相关论文

- **IMPACT / IGAD**：都从重建泛化或训练污染切入；IGAD 改造 normal fixed-point manifold，RTdetector 用重建趋势 / 自条件误差，两者训练目标与分数不同。
- **When Model Meets New Normals**：通过测试时适配处理新正常状态；RTdetector 恢复统计变化，但不识别状态或进行持续适配。
- **MACE / TFC**：频域 / 动态模式作为正常性证据；RTdetector 将均值、方差趋势纳入注意力。
- **KAN-AD**：平滑预测抑制局部噪声；RTdetector 使用双路重建建模非平稳统计变化，可比较其残差语义与校准协议。
