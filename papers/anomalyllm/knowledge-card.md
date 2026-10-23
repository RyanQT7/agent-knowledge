# 知识卡片：AnomalyLLM

> 标记：**[作者主张]** 论文的机制 / 解释；**[实验支持]** 结果表或消融直接支持；**[分析推断]** 本知识库的批判性判断。页码按 IJCAI 2024 PDF。

## 1. Research Scenario

- **[作者主张]** 小样本、无监督的单变量 / 多变量 TSAD：用预训练 GPT-2 teacher 的表示作为通用参照。（§1–3, pp.1–4）
- **[实验支持]** 9 个 UCR domain groups 与 SMD、MSL、SMAP、PSM、GECCO、SWAN 六个 multivariate sets。（§4.1, Tables 1–2）

## 2. Core Challenges

- **[作者主张]** 常规 self-supervised 方法在少量样本下难学通用表示；teacher 与 student 都只用正常数据拟合时，可能连异常也学得相似。（§1–2, p.2）
- **[分析推断]** 以局部扰动近似异常，面临扰动类型与真实故障 / 合法业务波动不一致的风险。（§3.4）

## 3. Existing Limitations

- **[作者主张]** 仅训练 student 拟合通用 teacher 会使 student 对未见异常也过度泛化。（§2, p.2）
- **[分析推断]** prototype 能记忆常见形态但不包含 workload / 业务状态语义，检测差距不能解释波动来源。

## 4. Core Idea

- **[作者主张]** 让 teacher、student 在正常窗口上表示接近；prototype 帮 student 拟合常见模式；合成异常增大两者差距。测试用 $\|z-c\|_2^2$。（§3, Eqs. 1–8, pp.3–5）

## 5. Technical Innovations

1. **[作者主张] GPT-2 teacher**：时序 patch 经过独立线性投影输入 GPT-2；freeze attention / FFN，只微调 positional embedding、LayerNorm。（§3.3, p.4）
2. **[作者主张] Prototype student**：每个变量维护可训练 prototype pool，按 cosine similarity 逐通道取最相似 prototype；作为 Transformer 的额外 key/value。（§3.2, Eqs. 2–4）
3. **[作者主张] 合成异常 distillation loss**：原始窗口对齐，扰动窗口分离；teacher 对原始和扰动视图加 cosine consistency。（§3.4, Eqs. 5–7）
4. **[作者主张] Discrepancy score**：teacher / student embedding 平方距离。（Eq. 8）

## 6. Key Mechanisms

- **[实验支持]** UCR 总 accuracy .820、AF1 .858；NCAD 为 .663 / .767。（Table 3, p.6）
- **[实验支持]** prototype TST 对比 TST 的 AF1 提升 14.7%；加入 teacher consistency 优于不增强和额外 student consistency 设置。（§4.4, Fig. 5, pp.6–7）
- **[实验支持]** PowerDemand 单数据集 F1 从 full-data .886 降至 zero-shot .650。（Table 6, p.7）
- **[论文口径提示]** 多变量 Table 4 是 adjusted F1；WaQ / SWAN Table 5 的结果分别为 .620 / .804，正文却误写其中一项为 GECCO。（§4.3, Tables 4–5, p.6）

## 7. Experimental Evidence

- **[实验支持]** 9 个 UCR domain groups 与 6 个多变量 dataset；比较 10 个方法；给出 teacher、student、训练策略和超参数分析。（§4, Tables 1–6）
- **[实验支持]** 主配置为 32 prototypes；敏感性文字称 48 prototypes 最有效，配置需复核。（§4.2, Fig. 4, pp.5, 7）
- **[证据边界]** 结果使用不同的 affiliation / adjusted F1 protocol；没有 workload、Trace 或故障并发验证。

## 8. Limitations

- **[作者说明]** GPT-2 teacher 资源开销较高；未来可研究轻量 teacher。（§5, p.8）
- **[分析推断]** 局部 jitter / scale / warp 不是经标注的真实故障模拟，难知其对正常高波动的误报行为。
- **[分析推断]** 原型表示形态而非运行状态语义，未见合法状态变化也可能造成 discrepancy。
- **[复现风险]** 32 vs 48 prototype 和 WaQ vs GECCO 文字 / 表格口径存在差异。

## 9. Research Opportunities

- **[分析推断]** 将 prototype 按 workload / release / service state 条件化，并设计保护机制阻止疑似故障污染更新。
- **[分析推断]** 把正常状态切换、单独故障、状态切换与故障并发做成受控实验；报告 validation-only threshold 和事件延迟。
- **[分析推断]** 公开统一复现配置，拆分 prototype、teacher prior、扰动语义的贡献。

## 10. Related Papers

- **Delving into LLMs for TSAD**：prompt-only，解决季节干扰和位置定位；本方法通过训练好的表示差距检测。
- **AnomSeer**：visual MLLM + ExpCoT/TimerPO 产生类型、区间和文本推理；本方法只输出异常分数。
- **CAROTS / MACE / When Model Meets New Normals**：分别提供因果约束、多模式频谱参照、测试时新正常适应机制。
- **TSB-AD / Quo Vadis**：用于审视其多套 F1 协议与测试运行点。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[AnomalyLLM PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Large_Language_Model_Guided_Knowledge_Distillation_for_Time_Series_Anomaly_Detection.pdf)
- IJCAI proceedings：[paper 0239](https://www.ijcai.org/proceedings/2024/0239.pdf)
