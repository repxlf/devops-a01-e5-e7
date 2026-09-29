# ADR-006：E3 实验结果的来源标记

## 状态

Accepted for E3 baseline

## 背景

E3 同时要求预期结果和真实观察。仓库当前只能保证 fixture、解析器和测试结构，不能把本机 Windows 的静态样例写成 Linux 原始实验结果。

## 决策

1. 课程 fixture 使用 `MOCK_FIXTURE`；课件给出的人工预期集中保存于 `fixtures/e3/instructor-oracle.json`，并明确标为 `INSTRUCTOR_ORACLE`。该标记不扩展 E2 线上 artifact 契约的 provenance 枚举。
2. `scripts/run_lab.py` 只有在实际执行命令后才保存 stdout、stderr、退出码和耗时。
3. `scripts/verify_docker.py` 的工具版本是实际命令输出，因此标为 `REAL_TOOL_OUTPUT`；它只报告环境就绪情况，不下载镜像、不启动容器，也不宣称实验通过。
4. `evidence/linux-verified/` 只存放 Linux 环境生成且 `status: PASSED`、`verified: true` 的记录。dry-run 只能生成 `PLANNED` 计划，不能作为通过证明。
5. 真实运行拒绝复用输出目录，避免覆盖或混合证据；从 fixture 复制文件时不保留外部文件系统时间戳，避免 clock-skew 污染增量实验。
6. 真实课程项目接入后，应替换 `fixtures/e3/`，保留 C0/C1/C2 完整 SHA、工具版本、命令和输出，并把真实工具产生的 artifact 标记为 `REAL_TOOL_OUTPUT`。

## 后果

当前分支完成 E3 测试基线与真实 Linux 行为观察，但不声称完成 E5 的通用 BuildChecker 或 E8 的 EChecker。`ACTUAL` 图由范围受限的本地 include 扫描器生成，原始 `strace` 另行保存；二者不能混称为完整依赖推断。
