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
    "region": "EU",
    "tournament_type": "FNCS",
    "show_win_tickers": True,
    "walkouts": False,
    "version": "1.2.1",
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
    "Vitality": "VIT",
    "AG Global": "AG",
    "Solary": "Solary",
    "HavoK": "HvK",
    "Atlantic": "Atlantic",
    "Al Qadsiah": "QAD",
    "Twisted Minds": "Twis",
    "XSET": "XSET",
    "RVL": "RVL",
    "WAVE": "WAVE",
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
    "K13": "K13",
    "Gen.G": "GEN",
    "2AM": "2AM",
    "Elite": "Elite",
    "Xen": "Xen",
    "Dignitas": "DIG",
    "Void": "Void",
    "Past Bliss": "PB",
    "Team Pulsar": "PSR",
    "REIGN": "REIGN",
    "Cynapse": "CYN",
    "Rising Legends": "RL",
    "One True Army": "1TA",
    "Monarcos": "MNRS",
    "Team Lumina": "LUM",
    "Saku": "SK",
    "Soul Runner": "SR",
    "H1TMAN": "HTM",
    "Vertios": "VET",
    "Virtus Pro": "VP",
    
    
}

def display_name(player):
    if player.org == "Free Agent":
        return player.name

    tag = ORG_TAGS.get(player.org)
    if not tag:
        return player.name

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
    else:
        time.sleep(seconds)
        
