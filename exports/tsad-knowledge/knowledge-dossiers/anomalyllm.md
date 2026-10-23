# Knowledge Dossier — Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection（AnomalyLLM）

## 1. Basic Information

- **English title**: Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection（AnomalyLLM）
- **中文译名**：大语言模型引导的时间序列异常检测知识蒸馏
- **Authors**: Chen Liu, Shibo He, Qihang Zhou, Shizhong Li, Wenchao Meng
- **Venue / year / CCF**: IJCAI 2024 / CCF B
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: LLM 教师蒸馏与时间序列表征检测
- **Method tags**: TSAD LLM teacher knowledge distillation prototype synthetic anomalies few-shot affiliation metric

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 小样本、无监督的单变量 / 多变量 TSAD：用预训练 GPT-2 teacher 的表示作为通用参照。（§1–3, pp.1–4）
- **[实验支持]** 9 个 UCR domain groups 与 SMD、MSL、SMAP、PSM、GECCO、SWAN 六个 multivariate sets。（§4.1, Tables 1–2）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文针对无监督 TSAD 中“可用异常标签少、训练样本也有限”的情形。作者认为，许多自监督方法在小样本下难学到可迁移表示；单纯采用预训练语言模型重建时，强泛化模型又可能把未见异常也重建得很好。方法把每条多变量序列切为固定长度窗口 $w\in\mathbb R^{D\times T}$，由 teacher $\phi$ 和 student $\varphi$ 分别映射到表示空间。目标是让正常样本的两种表示接近、异常样本表示远离；无监督训练时训练窗默认正常。（§1, §3.1, PDF pp.1–3）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **小样本难以学习通用表示**：自监督 detector 通常依赖大量训练样本。（§1–2.1）
2. **teacher 与 student 可能一起拟合异常**：若训练只有正常样本，student 只模仿 teacher，可能对测试异常也得到接近表示，造成漏检。（§2, §3.4）
3. **通用 teacher 与领域正常模式之间存在差异**：teacher 希望通用，student 则需熟悉当前序列反复出现的正常形态。（§3.2–3.3）
4. **合成异常有语义风险**：局部 jittering、scaling、warping 只是代理扰动，不能保证等价于真实故障，也可能改变合法正常形态。（§3.4；最后一点为分析推断）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 仅训练 student 拟合通用 teacher 会使 student 对未见异常也过度泛化。（§2, p.2）
- **[分析推断]** prototype 能记忆常见形态但不包含 workload / 业务状态语义，检测差距不能解释波动来源。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

AnomalyLLM 用冻结大部分 GPT-2 权重的时序 teacher 产生通用表示，以逐通道可学习 prototypes 增强 student 对训练期常见模式的建模，再用局部合成扰动同时拉大 student–teacher 异常表示差距并保持 teacher 对扰动视图稳定；测试时以两者 embedding 的平方距离作窗口异常分数。（§3, Eqs. 1–8, PDF pp.3–5）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：小样本难以学习通用表示：自监督 detector 通常依赖大量训练样本。（§1–2.1）
- **C2（第4节挑战）**：teacher 与 student 可能一起拟合异常：若训练只有正常样本，student 只模仿 teacher，可能对测试异常也得到接近表示，造成漏检。（§2, §3.4）
- **C3（第4节挑战）**：通用 teacher 与领域正常模式之间存在差异：teacher 希望通用，student 则需熟悉当前序列反复出现的正常形态。（§3.2–3.3）
- **C4（第4节挑战）**：合成异常有语义风险：局部 jittering、scaling、warping 只是代理扰动，不能保证等价于真实故障，也可能改变合法正常形态。（§3.4；最后一点为分析推断）

### 7.1 GPT-2 teacher

- **作者技术描述**：**[作者主张] GPT-2 teacher**：时序 patch 经过独立线性投影输入 GPT-2；freeze attention / FFN，只微调 positional embedding、LayerNorm。（§3.3, p.4）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 GPT-2-based time-series teacher”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Prototype student

- **作者技术描述**：**[作者主张] Prototype student**：每个变量维护可训练 prototype pool，按 cosine similarity 逐通道取最相似 prototype；作为 Transformer 的额外 key/value。（§3.2, Eqs. 2–4）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Prototype-based student”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 合成异常 distillation loss

