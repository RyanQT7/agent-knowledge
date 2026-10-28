# LLM 驱动的微服务异常生成：研究现状与创新重合分析

## 1. 范围与证据规则

本报告以知识库已经完成的 33 篇 TSAD 论文和 6 篇微服务 / LLM 专题论文为主，复用详细精读笔记、知识档案、专题 Review 和研究问题地图。没有重新逐篇精读全部 39 篇。对本研究直接相关的生成机制、真实性验证和实验结论，优先引用已有笔记中的原文页码、章节、公式或表图定位。

证据层次采用以下标记：

- **论文事实**：来源论文实际描述的方法或实验，附原文定位。
- **作者结论**：论文作者对贡献或结果的解释。
- **实验支持**：结果实际支持的范围；不超出相应数据、任务和指标。
- **本报告分析 / 假设**：基于多篇论文得出的判断或待验证研究问题，不代表作者结论。

AMulSys 的合法全文仍未取得。本次检索到出版方 ScienceDirect 页面及摘要预览，页面标明论文发表于 *Information Fusion* 118 (2025), article 103017，DOI 10.1016/j.inffus.2025.103017；页面显示全文需授权，数据按申请提供。方法级分析因此仅引用公开摘要中的概述，不把它当作完成全文精读的证据。[出版方页面](https://www.sciencedirect.com/science/article/pii/S1566253525000909)；知识库获取记录见 [AMulSys availability](../../papers/aiops/amulsys/availability.md)。

RedLamp 是 CAPMix 的一个对照方法，但不属于本轮 39 篇已完成档案集合。为了回应指定比较，本报告按 KDD ’25 论文公开版本定点核验其方法章节；不将该定点比较冒充为完整知识档案。原文位置为 §3.2–3.6、§4.2–4.6、Appendix C；公开版本为 [arXiv:2505.20765](https://arxiv.org/html/2505.20765)。

## 2. 结论摘要

当前资料支持的结论是：相关工作已经分别覆盖了**数值伪异常生成、Trace 图生成、正常业务负载与故障注入、三模态检测 / 诊断、正常状态适应和伪标签鲁棒性**。这些工作解决的是相邻但不同的问题，不能把它们拼接后直接称为已有的“故障机制驱动的 Metric–Trace 联合异常生成”。

在本知识库的 39 篇完成精读论文中，未见一项工作同时满足以下四点：①由明确微服务故障计划条件化；②联合生成或采集同一事件下的 Metric 与 Trace；③验证两种模态的拓扑、时间和故障语义一致；④在独立真实故障事件上证明训练收益，并报告正常业务波动下的误报代价。这是对当前资料集合的证据边界，不是对全部公开文献的“全球首次”断言。

最有力的研究路径不是让 LLM 自由编写 KPI 数值，而是把它作为受约束的**场景规划器**：将架构、允许的故障动作、目标服务、负载状态和预期影响编译为结构化实验计划，再由规则、条件生成器或真实注入平台执行。LLM 是否比同信息量的规则 / 模板系统更有价值，必须通过等预算对照验证。Metric–Trace 的“看起来相似”也不等于“机制一致”；一致性验证需要有可执行的因果干预和独立遥测作为参照。

## 3. 论文能力边界对照

| 工作 | 生成 / 处理对象 | LLM 实际作用 | 故障机制依据 | 跨模态关系 | 正常业务波动与困难对照 | 真实性及下游证据 | 主要边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [TraceLLM](../../papers/aiops/tracellm/notes.md) | 微服务调用 Trace DAG | Llama-2 7B + LoRA 生成分层调用图与边字段 | 没有根因或注入计划；条件可包含深度、边数、稀有通信和高延迟 | 无 Metric / Log 联合输出 | 没有 workload 健康状态对照 | 图结构 / 条件有效性、分布距离、合成训练与真实图测试的下游图任务；PDF §§3–4, Eqs. 1, Figs. 3–7 | 结构可用不证明故障语义真实；下游任务不是异常检测 |
| [LLM-AP](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md) | 单变量连续异常窗口 | 冻结 GPT-3.5 / GPT-4o 按提示直接改写数值窗口 | 无微服务故障知识 | 无 | 使用局部上下文窗口，但无业务负载语义 | 五阶段统计 / 形态过滤；NAB 上部分 detector 提升、Autoformer 退化；PDF §§3–4, Eqs. 1–12, Table 8 | 局部形态过滤不证明生成窗口对应真实故障原因 |
| [Synthetic Time Series](../../papers/aiops/synthetic-cloud-microservices/notes.md) | EKS 微服务运行遥测：主要为 470 项 Metric，并采集日志 | 不使用 LLM | Locust 工作负载与 AWS FIS 故障动作在运行系统中执行 | 同一运行环境采集多类信号，但论文版本没有 Trace，也没有联合生成器或一致性度量 | 用趋势、多周期和噪声形成动态正常负载；另设负载乘数异常及基础设施注入 | 注入时间区间标签、指标响应示例；PDF §3, Eqs. 1–2, Algorithms 1–2, Tables 1–3, Figs. 5–6；没有 detector benchmark | 受限于两个应用、实验环境和已配置故障；未证明检测收益 |
| [GenIAS](../../papers/aiops/genias/notes.md) | 单 / 多变量数值异常 | 不使用 LLM；TCN-VAE 潜变量扰动与维度级 patch | 没有运维根因或服务调用机理 | 无 | 学习数值正常分布，但没有负载语义状态 | 9 个 TSAD 基准，ARP / EDI 及下游检测；PDF §3, Eqs. 1–6, Algorithms 1–2, Tables 1–4 | 潜空间偏离不等于具体微服务故障机制 |
| [RedLamp](https://arxiv.org/html/2505.20765) | 单 / 多变量窗口上的 11 类伪异常 | 不使用 LLM；多种时序增强 + 多类软标签分类 | 无服务故障机制；伪异常按波形操作构造 | 无 | 主要解决 anomaly contamination、false anomaly 和增强多样性，不标注 workload / release 状态 | 多数据集 VUS-PR、污染鲁棒性、消融；原文 §§3.2–3.6, 4.2–4.6 | 增强类别是人为形态类别，不是故障本体或因果类别 |
| [CAPMix](../../papers/capmix/notes.md) | KPI 数值伪异常及 detector 训练 | 不使用 LLM；CutAddPaste、DTW 软化伪标签、输入 / 潜空间 Mixup | 无显式服务故障计划 | 无 Trace | 面向 noisy / dynamic KPI；有生产案例区分部分监控伪影和持续故障，但不显式识别业务负载成因 | 33 篇集合内的多数据集对比、污染与动态环境实验、Kuaishou 案例；PDF §§3–5, Tables 2–5, Figs. 4–8 | KPI 形态鲁棒性不等于上下文语义判断或 Metric–Trace 故障生成 |
| [CAROTS](../../papers/carots/notes.md) | 因果关系保持 / 破坏的 MTS 对比样本 | 不使用 LLM | 变量因果结构被用作增强约束，但非微服务故障动作 | 数值变量关系建模，不含分布式 Trace | 区分值变化但关系保持与关系破坏；不是业务状态标签 | 合成因果系统、公开基准和消融；详见其笔记 §6 / Evidence Map | 因果依赖结构不自动等于服务拓扑或真实干预因果 |
| [MODIFy](../../papers/aiops/modify/notes.md) | 已观测的 Log + Metric + Trace 输入；检测和服务级定位 | 不使用 LLM | 有监督故障 / 根因标签；不是样本生成 | 6 秒时间对齐、模态融合、调用图 GAT；训练期 Trace diffusion 是去噪表征，不是故障合成 | 没有 workload / release context 测试 | SocialNetwork / TrainTicket 上检测、定位、消融和噪声鲁棒性；PDF §§4–5, Eqs. 1–17, Tables 2–7, Figs. 2–9 | 融合实测模态不代表联合生成；静态拓扑和已知标签依赖 |
| [AIOpsLab](../../papers/aiops/aiopslab/notes.md) | 真实运行服务的 Metrics、Logs、Traces、配置与 Agent 交互 | LLM 是被测运维 Agent，不是遥测生成器 | 测试床中受控故障动作及内部 oracle | 模态由同一运行环境采集，因而有共享事件来源；非生成器 | 正式版有两个 no-op 正常任务，多个 Agent 在其上误报；覆盖有限 | 100 个框架问题中选 48 个运行；Agent 任务准确率，PDF §§2–3, Table 3, §3.6.4 | 端到端 Agent 评测不是 detector 增强实验，也不等同生产分布验证 |
| AMulSys | 公开摘要描述的 Trace + Metric + Log 检测框架与多模态 Mixup | 公开摘要没有报告 LLM | 仅能确认摘要提及类别先验和异常样本增强，无法核验具体故障机理 | 摘要称三模态图表示和多模态增强；缺全文无法判断对齐细节 | 未知 | 出版方摘要报告两个系统、F1 > 0.97；只能作为摘要级作者报告，不能由此判断数据切分、消融或真实性验证 | 全文不可得；不作方法级结论 |
| [When Model Meets New Normals](../../papers/when-model-meets-new-normals/notes.md) / [MACE](../../papers/mace/notes.md) / [TimeRCD](../../papers/time-rcd/notes.md) | 新正常适应、多原型或序列相对上下文 | 否 | 不是故障生成 | 不含真实 Metric–Trace 对齐 | 已有方法处理统计新正常 / 多模式 / 序列上下文，但不等于业务状态语义 | 各自有 TSAD benchmark 证据；见档案与 [TSAD 问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md) | 不能把“建模多正常状态”作为宽泛的首次创新 |

### 3.1 关键定量证据及其边界

- **TraceLLM**：在合成图训练、真实图测试的特定图任务中，FIRM SVM 的准确率距真实图训练约 1.5 个百分点；这支持生成调用图的任务效用，不是故障检测收益。（PDF §4.3, Fig. 6）
- **LLM-AP**：TimesNet 上 GPT-4o、temperature 1、Append 配置报告 F1 0.7238±0.001，对照 0.6893±0.002；PatchTST 最佳值 0.7024，对照 0.6929。Autoformer 有明显退化，例如一个 Replace 配置为 0.2753，对照 0.6071。（PDF Table 8）这说明生成样本效用依 detector 而异。
- **Synthetic Time Series**：报告 25×5 个 node metric、18×14 个 Pod metric、9×10 个 service metric，共 470 项指标；论文没有检测器基准实验。（PDF §3.5, Tables 2–3）
- **GenIAS**：其数据集平均结果中，GenIAS + CARLA F1 为 .557、CARLA 为 .509；具体数据集如 MSL .579 vs .523、SMAP .620 vs .529、Yahoo-A1 .811 vs .749。（PDF Table 2）ARP / EDI 与这些 benchmark 结果均不证明微服务故障机理。
- **CAPMix**：在其采用的 Best RPA-F1 协议下，平均得分报告 60.69%，但各数据集并非总是领先；例如 ASD 为 61.30±1.96，低于 RedLamp 的 69.59±1.33。（PDF §§4.1–4.3, Tables 2–4）RPA-F1 与其他论文指标不可直接混排。
- **RedLamp**：作者报告五个 real-world dataset 上相对基线 VUS-PR 平均提高 17%；UCR 加入 5% contamination 后，VUS-PR 下降 1.8%，CutAddPaste 下降 15.5%。（RedLamp §§4.2、4.5）这些是同一 TSAD 评测设定下的 pseudo-anomaly / contamination 证据，不是微服务根因真实性。
- **MODIFy**：SocialNetwork / TrainTicket 两个 benchmark 的平均检测 F1 为 .883，平均 HR@1 为 .847；消融显示移除任一模态会改变检测 / 定位表现。（PDF §§5.6–5.7, Tables 4–5）这是多模态 detector / RCA 证据，不是生成真实性证据。
- **AIOpsLab**：正式版框架概述 100 个问题，实验选出 48 个；两个 no-op 检测任务中，除 GPT-4-W-Shell 外的受测 Agent 会把正常 workload 误报为异常。（PDF §3.1, §3.6.4, Table 3）这是一项有限任务级观察，不等价于完整 workload-state benchmark。
- **AMulSys**：出版方公开摘要报告两个微服务系统上 F1 > 0.97；因全文不可得，不引用此数值推断数据切分、类别定义、训练 / 测试泄漏、增广独立贡献或 Metric–Trace 一致性。[出版方摘要](https://www.sciencedirect.com/science/article/pii/S1566253525000909)

不同论文的数据集、阈值选择、评价粒度、split 和指标定义不同，上述数值只用于说明各自结果的证据范围，不能拼接成横向排行榜。

## 4. 对关键研究问题的回答

### 4.1 现有方法如何生成异常时间序列？

- **直接语言生成**：LLM-AP 把局部窗口和类型提示交给冻结 GPT 模型，由 LLM 生成连续数值，随后用长度、RelDTW、z-score / CUSUM、形态规则等过滤。它是目前此集合中最直接的 LLM 数值生成方法，但对象是 NAB 单变量异常，不是微服务因果故障。（LLM-AP PDF §§3.1–3.3, Eqs. 1–12, Table 2）
- **潜空间扰动**：GenIAS 学习正常 TCN-VAE 潜分布，以可学习逐维扰动尺度制造偏离，经解码后按变量动态范围 patch 回输入。（GenIAS PDF §3, Eqs. 1–6, Algorithms 1–2）
- **规则 / 形态增强**：CAPMix 建立 CutAddPaste 伪异常，按 DTW 相似度降低可能仍属正常的样本标签置信度，再通过输入和潜空间 Mixup 缓解增强伪影；RedLamp 构造 11 种时序增强类别，通过多类 soft label 和 masked reconstruction 处理伪异常及训练污染。（CAPMix PDF §§3–4；RedLamp §3.2–3.6）
- **从系统动作得到观测**：Synthetic Time Series 与 AIOpsLab 在真实运行的测试床执行 workload / fault action，由系统实际产生 Metric、Trace 或 Log。前者的指标数据集没有 detector 评测；后者的目标是 Agent 工具和任务评估，并非训练异常生成器。

### 4.2 是否已有人利用故障机理生成异常？

需要区分“机理驱动”和“可控注入”。

**已确认的相邻能力**：Synthetic Time Series 与 AIOpsLab 通过 CPU / 内存压力、网络延迟 / 丢包、服务删除或功能性故障等受控动作影响运行服务，并按动作对象和时间记录真值。这比直接改 KPI 数值更接近机制可追溯的观测生成。（Synthetic Time Series §3.4, Algorithm 2；AIOpsLab §§2.1–2.5, Table 1）

**仍未确认的能力**：两篇工作不等于 LLM 根据架构自动推导故障传播计划；它们也没有证明所有生产故障都由这些注入模板覆盖。TraceLLM 的高延迟 / 稀有通信条件不是根因规划；LLM-AP、GenIAS、RedLamp、CAPMix 的异常是数值或形态空间样本，没有可执行的服务故障动作。

### 4.3 LLM 实际负责什么？

此集合里的职责明显不同：

1. TraceLLM：将 LLM 训练成调用图条件生成器；未生成根因或故障机制。
2. LLM-AP：提示 LLM 直接改写数值窗口，五阶段规则筛选输出。
3. AIOpsLab：LLM 在实验中承担调查和操作服务的 Agent 角色；其运行环境负责故障注入和遥测采集。
4. Synthetic Time Series、GenIAS、CAPMix、RedLamp、MODIFy：不以 LLM 作为生成器或检测器。

因此，“使用了 LLM”不是一个足够精确的贡献描述。需要说明 LLM 对场景语义、动作选择、参数组合或数值生成到底承担了哪一步，并通过移除 LLM 的对照测量增益。

### 4.4 是否联合生成 Metric 和 Trace？

在本知识库的 39 篇已精读范围内，没有找到“同一故障计划条件化，联合生成 Metric 与 Trace，并用外部事件真值验证跨模态一致性”的已验证方法。TraceLLM 生成 Trace DAG；Synthetic Time Series / AIOpsLab 从共享运行环境采集遥测；MODIFy 消费已采集的三模态并进行检测 / 定位；这些能力相互补充但不能互换。

AMulSys 的出版方摘要描述三模态表示和多模态 Mixup augmentation，但这属于检测训练中的特征增强主张。没有全文时，无法验证其是否保留样本级时序 / 拓扑一致性，更不能宣称它联合生成真实 Metric–Trace 故障事件。

### 4.5 如何评价“真实”？

评价应拆成互不替代的层次：

| 层次 | 可测量内容 | 现有例子 | 局限 |
| --- | --- | --- | --- |
| 语法 / 结构有效 | Trace ID、父子关系、服务拓扑、窗口长度、字段范围 | TraceLLM 图结构；LLM-AP 格式和长度 | 有效格式不能证明真实故障 |
| 局部统计相似 | 分布、DTW、频谱、自相关、跨变量相关 | LLM-AP RelDTW；GenIAS ARP / EDI | 与同一原因的观测响应不等价 |
| 运行机制可执行 | 计划可编译、目标动作确实执行、时间和服务身份已记录 | Synthetic Time Series、AIOpsLab | 只证明特定环境和动作，不代表生产覆盖 |
| 跨模态一致 | 同一 trace / service / 时间窗下 Metric 和 Span 的关系符合已校准机制 | 当前档案集合未见生成器完成此验证 | 统计相关不是因果证明，采样 / 聚合会削弱关系 |
| 下游任务效用 | 合成训练、真实独立测试上的检测收益 | LLM-AP 部分 NAB detector、GenIAS benchmark、TraceLLM 图任务 | detector gain 不证明根因保真；需跨系统验证 |
| 真实故障泛化 | 真实或独立注入 incident、服务 / 故障模板留出、健康负载对照 | 本集合没有完整的 Metric–Trace 合成训练 / 实测故障测试链 | 是最关键且尚缺的证据 |

LLM-AP 的 Autoformer 下降说明生成收益依检测器变化；GenIAS 的 ARP / EDI 说明数值表征相近和多样不等于机制真值；TraceLLM 的合成图迁移测的是图任务而非故障检测。因而应把“分布相似”“执行真实”“跨模态正确”和“检测有效”分别报告。

### 4.6 是否已有正常波动与真实故障的困难对照？

Synthetic Time Series 同时有动态正常负载、独立负载突变和基础设施故障；AIOpsLab 有两个正常 no-op 任务。但现有证据没有构成这样一个**负载匹配矩阵**：相同正常高负载下，一组无服务退化，一组叠加下游延迟 / 资源竞争 / 超时故障，并用真实系统健康度确认差别。AIOpsLab 的 no-op 数量也不足以证明广泛的合法业务变化识别能力。CAPMix 的动态 KPI 和线上案例对形态噪声有价值，但不把外部业务上下文作为完整因果标注。（AIOpsLab PDF §3.6.4, p.9；Synthetic Time Series §§3.2–3.4）

TSAD 论文中已有多正常性、context-relative、因果关系和测试时适应路线，例如 MACE、TimeRCD、CAROTS、When Model Meets New Normals。这意味着“区分多种正常状态”并非全新问题；更具体的潜在差异是以真实业务负载 / 部署状态作为上下文，在健康高负载、故障、二者并发条件下验证 Metric 与 Trace 的增量价值。（[TSAD 研究问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md)，第 1、2、6、7 节）

### 4.7 是否在独立真实故障数据上验证生成训练收益？

各论文提供的证据不同：

- LLM-AP 在 NAB 真实序列上训练 / 测试 detector，但数据不是微服务 Trace / Metric 对，也未建立生成样本与真实根因的对应关系。
- GenIAS 在多个 TSAD benchmark 上评估合成增强收益，但不是微服务运行事件的独立故障注入验证。
- TraceLLM 用合成调用图训练、真实图测试，测试的是调用图预测类任务，不是异常检测。
- Synthetic Time Series 与 AIOpsLab 的故障来自真实运行测试床，但没有完成“生成训练数据 → 独立真实故障测试 detector”的端到端收益实验。
- MODIFy 在两个微服务基准上报告检测与定位效果；它不是合成生成器，不能证明生成增强能带来独立真实故障收益。

因此，当前最重要的实验缺口不是“再证明合成样本可以提高一个合成测试集的分数”，而是固定生成训练预算后，在 generator-held-out 的实测 fault incident 和健康负载上验证增益、误报和延迟。

## 5. 与设想方向的实质重合

| 设想中的组件 | 已有相邻研究 | 不能宣称的内容 | 可能形成的实质区别 |
| --- | --- | --- | --- |
| LLM 产生异常样本 | LLM-AP 直接生成数值；TraceLLM 生成调用图；AIOpsLab 使用 LLM Agent 操作环境 | “首次将 LLM 用于异常 / Trace 生成” | LLM 生成可执行、受拓扑约束且可被系统验证的故障计划，并证明优于同覆盖规则模板 |
| 结合微服务故障机制 | Synthetic Time Series、AIOpsLab 实施可控 fault injection；MODIFy 使用有标签微服务故障 | “首次面向微服务故障” | 把结构化故障计划与受控动作、目标实例、跨服务传播证据、实测遥测连成可追溯链路 |
| 联合 Metric–Trace | MODIFy 做 Metric / Trace / Log 检测融合；AMulSys 摘要称多模态图和 Mixup；测试床同源采集多模态 | “首次融合 Metric 和 Trace” | 样本级联合生成 / 执行，并用 topology、span timing、service mapping 和 fault timeline 量化一致性 |
| 正常负载与故障区分 | Synthetic Time Series 的动态负载；AIOpsLab 两 no-op；CAPMix、MACE、CAROTS、WMMNN 等处理不同层面的动态正常 / 伪异常 | “首次建模多种 normal” | 受控 matched-load 对照，加上 SLO/交易健康验证；分开标注 demand shift 与 service degradation |
| 条件生成模型 | GenIAS、LLM-AP 和 TSAD 多种 augmentation / latent generator | “首次生成微服务异常时间序列” | 结构化机制条件同时驱动 Metric 和 Trace，并对生成结果执行来源外的真实性验证 |
| 新数据集 / 平台 | Synthetic Time Series 与 AIOpsLab 已展示可控运行系统与遥测 | “首次真实故障注入数据” | 给出强配对正常 / 故障 / 混合矩阵、独立真实测试、统一事件级指标和可复用 schema |

## 6. 研究空白与可证伪问题

以下均为**本报告的证据缺口判断**，不是已被证明的全球空白：

1. **计划语义到观测响应的闭环**：给定相同架构、负载、根因和动作时，LLM 计划是否能在安全白名单约束下提高有效场景覆盖，而不降低动作执行率？与等量规则模板比对计划合法率、覆盖、重复度、实测影响。
2. **Metric–Trace 一致性的增量效果**：显式约束后，拓扑 / 时间违规率是否降低，且真实故障检测召回是否提高？对比只有 metric、只有 trace、无约束融合、约束融合和真实遥测。
3. **正常状态与性能退化的多轴标注**：高需求是否健康不能只由负载高低决定。需分别标记 demand shift、服务 SLO / 交易结果、故障动作与资源压力，识别“负载变化但健康”“负载相同但故障”“负载加故障”。
4. **Trace 的条件增量**：Trace 是否在高请求量、采样率足够、跨服务传播时提高召回 / 根因定位？在低流量、漏采、局部资源故障下是否无增益或引入延迟？应按采样条件分层报告。
5. **生成训练收益能否迁移到生成器之外**：按 incident、服务、故障模板和时间切分；真实 holdout 测试不能使用同一合成器或同一注入实例构造。测量 detector 迁移、健康业务 FPR 和跨负载性能。
6. **机制真实性与指标真实性是否一致**：执行了一个真实的注入动作，不保证它对目标业务造成了预期故障；必须同时验证 action executed、服务功能 / SLO 退化和观测响应，区分“注入成功但无效应”。

## 7. 结论

已有工作分别提供可复用的部件：LLM 的结构化生成与数字编辑、TSAD 伪异常增强及软标签、测试床故障注入、多模态 detector 和新正常态适应。真正需要验证的差异不在于把这些模型名称组合起来，而在于能否建立一条**故障计划 → 受控动作 / 生成 → Metric–Trace 对齐与一致性检查 → 独立实测故障检测**的证据链，并用负载匹配的健康对照显示正常波动误报下降。

建议研究主张先限于可验证范围：**“机制条件化的 Metric–Trace 故障样本构造与负载匹配评测框架”**是候选问题表述，不是已经确认的新颖性结论。若 LLM 计划器不能显著优于规则模板，论文应把贡献放在数据 / 评测设计或一致性验证，而不是把 LLM 作为必要创新。

## 主要证据入口

- [AIOps 微服务专题 Review v4](reviews/aiops-knowledge-review-v4.md)
- [TSAD 综合 Review](../reviews/tsad-final-synthesis.md)
- [TSAD 研究问题地图](../../exports/tsad-knowledge/tsad-research-problem-map.md)
- [专题论文对比表](../../exports/llm-microservice-anomaly-generation/comparison.md)
- [AMulSys 获取记录](../../papers/aiops/amulsys/availability.md)
- RedLamp 原文：[arXiv HTML](https://arxiv.org/html/2505.20765)，§§3.2–3.6、4.2–4.6
