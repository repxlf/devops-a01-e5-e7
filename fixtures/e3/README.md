# E3 A 组实验 fixtures

本目录对应 E3 PPT 中 A 组的实验材料。它们是可替换的课程样例，不是课程仓库的真实副本。

```text
md-rd/                 一个同时包含 MD 和 RD 的最小 GNU Make 项目
commits/C0/            正确的初始依赖声明
commits/C1/            增加 feature.h include，但不修改 Makefile
commits/C2/            只修改 CFLAGS，加入 -DMODE=7
commits/expected...    预期 stdout、clean build 和 finding
instructor-oracle.json E3 课件给出的人工答案和判断依据
```

`md-rd/` 中的 `main.c` 读取 `config.h`，Makefile 声明了未使用的 `unused.h`，因此预期得到：

- `MISSING`: `main.o` 实际读取 `config.h`，但 Makefile 没有声明它
- `REDUNDANT`: Makefile 声明 `unused.h`，但 `main.c` 没有读取它

`commits/C0` 到 `C2` 用来观察连续提交：C0 输出 10，C1 输出 12 并新增 `feature.h` 缺失声明，C2 的普通增量构建仍保持 12，而 clean build 输出 19。

这些预期值来自 E3 材料。`instructor-oracle.json` 用 `INSTRUCTOR_ORACLE` 明确来源，fixture 自身保持 `MOCK_FIXTURE`，实际 Linux 命令和扫描器输出才使用 `REAL_TOOL_OUTPUT`。runner 会创建并标记 C0/C1/C2 的真实提交，同时记录 C1/C2 的 `make -n -B main.o` 命令快照；C2 的配置标识为 `cc-O0-MODE7`，不会沿用 C1 的 MODE0 标识。
