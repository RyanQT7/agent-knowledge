# 知识卡片：Delving into Large Language Models for Effective Time-Series Anomaly Detection

> 标记：**[作者主张]** 论文解释 / 方法；**[实验支持]** 表格或分析直接支持；**[分析推断]** 本知识库判断。页码按 NeurIPS 2025 PDF。

## 1. Research Scenario

- **[作者主张]** 对零样本 LLM / MLLM TSAD 做 failure analysis，分别研究异常理解和区间定位，再通过预处理与 prompt 改善模型。（§2–3, pp.2–6）
- **[实验支持]** AnomLLM 4 类 synthetic anomalies、TSB-AD-U 短序列子集，以及 ETTh2 / Electricity context case。（§4–5）

## 2. Core Challenges

- **[作者主张]** trend / frequency anomaly 被季节背景遮挡；LLM 用 raw text 时还须从数值 token 计数出时间位置。（§2.1–2.2, pp.3–4）
- **[实验支持]** GT 在图上标出异常后 localization 仍有明显错误；输入索引能改善返回端点。（Fig. 3; Table 4, pp.4, 9）

## 3. Existing Limitations

- **[作者主张]** 既有 zero-shot prompting 易把正常波动报成异常，图像 prompt 又偏向显著 spike 而漏掉细节。（§1–2, pp.1–4）
- **[分析推断]** 只依靠独立时序 / 图像 prompt 无法判断某个真实业务变动是否被事件上下文解释。

## 4. Core Idea

- **[作者主张]** 统计分解先移除主要周期项 $s_t$，再把 index-value text 和 plot image 一起给 LLM；不训练模型参数。（§3, Fig. 4）

## 5. Technical Innovations

1. **[作者主张] Failure diagnostics**：instance-level 二分类测理解；输入标出 GT 的定位任务测 coordinate localization。（§2, Figs. 2–3）
2. **[作者主张] De-seasonalization**：用 ACF 选 dominant period $P^*$，做 $x_t=s_t+\tau_t+r_t$，仅输入 $x_t-s_t$。（§3.1, p.5）
3. **[作者主张] Index-aware text**：显式将观测位置与数值配对，把隐式 token counting 改为 index lookup。（§3.2, pp.5–6）
4. **[作者主张] Context filtering**：让 LLM 按文字背景剔除可解释、无关心的异常模式。（§5.2）

## 6. Key Mechanisms

- **[实验支持]** 去掉季节分解使平均 standard F1 下降 5.64 points；去掉索引降 23.36 points；去掉数值 text / 图像分别降 16.88 / 14.24。（Table 3, p.8）
- **[实验支持]** AnomLLM 上 GPT-4o / Qwen text+vision standard F1 为 70.04 / 67.56，zero-shot vision 对照为 42.03 / 46.65。（Table 1, p.7）
- **[实验支持]** Qwen 的 GT localization diagnostic 中 index-aware F1 60.16、6.45s；index-free F1 20.33、29.79s。（Table 4, p.9）
- **[实验支持]** TSB-AD-U 表中 GPT-4o standard F1 34.20、Affiliation F1 74.64、140.63s；SR + MAD 是 30.57 / 75.94 / .02s。（Appendix Table 9）

## 7. Experimental Evidence

- **[实验支持]** 21 prompt variants、四个 MLLM、standard 与 affiliation metrics；另测 16 种 conventional / foundation model detector。（§4–5）
- **[实验支持]** 作者报告提示方法相对其他 prompts 平均改善 39.9%、最高 66.6%；模型间差异明显，InternVL improvement 仅 +.99 F1 point。（摘要; Table 2, p.8）
- **[实验支持]** ETTh2 / Electricity qualitative cases 支持 LLM 可按人工构造的 event context 排除已知模式。（§5.2, Fig. 8）
- **[协议边界]** TSB-AD-U 只评 8 个短类别；传统方法按三种 threshold 中最优者比较；GT localization table 不是无监督 detector 结果。（§5.1; Table 4）

## 8. Limitations

- **[作者说明]** LLM latency 高，不适于 real-time 批量检测。（§5.1）
- **[分析推断]** 单一 dominant period 在多周期 / 非平稳 seasonal patterns 下可能失准；时序状态变化可能被预处理改变。
- **[实验边界]** context 是合成 / 人工措辞的解释，没有来自真实 Metric、Trace、release 的上下文，也未测试过滤已知波动时对未知故障召回的影响。
- **[实验边界]** context 结果是少量 qualitative cases；prompt、API model revision、selected TSB categories 会影响复现与泛化。

## 9. Research Opportunities

- **[分析推断]** 结合可信业务事件、负载、Trace 与时间窗，评估正常变化、真实故障、并发和未知事件四种条件。
- **[分析推断]** 用多尺度 / 在线周期分解，同时检查去 seasonal 前后 anomaly evidence，避免把频率故障抵消。
- **[分析推断]** LLM 负责低频 context adjudication，传统低延迟 detector 做第一阶段筛选；用固定 false-alarm budget 和 event delay 比较成本。

## 10. Related Papers

- **AnomalyLLM**：LLM embedding teacher + prototype student distillation；本篇只改输入，推理更慢但无需训练。
- **AnomSeer**：MLLM post-training，以专家统计 reasoning trace 训练 detection、classification 和 explanation；本篇不训练模型。
- **TSB-AD / Quo Vadis**：共同提醒逐点 / event metrics 与 threshold protocol 不应混用。
- **MACE / When Model Meets New Normals / CAROTS**：显式建模多正常模式、测试时适应和因果增强；本篇主要分解 stable periodicity。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[NeurIPS paper PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf)
- 代码：[LLM-TSAD repository](https://github.com/junwoopark92/LLM-TSAD)
- Proceedings：[NeurIPS 2025 paper](https://doi.org/10.52202/085713-3444)
