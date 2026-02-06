# Change: 投放魚清單改為以魚種資料夾為選單文本

## Why
投放魚清單目前顯示為「魚種名稱 / small 變體名稱」（例如：「guppy / small_guppy」），需進入 `resource/fish/` 子目錄掃描名稱含 "small" 的資料夾。使用者希望清單更簡潔，僅以魚種為選項，不需在選單中暴露子目錄層級。

## What Changes
- **投放魚清單來源**：改為僅列舉 `resource/fish/` 底下的**一層資料夾**（魚種目錄），不再進入子目錄掃描 "small" 變體。
- **選單顯示**：清單項目僅顯示魚種資料夾名稱（例如：「guppy」、「puppy」），不再顯示「guppy / small_guppy」格式。
- **新增魚邏輯**：選擇魚種後傳入魚種目錄路徑（例如 `resource/fish/guppy`）；`add_one_fish()` 接受魚種目錄或階段目錄，若為魚種目錄則自動在該目錄下解析出名稱含 "small" 的子目錄並載入動畫後新增魚。

## Impact
- **受影響能力**：水族箱使用者介面（aquarium-ui）
- **受影響代碼**：`aquarium_window.py` 之 `_list_small_fish()`、`add_one_fish()`
- **向後相容**：`add_one_fish()` 仍接受階段目錄路徑（如 `resource/fish/guppy/small_guppy`），僅新增對魚種目錄的解析行為。
