# BuildChecker service boundary

A 组负责的全量依赖检测服务。未来实现应组合 `src/a_group/build_checker/` 中的 graph collector、MD/RD detector 和 evidence provider。

E4 起，本目录统一采用老师模板的 `services/buildchecker/` 路径。
Dockerfile、CLI、pytest 和冒烟测试均在此目录；从仓库根目录执行 `make all`。
原目录 `services/build-checker/` 的说明已合并到这里。

现有 `src/a_group/build_checker/` 是 Python 内部模块，保留原有名称和导入路径。
老师的 E4 镜像目前只复制本目录与 `fixtures/`，不会自动安装 `src/a_group/`。
E5/E6 接入算法时再显式安装或复制所需模块。

当前 CLI 只提供 `version` 和 `smoke`，完整 MD/RD 检测和 HTTP 服务仍待后续实现。
详细命令见仓库根目录 `E4_README.md`。
