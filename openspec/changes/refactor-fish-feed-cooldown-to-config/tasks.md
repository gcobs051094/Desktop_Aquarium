## 1. 配置檔修改
- [x] 1.1 在 `config.py` 中新增 `FISH_FEED_COOLDOWN_SEC = 1.0` 配置項

## 2. Fish 類別修改
- [x] 2.1 在 `fish.py` 導入語句中添加 `FISH_FEED_COOLDOWN_SEC`
- [x] 2.2 將 `_update_eating_state()` 方法中的 `feed_cooldown_timer = 1.0` 改為使用 `FISH_FEED_COOLDOWN_SEC`
- [x] 2.3 將 `consume_feed()` 方法中的 `feed_cooldown_timer = 1.0` 改為使用 `FISH_FEED_COOLDOWN_SEC`
- [x] 2.4 修改 `update()` 方法中的追擊邏輯，讓鯊魚和孔雀魚不受 `feed_cooldown_timer` 限制

## 3. Pet 類別修改
- [x] 3.1 在 `pet.py` 導入語句中添加 `FISH_FEED_COOLDOWN_SEC`
- [x] 3.2 將 `PatchworkFishPet._update_eating_state()` 方法中的 `feed_cooldown_timer = 1.0` 改為使用 `FISH_FEED_COOLDOWN_SEC`
- [x] 3.3 將 `PatchworkFishPet.consume_feed()` 方法中的 `feed_cooldown_timer = 1.0` 改為使用 `FISH_FEED_COOLDOWN_SEC`
