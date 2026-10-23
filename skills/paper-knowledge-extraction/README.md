# paper-knowledge-extraction

## 用途

把完成全文精读的论文转为可追溯、可复用的科研知识档案，再按需校验和导出指定论文集合。本 Skill 适用于单篇精读后提取和专题知识打包，不替代 `paper-reading` 或 `knowledge-review`。

## 产物

- `papers/<paper-id>/knowledge-dossier.md`：中文独立档案，含结构化方法 / 实验证据分析、原文定位和机器可读 JSON。
- 批量导出：完整 Markdown、精简总览、JSONL、可选研究问题地图、独立档案副本，以及可选的无 PDF ZIP。
- `INDEX.md`：知识档案集合和查询入口。

## 来源与证据规则

重要机制、公式、新颖性、实验数值和证据冲突应回查原始 PDF。主要依据为完成精读的详细笔记，知识卡片和 Review 仅用于导航和横向比较。明确区分作者主张、实验实际支持和本知识库分析；未知信息标记“待确认”，不得从标题、摘要或记忆补全。

## 验证情况

先用两篇方法差异明显的论文试运行：

- FlowFuse：多视角异常分数与 coupling-flow 融合。
- Conditional Normalizing Flows：条件生成模型、潜动态与 goodness-of-fit 检验。

两份试点档案均通过章节、JSON、PDF / 精读笔记 / 知识卡片哈希校验及无 PDF ZIP 检查。之后同一导出脚本通过了 33 篇 TSAD 知识档案校验。

## 导出脚本

在知识库根目录运行：

```bash
python3 skills/paper-knowledge-extraction/scripts/export_knowledge.py \
  --paper-ids paper-a paper-b \
  --expected-count 2 \
  --prefix paper-knowledge \
  --jsonl-name paper-knowledge.jsonl \
  --output-dir /tmp/paper-knowledge-export \
  --zip
```

TSAD 全集使用前缀 `tsad-33-paper-knowledge` 和文件名 `tsad-paper-knowledge.jsonl`；其他领域选择通用前缀。导出器读取嵌在档案中的 JSON，校验章节、字段、稳定 ID、本地来源路径与哈希，并生成 Markdown / JSONL、独立档案副本和可选无 PDF ZIP。研究问题地图及跨论文结论需要以证据为基础单独撰写，导出器不会代替研究者推断。

如需向精简总览追加手工整理的跨论文关系段落，可使用 `--overview-addendum FILE`。领域专属问题地图必须由研究者根据来源证据撰写。

## 增量和恢复

处理前将档案 JSON 中的 SHA-256 与当前精读笔记、知识卡片和 PDF 比对。仅当这些来源或档案 schema 未变化时跳过重做。长批次定期保存已完成档案和进度清单；后续从清单继续，不重复处理校验通过且来源未变的论文。

完整工作流程见 [SKILL.md](SKILL.md)，新档案采用[知识档案模板](templates/knowledge-dossier.md)。
