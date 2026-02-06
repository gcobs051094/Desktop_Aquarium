## 1. 視窗與面板結構
- [x] 1.1 擴大視窗尺寸，在水族箱右側新增 180px 寬的控制面板區域
- [x] 1.2 定義 `PANEL_WIDTH` 常數（180px）
- [x] 1.3 新增 `panel_rect` 矩形定義控制面板位置
- [x] 1.4 更新視窗遮罩邏輯，將控制面板區域加入遮罩（`aquarium_rect | panel_rect`）
- [x] 1.5 實作滑鼠事件轉發邏輯，將面板區域的點擊事件正確轉發給面板部件（座標轉換）

## 2. 控制面板元件
- [x] 2.1 創建 `ControlPanel` 類別（繼承 `QFrame`）
- [x] 2.2 設定面板樣式（深色半透明背景、圓角、按鈕樣式）
- [x] 2.3 設定 `WA_StyledBackground` 屬性以確保背景正確繪製
- [x] 2.4 實作垂直佈局（`QVBoxLayout`）放置三個按鈕

## 3. 資源列舉功能
- [x] 3.1 實作 `_resource_dir()` 輔助函數
- [x] 3.2 實作 `_list_backgrounds()`：掃描 `resource/background/` 目錄，列出所有 .jpg/.png 檔案
- [x] 3.3 實作 `_list_feeds()`：掃描 `resource/feed/` 目錄，列出所有子目錄（飼料類型）
- [x] 3.4 實作 `_list_small_fish()`：掃描 `resource/fish/` 目錄，僅列出名稱包含 "small" 的子目錄層級

## 4. 切換背景功能
- [x] 4.1 在 `ControlPanel` 中新增「切換背景」按鈕
- [x] 4.2 實作按鈕點擊後展開清單（使用 `QMenu`）
- [x] 4.3 清單項目顯示背景檔案名稱（不含副檔名）
- [x] 4.4 選擇背景後發出 `background_selected` 信號
- [x] 4.5 在 `AquariumWidget` 中新增 `set_background(path)` 方法
- [x] 4.6 在 `AquariumWidget` 中新增 `_load_background_pixmap()` 方法
- [x] 4.7 連接信號處理器 `on_background_selected()`，切換水族箱背景

## 5. 切換飼料功能
- [x] 5.1 在 `ControlPanel` 中新增「切換飼料」按鈕
- [x] 5.2 實作按鈕點擊後展開清單（使用 `QMenu`）
- [x] 5.3 清單項目顯示飼料類型名稱（子目錄名稱）
- [x] 5.4 選擇飼料後發出 `feed_selected` 信號（包含名稱與路徑）
- [x] 5.5 連接信號處理器 `on_feed_selected()`，儲存當前飼料類型

## 6. 投放魚功能
- [x] 6.1 在 `ControlPanel` 中新增「投放魚」按鈕
- [x] 6.2 實作按鈕點擊後展開清單（使用 `QMenu`）
- [x] 6.3 清單項目顯示魚種名稱（格式：`species_name / small_variant_name`）
- [x] 6.4 選擇魚種後發出 `fish_add_requested` 信號（包含魚種目錄路徑）
- [x] 6.5 實作 `add_one_fish(fish_dir)` 方法：載入魚種動畫、隨機位置與速度、新增到水族箱
- [x] 6.6 連接信號處理器 `on_fish_add_requested()`，呼叫 `add_one_fish()` 新增魚類

## 7. 移除初始魚類
- [x] 7.1 移除 `load_fishes()` 方法中的初始 10 條魚載入邏輯
- [x] 7.2 確保水族箱初始狀態為空（無魚類）

## 8. 事件處理與座標轉換
- [x] 8.1 實作 `_panel_event()` 輔助方法，將視窗座標轉換為面板相對座標
- [x] 8.2 實作 `mousePressEvent()`：將面板區域的點擊事件轉發給面板
- [x] 8.3 實作 `mouseMoveEvent()`：將面板區域的移動事件轉發給面板
- [x] 8.4 實作 `mouseReleaseEvent()`：將面板區域的釋放事件轉發給面板
