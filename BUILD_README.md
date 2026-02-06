# 打包說明文件

## 打包工具建議

本專案使用 **PyInstaller** 來打包 Python 應用程式為 Windows exe 文件。

### 為什麼選擇 PyInstaller？

1. ✅ **對 PyQt6 支援最好** - PyInstaller 對 PyQt6 有完整的支援
2. ✅ **資源文件打包** - 可以輕鬆打包 resource 目錄中的所有圖片資源
3. ✅ **單文件打包** - 可以打包成單一 exe 文件，方便分發
4. ✅ **圖標支援** - 支援自訂應用程式圖標
5. ✅ **社群支援** - 最流行的 Python 打包工具，問題容易找到解決方案

## 安裝依賴

首先確保已安裝所有依賴：

```bash
pip install -r requirements.txt
pip install pyinstaller
```

## 設置應用程式圖標

### 步驟 1：準備圖標文件

您已經有寶石鬥魚的 PNG 圖片，需要將其轉換為 ICO 格式：

1. **方法一：使用提供的轉換腳本**
   ```bash
   python convert_icon.py
   ```
   腳本會自動尋找 PNG 圖片並轉換為 `icon.ico`

2. **方法二：手動轉換**
   - 使用線上工具：https://convertio.co/zh/png-ico/
   - 或使用 ImageMagick：`magick convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico`
   - 建議包含多種尺寸：16x16, 32x32, 48x48, 64x64, 128x128, 256x256

3. **方法三：使用 Python PIL**
   ```python
   from PIL import Image
   img = Image.open('betta.png')
   img.save('icon.ico', format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
   ```

### 步驟 2：放置圖標文件

將轉換好的 `icon.ico` 文件放在專案根目錄（與 `aquarium_window.py` 同一目錄）。

## 打包步驟

### 方法一：使用提供的批次檔（推薦）

直接執行：
```bash
build_exe.bat
```

這個腳本會自動：
1. 檢查並安裝 PyInstaller（如果未安裝）
2. 檢查並轉換圖標文件
3. 清理舊的構建文件
4. 執行打包

### 方法二：手動執行

1. **清理舊文件**（可選）
   ```bash
   rmdir /s /q build dist __pycache__
   ```

2. **執行打包**
   ```bash
   pyinstaller aquarium_window.spec
   ```

3. **或使用命令行參數**（不使用spec文件）
   ```bash
   pyinstaller --name="Desktop_Feeding_Fish" ^
                --onefile ^
                --windowed ^
                --icon=icon.ico ^
                --add-data="resource;resource" ^
                aquarium_window.py
   ```

## 打包結果

打包完成後，可執行文件位於：
```
dist/Desktop_Feeding_Fish.exe
```

## 測試打包結果

1. 進入 `dist` 目錄
2. 雙擊 `Desktop_Feeding_Fish.exe` 運行
3. 檢查：
   - ✅ 應用程式是否能正常啟動
   - ✅ 圖片資源是否正常載入
   - ✅ 功能是否正常運作
   - ✅ 圖標是否正確顯示

## 常見問題

### Q: exe 文件很大？
A: 這是正常的，因為 PyInstaller 會打包 Python 解釋器和所有依賴庫。可以使用 UPX 壓縮（已在 spec 文件中啟用）來減少文件大小。

### Q: 運行時提示缺少模組？
A: 檢查 `aquarium_window.spec` 中的 `hiddenimports` 列表，添加缺少的模組名稱。

### Q: 圖片資源無法載入？
A: 確保 `aquarium_window.spec` 中的 `datas` 包含 `('resource', 'resource')`，這會將整個 resource 目錄打包進去。

### Q: 想要單文件還是文件夾分發？
A: 當前配置為單文件（`--onefile`）。如果希望分發文件夾，可以修改 spec 文件，將 `EXE` 改為 `COLLECT`。

### Q: 防毒軟體誤報？
A: PyInstaller 打包的 exe 有時會被防毒軟體誤報。這是因為打包工具的特性，不是病毒。可以：
- 將 exe 加入防毒軟體白名單
- 使用數位簽章（需要購買證書）
- 向防毒軟體廠商提交誤報報告

## 進階配置

### 修改 spec 文件

如果需要自訂打包選項，編輯 `aquarium_window.spec`：

- **修改輸出文件名**：更改 `name='Desktop_Feeding_Fish'`
- **添加更多資源**：在 `datas` 列表中添加更多元組
- **添加隱藏導入**：在 `hiddenimports` 列表中添加模組名
- **啟用/禁用控制台**：修改 `console=False` 為 `True`（用於調試）

### 分發建議

1. **測試多台電腦**：在不同 Windows 版本上測試
2. **包含說明文件**：提供 README 說明如何使用
3. **版本號**：考慮在應用程式中顯示版本號
4. **更新機制**：考慮添加自動更新功能（可選）

## 其他打包工具（參考）

如果 PyInstaller 不適合，也可以考慮：

- **cx_Freeze**：跨平台，但配置較複雜
- **auto-py-to-exe**：PyInstaller 的 GUI 版本，適合不熟悉命令行的用戶
- **Nuitka**：編譯為機器碼，性能更好但打包時間較長

## 相關資源

- PyInstaller 官方文檔：https://pyinstaller.org/
- PyQt6 打包指南：https://www.riverbankcomputing.com/static/Docs/PyQt6/
