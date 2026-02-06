# Change: 修正投食機區域座標系統與滑鼠事件處理

## Why
1. **左側空白區域座標問題**：當 `FEED_MACHINE_AREA_WIDTH` 設定為 150 時，主視窗左側新增了空白區域用於放置投食機，但滑鼠事件處理邏輯未正確處理座標轉換，導致水族箱左半邊無法正常投放飼料。
2. **滑鼠事件處理順序問題**：投食機部件作為透明覆蓋層，其滑鼠事件處理優先於水族箱區域，導致即使點擊在水族箱區域，如果投食機部件覆蓋該區域，事件會被投食機部件攔截。
3. **座標轉換不一致**：水族箱區域的點擊事件需要將主視窗座標轉換為水族箱部件相對座標，但部分事件處理中缺少此轉換。
4. **調試標記影響視覺**：開發過程中添加的調試用顏色標記（綠色半透明區域、各種邊界框、投食機藍色半透明背景）影響使用者體驗，需要移除。

## What Changes
- **新增左側空白區域**：
  - 在 `config.py` 中新增 `FEED_MACHINE_AREA_WIDTH = 150`，定義主視窗左側空白區域寬度
  - 調整主視窗大小：`左側空白區域 + 水族箱 + 右側面板`
  - 水族箱區域向右移動 `FEED_MACHINE_AREA_WIDTH` 像素
  - 控制面板區域也向右移動相同距離
- **修正滑鼠事件處理邏輯**：
  - 重構 `mousePressEvent`、`mouseMoveEvent`、`mouseReleaseEvent` 的處理順序
  - 優先處理水族箱區域和左側空白區域的點擊
  - 將主視窗座標轉換為水族箱部件相對座標（`aquarium_local_pos = pos - self.aquarium_rect.topLeft()`）
  - 左側空白區域的點擊映射到水族箱左側區域（`aquarium_local_x = pos.x()`）
  - 投食機部件的透明區域不阻擋水族箱區域的點擊
- **投食機部件滑鼠事件處理**：
  - 在 `FeedMachineWidget` 中實現 `mousePressEvent`、`mouseMoveEvent`、`mouseReleaseEvent`
  - 只有點擊在投食機圖片的實際區域內才處理，透明區域讓事件穿透
  - 使用 `event.ignore()` 和 `QApplication.sendEvent()` 讓事件穿透到父視窗
- **移除調試標記**：
  - 移除主視窗 `paintEvent` 中所有綠色半透明區域填充（水族箱區域和左側空白區域）
  - 移除所有邊界框繪製（綠色、紅色、黃色、紫色、藍色）
  - 移除投食機部件的藍色半透明背景繪製（或保留作為可選的視覺輔助）

## Impact
- Affected specs: aquarium-ui
- Affected code:
  - `config.py`：新增 `FEED_MACHINE_AREA_WIDTH` 常數
  - `aquarium_window.py`：
    - `TransparentAquariumWindow.__init__`：調整區域位置計算
    - `TransparentAquariumWindow.mousePressEvent`：重構滑鼠事件處理邏輯
    - `TransparentAquariumWindow.mouseMoveEvent`：重構滑鼠移動事件處理
    - `TransparentAquariumWindow.mouseReleaseEvent`：重構滑鼠釋放事件處理
    - `TransparentAquariumWindow.paintEvent`：移除調試標記
    - `TransparentAquariumWindow.updateWindowMask`：更新遮罩以包含左側空白區域
    - `FeedMachineWidget`：新增滑鼠事件處理方法，實現事件穿透
    - `FeedMachineWidget.paintEvent`：移除藍色半透明背景（或保留作為可選）
