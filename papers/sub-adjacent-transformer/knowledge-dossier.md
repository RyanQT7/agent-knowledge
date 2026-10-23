# Knowledge Dossier — Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods

## 1. Basic Information

- **English title**: Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods
- **中文译名**：Sub-Adjacent Transformer：从非相邻邻域重建误差改进时间序列异常检测
- **Authors**: Wenzhen Yue, Xianghua Ying, Ruohao Guo, DongDong Chen, Ji Shi, Bowei Xing, Yuqing Zhu, Taiyan Chen
- **Venue / year / CCF**: IJCAI 2024 / CCF B
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: [Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf](../../sources/papers/tsad-2024-2026/2024/IJCAI/Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf)
- **Completed reading note**: [notes.md](notes.md)
- **Knowledge card**: [knowledge-card.md](knowledge-card.md)
- **Verified code URL**: https://github.com/jackyue1994/sub_adjacent_transformer
- **Research area**: 非相邻时间邻域重建式异常检测
- **Method tags**: TSAD Transformer linear attention sub-adjacent context reconstruction dynamic Gaussian scoring point adjustment

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 无监督多变量重建 TSAD：防止异常从 immediate neighbors 被直接重建。（§3.2, pp.2–3）
- **[实验支持]** SWaT/WADI/PSM/MSL/SMAP/SMD 及合成 NeurIPS-TS。（Tables 1–3, pp.4–5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

经典重建型 TSAD 常使用滑窗内所有点重建目标时间点。作者观察到，连续数据中的点通常与紧邻点相似，异常附近的紧邻观测尤其可能帮助重建异常本身；如果重建只读距离至少 $k_1$ 且不超过 $k_2$ 的 **sub-adjacent neighborhoods**，正常点仍能从较远邻域恢复，而异常重建会更难，残差可能变大。（§1, §3.2, pp.1–3）

任务为多变量时间序列 $X\in\mathbb R^{T\times N}$ 逐时间点无监督重建和标签预测。核心不是对通道间关系建真实因果图，而是约束 Transformer 的**时间 attention map**：attention 值被视为一个时间点对另一个时间点重建表示的贡献。（§3.1–3.2, pp.2–3）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **紧邻复制会遮蔽异常**：如果 target anomaly 与 immediate neighbors 同处异常段，使用邻近上下文重建会降低 residual。（§3.2, Fig. 1, pp.2–3）
2. **attention 形状难用 vanilla softmax 控制**：标准 row-wise softmax 使同一行竞争，不易形成需要的非对角 sub-adjacent band。（§3.2, Figs. 2–4, pp.3–4）
3. **滑窗边界的可用邻居数不平衡**：窗头 / 窗尾距指定 band 的点较少，attention contribution 会系统性偏低；论文用 circular index shift 平衡各列。（Eq. 2–3）
4. **单一 residual 的 score scale 会动态变化**：作者加入滑动 mean / std 的 dynamic Gaussian score 转换。（§3.3, Eq. 7）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 依赖所有局部邻域的重建模型可能学会异常模式。（§1, §3.2）
- **[分析推断]** 全局固定 sub-adjacent span 不能识别它对应的是合法状态变化还是故障。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

Sub-Adjacent Transformer 将目标点的重建上下文限制在距离 $[k_1,k_2]$ 的非紧邻时间点，使异常较难从最近邻直接复制；用 circularly constructed sub-adjacent attention contribution 最大化该范围权重，与重建误差组合为 anomaly score，并通过可学习 map 的 linear attention 和动态 Gaussian score 改善表示与尺度适应。（§3, Eqs. 1–7, PDF pp.2–4）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：紧邻复制会遮蔽异常：如果 target anomaly 与 immediate neighbors 同处异常段，使用邻近上下文重建会降低 residual。（§3.2, Fig. 1, pp.2–3）
- **C2（第4节挑战）**：attention 形状难用 vanilla softmax 控制：标准 row-wise softmax 使同一行竞争，不易形成需要的非对角 sub-adjacent band。（§3.2, Figs. 2–4, pp.3–4）
- **C3（第4节挑战）**：滑窗边界的可用邻居数不平衡：窗头 / 窗尾距指定 band 的点较少，attention contribution 会系统性偏低；论文用 circular index shift 平衡各列。（Eq. 2–3）
- **C4（第4节挑战）**：单一 residual 的 score scale 会动态变化：作者加入滑动 mean / std 的 dynamic Gaussian score 转换。（§3.3, Eq. 7）

