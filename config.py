#!/usr/bin/env python3
def get_fish_speed_range(species: str) -> tuple:
    """依魚種回傳速度範圍 (min, max)。"""
    return FISH_SPEED_BY_SPECIES.get(species, (DEFAULT_FISH_SPEED_MIN, DEFAULT_FISH_SPEED_MAX))


def get_fish_animation_speed(species: str) -> float:
    """依魚種回傳動畫速度。"""
    return FISH_ANIMATION_SPEED_BY_SPECIES.get(species, DEFAULT_FISH_ANIMATION_SPEED)


def get_feed_fall_speed(feed_name: str) -> float:
    """依飼料名稱回傳下落速度。"""
    return FEED_FALL_SPEED.get(feed_name, DEFAULT_FEED_FALL_SPEED)


def get_feed_animation_speed(feed_name: str) -> float:
    """依飼料名稱回傳動畫速度。"""
    return FEED_ANIMATION_SPEED.get(feed_name, DEFAULT_FEED_ANIMATION_SPEED)


def get_money_fall_speed(money_type: str) -> float:
    """依金錢類型回傳下落速度。"""
    return MONEY_FALL_SPEED.get(money_type, DEFAULT_MONEY_FALL_SPEED)


def get_money_animation_speed(money_type: str) -> float:
    """依金錢類型回傳動畫速度。"""
    return MONEY_ANIMATION_SPEED.get(money_type, DEFAULT_MONEY_ANIMATION_SPEED)


def get_material_speed(key: str) -> float:
    """依素材鍵回傳移動速度（供後續擴充用）。"""
    return MATERIAL_SPEED_BY_KEY.get(key, DEFAULT_MATERIAL_SPEED)


def get_feed_counter_interval_sec(feed_name: str):
    """依飼料名稱回傳計時器間隔秒數（解鎖後每隔幾秒數量+1）；None 表示無限投餵不計數。"""
    return FEED_COUNTER_INTERVAL_SEC.get(feed_name)


"""
遊戲設定檔

定義飼料成長度、升級閾值等遊戲參數。
"""

# ---------------------------------------------------------------------------
# 金錢：初始金錢與產物價值
# ---------------------------------------------------------------------------
# 新遊戲或無存檔時的初始金錢（單位：$）
INITIAL_MONEY = 100

# 飼料成長度對應表（金條、鑽石為 0：僅天使鬥魚吃後變身，不累積成長度）
FEED_GROWTH_POINTS = {
    "便宜飼料": 2,
    "鯉魚飼料": 5,
    "藥丸": 10,
    "核廢料": 1,
    "金條": 0,
    "鑽石": 0,
}

# 魚種升級閾值（成長度達到此值時升級）
FISH_UPGRADE_THRESHOLDS = {
    "鬥魚": {
        "small": 50,   # small -> medium 需要 10 成長度
        "medium": 150,  # medium -> large 需要 30 成長度
        "large": 300,  # large -> angel 需要 100 成長度
    },
    # 可以在這裡添加其他魚種的升級閾值
    # "goldfish": {
    #     "small": 15,
    #     "medium": 35,
    # },
}

# 鬥魚大便行為：各階段鬥魚每隔一段時間會排出金錢類素材
# 格式: "階段_魚種" -> (money 素材目錄名, (最小間隔秒數, 最大間隔秒數))
# 每次大便後會隨機選擇一個範圍內的間隔時間，避免同時大便造成卡頓
BETTA_POOP_CONFIG = {
    "small_鬥魚": ("銅幣", (15, 20)),      # 幼鬥魚：銅幣，每 5~10 秒
    "medium_鬥魚": ("銀幣", (20, 25)),    # 中鬥魚：銀幣，每 10~15 秒
    "large_鬥魚": ("金幣", (35, 40)),     # 成年鬥魚：金幣，每 15~20 秒
    "angel_鬥魚": ("金心幣", (40, 50)),   # 天使鬥魚：金心幣，每 25~30 秒
    "golden_鬥魚": ("金錐體", (50, 60)),  # 金鬥魚：金錐體，每 50~60 秒
    "gem_鬥魚": ("藍寶石", (50, 60)),     # 寶石鬥魚：藍寶石，每 50~60 秒
}

