# Knowledge Dossier — Fortifying Time Series: DTW-Certified Robust Anomaly Detection

## 1. Basic Information

- **English title**: Fortifying Time Series: DTW-Certified Robust Anomaly Detection
- **中文译名**：加固时间序列：DTW 认证鲁棒异常检测
- **Authors**: Shijie Liu, Tansu Alpcan, Christopher Leckie, Sarah Erfani
- **Venue / year / CCF**: NeurIPS 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: 精读笔记未核实到作者代码仓库（待确认）
- **Research area**: 时间序列异常分类器的 DTW 对抗鲁棒认证
- **Method tags**: TSAD adversarial-robustness DTW randomized-smoothing percentile-smoothing certified-defense Keogh-bound robustness-certificate NeurIPS-2025

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 安全关键时序异常检测中的白盒对抗鲁棒性；覆盖 evasion（异常逃逸）和 availability（正常样本被误报）两类扰动。（PDF pp.1–4, §§1, 3.1）
- **[实验支持]** COUTA、TimesNet、DeepSVDDTS；SMAP、MSL、SMD、SWAN、CREDITCARD、WATER、UCR-1、UCR-2 表列基准。（PDF pp.7–8, 24）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

作者关注对抗鲁棒性。时序异常检测在医疗、金融、工业和移动网络等场景中可能被对抗者操纵；传统认证多约束 $\ell_p$ 范数，但小幅时间平移、拉伸或压缩会显著增加逐点 $\ell_p$ 距离，即使序列的时间形态语义相近。DTW 通过寻找单调、端点匹配的时间对齐路径来比较序列，更适合刻画时间变化。（PDF pp.1–3, §1, Fig. 1）

论文威胁模型设攻击者具有白盒检测器访问和无限计算能力，可对当前判为正常或异常的序列发起两类攻击：**evasion** 将真实异常变成正常，**availability** 将正常样本变成误报。攻击输入必须在 DTW 半径 $e$ 内，以表示时间扭曲后语义仍需保持。对抗者不限攻击优化手段；认证目标是对半径内所有输入保证原预测决策不变，概率至少为 $1-\alpha$。（PDF pp.3–4, §3.1）

重要区分：这是“相对于已作预测的决策稳定性”，不是“标签正确性”本身。对一个误报样本证明其在小 DTW 扰动下仍为误报，也满足稳定性定义；只有将证书和真值结合，构造 certified TP/TN 等指标，才衡量正确预测是否得到保护。（PDF pp.7–8, §4; Appendix E, pp.24–25）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** 对时序数据，逐点 $\ell_p$ 范数不能表达时间移动、拉伸和压缩带来的形态相似性；已有 $\ell_p$ 认证防护对 DTW 攻击不充分。（PDF pp.1–3, Fig. 1）
- **[作者目标]** 为 anomaly score detector 提供 DTW 半径内的形式化分类不变性保证。（PDF pp.3–6, §3, Theorem 3.3）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 经验防御可能被自适应攻击绕过；已有认证大多使用与时序形变不匹配的 $\ell_p$ 威胁模型。（PDF pp.2–3）
- **[分析推断]** DTW 认证解决的是对抗决策稳定性，不覆盖业务负载变化的合法性识别，也不自动证明原预测是正确的。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：4. Core Idea and Pipeline

```text
预训练打分器 f(x) + 原阈值 γ
       → 对输入加多份高斯噪声，计算扰动分数
       →（作者所述 denoising layer）+ p 分位数平滑分数 h_p(x)
       → Monte Carlo order statistics 得 h_p 的上下界，置信度 1−α
       → 由分位数到 γ 的 margin 求输入 ℓ2 认证半径 r
       → 用局部 Keogh envelope slack (R, M) 把 r 转成 DTW 半径 e
       → 输出平滑检测结果及每个样本的证书
```

这是一个免重训练的 wrapper：被保护的检测器可以是任意确定性或随机打分函数；框架不要求修改原模型训练。主要方法依赖随机输入扰动、有限样本的分位数界与一个可计算 DTW 下界。（PDF pp.4–7, §§3.2–3.3, Fig. 2）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] 对时序数据，逐点 $\ellp$ 范数不能表达时间移动、拉伸和压缩带来的形态相似性；已有 $\ellp$ 认证防护对 DTW 攻击不充分。（PDF pp.1–3, Fig. 1）
- **C2（第4节挑战）**：[作者目标] 为 anomaly score detector 提供 DTW 半径内的形式化分类不变性保证。（PDF pp.3–6, §3, Theorem 3.3）

### 7.1 Percentile smoothing

- **作者技术描述**：**Percentile smoothing**：$h_p(x)=\sup\{u:P[f(x+\eta)\le u]\le p\}$，针对异常分数无界、高方差改用分位数而非均值平滑。（PDF p.4, Eq. 4）
- **对应挑战**：C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Monte Carlo confidence bounds

- **作者技术描述**：**Monte Carlo confidence bounds**：排序 $n$ 次扰动分数，以二项分布 order-statistic 界估计分位上下界；实验置信度 $1-\alpha$，$\alpha=10^{-3}$。（PDF p.7, Eq. 11）
- **对应挑战**：C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.3 Monte Carlo 分位数的统计保证”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Keogh bridge

