# Change: 金錢類物品與寶箱怪產物消失動畫

## Why
當玩家點擊或滑鼠移動到金錢類物品（銅幣/銀幣/金幣/魚翅/金心幣等）或寶箱怪產物時，目前是立即消失，缺乏視覺回饋。添加消失動畫可以：
1. **提升視覺體驗**：提供流暢的收集動畫，讓玩家清楚看到物品被收集
2. **改善遊戲感受**：動畫效果讓收集更有成就感
3. **可配置性**：動畫參數開放至 `config.py`，方便調整持續時間與速度

## What Changes
- **金錢類物品消失動畫**：當金錢類物品被收集時（點擊或滑鼠移動觸發），播放消失動畫：
  - 如果該物品有動畫，動畫加速播放（倍率可配置）
  - 物品往上移動並逐漸淡出
  - 動畫持續時間可配置（預設 2 秒）
  - 動畫結束後才從列表移除
- **寶箱怪產物消失動畫**：當寶箱怪產物被點擊收集時，播放類似的消失動畫（往上移動、淡出）
- **配置參數**：在 `config.py` 新增 `MONEY_COLLECT_ANIMATION_DURATION_SEC`（持續時間）、`MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER`（動畫加速倍率）、`MONEY_COLLECT_VELOCITY_Y`（往上移動速度）

## Impact
- **受影響能力**：遊戲經濟（game-economy）
- **受影響代碼**：
  - `config.py`：新增消失動畫配置參數
  - `aquarium_window.py`：`Money` 類添加消失動畫狀態與邏輯，修改 `try_collect_money_at()` 和 `mouseMoveEvent()` 觸發動畫
  - `pet.py`：`ChestMonsterPet` 類添加產物消失動畫狀態與邏輯，修改 `try_collect_chest_produce_at()` 觸發動畫
