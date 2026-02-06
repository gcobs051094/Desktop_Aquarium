## ADDED Requirements

### Requirement: 寵物配置
系統 SHALL 在 `config.py` 中定義寵物配置，包括解鎖條件和召喚條件。

#### Scenario: 寵物配置定義
- **WHEN** 系統載入寵物配置
- **THEN** `config.PET_CONFIG` 包含所有寵物的配置資訊
- **AND** 每個寵物配置包含：unlock_species（解鎖用魚種）、unlock_count（解鎖所需數量）、require_species（召喚時需要的魚種，可為 None）、require_count（召喚時需要的數量）
- **AND** 龍蝦寵物配置為：unlock_species="large_guppy", unlock_count=5, require_species=None, require_count=0

### Requirement: 寵物解鎖追蹤
系統 SHALL 追蹤寵物的解鎖狀態，基於魚種的最大數量記錄。

#### Scenario: 解鎖狀態判定
- **WHEN** 系統檢查寵物是否已解鎖
- **THEN** 根據 `_unlocked_species` 中對應魚種的 `max_count_reached` 與 `PET_CONFIG` 中的解鎖條件比較
- **AND** 若 `max_count_reached >= unlock_count`，則寵物已解鎖
