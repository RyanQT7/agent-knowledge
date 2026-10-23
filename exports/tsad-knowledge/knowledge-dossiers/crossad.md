# Knowledge Dossier — CrossAD: Time Series Anomaly Detection with Cross-scale Associations and Cross-window Modeling

## 1. Basic Information

- **English title**: CrossAD: Time Series Anomaly Detection with Cross-scale Associations and Cross-window Modeling
- **中文译名**：跨尺度关联与跨窗口建模的时间序列异常检测
- **Authors**: Beibu Li, Qichao Shentu（共同一作）, Yang Shu, Hui Zhang, Ming Li, Ning Jin, Bin Yang, Chenjuan Guo
- **Venue / year / CCF**: NeurIPS 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/decisionintelligence/CrossAD
- **Research area**: 无监督多变量异常检测与跨尺度/跨窗口建模
- **Method tags**: TSAD multivariate-time-series multi-scale cross-scale-reconstruction cross-window-context prototype sub-series-query reconstruction VUS-PR NeurIPS-2025

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督多变量时间序列异常检测，目标是在多种时间分辨率下检测点异常和子序列异常。（PDF pp.1–4, §§1, 3）
- **[实验支持]** SMD、MSL、SMAP、SWaT、PSM、GECCO、SWAN 七个测试集；另有 UCR 250 子集和 TSB-AD 补充基准。（PDF pp.7–9, 21, 24–25）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

论文研究无监督多变量时序异常检测：给定训练序列，测试时为未知序列的每个时间点产生异常分数 / 标签。异常的时长和形态不一：细粒度适合发现单点尖峰，粗粒度更容易呈现一段子序列的整体异常。已有多尺度路线往往独立编码各尺度或在特征层简单融合，未直接学习尺度之间的映射；同时常以固定长度窗口切分序列，使窗口只能访问局部数据。（PDF pp.1–3, §§1–2）

作者的关键假设是：训练正常序列中存在稳定的粗到细映射。正常时，较粗的整体趋势和上下文足以重建相应的细节；异常发生后，局部和整体变化对各尺度的影响不同，原有映射被破坏，因此细尺度重构误差上升。第二个假设是，不同窗口里会反复出现上下文相似的子序列，可通过共享的子序列表示和全局原型提供窗口外信息。（PDF pp.2–6, Fig. 1, §§3.1–3.3）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 多尺度方法常分别建模或简单融合，不显式学习粗粒度到细粒度的正常映射；固定滑窗限制窗口外上下文。（PDF pp.2–3, Fig. 1）
- **[作者假设]** 正常期的跨尺度映射可从训练序列学习，异常会因各尺度敏感性不同而破坏这种映射。（PDF pp.4–5, §3.2）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 独立尺度建模、特征融合与局部滑窗使已有模型难以捕捉跨尺度关联和窗口间共享上下文。（PDF pp.2–3）
- **[分析推断]** 原型上下文记住重复子序列的统计相似性，不自动提供模式含义，也不区分高负载业务波动和故障。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：4. Core Idea and Architecture

```text
多变量序列 → 平均池化生成多分辨率序列 → patch embedding + positional encoding
          → 分尺度编码（Scale-Independent Mask）
          → 对齐尺度表示 → 以更粗尺度重建细尺度（Cross-scale Mask）
          ↘ 周期感知 Router 选择 learnable sub-series queries
             → 对当前窗口多尺度表示 cross-attention 得到子序列表示
             → 分配并 EMA 更新全局多尺度原型
          → Decoder cross-attend 全局原型并重建各尺度
          → 各尺度平方误差插值回原时间轴并平均 → SPOT 阈值
```

整体采用 channel-independent 处理。每个窗口先经过多尺度重构主干；跨窗口模块则从该窗口的多尺度编码中抽取代表性子序列，将相似模式累积为全局多尺度上下文，并在解码重构时将上下文提供给当前尺度。（PDF pp.3–6, Fig. 2, §§3.1–3.3）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 多尺度方法常分别建模或简单融合，不显式学习粗粒度到细粒度的正常映射；固定滑窗限制窗口外上下文。（PDF pp.2–3, Fig. 1）
- **C2（第4节挑战）**：[作者假设] 正常期的跨尺度映射可从训练序列学习，异常会因各尺度敏感性不同而破坏这种映射。（PDF pp.4–5, §3.2）

### 7.1 Cross-scale reconstruction

- **作者技术描述**：**Cross-scale reconstruction**：目标为所有尺度的平方重构误差和；用更粗尺度条件预测更细尺度。（Eq. 1, Eqs. 4–6）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.2 Cross-scale decoder：以粗尺度为条件重建细尺度”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** 消融平均 VUS-PR：单尺度 0.3665，多尺度 0.3962，加跨尺度重构 0.4326，加由 encoder 表示更新的上下文 0.4597，完整模型 0.4984。（PDF p.9, Table 3）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Scale-Independent Mask

- **作者技术描述**：**Scale-Independent Mask**：encoder 的 attention mask 为块对角矩阵，只允许同一尺度内部注意力。（PDF p.5, Eqs. 2–3）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Cross-scale Mask decoder

- **作者技术描述**：**Cross-scale Mask decoder**：尺度对齐后按粗到细关系解码，避免将跨尺度关系留给隐式 feature fusion。（PDF pp.5–6, Fig. 2, Eqs. 4–6）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.2 Cross-scale decoder：以粗尺度为条件重建细尺度”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Period-aware query router

