import random
import time
CONFIG = {
    "players": 100,
    "matches": 12,
    "elim_points": 3,
    "poi_count": 13,
    "min_poi_size": 1,
    "max_poi_size": 3,
    "storm_circles": 12,
    "allow_griefing": True,
    "speed": "NORMAL", # SLOW | NORMAL | FAST | INSTANT
    "random_seed": random.randint(1,1000),
    "tournament_type": "FNCS", # CASH CUP | FNCS | LAN EVENT | VICTORY CUP
    "show_win_tickers": True,
    "version": "1.1.3",
    "build": "Stable", # or "Experimental"
}

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
        
