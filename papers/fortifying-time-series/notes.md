# Fortifying Time Series：基于 DTW 认证的鲁棒异常检测

## 1. Metadata

- Title: Fortifying Time Series: DTW-Certified Robust Anomaly Detection
- Authors: Shijie Liu, Tansu Alpcan, Christopher Leckie, Sarah Erfani
- Year / Venue: 2025 / NeurIPS
- CCF: A（采用已人工确认的论文清单等级）
- Paper page: [NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/f2192666f094c0115f09162e8c66d67f-Abstract-Conference.html)
- Code: 论文附录称提供 code 和 environment 文件；本地清单未列稳定代码 URL，需从 proceedings / 作者匿名附件核实。
- Knowledge Card: [knowledge-card.md](knowledge-card.md)
- Local File: [Fortifying Time Series PDF](../../sources/papers/tsad-2024-2026/2025/NeurIPS/Fortifying_Time_Series_DTW_Certified_Robust_Anomaly_Detection.pdf)
- 版本说明：本地 PDF 正文标有 NeurIPS 2025，同时第一页还带 arXiv:2605.07690v1（2026-05-08）标记。此笔记以本地 PDF 的实际内容为准，不把会议信息和该版本标记混为一谈。（PDF p.1）

## 2. One-Sentence Summary

该方法把任意预训练时序异常分数器包进高斯随机平滑与分位数估计中，先得到输入空间 $\ell_2$ 鲁棒半径，再用 Keogh DTW 下界将其转换成时间扭曲距离下的认证半径；它证明的是阈值分类在指定 DTW 扰动预算内不变，而不是模型对合法业务变化有正确解释。

## 3. Problem, Threat Model, and Motivation

作者关注对抗鲁棒性。时序异常检测在医疗、金融、工业和移动网络等场景中可能被对抗者操纵；传统认证多约束 $\ell_p$ 范数，但小幅时间平移、拉伸或压缩会显著增加逐点 $\ell_p$ 距离，即使序列的时间形态语义相近。DTW 通过寻找单调、端点匹配的时间对齐路径来比较序列，更适合刻画时间变化。（PDF pp.1–3, §1, Fig. 1）

论文威胁模型设攻击者具有白盒检测器访问和无限计算能力，可对当前判为正常或异常的序列发起两类攻击：**evasion** 将真实异常变成正常，**availability** 将正常样本变成误报。攻击输入必须在 DTW 半径 $e$ 内，以表示时间扭曲后语义仍需保持。对抗者不限攻击优化手段；认证目标是对半径内所有输入保证原预测决策不变，概率至少为 $1-\alpha$。（PDF pp.3–4, §3.1）

重要区分：这是“相对于已作预测的决策稳定性”，不是“标签正确性”本身。对一个误报样本证明其在小 DTW 扰动下仍为误报，也满足稳定性定义；只有将证书和真值结合，构造 certified TP/TN 等指标，才衡量正确预测是否得到保护。（PDF pp.7–8, §4; Appendix E, pp.24–25）

## 4. Core Idea and Pipeline

```text
预训练打分器 f(x) + 原阈值 γ
       → 对输入加多份高斯噪声，计算扰动分数
       →（作者所述 denoising layer）+ p 分位数平滑分数 h_p(x)
       → Monte Carlo order statistics 得 h_p 的上下界，置信度 1−α
       → 由分位数到 γ 的 margin 求输入 ℓ2 认证半径 r
       → 用局部 Keogh envelope slack (R, M) 把 r 转成 DTW 半径 e
       → 输出平滑检测结果及每个样本的证书
```

这是一个免重训练的 wrapper：被保护的检测器可以是任意确定性或随机打分函数；框架不要求修改原模型训练。主要方法依赖随机输入扰动、有限样本的分位数界与一个可计算 DTW 下界。（PDF pp.4–7, §§3.2–3.3, Fig. 2）

## 5. Method in Detail

### 5.1 输入、逐点 detector 与 DTW 距离

输入窗口 $x\in\mathbb R^{T\times C}$，其中 $T$ 为窗口长度，$C$ 为通道数。检测器输出 anomaly score $f(x)$，再按阈值 $\gamma$ 给出 $d(x)=\mathbb 1[f(x)>\gamma]$。（PDF pp.3–4, §3.1, Eqs. 1–3）

