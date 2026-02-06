# Tasks: 孔雀魚與鯊魚移至商店魚種 tab

## 1. 投放魚清單排除商店魚種
- [x] 1.1 在 `config.py` 新增 `FISH_SHOP_CONFIG`（孔雀魚、鯊魚之解鎖與購買條件）
- [x] 1.2 修改 `_list_small_fish()`：排除 `FISH_SHOP_CONFIG` 內的魚種，僅列舉其餘魚種目錄

## 2. 商店魚種 tab 與寵物相同欄位
- [x] 2.1 ShopOverlay 魚種 tab 改為可捲動區域與卡片版面（與寵物 tab 相同結構）
- [x] 2.2 新增 `_update_fish_items(unlocked_species, total_money, fish_counts)`：依 `FISH_SHOP_CONFIG` 建立每項魚種卡片（64×64 預覽圖、名稱、描述、解鎖／購買條件、購買／未解鎖按鈕）
- [x] 2.3 新增 `fish_purchase_requested` 信號；`update_items()` 新增 `fish_counts` 參數並呼叫 `_update_fish_items()`

## 3. 主視窗魚種購買處理
- [x] 3.1 連接 `_shop_overlay.fish_purchase_requested` 至 `_on_fish_purchase_requested(species_name)`
- [x] 3.2 實作 `_on_fish_purchase_requested()`：檢查解鎖、犧牲魚或扣金幣、呼叫 `on_fish_add_requested(fish_dir)`、刷新商店與存檔
- [x] 3.3 所有呼叫 `update_items()` 處傳入 `self._get_fish_count_by_species()` 作為 `fish_counts`

## 4. 新增魚支援無 small/幼 子目錄
- [x] 4.1 修改 `add_one_fish()`：當魚種目錄下找不到含 "small" 或「幼」的子目錄時，使用魚種目錄本身作為動畫路徑，階段視為 small
