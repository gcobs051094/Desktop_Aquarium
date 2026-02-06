# Change: 將魚追飼料冷卻時間移至配置檔並排除鯊魚與孔雀魚

## Why
原本魚追飼料的冷卻時間（`feed_cooldown_timer`）在代碼中硬編碼為 1.0 秒，不便于調整。此外，鯊魚和孔雀魚雖然不會吃飼料，但卻受到 `feed_cooldown_timer` 的影響，導致它們在冷卻期間無法追擊各自的目標（幼鬥魚和金錢），這不符合設計意圖。

## What Changes
- 在 `config.py` 中新增 `FISH_FEED_COOLDOWN_SEC` 配置項（預設 1.0 秒）
- 將 `fish.py` 和 `pet.py` 中所有硬編碼的 `feed_cooldown_timer = 1.0` 改為使用 `FISH_FEED_COOLDOWN_SEC`
- 修改 `fish.py` 中的追擊邏輯，讓鯊魚和孔雀魚不受 `feed_cooldown_timer` 限制
- 鯊魚和孔雀魚只受各自的冷卻機制影響：
  - 鯊魚：受 `SHARK_EAT_BETTA_INTERVAL_SEC`（300秒）限制
  - 孔雀魚：受 `GUPPY_MONEY_COOLDOWN_SEC`（5秒）限制

## Impact
- Affected specs: `fish-behavior`
- Affected code: `config.py`（新增配置）、`fish.py`（使用配置並排除鯊魚/孔雀魚）、`pet.py`（使用配置）
