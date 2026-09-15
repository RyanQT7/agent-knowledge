# LLM+P: Empowering Large Language Models with Optimal Planning Proficiency

## 1. Metadata

- Title: LLM+P: Empowering Large Language Models with Optimal Planning Proficiency
- Authors: Bo Liu, Yuqian Jiang, Xiaohan Zhang, Qiang Liu, Shiqi Zhang, Joydeep Biswas, Peter Stone
- Year: 2023
- Venue: arXiv preprint v3; a formal venue is not explicitly stated in the local PDF
- URL / DOI: [arXiv:2304.11477v3](https://arxiv.org/abs/2304.11477)
- Local File: [LLM+P.pdf](../../sources/papers/LLM+P.pdf)

## 2. One-Sentence Summary

LLM+P uses an LLM to translate a natural-language planning problem into PDDL, delegates plan search to a classical planner, and translates the resulting symbolic plan back into natural language or robot actions.

**Source:** Abstract; Fig. 1; Sec. III.

## 3. Problem

LLM+P 试图解决的问题是：LLM 能够生成看起来合理的语言，但在需要满足状态约束、动作前置条件和长时程依赖的机器人规划任务中，往往不能可靠地产生可执行甚至可行的计划。

论文把这种缺陷描述为 linguistic competence 与 functional competence 的差异。单靠 LLM 生成动作序列时，输出可能违反世界状态或动作前置条件；而 classical planner 在获得格式化的规划问题后，可以用搜索算法寻找正确、甚至最优的计划。（Source: Sec. I）

因此，论文的目标不是让 LLM 记住所有规划问题，也不是通过微调改变 LLM 参数，而是让自然语言接口连接到已有的、具有形式化正确性保证的规划求解器。（Source: Sec. I; Sec. III.C）

## 4. Motivation

论文的动机可以用三种方式的分工来理解：

- **LLM-as-planner / LLM-only：** LLM 直接从自然语言生成动作计划。它可以进行零样本泛化，但很难稳定维护复杂状态、动作前置条件和长时程目标。
- **Classical planner alone：** planner 能在 PDDL 等结构化表示上进行高效搜索，并在给定足够时间时提供 sound/complete 或 optimal 的求解能力；但用户通常不会直接用 PDDL 描述任务。
- **LLM+P：** LLM 负责自然语言理解与 PDDL problem file 的生成，classical planner 负责结构化搜索，LLM 再负责把符号计划翻译成自然语言或机器人执行接口。

论文还比较了直接 LLM-as-planner 与 Tree of Thoughts 风格的搜索。作者观察到，增加语言模型调用并不自动解决状态前置条件问题；把搜索交给具有规划语义的 solver 才是 LLM+P 的关键分工。（Source: Sec. IV; Sec. V.B–V.C; Table I）

## 5. Core Idea

用自己的话说，LLM+P 把“理解任务”和“求解计划”拆开：

1. LLM 读取自然语言任务，并根据一个 problem/PDDL 示例生成 PDDL problem file。
2. 人类或领域专家预先提供描述动作前置条件和效果的 domain PDDL file。
3. classical planner 接收 domain PDDL 与 LLM 生成的 problem PDDL，搜索满足目标的符号动作序列。
4. LLM 将 planner 的原始计划翻译回自然语言；在机器人场景中，也可以直接连接 action executor。

这里的核心不是让 LLM 自己拥有一个经过验证的 hidden planner，而是利用 LLM 的语言转换与 in-context learning 能力，接入一个在结构化表示上工作的外部 planner。（Source: Fig. 1; Sec. III.A–III.C）

## 6. Architecture / Workflow

论文的主流程是一个 plan-first、solver-backed pipeline，而不是 ReAct 式的每一步都等待环境 Observation：

~~~text
Natural-language task
→ LLM: generate PDDL problem
→ Domain PDDL + Problem PDDL
→ Classical planner: search for a symbolic plan
→ LLM: translate plan
→ Natural-language answer or robot action executor
~~~

**Paper states:** LLM+P 的三个必要假设是：

1. 机器人能够根据与用户的对话判断何时触发 LLM+P。
2. 每个规划域已有由人类或领域专家提供的 domain PDDL，描述任务无关的动作规则。
3. 有一个简单的自然语言 planning problem 与对应 PDDL 的示例，作为 in-context demonstration。（Source: Sec. III.C）

在 classical planning 的形式化背景中，一个问题被表示为 P = <S, s_init, S_G, A, f>：状态空间、初始状态、目标状态集合、符号动作集合和状态转移函数。计划是一串动作，其每一步的前置条件必须在对应状态成立，最终状态满足目标条件。（Source: Sec. II.A）

这意味着 LLM+P 的显式 planner 位于“PDDL problem 已生成”之后；LLM 生成的语言计划或 PDDL 文本本身不能替代 planner 对前置条件和目标的搜索验证。

## 7. Key Concepts

- [Planning](../../concepts/planning.md)
- [Reasoning](../../concepts/reasoning.md)
- [Agent](../../concepts/agent.md)
- [Tool Use](../../concepts/tool-use.md)

## 8. Method

### 8.1 Classical planning representation

PDDL 将规划域与具体问题分开：

- domain file 描述 predicates、动作、前置条件和 effects，即规划域的规则；
- problem file 描述具体 objects、initial state 和 goal conditions。

论文假设 domain file 已经可用，主要让 LLM 生成与新自然语言任务对应的 problem file。这个限制使 LLM+P 更像“自然语言到结构化规划问题的接口”，而不是自动学习完整世界模型。（Source: Sec. II.B; Sec. III.C）

### 8.2 LLM as PDDL writer

作者展示了 GPT-4 在没有 prompt engineering、没有示例上下文时生成的 PDDL：文本在语法上看起来接近 PDDL，但可能创建未定义的 predicate，并遗漏初始条件。加入一个自然语言 problem、对应 PDDL 和 plan 的示例后，生成的 problem file 可以被 planner 求解。（Source: Sec. III.A–III.B）

这说明 in-context example 在该方法中不是装饰性的 prompt，而是把自然语言描述映射到特定规划域表示的重要条件。论文没有解决自动生成 domain PDDL，也没有要求 LLM 判断所有输入是否适合该 pipeline。（Source: Sec. III.C; Sec. I limitation）

### 8.3 Classical planner as solver

生成 problem PDDL 后，论文把它与固定 domain PDDL 一起交给 classical planner。实验使用 FAST-DOWNWARD，并尝试 SEQ-OPT-FDSS-1（保证最优）与 LAMA（不保证最优）两个 alias；最大搜索时间为 200 秒。（Source: Sec. V.B）

这一步将计划的可行性与最优性主要交给符号 solver，而不是让 LLM 凭 token likelihood 自行决定动作顺序。保证成立的前提是 domain/problem PDDL 正确、planner 求解在资源限制内完成，并且自然语言任务确实能被该规划域表示。

### 8.4 Robot interface

论文展示了一个 home robot tidy-up task：机器人需要把 mustard bottle 放到 pantry，并把 empty soup can 放进 recycle bin。LLM+P 找到的计划总 cost 为 22；LLM-as-planner baseline 产生的计划总 cost 为 31。（Source: Sec. V.D; Fig. 2）

## 9. Experiments

- Dataset: 七个机器人规划域，每个域包含 20 个自动生成任务：Blocksworld、Barman、Floortile、Grippers、Storage、Termes、Tyreworld。每个问题有自然语言描述和 ground-truth problem PDDL；各域还提供示例 problem/PDDL/plan。（Source: Sec. V.A）
- Baselines: LLM-as-planner without context、LLM-as-planner with context、Tree of Thoughts adaptation（论文表中记为 LLM-AS-P 的不同设置），以及 LLM+P without context。所有方法与 LLM+P 进行比较。（Source: Sec. V.B–V.C; Table I）
- Models / setup: 所有实验使用 GPT-4；temperature 为 0，使用 top-probability response，因此生成是确定性的。PDDL 由 FAST-DOWNWARD 求解，单次最大搜索时间为 200 秒。（Source: Sec. V.B）
- Metrics: Success rate；对 optimal alias 超时的域，表中在括号内报告 non-optimal alias 的 success rate。对 baseline 的结果，作者手工统计 optimal plans，并在适用时在括号内记录 sub-optimal correct plans。（Source: Sec. V.B; Table I）
- Main Results:

  | Domain | LLM-AS-P (no context) | LLM-AS-P | LLM-AS-P (ToT) | LLM+P (no context) | LLM+P |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | Barman | 0 | 0 | 0 | 0 | 20 (100) |
  | Blocksworld | 20 | 15 (30) | 0 (5) | 0 | 90 |
  | Floortile | 0 | 0 | 0 | 0 | 0 |
  | Grippers | 25 (60) | 35 (50) | 10 (20) | 0 | 95 (100) |
  | Storage | 0 | 0 (25) | 0 | 0 | 85 |
  | Termes | 0 | 0 | 0 | 0 | 20 |
  | Tyreworld | 5 | 15 | 0 | 0 | 10 (90) |

  **Source:** Table I, Sec. V.C. 表中括号是作者对 non-optimal alias 的补充结果，不应与主 success-rate 列混为同一个指标。

论文的主要结论是：在这组实验中，LLM+P 对多数规划域产生了 optimal plan，而 LLM-only / LLM-as-planner 方法在复杂域中通常无法产生可行计划。没有 context 时，LLM+P 也无法正确生成 problem PDDL，说明 PDDL 示例对该 pipeline 很关键；Floortile 的失败主要来自 mis-specified problem files，例如遗漏使地面连通的初始条件。（Source: Sec. V.C; Table I）

Tree of Thoughts adaptation 虽然在部分 partial-plan ranking 上给出合理判断，但需要大量 LLM calls，通常在时间限制内超时，因此不适合论文测试的长时程 planning。（Source: Sec. V.C）

## 10. Strengths

- 将自然语言泛化能力与 classical planner 的形式化搜索能力清晰分工。
- 使用 domain/problem PDDL 显式表示状态、动作前置条件、effects 和 goals，比直接生成自由形式动作序列更容易验证。
- 在正确 PDDL 和 solver 假设下，可以获得正确或最优计划；这是语言模型自身不容易提供的保证。（Source: Sec. II; Sec. IV; Sec. V）
- 不需要 fine-tune 或 retrain LLM，保留了自然语言接口和 zero-shot / in-context 使用方式。（Source: Sec. I; Sec. IV）
- 通过真实 home robot demonstration 说明计划结果可以连接到 action executor，而不只停留在文本答案。（Source: Sec. V.D; Fig. 2）

## 11. Limitations

### Paper-stated limitations and assumptions

- 论文没有要求 LLM 自动识别一个 prompt 是否适合 LLM+P；自动 routing 被列为 future work。（Source: Sec. I）
- 每个规划域需要预先提供 domain PDDL，且还需要一个 problem/PDDL example；domain description 的自动生成不在本文范围内。（Source: Sec. III.C）
- 作者指出未来可以研究 fine-tuning 以减少对人工提供信息的依赖。（Source: Sec. VI）

### What the paper does not establish

- LLM+P 的正确性依赖 problem PDDL 翻译正确；planner 的形式化保证不能修复自然语言到 PDDL 的语义遗漏。Floortile 结果具体显示了这一瓶颈。（Source: Sec. V.C）
- 论文的主实验是从已知初始状态和目标求解静态 symbolic planning problem。对执行中出现的未知 Observation、环境变化、在线 replanning 或部分可观测世界，没有提供系统实验：**Unclear / Not explicitly stated in the paper**。
- 该 pipeline 具有显式外部 planner，但论文没有据此给出通用的 Agent 定义，也没有证明 LLM 本身拥有独立的 internal planner。
- 机器人 demonstration 证明了一个计划可以连接 executor，但不等于论文实现了完整的 persistent memory、feedback recovery 或通用 Agent architecture。

## 12. Relationship to Existing Knowledge

### ReAct

ReAct 的核心是 runtime 的 Thought → Action → Observation 交互闭环：模型边执行边读取环境反馈。LLM+P 则先把问题翻译为 PDDL，再由 classical planner 在没有逐步外部 Observation 的主流程中搜索完整 symbolic plan。两者都可以产生多步行为，但前者重点是 observation-grounded interaction，后者重点是显式状态/动作表示与 solver-backed plan search。（Cross-paper synthesis; [ReAct paper note](../react/notes.md); [Planning](../../concepts/planning.md)）

### Toolformer

Toolformer 学习在 token generation 中何时、如何插入 API call；LLM+P 没有学习通用 API-use policy，而是把一个预先定义的 classical planner 当作结构化求解模块。把 planner 当作外部工具是一个有用的系统视角，但两者的学习目标和运行时接口不同。（Cross-paper synthesis; [Toolformer paper note](../toolformer/notes.md); [Tool Use](../../concepts/tool-use.md)）

### Reflexion

Reflexion 关注 evaluator feedback、verbal reflection 和跨 attempt memory 如何影响下一次 trajectory。LLM+P 关注一次规划问题的结构化求解；它没有引入 Reflexion 式的跨 attempt reflection 或 episodic memory。（Cross-paper synthesis; [Reflexion paper note](../reflexion/notes.md)）

### Concepts

这篇论文给 [Planning](../../concepts/planning.md) 增加了一个重要边界：显式 planning 可以由 formal state/action/goal representation 和独立 solver 实现，而不等同于语言 Thought 中的 plan-like behavior。它也给 [Reasoning](../../concepts/reasoning.md) 增加了“语言翻译与符号搜索解耦”的例子，并提醒我们 [Agent](../../concepts/agent.md) 与 [Tool Use](../../concepts/tool-use.md) 的系统边界不能仅由是否连接外部模块判断。

## 13. My Understanding

我目前把 LLM+P 理解成一个“自然语言前端 + 形式化规划后端”，而不是一个让 LLM 自己变成 classical planner 的方法。LLM 的优势被限制在：理解用户描述、利用示例写出域内的 problem PDDL、把符号结果翻译成人类或机器人可用的形式；状态转移、前置条件检查、搜索和最优性由 planner 承担。

这篇论文使 explicit planning 的边界更清楚：至少需要可区分的状态、动作、目标和转移/约束语义，以及一个负责组织或搜索未来动作序列的规划过程。ReAct 的 Thought 可能表现出分解和计划性，但若没有独立的形式化表示或 Planner/solver，它更准确地称为 plan-like reasoning。反过来，拥有外部 planner 也不自动意味着整个系统就是 Agent；是否持续感知、决策、执行并根据反馈调整，仍要看系统边界。

## 14. Questions

### Questions left by the paper

- 如何让系统自动识别一个自然语言请求是否适合 LLM+P，以及选择哪个 planning domain？（Source: Sec. I）
- 如何减少对人工 domain PDDL 和 problem/PDDL demonstration 的依赖？（Source: Sec. III.C; Sec. VI）
- 如何检测、修复或验证 LLM 生成的 problem PDDL，避免遗漏初始条件导致 planner 得到错误或无解问题？
- 如何将执行期间的 Observation、状态变化和 action failure 纳入 plan revision / replanning？**Unclear / Not explicitly stated in the paper**。

### Further questions from my interpretation

- “LLM 调用 classical planner”应如何与一般 Tool Use、Planner–Executor architecture 和 Agent interaction loop 区分？
- 当规划域不完整、状态连续或环境开放时，PDDL planner 与 language reasoning 应如何协同？
- 如何分别评估 natural-language translation、formal planning、plan execution 和 online recovery 的贡献？

## 15. Related Work

论文回顾了 classical planning、PDDL、STRIPS、HTN、task-and-motion planning，以及使用 LLM 做机器人任务规划的方法，包括 SayCan、Inner Monologue、Tree of Thoughts 和其他 PDDL/LLM 结合工作。（Source: Sec. IV）

与本知识库最直接的关系是：LLM+P 把 ReAct 等 runtime language interaction 与 classical symbolic planning 放在了不同层次；它还将 Toolformer 作为外部模块增强的相关工作，但自身不研究 learned API-use policy。（Source: Sec. IV.C）

## 16. Useful Quotes / Definitions

- “correct (or optimal) plan” 是论文对 LLM+P 输出目标的概括。（Source: Abstract）
- Classical planning problem 的工作表示为 P = <S, s_init, S_G, A, f>；计划必须满足逐步 action preconditions，并在末状态满足 goals。（Source: Sec. II.A）
- PDDL domain file 描述规则，problem file 描述 objects、initial state 和 goals。（Source: Sec. II.B）
- 论文称 LLM+P 的一个 future direction 是让系统识别何时应触发该 pipeline。（Source: Sec. I）

## 17. Tags

planning, explicit-planning, classical-planner, PDDL, planner-solver, LLM, robotics, natural-language-interface, plan-first

## Code / Implementation

- Repository: [Cranial-XIX/llm-pddl](https://github.com/Cranial-XIX/llm-pddl)
- Official status: Confirmed Official
- Read at commit: `f5f897ccabfb19d5158e5a7ac4cb36517cd4c2e0`
- Code notes: [LLM+P source-code notes](../../code/llm-p/notes.md)
- Implementation coverage: LLM-to-PDDL translation, Fast Downward invocation, validation path, and comparison baselines.
