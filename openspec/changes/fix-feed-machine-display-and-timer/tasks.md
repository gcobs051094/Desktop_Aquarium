# Tasks: 修復投食機顯示與飼料計時器

## 1. 投食機飼料圖片顯示
- [x] 1.1 在 `FeedMachineWidget` 新增 `_selected_feed_pixmap` 屬性存儲選中飼料的預覽圖
- [x] 1.2 新增 `set_selected_feed()` 方法設定選中飼料並載入預覽圖
- [x] 1.3 修改 `paintEvent()` 在投食機圖片中下方繪製飼料圖片
- [x] 1.4 移除 `ControlPanel` 中的「投食機飼料」標籤和 `_feed_machine_selected_label`
- [x] 1.5 移除 `ControlPanel.update_feed_machine_selected()` 方法

## 2. 配置參數
- [x] 2.1 在 `config.py` 新增 `FEED_MACHINE_FEED_IMAGE_SIZE`（預設 25）
- [x] 2.2 在 `config.py` 新增 `FEED_MACHINE_FEED_IMAGE_OFFSET_X`（預設 0）
- [x] 2.3 在 `config.py` 新增 `FEED_MACHINE_FEED_IMAGE_OFFSET_Y`（預設 -10）
- [x] 2.4 在 `aquarium_window.py` 導入並使用這些配置參數

## 3. 修復投食機選擇飼料時的錯誤扣減
- [x] 3.1 修改 `_on_feed_machine_feed_selected()`：移除選擇時的飼料扣減邏輯
- [x] 3.2 保留 `_feed_machine_shoot_feeds()` 中發射時的扣減邏輯

## 4. 修復飼料計時器
- [x] 4.1 在 `_on_game_time_updated()` 中添加計時器初始化檢查
- [x] 4.2 在 `_restore_state()` 中重置所有已解鎖飼料的 `_feed_counter_last_add` 為當前遊戲時間
- [x] 4.3 確保計時器能正確觸發（避免 `game_time - last` 為負數）
