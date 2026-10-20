# AI 使用记录

## 条目 2026-09-29：E4 老师模板与现有仓库整合

- 工具：Codex AI 编程助手。
- 用户授权：通过专用 SSH 密钥在 A01 服务器接入 E4，并提供学号 241880161 与提交邮箱。
- 依据：E4 A 组命令手册、E4 可重复工程环境 PPT、2026-09-29 实验包 A-buildchecker 模板。
- 实施方案：从最新 `main@a913d27` 开始，保留 E2 契约和 E3 基线/证据，统一 E4 服务入口到 `services/buildchecker/`。
- 模板来源：Dockerfile、Compose、Makefile、锁文件、CLI、服务测试、doctor 与扫描器来自老师实验包。此前 `services/build-checker/` 的说明迁入新服务目录；Python 内部包名保持不变。
- 用户追加确认：官方 Debian 索引下载约 13.5 KB/s，同意仅将容器内普通 Debian 仓库换为清华 HTTPS 镜像。Dockerfile 保留安全更新上游、基础 digest、签名配置、Python 锁文件及工具列表；原因与恢复方式见 `E4_README.md`。未修改宿主机软件源。
- 验证范围：根目录回归测试与 E4 服务测试分别检查。服务器真实构建、冒烟、扫描结果写入个人 `work/`，不以静态检查代替实际执行。
- 首轮实际结果：整合工作区 `work/20260929-140552/` 中 `make all` 成功；服务单测 3 项通过，烟测输出 `1` 且捕获 `config.h`，文件/历史/镜像扫描通过。另以该镜像只读挂载仓库运行根目录测试，33 项全部通过（无跳过），契约校验 14 项通过。假值暂存测试返回 1，移除后返回 0。此轮为提交前验证，正式个人运行另记录最终源码 SHA。
- 人工待办：检查整合结果，并由另一名组员在自己的目录独立重跑同一 SHA、填写对照结论。AI 代理运行不冒充第二名组员的个人实验。

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
