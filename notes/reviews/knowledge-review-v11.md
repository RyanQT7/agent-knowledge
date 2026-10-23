# Knowledge Review v11：TSAD batch 9 — 平滑预测、重建趋势与正常流形约束

## Scope and Evidence Labels

本次评审第 25–27 篇，累计 **27/33** 篇已完成实际 PDF 精读：

- [KAN-AD](../../papers/kan-ad/notes.md)：Fourier 平滑函数预测与周期索引特征。
- [RTdetector](../../papers/rtdetector/notes.md)：原分布趋势恢复、自条件双解码与 RT-Attention。
- [Idempotent Reconstruction / IGAD](../../papers/idempotent-reconstruction/notes.md)：重建模型训练期幂等与 manifold tightness 正则。

本文区分**论文明确提出或解释**、**实验直接支持**和**跨论文分析推断**。不同数据、指标和阈值设置不构成统一 leaderboard；本评审不据此给三篇排总体名次。

## 1. 核心机制与参照对象

| Paper | 正常性参照 / 假设 | 学习与推理路径 | 证据边界 |
| --- | --- | --- | --- |
| KAN-AD | 正常序列由平滑的一元函数及周期索引模式近似；有限 Fourier 基舍弃局部高频残差 | 单变量一步预测；Mapping→Reducing→Projection，预测偏差用于检测 | 4 个 UTS 主测，Event F1 为主；TODS 合成污染实验；正文未清楚定义统一最终 score 方程（§§3–4, Eqs. 3–12, Table 2） |
| RTdetector | 序列的局部依赖加原始均值 / 方差趋势；异常由首轮和 focus 后重建残差共同显现 | 标准化 Transformer、自条件双解码、RTE、RT-Attention；POT 阈值 | UCR / MBA / SMD / SMAP，非重叠窗口 10；SMAP 非最佳，窗口 >10 可退化（§§3–4, Tables 1–3） |
| IGAD | 正常点应靠近重建映射的 target fixed-point manifold；异常应不落在该紧致区域 | 包装既有重建器，训练加入 FFT 增强、幂等和 tightness loss；推理复用原始重建误差 / auxiliary score | 15 模型 × 4 数据；主指标 VUS-PR、5 seeds；52/60 组合提升但有 8 个回退，按模型 / 数据集调参（§§3–4, Tables 1–2; p.59） |

它们处理重建 / 预测泛化的不同位置：KAN-AD 在**函数表示**上限制局部过拟合；RTdetector 在**输入统计量、注意力和第二次重建**中保留趋势并突出难重建部分；IGAD 直接改**重建映射的训练几何**，使正常附近的映射趋于幂等并收紧目标区域。三者不是同一种“抑噪模块”。

## 2. 每篇的实验证据和反例

### 2.1 KAN-AD

- **[实验支持]** Table 2 的平均 Event F1 为 KAN-AD .7798、KAN .6835、LSTMAD .6808、FCVAE .6743；作者据此报告平均约 15% 增益。（§4.2, Table 2）
- **[实验支持]** CTE、Fourier 函数族及周期 / 原始 / Fourier 组合都有消融；274 参数及 UCR CPU / GPU 时间支持其轻量设计。（§4.4, Figs. 4–6; Table 3）
- **[有限鲁棒证据]** TODS 训练污染比例由 10% 增至 40% 的受控实验中相对稳定，但仅覆盖指定合成数据构造。（§4.4.4, Fig. 7）
- **[证据边界]** 单变量主实验与 channel-independent MTS 扩展使用不同指标；Best F1 带阈值搜索 / 点调整，不能代替固定运行点表现。（§4.1.4; Appendix A.3）

### 2.2 RTdetector

- **[实验支持]** UCR / MBA / SMD F1 为 .9910 / .9865 / .9983，但 SMAP .9094 低于 DCdetector .9702。（§4.2, Table 1）
- **[消融支持]** UCR 完整模型 .9983；移除 RTE 后 .9877，移除 RT-Attention 后 .9868。（§4.3, Table 2）
- **[证据边界]** 非平稳 SMD 上的优势支持该 benchmark 现象，不能单独证明 RTE 能解释任意分布变化；窗口长度超过 10 后退化，且速度不是所有基线中最快。（§4.3–4.4, Table 3）
- **[需核对]** Eq. (3) 印刷的反归一化括号顺序异于常见形式，笔记保留公式并建议与代码核对，不静默改写。（§3.2, Eq. 3）

### 2.3 IGAD

- **[实验支持]** 15 个模型平均 VUS-PR 在 SMD、MSL、PSM、SMAP 分别 .1554→.1752、.0416→.0920、.1542→.1592、.3223→.4056；52/60 组合提升，8 个下降。（§4.1, Table 1）
- **[消融支持]** 两个 MAE 正则都用时平均约 .208；去掉 idem、平滑 tightness 或两者后分别约 .1914、.1822、.1684。（§4.3, Table 2）
- **[有限鲁棒证据]** 1–20% Gaussian test noise 的图显示若干模型 / 数据组合较稳；并非真实 workload shift / 合法状态变迁验证。（§4.2, Figs. 3–4）
- **[资源与稳定性边界]** 作者承认部分下降、更大的标准差及额外训练成本；OFA 个别设置增加约 200.5 秒 / epoch、显存可增约 8.5GB。（Limitations, p.59; Appendix efficiency）

