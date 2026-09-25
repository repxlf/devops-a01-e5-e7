# A 组 Backlog

| ID | 任务 | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|---|
| E2-01 | 统一 Job 模型 | A01/B01 | `schemas/task.schema.json` | 四类任务可表达 | DONE-MOCK |
| E2-02 | FULL_CHECK 输入输出 | A01 | `examples/e2-contract/` | 固定提交和环境可说明 | DONE-MOCK |
| E2-03 | 增量 baseline | A01 | incremental request | 缺 baseline、环境或配置不匹配被拒绝 | DONE-MOCK |
| E2-04 | MD/RD 报告 | A01/B01 | report fixtures、`report.schema.json` | 下游能识别 finding、提交、配置和证据 | DONE-MOCK |
| E2-05 | artifact 访问约定 | A01/B01 | ADR-002、artifact schema | 下游知道如何读取 URI、生产 Job、提交和配置 | DONE-MOCK |
| E2-08 | 修复报告输入 | B01 | REPAIR request、ADR-005 | 只消费同源 MD 报告；缺失或不匹配时创建阶段拒绝 | DONE-MOCK |
| E2-09 | 契约一致性加固 | A01/B01 | schemas、validator、HTTP 响应样例 | 成功输出、请求拒绝、REPAIR 拒绝和报告 URI 均有机器可检查的样例 | DONE-MOCK |
| E3-01 | 准备 MD/RD 项目 | A01 | `fixtures/projects/` | 有 C0/C1/C2 版本记录 | READY-FOR-INPUT |
| E3-02 | 复现 BuildChecker | A01 | `build_checker/` | 可复现固定提交检测 | SCAFFOLD |
| E3-03 | 采集实际/声明图 | A01 | graph collector | 两类图可导出 | SCAFFOLD |
| E3-04 | 验证检测证据 | A01 | evidence tests | 证据可追溯到提交和位置 | SCAFFOLD |
| E3-05 | 复现 EChecker | A01 | `e_checker/` | 可消费 BuildChecker baseline | SCAFFOLD |
| E3-06 | 增量/全量比较 | A01 | `evaluation/` | 输出一致性和耗时 | SCAFFOLD |

状态中的 `SCAFFOLD` 表示只有接口和测试位置，不代表真实算法已经完成。
