# Git 可追溯性

本文件用于记录真实协作过程。当前仓库只记录框架生成阶段，不伪造课程项目的作者、Issue、PR 或实验结果。

## 仓库

| 仓库 | 用途 | 关系 |
|---|---|---|
| **`devops-a01`**（本仓库） | A 组工作库 | **共享契约的权威源** |
| `devops-final-product` | A01 / B01 共享契约库 | 镜像自本仓库 |
| `devops-b01` | B 组工作库 | — |

- Repository: `https://git.nju.edu.cn/devops-a01/devops-a01/devops-a01.git`
- Group: `A01`
- Paired group: `B01`
- Shared contract review: `devops-final-product` 分支 `b01xiugai`，提交 `23c0699`
- B01 work repository: `https://git.nju.edu.cn/devops-a01/devops-b01/dev.git`

## 契约同步规则

本仓库是共享契约的**权威源**。修改以下内容后，**必须同步到 `devops-final-product`**，保持逐字节一致：

```text
schemas/        统一 Job、请求、artifact、finding、依赖图
examples/       契约样例
scripts/        校验与 mock 流程
docs/           共同文档（ADR、API_CONTRACT、END_TO_END_FLOW、BACKLOG）
```

**不要只改共享库**——否则两边会分叉，联调时接口对不上。

同步后需在共享库提 Merge Request，由 B01 确认。

## 贡献记录

| 日期 | 作者 | Commit SHA | 变更 | 验证 | Issue/PR |
|---|---|---|---|---|---|
| 2026-09-20 | Tillthen | `98b9676` | A 组仓库框架（Schema、样例和实现骨架） | 初始校验脚本与单元测试 | 初始提交 |
| 2026-09-22 | 李然 / Ran Li | `4509706`、`d93a4d1`、`05fafc6` | 明确三仓关系、A01 契约权威源及同步规则 | 文档审阅 | 已合入 `main` |
| 2026-09-22 | Tillthen | `71d3715` | 完成 A 组 E2 契约包和四类任务样例 | 契约校验与单元测试 | `feature/e2-contract` |
| 2026-09-23 | 谢汶展（B01） | `23c0699` | 在共享仓库提出契约修订、反例和 18 项评审意见 | B01 校验脚本 9 项通过 | `devops-final-product:b01xiugai` |
| 2026-09-24 | Tillthen | `75a5529`～`0ba9075` | 批判性吸收 B01 评审，补强 Schema、样例、跨字段校验和端到端流程 | 契约校验 14 项、单元测试 24 项、mock flow 通过 | `feature/e2-contract`，MR 待创建 |
| 2026-09-24 | RepXlf | `cee6f08` | 将 A01 `main` 的契约权威源和三仓同步规则合入 E2 分支，补充 AI 判断与贡献追溯 | 契约校验 14 项、单元测试 24 项、mock flow 通过、`git diff --check` 通过 | `feature/e2-contract`，MR 待创建 |

最终合并 SHA 与 MR 链接只能在合并后填写，不在合并前虚构。

## 规则

- 每个功能变更使用清晰的 commit message。
- Schema 变更必须同步更新样例和校验结果。
- 真实实验必须记录输入提交、配置、工具版本和输出提交。
- 不使用虚构的 commit SHA、作者和验证结果。
- 每位组员的提交必须使用**真实姓名**（`git config user.name`），保证贡献可追溯。
