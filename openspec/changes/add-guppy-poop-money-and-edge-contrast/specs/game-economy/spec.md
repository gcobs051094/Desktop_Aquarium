## ADDED Requirements

### Requirement: Guppy 大便金錢行為
中、大型 guppy SHALL 依設定間隔自動排出金錢類素材；對應關係與間隔 SHALL 由 `config.py` 之 `GUPPY_POOP_CONFIG` 定義。

#### Scenario: 中 guppy 排出銅幣
- **WHEN** 水族箱內存在階段為 medium 之 guppy
- **THEN** 每經過 10 秒在該魚當前位置產生一個 copper_coin 金錢物件
- **AND** 金錢素材來自 `resource/money/copper_coin`

#### Scenario: 大 guppy 排出金幣
- **WHEN** 水族箱內存在階段為 large 之 guppy
- **THEN** 每經過 15 秒在該魚當前位置產生一個 gold_coin 金錢物件
- **AND** 金錢素材來自 `resource/money/gold_coin`

### Requirement: 金錢物件落下與動畫
金錢物件 SHALL 以與飼料相同之落下速度與連續動畫方式呈現，並在觸底或過期後移除。

#### Scenario: 金錢落下與動畫
- **WHEN** 金錢物件存在於水族箱中
- **THEN** 該物件以與飼料相同之落下速度（像素/幀）向下移動
- **AND** 使用 `resource/money/{money_type}` 內之連續幀播放動畫

### Requirement: 金錢拾取與計數
玩家 SHALL 可透過點擊金錢物件進行拾取；拾取後 SHALL 依 `config.MONEY_VALUE` 增加金錢總額，並在介面上顯示當前金錢。

#### Scenario: 點擊拾取金錢
- **WHEN** 玩家在水族箱內點擊位置落在某金錢物件的顯示範圍內
- **THEN** 該金錢被移除並依其類型增加對應金額（copper_coin $10，gold_coin $20）
- **AND** 控制面板上之金錢計數器更新為當前總額

#### Scenario: 點擊優先拾取金錢
- **WHEN** 玩家點擊位置同時可能對應金錢或投放飼料
- **THEN** 若該位置有金錢則僅處理拾取金錢，不投放飼料
- **AND** 若該位置無金錢則依現有邏輯投放飼料

### Requirement: 金錢素材邊緣對比
載入金錢動畫幀時，系統 SHALL 對最外圍非透明像素加深顏色以增加對比，便於玩家辨識與點擊。

#### Scenario: 邊緣像素加深
- **WHEN** 系統從 `resource/money/{money_type}` 載入金錢幀
- **THEN** 對每張幀中「非透明且至少有一鄰點為透明或越界」的像素進行顏色加深（例如 RGB 乘以一固定係數，alpha 不變）
- **AND** 加深後之幀用於金錢物件的顯示
