# agent-framework-learning

## Purpose

从开源 Agent Framework、SDK 或 Runtime 的真实源码中学习 Agent 架构和可复用实现模式；不要求存在对应论文。

## Input

可以给出一个或多个 repository URL、项目名称，或明确的框架学习范围。

## Output

生成 `code/agent-frameworks/<framework-id>.md`，记录固定 commit、真实入口、执行链、工具/状态/记忆/循环实现、实现边界和可复用模式，并更新 `code/repository-index.md` 与必要的通用 Concept。

## Method

读取 README、文档、examples 和真实源码，静态追踪：

```text
User Task → Agent/Runner → Model → Decision/Tool → Observation → State → Next Step/Stop
```

外部源码放在被忽略的 `sources/code/agent-frameworks/`，只做静态阅读，不安装依赖、不运行代码、不提交源码。

完成源码身份、固定 commit、执行路径和知识文档检查后，知识库变更默认自动 commit 并 push 到 `origin main`；外部源码永远不进入知识库 Git history。

## Example

```text
使用 agent-framework-learning 学习 https://github.com/huggingface/smolagents
```