# 金錢類素材價值（點擊拾取時增加的金額，單位：$）
# 鍵名需與 resource/money/ 目錄名稱一致
MONEY_VALUE = {
    "銅幣": 5,
    "銀幣": 10,
    "金幣": 15,
    "金心幣": 30,
    "珍珠": 50,
    "金條": 70,
    "鑽石": 70,
    "魚翅": 100,
    "金錐體": 120,
    "藍寶石": 120,
}

# 各飼料計時器秒數（解鎖後每隔幾秒數量+1；None 表示無限投餵不計數）
FEED_COUNTER_INTERVAL_SEC = {
    "便宜飼料": None,
    "鯉魚飼料": 3,
    "藥丸": 5,
    "核廢料": 60,
    "金條": None,
    "鑽石": None,
}

# 飼料解鎖與數量計數器配置（待解鎖的飼料不會出現在切換飼料選單）
# unlock_by: "always" | "feed_cheap_count" | "large_betta_count" | "sacrifice_medium_betta"
# unlock_value: 解鎖所需數值（feed_cheap_count 次數、large_鬥魚 隻數等）
# counter_interval_sec: 由 FEED_COUNTER_INTERVAL_SEC 對應，解鎖後每隔幾秒數量+1
FEED_UNLOCK_CONFIG = {
    "便宜飼料": {"unlock_by": "always", "counter_interval_sec": FEED_COUNTER_INTERVAL_SEC["便宜飼料"]},
    "鯉魚飼料": {"unlock_by": "feed_cheap_count", "unlock_value": 100, "counter_interval_sec": FEED_COUNTER_INTERVAL_SEC["鯉魚飼料"]},
    "藥丸": {"unlock_by": "large_betta_count", "unlock_value": 10, "counter_interval_sec": FEED_COUNTER_INTERVAL_SEC["藥丸"]},
    "核廢料": {"unlock_by": "sacrifice_medium_betta", "unlock_value": 6, "counter_interval_sec": FEED_COUNTER_INTERVAL_SEC["核廢料"]},
    "金條": {"unlock_by": "chest_feed_count", "counter_interval_sec": None},
    "鑽石": {"unlock_by": "chest_feed_count", "counter_interval_sec": None},
}

# 投放魚費用
SMALL_BETTA_COST = 20  # 投放一隻幼鬥魚的費用（金幣）

# 飼料投餵費用（單位：$）
FEED_COST = {
    "便宜飼料": 2,
    # 其他飼料不需要費用（使用計數器系統）
}

# 孔雀魚行為：每5秒追最近的金錢，碰觸後60%機率轉換為石榴結晶（紅色色調）
GUPPY_MONEY_CHASE_INTERVAL_SEC = 5.0
GUPPY_MONEY_TRANSFORM_CHANCE = 1.0
GUPPY_MONEY_CHASE_SPEED_MULTIPLIER = 2.5  # 孔雀魚追金錢時的速度倍率（比追飼料更快）
GUPPY_MONEY_COOLDOWN_SEC = 5.0  # 孔雀魚碰觸金錢並產生石榴結晶後的冷卻時間（秒）

# 鯊魚：每 300 秒可吃一隻幼年鬥魚，吃過後 300 秒內每 30 秒大便魚翅
SHARK_EAT_BETTA_INTERVAL_SEC = 300
SHARK_POOP_INTERVAL_SEC = 30
SHARK_POOP_DURATION_SEC = 300

# 核廢料：僅鬥魚魚種會吃（寵物類都不吃）；進食後 80% 死亡、20% 複製
NUCLEAR_DEATH_CHANCE = 0.8

# 魚死亡／移除動畫：淡出上移的持續時間（秒），結束後從列表移除
FISH_DEATH_ANIMATION_DURATION_SEC = 5.0

# 金錢類物品與寶箱怪產物消失動畫配置
MONEY_COLLECT_ANIMATION_DURATION_SEC = 0.2  # 消失動畫持續時間（秒）
MONEY_COLLECT_ANIMATION_SPEED_MULTIPLIER = 5.0  # 消失動畫期間動畫加速倍率（金錢類物品有動畫時）
MONEY_COLLECT_VELOCITY_Y = -2.0  # 消失動畫往上移動速度（像素/幀，負值表示往上）

