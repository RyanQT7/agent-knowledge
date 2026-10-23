# 知识卡片：Conditional Normalizing Flows with Latent Dynamics

**论文**：*Anomaly Detection in Time-Series via Inductive Biases in the Latent Space of Conditional Normalizing Flows* (UAI 2026)。标记区分**作者主张 / 实验支持 / 分析推断**；页码是论文 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 无监督时序异常检测中 observation-space likelihood 可能把 OOD / 异常赋予高密度，需直接定义 temporal typicality。（§1, PDF pp. 1–2）
- **[实验支持]** 评估合成 amplitude/frequency/noise alterations 与 TSB-AD 真实序列。（§4）

## 2. Core Challenges

- **[作者主张]** 纯 NLL 拟合边缘密度，不保证时序行为符合指定结构。（§1）
- **[分析推断]** 对 latent trajectory 做 GOF 的统计效能随维度、样本窗口、模型拟合合规性变化。

## 3. Existing Limitations

- **[作者主张]** likelihood-based anomaly scoring 可在高密度区域漏掉异常。（§1; Fig. 1）
- **[作者明确限制]** Flat/erratic 数据、过高 CNF 容量、context mismatch、高维小样本 GOF，以及 LG-LDM 与数据不匹配都会削弱方法。（§5, PDF p. 8）

## 4. Core Idea

- **[作者主张]** CNF 映射 $x_t$ 到带预设动态分布的 $z_t$；在白化 latent trajectory 上检验 prescribed dynamics 的统计合规性，以异常替代直接 NLL 阈值。（§3, Eqs. 1–12）

## 5. Technical Innovations

1. **[作者主张] CNF + state-space latent bias**：$z_t=F(x_t\mid W_t;\theta)\sim\mathcal N(\mu_t,\Sigma_t)$，$\mu_t=\psi(\mu_{t-1};\phi)$；实验实例为 LG-LDM $\mu_t=A\mu_{t-1}+b,\Sigma_t=I$。（§3.1, Eqs. 1–5）
2. **[作者主张] NLL 联合训练**：对动态 Gaussian likelihood 和 flow Jacobian 一起优化；支持 sequential / Markovian mini-batch。（§3.1.2, Eqs. 7–11）
3. **[作者主张] MV-KS compliance test**：训练 FIT 检查假设是否成立；测试窗口若 $s_w\ge\tau_w$ 则拒绝 latent distribution compliance。（§3.2, Eq. 12）

## 6. Key Mechanisms

- **[原文]** Whitening $\tilde z_t=\Sigma_t^{-1/2}(z_t-\mu_t)$；假设合规时 $\tilde z_t$ iid $\mathcal N(0,I)$。（§3.1–3.2）
- **[原文]** FIT $=\mathbf1[s_T\le\tau_T]$ 是 training fit diagnostic，不等于 AD quality。（§3.2; Fig. 3）
- **[分析推断]** 检验拒绝预设 latent dynamics，不会自动判定 deviation 来源是合法业务状态还是故障。

## 7. Experimental Evidence

- **[实验支持]** synthetic 4D、$w=64$ 时 MV-KS 对 NLL：AUC-PR 82.1 vs 78.8，VUS-PR 96.0 vs 92.8，Aff-F1 92.6 vs 85.0。（§4.2, Table 2）
- **[实验支持]** TSB-AD 1080 sequences leaderboard 上 NLL 为 UTS 第 7，KS 第 17；所以 KS 不是普遍优于 NLL。（Table 5）
- **[实验支持]** compliance 成功的 NEK / Stock 子集较强；MITDB 训练 FIT 低，NLL 与 KS 均退化。（§4.2, Tables 3–5）
- **[消融支持]** 相对标准 $\mathcal N(0,I)$ latent prior，LG-LDM 在真实序列上 KS VUS-PR 为 $.921\pm.092$ vs. $.836\pm.213$，VUS-ROC 为 $.984\pm.027$ vs. $.977\pm.032$；不代表 LG-LDM 对所有数据都适用。（§4.2, PDF pp. 6–7）

## 8. Limitations

- **[作者明确]** 高维 GOF 低 power，需要较长窗口（建议 $O(D^3)$）；长窗会抹平孤立点异常。容量、context、数据行为敏感，LG-LDM 不适用所有序列。（§5）
- **[作者明确]** NLL 对点 / spike 异常可更好；真实数据上的 KS 竞争力取决于 anomaly type 与 FIT。（§5）
- **[分析推断]** 单一 latent law 未显式区分多个合法 operating states 或 workload/fault concurrency。

## 9. Research Opportunities

- **[分析推断]** 设计多状态 / context-conditioned latent dynamics，测试合法状态切换、未见状态、仅故障和切换+故障并发。
- **[分析推断]** 研究低维 / 分块 GOF、多重检验控制和短窗 point anomaly 的统计 power。
- **[分析推断]** 联合报告 FIT、group-wise FPR、fixed-threshold event recall 与 delay，而非将 training compliance 当作部署性能保证。

## 10. Related Papers

- [完整精读笔记](notes.md) · [原始 PDF](../../sources/papers/tsad-2024-2026/2026/UAI/Anomaly_detection_in_time_series_via_inductive_biases_in_the_latent_space_of_conditional_normalizing_flow.pdf)
- **FlowFuse**：score-space flow 联合密度；**COGNOS**：residual whiteness / NIS；**MACE / CAPMix / WMMNN**：多正常模式与新状态；**AnoMamba / IGAD**：重构正常性约束。
