# BuildChecker 服务（E4 骨架）

本仓库在 E4 中建立可重复环境，E5 起在 `services/buildchecker/` 中实现论文方法。

本次基于远端 `main` 的 `a913d27` 接入老师 2026-09-29 的 `E4实验包/A-buildchecker`。
模板的 Compose、锁文件、Makefile、环境检查、扫描器及服务测试保留原有行为。
Dockerfile 仅增加下述经用户确认的 Debian 普通软件源适配；基础镜像 digest 和安装内容不变。
其余整合调整目录说明、根 README 与忽略规则，没有修改 E2 共享契约。

## 当前分支与目录

E4 分支是 `feature/e4-environment`。合入 `main` 之前，组员必须显式克隆此分支：

```bash
mkdir -p ~/<学号>
cd ~/<学号>
git clone --branch feature/e4-environment https://git.nju.edu.cn/devops-a01/devops-a01/devops-a01.git buildchecker
cd buildchecker
git config --local user.name '<学号>'
git config --local user.email '<学号>@localhost'
git rev-parse HEAD
make doctor
make all
```

合入 `main` 后再统一从 `main` 克隆。共享服务器上使用 `--local` 身份，
不要在已有的他人目录重复克隆、覆盖文件或清理共享 Docker 缓存。

| 内容 | 本仓库位置 | 运行入口 |
|---|---|---|
| E4 服务、Dockerfile 与服务单测 | `services/buildchecker/` | 根目录 `make all` |
| E4 冒烟项目 | `fixtures/md-rd/` | `make smoke` 自动选用 |
| E2 契约与样例 | `schemas/`、`examples/` | `python3 scripts/validate.py` |
| E2/E3 既有 Python 模块 | `src/a_group/` | 保留原有导入路径 |
| E3 连续提交与 Linux 证据 | `fixtures/e3/`、`evidence/linux-verified/` | `scripts/run_lab.py` |
| E2/E3 回归测试 | 根目录 `tests/` | `python3 -m unittest discover -s tests -v` |

旧 `services/build-checker/` 只有说明文档，已迁移到 `services/buildchecker/README.md`。
`examples/build-checker/` 是契约样例目录，名称不变。不要批量替换其中的路径或 URI。
老师镜像没有安装 `src/a_group/`，`make test` 只执行容器内老师的服务单测。
因此 E4 的 `3 passed` 不表示根目录旧测试已经运行，整合时两套检查分别执行。

## 服务器准备与镜像核验

使用老师已初始化的 Ubuntu/Docker 环境。只在 Docker 尚未安装时，由组长检查
Ubuntu 22.04/24.04 后运行实验包的 `setup/bootstrap_ubuntu.sh` 一次。
该初始化脚本不属于服务运行目录，不需要组员重复执行。

```bash
docker version
docker compose version
docker buildx version
BASE_IMAGE=$(sed -n 's/^ARG BASE_IMAGE=//p' services/buildchecker/Dockerfile)
docker buildx imagetools inspect "$BASE_IMAGE"
```

核对模板固定 digest；x86_64 服务器对应 `linux/amd64`。初次构建需要下载镜像、
Debian 包和 Python 包，请错开首次构建，不要使用 `make -j all`。
A 组无需 API Key，`.env` 保持空值示例即可。

### 本组网络适配（与老师原版的差异）

2026-09-29 首次构建中，Debian 官方源下载 10.2 MB 索引用时约 12 分 32 秒，
平均 13.5 KB/s，后续还需下载约 87.8 MB 系统包。经用户确认，只在 Dockerfile
内把普通仓库 `http://deb.debian.org/debian` 改为
`https://mirrors.tuna.tsinghua.edu.cn/debian`。安全更新仓库保持上游地址，
避免改变安全更新来源；不修改宿主机 Ubuntu 软件源。

