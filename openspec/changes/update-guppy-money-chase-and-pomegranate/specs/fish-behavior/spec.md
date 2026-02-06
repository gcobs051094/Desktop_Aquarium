## REMOVED Requirements

### Requirement: 鬥魚碰觸孔雀魚時追飼料速度加成
**Reason**: 此加成機制不再需要，簡化遊戲邏輯
**Migration**: 所有相關代碼已移除，無需遷移

## ADDED Requirements

### Requirement: 孔雀魚追金錢行為
孔雀魚 SHALL 每5秒追最近的金錢，追金錢時速度倍率為 2.5（比追飼料更快）。冷卻期間（5秒）不追金錢。

#### Scenario: 孔雀魚每5秒追最近金錢
- **WHEN** 水族箱內存在孔雀魚
- **THEN** 每5秒選擇最近的金錢作為目標
- **AND** 排除已收集、已石榴化、已觸底的金錢

#### Scenario: 孔雀魚追金錢速度更快
- **WHEN** 孔雀魚正在追金錢
- **THEN** 移動速度倍率為 2.5（比追飼料時的倍率更快）

#### Scenario: 冷卻期間不追金錢
- **WHEN** 孔雀魚成功轉換金錢為石榴結晶
- **THEN** 5秒內不再追任何金錢
- **AND** 當前追蹤目標被清除

### Requirement: 孔雀魚碰觸金錢轉換為石榴結晶
孔雀魚 SHALL 在碰觸金錢時，依配置機率將該金錢轉換為石榴結晶（紅色色調）。轉換後原金錢消失。

#### Scenario: 成功轉換為石榴結晶
- **WHEN** 孔雀魚碰觸到金錢（矩形相交）
- **AND** 隨機數 < `GUPPY_MONEY_TRANSFORM_CHANCE`（預設1.0）
- **THEN** 原金錢消失（播放消失動畫）
- **AND** 在原位置創建新的石榴結晶金錢（紅色色調，名稱格式「石榴結晶_<原金錢名>」）
- **AND** 設定5秒冷卻時間

#### Scenario: 轉換失敗
- **WHEN** 孔雀魚碰觸到金錢
- **AND** 隨機數 >= `GUPPY_MONEY_TRANSFORM_CHANCE`
- **THEN** 原金錢消失（播放消失動畫）
- **AND** 不創建石榴結晶
- **AND** 不設定冷卻時間

#### Scenario: 已石榴化金錢不被轉換
- **WHEN** 金錢名稱以「石榴結晶_」開頭
- **THEN** 孔雀魚不會追該金錢
- **AND** 不會碰觸該金錢

#### Scenario: 已觸底金錢不被追
- **WHEN** 金錢已觸底（`bottom_time >= 0`）
- **THEN** 孔雀魚不會追該金錢
