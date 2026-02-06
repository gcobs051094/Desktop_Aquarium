# Change: 寶箱怪產物隨機、金條鑽石僅天使鬥魚追食、金錢幀快取、龍蝦解鎖與飼料投食機一致

## Why
1. **寶箱怪產物**：升級後應依等級隨機產出（+0 珍珠、+1 珍珠或金條、+2 珍珠或金條或鑽石），且 `set_level` 需與 `__init__` 一致。
2. **切換飼料清單**：拾取金條/鑽石後，投食機與側邊面板「切換飼料」選單皆須即時顯示金條/鑽石選項。
3. **金條鑽石追逐與進食**：僅天使鬥魚會追、會吃金條與鑽石；其餘魚種與寵物（如拼布魚）不追也不吃。
4. **大便卡頓**：金鬥魚、寶石鬥魚大便時每次重載金錢動畫幀並做邊緣加深，造成卡頓，需快取。
5. **龍蝦解鎖**：龍蝦解鎖條件為曾經獲得 5 隻成年鬥魚，顯示與計算方式須與飼料投食機一致（effective_count = max(total_count_reached, max_count_reached)），並顯示「累計 n 隻」或「目前最多 n 隻」。

## What Changes
- **寶箱怪產物**：+0 只產珍珠；+1 珍珠或金條隨機（各 50%）；+2 珍珠或金條或鑽石隨機（各約 1/3）。`ChestMonsterPet.set_level()` 與 `__init__` 之 `_produce_types` 一致。
- **切換飼料清單**：拾取金條/鑽石後呼叫 `_feed_machine_widget.set_unlocked_feeds()` 同步投食機；面板 `_refresh_feed_menu()` 在遍歷 `_feed_list` 後加入 `CHEST_FEED_ITEMS` 中已解鎖項目（金條/鑽石），使側邊「切換飼料」按鈕之下拉選單也顯示金條/鑽石。
- **金條鑽石僅天使鬥魚**：更新魚類時，僅天使鬥魚（species==鬥魚且 stage==angel）傳入完整 `self.feeds`；其餘魚傳入排除金條/鑽石的飼料列表。寵物更新與寵物–飼料碰撞時，金條/鑽石不傳入、不處理，寵物不吃金條/鑽石。
- **金錢動畫幀快取**：`_load_money_frames(money_type)` 使用模組級快取 `_money_frames_cache`，同一 `money_type` 只載入並做 `_darken_money_edges` 一次，後續大便/寶箱怪產物復用，避免卡頓。
- **龍蝦解鎖**：商店寵物列表顯示龍蝦解鎖條件時，取 `total_count_reached` 與 `max_count_reached`，以 `effective_count = max(total_count, max_count)` 判定是否已解鎖；未解鎖時顯示「曾經獲得 5 隻成年鬥魚（累計 n 隻）」或「目前最多 n 隻」。召喚龍蝦時亦以 `effective_count >= 5` 判定。

## Impact
- Affected specs: pet-behavior, aquarium-ui, fish-behavior, game-economy
- Affected code:
  - `pet.py`：`ChestMonsterPet` 之 `set_level`、類別註解
  - `config.py`：`CHEST_LEVEL` 註解
  - `aquarium_window.py`：拾取金條/鑽石後同步投食機；`_refresh_feed_menu` 加入金條/鑽石；魚與寵物傳入飼料過濾；寵物碰撞跳過金條/鑽石；`_load_money_frames` 快取；龍蝦解鎖顯示與召喚判定（effective_count）
