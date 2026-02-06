## MODIFIED Requirements

### Requirement: 商店商品卡片布局
商店各tab（魚種、寵物、飼料、工具）的商品卡片 SHALL 使用統一的布局格式。

#### Scenario: 統一卡片布局
- **WHEN** 商店顯示商品卡片
- **THEN** 所有tab使用相同的卡片樣式（背景、圓角、padding）
- **AND** 左側64x64預覽圖、右側資訊區（最大寬度200px）、右側按鈕（寬度80px）
- **AND** 資訊區包含：名稱（黃字14px粗體）、描述（灰字11px）、解鎖/狀態文字（12px）

#### Scenario: 無按鈕項目保留佔位
- **WHEN** 飼料tab顯示無按鈕的飼料（便宜飼料、鯉魚飼料、藥丸等）
- **THEN** 右側保留80px寬度的佔位，保持與有按鈕項目對齊

#### Scenario: 工具tab未解鎖狀態
- **WHEN** 工具tab顯示未解鎖的工具
- **THEN** 顯示禁用按鈕「未解鎖」（與魚種/寵物tab一致）

### Requirement: 商店魚種顯示
商店魚種tab中，孔雀魚的解鎖/購買描述 SHALL 將「angel_鬥魚」顯示為「天使鬥魚」。

#### Scenario: 孔雀魚解鎖描述
- **WHEN** 商店魚種tab顯示孔雀魚
- **AND** 未解鎖
- **THEN** 顯示「解鎖條件：犧牲 5 隻天使鬥魚」（而非「angel_鬥魚」）

#### Scenario: 孔雀魚購買描述
- **WHEN** 商店魚種tab顯示孔雀魚
- **AND** 已解鎖但條件不足
- **THEN** 顯示「需要 1 隻天使鬥魚」（而非「angel_鬥魚」）

### Requirement: 飼料清單顯示
切換飼料選單 SHALL 不重複顯示金條/鑽石。

#### Scenario: 金條/鑽石不重複
- **WHEN** 切換飼料選單顯示
- **THEN** 金條/鑽石僅出現一次（由 `CHEST_FEED_ITEMS` 區塊處理）
- **AND** 不在 `resource/feed/` 掃描清單中重複加入

#### Scenario: 飼料tab顯示金條/鑽石預覽圖
- **WHEN** 商店飼料tab顯示金條/鑽石
- **THEN** 顯示預覽圖（使用 `_get_chest_feed_image_path()` 載入）

### Requirement: 投放魚清單顯示
投放魚清單中，幼鬥魚 SHALL 顯示費用註記。

#### Scenario: 幼鬥魚顯示費用
- **WHEN** 投放魚清單顯示「鬥魚」項目
- **THEN** 顯示為「鬥魚 (花費20$)」