依据：[清华镜像站 Debian 使用说明](https://mirrors.tuna.tsinghua.edu.cn/help/debian/)。
只替换 DEB822 的对应 `URIs` 行，保留 `Suites`、`Components` 和 `Signed-By`，
不关闭 TLS、包签名或哈希校验。基础镜像 digest、Python 依赖锁文件、安装工具列表
和测试不变。实际系统包版本仍以本次 `toolchain.lock` 为准；老师模板没有将
apt 包版本固定到历史快照，不能仅凭基础镜像 digest 声称长期逐字节复现。

需恢复老师原源时，删除 Dockerfile 中这一条 `sed`，从 `RUN apt-get update` 开始，
统一提交后让组员重新构建；不要各自修改源而继续宣称测试的是同一源码 SHA。

## 证据与扫描器验证

`make all` 成功会打印本次证据目录。立即保存该目录和 `git rev-parse HEAD`，
不要在后续 `make scan` 之后把“最新目录”误当成完整运行证据。

| 文件 | 验收条件 |
|---|---|
| `env.json` | `problems` 为空，身份为自己的学号 |
| `build.log`、`image.json`、`toolchain.lock` | 构建成功，记录镜像和工具版本 |
| `test.log` | 老师服务原版为 `3 passed` |
| `smoke.json` | `make_exit_code` 为 0，`app_output` 为 `1`，`config_h_opened` 非空，`passed` 为 true |
| `secret-scan.txt` | 未发现问题 |

使用一个专用假值验证扫描器，以下只在自己的克隆执行，**不要提交测试文件**：

```bash
python3 -c "from pathlib import Path; p=Path('leak-demo.txt'); assert not p.exists(); p.write_text('api_key = ' + chr(34) + 'sk-' + 'demo1234567890abcdefghijk' + chr(34) + chr(10))"
git add leak-demo.txt
make scan
# 上一步应失败并检出假值，再清理刚创建的文件。
git rm --cached -q leak-demo.txt
rm leak-demo.txt
make scan
git ls-files .env
git status --short
```

清理后扫描应通过，`.env` 不应被跟踪。两次扫描各产生独立运行目录。
记录中说明测试由本人操作还是 AI 代理执行，不用代理重跑冒充第二名组员。

## 两人对照与 E5 接续

第二名组员在自己的学号目录克隆**同一提交**并运行 `make all`。各自记录
学号、克隆目录、完整源码 SHA、成功证据目录，然后比较 `toolchain.lock`、
`test.log` 和 `smoke.json` 的结论。允许耗时、PID 和跟踪行数不同。
可对两份工具清单执行 `diff -u`，差异需解释。

`work/` 默认忽略，E4 不要求每人提交运行记录。老师模板中的冒烟摘要会删除临时
原始 trace；E5 要在相同环境重新采集完整 `strace -ff` 与 `make -p`，
通过 `make shell` 把结果保存到容器的 `/app/work`。

`git remote -v` 应指向真正的本组远程仓库。课堂试跑所用的 `/root/E4实验包/A-buildchecker` 只是本地模板；从它克隆不会自动同步到课程平台。共享服务器上的学号目录与 Git 身份只隔离个人工作和标记未来的提交，运行 `make all` 本身不会产生 Git 提交。

## 命令

| 命令 | 作用 | 证据（work/<时间>/） |
| --- | --- | --- |
| `make doctor` | 服务器与 Git 身份自检 | env.json |
| `make build` | 构建服务镜像 | build.log、image.json、toolchain.lock |
| `make test` | 容器内运行单元测试 | test.log |
| `make smoke` | 用 E3 样例做冒烟测试 | smoke.json |
| `make scan` | 密钥检查（工作区、Git 历史、镜像） | secret-scan.txt |
| `make all` | 以上五步 | 同一个证据目录 |
| `make shell` | 进入服务容器；仓库的 `work/` 挂到容器的 `/app/work`，在那里保存的文件退出后仍保留 | — |
| `make lock` | 修改 requirements-dev.in 后重新生成锁文件 | requirements-dev.lock |

预期：`make test` 全部通过；`make smoke` 输出 `"passed": true`，strace 记录中能看到 `config.h` 被打开，`app_output` 为 `1`；`make scan` 显示"未发现问题"。

## 约定

- 基础镜像按 digest 固定，升级时只改 `services/buildchecker/Dockerfile` 的 `ARG BASE_IMAGE` 一行，并在提交说明中写明新 digest。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- 密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志。
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 和所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；E4 不要求个人创建分支、提交或合并。后续课程若要求提交原始证据，另按当时要求处理。
