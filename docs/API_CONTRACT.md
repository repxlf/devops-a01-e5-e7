# API 与 Job 契约

E2 阶段只定义接口，不要求部署服务。

## 创建接口

```http
POST /v1/dockerfile-jobs
POST /v1/full-check-jobs
POST /v1/incremental-check-jobs
POST /v1/repair-jobs
```

创建任务携带请求体和幂等键，服务立即返回：

```http
HTTP/1.1 202 Accepted
```

```json
{
  "job_id": "job-full-c0-001",
  "status": "QUEUED"
}
```

## 查询接口

```http
GET /v1/jobs/{job_id}
```

查询结果使用 `schemas/task.schema.json` 的统一 Job 外壳。

## 状态

```text
QUEUED → RUNNING → SUCCEEDED
                  ├→ FAILED
                  ├→ TIMED_OUT
                  └→ CANCELLED
```

## 结果区分

- `MISSING` / `REDUNDANT` 属于正常分析 findings。
- 镜像构建失败、任务超时、分析器失败属于 `job.error`。
- Job 可以是 `SUCCEEDED`，同时 output 中包含 MD/RD findings。
