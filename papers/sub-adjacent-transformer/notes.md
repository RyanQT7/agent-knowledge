# Sub-Adjacent Transformer: Improving Time Series Anomaly Detection with Reconstruction Error from Sub-Adjacent Neighborhoods

## 1. Metadata

- **Authors**: Wenzhen Yue, Xianghua Ying, Ruohao Guo, DongDong Chen, Ji Shi, Bowei Xing, Yuqing Zhu, Taiyan Chen
- **Year / Venue**: 2024 / IJCAI（CCF B，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf)
- **Official proceedings**: [IJCAI 2024, paper 0279](https://www.ijcai.org/proceedings/2024/0279.pdf)
- **Code**: [Sub-Adjacent Transformer repository](https://github.com/jackyue1994/sub_adjacent_transformer)
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

Sub-Adjacent Transformer 将目标点的重建上下文限制在距离 $[k_1,k_2]$ 的非紧邻时间点，使异常较难从最近邻直接复制；用 circularly constructed sub-adjacent attention contribution 最大化该范围权重，与重建误差组合为 anomaly score，并通过可学习 map 的 linear attention 和动态 Gaussian score 改善表示与尺度适应。（§3, Eqs. 1–7, PDF pp.2–4）

## 3. Background and Problem Definition

经典重建型 TSAD 常使用滑窗内所有点重建目标时间点。作者观察到，连续数据中的点通常与紧邻点相似，异常附近的紧邻观测尤其可能帮助重建异常本身；如果重建只读距离至少 $k_1$ 且不超过 $k_2$ 的 **sub-adjacent neighborhoods**，正常点仍能从较远邻域恢复，而异常重建会更难，残差可能变大。（§1, §3.2, pp.1–3）

任务为多变量时间序列 $X\in\mathbb R^{T\times N}$ 逐时间点无监督重建和标签预测。核心不是对通道间关系建真实因果图，而是约束 Transformer 的**时间 attention map**：attention 值被视为一个时间点对另一个时间点重建表示的贡献。（§3.1–3.2, pp.2–3）

## 4. Core Challenges

1. **紧邻复制会遮蔽异常**：如果 target anomaly 与 immediate neighbors 同处异常段，使用邻近上下文重建会降低 residual。（§3.2, Fig. 1, pp.2–3）
2. **attention 形状难用 vanilla softmax 控制**：标准 row-wise softmax 使同一行竞争，不易形成需要的非对角 sub-adjacent band。（§3.2, Figs. 2–4, pp.3–4）
3. **滑窗边界的可用邻居数不平衡**：窗头 / 窗尾距指定 band 的点较少，attention contribution 会系统性偏低；论文用 circular index shift 平衡各列。（Eq. 2–3）
4. **单一 residual 的 score scale 会动态变化**：作者加入滑动 mean / std 的 dynamic Gaussian score 转换。（§3.3, Eq. 7）

## 5. Architecture Overview

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

## 6. Method in Detail

### 6.1 Sub-adjacent attention contribution

对窗口 attention matrix $A$，作者把第 $i$ 列理解为第 $i$ 个 target point 对其他点的 attention contribution。指定 $0<k_1\le k_2$；该列离对角线距离满足 $k_1\le |j-i|\le k_2$ 的 attention 值累加，得到逐点 sub-adjacent contribution：

$$\mathrm{SACon}(A)_{i}=\sum_{j:\ k_1\le |j-i|\le k_2} A_{j,i}. \tag{1}$$

如此排除 target 的自身 / 紧邻点，又只使用局部而非整窗远距离 points。正常点应有足够来自 sub-adjacent 周边的 contribution；异常被其紧邻上下文遮蔽的机会减少。（§3.2, Fig. 2, Eq. 1, p.3）

### 6.2 Circular shift 和 learnable linear attention

若只在矩阵内部求 band，窗口边缘列可参与贡献的 cell 较少。作者通过 cyclic roll $Q$ 构造 attention element（Eq. 2），使索引环绕；等价实现按 Eq. 3 用 circular index 计算 SACon，形成 attention map 的两条额外 side stripes（Fig. 3, p.3）。这均衡列 contribution，但把窗口两端视为循环邻接，是实现上的边界先验。

使用 linear attention：

$$\mathrm{Attn}(Q,K,V)=\Phi(Q)\Phi(K)^\top V,$$

其中映射函数为 row-wise temperature-scaled Softmax：

$$\Phi(U)=\mathrm{Softmax}_{row}(U/g). \tag{4}$$

$g$ 是 learnable 参数；$Q,K$ 中负值先设成约 $-100$，避免通过 row-softmax 变为正权。它不同于 vanilla self-attention 对 $QK^\top$ 结果做 Softmax；对 $Q,K$ 单独作 mapping 使 attention map 更灵活，可调整到预期的 band 形状。（§3.2, Fig. 4, Eq. 4, p.4）

### 6.3 联合重建与 attention loss

总 loss 由数据重建项和鼓励 sub-adjacent attention 的项构成：

$$\mathcal L_{Total}(X,\hat X,A)=\|X-\hat X\|_F^2-\lambda\|\mathrm{SACon}(A)\|_1. \tag{5}$$

优化时最小化 reconstruction error，同时最大化所有点在有效 sub-adjacent region 的贡献；$\lambda>0$ 平衡两项。直觉是让模型按假设的时间 band 重建，而不靠相邻 target values。若某正常状态变化本身无法由这段较远上下文恢复，目标也会增加其 score。（§3.3, Eq. 5, p.4）

### 6.4 Reconstruction-weighted anomaly score

先用 $\mathrm{Softmax}(-\mathrm{SACon}(A))$ 为低 attention contribution 的时刻分配更高权重，再逐点乘以 multivariate reconstruction error：

$$\mathrm{AnomalyScore}_i=\mathrm{Softmax}(-\mathrm{SACon}(A))_i\times\|X_{:,i}-\hat X_{:,i}\|_2^2. \tag{6}$$

即异常要同时具备较高重建误差和较低 sub-adjacent contribution 才能获得较高 score。随后在 score 上估计滑动动态 mean $\mu_i$ 和 standard deviation $\sigma_i$，用 Gaussian CDF 上尾概率做变换：

$$\mathrm{DyAnoSco}_i=-\log\left(1-\mathrm{cdf}\left(\frac{\mathrm{AnomalyScore}_i-\mu_i}{\sigma_i}\right)\right). \tag{7}$$

该动态分布转换用于将 score 映射成相对局部 background 的 tail likelihood；是否能在未见合法状态变化时避免误报取决于 local score distribution 的适配与阈值。（§3.3, Eqs. 6–7, pp.4–5）

### 6.5 参数和训练

- 窗口非重叠划分，默认 window size 100；$k_1=20, k_2=30$。
- 3 层 Transformer，$d_{model}=512$、8 heads，$\lambda=10$。
- Adam，初始学习率 $10^{-4}$，batch size 128，10 epochs 内 early stopping。
- Threshold 按 test best-F1 选择；主报告使用 point adjustment。（§4.2, pp.4–5）

## 7. Experimental Design and Evidence

### 7.1 Dataset / baselines / metrics

- **六个真实多变量数据**：SWaT、WADI、PSM（single entity）；MSL、SMAP、SMD（multi-entity）。另有合成 NeurIPS-TS，含 global/contextual point anomaly、shapelet/seasonal/trend pattern anomalies。（Table 1, §4.1, pp.4–6）
- **对照**：15 个公开 baseline，包含 statistical heuristic、deep reconstruction、GNN、Anomaly Transformer、TimesNet、NPSR 等；完整 Table 2。（§4.3, Table 2, p.5）
- **主指标**：AUC 和 point-adjusted F1；补充材料提供未 point-adjusted F1。最佳 threshold 从 F1 选择，需视为 test label oracle protocol。（§4.2–4.3, pp.4–6）
- **Multi-entity 对比**：作者以同一模型把 MSL / SMAP / SMD 的所有实体合并训练测试；部分 baselines 按 entity 单独训练后取平均，因此参数量 / entity-specific fitting 不完全同一 protocol。（§4.3, p.5）

### 7.2 主结果

Table 2（PDF p.5）中作者报告在六个 real-world datasets 均达到当时最优 / 领先结果：SWaT F1 99.0、WADI 99.3、PSM 98.9、MSL 96.7、SMAP 98.2、SMD 97.7（单位 %）；single entity 平均比当时最佳 F1 提升约 1.7 percentage points，multi-entity 约 0.4 points。NeurIPS-TS synthetic Table 3（p.5）F1 为 86.6%，对比 Anomaly Transformer 77.5%。

这组数值依赖 PA 和 best-F1 threshold。作者附录 / supplementary 另报 no-point-adjustment F1，仍具竞争力，但主文标题性的 SOTA 结论不能与 TSB-AD 的 VUS-PR 直接拼接。（Tables 2–3; Supplementary）

### 7.3 消融和敏感性

- **Mapping function（Table 5, p.7）**：Eq. 4 的 learnable row-softmax mapping 在六数据集上优于 vanilla self-attention、column-softmax、power、ReLU 和 ELU+1 中大多数设置，最多 F1 差异约 1.5 points。
- **Sub-adjacent interval（Table 4, p.6）**：$k_1=20,k_2=30$ 通常表现较好（SMD 除外）；$k_1=k_2=0$ 时结果大幅下降，支持排除紧邻 target 的设计。（§4.4）
- **模块 ablation（Table 6, pp.6–7）**：对其内部 baseline 加 linear attention 平均增益约 1.0 points，dynamic Gaussian scoring 再加约 .2；对 Anomaly Transformer 加相同两项也有增益。仅 sub-adjacent baseline 也平均比 Anomaly Transformer 高约 1.8 points。（§4.4）
- **窗口长度（Table 7, p.7）**：多个设置表现接近，100 通常较好，但 SWaT 最佳长度不同；并非一个完全消除窗口敏感性的结果。
- **Loss weight（Table 8, p.7）**：$\lambda=10$ 的六数据集综合表现较优；$\lambda=0$（移除 attention loss）性能明显降低。（§4.4）

## 8. Contributions and Reproduction Value

1. 提出时间 attention sub-adjacent band，限制模型直接依赖 target 的紧邻点。（§3.2）
2. 以 circular indexing、linear attention 和 learnable row-softmax mapping 实现可控非对角 attention map。（Eqs. 2–4）
3. 将 attention contribution 与 reconstruction error 结合，再通过局部 Gaussian score 做相对异常度量。（Eqs. 5–7）
4. 在 6 real + 1 synthetic benchmark 上报告主比较、未 PA 结果、mapping / window / parameter / loss ablation。（§4）

代码公开（repo 含基准实验脚本、依赖和说明），主要参数与硬件有披露，适合复核；数据中 SWaT 需按其官方政策申请。复现时要固定 test threshold protocol、PA 实现、multi-entity split、动态 Gaussian 窗口与 rolling attention 的边界。（[repo README](https://github.com/jackyue1994/sub_adjacent_transformer); §4）

## 9. Limitations and Critical Reading

- **方法假设**：异常相比正常更难由 target 的 sub-adjacent window 重建；若故障影响整段较大范围、合法状态突然切换，较远窗口本身也可能无法重建，分数没有来源区分能力。（§3.2, Eq. 5）
- **Circular boundary**：循环 shift 使窗口首尾位置成为环状邻居；这是平衡 attention contribution 的数学实现，未必符合真实时间序列边界语义。（Eqs. 2–3）
- **Global fixed band**：$k_1,k_2$ 和 window size 固定 / 手调；不同 sampling interval、周期长度、短异常可能需要不同 span。（Tables 4, 7）
- **Threshold protocol**：test-set best-F1 与 point adjustment 可提升汇报分数，不能等同于 validation-only streaming result。（§4.2）
- **多实体 protocol**：作者的 pooled model 与部分逐实体 baseline 比较，不能把分数差全归因于 attention 新颖性。（§4.3）
- **Dynamic Gaussian score 语义有限**：它用局部 score mean/std 重新标定，不利用 workload、service stage、release 或 Trace；未提供合法负载变更 + 故障并发实验。
- **Attention 不是因果关系**：这是时间维重建 contribution，不是传感器 dependency graph 或故障 root cause。
- paper 没有专门 Limitations section；以上边界来自其公式、数据 / metric、实验协议及实现假设的逐项分析。

## 10. Related Papers

- **SARAD**：两者均重加权 Transformer attention evidence；SARAD 读取变量维 MHSA 关系的前后窗口变化，Sub-Adjacent 直接约束时间维 attention band 并乘 reconstruction error。
- **CrossAD**：关注 cross-scale / cross-window mapping prototypes；Sub-Adjacent 关注窗口内 target 周边的时间 attention geometry。
- **TFMAE / TriAD**：均用多种时序结构线索。TFMAE 双视图 representation discrepancy，TriAD 三域窗口筛选 + discord；Sub-Adjacent 是局部重建条件约束。
- **Quo Vadis / TSB-AD**：提醒 point adjustment 与 test best threshold 的比较边界；Sub-Adjacent 的主 F1 采用这两种高风险设定。

## 11. Questions for Further Reading

1. 可否按业务周期 / workload 动态设定 $k_1,k_2$，而不是对所有 operating states 使用同一 band？
2. 有限历史因果流中如何处理 circular wrap，替代 padding / causal attention 是否仍能保留非紧邻机制？
3. 该方法在不同 anomaly duration、周期变化、状态切换与故障并发时的 window-size / sub-adjacent-distance 敏感性如何？
4. attention contribution 是否跨随机种子稳定，并与传感器拓扑、Trace 或故障注入来源一致？
5. 在 validation-only 阈值、无 PA event metric 和流式检测延迟下，reported SOTA 是否保留？
6. Dynamic Gaussian calibration 在概念漂移时会否把故障或新正常一并当作局部背景？

## 12. Key Terms

- **Sub-adjacent neighborhood**：距 target 至少 $k_1$、不超过 $k_2$ 的非紧邻时间点。
- **Sub-adjacent attention contribution**：attention matrix 某 target 列在指定 band 中的贡献加总。
- **Linear attention mapping**：用 $\Phi(Q)\Phi(K)^\top V$ 计算 attention；论文的 $\Phi$ 是带 learnable temperature 的 row-softmax。
- **Dynamic Gaussian score**：基于滑动局部 score 均值 / 方差计算 Gaussian tail 变换。

## 13. Tags

`TSAD` `Transformer` `linear attention` `sub-adjacent context` `reconstruction` `dynamic Gaussian scoring` `point adjustment`
