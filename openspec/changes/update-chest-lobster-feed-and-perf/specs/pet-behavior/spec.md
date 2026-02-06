## ADDED Requirements

### Requirement: 寶箱怪升級產物依等級隨機
寶箱怪 SHALL 依等級（+0 / +1 / +2）決定可產出之產物種類，每次產出時從該等級對應的產物列表中**隨機**選一項產出。+0 只產珍珠；+1 產珍珠或金條（各 50%）；+2 產珍珠或金條或鑽石（各約 1/3）。`ChestMonsterPet` 之 `__init__` 與 `set_level()` SHALL 使用相同之 `_produce_types` 對應（level 0→["珍珠"]，level 1→["珍珠","金條"]，level 2→["珍珠","金條","鑽石"]）。

#### Scenario: 寶箱怪 +0 只產珍珠
- **WHEN** 寶箱怪等級為 0 且產物計時觸發
- **THEN** 產出物為珍珠（100%）

#### Scenario: 寶箱怪 +1 產珍珠或金條隨機
- **WHEN** 寶箱怪等級為 1 且產物計時觸發
- **THEN** 產出物為珍珠或金條其一，隨機選一（各 50%）

#### Scenario: 寶箱怪 +2 產珍珠或金條或鑽石隨機
- **WHEN** 寶箱怪等級為 2 且產物計時觸發
- **THEN** 產出物為珍珠、金條或鑽石其一，隨機選一（各約 1/3）

#### Scenario: 升級後 set_level 與 __init__ 產物一致
- **WHEN** 寶箱怪由等級 1 升級至等級 2（呼叫 `set_level(2)`）
- **THEN** `_produce_types` 為 `["珍珠", "金條", "鑽石"]`，與新建時 `chest_level=2` 一致
