Status: evolving

# MCP

## Definition

初始占位定义：用于连接模型应用与外部工具、资源或提示的标准化协议。

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

## Framework Implementation Examples

源码阅读补充了 MCP 的位置：它是把远程能力发现、参数 schema、调用和结果转换接入 Agent Runtime 的协议/适配层，不是 Agent、Skill、Memory 或 Knowledge Base。

- smolagents 的 `ToolCollection`/MCP client 可将 MCP tools 接入工具集合。
- OpenAI Agents SDK 通过 `AgentBase.mcp_servers` 将 MCP tools 纳入 Agent 能力。
- Microsoft Agent Framework 的 `_mcp.py:MCPTool` 负责发现、调用、错误/metadata 处理和结果规范化。

这些项目证明的是“协议如何进入 tool surface”，不是 MCP 自动提供了安全、语义记忆或领域 verification。

## Open Questions
