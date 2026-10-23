# Knowledge Dossier — Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion

## 1. Basic Information

- **English title**: Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion
- **中文译名**：从动态视角重新思考时间序列异常检测：时域—频域—曲率融合
- **Authors**: Hang Cui, Zexin Wang, Changhua Pei, Juncheng Hu, Haotian Si, Quan Zhou, Cenjie Hu, Jingjing Li, Dan Pei, Gaogang Xie
- **Venue / year / CCF**: ACM SIGKDD 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/CSTCloudOps/TFC
- **Research area**: 单变量时序动态形态、频率和曲率检测
- **Method tags**: TSAD univariate curvature second-difference frequency-domain multi-span-attention pattern-anomaly event-F1 KDD-2026

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 检测数值范围正常、但局部形状、趋势弯折或周期驱动力已变化的 pattern-wise 时序异常。（PDF §§1–2）
- **[实验支持]** 六个基准 AIOPS、WSD、Yahoo、NAB、UCR、TODS；模型按每条单变量序列分别训练。（PDF §4; Appendix B–C）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

作者认为点值残差擅长识别突变尖峰，却可能漏掉仍处于合理数值范围内的形态改变：连续信号斜率转折、缓慢趋势弯曲、周期驱动力变化。预测 / 重构深网常依赖平滑、聚合或频域重构压制噪声；这些操作也会削弱细小的局部几何变化。作者因此把时序看作演化系统产生的轨迹，写出：

$$x_{t+1}=f_\theta(x_t,u_t)+w_t,\qquad y_t=h(x_t)+v_t.\tag{4}$$

其中 $u_t$ 是外生驱动，异常可能来自转移机制 $f_\theta$ 或 forcing 统计改变，而非观测值 $y_t$ 的立即大幅越界。（PDF pp.1–3, §§1–2）

这里需注意方法与动机的边界：TFC 的 state-space 方程用于说明“机制变化可能不表现为明显点异常”，论文实现是**逐条单变量序列**的表示模型，并没有将真实 workload / 外生驱动 $u_t$ 作为模型输入或估计系统转移机制。（PDF p.4, §3; Appendix C, p.11）

## 4. Core Challenges

#### 精读笔记原章节：4. Three Technical Challenges

1. **Mechanism shift ≠ value shift**：有限窗口内可能存在数值都合理、但演化规律不同的序列；仅在观测空间逐点拟合不易区分。（PDF p.2, §1）
2. **动力学异常支持多尺度**：尖峰与 shapelet 局部，趋势弯曲中程，季节变化长程；单一窗口可能错配。（PDF p.2, §1）
3. **曲率灵敏度与误报的权衡**：二阶差分会放大高频变化，因此也容易放大正常震荡和噪声；需要其他证据进行校准。（PDF p.2, §1）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 单看 point residual 可能漏掉连续值合理的斜率 / 轨迹机制变化；固定 receptive field 难同时适配尖峰、shapelet 与慢趋势。（PDF §§1–2）
- **[分析推断]** 状态空间动机引入外生变量 $u_t$，但模型只使用单变量观测信号，不验证 business context 或机制来源。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

TFC 将时间值、频域周期结构与二阶差分曲率并行编码，以多跨度注意力保留曲率的短、中、长局部形状证据，再用 frequency–curvature cross-attention 校准周期引起的曲率响应，最后逐时路由 pattern evidence 与 temporal evidence。

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：Mechanism shift ≠ value shift：有限窗口内可能存在数值都合理、但演化规律不同的序列；仅在观测空间逐点拟合不易区分。（PDF p.2, §1）
- **C2（第4节挑战）**：动力学异常支持多尺度：尖峰与 shapelet 局部，趋势弯曲中程，季节变化长程；单一窗口可能错配。（PDF p.2, §1）
- **C3（第4节挑战）**：曲率灵敏度与误报的权衡：二阶差分会放大高频变化，因此也容易放大正常震荡和噪声；需要其他证据进行校准。（PDF p.2, §1）

### 7.1 离散二阶差分放大斜率变化点

- **作者技术描述**：**[作者主张]** 离散二阶差分放大斜率变化点，并具有 $-4\sin^2(\omega/2)$ 的频率响应。（Propositions 2.1–2.3, Eqs. 7–9）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 三类证据及二阶差分依据”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 FFT 频谱切成 $K$ 带

- **作者技术描述**：**[作者主张]** FFT 频谱切成 $K$ 带，经 mask / IFFT 形成分带时间表示，再由 MHA 混合。（§3.1, Eqs. 10–11）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Frequency perspective：分带 FFT 表示”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度

- **作者技术描述**：**[作者主张]** Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度。（§3.2, Eqs. 12–16）
- **对应挑战**：C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 Curvature perspective：Multi-Span Attention (MSA)”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 两阶段融合