## 3. 正常状态、波动与异常判据

### 多种正常运行状态如何建模？

- **KAN-AD** 用可组合的 Fourier 阶和时间索引编码表示不同平滑 / 周期形态。它允许形态共存于输入表示，但没有明确状态聚类、业务状态标签或状态间转移模型。（§3.2, Eq. 5）
- **RTdetector** 保留每个窗口的统计位置 / 尺度，使模型不必把不同均值、方差变化全部归一为同一模式；不过其 reference 是数值统计量，不区分这些变化分别来自扩缩容、发布、周期负载或传感器漂移。（§3.2–3.3）
- **IGAD** 以正常映射 fixed points 和频域采样的附近扰动扩大可容忍的正常区域，目标是收紧异常可被重建的空间；它并不为不同正常群体建立具名或条件化的 manifold。（§3.1–3.3）

**[跨论文推断]** 平滑函数、局部统计趋势、频域邻域和固定点流形，都是正常性假设的不同数值表征；它们提升对波动的容纳能力，不等于识别“当前业务正处于哪个状态”。这一边界也见 MACE / Graph-MoE 的多模式参照、When Model Meets New Normals 的新状态适配、TimeRCD 的序列相对上下文和 IMPACT 的 reference normals；这些已存在机制说明“多个 normal references”本身不能作为未探索问题。尚需验证的是状态语义、切换时的更新安全与故障敏感度能否同时保留。

### 正常业务波动与真实故障如何区分？

- KAN-AD 将局部高频变化视为可能不应拟合的残差；这可抑制噪声，也可能将短时故障一并平滑掉。论文报告 benchmark / 合成污染，而没有以 workload 变动标签和故障真值拆分两类变化。（§1, §4.4.4；分析边界）
- RTdetector 将均值 / 方差和自条件重建误差纳入证据；趋势变化被保留，但趋势来源没有解释，也没有在“仅负载变更、仅故障、两者并发”的对照中证明区分能力。（§3; §4）
- IGAD 的 Gaussian noise 测试支持一定数值噪声下的分数稳定；噪声不是业务变化，tightness 也不能判断一个稀有正常状态是否合法。（§4.2; 分析推断）

与此前 24 篇相比，新增三种针对拟合 / 重建过泛化的机制，但截至 27 篇，仍没有覆盖真实 workload / release / Trace 条件下的状态变化、故障与并发矩阵。现有 AIOps 论文提供拓扑、事件和证据链的部分素材，但并非这些 TSAD benchmark 已经验证了并发检测。

### 方法是抑噪还是解释来源？

KAN-AD 通过截断傅里叶项过滤不平滑变化；RTdetector 通过统计趋势和双残差暴露难重建点；IGAD 通过形状 / 固定点约束提高异常与正常的可分性。它们都改进异常分数证据，但均不输出为何某次波动由某业务活动造成的可验证来源解释。解释性需要与检测分数、attention / reconstruction pattern、业务因果 / Trace attribution 区分。

## 4. 与此前方法的关系和边界

1. **与多模式 / 频域方法**：MACE 显式建服务条件多频谱正常原型；KAN-AD 用 Fourier 基构造平滑函数族；IGAD 使用 FFT 只用于训练增强。三者中只有前者构建明确原型记忆，不能将所有“使用频域”视作同一机制。
2. **与在线适配**：When Model Meets New Normals 面向观察到的新正常状态做测试时更新；RTdetector 保留分布统计但不在线辨认并适配新状态，IGAD 通过固定训练目标改善泛化，也不等同 TTA。
3. **与鲁棒性论文**：Fortifying Time Series 的目标包括受约束输入变化下的鲁棒性 / 认证；KAN-AD 的合成训练污染、IGAD 的 Gaussian 测试噪声、RTdetector 的非平稳 benchmark 结果分别是不同 robustness protocol，不应互换称为同一类鲁棒性证明。
4. **与重建式防过拟合**：RTdetector 是模型结构 / 目标；IGAD 是可插拔训练包装；IMPACT 则用 few-shot 标签与 validation-risk influence 清理污染。其监督前提和 inference score 完全不同。
5. **与上下文方法**：TimeRCD 使用当前长程序列关系定义局部 discrepancy；Delving 让自然语言背景参与 filtering；KAN / RTdetector / IGAD 的 context 仍是数值窗口与模型分布，没有业务元数据。

## 5. 研究空白（限定当前 27 篇范围）

以下判断由单篇证据及 Reviews v3–v10 共同支撑，不声称穷尽全领域：

