# TSAD 2024–2026：33 篇论文综合全景与研究问题

## 范围与证据标记

本文综合本知识库中 33 篇论文的完整 PDF 精读笔记和 Knowledge Review v3–v13。它不是统一 benchmark 排名：论文使用的数据、标签、阈值、窗口和指标不同。每行中的评估结论仅说明对应论文报告的证据；跨论文研究空白均列出具体论文证据。统一使用：

- **[论文主张]**：作者提出的动机、方法或解释。
- **[实验支持]**：论文数据、对比、消融、失败案例或作者明确报告的实验结果。
- **[综合分析]**：跨论文解释或待验证推断，不应误读为某篇论文的结论。

每篇都可从下表进入详细笔记。原始 PDF 位于 [TSAD 论文目录](../../sources/papers/tsad-2024-2026/)；[Knowledge Reviews v3–v13](./knowledge-review-v3.md) 给出按批次整理的机制比较和证据边界。

## 1. 33 篇论文全景对比

| 论文 | 正常性参照 / 异常证据 | 主要实验支持 | 关键边界（原文或本库分析） |
| --- | --- | --- | --- |
| [CAPMix (2026)](../../papers/capmix/notes.md) | KPI 窗口的形态与 DTW 单中心距离；CutAddPaste 伪异常、软标签和 dual-space Mixup | 对注入分布偏移与噪声有鲁棒性实验 | 单中心、多数正常假设；Best RPA-F1 阈值扫描不等于线上固定运行点（Review v3–v5） |
| [When Model Meets New Normals (2024)](../../papers/when-model-meets-new-normals/notes.md) | EMA 趋势去除后，按模型重建 / 预测 mask 适配测试期新分布 | 测试时更新对新正常状态的实验 | 多数点确为正常、伪标签可信；更新可能吸收漏检故障，状态语义未验证（Review v3–v6） |
| [CAROTS (2025)](../../papers/carots/notes.md) | 正常期 Granger 预测关系；CPA 保持、CDA 扰动关系，SOC 保留多种正例 | 因果感知增强和对比学习消融；多变量鲁棒性实验 | 现实因果图缺 ground truth；假设机制相对稳定；加入因果预测分数不总有益（Review v3, v6） |
| [CrossAD (2025)](../../papers/crossad/notes.md) | 粗到细多尺度重建、跨窗子序列 query 与 EMA 原型 | 多尺度 / 跨窗模块消融和多 benchmark | 原型不等于业务状态标签；测试更新边界与个别 SWAN 指标例外需注意（Review v4–v6） |
| [Fortifying Time Series (2025)](../../papers/fortifying-time-series/notes.md) | 对 DTW 扰动下分类决策做 randomized smoothing / Keogh 证书 | 报告 certified radius、覆盖率与鲁棒检测 | 证书表示有限威胁集下决策不翻转，不保证原预测正确；保守半径和覆盖、效用、成本有权衡（Review v4–v5） |
| [MACE (2024)](../../papers/mace/notes.md) | 服务条件 Fourier 基学习多模式频域 normality | 多数据服务 / 频谱表达效果及效率比较 | service identity 是静态条件，不等价于同一服务内部动态 workload state（Review v4–v6） |
| [Graph-MoE (2025)](../../papers/graph-moe/notes.md) | 多层图专家表示和窗口级 latent memory 路由 | 多深度专家 / memory routing 实验 | attention graph 与 memory 不自动代表物理拓扑或业务模式；memory 更新与异常写入语义未充分验证（Review v5–v6） |
| [CCM-TAD (2026)](../../papers/ccm-tad/notes.md) | 静态 channel correlation profile clusters、因果时间遮罩和顺序分数 | 在线多变量数据上的多指标比较 | “causal”时间遮罩不等于变量间因果；cluster 不是动态业务态；部分 Best-F1 协议使用标签搜索（Review v5–v6） |
| [TFC (2026)](../../papers/tfc/notes.md) | Temporal、frequency、curvature 特征融合与动态路由 | 多类指标 / 数据集对比 | 主要单变量；异常分数 / loss 细节、曲率边界和潜在前视依赖需要核查（Review v5–v6） |
| [GCAD (2025)](../../papers/gcad/notes.md) | forecasting loss 对输入的梯度作为 Granger predictive-influence proxy，构成稀疏图 | 依赖变化异常检测结果 | 无真实图真值或 intervention 核验；高阶交互和状态条件图不足（Review v6） |
| [OracleAD (2025)](../../papers/oraclead/notes.md) | 点级预测残差加 contextual embedding 的结构偏差 | 预测 / 结构分数对比与消融 | 结构距离对滑窗延迟 / 恢复期敏感；部分 F1 采用测试 oracle threshold（Review v6） |
| [SARAD (2024)](../../papers/sarad/notes.md) | 前后半窗 self-attention association 下降，识别关联减弱 | 关联下降检测与诊断实验 | 半窗可能稀释短异常；空间成本随 channel 数二次增加；关联变化不等于故障原因（Review v6） |
| [Quo Vadis (2024)](../../papers/quo-vadis/notes.md) | 评测常见 unsupervised baseline、score normalization、point / range metric 和阈值协议 | 展示简单方法在其协议下具有竞争力，分析 point adjustment 影响 | 不证明简单 baseline 全场景充分；test-oracle F1 不等于部署表现（Review v7） |
| [TSB-AD / The Elephant in the Room (2024)](../../papers/tsb-ad/notes.md) | 数据质量、统一 detector 调参和指标行为作为 benchmark 参照 | 数据集统一整理、多指标排名和方法比较 | 排名随数据 / metric / anomaly type 改变；benchmark label 与单一 metric 均非普适真值（Review v7） |
| [TFMAE (2024)](../../papers/tfmae/notes.md) | temporal / frequency masked-view 表示差异作为异常证据 | 组件消融及其评估协议下的检测结果 | 主要依赖 point adjustment 等协议；未证明可区分合法业务状态转移（Review v7） |
| [TriAD (2024)](../../papers/triad/notes.md) | temporal / frequency / residual 三域窗口表示；跨窗口对比后用 discord 进行变量定位 | UCR benchmark 上不同域和局部化结果 | 实验假设每条 UCR test series 一个事件；$Z=1$ 假设限制多事件外推（Review v8） |
| [PCRTA (2024)](../../papers/pcrta/notes.md) | 七类扰动和伪标签引导的对比表示，多个 view 的 LOF 分数融合 | perturbation / view 消融 | synthetic perturbation family 未必代表真实故障；标签阈值枚举、推理成本和新正常混淆需检验（Review v8） |
| [Sub-Adjacent Transformer (2024)](../../papers/sub-adjacent-transformer/notes.md) | 约束 attention 关注非紧邻时间邻域；重建异常点 | attention band / reconstruction 结果 | 依赖固定 sub-adjacent band 和窗口；循环边界、局部状态变化及 test-best threshold / point adjustment 影响外推（Review v8） |
| [AnomalyLLM (2024)](../../papers/anomalyllm/notes.md) | 冻结大模型 teacher 表示，prototype student 学正常嵌入，距离为分数 | UCR 和多变量数据上的蒸馏 / prototype 实验 | LLM 主要充当 teacher，不等于生成式语义诊断；prototype 数、metric 与数据设置口径需核对（Review v9） |
| [Delving into LLMs for TSAD (2025)](../../papers/delving-llm-tsad/notes.md) | ACF 去季节后，以 index-value 文本和图像提示 frozen LLM/MLLM 预测区间 | 21 个 prompt 对照及若干 context 示例 | TSB-AD 子集偏短；延迟高；少量模拟文字背景不代表真实 Trace / release context（Review v9） |
| [AnomSeer (2026)](../../papers/anomseer/notes.md) | 多模态 LLM 生成类别、区间和 reasoning trace；OT 对齐和 RL 优化 | 3,200 个合成训练样本与多 benchmark 比较 | 训练依赖标注 / 合成轨迹；解释 trace 未经外部 cause ground truth 验证，主实验偏单变量（Review v9） |
| [VLM4TS (2026)](../../papers/vlm4ts/notes.md) | 同序列 patch CLIP 表示 nearest-match discrepancy，再经 VLM/LLM 全局走势验证 | 11 个 univariate benchmark 的多尺度 proposals / filtering | F1-max 协议；稠密重复异常可能违反“异常稀有”假设而降 recall；真实业务 metadata 未输入（Review v10） |
| [TimeRCD (2026)](../../papers/time-rcd/notes.md) | 合成预训练 relative context discrepancy，直接预测时间 / 跨变量关系异常 | 16 数据和 contextual synthetic split | 固定 context=5k；context 含异常会污染参照；held-out generator 与真实状态迁移未证明（Review v10） |
| [IMPACT (2026)](../../papers/impact/notes.md) | Validation-risk influence 清理污染标签；参考 normal、seen / unseen heads 做 open-set 检测 | 多种污染 / open-set 设置与 8 个数据集 | 依赖少量异常标签、validation signal；污染构造借用 test anomalies 后隔离；rare valid normal 可能被翻标（Review v10） |
| [KAN-AD (2025)](../../papers/kan-ad/notes.md) | 有限 Fourier KAN 平滑单变量序列，以周期索引和轻卷积做一步预测 | UCR 等单变量数据；污染 / 平滑机制消融 | 平滑可能压制局部真故障；TODS 污染实验属合成 stress test；主文 score 方程有不清楚处（Review v11） |
| [RTdetector (2025)](../../papers/rtdetector/notes.md) | 首轮重建趋势与残差驱动第二 decoder；统计均值 / 方差注入注意力 | UCR、MBA、SMD 等数据和组件消融 | SMAP 等有基线例外；反归一化公式实现需核对；重建趋势不是业务状态识别（Review v11） |
| [IGAD (2025)](../../papers/idempotent-reconstruction/notes.md) | 频域增强、幂等一致性与 target-manifold tightness 限制重建映射 | 15×4 组合中 52/60 VUS-PR 提升，8 组合回退 | 数据集 / 模型调参、成本 / 方差；tight manifold 可能排斥稀有正常状态（Review v11） |
| [ScatterAD (2025)](../../papers/scatterad/notes.md) | 时间点图、latent scattering 与相邻时间一致性；中心偏离+突变分数 | 24 个设置 15 项第一；SWAN 时间偏移及 WADI 强噪声展示指标 / 假设边界 | 图节点是时间而非 service topology；噪声增大时散布比例可反转；score 公式疑点需核实现（Review v12） |
| [COGNOS (2026)](../../papers/cognos/notes.md) | 将 MSE residual 约束为近 Gaussian white noise；ARKS 用 NIS 与 Kalman smoothing 去背景噪声 | 多 backbone / 多集总体提升；单模块和不同指标存在回退 | 作者明确固定 $R$、残差适用范围；分数偏 onset，不保证持续区间 coverage（Review v12） |
| [TeamWork (2026)](../../papers/teamwork/notes.md) | ERI 分 dominant / auxiliary channel，前三周期做 point/segment/period masking 后门控重建 | 8 个基准、role / branch / mask 消融 | ERI 是统计互信息 proxy 而非因果等级；静态 role 和全局 FFT 弱周期边界由作者指出（Review v12） |
| [AnoMamba (2026)](../../papers/anomamba/notes.md) | GSR 以全局上下文重加权 Mamba step-size，并用 multi-scale prior 约束重建 | 8 集上 F1-AF 7/8、VUS-ROC 6/8 第一；去 GSR 后 UTS F1-AF 降低 | SPOT / window 固定；hidden attention 是贡献可视化而非因果解释（§§5.3, 5.8） |
| [FlowFuse (2026)](../../papers/flowfuse/notes.md) | temporal/frequency × clustering/reconstruction 四视角分数由 coupling flow 联合建模 | 18 基准；消融对简单平均约 +8.0% Aff-F1；mixed anomaly 仍困难 | score uncertainty 是 ensemble variance proxy；view 同时失败和业务状态条件化未验证（§4） |
| [Conditional Normalizing Flows (2026)](../../papers/cnf-latent-dynamics/notes.md) | 条件 flow 将序列映为 latent；LG-LDM + MV-KS 检验动态合规性，FIT 诊断训练 | 合成结构异常下 KS 超 NLL 若干指标；真实 leaderboard KS 排名低于 NLL | GOF 对窗口 / 维度 / 训练 FIT 敏感；LG-LDM 不适合所有数据，point anomaly 会被长窗口稀释（§§4–5） |

