# Tasks: 新增寶箱怪與拼布魚寵物

## 1. 配置與金錢
- [x] 1.1 在 `config.py` 之 `PET_CONFIG` 支援可選欄位 `unlock_money`；新增 `寶箱怪`（unlock_money: 2000）、`拼布魚`（unlock_money: 3500），並設定 scale、speed 等。
- [x] 1.2 在 `config.py` 之 `MONEY_VALUE` 新增珍珠（500）、金條（1000）、鑽石（1500）；若有金錢素材目錄則與現有金錢載入方式一致。
- [x] 1.3 新增寶箱怪產物設定（產出間隔與開啟動畫起始時間可調：`CHEST_PRODUCE_INTERVAL_*`、`CHEST_OPENING_START_*`）；產物圖片來自 `resource/money/寶箱怪產物/`（`寶箱怪產物_珍珠/金條/鑽石.png`）；口中產物縮放 `CHEST_PRODUCE_IMAGE_SCALE` 可調。
- [x] 1.4 龍蝦素材目錄改為「龍蝦」，程式引用更新；`config.py` 支援使用者初始金錢（`INITIAL_MONEY`）。

## 2. 金幣解鎖流程
- [x] 2.1 在 `aquarium_window.py` 商店/寵物購買邏輯中：若寵物配置含 `unlock_money`，則解鎖條件改為「當前金幣 ≥ unlock_money」且點擊購買時扣款並標記已解鎖；不檢查 unlock_species。
- [x] 2.2 存檔中持久化「已解鎖寵物」名單（含金幣解鎖之寵物），載入時還原解鎖狀態。

## 3. 寶箱怪寵物
- [x] 3.1 在 `pet.py` 新增寶箱怪寵物類別：固定位置 (400, 280)、不移動；使用「1_開啟」動畫，預設第 0 幀。
- [x] 3.2 實作產物計時：接近週期結束前開始播放開啟動畫（2:51→001…2:59→009），於 006 幀時在寶箱嘴部 (400, 300) 顯示產物圖片並在水族箱加入可拾取金錢；產物顯示直至使用者拾取，拾取後重置為 000 幀並重新計時。
- [x] 3.3 在 `aquarium_window.py` 召喚寵物時若為 `寶箱怪`，載入「1_開啟」動畫並創建寶箱怪實例，加入寵物列表並參與繪製與更新。
- [x] 3.4 寶箱怪不拾取魚種產出的金錢（`check_money_collision` 回傳空）；產物由滑鼠碰撞拾取後消失，價值加入總金額並呼叫寶箱怪 `reset_after_collect()`。
- [x] 3.5 寶箱怪產物圖片載入自 `resource/money/寶箱怪產物/`，檔名 `寶箱怪產物_珍珠.png` 等；`_load_produce_images` 使用本地 `all_produce_types = ["珍珠", "金條", "鑽石"]`。

## 4. 拼布魚寵物
- [x] 4.1 在 `pet.py` 新增拼布魚寵物類別：使用 5_吃飽游泳、6_吃飽吃、7_吃飽轉向；具移動、朝向、吃飼料偵測與飽足度，移動速度由 `PATCHWORK_FISH_SPEED` 可調。
- [x] 4.2 飽足度計數與飼料成長度一致（吃哪種飼料就加該飼料的 `FEED_GROWTH_POINTS`）；滿飽足度時觸發街頭表演（快樂 buff），持續時間由 `PET_UPGRADE_CONFIG` 拼布魚 `performance_duration_by_level` 可調（30/40/50 秒）。
- [x] 4.3 在 `aquarium_window.py` 召喚拼布魚時載入對應動畫並創建拼布魚實例，參與飼料碰撞檢測與更新。
- [x] 4.4 拼布魚不拾取魚種產出的金錢（`check_money_collision` 回傳空）；碰到飼料後播放 6_吃飽吃 素材。

## 5. 快樂 buff 與魚大便間隔
- [x] 5.1 拼布魚街頭表演期間，水族箱維護快樂 buff 剩餘時間（幀數），每幀遞減。
- [x] 5.2 魚類大便計時使用「有效間隔」：若快樂 buff 啟用則間隔乘以 `PATCHWORK_HAPPY_BUFF_POOP_MULTIPLIER`（預設 0.5，即縮短 50%）。
- [x] 5.3 快樂 buff 期間，受影響的魚頭上持續繪製 `resource/money/UI/拼布魚_愛心.png`，縮放由 `PATCHWORK_HAPPY_BUFF_HEART_SCALE` 可調。

## 6. 商店與 UI
- [x] 6.1 商店有魚種 tab／寵物 tab；寵物列表顯示寶箱怪、拼布魚；解鎖條件顯示「2000 金幣」「3500 金幣」；已解鎖且未召喚時顯示「召喚」；各項目有簡短描述（龍蝦／寶箱怪／拼布魚）。
- [x] 6.2 已解鎖之金幣解鎖寵物存檔/讀檔正確還原，重開後仍可召喚。
- [x] 6.3 寵物預覽圖 64×64，縮放影像於容器內不裁切；寶箱預覽使用縮放邏輯確保完整顯示。
- [x] 6.4 已召喚時顯示當前等級與升級按鈕（升級 (+1)/(+2) 及費用）；已滿級顯示「已滿級」禁用按鈕；`update_items` 接受 `pet_levels` 參數。

## 7. 寵物升級系統
- [x] 7.1 在 `config.py` 新增 `PET_UPGRADE_CONFIG`（各寵物 upgrade_costs、max_level；龍蝦 speed_by_level、拼布魚 performance_duration_by_level）。
- [x] 7.2 在 `TransparentAquariumWindow` 維護 `_pet_levels`，存檔/載入 `pet_levels`；召喚時依等級套用效果（龍蝦速度、寶箱怪 chest_level、拼布魚 set_level）。
- [x] 7.3 實作 `_on_pet_upgrade_requested`：扣款、更新 `_pet_levels`、對寵物實例套用新等級（龍蝦 speed、寶箱怪 set_level、拼布魚 set_level）、刷新商店、自動存檔。
- [x] 7.4 商店連接 `pet_upgrade_requested` 信號，升級按鈕依費用與當前金錢啟用/禁用。

## 8. 金錢 UI 與其他
- [x] 8.1 金錢總量顯示改為金幣堆圖示（`resource/money/UI/UI_金幣堆-removebg-preview.png`）＋金額文字（`$數字`）。
- [x] 8.2 寶箱怪產物拾取：滑鼠碰撞時產物消失，對應價值加入總金額，並重置寶箱怪計時與動畫。
