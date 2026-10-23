# Large Language Model Guided Knowledge Distillation for Time Series Anomaly Detection（AnomalyLLM）

## 1. Metadata

- **Authors**: Chen Liu, Shibo He, Qihang Zhou, Shizhong Li, Wenchao Meng
- **Year / Venue**: 2024 / IJCAI（CCF B，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf)
- **Official proceedings**: [IJCAI 2024, paper 0239](https://www.ijcai.org/proceedings/2024/0239.pdf)
- **Code**: PDF 正文未提供代码仓库链接。
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

AnomalyLLM 用冻结大部分 GPT-2 权重的时序 teacher 产生通用表示，以逐通道可学习 prototypes 增强 student 对训练期常见模式的建模，再用局部合成扰动同时拉大 student–teacher 异常表示差距并保持 teacher 对扰动视图稳定；测试时以两者 embedding 的平方距离作窗口异常分数。（§3, Eqs. 1–8, PDF pp.3–5）

## 3. Background and Problem Definition

论文针对无监督 TSAD 中“可用异常标签少、训练样本也有限”的情形。作者认为，许多自监督方法在小样本下难学到可迁移表示；单纯采用预训练语言模型重建时，强泛化模型又可能把未见异常也重建得很好。方法把每条多变量序列切为固定长度窗口 $w\in\mathbb R^{D\times T}$，由 teacher $\phi$ 和 student $\varphi$ 分别映射到表示空间。目标是让正常样本的两种表示接近、异常样本表示远离；无监督训练时训练窗默认正常。（§1, §3.1, PDF pp.1–3）

## 4. Core Challenges

1. **小样本难以学习通用表示**：自监督 detector 通常依赖大量训练样本。（§1–2.1）
2. **teacher 与 student 可能一起拟合异常**：若训练只有正常样本，student 只模仿 teacher，可能对测试异常也得到接近表示，造成漏检。（§2, §3.4）
3. **通用 teacher 与领域正常模式之间存在差异**：teacher 希望通用，student 则需熟悉当前序列反复出现的正常形态。（§3.2–3.3）
4. **合成异常有语义风险**：局部 jittering、scaling、warping 只是代理扰动，不能保证等价于真实故障，也可能改变合法正常形态。（§3.4；最后一点为分析推断）

## 5. Architecture Overview

```text
固定长度多变量窗口 w
  ├─ teacher：instance norm / patch → 线性映射 → GPT-2（attention/FFN 冻结）→ c
  ├─ student：逐通道 cosine 匹配 prototype → instance norm / patch → prototype Transformer → z
  ├─ 正常窗口：拉近 z 与 c；局部扰动窗口：推远扰动后的 student / teacher 表示
  ├─ teacher consistency：拉近 teacher 对原始与扰动视图的表示
  └─ 推理：A(w)=||z-c||²
```

（Fig. 2, §3, Eqs. 1–8, PDF pp.3–5）

## 6. Method in Detail

### 6.1 Teacher–student discrepancy objective

对一对 student / teacher 表示 $z,c$，定义

$$\ell(z,c)=\exp(-\|z-c\|_2^2),\qquad
\mathcal L=- (1-y)\log\ell(z,c)-y\log(1-\ell(z,c)). \tag{1}$$

无监督设定把训练窗当成 normal（$y=0$），于是目标是提高两表示的接近度。测试阶段若差距变大，作为异常证据。这里“正常点 close、异常点 distant”是学习设计假设，并非由无监督训练直接观测到真实故障标签。（§3.1, Eq. 1, p.3）

### 6.2 Prototype-based student

学生模型为每个变量 $j$ 维护一个可训练原型池 $M_j=\{m_j^1,\ldots,m_j^M\}$。对输入通道 $w_j$ 与该通道各原型计算 cosine similarity，选择最相似的 prototype $m_j^s$（Eq. 2）。逐通道匹配保留 channel-independent 建模方式；匹配原型提供历史常见形状参照。它学的是窗口形态相似性，不包含业务状态名称或 workload 语义。（§3.2, Eq. 2, p.3）

输入和所选原型分别经 instance normalization、patching、线性 patch embedding 与位置编码。之后 prototype-based Transformer 以输入 patch 为 query，让输入和原型 patch 都参与 attention 的 key/value 加权；多头机制融合不同尺度信息，flatten + linear projection 得到最终 $z$（Eqs. 3–4）。所以 student 不只是计算“离最近原型多远”，而是将原型片段作为构造窗口表示的上下文。（§3.2, Fig. 2, Eqs. 3–4, pp.3–4）

### 6.3 GPT-2-based time-series teacher

teacher 对输入做 instance normalization、patching 和独立的线性嵌入，再使用预训练 GPT-2 的位置表示与 $B$ 个 self-attention blocks。作者冻结 attention 与 feed-forward blocks，只微调 positional embedding 和 LayerNorm，以保留预训练序列建模参数并适配时序输入；最后 flatten 和线性映射得到 $c$。（§3.3, p.4）

这不是直接把数值序列交给 GPT-2 做自然语言推理：模型以可学习的输入映射和 patch 序列供 GPT-2 编码，teacher 的预测结论也不以自然语言输出。teacher 的通用性是否来自语言预训练本身，需要与其替换实验一并看，不能仅由模型名称推断。（§3.3–4.4）

### 6.4 局部合成异常与两类损失

训练时在每个窗口随机选一段，应用 jittering、scaling 或 warping，形成合成窗口 $w^a$。原始窗口的 student / teacher 表示被拉近；扰动窗口两表示被推远。论文给出：

$$\mathcal L_{kd}=\frac1N\sum_i\left[\|z_i-c_i\|_2^2-\log\left(1-\exp(-\|z_i^a-c_i^a\|_2^2)\right)\right]. \tag{5}$$

其中前项对应 normal 原样本，后项鼓励合成异常的两端表示分离。作者还用 teacher consistency 项：

$$\mathcal L_{ce}=\frac1N\sum_i -\frac{c_i}{\|c_i\|_2}\cdot\frac{c_i^a}{\|c_i^a\|_2},\qquad
\mathcal L_{total}=\mathcal L_{kd}+\lambda\mathcal L_{ce}. \tag{6–7}$$

这个项将 teacher 对原始与扰动视图视为 positive pair，鼓励其保留更稳定的通用表示；于是 Eq. 5 推远 synthetic pair 中的 student–teacher，Eq. 6 却保持 teacher 自身跨视图相似。没有 student consistency loss；作者的消融显示额外把 student 原始 / 扰动表示拉开反而降低效果。（§3.4, Eqs. 5–7, pp.4–5；§4.4, p.7）

### 6.5 推理分数

对测试窗口 $w$，按

$$A(w)=\|\varphi(w)-\phi(w)\|_2^2. \tag{8}$$

计算异常分数。论文按 window 进行检测；需将窗口分数映射到时间戳，具体窗口汇聚及 threshold 协议应结合实验实现核对。（§3.4, Eq. 8, p.5）

## 7. Experimental Design and Evidence

### 7.1 数据集、对照与指标

- **UCR**：250 条 univariate archive 按领域聚合成 9 组（ABP、Acceleration、AirTemperature、ECG、EPG、Gait、NASA、PowerDemand、RESP）。（§4.1, Table 1, p.5）
- **多变量集**：SMD、MSL、SMAP、PSM、GECCO、SWAN。（§4.1, Table 2, p.6）
- **对照**：DeepSVDD、THOC、NCAD、MTGFlow、AnoTrans、MEMTO、TS-TCC、COCA、DCdetector、GPT4TS 等 10 个方法。（§4.2, pp.5–6）
- **指标**：UCR 采用 affiliation precision / recall / F1（AF1）以及把数据集分域分类的 accuracy；多变量表另报告与 prior work 对齐的 point-adjusted F1。AF1、accuracy 与 PA-F1 衡量的任务不同，不宜合成一个排名。（§4.2–4.3, pp.5–6）
- **设置**：GPT-2 teacher 为 6 层；student prototype pool 主设置 32、attention 中间维 64、8 heads；Adam $10^{-4}$、batch 32；单张 RTX 3090。（§4.2, p.5）

### 7.2 主要结果

- **UCR Table 3**：总 accuracy 0.820、AF1 0.858；最强对照 NCAD 为 0.663 / 0.767。作者据此报告平均 accuracy 提升 22.2%、AF1 提升 10.0%，并称总计检出 82% 的异常。总表中 PowerDemand AF1 为 .886，RESP 为 .736，说明提升并非对每个领域都同幅度。（§4.3, Table 3, PDF p.6）
- **SMD / MSL / SMAP / PSM Table 4**：adjusted F1 分别 .958 / .956 / .965 / .997，处于与当时方法可比的水平。作者称这些数据集包含较多明显异常；此表不等同 UCR 的 affiliation protocol。（§4.3, Table 4, p.6）
- **WaQ / SWAN Table 5**：ours F1 .620 / .804，对比 DCdetector .466 / .734。（Table 5, p.6）正文却有一句写成“62% vs 47% on GECCO”；表 5 实际列名是 WaQ，GECCO 出现在 Table 2 的数据集清单而非 Table 5 结果列。此处应记录为论文内部数据集名称不一致，不能照正文把分数归到 GECCO。（§4.3, Table 5, p.6）

### 7.3 消融与敏感性

- **Teacher 结构替换**：用 Informer / Reformer / Autoformer blocks 从头训练替代 GPT-2，F1 变化小于 2.6%，平均 AF1 73.6%；预训练 GPT-2 只微调 position embedding 和 LayerNorm 后，AF1 提高 12%（作者报告，Table/figure analysis, pp.6–7）。这支持其实现中预训练 teacher 有价值，但不隔离语言预训练知识与初始化 / 优化差异。（分析边界）
- **Student 结构**：TCN、TimesNet、TST 对照中，给 TST 加 prototype 后 AF1 提高 14.7%，支持显式常见形态记忆。（§4.4, p.6）
- **训练目标**：不增强的 NonAug 最差；去掉 teacher consistency 比 NonAug 提升 AF1 4.2%，但仍低于完整方法；加入额外 student consistency 使 AF1 下降 8.0%。（§4.4, Fig. 5, p.7）
- **敏感性**：window size 增大时 UCR accuracy 保持 72% 以上、AF1 80% 以上；warping 有益；GPT-2 至少 3 层后趋稳，projector 3 层最好。主设置 prototype pool 写 32，而敏感性分析说 48 最有用，两个配置口径不同，复现要以附录实现 / 配置为准。（§4.4, Fig. 4, pp.6–7）
- **少样本 / zero-shot case**：PowerDemand 全数据、50%、20%、10%、zero-shot 条件下 F1 为 .886 / .817 / .784 / .781 / .650。（Table 6, p.7）这是单个数据集案例，不足以单独支持跨场景普遍迁移结论。

## 8. Contributions and Reproduction Value

1. 将 teacher–student feature discrepancy 用于 TSAD，并把预训练 GPT-2 接到数值窗口 embedding 上。（§3）
2. 用每通道 prototype bank 为 student 提供正常形态参照。（§3.2）
3. 以局部 synthetic anomalies 同时监督 student–teacher 分离和 teacher 跨视图一致性。（§3.4）
4. 在 9 个 UCR 领域组和 6 个多变量数据集上评估，并提供结构替换、student 结构、损失和超参数分析。（§4）

训练硬件和部分超参数有说明，但会议论文 PDF 未给代码链接；复现需要补齐 split、窗口分数对时间戳的映射、threshold、prototype 初始化 / pool-size 口径以及扰动分布。无须把论文中的 few-shot / zero-shot 叙述当作部署验证。（§4）

## 9. Limitations and Critical Reading

- **[作者说明]** teacher 部署成本 / memory 较高，结论中提出研究轻量 teacher。（§5, p.8）
- **[实验支持]** synthetic anomaly 的结果依赖三类扰动代理；论文没有 workload / release / Trace 条件的合法波动与故障并发实验。（§3.4, §4）
- **[分析推断]** prototype 是时间形态参照，能覆盖常见局部形状但没有语义化的多运行状态标签；发生未见但合法的状态切换时，差距仍可能升高。
- **[实验口径]** UCR 的 domain accuracy、affiliation event metrics 与其他表的 adjusted F1 不同；UCR 单域 9 组总均值不能证明跨组织真实迁移。（Tables 3–5）
- **[复现风险]** 文中主设置 32 prototypes 与敏感性结论 48 prototypes 不一致；WaQ / GECCO 的一句文字也与 Table 5 结果列不一致。（§4.2–4.4）
- **[分析推断]** 表示差距只能提供“未被 student 模仿”的异常证据，不解释异常来自业务事件、状态切换、传感器故障还是负载冲击。

## 10. Related Papers

- **Delving into LLMs for TSAD**：同属 LLM TSAD，但采用无训练的 de-seasonalization + index-aware prompting，重点解决理解与定位失败；AnomalyLLM 把 LLM 作为表示 teacher，并训练 student。
- **AnomSeer**：视觉 MLLM 通过 ExpCoT + TimerPO 做 post-training，强调统计证据与可读解释；AnomalyLLM 不输出自然语言解释，而用 embedding discrepancy 检测。
- **TSB-AD / Quo Vadis**：帮助解释异常评分、affiliation、point-adjusted F1 与阈值的比较边界。
- **CAROTS / MACE / When Model Meets New Normals**：分别从因果保持增强、多模态态频谱模式、测试时状态适应角度建模正常变化；prototype pool 是另一种常见形态参照，但不做状态语义辨识。

## 11. Questions for Further Reading

1. 多种合法 workload / release 状态下 prototype 如何覆盖并及时更新？如何防止测试期故障进入原型？
2. 对比 prototype 距离与 teacher–student discrepancy，哪一个贡献了多少召回收益？阈值如何在 validation-only / 固定告警预算下设定？
3. jittering、scaling、warping 的强度和片段长度如何映射到真实故障类型？合法大幅波动会否被当成 synthetic negative 同类？
4. 若正常状态切换与故障同时发生，teacher 与 prototypes 哪一方提供证据，分数可否解释来源？
5. 统一 prototype 数 32 / 48、数据划分和输出窗口到 timestamp 的实现后，少样本优势是否仍成立？

## 12. Key Terms

- **Knowledge distillation TSAD**：让 student 拟合 teacher 的时序表示，以双方输出差距作为异常证据。
- **Prototype pool**：每个变量的一组可学习典型窗口形态。
- **Teacher consistency loss**：令 teacher 对原始和合成扰动视图的 embedding 接近。
- **Affiliation metrics**：对预测事件与真实事件空间关系计算的事件级 precision / recall / F1。

## 13. Tags

`TSAD` `LLM teacher` `knowledge distillation` `prototype` `synthetic anomalies` `few-shot` `affiliation metric`
