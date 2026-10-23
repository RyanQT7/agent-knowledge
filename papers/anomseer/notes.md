# AnomSeer: Reinforcing Multimodal LLMs to Reason for Time-Series Anomaly Detection

## 1. Metadata

- **Authors**: Junru Zhang, Lang Feng, Haoran Shi, Xu Guo, Han Yu, Yabo Dong, Duanqing Xu
- **Year / Venue**: 2026 / ICML（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2026/ICML/AnomSeer_Reinforcing_Multimodal_LLMs_to_Reason_for_Time_Series_Anomaly_Detection.pdf)
- **Proceedings**: [PMLR 306 paper page](https://proceedings.mlr.press/v306/zhang26aw.html)
- **Code**: [AnomSeer repository](https://github.com/jrzhang33/AnomSeer)（PDF p.1）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

AnomSeer 以 Qwen2.5-VL 将时序图像输入映射为分类、异常区间和自然语言分析；训练时从带标签的合成序列构造使用 classical TSAD probes 的 ExpCoT 轨迹，再用 TimerPO 在 GRPO 的 outcome advantage 外增加 token-level optimal-transport reasoning reward，并把辅助 advantage 在 advantage 空间正交化后更新策略。（§§3–5, Eqs. 1–8, PDF pp.2–9）

## 3. Background and Problem Definition

作者指出视觉 MLLM 可利用 plot 进行整体模式感知，但容易凭粗糙视觉启发式识别显眼 spike，难以分析细小 frequency shift、trend drift 或局部 contextual point。论文把任务设置为多模态 TSAD：序列 $X$ 被渲染成图像 $I$，并附文字 instruction/context $c$；模型 autoregressively 输出类别、异常区间和解释。（§§1–3, Fig. 1–2, pp.1–4）

五种目标 anomaly type 为 global point、contextual point、trend、seasonal/frequency、shapelet/subsequence。作者将“检测 + 分类 + 解释”统一到一个模型生成流程，但检测范围与类型标签使用 benchmark 注释评价。（§3, Appendix B.1 / C.1）

## 4. Core Challenges

1. **仅有最终答对 / 答错 reward 太粗**：模型可能只学会显眼全局 outlier，不学细粒度频率、趋势与定位证据。（§1, §4.2）
2. **时序专家证据需转成 MLLM 可学信号**：不同 anomaly type 需适配不同数值检验与时间尺度。（§4.1）
3. **推理辅助目标可能与主检测目标冲突**：共享标签监督时，简单相加可能把次要 trace similarity 变成错误更新方向。（§4.2）
4. **reasoning 质量难定量**：文本轨迹长短和表述差异较大，不能只按词面重合比较。（§4.2）

## 5. Architecture Overview

```text
训练（AnomLLM synthetic train，3,200 labeled samples）
  ├─ 图像序列 + GT anomaly type / intervals
  ├─ classical probes → ExpCoT: Observation → Reasoning & Validation → Conclusion
  ├─ Qwen2.5-VL 采样一组 G 个回答
  ├─ task reward: format + type + localization → group-normalized A_main
  ├─ token embedding cosine cost + Sinkhorn OT(model trace, ExpCoT) → A_TsR
  ├─ A_TsR 对 A_main 正交投影 → A_final = A_main + α A_TsR⊥
  └─ clipped RL objective + KL regularization 更新 MLLM

推理：时序 plot + instruction/context → 单次端到端输出思路、类型和区间
```

（Fig. 2–3, §§4–5, Eqs. 1–8, PDF pp.4–7）

## 6. Method in Detail

### 6.1 输入、输出和 anomaly taxonomy

输入为 line-plot 图像和文本 context / task instruction。模型按 token 顺序输出结构化结果：`<think>` 内的分析、`<class>` 的 anomaly category 和 `<answer>` 中的区间端点（prompt 见 Appendix B.1, Fig. 7）。论文主要实验使用 univariate series，图像尺寸为 $805\times124$，不在 plot 上标记 GT anomaly。（§3, Appendix B.1 / C.4, pp.3–4, 18）

### 6.2 ExpCoT：以 classical analysis 生成结构化参考推理

ExpCoT 的流程为 **Observation → Reasoning & Validation → Conclusion**。观察阶段作 global → structural → local 扫描：全局值分布 / histogram-based outlier score；平滑 gradient 和周期性 FFT；再看局部 subsequence discord / Matrix Profile。推理与验证阶段根据**GT anomaly type**选 targeted probe，把定量数值转成可读证据；结论整合证据并返回 GT 类型和区间。（§4.1, Fig. 2, pp.4–5；Appendix B.2, pp.13–16）

五类 probe 包括：

- **Global point / out-of-range**：检查 $[\mu-k\sigma,\mu+k\sigma]$ envelope 超界，并合并连续越界区间。（Appendix B.2）
- **Contextual point**：用 fixed-length、z-normalized subsequence 的 Matrix Profile 找最大 discord $i^*=\arg\max_i d(i)$；标准化 discord score，若最高 $z>\tau$（示例 $\tau=3.5$）作为局部证据。（Appendix B.2）
- **Trend shift**：对平滑序列计算 gradient $g_t$，标出超出 gradient dispersion threshold 的片段并合并。（Appendix B.2）
- **Seasonal / frequency**：在滑窗 periodogram 中估主周期，找偏离 median $\pm k\cdot1.4826\,MAD$ 的窗口后映回时间区间。（Appendix B.2）
- **Shapelet / subsequence**：Matrix Profile discord 搜索，并可检查附近窗口长度的跨尺度稳定性。（Appendix B.2）

**监督边界**：Appendix B.2 明确说 ExpCoT 每条样本由 ground-truth class 和 temporal annotation 生成；Conclusion 也保留 GT 区间作为最终定位。 traces 先自动生成，再由人类专家润色。因此它不是无标签自监督的 reasoning source；训练用的 $3,200$ synthetic examples 带 anomaly 类别 / 区间监督。推理时不需要 ExpCoT 或外部 detector，但训练期目标答案已进入参考 trace。（Appendix B.2, PDF pp.13–14；§5, p.7）

### 6.3 TimerPO：outcome-aware advantage

对输入 $(I,c)$ 一次采样 $G$ 个 candidate responses。每个回答获得三项任务奖励：输出格式是否可解析 $r_{fmt}$、anomaly type 正确性 $r_{cls}$、检测定位 reward $r_{loc}$（整合 TSAD localization metrics）。加权得到

$$r_i=\lambda_{fmt}r_{fmt,i}+\lambda_{cls}r_{cls,i}+\lambda_{loc}r_{loc,i}. \tag{1}$$

再在 group 内按均值 / 标准差归一化为 $\hat A^i_{main}$（Eq. 2）。这给出相对候选组的 task outcome signal，而非跨 prompt / dataset 的绝对置信分数。（§4.2, Eqs. 1–2, pp.5–6）

### 6.4 Token-level optimal transport reasoning advantage

对生成轨迹 $y^i$ 与该样本 reference ExpCoT $y^*$，取模型最终层 token embedding $e_n^i,e_m^*$。定义 token cosine-distance cost：

$$C^i_{nm}=1-\frac{e_n^i\cdot e_m^*}{\|e_n^i\|\|e_m^*\|}. \tag{3}$$

以生成概率归一化得到两个 token-position marginals $u^i,v$，计算 transport plan：

$$W_i=\min_{P_i\in\Pi(u^i,v)}\langle P_i,C_i\rangle_F. \tag{4}$$

作者用 entropic-regularized Sinkhorn–Knopp 近似。再把低 transport cost 转成 reasoning reward $r^i_{TsR}=\exp(-W_i/\tau)$，并对 group 内 reward 做标准化得到 $\hat A^i_{TsR}$（Eq. 5）。这样比 token-by-token exact match 容忍不同词句与长度，也保留 token embedding 语义关系；但它优化的是与带标签构造的 ExpCoT 表示对齐，不等同直接证明文本解释忠实于模型内部因果证据。（§4.2, Eqs. 3–5, pp.5–6；后一判断为分析推断）

### 6.5 Advantage 正交化与 RL update

为避免 reasoning reward 重复或干扰 task reward，将 $\hat A_{TsR}$ 在 group 向量空间内投影到 $\hat A_{main}$ 的正交补：

$$\hat A^{\perp}_{TsR}=\hat A_{TsR}-\frac{\langle\hat A_{TsR},\hat A_{main}\rangle}{\|\hat A_{main}\|_2^2+\epsilon}\hat A_{main}. \tag{6}$$

最终 advantage 为

$$A^i_{final}=\hat A^i_{main}+\alpha(\hat A^{\perp}_{TsR})_i. \tag{7}$$

作者将其替换进 clipped policy objective，并保留 $\beta KL[\pi_\theta\|\pi_{ref}]$ regularizer（Eq. 8）。因此，正交化作用于 response-group advantage，不是直接对网络参数梯度做 PCGrad；其“主方向不变”是公式设计主张，实践效果由 ablation 比较支持。（§4.2, Eqs. 6–8, pp.6–7）

### 6.6 训练 / 推理设置

作者称方法为 pure RL post-training：不做 SFT cold start、不改模型结构；训练先生成 ExpCoT，再按 TimerPO 训练 Qwen2.5-VL-3B / 7B。主设置 $G=5$、PPO clip $\epsilon=.2$、reward weights $\lambda_{fmt}=.1,\lambda_{cls}=.2,\lambda_{loc}=.7$、$\alpha=.3$。Appendix Table 4 另列 max response 1024、batch / mini-batch 128、KL .001、learning rate $10^{-6}$。（§5, Appendix C.4, Table 4, pp.7, 19）

## 7. Experimental Design and Evidence

### 7.1 Benchmarks / baselines / metrics

- **训练**：只用 AnomLLM 的 3,200 synthetic instances，生成 GT-based ExpCoT。（§5, p.7）
- **测试**：AnomLLM synthetic；VisualTimeAnomaly mixed synthetic-real image benchmark（含训练未见的 shapelet）；TSB-UAD real-world univariate collection。论文附录称 TSB-UAD 合并 1,635 条 univariate series，跨工业传感器、医学、金融、web traffic。（§5; Appendix C.1, p.15）
- **基线**：GPT-4o / mini、Gemini-2.5 Pro / Flash，Qwen2.5-VL 3B–72B、SigLLM、TimeMaster，以及 SFT 3.2k / 32k。（§5）
- **指标**：anomaly type classification accuracy 与 label-based Affinity precision / recall / F1；每结果 3 runs。Affinity 适合由模型直接输出的离散区间，但与 point-wise score threshold 指标不相同。（§5, Appendix C.3）
- **算力**：3B 训练用 4×A100 / 4×A6000；7B 用 4×H100。作者报告 3B 训练需 12.4 hours，单 GPU 约 7GB、平均 4.8 秒 / sample inference。（Appendix C.5 / D.1, pp.19–20）

### 7.2 主结果

- **AnomLLM Table 1**：平均 Affinity F1，TimeMaster-3B 为 71.9；AnomSeer-3B 为 79.3；AnomSeer-7B 为 84.4。频率异常上 3B F1 为 58.9、7B 为 60.8，GPT-4o 为 10.9，显示增益重点在数值细节难题；仍应限定在训练分布 / 指定生成设置。（§5.1, Table 1, PDF pp.7–8）
- **训练数据量**：从 1k 增至 5k synthetic examples 时平均 Affinity F1 仍提升，作者称尚未饱和；说明当前小规模数据的 scaling curve 仍向上，不能据此推断真实领域迁移会持续同步提升。（Appendix D.2, Fig. 13）
- **跨集泛化**：只在 AnomLLM synthetic 训练，在 VisualTimeAnomaly 与 TSB-UAD 评估；作者报告对未见 shapelet 类别也有较好表现、真实 TSB-UAD 上优势持续（Fig. 6, p.8）。主文图未给出与 Table 1 同样完整的分类明细，故不在此补读 / 推算精确数值。
- **补充实验**：Appendix Table 7 的 multivariate synthetic / real-world Affinity F1 中，7B 为 83.5 / 72.4，对比 GPT-4o 62.7 / 54.2；short/boundary anomaly targeted augmentation 结果由 56.2 提至 75.8。（Appendix D.4, p.21）

### 7.3 Ablation 与 mechanism evidence

- **ExpCoT / orthogonalization**：全方法 3B anomaly-type F1 分别为 frequency 58.9、trend 84.9、range 85.6、point 87.8。移除 ExpCoT、reasoning advantage 或 orthogonalization 均下降；纯 GRPO-style 结果为 50.4 / 77.8 / 81.8 / 80.6。（§5.2, Table 2, pp.7–8）作者正文还报告用 GPT-4o 生成的通用 CoT 替换 ExpCoT 后、特别是频率异常表现明显下降。
- **orthogonalization alternatives**：TimerPO 平均 F1 79.3，weighted-sum 75.9、PCGrad 76.3。（Appendix D.3, Table 6, p.20）
- **OT alternatives**：OT 平均 F1 79.3；token cosine similarity 71.7，CLIP-style 73.4。此对照支持采用 OT 作为对齐奖励的收益，但仍依赖 reference traces 质量。（Appendix D.3, Table 6）
- **reasoning pattern**：Figure 5 / Appendix Fig. 12 显示训练前后表征分布更贴近 ExpCoT，词使用从 global / sudden / change 转向 timestamp / intervals / amplitude。（§5.3, pp.8, 20）这是 distribution / token usage evidence，不是对每个解释都逐条验证其因果忠实度。
- **失败案例**：附录展示末端短 trend anomaly `[998,1000]` 被判正常；作者指出需要改进 boundary sensitivity。（Appendix D.7, p.21–24）

## 8. Contributions and Reproduction Value

1. 提出将 classical TSAD 统计证据结构化为 MLLM 的 ExpCoT 训练参考。（§4.1）
2. 提出 TimerPO：token embedding OT reasoning reward 与 advantage-space orthogonalization。（§4.2, Eqs. 3–8）
3. 对比不同规模 MLLM、SFT、GRPO 和替代 alignment / projection，并用三种 benchmark 检验迁移。（§5, Appendix D）
4. 有公开 [代码](https://github.com/jrzhang33/AnomSeer)、数据配置、超参数、硬件、confidence intervals 和失败案例，可复核方法；这里仅记录 paper 的复现条件，不执行训练或复现实验。

主要复现成本是专家 trace 生成及人工润色、多卡 RL 训练、API 基线版本、ExpCoT 统计阈值 / 区间规则、Sinkhorn 温度与正则、anomaly interval 转 Affinity metrics 的细节。无 SFT 不代表无标签：其训练 trace 来自 anomaly class 与 temporal annotations。（Appendix B.2, C–D）

## 9. Limitations and Critical Reading

- **[作者说明]** 论文主要围绕 univariate TSAD；复杂 multivariate joint structure 仍需后续研究。作者建议按变量渲染 subplot 并建模联合结构，也提出加入解释 anomaly dynamics 的 external knowledge。（§6, p.9）
- **[实验支持]** 主训练集是 3,200 合成标注样本；虽然跨 benchmark 测试，训练标签和 reference traces 明确由 GT 类别与区间构造。（§5; Appendix B.2）
- **[分析推断]** ExpCoT 的 GT localization 既用于选 targeted test，也在最终结论中保留作目标 interval；OT reward 因此部分对齐到包含目标答案的训练参考，不能解释为无需监督的自主发现统计证据。
- **[分析推断]** 输出解释可以复述统计量和已知 GT，但 paper 并未用额外的 independent expert review / perturbation test 充分验证每个 generated rationale 的 faithfulness 或因果正确性。
- **[评测边界]** Affinity F1 以离散区间衡量 event proximity；没有在统一 validation-only threshold、生产告警预算、长流 latency / false alarm cost 下与传统连续 score detector 做完整比较。
- **[方法边界]** input definition 含 context $c$，但主要 benchmark 是 taxonomy / prompt-defined anomaly task；并未系统输入和消融真实 workload、release、Trace 或业务事件信息。多变量附录是补充实验，不能替代 multivariate real workload state transition validation。
- **[实现边界]** short/boundary appendix 通过 targeted augmentation 改善，但附录仍展示最末端极短故障未检出，边界定位未被彻底解决。（Appendix D.4, D.7）

## 10. Related Papers

- **AnomalyLLM**：GPT-2 teacher + prototype student 的 discrepancy detector；AnomSeer 改为视觉生成模型的 post-training，直接输出类别、区间、解释。
- **Delving into LLMs for TSAD**：分析 zero-shot 理解与 localization，并用去季节和索引改 prompt；AnomSeer 用带 GT 的专家 trace / RL 训练来加强 reasoning。
- **Harnessing Vision-Language Models for TSAD**：同属 image + MLLM 路线，但侧重 VLM detector 结构 / memory；可作为 post-training 对比。
- **TSB-AD / Quo Vadis**：说明不同 anomaly benchmark、range metric、阈值协议对结果解读的影响。
- **TFC / TFMAE / MACE**：都利用 trend / frequency 证据，AnomSeer 将类似信号通过 trace reward 教给生成模型。

## 11. Questions for Further Reading

1. 若 ExpCoT 的 targeted test 和最终定位直接使用 GT 类别 / 区间，训练与真正无标签或弱监督部署之间的差距多大？
2. 能否对生成 explanations 做 blinded expert factuality review、counterfactual perturbation 和 GT-independent evidence verification？
3. 当正常 workload / release 切换与真实故障并发时，ExpCoT 会将哪类结构变化认作异常？加入事件 context 是否提升或抑制未知故障 recall？
4. 多变量模型怎样联合呈现变量关系、时间顺序、Trace / topology，并验证语言解释与已知因果路径相符？
5. 在固定 false-alarm budget、长序列、边界短事件、实时延迟与开放集 anomaly 下，Affinity-F1 的提升是否保留？
6. 增加 synthetic trace 数量后，性能是否改善真实数据、还是扩大对 AnomLLM 的规则 / 生成器依赖？

## 12. Key Terms

- **ExpCoT**：从带 anomaly label / interval 的序列与统计诊断生成的结构化 expert reasoning trace。
- **TimerPO**：在 GRPO outcome reward 上加入 OT-based reasoning advantage，并在 advantage space 投影正交分量。
- **Outcome-aware advantage**：在同一组采样回答间标准化的格式、分类、定位任务 reward。
- **Affinity metrics**：按异常事件时间邻近关系计算的 precision / recall / F1。

## 13. Tags

`TSAD` `MLLM` `reinforcement learning` `optimal transport` `ExpCoT` `reasoning reward` `anomaly localization` `synthetic supervision`