## 2. 方法分类与技术演进

这些路线并非互相替代，也不构成从 2024 到 2026 的单线性能进步。更有用的分类轴是：**正常性参照放在哪里、用何种异常证据、以及方法是否观察运行上下文**。

### 2.1 多模式、状态与参照建模

- **样本 / 原型 / 聚类参照**：CAPMix 的 DTW center、CrossAD 的 sub-sequence prototypes、Graph-MoE 的 memory experts、TeamWork 的变量角色，分别以窗口形态、跨尺度模式、潜在专家状态和通道依赖压缩正常性；这些原型或记忆多未被标注为真实业务模式（Reviews v3–v6, v12）。
- **频率与时间尺度参照**：MACE 按 service 学 Fourier bases；TFMAE、TriAD、TFC、FlowFuse 将 temporal/frequency（有的再加 residual/curvature）作为互补 evidence。它们扩展观测视角，但频谱变化本身不能说明变化由负载还是故障引起（Reviews v4–v8）。
- **状态适应与相对上下文**：When Model Meets New Normals 在测试期更新；CAROTS 的多正例和 CCM-TAD 的 profile clusters 处理关系模式；TimeRCD 以同序列长程关系作 zero-shot reference；VLM4TS 用同序列其他 windows 作视觉参照。其风险分别包括 pseudo-label contamination、静态结构、context anomaly 污染和异常稀有性假设（Reviews v3, v5–v6, v10）。
- **显式统计动态**：COGNOS 将 residual 当作 white-noise null，Conditional NF 将 whitened latent 定义成特定动态分布。这类方法更明确地陈述可检验假设；适用性依赖校准数据满足假设，且检验拒绝不直接给出业务原因（Reviews v12–v13）。

