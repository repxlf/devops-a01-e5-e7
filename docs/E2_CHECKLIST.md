# E2 交付检查表

本文件把 PPT 中的 E2 要求映射到仓库文件，便于 A/B 配对组检查。

| PPT 要求 | 仓库位置 | 检查方式 |
|---|---|---|
| 统一任务模型 | `schemas/task.schema.json` | 检查四类 `job_type`、六种状态、成功 output 和公共字段 |
| 四类任务请求/响应 | `examples/draft/`、`examples/e2-contract/`、`examples/repair/` | `python scripts/validate.py` |
| 异步创建和查询 | `docs/API_CONTRACT.md`、`schemas/job-created-response.schema.json` | 检查 POST 202、GET 查询和取消接口约定 |
| FULL_CHECK 输入输出 | `examples/e2-contract/full-check-*` | 检查仓库、commit、镜像、配置和构建命令 |
| INCREMENTAL_CHECK baseline | `examples/e2-contract/incremental-check-*` | 检查环境、构建命令和 baseline commit/configuration 匹配 |
| REPAIR 报告同源 | `docs/ADR-005-repair-report-source-match.md`、`examples/invalid/invalid-repair-mismatched-report.json` | 检查报告 commit/configuration 不匹配时不创建 Job |
| 非法输入拒绝 | `examples/invalid/`、`examples/e2-contract/rejected-invalid-request.json` | 校验非法 job_type、缺字段、缺 baseline 和不匹配 baseline |
| 系统错误与 findings 分离 | `examples/e2-contract/system-error-analysis-failed.json`、`full-check-success.json` | FAILED 写 error，SUCCEEDED 可带 findings |
| MD/RD 报告与依赖图 | `examples/build-checker/`、`schemas/report.schema.json` | 检查报告类型、提交、配置、位置和证据 |
| artifact 传递 | `docs/ADR-002-artifact-uri.md`、各 Job output | 检查 `artifact://` URI、生产 Job、commit 和 configuration ID |
| ADR | `docs/ADR-001` 至 `ADR-005` | 检查问题、决策、替代方案和代价 |
| Backlog | `docs/BACKLOG.md` | 每项有责任方、产物和验收条件 |
| AI 使用记录 | `docs/AI_USAGE.md` | 检查建议、人工判断和验证方法 |
| 个人/Git 追溯 | `docs/GIT_TRACEABILITY.md`、`CHANGELOG.md` | 真实协作后补充作者、SHA、Issue/PR，变更记录保留 mock 标记 |

当前 E2 文件中的项目地址、镜像和提交均为示例值，需在与 B 组协商后替换为实际值。