论文定义 $p$ 阶 DTW 距离为：

$$\operatorname{DTW}_p(x,x')=\min_{\pi\in\mathcal A(x,x')}\left(\sum_{(i,j)\in\pi}|x_i-x'_j|^p\right)^{1/p}.\tag{3}$$

$\pi$ 是端点匹配、单调前进且每个序列索引至少出现一次的对齐路径；主文默认 $p=2$。实验进一步用 Sakoe–Chiba wrapping window $w$ 限制允许对齐范围。多变量情况下通道误差进入距离 / envelope 计算；具体任意 $p$ 推广在 Appendix C。（PDF pp.4–5, §3.1, Eq. 3; pp.23–24, Appendix C）

### 5.2 随机平滑与分位数打分

标准 randomized smoothing 常对 $f(x+\eta)$ 取期望。但异常分数通常无界且可能高方差，均值容易被极端输出影响。作者使用分位数平滑，对噪声分数分布取第 $p$ 分位：

$$h_p(x)=\sup\{u\in\mathbb R:\Pr_{\eta\sim\mathcal N(0,\sigma^2 I)}[f(x+\eta)\le u]\le p\}.\tag{4}$$

它不必对输入作可微修改，可以把多个 $x+\eta$ 送入原模型，对噪声分数取指定 quantile。Lemma 3.1 给出：若 $\|x-x'\|_2\le r$，那么输入变化会把分位水平移动到

$$p^- = \Phi(\Phi^{-1}(p)-r/\sigma),\qquad p^+ = \Phi(\Phi^{-1}(p)+r/\sigma),$$

并有对所有半径内 $x'$ 的下 / 上分位数界 $h_{p^-}(x)\le h_p(x')\le h_{p^+}(x)$。$\Phi$ 为标准高斯 CDF。若原输入的下界仍高于 $\gamma$，异常决策在整个 $\ell_2$ 球内不变；若上界仍不超过 $\gamma$，正常决策不变。根据分位数与阈值间的余量，可反解出最大有效 $r$。（PDF pp.4–5, §3.2, Lemma 3.1, Eqs. 4–5, 9）

附录 A 先复述均值平滑的界，再以分位数版本处理异常分数。主文 Fig. 2 / §3.3 将 wrapper 描述为 $h_p=j\circ k\circ f$：$j$ 注入高斯噪声，$k$ 为降低输出噪声方差的 denoising layer；论文指出任意 downstream pipeline 不破坏随机平滑证书。不过正文没有把该 denoising 层的具体结构、参数化训练方式与逐模型实现完全展开，复现时需依附件代码确定。（PDF pp.6–7, §3.3, Fig. 2; pp.21–23, Appendix A–C）

### 5.3 Monte Carlo 分位数的统计保证

$h_p$ 无闭式表达，推理时为每个输入生成 $n$ 个独立高斯噪声样本，计算 $f(x+\mu_i)$ 并排序成 order statistics $K_1,\dots,K_n$。基于二项分布尾概率，选择上下次序统计量 $K_{q_l}$ 和 $K_{q_u}$，使估计下界和上界以至少 $1-\alpha$ 的置信度包住分位数；通过二分搜索找到满足置信约束的次序。实验设 $\alpha=10^{-3}$、$n=1000$。增加采样数可提高半径估计精度，但推理开销也随之增加。（PDF p.7, §3.3, Eq. 11）

这里有两层“概率”需分清：高斯扰动定义了平滑分数；有限次 Monte Carlo 又产生估计置信度。统计置信度不是数据标签正确率，也不表示线上事件发生概率。（PDF pp.6–7, §3.3）

### 5.4 从 $\ell_2$ 半径到 DTW 认证半径

