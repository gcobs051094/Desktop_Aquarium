## 1. 投食機點擊選擇飼料功能
- [x] 1.1 創建 `FeedSelectionDialog` 對話框類
- [x] 1.2 在 `FeedMachineWidget` 中添加 `feed_selected` 信號
- [x] 1.3 實現 `FeedMachineWidget.mousePressEvent()` 點擊處理，彈出選擇對話框
- [x] 1.4 在 `ControlPanel` 中添加投食機選取飼料顯示區域
- [x] 1.5 實現 `ControlPanel.update_feed_machine_selected()` 更新顯示

## 2. 投食機自動投食功能
- [x] 2.1 在 `config.py` 添加 `FEED_MACHINE_INTERVAL_SEC` 配置
- [x] 2.2 在 `TransparentAquariumWindow` 添加投食機計時器
- [x] 2.3 實現 `_feed_machine_shoot_feeds()` 發射飼料功能
- [x] 2.4 在 `_on_game_time_updated()` 中添加自動投食計時邏輯
- [x] 2.5 實現 `_on_feed_machine_feed_selected()` 處理選擇飼料事件

## 3. 拋物線軌跡實現
- [x] 3.1 修改 `Feed` 類添加拋物線參數（`is_parabolic`、`target_position`、`parabolic_progress`）
- [x] 3.2 實現 `Feed.update()` 中的拋物線軌跡計算
- [x] 3.3 使用 sin 函數創建平滑的拋物線高度變化

## 4. 投食機位置配置
- [x] 4.1 在 `config.py` 添加位置配置參數：
  - `FEED_MACHINE_EXIT_X_RATIO`
  - `FEED_MACHINE_EXIT_X_OFFSET`
  - `FEED_MACHINE_TARGET_X_MIN_RATIO`
  - `FEED_MACHINE_TARGET_X_MAX_RATIO`
- [x] 4.2 在 `_feed_machine_shoot_feeds()` 中使用配置計算起始位置
- [x] 4.3 在 `_feed_machine_shoot_feeds()` 中使用配置計算落點範圍
- [x] 4.4 修正座標轉換（主視窗座標轉換為水族箱本地座標）

## 5. 大便行為優化
- [x] 5.1 修改 `config.py` 中的 `BETTA_POOP_CONFIG`，間隔值改為範圍元組
- [x] 5.2 修改 `Fish.__init__()` 支援範圍間隔配置
- [x] 5.3 修改 `Fish.update()` 每次大便後重新隨機選擇間隔時間
- [x] 5.4 確保向後兼容（支援單一數值格式）

## 6. 測試與驗證
- [ ] 6.1 測試投食機點擊選擇飼料功能
- [ ] 6.2 測試自動投食功能（間隔、數量、拋物線軌跡）
- [ ] 6.3 測試位置配置參數的效果
- [ ] 6.4 測試大便行為範圍間隔是否有效分散大便時間
- [ ] 6.5 驗證座標轉換正確性（標記位置與實際位置一致）
