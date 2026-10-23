# SARAD：基于空间关联感知的多变量时序异常检测与诊断

## 1. Metadata

- **Title**: SARAD: Spatial Association-Aware Anomaly Detection and Diagnosis for Multivariate Time Series
- **Authors**: Zhihao Dai, Ligang He, Shuang-Hua Yang, Matthew Leeke
- **Year / Venue**: 2024 / NeurIPS（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/NeurIPS/SARAD_Spatial_Association_Aware_Anomaly_Detection_and_Diagnosis_for_Multivariate_Time_Series.pdf)
- **Official source**: [NeurIPS proceedings PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/56ad264ac7448239145606cf4106042f-Paper-Conference.pdf)（如需核对请以本地 PDF 为准）
- **Code**: [公开实现 SARAD](https://github.com/daidahao/SARAD/)（Appendix G, PDF p.22）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

SARAD 将多变量窗口分成前后两个子序列，经 encoder-only Transformer 读取变量维（论文称 spatial）的 MHSA 关联矩阵，提取关联随时间下降的 column-wise progression；用 MLP 重建该 progression 以过滤正常下降，再将数据重建误差和 progression 重建误差标准化后相加，兼做异常检测与变量级候选诊断。

## 3. Background and Problem Definition

SARAD 面向无监督 multivariate time-series anomaly detection（MTSAD）和 feature-level diagnosis。作者指出，常见 temporal detectors 主要根据预测 / 重建残差测量时间新颖性，却可能遗漏跨变量依赖变化；仅考虑多变量相关性的图模型也可能把预测误差作为唯一检测证据。论文提出观察：异常期间原本存在的空间关联（作者定义为多变量特征维度上的关联，不是地理空间）可能减弱，称为 **Spatial Association Reduction (SAR)**。（PDF pp.2–4, §§1–3）

检测目标为每时刻异常标签 $y_t$；诊断目标为时刻 $t$ 的异常特征集合 $g_t\subseteq[N]$。（PDF p.4, §3）

需要保留定义边界：模型读取 Transformer 的 attention association map，并将其变化视作 learned reconstruction association reduction。该 map 是模型内部信息流 / 重建依赖，不等于 ground-truth Pearson correlation、Granger graph、已知系统拓扑或干预因果图；诊断是基于检测分数得到 feature ranking。（PDF pp.5–6, §§3.2–3.3, Eq. 6）

## 4. Core Challenges

1. **异常空间位置与时间位置并不相同**：异常点可以由受影响少数变量引起，纯时间建模难以定位通道。（PDF pp.3–4, §2）
2. **正常也会出现 association reduction**：若直接把注意力关系下降全判异常，会将无害变化计入；SARAD 以 progression reconstruction residual 对“常见下降”做正常性建模。（PDF p.6, §3.3）
3. **短异常与窗口聚合冲突**：使用半窗口前后比较有利于检测关系演进，但长窗口会稀释短异常。（PDF pp.7, 21, Appendix E.2 / H）
4. **诊断标签不完整**：SMD 有 forensic feature labels；SWaT、HAI 多标攻击来源而不是完整异常变量集合，诊断指标受标注语义影响。（PDF p.8, §4.2; Appendix E.3, p.21）

## 5. Architecture Overview

```text
输入窗口 X ∈ R^(2W×N)
  ├─ 沿时间一分为二：X1、X2
  ├─ 每个子窗转置为变量为 token：Linear(Xiᵀ) + learnable feature embedding M
  ├─ Encoder-only Transformer 沿变量维 MHSA 编码 / 重构
  │    └─ 各层各头输出 association map A^l_{i,h}
  ├─ 最后一层两子窗：S^l_h = ReLU(A^l_{1,h} − A^l_{2,h})
  ├─ 每个 head 对 association progression 做 column sum → S ∈ R^(H×N)
  ├─ MLP 重构 S → Ŝ，用 ||S−Ŝ||² 量化罕见关联下降
  └─ 标准化 data reconstruction error r 和 progression error p 后相加 → s
```

数据重建 Transformer 与 spatial progression MLP 端到端联合训练；stop-gradient 阻断 $S$ 的梯度回流数据模块。检测使用全局 scalar score；主文诊断公式使用逐特征数据 reconstruction residual。（PDF pp.5–7, Fig. 1, Table 1, Eqs. 1–6）

## 6. Method in Detail

### 6.1 Spatial data reconstruction

输入窗口 $X\in\mathbb R^{2W\times N}$，其中 $N$ 是特征数。先切成前后各 $W$ 点的 $X_1,X_2\in\mathbb R^{W\times N}$。每个 subseries 分别转置并线性投影：$E_i=Linear(X_i^T)\in\mathbb R^{N\times D}$，再叠加可学习 feature-level embedding $M=\{m_i\in\mathbb R^D\}$ 得到变量 token 表示。（PDF pp.5–6, §3.2）

多层 encoder-only Transformer 沿变量 token 做 MHSA。第 $l$ 层为

$$Z_i^l=LN(MHSA(X_i^{l-1})+X_i^{l-1}),\quad X_i^l=LN(MLP(Z_i^l)+Z_i^l).\tag{1}$$

每个 head 的 association map $A_{i,h}^l\in\mathbb R^{N\times N}$：行 $j$ 上对 key $k$ 的注意力权重描述第 $j$ 个特征表示从第 $k$ 个特征读取的信息；从重建角度看，作者将列 $k$ 理解为原始 feature $k$ 对所有 feature 重建的贡献。最终层输出线性投影并转置为重建序列 $\hat X_i\in\mathbb R^{W\times N}$，前后两部分拼成 $\hat X$。（PDF pp.5–6, §3.2, Eq. 1）

### 6.2 Association progression extraction

对每个 Transformer 层 $l$、注意力 head $h$，定义前后子序列 attention map 的非负反向差：

$$S_h^l=ReLU(A_{1,h}^l-A_{2,h}^l).\tag{2}$$

该操作只保留“前半关联强于后半”的下降方向。作者观察异常可能瓦解已有空间关联，因此聚焦 reduction，而不把增加与下降对称看待。

只取最终编码层 $L$ 的 progression，之后按 head 做 column sum 得到 $S\in\mathbb R^{H\times N}$：

$$S=\left\{\sum_{j=1}^{N}S_{h,(j,k)}^L\mid h\in[H], k\in[N]\right\}.\tag{3}$$

每列对应输入特征 $k$ 对其他变量重建的贡献，列和近似该特征关联贡献下降总量。作者认为列聚合比行聚合更能凸显 anomalous-feature association dropout；Table 5 的替代行和实验总体支持此选择，但 PSM 的部分指标行和略高，不能说 column sum 对每个数据集 / 指标均优。（PDF pp.6, 10, §3.3, Table 5）

### 6.3 Progression reconstruction filters benign reductions

将 $S$ 展平，输入两层 MLP 得到重构并 reshape 为 $\hat S\in\mathbb R^{H\times N}$。直观上，attention association reduction 本身不是异常标签；如果某种下降模式可由训练正常数据中的 progression autoencoder 重建，则其重构误差较小；罕见 / 异常下降可能产生较大 $\|\hat S-S\|^2$。（PDF p.6, §3.3）

### 6.4 Joint objective and score

数据分支重构损失、progression 分支重构损失和联合目标为

$$L_R=\|\hat X-X\|_2^2,\quad L_S=\|\hat S-S\|_2^2,\quad L=L_R+\lambda_{LS}L_S.\tag{4}$$

从 $S$ 到 Transformer 数据模块的 gradient 被 stop，防止 progression loss 改写原始 association map 并发生表示塌缩。两个分支同步训练，分别学习原始数据重建和 association-progression normality。（PDF p.6, §3.4, Eq. 4）

输入窗口的检测分数由两种残差分别按验证集均值 / 标准差标准化，再相加：

$$r=\|\hat X-X\|_2^2,\quad p=\|\hat S-S\|_2^2,\quad s=\frac{r-\mu_r}{\sigma_r}+\frac{p-\mu_p}{\sigma_p}.\tag{5}$$

验证集用于 score 归一化（均值、标准差）和训练超参选择；论文并不把归一化后的分数称为概率。主文诊断 criterion 是第 $j$ 个变量在重建数据上的误差：

$$s_j=r_j=\|\hat X(j,\cdot)-X(j,\cdot)\|_2^2.\tag{6}$$

因此检测联合两类证据，主要诊断分数却不是 progression 的变量级 residual。Appendix D 测试 alternate joint diagnosis criterion（加上 progression）；未证明始终更好。（PDF p.7, Eqs. 5–6; Appendix D, pp.11–12）

### 6.5 训练流程及配置

训练集均为 unlabeled normal data；训练集按时间切分 80% train / 20% validation。先对数据分支在 validation reconstruction loss 上用 TPE 选择 encoder 层数 $L\in\{3,5\}$ 和 learning rate $10^{-4}$ 到 $10^{-2}$；再用 TPE 选 $\lambda_{LS}\in[10^{-2},10^2]$。默认窗口 $2W=100$、每层 8 heads、attention dimension 512、FFN dimension 2048、progression hidden dimension 64；Adam，每 epoch 学习率减半，共 3 epochs。（Appendix F, PDF p.22）

## 7. Experimental Design and Evidence

### 7.1 Datasets and metrics

四个公开基准：SMD（38 features）、PSM（25）、SWaT（51）、HAI（79）。训练集只含无标签数据，测试集带异常 labels。Table 2 的训练 / 测试点数分别为 SMD 708,405 / 708,420，PSM 132,481 / 87,841，SWaT 496,800 / 449,919，HAI 921,603 / 402,005；异常比例 4.16%、27.73%、12.02%、2.23%。异常持续时间差异明显：中位长度 SMD 11、PSM 5、SWaT 447、HAI 162。（PDF pp.7, 21, Table 2; Appendix E.2）

Detection 报告 threshold-independent range-based AUC-ROC / AUC-PR 及 VUS-ROC / VUS-PR；五次 seed 平均。Baselines 包含 IF、DIF、USAD、GDN、MAD-GAN、DiffAD、TranAD、ATF-UAD、Anomaly Transformer、DCdetector。诊断在有标签数据集上使用 HR、NDCG 和 IPS；标注完整性因数据集而异。（PDF pp.7–9, §§4.1–4.2）

### 7.2 Detection results

Table 3 的 SARAD 四指标（AUROC / AUPRC / VUS-ROC / VUS-PR，%）：

| Dataset | AUROC | AUPRC | VUS-ROC | VUS-PR |
|---|---:|---:|---:|---:|
| SMD | 79.97 | 15.09 | 79.67 | 15.02 |
| PSM | 61.87 | 41.06 | 61.77 | 41.01 |
| SWaT | 88.29 | 72.90 | 87.52 | 70.68 |
| HAI | 96.87 | 67.78 | 96.17 | 64.70 |

作者称 SMD 的 VUS-ROC 比 MAD-GAN 高 15.51 个百分点、HAI 比 DiffAD 高 9.92 点；PSM 比 GDN 低 1.36 点、SWaT 比 DIF 低 0.36 点，显示其为领先或相近而非全数据集完全领先。（PDF p.8, Table 3, §4.2）

Appendix E.2 说明 SMD、PSM 的异常较短，SARAD 半窗聚合可能稀释短异常；这和其使用空间关系而不是局部 temporal detector 的收益—代价相对应。（PDF pp.8, 21）

### 7.3 Diagnosis results

Table 4 报告点级 HR@100/150、NDCG@100/150 和范围级 IPS@100/150。SARAD 的 HR@150 / NDCG@150 / IPS@150：SMD 71.93 / 69.78 / 76.44；SWaT 12.83 / 11.65 / 54.34；HAI 12.10 / 10.16 / 14.07。（PDF p.9, Table 4）

相对增益需结合标签含义看：SMD 为 forensic anomalous features；SWaT / HAI 只标攻击来源，有的攻击失败，攻击源也不一定呈现异常，且全体异常变量可能未标全。因此 SWaT / HAI 的低 HR/NDCG 既反映模型排序，也受监督标签不完整影响，不能只按数字归结为检测算法能力。（PDF p.8, §4.2; Appendix E.3, p.21）

### 7.4 Ablations and operational cost

- Table 5：去掉 ReLU 后 SMD VUS-ROC/VUS-PR 从 79.67/15.02 降至 75.16/12.35，支持专注 association reduction；将 column sum 改 row sum 后部分性能小幅变动且并非所有指标都差；完全不聚合（no sum）会显著退化，例如 SMD AUROC / AUPRC 79.97/15.09 → 57.31/6.09。将 $S$ 直接作为异常证据（不经 MLP reconstruction）只在 SMD 部分项更好，在其余数据集多数变弱，符合 MLP 过滤常见 reduction 模式的设计动机。（PDF p.10, Table 5）
- Table 6 比较 data-only、progression-only 与 joint detection。作者总结联合分数总体更强；应查看逐 dataset 行，避免推成每个单项指标必胜。（PDF pp.10–11, Table 6）
- Appendix D 对 diagnosis score 比较 data-only 和 joint criterion；main paper 仍采用 data-only per-feature reconstruction。（Appendix D, pp.11–12）
- HAI 上报告训练约 32 分钟、单样本推理约 0.39ms；空间维 attention 的时间复杂度对特征数为 $O(N^2)$。作者指出大规模特征系统成本会增加，提出层级聚类扩展方向；同时指出 forensic diagnosis 标签稀少。（PDF pp.9, 16; Appendix N）

## 8. Contributions and Reproduction Value

### Technical contributions

1. 以窗口前后两半 MHSA map 的非负差构造 association reduction progression。（§3.3, Eq. 2）
2. 汇总最终层 column-wise progression，突出被该特征贡献关系衰减的通道。（Eq. 3）
3. 用 progression autoencoder residual 学会过滤可重建的正常关联下降，并与原数据 reconstruction residual 共同检测。（§3.4, Eqs. 4–5）
4. 提供检测与 feature ranking，比较 4 个数据集的 range metrics、诊断 metrics 及模块消融。（§4, Tables 3–6）

### Reproduction value

- **较有利**：代码公开；窗口、Transformer heads / dimensions、训练轮数、validation split 与 TPE 搜索范围见 Appendix F；作者报多 seed 结果、模块消融和硬件运行成本。（PDF pp.10, 22）
- **需复现确认**：主文与实现中的 subseries split / merge 滑窗标签对齐、$A$ map 的取法和 validation 标准化细节、不同数据集调参随机性、range metrics 实现版本。
- **标签边界**：诊断基准的 feature ground truth 不等价；SMD forensic labels 比 SWaT / HAI attack-origin labels 更适合 feature localization 的精度判断。（Appendix E.3）
- **部署边界**：前后半窗口关联对比依赖完整 $2W$ 窗口；论文给出运行成本低于采样频率的估计，但真实 stream 中滑窗告警延迟、短异常衰减和负载变化影响仍要单独评估。

## 9. Limitations

### 作者明确指出

Appendix B 指出 attention 空间复杂度随特征数二次增长，在超大监控系统有计算代价；可探索按变量层级聚类。另一个限制是 forensic diagnosis labels 稀少，收集需要大量专业标注。（PDF p.16, Appendix B）

### 实验支持的边界

- 短异常数据集 SMD / PSM 的半窗口机制可能稀释关联变化；窗口敏感性强调过大的窗口有计算代价并进一步稀释短异常。（Appendix E.2, H, PDF pp.21–22）
- HAI 的 32min / .39ms 结果来自论文设定的硬件和数据规模，不能直接外推到超高维指标集。（Appendix N）
- 主诊断分数为 per-feature data reconstruction error，空间 progression 主要参与全局检测分数；它不是 attention edge causality-based diagnosis。（Eq. 6）
- 论文用验证集归一化并调超参，但主报告主要是阈值无关 AUC / VUS；在真实报警中固定 operating point 和告警成本未成为主结果。（§4.1）

### 本知识库的分析推断

- 合法 workload / control-state 切换也可能改变 MHSA associations；SARAD 只比较窗口前后关系并以训练正常 progression autoencoder 作参照，没有外部业务 context 判断该下降是否“正常状态变化”。
- association reduction 是模型 attention map 的变化；它提供检测证据，但不能单独解释关联为何变化，更不能替代 Trace / topology / intervention 的根因验证。
- 窗口里正常状态切换与真实故障并发时，差分会混合二者；若状态切换本身产生普遍性 association dropout，progression MLP 是否会过滤它取决于训练样本是否覆盖该状态。
- 稀疏标签和攻击来源标签不完整，限制了对 feature localization 泛化能力的主张。

## 10. Related Papers

- **OracleAD / Structured Temporal Causality**：OracleAD 比较当前 latent pairwise-distance matrix 与 SLS；SARAD 比较两半 attention map 的下降并重构 progression。二者都从表示结构提取异常线索，但 SLS 是全局对称 latent-distance 模板，SARAD 则显式利用窗口内关联变化。
- **GCAD**：GCAD 根据各 target prediction loss 对输入通道的梯度近似窗口级有向 Granger influence；SARAD attention weights 是重建依赖，未主张 Granger 因果。
- **CAROTS**：用 Granger 图指导因果保持 / 破坏增强；SARAD 用 attention association progression 作为直接异常信号。
- **Graph-MoE**：Graph-MoE 学当前窗口图并用历史 memory 路由 GNN-depth experts；SARAD 从 Transformer attention 关系下降构造独立 progression detector。
- **CrossAD**：CrossAD 比较粗细时间尺度正常映射并用跨窗原型；SARAD 比较跨变量关系在窗口前后两半的变化。

## 11. Questions for Further Reading

1. 新负载、控制状态切换或发布带来的关联下降，如何与传感器故障造成的 SAR 区分？需什么外部状态标签 / 控制实验？
2. 关系图 attention 权重是否能在跨模型、跨初始化下稳定对齐，是否对应真实传感器拓扑或可干预关系？
3. 正常业务状态切换与故障并发时，progression MLP 是否能分离二者；是否会过滤掉真实故障或把未见正常切换报警？
4. 用前后窗口关联变化检测时，告警延迟是否随 $W$ 增长；对于持续 1–5 点异常，最优窗口的精确召回 / 延迟是多少？
5. progression reconstruction error 是否给出有效的变量级解释？当前主诊断分数采用数据误差，能否用 forensic ground truth 验证结构贡献？
6. 在大规模指标空间，按 service topology / feature cluster 分层是否既降 $O(N^2)$ 计算又保留跨组异常关联？

## 12. Key Terms

- **Spatiality**：本文指多变量时序的 feature / channel 维度，不是地理空间。
- **Spatial Association Reduction (SAR)**：异常过程中 Transformer MHSA 学得的 feature reconstruction associations 下降现象。
- **Spatial progression $S$**：前半与后半 association map 的 ReLU 差异，经最终层 column sum 聚合而成的矩阵。
- **Joint detector score**：数据重建误差与 progression 重建误差分别按 validation 统计标准化后求和。

## 13. Tags

`TSAD` `multivariate` `association-reduction` `attention` `spatial-progression` `anomaly-diagnosis` `NeurIPS-2024`
