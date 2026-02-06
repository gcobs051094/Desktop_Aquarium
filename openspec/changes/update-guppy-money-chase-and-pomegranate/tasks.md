# Tasks: 孔雀魚追金錢與石榴結晶轉換、投放幼鬥魚費用、商店UI統一

## 1. 移除鬥魚碰觸孔雀魚加成
- [x] 1.1 移除 `config.py` 中的 `BETTA_GUPPY_TOUCH_SPEED_BONUS`、`GUPPY_TOUCH_BUFF_DURATION_SEC`
- [x] 1.2 移除 `fish.py` 中的 `guppy_touch_buff_until` 屬性
- [x] 1.3 移除 `fish.py` 中所有使用 `BETTA_GUPPY_TOUCH_SPEED_BONUS` 的代碼
- [x] 1.4 移除 `aquarium_window.py` 中的 `_check_betta_touch_guppy()` 方法
- [x] 1.5 移除 `aquarium_window.py` 中對 `GUPPY_TOUCH_BUFF_DURATION_SEC` 的引用

## 2. 孔雀魚追金錢功能
- [x] 2.1 在 `config.py` 新增 `GUPPY_MONEY_CHASE_INTERVAL_SEC = 5.0`
- [x] 2.2 在 `fish.py` 新增 `money_chase_timer`、`money_chase_interval`、`_current_money_target` 屬性
- [x] 2.3 修改 `Fish.update()` 支援 `moneys` 參數
- [x] 2.4 實作孔雀魚每5秒追最近金錢的邏輯（排除已收集、已石榴化、已觸底）
- [x] 2.5 在 `aquarium_window.py` 的 `update_fishes()` 中傳入 `moneys` 列表給孔雀魚
- [x] 2.6 在 `config.py` 新增 `GUPPY_MONEY_CHASE_SPEED_MULTIPLIER = 2.5`
- [x] 2.7 修改 `Fish._move_towards_feed()` 支援 `is_chasing_money` 參數，使用更快的速度倍率

## 3. 石榴結晶轉換
- [x] 3.1 在 `config.py` 新增 `GUPPY_MONEY_TRANSFORM_CHANCE = 1.0`、`GUPPY_MONEY_COOLDOWN_SEC = 5.0`
- [x] 3.2 在 `config.py` 新增 `POMEGRANATE_FIXED_HUE = 0`、`POMEGRANATE_MONEY_VALUE_MULTIPLIER = 1.5`
- [x] 3.3 實作 `_adjust_hue_to_pomegranate()` 函數（固定色相調整）
- [x] 3.4 實作 `_check_guppy_touch_money()` 方法（碰撞檢測、轉換邏輯）
- [x] 3.5 在 `fish.py` 新增 `money_touch_cooldown_until` 屬性
- [x] 3.6 冷卻期間不追金錢（`fish.py` 中檢查冷卻時間）
- [x] 3.7 過濾已石榴化的金錢（名稱以「石榴結晶_」開頭）
- [x] 3.8 過濾已觸底的金錢（`bottom_time >= 0`）
- [x] 3.9 實作 `get_money_value()` 函數，支援石榴結晶價值倍率
- [x] 3.10 更新所有金錢價值取得處使用 `get_money_value()`

## 4. 投放幼鬥魚費用
- [x] 4.1 在 `config.py` 新增 `SMALL_BETTA_COST = 20`
- [x] 4.2 在 `add_one_fish()` 中檢查是否為幼鬥魚，扣除20元
- [x] 4.3 在投放魚清單中，幼鬥魚顯示「鬥魚 (花費20$)」

## 5. 商店UI統一
- [x] 5.1 統一飼料tab卡片布局（移除 `setMinimumHeight`、`setContentsMargins`，使用 `info_layout` 直接）
- [x] 5.2 統一工具tab卡片布局（同上）
- [x] 5.3 統一按鈕寬度為80px
- [x] 5.4 無按鈕的飼料項目右側保留80px佔位
- [x] 5.5 所有tab的資訊區最大寬度200px
- [x] 5.6 工具tab未解鎖狀態改為禁用按鈕（與魚種/寵物一致）

## 6. 商店顯示優化
- [x] 6.1 孔雀魚解鎖/購買描述中「angel_鬥魚」顯示為「天使鬥魚」
- [x] 6.2 修復金條/鑽石在飼料清單重複顯示（跳過 `CHEST_FEED_ITEMS`）
- [x] 6.3 飼料tab中金條/鑽石顯示預覽圖（使用 `_get_chest_feed_image_path()`）
