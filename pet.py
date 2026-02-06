#!/usr/bin/env python3
"""
寵物類別

處理寵物的動畫、位置和行為邏輯。
寵物素材預設頭部朝左；轉向素材為由左往右（左面轉到右面）。
"""

import random
import math
from pathlib import Path
from typing import Callable, List, Optional, Tuple
from PyQt6.QtCore import QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QPixmap
from config import (
    PET_CONFIG,
    DEFAULT_PET_ANIMATION_SPEED,
    FISH_FEED_CHASE_SPEED_MULTIPLIER,
    FISH_FEED_COOLDOWN_SEC,
    FEED_GROWTH_POINTS,
    CHEST_PRODUCE_INTERVAL_FRAMES,
    CHEST_OPENING_START_FRAMES,
    CHEST_PRODUCE_IMAGE_SCALE,
    PATCHWORK_FISH_MAX_SATIATION,
    PATCHWORK_FISH_PERFORMANCE_DURATION_FRAMES,
    PATCHWORK_FISH_SPEED,
    MONEY_COLLECT_ANIMATION_DURATION_SEC,
    MONEY_COLLECT_VELOCITY_Y,
)


def load_pet_animation(pet_dir: Path, behavior: str) -> List[QPixmap]:
    """
    載入寵物動畫幀
    
    Args:
        pet_dir: 寵物目錄路徑（如 resource/pet/龍蝦）
        behavior: 行為名稱（如 "1_游動"、"2_轉向"）
    
    Returns:
        動畫幀列表
    """
    behavior_dir = pet_dir / behavior
    if not behavior_dir.exists():
        return []
    
    frame_files = sorted(behavior_dir.glob("*.png"))
    frames = []
    for frame_file in frame_files:
        pixmap = QPixmap(str(frame_file))
        if not pixmap.isNull():
            frames.append(pixmap)
    return frames


