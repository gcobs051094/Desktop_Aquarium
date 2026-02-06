# Change: Add Alpha Channel DFS Auto-Crop Algorithm

## Why
目前的滑窗裁切方法需要手動設定滑窗大小和步長，對於不規則排列的雪碧圖不夠智能。基於 Alpha 通道的 DFS 演算法可以自動檢測每個精靈圖的邊界，無需手動參數設定，提高裁切效率和準確性。

## What Changes
- 新增基於 Alpha 通道的 DFS（深度優先搜尋）演算法
- 自動檢測非透明連續區域（每個精靈圖）
- 計算每個區域的邊界框（bounding box）
- 更新 GUI 工具支援算法選擇（滑窗 vs DFS）
- 保留原有滑窗方法作為備選

## Impact
- **修改能力**：圖片處理工具（image-processing）
- **受影響的代碼**：
  - 新增 `tools/alpha_dfs_crop.py` - DFS 算法實現
  - 修改 `tools/image_cutter_gui.py` - 添加算法選擇
  - 修改 `tools/image_sliding_window.py` - 整合 DFS 功能
- **受影響的目錄**：`tools/` 目錄
