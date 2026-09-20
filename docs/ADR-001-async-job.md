# ADR-001：采用异步 Job 模型

## Context

构建、依赖图采集和分析可能超过一次 HTTP 请求的生命周期。配对组需要先获得任务编号，再查询执行状态和产物。

## Decision

创建接口使用 `POST` 并返回 `202 Accepted`，查询接口使用 `GET /v1/jobs/{job_id}`。统一 Job 包含 `job_id`、`trace_id`、`job_type`、`status`、`input`、`output` 和 `error`。

## Alternatives

同步等待实现简单，但会把客户端和长时间执行过程耦合起来，也不适合传递大型日志和产物。

## Consequences

需要任务状态和查询约定。E2 先用契约样例验证，不要求部署 API。
