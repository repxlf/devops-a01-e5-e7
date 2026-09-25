# DevOps A01：依赖检测任务框架

这是 A 组面向完整任务流程的仓库框架。仓库从 E2 的接口契约开始，为后续 BuildChecker、EChecker、MD/RD 检测、连续提交分析和结果评估预留实现位置。

当前版本的目标不是声称真实检测器已经完成，而是把后续实现所需的边界、输入、输出、样例、测试和接入位置固定下来。

> 当前仓库中的 JSON、依赖图、报告、证据和流程结果均为 `MOCK_FIXTURE` 或 `CONTRACT_EXAMPLE`，除非文件明确说明已经接入真实工具。

## 1. 完整任务流程

```text
B 组 DRAFT
    │  环境、镜像、日志
    ▼
A 组 BuildChecker / FULL_CHECK
    │  实际图、声明图、MD/RD、证据
    ▼
A 组 EChecker / INCREMENTAL_CHECK
    │  baseline、增量图、新增/消除 findings
    ▼
B 组 MDFixer / REPAIR
    │  Patch、构建结果、验证结果
    ▼
重新构建、测试和检测（RECHECK）
    │
    ▼
接受或拒绝补丁
```

图片中列出的 A 组后续任务在本仓库中对应为：

1. 准备 MD/RD 项目和连续提交 `C0/C1/C2`
2. 复现 BuildChecker
3. 采集实际依赖图和声明依赖图
4. 检测 `MISSING` / `REDUNDANT`
5. 验证检测证据与结果正确性
6. 基于 BuildChecker 结果复现 EChecker
7. 增量更新依赖图，识别新增和消除错误
8. 比较增量与全量检测的一致性和耗时
9. 完成 BuildChecker → EChecker 联调

## 1.1 E3 A 组并行测试基线

E3 的 A 组实验入口是 `scripts/run_lab.py`，材料与结果目录如下：

```text
fixtures/e3/md-rd/                 MD/RD 最小 GNU Make 项目
fixtures/e3/commits/C0/            正确初始版本
fixtures/e3/commits/C1/            增加 feature.h include，Makefile 不变
fixtures/e3/commits/C2/            只增加 -DMODE=7
scripts/run_lab.py                 记录命令、退出码、输出和耗时
scripts/verify_docker.py           只检查环境，不下载或启动容器
work/<run>/                        单次运行目录，默认忽略
evidence/linux-verified/            Linux 原始证据目录，默认忽略
```

运行前先检查工具：

```bash
python3 scripts/verify_docker.py
python3 scripts/run_lab.py --strace --output-dir work/e3-<timestamp>
```

缺少 Linux/GNU Make/C 编译器时可以检查结构，但只能使用 dry-run：

```bash
python scripts/run_lab.py --dry-run --output-dir work/e3-dry-run
```

dry-run 和仓库静态样例都标记为 `MOCK_FIXTURE`。它们不能冒充 Linux 原始实验。完整映射见 `docs/E3_CHECKLIST.md`，来源标记决策见 `docs/ADR-006-e3-experiment-provenance.md`。

## 2. A 组服务边界

### BuildChecker

BuildChecker 面向固定提交和固定构建配置执行全量依赖检测。输入至少包括：

- 仓库地址和完整 commit SHA
- 可运行镜像
- `configuration_id`
- clean build 命令
- 项目根目录

输出包括：

- 实际依赖图
- 声明依赖图
- MD 报告
- RD 报告
- 进程、文件、声明位置和其他证据
- 可供下游读取的 artifact URI

### EChecker

EChecker 使用 BuildChecker 产生的历史依赖图作为 baseline，对后续提交执行增量检测。

增量任务必须能够追溯到：

- `base_commit`
- 当前 commit
- baseline actual graph
- baseline commit
- `configuration_id`

输出包括：

- 当前依赖图
- 当前 MD/RD findings
- 新增 findings
- 消除 findings
- 可供下一个提交继续使用的更新后依赖图

## 3. 目录说明

```text
schemas/       统一 Job、请求、报告、依赖图、finding 和 artifact 结构
src/a_group/   A 组后续实现的代码入口，包括 E3 实验纯逻辑
services/      A/B 四个服务角色的边界说明
fixtures/      C0/C1/C2、E3 项目、依赖图、报告和证据的 mock 数据
examples/      从 E2 契约到端到端流程以及 E3 预期结果的样例
tests/         契约、BuildChecker、EChecker、流程和评估测试
docs/          架构、接口、ADR、Backlog、AI 使用和 Git 追溯
scripts/       样例、报告校验、mock 流程和 E3 实验入口
```

代码实现边界如下：

```text
src/a_group/build_checker/
    全量构建、实际图/声明图采集、MD/RD 检测和证据生成

src/a_group/e_checker/
    baseline 检查、增量图更新、findings diff 和一致性比较

src/a_group/adapters/
    仓库、构建环境、artifact 存储和报告来源的真实工具适配器

src/a_group/evaluation/
    正确性验证、增量/全量比较和耗时统计

src/a_group/workflow/
    Job 状态、阶段编排和 BuildChecker → EChecker 端到端流程
```

