# 知识卡片：AnoMamba

**论文**：*AnoMamba: Aligning Reconstruction with Time Series Anomaly Detection via Selective Global Dependency Modeling* (IJCAI 2026)。标记为**作者主张 / 实验支持 / 分析推断**。页码对应 PDF。

## 1. Research Scenario

- **[作者主张]** 无监督重建式 TSAD 中局部依赖易拟合、异常也被重建；希望学习 global normal behavior。（§1）
- **[实验支持]** 4 个 UCR UTS + 4 个 TSB-AD MTS benchmarks。（§5）

## 2. Core Challenges

- **[作者主张]** 固定位置 prior / window 无法适配随上下文变化的 global dependencies。（§1–2）
- **[分析推断]** 学得全局关系仍不保证是业务状态或故障因果关系。

## 3. Existing Limitations

- **[作者主张]** MSE-only reconstruction 会偏向简单局部模式；Mamba 原 step-size 只依当前输入，难以充分选择长程信息。（§1–2）
- **[分析推断]** reconstruction residual、SPOT 阈值仍限制实际告警点表现。

## 4. Core Idea

- **[作者主张]** Patch embedding 降低局部冗余，以全局 patch context 重加权 Mamba step-size，并加多尺度 prior 防止局部过拟合。（§4）

## 5. Technical Innovations

1. **[作者主张] Patch embedding**：通道独立分 patch、Conv 编码。（§4.1, Eq. 12）
2. **[作者主张] GSR**：$\Delta_n^{GSR}=\Delta_n\odot\omega_n$，$\omega$ 由两级 FFN 的跨 patch 上下文产生。（§§4.2–4.3, Eqs. 13–19）
3. **[作者主张] Multi-scale prior**：$P(n)=(n+\alpha)^\alpha e^{-n}$，每步随机采样 $\alpha\in[1,T]$，用 KL regularize。（§4.4, Eqs. 20, 23）
4. **[作者主张] Hidden attention**：由 SSM 展开式显示输入点对 reconstruction 的贡献。（§3.3, Eqs. 8–11）

## 6. Key Mechanisms

- **[原文]** $L=L_{rec}+\lambda L_{KL}$；推理 score 仍为 reconstruction error。（§4.6）
- **[分析推断]** GSR 在数值序列上学 dependency，不显式命名 workload / release states。
- **[解释边界]** hidden attention 是模型 attribution，不自动证明业务原因。

## 7. Experimental Evidence

- **[实验支持]** F1-AF 在 7/8 集第一，VUS-ROC 在 6/8 第一；UTS 平均 .7830/.7739，MTS .7900/.7973。（§5, Tables 1–2）
- **[消融支持]** 去 GSR 后 UTS 平均 F1-AF .7830→.6547；MTS VUS-ROC .7973→.7701。（Table 3）
- **[协议]** 窗口 100、SPOT、5 seeds；prior 固定 α 仍接近多尺度版。（§§5.3–5.6）

## 8. Limitations

- **[证据边界]** 8 datasets，论文未有专门 limitations section；只展示有限 anomaly cases。
- **[分析推断]** 不识别动态正常状态；局部故障、结构变化、固定 FPR / delay 需另验。
- **[代码]** PDF 未列 public repository。

## 9. Research Opportunities

- **[分析推断]** 将 GSR 与业务上下文 / 动态状态适配结合，测负载变化和故障并发。
- **[分析推断]** 检验 hidden attention 与真实 topology / injected cause 的忠实性。
- **[分析推断]** 固定 FPR、point / event delay 和多 entity 外推下比较 local/global trade-off。

## 10. Related Papers

- [完整精读笔记](notes.md) · [原始 PDF](../../sources/papers/tsad-2024-2026/2026/IJCAI/AnoMamba_Aligning_Reconstruction_with_Time_Series_Anomaly_Detection_via_Selective_Global_Dependency_Model.pdf)
- **KAN-AD / RTdetector / IGAD**：prediction / reconstruction alignment；**CrossAD / Sub-Adjacent**：跨尺度 / 非邻近依赖；**WMMNN / CCM-TAD**：新状态 / 在线动态。
