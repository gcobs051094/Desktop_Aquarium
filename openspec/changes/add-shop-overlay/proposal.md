# Change: 新增商店按鈕與半透明商店覆蓋視窗

## Why
使用者需要一個商店入口，未來可在商店內購買魚種。商店應以半透明覆蓋視窗的形式顯示在水族箱頁面階層上，不遮住右側控制面板；購買邏輯預留兩種條件：解鎖（曾達到指定魚種數量）與購買當下（當下滿足指定魚種數量，購買後生成新魚並移除指定魚種、觸發餓肚子死掉動畫）。

## What Changes
- **控制面板**：新增「商店」按鈕，點擊後發出開啟商店請求。
- **商店覆蓋視窗**：在水族箱視窗上層顯示半透明覆蓋（ShopOverlay），覆蓋水族箱區域，包含標題「商店」、關閉按鈕、預留說明（解鎖／購買條件）與預留商品列表版面。
- **主視窗事件**：商店顯示時，水族箱區域的滑鼠事件改轉發給商店覆蓋，使關閉按鈕與未來商品可正常點擊。
- **設定與預留**：在 `config.py` 註解中預留商店商品結構說明（unlock_species、unlock_count、require_species、require_count、spawn_fish_species），供未來實作魚選項與購買條件使用。

## Impact
- **受影響能力**：水族箱使用者介面（aquarium-ui）
- **受影響代碼**：
  - `aquarium_window.py`：ControlPanel 新增商店按鈕與 `shop_requested` 信號；新增 `ShopOverlay` 類別；TransparentAquariumWindow 建立覆蓋、連接信號、滑鼠事件依覆蓋顯示與否轉發至覆蓋或水族箱
  - `config.py`：新增商店商品預留結構註解