**演进判断（综合分析）**：论文从“单一 residual / distance”拓展到多视角、关系、在线参照、语义模型和显式统计合规；同时 normality 的表达越来越丰富，但**状态参照的业务命名、切换保护和外部解释验证并没有随模型复杂度自动解决**。

### 2.2 重建、预测、结构关系与鲁棒性

1. **重建 / 预测对齐**：KAN-AD 以 Fourier 平滑预测抑制局部噪声；RTdetector 将首轮重建趋势转为后续关注；IGAD 对正常重建映射加幂等和流形约束；AnoMamba 用全局依赖 reweighting 减少只拟合局部模式；Sub-Adjacent 让正常点从非紧邻上下文重建。它们改善“怎样拟合正常序列”，不等同于“状态是否合法”。
2. **时序和变量关系证据**：CAROTS、GCAD、OracleAD、SARAD、CCM-TAD、Graph-MoE、ScatterAD、TeamWork 等分别使用预测影响、图 / attention / association、时间节点或统计变量作用。术语“causal”“graph”“dominant”须按论文的实际对象理解，除非有 intervention / ground truth 与业务拓扑核验，不推成服务依赖或根因解释（Review v6, v12）。
3. **鲁棒与开集**：CAPMix 面对训练污染和伪异常偏差；Fortifying 给 DTW 威胁下的决策证书；PCRTA 用扰动对比；IMPACT 处理少量异常标签和 contamination；COGNOS 约束噪声并滤波。这些对应不同威胁模型，不能统称“对噪声鲁棒”。证书不等于预测正确，synthetic perturbation 不必然覆盖真实故障，且异常/正常标签污染会改变参照（Reviews v4, v8, v10–v12）。

