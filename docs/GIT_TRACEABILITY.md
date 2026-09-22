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
| 2026-09-22 | 李然 | `98b9676` | A 组仓库框架（schema、样例、实现骨架） | `python scripts/validate.py`（7 项通过） | — |
| | | | | | |

> 新记录请追加到上表。Commit SHA 用 `git log --oneline -1` 获取。

## 规则

- 每个功能变更使用清晰的 commit message。
- Schema 变更必须同步更新样例和校验结果。
- 真实实验必须记录输入提交、配置、工具版本和输出提交。
- 不使用虚构的 commit SHA、作者和验证结果。
- 每位组员的提交必须使用**真实姓名**（`git config user.name`），保证贡献可追溯。
