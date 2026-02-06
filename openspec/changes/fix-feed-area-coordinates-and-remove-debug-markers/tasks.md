# Tasks: 修正投食機區域座標系統與滑鼠事件處理

## 1. 新增左側空白區域配置
- [x] 在 `config.py` 中新增 `FEED_MACHINE_AREA_WIDTH = 150` 常數
- [x] 更新相關導入語句

## 2. 調整主視窗區域布局
- [x] 修改 `TransparentAquariumWindow.__init__` 中的區域計算：
  - `feed_machine_area_rect = QRect(0, 0, FEED_MACHINE_AREA_WIDTH, aquarium_size[1])`
  - `aquarium_rect = QRect(FEED_MACHINE_AREA_WIDTH, 0, aquarium_size[0], aquarium_size[1])`
  - `panel_rect = QRect(FEED_MACHINE_AREA_WIDTH + aquarium_size[0], 0, PANEL_WIDTH, aquarium_size[1])`
- [x] 調整主視窗大小：`FEED_MACHINE_AREA_WIDTH + aquarium_size[0] + PANEL_WIDTH`
- [x] 更新水族箱部件和控制面板的位置

## 3. 更新視窗遮罩
- [x] 修改 `updateWindowMask` 方法，包含左側空白區域
- [x] 確保左側空白區域可接收滑鼠事件

## 4. 重構滑鼠事件處理邏輯
- [x] 修改 `mousePressEvent`：
  - 優先檢查水族箱區域和左側空白區域
  - 將主視窗座標轉換為水族箱部件相對座標
  - 左側空白區域的點擊映射到水族箱左側
  - 檢查投食機部件圖片區域，透明區域不阻擋
- [x] 修改 `mouseMoveEvent`：同樣的優先順序和座標轉換
- [x] 修改 `mouseReleaseEvent`：同樣的優先順序和座標轉換

## 5. 實現投食機部件滑鼠事件穿透
- [x] 在 `FeedMachineWidget` 中實現 `mousePressEvent`：
  - 檢查點擊是否在圖片實際區域內
  - 透明區域使用 `event.ignore()` 和 `QApplication.sendEvent()` 讓事件穿透
- [x] 在 `FeedMachineWidget` 中實現 `mouseMoveEvent`：讓透明區域事件穿透
- [x] 在 `FeedMachineWidget` 中實現 `mouseReleaseEvent`：讓透明區域事件穿透

## 6. 移除調試標記（可選）
- [ ] 移除主視窗 `paintEvent` 中的綠色半透明區域填充
- [ ] 移除所有邊界框繪製（綠色、紅色、黃色、紫色、藍色）
- [ ] 移除投食機部件的藍色半透明背景（或保留作為可選的視覺輔助）

## 7. 測試與驗證
- [ ] 測試 `FEED_MACHINE_AREA_WIDTH = 0` 時的功能正常
- [ ] 測試 `FEED_MACHINE_AREA_WIDTH = 150` 時的功能正常
- [ ] 驗證水族箱左半邊可以正常投放飼料
- [ ] 驗證左側空白區域的點擊正確映射到水族箱
- [ ] 驗證投食機圖片區域不阻擋投放飼料
- [ ] 驗證投食機透明區域不阻擋投放飼料
