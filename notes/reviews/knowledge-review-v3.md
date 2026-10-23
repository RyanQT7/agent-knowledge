# Knowledge Review v3

## Scope

本次 Review 聚焦首批三篇 TSAD 论文的已完成笔记与知识卡片，不重新解析 PDF：

- [CAPMix](../../papers/capmix/notes.md) — Robust KPI Anomaly Detection for AIOps in Noisy and Dynamic Environments
- [When Model Meets New Normals](../../papers/when-model-meets-new-normals/notes.md) — Test-Time Adaptation for Unsupervised Time-Series Anomaly Detection
- [CAROTS](../../papers/carots/notes.md) — Causality-Aware Contrastive Learning for Robust Multivariate Time-Series Anomaly Detection

关注的问题是正常状态变化、正常业务波动与真实异常的边界、各方法使用的证据类型，以及哪些解释和部署结论尚缺实验支持。本文明确区分：

- **Paper-backed fact：** 可追溯至单篇笔记中的原文小节、公式、图表或附录。
- **Cross-paper synthesis / current interpretation：** 基于多篇笔记形成的当前认识，不归为任一作者的正式主张。

本仓库当前没有与 TSAD 直接对应的独立 `concepts/` 文档；这批材料仍在扩充，尚不把阶段性结论提升为稳定通用定义。通过 INDEX、逐篇笔记、卡片和本 Review 进入现有知识库。

## 1. What I Understand So Far

### Paper-backed fact

三篇文章在不同阶段改善检测器对正常性的处理：

- CAPMix 在**训练阶段**生成 CutAddPaste 伪异常，以训练窗均值序列作 DTW 正常中心，将离正常中心较近的伪异常软标注，并在输入和 TCN 表示层 Mixup。（[CAPMix note](../../papers/capmix/notes.md), §§6–8; Eqs. (2)–(7), Tables 3–4）
- When Model Meets New Normals 在**测试流阶段**用 EMA 跟踪窗口趋势、做去趋势重构，再仅用模型预测正常的点做在线更新。（[When Model Meets New Normals note](../../papers/when-model-meets-new-normals/notes.md), §§6–7; Eqs. (2)–(4), Algorithm 1）
- CAROTS 在**训练阶段**从正常数据估计 Granger 预测图，用 CPA 构造因果保持正例、CDA 构造因果破坏负例，以 SOC 学习表示，并结合正常嵌入质心距离与因果预测残差评分。（[CAROTS note](../../papers/carots/notes.md), §§5–8; Eqs. (1)–(7), Tables 1–4）

### Cross-paper synthesis / current interpretation

本批把正常性建模推进了三个不同方向：

1. **形态与伪标签可信度（CAPMix）：** “像不像正常波动”被转成合成样本与训练正常中心的 DTW 距离。
2. **时间分布与适应状态（When Model Meets New Normals）：** “测试流中的正常分布是否已变”被转成趋势状态与在线更新。
3. **变量间关系（CAROTS）：** “数值变化是否仍遵守正常运行的预测性联动”被转成因果图增强、嵌入和预测残差。

三条路线互补，但都没有单独证明“业务负载变化与故障同时发生时，系统能稳健区分并解释来源”。

## 2. Cross-Paper Relationships

| Paper | 主要作用阶段 | 正常性的依据 | 异常 / 变化处理机制 | 重要证据边界 |
| --- | --- | --- | --- | --- |
| CAPMix | 训练期数据增强与分类 | KPI 窗口的形态、单一均值中心的 DTW 距离 | 对近中心伪异常软标签；双空间 Mixup 缓和注入分布偏移 | 中心假设多数正常且单一；主结果报告阈值扫描 Best RPA-F1；业务波动原因未条件化 |
| When Model Meets New Normals | 测试期在线适应 | EMA 趋势与当前检测器的重构模式 | 去趋势后重构；预测正常点参与梯度更新 | 正常比例和伪标签可靠性是假设；全窗口也更新趋势；阈值与 WADI 附录结果有报告问题 |
| CAROTS | 训练期图发现、增强与对比学习 | 训练正常期的 Granger 预测关系及其保持性 | CPA 保持关系、CDA 扰动关系、SOC 保留多个语义正例模式；可附加因果残差分数 | 假设因果结构稳定；现实图无真值；WADI 上双分数融合弱于只用对比分数 |

