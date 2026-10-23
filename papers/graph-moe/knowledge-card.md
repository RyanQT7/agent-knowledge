# 知识卡片：Graph-MoE

> 标签：**[作者主张]** 指论文提出的机制 / 结论；**[实验支持]** 指表格、消融或图示的实际证据；**[分析推断]** 指本文的跨论文归纳或研究假设。

## 1. Research Scenario

- **[作者主张]** 无监督多变量 TSAD：联合建模多个实体间的时序依赖，对窗口估计条件密度。（PDF §§1, 3）
- **[实验支持]** SWaT、WADI、PSM、MSL、SMD 五个基准；主实现依托 conditional normalizing flow。（PDF §4, Table 1）

## 2. Core Challenges

- **[作者主张]** 多层 GNN 捕获不同邻域距离，但只用最后一层会丢掉浅层 / 中层表示；所有实体都用同一种聚合深度也可能不合适。（PDF pp.1–3, Fig. 1）
- **[作者主张]** 当前局部关系需结合全局历史特征来动态选择不同图层 expert。（PDF pp.2–5, Fig. 3）

## 3. Existing Limitations

- **[作者主张]** 既有 GNN TSAD 通常只使用最后层图输出。（PDF §§1, 3）
- **[分析推断]** 论文未把潜在 graph / memory 表征与可命名业务态、workload、Trace 或 service topology 对齐。

## 4. Core Idea

- **[作者主张]** 把每个 GNN 深度变成一位 expert，用当前 RNN 表征对齐各层输出，再用记忆增强路由器生成各层混合权重，接入条件 flow 进行异常检测。（PDF §3, Eqs. 7–16）

## 5. Technical Innovations

1. **[作者主张]** 每个窗口用 self-attention 建动态加权实体图 $A^c$。（Eq. 5–6）
2. **[作者主张]** 时空图更新同时使用邻接聚合 $A^cH_t^{l-1}W_1$ 和历史项 $H_{t-1}^{l-1}W_2$。（Eq. 7）
3. **[作者主张]** 每个图层由独立 expert cross-attend 当前 RNN 时序特征并得到对齐输出。（Eq. 9–10）
4. **[作者主张]** MAR 用残差注意力与 forget / input gates 更新 $M^t$，随后 $R=\mathrm{Softmax}(\phi_R(M^t))$。（Eq. 12–16）

## 6. Key Mechanisms

- **[分析推断]** MoE 主要补充“同一窗口中选哪种图传播范围”；MAR 让选择权重接收当前和历史 latent 表征；它不显式估计状态标签或业务状态概率。
- **[作者主张]** Graph-MoE 可作为插件集成到图式 MTSAD。（§1, Table 4）

## 7. Experimental Evidence

- **[实验支持]** Table 1 五次运行 AUROC：SWaT 87.2±1.3、WADI 94.2±0.8、PSM 88.0±0.7、MSL 72.1±1.1、SMD 93.3±5.6；高于表中 MTGFlow 对照。（PDF p.6, Table 1）
- **[实验支持]** SWaT / WADI 上 3 层优于 4 层；MoE 与 MAR 同时启用达 87.2 / 94.2，分别高于基础 85.5 / 92.2。（PDF pp.6–7, Tables 2–3）
- **[实验支持]** SWaT 插接 GANF、MTGFlow、USD 后 AUROC 分别提升 79.8→82.6、84.8→87.2、90.2→92.3。（PDF p.7, Table 4）
- **[证据边界]** SWaT 的原 test 序列据正文再切成训练 / 验证 / 测试；主指标是 any-point-positive window AUROC，不等于固定线上告警表现。（PDF p.5, §4）

## 8. Limitations

- **[作者未明确讨论]** 论文没有单独限制章节或 workload / Trace 条件化实验。
- **[分析推断]** latent memory 可能总结历史，但论文没有证明其分离日夜、高峰、发布等动态业务状态；无 memory 污染与异常并发负载切换实验。
- **[实验设置边界]** 需复查 SWaT 测试子集重切分、z-score 统计范围及 window-level AUROC；不能将现有数字视作严格跨状态泛化保证。

## 9. Research Opportunities

- **[分析推断]** 将 memory router 与显式 workload / release / Trace 等上下文对齐，评估隐式路由与业务状态条件化的差异。
- **[分析推断]** 对异常写入 memory、状态更新回滚和新正常冷启动设计在线评测。
- **[分析推断]** 将层路由变化与真实实体依赖图、跨指标机制变化及告警解释核验。

## 10. Related Papers

- **MACE**：服务条件的静态频域正常子空间；Graph-MoE 用窗口图与潜在历史路由，均未将业务状态语义作为输入。
- **CAROTS**：显式讨论跨变量 Granger 预测关系；Graph-MoE 的 learned attention graph 不是因果图。
- **CCM-TAD**：其 causal 指因果遮罩的时间信息流；Graph-MoE 的动态图是潜在相关结构。
- **CrossAD**：以跨尺度时间关系和窗口原型为核心，Graph-MoE 以图深度 / 实体邻域为核心。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[Graph-MoE PDF](../../sources/papers/tsad-2024-2026/2025/AAAI/Graph_Mixture_of_Experts_and_Memory_augmented_Routers_for_Multivariate_Time_Series_Anomaly_Detection.pdf)
