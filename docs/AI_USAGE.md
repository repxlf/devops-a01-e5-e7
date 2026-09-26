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

## Record 002：B01 契约评审与 E2 加固

### 工具/模型

AI 辅助编码代理；具体模型名称未记录在 Git 历史中。

### 任务

审阅 B01 在共享仓库 `devops-final-product` 的 `b01xiugai` 分支提交 `23c0699`，批判性吸收其中对 A01 E2 契约、反例和端到端流程的修改意见。

### AI 建议

- 强制成功 Job 携带 `output`，补齐四类请求的必要输入。
- 为 Artifact 增加 commit/configuration 元数据。
- 校验增量 baseline 与 REPAIR 报告的跨字段同源关系。
- 增加创建成功、请求拒绝和 REPAIR 候选拒绝样例。
- 将一致性评估与修复后的 RECHECK 分开。

### 人工判断

采纳 B01 对成功输出、Artifact 元数据、跨字段校验、反例和流程职责的意见；保留 `CANCELLED` 并定义取消接口，将声明风格说明建模为 `PATCH_NOTES`。

没有逐字照搬 B01 修改稿：MD 报告混入 `REDUNDANT` 被视为接线错误并拒绝，而不是静默忽略。E2 仍是契约和 mock 阶段，不扩展为真实服务或真实检测算法；契约允许在 E3 开发过程中继续版本化演进。

### 关联与验证

- B01 评审来源：`devops-final-product@23c0699`。
- A01 实施提交：`75a5529`～`0ba9075`。
- `python3 scripts/validate.py`：14 项通过。
- `python3 scripts/run_mock_flow.py`：6 个 mock 阶段通过。
- `python3 -m unittest discover -s tests -v`：24 项通过。
- 标准 Draft 2020-12 独立校验：4 个请求、8 个 Job、5 个依赖图、3 个报告及 2 个 HTTP 响应样例通过。
- `git diff --check`：通过。

上述结果只证明 E2 契约、样例和 mock 数据交接自洽，不表示 BuildChecker、EChecker、DRAFT 或 MDFixer 的真实算法已经完成。
## 条目 2026-09-26：EChecker 增量请求契约与反例拦截设计
- 记录人：张润弛
- 涉及模块/文件：`docs/BACKLOG.md`, `tests/test_negative_cases.py`
- AI 提出方案：
  - 建议当增量检测请求缺少 `baseline` 字段时，后台自动退化为全量检测（FULL_CHECK）以提高容错性。
- 人工分析与决策：
  - 拒绝自动退化方案：根据课程规范，增量任务必须能严格追溯基线提交与历史图（E2 / 12, E2 / 22），隐式退化会破坏下游审计追踪链。
  - 采纳强校验规则：缺少 `baseline` 或基线配置与当前提交不匹配时，API 层面直接返回 400 拒绝请求。
- 验证方式：
  - 补充反例用例断言，运行 `python -m unittest discover -s tests -v` 验证全部拦截通过。