**Cross-paper synthesis / current interpretation：** CAPMix 与 CAROTS 都通过训练期合成样本扩充边界，但增强所表达的语义不同：CAPMix 主要按时间窗形状和 DTW 相似度校准伪异常，CAROTS 则以估计的跨变量关系定义“保持正常”与“破坏关系”。When Model Meets New Normals 不是同类训练增强，而是在推理期改变趋势与模型参数；其动态适应可以补足静态训练分布，却增加伪标签反馈和异常吸收风险。

因此这些工作并非三个同义的鲁棒性方法，也不能互换为一种机制：一个校准合成监督，一个跟随变化后的统计状态，一个利用跨变量预测关系。把三者组合为训练增强 + 在线适应 + 因果评分是可能的研究假设，本批未验证该组合的收益、稳定性或成本。

## 3. Concept Boundaries

### “新正常”不等于“已证实无故障”

**Paper-backed fact：** When Model Meets New Normals 明确指出，远离训练分布的测试点既可能是新正常，也可能是异常；方法假设测试点中正常更多，再以预测掩码保护参数更新。（[note](../../papers/when-model-meets-new-normals/notes.md), §§7.2–7.3, 11）

**Cross-paper synthesis / current interpretation：** 检测器判断“可学习”是一种伪标签规则，不是业务真值。误报的新正常不会更新模型，漏报的故障可能进入更新；分布漂移本身不能决定一个点的业务语义。

### 正常幅度变化与正常关系变化

**Paper-backed fact：** CAPMix 通过输入窗口统计结构化形态扰动，并依据 DTW 中心距离修正标签；CAROTS 的热浪—空调例子说明变量数值可变化而驱动—响应仍保持。（[CAPMix note](../../papers/capmix/notes.md), §8.2; [CAROTS note](../../papers/carots/notes.md), §3, §6.2）

**Cross-paper synthesis / current interpretation：** “数值形态不像旧数据”和“变量关系不再成立”是两种不同异常证据。前者易混淆正常负载位移；后者有解释关系的潜力，但要求输入变量充分、估计图可靠且正常机制稳定。

### 因果关系分数与故障解释

**Paper-backed fact：** CAROTS 将 Granger 预测误差及嵌入距离作为检测分数；作者承认未建模混杂和外生变量，并把动态因果结构作为未来方向。（[CAROTS note](../../papers/carots/notes.md), §§6.1, 6.5, 10）

**Cross-paper synthesis / current interpretation：** 违反预测性依赖可以指出“哪些序列关系不符合训练期”，但不等同于识别引起波动的业务事件、根因或责任组件。CAPMix 和 EMA 适应更直接优化误报/边界，对波动来源的解释更少；CAROTS 提供结构化依赖证据，但没有 Trace、发布或负载事件的归因链。

### 多种正常模式与单一中心

**Paper-backed fact：** CAPMix 的 LR 用训练窗口均值中心；论文没有报告多中心或按运行模式分组。CAROTS 用 CPA 产生多样正常变体并用 SOC 延后纳入低相似正例；When Model Meets New Normals 的 EMA 跟踪均值、参数更新学习剩余动态，但不显式命名工作状态。（各 note §§6–7、8）

**Cross-paper synthesis / current interpretation：** 本批最明确保留语义多样性的设计在 CAROTS 的 SOC，但其语义差异被认为共享固定因果关系；这不等于识别了“日常峰值 / 夜间低负载 / 发布期”等业务模式。显式多模式状态建模和模式条件化的误报控制仍是开放方向。

## 4. Key Mechanisms

### 4.1 训练期构造可控边界：CAPMix 与 CAROTS

CAPMix 针对合成异常过于接近正常或过于夸张的两类 Anomaly Shift：DTW 标签修订对应近正常、标签不确定样本，Mixup 对应训练边界过度依赖极端注入样本。CAROTS 直接以因果预测器生成“原因变化但后果随之重算”的正样本，以及“图子集被扰动”的负样本。

两者都说明 synthetic anomaly 并非自动等于高质量监督：生成操作决定模型学到的“正常/异常”分界。它们的增强方法均已有明确相邻路线：CAPMix 复用 CutAddPaste、与 RedLamp 等异常增强方法比较；CAROTS 的新意是按因果保持/破坏机制组织对比增强，且它明确置于既有 Granger/因果 MTSAD 研究背景下。不能据这三篇笔记宣称“异常合成”或“因果异常检测”整体尚无人研究。（对应 note：CAPMix §§8, 12, 15；CAROTS §§4, 11, 14）

### 4.2 测试期学习新状态：When Model Meets New Normals