直接算 DTW 代价较高。作者使用 Keogh lower bound：围绕原序列每个时点 $i$，在允许时间扭曲窗口 $w$ 内构造上包络 $U_i$ 与下包络 $L_i$。新序列 $x'_i$ 若在 envelope 内，对 lower bound 不产生代价；落在 envelope 外则按到 envelope 的距离累计。因此 $LB_{Keogh}(x,x')\le DTW(x,x')$，并在 $w>0,x'\ne x$ 的条件下使用严格下界性质。（PDF p.5, §3.2, Eqs. 6–7; Appendix B, p.22）

一般的下界转换引理是：若平滑打分器在输入 $\ell_2$ 球 $\|x'-x\|_2\le r$ 内有证书，取 $e=\inf\{LB(x,x'):\|x'-x\|_2>r\}$，则 DTW 半径不超过 $e$ 的输入必须在该 $\ell_2$ 球内，继承其分类保证。（PDF p.5, Lemma 3.2, Eq. 8）

对 Keogh 下界，定义每个时刻在包络内可“隐藏”的最大偏移

$$\Delta_i=\max(U_i-x_i,\,x_i-L_i),\quad R=\sqrt{\sum_i\|\Delta_i\|_2^2},\quad M=\max_i\|\Delta_i\|_2.$$

当 $r\le R$，允许的 $\ell_2$ 扰动可以完全落在 envelope slack 中，故无法保证正 DTW 半径，$e=0$。当 $r>R$，至少有一部分扰动越出 envelope，定理 3.3 给出

$$e=\sqrt{M^2+r^2-R^2}-M.\tag{10}$$

这是把分位数分数与决策阈值的 margin 得到的 $r$ 转成 DTW 半径；若高斯分位数边界离阈值很近，则 $r$ 小，证书可能为零。包络宽、通道多、样本变化大时 $R$ 或 $M$ 增大，也会使 DTW 下界证书偏松。（PDF pp.5–6, Theorem 3.3, Eqs. 9–10; Appendix B, pp.22–23）

附录 C 声称可扩展至任意 $\ell_p$，将高斯噪声换成相对该范数径向对称的噪声（示例 $\ell_1$ 用 Laplace、$\ell_\infty$ 用均匀噪声），并用对偶范数界推导分位数稳定性。主文结果以 $\ell_2$ / Gaussian 为主，不能把推广当作已广泛实测的结论。（PDF p.23, Appendix C）

### 5.5 训练 / 推理流程与阈值

训练阶段照原流程训练 COUTA、TimesNet 或 DeepSVDDTS；防护包装不修改预训练参数。推理时，对窗口增加高斯扰动并重复打分，估计平滑分位数、输出平滑二分类结果和证书。阈值 $\gamma$ 沿用被保护 detector 的决策阈值；论文没有把这个体系设计成业务代价感知的重新校准模块。（PDF pp.3–7, §§3.1–3.3）

## 6. Experiments

### 6.1 设置与指标

实验用三个 detector：COUTA、TimesNet、DeepSVDDTS。数据集表列有 SMAP、MSL、SMD、NeurIPS-TS 的 SWAN / CREDITCARD / WATER，以及 UCR-1 / UCR-2，共八个表列项，兼有单变量和多变量；而 §4 Settings 文字称 seven benchmark datasets，且把 UCR-1/UCR-2 合称 collection。此处是“七个”与 Table 4 八行的口径差异，笔记以表列具体数据为准。（PDF pp.7–8, §4; p.24, Table 4）

主设置 $T=50$、DTW wrapping window $w=4$、噪声样本 $n=1000$、$\sigma=0.5$、percentile $p=0.5$；A100 80GB GPU 与 Xeon Gold 6326 CPU。检测指标是 point-adjusted F1 和 ROC-AUC；证书报告半径均值 / 最大值 / 标准差、非零证书比例；并为 evasion 与 availability 分别定义最坏情况下的 certified TP / TN，计算 certified accuracy 和 certified F1。（PDF pp.7–8, §4; pp.24–25, Appendix E）

### 6.2 检测性能和证书

Table 1 对比原模型与加上 wrapper 后的性能及证书。结果依模型和数据显著变化，不能概括为“性能总无损”：例如 NIPS-TS-WATER + DeepSVDDTS 非零证书比例 99.46%，平均证书半径 0.189，F1 / ROC-AUC 未下降；但 NIPS-TS-CREDITCARD + COUTA 的 F1 从 0.192 降至 0.003、ROC-AUC 从 0.900 降至 0.300。SMAP/SWAN 上某些模型证书比例偏低，例如 SWAN + COUTA 14.52%。这显示证书覆盖率、半径强度和检测质量之间并不保证同时改善。（PDF pp.7–8, §4.1, Table 1）

