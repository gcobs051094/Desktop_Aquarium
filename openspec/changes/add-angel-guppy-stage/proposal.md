# Change: Guppy 第四型態 angel_guppy 與 heart_coin

## Why
1. **成長與回饋延伸**：在 large_guppy 之後提供第四階段（angel_guppy），延長成長線並提高高階魚的產出價值。
2. **遊戲經濟**：天使型 guppy 產出高價值 heart_coin（$500），每 20 秒一次，強化後期經濟回饋。

## What Changes
- **成長階段**：在 `config.py` 之 `GROWTH_STAGES` 新增第四階段 `"angel"`；在 `FISH_UPGRADE_THRESHOLDS["guppy"]` 新增 `"large": 100`，large_guppy 成長度達 100 時升級為 angel_guppy。
- **大便金錢**：在 `GUPPY_POOP_CONFIG` 新增 `"angel_guppy": ("heart_coin", 20)`，天使型 guppy 每 20 秒在當前位置產生 heart_coin；金錢素材來自 `resource/money/heart_coin`。
- **金錢價值**：在 `MONEY_VALUE` 新增 `"heart_coin": 500`，拾取 heart_coin 時增加 500 金錢。

## Impact
- Affected specs: game-economy
- Affected code: `config.py`（`GROWTH_STAGES`、`FISH_UPGRADE_THRESHOLDS`、`GUPPY_POOP_CONFIG`、`MONEY_VALUE`）；`fish.py` 與 `aquarium_window.py` 沿用既有升級與大便邏輯，無需改動即可支援新階段與新金錢類型。
