# 端到端流程

## 阶段

| 阶段 | 负责方 | 输入 | 输出 |
|---|---|---|---|
| DRAFT | B01 | 仓库、构建要求 | 镜像、环境、构建/验证日志 |
| FULL_CHECK | A01 | 固定提交、镜像、配置 | actual/declared graph、MD/RD、证据 |
| INCREMENTAL_CHECK | A01 | baseline、当前提交 | 更新图、全部 findings、新增/消除 findings |
| REPAIR | B01 | 与源码同 commit 的 MD 报告、目标文件、验证命令 | patch、PATCH_NOTES、构建/测试结果、候选决策 |
| CONSISTENCY_EVALUATION | A01 | 增量图与对应全量图 | 一致性、耗时和 findings 比较 |
| RECHECK | A01+B01 | 修复后的版本 | 接受或拒绝补丁的最终决定 |

REPAIR 的 `output.decision` 表示候选自身是否通过 B01 的验证；RECHECK 的决定表示补丁是否作为端到端结果被接受。

## 当前 mock 路径

```text
examples/draft/draft-success.json
    ↓
examples/e2-contract/full-check-success.json
    ↓
examples/e2-contract/incremental-check-success-c0-c1.json
    ↓
examples/repair/repair-result.json
    ↓
examples/e-checker/consistency-report-c1.json
    ↓
examples/end-to-end/recheck-result.json
```

## 后续真实流程

后续实现可以把每个 fixture 替换为真实工具输出，但必须保留：

- 完整 commit SHA
- configuration ID
- baseline 与当前提交的对应关系
- artifact URI 和生产 Job
- 报告与源码同源的校验
- 证据到文件、位置和提交的追溯关系
- REPAIR 候选决策与 RECHECK 最终决定的区分
