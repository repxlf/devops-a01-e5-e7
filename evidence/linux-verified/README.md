# E3 Linux 实验原始证据

本目录保存 A01 在 Linux 环境实际执行 E3 A 组测试基线后的记录。此次归档由修正后的 runner 一次生成，`observations.json` 为 `status: PASSED`、`verified: true`，所有命令均为零退出码，日志中没有 `Clock skew detected`。

## 运行环境

| 项目 | 值 |
|---|---|
| 平台 | Linux x86_64（kernel 7.0.0-31-generic，glibc 2.43） |
| GNU Make | 4.4.1 |
| C 编译器 | gcc / cc 15.2.0 |
| strace | 6.19 |
| Python | 3.14.4 |
| Git | 2.53.0 |

完整机器记录见 `environment.json`。本次运行位置为 Linux 原生文件系统；runner 复制 fixture 时不继承源时间戳，避免 Windows 挂载或归档时间造成 clock-skew。

## 复现命令

```bash
python3 scripts/verify_docker.py
python3 scripts/run_lab.py --strace --output-dir work/e3-<new-timestamp>
```

输出目录必须尚不存在，避免新旧证据混合。非 Linux、必需工具缺失、行为与 oracle 不符或请求了但无法使用 strace 时，runner 返回非零退出码。

## 人工答案与实际观察

人工预期来自 `fixtures/e3/instructor-oracle.json`，标记为 `INSTRUCTOR_ORACLE`。项目源码是课程 fixture，标记为 `MOCK_FIXTURE`。本目录的环境、命令、构建输出、扫描器输出和 trace 是实际工具运行结果，标记为 `REAL_TOOL_OUTPUT`。

### MD/RD 故障项目

| 阶段 | 预期 | 实际 | 结果 |
|---|---:|---:|---|
| 初始 clean build | 1 | 1 | 通过 |
| 只把未声明的 `config.h` 从 1 改为 2 后增量构建 | 1 | 1 | 通过，复现旧产物 |
| 相同源码 clean build | 2 | 2 | 通过 |
| 只修改已声明但未使用的 `unused.h` 后增量构建 | 2，并重新编译 `main.o` | 2，且出现编译命令 | 通过，复现多余构建 |

扫描器得到一条 `MISSING main.o → config.h` 和一条 `REDUNDANT main.o → unused.h`，与 oracle 一致。

### C0/C1/C2 连续提交

| tag | SHA | 配置 | 增量输出 | clean 输出 | finding |
|---|---|---|---:|---:|---|
| C0 | `f5554c6ea70ca71da01755cf6a217176ecc968c7` | `cc-O0-MODE0` | 10 | 10 | 无 |
| C1 | `cde92752d5f313721b3ebacb962096667ebfffe1` | `cc-O0-MODE0` | 12 | 12 | `MISSING main.o → feature.h` |
| C2 | `d64348a3156817db3a3d28b4ba5703152d47d048` | `cc-O0-MODE7` | 12 | 19 | `MISSING main.o → feature.h` |

runner 同时保存 C1 与 C2 的 `make -n -B main.o` 输出并确认编译命令发生变化；三个提交均创建了同名 tag。

## 证据清单

| 路径 | 内容 | 数量 |
|---|---|---:|
| `environment.json` | 环境和工具版本 | 1 |
| `observations.json` | oracle 对照、行为结果和总状态 | 1 |
| `commands.json` | Git、构建、执行和文件变更的汇总记录 | 52 |
| `commands/commit-repository.json` | C0/C1/C2 Git、构建和命令快照子集 | 38 |
| `graphs/` | actual / declared 图 | 8 |
| `reports/` | MD / RD 报告 | 8 |
| `traces/` | `strace -e trace=%file,%process` 原始记录 | 61 |

`trace_summary` 统计到 12 条 `config.h` 记录和 3 条 `feature.h` 记录，可继续回溯到 `traces/` 文件。

## 边界

- E3 要求的是测试基线，不是 E5 BuildChecker 或 E8 EChecker 的完整实现。
- `ACTUAL` 图由范围受限的本地 C include 扫描器生成；`strace` 是独立保存的真实读取证据，当前代码没有声称从 trace 完成通用依赖推断。
- fixture 不是外部论文项目或生产项目。后续接入真实项目时需要重新运行并生成新的提交 SHA 和证据目录。