# 魚的成長階段順序
GROWTH_STAGES = ["small", "medium", "large", "angel"]

# ---------------------------------------------------------------------------
# 魚種動畫行為（游泳、轉向、吃飯的目錄名）
# ---------------------------------------------------------------------------
# 鬥魚、鯊魚、孔雀魚使用相同行為：5_吃飽游泳、7_吃飽轉向、6_吃飽吃。
# 可依魚種覆寫（鍵為魚種目錄名，如 "鬥魚"、"鯊魚"、"孔雀魚"）。
DEFAULT_FISH_SWIM_BEHAVIOR = "5_吃飽游泳"
DEFAULT_FISH_TURN_BEHAVIOR = "7_吃飽轉向"
DEFAULT_FISH_EAT_BEHAVIOR = "6_吃飽吃"
FISH_BEHAVIOR_BY_SPECIES = {
    # 孔雀魚與鬥魚、鯊魚使用相同行為（預設），無需覆寫
    # 若某魚種使用不同目錄名可在此設定，例如：
    # "某魚種": {"swim": "1_游動", "turn": "2_轉向", "eat": "6_吃飽吃"},
}


def get_fish_behaviors(species: str) -> tuple:
    """
    依魚種回傳動畫行為目錄名 (swim_behavior, turn_behavior, eat_behavior)。
    鬥魚、鯊魚、孔雀魚皆使用預設：5_吃飽游泳、7_吃飽轉向、6_吃飽吃。
    """
    if species and species in FISH_BEHAVIOR_BY_SPECIES:
        cfg = FISH_BEHAVIOR_BY_SPECIES[species]
        return (
            cfg.get("swim", DEFAULT_FISH_SWIM_BEHAVIOR),
            cfg.get("turn", DEFAULT_FISH_TURN_BEHAVIOR),
            cfg.get("eat", DEFAULT_FISH_EAT_BEHAVIOR),
        )
    return (
        DEFAULT_FISH_SWIM_BEHAVIOR,
        DEFAULT_FISH_TURN_BEHAVIOR,
        DEFAULT_FISH_EAT_BEHAVIOR,
    )


# ---------------------------------------------------------------------------
# 顯示縮放（scale）：魚種 / 飼料 / 金錢 / 寵物及後續素材
# ---------------------------------------------------------------------------
# 調整下列參數即可改變各物件的顯示大小（倍率，1.0 為原始尺寸）。

# 魚種：預設縮放；可依魚種或階段+魚種覆寫
# FISH_SCALE_BY_SPECIES: 鍵為魚種「目錄名」（如 "鬥魚"），適用於該魚種所有階段
# FISH_SCALE_BY_STAGE_SPECIES: 鍵為 "階段_魚種"（如 "small_鬥魚"、"medium_鬥魚"），可為不同階段設定不同縮放
DEFAULT_FISH_SCALE = 0.8
FISH_SCALE_BY_SPECIES = {
    # "鬥魚": 0.2,  # 鬥魚所有階段共用此縮放（若未在 FISH_SCALE_BY_STAGE_SPECIES 中設定）
}

# 階段+魚種的縮放設定（優先於 FISH_SCALE_BY_SPECIES）
FISH_SCALE_BY_STAGE_SPECIES = {
    "small_鬥魚": 0.1,      # 幼鬥魚
    "medium_鬥魚": 0.2,     # 中鬥魚
    "large_鬥魚": 0.3,      # 成年鬥魚
    "angel_鬥魚": 0.4,      # 天使鬥魚
    "golden_鬥魚": 0.4,     # 金鬥魚（天使鬥魚吃金條變身）
    "gem_鬥魚": 0.4,        # 寶石鬥魚（天使鬥魚吃鑽石變身）
    "鯊魚": 0.4,           # 鯊魚
    "孔雀魚": 0.3,         # 孔雀魚
    # 可以在這裡為其他魚種的不同階段設定縮放
}

# 飼料：預設縮放；可依飼料名稱覆寫（鍵與 FEED_GROWTH_POINTS 一致）
DEFAULT_FEED_SCALE = 0.6
FEED_SCALE = {
    "便宜飼料": 0.3,
    "鯉魚飼料": 0.3,
    "藥丸": 0.4,
    "核廢料": 0.3,
    "金條": 0.2,
    "鑽石": 0.2,
    # "便宜飼料": 0.5,
}

