# 安装与兼容性

本页解决的是“怎样把 Skill 放到目标产品能读取的位置”，不是简历运行流程。优先使用标准 CLI；CLI 因代理、沙箱或网络失败时，改用仓库 ZIP 手动复制，不必反复重试同一条命令。

## 路径选择

| 场景 | 推荐方式 |
| --- | --- |
| 已安装 Node.js，可正常访问 npm 与 GitHub | `npx` 安装 |
| 已安装 Bun，且 registry/代理配置可用 | `bunx` 安装 |
| `npx`/`bunx` 缓存写入被宿主沙箱拦截 | 下载 ZIP 后手动复制 |
| GitHub clone/tarball 经常中断 | 下载仓库内已打包的小型 ZIP |
| 豆包、WorkBuddy 或未被 CLI 列出的 Agent 平台 | 按产品显示的用户 Skill 目录手动复制 |

## 标准安装

推荐使用 Node.js 随附的 `npx`：

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

使用 Bun：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

先查看仓库中可安装的 Skill：

```bash
npx -y skills add 674180795-dotcom/lyz-skills --list
```

只想下载已经发布的包，也可以让 CLI 读取 ZIP URL：

```bash
npx -y skills add https://github.com/674180795-dotcom/lyz-skills/raw/main/lyz-resume/dist/lyz-resume.zip -g -a codex -y
```

`-g` 表示安装到用户范围，`-a codex` 选择 Codex 目标，`--skill lyz-resume` 只安装这一项，`-y` 跳过交互确认。若目标产品不是 Codex，不要机械照抄 `-a codex`；先用 CLI 的目标列表确认是否原生支持，否则走手动复制。

## ZIP 手动安装

下载：

```text
https://github.com/674180795-dotcom/lyz-skills/raw/main/lyz-resume/dist/lyz-resume.zip
```

解压后应得到一个顶层 `lyz-resume/` 目录，且其内部直接包含 `SKILL.md`。不要形成 `lyz-resume/lyz-resume/SKILL.md` 的双重嵌套。

macOS / Linux，安装到通用用户 Skill 目录：

```bash
unzip lyz-resume.zip
mkdir -p "$HOME/.agents/skills"
cp -R lyz-resume "$HOME/.agents/skills/lyz-resume"
```

Windows PowerShell：

```powershell
Expand-Archive .\lyz-resume.zip -DestinationPath .\lyz-resume-package
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\lyz-resume-package\lyz-resume" "$env:USERPROFILE\.agents\skills\lyz-resume"
```

豆包、WorkBuddy 或其他平台不要猜目录：在产品设置、开发者文档或 Skill 管理页确认“用户 Skill 目录”，把完整的 `lyz-resume/` 复制进去，再刷新 Skill 列表或重启产品。若该产品不读取 Agent Skills 格式，手动复制也不会自动获得兼容性。

当前仓库对豆包和 WorkBuddy 的声明是“平台无关源文件可手动复制”，不是官方安装器、宿主权限或完整运行链路的原生认证。`target_platforms` 只列已经生成适配证据的目标，避免把一次成功复制误报成平台级支持。

## 代理 407 与 Bun registry

如果报错 URL 是 `registry.npmmirror.com`，状态为 `407 Proxy Authentication Required`，而直连该域名正常，通常是代理拒绝了该 registry，不是 Skill 包损坏。

组织策略允许时，可以把该域名加入 `NO_PROXY`/`no_proxy` 后重试。也可以明确让 Bun 使用 npm 官方 registry。

macOS / Linux 单次命令：

```bash
BUN_CONFIG_REGISTRY=https://registry.npmjs.org bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

Windows PowerShell：

```powershell
$env:BUN_CONFIG_REGISTRY="https://registry.npmjs.org"
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill lyz-resume -y
```

或在 Bun 配置文件中设置：

```toml
[install]
registry = "https://registry.npmjs.org"
```

不要把 `npm_config_registry` 当作 Bun 的可靠覆盖方式；对 Bun 使用其官方 `BUN_CONFIG_REGISTRY` 或 `bunfig.toml` 配置。修改代理白名单前应遵守所在组织的网络策略。

## 沙箱误拦截与空白 SIGTERM

`npx` 和 `bunx` 会写入各自的包缓存。某些桌面 Agent 的沙箱会把缓存清理或临时目录变更误判为批量删除；这属于宿主/安装器行为，Skill 仓库无法从包内修复。可行路径是：

1. 记录完整命令、退出码、首个失败 URL 与宿主拦截提示；
2. 若宿主允许，授权对应的 npm/Bun 缓存操作；
3. 不允许授权时，直接改用 ZIP 手动安装；
4. `SIGTERM` 且 stdout/stderr 为空时，不要据此判断 Skill 有错，应同时排查宿主沙箱、代理和 GitHub TLS 连接。

## 运行依赖

访谈、事实整理与 HTML 生成只要求 Python 3.10+ 标准库。PDF 相关流程还需要本地可执行文件：

- Chrome 或 Chromium：把 HTML 打印为 PDF；
- Poppler：`pdfinfo`、`pdftotext`、`pdftoppm`，用于页数、文本提取与逐页图片验收。

依赖缺失时仍可完成内容与 HTML，不应伪装成 PDF 已经验证通过。

## 安装后检查

至少确认：

```text
<用户 Skill 目录>/lyz-resume/SKILL.md
<用户 Skill 目录>/lyz-resume/scripts/render_resume.py
<用户 Skill 目录>/lyz-resume/assets/resume-data.schema.json
```

并检查 `SKILL.md` 头部的 `name` 为 `lyz-resume`。然后在目标产品中新建会话，明确调用 `$lyz-resume`，用“我没有现成简历，请从零采访我”做一次最小触发验证。

若安装器只显示复制到了另一个产品目录，那只是目标选择不对，不代表此 Skill 本身安装失败；应更换目标或按目标产品的用户 Skill 目录手动复制。
