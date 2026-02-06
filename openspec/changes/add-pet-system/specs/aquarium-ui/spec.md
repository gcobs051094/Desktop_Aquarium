## MODIFIED Requirements

### Requirement: 商店商品顯示
商店覆蓋視窗 SHALL 顯示可購買的商品，包括魚種和寵物。商品 SHALL 顯示解鎖狀態、解鎖條件和購買按鈕。

#### Scenario: 寵物商品顯示
- **WHEN** 商店覆蓋視窗顯示
- **THEN** 商店中顯示寵物商品列表
- **AND** 每個寵物商品顯示預覽圖、名稱、解鎖條件說明
- **AND** 未解鎖的寵物顯示為鎖定狀態，已解鎖的寵物顯示為可購買狀態

#### Scenario: 寵物解鎖條件檢查
- **WHEN** 系統檢查寵物是否已解鎖
- **THEN** 根據 `config.PET_CONFIG` 中的解鎖條件（unlock_species、unlock_count）檢查
- **AND** 檢查 `_unlocked_species` 中對應魚種的最大數量是否達到解鎖條件
- **AND** 龍蝦寵物需要 5 隻 large_guppy 解鎖

#### Scenario: 寵物購買與召喚
- **WHEN** 使用者點擊已解鎖寵物的購買按鈕
- **THEN** 系統檢查該寵物是否已存在於水族箱中
- **AND** 若不存在，則召喚該寵物到水族箱底部
- **AND** 若已存在，則不執行任何操作（或顯示提示）
- **AND** 龍蝦寵物不需要犧牲魚即可召喚（require_species=None, require_count=0）
