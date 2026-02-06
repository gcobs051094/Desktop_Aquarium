# Tasks: 遊戲狀態儲存與載入系統

## 1. 遊戲狀態管理模組（game_state.py）
- [x] 1.1 創建 `game_state.py` 模組，定義 `GameState` 類別
- [x] 1.2 實作 `get_save_path()`：取得存檔檔案路徑（Windows: `%APPDATA%/Desktop_Feeding_Fish/save.json`）
- [x] 1.3 實作 `load()`：從檔案載入遊戲狀態，處理 JSON 解析錯誤、版本檢查、缺失欄位預設值
- [x] 1.4 實作 `save(state_dict)`：將遊戲狀態寫入檔案，處理寫入錯誤
- [x] 1.5 定義存檔格式版本號常數 `SAVE_FORMAT_VERSION = "1.0.0"`
- [x] 1.6 實作 `get_default_state()`：回傳預設遊戲狀態字典

## 2. 遊戲狀態資料結構定義
- [x] 2.1 定義 `GameState` 資料類別或使用 TypedDict，包含：
  - `version: str`
  - `money: int`
  - `unlocked_species: Dict[str, Dict]`（species -> {max_count_reached, unlocked}）
  - `fishes: List[Dict]`（每條魚的完整狀態）
  - `background_path: Optional[str]`
  - `background_opacity: int`

## 3. 魚類狀態序列化
- [x] 3.1 在 `fish.py` 新增 `to_dict()` 方法：將 Fish 實例轉換為字典
- [x] 3.2 在 `fish.py` 新增 `from_dict()` 類別方法：從字典重建 Fish 實例
- [x] 3.3 確保序列化包含：species, stage, growth_points, position, direction, facing_left 等必要欄位

## 4. 主視窗整合儲存功能
- [x] 4.1 在 `aquarium_window.py` 的 `TransparentAquariumWindow.__init__()` 中載入存檔
- [x] 4.2 實作 `_load_game_state()`：載入存檔並恢復遊戲狀態（魚類、金額、背景等）
- [x] 4.3 實作 `_save_game_state()`：收集當前遊戲狀態並儲存
- [x] 4.4 在 `closeEvent()` 中呼叫 `_save_game_state()` 確保關閉時儲存

## 5. 自動儲存觸發點
- [x] 5.1 在 `add_one_fish()` 後觸發自動儲存
- [x] 5.2 在魚類升級或移除時觸發自動儲存
- [x] 5.3 在 `on_aquarium_clicked()` 中拾取金錢後觸發自動儲存
- [x] 5.4 在背景或透明度變更時觸發自動儲存（可選）

## 6. 解鎖狀態追蹤
- [x] 6.1 在 `TransparentAquariumWindow` 新增 `_unlocked_species` 字典追蹤解鎖狀態
- [x] 6.2 實作 `_update_unlock_status(species, count)`：更新指定魚種的最大數量記錄
- [x] 6.3 在 `add_one_fish()` 中更新對應魚種的數量統計
- [x] 6.4 在 `_remove_fish()` 或魚類升級時更新數量統計（確保追蹤當前水族箱內的魚種數量）
- [x] 6.5 實作 `_get_fish_count_by_species()`：統計各魚種當前數量
- [x] 6.6 在儲存時將解鎖狀態寫入存檔

## 7. 版本相容性處理
- [x] 7.1 在 `load()` 中檢查存檔版本號
- [x] 7.2 實作版本遷移邏輯（目前為空，未來可擴展）
- [x] 7.3 確保未知欄位被忽略，缺失欄位使用預設值
- [ ] 7.4 測試舊版本存檔在新版本中的載入（模擬測試）

## 8. 錯誤處理與日誌
- [x] 8.1 載入失敗時使用預設狀態，不中斷程式啟動
- [x] 8.2 儲存失敗時記錄錯誤（print 或 logging），不中斷程式運行
- [x] 8.3 驗證 JSON 格式有效性
- [x] 8.4 處理檔案不存在的情況（首次啟動）

## 9. 測試與驗證
- [ ] 9.1 測試基本儲存/載入功能
- [ ] 9.2 測試魚類狀態的完整恢復（位置、方向、成長度等）
- [ ] 9.3 測試解鎖狀態的儲存與載入
- [ ] 9.4 測試存檔損壞時的錯誤處理
- [ ] 9.5 測試版本相容性（模擬舊版本存檔格式）
