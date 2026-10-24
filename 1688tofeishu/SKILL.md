---
name: 1688tofeishu
description: MUST USE when the user wants to inspect, scrape, extract, or catalog 1688 mobile app merchant chat records (1688 聊天记录 / 抓取工厂沟通 / 询盘比价 / 回访供应商 / 整理1688报价 / 消息页面抓取), parse structured quotes (大货单价、打样费、包装背卡费、税点、交期保障), and deliver comparison results into Feishu Bitable (多维表格) and mobile-first Feishu Docx (飞书云文档垂直卡片流). Uses dynamic semantic anchoring, safe navigation state machines, and auto-archiving to 「Antigravity 报告归档」.
---

# 1688 供应商询盘抓取与飞书比价交付技能 (1688tofeishu)

本技能专用于自动化巡检 1688 移动端（Android ADB 真机），动态检索目标工厂/商家的真实聊天记录，通过三段全景截屏与本地 OCR 提取沟通文本，解析全维度报价矩阵，并自动同步至**飞书多维表格（Bitable）**与**飞书云文档（Docx 移动端垂直卡片流）**。

---

## 🎯 核心解决痛点

1. **会话动态置顶错位**：商家回复消息后会话卡片瞬间置顶，本技能使用 UIAutomator 动态语义寻址（`find_factory_bounds`），彻底抛弃脆弱的静态坐标；
2. **列表滑动误触底栏**：自动执行中上部 4 连滑快速回顶（`reset_list_to_top`），杜绝滑入“为你推荐”商品流；
3. **聊天页退出死锁**：双保险安全回退状态机（左上角 `(67, 188)` 结合 `keyevent 4`，强校验 `V5HomeActivity`）；
4. **截屏二进制损坏**：强制使用 `adb shell screencap -p /sdcard/xxx.png && adb pull`，彻底规避管道 CRLF 换行符破坏图片文件头；
5. **手机端阅读塌陷**：严格禁止 3 列以上宽表格，全面采用“垂直卡片流”，自动归档至「Antigravity 报告归档」文件夹。

---

## 🛠️ 资产与脚本工具集

- **真机导航与抓取**：[`scripts/conversation_harvester.py`](scripts/conversation_harvester.py)
  - 动态语义锚点定位、快速回顶、三段全景截图（底端最新、中段报价、顶部原诉求）、安全回退。
- **本地 OCR 与报价解析**：[`scripts/ocr_extractor.py`](scripts/ocr_extractor.py)
  - 本地 Tesseract 466 DPI 解析、过滤 1688 界面噪音、正则提取大货价、打样费、包材、税点、交期。
- **飞书交付套件**：[`scripts/feishu_deliverer.py`](scripts/feishu_deliverer.py)
  - 自动读取 `~/.feishu_config.json`，多维表格自动建表入库、生成垂直卡片流报告并调用 `feishu-doc --clean` 发布。
- **参考规约**：
  - [防死锁导航规约](references/anti-stalling-navigation.md)
  - [飞书多维表格与移动端排版规约](references/feishu-schema-guidelines.md)

---

## 📋 标准执行流水线 (Standard Workflow)

### Step 01 · 目标锁定与环境校验
1. 校验 ADB 设备在线状态：`adb devices`；
2. 确认 1688 处于前台主界面或消息列表：`adb shell dumpsys window | grep mCurrentFocus`；
3. 明确需抓取的工厂全称或关键词列表。

### Step 02 · 动态语义巡检与三段抓取
调用 `ConversationHarvester` 执行批量巡检：
1. 每次定位前调用 `reset_list_to_top()` 安全复位；
2. Dump UI 树并计算目标文本中心坐标 `(cx, cy)`；
3. 点击进入 `CBUMessageChatActivity`；
4. 顺序捕获：`_bot.png`（最新消息）➔ 上滑 1000px 捕获 `_mid.png`（核心报价）➔ 再上滑 1000px 捕获 `_top.png`（初始询盘）；
5. 调用 `exit_chat_safely()` 确认脱离聊天页并返回 `V5HomeActivity`。

### Step 03 · 本地 OCR 提取与结构化解析
1. 对所有截屏执行本地 Tesseract OCR 解析；
2. 过滤系统干扰词（“发订单”、“发商品”、“AI查企”等）；
3. 结构化抽取 8 大核心维度：
   - `对接状态`（详细报价 / 部分报价 / 未报价 / 超时未回）
   - `工艺方案建议`（数码印+绣边 / 织唛 / 平织）
   - `打样/版费`（是否退样费、周期天数）
   - `大货单价(1000套)`
   - `背卡与包装费`（分拆报 vs 合并报）
   - `普票/专票税点`（+1% ~ +13%）
   - `11.15能否发货`（可以满足 / 需尽快定样 / 无法满足）
   - `综合推荐评级`（⭐⭐⭐⭐⭐ / ⭐⭐⭐⭐ / ⭐⭐⭐ / ❌）

### Step 04 · 飞书双资产交付与对话极简闭环
1. **多维表格 (Bitable)**：
   - 调用 `FeishuDeliverer.push_bitable_records` 写入 Base，严禁技术噪音字段；
2. **云文档 (Docx)**：
   - 撰写包含一句话结论、四大梯队卡片流、工艺对比与采买步进的 Markdown；
   - 调用 `FeishuDeliverer.publish_docx_report` 发布，自动归档至「Antigravity 报告归档」文件夹；
3. **对话框极简响应**：
   - 仅输出 200 字以内核心摘要与双直达链接（Base 直达 + Docx 直达）。
