# LLM-Driven Microservice Anomaly Generation — 下载与版本核验

## 范围与结果

按用户指定的 7 个标题、DOI、arXiv ID 和正式出版入口核验。知识库内此前未发现这 7 篇论文对应的完整精读笔记、知识卡片或知识档案；跨 sources/papers 下的 SHA-256 精确比对也未发现重复 PDF。新增 6 份 PDF 并完成全文阅读；AMulSys 因当前可核验的合法全文不可获取而保留为待获取，不以摘要代替精读。

6 份 PDF 均有有效 PDF 文件头和 EOF 结束标记，file 识别为 PDF，SHA-256 均唯一。PDF 原始字节未修改，且均被 .gitignore 的 sources/papers/**/*.pdf 规则忽略。

## 论文状态

| 论文 | 年份 / 出版信息 | 原始入口 | 本地 PDF | 状态 | 重复 |
| --- | --- | --- | --- | --- | --- |
| TraceLLM — Large Language Models as Realistic Microservice Trace Generators | 2025, EMNLP | [ACL Anthology](https://aclanthology.org/2025.emnlp-main.4/) | tracellm_emnlp2025.pdf | 正式公开 PDF 已下载，全文精读完成 | 否 |
| LLM-AP — LLM-Based Anomaly Detection with Synthetic Time-Series Data Augmentation | 2026, Applied Sciences 16(14), 6851 | [DOI / MDPI](https://doi.org/10.3390/app16146851) | llm-ap_applied-sciences-2026.pdf | 正式开放全文 PDF 已下载，全文精读完成 | 否 |
| Synthetic Time Series for Anomaly Detection in Cloud Microservices | 2024, MLDS 2024；arXiv:2408.00006 | [arXiv](https://arxiv.org/abs/2408.00006) | synthetic-cloud-microservices-arxiv2408.00006.pdf | 作者公开预印本已下载；文内注明 MLDS 2024 接收，全文精读完成 | 否 |
| AMulSys — Anomaly Detection for Microservice System via Augmented Multimodal Data and Hybrid Graph Representations | 2025, Information Fusion 118, 103017 | [DOI / ScienceDirect](https://doi.org/10.1016/j.inffus.2025.103017) | 无 | 出版方需购买全文；直接访问 PDF 返回 403，未找到可核验的合法作者公开全文；待获取 | 否 |
| GenIAS — GenIAS: Generator for Instantiating Anomalies in Time Series | 2026-02-05 v2, arXiv preprint | [arXiv](https://arxiv.org/abs/2502.08262) | genias_arxiv2502.08262.pdf | 最新 v2 公开 PDF 已下载，全文精读完成；不标注为已接收会议论文 | 否 |
| MODIFy — A Multi-modal Anomaly Diagnosis Framework with Diffusion-enhanced Adaptive Fusion in Microservices | 2026, Journal of Systems and Software 237, 112844 | [DOI / ScienceDirect](https://doi.org/10.1016/j.jss.2026.112844)；[作者公开存档](https://zenodo.org/records/19016326) | modify_jss-2026.pdf | JSS 论文对应的作者公开 PDF 已下载并核验，全文精读完成 | 否 |
| AIOpsLab — A Holistic Framework to Evaluate AI Agents for Enabling Autonomous Clouds | 2025, MLSys 2025 | [MLSys Proceedings](https://proceedings.mlsys.org/)；[arXiv](https://arxiv.org/abs/2501.06706) | aiopslab_mlsys2025.pdf | MLSys 正式会议 PDF 已下载，全文精读完成 | 否 |

## 版本及事实边界

- TraceLLM 以 ACL Anthology 正式论文 PDF 为准。
- Synthetic Time Series 保留 arXiv 作者版本；其会议接收信息来自论文正文，不将 arXiv 预印本误标作 CCF 会议论文。
- GenIAS 使用 arXiv v2；作者列表按该版本 PDF 首页记载，其中作者为 Mike Wang。
- MODIFy 使用作者合法存档的 JSS 论文 PDF；Zenodo 文件 MD5 与下载件一致。它是异常诊断模型，不生成异常样本，也不使用 LLM。
- AIOpsLab 使用 MLSys 正式会议版本。该版介绍框架包含 100 个问题，但由于评估成本只选 48 个代表性场景作实验；不将 arXiv 早期版本摘要中的场景数混作正式版实验数。
- AMulSys 仅有出版元数据和受限摘要预览。本次没有形成精读笔记或知识卡片，也没有将其记作已完成知识档案。

## 校验记录

| 文件 | 字节数 | SHA-256 | PDF 结构检查 | 与知识库已有 PDF 精确重复 |
| --- | ---: | --- | --- | --- |
| aiopslab_mlsys2025.pdf | 746003 | ea8af2dc2bb1409b8d29ef0f571a3e4a22806cf32c81934367695da277b7d9f5 | 通过 | 否 |
| genias_arxiv2502.08262.pdf | 3244400 | 8c3e6800591915b34f00f3c3a20aa82f9050175b978f495f81be2cef847584fb | 通过 | 否 |
| llm-ap_applied-sciences-2026.pdf | 2133733 | 834536d5ab3c8095c4b27aeda10f9f0587d544d7c9c24061fff52489085fbef3 | 通过 | 否 |
| modify_jss-2026.pdf | 2601773 | 3d00001f633dd5e6421420906e0581010090aa4b8878dbbcacac9cf520e4a15b | 通过；Zenodo MD5 匹配 | 否 |
| synthetic-cloud-microservices-arxiv2408.00006.pdf | 1312554 | d75d18d66929feb72b25763a5b56e2e014380a14f1292cd130213398e1a91214 | 通过 | 否 |
| tracellm_emnlp2025.pdf | 621238 | 4d34ad1dff644e65d1d0fd6ca816cba9664747ccc46c45f405a019eef2cd9c26 | 通过 | 否 |

PDF 由 .gitignore 忽略；本报告、CSV 和 Markdown 知识成果可纳入 Git。PDF 校验用于格式、完整性、标题版本和重复检查，不涉及改写论文内容。

## 专题研究边界

本集合覆盖 LLM 生成调用 Trace（TraceLLM）、LLM 生成单变量数值异常（LLM-AP）、传统合成数据增强（GenIAS）、云微服务负载与故障注入数据构造（Synthetic Time Series）、三模态异常诊断（MODIFy）、真实测试床故障注入与 Agent 评估（AIOpsLab），以及待获取的多模态增强检测论文 AMulSys。它们的任务不同，不能将 Trace 生成、数值异常合成、运行时故障注入和融合遥测检测统一宣称为同一种异常生成能力。
