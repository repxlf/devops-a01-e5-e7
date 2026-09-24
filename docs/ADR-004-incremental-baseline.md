# ADR-004：增量检测必须携带可匹配的 baseline

## Context

EChecker 不能只收到一个当前 commit。它必须知道历史依赖图来自哪个提交和哪个构建配置。

## Decision

`INCREMENTAL_CHECK` 必须携带 `base_commit`、当前 repository、environment、build、baseline graph URI、baseline commit 和 baseline configuration ID。服务必须拒绝缺失或不匹配的 baseline 或环境配置。

`baseline.commit` 必须等于 `base_commit`，`baseline.configuration_id` 必须等于当前 `environment.configuration_id`。这些跨字段相等关系由校验代码强制。

## Consequences

每次全量检测都要留下可复用的 actual graph artifact，并把提交和 configuration ID 写入产物元数据。
