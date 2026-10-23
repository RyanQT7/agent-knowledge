# 知识卡片：COGNOS

**论文**：*COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing* (ICML 2026)。标签区分**作者主张 / 实验支持 / 分析推断**。页码对应 PDF。

## 1. Research Scenario

- **[作者主张]** MSE reconstruction-based TSAD：使正常 residual 近似 Gaussian white noise，再以 Kalman filter 分离噪声和结构异常。（§3–4）
- **[实验支持]** 七类 benchmark、九个 MSE-based backbone。（§5.1, Appendix D）

## 2. Core Challenges

- **[作者主张]** MSE 降低 residual energy，但不保证 residual 无自相关 / Gaussian；原始异常分数因此噪声大。（§3, Fig. 1）
- **[作者指出]** fixed observation-noise $R$ 不适用于 state-dependent heteroscedasticity；Circuit Breaker 偏 onset、不保证区间覆盖。（Limitations, p.9）

## 3. Existing Limitations

- **[作者主张]** 纯换 backbone 仍保留“优化 MSE 但推理靠 residual statistical validity”的错配。（§1–3）
- **[适用边界]** 需要 MSE reconstruction residual；association discrepancy 模型不在原框架适用范围。（p.9）

## 4. Core Idea

- **[作者主张]** 训练时用 GWNR 对 residual 加谱平坦与 Gaussian 形状约束；推理用 NIS chi-square 检验切换 Kalman gain。（§4）

## 5. Technical Innovations

1. **[作者主张] Activity mask**：dilate $|X_t-X_{t-1}|$，对 active residual 施加辅助约束。（§4.1.1, Eq. 2）
2. **[作者主张] Spectral whitening**：归一化 PSD 对 uniform 的 KL，提升谱熵。（§4.1.3, Eqs. 4–5）
3. **[作者主张] Wavelet MMD**：Haar detail coefficients 经 instance standardization 后与 Gaussian MMD。（§4.1.4, Eqs. 6–7）
4. **[作者主张] ARKS**：normal calibration 分 leakage tracking / noise suppression 两种模式；NIS 超阈后放大 $Q$ 并输出结构状态能量。（§4.2, Eqs. 10–16）

## 6. Key Mechanisms

- **[原文]** $X_t=f_\theta(X_{<t})+n_t+s_t$；$S_t=\|\hat x_{t|t}\|^2$。（Eqs. 1, 16）
- **[作者主张]** normal white-noise 下 NIS 遵循 $\chi^2_1$；触发 circuit breaker 后更快跟踪新突变。（§4.2.2）
- **[分析推断]** 任何合法但未建模的 state transition 也可能有高 NIS；状态语义未参与过滤。

## 7. Experimental Evidence

- **[实验支持]** KAN-AD / MSL Std-F1 .8115→.9165、Aff-F1 .5360→.9157；TimesNet / SWAN Std-F1 .7371→.8313、Aff-F1 .1961→.5249。（Table 1）
- **[实验支持]** GWNR + ARKS 联合比单组件稳定；但 GWNR-only 的 GECCO Std-F1 .4738→.3440，ARKS-only 在 MSL 也略降。（Table 3）
- **[反例]** KAN-AD / PSM 的 Std-F1、Aff-F1 上升但 R-A-R、VUS-ROC、VUS-PR 下降，显示 onset 与 range coverage 的取舍。（Table 1）
- **[协议]** 每数据集 shared quantile threshold 98%–99.5%，不做 per-model test best F1；ARKS calibration 用 normal training set。（Appendix D.2）

## 8. Limitations

- **[作者指出]** fixed $R$、MSE reconstruction 适用范围、onset-vs-coverage trade-off。（Limitations, p.9）
- **[理论边界]** channel-wise ARKS 与完整多变量 KF 等价需 residual covariance diagonal / channel independence。（Appendix A.2）
- **[分析推断]** Gaussian white residual、stationary noise null、独立 channel 假设可能被多状态和同步故障打破。

## 9. Research Opportunities

- **[分析推断]** 以 workload / release context 做 state-conditioned $R$ 和 circuit breaker；测状态切换误报与未知故障召回。
- **[分析推断]** 比较 onset delay、duration coverage、fixed-FPR 与 range/VUS 指标，明确报警目标。
- **[分析推断]** 在跨通道相关 residual 与 heteroscedastic noise 下设计 covariance-aware ARKS。

## 10. Related Papers

- [完整精读笔记](notes.md) · [原始 PDF](../../sources/papers/tsad-2024-2026/2026/ICML/COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf)
- **KAN-AD**：可作 backbone；**IGAD**：manifold regularization；**Fortifying Time Series**：输入变形证据；**Quo Vadis / TSB-AD**：阈值与区间指标。
