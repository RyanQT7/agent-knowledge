# CTBench：电信网络 Agent 的部分可观测排障评测

## 论文身份与阅读范围

- **标题：** *CTBench: Evaluating Troubleshooting Capabilities of AI Agents in Realistic Telecom Network Operations*。
- **作者：** Xingyu Yan, Tingting Dai, Antonio De Domenico, Mohamed Sana, Nicola Piovesan, Changchang Li, Bowen Liu, Kun Jiang, Mengjie Zhang, Dingcheng Shan, Jing-Cheng Pang, Chenwei Wu, Sijie Wu, Lianying Chao, Haoran Cai, Jiantao Ye, Xubin Li, Simon Mark Lucas, Xin Chen。
- **版本：** arXiv:2608.12002v2，2026-10-21。[论文](https://arxiv.org/abs/2608.12002)；[公开数据卡](https://huggingface.co/datasets/netop/CTBench)。未核实到独立官方代码仓库。
- **本地材料：** [PDF](../../../sources/papers/benchmark/CTBench_2608.12002.pdf) 与全文抽取文本；已完整阅读论文正文及任务/指标附录。未下载带访问条件的数据、未运行 Agent。

## 1. 研究问题与数据边界

电信运维任务需要从不同厂商 CLI、拓扑关系和有限观察中逐步排查：形成假设、选择命令、解释输出、排除替代原因，再给出最小故障集合或恢复路径。CTBench 把这种过程建成 234 个专家整理任务：126 个 RCA、108 个 path restoration。

案例来自脱敏真实维护场景和多厂商设备 CLI 输出，但运行环境是 **replay-based mock backend**：给定设备/命令时回放记录输出，缺少的命令被拒绝；Agent 不会改变真实路由或设备状态。它比静态问答更接近多轮调查，却仍不能测试动态修复、命令副作用或实时网络应答。（§3.1–3.2）

## 2. 任务、Ground Truth 与专家筛选

### 任务输出

- RCA 预测一个或多个 `(node, object, root_cause)`，可包含独立根因；根因对象可为设备、接口、地址、策略等。
- Path restoration 预测有序转发路径，保留节点/接口/路径分支语义。
- 任务元数据标注可观测性 O1/O2、故障类别、独立根因数、传播链长度、路径数、golden solution 长度、异构程度等。

O1 表示允许命令可以直接得到决定性证据；O2 表示直观命令不可用或失败，需从间接观测推理并交叉核对。它提供了按信息可见性分析而非只按平均分汇总的基础。（§3.4，Table 2）

### 任务筛选过程

15 名资深电信专家（平均约 20 年经验）撰写任务接口、答案、操作约束和元数据。初始 359 个候选（205 RCA、154 path），最终保留 234 个（126 RCA、108 path）；最终保留任务中有 154 个经过修改。独立专家在看不到预设答案和轨迹时盲解候选，再检查可解性、答案完整性、golden actions 与元数据一致性；无法达成作者—审阅者共识的任务删除。（§3.2）

这是一套强调“题目确实可从提供的证据中解出”的流程。盲解能发现无解/漏标，但不等于多名专家对每条真实故障原因达成统计一致性；论文未对每个题目都进行多个独立专家解题复现。

## 3. Golden actions：过程指标测量什么

每个问题对应专家验证的 key evidence commands 集合 \(A^*\)。Agent 实际执行命令集合记为 \(\hat A\)，golden-action coverage 为：

\[
\mathrm{Evidence} = \frac{|A^*\cap \hat A|}{|A^*|}
\]

跨任务将命中动作数与 golden action 总数汇总后求比例。匹配要求正确设备和精确命令；任务制作时排除等价替代命令，因此它衡量的是“覆盖该题指定参考路线”，而非一般意义上的证据充分性。独立检查顺序可以不同；对同一问题用不同但等价 CLI 查询得到正确证据会被低估。（§3.3）

**真实例：** Appendix A.7 的 RCA‑90 要诊断从 `Site1 area, Access‑PC‑01` 到 `20.1.1.10` 不通。答案有两个独立根因：`BoardLeaf-01;GE1/0/0;shutdown` 与 `BoardLeaf-01;GE1/0/1;shutdown`。它属于 O1，golden 路线包含接口描述、当前配置、LLDP 邻居检查三步。这个例子要求模型区分两条被关闭的接口，而不能把一条链路问题写成笼统“网络不通”。

**路径例：** PR‑100 从深圳数据中心服务器到上海分支 PC，gold path 有 12 个有序元素、横跨深圳核心、PE、北京网关及上海汇聚；专家路线有 33 个关键检查。只找到起终点不是完整恢复，整条路径和接口顺序都影响 Path‑Rest。（Appendix A.7）

## 4. 评价指标：最终答案、定位、过程与成本分开

### RCA

- Exact Accuracy：标准化答案与 Gold 完全相同的任务比例。
- **RCA-Loc**：每题预测与 Gold 的受影响 `(node, object)` 集合 IoU 的宏平均。
- **RCA-ID**：每题预测与 Gold 根因类型集合 IoU 的宏平均。
- **RCA-Evidence**：golden action recall；是合并动作计数的 pooled ratio。
- 分层 RCA/拓扑相似度仅辅助解释近似错误，不替代主指标。

集合 IoU 为 \(|X\cap Y|/|X\cup Y|\)。例如 Gold 有两条根因接口，Agent 只报出其中一条且无误报，则该组 IoU=1/2；Exact Accuracy 仍为 0。这两类指标回答不同问题。

### Path restoration

- **Path-Loc**：预测/标注的角色标记端点集合 IoU；source 和 destination 不能对调。
- **Path-Rest**：有向路径边集合 IoU；路径顺序、方向和接口信息重要。
- **Path-Evidence**：golden action coverage。

Path-Loc 很高仍可能漏中间路径。主论文另报告 task-level exact accuracy；IoU 是按任务计算后宏平均。成本独立报告 latency、interaction rounds、tokens；\(Tokens_{total}=Tokens_{input}+Tokens_{output}\)。

## 5. 实验结果与案例含义

实验用四组固定 Agent–LLM harness，zero-shot、共享任务集合、单次 Pass@1、无重试；每任务 3,600 秒超时。表内误差是任务间标准误而非同一任务重复运行方差。

| 配置 | RCA Exact | RCA-Loc | RCA-ID | RCA evidence | Path exact | Path-Loc | Path-Rest | Path evidence |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Codex + GPT‑5.5 (medium) | 47.62% | 63.99% | 74.74% | 51.64% | 87.96% | 99.38% | 95.42% | 55.81% |
| ClaudeCode + Sonnet‑5.5 (medium) | 34.92% | 55.36% | 70.90% | 26.81% | 32.41% | 98.46% | 77.45% | 14.52% |
| Hermes + DeepSeek‑V4‑Pro (high) | 17.46% | 37.74% | 49.47% | 41.13% | 26.85% | 85.49% | 65.42% | 21.52% |
| Hermes + Qwen3.7‑Max (medium) | 25.40% | 45.03% | 59.46% | 34.95% | 40.74% | 81.48% | 67.48% | 20.25% |

Codex 平均约 10.81 rounds/333.4s/476.5K tokens 做 RCA，路径任务约 14.14 rounds/419.8s/1,019.2K tokens。ClaudeCode 约 2.7M token 的 RCA 消耗仍低于 Codex 的主要答案成绩；成本不能作为能力代理。（§5.1–5.2，Tables 5–6）

更重要的是：在精确答对的 Codex 任务中，RCA 的 60 题有 47 题没覆盖完整参考证据；路径任务 95 题有 93 题缺少至少一个 golden action。该子集的证据 coverage（60.42% / 56.15%）与全任务 Table 5 pooled coverage（51.64% / 55.81%）分母不同，不应混用。结果说明“答对”和“按专家建议收集证据”是不同能力，不足以单凭路线未命中断言模型完全没有其它合理证据。（Table 18）

O2→O1 的 19 个 RCA 任务消融给部分任务添加直接证据。Codex exact accuracy 从 36.84% 到 73.68%，其余模型也有变化；但这反映信息可见性变化，不是单纯提示技巧。由于参考动作数从平均 4.32 减到 2.95，两个设置下的 coverage 分母不同，coverage 数字不能直接对比。异构度高的 RCA exact 下降也只是不同任务子集间相关性，非受控因果证据。（§5.4）

5 名人类专家分别答题，RCA 126 题答对 102（80.95%），路径 108 题答对 104（96.30%），每题需约 40–60 分钟。专家与 Agent 的覆盖率不能直接视为成对比较，因为每题由单一专家作答，模型评测协议与专家工作时间不同。（§5）

## 6. 复现、Shortcut 与局限

- **Replay 边界：** 已知设备/命令回放固定输出，未模拟真实网络随动作变化、实际配置修改或恢复。
- **路线偏置：** 排除替代等价命令使过程评分可复现，但可能惩罚有效替代调查。
- **任务泄漏风险（待测，不是作者证实）：** CLI 输出格式、设备型号或固定 replay 响应可能暴露任务家族；应按设备/vendor/协议/任务模板留出。
- **答案/过程分离：** 分数显示 fault identification 通常高于精确定位；获得正确 endpoint 不代表完整路径恢复；证据 coverage 也不证明 Agent 将证据用于正确因果推断。
- **预算：** 只设单任务 1 小时和 Pass@1；没有单任务最大 tool step、round 或 Token 上限。论文报告实际资源，不意味着有硬预算治理。
- **统计：** 标准误只刻画任务抽样变化，不刻画模型随机种子/重复运行差异。

## 7. 开放性与数据/代码

论文描述公开任务数据与数据卡；当前 [Hugging Face 数据卡](https://huggingface.co/datasets/netop/CTBench)可查看项目说明，但数据文件需要接受使用条件/登录后才能访问。本次没有下载数据。没有核实到单独官方 Git 源码库或可静态审阅的 scorer，因此只按论文公式分析，不能声称源码复现。Replay 的具体输出一致性、工具版本和完整任务数据都需在后续取得数据后复核。

## 8. 对网络 AIOps 数据集的启发

CTBench 适合补充网络 Agent 的调查层指标：最终实体/原因、路径恢复、参考证据动作、实际 Tokens/时延/轮数分别报告；通过 O1/O2 与故障传播长度描述问题难度。对我们数据集，不能把单一专家命令路线当唯一正确过程。更合适的做法是将必须证据节点和可替代操作分开标记，允许等价命令并按语义证据评分；若要评修复，还需真实状态转移、变更权限、安全回滚和恢复验证数据。

关联：[NIKA](../nika/notes.md) 的可交互仿真、[AgenticOpsEval](../agenticopseval/notes.md) 的证据 checkpoint 和[综合对比](../../../notes/benchmark/benchmark-comparison.md)。
