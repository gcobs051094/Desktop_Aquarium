## ADDED Requirements

### Requirement: 孔雀魚不進食不追飼料
孔雀魚 SHALL 不進食、不追飼料；碰撞檢測與魚類更新邏輯 SHALL 跳過孔雀魚的吃飼料與追飼料行為。

#### Scenario: 孔雀魚不追飼料
- **WHEN** 魚種為孔雀魚（`species == "孔雀魚"`）且 `Fish.update()` 被呼叫
- **THEN** 傳入之飼料列表在追飼料邏輯中被視為 None（不執行 `_find_nearest_feed`／`_move_towards_feed`）

#### Scenario: 孔雀魚不吃飼料
- **WHEN** 碰撞檢測處理魚與飼料
- **THEN** 若魚種為孔雀魚則跳過該魚，不觸發 `eat_feed()` 或 `consume_feed()`

---

### Requirement: 鬥魚碰觸孔雀魚時追飼料速度加成
鬥魚魚種 SHALL 在碰觸孔雀魚時，追飼料的速度倍率增加約 0.2 個單位，並維持 2 秒。

#### Scenario: 碰觸孔雀魚後加速
- **WHEN** 鬥魚（`species == "鬥魚"`）的顯示矩形與孔雀魚的顯示矩形相交
- **THEN** 該鬥魚之 `guppy_touch_buff_until` 設為當前遊戲時間 + 2 秒
- **AND** 在該時間之前，該鬥魚朝飼料移動時速度倍率為基礎追飼料倍率 + 0.2

#### Scenario: 加成維持 2 秒
- **WHEN** 鬥魚享有孔雀魚碰觸加成（`current_game_time_sec < guppy_touch_buff_until`）
- **THEN** `_move_towards_feed()` 計算之速度倍率包含 `BETTA_GUPPY_TOUCH_SPEED_BONUS`（0.2）
- **AND** 超過 2 秒後加成失效，速度倍率恢復為僅基礎追飼料倍率

---

### Requirement: 鯊魚不吃飼料不追飼料但吃幼年鬥魚
鯊魚 SHALL 不吃飼料、不追飼料；SHALL 每 300 秒可吃一隻幼年鬥魚，吃過後 300 秒內不再進食，期間每 30 秒大便魚翅；超過 300 秒沒吃過幼年鬥魚則不大便魚翅。

#### Scenario: 鯊魚不追飼料不進食飼料
- **WHEN** 魚種為鯊魚（`species == "鯊魚"`）
- **THEN** `Fish.update()` 中不傳飼料給追飼料邏輯；碰撞檢測跳過鯊魚與飼料的吃飼料行為

#### Scenario: 鯊魚吃幼年鬥魚
- **WHEN** 鯊魚自上次吃幼年鬥魚起已過 300 秒（或從未吃過）且其顯示矩形與幼年鬥魚（`species == "鬥魚"` 且 `stage == "small"`）相交
- **THEN** 該幼年鬥魚進入死亡效果（`set_dead()`）；該鯊魚之 `last_eat_betta_time` 設為當前遊戲時間，`next_poop_at` 設為當前時間 + 30 秒

#### Scenario: 吃過幼年鬥魚後 300 秒內每 30 秒大便魚翅
- **WHEN** 鯊魚之 `last_eat_betta_time` 已設定且當前遊戲時間在 `last_eat_betta_time + 300` 之內
- **AND** 當前遊戲時間 ≥ `next_poop_at`
- **THEN** 在水族箱中產生魚翅金錢（`_on_fish_poop("魚翅", position)`）
- **AND** `next_poop_at` 增加 30 秒，直至超過 `last_eat_betta_time + 300` 則不再大便

#### Scenario: 超過 300 秒沒吃幼年鬥魚則不大便魚翅
- **WHEN** 當前遊戲時間 - `last_eat_betta_time` > 300 秒（或鯊魚從未吃過幼年鬥魚）
- **THEN** 不觸發魚翅大便
- **AND** 鯊魚可再次吃一隻幼年鬥魚（下次碰撞時）

---

### Requirement: 死亡／犧牲召喚／移除之死亡動畫
魚隻被死亡或被移除（解鎖、犧牲召喚等）時，SHALL 以該魚種第一幀反轉 xy、灰階呈現，不再進行進食、游泳、轉向、追飼料，並以約 10 幀往上緩慢移動、逐漸消失；灰階處理 SHALL 僅對不透明像素做灰階，保留透明（去背），確保 PNG 去背處不變黑。

#### Scenario: 進入死亡狀態
- **WHEN** 魚隻因死亡或移除而呼叫 `set_dead()`
- **THEN** `is_dead = True`；建立死亡用幀：第一幀（游泳第一幀）反轉 xy、灰階
- **AND** 灰階時使用帶 alpha 的格式（如 `Format_ARGB32`），僅對 `alpha > 0` 之像素將 R、G、B 改為灰階值，`alpha == 0` 之像素維持不變（去背維持透明）

#### Scenario: 死亡狀態下不進行一般行為
- **WHEN** 魚隻 `is_dead == True`
- **THEN** 不執行進食、游泳、轉向、追飼料；僅執行死亡效果更新（上移、淡出）
- **AND** 顯示時使用 `death_opacity` 繪製

#### Scenario: 死亡動畫結束後移除
- **WHEN** 魚隻死亡狀態下 `death_timer > 2` 秒或 `death_opacity <= 0`
- **THEN** 該魚從水族箱魚類列表中移除
