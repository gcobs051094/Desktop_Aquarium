## MODIFIED Requirements

### Requirement: 金錢拾取與計數
玩家 SHALL 可透過點擊或滑鼠移動到金錢物件進行拾取；拾取時 SHALL 播放消失動畫（動畫加速、往上移動、逐漸淡出），動畫結束後 SHALL 依 `config.MONEY_VALUE` 增加金錢總額，並在介面上顯示當前金錢。消失動畫參數（持續時間、動畫加速倍率、往上移動速度）SHALL 可在 `config.py` 中配置。

#### Scenario: 點擊拾取金錢並播放消失動畫
- **WHEN** 玩家在水族箱內點擊位置落在某金錢物件的顯示範圍內
- **THEN** 該金錢開始播放消失動畫（如果該物品有動畫，動畫加速播放；物品往上移動並逐漸淡出）
- **AND** 動畫持續時間由 `MONEY_COLLECT_ANIMATION_DURATION_SEC` 配置（預設 2 秒）
- **AND** 動畫結束後該金錢被移除並依其類型增加對應金額
- **AND** 控制面板上之金錢計數器更新為當前總額

#### Scenario: 滑鼠移動拾取金錢並播放消失動畫
- **WHEN** 玩家滑鼠移動到某金錢物件的顯示範圍內
- **THEN** 該金錢開始播放消失動畫（如果該物品有動畫，動畫加速播放；物品往上移動並逐漸淡出）
- **AND** 動畫持續時間由 `MONEY_COLLECT_ANIMATION_DURATION_SEC` 配置（預設 2 秒）
- **AND** 動畫結束後該金錢被移除並依其類型增加對應金額
- **AND** 控制面板上之金錢計數器更新為當前總額

#### Scenario: 消失動畫參數可配置
- **WHEN** 系統載入配置
- **THEN** `MONEY_COLLECT_ANIMATION_DURATION_SEC` 控制消失動畫持續時間（秒）
- **AND** `MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER` 控制動畫加速倍率（金錢類物品有動畫時）
- **AND** `MONEY_COLLECT_VELOCITY_Y` 控制往上移動速度（像素/幀，負值表示往上）

## ADDED Requirements

### Requirement: 寶箱怪產物消失動畫
當玩家點擊寶箱怪產物進行拾取時，SHALL 播放消失動畫（往上移動、逐漸淡出），動畫結束後 SHALL 重置寶箱怪並依產物類型增加對應金額。消失動畫參數（持續時間、往上移動速度）SHALL 與金錢類物品共用配置。

#### Scenario: 點擊拾取寶箱怪產物並播放消失動畫
- **WHEN** 玩家在水族箱內點擊位置落在寶箱怪產物的顯示範圍內
- **THEN** 該產物開始播放消失動畫（往上移動並逐漸淡出）
- **AND** 動畫持續時間由 `MONEY_COLLECT_ANIMATION_DURATION_SEC` 配置（預設 2 秒）
- **AND** 動畫結束後寶箱怪重置為關閉狀態並重新計時
- **AND** 依產物類型增加對應金額（珍珠 $500、金條 $1000、鑽石 $1500）
- **AND** 控制面板上之金錢計數器更新為當前總額
