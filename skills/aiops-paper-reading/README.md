# aiops-paper-reading

## Purpose

对单篇 AIOps、基础设施运维或网络运维论文进行全文阅读，并将任务边界、遥测模态、RCA、Agent、生产环境和 Network AIOps 迁移价值整合进知识库。

## When to use

当用户明确要求正式阅读一篇 AIOps / Infrastructure / Network Operations PDF 时使用。批量发现与批次编排仍由其他现有流程负责；本 Skill 不负责批量编排或自动启动 Knowledge Review。

## Input and output

输入示例：

~~~text
使用 aiops-paper-reading 阅读：
sources/papers/AIOps_papers/xxx.pdf
~~~
输出：

~~~text
papers/aiops/<paper-id>/notes.md
~~~

同时按需更新 concepts/aiops/、相关通用 Concepts、notes/aiops/、notes/learning-log.md、INDEX.md，不移动或提交原始 PDF。

## AIOps-specific analysis dimensions

重点检查：

- Detection、Localization、RCA、Diagnosis、Explanation、Remediation 的任务边界。
- Metrics、Logs、Traces、Topology、Traffic、NetFlow、Tickets、Knowledge 等模态及融合方式。
- Candidate space、candidate pruning、ground truth、topology/graph 语义。
- LLM / Tool / Agent / Multi-Agent 身份、Planning、Observation、Memory、RAG、Verification 和 Human gate。
- Production data、production-scale evaluation、production deployment 的区别。
- Reliability、remediation safety、recovery verification、Reproducibility。
- 对 device、interface、link、optical module、network topology、syslog 和 traffic/NetFlow 的迁移性。

详细字段使用 [AIOps paper template](../../templates/aiops-paper-note.md)；关键事实必须标注 Section、Figure、Table 或 Appendix。

## Git behavior

Source Grounding、Concept integration、cross-links 和质量检查全部通过后，默认执行：

~~~text
git diff --check
→ git add intended knowledge files
→ git commit
→ git push origin main
~~~

不创建空 commit，不 force push，不提交原始 PDF。任务失败、来源核验未通过、存在未解决冲突或 GitHub 同步失败时保留本地状态并报告问题。

## Example

~~~text
使用 aiops-paper-reading 阅读：
sources/papers/AIOps_papers/xxx.pdf
~~~