### 2.3 LLM / VLM 路线

AnomalyLLM 把大模型用作时序 representation teacher；Delving 将数值和图转为 index-aware prompt；AnomSeer 用多模态生成监督和 RL 输出类别 / 区间 / rationale；VLM4TS 将 patch matching proposal 与全局视觉语言验证结合。TimeRCD 是 synthetic relative-context foundation model，不是将任意真实运维文本直接接入 detector。**已展示的是特定表示、prompt、合成训练或视觉核验对 benchmark 的效果；rationale fidelity 和真实业务 context 的安全使用未被这些分数单独证明**（Reviews v9–v10）。

## 3. 专题：正常业务波动与真实故障

### 3.1 多种正常运行状态如何建模？

**论文主张 / 机制已经出现**：

- 按模式分组或保存代表：CAPMix center、CrossAD 原型、Graph-MoE memory、TeamWork dominant/auxiliary role。
- 显式正常模式多样性：CAROTS 的 multiple semantic positives、MACE 的多 Fourier bases。
- 在线适配或序列内参照：When Model Meets New Normals、TimeRCD、VLM4TS、IMPACT。
- 条件 / 动态参照：服务 identity-conditioned MACE、COGNOS per-channel residual calibration、CNF latent dynamics。

**[实验支持]** 这些机制分别有消融或 benchmark 结果，但实验多只证明该机制改变检测分数或平均指标。WMMNN / TimeRCD / VLM4TS 等相关证据与各自伪标签、context 稀有性、context contamination 风险同时存在；TeamWork 明确指出 ERI role 是 static，CNF 明确指出 LG-LDM 不适合所有数据（Reviews v3, v10, v12–v13）。

