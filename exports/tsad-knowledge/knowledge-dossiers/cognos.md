# Knowledge Dossier — COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing

## 1. Basic Information

- **English title**: COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing
- **中文译名**：COGNOS：通过受约束的高斯白噪声优化与平滑增强时间序列异常检测
- **Authors**: Wenlong Shang, Shihao Tian, Xutong Wan, Peng Chang
- **Venue / year / CCF**: ICML 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/giansha/COGNOS
- **Research area**: MSE 重建残差整形与统计平滑增强检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** MSE reconstruction-based TSAD：使正常 residual 近似 Gaussian white noise，再以 Kalman filter 分离噪声和结构异常。（§3–4）
- **[实验支持]** 七类 benchmark、九个 MSE-based backbone。（§5.1, Appendix D）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

作者把观测分解为可预测确定性动态、不可约随机噪声和稀疏结构异常：

$$X_t=f_\theta(X_{<t})+n_t+s_t. \tag{1}$$

正常时 $s_t=0$；重建器预测 $\hat X_t$ 后得到 $R_t=X_t-\hat X_t$。作者指出 MSE 只在 i.i.d. Gaussian noise 等假设下对应简单高斯似然；真实序列的 residual 常仍含自相关、非高斯重尾和正常状态噪声变化，使得 raw reconstruction error 形成高噪声底，难以以稳定的白噪声 null 假设设阈。（§1, §3, Fig. 1, pp.1–3）

COGNOS 把“正常 residual 近似 Gaussian white noise、异常是结构性偏离”作为明确归纳假设。它不是跨任意 TSAD 目标的通用插件：作者限制到使用 MSE reconstruction residual 的 backbone；例如只优化 association discrepancy 的 Anomaly Transformer 不产生其 ARKS 所需 residual。（§3, §6, p.9）

## 4. Core Challenges

#### 精读笔记原章节：4. 挑战与现有方法不足

1. MSE 降低平均 residual 能量，却不保证 residual 无时间相关或呈 Gaussian；模型还可能把异常尖峰拟合进去。（§3; Appendix A.1）
2. 传统 moving-average / low-pass 降噪会同时压低异常 onset 并引入延迟；固定过程噪声 Kalman filter 则在平滑和快速跟踪突变间折衷。（§4.2.2）
3. 恒定 / frozen sensor 区段不适合强加白噪声统计约束；transition 附近必须保留活动边界。（§4.1.1）
4. 噪声方差可能随 operating state 改变；用固定 $R$ 会在高信号期间误触发。（作者 limitations, p.9）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 纯换 backbone 仍保留“优化 MSE 但推理靠 residual statistical validity”的错配。（§1–3）
- **[适用边界]** 需要 MSE reconstruction residual；association discrepancy 模型不在原框架适用范围。（p.9）

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. 一句话总结

COGNOS 不另造检测 backbone，而把 MSE 重建器的正常残差通过 Gaussian-White-Noise Regularized (GWNR) loss 整形成近似高斯白噪声，再用每通道离线校准的 Adaptive Residual Kalman Smoother (ARKS) 平滑背景噪声、在 NIS 统计显著时快速跟踪结构突变；作者明确指出它偏向异常 onset 检测，可能无法覆盖完整异常区间。（§§3–4, Eqs. 1–16; Limitations, p.9）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：MSE 降低平均 residual 能量，却不保证 residual 无时间相关或呈 Gaussian；模型还可能把异常尖峰拟合进去。（§3; Appendix A.1）
- **C2（第4节挑战）**：传统 moving-average / low-pass 降噪会同时压低异常 onset 并引入延迟；固定过程噪声 Kalman filter 则在平滑和快速跟踪突变间折衷。（§4.2.2）
- **C3（第4节挑战）**：恒定 / frozen sensor 区段不适合强加白噪声统计约束；transition 附近必须保留活动边界。（§4.1.1）
- **C4（第4节挑战）**：噪声方差可能随 operating state 改变；用固定 $R$ 会在高信号期间误触发。（作者 limitations, p.9）