## 4. 运行当前框架

本仓库不要求第三方运行时依赖。使用 Python 3.10 或更高版本。

### 校验契约和样例

```powershell
python scripts/validate.py
```

校验脚本会检查：

- 四类任务的合法请求和响应
- 成功 Job 必须有 output
- 缺失 baseline、环境、目标文件或报告同源关系
- baseline commit/configuration 不匹配
- artifact commit/configuration 元数据和 URI
- MD/RD/一致性报告结构
- 202 创建响应和 400 请求拒绝响应
- 系统错误、findings、REPAIR 候选拒绝的区分
- 端到端场景的阶段链路

### 运行 mock 流程

```powershell
python scripts/run_mock_flow.py
```

mock 流程只演示数据交接和阶段编排：

```text
C0 DRAFT
    ↓
C0 FULL_CHECK
    ↓
生成 baseline actual graph
    ↓
C1 INCREMENTAL_CHECK
    ↓
计算新增和消除 findings
    ↓
与 C1 FULL_CHECK 结果比较
    ↓
RECHECK 决定是否接受补丁
```

它不执行真实编译，不采集真实依赖图，也不实现依赖分析算法。

### 运行单元测试

```powershell
python -m unittest discover -s tests -v
```

## 5. E2 与后续实现的关系

```text
E2
├─ task.schema.json
├─ FULL_CHECK / INCREMENTAL_CHECK 样例
├─ Job 状态和错误约定
├─ artifact URI 约定
├─ MD/RD 报告样例
├─ ADR、Backlog、AI_USAGE
└─ 合法/非法输入验证

后续任务
├─ 准备 MD/RD 项目
├─ 准备 C0/C1/C2 连续提交
├─ 复现 BuildChecker
├─ 采集实际/声明依赖图
├─ 检测 MD/RD
├─ 验证检测证据与正确性
├─ 基于 BuildChecker 结果复现 EChecker
├─ 增量更新依赖图
├─ 识别新增/消除错误
└─ 比较增量与全量的一致性和耗时
```

E2 的契约位于 `schemas/`、`examples/e2-contract/`、`examples/build-checker/` 和 `docs/API_CONTRACT.md`。其中 `report.schema.json`、`job-created-response.schema.json` 和 `request-rejected-response.schema.json` 分别约束报告、异步创建响应和请求拒绝响应。后续实现应消费这些契约，而不是重新发明一套输入输出格式。

E2 要求到文件和验证命令的逐项对应关系见 `docs/E2_CHECKLIST.md`。

## 6. 接入真实实现的顺序

1. 将 `fixtures/projects/md-rd-project/` 替换为实际 MD/RD 项目。
2. 准备真实的 `C0`、`C1`、`C2` 提交并记录完整 SHA。
3. 在 `src/a_group/adapters/repository.py` 接入仓库读取。
4. 在 `src/a_group/adapters/build_environment.py` 接入构建环境和构建命令。
5. 在 `src/a_group/build_checker/graph_collection.py` 接入实际依赖图采集器。
6. 在 `src/a_group/build_checker/md_rd_detection.py` 实现 MD/RD 检测。
7. 在 `src/a_group/build_checker/evidence.py` 生成可追溯证据。
8. 在 `src/a_group/e_checker/incremental_update.py` 实现增量图更新。
9. 在 `src/a_group/e_checker/finding_diff.py` 计算新增和消除错误。
10. 在 `src/a_group/evaluation/` 比较增量与全量结果及耗时。

如果字段需要变化，应先更新 Schema、ADR、样例和下游验证，再修改实现。

## 7. 错误与 findings 的区别

正常分析发现问题时，任务可以仍然是 `SUCCEEDED`：

```json
{
  "status": "SUCCEEDED",
  "output": {
    "findings": [
      {
        "type": "MISSING",
        "target": "main.o",
        "dependency": "config.h"
      }
    ]
  },
  "error": null
}
```

工具没有正常完成时，才写入 `job.error`，例如：

```text
ENV_3002       镜像构建失败
EXEC_4002      任务超时
ANALYSIS_5001  分析器失败
```

`MISSING` 表示实际需要但声明缺失，`REDUNDANT` 表示声明存在但当前配置未使用。

## 8. 当前版本边界

当前框架不包含：

- 真实 BuildChecker 服务
- 真实 EChecker 服务
- 真实 MDFixer 服务
- 特定语言或编译器的依赖分析算法
- Docker 服务部署
- 真实仓库、镜像、作者、commit 或 PR 信息

所有未接入真实工具的结果必须标记为 `MOCK_FIXTURE` 或 `CONTRACT_EXAMPLE`。

## 9. 贡献与追溯

每次修改至少应同步检查：

- Schema 是否需要更新
- 请求/响应样例是否仍然有效
- 下游 artifact 是否仍然可读取
- `docs/BACKLOG.md` 是否需要更新
- `docs/AI_USAGE.md` 是否需要记录 AI 建议和人工判断
- `docs/GIT_TRACEABILITY.md` 是否记录作者、commit、Issue 或 PR

不要在文档中伪造真实 commit SHA、作者或验证结果。没有真实数据时，使用明确占位符并标注待补充。
