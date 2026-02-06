## ADDED Requirements

### Requirement: Guppy 第四成長階段（angel_guppy）
Guppy SHALL 具備第四成長階段 `angel`（angel_guppy）；當 large_guppy 之成長度達到 `config.py` 中 `FISH_UPGRADE_THRESHOLDS["guppy"]["large"]` 所定義之閾值（100）時，SHALL 升級為 angel_guppy。

#### Scenario: large_guppy 成長度達 100 升級為 angel_guppy
- **WHEN** 水族箱內存在階段為 large 之 guppy，且其成長度達到 100
- **THEN** 該魚升級為階段 angel（angel_guppy）
- **AND** 升級後使用 `resource/fish/guppy/angel` 或 `resource/fish/guppy/angel_guppy` 之動畫素材

## MODIFIED Requirements

### Requirement: Guppy 大便金錢行為
中、大、天使型 guppy SHALL 依設定間隔自動排出金錢類素材；對應關係與間隔 SHALL 由 `config.py` 之 `GUPPY_POOP_CONFIG` 定義。

#### Scenario: 中 guppy 排出銅幣
- **WHEN** 水族箱內存在階段為 medium 之 guppy
- **THEN** 每經過 10 秒在該魚當前位置產生一個 copper_coin 金錢物件
- **AND** 金錢素材來自 `resource/money/copper_coin`

#### Scenario: 大 guppy 排出金幣
- **WHEN** 水族箱內存在階段為 large 之 guppy
- **THEN** 每經過 15 秒在該魚當前位置產生一個 gold_coin 金錢物件
- **AND** 金錢素材來自 `resource/money/gold_coin`

#### Scenario: 天使 guppy 排出愛心幣
- **WHEN** 水族箱內存在階段為 angel 之 guppy
- **THEN** 每經過 20 秒在該魚當前位置產生一個 heart_coin 金錢物件
- **AND** 金錢素材來自 `resource/money/heart_coin`

### Requirement: 金錢拾取與計數
玩家 SHALL 可透過點擊金錢物件進行拾取；拾取後 SHALL 依 `config.MONEY_VALUE` 增加金錢總額，並在介面上顯示當前金錢。

#### Scenario: 點擊拾取金錢
- **WHEN** 玩家在水族箱內點擊位置落在某金錢物件的顯示範圍內
- **THEN** 該金錢被移除並依其類型增加對應金額（copper_coin $10，gold_coin $20，heart_coin $500）
- **AND** 控制面板上之金錢計數器更新為當前總額

#### Scenario: 點擊優先拾取金錢
- **WHEN** 玩家點擊位置同時可能對應金錢或投放飼料
- **THEN** 若該位置有金錢則僅處理拾取金錢，不投放飼料
- **AND** 若該位置無金錢則依現有邏輯投放飼料
