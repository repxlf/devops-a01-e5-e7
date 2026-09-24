# Changelog

## 2026-09-24 — A01/B01 契约加固

- 补齐 DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 的输入约束。
- 强制成功 Job 携带 output，区分 findings、系统错误和 REPAIR 候选拒绝。
- 为 artifact 补充 commit/configuration 元数据，并增加 PATCH_NOTES。
- 增加 MD/RD/一致性报告、202 创建响应和 400 请求拒绝响应样例。
- 增加 REPAIR 报告同源校验、CANCELLED 取消接口和幂等键语义。
- 修正端到端流程，将一致性评估与 RECHECK 分开。

以上 JSON、报告、响应和流程结果均为 `MOCK_FIXTURE` 或 `CONTRACT_EXAMPLE`，不代表真实工具执行结果。
