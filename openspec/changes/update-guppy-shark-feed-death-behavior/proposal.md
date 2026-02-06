# Change: 孔雀魚／鯊魚行為、飼料解鎖與計數、死亡動畫

## Why
統一規範孔雀魚（不進食不追飼料）、鬥魚碰孔雀魚時追飼料加速、鯊魚吃幼年鬥魚與魚翅產出、飼料解鎖與專屬計數器、核廢料食用與死亡／複製、死亡／犧牲召喚／移除的死亡動畫（第一幀反轉 xy、灰階保留去背、上移淡出），以及商店飼料 tab 與魚種／寵物相同格式（黃字名稱、說明、解鎖條件）。

## What Changes
- **孔雀魚**：不進食、不追飼料；碰撞檢測與 `Fish.update()` 中跳過孔雀魚的吃飼料與追飼料邏輯。
- **鬥魚碰孔雀魚**：鬥魚碰觸孔雀魚時，追飼料速度倍率 +0.2，維持 2 秒（`guppy_touch_buff_until`、`_check_betta_touch_guppy()`）。
- **鯊魚**：不吃飼料、不追飼料；每 300 秒可吃一隻幼年鬥魚，吃過後 300 秒內不再進食，期間每 30 秒大便魚翅（`resource/money/魚翅`）；超過 300 秒沒吃過幼年鬥魚則不大便魚翅。
- **飼料**：便宜飼料成長度 1、可無限投餵；鯉魚飼料成長度 3、投餵便宜飼料 100 次解鎖、解鎖後每 5 秒數量+1；藥丸成長度 10、曾達到 10 隻成年鬥魚解鎖、解鎖後每 20 秒數量+1；核廢料成長度 1、犧牲 6 隻中鬥魚解鎖、解鎖後每 300 秒數量+1，鬥魚與拼布魚會吃核廢料，進食後 80% 死亡、20% 複製。待解鎖飼料不出現在切換飼料選單；解鎖後出現，可點擊次數依該飼料專屬數量計數器。
- **商店飼料 tab**：格式與魚種／寵物一致（黃字名稱、說明、解鎖條件）；含便宜飼料、鯉魚飼料、藥丸、核廢料；核廢料解鎖條件與「目前中鬥魚：X 隻」同一欄位；僅核廢料有「解鎖（犧牲 6 隻中鬥魚）」按鈕。
- **死亡／犧牲召喚／移除**：魚隻被死亡或被移除時，以該魚種第一幀反轉 xy、灰階（僅對不透明像素做灰階，保留透明去背）、不再進食／游泳／轉向／追飼料，以約 10 幀往上緩慢移動並逐漸消失；灰階處理須保留 alpha，避免去背變黑。

## Impact
- **受影響能力**：魚類行為（fish-behavior）、遊戲經濟（game-economy）、水族箱 UI（aquarium-ui）
- **受影響代碼**：
  - `config.py`：`FEED_GROWTH_POINTS`（藥丸 10）、`FEED_UNLOCK_CONFIG`、`BETTA_GUPPY_TOUCH_SPEED_BONUS`、`GUPPY_TOUCH_BUFF_DURATION_SEC`、鯊魚與核廢料常數、`MONEY_VALUE["魚翅"]`
  - `fish.py`：孔雀魚／鯊魚不追飼料、鬥魚碰孔雀魚加速、鯊魚 `last_eat_betta_time`／`next_poop_at`、死亡狀態與 `_build_death_frame()`（灰階保留 alpha）
  - `aquarium_window.py`：`_check_betta_touch_guppy()`、`_check_shark_eat_betta()`、`_update_shark_poop()`、飼料碰撞跳過孔雀魚／鯊魚、核廢料 80%／20%、死亡效果與移除時序、飼料計數與解鎖、商店飼料 tab 格式與解鎖說明
  - `game_state.py`：`feed_cheap_count`、`feed_counters`、`unlocked_feeds`、`feed_counter_last_add`
