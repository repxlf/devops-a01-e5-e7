# ADR-002：通过 URI 传递大型产物

## Context

依赖图、报告、日志和 patch 不适合直接塞进每个 Job 响应。下游服务需要知道文件类型、地址和生产任务。

## Decision

Job output 保存 artifact 元数据，文件内容通过 `artifact://` URI 引用。URI 至少包含配对组、生产 Job 和文件名。

## Example

```text
artifact://pair-A01-B01/job-full-c0-001/actual.json
```

## Consequences

后续实现需要提供 URI 解析器或下载接口，并记录生产任务、提交和 configuration ID。