- **作者技术描述**：**Keogh bridge**：用 envelope $U_i,L_i$ 构造 DTW 下界，再将 $\ell_2$ 半径转换成 DTW radius。（PDF pp.5–6, Eqs. 6–10）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Closed-form certificate

- **作者技术描述**：**Closed-form certificate**：若 $r\le R$，$e=0$；否则 $e=\sqrt{M^2+r^2-R^2}-M$，其中 $R$ 汇总包络 slack，$M$ 为最大逐点 slack。（PDF p.5, Theorem 3.3）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.5 Model-agnostic wrapper

- **作者技术描述**：**Model-agnostic wrapper**：无需修改预训练 detector 的训练阶段；对噪声扰动分数求 percentile 并输出平滑预测和证书。（PDF pp.6–7, §3.3, Fig. 2）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：基于精读笔记的流程概述

该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\ell2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：5.1 输入、逐点 detector 与 DTW 距离。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. Method in Detail

#### 5.1 输入、逐点 detector 与 DTW 距离

输入窗口 $x\in\mathbb R^{T\times C}$，其中 $T$ 为窗口长度，$C$ 为通道数。检测器输出 anomaly score $f(x)$，再按阈值 $\gamma$ 给出 $d(x)=\mathbb 1[f(x)>\gamma]$。（PDF pp.3–4, §3.1, Eqs. 1–3）

论文定义 $p$ 阶 DTW 距离为：

$$\operatorname{DTW}_p(x,x')=\min_{\pi\in\mathcal A(x,x')}\left(\sum_{(i,j)\in\pi}|x_i-x'_j|^p\right)^{1/p}.\tag{3}$$

$\pi$ 是端点匹配、单调前进且每个序列索引至少出现一次的对齐路径；主文默认 $p=2$。实验进一步用 Sakoe–Chiba wrapping window $w$ 限制允许对齐范围。多变量情况下通道误差进入距离 / envelope 计算；具体任意 $p$ 推广在 Appendix C。（PDF pp.4–5, §3.1, Eq. 3; pp.23–24, Appendix C）

#### 5.2 随机平滑与分位数打分

标准 randomized smoothing 常对 $f(x+\eta)$ 取期望。但异常分数通常无界且可能高方差，均值容易被极端输出影响。作者使用分位数平滑，对噪声分数分布取第 $p$ 分位：

$$h_p(x)=\sup\{u\in\mathbb R:\Pr_{\eta\sim\mathcal N(0,\sigma^2 I)}[f(x+\eta)\le u]\le p\}.\tag{4}$$

它不必对输入作可微修改，可以把多个 $x+\eta$ 送入原模型，对噪声分数取指定 quantile。Lemma 3.1 给出：若 $\|x-x'\|_2\le r$，那么输入变化会把分位水平移动到

$$p^- = \Phi(\Phi^{-1}(p)-r/\sigma),\qquad p^+ = \Phi(\Phi^{-1}(p)+r/\sigma),$$

并有对所有半径内 $x'$ 的下 / 上分位数界 $h_{p^-}(x)\le h_p(x')\le h_{p^+}(x)$。$\Phi$ 为标准高斯 CDF。若原输入的下界仍高于 $\gamma$，异常决策在整个 $\ell_2$ 球内不变；若上界仍不超过 $\gamma$，正常决策不变。根据分位数与阈值间的余量，可反解出最大有效 $r$。（PDF pp.4–5, §3.2, Lemma 3.1, Eqs. 4–5, 9）

附录 A 先复述均值平滑的界，再以分位数版本处理异常分数。主文 Fig. 2 / §3.3 将 wrapper 描述为 $h_p=j\circ k\circ f$：$j$ 注入高斯噪声，$k$ 为降低输出噪声方差的 denoising layer；论文指出任意 downstream pipeline 不破坏随机平滑证书。不过正文没有把该 denoising 层的具体结构、参数化训练方式与逐模型实现完全展开，复现时需依附件代码确定。（PDF pp.6–7, §3.3, Fig. 2; pp.21–23, Appendix A–C）

#### 5.3 Monte Carlo 分位数的统计保证

$h_p$ 无闭式表达，推理时为每个输入生成 $n$ 个独立高斯噪声样本，计算 $f(x+\mu_i)$ 并排序成 order statistics $K_1,\dots,K_n$。基于二项分布尾概率，选择上下次序统计量 $K_{q_l}$ 和 $K_{q_u}$，使估计下界和上界以至少 $1-\alpha$ 的置信度包住分位数；通过二分搜索找到满足置信约束的次序。实验设 $\alpha=10^{-3}$、$n=1000$。增加采样数可提高半径估计精度，但推理开销也随之增加。（PDF p.7, §3.3, Eq. 11）

这里有两层“概率”需分清：高斯扰动定义了平滑分数；有限次 Monte Carlo 又产生估计置信度。统计置信度不是数据标签正确率，也不表示线上事件发生概率。（PDF pp.6–7, §3.3）

