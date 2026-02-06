#!/usr/bin/env python3
"""
基於 Alpha 通道的 DFS 自動裁切工具

使用深度優先搜尋（DFS）演算法檢測雪碧圖中的非透明連續區域，
自動識別每個精靈圖的邊界並進行裁切。
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional, Set
from PIL import Image
import numpy as np


class AlphaDFSCropper:
    """基於 Alpha 通道的 DFS 裁切器"""
    
    def __init__(self, 
                 min_region_size: int = 100,
                 alpha_threshold: int = 1,
                 padding: int = 0,
                 split_sensitivity: float = 0.3):
        """
        初始化裁切器
        
        Args:
            min_region_size: 最小區域大小（像素數），小於此值的區域會被過濾
            alpha_threshold: Alpha 閾值，大於此值視為非透明
            padding: 邊界框的邊距（像素）
            split_sensitivity: 分割敏感度（0.0-1.0），值越小越容易分割。0.3表示瓶頸寬度需達到區域寬度的30%才會分割
        """
        self.min_region_size = min_region_size
        self.alpha_threshold = alpha_threshold
        self.padding = padding
        self.split_sensitivity = split_sensitivity
    
    def detect_regions(self, image: Image.Image) -> List[Tuple[int, int, int, int]]:
        """
        檢測圖片中的非透明連續區域
        
        Args:
            image: PIL Image 對象（必須有 Alpha 通道）
        
        Returns:
            邊界框列表，每個為 (left, top, right, bottom)
        """
        # 確保圖片有 Alpha 通道
        original_mode = image.mode
        has_alpha = original_mode in ('RGBA', 'LA')
        
        if not has_alpha:
            if image.mode == 'RGB':
                # RGB 轉 RGBA，但需要檢測背景色（通常是白色或特定顏色）
                # 這裡我們假設白色背景應該被視為透明
                image = image.convert('RGBA')
                # 將白色像素設為透明
                data = np.array(image)
                # 檢測白色背景（RGB 值接近 255,255,255）
                white_threshold = 250
                white_mask = (data[:, :, 0] > white_threshold) & \
                            (data[:, :, 1] > white_threshold) & \
                            (data[:, :, 2] > white_threshold)
                data[:, :, 3] = np.where(white_mask, 0, 255)  # 白色設為透明
                image = Image.fromarray(data, 'RGBA')
            elif image.mode == 'L':
                # 灰度圖轉 LA（L + Alpha）
                image = image.convert('LA')
            else:
                # 其他模式轉 RGBA
                image = image.convert('RGBA')
        
        # 提取 Alpha 通道
        if image.mode == 'RGBA':
            alpha = image.split()[3]
        elif image.mode == 'LA':
            alpha = image.split()[1]
        else:
            raise ValueError(f"不支援的圖片模式: {image.mode}")
        
        # 轉為 numpy 數組以便處理
        alpha_array = np.array(alpha)
        height, width = alpha_array.shape
        
        # 創建訪問標記數組
        visited = np.zeros((height, width), dtype=bool)
        
        # 存儲所有檢測到的區域
        regions = []
        
        # 遍歷每個像素
        for y in range(height):
            for x in range(width):
                # 如果像素非透明且未訪問過，開始 DFS
                if alpha_array[y, x] >= self.alpha_threshold and not visited[y, x]:
                    # DFS 搜尋連通區域
                    region_pixels = self._dfs(alpha_array, visited, x, y, width, height)
                    
                    # 如果區域足夠大，嘗試分割（檢測是否包含多個獨立對象）
                    if len(region_pixels) >= self.min_region_size:
                        # 嘗試分割區域
                        split_regions = self._split_region_if_needed(region_pixels, alpha_array, width, height)
                        
                        # 為每個分割後的區域計算邊界框
                        for sub_region_pixels in split_regions:
                            if len(sub_region_pixels) >= self.min_region_size:
                                bbox = self._calculate_bbox(sub_region_pixels, image_width=width, image_height=height)
                                if bbox:
                                    regions.append(bbox)
        
        return regions
    
    def _dfs(self, alpha_array: np.ndarray, visited: np.ndarray,
             start_x: int, start_y: int, width: int, height: int) -> List[Tuple[int, int]]:
        """
        深度優先搜尋連通區域
        
        Returns:
            區域內所有像素的座標列表
        """
        stack = [(start_x, start_y)]
        region_pixels = []
        
        while stack:
            x, y = stack.pop()
            
            # 檢查邊界
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            
            # 檢查是否已訪問或非透明
            if visited[y, x] or alpha_array[y, x] < self.alpha_threshold:
                continue
            
            # 標記為已訪問
            visited[y, x] = True
            region_pixels.append((x, y))
            
            # 檢查四個方向的鄰居（上下左右）
            neighbors = [
                (x, y - 1),  # 上
                (x, y + 1),  # 下
                (x - 1, y),  # 左
                (x + 1, y),  # 右
            ]
            
            for nx, ny in neighbors:
                if (0 <= nx < width and 0 <= ny < height and 
                    not visited[ny, nx] and 
                    alpha_array[ny, nx] >= self.alpha_threshold):
                    stack.append((nx, ny))
        
        return region_pixels
    
    def _split_region_if_needed(self, pixels: List[Tuple[int, int]], 
                                 alpha_array: np.ndarray,
                                 width: int, height: int) -> List[List[Tuple[int, int]]]:
        """
        檢測區域是否包含多個獨立對象，如果是則分割
        
        Args:
            pixels: 區域內像素座標列表
            alpha_array: Alpha通道數組
            width: 圖片寬度
            height: 圖片高度
        
        Returns:
            分割後的像素列表（如果不需要分割，返回包含原列表的列表）
        """
        if len(pixels) < self.min_region_size * 2:
            # 區域太小，不需要分割
            return [pixels]
        
        # 創建一個只包含當前區域的臨時數組
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # 創建區域的像素集合以便快速查找
        pixel_set = set(pixels)
        
        # 方法1: 檢測水平方向的"瓶頸"（狹窄連接）
        # 在區域中間位置掃描水平線，尋找連續的透明或稀疏像素
        center_y = (min_y + max_y) // 2
        bottleneck_threshold = (max_x - min_x) * self.split_sensitivity  # 瓶頸寬度閾值：區域寬度的split_sensitivity倍
        
        # 掃描水平線，尋找可能的瓶頸
        transparent_gaps = []
        current_gap_start = None
        for x in range(min_x, max_x + 1):
            if (x, center_y) not in pixel_set:
                if current_gap_start is None:
                    current_gap_start = x
            else:
                if current_gap_start is not None:
                    gap_width = x - current_gap_start
                    if gap_width >= bottleneck_threshold:
                        transparent_gaps.append((current_gap_start, x))
                    current_gap_start = None
        
        # 如果找到明顯的瓶頸，嘗試分割
        if transparent_gaps:
            # 使用最大的瓶頸進行分割
            best_gap = max(transparent_gaps, key=lambda g: g[1] - g[0])
            split_x = (best_gap[0] + best_gap[1]) // 2
            
            # 分割像素到左右兩部分
            left_pixels = [p for p in pixels if p[0] < split_x]
            right_pixels = [p for p in pixels if p[0] >= split_x]
            
            # 如果兩部分都足夠大，返回分割結果
            if len(left_pixels) >= self.min_region_size and len(right_pixels) >= self.min_region_size:
                return [left_pixels, right_pixels]
        
        # 方法2: 檢測垂直方向的"瓶頸"
        center_x = (min_x + max_x) // 2
        bottleneck_threshold_v = (max_y - min_y) * self.split_sensitivity
        
        transparent_gaps_v = []
        current_gap_start_v = None
        for y in range(min_y, max_y + 1):
            if (center_x, y) not in pixel_set:
                if current_gap_start_v is None:
                    current_gap_start_v = y
            else:
                if current_gap_start_v is not None:
                    gap_height = y - current_gap_start_v
                    if gap_height >= bottleneck_threshold_v:
                        transparent_gaps_v.append((current_gap_start_v, y))
                    current_gap_start_v = None
        
        if transparent_gaps_v:
            best_gap_v = max(transparent_gaps_v, key=lambda g: g[1] - g[0])
            split_y = (best_gap_v[0] + best_gap_v[1]) // 2
            
            top_pixels = [p for p in pixels if p[1] < split_y]
            bottom_pixels = [p for p in pixels if p[1] >= split_y]
            
            if len(top_pixels) >= self.min_region_size and len(bottom_pixels) >= self.min_region_size:
                return [top_pixels, bottom_pixels]
        
        # 方法3: 使用連通組件分析（如果區域很大，可能有未連接的部分）
        # 在區域內重新進行DFS，尋找未連接的子區域
        if len(pixels) > self.min_region_size * 3:
            # 創建區域內的訪問標記
            region_visited = set()
            sub_regions = []
            
            for start_pixel in pixels:
                if start_pixel in region_visited:
                    continue
                
                # 在區域內進行DFS
                stack = [start_pixel]
                sub_region = []
                
                while stack:
                    x, y = stack.pop()
                    if (x, y) in region_visited or (x, y) not in pixel_set:
                        continue
                    
                    region_visited.add((x, y))
                    sub_region.append((x, y))
                    
                    # 檢查四個方向的鄰居（僅在區域內）
                    for nx, ny in [(x, y-1), (x, y+1), (x-1, y), (x+1, y)]:
                        if (nx, ny) in pixel_set and (nx, ny) not in region_visited:
                            stack.append((nx, ny))
                
                if len(sub_region) >= self.min_region_size:
                    sub_regions.append(sub_region)
            
            # 如果找到多個子區域，返回它們
            if len(sub_regions) > 1:
                return sub_regions
        
        # 不需要分割
        return [pixels]
    
    def _calculate_bbox(self, pixels: List[Tuple[int, int]], 
                       padding: Optional[int] = None,
                       image_width: Optional[int] = None,
                       image_height: Optional[int] = None) -> Optional[Tuple[int, int, int, int]]:
        """
        計算區域的邊界框
        
        Args:
            pixels: 區域內像素座標列表
            padding: 邊距（如果為 None，使用 self.padding）
            image_width: 圖片寬度（用於限制右邊界）
            image_height: 圖片高度（用於限制下邊界）
        
        Returns:
            (left, top, right, bottom) 或 None（如果區域為空）
        """
        if not pixels:
            return None
        
        if padding is None:
            padding = self.padding
        
        xs = [p[0] for p in pixels]
        ys = [p[1] for p in pixels]
        
        left = max(0, min(xs) - padding)
        top = max(0, min(ys) - padding)
        right = (max(xs) + 1 + padding) if image_width is None else min(image_width, max(xs) + 1 + padding)
        bottom = (max(ys) + 1 + padding) if image_height is None else min(image_height, max(ys) + 1 + padding)
        
        return (left, top, right, bottom)
    
    def crop_image(self, image: Image.Image, 
                   output_dir: Path,
                   base_name: str) -> int:
        """
        檢測並裁切圖片中的所有區域
        
        Args:
            image: 原始圖片
            output_dir: 輸出目錄
            base_name: 輸出文件基礎名稱
        
        Returns:
            成功裁切的區域數量
        """
        # 檢測區域
        regions = self.detect_regions(image)
        
        if not regions:
            return 0
        
        # 按照由上而下、由左而右的順序排序
        # 改進的排序方法：使用區域中心點進行更穩定的排序
        if not regions:
            regions_sorted = []
        else:
            # 計算平均區域高度和寬度，用於判斷是否在同一行
            avg_height = sum(r[3] - r[1] for r in regions) / len(regions)
            avg_width = sum(r[2] - r[0] for r in regions) / len(regions)
            
            # 使用更寬鬆的容差，但基於區域中心點
            row_tolerance = max(avg_height * 0.5, 10)  # 容差：平均高度的50%或至少10像素
            
            # 計算每個區域的中心點
            regions_with_center = []
            for r in regions:
                left, top, right, bottom = r
                center_x = (left + right) / 2
                center_y = (top + bottom) / 2
                regions_with_center.append((r, center_x, center_y))
            
            # 按中心點的y座標排序（由上而下）
            regions_with_center.sort(key=lambda x: x[2])  # 按center_y排序
            
            # 分組到行（基於中心點的y座標）
            rows = []
            current_row = [regions_with_center[0]]
            current_center_y = regions_with_center[0][2]
            
            for item in regions_with_center[1:]:
                _, center_x, center_y = item
                # 如果中心點的y座標在容差範圍內，視為同一行
                if abs(center_y - current_center_y) <= row_tolerance:
                    current_row.append(item)
                else:
                    # 新的一行，先排序當前行（按中心點的x座標），然後開始新行
                    current_row.sort(key=lambda x: x[1])  # 按center_x排序
                    rows.append([x[0] for x in current_row])  # 只保留bbox
                    current_row = [item]
                    current_center_y = center_y
            
            # 處理最後一行
            if current_row:
                current_row.sort(key=lambda x: x[1])  # 按center_x排序
                rows.append([x[0] for x in current_row])  # 只保留bbox
            
            # 合併所有行
            regions_sorted = []
            for row in rows:
                regions_sorted.extend(row)
        
        # 裁切每個區域
        count = 0
        for idx, (left, top, right, bottom) in enumerate(regions_sorted):
            try:
                # 裁切區域
                cropped = image.crop((left, top, right, bottom))
                
                # 保存文件，使用順序編號（由上而下、由左而右）
                output_filename = f"{base_name}_sprite_{idx:03d}.png"
                output_path = output_dir / output_filename
                cropped.save(output_path, "PNG")
                count += 1
            except Exception as e:
                print(f"警告: 無法裁切區域 {idx}: {e}", file=sys.stderr)
        
        return count


def process_image_dfs(input_path: Path,
                      output_dir: Path,
                      min_region_size: int = 100,
                      alpha_threshold: int = 1,
                      padding: int = 0) -> int:
    """
    使用 DFS 算法處理單個圖片
    
    Args:
        input_path: 輸入圖片路徑
        output_dir: 輸出目錄
        min_region_size: 最小區域大小
        alpha_threshold: Alpha 閾值
        padding: 邊距
    
    Returns:
        成功裁切的區域數量
    """
    try:
        image = Image.open(input_path)
        cropper = AlphaDFSCropper(
            min_region_size=min_region_size,
            alpha_threshold=alpha_threshold,
            padding=padding
        )
        
        base_name = input_path.stem
        count = cropper.crop_image(image, output_dir, base_name)
        return count
    except Exception as e:
        print(f"錯誤: 處理 {input_path.name} 時發生錯誤: {e}", file=sys.stderr)
        return 0


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='基於 Alpha 通道的 DFS 自動裁切工具'
    )
    parser.add_argument('-i', '--input', type=str, required=True,
                       help='輸入圖片文件或目錄')
    parser.add_argument('-o', '--output', type=str, required=True,
                       help='輸出目錄')
    parser.add_argument('--min-size', type=int, default=100,
                       help='最小區域大小（像素數，預設: 100）')
    parser.add_argument('--alpha-threshold', type=int, default=1,
                       help='Alpha 閾值（預設: 1）')
    parser.add_argument('--padding', type=int, default=0,
                       help='邊界框邊距（像素，預設: 0）')
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if input_path.is_file():
        count = process_image_dfs(
            input_path, output_dir,
            args.min_size, args.alpha_threshold, args.padding
        )
        print(f"完成！檢測到 {count} 個區域")
    else:
        print("批量處理功能待實現")
