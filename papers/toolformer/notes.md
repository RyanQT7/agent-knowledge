# Toolformer: Language Models Can Teach Themselves to Use Tools

## 1. Metadata

- Title: Toolformer: Language Models Can Teach Themselves to Use Tools
- Authors: Timo Schick, Jane Dwivedi-Yu, Roberto Dessy, Roberta Raileanu, Maria Lomeli, Eric Hambro, Luke Zettlemoyer, Nicola Cancedda, Thomas Scialom
- Year: 2023
- Venue: 37th Conference on Neural Information Processing Systems (NeurIPS 2023)
- URL / DOI: Unclear / Not explicitly stated in the paper
- Local File: [sources/papers/Toolformer.pdf](../../sources/papers/Toolformer.pdf)

阅读边界：本地 PDF 共 13 页，其中正文到第 9 页、参考文献占第 10–13 页。正文多次引用 Appendix A–G，但这些附录页面不在当前 PDF 中；下文只把正文中能够确认的附录结论标为“正文报告”，不把缺失附录的细节当作已核实内容。

## 2. One-Sentence Summary

Toolformer 让语言模型先自行采样 API 调用候选，执行这些调用，再根据调用结果是否降低后续 token 的预测损失进行筛选，最后在保留原文的增强语料上微调，从而学习何时、调用哪个工具、传入什么参数以及如何把结果用于后续生成。

**Source:** Abstract; Sec. 2; Fig. 2; Sec. 7.

## 3. Problem

Toolformer 试图解决的是：如何让一个保持通用语言建模能力的 LM，在没有大量人工 API 调用标注、也没有为每个下游任务编写专用 prompt 的情况下，主动使用外部工具。

论文首先指出，纯语言模型在算术、事实查找、最新信息、时间意识和低资源语言等方面存在明显弱点；这些任务往往可以由更小、更专门的工具处理。另一方面，已有工具使用方法通常依赖大量人工监督，或者只在预先知道“这个任务应该使用哪个工具”的 task-specific few-shot 设置中工作。这样的方式难以让模型自行决定是否调用工具、调用时机和参数。

因此，论文的目标不是单纯增加一个工具接口，而是让 LM 在保持一般语言能力的同时，自己学会选择工具、决定调用时机、生成参数并利用结果。论文把这个目标表述为一种 LM 的 self-supervised tool-use 学习问题；它没有把问题定义成一个包含独立 Planner、Executor、Memory 和 Environment 的通用 Agent 架构。

**Source:** Abstract; Sec. 1; Sec. 2.

## 4. Motivation

论文的动机可以概括为“通用性”和“专门能力”的结合：参数化 LM 擅长灵活的语言生成和 zero-/few-shot 泛化，但不擅长精确计算、事实检索或获取动态信息；外部 API 擅长这些能力，却需要模型知道什么时候调用以及如何解释返回值。

论文特别强调两点：

- Tool use 应该以 self-supervised 方式学习，而不是依赖大规模人工标注；人类认为有用的调用不一定就是模型在预测后续文本时认为有用的调用。
- 模型应保留 generality，并自行决定何时、如何使用哪个工具，而不是由任务 prompt 预先规定调用方式。

它的解决方向是利用 LM 的 in-context learning 能力生成候选 API 调用，再用模型自己的 future-token loss 作为过滤信号。这样，原始文本仍然保留，API 调用和结果只是插入到有帮助的位置。

**Source:** Sec. 1; Fig. 2.

## 5. Core Idea

Toolformer 的核心是一个“生成候选调用 → 执行 → 用预测损失筛选 → 微调”的自举过程：

1. 对每个工具提供少量如何使用 API 的示例，并为原始文本构造 prompt。
2. 让基础 LM 在文本的不同位置生成可能的 API 调用，包括工具名和参数。
3. 执行每个候选调用，得到一个文本形式的工具结果。
4. 比较模型在有“调用 + 结果”、无调用、以及有调用但无结果时对后续文本的预测损失。只有结果确实使未来 token 更容易预测的调用才被保留。
5. 将保留的调用和结果插回原始语料，得到增强数据集，并用标准 language-modeling objective 微调同一个 LM。
6. 推理时，模型照常生成文本；生成表示“等待 API 结果”的 `!` 触发标记后，外部执行器调用相应 API，把结果和 `</API>` 标记插回上下文，模型再继续生成。

