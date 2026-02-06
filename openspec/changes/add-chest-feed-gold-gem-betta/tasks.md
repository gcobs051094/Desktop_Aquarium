# Tasks: 寶箱怪金條鑽石改為飼料、天使鬥魚變身金鬥魚與寶石鬥魚

## 1. 配置
- [x] 1.1 在 `config.py` 新增 `CHEST_FEED_ITEMS = ["金條", "鑽石"]`；拾取金條/鑽石時不增加總金額、改為加入飼料計數。
- [x] 1.2 在 `MONEY_VALUE` 新增金錐體（1000）、藍寶石（1500）。
- [x] 1.3 在 `BETTA_POOP_CONFIG` 新增 `golden_鬥魚`（金錐體，50～60 秒）、`gem_鬥魚`（藍寶石，50～60 秒）。
- [x] 1.4 在 `FEED_GROWTH_POINTS`、`FEED_COUNTER_INTERVAL_SEC`、`FEED_UNLOCK_CONFIG`、`FEED_SCALE` 新增金條、鑽石（成長度 0、`unlock_by: "chest_feed_count"`）。
- [x] 1.5 在 `FISH_SCALE_BY_STAGE_SPECIES` 新增 `golden_鬥魚`、`gem_鬥魚` 縮放。

## 2. 寶箱怪拾取與飼料計數
- [x] 2.1 `try_collect_chest_produce_at()` 改為回傳 `Optional[Tuple[str, int]]`（產物類型, 金額）。
- [x] 2.2 在 `on_aquarium_clicked()`：若產物為金條或鑽石，不增加 `total_money`，改為 `_feed_counters[產物] += 1` 並將該飼料加入 `_unlocked_feeds`、更新飼料選單。
- [x] 2.3 在 `_update_feed_unlocks()` 新增 `unlock_by == "chest_feed_count"`：當 `_feed_counters[feed_name] > 0` 時將該飼料加入 `_unlocked_feeds`。

## 3. 飼料清單與投放
- [x] 3.1 新增 `_get_chest_feed_image_path(feed_name)`，回傳 `resource/money/寶箱怪產物/寶箱怪產物_{name}.png`。
- [x] 3.2 `_feed_preview_pixmap()` 支援單一檔案路徑（供金條/鑽石預覽）。
- [x] 3.3 在 `FeedSelectionDialog` 中，飼料列表除 `_list_feeds()` 外，若金條/鑽石在 `unlocked_feeds` 中，加入 (名稱, 寶箱怪產物圖路徑) 並顯示數量。
- [x] 3.4 在 `on_aquarium_clicked()` 投放飼料時：若當前飼料為金條/鑽石，從 `_get_chest_feed_image_path()` 載入單幀作為飼料並可投放；投放時扣減對應 `_feed_counters`。

## 4. 天使鬥魚吃金條/鑽石變身
- [x] 4.1 在 `_check_feed_collisions()`：若飼料為金條或鑽石，金鬥魚/寶石鬥魚（`stage in ("golden", "gem")`）不處理；僅當 `species == "鬥魚"` 且 `stage == "angel"` 時可吃；吃後呼叫 `_on_fish_upgrade(fish, "golden")` 或 `_on_fish_upgrade(fish, "gem")`。
- [x] 4.2 在 `_create_upgraded_fish()` 與 `_load_game_state()` 的階段名稱映射中新增 `"golden": "金鬥魚"`、`"gem": "寶石鬥魚"`，使用 `resource/fish/鬥魚/金鬥魚`、`resource/fish/鬥魚/寶石鬥魚`。

## 5. 金鬥魚/寶石鬥魚大便與只吃飼料
- [x] 5.1 金鬥魚、寶石鬥魚之大便由既有 `Fish` 大便計時與 `BETTA_POOP_CONFIG` 處理（golden_鬥魚→金錐體、gem_鬥魚→藍寶石，50～60 秒）。
- [x] 5.2 金鬥魚、寶石鬥魚在碰撞檢測中不吃金條/鑽石（已於 4.1 排除）；金錐體/藍寶石為金錢物件非飼料，故僅吃一般飼料。
