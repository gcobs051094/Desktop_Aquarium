# Tasks: 將 Guppy 替換為鬥魚系列

## 1. 配置更新
- [x] 1.1 在 `config.py` 將 `FISH_UPGRADE_THRESHOLDS["guppy"]` 改為 `FISH_UPGRADE_THRESHOLDS["鬥魚"]`
- [x] 1.2 將 `GUPPY_POOP_CONFIG` 重命名為 `BETTA_POOP_CONFIG`，並更新為鬥魚系列配置：
  - `small_鬥魚`: ("銅幣", 5秒)
  - `medium_鬥魚`: ("銀幣", 10秒)
  - `large_鬥魚`: ("金幣", 15秒)
  - `angel_鬥魚`: ("金心幣", 30秒)
- [x] 1.3 在 `MONEY_VALUE` 新增 `"銀幣": 15` 配置，並更新所有金錢類型為中文名稱
- [x] 1.4 更新 `PET_CONFIG` 中 `large_guppy` 引用為 `large_鬥魚`

## 2. 代碼更新
- [x] 2.1 在 `fish.py` 將 `GUPPY_POOP_CONFIG` 引用改為 `BETTA_POOP_CONFIG`
- [x] 2.2 更新 `fish.py` 中註釋，將 "guppy" 改為 "鬥魚"
- [x] 2.3 在 `aquarium_window.py` 將 `"guppy"` 限制邏輯改為 `"鬥魚"`
- [x] 2.4 更新 `aquarium_window.py` 中所有 `guppy` 相關註釋與變數名
- [x] 2.5 在 `aquarium_window.py` 添加中文階段名稱映射邏輯（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚）

## 3. 資源確認
- [x] 3.1 確認 `resource/fish/鬥魚/` 目錄下存在所有階段素材（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚等）
- [x] 3.2 確認 `resource/money/銀幣/` 目錄存在並包含動畫幀
- [x] 3.3 確認 `resource/money/銅幣/`、`resource/money/金幣/`、`resource/money/金心幣/` 目錄存在

## 4. 投放與載入鬥魚
- [x] 4.1 在 `add_one_fish` 中支援以「幼」或 "small" 識別 small 階段目錄，使「幼鬥魚」目錄可被選為投放
- [x] 4.2 在 `add_one_fish` 中新增中文階段名稱映射（幼→small、中→medium、成年→large、天使→angel）
- [x] 4.3 在 `_load_game_state` 中對 species 為「鬥魚」時，依 stage 對應至中文目錄名（small→幼鬥魚、medium→中鬥魚、large→成年鬥魚、angel→天使鬥魚），確保存檔載入後鬥魚正確還原

## 5. 魚種依階段縮放
- [x] 5.1 在 `config.py` 新增 `FISH_SCALE_BY_STAGE_SPECIES`（鍵為 `"階段_魚種"`），並為鬥魚各階段提供範例設定
- [x] 5.2 修改 `get_fish_scale(species, stage)` 支援可選參數 `stage`，優先查詢 `FISH_SCALE_BY_STAGE_SPECIES`，其次 `FISH_SCALE_BY_SPECIES`，最後 `DEFAULT_FISH_SCALE`
- [x] 5.3 在 `add_one_fish` 呼叫 `get_fish_scale(species, stage)` 傳入當前階段
- [x] 5.4 在 `_create_upgraded_fish` 中升級時以 `get_fish_scale(species, next_stage)` 取得新階段縮放，不再繼承舊魚 scale

## 6. 存檔還原與各形態縮放
- [x] 6.1 確保存檔載入時，species 為「鬥魚」之魚依 stage（small/medium/large/angel）對應至目錄名（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚），使重新啟動程式後鬥魚正確還原
- [x] 6.2 支援各形態獨立 scale：可透過 `FISH_SCALE_BY_SPECIES`（如「幼鬥魚」）或 `FISH_SCALE_BY_STAGE_SPECIES`（如 `small_鬥魚`）設定，投放與升級時皆使用 `get_fish_scale(species, stage)` 使 config 縮放生效
