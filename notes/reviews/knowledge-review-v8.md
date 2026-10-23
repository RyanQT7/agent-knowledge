# Knowledge Review v8：TSAD batch 6 — 扰动对比、三域定位与非紧邻重建

## Scope and Evidence Labels

本次覆盖第 16–18 篇，累计 **18/33** 篇全文精读：

- [TriAD](../../papers/triad/notes.md)：三域表示、contrastive learning、候选窗和 discord discovery。
- [PCRTA](../../papers/pcrta/notes.md)：perturbation classifier pseudo-labels 和 LOF representation score。
- [Sub-Adjacent Transformer](../../papers/sub-adjacent-transformer/notes.md)：对 target 重建使用非紧邻 attention band。

将**论文事实**、**跨论文归纳**、**已读范围内的缺口**与**分析推断**分开。三篇的 datasets、阈值和指标不同，结果不能直接排行。

## 1. 本批机制对比

| 方法 | 核心异常证据 | 训练 / 参照机制 | 推理输出 | 关键任务假设 |
| --- | --- | --- | --- | --- |
| TriAD | 不同域中窗口 embedding 对其余窗口的 dissimilarity | temporal / frequency / residual encoder；perturbed windows 作 intra-domain negatives；域间 contrast | 每域 top-1 candidate window，normal-train comparison 后局部 MERLIN variable-length discord，再投票 | UCR 每条 test series 一个 anomaly event，$Z=1$ |
| PCRTA | 原始与扰动 views 的低维 LOF embedding density | 7 类原始 / synthetic perturbation classifier 及 pseudo-label guided contrastive learning | 七个 view 的 LOF average，每个窗口 score 对应最后一个时刻 | 固定 perturbation family 能代表异常相关变化；F1 用枚举阈值 |
| Sub-Adjacent | 重建误差与时间 attention sub-adjacent contribution 的组合 | 对指定 $[k_1,k_2]$ 时间 band 的 attention 权重加正则；dynamic Gaussian score | 逐点 score，threshold 后输出 labels | 正常点可由非紧邻上下文重建，异常较难；窗口长度 / band 适用 |

三篇都把“异常是什么”转换为人为指定或学习到的统计偏离：域间窗口相似度低、扰动类别难判 / LOF 离群、非紧邻重建失败。它们的 evidence unit 并不相同，不能笼统归类成 contrastive anomaly detection 或 robust TSAD。

## 2. 论文直接支持的结论

### 2.1 TriAD

- temporal raw、frequency amplitude/phase/power、periodic residual 三种输入；dilated residual CNN 将每域 embedding 压到 $\mathbb R^L$。（§III-B, Table I）
- intra-domain loss 把原始窗口和同域增强窗口分别作 positive candidates / negatives；inter-domain loss 使 representation 保持域特异性；两项按 $\alpha$ 加权。（§III-C, Eqs. 5–7）
- UCR 250 条单事件测试序列；Table III 报告 PA%K F1 .233±.009、Affiliation F1 .729±.014。62 个最短 UCR series 的 MERLIN++ 比较中，TriAD tri-window .681 accuracy / .99 min，MERLIN++ .424 / 14.5 min。（§IV, Tables III–IV）
- residual encoder 的 ablation 贡献小于 temporal/general 与 frequency encoder；论文提到 window vote 与 discord vote 尚无 normalization / sophisticated weighting，并演示异常占 search window 多数时的 fallback。（§IV-D, §IV-G, Fig. 9, p.11）

### 2.2 PCRTA

- 六个 perturbation 覆盖 point / contextual / collective 三种 synthetic anomaly；分类网络通过 transform ID 学 7-way class，低维 projection 后由 pseudo-label 选 same-class top-$k$ positives 与 other-class negatives。（§III-C–D, Eqs. 2–8）
- 最终 score 是原始及六个 augmentation embeddings 上 LOF scores 的平均值，不是 classifier misclassification probability。（§IV-A–B, Eq. 9）
- Table 2 六集 F1 / AUC-PR 为 WaQ .784/.794、DSADS .943/.960、Epilepsy .934/.964、ASD .927/.933、SMD .987/.988、SWaT .978/.996；Table 3 显示 pseudo label / classifier loss / contrastive loss 多数对三集结果有帮助。（Tables 2–3, PDF pp.6–7）
- 作者枚举 score threshold 计算 best F1；由此得到的 F1 与 AUC-PR 一个是 best-case oracle operating point、一个是阈值曲线聚合，部署时不能将二者等同。（§IV-A）

### 2.3 Sub-Adjacent Transformer

- contribution 定义为 attention matrix 中相距 $[k_1,k_2]$ 的非紧邻时间 band 权重；对 $Q,K$ 单独 row-softmax、可学习 temperature 的 linear attention 及 circular indexing 构造期望 band。（§3.2, Eqs. 1–4）
- loss 将重建误差与 $-\lambda\|SACon(A)\|_1$ 组合，point score 为 $Softmax(-SACon)$ 乘 reconstruction error，再以动态 Gaussian tail score 变换。（§3.3, Eqs. 5–7）
- 在 6 real + NeurIPS-TS synthetic benchmark 上报告主表；ablation 支持 non-adjacent band、attention mapping 和 dynamic scoring 的贡献。（§4, Tables 2–8）
- main F1 使用 point adjustment，threshold 通过 best test F1 选择；multi-entity dataset 使用 pooled single model，而部分 baseline per entity 独立训练。（§4.2–4.4）

## 3. 三篇的共性与差异

### 扰动信息何时算异常证据？

