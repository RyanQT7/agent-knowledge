# LLM 驱动的微服务异常生成与 Metric–Trace 联合建模

## 摘要

本报告基于知识库中已完成精读的 33 篇 TSAD 论文和 6 篇 LLM / 微服务专题论文，对“用 LLM 生成符合微服务故障机制的场景，并构造 Metric–Trace 一致异常训练样本，以区分正常业务波动和真实故障”这一方向进行研究现状、创新重合、技术路线、实验设计和数据可行性分析。AMulSys 的出版方全文仍不可获取，本报告只使用摘要级信息。RedLamp 是指定的重点比较对象，但不属于 39 篇精读档案；其公开 KDD ’25 版本已做方法章节定点核验。

核心判断是：相关研究分别具备 LLM 数值窗口生成、LLM 调用图生成、TSAD 伪异常增强、真实测试床故障注入、动态正常态建模、多模态检测 / 诊断等能力；当前知识库内未发现一项工作同时实现故障计划条件化、Metric–Trace 样本级一致、独立真实故障检测收益和健康负载波动对照。该结论仅覆盖已检查的资料集合，不能当作全面文献首创证明。

建议先用真实故障注入环境 C 建立真实性锚点，以规则异常注入 A 作为强基线，并严格比较 LLM planner 与同知识 / 同预算的无 LLM 模板。只有确认拥有足够的对齐事件、故障 / 健康真值及跨事件 holdout 后，再考虑条件生成模型 B。潜在的三项研究切入点是：负载变化 × 服务退化的 matched 事件与多轴标签；可执行计划到遥测的故障 provenance；Metric–Trace 一致性定义与真实 holdout 下的增益验证。

## 1. 研究任务的准确表述

### 1.1 研究目标

给定服务拓扑、Metric / Trace schema、运行版本、业务负载及允许执行的故障动作，构造一组可以追溯到机制的运行样本。样本至少包含：

- **健康稳定状态**：无业务状态切换、无服务退化；
- **健康业务波动**：负载 / 请求 mix 显著变化，但端到端交易与服务健康检查保持通过；
- **故障状态**：故障动作或事故真实发生，且由服务健康 / SLO / 交易 oracle 观察到性能退化；
- **并发状态**：业务负载变化与故障同时存在，并记录两者独立标签。

目标 detector 应在未参与数据生成 / 规则构造的真实或独立 fault-injection 事件中，提高故障召回或降低检测延迟，同时限制健康业务波动下的误报。

### 1.2 三类标签必须分开

1. **Demand shift**：业务流量、请求种类或时段改变。
2. **Fault action / incident**：系统中是否执行故障动作或出现已核验根因。
3. **Observed service degradation**：实际用户路径、可用性、错误率或 SLO 是否退化。

无注入动作不代表健康：负载升高本身可能导致自然过载。注入动作成功也不等于业务发生退化：重试、缓存或隔离策略可能隐藏其影响。把这些标签折叠成单个 normal / anomaly 会产生错误监督。

## 2. 文献全景与能力边界

