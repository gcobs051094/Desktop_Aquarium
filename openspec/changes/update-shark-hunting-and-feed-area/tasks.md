# Tasks: 鯊魚主動追獵、死亡動畫調整與飼料投放區域限制

## 1. 鯊魚主動追幼鬥魚
- [x] 1.1 在 `fish.py` 的 `update()` 新增 `prey` 參數，讓鯊魚追獵幼鬥魚
- [x] 1.2 在 `aquarium_window.py` 的 `update_fishes()` 中建立幼鬥魚列表並傳入鯊魚的 `update()` 方法

## 2. 被鯊魚吃掉不播死亡動畫
- [x] 2.1 修改 `_check_shark_eat_betta()` 回傳 `(shark, eaten_fish)` 而非直接呼叫 `set_dead()`
- [x] 2.2 在 `update_fishes()` 中處理回傳值：直接移除被吃魚，呼叫 `shark.eat_feed()` 播吃飯動畫

## 3. 魚升級不播死亡動畫
- [x] 3.1 修改 `_on_fish_upgrade()` 中舊魚處理：直接從列表移除而非呼叫 `set_dead()`

## 4. 鬥魚碰孔雀魚加速擴展
- [x] 4.1 在 `fish.py` 的 `update()` 中，若鬥魚有孔雀魚 buff 且非追飼料狀態，也套用速度加成

## 5. 飼料投放區域限制
- [x] 5.1 在 `on_aquarium_clicked()` 中計算魚可游動區域（邊緣向內 50 像素）
- [x] 5.2 點擊位置若不在可游動區域內則不投放飼料

## 6. 商店飼料 tab 按鈕修復
- [x] 6.1 調整飼料 tab ScrollArea 設定（margin、scrollbar policy）
- [x] 6.2 為卡片資訊區設定 `setSizePolicy` 和 `setMinimumWidth(0)` 讓文字能縮小
- [x] 6.3 為 desc_label、status_label 設定 `setWordWrap(True)` 和 `setSizePolicy`
- [x] 6.4 調整核廢料解鎖按鈕為兩行文字、固定尺寸