#### 5.4 从 $\ell_2$ 半径到 DTW 认证半径

直接算 DTW 代价较高。作者使用 Keogh lower bound：围绕原序列每个时点 $i$，在允许时间扭曲窗口 $w$ 内构造上包络 $U_i$ 与下包络 $L_i$。新序列 $x'_i$ 若在 envelope 内，对 lower bound 不产生代价；落在 envelope 外则按到 envelope 的距离累计。因此 $LB_{Keogh}(x,x')\le DTW(x,x')$，并在 $w>0,x'\ne x$ 的条件下使用严格下界性质。（PDF p.5, §3.2, Eqs. 6–7; Appendix B, p.22）

一般的下界转换引理是：若平滑打分器在输入 $\ell_2$ 球 $\|x'-x\|_2\le r$ 内有证书，取 $e=\inf\{LB(x,x'):\|x'-x\|_2>r\}$，则 DTW 半径不超过 $e$ 的输入必须在该 $\ell_2$ 球内，继承其分类保证。（PDF p.5, Lemma 3.2, Eq. 8）

对 Keogh 下界，定义每个时刻在包络内可“隐藏”的最大偏移

$$\Delta_i=\max(U_i-x_i,\,x_i-L_i),\quad R=\sqrt{\sum_i\|\Delta_i\|_2^2},\quad M=\max_i\|\Delta_i\|_2.$$

当 $r\le R$，允许的 $\ell_2$ 扰动可以完全落在 envelope slack 中，故无法保证正 DTW 半径，$e=0$。当 $r>R$，至少有一部分扰动越出 envelope，定理 3.3 给出

$$e=\sqrt{M^2+r^2-R^2}-M.\tag{10}$$

这是把分位数分数与决策阈值的 margin 得到的 $r$ 转成 DTW 半径；若高斯分位数边界离阈值很近，则 $r$ 小，证书可能为零。包络宽、通道多、样本变化大时 $R$ 或 $M$ 增大，也会使 DTW 下界证书偏松。（PDF pp.5–6, Theorem 3.3, Eqs. 9–10; Appendix B, pp.22–23）

附录 C 声称可扩展至任意 $\ell_p$，将高斯噪声换成相对该范数径向对称的噪声（示例 $\ell_1$ 用 Laplace、$\ell_\infty$ 用均匀噪声），并用对偶范数界推导分位数稳定性。主文结果以 $\ell_2$ / Gaussian 为主，不能把推广当作已广泛实测的结论。（PDF p.23, Appendix C）

#### 5.5 训练 / 推理流程与阈值

训练阶段照原流程训练 COUTA、TimesNet 或 DeepSVDDTS；防护包装不修改预训练参数。推理时，对窗口增加高斯扰动并重复打分，估计平滑分位数、输出平滑二分类结果和证书。阈值 $\gamma$ 沿用被保护 detector 的决策阈值；论文没有把这个体系设计成业务代价感知的重新校准模块。（PDF pp.3–7, §§3.1–3.3）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (3)、Eq. (4)、Eq. (6)、Eq. (8)、Eq. (9)、Eq. (11)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：5.5 训练 / 推理流程与阈值；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.5 训练 / 推理流程与阈值及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\ell2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。

## 9. Experimental Evidence

#### 精读笔记原章节：6. Experiments

#### 6.1 设置与指标

实验用三个 detector：COUTA、TimesNet、DeepSVDDTS。数据集表列有 SMAP、MSL、SMD、NeurIPS-TS 的 SWAN / CREDITCARD / WATER，以及 UCR-1 / UCR-2，共八个表列项，兼有单变量和多变量；而 §4 Settings 文字称 seven benchmark datasets，且把 UCR-1/UCR-2 合称 collection。此处是“七个”与 Table 4 八行的口径差异，笔记以表列具体数据为准。（PDF pp.7–8, §4; p.24, Table 4）

主设置 $T=50$、DTW wrapping window $w=4$、噪声样本 $n=1000$、$\sigma=0.5$、percentile $p=0.5$；A100 80GB GPU 与 Xeon Gold 6326 CPU。检测指标是 point-adjusted F1 和 ROC-AUC；证书报告半径均值 / 最大值 / 标准差、非零证书比例；并为 evasion 与 availability 分别定义最坏情况下的 certified TP / TN，计算 certified accuracy 和 certified F1。（PDF pp.7–8, §4; pp.24–25, Appendix E）

#### 6.2 检测性能和证书

Table 1 对比原模型与加上 wrapper 后的性能及证书。结果依模型和数据显著变化，不能概括为“性能总无损”：例如 NIPS-TS-WATER + DeepSVDDTS 非零证书比例 99.46%，平均证书半径 0.189，F1 / ROC-AUC 未下降；但 NIPS-TS-CREDITCARD + COUTA 的 F1 从 0.192 降至 0.003、ROC-AUC 从 0.900 降至 0.300。SMAP/SWAN 上某些模型证书比例偏低，例如 SWAN + COUTA 14.52%。这显示证书覆盖率、半径强度和检测质量之间并不保证同时改善。（PDF pp.7–8, §4.1, Table 1）

