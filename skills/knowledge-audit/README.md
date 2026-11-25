# knowledge-audit

对知识库做两层只读检查：确定性脚本检查链接、索引、重复身份、Claim schema、源码映射等结构问题；Skill 只对少量相关页面做语义比较。

运行结构检查：

```bash
python3 -m scripts.evolution.audit --json
```

语义审核默认最多读取 10 个相关页面，并为每项写明证据、影响、置信度和建议。Audit 不修改正式知识；有价值的变更转交 `knowledge-evolution` 生成 Proposal。
