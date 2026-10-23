# 知识档案 — [English title]

## 1. Basic Information / 基本信息

- **English title**:
- **中文译名**:
- **Authors**:
- **Venue / year / CCF**:
- **CCF provenance**：知识库清单 / 用户人工确认 / 原始来源；不得自行推断等级。
- **Original PDF**:
- **Completed reading note**:
- **Knowledge card**:
- **Verified code URL**: 若未核实则填 `null`
- **Research area**:
- **Method tags**:

## 2. Research Scenario / 研究场景

说明真实场景或基准场景、数据模态和形状、输入 / 输出、异常粒度及实际运维需求。区分论文原始目标与本知识库提出的跨领域迁移。

## 3. Research Problem / 研究问题

用“场景 + 现有实践为何失败 + 尚未完成的任务”描述问题。不要把所提模块写成研究问题。

## 4. Core Challenges / 核心挑战

逐项说明具体现象、成因、对检测的影响，以及传统方法难以处理的原因；附上 PDF 定位。

## 5. Limitations of Existing Methods / 已有方法不足

比较已有方法类型、基本假设、实际或作者声称的失效方式，以及本文针对的不足。区分作者主张和直接实验依据。

## 6. Core Idea / 核心思想

准确、通俗地解释整体设计为何如此，使读者形成忠实的端到端理解。

## 7. Technical Innovations / 技术创新

逐项说明论文声称的贡献：名称、对应挑战、机制、相对于已有工作的实际新意、支持实验、适用条件和限制。不要把常见 backbone 当成创新。

## 8. Methodology / 方法详解

### A. 总体架构

### B. 数据处理

### C. 模块机制

针对每个重要模块，说明输入 → 操作 → 输出 → 作用。

### D. 关键公式与优化目标

定义符号、损失函数及其训练含义，引用论文公式编号。

### E. 训练流程

### F. 推理流程

### G. 端到端技术流程

用紧凑步骤串联 `输入 → 预处理 → 表征 / 模型 → 分数 / 判定 → 输出`。原文未说明的细节标为“原文未明确说明”。

## 9. Experimental Evidence / 实验依据

### 数据集、Baseline 与指标

### 主要结果

### 消融实验

### 鲁棒性、泛化与工业验证

对每项关键结果注明证据范围，以及它不能证明什么。

## 10. Limitations / 局限性

### A. 作者明确承认的局限

### B. 基于方法或实验的分析推断

说明每条推断基于的方法细节或评估范围。

### C. 尚缺乏的证据

没有某项实验代表证据边界，不代表方法必然不具备该能力。

## 11. Research Implications / 研究启示

可复用思路、AIOps / 其他领域迁移、Baseline 价值及未来假设均标记为“本知识库分析”，除非作者原文明确提出。

## 12. Related Papers / 相关论文

链接稳定论文 ID，并说明关系属于同类问题、相似机制、互补方法或后续工作。

## 13. Evidence References / 证据来源

| Claim area | PDF filename | Section / page / table / figure / equation | Status |
| --- | --- | --- | --- |
| ... | ... | ... | Verified / 待确认 |

正文的重要主张旁也应标注来源定位。

<!-- paper-knowledge-record:start -->
```json
{
  "schema_version": "1.0",
  "paper_id": "stable-lowercase-id",
  "title_en": "",
  "title_zh": "",
  "authors": [],
  "year": null,
  "venue": "",
  "ccf_level": null,
  "ccf_provenance": "",
  "pdf_path": "",
  "reading_note_path": "",
  "knowledge_card_path": "",
  "code_url": null,
  "research_area": "",
  "method_tags": [],
  "research_scenario": "",
  "research_problem": "",
  "core_challenges": [],
  "existing_method_limits": [],
  "core_idea": "",
  "technical_innovations": [],
  "methodology": {
    "architecture": "",
    "data_processing": "",
    "modules": [],
    "key_formulas": [],
    "training": "",
    "inference": "",
    "end_to_end": ""
  },
  "experimental_evidence": {
    "datasets": [],
    "baselines": [],
    "metrics": [],
    "main_results": [],
    "ablations": [],
    "robustness_generalization": [],
    "industrial_validation": []
  },
  "limitations": {
    "author_stated": [],
    "reasoned_inference": [],
    "evidence_gaps": []
  },
  "research_implications": [],
  "related_papers": [],
  "evidence_references": [],
  "provenance": {
    "pdf_sha256": "",
    "reading_note_sha256": "",
    "knowledge_card_sha256": "",
    "extraction_status": "complete"
  }
}
```
<!-- paper-knowledge-record:end -->