class Pet:
    """
    寵物基礎類別
    
    管理寵物的位置、動畫和基本行為。
    """
    
    def __init__(
        self,
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        position: QPoint,
        speed: float = 0.3,
        scale: float = 1.0,
        pet_name: str = "pet",
    ):
        """
        初始化寵物
        
        Args:
            swim_frames: 游動動畫幀（頭朝左）
            turn_frames: 轉向動畫幀（由左往右）
            position: 初始位置
            speed: 移動速度（像素/幀）
            scale: 顯示縮放倍率
            pet_name: 寵物名稱
        """
        self.swim_frames = swim_frames
        self.turn_frames = turn_frames
        self.position = QPointF(float(position.x()), float(position.y()))
        self.speed = speed
        self.scale = scale
        self.pet_name = pet_name
        
        # 方向：-1=左, 1=右
        self.horizontal_direction = random.choice([-1, 1])
        self.facing_left = self.horizontal_direction < 0
        
        # 行為狀態
        self.state = "swim"  # "swim" | "turning"
        self.turn_progress = 0.0  # 轉向動畫進度
        self.turning_to_left: Optional[bool] = None  # 轉向目標朝向
        
        # 動畫計時
        self.animation_timer = 0.0
        # 從 PET_CONFIG 讀取動畫速度，若無則使用預設值
        pet_config = PET_CONFIG.get(self.pet_name, {})
        self.animation_speed = pet_config.get("animation_speed", DEFAULT_PET_ANIMATION_SPEED)
    
    def update(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        """
        更新寵物狀態
        
        Args:
            aquarium_rect: 水族箱矩形區域
            feeds: 飼料列表（可選，供會吃飼料的寵物如拼布魚使用）
        """
        # 更新動畫
        if self.swim_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.swim_frames):
                self.animation_timer = 0.0
        
        # 子類別實作具體的移動邏輯
        self._update_movement(aquarium_rect, feeds)
    
    def _update_movement(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        """
        更新移動邏輯（子類別覆寫）
        
        Args:
            aquarium_rect: 水族箱矩形區域
            feeds: 飼料列表（可選）
        """
        pass
    
    def get_current_frame(self) -> Optional[QPixmap]:
        """取得當前動畫幀"""
        if self.state == "turning" and self.turn_frames:
            idx = int(self.turn_progress * len(self.turn_frames))
            idx = min(idx, len(self.turn_frames) - 1)
            return self.turn_frames[idx]
        elif self.swim_frames:
            idx = int(self.animation_timer) % len(self.swim_frames)
            return self.swim_frames[idx]
        return None
    
    def get_display_rect(self) -> Optional[QRect]:
        """取得顯示矩形"""
        frame = self.get_current_frame()
        if not frame:
            return None
        
        w = int(frame.width() * self.scale)
        h = int(frame.height() * self.scale)
        x = int(self.position.x() - w // 2)
        y = int(self.position.y() - h // 2)
        return QRect(x, y, w, h)
    
    def get_should_mirror(self) -> bool:
        """判斷是否需要鏡像（頭朝右時需要鏡像）"""
        if self.state == "turning":
            # 轉向動畫：如果目標朝向與素材方向相反，需要鏡像
            if self.turning_to_left is not None:
                return not self.turning_to_left
        # 游動狀態：頭朝右時需要鏡像
        return not self.facing_left
    
    def check_money_collision(self, moneys: List) -> List[Tuple]:
        """
        檢查與金錢物件的碰撞
        
        Args:
            moneys: 金錢物件列表
        
        Returns:
            碰撞的金錢物件與金額的列表 [(money, value), ...]
        """
        collisions = []
        pet_rect = self.get_display_rect()
        if not pet_rect:
            return collisions
        
        for money in moneys:
            if money.is_collected:
                continue
            money_rect = money.get_display_rect()
            if money_rect and pet_rect.intersects(money_rect):
                from config import get_money_value
                value = get_money_value(money.money_name)
                collisions.append((money, value))
        
        return collisions


class ChestMonsterPet(Pet):
    """
    寶箱怪寵物
    
    固定於 (400, 280)，不移動。初始為關閉（幀 000）；接近 3 分鐘時播放幀 001～009
    （2:51→001、2:52→002…2:59→009），3 分鐘到時依等級隨機產出並停在 009：
    +0 只產珍珠；+1 珍珠或金條隨機；+2 珍珠或金條或鑽石隨機。
    直到玩家拾取產物後重置為 000 並重新計時。
    """

    def __init__(
        self,
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        position: QPoint,
        spawn_money_cb: Callable[[str], None],
        scale: float = 0.5,
        pet_name: str = "寶箱怪",
        chest_level: int = 0,
    ):
        super().__init__(
            swim_frames=swim_frames,
            turn_frames=turn_frames,
            position=position,
            speed=0,
            scale=scale,
            pet_name=pet_name,
        )
        self.spawn_money_cb = spawn_money_cb
        self.timer_frames = 0
        self.state_chest = "idle"  # "idle" | "opening" | "waiting_collect"
        # 根據等級決定可產出的物品（0=珍珠，1=珍珠+金條，2=珍珠+金條+鑽石）
        self._level = chest_level
        if self._level == 0:
            self._produce_types = ["珍珠"]
        elif self._level == 1:
            self._produce_types = ["珍珠", "金條"]
        else:  # level >= 2
            self._produce_types = ["珍珠", "金條", "鑽石"]
        self._current_produce_type: Optional[str] = None
        self._produce_images: dict[str, QPixmap] = {}
        self._load_produce_images()
        # 消失動畫狀態（產物被收集時觸發）
        self.is_produce_collecting = False  # 是否正在播放產物消失動畫
        self.produce_collect_timer = 0.0  # 消失動畫計時器（幀數）
        self.produce_collect_duration = MONEY_COLLECT_ANIMATION_DURATION_SEC * 60.0  # 消失動畫持續時間（秒轉幀數，60fps）
        self.produce_collect_opacity = 1.0  # 消失動畫透明度（1.0 -> 0.0）
        self.produce_collect_position = QPointF(398, 300)  # 消失動畫位置（初始為產物位置）
        self.produce_collect_velocity_y = MONEY_COLLECT_VELOCITY_Y  # 消失動畫往上移動速度（像素/幀，負值表示往上）

    def _load_produce_images(self) -> None:
        """載入寶箱怪產物圖片（珍珠、金條、鑽石皆載入以支援升級後產物）"""
        all_produce_types = ["珍珠", "金條", "鑽石"]
        pet_file = Path(__file__)
        resource_dir = pet_file.parent / "resource" / "money" / "寶箱怪產物"
        if not resource_dir.exists():
            print(f"[寶箱怪] 產物目錄不存在: {resource_dir}")
            return
        for produce_type in all_produce_types:
            image_path = resource_dir / f"寶箱怪產物_{produce_type}.png"
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                if not pixmap.isNull():
                    self._produce_images[produce_type] = pixmap
        print(f"[寶箱怪] 產物圖片載入完成，共 {len(self._produce_images)} 張")

    def _update_movement(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        """寶箱怪不移動，位置固定"""
        pass

    def update(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        # 處理產物消失動畫
        if self.is_produce_collecting:
            self.produce_collect_timer += 1.0
            # 往上移動
            self.produce_collect_position.setY(self.produce_collect_position.y() + self.produce_collect_velocity_y)
            # 計算透明度（從1.0漸變到0.0）
            progress = self.produce_collect_timer / self.produce_collect_duration
            self.produce_collect_opacity = max(0.0, 1.0 - progress)
            # 動畫結束後重置寶箱怪
            if self.produce_collect_timer >= self.produce_collect_duration:
                self.reset_after_collect()
                self.is_produce_collecting = False
            return
        
        if self.state_chest == "waiting_collect":
            return
        self.timer_frames += 1
        if self.state_chest == "idle":
            if self.timer_frames >= CHEST_OPENING_START_FRAMES:
                self.state_chest = "opening"
        if self.state_chest == "opening":
            # 在006幀時產出產物（2:51→001, 2:52→002... 2:54→006）
            elapsed = self.timer_frames - CHEST_OPENING_START_FRAMES
            step = elapsed // 60  # 每秒一幀
            if step == 6 and not hasattr(self, "_produced"):  # 006幀時產出
                name = random.choice(self._produce_types)
                self._current_produce_type = name
                print(f"[寶箱怪] 在006幀產出產物: {name}, 當前產物類型: {self._current_produce_type}")
                print(f"[寶箱怪] 產物圖片字典: {list(self._produce_images.keys())}")
                self.spawn_money_cb(name)
                self._produced = True
            # 到達009幀時進入等待拾取狀態
            if step >= 9:
                self.state_chest = "waiting_collect"

    def get_current_frame(self) -> Optional[QPixmap]:
        if not self.swim_frames:
            return None
        if self.state_chest == "idle":
            return self.swim_frames[0]
        if self.state_chest == "waiting_collect":
            return self.swim_frames[min(9, len(self.swim_frames) - 1)]
        # opening: 2:51→001, 2:52→002 ... 2:59→009
        elapsed = self.timer_frames - CHEST_OPENING_START_FRAMES
        step = elapsed // 60  # 每秒一幀
        idx = min(9, 1 + step)
        return self.swim_frames[min(idx, len(self.swim_frames) - 1)]

    def get_produce_image(self) -> Optional[QPixmap]:
        """獲取當前產物圖片（在waiting_collect狀態且step >= 6時顯示），已應用縮放"""
        raw_image = None
        if self.state_chest == "waiting_collect" and self._current_produce_type:
            raw_image = self._produce_images.get(self._current_produce_type)
            if raw_image is None:
                print(f"[寶箱怪] 警告：waiting_collect狀態但找不到產物圖片: {self._current_produce_type}")
        # 在opening狀態且step >= 6時也顯示
        elif self.state_chest == "opening":
            elapsed = self.timer_frames - CHEST_OPENING_START_FRAMES
            step = elapsed // 60
            if step >= 6 and self._current_produce_type:
                raw_image = self._produce_images.get(self._current_produce_type)
                if raw_image is None:
                    print(f"[寶箱怪] 警告：opening狀態step={step}但找不到產物圖片: {self._current_produce_type}")
        
        # 應用縮放
        if raw_image:
            scale = CHEST_PRODUCE_IMAGE_SCALE
            scaled_width = int(raw_image.width() * scale)
            scaled_height = int(raw_image.height() * scale)
            if scaled_width > 0 and scaled_height > 0:
                scaled = raw_image.scaled(
                    scaled_width,
                    scaled_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                #print(f"[寶箱怪] 產物圖片縮放: {raw_image.width()}x{raw_image.height()} -> {scaled_width}x{scaled_height} (scale={scale})")
                return scaled
            else:
                print(f"[寶箱怪] 警告：縮放後尺寸無效: {scaled_width}x{scaled_height}")
        return None

    def get_produce_position(self) -> QPointF:
        """獲取產物顯示位置（消失動畫期間使用動畫位置）"""
        if self.is_produce_collecting:
            return self.produce_collect_position
        return QPointF(398, 300)
    
    def start_produce_collect_animation(self) -> None:
        """開始產物消失動畫（被收集時呼叫）"""
        if not self.is_produce_collecting and self._current_produce_type:
            self.is_produce_collecting = True
            self.produce_collect_timer = 0.0
            self.produce_collect_opacity = 1.0
            self.produce_collect_position = QPointF(398, 300)  # 從產物位置開始
    
    def get_produce_opacity(self) -> float:
        """獲取產物透明度（用於消失動畫）"""
        if self.is_produce_collecting:
            return self.produce_collect_opacity
        return 1.0

    def reset_after_collect(self) -> None:
        """玩家拾取產物後重置計時與動畫（消失動畫結束後自動呼叫）"""
        self.timer_frames = 0
        self.state_chest = "idle"
        self._current_produce_type = None
        if hasattr(self, "_produced"):
            delattr(self, "_produced")

    def set_level(self, level: int) -> None:
        """升級時更新等級與可產出物品（+0=珍珠；+1=珍珠或金條隨機；+2=珍珠或金條或鑽石隨機）"""
        self._level = min(2, max(0, level))
        if self._level == 0:
            self._produce_types = ["珍珠"]
        elif self._level == 1:
            self._produce_types = ["珍珠", "金條"]
        else:
            self._produce_types = ["珍珠", "金條", "鑽石"]

    def check_money_collision(self, moneys: List) -> List[Tuple]:
        """寶箱怪不拾取金錢（魚種產出的金幣/金錢），返回空列表"""
        return []


class LobsterPet(Pet):
    """
    龍蝦寵物
    
    在水族箱底部水平走動，自動拾取金錢。
    """
    
    def __init__(
        self,
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        position: QPoint,
        speed: float = 0.2,  # 慢速
        scale: float = 0.6,
    ):
        """
        初始化龍蝦寵物
        
        Args:
            swim_frames: 游動動畫幀
            turn_frames: 轉向動畫幀
            position: 初始位置（應在水族箱底部）
            speed: 移動速度（慢速）
            scale: 顯示縮放倍率
        """
        super().__init__(
            swim_frames=swim_frames,
            turn_frames=turn_frames,
            position=position,
            speed=speed,
            scale=scale,
            pet_name="龍蝦",
        )
        
        # 底部距離（距離底部多少像素）
        self.bottom_margin = 40
    
    def _update_movement(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        """
        更新龍蝦的底部水平移動
        
        Args:
            aquarium_rect: 水族箱矩形區域
            feeds: 飼料列表（龍蝦不使用）
        """
        # 計算目標 Y 位置（底部上方一定距離）
        target_y = aquarium_rect.bottom() - self.bottom_margin
        
        # 如果不在目標 Y 位置，先移動到目標位置
        if abs(self.position.y() - target_y) > 1:
            if self.position.y() < target_y:
                self.position.setY(self.position.y() + self.speed)
            else:
                self.position.setY(self.position.y() - self.speed)
            return
        
        # 保持在目標 Y 位置
        self.position.setY(target_y)
        
        # 處理轉向動畫
        if self.state == "turning":
            self.turn_progress += 0.15
            if self.turn_progress >= 1.0:
                # 轉向完成
                self.state = "swim"
                self.facing_left = self.turning_to_left if self.turning_to_left is not None else not self.facing_left
                self.horizontal_direction = -1 if self.facing_left else 1
                self.turning_to_left = None
                self.turn_progress = 0.0
            return
        
        # 水平移動
        frame = self.get_current_frame()
        if frame:
            w = int(frame.width() * self.scale)
        else:
            w = 50  # 預設寬度
        
        # 檢查邊界
        left_bound = aquarium_rect.left() + w // 2
        right_bound = aquarium_rect.right() - w // 2
        
        # 如果到達邊界，開始轉向
        if self.horizontal_direction < 0 and self.position.x() <= left_bound:
            self.state = "turning"
            self.turning_to_left = False  # 轉向右
            self.turn_progress = 0.0
        elif self.horizontal_direction > 0 and self.position.x() >= right_bound:
            self.state = "turning"
            self.turning_to_left = True  # 轉向左
            self.turn_progress = 0.0
        else:
            # 正常移動
            self.position.setX(self.position.x() + self.horizontal_direction * self.speed)


class PatchworkFishPet(Pet):
    """
    拼布魚寵物
    
    行為與魚種相同：會游泳、會進食（吃飼料），但不會大便。
    周圍有飼料時移動速度較快（與魚類追飼料邏輯一致）。
    """

    def __init__(
        self,
        swim_frames: List[QPixmap],
        turn_frames: List[QPixmap],
        position: QPoint,
        speed: float = 0.6,
        scale: float = 0.5,
        pet_name: str = "拼布魚",
        eat_frames: Optional[List[QPixmap]] = None,
        performance_duration_frames: Optional[float] = None,
    ):
        super().__init__(
            swim_frames=swim_frames,
            turn_frames=turn_frames,
            position=position,
            speed=speed,
            scale=scale,
            pet_name=pet_name,
        )
        self.eat_frames = eat_frames if eat_frames else swim_frames
        self.state = "swim"  # "swim" | "turning" | "eating"
        self.eat_progress = 0.0
        self.vertical_direction = random.choice([-1, 0, 1])
        if self.horizontal_direction == 0 and self.vertical_direction == 0:
            self.vertical_direction = random.choice([-1, 1])
        self._speed_multiplier = 1.0
        self.feed_detection_range = 300.0
        self.feed_cooldown_timer = 0.0
        self.direction_timer = 0
        self.direction_change_interval = random.randint(180, 400)
        self.boundary_margin = 50
        # 飽足度系統
        self.satiation = 0  # 當前飽足度
        self.max_satiation = PATCHWORK_FISH_MAX_SATIATION
        self.performance_timer = 0.0  # 街頭表演模式剩餘時間（幀數）
        self.on_performance_start_callback: Optional[Callable[[], None]] = None  # 街頭表演開始回調
        # 依等級的快樂buff持續時間（幀數），由外部設定
        self._performance_duration_frames = PATCHWORK_FISH_PERFORMANCE_DURATION_FRAMES
        # 依等級的快樂buff持續時間（幀數），由呼叫方在創建/升級時設定
        self.performance_duration_frames = performance_duration_frames

    def update(self, aquarium_rect: QRect, feeds: Optional[List] = None) -> None:
        self._speed_multiplier = 1.0
        if self.state == "eating":
            self._update_eating_state()
            self.position = QPointF(self.position.x(), self.position.y())
            return
        if feeds and self.feed_cooldown_timer <= 0:
            nearest_feed = self._find_nearest_feed(feeds)
            if nearest_feed:
                self._move_towards_feed(nearest_feed)
            else:
                if self.state == "swim":
                    self._update_swim_state()
                elif self.state == "turning":
                    self._update_turning_state()
        else:
            if self.state == "swim":
                self._update_swim_state()
            elif self.state == "turning":
                self._update_turning_state()
        dx, dy = self._calculate_movement()
        new_x = self.position.x() + dx
        new_y = self.position.y() + dy
        new_x, new_y = self._handle_boundaries(new_x, new_y, aquarium_rect)
        self.position = QPointF(new_x, new_y)
        if self.feed_cooldown_timer > 0:
            self.feed_cooldown_timer -= 1.0 / 60.0
            if self.feed_cooldown_timer < 0:
                self.feed_cooldown_timer = 0.0
        
        # 街頭表演模式計時（約 60 FPS）
        if self.performance_timer > 0:
            self.performance_timer -= 1.0
            if self.performance_timer <= 0:
                self.performance_timer = 0.0
                print(f"[拼布魚] 街頭表演模式結束")

    def _update_swim_state(self) -> None:
        if self.horizontal_direction != 0:
            expected_facing = self.horizontal_direction < 0
            if self.facing_left != expected_facing:
                self._start_turning(expected_facing)
                return
        if self.swim_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.swim_frames):
                self.animation_timer = 0.0
        self.direction_timer += 1
        if self.direction_timer >= self.direction_change_interval:
            self._random_direction_change()
            self.direction_timer = 0
            self.direction_change_interval = random.randint(180, 400)

    def _update_turning_state(self) -> None:
        """更新轉向狀態（與Fish邏輯一致）"""
        self.turn_progress += 0.15
        if self.turn_frames and self.turn_progress >= len(self.turn_frames):
            # 轉向完成
            self.state = "swim"
            self.facing_left = self.turning_to_left if self.turning_to_left is not None else self.facing_left
            self.turn_progress = 0.0
            # 確保 horizontal_direction 與 facing_left 一致
            if self.facing_left and self.horizontal_direction > 0:
                self.horizontal_direction = -1
            elif not self.facing_left and self.horizontal_direction < 0:
                self.horizontal_direction = 1
            self.turning_to_left = None

    def _update_eating_state(self) -> None:
        """更新吃動作狀態，播完一輪後回到游泳，並開始冷卻（與Fish邏輯一致）"""
        if not self.eat_frames:
            self.state = "swim"
            self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC
            return
        self.eat_progress += 0.2
        if self.eat_progress >= len(self.eat_frames):
            self.state = "swim"
            self.eat_progress = 0.0
            self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC  # 吃完後冷卻期間不追飼料

    def _find_nearest_feed(self, feeds: List) -> Optional[object]:
        min_distance = float("inf")
        nearest = None
        for feed in feeds:
            if getattr(feed, "is_eaten", False):
                continue
            dx = feed.position.x() - self.position.x()
            dy = feed.position.y() - self.position.y()
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < min_distance and distance <= self.feed_detection_range:
                min_distance = distance
                nearest = feed
        return nearest

    def _move_towards_feed(self, feed: object) -> None:
        dx = feed.position.x() - self.position.x()
        dy = feed.position.y() - self.position.y()
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < 5:
            return
        threshold_ratio = 0.3
        threshold = distance * threshold_ratio
        new_h = 1 if dx > 0 else -1 if abs(dx) > threshold else 0
        new_v = 1 if dy > 0 else -1 if abs(dy) > threshold else 0
        if new_h == 0 and new_v == 0:
            if abs(dx) > abs(dy):
                new_h = 1 if dx > 0 else -1
            else:
                new_v = 1 if dy > 0 else -1
        self._change_horizontal_direction(new_h)
        self.vertical_direction = new_v
        self._speed_multiplier = FISH_FEED_CHASE_SPEED_MULTIPLIER
        if self.state == "turning":
            self._update_turning_state()
        elif self.state == "swim" and self.swim_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.swim_frames):
                self.animation_timer = 0.0

    def _calculate_movement(self) -> Tuple[float, float]:
        current_speed = self.speed * self._speed_multiplier
        dx = self.horizontal_direction * current_speed
        dy = self.vertical_direction * current_speed
        if self.horizontal_direction != 0 and self.vertical_direction != 0:
            factor = 1.0 / math.sqrt(2)
            dx *= factor
            dy *= factor
        return dx, dy

    def _handle_boundaries(self, new_x: float, new_y: float, aquarium_rect: QRect) -> Tuple[float, float]:
        frame = self.get_current_frame()
        if not frame:
            return new_x, new_y
        min_side = 2 * self.boundary_margin + 20
        if aquarium_rect.width() < min_side or aquarium_rect.height() < min_side:
            return new_x, new_y
        w = int(frame.width() * self.scale)
        h = int(frame.height() * self.scale)
        half_w, half_h = w // 2, h // 2
        left_bound = aquarium_rect.left() + self.boundary_margin
        right_bound = aquarium_rect.right() - self.boundary_margin
        top_bound = aquarium_rect.top() + self.boundary_margin
        bottom_bound = aquarium_rect.bottom() - self.boundary_margin
        if new_x - half_w < left_bound:
            new_x = left_bound + half_w
            self._change_horizontal_direction(1)
        elif new_x + half_w > right_bound:
            new_x = right_bound - half_w
            self._change_horizontal_direction(-1)
        if new_y - half_h < top_bound:
            new_y = top_bound + half_h
            self.vertical_direction = 1
        elif new_y + half_h > bottom_bound:
            new_y = bottom_bound - half_h
            self.vertical_direction = -1
        return new_x, new_y

    def _change_horizontal_direction(self, new_direction: int) -> None:
        self.horizontal_direction = new_direction
        if new_direction == 0:
            return
        target_facing_left = new_direction < 0
        if target_facing_left != self.facing_left:
            if self.state == "swim":
                self._start_turning(target_facing_left)
            elif self.state == "turning":
                self.turning_to_left = target_facing_left

    def _start_turning(self, turn_to_left: bool) -> None:
        if not self.turn_frames:
            self.facing_left = turn_to_left
            return
        self.state = "turning"
        self.turn_progress = 0.0
        self.turning_to_left = turn_to_left

    def _random_direction_change(self) -> None:
        if random.random() < 0.6:
            new_h = random.choice([-1, 0, 1])
            if new_h == 0 and self.vertical_direction == 0:
                new_h = random.choice([-1, 1])
            self._change_horizontal_direction(new_h)
        if random.random() < 0.5:
            self.vertical_direction = random.choice([-1, 0, 1])
        if self.horizontal_direction == 0 and self.vertical_direction == 0:
            if random.random() < 0.5:
                self._change_horizontal_direction(random.choice([-1, 1]))
            else:
                self.vertical_direction = random.choice([-1, 1])

    def get_current_frame(self) -> Optional[QPixmap]:
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

    def eat_feed(self, feed: Optional[object] = None) -> None:
        """吃到飼料：播放吃動畫，增加飽足度（根據飼料成長度），不觸發大便"""
        self.state = "eating"
        self.eat_progress = 0.0
        self.feed_cooldown_timer = 0.0  # 冷卻在吃動畫結束時才開始
        # 根據飼料類型增加飽足度（與飼料成長度相同）
        if feed and hasattr(feed, 'feed_name'):
            feed_name = feed.feed_name
            growth_points = FEED_GROWTH_POINTS.get(feed_name, 1)  # 預設為1
            old_satiation = self.satiation
            self.satiation = min(self.satiation + growth_points, self.max_satiation)
            print(f"[拼布魚] 吃到飼料({feed_name})，成長度+{growth_points}，飽足度: {old_satiation} -> {self.satiation}/{self.max_satiation}")
            # 檢查是否達到滿飽足度，觸發街頭表演
            if self.satiation >= self.max_satiation:
                self._trigger_performance()
        else:
            # 沒有飼料對象時，預設+1
            if self.satiation < self.max_satiation:
                self.satiation += 1
                print(f"[拼布魚] 吃到飼料（未知類型），飽足度: {self.satiation}/{self.max_satiation}")
                if self.satiation >= self.max_satiation:
                    self._trigger_performance()

    def consume_feed(self, feed: Optional[object] = None) -> None:
        """僅消耗飼料（不播吃動畫），增加飽足度（根據飼料成長度），不觸發大便"""
        self.feed_cooldown_timer = FISH_FEED_COOLDOWN_SEC
        # 根據飼料類型增加飽足度（與飼料成長度相同）
        if feed and hasattr(feed, 'feed_name'):
            feed_name = feed.feed_name
            growth_points = FEED_GROWTH_POINTS.get(feed_name, 1)  # 預設為1
            old_satiation = self.satiation
            self.satiation = min(self.satiation + growth_points, self.max_satiation)
            print(f"[拼布魚] 消耗飼料({feed_name})，成長度+{growth_points}，飽足度: {old_satiation} -> {self.satiation}/{self.max_satiation}")
            # 檢查是否達到滿飽足度，觸發街頭表演
            if self.satiation >= self.max_satiation:
                self._trigger_performance()
        else:
            # 沒有飼料對象時，預設+1
            if self.satiation < self.max_satiation:
                self.satiation += 1
                print(f"[拼布魚] 消耗飼料（未知類型），飽足度: {self.satiation}/{self.max_satiation}")
                if self.satiation >= self.max_satiation:
                    self._trigger_performance()

    def _trigger_performance(self) -> None:
        """觸發街頭表演模式"""
        self.performance_timer = float(self._performance_duration_frames)
        self.satiation = 0  # 重置飽足度
        remaining_sec = int(self.performance_timer / 60)
        print(f"[拼布魚] 街頭表演模式啟動！剩餘時間: {remaining_sec} 秒")
        if self.on_performance_start_callback:
            self.on_performance_start_callback()

    def set_level(self, level: int) -> None:
        """升級時更新快樂buff持續時間（幀數）"""
        from config import PET_UPGRADE_CONFIG
        cfg = PET_UPGRADE_CONFIG.get("拼布魚", {})
        durations = cfg.get("performance_duration_by_level", [30, 40, 50])
        idx = min(level, len(durations) - 1)
        self._performance_duration_frames = durations[idx] * 60  # 秒轉幀

    def get_satiation(self) -> int:
        """獲取當前飽足度"""
        return self.satiation

    def get_performance_remaining_sec(self) -> float:
        """獲取街頭表演模式剩餘時間（秒）"""
        return self.performance_timer / 60.0

    def is_performing(self) -> bool:
        """是否正在街頭表演"""
        return self.performance_timer > 0

    def check_money_collision(self, moneys: List) -> List[Tuple]:
        """拼布魚不拾取金錢，返回空列表"""
        return []

    def get_should_mirror(self) -> bool:
        """
        當前幀是否要水平鏡像（與Fish邏輯一致）
        
        素材規則：
        - 游泳素材：頭朝左，因此頭朝右時需要鏡像
        - 轉向素材：左轉右（不鏡像），右轉左（鏡像）
        - 吃動畫：頭朝右時需要鏡像
        """
        if self.state == "swim" or self.state == "eating":
            # 游泳／吃：頭朝右時鏡像
            return not self.facing_left
        elif self.state == "turning" and self.turning_to_left is not None:
            # 轉向：
            # - 左轉右（turning_to_left=False）：使用原始素材，不鏡像
            # - 右轉左（turning_to_left=True）：鏡像素材
            return self.turning_to_left
        return False