- **作者技术描述**：**Period-aware query router**：保留 Fourier 幅度 top-k 成分，逆变换后经 MLP 和 Gumbel-Softmax 激活 learnable sub-series queries。（PDF pp.6–7, Eqs. 7–9）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.3 Period-aware Router、子序列查询与全局原型”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.5 Global multi-scale prototypes

- **作者技术描述**：**Global multi-scale prototypes**：将窗口表示分配到最近欧氏距离原型并用 EMA 更新，作为 decoder 全局上下文。（PDF p.7, Eqs. 10–11; Appendix A）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**证据边界**：全局上下文在训练期持续更新会增加训练成本。（PDF p.10, §4.3）

### 7.6 Multi-scale score fusion

- **作者技术描述**：**Multi-scale score fusion**：每个尺度的平方残差插值回原时间轴并取平均；采用 SPOT 阈值。（PDF p.7, §3.4, Eq. 12）
- **对应挑战**：C1、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. Core Idea and Architecture

```text
多变量序列 → 平均池化生成多分辨率序列 → patch embedding + positional encoding
          → 分尺度编码（Scale-Independent Mask）
          → 对齐尺度表示 → 以更粗尺度重建细尺度（Cross-scale Mask）
          ↘ 周期感知 Router 选择 learnable sub-series queries
             → 对当前窗口多尺度表示 cross-attention 得到子序列表示
             → 分配并 EMA 更新全局多尺度原型
          → Decoder cross-attend 全局原型并重建各尺度
          → 各尺度平方误差插值回原时间轴并平均 → SPOT 阈值
```

整体采用 channel-independent 处理。每个窗口先经过多尺度重构主干；跨窗口模块则从该窗口的多尺度编码中抽取代表性子序列，将相似模式累积为全局多尺度上下文，并在解码重构时将上下文提供给当前尺度。（PDF pp.3–6, Fig. 2, §§3.1–3.3）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. Method in Detail

#### 5.1 多尺度生成与尺度内编码

原序列记为 $X^m$，经不同核宽的平均池化形成从粗到细的 $X^0,\ldots,X^{m-1}$。各尺度分别切 patch，经 MLP 映射到统一隐藏维度并加入位置编码，随后拼接为总长度 $P=\sum_i P_i$ 的表示。论文把多尺度目标写为：

$$
\theta^*=\arg\min_\theta\sum_i\left\|X^i-\hat X^i\right\|_2^2,
\qquad \hat X^i=f(\{X^0,\ldots,X^{i-1}\};\theta).
\tag{1}
$$

这里的核心是每个尺度的重构条件由更粗尺度表示构成；异常分数来自尺度映射失败，而不是只看各尺度独立自编码误差。原文的尺度上下标说明略紧凑，阅读时宜按“粗到细”文字和 Fig. 2 理解。（PDF pp.4–5, §3.2, Eq. 1）

尺度内 Transformer 使用 mask attention：

$$\operatorname{MaskAttn}(Q,K,V,M)=\operatorname{softmax}\!\left(\frac{(QW_q)(KW_k)^\top}{\sqrt d}+M\right)(VW_v).\tag{2}$$

Scale-Independent Mask $M^1$ 是块对角矩阵：不同尺度之间的注意力设为 $-\infty$，同一尺度块设为 0。因而 encoder 在每个尺度内学习时间依赖，但不会在这一步提前混合尺度。每层以残差、LayerNorm 和 FeedForward 更新表示（Eq. 3）。（PDF p.5, §3.2, Eqs. 2–3, Fig. 2②）

#### 5.2 Cross-scale decoder：以粗尺度为条件重建细尺度

Encoder 输出各尺度的 patch 表示后，先插值到相邻细尺度所需长度（Eq. 4）。Decoder 的 Cross-scale Mask $M^2$ 屏蔽不允许的细尺度到粗尺度访问，使某个目标尺度的重建只条件化于更粗的尺度表示。论文把该注意力层与全局上下文 cross-attention、前馈层串联：

$$\tilde Z^l=\operatorname{LN}(Z^{l-1}+\operatorname{MaskAttn}(Z^{l-1},Z^{l-1},Z^{l-1},M^2)),\tag{5}$$
$$\hat Z^l=\operatorname{LN}(\tilde Z^l+\operatorname{Attention}(\tilde Z^l,G',G')),\quad Z^l=\operatorname{LN}(\hat Z^l+\operatorname{FFN}(\hat Z^l)).\tag{6}$$

最后线性映射回原输入空间，得到每尺度的 $\hat X^i$。其作用不是把尺度差异直接当成异常，而是让模型拟合正常期的尺度间映射，再把映射被破坏的程度变成重构误差。（PDF pp.5–6, §3.2, Eqs. 4–6）

#### 5.3 Period-aware Router、子序列查询与全局原型

固定窗口缺少窗口外上下文。作者维护可学习查询库 $Q=\{q^1,\ldots,q^n\}$，每个查询是长度 $S$、维数 $d$ 的子序列表示。Period-aware Router 对当前窗口做 Fourier transform，保留幅度最大的 $k$ 个频率分量并逆变换以滤除较弱频率；重构时保留相位 $\Phi$：

$$X^t_{period}=\mathcal F^{-1}(A^t_{top-k},\Phi).\tag{7}$$

将 $X^t_{period}$ 输入 MLP 得到路由向量 $u\in\mathbb R^n$，以带独立 Gumbel 噪声和温度 $\tau$ 的 Gumbel-Softmax 对查询加权 / 选择（Eq. 8）。选出的当前窗口查询 $q^t$ 对 encoder 的多尺度表示 $H^{L,t}$ 做 cross-attention：

