# Knowledge Dossier — Multi-View Ensemble for Time Series Anomaly Detection via Coupling Flows

## 1. Basic Information

- **English title**: Multi-View Ensemble for Time Series Anomaly Detection via Coupling Flows
- **中文译名**: 基于耦合流的时间序列异常检测多视角集成
- **Authors**: Wanghui Qiu, Chenxi Liu, Shiyan Hu, Zhengyu Li, Chenjuan Guo, Bin Yang
- **Venue / year / CCF**: IJCAI 2026 / CCF B（依照人工确认）
- **Original PDF**: `Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf`
- **Completed reading note**: `papers/flowfuse/notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/decisionintelligence/FlowFuse（论文 PDF 首页列出）
- **Research area**: 无监督单变量 / 多变量时间序列异常检测；跨视角异常分数建模。
- **Method tags**: temporal-frequency；clustering；reconstruction；score fusion；normalizing flow；ensemble；uncertainty-guided supervision。

## 2. Research Scenario

论文面向跨领域时序监控：数据包含 spacecraft telemetry、server monitoring、health / movement、industrial systems、transport 等 benchmark。输入是带 $d$ 个测量维度的数值序列窗口，输出逐时刻、逐维度的异常分数及阈值化标签。论文没有输入 Log、Trace、release 或真实 workload 元数据；其 benchmark 场景虽含 AIOps / 服务器数据，但方法解决的是时序异常评分，不能等同完整运维诊断。（PDF §3.1, §4.1, Table 2, pp.3, 5）

窗口级 detector 分数先汇总到 timestamp，因此最终粒度是 point score；论文还按 global、contextual、seasonal、trend、shapelet、mixed 六类异常讨论 detector 差异。运维动机是复杂系统的异常形态不同，单一 detector 可能顾此失彼；系统可能需要将“局部时间偏离”“周期变化”“新模式”分别显现的证据组合起来。（§1, §3.3, §4.4, pp.1–3, 7）

## 3. Research Problem

在单变量和多变量监控序列中，不同异常形态会对时域、频域、聚类距离和重建误差产生不同响应；现有单一检测机制及简单平均 / 最大值等融合规则，难以同时覆盖多种异常并学习不同分数之间的非线性依赖。因此，作者研究的是：**如何构造异质的时序异常分数，并在无异常标签条件下学习其正常联合分布，以比线性聚合更好地利用互补检测证据。**（作者主张；PDF §§1, 3.2–3.5）

## 4. Core Challenges

1. **异常形态异质。** 点、上下文、周期、趋势、shapelet 与混合异常的显现域不同；只看时域或只用重建可能遗漏频谱变化或模式级偏离。检测影响是各模型的排名会随异常类型改变。（作者主张 §1；实验分型 §4.4, Fig. 2）
2. **分数融合存在交互。** 高 temporal 分数、低 frequency 分数可能是有效的局部异常组合；多路中等分数也可能共同指示异常。平均可能稀释第一种信号，max 可能忽视第二种，固定权重无法按分数组合变化。（作者主张 §3.4, Table 1）
3. **训练分布必须能代表正常 score pattern。** Flow 只处理四种 base detectors 产生的分数；如果这些 view 同时受到同一异常或状态切换影响，后续 score-density model 未必有额外信息可恢复。（分析推断，基于 §§3.3–3.4）

## 5. Limitations of Existing Methods

- **作者对方法家族的主张**：统计聚类、重建和判别方法各自依赖不同归纳偏置，倾向于对某些异常类型更有效。统计距离 / 聚类可抓新模式，重建模型对细微局部偏离有优势，但单方法难以覆盖上述多样性。（§2.1, §3.3）
- **作者对融合方式的主张**：average、maximum、learned linear weights 把不同 view 当作独立输入；MLP 可学非线性交互，但不显式估计正常分数组合的概率分布。FlowFuse 以可逆变换与 tractable likelihood 针对后一差距。（§3.4, Table 1）
- **实验实际支持**：六类异常中 detector 家族排名存在差异，mixed anomaly 下许多方法表现较低，支持“异质 detector 有互补空间”，但不证明本文覆盖了所有故障类型。（§4.4, Fig. 2）
- **证据冲突 / 边界**：论文形式化假设训练数据为 normal behavior（§3.1），但 Table 2 的部分 `Train AR` 数值非零，例如 NAB、OPPORTUNITY 等。正文未在该处解释此差异；不宜擅自断言 benchmark 训练段完全无异常，也不据此判断标签泄漏。此处作为复现核查项。（§3.1; Table 2, p.5）

## 6. Core Idea

先用四种“观察异常的角度”各自产生分数：时域聚类、时域重建、频域聚类、频域重建；再学习正常训练数据下这四组分数通常如何共同变化。测试分数若落在学到的联合分布低似然区域，就得到较高异常证据。多套 flow 的分歧可指出它们对某个分数组合意见不一致；有少量标签时，可把标注用在这些模糊样本上训练路由器。

## 7. Technical Innovations

### 7.1 Multi-perspective score construction

- **针对挑战**：不同异常类型在不同表示和检测范式下更显著。
- **机制**：对每个窗口并行计算 temporal/frequency × clustering/reconstruction 四个分数，再把重叠窗口分数平均到 timestamp，形成 $S_t\in\mathbb R^{d\times4$}。（修正排版：$S_t\in\mathbb R^{d\times4}$；PDF Eq. 1）
- **新颖边界**：FFT、K-means、Transformer reconstruction 是已有技术；论文的设计点是将两种域与两类 detector 范式组合为 score views，并将其交给联合融合模型，而非发明四个基础模型本身。
- **实验支持 / 适用限制**：四 view 消融都贡献，temporal view 在多数被测集影响更大；频域 view 在季节 / 谐波异常上有设计动机。mixed anomalies 仍难。（§4.3, Table 5; §4.4, Fig. 2）

### 7.2 Alternating temporal-frequency coupling flow

- **针对挑战**：线性分数聚合不能学习不同检测视角之间的非线性联合模式。
- **机制**：可逆 affine coupling 交替以 $T$ 更新 $F$、再以更新后的 $F$ 更新 $T$；flow 的标准 Gaussian latent norm 与 Jacobian determinant 共同给出负对数似然。模型学习 score-space normal density，不重新训练前四个 detector。（§3.4, Eqs. 2–5）
- **新颖边界**：normalizing flow 本身是成熟概率模型；作者贡献主张是其在 temporal/frequency score partitions 上的交替耦合方式和 score-fusion 应用。
- **实验支持 / 适用限制**：四个代表数据集的消融中，coupling-flow fusion 相对 simple averaging 的 Aff-F1 平均提高约 8.0%；这并非所有 benchmark、所有阈值预算上的普遍提升。（§4.3, Table 5）

### 7.3 Ensemble uncertainty 与可选监督路由

- **针对挑战**：无监督情况下的异质 flow 可能对样本分歧；有限标签应集中于决策模糊区域。
- **机制**：训练 $E=4$ 个不同初始化 / 数据子集的 flow；各自把 likelihood 转成相对训练分布的经验百分位分数，默认取平均。flow score variance 作为不确定性 proxy；有标签时选择高 uncertainty top-K 样本，以 pairwise ranking loss 训练 router。（§§3.4–3.5, Eqs. 5–9）
- **新颖边界**：ensemble disagreement 和 ranking router 是集成学习常见思想；论文将其用于 normal score distribution ensemble 与 selective supervision。
- **实验支持 / 适用限制**：1–5% 标签在四个展示数据集带来提升，继续增加标签收益变小；variance 是分歧代理，并未证明校准成概率置信度。（§4.4, Table 6）

## 8. Methodology

### A. Overall Architecture

序列标准化 → 默认长度 50、步长 1 的重叠窗口 → 四个 detector 分别生成 window-level score → 按时间戳平均窗口分数 → 逐变量标准化 $S_t$ → E 个 coupling flows 建模其联合正常分布 → likelihood percentile → 无监督平均 router 或可选半监督 router → threshold 得异常标签。（PDF §§3.2–3.5, pp.3–5）

### B. Data Processing

- 先 standardization；对时间序列用窗口 $W$ 和步长 $s$ 切分，默认 $W=50,s=1$。作者称可根据 FFT 周期自动确定窗口或由领域知识指定，默认实验统一使用 50。（§3.3）
- temporal / frequency view 共用窗口位置；frequency representation 由 FFT 得到。频域重建使用 magnitude 与 phase，频域 K-means 使用 magnitude spectrum。（§3.3）
- 窗口重叠时，对包含 timestamp $t$ 的所有窗口分数取平均：

$$s_t^{(v)}=\frac{1}{|W_t|}\sum_{w\in W_t}s_w^{(v)},\quad v\in\{1,2,3,4\}. \tag{1}$$

### C. Four Score Modules

1. **Temporal clustering**：训练窗口 K-means 学 $C=24$ 个典型模式；输入测试窗口，输出其到最近中心的 Euclidean distance。聚类外模式视为异常证据。
2. **Temporal reconstruction**：inverted-tokenization Transformer 以变量而非时间点作为 token，重建正常时间依赖；输出重建误差。
3. **Frequency clustering**：对窗口作 FFT，在幅度谱上做相同数量 $C=24$ 的 K-means，输出最近谱原型距离。
4. **Frequency reconstruction**：Transformer 处理 magnitude + phase 表示，重建正常谱型，输出误差；目标模式包括周期断裂和 harmonic distortion。（§3.3, PDF pp.3–4）

四路逐变量分数组成 $S_t\in\mathbb R^{d\times4}$，分成 $T_t=S_t[:,1:2]$ 和 $F_t=S_t[:,3:4]$。这些“异常形态与视角对应”是方法设计假设，不是一一确定的定理。（§3.3）

### D. Coupling Flow 公式与目标

分数先在每个变量内作零均值、单位方差标准化。每个 flow 由 $L_c$ 个 coupling blocks 构成。第 $\ell$ 层先用 $T$ 更新频率分数：

$$T_t^{(\ell+1/2)}=T_t^{(\ell)},\quad F_t^{(\ell+1/2)}=F_t^{(\ell)}\odot\exp s_\theta(T_t^{(\ell)})+t_\theta(T_t^{(\ell)}). \tag{2}$$

然后用更新后的 $F$ 反向条件化 temporal scores：

$$F_t^{(\ell+1)}=F_t^{(\ell+1/2)},\quad T_t^{(\ell+1)}=T_t^{(\ell+1/2)}\odot\exp s_\phi(F_t^{(\ell+1/2)})+t_\phi(F_t^{(\ell+1/2)}). \tag{3}$$

经过多个 block 得 $z_t=f_e(S_t)$。flow 训练目标为：

$$\mathcal L_{flow}^{(e)}=\frac1N\sum_t\left[\frac12\|z_t^{(e)}\|_F^2-\log|\det J_{f_e}(S_t)|\right]. \tag{5}$$

第一项让潜变量符合标准 Gaussian，Jacobian 项负责可逆变换的密度修正。每个 flow 依据训练分布将 test likelihood 转经验百分位 $r_e(S_t)$（Eq. 6）；无监督分数 $\bar r(S_t)=E^{-1}\sum_e r_e(S_t)$（Eq. 7）。原文的实现方向应结合其 score 定义保持一致，复现时核对代码。

### E. Training

先用 training sequences 训练四个 view 并计算正常 score patterns，再标准化这些 scores 并训练多个 flow，优化每个 flow 的 negative log-likelihood。默认 $C=24,E=4,L_c=2$。作者的任务 formulation 假设正常训练，但 Table 2 某些 `Train AR` 非零，实际数据预处理需要回代码 / benchmark split 核实。可选监督训练从 ensemble disagreement 最大样本中选 top-K，用标签异常-正常 pair 更新 routing network，目标是 pairwise ranking loss Eq. 9。（§3.1, §§3.3–3.5, §4.1）

### F. Inference

对新序列标准化并滑窗；四个 view 产生并 overlap-average 成 point scores；用各个 flow 计算样本 likelihood 相对 training likelihood distribution 的 percentile；默认平均 flow scores。若启用监督 router，则基于该 timestamp 的 $S_t$ 对 ensemble members 赋权。最终通过 score threshold 得到点级标签；论文全文对不同平台的统一部署 threshold policy 未明确完整展开。（§3.3–3.5）

### G. End-to-End Mechanism

数值时序 → 标准化 / 滑窗 / FFT → 四种异质 detector 输出 → 窗口到点级汇总 → temporal/frequency coupling-flow joint density → 各 flow 相对训练分布的百分位 → ensemble average / uncertainty-guided router → timestamp anomaly score 与 thresholded label。

## 9. Experimental Evidence

### Data, Baselines, and Metrics

实验包含 10 UTS + 8 MTS，共 18 个 benchmark；维数 1–55，平均序列长度约 785–1,416,825，异常率约 0.20%–15.57%。领域包括 telemetry、server、healthcare、movement、industrial 与 transport。（§4.1, Table 2, p.5）基线有 18 个，涵盖统计分布、重建、判别学习范式，并通过 TAB 统一评估。报告 Affiliated F1 与 AUROC；另按 35 种 detector 对六类 anomaly type 进行分组分析。（§4.1, Table 4; §4.4, Fig. 2）

### Main Results and Ablations

- **[实验支持]** FlowFuse 在多数数据集达到最佳或具竞争力表现；作者特别报告 LTDB、MITDB、NYC、SVDB 的较强结果。不是所有数据行都第一。（§4.2, Table 3）
- **[实验支持]** coupling-flow fusion 相对 simple averaging 的 Aff-F1 在四个代表数据集平均约 +8.0%；四个 view 均有贡献，temporal views 在大多数测试集影响较大。（§4.3, Table 5）
- **[实验支持]** deep models 对 global/contextual point anomalies 表现较好；KMeans / DWT / HBOS 等统计法在 seasonal/shapelet pattern 上较强；mixed anomaly 下各方法得分偏低。（§4.4, Fig. 2）
- **[实验支持]** $C=8$–32 对大多数被测集的变化低于 3%；$E=2\to4$ 有增益，更多 flow 收益饱和；四个展示集上 1–5% 标签改善 AUROC。（§4.4, Figs. 3, Table 6）
- **未充分证明**：flow 消融是四个代表数据集的 Aff-F1 平均，不能单独证明在固定线上误报预算、所有类别或所有 view 失效情形下同样获益。

## 10. Limitations

### A. 作者明确承认

正文没有专门的 limitations section。作者指出 mixed anomaly 总体较难（§4.4, Fig. 2），并报告不同检测范式存在 method-specific bias。其主要方法结论仍受训练 score pattern 与 benchmark setting 限制。

### B. 根据方法推断的潜在局限

- 若四个 base views 在新 workload / release 变化时一起改变，flow 可能把合法状态转换判成低似然，而 ensemble disagreement 也可能低估共同偏差（共同盲点）。这是按依赖训练 score distribution 作的推断，论文未直接测量。
- variance 衡量 flow members 分歧，不是校准概率或风险界限；不能只凭“不确定性低”认为 score 可靠。
- score fusion 能识别不常见的联合分数模式，但不会说明异常由哪个业务事件、服务依赖或资源负载造成。

### C. 尚缺乏证据

论文未报告真实 Trace / release / workload 条件化实验，也没有统一控制仅正常状态切换、仅故障、并发、未见合法状态的矩阵；缺少跨实体固定 FPR、event delay、group-wise false alarm 和 uncertainty calibration 结果。它没有证明这些能力不存在，而是该论文证据尚未覆盖。

## 11. Research Implications

**本知识库分析**：对 AIOps KPI 检测，可以把 forecast residual、频谱异常、聚类距离、重建误差等现成 detector scores 交给 score-level fusion；这可能比要求一个 backbone 同时学好所有异常类型更模块化。FlowFuse 适合作为无监督 score fusion baseline，且可用现成模型分数接入。但必须先确保 calibration 段代表各合法业务状态，另测多 view 共因失效；如果加入 Trace / release / workload，需作为显式 context 输入或评估变量，而非从 score likelihood 中推定原因。

## 12. Related Papers

- `TFC`、`TriAD`、`TFMAE`：使用多域 / 时频视角，但主要在表示、masking 或跨域候选层融合；FlowFuse 的关键在 detector score-space joint density。
- `COGNOS`：组合统计 residual 与 Kalman smoothing；可以提供一种统计分数作为 FlowFuse view，但两篇假设 / 输出阶段不同。
- [Conditional Normalizing Flows](cnf-latent-dynamics.md)：也是 flow 概率建模；FlowFuse 建模 detector scores 的联合分布，CNF 在原始序列 latent space 显式规定 temporal dynamics 并用 GOF 测合规。
- `CAPMix`：关注 noisy/dynamic KPI 的鲁棒训练与合成样本，属于 score 前端的互补方向。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| 任务与作者动机 | Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf | §1, PDF pp.1–2 | Verified in PDF-derived text and reading note |
| 四视角和输入输出 | same | §§3.2–3.3, Eq. 1, PDF pp.3–4 | Verified |
| Coupling transformation / density objective | same | §3.4, Eqs. 2–6, PDF pp.4–5 | Verified |
| Average and supervised router | same | §3.5, Eqs. 7–9, PDF p.5 | Verified |
| Dataset, train AR caveat, metrics | same | §4.1, Table 2, PDF p.5 | Verified; interpretation flagged |
| Main result and flow ablation | same | §§4.2–4.3, Tables 3, 5, PDF p.6 | Verified |
| Type-specific results and uncertainty supervision | same | §4.4, Figs. 2–3, Table 6, PDF p.7 | Verified |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "flowfuse",
  "title_en": "Multi-View Ensemble for Time Series Anomaly Detection via Coupling Flows",
  "title_zh": "基于耦合流的时间序列异常检测多视角集成",
  "authors": [
    "Wanghui Qiu",
    "Chenxi Liu",
    "Shiyan Hu",
    "Zhengyu Li",
    "Chenjuan Guo",
    "Bin Yang"
  ],
  "year": 2026,
  "venue": "IJCAI",
  "ccf_level": "B",
  "ccf_provenance": "user-confirmed inventory",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/IJCAI/Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf",
  "reading_note_path": "papers/flowfuse/notes.md",
  "code_url": "https://github.com/decisionintelligence/FlowFuse",
  "research_area": "Unsupervised time series anomaly detection; multi-view detector score fusion",
  "method_tags": [
    "temporal-frequency",
    "clustering",
    "reconstruction",
    "coupling flow",
    "ensemble",
    "uncertainty-guided routing"
  ],
  "research_scenario": "跨领域 UTS/MTS 数值时序监控；对 point-level anomaly scores 建模，benchmark 涵盖 telemetry、server、health、movement、industrial 和 transport。",
  "research_problem": "单一检测器与线性分数融合难以适应异质异常类型并建模不同视角分数之间的非线性依赖。",
  "core_challenges": [
    "不同异常类型在时域/频域和聚类/重建分数中的表现不同。",
    "平均、max 和固定线性权重不能学习复杂联合 score pattern。",
    "训练 score distribution 需代表正常状态，且基础 view 存在共同失效风险。"
  ],
  "existing_method_limits": [
    "作者认为单检测范式受特定归纳偏置限制。",
    "线性聚合忽略 cross-view interaction；MLP 不显式进行联合 density estimation。"
  ],
  "core_idea": "组合四个 temporal/frequency × clustering/reconstruction scores，以 coupling flows 学习正常联合分布，再对 flow percentile scores 做 ensemble routing。",
  "technical_innovations": [
    {
      "name": "Four-view score construction",
      "challenge": "anomaly heterogeneity",
      "mechanism": "temporal/frequency × clustering/reconstruction 四路窗口评分并聚合到 timestamp",
      "novelty_boundary": "基础 detector 是已有技术，贡献在系统化 score view 组合",
      "evidence": "四 view ablation; §4.3 Table 5",
      "conditions": "依赖 view 覆盖互补异常证据"
    },
    {
      "name": "Alternating coupling-flow fusion",
      "challenge": "nonlinear score dependency",
      "mechanism": "交替条件更新 temporal/frequency scores 并以 flow NLL 学 normal joint density",
      "novelty_boundary": "flow 方法已知，贡献在 score-space coupling 设计与应用",
      "evidence": "相对 simple average 四集平均约 +8.0% Aff-F1; §4.3 Table 5",
      "conditions": "训练分数分布需有代表性"
    },
    {
      "name": "Ensemble disagreement router",
      "challenge": "uncertain score patterns / limited labels",
      "mechanism": "ensemble variance proxy; optional top-K uncertainty samples + ranking loss",
      "novelty_boundary": "集成分歧和 ranking 思路已有，本文用于 selective score routing",
      "evidence": "1–5% labels results; §4.4 Table 6",
      "conditions": "variance is not calibrated probability"
    }
  ],
  "methodology": {
    "architecture": "standardize → sliding windows → four score modules → overlap aggregation → per-variable score standardization → E coupling flows → percentile scores → router/threshold",
    "data_processing": "window W=50, stride=1 by default; FFT for frequency views; overlap-average to timestamp",
    "modules": [
      "K-means temporal distance, C=24",
      "inverted-token Transformer temporal reconstruction",
      "K-means FFT magnitude distance",
      "frequency Transformer reconstruction over magnitude and phase",
      "alternating temporal-frequency affine coupling flows",
      "ensemble average or optional uncertainty-guided router"
    ],
    "key_formulas": [
      "Eq. 1 overlapping score aggregation",
      "Eqs. 2–3 alternating affine coupling",
      "Eq. 5 flow negative log-likelihood",
      "Eqs. 6–9 percentile scoring and routing loss"
    ],
    "training": "Train four detector views and score distribution; optimize E flows by NLL. Default E=4, Lc=2. Optional high-uncertainty labeled pairs train router with ranking loss.",
    "inference": "Compute four point-level scores, transform through each flow, map likelihood against training percentile distribution, average or route, then threshold.",
    "end_to_end": "numeric series → standardization/window/FFT → four detector scores → point aggregation → coupling-flow joint density → ensemble routing → point score/label"
  },
  "experimental_evidence": {
    "datasets": [
      "18 benchmarks: 10 UTS + 8 MTS; domains include telemetry, servers, health, movement, industrial and transport"
    ],
    "baselines": [
      "18 methods spanning statistical, reconstruction and discriminative paradigms",
      "35 detector types grouped by six anomaly types"
    ],
    "metrics": [
      "Affiliated F1",
      "AUROC",
      "VUS-PR in anomaly-type analysis"
    ],
    "main_results": [
      "Best or competitive on most benchmarks; strong on LTDB, MITDB, NYC and SVDB; §4.2 Table 3"
    ],
    "ablations": [
      "Coupling flow improves average Aff-F1 by about 8.0% over simple averaging on four representative datasets; all four views contribute; §4.3 Table 5"
    ],
    "robustness_generalization": [
      "Cluster count 8–32 stable within <3% for most datasets; ensemble size benefit saturates after E=4; §4.4 Fig. 3"
    ],
    "industrial_validation": [
      "No production deployment study or real Metric/Trace/release-conditioned validation is reported in the reading note."
    ]
  },
  "limitations": {
    "author_stated": [
      "Mixed anomaly performance remains challenging; §4.4 Fig. 2."
    ],
    "reasoned_inference": [
      "Common failures across all views cannot be repaired by a score-level fusion model.",
      "Ensemble variance is disagreement, not calibrated uncertainty.",
      "Joint score density does not explain operational cause."
    ],
    "evidence_gaps": [
      "State-transition × fault concurrency",
      "real Trace/workload conditioning",
      "fixed-FPR event delay",
      "uncertainty calibration",
      "training AR/table interpretation"
    ]
  },
  "research_implications": [
    "AIOps candidate baseline for fusing forecast residual, spectral, clustering, and reconstruction scores, provided normal states are separately represented and common-mode failures are evaluated."
  ],
  "related_papers": [
    {
      "paper_id": "tfc",
      "relation": "multi-domain features; FlowFuse fuses scores rather than building one fused representation"
    },
    {
      "paper_id": "cognos",
      "relation": "statistical residual score can complement detector views"
    },
    {
      "paper_id": "cnf-latent-dynamics",
      "relation": "both use flow density, but the modeled spaces and anomaly tests differ"
    },
    {
      "paper_id": "capmix",
      "relation": "robust KPI training complements score fusion"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "four views and task",
      "pdf_file": "Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf",
      "locator": "§§3.1–3.3, Eq. 1, PDF pp.3–4",
      "status": "verified"
    },
    {
      "claim_area": "flow fusion and loss",
      "pdf_file": "Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf",
      "locator": "§3.4, Eqs. 2–6, PDF pp.4–5",
      "status": "verified"
    },
    {
      "claim_area": "datasets and train AR caveat",
      "pdf_file": "Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf",
      "locator": "§4.1, Table 2, PDF p.5",
      "status": "verified; interpretation flagged"
    },
    {
      "claim_area": "results and ablations",
      "pdf_file": "Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf",
      "locator": "§§4.2–4.4, Tables 3,5,6; Figs.2–3, PDF pp.6–7",
      "status": "verified"
    }
  ],
  "provenance": {
    "pdf_sha256": "7e998d107c7addc51ae8aadc37173d4b769c1614ac69fb0f1b1375e41fcea497",
    "reading_note_sha256": "1d301640850880e30a91d6189305df00a6f6f3595012e1b12fec4e09e0f6bf15",
    "extraction_status": "complete",
    "knowledge_card_sha256": "34aeaa31e2b6cfe040312ea17fba4811341971981cbb53ca1339869a80ba9ed8"
  },
  "knowledge_card_path": "papers/flowfuse/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
