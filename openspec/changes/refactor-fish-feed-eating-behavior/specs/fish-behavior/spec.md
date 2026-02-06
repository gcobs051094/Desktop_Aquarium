## ADDED Requirements

### Requirement: 吃飼料行為與動畫分離
魚類的「吃飼料」SHALL 分為「行為」與「動畫」兩個獨立概念。

- **吃的行為**：飼料消失、成長度增加、計數增加、啟動 1 秒冷卻
- **吃的動畫**：播放吃飼料動畫（僅在特定情況下播放）

#### Scenario: 觸發吃的行為
- **WHEN** 魚觸發吃的行為（無論是否有動畫）
- **THEN** 飼料消失（`feed.is_eaten = True`）
- **AND** 成長度根據飼料類型增加
- **AND** 吃飼料計數 +1
- **AND** 啟動 1 秒冷卻計時器（`feed_cooldown_timer = 1.0`）

#### Scenario: 播放吃的動畫
- **WHEN** 魚在游泳狀態下觸發吃飼料
- **THEN** 播放吃飼料動畫（`state = "eating"`）
- **AND** 動畫播放期間魚不移動
- **AND** 動畫結束後回到游泳狀態（`state = "swim"`）
- **AND** 動畫結束時才開始 1 秒冷卻計時

---

### Requirement: 吃飼料冷卻機制
魚類 SHALL 在觸發吃的行為後，必須等待 1 秒才能再次觸發吃的行為。

- **冷卻計時器**：`feed_cooldown_timer`（秒），> 0 時表示在冷卻中
- **冷卻期間行為**：不追飼料、不觸發吃的行為

#### Scenario: 冷卻期間不追飼料
- **WHEN** `feed_cooldown_timer > 0`
- **THEN** 不執行 `_find_nearest_feed()` 和 `_move_towards_feed()`
- **AND** 魚繼續正常游泳或轉向行為

#### Scenario: 冷卻期間碰到飼料
- **WHEN** 魚在冷卻期間（`feed_cooldown_timer > 0`）碰到飼料
- **THEN** 不觸發任何吃的行為
- **AND** 飼料繼續存在並往下移動

#### Scenario: 冷卻計時器遞減
- **WHEN** 每幀更新（約 60 FPS）
- **THEN** `feed_cooldown_timer` 減去 `1.0 / 60.0` 秒
- **AND** 當 `feed_cooldown_timer < 0` 時設為 `0.0`

---

### Requirement: 吃動畫播放中碰到飼料
魚類 SHALL 在播放吃動畫期間，如果碰到飼料，不觸發任何吃的行為。

#### Scenario: 吃動畫中碰到飼料
- **WHEN** 魚的狀態為 `"eating"`（正在播放吃動畫）
- **AND** 魚的碰撞矩形與飼料碰撞矩形相交
- **THEN** 不呼叫 `eat_feed()` 或 `consume_feed()`
- **AND** 不設定 `feed.is_eaten = True`
- **AND** 飼料繼續存在並依原本邏輯往下移動

---

### Requirement: 轉向中碰到飼料
魚類 SHALL 在轉向過程中碰到飼料時，只觸發吃的行為，不播放吃動畫。

#### Scenario: 轉向中碰到飼料（不在冷卻中）
- **WHEN** 魚的狀態為 `"turning"`（正在轉向）
- **AND** `feed_cooldown_timer <= 0`（不在冷卻中）
- **AND** 魚的碰撞矩形與飼料碰撞矩形相交
- **THEN** 呼叫 `consume_feed(feed)`，只觸發吃的行為
- **AND** 不改變魚的狀態（繼續轉向，`state` 仍為 `"turning"`）
- **AND** 不播放吃動畫
- **AND** 飼料消失（`feed.is_eaten = True`）
- **AND** 成長度增加、計數增加、啟動 1 秒冷卻

#### Scenario: 轉向中碰到飼料（在冷卻中）
- **WHEN** 魚的狀態為 `"turning"`（正在轉向）
- **AND** `feed_cooldown_timer > 0`（在冷卻中）
- **AND** 魚的碰撞矩形與飼料碰撞矩形相交
- **THEN** 不觸發任何吃的行為
- **AND** 飼料繼續存在並往下移動

---

### Requirement: 游泳狀態下吃飼料
魚類 SHALL 在游泳狀態下碰到飼料時，觸發吃的行為與動畫。

#### Scenario: 游泳中碰到飼料（不在冷卻中）
- **WHEN** 魚的狀態為 `"swim"`（游泳）
- **AND** `feed_cooldown_timer <= 0`（不在冷卻中）
- **AND** 魚的碰撞矩形與飼料碰撞矩形相交
- **THEN** 呼叫 `eat_feed(feed)`，觸發吃的行為與動畫
- **AND** 魚的狀態變為 `"eating"`，開始播放吃動畫
- **AND** 飼料消失（`feed.is_eaten = True`）
- **AND** 成長度增加、計數增加
- **AND** 動畫結束時啟動 1 秒冷卻

#### Scenario: 游泳中碰到飼料（在冷卻中）
- **WHEN** 魚的狀態為 `"swim"`（游泳）
- **AND** `feed_cooldown_timer > 0`（在冷卻中）
- **AND** 魚的碰撞矩形與飼料碰撞矩形相交
- **THEN** 不觸發任何吃的行為
- **AND** 飼料繼續存在並往下移動

---

### Requirement: 碰撞檢測優先順序
碰撞檢測 SHALL 按照以下優先順序處理：

1. **吃動畫播放中**：跳過碰撞，飼料不消失
2. **冷卻期間**：跳過碰撞，不觸發吃的行為
3. **轉向中**：觸發吃的行為（無動畫）
4. **游泳狀態**：觸發吃的行為與動畫

#### Scenario: 碰撞檢測流程
- **WHEN** 檢測到魚與飼料碰撞
- **THEN** 依序檢查：
  1. 若 `state == "eating"` → 跳過此顆飼料
  2. 若 `feed_cooldown_timer > 0` → 跳過此顆飼料
  3. 若 `state == "turning"` → 呼叫 `consume_feed(feed)`
  4. 否則 → 呼叫 `eat_feed(feed)`
- **AND** 一旦觸發吃的行為，立即 `break`（一條魚一次只能吃一個飼料）