$$R^t=\operatorname{CrossAttention}(q^t,H^{L,t},H^{L,t}).\tag{9}$$

$R^t$ 被送到 $K$ 个全局原型 $G=\{g_1,\ldots,g_K\}$ 中，以欧氏距离选最近原型，并用 EMA 更新：

$$d_i^t=\operatorname{distance}(R^t,g_i),\quad j=\arg\min_i d_i^t,\quad g_j\leftarrow \alpha g_j+(1-\alpha)R^t.\tag{10–11}$$

拼接原型成为 $G'$，供 Eq. (6) decoder cross-attention 使用。作者将此称为跨窗口全局上下文共享：学习的查询从当前窗口提取可复用的多尺度子序列表示，原型把不同窗口的相似表示聚在一起。（PDF pp.6–7, §3.3, Eqs. 7–11）

正文说在训练期间持续更新上下文；附录 Algorithm 1 写作“for each new window”，使用 $\alpha=0.95$。这段伪代码没有明确说明测试推理时是否也更新原型，故不把它记成已证实的测试时自适应机制。原型也没有业务状态标签，不能直接解释某个模式对应高峰、发布或扩容。（PDF p.7, §3.3; PDF p.21, Appendix A）

#### 5.4 目标函数、异常分数与阈值

论文的训练目标为 Eq. (1) 各尺度重构平方误差之和，没有分类标签损失或对比损失。测试时，对各尺度误差进行插值，恢复到原序列长度并取平均：

$$\operatorname{AnomalyScore}(X^m)=\frac1m\sum_i\operatorname{interpolate}\!\left((X^i-f(\{X^0,\ldots,X^{i-1}\};\theta))^2\right).\tag{12}$$

分数超过 SPOT 自动阈值 $\delta$ 的点被标为异常。由此，CrossAD 输出的是与尺度重构不一致相联系的分数；公式本身不提供故障类型或业务原因。（PDF p.7, §3.4, Eq. 12）

#### 5.5 训练与复现要点

附录配置：hidden dimension 128、attention dimension 32、4 heads、dropout 0.1、encoder/decoder 各 2 层、默认 5 个子序列查询、32 个上下文原型；按数据集使用非重叠滑窗；平均池化核从 $\{32,16,8,4,2\}$ 中选择；Adam、初始学习率 $10^{-4}$、batch size 128，推理时不 drop-last；用 PyTorch 和 NVIDIA A800-80GB。统计表给出各数据集窗口长度（96–192，UCR 不使用窗口）。（PDF p.21, Appendices B–C, Table 5）

论文主要是训练正常序列的无监督重构路线；没有使用告警根因标签训练。模型的超参数敏感性分析覆盖 patch size、window size、hidden size、尺度数、查询数与原型数；UCR 额外采用“排名靠前的分数是否击中标注异常区间”的定位式评估，和常规逐点异常分类指标不是同一个评估协议。（PDF pp.22–24, Appendix D–E.4）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (4)、Eq. (6)、Eq. (7)、Eq. (8)、Eq. (12)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：5.5 训练与复现要点；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.4 目标函数、异常分数与阈值及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

CrossAD 不把不同分辨率的序列分开重构或简单融合，而是学习“粗尺度能否按正常映射重建细尺度”；再用周期感知查询和跨窗口原型上下文共享相似子序列模式，以多尺度重构误差作为逐点异常分数。

## 9. Experimental Evidence

#### 精读笔记原章节：6. Experiments

#### 6.1 数据、Baseline 与指标

主实验用七个真实数据集 / 子集：SMD（服务器，38维）、MSL（航天器，保留第一个连续维度）、SMAP（同样仅保留第一个连续维度）、SWaT（水处理，31维）、PSM（eBay 服务器，25维）、NeurIPS-TS 的 GECCO（水处理，9维）及 SWAN（Space Weather，38维）。窗口长度分别为 96、128 或 192，训练/验证/测试拆分和异常率见 Appendix B Table 5。补充实验包括 UCR 250 个子数据集以及 TSB-AD-U / TSB-AD-M 40 数据集基准。（PDF pp.7–8, §4.1; pp.21, 24–25, Tables 5, 10）

18 个 baseline 覆盖 OCSVM、PCA、IForest、LODA、HBOS、LOF、AE、DAGMM、LSTM、CAE-Ensemble、OmniAnomaly、Anomaly Transformer、DCdetector、ModernTCN、GPT4TS、MtsCID、TimeMixer、TimesNet。主表重点报告 VUS-ROC / VUS-PR，并补充 AUC-ROC/PR、Standard-F1、Affiliation-F1 和 Range-AUC-ROC/PR；阈值由 SPOT 选取。作者指出 point adjustment 可能导致不公平或虚高，因此采用多种事件 / 阈值敏感指标。（PDF pp.7–9, §4.1, Tables 1–2; Appendix E.1）

#### 6.2 主结果与证据边界

Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。（PDF pp.8–9, Table 1）

Table 2 对 ModernTCN、TimeMixer、TimesNet 做多指标比较。在 SMD、PSM、GECCO 的九项指标中，CrossAD 整体表现强；例如 PSM 的 VUS-PR 是 0.5596，TimesNet 是 0.4373。但指标和数据集有限，不宜推广成在所有 benchmark 上必然最好。（PDF pp.8–9, Table 2）