EMA 抵消整体趋势项，模型更新从预测正常点学习更复杂动态；消融中趋势与 TTA 单独使用各有问题，MSL P-15 上 TTA-only 明显退化，联合方法改善。这证明趋势处理和参数适应在所测设置中互补，却不能保证异常不会被误纳入更新。论文中包括在线 RNN-AD、FITNESS 等已有概念漂移适应背景，因此“在线适应 TSAD”不是本批新提出的空白；更具体的可研究问题是有业务代价约束的安全筛选、校准与因果上下文。（对应 note：When §5, §7, §9, §11, §15）

### 4.3 证据层级：点形态、时间状态、结构关系

当前可以把三类检测证据分层阅读：

- **局部观测形态：** 时序片段、点/上下文异常形状、到正常中心的距离。
- **随时间更新的统计状态：** 当前分布趋势、重构模式和在线适应状态。
- **跨变量预测关系：** 哪些变量按正常机制响应，以及模型预测误差是否增加。

这是一种 Review 的组织框架，不是三篇作者共同定义的 taxonomy。若实际系统只有 KPI/metric 时序而无负载、trace、发布信息，第二、三层仍只能说明“指标如何变”或“指标联动是否符合历史”，未必说明“为什么业务会变”。

## 5. Common Misconceptions

- **新分布就是异常：** When Model Meets New Normals 明确把 test normal 与 anomaly 的语义歧义作为挑战；漂移检测不能替代故障判定。
- **预测正常掩码就保证安全更新：** 这是自监督伪标签，不是标签验证。论文依赖多数样本正常，未系统评估持续漏报后的污染闭环。
- **更多合成异常就代表更鲁棒：** CAPMix 的 Anomaly Shift 和 CAROTS 对 CPA/CDA 的消融都显示增强机制及标签含义重要；生成数据不能自动覆盖真实未见故障。
- **低误报等于解释正常波动来源：** CAPMix 和 EMA 适应主要在学习边界或适应状态；CAROTS 的预测依赖违反信号也不直接定位发布、业务负载或外部事件。
- **Granger 图等同物理因果真值：** CAROTS 从预测关系中估图；按时间块图相似度高证明结构估计一致，不证明边的因果正确性，也不证明跨模式不变。
- **融合多个 anomaly score 必然提高性能：** CAROTS 的 WADI 表中完整模型低于只用对比分数；融合需要数据集与阈值层面的证据。（CAROTS note §§8.1, 8.3, 10）
- **报出 Best F1 / Best RPA-F1 就代表线上告警有效：** CAPMix 报 threshold sweep 的 Best RPA-F1，When Model Meets New Normals 的阈值与附录有口径问题，CAROTS 的 best F1 阈值协议未完全说明。必须单独检查离线最优阈值、固定阈值和可部署校准。（各 note §8–9, §11）

## 6. What These Papers Explain Well

- 正常性不是单一固定分布：分布、趋势、形态及变量关系都可能变化。
- 训练期增强、测试时适应、因果感知建模分别处理不同失败模式；各自消融能暴露机制收益和短板。
- “正常波动”可以用高幅值但符合因果响应的变化作为结构化概念，而不只用点值范围刻画。（CAROTS 的热浪—空调例子）
- 多种评价指标能揭示 point-adjusted 与逐点指标、阈值选择和排序质量之间的区别；数字口径冲突应被记入后续复核，而非被总结语句覆盖。

## 7. What They Do Not Yet Explain

以下判断限定为本批三篇文章的证据，不代表对全部 TSAD 文献的完整检索结论：

- **负载变化与故障并发：** 没有一篇提供系统构造和评估“业务负载上升 / 发布 / 扩缩容与真实故障同时发生”的实验。CAPMix 有一个生产案例，CAROTS 有因果保持正常变化的动机示例；这些不等于并发冲突实验。
- **波动来源解释：** 本批方法没有把业务 workload、deployment events、trace 或运维动作作为成套上下文输入来校准告警。CAROTS 增加跨变量关系证据，但未生成业务事件根因解释。
- **多模态正常状态：** CAPMix 的单均值中心存在多模态边界；EMA 方法连续适应但不输出模式语义；CAROTS 的 SOC 能保留相似因果下的语义簇，却假设因果结构静态。尚未证明它们能发现、命名和比较线上业务状态。
- **安全适应：** TTA 可能吸收漏检异常；全窗口 EMA 也可能受突发点影响。在线回滚、异常污染界限、恢复旧模型和人机反馈策略缺少系统验证。
- **因果正确性：** 合成系统的机制明确，但真实基准没有因果图真值；季度图相似度不是 ground-truth validation。
- **无标签工作阈值：** CAPMix 主要以 Best RPA-F1 汇总，When Model Meets New Normals 使用训练阈值与测试标签基线的协议不完全相同并存在 WADI 计数冲突，CAROTS 的 best F1 口径未完全说明。现有结果不足以直接给出业务成本下的部署保证。

