# FlowFuse: Multi-View Ensemble for Time Series Anomaly Detection via Coupling Flows

## 1. Metadata

- **Authors**: Wanghui Qiu, Chenxi Liu, Shiyan Hu, Zhengyu Li, Chenjuan Guo, Bin Yang
- **Year / venue**: 2026 / IJCAI (CCF B，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2026/IJCAI/Multi_View_Ensemble_for_Time_Series_Anomaly_Detection_via_Coupling_Flows.pdf)
- **Proceedings**: IJCAI-26, pp. 2987–2995 (PDF 1–9)
- **Code**: [FlowFuse repository](https://github.com/decisionintelligence/FlowFuse)
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

FlowFuse 用 temporal/frequency × clustering/reconstruction 构造四路逐变量异常分数，再以多层、双向交替的 affine coupling flows 学习这些分数在正常训练数据下的联合分布；flow ensemble 的经验百分位分数经无监督平均路由器融合，也可将分歧当作不确定性，在有少量标签时训练选择性路由器。（§§3.2–3.5, Eqs. 1–9, PDF pp. 3–5）

## 3. 背景与问题定义

作者将困难分成两部分。第一，异常形态不同：point/global/contextual 异常、seasonal、trend、shapelet 和混合异常可能分别在时域、频域、聚类距离或重建误差中显现。单个 detector 的归纳偏置会使它在某些异常类型上有效、在另一些类型上失效。第二，即使已有多路分数，平均、最大值或固定加权也没有学习 view 之间的非线性交互；MLP 可拟合交互，却没有显式地把“正常分数组合”当作可计算的密度分布。（§1, §2.1–2.2, §3.4, PDF pp. 1–4）

任务假定训练时间序列代表正常行为，测试阶段输出逐时刻异常判断。方法首先产生多个 detection view 的分数，之后在 score space 而不是原始序列空间做无监督密度建模。（§3.1–3.2）这里“正常”仍由训练 score 分布定义，并非业务状态或因果语义的定义。

## 4. 整体架构

```text
滑动窗口 W_i (默认长度 50、步长 1) + 标准化
  ├─ Temporal K-means distance (C=24)
  ├─ Temporal inverted-token Transformer reconstruction
  ├─ Frequency K-means distance on FFT magnitude (C=24)
  └─ Frequency Transformer reconstruction (magnitude + phase)
        ↓ overlap window scores → point-level average
逐时刻、逐变量四视角 score S_t ∈ R^(d×4)
        ↓ 训练集内逐变量标准化
E 个 coupling flow (默认 E=4, L_c=2)，交替更新 temporal / frequency score
        ↓ 各 flow 对正常 score 联合分布建模，likelihood 转经验百分位异常分
无监督：ensemble average router
半监督：取高分歧 top-K 样本，用 pairwise ranking loss 学 router
```

## 5. 方法细节

### 5.1 四路视角与窗口分数

对标准化序列用长度 $W$、步长 $s$ 的滑动窗口；默认 $W=50,s=1$，论文也提到可依 FFT 周期性自动定窗，或依据领域知识设定。（§3.3, PDF p. 3）四个 detector 是：

1. **Temporal clustering**：在训练窗口上用 K-means 学 $C=24$ 个代表模式；测试窗口到最近中心的 Euclidean distance 作为异常证据。强调离已见模式的全局 / 新颖偏离。
2. **Temporal reconstruction**：inverted-tokenization Transformer 以变量为 token，重建正常时域依赖，重建误差为分数。
3. **Frequency clustering**：对窗口作 FFT，在 magnitude spectrum 上聚类，最近中心距离测未见谱型。
4. **Frequency reconstruction**：专用 Transformer 直接重建频域表示，同时输入 magnitude 和 phase，关注周期断裂、harmonic distortion 和异常频率分量。（§3.3, PDF pp. 3–4）

四路窗口分数对包含同一时刻的所有重叠窗口取平均：

$$s_t^{(v)}=\frac{1}{|W_t|}\sum_{w\in W_t}s_w^{(v)},\quad v\in\{1,2,3,4\}. \tag{1}$$

由此得到 $S_t\in\mathbb R^{d\times4}$，并按视角分成 temporal $T_t=S_t[:,1:2]$ 和 frequency $F_t=S_t[:,3:4]$ 两组。作者的设计假设是 point/local contextual 更易在时域显现，季节性与谐波异常更易在频域显现；clustering 对全局离群 / 新型模式敏感，reconstruction 对局部细微偏离敏感。这是视角设计动机，不能推成严格的一一异常类型映射。（§3.3）

### 5.2 交替 coupling flow 学习跨视角依赖

传统平均、max、学习权重将分数视为相互独立；普通 MLP 虽能学习非线性交互，却没有 flow 的可逆变换和显式 likelihood。FlowFuse 逐变量将四路分数标准化为零均值、单位方差，接着用 coupling flow $f_e:\mathbb R^{d\times4}\to\mathbb R^{d\times4}$ 把训练 score 联合分布变换到标准高斯潜变量。（Table 1; §3.4, PDF pp. 4–5）

每层把 $T,F$ 划分作条件 affine update。先以 temporal scores 更新 frequency：

$$T_t^{(\ell+1/2)}=T_t^{(\ell)},\quad F_t^{(\ell+1/2)}=F_t^{(\ell)}\odot\exp s_\theta(T_t^{(\ell)})+t_\theta(T_t^{(\ell)}). \tag{2}$$

再用已更新的 $F$ 更新 temporal：

$$F_t^{(\ell+1)}=F_t^{(\ell+1/2)},\quad T_t^{(\ell+1)}=T_t^{(\ell+1/2)}\odot\exp s_\phi(F_t^{(\ell+1/2)})+t_\phi(F_t^{(\ell+1/2)}). \tag{3}$$

交替顺序使两组 view 可双向条件化：模型可以学到“某时域分数高而频域分数低”与“两类分数同时中等”分别是否符合正常联合 score pattern，而非假定每一路需独立越阈值。堆叠 $L_c$ 个 block 得 $z_t=f_e(S_t)$。（Eqs. 2–4）

每个 ensemble flow 独立优化标准高斯潜空间下的负对数似然：

$$\mathcal L_{flow}^{(e)}=\frac1N\sum_t\left[\frac12\|z_t^{(e)}\|_F^2-\log|\det J_{f_e}(S_t)|\right]. \tag{5}$$

默认 $E=4,L_c=2$；flow 使用不同随机初始化和数据子集以形成 ensemble 多样性。训练时存储各 flow 的 likelihood 分布，测试时以相对于该训练分布的经验百分位转成 $r_e(S_t)\in[0,1]$（Eq. 6）。该百分位方向按论文定义，是测试 likelihood 大于训练 likelihood 的比例，并需结合代码核对其异常方向与实现约定。

### 5.3 无监督融合、不确定性与可选半监督路由

无监督默认使用简单均值：

$$\bar r(S_t)=\frac1E\sum_{e=1}^E r_e(S_t). \tag{7}$$

不同 flow 的分数方差 $u_t=\operatorname{Var}_{e=1}^E[r_e(S_t)]$ 作为 ensemble disagreement uncertainty。若存在标签，取不确定性最高的 $K=\lceil p_{train}N_{train}\rceil$ 个样本，由轻量网络 $g_\psi$ 生成 softmax router 权重 $w_e$（Eq. 8），并在异常-正常标签对上使用 pairwise ranking loss（Eq. 9）训练融合分数。论文展示 1–5% 标签通常已带来收益，之后趋于饱和。（§3.5, §4.4, Table 6, PDF pp. 5, 7）

**解释边界**：flow 学到的是四种 detector score 的联合统计结构，不直接解释指标变化的业务来源。ensemble 分歧是经验不确定性代理，论文并未声称它是经过概率校准的 epistemic uncertainty 或可用于风险保证的置信区间。

## 6. 实验设计与结果

### 6.1 数据、基线、指标

18 个基准：10 个 UTS、8 个 MTS，涉及航天器、服务器、健康、生理、运动、工业、交通及多领域集合；维度 1–55，序列平均长度约 785–1,416,825，异常率约 0.20%–15.57%。（§4.1, Table 2, PDF p. 5）基线含 18 个方法，覆盖统计分布、重建、判别式；使用 TAB 统一评估，不同 UTS / MTS 各用一组共享超参，而非按每个数据集分别调参。指标为 Affiliated F1 与 AUROC。（§4.1, Table 4）

### 6.2 主结果及其边界

- **[实验支持]** 作者报告 FlowFuse 在多数基准取得最佳结果，尤其在 LTDB、MITDB、NYC、SVDB 等 MTS 上较强；原文称 18 个数据集总体稳定，但不是所有表格单元都第一。（§4.2, Table 3, PDF p. 6）
- **[实验支持]** 按 6 类异常分组比较 35 种方法：深度方法对 global/contextual 点异常较强，KMeans/DWT/HBOS 等统计方法在 seasonal/shapelet 子序列上较强；各方法在 mixed anomalies 上整体较弱。（§4.4, Fig. 2, PDF p. 7）
- **[作者主张 + 实验支持]** coupling-flow 融合相对简单平均平均提升约 8.0%；四个 view 都有贡献，temporal views 在多数被测集上影响较大。（§4.3, Table 5）
- **[实验支持]** cluster 数 $C=8$–32 对大多数数据集变化小于 3%；ensemble size 从 2 增至 4 有提升，之后趋于饱和，故默认 $C=24,E=4$。（§4.4, Fig. 3）
- **[实验支持]** 在 NAB、SVDB、YAHOO、LTDB 上可选监督学习显示 1–5% 标签已提高 AUROC，继续增加标签收益减小。（Table 6）

### 6.3 消融和复现边界

消融支持“learned joint score distribution 有价值”，但其报告为四个代表数据集的 Aff-F1，而非所有任务 / 固定 FPR 下的普遍因果结论。（Table 5）共享 UTS / MTS 超参降低数据集级调参程度，但整体 pipeline 仍包括 K-means、Transformer、窗口、训练 score 标准化、经验百分位和最终 threshold；跨域运行点和在线更新没有在本文统一验证。作者未提供专项 limitation section；以上边界属于按实验设计和方法假设作的分析。

## 7. 技术贡献、局限与复现价值

### 技术贡献

1. 把时域 / 频域和 clustering / reconstruction 作为两条正交视角，生成互补而可对比的 anomaly score。（§3.3）
2. 以可逆 affine coupling 建模正常多视角分数的联合密度，显式捕捉 score 之间的非线性交互。（§3.4, Eqs. 2–6）
3. 将 ensemble disagreement 用于选取有限标签的模糊样本，再进行可选 ranking-based routing。（§3.5）

### 局限和审慎解读

- **[分析推断]** 四路 view 若在同一状态切换或同类故障上共同失效，后续 flow 只能融合已有错误证据，不能恢复缺失的信息。
- **[分析推断]** 用训练 score 分布定义 normality 仍依赖训练集主要为正常、标准化 / windowing 适当、且数据分布足够稳定；新合法负载状态可能导致多路分数一起偏离。
- **[分析推断]** 时间与频率两组不是独立来源，DFT 的窗口泄漏、相位表示和周期变化可能影响联合 score；正文未对 workload shift × fault 并发或真实 Trace / release context 作专门对照。
- Ensemble variance 只量化成员之间的分歧，不证明已校准；论文也未证明 score fusion 能解释 anomaly cause。
- 论文讨论 mixed anomalies 难度仍高（Fig. 2(f)），显示多 view 的互补性不是覆盖所有异常组合的保证。

### 开源与复现

官方仓库公开。复现要对齐 TAB 数据划分、窗口默认值、聚类数、两个 Transformer score 的构造和 point aggregation、score 标准化、flow 结构 / ensemble seeds、训练 score 百分位映射、threshold 及 Aff-F 评估协议；检查不同版本数据是否含训练异常（Table 2 中部分 train AR 非零）。本次只读 PDF 和笔记，未运行代码或训练。

## 8. 与知识库论文的关系

- **TFC / TriAD / TFMAE / MACE**：都结合 temporal-frequency 证据；FlowFuse 的主要新意在 score-space 的联合概率融合，而不是统一的双域 encoder。
- **COGNOS**：也从多个统计分数/不确定性形成检测判断；COGNOS 用 innovation 与 Kalman residual filter，FlowFuse 用四个异质 detector 的联合 score density。
- **CAPMix / Graph-MoE / WMMNN**：显式分组、多模式参考或不同专家侧重正常模式；FlowFuse 面向 detector score pattern，不建立业务状态标签。
- **AnoMamba / KAN-AD / RTdetector**：改造重建机制或其依赖；FlowFuse 把重建作为四路证据之一，且结合 clustering / FFT view。
- **CNF latent dynamics**：两者均使用 density / flow 类模型，但 FlowFuse 在 detector-score space 学多视角 normal density；CNF 在原始时序到 latent-space 后显式规定时间演化，并用 GOF 检验 compliance。
