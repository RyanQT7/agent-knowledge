Status: evolving

# Skill

## Definition

初始占位定义：可复用的任务能力、流程或行为规范。

## Why It Matters

## Core Mechanism

## Typical Architecture

## Example

## Related Concepts

## Representative Papers

## Representative Systems / Code

## Advantages

## Limitations

## My Understanding

## Engineering Interpretation from This Knowledge Base

当前知识库中的 `SKILL.md` 更接近一组可复用的 instructions、SOP、输入/输出约定和质量检查。它不是模型能力、不是可执行 Tool，也不是 Agent Runtime。

源码中的 Agent 可以在运行时加载一组 Skill，再用 Skill 约束 prompt、tool selection、状态读写和检查流程；但是否真正执行这些约束取决于 Runtime。当前的 `paper-reading`、`knowledge-review`、`knowledge-query`、`aiops-paper-reading` 和 `agent-framework-learning` 是这一工程含义的实例，而不是论文界统一的 Skill 定义。

## Open Questions
