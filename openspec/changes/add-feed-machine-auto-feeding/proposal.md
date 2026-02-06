# Change: 投食機自動投食功能與大便行為優化

## Why
1. **自動化投食**：投食機解鎖後應提供自動投食功能，減少玩家手動操作，提升遊戲體驗。
2. **視覺效果**：投食機發射飼料應有拋物線軌跡，增加遊戲的視覺趣味性。
3. **性能優化**：當多條魚同時大便時會造成卡頓，需要將大便間隔改為範圍值，分散大便時間。

## What Changes
- **投食機點擊選擇飼料**：
  - 點擊投食機圖片時彈出對話框，顯示已解鎖的飼料供選擇
  - 選擇後在控制面板下方顯示選取的飼料圖示和名稱
- **投食機自動投食**：
  - 選擇飼料後，投食機每隔配置的秒數自動投放一次
  - 每次投放 5~10 顆飼料（隨機）
  - 飼料從投食機出口以拋物線軌跡投出，到達目標位置後切換為正常下落
- **投食機位置配置**：
  - 起始位置和落點位置可通過配置參數控制（x 座標）
  - 支援比例值（相對於水族箱寬度）或偏移值（相對於投食機位置）
- **大便行為優化**：
  - 將大便間隔從固定值改為範圍值
  - 幼鬥魚：5~10秒
  - 中鬥魚：10~15秒
  - 成年鬥魚：15~20秒
  - 天使鬥魚：25~30秒
  - 每次大便後重新隨機選擇間隔時間，避免同時大便造成卡頓

## Impact
- **受影響能力**：水族箱使用者介面（aquarium-ui）、遊戲經濟（game-economy）、魚類行為（fish-behavior）
- **受影響代碼**：
  - `config.py`：
    - 新增 `FEED_MACHINE_INTERVAL_SEC`：投食機自動投食間隔（秒）
    - 新增 `FEED_MACHINE_EXIT_X_RATIO`：投食機出口 x 位置比例（None=自動，0.0~1.0=相對於水族箱寬度）
    - 新增 `FEED_MACHINE_EXIT_X_OFFSET`：投食機出口 x 位置偏移（當 EXIT_X_RATIO 為 None 時使用）
    - 新增 `FEED_MACHINE_TARGET_X_MIN_RATIO`：落點 x 最小位置比例
    - 新增 `FEED_MACHINE_TARGET_X_MAX_RATIO`：落點 x 最大位置比例
    - 修改 `BETTA_POOP_CONFIG`：間隔值從單一數值改為範圍元組 (min, max)
  - `aquarium_window.py`：
    - 新增 `FeedSelectionDialog`：選擇飼料的對話框
    - 修改 `FeedMachineWidget`：添加點擊選擇飼料功能，添加信號 `feed_selected`
    - 修改 `ControlPanel`：添加投食機選取飼料顯示區域
    - 修改 `Feed` 類：支援拋物線軌跡（`is_parabolic`、`target_position` 參數）
    - 新增 `_feed_machine_shoot_feeds()`：投食機發射飼料功能
    - 新增 `_on_feed_machine_feed_selected()`：處理投食機選擇飼料事件
    - 修改 `_on_game_time_updated()`：添加投食機自動投食計時邏輯
  - `fish.py`：
    - 修改 `Fish.__init__()`：支援範圍間隔的大便配置
    - 修改 `Fish.update()`：每次大便後重新隨機選擇間隔時間
