# Change: 改進水族箱 UI 控制功能

## Why
為了改善使用者體驗和介面整潔度，需要進行以下改進：
1. **隱藏成長度數值顯示**：魚類上方的成長度數值顯示會影響視覺體驗，需要暫時隱藏（保留程式碼以便後續啟用）
2. **飼料清單排序優化**：飼料清單應按照 `config.py` 中定義的 `FEED_GROWTH_POINTS` 順序顯示，確保使用者看到的順序與配置一致
3. **新增關閉按鈕**：使用者需要一個明確的方式來關閉應用程式，後續將在此流程中加入存檔機制

## What Changes
- **隱藏成長度顯示**：註解 `aquarium_window.py` 中繪製成長度文字的程式碼區塊（第376-410行），保留程式碼以便後續恢復
- **飼料清單排序**：修改 `_list_feeds()` 函數，按照 `config.py` 中 `FEED_GROWTH_POINTS` 字典的順序排序飼料清單
- **新增關閉按鈕**：在控制面板底部新增「關閉」按鈕，點擊後關閉視窗並退出應用程式
- **關閉流程預留**：在 `close_window()` 方法中預留 TODO 註解，供後續添加存檔機制

## Impact
- **修改能力**：水族箱使用者介面（aquarium-ui）
- **受影響的代碼**：
  - `aquarium_window.py`：
    - 註解成長度顯示相關程式碼
    - 修改 `_list_feeds()` 函數的排序邏輯
    - 在 `ControlPanel` 中新增關閉按鈕和 `close_requested` 信號
    - 在 `TransparentAquariumWindow` 中新增 `close_window()` 方法
  - `config.py`：導入 `FEED_GROWTH_POINTS` 用於排序（僅在 `aquarium_window.py` 中使用）
