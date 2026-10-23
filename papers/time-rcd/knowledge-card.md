# 知识卡片：TimeRCD

> 完整题名：*Towards Foundation Models for Zero-Shot Time Series Anomaly Detection: Leveraging Synthetic Data and Relative Context Discrepancy*。标记：**[作者主张]** 论文机制 / 解释；**[实验支持]** 结果直接支持；**[分析推断]** 知识库判断。页码按 ICML 2026 PDF。

## 1. Research Scenario

- **[作者主张]** 对未见目标数据集的 univariate / multivariate series 做 strict zero-shot、point-level TSAD；模型从当前序列内部推断 normality，不用目标集训练。（§2.1, p.3）
- **[实验支持]** 以 2.5B 点 synthetic-only 语料预训练，在 16 个公开 benchmark 上与 zero-shot foundation model 及 per-dataset full-shot baseline 比较。（§3.1; Appendix D.5）

## 2. Core Challenges

- **[作者主张]** 重建误差可能漏掉能重建的平滑异常，也可能误报未见复杂正常模式；zero-shot 下相同形态在不同序列可以有相反 normality label，即 representation conflict。（§1–2.1, Fig. 1–2）
- **[作者主张]** 短窗口缺少长程周期 / pattern 参照；形态 augmentation 本身不一定教会“相同形状在不同 context 可有不同标签”。（§2.1–2.3）

## 3. Existing Limitations

- **[作者主张]** 常见 reconstruction-error inference 与训练目标不一致；依赖固定 source-domain global normal distribution 的 discrepancy 方法也难适应 zero-shot concept shift。（§1–2）
- **[分析推断]** 时间序列内的相对 pattern 不会自动识别 workload、release、用户行为等外部语义状态。

## 4. Core Idea

- **[作者主张]** 以 Relative Context Discrepancy 学“token 与当前 sequence context 的关系是否异常”；用 context-dependent synthetic labels 打破形态与标签固定绑定。（§2.1–2.3）

## 5. Technical Innovations

1. **[作者主张] RCD**：token 与长时上下文建立 pairwise relation，经 Transformer self-attention 聚合；contextual relational deviation 交 anomaly head 分类。（Appendix C.1–C.4, pp.21–22）
2. **[作者主张] Variate-window Transformer**：instance-normalized multivariate series 切成 patch 16，flatten 各 channel-window tokens，使 attention 可跨时间 / channel 建模；8 层、8 heads。（§2.2; Appendix D.5）
3. **[作者主张] 合成语料**：随机 trend + multi-wave seasonality + volatility → DAG / lagged ARX 多变量关系 → 20+ temporal 与 causal violations → root / descendants token labels。（§2.3, p.5; Appendix B）
4. **[作者主张] 双头分工**：15% patch masking 的 reconstruction 作训练 scaffold；联合 BCE anomaly supervision；inference 移除 reconstruction head，仅用 anomaly head。（§2.2, Eq. 1; Appendix C.4）

## 6. Key Mechanisms

- **[实验支持]** 固定 5k context 的主结果：64 个 zero-shot dataset-metric case 中 TimeRCD 38 次第 1、14 次第 2；与 full-shot baseline 比较为 35 次第 1、3 次第 2。（Table 1, pp.6–7）
- **[实验支持]** 纯 contextual anomaly synthetic test 上 Standard-F1 0.827，竞争 zero-shot model 在该 split 明显降低；point anomaly 上保持竞争力。（§3.3; Appendix E.2）
- **[实验支持]** joint reconstruction + anomaly training 但 anomaly-head inference 的 UCR VUS-PR 33.57；改用 reconstruction-error inference 降为 4.08，支持两者功能区分。（Appendix E.5, Table 3）
- **[实验支持]** synthetic context anomaly corpus 优于 generic / real data + DADA injection ablations；2.5B generally improves over 350M / 700M，但非每个 dataset-metric 单调。（Table 2, p.8; Appendix E.4）

## 7. Experimental Evidence

- **[实验支持]** 16 datasets、4 metrics（Affiliation-F1、F1-T、Standard-F1、VUS-PR）；主比较固定 5k context、zero-shot。（§3.1–3.2）
- **[实验支持]** window sensitivity 在 1k–13k 显示 context 最优值随数据而变；MovingVar 在部分 variance-sensitive benchmark 有竞争力。（§3.2–3.3; Appendix E.3）
- **[证据边界]** 专门 contextual test 由同一个 synthetic generator 家族构造；支持受控 context claim，但没有完成真实域外业务 context validation。

## 8. Limitations

- **[作者指出]** 同一个 inference window 若含很多 anomaly，异常可被纳入 context；作者报告 Stock 上频繁 outlier 可能被当成正常背景。（§3.3 / Discussion）
- **[作者指出]** 固定 5k 不是 universal optimum；reconstruction scaffold 理论角色与 Transformer 长序列效率仍是可研究问题。（Appendix E.3, G; Discussion）
- **[分析推断]** synthetic DAG、ARX 与 intervention 不等于真实服务拓扑、业务活动或故障因果；模型未读 Trace / release / workload metadata。
- **[分析推断]** 规模大且纯 synthetic 的预训练结果需要独立 generator family / 真实域检验，排除模型 benchmark leakage 也应严格核对。

## 9. Research Opportunities

- **[分析推断]** 研究 context 污染检测、多个 reference state / robust consensus，使长窗中 anomaly 密集时不把故障吸收入 normality。
- **[分析推断]** 在真实业务的 workload / release context 下比较“序列内相对模式”与“业务状态条件化 normality”，测试负载变化与故障并发。
- **[分析推断]** 对合成机制做 generator-held-out、拓扑-held-out 和真实 Trace / fault injection 外部验证。
- **[分析推断]** 固定 5k 主协议下补充业务 false-alarm budget、事件延迟、显存 / latency 预算与 threshold calibration。

## 10. Related Papers

- **IMPACT**：少量 labeled anomaly 的 open-set supervised learning + validation risk influence；与 RCD zero-shot 内部 context 对照。
- **When Model Meets New Normals**：test-time adaptation 学新正常；RCD 推理时在输入 context 内部比较但不更新目标模型。
- **CAPMix**：动态 KPI / 噪声与正常变化建模，可对比业务 context 与合成上下文先验。
- **CrossAD / MACE / Graph-MoE**：分别从 cross-window、频谱多模式、memory routing 提供正常参照机制。
- **TSB-AD / Quo Vadis**：评测与 protocol 依据，提醒区分 zero-shot、full-shot、metric 和 threshold 口径。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[TimeRCD PDF](../../sources/papers/tsad-2024-2026/2026/ICML/Towards_Foundation_Models_for_Zero_Shot_Time_Series_Anomaly_Detection_Leveraging_Synthetic_Data_and_Relat.pdf)
- 代码：[TimeRCD repository](https://github.com/thu-sail-lab/Time-RCD)
- Proceedings：[PMLR 306](https://proceedings.mlr.press/v306/lan26b.html)
