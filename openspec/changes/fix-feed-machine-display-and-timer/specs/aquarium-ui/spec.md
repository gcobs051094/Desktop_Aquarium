## MODIFIED Requirements

### Requirement: 投食機飼料選擇顯示
投食機選取飼料後 SHALL 在投食機圖片的中下方顯示當前選取的飼料圖片；控制面板右側 SHALL NOT 顯示「投食機飼料」或「未選擇」文字。

#### Scenario: 選取飼料後顯示於投食機
- **WHEN** 使用者在投食機選擇了飼料
- **THEN** 飼料圖片疊加顯示在投食機圖片的中下方
- **AND** 飼料圖片大小由 `FEED_MACHINE_FEED_IMAGE_SIZE` 控制
- **AND** 飼料圖片位置由 `FEED_MACHINE_FEED_IMAGE_OFFSET_X` 和 `FEED_MACHINE_FEED_IMAGE_OFFSET_Y` 調整

#### Scenario: 控制面板不顯示投食機飼料狀態
- **WHEN** 控制面板顯示
- **THEN** 控制面板 SHALL NOT 包含「投食機飼料」標籤
- **AND** 控制面板 SHALL NOT 包含「未選擇」文字

---

## ADDED Requirements

### Requirement: 投食機飼料圖片配置參數
投食機上顯示的飼料圖片 SHALL 可通過 `config.py` 配置參數調整。

#### Scenario: 配置參數定義
- **WHEN** 系統載入配置
- **THEN** `FEED_MACHINE_FEED_IMAGE_SIZE` 控制飼料圖片大小（像素）
- **AND** `FEED_MACHINE_FEED_IMAGE_OFFSET_X` 控制飼料圖片相對於投食機中心的 X 偏移（正值向右，負值向左）
- **AND** `FEED_MACHINE_FEED_IMAGE_OFFSET_Y` 控制飼料圖片相對於投食機底部的 Y 偏移（正值向下，負值向上）
