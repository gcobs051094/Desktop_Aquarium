## ADDED Requirements

### Requirement: 魚類移動方向系統
魚類 SHALL 使用基於水平方向（horizontal_direction）和垂直方向（vertical_direction）的移動系統。

- **水平方向**：-1（左）、0（靜止）、1（右）
- **垂直方向**：-1（上）、0（靜止）、1（下）
- 組合後可產生 8 個方向的移動：左、右、上、下、左上、左下、右上、右下

#### Scenario: 向左移動
- **WHEN** horizontal_direction = -1, vertical_direction = 0
- **THEN** 魚向左移動，頭部朝左，使用原始素材

#### Scenario: 向右移動
- **WHEN** horizontal_direction = 1, vertical_direction = 0
- **THEN** 魚向右移動，頭部朝右，使用鏡像素材

#### Scenario: 向上移動（保持當前朝向）
- **WHEN** horizontal_direction = 0, vertical_direction = -1
- **THEN** 魚向上移動，頭部方向保持不變

#### Scenario: 向下移動（保持當前朝向）
- **WHEN** horizontal_direction = 0, vertical_direction = 1
- **THEN** 魚向下移動，頭部方向保持不變

#### Scenario: 左上移動
- **WHEN** horizontal_direction = -1, vertical_direction = -1
- **THEN** 魚向左上移動，頭部朝左，使用原始素材

#### Scenario: 右下移動
- **WHEN** horizontal_direction = 1, vertical_direction = 1
- **THEN** 魚向右下移動，頭部朝右，使用鏡像素材

---

### Requirement: 頭部朝向與素材使用規則
魚類 SHALL 根據頭部朝向（facing_left）決定素材的鏡像方式。

- **素材假設**：所有游泳素材的魚頭部朝左
- **轉向素材假設**：轉向動畫為從「頭朝左」轉到「頭朝右」

#### Scenario: 頭朝左時顯示游泳動畫
- **WHEN** facing_left = True 且狀態為游泳
- **THEN** 直接使用游泳素材，不鏡像

#### Scenario: 頭朝右時顯示游泳動畫
- **WHEN** facing_left = False 且狀態為游泳
- **THEN** 水平鏡像游泳素材

---

### Requirement: 轉向動畫播放規則
當魚的水平移動方向改變（左↔右）時 SHALL 播放轉向動畫。

- **轉向素材**：動畫內容為從「頭朝左」轉到「頭朝右」
- **左轉右**：直接播放轉向素材
- **右轉左**：鏡像播放轉向素材

#### Scenario: 從左轉向右
- **WHEN** 魚從 facing_left=True 變為 facing_left=False
- **THEN** 播放轉向動畫（不鏡像）

#### Scenario: 從右轉向左
- **WHEN** 魚從 facing_left=False 變為 facing_left=True
- **THEN** 播放轉向動畫（水平鏡像）

#### Scenario: 純垂直移動不觸發轉向
- **WHEN** 水平方向保持不變（horizontal_direction 不變），僅垂直方向改變
- **THEN** 不播放轉向動畫，保持當前頭部朝向

---

### Requirement: 邊界碰撞處理
魚類 SHALL 在碰到水族箱邊界時改變移動方向。

#### Scenario: 碰到左邊界
- **WHEN** 魚的位置超出水族箱左邊界
- **THEN** 將 horizontal_direction 設為 1（向右），觸發轉向動畫

#### Scenario: 碰到右邊界
- **WHEN** 魚的位置超出水族箱右邊界
- **THEN** 將 horizontal_direction 設為 -1（向左），觸發轉向動畫

#### Scenario: 碰到上邊界
- **WHEN** 魚的位置超出水族箱上邊界
- **THEN** 將 vertical_direction 設為 1（向下），不改變水平方向

#### Scenario: 碰到下邊界
- **WHEN** 魚的位置超出水族箱下邊界
- **THEN** 將 vertical_direction 設為 -1（向上），不改變水平方向

---

### Requirement: 隨機方向變更
魚類 SHALL 隨機改變移動方向以模擬自然游動行為。

#### Scenario: 隨機改變移動方向
- **WHEN** 距離上次方向變更超過設定的間隔時間
- **THEN** 隨機選擇新的 horizontal_direction 和 vertical_direction
- **AND** 如果水平方向改變（左↔右），觸發轉向動畫

#### Scenario: 維持一定機率繼續直行
- **WHEN** 隨機方向變更觸發
- **THEN** 有一定機率保持當前方向不變，避免過於頻繁改變

---

### Requirement: 位置精度與座標系統
魚類 SHALL 使用浮點數座標系統儲存位置，確保小數位移能夠正確累積。

- **位置儲存**：使用 `QPointF`（浮點數座標）儲存位置
- **繪製座標**：繪製時將浮點數座標轉換為整數像素座標
- **位移計算**：每幀位移可能為小數（例如 0.67 像素/幀），必須累積而非截斷

#### Scenario: 小數位移累積
- **WHEN** 魚以速度 0.67 像素/幀向右移動
- **THEN** 位置從 642.0 → 642.67 → 643.34 → 644.01，正確累積移動
- **AND** 不會因為 `int()` 截斷導致位置卡在 642

#### Scenario: 繪製時座標轉換
- **WHEN** 魚的位置為 `QPointF(642.67, 172.34)`
- **THEN** 繪製矩形使用 `int(642.67)` 和 `int(172.34)` 計算像素位置
- **AND** 內部位置仍保持浮點精度，下一幀繼續累積

---

### Requirement: 邊界處理穩定性
邊界處理 SHALL 在 widget 尚未完成佈局時也能正確運作。

- **無效矩形檢查**：當 `aquarium_rect` 寬度或高度小於最小值時，跳過邊界處理
- **備援機制**：`aquarium_window.py` 在 widget rect 無效時使用視窗的 `aquarium_rect`

#### Scenario: 無效矩形時不處理邊界
- **WHEN** `aquarium_rect.width() < 120` 或 `aquarium_rect.height() < 120`
- **THEN** 邊界處理直接返回 `new_x, new_y`，不進行任何 clamp 或方向改變
- **AND** 避免因無效邊界值導致魚被錯誤地限制移動

#### Scenario: Widget rect 無效時使用備援
- **WHEN** `AquariumWidget.rect()` 寬度或高度小於 100
- **THEN** 使用 `window.aquarium_rect` 作為邊界矩形
- **AND** 確保魚的邊界判斷使用有效的矩形
