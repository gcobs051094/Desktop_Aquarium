# Tasks: 投放魚清單改為以魚種資料夾為選單文本

## 1. 清單列舉邏輯
- [x] 1.1 修改 `_list_small_fish()`：僅列舉 `resource/fish/` 底下一層資料夾（魚種目錄）
- [x] 1.2 清單回傳 (顯示名, 魚種目錄 Path)，顯示名為資料夾名稱（如 guppy、puppy）

## 2. 新增魚邏輯
- [x] 2.1 修改 `add_one_fish(fish_dir)`：接受魚種目錄（resource/fish/{species}/）或階段目錄（resource/fish/{species}/{stage}/）
- [x] 2.2 當傳入魚種目錄時，在該目錄下解析出名稱含 "small" 的子目錄作為實際載入路徑
- [x] 2.3 維持對階段目錄路徑的既有行為（向後相容）
