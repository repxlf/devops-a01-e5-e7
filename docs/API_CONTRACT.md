# API 与 Job 契约

E2 阶段只定义接口，不要求部署服务。本文描述请求被接受、异步查询、取消和拒绝的边界；JSON 样例全部是 mock/contract fixture。

## 创建接口

```http
POST /v1/dockerfile-jobs       # DRAFT
POST /v1/full-check-jobs       # FULL_CHECK
POST /v1/incremental-check-jobs
POST /v1/repair-jobs
```

创建请求携带请求体和 `idempotency_key`。成功接收后立即返回：

```http
HTTP/1.1 202 Accepted
```

```json
{
  "job_id": "job-full-c0-001",
  "status": "QUEUED"
}
```

对应样例见 `examples/e2-contract/full-check-created.json`。

无效请求在创建阶段拒绝，不创建 Job：

```http
HTTP/1.1 400 Bad Request
```

```json
{
  "error": {
    "code": "REQUEST_REJECTED",
    "message": "INCREMENTAL_CHECK requires a baseline before a Job is created"
  }
}
```

对应样例见 `examples/e2-contract/rejected-invalid-request.json`。

## 查询与取消接口

```http
GET /v1/jobs/{job_id}
POST /v1/jobs/{job_id}/cancel
```

查询结果使用 `schemas/task.schema.json` 的统一 Job 外壳。取消只允许作用于 `QUEUED` 或 `RUNNING` Job，成功后终态为 `CANCELLED`；已完成 Job 不可取消。

## 幂等键

- 相同 `idempotency_key` 与相同请求体：返回原 Job 的 `202` 创建响应，不重复创建任务。
- 相同 `idempotency_key` 与不同请求体：返回 `409 Conflict`，提示幂等键已绑定到另一请求。

## 状态

```text
QUEUED → RUNNING → SUCCEEDED
                  ├→ FAILED
                  ├→ TIMED_OUT
                  └→ CANCELLED
```

## 结果区分

- `MISSING` / `REDUNDANT` 是正常分析 findings。
- 镜像构建失败、任务超时、分析器失败写入 `job.error`。
- Job 可以是 `SUCCEEDED`，同时 `output.findings` 非空。
- REPAIR 候选验证失败不是执行失败：Job 仍为 `SUCCEEDED`，并在 `output.decision` 写 `REJECTED`，原因写入测试报告 artifact。
- `ERROR_REPORT` 只表示系统错误报告，不承载 findings。

## artifact 与报告

大依赖图、报告、日志、patch 和声明风格说明通过 `artifact://` URI 引用。artifact 至少带有：

```json
{
  "type": "MD_REPORT",
  "uri": "artifact://pair-A01-B01/job-full-c0-001/md-report.json",
  "producer_job_id": "job-full-c0-001",
  "commit": "00000000000000000000000000000000000000c0",
  "configuration_id": "cc-MODE0"
}
```

REPAIR 只消费 MD 报告中的 `MISSING` findings；如果报告含 `REDUNDANT`，请求应被拒绝。声明风格说明作为 `PATCH_NOTES` artifact 独立交付。
