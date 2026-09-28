# A 组后续任务路线

| 编号 | 后续任务 | 代码入口 | 验证入口 |
|---|---|---|---|
| A-01 | 准备 MD/RD 项目和 C0/C1/C2（E3 已完成） | `fixtures/e3/` | `tests/test_e3_lab.py`、`evidence/linux-verified/` |
| A-02 | 复现 BuildChecker | `src/a_group/build_checker/` | `tests/build_checker/` |
| A-03 | 采集实际/声明依赖图 | `graph_collection.py` 和 adapters | `tests/build_checker/` |
| A-04 | 检测 MD/RD | `md_rd_detection.py` | `tests/build_checker/` |
| A-05 | 验证证据与正确性 | `evidence.py`、`evaluation/correctness.py` | `tests/evaluation/` |
| A-06 | 复现 EChecker | `src/a_group/e_checker/` | `tests/e_checker/` |
| A-07 | 增量更新依赖图 | `incremental_update.py` | `tests/e_checker/` |
| A-08 | 识别新增/消除 findings | `finding_diff.py` | `tests/e_checker/` |
| A-09 | 比较增量/全量一致性与耗时 | `src/a_group/evaluation/` | `tests/evaluation/` |
| A-10 | BuildChecker → EChecker 联调 | `src/a_group/workflow/` | `tests/workflow/` |

当前仓库已完成 E2 契约和 E3 测试基线，并保留真实 Linux 构建/跟踪记录；A-02 及之后仍是后续检测器工作。E3 的 fixture、人工 oracle、真实工具观察必须继续分开标记，不能用基线结果冒充通用检测器实现。
