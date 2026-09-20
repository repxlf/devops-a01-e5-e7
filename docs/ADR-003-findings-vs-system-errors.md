# ADR-003：分离 findings 与系统执行错误

## Context

“发现缺失依赖”和“工具没能完成执行”是两种不同结果。下游 MDFixer 需要消费前者，平台运维需要处理后者。

## Decision

- `MISSING` / `REDUNDANT` 写入报告 findings。
- 镜像构建失败、超时和分析器失败写入 `job.error`。
- 正常分析即使产生 findings，也可以返回 `SUCCEEDED`。

## Consequences

校验脚本和测试必须同时覆盖成功且有 findings、以及真正执行失败的样例。