- **作者技术描述**：**[作者主张] 合成异常 distillation loss**：原始窗口对齐，扰动窗口分离；teacher 对原始和扰动视图加 cosine consistency。（§3.4, Eqs. 5–7）
- **对应挑战**：C4、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 局部合成异常与两类损失”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Discrepancy score

- **作者技术描述**：**[作者主张] Discrepancy score**：teacher / student embedding 平方距离。（Eq. 8）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 Teacher–student discrepancy objective”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
固定长度多变量窗口 w
  ├─ teacher：instance norm / patch → 线性映射 → GPT-2（attention/FFN 冻结）→ c
  ├─ student：逐通道 cosine 匹配 prototype → instance norm / patch → prototype Transformer → z
  ├─ 正常窗口：拉近 z 与 c；局部扰动窗口：推远扰动后的 student / teacher 表示
  ├─ teacher consistency：拉近 teacher 对原始与扰动视图的表示
  └─ 推理：A(w)=||z-c||²
```

（Fig. 2, §3, Eqs. 1–8, PDF pp.3–5）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 Teacher–student discrepancy objective

对一对 student / teacher 表示 $z,c$，定义

$$\ell(z,c)=\exp(-\|z-c\|_2^2),\qquad
\mathcal L=- (1-y)\log\ell(z,c)-y\log(1-\ell(z,c)). \tag{1}$$

无监督设定把训练窗当成 normal（$y=0$），于是目标是提高两表示的接近度。测试阶段若差距变大，作为异常证据。这里“正常点 close、异常点 distant”是学习设计假设，并非由无监督训练直接观测到真实故障标签。（§3.1, Eq. 1, p.3）

#### 6.2 Prototype-based student

学生模型为每个变量 $j$ 维护一个可训练原型池 $M_j=\{m_j^1,\ldots,m_j^M\}$。对输入通道 $w_j$ 与该通道各原型计算 cosine similarity，选择最相似的 prototype $m_j^s$（Eq. 2）。逐通道匹配保留 channel-independent 建模方式；匹配原型提供历史常见形状参照。它学的是窗口形态相似性，不包含业务状态名称或 workload 语义。（§3.2, Eq. 2, p.3）

输入和所选原型分别经 instance normalization、patching、线性 patch embedding 与位置编码。之后 prototype-based Transformer 以输入 patch 为 query，让输入和原型 patch 都参与 attention 的 key/value 加权；多头机制融合不同尺度信息，flatten + linear projection 得到最终 $z$（Eqs. 3–4）。所以 student 不只是计算“离最近原型多远”，而是将原型片段作为构造窗口表示的上下文。（§3.2, Fig. 2, Eqs. 3–4, pp.3–4）

#### 6.3 GPT-2-based time-series teacher

teacher 对输入做 instance normalization、patching 和独立的线性嵌入，再使用预训练 GPT-2 的位置表示与 $B$ 个 self-attention blocks。作者冻结 attention 与 feed-forward blocks，只微调 positional embedding 和 LayerNorm，以保留预训练序列建模参数并适配时序输入；最后 flatten 和线性映射得到 $c$。（§3.3, p.4）

这不是直接把数值序列交给 GPT-2 做自然语言推理：模型以可学习的输入映射和 patch 序列供 GPT-2 编码，teacher 的预测结论也不以自然语言输出。teacher 的通用性是否来自语言预训练本身，需要与其替换实验一并看，不能仅由模型名称推断。（§3.3–4.4）

#### 6.4 局部合成异常与两类损失

训练时在每个窗口随机选一段，应用 jittering、scaling 或 warping，形成合成窗口 $w^a$。原始窗口的 student / teacher 表示被拉近；扰动窗口两表示被推远。论文给出：

$$\mathcal L_{kd}=\frac1N\sum_i\left[\|z_i-c_i\|_2^2-\log\left(1-\exp(-\|z_i^a-c_i^a\|_2^2)\right)\right]. \tag{5}$$

其中前项对应 normal 原样本，后项鼓励合成异常的两端表示分离。作者还用 teacher consistency 项：

$$\mathcal L_{ce}=\frac1N\sum_i -\frac{c_i}{\|c_i\|_2}\cdot\frac{c_i^a}{\|c_i^a\|_2},\qquad
\mathcal L_{total}=\mathcal L_{kd}+\lambda\mathcal L_{ce}. \tag{6–7}$$

这个项将 teacher 对原始与扰动视图视为 positive pair，鼓励其保留更稳定的通用表示；于是 Eq. 5 推远 synthetic pair 中的 student–teacher，Eq. 6 却保持 teacher 自身跨视图相似。没有 student consistency loss；作者的消融显示额外把 student 原始 / 扰动表示拉开反而降低效果。（§3.4, Eqs. 5–7, pp.4–5；§4.4, p.7）

#### 6.5 推理分数

对测试窗口 $w$，按

$$A(w)=\|\varphi(w)-\phi(w)\|_2^2. \tag{8}$$

计算异常分数。论文按 window 进行检测；需将窗口分数映射到时间戳，具体窗口汇聚及 threshold 协议应结合实验实现核对。（§3.4, Eq. 8, p.5）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (5)、Eq. (6)、Eq. (8)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.1 Teacher–student discrepancy objective；6.4 局部合成异常与两类损失；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.5 推理分数及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

AnomalyLLM 用冻结大部分 GPT-2 权重的时序 teacher 产生通用表示，以逐通道可学习 prototypes 增强 student 对训练期常见模式的建模，再用局部合成扰动同时拉大 student–teacher 异常表示差距并保持 teacher 对扰动视图稳定；测试时以两者 embedding 的平方距离作窗口异常分数。（§3, Eqs. 1–8, PDF pp.3–5）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 数据集、对照与指标

- **UCR**：250 条 univariate archive 按领域聚合成 9 组（ABP、Acceleration、AirTemperature、ECG、EPG、Gait、NASA、PowerDemand、RESP）。（§4.1, Table 1, p.5）
- **多变量集**：SMD、MSL、SMAP、PSM、GECCO、SWAN。（§4.1, Table 2, p.6）
- **对照**：DeepSVDD、THOC、NCAD、MTGFlow、AnoTrans、MEMTO、TS-TCC、COCA、DCdetector、GPT4TS 等 10 个方法。（§4.2, pp.5–6）
- **指标**：UCR 采用 affiliation precision / recall / F1（AF1）以及把数据集分域分类的 accuracy；多变量表另报告与 prior work 对齐的 point-adjusted F1。AF1、accuracy 与 PA-F1 衡量的任务不同，不宜合成一个排名。（§4.2–4.3, pp.5–6）
- **设置**：GPT-2 teacher 为 6 层；student prototype pool 主设置 32、attention 中间维 64、8 heads；Adam $10^{-4}$、batch 32；单张 RTX 3090。（§4.2, p.5）

#### 7.2 主要结果

- **UCR Table 3**：总 accuracy 0.820、AF1 0.858；最强对照 NCAD 为 0.663 / 0.767。作者据此报告平均 accuracy 提升 22.2%、AF1 提升 10.0%，并称总计检出 82% 的异常。总表中 PowerDemand AF1 为 .886，RESP 为 .736，说明提升并非对每个领域都同幅度。（§4.3, Table 3, PDF p.6）
- **SMD / MSL / SMAP / PSM Table 4**：adjusted F1 分别 .958 / .956 / .965 / .997，处于与当时方法可比的水平。作者称这些数据集包含较多明显异常；此表不等同 UCR 的 affiliation protocol。（§4.3, Table 4, p.6）
- **WaQ / SWAN Table 5**：ours F1 .620 / .804，对比 DCdetector .466 / .734。（Table 5, p.6）正文却有一句写成“62% vs 47% on GECCO”；表 5 实际列名是 WaQ，GECCO 出现在 Table 2 的数据集清单而非 Table 5 结果列。此处应记录为论文内部数据集名称不一致，不能照正文把分数归到 GECCO。（§4.3, Table 5, p.6）

#### 7.3 消融与敏感性

- **Teacher 结构替换**：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界）
- **Student 结构**：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，支持显式常见形态记忆。（§4.4, p.6）
- **训练目标**：不增强的 NonAug 最差；去掉 teacher consistency 比 NonAug 提升 AF1 4.2%，但仍低于完整方法；加入额外 student consistency 使 AF1 下降 8.0%。（§4.4, Fig. 5, p.7）
- **敏感性**：window size 增大时 UCR accuracy 保持 72% 以上、AF1 80% 以上；warping 有益；GPT-2 至少 3 层后趋稳，projector 3 层最好。主设置 prototype pool 写 32，而敏感性分析说 48 最有用，两个配置口径不同，复现要以附录实现 / 配置为准。（§4.4, Fig. 4, pp.6–7）
- **少样本 / zero-shot case**：PowerDemand 全数据、50%、20%、10%、zero-shot 条件下 F1 为 .886 / .817 / .784 / .781 / .650。（Table 6, p.7）这是单个数据集案例，不足以单独支持跨场景普遍迁移结论。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations and Critical Reading

**[作者说明]** teacher 部署成本 / memory 较高，结论中提出研究轻量 teacher。（§5, p.8）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[实验支持]** synthetic anomaly 的结果依赖三类扰动代理；论文没有 workload / release / Trace 条件的合法波动与故障并发实验。（§3.4, §4）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[分析推断]** prototype 是时间形态参照，能覆盖常见局部形状但没有语义化的多运行状态标签；发生未见但合法的状态切换时，差距仍可能升高。

#### 精读笔记原章节：9. Limitations and Critical Reading

**[实验口径]** UCR 的 domain accuracy、affiliation event metrics 与其他表的 adjusted F1 不同；UCR 单域 9 组总均值不能证明跨组织真实迁移。（Tables 3–5）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[复现风险]** 文中主设置 32 prototypes 与敏感性结论 48 prototypes 不一致；WaQ / GECCO 的一句文字也与 Table 5 结果列不一致。（§4.2–4.4）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[分析推断]** 表示差距只能提供“未被 student 模仿”的异常证据，不解释异常来自业务事件、状态切换、传感器故障还是负载冲击。

### C. 仍缺乏证据的问题

未做的实验只标记为证据边界，不解释为方法不具备该能力。具体未充分验证项见上方原精读笔记限制章节。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 将 prototype 按 workload / release / service state 条件化，并设计保护机制阻止疑似故障污染更新。
- **[分析推断]** 把正常状态切换、单独故障、状态切换与故障并发做成受控实验；报告 validation-only threshold 和事件延迟。
- **[分析推断]** 公开统一复现配置，拆分 prototype、teacher prior、扰动语义的贡献。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **Delving into LLMs for TSAD**：同属 LLM TSAD，但采用无训练的 de-seasonalization + index-aware prompting，重点解决理解与定位失败；AnomalyLLM 把 LLM 作为表示 teacher，并训练 student。
- **AnomSeer**：视觉 MLLM 通过 ExpCoT + TimerPO 做 post-training，强调统计证据与可读解释；AnomalyLLM 不输出自然语言解释，而用 embedding discrepancy 检测。
- **TSB-AD / Quo Vadis**：帮助解释异常评分、affiliation、point-adjusted F1 与阈值的比较边界。
- **CAROTS / MACE / When Model Meets New Normals**：分别从因果保持增强、多模态态频谱模式、测试时状态适应角度建模正常变化；prototype pool 是另一种常见形态参照，但不做状态语义辨识。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | PDF pp.1–3, §1, §3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §1–2.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §2, §3.4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.2–3.3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §2 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | PDF pp.3–5, §3, Eqs. 1–8, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.1, Eq. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.2, Eq. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.2, Eqs. 3–4, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.3 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.3–4.4 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.4, §4.4, Eq. 5, Eq. 6, Eqs. 5–7 | 精读笔记保留的原文定位 |
| Method / formulas | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §3.4, Eq. 8 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.1, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.1, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.2 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.2–4.3 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | PDF p.6, §4.3, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.3, Table 4 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.3, Table 5, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf | §4.4 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "anomalyllm",
  "title_en": "Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection（AnomalyLLM）",
  "title_zh": "大语言模型引导的时间序列异常检测知识蒸馏",
  "authors": [
    "Chen Liu",
    "Shibo He",
    "Qihang Zhou",
    "Shizhong Li",
    "Wenchao Meng"
  ],
  "year": 2024,
  "venue": "IJCAI",
  "ccf_level": "B",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2024/IJCAI/Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/anomalyllm/notes.md",
  "code_url": null,
  "research_area": "LLM 教师蒸馏与时间序列表征检测",
  "method_tags": [
    "TSAD LLM teacher knowledge distillation prototype synthetic anomalies few-shot affiliation metric"
  ],
  "research_scenario": "- [作者主张] 小样本、无监督的单变量 / 多变量 TSAD：用预训练 GPT-2 teacher 的表示作为通用参照。（§1–3, pp.1–4） - [实验支持] 9 个 UCR domain groups 与 SMD、MSL、SMAP、PSM、GECCO、SWAN 六个 multivariate sets。（§4.1, Tables 1–2）",
  "research_problem": "论文针对无监督 TSAD 中“可用异常标签少、训练样本也有限”的情形。作者认为，许多自监督方法在小样本下难学到可迁移表示；单纯采用预训练语言模型重建时，强泛化模型又可能把未见异常也重建得很好。方法把每条多变量序列切为固定长度窗口 $w\\in\\mathbb R^{D\\times T}$，由 teacher $\\phi$ 和 student $\\varphi$ 分别映射到表示空间。目标是让正常样本的两种表示接近、异常样本表示远离；无监督训练时训练窗默认正常。（§1, §3.1, PDF pp.1–3）",
  "core_challenges": [
    "小样本难以学习通用表示：自监督 detector 通常依赖大量训练样本。（§1–2.1）",
    "teacher 与 student 可能一起拟合异常：若训练只有正常样本，student 只模仿 teacher，可能对测试异常也得到接近表示，造成漏检。（§2, §3.4）",
    "通用 teacher 与领域正常模式之间存在差异：teacher 希望通用，student 则需熟悉当前序列反复出现的正常形态。（§3.2–3.3）",
    "合成异常有语义风险：局部 jittering、scaling、warping 只是代理扰动，不能保证等价于真实故障，也可能改变合法正常形态。（§3.4；最后一点为分析推断）"
  ],
  "existing_method_limits": [
    "[作者主张] 仅训练 student 拟合通用 teacher 会使 student 对未见异常也过度泛化。（§2, p.2）",
    "[分析推断] prototype 能记忆常见形态但不包含 workload / 业务状态语义，检测差距不能解释波动来源。"
  ],
  "core_idea": "AnomalyLLM 用冻结大部分 GPT-2 权重的时序 teacher 产生通用表示，以逐通道可学习 prototypes 增强 student 对训练期常见模式的建模，再用局部合成扰动同时拉大 student–teacher 异常表示差距并保持 teacher 对扰动视图稳定；测试时以两者 embedding 的平方距离作窗口异常分数。（§3, Eqs. 1–8, PDF pp.3–5）",
  "technical_innovations": [
    {
      "name": "GPT-2 teacher",
      "author_claim": "**[作者主张] GPT-2 teacher**：时序 patch 经过独立线性投影输入 GPT-2；freeze attention / FFN，只微调 positional embedding、LayerNorm。（§3.3, p.4）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 GPT-2-based time-series teacher",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] GPT-2 teacher**：时序 patch 经过独立线性投影输入 GPT-2；freeze attention / FFN，只微调 positional embedding、LayerNorm。（§3.3, p.4）"
    },
    {
      "name": "Prototype student",
      "author_claim": "**[作者主张] Prototype student**：每个变量维护可训练 prototype pool，按 cosine similarity 逐通道取最相似 prototype；作为 Transformer 的额外 key/value。（§3.2, Eqs. 2–4）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Prototype-based student",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Prototype student**：每个变量维护可训练 prototype pool，按 cosine similarity 逐通道取最相似 prototype；作为 Transformer 的额外 key/value。（§3.2, Eqs. 2–4）"
    },
    {
      "name": "合成异常 distillation loss",
      "author_claim": "**[作者主张] 合成异常 distillation loss**：原始窗口对齐，扰动窗口分离；teacher 对原始和扰动视图加 cosine consistency。（§3.4, Eqs. 5–7）",
      "challenge_ids": [
        "C4",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 局部合成异常与两类损失",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] 合成异常 distillation loss**：原始窗口对齐，扰动窗口分离；teacher 对原始和扰动视图加 cosine consistency。（§3.4, Eqs. 5–7）"
    },
    {
      "name": "Discrepancy score",
      "author_claim": "**[作者主张] Discrepancy score**：teacher / student embedding 平方距离。（Eq. 8）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 Teacher–student discrepancy objective",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Discrepancy score**：teacher / student embedding 平方距离。（Eq. 8）"
    }
  ],
  "methodology": {
    "architecture": "text 固定长度多变量窗口 w ├─ teacher：instance norm / patch → 线性映射 → GPT-2（attention/FFN 冻结）→ c ├─ student：逐通道 cosine 匹配 prototype → instance norm / patch → prototype Transformer → z ├─ 正常窗口：拉近 z 与 c；局部扰动窗口：推远扰动后的 student / teacher 表示 ├─ teacher consistency：拉近 teacher 对原始与扰动视图的表示 └─ 推理：A(w)=||z-c||² （Fig. 2, §3, Eqs. 1–8, PDF pp.3–5）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 Teacher–student discrepancy objective",
      "6.2 Prototype-based student",
      "6.3 GPT-2-based time-series teacher",
      "6.4 局部合成异常与两类损失",
      "6.5 推理分数"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (5)",
      "Eq. (6)",
      "Eq. (8)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "AnomalyLLM 用冻结大部分 GPT-2 权重的时序 teacher 产生通用表示，以逐通道可学习 prototypes 增强 student 对训练期常见模式的建模，再用局部合成扰动同时拉大 student–teacher 异常表示差距并保持 teacher 对扰动视图稳定；测试时以两者 embedding 的平方距离作窗口异常分数。（§3, Eqs. 1–8, PDF pp.3–5）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 数据集、对照与指标",
      "- UCR：250 条 univariate archive 按领域聚合成 9 组（ABP、Acceleration、AirTemperature、ECG、EPG、Gait、NASA、PowerDemand、RESP）。（§4.1, Table 1, p.5） - 多变量集：SMD、MSL、SMAP、PSM、GECCO、SWAN。（§4.1, Table 2, p.6） - 对照：DeepSVDD、THOC、NCAD、MTGFlow、AnoTrans、MEMTO、TS-TCC、COCA、DCdetector、GPT4TS 等 10 个方法。…",
      "- UCR Table 3：总 accuracy 0.820、AF1 0.858；最强对照 NCAD 为 0.663 / 0.767。作者据此报告平均 accuracy 提升 22.2%、AF1 提升 10.0%，并称总计检出 82% 的异常。总表中 PowerDemand AF1 为 .886，RESP 为 .736，说明提升并非对每个领域都同幅度。（§4.3, Table 3, PDF p.6） - SMD / MSL / SMAP / PSM Table 4：adjusted F1 分别 .958 / .956 / .965 / .997，处于与当时方法可比的水平。作者称这些数据集包含较多明显异常；…",
      "- Teacher 结构替换：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界） - Student 结构：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，…"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 7.1 数据集、对照与指标",
      "- UCR：250 条 univariate archive 按领域聚合成 9 组（ABP、Acceleration、AirTemperature、ECG、EPG、Gait、NASA、PowerDemand、RESP）。（§4.1, Table 1, p.5） - 多变量集：SMD、MSL、SMAP、PSM、GECCO、SWAN。（§4.1, Table 2, p.6） - 对照：DeepSVDD、THOC、NCAD、MTGFlow、AnoTrans、MEMTO、TS-TCC、COCA、DCdetector、GPT4TS 等 10 个方法。…",
      "- UCR Table 3：总 accuracy 0.820、AF1 0.858；最强对照 NCAD 为 0.663 / 0.767。作者据此报告平均 accuracy 提升 22.2%、AF1 提升 10.0%，并称总计检出 82% 的异常。总表中 PowerDemand AF1 为 .886，RESP 为 .736，说明提升并非对每个领域都同幅度。（§4.3, Table 3, PDF p.6） - SMD / MSL / SMAP / PSM Table 4：adjusted F1 分别 .958 / .956 / .965 / .997，处于与当时方法可比的水平。作者称这些数据集包含较多明显异常；…",
      "- Teacher 结构替换：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界） - Student 结构：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，…"
    ],
    "main_results": [
      "- UCR：250 条 univariate archive 按领域聚合成 9 组（ABP、Acceleration、AirTemperature、ECG、EPG、Gait、NASA、PowerDemand、RESP）。（§4.1, Table 1, p.5） - 多变量集：SMD、MSL、SMAP、PSM、GECCO、SWAN。（§4.1, Table 2, p.6） - 对照：DeepSVDD、THOC、NCAD、MTGFlow、AnoTrans、MEMTO、TS-TCC、COCA、DCdetector、GPT4TS 等 10 个方法。…",
      "- UCR Table 3：总 accuracy 0.820、AF1 0.858；最强对照 NCAD 为 0.663 / 0.767。作者据此报告平均 accuracy 提升 22.2%、AF1 提升 10.0%，并称总计检出 82% 的异常。总表中 PowerDemand AF1 为 .886，RESP 为 .736，说明提升并非对每个领域都同幅度。（§4.3, Table 3, PDF p.6） - SMD / MSL / SMAP / PSM Table 4：adjusted F1 分别 .958 / .956 / .965 / .997，处于与当时方法可比的水平。作者称这些数据集包含较多明显异常；此表不等同 UCR 的 affiliation protocol。…",
      "- Teacher 结构替换：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界） - Student 结构：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，支持显式常见形态记忆。（§4.4, p.6） - 训练目标：不增强的 NonAug 最差；…"
    ],
    "ablations": [
      "### 7.3 消融与敏感性",
      "- Teacher 结构替换：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界） - Student 结构：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "[作者说明] teacher 部署成本 / memory 较高，结论中提出研究轻量 teacher。（§5, p.8）",
      "[实验支持] synthetic anomaly 的结果依赖三类扰动代理；论文没有 workload / release / Trace 条件的合法波动与故障并发实验。（§3.4, §4）",
      "[分析推断] prototype 是时间形态参照，能覆盖常见局部形状但没有语义化的多运行状态标签；发生未见但合法的状态切换时，差距仍可能升高。",
      "[实验口径] UCR 的 domain accuracy、affiliation event metrics 与其他表的 adjusted F1 不同；UCR 单域 9 组总均值不能证明跨组织真实迁移。（Tables 3–5）",
      "[复现风险] 文中主设置 32 prototypes 与敏感性结论 48 prototypes 不一致；WaQ / GECCO 的一句文字也与 Table 5 结果列不一致。（§4.2–4.4）",
      "[分析推断] 表示差距只能提供“未被 student 模仿”的异常证据，不解释异常来自业务事件、状态切换、传感器故障还是负载冲击。"
    ],
    "evidence_gaps": [
      "未报告的环境属于证据不足，不等于方法能力不足"
    ]
  },
  "research_implications": [
    "- [分析推断] 将 prototype 按 workload / release / service state 条件化，并设计保护机制阻止疑似故障污染更新。 - [分析推断] 把正常状态切换、单独故障、状态切换与故障并发做成受控实验；报告 validation-only threshold 和事件延迟。 - [分析推断] 公开统一复现配置，拆分 prototype、teacher prior、扰动语义的贡献。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "carots",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomseer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomalyllm",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–3, §1, §3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2, §3.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.2–3.3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–5, §3, Eqs. 1–8, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.1, Eq. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.2, Eq. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3.2, Eqs. 3–4, Fig. 2",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "ddec5e5bc64fba82a6d70687028057349cb716f04aff3e7c639357f66c33461b",
    "reading_note_sha256": "a8bfcd7a01a404272596a50d18c5c5e9046f0198dcef1fa4ffae97bec431eb6a",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "56c963c7140fb0a44894e4161de06c4ab35ce1c78d994161cf05205fd74407b6"
  },
  "knowledge_card_path": "papers/anomalyllm/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