| 论文 | 实际任务 / 输出 | LLM 用途 | 故障知识 / runtime | 多模态与一致性 | 正常波动证据 | 主要实验能证明什么 |
| --- | --- | --- | --- | --- | --- | --- |
| TraceLLM (EMNLP 2025) | 条件化调用 Trace DAG 生成 | Llama-2 7B + LoRA 分层图生成 | 无故障根因动作 | 仅 Trace 结构 | 无业务健康状态 | 验证 DAG 条件、分布和下游图任务；不证明故障异常生成 |
| LLM-AP (Applied Sciences 2026) | 单变量数值异常窗口 | 冻结 GPT-3.5 / GPT-4o 直接改写序列 | 无微服务机理 | 单变量 | 局部窗口，不含业务 context | NAB 上部分 detector 有增益、Autoformer 下降；统计 / 形态过滤不代表根因真实性 |
| Synthetic Time Series (MLDS 2024) | 云微服务运行指标 / 日志数据构造 | 不用 LLM | AWS EKS、Locust 动态 workload、AWS FIS 故障注入 | 多种运行信号同源，但该版没有 Trace joint generator | trend、多周期、噪声正常负载与独立 load anomaly | 证明可构造可控运行数据与注入标签；没有 detector 收益实验 |
| GenIAS (arXiv 2026 v2) | 单 / 多变量伪异常 | 不用 LLM；TCN-VAE 潜扰动、变量级 patch | 无服务机理 | 数值单模态 | 数值正常分布，无业务标签 | 9 个 TSAD benchmark 的质量和 detector evidence；不证明服务故障真实性 |
| RedLamp (KDD 2025) | 11 类时序伪异常与多类 detector | 不用 LLM；多种增强、软标签、masked reconstruction | 无服务机理 | 数值单模态 | 关注 contamination / false pseudo-anomaly | benchmark 和污染鲁棒性；类别是波形增强类别而非故障本体 |
| CAPMix (ASE 2026) | KPI 伪异常与检测训练 | 不用 LLM；CutAddPaste、DTW 软标签、Mixup | 无显式故障计划 | KPI | noisy / dynamic KPI 与生产案例 | 多个数据集、污染和 Kuaishou 部署结果；不提供 workload 来源解释或 Trace 对齐 |
| CAROTS (2025) | 因果关系保持 / 破坏的 MTS 对比样本 | 不用 LLM | 变量关系先验，不是服务故障动作 | 数值关系，不含 Trace | 值变化但结构关系可保持 | 支持相应因果增强检测路线；预测关系不等于真实微服务拓扑 / 干预因果 |
| MODIFy (JSS 2026) | 多模态异常检测与服务级根因排序 | 不用 LLM；Trace diffusion 做去噪表征 | 已标注微服务故障 | Log / Metric / Trace 对齐融合，不生成这些模态 | 未系统建模业务负载 | 两系统检测 / 定位、消融和噪声鲁棒性；不能证明异常样本生成 |
| AIOpsLab (MLSys 2025) | 自主云 Agent 评测 | LLM 是被测 Agent | live workloads、故障注入、内部 oracle | 真实运行时采集多模态观测 | 两个 no-op 任务暴露部分 Agent 误报 | 评估 48 个代表性 Agent 问题；不是异常数据生成 / detector benchmark |
| AMulSys (Information Fusion 2025) | 摘要描述的三模态异常检测与增强 | 摘要未报告 LLM | 仅可见摘要说明 | 摘要称三模态图 + 类别先验 Mixup | 未核实 | 出版方摘要报告两系统 F1 > 0.97；全文、切分、消融和一致性细节未核验 |
| MACE / WMMNN / TimeRCD | 多正常模式、测试时适应、序列相对 context | 无 | 数值统计 / context，不是运维语义根因 | 主要 TSAD 序列输入 | 显示多正常建模已存在 | 不能把“建模多种 normal”宽泛宣称为空白 |

### 2.1 数值、图、运行系统是三个不同层次

- LLM-AP 输出数值窗口；GenIAS、CAPMix 和 RedLamp 输出或构造数值伪异常。
- TraceLLM 输出调用图 / Trace 结构，条件中的高延迟不等于根因故障计划。
- Synthetic Time Series 和 AIOpsLab 触发真实运行环境中的动作并测量遥测；测量同源不等于联合生成。
- MODIFy 消费已有三模态观测，执行检测与服务定位；它的 diffusion 模块是 Trace 特征去噪机制，不是异常样本生成器。

### 2.2 当前未被验证的组合

在本知识库的 39 篇已精读论文中，没有找到一项方法同时：

1. 以微服务故障计划为条件；
2. 联合生成或运行采集同一事件下的 Metric 和 Trace；
3. 验证 service / instance、拓扑边、span 时间、Metric 窗口与故障时间相容；
4. 在独立真实故障 holdout 上证明训练收益，并报告健康负载波动误报。

这是有限语料里的证据边界，不是覆盖所有研究领域后的首创证明。AMulSys 摘要称其有三模态图和多模态样本增强，但没有足够全文证据将其认定为 joint fault generator。

### 2.3 代表性方法机制

**TraceLLM：生成的是调用图。** 作者把调用边和字段序列化为文本，采用 Llama-2 7B + LoRA 进行领域适配；生成时从当前父节点 / 层条件生成边文本，再递归生成下一层。概率分解为 P(t | c) = ∏ₖ P(c⁽ᵏ⁺¹⁾, tᵏ | cᵏ)。图级指令包括深度、边数、延迟或通信条件，指令微调教模型推算剩余约束。方法检查 DAG 和条件遵循，但没有给每个调用图附加真实根因事件。（PDF §§3.1–3.3, Eq. 1, Fig. 2）

