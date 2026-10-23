# 知识卡片：TeamWork

**论文**：*TeamWork: Multivariate Time Series Anomaly Detection via Asymmetric Role-aware Channel Modeling* (ICML 2026)。**作者主张 / 实验支持 / 分析推断**分层标记。页码对应 PDF。

## 1. Research Scenario

- **[作者主张]** MTSAD 中通道重要性不均、周期尺度不同，需同时处理 dominant / auxiliary channel 及 point / subsequence anomalies。（§1）
- **[实验支持]** 8 个真实数据集、16 个 baselines、统一评估协议。（§5）

## 2. Core Challenges

- **[作者主张]** CI 漏 channel dependency；CD 加入冗余关系；CC 按相似度分组但可能漏掉 dominant variables。（§2.2）
- **[作者主张]** period-agnostic mask 不适配短周期点异常 / 长周期子序列异常。（§2.1）

## 3. Existing Limitations

- **[作者主张]** 等容量 / 全连接建模忽略变量相对 explanatory role；固定 point / patch masking 忽略多周期。（§1–2）
- **[分析推断]** ERI 反映统计依赖，不证明变量是因果驱动因素。

## 4. Core Idea

- **[作者主张]** ERI 选出 dominant channel 做多周期 masked modeling；辅助 channel 用轻量 MLP，再由 dominant-guided gates 选择性融合。（§4）

## 5. Technical Innovations

1. **[作者主张] ERI decouple**：$\Delta H_i=H(X_{-i})-H(X_{-i}|x_i)=I(X_{-i};x_i)$，Kraskov estimator、按 max ERI 归一化、阈值 .5。（§4.1, Eqs. 1–4）
2. **[作者主张] Period maskers**：top-3 FFT periods 分别用 point / segment / period masking。（§4.2, Eqs. 5–9）
3. **[作者主张] Asymmetric gate**：主支多尺度建模、辅助支轻量 MLP，由 HM 过滤 HA，再逐支门控融合。（§4.3, Eqs. 10–12）
4. **[作者主张] Reconstruction score**：融合表示重建 X，以平方误差检测。（§4.4, Eqs. 13–14）

## 6. Key Mechanisms

- **[原文]** Dominant channels 按 $\delta_i\ge\delta^*$ 选取；period masker 的 mask 粒度和周期长度关联。
- **[原文]** 作者解释 dominant / auxiliary 分别是系统 driving 与 complementary cues；ERI 实际只量化 entropy reduction / mutual information。
- **[分析推断]** static ERI 排名可能在不同业务状态过时；周期和角色都非因果标签。

## 7. Experimental Evidence

- **[实验支持]** Table 1 在 8 集报告 Aff-F / AUC-ROC 竞争最佳；包括 GECCO .934/.992、Genesis .928/.994、SMAP .864/.592。（Table 1）
- **[实验支持]** 3 集消融 Accuracy avg .927；CI .864、CD .899、CC .872，random role .867、去 dominant .673；三种 masker 均低于 full。（Table 3）
- **[实验支持]** top-3 periods 和三种卷积核已足够；默认角色 threshold 与 mask ratio 均 .5。（Fig. 4; Appendix E.1）

## 8. Limitations

- **[作者指出]** roles 静态；全局 FFT 对弱周期 / 局部非平稳较弱。（Limitations, p.14）
- **[分析推断]** 没有 workload / release / Trace 上下文；dominant role 不能直接作根因或系统因果解释。
- **[评估边界]** threshold-ratio set 和 CATCH 参数 protocol 需记录；跨状态 / entity 泛化不足以由当前表格证明。

## 9. Research Opportunities

- **[分析推断]** 按运行阶段动态估计 ERI，检测角色切换时避免异常污染角色更新。
- **[分析推断]** 在弱周期、局部非平稳与周期变化、负载 / 故障并发中测多尺度 mask 的作用。
- **[分析推断]** 对比 ERI 角色、因果图和业务拓扑，报告 role stability 与变量级解释忠实度。

## 10. Related Papers

- [完整精读笔记](notes.md) · [原始 PDF](../../sources/papers/tsad-2024-2026/2026/ICML/TeamWork_Multivariate_Time_Series_Anomaly_Detection_via_Asymmetric_Role_aware_Channel_Modeling.pdf)
- **ScatterAD**：时间节点 GAT / 散布；**Graph-MoE / CATCH / CrossAD**：变量交互；**CCM-TAD / SARAD / GCAD / CAROTS**：关系 / 因果；**MACE / WMMNN**：状态化 normality。
