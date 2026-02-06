#!/usr/bin/env python3
"""
透明水族箱視窗應用程式

創建一個透明視窗，其中包含一個水族箱區域，魚類可以在其中游動，
使用者可以與水族箱區域進行互動（如投放飼料）。
"""

import sys
import random
import math
from pathlib import Path
from typing import Callable, Optional, List, Tuple, Dict
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QFrame,
    QMenu, QSizePolicy, QLabel, QSlider, QHBoxLayout,
    QScrollArea, QTabWidget, QComboBox, QDialog, QDialogButtonBox,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QRect, QPoint, QPointF, QTimer, pyqtSignal, QEvent
from PyQt6.QtGui import QPainter, QPixmap, QColor, QMouseEvent, QPaintEvent, QRegion, QAction, QFont, QImage, QIcon, QPen
from fish import Fish, load_swim_and_turn, load_fish_animation
from pet import Pet, LobsterPet, ChestMonsterPet, PatchworkFishPet, load_pet_animation
from config import (
    FEED_GROWTH_POINTS,
    FEED_UNLOCK_CONFIG,
    get_feed_counter_interval_sec,
    MONEY_VALUE,
    get_money_value,
    FEED_COST,
    CHEST_FEED_ITEMS,
    POMEGRANATE_FIXED_HUE,
    PET_CONFIG,
    PET_UPGRADE_CONFIG,
    FISH_SHOP_CONFIG,
    TOOL_CONFIG,
    FEED_MACHINE_COLORS,
    FEED_MACHINE_DEFAULT_COLOR,
    FEED_MACHINE_SCALE,
    FEED_MACHINE_AREA_WIDTH,
    FEED_MACHINE_WIDGET_WIDTH,
    FEED_MACHINE_WIDGET_HEIGHT,
    FEED_MACHINE_WIDGET_OFFSET_X,
    FEED_MACHINE_WIDGET_OFFSET_Y,
    FEED_MACHINE_INTERVAL_SEC,
    FEED_MACHINE_FEED_IMAGE_SIZE,
    FEED_MACHINE_FEED_IMAGE_OFFSET_X,
    FEED_MACHINE_FEED_IMAGE_OFFSET_Y,
    FEED_MACHINE_EXIT_X_RATIO,
    FEED_MACHINE_EXIT_X_OFFSET,
    FEED_MACHINE_TARGET_X_MIN_RATIO,
    FEED_MACHINE_TARGET_X_MAX_RATIO,
    get_fish_scale,
    get_fish_behaviors,
    get_feed_scale,
    get_money_scale,
    get_fish_speed_range,
    get_fish_animation_speed,
    get_feed_fall_speed,
    get_feed_animation_speed,
    get_money_fall_speed,
    get_money_animation_speed,
    DEFAULT_PET_SPEED,
    DEFAULT_PET_ANIMATION_SPEED,
    FISH_FEED_CHASE_SPEED_MULTIPLIER,
    SHARK_EAT_BETTA_INTERVAL_SEC,
    SHARK_POOP_INTERVAL_SEC,
    SHARK_POOP_DURATION_SEC,
    NUCLEAR_DEATH_CHANCE,
    FISH_DEATH_ANIMATION_DURATION_SEC,
    MONEY_COLLECT_ANIMATION_DURATION_SEC,
    MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER,
    MONEY_COLLECT_VELOCITY_Y,
    SMALL_BETTA_COST,
)
from game_state import load, save, get_default_state


class Feed:
    """
    飼料類別
    
    管理飼料的位置、動畫和狀態。
    支援拋物線軌跡（用於投食機自動投食）。
    """
    
    def __init__(self, position: QPoint, feed_frames: List[QPixmap], feed_name: str, scale: float = 0.6, 
                 target_position: Optional[QPointF] = None, is_parabolic: bool = False):
        """
        初始化飼料
        
        Args:
            position: 飼料初始位置
            feed_frames: 飼料動畫幀列表
            feed_name: 飼料名稱（用於計算成長度）
            scale: 顯示縮放倍率
            target_position: 目標位置（拋物線終點，用於投食機自動投食）
            is_parabolic: 是否使用拋物線軌跡
        """
        self.position = QPointF(float(position.x()), float(position.y()))
        self.feed_frames = feed_frames
        self.feed_name = feed_name  # 飼料類型名稱
        self.scale = scale
        self.animation_timer = 0.0
        self.animation_speed = get_feed_animation_speed(feed_name)
        self.lifetime = 0  # 飼料存在時間（幀數）
        self.max_lifetime = 600  # 最大存在時間（約10秒，60fps）
        self.fall_speed = get_feed_fall_speed(feed_name)  # 下落速度（像素/幀）
        self.is_eaten = False  # 是否被吃掉
        
        # 拋物線軌跡參數
        self.is_parabolic = is_parabolic
        self.target_position = target_position  # 目標位置（拋物線終點）
        self.parabolic_progress = 0.0  # 拋物線進度（0.0 到 1.0）
        self.parabolic_speed = 0.02  # 拋物線移動速度（每幀增加的進度）
        self.start_position = QPointF(self.position)  # 起始位置
        self.parabolic_height = 100.0  # 拋物線最高點的高度（相對於起始和終點的中間）
        
    def update(self, aquarium_rect: QRect) -> None:
        """
        更新飼料狀態
        
        Args:
            aquarium_rect: 水族箱矩形（用於檢測是否落到底部）
        """
        # 更新動畫
        if self.feed_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.feed_frames):
                self.animation_timer = 0.0
        
        # 處理拋物線軌跡
        if self.is_parabolic and self.target_position:
            self.parabolic_progress += self.parabolic_speed
            if self.parabolic_progress >= 1.0:
                # 到達目標位置，切換為正常下落
                self.position = QPointF(self.target_position)
                self.is_parabolic = False
            else:
                # 計算拋物線位置
                # 使用二次貝塞爾曲線：起點 -> 最高點 -> 終點
                t = self.parabolic_progress
                
                # 線性插值：起點到終點
                x = self.start_position.x() * (1 - t) + self.target_position.x() * t
                y_base = self.start_position.y() * (1 - t) + self.target_position.y() * t
                
                # 添加拋物線高度（在 t=0.5 時達到最高點）
                # 使用 sin 函數來創建平滑的拋物線
                height_factor = math.sin(t * math.pi)  # 0 到 1 再到 0
                y = y_base - self.parabolic_height * height_factor
                
                self.position = QPointF(x, y)
        else:
            # 正常下落
            self.position.setY(self.position.y() + self.fall_speed)
        
        # 檢查是否碰到水族箱下方邊界上面一點（預留一點即消失）
        frame = self.get_current_frame()
        if frame:
            h = int(frame.height() * self.scale)
            bottom_margin = 24  # 飼料在底邊上方此距離內即消失
            if self.position.y() + h // 2 >= aquarium_rect.bottom() - bottom_margin:
                self.lifetime = self.max_lifetime
        
        # 增加存在時間
        self.lifetime += 1
        
    def is_expired(self) -> bool:
        """檢查飼料是否已過期或被吃掉"""
        return self.is_eaten or self.lifetime >= self.max_lifetime
        
    def get_current_frame(self) -> Optional[QPixmap]:
        """取得當前動畫幀"""
        if not self.feed_frames:
            return None
        idx = int(self.animation_timer) % len(self.feed_frames)
        return self.feed_frames[idx]
        
    def get_display_rect(self) -> Optional[QRect]:
        """取得繪製矩形（已含縮放）"""
        frame = self.get_current_frame()
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