- **作者技术描述**：**[作者主张]** 两阶段融合：$H_{fc}=\mathrm{CrossAttention}(F,C)$，再 $\hat Y=\alpha(x)H_{fc}+(1-\alpha(x))H_t$。（§3.4, Eqs. 18–19）
- **对应挑战**：C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 Temporal perspective 与两阶段融合”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
univariate input window X
  ├─ Temporal encoder：2 层 Transformer → temporal prediction / embedding H_t
  ├─ Frequency encoder：FFT → K 个频带掩码 → IFFT 频带序列 → MHA / projection → F_fusion
  └─ Curvature encoder：second difference κ_t → per-head span-masked attention → C_fusion
                 ↓
    CrossAttention(F_fusion, C_fusion) → H_fc （周期证据校准曲率形态）
                 ↓
    α(x) 逐时 router：Ŷ = α(x)H_fc + (1−α(x))H_t
```

三个分支分别偏向点 / 上下文异常、周期 / 趋势偏离、局部曲线形状变化；两阶段融合先融合频率与曲率，再与时间表征自适应融合。作者把这一结构称为 temporal–frequency–curvature fusion。（PDF pp.4–6, Fig. 3, §§3.1–3.4）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method Details

#### 6.1 三类证据及二阶差分依据

对离散序列 $y_t$，曲率 proxy 为：

$$a_t=\frac{y_{t+1}-2y_t+y_{t-1}}{\Delta t^2}.\tag{2, 5}$$

作者给出三项理论说明：

- 若连续信号 $y\in C^4$ 且采样间隔足够小，中心二阶差商近似 $y''(t)+O(\Delta t^2)$（Proposition 2.1, Eq. 7）。
- 若分段线性曲线在采样点 $t_0$ 发生斜率从 $m_1$ 到 $m_2$ 的转折，二阶差分在该点为 $(m_2-m_1)/\Delta t$，其他网格位置为零（Proposition 2.2, Eq. 8）。
- 二阶差分的 DTFT 传递函数是 $H(\omega)=e^{j\omega}-2+e^{-j\omega}=-4\sin^2(\omega/2)$，所以频率越高幅度越大，低频极限约为 $\omega^2$（Proposition 2.3, Eq. 9）。

这些命题解释曲率对转折点和高频形变灵敏的原因，也说明高频正常震荡 / 测量噪声会被同样放大，因此论文需要频率分支校准。它们是算子性质，不是“曲率变化即故障”的统计保证。（PDF pp.2–4, Eqs. 2, 5, 7–9）

论文还定义 temporal evidence $y_t$ 本身，以及对过去 $L$ 个观测计算的频谱摘要 $p_t=\Phi(y_{t-L+1:t})$（Eq. 6）。模型未将摘要中的业务驱动变量 / Trace 加进 $\Phi$；周期频谱是观测信号内生证据。（PDF p.3, §2.1, Eqs. 5–6）

#### 6.2 Frequency perspective：分带 FFT 表示

对输入序列 $X$ 做 FFT，将频谱划分为 $K$ 个区间。第 $k$ 个二进制频带 mask $M_k$ 仅保留其索引区间，得到：

$$C_k=\mathcal F^{-1}(\mathcal F(X)\odot M_k).\tag{10}$$

各 $C_k$ 通过 concatenation 和上下投影后由 Multi-Head Attention 混合：

$$\hat F=\operatorname{MHA}(\operatorname{Concat}(C_1,\ldots,C_K)W_{up})W_{down}.\tag{11}$$

这一路让模型表达不同频带 / 周期尺度的信号；作者认为频域信息能帮助识别周期性偏离，并与曲率交叉注意力减少正常周期振荡引起的误报。（PDF p.4, §3.1, Eqs. 10–11）

#### 6.3 Curvature perspective：Multi-Span Attention (MSA)

计算二阶差分 $\kappa_t=(X_{t+1}-2X_t+X_{t-1})/\Delta t^2$（Eq. 12），对曲率序列生成各注意力头的 $Q_r,K_r,V_r$，内积注意力 logits 为 $Q_rK_r^\top/\sqrt{d_k}$（Eq. 13）。与普通全局 attention 不同，MSA 给每个 head 分配一个动态跨度 $r$，使用相对位置 mask：

$$\phi(r,\delta)=\begin{cases}e_r(\delta)w_r,&|\delta|\le 2^r,\\-\infty,&\text{otherwise},\end{cases}\quad
A^r_{ij}=\operatorname{Softmax}\bigl(A_{ij}+\phi(r,|i-j|)\bigr).\tag{14–15}$$

其中 $e_r$ 是可学习相对位置 embedding，$w_r$ 为跨度相关可学习标量。越界位置 softmax 前设成 $-\infty$，各 head 因而只关注自身局部范围；不同 $r$ 的并行 heads 覆盖不同跨度，输出 $A^rV_r$ 拼接后线性映射为 curvature feature $C_{fusion}$（Eqs. 16 及 Fig. 3）。这一分支试图避免全局 attention 混合后局部弯折证据被稀释。（PDF pp.4–5, §3.2, Eqs. 12–16）

#### 6.4 Temporal perspective 与两阶段融合

temporal encoder 是 2 层 Transformer block，每层包含 self-attention、残差 / Dropout / LayerNorm 和两层 ReLU FFN；线性投影得到 temporal prediction $H_t$（Eq. 17）。正文公式未显示 causal mask；因而不能仅凭“trajectory / dynamics-aware”将模型称为流式 causal detector。（PDF p.5, §3.3）

**第一阶段：Frequency–Curvature Cross-Attention。**

$$H_{fc}=\operatorname{CrossAttention}(F_{fusion},C_{fusion}).\tag{18}$$

设计意图是以周期线索调制容易对周期正常振荡过敏的 curvature 表征，保留细微形态变化并减小伪异常响应。（PDF p.5, §3.4）

**第二阶段：Expert Routing with Temporal Integration。**

$$\hat Y=\alpha(x)H_{fc}+(1-\alpha(x))H_t,\qquad \alpha(x)=\operatorname{MLP}(x).\tag{19}$$

routing 根据输入 $x$ 动态分配 pattern embedding 和 temporal embedding 的贡献，目标是使点型异常与形态异常可由不同证据权衡。论文给出结构与融合消融，但没有将 $\alpha$ 解释成概率校准值或具体运行状态分类器。（PDF p.5, §3.4, Eq. 19）

#### 6.5 训练目标、异常分数与可复现细节

作者把 TFC 说成预测下一个 token 的无监督模型，提供了编码 / 融合公式和训练数据划分说明；主文与附录未明确写出最终 point-wise anomaly score 的精确公式、损失函数形式、如何由 $\hat Y$ 生成 score 和实际告警阈值策略。它应属于复现时查代码的项目，不在笔记中臆测成常见 MSE / 残差定义。（PDF pp.4–6, §§3–4; Appendix C–D）

#### 6.6 因果在线性与中心差分的边界

虽然 Eq. 6 的短时频谱可用截至当前的窗口，二阶差分 Eq. 12 明确依赖 $X_{t+1}$，而 temporal Transformer 也未在论文中说明 causal attention mask。因此在逐时间点在线告警下，曲率支路可能需要未来采样点，整体 TFC 不应假定为零前视延迟 / strict online。其论文重点是检测分数而非在线部署。（PDF pp.3–5, Eqs. 6, 12, 17）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (2)、Eq. (5)、Eq. (6)、Eq. (7)、Eq. (8)、Eq. (9)、Eq. (10)、Eq. (12)、Eq. (13)、Eq. (16)、Eq. (17)、Eq. (19)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.5 训练目标、异常分数与可复现细节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.5 训练目标、异常分数与可复现细节及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

TFC 将时间值、频域周期结构与二阶差分曲率并行编码，以多跨度注意力保留曲率的短、中、长局部形状证据，再用 frequency–curvature cross-attention 校准周期引起的曲率响应，最后逐时路由 pattern evidence 与 temporal evidence。

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experiments

#### 7.1 Datasets, baselines, metrics

- **六个数据集**：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11）
- **使用方式**：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。（Appendix C, p.11）
- **Baselines**：17 项，包括 KANAD、AR、TShape、LSTMAD，统计 SubLOF / MatrixProfile / SAND，重构 AE / EncDecAD / TranAD / FCVAE 等。（PDF p.6, §4.1）
- **指标**：Best F1 与 Event F1（F1-E）。后者把连续异常区间当事件单元；Best F1 本身需调阈值，不能作为无标签线上点的直接保证。（PDF pp.5–6, §4.1, Table 1; Appendix D）
- **训练**：每序列 batch=128、初始 lr=.001、最多 100 epochs early stopping；UCR 原训练样本留 20% validation，其余数据采用 train:validation:test=4:1:5；五个随机 seed。（Appendix C, p.11）

#### 7.2 主结果

Table 1 报告 TFC 的 F1 / Event-F1：

| Dataset | F1 | Event F1 |
| --- | ---: | ---: |
| AIOPS | .9406 | .8235 |
| NAB | .9987 | .9308 |
| TODS | .9481 | .9231 |
| UCR | .8996 | .6289 |
| WSD | .9883 | .9315 |
| Yahoo | .9741 | .9618 |

作者声称平均 Best-F1 和 Event-F1 达 SOTA、相对强 baseline 平均提升 10.8%。逐格 Table 1 中 TFC 的 Event-F1 六列均最高；普通 F1 的 AIOPS 为 .9406，低于 POLY 的 .9550，因此不能说每项数据、每个指标都领先。该表只展示一组数值，虽然 Appendix C 提到五个随机种子，却未在 Table 1 展开标准差。应把作者的平均领先结论与逐数据集结果区分开。（PDF pp.6–7, Table 1; Abstract; Appendix C）

#### 7.3 视角消融和融合设计

Table 2 比较完整 TFC、把 MSA 换成 MHA 的 TFC with MHA、仅 Curvature Perspective (CP)、以及 CP w/o MSA。完整 TFC 的表列结果分别为 AIOPS .9405/.8235、NAB .9987/.9307、TODS .9258/.9155、UCR .8995/.6288、WSD .9883/.9315、Yahoo .9741/.9617（依次为 F1 / Event-F1）。**TODS 的 Table 2 值 .9258/.9155 与 Table 1 的 .9481/.9231 不一致**，论文没有解释差异，引用时应注明表号。消融支持多视角与 MSA 总体有益，但 CP 在个别事件指标上接近完整模型，不能推断每个数据每个指标都由所有模块提高。（PDF pp.7–8, Fig. 4, Table 2, §§4.3–4.4）

Figure 6 对比不同融合次序、直接 concat-MLP、固定线性权重等，作者报告所提两阶段策略整体较好；该处主要以图为证，没有逐项数值表。（PDF pp.7–8, §4.5, Fig. 6）

#### 7.4 窗口敏感性、速度和误报图

- Figure 7 在五种窗口设置上比较六种方法的跨数据集平均 F1 / F1-E；作者报告 TFC 更稳定。但属于固定实验基准上的窗口敏感性分析，不等于训练部署后对任意未知业务频率均无需校准。（PDF p.8, §4.6）
- Figure 8 将 AIOPS 一个约 140,000 样本序列的推理时间、平均主指标和磁盘模型大小作图；TFC 位于高分低时延区域。原文没有给出一个跨硬件 / 长期流量负载的具体 SLA 延迟保证。（PDF p.8, §4.7, Fig. 8）
- Figure 2 逐异常类型展示方法检测分数和案例；Figure 5 分别展示单分支输出。它们支持形态差异的可视化解释，但不是对真实故障机制或业务根因的验证。（PDF pp.2–3, 7）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

精读笔记未单独归类；分析推断需依据第 8–9 节的方法假设和实验范围，不能表述为已证实缺陷。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**作者未单列 Limitations 章节**：Conclusion 宣称有益未来多视角建模方向；正文没有系统局限清单。（PDF p.8, §5）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**不使用作者引入的外生驱动 $u_t$**：state-space motivation 强调机制 / forcing 改变，但算法输入仍是单变量 KPI / signal。因而 detector 可能辨识形态变化，却不说明变化是负载、发布、环境变化还是故障导致。（PDF pp.2–5; Appendix C）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**高频噪声也被曲率放大**：频率 cross-attention 的目标是缓解周期振荡误报，但实验没有用已知物理 / 业务驱动说明哪些振荡是合法，也没有压力测试低信噪曲率。（PDF pp.2–5, §3.4）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**中心差分及 temporal self-attention 的在线性不明**：$kappa_t$ 需 $t+1$，Transformer 未给 causal mask；因此无法从论文断定 timestamp $t$ 可无延迟在线评分。（PDF pp.4–5, Eqs. 12, 17）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**阈值与训练目标公开细节不足**：主文未写清最终异常 score 与 loss 计算式；Best-F1 使用阈值校准，部署前固定阈值成绩需要独立验证。（PDF §§3–4, Appendix C–D）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**逐序列独立训练**：跨指标相关性、不同 KPI 的共同故障模式和多实体状态关联未被模型利用；AIOPS / WSD 场景的数据来源不等于系统实际使用了 Trace / release context。（Appendix B–C）

#### 精读笔记原章节：8. Contributions, Limitations and Reproduction — Limitations and evidence boundaries

**评估结论边界**：数据和人工标注模式不一定覆盖真实生产中业务高峰与真实故障并发；Table 1 的 AIOPS F1 并非表中第一，尽管平均与 Event-F1 声称领先；没有公开该 benchmark 的告警人力成本 / 固定阈值精确度。（Table 1; §§4.1–4.7）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 加入负载、发布和 Trace 条件，验证“波形机制变了”是否能进一步区分合法业务变化与故障。
- **[分析推断]** 将 causal / one-sided curvature 与中心差分、离线 Transformer 对照，量化前视延迟对在线告警的影响。
- **[分析推断]** 构造正常周期切换与并发故障的受控数据，测试 frequency branch 是否校准掉真实异常证据。
- **[分析推断]** 公开固定阈值、PR-AUC、Event-F1、误报周期和事件时延，核验 Best-F1 优势能否转成运行收益。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **MACE / TFMAE / Tri-domain ICDE work**：共同利用时频表示，但 TFC 新增显式二阶几何证据和 curvature–frequency cross-attention；频率表示本身不是首创。
- **TShape**：TShape 关注 shapelet / 形状匹配；TFC 以曲率二阶变化形成分支，并用多跨度 attention 汇聚局部几何证据。两者都覆盖 pattern-wise anomalies，但可比较的表示单元不同。
- **CrossAD**：CrossAD 用跨采样尺度粗到细映射失配；TFC 的 frequency bands / curvature spans 是同一输入内的视角与时间跨度，不能等同跨尺度正常映射。
- **CCM-TAD**：CCM-TAD 对多变量通道做静态相关聚类并使用因果时间 mask；TFC 为逐条 univariate 模型，反而存在中心差分未来点依赖问题。
- **CAPMix / When Model Meets New Normals**：前者校准合成异常边界，后者在线适应新正常；TFC 增加形状变化灵敏度，但没有在线新态安全更新或外因归因机制。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.1–3, §§1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.4, §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | §§1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | §4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.2, §1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | §§1–2 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.4–6, §§3.1–3.4, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | Eq. 7 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | Eq. 8 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | Eq. 9 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.2–4, Eqs. 2 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.3, §2.1, Eq. 6, Eqs. 5–6 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.4, §3.1, Eqs. 10–11 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | Eq. 12, Eq. 13 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.4–5, §3.2, Eqs. 16, Eqs. 12–16, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.5, §3.3, Eq. 17 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.5, §3.4 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.5, §3.4, Eq. 19 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.4–6, §§3–4 | 精读笔记保留的原文定位 |
| Method / formulas | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.3–5, Eq. 6, Eq. 12, Eqs. 6 | 精读笔记保留的原文定位 |
| Experimental evidence | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.5–6, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF p.6, §4.1 | 精读笔记保留的原文定位 |
| Experimental evidence | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | PDF pp.5–6, §4.1, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf | Table 1 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "tfc",
  "title_en": "Rethinking Time Series Anomaly Detection from a Dynamic Perspective: Temporal–Frequency–Curvature Fusion",
  "title_zh": "从动态视角重新思考时间序列异常检测：时域—频域—曲率融合",
  "authors": [
    "Hang Cui",
    "Zexin Wang",
    "Changhua Pei",
    "Juncheng Hu",
    "Haotian Si",
    "Quan Zhou",
    "Cenjie Hu",
    "Jingjing Li",
    "Dan Pei",
    "Gaogang Xie"
  ],
  "year": 2026,
  "venue": "ACM SIGKDD",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/KDD/KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
  "reading_note_path": "papers/tfc/notes.md",
  "code_url": "https://github.com/CSTCloudOps/TFC",
  "research_area": "单变量时序动态形态、频率和曲率检测",
  "method_tags": [
    "TSAD univariate curvature second-difference frequency-domain multi-span-attention pattern-anomaly event-F1 KDD-2026"
  ],
  "research_scenario": "- [作者主张] 检测数值范围正常、但局部形状、趋势弯折或周期驱动力已变化的 pattern-wise 时序异常。（PDF §§1–2） - [实验支持] 六个基准 AIOPS、WSD、Yahoo、NAB、UCR、TODS；模型按每条单变量序列分别训练。（PDF §4; Appendix B–C）",
  "research_problem": "作者认为点值残差擅长识别突变尖峰，却可能漏掉仍处于合理数值范围内的形态改变：连续信号斜率转折、缓慢趋势弯曲、周期驱动力变化。预测 / 重构深网常依赖平滑、聚合或频域重构压制噪声；这些操作也会削弱细小的局部几何变化。作者因此把时序看作演化系统产生的轨迹，写出： $$x{t+1}=f\\theta(xt,ut)+wt,\\qquad yt=h(xt)+vt.\\tag{4}$$ 其中 $ut$ 是外生驱动，异常可能来自转移机制 $f\\theta$ 或 forcing 统计改变，而非观测值 $yt$ 的立即大幅越界。（PDF pp.1–3, §§1–2） 这里需注意方法与动机的边界：TFC 的 state-space 方程用于说明“机制变化可能不表现为明显点异常”，论文实现是逐条单变量序列的表示模型，并没有将真实 workload / 外生驱动 $ut$ 作为模型输入或估计系统转移机制。（PDF p.4, §3; Appendix C, p.11）",
  "core_challenges": [
    "Mechanism shift ≠ value shift：有限窗口内可能存在数值都合理、但演化规律不同的序列；仅在观测空间逐点拟合不易区分。（PDF p.2, §1）",
    "动力学异常支持多尺度：尖峰与 shapelet 局部，趋势弯曲中程，季节变化长程；单一窗口可能错配。（PDF p.2, §1）",
    "曲率灵敏度与误报的权衡：二阶差分会放大高频变化，因此也容易放大正常震荡和噪声；需要其他证据进行校准。（PDF p.2, §1）"
  ],
  "existing_method_limits": [
    "[作者主张] 单看 point residual 可能漏掉连续值合理的斜率 / 轨迹机制变化；固定 receptive field 难同时适配尖峰、shapelet 与慢趋势。（PDF §§1–2）",
    "[分析推断] 状态空间动机引入外生变量 $ut$，但模型只使用单变量观测信号，不验证 business context 或机制来源。"
  ],
  "core_idea": "TFC 将时间值、频域周期结构与二阶差分曲率并行编码，以多跨度注意力保留曲率的短、中、长局部形状证据，再用 frequency–curvature cross-attention 校准周期引起的曲率响应，最后逐时路由 pattern evidence 与 temporal evidence。",
  "technical_innovations": [
    {
      "name": "离散二阶差分放大斜率变化点",
      "author_claim": "**[作者主张]** 离散二阶差分放大斜率变化点，并具有 $-4\\sin^2(\\omega/2)$ 的频率响应。（Propositions 2.1–2.3, Eqs. 7–9）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 三类证据及二阶差分依据",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 离散二阶差分放大斜率变化点，并具有 $-4\\sin^2(\\omega/2)$ 的频率响应。（Propositions 2.1–2.3, Eqs. 7–9）"
    },
    {
      "name": "FFT 频谱切成 $K$ 带",
      "author_claim": "**[作者主张]** FFT 频谱切成 $K$ 带，经 mask / IFFT 形成分带时间表示，再由 MHA 混合。（§3.1, Eqs. 10–11）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Frequency perspective：分带 FFT 表示",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** FFT 频谱切成 $K$ 带，经 mask / IFFT 形成分带时间表示，再由 MHA 混合。（§3.1, Eqs. 10–11）"
    },
    {
      "name": "Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度",
      "author_claim": "**[作者主张]** Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度。（§3.2, Eqs. 12–16）",
      "challenge_ids": [
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 Curvature perspective：Multi-Span Attention (MSA)",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** Curvature branch 用不同范围 mask 的 MSA head 专门读取不同相对跨度。（§3.2, Eqs. 12–16）"
    },
    {
      "name": "两阶段融合",
      "author_claim": "**[作者主张]** 两阶段融合：$H_{fc}=\\mathrm{CrossAttention}(F,C)$，再 $\\hat Y=\\alpha(x)H_{fc}+(1-\\alpha(x))H_t$。（§3.4, Eqs. 18–19）",
      "challenge_ids": [
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 Temporal perspective 与两阶段融合",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张]** 两阶段融合：$H_{fc}=\\mathrm{CrossAttention}(F,C)$，再 $\\hat Y=\\alpha(x)H_{fc}+(1-\\alpha(x))H_t$。（§3.4, Eqs. 18–19）"
    }
  ],
  "methodology": {
    "architecture": "text univariate input window X ├─ Temporal encoder：2 层 Transformer → temporal prediction / embedding Ht ├─ Frequency encoder：FFT → K 个频带掩码 → IFFT 频带序列 → MHA / projection → Ffusion └─ Curvature encoder：second difference κt → per-head span-masked attention → Cfusion ↓ CrossAttention(Ffusion, Cfusion) → Hfc （周期证据校准曲率形态） ↓ α(x) 逐时 router：Ŷ = α(x)Hfc + (1−α(x))Ht 三个分支分别偏向点 / 上下文异常、周期 / 趋势偏离、局部曲线形状变化；两阶段融合先融合频率与曲率，再与时间表征自适应融合。作者把这一结构称为 temporal–frequency–curvature fusion。（PDF pp.4–6, Fig. 3, §§3.1–3.4）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 三类证据及二阶差分依据",
      "6.2 Frequency perspective：分带 FFT 表示",
      "6.3 Curvature perspective：Multi-Span Attention (MSA)",
      "6.4 Temporal perspective 与两阶段融合",
      "6.5 训练目标、异常分数与可复现细节",
      "6.6 因果在线性与中心差分的边界"
    ],
    "key_formulas": [
      "Eq. (2)",
      "Eq. (5)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)",
      "Eq. (9)",
      "Eq. (10)",
      "Eq. (12)",
      "Eq. (13)",
      "Eq. (16)",
      "Eq. (17)",
      "Eq. (19)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "TFC 将时间值、频域周期结构与二阶差分曲率并行编码，以多跨度注意力保留曲率的短、中、长局部形状证据，再用 frequency–curvature cross-attention 校准周期引起的曲率响应，最后逐时路由 pattern evidence 与 temporal evidence。"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Datasets, baselines, metrics",
      "- 六个数据集：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11） - 使用方式：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。…",
      "| Dataset | F1 | Event F1 | | --- | ---: | ---: | | AIOPS | .9406 | .8235 | | NAB | .9987 | .9308 | | TODS | .9481 | .9231 | | UCR | .8996 | .6289 | | WSD | .9883 | .9315 | | Yahoo | .9741 | .9618 |",
      "作者声称平均 Best-F1 和 Event-F1 达 SOTA、相对强 baseline 平均提升 10.8%。逐格 Table 1 中 TFC 的 Event-F1 六列均最高；普通 F1 的 AIOPS 为 .9406，低于 POLY 的 .9550，因此不能说每项数据、每个指标都领先。该表只展示一组数值，虽然 Appendix C 提到五个随机种子，却未在 Table 1 展开标准差。应把作者的平均领先结论与逐数据集结果区分开。（PDF pp.6–7, Table 1; Abstract; Appendix C）"
    ],
    "baselines": [
      "### 7.1 Datasets, baselines, metrics",
      "- 六个数据集：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11） - 使用方式：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。…",
      "作者声称平均 Best-F1 和 Event-F1 达 SOTA、相对强 baseline 平均提升 10.8%。逐格 Table 1 中 TFC 的 Event-F1 六列均最高；普通 F1 的 AIOPS 为 .9406，低于 POLY 的 .9550，因此不能说每项数据、每个指标都领先。该表只展示一组数值，虽然 Appendix C 提到五个随机种子，却未在 Table 1 展开标准差。应把作者的平均领先结论与逐数据集结果区分开。（PDF pp.6–7, Table 1; Abstract; Appendix C）"
    ],
    "metrics": [
      "### 7.1 Datasets, baselines, metrics",
      "- 六个数据集：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11） - 使用方式：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。…",
      "Table 1 报告 TFC 的 F1 / Event-F1：",
      "| Dataset | F1 | Event F1 | | --- | ---: | ---: | | AIOPS | .9406 | .8235 | | NAB | .9987 | .9308 | | TODS | .9481 | .9231 | | UCR | .8996 | .6289 | | WSD | .9883 | .9315 | | Yahoo | .9741 | .9618 |"
    ],
    "main_results": [
      "- 六个数据集：AIOPS、WSD、Yahoo、NAB、UCR、TODS。AIOPS 汇集多互联网公司运维数据；WSD 是 Baidu / Sogou / eBay 生产 KPI；Yahoo 包含 CDN / 广告指标和合成序列；UCR 是跨领域标注集合；TODS 可控合成；NAB 混合云指标与合成流。（PDF pp.5–6, §4.1; Appendix B, pp.10–11） - 使用方式：每条 univariate series 单独训练一个专用模型；AIOPS、WSD 等即使源数据与日志 / Trace / Metrics 相关，输入模型的仍是分开的单变量序列，不是多模态联动输入。（Appendix C, p.11） - Baselines：17 项，…",
      "### 7.2 主结果",
      "Table 1 报告 TFC 的 F1 / Event-F1：",
      "作者声称平均 Best-F1 和 Event-F1 达 SOTA、相对强 baseline 平均提升 10.8%。逐格 Table 1 中 TFC 的 Event-F1 六列均最高；普通 F1 的 AIOPS 为 .9406，低于 POLY 的 .9550，因此不能说每项数据、每个指标都领先。该表只展示一组数值，虽然 Appendix C 提到五个随机种子，却未在 Table 1 展开标准差。应把作者的平均领先结论与逐数据集结果区分开。（PDF pp.6–7, Table 1; Abstract; Appendix C）",
      "Table 2 比较完整 TFC、把 MSA 换成 MHA 的 TFC with MHA、仅 Curvature Perspective (CP)、以及 CP w/o MSA。完整 TFC 的表列结果分别为 AIOPS .9405/.8235、NAB .9987/.9307、TODS .9258/.9155、UCR .8995/.6288、WSD .9883/.9315、Yahoo .9741/.9617（依次为 F1 / Event-F1）。TODS 的 Table 2 值 .9258/.9155 与 Table 1 的 .9481/.9231 不一致，论文没有解释差异，引用时应注明表号。消融支持多视角与 MSA 总体有益，但 CP 在个别事件指标上接近完整模型，不能推断每个数据每个指标都由所有模块提高。…"
    ],
    "ablations": [
      "### 7.3 视角消融和融合设计",
      "Table 2 比较完整 TFC、把 MSA 换成 MHA 的 TFC with MHA、仅 Curvature Perspective (CP)、以及 CP w/o MSA。完整 TFC 的表列结果分别为 AIOPS .9405/.8235、NAB .9987/.9307、TODS .9258/.9155、UCR .8995/.6288、WSD .9883/.9315、Yahoo .9741/.9617（依次为 F1 / Event-F1）。TODS 的 Table 2 值 .9258/.9155 与 Table 1 的 .9481/.9231 不一致，论文没有解释差异，引用时应注明表号。消融支持多视角与 MSA 总体有益，…",
      "### 7.4 窗口敏感性、速度和误报图",
      "- Figure 7 在五种窗口设置上比较六种方法的跨数据集平均 F1 / F1-E；作者报告 TFC 更稳定。但属于固定实验基准上的窗口敏感性分析，不等于训练部署后对任意未知业务频率均无需校准。（PDF p.8, §4.6） - Figure 8 将 AIOPS 一个约 140,000 样本序列的推理时间、平均主指标和磁盘模型大小作图；TFC 位于高分低时延区域。原文没有给出一个跨硬件 / 长期流量负载的具体 SLA 延迟保证。（PDF p.8, §4.7, Fig. 8） - Figure 2 逐异常类型展示方法检测分数和案例；Figure 5 分别展示单分支输出。它们支持形态差异的可视化解释，…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "- Figure 7 在五种窗口设置上比较六种方法的跨数据集平均 F1 / F1-E；作者报告 TFC 更稳定。但属于固定实验基准上的窗口敏感性分析，不等于训练部署后对任意未知业务频率均无需校准。（PDF p.8, §4.6） - Figure 8 将 AIOPS 一个约 140,000 样本序列的推理时间、平均主指标和磁盘模型大小作图；TFC 位于高分低时延区域。原文没有给出一个跨硬件 / 长期流量负载的具体 SLA 延迟保证。（PDF p.8, §4.7, Fig. 8） - Figure 2 逐异常类型展示方法检测分数和案例；Figure 5 分别展示单分支输出。它们支持形态差异的可视化解释，…"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "见档案 §10.B；保持为分析而非已证实结论"
    ],
    "evidence_gaps": [
      "作者未单列 Limitations 章节：Conclusion 宣称有益未来多视角建模方向；正文没有系统局限清单。（PDF p.8, §5）",
      "不使用作者引入的外生驱动 $ut$：state-space motivation 强调机制 / forcing 改变，但算法输入仍是单变量 KPI / signal。因而 detector 可能辨识形态变化，却不说明变化是负载、发布、环境变化还是故障导致。（PDF pp.2–5; Appendix C）",
      "高频噪声也被曲率放大：频率 cross-attention 的目标是缓解周期振荡误报，但实验没有用已知物理 / 业务驱动说明哪些振荡是合法，也没有压力测试低信噪曲率。（PDF pp.2–5, §3.4）",
      "中心差分及 temporal self-attention 的在线性不明：$kappat$ 需 $t+1$，Transformer 未给 causal mask；因此无法从论文断定 timestamp $t$ 可无延迟在线评分。（PDF pp.4–5, Eqs. 12, 17）",
      "阈值与训练目标公开细节不足：主文未写清最终异常 score 与 loss 计算式；Best-F1 使用阈值校准，部署前固定阈值成绩需要独立验证。（PDF §§3–4, Appendix C–D）",
      "逐序列独立训练：跨指标相关性、不同 KPI 的共同故障模式和多实体状态关联未被模型利用；AIOPS / WSD 场景的数据来源不等于系统实际使用了 Trace / release context。（Appendix B–C）",
      "评估结论边界：数据和人工标注模式不一定覆盖真实生产中业务高峰与真实故障并发；Table 1 的 AIOPS F1 并非表中第一，尽管平均与 Event-F1 声称领先；没有公开该 benchmark 的告警人力成本 / 固定阈值精确度。（Table 1; §§4.1–4.7）"
    ]
  },
  "research_implications": [
    "- [分析推断] 加入负载、发布和 Trace 条件，验证“波形机制变了”是否能进一步区分合法业务变化与故障。 - [分析推断] 将 causal / one-sided curvature 与中心差分、离线 Transformer 对照，量化前视延迟对在线告警的影响。 - [分析推断] 构造正常周期切换与并发故障的受控数据，测试 frequency branch 是否校准掉真实异常证据。 - [分析推断] 公开固定阈值、PR-AUC、Event-F1、误报周期和事件时延，核验 Best-F1 优势能否转成运行收益。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "crossad",
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
      "paper_id": "tfmae",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "ccm-tad",
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
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF pp.1–3, §§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF p.4, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "§§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "§4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF p.2, §1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "§§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF pp.4–6, §§3.1–3.4, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "Eq. 7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "Eq. 8",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "Eq. 9",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF pp.2–4, Eqs. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "KDD26-Rethinking Time Series Anomaly Detection from a DynamicPerspective- Temporal–Frequency–Curvature Fusion.pdf",
      "locator": "PDF p.3, §2.1, Eq. 6, Eqs. 5–6",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "74d591e914db9b650e6b646e84ea07abcdf23579343e33523ff1911d2d6fe328",
    "reading_note_sha256": "1a37381cf2340d9ab8386c9e2f17328ceff66736b95743723c083de6fbea2b4c",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "4ce890f6eb6dd6ddf101d0dc07703be1e872f811386b5b760194b203798caa82"
  },
  "knowledge_card_path": "papers/tfc/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