用自己的语言说，Toolformer 把“外部结果是否有助于继续写对文本”当作工具调用的训练信号。模型不是被逐条人工告知“这里必须调用计算器”，而是从自己的预测损失中学习哪些调用值得插入。

**Source:** Sec. 1; Sec. 2; Fig. 2; Sec. 7.

## 6. Architecture / Workflow

### 6.1 API call representation

论文把 API call 表示为：

~~~
c = (a_c, i_c)
~~~

其中 `a_c` 是 API 名称，`i_c` 是输入。给定调用结果 `r`，论文定义了两个线性化序列：

~~~
e(c)   = <API> a_c(i_c) </API>
e(c;r) = <API> a_c(i_c) ! r </API>
~~~

`<API>`、`</API>` 和 `!` 是特殊标记；实际实现使用 `[`, `]` 和 `->` 的 token 序列来避免修改已有 LM 的词表。

这意味着工具调用、参数和返回值都被序列化成模型可以读写的文本 token。它不是现代 function-calling schema 的自动等价物：论文展示的是一种文本协议，并由外部程序负责识别标记、执行 API 和插入返回文本。

**Source:** Sec. 2 and footnote 1.

### 6.2 Training-time workflow

~~~
Plain corpus C
→ Prompt P(x)
→ Sample candidate positions and API calls
→ Execute API calls
→ Filter by future-token loss reduction
→ Interleave retained calls/results with original text
→ Fine-tune the LM on C_fl
~~~

给定一段文本 `x = x_1, ..., x_n`，模型先根据生成 `<API>` 的概率选择候选位置，再从包含 prompt、文本前缀和 `<API>` 的上下文中采样 API call。每个 API 的执行方式可以是调用另一个神经网络、运行 Python 脚本，或使用检索系统；论文只要求 API 的输入和输出都能表示为文本。

过滤阶段的关键不是单纯看 API call 是否语法正确，而是看提供调用输入和调用结果后，模型对从该位置开始的未来 token 的加权交叉熵是否至少降低阈值 `f`。比较基线取“完全不调用”和“调用但不给结果”两者中较好的损失，因此调用本身的格式不会仅凭 token 暴露就自动被保留。

保留后，论文把 `e(c;r)` 插入原文对应位置；除此之外，增强数据集包含与原始数据相同的文本。微调使用标准 LM objective，所以模型同时学习普通文本和在有帮助的位置生成 API call/result 序列。

**Source:** Sec. 2; Fig. 2; Fig. 3.

### 6.3 Inference-time workflow

~~~
Task / text context
→ Normal autoregressive decoding
→ Model emits the API-result trigger `!`
→ External wrapper executes the selected API
→ Insert textual result and `</API>`
→ Continue decoding
→ Final generated text
~~~

论文的推理过程不是每一步都显式生成 `Thought → Action → Observation`。模型可以在普通文本生成中插入 API call；当生成 `!` 时，解码被中断，执行器获取结果并把结果及 `</API>` 加回上下文。这里的“结果进入上下文”是线性化 token 序列的一部分，而不是论文定义的独立 Observation 对象。

实验解码使用 greedy decoding 的变体：当 `<API>` 属于 top-10 token 时允许开始调用，并限制每个输入最多一次 API call，以避免模型卡在循环中。这个限制属于实验设置，不应当概括为 Toolformer 的所有可能推理方式。

**Source:** Sec. 2; Sec. 4.2; footnote 3.

### 6.4 Components and the Agent boundary

- **Language model `M`**：既生成候选 API call，也根据 future-token loss 参与筛选，最后在增强语料上微调并在推理时决定是否生成 API 标记。
- **APIs / tools**：接收文本输入并返回单个文本序列。工具可以是 QA 模型、检索系统、计算脚本、翻译模型或日历服务。
- **Execution wrapper**：在训练时批量执行候选调用，在推理时检测标记、调用 API、插入结果。论文没有将其定义成独立的 Agent Executor 模块。
- **Training corpus and loss filter**：是 Toolformer 的训练数据构造机制，不是运行时的长期记忆。

