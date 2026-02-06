## 1. 控制面板商店按鈕
- [x] 1.1 在 ControlPanel 新增 `shop_requested` 信號
- [x] 1.2 在 ControlPanel 新增「商店」按鈕（位於「投放魚」與 stretch/關閉之間）
- [x] 1.3 按鈕點擊時發出 `shop_requested`
- [x] 1.4 設定按鈕樣式（例如綠色系）以區別其他按鈕

## 2. 商店半透明覆蓋視窗（ShopOverlay）
- [x] 2.1 新增 `ShopOverlay` 類別（QFrame），接受 geometry 與 parent
- [x] 2.2 覆蓋視窗覆蓋水族箱區域（與 aquarium_rect 同尺寸與位置）
- [x] 2.3 設定半透明深色背景樣式
- [x] 2.4 顯示標題「商店」與「關閉」按鈕
- [x] 2.5 關閉按鈕點擊時發出 `closed` 信號並隱藏覆蓋
- [x] 2.6 顯示預留說明（解鎖／購買條件）
- [x] 2.7 提供可捲動區域與 `items_layout()` 供未來加入魚選項

## 3. 主視窗整合與事件轉發
- [x] 3.1 在 TransparentAquariumWindow 建立 ShopOverlay 實例（geometry = aquarium_rect）
- [x] 3.2 連接 panel.shop_requested → 顯示並 raise 商店覆蓋
- [x] 3.3 連接 _shop_overlay.closed → 關閉處理（可選）
- [x] 3.4 當商店覆蓋顯示時，水族箱區域的 mousePressEvent 轉發給覆蓋（座標轉為覆蓋相對）
- [x] 3.5 當商店覆蓋顯示時，水族箱區域的 mouseMoveEvent / mouseReleaseEvent 轉發給覆蓋

## 4. 設定與預留
- [x] 4.1 在 config.py 新增商店商品預留結構註解（unlock_species、unlock_count、require_species、require_count、spawn_fish_species）