pro_players_skills = [
    ("Swizzy", 110, "Fragger", "Free Agent"),
    ("Merstach", 109, "Fragger", "Gentle Mates"),
    ("Vico", 108, "Fragger", "BIG"),
    ("Wox", 107, "Strategist", "HavoK"),
    ("Pixie", 106, "Fragger", "HavoK"),
    ("MariusCOW", 105, "Aggressive", "Gentle Mates"),
    ("Tjino", 108, "Aggressive", "HavoK"),
    ("PabloWingu", 108, "Aggressive", "HavoK"),
    ("Chap", 108, "Fragger", "Free Agent"),
    ("Shxrk", 107, "Fragger", "BIG"),
    ("Scroll", 104, "Strategist", "Atlantic"),
    ("Th0masHD", 103, "Strategist", "Free Agent"),
    ("Kami", 109, "Passive", "Free Agent"),
    ("Chico", 101, "Strategist", "Free Agent"),
    ("Charyy", 100, "Passive", "Free Agent"),
    ("Japko", 104, "Fragger", "Falcons"),
    ("Queasy", 103, "Passive", "Free Agent"),
    ("Veno", 102, "Fragger", "XSET"),
    ("Flickzy", 101, "Aggressive", "Free Agent"),
    ("P1ngfnz", 100, "Fragger", "Free Agent"),
    ("Malibuca", 104, "Strategist", "Free Agent"),
    ("Vanyak3k", 103, "Passive", "Gentle Mates"),
    ("Fredoxie", 102, "Strategist", "Free Agent"),
    ("MrSavage", 101, "Aggressive", "XSET"),
    ("Sky", 100, "Strategist", "Atlantic"),
    ("t3eny", 106, "Aggressive", "Free Agent"),
    ("Trulex", 98, "Strategist", "Free Agent"),
    ("Tayson", 97, "Strategist", "Falcons"),
    ("IDrop", 104, "Fragger", "HavoK"),
    ("Rezon", 95, "Fragger", "WAVE"),
    ("Setty", 99, "Passive", "Free Agent"),
    ("Panzer", 98, "Strategist", "Free Agent"),
    ("Vadeal", 87, "Passive", "WAVE"),
    ("Focus", 86, "Fragger", "Free Agent"),
    ("Akiira", 95, "Fragger", "Gentle Mates"),
    ("Rax", 84, "Fragger", "Free Agent"),
    ("Kurama", 99, "Fragger", "Solary"),
    ("Werex", 98, "Strategist", "Lyost"),
    ("Seyyto", 94, "Strategist", "K13"),
    ("Kiro", 86, "Strategist", "Free Agent"),
    ("Podasai", 85, "Strategist", "Free Agent"),
    ("Momsy", 89, "Strategist", "Free Agent"),
    ("Pixx", 90, "Passive", "HavoK"),
    ("Demus", 92, "Fragger", "T1"),
    ("Darm", 90, "Fragger", "T1"),
    ("Sangild", 85, "Strategist", "Free Agent"),
    ("Huty", 84, "Strategist", "The One"),
    ("F1shyX", 83, "Strategist", "Free Agent"),
    ("Mappi", 83, "Strategist", "Free Agent"),
    ("Moneymaker", 82, "Fragger", "Free Agent"),
    ("Mongraal", 81, "Aggressive", "Free Agent"),
    ("Wheat", 80, "Strategist", "FLC"),
    ("NeFrizi", 79, "Strategist", "Detect"),
    ("Twi", 78, "Aggressive", "Free Agent"),
    ("SkyJump", 77, "Fragger", "Solary"),
    ("Mikson", 76, "Fragger", "Free Agent"),
    ("Upl", 80, "Fragger", "Free Agent"),
    ("Kombek", 79, "Fragger", "Free Agent"),
    ("Blacha", 78, "Passive", "Free Agent"),
    ("Hris", 77, "Fragger", "Free Agent"),
    ("Ankido", 71, "Strategist", "BIG"),
    ("Cringe", 70, "Strategist", "AVE"),
    ("Volko", 69, "Strategist", "BIG"),
    ("JannisZ", 78, "Passive", "CGN"),
    ("Pinq", 75, "Passive", "Free Agent"),
    ("Dela", 83, "Aggressive", "Free Agent"),
    ("Bevvys", 83, "Aggressive", "Free Agent"),
    ("Eclipse", 78, "Aggressive", "Free Agent"),
    ("Hellfire", 83, "Strategist", "Free Agent"),
    ("Andilex", 86, "Fragger", "MGA"),
    ("Kiduoo", 71, "Passive", "BIG"),
    ("Robin", 70, "Strategist", "FOKUS"),
    ("Kyto", 70, "Fragger", "Free Agent"),
    ("Hijoe", 70, "Strategist", "Aight"),
    ("Dandepuzo", 73, "Fragger", "TKRF"),
    ("iFr0zi", 70, "Passive", "FataL"),
    ("Skvii", 85, "Strategist", "Free Agent"),
    ("Fastroki", 70, "Strategist", "Free Agent"),
    ("1Lusha", 76, "Aggressive", "Free Agent"),
    ("S1neD", 78, "Strategist", "NTO Corp"),
    ("F1n4ik", 75, "Fragger", "FLC"),
    ("Howly", 75, "Fragger", "Free Agent"),
    ("G13ras", 70, "Strategist", "Detect"),
    ("CZB", 79, "Aggressive", "Free Agent"),
    ("Axeforce", 78, "Aggressive", "Free Agent"),
    ("Fnajen", 79, "Fragger", "Free Agent"),
    ("Predage", 80, "Passive", "Free Agent"),
    ("Deckzee", 78, "Aggressive", "Free Agent"),
    ("Artskill", 84, "Aggressive", "Free Agent"),
    ("Xsweeze", 82, "Strategist", "Free Agent"),
    ("Noahreyli", 81, "Fragger", "Free Agent"),
    ("Snayzy", 80, "Strategist", "HavoK"),
    ("Tidi", 75, "Fragger", "Free Agent"),
    ("Zangi", 80, "Fragger", "Free Agent"),
    ("Franek", 80, "Aggressive", "MGA"),
    ("Asa", 80, "Passive", "Free Agent"),
    ("Belusi", 79, "Fragger", "Free Agent"),
    ("Refsgaard", 78, "Strategist", "Free Agent"),
    ("Nxthan", 77, "Fragger", "Free Agent"),
    ("Juu", 76, "Strategist", "FataL"),
]
