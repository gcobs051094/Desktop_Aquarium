# Change: 新增視窗控制按鈕與UI修復

## Why
1. **視窗控制需求**：使用者需要能夠錨定視窗（防止拖動）、隱藏視窗內容（只保留控制按鈕）、以及擊殺魚類的功能
2. **投食機清單重複問題**：投食機的飼料清單會出現重複的鑽石和金條，因為 `_list_feeds()` 已經包含了它們，然後代碼又再次添加
3. **打包後icon缺失**：打包後的exe中，彈出視窗的左上角icon無法顯示，因為icon文件沒有被打包到數據文件中
4. **UI佈局優化**：總金額UI與控制按鈕在同一列，影響視覺效果；切換背景按鈕寬度過寬

## What Changes
- **新增右上角控制按鈕**：
  - 錨定按鈕（⚓）：點擊後禁止拖動視窗，但保持其他交互行為正常
  - 隱藏按鈕（👁/🙈）：點擊後隱藏所有內容，只保留控制按鈕；再次點擊恢復顯示
  - 擊殺按鈕（⚔）：點擊後開啟擊殺模式，點擊魚類會觸發死亡動畫；擊殺模式開啟時不執行餵食操作
- **修復投食機清單重複問題**：
  - 在 `FeedSelectionDialog` 中添加 `existing_feeds` 集合來記錄已經在 `feed_list` 中的飼料名稱
  - 避免重複添加 `CHEST_FEED_ITEMS`（金條、鑽石）
- **修復打包後icon問題**：
  - 修改 `_get_app_icon()` 函數，支援打包後環境（使用 `sys._MEIPASS`）
  - 在 `aquarium_window.spec` 的 `datas` 中添加 `icon.ico` 和 `betta_icon.png`
  - 優先使用 `icon.ico`，如果不存在則使用 `betta_icon.png`
- **UI佈局調整**：
  - 將總金額UI從控制面板頂部移到底部（在關閉按鈕之前），避免與右上角按鈕在同一列
  - 將切換背景按鈕寬度設置為面板寬度的一半（減去左右邊距）

## Impact
- Affected specs: aquarium-ui
- Affected code:
  - `aquarium_window.py`：
    - `TransparentAquariumWindow.__init__`：新增控制按鈕和狀態變量
    - `TransparentAquariumWindow._toggle_anchor`：實現錨定功能
    - `TransparentAquariumWindow._toggle_hide`：實現隱藏功能
    - `TransparentAquariumWindow._toggle_kill_mode`：實現擊殺模式
    - `TransparentAquariumWindow._update_button_positions`：更新按鈕位置
    - `TransparentAquariumWindow.updateWindowMask`：更新視窗遮罩以包含控制按鈕
    - `TransparentAquariumWindow.mousePressEvent/mouseMoveEvent/mouseReleaseEvent`：處理控制按鈕的點擊事件
    - `TransparentAquariumWindow.on_aquarium_clicked`：添加擊殺模式檢查
    - `AquariumWidget.mousePressEvent/mouseMoveEvent`：檢查錨定狀態，禁用拖動
    - `ControlPanel.__init__`：調整總金額UI位置和切換背景按鈕寬度
    - `FeedSelectionDialog.__init__`：修復重複添加飼料問題
    - `_get_app_icon`：支援打包後環境
  - `aquarium_window.spec`：添加icon文件到datas
