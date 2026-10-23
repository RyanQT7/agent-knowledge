# Knowledge Dossier — Delving into Large Language Models for Effective Time-Series Anomaly Detection

## 1. Basic Information

- **English title**: Delving into Large Language Models for Effective Time-Series Anomaly Detection
- **中文译名**：深入探索大语言模型以实现有效的时间序列异常检测
- **Authors**: Junwoo Park, Kyudan Jung, Dohyun Lee, Hyuck Lee, Daehoon Gwak, ChaeHun Park, Jaegul Choo, Jaewoong Cho
- **Venue / year / CCF**: NeurIPS 2025 / CCF A
- **CCF provenance**: 用户已人工确认；保留清单等级，不在本次重新评定。
- **Original PDF**: `Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf`
- **Completed reading note**: `notes.md`
- **Knowledge card**: `knowledge-card.md`
- **Verified code URL**: https://github.com/junwoopark92/LLM-TSAD
- **Research area**: 基于 LLM 提示的单变量异常判定与定位
- **Method tags**: TSAD LLM zero-shot de-seasonalization index-aware prompting context-aware detection latency localization

## 2. Research Scenario

**来源标记**：以下场景摘要优先取自已完成精读后的知识卡片与精读笔记；基准实验不外推为生产部署。

- **[作者主张]** 对零样本 LLM / MLLM TSAD 做 failure analysis，分别研究异常理解和区间定位，再通过预处理与 prompt 改善模型。（§2–3, pp.2–6）
- **[实验支持]** AnomLLM 4 类 synthetic anomalies、TSB-AD-U 短序列子集，以及 ETTh2 / Electricity context case。（§4–5）

## 3. Research Problem

**作者任务定义与失败条件（按精读笔记转述）**：

作者观察到，文本输入时 LLM 经常把噪声或普通波动报成异常；图像输入更容易抓住醒目的 spike，却容易错过趋势、频率等细微变化。论文将 TSAD 任务拆为：(1) 判断是否理解序列动态并区分 normal / abnormal；(2) 把判断落到精确区间。若模型甚至在不需要定位的实例级二分类中漏掉异常，代表理解不足；若 GT 区间已在图上高亮仍无法准确返回区间，代表定位也有独立瓶颈。（§2, Figs. 1–3, pp.2–4）

方法沿用 zero-shot LLM：不给模型领域训练数据，输入序列文本、图像或二者，令 LLM 输出异常区间。它不改模型权重，而用统计预处理与 prompt formatting 调整输入结构。（§3, pp.4–6）

## 4. Core Challenges

#### 精读笔记原章节：4. Core Challenges

1. **季节性遮挡细微异常**：稳定季节项与 trend / frequency shift 叠加时，LLM 难直接从原始输入找出微弱变化。（§2.1, §3.1）
2. **模型不会可靠地按数值 token 计数**：只给无索引数值序列时，模型须隐式计算 anomaly 的 start/end 位置。（§2.2, §3.2, Fig. 5）
3. **输入模态各有缺陷**：image 的 x-axis 位置感不精确，raw text 的数值位置隐式，混合模态也不能保证改进所有模型。（§2–4）
4. **LLM 精度与实际使用成本有差距**：生成文本区间耗时远高于传统 detector；context-aware 输出还须检验是否漏掉未见故障。（§5）

**证据区分**：作者提出的挑战是研究动机；是否被实验直接验证，应结合第 9 节对应数据和消融判断。

## 5. Limitations of Existing Methods

#### 精读笔记原章节：知识卡片 Existing Limitations（精读笔记未单列）

- **[作者主张]** 既有 zero-shot prompting 易把正常波动报成异常，图像 prompt 又偏向显著 spike 而漏掉细节。（§1–2, pp.1–4）
- **[分析推断]** 只依靠独立时序 / 图像 prompt 无法判断某个真实业务变动是否被事件上下文解释。

**新颖性边界**：作者对既有方法的分析不自动等于实验证明；只在第 9 节出现直接对比或消融时描述实验支持。

## 6. Core Idea

#### 精读笔记原章节：2. One-Sentence Summary

