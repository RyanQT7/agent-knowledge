# source-code-annotation

## Purpose

把开源项目中与核心执行路径相关的真实源码整理成中文教学注释版，帮助从
`入口 → 主循环 → 模型/算法 → 操作 → 状态更新 → 输出` 理解实现。

## Modes

- **General Source Annotation**：输入本地源码或 repository，输出注释版核心源码、执行路径和源码指南。
- **Paper-Aware Source Annotation**：在上述基础上建立保守的 Paper Concept ↔ Source File ↔ Class/Function 映射。

## Outputs

默认写入 `annotations/<project>/<full-commit-sha>/`，包括 `annotated/`、
`EXECUTION_PATH.md`、`CODE_GUIDE.md` 和 `SOURCE_MANIFEST.md`；论文模式另有
`PAPER_CODE_MAPPING.md`。原始源码继续保持在只读、被忽略的外部 source 目录。

## Example

```text
为 sources/code/agent-frameworks/smolagents 的固定 commit 创建中文源码注释版，
重点解释 MultiStepAgent 的 run → loop → tool → observation → memory 路径。
```

This Skill is a teaching transformation after source tracing; it does not replace
`code-reading`, `agent-framework-learning`, or repository discovery.
