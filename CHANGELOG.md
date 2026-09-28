# Changelog

## 2026-09-24 — A01/B01 契约加固

- 补齐 DRAFT、FULL_CHECK、INCREMENTAL_CHECK、REPAIR 的输入约束。
- 强制成功 Job 携带 output，区分 findings、系统错误和 REPAIR 候选拒绝。
- 为 artifact 补充 commit/configuration 元数据，并增加 PATCH_NOTES。
- 增加 MD/RD/一致性报告、202 创建响应和 400 请求拒绝响应样例。
- 增加 REPAIR 报告同源校验、CANCELLED 取消接口和幂等键语义。
- 修正端到端流程，将一致性评估与 RECHECK 分开。

以上 JSON、报告、响应和流程结果均为 `MOCK_FIXTURE` 或 `CONTRACT_EXAMPLE`，不代表真实工具执行结果。

## 2026-09-25 — E3 A 组并行测试基线

- 增加 MD/RD 最小项目以及 C0/C1/C2 连续提交快照。
- 增加实际/声明图构造、`MISSING`/`REDUNDANT` finding 和证据字符串的可测试纯逻辑。
- 增加 `scripts/run_lab.py`、`scripts/verify_docker.py` 和 E3 检查清单。
- 明确区分 fixture 预期结果、dry-run 结果和 Linux 原始观察，未声称真实课程项目实验已经通过。

## 2026-09-28 — E3 基线完整性修正（未提交）

- 补齐 MD 旧产物/clean 对照和 RD 多余重编译的真实行为实验。
- 将课件人工答案独立标为 `INSTRUCTOR_ORACLE`，不再与工具观察混淆。
- 为 C0/C1/C2 创建真实 tags，保存编译命令快照，并修正 C2 的 MODE7 配置标识。
- 增加 Linux/工具前置检查、独占输出目录、汇总命令记录、strace 摘要和失败退出码。
- 不再继承外部文件时间戳，避免 clock-skew 破坏增量构建证据。
