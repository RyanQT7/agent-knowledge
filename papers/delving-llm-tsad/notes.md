# Delving into Large Language Models for Effective Time-Series Anomaly Detection

## 1. Metadata

- **Authors**: Junwoo Park, Kyudan Jung, Dohyun Lee, Hyuck Lee, Daehoon Gwak, ChaeHun Park, Jaegul Choo, Jaewoong Cho
- **Year / Venue**: 2025 / NeurIPS（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf)
- **Proceedings**: [NeurIPS 2025 paper](https://doi.org/10.52202/085713-3444)
- **Code**: [LLM-TSAD repository](https://github.com/junwoopark92/LLM-TSAD)（论文首页）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

论文把 LLM-based TSAD 拆成时序理解和异常定位，先用实例级检测及 GT-highlighted localization diagnostic 定位失败来源，再在输入前去除估计出的 seasonal component，并在文本 prompt 中给每个数值显式附 index；这种不训练模型的输入设计提升 AnomLLM 上的 prompt 结果，而真实 TSB-AD-U 小子集和上下文实验同时暴露出 LLM 推理时延与 context evidence 的边界。（§§2–5, Eqs. 1–2, Tables 1–4, PDF pp.3–11）

## 3. Background and Problem Definition

作者观察到，文本输入时 LLM 经常把噪声或普通波动报成异常；图像输入更容易抓住醒目的 spike，却容易错过趋势、频率等细微变化。论文将 TSAD 任务拆为：(1) 判断是否理解序列动态并区分 normal / abnormal；(2) 把判断落到精确区间。若模型甚至在不需要定位的实例级二分类中漏掉异常，代表理解不足；若 GT 区间已在图上高亮仍无法准确返回区间，代表定位也有独立瓶颈。（§2, Figs. 1–3, pp.2–4）

方法沿用 zero-shot LLM：不给模型领域训练数据，输入序列文本、图像或二者，令 LLM 输出异常区间。它不改模型权重，而用统计预处理与 prompt formatting 调整输入结构。（§3, pp.4–6）

## 4. Core Challenges

1. **季节性遮挡细微异常**：稳定季节项与 trend / frequency shift 叠加时，LLM 难直接从原始输入找出微弱变化。（§2.1, §3.1）
2. **模型不会可靠地按数值 token 计数**：只给无索引数值序列时，模型须隐式计算 anomaly 的 start/end 位置。（§2.2, §3.2, Fig. 5）
3. **输入模态各有缺陷**：image 的 x-axis 位置感不精确，raw text 的数值位置隐式，混合模态也不能保证改进所有模型。（§2–4）
4. **LLM 精度与实际使用成本有差距**：生成文本区间耗时远高于传统 detector；context-aware 输出还须检验是否漏掉未见故障。（§5）

## 5. Architecture Overview

```text
输入时序 x[1:T]
  ├─ ACF(k), k=1…floor(T/2) → 主周期 P* = argmax ACF(k)
  ├─ additive decomposition x = s + τ + r → 只去 seasonal: x̃ = x − s
  ├─ 输出为 (index, value) 文本 + time-series plot image
  └─ 零样本 LLM → 异常 interval JSON / list
```

（Fig. 4, §3, PDF pp.4–6）

## 6. Method in Detail

### 6.1 失效分析：理解与定位分开诊断

- **实例级 TSAD**：把区间检测简化为一条序列是否含 anomaly 的二分类，不要求精确 localization。使用四类 anomaly 的 1,600 个序列（每类 400），比较 21 种 prompt。trend shift 和 frequency change 上模型常只略高于、甚至不优于常数分类器；image 对明显 point / range 的表现较好。（§2.1, Fig. 2, PDF pp.3–4；实验细节 Appendix D.1）
- **GT localization diagnostic**：在输入图上标出真实 anomaly 区间，只要求返回坐标。整体结果仍有定位误差，且频率型异常往往由许多分散片段构成，输出端点困难。（§2.2, Fig. 3, PDF p.4）

这两种实验用于诊断模型能力，不是部署方法：第二项显式提供了真实位置，不能用来代表正常在线检测性能。（§2.2）

### 6.2 Seasonal decomposition

对输入 $x_{1:T}$ 计算 lag $k=1,\dots,\lfloor T/2\rfloor$ 的 sample autocorrelation $\hat\rho(k)$，取

$$P^*=\arg\max_{k\ge1}\hat\rho(k).$$

用 $P^*$ 作窗口长度作经典加性分解

$$x_t=s_t+\tau_t+r_t,$$

其中 $s_t$ 为 seasonality、$\tau_t$ 为 trend、$r_t$ 为 residual。只将 $s_t$ 从原序列减掉，输入 $\tilde x_t=x_t-s_t$；剩余序列以 text 和 image 输入 LLM。作者选择“只去 seasonal”是为了突出微弱 trend / frequency deviations，不在预处理阶段把这些变化也消掉。（§3.1, PDF p.5）

论文称用 FFT 实现可达 $O(T\log T)$ 且相较 LLM 推理开销很小，也讨论可换 STL、Seasonal-HODMD 或 Prophet。Table 3 的消融表明移除该步骤后，三种 LLM 的 standard F1 平均下降 5.64 points。（§3.1–4.2.1, Table 3, pp.5, 8）

### 6.3 Index-aware prompt

对文本输入显式写成位置和值配对，例如 $(t,x_t)$，使模型能直接回报区间端点，而不再从长序列内数 token。索引使输入长度近乎翻倍，但能把脆弱的隐式 counting 转成 lookup。图像无法方便叠加密集索引（会重叠、杂乱），所以索引主要加在文本模态；完整方法可同时输入 index-aware text 与图像。（§3.2, Fig. 5, pp.5–6）

在给定 GT anomalies 的文本定位诊断中，Qwen index-free 平均输出 573.05 tokens、29.79 秒，standard F1 20.33；index-aware 输入 token 从 5,161 增至 10,051，但输出降至 59.01 tokens / 6.45 秒，F1 升至 60.16。Gemini 也从 index-free F1 27.74 升至 62.83。（Table 4, PDF p.9）这些数字是在 GT 给定的定位设置，证明索引格式有助坐标输出，不是完整 detector 的无 oracle 结果。

### 6.4 推理与 thresholding 对照

LLM 直接生成区间或标签；经典 detector 产生 timestamp anomaly score，再通过 Percentile、MAD 或 EVT-POT 阈值化成标签。为跨输出类型比较，作者在 TSB-AD-U 使用 label-based metrics，并选这三种 thresholding 方法中表现最好的一个；不是统一的在线、validation-only threshold。（§5.1, Appendix C.3）

## 7. Experimental Design and Evidence

### 7.1 数据、模型与指标

- **AnomLLM synthetic benchmark**：point、range、trend、frequency 四类；主实验对 21 个 prompt variants、四个 MLLM backbone（GPT-4o、Gemini-1.5 Flash、Qwen2.5-VL-72B、InternVL2-LLaMA3-76B）测试；使用 standard 和 affiliation precision / recall / F1。（§4, Table 1, PDF pp.6–7）
- **TSB-AD-U**：从 TSB-AD-U 中选 8 个较短类别以压低总推理成本；对照 16 个传统 / 深度 / foundation-model detectors，thresholding 试 Percentile、MAD、EVT-POT。（§4, §5.1, Appendix B.2 / C.3）
- **context experiment**：ETTh2、Electricity 上选传统 detector 常共同报警的片段，作者为片段生成领域化的合理背景描述，再看 LLM 是否将“可解释的已知异常”排除。（§5.2, Fig. 8, Appendix D.6）

### 7.2 主结果

- **AnomLLM Table 1**：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；Table 2 对四个模型相对 0-shot vision 的绝对 F1-point 差为 +28.01、+20.91、+19.75、+0.99，须区分 relative gain 与百分点差。（Tables 1–2, pp.7–8）
- **消融 Table 3**：去除 de-seasonalization 平均 F1 -5.64；去除 index -23.36；去掉文本数值 -16.88；去掉图像 -14.24。支持季节分解、位置索引和两种输入模态互补，但依赖所测合成 benchmark 和这些 backbone。（§4.2.1, Table 3, p.8）
- **TSB-AD-U Table 9**：其 GPT-4o 结果 standard F1 34.20、affiliation F1 74.64，单 sample inference time 140.63s；SR + MAD 为 standard F1 30.57、affiliation F1 75.94，推理约 .02s。故 GPT-4o 在标准 F1 略高，但不是所有 metric 最优，且速度差约数千倍。（§5.1, Appendix Table 9, PDF pp.10 / 35）
- **上下文案例**：ETTh2 / Electricity 的定性例子展示给出停机导致 flat pattern 等 context 后，GPT-4o 可把该可解释段过滤掉，同时保留无上下文解释的骤降。（§5.2, Fig. 8, Appendix D.6）

## 8. Contributions and Reproduction Value

1. 用诊断性实验将 LLM TSAD 的 failure 分成 temporal understanding 与 interval localization。（§2）
2. 提出轻量去季节项预处理和 index-value text prompting；不训练 / 微调 LLM。（§3）
3. 同时报告 AnomLLM standard + affiliation metrics、TSB-AD-U 的效率 / 阈值比较及 context qualitative case。（§4–5）
4. 公开 [代码](https://github.com/junwoopark92/LLM-TSAD)，适合复核 prompt 与评测脚本。

复现时需固定商业 API 版本和调用日期、image rendering、ACF period selection、分解边界、prompt、LLM decoding、TSB-AD-U 8 类子集以及 threshold search；API 模型版本会变化。作者没有对 context 设置做大量跨场景定量 benchmark，因此应把它当作探索案例。（§4–5, Appendix）

## 9. Limitations and Critical Reading

- **[作者说明]** LLM inference 慢，不适合对大量样本做 real-time detection；作者主张其更适用于离线或资源受限样本较少场景。（§5.1, PDF p.10）
- **[作者主张 / 证据边界]** context reasoning 可帮助排除用户认定的已知 / explainable anomalies；但例子使用人工构造的合理背景描述及模型共同报警的片段，不代表真实业务事件日志、workload 或 trace-grounded 的异常根因判断。（§5.2, Appendix D.6）
- **[实验范围]** TSB-AD-U 只选 8 个较短类别；用三个阈值法里最好者转换传统 score，标准与 affiliation metric 排名不完全相同。（§5.1, Appendix B.2, Table 9）
- **[方法推断]** 选全序列最高 ACF lag 的单一 dominant period，可能不适用于多周期、周期漂移或短序列；若 legitimate regime transition 同时改变 autocorrelation，去季节操作会否抹除需要验证。（§3.1）
- **[定位限制]** index-format 消融的强结果来自 GT 标注的 localization-only setting；完整检测仍需要模型先发现 anomaly，索引本身不能补足语义判断。（Table 4）
- **[研究缺口]** 论文 context study 只过滤预先描述为可解释的模式，没有系统测试过滤已知波动时是否损害未见故障召回，也没有测试负载正常变化与故障同窗并发。

## 10. Related Papers

- **AnomalyLLM**：用 GPT-2 teacher / prototype student 训练 representation discrepancy；本论文是统计工具 + prompt formatting，不更新模型参数。
- **AnomSeer**：用 visual MLLM 生成类别、定位、reasoning，并以 ExpCoT + TimerPO 后训练；本论文只作零样本提示，不产生训练期专家推理链。
- **TSB-AD / Quo Vadis**：提供 benchmark 与 threshold / point-adjustment 的评测语境；本论文 TSB 子集与最佳阈值搜索应单独看待。
- **MACE / When Model Meets New Normals / CAROTS**：显式多正常模式、test-time 状态适应、因果保持增强；本论文去季节项只处理时间分解，不识别业务状态。

## 11. Questions for Further Reading

1. 多个或变化中的周期下，ACF 主周期及 de-seasonalization 是否把真正频率故障减弱？
2. context prompt 怎样从业务事件、workload、发布和 Trace 可靠产生，而不把异常强行解释为正常？
3. 能否同时测试正常业务波动、故障、二者并发与未知事件，报告固定误报预算 / event latency 下的效果？
4. 更快的 open MLLM、量化、批量输出或传统 detector + LLM selective review 能否保留上下文价值？
5. 所选短序列 TSB 子集、商业 API 当前版本、best threshold 对结论排序有多大影响？

## 12. Key Terms

- **De-seasonalization**：识别并移除可重复 seasonal component，保留 trend + residual 给 detector。
- **Index-aware prompt**：明确将每个观测值与 timestamp/index 配对。
- **Localization-only diagnostic**：输入中给出真实异常位置来评估模型能否回报坐标。
- **Affiliation metric**：按真实 / 预测 anomaly event 的时间关系评估，不等同逐点 standard F1。

## 13. Tags

`TSAD` `LLM` `zero-shot` `de-seasonalization` `index-aware prompting` `context-aware detection` `latency` `localization`
