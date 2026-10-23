# Knowledge Review v12：TSAD batch 10 — 表征散布、残差白化与变量角色

## Scope and Evidence Labels

本次评审第 28–30 篇，累计 **30/33** 篇完成实际 PDF 精读：

- [ScatterAD](../../papers/scatterad/notes.md)：时间节点图上的 latent scattering、时间一致性与双 encoder 融合。
- [COGNOS](../../papers/cognos/notes.md)：MSE residual engineering + adaptive Kalman smoothing。
- [TeamWork](../../papers/teamwork/notes.md)：ERI dominant / auxiliary channel 分工与 period-aware masking。

本 Review 以每篇 PDF 笔记和 Reviews v3–v11 为证据来源；**[论文主张]**、**[实验支持]**、**[跨论文分析]**分开写。三篇任务与指标不同，不能依据单一数字排成同协议的总榜。

## 1. 三种不同的 normality / anomaly reference

| 论文 | 表示或统计假设 | 异常证据 | 关键适用条件 |
| --- | --- | --- | --- |
| ScatterAD | 正常的 temporal-topological latent embedding 更靠近散布中心；邻接 latent 突变也值得关注 | 中心偏离项 + 相邻时刻不一致项（§§3.3–3.4, Eqs. 6–10） | 训练表示可中心化、异常能产生散布 / latent transition；固定时间 lag graph，公式需与实现核对 |
| COGNOS | 正常 MSE residual 可近似 Gaussian white noise；异常是 white-noise null 下的 structural break | NIS 统计检验 + Kalman posterior structural signal energy（§4.2, Eqs. 10–16） | MSE reconstruction residual、normal calibration、相对稳定的 per-channel noise scale；score 偏 onset |
| TeamWork | 每个 channel 的统计 explanatory power 不同； dominant channel 更适合重周期 modeling，auxiliary 提供补充线索 | 多角色交互后的重建误差（§§4.1–4.4, Eqs. 1–14） | 静态 ERI role 与有可提取的全局周期；role 依据统计互信息而非业务因果 |

这三篇放置检测信息的位置不同：ScatterAD 改 latent representation 几何，COGNOS 改输出 residual 的统计性质并后接滤波，TeamWork 改变量选择 / 分工和时间尺度建模。共同点是用“更合适的参考 / 约束”改善异常分数，但 reference 分别是中心、噪声 null、相对变量角色，不能笼统归为结构建模或鲁棒降噪。

## 2. 关键实验支持和失败证据

### ScatterAD

- **[实验支持]** 六个多变量 benchmark、12 类指标；作者报告 24 个主文数据集-指标设置中 15 项第一，并称 Aff-F、AUC-ROC 在六集最佳。（§4.2, Table 1）
- **[失败 / 评估证据]** NIPS-TS-SWAN Aff-F .038，PA-F .736、AUC-ROC .792、AUC-PR .716；作者以不规则 burst 与 metric localization sensitivity 解释。其 synthetic shift test 显示 SWAN 的 prediction shift 1 点可使 Aff-F 从 1.000 降至 .065，而 MSL 仍为 1.000。（Appendix F, Table 9）
- **[噪声边界]** WADI 的异常/正常 scattering ratio 在 test Gaussian noise $\sigma=0$ 为 1.49，$\sigma=1$ / $2$ 时为 .83 / .82，说明强噪声下该表征假设可反转。（Appendix D, Table 7）
- **[实现疑点]** Eq. (10) reciprocal minimum-distance 与“距离中心越远越异常”的解释不显然一致；Eq. (6) 负 cosine 文本和 Eq. (9) 总体最小化、Eq. (8) EMA 符号亦需按官方实现复核。（§§3.3–3.4）

### COGNOS

- **[实验支持]** KAN-AD backbone MSL Std-F1 .8115→.9165、Aff-F1 .5360→.9157；TimesNet SWAN Std-F1 .7371→.8313、Aff-F1 .1961→.5249。（Table 1）
- **[指标反例]** KAN-AD PSM 的 Std-F1 / Aff-F1 明显上升，但 R-A-R .7005→.6799、VUS-ROC .6846→.6624、VUS-PR .4724→.4432 下降；完整区间 coverage 与 onset sensitivity 并不等价。（Table 1, Appendix D.1）
- **[消融支持 / 失败]** 联合 GWNR+ARKS 普遍更稳，但 GWNR-only 在 GECCO Std-F1 .4738→.3440，ARKS-only 的 MSL Std-F1 .8115→.8083 略降。说明白化残差需要与 scoring filter 协同，单独改变 residual statistics 未必提高可分性。（Table 3）
- **[协议边界]** 使用 normal training residual 校准 ARKS；每个数据集 shared global quantile threshold 从 98%–99.5% 范围选择，而不是对每个 model 做 F1-max。（Appendix D.2）
- **[作者指出]** fixed $R$ 不适用于 state-dependent heteroscedasticity；不适合没有 MSE residual 的检测器；异常 score 偏 onset，不保证段覆盖。（Limitations, p.9）

