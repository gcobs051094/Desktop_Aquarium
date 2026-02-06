# Change: Add Image Cutter GUI Tool

## Why
需要一個圖形化介面來簡化圖片裁切工具的使用，提供視覺化的參數設定、圖片預覽和資料夾結構管理，避免在處理多個圖片時發生資料混淆。

## What Changes
- 新增 PyQt6 圖形化介面工具
- 提供圖片預覽功能，顯示原圖和裁切區域
- 提供參數設定介面（滑窗長寬、跨步步長）
- 實現資料夾結構的可視化顯示
- 支援分類管理和載入狀態顯示
- 整合現有的命令行裁切功能到 GUI

## Impact
- **修改能力**：圖片處理工具（image-processing）
- **受影響的代碼**：新增 GUI 工具文件 `tools/image_cutter_gui.py`
- **受影響的目錄**：`tools/` 目錄
