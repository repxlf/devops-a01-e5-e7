# E3 Linux 实验原始证据

本目录保存 **A01 组在 Linux 环境上实际执行 E3 实验后产生的记录**。

> 对应 `docs/E3_CHECKLIST.md` 中的条目：**「Linux 原始证据 —— 仅接受人工/CI 在 Linux 上生成的记录」**

所有文件均为工具实际输出，**未经手工修改**。`provenance` 字段统一为 `REAL_TOOL_OUTPUT`。

---

## 1. 运行环境

| 项目 | 值 |
|---|---|
| 平台 | Linux x86_64（WSL2，`Linux-5.10.16.3-microsoft-standard-WSL2`，glibc 2.35） |
| 发行版 | Ubuntu 22.04.1 LTS |
| GNU Make | 4.3 |
| C 编译器 | gcc / cc 11.4.0 (Ubuntu 11.4.0-1ubuntu1~22.04.3) |
| strace | 5.16 |
| Python | 3.10.12 |
| git | 2.34.1 |

完整快照见 [`environment.json`](environment.json)。

> 依据 E3 要求「系统调用跟踪使用 Linux 环境」，本实验在 WSL2 的 Linux 内核上执行，
> 并启用 `strace` 记录系统调用。

## 2. 复现命令

```bash
# 就绪检查（应输出 "ready": true）
python3 scripts/verify_docker.py

# 真实实验（带 strace 追踪）
python3 scripts/run_lab.py --strace --output-dir work/e3-linux-verified
```

无 Linux 环境时可只跑计划模式（**不产生真实执行记录**）：

```bash
python scripts/run_lab.py --dry-run --output-dir work/e3-dry-run
```

## 3. 预期值与实际结果

预期值来自 `fixtures/e3/commits/expected-observations.json`（E3 材料给定）。

### 3.1 C0 / C1 / C2 连续提交

| 提交 | SHA | 预期增量输出 | 实际 | 预期 clean 输出 | 实际 | 匹配 |
|---|---|---|---|---|---|---|
| **C0** | `948bd3bb259a6fb0e37b2036cf8144372070098f` | 10 | **10** | 10 | **10** | ✅ |
| **C1** | `318511d7bbe5ea779799835f4bc40ec2b340259a` | 12 | **12** | 12 | **12** | ✅ |
| **C2** | `025ce3991683af7850e9d997c844f4705eb2f312` | 12 | **12** | 19 | **19** | ✅ |

### 3.2 检出的依赖错误

| 提交 | 预期 finding | 实际 finding |
|---|---|---|
| C0 | 无 | 无 ✅ |
| C1 | `MISSING main.o → feature.h` | **一致** ✅ |
| C2 | `MISSING main.o → feature.h` | **一致** ✅ |

> **C1 的含义**：C1 在 `main.c` 中新增 `#include "feature.h"`，但**没有修改 Makefile**。
> 因此 Makefile 的声明依赖里缺少 `feature.h`，而实际编译会读取它 —— 这正是缺失依赖（MD）的定义。

### 3.3 MD / RD 样例项目（`fixtures/e3/md-rd/`）

| 预期 | 实际 |
|---|---|
| 1 条 `MISSING`（`main.o` 实际读 `config.h`，Makefile 未声明） | ✅ |
| 1 条 `REDUNDANT`（Makefile 声明 `unused.h`，`main.c` 未读） | ✅ |
| 合计 2 条 | **2 条** ✅ |

## 4. 关键证据：编译器确实读取了未声明的头文件

`C1` 的增量构建 `strace` 记录中出现：

```text
openat(AT_FDCWD, "feature.h", O_RDONLY|O_NOCTTY) = 4
```

而 `C0` 的构建记录中**完全没有** `feature.h`（符合预期 —— C0 未引入该头文件）。

**这条系统调用记录与图中的 `MISSING main.o → feature.h` finding 一一对应**，
证明该 finding 来自真实的文件读取行为，而非静态猜测。

## 5. 证据清单

| 路径 | 内容 | 数量 |
|---|---|---|
| `environment.json` | 运行环境与工具版本快照 | 1 |
| `observations.json` | 实验总览（预期 vs 实际、构建结果、findings） | 1 |
| `commands/commit-repository.json` | C0/C1/C2 的 git 操作、退出码与输出 | 19 条记录，**全部退出码 0** |
| `graphs/` | 实际依赖图与声明依赖图（actual / declared） | 8 |
| `reports/` | MD / RD 报告 | 8 |
| `traces/` | `strace -e trace=%file,%process` 系统调用记录 | 44 |

## 6. 边界声明

- 本实验的**项目源码为课程 fixture**（`fixtures/e3/`），不是某个上游仓库的真实副本。
  但 **make / gcc / git / strace 的执行与输出是真实的 Linux 工具产出**。
- 因此 `provenance` 标为 `REAL_TOOL_OUTPUT`，指的是**工具输出真实**；
  fixture 本身的可替换性见 `fixtures/e3/README.md`。
- 本实验验证的是 E3 基线的**可判断性**（预期值与实际值是否一致），
  **不构成 BuildChecker / EChecker 真实算法的完成证明**。
- E12 阶段将接入 B01 的真实数据，届时需重新执行并替换本目录内容。

## 7. 执行记录

| 日期 | 执行人 | 环境 | 命令 | 结果 |
|---|---|---|---|---|
| 2026-09-26 | 李然（A01） | WSL2 / Ubuntu 22.04 / GNU Make 4.3 / gcc 11.4.0 / strace 5.16 | `python3 scripts/run_lab.py --strace` | 全部预期值匹配，14 项契约校验与 28 项单元测试通过 |
