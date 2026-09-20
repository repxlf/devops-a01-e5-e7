# BuildChecker service boundary

A 组负责的全量依赖检测服务。未来实现应组合 `src/a_group/build_checker/` 中的 graph collector、MD/RD detector 和 evidence provider。

当前目录只记录服务边界，不包含真实检测算法或 HTTP 服务。
