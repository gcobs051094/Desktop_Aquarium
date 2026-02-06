## 1. 隱藏成長度數值顯示
- [x] 1.1 註解 `aquarium_window.py` 中繪製成長度文字的程式碼區塊（第376-410行）
- [x] 1.2 保留被註解的程式碼以便後續恢復使用

## 2. 飼料清單排序優化
- [x] 2.1 在 `aquarium_window.py` 中導入 `FEED_GROWTH_POINTS` from config
- [x] 2.2 修改 `_list_feeds()` 函數，按照 `FEED_GROWTH_POINTS` 字典的順序排序
- [x] 2.3 實作排序邏輯：在字典中的飼料按字典順序排序，不在字典中的飼料放在最後並按字母順序排序

## 3. 新增關閉按鈕
- [x] 3.1 在 `ControlPanel` 類別中新增 `close_requested` 信號
- [x] 3.2 在控制面板底部新增「關閉」按鈕（位於 `addStretch()` 之後）
- [x] 3.3 設定關閉按鈕樣式（紅色背景，hover 和 pressed 效果）
- [x] 3.4 連接按鈕點擊事件到 `close_requested` 信號

## 4. 實作關閉功能
- [x] 4.1 在 `TransparentAquariumWindow` 中連接 `close_requested` 信號到 `close_window` 方法
- [x] 4.2 實作 `close_window()` 方法，預留 TODO 註解供後續添加存檔機制
- [x] 4.3 在 `close_window()` 中調用 `self.close()` 和 `QApplication.instance().quit()` 確保應用程式完全退出
