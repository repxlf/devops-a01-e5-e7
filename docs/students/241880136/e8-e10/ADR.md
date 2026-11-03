# 决策记录：删除必需头文件时拒绝复用旧图

## 背景与约束

EChecker 通过历史实际依赖图减少重复扫描，但复用必须以当前提交和配置仍能证明旧图有效为前提。删除一个实际包含的项目内头文件后，如果仍复用旧图，工具会把已无法构建的项目误报为一次成功检测。

## 选择与替代方案

选择：保留现有签名中的项目内 C/H 文件集合和预处理指令；删除 `config.h` 后要求签名变化、重新运行 GCC 依赖采集，并传播 `COMMAND_FAILED`。

未选择：

- 静默复用旧图：速度快但结果已经失真。
- 把失败转换成普通 MD：构建输入不存在属于采集失败，不是一次成功图比较中的 missing declaration。
- 仅检查 `main.c` 文本：无法覆盖头文件新增、删除和间接 include 变化。

## 代价与覆盖范围

保守刷新会增加小提交的扫描成本，但避免假成功。当前测试覆盖被源文件直接包含的项目内头文件删除；系统头、生成头、复杂隐式规则和更精确的目标级失效仍属于扩展范围。

## 验证命令与证据

```bash
docker run --rm --network none --user "$(id -u):$(id -g)" \
  -e HOME=/tmp -v "$PWD:/course" -w /course \
  course-e8e10:241880136 \
  python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v
```

结果：9 项测试通过；个人用例确认 `scan(project, previous)` 抛出包含 `COMMAND_FAILED` 的 `ValueError`。证据：`work/unit-tests-241880136-final-20261103-103003.log`。
