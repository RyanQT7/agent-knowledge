# Lightweight Research Workflow

日常研究默认由当前 Codex 主会话组织，直接复用已有 Skills、知识文件和 Experience Memory。完整 Evolution Engine 保留为可选的多轮实验工具，不为普通论文或源码任务默认启动。

## 默认流程

1. 根据任务读取相关的现有 `skills/<name>/SKILL.md`，不重建 Skill 已负责的阅读或分析步骤。
2. 用 `experience-memory` 检索最多 3–5 条相关经验；旧经验只指导工作方式，不作为当前研究事实。
3. 先查 `INDEX.md`、相关 Questions / Concepts / Reviews、已有论文笔记和 `sources/papers/` 原文；只补尚缺的证据。
4. 由当前主会话规划并完成研究。直接写入符合对应 Skill 规范的研究成果，不在普通流程之外再启动一套 Engine 研究。
5. 收尾时说明新增知识、对已有结论的影响、未解决问题；只记录有跨任务价值的经验。正式 Claim 或知识文件更新继续遵守 Proposal 和审批边界。

## 日常入口

```text
按知识库的轻量研究约定完成：先读取相关 Skill，检索少量经验，复用现有笔记和原始资料，由当前 Codex 会话直接完成，不启动完整 Evolution Engine。任务：<主题或任务>
```

常用已有 Skills：

- 单篇论文：`paper-reading`；AIOps 专题论文：`aiops-paper-reading`。
- 论文对应源码：`paper-code-discovery`，再按需用 `code-reading` 做静态分析。
- 多篇已完成阅读的综合：`knowledge-review`；用户需要批次编排时可用 `learning-batch` 或 `aiops-learning-batch`。
- 新资料发现：`research-discovery`；只读结构或语义检查：`knowledge-audit`；已有知识检索：`knowledge-query`。

批次 Skill 只在确实需要组织多篇材料时使用。完整 Engine 自己管理研究轮次和预算，不要在 Engine 里再嵌套 `learning-batch`。

## Experience Memory

检索经验：

```bash
python3 scripts/evolution/experience.py search \
  --task-type research --topic "<主题>" --skill paper-reading --limit 5
```

记录用户反馈或可复用经验：

```bash
python3 scripts/evolution/experience.py add \
  --type user_feedback --task-type research --skill paper-reading \
  --message "<简短反馈>" --source-ref "<报告或任务引用>"
```

只有用户明确要求长期遵守的偏好才加 `--persistent`。不要保存完整聊天、原文、凭据或普通成功操作。

## 按需 Independent Judge

仅对重要、有争议或证据边界不清的结论请求独立核验，例如：

```text
请对以下 Findings 做一次只读 Independent Judge 核验。使用独立、无历史上下文的临时 Codex 会话（若当前环境支持）；只提供验收标准、Findings 和对应原始来源定位，逐条判断证据是否支持、范围是否准确、哪些需要限定或拒绝。复用本地原文，只读必要章节，不重做完整研究，不修改知识文件或 Skill。若无法建立独立会话，请明确标记为主会话自检，不要称为独立评估。
```

当前没有独立 Judge 专用 CLI。`knowledge-audit` 是知识审计 Skill，不等于独立 Judge；完整 Engine 的 Evaluator 是可选完整流程的一部分。无需因每项普通研究都调用额外模型。

## 按需 Skill Evolution

出现明确、可复用的 Skill 问题时，先用 `experience-memory` 找相关记录，再请求：

```text
使用 skill-evolution，根据这些真实经验检查 <skill-name> 是否有明确且可复用的缺陷。区分 Skill、Controller、模型、环境和证据问题；如有依据，只生成并评估一个最小候选，不要直接修改正式 Skill。
```

查看和评估候选：

```bash
python3 scripts/evolution/skill_evolution.py list
python3 scripts/evolution/skill_evolution.py show <PROPOSAL_ID>
python3 scripts/evolution/skill_evolution.py evaluate <PROPOSAL_ID>
```

正式应用必须由用户明确批准；批准后可用 `approve`、`apply`，需要撤回时用 `rollback`。没有可靠改进依据时保留经验即可，不必创建 Proposal。

## 可选完整 Evolution Engine

只有任务明确需要可恢复的多轮 Planner / Executor / Evaluator / Reflector、Engine 状态和预算控制时才启动：

```bash
python3 scripts/evolution/evolve.py run \
  --focus "<研究主题>" --max-rounds 3 --max-model-calls 12
```

Engine 使用冻结 Git 基线和隔离候选工作区。运行前先提交希望它读取的知识或 Skill 更新；Engine 不会自动看到主工作区中尚未提交的文件。其研究产物和知识 Proposal 仍需人工审阅。
