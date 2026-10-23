# COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing

## 1. Metadata

- **Authors**: Wenlong Shang, Shihao Tian, Xutong Wan, Peng Chang
- **Year / venue**: 2026 / ICML (CCF A，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2026/ICML/COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf)
- **Proceedings**: [ICML 2026 poster](https://icml.cc/virtual/2026/poster/60841)
- **Preprint**: [arXiv:2511.06894](https://arxiv.org/abs/2511.06894)
- **Code**: [COGNOS repository](https://github.com/giansha/COGNOS)
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

COGNOS 不另造检测 backbone，而把 MSE 重建器的正常残差通过 Gaussian-White-Noise Regularized (GWNR) loss 整形成近似高斯白噪声，再用每通道离线校准的 Adaptive Residual Kalman Smoother (ARKS) 平滑背景噪声、在 NIS 统计显著时快速跟踪结构突变；作者明确指出它偏向异常 onset 检测，可能无法覆盖完整异常区间。（§§3–4, Eqs. 1–16; Limitations, p.9）

## 3. 背景与问题定义

作者把观测分解为可预测确定性动态、不可约随机噪声和稀疏结构异常：

$$X_t=f_\theta(X_{<t})+n_t+s_t. \tag{1}$$

正常时 $s_t=0$；重建器预测 $\hat X_t$ 后得到 $R_t=X_t-\hat X_t$。作者指出 MSE 只在 i.i.d. Gaussian noise 等假设下对应简单高斯似然；真实序列的 residual 常仍含自相关、非高斯重尾和正常状态噪声变化，使得 raw reconstruction error 形成高噪声底，难以以稳定的白噪声 null 假设设阈。（§1, §3, Fig. 1, pp.1–3）

COGNOS 把“正常 residual 近似 Gaussian white noise、异常是结构性偏离”作为明确归纳假设。它不是跨任意 TSAD 目标的通用插件：作者限制到使用 MSE reconstruction residual 的 backbone；例如只优化 association discrepancy 的 Anomaly Transformer 不产生其 ARKS 所需 residual。（§3, §6, p.9）

## 4. 挑战与现有方法不足

1. MSE 降低平均 residual 能量，却不保证 residual 无时间相关或呈 Gaussian；模型还可能把异常尖峰拟合进去。（§3; Appendix A.1）
2. 传统 moving-average / low-pass 降噪会同时压低异常 onset 并引入延迟；固定过程噪声 Kalman filter 则在平滑和快速跟踪突变间折衷。（§4.2.2）
3. 恒定 / frozen sensor 区段不适合强加白噪声统计约束；transition 附近必须保留活动边界。（§4.1.1）
4. 噪声方差可能随 operating state 改变；用固定 $R$ 会在高信号期间误触发。（作者 limitations, p.9）

## 5. 总体架构

```text
任意 MSE reconstruction backbone
 Training / GWNR
   ├─ 全序列 MSE：残差总能量最小
   ├─ active mask：只在有效动态残差约束统计属性
   ├─ PSD → uniform：降低残差频谱集中度 / 时间相关
   ├─ Haar DWT detail → Gaussian MMD：整形高频残差分布
   └─ gradient balancing：避免正则淹没重建任务
 Inference / ARKS (per channel)
   ├─ normal calibration residuals → AR(1) leakage tracking 或 random-walk noise suppression
   ├─ sliding overlapping predictions → buffer aggregation
   ├─ NIS χ² test → circuit breaker 动态放大 Q
   └─ Kalman posterior structural signal energy → anomaly score
```

## 6. 方法细节

### 6.1 Activity-aware dynamic mask

用一阶绝对差 $\Delta_t=|X_t-X_{t-1}|$，通过形态学 dilation 构造 active mask：

$$M_t=\max_{k\in[-w,w]}\mathbf1(\Delta_{t+k}>\delta). \tag{2}$$

主要重建 MSE $L_{MSE}=\|R\|_F^2/N$ 作用于全体输入，避免 frozen zone 漂移；频域 / 统计正则仅作用于 $R_{active}=R\odot M$ 的有效片段。（§4.1.1–4.1.2, Eqs. 2–3, pp.3–4）

### 6.2 GWNR：时间、频域、统计域 residual engineering

**时间域：全局能量。** $L_{MSE}=\|R\|_F^2/N$ 保留基础拟合精度（Eq. 3）。

**频域：谱白化。** 对 active residual 做 DFT 得 $Z(f)$ 与功率谱 $S(f)=|Z(f)|^2$，归一化为频率概率 $\tilde S$；定义与均匀分布 $U(f)=1/K$ 的 KL：

$$L_{Spec}=\sum_f\tilde S(f)\log\tilde S(f)+\log K. \tag{5}$$

最小化它等价于提高谱熵 / 频谱平坦度，目标是降低时间相关残留；并非直接对白化原始观测序列。（§4.1.3, Eqs. 4–5, p.4）

**统计域：Wavelet MMD。** 对 $R_{active}$ 做正交 Haar DWT，拆出低频 approximation $A$ 与高频 detail $D$（Eq. 6）。作者称只约束 $D$，以避免妨碍 backbone 拟合趋势；在时间维 instance standardization 后，使用 multi-scale RBF-kernel MMD 使 $\tilde D$ 接近标准 Gaussian（Eq. 7）。标准化旨在约束分布形状而非每个 channel 的物理方差。（§4.1.4, pp.4–5）

**梯度平衡。** 总目标为 $L_{total}=L_{MSE}+\sum_{k\in\{Spec,MMD\}}\alpha_kL_k$；用主损失梯度范数 $G_{main}$ 与辅助梯度 $G_k$ 自适应缩放：

$$\alpha_k=\operatorname{sg}\!\left(\frac{G_{main}}{G_k+\delta}\right)\mathbf1(L_k>\delta). \tag{8}$$

该机制避免在不同损失尺度下 GWNR 压过重建 fidelity。（§4.1.5, Eqs. 8–9, p.5）

### 6.3 ARKS：离线校准的每通道状态空间滤波

每个 channel 的 residual $y_t$ 由线性 Gaussian SSM 表示：$x_t=Ax_{t-1}+w_t$，$y_t=Hx_t+v_t$，其中隐状态 $x_t$ 被解释为 anomaly signal；正常时期望 $x_t\approx0$（Eq. 10）。只用 normal calibration residual 的 lag autocovariances $\gamma_k$ 离线估计参数并分两种模式（Eq. 11）：

- **Leakage-Tracking mode**：若 $\gamma_1>\delta$ 且 $\gamma_2>\delta$，以 Yule-Walker 拟合 AR(1)，让滤波状态吸收 backbone 留下的可预测周期泄漏，避免当 anomaly 分数累加。
- **Noise-Suppression mode**：否则设 $A=1,R=\gamma_0,Q=\lambda R$ 且 $\lambda\ll1$，让 Kalman gain 较低、正常白噪声被压制。（§4.2.1, p.5）

### 6.4 NIS Circuit Breaker 与异常分数

每步先预测 $\hat x_{t|t-1}=A\hat x_{t-1|t-1}$（Eq. 12），计算 normalized innovation squared：

$$\epsilon_t=\frac{(y_t-\hat x_{t|t-1})^2}{P_{t|t-1}+R}. \tag{13}$$

若 $\epsilon_t>\tau_\alpha$，在 $H_0$（Gaussian white residual）下视作统计显著结构突变，放大过程方差 $Q_t^*=\beta R$；否则沿用 $Q_{base}$（Eqs. 14–15）。随后更新 Kalman gain 和后验 $\hat x_{t|t}$（Eq. 16）。最终分数为结构状态能量 $S_t=\|\hat x_{t|t}\|^2$（§4.2.2–4.2.3, pp.5–6）。

作者还对 backbone 重叠窗口的 residual 进行固定 buffer aggregation：等一个时间点由其覆盖的 $w$ 个窗口预测均值完成后再进 ARKS；实验取 $k=w-1$，稳定优先，较小 $k$ 可降延迟但数值稳定性下降。（Appendix, Algorithm 1, pp.16–17）

### 6.5 “Onset”与“duration”之间的设计取舍

Circuit Breaker 对首次显著创新快速提高 gain，便于捕获异常开始时刻；若随后序列停留在新稳态，innovation 会减小，滤波后验异常分数衰减。作者指出该机制抑制持续报警疲劳，但会损害奖励完整时间覆盖的 range metrics；需要按告警目标决定更偏 onset 还是 interval coverage。（§5.2, p.7; Limitations, p.9）

## 7. 实验设计与证据

### 7.1 数据、backbone、指标和阈值

7 类真实数据：MSL、SMAP、SWaT、PSM、GECCO、SWAN、UCR。9 个 backbone 覆盖 CrossAD、KAN-AD、LSTM-AE、ModernTCN、TimesNet、TimeMixer++、Autoformer、DLinear、MICN。评价包含 Standard F1（点调整）、Aff-F1、Range-AUC-ROC / PR、VUS-ROC / PR；UCR 报 250 subsets 平均（§5.1; Appendix D.1, pp.6, 22）。

ARKS confidence level $1-\alpha=0.90$ 在所有数据集统一，calibration 使用仅含正常序列的 training split。分数二值化使用每个数据集统一 global quantile percentile，在 98%–99.5% 的约束区间选取，并对各模型共享，不做 per-model exhaustive F1-max 或动态阈值（Appendix D.2, pp.19, 22–24）。百分位具体选择依据仍应在复现报告中说清楚。

### 7.2 主结果与不一致指标

- **[实验支持]** 例如 KAN-AD backbone 在 MSL 上 Standard-F1 .8115→.9165、Aff-F1 .5360→.9157；TimesNet 在 SWAN Standard-F1 .7371→.8313、Aff-F1 .1961→.5249。结果支持 COGNOS 在若干架构 / 数据上的显著改善。（Table 1, pp.6–7）
- **[证据边界]** 不是每个 backbone × metric 都提高：KAN-AD 在 PSM 上 Std-F1 .8946→.9744、Aff-F1 .6223→.8628 上升，但 Range-AUC-ROC .7005→.6799、VUS-ROC .6846→.6624、VUS-PR .4724→.4432 下降；GECCO 上 Autoformer 某些 range / VUS-PR 指标也退化。（Table 1; Appendix Table 7）
- **[作者结论]** 作者称跨架构总体稳定增益，并把优势归于 GWNR 与 ARKS 协同；平均 / selected metrics 不应抹去上面的下降和 onset-vs-coverage 取舍。（§5.2; Table 1）

### 7.3 消融、诊断和开销

- **[消融支持]** KAN-AD backbone 消融中，不带 GWNR 的 ARKS 单独在 PSM Standard-F1 .8946→.9433，但在 MSL .8115→.8083 略降；说明 filter 作用依赖 residual 条件。（Table 3, p.7）
- **[消融反例]** GECCO 上 GWNR 单独把 Standard-F1 从 .4738 降至 .3440；整套 GWNR+ARKS 才到 .7466。残差白化可能降低原始 residual 分数可分性，必须与 score extractor 联合验证。（Table 3）
- **[机制诊断]** SWaT / PSM / SMAP residual ACF 与 QQ plot 显示 GWNR 后自相关下降、Gaussian QQ 对齐改善；这些图仅是选定序列的分布诊断。（Figs. 3, 5–7, pp.7–8; Appendix C）
- **[效率]** 框架训练需多项 loss 和反向梯度范数，ARKS 还有逐点递归和重叠窗口 buffer；附录以 RTX 4090 / EPYC 测试，实际开销依 backbone。（Table 4, Appendix D.4）

## 8. 贡献、局限与复现价值

### 贡献

1. 把 residual 的时间谱形与统计分布纳入训练目标，而非只堆叠更复杂 backbone。（§4.1）
2. 将正常 residual 校准和异常过程信号分离为每通道 ARKS 状态空间模型，使用 NIS 驱动动态 gain。（§4.2）
3. 提供九个 backbone、多个 range / event metrics、component filter 对照和 residual ACF / QQ diagnostics。（§5; Appendix D）

### 局限

- **[作者指出] 固定噪声方差**：校准 $R$ 假设噪声地板跨状态稳定；状态相关 heteroscedastic noise 可能误报，作者计划自适应 $R$。（Limitations, p.9）
- **[作者指出] 目标适用范围**：针对 MSE reconstruction residual；不直接适用于没有这种 residual 的 association / contrastive detector。（Limitations, p.9）
- **[作者指出] onset bias**：擅长异常 onset，未必覆盖长异常区间；需要按业务告警任务调整 circuit-breaker confidence。（§6, p.9）
- **[分析推断] 白噪声假设**：合法负载状态切换也可能产生显著 NIS；方法没有 workload / release / Trace 判断来源，可能触发告警或在持续新状态中迅速衰减。
- **[理论边界] 通道独立性**：ARKS channel-wise factorization 在 covariance 对角 / residual channel independence 条件下才与完整多变量 KF 等价；真实跨指标噪声相关可能破坏这一假设。（Appendix A.2, p.14）
- **[评估边界] 校准协议**：global quantile 在 98%–99.5% 范围内按数据集选取；需在部署时确认 calibration 范围、异常占比假设与固定告警预算。（Appendix D.2）

### 开源与复现

论文提供 [COGNOS 代码](https://github.com/giansha/COGNOS)。复现建议锁定 MSE backbone、active-zone mask dilation、Haar / RBF 设置、训练-only calibration、逐通道 ARKS 参数、overlap buffer $k$、confidence 0.9 和 global-quantile threshold；分别报告 onset delay、点级 / Aff-F1、Range / VUS 覆盖及不同状态下的 false alarm。重点验证 GWNR-only 在 GECCO 的退化、固定 $R$ 对状态切换的响应，以及持续异常分数衰减。本次没有运行代码或训练。

## 9. 相关论文

- **KAN-AD**：同为 MSE residual / forecasting 背景，COGNOS 在其上作 residual engineering；KanAD-PSM range / VUS 下降说明组合收益仍需逐指标核查。
- **IGAD**：也是可插入既有重建器的训练 / 推理增强，但 IGAD 约束 fixed-point manifold、COGNOS 整形 residual 统计并后接滤波。
- **Fortifying Time Series**：认证输入时间变形鲁棒性；COGNOS 的噪声白化 + Kalman filtering 是随机 residual null-model 路线。
- **ScatterAD / TFC**：直接构造 latent 多视图结构；COGNOS 改 residual 统计假设，关注点不同。
- **Quo Vadis / TSB-AD**：帮助解释 PA-F1、Affinity 与 range / VUS 的差别；COGNOS 的 onset score 特别应做区间覆盖审查。