### 7.1 Activity mask

- **作者技术描述**：**[作者主张] Activity mask**：dilate $|X_t-X_{t-1}|$，对 active residual 施加辅助约束。（§4.1.1, Eq. 2）
- **对应挑战**：C4、C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 Activity-aware dynamic mask”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Spectral whitening

- **作者技术描述**：**[作者主张] Spectral whitening**：归一化 PSD 对 uniform 的 KL，提升谱熵。（§4.1.3, Eqs. 4–5）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Wavelet MMD

- **作者技术描述**：**[作者主张] Wavelet MMD**：Haar detail coefficients 经 instance standardization 后与 Gaussian MMD。（§4.1.4, Eqs. 6–7）
- **对应挑战**：C4、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 ARKS

- **作者技术描述**：**[作者主张] ARKS**：normal calibration 分 leakage tracking / noise suppression 两种模式；NIS 超阈后放大 $Q$ 并输出结构状态能量。（§4.2, Eqs. 10–16）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 ARKS：离线校准的每通道状态空间滤波”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** GWNR + ARKS 联合比单组件稳定；但 GWNR-only 的 GECCO Std-F1 .4738→.3440，ARKS-only 在 MSL 也略降。（Table 3）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. 总体架构

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

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：6.1 Activity-aware dynamic mask。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. 方法细节

#### 6.1 Activity-aware dynamic mask

用一阶绝对差 $\Delta_t=|X_t-X_{t-1}|$，通过形态学 dilation 构造 active mask：

$$M_t=\max_{k\in[-w,w]}\mathbf1(\Delta_{t+k}>\delta). \tag{2}$$

主要重建 MSE $L_{MSE}=\|R\|_F^2/N$ 作用于全体输入，避免 frozen zone 漂移；频域 / 统计正则仅作用于 $R_{active}=R\odot M$ 的有效片段。（§4.1.1–4.1.2, Eqs. 2–3, pp.3–4）

#### 6.2 GWNR：时间、频域、统计域 residual engineering

**时间域：全局能量。** $L_{MSE}=\|R\|_F^2/N$ 保留基础拟合精度（Eq. 3）。

**频域：谱白化。** 对 active residual 做 DFT 得 $Z(f)$ 与功率谱 $S(f)=|Z(f)|^2$，归一化为频率概率 $\tilde S$；定义与均匀分布 $U(f)=1/K$ 的 KL：

$$L_{Spec}=\sum_f\tilde S(f)\log\tilde S(f)+\log K. \tag{5}$$

最小化它等价于提高谱熵 / 频谱平坦度，目标是降低时间相关残留；并非直接对白化原始观测序列。（§4.1.3, Eqs. 4–5, p.4）

**统计域：Wavelet MMD。** 对 $R_{active}$ 做正交 Haar DWT，拆出低频 approximation $A$ 与高频 detail $D$（Eq. 6）。作者称只约束 $D$，以避免妨碍 backbone 拟合趋势；在时间维 instance standardization 后，使用 multi-scale RBF-kernel MMD 使 $\tilde D$ 接近标准 Gaussian（Eq. 7）。标准化旨在约束分布形状而非每个 channel 的物理方差。（§4.1.4, pp.4–5）

**梯度平衡。** 总目标为 $L_{total}=L_{MSE}+\sum_{k\in\{Spec,MMD\}}\alpha_kL_k$；用主损失梯度范数 $G_{main}$ 与辅助梯度 $G_k$ 自适应缩放：

$$\alpha_k=\operatorname{sg}\!\left(\frac{G_{main}}{G_k+\delta}\right)\mathbf1(L_k>\delta). \tag{8}$$

该机制避免在不同损失尺度下 GWNR 压过重建 fidelity。（§4.1.5, Eqs. 8–9, p.5）

#### 6.3 ARKS：离线校准的每通道状态空间滤波

