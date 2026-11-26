# Agent Knowledge Base

这是一个用于长期学习、整理和沉淀以下方向的个人 Markdown 知识库：

- LLM
- Agent / Agentic System
- Reasoning
- Planning
- Tool Use
- Memory
- RAG
- Skill
- MCP
- Context Engineering
- Multi-Agent
- Code Agent
- Research Agent

## 知识组织方式

知识库分为四层：

```text
Sources
→ Notes
→ Concepts
→ Personal Understanding
```

- `sources/`：保存原始资料文件，或保存资料引用所需的本地内容。
- `papers/`：保存论文阅读笔记。
- `code/`：保存代码和 GitHub Repository 阅读笔记。
- `code/agent-frameworks/`：保存独立 Agent Framework / SDK / Runtime 的源码学习笔记和横向比较；第三方源码本体位于被忽略的 `sources/code/`。
- `docs/`：保存博客、官方文档、教程、演讲和课程资料笔记。
- `concepts/`：保存跨资料综合后的概念知识，而不是单篇资料的摘要。
- `notes/`：保存自己的问题、想法和学习记录。
- `frameworks/`：用于未来整理和比较不同 Agent / LLM 框架。
- `templates/`：保存固定的阅读和概念记录模板。
- `skills/`：保存用于论文阅读、源码分析、知识综合与维护的现有 Skills。

源码学习入口：[Agent Framework Learning Skill](skills/agent-framework-learning/SKILL.md)；知识导航见 [INDEX.md](INDEX.md)。

## 建议工作流

日常研究默认采用轻量流程：由当前 Codex 主会话选择并读取相关 `SKILL.md`，检索少量 Experience Memory，复用知识库中的笔记、PDF 和源码，再直接完成研究成果。完整 Evolution Engine 保留为需要多轮状态管理时显式启动的可选实验模式，不是默认入口。详见[轻量研究约定](notes/guides/lightweight-research-workflow.md)。

```text
原始资料
→ Codex 主会话按需调用已有 Skills
→ 论文 / 代码 / 资料笔记
→ 提取核心概念
→ 更新 Concept 知识
→ 建立资料之间的关联
→ 形成个人理解
```

当前阶段只使用 Markdown 和 Git 管理知识，不引入向量数据库、Embedding、RAG 框架、数据库、Web 前端或复杂 Agent Framework。后续确有需要时再扩展。

从 [INDEX.md](INDEX.md) 开始浏览知识库。
