# ReAct: Synergizing Reasoning and Acting in Language Models

## 1. Metadata

- Title: ReAct: Synergizing Reasoning and Acting in Language Models
- Authors: Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
- Year: 2023
- Venue: ICLR 2023
- URL / DOI: [arXiv:2210.03629v3](https://arxiv.org/abs/2210.03629v3); [project page and code](https://react-lm.github.io/)
- Local File: [sources/papers/react.pdf](../../sources/papers/react.pdf)

原始 PDF 按知识库规范保存在 `sources/papers/`，论文阅读笔记保存在 `papers/react/`。

## 2. One-Sentence Summary

ReAct prompts a frozen large language model to interleave free-form reasoning traces with task actions, so that reasoning can guide planning and information seeking while external observations ground and update subsequent reasoning.

**Source:** Abstract; Sec. 2.

## 3. Problem

ReAct 试图解决的核心问题，是让 LLM 在解决任务时同时具备“会想”和“会做”，而不是把 reasoning 与 acting 当成两个孤立能力研究。

论文指出两类已有方法各有缺陷：

- Chain-of-thought（CoT）可以生成多步推理，但推理过程是静态的、没有被外部世界约束的 black box。模型不能通过行动获取新信息，也难以及时更新知识，因此容易产生事实幻觉，并在错误推理后继续传播错误。
- 面向交互决策的语言模型通常把观察转成文本，再直接生成领域动作或计划，并由 controller 执行；但它们很少使用语言模型显式地围绕高层目标进行抽象推理、维护工作记忆或动态调整计划。

因此，给定一个需要多步推理或长时程交互的任务，论文要研究的是：能否让同一个 LLM 在一个闭环轨迹中交替生成 reasoning traces 和 task-specific actions，并且比单独 reasoning 或单独 acting 带来系统性收益？

**Source:** Sec. 1; Fig. 1; Sec. 2.

## 4. Motivation

论文借用了人类解决任务时“行动与内在语言连续交织”的观察：语言推理可以帮助人跟踪进度、分解目标、调整计划、处理例外和维持工作记忆；行动又可以打开食谱、查看冰箱或查询互联网，为推理提供外部信息。

对 LLM 而言，这种交互尤其重要，因为：

1. 只在模型内部展开 CoT，无法验证中间事实，也无法在需要时主动获取信息。
2. 只生成动作时，动作选择依赖一个高度隐式的 `context → action` 映射，模型可能无法从长轨迹中提取高层目标、子目标和当前状态。
3. 把两者放到同一轨迹中，理论上可以形成两个方向的协同：`reason to act` 和 `act to reason`。

**Source:** Sec. 1; Sec. 2.

## 5. Core Idea

ReAct 的核心不是简单地在一次回答前加一句“Let's think step by step”，而是把语言推理和外部行动都纳入连续的任务轨迹：

1. 将语言空间 `L` 加入原有外部动作空间 `A`，得到增强动作空间 `\hat{A} = A ∪ L`。
2. 当模型生成一个 language thought 时，这个 thought 不改变外部环境，也不会产生环境 Observation；它的作用是对当前上下文进行推理，并把新的信息追加到后续上下文中。
3. 当模型生成一个外部 Action 时，Action 被 Wikipedia API 或交互环境执行，环境返回 Observation；Observation 再被放回上下文，成为下一次 thought/action 生成的依据。
4. 通过 few-shot prompt 中的人类示范轨迹，教 frozen PaLM-540B 同时学习 thought、action 和 observation 的交错格式。

于是，模型可以用 thought 生成或修改高层计划、提取观察中的关键信息、处理异常、决定下一次检索或行动；也可以用 action 主动取得模型内部没有的外部信息。

**Source:** Abstract; Sec. 2; Fig. 1.

## 6. Architecture / Workflow

### 6.1 General interaction loop

论文将一般的 agent-environment 设置形式化为：在时间 `t`，Agent 从环境收到 `o_t ∈ O`，并根据上下文 `c_t` 按策略 `π(a_t | c_t)` 选择外部动作 `a_t ∈ A`。上下文写作：

```text
c_t = (o_1, a_1, ..., o_{t-1}, a_{t-1}, o_t)
```

ReAct 将语言空间加入动作空间：

```text
\hat{A} = A ∪ L
```

一个 thought `\hat{a}_t ∈ L` 不影响环境，不触发 Observation，但会更新上下文：

```text
c_{t+1} = (c_t, \hat{a}_t)
```

一个外部 Action 则被环境执行，并产生下一条 Observation。

**Source:** Sec. 2.

### 6.2 ReAct workflow

```text
Task / Current Observation
→ Thought / Reasoning
→ Action
→ Observation
→ Thought / Reasoning
→ Action
→ ...
→ Finish[Answer]
```

每一步的意义如下：

| 步骤 | 作用 |
| --- | --- |
| Task | 给出问题、claim 或环境中的高层目标。 |
| Thought / Reasoning | 在语言中分解目标、建立或更新计划、提取事实、比较候选项、识别异常，或决定下一次需要查询什么。它只更新模型上下文。 |
| Action | 向外部 API 或环境发出任务相关指令，例如 `Search[entity]`、`Lookup[string]`、`go to ...` 或网页点击。 |
| Observation | 返回检索结果、环境状态变化或动作失败信息；它把外部世界反馈注入后续上下文。 |
| Finish | 通过 `Finish[answer]` 输出最终答案或任务完成信号。 |

### 6.3 Dense and sparse thoughts

- 对 HotpotQA 和 FEVER 这类 reasoning 主要的任务，论文让 thought 与 action 交替出现，形成相对 dense 的 thought-action-observation 轨迹。
- 对 ALFWorld 和 WebShop 这类可能包含大量动作的决策任务，thought 只在有用的位置稀疏出现，并让语言模型自己决定 thought 与 action 的异步出现位置。

### 6.4 Agent、environment 与 tools 的关系

在这篇论文里，LLM 同时充当基于上下文的 policy 和生成 thought/action 的主体；environment 或工具负责执行外部 Action 并返回 Observation。

- 在知识密集型任务中，Wikipedia API 是外部工具，Action 是文本化的 `Search` / `Lookup` / `Finish` 指令。
- 在 ALFWorld 中，environment 是文本化的模拟家庭环境，Observation 描述物体和状态，Action 会改变环境或因前置条件不满足而失败。
- 在 WebShop 中，environment 是带有商品、属性和网页操作的购物环境，Observation 含有搜索结果、商品选项和页面反馈。

**Unclear / Not explicitly stated in the paper:** 论文没有定义独立的 Planner、Executor 或 Memory 模块。高层计划、动作决策和历史信息主要通过语言模型生成的 thought 以及 trajectory context 表达；把其中一部分理解为“任务内 working-memory-like context”是本笔记的解释，不是论文提出的独立 Memory 架构。

**Source:** Sec. 2; Sec. 3.1; Sec. 4; Appendix C-D.

## 7. Key Concepts

- [Agent](../../concepts/agent.md)：ReAct 给出一个显式的 agent-environment 闭环，并把 thought 作为增强动作空间中的语言动作。
- [Reasoning](../../concepts/reasoning.md)：reasoning trace 不再是与环境隔离的静态 CoT，而是可以决定下一次行动、并被 Observation 纠正的上下文内容。
- [Tool Use](../../concepts/tool-use.md)：Action 能调用 Wikipedia API 或交互环境，返回的 Observation 直接进入后续推理。
- [Planning](../../concepts/planning.md)：thought 可以分解高层目标、跟踪子目标、调整行动计划；论文没有把它实现为独立规划器。
- [Memory](../../concepts/memory.md)：trajectory context 和 thought 可以表现出任务内 working-memory-like behavior（本笔记的解释），但论文没有实现持久化记忆模块。

## 8. Method

### 8.1 Knowledge-intensive reasoning tasks

论文使用两个 question-only 设置的知识密集型 benchmark：

- HotpotQA：需要跨两个或更多 Wikipedia passages 进行多跳问答。
- FEVER：判断 claim 是 `SUPPORTS`、`REFUTES` 还是 `NOT ENOUGH INFO`，依据是是否存在可以验证 claim 的 Wikipedia passage。

模型不直接获得 support paragraphs，只能依靠内部知识，或通过外部 Wikipedia API 获取信息。

### 8.2 Wikipedia action space

论文设计了一个简单且有意较弱的 Wikipedia web API：

```text
search[entity]
```

如果实体页面存在，返回该页面前五句话；否则返回 Wikipedia 搜索引擎给出的最多五个相似实体。

```text
lookup[string]
```

返回页面中包含给定字符串的下一句话，模拟浏览器中的 Ctrl+F。

```text
finish[answer]
```

以给定答案结束当前任务。

这个 action space 明显弱于 state-of-the-art 的 lexical 或 neural retriever。作者这样设计是为了模拟人通过 Wikipedia 交互，并迫使模型用显式语言 reasoning 指定检索目标，而不是把检索过程藏在一个强 retriever 中。

**Source:** Sec. 3.1.

### 8.3 ReAct prompting

HotpotQA 随机选择 6 个训练案例，FEVER 随机选择 3 个训练案例，人工编写 ReAct 格式的 few-shot 轨迹。论文报告更多示例没有带来更好性能。

示例中的 thought 主要承担以下功能：

- 分解问题并建立检索计划。
- 从 Wikipedia Observation 中提取关键事实。
- 进行 commonsense 或 arithmetic reasoning。
- 改写搜索词或在实体不明确时选择新的查询。
- 综合已获得的信息并生成最终答案。

### 8.4 Baselines and hybrid methods

论文通过删除 ReAct 示范中的不同部分构造受控 baseline：

- `Standard`：删除 thought、action 和 observation。
- `CoT`：只保留 reasoning，删除 action 和 observation。
- `CoT-SC`：推理时采样 21 条 CoT 轨迹，temperature 为 0.7，用多数答案作为结果。
- `Act`：删除 thought，只保留 action，近似纯行动生成。

论文还组合内部知识与外部知识：

- `ReAct → CoT-SC`：先运行 ReAct；HotpotQA 超过 7 steps、FEVER 超过 5 steps 仍未返回答案时，退回 CoT-SC。
- `CoT-SC → ReAct`：如果 `n` 个 CoT-SC 样本中多数答案出现次数小于 `n/2`，认为内部知识不够可靠，退回 ReAct。

### 8.5 Fine-tuning

为探索 prompt 之外的训练方式，作者使用 ReAct 生成的 3,000 条正确轨迹（其他 baseline 也使用相应轨迹）对较小的 PaLM-8B 和 PaLM-62B 进行 fine-tuning，目标是根据问题或 claim 生成完整的 thoughts、actions 和 observations。

Appendix B.1 给出的设置是 batch size 64：

- PaLM-8B：ReAct / Act 训练 4,000 steps；Standard / CoT 训练 2,000 steps。
- PaLM-62B：ReAct / Act 训练 4,000 steps；Standard / CoT 训练 1,000 steps。

作者观察到 ReAct 和 Act 通常从更多 steps / data 中受益，而 Standard 和 CoT 在 fine-tuning 一段时间后性能下降。

**Source:** Sec. 3.2; Appendix B.1.

### 8.6 Interactive decision-making tasks

#### ALFWorld

ALFWorld 是与 ALFRED 对齐的文本环境，包含 6 类家庭任务，例如在 desklamp 下检查 paper。一个实例可能有超过 50 个位置，专家策略可能需要超过 50 steps；因此任务要求 Agent 分解目标、跟踪子目标并系统探索物体可能出现的位置。

作者为每个 task type 从训练集人工标注 3 条轨迹，每条轨迹包含稀疏 thoughts，用于：

1. 分解目标。
2. 跟踪子目标是否完成。
3. 决定下一个子目标。
4. 利用 commonsense 推断物体可能在哪里以及下一步该做什么。

评测使用 134 个未见过的 evaluation games。每个 task type 用 3 条标注轨迹的两两排列构造 6 个 prompt；`Act` 使用同样的示例但删除 thought，因此是测试稀疏 reasoning 作用的受控比较。baseline 是 BUTLER，一个每类使用 `10^5` 条 expert trajectories 训练的 imitation-learning agent。

#### WebShop

WebShop 是在线购物网页环境，包含 1.18M 个真实商品和 12k 条人工指令。Agent 要依据包含多个属性和价格约束的用户指令进行搜索、选择商品、选择选项并购买。评测包括：

- `Score`：选中商品满足的目标属性比例，在 episodes 上平均。
- `Success rate`：满足全部要求的 episodes 比例。

评测使用 500 条测试指令。baseline 包括使用 1,012 条人工轨迹训练的 imitation learning，以及进一步使用 10,587 条训练指令的 IL + RL。

在 WebShop 的 `Act` prompt 中只有外部动作；ReAct 额外使用稀疏 reasoning 来判断应该探索什么、什么时候购买、商品选项是否符合指令。

**Source:** Sec. 4; Appendix C.3-C.4.

### 8.7 ReAct-IM ablation

作者将 ReAct 与 Inner Monologue（IM）式的反馈进行对比。`ReAct-IM` 使用 dense external feedback thoughts，但限制 thought 只讨论当前目标和当前子目标；它缺少：

- 判断子目标何时完成。
- 判断下一个子目标是什么。
- 调用语言模型预训练 commonsense 来推断物体位置。

这项 ablation 用来区分“真正进行高层内部推理”与“重复描述外部状态反馈”的作用。

**Source:** Sec. 4; Appendix B.2; Table 3.

## 9. Experiments

### 9.1 HotpotQA and FEVER

Table 1 的 PaLM-540B prompting 结果如下：

| Method | HotpotQA EM | FEVER Acc |
| --- | ---: | ---: |
| Standard | 28.7 | 57.1 |
| CoT | 29.4 | 56.3 |
| CoT-SC | 33.4 | 60.4 |
| Act | 25.7 | 58.9 |
| ReAct | 27.4 | 60.9 |
| CoT-SC → ReAct | 34.2 | 64.6 |
| ReAct → CoT-SC | 35.1 | 62.0 |
| Supervised SoTA | 67.5 | 89.5 |

**Source:** Table 1, Sec. 3.3.

主要解读：

- ReAct 在两个任务上都优于 Act，说明 reasoning 能帮助 action 选择，尤其是帮助综合最终答案。
- 与 CoT 相比，ReAct 在 FEVER 上为 60.9 对 56.3，但在 HotpotQA 上为 27.4 对 29.4。论文将差异解释为：FEVER 的支持/反驳往往依赖细微事实差异，外部检索更有价值；而 HotpotQA 上 CoT 的推理结构较灵活，ReAct 的结构约束会带来代价。
- 组合方法优于单一方法：HotpotQA 上 `ReAct → CoT-SC` 最好，FEVER 上 `CoT-SC → ReAct` 最好。这表明内部知识与外部知识可以互补，而不是必须二选一。

论文还研究了不同 CoT-SC sample 数量下的组合方法。两种组合策略在不同 sample 数量下都持续优于单独 CoT-SC；达到 21 samples 的 CoT-SC 性能时，组合方法只需约 3-5 samples。

**Source:** Sec. 3.3; Fig. 2.

### 9.2 Human-labeled success and failure modes

作者从 ReAct 和 CoT 中分别随机抽取正确与错误的轨迹，人工检查共 200 个例子。Table 2 的模式比例为：

| Outcome / Mode | Description | ReAct | CoT |
| --- | --- | ---: | ---: |
| Success: true positive | 正确的 reasoning trace 和 facts | 94% | 86% |
| Success: false positive | 含有 hallucinated reasoning trace 或 facts | 6% | 14% |
| Failure: reasoning error | 错误推理，包括无法跳出重复步骤 | 47% | 16% |
| Failure: search result error | Search 为空或没有有用信息 | 23% | - |
| Failure: hallucination | hallucinated reasoning trace 或 facts | 0% | 56% |
| Failure: label ambiguity | 预测正确但没有精确匹配数据集 label | 29% | 28% |

这里的百分比是作者对抽样轨迹进行人工分类的结果，并非对所有数据集实例的总体统计。

论文的重点观察是：

1. CoT 的主要失败模式是 hallucination；ReAct 通过 Wikipedia Observation 使轨迹更 grounded、fact-driven 和可检查。
2. ReAct 的交错结构提高了 groundedness，却减少了自由组织推理的灵活性，因此 reasoning error 比 CoT 更高。
3. ReAct 的一个特有错误是反复生成之前的 thought 和 action，作者推测这可能与 sub-optimal greedy decoding 有关，并提出更好的 decoding（例如 beam search）可能有帮助。
4. ReAct 的 Search 若返回非信息性结果，会使后续 reasoning 偏离；这类 search result error 占作者分析的 ReAct 错误案例的 23%。

**Source:** Table 2; Sec. 3.3; Appendix E.1.

### 9.3 Fine-tuning scaling

Figure 3 给出 HotpotQA 上四种方法在 PaLM-8B、62B、540B 下 prompting 与 fine-tuning 的 scaling 对比。文字结论是：

- 在 PaLM-8B/62B 上只 prompting 时，ReAct 因为同时学习 reasoning 和 acting，性能反而是四种方法中最差。
- 只用 3,000 条轨迹 fine-tuning 后，ReAct 成为四种方法中最好；PaLM-8B fine-tuned ReAct 超过所有 PaLM-62B prompting 方法，PaLM-62B fine-tuned ReAct 超过所有 PaLM-540B prompting 方法。
- Standard / CoT 的 fine-tuning 明显不如 ReAct / Act；作者认为前者更像在记忆可能 hallucinated 的事实，后者学习的是通过 Wikipedia 获取信息的更一般化能力。

**Unclear / Not explicitly stated in the paper:** Figure 3 的每个曲线点的完整数值没有在正文或表格中逐项列出，本笔记不从图形估读具体数字。

**Source:** Sec. 3.3; Fig. 3; Appendix B.1.

### 9.4 ALFWorld

Table 3 的 task-specific success rates（%）如下：

| Method | Pick | Clean | Heat | Cool | Look | Pick 2 | All |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Act (best of 6) | 88 | 42 | 74 | 67 | 72 | 41 | 45 |
| ReAct (avg) | 65 | 39 | 83 | 76 | 55 | 24 | 57 |
| ReAct (best of 6) | 92 | 58 | 96 | 86 | 78 | 41 | 71 |
| ReAct-IM (avg) | 55 | 59 | 60 | 55 | 23 | 24 | 48 |
| ReAct-IM (best of 6) | 62 | 68 | 87 | 57 | 39 | 33 | 53 |
| BUTLER-g (best of 8) | 33 | 26 | 70 | 76 | 17 | 12 | 22 |
| BUTLER (best of 8) | 46 | 39 | 74 | 100 | 22 | 24 | 37 |

主要结果：

- ReAct 最好的 prompt set 总体为 71%，高于 Act 的 45% 和 BUTLER 的 37%。
- 即使是最差的 ReAct trial（48%，论文正文如此描述）也高于 Act 和 BUTLER 的最佳 trial。
- ReAct 相对于 Act 的优势在 6 个受控 trial 中都出现，相对性能增益为 33%-90%，平均 62%。
- ReAct-IM 总体为 48%（best 为 53%），显示仅注入密集外部反馈不足以替代高层目标分解、子目标跟踪和 commonsense reasoning。

**Source:** Table 3; Sec. 4; Appendix D.2.

### 9.5 WebShop

Table 4 的结果如下：

| Method | Score | Success Rate |
| --- | ---: | ---: |
| Act | 62.3 | 30.1 |
| ReAct | 66.6 | 40.0 |
| IL | 59.9 | 29.1 |
| IL + RL | 62.4 | 28.7 |
| Human | 82.1 | 59.6 |

ReAct 比 Act 的 success rate 高 9.9 个百分点，比此前最佳的 IL success rate 高 10.9 个百分点；论文摘要将其概括为约 10% 的绝对提升。论文的定性分析认为，ReAct 更容易从 noisy observation 中识别同时满足用户属性要求的商品和选项，但仍明显落后于人类。

**Source:** Table 4; Sec. 4; Appendix C.3 and D.3.

### 9.6 GPT-3 supplementary experiment

作者使用 GPT-3 `text-davinci-002` 的 greedy decoding 做补充验证：

| Model | HotpotQA EM | ALFWorld Success Rate |
| --- | ---: | ---: |
| PaLM-540B | 29.4 | 70.9 |
| GPT-3 | 30.8 | 78.4 |

HotpotQA 使用 500 个 validation questions 的子集，ALFWorld 使用全部 134 个 unseen validation instances，并采用按 PaLM-540B 选择的最佳 prompt set。作者据此认为 ReAct prompting 的效果并不只依赖单一 LLM。

**Source:** Appendix A.1, Table 5.

### 9.7 Additional qualitative evidence

- Appendix A.2 展示一个 HotpotQA 数据集 label 已过时的例子：只有 ReAct 能通过真实世界网页交互取得较新的信息并给出合理答案；Act 虽然也能访问网页，但缺少 reasoning 来指导查询。
- Appendix A.3 的 human-in-the-loop 例子中，人只需删除一个 hallucinating thought 并补充一个 hint，ReAct 就改变后续行为并成功完成 ALFWorld 任务。作者据此提出 thought editing 可能支持新的 human-machine collaboration，但没有进行系统研究。
- Appendix D 的轨迹显示，Act 可能在未到达 sinkbasin 时就尝试清洗刀具并陷入重复；ReAct 的 thought 会明确记录“已拿到物体”以及“下一子目标是去 sinkbasin 清洗”。ReAct-IM 还可能因错误 thought 误以为刀具已经清洗完成。

**Source:** Appendix A.2-A.3; Appendix D.2.

## 10. Strengths

1. **方法简单而统一。** 不需要新的模型结构；通过统一的语言轨迹就能把 reasoning、action 和 observation 放进同一上下文。
2. **形成闭环。** Action 不只是最终输出，也可以是获取信息和改变环境的中间步骤；Observation 能影响下一轮 reasoning。
3. **跨任务泛化。** 同一范式覆盖多跳问答、事实验证、文本游戏和网页导航，只需更换 action space 与 few-shot trajectories。
4. **兼顾可解释性和诊断性。** 人可以区分模型已有的 thought 与外部环境返回的 Observation，并检查 action 为什么发生。
5. **支持在线干预。** Appendix A.3 表明，编辑 thought 可能比手工改写大量动作更直接地控制长轨迹行为。
6. **内部与外部知识互补。** CoT-SC 与 ReAct 的组合结果显示，外部检索并不需要完全取代模型内部知识。

## 11. Limitations

本节明确区分两类内容：11.1-11.3 是论文明确指出或通过实验观察到的限制；11.4-11.5 是论文没有直接证明、但根据其方法边界整理出的谨慎分析。

### 11.1 论文明确指出：Prompting and scale

- Few-shot 轨迹需要人工设计；复杂任务和大 action space 需要更多 demonstrations，而 demonstrations 很容易超过 in-context learning 的输入长度限制。
- 小模型只靠 prompting 时难以同时学会 reasoning 和 acting；PaLM-8B/62B 的 ReAct prompting 结果最差，fine-tuning 才明显改善。
- 当前实验主要依赖 PaLM-540B，而论文注明该模型当时并不公开；虽然提供了 prompt 和 GPT-3 补充实验，复现仍有模型可得性限制。

**Source:** Sec. 3.3; Sec. 6; Reproducibility Statement; Appendix A.1.

### 11.2 论文明确指出或实验观察：Action space and environment dependence

- Wikipedia API 是人为设计且能力较弱的 task-specific action space；真实系统需要额外的 action schema、执行器、错误处理和权限控制，这些不在本论文方法中解决。
- Search 结果依赖实体名和字符串匹配；非信息性结果会使 reasoning 偏离，且模型不一定能够恢复。
- WebShop 中 ReAct 仍明显低于人类（Score 66.6 vs. 82.1，success rate 40.0 vs. 59.6）。

**Source:** Sec. 3.1; Sec. 4; Table 4; Appendix D.

### 11.3 论文明确指出或实验观察：Reasoning flexibility and loops

- 交错结构提升 grounding，但也限制了 CoT 的自由推理形式；Table 2 中 ReAct 的 reasoning error 为 47%，高于 CoT 的 16%。
- ReAct 可能重复生成先前 thought/action，陷入循环；作者把它部分归因于 greedy decoding，但没有在本文中解决。
- ReAct 不是零 hallucination：Table 2 的 success false positive 为 6%，Fig. 5 还展示了 hallucinating thought 导致任务失败的例子。

**Source:** Table 2; Sec. 3.3; Appendix A.3 and D.2.

### 11.4 本笔记进一步分析：What the thought represents

论文把 thought 作为可读的语言上下文和一种不影响环境的语言 action，但没有证明它是模型真实内部状态的 faithful readout，也没有证明生成的自然语言 reasoning 就等价于稳定的 planning 或可执行的 belief state。

**Unclear / Not explicitly stated in the paper:** thought 的可解释性、faithfulness、token 成本、延迟和跨任务稳定性没有被系统量化。

### 11.5 论文边界与本笔记分析：Memory and safety boundaries

- 论文中的工作记忆主要体现在当前 trajectory context；没有持久化 memory、跨 episode memory 或独立 memory retrieval 的实验。
- 将 LLM 接到网页、物理环境或其他外部 action space 具有隐私、不当检索和有害行动风险。论文只在受限的 Wikipedia / WebShop benchmark 中规避了这些风险。

**Source:** Sec. 1; Ethics Statement; Sec. 2.

## 12. Relationship to Existing Knowledge

| Existing concept | ReAct 增加的理解 | 知识库更新 |
| --- | --- | --- |
| [Agent](../../concepts/agent.md) | Agent 可以被看作根据 trajectory context 运行的 policy；thought 是扩展 action space 中的语言动作，外部 action 才与 environment 交换状态。 | Agent 概念补充 closed-loop、thought action 和 Observation。 |
| [Reasoning](../../concepts/reasoning.md) | Reasoning trace 不只是离线解释或最终答案前的 scratchpad；它可以改变下一次 tool/environment action，并被 Observation 纠正。 | Reasoning 概念补充 grounded、interleaved reasoning 及其灵活性代价。 |
| [Tool Use](../../concepts/tool-use.md) | 工具调用可以是推理过程中的信息获取动作；工具返回的 Observation 是后续推理的输入，而不是只在任务末尾调用一次。 | Tool Use 概念补充 ReAct 的查询-观察闭环。 |
| [Planning](../../concepts/planning.md) | 计划可以通过自然语言 thought 被分解、跟踪和调整，但论文没有单独的 Planner；planning 是模型在轨迹中的一种行为。 | Planning 概念补充 language-mediated planning 与无独立规划器的限制。 |
| [Memory](../../concepts/memory.md) | trajectory context 和 thought 可表现出任务内 working-memory-like behavior（本笔记的解释）；这不等于持久化或跨任务 memory。 | Memory 概念补充这一边界。 |

与当前知识库其他方向的关系：ReAct 的 Wikipedia 交互与 [RAG](../../concepts/rag.md) 都使用外部知识，但本文采用的是由语言模型主动选择的交互式 `Search` / `Lookup` action，而不是一个独立的标准 RAG pipeline。论文没有涉及 [MCP](../../concepts/mcp.md)，也没有使用现代 function/tool-calling schema；因此不能把 ReAct 的文本 Action 直接等同于 MCP 或现代结构化工具调用。

**Source:** Sec. 2; Sec. 3.1; Sec. 5.

## 13. My Understanding

我对 ReAct 的理解是：它把“想法”提升为一种真正参与任务执行的中间语言状态，同时把“行动”提升为一种可以为推理获取证据的过程。关键收益来自二者的交替，而不是 thought 或 action 单独存在。

这篇工作也帮助区分了三个容易混淆的层次：

1. **Reasoning 是行为。** 模型生成语言 thought 来分解、比较、综合和纠错，但 paper 没有证明 thought 等于隐藏层中的完整推理状态。
2. **Planning 是轨迹中的功能。** ReAct 可以出现高层计划和子目标跟踪，但没有一个显式 Planner；计划是否稳定取决于模型、prompt、context 和 Observation。
3. **Memory 的边界在当前上下文。** 当前轨迹可以表现出 task-time working-memory-like behavior（这是本笔记的解释），但这不等于可持久化、可检索、跨任务的 Memory 系统。

因此，一个 ReAct agent 的强弱不仅取决于 LLM 的推理能力，还取决于 action space 是否能提供有用反馈、Observation 是否可靠、prompt 是否教会了正确的轨迹模式，以及模型能否在错误检索或失败动作后恢复。

## 14. Questions

### 14.1 论文明确暴露或留下的问题

- ReAct 的重复 thought/action 循环究竟主要来自 greedy decoding、prompt 结构，还是模型对环境状态的表示不足？作者只提出更好的 decoding 作为可能方向。
- 非信息性 Search 结果占 ReAct 错误案例的 23%；如何自动判断检索结果是否值得继续使用，并在失败后有效改写查询？
- 更多高质量 human-written trajectories、multi-task training 和与 reinforcement learning 的组合，能否稳定改善大 action space 和长时程任务？
- 如何在保持 grounding 的同时恢复 CoT 的推理灵活性？

### 14.2 本次阅读进一步产生的问题

- **ReAct 是否真正具有 planning？** 应该用计划一致性、子目标完成率、重规划能力还是最终任务成功率来定义和测量 planning？
- **Reasoning trace 是否等价于 Agent internal state？** 可读 thought 可能是有用的控制接口，但未必是模型真实 belief 或因果决策过程的忠实读出。
- **ReAct 和现代 tool calling 有什么区别？** ReAct 使用文本化 Action 和人工设计的 API；结构化参数、schema 验证、工具权限和执行错误重试如何改变这一范式？
- **ReAct 的 memory 实际在哪里？** 当前 context 如何随长轨迹增长、压缩或遗忘？没有 persistent memory 时，跨 episode 学习应放在哪里？
- **Observation 的可信度如何建模？** 如果工具返回冲突、过时或恶意信息，模型如何区分 evidence、noise 和 instruction？
- **Thought 的 token 成本是否值得？** 稀疏 thought、压缩 thought 或隐藏 thought 会如何影响性能、延迟、可解释性和安全控制？

## 15. Related Work

- **Language models for reasoning：** CoT 让 LLM 生成多步 reasoning；CoT-SC 通过多条 reasoning 轨迹投票提高稳定性；least-to-most、Selection-Inference、STaR、Scratchpad 等进一步研究了结构化或训练式 reasoning。ReAct 的差异在于把 action 与对应 observation 也放进 reasoning stream，使模型可以处理需要外部交互的任务。
- **Language models for decision making：** WebGPT、对话系统和 API-call 系统主要学习生成动作或调用接口，往往依赖 imitation / reinforcement learning 或 human feedback；ReAct 通过 few-shot language trajectories 学习 reasoning 与 action 的组合。
- **Embodied planning：** SayCan 让 LLM 直接提出机器人动作，再由 affordance model 结合视觉环境重排；Inner Monologue 注入环境反馈。ReAct 在此基础上强调自由、稀疏且任务相关的 language thought，而不是只重复当前环境反馈。

**Source:** Sec. 5.

## 16. Useful Quotes / Definitions

- `\hat{A} = A ∪ L`：把语言空间加入外部动作空间的形式化定义。**Source:** Sec. 2.
- `reason to act` / `act to reason`：论文对两种协同方向的简短概括。**Source:** Abstract; Sec. 2.
- Thought 不影响 external environment，也不会产生 observation；它的作用是更新后续 context。**Source:** Sec. 2.

## 17. Tags

#react #agent #llm #reasoning #tool-use #planning #observation #closed-loop #few-shot #alfworld #webshop
