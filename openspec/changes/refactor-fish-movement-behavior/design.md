# Design: 重構魚類移動行為系統

## Context
重構前的魚類移動系統使用角度（0-360°）來表示方向，導致：
1. 頭部朝向與移動方向的對應邏輯複雜
2. 需要多處角度修正程式碼
3. 位置使用整數座標，小數位移無法累積

## Goals
- 簡化移動方向系統，使用離散的水平/垂直方向
- 確保頭部朝向與移動方向一致
- 支援小數位移的正確累積
- 提高程式碼可維護性

## Decisions

### Decision: 使用離散方向系統而非連續角度
**選擇**：使用 `horizontal_direction` (-1/0/1) 和 `vertical_direction` (-1/0/1) 而非角度

**理由**：
- 更直觀：直接對應「左/右/上/下」
- 簡化邏輯：不需要複雜的角度轉換和修正
- 易於除錯：方向值一目了然

**替代方案**：保持角度系統但簡化邏輯
- **缺點**：仍需處理角度到方向的轉換，複雜度較高

---

### Decision: 使用 QPointF 而非 QPoint 儲存位置
**選擇**：使用 `QPointF`（浮點數座標）儲存魚的位置

**理由**：
- **關鍵問題**：魚的速度通常為小數（如 0.67 像素/幀）
- **問題場景**：使用 `QPoint(int(x), int(y))` 時，每幀位移被截斷
  - 例如：642.67 → `int(642.67)` = 642，下一幀又從 642 開始
  - 結果：魚永遠無法累積移動，看起來卡住
- **解決方案**：使用 `QPointF` 保持浮點精度，繪製時再轉換為整數

**實作細節**：
```python
# 儲存：使用浮點數
self.position = QPointF(new_x, new_y)

# 繪製：轉換為整數
cx, cy = int(self.position.x()), int(self.position.y())
display_rect = QRect(cx - w//2, cy - h//2, w, h)
```

**替代方案**：累積小數部分
- **缺點**：需要額外的累積變數，增加複雜度

---

### Decision: 邊界處理的無效矩形檢查
**選擇**：當 `aquarium_rect` 無效時跳過邊界處理

**理由**：
- Widget 尚未完成佈局時，`rect()` 可能返回 `(0,0,0,0)`
- 無效矩形會導致 `right_bound` 和 `bottom_bound` 為負數
- 負數邊界會讓所有位置都被判定為「出界」，導致魚被錯誤地限制

**實作**：
```python
min_side = 2 * self.boundary_margin + 20
if aquarium_rect.width() < min_side or aquarium_rect.height() < min_side:
    return new_x, new_y  # 跳過邊界處理
```

**備援機制**：在 `aquarium_window.py` 中，當 widget rect 無效時使用視窗的 `aquarium_rect`

---

### Decision: 轉向動畫只在水平方向改變時觸發
**選擇**：只有當 `horizontal_direction` 從 -1 變 1 或從 1 變 -1 時才播放轉向動畫

**理由**：
- 轉向動畫是「左轉右」或「右轉左」的視覺效果
- 純垂直移動（上/下）不改變頭部朝向，不需要轉向動畫
- 簡化狀態機邏輯

**實作**：
```python
if old_direction != 0 and new_direction != 0 and old_direction != new_direction:
    # 需要轉向（左↔右）
    target_facing_left = new_direction < 0
    if target_facing_left != self.facing_left:
        self._start_turning(target_facing_left)
```

---

## Risks / Trade-offs

### Risk: 浮點數精度累積誤差
**風險**：長時間運行後，浮點數可能累積誤差

**緩解**：
- Qt 的 `QPointF` 使用 `double` 精度，誤差極小
- 繪製時轉換為整數，視覺上無影響
- 邊界處理會定期「校正」位置（clamp 到邊界）

### Trade-off: 離散方向 vs 平滑轉向
**權衡**：離散方向系統無法實現平滑的角度轉向

**選擇**：優先考慮簡潔性和可維護性
- 遊戲中魚的移動不需要精確的角度控制
- 離散方向已足夠表現自然的游動行為

---

## Migration Plan
1. ✅ 重寫 `Fish` 類別的方向系統
2. ✅ 將 `QPoint` 改為 `QPointF`
3. ✅ 更新邊界處理邏輯
4. ✅ 添加調試輸出驗證行為
5. ⏳ 移除調試輸出（可選）

---

## Open Questions
無