- TriAD 把 jitter / magnitude warping 的局部结果直接当作同域 representation negatives；它依赖扰动能覆盖异常特征而不把主要正常变化过度分离。（§III-A, C）
- PCRTA 更显式学扰动类别，但 classifier 的 pseudo-label 负责 pair selection；最终 score 仍通过 LOF 测试原始 / synthetic views 的 embedding density。（§III-C–D, §IV-B）
- Sub-Adjacent 不合成扰动；通过禁止紧邻重建让异常变难重建。它的“扰动”是结构化 attention constraint，不是样本 transform。（§3.2–3.3）

**综合判断**：扰动表征不是一个单一机制。需要区分 augmentation 作为正样本不变性、作为 anomaly-like hard negative、作为伪标签来源，以及通过受限上下文间接制造 reconstruction difficulty。

### 从统计分数到事件定位

TriAD 有明确二阶段定位：candidate window 再交给变长 discord detector；PCRTA 与 Sub-Adjacent 输出逐窗口 / 逐时刻分数，需外部 threshold protocol 形成区间。TriAD 的候选定位依赖 single-event 先验，PCRTA 的 score endpoint 对齐和 Sub-Adjacent 的窗口 / 动态高斯都可能影响边界与延迟。算法单点 F1 并不充分表达告警是否及时、是否重复或涵盖太长窗口。

### Normal dynamics / 运维上下文

TriAD 按 periodicity 定窗口并剥离 periodic trend；PCRTA 用前 $k=10$ 均值生成 contextual perturbation；Sub-Adjacent 用固定距离 band 重建。这些机制都涉及局部规律或周期性，但三篇没有输入 workload、release、Trace 或已知 business-state labels。因而“对时序结构建模”不等于“识别多种业务正常状态”。

## 4. 研究问题当前状态（18 篇 scope）

### 多种正常运行状态如何建模？

已有静态服务频谱、跨窗 prototype、latent memory、test-time adaptation、多视图一致性、周期 residual、perturbation pseudo-labels 和 sub-adjacent temporal context 等不同 normal references。它们的表示单位分别为 service、window、latent history、test stream、view、periodic component 或 temporal band。

**状态：Partially Answered。** 这些算法展示了不止单一点残差的正常参照，但未证实以运行语义命名同一服务的合法状态，并在状态迁移时保持故障敏感度。

### 正常业务波动与真实故障如何区分？

已读 18 篇涵盖形状 / 扰动、周期 / 频域、窗口相似度、变量关系、时间 attention band、在线适应和关系变化等 evidence。尚无论文组合运行上下文与多事件故障控制实验，专门覆盖 “only state change / only fault / state+fault concurrent / unseen legitimate state”。

**状态：Partially Answered。** 有异常 score 的多种统计来源，但少有来源层面判别证据；不能从 score deviation 直接推断故障原因。

### 是否仅抑制噪声，是否解释波动来源？

TriAD / PCRTA 通过扰动或 representation density 增强 discriminability；Sub-Adjacent 用 attention contribution 降低近邻复制。关系型方法已提供结构证据，但本批结果未映射到外部 service topology 或 Trace root cause。

**状态：Partially Answered。** 许多机制不只是平滑噪声，但还没有形成从负载 / 发布变化到指标响应再到根因核验的完整证据链。

### Metric、Trace、workload 与运行 context 是否被使用？

这批只用数值序列 / 其频域与合成扰动；UCR 的多领域标签和 SWaT / server 数据来源没有进入模型条件变量。

**状态：Open within the 18-paper scope。** 后续 LLM / VLM / foundation-model 论文需仔细区分“将时序图像化”与真正引入运行 context。

## 5. 结果外推的限制与下一步证据

1. **阈值可部署性**：PCRTA、Sub-Adjacent 的 best-F1 test threshold；TriAD 的 vote / PA%K / affiliation 各自需对照 validation-only 和固定告警预算。
2. **事件数量**：TriAD 明确每条测试序列一个事件；需多事件、持续故障、状态切换和短故障测试。
3. **扰动匹配度**：point / context / collective synthetic perturbations 的幅度对某领域是否真实，应与实际故障样本和合法高波动 normal 做对照。
4. **上下文语义**：引入业务负载 / release / Trace 时需对照消融并防止 label leakage，报告条件 false alerts 和 event delay。
5. **模型成本**：TriAD 的 MERLIN candidate pipeline 有独立效率实验；PCRTA 的 7 view LOF 与 Sub-Adjacent 的 linear attention / score window 应在同硬件与同窗口下报告端到端延迟。
6. **公平比较**：不同论文的 datasets、per-entity vs pooled training、test-best threshold、PA、window stride 不统一，应采用 TSB-AD 或统一 evaluator 做 protocol-aligned re-run，且同时保留各文原生结果。

以上是 18 篇当前证据范围的限制描述，不代表全领域都没有后续工作。

## 6. 下批阅读计划

第 19–21 篇聚焦 LLM / 语言先验进入 TSAD 的三种路径：

1. **Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection**（IJCAI 2024）：核对 LLM 提供何种 teacher knowledge、如何蒸馏及其实际输入是否含业务语义。
2. **Delving into Large Language Models for Effective Time-Series Anomaly Detection**（NeurIPS 2025）：逐模块核对语言模型怎样转成时序异常特征、对照及消融。
3. **AnomSeer: Reinforcing Multimodal LLMs to Reason for Time-Series Anomaly Detection**（ICML 2026）：重点查实际多模态输入、reinforcement signal 与 reasoning evidence，而不从题名推断能力。

下批后再将 vision-language / zero-shot foundation model 与 LLM 方法合并比较。