Figure 3 给出 COUTA 在 MSL / SMAP 上攻击预算 $t\in[0,0.5]$ 的 certified accuracy / F1 下界曲线；增大 $\sigma$ 时一些曲线更稳健，且作者举 SMAP、$\sigma=1$、evasion $t=0.2$ 时 certified F1 约 0.5。曲线表示对该范围任意对手扰动的最坏情况性能下界，并非实测攻击平均效果。（PDF pp.7–8, Fig. 3）

#### 6.3 与 $\ell_p$ 认证防护在 DTW 攻击下的对比

Table 2 用 COUTA、DTW 攻击预算 $e_{att}=1.0$ 比较无防护、$\ell_p$ certified defense 与 DTW-Certified Defense。无防护模型在 SMD / UCR-1 的 F1 分别下降 60.6% / 89.7%（论文报告）；DTW defense 的 F1 对比 $\ell_p$ 防护，在 MSL 由 0.672 到 0.784（绝对 +0.112），在 UCR-1 由 0.761 到 0.948（绝对 +0.187）；SMD 为 0.392→0.464，WATER 为 0.423→0.525。AUC 也在四个数据集均高于 $\ell_p$ defense。结果支持“所测 DTW 威胁与认证度量对齐后更有抵抗力”，不能推出对非对抗性负载变化 / 未建模业务事件也更鲁棒。（PDF pp.8–9, Table 2）

#### 6.4 噪声强度与窗口消融

Table 3 比较 $\sigma\in\{0.1,0.5,1,2\}$。总体上增大噪声提升平均 / 最大证书半径及非零证书比例，但过大的 $\sigma$ 会损害 F1 / AUC。例如 SMD 的非零证书比例从 52.42%（$\sigma=.1$）升至 94.66%（$\sigma=2$），但 F1 从 .504 降至 .315；SMAP 到 $\sigma=2$ 时 F1/AUC 也降至 .913/.958。中等噪声可能因平滑边界而改善基线指标，但并非单调。（PDF pp.8–9, §4.1, Table 3）

Appendix F Table 7 在 SMD / COUTA 上变更窗口长度 $T\in\{10,50,100,200\}$ 和 DTW 对齐窗口 $w\in\{2,4,10\}$。增大 $T$ 有时提升未平滑 detector 的上下文表现，却大幅降低认证比例：$T=50,w=4$ 为 77.99%，$T=200,w=4$ 降至 41.05%；增大 $w$ 放宽时间对齐、使 Keogh 包络更宽，通常降低证书半径 / 覆盖率。超参数反映 detection context 与 certificate tightness 的权衡。（PDF p.25, Appendix F, Table 7）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

这项工作的“鲁棒”明确针对攻击者在 DTW 半径内对输入做时序变形，不应与“区分正常业务波动 / 真故障”混用。业务负载导致的合法均值或周期切换可能超出证书假设，也可能在半径内但对标签语义重要。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

形式化决策稳定性需要和语义保持威胁模型相匹配。DTW 对齐适合形态平移 / 拉伸，但有的控制系统中时间偏移本身就是故障；应按领域验证 DTW 半径是否真代表语义等价。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 我的分析推断

低覆盖率、零证书和运维可接受的成本应与业务状态条件化报告。仅提高 $\sigma$ 增大证书，同时可能严重降分；这不是免成本安全强化。

### C. 仍缺乏证据的问题

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确讨论（归属未明确）

Monte Carlo 采样引入测试时开销；未来需更高效的采样或自适应噪声注入。（PDF p.9, §5）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 作者明确讨论（归属未明确）

更精确的 DTW lower bound 可能收紧证书；框架未来可推广到时序分类等任务。（PDF p.9, §5）

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

Keogh 是保守下界，不等于精确 DTW 球覆盖；$r\le R$ 时方法明确只能给 $e=0$。严格证书可能比实际经验鲁棒范围小。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

半径对噪声量、窗口长度、warping window、数据变化和通道维数敏感；Table 1 中异常性能有显著下跌案例，需按模型 / 数据分别选择参数。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

证书保证被扰动输入不会改变平滑二分类决策，不保证原始分类正确、不保证跨状态泛化，也不解释告警的业务原因。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

使用 point-adjusted F1，且测试数据 / 阈值协议依常用 benchmark；没有线上业务代价、事件共现或 workload context 评估。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

每点需要多次带噪前向推理，实时报表延迟、吞吐和部署成本未提供系统量化。Table 1 / §5 只指出 overhead 与未来优化。

#### 精读笔记原章节：8. Limitations and Reproduction Value — 方法 / 实验边界

论文报告代码及环境文件在补充材料中，但本地论文索引没有稳定公共仓库 URL；具体复现入口和版本仍需检查附件。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：10. My Understanding

