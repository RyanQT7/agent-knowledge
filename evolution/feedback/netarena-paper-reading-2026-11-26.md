# NetArena 论文精读人工反馈

- feedback_id: `feedback-netarena-paper-reading-20261126`
- task_type: `research`
- skill_name: `paper-reading`
- skill_version: `skill-paper-reading-20261126t110225z-ed765d`（待审候选；未应用）
- evidence: 用户结合原始论文 PDF 对精读结果的人工评价，8.5/10。
- failure_signature: 图文对照、统计解释和应用级指标实现边界仍可进一步具体化。
- expected_behavior: 对关键图表进行原始页面核验，明确正文与图值差异，区分统一定义和代码中的应用级指标。
- observed_behavior: 用户认可主动识别核心贡献、查看附录、发现统计口径差异与论文内部矛盾、分析潜在 Shortcut；以下为具体补充意见。
- reproducibility: 单篇论文的独立人工反馈；不是新旧 Skill 受控对照。
- status: `recorded`
- recorded_at: `2026-11-26`
- related_experience_ids: `exp-311316848c9f`, `exp-77ed5c77884f`, `exp-8da9d9cb732b`（复用既有论文阅读深度与证据定位经验；未重复新增相同经验）

## 反馈条目

- **NET01**：已发现 SFT 图文矛盾，但还需明确混合难度 Correctness 正文与图中 Level 2 数值的差异。
- **NET02**：SFT 训练样本规模与训练难度多样性存在混杂因素。
- **NET03**：统计分辨能力缺少具体计算示例。
- **NET04**：Figure 3 部分模型排名与正文描述需要进一步核对。
- **NET05**：三类任务的 Safety 定义及实际实现边界未充分区分。
- **NET06**：可以进一步分析 Correctness 与 Safety 的联合评价。
- **NET07**：真实调查案例与任务复杂度划分可以更加具体。
- **NET08**：PDF 原始图表读取与核验能力不足。

## 已认可的表现

- 主动识别论文关键贡献。
- 主动查看附录。
- 识别统计口径差异。
- 发现论文内部文字与图表矛盾。
- 分析潜在 Shortcut 风险。

## 本轮处理边界

本轮新增 PDF 页面读取工具，并基于原始页面对 Table 1、Figure 3、Figure 5 做定向核验；只补充 NetArena 笔记中证据足够的细节。NET07 中完整真实调查过程与任务复杂度和生产运维难度的对应关系仍待补充。没有修改正式 Skill 或候选，也没有据此宣称 Skill 改进已获受控验证。
