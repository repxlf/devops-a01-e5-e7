# EChecker service boundary

A 组负责的跨提交增量依赖检测服务。未来实现应消费 BuildChecker 产生的 baseline，并提供增量图、新增 findings、消除 findings 和一致性结果。

当前目录只记录服务边界，不包含真实增量算法。
