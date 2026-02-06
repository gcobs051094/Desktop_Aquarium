#!/usr/bin/env python3
"""
魚類類別

處理魚類的動畫、位置和行為邏輯。
素材預設頭部朝左；轉向素材為由左往右（左面轉到右面）。

移動方向系統：
- horizontal_direction: -1（左）、0（靜止）、1（右）
- vertical_direction: -1（上）、0（靜止）、1（下）
- 組合可產生 8 方向移動

鏡像規則：
- 游泳素材頭朝左，頭朝右時鏡像
- 轉向素材為左轉右，右轉左時鏡像
"""

import random
import math
from pathlib import Path
from typing import List, Optional, Tuple, Callable, Dict, Any
from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF
from PyQt6.QtGui import QPixmap, QImage, QTransform, QColor
from config import (
    FEED_GROWTH_POINTS,
    FISH_UPGRADE_THRESHOLDS,
    GROWTH_STAGES,
    BETTA_POOP_CONFIG,
    FISH_DEATH_ANIMATION_DURATION_SEC,
    get_fish_animation_speed,
    FISH_FEED_CHASE_SPEED_MULTIPLIER,
    FISH_FEED_COOLDOWN_SEC,
    GUPPY_MONEY_CHASE_SPEED_MULTIPLIER,
    GUPPY_MONEY_COOLDOWN_SEC,
)


