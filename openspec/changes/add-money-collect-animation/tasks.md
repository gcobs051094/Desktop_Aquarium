# Tasks: 金錢類物品與寶箱怪產物消失動畫

## 1. 配置參數
- [x] 1.1 在 `config.py` 新增 `MONEY_COLLECT_ANIMATION_DURATION_SEC`（消失動畫持續時間，預設 2.0 秒）
- [x] 1.2 在 `config.py` 新增 `MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER`（消失動畫期間動畫加速倍率，預設 3.0）
- [x] 1.3 在 `config.py` 新增 `MONEY_COLLECT_VELOCITY_Y`（消失動畫往上移動速度，預設 -2.0 像素/幀）

## 2. Money 類消失動畫
- [x] 2.1 在 `Money` 類添加消失動畫狀態變數（`is_collecting`、`collect_timer`、`collect_opacity`、`collect_velocity_y`、`collect_duration`、`collect_animation_speed_multiplier`）
- [x] 2.2 實作 `start_collect_animation()` 方法，開始消失動畫
- [x] 2.3 修改 `update()` 方法，處理消失動畫邏輯（加速動畫、往上移動、透明度漸變）
- [x] 2.4 修改 `get_opacity()` 方法，優先返回消失動畫透明度
- [x] 2.5 修改 `try_collect_money_at()` 和 `mouseMoveEvent()`，觸發消失動畫而非立即標記為已收集
- [x] 2.6 修改寵物自動拾取金錢的邏輯，觸發消失動畫
- [x] 2.7 修改繪製邏輯，支援消失動畫的透明度

## 3. 寶箱怪產物消失動畫
- [x] 3.1 在 `ChestMonsterPet` 類添加產物消失動畫狀態變數（`is_produce_collecting`、`produce_collect_timer`、`produce_collect_opacity`、`produce_collect_position`、`produce_collect_velocity_y`、`produce_collect_duration`）
- [x] 3.2 實作 `start_produce_collect_animation()` 方法，開始產物消失動畫
- [x] 3.3 實作 `get_produce_opacity()` 方法，返回產物透明度
- [x] 3.4 修改 `update()` 方法，處理產物消失動畫邏輯（往上移動、透明度漸變），動畫結束後重置寶箱怪
- [x] 3.5 修改 `get_produce_position()` 方法，消失動畫期間返回動畫位置
- [x] 3.6 修改 `try_collect_chest_produce_at()`，觸發消失動畫而非立即重置
- [x] 3.7 修改寶箱怪產物繪製邏輯，支援消失動畫的透明度

## 4. 導入配置
- [x] 4.1 在 `aquarium_window.py` 導入消失動畫配置參數
- [x] 4.2 在 `pet.py` 導入消失動畫配置參數
