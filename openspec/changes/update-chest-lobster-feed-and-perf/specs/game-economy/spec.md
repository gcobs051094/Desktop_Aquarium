## ADDED Requirements

### Requirement: 金錢動畫幀快取
系統 SHALL 對金錢動畫幀載入結果進行快取，以 `money_type`（如「金錐體」「藍寶石」「魚翅」）為鍵。同一 `money_type` 僅在首次需要時從 `resource/money/{money_type}` 載入幀並執行 `_darken_money_edges`，之後產生同類型金錢物件時 SHALL 復用快取之幀列表，避免重複磁碟讀取與像素處理造成卡頓。

#### Scenario: 金鬥魚大便不重載金錐體幀
- **WHEN** 金鬥魚首次大便產出金錐體
- **THEN** 呼叫 `_load_money_frames("金錐體")` 載入並快取
- **WHEN** 金鬥魚或其它來源再次產生金錐體
- **THEN** `_load_money_frames("金錐體")` 回傳快取結果，不重複載入與邊緣加深

#### Scenario: 寶石鬥魚大便不重載藍寶石幀
- **WHEN** 寶石鬥魚首次大便產出藍寶石
- **THEN** 呼叫 `_load_money_frames("藍寶石")` 載入並快取
- **WHEN** 再次產生藍寶石
- **THEN** 回傳快取，不重複 I/O 與 _darken_money_edges
