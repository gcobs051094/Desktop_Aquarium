## ADDED Requirements

### Requirement: 商店魚種配置
系統 SHALL 在 `config.py` 中提供 `FISH_SHOP_CONFIG`，定義僅在商店「魚種」tab 販售之魚種；該等魚種 SHALL 不出現在「投放魚」清單中。每筆魚種配置欄位與寵物一致：解鎖條件（unlock_species／unlock_count 或 unlock_money）、描述（description）、購買時條件（require_species／require_count 犧牲魚，或 purchase_money 消耗金幣）。

#### Scenario: FISH_SHOP_CONFIG 定義
- **WHEN** 系統載入商店魚種配置
- **THEN** `config.FISH_SHOP_CONFIG` 包含孔雀魚、鯊魚等僅在商店販售之魚種
- **AND** 孔雀魚配置包含：unlock_species（如 angel_鬥魚）、unlock_count（5）、require_species、require_count（1）、description
- **AND** 鯊魚配置包含：unlock_money（0 表示無需解鎖）、purchase_money（3000）、description

#### Scenario: 投放魚清單排除商店魚種
- **WHEN** 系統建立投放魚清單
- **THEN** 凡其魚種名稱存在於 `FISH_SHOP_CONFIG` 鍵值者，不列入清單
- **AND** 孔雀魚、鯊魚不出現在投放魚按鈕之選單中

#### Scenario: 魚種購買條件檢查
- **WHEN** 玩家於商店點擊魚種「購買」
- **THEN** 系統依 `FISH_SHOP_CONFIG` 檢查解鎖條件（魚種最大數量或金幣）
- **AND** 若已解鎖，再檢查購買當下條件：require_species／require_count 時檢查水族箱內該魚種數量；purchase_money 時檢查金幣是否足夠
- **AND** 通過後扣除金幣或移除犧牲魚，並在水族箱新增一隻該魚種（small 階段）
