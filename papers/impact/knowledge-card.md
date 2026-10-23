# 知识卡片：IMPACT

> 全名：*IMPACT: Influence Modeling for Open-Set Time Series Anomaly Detection*。标记：**[作者主张]** 论文机制 / 解释；**[实验支持]** 结果直接支持；**[分析推断]** 知识库判断。页码按 ICML 2026 PDF。

## 1. Research Scenario

- **[作者主张]** Open-set supervised TSAD：有少量 labeled seen anomalies，nominal-normal training pool 含未标记 anomaly contamination，测试需识别 seen + unseen anomaly classes。（§3, p.3）
- **[实验支持]** 4 个单类与 4 个多类 benchmark，含 SMD / ASD / PSM telemetry、ECG、EEG；2% 主设置污染，另有 2%–10% 分析。（§4.1; Appendix E, H.3）

## 2. Core Challenges

- **[作者主张]** 污染正常样本会误导有监督边界；少量 seen classes 无法覆盖未见异常；手写 pseudo anomaly 可能不符合时序结构。（§1–2）
- **[作者主张]** helpful rare normal 与 harmful contamination 要依其对验证 risk 的方向区别。（§3.1）

## 3. Existing Limitations

- **[作者主张]** Open-set baselines 常默认未标记池干净；固定 augmentation 不保证生成有用的 unseen anomaly。（§1–2）
- **[分析推断]** 需 validation labels / reliable risk estimate 的条件较强；valid rare subpopulation 也可能因组间差异而被错误剔除或翻标。

## 4. Core Idea

- **[作者主张]** Influence scoring 同时做两件事：把 positive validation-risk influence 的 nominal sample 翻为 anomaly；将最不利于降低 risk 的 clean normal embedding 沿 risk-increasing direction 扰动，作为 unseen anomaly 训练。（§3.1–3.2）

## 5. Technical Innovations

1. **[作者主张] TIS**：multi-channel Gaussian deviation score / margin loss，使用 influence function 估算训练样本对 validation risk 的影响。（§3.1, Eqs. 1–7）
2. **[作者主张] RADG decontamination**：对 $I_L(z_i)>0$ 的 $D_n$ 样本做 0→1 label flip；作者给出一阶 risk 下降表达式。（§3.2, Eqs. 8–13）
3. **[作者主张] Feature-space pseudo anomaly**：取最 less-helpful 的 k 个 normals，在 $I_{per}^\top$ 方向加扰动，并标为 unseen anomaly。（§3.2, Eqs. 14–16）
4. **[作者主张] 双头训练与 score**：seen / unseen head 联合 loss，加 multi-channel max abnormality 与到 $D_{ref}$ 平均 embedding 的 L2 distance。（§3.3, Eqs. 17–21）

## 6. Key Mechanisms

- **[实验支持]** General setting 八数据 IMPACT AUC：59.21、65.76、64.24、75.97、91.96、68.13、66.99、82.91。（Table 1, p.7）
- **[实验支持]** Hard open-set mean AUC：CT 81.90、SAD 66.19、PTBXL 62.48、TUSZ 75.70。（Table 2, p.8）
- **[实验支持]** 去掉 unseen loss 后 hard TUSZ 75.70→60.92；随机 feature perturbation 为 62.87；显示 unseen head / risk-guided features 在该协议的重要性。（Table 3, p.9）
- **[实验支持]** 2%–10% contamination 下作者报告表现相对稳定；相较常见 augmentation 的 pseudo-feature KLD 平均降低 64.13%。（Appendix H.3–H.4, pp.21–23）

## 7. Experimental Evidence

- **[实验支持]** 比较 unsupervised 与 open-set baseline；open-set general / hard 都只提供每个可用 anomaly class 10 个 labeled examples，结果为五次 run 的 AUC。（§4.1）
- **[实验支持]** 污染从原 test anomalies 抽样但明确排除最终 test set；外加 point-level Affiliation-F1 / VUS-ROC 和 seen / unseen 拆分分析。（Appendix E, H.1, H.7）
- **[证据边界]** “few-shot open-set + contamination correction”不等于 unsupervised、zero-shot 或无标注生产系统。

## 8. Limitations

- **[作者指出]** Rare normal subpopulation 可能因语义上与其它 normal 差异大而被误判；作者将其列为 group-robustness failure mode。（Appendix I, p.28）
- **[分析推断]** Influence 判断依赖初始模型、validation set 和 Hessian / Fisher 近似；risk sign 不是 perfect contamination label。
- **[分析推断]** 伪异常是在 feature space 合成，KLD / t-SNE 与 AUC 不证明 waveform、系统因果或业务事件真实。
- **[分析推断]** 测试异常模拟污染来源，实际污染机制可能不同；AUC 不说明固定阈值误报或在线延迟。
- **[分析推断]** 不输入 workload、release、Trace / service topology；未验证正常负载变化与故障并发。

## 9. Research Opportunities

- **[分析推断]** 用 group-aware / state-aware validation 区分 contamination 与稀有但合法的 normal state，报告 group-wise false-positive / recall。
- **[分析推断]** 在污染类别、发生机制、污染比例与验证标签质量之外做 held-out stress tests，并验证 influence ranking。
- **[分析推断]** 为 feature pseudo anomaly 加 temporal decoder / causal constraints，验证其是否可映射到真实故障形态。
- **[分析推断]** 在固定 false-alarm budget 下比较 AUC、event delay、审查负担和每轮 influence compute。

## 10. Related Papers

- **TimeRCD**：zero-shot synthetic RCD foundation model；IMPACT 是 few-shot open-set 与风险驱动训练样本治理。
- **DRA / MOSAD / InvAD / WSAD-DT**：open-set baselines 与伪异常机制参照。
- **Fortifying Time Series**：对比 adversarial input robustness 与 training contamination robustness。
- **CAPMix / When Model Meets New Normals**：分别研究动态 KPI / 新正常状态，不应把 contaminated nominal pool 视作状态变化本身。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[IMPACT PDF](../../sources/papers/tsad-2024-2026/2026/ICML/IMPACT_Influence_Modeling_for_Open_Set_Time_Series_Anomaly_Detection.pdf)
- 代码：[IMPACT repository](https://github.com/mala-lab/IMPACT)
- Proceedings：[PMLR 306](https://proceedings.mlr.press/v306/zhou26as.html)