# 金錢類素材：預設縮放；可依金錢類型覆寫（鍵與 MONEY_VALUE / resource/money 目錄名一致）
DEFAULT_MONEY_SCALE = 0.75
MONEY_SCALE = {
    "銅幣": 0.8,
    "銀幣": 0.8,
    "金幣": 0.8,
    "金心幣": 0.6,
    "金錐體": 0.7,
    "藍寶石": 0.7,
    # "heart_coin": 0.8,
}

# 後續添加的素材：預設縮放；可依類型覆寫（鍵自訂，如 "monster"、"decoration"）
DEFAULT_MATERIAL_SCALE = 0.75
MATERIAL_SCALE_BY_KEY = {
    # "monster": 0.7,
}


def get_fish_scale(species: str, stage: str = "small") -> float:
    """
    依魚種和階段回傳顯示縮放倍率。

    查詢順序：
    1. FISH_SCALE_BY_STAGE_SPECIES["階段_魚種"]（如 "small_鬥魚"）
    2. FISH_SCALE_BY_STAGE_SPECIES["魚種"]（僅魚種鍵，如 "鯊魚"、"孔雀魚"）
    3. FISH_SCALE_BY_SPECIES["魚種"]
    4. DEFAULT_FISH_SCALE

    Args:
        species: 魚種名稱（如 "鬥魚"、"鯊魚"）
        stage: 成長階段（"small", "medium", "large", "angel"），預設為 "small"

    Returns:
        縮放倍率
    """
    if species:
        # 1. 先檢查階段+魚種的設定（如 small_鬥魚）
        stage_species_key = f"{stage}_{species}"
        if stage_species_key in FISH_SCALE_BY_STAGE_SPECIES:
            return FISH_SCALE_BY_STAGE_SPECIES[stage_species_key]
        # 2. 無階段區分的魚種（如鯊魚、孔雀魚）可只用魚種當鍵
        if species in FISH_SCALE_BY_STAGE_SPECIES:
            return FISH_SCALE_BY_STAGE_SPECIES[species]
        # 3. 魚種共用縮放
        if species in FISH_SCALE_BY_SPECIES:
            return FISH_SCALE_BY_SPECIES[species]
    # 4. 使用預設值
    return DEFAULT_FISH_SCALE


def get_feed_scale(feed_name: str) -> float:
    """依飼料名稱回傳顯示縮放倍率。"""
    return FEED_SCALE.get(feed_name, DEFAULT_FEED_SCALE)


def get_money_scale(money_type: str) -> float:
    """依金錢類型回傳顯示縮放倍率。"""
    return MONEY_SCALE.get(money_type, DEFAULT_MONEY_SCALE)


def get_material_scale(key: str) -> float:
    """依素材鍵回傳顯示縮放倍率（供後續擴充用）。"""
    return MATERIAL_SCALE_BY_KEY.get(key, DEFAULT_MATERIAL_SCALE)


# ---------------------------------------------------------------------------
# 移動速度（speed）：魚種 / 飼料 / 金錢 / 寵物及後續素材
# ---------------------------------------------------------------------------
# 調整下列參數即可改變各物件的移動速度（像素/幀，數值越大移動越快）。

# 魚種：預設速度範圍；可依魚種覆寫（鍵為魚種名，如 "鬥魚"）
DEFAULT_FISH_SPEED_MIN = 0.4  # 新增魚時的隨機速度最小值
DEFAULT_FISH_SPEED_MAX = 0.8  # 新增魚時的隨機速度最大值
FISH_SPEED_BY_SPECIES = {
    # "鬥魚": (0.5, 0.9),  # (min, max)
}

# 魚類動畫速度（動畫播放速度）
DEFAULT_FISH_ANIMATION_SPEED = 0.12
FISH_ANIMATION_SPEED_BY_SPECIES = {
    # "鬥魚": 0.15,
}

# 魚類朝飼料移動時的速度倍率（相對於正常速度）
FISH_FEED_CHASE_SPEED_MULTIPLIER = 2.0

# 魚類吃完飼料後的冷卻時間（秒），此期間不追飼料
FISH_FEED_COOLDOWN_SEC = 3.0

