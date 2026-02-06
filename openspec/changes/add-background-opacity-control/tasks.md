# Tasks: 新增背景圖片透明度調整功能

## 1. 水族箱背景透明度屬性
- [x] 1.1 在 `AquariumWidget.__init__` 中新增 `self.background_opacity = 80`（0~100%，預設 80%）
- [x] 1.2 新增 `set_background_opacity(percent: int)` 方法，限制範圍 0~100 並觸發重繪
- [x] 1.3 在 `paintEvent` 中繪製背景時，先 `painter.setOpacity(background_opacity / 100.0)`，繪製完成後 `setOpacity(1.0)` 恢復

## 2. 控制面板透明度 UI
- [x] 2.1 在 `ControlPanel` 中新增 `background_opacity_changed = pyqtSignal(int)` 信號
- [x] 2.2 在控制面板中新增「背景透明度」標籤（`QLabel`），初始顯示「背景透明度 80%」
- [x] 2.3 新增水平滑桿（`QSlider`），範圍 0~100，預設值 80，設定刻度標記（0、25、50、75、100）
- [x] 2.4 連接滑桿 `valueChanged` 到 `_on_opacity_changed`，更新標籤文字並發出信號

## 3. 視窗連接與更新
- [x] 3.1 在 `TransparentAquariumWindow` 中連接 `panel.background_opacity_changed` 到 `on_background_opacity_changed` 方法
- [x] 3.2 實作 `on_background_opacity_changed(percent)` 方法，呼叫 `aquarium.set_background_opacity(percent)`
