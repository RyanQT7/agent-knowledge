# knowledge-evolution

总调度器，调用 Research Discovery、只读 Knowledge Audit、现有论文/源码阅读和 Proposal 验证。它维护每轮状态，允许中断恢复；正式知识文件不会由未审核 Proposal 自动修改。

```bash
python3 -m scripts.evolution.run start --mode proposal --auto
python3 -m scripts.evolution.run resume <RUN_ID>
```

一次完整流程由 Codex 按 Skill 逐步完成语义阅读、Claim 更新和提案；脚本只负责确定性发现、去重、状态、审计与 Proposal 路径/hash 门禁。无高价值新证据时可正常以 `no_update_needed` 结束。