**LLM-AP：LLM 直接改写单变量数值。** 作者从标注序列归纳 local spike、level shift、variance change、trend change、gradual drift、slow degradation 六类，提示中提供最多 2 个正常和 2 个异常上下文窗口。冻结 GPT-3.5 / GPT-4o 输出 JSON 序列后经过五级验证：解析 / 长度；RelDTW 下限；异常存在性规则（z-score 或 CUSUM）；目标子类型形态检查；RelDTW 上限。失败信息通过 Self-Refine 最多反馈重试 3 次。过滤器是局部形态 / 距离门控，不是独立故障语义 oracle。（PDF §§3.1–3.3, Eqs. 1–12, Table 2）

**GenIAS：从正常潜空间扰动出候选异常。** TCN-VAE 学习正常窗口的紧致表示，z = μ + σ ⊙ ε；对逐维标准差使用可学习扰动 ψ，形成 z̃ = μ + ψ ⊙ (σ ⊙ ε)。训练目标结合重构、triplet 风格的最小 / 最大偏离约束、零扰动维度惩罚和紧致 KL 先验。解码后按每个变量的 L2 偏离与该变量动态范围比较；超过 τ × range 才替换该维输入，否则保留原轨迹。其扰动依据潜空间几何而非微服务故障知识。（PDF §3, Eqs. 1–6, Algorithms 1–2）

**CAPMix 与 RedLamp：伪异常标签也可能错。** CAPMix 先用 CutAddPaste 造 KPI 形态候选，再以 DTW 关系降低与正常窗口相似的候选伪标签可信度，并在输入空间 / TCN 潜空间 mixup。RedLamp 用 11 种时序伪异常增强（外加原始 normal 类），由 CNN encoder-decoder 重构 anomaly-free 区域，同时用多类标签分类；backward correction 软化有污染或误标样本，并在评分中处理经常被预测为正常的 pseudo-normal 类。两者均在数值空间提高伪异常训练鲁棒性，没有跨服务因果路径。（CAPMix PDF §§3.3–3.4, Eq. 8；RedLamp §§3.2–3.6）

**Synthetic Time Series 与 AIOpsLab：由运行系统响应产生数据。** Synthetic Time Series 用 Locust 驱动含趋势、多周期和噪声的正常流量；对选定区间乘负载因子形成负载异常，另由 AWS FIS 注入 CPU / 内存 / 网络 / I/O / Pod 等故障，并采集 EKS 的 node、Pod、service metrics（共 470 项）和日志。AIOpsLab 的测试床提供可控 workload / faults、遥测 API 与内部任务 oracle，正式版在 100 个框架问题中评估 48 个代表问题。前者偏数据集构造、后者偏 Agent 任务评测，均不是 Metric–Trace 联合生成器。（Synthetic Time Series §§3.2–3.5, Eqs. 1–2, Algorithms 1–2；AIOpsLab §§2–3）

**MODIFy 与 AMulSys：观测融合不等于联合生成。** MODIFy 用 Hawkes 强度编码 Log、Transformer 编码 Metric、扩散式去噪后再 Transformer 编码 Trace；把三类表示按 6 秒窗对齐，经多尺度融合和服务调用 GAT 输出异常检测与 service-level root ranking。Trace diffusion 的输入是受噪声扰动的表示，目标是恢复 / 鲁棒编码特征，不是采样故障 Trace。AMulSys 摘要只支持“使用三模态图表示与类别先验多模态 Mixup”的概述，缺少全文无法审查其样本级时间对应关系。（MODIFy PDF §§4–6, Eqs. 1–17, Figs. 2–4；AMulSys 出版方摘要）

### 2.4 关键实验结果与正确解读

