## 1. 里程碑計數邏輯修改
- [x] 1.1 在 `_update_unlock_status` 中新增 `total_count_reached` 欄位初始化
- [x] 1.2 新增 `_increment_total_count` 方法，用於累加累計總數
- [x] 1.3 在 `_on_fish_upgraded` 中調用 `_increment_total_count`，每次魚升級到某階段時累加

## 2. 解鎖判定邏輯修改
- [x] 2.1 修改 `_on_tool_unlock_requested` 使用 `max(total_count, max_count)` 判定解鎖
- [x] 2.2 修改 `_update_tool_items` 商店 UI 顯示累計總數
- [x] 2.3 修改 `_update_feed_items` 飼料解鎖條件顯示累計總數

## 3. 向後兼容性處理
- [x] 3.1 讀檔時根據天使鬥魚數量推斷成年鬥魚累計總數
- [x] 3.2 存檔時自動保存 `total_count_reached` 欄位（無需額外修改，`_unlocked_species` 已自動保存）

## 4. 日誌輸出
- [x] 4.1 在 `_record_fish_milestone_before_upgrade` 中添加詳細日誌
- [x] 4.2 在 `_on_fish_upgraded` 中添加詳細日誌
- [x] 4.3 在 `_update_unlock_status` 中添加 `large_鬥魚` 相關日誌
- [x] 4.4 更新讀檔時的里程碑狀態輸出，顯示累計總數
