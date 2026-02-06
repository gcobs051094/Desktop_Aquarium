# Change: 孔雀魚與鯊魚自投放魚清單移至商店魚種 tab

## Why
孔雀魚與鯊魚改為僅在商店「魚種」tab 販售，不再出現在「投放魚」按鈕清單中；商店魚種項目需與寵物 tab 相同欄位（預覽圖、名稱、描述、解鎖條件、購買按鈕），以維持一致的商店體驗並支援解鎖／購買條件（魚種數量或金幣）。

## What Changes
- **投放魚清單**：`_list_small_fish()` 排除僅在商店販售的魚種；凡列於 `FISH_SHOP_CONFIG` 的魚種（孔雀魚、鯊魚）不再出現在投放魚清單，僅鬥魚等未列入商店魚種者仍可從投放魚按鈕新增。
- **商店魚種配置**：在 `config.py` 新增 `FISH_SHOP_CONFIG`，定義孔雀魚與鯊魚之解鎖與購買條件：
  - 孔雀魚：解鎖條件為曾達到 5 隻天使鬥魚；購買時需犧牲 1 隻天使鬥魚換取一隻孔雀魚。
  - 鯊魚：無解鎖條件；每次購買需消耗 3000 金幣。
- **商店魚種 tab**：商店「魚種」tab 改為與「寵物」tab 相同結構：可捲動區域、每項為卡片（64×64 預覽圖、名稱、描述、解鎖／購買條件、購買／未解鎖按鈕）；依 `FISH_SHOP_CONFIG` 與當前解鎖狀態、魚種數量、金幣更新顯示；點擊「購買」時檢查解鎖與購買條件，通過後在水族箱新增該魚種（犧牲魚或扣金幣由配置決定）。
- **主視窗**：連接商店 `fish_purchase_requested` 信號至 `_on_fish_purchase_requested()`，實作解鎖檢查、犧牲魚或扣金幣、呼叫 `add_one_fish()` 新增魚、刷新商店與存檔。
- **新增魚邏輯**：`add_one_fish()` 支援魚種目錄下無「small」或「幼」子目錄時，直接使用魚種目錄作為動畫路徑（如孔雀魚、鯊魚），仍以階段 small 新增魚。

## Impact
- **受影響能力**：水族箱使用者介面（aquarium-ui）、遊戲經濟（game-economy）
- **受影響代碼**：
  - `config.py`：新增 `FISH_SHOP_CONFIG`（孔雀魚、鯊魚）
  - `aquarium_window.py`：`_list_small_fish()` 排除商店魚種；ShopOverlay 魚種 tab 改為與寵物相同欄位、`_update_fish_items()`、`fish_purchase_requested`、`_on_fish_purchase_requested()`；`update_items()` 新增 `fish_counts` 參數；`add_one_fish()` 支援無 small/幼 子目錄之魚種目錄
