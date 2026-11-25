# research-discovery

发现与当前 Research Questions、Research Gaps 和 Reading Roadmap 相关的新论文或源码，并把经过去重和优先级筛选的元数据写入 `evolution/inbox/candidates.jsonl`。

它不代替全文阅读，也不从摘要推断方法结论。增量游标保存在 `evolution/state/discovery.json`；源不可用时记录失败并继续其他来源。

入口示例：

```bash
python3 -m scripts.evolution.discovery --topic agent-memory --json
python3 -m scripts.evolution.discovery --query "AgentOps trajectory failure attribution" --source arxiv --source github --json
```

完整迭代应使用 `knowledge-evolution`。GitHub MCP 不可用时使用公开 GitHub API/页面或只读 Git 查询，并记录 fallback。
