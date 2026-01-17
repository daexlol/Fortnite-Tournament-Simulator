if __name__ == "__main__":
    raise RuntimeError("utils.py should not be run directly!")

import os, json, random, time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")

DEFAULT_CONFIG = {
    "players": 100,
    "matches": 12,
    "elim_points": 3,
    "poi_count": 13,
    "min_poi_size": 1,
    "max_poi_size": 3,
    "storm_circles": 12,
    "allow_griefing": True,
    "speed": "NORMAL",
    "random_seed": random.randint(1, 1000),
    "tournament_type": "FNCS",
    "show_win_tickers": True,
    "walkouts": False,
    "version": "1.1.4",
    "build": "Stable",
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Config file invalid, resetting...")
            return data
    except (json.JSONDecodeError, ValueError):
        print("⚠️  Config file empty or invalid, resetting to defaults...")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

CONFIG = load_config()


MODS_FILE = os.path.join(DATA_DIR, "active_mods.json")

def save_active_mods(mods):
    data = [{"name": mod.name, "enabled": mod.enabled} for mod in mods]
    with open(MODS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def load_active_mods(all_mods):
    if not os.path.exists(MODS_FILE):
        save_active_mods(all_mods)
        return all_mods

    try:
        with open(MODS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            name_to_mod = {mod.name: mod for mod in all_mods}
            for item in data:
                if item["name"] in name_to_mod:
                    name_to_mod[item["name"]].enabled = item.get("enabled", False)
        return all_mods
    except (json.JSONDecodeError, ValueError):
        print("⚠️  Mods file empty or invalid, resetting to defaults...")
        save_active_mods(all_mods)
        return all_mods




ORG_TAGS = {
    "Gentle Mates": "M8",
    "Falcons": "Falcon",
    "BIG": "BIG",
    "Solary": "Solary",
    "HavoK": "HvK",
    "Atlantic": "Atlantic",
    "Al Qadsiah": "QAD",
    "Twisted Minds": "Twis",
    "XSET": "XSET",
    "RVL": "RVL",
    "Wave": "WAVE",
    "MGA": "MGA",
    "Detect": "Detect",
    "FataL": "FataL",
    "NTO Corp": "NTO",
    "CGN": "CGN",
    "AVE": "AVE",
    "FOKUS": "FOKUS",
    "TKRF": "TKRF",
    "Aight": "Aight",
    "Lyost": "Lyost",
    "FLC": "FLC",
    "The One": "One",
    "T1": "T1",
}

def display_name(player):
    if player.org == "Free Agent":
        return player.name

    tag = ORG_TAGS.get(player.org)
    if not tag:
        return player.name  # fallback safety

    return f"{tag} {player.name}"

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    
    SOFT_RED     = "\033[38;2;255;102;102m"
    SOFT_GREEN   = "\033[38;2;102;204;102m"
    SOFT_YELLOW  = "\033[38;2;255;204;102m"
    SOFT_BLUE    = "\033[38;2;102;153;255m"
    SOFT_PURPLE  = "\033[38;2;204;153;255m"
    SOFT_CYAN    = "\033[38;2;102;204;204m"
    
    LIGHT_GRAY   = "\033[38;2;150;150;150m"
    VERY_LIGHT_GRAY = "\033[38;2;230;230;235m"
    WARM_WHITE   = "\033[38;2;245;245;240m"
    
    BORDER_BLUE  = "\033[38;2;150;180;220m"


def sim_sleep(seconds):
    if CONFIG["speed"] == "INSTANT":
        return
    elif CONFIG["speed"] == "FAST":
        time.sleep(seconds * 0.65)
    elif CONFIG["speed"] == "SLOW":
        time.sleep(seconds * 1.35)
    else:  # NORMAL
        time.sleep(seconds)
        
