# Tasks: Guppy 大便金錢機制與金錢素材邊緣對比

## 1. 設定與資料
- [x] 1.1 在 `config.py` 新增 `GUPPY_POOP_CONFIG`（medium_guppy → copper_coin 每 10 秒，large_guppy → gold_coin 每 15 秒）
- [x] 1.2 在 `config.py` 新增 `MONEY_VALUE`（copper_coin $10，gold_coin $20）

## 2. 魚大便行為
- [x] 2.1 在 `fish.py` 引入 `GUPPY_POOP_CONFIG`，魚初始化時依 species/stage 設定 `poop_interval_sec` 與 `poop_timer`
- [x] 2.2 在 `fish.py` 新增 `on_poop_callback` 與 `set_poop_callback`，在 `update()` 中每幀累加大便計時，達間隔時呼叫 callback(money_type, position)
- [x] 2.3 在 `aquarium_window.py` 的 `add_fish()` 中為魚設定 `set_poop_callback(self._on_fish_poop)`，實作 `_on_fish_poop(money_type, position)` 產生金錢物件並加入 `moneys` 列表

## 3. 金錢物件與落下
- [x] 3.1 在 `aquarium_window.py` 新增 `Money` 類（位置、動畫幀、落下速度與飼料同 0.6、過期邏輯）
- [x] 3.2 實作 `_load_money_frames(money_type)` 從 `resource/money/{money_type}/*.png` 載入幀
- [x] 3.3 在 `update_fishes()` 中更新金錢落下與動畫、移除過期金錢；在 `paintEvent` 中繪製金錢

## 4. 拾取與金錢計數器
- [x] 4.1 在 `AquariumWidget` 實作 `try_collect_money_at(pos)`：若點擊在金錢上則標記為已拾取、從列表移除，回傳 `MONEY_VALUE[money_name]`
- [x] 4.2 在 `on_aquarium_clicked(pos)` 中先呼叫 `try_collect_money_at(pos)`，若有回傳值則累加 `total_money` 並更新顯示，否則再處理投放飼料
- [x] 4.3 在控制面板頂部新增金錢計數器（QLabel「金錢: $0」），`ControlPanel` 提供 `set_money(value)`，視窗在拾取後更新顯示

## 5. 金錢素材邊緣對比
- [x] 5.1 在 `aquarium_window.py` 新增 `_darken_money_edges(pixmap, alpha_threshold, darken_factor)`：將最外圍非透明像素（alpha > threshold 且至少一鄰點透明或越界）之 RGB 乘以 darken_factor 加深
- [x] 5.2 在 `_load_money_frames()` 中對每幀載入的 pixmap 呼叫 `_darken_money_edges()` 後再加入 frames 列表