**[综合分析]** “多原型 / 多频谱 / 在线适配”已经是已有研究方向，不能笼统宣称未解决。更具体的待验证问题是：系统是否能将 reference 与**外部可核验的 workload、发布、租户、业务时段**关联；当合法 state transition 与异常并发时，是否能分开保留各状态 normality 与异常敏感性；rare-but-valid 状态是否获得可接受的 group-wise false alarm。

### 3.2 目前怎样区分波动和故障？

当前论文采用的是偏离证据，而非普适的来源判别器：

- 预测 / 重建误差表示样本难以由学习到的 normality 解释；
- shape / frequency / curvature / temporal context 表示局部或周期模式偏离；
- cross-channel association / Granger-style score 表示变量关系改变；
- NIS、残差白化、MV-KS 表示预设统计假设被拒绝；
- RCD、视觉语境、validation influence 表示相对参考集合不一致或训练样本可疑。

这些证据能帮助检测“发生了变化”，但**状态切换本身也会使模型 reference 改变或统计假设失配**。CAROTS / GCAD 等关系分数尚未与真实故障 cause intervention 对照；COGNOS 的 NIS 会对结构突变响应，却不自带 workload 语义；CNF reject latent compliance 也只说明相对规定动态偏离；attention / score visualizations 不等于 root cause（Reviews v3, v6, v12–v13）。

### 3.3 是否只抑制噪声？是否解释变化来源？

不是所有论文都只是抑噪：因果 / 预测关联、对比关系、异常频谱、latent GOF、开放集 influence 和多视角分数都构造了更丰富的异常证据。COGNOS 最直接把背景噪声作为近似白噪声建模并抑制；Fortifying 的对象是指定 DTW 扰动鲁棒性；KAN-AD 关注平滑拟合；其它方法有的隐式过滤扰动，有的检测关系破坏。

