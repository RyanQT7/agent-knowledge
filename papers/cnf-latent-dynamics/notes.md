# Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows

## 1. Metadata

- **Authors**: David Baumgartner, Eliezer de Souza da Silva, Iñigo Urteaga
- **Year / venue**: 2026 / UAI (CCF B，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2026/UAI/Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf)
- **Proceedings**: PMLR 337, pp. 448–468
- **Code and models**: [probML anomaly detection repository](https://github.com/iurteagalab/probML_anomaly_detection)
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

论文将条件 normalizing flow (CNF) 从过去观测映射到潜变量，并在潜空间显式规定随时间演化的概率动力学；训练后先检查白化潜变量是否符合该分布，再用 multivariate Kolmogorov–Smirnov (MV-KS) goodness-of-fit (GOF) 检验判定一段序列是否偏离预设 latent dynamics。其关键点是“检验动态合规性”而非直接把 observation-space likelihood 当异常分数。（§§3.1–3.2, Eqs. 1–12, PDF pp. 3–5）

## 3. 背景与问题定义

无监督 generative AD 常用负对数似然 (NLL) 表示异常程度，但 likelihood 衡量的是模型赋予观测的密度，不保证数据的 temporal typicality。高维数据中，OOD 样本可能落在高 likelihood 区域，因而仅以 NLL 排序并不等价于检验是否符合正常时序动力学。（§1, PDF pp. 1–2）

作者提出：若无异常标签，模型需要显式定义何谓 expected behavior。该文把定义放在 latent space 中：训练数据映射后的 latent trajectory 应服从预先指定的时间演化分布；测试窗口若不符合此假设，则作为 anomaly。论文以简单可解释的线性 Gaussian latent dynamical model (LG-LDM) 实例化一般动力学，但框架允许依应用选择其它 inductive bias。（§3, PDF pp. 3–4）

## 4. 总体架构

```text
历史上下文 W_t = x_(t-k:t-1) + 当前观测 x_t
       ↓ conditional normalizing flow F(x_t | W_t; θ)
潜表示 z_t，与 prescribed latent dynamics 预测的 μ_t / Σ_t 对照
       ↓ whitening: z~_t = Σ_t^(-1/2)(z_t − μ_t)
训练诊断：训练 latent trajectory 的 MV-KS GOF → FIT
测试检测：长度 w 的测试窗口 MV-KS statistic s_w 与样本数相关临界值 τ_w 比较
       ↓ s_w ≥ τ_w 则拒绝 prescribed dynamics compliance
```

## 5. 方法细节

### 5.1 条件 flow 与 latent dynamics

每个 $D$ 维观测 $x_t$ 经条件流，根据过去 $k$ 步上下文 $W_t=x_{t-k:t-1}$ 映射为同维潜变量：

$$z_t=F(x_t\mid W_t;\theta)\sim\mathcal N(\mu_t,\Sigma_t). \tag{1}$$

预期状态的均值由一般确定性映射递推：

$$\mu_0\sim p(\phi_0),\qquad \mu_t=\psi(\mu_{t-1};\phi). \tag{2–3}$$

实验使用 LG-LDM：$\mu_0\sim\mathcal N(0,I)$、$\mu_t=A\mu_{t-1}+b$、$\Sigma_t=I$（Eqs. 4–5）。若 $\rho(A)<1$，其均值轨迹趋向固定点；$b=0$ 时固定点为原点。这里是 latent 参照模型，不是论文证明真实业务系统本身线性、Gaussian 或处于单一 operational state。

定义白化 latent：

$$\tilde z_t=\Sigma_t^{-1/2}(z_t-\mu_t).$$

当模型拟合良好且样本服从指定 dynamics 时，$\tilde z_t$ 应为 independent standard Gaussian。（§3.1, PDF pp. 3–4）

### 5.2 用条件似然联合训练 CNF 和状态动力学

作者联合优化 flow 参数 $\theta$ 与 latent dynamics 参数 $\phi$ 的 NLL。完整序列版本将各时点的动态 Gaussian likelihood 与所有 flow layer 的 Jacobian determinant 累加（Eq. 7）：

$$\mathcal L_{seq}=-\frac1T\sum_{t=1}^T\left[\log p_t(F(x_t\mid W_t))+\sum_{l=1}^L\log|\det J_{F_l}(x_{t,l}\mid W_t)|\right],$$

其中 $p_t=\mathcal N(\mu_t,\Sigma_t)$，且 $\mu_t$ 按 $\psi$ 递推。（Eqs. 7–9）实现使用 RealNVP 变体。因完整序列优化的依赖随 $T$ 增长，作者另给 Markovian dynamics 下的 subsequence mini-batch 版本（Eqs. 10–11）：每个 batch 使用上下文 $W_b$，并将前一 batch 最后一个 $\mu$ 作为下一 batch 初值。二者在 batch size 等于序列长度时一致。（§3.1.2, PDF p. 4）

### 5.3 Compliance GOF：训练诊断 FIT 与测试异常检测

训练阶段计算全训练 whitened latent trajectory 相对完全指定 $\mathcal N(0,I)$ 的 MV-KS 统计量 $s_T$，用随样本数变化的临界值 $\tau_T$ 定义：

$$FIT=\mathbf1[s_T\le\tau_T].$$

FIT 表示训练 latent trajectory 是否符合规定的 inductive bias；作者强调这只是模型拟合/统计合规性诊断，不代表 anomaly detection 性能本身。（§3.2, Fig. 3, PDF pp. 4, 7）

测试时，在长度为 $w$ 的 latent sequence 上计算 MV-KS 统计量 $s_w$，若 $s_w\ge\tau_w$ 就拒绝“这些样本来自规定 latent 分布”的原假设，判定 unexpected behavior（Eq. 12）。$\tau_w$ 由 MV-KS 检验的样本数相关临界值给出，所以作者称其为 label-free / 无需手调 anomaly threshold 的规则。这个性质以测试窗口样本满足 GOF 检验所要求条件、训练模型已通过 FIT、且 inductive bias 合适为前提；不是脱离假设的无校准承诺。（§3.2）

### 5.4 关键选择：窗口、latent dimension 与 inductive bias

MV-KS 的 statistical power 取决于样本数与 latent dimension。synthetic experiment 中 $w\le20$ 过噪，$w\ge200$ 会把异常平均 / 稀释；四维例子 $w=64$ 较好。作者据此建议窗口尺度至少为 $O(D^3)$，也讨论在可因子化假设下做低维 subspace GOF 来降低样本成本，但这引入 multiple-testing 等局限。（§4.2, Table 2, Discussion, PDF pp. 6, 8）

## 6. 实验与证据

### 6.1 实验设计

- **合成序列**：四维序列中注入 amplitude、frequency 和 observation-noise 变化，比较 NLL 与 latent GOF / MV-KS。（§4.2, Figs. 1–2）
- **真实序列**：TSB-AD 的 univariate、multivariate 子集和 1080 条 benchmark 序列 aggregate leaderboard。基线按 TSB-AD 排名选取；Optuna TPE 对 real-data 每个配置 20 warm-up + 100 trials。详细逐序列对比可用指标主要为 VUS-PR；论文另报告 oracle-thresholded metrics，但这些不属于无监督 test-time 阈值。（§4.1, Tables 1, 3–5）
- **模型**：CNF 用 RealNVP 变体；搜索 context 5–500、flow layers 3–40、hidden layers 1–20、hidden size 4–200，说明 model capacity 和 context 是重要变量。（Table 1）

### 6.2 合成实验：高 likelihood 不等于正常

- **[实验支持]** Fig. 1 中 NLL 可找到约 $t\approx200$ 的 frequency alteration，却漏掉被 CNF 映射至高密度区的 amplitude changes（约 $t\approx500,800$）；MV-KS 能检出三段。（Fig. 1, PDF p. 6）
- **[实验支持]** 对 $w=64$，MV-KS 的 AUC-PR 82.1、VUS-PR 96.0、Affiliation F1 92.6；NLL 对应 78.8、92.8、85.0。指标表以百分数显示。（Table 2, Fig. 1）
- **[实验支持]** 窗口过短统计波动大、过长稀释异常；例如 $w=200$ 时 AUC-PR 58.3，VUS-PR 90.4，Aff-F 等指标也较差。（Table 2）
- **[解释边界]** 图中 latent scatter / whitened trajectory 使偏离更可见；这是对模型指定统计假设的检查，不是对业务根因的解释。

### 6.3 真实数据：合规性诊断限制了 GOF 规则的适用范围

- **[实验支持]** 1080 条 TSB-AD leaderboard aggregate 中 NLL 排名为 UTS 第 7，KS 第 17；MTS 报告值也显示 NLL 优于 KS。故论文不是声称 KS 在真实数据全面优于 NLL。（§4.2, Table 5, PDF p. 8）
- **[实验支持]** 当训练满足 latent dynamics，例如 NEK 序列 FIT 88%、Stock 100%，NLL 的 mean VUS-PR 约 54、KS 约 44，表现具竞争力；MITDB 不满足合规时，FIT 约 18%（不同表列为相应 subset 的 FIT），两类 scoring 均退化。（§4.2, Tables 3–5）
- **[作者解释]** NLL 在真实 point/spike anomalies 往往更好，KS 在 synthetic structural / frequency / amplitude / regime changes 更有优势。作者把方法定位为无监督时使用合规统计检验，而不是取代所有 likelihood detector。（§5, PDF p. 8）

### 6.4 训练 compliance 对部署的意义

Figure 3 展示 CNF capacity 过大或 context 不匹配时，训练 latent trajectory 的 KS statistic 会显著升高；此时自动 KS 临界值不能被信任。FIT 用于识别这种情况。论文明确指出 FIT 衡量 statistical validity，不是 AD quality。（§4.2, Fig. 3, PDF p. 7）

## 7. 贡献、作者局限、分析与复现

### 贡献

1. 将异常定义为 latent temporal dynamics 不合规，而不等同于低 observation-space likelihood。（§3）
2. 将条件 flow 与显式 state-space latent dynamics 联合训练，并以 MV-KS GOF 形成 threshold-free statistical decision rule。（§3.1–3.2）
3. 提供训练阶段 FIT compliance diagnostic，暴露 inductive bias / 模型容量不适配时不宜信任测试阈值。（Fig. 3; §5）

### 作者明确讨论的限制

- Highly flat / erratic sequences 对 CNF calibration 仍困难。（§5, PDF p. 8）
- GOF 效能受 statistic、sample size 和高维 curse 影响；窗口太长会平滑孤立 point anomalies，作者建议约 $O(D^3)$ 窗口，或考虑 subspace testing。（§5）
- 方法对 model capacity、dataset behavior 敏感，需要充分超参搜索；预处理和 inductive bias 应有领域知识支持，LG-LDM 不适合所有数据集。（§5）
- KS 在真实数据并非总能超过 NLL；MITDB 例子中 prescribed dynamics 无法拟合，方法按 FIT 预期退化。（§4.2）

### 分析推断

- latent dynamics 检验能区分“符合某个预设模型”与“偏离该模型”，但**不能仅凭该检验区分合法新 workload、release transition 和真实故障**；若多种正常状态无法由同一 LG-LDM 表示，可能产生误报。
- 统计 compliance 不表示 temporal independence / latent distribution 假设在运行环境的每个局部窗口都成立；部署时需按状态检查 FIT、阈值覆盖率和 false alarm。
- GOF 的可解释性是“哪种统计假设遭拒绝”，不是 Metric/Trace 根因路径或业务来源因果解释。
- 当前是 CNF + LG-LDM 特例，如何选择或在线切换 state-dependent / multimodal inductive biases 尚未由本实验回答。

### 开源与复现

论文给出代码、模型和表格仓库。复现需固定 CNF RealNVP 配置、条件上下文长度、序列标准化、数据切分、训练顺序 / mini-batch 状态传递、MV-KS 实现 / critical value 和滑窗 $w$。真实数据上的 Optuna 配置使用标签指标调超参，因此应与最终 label-free test scoring 的声明分开看。本文未训练或复现模型。

## 8. 相关工作关系

- **CNF / FlowFuse**：两者都使用 flow 概率密度，但 FlowFuse 在多检测器 score space 学 normal joint density，CNF 把原始观测映到带显式时间动力学的 latent space，并做 GOF 合规检验。
- **COGNOS**：两者都把异常检测建立在可检验的统计残差 / 分布假设上；COGNOS 检验 MSE residual whiteness 并用 Kalman smoothing，CNF 检查 latent trajectories 对规定动态高斯的符合程度。
- **MACE / CAPMix / When Model Meets New Normals**：提供多模式或状态适配参照；CNF 的简洁 LG-LDM 是参数化单一路径实例，状态语义与安全 state transition 尚需扩展。
- **AnoMamba / IGAD / KAN-AD**：均试图让“学到的正常性”约束异常分数；AnoMamba 通过重构依赖，CNF 通过 latent GOF，IGAD 通过 idempotent manifold。
