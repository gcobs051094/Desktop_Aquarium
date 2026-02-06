@echo off
chcp 65001 >nul
echo ========================================
echo 水族箱應用程式打包腳本
echo ========================================
echo.

REM 檢查是否安裝了PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [錯誤] 未安裝 PyInstaller
    echo 正在安裝 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [錯誤] PyInstaller 安裝失敗
        pause
        exit /b 1
    )
)

echo [1/3] 檢查圖標文件...
if not exist "icon.ico" (
    echo [警告] 找不到 icon.ico 文件
    echo 正在嘗試從PNG轉換...
    if exist "convert_icon.py" (
        python convert_icon.py
        if errorlevel 1 (
            echo [警告] 圖標轉換失敗，將使用預設圖標
        )
    ) else (
        echo [警告] 找不到 convert_icon.py，將使用預設圖標
    )
)

echo.
echo [2/3] 清理舊的構建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "__pycache__" rmdir /s /q __pycache__

echo.
echo [3/3] 開始打包...
pyinstaller aquarium_window.spec

if errorlevel 1 (
    echo.
    echo [錯誤] 打包失敗！
    pause
    exit /b 1
)

echo.
echo ========================================
echo 打包完成！
echo ========================================
echo.
echo 可執行文件位置: dist\Desktop_Feeding_Fish.exe
echo.
echo 提示：
echo - 如果exe無法運行，請檢查 dist 目錄中是否包含 resource 文件夾
echo - 首次運行可能需要一些時間載入資源
echo.
pause
