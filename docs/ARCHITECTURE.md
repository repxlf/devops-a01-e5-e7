# A 组架构边界

## 目标

仓库为 A 组的 BuildChecker、EChecker 和后续评估工作提供统一的契约、数据模型、适配器入口和测试位置。

## 分层

```text
contracts
    统一 Job、artifact、finding 和依赖图结构

adapters
    接入仓库、构建环境、artifact 存储和报告来源

build_checker
    固定提交上的全量检测流程

e_checker
    基于 baseline 的跨提交增量检测流程

evaluation
    正确性、一致性和耗时评估

workflow
    Job 状态和端到端阶段编排
```

## 关键边界

- BuildChecker 负责生成 actual graph、declared graph 和 MD/RD 报告。
- EChecker 负责消费历史图，更新当前图并计算新增/消除 findings。
- 正常分析发现写入 findings，不等同于 Job 执行失败。
- 环境失败、超时和分析器失败写入 `job.error`。
- 大文件通过 artifact URI 交接。
- 当前代码只提供可插拔接口和 mock 流程，不包含真实检测算法。
