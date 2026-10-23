# 知识卡片：GCAD（Granger Causality Anomaly Detection）

> 标签：**[作者主张]** 作者提出的观点；**[实验支持]** 表格、消融或案例支持；**[分析推断]** 本知识库的判断。页码均为论文 PDF 页码。

## 1. Research Scenario

- **[作者主张]** 多变量 TSAD 中，异常除了改变数值 / 预测误差，也可能使变量间 Granger predictive dependency 发生变化。（§§1–3, PDF pp.2–5）
- **[实验支持]** 在 SWaT、SMD、MSL、SMAP、PSM 上用窗口级图相对正常图模板的偏差检测异常。（Tables 1–3, PDF pp.5–6）

## 2. Core Challenges

- **[作者主张]** 基于图的 detector 常以 prediction error 作为唯一检测准则，未把关系结构变化直接作为异常证据。（§1）
- **[分析推断]** 真实故障、正常业务阶段切换都可能改变预测依赖；需要区分结构变化来源。

## 3. Existing Limitations

- **[作者主张]** 传统线性 Granger 对非线性时序有限；常用相似性图可能对称，不符合有向预测关系。（§2–3）
- **[作者明确限制]** 仅建模 pairwise binary causal relationships，无法直接表达高阶多变量交互。（Conclusion, PDF p.7）
- **[分析推断]** 预测 loss 梯度只是模型局部敏感度 proxy，并非干预验证的真实 causal graph。

## 4. Core Idea

- **[作者主张]** 训练 Mixer 预测下一时刻；对每个目标通道分别反传预测 loss，聚合对各输入通道历史的梯度幅值估计窗口级非线性 Granger 影响；将测试图与正常图模板比较。（§3, Eqs. 1–12, PDF pp.3–6）

## 5. Technical Innovations

1. **[作者主张]** 以每个目标通道 $j$ 的平方预测误差 $L_{t,j}$ 构造独立 backward pass。（Eq. 1）
2. **[作者主张]** 通过 $|\partial L_{t,j}/\partial x_{\phi,i}|$ 对滞后和输入值分布积分，形成 $a_{i,j}$。（Eqs. 2–5）
3. **[作者主张]** 用 $\tilde A_{ij}=\max(0,A_{ij}-A_{ji})$ 去除对称关系，再以阈值 $h$ 稀疏化；不保证 DAG。（Eq. 6）
4. **[作者主张]** 对正常训练窗口抽样并求平均图 $A_{norm}$；测试时计算因果关系相对偏差 $S_c$、时间对角偏差 $S_t$，最终 $S=S_c+\beta S_t$。（Eqs. 7–12）

## 6. Key Mechanisms

- **[作者主张]** Predictor 同时产生检测所需的局部梯度图；关系偏差和对角自时序偏差互补。（§3）
- **[实验支持]** 去掉因果关系或时间对角项后，SWaT / SMD 多项 AUROC / AUPRC 降低；去掉 sparsification 对 SMD AUPRC 影响显著。（Table 3, PDF p.6）
- **[分析推断]** $A_{norm}$ 是全局均值模板，未按工作负载 / 运行阶段条件化，合法模式切换可能被视为异常。
- **[证据边界]** $A$ 来自 loss sensitivity，依赖 predictor 拟合、残差与局部输入点；真实图边精度没有 ground-truth causal graph 实验验证。

## 7. Experimental Evidence

- **[实验支持]** Table 2 AUROC/AUPRC：SWaT .8690/.7758、SMD .9533/.7502、MSL .7658/.3679、SMAP .7273/.4555、PSM .7618/.6136。（PDF pp.5–6）
- **[实验支持]** SMAP AUPRC 中 GCAD .4555 低于 GANF .5259；不能说所有数据集每个指标都最优。（Table 2）
- **[实验支持]** Table 3 的 no-sparsification、no-GC、no-TC ablation 在 SWaT / SMD 多项指标下降；但 SMD full/no-sparse AUROC 几乎相同，影响并不均匀。（PDF p.6）
- **[实验支持]** SWaT 单案例把 P203 / P205 泵攻击与 AIT202、AIT501、FIT301、FIT503 关系偏移联系起来；属定性解释，不是全量变量定位准确率。（Figs. 3–5, PDF p.7）
- **[实验限制]** 报告 AUROC/AUPRC、10 次均值；未报告标准差、固定运行阈值告警成本或事件级检测时延。（§4）

## 8. Limitations

- **[作者明确指出]** pairwise binary edges 不能表示高阶因果关系；非线性因果图 sparsification 不保证无环。（§3, Conclusion）
- **[实验支持]** 某些表中数据集点数明显小于常用全量统计，预处理 / 子集口径需核实；论文正文未逐项解释。（Table 1）
- **[分析推断]** 未用 workload、Trace、发布或阶段信息；正常状态改变因果依赖与真实故障结构破坏可能混淆。
- **[复现边界]** 论文未提供专属代码链接；$P$ 积分近似、抽样数、$h/\beta$ 选择、窗口对齐等实现细节需要补齐。

## 9. Research Opportunities

- **[分析推断]** 以状态条件图模板 / 图混合模型表示多种正常负载状态，检查均值模板是否构成不存在的中间关系图。
- **[分析推断]** 将梯度图和真实 topology、故障注入、operator event / Trace 对齐，区分 predictive sensitivity 与可验证因果关系。
- **[分析推断]** 构造正常负载变化与故障并发测试，量化图模板切换与在线更新的污染风险。
- **[分析推断]** 加入高阶交互图、固定 FPR 的运行点、事件级时延和跨实体迁移评测。

## 10. Related Papers

- **CAROTS**：都使用 Granger 概念；CAROTS 用图引导 CPA/CDA augmentation 和预测，GCAD 用 loss-gradient 建图并检测图偏移。
- **OracleAD**：结构偏差也与正常模板比较；OracleAD 的模板是对称 latent pairwise distances，并非显式有向 Granger 图。
- **SARAD**：同属结构关系信号检测；SARAD 读 MHSA reconstruction association 的时序下降，不估计 Granger causal influence。
- **CCM-TAD**：causal 指时间 mask 防 future leakage，未学习跨通道因果边。
- **Graph-MoE**：Graph-MoE attention graph 用于层级专家路由，GCAD 图是预测误差梯度派生的检测量。

## Links

- 精读笔记：[notes.md](notes.md)
- 原始 PDF：[GCAD PDF](../../sources/papers/tsad-2024-2026/2025/AAAI/GCAD_Anomaly_Detection_in_Multivariate_Time_Series_from_the_Perspective_of_Granger_Causality.pdf)
- AAAI 页面：[paper page](https://ojs.aaai.org/index.php/AAAI/article/view/34096)