Figure 3 给出 COUTA 在 MSL / SMAP 上攻击预算 $t\in[0,0.5]$ 的 certified accuracy / F1 下界曲线；增大 $\sigma$ 时一些曲线更稳健，且作者举 SMAP、$\sigma=1$、evasion $t=0.2$ 时 certified F1 约 0.5。曲线表示对该范围任意对手扰动的最坏情况性能下界，并非实测攻击平均效果。（PDF pp.7–8, Fig. 3）

### 6.3 与 $\ell_p$ 认证防护在 DTW 攻击下的对比

Table 2 用 COUTA、DTW 攻击预算 $e_{att}=1.0$ 比较无防护、$\ell_p$ certified defense 与 DTW-Certified Defense。无防护模型在 SMD / UCR-1 的 F1 分别下降 60.6% / 89.7%（论文报告）；DTW defense 的 F1 对比 $\ell_p$ 防护，在 MSL 由 0.672 到 0.784（绝对 +0.112），在 UCR-1 由 0.761 到 0.948（绝对 +0.187）；SMD 为 0.392→0.464，WATER 为 0.423→0.525。AUC 也在四个数据集均高于 $\ell_p$ defense。结果支持“所测 DTW 威胁与认证度量对齐后更有抵抗力”，不能推出对非对抗性负载变化 / 未建模业务事件也更鲁棒。（PDF pp.8–9, Table 2）

### 6.4 噪声强度与窗口消融

Table 3 比较 $\sigma\in\{0.1,0.5,1,2\}$。总体上增大噪声提升平均 / 最大证书半径及非零证书比例，但过大的 $\sigma$ 会损害 F1 / AUC。例如 SMD 的非零证书比例从 52.42%（$\sigma=.1$）升至 94.66%（$\sigma=2$），但 F1 从 .504 降至 .315；SMAP 到 $\sigma=2$ 时 F1/AUC 也降至 .913/.958。中等噪声可能因平滑边界而改善基线指标，但并非单调。（PDF pp.8–9, §4.1, Table 3）

Appendix F Table 7 在 SMD / COUTA 上变更窗口长度 $T\in\{10,50,100,200\}$ 和 DTW 对齐窗口 $w\in\{2,4,10\}$。增大 $T$ 有时提升未平滑 detector 的上下文表现，却大幅降低认证比例：$T=50,w=4$ 为 77.99%，$T=200,w=4$ 降至 41.05%；增大 $w$ 放宽时间对齐、使 Keogh 包络更宽，通常降低证书半径 / 覆盖率。超参数反映 detection context 与 certificate tightness 的权衡。（PDF p.25, Appendix F, Table 7）

## 7. Contributions and Strengths

- 将时序语义更相关的 DTW 威胁模型纳入正式认证，给出从 randomized smoothing 的 $\ell_2$ 证书到 Keogh DTW 下界的可计算桥接。
- 分位数平滑适配无界、高方差 anomaly score；有限样本次序统计量和二项尾概率给出所需置信界。
- wrapper 与训练期模型解耦，并在三个架构、多个数据集和两类攻击目标上做评估。
- 同时报告证书半径分布、coverage 和 certified confusion matrix，而不只报某个半径下的点值性能。

## 8. Limitations and Reproduction Value

### 作者明确讨论

- Monte Carlo 采样引入测试时开销；未来需更高效的采样或自适应噪声注入。（PDF p.9, §5）
- 更精确的 DTW lower bound 可能收紧证书；框架未来可推广到时序分类等任务。（PDF p.9, §5）

### 方法 / 实验边界

- Keogh 是保守下界，不等于精确 DTW 球覆盖；$r\le R$ 时方法明确只能给 $e=0$。严格证书可能比实际经验鲁棒范围小。
- 半径对噪声量、窗口长度、warping window、数据变化和通道维数敏感；Table 1 中异常性能有显著下跌案例，需按模型 / 数据分别选择参数。
- 证书保证被扰动输入不会改变平滑二分类决策，不保证原始分类正确、不保证跨状态泛化，也不解释告警的业务原因。
- 使用 point-adjusted F1，且测试数据 / 阈值协议依常用 benchmark；没有线上业务代价、事件共现或 workload context 评估。
- 每点需要多次带噪前向推理，实时报表延迟、吞吐和部署成本未提供系统量化。Table 1 / §5 只指出 overhead 与未来优化。
- 论文报告代码及环境文件在补充材料中，但本地论文索引没有稳定公共仓库 URL；具体复现入口和版本仍需检查附件。

