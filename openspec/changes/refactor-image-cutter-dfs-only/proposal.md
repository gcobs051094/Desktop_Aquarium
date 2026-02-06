# Change: Refactor Image Cutter to DFS-Only Mode

## Why
使用者已確認不再需要滑窗裁切功能，現在專注於使用 DFS（深度優先搜尋）模式進行自動區域檢測。同時需要將魚的 7 行 10 列分類邏輯整合到 DFS 模式中，以簡化工具使用流程並提高自動化程度。

## What Changes
- **移除滑窗裁切功能**：完全移除滑窗相關的 UI 元素和代碼邏輯
- **簡化算法選擇**：移除算法選擇下拉框，工具僅支援 DFS 模式
- **整合魚分類邏輯**：將魚的 7 行 10 列分類邏輯從滑窗模式遷移到 DFS 模式
- **優化代碼結構**：移除不再使用的 `CropWorker` 類和相關滑窗參數設定
- **更新文件處理狀態檢查**：移除滑窗格式的文件檢查邏輯

## Impact
- **修改能力**：圖片處理工具（image-processing）
- **受影響的代碼**：
  - 修改 `tools/image_cutter_gui.py` - 移除滑窗相關 UI 和邏輯，整合魚分類到 DFS
  - 保留 `tools/alpha_dfs_crop.py` - DFS 算法實現（不變）
  - 保留 `tools/image_sliding_window.py` - CLI 工具保留（GUI 不再使用）
- **受影響的目錄**：`tools/` 目錄
- **BREAKING**：GUI 工具不再支援滑窗裁切模式，現有使用滑窗模式的用戶需要改用 DFS 模式