class Money:
    """
    金錢類別（魚大便排出的可拾取物）

    與飼料同樣的落下速度與連續動畫，玩家點擊可拾取並增加金錢計數。
    """

    def __init__(
        self,
        position: QPointF,
        money_frames: List[QPixmap],
        money_name: str,
        scale: float = 0.75,
        on_collected_callback: Optional[Callable[[], None]] = None,
    ):
        self.position = QPointF(float(position.x()), float(position.y()))
        self.money_frames = money_frames
        self.money_name = money_name  # 對應 config.MONEY_VALUE 的鍵
        self.scale = scale
        self.on_collected_callback = on_collected_callback
        self.animation_timer = 0.0
        self.animation_speed = get_money_animation_speed(money_name)
        self.lifetime = 0
        self.max_lifetime = 600
        self.fall_speed = get_money_fall_speed(money_name)  # 下落速度（像素/幀）
        self.is_collected = False
        self.bottom_time = -1  # 觸底時間（幀數），-1表示未觸底
        self.bottom_lifetime = 600  # 觸底後存在時間（10秒，60fps = 600幀）
        self.blink_start_time = 420  # 開始閃爍的時間（7秒，60fps = 420幀）
        # 消失動畫狀態（被收集時觸發）
        self.is_collecting = False  # 是否正在播放消失動畫
        self.collect_timer = 0.0  # 消失動畫計時器（幀數）
        self.collect_duration = MONEY_COLLECT_ANIMATION_DURATION_SEC * 60.0  # 消失動畫持續時間（秒轉幀數，60fps）
        self.collect_opacity = 1.0  # 消失動畫透明度（1.0 -> 0.0）
        self.collect_velocity_y = MONEY_COLLECT_VELOCITY_Y  # 消失動畫往上移動速度（像素/幀，負值表示往上）
        self.base_animation_speed = self.animation_speed  # 記錄原始動畫速度
        self.collect_animation_speed_multiplier = MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER  # 消失動畫期間動畫加速倍率

    def update(self, aquarium_rect: QRect) -> None:
        if self.is_collected:
            return
        
        # 處理消失動畫
        if self.is_collecting:
            self.collect_timer += 1.0
            # 加速動畫（動畫速度加快，倍率由配置決定）
            if self.money_frames:
                self.animation_timer += self.base_animation_speed * self.collect_animation_speed_multiplier
                if self.animation_timer >= len(self.money_frames):
                    self.animation_timer = 0.0
            # 往上移動
            self.position.setY(self.position.y() + self.collect_velocity_y)
            # 計算透明度（從1.0漸變到0.0）
            progress = self.collect_timer / self.collect_duration
            self.collect_opacity = max(0.0, 1.0 - progress)
            # 動畫結束後標記為已收集
            if self.collect_timer >= self.collect_duration:
                self.is_collected = True
            return
        
        # 正常狀態下的更新
        if self.money_frames:
            self.animation_timer += self.animation_speed
            if self.animation_timer >= len(self.money_frames):
                self.animation_timer = 0.0
        
        # 如果還沒觸底，繼續落下
        if self.bottom_time < 0:
            self.position.setY(self.position.y() + self.fall_speed)
            frame = self.get_current_frame()
            if frame:
                h = int(frame.height() * self.scale)
                bottom_margin = 24
                if self.position.y() + h // 2 >= aquarium_rect.bottom() - bottom_margin:
                    # 觸底，記錄觸底時間
                    self.bottom_time = 0
        else:
            # 已經觸底，累加觸底時間
            self.bottom_time += 1
        
        self.lifetime += 1
    
    def start_collect_animation(self) -> None:
        """開始消失動畫（被收集時呼叫）"""
        if not self.is_collecting and not self.is_collected:
            self.is_collecting = True
            self.collect_timer = 0.0
            self.collect_opacity = 1.0

    def is_expired(self) -> bool:
        if self.is_collected:
            return True
        # 如果觸底了，檢查觸底後的生存時間
        if self.bottom_time >= 0:
            return self.bottom_time >= self.bottom_lifetime
        # 如果還沒觸底，使用原來的邏輯
        return self.lifetime >= self.max_lifetime
    
    def should_blink(self) -> bool:
        """判斷是否應該閃爍（觸底後7秒開始閃爍）"""
        if self.bottom_time < 0:
            return False
        return self.bottom_time >= self.blink_start_time
    
    def get_opacity(self) -> float:
        """獲取當前透明度（用於閃爍效果或消失動畫）"""
        # 優先處理消失動畫透明度
        if self.is_collecting:
            return self.collect_opacity
        # 閃爍效果（觸底後7秒開始閃爍）
        if not self.should_blink():
            return 1.0
        # 閃爍效果：在0.3到1.0之間變化（每10幀一個週期）
        blink_cycle = (self.bottom_time - self.blink_start_time) % 20
        if blink_cycle < 10:
            return 0.3 + (blink_cycle / 10) * 0.7
        else:
            return 1.0 - ((blink_cycle - 10) / 10) * 0.7

    def get_current_frame(self) -> Optional[QPixmap]:
        if not self.money_frames:
            return None
        idx = int(self.animation_timer) % len(self.money_frames)
        return self.money_frames[idx]

    def get_display_rect(self) -> Optional[QRect]:
        """獲取顯示矩形（消失動畫期間仍可檢測碰撞，但會逐漸淡出）"""
        frame = self.get_current_frame()
        if not frame:
            return None
        w = int(frame.width() * self.scale)
        h = int(frame.height() * self.scale)
        cx, cy = int(self.position.x()), int(self.position.y())
        return QRect(cx - w // 2, cy - h // 2, w, h)


class FeedSelectionDialog(QDialog):
    """
    選擇飼料對話框
    
    顯示已解鎖的飼料供使用者選擇。
    """
    
    def __init__(self, unlocked_feeds: List[str], feed_counters: dict, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("選擇飼料")
        self.setWindowIcon(_get_app_icon())
        self.setModal(True)
        self._selected_feed: Optional[Tuple[str, Path]] = None
        
        layout = QVBoxLayout(self)
        
        # 標題
        title_label = QLabel("請選擇要使用的飼料：")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 飼料列表：resource/feed 內飼料 + 寶箱怪飼料（金條、鑽石，有數量時顯示）
        feed_list = _list_feeds()
        # 記錄已經在 feed_list 中的飼料名稱，避免重複添加
        existing_feeds = {name for name, _ in feed_list}
        for name in CHEST_FEED_ITEMS:
            if name in unlocked_feeds:
                # 如果已經在 feed_list 中（resource/feed/ 目錄存在），跳過
                if name in existing_feeds:
                    continue
                # 優先使用 resource/feed/ 目錄路徑（用於動畫），如果不存在則使用單一圖片路徑
                feed_dir = _resource_dir() / "feed" / name
                if feed_dir.exists() and feed_dir.is_dir():
                    feed_list.append((name, feed_dir))
                else:
                    feed_list.append((name, _get_chest_feed_image_path(name)))
        for feed_name, feed_path in feed_list:
            if feed_name not in unlocked_feeds:
                continue
            
            # 創建飼料按鈕
            feed_btn = QPushButton()
            feed_btn.setMinimumHeight(50)
            
            # 顯示飼料圖示和名稱
            feed_layout = QHBoxLayout()
            feed_layout.setContentsMargins(10, 5, 10, 5)
            
            # 飼料圖示（feed_path 可能為目錄或單一檔案，如金條/鑽石）
            icon_pix = _feed_preview_pixmap(feed_path, 40)
            if icon_pix and not icon_pix.isNull():
                icon_label = QLabel()
                icon_label.setPixmap(icon_pix)
                icon_label.setFixedSize(40, 40)
                feed_layout.addWidget(icon_label)
            
            # 飼料名稱和數量
            name_label = QLabel()
            if feed_name == "便宜飼料":
                name_label.setText("便宜飼料 (2$)")
            else:
                cnt = feed_counters.get(feed_name, 0)
                name_label.setText(f"{feed_name} ({cnt})")
            name_label.setStyleSheet("font-size: 12px;")
            feed_layout.addWidget(name_label)
            
            feed_layout.addStretch()
            feed_btn.setLayout(feed_layout)
            
            # 連接點擊事件
            feed_btn.clicked.connect(lambda checked, n=feed_name, p=feed_path: self._on_feed_selected(n, p))
            layout.addWidget(feed_btn)
        
        # 取消按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _on_feed_selected(self, feed_name: str, feed_path: Path) -> None:
        """選擇飼料"""
        self._selected_feed = (feed_name, feed_path)
        self.accept()
    
    def get_selected_feed(self) -> Optional[Tuple[str, Path]]:
        """取得選取的飼料"""
        return self._selected_feed


class FeedMachineWidget(QWidget):
    """
    投食機透明部件
    
    作為主視窗的子部件，重疊在主視窗上顯示投食機，掛在水族箱左側以避免被邊界裁切。
    """
    
    # 信號：選擇飼料時發出 (feed_name, feed_path)
    feed_selected = pyqtSignal(str, object)  # Path
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # 設定部件背景為透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 設定部件只在非透明區域接收滑鼠事件（透明區域穿透）
        # 這需要通過重寫 hitTest 或使用區域遮罩來實現
        # 但 PyQt6 沒有直接的 WA_TransparentMouseEvents，所以我們在 mousePressEvent 中處理
        
        # 投食機狀態
        self._feed_machine_visible = False
        self._feed_machine_color = FEED_MACHINE_DEFAULT_COLOR
        self._feed_machine_pixmap: Optional[QPixmap] = None
        self._load_feed_machine_pixmap()
        
        # 根據圖片實際大小設定部件大小（確保不會被裁切）
        self._update_widget_size()
        
        # 初始隱藏
        self.hide()
        
        # 投食機選取的飼料（用於自動投食）
        self._selected_feed: Optional[Tuple[str, Path]] = None
        self._selected_feed_pixmap: Optional[QPixmap] = None  # 選中飼料的預覽圖
        self._unlocked_feeds: List[str] = []
        self._feed_counters: dict = {}
    
    def _update_widget_size(self) -> None:
        """根據圖片實際大小更新部件大小，確保圖片不會被裁切"""
        if self._feed_machine_pixmap and not self._feed_machine_pixmap.isNull():
            # 使用圖片實際大小，加上一些邊距確保完整顯示
            pixmap_width = self._feed_machine_pixmap.width()
            pixmap_height = self._feed_machine_pixmap.height()
            # 部件寬度至少為配置值，高度根據圖片調整
            widget_width = max(FEED_MACHINE_WIDGET_WIDTH, pixmap_width + 10)
            widget_height = max(FEED_MACHINE_WIDGET_HEIGHT, pixmap_height + 10)
            self.setFixedSize(widget_width, widget_height)
        else:
            # 如果圖片未載入，使用預設大小
            self.setFixedSize(FEED_MACHINE_WIDGET_WIDTH, FEED_MACHINE_WIDGET_HEIGHT)
    
    def _load_feed_machine_pixmap(self) -> None:
        """載入投食機圖片（依當前顏色），並套用縮放倍率"""
        resource_dir = _resource_dir()
        feed_machine_path = resource_dir / "feed_machine" / f"投食機_{self._feed_machine_color}.png"
        if feed_machine_path.exists():
            original_pixmap = QPixmap(str(feed_machine_path))
            if not original_pixmap.isNull():
                # 套用縮放倍率
                scaled_width = int(original_pixmap.width() * FEED_MACHINE_SCALE)
                scaled_height = int(original_pixmap.height() * FEED_MACHINE_SCALE)
                self._feed_machine_pixmap = original_pixmap.scaled(
                    scaled_width, scaled_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                print(f"[投食機] 載入圖片成功: {feed_machine_path}, 原始大小: {original_pixmap.width()}x{original_pixmap.height()}, 縮放後: {scaled_width}x{scaled_height}")
                # 載入圖片後更新部件大小
                self._update_widget_size()
            else:
                self._feed_machine_pixmap = None
                print(f"[投食機] 圖片載入失敗（QPixmap.isNull）: {feed_machine_path}")
        else:
            self._feed_machine_pixmap = None
            print(f"[投食機] 圖片檔案不存在: {feed_machine_path}")
    
    def set_feed_machine_visible(self, visible: bool) -> None:
        """設定投食機是否顯示，並更新部件位置"""
        self._feed_machine_visible = visible
        if visible:
            # 確保部件大小已根據圖片更新
            self._update_widget_size()
            
            # 計算部件位置（在左側空白區域內，垂直居中）
            x = FEED_MACHINE_WIDGET_OFFSET_X
            parent = self.parent()
            if parent:
                # 垂直居中：主視窗高度的一半減去部件高度的一半
                parent_height = parent.height()
                widget_height = self.height()
                y = max(0, (parent_height - widget_height) // 2)
            else:
                y = FEED_MACHINE_WIDGET_OFFSET_Y
            
            # 檢查部件是否會延伸到水族箱區域
            widget_right = x + self.width()
            if hasattr(parent, 'feed_machine_area_rect'):
                feed_area_right = parent.feed_machine_area_rect.right()
                if widget_right > feed_area_right:
                    print(f"[警告] 投食機部件右側 ({widget_right}) 超出左側空白區域 ({feed_area_right})，會延伸到水族箱區域！")
                    print(f"[警告] 投食機部件位置: ({x}, {y}), 大小: {self.width()}x{self.height()}")
                    print(f"[警告] 左側空白區域: {parent.feed_machine_area_rect}")
                    print(f"[警告] 水族箱區域: {parent.aquarium_rect}")
            
            self.setGeometry(x, y, self.width(), self.height())
            self.show()
            self.raise_()  # 確保在最上層
            # 更新主視窗遮罩（左側空白區域已包含在遮罩中）
            if parent and hasattr(parent, 'updateWindowMask'):
                parent.updateWindowMask()
            print(f"[投食機] 顯示投食機，位置: ({x}, {y}), 大小: {self.width()}x{self.height()}")
        else:
            self.hide()
            # 更新主視窗遮罩
            parent = self.parent()
            if parent and hasattr(parent, 'updateWindowMask'):
                parent.updateWindowMask()
        self.update()
    
    def set_feed_machine_color(self, color: str) -> None:
        """設定投食機顏色並重新載入圖片"""
        if color in FEED_MACHINE_COLORS:
            self._feed_machine_color = color
            self._load_feed_machine_pixmap()
            self.update()
    
    def _get_feed_machine_image_rect(self) -> Optional[QRect]:
        """獲取投食機圖片的實際顯示區域（相對於部件的座標）"""
        if self._feed_machine_visible and self._feed_machine_pixmap and not self._feed_machine_pixmap.isNull():
            x = (self.width() - self._feed_machine_pixmap.width()) // 2
            y = (self.height() - self._feed_machine_pixmap.height()) // 2
            return QRect(
                x, y,
                self._feed_machine_pixmap.width(),
                self._feed_machine_pixmap.height()
            )
        return None
    
    def set_unlocked_feeds(self, unlocked_feeds: List[str], feed_counters: dict) -> None:
        """設定已解鎖的飼料列表和計數器"""
        self._unlocked_feeds = list(unlocked_feeds) if unlocked_feeds else []
        self._feed_counters = dict(feed_counters) if feed_counters else {}
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """處理滑鼠點擊事件：只有點擊在投食機圖片區域內才處理，否則讓事件穿透"""
        pos = event.position().toPoint()
        image_rect = self._get_feed_machine_image_rect()
        
        if image_rect and image_rect.contains(pos):
            # 點擊在投食機圖片區域內，彈出選擇飼料對話框
            if self._unlocked_feeds:
                dialog = FeedSelectionDialog(self._unlocked_feeds, self._feed_counters, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected = dialog.get_selected_feed()
                    if selected:
                        feed_name, feed_path = selected
                        self.set_selected_feed(feed_name, feed_path)
                        self.feed_selected.emit(feed_name, feed_path)
                        print(f"[投食機] 選擇飼料: {feed_name}")
            event.accept()
            return
        
        # 點擊在透明區域，讓事件穿透到父視窗（水族箱）
        # 將事件轉換為父視窗座標並重新發送
        event.ignore()
        # 創建一個新事件，座標轉換為父視窗座標
        parent = self.parent()
        if parent:
            global_pos = self.mapToGlobal(pos)
            parent_local_pos = parent.mapFromGlobal(global_pos)
            parent_event = QMouseEvent(
                event.type(),
                QPointF(parent_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            QApplication.sendEvent(parent, parent_event)
    
    def get_selected_feed(self) -> Optional[Tuple[str, Path]]:
        """取得選取的飼料"""
        return self._selected_feed
    
    def set_selected_feed(self, feed_name: Optional[str], feed_path: Optional[Path] = None) -> None:
        """設定選取的飼料並更新顯示"""
        if feed_name and feed_path:
            self._selected_feed = (feed_name, feed_path)
            # 載入飼料預覽圖
            self._selected_feed_pixmap = _feed_preview_pixmap(feed_path, FEED_MACHINE_FEED_IMAGE_SIZE)
        else:
            self._selected_feed = None
            self._selected_feed_pixmap = None
        self.update()  # 觸發重繪
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """處理滑鼠移動事件：讓事件穿透到父視窗"""
        pos = event.position().toPoint()
        image_rect = self._get_feed_machine_image_rect()
        
        if image_rect and image_rect.contains(pos):
            # 在投食機圖片區域內，忽略事件
            event.ignore()
            return
        
        # 在透明區域，讓事件穿透到父視窗
        event.ignore()
        parent = self.parent()
        if parent:
            global_pos = self.mapToGlobal(pos)
            parent_local_pos = parent.mapFromGlobal(global_pos)
            parent_event = QMouseEvent(
                event.type(),
                QPointF(parent_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            QApplication.sendEvent(parent, parent_event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """處理滑鼠釋放事件：讓事件穿透到父視窗"""
        pos = event.position().toPoint()
        image_rect = self._get_feed_machine_image_rect()
        
        if image_rect and image_rect.contains(pos):
            # 在投食機圖片區域內，忽略事件
            event.ignore()
            return
        
        # 在透明區域，讓事件穿透到父視窗
        event.ignore()
        parent = self.parent()
        if parent:
            global_pos = self.mapToGlobal(pos)
            parent_local_pos = parent.mapFromGlobal(global_pos)
            parent_event = QMouseEvent(
                event.type(),
                QPointF(parent_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            QApplication.sendEvent(parent, parent_event)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """繪製投食機"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 繪製投食機（居中顯示）
        if self._feed_machine_visible:
            if self._feed_machine_pixmap and not self._feed_machine_pixmap.isNull():
                feed_machine_rect = self._get_feed_machine_image_rect()
                if feed_machine_rect:
                    # 繪製投食機圖片
                    painter.drawPixmap(feed_machine_rect, self._feed_machine_pixmap)
                    
                    # 如果有選中的飼料，在投食機圖片的中下方繪製飼料圖片
                    if self._selected_feed_pixmap and not self._selected_feed_pixmap.isNull():
                        # 計算飼料圖片的位置（投食機圖片的中下方）
                        feed_size = FEED_MACHINE_FEED_IMAGE_SIZE
                        feed_x = feed_machine_rect.center().x() - feed_size // 2 + FEED_MACHINE_FEED_IMAGE_OFFSET_X
                        feed_y = feed_machine_rect.bottom() - feed_size + FEED_MACHINE_FEED_IMAGE_OFFSET_Y
                        feed_rect = QRect(feed_x, feed_y, feed_size, feed_size)
                        painter.drawPixmap(feed_rect, self._selected_feed_pixmap)
            else:
                # 調試：繪製一個紅色矩形表示部件存在但圖片未載入
                painter.fillRect(self.rect(), QColor(255, 0, 0, 100))
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "投食機\n圖片未載入")


class AquariumWidget(QWidget):
    """
    水族箱部件
    
    顯示背景圖片，魚類可以在其中游動，並處理互動事件。
    """
    
    # 信號：當在水族箱區域內點擊時發出
    clicked = pyqtSignal(QPoint)
    # 信號：當滑鼠移動到金錢物件上時發出（用於自動拾取），參數為金額值
    money_hovered = pyqtSignal(int)
    # 信號：拼布魚吃核廢料 20% 複製時發出，參數為寵物名稱（如 "拼布魚"）
    pet_duplicate_requested = pyqtSignal(str)
    # 信號：每幀更新時發出遊戲時間（秒），供主視窗更新飼料計數器等
    game_time_updated = pyqtSignal(float)

    def __init__(self, background_path: Optional[Path] = None, parent: Optional[QWidget] = None):
        """
        初始化水族箱部件
        
        Args:
            background_path: 背景圖片路徑
            parent: 父部件
        """
        super().__init__(parent)
        self.background_path = background_path
        self.background_pixmap: Optional[QPixmap] = None
        
        # 背景透明度 0~100%（預設 80%）
        self.background_opacity = 80

        # 載入背景圖片
        self._load_background_pixmap()
        
        # 設定背景為透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 魚類列表
        self.fishes: List[Fish] = []
        
        # 飼料列表
        self.feeds: List[Feed] = []
        # 金錢列表（魚大便排出，可點擊拾取）
        self.moneys: List[Money] = []
        # 寵物列表
        self.pets: List[Pet] = []
        self._game_time_sec = 0.0  # 遊戲時間（秒），用於鯊魚吃幼鬥魚／大便魚翅計時

        # 拖曳視窗用（按下時的起點，用來區分點擊 vs 拖曳）
        self._drag_initial_global: Optional[QPoint] = None
        self._drag_start_global: Optional[QPoint] = None
        self._drag_window_top_left: Optional[QPoint] = None
        
        # 快樂buff愛心圖示（拼布魚街頭表演時顯示在會產金錢的魚頭上）
        self._happy_buff_heart_pixmap: Optional[QPixmap] = None
        
        
        # 更新計時器
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_fishes)
        self.update_timer.start(16)  # 約 60 FPS
        
        # 啟用滑鼠追蹤（用於檢測滑鼠移動到金錢物件上）
        self.setMouseTracking(True)
        
    def _load_background_pixmap(self) -> None:
        """依當前 background_path 載入背景圖"""
        if self.background_path and self.background_path.exists():
            self.background_pixmap = QPixmap(str(self.background_path))
        else:
            self.background_pixmap = None

    def set_background(self, path: Optional[Path]) -> None:
        """切換背景圖片"""
        self.background_path = path
        self._load_background_pixmap()
        self.update()

    def set_background_opacity(self, percent: int) -> None:
        """設定背景圖片透明度（0=完全透明，100=完全不透明），觸發重繪"""
        self.background_opacity = max(0, min(100, percent))
        self.update()
    

    def add_fish(self, fish: Fish) -> None:
        """添加魚類到水族箱"""
        fish.set_upgrade_callback(self._on_fish_upgrade)
        fish.set_poop_callback(self._on_fish_poop)
        self.fishes.append(fish)

    def _duplicate_fish(self, fish: Fish, spawn_position: QPointF | QPoint | None = None) -> None:
        """複製一隻相同魚種、階段、成長度的魚（用於核廢料 20% 複製）。新魚出生在 spawn_position，未傳入時為原魚位置。"""
        if not fish.species:
            return
        resource_dir = Path(__file__).parent / "resource"
        fish_species_dir = resource_dir / "fish" / fish.species
        stage = fish.stage or "small"
        possible_dirs = [
            fish_species_dir / stage,
            fish_species_dir / f"{stage}_{fish.species}",
        ]
        if fish.species == "鬥魚":
            stage_name_map = {"small": "幼鬥魚", "medium": "中鬥魚", "large": "成年鬥魚", "angel": "天使鬥魚"}
            if stage in stage_name_map:
                possible_dirs.insert(0, fish_species_dir / stage_name_map[stage])
        fish_dir = None
        for d in possible_dirs:
            if d.exists() and d.is_dir():
                fish_dir = d
                break
        if fish_dir is None:
            fish_dir = fish_species_dir
        swim_behavior, turn_behavior, eat_behavior = get_fish_behaviors(fish.species)
        swim_frames, turn_frames = load_swim_and_turn(fish_dir, swim_behavior, turn_behavior)
        if not swim_frames:
            return
        eat_frames = load_fish_animation(fish_dir, behavior=eat_behavior)
        swim_copy = [QPixmap(p) for p in swim_frames]
        turn_copy = [QPixmap(p) for p in turn_frames] if turn_frames else swim_copy[:]
        eat_copy = [QPixmap(p) for p in eat_frames] if eat_frames else []
        # 起始位置：有傳入則用該處（核廢料位置）；否則用原魚位置
        if spawn_position is not None:
            x, y = int(spawn_position.x()), int(spawn_position.y())
        else:
            x, y = int(fish.position.x()), int(fish.position.y())
        h_dir, v_dir = fish.horizontal_direction, fish.vertical_direction
        if h_dir != 0 or v_dir != 0:
            direction = math.degrees(math.atan2(-v_dir, h_dir))
            if direction < 0:
                direction += 360.0
        else:
            direction = 90.0
        scale = get_fish_scale(fish.species, stage)
        new_fish = Fish(
            swim_frames=swim_copy,
            turn_frames=turn_copy,
            position=QPoint(x, y),
            speed=fish.speed,
            direction=direction,
            scale=scale,
            eat_frames=eat_copy if eat_copy else None,
            species=fish.species,
            stage=stage,
        )
        new_fish.growth_points = fish.growth_points
        new_fish.facing_left = fish.facing_left
        self.add_fish(new_fish)
    
    def add_pet(self, pet: Pet) -> None:
        """添加寵物到水族箱"""
        self.pets.append(pet)

    def _on_fish_poop(self, money_type: str, position: QPointF) -> None:
        """魚大便時產生金錢物件（各階段鬥魚定時觸發）"""
        money_frames = _load_money_frames(money_type)
        if not money_frames:
            return
        money = Money(
            position=position,
            money_frames=money_frames,
            money_name=money_type,
            scale=get_money_scale(money_type),
        )
        self.moneys.append(money)

    def add_money_with_callback(
        self,
        position: QPointF,
        money_name: str,
        on_collected_callback: Callable[[], None],
    ) -> None:
        """加入可拾取金錢，拾取時呼叫 on_collected_callback（用於寶箱怪產物等）"""
        money_frames = _load_money_frames(money_name)
        if not money_frames:
            return
        money = Money(
            position=position,
            money_frames=money_frames,
            money_name=money_name,
            scale=get_money_scale(money_name),
            on_collected_callback=on_collected_callback,
        )
        self.moneys.append(money)
    
    def _on_fish_upgrade(self, old_fish: Fish, next_stage: str) -> None:
        """
        處理魚的升級
        
        Args:
            old_fish: 需要升級的魚
            next_stage: 下一個成長階段
        """
        print(f"[升級處理] 開始處理升級: {old_fish.species} {old_fish.stage} -> {next_stage}")
        
        # 在移除舊魚之前，先記錄舊魚種的當前數量（用於里程碑追蹤）
        parent_window = self.window()
        if parent_window and hasattr(parent_window, '_record_fish_milestone_before_upgrade'):
            parent_window._record_fish_milestone_before_upgrade(old_fish)
        
        # 先創建新階段的魚
        new_fish = self._create_upgraded_fish(old_fish, next_stage)
        if new_fish:
            print(f"[升級處理] 成功創建新魚: {new_fish.species} {new_fish.stage}")
            # 舊魚直接從列表移除（升級不是死亡，不播死亡動畫）
            if old_fish in self.fishes:
                self.fishes = [f for f in self.fishes if f is not old_fish]
            # 使用 add_fish 方法添加新魚（會自動設置升級回調）
            self.add_fish(new_fish)
            print(f"[升級處理] 已添加新魚並設置升級回調: {new_fish.species} {new_fish.stage}")
            
            # 通知父視窗進行自動儲存（如果父視窗是 TransparentAquariumWindow）
            if parent_window and hasattr(parent_window, '_on_fish_upgraded'):
                parent_window._on_fish_upgraded(new_fish)
        else:
            print(f"[升級處理] 無法創建新魚，升級失敗")
    
    def _create_upgraded_fish(self, old_fish: Fish, next_stage: str) -> Optional[Fish]:
        """
        創建升級後的魚
        
        Args:
            old_fish: 舊魚對象
            next_stage: 下一個成長階段
        
        Returns:
            新魚對象，如果無法創建則返回 None
        """
        if not old_fish.species:
            print(f"[創建升級魚] 舊魚沒有 species，無法升級")
            return None
        
        # 構建新階段的魚目錄路徑
        resource_dir = Path(__file__).parent / "resource"
        fish_species_dir = resource_dir / "fish" / old_fish.species
        
        # 嘗試多種可能的目錄名稱格式
        # 1. 先嘗試純階段名稱（如 medium）
        # 2. 再嘗試帶魚種名稱的格式（如 medium_鬥魚）
        # 3. 嘗試中文階段名稱（如 中鬥魚、成年鬥魚、天使鬥魚）
        possible_dirs = [
            fish_species_dir / next_stage,  # medium
            fish_species_dir / f"{next_stage}_{old_fish.species}",  # medium_鬥魚
        ]
        
        # 為鬥魚添加中文階段名稱映射
        if old_fish.species == "鬥魚":
            stage_name_map = {
                "small": "幼鬥魚",
                "medium": "中鬥魚",
                "large": "成年鬥魚",
                "angel": "天使鬥魚",
                "golden": "金鬥魚",
                "gem": "寶石鬥魚",
            }
            if next_stage in stage_name_map:
                possible_dirs.insert(0, fish_species_dir / stage_name_map[next_stage])
        
        fish_dir = None
        for possible_dir in possible_dirs:
            if possible_dir.exists() and possible_dir.is_dir():
                fish_dir = possible_dir
                break
        
        print(f"[創建升級魚] 檢查路徑: {[str(d) for d in possible_dirs]}")
        if fish_dir is None:
            print(f"[創建升級魚] 找不到升級目錄，嘗試的路徑都不存在")
            return None
        
        print(f"[創建升級魚] 找到升級目錄: {fish_dir}")
        
        # 載入新階段的動畫（游泳、轉向、吃飯行為與鬥魚、鯊魚、孔雀魚相同，由 config.get_fish_behaviors 取得）
        swim_behavior, turn_behavior, eat_behavior = get_fish_behaviors(old_fish.species or "")
        swim_frames, turn_frames = load_swim_and_turn(
            fish_dir,
            swim_behavior=swim_behavior,
            turn_behavior=turn_behavior,
        )
        if not swim_frames:
            return None
        
        eat_frames = load_fish_animation(fish_dir, behavior=eat_behavior)
        
        # 創建新魚，繼承舊魚的位置和狀態
        swim_copy = [QPixmap(p) for p in swim_frames]
        turn_copy = [QPixmap(p) for p in turn_frames] if turn_frames else swim_copy[:]
        eat_copy = [QPixmap(p) for p in eat_frames] if eat_frames else []
        
        # 計算方向角度（從水平/垂直方向轉換）
        h_dir = old_fish.horizontal_direction
        v_dir = old_fish.vertical_direction
        if h_dir == 0 and v_dir == 0:
            direction = 0.0
        elif h_dir == 1 and v_dir == 0:
            direction = 0.0  # 右
        elif h_dir == -1 and v_dir == 0:
            direction = 180.0  # 左
        elif h_dir == 0 and v_dir == 1:
            direction = 90.0  # 下
        elif h_dir == 0 and v_dir == -1:
            direction = 270.0  # 上
        else:
            # 斜向，使用atan2計算
            direction = math.degrees(math.atan2(v_dir, h_dir))
            if direction < 0:
                direction += 360
        
        # 使用新階段的縮放倍率
        new_fish_scale = get_fish_scale(old_fish.species or "", next_stage)
        
        new_fish = Fish(
            swim_frames=swim_copy,
            turn_frames=turn_copy,
            position=QPoint(int(old_fish.position.x()), int(old_fish.position.y())),
            speed=old_fish.speed,
            direction=direction,
            scale=new_fish_scale,
            eat_frames=eat_copy if eat_copy else None,
            species=old_fish.species,
            stage=next_stage,
        )
        
        # 繼承成長度
        new_fish.growth_points = old_fish.growth_points
        
        return new_fish
    
    def add_feed(self, feed: Feed) -> None:
        """添加飼料到水族箱"""
        self.feeds.append(feed)
    
    def update_fishes(self) -> None:
        """更新所有魚類的狀態（使用有效的水族箱矩形，避免尚未佈局時 rect 無效導致魚只往左/上）"""
        aquarium_rect = self.rect()
        if aquarium_rect.width() < 100 or aquarium_rect.height() < 100:
            win = self.window()
            if win is not None and hasattr(win, 'aquarium_rect'):
                aquarium_rect = win.aquarium_rect
        
        # 更新飼料（傳入水族箱矩形以便檢測是否落到底部）
        for feed in self.feeds:
            feed.update(aquarium_rect)

        # 更新金錢（落下、動畫、過期、消失動畫）
        for money in self.moneys:
            money.update(aquarium_rect)
        # 移除已過期或已收集的金錢（消失動畫結束後 is_collected 會被設為 True）
        self.moneys = [m for m in self.moneys if not m.is_expired()]
        
        # 更新寵物（傳入飼料列表，供會吃飼料的寵物如拼布魚使用；金條/鑽石僅天使鬥魚會追，寵物不追；寵物也不追核廢料）
        excluded_feed_for_pet = set(CHEST_FEED_ITEMS) | {"核廢料"}
        feeds_for_pet = [f for f in self.feeds if getattr(f, "feed_name", None) not in excluded_feed_for_pet]
        for pet in self.pets:
            pet.update(aquarium_rect, feeds_for_pet)
            # 檢測寵物與金錢的碰撞
            collisions = pet.check_money_collision(self.moneys)
            for money, value in collisions:
                # 開始消失動畫而非立即標記為已收集
                if not money.is_collecting and not money.is_collected:
                    money.start_collect_animation()
                    # 發送信號通知拾取金錢
                    self.money_hovered.emit(value)
        
        # 遊戲時間遞增（約 60 FPS）
        self._game_time_sec += 1.0 / 60.0
        self.game_time_updated.emit(self._game_time_sec)

        # 鯊魚吃幼年鬥魚與大便魚翅（每 300 秒可吃一隻，吃後 300 秒內每 30 秒大便魚翅）
        eaten = self._check_shark_eat_betta(aquarium_rect)
        if eaten:
            shark, eaten_fish = eaten
            self.fishes = [f for f in self.fishes if f is not eaten_fish]
            shark.eat_feed()
        self._update_shark_poop()
        # 檢測孔雀魚與金錢的碰撞（每5秒追金錢，碰觸後60%機率轉換為石榴結晶）
        self._check_guppy_touch_money()

        # 檢測魚和飼料的碰撞
        self._check_feed_collisions(aquarium_rect)
        
        # 移除已過期或被吃掉的飼料
        self.feeds = [feed for feed in self.feeds if not feed.is_expired()]
        
        # 快樂buff：拼布魚街頭表演時，會產金錢的魚大便間隔縮短50%
        from config import PATCHWORK_HAPPY_BUFF_POOP_MULTIPLIER
        happy_buff_active = any(
            pet.is_performing() for pet in self.pets
            if isinstance(pet, PatchworkFishPet)
        )
        buff_multiplier = PATCHWORK_HAPPY_BUFF_POOP_MULTIPLIER if happy_buff_active else 1.0
        for fish in self.fishes:
            fish.happy_buff_multiplier = buff_multiplier
            fish.current_game_time_sec = self._game_time_sec

        # 可被鯊魚追的幼鬥魚列表（供鯊魚可進食時追逐）
        small_bettas = [
            f for f in self.fishes
            if f.species == "鬥魚" and f.stage == "small" and not getattr(f, "is_dead", False)
        ]
        
        # 更新魚類（傳入飼料列表；鯊魚可進食時傳入幼鬥魚作為獵物以追逐）
        # 金條/鑽石僅天使鬥魚會追，其餘魚傳入的飼料列表需排除金條與鑽石
        for fish in self.fishes:
            prey = None
            if fish.species == "鯊魚" and not getattr(fish, "is_dead", False) and small_bettas:
                can_eat = fish.last_eat_betta_time is None or (
                    self._game_time_sec - fish.last_eat_betta_time >= SHARK_EAT_BETTA_INTERVAL_SEC
                )
                if can_eat:
                    prey = small_bettas
            if fish.species == "鬥魚" and fish.stage == "angel":
                feeds_for_fish = self.feeds
            else:
                feeds_for_fish = [f for f in self.feeds if getattr(f, "feed_name", None) not in CHEST_FEED_ITEMS]
            # 孔雀魚傳入金錢列表，其餘魚傳入 None
            moneys_for_fish = self.moneys if fish.species == "孔雀魚" else None
            fish.update(aquarium_rect, feeds=feeds_for_fish, prey=prey, moneys=moneys_for_fish)

        # 移除死亡動畫已結束的魚（死亡／移除效果播完後才從列表移除）
        self.fishes = [
            f for f in self.fishes
            if not (getattr(f, "is_dead", False) and (f.death_timer > FISH_DEATH_ANIMATION_DURATION_SEC or f.death_opacity <= 0))
        ]
        
        # 觸發重繪
        self.update()
    
    def try_collect_money_at(self, pos: QPoint) -> Optional[int]:
        """若點擊位置在金錢上則開始消失動畫並回傳金額，否則回傳 None；若有 on_collected_callback 則呼叫"""
        for money in self.moneys:
            if money.is_collected or money.is_collecting:
                continue
            rect = money.get_display_rect()
            if rect and rect.contains(pos):
                money.start_collect_animation()
                if money.on_collected_callback:
                    money.on_collected_callback()
                value = get_money_value(money.money_name)
                return value
        return None
    
    def check_money_at(self, pos: QPoint) -> Optional[Tuple[Money, int]]:
        """檢查位置是否有金錢物件，回傳(money物件, 金額)或None（不標記為已拾取）"""
        for money in self.moneys:
            if money.is_collected or money.is_collecting:
                continue
            rect = money.get_display_rect()
            if rect and rect.contains(pos):
                value = get_money_value(money.money_name)
                return (money, value)
        return None

    def try_collect_chest_produce_at(self, pos: QPoint) -> Optional[Tuple[str, int]]:
        """若點擊位置在寶箱怪產物上則開始消失動畫並回傳 (產物類型, 金額)，否則回傳 None"""
        for pet in self.pets:
            if not isinstance(pet, ChestMonsterPet):
                continue
            # 如果正在播放消失動畫，不允許再次收集
            if pet.is_produce_collecting:
                continue
            produce_image = pet.get_produce_image()
            if not produce_image or not pet._current_produce_type:
                continue
            produce_pos = pet.get_produce_position()
            produce_rect = QRect(
                int(produce_pos.x() - produce_image.width() // 2),
                int(produce_pos.y() - produce_image.height() // 2),
                produce_image.width(),
                produce_image.height()
            )
            if produce_rect.contains(pos):
                # 獲取產物類型與價值
                produce_type = pet._current_produce_type
                value = get_money_value(produce_type)
                # 開始消失動畫（動畫結束後會自動重置寶箱怪）
                pet.start_produce_collect_animation()
                return (produce_type, value)
        return None

    def _check_guppy_touch_money(self) -> None:
        """孔雀魚碰觸金錢：每5秒追最近金錢，碰觸後60%機率轉換為石榴結晶（紅色色調）。碰觸後5秒內無法再碰觸其他金錢。"""
        import random
        from config import GUPPY_MONEY_COOLDOWN_SEC, GUPPY_MONEY_TRANSFORM_CHANCE
        for guppy in self.fishes:
            if guppy.species != "孔雀魚" or getattr(guppy, "is_dead", False):
                continue
            # 檢查冷卻時間：如果還在冷卻中，跳過碰撞檢測
            if guppy.current_game_time_sec < guppy.money_touch_cooldown_until:
                continue
            guppy_rect = guppy.get_display_rect()
            if not guppy_rect:
                continue
            # 檢測碰撞（排除已石榴化的金錢）
            for money in self.moneys:
                if money.is_collected or money.is_collecting:
                    continue
                # 跳過已石榴化的金錢
                if hasattr(money, "money_name") and str(money.money_name).startswith("石榴結晶_"):
                    continue
                money_rect = money.get_display_rect()
                if not money_rect:
                    continue
                if guppy_rect.intersects(money_rect):
                    # 碰觸到：60%機率轉換為石榴結晶
                    if random.random() < GUPPY_MONEY_TRANSFORM_CHANCE:
                        # 轉換為石榴結晶
                        money_type = money.money_name
                        # 載入原始動畫幀並調整為紅色色調
                        original_frames = _load_money_frames(money_type)
                        if original_frames:
                            red_frames = [_adjust_hue_to_pomegranate(pixmap) for pixmap in original_frames]
                            # 創建新的石榴結晶金錢物件
                            new_money = Money(
                                position=QPointF(money.position.x(), money.position.y()),
                                money_frames=red_frames,
                                money_name=f"石榴結晶_{money_type}",
                                scale=money.scale,
                            )
                            # 複製動畫狀態
                            new_money.animation_timer = money.animation_timer
                            new_money.bottom_time = money.bottom_time
                            new_money.lifetime = money.lifetime
                            self.moneys.append(new_money)
                        # 設定冷卻時間：5秒內無法再碰觸其他金錢
                        guppy.money_touch_cooldown_until = self._game_time_sec + GUPPY_MONEY_COOLDOWN_SEC
                    # 原金錢消失（不論成功與否都要消失）
                    money.start_collect_animation()
                    # 避免孔雀魚持續黏著同一顆目標
                    if hasattr(guppy, "_current_money_target"):
                        guppy._current_money_target = None
                    break

    def _check_shark_eat_betta(self, aquarium_rect: QRect) -> Optional[Tuple["Fish", "Fish"]]:
        """鯊魚吃幼年鬥魚：每 300 秒可吃一隻，吃過後 300 秒內不再進食。回傳 (鯊魚, 被吃的魚) 由呼叫端移除魚並觸發鯊魚吃飯動畫，不播死亡動畫。"""
        import random
        for shark in self.fishes:
            if shark.species != "鯊魚" or getattr(shark, "is_dead", False):
                continue
            can_eat = shark.last_eat_betta_time is None or (
                self._game_time_sec - shark.last_eat_betta_time >= SHARK_EAT_BETTA_INTERVAL_SEC
            )
            if not can_eat:
                continue
            shark_rect = shark.get_display_rect()
            if not shark_rect:
                continue
            for fish in self.fishes:
                if fish is shark or getattr(fish, "is_dead", False):
                    continue
                if fish.species != "鬥魚" or fish.stage != "small":
                    continue
                fish_rect = fish.get_display_rect()
                if not fish_rect or not shark_rect.intersects(fish_rect):
                    continue
                shark.last_eat_betta_time = self._game_time_sec
                shark.next_poop_at = self._game_time_sec + SHARK_POOP_INTERVAL_SEC
                return (shark, fish)  # 一隻鯊魚一幀只吃一隻；由呼叫端移除魚並觸發鯊魚吃飯動畫
        return None

    def _update_shark_poop(self) -> None:
        """鯊魚在吃過幼鬥魚後的 300 秒內，每 30 秒大便魚翅；超過 300 秒沒吃則不大便。"""
        for shark in self.fishes:
            if shark.species != "鯊魚" or shark.last_eat_betta_time is None:
                continue
            elapsed = self._game_time_sec - shark.last_eat_betta_time
            if elapsed > SHARK_POOP_DURATION_SEC:
                continue
            if shark.next_poop_at is None or self._game_time_sec < shark.next_poop_at:
                continue
            self._on_fish_poop("魚翅", QPointF(shark.position.x(), shark.position.y()))
            shark.next_poop_at += SHARK_POOP_INTERVAL_SEC
            if shark.next_poop_at > shark.last_eat_betta_time + SHARK_POOP_DURATION_SEC:
                shark.next_poop_at = None

    def _check_feed_collisions(self, aquarium_rect: QRect) -> None:
        """檢測魚、會吃飼料的寵物（如拼布魚）與飼料的碰撞。孔雀魚與鯊魚不進食；核廢料僅鬥魚會吃（寵物類都不吃）；金條/鑽石僅天使鬥魚會吃，吃後變身金鬥魚/寶石鬥魚；金鬥魚/寶石鬥魚只吃一般飼料。"""
        import random
        for fish in self.fishes:
            if fish.species == "孔雀魚" or fish.species == "鯊魚" or getattr(fish, "is_dead", False):
                continue
            fish_rect = fish.get_display_rect()
            if not fish_rect:
                continue
            
            for feed in self.feeds:
                if feed.is_eaten:
                    continue
                
                feed_rect = feed.get_display_rect()
                if not feed_rect:
                    continue
                
                if not fish_rect.intersects(feed_rect):
                    continue
                if fish.state == "eating":
                    continue
                if fish.feed_cooldown_timer > 0:
                    continue
                # 金條/鑽石：金鬥魚、寶石鬥魚不吃，僅天使鬥魚可吃，吃後變身
                if feed.feed_name in CHEST_FEED_ITEMS:
                    if fish.species == "鬥魚" and fish.stage in ("golden", "gem"):
                        continue
                    if fish.species != "鬥魚" or fish.stage != "angel":
                        continue
                    feed.is_eaten = True
                    next_stage = "golden" if feed.feed_name == "金條" else "gem"
                    self._on_fish_upgrade(fish, next_stage)
                    break
                # 核廢料：僅鬥魚魚種會吃；進食後 80% 死亡、20% 複製（新魚在原魚位置生成）
                if feed.feed_name == "核廢料":
                    if fish.species != "鬥魚":
                        continue
                    feed.is_eaten = True
                    if random.random() < NUCLEAR_DEATH_CHANCE:
                        fish.set_dead()
                    else:
                        self._duplicate_fish(fish)
                    break
                if fish.state == "turning":
                    fish.consume_feed(feed)
                    feed.is_eaten = True
                    break
                fish.eat_feed(feed)
                feed.is_eaten = True
                break

        # 檢測會吃飼料的寵物（如拼布魚）與飼料的碰撞；寵物類都不吃核廢料
        _pets_to_remove = []
        for pet in self.pets:
            if not hasattr(pet, "eat_feed"):
                continue
            pet_rect = pet.get_display_rect()
            if not pet_rect:
                continue
            for feed in self.feeds:
                if feed.is_eaten:
                    continue
                feed_rect = feed.get_display_rect()
                if not feed_rect:
                    continue
                if not pet_rect.intersects(feed_rect):
                    continue
                if getattr(pet, "state", None) == "eating":
                    continue
                if getattr(pet, "feed_cooldown_timer", 0) > 0:
                    continue
                # 金條/鑽石僅天使鬥魚會吃，寵物（如拼布魚）不處理
                if feed.feed_name in CHEST_FEED_ITEMS:
                    continue
                # 核廢料：僅鬥魚會吃，寵物類都不吃
                if feed.feed_name == "核廢料":
                    continue
                if getattr(pet, "state", None) == "turning":
                    pet.consume_feed(feed)
                    feed.is_eaten = True
                    break
                pet.eat_feed(feed)
                feed.is_eaten = True
                break
        for pet in _pets_to_remove:
            if pet in self.pets:
                self.pets.remove(pet)
        
    def _get_feed_machine_exit_position(self) -> Optional[QPointF]:
        """計算投食機飼料起始位置（用於繪製標記）"""
        parent = self.parent()
        if not parent or not hasattr(parent, '_feed_machine_widget') or not hasattr(parent, 'aquarium_rect'):
            return None
        
        feed_machine_widget = parent._feed_machine_widget
        if not feed_machine_widget or not feed_machine_widget.isVisible():
            return None
        
        feed_machine_geometry = feed_machine_widget.geometry()
        aquarium_rect = self.rect()  # AquariumWidget 的本地座標（從 0,0 開始）
        parent_aquarium_rect = parent.aquarium_rect  # 主視窗中水族箱的全局座標
        
        # 計算起始 x 位置（與 _feed_machine_shoot_feeds 相同的邏輯）
        if FEED_MACHINE_EXIT_X_RATIO is not None:
            # 使用配置的比例值（相對於水族箱寬度）
            aquarium_width = aquarium_rect.width()
            exit_x = aquarium_rect.left() + aquarium_width * FEED_MACHINE_EXIT_X_RATIO
        else:
            # 使用投食機位置自動計算（相對於投食機右側）
            # feed_machine_geometry.right() 是主視窗座標，需要轉換為水族箱本地座標
            exit_x_base = feed_machine_geometry.right() - parent_aquarium_rect.left()  # 轉換為水族箱座標
            exit_x = exit_x_base + FEED_MACHINE_EXIT_X_OFFSET  # 應用 x 偏移配置
        
        # 計算起始 y 位置（投食機頂部稍微下方）
        # feed_machine_geometry.top() 是主視窗座標，需要轉換為水族箱本地座標
        exit_y = feed_machine_geometry.top() - parent_aquarium_rect.top() + 20
        
        return QPointF(exit_x, exit_y)
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """繪製水族箱背景和魚類"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 繪製背景（依背景透明度 0~100%）
        if self.background_pixmap:
            opacity = self.background_opacity / 100.0
            painter.setOpacity(opacity)
            scaled_pixmap = self.background_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            painter.drawPixmap(0, 0, scaled_pixmap)
            painter.setOpacity(1.0)
        else:
            # 如果沒有背景圖片，繪製一個半透明的藍色背景
            painter.fillRect(self.rect(), QColor(100, 150, 255, 200))
        
        # 繪製飼料
        for feed in self.feeds:
            frame = feed.get_current_frame()
            if frame:
                display_rect = feed.get_display_rect()
                if display_rect:
                    painter.drawPixmap(display_rect, frame)

        # 繪製金錢（魚大便，與飼料同落下速度）
        for money in self.moneys:
            frame = money.get_current_frame()
            if frame:
                display_rect = money.get_display_rect()
                if display_rect:
                    # 獲取透明度（消失動畫或閃爍效果）
                    opacity = money.get_opacity()
                    if opacity < 1.0:
                        painter.setOpacity(opacity)
                        painter.drawPixmap(display_rect, frame)
                        painter.setOpacity(1.0)  # 恢復透明度
                    else:
                        painter.drawPixmap(display_rect, frame)
        
        # 繪製魚類（頭朝左素材；朝右或轉向到右不鏡像，朝左或轉向到左時轉向幀鏡像）
        happy_buff_active = any(
            pet.is_performing() for pet in self.pets
            if isinstance(pet, PatchworkFishPet)
        )
        for fish in self.fishes:
            frame = fish.get_current_frame()
            if frame:
                display_rect = fish.get_display_rect()
                if display_rect:
                    if getattr(fish, "is_dead", False):
                        painter.setOpacity(fish.death_opacity)
                    if fish.get_should_mirror():
                        painter.save()
                        painter.translate(display_rect.center().x(), display_rect.center().y())
                        painter.scale(-1, 1)
                        painter.translate(-display_rect.center().x(), -display_rect.center().y())
                        painter.drawPixmap(display_rect, frame)
                        painter.restore()
                    else:
                        painter.drawPixmap(display_rect, frame)
                    if getattr(fish, "is_dead", False):
                        painter.setOpacity(1.0)
            
            # 快樂buff：在會產金錢的魚頭上繪製愛心圖示
            if happy_buff_active and getattr(fish, "poop_interval_sec", 0) > 0:
                if self._happy_buff_heart_pixmap is None:
                    heart_path = _resource_dir() / "money" / "UI" / "拼布魚_愛心.png"
                    if heart_path.exists():
                        self._happy_buff_heart_pixmap = QPixmap(str(heart_path))
                if self._happy_buff_heart_pixmap and not self._happy_buff_heart_pixmap.isNull():
                    fish_rect = fish.get_display_rect()
                    if fish_rect:
                        from config import PATCHWORK_HAPPY_BUFF_HEART_SCALE
                        scale = PATCHWORK_HAPPY_BUFF_HEART_SCALE
                        orig_w = self._happy_buff_heart_pixmap.width()
                        orig_h = self._happy_buff_heart_pixmap.height()
                        heart_w = max(12, int(orig_w * scale))
                        heart_h = max(12, int(orig_h * scale))
                        heart_x = fish_rect.center().x() - heart_w // 2
                        heart_y = fish_rect.top() - heart_h - 4
                        heart_rect = QRect(heart_x, heart_y, heart_w, heart_h)
                        painter.drawPixmap(heart_rect, self._happy_buff_heart_pixmap.scaled(
                            heart_w, heart_h,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        ))
        
        # 繪製寵物
        for pet in self.pets:
            frame = pet.get_current_frame()
            if frame:
                display_rect = pet.get_display_rect()
                if display_rect:
                    if pet.get_should_mirror():
                        painter.save()
                        painter.translate(display_rect.center().x(), display_rect.center().y())
                        painter.scale(-1, 1)
                        painter.translate(-display_rect.center().x(), -display_rect.center().y())
                        painter.drawPixmap(display_rect, frame)
                        painter.restore()
                    else:
                        painter.drawPixmap(display_rect, frame)
            
            # 繪製寶箱怪產物圖片（在006幀後顯示）
            if isinstance(pet, ChestMonsterPet):
                produce_image = pet.get_produce_image()
                if produce_image:
                    produce_pos = pet.get_produce_position()
                    produce_rect = QRect(
                        int(produce_pos.x() - produce_image.width() // 2),
                        int(produce_pos.y() - produce_image.height() // 2),
                        produce_image.width(),
                        produce_image.height()
                    )
                    # 獲取透明度（消失動畫期間會逐漸淡出）
                    opacity = pet.get_produce_opacity()
                    if opacity < 1.0:
                        painter.setOpacity(opacity)
                        painter.drawPixmap(produce_rect, produce_image)
                        painter.setOpacity(1.0)  # 恢復透明度
                    else:
                        painter.drawPixmap(produce_rect, produce_image)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """記錄拖曳起點（左鍵）；點擊在 release 時判斷是否為純點擊"""
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            # 檢查是否錨定（通過主視窗）
            if win and hasattr(win, '_is_anchored') and win._is_anchored:
                # 錨定狀態下不記錄拖動起點，但允許其他交互行為
                # 為了讓點擊事件能正常工作，我們仍然記錄初始位置（用於判斷是否為點擊）
                g = event.globalPosition().toPoint()
                self._drag_initial_global = g
                # 但不記錄拖動相關變量，這樣就不會觸發拖動
                self._drag_start_global = None
                self._drag_window_top_left = None
            else:
                # 未錨定狀態：正常記錄拖動起點
                g = event.globalPosition().toPoint()
                self._drag_initial_global = g
                self._drag_start_global = g
                if win:
                    self._drag_window_top_left = win.frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """左鍵拖曳時移動視窗，同時檢測滑鼠是否移動到金錢物件上"""
        # 檢測滑鼠是否移動到金錢物件上（自動拾取）- 無論是否錨定都應該執行
        pos = event.position().toPoint()
        money_info = self.check_money_at(pos)
        if money_info is not None:
            money, value = money_info
            # 開始消失動畫並發送信號（傳遞金額值）
            money.start_collect_animation()
            self.money_hovered.emit(value)
        
        # 處理視窗拖曳（檢查是否錨定）
        win = self.window()
        # 如果錨定，直接返回，不執行拖動邏輯
        if win and hasattr(win, '_is_anchored') and win._is_anchored:
            return
        
        # 未錨定狀態：正常處理拖動
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if self._drag_start_global is None or self._drag_window_top_left is None:
            return
        if not win:
            return
        now_global = event.globalPosition().toPoint()
        delta = now_global - self._drag_start_global
        new_top_left = self._drag_window_top_left + delta
        win.move(new_top_left)
        self._drag_start_global = now_global
        self._drag_window_top_left = new_top_left
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """左鍵放開：若幾乎沒移動則視為點擊並發送 clicked"""
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._drag_initial_global is not None:
            moved = (event.globalPosition().toPoint() - self._drag_initial_global).manhattanLength()
            if moved < 8:
                self.clicked.emit(event.position().toPoint())
        self._drag_initial_global = None
        self._drag_start_global = None
        self._drag_window_top_left = None


# 按鈕面板寬度（在水族箱右側）
PANEL_WIDTH = 180


def _resource_dir() -> Path:
    """專案 resource 目錄"""
    return Path(__file__).parent / "resource"


def _get_app_icon() -> QIcon:
    """取得應用程式圖示（項目根目錄的 icon.ico 或 betta_icon.png）"""
    # 處理 PyInstaller 打包後的路徑
    if getattr(sys, 'frozen', False):
        # 打包後的環境：使用 sys._MEIPASS（臨時解壓目錄）
        base_path = Path(sys._MEIPASS)
    else:
        # 開發環境：使用腳本所在目錄
        base_path = Path(__file__).parent
    
    # 優先嘗試 icon.ico
    icon_path = base_path / "icon.ico"
    if icon_path.exists():
        return QIcon(str(icon_path))
    
    # 如果沒有 icon.ico，嘗試 betta_icon.png
    icon_path = base_path / "betta_icon.png"
    if icon_path.exists():
        return QIcon(str(icon_path))
    
    return QIcon()


def _list_backgrounds() -> List[Path]:
    """列出 resource/background 內可用的背景檔（jpg/png）"""
    bg_dir = _resource_dir() / "background"
    if not bg_dir.exists():
        return []
    files = list(bg_dir.glob("*.jpg")) + list(bg_dir.glob("*.png"))
    return sorted(files, key=lambda p: p.stem)


def _darken_money_edges(pixmap: QPixmap, alpha_threshold: int = 32, darken_factor: float = 0.55) -> QPixmap:
    """
    將金錢素材最外圍非透明像素加深顏色，增加對比。
    邊緣定義：alpha > alpha_threshold 且至少有一個相鄰像素為（近似）透明。
    """
    img = pixmap.toImage().convertToFormat(QImage.Format.Format_ARGB32)
    if img.isNull():
        return pixmap
    w, h = img.width(), img.height()
    edge_mask: List[Tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            c = img.pixelColor(x, y)
            if c.alpha() <= alpha_threshold:
                continue
            # 檢查 4 鄰點是否有透明或越界（即為外圍）
            is_edge = False
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= w or ny < 0 or ny >= h:
                    is_edge = True
                    break
                if img.pixelColor(nx, ny).alpha() <= alpha_threshold:
                    is_edge = True
                    break
            if is_edge:
                edge_mask.append((x, y))
    for (x, y) in edge_mask:
        c = img.pixelColor(x, y)
        r = max(0, int(c.red() * darken_factor))
        g = max(0, int(c.green() * darken_factor))
        b = max(0, int(c.blue() * darken_factor))
        img.setPixelColor(x, y, QColor(r, g, b, c.alpha()))
    return QPixmap.fromImage(img)


# 金錢動畫幀快取：金鬥魚/寶石鬥魚大便時會重複產生金錐體/藍寶石，避免每次從磁碟載入與 _darken_money_edges 造成卡頓
_money_frames_cache: Dict[str, List[QPixmap]] = {}


def _adjust_hue_to_pomegranate(pixmap: QPixmap) -> QPixmap:
    """將圖片調整為石榴化色調（HSV 色相固定）。"""
    img = pixmap.toImage()
    for y in range(img.height()):
        for x in range(img.width()):
            c = img.pixelColor(x, y)
            if c.alpha() == 0:
                continue
            # 轉換為 HSV
            h = c.hsvHue()  # -1 表示無效色相（灰階）
            s = c.hsvSaturation()
            v = c.value()
            
            # 判斷是否為灰階或低飽和度顏色（需要強制轉為紅色）
            is_gray_or_low_sat = (h < 0) or (s < 50)  # 灰階或飽和度低於50
            
            if is_gray_or_low_sat:
                # 灰階或低飽和度：使用固定色相，並拉高飽和度
                if v < 128:
                    s_fixed = max(200, int(v * 1.5))  # 暗色：較高飽和度
                else:
                    s_fixed = max(220, int(255 - (255 - v) * 0.3))  # 亮色：高飽和度
                s_fixed = min(255, s_fixed)
                new_color = QColor.fromHsv(POMEGRANATE_FIXED_HUE, s_fixed, v, c.alpha())
            else:
                # 有明顯顏色：固定色相 + 增強飽和度
                s_enhanced = min(255, int(s * 1.5))
                new_color = QColor.fromHsv(POMEGRANATE_FIXED_HUE, s_enhanced, v, c.alpha())
            img.setPixelColor(x, y, new_color)
    return QPixmap.fromImage(img)


def _load_money_frames(money_type: str) -> List[QPixmap]:
    """從 resource/money/{money_type} 載入金錢動畫幀（與飼料同樣的連續動畫），並對最外圍像素加深以增加對比。結果會快取，重複大便時不再重載。"""
    if money_type in _money_frames_cache:
        return _money_frames_cache[money_type]
    money_dir = _resource_dir() / "money" / money_type
    if not money_dir.exists() or not money_dir.is_dir():
        return []
    frame_files = sorted(money_dir.glob("*.png"))
    frames = []
    for path in frame_files:
        pixmap = QPixmap(str(path))
        if not pixmap.isNull():
            pixmap = _darken_money_edges(pixmap)
            frames.append(pixmap)
    _money_frames_cache[money_type] = frames
    return frames


def _list_feeds() -> List[Tuple[str, Path]]:
    """列出 resource/feed 內可用的飼料（子目錄名與路徑），按照 config 中 FEED_GROWTH_POINTS 的順序排序"""
    feed_dir = _resource_dir() / "feed"
    if not feed_dir.exists():
        return []
    
    # 收集所有飼料
    feeds = []
    for d in feed_dir.iterdir():
        if d.is_dir():
            feeds.append((d.name, d))
    
    # 按照 FEED_GROWTH_POINTS 的順序排序
    # 建立排序鍵：在字典中的飼料使用其在字典中的索引，不在字典中的使用大數字（放在最後）
    def sort_key(item: Tuple[str, Path]) -> Tuple[int, str]:
        feed_name = item[0]
        if feed_name in FEED_GROWTH_POINTS:
            # 取得在字典中的索引位置
            index = list(FEED_GROWTH_POINTS.keys()).index(feed_name)
            return (index, feed_name)
        else:
            # 不在字典中的飼料放在最後，按字母順序排序
            return (len(FEED_GROWTH_POINTS), feed_name)
    
    return sorted(feeds, key=sort_key)


def _list_small_fish() -> List[Tuple[str, Path]]:
    """列出 resource/fish 內可用的魚種：以 fish 底下的資料夾當選單，回傳 (顯示名, 魚種目錄 Path)。排除僅在商店販售的魚種（如孔雀魚、鯊魚）。"""
    fish_dir = _resource_dir() / "fish"
    if not fish_dir.exists():
        return []
    shop_only_species = set(FISH_SHOP_CONFIG.keys())
    result = []
    for species_dir in sorted(fish_dir.iterdir()):
        if not species_dir.is_dir():
            continue
        if species_dir.name in shop_only_species:
            continue
        result.append((species_dir.name, species_dir))
    return result


def _get_chest_feed_image_path(feed_name: str) -> Path:
    """寶箱怪飼料（金條、鑽石）的圖片路徑：resource/money/寶箱怪產物/寶箱怪產物_{name}.png"""
    return _resource_dir() / "money" / "寶箱怪產物" / f"寶箱怪產物_{feed_name}.png"


def _feed_preview_pixmap(feed_path: Path, size: int = 24) -> Optional[QPixmap]:
    """從飼料目錄或單一檔案取得第一幀作為預覽圖，縮放為指定尺寸。"""
    if not feed_path.exists():
        return None
    if feed_path.is_file():
        pixmap = QPixmap(str(feed_path))
    else:
        frame_files = sorted(feed_path.glob("*.png"))
        if not frame_files:
            return None
        pixmap = QPixmap(str(frame_files[0]))
    if pixmap.isNull():
        return None
    return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


def _fish_preview_pixmap(species_dir: Path, size: int = 24) -> Optional[QPixmap]:
    """從魚種目錄取得第一幀游泳動畫作為預覽圖，縮放為指定尺寸（行為與鬥魚、鯊魚、孔雀魚相同）。"""
    if not species_dir.exists() or not species_dir.is_dir():
        return None
    swim_behavior, _, _ = get_fish_behaviors(species_dir.name)
    frames = load_fish_animation(species_dir, swim_behavior)
    if not frames:
        frames = load_fish_animation(species_dir, "1_游動")
    if not frames:
        return None
    return frames[0].scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)


class ShopOverlay(QFrame):
    """
    商店半透明覆蓋視窗
    
    顯示在水族箱頁面階層上，未來會提供魚的選項供購買。
    購買條件（預留）：
    1. 解鎖：是否曾經滿足指定魚種的數量
    2. 購買時：是否當下滿足指定魚種的數量；點擊購買後在水族箱生成新魚種，指定魚種會被殺死（觸發餓肚子死掉動畫）
    """

    # 關閉商店時發出
    closed = pyqtSignal()
    # 寵物購買請求時發出（pet_name）
    pet_purchase_requested = pyqtSignal(str)
    # 寵物升級請求時發出（pet_name）
    pet_upgrade_requested = pyqtSignal(str)
    # 魚種購買請求時發出（species_name）
    fish_purchase_requested = pyqtSignal(str)
    # 飼料解鎖請求時發出（feed_name，如核廢料犧牲 6 隻中鬥魚解鎖）
    feed_unlock_requested = pyqtSignal(str)
    # 工具解鎖請求時發出（tool_name）
    tool_unlock_requested = pyqtSignal(str)
    # 工具顏色變更請求時發出（tool_name, color_name）
    tool_color_changed = pyqtSignal(str, str)

    def __init__(self, geometry: QRect, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setGeometry(geometry)
        self.setObjectName("ShopOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # 半透明深色背景
        self.setStyleSheet(
            "#ShopOverlay { background-color: rgba(30, 35, 45, 220); border-radius: 12px; }"
            "QLabel { color: #e0e0e0; }"
            "QPushButton { min-height: 28px; padding: 4px 12px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 標題列：商店 + 關閉按鈕
        title_row = QHBoxLayout()
        title = QLabel("商店")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffd700;")
        title_row.addWidget(title)
        title_row.addStretch()
        btn_close = QPushButton("關閉")
        btn_close.setFixedHeight(32)
        btn_close.clicked.connect(self._on_close)
        btn_close.setStyleSheet(
            "QPushButton { background-color: rgba(100, 100, 100, 200); color: white; }"
            "QPushButton:hover { background-color: rgba(120, 120, 120, 255); }"
        )
        title_row.addWidget(btn_close)
        layout.addLayout(title_row)

        # 魚種 / 寵物 tab
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet("QTabWidget::pane { border: none; background: transparent; }")
        # 魚種 tab（與寵物相同欄位：預覽圖、名稱、描述、解鎖條件、購買按鈕）
        fish_tab = QWidget()
        self._fish_items_scroll = QScrollArea()
        self._fish_items_scroll.setWidgetResizable(True)
        self._fish_items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._fish_items_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        fish_inner = QWidget()
        self._fish_items_layout = QVBoxLayout(fish_inner)
        self._fish_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._fish_items_scroll.setWidget(fish_inner)
        fish_tab_layout = QVBoxLayout(fish_tab)
        fish_tab_layout.setContentsMargins(0, 0, 0, 0)
        fish_tab_layout.addWidget(self._fish_items_scroll)
        self._tab_widget.addTab(fish_tab, "魚種")
        # 寵物 tab
        pet_tab = QWidget()
        self._items_scroll = QScrollArea()
        self._items_scroll.setWidgetResizable(True)
        self._items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._items_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        items_inner = QWidget()
        self._items_layout = QVBoxLayout(items_inner)
        self._items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._items_scroll.setWidget(items_inner)
        pet_tab_layout = QVBoxLayout(pet_tab)
        pet_tab_layout.setContentsMargins(0, 0, 0, 0)
        pet_tab_layout.addWidget(self._items_scroll)
        self._tab_widget.addTab(pet_tab, "寵物")
        # 飼料 tab（核廢料等解鎖：犧牲 6 隻中鬥魚解鎖時按鈕顯示解鎖）
        feed_tab = QWidget()
        self._feed_items_scroll = QScrollArea()
        self._feed_items_scroll.setWidgetResizable(True)
        self._feed_items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._feed_items_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._feed_items_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        feed_inner = QWidget()
        self._feed_items_layout = QVBoxLayout(feed_inner)
        self._feed_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._feed_items_scroll.setWidget(feed_inner)
        feed_tab_layout = QVBoxLayout(feed_tab)
        feed_tab_layout.setContentsMargins(0, 0, 0, 0)
        feed_tab_layout.addWidget(self._feed_items_scroll)
        self._tab_widget.addTab(feed_tab, "飼料")
        # 工具 tab
        tool_tab = QWidget()
        self._tool_items_scroll = QScrollArea()
        self._tool_items_scroll.setWidgetResizable(True)
        self._tool_items_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._tool_items_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        tool_inner = QWidget()
        self._tool_items_layout = QVBoxLayout(tool_inner)
        self._tool_items_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._tool_items_scroll.setWidget(tool_inner)
        tool_tab_layout = QVBoxLayout(tool_tab)
        tool_tab_layout.setContentsMargins(0, 0, 0, 0)
        tool_tab_layout.addWidget(self._tool_items_scroll)
        self._tab_widget.addTab(tool_tab, "工具")
        layout.addWidget(self._tab_widget, 1)

    def _on_close(self) -> None:
        self.closed.emit()
        self.hide()

    def _update_feed_items(
        self,
        unlocked_feeds: List[str],
        fish_counts: dict,
        feed_cheap_count: int = 0,
        unlocked_species: Optional[dict] = None,
    ) -> None:
        """更新飼料 tab：格式與魚種／寵物一致（黃字名稱、說明、解鎖條件），含便宜飼料、鯉魚飼料、藥丸、核廢料。"""
        while self._feed_items_layout.count():
            item = self._feed_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        resource_dir = _resource_dir()
        feed_dir = resource_dir / "feed"
        unlocked_species = unlocked_species or {}
        # 飼料說明（與魚種／寵物同欄位：名稱、說明、解鎖條件）
        feed_descriptions = {
            "便宜飼料": "成長度 2，可無限投餵。",
            "鯉魚飼料": "成長度 5。解鎖後每 5 秒數量+1。",
            "藥丸": "成長度 10。解鎖後每 20 秒數量+1。",
            "核廢料": "成長度 1。解鎖後每 300 秒數量+1。僅鬥魚會吃（寵物類不吃）；進食後 80% 死亡、20% 複製。",
            "金條": "看似有價值，但不是拿來賣的",
            "鑽石": "看似有價值，但不是拿來賣的",
        }
        for feed_name in list(FEED_UNLOCK_CONFIG.keys()):
            cfg = FEED_UNLOCK_CONFIG.get(feed_name, {})
            is_unlocked = feed_name in unlocked_feeds
            unlock_text = ""
            if cfg.get("unlock_by") == "always":
                unlock_text = "已解鎖"
            elif cfg.get("unlock_by") == "feed_cheap_count":
                need = cfg.get("unlock_value", 100)
                if is_unlocked:
                    unlock_text = "已解鎖"
                else:
                    unlock_text = f"解鎖條件：投餵便宜飼料 {need} 次（目前 {feed_cheap_count} 次）"
            elif cfg.get("unlock_by") == "large_betta_count":
                need = cfg.get("unlock_value", 10)
                key = "large_鬥魚"
                total_count = unlocked_species.get(key, {}).get("total_count_reached", 0)
                max_count = unlocked_species.get(key, {}).get("max_count_reached", 0)
                if is_unlocked:
                    unlock_text = "已解鎖"
                else:
                    # 顯示累計總數（如果有）和最大同時數量
                    if total_count > 0:
                        unlock_text = f"解鎖條件：曾達到 {need} 隻成年鬥魚（累計 {total_count} 隻）"
                    else:
                        unlock_text = f"解鎖條件：曾達到 {need} 隻成年鬥魚（目前最多 {max_count} 隻）"
            elif cfg.get("unlock_by") == "sacrifice_medium_betta":
                need_count = cfg.get("unlock_value", 6)
                medium_betta_count = fish_counts.get("medium_鬥魚", 0)
                if is_unlocked:
                    unlock_text = "已解鎖"
                else:
                    unlock_text = f"解鎖條件：場上至少 {need_count} 隻中鬥魚（目前中鬥魚：{medium_betta_count} 隻）"
            else:
                unlock_text = "已解鎖" if is_unlocked else "解鎖條件：寶箱怪升級"

            if feed_name in CHEST_FEED_ITEMS:
                feed_path = _get_chest_feed_image_path(feed_name)
                if not feed_path.exists():
                    feed_path = None
            else:
                feed_path = feed_dir / feed_name if feed_dir.exists() else None
                if not feed_path or not feed_path.is_dir():
                    feed_path = None
            preview_pixmap = _feed_preview_pixmap(feed_path, 64) if feed_path else None

            card = QFrame()
            card.setStyleSheet(
                "QFrame { background-color: rgba(50, 55, 65, 200); border-radius: 8px; padding: 8px; }"
            )
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(12)
            preview_label = QLabel()
            preview_label.setFixedSize(64, 64)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setScaledContents(False)
            if preview_pixmap and not preview_pixmap.isNull():
                w, h = preview_pixmap.width(), preview_pixmap.height()
                if w > 0 and h > 0:
                    scale = min(50.0 / w, 50.0 / h)
                    sw, sh = int(w * scale), int(h * scale)
                    scaled = preview_pixmap.scaled(sw, sh, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    preview_label.setPixmap(scaled)
            preview_label.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 4px;")
            card_layout.addWidget(preview_label)

            info_container = QWidget()
            info_container.setMaximumWidth(200)
            info_layout = QVBoxLayout(info_container)
            info_layout.setSpacing(4)
            info_layout.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(feed_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700;")
            info_layout.addWidget(name_label)
            desc_text = feed_descriptions.get(feed_name, "")
            if desc_text:
                desc_label = QLabel(desc_text)
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                info_layout.addWidget(desc_label)
            status_label = QLabel(unlock_text)
            status_label.setWordWrap(True)
            if is_unlocked:
                status_label.setStyleSheet("color: #90ee90; font-size: 12px;")
            else:
                status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            info_layout.addWidget(status_label)
            card_layout.addWidget(info_container, 1)

            if cfg.get("unlock_by") == "sacrifice_medium_betta" and not is_unlocked:
                need_count = cfg.get("unlock_value", 6)
                medium_betta_count = fish_counts.get("medium_鬥魚", 0)
                if medium_betta_count >= need_count:
                    btn = QPushButton("解鎖")
                    btn.setStyleSheet(
                        "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; }"
                        "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
                    )
                    btn.clicked.connect(lambda checked, n=feed_name: self.feed_unlock_requested.emit(n))
                else:
                    btn = QPushButton("未解鎖")
                    btn.setEnabled(False)
                    btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
                btn.setFixedWidth(80)
                card_layout.addWidget(btn)
            else:
                # 無按鈕的飼料（便宜飼料、鯉魚飼料、藥丸等）：右側保留同寬佔位，格式與有 btn 一致
                placeholder = QWidget()
                placeholder.setFixedWidth(80)
                card_layout.addWidget(placeholder)

            self._feed_items_layout.addWidget(card)
        self._feed_items_layout.addStretch()

    def _update_fish_items(
        self,
        unlocked_species: dict,
        total_money: int,
        fish_counts: dict,
    ) -> None:
        """更新魚種 tab 商品卡片（與寵物 tab 相同欄位：預覽圖、名稱、描述、解鎖條件、購買按鈕）。"""
        while self._fish_items_layout.count():
            item = self._fish_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        resource_dir = _resource_dir()
        for species_name, cfg in FISH_SHOP_CONFIG.items():
            is_unlocked = False
            unlock_text = ""
            if "unlock_money" in cfg:
                if cfg.get("unlock_money", 0) == 0:
                    is_unlocked = True
                else:
                    unlock_text = f"解鎖條件：{cfg['unlock_money']} 金幣"
            else:
                unlock_species = cfg.get("unlock_species", "")
                unlock_count = cfg.get("unlock_count", 0)
                key = unlock_species if "_" in unlock_species else unlock_species
                if key in unlocked_species:
                    max_count = unlocked_species[key].get("max_count_reached", 0)
                    is_unlocked = max_count >= unlock_count
                if not is_unlocked:
                    # 將 "angel_鬥魚" 轉換為 "天使鬥魚" 顯示
                    display_unlock_species = "天使鬥魚" if unlock_species == "angel_鬥魚" else unlock_species
                    unlock_text = f"解鎖條件：犧牲 {unlock_count} 隻{display_unlock_species}"
            can_purchase = is_unlocked
            purchase_hint = ""
            if is_unlocked:
                if cfg.get("require_species") and cfg.get("require_count", 0) > 0:
                    req_key = cfg["require_species"]
                    if "_" in req_key:
                        current = fish_counts.get(req_key, 0)
                    else:
                        current = fish_counts.get(req_key, 0)
                    can_purchase = current >= cfg["require_count"]
                    # 將 "angel_鬥魚" 轉換為 "天使鬥魚" 顯示
                    display_require_species = "天使鬥魚" if cfg["require_species"] == "angel_鬥魚" else cfg["require_species"]
                    purchase_hint = f"需要 {cfg['require_count']} 隻{display_require_species}"
                elif cfg.get("purchase_money", 0) > 0:
                    can_purchase = total_money >= cfg["purchase_money"]
                    purchase_hint = f"消耗 {cfg['purchase_money']} 金幣"
            card = QFrame()
            card.setStyleSheet(
                "QFrame { background-color: rgba(50, 55, 65, 200); border-radius: 8px; padding: 8px; }"
            )
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(12)
            preview_label = QLabel()
            preview_label.setFixedSize(64, 64)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setScaledContents(False)
            fish_dir = resource_dir / "fish" / species_name
            for behavior in ("5_吃飽游泳", "6_吃飽吃", "7_吃飽轉向"):
                anim_dir = fish_dir / behavior
                if anim_dir.is_dir():
                    frame_files = sorted(p for p in anim_dir.iterdir() if p.suffix == ".png" and p.is_file())
                    if frame_files:
                        preview_pixmap = QPixmap(str(frame_files[0]))
                        if not preview_pixmap.isNull() and preview_pixmap.width() > 0 and preview_pixmap.height() > 0:
                            scale_w = 50.0 / preview_pixmap.width()
                            scale_h = 50.0 / preview_pixmap.height()
                            scale = min(scale_w, scale_h)
                            scaled_width = int(preview_pixmap.width() * scale)
                            scaled_height = int(preview_pixmap.height() * scale)
                            scaled = preview_pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                            preview_label.setPixmap(scaled)
                        break
            preview_label.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 4px;")
            card_layout.addWidget(preview_label)
            info_container = QWidget()
            info_container.setMaximumWidth(200)
            info_layout = QVBoxLayout(info_container)
            info_layout.setSpacing(4)
            info_layout.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(species_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700;")
            info_layout.addWidget(name_label)
            description = cfg.get("description", "")
            if description:
                desc_label = QLabel(description)
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                info_layout.addWidget(desc_label)
            if is_unlocked:
                status_label = QLabel("已解鎖 · 可購買" if not purchase_hint else purchase_hint)
                status_label.setStyleSheet("color: #90ee90; font-size: 12px;")
            else:
                status_label = QLabel(unlock_text)
                status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            info_layout.addWidget(status_label)
            card_layout.addWidget(info_container, 1)
            if can_purchase:
                btn = QPushButton("購買")
                btn.setStyleSheet(
                    "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; }"
                    "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
                )
                btn.clicked.connect(lambda checked, name=species_name: self.fish_purchase_requested.emit(name))
            else:
                # 已解鎖但條件不足（如孔雀魚需犧牲天使鬥魚但場上沒有）顯示「無法召喚」
                btn_text = "無法召喚" if is_unlocked and cfg.get("require_species") and cfg.get("require_count", 0) > 0 else "未解鎖"
                btn = QPushButton(btn_text)
                btn.setEnabled(False)
                btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
            btn.setFixedWidth(80)
            card_layout.addWidget(btn)
            self._fish_items_layout.addWidget(card)
        if not FISH_SHOP_CONFIG:
            placeholder = QLabel("目前沒有可購買的魚種")
            placeholder.setStyleSheet("color: #b0b0b0; font-size: 13px; padding: 8px;")
            self._fish_items_layout.addWidget(placeholder)

    def items_layout(self) -> QVBoxLayout:
        """供未來加入魚選項按鈕/卡片的版面"""
        return self._items_layout
    
    def update_items(
        self,
        unlocked_species: dict,
        existing_pets: dict,
        total_money: int = 0,
        unlocked_pets: Optional[List[str]] = None,
        pet_levels: Optional[dict] = None,
        fish_counts: Optional[dict] = None,
        unlocked_feeds: Optional[List[str]] = None,
        feed_cheap_count: int = 0,
        unlocked_tools: Optional[List[str]] = None,
        tool_colors: Optional[dict] = None,
    ) -> None:
        """更新商店商品顯示（寵物 tab、魚種 tab、飼料 tab、工具 tab）。feed_cheap_count：投餵便宜飼料次數，供飼料 tab 解鎖說明。"""
        unlocked_pets = unlocked_pets or []
        pet_levels = pet_levels or {}
        fish_counts = fish_counts or {}
        unlocked_tools = unlocked_tools or []
        tool_colors = tool_colors or {}
        self._update_fish_items(unlocked_species, total_money, fish_counts)
        self._update_feed_items(
            unlocked_feeds or ["便宜飼料"],
            fish_counts or {},
            feed_cheap_count=feed_cheap_count,
            unlocked_species=unlocked_species,
        )
        self._update_tool_items(unlocked_species, unlocked_tools, tool_colors)
        while self._items_layout.count():
            item = self._items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        resource_dir = _resource_dir()
        for pet_name, pet_config in PET_CONFIG.items():
            is_unlocked = False
            unlock_text = ""
            # 金幣解鎖
            if "unlock_money" in pet_config:
                unlock_money = pet_config["unlock_money"]
                is_unlocked = pet_name in unlocked_pets
                if not is_unlocked:
                    unlock_text = f"解鎖條件：{unlock_money} 金幣"
            else:
                unlock_species = pet_config.get("unlock_species", "")
                unlock_count = pet_config.get("unlock_count", 0)
                if "_" in unlock_species:
                    key = unlock_species
                else:
                    key = unlock_species
                current_total = 0
                current_max = 0
                if key in unlocked_species:
                    total_count = unlocked_species[key].get("total_count_reached", 0)
                    max_count = unlocked_species[key].get("max_count_reached", 0)
                    current_total = total_count
                    current_max = max_count
                    # 與飼料投食機一致：取兩者較大的值（向後兼容舊存檔）
                    effective_count = max(total_count, max_count)
                    is_unlocked = effective_count >= unlock_count
                if not is_unlocked:
                    # 與飼料投食機一致：顯示累計或目前最多
                    display_species = "成年鬥魚" if unlock_species == "large_鬥魚" else unlock_species
                    if current_total > 0:
                        unlock_text = f"解鎖條件：曾經獲得 {unlock_count} 隻{display_species}（累計 {current_total} 隻）"
                    else:
                        unlock_text = f"解鎖條件：曾經獲得 {unlock_count} 隻{display_species}（目前最多 {current_max} 隻）"
            
            is_summoned = pet_name in existing_pets
            description = pet_config.get("description", "")
            swim_behavior = pet_config.get("swim_behavior", "1_游動")
            
            card = QFrame()
            card.setStyleSheet(
                "QFrame { background-color: rgba(50, 55, 65, 200); border-radius: 8px; padding: 8px; }"
            )
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(12)
            
            preview_label = QLabel()
            preview_label.setFixedSize(64, 64)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setScaledContents(False)
            pet_dir = resource_dir / "pet" / pet_name
            preview_path = pet_dir / swim_behavior
            if not preview_path.exists():
                preview_path = pet_dir / "1_游動"
            if preview_path.exists():
                frame_files = sorted(preview_path.glob("*.png"))
                if frame_files:
                    preview_pixmap = QPixmap(str(frame_files[0]))
                    if not preview_pixmap.isNull():
                        # 計算縮放比例，確保圖片能完整顯示在 64x64 容器內
                        pixmap_width = preview_pixmap.width()
                        pixmap_height = preview_pixmap.height()
                        scale_w = 50.0 / pixmap_width
                        scale_h = 50.0 / pixmap_height
                        scale = min(scale_w, scale_h)  # 取較小的比例，確保完整顯示
                        scaled_width = int(pixmap_width * scale)
                        scaled_height = int(pixmap_height * scale)
                        scaled = preview_pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        preview_label.setPixmap(scaled)
            preview_label.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 4px;")
            card_layout.addWidget(preview_label)
            
            info_container = QWidget()
            info_container.setMaximumWidth(200)
            info_layout = QVBoxLayout(info_container)
            info_layout.setSpacing(4)
            info_layout.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(pet_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700;")
            info_layout.addWidget(name_label)
            if description:
                desc_label = QLabel(description)
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                info_layout.addWidget(desc_label)
            current_level = pet_levels.get(pet_name, 0)
            upgrade_cfg = PET_UPGRADE_CONFIG.get(pet_name, {})
            max_level = upgrade_cfg.get("max_level", 2)
            if is_summoned:
                status_label = QLabel(f"已召喚 · 等級 {current_level}")
                status_label.setStyleSheet("color: #90ee90; font-size: 12px;")
            elif is_unlocked:
                status_label = QLabel("已解鎖 · 可召喚")
                status_label.setStyleSheet("color: #90ee90; font-size: 12px;")
            else:
                status_label = QLabel(unlock_text)
                status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            info_layout.addWidget(status_label)
            card_layout.addWidget(info_container, 1)
            
            if is_summoned:
                if current_level >= max_level:
                    btn = QPushButton("已滿級")
                    btn.setEnabled(False)
                    btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
                else:
                    cost = upgrade_cfg.get("upgrade_costs", [])[current_level]
                    btn = QPushButton(f"升級 (+{current_level + 1})\n{cost}金幣")
                    btn.setStyleSheet(
                        "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; }"
                        "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
                        "QPushButton:disabled { background-color: rgba(100, 100, 100, 150); color: #888; }"
                    )
                    if total_money < cost:
                        btn.setEnabled(False)
                    else:
                        btn.clicked.connect(lambda checked, name=pet_name: self.pet_upgrade_requested.emit(name))
            elif "unlock_money" in pet_config:
                unlock_money = pet_config["unlock_money"]
                if pet_name in unlocked_pets:
                    btn = QPushButton("召喚")
                    btn.setStyleSheet(
                        "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; }"
                        "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
                    )
                    btn.clicked.connect(lambda checked, name=pet_name: self.pet_purchase_requested.emit(name))
                elif total_money >= unlock_money:
                    btn = QPushButton("解鎖")
                    btn.setStyleSheet(
                        "QPushButton { background-color: rgba(255, 165, 0, 200); color: white; }"
                        "QPushButton:hover { background-color: rgba(255, 165, 0, 255); }"
                    )
                    btn.clicked.connect(lambda checked, name=pet_name: self.pet_purchase_requested.emit(name))
                else:
                    btn = QPushButton("未解鎖")
                    btn.setEnabled(False)
                    btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
            elif is_unlocked:
                btn = QPushButton("召喚")
                btn.setStyleSheet(
                    "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; }"
                    "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
                )
                btn.clicked.connect(lambda checked, name=pet_name: self.pet_purchase_requested.emit(name))
            else:
                btn = QPushButton("未解鎖")
                btn.setEnabled(False)
                btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
            btn.setFixedWidth(80)
            card_layout.addWidget(btn)
            self._items_layout.addWidget(card)
        
        if not PET_CONFIG:
            placeholder = QLabel("目前沒有可購買的寵物")
            placeholder.setStyleSheet("color: #b0b0b0; font-size: 13px; padding: 8px;")
            self._items_layout.addWidget(placeholder)

    def _update_tool_items(
        self,
        unlocked_species: dict,
        unlocked_tools: List[str],
        tool_colors: dict,
    ) -> None:
        """更新工具 tab：顯示工具項目（如飼料投食機）的解鎖狀態與顏色選擇。"""
        while self._tool_items_layout.count():
            item = self._tool_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        resource_dir = _resource_dir()
        for tool_name, cfg in TOOL_CONFIG.items():
            unlock_species = cfg.get("unlock_species", "")
            unlock_count = cfg.get("unlock_count", 0)
            description = cfg.get("description", "")
            
            # 判定是否已解鎖（在 unlocked_tools 列表中）
            is_unlocked = tool_name in unlocked_tools
            
            # 判定是否達到解鎖條件（以累計里程碑判定）
            can_unlock = False
            key = unlock_species
            current_total = 0
            current_max = 0
            if key in unlocked_species:
                total_count = unlocked_species[key].get("total_count_reached", 0)
                max_count = unlocked_species[key].get("max_count_reached", 0)
                current_total = total_count
                current_max = max_count
                # 取兩者較大的值（向後兼容舊存檔）
                effective_count = max(total_count, max_count)
                can_unlock = effective_count >= unlock_count
            
            unlock_text = ""
            if not is_unlocked:
                # 格式化顯示名稱（large_鬥魚 -> 成年鬥魚）
                display_species = unlock_species
                if unlock_species == "large_鬥魚":
                    display_species = "成年鬥魚"
                # 顯示累計總數（如果有）和最大同時數量
                if current_total > 0:
                    unlock_text = f"解鎖條件：曾經獲得 {unlock_count} 隻{display_species}（累計 {current_total} 隻）"
                else:
                    unlock_text = f"解鎖條件：曾經獲得 {unlock_count} 隻{display_species}（目前最多 {current_max} 隻）"
            
            # 載入預覽圖（預設灰黑色）
            preview_color = tool_colors.get(tool_name, FEED_MACHINE_DEFAULT_COLOR)
            if tool_name == "飼料投食機":
                feed_machine_path = resource_dir / "feed_machine" / f"投食機_{preview_color}.png"
                preview_pixmap = None
                if feed_machine_path.exists():
                    preview_pixmap = QPixmap(str(feed_machine_path))
                    if preview_pixmap.isNull():
                        preview_pixmap = None
            else:
                preview_pixmap = None
            
            # 建立卡片（與魚種 tab 相同欄位與樣式）
            card = QFrame()
            card.setStyleSheet(
                "QFrame { background-color: rgba(50, 55, 65, 200); border-radius: 8px; padding: 8px; }"
            )
            card_layout = QHBoxLayout(card)
            card_layout.setSpacing(12)
            
            preview_label = QLabel()
            preview_label.setFixedSize(64, 64)
            preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            preview_label.setScaledContents(False)
            if preview_pixmap and not preview_pixmap.isNull():
                w, h = preview_pixmap.width(), preview_pixmap.height()
                if w > 0 and h > 0:
                    scale = min(50.0 / w, 50.0 / h)
                    sw, sh = int(w * scale), int(h * scale)
                    scaled = preview_pixmap.scaled(sw, sh, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    preview_label.setPixmap(scaled)
            preview_label.setStyleSheet("background-color: rgba(30, 30, 30, 200); border-radius: 4px;")
            card_layout.addWidget(preview_label)
            
            info_container = QWidget()
            info_container.setMaximumWidth(200)
            info_layout = QVBoxLayout(info_container)
            info_layout.setSpacing(4)
            info_layout.setContentsMargins(0, 0, 0, 0)
            name_label = QLabel(tool_name)
            name_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffd700;")
            info_layout.addWidget(name_label)
            if description:
                desc_label = QLabel(description)
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #c0c0c0; font-size: 11px;")
                info_layout.addWidget(desc_label)
            if is_unlocked:
                status_label = QLabel("已解鎖")
                status_label.setStyleSheet("color: #90ee90; font-size: 12px;")
            else:
                status_label = QLabel(unlock_text)
                status_label.setWordWrap(True)
                status_label.setStyleSheet("color: #ff6b6b; font-size: 12px;")
            info_layout.addWidget(status_label)
            card_layout.addWidget(info_container, 1)
            
            # 操作按鈕/控制
            if is_unlocked and tool_name == "飼料投食機":
                # 已解鎖：顯示顏色下拉選單
                color_combo = QComboBox()
                color_combo.addItems(FEED_MACHINE_COLORS)
                current_color = tool_colors.get(tool_name, FEED_MACHINE_DEFAULT_COLOR)
                if current_color in FEED_MACHINE_COLORS:
                    color_combo.setCurrentText(current_color)
                color_combo.setFixedWidth(100)
                color_combo.currentTextChanged.connect(
                    lambda color, name=tool_name: self.tool_color_changed.emit(name, color)
                )
                card_layout.addWidget(color_combo)
            elif can_unlock and not is_unlocked:
                # 達到解鎖條件但尚未解鎖：顯示解鎖按鈕
                btn = QPushButton("解鎖")
                btn.setStyleSheet(
                    "QPushButton { background-color: rgba(255, 165, 0, 200); color: white; }"
                    "QPushButton:hover { background-color: rgba(255, 165, 0, 255); }"
                )
                btn.setFixedWidth(80)
                btn.clicked.connect(lambda checked, name=tool_name: self.tool_unlock_requested.emit(name))
                card_layout.addWidget(btn)
            elif not is_unlocked:
                # 未達到解鎖條件：顯示禁用按鈕（與魚種／寵物 tab 一致）
                btn = QPushButton("未解鎖")
                btn.setEnabled(False)
                btn.setStyleSheet("QPushButton { background-color: rgba(100, 100, 100, 150); color: #888; }")
                btn.setFixedWidth(80)
                card_layout.addWidget(btn)
            
            self._tool_items_layout.addWidget(card)
        self._tool_items_layout.addStretch()


class ControlPanel(QFrame):
    """
    控制面板：在水族箱外的透明視窗區域內，提供切換背景、切換飼料、投放魚的按鈕與清單。
    """

    # 選擇背景時發出 (path)
    background_selected = pyqtSignal(object)  # Path | None
    # 背景透明度變更時發出 (0~100)
    background_opacity_changed = pyqtSignal(int)
    # 選擇飼料時發出 (feed_name, feed_dir_path)
    feed_selected = pyqtSignal(str, object)
    # 選擇要投放的魚時發出 (fish_dir_path)
    fish_add_requested = pyqtSignal(object)  # Path
    # 開啟商店請求時發出
    shop_requested = pyqtSignal()
    # 關閉視窗請求時發出
    close_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("ControlPanel")
        self.setFixedWidth(PANEL_WIDTH)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # 面板背景：不透明，方便在水族箱外辨識按鈕區域
        self.setStyleSheet(
            "#ControlPanel { background-color: rgba(40, 44, 52, 230); border-radius: 8px; }"
            "QPushButton { min-height: 32px; padding: 6px; }"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 切換背景
        self._btn_bg = QPushButton("切換\n背景")
        self._btn_bg.setMinimumHeight(36)
        # 設置按鈕寬度為面板寬度的一半（減去左右邊距）
        button_width = (PANEL_WIDTH - 16) // 3  # 16 是左右邊距總和（8+8）
        self._btn_bg.setMaximumWidth(button_width)
        self._setup_button_menu(
            self._btn_bg,
            _list_backgrounds(),
            lambda p: p.stem,
            self._on_background_chosen,
        )
        layout.addWidget(self._btn_bg)

        # 背景透明度 0~100%（預設 80%）
        self._opacity_label = QLabel("背景透明度 80%")
        self._opacity_label.setStyleSheet("color: #e0e0e0; font-size: 12px;")
        layout.addWidget(self._opacity_label)
        self._opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self._opacity_slider.setMinimum(1)
        self._opacity_slider.setMaximum(100)
        self._opacity_slider.setValue(80)
        self._opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._opacity_slider.setTickInterval(25)
        self._opacity_slider.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self._opacity_slider)

        # 切換飼料（僅顯示已解鎖飼料，可點擊次數依該飼料專屬數量計數器）
        self._btn_feed = QPushButton("切換飼料")
        self._btn_feed.setMinimumHeight(36)
        self._feed_list = _list_feeds()
        self._feed_menu = QMenu(self)
        self._unlocked_feeds_for_menu: List[str] = ["便宜飼料"]
        self._feed_counters_for_menu: dict = {}
        self._feed_menu.aboutToShow.connect(self._refresh_feed_menu)
        self._refresh_feed_menu()
        self._btn_feed.setMenu(self._feed_menu)
        layout.addWidget(self._btn_feed)

        # 投放魚（選單項目左側顯示該魚種圖片）
        self._btn_fish = QPushButton("投放魚")
        self._btn_fish.setMinimumHeight(36)
        self._fish_list = _list_small_fish()
        self._fish_menu = QMenu(self)
        for name, path in self._fish_list:
            icon_pix = _fish_preview_pixmap(path)
            icon = QIcon(icon_pix) if icon_pix and not icon_pix.isNull() else QIcon()
            # 幼鬥魚顯示「花費20$」註記
            display_name = name
            if name == "鬥魚":
                display_name = f"{name} (花費{SMALL_BETTA_COST}$)"
            action = self._fish_menu.addAction(icon, display_name)
            action.triggered.connect(lambda checked, fp=path: self.fish_add_requested.emit(fp))
        self._btn_fish.setMenu(self._fish_menu)
        layout.addWidget(self._btn_fish)

        # 商店按鈕
        self._btn_shop = QPushButton("商店")
        self._btn_shop.setMinimumHeight(36)
        self._btn_shop.clicked.connect(self.shop_requested.emit)
        self._btn_shop.setStyleSheet(
            "QPushButton { background-color: rgba(76, 175, 80, 200); color: white; font-weight: bold; }"
            "QPushButton:hover { background-color: rgba(76, 175, 80, 255); }"
            "QPushButton:pressed { background-color: rgba(56, 142, 60, 255); }"
        )
        layout.addWidget(self._btn_shop)

        layout.addStretch()

        # 金錢計數器：金幣堆圖示 + 金額（放在底部，避免與右上角按鈕在同一列）
        money_row = QHBoxLayout()
        money_row.setSpacing(6)
        money_icon_path = _resource_dir() / "money" / "UI" / "UI_金幣堆-removebg-preview.png"
        self._money_icon_label = QLabel()
        self._money_icon_label.setFixedSize(30, 30)
        self._money_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._money_icon_label.setScaledContents(False)
        if money_icon_path.exists():
            money_pixmap = QPixmap(str(money_icon_path))
            if not money_pixmap.isNull():
                scaled = money_pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self._money_icon_label.setPixmap(scaled)
        money_row.addWidget(self._money_icon_label)
        self._money_label = QLabel("$0")
        self._money_label.setStyleSheet("color: #ffd700; font-weight: bold; font-size: 14px;")
        money_row.addWidget(self._money_label)
        layout.addLayout(money_row)

        # 關閉按鈕
        self._btn_close = QPushButton("關閉")
        self._btn_close.setMinimumHeight(36)
        self._btn_close.clicked.connect(self.close_requested.emit)
        # 設定關閉按鈕樣式（紅色背景）
        self._btn_close.setStyleSheet(
            "QPushButton { background-color: rgba(220, 53, 69, 200); color: white; font-weight: bold; }"
            "QPushButton:hover { background-color: rgba(220, 53, 69, 255); }"
            "QPushButton:pressed { background-color: rgba(200, 35, 51, 255); }"
        )
        layout.addWidget(self._btn_close)

    def _setup_button_menu(
        self,
        button: QPushButton,
        items: List[Path],
        label_fn,
        callback,
    ) -> None:
        menu = QMenu(self)
        for i, path in enumerate(items):
            action = menu.addAction(label_fn(path))
            action.triggered.connect(lambda checked, p=path: callback(p))
        button.setMenu(menu)

    def update_feed_menu(self, unlocked_feeds: List[str], feed_counters: dict) -> None:
        """更新切換飼料選單用的解鎖列表與計數器（僅已解鎖飼料出現在選單，可點擊次數依計數器）。"""
        self._unlocked_feeds_for_menu = list(unlocked_feeds) if unlocked_feeds else ["便宜飼料"]
        self._feed_counters_for_menu = dict(feed_counters) if feed_counters else {}
        # 選單在 aboutToShow 時會呼叫 _refresh_feed_menu 以最新資料重建

    def _refresh_feed_menu(self) -> None:
        """依已解鎖飼料與計數器重建切換飼料選單（含 resource/feed 飼料與寶箱怪飼料金條/鑽石）。"""
        self._feed_menu.clear()
        for name, path in self._feed_list:
            # 寶箱怪飼料（金條、鑽石）固定由下方 CHEST_FEED_ITEMS 區塊處理，
            # 避免在 resource/feed 清單中（若存在同名資料夾）被加入兩次而出現兩排。
            if name in CHEST_FEED_ITEMS:
                continue
            if name not in self._unlocked_feeds_for_menu:
                continue
            if name == "便宜飼料":
                label = "便宜飼料 (無限)"
            else:
                cnt = self._feed_counters_for_menu.get(name, 0)
                label = f"{name} ({cnt})"
            icon_pix = _feed_preview_pixmap(path)
            icon = QIcon(icon_pix) if icon_pix and not icon_pix.isNull() else QIcon()
            action = self._feed_menu.addAction(icon, label)
            action.triggered.connect(lambda checked, n=name, p=path: self.feed_selected.emit(n, p))
        # 寶箱怪飼料（金條、鑽石）：有解鎖且數量 > 0 時才出現在選單
        for name in CHEST_FEED_ITEMS:
            if name not in self._unlocked_feeds_for_menu:
                continue
            # 優先使用 resource/feed/ 目錄路徑（用於動畫），如果不存在則使用單一圖片路徑（用於預覽圖）
            feed_dir = _resource_dir() / "feed" / name
            if feed_dir.exists() and feed_dir.is_dir():
                path = feed_dir
            else:
                path = _get_chest_feed_image_path(name)
            cnt = self._feed_counters_for_menu.get(name, 0)
            label = f"{name} ({cnt})"
            # 預覽圖使用單一圖片路徑
            preview_path = _get_chest_feed_image_path(name)
            icon_pix = _feed_preview_pixmap(preview_path)
            icon = QIcon(icon_pix) if icon_pix and not icon_pix.isNull() else QIcon()
            action = self._feed_menu.addAction(icon, label)
            action.triggered.connect(lambda checked, n=name, p=path: self.feed_selected.emit(n, p))

    def _on_background_chosen(self, path: Path) -> None:
        self.background_selected.emit(path)

    def _on_opacity_changed(self, value: int) -> None:
        self._opacity_label.setText(f"背景透明度 {value}%")
        self.background_opacity_changed.emit(value)
    

    def set_money(self, value: int) -> None:
        """更新金錢計數器顯示（圖示旁的金額）"""
        self._money_label.setText(f"${value}")


class TransparentAquariumWindow(QWidget):
    """
    透明水族箱視窗
    
    創建一個透明視窗，其中包含一個水族箱區域。
    視窗除了水族箱區域外都是透明的，並且透明區域不接收滑鼠事件。
    """
    
    def __init__(self, aquarium_size: tuple = (800, 600), background_path: Optional[Path] = None):
        """
        初始化透明水族箱視窗
        
        Args:
            aquarium_size: 水族箱區域大小 (寬度, 高度)
            background_path: 背景圖片路徑
        """
        super().__init__()
        
        self.aquarium_size = aquarium_size
        # 左側空白區域用於放置投食機（高度與主視窗一致，使用 aquarium_size[1]）
        self.feed_machine_area_rect = QRect(0, 0, FEED_MACHINE_AREA_WIDTH, aquarium_size[1])
        # 水族箱區域向右移動，不包含左側空白區域
        self.aquarium_rect = QRect(FEED_MACHINE_AREA_WIDTH, 0, aquarium_size[0], aquarium_size[1])
        # 控制面板區域也向右移動
        self.panel_rect = QRect(FEED_MACHINE_AREA_WIDTH + aquarium_size[0], 0, PANEL_WIDTH, aquarium_size[1])

        # 設定視窗屬性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 無邊框
            Qt.WindowType.WindowStaysOnTopHint |  # 保持在最上層
            Qt.WindowType.Tool  # 工具視窗（不顯示在工作列）
        )

        # 設定視窗背景為透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 啟用滑鼠追蹤（用於檢測滑鼠移動到金錢物件上）
        self.setMouseTracking(True)

        # 視窗大小 = 左側空白區域 + 水族箱 + 右側按鈕面板
        self.setFixedSize(FEED_MACHINE_AREA_WIDTH + aquarium_size[0] + PANEL_WIDTH, aquarium_size[1])

        # 創建水族箱部件
        self.aquarium = AquariumWidget(background_path, self)
        self.aquarium.setGeometry(self.aquarium_rect)
        self.aquarium.clicked.connect(self.on_aquarium_clicked)
        self.aquarium.money_hovered.connect(self.on_money_hovered)
        self.aquarium.pet_duplicate_requested.connect(self._on_pet_duplicate_requested)
        self.aquarium.game_time_updated.connect(self._on_game_time_updated)

        # 飼料解鎖與數量計數器（待解鎖的飼料不出現在切換飼料選單）
        self._feed_cheap_count = 0
        self._feed_counters = {}
        self._unlocked_feeds = ["便宜飼料"]
        self._feed_counter_last_add = {}

        # 創建控制面板（水族箱外、透明視窗內）
        self.panel = ControlPanel(self)
        self.panel.setGeometry(self.panel_rect)
        self.panel.background_selected.connect(self.on_background_selected)
        self.panel.background_opacity_changed.connect(self.on_background_opacity_changed)
        self.panel.feed_selected.connect(self.on_feed_selected)
        self.panel.fish_add_requested.connect(self.on_fish_add_requested)
        self.panel.shop_requested.connect(self.on_shop_requested)
        self.panel.close_requested.connect(self.close_window)

        # 商店半透明覆蓋視窗（疊在水族箱上層）
        self._shop_overlay = ShopOverlay(self.aquarium_rect, self)
        self._shop_overlay.hide()
        self._shop_overlay.closed.connect(self._on_shop_closed)
        self._shop_overlay.pet_purchase_requested.connect(self._on_pet_purchase_requested)
        self._shop_overlay.pet_upgrade_requested.connect(self._on_pet_upgrade_requested)
        self._shop_overlay.fish_purchase_requested.connect(self._on_fish_purchase_requested)
        self._shop_overlay.feed_unlock_requested.connect(self._on_feed_unlock_requested)
        self._shop_overlay.tool_unlock_requested.connect(self._on_tool_unlock_requested)
        self._shop_overlay.tool_color_changed.connect(self._on_tool_color_changed)
        
        # 投食機透明部件（重疊在主視窗上，掛在水族箱左側）
        self._feed_machine_widget = FeedMachineWidget(self)
        self._feed_machine_widget.feed_selected.connect(self._on_feed_machine_feed_selected)
        self._feed_machine_widget.set_unlocked_feeds(self._unlocked_feeds, self._feed_counters)
        
        # 投食機自動投食計時器
        self._feed_machine_timer = 0.0  # 秒
        self._feed_machine_interval = FEED_MACHINE_INTERVAL_SEC  # 投食間隔（從 config 讀取）
        
        # 寵物追蹤：{pet_name: pet_instance}
        self._pets: dict = {}

        # 設定視窗標題
        self.setWindowTitle("桌面水族箱")

        # 初始化狀態變量（需要在 updateWindowMask() 之前初始化）
        # 錨定狀態：是否禁止拖動視窗
        self._is_anchored = False
        # 隱藏狀態：是否隱藏視窗內容
        self._is_hidden = False
        # 保存隱藏前的視窗位置
        self._saved_window_pos: Optional[QPoint] = None
        # 擊殺模式：是否啟用擊殺功能
        self._kill_mode_enabled = False

        # 遮罩：水族箱 + 面板區域可接收滑鼠，其餘穿透
        # 注意：updateWindowMask() 會在創建控制按鈕後再次調用，這裡先調用以設置基本遮罩
        self.updateWindowMask()

        # 金錢總計（點擊拾取金錢時增加）
        self.total_money = 0
        
        # 追蹤上一次是否滿足贈送條件（用於檢測狀態變化）
        self._last_bonus_condition_met = False

        # 解鎖狀態追蹤：{species: {"max_count_reached": int, "unlocked": bool}}
        self._unlocked_species: dict = {}
        self._unlocked_pets: list = []  # 金幣解鎖的寵物名稱列表
        # 寵物等級：{pet_name: level}，0=基礎、1=+1、2=+2
        self._pet_levels: dict = {}
        # 工具解鎖狀態：已解鎖的工具名稱列表
        self._unlocked_tools: list = []
        # 工具顏色：{tool_name: color_name}
        self._tool_colors: dict = {}

        # 初始不載入魚，由使用者從「投放魚」按鈕自行新增
        # 設定預設飼料為"便宜飼料"
        feed_dir = _resource_dir() / "feed" / "便宜飼料"
        if feed_dir.exists():
            self._current_feed = ("便宜飼料", feed_dir)
        else:
            self._current_feed = None
        
        # 載入遊戲狀態
        self._load_game_state()
        
        # 更新工具解鎖狀態與顯示
        self._update_tool_unlocks()
        
        # 創建右上角隱藏按鈕（放在最右側）
        self._hide_button = QPushButton("👁", self)
        self._hide_button.setFixedSize(30, 30)
        self._hide_button.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(60, 60, 60, 200); "
            "border: 1px solid rgba(100, 100, 100, 200); "
            "border-radius: 4px; "
            "color: white; "
            "font-size: 16px; "
            "font-weight: bold; "
            "}"
            "QPushButton:hover { "
            "background-color: rgba(80, 80, 80, 255); "
            "}"
            "QPushButton:pressed { "
            "background-color: rgba(100, 100, 100, 255); "
            "}"
        )
        self._hide_button.clicked.connect(self._toggle_hide)
        
        # 創建右上角錨定按鈕（放在隱藏按鈕左側）
        self._anchor_button = QPushButton("⚓", self)
        self._anchor_button.setFixedSize(30, 30)
        self._anchor_button.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(60, 60, 60, 200); "
            "border: 1px solid rgba(100, 100, 100, 200); "
            "border-radius: 4px; "
            "color: white; "
            "font-size: 16px; "
            "font-weight: bold; "
            "}"
            "QPushButton:hover { "
            "background-color: rgba(80, 80, 80, 255); "
            "}"
            "QPushButton:pressed { "
            "background-color: rgba(100, 100, 100, 255); "
            "}"
        )
        self._anchor_button.clicked.connect(self._toggle_anchor)
        
        # 創建右上角擊殺模式按鈕（放在錨定按鈕左側）
        self._kill_button = QPushButton("⚔", self)
        self._kill_button.setFixedSize(30, 30)
        self._kill_button.setStyleSheet(
            "QPushButton { "
            "background-color: rgba(60, 60, 60, 200); "
            "border: 1px solid rgba(100, 100, 100, 200); "
            "border-radius: 4px; "
            "color: white; "
            "font-size: 16px; "
            "font-weight: bold; "
            "}"
            "QPushButton:hover { "
            "background-color: rgba(80, 80, 80, 255); "
            "}"
            "QPushButton:pressed { "
            "background-color: rgba(100, 100, 100, 255); "
            "}"
        )
        self._kill_button.clicked.connect(self._toggle_kill_mode)
        self._update_button_positions()
        
    def _update_button_positions(self) -> None:
        """更新右上角按鈕位置"""
        button_size = 30
        margin = 5
        button_spacing = 5  # 按鈕之間的間距
        
        # 隱藏按鈕在最右側
        hide_x = self.width() - button_size - margin
        hide_y = margin
        self._hide_button.move(hide_x, hide_y)
        
        # 錨定按鈕在隱藏按鈕左側
        anchor_x = hide_x - button_size - button_spacing
        anchor_y = margin
        self._anchor_button.move(anchor_x, anchor_y)
        
        # 擊殺按鈕在錨定按鈕左側
        kill_x = anchor_x - button_size - button_spacing
        kill_y = margin
        self._kill_button.move(kill_x, kill_y)
        
        # 確保按鈕在最上層
        self._hide_button.raise_()
        self._anchor_button.raise_()
        self._kill_button.raise_()
        
    def _toggle_anchor(self) -> None:
        """切換錨定狀態"""
        self._is_anchored = not self._is_anchored
        if self._is_anchored:
            # 錨定狀態：顯示深色背景
            self._anchor_button.setStyleSheet(
                "QPushButton { "
                "background-color: rgba(100, 150, 200, 255); "
                "border: 1px solid rgba(150, 200, 255, 255); "
                "border-radius: 4px; "
                "color: white; "
                "font-size: 16px; "
                "font-weight: bold; "
                "}"
                "QPushButton:hover { "
                "background-color: rgba(120, 170, 220, 255); "
                "}"
                "QPushButton:pressed { "
                "background-color: rgba(80, 130, 180, 255); "
                "}"
            )
        else:
            # 未錨定狀態：恢復原樣
            self._anchor_button.setStyleSheet(
                "QPushButton { "
                "background-color: rgba(60, 60, 60, 200); "
                "border: 1px solid rgba(100, 100, 100, 200); "
                "border-radius: 4px; "
                "color: white; "
                "font-size: 16px; "
                "font-weight: bold; "
                "}"
                "QPushButton:hover { "
                "background-color: rgba(80, 80, 80, 255); "
                "}"
                "QPushButton:pressed { "
                "background-color: rgba(100, 100, 100, 255); "
                "}"
            )
    
    def _toggle_kill_mode(self) -> None:
        """切換擊殺模式"""
        self._kill_mode_enabled = not self._kill_mode_enabled
        
        if self._kill_mode_enabled:
            # 擊殺模式開啟：顯示紅色背景
            self._kill_button.setStyleSheet(
                "QPushButton { "
                "background-color: rgba(200, 50, 50, 255); "
                "border: 1px solid rgba(255, 100, 100, 255); "
                "border-radius: 4px; "
                "color: white; "
                "font-size: 16px; "
                "font-weight: bold; "
                "}"
                "QPushButton:hover { "
                "background-color: rgba(220, 70, 70, 255); "
                "}"
                "QPushButton:pressed { "
                "background-color: rgba(180, 30, 30, 255); "
                "}"
            )
            # 顯示提示視窗
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("擊殺模式")
            msg_box.setWindowIcon(_get_app_icon())
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setText("點擊魚會殺死魚喔！")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.button(QMessageBox.StandardButton.Ok).setText("知道了")
            msg_box.exec()
        else:
            # 擊殺模式關閉：恢復原樣
            self._kill_button.setStyleSheet(
                "QPushButton { "
                "background-color: rgba(60, 60, 60, 200); "
                "border: 1px solid rgba(100, 100, 100, 200); "
                "border-radius: 4px; "
                "color: white; "
                "font-size: 16px; "
                "font-weight: bold; "
                "}"
                "QPushButton:hover { "
                "background-color: rgba(80, 80, 80, 255); "
                "}"
                "QPushButton:pressed { "
                "background-color: rgba(100, 100, 100, 255); "
                "}"
            )
    
    def _toggle_hide(self) -> None:
        """切換隱藏狀態"""
        self._is_hidden = not self._is_hidden
        
        if self._is_hidden:
            # 隱藏狀態：隱藏所有內容，只保留按鈕
            # 保存當前視窗位置和按鈕在螢幕上的絕對位置
            self._saved_window_pos = self.pos()
            
            # 計算按鈕在螢幕上的絕對位置（視窗位置 + 按鈕相對位置）
            hide_button_global_pos = self._hide_button.mapToGlobal(QPoint(0, 0))
            anchor_button_global_pos = self._anchor_button.mapToGlobal(QPoint(0, 0))
            
            self.aquarium.hide()
            self.panel.hide()
            if hasattr(self, '_feed_machine_widget'):
                self._feed_machine_widget.hide()
            if hasattr(self, '_shop_overlay'):
                self._shop_overlay.hide()
            
            # 更新隱藏按鈕圖標為閉眼（使用更通用的符號）
            self._hide_button.setText("🙈")
            
            # 更新視窗大小為只包含按鈕的大小
            button_width = 30 + 30 + 30 + 10 + 10  # 三個按鈕寬度 + 間距 + 邊距
            button_height = 30 + 10  # 按鈕高度 + 邊距
            self.setFixedSize(button_width, button_height)
            
            # 調整視窗位置，使按鈕保持在螢幕上的相同位置
            # 隱藏按鈕應該在視窗的右上角（最右側）
            margin = 5
            button_size = 30
            # 計算新的視窗位置：按鈕的絕對位置 - 按鈕在視窗內的相對位置
            # button_width 現在包含三個按鈕
            new_window_x = hide_button_global_pos.x() - (button_width - button_size - margin)
            new_window_y = hide_button_global_pos.y() - margin
            
            # 確保視窗不會超出螢幕邊界
            screen_geometry = self.screen().availableGeometry()
            if new_window_x + button_width > screen_geometry.right():
                new_window_x = screen_geometry.right() - button_width
            if new_window_x < screen_geometry.left():
                new_window_x = screen_geometry.left()
            if new_window_y + button_height > screen_geometry.bottom():
                new_window_y = screen_geometry.bottom() - button_height
            if new_window_y < screen_geometry.top():
                new_window_y = screen_geometry.top()
            
            self.move(new_window_x, new_window_y)
            
            # 更新按鈕位置（因為視窗大小改變了）
            self._update_button_positions()
        else:
            # 顯示狀態：恢復所有內容
            self.aquarium.show()
            self.panel.show()
            if hasattr(self, '_feed_machine_widget'):
                self._feed_machine_widget.show()
            
            # 更新隱藏按鈕圖標為睜眼
            self._hide_button.setText("👁")
            
            # 恢復視窗大小
            self.setFixedSize(FEED_MACHINE_AREA_WIDTH + self.aquarium_size[0] + PANEL_WIDTH, self.aquarium_size[1])
            
            # 恢復視窗位置（如果之前保存過）
            if self._saved_window_pos is not None:
                self.move(self._saved_window_pos)
            
            # 更新按鈕位置
            self._update_button_positions()
        
        # 更新視窗遮罩
        self.updateWindowMask()
        
    def updateWindowMask(self) -> None:
        """
        更新視窗遮罩
        
        如果隱藏：只有按鈕區域可接收滑鼠事件
        如果未隱藏：左側空白區域、水族箱區域、按鈕面板、控制按鈕可接收滑鼠事件，其餘透明區域點擊穿透。
        """
        if self._is_hidden:
            # 隱藏狀態：只有按鈕區域可點擊
            region = QRegion()
            if hasattr(self, '_hide_button'):
                button_rect = self._hide_button.geometry()
                region = region | QRegion(button_rect)
            if hasattr(self, '_anchor_button'):
                button_rect = self._anchor_button.geometry()
                region = region | QRegion(button_rect)
            if hasattr(self, '_kill_button'):
                button_rect = self._kill_button.geometry()
                region = region | QRegion(button_rect)
            self.setMask(region)
        else:
            # 正常狀態：所有區域可點擊
            # 使用主視窗的實際高度，確保左側空白區域與主視窗高度一致
            window_height = self.height()
            # 左側空白區域（用於投食機）- 高度與主視窗一致
            feed_machine_area = QRect(0, 0, FEED_MACHINE_AREA_WIDTH, window_height)
            region = QRegion(feed_machine_area)
            # 水族箱區域
            region = region | QRegion(self.aquarium_rect)
            # 右側控制面板區域
            region = region | QRegion(self.panel_rect)
            # 控制按鈕區域
            if hasattr(self, '_hide_button'):
                button_rect = self._hide_button.geometry()
                region = region | QRegion(button_rect)
            if hasattr(self, '_anchor_button'):
                button_rect = self._anchor_button.geometry()
                region = region | QRegion(button_rect)
            if hasattr(self, '_kill_button'):
                button_rect = self._kill_button.geometry()
                region = region | QRegion(button_rect)
            self.setMask(region)
    
    def resizeEvent(self, event) -> None:
        """處理視窗大小改變事件"""
        super().resizeEvent(event)
        # 更新按鈕位置
        if hasattr(self, '_anchor_button') and hasattr(self, '_hide_button') and hasattr(self, '_kill_button'):
            self._update_button_positions()
        # 更新遮罩以適應新的視窗大小
        self.updateWindowMask()
    
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """繪製視窗（主要是處理透明區域）"""
        # 父類的 paintEvent 會處理透明背景
        super().paintEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
        處理滑鼠點擊事件
        
        水族箱區域與按鈕面板區域內的點擊會傳給對應部件，其餘穿透。
        商店覆蓋顯示時，水族箱區域的點擊改傳給商店覆蓋。
        左側空白區域的點擊會穿透到水族箱（用於投放飼料）。
        """
        pos = event.position().toPoint()

        # 優先處理控制按鈕的點擊
        if hasattr(self, '_kill_button') and self._kill_button.geometry().contains(pos):
            # 將事件傳遞給擊殺按鈕
            local_pos = pos - self._kill_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._kill_button.mousePressEvent(button_event)
            return
        
        if hasattr(self, '_hide_button') and self._hide_button.geometry().contains(pos):
            # 將事件傳遞給隱藏按鈕
            local_pos = pos - self._hide_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._hide_button.mousePressEvent(button_event)
            return
        
        if hasattr(self, '_anchor_button') and self._anchor_button.geometry().contains(pos):
            # 將事件傳遞給按鈕
            local_pos = pos - self._anchor_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._anchor_button.mousePressEvent(button_event)
            return

        # 優先處理水族箱區域和左側空白區域的點擊
        if self.aquarium_rect.contains(pos):
            # 檢查是否點擊在投食機部件的圖片區域內（如果可見且重疊）
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 點擊在水族箱區域，且不在投食機圖片上
                if self._shop_overlay.isVisible():
                    overlay_event = QMouseEvent(
                        event.type(),
                        QPointF(pos - self._shop_overlay.geometry().topLeft()),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self._shop_overlay.mousePressEvent(overlay_event)
                else:
                    # 將主視窗座標轉換為水族箱部件相對座標
                    aquarium_local_pos = pos - self.aquarium_rect.topLeft()
                    aquarium_event = QMouseEvent(
                        event.type(),
                        QPointF(aquarium_local_pos),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self.aquarium.mousePressEvent(aquarium_event)
                return
        elif self.feed_machine_area_rect.contains(pos):
            # 點擊在左側空白區域
            # 檢查是否點擊在投食機部件的圖片區域內
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 點擊在左側空白區域，且不在投食機圖片上，映射到水族箱左側
                aquarium_local_x = pos.x()  # 左側空白區域的 x 直接映射到水族箱的 x（0 到 FEED_MACHINE_AREA_WIDTH）
                aquarium_local_y = pos.y()
                aquarium_local_pos = QPoint(aquarium_local_x, aquarium_local_y)
                aquarium_event = QMouseEvent(
                    event.type(),
                    QPointF(aquarium_local_pos),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
                self.aquarium.mousePressEvent(aquarium_event)
                return
        
        # 檢查是否點擊在投食機部件的圖片區域內（但不在水族箱或左側空白區域）
        if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
            feed_machine_geometry = self._feed_machine_widget.geometry()
            if feed_machine_geometry.contains(pos):
                local_pos = pos - feed_machine_geometry.topLeft()
                image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                if image_rect and image_rect.contains(local_pos):
                    # 點擊在投食機圖片區域內，可以處理（未來可能添加互動功能）
                    # 目前先忽略，讓事件穿透
                    event.ignore()
                    return
        
        if self.aquarium_rect.contains(pos):
            if self._shop_overlay.isVisible():
                overlay_event = QMouseEvent(
                    event.type(),
                    QPointF(pos - self._shop_overlay.geometry().topLeft()),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
                self._shop_overlay.mousePressEvent(overlay_event)
            else:
                # 將主視窗座標轉換為水族箱部件相對座標
                aquarium_local_pos = pos - self.aquarium_rect.topLeft()
                aquarium_event = QMouseEvent(
                    event.type(),
                    QPointF(aquarium_local_pos),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
                self.aquarium.mousePressEvent(aquarium_event)
        elif self.panel_rect.contains(pos):
            local_pos = pos - self.panel_rect.topLeft()
            panel_event = QMouseEvent(
                QEvent.Type.MouseButtonPress,
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self.panel.mousePressEvent(panel_event)
        else:
            event.ignore()

    def _panel_event(self, event: QMouseEvent) -> QMouseEvent:
        """將視窗座標的滑鼠事件轉成面板相對座標的事件"""
        pos = event.position().toPoint()
        local_pos = pos - self.panel_rect.topLeft()
        return QMouseEvent(
            event.type(),
            QPointF(local_pos),
            event.globalPosition(),
            event.button(),
            event.buttons(),
            event.modifiers(),
        )

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        
        # 優先處理控制按鈕區域的移動
        if hasattr(self, '_kill_button') and self._kill_button.geometry().contains(pos):
            # 將事件傳遞給擊殺按鈕（用於 hover 效果）
            local_pos = pos - self._kill_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._kill_button.mouseMoveEvent(button_event)
            return
        
        if hasattr(self, '_hide_button') and self._hide_button.geometry().contains(pos):
            # 將事件傳遞給隱藏按鈕（用於 hover 效果）
            local_pos = pos - self._hide_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._hide_button.mouseMoveEvent(button_event)
            return
        
        if hasattr(self, '_anchor_button') and self._anchor_button.geometry().contains(pos):
            # 將事件傳遞給按鈕（用於 hover 效果）
            local_pos = pos - self._anchor_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._anchor_button.mouseMoveEvent(button_event)
            return
        
        # 優先處理水族箱區域和左側空白區域的移動
        if self.aquarium_rect.contains(pos):
            # 檢查是否在投食機部件的圖片區域內（如果可見且重疊）
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 在水族箱區域，且不在投食機圖片上
                if self._shop_overlay.isVisible():
                    overlay_event = QMouseEvent(
                        event.type(),
                        QPointF(pos - self._shop_overlay.geometry().topLeft()),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self._shop_overlay.mouseMoveEvent(overlay_event)
                else:
                    # 將主視窗座標轉換為水族箱部件相對座標
                    aquarium_local_pos = pos - self.aquarium_rect.topLeft()
                    aquarium_event = QMouseEvent(
                        event.type(),
                        QPointF(aquarium_local_pos),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self.aquarium.mouseMoveEvent(aquarium_event)
                return
        elif self.feed_machine_area_rect.contains(pos):
            # 在左側空白區域
            # 檢查是否在投食機部件的圖片區域內
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 在左側空白區域，且不在投食機圖片上，映射到水族箱左側
                aquarium_local_x = pos.x()
                aquarium_local_y = pos.y()
                aquarium_local_pos = QPoint(aquarium_local_x, aquarium_local_y)
                aquarium_event = QMouseEvent(
                    event.type(),
                    QPointF(aquarium_local_pos),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
                self.aquarium.mouseMoveEvent(aquarium_event)
                return
        
        if self._shop_overlay.isVisible() and self.aquarium_rect.contains(pos):
            overlay_event = QMouseEvent(
                event.type(),
                QPointF(pos - self._shop_overlay.geometry().topLeft()),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._shop_overlay.mouseMoveEvent(overlay_event)
        elif self.aquarium_rect.contains(pos):
            # 將滑鼠移動事件傳遞給水族箱部件（用於檢測金錢物件）
            # 將主視窗座標轉換為水族箱部件相對座標
            aquarium_local_pos = pos - self.aquarium_rect.topLeft()
            aquarium_event = QMouseEvent(
                event.type(),
                QPointF(aquarium_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self.aquarium.mouseMoveEvent(aquarium_event)
        elif self.feed_machine_area_rect.contains(pos):
            # 左側空白區域的滑鼠移動：轉換座標後傳遞給水族箱（用於檢測金錢物件）
            # 將左側空白區域的 x 座標映射到水族箱的左側區域（x=0 到 x=FEED_MACHINE_AREA_WIDTH）
            aquarium_local_x = pos.x()  # 左側空白區域的 x 直接映射到水族箱的 x（0 到 FEED_MACHINE_AREA_WIDTH）
            aquarium_local_y = pos.y()
            aquarium_local_pos = QPoint(aquarium_local_x, aquarium_local_y)
            aquarium_event = QMouseEvent(
                event.type(),
                QPointF(aquarium_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self.aquarium.mouseMoveEvent(aquarium_event)
        elif self.panel_rect.contains(pos):
            self.panel.mouseMoveEvent(self._panel_event(event))
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = event.position().toPoint()
        
        # 優先處理控制按鈕區域的釋放
        if hasattr(self, '_kill_button') and self._kill_button.geometry().contains(pos):
            # 將事件傳遞給擊殺按鈕
            local_pos = pos - self._kill_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._kill_button.mouseReleaseEvent(button_event)
            return
        
        if hasattr(self, '_hide_button') and self._hide_button.geometry().contains(pos):
            # 將事件傳遞給隱藏按鈕
            local_pos = pos - self._hide_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._hide_button.mouseReleaseEvent(button_event)
            return
        
        if hasattr(self, '_anchor_button') and self._anchor_button.geometry().contains(pos):
            # 將事件傳遞給按鈕
            local_pos = pos - self._anchor_button.geometry().topLeft()
            button_event = QMouseEvent(
                event.type(),
                QPointF(local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._anchor_button.mouseReleaseEvent(button_event)
            return
        
        # 優先處理水族箱區域和左側空白區域的釋放
        if self.aquarium_rect.contains(pos):
            # 檢查是否在投食機部件的圖片區域內（如果可見且重疊）
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 在水族箱區域，且不在投食機圖片上
                if self._shop_overlay.isVisible():
                    overlay_event = QMouseEvent(
                        event.type(),
                        QPointF(pos - self._shop_overlay.geometry().topLeft()),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self._shop_overlay.mouseReleaseEvent(overlay_event)
                else:
                    # 將主視窗座標轉換為水族箱部件相對座標
                    aquarium_local_pos = pos - self.aquarium_rect.topLeft()
                    aquarium_event = QMouseEvent(
                        event.type(),
                        QPointF(aquarium_local_pos),
                        event.globalPosition(),
                        event.button(),
                        event.buttons(),
                        event.modifiers(),
                    )
                    self.aquarium.mouseReleaseEvent(aquarium_event)
                return
        elif self.feed_machine_area_rect.contains(pos):
            # 在左側空白區域
            # 檢查是否在投食機部件的圖片區域內
            is_on_feed_machine_image = False
            if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
                feed_machine_geometry = self._feed_machine_widget.geometry()
                if feed_machine_geometry.contains(pos):
                    local_pos = pos - feed_machine_geometry.topLeft()
                    image_rect = self._feed_machine_widget._get_feed_machine_image_rect()
                    if image_rect and image_rect.contains(local_pos):
                        is_on_feed_machine_image = True
            
            if not is_on_feed_machine_image:
                # 在左側空白區域，且不在投食機圖片上，映射到水族箱左側
                aquarium_local_x = pos.x()
                aquarium_local_y = pos.y()
                aquarium_local_pos = QPoint(aquarium_local_x, aquarium_local_y)
                aquarium_event = QMouseEvent(
                    event.type(),
                    QPointF(aquarium_local_pos),
                    event.globalPosition(),
                    event.button(),
                    event.buttons(),
                    event.modifiers(),
                )
                self.aquarium.mouseReleaseEvent(aquarium_event)
                return
        
        if self._shop_overlay.isVisible() and self.aquarium_rect.contains(pos):
            overlay_event = QMouseEvent(
                event.type(),
                QPointF(pos - self._shop_overlay.geometry().topLeft()),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self._shop_overlay.mouseReleaseEvent(overlay_event)
        elif self.aquarium_rect.contains(pos):
            # 將主視窗座標轉換為水族箱部件相對座標
            aquarium_local_pos = pos - self.aquarium_rect.topLeft()
            aquarium_event = QMouseEvent(
                event.type(),
                QPointF(aquarium_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self.aquarium.mouseReleaseEvent(aquarium_event)
        elif self.panel_rect.contains(pos):
            self.panel.mouseReleaseEvent(self._panel_event(event))
        elif self.feed_machine_area_rect.contains(pos):
            # 左側空白區域的點擊釋放：轉換座標後傳遞給水族箱
            # 將左側空白區域的 x 座標映射到水族箱的左側區域（x=0 到 x=FEED_MACHINE_AREA_WIDTH）
            aquarium_local_x = pos.x()  # 左側空白區域的 x 直接映射到水族箱的 x（0 到 FEED_MACHINE_AREA_WIDTH）
            aquarium_local_y = pos.y()
            aquarium_local_pos = QPoint(aquarium_local_x, aquarium_local_y)
            aquarium_event = QMouseEvent(
                event.type(),
                QPointF(aquarium_local_pos),
                event.globalPosition(),
                event.button(),
                event.buttons(),
                event.modifiers(),
            )
            self.aquarium.mouseReleaseEvent(aquarium_event)
        else:
            super().mouseReleaseEvent(event)

    def on_shop_requested(self) -> None:
        """開啟商店時更新商品顯示"""
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )
        self._shop_overlay.show()
        self._shop_overlay.raise_()

    def _on_shop_closed(self) -> None:
        """商店覆蓋關閉後可做後續處理（目前僅隱藏）"""
        pass
    
    def _on_pet_purchase_requested(self, pet_name: str) -> None:
        """處理寵物購買請求（含金幣解鎖與魚種解鎖）"""
        if pet_name in self._pets:
            print(f"[寵物] {pet_name} 已存在，無法重複召喚")
            return
        if pet_name not in PET_CONFIG:
            print(f"[寵物] {pet_name} 配置不存在")
            return
        
        pet_config = PET_CONFIG[pet_name]
        
        # 金幣解鎖
        if "unlock_money" in pet_config:
            unlock_money = pet_config["unlock_money"]
            if pet_name not in self._unlocked_pets:
                if self.total_money < unlock_money:
                    print(f"[寵物] {pet_name} 未解鎖（需要 {unlock_money} 金幣）")
                    return
                self.total_money -= unlock_money
                self._unlocked_pets.append(pet_name)
                self.panel.set_money(self.total_money)
            self._spawn_pet(pet_name)
            self._auto_save()
            self._shop_overlay.update_items(
                self._unlocked_species, self._pets,
                self.total_money, self._unlocked_pets,
                self._pet_levels,
                self._get_fish_count_by_species(),
                self._unlocked_feeds,
                self._feed_cheap_count,
                self._unlocked_tools,
                self._tool_colors,
            )
            return
        
        # 魚種解鎖（與飼料投食機一致：effective_count = max(total_count_reached, max_count_reached)）
        unlock_species = pet_config.get("unlock_species")
        unlock_count = pet_config.get("unlock_count", 0)
        if "_" in unlock_species:
            stage, species = unlock_species.split("_", 1)
            key = f"{stage}_{species}"
        else:
            species = unlock_species
            key = species
        if key not in self._unlocked_species:
            print(f"[寵物] {pet_name} 未解鎖（{unlock_species} 未達到 {unlock_count} 隻）")
            return
        total_count = self._unlocked_species[key].get("total_count_reached", 0)
        max_count = self._unlocked_species[key].get("max_count_reached", 0)
        effective_count = max(total_count, max_count)
        if effective_count < unlock_count:
            print(f"[寵物] {pet_name} 未解鎖（{unlock_species} 有效數量 {effective_count}，需要 {unlock_count} 隻）")
            return
        self._spawn_pet(pet_name)
        self._auto_save()
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )

    def _on_pet_duplicate_requested(self, pet_name: str) -> None:
        """拼布魚吃核廢料 20% 複製時，再召喚一隻該寵物。"""
        if pet_name in self._pets:
            return
        self._spawn_pet(pet_name)
        self._auto_save()

    def _on_game_time_updated(self, game_time_sec: float) -> None:
        """每幀更新：飼料數量計數器定時 +1（僅已解鎖飼料），並檢查解鎖條件。"""
        changed = False
        for feed_name, cfg in FEED_UNLOCK_CONFIG.items():
            if feed_name == "便宜飼料":
                continue
            if feed_name not in self._unlocked_feeds:
                continue
            interval = get_feed_counter_interval_sec(feed_name)
            if interval is None:
                continue
            # 確保計時器已初始化
            if feed_name not in self._feed_counter_last_add:
                self._feed_counter_last_add[feed_name] = game_time_sec
                continue
            last = self._feed_counter_last_add.get(feed_name, game_time_sec)
            if game_time_sec - last >= interval:
                self._feed_counters[feed_name] = self._feed_counters.get(feed_name, 0) + 1
                self._feed_counter_last_add[feed_name] = game_time_sec
                changed = True
        if changed:
            self._update_feed_unlocks()
            if hasattr(self.panel, "update_feed_menu"):
                self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)
        
        # 更新投食機的已解鎖飼料列表（每次更新，確保同步）
        if hasattr(self, '_feed_machine_widget'):
            self._feed_machine_widget.set_unlocked_feeds(self._unlocked_feeds, self._feed_counters)
        
        # 投食機自動投食（依配置間隔投放5~10顆）
        if hasattr(self, '_feed_machine_widget') and self._feed_machine_widget.isVisible():
            selected_feed = self._feed_machine_widget.get_selected_feed()
            if selected_feed:
                feed_name, feed_path = selected_feed
                # 檢查飼料是否可用
                if feed_name in self._unlocked_feeds:
                    if feed_name == "便宜飼料" or self._feed_counters.get(feed_name, 0) > 0:
                        # 更新計時器（約60 FPS，每幀 1/60 秒）
                        self._feed_machine_timer += 1.0 / 60.0
                        if self._feed_machine_timer >= self._feed_machine_interval:
                            # 投放飼料（5~10顆）
                            feed_count = random.randint(5, 10)
                            # 檢查實際可用的飼料數量
                            can_feed = True
                            if feed_name == "便宜飼料":
                                # 便宜飼料：檢查是否有足夠的錢
                                feed_cost = FEED_COST.get(feed_name, 0)
                                if feed_cost > 0:
                                    total_cost = feed_cost * feed_count
                                    if self.total_money < total_cost:
                                        # 金錢不足，計算能負擔的數量
                                        affordable_count = self.total_money // feed_cost
                                        if affordable_count <= 0:
                                            # 完全無法負擔，跳過本次投餵
                                            can_feed = False
                                        else:
                                            feed_count = affordable_count
                            else:
                                # 其他飼料：檢查實際擁有的數量
                                available_count = self._feed_counters.get(feed_name, 0)
                                if available_count <= 0:
                                    # 沒有飼料，跳過本次投餵
                                    can_feed = False
                                elif feed_count > available_count:
                                    # 隨機數量超過實際數量，只拋出實際擁有的數量
                                    feed_count = available_count
                            if can_feed:
                                self._feed_machine_shoot_feeds(feed_name, feed_path, feed_count)
                            self._feed_machine_timer = 0.0
        
        # 檢查是否需要贈送100$（沒有魚且總金額歸0）
        fish_count = len(self.aquarium.fishes)
        current_condition_met = (fish_count == 0 and self.total_money == 0)
        
        # 只有當狀態從"不滿足條件"變成"滿足條件"時才觸發
        if current_condition_met and not self._last_bonus_condition_met:
            self._show_bonus_dialog()
        
        # 更新上一次的狀態
        self._last_bonus_condition_met = current_condition_met

    def _show_bonus_dialog(self) -> None:
        """顯示贈送100$的確認對話框"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("贈送")
        msg_box.setWindowIcon(_get_app_icon())
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText("送你100$~")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("謝謝")
        msg_box.exec()
        
        # 贈送100$
        self.total_money += 100
        self.panel.set_money(self.total_money)
        self._auto_save()

    def _update_feed_unlocks(self) -> None:
        """依 FEED_UNLOCK_CONFIG 與當前狀態更新 _unlocked_feeds（鯉魚飼料、藥丸；核廢料由商店解鎖按鈕）。"""
        for feed_name, cfg in FEED_UNLOCK_CONFIG.items():
            if feed_name in self._unlocked_feeds:
                continue
            unlock_by = cfg.get("unlock_by")
            if unlock_by == "always":
                self._unlocked_feeds.append(feed_name)
                continue
            if unlock_by == "feed_cheap_count":
                if self._feed_cheap_count >= cfg.get("unlock_value", 100):
                    self._unlocked_feeds.append(feed_name)
                    if feed_name not in self._feed_counters:
                        self._feed_counters[feed_name] = 0
                    if feed_name not in self._feed_counter_last_add:
                        self._feed_counter_last_add[feed_name] = self.aquarium._game_time_sec
            elif unlock_by == "large_betta_count":
                key = "large_鬥魚"
                max_count = self._unlocked_species.get(key, {}).get("max_count_reached", 0)
                if max_count >= cfg.get("unlock_value", 10):
                    self._unlocked_feeds.append(feed_name)
                    if feed_name not in self._feed_counters:
                        self._feed_counters[feed_name] = 0
                    if feed_name not in self._feed_counter_last_add:
                        self._feed_counter_last_add[feed_name] = self.aquarium._game_time_sec
            elif unlock_by == "chest_feed_count":
                if self._feed_counters.get(feed_name, 0) > 0:
                    self._unlocked_feeds.append(feed_name)

    def _on_pet_upgrade_requested(self, pet_name: str) -> None:
        """處理寵物升級請求：扣款、更新等級、套用效果、刷新商店"""
        if pet_name not in self._pets:
            return
        upgrade_cfg = PET_UPGRADE_CONFIG.get(pet_name, {})
        if not upgrade_cfg:
            return
        current = self._pet_levels.get(pet_name, 0)
        next_level = current + 1
        if next_level > upgrade_cfg.get("max_level", 2):
            return
        costs = upgrade_cfg.get("upgrade_costs", [])
        if current >= len(costs):
            return
        cost = costs[current]
        if self.total_money < cost:
            return
        self.total_money -= cost
        self.panel.set_money(self.total_money)
        self._pet_levels[pet_name] = next_level
        pet = self._pets[pet_name]
        if pet_name == "龍蝦":
            speeds = PET_CONFIG.get("龍蝦", {}).get("speed_by_level", [0.4, 0.5, 0.6])
            pet.speed = speeds[min(next_level, len(speeds) - 1)]
        elif pet_name == "寶箱怪":
            pet.set_level(next_level)
        elif pet_name == "拼布魚":
            pet.set_level(next_level)
        self._auto_save()
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )
        
    def _on_feed_unlock_requested(self, feed_name: str) -> None:
        """飼料解鎖請求：核廢料需犧牲 6 隻中鬥魚，解鎖時將場上 6 隻中鬥魚改為死亡效果並加入核廢料至已解鎖。"""
        if feed_name != "核廢料":
            return
        cfg = FEED_UNLOCK_CONFIG.get(feed_name, {})
        if cfg.get("unlock_by") != "sacrifice_medium_betta":
            return
        need_count = cfg.get("unlock_value", 6)
        to_remove = []
        for fish in self.aquarium.fishes:
            if len(to_remove) >= need_count:
                break
            if getattr(fish, "is_dead", False):
                continue
            if fish.species == "鬥魚" and fish.stage == "medium":
                to_remove.append(fish)
        if len(to_remove) < need_count:
            print(f"[飼料解鎖] 核廢料需要 {need_count} 隻中鬥魚，目前僅 {len(to_remove)} 隻")
            return
        for fish in to_remove:
            fish.set_dead()
        self._unlocked_feeds.append(feed_name)
        if feed_name not in self._feed_counters:
            self._feed_counters[feed_name] = 0
        self._feed_counter_last_add[feed_name] = self.aquarium._game_time_sec
        self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )
        self._auto_save()

    def _on_fish_purchase_requested(self, species_name: str) -> None:
        """處理商店魚種購買請求：檢查解鎖與購買條件，扣除金幣或犧牲魚後在水族箱新增該魚種。"""
        if species_name not in FISH_SHOP_CONFIG:
            return
        cfg = FISH_SHOP_CONFIG[species_name]
        resource_dir = _resource_dir()
        fish_dir = resource_dir / "fish" / species_name
        if not fish_dir.is_dir():
            print(f"[商店魚種] {species_name} 資源目錄不存在: {fish_dir}")
            return
        # 解鎖檢查
        is_unlocked = False
        if "unlock_money" in cfg:
            is_unlocked = cfg.get("unlock_money", 0) == 0
        else:
            unlock_species = cfg.get("unlock_species", "")
            unlock_count = cfg.get("unlock_count", 0)
            key = unlock_species if "_" in unlock_species else unlock_species
            if key in self._unlocked_species:
                max_count = self._unlocked_species[key].get("max_count_reached", 0)
                is_unlocked = max_count >= unlock_count
        if not is_unlocked:
            print(f"[商店魚種] {species_name} 未解鎖")
            return
        # 購買條件：犧牲魚 或 金幣
        require_species = cfg.get("require_species")
        require_count = cfg.get("require_count", 0)
        purchase_money = cfg.get("purchase_money", 0)
        if require_species and require_count > 0:
            req_key = require_species
            fish_counts = self._get_fish_count_by_species()
            current = fish_counts.get(req_key, 0)
            if current < require_count:
                print(f"[商店魚種] {species_name} 需要 {require_count} 隻 {require_species}，目前 {current} 隻")
                return
            # 犧牲魚改為死亡效果（不立即移除，由 update_fishes 在動畫結束後移除）
            to_remove = []
            for fish in self.aquarium.fishes:
                if len(to_remove) >= require_count:
                    break
                if getattr(fish, "is_dead", False):
                    continue
                key = f"{fish.stage}_{fish.species}" if fish.stage else fish.species
                if key == req_key:
                    to_remove.append(fish)
            for fish in to_remove:
                fish.set_dead()
        if purchase_money > 0:
            if self.total_money < purchase_money:
                print(f"[商店魚種] {species_name} 需要 {purchase_money} 金幣")
                return
            self.total_money -= purchase_money
            self.panel.set_money(self.total_money)
        self.on_fish_add_requested(fish_dir)
        self._auto_save()
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )

    def _spawn_pet(self, pet_name: str) -> None:
        """召喚寵物到水族箱"""
        resource_dir = _resource_dir()
        pet_dir = resource_dir / "pet" / pet_name
        if not pet_dir.exists():
            print(f"[寵物] {pet_name} 資源目錄不存在: {pet_dir}")
            return
        
        pet_config = PET_CONFIG.get(pet_name, {})
        swim_behavior = pet_config.get("swim_behavior", "1_游動")
        turn_behavior = pet_config.get("turn_behavior", "2_轉向")
        swim_frames = load_pet_animation(pet_dir, swim_behavior)
        turn_frames = load_pet_animation(pet_dir, turn_behavior) if turn_behavior else swim_frames
        if not swim_frames:
            print(f"[寵物] {pet_name} 無法載入動畫: {swim_behavior}")
            return
        if not turn_frames:
            turn_frames = swim_frames
        
        aquarium_rect = self.aquarium_rect
        pet_scale = pet_config.get("scale", 0.6)
        level = self._pet_levels.get(pet_name, 0)
        pet_speed = pet_config.get("speed", DEFAULT_PET_SPEED)
        if pet_name == "龍蝦":
            speed_by_level = pet_config.get("speed_by_level", [pet_speed])
            pet_speed = speed_by_level[min(level, len(speed_by_level) - 1)]
        
        if pet_name == "龍蝦":
            x = aquarium_rect.center().x()
            y = aquarium_rect.bottom() - 40
            position = QPoint(x, y)
            pet = LobsterPet(
                swim_frames=swim_frames,
                turn_frames=turn_frames,
                position=position,
                speed=pet_speed,
                scale=pet_scale,
            )
        elif pet_name == "寶箱怪":
            position = QPoint(400, 300)
            pet = ChestMonsterPet(
                swim_frames=swim_frames,
                turn_frames=turn_frames,
                position=position,
                spawn_money_cb=lambda name: self._do_chest_spawn_money(name),
                scale=pet_scale,
                pet_name=pet_name,
                chest_level=level,
            )
        elif pet_name == "拼布魚":
            x = random.randint(aquarium_rect.left() + 60, aquarium_rect.right() - 60)
            y = random.randint(aquarium_rect.top() + 60, aquarium_rect.bottom() - 60)
            position = QPoint(x, y)
            eat_frames = load_pet_animation(pet_dir, "6_吃飽吃") or swim_frames
            # 使用config中的拼布魚速度，而非PET_CONFIG中的speed
            from config import PATCHWORK_FISH_SPEED
            patchwork_speed = PATCHWORK_FISH_SPEED
            pet = PatchworkFishPet(
                swim_frames=swim_frames,
                turn_frames=turn_frames,
                position=position,
                speed=patchwork_speed,
                scale=pet_scale,
                pet_name=pet_name,
                eat_frames=eat_frames,
            )
            pet.set_level(level)
            # 設置街頭表演開始回調（用於觸發全場快樂buff）
            pet.on_performance_start_callback = lambda: self._on_patchwork_performance_start()
        else:
            x = random.randint(aquarium_rect.left() + 60, aquarium_rect.right() - 60)
            y = random.randint(aquarium_rect.top() + 60, aquarium_rect.bottom() - 60)
            position = QPoint(x, y)
            pet = Pet(
                swim_frames=swim_frames,
                turn_frames=turn_frames,
                position=position,
                speed=pet_speed,
                scale=pet_scale,
                pet_name=pet_name,
            )
        self.aquarium.add_pet(pet)
        self._pets[pet_name] = pet
        print(f"[寵物] 成功召喚 {pet_name}")

    def _do_chest_spawn_money(self, money_name: str) -> None:
        """寶箱怪產物：在水族箱加入金錢，拾取時重置寶箱怪計時"""
        pos = QPointF(400, 300)

        def on_collected() -> None:
            if "寶箱怪" in self._pets:
                self._pets["寶箱怪"].reset_after_collect()

        self.aquarium.add_money_with_callback(pos, money_name, on_collected)

    def _on_patchwork_performance_start(self) -> None:
        """拼布魚街頭表演模式開始（觸發全場快樂buff）"""
        # 這裡可以實現全場快樂buff邏輯（例如減少魚的大便間隔5%）
        # 目前先記錄log
        print(f"[拼布魚] 街頭表演模式已啟動，全場快樂buff生效")

    def on_background_selected(self, path: Optional[Path]) -> None:
        """使用者從清單選擇背景後切換水族箱背景"""
        self.aquarium.set_background(path)
        # 自動儲存
        self._auto_save()

    def on_background_opacity_changed(self, percent: int) -> None:
        """使用者調整背景透明度後更新水族箱背景透明度"""
        self.aquarium.set_background_opacity(percent)
        # 自動儲存
        self._auto_save()

    def on_feed_selected(self, feed_name: str, feed_path: Path) -> None:
        """使用者選擇飼料類型（可留給之後投放飼料時使用）"""
        self._current_feed = (feed_name, feed_path)
    
    def _on_feed_machine_feed_selected(self, feed_name: str, feed_path: Path) -> None:
        """投食機選擇飼料時更新顯示"""
        # 更新投食機部件的顯示
        self._feed_machine_widget.set_selected_feed(feed_name, feed_path)
        # 注意：選擇飼料時不扣減數量，只有在實際發射飼料時才扣減（在 _feed_machine_shoot_feeds 中處理）
    
    def _feed_machine_shoot_feeds(self, feed_name: str, feed_path: Path, count: int) -> None:
        """投食機發射飼料（拋物線軌跡）"""
        # 載入飼料動畫幀
        feed_frames = []
        if feed_name in CHEST_FEED_ITEMS:
            # 金條、鑽石：優先從 resource/feed/ 目錄載入動畫幀
            feed_dir = _resource_dir() / "feed" / feed_name
            if feed_dir.exists() and feed_dir.is_dir():
                frame_files = sorted(feed_dir.glob("*.png"))
                for frame_file in frame_files:
                    pixmap = QPixmap(str(frame_file))
                    if not pixmap.isNull():
                        feed_frames.append(pixmap)
            # 如果 resource/feed/ 目錄不存在，回退到單一圖片
            if not feed_frames and feed_path.exists():
                if feed_path.is_file():
                    pixmap = QPixmap(str(feed_path))
                    if not pixmap.isNull():
                        feed_frames.append(pixmap)
        elif feed_path.exists() and feed_path.is_dir():
            frame_files = sorted(feed_path.glob("*.png"))
            for frame_file in frame_files:
                pixmap = QPixmap(str(frame_file))
                if not pixmap.isNull():
                    feed_frames.append(pixmap)
        
        if not feed_frames:
            return
        
        # 計算投食機出口位置
        feed_machine_widget = self._feed_machine_widget
        feed_machine_geometry = feed_machine_widget.geometry()
        
        # 計算起始 x 位置
        if FEED_MACHINE_EXIT_X_RATIO is not None:
            # 使用配置的比例值（相對於水族箱寬度）
            aquarium_width = self.aquarium_rect.width()
            exit_x = self.aquarium_rect.left() + aquarium_width * FEED_MACHINE_EXIT_X_RATIO
        else:
            # 使用投食機位置自動計算（相對於投食機右側）
            exit_x_base = feed_machine_geometry.right() - self.aquarium_rect.left()  # 轉換為水族箱座標
            exit_x = exit_x_base + FEED_MACHINE_EXIT_X_OFFSET  # 應用 x 偏移配置
        
        # 計算起始 y 位置（投食機頂部稍微下方）
        exit_y = feed_machine_geometry.top() + 20
        
        # 限制在水族箱範圍內（但允許稍微超出邊界以支持更靈活的配置）
        exit_x = max(self.aquarium_rect.left() - 100, min(exit_x, self.aquarium_rect.right() + 100))
        exit_y = max(self.aquarium_rect.top() - 100, min(exit_y, self.aquarium_rect.bottom() - 100))
        
        # 轉換為水族箱本地座標（Feed 使用相對於 AquariumWidget 的座標）
        exit_x_local = exit_x - self.aquarium_rect.left()
        exit_y_local = exit_y - self.aquarium_rect.top()
        
        # 計算目標位置（使用配置的比例範圍，也是水族箱本地座標）
        aquarium_width = self.aquarium_rect.width()
        aquarium_height = self.aquarium_rect.height()
        target_x_min = aquarium_width * FEED_MACHINE_TARGET_X_MIN_RATIO
        target_x_max = aquarium_width * FEED_MACHINE_TARGET_X_MAX_RATIO
        margin = 50
        for _ in range(count):
            target_x = random.uniform(
                max(margin, target_x_min),
                min(aquarium_width - margin, target_x_max)
            )
            target_y = random.uniform(
                margin,
                aquarium_height - margin - 100  # 留出底部空間
            )
            
            # 創建拋物線飼料（使用水族箱本地座標）
            feed = Feed(
                position=QPoint(int(exit_x_local), int(exit_y_local)),
                feed_frames=feed_frames.copy(),
                feed_name=feed_name,
                scale=get_feed_scale(feed_name),
                target_position=QPointF(target_x, target_y),  # 目標位置也是水族箱本地座標
                is_parabolic=True
            )
            self.aquarium.add_feed(feed)
        
        # 扣除飼料數量或費用（如果不是便宜飼料則扣數量，如果是便宜飼料則扣費用）
        if feed_name == "便宜飼料":
            feed_cost = FEED_COST.get(feed_name, 0)
            if feed_cost > 0:
                total_cost = feed_cost * count
                self.total_money -= total_cost
                self.panel.set_money(self.total_money)
        else:
            self._feed_counters[feed_name] = max(0, self._feed_counters.get(feed_name, 0) - count)
            self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)

    def on_fish_add_requested(self, fish_dir: Path) -> None:
        """使用者從清單選擇魚種後，在水族箱內新增一條該魚"""
        self.add_one_fish(fish_dir)

    def add_one_fish(self, fish_dir: Path) -> None:
        """
        在水族箱內新增一條魚（依 fish_dir 載入游泳/轉向，隨機位置與速度）
        
        注意：puppy 魚種只能新增 small 階段，其他階段需透過餵飼料升級獲得
        fish_dir 可為魚種目錄 resource/fish/{species}/ 或階段目錄 resource/fish/{species}/{stage}/
        """
        if not fish_dir.exists() or not fish_dir.is_dir():
            return
        
        parts = fish_dir.parts
        stage_raw = None
        species = None
        try:
            fish_index = parts.index("fish")
            if fish_index + 2 < len(parts):
                # 已是階段目錄：resource/fish/{species}/{stage}/
                species = parts[fish_index + 1]
                stage_raw = parts[fish_index + 2]
            else:
                # 僅魚種目錄：resource/fish/{species}/ → 解析出 small 變體，或直接使用魚種目錄（如孔雀魚、鯊魚）
                species = parts[fish_index + 1]
                for sub in sorted(fish_dir.iterdir()):
                    if sub.is_dir():
                        # 支援英文 "small" 或中文「幼」作為 small 階段的標識
                        sub_name_lower = sub.name.lower()
                        if "small" in sub_name_lower or "幼" in sub.name:
                            fish_dir = sub
                            stage_raw = sub.name
                            break
                else:
                    # 找不到含 small 或「幼」的子目錄時，使用魚種目錄本身（動畫在魚種目錄下，如孔雀魚、鯊魚）
                    stage_raw = "small"
        except (ValueError, IndexError):
            species = None
            stage_raw = None
        
        # 從階段名稱提取純階段（small/medium/large）
        # 支援英文階段名稱和中文階段名稱映射
        stage = "small"
        if stage_raw:
            # 中文階段名稱映射
            chinese_stage_map = {
                "幼": "small",
                "中": "medium",
                "成年": "large",
                "天使": "angel",
            }
            
            # 先檢查中文階段名稱
            matched = False
            for chinese_key, english_stage in chinese_stage_map.items():
                if chinese_key in stage_raw:
                    stage = english_stage
                    matched = True
                    break
            
            # 如果沒有匹配中文，再檢查英文階段名稱
            if not matched:
                for valid_stage in ["small", "medium", "large", "angel"]:
                    if stage_raw.lower().startswith(valid_stage):
                        stage = valid_stage
                        break
                else:
                    stage = stage_raw
        
        print(f"[新增魚] 路徑: {fish_dir}, 提取的魚種: {species}, 原始階段: {stage_raw}, 處理後階段: {stage}")
        
        # 確保 puppy 和鬥魚魚種只能新增 small 階段
        if species in ("puppy", "鬥魚") and stage != "small":
            print(f"[新增魚] 拒絕新增非 small 階段的 {species} (階段: {stage})")
            return  # 拒絕新增非 small 階段的 puppy/鬥魚
        
        # 投放幼鬥魚需要花費 20 元
        if species == "鬥魚" and stage == "small":
            if self.total_money < SMALL_BETTA_COST:
                print(f"[新增魚] 金幣不足，無法投放幼鬥魚（需要 {SMALL_BETTA_COST} 元，目前 {self.total_money} 元）")
                return
            # 扣除金幣
            self.total_money -= SMALL_BETTA_COST
            self.panel.set_money(self.total_money)
            print(f"[新增魚] 扣除 {SMALL_BETTA_COST} 元投放幼鬥魚，剩餘 {self.total_money} 元")
        
        # 游泳、轉向、吃飯行為與鬥魚、鯊魚相同（5_吃飽游泳、7_吃飽轉向、6_吃飽吃），由 config.get_fish_behaviors 取得
        swim_behavior, turn_behavior, eat_behavior = get_fish_behaviors(species or "")
        swim_frames, turn_frames = load_swim_and_turn(
            fish_dir,
            swim_behavior=swim_behavior,
            turn_behavior=turn_behavior,
        )
        if not swim_frames:
            return
        eat_frames = load_fish_animation(fish_dir, behavior=eat_behavior)
        aquarium_rect = self.aquarium_rect
        fish_scale = get_fish_scale(species or "", stage)
        x = random.randint(
            aquarium_rect.left() + 60,
            aquarium_rect.right() - 60,
        )
        y = random.randint(
            aquarium_rect.top() + 60,
            aquarium_rect.bottom() - 60,
        )
        direction = random.uniform(0, 360)
        speed_min, speed_max = get_fish_speed_range(species or "")
        speed = random.uniform(speed_min, speed_max)
        swim_copy = [QPixmap(p) for p in swim_frames]
        turn_copy = [QPixmap(p) for p in turn_frames] if turn_frames else swim_copy[:]
        eat_copy = [QPixmap(p) for p in eat_frames] if eat_frames else []
        fish = Fish(
            swim_frames=swim_copy,
            turn_frames=turn_copy,
            position=QPoint(x, y),
            speed=speed,
            direction=direction,
            scale=fish_scale,
            eat_frames=eat_copy if eat_copy else None,
            species=species,  # 設置魚種
            stage=stage,       # 設置階段
        )
        self.aquarium.add_fish(fish)
        
        # 更新解鎖狀態並自動儲存
        counts = self._get_fish_count_by_species()
        if species:
            # 更新基本魚種解鎖狀態
            self._update_unlock_status(species, counts.get(species, 0))
            # 更新階段_魚種格式解鎖狀態（用於寵物解鎖）
            if stage:
                stage_key = f"{stage}_{species}"
                self._update_unlock_status(stage_key, counts.get(stage_key, 0))
        self._auto_save()

    def on_money_hovered(self, value: int) -> None:
        """處理滑鼠移動到金錢物件上時自動拾取"""
        # 金錢已經在AquariumWidget的mouseMoveEvent中被標記為已拾取
        # 這裡只需要更新金額顯示
        self.total_money += value
        self.panel.set_money(self.total_money)
        # 自動儲存
        self._auto_save()
    
    def on_aquarium_clicked(self, pos: QPoint) -> None:
        """處理水族箱區域內的點擊事件：先檢查擊殺模式，再檢查是否點到寶箱怪產物，再檢查金錢，否則投放飼料"""
        # 如果擊殺模式開啟，只檢查是否點到魚，不執行其他操作（包括餵食）
        if self._kill_mode_enabled:
            for fish in self.aquarium.fishes:
                if getattr(fish, "is_dead", False):
                    continue  # 跳過已經死亡的魚
                display_rect = fish.get_display_rect()
                if display_rect and display_rect.contains(pos):
                    # 點擊到魚，觸發死亡動畫
                    fish.set_dead()
                    print(f"[擊殺] 擊殺了 {fish.species} (階段: {fish.stage})")
                # 擊殺模式開啟時，無論是否點到魚，都不執行後續操作（包括餵食）
            return
        
        # 先檢查是否點到寶箱怪產物並拾取
        chest_result = self.aquarium.try_collect_chest_produce_at(pos)
        if chest_result is not None:
            produce_type, value = chest_result
            if produce_type in CHEST_FEED_ITEMS:
                # 金條、鑽石：不增加總金額，改為加入飼料清單數量
                self._feed_counters[produce_type] = self._feed_counters.get(produce_type, 0) + 1
                if produce_type not in self._unlocked_feeds:
                    self._unlocked_feeds.append(produce_type)
                self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)
                # 同步到投食機，切換飼料對話框才會顯示金條/鑽石
                self._feed_machine_widget.set_unlocked_feeds(self._unlocked_feeds, self._feed_counters)
                print(f"[拾取] 拾取寶箱怪產物 {produce_type}，加入飼料清單，數量: {self._feed_counters[produce_type]}")
            else:
                self.total_money += value
                self.panel.set_money(self.total_money)
                print(f"[拾取] 拾取寶箱怪產物，獲得 {value} 金幣，總金額: {self.total_money}")
            # 自動儲存
            self._auto_save()
            return
        # 再檢查是否點到金錢並拾取
        collected = self.aquarium.try_collect_money_at(pos)
        if collected is not None:
            self.total_money += collected
            self.panel.set_money(self.total_money)
            # 自動儲存
            self._auto_save()
            return
        # 投放飼料（僅已解鎖飼料可投；便宜飼料無限，其餘依專屬計數器扣減）
        # 限制投放區域在魚可游動範圍內（與魚的 boundary_margin 一致，為 50 像素）
        # 注意：pos 是水族箱本地座標（從 0 開始），所以 swim_area 也要用本地座標
        margin = 50
        swim_area = QRect(
            margin,  # 水族箱本地座標，從 0 開始
            margin,
            self.aquarium_rect.width() - 2 * margin,
            self.aquarium_rect.height() - 2 * margin,
        )
        if not swim_area.contains(pos):
            return
        if self._current_feed:
            feed_name, feed_path = self._current_feed
            if feed_name not in self._unlocked_feeds:
                return
            if feed_name != "便宜飼料" and feed_name not in CHEST_FEED_ITEMS and self._feed_counters.get(feed_name, 0) <= 0:
                return
            if feed_name in CHEST_FEED_ITEMS and self._feed_counters.get(feed_name, 0) <= 0:
                return
            feed_frames = []
            if feed_name in CHEST_FEED_ITEMS:
                # 金條、鑽石：從 resource/feed/ 目錄載入動畫幀
                feed_dir = _resource_dir() / "feed" / feed_name
                if feed_dir.exists() and feed_dir.is_dir():
                    frame_files = sorted(feed_dir.glob("*.png"))
                    for frame_file in frame_files:
                        pixmap = QPixmap(str(frame_file))
                        if not pixmap.isNull():
                            feed_frames.append(pixmap)
                # 如果 resource/feed/ 目錄不存在，回退到單一圖片
                if not feed_frames:
                    chest_path = _get_chest_feed_image_path(feed_name)
                    if chest_path.exists():
                        pixmap = QPixmap(str(chest_path))
                        if not pixmap.isNull():
                            feed_frames.append(pixmap)
            elif feed_path.exists() and feed_path.is_dir():
                frame_files = sorted(feed_path.glob("*.png"))
                for frame_file in frame_files:
                    pixmap = QPixmap(str(frame_file))
                    if not pixmap.isNull():
                        feed_frames.append(pixmap)
            if feed_frames:
                # 檢查便宜飼料是否需要扣錢（在創建飼料之前檢查）
                if feed_name == "便宜飼料":
                    feed_cost = FEED_COST.get(feed_name, 0)
                    if feed_cost > 0:
                        if self.total_money < feed_cost:
                            # 金錢不足，不投餵
                            return
                        self.total_money -= feed_cost
                        self.panel.set_money(self.total_money)
                
                feed = Feed(
                    position=pos,
                    feed_frames=feed_frames,
                    feed_name=feed_name,
                    scale=get_feed_scale(feed_name),
                )
                self.aquarium.add_feed(feed)
                
                if feed_name == "便宜飼料":
                    self._feed_cheap_count += 1
                else:
                    self._feed_counters[feed_name] = max(0, self._feed_counters.get(feed_name, 0) - 1)
                self._update_feed_unlocks()
                self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)
                self._auto_save()

    def closeEvent(self, event) -> None:
        """
        處理視窗關閉事件，確保儲存遊戲狀態
        """
        self._save_game_state()
        event.accept()
        QApplication.instance().quit()
    
    def close_window(self) -> None:
        """
        關閉視窗並退出應用程式
        """
        self.close()
    
    def _get_fish_count_by_species(self) -> dict:
        """
        統計各魚種當前數量（包括階段_魚種格式）。僅計入存活魚（未 is_dead），
        用於解鎖判定與商店購買條件（如孔雀魚需犧牲場上 1 隻天使鬥魚）。
        
        Returns:
            字典：{species: count, "stage_species": count}
        """
        counts = {}
        for fish in self.aquarium.fishes:
            if getattr(fish, "is_dead", False):
                continue
            if fish.species:
                # 基本魚種計數
                counts[fish.species] = counts.get(fish.species, 0) + 1
                # 階段_魚種格式計數（用於寵物解鎖）
                if fish.stage:
                    key = f"{fish.stage}_{fish.species}"
                    counts[key] = counts.get(key, 0) + 1
        return counts
    
    def _update_unlock_status(self, species: str, count: int) -> None:
        """
        更新指定魚種的最大數量記錄
        
        Args:
            species: 魚種名稱
            count: 當前數量
        """
        if not species:
            return
        
        if species not in self._unlocked_species:
            self._unlocked_species[species] = {
                "max_count_reached": 0,
                "total_count_reached": 0,  # 新增：累計曾達到過該階段的魚數量
                "unlocked": False,
            }
        
        old_max = self._unlocked_species[species]["max_count_reached"]
        old_total = self._unlocked_species[species].get("total_count_reached", 0)
        
        # 更新最大數量記錄（同時存在的最大數量）
        if count > self._unlocked_species[species]["max_count_reached"]:
            self._unlocked_species[species]["max_count_reached"] = count
            # 這裡可以根據解鎖條件設定 unlocked 狀態
            # 目前先設為 True（未來商店系統會使用此資訊）
            self._unlocked_species[species]["unlocked"] = True
        
        # 記錄更新詳情（僅對 large_鬥魚 輸出詳細日誌）
        if "large_鬥魚" in species:
            new_max = self._unlocked_species[species]["max_count_reached"]
            new_total = self._unlocked_species[species].get("total_count_reached", 0)
            print(f"[里程碑更新] {species}: count={count}, 舊max={old_max}, 新max={new_max}, 舊total={old_total}, 新total={new_total}")
        
        # 更新工具解鎖狀態（當魚種數量變更時）
        self._update_tool_unlocks()
    
    def _update_tool_unlocks(self) -> None:
        """依工具配置與當前解鎖狀態更新水族箱投食機顯示（僅更新已解鎖的工具）"""
        print(f"[工具解鎖狀態] 已解鎖工具: {self._unlocked_tools}")
        for tool_name in self._unlocked_tools:
            # 更新投食機部件顯示（僅已解鎖的工具）
            if tool_name == "飼料投食機":
                print(f"[工具解鎖狀態] 顯示投食機")
                self._feed_machine_widget.set_feed_machine_visible(True)
                current_color = self._tool_colors.get(tool_name, FEED_MACHINE_DEFAULT_COLOR)
                print(f"[工具解鎖狀態] 投食機顏色: {current_color}")
                self._feed_machine_widget.set_feed_machine_color(current_color)
                # 更新投食機的已解鎖飼料列表
                self._feed_machine_widget.set_unlocked_feeds(self._unlocked_feeds, self._feed_counters)
    
    def _on_tool_unlock_requested(self, tool_name: str) -> None:
        """處理工具解鎖請求：檢查解鎖條件，通過後加入解鎖列表並更新顯示"""
        if tool_name not in TOOL_CONFIG:
            return
        if tool_name in self._unlocked_tools:
            return  # 已經解鎖
        
        cfg = TOOL_CONFIG[tool_name]
        unlock_species = cfg.get("unlock_species", "")
        unlock_count = cfg.get("unlock_count", 0)
        
        # 檢查解鎖條件（使用累計總數 total_count_reached 判定）
        key = unlock_species
        can_unlock = False
        if key in self._unlocked_species:
            # 優先使用 total_count_reached（累計曾達到過該階段的魚數量）
            total_count = self._unlocked_species[key].get("total_count_reached", 0)
            max_count = self._unlocked_species[key].get("max_count_reached", 0)
            # 取兩者較大的值（向後兼容舊存檔）
            effective_count = max(total_count, max_count)
            can_unlock = effective_count >= unlock_count
            print(f"[工具解鎖檢查] {tool_name}: key={key}, total={total_count}, max={max_count}, effective={effective_count}, 需要={unlock_count}, 可解鎖={can_unlock}")
        
        if not can_unlock:
            print(f"[工具解鎖] {tool_name} 未達到解鎖條件")
            return
        
        # 解鎖工具
        self._unlocked_tools.append(tool_name)
        # 初始化顏色（如果尚未設定）
        if tool_name not in self._tool_colors:
            self._tool_colors[tool_name] = FEED_MACHINE_DEFAULT_COLOR
        
        # 更新水族箱顯示
        self._update_tool_unlocks()
        
        # 更新商店顯示
        self._shop_overlay.update_items(
            self._unlocked_species, self._pets,
            self.total_money, self._unlocked_pets,
            self._pet_levels,
            self._get_fish_count_by_species(),
            self._unlocked_feeds,
            self._feed_cheap_count,
            self._unlocked_tools,
            self._tool_colors,
        )
        
        self._auto_save()
    
    def _on_tool_color_changed(self, tool_name: str, color: str) -> None:
        """處理工具顏色變更請求"""
        if tool_name not in self._unlocked_tools:
            return
        self._tool_colors[tool_name] = color
        if tool_name == "飼料投食機":
            self._feed_machine_widget.set_feed_machine_color(color)
        self._auto_save()
    
    def _load_game_state(self) -> None:
        """
        載入存檔並恢復遊戲狀態（魚類、金額、背景等）
        """
        state = load()
        
        # 恢復金額
        self.total_money = state.get("money", 0)
        self.panel.set_money(self.total_money)
        
        # 初始化贈送條件追蹤（載入時重置，確保狀態變化檢測正常）
        self._last_bonus_condition_met = False
        
        # 恢復解鎖狀態
        self._unlocked_species = state.get("unlocked_species", {})
        self._unlocked_pets = list(state.get("unlocked_pets", []))
        self._pet_levels = dict(state.get("pet_levels", {}))
        self._feed_cheap_count = int(state.get("feed_cheap_count", 0))
        self._feed_counters = dict(state.get("feed_counters", {}))
        self._unlocked_feeds = list(state.get("unlocked_feeds", ["便宜飼料"]))
        self._feed_counter_last_add = dict(state.get("feed_counter_last_add", {}))
        self._unlocked_tools = list(state.get("unlocked_tools", []))
        self._tool_colors = dict(state.get("tool_colors", {}))
        self._update_feed_unlocks()
        # 重要：遊戲時間不會被保存，每次載入時從 0 開始
        # 所以必須重置所有飼料計時器，避免 game_time - last 為負數導致計時器永不觸發
        for feed_name in self._unlocked_feeds:
            if feed_name == "便宜飼料":
                continue
            interval = get_feed_counter_interval_sec(feed_name)
            if interval is None:
                continue
            # 如果沒有計數器記錄，初始化為0
            if feed_name not in self._feed_counters:
                self._feed_counters[feed_name] = 0
            # 重置計時器為當前遊戲時間（0），確保計時器能正常運作
            self._feed_counter_last_add[feed_name] = self.aquarium._game_time_sec
        if hasattr(self.panel, "update_feed_menu"):
            self.panel.update_feed_menu(self._unlocked_feeds, self._feed_counters)
        
        # 恢復背景
        bg_path_str = state.get("background_path")
        if bg_path_str:
            # 嘗試解析為 Path
            bg_path = Path(bg_path_str)
            # 如果是相對路徑，從資源目錄解析
            if not bg_path.is_absolute():
                bg_path = _resource_dir() / bg_path
            # 如果路徑不存在，嘗試從資源目錄查找
            if not bg_path.exists():
                bg_name = Path(bg_path_str).name
                bg_path = _resource_dir() / "background" / bg_name
            if bg_path.exists():
                self.aquarium.set_background(bg_path)
        
        # 恢復背景透明度
        opacity = state.get("background_opacity", 80)
        self.aquarium.set_background_opacity(opacity)
        self.panel._opacity_slider.setValue(opacity)
        
        # 恢復魚類
        fishes_data = state.get("fishes", [])
        resource_dir = _resource_dir()
        
        for fish_dict in fishes_data:
            species = fish_dict.get("species")
            stage = fish_dict.get("stage", "small")
            
            if not species:
                continue
            
            # 構建魚類資源路徑
            # 嘗試找到對應階段的目錄
            fish_species_dir = resource_dir / "fish" / species
            if not fish_species_dir.exists():
                continue
            
            # 尋找對應階段的目錄
            stage_dir = None
            # 鬥魚使用中文階段目錄名（幼鬥魚、中鬥魚、成年鬥魚、天使鬥魚、金鬥魚、寶石鬥魚）
            if species == "鬥魚":
                stage_name_map = {
                    "small": "幼鬥魚",
                    "medium": "中鬥魚",
                    "large": "成年鬥魚",
                    "angel": "天使鬥魚",
                    "golden": "金鬥魚",
                    "gem": "寶石鬥魚",
                }
                stage_dir_name = stage_name_map.get(stage)
                if stage_dir_name:
                    stage_dir = fish_species_dir / stage_dir_name
                    if not stage_dir.exists() or not stage_dir.is_dir():
                        stage_dir = None
            if not stage_dir:
                for subdir in fish_species_dir.iterdir():
                    if subdir.is_dir() and stage.lower() in subdir.name.lower():
                        stage_dir = subdir
                        break
            # 如果找不到對應階段，嘗試使用 small 或「幼」階段
            if not stage_dir:
                for subdir in fish_species_dir.iterdir():
                    if subdir.is_dir() and ("small" in subdir.name.lower() or "幼" in subdir.name):
                        stage_dir = subdir
                        break
            # 仍無階段目錄時，使用魚種目錄本身（如鯊魚、孔雀魚的動畫直接在魚種目錄下，無階段子目錄）
            if not stage_dir:
                stage_dir = fish_species_dir
            
            # 游泳、轉向、吃飯行為與鬥魚、鯊魚相同，由 config.get_fish_behaviors 取得
            swim_behavior, turn_behavior, eat_behavior = get_fish_behaviors(species)
            swim_frames, turn_frames = load_swim_and_turn(
                stage_dir,
                swim_behavior=swim_behavior,
                turn_behavior=turn_behavior,
            )
            if not swim_frames:
                continue
            
            eat_frames = load_fish_animation(stage_dir, behavior=eat_behavior)
            
            # 從字典重建魚類
            fish = Fish.from_dict(
                fish_dict,
                swim_frames=[QPixmap(p) for p in swim_frames],
                turn_frames=[QPixmap(p) for p in turn_frames] if turn_frames else [QPixmap(p) for p in swim_frames],
                eat_frames=[QPixmap(p) for p in eat_frames] if eat_frames else None,
            )
            
            # 添加到水族箱（add_fish 會自動設置回調函數）
            self.aquarium.add_fish(fish)
        
        # 更新解鎖狀態（根據載入的魚類數量）
        counts = self._get_fish_count_by_species()
        for key, count in counts.items():
            self._update_unlock_status(key, count)
        
        # 推斷里程碑：如果有天使鬥魚，推斷曾經有過至少相同數量的成年鬥魚
        # （因為天使鬥魚是從成年鬥魚升級來的）
        angel_betta_count = counts.get("angel_鬥魚", 0)
        if angel_betta_count > 0:
            large_betta_key = "large_鬥魚"
            current_large_max = self._unlocked_species.get(large_betta_key, {}).get("max_count_reached", 0)
            current_large_total = self._unlocked_species.get(large_betta_key, {}).get("total_count_reached", 0)
            # 推斷：曾經的成年鬥魚數量至少 = 當前成年鬥魚 + 天使鬥魚數量
            inferred_large_count = counts.get("large_鬥魚", 0) + angel_betta_count
            if inferred_large_count > current_large_max:
                print(f"[里程碑推斷] 根據 {angel_betta_count} 隻天使鬥魚，推斷曾經有過至少 {inferred_large_count} 隻成年鬥魚")
                self._update_unlock_status(large_betta_key, inferred_large_count)
            # 同時更新累計總數（向後兼容舊存檔）
            if inferred_large_count > current_large_total:
                if large_betta_key not in self._unlocked_species:
                    self._unlocked_species[large_betta_key] = {"max_count_reached": 0, "total_count_reached": 0, "unlocked": False}
                if "total_count_reached" not in self._unlocked_species[large_betta_key]:
                    self._unlocked_species[large_betta_key]["total_count_reached"] = 0
                self._unlocked_species[large_betta_key]["total_count_reached"] = inferred_large_count
                print(f"[里程碑推斷] 更新 {large_betta_key} 累計總數: {current_large_total} -> {inferred_large_count}")
        
        # 更新工具解鎖狀態（載入後）
        self._update_tool_unlocks()
        
        # 調試輸出：顯示當前里程碑狀態
        large_betta_max = self._unlocked_species.get('large_鬥魚', {}).get('max_count_reached', 0)
        large_betta_total = self._unlocked_species.get('large_鬥魚', {}).get('total_count_reached', 0)
        print(f"[里程碑狀態] large_鬥魚 最大同時數量: {large_betta_max}, 累計總數: {large_betta_total}")
        print(f"[里程碑狀態] 當前 large_鬥魚 數量: {counts.get('large_鬥魚', 0)}, angel_鬥魚 數量: {counts.get('angel_鬥魚', 0)}")
        
        # 恢復寵物（在恢復魚類和解鎖狀態之後）
        pets_data = state.get("pets", [])
        for pet_data in pets_data:
            pet_name = pet_data.get("pet_name")
            if pet_name:
                if pet_name == "lobster":
                    pet_name = "龍蝦"
                try:
                    self._spawn_pet(pet_name)
                    # 恢復寵物位置和狀態
                    if pet_name in self._pets:
                        pet = self._pets[pet_name]
                        pos_data = pet_data.get("position", {})
                        if pos_data:
                            pet.position = QPointF(pos_data.get("x", 0), pos_data.get("y", 0))
                        pet.horizontal_direction = pet_data.get("horizontal_direction", 1)
                        pet.facing_left = pet_data.get("facing_left", False)
                except Exception as e:
                    print(f"[載入] 無法恢復寵物 {pet_name}: {e}")
    
    def _save_game_state(self) -> None:
        """
        收集當前遊戲狀態並儲存
        """
        # 收集魚類狀態
        fishes_data = []
        for fish in self.aquarium.fishes:
            fishes_data.append(fish.to_dict())
        
        # 收集寵物狀態
        pets_data = []
        for pet_name, pet in self._pets.items():
            pet_dict = {
                "pet_name": pet_name,
                "position": {"x": float(pet.position.x()), "y": float(pet.position.y())},
                "horizontal_direction": pet.horizontal_direction,
                "facing_left": pet.facing_left,
            }
            pets_data.append(pet_dict)
        
        # 構建狀態字典
        state = {
            "version": "1.0.0",  # 版本號由 game_state.save() 統一設定，這裡僅供參考
            "money": self.total_money,
            "unlocked_species": self._unlocked_species.copy(),
            "unlocked_pets": list(self._unlocked_pets),
            "pet_levels": self._pet_levels.copy(),
            "feed_cheap_count": self._feed_cheap_count,
            "feed_counters": self._feed_counters.copy(),
            "unlocked_feeds": list(self._unlocked_feeds),
            "feed_counter_last_add": self._feed_counter_last_add.copy(),
            "unlocked_tools": list(self._unlocked_tools),
            "tool_colors": self._tool_colors.copy(),
            "fishes": fishes_data,
            "pets": pets_data,
            "background_path": None,
            "background_opacity": self.aquarium.background_opacity,
        }
        
        # 保存背景路徑（相對路徑）
        if self.aquarium.background_path:
            bg_path = Path(self.aquarium.background_path)
            resource_dir = _resource_dir()
            try:
                # 嘗試轉換為相對路徑
                relative_path = bg_path.relative_to(resource_dir)
                state["background_path"] = str(relative_path)
            except ValueError:
                # 如果無法轉換為相對路徑，保存檔案名稱
                state["background_path"] = bg_path.name
        
        # 儲存
        save(state)
    
    def _auto_save(self) -> None:
        """
        觸發自動儲存（非阻塞，失敗不影響遊戲運行）
        """
        try:
            self._save_game_state()
        except Exception as e:
            print(f"[自動儲存] 失敗: {e}")
    
    def _record_fish_milestone_before_upgrade(self, old_fish: Fish) -> None:
        """
        在魚類升級前記錄舊魚種的里程碑（確保升級前的最後數量被記錄）
        
        Args:
            old_fish: 即將升級的舊魚
        """
        if not old_fish.species:
            return
        
        # 計算升級前的當前數量（包含即將升級的這條魚）
        counts = self._get_fish_count_by_species()
        
        # 顯示升級前的詳細狀態
        print(f"[里程碑-升級前] 魚種: {old_fish.species}, 階段: {old_fish.stage}")
        print(f"[里程碑-升級前] 當前魚數量統計: {counts}")
        
        # 記錄基本魚種里程碑
        if old_fish.species:
            current_count = counts.get(old_fish.species, 0)
            old_max = self._unlocked_species.get(old_fish.species, {}).get("max_count_reached", 0)
            self._update_unlock_status(old_fish.species, current_count)
            print(f"[里程碑-升級前] {old_fish.species}: 當前數量={current_count}, 舊里程碑={old_max}, 新里程碑={self._unlocked_species.get(old_fish.species, {}).get('max_count_reached', 0)}")
            if current_count > old_max:
                print(f"[里程碑] {old_fish.species} 里程碑更新: {old_max} -> {current_count}")
        
        # 記錄階段_魚種格式里程碑（重要：記錄升級前的階段）
        if old_fish.stage:
            old_stage_key = f"{old_fish.stage}_{old_fish.species}"
            current_stage_count = counts.get(old_stage_key, 0)
            old_stage_max = self._unlocked_species.get(old_stage_key, {}).get("max_count_reached", 0)
            self._update_unlock_status(old_stage_key, current_stage_count)
            new_max = self._unlocked_species.get(old_stage_key, {}).get("max_count_reached", 0)
            print(f"[里程碑-升級前] {old_stage_key}: 當前數量={current_stage_count}, 舊里程碑={old_stage_max}, 新里程碑={new_max}")
            if current_stage_count > old_stage_max:
                print(f"[里程碑] {old_stage_key} 里程碑更新: {old_stage_max} -> {current_stage_count}")
    
    def _on_fish_upgraded(self, new_fish: Fish) -> None:
        """
        當魚類升級時被調用（由 AquariumWidget 的 _on_fish_upgrade 觸發）
        
        Args:
            new_fish: 升級後的新魚
        """
        # 更新解鎖狀態並自動儲存
        counts = self._get_fish_count_by_species()
        
        # 顯示升級後的詳細狀態
        print(f"[里程碑-升級後] 新魚種: {new_fish.species}, 新階段: {new_fish.stage}")
        print(f"[里程碑-升級後] 當前魚數量統計: {counts}")
        
        if new_fish.species:
            # 更新基本魚種解鎖狀態
            old_max = self._unlocked_species.get(new_fish.species, {}).get("max_count_reached", 0)
            self._update_unlock_status(new_fish.species, counts.get(new_fish.species, 0))
            new_max = self._unlocked_species.get(new_fish.species, {}).get("max_count_reached", 0)
            print(f"[里程碑-升級後] {new_fish.species}: 當前數量={counts.get(new_fish.species, 0)}, 舊里程碑={old_max}, 新里程碑={new_max}")
            
            # 更新階段_魚種格式解鎖狀態（用於寵物解鎖）
            if new_fish.stage:
                stage_key = f"{new_fish.stage}_{new_fish.species}"
                old_stage_max = self._unlocked_species.get(stage_key, {}).get("max_count_reached", 0)
                old_total = self._unlocked_species.get(stage_key, {}).get("total_count_reached", 0)
                
                self._update_unlock_status(stage_key, counts.get(stage_key, 0))
                
                # 累計曾達到過該階段的魚數量（每次有魚升級到此階段時 +1）
                self._increment_total_count(stage_key)
                
                new_stage_max = self._unlocked_species.get(stage_key, {}).get("max_count_reached", 0)
                new_total = self._unlocked_species.get(stage_key, {}).get("total_count_reached", 0)
                print(f"[里程碑-升級後] {stage_key}: 當前數量={counts.get(stage_key, 0)}, 舊max={old_stage_max}, 新max={new_stage_max}, 舊total={old_total}, 新total={new_total}")
        
        # 顯示所有 large_鬥魚 相關的里程碑狀態
        large_betta_max = self._unlocked_species.get("large_鬥魚", {}).get("max_count_reached", 0)
        large_betta_total = self._unlocked_species.get("large_鬥魚", {}).get("total_count_reached", 0)
        print(f"[里程碑-升級後] === large_鬥魚 最大同時數量: {large_betta_max}, 累計總數: {large_betta_total} ===")
        
        self._auto_save()
    
    def _increment_total_count(self, species_key: str) -> None:
        """
        累加指定魚種/階段的累計達到總數
        
        Args:
            species_key: 魚種/階段鍵名（如 "large_鬥魚"）
        """
        if not species_key:
            return
        
        if species_key not in self._unlocked_species:
            self._unlocked_species[species_key] = {
                "max_count_reached": 0,
                "total_count_reached": 0,
                "unlocked": False,
            }
        
        # 確保有 total_count_reached 欄位
        if "total_count_reached" not in self._unlocked_species[species_key]:
            self._unlocked_species[species_key]["total_count_reached"] = 0
        
        # 累加總數
        self._unlocked_species[species_key]["total_count_reached"] += 1
        
        print(f"[累計里程碑] {species_key} 累計總數 +1 = {self._unlocked_species[species_key]['total_count_reached']}")


def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    # 設定應用程式樣式
    app.setStyle('Fusion')
    
    
    # 查找"水世界"背景圖片
    resource_dir = Path(__file__).parent / "resource" / "background"
    background_path = None
    if resource_dir.exists():
        water_world_path = resource_dir / "水世界.jpg"
        if water_world_path.exists():
            background_path = water_world_path
        else:
            # 如果找不到水世界，使用第一個找到的背景圖片
            background_files = list(resource_dir.glob("*.jpg")) + list(resource_dir.glob("*.png"))
            if background_files:
                background_path = background_files[0]
    
    # 創建透明水族箱視窗（進一步縮小尺寸：512x384）
    window = TransparentAquariumWindow(
        aquarium_size=(512, 384),
        background_path=background_path
    )
    
    # 顯示視窗
    window.show()
    
    # 運行應用程式
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
