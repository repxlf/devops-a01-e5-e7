# E3 A 组并行测试基线实施计划

> **For the implementer:** Follow this plan task by task. Keep every generated observation labeled as a mock fixture, a contract example, or real tool output.

**Goal:** 在不伪造课程项目实验结果的前提下，把 E3 A 组要求落成一个可运行、可替换、可追溯的 MD/RD 并行测试基线。

**Scope:** A 组的 MD/RD 项目、C0/C1/C2 版本样例、Linux/工具检查、构建命令记录、实际/声明依赖图、MISSING/REDUNDANT 证据和实验说明。不实现 B 组 DRAFT/MDFixer，不声称已经完成真实课程项目的 Linux 实验。

**Design:** 使用 `fixtures/e3/` 保存可替换的课程样例，使用 `src/a_group/e3/` 保存纯 Python 的解析、图构造、检测和证据逻辑，使用 `scripts/run_e3_lab.py` 负责真实命令记录。当前环境若缺少 Linux 工具，只运行结构和纯逻辑测试；真实证据由 Linux 上的脚本生成到 `evidence/linux-verified/`。

## Tasks

- [ ] 先写 E3 fixture、图构造、MD/RD 检测和命令记录的失败测试
- [ ] 增加 MD/RD 基线与 C0/C1/C2 文件快照，并写清预期观察
- [ ] 实现 BuildChecker E3 实验库：本地 include、Makefile prerequisites、图和证据
- [ ] 实现 E3 runner：环境检查、构建命令、观察记录、报告输出和 provenance 标记
- [ ] 增加 Docker/Linux 环境检查入口，不自动下载镜像或伪造验证结果
- [ ] 增加 E3 README、样例报告、运行清单、追溯和 AI 使用记录
- [ ] 运行失败测试、完整测试、契约校验和 diff 检查
- [ ] 提交到新分支，并尝试推送到远端