### 我的分析推断

- 这项工作的“鲁棒”明确针对攻击者在 DTW 半径内对输入做时序变形，不应与“区分正常业务波动 / 真故障”混用。业务负载导致的合法均值或周期切换可能超出证书假设，也可能在半径内但对标签语义重要。
- 形式化决策稳定性需要和语义保持威胁模型相匹配。DTW 对齐适合形态平移 / 拉伸，但有的控制系统中时间偏移本身就是故障；应按领域验证 DTW 半径是否真代表语义等价。
- 低覆盖率、零证书和运维可接受的成本应与业务状态条件化报告。仅提高 $\sigma$ 增大证书，同时可能严重降分；这不是免成本安全强化。

## 9. Relationship to Other Papers

- **CrossAD** 学习正常粗细时间尺度映射，并用残差做检测；本论文用 DTW 约束证明某检测决策对恶意扰动的稳定性，分别是检测表示和对抗安全层。
- **CAPMix** 对训练时合成异常的可信度与判别边界做鲁棒化；此处不造伪异常、不解释正常态，只对预训练打分器做 randomized smoothing。
- **When Model Meets New Normals** 适应测试分布的新正常；此处追求固定预测在指定 DTW 攻击球内不变，不能作为状态适应机制。
- **研究对比** 可将 DTW 证书放在“异常告警稳健性”这一维，与 CAROTS 的因果异常分数、CrossAD 的尺度关联分数分开评价。

## 10. My Understanding

论文的理论桥接是主贡献：把“随机平滑模型对 $\ell_2$ 扰动不变”转成“对 DTW 扰动不变”。Keogh envelope 也暴露了证书松弛的来源——时间轴允许一定范围的对齐偏差，很多 $\ell_2$ 变化可能藏在 envelope slack 内，转成 $e=0$ 或很小的证书。因而论文不是直接在 DTW 球里重新训练或精确搜索所有样本，而是用可计算下界给出保守保证。结果应按“理论可证半径 + 该半径下的正确性覆盖”理解，而不能只看对抗样例上的 F1 增长。

## 11. Questions

1. 真实时序运维中，哪些时间扭曲是语义保持的，哪些平移 / 拉伸本身就是故障？如何由业务专家或事件标签校准 $w$ 和预算 $e$？
2. Keogh $e=0$ 的样本是否在经验 DTW 攻击下仍稳定？更紧下界能否明显提高 coverage，且不损失计算效率？
3. 如何在上线时选择 $\sigma$、$T$、$w$，同时约束告警指标、 certified radius、非零证书率和延迟，而不访问测试标签？
4. 认证包裹的 detector 阈值与分数是否需要重新校准？若在新正常状态期间在线适应，证书是否还能在更新模型上成立？
5. PDF 同时包含 NeurIPS 2025 标记和 2026 arXiv 版本标记，主文及补充附录和会议发表稿是否一致？

## 12. Useful Definitions

- **Percentile smoothing**：对高斯扰动后的异常分数分布取分位数并利用分位稳定界形成分类证书。（§3.2, Eqs. 4–5）
- **DTW certificate**：在以输入序列为中心、半径 $e$ 的 DTW 球内，平滑 detector 决策保持不变的下界保证。（§3.1, §3.2, Theorem 3.3）
- **Keogh lower bound slack**：以局部 DTW envelope 内允许的最大偏移量 $\Delta_i$ 汇总为 $R$；若输入空间证书半径不超过 $R$，则无法推出非零 DTW 证书。（§3.2, Eq. 10）

## 13. Tags

`TSAD` `adversarial-robustness` `DTW` `randomized-smoothing` `percentile-smoothing` `certified-defense` `Keogh-bound` `robustness-certificate` `NeurIPS-2025`
