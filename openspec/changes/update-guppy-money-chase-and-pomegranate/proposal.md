# Change: 孔雀魚追金錢與石榴結晶轉換、投放幼鬥魚費用、商店UI統一

## Why
1. **移除鬥魚碰觸孔雀魚加成**：原本的加成機制不再需要，簡化遊戲邏輯。
2. **新增孔雀魚追金錢功能**：讓孔雀魚有獨特的行為，每5秒追最近的金錢並有機會轉換為石榴結晶。
3. **統一商店UI樣式**：商店各tab（魚種、寵物、飼料、工具）的卡片與按鈕布局統一，提升一致性。
4. **投放幼鬥魚費用**：增加遊戲經濟平衡，投放幼鬥魚需要花費20元。
5. **修復UI問題**：修復金條/鑽石在飼料清單重複顯示的問題。

## What Changes
- **移除鬥魚碰觸孔雀魚加成**：移除 `_check_betta_touch_guppy()`、`guppy_touch_buff_until`、`BETTA_GUPPY_TOUCH_SPEED_BONUS` 等相關代碼。
- **孔雀魚追金錢**：
  - 每5秒追最近的金錢（排除已收集、已石榴化、已觸底的金錢）
  - 追金錢時速度倍率為 2.5（比追飼料更快）
  - 冷卻期間（5秒）不追金錢，避免黏在同一顆金錢上
- **石榴結晶轉換**：
  - 孔雀魚碰觸金錢後，依 `GUPPY_MONEY_TRANSFORM_CHANCE`（預設1.0，100%）機率轉換為石榴結晶
  - 使用固定色相（HSV 0度，紅色）調整圖片色調
  - 轉換後原金錢消失（播放消失動畫）
  - 石榴結晶金錢拾取價值為原金錢的 1.5 倍
- **投放幼鬥魚費用**：
  - 投放一隻幼鬥魚需要花費 20 元（`SMALL_BETTA_COST`）
  - 投放魚清單中幼鬥魚顯示「鬥魚 (花費20$)」
  - 金幣不足時無法投放
- **商店UI統一**：
  - 魚種、寵物、飼料、工具四個tab的卡片布局統一（預覽圖、名稱、描述、解鎖條件、按鈕）
  - 資訊區最大寬度200px，按鈕寬度80px
  - 無按鈕的飼料項目右側保留佔位，保持對齊
- **商店顯示優化**：
  - 孔雀魚解鎖/購買描述中「angel_鬥魚」顯示為「天使鬥魚」
  - 修復金條/鑽石在飼料清單重複顯示的問題（跳過 `CHEST_FEED_ITEMS` 避免重複）

## Impact
- **Affected specs**: `fish-behavior`、`game-economy`、`aquarium-ui`
- **Affected code**:
  - `config.py`：`GUPPY_MONEY_CHASE_INTERVAL_SEC`、`GUPPY_MONEY_TRANSFORM_CHANCE`、`GUPPY_MONEY_CHASE_SPEED_MULTIPLIER`、`GUPPY_MONEY_COOLDOWN_SEC`、`POMEGRANATE_FIXED_HUE`、`POMEGRANATE_MONEY_VALUE_MULTIPLIER`、`SMALL_BETTA_COST`、`get_money_value()`
  - `fish.py`：移除 `guppy_touch_buff_until`、新增 `money_chase_timer`、`money_chase_interval`、`money_touch_cooldown_until`、`_current_money_target`，修改 `update()` 支援 `moneys` 參數
  - `aquarium_window.py`：移除 `_check_betta_touch_guppy()`，新增 `_check_guppy_touch_money()`、`_adjust_hue_to_pomegranate()`，修改商店UI統一格式，修改 `add_one_fish()` 加入費用檢查
  - `pet.py`：修改 `check_money_collision()` 使用 `get_money_value()`
