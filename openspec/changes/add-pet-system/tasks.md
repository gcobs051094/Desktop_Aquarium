# Tasks: 新增寵物系統與龍蝦寵物

## 1. 設定與配置
- [x] 1.1 在 `config.py` 新增 `PET_CONFIG` 字典，定義寵物解鎖與召喚條件（lobster: unlock_species="large_guppy", unlock_count=5, require_species=None, require_count=0）
- [x] 1.2 在 `config.py` 新增寵物資源路徑配置

## 2. 寵物基礎類別
- [x] 2.1 新增 `pet.py` 檔案，實作 `Pet` 基礎類別（位置、動畫幀、更新邏輯）
- [x] 2.2 實作寵物動畫載入函數（從 `resource/pet/{pet_name}/1_游動` 和 `2_轉向` 載入）

## 3. 龍蝦寵物實作
- [x] 3.1 在 `pet.py` 新增 `LobsterPet` 類別，繼承 `Pet`
- [x] 3.2 實作底部走動邏輯（限制在水族箱底部區域，水平移動）
- [x] 3.3 實作轉向邏輯（到達邊界時轉向）
- [x] 3.4 設定移動速度為慢速
- [x] 3.5 設定龍蝦顯示大小為 scale=0.6（較小尺寸）

## 4. 水族箱寵物整合
- [x] 4.1 在 `AquariumWidget` 新增 `pets` 列表
- [x] 4.2 在 `update_fishes()` 中新增寵物更新邏輯
- [x] 4.3 在 `paintEvent()` 中新增寵物繪製邏輯
- [x] 4.4 實作 `add_pet(pet)` 方法

## 5. 寵物金錢拾取
- [x] 5.1 在 `LobsterPet` 實作 `check_money_collision()` 方法，檢測與金錢的碰撞
- [x] 5.2 在寵物更新邏輯中呼叫碰撞檢測，觸碰金錢時標記為已拾取並累積金額
- [x] 5.3 確保寵物拾取金錢的邏輯與滑鼠拾取相同（使用 `MONEY_VALUE` 累積金額）

## 6. 商店寵物商品
- [x] 6.1 在 `ShopOverlay` 中新增寵物商品顯示邏輯
- [x] 6.2 實作寵物商品卡片/按鈕，顯示寵物預覽圖、名稱、解鎖條件
- [x] 6.3 實作解鎖狀態檢查（根據 `_unlocked_species` 和 `PET_CONFIG`）
- [x] 6.4 實作購買按鈕（解鎖後可點擊，召喚寵物）

## 7. 寵物解鎖與召喚
- [x] 7.1 在 `TransparentAquariumWindow` 新增 `_pets` 字典追蹤已召喚的寵物（pet_name -> pet_instance）
- [x] 7.2 實作 `_check_pet_unlock(pet_name)` 方法，檢查解鎖條件
- [x] 7.3 實作 `_spawn_pet(pet_name)` 方法，召喚寵物到水族箱
- [x] 7.4 確保每種寵物只能召喚一隻（檢查 `_pets` 字典）
- [x] 7.5 在商店購買時呼叫 `_spawn_pet()`

## 8. 寵物狀態儲存
- [x] 8.1 在 `_save_game_state()` 中新增寵物狀態儲存（寵物類型、位置等）
- [x] 8.2 在 `_load_game_state()` 中新增寵物狀態載入與恢復
