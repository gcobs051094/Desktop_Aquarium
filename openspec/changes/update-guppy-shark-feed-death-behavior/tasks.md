# Tasks: 孔雀魚／鯊魚行為、飼料解鎖與計數、死亡動畫

## 1. 孔雀魚與鬥魚碰孔雀魚
- [x] 1.1 孔雀魚不進食、不追飼料：`Fish.update()` 中孔雀魚／鯊魚時將 feeds 視為 None；`_check_feed_collisions` 跳過孔雀魚與鯊魚
- [x] 1.2 鬥魚碰孔雀魚時追飼料速度倍率 +0.2、維持 2 秒：config 新增 `BETTA_GUPPY_TOUCH_SPEED_BONUS`、`GUPPY_TOUCH_BUFF_DURATION_SEC`；Fish 新增 `guppy_touch_buff_until`、`current_game_time_sec`；`_move_towards_feed()` 依 buff 加成；AquariumWidget 新增 `_check_betta_touch_guppy()` 並每幀寫入 `current_game_time_sec`

## 2. 鯊魚吃幼年鬥魚與魚翅
- [x] 2.1 鯊魚不吃飼料、不追飼料（同 1.1）
- [x] 2.2 每 300 秒可吃一隻幼年鬥魚，吃過後 300 秒內不再進食：config 新增 `SHARK_EAT_BETTA_INTERVAL_SEC`、`SHARK_POOP_INTERVAL_SEC`、`SHARK_POOP_DURATION_SEC`；Fish 新增 `last_eat_betta_time`、`next_poop_at`；AquariumWidget 新增 `_check_shark_eat_betta()`、`_update_shark_poop()`、`_game_time_sec`
- [x] 2.3 吃過幼年鬥魚後 300 秒內每 30 秒大便魚翅；超過 300 秒沒吃則不大便：`_on_fish_poop("魚翅", ...)`；`MONEY_VALUE["魚翅"]`、resource/money/魚翅
- [x] 2.4 鯊魚狀態存檔：`to_dict`／`from_dict` 儲存與還原 `last_eat_betta_time`、`next_poop_at`

## 3. 飼料解鎖與計數
- [x] 3.1 config 新增 `FEED_UNLOCK_CONFIG`（便宜／鯉魚／藥丸／核廢料之 unlock_by、unlock_value、counter_interval_sec）；藥丸成長度改為 10
- [x] 3.2 主視窗與 game_state：`_feed_cheap_count`、`_feed_counters`、`_unlocked_feeds`、`_feed_counter_last_add`；載入／儲存；`_update_feed_unlocks()`、`_on_game_time_updated()` 定時增加計數器
- [x] 3.3 切換飼料選單僅顯示已解鎖飼料，可點擊次數依專屬計數器；投放飼料時便宜飼料不扣數、其餘扣減對應計數器
- [x] 3.4 核廢料：僅鬥魚與拼布魚會吃；進食後 80% 死亡、20% 複製；解鎖為犧牲 6 隻中鬥魚（商店飼料 tab 解鎖按鈕）

## 4. 商店飼料 tab
- [x] 4.1 飼料 tab 格式與魚種／寵物一致：黃字名稱（#ffd700）、說明（#c0c0c0）、解鎖條件（已解鎖 #90ee90／未解鎖 #ff6b6b）；64×64 預覽圖、卡片版面
- [x] 4.2 含便宜飼料、鯉魚飼料、藥丸、核廢料解鎖說明；核廢料解鎖條件與「目前中鬥魚：X 隻」同一欄位；僅核廢料有「解鎖（犧牲 6 隻中鬥魚）」按鈕
- [x] 4.3 `update_items()` 新增 `feed_cheap_count`；`_update_feed_items()` 接收 `unlocked_feeds`、`fish_counts`、`feed_cheap_count`、`unlocked_species`

## 5. 死亡／犧牲召喚／移除動畫
- [x] 5.1 魚隻死亡或移除時改為 `set_dead()`，不立即從列表移除：升級、犧牲購買、核廢料致死、鯊魚吃幼鬥魚時呼叫 `fish.set_dead()`
- [x] 5.2 死亡幀：第一幀反轉 xy、灰階；灰階時僅對不透明像素做灰階，保留 alpha（去背維持透明），避免 PNG 去背變黑
- [x] 5.3 死亡狀態：不進食、不游泳、不轉向、不追飼料；往上緩慢移動並逐漸消失；`death_timer > 2` 或 `death_opacity <= 0` 時從列表移除
