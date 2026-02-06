## MODIFIED Requirements

### Requirement: 魚類吃飼料冷卻機制
魚類 SHALL 在觸發吃的行為後，必須等待配置的冷卻時間才能再次觸發吃的行為。冷卻時間 SHALL 在 `config.py` 中定義為 `FISH_FEED_COOLDOWN_SEC`（預設 1.0 秒）。

- **冷卻計時器**：`feed_cooldown_timer`（秒），> 0 時表示在冷卻中
- **冷卻期間行為**：不追飼料、不觸發吃的行為
- **配置化**：冷卻時間由 `config.FISH_FEED_COOLDOWN_SEC` 定義，可在配置檔中調整

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

#### Scenario: 觸發吃的行為後啟動冷卻
- **WHEN** 魚觸發吃的行為（無論是否有動畫）
- **THEN** `feed_cooldown_timer` 設為 `FISH_FEED_COOLDOWN_SEC`
- **AND** 冷卻期間不追飼料

---

### Requirement: 鯊魚與孔雀魚不受飼料冷卻限制
鯊魚和孔雀魚 SHALL 不受 `feed_cooldown_timer` 的影響，可以隨時追擊各自的目標。

- **鯊魚**：可以隨時追擊幼鬥魚，不受 `feed_cooldown_timer` 限制，只受 `SHARK_EAT_BETTA_INTERVAL_SEC`（300秒）限制
- **孔雀魚**：可以隨時追擊金錢，不受 `feed_cooldown_timer` 限制，只受 `GUPPY_MONEY_COOLDOWN_SEC`（5秒）限制

#### Scenario: 鯊魚不受飼料冷卻限制
- **WHEN** 鯊魚的 `feed_cooldown_timer > 0`
- **THEN** 鯊魚仍然可以追擊幼鬥魚（prey）
- **AND** 鯊魚的追擊行為只受 `last_eat_betta_time` 和 `SHARK_EAT_BETTA_INTERVAL_SEC` 限制

#### Scenario: 孔雀魚不受飼料冷卻限制
- **WHEN** 孔雀魚的 `feed_cooldown_timer > 0`
- **THEN** 孔雀魚仍然可以追擊金錢（moneys）
- **AND** 孔雀魚的追擊行為只受 `money_touch_cooldown_until` 和 `GUPPY_MONEY_COOLDOWN_SEC` 限制

#### Scenario: 其他魚種仍受冷卻限制
- **WHEN** 非鯊魚、非孔雀魚的魚種的 `feed_cooldown_timer > 0`
- **THEN** 該魚種不追擊飼料
- **AND** 冷卻期間不觸發吃的行為