论文的理论桥接是主贡献：把“随机平滑模型对 $\ell_2$ 扰动不变”转成“对 DTW 扰动不变”。Keogh envelope 也暴露了证书松弛的来源——时间轴允许一定范围的对齐偏差，很多 $\ell_2$ 变化可能藏在 envelope slack 内，转成 $e=0$ 或很小的证书。因而论文不是直接在 DTW 球里重新训练或精确搜索所有样本，而是用可计算下界给出保守保证。结果应按“理论可证半径 + 该半径下的正确性覆盖”理解，而不能只看对抗样例上的 F1 增长。

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[证据缺口]** 以真实业务时序事件验证 DTW 扰动语义，校准 $w$、半径和“时间形变仍语义等价”的假设。
- **[分析推断]** 联合报告 certificate coverage、正确性、误报成本、延迟、零证书比例，并按负载 / 工作状态分层，而不是只比较总体指标。
- **[证据缺口]** 评估新正常在线适应后能否重新认证；控制版本更新、训练 / 推理分布差异和阈值校准的证明边界。
- **[分析推断]** 使用更紧 DTW 下界减少 $e=0$ 样本，同时测算额外计算成本和实际攻击安全收益。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **CrossAD** 学习正常粗细时间尺度映射，并用残差做检测；本论文用 DTW 约束证明某检测决策对恶意扰动的稳定性，分别是检测表示和对抗安全层。
- **CAPMix** 对训练时合成异常的可信度与判别边界做鲁棒化；此处不造伪异常、不解释正常态，只对预训练打分器做 randomized smoothing。
- **When Model Meets New Normals** 适应测试分布的新正常；此处追求固定预测在指定 DTW 攻击球内不变，不能作为状态适应机制。
- **研究对比** 可将 DTW 证书放在“异常告警稳健性”这一维，与 CAROTS 的因果异常分数、CrossAD 的尺度关联分数分开评价。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.1–3, §1, Fig. 1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.3–4, §3.1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8, §4 | 精读笔记保留的原文定位 |
| Research problem / scenario | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.1–4, §§1 | 精读笔记保留的原文定位 |
| Research problem / scenario | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.1–3, Fig. 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.3–6, §3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.2–3 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.3–4, §3.1, Eqs. 1–3 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.4–5, §3.1, Eq. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.4–5, §3.2, Eqs. 4–5 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.6–7, §3.3, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF p.7, §3.3, Eq. 11 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.6–7, §3.3 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF p.5, §3.2, Eqs. 6–7 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF p.5, Eq. 8 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.5–6, Eqs. 9–10 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF p.23 | 精读笔记保留的原文定位 |
| Method / formulas | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.3–7, §§3.1–3.3 | 精读笔记保留的原文定位 |
| Experimental evidence | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8, §4, Table 4 | 精读笔记保留的原文定位 |
| Experimental evidence | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8, §4 | 精读笔记保留的原文定位 |
| Experimental evidence | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8, §4.1, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.7–8, Figure 3, Fig. 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf | PDF pp.8–9, Table 2 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "fortifying-time-series",
  "title_en": "Fortifying Time Series: DTW-Certified Robust Anomaly Detection",
  "title_zh": "加固时间序列：DTW 认证鲁棒异常检测",
  "authors": [
    "Shijie Liu",
    "Tansu Alpcan",
    "Christopher Leckie",
    "Sarah Erfani"
  ],
  "year": 2025,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/NeurIPS/Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
  "reading_note_path": "papers/fortifying-time-series/notes.md",
  "code_url": null,
  "research_area": "时间序列异常分类器的 DTW 对抗鲁棒认证",
  "method_tags": [
    "TSAD adversarial-robustness DTW randomized-smoothing percentile-smoothing certified-defense Keogh-bound robustness-certificate NeurIPS-2025"
  ],
  "research_scenario": "- [作者主张] 安全关键时序异常检测中的白盒对抗鲁棒性；覆盖 evasion（异常逃逸）和 availability（正常样本被误报）两类扰动。（PDF pp.1–4, §§1, 3.1） - [实验支持] COUTA、TimesNet、DeepSVDDTS；SMAP、MSL、SMD、SWAN、CREDITCARD、WATER、UCR-1、UCR-2 表列基准。（PDF pp.7–8, 24）",
  "research_problem": "作者关注对抗鲁棒性。时序异常检测在医疗、金融、工业和移动网络等场景中可能被对抗者操纵；传统认证多约束 $\\ellp$ 范数，但小幅时间平移、拉伸或压缩会显著增加逐点 $\\ellp$ 距离，即使序列的时间形态语义相近。DTW 通过寻找单调、端点匹配的时间对齐路径来比较序列，更适合刻画时间变化。（PDF pp.1–3, §1, Fig. 1） 论文威胁模型设攻击者具有白盒检测器访问和无限计算能力，可对当前判为正常或异常的序列发起两类攻击：evasion 将真实异常变成正常，availability 将正常样本变成误报。攻击输入必须在 DTW 半径 $e$ 内，以表示时间扭曲后语义仍需保持。对抗者不限攻击优化手段；认证目标是对半径内所有输入保证原预测决策不变，概率至少为 $1-\\alpha$。（PDF pp.3–4, §3.1） 重要区分：这是“相对于已作预测的决策稳定性”，不是“标签正确性”本身。对一个误报样本证明其在小 DTW 扰动下仍为误报，也满足稳定性定义；只有将证书和真值结合，构造 certified TP/TN 等指标，才衡量正确预测是否得到保护。（PDF pp.7–8, §4; Appendix E, pp.24–25）",
  "core_challenges": [
    "[作者主张] 对时序数据，逐点 $\\ellp$ 范数不能表达时间移动、拉伸和压缩带来的形态相似性；已有 $\\ellp$ 认证防护对 DTW 攻击不充分。（PDF pp.1–3, Fig. 1）",
    "[作者目标] 为 anomaly score detector 提供 DTW 半径内的形式化分类不变性保证。（PDF pp.3–6, §3, Theorem 3.3）"
  ],
  "existing_method_limits": [
    "[作者主张] 经验防御可能被自适应攻击绕过；已有认证大多使用与时序形变不匹配的 $\\ellp$ 威胁模型。（PDF pp.2–3）",
    "[分析推断] DTW 认证解决的是对抗决策稳定性，不覆盖业务负载变化的合法性识别，也不自动证明原预测是正确的。"
  ],
  "core_idea": "该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\\ell2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。",
  "technical_innovations": [
    {
      "name": "Percentile smoothing",
      "author_claim": "**Percentile smoothing**：$h_p(x)=\\sup\\{u:P[f(x+\\eta)\\le u]\\le p\\}$，针对异常分数无界、高方差改用分位数而非均值平滑。（PDF p.4, Eq. 4）",
      "challenge_ids": [
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Percentile smoothing**：$h_p(x)=\\sup\\{u:P[f(x+\\eta)\\le u]\\le p\\}$，针对异常分数无界、高方差改用分位数而非均值平滑。（PDF p.4, Eq. 4）"
    },
    {
      "name": "Monte Carlo confidence bounds",
      "author_claim": "**Monte Carlo confidence bounds**：排序 $n$ 次扰动分数，以二项分布 order-statistic 界估计分位上下界；实验置信度 $1-\\alpha$，$\\alpha=10^{-3}$。（PDF p.7, Eq. 11）",
      "challenge_ids": [
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.3 Monte Carlo 分位数的统计保证",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Monte Carlo confidence bounds**：排序 $n$ 次扰动分数，以二项分布 order-statistic 界估计分位上下界；实验置信度 $1-\\alpha$，$\\alpha=10^{-3}$。（PDF p.7, Eq. 11）"
    },
    {
      "name": "Keogh bridge",
      "author_claim": "**Keogh bridge**：用 envelope $U_i,L_i$ 构造 DTW 下界，再将 $\\ell_2$ 半径转换成 DTW radius。（PDF pp.5–6, Eqs. 6–10）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Keogh bridge**：用 envelope $U_i,L_i$ 构造 DTW 下界，再将 $\\ell_2$ 半径转换成 DTW radius。（PDF pp.5–6, Eqs. 6–10）"
    },
    {
      "name": "Closed-form certificate",
      "author_claim": "**Closed-form certificate**：若 $r\\le R$，$e=0$；否则 $e=\\sqrt{M^2+r^2-R^2}-M$，其中 $R$ 汇总包络 slack，$M$ 为最大逐点 slack。（PDF p.5, Theorem 3.3）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Closed-form certificate**：若 $r\\le R$，$e=0$；否则 $e=\\sqrt{M^2+r^2-R^2}-M$，其中 $R$ 汇总包络 slack，$M$ 为最大逐点 slack。（PDF p.5, Theorem 3.3）"
    },
    {
      "name": "Model-agnostic wrapper",
      "author_claim": "**Model-agnostic wrapper**：无需修改预训练 detector 的训练阶段；对噪声扰动分数求 percentile 并输出平滑预测和证书。（PDF pp.6–7, §3.3, Fig. 2）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**Model-agnostic wrapper**：无需修改预训练 detector 的训练阶段；对噪声扰动分数求 percentile 并输出平滑预测和证书。（PDF pp.6–7, §3.3, Fig. 2）"
    }
  ],
  "methodology": {
    "architecture": "该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\\ell2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 输入、逐点 detector 与 DTW 距离",
      "5.2 随机平滑与分位数打分",
      "5.3 Monte Carlo 分位数的统计保证",
      "5.4 从 $\\ell_2$ 半径到 DTW 认证半径",
      "5.5 训练 / 推理流程与阈值"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (6)",
      "Eq. (8)",
      "Eq. (9)",
      "Eq. (11)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\\ell2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。"
  },
  "experimental_evidence": {
    "datasets": [
      "实验用三个 detector：COUTA、TimesNet、DeepSVDDTS。数据集表列有 SMAP、MSL、SMD、NeurIPS-TS 的 SWAN / CREDITCARD / WATER，以及 UCR-1 / UCR-2，共八个表列项，兼有单变量和多变量；而 §4 Settings 文字称 seven benchmark datasets，且把 UCR-1/UCR-2 合称 collection。此处是“七个”与 Table 4 八行的口径差异，笔记以表列具体数据为准。（PDF pp.7–8, §4; p.24, Table 4）",
      "Table 2 用 COUTA、DTW 攻击预算 $e{att}=1.0$ 比较无防护、$\\ellp$ certified defense 与 DTW-Certified Defense。无防护模型在 SMD / UCR-1 的 F1 分别下降 60.6% / 89.7%（论文报告）；DTW defense 的 F1 对比 $\\ellp$ 防护，在 MSL 由 0.672 到 0.784（绝对 +0.112），在 UCR-1 由 0.761 到 0.948（绝对 +0.187）；SMD 为 0.392→0.464，WATER 为 0.423→0.525。AUC 也在四个数据集均高于 $\\ellp$ defense。…"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 6.1 设置与指标",
      "主设置 $T=50$、DTW wrapping window $w=4$、噪声样本 $n=1000$、$\\sigma=0.5$、percentile $p=0.5$；A100 80GB GPU 与 Xeon Gold 6326 CPU。检测指标是 point-adjusted F1 和 ROC-AUC；证书报告半径均值 / 最大值 / 标准差、非零证书比例；并为 evasion 与 availability 分别定义最坏情况下的 certified TP / TN，计算 certified accuracy 和 certified F1。（PDF pp.7–8, §4; pp.24–25, Appendix E）",
      "Table 1 对比原模型与加上 wrapper 后的性能及证书。结果依模型和数据显著变化，不能概括为“性能总无损”：例如 NIPS-TS-WATER + DeepSVDDTS 非零证书比例 99.46%，平均证书半径 0.189，F1 / ROC-AUC 未下降；但 NIPS-TS-CREDITCARD + COUTA 的 F1 从 0.192 降至 0.003、ROC-AUC 从 0.900 降至 0.300。SMAP/SWAN 上某些模型证书比例偏低，例如 SWAN + COUTA 14.52%。这显示证书覆盖率、半径强度和检测质量之间并不保证同时改善。（PDF pp.7–8, §4.1, Table 1）",
      "Figure 3 给出 COUTA 在 MSL / SMAP 上攻击预算 $t\\in[0,0.5]$ 的 certified accuracy / F1 下界曲线；增大 $\\sigma$ 时一些曲线更稳健，且作者举 SMAP、$\\sigma=1$、evasion $t=0.2$ 时 certified F1 约 0.5。曲线表示对该范围任意对手扰动的最坏情况性能下界，并非实测攻击平均效果。（PDF pp.7–8, Fig. 3）"
    ],
    "main_results": [
      "实验用三个 detector：COUTA、TimesNet、DeepSVDDTS。数据集表列有 SMAP、MSL、SMD、NeurIPS-TS 的 SWAN / CREDITCARD / WATER，以及 UCR-1 / UCR-2，共八个表列项，兼有单变量和多变量；而 §4 Settings 文字称 seven benchmark datasets，且把 UCR-1/UCR-2 合称 collection。此处是“七个”与 Table 4 八行的口径差异，笔记以表列具体数据为准。（PDF pp.7–8, §4; p.24, Table 4）",
      "Table 1 对比原模型与加上 wrapper 后的性能及证书。结果依模型和数据显著变化，不能概括为“性能总无损”：例如 NIPS-TS-WATER + DeepSVDDTS 非零证书比例 99.46%，平均证书半径 0.189，F1 / ROC-AUC 未下降；但 NIPS-TS-CREDITCARD + COUTA 的 F1 从 0.192 降至 0.003、ROC-AUC 从 0.900 降至 0.300。SMAP/SWAN 上某些模型证书比例偏低，例如 SWAN + COUTA 14.52%。这显示证书覆盖率、半径强度和检测质量之间并不保证同时改善。（PDF pp.7–8, §4.1, Table 1）",
      "Figure 3 给出 COUTA 在 MSL / SMAP 上攻击预算 $t\\in[0,0.5]$ 的 certified accuracy / F1 下界曲线；增大 $\\sigma$ 时一些曲线更稳健，且作者举 SMAP、$\\sigma=1$、evasion $t=0.2$ 时 certified F1 约 0.5。曲线表示对该范围任意对手扰动的最坏情况性能下界，并非实测攻击平均效果。（PDF pp.7–8, Fig. 3）",
      "Table 2 用 COUTA、DTW 攻击预算 $e{att}=1.0$ 比较无防护、$\\ellp$ certified defense 与 DTW-Certified Defense。无防护模型在 SMD / UCR-1 的 F1 分别下降 60.6% / 89.7%（论文报告）；DTW defense 的 F1 对比 $\\ellp$ 防护，在 MSL 由 0.672 到 0.784（绝对 +0.112），在 UCR-1 由 0.761 到 0.948（绝对 +0.187）；SMD 为 0.392→0.464，WATER 为 0.423→0.525。AUC 也在四个数据集均高于 $\\ellp$ defense。结果支持“所测 DTW 威胁与认证度量对齐后更有抵抗力”，…",
      "Table 3 比较 $\\sigma\\in\\{0.1,0.5,1,2\\}$。总体上增大噪声提升平均 / 最大证书半径及非零证书比例，但过大的 $\\sigma$ 会损害 F1 / AUC。例如 SMD 的非零证书比例从 52.42%（$\\sigma=.1$）升至 94.66%（$\\sigma=2$），但 F1 从 .504 降至 .315；SMAP 到 $\\sigma=2$ 时 F1/AUC 也降至 .913/.958。中等噪声可能因平滑边界而改善基线指标，但并非单调。（PDF pp.8–9, §4.1, Table 3）"
    ],
    "ablations": [
      "### 6.4 噪声强度与窗口消融"
    ],
    "robustness_generalization": [
      "Table 2 用 COUTA、DTW 攻击预算 $e{att}=1.0$ 比较无防护、$\\ellp$ certified defense 与 DTW-Certified Defense。无防护模型在 SMD / UCR-1 的 F1 分别下降 60.6% / 89.7%（论文报告）；DTW defense 的 F1 对比 $\\ellp$ 防护，在 MSL 由 0.672 到 0.784（绝对 +0.112），在 UCR-1 由 0.761 到 0.948（绝对 +0.187）；SMD 为 0.392→0.464，WATER 为 0.423→0.525。AUC 也在四个数据集均高于 $\\ellp$ defense。…"
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
      "这项工作的“鲁棒”明确针对攻击者在 DTW 半径内对输入做时序变形，不应与“区分正常业务波动 / 真故障”混用。业务负载导致的合法均值或周期切换可能超出证书假设，也可能在半径内但对标签语义重要。",
      "形式化决策稳定性需要和语义保持威胁模型相匹配。DTW 对齐适合形态平移 / 拉伸，但有的控制系统中时间偏移本身就是故障；应按领域验证 DTW 半径是否真代表语义等价。",
      "低覆盖率、零证书和运维可接受的成本应与业务状态条件化报告。仅提高 $\\sigma$ 增大证书，同时可能严重降分；这不是免成本安全强化。"
    ],
    "evidence_gaps": [
      "Monte Carlo 采样引入测试时开销；未来需更高效的采样或自适应噪声注入。（PDF p.9, §5）",
      "更精确的 DTW lower bound 可能收紧证书；框架未来可推广到时序分类等任务。（PDF p.9, §5）",
      "Keogh 是保守下界，不等于精确 DTW 球覆盖；$r\\le R$ 时方法明确只能给 $e=0$。严格证书可能比实际经验鲁棒范围小。",
      "半径对噪声量、窗口长度、warping window、数据变化和通道维数敏感；Table 1 中异常性能有显著下跌案例，需按模型 / 数据分别选择参数。",
      "证书保证被扰动输入不会改变平滑二分类决策，不保证原始分类正确、不保证跨状态泛化，也不解释告警的业务原因。",
      "使用 point-adjusted F1，且测试数据 / 阈值协议依常用 benchmark；没有线上业务代价、事件共现或 workload context 评估。",
      "每点需要多次带噪前向推理，实时报表延迟、吞吐和部署成本未提供系统量化。Table 1 / §5 只指出 overhead 与未来优化。",
      "论文报告代码及环境文件在补充材料中，但本地论文索引没有稳定公共仓库 URL；具体复现入口和版本仍需检查附件。"
    ]
  },
  "research_implications": [
    "论文的理论桥接是主贡献：把“随机平滑模型对 $\\ell2$ 扰动不变”转成“对 DTW 扰动不变”。Keogh envelope 也暴露了证书松弛的来源——时间轴允许一定范围的对齐偏差，很多 $\\ell2$ 变化可能藏在 envelope slack 内，转成 $e=0$ 或很小的证书。因而论文不是直接在 DTW 球里重新训练或精确搜索所有样本，而是用可计算下界给出保守保证。结果应按“理论可证半径 + 该半径下的正确性覆盖”理解，而不能只看对抗样例上的 F1 增长。",
    "- [证据缺口] 以真实业务时序事件验证 DTW 扰动语义，校准 $w$、半径和“时间形变仍语义等价”的假设。 - [分析推断] 联合报告 certificate coverage、正确性、误报成本、延迟、零证书比例，并按负载 / 工作状态分层，而不是只比较总体指标。 - [证据缺口] 评估新正常在线适应后能否重新认证；控制版本更新、训练 / 推理分布差异和阈值校准的证明边界。 - [分析推断] 使用更紧 DTW 下界减少 $e=0$ 样本，同时测算额外计算成本和实际攻击安全收益。"
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
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–3, §1, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–4, §3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.7–8, §4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–4, §§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.7–8",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.1–3, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–6, §3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–4, §3.1, Eqs. 1–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–5, §3.1, Eq. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–5, §3.2, Eqs. 4–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf",
      "locator": "PDF pp.6–7, §3.3, Fig. 2",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "b07d64fae2ad598ba1090bb2482f1a6aa00a7b697f9ebde84c7520390d71703d",
    "reading_note_sha256": "4f57c3ede378ce5c17bebc848ff873951386eb0ad080d22c2be08e72ca2c8627",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "81a663029fc9a9eb7cdc97e1bc2a9c7bcd9182388c1d3a43054bb4bd0a1dbf5d"
  },
  "knowledge_card_path": "papers/fortifying-time-series/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