## 8. Open Questions

### 本 Review 更新的问题状态

以下状态只对应本批证据，未来论文可以进一步修订：

| Question | Status | Current understanding |
| --- | --- | --- |
| 如何区分正常业务波动与真实故障？ | Partially Answered | CAPMix 用形态/DTW 与软标签处理模糊伪异常；WMMNN 用趋势和预测正常更新适应新状态；CAROTS 用变量因果关系变化作异常信号。但没有真实业务负载变化与故障共现的系统测试。（本 Review §§2–3） |
| 多种合法运行状态如何建模？ | Partially Answered | CAROTS 的 CPA + SOC 能覆盖共享关系下的多种语义正例；WMMNN 学新状态，CAPMix 的单一均值中心可能受限。显式工作模式识别与状态切换验证仍开放。（本 Review §3） |
| 指标异常分数是否能解释波动来源？ | Partially Answered | CAROTS 比纯数值分数多给出跨变量预测关系证据，但没有事件、workload、trace 的根因 attribution；另外两篇主要优化检测 / 适应。（本 Review §§3, 7） |
| 是否利用 Metric、Trace、业务负载和运行上下文？ | Open | 当前三篇都以时序指标为核心；CAROTS 明确把 exogenous variables/context 作为未来方向。没有成套使用 Trace 或业务事件上下文的验证。（本 Review §7） |
| 正常状态变化与真实故障同时发生时如何安全处理？ | Open | WMMNN 的伪正常更新可能吸收漏报，CAROTS 假设静态因果机制，CAPMix 未显式条件化负载；缺少并发条件实验。（本 Review §7） |
| 哪些方法机制已被提出，哪些仍可作为空白？ | Partially Answered | 伪异常增强、在线漂移适应、Granger/因果异常检测均有先行路线；本批更具体的差异是各自的软标签 / EMA+mask / 因果增强+SOC。新的 gap 需要超出这些已报道机制。（本 Review §4） |
| 哪些结论缺少实验支持？ | Partially Answered | 真实因果图正确性、业务并发条件、线上安全阈值、长时间更新和跨组织迁移都未充分验证；WADI 指标报告本身还需复核。（本 Review §7） |

相关原始问题与历史保留在 [notes/questions.md](../questions.md) 的 CAPMix、When Model Meets New Normals 和 CAROTS reading sections。此 Review 补充当前状态，不删除原始提问。

## 9. Current Mental Model

**以下是本批跨论文形成的阅读框架，不是标准 TSAD 架构，也不是三篇论文共同提出的 pipeline：**

```text
观测到的多变量时间序列
   ├─ 形态证据：窗口、变化形状、到正常表示的距离
   ├─ 时间状态证据：趋势、分布迁移、在线更新状态
   └─ 关系证据：变量间预测依赖与因果结构偏离
                  ↓
       分数校准 + 业务上下文 + 当前状态
                  ↓
         对异常告警进行阈值决策
                  ↓
   独立核验：发布 / workload / Trace / 故障事件 / 运维反馈
```

当前三篇主要验证上半部分的时序证据和部分分数校准。框架中“业务上下文”“异常事件核验”是待验证的系统要求，不是已由论文实现的模块。

## 10. Next Learning Priorities

下一批按用户指定顺序先读 CrossAD 与 Fortifying Time Series；第三篇优先补充多模式正常性建模，以便与本批三个证据轴形成对照。后续 Review 再把以下方向放到共同证据表中：

1. 跨尺度与跨窗口的关联是否显式表示动态业务状态，还是仍从输入序列的统计关系得分。
2. 鲁棒检测的认证范围、扰动威胁模型和真实运行波动之间有什么边界。
3. 多种正常模式能否被显式表示、切换和解释；它与在线 TTA、因果关系不变性的适用条件如何不同。
4. 对每个候选研究空白，持续检查 33 篇论文中是否已有方法或实验回答，避免把已存在的技术方向重新命名为创新点。
