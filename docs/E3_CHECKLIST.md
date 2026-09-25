# E3 A 组检查清单

本清单把 `E3_并行测试基线_20260910.pptx` 中 A 组的要求映射到仓库文件。`MOCK_FIXTURE` 只表示仓库内构造的样例，`REAL_TOOL_OUTPUT` 只能由 Linux 实验实际生成，不能手工改标签。

| E3 要求 | 仓库位置 | 当前状态 |
|---|---|---|
| MD/RD 最小项目 | `fixtures/e3/md-rd/` | 已提供可替换 fixture |
| C0/C1/C2 连续提交样例 | `fixtures/e3/commits/C0/`、`C1/`、`C2/` | 已提供快照和预期值 |
| C0 正确初始版本 | `fixtures/e3/commits/C0/` | 预期 clean build 为 10 |
| C1 增加 `feature.h` include，Makefile 不变 | `fixtures/e3/commits/C1/` | 预期为 `MISSING main.o -> feature.h` |
| C2 只修改 `-DMODE=7` | `fixtures/e3/commits/C2/` | 普通增量构建预期 12，clean build 预期 19 |
| Linux 工具版本 | `scripts/verify_docker.py`、`work/<run>/environment.json` | 运行时记录，不伪造 |
| 实际/声明依赖图 | `src/a_group/e3/lab.py`、`work/<run>/graphs/` | fixture 解析器，预留真实采集器替换点 |
| `MISSING` / `REDUNDANT` | `src/a_group/e3/lab.py`、`work/<run>/reports/` | 有单元测试和证据字符串 |
| 命令、退出码、输出、耗时 | `scripts/run_lab.py`、`work/<run>/commands/` | 实际运行时保存 |
| 原始观察与预期结果分离 | `work/<run>/observations.json` | 预期来自 fixture，观察来自命令执行 |
| Linux 原始证据 | `evidence/linux-verified/` | 仅接受人工/CI 在 Linux 上生成的记录 |

## 推荐运行顺序

在要求的 Linux 环境中执行：

```bash
python3 scripts/verify_docker.py
python3 scripts/run_lab.py --strace --output-dir work/e3-<timestamp>
```

然后检查：

1. `environment.json` 是否包含系统、CPU 架构、GNU Make、C 编译器、Python 和可选 `strace` 版本。
2. `commands/` 是否保存了 `make clean`、`make`、可执行文件以及 C0/C1/C2 Git 操作的退出码和日志。
3. `graphs/` 是否同时有 actual 和 declared 图。
4. `reports/` 是否出现 MD/RD 报告，且 finding 能回溯到源文件、Makefile 行或构建命令。
5. C2 普通构建与 clean build 的输出是否分别为 12 和 19。
6. Linux 上若 `strace` 可用，检查 `traces/` 中的 `%file,%process` 记录，并确认 `config.h` 的读取记录与图中的 MISSING finding 对应。

Windows 或缺少 GNU Make/C 编译器时只运行：

```bash
python scripts/run_lab.py --dry-run --output-dir work/e3-dry-run
```

该模式只生成实验计划和 fixture-derived contract examples，不能作为 Linux 实验通过证明。
