## 1. 新增視窗控制按鈕
- [x] 1.1 添加錨定按鈕（⚓）到右上角
- [x] 1.2 實現錨定功能：點擊後禁止拖動視窗，但保持其他交互行為正常
- [x] 1.3 添加隱藏按鈕（👁/🙈）到右上角
- [x] 1.4 實現隱藏功能：點擊後隱藏所有內容，只保留控制按鈕；再次點擊恢復顯示
- [x] 1.5 添加擊殺按鈕（⚔）到右上角
- [x] 1.6 實現擊殺模式：點擊後開啟擊殺模式，點擊魚類會觸發死亡動畫
- [x] 1.7 擊殺模式開啟時顯示提示視窗
- [x] 1.8 擊殺模式開啟時不執行餵食操作

## 2. 修復投食機清單重複問題
- [x] 2.1 在 `FeedSelectionDialog` 中添加 `existing_feeds` 集合
- [x] 2.2 避免重複添加 `CHEST_FEED_ITEMS`（金條、鑽石）

## 3. 修復打包後icon問題
- [x] 3.1 修改 `_get_app_icon()` 函數，支援打包後環境（使用 `sys._MEIPASS`）
- [x] 3.2 在 `aquarium_window.spec` 的 `datas` 中添加 `icon.ico` 和 `betta_icon.png`
- [x] 3.3 優先使用 `icon.ico`，如果不存在則使用 `betta_icon.png`
- [x] 3.4 為所有 QMessageBox 設置 icon

## 4. UI佈局調整
- [x] 4.1 將總金額UI從控制面板頂部移到底部（在關閉按鈕之前）
- [x] 4.2 將切換背景按鈕寬度設置為面板寬度的一半（減去左右邊距）

## 5. 事件處理
- [x] 5.1 更新視窗遮罩以包含控制按鈕區域
- [x] 5.2 處理控制按鈕的點擊事件（mousePressEvent/mouseMoveEvent/mouseReleaseEvent）
- [x] 5.3 在 AquariumWidget 中檢查錨定狀態，禁用拖動
