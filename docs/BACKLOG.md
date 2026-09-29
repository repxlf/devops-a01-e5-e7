# A 组 Backlog

| ID | 任务 | 责任方 | 产物 | 验收条件 | 状态 |
|---|---|---|---|---|---|
| E2-01 | 统一 Job 模型 | A01/B01 | `schemas/task.schema.json` | 四类任务可表达 | DONE-MOCK |
| E2-02 | FULL_CHECK 输入输出 | A01 | `examples/e2-contract/` | 固定提交和环境可说明 | DONE-MOCK |
| E2-03 | 增量 baseline 校验用例 | A01 (张润弛) | `examples/e2-contract/invalid/`, `tests/` | 缺 baseline、环境或配置不匹配被 400 拒绝 | DONE-MOCK |
| E2-04 | MD/RD 报告 | A01/B01 | report fixtures、`report.schema.json` | 下游能识别 finding、提交、配置和证据 | DONE-MOCK |
| E2-05 | artifact 访问约定 | A01/B01 | ADR-002、artifact schema | 下游知道如何读取 URI、生产 Job、提交和配置 | DONE-MOCK |
| E2-08 | 修复报告输入 | B01 | REPAIR request、ADR-005 | 只消费同源 MD 报告；缺失或不匹配时创建阶段拒绝 | DONE-MOCK |
| E2-09 | 契约一致性加固 | A01/B01 | schemas、validator、HTTP 响应样例 | 成功输出、请求拒绝、REPAIR 拒绝和报告 URI 均有机器可检查的样例 | DONE-MOCK |
| E3-01 | 准备 MD/RD 项目与人工答案 | A01 | `fixtures/e3/md-rd/`、`instructor-oracle.json` | MD/RD 样例、依据和 oracle 与工具输出分离 | DONE |
| E3-02 | 验证 MD/RD 构建行为 | A01 | `scripts/run_lab.py`、Linux evidence | 保存旧产物、clean 对照和多余重编译记录 | DONE |
| E3-03 | 准备 C0/C1/C2 连续版本 | A01 | `fixtures/e3/commits/`、运行时 Git 仓库 | 有三个真实 SHA、tags、配置和命令快照 | DONE |
| E3-04 | 保存 Linux 跟踪与可复跑记录 | A01 | `evidence/linux-verified/` | 环境、命令、输出、报告和 strace 可追溯且无时钟偏移 | DONE |
| E4-01 | 接入老师可重复工程环境模板 | A01 | `services/buildchecker/`、Compose、Makefile、锁文件 | 保留旧契约/基线，E4 从仓库根目录运行 | DONE |
| E4-02 | 个人完整运行与密钥扫描检查 | A01 各组员 | 个人 `work/<时间>/` | doctor/build/test/smoke/scan 通过，假值检测有效 | PER-MEMBER-RUN |
| E4-03 | 第二名组员独立重跑对照 | A01 | 两份同 SHA 的运行记录 | 工具版本和测试结论一致或解释差异 | TODO-MEMBER-RERUN |
| E5-01 | 复现真实 BuildChecker | A01 | `build_checker/` | 从真实执行采集依赖并生成报告 | SCAFFOLD |
| E8-01 | 复现真实 EChecker | A01 | `e_checker/` | 可消费 BuildChecker baseline | SCAFFOLD |
| E10-01 | 增量/全量比较 | A01 | `evaluation/` | 输出一致性和耗时 | SCAFFOLD |

E3 是测试基线准备，不将 E5 BuildChecker、E8 EChecker 或 E10 性能比较的 scaffold 冒充为已实现算法。

E4 模板已在服务器完成首轮代理验证；E4-02 的完成情况以每名组员自己的运行记录为准，
不是通过一个小组提交替所有人完成。两人对照仍需真实组员独立执行，见 `E4_README.md`。
