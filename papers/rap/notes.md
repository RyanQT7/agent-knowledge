# RAP: Reasoning with Language Model is Planning with World Model

## 1. Metadata

- Title: Reasoning with Language Model is Planning with World Model
- Authors: Shibo Hao, Yi Gu, Haodi Ma, Joshua Jiahua Hong, Zhen Wang, Daisy Zhe Wang, Zhiting Hu
- Year: 2023
- Venue: EMNLP 2023, pages 8154–8173
- URL / DOI: The local PDF does not explicitly provide a DOI or a separate paper URL.
- Local File: [RAP.pdf](../../sources/papers/RAP.pdf)

## 2. One-Sentence Summary

RAP treats a language model as both a reasoning agent and a prompted world model, then uses rewards and Monte Carlo Tree Search to explore and select high-value reasoning trajectories.

**Source:** Abstract; Fig. 1; Sec. 3.

## 3. Problem

RAP 试图解决的问题是：自回归语言模型通常沿着一条 reasoning trace 继续生成，缺少对行动后状态、未来中间变量和候选路径价值的显式建模，因此在多步 planning 或 reasoning 中容易走入错误分支，却没有系统的探索、回溯和选择机制。

论文将这一问题表述为语言模型缺少可用于预测未来状态的 internal world model、缺少 reward mechanism，以及缺少 exploration / exploitation balance。（Source: Abstract; Sec. 1）

这里的目标不是让模型直接输出一条更长的 Chain-of-Thought，而是把 reasoning 过程表示为可搜索的状态—行动轨迹，并在推理时对多个候选分支进行评估。RAP 的实验覆盖 Blocksworld、数学和逻辑推理，而不是一个统一的真实机器人环境。（Source: Sec. 1; Sec. 4）

## 4. Motivation

论文将已有方法和 RAP 的动机区分如下：

- **CoT：** 通常沿单条自回归路径展开；如果早期中间步骤错误，后续生成会继续受到影响。
- **Self-consistency：** 可以采样多条完整 trace 并聚合答案，但缺少对中间状态、未来转移和分支价值的显式规划组织。
- **Least-to-most / Tree of Thoughts 等方法：** 引入分解或搜索，但论文认为它们没有在同一框架中明确统一 state、action、world model、reward 和更一般的 planning search。
- **RAP：** 将 LLM 重新提示为 world model，预测动作后的状态；再使用 reward 和 MCTS 在推理时探索、回溯并选择分支。

这是论文的 framing 和与相关工作的比较，不能解读为 RAP 已经解决所有搜索式 reasoning 的状态建模问题。（Source: Sec. 1–2; Sec. 3）

## 5. Core Idea

用自己的语言概括，RAP 把 LLM 的多步 reasoning 看成一个可以进行 inference-time planning 的过程：

1. 为任务定义初始 state、候选 action 以及 action 后的 state 表示。
2. 用一个 LLM role 作为 reasoning agent，提出下一步 action。
3. 用同一个或同类 LLM role 作为 world model，根据当前 state 和 action 预测 next state。
4. 用 action likelihood、state confidence、self-evaluation 或 task-specific heuristic 产生 reward。
5. 将 state 作为 MCTS 节点、action/transition 作为边，通过 selection、expansion、simulation、backpropagation 搜索高奖励路径。
6. 对需要完整 trace 的任务输出搜索到的路径；对数学等可以聚合多条答案或 reasoning trace。

关键变化是：模型不再只生成一条语言序列，而是使用“状态预测 + 价值信号 + 搜索”反复比较候选未来。RAP 的 world model 是推理时通过 prompting 复用的语言模型，不是论文中另行训练出的环境动力学模型。（Source: Sec. 3.1–3.4; Appendix D）

## 6. Architecture / Workflow

RAP 的抽象流程如下：

~~~text
Task / Initial State
→ MCTS selects a promising state
→ LLM reasoning agent proposes actions
→ LLM world model predicts next states
→ Reward evaluates action / state / progress
→ MCTS expands, simulates, and backpropagates
→ Best path or aggregated answer
~~~

论文把 reasoning formalize 为一个 MDP。在 state s_t，reasoning agent 根据任务 context 采样 action；world model 根据 s_t、a_t 和 context 预测 s_t+1。完整 trace 是一串模拟的 state/action/state，而不是必须在外部真实 environment 中执行的轨迹。（Source: Sec. 3.1）

