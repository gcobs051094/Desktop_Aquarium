# Change: 修復投食機顯示與飼料計時器

## Why
1. 投食機選取飼料後，應在投食機圖片上顯示當前選取的飼料，而非在控制面板右側顯示
2. 投食機選擇飼料時錯誤地扣減了飼料數量，應只在發射時扣減
3. 飼料計時器在載入存檔後無法正常運作，因為遊戲時間不會被保存

## What Changes
- 移除控制面板右側的「投食機飼料」和「未選擇」文字
- 將選取的飼料圖片疊加在投食機影像的中下方顯示
- 新增 `config.py` 配置參數：`FEED_MACHINE_FEED_IMAGE_SIZE`、`FEED_MACHINE_FEED_IMAGE_OFFSET_X`、`FEED_MACHINE_FEED_IMAGE_OFFSET_Y`
- 修復投食機選擇飼料時錯誤扣減數量的問題
- **修復飼料計時器**：載入存檔時重置 `_feed_counter_last_add` 為當前遊戲時間，避免計時器永不觸發

## Impact
- Affected specs: aquarium-ui, game-economy
- Affected code: `aquarium_window.py`, `config.py`