论文把 LLM-based TSAD 拆成时序理解和异常定位，先用实例级检测及 GT-highlighted localization diagnostic 定位失败来源，再在输入前去除估计出的 seasonal component，并在文本 prompt 中给每个数值显式附 index；这种不训练模型的输入设计提升 AnomLLM 上的 prompt 结果，而真实 TSB-AD-U 小子集和上下文实验同时暴露出 LLM 推理时延与 context evidence 的边界。（§§2–5, Eqs. 1–2, Tables 1–4, PDF pp.3–11）

## 7. Technical Innovations

> 本节按精读卡片列出论文报告的技术主张 / 关键机制，并链接到档案中的完整方法与实验。挑战对应和新颖性边界属于本知识库分析；模块被使用不自动代表首次提出，通用 backbone / 算子也不单独视为创新。

- **C1（第4节挑战）**：季节性遮挡细微异常：稳定季节项与 trend / frequency shift 叠加时，LLM 难直接从原始输入找出微弱变化。（§2.1, §3.1）
- **C2（第4节挑战）**：模型不会可靠地按数值 token 计数：只给无索引数值序列时，模型须隐式计算 anomaly 的 start/end 位置。（§2.2, §3.2, Fig. 5）
- **C3（第4节挑战）**：输入模态各有缺陷：image 的 x-axis 位置感不精确，raw text 的数值位置隐式，混合模态也不能保证改进所有模型。（§2–4）
- **C4（第4节挑战）**：LLM 精度与实际使用成本有差距：生成文本区间耗时远高于传统 detector；context-aware 输出还须检验是否漏掉未见故障。（§5）

### 7.1 Failure diagnostics

- **作者技术描述**：**[作者主张] Failure diagnostics**：instance-level 二分类测理解；输入标出 GT 的定位任务测 coordinate localization。（§2, Figs. 2–3）
- **对应挑战**：C3、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.2 De-seasonalization

- **作者技术描述**：**[作者主张] De-seasonalization**：用 ACF 选 dominant period $P^*$，做 $x_t=s_t+\tau_t+r_t$，仅输入 $x_t-s_t$。（§3.1, p.5）
- **对应挑战**：C3、C1（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.3 Index-aware text

- **作者技术描述**：**[作者主张] Index-aware text**：显式将观测位置与数值配对，把隐式 token counting 改为 index lookup。（§3.2, pp.5–6）
- **对应挑战**：C3、C2（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“6.3 Index-aware prompt”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

### 7.4 Context filtering

- **作者技术描述**：**[作者主张] Context filtering**：让 LLM 按文字背景剔除可解释、无关心的异常模式。（§5.2）
- **对应挑战**：C1、C4（本知识库映射，不代表作者的一对一组件归因）
- **机制及输入—处理—输出**：具体输入、操作 / 公式、输出和作用见第8节 C 的“第8节 C（完整模块流程和输入 / 输出说明）”。
- **与已有方法的区别 / 新颖性边界**：本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。
- **实验支持**：未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。（无独立组件级验证）
- **适用条件 / 限制**：**论文级边界**：未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。

## 8. Methodology

### A. Overall Architecture

#### 精读笔记原章节：5. Architecture Overview

```text
输入时序 x[1:T]
  ├─ ACF(k), k=1…floor(T/2) → 主周期 P* = argmax ACF(k)
  ├─ additive decomposition x = s + τ + r → 只去 seasonal: x̃ = x − s
  ├─ 输出为 (index, value) 文本 + time-series plot image
  └─ 零样本 LLM → 异常 interval JSON / list
```

（Fig. 4, §3, PDF pp.4–6）

### B. Data Processing

**预处理、窗口切分、标准化、数据增强或样本构造**按 C 节原方法小节保留。可直接定位的小节：原笔记未单列专门预处理标题；请沿 C 节方法数据流查阅。没有在原文 / 精读笔记中找到的信息不作默认补全。

### C. Module Mechanisms and Equations

#### 精读笔记原章节：6. Method in Detail

#### 6.1 失效分析：理解与定位分开诊断

- **实例级 TSAD**：把区间检测简化为一条序列是否含 anomaly 的二分类，不要求精确 localization。使用四类 anomaly 的 1,600 个序列（每类 400），比较 21 种 prompt。trend shift 和 frequency change 上模型常只略高于、甚至不优于常数分类器；image 对明显 point / range 的表现较好。（§2.1, Fig. 2, PDF pp.3–4；实验细节 Appendix D.1）
- **GT localization diagnostic**：在输入图上标出真实 anomaly 区间，只要求返回坐标。整体结果仍有定位误差，且频率型异常往往由许多分散片段构成，输出端点困难。（§2.2, Fig. 3, PDF p.4）

