## ADDED Requirements

### Requirement: 可配置的物件顯示縮放參數
系統 SHALL 在 `config.py` 中提供可配置的顯示縮放（scale）參數，允許使用者調整魚種、飼料、金錢、寵物及後續素材的顯示大小。

#### Scenario: 魚種縮放配置
- **WHEN** 系統建立魚類物件時
- **THEN** 使用 `config.get_fish_scale(species)` 取得縮放倍率
- **AND** 若 `FISH_SCALE_BY_SPECIES` 中有該魚種的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_FISH_SCALE` 作為預設值

#### Scenario: 飼料縮放配置
- **WHEN** 系統建立飼料物件時
- **THEN** 使用 `config.get_feed_scale(feed_name)` 取得縮放倍率
- **AND** 若 `FEED_SCALE` 中有該飼料名稱的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_FEED_SCALE` 作為預設值

#### Scenario: 金錢縮放配置
- **WHEN** 系統建立金錢物件時
- **THEN** 使用 `config.get_money_scale(money_type)` 取得縮放倍率
- **AND** 若 `MONEY_SCALE` 中有該金錢類型的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_MONEY_SCALE` 作為預設值

#### Scenario: 寵物縮放配置
- **WHEN** 系統建立寵物物件時
- **THEN** 從 `PET_CONFIG[pet_name].get("scale", default)` 取得縮放倍率
- **AND** 若該寵物配置中有 `scale` 欄位，則使用該值
- **AND** 否則使用程式內建預設值

#### Scenario: 後續素材縮放配置
- **WHEN** 系統建立後續新增的素材物件時
- **THEN** 可使用 `config.get_material_scale(key)` 取得縮放倍率
- **AND** 若 `MATERIAL_SCALE_BY_KEY` 中有該素材鍵的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_MATERIAL_SCALE` 作為預設值

### Requirement: Scale 配置輔助函式
系統 SHALL 在 `config.py` 中提供輔助函式，統一處理各類物件的縮放倍率查詢。

#### Scenario: 輔助函式提供
- **WHEN** 程式需要取得物件的縮放倍率時
- **THEN** 可使用 `get_fish_scale(species)` 取得魚種縮放
- **AND** 可使用 `get_feed_scale(feed_name)` 取得飼料縮放
- **AND** 可使用 `get_money_scale(money_type)` 取得金錢縮放
- **AND** 可使用 `get_material_scale(key)` 取得後續素材縮放
- **AND** 所有函式均回傳 float 類型的縮放倍率（1.0 為原始尺寸）

### Requirement: 可配置的物件移動速度參數
系統 SHALL 在 `config.py` 中提供可配置的移動速度（speed）參數，允許使用者調整魚種、飼料、金錢、寵物及後續素材的移動速度與動畫速度。

#### Scenario: 魚種速度配置
- **WHEN** 系統建立魚類物件時
- **THEN** 使用 `config.get_fish_speed_range(species)` 取得速度範圍 (min, max)
- **AND** 若 `FISH_SPEED_BY_SPECIES` 中有該魚種的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_FISH_SPEED_MIN` 與 `DEFAULT_FISH_SPEED_MAX` 作為預設範圍
- **AND** 使用 `config.get_fish_animation_speed(species)` 取得動畫速度
- **AND** 魚類朝飼料移動時使用 `FISH_FEED_CHASE_SPEED_MULTIPLIER` 作為速度倍率

#### Scenario: 飼料速度配置
- **WHEN** 系統建立飼料物件時
- **THEN** 使用 `config.get_feed_fall_speed(feed_name)` 取得下落速度
- **AND** 使用 `config.get_feed_animation_speed(feed_name)` 取得動畫速度
- **AND** 若對應字典中有該飼料名稱的設定，則使用該設定
- **AND** 否則使用對應的預設值

#### Scenario: 金錢速度配置
- **WHEN** 系統建立金錢物件時
- **THEN** 使用 `config.get_money_fall_speed(money_type)` 取得下落速度
- **AND** 使用 `config.get_money_animation_speed(money_type)` 取得動畫速度
- **AND** 若對應字典中有該金錢類型的設定，則使用該設定
- **AND** 否則使用對應的預設值

#### Scenario: 寵物速度配置
- **WHEN** 系統建立寵物物件時
- **THEN** 從 `PET_CONFIG[pet_name].get("speed", DEFAULT_PET_SPEED)` 取得移動速度
- **AND** 從 `PET_CONFIG[pet_name].get("animation_speed", DEFAULT_PET_ANIMATION_SPEED)` 取得動畫速度
- **AND** 若該寵物配置中有對應欄位，則使用該值
- **AND** 否則使用對應的預設值

#### Scenario: 後續素材速度配置
- **WHEN** 系統建立後續新增的素材物件時
- **THEN** 可使用 `config.get_material_speed(key)` 取得移動速度
- **AND** 若 `MATERIAL_SPEED_BY_KEY` 中有該素材鍵的設定，則使用該設定
- **AND** 否則使用 `DEFAULT_MATERIAL_SPEED` 作為預設值

### Requirement: Speed 配置輔助函式
系統 SHALL 在 `config.py` 中提供輔助函式，統一處理各類物件的移動速度與動畫速度查詢。

#### Scenario: 速度輔助函式提供
- **WHEN** 程式需要取得物件的移動速度或動畫速度時
- **THEN** 可使用 `get_fish_speed_range(species)` 取得魚種速度範圍 (min, max)
- **AND** 可使用 `get_fish_animation_speed(species)` 取得魚種動畫速度
- **AND** 可使用 `get_feed_fall_speed(feed_name)` 取得飼料下落速度
- **AND** 可使用 `get_feed_animation_speed(feed_name)` 取得飼料動畫速度
- **AND** 可使用 `get_money_fall_speed(money_type)` 取得金錢下落速度
- **AND** 可使用 `get_money_animation_speed(money_type)` 取得金錢動畫速度
- **AND** 可使用 `get_material_speed(key)` 取得後續素材移動速度
- **AND** 所有函式均回傳 float 類型的速度值（像素/幀或動畫播放倍率）
