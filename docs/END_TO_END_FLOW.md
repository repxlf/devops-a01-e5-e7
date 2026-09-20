# 端到端流程

## 阶段

| 阶段 | 负责方 | 输入 | 输出 |
|---|---|---|---|
| DRAFT | B01 | 仓库、构建要求 | 镜像、环境、日志 |
| FULL_CHECK | A01 | 固定提交、镜像、配置 | actual/declared graph、MD/RD、证据 |
| INCREMENTAL_CHECK | A01 | baseline、当前提交 | 更新图、新增/消除 findings |
| REPAIR | B01 | MD 报告、目标文件、验证命令 | patch、构建/测试/重检结果 |
| RECHECK | A01+B01 | 修复后的版本 | 接受或拒绝补丁 |

## 当前 mock 路径

```text
examples/end-to-end/scenario.json
    ↓
examples/e2-contract/full-check-success.json
    ↓
examples/build-checker/actual-graph-c0.json
    ↓
examples/e2-contract/incremental-check-success-c0-c1.json
    ↓
examples/e-checker/incremental-graph-c0-c1.json
    ↓
examples/repair/repair-result.json
    ↓
examples/e-checker/consistency-report-c1.json
```

## 后续真实流程

后续实现可以把每个 fixture 替换为真实工具输出，但必须保留：

- 完整 commit SHA
- configuration ID
- baseline 与当前提交的对应关系
- artifact URI 和生产 Job
- 证据到文件、位置和提交的追溯关系
