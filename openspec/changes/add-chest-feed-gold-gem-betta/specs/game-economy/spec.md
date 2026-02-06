## ADDED Requirements

### Requirement: 寶箱怪金條鑽石拾取改為飼料
系統 SHALL 將寶箱怪產出的**金條、鑽石**視為「飼料類」產物：玩家拾取金條或鑽石時，不增加總金額；改為將該產物數量加入飼料計數器（`_feed_counters`），並在切換飼料清單中顯示金條、鑽石供選擇與投餵。珍珠等其他寶箱怪產物拾取時仍依 `MONEY_VALUE` 增加總金額。

#### Scenario: 拾取金條不增加總金額
- **WHEN** 玩家在水族箱內點擊位置落在寶箱怪產出的金條上並完成拾取
- **THEN** 總金額不變
- **AND** `_feed_counters["金條"]` 增加 1
- **AND** 金條出現在切換飼料清單中（若尚未在 `_unlocked_feeds` 則加入）

#### Scenario: 拾取鑽石不增加總金額
- **WHEN** 玩家在水族箱內點擊位置落在寶箱怪產出的鑽石上並完成拾取
- **THEN** 總金額不變
- **AND** `_feed_counters["鑽石"]` 增加 1
- **AND** 鑽石出現在切換飼料清單中

#### Scenario: 拾取珍珠仍增加總金額
- **WHEN** 玩家拾取寶箱怪產出的珍珠
- **THEN** 依 `MONEY_VALUE["珍珠"]` 增加總金額（$500）

### Requirement: 金錐體與藍寶石價值與大便產出
金錐體、藍寶石 SHALL 於 `config.MONEY_VALUE` 中定義價值：金錐體 1000、藍寶石 1500。金鬥魚（`stage == "golden"`）大便產出金錐體，寶石鬥魚（`stage == "gem"`）大便產出藍寶石；產出資源路徑為 `resource/money/金錐體`、`resource/money/藍寶石`。點擊拾取時依 `MONEY_VALUE` 增加對應金額。

#### Scenario: 金鬥魚大便產出金錐體
- **WHEN** 金鬥魚（鬥魚、stage golden）大便計時觸發
- **THEN** 在水族箱中產生金錐體金錢物件（`_on_fish_poop("金錐體", position)`）
- **AND** 大便間隔為 50～60 秒（`BETTA_POOP_CONFIG["golden_鬥魚"]`）

#### Scenario: 寶石鬥魚大便產出藍寶石
- **WHEN** 寶石鬥魚（鬥魚、stage gem）大便計時觸發
- **THEN** 在水族箱中產生藍寶石金錢物件（`_on_fish_poop("藍寶石", position)`）
- **AND** 大便間隔為 50～60 秒（`BETTA_POOP_CONFIG["gem_鬥魚"]`）

#### Scenario: 拾取金錐體與藍寶石增加金額
- **WHEN** 玩家拾取金錐體或藍寶石
- **THEN** 依 `MONEY_VALUE` 增加對應金額（金錐體 $1000、藍寶石 $1500）

## MODIFIED Requirements

### Requirement: 寶箱怪產物價值
珍珠、金條、鑽石 SHALL 於 `config.MONEY_VALUE` 中定義價值：珍珠 500、金條 1000、鑽石 1500。拾取**珍珠**時依該值增加總金額；拾取**金條、鑽石**時不增加總金額，改為加入飼料計數器並在切換飼料清單中顯示（見「寶箱怪金條鑽石拾取改為飼料」需求）。

#### Scenario: 拾取寶箱怪產物珍珠
- **WHEN** 玩家拾取寶箱怪產出之珍珠
- **THEN** 依 `MONEY_VALUE` 增加 $500 總金額

#### Scenario: 拾取寶箱怪產物金條或鑽石
- **WHEN** 玩家拾取寶箱怪產出之金條或鑽石
- **THEN** 不增加總金額；該產物數量加入飼料計數器並在切換飼料清單中顯示
