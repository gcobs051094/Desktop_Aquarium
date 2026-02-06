# Change: 寶箱怪金條鑽石改為飼料、天使鬥魚變身金鬥魚與寶石鬥魚

## Why
1. **經濟與玩法分流**：拾取寶箱怪產出的金條、鑽石時不增加總金額，改為加入飼料清單，讓玩家可選擇投餵給天使鬥魚，形成「產物→飼料→變身」的玩法鏈。
2. **鬥魚型態擴充**：天使鬥魚吃金條變身金鬥魚、吃鑽石變身寶石鬥魚；金鬥魚與寶石鬥魚大便產出高價值金錐體、藍寶石，且只吃一般飼料，不再吃金條/鑽石/金錐體/藍寶石，豐富鬥魚階段與經濟回饋。

## What Changes
- **寶箱怪拾取行為**：拾取寶箱怪產出的**金條、鑽石**時，不增加總金額；改為將該產物數量加入飼料計數器（`_feed_counters`），並在「切換飼料」清單中顯示金條、鑽石供選擇與投餵。拾取**珍珠**仍依 `MONEY_VALUE` 增加總金額。
- **飼料清單與投放**：金條、鑽石納入飼料系統（`FEED_GROWTH_POINTS`、`FEED_UNLOCK_CONFIG` 等）；解鎖條件為「有數量」（`unlock_by: "chest_feed_count"`）。飼料選單顯示金條/鑽石時使用 `resource/money/寶箱怪產物/寶箱怪產物_金條.png`、`寶箱怪產物_鑽石.png` 作為預覽與投餵幀。
- **天使鬥魚吃金條/鑽石變身**：僅**天使鬥魚**（`species == "鬥魚"` 且 `stage == "angel"`）會吃投餵的金條、鑽石；吃金條後變身為**金鬥魚**（`stage == "golden"`），吃鑽石後變身為**寶石鬥魚**（`stage == "gem"`）。金鬥魚、寶石鬥魚**不吃**金條、鑽石、金錐體、藍寶石，僅吃一般飼料。
- **金鬥魚與寶石鬥魚大便**：金鬥魚大便產出**金錐體**（`resource/money/金錐體`），寶石鬥魚大便產出**藍寶石**（`resource/money/藍寶石`）；大便間隔皆為 50～60 秒（`BETTA_POOP_CONFIG`）。金錐體價值 1000、藍寶石價值 1500（`MONEY_VALUE`）。
- **配置與資源**：`config.py` 新增 `CHEST_FEED_ITEMS`、金錐體/藍寶石之 `MONEY_VALUE`、`BETTA_POOP_CONFIG`（`golden_鬥魚`、`gem_鬥魚`）、`FISH_SCALE_BY_STAGE_SPECIES`（金鬥魚、寶石鬥魚）；鬥魚階段目錄對應新增 `golden`→金鬥魚、`gem`→寶石鬥魚；存檔/讀檔支援金條/鑽石飼料數量與金鬥魚/寶石鬥魚階段。

## Impact
- Affected specs: game-economy, fish-behavior, aquarium-ui
- Affected code:
  - `config.py`：`CHEST_FEED_ITEMS`、`MONEY_VALUE`（金錐體、藍寶石）、`BETTA_POOP_CONFIG`、`FEED_*`（金條、鑽石）、`FISH_SCALE_BY_STAGE_SPECIES`（golden_鬥魚、gem_鬥魚）
  - `aquarium_window.py`：寶箱怪拾取回傳 `(產物類型, 金額)`；金條/鑽石拾取改為增加飼料計數；飼料清單與投放支援金條/鑽石；`_check_feed_collisions` 僅天使鬥魚吃金條/鑽石並變身；`_create_upgraded_fish`、`_load_game_state` 支援 golden/gem 階段
  - 存檔：`feed_counters`、`unlocked_feeds` 已涵蓋金條/鑽石
