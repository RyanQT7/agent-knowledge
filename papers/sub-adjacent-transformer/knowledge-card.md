# 知识卡片：Sub-Adjacent Transformer

> 标记：**[作者主张]** 机制或作者解释；**[实验支持]** 表格 / 消融直接支持；**[分析推断]** 本知识库判断。PDF 页码指会议论文页码。

## 1. Research Scenario

- **[作者主张]** 无监督多变量重建 TSAD：防止异常从 immediate neighbors 被直接重建。（§3.2, pp.2–3）
- **[实验支持]** SWaT/WADI/PSM/MSL/SMAP/SMD 及合成 NeurIPS-TS。（Tables 1–3, pp.4–5）

## 2. Core Challenges

- **[作者主张]** 紧邻时间点与 target 相关更强；对异常尤其容易用邻居复制，使 reconstruction residual 变小。（§3.2, Fig. 1）
- **[作者主张]** vanilla attention 的 row-wise Softmax 不易形成本方法所需非对角 band；窗口边界 contribution 不平衡。（§3.2–3.3, Figs. 2–4）

## 3. Existing Limitations

- **[作者主张]** 依赖所有局部邻域的重建模型可能学会异常模式。（§1, §3.2）
- **[分析推断]** 全局固定 sub-adjacent span 不能识别它对应的是合法状态变化还是故障。

## 4. Core Idea

- **[作者主张]** 排除 target 的紧邻点，让 Transformer 主要由距离 $k_1$ 到 $k_2$ 的邻域重建；以低 SA contribution + 高 reconstruction error 作为异常证据。（Eqs. 1–7）

## 5. Technical Innovations

1. **[作者主张] Sub-adjacent contribution**：对 attention map 目标列累加指定距离 band。（Eq. 1, p.3）
2. **[作者主张] Circular index construction**：平衡窗口两端的有效 neighbor 数量。（Eqs. 2–3, p.3）
3. **[作者主张] Learnable linear mapping**：$\Phi(U)=Softmax_{row}(U/g)$ 并用 $\Phi(Q)\Phi(K)^T V$ 得到灵活 band map。（Eq. 4, p.4）
4. **[作者主张] Joint score**：优化 $\|X-\hat X\|^2-\lambda\|SACon\|_1$；推理点 score 为 softmax(-SACon) 与重建误差相乘，再做 dynamic Gaussian tail transform。（Eqs. 5–7）

## 6. Key Mechanisms

- **[实验支持]** $k_1=20,k_2=30$ 通常效果最佳；$k_1=k_2=0$ 性能明显下降。（Table 4, p.6）
- **[实验支持]** learnable mapping、linear attention 和 dynamic scoring 的 ablation 显示平均增益；移除 attention loss 也明显降低 F1。（Tables 5–8, pp.6–7）
- **[实验支持]** 六个真实集 F1 表中 99.0 / 99.3 / 98.9 / 96.7 / 98.2 / 97.7%（SWaT / WADI / PSM / MSL / SMAP / SMD），但主结果使用 point adjustment 和 test best-F1 threshold。（Table 2, pp.4–5）
- **[分析推断]** Attention contribution 是时间重建上下文约束，不是物理因果边或 root-cause explanation。

## 7. Experimental Evidence

- **[实验支持]** 6 real + NeurIPS-TS synthetic，15 baseline；报告 AUC/F1 和补充 no-PA F1。（§4）
- **[实验支持]** sub-adjacent distance、window size、lambda、attention mapping 和 dynamic scoring 均有 ablation / sensitivity 表。（Tables 4–8）
- **[协议边界]** pooled multi-entity model 对照部分 per-entity baseline；threshold 为 test best-F1，主 F1 使用 PA。（§§4.2–4.3）

## 8. Limitations

- **[分析推断]** 固定时间距离带对周期 / 采样率 / operating state 敏感；circular wrap 会连通窗口首尾。
- **[分析推断]** 局部正常切换若也难以由 sub-adjacent context 重建可能误报；并发故障未控制验证。
- **[分析推断]** score dynamic Gaussian 只适应局部分数尺度，不接入业务负载、Trace 或发布上下文。
- **[实验边界]** test-label best F1 + PA 会高估部署可用性；不同 entity fitting 方式影响横向比较。

## 9. Research Opportunities

- **[分析推断]** 以周期 / workload context 自适应选择 band，比较合法状态变化与异常故障并发。
- **[分析推断]** 用 causal streaming boundary handling 替代 circular wrap，并测短异常的定位延迟。
- **[分析推断]** 固定告警预算和 range / event metric 下复核收益；验证 attention map 与 topology / Trace / fault injection 对齐。

## 10. Related Papers

- **SARAD**：两者用 attention 结构信息，但 SARAD 是变量维 association progression；Sub-Adjacent 是时间维重建 attention band。
- **CrossAD**：Sub-Adjacent 是窗内上下文距离约束；CrossAD 建模跨尺度映射与窗原型。
- **TriAD / TFMAE**：三域 discord localization / temporal-frequency mask discrepancy 与此处局部邻居排除机制不同。
- **Quo Vadis / TSB-AD**：为该 paper 的 PA-F1 与 test best threshold 结果提供评测警示。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[Sub-Adjacent Transformer PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Sub_Adjacent_Transformer_Improving_Time_Series_Anomaly_Detection_with_Reconstruction_Error_from_Sub_Adjac.pdf)
- 代码：[GitHub repository](https://github.com/jackyue1994/sub_adjacent_transformer)
- IJCAI proceedings：[paper 0279](https://www.ijcai.org/proceedings/2024/0279.pdf)
