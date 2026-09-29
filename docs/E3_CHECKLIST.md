# E3 A 组检查清单

本清单把 `E3_并行测试基线_20260910.pptx` 中 A 组的要求映射到仓库文件。课件给出的人工答案单独标为 `INSTRUCTOR_ORACLE`，静态样例标为 `MOCK_FIXTURE`，Linux 上实际执行工具得到的记录标为 `REAL_TOOL_OUTPUT`。

| E3 要求 | 仓库位置 | 当前状态 |
|---|---|---|
| MD/RD 最小项目 | `fixtures/e3/md-rd/` | 已提供 fixture，并真实验证旧产物与多余重编译 |
| 课件人工答案 | `fixtures/e3/instructor-oracle.json` | 与工具观察分离并标明课件来源 |
| C0/C1/C2 连续提交样例 | `fixtures/e3/commits/C0/`、`C1/`、`C2/` | 运行时创建真实提交和同名 tags，保存完整 SHA |
| C0 正确初始版本 | `fixtures/e3/commits/C0/` | 预期 clean build 为 10 |
| C1 增加 `feature.h` include，Makefile 不变 | `fixtures/e3/commits/C1/` | 预期为 `MISSING main.o -> feature.h` |
| C2 只修改 `-DMODE=7` | `fixtures/e3/commits/C2/` | 普通增量构建预期 12，clean build 预期 19 |
| MD 行为对照 | `work/<run>/observations.json` | 初始 1、改 `config.h` 后增量 1、clean 后 2 |
| RD 行为对照 | `work/<run>/observations.json` | 改 `unused.h` 后记录 `main.o` 的多余重编译 |
| C1/C2 编译命令快照 | `work/<run>/observations.json` | 保存 `make -n -B main.o`，验证 C2 命令发生变化 |
| Linux 工具版本 | `scripts/verify_docker.py`、`work/<run>/environment.json` | 要求 Linux、git、make、cc、strace、Python |
| 实际/声明依赖图 | `src/a_group/e3/lab.py`、`work/<run>/graphs/` | fixture 解析器，预留真实采集器替换点 |
| `MISSING` / `REDUNDANT` | `src/a_group/e3/lab.py`、`work/<run>/reports/` | 有单元测试和证据字符串 |
| 命令、文件变更、退出码、输出、耗时 | `scripts/run_lab.py`、`work/<run>/commands.json` | 实际运行时完整保存 |
| 原始观察与预期结果分离 | `work/<run>/observations.json` | oracle、fixture 和工具观察分别标记 |
| Linux 原始证据 | `evidence/linux-verified/` | 仅接受人工/CI 在 Linux 上生成的记录 |

## 推荐运行顺序

在要求的 Linux 环境中执行：

```bash
python3 scripts/verify_docker.py
python3 scripts/run_lab.py --strace --output-dir work/e3-<timestamp>
```

然后检查：

1. `environment.json` 是否包含系统、CPU 架构、GNU Make、C 编译器、Python 和可选 `strace` 版本。
2. `commands.json` 是否保存了文件变更、`make clean`、`make`、程序执行及 C0/C1/C2 Git 操作；`commands/commit-repository.json` 是否保存 Git 子集。
3. `graphs/` 是否同时有 actual 和 declared 图。
4. `reports/` 是否出现 MD/RD 报告，且 finding 能回溯到源文件、Makefile 行或构建命令。
5. MD/RD 行为是否依次为 1、1、2、2，且修改 `unused.h` 后确实出现 `main.o` 重编译。
6. C0/C1/C2 是否有三个不同 SHA 和同名 tags；C2 普通构建与 clean build 是否分别为 12 和 19。
7. `trace_summary` 是否同时记录 `config.h` 和 `feature.h`，并可回溯到 `traces/` 原始记录。
8. 只有 `status: PASSED` 且 `verified: true` 才可视为真实实验通过；dry-run 必须是 `PLANNED`。

Windows 或缺少 GNU Make/C 编译器时只运行：

```bash
python scripts/run_lab.py --dry-run --output-dir work/e3-dry-run
```

该模式只生成实验计划和 fixture-derived contract examples，不能作为 Linux 实验通过证明。