# 飼料：下落速度與動畫速度
DEFAULT_FEED_FALL_SPEED = 0.6  # 下落速度（像素/幀）
FEED_FALL_SPEED = {
    # "便宜飼料": 0.5,
}

DEFAULT_FEED_ANIMATION_SPEED = 0.15
FEED_ANIMATION_SPEED = {
    # "便宜飼料": 0.12,
}

# 金錢類素材：下落速度與動畫速度
DEFAULT_MONEY_FALL_SPEED = 0.6  # 下落速度（像素/幀，與飼料相同）
MONEY_FALL_SPEED = {
    "金心幣": 0.5,
    #  "heart_coin": 0.7,
}

DEFAULT_MONEY_ANIMATION_SPEED = 0.15
MONEY_ANIMATION_SPEED = {
    # "heart_coin": 0.12,
}

# 寵物：移動速度與動畫速度（在 PET_CONFIG 中可設定 "speed" 欄位）
DEFAULT_PET_SPEED = 0.3
DEFAULT_PET_ANIMATION_SPEED = 0.12

# 後續添加的素材：預設速度；可依類型覆寫（鍵自訂）
DEFAULT_MATERIAL_SPEED = 0.5
MATERIAL_SPEED_BY_KEY = {
    # "monster": 0.3,
}

# 石榴結晶：孔雀魚加工後的金錢拾取價值倍率
POMEGRANATE_MONEY_VALUE_MULTIPLIER = 1.5

# 石榴結晶：色相（Hue）固定值（0~359，使用 HSV 的色相角度）
# 註：HSV 色相中 0/360 為紅、120 為綠、240 為藍
POMEGRANATE_FIXED_HUE = 0


def get_money_value(money_name: str) -> int:
    """
    取得金錢拾取價值（單位：$）。

    - 一般金錢：直接查 MONEY_VALUE
    - 石榴結晶金錢：名稱格式為「石榴結晶_<原金錢名>」，價值為原金錢 * 倍率
    """
    if not money_name:
        return 0
    if money_name.startswith("石榴結晶_"):
        base = money_name[len("石榴結晶_") :]
        base_value = MONEY_VALUE.get(base, 0)
        return int(base_value * POMEGRANATE_MONEY_VALUE_MULTIPLIER)
    return MONEY_VALUE.get(money_name, 0)

# 寶箱怪產物中，拾取後不增加總金額、改為加入飼料清單的項目（金條、鑽石可投餵給天使鬥魚變身）
CHEST_FEED_ITEMS = ["金條", "鑽石"]

# ---------------------------------------------------------------------------
# 寶箱怪配置
# ---------------------------------------------------------------------------
# 寶箱怪產物間隔時間（秒），預設3分鐘
CHEST_PRODUCE_INTERVAL_SEC = 180
# 寶箱怪開啟動畫開始時間（秒），預設2:51（最後9秒）
CHEST_OPENING_START_SEC = 171
# 轉換為幀數（60 FPS）
CHEST_PRODUCE_INTERVAL_FRAMES = CHEST_PRODUCE_INTERVAL_SEC * 60
CHEST_OPENING_START_FRAMES = CHEST_OPENING_START_SEC * 60
# 寶箱怪產物圖片縮放倍率（顯示在口中的大小），預設0.3（縮小70%）
CHEST_PRODUCE_IMAGE_SCALE = 0.2
# 寶箱怪等級（影響產物種類）
# +0：只產珍珠；+1：珍珠或金條隨機；+2：珍珠或金條或鑽石隨機
CHEST_LEVEL = 1

# ---------------------------------------------------------------------------
# 拼布魚配置
# ---------------------------------------------------------------------------
# 拼布魚飽足度上限
PATCHWORK_FISH_MAX_SATIATION = 30
# 拼布魚街頭表演模式持續時間（秒）
PATCHWORK_FISH_PERFORMANCE_DURATION_SEC = 30
PATCHWORK_FISH_PERFORMANCE_DURATION_FRAMES = PATCHWORK_FISH_PERFORMANCE_DURATION_SEC * 60
# 拼布魚移動速度（像素/幀），數值越大移動越快
PATCHWORK_FISH_SPEED = 1.0
# 街頭表演快樂buff：魚種大便間隔倍率（0.5 = 間隔縮短50%，即大便頻率加倍）
PATCHWORK_HAPPY_BUFF_POOP_MULTIPLIER = 0.5
# 快樂buff愛心圖示縮放倍率（顯示在魚頭上），預設0.5（縮小50%）
PATCHWORK_HAPPY_BUFF_HEART_SCALE = 0.2