这两种实验用于诊断模型能力，不是部署方法：第二项显式提供了真实位置，不能用来代表正常在线检测性能。（§2.2）

#### 6.2 Seasonal decomposition

对输入 $x_{1:T}$ 计算 lag $k=1,\dots,\lfloor T/2\rfloor$ 的 sample autocorrelation $\hat\rho(k)$，取

$$P^*=\arg\max_{k\ge1}\hat\rho(k).$$

用 $P^*$ 作窗口长度作经典加性分解

$$x_t=s_t+\tau_t+r_t,$$

其中 $s_t$ 为 seasonality、$\tau_t$ 为 trend、$r_t$ 为 residual。只将 $s_t$ 从原序列减掉，输入 $\tilde x_t=x_t-s_t$；剩余序列以 text 和 image 输入 LLM。作者选择“只去 seasonal”是为了突出微弱 trend / frequency deviations，不在预处理阶段把这些变化也消掉。（§3.1, PDF p.5）

论文称用 FFT 实现可达 $O(T\log T)$ 且相较 LLM 推理开销很小，也讨论可换 STL、Seasonal-HODMD 或 Prophet。Table 3 的消融表明移除该步骤后，三种 LLM 的 standard F1 平均下降 5.64 points。（§3.1–4.2.1, Table 3, pp.5, 8）

#### 6.3 Index-aware prompt

对文本输入显式写成位置和值配对，例如 $(t,x_t)$，使模型能直接回报区间端点，而不再从长序列内数 token。索引使输入长度近乎翻倍，但能把脆弱的隐式 counting 转成 lookup。图像无法方便叠加密集索引（会重叠、杂乱），所以索引主要加在文本模态；完整方法可同时输入 index-aware text 与图像。（§3.2, Fig. 5, pp.5–6）

在给定 GT anomalies 的文本定位诊断中，Qwen index-free 平均输出 573.05 tokens、29.79 秒，standard F1 20.33；index-aware 输入 token 从 5,161 增至 10,051，但输出降至 59.01 tokens / 6.45 秒，F1 升至 60.16。Gemini 也从 index-free F1 27.74 升至 62.83。（Table 4, PDF p.9）这些数字是在 GT 给定的定位设置，证明索引格式有助坐标输出，不是完整 detector 的无 oracle 结果。

#### 6.4 推理与 thresholding 对照

LLM 直接生成区间或标签；经典 detector 产生 timestamp anomaly score，再通过 Percentile、MAD 或 EVT-POT 阈值化成标签。为跨输出类型比较，作者在 TSB-AD-U 使用 label-based metrics，并选这三种 thresholding 方法中表现最好的一个；不是统一的在线、validation-only threshold。（§5.1, Appendix C.3）

### D. Key Formulas and Objectives

公式、变量定义和目标解释已在 C 节原方法文字中保留；可定位的编号：公式编号随原文小节引用，未单独转录编号。。不在此处重复改写，以避免脱离上下文。

### E. Training Process

训练数据构造、监督信号、优化目标与迭代方式见 C 节原方法章节；具体配置若原文未明确，保留该边界，不从常见实现习惯补写。

### F. Inference Process

推理输入、异常分数、标签 / 阈值判定见 C 节方法内容，重点小节：6.4 推理与 thresholding 对照及第 9 节评估协议；若原文未统一点级或事件级聚合，精读笔记会保留相应说明。

### G. End-to-End Mechanism

论文把 LLM-based TSAD 拆成时序理解和异常定位，先用实例级检测及 GT-highlighted localization diagnostic 定位失败来源，再在输入前去除估计出的 seasonal component，并在文本 prompt 中给每个数值显式附 index；这种不训练模型的输入设计提升 AnomLLM 上的 prompt 结果，而真实 TSB-AD-U 小子集和上下文实验同时暴露出 LLM 推理时延与 context evidence 的边界。（§§2–5, Eqs. 1–2, Tables 1–4, PDF pp.3–11）

## 9. Experimental Evidence

#### 精读笔记原章节：7. Experimental Design and Evidence

#### 7.1 数据、模型与指标