1. **状态身份与统计变化的分离**：已有 Fourier 多模式、memory/prototype、TTA、context-relative normality、统计趋势及 fixed-point manifold；但这些方法是否能把合法状态切换识别为状态事件、并在状态内继续检出异常，缺少带状态标注的统一实验。（KAN-AD §3; RTdetector §3; IGAD §3; WMMNN / MACE / TimeRCD notes）
2. **状态变化 + 故障并发**：27 篇 TSAD 笔记尚无真实业务负载变化与已知故障并发的系统测试。重要控制应含仅状态变化、仅故障、并发、未见合法状态及跨实体迁移，而不只增加 Gaussian noise 或污染训练异常。（IGAD §4.2; KAN-AD §4.4.4; RTdetector §4; Reviews v3–v10）
3. **稳健性证据不可横向等价**：论文分别研究训练污染、数值测试噪声、非平稳子集、对抗 / 受限时间变形；应在统一扰动来源、强度、事件指标及 fixed-FPR 运行点下比较。（KAN-AD §4.4.4; IGAD §4.2; RTdetector §4; Fortifying notes）
4. **稀有正常群体安全**：IMPACT 明确指出 rare normal subpopulation 可能被 influence rule 误翻；IGAD 的 manifold tightness 与 KAN 的平滑 prior 也可能压缩合法稀有形态。缺少按业务群体 / 状态报告 false alarm 与保留率的共同比较。（IMPACT Appendix I; IGAD §3.2; KAN-AD §3）
5. **检测分数与业务解释分离**：已有频域、注意力、重建残差、relative discrepancy、影响方向等可视化 / 分数，但还缺基于 Trace、release、负载或注入故障来源标签的忠实性验证。（27 篇对应笔记，尤其 KAN-AD §§3–4、RTdetector §§3–4、IGAD §§3–4）
6. **操作性阈值与延迟**：Best-F1 / 点调整、POT、$\mu+3\sigma$、AUC / VUS 等协议不同；需要统一 validation-only calibration、固定误报预算、告警延迟、事件合并和训练 / 推理开销，且说明跨服务部署时哪些量需重估。（三篇 §4；Quo Vadis / TSB-AD notes）
7. **复现细节**：KAN-AD 主文未清楚列最终 anomaly score；RTdetector Eq. (3) 需核对括号；IGAD 的调参和数据预处理需锁定。报告公式 / 代码差异本身是复现质量的一部分。（各笔记 §5–7）

## 6. TSAD 问题进度（27 篇范围）

| 研究问题 | 状态 | 当前证据边界 |
| --- | --- | --- |
| 多种正常状态如何建模？ | Partially Answered | prototypes、memory、频谱、TTA、长程上下文、统计趋势、固定点流形已有机制；状态语义识别和安全更新未充分验证。 |
| 正常业务波动与真实故障如何区分？ | Partially Answered | 有平滑、趋势恢复、重建分数、关系、视觉和影响证据；缺真实业务状态及故障并发矩阵。 |
| 方法是否只抑噪，是否解释来源？ | Partially Answered | 表征 / 分数比简单阈值丰富，但业务来源 attribution 仍未被上述证据证明。 |
| 是否使用 Metric、Trace、workload、release？ | Open | TSAD 论文大多把数值序列作为输入；少量模拟文本上下文不等同真实 Trace / release-conditioned benchmark。 |
| 正常负载变更和故障并发时如何处理？ | Open | 截至 27 篇没有系统真实并发控制评估；合成噪声和训练污染并非替代品。 |
| 哪些相关思路已被提出？ | Partially Answered | 多 prototype / memory、频谱 normality、TTA、context-relative scoring、VLM 核验、open-set influence、平滑预测、趋势重建、idempotent manifold 均已提出。 |
| 哪些结论缺少充分实验？ | Partially Answered | 状态语义 / 并发、rare-normal safety、跨 generator / 实体、解释忠实性、固定运行点和统一鲁棒性 protocol 证据不足。 |

## 7. 知识库检索路径

- 单篇细节：各 paper note 的“方法细节 / 实验设计 / 局限”部分；知识卡片适合快速比较和主题检索。
- 批次关系：本 Review 对照 KAN-AD、RTdetector、IGAD；Review v3–v10 追踪此前状态 / 因果 / benchmark / context 论文的变化。
- 研究问题：`notes/questions.md` 的 TSAD 当前状态和逐篇问题；`INDEX.md` 的论文入口及 `notes/learning-log.md` 的批次进度。
- PDF 源证据：每篇笔记开头链接至 `sources/papers/tsad-2024-2026/` 下原 PDF。

## 8. 下一批（28–30）

按表示与稳健证据继续阅读：

1. **ScatterAD**：时序-拓扑散射表示；与频域、曲率 / 多域表示比较。
2. **COGNOS**：受约束 Gaussian noise optimization / smoothing；检查其噪声假设与鲁棒性评价。
3. **TeamWork**：asymmetric role-aware channel modeling；比较多变量通道角色和关系建模。

下一批后再读 AnoMamba、Multi-View Ensemble 与 conditional normalizing flow，聚焦全局依赖和生成式 / coupling-flow 异常证据。
