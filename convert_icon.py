#!/usr/bin/env python3
"""
將PNG圖片轉換為ICO格式（包含多種尺寸）
用於Windows應用程式圖標
"""
from PIL import Image
from pathlib import Path

def convert_png_to_ico(png_path: str, ico_path: str, sizes: list = None):
    """
    將PNG圖片轉換為ICO格式
    
    Args:
        png_path: PNG圖片路徑
        ico_path: 輸出的ICO文件路徑
        sizes: ICO文件中包含的尺寸列表，預設為 [16, 32, 48, 64, 128, 256]
    """
    if sizes is None:
        sizes = [16, 32, 48, 64, 128, 256]
    
    # 載入原始PNG圖片
    img = Image.open(png_path)
    
    # 創建多尺寸圖標列表
    icon_images = []
    for size in sizes:
        # 調整圖片大小並保持透明通道
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        icon_images.append(resized)
    
    # 儲存為ICO格式
    icon_images[0].save(
        ico_path,
        format='ICO',
        sizes=[(size, size) for size in sizes]
    )
    print(f"✓ 成功將 {png_path} 轉換為 {ico_path}")
    print(f"  包含尺寸: {', '.join(map(str, sizes))}x{', '.join(map(str, sizes))}")

if __name__ == '__main__':
    import sys
    
    # 如果提供了命令行參數，使用該路徑
    if len(sys.argv) > 1:
        png_path = Path(sys.argv[1])
        if not png_path.exists():
            print(f"錯誤：找不到指定的PNG文件：{png_path}")
            exit(1)
    else:
        # 嘗試從多個可能的位置尋找PNG圖片
        possible_paths = [
            # Cursor workspace assets 目錄
            Path(r"C:\Users\V003479\.cursor\projects\d-Work-File-Project-Desktop-Feeding-Fish\assets\c__Users_V003479_AppData_Roaming_Cursor_User_workspaceStorage_13ac80edf77a81f5110ea4f8497decc9_images___________-removebg-preview_000-77b6e167-9bc1-4732-9cea-b7d4874a5357.png"),
            # 專案根目錄下的常見名稱
            Path(__file__).parent / "icon.png",
            Path(__file__).parent / "betta_icon.png",
            Path(__file__).parent / "gem_betta.png",
            Path(__file__).parent / "寶石鬥魚.png",
            Path(__file__).parent / "betta.png",
        ]
        
        png_path = None
        for path in possible_paths:
            if path.exists():
                png_path = path
                print(f"找到PNG圖片：{path}")
                break
        
        if not png_path:
            print("錯誤：找不到PNG圖片文件")
            print("\n請使用以下方式之一：")
            print("1. 將PNG圖片放在專案根目錄，命名為 icon.png、betta_icon.png 或 gem_betta.png")
            print("2. 使用命令行參數指定圖片路徑：")
            print("   python convert_icon.py <圖片路徑>")
            print("\n可能的圖片位置：")
            for path in possible_paths:
                print(f"  - {path}")
            exit(1)
    
    # 輸出ICO路徑
    ico_path = Path(__file__).parent / "icon.ico"
    
    # 執行轉換
    print(f"\n正在轉換：{png_path} -> {ico_path}")
    convert_png_to_ico(str(png_path), str(ico_path))
    print(f"\n✓ ICO文件已生成：{ico_path}")
    print("現在可以使用 build_exe.bat 進行打包了！")
