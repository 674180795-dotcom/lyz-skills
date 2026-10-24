# 真机防死锁与底层硬件守护规范 (Hardware Guardians)

本规范总结自 Redmi K60 Ultra（分辨率 1220×2712，Xiaomi HyperOS / Android 14）在 1688 App 实操中沉淀的高频物理陷阱防护与底层状态机工具。

---

## 📱 核心硬件参数与安全坐标系

- **设备型号**：Redmi K60 Ultra (`MBLVJZVCE6959PHU`)
- **屏幕分辨率**：`1220 × 2712`（物理 DPI ~466）
- **基准触点坐标表**：

| 功能 / 控件 | 坐标 (X, Y) | 说明 |
| :--- | :--- | :--- |
| **聊天详情左上角返回** | `(67, 188)` | 必须在软键盘收起后点击 |
| **1688 首页 Tab** | `(122, 2587)` | 底栏第 1 格 |
| **1688 消息/旺旺 Tab** | `(366, 2587)` | 底栏第 2 格（常驻未读消息红点） |
| **拍立淘相机禁区** | `(500~720, 2500~2660)` | ⚠️ **严禁点击！会强占全屏相机** |
| **店铺退出挽留弹窗** | `(423, 1681)` | 仅在退出店铺主页时点击“离开” |
| **聊天输入框常规中心** | `(400, 2600)` | 激活剪贴板粘贴前聚焦 |

---

## 🛡️ 四大高频物理陷阱与防护状态机

### 1. 软键盘事件拦截陷阱 (Keyboard IME Trap)
- ❌ **痛点**：
  当输入框激活、软键盘弹起时，直接点击左上角返回 `(67, 188)` 或下发 `KEYCODE_BACK`，事件会被输入法先行消费（仅收起键盘），导致未真正退出聊天详情页，引发后续状态错乱。
- ✅ **刚性规范**：
  退出聊天前必须调用 `NavigationGuardian.dismiss_keyboard_if_present()`：
  ```bash
  adb shell "dumpsys input_method | grep mInputShown=true"
  ```
  - 若包含 `mInputShown=true`：先执行一次 `adb shell input keyevent 4`（收起键盘）；
  - 键盘收起后再点击 `(67, 188)`；
  - 检查当前 Activity，若仍为 `CBUMessageChatActivity` 则补发一次 `KEYCODE_BACK`。

---

### 2. 拍立淘底栏相机误触死锁 (Camera Capture Trap)
- ❌ **痛点**：
  1688 首页底栏居中为“拍立淘”相机扫码功能（`CameraCaptureActivity`）。如果盲目点击底栏居中区域（如 `(610, 2580)`），系统会唤起全屏相机，导致后续 UI Automator 无法定位底栏且常规 BACK 极难脱离。
- ✅ **刚性规范**：
  - 严格锁定消息 Tab 为 `(366, 2587)`；
  - 绝对禁止在 `X: 500~720, Y: 2500~2660` 区间内下发任何点击指令。

---

### 3. 嵌套 WebView 与瀑布流深渊重置 (Launcher Activity Fast Reset)
- ❌ **痛点**：
  点击供应商黄页、企业资质或商品详情后，进入 UC 极速内核 WebView 或无限向下瀑布流，连续按返回键极易陷入挽留弹窗与历史栈循环。
- ✅ **刚性规范**：
  一旦检测到偏离主航道或需要快速回顶消息列表，直接调用秒级无损切回指令：
  ```bash
  adb shell am start -n com.alibaba.wireless/.launch.LauncherActivity
  ```
  在 1.2 秒内干净切回 1688 根节点，随后一键直达消息 Tab `(366, 2587)`，耗时比逐级返回缩短 80%，彻底杜绝死锁。

---

### 4. 1688 自定义聊天气泡无障碍盲区 (Accessibility Node Blindness)
- ❌ **痛点**：
  1688 旺旺聊天详情页的文字气泡（`LinearLayout`）多采用自定义 Canvas 或特殊 Spannable 绘制，UIAutomator XML Dump 下全部表现为 `text=''`、`label='None'`，无障碍层级完全盲目。
- ✅ **刚性规范**：
  弃用纯 XML 探测聊天正文，统一接入本地 Tesseract OCR 流水线：
  ```bash
  adb shell screencap -p /sdcard/chat_snap.png
  adb pull /sdcard/chat_snap.png ./chat_snap.png
  tesseract chat_snap.png stdout -l chi_sim --dpi 466
  ```
  - **避坑提示**：统一使用 `screencap -p` 存手机后再 `pull`，彻底规避 `adb exec-out` 在 macOS 管道下的换行符 CRLF 截断与 Leptonica 格式解析报错。

---

## 🖼️ 相册强占位与媒体库强刷规范 (DCIM Slot 0 Pinning)

为了让 1688 聊天界面的相册选择器（MediaPicker）第 1 格永远固定为我们要发送的目标效果图，执行以下两步刚性注入：

1. **推送到相册前置命名**：
   ```bash
   adb push /local/target_artwork.jpg /sdcard/DCIM/Camera/000_target_artwork.jpg
   ```
2. **广播媒体扫描器强刷新**：
   ```bash
   adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d file:///sdcard/DCIM/Camera/000_target_artwork.jpg
   ```
3. **调起相册发送**：
   此时在 1688 聊天框点击 `+` 号并打开相册，第 1 行第 1 列必定是 `000_target_artwork.jpg`，直接点击勾选框发送即可，耗时 < 1 秒。

---

## 🚫 店铺退出防挽留弹窗守护 (Popup Guardian)

- **场景**：离开店铺主页（Store Activity）时；
- **规范**：在 `400ms` 内点击 `(423, 1681)` 释放“关注我们工厂吧”挽留弹窗；
- ⚠️ **场景隔离边界**：
  点击 `(423, 1681)` **仅限离开店铺主页**；在消息列表或聊天详情界面（`CBUMessageChatActivity`）**严禁点击该坐标**（否则会误触列表中的消息卡片触发死循环）。
