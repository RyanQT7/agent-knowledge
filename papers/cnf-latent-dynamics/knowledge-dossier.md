# Knowledge Dossier — Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows

## 1. Basic Information

- **English title**: Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows
- **中文译名**：通过条件正则化流潜空间归纳偏置进行时间序列异常检测
- **Authors**: David Baumgartner, Eliezer de Souza da Silva, Iñigo Urteaga
- **Venue / year / CCF**: UAI 2026 / CCF B（按用户已确认清单）
- **CCF provenance**: 用户已人工确认；本次不重新评定。
- **Original PDF**: [Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf](../../sources/papers/tsad-2024-2026/2026/UAI/Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf)
- **Completed reading note**: [papers/cnf-latent-dynamics/notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/iurteagalab/probML_anomaly_detection （论文资料列出的作者实验仓库；代码是否包含论文全部最终配置需按仓库版本核对）
- **Research area**: 无监督时间序列异常检测、生成式建模、统计 goodness-of-fit 检验。
- **Method tags**: conditional normalizing flow；latent dynamics；Gaussian state-space prior；whitening；MV-KS；GOF；threshold-free decision（依赖检验假设）。

## 2. Research Scenario

论文针对无异常标注或异常标签有限时的通用时间序列异常检测。输入是多维观测序列 $x_t\in\mathbb R^D$，模型使用过去 $k$ 步 $W_t=x_{t-k:t-1}$ 作为条件，将当前观测映射为 latent $z_t$；测试阶段对一段连续 latent trajectory 输出窗口级异常判定。实验既包含四维合成数据上的 amplitude、frequency、observation-noise 改变，也包含 TSB-AD 的 UTS / MTS 序列；论文没有把 Metric、Trace、Log、服务拓扑或业务事件作为输入。真实序列 benchmark 不等同真实生产部署。（§§1、3、4.1–4.2，PDF pp.1–8）

它面对的运维动机是：NLL 衡量模型给观测分配的密度，但高维异常可能仍落在高似然区域；若只用 observation-space likelihood 排序，检测器可能忽略时间结构发生的改变。论文转而问一段 latent 轨迹是否符合预先规定的动态统计规律。输出是检验拒绝 / 接受该动态合规假设，不是故障类型或根因。（§1、§3.2）

## 3. Research Problem

在无监督时序检测中，生成模型可拟合观测密度，却可能把不符合正常时间演化的样本映射到高似然区域，因而似然排序不能可靠代表 temporal typicality；因此作者研究如何在潜空间显式定义正常 latent dynamics，并对测试轨迹是否符合这一统计规律进行可检验的异常判断。（作者问题定义，§1、§3，PDF pp.1–4）

## 4. Core Challenges

1. **Likelihood 与时序典型性不等价。** 异常可能在观测空间具有较高密度，NLL 因此漏报；直接提高 density fit 并不自动解决该问题。（作者主张；合成例子实验支持，Fig.1, §4.2, PDF p.6）
2. **无标签条件下需要可操作的“正常行为”定义。** 仅训练 CNF 不说明何为时间上合理；需给 latent trajectory 一个显式统计假设，并检查训练 latent 是否满足它。（§3.1–3.2, Fig.3）
3. **GOF 检验依赖窗口样本数、维度和模型合规性。** 窗口太短时 MV-KS power 低，过长会把点异常平均掉；若训练 latent 本身不符合规定分布，自动临界值没有可靠含义。（§3.2、§4.2、§5，Table 2、Fig.3）
4. **归纳偏置可能与真实序列不匹配。** 实验采用线性 Gaussian latent dynamics (LG-LDM)；平坦 / 高度不规则序列、context 失配和模型容量选择会影响拟合与 FIT。（作者限制，§5, PDF p.8）

## 5. Limitations of Existing Methods

- **Likelihood-based detector**：常将负对数似然作为异常分数，核心假设是低观测密度意味着异常。作者以高维 OOD / amplitude alteration 可能仍落入高似然区域为动机，因而提出 temporal GOF；合成 Fig.1 支持该风险存在，但不能推出 NLL 在所有真实任务均不适用。（§1、Fig.1）
- **静态 latent prior**：标准 $\mathcal N(0,I)$ prior 表示静态 latent 分布，未显式描述潜变量随时间的演化。作者用 LG-LDM 增加动态均值结构；消融结果支持测试序列上有改善，但不证明任意数据均适合线性动态。（§3.1、§4.2）
- **证据边界**：真实基准 aggregate 中 NLL 排名优于 KS（UTS 第 7 vs 第 17），作者并未声称 GOF 全面取代 likelihood。KS 的优势主要出现在合成结构改变及满足 FIT 的数据子集。（§4.2, Tables 3–5, PDF pp.7–8）

## 6. Core Idea

先训练条件 flow，把每个当前观测连同其过去上下文映射到 latent；与此同时规定 latent 均值如何随时间变化。将 latent 按该动态均值和方差白化后，若模型及归纳偏置合适，训练数据应近似来自独立标准 Gaussian。训练时先做 FIT 合规检查；部署时对连续窗口做 MV-KS 检验。这样检测的对象不是“这个观测密度低不低”，而是“这一段 latent 轨迹是否符合预设的正常时间规律”。（§§3.1–3.2, Eqs.1–12）

## 7. Technical Innovations

### 7.1 在条件 flow latent 中显式加入时间演化偏置

- **挑战**：观测似然不保证时间行为 typical。
- **机制**：$z_t=F(x_t\mid W_t;\theta)\sim\mathcal N(\mu_t,\Sigma_t)$，用 $\mu_t=\psi(\mu_{t-1};\phi)$ 指定 latent 轨迹演化；实验以 $\mu_t=A\mu_{t-1}+b,\Sigma_t=I$ 实例化 LG-LDM。（§3.1, Eqs.1–5, PDF pp.3–4）
- **新在哪里**：CNF 和 state-space dynamics 都是已有组件；论文的主张是联合拟合条件流与 latent dynamics，并将异常判为潜在动态不合规，而非仅依据 observation NLL。
- **实验支持与限制**：与静态 Gaussian prior 消融在被测真实数据上有优势；MITDB 低 FIT 例说明偏置错配会削弱方法。（§4.2, pp.6–7）

### 7.2 将白化 latent 轨迹转化为 MV-KS 合规性检验

- **挑战**：无标签检测需要可说明的正常假设，且避免人工选异常阈值。
- **机制**：$\tilde z_t=\Sigma_t^{-1/2}(z_t-\mu_t)$；训练阶段以 MV-KS statistic 和样本数相关临界值定义 $FIT=\mathbf1[s_T\le\tau_T]$。测试长度 $w$ 的窗口若 $s_w\ge\tau_w$，拒绝“服从规定 latent dynamics”的原假设。（§3.2, Eq.12, Fig.3）
- **新颖边界**：统计 GOF 检验本身并非新技术；创新主张在于把它作用于经动态条件 flow 白化的 latent trajectory，并同时给出训练拟合诊断 FIT。
- **实验支持与限制**：合成结构 / 频率变化下可优于 NLL；真实 leaderboard 上 KS 排名较低，且需要 FIT 和样本窗口条件成立。无阈值调节不是无假设或无适配成本。

### 7.3 完整序列与 Markovian subsequence 的联合似然训练

- **机制**：联合优化 flow 参数 $\theta$ 和动态参数 $\phi$，似然含动态 Gaussian 项与各 flow layer 的 Jacobian log-determinant；另提供 Markovian dynamics 下的 subsequence mini-batch 形式以控制长序列计算。（§3.1.2, Eqs.7–11）
- **创新边界**：这为长序列 flow 训练提供与动态状态传递相容的优化形式；RealNVP 变体和最大似然优化本身不是新贡献。
- **证据范围**：论文报告训练配置与真实数据实验，但没有独立消融完整序列优化与 subsequence 优化对检测质量的差异，故其具体性能收益未被单独量化。

## 8. Methodology

### A. 总体架构

历史上下文 $W_t$ 与当前观测 $x_t$ → 条件 normalizing flow → latent $z_t$ → latent dynamics 产生 $\mu_t,\Sigma_t$ → 白化 $\tilde z_t$ → 训练期 FIT / 测试期窗口 MV-KS → 接受或拒绝动态合规性原假设。（§§3.1–3.2, Fig.2, PDF pp.3–5）

### B. 数据处理

对每个时刻使用过去 $k$ 个观测作为条件上下文。真实实验搜索 context 长度 5–500、flow 层数 3–40、hidden layers 1–20、hidden size 4–200；序列标准化的统一细节以论文数据 pipeline 为准，阅读笔记未指出所有基准采用完全相同预处理。原文使用 RealNVP 变体。滑窗统计长度 $w$ 决定 GOF 的样本量，也决定异常平均效应。（§4.1 Table 1；§4.2 Table 2）

### C. 模块机制

1. **条件 flow**：输入 $(x_t,W_t)$；$F$ 按条件可逆映射得到 $z_t$；输出同维 latent 及可计算 Jacobian；作用是拟合条件观测分布。（Eq.1）
2. **Latent dynamics**：通用形式为 $\mu_0\sim p(\phi_0),\;\mu_t=\psi(\mu_{t-1};\phi)$。实验中 $\mu_0\sim\mathcal N(0,I)$、$\mu_t=A\mu_{t-1}+b$、$\Sigma_t=I$。若 $\rho(A)<1$，均值轨迹趋向固定点；这只是 latent 参照模型，不表示真实业务系统必为线性单状态过程。（Eqs.2–5）
3. **联合似然训练**：优化 flow 与 dynamics 参数，序列级目标为：

$$\mathcal L_{seq}=-\frac1T\sum_{t=1}^T\left[\log p_t(F(x_t\mid W_t))+\sum_{l=1}^L\log|\det J_{F_l}(x_{t,l}\mid W_t)|\right],$$

其中 $p_t=\mathcal N(\mu_t,\Sigma_t)$。在 Markovian dynamics 下可对子序列 mini-batch 训练，并将上一个 batch 末状态用作后续初始状态。（§3.1.2, Eqs.7–11）
4. **Whiteening 与 GOF**：将 latent 减去规定动态均值并按协方差白化。若动力学被满足，白化变量应近似 iid $\mathcal N(0,I)$。MV-KS 比较经验样本与完全指定的高斯分布；统计量依序列长度有对应临界值。（§3.2）

### D. 关键公式与损失含义

核心检测判据为 $s_w\ge\tau_w$ 时拒绝规定 latent dynamics 合规性（Eq.12）。$s_w$ 是窗口 whitened latent 的 MV-KS 统计量，$\tau_w$ 是对应样本数下的临界值。训练诊断 $FIT=\mathbf1[s_T\le\tau_T]$ 仅表示训练轨迹统计上是否符合归纳偏置，不代表检测性能，也不是运行期 SLA 保证。（§3.2, Fig.3）

### E. 训练

训练数据被作为正常行为样本；同时优化 RealNVP 条件 flow 与 latent dynamics 参数，以条件 likelihood 与 Jacobian 项形成目标。完整序列和 subsequence mini-batch 两种写法在 batch size 等于整段长度时一致。训练后计算全训练白化 latent 轨迹的 MV-KS，并先检查 FIT。超参数在真实数据上以 Optuna TPE 搜索；论文报告每个配置 20 次 warm-up + 100 次 trials。因搜索可使用标签指标，需将超参选择协议与测试阶段 label-free 判定区分。（§3.1.2、§4.1）

### F. 推理

对测试流逐时构造条件 latent，按模型估计的动态均值 / 协方差白化；取长度 $w$ 的窗口计算 MV-KS statistic。如果 $s_w\ge\tau_w$ 则拒绝原假设并标为 unexpected behavior。论文并未将每个窗口判断如何在重叠窗口下聚合成最终点级标签完整标准化，相关实现应以代码确认；不能将统计检验判定直接解释成故障原因。（Eq.12）

### G. 端到端机制

数值序列 → 构造历史上下文 → CNF 条件映射 → latent dynamics 参照 / 白化 → FIT 检查或窗口 MV-KS → 检验是否拒绝预设的正常动态。潜变量维度、窗口选择和归纳偏置需要与数据适配；原文未明确的部署聚合细节留待代码核对。

## 9. Experimental Evidence

### 数据、Baseline 与指标

论文包括四维合成序列及 TSB-AD 的单变量、多变量子集和 1080 条序列 leaderboard 聚合。基线按 TSB-AD 排名挑选；真实数据超参用 Optuna TPE 搜索。报告 VUS-PR 及 oracle-thresholded 指标；oracle 阈值结果不等于无监督测试阈值性能。（§4.1, Table 1; §4.2, Tables 3–5）

### 主要结果与消融

- **[实验支持] 合成异常**：$w=64$ 时 MV-KS 的 AUC-PR 82.1、VUS-PR 96.0、Affiliation F1 92.6；NLL 分别为 78.8、92.8、85.0（百分数）。Fig.1 中 NLL 漏掉被映射至高密度区的 amplitude alterations，而 MV-KS 检出三类变化。（§4.2, Table 2, Fig.1, PDF p.6）
- **[实验支持] 窗口敏感性**：窗口过短导致统计波动，过长会稀释异常；$w=200$ 时 AUC-PR 为 58.3、VUS-PR 为 90.4，说明窗口选择有实质影响。（Table 2）
- **[实验支持] 真实 leaderboard**：1080 条序列聚合中 UTS 的 NLL 排名第 7，KS 第 17；真实数据不支持 KS 普遍胜过 likelihood。（§4.2, Table 5, PDF p.8）
- **[实验支持] FIT 子集差异**：NEK / Stock 等 FIT 较高序列具有竞争结果；MITDB 的 FIT 约 18% 且 NLL、KS 都退化，支持先检查动态假设适配性的必要性。（§4.2, Tables 3–5）
- **[消融支持] 动态 prior**：在 UCR、TAO、MITDB、Exathlon、Yahoo、Opportunity 等测试序列上，LG-LDM 对标准高斯 latent prior 的 KS VUS-PR 为 $0.921\pm0.092$ vs. $0.836\pm0.213$，VUS-ROC 为 $0.984\pm0.027$ vs. $0.977\pm0.032$。（§4.2, PDF pp.6–7）

这些实验支持在特定合成改变和 FIT 适配数据上检验 latent dynamics 的价值；并未证明窗口无关、在任意高维序列有足够统计 power，或能解释合法状态变化与故障。

## 10. Limitations

### A. 作者明确承认

作者指出 highly flat / erratic 序列仍难校准；GOF 效能受样本量和维数影响，高维时需要较长窗口（讨论建议约 $O(D^3)$），但长窗口会平滑孤立异常；模型容量、context 和数据行为敏感，预处理及 latent inductive bias 需要领域知识，LG-LDM 并不适合所有序列。（§5, PDF p.8）真实序列中 NLL 对 point / spike anomaly 可更好。（§4.2, §5）

### B. 根据方法推断的潜在局限

- 单一 latent dynamics 可能把合法的新 workload / 发布状态视为不合规；因为检验只针对预先指定统计规律，不含业务状态语义。论文没有直接验证状态切换并发故障。
- MV-KS 检验拒绝的是分布假设，不是故障因果解释；不能单独归因到 Metric、服务依赖或发布。
- FIT 是训练数据上的合规诊断，不能保证未来分布仍合规；部署应监控 FIT 类统计、误报和状态分组性能。

### C. 尚缺乏的证据

论文没有充分给出业务上下文条件化的多正常状态检验、状态转换与故障同时发生的分解实验，以及跨环境固定误报率 / 延迟评测。缺少这些评测是证据边界，不表示方法必然无法扩展。

## 11. Research Implications

**本知识库分析**：CNF + GOF 可作为检验式无监督 baseline，尤其适合要显式核对“正常动态假设是否成立”的实验；AIOps 使用时，应将 workload、release 和服务状态作为分组 / 条件变量，另行评估新状态和状态切换中的故障共现。对 Metric 可尝试在低维残差或状态表示上做分块 GOF；对 Trace / Log 只能在先构造结构化时间序列表示后探索，论文没有验证多模态输入。值得验证的方向包括 context-conditioned latent dynamics、短窗统计 power 和误报预算下的事件延迟。

## 12. Related Papers

- [FlowFuse](../flowfuse/knowledge-dossier.md)：都使用 normalizing flow，但 FlowFuse 建模 detector-score 联合分布；本文建模原始观测条件 latent 的时间动态并做 GOF，正常性定义不同。
- [COGNOS](../cognos/notes.md)：两者以统计假设增强检测；COGNOS 检查 MSE residual 的 Gaussian whiteness 并做 Kalman smoothing，本文检验 latent dynamics 合规。
- [MACE](../mace/notes.md) 与 [CAPMix](../capmix/notes.md)：涉及多正常模式或动态 KPI 鲁棒性，可作为检验单一 LG-LDM 假设的对照。
- [When Model Meets New Normals](../when-model-meets-new-normals/notes.md)：显式在线适应测试期新正常状态；与本文拒绝固定 latent dynamics 的路线互补。
- [AnoMamba](../anomamba/notes.md)、[Idempotent Reconstruction](../idempotent-reconstruction/notes.md)：分别以全局依赖和固定点流形约束定义可重建正常性，和本文的 latent GOF 形成不同的正常性约束范式。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Likelihood 与 temporal typicality 动机 | Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf | §1, PDF pp.1–2; Fig.1, p.6 | 已由精读笔记及 PDF 派生文本核对 |
| CNF 与 latent dynamics | same | §3.1, Eqs.1–11, PDF pp.3–5 | 已核对 |
| FIT / MV-KS 判据 | same | §3.2, Eq.12; Fig.3, PDF pp.4,7 | 已核对 |
| Synthetic 与窗口结果 | same | §4.2, Table 2; Fig.1, PDF p.6 | 已核对 |
| 真实数据、prior ablation、FIT | same | §4.2, Tables 3–5, PDF pp.6–8 | 已核对 |
| 作者局限 | same | §5, PDF p.8 | 已核对 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "cnf-latent-dynamics",
  "title_en": "Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows",
  "title_zh": "通过条件正则化流潜空间归纳偏置进行时间序列异常检测",
  "authors": [
    "David Baumgartner",
    "Eliezer de Souza da Silva",
    "Iñigo Urteaga"
  ],
  "year": 2026,
  "venue": "UAI",
  "ccf_level": "B",
  "ccf_provenance": "用户已人工确认的论文清单",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/UAI/Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf",
  "reading_note_path": "papers/cnf-latent-dynamics/notes.md",
  "code_url": "https://github.com/iurteagalab/probML_anomaly_detection",
  "research_area": "无监督时序异常检测；生成式建模与统计检验",
  "method_tags": [
    "conditional normalizing flow",
    "latent dynamics",
    "LG-LDM",
    "whitening",
    "MV-KS",
    "goodness-of-fit"
  ],
  "research_scenario": "多维连续时序；用历史上下文生成条件 latent，并按窗口判断 latent dynamics 是否合规；没有输入业务上下文、多模态遥测或因果标签。",
  "research_problem": "观测似然可能把违反正常时间规律的样本映射到高密度区域，因此需要在潜空间显式规定并检验正常时间动态。",
  "core_challenges": [
    "观测似然不等同 temporal typicality",
    "无标签时必须给正常动态可检验定义",
    "GOF 对窗口长度、维数和训练合规性敏感",
    "LG-LDM 归纳偏置可能与数据失配"
  ],
  "existing_method_limits": [
    "NLL 可能漏掉落入高密度区域的异常",
    "静态高斯 latent prior 不编码动态演化",
    "真实 leaderboard 中 KS 并未全面胜过 NLL"
  ],
  "core_idea": "将条件观测映射到带预设时间演化的 latent trajectory，白化后用训练 FIT 与测试 MV-KS 检验分布合规性，而非单靠 observation-space NLL。",
  "technical_innovations": [
    {
      "name": "Latent temporal inductive bias",
      "challenge": "似然和 temporal typicality 不等价",
      "mechanism": "联合条件 flow 与 latent dynamics，实验采用 LG-LDM",
      "evidence": "LG-LDM 对静态 Gaussian prior 的 ablation 提升被测集平均 VUS-PR",
      "boundary": "线性 Gaussian law 不适用于所有序列"
    },
    {
      "name": "FIT + MV-KS compliance",
      "challenge": "无标签定义正常动态并判断统计偏离",
      "mechanism": "白化 latent 后作样本数相关的 GOF 检验",
      "evidence": "合成改变实验有效，FIT 低的 MITDB 表现退化",
      "boundary": "窗口和维数强烈影响统计效能"
    },
    {
      "name": "Markovian subsequence optimization",
      "challenge": "完整长序列 flow 优化成本",
      "mechanism": "跨 batch 传递上一子序列的 latent dynamics 状态",
      "evidence": "训练方案给出，未独立消融其检测收益",
      "boundary": "依赖 Markovian dynamics 假设"
    }
  ],
  "methodology": {
    "architecture": "history context → conditional RealNVP flow → prescribed latent dynamics → whitening → FIT or window MV-KS",
    "data_processing": "每个时刻使用过去 k 步为条件；测试在长度 w 窗口做 GOF；超参范围见 §4.1 Table 1",
    "modules": [
      "conditional normalizing flow",
      "linear Gaussian latent dynamical model",
      "whitening",
      "multivariate Kolmogorov–Smirnov test"
    ],
    "key_formulas": [
      "z_t=F(x_t|W_t;theta)~N(mu_t,Sigma_t), Eqs.1–5",
      "sequence conditional NLL with flow Jacobian, Eqs.7–11",
      "FIT=1[s_T<=tau_T]",
      "reject if s_w>=tau_w, Eq.12"
    ],
    "training": "Joint conditional likelihood optimization over flow and dynamics parameters; FIT is evaluated on the whitened training trajectory.",
    "inference": "Generate conditional latent sequence, whiten it, and reject the prescribed dynamic distribution when MV-KS statistic reaches its sample-size threshold.",
    "end_to_end": "sequence → context → conditional latent → dynamics whitening → statistical compliance test → unexpected-behavior decision"
  },
  "experimental_evidence": {
    "datasets": [
      "4D synthetic amplitude/frequency/noise alterations",
      "TSB-AD UTS/MTS subsets",
      "1080-series aggregate leaderboard"
    ],
    "baselines": [
      "NLL",
      "TSB-AD-ranked anomaly detection methods",
      "LG-LDM vs standard Gaussian latent prior"
    ],
    "metrics": [
      "AUC-PR",
      "VUS-PR",
      "Affiliation F1",
      "VUS-ROC",
      "FIT"
    ],
    "main_results": [
      "Synthetic w=64: MV-KS AUC-PR 82.1, VUS-PR 96.0, Aff-F1 92.6 vs NLL 78.8, 92.8, 85.0",
      "1080-series UTS ranking: NLL 7th, KS 17th"
    ],
    "ablations": [
      "LG-LDM KS VUS-PR .921±.092 vs static Gaussian .836±.213; VUS-ROC .984±.027 vs .977±.032"
    ],
    "robustness_generalization": [
      "Short windows unstable; long windows dilute point anomalies; MITDB low FIT accompanies degradation"
    ],
    "industrial_validation": [
      "No production Metric/Trace/release-conditioned deployment study reported"
    ]
  },
  "limitations": {
    "author_stated": [
      "flat/erratic data difficult to calibrate",
      "high-dimensional GOF needs long windows that can smooth point anomalies",
      "model capacity, context and LG-LDM fit are data-sensitive"
    ],
    "reasoned_inference": [
      "one latent law may reject legal workload or release transitions",
      "GOF rejection does not identify fault cause",
      "training FIT does not guarantee future compliance"
    ],
    "evidence_gaps": [
      "multiple legal states and transitions",
      "fault concurrent with state change",
      "cross-environment fixed-FPR and event-delay evaluation"
    ]
  },
  "research_implications": [
    "Use as a statistical-compliance baseline; evaluate context-conditioned latent laws and false-alarm budgets for AIOps."
  ],
  "related_papers": [
    {
      "paper_id": "flowfuse",
      "relation": "Both use flows but model score-space joint density versus original observation latent dynamics."
    },
    {
      "paper_id": "cognos",
      "relation": "Both define statistical normality using residual or latent distribution assumptions."
    },
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "Online new-normal adaptation is complementary to testing a fixed latent law."
    },
    {
      "paper_id": "mace",
      "relation": "Multi-pattern normality can test the single-dynamics assumption."
    }
  ],
  "evidence_references": [
    {
      "claim_area": "method",
      "pdf_file": "Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf",
      "locator": "§§3.1–3.2, Eqs.1–12, PDF pp.3–5",
      "status": "verified from source-grounded note and PDF-derived text"
    },
    {
      "claim_area": "synthetic results",
      "pdf_file": "same",
      "locator": "§4.2, Table 2, Fig.1, PDF p.6",
      "status": "verified"
    },
    {
      "claim_area": "real data and limitations",
      "pdf_file": "same",
      "locator": "§4.2 Tables 3–5 and §5, PDF pp.6–8",
      "status": "verified"
    }
  ],
  "provenance": {
    "pdf_sha256": "cd76f7ee450fee5ebe22c8db1c9215a2d411db43d848df1d77f499283b5530cb",
    "reading_note_sha256": "f6d5eb53cccb058a6d7d319801a95baae2440a7c6dba6a54ccab9bfbe6484e4e",
    "extraction_status": "complete",
    "knowledge_card_sha256": "a9cb366fb61b9991d888470a441932ed9818aa8744055e43f6b8071e871dcfa4"
  },
  "knowledge_card_path": "papers/cnf-latent-dynamics/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