**Paper states:** 论文在 Abstract、Sec. 2 和 Conclusion 中把 Toolformer 称为一个学习使用工具的 `LM`，而不是给出一个带有独立规划器、持久化记忆和环境状态的 Agent 系统。

**My interpretation:** Toolformer 可以被描述为具有工具选择能力的 tool-using LM，且在广义上具有一定自主调用行为；但仅凭“能决定何时调用 API”不足以把它直接称为完整 Agent 架构。论文没有证明它具有显式 Planner、persistent/long-term Memory，或 ReAct 式的多步 environment trajectory。

**Source:** Abstract; Sec. 2; Sec. 4.2; Sec. 6; Sec. 7.

## 7. Key Concepts

- [LLM](../../concepts/llm.md)：Toolformer 把基础 LM 同时用作候选调用生成器、损失评估器和最终工具使用模型。
- [Tool Use](../../concepts/tool-use.md)：核心是学习调用时机、调用表示、工具执行和结果注入上下文之间的接口，而不是把任意 API 调用都视作 Agent。
- [Agent](../../concepts/agent.md)：用于记录边界：Toolformer 有模型驱动的 API 选择，但论文没有定义完整 Agent-environment 架构。
- [RAG](../../concepts/rag.md)：其中 QA 工具基于 Atlas，Wikipedia Search 使用 BM25 检索；这些是被 Toolformer 调用的具体工具，不等于 Toolformer 本身就是 RAG 系统。

## 8. Method

### 8.1 Tools

论文实验使用五类工具：

| Tool | 论文中的实现/作用 |
| --- | --- |
| Question Answering | 基于 Atlas 的 QA 系统；Atlas 是在 Natural Questions 上微调的 retrieval-augmented LM。 |
| Calculator | 支持四种基本算术运算，结果总是四舍五入到两位小数。 |
| Wikipedia Search | 在 KILT 的 Wikipedia dump 上建立 BM25 索引，返回短文本片段；相比 QA 工具需要模型自己抽取相关内容。 |
| Machine Translation | 使用 600M 参数的 NLLB，将检测到的任意语言短语翻译成英语，覆盖论文所述的 200 种语言。 |
| Calendar | 不需要输入，返回当前日期，为需要时间意识的预测提供 temporal context。 |

**Source:** Table 1; Sec. 3.

### 8.2 Sampling API calls

论文对每个 API 写 prompt `P(x)`。对文本的每个位置，模型给出生成 `<API>` 的概率；超过采样阈值 `s` 的位置成为候选，若候选过多则保留 top-`k`。对每个候选位置，模型继续生成 API 名称和参数，并以 `</API>` 作为结束标记，最多采样 `m` 个候选调用。

工具的 prompt 只需要少量人工示例；但各工具的阈值和具体启发式设置依赖实验配置。正文把详细参数放在 Appendix A，而该附录不在当前 PDF 中，因此这些参数在本笔记中标为：**Unclear / Not explicitly stated in the paper**。

**Source:** Sec. 2, “Sampling API Calls”; Fig. 3; Appendix A（正文引用但本地 PDF 未包含）。

### 8.3 Executing and filtering calls

每个候选调用被执行并得到单个文本结果 `r_i`。令 `L_i(z)` 表示模型在以前缀 `z` 的情况下，对未来 token 的加权交叉熵。论文比较：

~~~
L_i^+ = L_i(e(c_i; r_i))
L_i^- = min(L_i(ε), L_i(e(c_i; ε)))
~~~

当调用及其结果使损失至少降低过滤阈值 `f` 时，保留该调用。直观上，工具结果必须让模型更容易预测接下来的原始文本；只生成一个 API call 或只看到调用输入但没有结果，都不足以满足这一标准。

在 `f = 1.0` 时，Table 2 报告保留调用的样本数分别为：Question Answering 18,526、Wikipedia Search 60,974、Calculator 994、Calendar 20,587、Machine Translation 1,034。阈值提高到 `f = 2.0` 后，数量进一步减少；这说明 filtering threshold 直接控制增强数据的严格程度。

**Source:** Sec. 2, “Filtering API Calls”; Table 2.

### 8.4 Fine-tuning

