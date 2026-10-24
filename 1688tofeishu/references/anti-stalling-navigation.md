# 1688 移动端真机防死锁导航与手势规约 (Anti-Stalling Navigation Protocol)

> 📌 本文档归纳 1688 App 自动化巡检与聊天回访中最关键的防卡死、防误触、防错位手势与状态机规范。

---

## 1. 动态语义定位原则 (Dynamic Semantic Anchor)

### 痛点根源
- 1688 消息列表是典型的即时通信时间线，一旦商家回复，会话卡片瞬间置顶；
- 列表滚动存在弹性惯性，绝对物理坐标（如 `(500, 755)`）极其脆弱，极易误入非目标商家的会话。

### 规约标准
- **严禁写死物理坐标**；
- 每次检索前先 Dump UI 树（`adb shell uiautomator dump`）；
- 按商家关键字匹配 `node.attrib['text']`，提取 `bounds`；
- 计算中心坐标 `cx = (x1 + x2) // 2`, `cy = (y1 + y2) // 2`；
- 校验 `cy` 在合理可点击区间（`450 < cy < 2350`），避免误触顶部标题栏或底部 Tab。

---

## 2. 消息列表毫秒级安全复位 (Safe List Top Reset)

### 痛点根源
- 下划过多会滑入底部“为你推荐/猜你喜欢”商品流；
- 若盲目点击底部“消息”Tab 会激活刷新或误点商品。

### 规约标准
- 在屏幕中上部（y: 600 到 2200）连续执行 4 次快速向下滑动：
  ```bash
  adb shell input swipe 600 600 600 2200 150
  ```
- 每次滑动间隔 200ms，整体在 1 秒内无损干净回顶；
- 回顶后 `sleep 1.0` 确保惯性完全消除。

---

## 3. 聊天页安全回退状态机 (Safe Navigation State Machine)

### 痛点根源
- 进入 `CBUMessageChatActivity` 后，单次点击可能因动效未结束被吞噬；
- 盲目多次按返回键可能直接退出 1688 App 甚至退回 Android 桌面。

### 规约标准
- **返回触点**：左上角返回按钮固定坐标 `(67, 188)`（节点 bounds `[33,154][101,222]`）；
- **双保险循环**：
  1. 点击 `(67, 188)`，延迟 1.0 秒；
  2. 检查 `adb shell dumpsys window | grep mCurrentFocus`；
  3. 若仍在 `CBUMessageChatActivity`，则补发 `adb shell input keyevent 4`；
  4. 循环直到确认回到 `V5HomeActivity`，最多重试 4 次。

---

## 4. 弹窗守卫场景隔离 (Popup Guardian Scope)

### 痛点根源
- 退出店铺主页（Store Activity）时有“关注我们工厂吧”挽留弹窗，点击 `(423, 1681)` 释放；
- 但在消息列表或聊天详情界面，`(423, 1681)` 正好落在屏幕中央的消息卡片上，盲目调用会不断重开聊天导致死锁。

### 规约标准
- **严格限定生效场景**：仅在脱离 `Store Activity` 时允许点击 `(423, 1681)`；
- 消息列表与聊天详情页**绝对禁止**调用该坐标。

---

## 5. 防 CRLF 截屏二进制污染

### 规约标准
- 严禁在 macOS / Linux 管道中使用重定向：
  `❌ adb exec-out screencap -p > file.png`
- 强制使用真机落盘提取：
  `✅ adb shell screencap -p /sdcard/tmp.png && adb pull /sdcard/tmp.png target.png`
- 彻底避免 Leptonica 与 Tesseract 图像解析损坏。