# ---------------------------------------------------------------------------
# 寵物配置
# ---------------------------------------------------------------------------
# 每個寵物配置包含：
#   unlock_species: str      # 解鎖用魚種（曾達到 unlock_count 即解鎖），格式為 "階段_魚種" 或 "魚種"
#   unlock_count: int        # 解鎖所需魚種數量（與 unlock_species 搭配）
#   unlock_money: int        # 金幣解鎖（一次性扣款；與 unlock_species 二擇一）
#   require_species: str    # 召喚時需要的魚種（None 表示不需要犧牲魚）
#   require_count: int       # 召喚時需要的數量（0 表示不需要犧牲魚）
#   scale / speed            # 顯示縮放、移動速度（可選）
#   description: str         # 商店顯示的簡短描述
#   swim_behavior / turn_behavior  # 動畫目錄名（可選，預設 1_游動、2_轉向）
PET_CONFIG = {
    "龍蝦": {
        "unlock_species": "large_鬥魚",
        "unlock_count": 5,
        "require_species": None,
        "require_count": 0,
        "scale": 0.4,
        "description": "底棲生物，會幫你撿錢",
        # 各等級移動速度（等級0/1/2 對應 speed[0]/[1]/[2]）
        "speed_by_level": [0.4, 0.5, 0.6],
    },
    "寶箱怪": {
        "unlock_money": 2000,
        "require_species": None,
        "require_count": 0,
        "scale": 0.5,
        "description": "異次元生物，每過一段時間會從異次元傳送高價值物品",
        "swim_behavior": "1_開啟",
        "turn_behavior": None,
    },
    "拼布魚": {
        "unlock_money": 3500,
        "require_species": None,
        "require_count": 0,
        "scale": 0.5,
        "speed": 0.6,
        "description": "窮酸的魚，會搶飼料，但吃飽後會街頭表演，觸發30秒其他魚隻的快樂(加速大便行為)",
        "swim_behavior": "5_吃飽游泳",
        "turn_behavior": "7_吃飽轉向",
    },
}

# ---------------------------------------------------------------------------
# 寵物升級配置（等級 0=基礎，1=+1，2=+2，最高 2）
# ---------------------------------------------------------------------------
# 各寵物升級費用與效果：
#   龍蝦: +1(500金幣)/+2(1000金幣)，速度 0.4/0.5/0.6（由 PET_CONFIG 龍蝦 speed_by_level）
#   寶箱怪: +1(1000金幣)/+2(1500金幣)，產出 珍珠 / 珍珠+金條 / 珍珠+金條+鑽石
#   拼布魚: +1(1500金幣)/+2(2000金幣)，快樂buff 30/40/50 秒
PET_UPGRADE_CONFIG = {
    "龍蝦": {
        "upgrade_costs": [500, 1000],   # 升到等級1需500，升到等級2需1000
        "max_level": 2,
    },
    "寶箱怪": {
        "upgrade_costs": [1000, 1500],
        "max_level": 2,
    },
    "拼布魚": {
        "upgrade_costs": [1500, 2000],
        "max_level": 2,
        # 各等級快樂buff持續時間（秒）
        "performance_duration_by_level": [30, 40, 50],
    },
}