但“比低通滤波更结构化”不等于“解释了业务原因”。来源解释至少需要与外部事件 / workload 状态、Trace 路径、拓扑变更或故障注入 ground truth 对齐，并评价解释稳定性与忠实性。AnomSeer rationale、AnoMamba hidden attention、TeamWork ERI、ScatterAD graph、FlowFuse view disagreement、CNF latent compliance 等仍需此类外部验证（Review v6, v9, v12–v13）。

### 3.4 是否真正使用 Metric、Trace、负载和运行上下文？

**当前证据边界**：33 篇中，多数直接以数值时序、频谱、模型 score 或图化数值表征为核心。存在 context-related designs：MACE 有 service identity，Delving 尝试少量文字背景，VLM4TS 由视觉模型参考序列形状，TimeRCD 生成式上下文标签关注 temporal / cross-variate relations，CAROTS 将外生变量作为可能的后续方向。但这不等于使用真实生产 Trace/span、release 事件、用户请求负载或 deployment metadata 的成套条件评估。Reviews v3–v10 多次把真实 Trace / workload / release-conditioned validation 记为 open。

## 4. 哪些研究问题仍缺充分实验证据？

下表把“研究空白”写成有出处的**实验缺口**，不主张没有任何方法触及相关概念。

| 证据缺口 / 研究机会 | 已有工作与直接边界证据 | 建议的可证伪实验问题 |
| --- | --- | --- |
| **负载 / 发布状态切换与故障并发** | WMMNN 在线伪正常更新可能污染；TimeRCD context anomaly 可能污染 reference；TeamWork static ERI、MACE 静态服务 Fourier basis、CNF LG-LDM 都有状态适配边界；Reviews v3–v13 均未发现统一四格并发矩阵。 | 固定训练正常期，分别测正常状态切换、仅故障、状态切换+故障、未见合法状态；给每类标注 state 和 fault onset，报告 per-state FPR、并发故障 recall、检测 delay 和恢复时间。 |
| **真实上下文带来的来源归因** | 多篇关系模型和 attention 结构没有 topology / cause ground truth；Delving 的文字 context 样本有限，CAROTS、GCAD、OracleAD 的结构代理未全面验证物理因果（Reviews v6, v9）。 | 将 Metric 与 Trace/span、release / workload / topology 对齐；通过真实 incident 或注入故障检验 top-k cause、路径忠实度和跨负载稳定性；同时单独报告检测与归因。 |
| **多状态 normality 与 rare-normal 安全** | CAPMix 单中心、IMPACT rare-normal label flips、ScatterAD 全局散布参照受噪声影响、TeamWork static role 和 CNF 单一 dynamics 指向风险（Reviews v3, v10, v12–v13）。 | 对合法低频 / 新状态分组报告 false alarm 与覆盖；用状态 holdout 与出现频率梯度检查 prototype、memory、adaptation 能否记住状态；验证在线更新是否把 fault 写入 normal memory。 |
| **事件持续区间 vs onset 的目标冲突** | COGNOS 作者称 score 偏 onset；ScatterAD Aff-F 对 1 timestep shift 敏感；不同论文使用 Aff-F、VUS、PA-F、oracle threshold 等协议（Reviews v7, v12）。 | 统一事件级 recall、onset delay、duration coverage、边界容差、固定 FPR；报告 point-adjustment 前后差异，禁止用测试标签选择部署阈值。 |
| **鲁棒性与假设失配的可比 protocol** | Fortifying 的证书针对 DTW radius；PCRTA/KAN-AD/IGAD 使用各自扰动或噪声协议；COGNOS 固定 $R$ 有局限；CNF FIT / window / dimension 敏感，FlowFuse view 存共同失效可能（Reviews v4, v8, v11–v13）。 | 同一 benchmark 控制 measurement noise、异方差、相关噪声、时间扭曲、训练污染、state drift、共同 view failure；报告对检测性能和校准的分层影响，区分 certified invariance 与 empirical robustness。 |
| **不确定性和阈值在部署运行点下的可靠性** | FlowFuse variance 只是分歧 proxy；CNF GOF 依赖 FIT 与样本数；COGNOS calibration quantile、多个论文 test-best threshold 设置不可直接比（Reviews v7, v10, v12–v13）。 | 只用 validation/normal data 固定阈值，报告 reliability / calibration、固定误报预算下召回、跨实体与跨状态迁移，并测试 uncertainty 是否能筛出真正可纠正的 ambiguous cases。 |
| **LLM/VLM 解释是否忠实且可安全过滤** | AnomSeer 生成 reasoning trace、VLM4TS 进行全局 verify、Delving 使用自然语言 prompt，但 rationale / filtering 与真实故障根因的忠实度验证不足；稠密异常会挑战稀有性先验（Reviews v9–v10）。 | 对解释进行 counterfactual / evidence deletion 测试；加入 dense anomaly、合法周期切换和 workload metadata 冲突，测漏报、false verification、API latency 与 abstention。 |

