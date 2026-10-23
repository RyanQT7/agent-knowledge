# Knowledge Dossier — KAN-AD: Time Series Anomaly Detection with Kolmogorov–Arnold Networks

## 1. Basic Information

- **English title**: KAN-AD: Time Series Anomaly Detection with Kolmogorov–Arnold Networks
- **中文译名**：KAN-AD：基于 Kolmogorov–Arnold 网络的时间序列异常检测
- **Authors**: Quan Zhou et al.
- **Venue / year / CCF**: ICML 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf](../../sources/papers/tsad-2024-2026/2025/ICML/KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/CSTCloudOps/KAN-AD
- **Research area**: 平滑 Fourier-KAN 预测式单变量异常检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 以单变量下一点预测做 TSAD，重点处理训练 / 测试序列中的局部扰动及训练污染。（§§1–3, pp.1–5）
- **[实验支持]** KPI、TODS、WSD、UCR 四个单变量 benchmark；另用五个 MTS 数据集作通道独立扩展。（§4.1, Appendix A.3）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文关注单变量时间序列异常检测，主要通过下一时刻预测值与真实观测的偏离发现异常。作者观察到，预测模型在训练数据含局部尖峰、跌落或异常点时，可能把这些局部变化也学成可预测规律，导致异常信号被拟合掉；直接将 KAN 用于该任务时，B-spline 局部支撑使函数对局部观测扰动敏感。（§1, Fig. 1–2, pp.1–2）

作者把“正常”具体操作化为时间上的平滑函数行为。这个表述是归纳偏置，不是业务语义定义：模型不判断峰值来自促销、发布或故障，只判断它能否由训练出的平滑 / 周期模式预测。（§1–3, pp.1–4；后句为分析推断）

## 4. Core Challenges

#### 精读笔记原章节：4. 核心挑战与既有方法不足

1. **局部扰动污染拟合**：常规预测网络可能对局部尖峰和跌落过拟合；异常训练污染也会使模型将异常作为可预测行为。（§1, Fig. 1–2）
2. **KAN 的局部基函数**：B-spline 的局部支撑便于表达，但会将窗口内局部噪声直接带入拟合；作者以此解释普通 KAN 不如其改造版本稳健。（§2–3.1）
3. **平滑性与细节的折衷**：有限 Fourier 展开舍弃高频残差，能抑制局部扰动，但也可能损失短暂、低幅且确实重要的真实异常。这是由模型结构推导出的风险，论文未给出业务语义验证。（分析推断）
4. **周期信息与局部趋势混杂**：同一局部片段的常值偏置会影响函数映射，且微弱但重复的周期规律不一定能由原始值显式表示；方法分别用常数项消除和索引周期编码处理。（§3.1–3.2, Eqs. 3–5）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：4. 核心挑战与既有方法不足

1. **局部扰动污染拟合**：常规预测网络可能对局部尖峰和跌落过拟合；异常训练污染也会使模型将异常作为可预测行为。（§1, Fig. 1–2）
2. **KAN 的局部基函数**：B-spline 的局部支撑便于表达，但会将窗口内局部噪声直接带入拟合；作者以此解释普通 KAN 不如其改造版本稳健。（§2–3.1）
3. **平滑性与细节的折衷**：有限 Fourier 展开舍弃高频残差，能抑制局部扰动，但也可能损失短暂、低幅且确实重要的真实异常。这是由模型结构推导出的风险，论文未给出业务语义验证。（分析推断）
4. **周期信息与局部趋势混杂**：同一局部片段的常值偏置会影响函数映射，且微弱但重复的周期规律不一定能由原始值显式表示；方法分别用常数项消除和索引周期编码处理。（§3.1–3.2, Eqs. 3–5）

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. 一句话总结

KAN-AD 把单变量序列预测改写为平滑函数拟合，用有限 Fourier 基替换 KAN 的局部 B-spline，再以原始序列、频率项和周期位置编码经轻量卷积抽取全局正常模式，最后做一步预测；论文的核心判断是平滑拟合对局部噪声和训练污染更稳。（§§2–3.4, Eqs. 1–12, pp.2–5）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：局部扰动污染拟合：常规预测网络可能对局部尖峰和跌落过拟合；异常训练污染也会使模型将异常作为可预测行为。（§1, Fig. 1–2）
- **C2（第4节挑战）**：KAN 的局部基函数：B-spline 的局部支撑便于表达，但会将窗口内局部噪声直接带入拟合；作者以此解释普通 KAN 不如其改造版本稳健。（§2–3.1）
- **C3（第4节挑战）**：平滑性与细节的折衷：有限 Fourier 展开舍弃高频残差，能抑制局部扰动，但也可能损失短暂、低幅且确实重要的真实异常。这是由模型结构推导出的风险，论文未给出业务语义验证。（分析推断）
- **C4（第4节挑战）**：周期信息与局部趋势混杂：同一局部片段的常值偏置会影响函数映射，且微弱但重复的周期规律不一定能由原始值显式表示；方法分别用常数项消除和索引周期编码处理。（§3.1–3.2, Eqs. 3–5）

### 7.1 Fourier-KAN

- **作者技术描述**：**[作者主张] Fourier-KAN**：有限 sin/cos 基替代 B-spline，有限阶表示抑制局部高频扰动。（§3.1, Eqs. 3–4）
- **对应挑战**：C3、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 CTE 与周期编码

- **作者技术描述**：**[作者主张] CTE 与周期编码**：一阶差分 / 消常数项减轻局部偏置，索引 sin/cos 编码加入相位信息。（§3.2, Eqs. 3–5）
- **对应挑战**：C4、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Mapping：常数项消除与周期位置编码”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** CTE、Fourier 族与组合编码有消融；TODS 合成训练污染比例 10–40% 下表现相对稳。（§4.4, Figs. 4–7）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Reducing

- **作者技术描述**：**[作者主张] Reducing**：Conv-BN-GELU 堆叠、残差与 1 宽度 DownConv 汇总函数特征。（§3.3, Eqs. 6–11）
- **对应挑战**：C4、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 Reducing：卷积汇总函数族”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Projection

- **作者技术描述**：**[作者主张] Projection**：线性预测下一点。（§3.4, Eq. 12）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 Projection：一步预测与训练”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. 算法总览

```text
历史窗口 x[0:i]
  ├─ 映射 Mapping：有限 Fourier 展开近似平滑函数；一阶差分消除局部常值 / 趋势项
  ├─ 周期增强：加入 sin/cos 的时间索引编码
  ├─ 降维 Reducing：堆叠轻量 1D CNN 汇总原始值、函数基和周期编码
  └─ 投影 Projection：线性映射出下一时刻预测 x[i+1]
异常判断：预测误差用于区分正常与异常（论文未在主文明确给出统一的最终 score 方程）
```

论文把 Mapping、Reducing、Projection 称为三阶段（§3.1, Fig. 3, pp.3–5）。预测任务使用历史窗口，每条时间序列单独训练；多变量扩展则将各通道拆成独立单变量输入，未建模通道间关系（§4.1, Appendix A.3）。

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. 方法细节

#### 6.1 从 KAN 到有限 Fourier 平滑函数

KAN 将多层映射写为若干一元函数的组合（Eq. 1）；原始 KAN 以 B-spline 参数化这些一元函数（Eq. 2）。KAN-AD 用有限 Fourier 截断近似每个窗口上的平滑映射：

$$f(x_{0:i})=A_0+\sum_{n=1}^{N}\{A_n\cos(n x_{0:i})+B_n\sin(n x_{0:i})\}+\epsilon. \tag{3}$$

这里 $A_n,B_n$ 是待学习系数，$N$ 控制函数复杂度；截断后未显式表示的高频项落入残差 $\epsilon$。作者将这一点解释为忽略局部扰动、聚焦全局模式。写成矩阵形式，令 $H$ 为按阶数堆叠的 sin/cos 基、$\Theta$ 为系数，则 $x'=A_0+\Theta H$（Eq. 4）。与每个局部 knot 自由拟合相比，有限基给表示施加全局平滑约束。（§3.1, Eqs. 1–4, pp.3–4）

#### 6.2 Mapping：常数项消除与周期位置编码

仅用原始值构建 Fourier 映射时，局部窗口均值 / 趋势可能占用函数系数，使映射对偏移敏感。Constant Term Elimination（CTE）用一阶差分 $\Delta x_t=x_t-x_{t-1}$ 及重归一化表达变化，并消除 Fourier 表达中的常数项 $A_0$；该操作旨在减少局部均值偏差，不能理解为识别并解释趋势来源。（§3.2, Eqs. 3–4, p.4；附录 A.4.1）

作者还为窗口位置 $i$ 和周期长度 $T$ 构造正余弦索引项 $P_n=\{\sin(2\pi n i/T),\cos(2\pi n i/T)\}$，与原始序列 $X$、Fourier 映射 $S_n$ 一起堆叠成 $H_0=\mathrm{Stack}(X,S_1,P_1,\ldots,S_N,P_N)$（Eq. 5）。原始值保留幅值信息，$S_n$ 表示平滑函数族，$P_n$ 显式提供周期相位 / 序号信息。（§3.2, Eq. 5, p.4）

#### 6.3 Reducing：卷积汇总函数族

$H_0$ 输入多层 1D CNN，卷积核大小为 3；每层使用 Conv、BatchNorm、GELU（Eqs. 6–9）。网络将原始局部观察、多个 Fourier 阶和周期编码压缩为低维隐表示。作者加入从输入到末层的残差 $H^{(L)'}=H^{(L)}+H^{(0)}$（Eq. 10），使输出仍保留初始信息；随后用宽度为 1 的 DownConv 聚合通道得到近似正常模式 $x'$（Eq. 11）。这一步学习各函数特征的组合权重，并非逐个选择单一周期。（§3.3, Eqs. 6–11, pp.4–5）

#### 6.4 Projection：一步预测与训练

最终用单层 MLP / 线性投影根据降低后的序列表示预测下一点：$\hat x_{i+1}=W x'_{0:i}+b$（Eq. 12, §3.4, p.5）。训练按窗口预测观测值；推理比较预测与实际观测以得到检测依据。**原文边界**：主文强调 forecasting-based anomaly detection，但未清楚定义一个可直接照抄的统一最终 anomaly-score 公式与 threshold calibration 流程；本笔记不自行指定绝对误差、平方误差或阈值作为论文定义。复现时应以官方实现为准，并记录其 score 与 calibration 细节。

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (4)、Eq. (5)、Eq. (6)、Eq. (10)、Eq. (11)、Eq. (12)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.4 Projection：一步预测与训练；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

KAN-AD 把单变量序列预测改写为平滑函数拟合，用有限 Fourier 基替换 KAN 的局部 B-spline，再以原始序列、频率项和周期位置编码经轻量卷积抽取全局正常模式，最后做一步预测；论文的核心判断是平滑拟合对局部噪声和训练污染更稳。（§§2–3.4, Eqs. 1–12, pp.2–5）

## 9. Experimental Evidence

#### 精读笔记原章节：7. 实验设计与证据

#### 7.1 数据、比较方法与指标

单变量数据集为 KPI、TODS、WSD、UCR。各集合训练异常率分别为 2.70%、5.32%、2.43%、0%；WSD / KPI 具有较强周期性，UCR 同时包含多种序列形态与较长异常区间（§4.1, Table 1, pp.5–6）。KPI、TODS、WSD 按 4:1:5 划分训练 / 验证 / 测试；UCR 从训练部分抽 20% 作验证。每个序列单独训练，batch size 1024、learning rate 0.01、最多 100 epochs，报告五个随机种子均值和标准差（§4.1.2, p.6）。

比较对象含常见深度预测与 KAN 类方法，包括 TimesNet、LSTMAD、FCVAE、KAN 等（完整清单见 §4.1.3 / Appendix B）。指标包括阈值搜索得到的 Best F1、Event F1、delay=5 的 Delay F1 与 AUPRC；作者以 Event F1 为主指标，因为按异常事件计分可降低点级指标对异常区间长度的偏置（§4.1.4, pp.6–7）。Best F1 使用点调整，应与更严格的 event / delay / PR 指标区别看待。

#### 7.2 主结果与效率

Table 2 中 KAN-AD 四数据集平均 Event F1 为 0.7798，KAN 为 0.6835，LSTMAD 为 0.6808，FCVAE 为 0.6743；作者据此报告相对既有 SOTA 平均约 15% 提升，部分数据增益超过 27%（Table 2, pp.7–8）。结果支持该设置下平滑 Fourier 表示 + 轻量学习机制的有效性，不等于任意领域、固定运行阈值或在线流的性能保证。

Table 3 报告 KAN-AD 约 274 个可训练参数，少于 KAN 的约 1,360 个；UCR 上 CPU/GPU 总时间约 36/42 秒，KAN 为 34/66 秒。作者报告推理较原始 KAN 约快 50%；设备、批量与实现均影响此比较（§4.2, Table 3, p.8）。

#### 7.3 消融和鲁棒性

- **CTE**：在 KPI、TODS、UCR 上整体更有帮助，WSD 收益较弱，说明去偏差并非对每种周期 / 数据形态都同等重要（§4.4.1, Fig. 4）。
- **函数族**：Fourier 在 Taylor、Chebyshev 等替代族比较中稳定处于前两位；结合原始序列、Fourier 项和周期位置项优于只用单一特征（§4.4.2–4.4.3, Figs. 5–6）。
- **训练污染**：作者在合成的 TODS 样本中逐步提高训练异常率（10%–40%），KAN-AD 相对若干基线更稳；这是对选定数据生成方式的受控注入，不证明对任意污染机制或合法负载跃迁都稳健（§4.4.4, Fig. 7）。
- **多变量扩展**：在 SMD、MSL、SMAP、SWaT、PSM 上采用 channel-independent 方案，报告平均 Best F1 0.9076、参数约 4,491（Appendix A.3, Table 5）。该结果的指标和通道假设与单变量主表不同，不能直接拼表排名。

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

“局部扰动是应舍弃残差”的先验可能抑制短时真实异常；实验对局部异常的召回和业务来源没有单独控制。（分析推断）

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

合成污染实验覆盖有限生成设置；没有按 workload / release / 业务状态标签测试正常状态转换与故障并发。（§4.4.4；分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

主模型是单变量预测；通道独立的 MTS 扩展不使用变量关联，因此不能利用跨指标因果 / 相关异常证据。（Appendix A.3）

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

主文未明确最终 score 和校准公式，复现须先核实官方实现，避免把常见 forecast residual 当成原文定义。

#### 精读笔记原章节：8. 贡献、局限与复现价值 — 局限

Event F1、Best F1、AUPRC 反映不同决策协议，best threshold / 点调整数值不能直接解释成固定误报预算下的线上告警质量。（§4.1.4）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 在状态标注数据中分别注入合法负载波动、短故障、两者并发，检验平滑阶数 / CTE 对召回与误报的影响。
- **[分析推断]** 把周期性与业务日历、负载或发布上下文关联，并比较 channel-independent 与关系建模。
- **[分析推断]** 明确验证集校准、固定 FPR、事件延迟和跨序列泛化，并开源最终 score / threshold 细节。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **MACE**：同样以频率结构刻画多种正常模式；MACE 使用频域原型，KAN-AD 用 Fourier 函数族拟合平滑预测，二者都没有业务状态语义标签。
- **TFC**：加入时间、频率、曲率动态证据；相比之下 KAN-AD 用频率基增强一步预测，未显式融合曲率或跨变量关系。
- **When Model Meets New Normals**：针对新正常状态进行测试时适配；KAN-AD 的固定训练函数族没有在线状态更新机制。
- **CAPMix**：面向 KPI 噪声 / 动态环境的鲁棒检测；可与 KAN-AD 的平滑函数假设比较，但要统一数据、窗口和校准协议。
- **Quo Vadis / TSB-AD**：提醒比较需控制 benchmark、threshold、point adjustment 与事件级指标。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §1, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §§1–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §1, Fig. 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §2–3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.1–3.2, Eqs. 3–5 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.1, §4.1, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | Eq. 1, Eq. 2 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.1, Eq. 4, Eqs. 1–4 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.2, Eqs. 3–4 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.2, Eq. 5 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.3, Eqs. 6–9, Eq. 10, Eq. 11, Eqs. 6–11 | 精读笔记保留的原文定位 |
| Method / formulas | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §3.4, Eq. 12 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.1, §4.1.2, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.1.3, §4.1.4 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.2, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.4.1, Fig. 4 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.4.2–4.4.3 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.4.4, Fig. 7 | 精读笔记保留的原文定位 |
| Experimental evidence | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | Table 5 | 精读笔记保留的原文定位 |
| Limitations | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.4.4 | 精读笔记保留的原文定位 |
| Limitations | KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf | §4.1.4 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "kan-ad",
  "title_en": "KAN-AD: Time Series Anomaly Detection with Kolmogorov–Arnold Networks",
  "title_zh": "KAN-AD：基于 Kolmogorov–Arnold 网络的时间序列异常检测",
  "authors": [
    "Quan Zhou et al."
  ],
  "year": 2025,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/ICML/KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
  "reading_note_path": "papers/kan-ad/notes.md",
  "code_url": "https://github.com/CSTCloudOps/KAN-AD",
  "research_area": "平滑 Fourier-KAN 预测式单变量异常检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] 以单变量下一点预测做 TSAD，重点处理训练 / 测试序列中的局部扰动及训练污染。（§§1–3, pp.1–5） - [实验支持] KPI、TODS、WSD、UCR 四个单变量 benchmark；另用五个 MTS 数据集作通道独立扩展。（§4.1, Appendix A.3）",
  "research_problem": "论文关注单变量时间序列异常检测，主要通过下一时刻预测值与真实观测的偏离发现异常。作者观察到，预测模型在训练数据含局部尖峰、跌落或异常点时，可能把这些局部变化也学成可预测规律，导致异常信号被拟合掉；直接将 KAN 用于该任务时，B-spline 局部支撑使函数对局部观测扰动敏感。（§1, Fig. 1–2, pp.1–2） 作者把“正常”具体操作化为时间上的平滑函数行为。这个表述是归纳偏置，不是业务语义定义：模型不判断峰值来自促销、发布或故障，只判断它能否由训练出的平滑 / 周期模式预测。（§1–3, pp.1–4；后句为分析推断）",
  "core_challenges": [
    "局部扰动污染拟合：常规预测网络可能对局部尖峰和跌落过拟合；异常训练污染也会使模型将异常作为可预测行为。（§1, Fig. 1–2）",
    "KAN 的局部基函数：B-spline 的局部支撑便于表达，但会将窗口内局部噪声直接带入拟合；作者以此解释普通 KAN 不如其改造版本稳健。（§2–3.1）",
    "平滑性与细节的折衷：有限 Fourier 展开舍弃高频残差，能抑制局部扰动，但也可能损失短暂、低幅且确实重要的真实异常。这是由模型结构推导出的风险，论文未给出业务语义验证。（分析推断）",
    "周期信息与局部趋势混杂：同一局部片段的常值偏置会影响函数映射，且微弱但重复的周期规律不一定能由原始值显式表示；方法分别用常数项消除和索引周期编码处理。（§3.1–3.2, Eqs. 3–5）"
  ],
  "existing_method_limits": [
    "局部扰动污染拟合：常规预测网络可能对局部尖峰和跌落过拟合；异常训练污染也会使模型将异常作为可预测行为。（§1, Fig. 1–2）",
    "KAN 的局部基函数：B-spline 的局部支撑便于表达，但会将窗口内局部噪声直接带入拟合；作者以此解释普通 KAN 不如其改造版本稳健。（§2–3.1）",
    "平滑性与细节的折衷：有限 Fourier 展开舍弃高频残差，能抑制局部扰动，但也可能损失短暂、低幅且确实重要的真实异常。这是由模型结构推导出的风险，论文未给出业务语义验证。（分析推断）",
    "周期信息与局部趋势混杂：同一局部片段的常值偏置会影响函数映射，且微弱但重复的周期规律不一定能由原始值显式表示；方法分别用常数项消除和索引周期编码处理。（§3.1–3.2, Eqs. 3–5）"
  ],
  "core_idea": "KAN-AD 把单变量序列预测改写为平滑函数拟合，用有限 Fourier 基替换 KAN 的局部 B-spline，再以原始序列、频率项和周期位置编码经轻量卷积抽取全局正常模式，最后做一步预测；论文的核心判断是平滑拟合对局部噪声和训练污染更稳。（§§2–3.4, Eqs. 1–12, pp.2–5）",
  "technical_innovations": [
    {
      "name": "Fourier-KAN",
      "author_claim": "**[作者主张] Fourier-KAN**：有限 sin/cos 基替代 B-spline，有限阶表示抑制局部高频扰动。（§3.1, Eqs. 3–4）",
      "challenge_ids": [
        "C3",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Fourier-KAN**：有限 sin/cos 基替代 B-spline，有限阶表示抑制局部高频扰动。（§3.1, Eqs. 3–4）"
    },
    {
      "name": "CTE 与周期编码",
      "author_claim": "**[作者主张] CTE 与周期编码**：一阶差分 / 消常数项减轻局部偏置，索引 sin/cos 编码加入相位信息。（§3.2, Eqs. 3–5）",
      "challenge_ids": [
        "C4",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Mapping：常数项消除与周期位置编码",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** CTE、Fourier 族与组合编码有消融；TODS 合成训练污染比例 10–40% 下表现相对稳。（§4.4, Figs. 4–7）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] CTE 与周期编码**：一阶差分 / 消常数项减轻局部偏置，索引 sin/cos 编码加入相位信息。（§3.2, Eqs. 3–5）"
    },
    {
      "name": "Reducing",
      "author_claim": "**[作者主张] Reducing**：Conv-BN-GELU 堆叠、残差与 1 宽度 DownConv 汇总函数特征。（§3.3, Eqs. 6–11）",
      "challenge_ids": [
        "C4",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 Reducing：卷积汇总函数族",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Reducing**：Conv-BN-GELU 堆叠、残差与 1 宽度 DownConv 汇总函数特征。（§3.3, Eqs. 6–11）"
    },
    {
      "name": "Projection",
      "author_claim": "**[作者主张] Projection**：线性预测下一点。（§3.4, Eq. 12）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 Projection：一步预测与训练",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Projection**：线性预测下一点。（§3.4, Eq. 12）"
    }
  ],
  "methodology": {
    "architecture": "text 历史窗口 x[0:i] ├─ 映射 Mapping：有限 Fourier 展开近似平滑函数；一阶差分消除局部常值 / 趋势项 ├─ 周期增强：加入 sin/cos 的时间索引编码 ├─ 降维 Reducing：堆叠轻量 1D CNN 汇总原始值、函数基和周期编码 └─ 投影 Projection：线性映射出下一时刻预测 x[i+1] 异常判断：预测误差用于区分正常与异常（论文未在主文明确给出统一的最终 score 方程） 论文把 Mapping、Reducing、Projection 称为三阶段（§3.1, Fig. 3, pp.3–5）。预测任务使用历史窗口，每条时间序列单独训练；多变量扩展则将各通道拆成独立单变量输入，未建模通道间关系（§4.1, Appendix A.3）。",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 从 KAN 到有限 Fourier 平滑函数",
      "6.2 Mapping：常数项消除与周期位置编码",
      "6.3 Reducing：卷积汇总函数族",
      "6.4 Projection：一步预测与训练"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (5)",
      "Eq. (6)",
      "Eq. (10)",
      "Eq. (11)",
      "Eq. (12)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "KAN-AD 把单变量序列预测改写为平滑函数拟合，用有限 Fourier 基替换 KAN 的局部 B-spline，再以原始序列、频率项和周期位置编码经轻量卷积抽取全局正常模式，最后做一步预测；论文的核心判断是平滑拟合对局部噪声和训练污染更稳。（§§2–3.4, Eqs. 1–12, pp.2–5）"
  },
  "experimental_evidence": {
    "datasets": [
      "单变量数据集为 KPI、TODS、WSD、UCR。各集合训练异常率分别为 2.70%、5.32%、2.43%、0%；WSD / KPI 具有较强周期性，UCR 同时包含多种序列形态与较长异常区间（§4.1, Table 1, pp.5–6）。KPI、TODS、WSD 按 4:1:5 划分训练 / 验证 / 测试；UCR 从训练部分抽 20% 作验证。每个序列单独训练，batch size 1024、learning rate 0.01、最多 100 epochs，报告五个随机种子均值和标准差（§4.1.2, p.6）。",
      "Table 2 中 KAN-AD 四数据集平均 Event F1 为 0.7798，KAN 为 0.6835，LSTMAD 为 0.6808，FCVAE 为 0.6743；作者据此报告相对既有 SOTA 平均约 15% 提升，部分数据增益超过 27%（Table 2, pp.7–8）。结果支持该设置下平滑 Fourier 表示 + 轻量学习机制的有效性，不等于任意领域、固定运行阈值或在线流的性能保证。"
    ],
    "baselines": [
      "### 7.1 数据、比较方法与指标"
    ],
    "metrics": [
      "### 7.1 数据、比较方法与指标",
      "比较对象含常见深度预测与 KAN 类方法，包括 TimesNet、LSTMAD、FCVAE、KAN 等（完整清单见 §4.1.3 / Appendix B）。指标包括阈值搜索得到的 Best F1、Event F1、delay=5 的 Delay F1 与 AUPRC；作者以 Event F1 为主指标，因为按异常事件计分可降低点级指标对异常区间长度的偏置（§4.1.4, pp.6–7）。Best F1 使用点调整，应与更严格的 event / delay / PR 指标区别看待。",
      "Table 2 中 KAN-AD 四数据集平均 Event F1 为 0.7798，KAN 为 0.6835，LSTMAD 为 0.6808，FCVAE 为 0.6743；作者据此报告相对既有 SOTA 平均约 15% 提升，部分数据增益超过 27%（Table 2, pp.7–8）。结果支持该设置下平滑 Fourier 表示 + 轻量学习机制的有效性，不等于任意领域、固定运行阈值或在线流的性能保证。",
      "- CTE：在 KPI、TODS、UCR 上整体更有帮助，WSD 收益较弱，说明去偏差并非对每种周期 / 数据形态都同等重要（§4.4.1, Fig. 4）。 - 函数族：Fourier 在 Taylor、Chebyshev 等替代族比较中稳定处于前两位；结合原始序列、Fourier 项和周期位置项优于只用单一特征（§4.4.2–4.4.3, Figs. 5–6）。 - 训练污染：作者在合成的 TODS 样本中逐步提高训练异常率（10%–40%），KAN-AD 相对若干基线更稳；这是对选定数据生成方式的受控注入，不证明对任意污染机制或合法负载跃迁都稳健（§4.4.4, Fig. 7）。…"
    ],
    "main_results": [
      "单变量数据集为 KPI、TODS、WSD、UCR。各集合训练异常率分别为 2.70%、5.32%、2.43%、0%；WSD / KPI 具有较强周期性，UCR 同时包含多种序列形态与较长异常区间（§4.1, Table 1, pp.5–6）。KPI、TODS、WSD 按 4:1:5 划分训练 / 验证 / 测试；UCR 从训练部分抽 20% 作验证。每个序列单独训练，batch size 1024、learning rate 0.01、最多 100 epochs，报告五个随机种子均值和标准差（§4.1.2, p.6）。",
      "### 7.2 主结果与效率",
      "Table 2 中 KAN-AD 四数据集平均 Event F1 为 0.7798，KAN 为 0.6835，LSTMAD 为 0.6808，FCVAE 为 0.6743；作者据此报告相对既有 SOTA 平均约 15% 提升，部分数据增益超过 27%（Table 2, pp.7–8）。结果支持该设置下平滑 Fourier 表示 + 轻量学习机制的有效性，不等于任意领域、固定运行阈值或在线流的性能保证。",
      "Table 3 报告 KAN-AD 约 274 个可训练参数，少于 KAN 的约 1,360 个；UCR 上 CPU/GPU 总时间约 36/42 秒，KAN 为 34/66 秒。作者报告推理较原始 KAN 约快 50%；设备、批量与实现均影响此比较（§4.2, Table 3, p.8）。",
      "- CTE：在 KPI、TODS、UCR 上整体更有帮助，WSD 收益较弱，说明去偏差并非对每种周期 / 数据形态都同等重要（§4.4.1, Fig. 4）。 - 函数族：Fourier 在 Taylor、Chebyshev 等替代族比较中稳定处于前两位；结合原始序列、Fourier 项和周期位置项优于只用单一特征（§4.4.2–4.4.3, Figs. 5–6）。 - 训练污染：作者在合成的 TODS 样本中逐步提高训练异常率（10%–40%），KAN-AD 相对若干基线更稳；这是对选定数据生成方式的受控注入，不证明对任意污染机制或合法负载跃迁都稳健（§4.4.4, Fig. 7）。 - 多变量扩展：在 SMD、MSL、SMAP、SWaT、PSM 上采用 channel-independent 方案，…"
    ],
    "ablations": [
      "### 7.3 消融和鲁棒性"
    ],
    "robustness_generalization": [
      "### 7.2 主结果与效率",
      "### 7.3 消融和鲁棒性",
      "- CTE：在 KPI、TODS、UCR 上整体更有帮助，WSD 收益较弱，说明去偏差并非对每种周期 / 数据形态都同等重要（§4.4.1, Fig. 4）。 - 函数族：Fourier 在 Taylor、Chebyshev 等替代族比较中稳定处于前两位；结合原始序列、Fourier 项和周期位置项优于只用单一特征（§4.4.2–4.4.3, Figs. 5–6）。 - 训练污染：作者在合成的 TODS 样本中逐步提高训练异常率（10%–40%），KAN-AD 相对若干基线更稳；这是对选定数据生成方式的受控注入，不证明对任意污染机制或合法负载跃迁都稳健（§4.4.4, Fig. 7）。…"
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
      "“局部扰动是应舍弃残差”的先验可能抑制短时真实异常；实验对局部异常的召回和业务来源没有单独控制。（分析推断）",
      "合成污染实验覆盖有限生成设置；没有按 workload / release / 业务状态标签测试正常状态转换与故障并发。（§4.4.4；分析推断）"
    ],
    "evidence_gaps": [
      "主模型是单变量预测；通道独立的 MTS 扩展不使用变量关联，因此不能利用跨指标因果 / 相关异常证据。（Appendix A.3）",
      "主文未明确最终 score 和校准公式，复现须先核实官方实现，避免把常见 forecast residual 当成原文定义。",
      "Event F1、Best F1、AUPRC 反映不同决策协议，best threshold / 点调整数值不能直接解释成固定误报预算下的线上告警质量。（§4.1.4）"
    ]
  },
  "research_implications": [
    "- [分析推断] 在状态标注数据中分别注入合法负载波动、短故障、两者并发，检验平滑阶数 / CTE 对召回与误报的影响。 - [分析推断] 把周期性与业务日历、负载或发布上下文关联，并比较 channel-independent 与关系建模。 - [分析推断] 明确验证集校准、固定 FPR、事件延迟和跨序列泛化，并开源最终 score / threshold 细节。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfc",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
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
      "paper_id": "kan-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§§1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§4.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§2–3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§3.1–3.2, Eqs. 3–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§3.1, §4.1, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "Eq. 1, Eq. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§3.1, Eq. 4, Eqs. 1–4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§3.2, Eqs. 3–4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KAN_AD_Time_Series_Anomaly_Detection_with_KolmogorovArnold_Networks.pdf",
      "locator": "§3.2, Eq. 5",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "167a26f478e73acda64ac8edbecb9b8b04bb1180eac454d199c19ff7465f9508",
    "reading_note_sha256": "757542fae867f6b69c7451006f457fd029afa8467f8dfa9ad66e381225d3de1c",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "38c4c4651419313e811c363b0baaab239eaeffe802113b5dd9430e438d21f200"
  },
  "knowledge_card_path": "papers/kan-ad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