- **AnomLLM synthetic benchmark**：point、range、trend、frequency 四类；主实验对 21 个 prompt variants、四个 MLLM backbone（GPT-4o、Gemini-1.5 Flash、Qwen2.5-VL-72B、InternVL2-LLaMA3-76B）测试；使用 standard 和 affiliation precision / recall / F1。（§4, Table 1, PDF pp.6–7）
- **TSB-AD-U**：从 TSB-AD-U 中选 8 个较短类别以压低总推理成本；对照 16 个传统 / 深度 / foundation-model detectors，thresholding 试 Percentile、MAD、EVT-POT。（§4, §5.1, Appendix B.2 / C.3）
- **context experiment**：ETTh2、Electricity 上选传统 detector 常共同报警的片段，作者为片段生成领域化的合理背景描述，再看 LLM 是否将“可解释的已知异常”排除。（§5.2, Fig. 8, Appendix D.6）

#### 7.2 主结果

- **AnomLLM Table 1**：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；Table 2 对四个模型相对 0-shot vision 的绝对 F1-point 差为 +28.01、+20.91、+19.75、+0.99，须区分 relative gain 与百分点差。（Tables 1–2, pp.7–8）
- **消融 Table 3**：去除 de-seasonalization 平均 F1 -5.64；去除 index -23.36；去掉文本数值 -16.88；去掉图像 -14.24。支持季节分解、位置索引和两种输入模态互补，但依赖所测合成 benchmark 和这些 backbone。（§4.2.1, Table 3, p.8）
- **TSB-AD-U Table 9**：其 GPT-4o 结果 standard F1 34.20、affiliation F1 74.64，单 sample inference time 140.63s；SR + MAD 为 standard F1 30.57、affiliation F1 75.94，推理约 .02s。故 GPT-4o 在标准 F1 略高，但不是所有 metric 最优，且速度差约数千倍。（§5.1, Appendix Table 9, PDF pp.10 / 35）
- **上下文案例**：ETTh2 / Electricity 的定性例子展示给出停机导致 flat pattern 等 context 后，GPT-4o 可把该可解释段过滤掉，同时保留无上下文解释的骤降。（§5.2, Fig. 8, Appendix D.6）

**结果解释规则**：定量结论仅限该数据集、Baseline、指标、阈值与切分。整体表现不自动证明每个技术模块独立有效；如有失败案例、协议例外或表格口径冲突，按精读笔记原记录保留。

## 10. Limitations

### A. 作者明确承认 / 原文指出

精读笔记未记录可确认的独立作者局限表述；这不表示作者认为方法没有局限。

### B. 基于方法与实验的分析推断

#### 精读笔记原章节：9. Limitations and Critical Reading

**[作者说明]** LLM inference 慢，不适合对大量样本做 real-time detection；作者主张其更适用于离线或资源受限样本较少场景。（§5.1, PDF p.10）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[作者主张 / 证据边界]** context reasoning 可帮助排除用户认定的已知 / explainable anomalies；但例子使用人工构造的合理背景描述及模型共同报警的片段，不代表真实业务事件日志、workload 或 trace-grounded 的异常根因判断。（§5.2, Appendix D.6）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[实验范围]** TSB-AD-U 只选 8 个较短类别；用三个阈值法里最好者转换传统 score，标准与 affiliation metric 排名不完全相同。（§5.1, Appendix B.2, Table 9）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[方法推断]** 选全序列最高 ACF lag 的单一 dominant period，可能不适用于多周期、周期漂移或短序列；若 legitimate regime transition 同时改变 autocorrelation，去季节操作会否抹除需要验证。（§3.1）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[定位限制]** index-format 消融的强结果来自 GT 标注的 localization-only setting；完整检测仍需要模型先发现 anomaly，索引本身不能补足语义判断。（Table 4）

#### 精读笔记原章节：9. Limitations and Critical Reading

**[研究缺口]** 论文 context study 只过滤预先描述为可解释的模式，没有系统测试过滤已知波动时是否损害未见故障召回，也没有测试负载正常变化与故障同窗并发。

### C. 仍缺乏证据的问题

未做的实验只标记为证据边界，不解释为方法不具备该能力。具体未充分验证项见上方原精读笔记限制章节。

## 11. Research Implications

**本知识库分析，不是作者结论**：

#### 精读笔记原章节：知识卡片 Research Opportunities（本知识库分析补充）

