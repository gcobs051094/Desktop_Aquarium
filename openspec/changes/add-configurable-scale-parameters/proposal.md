# Change: 新增可配置的顯示縮放與移動速度參數

## Why
目前魚種、飼料、金錢、寵物等物件的顯示縮放（scale）與移動速度（speed）參數硬編碼在程式碼中，無法透過設定檔調整。為了讓使用者能夠方便地調整各物件的顯示大小與移動速度，需要在 `config.py` 中提供可配置的 scale 與 speed 參數。

## What Changes
- **新增 scale 配置參數**：在 `config.py` 中新增魚種、飼料、金錢、寵物及後續素材的 scale 配置
  - `DEFAULT_FISH_SCALE`：魚種預設縮放
  - `FISH_SCALE_BY_SPECIES`：依魚種覆寫的縮放字典
  - `DEFAULT_FEED_SCALE`：飼料預設縮放
  - `FEED_SCALE`：依飼料名稱覆寫的縮放字典
  - `DEFAULT_MONEY_SCALE`：金錢預設縮放
  - `MONEY_SCALE`：依金錢類型覆寫的縮放字典
  - `DEFAULT_MATERIAL_SCALE`：後續素材預設縮放
  - `MATERIAL_SCALE_BY_KEY`：依素材鍵覆寫的縮放字典
- **新增 speed 配置參數**：在 `config.py` 中新增各物件的移動速度配置
  - `DEFAULT_FISH_SPEED_MIN/MAX`：魚種速度範圍
  - `FISH_SPEED_BY_SPECIES`：依魚種覆寫的速度範圍字典
  - `DEFAULT_FISH_ANIMATION_SPEED`：魚類動畫速度
  - `FISH_FEED_CHASE_SPEED_MULTIPLIER`：魚類追飼料時的速度倍率
  - `DEFAULT_FEED_FALL_SPEED`：飼料下落速度
  - `FEED_FALL_SPEED`：依飼料名稱覆寫的下落速度字典
  - `DEFAULT_FEED_ANIMATION_SPEED`：飼料動畫速度
  - `DEFAULT_MONEY_FALL_SPEED`：金錢下落速度
  - `MONEY_FALL_SPEED`：依金錢類型覆寫的下落速度字典
  - `DEFAULT_MONEY_ANIMATION_SPEED`：金錢動畫速度
  - `DEFAULT_PET_SPEED`：寵物預設移動速度
  - `DEFAULT_PET_ANIMATION_SPEED`：寵物預設動畫速度
- **新增輔助函式**：提供 `get_fish_scale()`, `get_feed_scale()`, `get_money_scale()`, `get_material_scale()` 以及速度相關的輔助函式
- **更新 PET_CONFIG**：在寵物配置中新增 `scale` 與 `speed` 欄位
- **程式碼更新**：修改 `aquarium_window.py`、`fish.py`、`pet.py` 中建立與更新物件的邏輯，改為從 config 讀取 scale 與 speed 參數

## Impact
- Affected specs: game-economy（新增配置參數規範）
- Affected code: `config.py`（新增 scale 與 speed 配置與輔助函式）、`aquarium_window.py`、`fish.py`、`pet.py`（使用 config 的 scale 與 speed）