对每段原文，论文将保留的 `(call, result)` 插入相应位置，得到 `x_fl`，再把所有增强文本合并为 `C_fl`。除插入的 API 序列外，`C_fl` 保留原始文本内容。模型在 `C_fl` 上使用标准 LM objective 微调，因此它学习的是一个统一的 next-token prediction 分布，而不是一个单独训练的 API classifier。

作者使用 CCNet 子集作为 `C`，以 GPT-J 作为基础模型；正文报告的主要实验中 GPT-J 有 6.7B 参数。为降低标注成本，作者还为部分 API 使用启发式预筛选文本，例如 calculator 只考虑包含至少三个数字的文本。

**Source:** Sec. 2, “Model Finetuning”; Sec. 4.1.

### 8.5 What the model learns

从训练目标可以分解出四个不同能力：

1. **When to call**：在什么位置生成 `<API>`；由候选位置和 loss filtering 共同塑造。
2. **Which tool / what arguments**：在 API 序列中生成 API 名称和输入参数。
3. **How to represent the call**：学习论文定义的文本标记、API 名称、参数和结束标记。
4. **How to use the result**：训练目标要求插入结果后能改善对后续原始 token 的预测，因此结果作为当前 token context 的条件参与后续生成。

这四点不应与 ReAct 中由 prompt 示范出来的 thought/action 轨迹混为一谈。Toolformer 的主要学习信号是模型自己的预测损失；论文没有训练一个单独的 planner，也没有把“工具结果导致下一步显式 reasoning”作为必须生成的轨迹格式。

## 9. Experiments

### 9.1 Setup, baselines, and metrics

作者使用 CCNet 子集和 GPT-J，并对增强语料进行微调。比较对象包括：

- `GPT-J`：原始模型。
- `GPT-J + CC`：在相同 CCNet 子集上微调但不插入 API call。
- `Toolformer`：在插入 API call/result 的 `C_fl` 上微调，并在推理时启用 API。
- `Toolformer (disabled)`：同一个 Toolformer 模型，但解码时禁止 API call。
- `OPT (66B)` 与 GPT-3 的 `davinci` 变体（175B）：明显更大的外部 baseline。

下游任务采用 prompted zero-shot 设置：用自然语言说明任务，但不给数据集专用的工具使用示例。LAMA 评估预测前五个词中是否包含正确词；数学任务取生成中的第一个数字（若生成方程，则取等号后的第一个数字）；QA 检查前 20 个词中是否包含答案；MLQA 使用最多 10 个生成词；这些宽松的评测定义均由正文说明。

**Source:** Sec. 4.1–4.2; Table 3; Table 4; Table 5; footnote 4.

### 9.2 LAMA and mathematical reasoning

Table 3 的结果显示，启用工具时 Toolformer 在 SQuAD、Google-RE、T-REx 三项 LAMA 子集上的结果为 `33.8 / 11.5 / 53.5`，而 `GPT-J + CC` 为 `19.2 / 5.6 / 33.2`；在 ASDiv、SVAMP、MAWPS 上分别为 `40.4 / 29.4 / 44.0`，而 `GPT-J + CC` 为 `9.6 / 5.0 / 9.3`。Toolformer 也超过了表中的 OPT 66B 和 GPT-3 175B 数学结果。

论文报告，Toolformer 在 LAMA 例子中有 98.1% 使用 QA 工具，0.7% 使用其他工具，1.2% 不使用工具；数学 benchmark 中有 97.9% 的例子调用 calculator。数学任务中，允许实际 API 调用后性能相较 disabled 版本大幅提升，说明“在训练中见过 API 序列”和“推理时获得真实计算结果”是不同贡献。

**Paper observes:** 结果支持自监督筛选能够教会 6.7B GPT-J 在 zero-shot 任务中选择有用工具，并改善事实查找和精确计算。

**Source:** Sec. 4.2; Table 3.

### 9.3 Question answering and temporal tasks

在 QA 任务中，Toolformer 使用 Wikipedia Search 的比例为 99.3%。Table 4 报告其 Web Questions、Natural Questions、TriviaQA 结果为 `26.3 / 17.7 / 48.8`，高于 `GPT-J + CC` 的 `18.4 / 12.2 / 45.6`，但低于 GPT-3 的 `29.0 / 22.6 / 65.9`。作者将差距部分归因于简单的搜索工具，以及模型不能与搜索结果交互、改写查询或浏览多个结果。

