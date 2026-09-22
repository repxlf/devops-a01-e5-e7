# E2 交付检查表

本文件把 PPT 中的 E2 要求映射到仓库文件，便于 A/B 配对组检查。

| PPT 要求 | 仓库位置 | 检查方式 |
|---|---|---|
| 统一任务模型 | `schemas/task.schema.json` | 检查四类 `job_type`、六种状态和公共字段 |
| 四类任务请求/响应 | `examples/draft/`、`examples/e2-contract/`、`examples/repair/` | `python scripts/validate.py` |
| 异步创建和查询 | `docs/API_CONTRACT.md`、`examples/e2-contract/full-check-queued.json` | 检查 POST 202 与 GET 查询约定 |
| FULL_CHECK 输入输出 | `examples/e2-contract/full-check-*` | 检查仓库、commit、镜像、配置和构建命令 |
| INCREMENTAL_CHECK baseline | `examples/e2-contract/incremental-check-*` | 检查 baseline commit/configuration 匹配 |
| 非法输入拒绝 | `examples/invalid/` | 校验非法 job_type、缺 baseline 和不匹配 baseline |
| 系统错误与 findings 分离 | `examples/e2-contract/system-error-analysis-failed.json`、`full-check-success.json` | FAILED 写 error，SUCCEEDED 可带 findings |
| MD/RD 报告与依赖图 | `examples/build-checker/` | 检查 actual/declared graph 与报告字段 |
| artifact 传递 | `docs/ADR-002-artifact-uri.md`、各 Job output | 检查 `artifact://` URI 与生产 Job |
| ADR | `docs/ADR-001` 至 `ADR-004` | 检查问题、决策、替代方案和代价 |
| Backlog | `docs/BACKLOG.md` | 每项有责任方、产物和验收条件 |
| AI 使用记录 | `docs/AI_USAGE.md` | 检查建议、人工判断和验证方法 |
| 个人/Git 追溯 | `docs/GIT_TRACEABILITY.md` | 真实协作后补充作者、SHA、Issue/PR |

当前 E2 文件中的项目地址、镜像和提交均为示例值，需在与 B 组协商后替换为实际值。
