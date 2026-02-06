## ADDED Requirements

### Requirement: 投食機點擊選擇飼料
投食機解鎖後，使用者 SHALL 可以點擊投食機圖片彈出對話框選擇已解鎖的飼料，選擇後在控制面板下方顯示選取的飼料圖示。

#### Scenario: 點擊投食機選擇飼料
- **WHEN** 投食機已解鎖且使用者點擊投食機圖片
- **THEN** 彈出選擇飼料對話框
- **AND** 對話框顯示所有已解鎖的飼料（含圖示和數量）
- **AND** 使用者選擇飼料後，控制面板下方顯示該飼料的圖示和名稱

### Requirement: 投食機自動投食
投食機選擇飼料後，SHALL 每隔配置的秒數自動投放一次飼料，每次投放 5~10 顆（隨機），飼料以拋物線軌跡從投食機出口投出。

#### Scenario: 自動投食觸發
- **WHEN** 投食機已選擇飼料且該飼料可用（已解鎖且有數量或為便宜飼料）
- **THEN** 每隔 `FEED_MACHINE_INTERVAL_SEC` 秒自動投放一次
- **AND** 每次投放 5~10 顆飼料（隨機）
- **AND** 扣除對應的飼料數量（便宜飼料除外）

#### Scenario: 拋物線軌跡
- **WHEN** 投食機發射飼料
- **THEN** 飼料從投食機出口位置開始
- **AND** 以拋物線軌跡移動到目標位置
- **AND** 到達目標位置後切換為正常下落（與手動投放的飼料相同）

### Requirement: 投食機位置配置
投食機發射飼料的起始位置和落點位置 SHALL 可通過配置參數控制。

#### Scenario: 起始位置配置
- **WHEN** `FEED_MACHINE_EXIT_X_RATIO` 不為 None
- **THEN** 起始 x 位置 = 水族箱左邊緣 + 水族箱寬度 × `FEED_MACHINE_EXIT_X_RATIO`
- **WHEN** `FEED_MACHINE_EXIT_X_RATIO` 為 None
- **THEN** 起始 x 位置 = 投食機右側 + `FEED_MACHINE_EXIT_X_OFFSET`

#### Scenario: 落點位置配置
- **WHEN** 投食機發射飼料
- **THEN** 落點 x 位置在 `FEED_MACHINE_TARGET_X_MIN_RATIO` 到 `FEED_MACHINE_TARGET_X_MAX_RATIO` 之間（相對於水族箱寬度）
- **AND** 落點 y 位置在水族箱可游動範圍內（隨機）

## MODIFIED Requirements

### Requirement: 大便行為間隔優化
各階段鬥魚的大便間隔 SHALL 使用範圍值而非固定值，每次大便後重新隨機選擇間隔時間，避免同時大便造成卡頓。

#### Scenario: 範圍間隔大便
- **WHEN** 魚類初始化時
- **THEN** 根據 `BETTA_POOP_CONFIG` 中的範圍值隨機選擇一個間隔時間
- **AND** 每次大便後重新隨機選擇間隔時間
- **AND** 各階段範圍：
  - 幼鬥魚：5~10秒
  - 中鬥魚：10~15秒
  - 成年鬥魚：15~20秒
  - 天使鬥魚：25~30秒