在时间数据上，TEMPLAMA 与 DATESET 的 Toolformer 结果分别为 `16.3` 和 `27.3`。但 TEMPLAMA 中 calendar 只被使用 0.2%，提升主要来自 Wikipedia Search 和 QA；DATESET 中 calendar 被使用 54.8%，提升才可以归因于日期工具。正文还指出，“先查询日期、再把日期交给 QA”这种组合既受到每个输入最多一次调用的实验限制，也不容易从独立采样的训练数据中学到。

**Source:** Sec. 4.2; Table 4.

### 9.4 Multilingual QA

在 MLQA 上，翻译 API 对所有评测语言都带来帮助；Toolformer 使用翻译工具的比例通常为 63.8%–94.9%，但 Hindi 只有 7.3%。Toolformer 并没有在所有语言上稳定超过 GPT-J，因为在 CCNet 上继续训练本身会使部分语言的表现下降。

这组实验说明工具调用可以改善跨语言输入的处理，但也说明“模型会调用工具”不等于所有下游任务都稳定收益；基础语料分布和工具选择质量仍然重要。

**Source:** Sec. 4.2; Table 5.

### 9.5 Language modeling and scaling

作者用 WikiText 和一个未用于训练的 CCNet 子集检查微调是否损害普通语言建模能力。正文报告：在禁用 API 的推理设置下，使用 `C_fl` 训练没有相对使用 `C` 训练造成额外的 perplexity 上升；但 CCNet 微调对 WikiText 有轻微退化。这里的结论是“在作者测量的设置中没有明显损害通用 LM 能力”，不是对所有分布都不退化的保证。

Scaling 实验把方法应用到 124M、355M、775M 和 1.6B 的 GPT-2 模型，并使用 QA、calculator、Wikipedia Search 三种工具。Fig. 4 显示，约从 775M 开始模型才明显学会利用工具；较小模型的有工具/无工具表现接近，较大模型则同时提升自身能力和使用工具的能力。

正文还提到 Appendix G 将实验扩展到 LLaMA v1 7B，并报告较弱的 WikiSearch 工具在更强基础模型上效用会消失；由于该附录未包含在当前 PDF 中，这一扩展结果的具体设置和数字为 **Unclear / Not explicitly stated in the paper**。

**Source:** Sec. 4.3; Sec. 4.4; Fig. 4; Appendix G（正文引用但本地 PDF 未包含）。

### 9.6 What the experiments do and do not show

实验支持的范围是：在给定的五种文本 API、给定的 CCNet/GPT-J 训练设置和若干 zero-shot benchmark 中，loss-based filtering 能产生有用的工具调用，并在不明显损害所测语言建模能力的情况下改善部分任务。

实验没有证明：Toolformer 能处理任意 API、能可靠规划长链调用、能交互式浏览搜索结果、能处理恶意/冲突返回值、具有 persistent memory，或已经构成通用 Agent。尤其是“工具结果帮助预测文本”这个训练判据，不等于结果在现实任务中一定正确或安全。

## 10. Strengths

- 用模型自身的 future-token loss 产生调用筛选信号，减少大规模人工调用标注的需要。
- 同时学习“是否/何时调用”“调用哪个工具”“生成什么参数”以及“如何把返回结果放入后续文本”。
- 增强语料保留原始文本，且 `Toolformer (disabled)` 对照可以区分 API 结果的实际作用与仅仅暴露 API 序列的作用。
- 在多个不同性质的任务上采用 zero-shot 评测，展示方法不是只针对单一 benchmark 的 prompt 技巧。
- 通过模型规模实验揭示：工具接口可用不代表小模型就能有效使用它，基础模型能力是重要条件。

**Source:** Sec. 1; Sec. 2; Sec. 4; Fig. 4.

## 11. Limitations

### 论文作者明确指出的限制

- **不能可靠地链式使用工具。** 各工具的 API call 独立生成，微调数据中没有学习“一个工具输出作为另一个工具输入”的 chained use。
- **不能交互式使用工具。** 对搜索引擎尤其如此：模型不能浏览多个结果、改写不好的 query 或根据中间结果继续探索。
- **对输入措辞敏感。** 模型是否调用 API 受 exact wording 影响。
- **样本效率不高。** 处理一百多万篇文档可能只得到几千个有用的 calculator 调用示例。
- **没有把工具调用成本纳入决策。** 当前过滤准则关注预测损失改善，不考虑工具本身的计算成本。

