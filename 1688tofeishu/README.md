# 1688tofeishu (1688 到飞书询盘比价管线)

自动化巡检 1688 移动端商家聊天记录，通过真机动态语义定位与本地 OCR 提取结构化报价，一键清洗并同步至**飞书多维表格（Bitable）**与**飞书云文档（Docx 移动端垂直卡片流）**。

---

## 🎯 核心解决痛点

1. **会话动态置顶错位**：商家回复消息后会话卡片瞬间跳到顶部，本技能使用 UIAutomator 动态语义寻址，彻底告别写死坐标的误触问题；
2. **列表滑动误触底栏**：执行中上部 4 连滑快速回顶（`reset_list_to_top`），杜绝滑入“为你推荐”商品流；
3. **聊天页退出死锁**：双保险安全回退状态机（左上角返回结合 `keyevent 4`，强校验当前 Activity 焦点）；
4. **截屏二进制损坏**：强制使用 `adb shell screencap -p /sdcard/xxx.png && adb pull`，彻底规避管道 CRLF 换行符破坏图片文件头；
5. **手机端阅读塌陷**：严格禁止 3 列以上宽表格，全面采用“垂直卡片流”，自动归档至「Antigravity 报告归档」文件夹。

---

## 📦 安装

### 推荐：通过 Skills 包管理器

```bash
npx -y skills add 674180795-dotcom/lyz-skills -g -a codex --skill 1688tofeishu -y
```

或使用 Bun：

```bash
bunx skills add 674180795-dotcom/lyz-skills -g -a codex --skill 1688tofeishu -y
```

### 手动安装（下载 ZIP）

下载 [独立 ZIP](dist/1688tofeishu.zip)，解压后将 `1688tofeishu/` 复制到你的 Agent Skills 目录：

```bash
unzip 1688tofeishu.zip
mkdir -p "$HOME/.gemini/config/skills"
cp -R 1688tofeishu "$HOME/.gemini/config/skills/1688tofeishu"
```

---

## 🚀 使用方式

在目标 Agent 中直接说：

```text
使用 $1688tofeishu 帮我抓取 1688 消息列表里刚才几家工厂的回复，并整理到飞书
```

或自然语言触发：
- *“抓取 1688 聊天记录并整理成飞书多维表格”*
- *“巡检 1688 工厂沟通，输出询盘比价报告”*

---

## 🛠️ 目录结构与资产

```text
1688tofeishu/
├── SKILL.md                          # 模型路由与标准执行流水线
├── README.md                         # 技能使用说明
├── agents/
│   └── interface.yaml                # 标准输入输出接口契约
├── references/
│   ├── anti-stalling-navigation.md   # 1688 真机防死锁导航与手势规约
│   └── feishu-schema-guidelines.md   # 飞书多维表格与移动端排版规约
├── scripts/
│   ├── conversation_harvester.py     # 真机动态定位、截屏与安全退出
│   ├── ocr_extractor.py              # 本地 OCR 与结构化报价抽取
│   └── feishu_deliverer.py           # 飞书 Bitable 入库与云文档发布
└── dist/
    └── 1688tofeishu.zip              # 离线发行包
```