- **[分析推断]** 结合可信业务事件、负载、Trace 与时间窗，评估正常变化、真实故障、并发和未知事件四种条件。
- **[分析推断]** 用多尺度 / 在线周期分解，同时检查去 seasonal 前后 anomaly evidence，避免把频率故障抵消。
- **[分析推断]** LLM 负责低频 context adjudication，传统低延迟 detector 做第一阶段筛选；用固定 false-alarm budget 和 event delay 比较成本。

## 12. Related Papers

以下关系来自原精读笔记明确记录的问题、方法或评测对照；不表示直接引用、继承或优劣排序。

- **AnomalyLLM**：用 GPT-2 teacher / prototype student 训练 representation discrepancy；本论文是统计工具 + prompt formatting，不更新模型参数。
- **AnomSeer**：用 visual MLLM 生成类别、定位、reasoning，并以 ExpCoT + TimerPO 后训练；本论文只作零样本提示，不产生训练期专家推理链。
- **TSB-AD / Quo Vadis**：提供 benchmark 与 threshold / point-adjustment 的评测语境；本论文 TSB 子集与最佳阈值搜索应单独看待。
- **MACE / When Model Meets New Normals / CAROTS**：显式多正常模式、test-time 状态适应、因果保持增强；本论文去季节项只处理时间分解，不识别业务状态。

