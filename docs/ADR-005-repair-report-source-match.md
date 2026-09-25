# ADR-005：REPAIR 必须使用与当前源码同源的 MD 报告

## Context

MDFixer 的输入是一份由 BuildChecker 生成的 MD 报告。如果报告来自另一个 commit 或构建配置，修复器可能把不属于当前源码的依赖写入 Makefile，生成表面合法但实际错误的 patch。

## Decision

REPAIR 必须同时携带：

- `repository.commit`
- `environment.configuration_id`
- `md_report_uri`

报告顶层的 `commit` 必须等于 `repository.commit`，报告顶层的 `configuration_id` 必须等于 `environment.configuration_id`。任一不匹配，服务端必须在创建阶段返回 `400 REQUEST_REJECTED`，不创建 Job。

MD 报告只允许包含 `MISSING` findings；`REDUNDANT` 应由独立的 RD_REPORT 传递。

## Alternatives

- 只传报告 URI：请求无法表达服务端应按哪个源码版本校验。
- 将报告 commit/configuration 平铺进请求：同一事实出现两份，容易漂移。
- 不校验，只在结果中标记：错误 patch 会继续进入后续构建和重检。

## Consequences

报告必须保留 commit 和 configuration ID，artifact URI 必须可解析。当前仓库用固定 mock URI 映射验证规则，后续真实实现需要提供 artifact URI 解析器或下载接口。
