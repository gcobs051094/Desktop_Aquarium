#!/usr/bin/env python3
"""
遊戲狀態管理模組

負責遊戲狀態的序列化、反序列化、儲存與載入。
使用 JSON 格式儲存，支援版本號機制確保向後相容。
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import INITIAL_MONEY


# 存檔格式版本號
SAVE_FORMAT_VERSION = "1.0.0"


def get_save_path() -> Path:
    """
    取得存檔檔案路徑
    
    Windows: %APPDATA%/Desktop_Feeding_Fish/save.json
    
    Returns:
        存檔檔案路徑
    """
    if os.name == 'nt':  # Windows
        appdata = os.getenv('APPDATA')
        if appdata:
            save_dir = Path(appdata) / "Desktop_Feeding_Fish"
            save_dir.mkdir(parents=True, exist_ok=True)
            return save_dir / "save.json"
    
    # 其他平台（macOS/Linux）使用使用者目錄
    home = Path.home()
    save_dir = home / ".config" / "Desktop_Feeding_Fish"
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir / "save.json"


def get_default_state() -> Dict[str, Any]:
    """
    取得預設遊戲狀態
    
    Returns:
        預設遊戲狀態字典
    """
    return {
        "version": SAVE_FORMAT_VERSION,
        "money": INITIAL_MONEY,
        "unlocked_species": {},
        "unlocked_pets": [],  # 金幣解鎖的寵物名稱列表
        "fishes": [],
        "background_path": None,
        "background_opacity": 80,
        "feed_cheap_count": 0,  # 投餵便宜飼料次數（解鎖鯉魚飼料用）
        "feed_counters": {},  # 各飼料數量計數器，如 {"鯉魚飼料": 0, "藥丸": 0, "核廢料": 0}
        "unlocked_feeds": ["便宜飼料"],  # 已解鎖飼料（待解鎖的不出現在切換飼料選單）
        "feed_counter_last_add": {},  # 各飼料上次 +1 的遊戲時間（秒），用於計數器定時
        "unlocked_tools": [],  # 已解鎖工具名稱列表
        "tool_colors": {},  # 工具顏色：{tool_name: color_name}
    }


def load() -> Dict[str, Any]:
    """
    從檔案載入遊戲狀態
    
    處理 JSON 解析錯誤、版本檢查、缺失欄位預設值。
    載入失敗時回傳預設狀態，不中斷程式啟動。
    
    Returns:
        遊戲狀態字典
    """
    save_path = get_save_path()
    
    # 檔案不存在時回傳預設狀態
    if not save_path.exists():
        print(f"[存檔] 存檔檔案不存在，使用預設狀態: {save_path}")
        return get_default_state()
    
    try:
        # 讀取並解析 JSON
        with open(save_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # 驗證基本結構
        if not isinstance(state, dict):
            print(f"[存檔] 存檔格式錯誤：根物件不是字典")
            return get_default_state()
        
        # 檢查版本號
        version = state.get("version", "unknown")
        if version != SAVE_FORMAT_VERSION:
            print(f"[存檔] 存檔版本 {version} 與當前版本 {SAVE_FORMAT_VERSION} 不同，嘗試載入...")
            # 未來可在此處實作版本遷移邏輯
        
        # 確保必要欄位存在，缺失欄位使用預設值
        default_state = get_default_state()
        for key, default_value in default_state.items():
            if key not in state:
                print(f"[存檔] 缺失欄位 {key}，使用預設值")
                state[key] = default_value
        
        # 驗證欄位類型
        if not isinstance(state.get("money"), (int, float)):
            state["money"] = 0
        if not isinstance(state.get("unlocked_species"), dict):
            state["unlocked_species"] = {}
        if not isinstance(state.get("fishes"), list):
            state["fishes"] = []
        if not isinstance(state.get("unlocked_pets"), list):
            state["unlocked_pets"] = []
        if not isinstance(state.get("background_opacity"), (int, float)):
            state["background_opacity"] = 80
        if not isinstance(state.get("feed_cheap_count"), (int, float)):
            state["feed_cheap_count"] = 0
        if not isinstance(state.get("feed_counters"), dict):
            state["feed_counters"] = {}
        if not isinstance(state.get("unlocked_feeds"), list):
            state["unlocked_feeds"] = ["便宜飼料"]
        if not isinstance(state.get("feed_counter_last_add"), dict):
            state["feed_counter_last_add"] = {}
        if not isinstance(state.get("unlocked_tools"), list):
            state["unlocked_tools"] = []
        if not isinstance(state.get("tool_colors"), dict):
            state["tool_colors"] = {}
        
        print(f"[存檔] 成功載入存檔: {save_path}")
        return state
        
    except json.JSONDecodeError as e:
        print(f"[存檔] JSON 解析錯誤: {e}")
        print(f"[存檔] 使用預設狀態")
        return get_default_state()
    except Exception as e:
        print(f"[存檔] 載入失敗: {e}")
        print(f"[存檔] 使用預設狀態")
        return get_default_state()


def save(state_dict: Dict[str, Any]) -> bool:
    """
    將遊戲狀態寫入檔案
    
    Args:
        state_dict: 遊戲狀態字典
        
    Returns:
        是否成功儲存
    """
    save_path = get_save_path()
    
    try:
        # 確保版本號正確
        state_dict["version"] = SAVE_FORMAT_VERSION
        
        # 確保目錄存在
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 寫入 JSON（使用縮排格式化，便於除錯）
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, indent=2, ensure_ascii=False)
        
        print(f"[存檔] 成功儲存存檔: {save_path}")
        return True
        
    except Exception as e:
        print(f"[存檔] 儲存失敗: {e}")
        return False
