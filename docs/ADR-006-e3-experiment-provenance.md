# ADR-006：E3 实验结果的来源标记

## 状态

Accepted for E3 scaffold

## 背景

E3 同时要求预期结果和真实观察。仓库当前只能保证 fixture、解析器和测试结构，不能把本机 Windows 的静态样例写成 Linux 原始实验结果。

## 决策

1. 提交到仓库的 E3 fixture、预期 finding 和预期 stdout 使用 `MOCK_FIXTURE`。
2. `scripts/run_lab.py` 只有在实际执行命令后才保存 stdout、stderr、退出码和耗时。
3. `scripts/verify_docker.py` 只报告环境就绪情况，不下载镜像、不启动容器、不宣称实验通过。
4. `evidence/linux-verified/` 只存放要求的 Linux 环境生成的原始记录；运行脚本不能把 dry-run 结果写入该目录。
5. 真实课程项目接入后，应替换 `fixtures/e3/`，保留 C0/C1/C2 完整 SHA、工具版本、命令和输出，并把真实工具产生的 artifact 标记为 `REAL_TOOL_OUTPUT`。

## 后果

当前分支可以检查接口和实验逻辑，但不会伪造课程项目的作者、提交 SHA、Linux 路径、Docker ID 或检测成功结论。真实 BuildChecker 采集器仍通过既有 adapter 接口接入。
