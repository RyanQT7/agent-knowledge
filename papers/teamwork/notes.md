# TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling

## 1. Metadata

- **Authors**: Shiyan Hu, Tengxue Zhang, Jianxin Jin, Xiangfei Qiu, Bin Yang, Chenjuan Guo
- **Year / venue**: 2026 / ICML (CCF A，已人工确认)
- **PDF**: [原始论文](../../sources/papers/tsad-2024-2026/2026/ICML/TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf)
- **Proceedings**: [PMLR 306](https://proceedings.mlr.press/v306/hu26bf.html)
- **Code**: [TeamWork repository](https://github.com/decisionintelligence/TeamWork)
- **知识卡片**: [knowledge-card.md](knowledge-card.md)

## 2. 一句话总结

TeamWork 先用 entropy reduction index (ERI) 把变量分成相对主导的 dominant 与补充性的 auxiliary channels，再只对 dominant channels 使用依 top-3 FFT 周期定制的 point / segment / period masking 和 multi-conv 时序建模；auxiliary channels 用轻量 MLP，随后由 dominant-guided extraction 与门控层融合，最终以 reconstruction error 检测。（§§3–4, Eqs. 1–14, pp.3–7）

## 3. 背景与问题定义

多变量异常检测既要处理时间依赖，也要处理跨 channel 关系。channel-independent (CI) 忽略真实依赖；channel-dependent (CD) 对所有通道一视同仁，可能引入冗余 / 虚假关系；channel-clustering (CC) 按相似度分组，但仍可能错过真正驱动系统的少数变量，或低估 cluster 外异质辅助信号。（§2.2, pp.3–4）

作者进一步指出，同一异常可随周期长度而变化：点异常在短周期更醒目，在长周期可能被平滑；持续子序列异常则需要更长时间范围；固定 point- / patch-mask 不会显式适应多周期结构。（§1–2, pp.1–3）

**任务边界**：dominant / auxiliary 是由数据统计上的解释力确定的通道角色，不是人工提供的业务主次 / 因果等级。论文称 dominant 变量“驱动系统演化”，但 ERI 本身来自 entropy / mutual information 估计，不单独证明因果方向。（§3.2; 分析推断）

## 4. 整体算法架构

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

## 5. 方法细节

### 5.1 ERI-based Variable Decouple

对变量 $x_{i,:}$，作者定义它对其余变量不确定性的降低：

$$\Delta H_i(X,x_{i,:})=H(X_{-x_i})-H(X_{-x_i}\mid x_{i,:}). \tag{1}$$

该式等价于 $I(X_{-x_i};x_{i,:})$。对每个变量用 Kraskov k-nearest-neighbor estimator 近似，按最大 ERI 归一化：

$$\delta_i=\frac{\Delta H_i}{\max_j\Delta H_j}. \tag{2}$$

阈值 $\delta^*$ 定义 dominant set $X_M=\{x_{i,:}:\delta_i\ge\delta^*\}$；其余通道为 auxiliary $X_A$（Eqs. 3–4）。作者实验默认 $\delta^*=0.5$；所有通道最终都会经某一路进入异常检测。（§4.1, pp.4–5; §5.3, p.8）

主导角色不是人工先验，而是“变量对其余序列统计依赖的相对解释力”。ERI 计算是数据驱动筛选，若变量角色随业务运行阶段变化，固定全局 ERI 会过时；作者在 limitations 明确称当前 role perception 是 static。（§5, p.14）

### 5.2 Period-aware Masked Modeling

先对 $X_M$ 进行 FFT，取前三个主要周期 $P_1,P_2,P_3$（按周期长度升序）；根据每个周期 $P_i$ 把输入重排成 $G_M^{(i)}\in\mathbb R^{H_i\times P_i}$，每行为一个周期、每列对应周期内相位。（§4.2, p.5）

不同周期分配不同自监督 mask：

- **Point Masker（短周期）**：独立随机遮单点 $M^{(s)}_{h,p}=\mathbf1(u_{h,p}>\rho)$，学细粒度、point anomaly 特征（Eq. 5）。
- **Segment Masker（中周期）**：每行屏蔽连续片段，长度 $\ell_k=\lfloor\alpha P_m\rfloor$，促使模型借助局部上下文恢复（Eq. 6）。
- **Period Masker（长周期）**：屏蔽完整周期行，学习跨周期依赖（Eq. 7）。

masked period matrices 经 projection 和多卷积核 $1\times1,3\times3,5\times5$，再 Align 去 padding、聚合得到 $H_M$（Eqs. 8–9, p.6）。作者解释点 mask 对点异常有用，segment / period masks 帮助 subsequence 异常；这是机制假设，需由异常持续时间分层实验验证。（§4.2）

### 5.3 Role-aware Gated Interaction Module

auxiliary branch 先以轻量 MLP 得到 $H_A$。dominant-guided extraction 将 dominant 与 auxiliary 拼接，经 $1\times1$ Conv / sigmoid 得 guidance gate：

$$H_A^*=H_A\odot\sigma(\mathrm{Conv}_{1\times1}([H_M;H_A])). \tag{10}$$

再分别对 $H_M$、$H_A^*$ 做 sigmoid-gated projection：

$$O_M=\sigma(\mathrm{Conv}_{1\times1}(H_M))\odot\mathrm{Conv}_{1\times1}(H_M),$$
$$O_A=\sigma(\mathrm{Conv}_{1\times1}(H_A^*))\odot\mathrm{Conv}_{1\times1}(H_A^*). \tag{11–12}$$

最后 $Z=O_M+O_A$。非对称设计给 dominant 多周期高容量表示，给 auxiliary 较轻的计算路径，并由 dominant 指引筛选 auxiliary 补充信息。（§4.3, p.6）

### 5.4 Reconstruction head 与推理

MLP projection 将融合表示重建为 $\hat X$；训练目标平方 Frobenius reconstruction loss：

$$L_{rec}=\|X-\hat X\|_F^2. \tag{14}$$

测试时重建误差作为 anomaly score，得分越大越异常（§4.4, p.6）。因此方法在 inference 上是 reconstruction scoring；role / period modules 主要改变学习表示，不额外输出变量级 causal explanation。

## 6. 实验设计与证据

### 6.1 数据、对照与阈值

8 个真实多变量数据集：GECCO（水处理）、Genesis（制造设备）、CalIt2（行人流量）、Creditcard、MSL / SMAP（航天）、PSM / SMD（服务器）。维数 2–55，异常率 .17%–11.07%，平均总长约 5,040–1,416,825。（§5.1, Appendix A.1, pp.7, 14）

对照 16 个基线，包括经典 HBOS / PCA / IForest / OCSVM、AE、NLinear / DLinear、PatchTST、TimesNet、DCdetector、Anomaly Transformer、iTransformer、DualTF、ModernTCN、CATCH、CrossAD。按统一 benchmark 重新评估，报告 Aff-F、AUC-ROC，附录扩展 16 指标；label threshold ratio 从预设 $[0.1,0.5,1,2,3,5,10,15,20,25]\%$ 集合选取。附录称遵从 TFB、关闭 drop-last，GPU 为 A800-80GB，Adam，并依 CATCH 的 optimal setting 配置。（§5.1–5.2; Appendix A.3–A.4）

### 6.2 主结果

作者报告 8 集 Aff-F 与 AUC-ROC 都优于表中 16 个竞争方法（Table 1, p.7）。例如 TeamWork 的 Aff-F：GECCO .934、Genesis .928、CalIt2 .852、Credit .756、MSL .744、SMAP .864、PSM .857、SMD .854；对应 AUC-ROC：.992、.994、.850、.963、.681、.592、.720、.825。注意这些数字的有效比较限于论文统一 benchmark 及该表设置。

### 6.3 消融和敏感性

- **Channel roles**：Credit / Genesis / SMD 平均 Accuracy 中，完整 TeamWork .927；CI .864、CD .899、CC .872、去掉 dominant .673、去掉 auxiliary .902、随机分配角色 .867（Table 3, p.8）。支持角色区分与两组互补，但角色“主导”不等于因果驱动已验证。
- **Interaction**：去掉 extraction、去掉 gate、简单 add 和双向 auxiliary→dominant 均低于 full 的平均 Accuracy .927（Table 3）。
- **Masking**：仅 point / segment / period masker 平均 .911 / .918 / .915，无 mask .890，完整多 mask .927；支持组合优于单一或无 mask。（Table 3）
- **参数敏感性**：$\delta^*$ 和 mask ratio 在多个值上相对稳定，作者取两者 .5；top-3 periods 足够，多于三周期没有额外收益，卷积核数量 3 较合适。（Fig. 4; Appendix E.1）

### 6.4 作者明确指出的限制

1. 角色划分静态：某变量在一个 operating stage 可能 dominant，在另一个阶段可能 auxiliary。
2. FFT 周期主要代表全局 periodic structure；弱周期或局部非平稳变化时可能不够有效。作者提出 dynamic roles、wavelet / 局部时频建模作为后续方向。（Limitations, p.14）

## 7. 技术贡献、边界与复现价值

### 贡献

1. 将 channel dependency 不等同于所有变量均等交互，而按 ERI 划分 dominant / auxiliary，并非对所有通道同容量建模。（§4.1）
2. 把异常持续尺度与周期相关联，设计 point / segment / period 三种 masking 机制。（§4.2）
3. 用 dominant-guided gate 融合角色表示，配合统一重建目标。（§4.3–4.4）

### 局限与分析

- ERI 是互信息 / entropy reduction 统计依赖；共同驱动、冗余变量或数据量 / estimator 偏差都可能影响角色归属，不能当作因果发现结果。（Eqs. 1–4；分析推断）
- 角色 static、period 用全局 FFT，是作者承认的不适应状态切换和局部非平稳边界。（Limitations, p.14）
- 辅助变量只用轻量 MLP，可能欠拟合某些高度动态的异质通道；反向信息对 dominant 的价值不确定。（Table 3; Appendix ablation）
- 预设 threshold ratio 集、统一 benchmark 与 CATCH-derived 配置降低比较差异，但训练 / 测试 threshold protocol 和跨实体外推需另行确认。（§5.2; Appendix A.4）
- 数值通道角色没有 workload / release / Trace / service graph 语义；重建误差定位偏差，但不解释波动成因。（方法定义；分析推断）

### 开源与复现

官方 [TeamWork 代码](https://github.com/decisionintelligence/TeamWork) 可帮助复核 Kraskov ERI 实现、变量切分是否只用训练数据、FFT period 对齐、mask index 及阈值选择。复现时按 operating stage 画出 ERI rank 稳定性，并把静态 / 动态角色比较、弱周期序列、局部故障、正常状态切换与并发故障纳入验证；无需重训时也可先复核输入/阈值协议。本次没有运行代码或训练。

## 8. 相关论文

- **Graph-MoE / CrossAD / CATCH**：均处理变量间交互 / 分组；TeamWork 明确区分变量相对角色，CATCH 偏频率通道关系，CrossAD 偏多尺度交叉重建。
- **ScatterAD**：两者均有“异质性 / representation structure”设计；ScatterAD 的图节点是时间步，TeamWork 的关键角色是传感器变量。
- **CCM-TAD / SARAD / CAROTS / GCAD**：学习 cluster、spatial association、因果保持或 Granger 关系；ERI 信息相关不能替代因果证据。
- **MACE / When Model Meets New Normals**：多正常谱模式 / 在线新状态适配，适合与 TeamWork 静态角色划分比较状态切换安全性。
- **COGNOS**：依 residual white-noise / Kalman filtering 处理统计噪声，TeamWork 依重建表征与角色交互处理跨变量与周期结构。
