## MODIFIED Requirements

### Requirement: 鬥魚大便金錢行為
中、大、天使型鬥魚 SHALL 依設定間隔自動排出金錢類素材；對應關係與間隔 SHALL 由 `config.py` 之 `BETTA_POOP_CONFIG` 定義。

#### Scenario: 幼鬥魚排出銅幣
- **WHEN** 水族箱內存在階段為 small 之鬥魚（species="鬥魚"）
- **THEN** 每經過 5 秒在該魚當前位置產生一個銅幣金錢物件
- **AND** 金錢素材來自 `resource/money/銅幣`

#### Scenario: 中鬥魚排出銀幣
- **WHEN** 水族箱內存在階段為 medium 之鬥魚（species="鬥魚"）
- **THEN** 每經過 10 秒在該魚當前位置產生一個銀幣金錢物件
- **AND** 金錢素材來自 `resource/money/銀幣`

#### Scenario: 成年鬥魚排出金幣
- **WHEN** 水族箱內存在階段為 large 之鬥魚（species="鬥魚"）
- **THEN** 每經過 15 秒在該魚當前位置產生一個金幣金錢物件
- **AND** 金錢素材來自 `resource/money/金幣`

#### Scenario: 天使鬥魚排出金心幣
- **WHEN** 水族箱內存在階段為 angel 之鬥魚（species="鬥魚"）
- **THEN** 每經過 30 秒在該魚當前位置產生一個金心幣金錢物件
- **AND** 金錢素材來自 `resource/money/金心幣`

### Requirement: 鬥魚成長階段
鬥魚 SHALL 具備成長階段系統；當各階段之成長度達到 `config.py` 中 `FISH_UPGRADE_THRESHOLDS["鬥魚"]` 所定義之閾值時，SHALL 升級至下一階段。

#### Scenario: small_鬥魚 成長度達閾值升級為 medium_鬥魚
- **WHEN** 水族箱內存在階段為 small 之鬥魚（species="鬥魚"），且其成長度達到 `FISH_UPGRADE_THRESHOLDS["鬥魚"]["small"]`（10）
- **THEN** 該魚升級為階段 medium（medium_鬥魚）
- **AND** 升級後使用 `resource/fish/鬥魚/中鬥魚` 之動畫素材

#### Scenario: medium_鬥魚 成長度達閾值升級為 large_鬥魚
- **WHEN** 水族箱內存在階段為 medium 之鬥魚（species="鬥魚"），且其成長度達到 `FISH_UPGRADE_THRESHOLDS["鬥魚"]["medium"]`（30）
- **THEN** 該魚升級為階段 large（large_鬥魚）
- **AND** 升級後使用 `resource/fish/鬥魚/成年鬥魚` 之動畫素材

#### Scenario: large_鬥魚 成長度達閾值升級為 angel_鬥魚
- **WHEN** 水族箱內存在階段為 large 之鬥魚（species="鬥魚"），且其成長度達到 `FISH_UPGRADE_THRESHOLDS["鬥魚"]["large"]`（100）
- **THEN** 該魚升級為階段 angel（angel_鬥魚）
- **AND** 升級後使用 `resource/fish/鬥魚/天使鬥魚` 之動畫素材

### Requirement: 金錢拾取與計數
玩家 SHALL 可透過點擊金錢物件進行拾取；拾取後 SHALL 依 `config.MONEY_VALUE` 增加金錢總額，並在介面上顯示當前金錢。

#### Scenario: 點擊拾取金錢
- **WHEN** 玩家在水族箱內點擊位置落在某金錢物件的顯示範圍內
- **THEN** 該金錢被移除並依其類型增加對應金額（銅幣 $10、銀幣 $15、金幣 $20、金心幣 $500，依 `MONEY_VALUE` 定義）
- **AND** 控制面板上之金錢計數器更新為當前總額

## ADDED Requirements

### Requirement: 投放鬥魚時解析中文階段目錄
系統 SHALL 在投放魚時，若魚種目錄下存在名稱含「幼」或 "small" 的子目錄，則視為 small 階段並載入該目錄動畫；階段名稱 SHALL 支援中文映射（幼→small、中→medium、成年→large、天使→angel），以便鬥魚目錄名「幼鬥魚」等可正確對應階段。

#### Scenario: 選擇鬥魚後投放幼鬥魚
- **WHEN** 使用者從投放魚清單選擇「鬥魚」（目錄 `resource/fish/鬥魚/`）
- **THEN** 系統在該目錄下尋找名稱含「幼」或 "small" 的子目錄（如「幼鬥魚」）
- **AND** 載入該子目錄動畫並在水族箱新增一條 species="鬥魚"、stage="small" 的魚

### Requirement: 存檔載入鬥魚時階段目錄對應
載入存檔時，若魚類之 species 為「鬥魚」，系統 SHALL 依 stage（small/medium/large/angel）對應至資源目錄名（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚），以正確載入該階段動畫並還原魚類。

#### Scenario: 載入存檔後鬥魚正確還原
- **WHEN** 存檔內含 species="鬥魚"、stage="small" 的魚
- **THEN** 系統尋找 `resource/fish/鬥魚/幼鬥魚` 目錄並載入動畫
- **AND** 該魚於水族箱中正確顯示為幼鬥魚

### Requirement: 魚種依階段縮放
系統 SHALL 支援依魚種與階段設定顯示縮放倍率。`config.py` 中 SHALL 提供 `FISH_SCALE_BY_STAGE_SPECIES`（鍵為 `"階段_魚種"`，如 `small_鬥魚`）；`get_fish_scale(species, stage)` SHALL 優先回傳該表中對應值，其次 `FISH_SCALE_BY_SPECIES`，最後 `DEFAULT_FISH_SCALE`。投放魚與升級時 SHALL 使用對應階段之縮放倍率。

#### Scenario: 鬥魚各階段使用設定之縮放
- **WHEN** `FISH_SCALE_BY_STAGE_SPECIES` 中設定 `small_鬥魚`、`medium_鬥魚` 等不同縮放值
- **THEN** 投放幼鬥魚時使用 `get_fish_scale("鬥魚", "small")` 之回傳值
- **AND** 魚升級至中鬥魚時使用 `get_fish_scale("鬥魚", "medium")` 之回傳值

## REMOVED Requirements

### Requirement: Guppy 大便金錢行為
**Reason**: 魚種已從 guppy 改為鬥魚
**Migration**: 所有 guppy 相關配置與代碼引用已更新為鬥魚（species="鬥魚"）

### Requirement: Guppy 成長階段
**Reason**: 魚種已從 guppy 改為鬥魚
**Migration**: 所有 guppy 相關配置與代碼引用已更新為鬥魚（species="鬥魚"）
