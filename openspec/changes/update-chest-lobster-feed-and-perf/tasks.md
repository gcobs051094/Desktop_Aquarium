# Tasks: 寶箱怪產物隨機、金條鑽石僅天使鬥魚、金錢快取、龍蝦解鎖一致

## 1. 寶箱怪產物依等級隨機
- [x] 1.1 修正 `pet.py` 中 `ChestMonsterPet.set_level()`：level 1 為 `["珍珠", "金條"]`，level 2 為 `["珍珠", "金條", "鑽石"]`
- [x] 1.2 更新類別與 `set_level` 之 docstring、`config.py` 中 `CHEST_LEVEL` 註解

## 2. 切換飼料清單顯示金條/鑽石
- [x] 2.1 拾取金條/鑽石後呼叫 `_feed_machine_widget.set_unlocked_feeds(self._unlocked_feeds, self._feed_counters)`
- [x] 2.2 面板 `_refresh_feed_menu()` 在 `_feed_list` 迴圈後，對 `CHEST_FEED_ITEMS` 中在 `_unlocked_feeds_for_menu` 者加入選單項目（金條/鑽石）

## 3. 金條/鑽石僅天使鬥魚追與吃
- [x] 3.1 更新魚類時：天使鬥魚傳入 `self.feeds`，其餘魚傳入排除 `CHEST_FEED_ITEMS` 的飼料列表
- [x] 3.2 更新寵物時傳入排除金條/鑽石的飼料列表
- [x] 3.3 `_check_feed_collisions` 中寵物與飼料碰撞時，若 `feed.feed_name in CHEST_FEED_ITEMS` 則 continue

## 4. 金錢動畫幀快取
- [x] 4.1 新增 `_money_frames_cache: Dict[str, List[QPixmap]]`
- [x] 4.2 `_load_money_frames(money_type)` 先查快取，無則載入並寫入快取後回傳

## 5. 龍蝦解鎖與飼料投食機一致
- [x] 5.1 寵物列表 `_update_pet_items`：龍蝦（unlock_species）取 `total_count_reached`、`max_count_reached`，`effective_count = max(兩者)` 判定解鎖；顯示「累計 n 隻」或「目前最多 n 隻」
- [x] 5.2 `_on_pet_purchase_requested`：魚種解鎖時以 `effective_count = max(total_count_reached, max_count_reached) >= unlock_count` 判定可否召喚