因此，RAP 中的 Observation 更准确地分为两类：

- 在核心 Blocksworld、数学和逻辑实验中，下一状态主要是由 world model 预测出来的 simulated state，不是 ReAct 那种执行外部工具或环境后返回的真实 Observation。
- 这些 predicted states 在搜索中充当后续 reasoning 的条件，并帮助检查一致性、非法动作和目标进展。

论文没有把一个通用的 real-world observation loop、执行器或跨 attempt memory 定义为 RAP 的必要模块。对真实环境中的在线 replanning，**Unclear / Not explicitly stated in the paper**。（Source: Sec. 3.1; Sec. 4; Sec. 6）

## 7. Key Concepts

- [Planning](../../concepts/planning.md)
- [Reasoning](../../concepts/reasoning.md)
- [World Model](../../concepts/world-model.md)
- [Agent](../../concepts/agent.md)
- [Memory](../../concepts/memory.md)

## 8. Method

### 8.1 Task-specific state and action

RAP 不使用一个对所有任务相同的 state 定义，而是根据任务确定状态和行动：

- Blocksworld 的 state 是当前积木配置，action 是移动积木。
- 数学任务的 state 是当前中间变量值，action 是提出一个 subquestion。
- 逻辑推理的 state 是当前聚焦的 fact，action 是选择下一条规则进行 deduction。

这使 MCTS 节点具有任务语义，但也意味着 RAP 的 state abstraction 和 action generator 需要针对任务设计。（Source: Sec. 3.1; Appendix C）

### 8.2 LLM as reasoning agent and world model

