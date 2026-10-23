# 知识卡片：CCM-TAD

> 标签：**[作者主张]** 为论文提出的机制或结论；**[实验支持]** 为表格、图或消融实际支持的内容；**[分析推断]** 为知识库的比较判断或待验证方向。

## 1. Research Scenario

- **[作者主张]** 多变量时序在线异常检测：用当前 / 历史窗口重建最新观测，并把重构误差转换为顺序告警证据。（PDF §§3.1, 3.4）
- **[实验支持]** SWaT、WADI、PSM、SMD、MSL、SMAP 六个基准；作者仅面向 multivariate，不适用于单变量。（Table 1; Appendix M）

## 2. Core Challenges

- **[作者主张]** 普通 MLP mixer 时间维全窗口混合可造成未来信息泄漏；统一 embedding 会混合不同相关结构；逐点分数忽略异常持续性。（PDF §§1, 3）
- **[作者主张]** 在线异常评分既需避免未来 test observations，也需要聚合连续的异常证据与校正边界。（§3.4; Appendix L）

## 3. Existing Limitations

- **[作者主张]** MLP mixer 缺少时间因果掩码；多通道若相关性异质，联合投影可能引入伪相关；单点阈值分类忽略前后时间联系。（PDF §§1, 3）
- **[作者明确限定]** 本文所谓因果仅为时间信息流因果，不发现 Granger / 通道间因果或根因变量。（Appendix M）

## 4. Core Idea

- **[作者主张]** 训练期按 Pearson 相关 profile 做 spectral clustering，每簇独立 embedding；causal mixer 做单向时间特征混合；验证 MSE 估计异常尾概率并累积证据，达到门限后输出事件片段。（PDF §§3.1–3.4）

## 5. Technical Innovations

1. **[作者主张]** 以相关 profile cosine graph 的 Laplacian 谱聚类通道；零相关 profile 通道单独成簇。（§3.2.1, Eqs. 6–9）
2. **[作者主张]** 每簇独立 embedding，并按通道数分配总维度。（§3.2.2, Eq. 10）
3. **[作者主张]** 两层 temporal linear mixer 均用三角掩码，并以 $1/j$ 调整累积输入数；feature mixer 仍为标准两层 MLP。（§3.3, Eqs. 11–13）
4. **[作者主张]** validation error empirical p-value → $\beta_t=\log(\alpha/(p_t+\epsilon))$ → 带连续负证据 reset 的累积 $s_t$ → onset/offset backtracking。（§3.4, Eqs. 14–17）

## 6. Key Mechanisms

- **[分析推断]** clustering 是静态训练期通道分组，不是实时状态切换器；causal mask 防止时间维未来泄漏，不表示跨通道因果发现。
- **[作者主张]** sequential score 通过累积异常证据改善连续事件覆盖，boundary correction 尝试补偿越阈检测的起止偏差。
- **[实现边界]** validation reference 和固定部署参数支持因果在线算分；但论文 Best-F1 定义在测试标签上 joint sweep $\alpha,h$，该表值是有标签阈值选择的 oracle 结果。（Appendix F Eq. 24; Appendix L）

## 7. Experimental Evidence

- **[实验支持]** Best-F1：PSM .716、SWaT .883、WADI .761；多实体协议 i / ii / iii 下 MSL .370/.613/.638，SMD .300/.612/.602，SMAP .389/.529/.551。（PDF p.7, Table 2）
- **[实验支持]** sequential score + boundary correction 相对 point-based 在多数据集提升，如 MSL F1 .557→.638、PR-AUC .339→.610；PSM F1 .657→.716。（p.8, Table 4）
- **[实验支持]** clustering 带来的 NN-sep 增益从 SWaT +39.11%、WADI +3.83% 到 PSM +0.06%，效果有明显数据依赖。（p.8, Table 6）
- **[实验支持]** 结果在 VUS-ROC 并非全面占优；计算量低于 SensitiveHUE Online，但平均延迟更高。（Appendix H, I, Tables 10, 12–13）

## 8. Limitations

- **[作者明确]** 不学习跨通道 Granger 因果、不定位异常通道；不适用于 univariate TSAD。训练污染可能降低性能。（Appendix M; §3）
- **[实验边界]** Best-F1 对测试标签扫 $\alpha,h$，在线表述不应与无标签阈值性能混为一谈。（Appendix F）
- **[分析推断]** clustering 根据训练期静态相关 profile 建立；未把负载、Trace、发布等运行上下文作为输入。论文仅考察部分 correlation shift，不足以证明剧烈状态迁移和故障并发鲁棒性。
- **[实验支持]** PSM 的 NN-sep 聚类前后只变化 0.06%；并非所有数据上 cluster module 都显著拉开表示距离。（Table 6）

## 9. Research Opportunities

- **[分析推断]** 将 correlation profile 分组与外部 workload / service graph / Trace 一起建模，判断合法状态切换与因果结构故障的差别。
- **[分析推断]** 固定部署前阈值报告 PR-AUC、事件 F1、告警延迟与误报周期，并对 test-label threshold sweep 单独作为 oracle 上界。
- **[分析推断]** 测试间歇性、低强度及与高峰负载并发的故障，量化累积证据的延迟 / 段合并效应。

## 10. Related Papers

- **CAROTS**：显式用估计 Granger 关系作增强和检测；CCM-TAD 明确不是跨变量因果发现。
- **Graph-MoE**：动态窗口图 + GNN 多跳 expert routing；CCM-TAD 用训练期 correlation profile clustering + cluster-wise embedding。
- **When Model Meets New Normals**：推理期更新以适应新正常；CCM-TAD 在线推分但不更新模型与验证误差 reference。
- **TFC**：单变量 curvature / frequency 多视角；CCM-TAD 多变量通道结构和顺序证据整合。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[CCM-TAD PDF](../../sources/papers/tsad-2024-2026/2026/ICML/Cluster_Aware_Causal_Mixer_for_Online_Anomaly_Detection_in_Multivariate_Time_Series.pdf)