### 7.1 Sub-adjacent contribution

- **作者技术描述**：**[作者主张] Sub-adjacent contribution**：对 attention map 目标列累加指定距离 band。（Eq. 1, p.3）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.1 Sub-adjacent attention contribution”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：**[实验支持]** sub-adjacent distance、window size、lambda、attention mapping 和 dynamic scoring 均有 ablation / sensitivity 表。（Tables 4–8）（论文相关组件比较，具体范围仅限其实际比较的数据集与指标。）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 Circular index construction

- **作者技术描述**：**[作者主张] Circular index construction**：平衡窗口两端的有效 neighbor 数量。（Eqs. 2–3, p.3）
- **对应挑战**：C3、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Circular shift 和 learnable linear attention”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Learnable linear mapping

- **作者技术描述**：**[作者主张] Learnable linear mapping**：$\Phi(U)=Softmax_{row}(U/g)$ 并用 $\Phi(Q)\Phi(K)^T V$ 得到灵活 band map。（Eq. 4, p.4）
- **对应挑战**：C4、C3（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.2 Circular shift 和 learnable linear attention”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Joint score

- **作者技术描述**：**[作者主张] Joint score**：优化 $\|X-\hat X\|^2-\lambda\|SACon\|_1$；推理点 score 为 softmax(-SACon) 与重建误差相乘，再做 dynamic Gaussian tail transform。（Eqs. 5–7）
- **对应挑战**：C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.4 Reconstruction-weighted anomaly score”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。（共享证据，避免重复归因）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
多变量窗口 X ∈ R^(W×N)
  ├─ Q,K,V 与 sub-adjacent linear attention
  │    ├─ Φ(Q), Φ(K) 用带 learnable temperature 的 row-softmax mapping
  │    └─ attention contribution 集中在 k1…k2 距离 band（circular wrap）
  ├─ Transformer reconstruction → X̂
  ├─ 训练目标：||X−X̂||² − λ ||SACon(A)||₁
  ├─ point score：softmax(−SACon(A)) ⊙ point reconstruction error
  └─ 对 score 做滑动 dynamic Gaussian tail transform → threshold label