TSB-AD-U 附加表中 CrossAD 的 AUC-PR/AUC-ROC/VUS-PR/VUS-ROC/Standard-F1/PA-F1/Event-F1/R-based-F1/Affiliation-F1 分别为 0.44/0.78/0.45/0.84/0.47/0.81/0.68/0.41/0.89；作者称 TSB-AD-U/M 均表现优秀。UCR 附加测试采用 top-quantile 命中异常区间数及平均 quantile，与时间点分类结果不可直接等价。（PDF pp.24–25, Appendix E.3–E.4, Table 10, Figs. 8–9）

#### 6.3 消融、可视化和效率

Table 3 在 PSM、MSL、GECCO 上逐步加入组件，平均 VUS-PR 从单尺度 0.3665 到多尺度 0.3962，再到多尺度 + cross-scale reconstruction 的 0.4326；继续用原型上下文（直接从 encoder 多尺度表示更新）为 0.4597；完整 CrossAD 为 VUS-ROC 0.8447 / VUS-PR 0.4984。该表支持多尺度、跨尺度映射和全局上下文均有贡献。正文称完整方法相较 Row 4 的提升为 3.18% / 10.4%，但用表中 Avg. 数值直接重算，VUS-ROC 相对增幅约 3.1%，VUS-PR 约 8.4%；笔记以表格可复核数值为准，保留此数字口径差异。（PDF pp.9–10, §4.3, Table 3）

Fig. 4 对点、shapelet、seasonal、trend 等五种形态可视化；作者观察到传统重构在 shapelet/seasonal/trend 情形下误差不稳定，而跨尺度残差更能揭示正常尺度映射被破坏。Fig. 5 显示单尺度响应可互补，合并多尺度分数更容易定位细微模式。可视化是案例证据，不是独立统计检验。（PDF pp.10–11, Figs. 4–5）

GECCO 5 epoch 效率对照表中 CrossAD 训练 270.75 秒、测试集推理 0.80 秒、0.93M 参数、VUS-PR 0.6211；Anomaly Transformer 训练 270.49 秒、推理 15.05 秒、4.74M 参数、VUS-PR 0.0278。该效率结果只覆盖 GECCO 和论文指定 batch/硬件，不代表跨数据集运行时保证；作者指出训练中持续更新全局上下文增加训练耗时。（PDF p.10, §4.3, Table 4）

#### 6.4 参数敏感性

作者报告模型对 patch size（设为 1 时明显退化）、window size 和 hidden dimension 相对不敏感；增大尺度数量总体有帮助但会饱和。查询数过多可能引入噪声；上下文原型数的最优值依数据集变化。具体例子：默认查询数 5 在 MSL 上 VUS-PR 0.3144，n=7 为 0.3141；在 GECCO 上 n=7 比 n=5 略好。附录明确将“不同数据集所需的最优查询数和原型数不同，但使用统一参数”列为局限。（PDF pp.22–24, Appendix D, Tables 6–8; PDF p.25, Appendix G）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

查询和原型或能捕捉“经常重复的多尺度形态”，但不一定能区分由相同形态造成的“合法业务高峰”和“资源故障”。如果负载状态变换伴随尺度关系变化，模型反而可能把新正常映射当作异常；论文没有做这种机制切换的条件实验。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

CrossAD 的“跨尺度关联”是同一时间序列不同采样尺度之间的映射，不是 CAROTS 所建模的跨变量 Granger 因果依赖；两者证据轴不同。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

若业务上下文随窗口共同进入 query/router 或原型更新，并以负载相近的不同状态和故障叠加做压力评估，才可检验“模式表示”能否从统计记忆提升为有语义的运行状态识别。这是待验证方向，不是本文结论。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确说明（归属未明确）

最优子序列查询数及全局上下文原型数随数据集变化；当前统一参数可能限制性能，未来可按数据特征自动调整。（PDF p.25, Appendix G）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确说明（归属未明确）

全局上下文在训练期持续更新会增加训练成本。（PDF p.10, §4.3）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

“全局多尺度上下文”是潜在模式原型，不含业务状态、负载、发布或根因标签；论文没有验证每个原型是否对应稳定、可解释的业务运行态。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

论文用 reconstruction residual 判断关系失配，但没有解释造成失配的运维事件；重构失败是异常证据，不等同于根因解释。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

主实验对 MSL/SMAP 仅保留一个连续维度，因而多变量关联价值不适用于所有数据集；其他数据集多变量结果也未配套外生上下文。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

正文强调各数据集 VUS 指标全面领先，但 SWAN 的 VUS-ROC 表格值略低于 TimesNet；消融文字给出的相对提升亦与表格重算略有差别。引用结论时应以具体表格、指标和数据集为单位。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

原型更新伪代码写“每个新窗口”，正文强调训练期间；测试时是否更新不够明确，复现时要核对代码，不能直接把 CrossAD 归类为已验证的 online test-time adaptation。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 实验和方法的边界

SPOT 提供自动阈值，但没有据此展示生产告警成本、业务接受度或故障与工作负载共现的评估。UCR 的量化命中协议也依赖标注异常区间。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：10. My Understanding

