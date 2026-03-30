import json
from gsuid_core.data_store import get_res_path

# 获取 GsMcStatus 的数据目录：gsuid_core/data/GsMcStatus
CONFIG_PATH = get_res_path('GsMcStatus') / 'aliases.json'

def load_aliases() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_aliases(aliases: dict):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(aliases, f, ensure_ascii=False, indent=4)