## ADDED Requirements

### Requirement: 切換飼料清單顯示金條與鑽石
當玩家擁有金條或鑽石數量（`_feed_counters` 對應數量 > 0）時，SHALL 在「切換飼料」清單中顯示金條、鑽石選項，並顯示當前數量。金條、鑽石之預覽圖 SHALL 使用 `resource/money/寶箱怪產物/寶箱怪產物_金條.png`、`寶箱怪產物_鑽石.png`。金條、鑽石解鎖條件為「有數量」（`unlock_by: "chest_feed_count"`），由 `_update_feed_unlocks` 在數量 > 0 時加入 `_unlocked_feeds`。

#### Scenario: 有金條數量時清單顯示金條
- **WHEN** `_feed_counters["金條"]` > 0 且玩家開啟切換飼料對話框
- **THEN** 飼料清單中包含「金條」選項並顯示數量（如「金條 (3）」）
- **AND** 預覽圖為寶箱怪產物之金條圖片

#### Scenario: 有鑽石數量時清單顯示鑽石
- **WHEN** `_feed_counters["鑽石"]` > 0 且玩家開啟切換飼料對話框
- **THEN** 飼料清單中包含「鑽石」選項並顯示數量

#### Scenario: 金條鑽石數量為 0 時不顯示於清單
- **WHEN** 金條或鑽石之 `_feed_counters` 數量為 0（或未在 unlocked_feeds）
- **THEN** 該項目不出現在切換飼料清單中（或依既有解鎖邏輯不顯示）

### Requirement: 投放金條與鑽石飼料
玩家 SHALL 可選擇金條或鑽石作為當前飼料並在水族箱內投放。投放時 SHALL 扣減對應之 `_feed_counters` 數量；飼料幀 SHALL 從 `resource/money/寶箱怪產物/寶箱怪產物_{金條|鑽石}.png` 載入（單幀）。金條、鑽石之成長度為 0（僅供天使鬥魚變身用，不累積成長度）。

#### Scenario: 選擇金條後投放
- **WHEN** 玩家已選擇金條為當前飼料且金條數量 > 0，並在水族箱可投放區域點擊
- **THEN** 在水族箱中加入一顆金條飼料（單幀圖）
- **AND** `_feed_counters["金條"]` 減少 1

#### Scenario: 選擇鑽石後投放
- **WHEN** 玩家已選擇鑽石為當前飼料且鑽石數量 > 0，並在水族箱可投放區域點擊
- **THEN** 在水族箱中加入一顆鑽石飼料
- **AND** `_feed_counters["鑽石"]` 減少 1