# ---------------------------------------------------------------------------
# 商店魚種配置（僅在商店「魚種」tab 顯示，不出現在投放魚清單）
# ---------------------------------------------------------------------------
# 欄位與寵物一致：unlock_species / unlock_count 或 unlock_money、description、
# 購買時可選 require_species + require_count（犧牲魚）或 purchase_money（消耗金幣）
#   unlock_species: str      # 解鎖用魚種（曾達到 unlock_count 即解鎖）
#   unlock_count: int        # 解鎖所需數量
#   unlock_money: int        # 金幣解鎖（與 unlock_species 二擇一）
#   require_species: str     # 購買時水族箱內須有的魚種（犧牲用）
#   require_count: int       # 購買時該魚種至少數量（購買後會移除並播餓肚子死掉動畫）
#   purchase_money: int      # 每次購買消耗金幣（可選，0 表示不需金幣）
#   description: str        # 商店顯示的簡短描述
FISH_SHOP_CONFIG = {
    "孔雀魚": {
        "unlock_species": "angel_鬥魚",
        "unlock_count": 5,
        "require_species": "angel_鬥魚",
        "require_count": 1,
        "purchase_money": 0,
        "description": "每5秒會在水中吃金錢，有機會加工成石榴結晶化產物 \n※每次購買需消耗 1 隻天使鬥魚換取一隻孔雀魚",
    },
    "鯊魚": {
        "unlock_money": 0,
        "require_species": None,
        "require_count": 0,
        "purchase_money": 3000,
        "description": "以幼鬥魚為食，每300秒吃一隻，期間會生產魚翅(100金幣) \n※忘記投餵幼鬥魚則不會生產",
    },
}

# ---------------------------------------------------------------------------
# 工具配置（商店「工具」tab）
# ---------------------------------------------------------------------------
# 飼料投食機顏色選項（對應 resource/feed_machine/投食機_<顏色>.png）
FEED_MACHINE_COLORS = [
    "灰黑色",
    "藍色",
    "綠色",
    "紅色",
    "黃色",
    "紫色",
    "粉紅色",
    "橘色",
    "靛色",
]
FEED_MACHINE_DEFAULT_COLOR = "灰黑色"  # 預設顏色
FEED_MACHINE_SCALE = 0.3  # 投食機顯示縮放倍率（30%）
FEED_MACHINE_AREA_WIDTH = 150  # 主視窗左側空白區域寬度（用於放置投食機）
FEED_MACHINE_WIDGET_WIDTH = 120  # 投食機部件寬度
FEED_MACHINE_WIDGET_HEIGHT = 200  # 投食機部件高度
FEED_MACHINE_WIDGET_OFFSET_X = 80  # 投食機部件在左側空白區域內的偏移（相對於左側空白區域左邊緣）
FEED_MACHINE_WIDGET_OFFSET_Y = 100  # 投食機部件相對於主視窗頂部的偏移（垂直居中位置）
FEED_MACHINE_INTERVAL_SEC = 15.0  # 投食機自動投食間隔（秒），每 X 秒投放一次

# 投食機上顯示的飼料圖片配置
FEED_MACHINE_FEED_IMAGE_SIZE = 15  # 投食機上顯示的飼料圖片大小（像素）
FEED_MACHINE_FEED_IMAGE_OFFSET_X = -13  # 飼料圖片相對於投食機圖片中心點的 X 偏移（像素，正值向右，負值向左）
FEED_MACHINE_FEED_IMAGE_OFFSET_Y = -10  # 飼料圖片相對於投食機圖片底部的 Y 偏移（像素，正值向下，負值向上）

# 投食機發射飼料位置配置（相對於水族箱座標）
# 起始位置：使用比例值（0.0=水族箱左邊緣，1.0=水族箱右邊緣），None 表示使用投食機位置自動計算
FEED_MACHINE_EXIT_X_RATIO = 0.1  # 投食機出口 x 位置比例（None=自動使用投食機位置，0.0~1.0=相對於水族箱寬度的比例）
FEED_MACHINE_EXIT_X_OFFSET = 0  # 投食機出口 x 位置偏移（當 EXIT_X_RATIO 為 None 時使用，相對於投食機右側，正值向右，負值向左）
FEED_MACHINE_TARGET_X_MIN_RATIO = 0.0  # 落點 x 最小位置比例（0.0=水族箱左邊緣，1.0=水族箱右邊緣）
FEED_MACHINE_TARGET_X_MAX_RATIO = 1.0  # 落點 x 最大位置比例（0.0=水族箱左邊緣，1.0=水族箱右邊緣）

# 工具解鎖配置
# 格式: "工具名稱" -> {unlock_species: str, unlock_count: int}
TOOL_CONFIG = {
    "飼料投食機": {
        "unlock_species": "large_鬥魚",  # 以成年鬥魚數量里程碑判定（曾達到 10 隻即解鎖）
        "unlock_count": 10,
        "description": "自動投食裝置，可調整顏色 \n※點選機器選擇飼料進行投食",
    },
}




