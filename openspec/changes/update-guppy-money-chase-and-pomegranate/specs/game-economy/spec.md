## ADDED Requirements

### Requirement: 石榴結晶價值倍率
石榴結晶金錢 SHALL 拾取價值為原金錢的 1.5 倍。

#### Scenario: 石榴結晶拾取價值
- **WHEN** 玩家拾取名稱格式為「石榴結晶_<原金錢名>」的金錢
- **THEN** 獲得金額為 `MONEY_VALUE[原金錢名] * 1.5`

### Requirement: 投放幼鬥魚費用
投放一隻幼鬥魚 SHALL 需要花費 20 元。

#### Scenario: 投放幼鬥魚扣除費用
- **WHEN** 玩家從投放魚清單選擇「鬥魚」
- **AND** 當前金幣 >= 20
- **THEN** 扣除 20 元
- **AND** 在水族箱新增一隻幼鬥魚

#### Scenario: 金幣不足無法投放
- **WHEN** 玩家從投放魚清單選擇「鬥魚」
- **AND** 當前金幣 < 20
- **THEN** 不扣除金幣
- **AND** 不在水族箱新增魚
- **AND** 輸出提示訊息

#### Scenario: 投放魚清單顯示費用
- **WHEN** 投放魚清單顯示「鬥魚」項目
- **THEN** 顯示為「鬥魚 (花費20$)」

## MODIFIED Requirements

### Requirement: 孔雀魚行為
孔雀魚 SHALL 不進食、不追飼料；每5秒追最近的金錢，碰觸後依機率轉換為石榴結晶。

#### Scenario: 孔雀魚不進食不追飼料
- **WHEN** 魚種為孔雀魚（`species == "孔雀魚"`）且 `Fish.update()` 被呼叫
- **THEN** `targets` 設為 `None`（不追飼料）
- **AND** 碰撞檢測跳過孔雀魚的吃飼料邏輯

#### Scenario: 孔雀魚追金錢
- **WHEN** 魚種為孔雀魚且 `Fish.update()` 被呼叫
- **AND** 傳入 `moneys` 列表
- **THEN** 每5秒選擇最近的金錢作為目標
- **AND** 追金錢時速度倍率為 2.5
