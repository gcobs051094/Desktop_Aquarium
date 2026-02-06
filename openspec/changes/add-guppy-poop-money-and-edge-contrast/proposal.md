# Change: Guppy 大便金錢機制與金錢素材邊緣對比

## Why
1. **遊戲經濟與回饋**：希望中、大型 guppy 能產出可拾取的金錢，增加成長回饋與互動。
2. **視覺辨識**：金錢素材（魚大便）在水族箱中需要更明顯的輪廓，以便玩家辨識與點擊拾取。

## What Changes
- **Guppy 大便行為**：中 guppy 每 10 秒排出銅幣（copper_coin）、大 guppy 每 15 秒排出金幣（gold_coin）；素材來自 `resource/money`，對應表置於 `config.py`（`GUPPY_POOP_CONFIG`、`MONEY_VALUE`）。
- **金錢物件**：金錢與飼料相同落下速度與連續動畫，可點擊拾取；銅幣 $10、金幣 $20，並在控制面板顯示金錢計數器。
- **金錢素材視覺**：載入金錢幀時對「最外圍非透明像素」加深顏色，增加對比，便於辨識。

## Impact
- Affected specs: game-economy（新建）
- Affected code: `config.py`, `fish.py`, `aquarium_window.py`