## 5. 研究问题状态总表

| 问题 | 状态 | 33 篇范围内的综合结论 |
| --- | --- | --- |
| 多种正常状态如何建模？ | **部分回答** | prototypes、memory、frequency bases、test-time adaptation、relative context、role branches、noise models 和 latent dynamics 均已有方法；业务状态语义、罕见状态安全与可验证迁移尚不充分。 |
| 正常业务波动与真实故障如何区分？ | **未解决** | 现有工作提供多种统计 / 结构偏离证据，但没有统一证明异常来源是故障、合法 workload transition 或其并发。 |
| 方法只是抑噪吗？ | **部分回答** | 很多已超出噪声抑制，使用形态、关联、频域、latent dynamics、open-set 等证据；具体证据的业务来源解释仍开放。 |
| 是否使用真实 Metric、Trace、workload、release？ | **未解决** | 论文以 numeric time series 为主；上下文相关原型存在，但缺少真实 Metric–Trace–workload–release 的统一条件实验。 |
| 如何处理正常负载变化与真实故障同时发生？ | **未解决** | 尚无系统并发矩阵、统一 FPR / delay 指标和状态安全基线。 |
| 哪些方法思路已经提出？ | **部分回答** | 第 1 节和 §2 列出代表路线；未来贡献要限定更窄的机制差异和新证据，避免把 multi-normality、causal TSAD、test-time adaptation、时频融合或 robust detection 本身重新宣称为空白。 |

## 6. 后续研究设计建议（基于上述缺口）

把“是否在变”和“为什么变”拆成两个可评估输出：第一阶段做状态条件化的异常检测；第二阶段在 Metric、Trace、拓扑和变更事件上做来源归因。用按时间隔离的训练 / validation / test，并保留合法状态 holdout；分别控制正常转换、故障、并发、测量噪声和训练污染。统一报告固定 validation FPR、per-state false alarm、event recall / delay / duration coverage、未见状态迁移及 attribution fidelity。与简单 robust baseline、状态 / memory 方法、结构关系方法、score fusion 和 latent GOF 同台比较；拆开“模型更稳”“阈值更好”“解释更准”三个结论。

该建议是**跨论文分析推断**，不是已完成实验证明的最佳方案；具体 benchmark、标签和线上约束仍需领域确定。

## 7. 阅读与引用路径

- 最近批次机制差异：[Knowledge Review v13](knowledge-review-v13.md)。
- 按技术主题找文献：[TSAD knowledge query guide](../guides/tsad-knowledge-query-guide.md)。
- 全部论文逐篇笔记与卡片：见 [INDEX 的 Papers 栏](../../INDEX.md#papers)。
- 原始 PDF：见 [sources/papers/tsad-2024-2026](../../sources/papers/tsad-2024-2026/)；PDF 由 `.gitignore` 管理，不通过 Git 同步。