class Fish:
    """
    魚類類別

    管理魚的位置、動畫和游動行為。
    使用水平/垂直方向系統，確保頭部方向與移動方向一致。
    """

    def __init__(
        self,
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        position: QPoint,
        speed: float = 0.5,
        direction: float = 0.0,
        scale: float = 1.25,
        eat_frames: Optional[List[QPixmap]] = None,
        species: Optional[str] = None,
        stage: str = "small",
    ):
        """
        初始化魚類

        Args:
            swim_frames: 游泳動畫幀（頭朝左）
            turn_frames: 轉向動畫幀（由左往右）
            position: 初始位置
            speed: 游動速度（像素/幀）
            direction: 初始游動方向（度數，0° 為向右，僅用於初始化方向）
            scale: 顯示縮放倍率
            eat_frames: 吃飼料動畫幀（頭朝左，可選）
            species: 魚種名稱（如 "puppy"）
            stage: 成長階段（"small", "medium", "large"）
        """
        self.swim_frames = swim_frames
        self.turn_frames = turn_frames
        self.eat_frames = eat_frames if eat_frames else []
        # 使用 QPointF 儲存位置，避免每幀小數位移被 int() 截斷導致魚不移動
        self.position = QPointF(float(position.x()), float(position.y()))
        self.speed = speed
        self.scale = scale

        # 從角度初始化方向（Qt 螢幕座標：X 向右為正，Y 向下為正）
        # 角度定義：0°=右, 90°=下, 180°=左, 270°=上
        # 注意：雖然數學座標 Y 向上為正，但我們的角度定義已經對應螢幕座標
        rad = math.radians(direction)
        cos_val = math.cos(rad)  # 0°=1(右), 180°=-1(左)
        sin_val = math.sin(rad)  # 90°=1(下), 270°=-1(上)
        
        # 設定水平和垂直方向
        self.horizontal_direction = self._quantize_direction(cos_val)  # -1=左, 0=靜止, 1=右
        self.vertical_direction = self._quantize_direction(sin_val)     # -1=上, 0=靜止, 1=下
        
        # 確保至少有一個方向
        if self.horizontal_direction == 0 and self.vertical_direction == 0:
            self.horizontal_direction = random.choice([-1, 1])
        
        # 頭部朝向：根據水平方向決定
        # 如果純垂直移動，隨機決定初始朝向
        if self.horizontal_direction == 0:
            self.facing_left = random.choice([True, False])
        else:
            self.facing_left = self.horizontal_direction < 0

        # 行為狀態
        self.state = "swim"  # "swim" | "turning" | "eating"
        self.turn_progress = 0.0  # 轉向動畫進度
        self.turning_to_left: Optional[bool] = None  # 轉向目標朝向
        self.eat_progress = 0.0  # 吃動作動畫進度

        # 動畫計時
        self.animation_timer = 0.0
        self.animation_speed = get_fish_animation_speed(species or "")

        # 方向變更計時器
        self.direction_timer = 0
        self.direction_change_interval = random.randint(180, 400)

        self.boundary_margin = 50
        
        # 速度倍率（用於朝飼料移動時加速）
        self._speed_multiplier = 1.0
        
        # 檢測飼料的距離閾值
        self.feed_detection_range = 300.0
        
        # 吃飯計數
        self.feed_count = 0  # 吃到的飼料數量
        
        # 吃完飼料後的冷卻時間（秒），此期間不追飼料
        self.feed_cooldown_timer = 0.0
        
        # 成長系統
        self.species = species  # 魚種名稱（如 "puppy"）
        self.stage = stage  # 當前成長階段（"small", "medium", "large"）
        self.growth_points = 0  # 當前成長度
        self.on_upgrade_callback: Optional[Callable] = None  # 升級回調函數

        # 大便行為（各階段鬥魚定時排出金錢）
        poop_key = f"{stage}_{species}" if species else ""
        if poop_key and poop_key in BETTA_POOP_CONFIG:
            _, interval_range = BETTA_POOP_CONFIG[poop_key]
            # 支援範圍間隔：(min, max) 或單一數值（向後兼容）
            if isinstance(interval_range, tuple) and len(interval_range) == 2:
                min_interval, max_interval = interval_range
                # 隨機選擇一個間隔時間，避免同時大便造成卡頓
                self.poop_interval_sec = random.uniform(float(min_interval), float(max_interval))
            else:
                # 向後兼容：單一數值
                self.poop_interval_sec = float(interval_range)
            self.poop_timer = 0.0  # 秒
        else:
            self.poop_interval_sec = 0.0
            self.poop_timer = 0.0
        self.on_poop_callback: Optional[Callable[[str, QPointF], None]] = None  # (money_type, position)
        # 快樂buff：大便間隔倍率（1.0=正常，0.5=間隔縮短50%），由水族箱每幀設定
        self.happy_buff_multiplier = 1.0

        # 鯊魚專用：吃幼年鬥魚後 300 秒內每 30 秒大便魚翅
        self.last_eat_betta_time: Optional[float] = None  # 上次吃幼鬥魚的時間（秒）
        self.next_poop_at: Optional[float] = None  # 下次大便魚翅的時間（秒）

        # 死亡／移除效果：第一幀反轉 xy、灰階，往上緩慢移動並逐漸消失
        self.is_dead = False
        self.death_timer = 0.0  # 秒
        self.death_opacity = 1.0
        self._death_frame: Optional[QPixmap] = None  # 第一幀反轉 xy 灰階，延遲建立

        # 孔雀魚追金錢：每5秒追最近的金錢
        self.money_chase_timer: float = 0.0  # 追金錢計時器（秒）
        self.money_chase_interval: float = 5.0  # 追金錢間隔（秒）
        self.money_touch_cooldown_until: float = 0.0  # 碰觸金錢後的冷卻時間（秒），此時間之前無法再碰觸
        self._current_money_target: Optional[object] = None  # 當前追蹤的金錢目標
        self.current_game_time_sec: float = 0.0   # 由水族箱每幀寫入，供判斷計時器
    
    @staticmethod
    def _quantize_direction(value: float, threshold: float = 0.3) -> int:
        """將連續值量化為 -1, 0, 1"""
        if value > threshold:
            return 1
        elif value < -threshold:
            return -1
        return 0

    def update(self, aquarium_rect: QRect, feeds: Optional[List] = None, prey: Optional[List] = None, moneys: Optional[List] = None) -> None:
        """
        更新魚的狀態與位置。

        Args:
            aquarium_rect: 水族箱矩形
            feeds: 飼料列表（可選）
            prey: 獵物列表（可選，僅鯊魚可進食時使用，用於追幼鬥魚；項目需有 .position）
            moneys: 金錢列表（可選，僅孔雀魚使用，用於追金錢；項目需有 .position）
        """
        # 死亡狀態：只做上移與淡出，不做進食／游泳／轉向／追飼料
        if self.is_dead:
            self._update_death_state()
            return

        # 重置速度倍率
        self._speed_multiplier = 1.0

        # 追逐目標：孔雀魚每5秒追金錢；鯊魚在可進食時追 prey（幼鬥魚），否則不追；其餘魚追飼料
        if self.species == "孔雀魚":
            # 冷卻期間不追金錢，避免黏在同一顆金錢上
            if self.current_game_time_sec < self.money_touch_cooldown_until:
                self._current_money_target = None
                targets = None
            else:
                # 孔雀魚每5秒追最近的金錢（排除已石榴化的金錢）
                self.money_chase_timer += 1.0 / 60.0  # 約 60 FPS
                # 尋找最近的金錢（排除已收集、正在收集、已石榴化、或已觸底的金錢）
                valid_moneys = []
                if moneys:
                    valid_moneys = [
                        m for m in moneys
                        if not (getattr(m, "is_collected", False) or getattr(m, "is_collecting", False))
                        and not (hasattr(m, "money_name") and str(m.money_name).startswith("石榴結晶_"))
                        and getattr(m, "bottom_time", -1) < 0  # 排除已觸底的金錢（bottom_time >= 0 表示已觸底）
                    ]

                # 每5秒重新選擇目標，或當前目標消失時立即重新選擇
                should_reselect = (
                    self.money_chase_timer >= self.money_chase_interval
                    or self._current_money_target is None
                    or self._current_money_target not in valid_moneys
                )

                if should_reselect:
                    if self.money_chase_timer >= self.money_chase_interval:
                        self.money_chase_timer = 0.0

                    if valid_moneys:
                        nearest_money = self._find_nearest_feed(valid_moneys)
                        if nearest_money:
                            self._current_money_target = nearest_money
                            targets = [nearest_money]
                        else:
                            self._current_money_target = None
                            targets = None
                    else:
                        self._current_money_target = None
                        targets = None
                else:
                    # 繼續追當前目標
                    if self._current_money_target in valid_moneys:
                        targets = [self._current_money_target]
                    else:
                        self._current_money_target = None
                        targets = None
        elif self.species == "鯊魚":
            targets = list(prey) if prey else None
        else:
            targets = feeds

        # 吃動作期間不移動
        if self.state == "eating":
            self._update_eating_state()
            self.position = QPointF(self.position.x(), self.position.y())
            return

        # 檢測並朝向最近的目標移動（冷卻期間不追）
        # 注意：鯊魚和孔雀魚不受 feed_cooldown_timer 影響（它們不吃飼料）
        is_chasing_money = False
        can_chase = True
        if self.species not in ("鯊魚", "孔雀魚"):
            # 只有非鯊魚、非孔雀魚的魚種才受 feed_cooldown_timer 限制
            can_chase = (self.feed_cooldown_timer <= 0)
        
        if targets and can_chase:
            nearest_feed = self._find_nearest_feed(targets)
            if nearest_feed:
                # 有目標時，加快速度並朝目標移動
                is_chasing_money = (self.species == "孔雀魚" and targets)
                self._move_towards_feed(nearest_feed, is_chasing_money=is_chasing_money)
            else:
                # 沒有目標時，正常行為
                if self.state == "swim":
                    self._update_swim_state()
                elif self.state == "turning":
                    self._update_turning_state()
        else:
            # 沒有目標列表時，正常行為
            if self.state == "swim":
                self._update_swim_state()
            elif self.state == "turning":
                self._update_turning_state()


        # 計算位移
        dx, dy = self._calculate_movement()
        new_x = self.position.x() + dx
        new_y = self.position.y() + dy

        # 邊界處理
        new_x, new_y = self._handle_boundaries(new_x, new_y, aquarium_rect)

        self.position = QPointF(new_x, new_y)

        # 吃完飼料冷卻計時（約 60 FPS）
        if self.feed_cooldown_timer > 0:
            self.feed_cooldown_timer -= 1.0 / 60.0
            if self.feed_cooldown_timer < 0:
                self.feed_cooldown_timer = 0.0

        # 大便計時：各階段鬥魚定時觸發排出金錢（約 60 FPS，每幀 1/60 秒）
        # 快樂buff時使用縮短後的間隔（happy_buff_multiplier < 1.0）
        if self.poop_interval_sec > 0 and self.on_poop_callback:
            effective_interval = self.poop_interval_sec * (self.happy_buff_multiplier if self.happy_buff_multiplier > 0 else 1.0)
            self.poop_timer += 1.0 / 60.0
            if self.poop_timer >= effective_interval:
                poop_key = f"{self.stage}_{self.species}"
                if poop_key in BETTA_POOP_CONFIG:
                    money_type, interval_range = BETTA_POOP_CONFIG[poop_key]
                    self.on_poop_callback(money_type, QPointF(self.position.x(), self.position.y()))
                    # 每次大便後重新隨機選擇間隔時間，避免同時大便造成卡頓
                    if isinstance(interval_range, tuple) and len(interval_range) == 2:
                        min_interval, max_interval = interval_range
                        self.poop_interval_sec = random.uniform(float(min_interval), float(max_interval))
                self.poop_timer = 0.0

    def _update_swim_state(self) -> None:
        """更新游泳狀態"""
        # 安全檢查：確保 facing_left 與 horizontal_direction 一致
        # （純垂直移動時保持當前朝向，所以只檢查非零的情況）
        if self.horizontal_direction != 0:
            expected_facing = self.horizontal_direction < 0
            if self.facing_left != expected_facing:
                # 不一致，觸發轉向
                self._start_turning(expected_facing)
                return
        
        # 更新游泳動畫
        if self.swim_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.swim_frames):
                self.animation_timer = 0.0
        
        # 定時隨機改變方向
        self.direction_timer += 1
        if self.direction_timer >= self.direction_change_interval:
            self._random_direction_change()
            self.direction_timer = 0
            self.direction_change_interval = random.randint(180, 400)

    def _update_turning_state(self) -> None:
        """更新轉向狀態"""
        self.turn_progress += 0.15
        if self.turn_progress >= len(self.turn_frames):
            # 轉向完成
            self.state = "swim"
            self.facing_left = self.turning_to_left
            self.turn_progress = 0.0
            
            # 確保 horizontal_direction 與 facing_left 一致
            # （防止轉向期間方向又被改變的情況）
            if self.facing_left and self.horizontal_direction > 0:
                self.horizontal_direction = -1
            elif not self.facing_left and self.horizontal_direction < 0:
                self.horizontal_direction = 1
            
            self.turning_to_left = None

    def _update_death_state(self) -> None:
        """死亡效果：往上緩慢移動並逐漸消失（由 config FISH_DEATH_ANIMATION_DURATION_SEC 秒內淡出）"""
        self.death_timer += 1.0 / 60.0
        # 往上緩慢移動（約 0.3 像素/幀）
        self.position.setY(self.position.y() - 0.3)
        # 逐漸消失
        duration = FISH_DEATH_ANIMATION_DURATION_SEC or 2.0
        self.death_opacity = max(0.0, 1.0 - self.death_timer / duration)

    def _build_death_frame(self) -> None:
        """建立死亡用幀：第一幀反轉 xy、灰階；僅對不透明像素做灰階，保留透明（去背）不變。"""
        if self._death_frame is not None:
            return
        src = self.swim_frames[0] if self.swim_frames else None
        if not src or src.isNull():
            self._death_frame = src
            return
        img = src.toImage()
        if img.isNull():
            self._death_frame = src
            return
        # 使用帶 alpha 的格式，灰階化時只改 RGB，保留 alpha（去背處維持透明）
        img = img.convertToFormat(QImage.Format.Format_ARGB32)
        if img.isNull():
            self._death_frame = src
            return
        w, h = img.width(), img.height()
        for y in range(h):
            for x in range(w):
                color = img.pixelColor(x, y)
                alpha = color.alpha()
                if alpha == 0:
                    continue
                r, g, b = color.red(), color.green(), color.blue()
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                img.setPixelColor(x, y, QColor(gray, gray, gray, alpha))
        transform = QTransform().scale(-1, -1)
        flipped = img.transformed(transform)
        self._death_frame = QPixmap.fromImage(flipped)

    def set_dead(self) -> None:
        """標記為死亡／移除，並建立死亡用幀（第一幀反轉 xy、灰階）。"""
        self.is_dead = True
        self.death_timer = 0.0
        self.death_opacity = 1.0
        self._build_death_frame()

    def _update_eating_state(self) -> None:
        """更新吃動作狀態，播完一輪後回到游泳，並開始冷卻"""
        if not self.eat_frames:
            self.state = "swim"
            self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC
            return
        self.eat_progress += 0.2
        if self.eat_progress >= len(self.eat_frames):
            self.state = "swim"
            self.eat_progress = 0.0
            self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC  # 吃完後冷卻期間不追飼料

    def _get_direction_name(self) -> str:
        """取得方向名稱（用於調試）"""
        h = self.horizontal_direction
        v = self.vertical_direction
        
        if h == -1 and v == -1:
            return "左上"
        elif h == -1 and v == 0:
            return "左"
        elif h == -1 and v == 1:
            return "左下"
        elif h == 0 and v == -1:
            return "上"
        elif h == 0 and v == 0:
            return "靜止"
        elif h == 0 and v == 1:
            return "下"
        elif h == 1 and v == -1:
            return "右上"
        elif h == 1 and v == 0:
            return "右"
        elif h == 1 and v == 1:
            return "右下"
        else:
            return f"未知({h},{v})"

    def _find_nearest_feed(self, feeds) -> Optional[object]:
        """找到最近的飼料"""
        if not feeds:
            return None
        
        min_distance = float('inf')
        nearest = None
        
        for feed in feeds:
            dx = feed.position.x() - self.position.x()
            dy = feed.position.y() - self.position.y()
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < min_distance and distance <= self.feed_detection_range:
                min_distance = distance
                nearest = feed
        
        return nearest
    
    def _move_towards_feed(self, feed, is_chasing_money: bool = False) -> None:
        """朝飼料移動（遵循八方向移動邏輯，速度稍快）"""
        dx = feed.position.x() - self.position.x()
        dy = feed.position.y() - self.position.y()
        distance = math.sqrt(dx * dx + dy * dy)
        
        # 如果距離很近，可以停止移動或繼續朝飼料移動
        if distance < 5:
            # 已經到達飼料附近，可以停止或繼續朝其他方向移動
            return
        
        # 計算方向（八方向）
        # 使用相對閾值來量化方向（相對於距離的百分比）
        threshold_ratio = 0.3  # 30%的距離閾值
        threshold = distance * threshold_ratio
        
        # 水平方向
        if abs(dx) > threshold:
            new_h = 1 if dx > 0 else -1  # 右或左
        else:
            new_h = 0  # 靜止
        
        # 垂直方向
        if abs(dy) > threshold:
            new_v = 1 if dy > 0 else -1  # 下或上
        else:
            new_v = 0  # 靜止
        
        # 確保至少有一個方向在移動
        if new_h == 0 and new_v == 0:
            # 如果兩個方向都接近0，選擇較大的那個方向
            if abs(dx) > abs(dy):
                new_h = 1 if dx > 0 else -1
            else:
                new_v = 1 if dy > 0 else -1
        
        # 更新方向
        self._change_horizontal_direction(new_h)
        self.vertical_direction = new_v
        
        # 加速：速度倍率設為配置值（朝目標移動時加速）
        # 孔雀魚追金錢時使用更快的速度倍率
        if is_chasing_money:
            self._speed_multiplier = GUPPY_MONEY_CHASE_SPEED_MULTIPLIER
        else:
            self._speed_multiplier = FISH_FEED_CHASE_SPEED_MULTIPLIER
        
        # 如果正在轉向，繼續轉向動畫
        if self.state == "turning":
            self._update_turning_state()
        elif self.state == "swim":
            # 更新游泳動畫
            if self.swim_frames:
                self.animation_timer += self.animation_speed
                if self.animation_timer >= len(self.swim_frames):
                    self.animation_timer = 0.0
    
    def _calculate_movement(self) -> Tuple[float, float]:
        """
        計算移動向量（螢幕座標：X 向右為正，Y 向下為正）。
        horizontal_direction=1 → dx>0 往右；vertical_direction=1 → dy>0 往下。
        """
        # 應用速度倍率
        current_speed = self.speed * self._speed_multiplier
        
        dx = self.horizontal_direction * current_speed
        dy = self.vertical_direction * current_speed
        
        # 斜向移動時正規化速度（保持一致的速度感）
        if self.horizontal_direction != 0 and self.vertical_direction != 0:
            factor = 1.0 / math.sqrt(2)
            dx *= factor
            dy *= factor
        
        # 調試：驗證移動方向（可移除）
        '''
        if abs(dx) > 0.1 or abs(dy) > 0.1:
            direction_name = self._get_direction_name()
            facing = "左" if self.facing_left else "右"
            state = self.state
            print(f"移動: 方向={direction_name}, 頭朝={facing}, 狀態={state}, h={self.horizontal_direction}, v={self.vertical_direction}, dx={dx:.2f}, dy={dy:.2f}, 位置=({self.position.x()}, {self.position.y()})")
        '''
        return dx, dy

    def _handle_boundaries(self, new_x: float, new_y: float, aquarium_rect: QRect) -> Tuple[float, float]:
        """
        處理邊界碰撞（螢幕座標：左<右、上<下，right/bottom 為邊界內側）。
        若 aquarium_rect 無效（尚未佈局），不進行邊界處理，避免誤判導致魚只往左/上。
        """
        frame = self._get_current_frame_raw()
        if not frame:
            return new_x, new_y

        # 無效矩形時不處理邊界，避免 right_bound/bottom_bound 為負導致永遠判定出界
        min_side = 2 * self.boundary_margin + 20
        if aquarium_rect.width() < min_side or aquarium_rect.height() < min_side:
            return new_x, new_y
        
        w = int(frame.width() * self.scale)
        h = int(frame.height() * self.scale)
        half_w, half_h = w // 2, h // 2
        
        # Qt QRect: left()/top() 為左上，right()=left()+width()-1，bottom()=top()+height()-1
        left_bound = aquarium_rect.left() + self.boundary_margin
        right_bound = aquarium_rect.right() - self.boundary_margin
        top_bound = aquarium_rect.top() + self.boundary_margin
        bottom_bound = aquarium_rect.bottom() - self.boundary_margin

        original_x, original_y = new_x, new_y
        boundary_hit = False

        # 左邊界：出界則 clamp 並改為向右 (horizontal_direction=1)
        if new_x - half_w < left_bound:
            new_x = left_bound + half_w
            self._change_horizontal_direction(1)
            boundary_hit = True
        # 右邊界：出界則 clamp 並改為向左 (horizontal_direction=-1)
        elif new_x + half_w > right_bound:
            new_x = right_bound - half_w
            self._change_horizontal_direction(-1)
            boundary_hit = True
        
        # 上邊界：出界則 clamp 並改為向下 (vertical_direction=1)
        if new_y - half_h < top_bound:
            new_y = top_bound + half_h
            self.vertical_direction = 1
            boundary_hit = True
        # 下邊界：出界則 clamp 並改為向上 (vertical_direction=-1)
        elif new_y + half_h > bottom_bound:
            new_y = bottom_bound - half_h
            self.vertical_direction = -1
            boundary_hit = True

        # 調試：如果位置被邊界處理改變，輸出資訊
        '''
        if boundary_hit or abs(new_x - original_x) > 0.01 or abs(new_y - original_y) > 0.01:
            print(f"邊界處理: 原始=({original_x:.2f}, {original_y:.2f}), 處理後=({new_x:.2f}, {new_y:.2f}), "
                  f"邊界=[L:{left_bound}, R:{right_bound}, T:{top_bound}, B:{bottom_bound}], "
                  f"half_w={half_w}, half_h={half_h}, rect=({aquarium_rect.left()}, {aquarium_rect.top()}, {aquarium_rect.width()}, {aquarium_rect.height()})")
        '''
        return new_x, new_y

    def _change_horizontal_direction(self, new_direction: int) -> None:
        """
        改變水平方向，必要時觸發轉向動畫
        
        Args:
            new_direction: 新的水平方向 (-1, 0, 1)
        """
        old_direction = self.horizontal_direction
        self.horizontal_direction = new_direction
        
        # 如果新方向是靜止(0)，保持當前朝向
        if new_direction == 0:
            return
        
        # 計算目標朝向
        target_facing_left = new_direction < 0
        
        # 如果朝向需要改變
        if target_facing_left != self.facing_left:
            if self.state == "swim":
                # 在游泳狀態，播放轉向動畫
                self._start_turning(target_facing_left)
            elif self.state == "turning":
                # 在轉向中，更新轉向目標
                self.turning_to_left = target_facing_left
        # 如果朝向已經正確，無需額外處理

    def _start_turning(self, turn_to_left: bool) -> None:
        """開始轉向動畫"""
        if not self.turn_frames:
            # 沒有轉向素材，直接改變朝向
            self.facing_left = turn_to_left
            return
        
        self.state = "turning"
        self.turn_progress = 0.0
        self.turning_to_left = turn_to_left

    def _random_direction_change(self) -> None:
        """隨機改變移動方向"""
        # 隨機選擇新的水平和垂直方向
        # 有較高機率保持當前方向
        
        # 水平方向變更
        if random.random() < 0.6:  # 60% 機率改變
            new_h = random.choice([-1, 0, 1])
            # 避免兩個方向都是靜止
            if new_h == 0 and self.vertical_direction == 0:
                new_h = random.choice([-1, 1])
            self._change_horizontal_direction(new_h)
        
        # 垂直方向變更
        if random.random() < 0.5:  # 50% 機率改變
            self.vertical_direction = random.choice([-1, 0, 1])
        
        # 確保至少有一個方向在移動
        if self.horizontal_direction == 0 and self.vertical_direction == 0:
            if random.random() < 0.5:
                # 注意：不要先設定 horizontal_direction 再呼叫 _change_horizontal_direction
                new_h = random.choice([-1, 1])
                self._change_horizontal_direction(new_h)
            else:
                self.vertical_direction = random.choice([-1, 1])

    def _get_current_frame_raw(self) -> Optional[QPixmap]:
        """取得當前要畫的幀（不考慮鏡像）。"""
        if self.is_dead and self._death_frame is not None:
            return self._death_frame
        if self.state == "eating" and self.eat_frames:
            idx = min(int(self.eat_progress), len(self.eat_frames) - 1)
            return self.eat_frames[idx]
        if self.state == "turning" and self.turn_frames:
            idx = min(int(self.turn_progress), len(self.turn_frames) - 1)
            return self.turn_frames[idx]
        if self.swim_frames:
            idx = int(self.animation_timer) % len(self.swim_frames)
            return self.swim_frames[idx]
        return None

    def get_current_frame(self) -> Optional[QPixmap]:
        """給繪製用的當前幀。"""
        return self._get_current_frame_raw()

    def get_should_mirror(self) -> bool:
        """
        當前幀是否要水平鏡像。
        
        素材規則：
        - 游泳素材：頭朝左，因此頭朝右時需要鏡像
        - 轉向素材：左轉右（不鏡像），右轉左（鏡像）
        - 死亡幀：已含反轉，不再鏡像
        """
        if self.is_dead:
            return False
        if self.state == "swim" or self.state == "eating":
            # 游泳／吃：頭朝右時鏡像
            return not self.facing_left
        elif self.state == "turning" and self.turning_to_left is not None:
            # 轉向：
            # - 左轉右（turning_to_left=False）：使用原始素材，不鏡像
            # - 右轉左（turning_to_left=True）：鏡像素材
            return self.turning_to_left
        return False

    def get_display_rect(self) -> Optional[QRect]:
        """取得繪製矩形（已含縮放）。"""
        frame = self._get_current_frame_raw()
        if not frame:
            return None
        w = int(frame.width() * self.scale)
        h = int(frame.height() * self.scale)
        cx, cy = int(self.position.x()), int(self.position.y())
        return QRect(
            cx - w // 2,
            cy - h // 2,
            w,
            h,
        )
    
    def consume_feed(self, feed=None) -> None:
        """
        僅消耗飼料（計數、成長度、冷卻），不播放吃動畫。
        用於轉向中碰到飼料時：飼料消失但魚不中斷轉向。
        仍會：1) 依飼料類型增加成長度並檢查升級
              2) 啟動冷卻，此期間不追飼料
        """
        self.feed_count += 1
        self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC  # 吃完後冷卻期間不追飼料（與 eat_feed 規則一致）
        if feed and hasattr(feed, 'feed_name'):
            feed_name = feed.feed_name
            growth_points = FEED_GROWTH_POINTS.get(feed_name, 0)
            if growth_points > 0:
                self.growth_points += growth_points
                self._check_upgrade()

    def eat_feed(self, feed=None) -> None:
        """
        魚吃到飼料，計數+1 並觸發吃動作，增加成長度
        
        Args:
            feed: 飼料對象（可選），用於獲取飼料類型計算成長度
        """
        self.feed_count += 1
        self.state = "eating"
        self.eat_progress = 0.0
        # 冷卻在吃動畫結束時才開始（見 _update_eating_state）
        
        # 根據飼料類型增加成長度
        if feed and hasattr(feed, 'feed_name'):
            feed_name = feed.feed_name
            growth_points = FEED_GROWTH_POINTS.get(feed_name, 0)
            if growth_points > 0:
                self.growth_points += growth_points
                # 檢查是否需要升級
                self._check_upgrade()
    
    def _check_upgrade(self) -> None:
        """檢查是否需要升級，如果需要則觸發升級回調"""
        if not self.species:
            print(f"[升級檢查] 魚沒有設置 species，跳過升級檢查")
            return
        
        if not self.on_upgrade_callback:
            print(f"[升級檢查] 魚種 {self.species} 階段 {self.stage} 沒有設置升級回調函數，跳過升級檢查")
            return
        
        # 獲取該魚種的升級閾值
        thresholds = FISH_UPGRADE_THRESHOLDS.get(self.species)
        if not thresholds:
            print(f"[升級檢查] 魚種 {self.species} 沒有配置升級閾值")
            return
        
        # 檢查當前階段是否需要升級
        current_threshold = thresholds.get(self.stage)
        print(f"[升級檢查] 魚種: {self.species}, 階段: {self.stage}, 成長度: {self.growth_points}, 閾值: {current_threshold}")
        
        if current_threshold and self.growth_points >= current_threshold:
            # 找到下一個階段
            try:
                current_index = GROWTH_STAGES.index(self.stage)
                if current_index < len(GROWTH_STAGES) - 1:
                    next_stage = GROWTH_STAGES[current_index + 1]
                    print(f"[升級檢查] 觸發升級: {self.species} {self.stage} -> {next_stage}")
                    # 觸發升級回調
                    self.on_upgrade_callback(self, next_stage)
                else:
                    print(f"[升級檢查] 已經是最高階段，無法升級")
            except ValueError:
                # 當前階段不在 GROWTH_STAGES 中，不處理
                print(f"[升級檢查] 階段 {self.stage} 不在 GROWTH_STAGES 中")
                pass
        else:
            if current_threshold:
                print(f"[升級檢查] 成長度 {self.growth_points} < 閾值 {current_threshold}，尚未達到升級條件")
            else:
                print(f"[升級檢查] 階段 {self.stage} 沒有配置升級閾值")
    
    def set_upgrade_callback(self, callback: Callable) -> None:
        """設置升級回調函數"""
        self.on_upgrade_callback = callback

    def set_poop_callback(self, callback: Callable[[str, QPointF], None]) -> None:
        """設置大便回調函數（各階段鬥魚定時排出金錢時呼叫，參數：money_type, position）"""
        self.on_poop_callback = callback
    
    def to_dict(self) -> Dict[str, Any]:
        """
        將 Fish 實例轉換為字典（用於儲存）
        
        Returns:
            包含魚類狀態的字典
        """
        # 從水平和垂直方向計算角度（度數）
        # horizontal_direction: -1=左, 0=靜止, 1=右
        # vertical_direction: -1=上, 0=靜止, 1=下
        # 角度定義：0°=右, 90°=下, 180°=左, 270°=上
        if self.horizontal_direction == 0 and self.vertical_direction == 0:
            # 如果沒有方向，使用 facing_left 決定
            direction = 180.0 if self.facing_left else 0.0
        else:
            # 計算角度
            if self.horizontal_direction == 0:
                # 純垂直移動
                direction = 90.0 if self.vertical_direction > 0 else 270.0
            elif self.vertical_direction == 0:
                # 純水平移動
                direction = 180.0 if self.horizontal_direction < 0 else 0.0
            else:
                # 對角移動
                dx = self.horizontal_direction
                dy = self.vertical_direction
                # atan2(y, x) 計算角度，但需要轉換為我們的座標系統
                # 我們的座標：X 向右為正，Y 向下為正
                # atan2 的座標：X 向右為正，Y 向上為正
                # 所以需要將 dy 取負
                angle_rad = math.atan2(-dy, dx)
                direction = math.degrees(angle_rad)
                # 確保角度在 0-360 範圍內
                if direction < 0:
                    direction += 360.0
        
        d = {
            "species": self.species,
            "stage": self.stage,
            "growth_points": self.growth_points,
            "position": {
                "x": float(self.position.x()),
                "y": float(self.position.y()),
            },
            "direction": direction,
            "facing_left": self.facing_left,
            "speed": self.speed,
            "scale": self.scale,
        }
        if self.species == "鯊魚":
            if self.last_eat_betta_time is not None:
                d["last_eat_betta_time"] = self.last_eat_betta_time
            if self.next_poop_at is not None:
                d["next_poop_at"] = self.next_poop_at
        return d
    
    @classmethod
    def from_dict(
        cls,
        fish_dict: Dict[str, Any],
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        eat_frames: Optional[List[QPixmap]] = None,
    ) -> 'Fish':
        """
        從字典重建 Fish 實例（用於載入）
        
        Args:
            fish_dict: 包含魚類狀態的字典
            swim_frames: 游泳動畫幀
            turn_frames: 轉向動畫幀
            eat_frames: 吃動畫幀（可選）
            
        Returns:
            Fish 實例
        """
        # 提取位置
        pos_dict = fish_dict.get("position", {"x": 0, "y": 0})
        position = QPoint(int(pos_dict.get("x", 0)), int(pos_dict.get("y", 0)))
        
        # 提取其他屬性
        direction = fish_dict.get("direction", 0.0)
        species = fish_dict.get("species")
        stage = fish_dict.get("stage", "small")
        growth_points = fish_dict.get("growth_points", 0)
        speed = fish_dict.get("speed", 0.5)
        scale = fish_dict.get("scale", 1.25)
        
        # 創建 Fish 實例
        fish = cls(
            swim_frames=swim_frames,
            turn_frames=turn_frames,
            position=position,
            speed=speed,
            direction=direction,
            scale=scale,
            eat_frames=eat_frames,
            species=species,
            stage=stage,
        )
        
        # 恢復成長度
        fish.growth_points = growth_points
        
        # 恢復 facing_left（因為 __init__ 可能會根據 direction 重新計算）
        if "facing_left" in fish_dict:
            fish.facing_left = fish_dict["facing_left"]

        # 鯊魚：恢復吃幼鬥魚／大便魚翅計時
        if species == "鯊魚":
            fish.last_eat_betta_time = fish_dict.get("last_eat_betta_time")
            fish.next_poop_at = fish_dict.get("next_poop_at")
        
        return fish


def load_fish_animation(fish_dir: Path, behavior: str = "5_吃飽游泳") -> List[QPixmap]:
    """載入單一行為的動畫幀。"""
    behavior_dir = fish_dir / behavior
    if not behavior_dir.exists():
        behavior_dirs = [d for d in fish_dir.iterdir() if d.is_dir()]
        if behavior_dirs:
            behavior_dir = behavior_dirs[0]
        else:
            return []

    frame_files = sorted(behavior_dir.glob("*.png"))
    frames = []
    for frame_file in frame_files:
        pixmap = QPixmap(str(frame_file))
        if not pixmap.isNull():
            frames.append(pixmap)
    return frames


def load_swim_and_turn(
    fish_dir: Path,
    swim_behavior: str = "5_吃飽游泳",
    turn_behavior: str = "7_吃飽轉向",
) -> Tuple[List[QPixmap], List[QPixmap]]:
    """載入游泳與轉向動畫，回傳 (swim_frames, turn_frames)。"""
    swim = load_fish_animation(fish_dir, swim_behavior)
    turn = load_fish_animation(fish_dir, turn_behavior)
    if not turn and swim:
        turn = swim[:]  # 沒有轉向素材時用游泳代替
    return swim, turn
