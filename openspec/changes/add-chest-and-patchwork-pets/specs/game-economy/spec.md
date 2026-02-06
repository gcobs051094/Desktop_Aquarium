## ADDED Requirements

### Requirement: 寵物金幣解鎖
系統 SHALL 支援寵物以「金幣解鎖」：`PET_CONFIG` 中可選欄位 `unlock_money`；若設定則解鎖條件為「當前金幣 ≥ unlock_money」且玩家點擊購買時扣款 `unlock_money` 並標記該寵物已解鎖，之後可免費召喚。若寵物同時具 `unlock_money` 與 `unlock_species`，以 `unlock_money` 優先（或僅擇一使用）。

#### Scenario: 寶箱怪 2000 金幣解鎖
- **WHEN** 玩家金幣 ≥ 2000 且點擊購買寶箱怪
- **THEN** 扣款 2000 金幣並標記寶箱怪已解鎖
- **AND** 之後可免費召喚寶箱怪

#### Scenario: 拼布魚 3500 金幣解鎖
- **WHEN** 玩家金幣 ≥ 3500 且點擊購買拼布魚
- **THEN** 扣款 3500 金幣並標記拼布魚已解鎖
- **AND** 之後可免費召喚拼布魚

### Requirement: 寶箱怪產物價值
珍珠、金條、鑽石 SHALL 於 `config.MONEY_VALUE` 中定義價值：珍珠 500、金條 1000、鑽石 1500；拾取時依該值增加總金額。

#### Scenario: 拾取寶箱怪產物
- **WHEN** 玩家拾取寶箱怪產出之珍珠/金條/鑽石
- **THEN** 依 `MONEY_VALUE` 增加對應金額（珍珠 $500、金條 $1000、鑽石 $1500）
- **AND** 控制面板金錢計數器更新

## MODIFIED Requirements

### Requirement: 寵物配置
系統 SHALL 在 `config.py` 中定義寵物配置，包括解鎖條件和召喚條件。

#### Scenario: 寵物配置定義
- **WHEN** 系統載入寵物配置
- **THEN** `config.PET_CONFIG` 包含所有寵物的配置資訊
- **AND** 每個寵物配置可包含：unlock_species（解鎖用魚種）、unlock_count（解鎖所需數量）、或 **unlock_money**（解鎖所需金幣，一次性扣款解鎖）
- **AND** 龍蝦寵物配置為：unlock_species="large_鬥魚", unlock_count=5
- **AND** 寶箱怪配置為：unlock_money=2000
- **AND** 拼布魚配置為：unlock_money=3500
