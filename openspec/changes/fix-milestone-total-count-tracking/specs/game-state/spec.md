## MODIFIED Requirements

### Requirement: 解鎖狀態追蹤
系統 SHALL 追蹤使用者曾經達到過的魚種數量里程碑，用於判斷魚種是否已解鎖。里程碑資料包括：
- `max_count_reached`：同時存在的最大數量
- `total_count_reached`：累計曾達到過該階段的魚數量（每次有魚升級到該階段時 +1）
- `unlocked`：是否已解鎖

#### Scenario: 記錄魚種最大數量
- **WHEN** 水族箱內某魚種的數量達到新的最大值時
- **THEN** 系統更新該魚種的 `max_count_reached` 記錄

#### Scenario: 記錄累計達到總數
- **WHEN** 有魚升級到某階段（如 small → medium、medium → large、large → angel）時
- **THEN** 系統將該階段的 `total_count_reached` 累加 +1
- **AND** 此累計值不會因為魚繼續升級或離開而減少

#### Scenario: 解鎖狀態判定
- **WHEN** 檢查魚種是否達到解鎖條件時
- **THEN** 系統使用 `max(total_count_reached, max_count_reached)` 作為有效計數
- **AND** 若有效計數 >= 解鎖所需數量，則判定為可解鎖

#### Scenario: 解鎖狀態持久化
- **WHEN** 儲存遊戲狀態時
- **THEN** 系統將所有魚種的解鎖狀態（包括 `max_count_reached`、`total_count_reached` 和 `unlocked`）寫入存檔

#### Scenario: 向後兼容舊存檔
- **WHEN** 載入不含 `total_count_reached` 欄位的舊存檔時
- **THEN** 系統根據現有魚類數量推斷累計總數
- **AND** 若有天使鬥魚，推斷曾經有過至少相同數量的成年鬥魚（因天使鬥魚由成年鬥魚升級而來）
