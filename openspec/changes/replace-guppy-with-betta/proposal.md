# Change: 將 Guppy 替換為鬥魚系列

## Why
1. **素材更新**：用戶已在 `resource/fish/鬥魚/` 目錄下新增完整的鬥魚系列素材，包含幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚、藍寶石鬥魚、金鬥魚等階段。
2. **遊戲內容調整**：將初始魚種從 guppy 改為鬥魚系列，並更新相關成長階段與大便產物配置。

## What Changes
- **魚種替換**：將所有 `guppy` 相關配置與代碼引用改為 `betta`（鬥魚）。
- **成長階段**：更新 `config.py` 之 `FISH_UPGRADE_THRESHOLDS`，將 `"guppy"` 改為 `"betta"`，並維持相同的升級閾值結構。
- **大便產物配置**：將 `GUPPY_POOP_CONFIG` 重命名為 `BETTA_POOP_CONFIG`，並更新為鬥魚系列的大便產物：
  - 幼鬥魚（small_betta）：銅幣
  - 中鬥魚（medium_betta）：銀幣
  - 成年鬥魚（large_betta）：金幣
  - 天使鬥魚（angel_betta）：金心幣
  - 藍寶石鬥魚（gem_betta）：待定（暫不配置）
  - 金鬥魚（gold_betta）：待定（暫不配置）
- **金錢類型**：新增銀幣（silver_coin）至 `MONEY_VALUE` 配置。
- **代碼引用**：更新 `fish.py`、`aquarium_window.py` 等文件中所有 `guppy` 相關引用為 `betta`。
- **初始魚種限制**：更新 `aquarium_window.py` 中限制邏輯，將 `"guppy"` 改為 `"鬥魚"`。
- **投放鬥魚**：`add_one_fish` 支援以「幼」或 "small" 識別 small 階段目錄；階段名稱支援中文映射（幼→small、中→medium、成年→large、天使→angel）。
- **存檔載入鬥魚**：`_load_game_state` 載入魚類時，若 species 為「鬥魚」，依 stage（small/medium/large/angel）對應至目錄名（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚），確保重開程式後鬥魚正確還原。
- **魚種依階段縮放**：新增 `config.py` 之 `FISH_SCALE_BY_STAGE_SPECIES`（鍵為 `"階段_魚種"`，如 `small_鬥魚`）；`get_fish_scale(species, stage)` 支援依階段回傳縮放倍率，優先使用階段+魚種設定；投放與升級時皆使用對應階段之縮放。
- **各形態獨立縮放**：鬥魚有不同形態（幼鬥魚／中鬥魚／成年鬥魚／天使鬥魚／藍寶石鬥魚／金鬥魚），可透過 `FISH_SCALE_BY_SPECIES`（以顯示名稱為鍵）或 `FISH_SCALE_BY_STAGE_SPECIES`（以 `階段_魚種` 為鍵）各自控制 scale，投放與升級時皆以 `get_fish_scale(species, stage)` 取得縮放，使 config 修改能生效。
- **存檔還原鬥魚**：載入存檔時，若魚類 species 為「鬥魚」，依 stage 對應至資源目錄名（small→幼鬥魚、medium→中鬥魚、large→成年鬥魚、angel→天使鬥魚），確保存檔後重新啟動程式時鬥魚能正確還原。

## Impact
- Affected specs: game-economy
- Affected code: 
  - `config.py`（`FISH_UPGRADE_THRESHOLDS`、`GUPPY_POOP_CONFIG` → `BETTA_POOP_CONFIG`、`MONEY_VALUE`、`FISH_SCALE_BY_STAGE_SPECIES`、`get_fish_scale(species, stage)`）
  - `fish.py`（`GUPPY_POOP_CONFIG` 引用）
  - `aquarium_window.py`（魚種限制邏輯、升級路徑解析、投放魚階段解析、載入存檔階段目錄對應、升級時 scale 依新階段）
  - `PET_CONFIG`（`large_guppy` → `large_鬥魚`）
