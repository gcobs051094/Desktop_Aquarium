# Tasks: 重構魚類吃飼料行為規則

## Implementation Checklist

- [x] 在 `Fish` 類別中新增 `feed_cooldown_timer` 屬性（初始化為 0.0）
- [x] 在 `Fish.update()` 中實作冷卻計時器遞減邏輯（每幀減 1/60 秒）
- [x] 修改 `Fish.update()` 中的飼料檢測邏輯，冷卻期間不追飼料
- [x] 新增 `Fish.consume_feed()` 方法：只觸發吃的行為（計數、成長、冷卻），不播放動畫
- [x] 修改 `Fish.eat_feed()` 方法：動畫結束時才開始冷卻計時
- [x] 修改 `AquariumWidget._check_feed_collisions()` 碰撞檢測邏輯：
  - [x] 吃動畫播放中碰到飼料：跳過，飼料不消失
  - [x] 冷卻期間碰到飼料：跳過，不觸發吃的行為
  - [x] 轉向中碰到飼料：呼叫 `consume_feed()`，只觸發行為
  - [x] 游泳狀態碰到飼料：呼叫 `eat_feed()`，觸發行為與動畫
- [x] 更新相關方法的 docstring，說明新的行為規則
