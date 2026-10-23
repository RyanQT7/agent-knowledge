# Temporal-Frequency Masked Autoencoders for Time Series Anomaly Detection

## 1. Metadata

- **Authors**: Yuchen Fang, Jiandong Xie, Yan Zhao, Lu Chen, Yunjun Gao, Kai Zheng
- **Year / Venue**: 2024 / ICDE（CCF A，依照人工确认清单）
- **Local PDF**: [原始论文 PDF](../../sources/papers/tsad-2024-2026/2024/ICDE/Temporal_Frequency_Masked_Autoencoders_for_Time_Series_Anomaly_Detection.pdf)
- **DOI**: [10.1109/ICDE60146.2024.00099](https://doi.org/10.1109/icde60146.2024.00099)
- **Code**: [TFMAE repository](https://github.com/LMissher/TFMAE)（PDF p.9）
- **Knowledge Card**: [knowledge-card.md](knowledge-card.md)

## 2. One-Sentence Summary

TFMAE 对同一多变量序列构造“高局部波动时间点遮盖”与“低幅值频率遮盖”两种输入视图，分别用 Transformer 恢复遮盖区域，再以对抗式对称 KL 让正常两视图表示靠近、异常差异保留，并将逐时刻表示差作为 anomaly score，以减少直接重建异常和测试分布漂移带来的影响。（§§III–IV, Eqs. 1–17, pp.3–8）

## 3. Background and Problem Definition

论文关注两种现象。第一，经典 reconstruction detector 可能将训练中见过的异常形态也重建得很好，形成 **abnormal bias**。第二，若正常测试数据相对训练数据发生 distribution shift，重建误差可能把“训练没见过”误当异常。（§I, pp.1–2; §IV-C, pp.6–7）

TFMAE 不再直接用 input-versus-reconstruction error 作为最终分数，而是比较两个不同 mask view 对同一输入形成的逐时间 latent representation。作者的出发点是：两视图对正常片段应保有一致结构；遮盖后无法从正常上下文恢复的异常片段则更可能造成 representation discrepancy。该主张建立在 temporal-frequency consistency 假设上，不能被理解为任意 distribution shift 都必定不改变两视图表示。（§IV-C–D, pp.6–7）

## 4. Core Challenges

1. **重建会“学会”异常**：若异常模式出现在训练数据或上下文内，模型可能将异常也当作可重建模式，降低 reconstruction residual。（§I, pp.1–2）
2. **新正常与新异常都可能偏离训练分布**：分布变化会提高重建误差，但仅凭误差无法区分合法状态变化和故障。（§IV-C, p.6）
3. **时间与频率视角的可恢复单元不同**：时间点可以分出 masked/unmasked tokens；频率经 IDFT 混合回时间域，不能直接套用标准 MAE 的 token encoder/decoder 流程。（§III-B, pp.4–6）
4. **对比学习可能把异常也拉近**：只有正对的两视图表示若统一做 minimize discrepancy，异常表示也可能逐渐靠近，削弱异常分离；作者因此引入 adversarial optimization。（§IV-C.2, pp.6–7）

## 5. Architecture Overview

输入多变量序列 $S\in\mathbb R^{|S|\times N}$，其中 $|S|$ 为时间长度，$N$ 为特征数：

```text
                               ┌─ 时间域 mask：局部窗口 CV 高的 r(T)% 时间点换成 learnable mask token
序列 S ── 两路视图 ──────────┤  └─ unmasked tokens 编码，再插入 masked tokens，temporal decoder 逐点输出 P^(L)
                               └─ 频域 mask：每特征 DFT 后遮盖幅值最低的 r(F)% 频率
                                  └─ 替换成 learnable frequency token → IDFT → 投影 → frequency decoder 输出 F^(L)

两视图 P^(L), F^(L) ── 对称 KL + 对抗式交替优化 ── 逐时间 symmetric KL score ── validation 阈值 δ
```

训练不以恢复原始序列为最终 anomaly objective；mask autoencoder 生成的两路表示通过 Eq. 15 的 min-max 对抗目标训练。推理时按 Eq. 16 对每个时间点计算 symmetric KL。（Fig. 1, Eqs. 1–17, pp.3–8）

## 6. Method in Detail

### 6.1 Temporal masking：遮盖局部波动最大的时间点

给定第 $n$ 个通道在时间 $t$ 周围宽度为 $W$ 的局部窗口，作者以局部 coefficient of variation 衡量波动。按 Eq. 1，将各通道的局部离散程度相对均值归一化并汇总：

$$v_t=\sum_{n=1}^{N}\frac{\mathrm{std}(s^n_{t-W:t})}{\mu^n_t}.$$

（Eq. 1, p.4；边界窗口按实现定义。）较大的 $v_t$ 表示局部变化更大。模型选择排序最高的 $r(T)\%$ 个时间点作为 candidate abnormal observations：

$$\mathrm{idx}^{(T)}=\mathrm{TopIndex}(V,\lfloor r(T)\%\cdot |S|\rfloor).$$

命中的输入被 learnable vector $m^{(T)}$ 替换；其余观察通过线性投影 $u_t=W^{(T)}s_t+b^{(T)}$ 映射到 $D$ 维（Eq. 3）。也就是说，时间 mask 的位置由输入自身的局部波动统计选择，而不是随机抽样或使用标签。高 CV 不一定是故障：它也可能来自合法的负载峰谷，这决定了该机制的风险边界。（Eqs. 1–3, pp.4–5）

**FFT 加速**：逐窗口计算均值、方差包含两个循环。作者用 $\mathbb E[x^2]-\mathbb E[x]^2$ 重新写局部方差（Eq. 4），通过长度 $W$ 的 box filter 与 FFT convolution 计算滑窗统计，借助 Wiener–Khinchin 把该步骤由 $O(N|S|W)$ 加速至 $O(N|S|\log |S|)$（Eq. 5, p.5）。这优化的是 mask 统计，不是 Transformer attention 的复杂度。

### 6.2 Frequency masking：遮盖低幅值频率分量

对每个变量分别做 DFT，按实部和虚部计算幅值：

$$a^n_i=\sqrt{\mathrm{Re}(x^n_i)^2+\mathrm{Im}(x^n_i)^2} \quad \text{(Eq. 7)}.$$

随后选取该通道幅值**最低**的 $r(F)\%$ 个 frequency bins（即对 $-a$ 取 TopIndex，Eq. 8），以 learnable complex frequency token $m^{(F)}$ 替换（Eq. 9），再经 IDFT 回到时间域并线性映射至 $D$ 维 $F\in\mathbb R^{|S|\times D}$（Eq. 10, pp.5–6）。作者认为弱幅值成分往往较短暂；mask 低幅值频率是为了覆盖不同频率异常，不假设异常仅是高频。**频率低幅值并不等于语义不重要**，该前提在别的业务时序上需单独检验。（§III-A.2, Eqs. 6–10, pp.5–6）

### 6.3 两个 Transformer autoencoder

- **Frequency view**：IDFT 后频率分量已混合到各个时间位置，作者直接将所有序列馈入 decoder-only Transformer，用以恢复频率 mask 后应有的时间结构。（Fig. 5 左，§III-B.1, pp.6–7）
- **Temporal view**：先仅对未遮盖时间点编码；对被遮盖 token 加上其原时间位置的 positional encoding，再插回编码序列，最后经 Transformer decoder 得到所有时间点的 $P^{(L)}$。（Fig. 5 右，§III-B.2, pp.6–7）
- **角色区别**：时间 view 保留更多原始观察，被指定为 adversarial training 中较接近 label/reference 的一方；频域 view 通过 low-amplitude mask 提供互补重构上下文。（§IV-C.2, p.7）

### 6.4 对称 KL 及 adversarial training

初始的正样本对比损失为两路最终表示的双向 KL 之和：

$$\mathcal L_{con}=D_{KL}(P^{(L)}\Vert F^{(L)})+D_{KL}(F^{(L)}\Vert P^{(L)}). \tag{14}$$

相较单向 KL，双向形式兼顾两个方向的表示差异。作者发现仅最小化该损失可能使异常的频域 view 也被拉向其 temporal 对应表示，因此改成：

$$\min_{F^{(L)}}\max_{P^{(L)}}\left[D_{KL}(P^{(L)}\Vert F^{(L)})+D_{KL}(F^{(L)}\Vert P^{(L)})\right]. \tag{15}$$

优化时交替进行 gradient stop：一阶段更新 frequency representation 以降低 discrepancy；另一阶段更新 temporal representation 以增加 discrepancy。论文称 temporal view 保留更多原始信息，因此将其作为较稳定参照。目标是使正常观测的两路表示相似、异常处差异维持或扩大。（§IV-C, Eqs. 14–15, pp.6–7）

### 6.5 Anomaly score 与 threshold

逐时间点的分数直接取两路表示的 symmetric KL：

$$\mathrm{Score}(s_t)=D_{KL}(p_t^{(L)}\Vert f_t^{(L)})+D_{KL}(f_t^{(L)}\Vert p_t^{(L)}). \tag{16}$$

若 score 不低于 $\delta$，判为异常（Eq. 17, p.7）。实验中 $\delta$ 通过验证集 score 分布确定，按预设异常比例 $r$ 取异常点阈值：MSL、PSM 为 0.9%，SMAP 0.75%，SMD 0.45%，SWaT 0.3%（§V-A.4, pp.8–9）。因此这不是完全无需阈值假设的部署机制；依赖预设比例是否适合会影响 operational behavior。文中汇报的 P/R/F1 另经过 point adjustment，见 §7。

### 6.6 训练目标、参数与复杂度

- Adam，初始学习率 $10^{-4}$，训练 1 epoch，batch size 64；autoencoder 3 个 Transformer layers，hidden dimension 128，temporal mask 窗口 $W=10$。（§V-A.4, p.8）
- $r(T)$、$r(F)$ 按数据集选择，而不是全局固定；对应最优比例见 §7.3 / Fig. 6。（p.11）
- Mask 计算 FFT 部分为 $O(N|S|\log|S|)$，DFT 亦可用 FFT；整体主要成本由 self-attention 决定，约 $O(LD|S|^2)$。（§III-A.1, §IV-E, pp.5, 8）

## 7. Experimental Design and Evidence

### 7.1 Datasets, baselines, metrics

- **7 个数据集**：5 个真实数据集 MSL、PSM、SMD、SWaT、SMAP；2 个合成集 NIPS-TS-Global 和 NIPS-TS-Seasonal。来源分别含 NASA spacecraft monitoring、eBay server metrics、Internet server、water-treatment facility 与合成 global/seasonal anomalies。Table II 给出维度、train/validation/inference size 和异常比。（§V-A.1, Table II, p.8）
- **14 个 baseline**：LOF、IForest、DSVDD、DAGMM、THOC、OmniAnomaly、TimesNet、GPT4TS、USAD、BeatGAN、DAEMON、TranAD、AnoTran、DCdetector，覆盖 density / tree / clustering / reconstruction / adversarial reconstruction / contrastive 方法。（§V-A.3, pp.8–9）
- **指标**：precision、recall、F1，按文献设置进行 point adjustment：标注异常段里只要命中一点，整段即视作检测成功。（§V-A.2, p.8）
- Baseline 使用官方实现与原论文配置；统一输入长度为 100，threshold 通过 validation set 计算。因此表中比较不是原论文所有参数设置的逐字复现，且点调整提高了区间级命中后的 F1。（§V-A.4–5, pp.8–9）

### 7.2 主结果

Table III（PDF pp.9–10）报告五个真实集上的 point-adjusted P/R/F1，TFMAE 的 F1 为：SWaT 98.36%、PSM 98.56%、SMD 91.24%、MSL 95.15%、SMAP 96.90%，平均 96.04%。表格中多数逐数据集结果为最佳或靠前；例如 average F1 对比中 TFMAE 96.04%，DCdetector 93.51%，但该数值依赖上述 PA 和异常比例阈值协议。

作者对基线的归因包括：时序建模、adversarial reconstruction、contrastive views 和频域输入各有优势。它们是作者对 benchmark 的解释，并非每个因素都由同一控制变量试验独立证明。（§V-B, Table III, pp.9–10）

### 7.3 结构与 mask 消融

- **训练目标与组件（Table IV, p.10）**：去掉 adversarial objective 后，SWaT F1 从 98.36 降至 64.96、SMAP 从 96.90 降至 68.48；SMD 也从 91.24 降到 83.89。反向 adversarial 角色配置在一些数据集可达较高 F1，但总体并非一致更好。去掉 temporal 或 frequency 分支、相应 decoder 后，若干数据集性能下降；例如去掉 temporal decoder 后 SWaT 50.69、SMD 60.58，说明该设置下完整结构重要。各组件收益依数据集而异，不能视为每项 ablation 在所有集都同等显著。
- **Mask 策略（Table V, pp.10–11）**：比较无 temporal mask、按标准差选择、随机 temporal mask，以及无 frequency mask、高频 mask、随机 frequency mask。作者设计的局部波动 temporal mask 与低幅值 frequency mask 整体较有竞争力；高频 mask 在多数任务不如设计方案，支持“异常并不只在高频”这一判断。个别数据的不同指标结果仍有波动。
- **Mask ratio / 架构参数（Fig. 6–7, p.11）**：三层、128 hidden dim、窗口宽度 10 是作者设置下表现较好的选择。Temporal mask 最佳比例（SWaT/SMD/SMAP/PSM/MSL）为 25/5/65/65/55%；frequency mask 为 40/20/30/10/40%。部分 temporal ratio 可提高至 95% 仍保持相近性能，作者归因于 temporal redundancy；frequency mask ratio 过高更容易损害结果，因为一个频率分量承载较多信息。（§V-E, p.11）

### 7.4 Case study 与效率

- **Abnormal bias**：Fig. 8 用 NIPS-TS-Global、NIPS-TS-Seasonal 合成异常展示 score 与已知注入异常的关系；TFMAE 能显示相应 seasonal/global anomaly，DCdetector 在这些例子未能同样识别。（§V-F, pp.11–12）
- **Distribution shift**：Fig. 9 比较 SMAP validation 与 test anomaly-score CDF；TimesNet 两者差距明显，而 TFMAE 的 CDF 更接近。该案例支持在此数据上阈值泛化较稳定，但只是单一数据集的案例，不是跨任务保证。（§V-F, p.12）
- **Efficiency**：Fig. 10 在 SMD 上对比 F1、训练速度和 GPU memory。作者报告 TFMAE 在图中 F1 最高、memory 占用最低、速度排名第二；去掉 FFT 的版本更慢。结论限于所测设备、实现和 SMD 长序列。（§V-G, p.12）

## 8. Contributions and Reproduction Value

1. 提出用 temporal/frequency masking views 及 representation discrepancy 替代直接 reconstruction residual 的检测思路。（§§III–IV）
2. 用窗口 CV mask 识别局部波动候选点，用低幅值频率 mask 覆盖非高频限定的异常模式，并通过 FFT 加速局部统计。（Eqs. 1–10）
3. 引入对抗式 symmetric-KL 目标，让两个 view 在正常点上对齐而在异常点上保留差异。（Eqs. 14–16）
4. 在 7 个数据集、14 个 baseline 上报告主比较、结构和 masking ablation、敏感性、case study 与效率数据。（§V）

复现入口公开，数据集、网络深度、hidden dimension、窗口长度、训练轮次、optimizer 和主要 mask ratio 均有披露。复现应额外确认具体 dataset version / preprocessing、seed、异常比例阈值选择、point adjustment 实现及不同设备上的效率口径。论文没有模型训练之外的系统部署验证；本知识库不执行复现实验。（§V-A, Figs. 6–10; code link）

## 9. Limitations and Critical Reading

- **评测边界**：所有主结果只报告 P/R/F1 且使用 point adjustment，interval 命中后整段回填，可能掩盖边界定位、告警延迟与逐点误报。应结合 TSB-AD、Quo Vadis 对该指标的批评阅读，而非直接把 96.04% 当成无条件可比的业务表现。（§V-A.2, Table III; TSB-AD §3.2）
- **阈值依赖异常率先验**：$\delta$ 按 validation score 以及给定异常比例确定；先验比例错误或业务异常率漂移会改变 precision / alert volume。（§V-A.4, pp.8–9）
- **局部 CV 的业务语义有限**：高局部波动可由正常峰值、切换状态、发布或负载变化导致；算法没有接入 workload、deployment、trace 或 service-state metadata，也不解释波动来源。（Eqs. 1–3; datasets in Table II）
- **频率先验有限**：低幅值频率被遮盖是设计选择，未验证对不同采样频率、非平稳周期、弱但关键的业务模式是否稳定适用；作者在现有 benchmark 上比较了高频与随机 mask，但范围有限。（Table V, Fig. 6）
- **shift 证据范围**：Distribution shift 主案例是 SMAP validation/test score CDF；未系统控制“合法负载/状态迁移与故障同时发生”，也未显示告警判定能解释新正常和故障的因果来源。（Fig. 9）
- **训练和评测成本**：self-attention 仍为 $O(LD|S|^2)$；长序列场景的端到端延迟 / streaming memory 尚需评估。（§IV-E, p.8）
- **作者所述 future work**：将方法拓展至时间序列预测与分类；论文未给出专门 limitation section。（Conclusion, p.12）

## 10. Related Papers

- **MACE**：频域多 pattern normality，显式保留不同服务频谱模式；TFMAE 用幅值 mask 构造自监督 view，并以 view discrepancy 打分。二者都用 frequency evidence，但不等于有业务状态语义。
- **TFC**：并行融合 temporal、frequency 与 curvature score；TFMAE 则通过两种 mask view 的 adversarial latent consistency 构造分数。
- **Quo Vadis / TSB-AD**：指出 PA-F1 对噪声和区间命中的偏向；TFMAE 的高 F1 使用 point adjustment，跨论文解释时必须保留该协议限定。
- **CrossAD、CCM-TAD**：跨窗关联或在线 sequential evidence 也处理不稳定模式 / 顺序上下文，机制与 TFMAE 的时间–频率 mask 不同。
- **When Model Meets New Normals**：直接在测试阶段适应新正常；TFMAE 用双视图分布一致性缓解某种 shift，不进行显式正常状态准入或在线参数更新。

## 11. Questions for Further Reading

1. 如何判定 high-CV 是新正常负载峰值还是故障前兆？将 workload / release / Trace context 加入 view conditioning 是否有效？
2. 正常状态切换与突发故障并发时，两个 view 的 discrepancy 谁占主导？需要怎样的可控数据和事件级指标？
3. 按预设 anomaly ratio 设 threshold 是否能由正常 validation-only 的误报预算替代，并在跨实体迁移时保持校准？
4. 遮盖低幅值频率的设计，对长期弱周期、低能耗但高语义风险异常是否会形成漏报？
5. adversarial 的 min/max 是否对更新顺序、随机种子、损失尺度及训练稳定性敏感？是否提供跨种子的 score distribution？
6. score discrepancy 能否与物理拓扑、依赖图或 trace-level causal evidence 对齐，而非只提供异常强度？

## 12. Key Terms

- **Abnormal bias**：重建器学习到异常形态、导致异常也能较低 residual 重建的现象。
- **Temporal-frequency masking views**：同一输入上分别遮盖高局部波动时间点与低幅值频率分量形成的两路视图。
- **Symmetric KL discrepancy**：两方向 KL 相加，用于比较时间 / 频域 view 的逐时刻 latent representations。
- **Point adjustment**：异常区间中命中任一时间点后将整段计为检测到。

## 13. Tags

`TSAD` `masked autoencoder` `frequency domain` `contrastive learning` `adversarial training` `distribution shift` `point adjustment`
