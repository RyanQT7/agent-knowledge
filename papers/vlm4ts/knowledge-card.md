# 知识卡片：Harnessing Vision-Language Models for Time Series Anomaly Detection

> 标记：**[作者主张]** 论文提出的机制或解释；**[实验支持]** 表格 / 消融直接支持的结论；**[分析推断]** 知识库分析。页码按 AAAI 2026 PDF。

## 1. Research Scenario

- **[作者主张]** 在不使用目标时序训练的条件下，对单变量序列输出异常 interval；两阶段视觉方法先找局部候选，再以 VLM 结合整个序列核验。（§3, pp.3–5）
- **[实验支持]** 在 MSL、SMAP、Yahoo A1–A4、NAB 五组共 11 个 benchmark 上评价；主线是 univariate。（§4; Appendix C）

## 2. Core Challenges

- **[作者主张]** 局部窗口能看清尖峰，却丢失长程趋势；全局图保留语境却难以定位细异常。逐窗口 VLM prompting 又成本高。（§1, §3）
- **[作者主张]** 视觉特征需要同时覆盖单 patch 短异常与跨 patch 的趋势 / 长片段异常。（§3.1）

## 3. Existing Limitations

- **[作者主张]** 传统数值 detector 常依赖目标域训练与特定假设；naive VLM prompting 的准确率及 token 成本不理想。（§1–2）
- **[分析推断]** 全局趋势语境只来自曲线图，不含业务状态、发布、负载或 Trace；不能当作业务语义理解的实证。

## 4. Core Idea

- **[作者主张]** ViT4TS 用跨窗多尺度视觉 patch 差异筛候选，VLM4TS 用全序列图与候选做 context verification / refinement。（§3, Fig. 3）

## 5. Technical Innovations

1. **[作者主张] ViT4TS**：224 点滑窗、56 步长、统一全序列 y 轴；CLIP ViT-B/16 patch map 经 1×1、2×2、3×3 pooling 后，与同序列其它窗口做最近 cosine patch 匹配，跨窗 median 聚合。（§3.1, pp.3–4）
2. **[作者主张] 多尺度 score fusion**：上采样后 harmonic 融合不同尺度差异图，以 patch-row quantile 汇聚到时间分数，并阈值化为候选 interval。（§3.1; Appendix B.3）
3. **[作者主张] VLM4TS**：把整序列图、ViT 候选区间交给 GPT-4o，要求拒绝与全局走势不符候选、补充明显遗漏，并输出 JSON、confidence 和简短理由；过滤 confidence 1。（§3.2; Appendix B.4）

## 6. Key Mechanisms

- **[实验支持]** ViT4TS 平均 F1-max 0.612，VLM4TS 0.659，第二名 LSTM-DT 0.529；VLM4TS 在 9/11 benchmark 领先。（Table 1, p.6）
- **[实验支持]** 相对 TAMA 提升 13.3%；论文报约 1,212 tokens、14.68 秒 / series，并称相对 rolling-window VLM prompting 平均 token 使用降低 36×。（Table 2; §3.2）
- **[实验支持]** 去掉局部 ViT screen 后表现下降；较短 28 点窗口在 Yahoo A3/A4 的 F1-max 分别由 0.614/0.565 提升到 0.906/0.844。（Table 3; Appendix D.4）

## 7. Experimental Evidence

- **[实验支持]** 11 个公开 benchmark，比较统计、深度、时序预训练和 LLM / VLM 基线；主指标为 sweep threshold 得到的 contextual F1-max。（§4; Appendix C）
- **[实验支持]** Yahoo A3/A4 密集注入异常是明显失败场景：VLM4TS 0.497/0.474，ViT4TS 0.614/0.565；作者归因于异常稀有假设失效与更保守筛选。（§4, p.6）
- **[证据边界]** 多变量附录只报告有限 MSL 扩展，逐 channel 到 subplot 融合的 F1 约 0.619→0.660；不足以证实一般 multivariate dependency modeling。（Appendix D.3）

## 8. Limitations

- **[作者说明]** 主线为单变量；A3 / A4 异常密集时召回下降。（§3–4）
- **[分析推断]** F1-max 需要事后阈值扫描；confidence 1–3 没有独立 calibration evidence。
- **[分析推断]** 每个局部 plot 使用全序列 min/max，极端点可能影响视觉动态范围；此敏感性没有单独评估。
- **[分析推断]** 方法没有输入真实 workload / release / Trace context；14 秒左右的 API 路径并未验证高频在线操作预算。

## 9. Research Opportunities

- **[分析推断]** 评估多变量 joint context、动态 scale / y-range 对极值与高波动状态的鲁棒性。
- **[分析推断]** 在合法业务状态切换、故障、以及二者同时出现的测试矩阵中测量 context verification 对未知故障的漏报代价。
- **[分析推断]** 固定误报预算下报告区间质量、检测延迟、VLM latency 和 token cost，并校准置信度。

## 10. Related Papers

- **Delving into LLMs for TSAD**：index-aware numeric text vs visual plot + patch candidates。
- **AnomSeer**：图像输入后训练 MLLM 做检测 / 分类 / 解释；VLM4TS 是 zero-shot candidate verifier。
- **TimeRCD**：同样关心 context，但以长窗数值关系和合成 context labels 训练 detector。
- **When Model Meets New Normals / CAPMix**：显式适应新正常或 KPI 波动，适合检验视觉全局趋势是否足够区分正常变化与故障。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[Harnessing VLMs PDF](../../sources/papers/tsad-2024-2026/2026/AAAI/Harnessing_Vision_Language_Models_for_Time_Series_Anomaly_Detection.pdf)
- 代码：[VLM4TS repository](https://github.com/ZLHe0/VLM4TS)
- AAAI：[公开论文 PDF](https://ojs.aaai.org/index.php/AAAI/article/download/39319/43280)
