# Change: 新增背景圖片透明度調整功能

## Why
使用者需要能夠調整水族箱背景圖片的透明度，以便：
1. **視覺自訂**：依個人喜好或桌面環境調整背景可見度
2. **桌面整合**：降低背景透明度可讓桌面內容更清晰可見，提升桌面小助手的整合感
3. **視覺層次**：透過透明度控制，使用者可以調整背景與前景（魚、飼料、金錢）的視覺層次

## What Changes
- **背景透明度屬性**：`AquariumWidget` 新增 `background_opacity`（0~100%，預設 80%），在繪製背景時套用透明度
- **透明度控制 UI**：在控制面板新增「背景透明度」標籤與水平滑桿（0~100%，預設 80%），提供刻度標記（0、25、50、75、100）
- **即時更新**：滑桿變動時即時更新背景透明度，標籤顯示當前百分比
- **信號機制**：`ControlPanel` 新增 `background_opacity_changed` 信號，視窗連接此信號以更新水族箱背景透明度

## Impact
- Affected specs: aquarium-ui（修改）
- Affected code: `aquarium_window.py`（`AquariumWidget`、`ControlPanel`、`TransparentAquariumWindow`）