## 13. Evidence References

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| Research problem / scenario | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2 | 精读笔记保留的原文定位 |
| Research problem / scenario | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2–3 | 精读笔记保留的原文定位 |
| Research problem / scenario | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §4–5 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2.1, §3.1 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2.2, §3.2, Fig. 5 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2–4 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §5 | 精读笔记保留的原文定位 |
| Challenges / prior methods | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §1–2 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF pp.4–6, §3, Fig. 4 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF pp.3–4, §2.1, Fig. 2 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF p.4, §2.2, Fig. 3 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §2.2 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF p.5, §3.1 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §3.1–4.2.1, Table 3 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §3.2, Fig. 5 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF p.9, Table 4 | 精读笔记保留的原文定位 |
| Method / formulas | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §5.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF pp.6–7, §4, Table 1 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §4, §5.1 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §5.2, Fig. 8 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §1, Table 1, Table 2 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | §4.2.1, Table 3 | 精读笔记保留的原文定位 |
| Experimental evidence | Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf | PDF pp.10, §5.1, Table 9 | 精读笔记保留的原文定位 |

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "delving-llm-tsad",
  "title_en": "Delving into Large Language Models for Effective Time-Series Anomaly Detection",
  "title_zh": "深入探索大语言模型以实现有效的时间序列异常检测",
  "authors": [
    "Junwoo Park",
    "Kyudan Jung",
    "Dohyun Lee",
    "Hyuck Lee",
    "Daehoon Gwak",
    "ChaeHun Park",
    "Jaegul Choo",
    "Jaewoong Cho"
  ],
  "year": 2025,
  "venue": "NeurIPS",
  "ccf_level": "A",
  "ccf_provenance": "用户已人工确认等级；沿用清单标记",
  "pdf_path": "sources/papers/tsad-2024-2026/2025/NeurIPS/Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
  "reading_note_path": "papers/delving-llm-tsad/notes.md",
  "code_url": "https://github.com/junwoopark92/LLM-TSAD",
  "research_area": "基于 LLM 提示的单变量异常判定与定位",
  "method_tags": [
    "TSAD LLM zero-shot de-seasonalization index-aware prompting context-aware detection latency localization"
  ],
  "research_scenario": "- [作者主张] 对零样本 LLM / MLLM TSAD 做 failure analysis，分别研究异常理解和区间定位，再通过预处理与 prompt 改善模型。（§2–3, pp.2–6） - [实验支持] AnomLLM 4 类 synthetic anomalies、TSB-AD-U 短序列子集，以及 ETTh2 / Electricity context case。（§4–5）",
  "research_problem": "作者观察到，文本输入时 LLM 经常把噪声或普通波动报成异常；图像输入更容易抓住醒目的 spike，却容易错过趋势、频率等细微变化。论文将 TSAD 任务拆为：(1) 判断是否理解序列动态并区分 normal / abnormal；(2) 把判断落到精确区间。若模型甚至在不需要定位的实例级二分类中漏掉异常，代表理解不足；若 GT 区间已在图上高亮仍无法准确返回区间，代表定位也有独立瓶颈。（§2, Figs. 1–3, pp.2–4） 方法沿用 zero-shot LLM：不给模型领域训练数据，输入序列文本、图像或二者，令 LLM 输出异常区间。它不改模型权重，而用统计预处理与 prompt formatting 调整输入结构。（§3, pp.4–6）",
  "core_challenges": [
    "季节性遮挡细微异常：稳定季节项与 trend / frequency shift 叠加时，LLM 难直接从原始输入找出微弱变化。（§2.1, §3.1）",
    "模型不会可靠地按数值 token 计数：只给无索引数值序列时，模型须隐式计算 anomaly 的 start/end 位置。（§2.2, §3.2, Fig. 5）",
    "输入模态各有缺陷：image 的 x-axis 位置感不精确，raw text 的数值位置隐式，混合模态也不能保证改进所有模型。（§2–4）",
    "LLM 精度与实际使用成本有差距：生成文本区间耗时远高于传统 detector；context-aware 输出还须检验是否漏掉未见故障。（§5）"
  ],
  "existing_method_limits": [
    "[作者主张] 既有 zero-shot prompting 易把正常波动报成异常，图像 prompt 又偏向显著 spike 而漏掉细节。（§1–2, pp.1–4）",
    "[分析推断] 只依靠独立时序 / 图像 prompt 无法判断某个真实业务变动是否被事件上下文解释。"
  ],
  "core_idea": "论文把 LLM-based TSAD 拆成时序理解和异常定位，先用实例级检测及 GT-highlighted localization diagnostic 定位失败来源，再在输入前去除估计出的 seasonal component，并在文本 prompt 中给每个数值显式附 index；这种不训练模型的输入设计提升 AnomLLM 上的 prompt 结果，而真实 TSB-AD-U 小子集和上下文实验同时暴露出 LLM 推理时延与 context evidence 的边界。（§§2–5, Eqs. 1–2, Tables 1–4, PDF pp.3–11）",
  "technical_innovations": [
    {
      "name": "Failure diagnostics",
      "author_claim": "**[作者主张] Failure diagnostics**：instance-level 二分类测理解；输入标出 GT 的定位任务测 coordinate localization。（§2, Figs. 2–3）",
      "challenge_ids": [
        "C3",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Failure diagnostics**：instance-level 二分类测理解；输入标出 GT 的定位任务测 coordinate localization。（§2, Figs. 2–3）"
    },
    {
      "name": "De-seasonalization",
      "author_claim": "**[作者主张] De-seasonalization**：用 ACF 选 dominant period $P^*$，做 $x_t=s_t+\\tau_t+r_t$，仅输入 $x_t-s_t$。（§3.1, p.5）",
      "challenge_ids": [
        "C3",
        "C1"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] De-seasonalization**：用 ACF 选 dominant period $P^*$，做 $x_t=s_t+\\tau_t+r_t$，仅输入 $x_t-s_t$。（§3.1, p.5）"
    },
    {
      "name": "Index-aware text",
      "author_claim": "**[作者主张] Index-aware text**：显式将观测位置与数值配对，把隐式 token counting 改为 index lookup。（§3.2, pp.5–6）",
      "challenge_ids": [
        "C3",
        "C2"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "6.3 Index-aware prompt",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Index-aware text**：显式将观测位置与数值配对，把隐式 token counting 改为 index lookup。（§3.2, pp.5–6）"
    },
    {
      "name": "Context filtering",
      "author_claim": "**[作者主张] Context filtering**：让 LLM 按文字背景剔除可解释、无关心的异常模式。（§5.2）",
      "challenge_ids": [
        "C1",
        "C4"
      ],
      "challenge_mapping_type": "本知识库分析；非作者一对一归因",
      "mechanism_and_io": "详见档案第8节 C 指定方法小节。",
      "method_detail_section": "第8节 C（完整模块流程和输入 / 输出说明）",
      "difference_from_prior": "本项具体价值限于作者描述的任务化操作 / 组合；与既有方法假设的区别见第5节。若缺少直接优先权证据，不宣称“首次提出”。",
      "experimental_support": "未找到直接隔离本项的消融；第9节整体结果只能支持整套方案在报告协议下的表现，不能归因到本模块。",
      "component_level_evidence_status": "无独立组件级验证",
      "applicability_boundary": "未找到本模块独立的适用性 / 限制声明；请结合第10节论文级局限和证据缺口，以及第9节实际测试范围判断。",
      "limitation_type": "论文级边界",
      "source_locator": "**[作者主张] Context filtering**：让 LLM 按文字背景剔除可解释、无关心的异常模式。（§5.2）"
    }
  ],
  "methodology": {
    "architecture": "text 输入时序 x[1:T] ├─ ACF(k), k=1…floor(T/2) → 主周期 P = argmax ACF(k) ├─ additive decomposition x = s + τ + r → 只去 seasonal: x̃ = x − s ├─ 输出为 (index, value) 文本 + time-series plot image └─ 零样本 LLM → 异常 interval JSON / list （Fig. 4, §3, PDF pp.4–6）",
    "data_processing": "按 §8.B–C 的精读笔记原章节保留；未报告细节不补写",
    "modules": [
      "6.1 失效分析：理解与定位分开诊断",
      "6.2 Seasonal decomposition",
      "6.3 Index-aware prompt",
      "6.4 推理与 thresholding 对照"
    ],
    "key_formulas": [],
    "training": "训练设置及目标见 §8.C 原方法章节；未明确项保留原文边界",
    "inference": "推理与分数判定见 §8.C 原方法章节及 §9 评估协议",
    "end_to_end": "论文把 LLM-based TSAD 拆成时序理解和异常定位，先用实例级检测及 GT-highlighted localization diagnostic 定位失败来源，再在输入前去除估计出的 seasonal component，并在文本 prompt 中给每个数值显式附 index；这种不训练模型的输入设计提升 AnomLLM 上的 prompt 结果，而真实 TSB-AD-U 小子集和上下文实验同时暴露出 LLM 推理时延与 context evidence 的边界。（§§2–5, Eqs. 1–2, Tables 1–4, PDF pp.3–11）"
  },
  "experimental_evidence": {
    "datasets": [
      "- AnomLLM synthetic benchmark：point、range、trend、frequency 四类；主实验对 21 个 prompt variants、四个 MLLM backbone（GPT-4o、Gemini-1.5 Flash、Qwen2.5-VL-72B、InternVL2-LLaMA3-76B）测试；使用 standard 和 affiliation precision / recall / F1。（§4, Table 1, PDF pp.6–7） - TSB-AD-U：从 TSB-AD-U 中选 8 个较短类别以压低总推理成本；…",
      "- AnomLLM Table 1：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；…"
    ],
    "baselines": [
      "完整对照名单与协议见 §9 原实验小节"
    ],
    "metrics": [
      "### 7.1 数据、模型与指标",
      "- AnomLLM synthetic benchmark：point、range、trend、frequency 四类；主实验对 21 个 prompt variants、四个 MLLM backbone（GPT-4o、Gemini-1.5 Flash、Qwen2.5-VL-72B、InternVL2-LLaMA3-76B）测试；使用 standard 和 affiliation precision / recall / F1。（§4, Table 1, PDF pp.6–7） - TSB-AD-U：从 TSB-AD-U 中选 8 个较短类别以压低总推理成本；…",
      "- AnomLLM Table 1：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；…"
    ],
    "main_results": [
      "- AnomLLM synthetic benchmark：point、range、trend、frequency 四类；主实验对 21 个 prompt variants、四个 MLLM backbone（GPT-4o、Gemini-1.5 Flash、Qwen2.5-VL-72B、InternVL2-LLaMA3-76B）测试；使用 standard 和 affiliation precision / recall / F1。（§4, Table 1, PDF pp.6–7） - TSB-AD-U：从 TSB-AD-U 中选 8 个较短类别以压低总推理成本；对照 16 个传统 / 深度 / foundation-model detectors，…",
      "### 7.2 主结果",
      "- AnomLLM Table 1：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；Table 2 对四个模型相对 0-shot vision 的绝对 F1-point 差为 +28.01、+20.91、+19.75、+0.99，须区分 relative gain 与百分点差。…"
    ],
    "ablations": [
      "- AnomLLM Table 1：代表性 text+vision 方法 standard F1：GPT-4o 70.04、Qwen 67.56、Gemini 63.31、InternVL 34.66；其 AnomLLM zero-shot vision prompt 分别为 42.03、46.65、43.56、23.92。InternVL 上提升很小，结果受 backbone reasoning ability 影响。作者称相对既有 prompt 平均提升 39.9%、最高 66.6%（摘要 / §1）；…"
    ],
    "robustness_generalization": [
      "鲁棒性、泛化、效率与边界见 §9 原实验小节"
    ],
    "industrial_validation": [
      "精读笔记未记录工业部署验证；主题面向工业不等于部署证据"
    ]
  },
  "limitations": {
    "author_stated": [
      "精读笔记未记录可确认的独立作者局限表述"
    ],
    "reasoned_inference": [
      "[作者说明] LLM inference 慢，不适合对大量样本做 real-time detection；作者主张其更适用于离线或资源受限样本较少场景。（§5.1, PDF p.10）",
      "[作者主张 / 证据边界] context reasoning 可帮助排除用户认定的已知 / explainable anomalies；但例子使用人工构造的合理背景描述及模型共同报警的片段，不代表真实业务事件日志、workload 或 trace-grounded 的异常根因判断。（§5.2, Appendix D.6）",
      "[实验范围] TSB-AD-U 只选 8 个较短类别；用三个阈值法里最好者转换传统 score，标准与 affiliation metric 排名不完全相同。（§5.1, Appendix B.2, Table 9）",
      "[方法推断] 选全序列最高 ACF lag 的单一 dominant period，可能不适用于多周期、周期漂移或短序列；若 legitimate regime transition 同时改变 autocorrelation，去季节操作会否抹除需要验证。（§3.1）",
      "[定位限制] index-format 消融的强结果来自 GT 标注的 localization-only setting；完整检测仍需要模型先发现 anomaly，索引本身不能补足语义判断。（Table 4）",
      "[研究缺口] 论文 context study 只过滤预先描述为可解释的模式，没有系统测试过滤已知波动时是否损害未见故障召回，也没有测试负载正常变化与故障同窗并发。"
    ],
    "evidence_gaps": [
      "未报告的环境属于证据不足，不等于方法能力不足"
    ]
  },
  "research_implications": [
    "- [分析推断] 结合可信业务事件、负载、Trace 与时间窗，评估正常变化、真实故障、并发和未知事件四种条件。 - [分析推断] 用多尺度 / 在线周期分解，同时检查去 seasonal 前后 anomaly evidence，避免把频率故障抵消。 - [分析推断] LLM 负责低频 context adjudication，传统低延迟 detector 做第一阶段筛选；用固定 false-alarm budget 和 event delay 比较成本。"
  ],
  "related_papers": [
    {
      "paper_id": "when-model-meets-new-normals",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "carots",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "mace",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomseer",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "quo-vadis",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "tsb-ad",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    },
    {
      "paper_id": "anomalyllm",
      "relation": "原精读笔记在相关工作 / 关系部分明确提及；具体关系及边界见第 12 节。"
    }
  ],
  "evidence_references": [
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2–3",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Research problem / scenario",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§4–5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2.1, §3.1",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2.2, §3.2, Fig. 5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§2–4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§5",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Challenges / prior methods",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "§1–2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.4–6, §3, Fig. 4",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF pp.3–4, §2.1, Fig. 2",
      "status": "精读笔记保留的原文定位"
    },
    {
      "claim_area": "Method / formulas",
      "pdf_file": "Delving_into_Large_Language_Models_for_Effective_Time_Series_Anomaly_Detection.pdf",
      "locator": "PDF p.4, §2.2, Fig. 3",
      "status": "精读笔记保留的原文定位"
    }
  ],
  "provenance": {
    "pdf_sha256": "6552084b5f391c020f7b7718178c40196219f89a6e2d33ab879078022adf8b53",
    "reading_note_sha256": "cce5ad00e9a830061d42217b570123bdf2b2470d2db0dbd533ad13d55e8de080",
    "extraction_status": "complete",
    "extraction_note": "技术贡献清单基于完成精读后的知识卡片整理，并映射到详细方法、实验和局限章节；挑战对应及新颖性边界明确标记为本知识库分析。",
    "knowledge_card_sha256": "d3c194eb74e5fd1134825cb9d4c7ddc99f8ca3a01686ad5dd070e0410504fb8b"
  },
  "knowledge_card_path": "papers/delving-llm-tsad/knowledge-card.md"
}
```
<!-- paper-knowledge-record:end -->
