## 1. 實作配置參數
- [x] 1.1 在 `config.py` 新增 `DEFAULT_FISH_SCALE` 與 `FISH_SCALE_BY_SPECIES`
- [x] 1.2 在 `config.py` 新增 `DEFAULT_FEED_SCALE` 與 `FEED_SCALE`
- [x] 1.3 在 `config.py` 新增 `DEFAULT_MONEY_SCALE` 與 `MONEY_SCALE`
- [x] 1.4 在 `config.py` 新增 `DEFAULT_MATERIAL_SCALE` 與 `MATERIAL_SCALE_BY_KEY`
- [x] 1.5 在 `config.py` 新增輔助函式：`get_fish_scale()`, `get_feed_scale()`, `get_money_scale()`, `get_material_scale()`
- [x] 1.6 在 `PET_CONFIG` 中為每個寵物新增 `scale` 欄位
- [x] 1.7 在 `config.py` 新增魚種速度配置：`DEFAULT_FISH_SPEED_MIN/MAX`, `FISH_SPEED_BY_SPECIES`, `DEFAULT_FISH_ANIMATION_SPEED`, `FISH_FEED_CHASE_SPEED_MULTIPLIER`
- [x] 1.8 在 `config.py` 新增飼料速度配置：`DEFAULT_FEED_FALL_SPEED`, `FEED_FALL_SPEED`, `DEFAULT_FEED_ANIMATION_SPEED`, `FEED_ANIMATION_SPEED`
- [x] 1.9 在 `config.py` 新增金錢速度配置：`DEFAULT_MONEY_FALL_SPEED`, `MONEY_FALL_SPEED`, `DEFAULT_MONEY_ANIMATION_SPEED`, `MONEY_ANIMATION_SPEED`
- [x] 1.10 在 `config.py` 新增寵物速度配置：`DEFAULT_PET_SPEED`, `DEFAULT_PET_ANIMATION_SPEED`
- [x] 1.11 在 `config.py` 新增速度相關輔助函式：`get_fish_speed_range()`, `get_fish_animation_speed()`, `get_feed_fall_speed()`, `get_feed_animation_speed()`, `get_money_fall_speed()`, `get_money_animation_speed()`, `get_material_speed()`
- [x] 1.12 在 `PET_CONFIG` 中為每個寵物新增 `speed` 欄位（可選）

## 2. 更新程式碼使用配置
- [x] 2.1 在 `aquarium_window.py` 導入 scale 與 speed 相關函式
- [x] 2.2 修改 `add_one_fish()` 使用 `get_fish_scale()` 與 `get_fish_speed_range()` 取代硬編碼值
- [x] 2.3 修改 `on_aquarium_clicked()` 建立 Feed 時使用 `get_feed_scale()`, `get_feed_fall_speed()`, `get_feed_animation_speed()` 取代硬編碼值
- [x] 2.4 修改 `_on_fish_poop()` 建立 Money 時使用 `get_money_scale()`, `get_money_fall_speed()`, `get_money_animation_speed()` 取代硬編碼值
- [x] 2.5 修改寵物建立邏輯，從 `PET_CONFIG` 讀取 `scale` 與 `speed` 參數
- [x] 2.6 在 `fish.py` 中使用 `get_fish_animation_speed()` 與 `FISH_FEED_CHASE_SPEED_MULTIPLIER` 取代硬編碼值
- [x] 2.7 在 `pet.py` 中使用 `PET_CONFIG` 讀取動畫速度，或使用 `DEFAULT_PET_ANIMATION_SPEED`
