# 知识卡片：PCRTA — Perturbation-Guided Contrastive Representation Learning

> 标记：**[作者主张]** 方法设计或解释；**[实验支持]** 表格 / ablation 支持；**[分析推断]** 本知识库判断。页码指 IJCAI 2024 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 无监督多变量 TSAD：用扰动类别识别的伪标签改善对比学习的正 / 负样本构造。（§§1, 3）
- **[实验支持]** WaQ、DSADS、Epilepsy、ASD、SMD、SWaT 六个 benchmark。（Table 1, p.5）

## 2. Core Challenges

- **[作者主张]** 固定 time-series augmentation 可能像异常；高维 embedding 中按距离选正负 pair 易误判并 class collapse。（§§1, 3.4）
- **[分析推断]** perturbation 分类混淆只是异常 proxy，合法动态正常模式也可能难分类。

## 3. Existing Limitations

- **[作者主张]** 现有 contrastive TSAD 对扰动影响与正负样本选择缺少明确建模。（§§1–2）
- **[分析推断]** 六类固定 perturbation 偏向 point / contextual / collective 人工模式，未覆盖业务负载切换、慢漂移或 topology change。

## 4. Core Idea

- **[作者主张]** 学习原始/增强 view 的扰动类别预测，使用其 pseudo-label 在低维表示空间构造类内 top-$k$ positives 和类间 negatives；联合训练 classifier / contrastive network，最后平均多-view LOF score。（§§3.2–3.4, Eq. 9）

## 5. Technical Innovations

1. **[作者主张] 六种局部异常扰动**：point 极值替换、contextual offset、collective 片段替换，各有两个数值变体。（§3.3, Eq. 2, p.4）
2. **[作者主张] Perturbation classifier**：TCN representation 上学原始 + 6 扰动类型 cross-entropy。（Eqs. 1–3）
3. **[作者主张] 低维 projection 与 class-guided pairs**：same pseudo-class top-5 cosine positives、different pseudo-class negatives。（Eqs. 5–8, pp.4–5）
4. **[作者主张] 多 view LOF**：原始及六类 transform embeddings 分别算局部密度异常分数并取均值。（Eq. 9, p.6）

## 6. Key Mechanisms

- **[实验支持]** 6 datasets 中 F1 在 5 个排名第一、ASD 排第二；Epilepsy F1/AUC-PR 高于强对照。（Table 2, pp.6–7）
- **[实验支持]** 三个 dataset 的 ablation 显示 $L_{mul}$、$L_{con}$ 和 pseudo labels 多数有增益。（Table 3, p.7）
- **[协议边界]** F1 遍历候选 threshold 取 best value，依赖 test labels；不等于固定 operating point。（§4.1）
- **[分析推断]** 扰动类别本身不是最终异常 score；最终 score 是 LOF 聚合，proxy 只能间接改善 embedding。

## 7. Experimental Evidence

- **[实验支持]** PCRTA: WaQ .784/.794、DSADS .943/.960、Epilepsy .934/.964、ASD .927/.933、SMD .987/.988、SWaT .978/.996（F1/AUC-PR）。（Table 2）
- **[实验支持]** Ablation full vs ground truth pseudo labels / no classifier loss / no contrastive loss，完整模型在多数组合更好。（Table 3）
- **[实验支持]** Epilepsy t-SNE 和合成 mixed-anomaly case 给出表征 / 泛化可视化。（Figs. 3–4）

## 8. Limitations

- **[分析推断]** 数据归一化后的固定 $\gamma$ 与 $k$ 需要领域重新调参；扰动 family 不保证覆盖真实故障和正常业务状态迁移。
- **[分析推断]** classifier pseudo labels 可能自我强化错误类别边界；最终 LOF 对扰动与嵌入设置敏感。
- **[实验边界]** 用 best-F1 threshold，不报告统一无标签 calibration；推理的 7 views 增加计算，但论文无充分延迟报告。
- **[复现边界]** 论文未注明公开代码 URL，需自行核对扰动采样与 LOF 配置。

## 9. Research Opportunities

- **[分析推断]** 以真实业务事件 / workload-conditioned perturbation 验证“分类困难度”是否跟故障相关。
- **[分析推断]** 对 rare-but-normal operating regime 作专门 hard negative tests，避免被扰动负样本机制当作异常。
- **[分析推断]** 评估 classifier calibration、pseudo-label noise、top-$k$ 和 LOF views 对 event-level detection latency / false-alert rate 的影响。
- **[分析推断]** 加入变量关系型扰动，检验跨通道故障而非逐变量值替换。

## 10. Related Papers

- **TriAD**：同用 augmentation anomaly cues；TriAD 将扰动 view 作为 intra-domain negatives，并与域间对比 + MERLIN 结合；PCRTA 学 perturbation-class pseudo labels。
- **CAPMix**：两者都合成 anomaly-like 数据，但 CAPMix 训练边界与形状模板不同；PCRTA 学 embedding / LOF。
- **TFMAE**：也是多视图自监督，机制为 temporal-frequency masks 与 symmetric-KL discrepancy。
- **Quo Vadis / TSB-AD**：其 threshold / PA caveats 对 PCRTA 的 best F1 数字同样适用。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[PCRTA PDF](../../sources/papers/tsad-2024-2026/2024/IJCAI/Perturbation_Guiding_Contrastive_Representation_Learning_for_Time_Series_Anomaly_Detection.pdf)
- IJCAI proceedings：[paper 0548](https://www.ijcai.org/proceedings/2024/0548.pdf)
