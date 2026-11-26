# 六篇 Benchmark 笔记的独立阅读反馈

- feedback_id: feedback-benchmark-paper-reading-20261126
- task_type: research
- skill_name: paper-reading
- skill_version: b01d766（正式版基线）
- evidence: 用户与 ChatGPT 逐篇对照 PDF 和 2421799 的笔记。79dde6f 记录此前的版本核对经验。
- failure_signature: 笔记篇幅和形式改善后，仍遗漏影响论文结论的关键机制、对照和证据边界。
- expected_behavior: 以科研问题和主要贡献决定阅读深度，核对版本、案例、指标和结论边界。
- reproducibility: 多篇出现同类遗漏，尚未独立复跑。
- status: candidate
- recorded_at: 2026-11-26

以下为用户提供的完整反馈。分数是主观笔记质量评价，不是论文评分或受控模型实验结果。

## RCABench（7.8/10）

- R01：遗漏 Type I、II、III 故障分类及现有数据集质量审计结果。
- R02：SimpleRCA 的具体实现及研究价值解释不足。
- R03：遗漏 SLI 门禁对灰色故障、部分故障等的筛选偏差。
- R04：遗漏传播距离和可观测性缺失两个 Benchmark 难度维度。
- R05：未明确区分层级根因标签与完整故障传播路径标签。
- R06：动态工作负载的状态机机制解释不够准确。
- R07：遗漏预热、数据采集、环境隔离和训练测试划分。
- R08：RCA 算法失效模式分析不完整。
- R09：部分原文定位与正式发表版本不一致，需核对实际论文版本。
- R10：缺少完整的真实故障构建或诊断案例。

用户对照 FSE 正式发表版本，原笔记可能使用 arXiv v2。应先判断版本差异。

## NIKA（7.8/10）

- N01：遗漏 Regular Traffic 与 Incident-triggering Traffic 的设计价值。
- N02：参数化任务构造和复合故障机制解释不足。
- N03：未充分利用 Fig. 3 的 DataCenterIncast 真实任务构造案例。
- N04：遗漏 Boolean Mask 与混淆矩阵评分机制。
- N05：Agent 工具使用及推理行为的实验分析不够深入。
- N06：AAL 权限控制与可观测性设计价值未充分解释。
- N07：遗漏 Diagnosis Agent 与 Submission Agent 两阶段工作流。
- N08：需要区分框架支持的评价能力与论文实际报告的实验结果；主动探测和 shell 工具也不能简单概括为严格只读。
- N09：同版本论文中存在多处章节及图表定位错误。
- N10：遗漏 Batfish 安全修复验证的未来研究方向。

## OpenRCA（7.8/10）

- O01：未明确数据来自历届 AIOps Challenge。
- O02：工程师数据校准的具体流程解释不足。
- O03：遗漏只验证根因组件遥测、剔除根因异常不明确案例可能造成的选择偏差。
- O04：RCA-Agent 的 Controller/Executor 交互协议、状态复用与错误恢复解释不足。
- O05：遗漏模型错误处理能力对 Agent 性能的影响。
- O06：遗漏随机基线校正及 Component、Time、Reason 三个字段的难度分析。
- O07：未充分展开 Fig. 7 中 Tomcat01 定位正确、故障原因错误，但仍获得任务正确得分的案例。
- O08：未综合理解 CoT 与多轮 Agent 调查的实验结果，应区分增加推理文本和获取新证据。
- O09：Balanced/Oracle Sampling、分钟采样方式及不同系统的遥测模态介绍不够准确。
- O10：部分章节定位、模型配置和实验设置遗漏。

OpenRCA 标签可靠性与 RCABench 复杂故障代表性的权衡是研究假设。

## CTBench（8.2/10）

- C01：遗漏固定 DeepSeek-V4-Pro 底层模型的 Harness 对照实验。
- C02：遗漏 RCA Triplet IoU 和 Path Sequence IoU 结构一致性评分。
- C03：遗漏层级故障类别相似度及最大权重二分图匹配。
- C04：遗漏拓扑感知节点相似度的计算及实验分析。
- C05：Metadata 只介绍定义，缺少实际分布及难度分析。
- C06：O2→O1 消融未完整比较四个 Agent 的能力差异。
- C07：遗漏 Evidence F1 及其与 Evidence Coverage 的区别。
- C08：专家筛选成本、标签分布及故障类别实验分析不足。
- C09：遗漏配对统计检验和实验隔离机制。
- C10：部分指标的原文定位及适用范围介绍不完整。

重点阅读 Appendix A–D。固定模型下的部分准确率差异未达统计显著性。

## Constructing Large-Scale Real-World Benchmark Datasets for AIOps（7.6/10）

- Z01：遗漏 AIOps 研究分类及故障管理生命周期。
- Z02：Dataset A 的正常模式、异常模式及横向比较介绍不足。
- Z03：遗漏 Dataset A 的 Table 1 和 Table 2 之间的统计口径差异。
- Z04：Dataset B 的任务目标与 Dataset C 存在混淆；Dataset B 的实际 measure 为平均每分钟订单数，主要定位属性组合。
- Z05：未充分利用 Table 4 的多维根因定位案例。
- Z06：GRE 核心机制及引用来源缺少定向研究。
- Z07：合成故障质量验证的两个拒绝条件及设计原因解释不足。
- Z08：Dataset C 的调用依赖、部署依赖及 Metric–Trace 关系未展开。
- Z09：2020 年竞赛的核心排序公式 Time-to-Diagnose/F0.5 遗漏；排名积分公式存在排版歧义，不应擅自修复。
- Z10：未充分提炼数据集论文的贡献组织与论证方法。

允许针对参考文献 [47] 定向阅读，优先复用本地材料。

## AgenticOpsEval（7.7/10）

- A01：将两项赛事合计 6,093 支队伍误写为 AIOps2025 参赛规模；实际为 CCF 561、Tianchi 5,532。
- A02：遗漏 §6.1 的三类无效故障注入模式：容错吸收、观测痕迹不足、实际故障偏离注入意图。
- A03：未充分解释增加 TiDB、Redis 存储层故障的设计原因。
- A04：多模态证据分布及结构证据作用分析不足，特别是 RCA100 的 98.2% checkpoint 位于 Metric 模态。
- A05：评分公式的激励机制与潜在缺陷分析不足。
- A06：未完整展示 RCA100 Fig. 6 的真实传播案例及数值 Checkpoints。
- A07：遗漏统一观测数据模型与工具层的设计思想，以及 UModel 的关联。
- A08：遗漏数据集在 TSAD、因果发现、Agent 学习等方面的扩展价值。
- A09：未充分区分大规模竞赛应用与评价机制科学有效性的验证。
- A10：数据完整性、独立答案包、许可及阅读范围等细节遗漏；当前 arXiv v1 无独立附录。

论文没有完整多模型对照。RCA100 Process 内部评分仍需实际 scorer 支持。

处理状态和候选评价见[逐项处理记录](../../notes/benchmark/reviews/reading-feedback-resolution.md)。