CrossAD 的有价值之处是把异常看成“一个尺度无法按正常规律从另一个尺度生成”，并试图让模型看到跨窗口重复出现的相似片段。它扩充了重构误差中可检查的关系结构，且多尺度误差比单尺度更适合不同持续长度。可是这仍是序列内部的统计一致性：正常业务波动的来源没有被读取，原型语义也没有被命名。因此它能回答“当前观测是否偏离已学习的跨尺度模式”，还没有回答“这个变化是否由合法负载、发布或环境切换导致”。

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 在多负载、多运行模式及故障叠加数据中，显式提供 workload / deployment / trace 上下文，验证模式原型能否识别合法状态切换。
- **[证据缺口]** 比较冻结、延迟更新和带置信校验的在线原型更新，测量新正常适应速度、故障吸收率、误报成本和恢复能力。
- **[分析推断]** 与 CAROTS 的跨变量依赖建模组合，分离“跨时间尺度映射被破坏”和“跨变量预测关系被破坏”的贡献。
- **[证据缺口]** 将查询和原型与可审计业务状态标签对齐，验证其可解释性，而非仅用检测分数验证聚类效果。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **CAPMix**：CAPMix 通过合成伪异常与 DTW 软标签改善训练判别边界；CrossAD 是无监督多尺度重构路线，检验尺度关联能否重构。前者关注伪标签可信度，后者关注跨尺度映射失配。
- **When Model Meets New Normals**：后者利用测试流 EMA 和伪正常点在线适应；CrossAD 以训练得到的查询/原型提供窗口间上下文，不能在推理阶段持续自适应这一点上与之混同。
- **CAROTS**：CAROTS 以跨变量 Granger 预测依赖指导增强与分数；CrossAD 以单个序列的粗细尺度映射及跨窗重复子序列为主。CAROTS 的关系偏因果预测图，CrossAD 的关系偏时间分辨率映射。
- **待读方向**：与 Learning Multi-Pattern Normalities in the Frequency Domain 比较时，重点核对 CrossAD 的查询 / 原型是否显式代表多种正常模式，还是只共享可重用统计子序列。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.1–3, §§1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.2–6, §§3.1–3.3, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.1–4, §§1 | 精读笔记保留的原文定位 |
| Research problem / scenario | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.7–9 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.2–3, Fig. 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.4–5, §3.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.2–3 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.3–6, §§3.1–3.3, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.4–5, §3.2, Eq. 1, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF p.5, §3.2, Eq. 3, Eqs. 2–3, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | Eq. 4 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.5–6, §3.2, Eqs. 4–6 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | Eq. 8 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.6–7, §3.3, Eq. (6), Eqs. 7–11 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF p.7, PDF p.21, §3.3, Algorithm 1 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | Eq. (1) | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF p.7, §3.4, Eq. 12 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF p.21, Table 5 | 精读笔记保留的原文定位 |
| Method / formulas | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.22–24 | 精读笔记保留的原文定位 |
| Experimental evidence | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.7–8, §4.1, Table 5 | 精读笔记保留的原文定位 |
| Experimental evidence | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.7–9, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.8–9, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.8–9, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf | PDF pp.24–25, Table 10 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "crossad",
  "title_en": "CrossAD: Time Series Anomaly Detection with Cross-scale Associations and Cross-window Modeling",
  "title_zh": "跨尺度关联与跨窗口建模的时间序列异常检测",
  "authors": [
    "Beibu Li",
    "Qichao Shentu（共同一作）",
    "Yang Shu",
    "Hui Zhang",
    "Ming Li",
    "Ning Jin",
    "Bin Yang",
    "Chenjuan Guo"
  ],
  "year": 2025,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/NeurIPS/CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
  "reading_note_path": "papers/crossad/notes.md",
  "code_url": "https://github.com/decisionintelligence/CrossAD",
  "research_area": "无监督多变量异常检测与跨尺度/跨窗口建模",
  "method_tags": [
    "TSAD multivariate-time-series multi-scale cross-scale-reconstruction cross-window-context prototype sub-series-query reconstruction VUS-PR NeurIPS-2025"
  ],
  "research_scenario": "- [作者主张] 无监督多变量时间序列异常检测，目标是在多种时间分辨率下检测点异常和子序列异常。（PDF pp.1–4, §§1, 3） - [实验支持] SMD、MSL、SMAP、SWaT、PSM、GECCO、SWAN 七个测试集；另有 UCR 250 子集和 TSB-AD 补充基准。（PDF pp.7–9, 21, 24–25）",
  "research_problem": "论文研究无监督多变量时序异常检测：给定训练序列，测试时为未知序列的每个时间点产生异常分数 / 标签。异常的时长和形态不一：细粒度适合发现单点尖峰，粗粒度更容易呈现一段子序列的整体异常。已有多尺度路线往往独立编码各尺度或在特征层简单融合，未直接学习尺度之间的映射；同时常以固定长度窗口切分序列，使窗口只能访问局部数据。（PDF pp.1–3, §§1–2） 作者的关键假设是：训练正常序列中存在稳定的粗到细映射。正常时，较粗的整体趋势和上下文足以重建相应的细节；异常发生后，局部和整体变化对各尺度的影响不同，原有映射被破坏，因此细尺度重构误差上升。第二个假设是，不同窗口里会反复出现上下文相似的子序列，可通过共享的子序列表示和全局原型提供窗口外信息。（PDF pp.2–6, Fig. 1, §§3.1–3.3）",
  "core_challenges": [
    "[作者主张] 多尺度方法常分别建模或简单融合，不显式学习粗粒度到细粒度的正常映射；固定滑窗限制窗口外上下文。（PDF pp.2–3, Fig. 1）",
    "[作者假设] 正常期的跨尺度映射可从训练序列学习，异常会因各尺度敏感性不同而破坏这种映射。（PDF pp.4–5, §3.2）"
  ],
  "existing_method_limits": [
    "[作者主张] 独立尺度建模、特征融合与局部滑窗使已有模型难以捕捉跨尺度关联和窗口间共享上下文。（PDF pp.2–3）",
    "[分析推断] 原型上下文记住重复子序列的统计相似性，不自动提供模式含义，也不区分高负载业务波动和故障。"
  ],
  "core_idea": "CrossAD 不把不同分辨率的序列分开重构或简单融合，而是学习“粗尺度能否按正常映射重建细尺度”；再用周期感知查询和跨窗口原型上下文共享相似子序列模式，以多尺度重构误差作为逐点异常分数。",
  "technical_innovations": [
    {
      "name": "Cross-scale reconstruction",
      "author_claim": "**Cross-scale reconstruction**：目标为所有尺度的平方重构误差和；用更粗尺度条件预测更细尺度。（Eq. 1, Eqs. 4–6）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.2 Cross-scale decoder：以粗尺度为条件重建细尺度",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** 消融平均 VUS-PR：单尺度 0.3665，多尺度 0.3962，加跨尺度重构 0.4326，加由 encoder 表示更新的上下文 0.4597，完整模型 0.4984。（PDF p.9, Table 3）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Cross-scale reconstruction**：目标为所有尺度的平方重构误差和；用更粗尺度条件预测更细尺度。（Eq. 1, Eqs. 4–6）"
    },
    {
      "name": "Scale-Independent Mask",
      "author_claim": "**Scale-Independent Mask**：encoder 的 attention mask 为块对角矩阵，只允许同一尺度内部注意力。（PDF p.5, Eqs. 2–3）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Scale-Independent Mask**：encoder 的 attention mask 为块对角矩阵，只允许同一尺度内部注意力。（PDF p.5, Eqs. 2–3）"
    },
    {
      "name": "Cross-scale Mask decoder",
      "author_claim": "**Cross-scale Mask decoder**：尺度对齐后按粗到细关系解码，避免将跨尺度关系留给隐式 feature fusion。（PDF pp.5–6, Fig. 2, Eqs. 4–6）",
      "challenge_ids": [
        "C1",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.2 Cross-scale decoder：以粗尺度为条件重建细尺度",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Cross-scale Mask decoder**：尺度对齐后按粗到细关系解码，避免将跨尺度关系留给隐式 feature fusion。（PDF pp.5–6, Fig. 2, Eqs. 4–6）"
    },
    {
      "name": "Period-aware query router",
      "author_claim": "**Period-aware query router**：保留 Fourier 幅度 top-k 成分，逆变换后经 MLP 和 Gumbel-Softmax 激活 learnable sub-series queries。（PDF pp.6–7, Eqs. 7–9）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.3 Period-aware Router、子序列查询与全局原型",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Period-aware query router**：保留 Fourier 幅度 top-k 成分，逆变换后经 MLP 和 Gumbel-Softmax 激活 learnable sub-series queries。（PDF pp.6–7, Eqs. 7–9）"
    },
    {
      "name": "Global multi-scale prototypes",
      "author_claim": "**Global multi-scale prototypes**：将窗口表示分配到最近欧氏距离原型并用 EMA 更新，作为 decoder 全局上下文。（PDF p.7, Eqs. 10–11; Appendix A）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "全局上下文在训练期持续更新会增加训练成本。（PDF p.10, §4.3）",
      "limitation_type": "证据边界",
      "source_locator": "**Global multi-scale prototypes**：将窗口表示分配到最近欧氏距离原型并用 EMA 更新，作为 decoder 全局上下文。（PDF p.7, Eqs. 10–11; Appendix A）"
    },
    {
      "name": "Multi-scale score fusion",
      "author_claim": "**Multi-scale score fusion**：每个尺度的平方残差插值回原时间轴并取平均；采用 SPOT 阈值。（PDF p.7, §3.4, Eq. 12）",
      "challenge_ids": [
        "C1",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Multi-scale score fusion**：每个尺度的平方残差插值回原时间轴并取平均；采用 SPOT 阈值。（PDF p.7, §3.4, Eq. 12）"
    }
  ],
  "methodology": {
    "architecture": "text 多变量序列 → 平均池化生成多分辨率序列 → patch embedding + positional encoding → 分尺度编码（Scale-Independent Mask） → 对齐尺度表示 → 以更粗尺度重建细尺度（Cross-scale Mask） ↘ 周期感知 Router 选择 learnable sub-series queries → 对当前窗口多尺度表示 cross-attention 得到子序列表示 → 分配并 EMA 更新全局多尺度原型 → Decoder cross-attend 全局原型并重建各尺度 → 各尺度平方误差插值回原时间轴并平均 → SPOT 阈值 整体采用 channel-independent 处理。每个窗口先经过多尺度重构主干；跨窗口模块则从该窗口的多尺度编码中抽取代表性子序列，将相似模式累积为全局多尺度上下文，并在解码重构时将上下文提供给当前尺度。（PDF pp.3–6, Fig. 2, §§3.1–3.3）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 多尺度生成与尺度内编码",
      "5.2 Cross-scale decoder：以粗尺度为条件重建细尺度",
      "5.3 Period-aware Router、子序列查询与全局原型",
      "5.4 目标函数、异常分数与阈值",
      "5.5 训练与复现要点"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)",
      "Eq. (12)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "CrossAD 不把不同分辨率的序列分开重构或简单融合，而是学习“粗尺度能否按正常映射重建细尺度”；再用周期感知查询和跨窗口原型上下文共享相似子序列模式，以多尺度重构误差作为逐点异常分数。"
  },
  "experimental_evidence": {
    "datasets": [
      "主实验用七个真实数据集 / 子集：SMD（服务器，38维）、MSL（航天器，保留第一个连续维度）、SMAP（同样仅保留第一个连续维度）、SWaT（水处理，31维）、PSM（eBay 服务器，25维）、NeurIPS-TS 的 GECCO（水处理，9维）及 SWAN（Space Weather，38维）。窗口长度分别为 96、128 或 192，训练/验证/测试拆分和异常率见 Appendix B Table 5。补充实验包括 UCR 250 个子数据集以及 TSB-AD-U / TSB-AD-M 40 数据集基准。（PDF pp.7–8, §4.1; pp.21, 24–25, Tables 5, 10）",
      "Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。…",
      "Table 2 对 ModernTCN、TimeMixer、TimesNet 做多指标比较。在 SMD、PSM、GECCO 的九项指标中，CrossAD 整体表现强；例如 PSM 的 VUS-PR 是 0.5596，TimesNet 是 0.4373。但指标和数据集有限，不宜推广成在所有 benchmark 上必然最好。（PDF pp.8–9, Table 2）",
      "GECCO 5 epoch 效率对照表中 CrossAD 训练 270.75 秒、测试集推理 0.80 秒、0.93M 参数、VUS-PR 0.6211；Anomaly Transformer 训练 270.49 秒、推理 15.05 秒、4.74M 参数、VUS-PR 0.0278。该效率结果只覆盖 GECCO 和论文指定 batch/硬件，不代表跨数据集运行时保证；作者指出训练中持续更新全局上下文增加训练耗时。（PDF p.10, §4.3, Table 4）"
    ],
    "baselines": [
      "### 6.1 数据、Baseline 与指标",
      "18 个 baseline 覆盖 OCSVM、PCA、IForest、LODA、HBOS、LOF、AE、DAGMM、LSTM、CAE-Ensemble、OmniAnomaly、Anomaly Transformer、DCdetector、ModernTCN、GPT4TS、MtsCID、TimeMixer、TimesNet。主表重点报告 VUS-ROC / VUS-PR，并补充 AUC-ROC/PR、Standard-F1、Affiliation-F1 和 Range-AUC-ROC/PR；阈值由 SPOT 选取。作者指出 point adjustment 可能导致不公平或虚高，因此采用多种事件 / 阈值敏感指标。…",
      "Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。…"
    ],
    "metrics": [
      "### 6.1 数据、Baseline 与指标",
      "18 个 baseline 覆盖 OCSVM、PCA、IForest、LODA、HBOS、LOF、AE、DAGMM、LSTM、CAE-Ensemble、OmniAnomaly、Anomaly Transformer、DCdetector、ModernTCN、GPT4TS、MtsCID、TimeMixer、TimesNet。主表重点报告 VUS-ROC / VUS-PR，并补充 AUC-ROC/PR、Standard-F1、Affiliation-F1 和 Range-AUC-ROC/PR；阈值由 SPOT 选取。作者指出 point adjustment 可能导致不公平或虚高，因此采用多种事件 / 阈值敏感指标。…",
      "Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。…",
      "Table 2 对 ModernTCN、TimeMixer、TimesNet 做多指标比较。在 SMD、PSM、GECCO 的九项指标中，CrossAD 整体表现强；例如 PSM 的 VUS-PR 是 0.5596，TimesNet 是 0.4373。但指标和数据集有限，不宜推广成在所有 benchmark 上必然最好。（PDF pp.8–9, Table 2）"
    ],
    "main_results": [
      "主实验用七个真实数据集 / 子集：SMD（服务器，38维）、MSL（航天器，保留第一个连续维度）、SMAP（同样仅保留第一个连续维度）、SWaT（水处理，31维）、PSM（eBay 服务器，25维）、NeurIPS-TS 的 GECCO（水处理，9维）及 SWAN（Space Weather，38维）。窗口长度分别为 96、128 或 192，训练/验证/测试拆分和异常率见 Appendix B Table 5。补充实验包括 UCR 250 个子数据集以及 TSB-AD-U / TSB-AD-M 40 数据集基准。（PDF pp.7–8, §4.1; pp.21, 24–25, Tables 5, 10）",
      "18 个 baseline 覆盖 OCSVM、PCA、IForest、LODA、HBOS、LOF、AE、DAGMM、LSTM、CAE-Ensemble、OmniAnomaly、Anomaly Transformer、DCdetector、ModernTCN、GPT4TS、MtsCID、TimeMixer、TimesNet。主表重点报告 VUS-ROC / VUS-PR，并补充 AUC-ROC/PR、Standard-F1、Affiliation-F1 和 Range-AUC-ROC/PR；阈值由 SPOT 选取。作者指出 point adjustment 可能导致不公平或虚高，因此采用多种事件 / 阈值敏感指标。（PDF pp.7–9, §4.1, Tables 1–2; Appendix E.1）",
      "### 6.2 主结果与证据边界",
      "Table 1 中 CrossAD 在六个数据集的 VUS-ROC 与 VUS-PR 同时高于对照方法；SWAN 上 VUS-PR 为 0.9171，高于 TimesNet 的 0.9160，但 VUS-ROC 为 0.9499，略低于 TimesNet 的 0.9515。因此数据表支持“多数数据集 / 指标领先”，不支持原文“所有数据集两项指标都优于”的绝对表述。代表性结果：SMD 0.8580 / 0.2344，MSL 0.8091 / 0.3144，SWaT 0.7865 / 0.4767，PSM 0.7302 / 0.5596，GECCO 0.9948 / 0.6211（依次为 VUS-ROC / VUS-PR）。（PDF pp.8–9, Table 1）",
      "Table 2 对 ModernTCN、TimeMixer、TimesNet 做多指标比较。在 SMD、PSM、GECCO 的九项指标中，CrossAD 整体表现强；例如 PSM 的 VUS-PR 是 0.5596，TimesNet 是 0.4373。但指标和数据集有限，不宜推广成在所有 benchmark 上必然最好。（PDF pp.8–9, Table 2）"
    ],
    "ablations": [
      "### 6.3 消融、可视化和效率",
      "### 6.4 参数敏感性"
    ],
    "robustness_generalization": [
      "### 6.3 消融、可视化和效率",
      "GECCO 5 epoch 效率对照表中 CrossAD 训练 270.75 秒、测试集推理 0.80 秒、0.93M 参数、VUS-PR 0.6211；Anomaly Transformer 训练 270.49 秒、推理 15.05 秒、4.74M 参数、VUS-PR 0.0278。该效率结果只覆盖 GECCO 和论文指定 batch/硬件，不代表跨数据集运行时保证；作者指出训练中持续更新全局上下文增加训练耗时。（PDF p.10, §4.3, Table 4）"
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
      "查询和原型或能捕捉“经常重复的多尺度形态”，但不一定能区分由相同形态造成的“合法业务高峰”和“资源故障”。如果负载状态变换伴随尺度关系变化，模型反而可能把新正常映射当作异常；论文没有做这种机制切换的条件实验。",
      "CrossAD 的“跨尺度关联”是同一时间序列不同采样尺度之间的映射，不是 CAROTS 所建模的跨变量 Granger 因果依赖；两者证据轴不同。",
      "若业务上下文随窗口共同进入 query/router 或原型更新，并以负载相近的不同状态和故障叠加做压力评估，才可检验“模式表示”能否从统计记忆提升为有语义的运行状态识别。这是待验证方向，不是本文结论。"
    ],
    "evidence_gaps": [
      "最优子序列查询数及全局上下文原型数随数据集变化；当前统一参数可能限制性能，未来可按数据特征自动调整。（PDF p.25, Appendix G）",
      "全局上下文在训练期持续更新会增加训练成本。（PDF p.10, §4.3）",
      "“全局多尺度上下文”是潜在模式原型，不含业务状态、负载、发布或根因标签；论文没有验证每个原型是否对应稳定、可解释的业务运行态。",
      "论文用 reconstruction residual 判断关系失配，但没有解释造成失配的运维事件；重构失败是异常证据，不等同于根因解释。",
      "主实验对 MSL/SMAP 仅保留一个连续维度，因而多变量关联价值不适用于所有数据集；其他数据集多变量结果也未配套外生上下文。",
      "正文强调各数据集 VUS 指标全面领先，但 SWAN 的 VUS-ROC 表格值略低于 TimesNet；消融文字给出的相对提升亦与表格重算略有差别。引用结论时应以具体表格、指标和数据集为单位。",
      "原型更新伪代码写“每个新窗口”，正文强调训练期间；测试时是否更新不够明确，复现时要核对代码，不能直接把 CrossAD 归类为已验证的 online test-time adaptation。",
      "SPOT 提供自动阈值，但没有据此展示生产告警成本、业务接受度或故障与工作负载共现的评估。UCR 的量化命中协议也依赖标注异常区间。"
    ]
  },
  "research_implications": [
    "CrossAD 的有价值之处是把异常看成“一个尺度无法按正常规律从另一个尺度生成”，并试图让模型看到跨窗口重复出现的相似片段。它扩充了重构误差中可检查的关系结构，且多尺度误差比单尺度更适合不同持续长度。可是这仍是序列内部的统计一致性：正常业务波动的来源没有被读取，原型语义也没有被命名。因此它能回答“当前观测是否偏离已学习的跨尺度模式”，还没有回答“这个变化是否由合法负载、发布或环境切换导致”。",
    "- [分析推断] 在多负载、多运行模式及故障叠加数据中，显式提供 workload / deployment / trace 上下文，验证模式原型能否识别合法状态切换。 - [证据缺口] 比较冻结、延迟更新和带置信校验的在线原型更新，测量新正常适应速度、故障吸收率、误报成本和恢复能力。 - [分析推断] 与 CAROTS 的跨变量依赖建模组合，分离“跨时间尺度映射被破坏”和“跨变量预测关系被破坏”的贡献。 - [证据缺口] 将查询和原型与可审计业务状态标签对齐，验证其可解释性，而非仅用检测分数验证聚类效果。"
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
      "paper_id": "crossad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "capmix",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.1–3, §§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.2–6, §§3.1–3.3, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.1–4, §§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.7–9",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.2–3, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.4–5, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.3–6, §§3.1–3.3, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.4–5, §3.2, Eq. 1, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF p.5, §3.2, Eq. 3, Eqs. 2–3, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "Eq. 4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "CrossAD_Time_Series_Anomaly_Detection_with_Cross_scale_Associations_and_Cross_window_Modeling.pdf",
      "locator": "PDF pp.5–6, §3.2, Eqs. 4–6",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "ba6793f3e0e449ad59ef8dd70a0248e49a8abc399f6adcda7cfc33dc183d24f3",
    "reading_note_sha256": "974861cbf58a3946e4ff578ab70fbb87f7afa151ce309d237c6127d812398243",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "90179daf3595052ef17c917ef07dbdfca47160b01f59da4b7ffa99afce1214ef"
  },
  "knowledge_card_path": "papers/crossad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
