## MODIFIED Requirements

### Requirement: 投食機飼料扣減時機
投食機 SHALL 僅在實際發射飼料時扣減飼料數量，選擇飼料時 SHALL NOT 扣減數量。

#### Scenario: 選擇飼料不扣減
- **WHEN** 使用者在投食機選擇飼料
- **THEN** 飼料數量 SHALL NOT 減少
- **AND** 投食機顯示選中的飼料圖片

#### Scenario: 發射飼料時扣減
- **WHEN** 投食機自動發射飼料
- **THEN** 若為便宜飼料則不扣減
- **AND** 若為其他飼料則扣減實際發射的數量

---

### Requirement: 飼料計時器載入修復
飼料計時器 SHALL 在載入存檔後正常運作；由於遊戲時間不會被保存，載入存檔時 SHALL 重置所有飼料的計時器記錄。

#### Scenario: 載入存檔後計時器重置
- **WHEN** 載入存檔
- **THEN** 所有已解鎖飼料的 `_feed_counter_last_add` SHALL 重置為當前遊戲時間（0）
- **AND** 飼料計時器 SHALL 從載入時開始正常計時

#### Scenario: 計時器正常增加飼料數量
- **WHEN** 飼料已解鎖且計時器達到間隔時間
- **THEN** 鯉魚飼料每 3 秒數量 +1
- **AND** 藥丸每 5 秒數量 +1
- **AND** 核廢料每 60 秒數量 +1

#### Scenario: 計時器初始化檢查
- **WHEN** 飼料在 `_feed_counter_last_add` 中沒有記錄
- **THEN** SHALL 初始化為當前遊戲時間
- **AND** 避免因 `game_time - last` 為負數導致計時器永不觸發