### TeamWork

- **[实验支持]** 在 GECCO、Genesis、CalIt2、Creditcard、MSL、SMAP、PSM、SMD 八个数据集报告 Aff-F / AUC-ROC 强结果；作者在统一重评协议中称两个指标均超越对照。（§5.2, Table 1）
- **[消融支持]** Credit / Genesis / SMD 的三集平均 Accuracy：full .927；CI .864、CD .899、CC .872；去 dominant .673、去 auxiliary .902、random roles .867。角色划分和两个分支均有贡献。（§5.3, Table 3）
- **[消融支持]** 三种 mask 单独使用的平均 Accuracy .911 / .918 / .915，无 mask .890，full .927；多粒度 mask 的组合有增益。（Table 3）
- **[作者指出]** 静态 ERI role 可能在不同 operating stage 翻转；全局 FFT 对弱周期 / 局部非平稳序列可能失效。（Limitations, p.14）

## 3. 通道依赖、图和“业务拓扑”的边界

- **ScatterAD 的 graph**：节点是时间戳，edge 连滞后时间点（实验 $\tau=2$）；GAT 表示的是时间节点关系，不是服务依赖图、设备连接拓扑或业务因果图。（§3.2）
- **TeamWork 的 role**：节点 / 被选择对象是变量通道，ERI 近似 $I(X_{-i};x_i)$，表示对其它通道统计不确定性的减少。它能对变量建模资源分配，但不说明某变量是物理因果驱动因素。（§3.2–4.1）
- **COGNOS 的 channel filter**：ARKS 按通道建标量状态空间过程。理论附录指出其与完整多变量 KF 等价依赖残差 covariance diagonal / channel independence；相关噪声会挑战该前提。（Appendix A.2）

**[跨论文分析]** “topological”, “dominant”, “channel-wise”都不自动等同于 AIOps service topology、cause ranking 或跨指标传播路径。要支撑这些语义，需要将学到的节点 / 变量 / innovation 与物理拓扑、Trace 或注入根因对照，而不仅比较预测分数。

## 4. 多种正常状态与正常波动区分

- **ScatterAD** 用一个全局散布中心、固定滞后图与连续性 loss；没有为每个负载 / 发布 / 控制模式分建中心。高维 WADI 噪声例外也说明“异常更散”并非在所有噪声条件都成立。
- **COGNOS** 用 normal residual autocovariance 确定每个 channel 的滤波模式和固定噪声参数；NIS 对分布突变敏感，但不能判断突变是合法状态切换还是故障。持续新状态的 innovation / score 可能衰减，符合作者 onset 取向，却不能代替新状态识别。
- **TeamWork** 用全局统计 ERI 与 FFT period 构成参照；它允许 dominant / auxiliary 两条分支，但 static roles 可能错过运行阶段切换，FFT 也可能漏局部非周期变化。

因此，在本批中能够被论文直接支持的是：多视角 / 多角色 / residual null modeling 改变 benchmark 异常分数；尚未支持的是把正常业务波动识别为特定 workload / release 状态，并在状态切换期间仍保持未知故障召回。该缺口与前 27 篇已见的 spectrum / memory / adaptation / context-relative normality 结果一致：多种正常参照已有不少方案，业务状态语义和安全条件化仍是缺证据环节（Reviews v3–v11）。

## 5. 噪声抑制、异常持续性和来源解释

1. **ScatterAD** 降低 latent center / temporal shift 之外的正常表征变异；Gaussian perturbation 是合成 stress test，且 WADI ratio 会反转。没有 workload 归因。
2. **COGNOS** 明确把背景 residual 作为白噪声并用 Kalman filter suppress；它比简单平滑多了 null hypothesis / NIS 检验，但分数对 onset 敏感，持续异常会因新稳态而衰减。来源 attribution 仍然缺失。
3. **TeamWork** 用周期级遮挡和变量角色改变 reconstruction evidence；没输出 ERI 是 workload、设备原因还是偶然相关的解释证据。

