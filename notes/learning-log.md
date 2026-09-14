# Learning Log

记录每次学习的日期、材料、主要收获、概念更新和后续行动。

建议格式：

```markdown
## YYYY-MM-DD

- Materials:
- What I learned:
- Concepts updated:
- New questions:
- Next steps:
```

## 2026-09-14

- Date: 2026-09-14
- Paper: ReAct: Synergizing Reasoning and Acting in Language Models
- Core takeaway: ReAct 将不改变环境但能更新 context 的 language thought，与会产生 Observation 的外部 Action 交错起来，形成 reasoning 与 acting 的闭环。
- New concepts: interleaved reasoning/action、Observation grounding、language-mediated planning、working-memory-like context（解释性说法）。
- Open questions: Thought 是否忠实反映 internal state，以及这种 plan-like behavior 如何扩展为长期 Memory 和结构化 tool use。
- Next step: 对比 ReAct 与现代 tool calling、planning 和 memory 系统的边界。

## 2026-09-14

- Date: 2026-09-14
- Paper: Toolformer: Language Models Can Teach Themselves to Use Tools
- Core takeaway: Toolformer 用候选 API 执行结果带来的 future-token loss 降低作为自监督信号，让 LM 学会何时、如何调用文本工具；这与 ReAct 的运行时 Thought/Action/Observation 闭环不同。
- New concepts: loss-based call filtering、inline textual API result、tool-augmented LM 与完整 Agent 的边界。
- Open questions: 如何把 learned call policy 迁移到 structured tool calling / MCP，以及如何支持可靠的链式、交互式调用。
- Next step: 比较更多 tool-use 方法，区分训练得到的调用策略与运行时 Agent trajectory。

## 2026-09-14

- Date: 2026-09-14
- Paper: Reflexion: Language Agents with Verbal Reinforcement Learning
- Core takeaway: Reflexion 用 Evaluator feedback 生成 verbal reflection，保存为受限的跨 attempt episodic memory；它改变下一次 context，而不是模型参数。
- New concepts: verbal reinforcement、reflection loop、episodic memory、Evaluator–Actor separation。
- Open questions: 错误 reflection 如何传播，以及 task-local memory 如何扩展为可靠的 persistent memory。
- Next step: 比较 reflection、critic 和其他 self-correction 方法。

## 2026-09-14 — Knowledge Review v1

- Scope: ReAct、Toolformer、Reflexion。
- Main conceptual changes: 将三篇论文分别定位为 runtime interaction、learned tool-use policy 和 cross-attempt feedback adaptation；明确区分 reasoning、planning、reflection、context 与 memory。
- Top open questions: Agent 与 tool-augmented LM 的边界；如何构造 explicit planning；如何让 feedback / memory 在错误累积下仍可靠。
- Next learning priorities: Explicit Planning and Replanning、Memory Architectures、Structured Tool Calling、Reflection / Critic / Self-Correction、Context Engineering。

## 2026-09-14

- Date: 2026-09-14
- Paper: LLM+P: Empowering Large Language Models with Optimal Planning Proficiency
- Core takeaway: LLM+P 将自然语言到 PDDL 的翻译与 classical planner 的显式计划搜索分开，说明 explicit planning 不等同于语言 Thought 中的 plan-like reasoning。
- New concepts: solver-backed planning、PDDL problem representation、LLM–planner boundary。
- Open questions: 如何验证 LLM 生成的 PDDL，以及如何把静态计划与执行中的 Observation 和 replanning 结合。
- Next step: 比较搜索式 world model planning 与 planner–executor / plan-first 架构。
