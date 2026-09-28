# AI 使用记录

## Record 001：仓库框架设计

### 工具/模型

ChatGPT / Codex

### 任务

根据 E2 需求与接口契约材料，以及 A 组后续任务截图，设计完整 A 组仓库框架。

### AI 建议

- 用统一 Job 模型承载四类耗时任务。
- 用 `FULL_CHECK` 和 `INCREMENTAL_CHECK` 表达 A 组两个核心服务。
- 用 artifact URI 传递依赖图、报告和证据。
- 为 C0/C1/C2、BuildChecker、EChecker 和一致性评估预留模块。

### 人工判断

采纳：

- E2 契约作为后续实现基础。
- BuildChecker 和 EChecker 分开建模。
- mock fixture 与真实实现明确分离。

保留待协商：

- 真实 MD/RD 项目和构建工具。
- A01/B01 的正式字段名和 artifact 存储方式。
- EChecker 的具体增量算法。

### 验证

当前通过 JSON 样例、校验脚本和 mock flow 验证结构与数据交接。真实算法接入后，需要补充实验结果和代码版本。

## Record 002：E3 A 组实验基线

### 工具/模型

ChatGPT / Codex

### 任务

根据 `E3_并行测试基线_20260910.pptx` 为 A 组建立 MD/RD 项目、C0/C1/C2 快照、命令观察和 finding 证据框架。

### AI 建议

- 用最小 C/Make 项目明确区分实际 include 与 Makefile prerequisites。
- 用 C0/C1/C2 保留普通增量构建与 clean build 的对比位置。
- 保存环境、命令、退出码、输出和耗时，并把预期值与实际值分开。

### 人工判断

采纳：

- 将 E3 A 组范围限定为 PPT 中的 MD/RD、BuildChecker 观察和连续提交实验。
- 将静态样例和 dry-run 统一标为 `MOCK_FIXTURE`。
- 只预留真实 Linux/BuildChecker 适配点，不虚构课程项目 SHA、Docker ID 或 Linux 结果。

未在本次任务中实现：

- B 组 DRAFT、MDFixer 和 Docker 镜像构建。
- 特定真实课程项目的依赖采集算法。
- 未获得远端新 main 时的 B 组分支修改。

## Record 003：E3 完整性复核与 Linux 重跑

### 工具/模型

ChatGPT / Codex

### 任务

逐页对照 E3 课件，复核 `feature/e3-linux-evidence` 的实现与归档证据，补齐遗漏后重新运行。

### AI 建议与人工判断

- 补做 MD 旧产物、clean build 和 RD 多余重编译三个行为步骤。
- 将课件人工答案与 fixture、真实工具输出分开标记。
- 创建 C0/C1/C2 tags，记录完整 SHA 和 C1/C2 编译命令快照。
- C2 使用 MODE7 配置标识；任何预期不匹配均使 runner 非零退出。
- 真实运行限制为 Linux，并拒绝复用输出目录或静默忽略缺失的 strace。
- 在 Linux 原生文件系统重新生成证据，排除原 WSL `/mnt/d` 日志中的 clock-skew。

以上均采纳；未扩大到 E5 BuildChecker、E8 EChecker 或 B 组任务。