**[跨论文分析]** 与 KAN-AD、RTdetector、IGAD 一起看，这些论文对“何种形态可重构、何种 residual / embedding 偏离正常”提供具体模型；“为什么发生波动”仍需用外部事件、Trace / 拓扑或控制实验去回答。尤其要把**检测分数稳定**与**对异常来源解释正确**区分开。

## 6. 研究空白（限定已读 30 篇）

1. **条件化的 normality 与 state transition safety**：出现多中心、动态适配、关系模式、role branches 和状态噪声参数，但没有统一检验正常状态切换、未见合法状态、仅故障和切换+故障并发。（WMMNN、MACE、TimeRCD、IMPACT、RTdetector、IGAD、TeamWork、COGNOS notes；Reviews v3–v11）
2. **统计角色 / 图结构的语义校验**：ERI、lag graph、attention、latent scatter 等提供数值关联，缺少与服务拓扑、Metric–Trace 对齐、发布 / 负载及注入根因的忠实性指标。（ScatterAD §§3–4; TeamWork §§4–5; CAROTS / GCAD / OracleAD / SARAD notes）
3. **异常起点与区间定位目标冲突**：COGNOS 明确 onset focus；ScatterAD 的 Aff-F 对微小偏移敏感；多个既读方法使用 PA-F / test-best threshold。需要统一报告 detection delay、event recall、duration coverage、boundary tolerance 和固定误报预算。（COGNOS §6; ScatterAD Appendix F; Quo Vadis / TSB-AD notes）
4. **异方差、跨变量噪声相关与状态漂移**：COGNOS 固定 $R$ 及 channel-wise filter；ScatterAD WADI Gaussian noise ratio 反转；TeamWork static roles / FFT 全局周期。应在相关噪声、多负载和跨状态噪声 floor 下分层报告误报 / 漏报。（COGNOS Limitations / Appendix A.2; ScatterAD Appendix D; TeamWork Limitations）
5. **异常稀疏 / 不平衡 / rare-normal safety**：ERI 按总体互信息分主次，scattering center 按整体正常性紧缩，白噪声假设将高 NIS 归为结构异常；罕见但合法状态可能成为异常。现有论文需补 group-wise false alarm 和各状态覆盖。（TeamWork §4.1; ScatterAD §3.3; COGNOS §4.2; IMPACT Appendix I）
6. **阈值 / 预处理复现透明度**：COGNOS 的全局 quantile 搜索区间、TeamWork threshold-ratio 集、ScatterAD Eq. (10) 方向与 Aff-F boundary sensitivity 都需在代码和数据拆分层面验证。（各自 notes）

## 7. TSAD 问题进度（30 篇范围）

| 研究问题 | 状态 | 当前结论 |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | spectrum / prototypes / memory / TTA / context / trends / fixed points / channel roles 已提出；状态语义标注与安全转移仍缺。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | latent scatter、NIS、ERI、重建 / 关系分数可区分统计偏离；没有依据说明是正常状态改变还是故障。 |
| 是否仅抑噪，是否解释波动来源？ | Partially Answered | 多种结构性证据超出简单降噪，但根因来源 / 因果解释需要外部验证。 |
| 是否使用 Metric、Trace、workload、release？ | Open | 30 篇 TSAD 主体仍以数值时序为输入，真实 Trace / release / load 条件化验证不足。 |
| 正常状态变化和故障并发如何处理？ | Open | 无系统真实控制矩阵；COGNOS NIS、TeamWork static roles 和 ScatterAD center drift 是值得验证的风险。 |
| 何种评估空白最明确？ | Partially Answered | onset / duration coverage、boundary tolerance、fixed FPR / validation-only threshold、跨状态 noise 和 rare-normal group 指标仍不统一。 |

## 8. 下一批（31–33）

最后三篇按生成 / 全局依赖表征阅读：

1. **AnoMamba**：selective global dependency modeling 与 reconstruction alignment。
2. **Multi-View Ensemble via Coupling Flows**：多视角 coupling-flow 集成。
3. **Conditional Normalizing Flows**：latent-space inductive biases 与条件流密度建模。

完成后以 33 篇最终笔记和各批 Reviews 为证据生成综合全景、方法演进、业务波动 / 故障区分专题、研究空白与检索指南。
