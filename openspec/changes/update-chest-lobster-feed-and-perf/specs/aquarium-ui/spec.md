## ADDED Requirements

### Requirement: 拾取金條鑽石後投食機與面板選單同步顯示
玩家拾取寶箱怪產出的金條或鑽石後，SHALL 同步更新投食機之已解鎖飼料與計數器（`_feed_machine_widget.set_unlocked_feeds`），使點擊投食機開啟的「選擇飼料」對話框能立即顯示金條/鑽石。側邊面板「切換飼料」按鈕之下拉選單 SHALL 在 `_refresh_feed_menu()` 中除 `_feed_list` 外，對 `CHEST_FEED_ITEMS` 中在 `_unlocked_feeds_for_menu` 者加入選項（金條/鑽石），並顯示數量；有累計時顯示「累計 n 隻」，否則顯示「目前最多 n 隻」風格之進度。

#### Scenario: 拾取金條後投食機選單顯示金條
- **WHEN** 玩家拾取寶箱怪產出的金條
- **THEN** 主視窗更新 `_feed_counters`、`_unlocked_feeds` 並呼叫 `_feed_machine_widget.set_unlocked_feeds`
- **AND** 玩家點擊投食機開啟選擇飼料對話框時，清單中包含金條並顯示數量

#### Scenario: 拾取金條後側邊切換飼料選單顯示金條
- **WHEN** 玩家拾取寶箱怪產出的金條且面板已呼叫 `update_feed_menu`
- **THEN** 玩家點擊側邊「切換飼料」按鈕展開下拉選單時，選單中包含金條選項並顯示數量（如「金條 (1）」）

### Requirement: 龍蝦解鎖顯示與計算與飼料投食機一致
龍蝦 SHALL 以「曾經獲得 5 隻成年鬥魚」解鎖（`unlock_species: "large_鬥魚"`, `unlock_count: 5`）。解鎖判定 SHALL 與飼料投食機一致：`effective_count = max(total_count_reached, max_count_reached)`，已解鎖為 `effective_count >= 5`。商店寵物列表中龍蝦未解鎖時 SHALL 顯示「解鎖條件：曾經獲得 5 隻成年鬥魚（累計 n 隻）」或「目前最多 n 隻」（與飼料投食機相同格式）。召喚龍蝦時 SHALL 以 `effective_count >= 5` 判定可否召喚，不以僅 `max_count_reached` 判定。

#### Scenario: 龍蝦解鎖條件顯示累計
- **WHEN** 龍蝦未解鎖且 `large_鬥魚` 之 `total_count_reached` > 0
- **THEN** 商店寵物列表龍蝦項目顯示「解鎖條件：曾經獲得 5 隻成年鬥魚（累計 n 隻）」且 n = total_count_reached

#### Scenario: 龍蝦解鎖條件顯示目前最多
- **WHEN** 龍蝦未解鎖且 `total_count_reached` 為 0
- **THEN** 顯示「解鎖條件：曾經獲得 5 隻成年鬥魚（目前最多 n 隻）」且 n = max_count_reached

#### Scenario: 龍蝦以 effective_count 判定可召喚
- **WHEN** `total_count_reached` 為 3、`max_count_reached` 為 2，unlock_count 為 5
- **THEN** effective_count = 3，未達 5，龍蝦不可召喚
- **WHEN** `total_count_reached` 為 5 或 `max_count_reached` 為 5（任一達 5）
- **THEN** effective_count >= 5，龍蝦可召喚