- TraceLLM 在 5K 合成图训练、2K 真实图测试的特定图任务中，FIRM SVM 准确率距真实图训练约 1.5 个百分点；不是异常检测收益。（§4.3, Fig. 6）
- LLM-AP 的 TimesNet 最佳配置 F1 为 0.7238±0.001，对照 0.6893±0.002；Autoformer 某一增强设置为 0.2753，对照 0.6071，说明收益依 backbone 变化。（Table 8）
- GenIAS + CARLA 的平均 F1 为 .557，CARLA 为 .509；其 ARP / EDI 与检测结果来自一般 TSAD benchmark，不含微服务因果标签。（Tables 1–2）
- CAPMix 报告平均 Best RPA-F1 60.69%，ASD 上低于 RedLamp 的 69.59±1.33；RPA-F1 协议与其他文章的 F1 / VUS-PR 不宜直接比较。（Tables 2–3）
- RedLamp 作者报告 benchmark 平均 VUS-PR 相对基线 +17%；UCR 的 5% contamination 下 VUS-PR 下降 1.8%，CutAddPaste 下降 15.5%。这是其增强 / contamination 设定，不证明微服务 fault realism。（§§4.2, 4.5）
- MODIFy 两 benchmark 平均 F1 .883、HR@1 .847，支持在已标注数据上做多模态检测 / service ranking；不说明生成异常能否迁移。（Tables 4–5）
- AIOpsLab 两个 no-op 任务展示部分 Agent 将正常 workload 误判为异常，但样本数有限，不能据此得出一般性误报率。（§3.6.4）
- AMulSys 摘要报告两真实微服务系统 F1 > .97；因全文不可得，无法核验其数据划分、类别不平衡、增广独立作用或是否测试了跨模态样本一致性。[出版方页面](https://www.sciencedirect.com/science/article/pii/S1566253525000909)

这些结果测量的目标不同：生成结构、统计特征、benchmark detector utility、live action effect 和多模态分类分别回答不同问题。不能用一个指标代替所有真实性结论，也不能把这些异构数值拼成 leaderboard。

## 3. 三个科学问题

### RQ1：如何生成由真实微服务机制支持的异常场景？

不建议让 LLM 自由生成 Metric 数值作为主路径。LLM 可能产出平滑且符合统计形态的序列，但数值没有服务动作、传播范围和用户影响来源。更可审计的生成链是：

1. **场景理解**：输入服务拓扑、允许故障清单、业务请求种类与历史事件文本。若 schema 或根因未知，保留 unknown。
2. **结构化计划**：预测目标服务 / 实例、故障类型、动作参数范围、开始 / 持续时间、workload 条件、可能影响的依赖路径。
3. **约束编译**：从拓扑筛掉不可达节点；从动作 allowlist 限定执行范围；校验资源预算 / 环境版本。
4. **动作执行或遥测生成**：由 rule engine、条件生成器或真实 fault-injection 平台生成实际 Metric / Trace 行为。
5. **效果核验**：分别记录 action executed、服务退化、拓扑传播和用户交易影响。

LLM 的候选作用是语义转结构、组合 scenario 与提高覆盖；不是根因真实的证明者。与模板 baseline 相比，应测量 valid compile rate、执行成功率、计划覆盖、重复率、真实检测收益。若 LLM 没有增益，应将其从方法中删除。

### RQ2：怎样保证 Metric–Trace 跨模态一致？

#### 结构和时间硬约束

- service / instance ID 可映射到同一拓扑版本；
- traceId、spanId 唯一，parent span 存在；
- 调用 edge 属于版本化允许拓扑，或被记录为动态发现的新边；
- span 开始 / 结束、父子时间容差、故障动作窗口可检查；
- Metric 事件时间按采样规则聚合到 Trace 所在时间段；
- 实例级 Metric 和 span service / instance 使用可审计映射。

这里应允许跨主机 clock skew，不应简单要求 parent span 严格包住所有 child span。复杂异步任务、消息队列和 trace sampling 会造成边界情况。

#### 需校准的统计约束

延迟、错误率、重试、吞吐量、CPU / queue / memory 等之间的关系是有条件的；具体影响依应用、请求类型、负载、熔断、缓存和采样策略变化。使用分层条件统计、置信范围或概率分数，比统一硬编码“某故障一定提高某指标”更合理。

一种候选损失写法是：

    L_consistency = λ_top L_topology + λ_time L_temporal
                    + λ_id L_identity + λ_stat L_conditional-statistics

前三项用于结构 / 时间 / 身份违反；统计项需要从真实受控数据校准。它是待验证的设计假设，尚无当前论文验证其足以恢复故障因果。

Trace 信息可能在低流量、重采样、局部资源故障不经过请求路径、Trace 丢失或 Metrics 已足够明显时没有额外价值。应测模态增量，并按采样率和故障类型分层，不默认“多模态总是更好”。

### RQ3：正常业务波动与真实故障如何区分？

用二维或多轴标签取代简单的 normal / anomaly：

| 需求变化 | 服务是否退化 | 解释 |
| --- | --- | --- |
| 无 | 否 | 平稳健康对照 |
| 有 | 否 | 健康业务波动 / 合法状态变化 |
| 无或有 | 是 | 服务性能退化；另记录根因是否为注入 / 业务负载 / 未知 |
| 有 | 是 | 负载变化与故障 / 过载共现，单独评估 |

“业务波动正常”指需求侧变化且业务服务仍然健康，不表示 KPI 必须稳定。高负载若导致 SLO 违规，就是服务退化事件，即使没有基础设施 fault injection。此定义能避免把业务原因和运维影响混淆。

健康样本由交易探针、成功率、可用性和业务 SLO 确认；故障样本由注入器日志 + 实测服务影响确认。只按“没有故障标签”不能保证健康，只按“注入了故障”也不能确认观测到故障。

## 4. 三种候选技术方案

### 方案 A：LLM 规划 + 规则异常注入

**模块**：输入架构 / fault ontology / workload；LLM 输出结构化 plan；规则 validator 做拓扑和动作白名单检查；Metric 注入器以健康窗口为背景改变受影响 KPI；Trace 注入器改写目标服务 span duration / status / retry 等；一致性校验器检查身份、时间和条件统计。

**训练数据**：健康 Metric–Trace 背景、故障规则、服务拓扑、采样与时间信息。LLM 可用提示，不需微调。

**优点**：成本最低、可解释、易构造反事实和 matched pairs。**风险**：显式人为模式可能泄漏给 detector；跨系统硬规则错误；LLM 计划不一定能执行。

**创新空间**：单独合成数字或规则增强创新较弱。可测贡献是可审计 plan provenance、同负载下健康 / 故障对照、独立实测故障验证、LLM 与非 LLM planner 的公平对比。

### 方案 B：LLM 计划 + 条件生成模型

**模块**：plan encoder 编码负载、拓扑、根因、严重度和持续时间；Metric generator 生成 KPI 残差 / 窗口；Trace generator 生成请求 DAG / span / latency / error；共享条件或 latent 表示跨模态；结构 / 时间 / 统计约束给出样本级质量分数。

**训练数据**：对齐的真实 Metric–Trace 正常 / 故障事件、service / instance ID、拓扑、workload 和 fault/action 标签，并记录 Trace sampling / missingness。大规模异常样本不足是主要瓶颈。

**优点**：理论上可学到真实背景噪声和条件分布。**风险**：生成器可分别逼真但联合矛盾；数据稀疏会让 plan condition 无法校准；generator artifact 会让 detector 在合成验证集上虚高。

**创新空间**：当前语料未发现完成 joint fault-plan-conditioned Metric–Trace generation 的工作，但需进一步检索并以 C 的真实事件为外部真实性锚点。

### 方案 C：LLM 计划 + 真实故障注入测试床

**模块**：LLM / 模板 plan → 安全 allowlist compiler → 控制 workload 与版本 → 执行 CPU / network / timeout / error 故障 → 采集真实 Metrics / Traces → 记录 action log 与 health oracle → 事件化样本 → detector train / independent test。

**数据要求**：可复现应用、隔离集群、故障执行器、时间同步、遥测采集、请求级 health check 和多次重复运行。

**优点**：样本来自共同运行过程，机制和时间真值最强；不需要先训练遥测生成器。**风险**：testbed 与生产分布差异；故障动作未必导致服务退化；集群复位与运行成本高。

**创新空间**：不能宣称“首次 fault injection”。候选贡献应是计划可编译 / LLM 对照、matched healthy / fault / concurrent episodes、双重 action / health oracle、Metric–Trace 一致性指标和独立 detector holdout。

### 方案比较

| 维度 | A：规则注入 | B：条件生成 | C：真实注入 |
| --- | --- | --- | --- |
| 样本机制 | 手工扰动 / 同步变换 | 学习分布条件映射 | 实际系统动作 |
| 跨模态保证 | 依赖规则同步 | 依赖 joint conditioning / loss | 同一运行源，但仍要检查对齐 |
| 数据要求 | 中 | 最高 | 测试床成本高、但可逐步采集 |
| GPU / 训练成本 | 低 | 高 | 不一定需要 GPU |
| 真实性强度 | 低到中 | 需要外部验证 | 高但受 testbed 限制 |
| 首要风险 | 人工伪影 | 统计似真、因果不真 | 环境代表性与动作 / 影响分离 |

## 5. 最小可行实验设计

### 5.1 场景

1. 稳定健康 baseline。
2. 请求量 / 业务 mix 上涨但健康 oracle 通过。
3. 同样 workload 下游调用延迟。
4. CPU / memory / I/O 资源竞争。
5. 同样 workload 下游 timeout / error propagation。
6. 可选但重要：负载上涨与故障并发，独立记录两个因素。

对 2、3、5 建 paired runs：控制服务版本、拓扑、请求曲线和 request mix，随机化故障注入时间并重复运行。真实系统自然噪声无法完全匹配时，记录差异并分层分析。

### 5.2 Baseline

- 原始训练集、无增强；
- 规则 / 模板场景规划与相同规则执行器；
- LLM planner + 相同规则执行器（只改变 planner）；
- CAPMix、GenIAS、RedLamp；
- 可选 LLM-AP 单指标生成；
- Metric-only、Trace-only、无约束融合、带结构 / 时间 / 统计一致性检查的融合；
- 条件生成方案 B 仅在真实对齐事件足够后加入。

尽可能固定 detector 容量、训练步骤、生成样本预算和阈值协议。MODIFy 可作多模态 detector 参考，但它不是 anomaly generator。

### 5.3 真实性检查和下游评估

真实性层次：结构合法、条件统计接近、动作真实执行、服务健康 / 退化得到 oracle 确认、生成训练数据对真实 holdout 有用。分布相似、classifier 的 real-vs-synthetic 分数、detector gain 都不能单独证明机制真实。

按 incident / service / fault type / workload / version 分组切分；测试集只使用未参与规则 / generator 构造的实测故障事件。至少报告：

- 事件级 precision / recall / F1、PR-AUC；
- N1 健康负载下 FPR / 每运行误报数；
- matched fault pair 召回和检测延迟；
- 跨 workload / service / fault family 的分组表现；
- 固定 FPR 下 Metric+Trace 相对 Metric-only 的增益；
- Trace sampling / missingness 下性能变化；
- 可选根因定位的 top-k accuracy / MRR。

阈值仅由独立验证集确定。点级 F1 或 point-adjusted F1 可补充报告，但不能替代事件级误报和延迟。

### 5.4 消融

- LLM planner vs 同知识、同预算的无 LLM 模板；
- 去掉故障本体 / 拓扑限制；
- Metric-only / Trace-only / 联合输入；
- 无一致性、结构约束、结构 + 时间、再加条件统计约束；
- 去掉健康负载困难对照；
- 规则合成训练 vs 实测故障训练 / 混合训练；
- 仅按注入动作打标签 vs 加入实测退化 oracle；
- 按 Trace sampling 与缺失率分层。

## 6. 评价指标与失败判据

### 生成计划质量

schema 合法率、拓扑可达率、编译成功率、动作执行成功率、场景覆盖 / 重复率、无效计划比例。计划质量不能只靠 LLM 自评。

### 跨模态一致性

身份映射失败、非法调用边、父子 span / 时间违规、故障窗口不匹配；按业务 / 服务 / fault type 校准延迟、error、retry、throughput、resource 等条件统计关系；同时报告采样 / 缺失分层。

### 下游效用

同一检测器在相同真实测试 incidents 下，评估事件级 recall、FPR、PR-AUC、检测延迟、跨负载稳定性。生成器自己的测试样本不得作为真实性与泛化评估唯一证据。

### 失败判据

- LLM 只提高描述多样性，不提高计划可执行率、覆盖或 detector transfer：不支持 LLM 独特价值。
- 一致性 validator 得分提高，但真实事件检测不提升：只证明样本结构符合设计规则。
- synthetic test 提升、real holdout 不提升：结论是未泛化或有人工痕迹。
- 健康 workload FPR 上升：不能只报告总 F1 增益。
- 注入成功但 health oracle 无影响：记录为“动作已执行、未见退化”，不强制标异常。

## 7. 数据可行性状态

已检查 agent-knowledge 中可找到的 Markdown 数据字典 / schema 文档；没有找到可核验的国网项目 Metric / Trace 字段文档。本次没有打开、修改或外传国网原始数据。下列字段均是**尚未确认**，不能据此断定原始数据缺失：

- KPI 类型、单位、时间戳、采样频率；
- service / instance ID 与版本化拓扑；
- Trace span ID、父子关系、时间、duration、status / error；
- Metric 与 Trace 的 join key、时钟偏移和采样 / 丢失；
- 故障、incident、根因标签；
- workload / 请求量 / 请求 mix；
- 交易健康结果、SLO 或业务成功率。

如这些信息没有历史标签，可在授权的隔离测试床补采。若只有 Metric，则不能声称完成 Metric–Trace 联合建模；若无 workload 与健康 oracle，则不能证明已区分“业务波动”和“故障”。

## 8. 创新性结论与推荐路径

### 已经不能单独声称的内容

- 首次使用 LLM 生成时序异常（LLM-AP 已做）；
- 首次生成微服务 Trace（TraceLLM 已做）；
- 首次进行时序伪异常增强（CAPMix / GenIAS / RedLamp / CAROTS 等已做）；
- 首次在微服务平台执行故障注入（Synthetic Time Series / AIOpsLab 已做）；
- 首次多模态异常检测 / 融合（MODIFy、AMulSys 摘要等已做）；
- 首次建模多正常状态 / 动态正常（MACE、WMMNN、TimeRCD 等已有相邻方法）。

### 三项候选研究切入点

1. **健康业务波动与服务退化的 matched episodes**：明确需求、注入和健康三轴标签；用实测交易 / SLO oracle 证明健康负样本；加入并发状态。这更可能首先形成数据 / 评测贡献。
2. **可执行故障计划到遥测的 provenance**：比较 LLM planner 与无 LLM 规则模板；由真实动作执行器和服务健康 oracle 判断计划语义是否落地。LLM 若无边际价值应移除。
3. **Metric–Trace 一致性约束和效用验证**：严格区分结构 / 时间硬约束与条件统计软约束；测试一致性约束对独立实测故障检测的增益，以及 Trace 在何种采样 / 流量下提供额外信息。

### 推荐

采用 **C 作为真实性锚点 + A 作为生成 / 规划对照**，先采集小规模 matched 健康与故障事件；此阶段不训练 B。检查数据对齐、健康标签、Trace 增量和 LLM 边际效果后，再决定是否投入条件联合生成模型。最大风险不是 GPU 成本，而是缺少对齐 schema、服务健康 oracle 和独立故障 holdout，导致无法区分生成器学到了机理还是数据伪影。

## 9. 证据和延伸阅读

知识库专题 Review：[AIOps Knowledge Review v4](reviews/aiops-knowledge-review-v4.md)；TSAD 证据地图：[TSAD research problem map](../../exports/tsad-knowledge/tsad-research-problem-map.md)；33 篇 TSAD 综合：[TSAD final synthesis](../reviews/tsad-final-synthesis.md)。

关键单篇精读：[TraceLLM](../../papers/aiops/tracellm/notes.md)、[LLM-AP](../../papers/aiops/llm-ap-synthetic-augmentation/notes.md)、[Synthetic Time Series](../../papers/aiops/synthetic-cloud-microservices/notes.md)、[GenIAS](../../papers/aiops/genias/notes.md)、[AIOpsLab](../../papers/aiops/aiopslab/notes.md)、[MODIFy](../../papers/aiops/modify/notes.md)、[CAPMix](../../papers/capmix/notes.md)、[CAROTS](../../papers/carots/notes.md)、[MACE](../../papers/mace/notes.md)、[When Model Meets New Normals](../../papers/when-model-meets-new-normals/notes.md)、[TimeRCD](../../papers/time-rcd/notes.md)。

外部原文入口：RedLamp [KDD ’25 公开版本](https://arxiv.org/html/2505.20765)；AMulSys [出版方摘要页](https://www.sciencedirect.com/science/article/pii/S1566253525000909)，其获取限制见 [知识库记录](../../papers/aiops/amulsys/availability.md)。

## 10. 配套研究文件

- [研究现状与重合分析](llm-microservice-anomaly-generation-survey.md)
- [候选技术方案](llm-metric-trace-generation-design.md)
- [最小实验计划](llm-metric-trace-experiment-plan.md)
- [创新性边界](llm-microservice-research-novelty.md)