```

（Fig. 1–5, Eqs. 1–7, pp.2–5）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 Sub-adjacent attention contribution

对窗口 attention matrix $A$，作者把第 $i$ 列理解为第 $i$ 个 target point 对其他点的 attention contribution。指定 $0<k_1\le k_2$；该列离对角线距离满足 $k_1\le |j-i|\le k_2$ 的 attention 值累加，得到逐点 sub-adjacent contribution：

$$\mathrm{SACon}(A)_{i}=\sum_{j:\ k_1\le |j-i|\le k_2} A_{j,i}. \tag{1}$$

如此排除 target 的自身 / 紧邻点，又只使用局部而非整窗远距离 points。正常点应有足够来自 sub-adjacent 周边的 contribution；异常被其紧邻上下文遮蔽的机会减少。（§3.2, Fig. 2, Eq. 1, p.3）

#### 6.2 Circular shift 和 learnable linear attention

若只在矩阵内部求 band，窗口边缘列可参与贡献的 cell 较少。作者通过 cyclic roll $Q$ 构造 attention element（Eq. 2），使索引环绕；等价实现按 Eq. 3 用 circular index 计算 SACon，形成 attention map 的两条额外 side stripes（Fig. 3, p.3）。这均衡列 contribution，但把窗口两端视为循环邻接，是实现上的边界先验。

使用 linear attention：

$$\mathrm{Attn}(Q,K,V)=\Phi(Q)\Phi(K)^\top V,$$

其中映射函数为 row-wise temperature-scaled Softmax：

$$\Phi(U)=\mathrm{Softmax}_{row}(U/g). \tag{4}$$

$g$ 是 learnable 参数；$Q,K$ 中负值先设成约 $-100$，避免通过 row-softmax 变为正权。它不同于 vanilla self-attention 对 $QK^\top$ 结果做 Softmax；对 $Q,K$ 单独作 mapping 使 attention map 更灵活，可调整到预期的 band 形状。（§3.2, Fig. 4, Eq. 4, p.4）

#### 6.3 联合重建与 attention loss

总 loss 由数据重建项和鼓励 sub-adjacent attention 的项构成：

$$\mathcal L_{Total}(X,\hat X,A)=\|X-\hat X\|_F^2-\lambda\|\mathrm{SACon}(A)\|_1. \tag{5}$$

优化时最小化 reconstruction error，同时最大化所有点在有效 sub-adjacent region 的贡献；$\lambda>0$ 平衡两项。直觉是让模型按假设的时间 band 重建，而不靠相邻 target values。若某正常状态变化本身无法由这段较远上下文恢复，目标也会增加其 score。（§3.3, Eq. 5, p.4）

#### 6.4 Reconstruction-weighted anomaly score

先用 $\mathrm{Softmax}(-\mathrm{SACon}(A))$ 为低 attention contribution 的时刻分配更高权重，再逐点乘以 multivariate reconstruction error：

$$\mathrm{AnomalyScore}_i=\mathrm{Softmax}(-\mathrm{SACon}(A))_i\times\|X_{:,i}-\hat X_{:,i}\|_2^2. \tag{6}$$

即异常要同时具备较高重建误差和较低 sub-adjacent contribution 才能获得较高 score。随后在 score 上估计滑动动态 mean $\mu_i$ 和 standard deviation $\sigma_i$，用 Gaussian CDF 上尾概率做变换：

$$\mathrm{DyAnoSco}_i=-\log\left(1-\mathrm{cdf}\left(\frac{\mathrm{AnomalyScore}_i-\mu_i}{\sigma_i}\right)\right). \tag{7}$$

该动态分布转换用于将 score 映射成相对局部 background 的 tail likelihood；是否能在未见合法状态变化时避免误报取决于 local score distribution 的适配与阈值。（§3.3, Eqs. 6–7, pp.4–5）

#### 6.5 参数和训练

- 窗口非重叠划分，默认 window size 100；$k_1=20, k_2=30$。
- 3 层 Transformer，$d_{model}=512$、8 heads，$\lambda=10$。
- Adam，初始学习率 $10^{-4}$，batch size 128，10 epochs 内 early stopping。
- Threshold 按 test best-F1 选择；主报告使用 point adjustment。（§4.2, pp.4–5）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：Eq. (1)、Eq. (2)、Eq. (3)、Eq. (4)、Eq. (5)、Eq. (6)。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节，重点小节：6.3 联合重建与 attention loss；6.5 参数和训练；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.4 Reconstruction-weighted anomaly score及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

Sub-Adjacent Transformer 将目标点的重建上下文限制在距离 $[k1,k2]$ 的非紧邻时间点，使异常较难从最近邻直接复制；用 circularly constructed sub-adjacent attention contribution 最大化该范围权重，与重建误差组合为 anomaly score，并通过可学习 map 的 linear attention 和动态 Gaussian score 改善表示与尺度适应。（§3, Eqs. 1–7, PDF pp.2–4）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 Dataset / baselines / metrics

- **六个真实多变量数据**：SWaT、WADI、PSM（single entity）；MSL、SMAP、SMD（multi-entity）。另有合成 NeurIPS-TS，含 global/contextual point anomaly、shapelet/seasonal/trend pattern anomalies。（Table 1, §4.1, pp.4–6）
- **对照**：15 个公开 baseline，包含 statistical heuristic、deep reconstruction、GNN、Anomaly Transformer、TimesNet、NPSR 等；完整 Table 2。（§4.3, Table 2, p.5）
- **主指标**：AUC 和 point-adjusted F1；补充材料提供未 point-adjusted F1。最佳 threshold 从 F1 选择，需视为 test label oracle protocol。（§4.2–4.3, pp.4–6）
- **Multi-entity 对比**：作者以同一模型把 MSL / SMAP / SMD 的所有实体合并训练测试；部分 baselines 按 entity 单独训练后取平均，因此参数量 / entity-specific fitting 不完全同一 protocol。（§4.3, p.5）

#### 7.2 主结果

Table 2（PDF p.5）中作者报告在六个 real-world datasets 均达到当时最优 / 领先结果：SWaT F1 99.0、WADI 99.3、PSM 98.9、MSL 96.7、SMAP 98.2、SMD 97.7（单位 %）；single entity 平均比当时最佳 F1 提升约 1.7 percentage points，multi-entity 约 0.4 points。NeurIPS-TS synthetic Table 3（p.5）F1 为 86.6%，对比 Anomaly Transformer 77.5%。

这组数值依赖 PA 和 best-F1 threshold。作者附录 / supplementary 另报 no-point-adjustment F1，仍具竞争力，但主文标题性的 SOTA 结论不能与 TSB-AD 的 VUS-PR 直接拼接。（Tables 2–3; Supplementary）

#### 7.3 消融和敏感性

- **Mapping function（Table 5, p.7）**：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。
- **Sub-adjacent interval（Table 4, p.6）**：$k_1=20,k_2=30$ 通常表现较好（SMD 除外）；$k_1=k_2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。（§4.4）
- **模块 ablation（Table 6, pp.6–7）**：对其内部 baseline 加 linear attention 平均增益约 1.0 points，dynamic Gaussian scoring 再加约 .2；对 Anomaly Transformer 加相同两项也有增益。仅 sub-adjacent baseline 也平均比 Anomaly Transformer 高约 1.8 points。（§4.4）
- **窗口长度（Table 7, p.7）**：多个设置表现接近，100 通常较好，但 SWaT 最佳长度不同；并非一个完全消除窗口敏感性的结果。
- **Loss weight（Table 8, p.7）**：$\lambda=10$ 的六数据集综合表现较优；$\lambda=0$（移除 attention loss）性能明显降低。（§4.4）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations and Critical Reading

**方法假设**：异常相比正常更难由 target 的 sub-adjacent window 重建；若故障影响整段较大范围、合法状态突然切换，较远窗口本身也可能无法重建，分数没有来源区分能力。（§3.2, Eq. 5）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Circular boundary**：循环 shift 使窗口首尾位置成为环状邻居；这是平衡 attention contribution 的数学实现，未必符合真实时间序列边界语义。（Eqs. 2–3）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Global fixed band**：$k_1,k_2$ 和 window size 固定 / 手调；不同 sampling interval、周期长度、短异常可能需要不同 span。（Tables 4, 7）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Threshold protocol**：test-set best-F1 与 point adjustment 可提升汇报分数，不能等同于 validation-only streaming result。（§4.2）

#### 精读笔记原章节：9. Limitations and Critical Reading

**多实体 protocol**：作者的 pooled model 与部分逐实体 baseline 比较，不能把分数差全归因于 attention 新颖性。（§4.3）

#### 精读笔记原章节：9. Limitations and Critical Reading

**Dynamic Gaussian score 语义有限**：它用局部 score mean/std 重新标定，不利用 workload、service stage、release 或 Trace；未提供合法负载变更 + 故障并发实验。

#### 精读笔记原章节：9. Limitations and Critical Reading

**Attention 不是因果关系**：这是时间维重建 contribution，不是传感器 dependency graph 或故障 root cause。

#### 精读笔记原章节：9. Limitations and Critical Reading

paper 没有专门 Limitations section；以上边界来自其公式、数据 / metric、实验协议及实现假设的逐项分析。

### C. 仍缺乏证据的问题

未做的实验只标记为证据边界，不解释为方法不具备该能力。具体未充分验证项见上方原精读笔记限制章节。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 以周期 / workload context 自适应选择 band，比较合法状态变化与异常故障并发。
- **[分析推断]** 用 causal streaming boundary handling 替代 circular wrap，并测短异常的定位延迟。
- **[分析推断]** 固定告警预算和 range / event metric 下复核收益；验证 attention map 与 topology / Trace / fault injection 对齐。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **SARAD**：两者均重加权 Transformer attention evidence；SARAD 读取变量维 MHSA 关系的前后窗口变化，Sub-Adjacent 直接约束时间维 attention band 并乘 reconstruction error。
- **CrossAD**：关注 cross-scale / cross-window mapping prototypes；Sub-Adjacent 关注窗口内 target 周边的时间 attention geometry。
- **TFMAE / TriAD**：均用多种时序结构线索。TFMAE 双视图 representation discrepancy，TriAD 三域窗口筛选 + discord；Sub-Adjacent 是局部重建条件约束。
- **Quo Vadis / TSB-AD**：提醒 point adjustment 与 test best threshold 的比较边界；Sub-Adjacent 的主 F1 采用这两种高风险设定。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §1, §3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.1–3.2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.2, Fig. 1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.2 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | Eq. 2–3 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.3, Eq. 7 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §1, §3.2 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | Eqs. 1–7, Fig. 1 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.2, Eq. 1, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | Eq. 2, Eq. 3, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.2, Eq. 4, Fig. 4 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.3, Eq. 5 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §3.3, Eqs. 6–7 | 精读笔记保留的原文定位 |
| Method / formulas | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.2 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.1, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.3, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.2–4.3 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.3 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | PDF p.5, Table 2, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | Eq. 4, Table 5 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.4, Table 4 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | §4.4, Table 6 | 精读笔记保留的原文定位 |
| Experimental evidence | Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf | Table 7 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "sub-adjacent-transformer",
  "title_en": "Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods",
  "title_zh": "Sub-Adjacent Transformer：从非相邻邻域重建误差改进时间序列异常检测",
  "authors": [
    "Wenzhen Yue",
    "Xianghua Ying",
    "Ruohao Guo",
    "DongDong Chen",
    "Ji Shi",
    "Bowei Xing",
    "Yuqing Zhu",
    "Taiyan Chen"
  ],
  "year": 2024,
  "venue": "IJCAI",
  "ccf_level": "B",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2024/IJCAI/Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
  "reading_note_path": "papers/sub-adjacent-transformer/notes.md",
  "code_url": "https://github.com/jackyue1994/sub_adjacent_transformer",
  "research_area": "非相邻时间邻域重建式异常检测",
  "method_tags": [
    "TSAD Transformer linear attention sub-adjacent context reconstruction dynamic Gaussian scoring point adjustment"
  ],
  "research_scenario": "- [作者主张] 无监督多变量重建 TSAD：防止异常从 immediate neighbors 被直接重建。（§3.2, pp.2–3） - [实验支持] SWaT/WADI/PSM/MSL/SMAP/SMD 及合成 NeurIPS-TS。（Tables 1–3, pp.4–5）",
  "research_problem": "经典重建型 TSAD 常使用滑窗内所有点重建目标时间点。作者观察到，连续数据中的点通常与紧邻点相似，异常附近的紧邻观测尤其可能帮助重建异常本身；如果重建只读距离至少 $k1$ 且不超过 $k2$ 的 sub-adjacent neighborhoods，正常点仍能从较远邻域恢复，而异常重建会更难，残差可能变大。（§1, §3.2, pp.1–3） 任务为多变量时间序列 $X\\in\\mathbb R^{T\\times N}$ 逐时间点无监督重建和标签预测。核心不是对通道间关系建真实因果图，而是约束 Transformer 的时间 attention map：attention 值被视为一个时间点对另一个时间点重建表示的贡献。（§3.1–3.2, pp.2–3）",
  "core_challenges": [
    "紧邻复制会遮蔽异常：如果 target anomaly 与 immediate neighbors 同处异常段，使用邻近上下文重建会降低 residual。（§3.2, Fig. 1, pp.2–3）",
    "attention 形状难用 vanilla softmax 控制：标准 row-wise softmax 使同一行竞争，不易形成需要的非对角 sub-adjacent band。（§3.2, Figs. 2–4, pp.3–4）",
    "滑窗边界的可用邻居数不平衡：窗头 / 窗尾距指定 band 的点较少，attention contribution 会系统性偏低；论文用 circular index shift 平衡各列。（Eq. 2–3）",
    "单一 residual 的 score scale 会动态变化：作者加入滑动 mean / std 的 dynamic Gaussian score 转换。（§3.3, Eq. 7）"
  ],
  "existing_method_limits": [
    "[作者主张] 依赖所有局部邻域的重建模型可能学会异常模式。（§1, §3.2）",
    "[分析推断] 全局固定 sub-adjacent span 不能识别它对应的是合法状态变化还是故障。"
  ],
  "core_idea": "Sub-Adjacent Transformer 将目标点的重建上下文限制在距离 $[k1,k2]$ 的非紧邻时间点，使异常较难从最近邻直接复制；用 circularly constructed sub-adjacent attention contribution 最大化该范围权重，与重建误差组合为 anomaly score，并通过可学习 map 的 linear attention 和动态 Gaussian score 改善表示与尺度适应。（§3, Eqs. 1–7, PDF pp.2–4）",
  "technical_innovations": [
    {
      "name": "Sub-adjacent contribution",
      "author_claim": "**[作者主张] Sub-adjacent contribution**：对 attention map 目标列累加指定距离 band。（Eq. 1, p.3）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.1 Sub-adjacent attention contribution",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "**[实验支持]** sub-adjacent distance、window size、lambda、attention mapping 和 dynamic scoring 均有 ablation / sensitivity 表。（Tables 4–8）",
      "component_level_evidence_status": "论文相关组件比较，具体范围仅限其实际比较的数据集与指标。",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Sub-adjacent contribution**：对 attention map 目标列累加指定距离 band。（Eq. 1, p.3）"
    },
    {
      "name": "Circular index construction",
      "author_claim": "**[作者主张] Circular index construction**：平衡窗口两端的有效 neighbor 数量。（Eqs. 2–3, p.3）",
      "challenge_ids": [
        "C3",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Circular shift 和 learnable linear attention",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Circular index construction**：平衡窗口两端的有效 neighbor 数量。（Eqs. 2–3, p.3）"
    },
    {
      "name": "Learnable linear mapping",
      "author_claim": "**[作者主张] Learnable linear mapping**：$\\Phi(U)=Softmax_{row}(U/g)$ 并用 $\\Phi(Q)\\Phi(K)^T V$ 得到灵活 band map。（Eq. 4, p.4）",
      "challenge_ids": [
        "C4",
        "C3"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.2 Circular shift 和 learnable linear attention",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Learnable linear mapping**：$\\Phi(U)=Softmax_{row}(U/g)$ 并用 $\\Phi(Q)\\Phi(K)^T V$ 得到灵活 band map。（Eq. 4, p.4）"
    },
    {
      "name": "Joint score",
      "author_claim": "**[作者主张] Joint score**：优化 $\\|X-\\hat X\\|^2-\\lambda\\|SACon\\|_1$；推理点 score 为 softmax(-SACon) 与重建误差相乘，再做 dynamic Gaussian tail transform。（Eqs. 5–7）",
      "challenge_ids": [
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.4 Reconstruction-weighted anomaly score",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "同一组件消融已在本节前项列出；该结果为组合 / 累积比较，不单独证明本模块的增量效果（第9节）。",
      "component_level_evidence_status": "共享证据，避免重复归因",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Joint score**：优化 $\\|X-\\hat X\\|^2-\\lambda\\|SACon\\|_1$；推理点 score 为 softmax(-SACon) 与重建误差相乘，再做 dynamic Gaussian tail transform。（Eqs. 5–7）"
    }
  ],
  "methodology": {
    "architecture": "text 多变量窗口 X ∈ R^(W×N) ├─ Q,K,V 与 sub-adjacent linear attention │ ├─ Φ(Q), Φ(K) 用带 learnable temperature 的 row-softmax mapping │ └─ attention contribution 集中在 k1…k2 距离 band（circular wrap） ├─ Transformer reconstruction → X̂ ├─ 训练目标：||X−X̂||² − λ ||SACon(A)||₁ ├─ point score：softmax(−SACon(A)) ⊙ point reconstruction error └─ 对 score 做滑动 dynamic Gaussian tail transform → threshold label （Fig. 1–5, Eqs. 1–7, pp.2–5）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 Sub-adjacent attention contribution",
      "6.2 Circular shift 和 learnable linear attention",
      "6.3 联合重建与 attention loss",
      "6.4 Reconstruction-weighted anomaly score",
      "6.5 参数和训练"
    ],
    "key_formulas": [
      "Eq. (1)",
      "Eq. (2)",
      "Eq. (3)",
      "Eq. (4)",
      "Eq. (5)",
      "Eq. (6)"
    ],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "Sub-Adjacent Transformer 将目标点的重建上下文限制在距离 $[k1,k2]$ 的非紧邻时间点，使异常较难从最近邻直接复制；用 circularly constructed sub-adjacent attention contribution 最大化该范围权重，与重建误差组合为 anomaly score，并通过可学习 map 的 linear attention 和动态 Gaussian score 改善表示与尺度适应。（§3, Eqs. 1–7, PDF pp.2–4）"
  },
  "experimental_evidence": {
    "datasets": [
      "### 7.1 Dataset / baselines / metrics",
      "Table 2（PDF p.5）中作者报告在六个 real-world datasets 均达到当时最优 / 领先结果：SWaT F1 99.0、WADI 99.3、PSM 98.9、MSL 96.7、SMAP 98.2、SMD 97.7（单位 %）；single entity 平均比当时最佳 F1 提升约 1.7 percentage points，multi-entity 约 0.4 points。NeurIPS-TS synthetic Table 3（p.5）F1 为 86.6%，对比 Anomaly Transformer 77.5%。",
      "- Mapping function（Table 5, p.7）：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。 - Sub-adjacent interval（Table 4, p.6）：$k1=20,k2=30$ 通常表现较好（SMD 除外）；$k1=k2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。…"
    ],
    "baselines": [
      "### 7.1 Dataset / baselines / metrics",
      "- 六个真实多变量数据：SWaT、WADI、PSM（single entity）；MSL、SMAP、SMD（multi-entity）。另有合成 NeurIPS-TS，含 global/contextual point anomaly、shapelet/seasonal/trend pattern anomalies。（Table 1, §4.1, pp.4–6） - 对照：15 个公开 baseline，包含 statistical heuristic、deep reconstruction、GNN、Anomaly Transformer、TimesNet、NPSR 等；完整 Table 2。…",
      "- Mapping function（Table 5, p.7）：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。 - Sub-adjacent interval（Table 4, p.6）：$k1=20,k2=30$ 通常表现较好（SMD 除外）；$k1=k2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。…"
    ],
    "metrics": [
      "### 7.1 Dataset / baselines / metrics",
      "- 六个真实多变量数据：SWaT、WADI、PSM（single entity）；MSL、SMAP、SMD（multi-entity）。另有合成 NeurIPS-TS，含 global/contextual point anomaly、shapelet/seasonal/trend pattern anomalies。（Table 1, §4.1, pp.4–6） - 对照：15 个公开 baseline，包含 statistical heuristic、deep reconstruction、GNN、Anomaly Transformer、TimesNet、NPSR 等；完整 Table 2。…",
      "Table 2（PDF p.5）中作者报告在六个 real-world datasets 均达到当时最优 / 领先结果：SWaT F1 99.0、WADI 99.3、PSM 98.9、MSL 96.7、SMAP 98.2、SMD 97.7（单位 %）；single entity 平均比当时最佳 F1 提升约 1.7 percentage points，multi-entity 约 0.4 points。NeurIPS-TS synthetic Table 3（p.5）F1 为 86.6%，对比 Anomaly Transformer 77.5%。",
      "这组数值依赖 PA 和 best-F1 threshold。作者附录 / supplementary 另报 no-point-adjustment F1，仍具竞争力，但主文标题性的 SOTA 结论不能与 TSB-AD 的 VUS-PR 直接拼接。（Tables 2–3; Supplementary）"
    ],
    "main_results": [
      "- 六个真实多变量数据：SWaT、WADI、PSM（single entity）；MSL、SMAP、SMD（multi-entity）。另有合成 NeurIPS-TS，含 global/contextual point anomaly、shapelet/seasonal/trend pattern anomalies。（Table 1, §4.1, pp.4–6） - 对照：15 个公开 baseline，包含 statistical heuristic、deep reconstruction、GNN、Anomaly Transformer、TimesNet、NPSR 等；完整 Table 2。（§4.3, Table 2, p.5） - 主指标：AUC 和 point-adjusted F1；…",
      "### 7.2 主结果",
      "Table 2（PDF p.5）中作者报告在六个 real-world datasets 均达到当时最优 / 领先结果：SWaT F1 99.0、WADI 99.3、PSM 98.9、MSL 96.7、SMAP 98.2、SMD 97.7（单位 %）；single entity 平均比当时最佳 F1 提升约 1.7 percentage points，multi-entity 约 0.4 points。NeurIPS-TS synthetic Table 3（p.5）F1 为 86.6%，对比 Anomaly Transformer 77.5%。",
      "这组数值依赖 PA 和 best-F1 threshold。作者附录 / supplementary 另报 no-point-adjustment F1，仍具竞争力，但主文标题性的 SOTA 结论不能与 TSB-AD 的 VUS-PR 直接拼接。（Tables 2–3; Supplementary）",
      "- Mapping function（Table 5, p.7）：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。 - Sub-adjacent interval（Table 4, p.6）：$k1=20,k2=30$ 通常表现较好（SMD 除外）；$k1=k2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。（§4.4） - 模块 ablation（Table 6, pp.6–7）：对其内部 baseline 加 linear attention 平均增益约 1.0 points，…"
    ],
    "ablations": [
      "### 7.3 消融和敏感性",
      "- Mapping function（Table 5, p.7）：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。 - Sub-adjacent interval（Table 4, p.6）：$k1=20,k2=30$ 通常表现较好（SMD 除外）；$k1=k2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。…"
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
      "方法假设：异常相比正常更难由 target 的 sub-adjacent window 重建；若故障影响整段较大范围、合法状态突然切换，较远窗口本身也可能无法重建，分数没有来源区分能力。（§3.2, Eq. 5）",
      "Circular boundary：循环 shift 使窗口首尾位置成为环状邻居；这是平衡 attention contribution 的数学实现，未必符合真实时间序列边界语义。（Eqs. 2–3）",
      "Global fixed band：$k1,k2$ 和 window size 固定 / 手调；不同 sampling interval、周期长度、短异常可能需要不同 span。（Tables 4, 7）",
      "Threshold protocol：test-set best-F1 与 point adjustment 可提升汇报分数，不能等同于 validation-only streaming result。（§4.2）",
      "多实体 protocol：作者的 pooled model 与部分逐实体 baseline 比较，不能把分数差全归因于 attention 新颖性。（§4.3）",
      "Dynamic Gaussian score 语义有限：它用局部 score mean/std 重新标定，不利用 workload、service stage、release 或 Trace；未提供合法负载变更 + 故障并发实验。",
      "Attention 不是因果关系：这是时间维重建 contribution，不是传感器 dependency graph 或故障 root cause。",
      "paper 没有专门 Limitations section；以上边界来自其公式、数据 / metric、实验协议及实现假设的逐项分析。"
    ],
    "evidence_gaps": [
      "未报告的环境属于证据不足，不等于方法能力不足"
    ]
  },
  "research_implications": [
    "- [分析推断] 以周期 / workload context 自适应选择 band，比较合法状态变化与异常故障并发。 - [分析推断] 用 causal streaming boundary handling 替代 circular wrap，并测短异常的定位延迟。 - [分析推断] 固定告警预算和 range / event metric 下复核收益；验证 attention map 与 topology / Trace / fault injection 对齐。"
  ],
  "related_papers": [
    {
      "paper_id": "crossad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "triad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tfmae",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "sarad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§1, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.1–3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.2, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "Eq. 2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.3, Eq. 7",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§1, §3.2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "Eqs. 1–7, Fig. 1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.2, Eq. 1, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "Eq. 2, Eq. 3, Fig. 3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf",
      "locator": "§3.2, Eq. 4, Fig. 4",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "ef9392552aa5a92612b63ae01f2b282603144ce64be66137da8504e5acc92621",
    "reading_note_sha256": "44bd4432b39f045fe7ab8c2e12397e48d4703a98e54a52509095befa20b712e8",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "e6138adba938c66d04062367ec66fc429b32a0862a90cf1df26332450269f54b"
  },
  "knowledge_card_path": "papers/sub-adjacent-transformer/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
