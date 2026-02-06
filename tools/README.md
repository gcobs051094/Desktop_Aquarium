# 圖片處理工具

## image_cutter_gui.py

**圖形化介面工具** - 推薦使用！

提供視覺化的圖片裁切工具，包含：
- 📁 資料夾結構樹狀視圖，清晰顯示 resource 目錄結構
- 🖼️ 圖片預覽功能，即時顯示裁切網格
- ⚙️ 參數設定介面（滑窗尺寸、步長）
- ✅ 已處理圖片的可視化標記（綠色顯示）
- 📊 進度顯示和狀態訊息

### 啟動 GUI

```bash
# Windows
python tools/image_cutter_gui.py
# 或直接雙擊
tools\run_gui.bat

# Linux/Mac
python tools/image_cutter_gui.py
# 或
bash tools/run_gui.sh
```

### GUI 使用說明

1. **左側面板**：瀏覽 resource 目錄結構
   - 選擇要裁切的圖片文件
   - 已處理的圖片會顯示為綠色
   - 點擊「重新載入」更新狀態

2. **中間面板**：圖片預覽
   - 顯示選中的圖片
   - 紅色網格顯示裁切區域
   - 調整參數時網格會即時更新

3. **右側面板**：參數設定
   - 設定滑窗寬度和高度
   - 設定 X/Y 方向步長
   - 選擇是否包含部分窗口
   - 選擇輸出目錄
   - 點擊「執行裁切」開始處理

---

## image_sliding_window.py

**命令行工具** - 適合自動化和腳本使用

滑窗圖片裁切工具，用於將雪碧圖（sprite sheet）按照固定的滑窗尺寸進行裁切。

### 功能特點

- 支援固定尺寸的滑窗裁切
- 可配置的步長（stride）參數，支援重疊或間隔裁切
- 批量處理多個圖片文件
- 自動處理圖片邊界情況
- 進度顯示和錯誤處理
- 支援多種圖片格式（PNG, JPG, JPEG, BMP, GIF）

### 安裝依賴

```bash
# 從專案根目錄安裝所有依賴
pip install -r requirements.txt

# 或僅安裝圖片處理工具所需的依賴
pip install Pillow
```

### 使用方法

#### 基本用法

```bash
# 裁切單個圖片，滑窗尺寸 64x64
python tools/image_sliding_window.py -i image.png -o output/ -w 64 -h 64

# 批量處理目錄中的所有圖片
python tools/image_sliding_window.py -i resource/ -o output/ -w 64 -h 64
```

#### 使用自訂步長

```bash
# 步長小於滑窗尺寸，產生重疊的裁切
python tools/image_sliding_window.py -i image.png -o output/ -w 64 -h 64 --stride-x 32 --stride-y 32

# 步長大於滑窗尺寸，產生間隔的裁切
python tools/image_sliding_window.py -i image.png -o output/ -w 64 -h 64 --stride-x 96 --stride-y 96
```

#### 包含部分窗口

```bash
# 不跳過超出邊界的不完整窗口
python tools/image_sliding_window.py -i image.png -o output/ -w 64 -h 64 --include-partial
```

### 參數說明

- `-i, --input`: 輸入圖片文件或目錄路徑（預設: `resource/`）
- `-o, --output`: 輸出目錄路徑（必需）
- `-w, --width`: 滑窗寬度（像素，必需）
- `-h, --height`: 滑窗高度（像素，必需）
- `--stride-x`: X 方向步長（預設等於滑窗寬度）
- `--stride-y`: Y 方向步長（預設等於滑窗高度）
- `--include-partial`: 包含部分窗口（不跳過超出邊界的不完整窗口）

### 輸出文件命名規則

輸出文件命名格式：`原文件名_r行號_c列號.png`

例如：
- `sprite_r000_c000.png` - 第 0 行第 0 列的裁切
- `sprite_r000_c001.png` - 第 0 行第 1 列的裁切
- `sprite_r001_c000.png` - 第 1 行第 0 列的裁切

### 使用範例

假設你有一個 640x448 的雪碧圖，包含 10 列 x 7 行的精靈圖，每個精靈圖約為 64x64：

```bash
# 使用 64x64 的滑窗，步長也是 64x64（無重疊）
python tools/image_sliding_window.py \
  -i resource/small_guppy/sprite.png \
  -o output/cropped/ \
  -w 64 \
  -h 64

# 如果需要重疊裁切（例如步長為 32x32）
python tools/image_sliding_window.py \
  -i resource/small_guppy/sprite.png \
  -o output/cropped/ \
  -w 64 \
  -h 64 \
  --stride-x 32 \
  --stride-y 32
```

### 注意事項

- 預設情況下，工具會跳過超出圖片邊界的不完整窗口
- 使用 `--include-partial` 選項可以保留這些部分窗口
- 輸出目錄如果不存在會自動創建
- 支援遞迴搜尋子目錄中的圖片文件
