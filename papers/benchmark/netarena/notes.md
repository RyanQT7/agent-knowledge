# NetArena: Dynamic Benchmarks for AI Agents in Network Automation

## 1. 论文身份与材料

- **作者：** Yajie Zhou, Jiajun Ruan, Eric S. Wang, Sadjad Fouladi, Francis Y. Yan, Kevin Hsieh, Zaoxing Liu。
- **发表：** ICLR 2026，正式会议版。
- **论文：** [出版社/作者托管 PDF](https://fyy.cs.illinois.edu/files/netarena-iclr26.pdf) · [OpenReview](https://openreview.net/forum?id=BPVPOtzoOz)。
- **本地材料：** [PDF](../../../sources/papers/benchmark/NetArena_ICLR2026.pdf)；[全文文本](../../../sources/papers/benchmark/NetArena_ICLR2026.txt)。全文文本由出版社 PDF 的文本解析结果生成，覆盖解析器给出的 906 个文本行；本机没有 `pdftotext` 或 PDF Python 库，未为此安装依赖。图表依据 PDF 解析描述和正文定位阅读，个别图中数值需谨慎。
- **官方代码：** [Froot-NetSys/NetArena](https://github.com/Froot-NetSys/NetArena)，只读静态分析，未运行、安装依赖或部署仿真环境。为贴近论文中的直接本地运行路径，按仓库 README 选择 `main` 分支；固定 commit `aefbd457497768a9504cfc1c6b0988a626cf082a`，本地忽略目录 `sources/code/NetArena/`。仓库当前默认分支 `a2a-agentx` 是 Docker/A2A 集成路径，不与本文分析的 `main` 混同。

## 2. 一句话概括

NetArena 把网络自动化任务表示为可执行的状态转换系统，由任务生成器随机生成查询和真值，再让 Agent 在 Mininet、Kubernetes 或图模拟器中多轮行动，以最终状态正确性、逐步安全性和任务耗时评价 Agent。

## 3. 问题、动机与贡献

论文认为，网络和系统 Agent 的评估不能只看静态问答：网络状态会随动作变化，调查过程有部分可观测性，配置动作可能破坏原有服务。人工构造的静态查询和答案制作成本高、覆盖有限，也更容易被模型预训练记住；只检查最终答案还看不到危险中间动作、冗余步骤或环境交互错误。（§1、§2）

NetArena 的贡献是提供跨任务的状态—动作接口、在可执行模拟器/仿真器中生成查询和真值、以及把 Correctness、Safety、Latency 放入一个可反复采样的评估流程。它不是新的 RCA 算法，也不是一个固定的独立数据集；它的核心产物是“任务定义 + 环境 + 随机生成器 + 评价器”。（§3、Appendix A）

论文用“少于 300 条”概括近期网络/系统 Benchmark 的数据稀缺，但自己的 Table 1 同时列出静态 NetConfEval 3,200 条。因此更稳妥的理解是：作者指出若干人工策划的 Agent 任务规模较小、静态且覆盖受限，而非断言所有相关 Benchmark 都少于 300 条。（§1、Table 1）

## 4. 统一任务模型与查询生成

论文把任务表示为有限状态转换系统 `(S, A, E)`：`S` 是系统状态，`A` 是带参数的原子动作集合，`E(s, a(θ))` 是应用特定的执行函数。一个 episode 从 `s₀` 开始，连续应用 `a₀(θ₀)…aₜ₋₁(θₜ₋₁)`，产生 `sₜ₊₁ = E(sₜ, aₜ(θₜ))`。（§3.2，Eq. 1）

添加新应用时，开发者需定义状态与动作、连接任务环境的 backend emulator/simulator，并为该应用实现三项指标；Appendix A 将工作展开为选模拟器、建拓扑、选 constructive/reactive 任务、定义操作或故障、定评价。（Appendix A，Table 3）

两类任务的真值含义不同：

- **Constructive：** 从已知初态出发，先采样动作序列 `A*`，由执行器生成目标态 `sT = E(s₀, A*)`。自然语言模板把目标转为问题；Agent 结果与目标态比较，若适用也可与动作序列比较。动作序列是可监督的参考构造，但不一定是唯一等价解。（§3.2，Eq. 2）
- **Reactive：** 从健康态 `s₀` 隐藏地注入故障动作序列，得到故障态。Agent 只收到问题和环境观察，目标是恢复到 `s₀`。评分不要求逆演相同注入动作，因为同一个故障态可能有多条有效修复路径。（§3.2，Eq. 3）

完整回路是：生成配置与查询 → 建立初态/注入故障 → 给 Agent 查询和可用工具 → 执行动作并更新状态 → 返回输出或连通性观察 → Agent 继续调查/修改 → 在每一步检查约束 → 最终比较目标状态、动作安全和耗时。Agent 内部架构并非 NetArena 统一定义；实验分别使用 CoT、Few-shot 和 GPT-4o+ReAct。（Fig. 1、§4）

## 5. 三类任务与数据构造

### 5.1 Datacenter Capacity Planning（constructive）

模拟器从 Google 多层数据中心拓扑抽象及公开拓扑数据构建有向图，共 5,493 个节点、6,424 条边和 10 种设备类型；层级约束表达 Rack、Chassis、Control Domain、Switch、Port 等包含关系，节点属性包括端口容量。（Appendix B.1，Fig. 7）

论文 §4 称有 12 种 operational types；Appendix B 和实现把基本操作列为 add、count、update、remove、list、rank 六类。现有信息更支持“六类基本操作组合成多种任务形式”，但论文没有给出 12 与 6 的逐项映射。（§4；Appendix B.2；`app-malt/dy_query_generation.py`）

复杂度通过操作数量及控制结构变化：单操作、顺序组合、If–Else、循环及其组合；参数和节点在大图中动态抽样。例：先列出所有 chassis，再为每个 chassis 加 packet switch，最后计算更新后的容量。生成器用同一组基本操作的函数模块拼接成 Ground Truth Python 函数；执行后校验图结构和容量约束，再以图同构或精确结果比较 Agent 输出。（Appendix B.2–B.4）

### 5.2 Routing Misconfiguration（reactive）

Mininet 中构造 Router–Switch–Host 多子网拓扑；子网数及每子网主机数由参数控制，论文给出的范围均为 2–4。对原先连通的状态注入故障，包含关闭 IP forwarding、禁用接口、移除/改错 IP、丢弃子网流量、错误路由表五类；每类还可由不同底层命令实现，某些案例依次注入两种错误以增加复杂度。（Appendix C.1–C.2，Table 5）

Agent 可发出 `ifconfig`、`ip addr`、`ip link`、`ip route` 等诊断/修复命令，环境返回命令结果及 `pingall` 连通状态。真实案例展示 `pingall` 76% 丢包，并返回路由表；Agent 需要结合两者定位问题。成功要求恢复连通且不破坏原有健康连边，评价不是“是否猜中被注入的错误类别”。（Appendix C.3，Fig. 8）

### 5.3 Kubernetes Microservice Policy Troubleshooting（reactive）

环境采用 Google Online Boutique 微服务示例，论文描述 11 个服务、13 条网络策略，使用本地 kind/Kubernetes 集群。生成器改写 YAML 中 ingress/egress、端口及协议；五类基本错误可顺序组合。题目会给定期望服务通信关系，故障后的观察由 connectivity checker 生成。（Appendix D.1–D.2，Fig. 9，Table 6）

每个 Pod 配置可复用的 debug container，以 `nc` 探测源 Pod 到目标服务/端口的实际连通；期望值与实际值组成 mismatch report 返回 Agent。交互约定每轮给一个命令，执行后给出命令结果和新的连通性观察，Agent据此继续修复。论文图示同时检查正向连通（例如 frontend→adservice:9555 应通）和负向约束（frontend→cartservice:7070 不应通），所以任务不只是把所有连接打开。（Appendix D.3，Fig. 10）

## 6. 评价指标与激励

**Correctness** 比较最终态 `ŝLLM` 与目标态 `s*T`：constructive 任务目标为生成的 `sT`，reactive 任务目标为原健康态 `s₀`。`Correct(Q)=I(ŝLLM ≡ s*T)`；等价关系按应用选择，可是图同构，也可以是功能连通性。（§3.3，Eq. 4）

**Safety 的论文级定义**是 episode 中每个中间状态都满足任务约束 `C_Q`：`Safe_all(Q)=I(∀t, sₜ ⊨ C_Q)`。（§3.3，Eq. 5）它与 Correctness 分别描述约束保持和目标达成；Figure 3 把两者作为二维坐标共同展示，没有定义将二者合成一个总分。需要注意，Eq. 5 是统一抽象，三种应用的开源评价代码并未实现成同一种轨迹约束，尤其 MALT 代码在返回图上检查结构不变量；详见 §8。不能仅凭论文的通用定义就推断每个应用均逐动作审计所有中间状态。

**Latency** 在通用定义中包括命令数与端到端时延，但具体任务口径不同：Capacity Planning 的附录测生成 Python 代码执行时间，并明确排除模型提示和生成时间；Routing/K8s 主要以修复迭代数表示效率。它们不能不加转换地横向排序，也未覆盖统一的 Token/费用预算。（§3.3；Appendix B.4、C.4、D.4）

Figure 3 的二维图也适合联合读分：例如 K8s:2000 中 GPT+CoT 点的 Safety 约 0.90，而 Correctness 约 0.02，呈现“多数任务不破坏检查约束，但几乎没有任务完成”的组合；该数值是从图上估读。NetArena 没有把两个轴合成总分。一般而言，最终恢复连通却在操作中破坏另一条健康链路，也可能产生 Correct=1、Safety=0；这是解释性例子，不是论文报告的轨迹。各应用 Safety 仍只是对应实现编码的代理约束，不自动等于完整业务安全或真实网络风险。

## 7. 实验设计与结果

论文比较五种 Agent：GPT-4o 与 Qwen2.5-72B 各用 CoT/Few-shot，另有 GPT-4o+ReAct。主评估小集合为 CP 100、Routing 150、K8s 150；大集合为 CP 5,000、Routing 2,250、K8s 2,000，合计 9,250 个动态查询。论文用 Bernoulli 成功率的 `SEM=√(p̂(1−p̂)/N)` 构造 `p̂ ± 1.96·SEM`。（§4.1，Fig. 3）例如以 `p̂=0.5` 作说明性计算：`N=100` 时 SEM 为 0.05，正态近似区间半宽约 0.098；`N=5,000` 时 SEM 约 0.0071，半宽约 0.0139。样本扩大可以缩小该估计误差，但依赖独立 Bernoulli 样本等假设；区间重叠变化不是配对显著性检验，也不能单独证明排名稳定或泛化。论文报告小集合中区间重叠最高约 85%，大集合降为 0%，而生成 query 的独立性未单独验证。（§4.1，Fig. 3）

大规模任务上的正确率仍低，作者在摘要报告平均表现约 13–38%、最低 3%，最佳 Agent 低于 60%。不同任务与复杂度上正确性、安全性和耗时表现不同；Table 2 分类了安全违规、控制逻辑错误和操作错误，例如加出无连接 switch、改错 IP 破坏连通、删除运行中 Pod、命令顺序错误或遗漏 namespace。Figure 4 显示复杂度上升会暴露失败，尤其 CP 的结构约束组合、K8s 的激进修复/过度保守，以及简单问题上的冗长命令。（§1、§4.1–4.2，Figs. 3–4，Table 2）

**Figure 3 的图文排名需要保留为未解矛盾。** §4.1 正文称扩大数据后“revealing GPT+ReAct as the clear winner”，并以 CP:5000 为例；但按 Figure 3(d–f) 的图例和 Correctness 纵轴直接目视读取，CP:5000 中 GPT+CoT 约 0.46、高于 GPT+ReAct 约 0.38；Routing:2250 中 GPT+Fewshot 约 0.59；K8s:2000 中 GPT+Fewshot 约 0.23，均高于对应图中的 GPT+ReAct 点。图中是可视估读而非原始数值，不能据此重算精确排名；但它并未直观支持“GPT+ReAct 在这些大样本任务中普遍明显胜出”。正文究竟指不同汇总口径、某一子任务还是误述，论文没有说明。（§4.1，Fig. 3(d–f)；原始图像核验：PDF 物理页 7）

Table 1 原始页面核验（PDF 物理页 3）确认：NetArena 行的 Scale 为 9,250（unlimited）；Correctness (95% CI) 单元格视觉上同时列出 `44%` 与下一行 `[0.01, 0.14]`；Safety/Latency 单元格列为 `35% / 18s`。因此此前的文本抽取并未错置这些值，矛盾来自论文表格本身：若 `[0.01, 0.14]` 是该列声明的 95% CI，它不覆盖 44%；论文未解释这两个数是否使用不同统计对象或口径。此处保留“表中原样如此、统计关系未说明”，不猜测或重算。（Table 1；PDF 原始页面图像核验）

§4.3 对 CP constructive 任务用 Qwen-7B 生成 SFT 训练集：Level 1 800、Level 2 600、Level 3 600、混合难度 2,000 条。单难度训练模型在本难度测试表现好、跨难度明显下降；Figure 5(a) 的混合训练 Correctness 目视标签为 Level 1 `0.99`、Level 2 `0.88`、Level 3 `0.96`。这与 §4.3 正文“maintaining over 0.96 correctness across all levels”直接不一致，尤其 Level 2。图中标签可读，故按图保留 0.88，不把正文改写成与图一致的值。训练集规模同时随训练条件变化（800/600/600/2,000），所以难度覆盖与样本量没有被等量控制；不能把混合数据结果完全归因为“多难度覆盖”而排除样本数量影响。（§4.3，Fig. 5；PDF 物理页 9）

Figure 5(b) 的 Safety 标签按测试 Level 1/2/3 依次为：Level 1 训练 `0.93/0.77/0.37`，Level 2 训练 `0.61/0.53/0.58`，Level 3 训练 `0.33/0.00/0.66`，混合训练 `0.88/0.53/0.66`；零样本基线为 `0.03/0.00/0.00`。因此 Level 1 训练并非逐级都最高：在 Level 3 测试中它为 0.37，而 Level 3 与混合训练为 0.66。正文“最简单级 across all tasks 最佳”不能从逐级图值直接推出；如指某种聚合，需要其权重和样本分布才能核对。Correctness 和 Safety 应作为互补结果并列阅读，不能因模型安全率高便称其完成任务，也不能因最终正确便推定过程安全。（§4.3，Fig. 5）

§5 还展示一个探索性 RL 用例：Qwen2.5-0.5B 在 Mininet routing 中用 GRPO，奖励无效命令 −100、有效诊断 +10、正确修复 +100；约第 36 个 episode 后累计奖励上升。作者将其定位为初步可行性，而非稳定提升或跨模型结论。对抗采样则是未来方向，不是本文已完成的评估实验。（§5.1–5.2，Fig. 6）

## 8. 官方源码静态分析

仓库 `main` commit `aefbd457497768a9504cfc1c6b0988a626cf082a` 按应用分目录，未见一个独立 `src/netarena` 通用运行时；通用抽象主要由三套应用分别实例化。

- **CP：** `app-malt/dy_query_generation.py` 以模板和 `solid_step_*` 操作生成 query 与 Ground Truth；`malt_env.py` 执行 Agent 生成的一段 Python，并在拿到返回图后调用一次 `SafetyChecker`。`error_check.py` 校验节点/边格式、层级、孤立节点、端口带宽与端口存在性。这个可见路径检查的是返回图结构，不是对 `process_graph` 内每个原子操作逐步记录状态；非图或不可恢复输出时 Safety 记为 Fail/未应用 checker。（Appendix B；该 commit 静态代码）
- **Routing：** `app-route/advanced_error_function.py` 生成错误配置与变化细节；`main.py` 组织 Mininet 交互。结果汇总的 Safety 是每条轨迹中 packet loss 不增加（`file_utils.py`）；另有 `safety_check.py` 用简单字符串 denylist 阻止若干命令（如含 `sudo`、`tcpdump`、`systemctl`、`ping`）。命令过滤和指标判定是两件事，denylist 不等于完整的操作安全策略。（Appendix C；该 commit 静态代码）
- **K8s：** `app-k8s/inject_errors.py` 改写策略并构造复合错误；`run_workflow.py` 按轮运行命令、调用 connectivity checker。结果汇总的 Safety 是 mismatch 数量沿记录轨迹不增加（`file_util.py`）；`command_validation.py` 则 fail-closed 地只允许 `kubectl get` 或 `kubectl patch networkpolicy`，配合有限管道过滤器。由于 patch 本身可改变策略，命令 allowlist 不等于只读，也不等于全套安全评价。（Appendix D；该 commit 静态代码）

以上仅证明该 commit 的静态实现包含这些路径，不证明其与论文实验环境完全一致。仓库根目录没有观察到 LICENSE 文件；不同应用依赖 Mininet、kind/Kubernetes、图模拟器及模型端点，公开代码不等于无条件开箱复现。未运行任何脚本、故障注入或仿真。

## 9. 局限与研究解释

**作者明确说明：** 模拟器成功不等于部署准备就绪。生产环境有观测噪声、缺失 instrumentation、运维漂移、异构工具和隐藏依赖；缩小 sim-to-real gap 是后续工作。（§5.3）

**进一步分析：** 随机采样降低对固定 query 的记忆风险，但题目仍由有限模板、动作库、错误类型和模拟器状态空间产生；“无限 query”是可持续生成不同实例，不等于无界覆盖生产故障语义。生成器/模板相关的 Shortcut、种子与任务参数造成的样本相关性、以及构造性任务中的执行器与评分器同源问题，值得独立审计，本文并未证明这些风险已经造成偏差。

该工作适合研究“Agent 在动态、可执行网络任务中如何行动并影响状态”，不能直接当作历史生产故障 RCA 数据集，也不能把恢复成功推成真实网络部署安全。Network emulation 提供可控因果/结构过程，但仍是结构化近似环境。

## 10. 与现有知识的关系

- 对照 [NIKA](../nika/notes.md)：两者都以网络交互环境观察多轮诊断；NIKA 聚焦故障诊断场景与任务配置，NetArena 用 constructive/reactive 状态转换统一更广的网络自动化任务，并在抽象定义上要求安全约束。
- 对照 [CTBench](../ctbench/notes.md)：CTBench 是专家维护案例和 CLI replay，NetArena 动态生成状态并实际执行；前者固定可重复的专家调查路线，后者接受多条能到达目标态的修复路径。
- 对照 [AgenticOpsEval](../agenticopseval/notes.md)：NetArena 通过可执行状态变化分别呈现最终效果和应用特定 Safety；AgenticOpsEval 的观察点/因果链强调轨迹证据覆盖。二者构念互补，最终状态成功并不证明 Agent 使用了正确因果证据，Safety 分值也不代表同一套跨应用的安全边界。
- 对照 [RCABench](../rcabench/notes.md)：RCABench 衡量有传播结构的微服务根因定位；NetArena 主要评价网络操作结果，任务目标不等同于定位真实根因。

## 11. 个人理解

NetArena 把“答案是什么”改成“在一个能执行且会改变状态的环境里，Agent 是否把任务做成、是否满足该应用编码的约束、付出多少命令和时间”。最有价值的设计是把 query 与目标状态从同一可执行生成流程派生，并把 Correctness 与 Safety 分开观察。最重要的解释边界是论文的统一 Safety 公式与三个应用当前代码的实际检查范围并不等价；模拟器结构真实性也不等于生产代表性，随机生成不能自动保证无污染、无 Shortcut 或统计独立。

## 12. 尚待回答的问题

- 生成模板与执行器是否覆盖了超出训练/公开代码的状态变体？按模板、种子、拓扑和故障族留出后性能怎样？
- Correctness 与 Safety 是否对三种应用采用可比的约束覆盖？通用 Eq. 5 与 MALT 返回态检查、Routing packet-loss 单调性、K8s mismatch 单调性的差别如何影响横向解释？Latency 的 wall-clock、命令数和轮数如何统一报告？
- CI 重叠比例下降能否在相同查询配对、重复生成种子和显著性检验下复现？查询间是否独立？
- Table 1 原始图确认 44%、`[0.01,0.14]` 同处 Correctness (95% CI) 单元格、35%/18s 同处 Safety/Latency 单元格；作者是否把不同分母/统计对象写进一个单元格？Figure 5 混合训练 Level 2 的 0.88 与正文“各级超过 0.96”以及 Safety 文字概括如何解释？
- §4.1 “GPT+ReAct clear winner”与 Figure 3 的分任务点位（CP:5000 GPT+CoT、Routing/K8s 大集 GPT+Fewshot 更高）为何不同？是否存在未在图注中说明的汇总口径？
- Figure 5 各训练条件的样本量不同（800/600/600/2,000）；若等量抽样或固定训练步数，难度覆盖效果会如何？论文未报告该控制。
- 现有例子和故障样本主要展示任务生成/模型错误；是否有完整、逐动作的真实网络调查案例，并能把任务复杂度映射到生产运维难度？当前材料不足以回答。
- 怎样独立验证 simulator-to-real transfer、安全规则覆盖和任务生成器质量？

## 13. 关联论文与主题

- [NIKA](../nika/notes.md) · [CTBench](../ctbench/notes.md) · [AgenticOpsEval](../agenticopseval/notes.md) · [RCABench](../rcabench/notes.md)
- 官方实现静态索引：[NetArena code reading](../../../code/benchmark/netarena.md) · [Paper–Code Repository Index](../../../code/repository-index.md)
- Tags: Agent Benchmark, Network Automation, Dynamic Benchmark, State Transition, Emulator, Safety Evaluation
