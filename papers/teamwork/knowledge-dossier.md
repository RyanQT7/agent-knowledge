# Knowledge Dossier — TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling

## 1. Basic Information

- **English title**: TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling
- **中文译名**：TeamWork：非对称角色感知通道建模的多变量时间序列异常检测
- **Authors**: Shiyan Hu, Tengxue Zhang, Jianxin Jin, Xiangfei Qiu, Bin Yang, Chenjuan Guo
- **Venue / year / CCF**: ICML 2026 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf](../../sources/papers/tsad-2024-2026/2026/ICML/TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/decisionintelligence/TeamWork
- **Research area**: 非对称角色感知多变量通道重建检测
- **Method tags**: TSAD

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** MTSAD 中通道重要性不均、周期尺度不同，需同时处理 dominant / auxiliary channel 及 point / subsequence anomalies。（§1）
- **[实验支持]** 8 个真实数据集、16 个 baselines、统一评估协议。（§5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

多变量异常检测既要处理时间依赖，也要处理跨 channel 关系。channel-independent (CI) 忽略真实依赖；channel-dependent (CD) 对所有通道一视同仁，可能引入冗余 / 虚假关系；channel-clustering (CC) 按相似度分组，但仍可能错过真正驱动系统的少数变量，或低估 cluster 外异质辅助信号。（§2.2, pp.3–4）

作者进一步指出，同一异常可随周期长度而变化：点异常在短周期更醒目，在长周期可能被平滑；持续子序列异常则需要更长时间范围；固定 point- / patch-mask 不会显式适应多周期结构。（§1–2, pp.1–3）

**任务边界**：dominant / auxiliary 是由数据统计上的解释力确定的通道角色，不是人工提供的业务主次 / 因果等级。论文称 dominant 变量“驱动系统演化”，但 ERI 本身来自 entropy / mutual information 估计，不单独证明因果方向。（§3.2; 分析推断）

## 4. Core Challenges

#### 精读笔记原章节：知识卡片 Challenges（精读笔记未单列挑战章节）

- **[作者主张]** CI 漏 channel dependency；CD 加入冗余关系；CC 按相似度分组但可能漏掉 dominant variables。（§2.2）
- **[作者主张]** period-agnostic mask 不适配短周期点异常 / 长周期子序列异常。（§2.1）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 等容量 / 全连接建模忽略变量相对 explanatory role；固定 point / patch masking 忽略多周期。（§1–2）
- **[分析推断]** ERI 反映统计依赖，不证明变量是因果驱动因素。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. 一句话总结

TeamWork 先用 entropy reduction index (ERI) 把变量分成相对主导的 dominant 与补充性的 auxiliary channels，再只对 dominant channels 使用依 top-3 FFT 周期定制的 point / segment / period masking 和 multi-conv 时序建模；auxiliary channels 用轻量 MLP，随后由 dominant-guided extraction 与门控层融合，最终以 reconstruction error 检测。（§§3–4, Eqs. 1–14, pp.3–7）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：[作者主张] CI 漏 channel dependency；CD 加入冗余关系；CC 按相似度分组但可能漏掉 dominant variables。（§2.2）
- **C2（第4节挑战）**：[作者主张] period-agnostic mask 不适配短周期点异常 / 长周期子序列异常。（§2.1）

### 7.1 ERI decouple

- **作者技术描述**：**[作者主张] ERI decouple**：$\Delta H_i=H(X_{-i})-H(X_{-i}|x_i)=I(X_{-i};x_i)$，Kraskov estimator、按 max ERI 归一化、阈值 .5。（§4.1, Eqs. 1–4）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.1 ERI-based Variable Decouple”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Period maskers

- **作者技术描述**：**[作者主张] Period maskers**：top-3 FFT periods 分别用 point / segment / period masking。（§4.2, Eqs. 5–9）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Asymmetric gate

- **作者技术描述**：**[作者主张] Asymmetric gate**：主支多尺度建模、辅助支轻量 MLP，由 HM 过滤 HA，再逐支门控融合。（§4.3, Eqs. 10–12）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Reconstruction score

- **作者技术描述**：**[作者主张] Reconstruction score**：融合表示重建 X，以平方误差检测。（§4.4, Eqs. 13–14）
- **对应挑战**：C2、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“5.4 Reconstruction head 与推理”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：4. 整体算法架构

```text
训练多变量序列 X ∈ R^(D×T)
  ├─ ERI：每个变量解释其余变量的 entropy reduction，归一化后按 δ* 切 dominant XM / auxiliary XA
  ├─ Dominant branch：FFT 得 top-3 periods → reshape 为 period matrices
  │    ├─ 短周期：point masker
  │    ├─ 中周期：segment masker
  │    ├─ 长周期：period masker
  │    └─ multi-conv encoder (1×1 / 3×3 / 5×5) → HM
  ├─ Auxiliary branch：轻量 MLP → HA
  ├─ Dominant-guided extraction：HM + HA 门控筛选 HA 信息
  ├─ Role-aware gated interaction：分支自门控后相加
  └─ Reconstruction head → X̂；平方重建误差为异常分数
```

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：5.2 Period-aware Masked Modeling。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：5. 方法细节

#### 5.1 ERI-based Variable Decouple

对变量 $x_{i,:}$，作者定义它对其余变量不确定性的降低：

$$\Delta H_i(X,x_{i,:})=H(X_{-x_i})-H(X_{-x_i}\mid x_{i,:}). \tag{1}$$

该式等价于 $I(X_{-x_i};x_{i,:})$。对每个变量用 Kraskov k-nearest-neighbor estimator 近似，按最大 ERI 归一化：

$$\delta_i=\frac{\Delta H_i}{\max_j\Delta H_j}. \tag{2}$$

阈值 $\delta^*$ 定义 dominant set $X_M=\{x_{i,:}:\delta_i\ge\delta^*\}$；其余通道为 auxiliary $X_A$（Eqs. 3–4）。作者实验默认 $\delta^*=0.5$；所有通道最终都会经某一路进入异常检测。（§4.1, pp.4–5; §5.3, p.8）

主导角色不是人工先验，而是“变量对其余序列统计依赖的相对解释力”。ERI 计算是数据驱动筛选，若变量角色随业务运行阶段变化，固定全局 ERI 会过时；作者在 limitations 明确称当前 role perception 是 static。（§5, p.14）

#### 5.2 Period-aware Masked Modeling

先对 $X_M$ 进行 FFT，取前三个主要周期 $P_1,P_2,P_3$（按周期长度升序）；根据每个周期 $P_i$ 把输入重排成 $G_M^{(i)}\in\mathbb R^{H_i\times P_i}$，每行为一个周期、每列对应周期内相位。（§4.2, p.5）

不同周期分配不同自监督 mask：

- **Point Masker（短周期）**：独立随机遮单点 $M^{(s)}_{h,p}=\mathbf1(u_{h,p}>\rho)$，学细粒度、point anomaly 特征（Eq. 5）。
- **Segment Masker（中周期）**：每行屏蔽连续片段，长度 $\ell_k=\lfloor\alpha P_m\rfloor$，促使模型借助局部上下文恢复（Eq. 6）。
- **Period Masker（长周期）**：屏蔽完整周期行，学习跨周期依赖（Eq. 7）。

masked period matrices 经 projection 和多卷积核 $1\times1,3\times3,5\times5$，再 Align 去 padding、聚合得到 $H_M$（Eqs. 8–9, p.6）。作者解释点 mask 对点异常有用，segment / period masks 帮助 subsequence 异常；这是机制假设，需由异常持续时间分层实验验证。（§4.2）

#### 5.3 Role-aware Gated Interaction Module

auxiliary branch 先以轻量 MLP 得到 $H_A$。dominant-guided extraction 将 dominant 与 auxiliary 拼接，经 $1\times1$ Conv / sigmoid 得 guidance gate：

$$H_A^*=H_A\odot\sigma(\mathrm{Conv}_{1\times1}([H_M;H_A])). \tag{10}$$

再分别对 $H_M$、$H_A^*$ 做 sigmoid-gated projection：

$$O_M=\sigma(\mathrm{Conv}_{1\times1}(H_M))\odot\mathrm{Conv}_{1\times1}(H_M),$$
$$O_A=\sigma(\mathrm{Conv}_{1\times1}(H_A^*))\odot\mathrm{Conv}_{1\times1}(H_A^*). \tag{11–12}$$

最后 $Z=O_M+O_A$。非对称设计给 dominant 多周期高容量表示，给 auxiliary 较轻的计算路径，并由 dominant 指引筛选 auxiliary 补充信息。（§4.3, p.6）

#### 5.4 Reconstruction head 与推理

MLP projection 将融合表示重建为 $\hat X$；训练目标平方 Frobenius reconstruction loss：

$$L_{rec}=\|X-\hat X\|_F^2. \tag{14}$$

测试时重建误差作为 anomaly score，得分越大越异常（§4.4, p.6）。因此方法在 inference 上是 reconstruction scoring；role / period modules 主要改变学习表示，不额外输出变量级 causal explanation。

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (3)、Eq. (5)、Eq. (6)、Eq. (7)、Eq. (8)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：5.4 Reconstruction head 与推理及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

TeamWork 先用 entropy reduction index (ERI) 把变量分成相对主导的 dominant 与补充性的 auxiliary channels，再只对 dominant channels 使用依 top-3 FFT 周期定制的 point / segment / period masking 和 multi-conv 时序建模；auxiliary channels 用轻量 MLP，随后由 dominant-guided extraction 与门控层融合，最终以 reconstruction error 检测。（§§3–4, Eqs. 1–14, pp.3–7）

## 9. Experimental Evidence

#### 精读笔记原章节：6. 实验设计与证据

#### 6.1 数据、对照与阈值

8 个真实多变量数据集：GECCO（水处理）、Genesis（制造设备）、CalIt2（行人流量）、Creditcard、MSL / SMAP（航天）、PSM / SMD（服务器）。维数 2–55，异常率 .17%–11.07%，平均总长约 5,040–1,416,825。（§5.1, Appendix A.1, pp.7, 14）

对照 16 个基线，包括经典 HBOS / PCA / IForest / OCSVM、AE、NLinear / DLinear、PatchTST、TimesNet、DCdetector、Anomaly Transformer、iTransformer、DualTF、ModernTCN、CATCH、CrossAD。按统一 benchmark 重新评估，报告 Aff-F、AUC-ROC，附录扩展 16 指标；label threshold ratio 从预设 $[0.1,0.5,1,2,3,5,10,15,20,25]\%$ 集合选取。附录称遵从 TFB、关闭 drop-last，GPU 为 A800-80GB，Adam，并依 CATCH 的 optimal setting 配置。（§5.1–5.2; Appendix A.3–A.4）

#### 6.2 主结果

作者报告 8 集 Aff-F 与 AUC-ROC 都优于表中 16 个竞争方法（Table 1, p.7）。例如 TeamWork 的 Aff-F：GECCO .934、Genesis .928、CalIt2 .852、Credit .756、MSL .744、SMAP .864、PSM .857、SMD .854；对应 AUC-ROC：.992、.994、.850、.963、.681、.592、.720、.825。注意这些数字的有效比较限于论文统一 benchmark 及该表设置。

#### 6.3 消融和敏感性

- **Channel roles**：Credit / Genesis / SMD 平均 Accuracy 中，完整 TeamWork .927；CI .864、CD .899、CC .872、去掉 dominant .673、去掉 auxiliary .902、随机分配角色 .867（Table 3, p.8）。支持角色区分与两组互补，但角色“主导”不等于因果驱动已验证。
- **Interaction**：去掉 extraction、去掉 gate、简单 add 和双向 auxiliary→dominant 均低于 full 的平均 Accuracy .927（Table 3）。
- **Masking**：仅 point / segment / period masker 平均 .911 / .918 / .915，无 mask .890，完整多 mask .927；支持组合优于单一或无 mask。（Table 3）
- **参数敏感性**：$\delta^*$ 和 mask ratio 在多个值上相对稳定，作者取两者 .5；top-3 periods 足够，多于三周期没有额外收益，卷积核数量 3 较合适。（Fig. 4; Appendix E.1）

#### 6.4 作者明确指出的限制

1. 角色划分静态：某变量在一个 operating stage 可能 dominant，在另一个阶段可能 auxiliary。
2. FFT 周期主要代表全局 periodic structure；弱周期或局部非平稳变化时可能不够有效。作者提出 dynamic roles、wavelet / 局部时频建模作为后续方向。（Limitations, p.14）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

#### 精读笔记原章节：7. 技术贡献、边界与复现价值 — 局限与分析

角色 static、period 用全局 FFT，是作者承认的不适应状态切换和局部非平稳边界。（Limitations, p.14）

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：7. 技术贡献、边界与复现价值 — 局限与分析

ERI 是互信息 / entropy reduction 统计依赖；共同驱动、冗余变量或数据量 / estimator 偏差都可能影响角色归属，不能当作因果发现结果。（Eqs. 1–4；分析推断）

#### 精读笔记原章节：7. 技术贡献、边界与复现价值 — 局限与分析

数值通道角色没有 workload / release / Trace / service graph 语义；重建误差定位偏差，但不解释波动成因。（方法定义；分析推断）

### C. 仍缺乏证据的问题

#### 精读笔记原章节：7. 技术贡献、边界与复现价值 — 局限与分析

辅助变量只用轻量 MLP，可能欠拟合某些高度动态的异质通道；反向信息对 dominant 的价值不确定。（Table 3; Appendix ablation）

#### 精读笔记原章节：7. 技术贡献、边界与复现价值 — 局限与分析

预设 threshold ratio 集、统一 benchmark 与 CATCH-derived 配置降低比较差异，但训练 / 测试 threshold protocol 和跨实体外推需另行确认。（§5.2; Appendix A.4）

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 按运行阶段动态估计 ERI，检测角色切换时避免异常污染角色更新。
- **[分析推断]** 在弱周期、局部非平稳与周期变化、负载 / 故障并发中测多尺度 mask 的作用。
- **[分析推断]** 对比 ERI 角色、因果图和业务拓扑，报告 role stability 与变量级解释忠实度。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **Graph-MoE / CrossAD / CATCH**：均处理变量间交互 / 分组；TeamWork 明确区分变量相对角色，CATCH 偏频率通道关系，CrossAD 偏多尺度交叉重建。
- **ScatterAD**：两者均有“异质性 / representation structure”设计；ScatterAD 的图节点是时间步，TeamWork 的关键角色是传感器变量。
- **CCM-TAD / SARAD / CAROTS / GCAD**：学习 cluster、spatial association、因果保持或 Granger 关系；ERI 信息相关不能替代因果证据。
- **MACE / When Model Meets New Normals**：多正常谱模式 / 在线新状态适配，适合与 TeamWork 静态角色划分比较状态切换安全性。
- **COGNOS**：依 residual white-noise / Kalman filtering 处理统计噪声，TeamWork 依重建表征与角色交互处理跨变量与周期结构。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §2.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §1–2 | 精读笔记保留的原文定位 |
| Research problem / scenario | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §1 | 精读笔记保留的原文定位 |
| Research problem / scenario | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §5 | 精读笔记保留的原文定位 |
| Challenges / prior methods | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §2.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §2.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §4.1, §5.3, Eqs. 3–4 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §5 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §4.2 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Eq. 5 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Eq. 6 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Eq. 7 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §4.2, Eqs. 8–9 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §4.3 | 精读笔记保留的原文定位 |
| Method / formulas | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §4.4 | 精读笔记保留的原文定位 |
| Experimental evidence | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §5.1 | 精读笔记保留的原文定位 |
| Experimental evidence | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | §5.1–5.2 | 精读笔记保留的原文定位 |
| Experimental evidence | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Fig. 4 | 精读笔记保留的原文定位 |
| Limitations | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Eqs. 1–4 | 精读笔记保留的原文定位 |
| Limitations | TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf | Table 3 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "teamwork",
  "title_en": "TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling",
  "title_zh": "TeamWork：非对称角色感知通道建模的多变量时间序列异常检测",
  "authors": [
    "Shiyan Hu",
    "Tengxue Zhang",
    "Jianxin Jin",
    "Xiangfei Qiu",
    "Bin Yang",
    "Chenjuan Guo"
  ],
  "year": 2026,
  "venue": "ICML",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2026/ICML/TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
  "reading_note_path": "papers/teamwork/notes.md",
  "code_url": "https://github.com/decisionintelligence/TeamWork",
  "research_area": "非对称角色感知多变量通道重建检测",
  "method_tags": [
    "TSAD"
  ],
  "research_scenario": "- [作者主张] MTSAD 中通道重要性不均、周期尺度不同，需同时处理 dominant / auxiliary channel 及 point / subsequence anomalies。（§1） - [实验支持] 8 个真实数据集、16 个 baselines、统一评估协议。（§5）",
  "research_problem": "多变量异常检测既要处理时间依赖，也要处理跨 channel 关系。channel-independent (CI) 忽略真实依赖；channel-dependent (CD) 对所有通道一视同仁，可能引入冗余 / 虚假关系；channel-clustering (CC) 按相似度分组，但仍可能错过真正驱动系统的少数变量，或低估 cluster 外异质辅助信号。（§2.2, pp.3–4） 作者进一步指出，同一异常可随周期长度而变化：点异常在短周期更醒目，在长周期可能被平滑；持续子序列异常则需要更长时间范围；固定 point- / patch-mask 不会显式适应多周期结构。（§1–2, pp.1–3） 任务边界：dominant / auxiliary 是由数据统计上的解释力确定的通道角色，不是人工提供的业务主次 / 因果等级。论文称 dominant 变量“驱动系统演化”，但 ERI 本身来自 entropy / mutual information 估计，不单独证明因果方向。（§3.2; 分析推断）",
  "core_challenges": [
    "[作者主张] CI 漏 channel dependency；CD 加入冗余关系；CC 按相似度分组但可能漏掉 dominant variables。（§2.2）",
    "[作者主张] period-agnostic mask 不适配短周期点异常 / 长周期子序列异常。（§2.1）"
  ],
  "existing_method_limits": [
    "[作者主张] 等容量 / 全连接建模忽略变量相对 explanatory role；固定 point / patch masking 忽略多周期。（§1–2）",
    "[分析推断] ERI 反映统计依赖，不证明变量是因果驱动因素。"
  ],
  "core_idea": "TeamWork 先用 entropy reduction index (ERI) 把变量分成相对主导的 dominant 与补充性的 auxiliary channels，再只对 dominant channels 使用依 top-3 FFT 周期定制的 point / segment / period masking 和 multi-conv 时序建模；auxiliary channels 用轻量 MLP，随后由 dominant-guided extraction 与门控层融合，最终以 reconstruction error 检测。（§§3–4, Eqs. 1–14, pp.3–7）",
  "technical_innovations": [
    {
      "name": "ERI decouple",
      "author_claim": "**[作者主张] ERI decouple**：$\\Delta H_i=H(X_{-i})-H(X_{-i}|x_i)=I(X_{-i};x_i)$，Kraskov estimator、按 max ERI 归一化、阈值 .5。（§4.1, Eqs. 1–4）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.1 ERI-based Variable Decouple",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] ERI decouple**：$\\Delta H_i=H(X_{-i})-H(X_{-i}|x_i)=I(X_{-i};x_i)$，Kraskov estimator、按 max ERI 归一化、阈值 .5。（§4.1, Eqs. 1–4）"
    },
    {
      "name": "Period maskers",
      "author_claim": "**[作者主张] Period maskers**：top-3 FFT periods 分别用 point / segment / period masking。（§4.2, Eqs. 5–9）",
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
      "source_locator": "**[作者主张] Period maskers**：top-3 FFT periods 分别用 point / segment / period masking。（§4.2, Eqs. 5–9）"
    },
    {
      "name": "Asymmetric gate",
      "author_claim": "**[作者主张] Asymmetric gate**：主支多尺度建模、辅助支轻量 MLP，由 HM 过滤 HA，再逐支门控融合。（§4.3, Eqs. 10–12）",
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
      "source_locator": "**[作者主张] Asymmetric gate**：主支多尺度建模、辅助支轻量 MLP，由 HM 过滤 HA，再逐支门控融合。（§4.3, Eqs. 10–12）"
    },
    {
      "name": "Reconstruction score",
      "author_claim": "**[作者主张] Reconstruction score**：融合表示重建 X，以平方误差检测。（§4.4, Eqs. 13–14）",
      "challenge_ids": [
        "C2",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "5.4 Reconstruction head 与推理",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Reconstruction score**：融合表示重建 X，以平方误差检测。（§4.4, Eqs. 13–14）"
    }
  ],
  "methodology": {
    "architecture": "text 训练多变量序列 X ∈ R^(D×T) ├─ ERI：每个变量解释其余变量的 entropy reduction，归一化后按 δ 切 dominant XM / auxiliary XA ├─ Dominant branch：FFT 得 top-3 periods → reshape 为 period matrices │ ├─ 短周期：point masker │ ├─ 中周期：segment masker │ ├─ 长周期：period masker │ └─ multi-conv encoder (1×1 / 3×3 / 5×5) → HM ├─ Auxiliary branch：轻量 MLP → HA ├─ Dominant-guided extraction：HM + HA 门控筛选 HA 信息 ├─ Role-aware gated interaction：分支自门控后相加 └─ Reconstruction head → X̂；平方重建误差为异常分数",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "5.1 ERI-based Variable Decouple",
      "5.2 Period-aware Masked Modeling",
      "5.3 Role-aware Gated Interaction Module",
      "5.4 Reconstruction head 与推理"
    ],
    "key_formulas": [
      "Eq. (3)",
      "Eq. (5)",
      "Eq. (6)",
      "Eq. (7)",
      "Eq. (8)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "TeamWork 先用 entropy reduction index (ERI) 把变量分成相对主导的 dominant 与补充性的 auxiliary channels，再只对 dominant channels 使用依 top-3 FFT 周期定制的 point / segment / period masking 和 multi-conv 时序建模；auxiliary channels 用轻量 MLP，随后由 dominant-guided extraction 与门控层融合，最终以 reconstruction error 检测。（§§3–4, Eqs. 1–14, pp.3–7）"
  },
  "experimental_evidence": {
    "datasets": [
      "8 个真实多变量数据集：GECCO（水处理）、Genesis（制造设备）、CalIt2（行人流量）、Creditcard、MSL / SMAP（航天）、PSM / SMD（服务器）。维数 2–55，异常率 .17%–11.07%，平均总长约 5,040–1,416,825。（§5.1, Appendix A.1, pp.7, 14）",
      "对照 16 个基线，包括经典 HBOS / PCA / IForest / OCSVM、AE、NLinear / DLinear、PatchTST、TimesNet、DCdetector、Anomaly Transformer、iTransformer、DualTF、ModernTCN、CATCH、CrossAD。按统一 benchmark 重新评估，报告 Aff-F、AUC-ROC，附录扩展 16 指标；label threshold ratio 从预设 $[0.1,0.5,1,2,3,5,10,15,20,25]\\%$ 集合选取。附录称遵从 TFB、关闭 drop-last，GPU 为 A800-80GB，Adam，…",
      "作者报告 8 集 Aff-F 与 AUC-ROC 都优于表中 16 个竞争方法（Table 1, p.7）。例如 TeamWork 的 Aff-F：GECCO .934、Genesis .928、CalIt2 .852、Credit .756、MSL .744、SMAP .864、PSM .857、SMD .854；对应 AUC-ROC：.992、.994、.850、.963、.681、.592、.720、.825。注意这些数字的有效比较限于论文统一 benchmark 及该表设置。"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "对照 16 个基线，包括经典 HBOS / PCA / IForest / OCSVM、AE、NLinear / DLinear、PatchTST、TimesNet、DCdetector、Anomaly Transformer、iTransformer、DualTF、ModernTCN、CATCH、CrossAD。按统一 benchmark 重新评估，报告 Aff-F、AUC-ROC，附录扩展 16 指标；label threshold ratio 从预设 $[0.1,0.5,1,2,3,5,10,15,20,25]\\%$ 集合选取。附录称遵从 TFB、关闭 drop-last，GPU 为 A800-80GB，Adam，…",
      "作者报告 8 集 Aff-F 与 AUC-ROC 都优于表中 16 个竞争方法（Table 1, p.7）。例如 TeamWork 的 Aff-F：GECCO .934、Genesis .928、CalIt2 .852、Credit .756、MSL .744、SMAP .864、PSM .857、SMD .854；对应 AUC-ROC：.992、.994、.850、.963、.681、.592、.720、.825。注意这些数字的有效比较限于论文统一 benchmark 及该表设置。"
    ],
    "main_results": [
      "### 6.2 主结果",
      "作者报告 8 集 Aff-F 与 AUC-ROC 都优于表中 16 个竞争方法（Table 1, p.7）。例如 TeamWork 的 Aff-F：GECCO .934、Genesis .928、CalIt2 .852、Credit .756、MSL .744、SMAP .864、PSM .857、SMD .854；对应 AUC-ROC：.992、.994、.850、.963、.681、.592、.720、.825。注意这些数字的有效比较限于论文统一 benchmark 及该表设置。",
      "- Channel roles：Credit / Genesis / SMD 平均 Accuracy 中，完整 TeamWork .927；CI .864、CD .899、CC .872、去掉 dominant .673、去掉 auxiliary .902、随机分配角色 .867（Table 3, p.8）。支持角色区分与两组互补，但角色“主导”不等于因果驱动已验证。 - Interaction：去掉 extraction、去掉 gate、简单 add 和双向 auxiliary→dominant 均低于 full 的平均 Accuracy .927（Table 3）。 - Masking：仅 point / segment / period masker 平均 .911 / .918 / .915，…"
    ],
    "ablations": [
      "### 6.3 消融和敏感性",
      "- Channel roles：Credit / Genesis / SMD 平均 Accuracy 中，完整 TeamWork .927；CI .864、CD .899、CC .872、去掉 dominant .673、去掉 auxiliary .902、随机分配角色 .867（Table 3, p.8）。支持角色区分与两组互补，但角色“主导”不等于因果驱动已验证。 - Interaction：去掉 extraction、去掉 gate、简单 add 和双向 auxiliary→dominant 均低于 full 的平均 Accuracy .927（Table 3）。…"
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
      "角色 static、period 用全局 FFT，是作者承认的不适应状态切换和局部非平稳边界。（Limitations, p.14）"
    ],
    "reasoned_inference": [
      "ERI 是互信息 / entropy reduction 统计依赖；共同驱动、冗余变量或数据量 / estimator 偏差都可能影响角色归属，不能当作因果发现结果。（Eqs. 1–4；分析推断）",
      "数值通道角色没有 workload / release / Trace / service graph 语义；重建误差定位偏差，但不解释波动成因。（方法定义；分析推断）"
    ],
    "evidence_gaps": [
      "辅助变量只用轻量 MLP，可能欠拟合某些高度动态的异质通道；反向信息对 dominant 的价值不确定。（Table 3; Appendix ablation）",
      "预设 threshold ratio 集、统一 benchmark 与 CATCH-derived 配置降低比较差异，但训练 / 测试 threshold protocol 和跨实体外推需另行确认。（§5.2; Appendix A.4）"
    ]
  },
  "research_implications": [
    "- [分析推断] 按运行阶段动态估计 ERI，检测角色切换时避免异常污染角色更新。 - [分析推断] 在弱周期、局部非平稳与周期变化、负载 / 故障并发中测多尺度 mask 的作用。 - [分析推断] 对比 ERI 角色、因果图和业务拓扑，报告 role stability 与变量级解释忠实度。"
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
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "cognos",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "gcad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "sarad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "ccm-tad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "graph-moe",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "teamwork",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§2.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§2.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§2.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§4.1, §5.3, Eqs. 3–4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "§4.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf",
      "locator": "Eq. 5",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "39626796cc927d40a8bdcc92eda7e49da9c43bffdff88ccb34779f4db8b376fa",
    "reading_note_sha256": "32d4bd75c1b601de81b1916af9ba9222aa0f3c228850b7d2b69bd0bd5351d1ed",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "4a9e9d084067886e0c4f643a9ddc377d8561f68ad46e9dec452cdf25f7e65e8a"
  },
  "knowledge_card_path": "papers/teamwork/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
