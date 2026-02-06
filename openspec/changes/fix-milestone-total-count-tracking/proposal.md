# Change: 修復里程碑累計計數追蹤

## Why
原本的里程碑系統只記錄「同時存在的最大數量」（`max_count_reached`），而不是「累計曾達到過該階段的魚數量」（`total_count_reached`）。當魚快速升級時，`large_鬥魚`（成年鬥魚）存在的時間很短就升級成 `angel_鬥魚`（天使鬥魚），導致里程碑無法累積。例如：飼料投食機需要「曾達到 10 隻 large_鬥魚」才能解鎖，但每次只能計算到 1 隻同時存在的 `large_鬥魚`，而不是累計達到過多少次。

## What Changes
- 新增 `total_count_reached` 欄位追蹤「累計曾達到過該階段的魚數量」
- 每次有魚升級到某階段時，該階段的 `total_count_reached` 累加 +1
- 工具/飼料解鎖判定改用 `max(total_count_reached, max_count_reached)` 來判定（向後兼容舊存檔）
- 商店 UI 顯示「累計 X 隻」而非「目前最多 X 隻」
- 讀檔時根據天使鬥魚數量推斷成年鬥魚累計總數（向後兼容）
- 添加詳細的里程碑追蹤日誌輸出

## Impact
- Affected specs: `game-state`
- Affected code: `aquarium_window.py`（里程碑追蹤邏輯、存讀檔邏輯、商店 UI 顯示）
