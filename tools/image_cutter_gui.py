#!/usr/bin/env python3
"""
圖片裁切工具 GUI

提供圖形化介面來設定裁切參數、預覽圖片、管理資料夾結構。
"""

import sys
import os
from pathlib import Path
from typing import Optional, Tuple, List
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit, QPushButton,
    QScrollArea, QCheckBox, QProgressBar, QMessageBox, QFileDialog,
    QSplitter, QGroupBox, QFormLayout, QSpinBox, QTextEdit, QComboBox,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QSize, QPoint
from PyQt6.QtGui import QPixmap, QColor, QIcon, QImage, QPainter, QPen
from PIL import Image, ImageDraw, ImageFont

# 嘗試導入 ImageQt，不同版本的 Pillow 可能有不同的導入方式
try:
    from PIL.ImageQt import ImageQt
except ImportError:
    try:
        from PIL import ImageQt
    except ImportError:
        ImageQt = None


FISH_BEHAVIOR_FOLDERS = [
    "1_餓肚子游泳",
    "2_餓肚子轉向",
    "3_餓肚子吃",
    "4_餓肚子死掉",
    "5_吃飽游泳",
    "6_吃飽吃",
    "7_吃飽轉向",
]




class ImagePreviewWidget(QWidget):
    """圖片預覽組件：用 QLabel 顯示圖片，避免自訂 paintEvent 導致崩潰"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_image: Optional[Image.Image] = None
        self.pixmap: Optional[QPixmap] = None
        self.selection_mode = False  # 是否處於選擇模式
        self.drawing_bbox = False  # 是否正在繪製bbox
        self.bbox_start: Optional[QPoint] = None  # bbox起始點
        self.bbox_end: Optional[QPoint] = None  # bbox結束點
        self.dfs_regions: List[Tuple[int, int, int, int]] = []
        self.categories: List[dict] = []
        self.selected_category_index = -1
        self.image_scale = 1.0  # 圖片縮放比例
        self.image_offset_x = 0  # 圖片在label中的偏移x
        self.image_offset_y = 0  # 圖片在label中的偏移y
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background-color: #2b2b2b;")
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumSize(400, 400)
        self.preview_label.setStyleSheet("background-color: #2b2b2b; color: #888;")
        self.preview_label.setText("請在左側選擇圖片")
        self.preview_label.setMouseTracking(True)
        self.preview_label.mousePressEvent = self.on_mouse_press
        self.preview_label.mouseMoveEvent = self.on_mouse_move
        self.preview_label.mouseReleaseEvent = self.on_mouse_release
        self.preview_label.paintEvent = self.on_paint
        self.scroll.setWidget(self.preview_label)
        layout.addWidget(self.scroll)
        
    def set_image(self, image_path: Path):
        """載入圖片並用 QLabel 顯示"""
        try:
            if not image_path.exists():
                self.original_image = None
                self.pixmap = None
                self.preview_label.clear()
                self.preview_label.setText("圖片不存在")
                return
            
            self.original_image = Image.open(image_path)
            if self.original_image.mode not in ('RGB', 'RGBA'):
                if self.original_image.mode == 'P' and 'transparency' in self.original_image.info:
                    self.original_image = self.original_image.convert('RGBA')
                else:
                    self.original_image = self.original_image.convert('RGB')
            
            # 顯示原圖
            self.pixmap = self._pil_to_pixmap(self.original_image)
            if self.pixmap and not self.pixmap.isNull():
                w, h = self.preview_label.width(), self.preview_label.height()
                if w > 0 and h > 0:
                    scaled = self.pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)
                else:
                    self.preview_label.setPixmap(self.pixmap)
                self.preview_label.adjustSize()
                self._calculate_image_transform()
        except Exception as e:
            self.preview_label.setText(f"載入失敗: {str(e)}")
            self.original_image = None
            self.pixmap = None
    
    def set_image_with_dfs_regions(self, image_path: Path, regions: List[Tuple[int, int, int, int]]):
        """載入圖片並顯示 DFS 檢測到的區域"""
        try:
            if not image_path.exists():
                self.original_image = None
                self.pixmap = None
                self.preview_label.clear()
                self.preview_label.setText("圖片不存在")
                return
            
            self.original_image = Image.open(image_path)
            if self.original_image.mode not in ('RGB', 'RGBA'):
                if self.original_image.mode == 'P' and 'transparency' in self.original_image.info:
                    self.original_image = self.original_image.convert('RGBA')
                else:
                    self.original_image = self.original_image.convert('RGB')
            
            self._update_preview_with_dfs_regions(regions)
        except Exception as e:
            self.preview_label.setText(f"載入失敗: {str(e)}")
            self.original_image = None
            self.pixmap = None
    
    def _update_preview_with_dfs_regions(self, regions: List[Tuple[int, int, int, int]]):
        """在圖片上畫 DFS 檢測到的區域邊界框"""
        if self.original_image is None:
            return
        
        if not regions:
            # 沒有區域時顯示原圖
            self.pixmap = self._pil_to_pixmap(self.original_image)
            if self.pixmap and not self.pixmap.isNull():
                w, h = self.preview_label.width(), self.preview_label.height()
                if w > 0 and h > 0:
                    scaled = self.pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)
            return
        
        try:
            img = self.original_image.copy()
            w_img, h_img = img.size
            draw = ImageDraw.Draw(img)
            # 邊界框顏色：RGB 用紅，RGBA 用半透明紅
            line_color = (255, 0, 0, 220) if img.mode == 'RGBA' else (255, 0, 0)
            line_width = max(2, min(w_img, h_img) // 150)
            
            # 嘗試載入字體（如果失敗則使用預設字體）
            try:
                # 嘗試使用系統字體
                font_size = max(12, min(w_img, h_img) // 30)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # 文字顏色：白色背景，黑色文字
            text_color = (255, 255, 255) if img.mode == 'RGB' else (255, 255, 255, 255)
            text_bg_color = (0, 0, 0) if img.mode == 'RGB' else (0, 0, 0, 200)
            
            # 畫每個檢測到的區域邊界框
            for idx, (left, top, right, bottom) in enumerate(regions):
                # 畫矩形邊框
                draw.rectangle([left, top, right - 1, bottom - 1], 
                             outline=line_color, width=line_width)
                
                # 在左上角畫順序編號
                text = str(idx)
                # 計算文字大小
                try:
                    bbox = draw.textbbox((0, 0), text, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                except:
                    # 如果 textbbox 不可用，使用估算值
                    text_width = len(text) * font_size // 2
                    text_height = font_size
                
                # 畫文字背景（小矩形）
                padding = 2
                bg_left = left + padding
                bg_top = top + padding
                bg_right = bg_left + text_width + padding * 2
                bg_bottom = bg_top + text_height + padding * 2
                draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], 
                             fill=text_bg_color)
                
                # 畫文字
                draw.text((bg_left + padding, bg_top + padding), text, 
                         fill=text_color, font=font)
            
            self.pixmap = self._pil_to_pixmap(img)
            if self.pixmap is None or self.pixmap.isNull():
                return
            
            w, h = self.preview_label.width(), self.preview_label.height()
            if w > 0 and h > 0:
                scaled = self.pixmap.scaled(
                    w, h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
            else:
                self.preview_label.setPixmap(self.pixmap)
            self.preview_label.adjustSize()
        except Exception as e:
            # 若畫框失敗，至少顯示原圖
            import traceback
            print(f"畫框失敗: {e}")
            traceback.print_exc()
            self.pixmap = self._pil_to_pixmap(self.original_image)
            if self.pixmap and not self.pixmap.isNull():
                w, h = self.preview_label.width(), self.preview_label.height()
                if w > 0 and h > 0:
                    scaled = self.pixmap.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.preview_label.setPixmap(scaled)
    
    def _pil_to_pixmap(self, pil_image) -> Optional[QPixmap]:
        """PIL Image 轉 QPixmap，優先字節方式避免 ImageQt 問題"""
        try:
            import io
            buf = io.BytesIO()
            pil_image.save(buf, format='PNG')
            buf.seek(0)
            data = buf.getvalue()
            pix = QPixmap()
            if pix.loadFromData(data):
                return pix
        except Exception:
            pass
        if ImageQt is not None:
            try:
                qimg = ImageQt(pil_image)
                return QPixmap.fromImage(qimg)
            except Exception:
                pass
        return None
    
    def set_selection_mode(self, enabled: bool):
        """設置選擇模式"""
        self.selection_mode = enabled
        if not enabled:
            self.drawing_bbox = False
            self.bbox_start = None
            self.bbox_end = None
        self.preview_label.update()
    
    def _calculate_image_transform(self):
        """計算圖片在label中的縮放和偏移"""
        if self.pixmap is None or self.pixmap.isNull() or self.original_image is None:
            return
        
        label_w = self.preview_label.width()
        label_h = self.preview_label.height()
        pixmap_w = self.pixmap.width()
        pixmap_h = self.pixmap.height()
        
        if label_w <= 0 or label_h <= 0 or pixmap_w <= 0 or pixmap_h <= 0:
            return
        
        # 計算縮放比例（保持長寬比）
        scale_w = label_w / pixmap_w
        scale_h = label_h / pixmap_h
        self.image_scale = min(scale_w, scale_h)
        
        # 計算縮放後的尺寸
        scaled_w = int(pixmap_w * self.image_scale)
        scaled_h = int(pixmap_h * self.image_scale)
        
        # 計算偏移（居中）
        self.image_offset_x = (label_w - scaled_w) // 2
        self.image_offset_y = (label_h - scaled_h) // 2
    
    def _label_to_image_coords(self, label_x: int, label_y: int) -> Optional[Tuple[int, int]]:
        """將label座標轉換為圖片座標"""
        if self.original_image is None or self.pixmap is None or self.pixmap.isNull():
            return None
        
        # 獲取label中實際顯示的pixmap
        current_pixmap = self.preview_label.pixmap()
        if current_pixmap is None or current_pixmap.isNull():
            return None
        
        label_w = self.preview_label.width()
        label_h = self.preview_label.height()
        pixmap_w = current_pixmap.width()
        pixmap_h = current_pixmap.height()
        
        if label_w <= 0 or label_h <= 0 or pixmap_w <= 0 or pixmap_h <= 0:
            return None
        
        # 計算縮放比例（保持長寬比）
        scale_w = label_w / pixmap_w
        scale_h = label_h / pixmap_h
        image_scale = min(scale_w, scale_h)
        
        # 計算縮放後的尺寸
        scaled_w = int(pixmap_w * image_scale)
        scaled_h = int(pixmap_h * image_scale)
        
        # 計算偏移（居中）
        image_offset_x = (label_w - scaled_w) // 2
        image_offset_y = (label_h - scaled_h) // 2
        
        # 轉換為相對於圖片的座標
        img_x = label_x - image_offset_x
        img_y = label_y - image_offset_y
        
        # 檢查是否在圖片範圍內
        if img_x < 0 or img_y < 0 or img_x > scaled_w or img_y > scaled_h:
            return None
        
        # 轉換回原始pixmap座標（相對於顯示的pixmap）
        pixmap_x = int(img_x / image_scale)
        pixmap_y = int(img_y / image_scale)
        
        # 確保在pixmap範圍內
        pixmap_x = max(0, min(pixmap_x, pixmap_w - 1))
        pixmap_y = max(0, min(pixmap_y, pixmap_h - 1))
        
        # 轉換回原始圖片座標（考慮pixmap可能與原始圖片尺寸不同）
        orig_w, orig_h = self.original_image.size
        orig_x = int(pixmap_x * orig_w / pixmap_w)
        orig_y = int(pixmap_y * orig_h / pixmap_h)
        
        # 確保在圖片範圍內
        orig_x = max(0, min(orig_x, orig_w - 1))
        orig_y = max(0, min(orig_y, orig_h - 1))
        
        return (orig_x, orig_y)
    
    def _image_to_label_coords(self, img_x: int, img_y: int) -> Optional[Tuple[int, int]]:
        """將圖片座標轉換為label座標"""
        if self.original_image is None or self.pixmap is None or self.pixmap.isNull():
            return None
        
        self._calculate_image_transform()
        
        label_x = int(img_x * self.image_scale) + self.image_offset_x
        label_y = int(img_y * self.image_scale) + self.image_offset_y
        
        return (label_x, label_y)
    
    def on_mouse_press(self, event):
        """滑鼠按下事件"""
        if not self.selection_mode:
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            coords = self._label_to_image_coords(event.pos().x(), event.pos().y())
            if coords:
                self.drawing_bbox = True
                self.bbox_start = QPoint(coords[0], coords[1])
                self.bbox_end = QPoint(coords[0], coords[1])
                self.preview_label.update()
        
        elif event.button() == Qt.MouseButton.RightButton:
            # 右鍵點擊：刪除點擊的區域
            coords = self._label_to_image_coords(event.pos().x(), event.pos().y())
            if coords and self.dfs_regions:
                click_x, click_y = coords
                
                # 找到點擊的區域（找到包含點擊座標的區域）
                clicked_region_idx = None
                for idx, (left, top, right, bottom) in enumerate(self.dfs_regions):
                    if left <= click_x < right and top <= click_y < bottom:
                        clicked_region_idx = idx
                        break
                
                if clicked_region_idx is not None:
                    # 通知主視窗刪除區域
                    parent = self.parent()
                    while parent:
                        if hasattr(parent, 'remove_dfs_region'):
                            parent.remove_dfs_region(clicked_region_idx)
                            break
                        parent = parent.parent()
    
    def on_mouse_move(self, event):
        """滑鼠移動事件"""
        if not self.selection_mode:
            # 顯示十字線
            self.preview_label.setCursor(Qt.CursorShape.CrossCursor)
            return
        
        # 顯示十字線
        self.preview_label.setCursor(Qt.CursorShape.CrossCursor)
        
        if self.drawing_bbox and self.bbox_start:
            coords = self._label_to_image_coords(event.pos().x(), event.pos().y())
            if coords:
                self.bbox_end = QPoint(coords[0], coords[1])
                self.preview_label.update()
    
    def on_mouse_release(self, event):
        """滑鼠釋放事件"""
        if not self.selection_mode or not self.drawing_bbox:
            return
        
        if event.button() == Qt.MouseButton.LeftButton:
            coords = self._label_to_image_coords(event.pos().x(), event.pos().y())
            if coords and self.bbox_start:
                self.bbox_end = QPoint(coords[0], coords[1])
                
                # 計算bbox範圍
                left = min(self.bbox_start.x(), self.bbox_end.x())
                top = min(self.bbox_start.y(), self.bbox_end.y())
                right = max(self.bbox_start.x(), self.bbox_end.x())
                bottom = max(self.bbox_start.y(), self.bbox_end.y())
                
                # 調試輸出
                print(f"BBox座標: ({left}, {top}, {right}, {bottom})")
                print(f"原始圖片尺寸: {self.original_image.size if self.original_image else 'None'}")
                print(f"DFS區域數量: {len(self.dfs_regions)}")
                
                # 通知主視窗分配區域
                # 向上查找主視窗
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'assign_regions_to_category'):
                        parent.assign_regions_to_category((left, top, right, bottom))
                        break
                    parent = parent.parent()
                else:
                    print("警告: 無法找到主視窗")
                
                # 重置bbox
                self.drawing_bbox = False
                self.bbox_start = None
                self.bbox_end = None
                self.preview_label.update()
    
    def on_paint(self, event):
        """繪製事件"""
        # 先調用原始的paintEvent來顯示圖片
        QLabel.paintEvent(self.preview_label, event)
        
        if not self.selection_mode:
            return
        
        # 繪製bbox（在圖片上方）
        if self.drawing_bbox and self.bbox_start and self.bbox_end:
            painter = QPainter(self.preview_label)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 轉換為label座標
            start_label = self._image_to_label_coords(self.bbox_start.x(), self.bbox_start.y())
            end_label = self._image_to_label_coords(self.bbox_end.x(), self.bbox_end.y())
            
            if start_label and end_label:
                pen = QPen(QColor(0, 255, 0), 2)  # 綠色邊框
                painter.setPen(pen)
                painter.setBrush(QColor(0, 255, 0, 30))  # 半透明綠色填充
                
                x1, y1 = start_label
                x2, y2 = end_label
                painter.drawRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))
            painter.end()
    
    def update_preview_with_categories(self, dfs_regions: List[Tuple[int, int, int, int]], 
                                      categories: List[dict], selected_category_index: int = -1):
        """更新預覽，顯示類別分配情況"""
        self.dfs_regions = dfs_regions
        self.categories = categories
        self.selected_category_index = selected_category_index
        
        if self.original_image is None:
            return
        
        try:
            img = self.original_image.copy()
            w_img, h_img = img.size
            draw = ImageDraw.Draw(img)
            
            # 定義顏色（為不同類別使用不同顏色）
            category_colors = [
                (255, 0, 0),    # 紅色
                (0, 255, 0),    # 綠色
                (0, 0, 255),    # 藍色
                (255, 255, 0),  # 黃色
                (255, 0, 255),  # 洋紅
                (0, 255, 255),  # 青色
            ]
            
            line_width = max(2, min(w_img, h_img) // 150)
            
            # 嘗試載入字體
            try:
                font_size = max(12, min(w_img, h_img) // 30)
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # 繪製每個類別的區域
            for cat_idx, category in enumerate(categories):
                color = category_colors[cat_idx % len(category_colors)]
                if img.mode == 'RGBA':
                    line_color = (*color, 220)
                    text_color = (255, 255, 255, 255)
                    text_bg_color = (*color, 200)
                else:
                    line_color = color
                    text_color = (255, 255, 255)
                    text_bg_color = (0, 0, 0)
                
                # 繪製該類別的所有區域
                for region_idx in category['regions']:
                    if 0 <= region_idx < len(dfs_regions):
                        left, top, right, bottom = dfs_regions[region_idx]
                        draw.rectangle([left, top, right - 1, bottom - 1], 
                                     outline=line_color, width=line_width)
                        
                        # 顯示類別名稱和索引
                        text = f"{category['name']}\n{region_idx}"
                        try:
                            bbox = draw.textbbox((0, 0), text.split('\n')[0], font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1] * 2
                        except:
                            text_width = len(text) * font_size // 2
                            text_height = font_size * 2
                        
                        padding = 2
                        bg_left = left + padding
                        bg_top = top + padding
                        bg_right = bg_left + text_width + padding * 2
                        bg_bottom = bg_top + text_height + padding * 2
                        draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], 
                                     fill=text_bg_color)
                        draw.text((bg_left + padding, bg_top + padding), text, 
                                 fill=text_color, font=font)
            
            # 繪製未分配的區域（灰色）
            assigned_indices = set()
            for category in categories:
                assigned_indices.update(category['regions'])
            
            unassigned_color = (128, 128, 128) if img.mode == 'RGB' else (128, 128, 128, 180)
            for idx, (left, top, right, bottom) in enumerate(dfs_regions):
                if idx not in assigned_indices:
                    draw.rectangle([left, top, right - 1, bottom - 1], 
                                 outline=unassigned_color, width=line_width)
                    
                    # 顯示索引
                    text = str(idx)
                    try:
                        bbox = draw.textbbox((0, 0), text, font=font)
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                    except:
                        text_width = len(text) * font_size // 2
                        text_height = font_size
                    
                    padding = 2
                    bg_left = left + padding
                    bg_top = top + padding
                    bg_right = bg_left + text_width + padding * 2
                    bg_bottom = bg_top + text_height + padding * 2
                    bg_color = (0, 0, 0) if img.mode == 'RGB' else (0, 0, 0, 200)
                    draw.rectangle([bg_left, bg_top, bg_right, bg_bottom], fill=bg_color)
                    draw.text((bg_left + padding, bg_top + padding), text, 
                             fill=(255, 255, 255) if img.mode == 'RGB' else (255, 255, 255, 255), 
                             font=font)
            
            self.pixmap = self._pil_to_pixmap(img)
            if self.pixmap is None or self.pixmap.isNull():
                return
            
            w, h = self.preview_label.width(), self.preview_label.height()
            if w > 0 and h > 0:
                scaled = self.pixmap.scaled(
                    w, h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
            else:
                self.preview_label.setPixmap(self.pixmap)
            self.preview_label.adjustSize()
        except Exception as e:
            import traceback
            print(f"更新預覽失敗: {e}")
            traceback.print_exc()
    
    def resizeEvent(self, event):
        """視窗大小改變時重新縮放預覽圖"""
        super().resizeEvent(event)
        if self.pixmap is not None and not self.pixmap.isNull():
            w = self.preview_label.width()
            h = self.preview_label.height()
            if w > 0 and h > 0:
                scaled = self.pixmap.scaled(
                    w, h,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
                self._calculate_image_transform()


class ImageCutterGUI(QMainWindow):
    """圖片裁切工具主視窗"""
    
    def __init__(self):
        super().__init__()
        self.resource_dir = Path("resource")
        self.output_dir: Optional[Path] = None
        self.selected_images = []
        self.dfs_regions = []  # DFS 檢測到的區域列表
        self.classify_basis = "none"  # none|fish|feed|monster|pet
        
        # 類別管理
        self.categories = []  # List[dict] 每個dict包含: {'name': str, 'regions': List[int]}，regions是dfs_regions的索引列表
        self.selected_category_index = -1  # 當前選中的類別索引，-1表示未選中
        self.current_category_name = ""  # 當前輸入的類別名稱
        
        self.init_ui()
        self.load_folder_structure()
    
    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("圖片裁切工具 - Desktop Feeding Fish")
        self.setGeometry(100, 100, 1400, 900)
        # 確保視窗不會被意外關閉
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, False)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主佈局
        main_layout = QHBoxLayout(central_widget)
        
        # 創建分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左側：資料夾樹狀視圖
        left_panel = self.create_folder_panel()
        splitter.addWidget(left_panel)
        
        # 中間：圖片預覽
        center_panel = self.create_preview_panel()
        splitter.addWidget(center_panel)
        
        # 右側：參數設定
        right_panel = self.create_parameter_panel()
        splitter.addWidget(right_panel)
        
        # 設定分割器比例
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        
        main_layout.addWidget(splitter)
        
        # 底部狀態欄
        self.statusBar().showMessage("就緒")
    
    def create_folder_panel(self) -> QWidget:
        """創建資料夾面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 標題
        title = QLabel("資源資料夾結構")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # 重新載入按鈕
        reload_btn = QPushButton("重新載入")
        reload_btn.clicked.connect(self.load_folder_structure)
        layout.addWidget(reload_btn)
        
        # 樹狀視圖
        self.folder_tree = QTreeWidget()
        self.folder_tree.setHeaderLabel("檔案結構")
        self.folder_tree.itemSelectionChanged.connect(self.on_item_selected)
        layout.addWidget(self.folder_tree)
        
        # 選擇資訊
        self.selection_info = QLabel("未選擇任何圖片")
        self.selection_info.setWordWrap(True)
        layout.addWidget(self.selection_info)
        
        return panel
    
    def create_preview_panel(self) -> QWidget:
        """創建預覽面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 標題
        title = QLabel("圖片預覽")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # 預覽區域
        self.preview_widget = ImagePreviewWidget(self)
        self.preview_widget.setMinimumSize(400, 400)
        self.preview_widget.setStyleSheet("background-color: #2b2b2b;")
        layout.addWidget(self.preview_widget)
        
        # 圖片資訊
        self.image_info = QLabel("未載入圖片")
        layout.addWidget(self.image_info)
        
        return panel
    
    def create_parameter_panel(self) -> QWidget:
        """創建參數設定面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 標題
        title = QLabel("裁切參數")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)
        
        # DFS 參數組
        self.dfs_group = QGroupBox("DFS 參數")
        dfs_layout = QFormLayout(self.dfs_group)
        
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(1, 10000)
        self.min_size_spin.setValue(100)
        self.min_size_spin.valueChanged.connect(self.on_dfs_params_changed)
        dfs_layout.addRow("最小區域大小:", self.min_size_spin)
        
        self.alpha_threshold_spin = QSpinBox()
        self.alpha_threshold_spin.setRange(0, 255)
        self.alpha_threshold_spin.setValue(1)
        self.alpha_threshold_spin.valueChanged.connect(self.on_dfs_params_changed)
        dfs_layout.addRow("Alpha 閾值:", self.alpha_threshold_spin)
        
        self.padding_spin = QSpinBox()
        self.padding_spin.setRange(0, 100)
        self.padding_spin.setValue(0)
        self.padding_spin.valueChanged.connect(self.on_dfs_params_changed)
        dfs_layout.addRow("邊距 (像素):", self.padding_spin)
        
        # 分割敏感度參數（使用QDoubleSpinBox）
        from PyQt6.QtWidgets import QDoubleSpinBox
        self.split_sensitivity_spin = QDoubleSpinBox()
        self.split_sensitivity_spin.setRange(0.05, 1.0)
        self.split_sensitivity_spin.setSingleStep(0.05)
        self.split_sensitivity_spin.setValue(0.3)
        self.split_sensitivity_spin.setDecimals(2)
        self.split_sensitivity_spin.valueChanged.connect(self.on_dfs_params_changed)
        dfs_layout.addRow("分割敏感度:", self.split_sensitivity_spin)
        dfs_layout.addRow("", QLabel("(越小越容易分割，建議0.1-0.3)"))
        
        self.dfs_detect_btn = QPushButton("檢測區域")
        self.dfs_detect_btn.clicked.connect(self.detect_dfs_regions)
        dfs_layout.addRow("", self.dfs_detect_btn)
        
        layout.addWidget(self.dfs_group)

        # 類別管理組
        category_group = QGroupBox("類別管理")
        category_layout = QVBoxLayout(category_group)
        
        # 類別清單
        category_list_label = QLabel("類別清單:")
        category_layout.addWidget(category_list_label)
        
        self.category_list = QListWidget()
        self.category_list.setMaximumHeight(150)
        self.category_list.itemClicked.connect(self.on_category_selected)
        category_layout.addWidget(self.category_list)
        
        # 類別名稱輸入框
        name_input_layout = QHBoxLayout()
        name_label = QLabel("類別名稱:")
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("輸入類別名稱（資料夾名稱）")
        self.category_name_input.textChanged.connect(self.on_category_name_changed)
        name_input_layout.addWidget(name_label)
        name_input_layout.addWidget(self.category_name_input)
        category_layout.addLayout(name_input_layout)
        
        # 新增/刪除按鈕
        button_layout = QHBoxLayout()
        self.add_category_btn = QPushButton("新增類別")
        self.add_category_btn.clicked.connect(self.add_category)
        self.delete_category_btn = QPushButton("刪除類別")
        self.delete_category_btn.clicked.connect(self.delete_category)
        button_layout.addWidget(self.add_category_btn)
        button_layout.addWidget(self.delete_category_btn)
        category_layout.addLayout(button_layout)
        
        layout.addWidget(category_group)

        # 輸出分類
        classify_group = QGroupBox("輸出分類")
        classify_layout = QFormLayout(classify_group)
        self.classify_combo = QComboBox()
        self.classify_combo.addItems(["不分類", "魚", "飼料 & 錢", "怪獸", "寵物"])
        self.classify_combo.currentIndexChanged.connect(self.on_classification_changed)
        classify_layout.addRow("分類依據:", self.classify_combo)
        self.classify_hint = QLabel(
            "提示：目前僅「魚」有自動分類邏輯。\n"
            "魚：DFS 檢測到的區域會依橫排(由上而下)分類到對應資料夾；\n"
            "每排前 10 個區域會被分類，logo區域會自動排除。\n"
            "如果logo未被正確排除，請使用右鍵點擊刪除。"
        )
        self.classify_hint.setWordWrap(True)
        classify_layout.addRow("", self.classify_hint)
        layout.addWidget(classify_group)
        
        # 輸出目錄
        output_group = QGroupBox("輸出設定")
        output_layout = QVBoxLayout(output_group)
        
        self.output_label = QLabel("未設定輸出目錄")
        output_layout.addWidget(self.output_label)
        
        output_btn = QPushButton("選擇輸出目錄")
        output_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(output_btn)
        
        layout.addWidget(output_group)
        
        # 操作按鈕
        self.crop_btn = QPushButton("執行裁切")
        self.crop_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 10px;")
        self.crop_btn.clicked.connect(self.start_cropping)
        layout.addWidget(self.crop_btn)
        
        # 進度條
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 狀態訊息
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        layout.addWidget(self.status_text)
        
        layout.addStretch()
        
        return panel

    def on_category_name_changed(self, text: str):
        """類別名稱改變"""
        self.current_category_name = text
    
    def add_category(self):
        """新增類別"""
        name = self.category_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "警告", "請輸入類別名稱")
            return
        
        # 檢查名稱是否重複
        if any(cat['name'] == name for cat in self.categories):
            QMessageBox.warning(self, "警告", f"類別「{name}」已存在")
            return
        
        # 新增類別
        self.categories.append({'name': name, 'regions': []})
        self.update_category_list()
        
        # 清空輸入框
        self.category_name_input.clear()
        self.current_category_name = ""
        
        # 選中新增的類別
        self.selected_category_index = len(self.categories) - 1
        self.category_list.setCurrentRow(self.selected_category_index)
        
        # 啟用預覽組件的交互模式
        self.preview_widget.set_selection_mode(True)
        self.statusBar().showMessage(f"已選中類別「{name}」，請在圖片上拖移選擇區域")
    
    def delete_category(self):
        """刪除類別"""
        if self.selected_category_index < 0 or self.selected_category_index >= len(self.categories):
            QMessageBox.warning(self, "警告", "請先選擇要刪除的類別")
            return
        
        category = self.categories[self.selected_category_index]
        reply = QMessageBox.question(
            self, "確認",
            f"確定要刪除類別「{category['name']}」嗎？\n"
            f"此類別包含 {len(category['regions'])} 個區域。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.categories.pop(self.selected_category_index)
            self.selected_category_index = -1
            self.update_category_list()
            self.preview_widget.set_selection_mode(False)
            self.preview_widget.update_preview_with_categories(self.dfs_regions, self.categories)
            self.statusBar().showMessage("已刪除類別")
    
    def on_category_selected(self, item: QListWidgetItem):
        """類別被選中"""
        index = self.category_list.row(item)
        if 0 <= index < len(self.categories):
            self.selected_category_index = index
            category = self.categories[index]
            self.statusBar().showMessage(
                f"已選中類別「{category['name']}」（{len(category['regions'])} 個區域），"
                f"請在圖片上拖移選擇區域"
            )
            # 啟用預覽組件的交互模式
            self.preview_widget.set_selection_mode(True)
            # 更新預覽以顯示當前類別的區域
            self.preview_widget.update_preview_with_categories(self.dfs_regions, self.categories, self.selected_category_index)
    
    def update_category_list(self):
        """更新類別清單顯示"""
        self.category_list.clear()
        for cat in self.categories:
            region_count = len(cat['regions'])
            item_text = f"{cat['name']} ({region_count} 個區域)"
            self.category_list.addItem(item_text)
    
    def remove_dfs_region(self, region_idx: int):
        """刪除指定的DFS區域"""
        if not self.dfs_regions or region_idx < 0 or region_idx >= len(self.dfs_regions):
            QMessageBox.warning(self, "警告", f"無效的區域索引: {region_idx}")
            return
        
        # 確認刪除
        reply = QMessageBox.question(
            self, "確認刪除",
            f"確定要刪除區域 {region_idx} 嗎？\n"
            f"座標: ({self.dfs_regions[region_idx][0]}, {self.dfs_regions[region_idx][1]}, "
            f"{self.dfs_regions[region_idx][2]}, {self.dfs_regions[region_idx][3]})",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 刪除區域
        removed_region = self.dfs_regions.pop(region_idx)
        self.status_text.append(f"已刪除區域 {region_idx}: ({removed_region[0]}, {removed_region[1]}, {removed_region[2]}, {removed_region[3]})")
        
        # 更新類別中的索引（需要調整所有大於region_idx的索引）
        for category in self.categories:
            # 移除被刪除的索引
            if region_idx in category['regions']:
                category['regions'].remove(region_idx)
            
            # 調整所有大於region_idx的索引（減1）
            adjusted_regions = []
            for idx in category['regions']:
                if idx > region_idx:
                    adjusted_regions.append(idx - 1)
                elif idx < region_idx:
                    adjusted_regions.append(idx)
            category['regions'] = adjusted_regions
        
        # 更新類別清單顯示
        self.update_category_list()
        
        # 更新預覽
        if self.categories:
            self.preview_widget.update_preview_with_categories(
                self.dfs_regions, self.categories, self.selected_category_index
            )
        else:
            # 沒有類別時，直接更新DFS區域顯示
            image_path = self.selected_images[0] if self.selected_images else None
            if image_path:
                self.preview_widget.set_image_with_dfs_regions(image_path, self.dfs_regions)
        
        self.status_text.append(f"剩餘 {len(self.dfs_regions)} 個區域")
        self.statusBar().showMessage(f"已刪除區域 {region_idx}，剩餘 {len(self.dfs_regions)} 個區域")
    
    def assign_regions_to_category(self, bbox: Tuple[int, int, int, int]):
        """將bbox框選到的DFS區域分配到當前選中的類別"""
        if self.selected_category_index < 0 or self.selected_category_index >= len(self.categories):
            print(f"警告: 無效的類別索引 {self.selected_category_index}")
            return
        
        if not self.dfs_regions:
            QMessageBox.warning(self, "警告", "沒有檢測到DFS區域，請先點擊「檢測區域」")
            return
        
        bbox_left, bbox_top, bbox_right, bbox_bottom = bbox
        
        # 找出所有與bbox相交的DFS區域
        # 檢查區域中心點是否在bbox內，或區域與bbox有重疊
        assigned_indices = []
        for idx, (left, top, right, bottom) in enumerate(self.dfs_regions):
            # 計算區域中心點
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            
            # 檢查中心點是否在bbox內，或者區域與bbox有重疊
            if (bbox_left <= center_x <= bbox_right and 
                bbox_top <= center_y <= bbox_bottom):
                assigned_indices.append(idx)
            # 或者檢查區域是否與bbox有重疊
            elif not (right < bbox_left or left > bbox_right or 
                     bottom < bbox_top or top > bbox_bottom):
                assigned_indices.append(idx)
        
        if not assigned_indices:
            QMessageBox.information(
                self, "提示", 
                f"未框選到任何DFS區域\n\n"
                f"BBox: ({bbox_left}, {bbox_top}, {bbox_right}, {bbox_bottom})\n"
                f"總共有 {len(self.dfs_regions)} 個DFS區域"
            )
            return
        
        # 將區域添加到當前類別（避免重複）
        category = self.categories[self.selected_category_index]
        added_count = 0
        for idx in assigned_indices:
            if idx not in category['regions']:
                category['regions'].append(idx)
                added_count += 1
        
        # 更新顯示
        self.update_category_list()
        self.preview_widget.update_preview_with_categories(
            self.dfs_regions, self.categories, self.selected_category_index
        )
        
        self.statusBar().showMessage(
            f"已將 {added_count} 個區域分配到類別「{category['name']}」"
        )

    def on_classification_changed(self, index: int):
        """分類依據改變"""
        mapping = {
            0: "none",
            1: "fish",
            2: "feed",
            3: "monster",
            4: "pet",
        }
        self.classify_basis = mapping.get(index, "none")
        # 魚分類：依來源圖片同級目錄輸出，不強制要求使用者選擇 output_dir
        if self.classify_basis == "fish" and self.selected_images:
            src_dir = self.selected_images[0].parent
            self.output_dir = src_dir
            if hasattr(self, "output_label"):
                self.output_label.setText(f"輸出: {src_dir}（魚行為分類）")
    
    def on_dfs_params_changed(self):
        """DFS 參數改變時重新檢測"""
        if self.selected_images:
            self.detect_dfs_regions()
    
    def detect_dfs_regions(self):
        """使用 DFS 算法檢測區域"""
        if not self.selected_images:
            QMessageBox.warning(self, "警告", "請先選擇圖片")
            return
        
        try:
            import sys
            from pathlib import Path
            tools_dir = Path(__file__).parent
            if str(tools_dir) not in sys.path:
                sys.path.insert(0, str(tools_dir))
            from alpha_dfs_crop import AlphaDFSCropper
            
            image_path = self.selected_images[0]
            image = Image.open(image_path)
            
            # 顯示檢測中訊息
            self.status_text.append(f"正在檢測區域: {image_path.name}...")
            self.status_text.append(f"圖片模式: {image.mode}, 尺寸: {image.size}")
            
            cropper = AlphaDFSCropper(
                min_region_size=self.min_size_spin.value(),
                alpha_threshold=self.alpha_threshold_spin.value(),
                padding=self.padding_spin.value(),
                split_sensitivity=self.split_sensitivity_spin.value()
            )
            
            regions = cropper.detect_regions(image)
            
            # 按照由左往右的順序排序（依左邊界 x 座標）
            if not regions:
                self.dfs_regions = []
            else:
                self.dfs_regions = sorted(regions, key=lambda r: r[0])  # 按 left 由左往右
            
            self.status_text.append(f"檢測完成！找到 {len(self.dfs_regions)} 個區域")
            
            if len(self.dfs_regions) == 0:
                QMessageBox.information(
                    self, "提示",
                    f"未檢測到任何區域。\n\n"
                    f"可能原因：\n"
                    f"1. 圖片沒有透明通道（Alpha）\n"
                    f"2. 最小區域大小設定過大（目前: {self.min_size_spin.value()}）\n"
                    f"3. Alpha 閾值設定過高（目前: {self.alpha_threshold_spin.value()}）\n\n"
                    f"建議：\n"
                    f"- 嘗試降低「最小區域大小」\n"
                    f"- 檢查圖片是否有透明背景"
                )
                # 即使沒有檢測到區域，也顯示原圖
                self.preview_widget.set_image(image_path)
                # 清空類別
                self.categories = []
                self.selected_category_index = -1
                self.update_category_list()
            else:
                # 更新預覽（如果有類別則顯示類別，否則顯示原始DFS區域）
                if self.categories:
                    # 確保預覽組件有原始圖片
                    if not self.preview_widget.original_image:
                        self.preview_widget.set_image(image_path)
                    self.preview_widget.update_preview_with_categories(
                        self.dfs_regions, self.categories, self.selected_category_index
                    )
                else:
                    self.preview_widget.set_image_with_dfs_regions(image_path, self.dfs_regions)
            
            # 更新資訊顯示
            if self.preview_widget.original_image:
                img = self.preview_widget.original_image
                self.image_info.setText(
                    f"檔案: {image_path.name}\n"
                    f"尺寸: {img.width} x {img.height} 像素\n"
                    f"格式: {img.format}\n"
                    f"檢測到 {len(self.dfs_regions)} 個區域"
                )
        except Exception as e:
            error_msg = f"DFS 檢測失敗: {str(e)}"
            self.status_text.append(f"錯誤: {error_msg}")
            import traceback
            self.status_text.append(traceback.format_exc())
            QMessageBox.warning(self, "錯誤", error_msg)
    
    def load_folder_structure(self):
        """載入資料夾結構"""
        self.folder_tree.clear()
        
        if not self.resource_dir.exists():
            self.statusBar().showMessage(f"資源目錄不存在: {self.resource_dir}")
            return
        
        # 創建根節點
        root_item = QTreeWidgetItem(self.folder_tree, [str(self.resource_dir)])
        root_item.setData(0, Qt.ItemDataRole.UserRole, self.resource_dir)
        
        # 遞迴載入子目錄和文件
        self.add_tree_items(root_item, self.resource_dir)
        
        # 展開根節點
        root_item.setExpanded(True)
        
        self.statusBar().showMessage(f"已載入: {self.resource_dir}")
    
    def add_tree_items(self, parent_item: QTreeWidgetItem, path: Path):
        """遞迴添加樹狀項目"""
        try:
            # 先添加目錄
            dirs = sorted([d for d in path.iterdir() if d.is_dir()])
            for dir_path in dirs:
                dir_item = QTreeWidgetItem(parent_item, [dir_path.name])
                dir_item.setData(0, Qt.ItemDataRole.UserRole, dir_path)
                dir_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_DirIcon))
                self.add_tree_items(dir_item, dir_path)
            
            # 再添加圖片文件
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif'}
            images = sorted([f for f in path.iterdir() 
                           if f.is_file() and f.suffix.lower() in image_extensions])
            
            for img_path in images:
                img_item = QTreeWidgetItem(parent_item, [img_path.name])
                img_item.setData(0, Qt.ItemDataRole.UserRole, img_path)
                img_item.setIcon(0, self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
                
                # 檢查是否已處理（檢查輸出目錄）
                base_name = img_path.stem
                output_files = []
                # 1) 魚分類輸出：在同級目錄的 7 個資料夾內有 base_name_XXX.png
                for folder in FISH_BEHAVIOR_FOLDERS:
                    output_files.extend(list((img_path.parent / folder).glob(f"{base_name}_*.png")))
                # 2) 一般輸出：base_name_sprite_XXX.png
                if self.output_dir and self.output_dir.exists():
                    output_files.extend(list(self.output_dir.glob(f"{base_name}_sprite_*.png")))
                if output_files:
                    img_item.setForeground(0, QColor(100, 200, 100))  # 綠色表示已處理
        except PermissionError:
            pass
    
    def on_item_selected(self):
        """處理項目選擇"""
        try:
            selected_items = self.folder_tree.selectedItems()
            self.selected_images = []
            
            for item in selected_items:
                path = item.data(0, Qt.ItemDataRole.UserRole)
                if path and isinstance(path, Path) and path.is_file():
                    self.selected_images.append(path)
            
            if self.selected_images:
                # 清空之前的類別和區域（切換圖片時）
                self.categories = []
                self.selected_category_index = -1
                self.dfs_regions = []
                self.update_category_list()
                self.preview_widget.set_selection_mode(False)
                
                # 魚分類：預設輸出到來源圖片同級目錄
                if self.classify_basis == "fish":
                    self.output_dir = self.selected_images[0].parent
                    if hasattr(self, "output_label"):
                        self.output_label.setText(f"輸出: {self.output_dir}（魚行為分類）")
                self.selection_info.setText(f"已選擇 {len(self.selected_images)} 個圖片")
                self.load_preview_image(self.selected_images[0])
                # 自動檢測區域
                self.detect_dfs_regions()
            else:
                self.selection_info.setText("未選擇任何圖片")
                self.preview_widget.original_image = None
                self.preview_widget.pixmap = None
                self.preview_widget.preview_label.clear()
                self.preview_widget.preview_label.setText("請在左側選擇圖片")
                self.image_info.setText("未載入圖片")
        except Exception as e:
            error_msg = f"選擇項目時發生錯誤: {str(e)}"
            print(f"錯誤: {error_msg}")
            import traceback
            traceback.print_exc()
            try:
                QMessageBox.warning(self, "錯誤", error_msg)
            except:
                print("無法顯示錯誤對話框")
    
    def load_preview_image(self, image_path: Path):
        """載入預覽圖片"""
        try:
            # DFS 模式：載入圖片
            self.preview_widget.set_image(image_path)
            if self.preview_widget.original_image:
                img = self.preview_widget.original_image
                self.image_info.setText(
                    f"檔案: {image_path.name}\n"
                    f"尺寸: {img.width} x {img.height} 像素\n"
                    f"格式: {img.format}"
                )
            else:
                self.image_info.setText(f"無法載入圖片: {image_path.name}")
        except Exception as e:
            error_msg = f"載入預覽圖片時發生錯誤: {str(e)}"
            print(f"錯誤: {error_msg}")
            import traceback
            traceback.print_exc()
            self.image_info.setText(f"錯誤: 無法載入圖片")
            try:
                QMessageBox.warning(self, "錯誤", error_msg)
            except:
                print("無法顯示錯誤對話框")
    
    def select_output_dir(self):
        """選擇輸出目錄"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "選擇輸出目錄", str(Path.cwd())
        )
        if dir_path:
            self.output_dir = Path(dir_path)
            self.output_label.setText(f"輸出: {self.output_dir}")
            self.statusBar().showMessage(f"輸出目錄: {self.output_dir}")
            # 重新載入資料夾結構以更新處理狀態
            self.load_folder_structure()
    
    def start_cropping(self):
        """開始裁切"""
        if not self.selected_images:
            QMessageBox.warning(self, "警告", "請先選擇要裁切的圖片")
            return
        
        # 檢查是否有自定義類別
        use_custom_categories = len(self.categories) > 0
        
        if use_custom_categories:
            # 自定義類別模式：輸出到來源圖片同級目錄，不需要選擇輸出目錄
            pass
        elif self.classify_basis == "fish":
            # 魚分類預設輸出到來源圖片同級目錄，不強制要求選擇輸出目錄
            self.output_dir = self.selected_images[0].parent
            if hasattr(self, "output_label"):
                self.output_label.setText(f"輸出: {self.output_dir}（魚行為分類）")
        else:
            if not self.output_dir:
                QMessageBox.warning(self, "警告", "請先選擇輸出目錄")
                return
        
        # 使用 DFS 模式裁切
        self.start_dfs_cropping()
    
    def start_dfs_cropping(self):
        """開始 DFS 自動裁切"""
        if not self.dfs_regions:
            QMessageBox.warning(self, "警告", "請先點擊「檢測區域」按鈕")
            return
        
        # 檢查是否有自定義類別
        use_custom_categories = len(self.categories) > 0
        
        if use_custom_categories:
            # 檢查是否有未分配的區域
            assigned_indices = set()
            for category in self.categories:
                assigned_indices.update(category['regions'])
            unassigned_count = len(self.dfs_regions) - len(assigned_indices)
            
            if unassigned_count > 0:
                reply = QMessageBox.question(
                    self, "提示",
                    f"有 {unassigned_count} 個區域未分配到任何類別，\n"
                    f"這些區域將不會被裁切。\n\n"
                    f"確定要繼續嗎？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # 確認對話框（輸出到來源圖片同級目錄）
            output_base_dir = self.selected_images[0].parent if self.selected_images else self.output_dir
            category_info = "\n".join([f"  - {cat['name']}: {len(cat['regions'])} 個區域" 
                                      for cat in self.categories])
            reply = QMessageBox.question(
                self, "確認",
                f"將裁切 {len(self.selected_images)} 個圖片\n"
                f"算法: DFS 自動檢測\n"
                f"檢測到 {len(self.dfs_regions)} 個區域\n"
                f"使用自定義類別:\n{category_info}\n"
                f"輸出到: {output_base_dir}（來源圖片同級目錄）\n\n"
                f"確定要繼續嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        else:
            # 確認對話框（原有邏輯）
            classify_info = ""
            if self.classify_basis == "fish":
                classify_info = f"\n分類: 魚（7 橫排，每排 10 個區域）"
            
            reply = QMessageBox.question(
                self, "確認",
                f"將裁切 {len(self.selected_images)} 個圖片\n"
                f"算法: DFS 自動檢測\n"
                f"檢測到 {len(self.dfs_regions)} 個區域{classify_info}\n"
                f"輸出到: {self.output_dir}\n\n"
                f"確定要繼續嗎？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # 創建輸出目錄（自定義類別模式不需要，會在處理時創建）
        if not use_custom_categories:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 禁用按鈕
        self.crop_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.selected_images))
        self.progress_bar.setValue(0)
        self.status_text.clear()
        self.status_text.append("開始 DFS 裁切...")
        
        # 創建 DFS 工作線程
        import sys
        from pathlib import Path
        tools_dir = Path(__file__).parent
        if str(tools_dir) not in sys.path:
            sys.path.insert(0, str(tools_dir))
        from alpha_dfs_crop import AlphaDFSCropper
        
        total_crops = 0
        for i, img_path in enumerate(self.selected_images):
            try:
                image = Image.open(img_path)
                cropper = AlphaDFSCropper(
                    min_region_size=self.min_size_spin.value(),
                    alpha_threshold=self.alpha_threshold_spin.value(),
                    padding=self.padding_spin.value(),
                    split_sensitivity=self.split_sensitivity_spin.value()
                )
                
                # 檢測區域
                regions = cropper.detect_regions(image)
                
                # 按由左往右排序（與 detect_dfs_regions 一致）
                if regions:
                    regions_sorted = sorted(regions, key=lambda r: r[0])  # 按 left 由左往右
                else:
                    regions_sorted = []
                
                base_name = img_path.stem
                
                # 檢查是否有自定義類別
                use_custom_categories = len(self.categories) > 0
                
                if use_custom_categories:
                    # 自定義類別輸出：按照類別組織輸出
                    # 輸出到來源圖片的同級目錄
                    output_base_dir = img_path.parent
                    
                    # 先建立類別資料夾
                    for category in self.categories:
                        category_dir = output_base_dir / category['name']
                        category_dir.mkdir(parents=True, exist_ok=True)
                    
                    # regions_sorted 已在上面按由左往右排好
                    # 使用self.dfs_regions的索引來對應當前圖片的regions
                    # 因為self.dfs_regions是基於第一張圖片的，而category['regions']存儲的是索引
                    count = 0
                    for category in self.categories:
                        if not category['regions']:
                            continue
                        
                        # 獲取該類別的所有區域
                        # category['regions']存儲的是self.dfs_regions的索引
                        # 我們需要將這些索引對應到當前圖片的regions_sorted
                        category_regions = []
                        for region_idx in category['regions']:
                            # 如果索引在範圍內，使用當前圖片的對應區域
                            if 0 <= region_idx < len(regions_sorted):
                                category_regions.append((region_idx, regions_sorted[region_idx]))
                            # 如果索引超出範圍，嘗試使用self.dfs_regions的座標（用於第一張圖片）
                            elif 0 <= region_idx < len(self.dfs_regions):
                                # 對於第一張圖片，直接使用self.dfs_regions
                                if i == 0:
                                    category_regions.append((region_idx, self.dfs_regions[region_idx]))
                        
                        # 按照由左往右排序
                        category_regions.sort(key=lambda x: x[1][0])  # 按 left
                        
                        # 裁切並保存
                        category_dir = output_base_dir / category['name']
                        for order, (region_idx, (left, top, right, bottom)) in enumerate(category_regions):
                            try:
                                cropped = image.crop((left, top, right, bottom))
                                output_filename = f"{base_name}_{order:03d}.png"
                                output_path = category_dir / output_filename
                                cropped.save(output_path, "PNG")
                                count += 1
                            except Exception as e:
                                self.status_text.append(
                                    f"警告: 無法裁切類別「{category['name']}」的區域 {region_idx}: {e}"
                                )
                    
                    total_crops += count
                    self.progress_bar.setValue(i + 1)
                    category_names = ", ".join([cat['name'] for cat in self.categories])
                    self.status_text.append(
                        f"處理 {img_path.name}: {count} 個區域（類別: {category_names}）"
                    )
                elif self.classify_basis == "fish":
                    # 魚分類：依橫排分類，需先將區域分組成行
                    root_dir = img_path.parent
                    if regions_sorted:
                        avg_height = sum(r[3] - r[1] for r in regions_sorted) / len(regions_sorted)
                        row_tolerance = avg_height * 0.3
                        regions_by_top = sorted(regions_sorted, key=lambda r: r[1])
                        rows = []
                        current_row = [regions_by_top[0]]
                        current_top = regions_by_top[0][1]
                        for region in regions_by_top[1:]:
                            if abs(region[1] - current_top) <= row_tolerance:
                                current_row.append(region)
                            else:
                                current_row.sort(key=lambda r: r[0])
                                rows.append(current_row)
                                current_row = [region]
                                current_top = region[1]
                        current_row.sort(key=lambda r: r[0])
                        rows.append(current_row)
                    else:
                        rows = []
                    
                    # 計算所有區域的平均尺寸（用於logo檢測）
                    all_regions_flat = list(regions_sorted) if regions_sorted else []
                    avg_width = sum(r[2] - r[0] for r in all_regions_flat) / len(all_regions_flat) if all_regions_flat else 0
                    avg_height = sum(r[3] - r[1] for r in all_regions_flat) / len(all_regions_flat) if all_regions_flat else 0
                    
                    # 計算需要多少個資料夾（每行一個，最多7個）
                    num_rows_to_process = min(len(rows), len(FISH_BEHAVIOR_FOLDERS))
                    
                    # 先建立資料夾
                    for folder_idx in range(num_rows_to_process):
                        (root_dir / FISH_BEHAVIOR_FOLDERS[folder_idx]).mkdir(parents=True, exist_ok=True)
                    
                    # 處理所有行，但排除logo區域
                    count = 0
                    for row_idx in range(len(rows)):
                        row_regions = rows[row_idx]
                        
                        # 如果超過7行，使用最後一個資料夾（第7個）
                        if row_idx >= len(FISH_BEHAVIOR_FOLDERS):
                            behavior_dir = root_dir / FISH_BEHAVIOR_FOLDERS[-1]
                        else:
                            behavior_dir = root_dir / FISH_BEHAVIOR_FOLDERS[row_idx]
                        
                        # 處理該行的區域（每行最多10個）
                        for col_idx in range(min(len(row_regions), 10)):
                            left, top, right, bottom = row_regions[col_idx]
                            
                            # Logo檢測：檢查區域特徵
                            width = right - left
                            height = bottom - top
                            aspect_ratio = width / height if height > 0 else 0
                            
                            # 如果寬高比異常（太寬或太高），可能是文字logo
                            # 或者區域尺寸異常大，也可能是logo
                            is_likely_logo = False
                            if aspect_ratio > 3.0 or aspect_ratio < 0.3:
                                is_likely_logo = True
                            elif width > avg_width * 2.5 or height > avg_height * 2.5:
                                is_likely_logo = True
                            
                            if is_likely_logo:
                                self.status_text.append(f"跳過可能的logo區域（第 {row_idx + 1} 行，第 {col_idx + 1} 個）")
                                continue
                            
                            try:
                                cropped = image.crop((left, top, right, bottom))
                                order = row_idx * 10 + col_idx
                                output_filename = f"{base_name}_{order:03d}.png"
                                output_path = behavior_dir / output_filename
                                cropped.save(output_path, "PNG")
                                count += 1
                            except Exception as e:
                                self.status_text.append(f"警告: 無法裁切區域 {row_idx}-{col_idx}: {e}")
                    
                    total_crops += count
                    self.progress_bar.setValue(i + 1)
                    self.status_text.append(f"處理 {img_path.name}: {count} 個區域（魚分類，共 {len(rows)} 行）")
                else:
                    # 一般輸出：不分類，使用已按由左往右排序的區域列表
                    count = 0
                    for idx, (left, top, right, bottom) in enumerate(regions_sorted):
                        try:
                            cropped = image.crop((left, top, right, bottom))
                            output_filename = f"{base_name}_sprite_{idx:03d}.png"
                            output_path = self.output_dir / output_filename
                            cropped.save(output_path, "PNG")
                            count += 1
                        except Exception as e:
                            self.status_text.append(f"警告: 無法裁切區域 {idx}: {e}")
                    total_crops += count
                    self.progress_bar.setValue(i + 1)
                    self.status_text.append(f"處理 {img_path.name}: {count} 個區域")
            except Exception as e:
                self.status_text.append(f"錯誤: {img_path.name} - {str(e)}")
                import traceback
                self.status_text.append(traceback.format_exc())
        
        self.on_crop_finished(total_crops)
    
    def on_crop_finished(self, total_crops):
        """處理裁切完成"""
        self.progress_bar.setVisible(False)
        self.crop_btn.setEnabled(True)
        self.status_text.append(f"\n完成！總共生成 {total_crops} 個裁切圖片")
        self.statusBar().showMessage(f"裁切完成: {total_crops} 個圖片")
        
        QMessageBox.information(
            self, "完成",
            f"裁切完成！\n總共生成 {total_crops} 個裁切圖片\n"
            f"輸出目錄: {self.output_dir}"
        )
        
        # 重新載入資料夾結構以更新狀態
        self.load_folder_structure()


def main():
    # 設置全局異常處理
    def exception_hook(exctype, value, traceback_obj):
        """捕獲未處理的異常"""
        import traceback
        error_msg = ''.join(traceback.format_exception(exctype, value, traceback_obj))
        print("=" * 60)
        print("未捕獲的異常:")
        print(error_msg)
        print("=" * 60)
        
        # 如果有 QApplication 實例，顯示錯誤對話框
        app = QApplication.instance()
        if app:
            try:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle("錯誤")
                msg.setText(f"發生未預期的錯誤:\n{str(value)}")
                msg.setDetailedText(error_msg)
                msg.exec()
            except Exception as e:
                print(f"無法顯示錯誤對話框: {e}")
        else:
            print("QApplication 實例不存在，直接退出")
            # 不要直接退出，讓程序繼續運行
            # sys.exit(1)
    
    sys.excepthook = exception_hook
    
    app = QApplication(sys.argv)
    try:
        app.setStyle('Fusion')
    except Exception:
        pass
    
    try:
        window = ImageCutterGUI()
        window.show()
        window.raise_()
        window.activateWindow()
        window.setWindowState(Qt.WindowState.WindowActive)
        exit_code = app.exec()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"啟動應用程式時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        try:
            QMessageBox.critical(None, "嚴重錯誤", f"無法啟動應用程式:\n{str(e)}")
        except:
            print("無法顯示錯誤對話框")
        # 不要直接退出，讓用戶看到錯誤
        # sys.exit(1)


if __name__ == '__main__':
    main()
