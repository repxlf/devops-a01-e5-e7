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