**Source:** Sec. 6.

### 基于论文的进一步判断

- loss 降低是“有助于预测后续文本”的代理目标，不自动等于工具结果正确、可验证或对用户任务最有用；论文没有对这一代理目标的 calibration 或安全性作完整证明。
- 文本 API 标记能工作，但论文没有定义通用 schema validation、权限控制、认证、参数类型检查或错误恢复，因此不能直接把它等同于现代 structured tool calling 或 MCP。
- 论文的 LM 微调和单次/非交互式调用机制没有持久化 Memory、显式 Planner 或完整 Environment state；把它称为通用 Agent 需要超出论文证据的额外定义。

## 12. Relationship to Existing Knowledge

### 12.1 ReAct 与 Toolformer 的共同点

两者都让语言模型使用外部工具，并且都允许模型根据当前文本上下文决定调用时机和参数；工具返回的信息也都会以文本形式影响后续生成。因此，两者都说明 Tool Use 不必只能是任务末尾的一次固定检索。

### 12.2 ReAct 与 Toolformer 的核心区别

| 维度 | ReAct | Toolformer |
| --- | --- | --- |
| 主要机制 | 推理时用 prompt 让模型交错生成 Thought、Action，并接收 Observation。 | 训练时采样 API call，用执行结果对 future-token loss 过滤，再微调 LM。 |
| 调用何时学会 | 主要通过人工示范轨迹和当前 trajectory context，在任务执行时决定；ReAct 论文也另行探索了轨迹微调。 | 通过自监督增强语料学习生成 API 标记的位置；推理时按 token 生成触发。 |
| 调用表示 | 实验中的文本 `Search` / `Lookup` / `Finish` Action。 | `<API> name(input) ! result </API>`，实际用 `[`, `]`, `->` token 表示。 |
| 结果角色 | Action 后的 Observation 是下一次 Thought/Action 的外部反馈。 | API response 是插入线性 token context 的文本，训练目标是帮助预测后续原文 token。 |
| 交互形态 | 核心价值在运行时的 thought-action-observation 闭环，可根据结果改写查询或继续行动。 | 当前方法不支持可靠的 chained / interactive tool use；评测还限制每个输入最多一次调用。 |
| 架构判断 | 明确研究 agent-environment interaction，但没有独立 Planner/Memory 模块。 | 论文主要提出 tool-using LM 的训练方法，没有定义完整 Agent runtime。 |

因此，ReAct 和 Toolformer 不是同一种 Agent 架构。更准确的说法是：ReAct 主要把 reasoning 与 acting 组织成运行时闭环；Toolformer 主要把“何时以及如何调用文本 API”蒸馏进 LM 的 token-generation policy。两者可以组合研究，但 Toolformer 本身不能因为有 API 调用就自动被命名为 ReAct Agent 或完整 Agent。

**Source:** Toolformer Sec. 2, Sec. 5–6; ReAct 论文笔记的 Sec. 5–8；Toolformer reference 对 Yao et al. (2022) 的列举。

### 12.3 与当前知识库的关系

- [Tool Use](../../concepts/tool-use.md)：Toolformer 补充了跨论文的重要区分：调用时机的学习、调用的文本表示、结果进入上下文的方式，以及运行时是否形成可交互 trajectory。
- [Agent](../../concepts/agent.md)：Toolformer 提供了一个边界案例——有自主 API 选择并不自动意味着完整 Agent-environment system。
- [RAG](../../concepts/rag.md)：QA 和 Wikipedia Search 是被调用的检索型工具；Toolformer 是学习使用这些工具的 LM 方法。
- [ReAct 论文笔记](../react/notes.md)：ReAct 是最直接的对照，尤其适合继续研究 learned tool-use policy 与 runtime trajectory 的组合。

## 13. My Understanding

我把 Toolformer 理解成一种“把工具使用编译进语言模型生成过程”的方法：模型先在训练数据上尝试 API call，只有当真实工具结果改善它对后续文本的预测时，调用才进入微调语料。经过微调后，调用时机、API 名称、参数和结果读取都表现为同一套 token prediction 行为。