每个 channel 的 residual $y_t$ 由线性 Gaussian SSM 表示：$x_t=Ax_{t-1}+w_t$，$y_t=Hx_t+v_t$，其中隐状态 $x_t$ 被解释为 anomaly signal；正常时期望 $x_t\approx0$（Eq. 10）。只用 normal calibration residual 的 lag autocovariances $\gamma_k$ 离线估计参数并分两种模式（Eq. 11）：

- **Leakage-Tracking mode**：若 $\gamma_1>\delta$ 且 $\gamma_2>\delta$，以 Yule-Walker 拟合 AR(1)，让滤波状态吸收 backbone 留下的可预测周期泄漏，避免当 anomaly 分数累加。
- **Noise-Suppression mode**：否则设 $A=1,R=\gamma_0,Q=\lambda R$ 且 $\lambda\ll1$，让 Kalman gain 较低、正常白噪声被压制。（§4.2.1, p.5）

#### 6.4 NIS Circuit Breaker 与异常分数

每步先预测 $\hat x_{t|t-1}=A\hat x_{t-1|t-1}$（Eq. 12），计算 normalized innovation squared：

$$\epsilon_t=\frac{(y_t-\hat x_{t|t-1})^2}{P_{t|t-1}+R}. \tag{13}$$

若 $\epsilon_t>\tau_\alpha$，在 $H_0$（Gaussian white residual）下视作统计显著结构突变，放大过程方差 $Q_t^*=\beta R$；否则沿用 $Q_{base}$（Eqs. 14–15）。随后更新 Kalman gain 和后验 $\hat x_{t|t}$（Eq. 16）。最终分数为结构状态能量 $S_t=\|\hat x_{t|t}\|^2$（§4.2.2–4.2.3, pp.5–6）。

作者还对 backbone 重叠窗口的 residual 进行固定 buffer aggregation：等一个时间点由其覆盖的 $w$ 个窗口预测均值完成后再进 ARKS；实验取 $k=w-1$，稳定优先，较小 $k$ 可降延迟但数值稳定性下降。（Appendix, Algorithm 1, pp.16–17）

#### 6.5 “Onset”与“duration”之间的设计取舍

Circuit Breaker 对首次显著创新快速提高 gain，便于捕获异常开始时刻；若随后序列停留在新稳态，innovation 会减小，滤波后验异常分数衰减。作者指出该机制抑制持续报警疲劳，但会损害奖励完整时间覆盖的 range metrics；需要按告警目标决定更偏 onset 还是 interval coverage。（§5.2, p.7; Limitations, p.9）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (2)、Eq. (3)、Eq. (4)、Eq. (6)、Eq. (7)、Eq. (8)、Eq. (10)、Eq. (11)、Eq. (12)、Eq. (14)、Eq. (16)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.4 NIS Circuit Breaker 与异常分数及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

COGNOS 不另造检测 backbone，而把 MSE 重建器的正常残差通过 Gaussian-White-Noise Regularized (GWNR) loss 整形成近似高斯白噪声，再用每通道离线校准的 Adaptive Residual Kalman Smoother (ARKS) 平滑背景噪声、在 NIS 统计显著时快速跟踪结构突变；作者明确指出它偏向异常 onset 检测，可能无法覆盖完整异常区间。（§§3–4, Eqs. 1–16; Limitations, p.9）

## 9. Experimental Evidence

#### 精读笔记原章节：7. 实验设计与证据

#### 7.1 数据、backbone、指标和阈值

7 类真实数据：MSL、SMAP、SWaT、PSM、GECCO、SWAN、UCR。9 个 backbone 覆盖 CrossAD、KAN-AD、LSTM-AE、ModernTCN、TimesNet、TimeMixer++、Autoformer、DLinear、MICN。评价包含 Standard F1（点调整）、Aff-F1、Range-AUC-ROC / PR、VUS-ROC / PR；UCR 报 250 subsets 平均（§5.1; Appendix D.1, pp.6, 22）。

