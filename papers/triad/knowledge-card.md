# 知识卡片：TriAD — Self-supervised Tri-domain TSAD

> 标记：**[作者主张]** 论文方法动机 / 作者解释；**[实验支持]** 表格、消融或案例直接支持；**[分析推断]** 本知识库判断。PDF 页码指会议论文页码。

## 1. Research Scenario

- **[作者主张]** 自监督、单变量 TSAD：面对不同异常长度与形状，用 temporal、frequency 和 residual 线索先找候选窗，再用 variable-length discord search 定位。（§§I, III, pp.1–7）
- **[实验支持]** UCR Archive 250 个 test series，每个数据集含一个 anomaly event。（§IV-A, p.7）

## 2. Core Challenges

- **[作者主张]** 常见 augmentation 可能合成出异常形状；continuous anomalies 可能也被 reconstruction model 重建；全 test series discord search 成本较高。（§I）
- **[实验支持]** PA-F1 对随机 score 的改善可很大；TriAD 使用 PA%K / affiliation 重新比较。（§II-B, Table II; §IV-B）

## 3. Existing Limitations

- **[作者主张]** 不恰当正样本 augmentation 与单一 temporal residual 难覆盖 anomaly diversity；discord 搜索需降低范围。（§§I, III）
- **[分析推断]** test-set single-event 先验使其 top-1 窗口选择不自然适用于多事件 streaming TSAD。（§III-D; §IV-A）

## 4. Core Idea

- **[作者主张]** 将局部 jitter / magnitude warp 视为可能异常负例，学三域 representation；用跨窗离群分数缩小 search region，再由 MERLIN 细化可变长度区间。（§III, Eqs. 3–8）

## 5. Technical Innovations

1. **[作者主张] 三域输入**：raw temporal；frequency amplitude / phase / power 三通道；周期趋势去除 residual。（§II-A, III-B, Table I）
2. **[作者主张] 局部合成异常**：random segment jitter / Butterworth magnitude warping，而不是把增强数据当正常正例。（§III-A, Eqs. 3–4）
3. **[作者主张] 双对比目标**：same-domain original positives / augmented negatives；inter-domain 保留 domain-specific cues。（§III-C, Eqs. 5–7）
4. **[作者主张] Candidate-window + discord pipeline**：每域 top-1 异常窗，经 normal-train comparison 选窗，再做局部多长度 MERLIN。（§III-D）

## 6. Key Mechanisms

- **[实验支持]** Table III：PA%K F1 .233±.009、Affiliation F1 .729±.014；TriAD 的 PA%K 相比 PA-F1 保持更稳，不像多数 baseline 在 PA 后大幅提高。（PDF p.9）
- **[实验支持]** MERLIN++ 的 62 个最短 UCR series 比较中，TriAD tri-window accuracy .681 / .99 min，MERLIN++ .424 / 14.5 min；作者还报告 search region 平均缩短约 20 倍。（Table IV, Fig. 7, p.9）
- **[分析推断]** TriAD 的 detection unit 是“候选窗和 discord 共同投票”，不是一条通用的逐点 anomaly likelihood model。

## 7. Experimental Evidence

- **[实验支持]** UCR 按 anomaly length / type 提供多样场景；5 seeds，10% training validation；单篇 dataset 单独训练。（§IV-A, pp.7–8）
- **[实验支持]** frequency/general encoder 与 intra-domain contrast 对本 benchmark 更重要；residual encoder ablation 贡献较小。（Fig. 9, p.10）
- **[实验支持]** UCR 025 的微妙频率 shift 案例由 frequency/residual window rankings 定位；UCR 150 展示 discord search 失败 fallback。（Figs. 10–16, pp.10–12）

## 8. Limitations

- **[分析推断]** 单异常事件、top-1 window 和 test series 相对离群假设限制多故障 / 状态切换场景。
- **[作者指出]** vote score 暂无 normalization / weighting；异常占窗口多数时 discord 可能失败，需 fallback 为窗口内全异常。（§III-D, §IV-G）
- **[分析推断]** periodic residual 的提取细节需核对代码；UCR 单变量数据不含 workload / Trace / topology，模型不解释异常根因。

## 9. Research Opportunities

- **[分析推断]** 放宽单事件先验，用 event count-free 候选筛选与多候选 NMS；测状态切换和多故障并发。
- **[分析推断]** 将业务周期 / workload context 与周期 residual 分解结合，检验合法周期切换是否误报。
- **[分析推断]** 校准三个 domain vote 及 MERLIN score，报告固定误报预算、event delay 和边界质量。
- **[分析推断]** 对照更丰富多变量工业指标、状态标签及 fault injection，验证不同域 representation 的外部语义。

## 10. Related Papers

- **TFMAE / TFC / MACE**：共享 frequency evidence，但 TriAD 是三域窗口离群与 discord 搜索；TFMAE 是双视图逐点 KL；TFC 是时频曲率融合；MACE 是服务条件频谱 normal subspace。
- **PCRTA**：同以 perturbation 提供异常相关信号；PCRTA 通过 perturbation type pseudo-label 引导对比，TriAD 直接将增强 view 作为同域负例。
- **Quo Vadis / TSB-AD**：共同关注 PA 调整与 benchmark 质量；TriAD 用 PA%K / affiliation，但还应核对 oracle threshold 和单 event 先验。
- **Sub-Adjacent Transformer**：都是局部异常范围方法，但一个先找离群窗、另一个限制重建依赖到非紧邻区域。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[TriAD PDF](../../sources/papers/tsad-2024-2026/2024/ICDE/Unraveling_the_Anomaly_in_Time_Series_Anomaly_Detection_A_Self_supervised_Tri_domain_Solution.pdf)
- 代码：[TriAD GitHub](https://github.com/pseudo-Skye/TriAD)