这和 ReAct 的差别在于反馈的组织方式。ReAct 的重点是一个正在运行的任务轨迹：Thought 提出下一步，Action 改变或查询外部环境，Observation 再直接约束下一步 Thought。Toolformer 的重点则是训练一个能在普通文本中插入 API call 的 LM；它可以获得外部结果，但当前论文没有建立 ReAct 那样可靠的多步交互、查询修正或显式 reasoning trajectory。

因此，Toolformer 最稳妥的分类是 **self-supervised tool-augmented language model**。它对 Agent 的重要贡献是展示了工具调用策略可以从模型自身的预测反馈中学习；是否把这种模型称为 Agent，还需要额外说明 Agent 的边界和运行时能力。

## 14. Questions

### 论文留下的问题

- 如何通过迭代式数据增强让模型真正学习 chained tool use？**Source:** Sec. 6。
- 如何让模型交互式浏览搜索结果、改写 query 并根据中间结果继续调用？**Source:** Sec. 6。
- 如何降低某些工具（论文以 calculator 为例）的样本效率？**Source:** Sec. 6。
- 如何在选择 API 时同时考虑预测收益和工具的计算成本？**Source:** Sec. 6。
- 论文中引用的 Appendix A–G 具体如何设置筛选、微调、prompt、附加实验？当前本地 PDF 未包含这些附录，细节为 **Unclear / Not explicitly stated in the paper**。

### 基于论文进一步产生的问题

- loss-based filtering 与真实任务正确性、事实 grounding 和工具结果可信度之间的关系是什么？是否需要独立的 utility / calibration 信号？
- Toolformer 学到的调用时机和文本 API 格式，能否迁移到未在增强语料中出现的新工具？
- 如何把 Toolformer 的文本 API 标记映射到 structured tool calling / MCP，同时保留它学到的调用时机，并加入 schema、权限和错误处理？
- Toolformer 的 inline API result 与 ReAct 的 Observation trajectory 能否组合成既会调用又会多步交互的 Agent？
- 什么样的额外运行时能力（目标、环境状态、执行器、记忆或可验证计划）才足以把 tool-using LM 称为 Agent？
- 当工具结果过时、冲突、错误或恶意时，模型如何识别并恢复？

## 15. Related Work

论文将自己的方法放在五条线索中：

- **Language-model pretraining with additional information：** 以往方法通常无论是否有帮助都提供 metadata、markup 或检索文本；Toolformer 学习自己请求可能有用的信息。
- **Tool use：** 既有工作一类依赖大量 human supervision，另一类依赖已知具体工具用法的 task-specific few-shot prompt；Toolformer 试图用 self-supervised filtering 避免这两种限制。
- **TALM：** 与 Toolformer 最接近，使用类似的 self-supervised objective 教模型使用 calculator 和 search engine，但论文指出 TALM 主要在下游任务微调设置中探索。
- **Bootstrapping / self-training：** Toolformer 在过滤自己的预测后，用这些预测继续训练自身，属于以模型生成结果构造训练数据的自举思路。
- **ReAct：** 论文将 Yao et al. (2022) 列为 tool-use 相关工作；本知识库中的[ReAct 笔记](../react/notes.md)记录了它与 Toolformer 在运行时 trajectory 上的差异。

**Source:** Sec. 5; References.

## 16. Useful Quotes / Definitions

- API call：`c = (a_c, i_c)`，其中 `a_c` 是 API 名称，`i_c` 是输入。**Source:** Sec. 2。
- 含结果的线性化调用：`e(c;r) = <API> a_c(i_c) ! r </API>`。**Source:** Sec. 2。
- 过滤原则：只有当调用及其结果使模型对未来 token 的 loss 至少降低 `f` 时才保留。**Source:** Sec. 2, “Filtering API Calls”。
- Toolformer 的论文定位：一个以 self-supervised 方式学习使用不同工具的 LM。**Source:** Abstract; Sec. 7。

## 17. Tags

#tool-use #tool-augmented-lm #self-supervised-learning #api-calls #zero-shot #language-model #ReAct-comparison #agent-boundary