ARKS confidence level $1-\alpha=0.90$ 在所有数据集统一，calibration 使用仅含正常序列的 training split。分数二值化使用每个数据集统一 global quantile percentile，在 98%–99.5% 的约束区间选取，并对各模型共享，不做 per-model exhaustive F1-max 或动态阈值（Appendix D.2, pp.19, 22–24）。百分位具体选择依据仍应在复现报告中说清楚。

#### 7.2 主结果与不一致指标

- **[实验支持]** 例如 KAN-AD backbone 在 MSL 上 Standard-F1 .8115→.9165、Aff-F1 .5360→.9157；TimesNet 在 SWAN Standard-F1 .7371→.8313、Aff-F1 .1961→.5249。结果支持 COGNOS 在若干架构 / 数据上的显著改善。（Table 1, pp.6–7）
- **[证据边界]** 不是每个 backbone × metric 都提高：KAN-AD 在 PSM 上 Std-F1 .8946→.9744、Aff-F1 .6223→.8628 上升，但 Range-AUC-ROC .7005→.6799、VUS-ROC .6846→.6624、VUS-PR .4724→.4432 下降；GECCO 上 Autoformer 某些 range / VUS-PR 指标也退化。（Table 1; Appendix Table 7）
- **[作者结论]** 作者称跨架构总体稳定增益，并把优势归于 GWNR 与 ARKS 协同；平均 / selected metrics 不应抹去上面的下降和 onset-vs-coverage 取舍。（§5.2; Table 1）

#### 7.3 消融、诊断和开销

- **[消融支持]** KAN-AD backbone 消融中，不带 GWNR 的 ARKS 单独在 PSM Standard-F1 .8946→.9433，但在 MSL .8115→.8083 略降；说明 filter 作用依赖 residual 条件。（Table 3, p.7）
- **[消融反例]** GECCO 上 GWNR 单独把 Standard-F1 从 .4738 降至 .3440；整套 GWNR+ARKS 才到 .7466。残差白化可能降低原始 residual 分数可分性，必须与 score extractor 联合验证。（Table 3）
- **[机制诊断]** SWaT / PSM / SMAP residual ACF 与 QQ plot 显示 GWNR 后自相关下降、Gaussian QQ 对齐改善；这些图仅是选定序列的分布诊断。（Figs. 3, 5–7, pp.7–8; Appendix C）
- **[效率]** 框架训练需多项 loss 和反向梯度范数，ARKS 还有逐点递归和重叠窗口 buffer；附录以 RTX 4090 / EPYC 测试，实际开销依 backbone。（Table 4, Appendix D.4）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[作者指出] 固定噪声方差**：校准 $R$ 假设噪声地板跨状态稳定；状态相关 heteroscedastic noise 可能误报，作者计划自适应 $R$。（Limitations, p.9）

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[作者指出] 目标适用范围**：针对 MSE reconstruction residual；不直接适用于没有这种 residual 的 association / contrastive detector。（Limitations, p.9）

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[作者指出] onset bias**：擅长异常 onset，未必覆盖长异常区间；需要按业务告警任务调整 circuit-breaker confidence。（§6, p.9）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[分析推断] 白噪声假设**：合法负载状态切换也可能产生显著 NIS；方法没有 workload / release / Trace 判断来源，可能触发告警或在持续新状态中迅速衰减。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[理论边界] 通道独立性**：ARKS channel-wise factorization 在 covariance 对角 / residual channel independence 条件下才与完整多变量 KF 等价；真实跨指标噪声相关可能破坏这一假设。（Appendix A.2, p.14）

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