形式上，reasoning agent 在 s_t 根据 p(a_t | s_t, c) 采样 action；world model 根据 p(s_t+1 | s_t, a_t, c') 预测下一状态。两种角色由同一个 LLM 通过不同 prompt 承担，论文没有把它们实现为独立参数模型。（Source: Sec. 3.1）

预测状态的价值在于让搜索过程可以继续向前模拟，并为后续 action 生成提供结构化条件。它的风险是：如果 world model 预测错，MCTS 可能在错误的 imagined state 上进行很有条理的搜索。论文的分析因此不能被理解为获得了真实环境的可靠 dynamics model。（Cross-paper interpretation; Source: Sec. 3.1; Sec. 6）

### 8.3 Reward design

论文使用多种 reward 设计：

- action likelihood / log probability，作为 LLM 对候选 action 的偏好；
- state confidence，通过重复采样答案或计算最常见答案的比例估计；
- LLM self-evaluation，例如预测回答是否有帮助的 Yes probability；
- task-specific heuristic，例如 Blocksworld 中与目标条件或距离有关的奖励。

不同任务需要不同 reward。Blocksworld 需要结构化的 action likelihood 和 task-specific reward；数学任务中 self-evaluation 和 state confidence 更有帮助。Reward 不是一个脱离任务的统一 ground-truth value function。（Source: Sec. 3.2; Sec. 4.1–4.2; Sec. 5.2; Tables 5–6; Appendix F）

### 8.4 MCTS

MCTS 的节点是 state，边包含 action 及其预测 transition，Q(s, a) 表示 action 的预期未来 reward。每轮搜索包含：

1. **Selection：** 使用 UCT 在 exploration 和 exploitation 之间选择已访问节点。
2. **Expansion：** 用 LLM 采样若干 action，并用 world model 预测 next states 和 rewards。
3. **Simulation：** 用 rollout policy 向前模拟，并使用轻量的局部 reward。
4. **Backpropagation：** 将未来 reward 汇总回路径，更新 Q 值。

搜索预算固定为若干 iteration；最终可以按最高 Q、最高 reward 的 iteration 或访问次数选择路径。作者观察到，在其设置中最高 reward path 往往更好，但这不是普适的选择保证。（Source: Sec. 3.3; Appendix A, Algorithm 1）

### 8.5 Aggregation

对于数学任务，RAP 可以聚合多条推理 trace 或答案；对于 Blocksworld 的完整行动计划和逻辑证明，主要需要保留一条完整搜索路径。这里的 aggregation 是 RAP 的任务相关输出策略，不应和 MCTS 本身混为一谈。（Source: Sec. 3.4; Sec. 4.2–4.3）

## 9. Experiments

- Models / setup: 默认使用 LLaMA-33B，temperature 0.8；在资源允许时与 GPT-4 CoT 比较。附录给出了 prompt 和搜索设置；实验使用 4 张 NVIDIA A5000 24GB。（Source: Sec. 4; Appendix B–C）
- Baselines: CoT、CoT + self-consistency、Least-to-Most、GPT-4 CoT，以及在不同任务中使用的 RAP 迭代预算。主要指标是任务准确率或计划 / 证明正确率。（Source: Sec. 4; Tables 1–4）

### Blocksworld

Blocksworld 的 state 是积木配置，action 是受限制的 STACK、UNSTACK、PUT、PICKUP。reward 结合 action likelihood 与 task-specific goal-condition reward，并给予达到目标的高 reward。测试集包含最多 5 个积木；有 30 个问题可在 2 步内解决、57 个可在 4 步内解决、114 个可在 6 步内解决。（Source: Sec. 4.1）

Table 1 报告的准确率如下：

| Method | 2 steps | 4 steps | 6 steps |
| --- | ---: | ---: | ---: |
| CoT | 0.17 | 0.02 | 0.00 |
| CoT pass@10 | 0.23 | 0.07 | 0.00 |
| CoT GPT-4 | 0.50 | 0.63 | 0.40 |
| RAP (10) | 1.00 | 0.86 | 0.26 |
| RAP (20) | 1.00 | 0.88 | 0.42 |

RAP 在 20 次 iteration 下对 6-step 问题达到 0.42；论文指出，LLaMA-33B RAP 相比 GPT-4 CoT 有 33% relative improvement，但这只是该实验设置中的相对比较，不是通用的模型能力结论。（Source: Table 1; Sec. 4.1）

### GSM8K

GSM8K 中 state 是中间变量值，action 是 incremental subquestion，world model 负责回答该 subquestion。reward 使用 self-evaluation helpfulness 与 state confidence 的 geometric mean。Table 2 结果为：

| Method | Accuracy |
| --- | ---: |
| CoT | 29.4 |
| CoT + SC (10) | 46.8 |
| Least-to-Most | 25.5 |
| Least-to-Most + SC | 42.5 |
| RAP (1) | 40.0 |
| RAP (10) | 48.6 |
| RAP + aggregation | 51.6 |

（Source: Sec. 4.2; Table 2）

### PrOntoQA

PrOntoQA 的 state 是当前聚焦的 fact，action 是选择下一条规则，world model 进行 one-hop deduction，reward 使用 self-evaluation。500 个 examples 按 3、4、5 hops 评估；RAP 使用 20 次 MCTS iterations 和 20 次 self-consistency samples。Table 3 报告：

| Method | Prediction | Proof |
| --- | ---: | ---: |
| CoT | 87.8 | 64.8 |
| CoT + SC | 89.8 | Not reported in the extracted table |
| RAP | 94.2 | 78.8 |

如果需要 CoT + SC 的 proof 数字，当前本地笔记没有可靠确认，标记为 **Unclear / Not explicitly stated in the paper**，不补写推测值。（Source: Sec. 4.3; Table 3）

### Larger Blocksworld and ablations

在 Llama-2 70B 的更大 Blocksworld 设置中，Table 4 比较 Easy / Hard 两种条件下 2、4、6、8、10、12-step 问题。RAP (10) 的 overall accuracy 是 Easy 0.65、Hard 0.51；对应 CoT 是 Easy 0.08、Hard 0.05。RAP 在更长问题上的优势随着难度增加而减弱。（Source: Sec. 5.1; Table 4）

Reward ablation 说明 reward 组合很重要。Blocksworld 的 Table 5 中，action likelihood、task-specific reward、self-evaluation 的组合结果分别包括 0.88、0.91、0.46、0.21、0.14 和 0.02 等准确率；移除或替换关键 reward 可能显著降低性能。论文同时报告 GSM8K 的 reward ablation 于 Table 6。（Source: Sec. 5.2; Tables 5–6; Appendix F）

## 10. Strengths

- 把多步 language reasoning 明确表示成 state、action、transition、reward 和 search 的组合，给出比单条 CoT 更具体的 inference-time planning 视角。
- 通过 MCTS 在候选路径之间进行 exploration、backtracking 和 reward-based selection，而不是只依赖一次贪心生成。
- 同一个 LLM 可以通过不同 prompt 兼任 reasoning agent 与 world model，不需要额外训练独立 dynamics model。（Source: Sec. 3.1–3.3）
- 在 Blocksworld、GSM8K 和 PrOntoQA 上展示了搜索式 reasoning 对不同任务的适应性。（Source: Sec. 4–5）
- 论文把 reward 设计作为独立因素进行 ablation，说明“搜索”本身不能脱离状态定义和价值信号评价。（Source: Sec. 5.2）

## 11. Limitations

### Paper-stated limitations

- RAP 主要研究 frozen LLM，能力受到预训练模型和 prompt-based world model 的限制；作者将 fine-tune world model 列为 future direction。（Source: Sec. 6）
- 论文未来希望将 RAP 与 external tools 结合；当前主要实验不是外部工具调用实验。（Source: Sec. 6）
- 不同任务需要定制 state、action 和 reward；论文没有给出完全自动的通用任务建模器。（Source: Sec. 3.1–3.2; Sec. 6）

### Limitations visible from the method and experiments

- world model 预测的是 imagined state，不是真实 environment observation；预测错误会使树搜索在错误状态上产生一致但错误的后续路径。（Cross-paper interpretation; Source: Sec. 3.1; Sec. 6）
- MCTS 需要多次调用 LLM；长路径的分支数会快速增加，论文也指出 6-step search 的空间可达到 5 的 6 次方量级。（Source: Sec. 4.1）
- reward 可能是 action likelihood、self-evaluation 或 heuristic 等代理信号，不等于任务真实效用或可靠的外部验证。
- 核心实验没有系统展示执行中真实 Observation 到来后的 replanning、工具失败恢复或长期跨 attempt memory：**Unclear / Not explicitly stated in the paper**。（Source: Sec. 4; Sec. 6）

## 12. Relationship to Existing Knowledge

### ReAct

ReAct 把 Thought、Action 和真实环境返回的 Observation 交错在 runtime trajectory 中，下一步可以直接依赖执行结果。RAP 则在 inference time 内部用 LLM 预测 next state，并在预测树上使用 MCTS；其核心实验不要求先执行外部动作再取得真实 Observation。两者都可以表示多步行为，但 ReAct 的关键是 observation-grounded interaction，RAP 的关键是 model-based search。（Cross-paper synthesis; [ReAct paper note](../react/notes.md); [Planning](../../concepts/planning.md)）

### LLM+P

LLM+P 使用 PDDL 和 classical planner 在显式形式化域中求解计划；RAP 使用被 prompting 的 LLM 作为 world model，在推理时预测状态并搜索。前者依赖预先给出的 domain PDDL 和 solver 的形式化语义，后者更灵活但依赖语言模型对状态转移和 reward 的预测。两者都属于显式 planning 的不同实现路径，但 RAP 不提供 LLM+P 那样的 classical soundness / optimality 条件。（Cross-paper synthesis; [LLM+P paper note](../llm-p/notes.md); [Planning](../../concepts/planning.md)）

### Toolformer

Toolformer 关注训练阶段学习何时、如何调用 API；RAP 的主要贡献是 inference-time search and world modeling，不是 learned API-use policy。论文只将 external tools 作为未来结合方向，因此不能把 RAP 的 simulated transition 等同于工具 Observation。（Cross-paper synthesis; [Toolformer paper note](../toolformer/notes.md); [Tool Use](../../concepts/tool-use.md)）

### Reflexion

Reflexion 将 evaluator feedback 转成跨 attempt 的 verbal reflection，并通过 episodic memory 影响下一次 trajectory。RAP 的 reward 主要在当前搜索树中评价候选 action/state，直接影响当前 MCTS 分支选择；它没有因此引入 Reflexion 式的跨 attempt reflection memory。（Cross-paper synthesis; [Reflexion paper note](../reflexion/notes.md); [Memory](../../concepts/memory.md)）

### Concepts

RAP 给 [Planning](../../concepts/planning.md) 增加了 search-based planning 和 model-based simulation 的证据，给 [Reasoning](../../concepts/reasoning.md) 增加了“多个候选推理路径可由状态预测和 reward 选择”的视角，并使 [World Model](../../concepts/world-model.md) 成为需要单独维护的概念。论文把 LLM 称为 reasoning agent，但这个角色称呼不等于论文定义了完整的 environment-facing Agent architecture。（Source: Sec. 3; Sec. 6）

## 13. My Understanding

我把 RAP 理解为一种 search-based reasoning / inference-time planning 框架：它不是让模型一次性写出更长的答案，而是先定义任务状态，使用语言模型预测行动后的 imagined state，再用 reward 和 MCTS 比较多个未来。这样，planning 的一部分从单条 token generation 中显式分离出来。

RAP 的“world model”应谨慎理解为一个由 prompt 驱动的状态预测器。它能让树搜索拥有中间节点和回溯机会，但这些节点是模型想象出来的，不是已经被环境执行验证的事实。因此，RAP 的 planning strength 来自搜索结构，可靠性仍取决于 state abstraction、transition prediction 和 reward 的质量。

与 ReAct 相比，RAP 牺牲了实时环境 Observation 的直接 grounding，换取了在内部候选路径上进行 lookahead；与 LLM+P 相比，它减少了对固定符号 domain 的依赖，但也缺少 classical planner 的形式化状态转移和最优性条件。这是两种不同的 explicit planning 路径，而不是一个统一算法。

## 14. Questions

### Questions left by the paper

- 如何自动为新任务定义可靠的 state、action 和 reward，而不依赖大量 task-specific prompt engineering？（Source: Sec. 3.1–3.2）
- 如何验证 LLM world model 的 transition prediction，并让搜索识别错误的 imagined state？（Source: Sec. 3.1; Sec. 6）
- MCTS 的搜索预算、分支因子和 LLM 调用成本如何随任务长度扩展？（Source: Sec. 3.3; Sec. 4.1）
- 如何将 RAP 与 external tools、真实环境 Observation 和 online replanning 结合？（Source: Sec. 6）

### Further questions from my interpretation

- RAP 的 predicted state 在什么条件下可以作为真实 Observation 的近似？
- state confidence、self-evaluation 和 task heuristic 如何校准到任务真实成功率？
- RAP 的 world model 是否需要与 reasoning agent 使用不同模型或不同训练目标？
- MCTS 的路径选择与 ReAct 的 runtime action loop 如何在同一 Agent 中组合？

## 15. Related Work

论文讨论了 Chain-of-Thought、self-consistency、least-to-most、Tree of Thoughts、LLM planning、world model、tree search 和 model predictive control 等方向。RAP 的区别在于：把 LLM 同时用于 reasoning agent 和 world model，并用 MCTS 在推理阶段组织状态—行动搜索。（Source: Sec. 2; Appendix D）

## 16. Useful Quotes / Definitions

- 论文将 reasoning agent 与 world model 统一放入 planning-style MDP：agent 选择 action，world model 预测 next state。（Source: Sec. 3.1）
- MCTS 的四个阶段是 selection、expansion、simulation 和 backpropagation。（Source: Sec. 3.3; Appendix A）
- world model 在 RAP 中由 LLM prompting 实现，论文并未将其等同于经过环境交互训练的独立 dynamics model。（Source: Sec. 3.1; Appendix D）
- 论文报告 LLaMA-33B RAP 在 Blocksworld 的特定设置中相对 GPT-4 CoT 有 33% relative improvement。（Source: Sec. 4.1; Table 1）

## 17. Tags

RAP, planning, reasoning, world-model, MCTS, search, inference-time-planning, model-based-planning, LLM, Blocksworld

## Code / Implementation

- Repository: [Ber666/RAP](https://github.com/Ber666/RAP)
- Official status: Confirmed Official; the paper's older `Ber666/llm-reasoners` link was unavailable and is recorded as a URL/version discrepancy.
- Read at commit: `774817c228b3d5ddfc18de2318f3476128ecf6eb`
- Code notes: [RAP source-code notes](../../code/rap/notes.md)
- Implementation coverage: MCTS, symbolic Blocksworld action/state transitions, LLM world-model scoring, and VAL validation.
