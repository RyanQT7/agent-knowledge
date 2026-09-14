# paper-reading

## 用途

阅读单篇学术论文 PDF，并将经过来源核对的理解整合进当前 Markdown 知识库。这个 Skill 关注论文理解、结构化笔记和跨资料知识关联，不是普通 PDF 转文本或批量摘要工具。

## 输入

提供一个知识库内的 PDF 路径即可，例如：

```text
阅读 sources/papers/react.pdf
```

如果路径有大小写或小幅命名差异，Skill 会在 `sources/papers/` 和 `papers/` 等合理位置查找明显对应的文件。

## 主要输出

- `papers/<paper-id>/notes.md`：基于论文模板的完整阅读笔记。
- 相关 `concepts/*.md`：仅在论文带来跨资料价值时更新。
- `notes/questions.md`：可继续研究的问题。
- `notes/learning-log.md`：简短学习记录。
- `INDEX.md`：论文入口索引。
- Git 状态、diff 和来源路径检查结果。

## 目录约定

```text
sources/papers/          原始论文 PDF
papers/<paper-id>/       单篇论文阅读笔记
concepts/                跨资料综合知识
notes/                   个人问题、想法和学习记录
templates/               固定输出模板
```

原始 PDF 不放在 `papers/` 根目录。所有检查通过且确有变更时，默认自动创建一个清晰的 Git commit，并执行 `git push origin main`；不会 force push，也不会上传原始 PDF。