**[评估边界] 校准协议**：global quantile 在 98%–99.5% 范围内按数据集选取；需在部署时确认 calibration 范围、异常占比假设与固定告警预算。（Appendix D.2）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 以 workload / release context 做 state-conditioned $R$ 和 circuit breaker；测状态切换误报与未知故障召回。
- **[分析推断]** 比较 onset delay、duration coverage、fixed-FPR 与 range/VUS 指标，明确报警目标。
- **[分析推断]** 在跨通道相关 residual 与 heteroscedastic noise 下设计 covariance-aware ARKS。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **KAN-AD**：同为 MSE residual / forecasting 背景，COGNOS 在其上作 residual engineering；KanAD-PSM range / VUS 下降说明组合收益仍需逐指标核查。
- **IGAD**：也是可插入既有重建器的训练 / 推理增强，但 IGAD 约束 fixed-point manifold、COGNOS 整形 residual 统计并后接滤波。
- **Fortifying Time Series**：认证输入时间变形鲁棒性；COGNOS 的噪声白化 + Kalman filtering 是随机 residual null-model 路线。
- **ScatterAD / TFC**：直接构造 latent 多视图结构；COGNOS 改 residual 统计假设，关注点不同。
- **Quo Vadis / TSB-AD**：帮助解释 PA-F1、Affinity 与 range / VUS 的差别；COGNOS 的 onset score 特别应做区间覆盖审查。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §1, §3, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §3, §6 | 精读笔记保留的原文定位 |
| Research problem / scenario | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §3–4 | 精读笔记保留的原文定位 |
| Research problem / scenario | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §5.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.2.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.1.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §1–3 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.1.1–4.1.2, Eqs. 2–3 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Eq. 3 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.1.3, Eqs. 4–5 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.1.4, Eq. 6, Eq. 7 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.1.5, Eqs. 8–9 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Eq. 10, Eq. 11 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.2.1 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Eq. 12 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §4.2.2–4.2.3, Eqs. 14–15, Eq. 16 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §5.2 | 精读笔记保留的原文定位 |
| Experimental evidence | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §5.1 | 精读笔记保留的原文定位 |
| Experimental evidence | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Table 1, Table 7 | 精读笔记保留的原文定位 |
| Experimental evidence | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | §5.2, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf | Table 3 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "cognos",
  "title_en": "COGNOS: Universal Enhancement for Time Series Anomaly Detection via Constrained Gaussian-Noise Optimization and Smoothing",
  "title_zh": "COGNOS：通过受约束的高斯白噪声优化与平滑增强时间序列异常检测",
  "authors": [
    "Wenlong Shang",
    "Shihao Tian",
    "Xutong Wan",
    "Peng Chang"
  ],
  "year": 2026,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ICML/COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
  "reading_note_path": "papers/cognos/notes.md",
  "code_url": "https://github.com/giansha/COGNOS",
  "research_area": "MSE 重建残差整形与统计平滑增强检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] MSE reconstruction-based TSAD：使正常 residual 近似 Gaussian white noise，再以 Kalman filter 分离噪声和结构异常。（§3–4） - [实验支持] 七类 benchmark、九个 MSE-based backbone。（§5.1, Appendix D）",
  "research_problem": "作者把观测分解为可预测确定性动态、不可约随机噪声和稀疏结构异常： $$Xt=f\\theta(X{<t})+nt+st. \\tag{1}$$ 正常时 $st=0$；重建器预测 $\\hat Xt$ 后得到 $Rt=Xt-\\hat Xt$。作者指出 MSE 只在 i.i.d. Gaussian noise 等假设下对应简单高斯似然；真实序列的 residual 常仍含自相关、非高斯重尾和正常状态噪声变化，使得 raw reconstruction error 形成高噪声底，难以以稳定的白噪声 null 假设设阈。（§1, §3, Fig. 1, pp.1–3） COGNOS 把“正常 residual 近似 Gaussian white noise、异常是结构性偏离”作为明确归纳假设。它不是跨任意 TSAD 目标的通用插件：作者限制到使用 MSE reconstruction residual 的 backbone；例如只优化 association discrepancy 的 Anomaly Transformer 不产生其 ARKS 所需 residual。（§3, §6, p.9）",
  "core_challenges": [
    "MSE 降低平均 residual 能量，却不保证 residual 无时间相关或呈 Gaussian；模型还可能把异常尖峰拟合进去。（§3; Appendix A.1）",
    "传统 moving-average / low-pass 降噪会同时压低异常 onset 并引入延迟；固定过程噪声 Kalman filter 则在平滑和快速跟踪突变间折衷。（§4.2.2）",
    "恒定 / frozen sensor 区段不适合强加白噪声统计约束；transition 附近必须保留活动边界。（§4.1.1）",
    "噪声方差可能随 operating state 改变；用固定 $R$ 会在高信号期间误触发。（作者 limitations, p.9）"
  ],
  "existing_method_limits": [
    "[作者主张] 纯换 backbone 仍保留“优化 MSE 但推理靠 residual statistical validity”的错配。（§1–3）",
    "[适用边界] 需要 MSE reconstruction residual；association discrepancy 模型不在原框架适用范围。（p.9）"
  ],
  "core_idea": "COGNOS 不另造检测 backbone，而把 MSE 重建器的正常残差通过 Gaussian-White-Noise Regularized (GWNR) loss 整形成近似高斯白噪声，再用每通道离线校准的 Adaptive Residual Kalman Smoother (ARKS) 平滑背景噪声、在 NIS 统计显著时快速跟踪结构突变；作者明确指出它偏向异常 onset 检测，可能无法覆盖完整异常区间。（§§3–4, Eqs. 1–16; Limitations, p.9）",
  "technical_innovations": [
    {
      "name": "Activity mask",
      "author_claim": "**[作者主张] Activity mask**：dilate $|X_t-X_{t-1}|$，对 active residual 施加辅助约束。（§4.1.1, Eq. 2）",
      "challenge_ids": [
        "C4",
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 Activity-aware dynamic mask",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Activity mask**：dilate $|X_t-X_{t-1}|$，对 active residual 施加辅助约束。（§4.1.1, Eq. 2）"
    },
    {
      "name": "Spectral whitening",
      "author_claim": "**[作者主张] Spectral whitening**：归一化 PSD 对 uniform 的 KL，提升谱熵。（§4.1.3, Eqs. 4–5）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Spectral whitening**：归一化 PSD 对 uniform 的 KL，提升谱熵。（§4.1.3, Eqs. 4–5）"
    },
    {
      "name": "Wavelet MMD",
      "author_claim": "**[作者主张] Wavelet MMD**：Haar detail coefficients 经 instance standardization 后与 Gaussian MMD。（§4.1.4, Eqs. 6–7）",
      "challenge_ids": [
        "C4",
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
      "source_locator": "**[作者主张] Wavelet MMD**：Haar detail coefficients 经 instance standardization 后与 Gaussian MMD。（§4.1.4, Eqs. 6–7）"
    },
    {
      "name": "ARKS",
      "author_claim": "**[作者主张] ARKS**：normal calibration 分 leakage tracking / noise suppression 两种模式；NIS 超阈后放大 $Q$ 并输出结构状态能量。（§4.2, Eqs. 10–16）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 ARKS：离线校准的每通道状态空间滤波",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** GWNR + ARKS 联合比单组件稳定；但 GWNR-only 的 GECCO Std-F1 .4738→.3440，ARKS-only 在 MSL 也略降。（Table 3）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] ARKS**：normal calibration 分 leakage tracking / noise suppression 两种模式；NIS 超阈后放大 $Q$ 并输出结构状态能量。（§4.2, Eqs. 10–16）"
    }
  ],
  "methodology": {
    "architecture": "text 任意 MSE reconstruction backbone Training / GWNR ├─ 全序列 MSE：残差总能量最小 ├─ active mask：只在有效动态残差约束统计属性 ├─ PSD → uniform：降低残差频谱集中度 / 时间相关 ├─ Haar DWT detail → Gaussian MMD：整形高频残差分布 └─ gradient balancing：避免正则淹没重建任务 Inference / ARKS (per channel) ├─ normal calibration residuals → AR(1) leakage tracking 或 random-walk noise suppression ├─ sliding overlapping predictions → buffer aggregation ├─ NIS χ² test → circuit breaker 动态放大 Q └─ Kalman posterior structural signal energy → anomaly score",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 Activity-aware dynamic mask",
      "6.2 GWNR：时间、频域、统计域 residual engineering",
      "6.3 ARKS：离线校准的每通道状态空间滤波",
      "6.4 NIS Circuit Breaker 与异常分数",
      "6.5 “Onset”与“duration”之间的设计取舍"
    ],
    "key_formulas": [
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)",
      "Eq. (10)",
      "Eq. (11)",
      "Eq. (12)",
      "Eq. (14)",
      "Eq. (16)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "COGNOS 不另造检测 backbone，而把 MSE 重建器的正常残差通过 Gaussian-White-Noise Regularized (GWNR) loss 整形成近似高斯白噪声，再用每通道离线校准的 Adaptive Residual Kalman Smoother (ARKS) 平滑背景噪声、在 NIS 统计显著时快速跟踪结构突变；作者明确指出它偏向异常 onset 检测，可能无法覆盖完整异常区间。（§§3–4, Eqs. 1–16; Limitations, p.9）"
  },
  "experimental_evidence": {
    "datasets": [
      "ARKS confidence level $1-\\alpha=0.90$ 在所有数据集统一，calibration 使用仅含正常序列的 training split。分数二值化使用每个数据集统一 global quantile percentile，在 98%–99.5% 的约束区间选取，并对各模型共享，不做 per-model exhaustive F1-max 或动态阈值（Appendix D.2, pp.19, 22–24）。百分位具体选择依据仍应在复现报告中说清楚。"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 7.1 数据、backbone、指标和阈值",
      "7 类真实数据：MSL、SMAP、SWaT、PSM、GECCO、SWAN、UCR。9 个 backbone 覆盖 CrossAD、KAN-AD、LSTM-AE、ModernTCN、TimesNet、TimeMixer++、Autoformer、DLinear、MICN。评价包含 Standard F1（点调整）、Aff-F1、Range-AUC-ROC / PR、VUS-ROC / PR；UCR 报 250 subsets 平均（§5.1; Appendix D.1, pp.6, 22）。",
      "ARKS confidence level $1-\\alpha=0.90$ 在所有数据集统一，calibration 使用仅含正常序列的 training split。分数二值化使用每个数据集统一 global quantile percentile，在 98%–99.5% 的约束区间选取，并对各模型共享，不做 per-model exhaustive F1-max 或动态阈值（Appendix D.2, pp.19, 22–24）。百分位具体选择依据仍应在复现报告中说清楚。",
      "### 7.2 主结果与不一致指标"
    ],
    "main_results": [
      "### 7.2 主结果与不一致指标",
      "- [实验支持] 例如 KAN-AD backbone 在 MSL 上 Standard-F1 .8115→.9165、Aff-F1 .5360→.9157；TimesNet 在 SWAN Standard-F1 .7371→.8313、Aff-F1 .1961→.5249。结果支持 COGNOS 在若干架构 / 数据上的显著改善。（Table 1, pp.6–7） - [证据边界] 不是每个 backbone × metric 都提高：KAN-AD 在 PSM 上 Std-F1 .8946→.9744、Aff-F1 .6223→.8628 上升，但 Range-AUC-ROC .7005→.6799、VUS-ROC .6846→.6624、VUS-PR .4724→.4432 下降；…",
      "- [消融支持] KAN-AD backbone 消融中，不带 GWNR 的 ARKS 单独在 PSM Standard-F1 .8946→.9433，但在 MSL .8115→.8083 略降；说明 filter 作用依赖 residual 条件。（Table 3, p.7） - [消融反例] GECCO 上 GWNR 单独把 Standard-F1 从 .4738 降至 .3440；整套 GWNR+ARKS 才到 .7466。残差白化可能降低原始 residual 分数可分性，必须与 score extractor 联合验证。（Table 3） - [机制诊断] SWaT / PSM / SMAP residual ACF 与 QQ plot 显示 GWNR 后自相关下降、Gaussian QQ 对齐改善；…"
    ],
    "ablations": [
      "### 7.3 消融、诊断和开销",
      "- [消融支持] KAN-AD backbone 消融中，不带 GWNR 的 ARKS 单独在 PSM Standard-F1 .8946→.9433，但在 MSL .8115→.8083 略降；说明 filter 作用依赖 residual 条件。（Table 3, p.7） - [消融反例] GECCO 上 GWNR 单独把 Standard-F1 从 .4738 降至 .3440；整套 GWNR+ARKS 才到 .7466。残差白化可能降低原始 residual 分数可分性，必须与 score extractor 联合验证。…"
    ],
    "robustness_generalization": [
      "- [消融支持] KAN-AD backbone 消融中，不带 GWNR 的 ARKS 单独在 PSM Standard-F1 .8946→.9433，但在 MSL .8115→.8083 略降；说明 filter 作用依赖 residual 条件。（Table 3, p.7） - [消融反例] GECCO 上 GWNR 单独把 Standard-F1 从 .4738 降至 .3440；整套 GWNR+ARKS 才到 .7466。残差白化可能降低原始 residual 分数可分性，必须与 score extractor 联合验证。…"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "[作者指出] 固定噪声方差：校准 $R$ 假设噪声地板跨状态稳定；状态相关 heteroscedastic noise 可能误报，作者计划自适应 $R$。（Limitations, p.9）",
      "[作者指出] 目标适用范围：针对 MSE reconstruction residual；不直接适用于没有这种 residual 的 association / contrastive detector。（Limitations, p.9）",
      "[作者指出] onset bias：擅长异常 onset，未必覆盖长异常区间；需要按业务告警任务调整 circuit-breaker confidence。（§6, p.9）"
    ],
    "reasoned_inference": [
      "[分析推断] 白噪声假设：合法负载状态切换也可能产生显著 NIS；方法没有 workload / release / Trace 判断来源，可能触发告警或在持续新状态中迅速衰减。"
    ],
    "evidence_gaps": [
      "[理论边界] 通道独立性：ARKS channel-wise factorization 在 covariance 对角 / residual channel independence 条件下才与完整多变量 KF 等价；真实跨指标噪声相关可能破坏这一假设。（Appendix A.2, p.14）",
      "[评估边界] 校准协议：global quantile 在 98%–99.5% 范围内按数据集选取；需在部署时确认 calibration 范围、异常占比假设与固定告警预算。（Appendix D.2）"
    ]
  },
  "research_implications": [
    "- [分析推断] 以 workload / release context 做 state-conditioned $R$ 和 circuit breaker；测状态切换误报与未知故障召回。 - [分析推断] 比较 onset delay、duration coverage、fixed-FPR 与 range/VUS 指标，明确报警目标。 - [分析推断] 在跨通道相关 residual 与 heteroscedastic noise 下设计 covariance-aware ARKS。"
  ],
  "related_papers": [
    {
      "paper_id": "cognos",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "idempotent-reconstruction",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "kan-ad",
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
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§1, §3, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§3, §6",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§3–4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§5.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§4.2.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§4.1.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§4.1.1–4.1.2, Eqs. 2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "Eq. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§4.1.3, Eqs. 4–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "COGNOS_Universal_Enhancement_for_Time_Series_Anomaly_Detection_via_Constrained_Gaussian_Noise_Optimizatio.pdf",
      "locator": "§4.1.4, Eq. 6, Eq. 7",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "4e2487fc67be092cd3d5c768caba45e8fd4b3bc5ae8a99b20c75a0b2a61abbe6",
    "reading_note_sha256": "7b8d36830e72e6cee77285abbc508895e017a823e74bfdc4a3ccaabd63e579b6",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "7e98f1135765c49de6c372b12dc0afba7fc352b0c589fc527dff58d51e354a96"
  },
  "knowledge_card_path": "papers/cognos/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
