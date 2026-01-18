import json
import os
import math
import random
import time
import datetime
from dataclasses import dataclass, field
from typing import List
from utils import display_name, ORG_TAGS, Colors, sim_sleep, DEFAULT_CONFIG, CONFIG, BASE_DIR, DATA_DIR, save_config, load_config, save_active_mods, load_active_mods
from rich.console import Console
from rich.table import Table
from mods import (
    TechnicalIssuesMod,
    RageQuitMod,
    ZeroBuildFlashbackMod,
    StreamSnipedMod,
    PingDiffMod,
)

console = Console(highlight=False)

ACTIVE_MODS = [
    TechnicalIssuesMod(crash_chance=0.008, no_load_chance=0.012),
    RageQuitMod(),
    ZeroBuildFlashbackMod(),
    StreamSnipedMod(),
    #PingDiffMod(bad_ping_chance=0.22),
]

ACTIVE_MODS = load_active_mods(ACTIVE_MODS)

TOURNAMENTS_ROOT = os.path.join(BASE_DIR, "tournaments")

REGION = CONFIG.get("region", "EU").lower()
REGION_DATA_DIR = os.path.join(DATA_DIR, REGION)
os.makedirs(REGION_DATA_DIR, exist_ok=True)
CAREER_FILE = os.path.join(REGION_DATA_DIR, "career_stats.json")
SEASON_FILE = os.path.join(REGION_DATA_DIR, "season_data.json")
SPLASH_FILE = "splash.txt"
SEASON = {
    "current_season": 1,
    "tournaments_played": 0,
    "tournaments_per_season": 16,
    "season_players": {},
    "history": [],
}

os.makedirs(DATA_DIR, exist_ok=True)


def load_splash_texts():
    try:
        with open(SPLASH_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines if lines else ["Welcome to the chaos..."]
    except FileNotFoundError:
        return ["No splash.txt found... dropping in silence"]
    except Exception:
        return ["Error loading splashes... pretend this is funny"]
        
def set_region(region_name):
    global REGION, REGION_DATA_DIR, CAREER_FILE, SEASON_FILE
    REGION = region_name.lower()
    REGION_DATA_DIR = os.path.join(DATA_DIR, REGION)
    os.makedirs(REGION_DATA_DIR, exist_ok=True)
    CAREER_FILE = os.path.join(REGION_DATA_DIR, "career_stats.json")
    SEASON_FILE = os.path.join(REGION_DATA_DIR, "season_data.json")
        

random.seed(CONFIG["random_seed"])

PRO_PLAYER_POOLS = {
    "EU": [
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
	],

    "NA": [
        ('Peterbot', 113, 'Aggressive', 'Falcons'),
        ('Cold', 109, 'Aggressive', 'Twisted Minds'),
        ('Ajerss', 108, 'Fragger', 'Gen.G'),
        ('Pollo', 108, 'Fragger', 'Gentle Mates'),
        ('Higgs', 107, 'Aggressive', 'XSET'),
        ('Eomzo', 107, 'Strategist', 'Elite'),
        ('Muz', 106, 'Fragger', 'XSET'),
        ('Rapid', 106, 'Strategist', 'Xen'),
        ('Ritual', 105, 'Fragger', 'Gen.G'),
        ('Boltz', 105, 'Aggressive', 'Twisted Minds'),
        ('Clix', 104, 'Fragger', 'XSET'),
        ('Sphinx', 104, 'Passive', 'Free Agent'),
        ('Acorn', 103, 'Passive', 'Dignitas'),
        ('Khanada', 103, 'Fragger', 'Dignitas'),
        ('Cooper', 102, 'Fragger', 'Dignitas'),
        ('Threats', 102, 'Aggressive', 'Free Agent'),
        ('Ark', 102, 'Fragger', 'Dignitas'),
        ('Rise', 101, 'Passive', 'Free Agent'),
        ('Bugha', 101, 'Strategist', 'Free Agent'),
        ('Avivv', 100, 'Fragger', '2AM'),
        ('Reet', 100, 'Strategist', 'Free Agent'),
        ('Shadow', 100, 'Fragger', 'Free Agent'),
        ('Skqttles', 99, 'Passive', 'Free Agent'),
        ('VerT', 99, 'Strategist', 'Void'),
        ('GMoney', 99, 'Fragger', '2AM'),
        ('PXMP', 90, 'Aggressive', 'Elite'),
        ('EpikWhale', 95, 'Strategist', 'Free Agent'),
        ('Noxy', 87, 'Passive', 'Free Agent'),
        ('Aminished', 87, 'Strategist', 'Past Bliss'),
        ('Chimp', 76, 'Fragger', 'Team Pulsar'),
        ('Channce', 76, 'Fragger', 'Team Pulsar'),
        ('Brycx', 85, 'Strategist', 'Free Agent'),
        ('Braydz', 85, 'Fragger', 'Free Agent'),
        ('Curve', 74, 'Aggressive', 'Free Agent'),
        ('oSydd', 74, 'Fragger', 'Free Agent'),
        ('Visxals', 73, 'Strategist', 'Free Agent'),
        ('Vergo', 73, 'Strategist', 'Rising Legends'),
        ('Parz', 72, 'Passive', 'Free Agent'),
        ('Seek', 72, 'Aggressive', 'Free Agent'),
        ('Bacca', 71, 'Fragger', 'Free Agent'),
        ('Curly', 71, 'Strategist', 'Free Agent'),
        ('Nvtylerh', 70, 'Aggressive', 'Free Agent'),
        ('Dash', 70, 'Fragger', 'REIGN'),
        ('Mason', 70, 'Strategist', 'Void'),
        ('Kraez', 69, 'Aggressive', 'Cynapse'),
        ('VicterV', 69, 'Fragger', 'Free Agent'),
        ('Paper', 69, 'Passive', 'Free Agent'),
        ('Eshouu', 68, 'Aggressive', 'Free Agent'),
        ('Tkay', 68, 'Fragger', 'Free Agent'),
        ('Ozone', 68, 'Strategist', 'One True Army'),
        ('Edgey', 68, 'Fragger', 'Free Agent'),
        ('Dukez', 68, 'Fragger', 'Free Agent'),
        ('Cam', 68, 'Strategist', 'Free Agent'),
        ('OliverOG', 68, 'Passive', 'Dignitas'),
        ('Trashy', 67, 'Aggressive', 'Free Agent'),
        ('Chubs', 67, 'Fragger', 'Free Agent'),
        ('Krreon', 67, 'Strategist', 'Monarcos'),
        ('Veer', 67, 'Aggressive', 'Free Agent'),
        ('Npen', 66, 'Fragger', 'Free Agent'),
        ('Aiden', 66, 'Passive', 'Team Lumina'),
        ('Takii', 66, 'Aggressive', 'Void'),
        ('Kwanti', 66, 'Fragger', 'Free Agent'),
        ('Mero', 95, 'Fragger', 'Xen'),
        ('Bacon', 65, 'Aggressive', 'Free Agent'),
        ('Ceneto', 65, 'Strategist', 'Saku'),
        ('Tonyfv', 65, 'Fragger', 'Free Agent'),
        ('Dolzeur', 65, 'Passive', 'Free Agent'),
        ('Bucke', 93, 'Strategist', 'Dignitas'),
        ('Xavi', 64, 'Aggressive', 'Free Agent'),
        ('Bylah', 64, 'Fragger', 'Free Agent'),
        ('Void', 64, 'Strategist', 'Free Agent'),
        ('Blake', 64, 'Passive', 'Soul Runner'),
        ('Aoxy', 63, 'Aggressive', 'Free Agent'),
        ('Okis', 63, 'Fragger', 'Free Agent'),
        ('Jojofishy', 63, 'Strategist', 'Free Agent'),
        ('Hound', 63, 'Aggressive', 'Free Agent'),
        ('Deyy', 74, 'Aggressive', 'Free Agent'),
        ('Scare', 62, 'Fragger', 'Cynapse'),
        ('Noizy', 62, 'Passive', 'Monarcos'),
        ('Golden', 62, 'Strategist', 'One True Army'),
        ('Krisp', 62, 'Aggressive', 'Free Agent'),
        ('Liam', 62, 'Fragger', 'H1TMAN'),
        ('Evyn', 61, 'Strategist', 'Free Agent'),
        ('Vortek', 61, 'Aggressive', 'Free Agent'),
        ('Chaos', 61, 'Fragger', 'Free Agent'),
        ('Death', 60, 'Aggressive', 'Free Agent'),
        ('Hxvac', 60, 'Strategist', 'Visual'),
        ('Broken', 60, 'Passive', 'Vertios'),
        ('Zandaa', 60, 'Fragger', 'H1TMAN'),
        ('Jaqck', 59, 'Aggressive', 'Free Agent'),
        ('Encrypted', 59, 'Strategist', 'Free Agent'),
        ('Zeus', 59, 'Aggressive', 'Free Agent'),
        ('Freeze', 59, 'Passive', 'One True Army'),
        ('Phenom', 58, 'Fragger', 'Free Agent'),
        ('Nekko', 58, 'Aggressive', 'Free Agent'),
        ('NoahWPlays', 58, 'Strategist', 'Free Agent'),
        ('Sandman', 57, 'Passive', 'Free Agent'),
        ('Josh', 57, 'Fragger', 'Free Agent'),
        ('Nurface', 57, 'Aggressive', 'Free Agent'),
        ('Circ', 56, 'Strategist', 'Free Agent'),
    ],
        "MIXED": [
        ("Swizzy", 110, "Fragger", "Free Agent"),
        ("Merstach", 109, "Fragger", "Gentle Mates"),
        ("Kami", 109, "Passive", "Free Agent"),
        ("Vico", 108, "Fragger", "BIG"),
        ("Tjino", 108, "Aggressive", "HavoK"),
        ("PabloWingu", 108, "Aggressive", "HavoK"),
        ("Chap", 108, "Fragger", "Free Agent"),
        ("Wox", 107, "Strategist", "HavoK"),
        ("Shxrk", 107, "Fragger", "BIG"),
        ("Pixie", 106, "Fragger", "HavoK"),
        ("t3eny", 106, "Aggressive", "Free Agent"),
        ("MariusCOW", 105, "Aggressive", "Gentle Mates"),
        ("Scroll", 104, "Strategist", "Atlantic"),
        ("Japko", 104, "Fragger", "Falcons"),
        ("Malibuca", 104, "Strategist", "Free Agent"),
        ("IDrop", 104, "Fragger", "HavoK"),
        ("Th0masHD", 103, "Strategist", "Free Agent"),
        ("Queasy", 103, "Passive", "Free Agent"),
        ("Vanyak3k", 103, "Passive", "Gentle Mates"),
        ("Veno", 102, "Fragger", "XSET"),
        ("Fredoxie", 102, "Strategist", "Free Agent"),
        ("Chico", 101, "Strategist", "Free Agent"),
        ("Flickzy", 101, "Aggressive", "Free Agent"),
        ("MrSavage", 101, "Aggressive", "XSET"),
        ("Charyy", 100, "Passive", "Free Agent"),
        ("P1ngfnz", 100, "Fragger", "Free Agent"),
        ("Sky", 100, "Strategist", "Atlantic"),
        ("Setty", 99, "Passive", "Free Agent"),
        ("Kurama", 99, "Fragger", "Solary"),
        ("Trulex", 98, "Strategist", "Free Agent"),
        ("Panzer", 98, "Strategist", "Free Agent"),
        ("Werex", 98, "Strategist", "Lyost"),
        ("Tayson", 97, "Strategist", "Falcons"),
        ("Rezon", 95, "Fragger", "WAVE"),
        ("Akiira", 95, "Fragger", "Gentle Mates"),
        ("Seyyto", 94, "Strategist", "K13"),
        ("Demus", 92, "Fragger", "T1"),
        ("Pixx", 90, "Passive", "HavoK"),
        ("Darm", 90, "Fragger", "T1"),
        ("Momsy", 89, "Strategist", "Free Agent"),
        ("Vadeal", 87, "Passive", "WAVE"),
        ("Focus", 86, "Fragger", "Free Agent"),
        ("Kiro", 86, "Strategist", "Free Agent"),
        ("Andilex", 86, "Fragger", "MGA"),
        ("Podasai", 85, "Strategist", "Free Agent"),
        ("Sangild", 85, "Strategist", "Free Agent"),
        ("Skvii", 85, "Strategist", "Free Agent"),
        ("Rax", 84, "Fragger", "Free Agent"),
        ("Huty", 84, "Strategist", "The One"),
        ("Artskill", 84, "Aggressive", "Free Agent"),
        ("Peterbot", 113, "Aggressive", "Falcons"),
        ("Cold", 109, "Aggressive", "Twisted Minds"),
        ("Ajerss", 108, "Fragger", "Gen.G"),
        ("Pollo", 108, "Fragger", "Gentle Mates"),
        ("Higgs", 107, "Aggressive", "XSET"),
        ("Eomzo", 107, "Strategist", "Elite"),
        ("Muz", 106, "Fragger", "XSET"),
        ("Rapid", 106, "Strategist", "Xen"),
        ("Ritual", 105, "Fragger", "Gen.G"),
        ("Boltz", 105, "Aggressive", "Twisted Minds"),
        ("Clix", 104, "Fragger", "XSET"),
        ("Sphinx", 104, "Passive", "Free Agent"),
        ("Acorn", 103, "Passive", "Dignitas"),
        ("Khanada", 103, "Fragger", "Dignitas"),
        ("Cooper", 102, "Fragger", "Dignitas"),
        ("Threats", 102, "Aggressive", "Free Agent"),
        ("Ark", 102, "Fragger", "Dignitas"),
        ("Rise", 101, "Passive", "Free Agent"),
        ("Bugha", 101, "Strategist", "Free Agent"),
        ("Avivv", 100, "Fragger", "2AM"),
        ("Reet", 100, "Strategist", "Free Agent"),
        ("Shadow", 100, "Fragger", "Free Agent"),
        ("Skqttles", 99, "Passive", "Free Agent"),
        ("VerT", 99, "Strategist", "Void"),
        ("GMoney", 99, "Fragger", "2AM"),
        ("EpikWhale", 95, "Strategist", "Free Agent"),
        ("Mero", 95, "Fragger", "Xen"),
        ("Bucke", 93, "Strategist", "Dignitas"),
        ("PXMP", 88, "Aggressive", "Elite"),
        ("Noxy", 87, "Passive", "Free Agent"),
        ("Aminished", 87, "Strategist", "Past Bliss"),
        ("Braydz", 85, "Fragger", "Free Agent"),
        ("Chimp", 76, "Fragger", "Team Pulsar"),
        ("Channce", 76, "Fragger", "Team Pulsar"),
        ("Brycx", 75, "Strategist", "Free Agent"),
        ("Curve", 74, "Aggressive", "Free Agent"),
        ("oSydd", 74, "Fragger", "Free Agent"),
        ("Deyy", 74, "Aggressive", "Free Agent"),
        ("Visxals", 73, "Strategist", "Free Agent"),
        ("Vergo", 73, "Strategist", "Rising Legends"),
        ("Parz", 72, "Passive", "Free Agent"),
        ("Seek", 72, "Aggressive", "Free Agent"),
        ("Bacca", 71, "Fragger", "Free Agent"),
        ("Curly", 71, "Strategist", "Free Agent"),
        ("Nvtylerh", 70, "Aggressive", "Free Agent"),
        ("Dash", 70, "Fragger", "REIGN"),
        ("Mason", 70, "Strategist", "Void"),
        ("Kraez", 69, "Aggressive", "Cynapse"),
        ("VicterV", 69, "Fragger", "Free Agent"),
        ("Paper", 69, "Passive", "Free Agent"),
    ],
}

def get_pro_players_from_config():
    region = CONFIG.get("region", "EU")
    pool = PRO_PLAYER_POOLS.get(region)

    if not pool:
        raise ValueError(f"No player pool found for region '{region}'")

    return pool

ARCHETYPES = ["Fragger", "Passive", "Strategist", "Aggressive"]

TOURNAMENT_TYPES = {
    "CASH_CUP": {
        "label": "CASH CUP",
        "prize_pool": [
            (1, 1, 10_000),
            (2, 2, 8_000),
            (3, 3, 6_000),
            (4, 4, 4_000),
            (5, 5, 3_250),
            (6, 6, 2_800),
            (7, 7, 2_000),
            (8, 8, 1_500),
            (9, 9, 1_000),
            (10, 10, 850),
            (11, 25, 500),
            (26, 50, 250),
            (51, 75, 100),
            (76, 90, 50),
            (91, 100, 0),
        ],
    },

    "FNCS": {
        "label": "FNCS",
        "prize_pool": [
            (1, 1, 100_000),
            (2, 2, 80_000),
            (3, 3, 60_000),
            (4, 4, 40_000),
            (5, 5, 32_500),
            (6, 6, 28_000),
            (7, 7, 20_000),
            (8, 8, 15_000),
            (9, 9, 10_000),
            (10, 10, 8_500),
            (11, 25, 5_000),
            (26, 50, 2_500),
            (51, 75, 1_000),
            (76, 90, 500),
            (91, 100, 0),
        ],
    },

    "LAN": {
        "label": "LAN EVENT",
        "prize_pool": [
            (1, 1, 250_000),
            (2, 2, 175_000),
            (3, 3, 125_000),
            (4, 4, 100_000),
            (5, 5, 80_000),
            (6, 10, 60_000),
            (11, 20, 40_000),
            (21, 50, 20_000),
            (51, 75, 10_000),
            (76, 100, 5_000)
        ],
    },
    
    "VICTORY_CUP": {
        "label": "VICTORY CUP",
        "points_per_win": 100,
        "money_per_point": 1
    }
}

TOURNAMENT_TEMPLATES = {
    "CASH_CUP": {
        "label": "CASH CUP",
        "players": 100,
        "matches": 6,
        "storm_circles": 12,
        "elim_points": 2,
        "tournament_type": "CASH_CUP",
    },
    "FNCS": {
        "label": "FNCS GRAND FINALS",
        "players": 100,
        "matches": 12,
        "storm_circles": 12,
        "elim_points": 3,
        "tournament_type": "FNCS",
    },
    "LAN": {
        "label": "LAN EVENT",
        "players": 100,
        "matches": 12,
        "storm_circles": 12,
        "elim_points": 4,
        "tournament_type": "LAN",
        "region": "MIXED",
    },
    "VICTORY_CUP": {
        "label": "VICTORY CUP",
        "players": 100,
        "matches": 4,
        "storm_circles": 12,
        "elim_points": 0,
        "tournament_type": "VICTORY_CUP",
    }
}

def apply_tournament_template(key):
    template = TOURNAMENT_TEMPLATES[key]

    CONFIG["players"] = template["players"]
    CONFIG["matches"] = template["matches"]
    CONFIG["storm_circles"] = template["storm_circles"]
    CONFIG["elim_points"] = template["elim_points"]
    CONFIG["tournament_type"] = template["tournament_type"]
    save_config(CONFIG)

    print("\n✅ Tournament template applied:")
    print(f"🏆 {template['label']}")
    print(f"• Players: {template['players']}")
    print(f"• Matches: {template['matches']}")
    print(f"• Storm Circles: {template['storm_circles']}")
    print(f"• Elim Points: {template['elim_points']}")


def get_prize_for_rank(rank: int, player):
    t_type = CONFIG["tournament_type"]
    t_data = TOURNAMENT_TYPES[t_type]

    if t_type == "VICTORY_CUP":
        return player.total_points * t_data["money_per_point"]

    for start, end, prize in t_data["prize_pool"]:
        if start <= rank <= end:
            return prize
    return 0



@dataclass
class Player:
    id: int
    name: str
    skill: float
    archetype: str = "TBD"
    org: str = "Free Agent"

    total_points: int = 0
    total_elims: int = 0
    placements: List[int] = field(default_factory=list)
    wins: int = 0

    drop_poi: str = ""
    alive: bool = True
    match_kills: List[int] = field(default_factory=list)

    confidence: float = 0.0
    tournament_earnings: int = 0

    career_earnings: int = 0
    career_kills: int = 0
    career_tournaments: int = 0
    career_wins: int = 0
    career_cashcup_wins: int = 0
    career_fncs_wins: int = 0
    career_lan_wins: int = 0
    career_victorycup_wins: int = 0
    best_finish: int = 999
    
    current_rank: int = 0
    points_to_first: int = 0
    points_to_above: int = 0
    points_to_below: int = 0
    safety_margin: int = 0

    risk_tolerance: float = 0.5
    grief_bias: float = 0.0
    
    rivals: dict = field(default_factory=dict)
    fear: dict = field(default_factory=dict)
    
    _has_rage_quit: bool = field(default=False)


    def add_match_result(self, placement, elims, points):
        self.total_points += points
        self.total_elims += elims
        self.placements.append(placement)
        self.match_kills.append(elims)

        if placement == 1:
            self.wins += 1

            
    @property
    def average_placement(self):
        return sum(self.placements) / len(self.placements) if self.placements else 0

    @property
    def average_elims(self):
        return self.total_elims / len(self.placements) if self.placements else 0


@dataclass
class POI:
    name: str
    size: int
    minis: List[str] = field(default_factory=list)


def update_confidence(players: List[Player]):
    ranked = sorted(
        players,
        key=lambda p: (
            p.total_points,
            p.wins,
            p.total_elims,
            -p.average_placement
        ),
        reverse=True
    )

    total = len(ranked)

    for idx, p in enumerate(ranked):
        percentile = idx / total

        p.confidence *= 0.9

        if percentile < 0.05:
            p.confidence += 0.05
        elif percentile < 0.15:
            p.confidence += 0.03
        elif percentile < 0.30:
            p.confidence += 0.015

        elif percentile > 0.95:
            p.confidence -= 0.06
        elif percentile > 0.85:
            p.confidence -= 0.035
        elif percentile > 0.70:
            p.confidence -= 0.02

        p.confidence = max(-1.0, min(1.0, p.confidence))
        

def load_season():
    global SEASON
    if os.path.exists(SEASON_FILE):
        with open(SEASON_FILE, "r", encoding="utf-8") as f:
            SEASON = json.load(f)
    else:
        save_season()


def save_season():
    with open(SEASON_FILE, "w", encoding="utf-8") as f:
        json.dump(SEASON, f, indent=2)


def load_career_data(players: List[Player]):
    if not os.path.exists(CAREER_FILE):
        return

    with open(CAREER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for p in players:
        if p.name in data:
            stats = data[p.name]
            p.career_earnings = stats.get("earnings", 0)
            p.career_kills = stats.get("kills", 0)
            p.career_tournaments = stats.get("tournaments", 0)
            p.career_wins = stats.get("wins", 0)
            p.career_cashcup_wins = stats.get("cashcup_wins", 0)
            p.career_fncs_wins = stats.get("fncs_wins", 0)
            p.career_lan_wins = stats.get("lan_wins", 0)
            p.career_victorycup_wins = stats.get("victorycup_wins", 0)
            p.best_finish = stats.get("best_finish", 999)


def save_career_data(players: List[Player]):
    data = {}
    for p in players:
        data[p.name] = {
            "earnings": p.career_earnings,
            "kills": p.career_kills,
            "tournaments": p.career_tournaments,
            "wins": p.career_wins,
            "cashcup_wins": p.career_cashcup_wins,
            "fncs_wins": p.career_fncs_wins,
            "lan_wins": p.career_lan_wins,
            "victorycup_wins": p.career_victorycup_wins,
            "best_finish": p.best_finish,
        }

    with open(CAREER_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def init_season_players(players):
    for p in players:
        if p.name not in SEASON["season_players"]:
            SEASON["season_players"][p.name] = {
                "points": 0,
                "wins": 0,
                "elims": 0,
                "earnings": 0
            }
                
                
def placement_points(placement: int) -> int:
    if placement > 50:
        return 0
    if placement == 50:
        return 1
    if 4 <= placement <= 49:
        return 51 - placement
    if placement == 3:
        return 49
    if placement == 2:
        return 53
    if placement == 1:
        return 60
    return 0


def generate_pois():
    base_names = [
        "Sandy Strip",
        "Latte Landing",
        "Painted Palms",
        "Fore Fields",
        "Classified Canyon",
        "Sus Studios",
        "Lethal Labs",
        "Humble Hills",
        "Bumpy Bay",
        "Tiptop Terrace",
        "Wonkeeland",
        "Battlewood Boulevard",
        "Ripped Tides",
        "Clawsy Lodge",
    ]

    pois = []

    for i in range(CONFIG["poi_count"]):
        size = random.randint(CONFIG["min_poi_size"], CONFIG["max_poi_size"])
        poi = POI(name=base_names[i % len(base_names)], size=size)

        if size > 1:
            for j in range(1, size + 1):
                poi.minis.append(f"{poi.name} - Mini-{j}")

        pois.append(poi)

    return pois


def assign_drops(players: List[Player], pois: List[POI]):
    drop_list = []

    for poi in pois:
        drop_list.append((poi.name, poi.size))
        for mini in poi.minis:
            drop_list.append((mini, poi.size))

    for player in players:
        player.drop_poi, poi_size = random.choices(
            drop_list,
            weights=[s for n, s in drop_list],
            k=1
        )[0]
        player.alive = True


def assign_archetypes(players):
    for p in players:
        if p.archetype == "TBD":
            p.archetype = "Strategist"


def get_kill_weight(player):
    base = player.skill
    
    multipliers = {
        "Fragger":    1.30,
        "Aggressive": 1.45,
        "Strategist": 0.90,
        "Passive":    0.80, 
    }
    
    return base * multipliers.get(player.archetype, 1.0)


def get_survival_weight(player):
    multipliers = {
        "Fragger":    0.85,
        "Aggressive": 0.75,
        "Strategist": 1.25,
        "Passive":    1.40,
    }
    return 1.0 * multipliers.get(player.archetype, 1.0)

# -----------------------------------------------------------
# DYNAMIC TOP 10
# -----------------------------------------------------------

previous_player_ranks = {}

def print_top10_cumulative(players: List[Player]):
    global previous_player_ranks
    JUMP_FIRE = 10
    JUMP_ROCKET = 20

    full_ranking = sorted(
        players,
        key=lambda p: (
            p.total_points,
            p.wins,
            p.average_elims,
            -p.average_placement
        ),
        reverse=True
    )

    top10_cumulative = full_ranking[:10]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 CURRENT TOP 10 STANDINGS 📊")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for rank, p in enumerate(top10_cumulative, 1):
        prev_rank = previous_player_ranks.get(p.name)

        if prev_rank is None:
            movement = "🆕"
        elif prev_rank > rank:
            diff = prev_rank - rank
            if diff >= JUMP_ROCKET:
                flair = " 🚀"
            elif diff >= JUMP_FIRE:
                flair = " 🔥"
            else:
                flair = ""
				
            movement = f"{Colors.SOFT_GREEN}▲{diff}{flair}{Colors.RESET}"
        elif prev_rank < rank:
            diff = rank - prev_rank
            movement = f"{Colors.SOFT_RED}▼{diff}{Colors.RESET}"
        else:
            movement = f"{Colors.LIGHT_GRAY}—0{Colors.RESET}"

        # Top 3 medals
        if rank == 1:
            medal = " 🥇"
        elif rank == 2:
            medal = " 🥈"
        elif rank == 3:
            medal = " 🥉"
        else:
            medal = f"{rank:>2}."

        bar_length = min(10, p.total_points // 50)
        points_bar = "█" * bar_length + "░" * (10 - bar_length)

        print(
            f"{medal} {p.name:<15} | Points: {p.total_points:<4} [{points_bar:<10}] "
            f"| Elims: {p.total_elims:<2} 🗡️ | Wins: {p.wins:<2} ⭐ | {movement}"
        )

    previous_player_ranks = {p.name: idx + 1 for idx, p in enumerate(full_ranking)}

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sim_sleep(2)


def print_tournament_win_ticker(players, current_match, total_matches):
    remaining = total_matches - current_match
    if remaining <= 0 or not players:
        return

    projections = []
    
    for p in players:
        if not p.placements:
            continue
        games_played = len(p.placements)
        avg_place_pts = placement_points(sum(p.placements) / games_played)
        avg_elim_pts = (p.total_elims / games_played) * CONFIG["elim_points"]
        expected_gain = (avg_place_pts + avg_elim_pts) * remaining
        
        conf_boost = p.confidence * 0.15 * remaining * CONFIG["elim_points"]
        projected = p.total_points + expected_gain + conf_boost


        projections.append((projected, p.total_points, p.wins, p))

    if not projections:
        return

    scale = max(1, sum(p.total_points for _, ppts, _, p in projections) / len(projections) / 2)

    exp_scores = [math.exp(proj / scale) for proj, _, _, _ in projections]
    total_exp = sum(exp_scores)

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"WIN % TICKER – GAME {current_match}/{total_matches} (Remaining: {remaining})")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Sort by projected points
    projections.sort(key=lambda x: x[0], reverse=True)

    for i, (proj_pts, curr_pts, wins, p) in enumerate(projections[:6]):
        chance = (math.exp(proj_pts / scale) / total_exp) * 100
        chance = max(0.5, min(99.5, chance))
        
        bar_len = int(chance / 12.5)
        bar = "█" * bar_len + "░" * (8 - bar_len)
        
        print(f"{i+1:>2}. {display_name(p):<15} {chance:>5.1f}% [{bar}] ({curr_pts} pts)")
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sim_sleep(1.5)


def get_victory_commentary(winner, match_number: int, total_matches: int):
    wins = winner.wins
    prev_wins = getattr(winner, "previous_wins", wins - 1)
    name = winner.name

    if wins == 1:
        if match_number == 1:
            commentary = [
                "Opens the tournament with a massive statement.",
                "First game. First win. You couldn’t script it better.",
                "Starts the day absolutely on fire.",
                "Sets the tone early — this lobby has been warned.",
                f"Coming in hot! {name} steals a win in the first game.",
                "They came, they dropped, they dominated.",
                "First blood? Nah, first ROYALE. {name} is cooking!",
                "The lobby did not see this coming.",
                "Already making the scoreboard sweat.",
                "Drops like a hammer, wins like a pro.",
                f"{name} just showed everyone that 'warm-up game' is a myth.",
                "Someone call the fire department — this lobby is on blaze.",
                "First game jitters? Not here.",
                "That's one for the highlight reel... if they don't mess up next match.",
                "First blood, first bragging rights.",
                "They came, they saw, they conquered game one.",
                "Lobby's still waking up, and they're already winning.",
                "Opens the day like they own the lobby.",
                "Kickstarts the tournament with style points.",
                "A calm start? Forget it, this is chaos already!",
            ]
        elif match_number == total_matches:
            commentary = [
                "Leaves it until the final game — and delivers.",
                "First win in the LAST possible moment.",
                "When it mattered most, they showed up.",
                "Ice in the veins — unbelievable timing.",
                "Saved it for the final game — ice cold!",
                f"{name} just wins in dramatic fashion. Someone cue the music.",
                "Final game energy: cinematic edition.",
                "That win should come with a soundtrack.",
                "Closes it out like a true champion.",
                "That final push was a statement nobody will forget.",
                "Tournament finale? Nailed it.",
                "All the pressure, all the stakes... and they're still smiling.",
                "Saved the best for last. Or maybe just got lucky.",
            ]
        else:
            commentary = [
                "Gets the monkey off their back.",
                "Finally breaks through with their first win.",    
                "That pressure has been building all tournament.",
                "They’ve been knocking on the door -- now it’s kicked in.",
                "Persistence pays off in a big way.",
                "The first of many? Only time will tell.",
                f"{name} proves why they’re still in the race.",
                "That awkward moment when everyone else is still landing.",
                "They win, and you just sit there like 'ok… wow.'",
                "Suddenly, the lobby realizes they might be in trouble.",
                "Took a few tries, but they finally cracked it.",
                "Finally found their rythym -- lobby beware.",
                "Monkey off back, now they're swinging through the leaderboard.",
                "That's the spark they needed to catch fire.",
                "Well, about time... we were starting to worry.",
                f"Took you long enough, {name}...",
                "Casters are questioning if anyone else even exists.",
                "Takes the crown they've been chasing.",
                "Breaks the streak, earns the respect.",
                "Finally puts that one to bed.",
                "The pressure valve has officially popped!",
                
            ]

    elif wins >= 2 and prev_wins == wins - 1:
        if wins == 2:
            commentary = [
                "Back-to-back wins to start the tournament.",
                "Two games. Two victories. Unreal pace.",
                "No cooldown between wins — straight dominance.",
                "The rest of the lobby is already chasing.",
                f"Back-to-back! {name} is on FIRE!",
                "Somebody check if this is a new exploit.",
                f"{name} is just here to collect trophies, apparently.",
                "Even the virtual fans are standing up.",
                "Double trouble -- they're untouchable!",
                "The streak is real, and it's scary.",
                "If this keeps up, we'll need a new rulebook.",
                "They're on a mission... and the rest are just extras.",
            ]
        elif wins == 3:
            commentary = [
                "That’s three wins in a row.",
                "Absolute control of the tournament.",
                "This is starting to feel inevitable.",
                "Pure dominance from start to finish.",
                "This is turning into a solo highlight reel.",
                f"{name} just broke the 'fun for others' rule.",
                "If the lobby had a scoreboard fear factor, it’s off the charts.",
                "Three games, zero mercy, infinite swagger.",
            ]
        else:
            commentary = [
                f"{wins} wins in a row — this is unreal.",
                "Every fight feels unfair.",
                "They are dictating the entire tournament.",
                "Historic-level dominance right here.",
                f"{wins} in a row — the rest of the lobby is just renting space.",
                f"{name} could be streaming in VR and still win the lobby.",
                "Somebody check the physics — is this even possible?",
                "The rest of the lobby might just start playing hide-and-seek.",
            ]

    else:
        if match_number == total_matches:
            commentary = [
                "Closes out the tournament with a huge win.",
                "Final game, final statement.",
                "They saved something special for the end.",
                "That win will be remembered.",
                f"{name} wins, and everyone else collectively facepalms.",
                "That moment when you realize you’re watching a legend in action.",
                "Final game glory: meme edition.",
            ]
        else:
            commentary = [
                f"That’s win number {wins} of the tournament.",
                "Keeps themselves firmly in the title race.",
                "Consistency like this wins tournaments.",
                f"{name} just casually reminds everyone who's boss.",
                "The lobby collectively sighs in despair.",
                "Somebody tell the others: it’s over… for now.",
                "Momentum is officially theirs.",
                "Who gave them the lobby keys?",
                f"{wins} wins? Somebody call the mata police.",
                f"Yup, {name}'s getting nerfed next update.",
                "Skill checks? They're passing with flying colours!",
                "Collectors of victories, masters of mayhem.",
                f"Skill level: over {wins}000.",
                "They don't chase the leaderboard -- it runs from them.",
                "The lobby called, they want their dignity back.",
                "Their highlight reel just got another clip.",
            ]

        return f"{random.choice(commentary)}"

    return random.choice(commentary)



def update_tournament_context(players: List[Player]):
    leaderboard = sorted(
        players,
        key=lambda p: (
            p.total_points,
            p.wins,
            p.total_elims,
            -p.average_placement
        ),
        reverse=True
    )

    for idx, p in enumerate(leaderboard):
        p.current_rank = idx + 1

        if idx == 0:
            p.points_to_first = 0
        else:
            p.points_to_first = leaderboard[0].total_points - p.total_points

        if idx > 0:
            p.points_to_above = leaderboard[idx - 1].total_points - p.total_points
        else:
            p.points_to_above = 0

        if idx < len(leaderboard) - 1:
            p.points_to_below = p.total_points - leaderboard[idx + 1].total_points
        else:
            p.points_to_below = 999

        p.safety_margin = p.points_to_below



def update_player_strategy(player: Player, match_number: int):
    pressure = match_number / CONFIG["matches"]


    risk = 0.4


    if player.points_to_first > 40:
        risk += 0.2


    if 0 < player.points_to_first <= 30:
        risk += 0.35


    if player.safety_margin >= 60:
        player.grief_bias = 0.7
        risk += 0.15
    elif player.safety_margin <= 15:
        player.grief_bias = 0.1
        risk -= 0.2
    else:
        player.grief_bias = 0.3


    risk += pressure * 0.25

    player.risk_tolerance = max(0.2, min(1.0, risk))
    

def choose_attacker(players):
    weights = []
    for p in players:
        w = p.skill * (0.7 + p.risk_tolerance)
        weights.append(max(w, 1))
    return random.choices(players, weights=weights, k=1)[0]


def choose_target(attacker, players):
    targets = [p for p in players if p != attacker]

    weights = []
    for t in targets:
        w = t.skill


        if attacker.grief_bias > 0 and t.current_rank < attacker.current_rank:
            w *= (1 + attacker.grief_bias)

        hatred = attacker.rivals.get(t.id, 0)
        w *= (1 + hatred * 0.25)


        fear = attacker.fear.get(t.id, 0)
        w *= max(0.4, 1 - fear * 0.15)


        if t.current_rank > 50:
            w *= 0.7

        weights.append(max(w, 1))

    return random.choices(targets, weights=weights, k=1)[0]



def register_elim(killer: Player, victim: Player):

    killer.rivals[victim.id] = killer.rivals.get(victim.id, 0) + 1


    victim.fear[killer.id] = victim.fear.get(killer.id, 0) + 1


def simulate_match(players: List[Player], match_number: int):
    update_tournament_context(players)

    for p in players:
        update_player_strategy(p, match_number)

    for mod in ACTIVE_MODS:
        if mod.enabled:
            mod.on_match_start(players, match_number, CONFIG)

    print("\n" + "━" * 50)
    print(f"🪂 GAME {match_number} — BATTLE BUS LAUNCHING")
    print("━" * 50)
    sim_sleep(1)

    print(f"🏝️ {len(players)} players drop into the island")
    sim_sleep(1)

    print(f"Storm Circles: {CONFIG['storm_circles']}")
    sim_sleep(0.8)
    print(f"Elim Points: {CONFIG['elim_points']}\n")
    sim_sleep(1)


    top_players = sorted(players, key=lambda p: p.total_points, reverse=True)[:3]
    print("⭐ Players to Watch")
    for p in top_players:
        print(f"• {display_name(p)}")
        sim_sleep(0.3)

    print("\n🚐 Bus launches in 3…")
    sim_sleep(1)
    print("2…")
    sim_sleep(1)
    print("1…")
    sim_sleep(1)
    print("━" * 50)
    sim_sleep(0.5)

    pois = generate_pois()
    assign_drops(players, pois)

    print("\nPlayer drop assignments (sample 10):")
    for p in players[:10]:
        print(f"{p.name} -> {p.drop_poi}")
        sim_sleep(0.3)
    if len(players) > 10:
        print(f"...and {len(players)-10} more players")
        sim_sleep(0.5)

    print("\n🪂 Players are now landing on the island…")
    sim_sleep(2)


    pre_dead_count = 0
    for player in players:
        for mod in ACTIVE_MODS:
            if mod.enabled:
                result = mod.on_player_spawn(player, match_number, CONFIG)
                if result in ("NO_LOAD", "CRASH"):
                    pre_dead_count += 1
                    reason = "didn't load in" if result == "NO_LOAD" else "crashed"
                    print(f"{'❌' if result == 'NO_LOAD' else '💥'} {Colors.SOFT_RED}{display_name(player)} {reason}! {Colors.RESET}")
                    player.alive = False

    if pre_dead_count > 0:
        print(f"\n⚠️  {pre_dead_count} player(s) eliminated before fights began\n")
        sim_sleep(1.2)


    alive = [p for p in players if p.alive]
    current_placement = len(alive)
    placements = {}
    elims = {p.id: 0 for p in players}
    
    rage_quitters = [p for p in players if getattr(p, '_has_rage_quit', False)]
    if rage_quitters:
        print(f"\n{Colors.SOFT_RED + Colors.BOLD}😤 {len(rage_quitters)} player(s) have rage quit and won't play this match!{Colors.RESET}")
        rage_quitters.sort(key=lambda p: p.skill)
        next_placement = len(players)
        for p in rage_quitters:
            placements[p.id] = next_placement
            next_placement -= 1
            p.alive = False
            elims[p.id] = 0
        sim_sleep(1.5)   
        
    alive = [p for p in players if p.alive]
    current_placement = len(alive)

    if len(alive) <= 1:
        print("Match aborted — no one left alive after spawn events.")
        return

    random.shuffle(alive)


    late_game = match_number >= CONFIG["matches"] - 2

    def should_fight(attacker, defender):
        if defender.skill > attacker.skill + 15:
            return False
        if attacker.skill > defender.skill + 10:
            return True
        if late_game and attacker.points_to_first < 50:
            return random.random() < 0.8
        if attacker.safety_margin > 80 and attacker.points_to_first > 50:
            return random.random() < 0.4
        if attacker.confidence > 0.6:
            return True
        fear = attacker.fear.get(defender.id, 0)
        if fear > 2:
            return random.random() < 0.3
        return random.random() < attacker.risk_tolerance

    def get_attack_weight(player, target):
        base = player.skill
        if player.archetype == "Fragger": base *= 1.2
        elif player.archetype == "Aggressive": base *= 1.35
        elif player.archetype == "Passive": base *= 0.8
        base *= (1.0 + player.confidence * 0.15)
        fear_level = player.fear.get(target.id, 0)
        base *= max(0.65, 1 - fear_level * 0.08)
        if late_game and player.skill >= 85:
            base *= 1.1
        return max(base, 1)

    def get_defense_weight(player, attacker):
        base = player.skill
        if player.archetype == "Passive": base *= 1.1
        elif player.archetype == "Aggressive": base *= 0.9
        base *= (1.0 + player.confidence * 0.1)
        fear_level = player.fear.get(attacker.id, 0)
        base *= max(0.65, 1 - fear_level * 0.08)
        return max(base, 1)

    while len(alive) > 1:
        attacker = choose_attacker(alive)
        defender = choose_target(attacker, alive)

        if not attacker.alive or not defender.alive:
            alive = [p for p in alive if p.alive]
            continue

        allow_fight = True
        for mod in ACTIVE_MODS:
            if mod.enabled:
                if not mod.on_fight(attacker, defender, CONFIG):
                    allow_fight = False
                    break

        if not allow_fight:
            continue

        if not should_fight(attacker, defender):
            continue

        p1, p2 = attacker, defender

        atk1 = get_attack_weight(p1, p2)
        def2 = get_defense_weight(p2, p1)

        p1_win_chance = atk1 / (atk1 + def2)
        skill_gap = abs(p1.skill - p2.skill)
        variance_modifier = max(0.25, 1 - skill_gap / 100)
        roll = random.random() * variance_modifier

        if roll < p1_win_chance:
            p2.alive = False
            alive.remove(p2)
            elims[p1.id] += 1
            register_elim(p1, p2)
            placements[p2.id] = current_placement
            current_placement -= 1
            emoji = "🌩️" if random.random() < 0.05 else "⚔️"
            print(f"{display_name(p1)} {emoji} {display_name(p2)} {Colors.LIGHT_GRAY}(Placement: {placements[p2.id]}){Colors.RESET}")
            for mod in ACTIVE_MODS:
                if mod.enabled:
                    mod.on_player_eliminated(p2, p1, CONFIG)
        else:
            p1.alive = False
            alive.remove(p1)
            elims[p2.id] += 1
            register_elim(p2, p1)
            placements[p1.id] = current_placement
            current_placement -= 1
            emoji = "🌩️" if random.random() < 0.05 else "⚔️"
            print(f"{display_name(p2)} {emoji} {display_name(p1)} {Colors.LIGHT_GRAY}(Placement: {placements[p1.id]}){Colors.RESET}")
            for mod in ACTIVE_MODS:
                if mod.enabled:
                    mod.on_player_eliminated(p1, p2, CONFIG)

        sim_sleep(0.25)

    pre_dead_players = [p for p in players if p.id not in placements and not p.alive]
    if pre_dead_players:

        pre_dead_players.sort(key=lambda p: p.skill)
        next_placement = len(players)
        for p in pre_dead_players:
            placements[p.id] = next_placement
            next_placement -= 1

        print(f"📊 {len(pre_dead_players)} pre-match eliminations assigned bottom placements")


    if not alive:
        print("No winner — everyone eliminated before end?")
        return

    winner = alive[0]
    placements[winner.id] = 1
    winner.alive = True
    if CONFIG["tournament_type"] == "VICTORY_CUP":
        winner.career_victorycup_wins += 1


    for p in players:
        placement = placements.get(p.id, len(players))
        elim_count = elims.get(p.id, 0)

        t_type = CONFIG["tournament_type"]
        if t_type == "VICTORY_CUP":
            pts = TOURNAMENT_TYPES[t_type]["points_per_win"] if placement == 1 else 0
        else:
            pts = placement_points(placement) + elim_count * CONFIG["elim_points"]

        p.add_match_result(placement, elim_count, pts)

    winner.previous_wins = winner.wins
    commentary = get_victory_commentary(winner, match_number, CONFIG["matches"])


    print("\n" + "━" * 50)
    print(f"🟩🟩🟩 #1 VICTORY ROYALE - GAME {match_number} 🟩🟩🟩")
    print("━" * 50)
    sim_sleep(1)

    print(f"\n🏆 {display_name(winner)}")
    sim_sleep(0.5)
    print(f"• Match Kills: {elims.get(winner.id, 0)}")
    sim_sleep(0.5)
    print(f"• Placement Points: {placement_points(1)}")
    sim_sleep(0.5)
    print(f"• Total Points: {winner.total_points}")
    sim_sleep(1)

    print(f"\n👑 {commentary}\n")
    sim_sleep(1)
    print("━" * 50)
    sim_sleep(1)
			
    for mod in ACTIVE_MODS:
        if mod.enabled and hasattr(mod, 'on_match_end'):
            mod.on_match_end(players, winner, CONFIG)

    update_confidence(players)
    print_top10_cumulative(players)
    
    if CONFIG.get("show_win_tickers", True):
        halfway_game = CONFIG["matches"] // 2
        before_final_game = CONFIG["matches"] - 1

        if match_number == halfway_game or match_number == before_final_game:
            if match_number == halfway_game:
                print("\n🎙️ Caster: Let's check the odds before the second half of the tournament...")
                sim_sleep(2)
                print("\n" + "─" * 50 )
                print("HALFTIME UPDATE – WIN % TICKER")
            else:
                print("\n🎙️ Caster: Quick odds check before the final drop...")
                sim_sleep(2)
                print("\n" + "─" * 50 )
                print("FINAL GAME SETUP – WIN % TICKER")
            print("─" * 50)
    
            print_tournament_win_ticker(players, match_number, CONFIG["matches"])
    
        sim_sleep(1.2)
    sim_sleep(1)
    print(f"\nMatch {match_number} complete! ✅")
    print("·" * 40)
    sim_sleep(1)
    
def walkout_hype(players: List[Player], count=15):
    import random
    top_players = [p for p in players if 90 <= p.skill <= 113]
    if not top_players:
        return

    hype_players = random.sample(top_players, min(count, len(top_players)))

    hype_lines = [
		"🔥 Domination is key for {Colors.BOLD}{player}{Colors.RESET}! Eyes on the prize today, no stopping at 2nd place!",
		"🎮 Watch out, {Colors.BOLD}{player}{Colors.RESET} is coming in hot-- expect a masterclass in elimination!",
		"🏆 The crowd is cheering! {Colors.BOLD}{player}{Colors.RESET} is ready to turn this tournament upside down!",
		"⚡ {Colors.BOLD}{player}{Colors.RESET} is feeling unstoppable today! Keep your eyes on the feed!",
		"👀 All eyes on {Colors.BOLD}{player}{Colors.RESET}! Every move counts in this tournament!",
		"🧠 Give it up for {Colors.BOLD}{player}{Colors.RESET}! Plenty of experience, but will it be enough to take them to the top?",
		"🍀 They say fortune favors the bold-- {Colors.BOLD}{player}{Colors.RESET} is ready to prove it!",
		"🔥 All eyes on {Colors.BOLD}{player}{Colors.RESET}! Today, domination isn’t optional… it’s mandatory!",
		"🎯 {Colors.BOLD}{player}{Colors.RESET} is ready to snatch the crown… will anyone stand in their way?",
		"🍳 Rumor has it {Colors.BOLD}{player}{Colors.RESET} eats elimination points for breakfast!",
		"🕹️ The LAN gods favor {Colors.BOLD}{player}{Colors.RESET}… will they answer the call?",
		"💎 Precision, power, and poise -- {Colors.BOLD}{player}{Colors.RESET} is a one-person highlight reel!",
		"🥳 {Colors.BOLD}{player}{Colors.RESET} doesn’t just drop… {Colors.BOLD}{player}{Colors.RESET} descends with flair!",
		"🍕 They say {Colors.BOLD}{player}{Colors.RESET} fuels up on pizza and pure aggression!",
		"🦄 {Colors.BOLD}{player}{Colors.RESET} is magical… but deadly. Expect the unexpected!",
		"👑 {Colors.BOLD}{player}{Colors.RESET} walks in like royalty… the throne is up for grabs!",
		"🎲 RNG, beware -- {Colors.BOLD}{player}{Colors.RESET} laughs in the face of chance!",
		"🎉 {Colors.BOLD}{player}{Colors.RESET} is partying and slaying… simultaneously!",
		"👀 {Colors.BOLD}{player}{Colors.RESET} sees everything… and so does your defeat!",
		"💥 {Colors.BOLD}{player}{Colors.RESET} brings chaos… and maybe a little bit of glitter!",
		"🛡️ Shields? What shields? {Colors.BOLD}{player}{Colors.RESET} melts 'em on sight!",
		"💥 Lobby panic mode: {Colors.BOLD}{player}{Colors.RESET} just stepped onto the stage!",
		"💪 Full send or bust-- {Colors.BOLD}{player}'s{Colors.RESET} locked and loaded.",
        "🔥 {Colors.BOLD}{player}{Colors.RESET} is walking in like they own the lobby… and maybe the tournament too!",
	    "🎮 Watch {Colors.BOLD}{player}{Colors.RESET} drop like a meteor — chaos incoming!",
	    "⚡ Lightning in human form: {Colors.BOLD}{player}{Colors.RESET} just entered the arena!",
	    "👀 Eyes peeled! {Colors.BOLD}{player}{Colors.RESET} is scanning, aiming, and ready to slay!",
	    "👻 Spooky or not, {Colors.BOLD}{player}{Colors.RESET} haunts the leaderboard with style.",
	    "🥷 Silent but deadly: {Colors.BOLD}{player}{Colors.RESET} just entered the battlefield.",    
]


    print("\n" + Colors.SOFT_PURPLE + "🏟️ TOURNAMENT HYPE WALKOUTS 🏟️" + Colors.RESET)
    print("━" * 50)
    sim_sleep(2)

    for p in hype_players:
        if not hype_lines:
            break
        line_template = random.choice(hype_lines)
        hype_lines.remove(line_template)
        line = line_template.format(player=p.name, Colors=Colors)
        for char in line:
            print(char, end="", flush=True)
            sim_sleep(0.04)
        print("\n")
        sim_sleep(1.5)
    print("━" * 50 + "\n")
    sim_sleep(2)




def simulate_tournament():
    new_seed = random.randint(1,1_000_000)
    CONFIG["random_seed"] = new_seed
    random.seed(new_seed)
    save_config(CONFIG)
    pro_players_skills = get_pro_players_from_config()

	
    players = []


    for i, (name, skill, arch, org) in enumerate(pro_players_skills):
        players.append(Player(
            id=i,
            name=name,
            skill=skill,
            archetype=arch,
            org=org
        ))


    for i in range(len(pro_players_skills), CONFIG["players"]):
        players.append(Player(
            id=i,
            name=f"Fill_{i+1}",
            skill=random.randint(1, 75)
        ))

    assign_archetypes(players)


    load_career_data(players)

    if CONFIG.get("walkouts", False):
        walkout_hype(players)

    for match_number in range(1, CONFIG["matches"] + 1):
        simulate_match(players, match_number)


    update_careers(players)
    save_career_data(players)
    init_season_players(players)
    update_season_stats(players)
    if SEASON["tournaments_played"] >= SEASON["tournaments_per_season"]:
        end_season()

    return players

def sort_leaderboard(players: List[Player]):
    players.sort(
        key=lambda p: (p.total_points, p.wins, p.total_elims, -p.average_placement),
        reverse=True
    )
    return players

def print_leaderboard(players: List[Player]):
    console.print("\n" + "━"*60)
    console.print(" FINAL FORTNITE TOURNAMENT LEADERBOARD")
    console.print("━"*60)

    table = Table(show_header=True, header_style=None)

    table.add_column("RANK", justify="right", width=4)
    table.add_column("PLAYER", width=12)
    table.add_column("POINTS", justify="right", width=7)
    table.add_column("ELIMS", justify="right", width=5)
    table.add_column("WINS", justify="right", width=5)
    table.add_column("AVG PLACE", justify="right")
    table.add_column("EARNINGS", justify="right")

    for rank, p in enumerate(players, 1):
        rank_display = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, str(rank))
        table.add_row(
            str(rank_display),
            p.name,
            str(p.total_points),
            str(p.total_elims),
            str(p.wins),
            f"{p.average_placement:.2f}",
            f"+${p.tournament_earnings:,}"
        )

    console.print(table)
    console.print("━"*60)

def update_careers(players: List[Player]):
    leaderboard = sort_leaderboard(players)
    t_type = CONFIG["tournament_type"]

    for rank, p in enumerate(leaderboard, 1):
        p.career_tournaments += 1
        p.career_kills += p.total_elims
        p.best_finish = min(p.best_finish, rank)
        earned = get_prize_for_rank(rank, p)
        p.career_earnings += earned
        p.tournament_earnings = earned

        if rank == 1 and t_type != "VICTORY_CUP":
            p.career_wins += 1
            if t_type == "CASH_CUP":
                p.career_cashcup_wins += 1
            elif t_type == "FNCS":
                p.career_fncs_wins += 1
            elif t_type == "LAN":
                p.career_lan_wins += 1
                
def update_season_stats(players):
    for p in players:
        s = SEASON["season_players"][p.name]
        s["points"] += p.total_points
        s["wins"] += p.wins
        s["elims"] += p.total_elims
        s["earnings"] += p.tournament_earnings

    SEASON["tournaments_played"] += 1
    save_season()
    
def end_season():
    leaderboard = sorted(
        SEASON["season_players"].items(),
        key=lambda x: (x[1]["earnings"], x[1]["points"], x[1]["wins"], x[1]["elims"]),
        reverse=True
    )
    champion, stats = leaderboard[0]
    SEASON["history"].append({
        "season": SEASON["current_season"],
        "champion": champion,
        "leaderboard": leaderboard[:10]
    })
    mvp_quotes = [
        f"{champion} just proved why they're built different.",
        f"{champion}: 'I didn't hear no bell.'",
        f"{champion} carrying the lobby like it's solos.",
        "Talk to the hand, because the leaderboard speaks for itself.",
        f"{champion} didn't come to play — they came to win.",
        f"From the shadows to the top. {champion} just did that.",
        f"{champion} turned doubters into viewers.",
        "Ice in the veins. Fire in the stats.",
        f"{champion}: 'They said I couldn't. I said watch me.'",
        "The crown fits. Always did.",
        f"{champion} didn't just win — they owned the meta.",
        f"When legends are made, {champion} was taking notes... then wrote the book.",
        f"{champion} walked so the rest could place 2nd.",
        f"{champion}: still undefeated in vibes."
    ]
    print("\n" + "━" * 60)
    print(f"🏁 SEASON {SEASON['current_season']} COMPLETE")
    print("━" * 60)
    print(f"👑 MVP: {champion}")
    print(f"⭐ Earnings: ${stats['earnings']:,} | Points: {stats['points']} | Wins: {stats['wins']} | Elims: {stats['elims']}")
    print(f"   MVP Quote: {random.choice(mvp_quotes)}")
    print("━" * 60)
    # Reset season
    SEASON["current_season"] += 1
    SEASON["tournaments_played"] = 0
    SEASON["season_players"] = {}
    save_season()



def get_org_players(players, org_name):
    return [p for p in players if p.org.lower() == org_name.lower()]

def show_org_page(org_name, players):
    org_players = get_org_players(players, org_name)
    if not org_players:
        print("No players found for this org.")
        return

    total_earnings = sum(p.career_earnings for p in org_players)
    total_wins = sum(p.career_wins for p in org_players)
    total_players = len(org_players)
    earnings_per_player = total_earnings / total_players if total_players else 0


    all_placements = []
    for p in org_players:
        all_placements.extend(p.placements)
    consistency = sum(all_placements) / len(all_placements) if all_placements else 0

    best_player = max(org_players, key=lambda p: p.career_earnings)

    print(f"\n🏢 ORG PAGE — {org_name}")
    print("━" * 60)
    print(f"Players: {total_players}")
    print(f"Total Earnings: ${total_earnings:,}")
    print(f"Total Wins: {total_wins}")
    print(f"Earnings per Player: ${earnings_per_player:,.0f}")
    print(f"Consistency Rating (avg placement): {consistency:.2f}")
    print("━" * 60)

    print(f"\n⭐ Best Player")
    print(f"{best_player.name}")
    print(f"• Earnings: ${best_player.career_earnings:,}")
    print(f"• Wins: {best_player.career_wins}")

    print(f"\n📊 Player Performance")
    print(f"{'Player':<15}{'Wins':<6}{'Kills':<8}{'Earnings'}")
    print("━" * 60)
    for p in sorted(org_players, key=lambda p: p.career_earnings, reverse=True):
        print(f"{display_name(p):<16}{p.career_wins:<6}{p.career_kills:<8}${p.career_earnings:,}")
    print("━" * 60)

def show_player_history(players: List[Player]):
    sorted_players = sort_leaderboard(players)
    while True:
        user_input = input(
            "\nEnter a placement number, player name, org name, "
            "or 'career' for career leaderboard, "
            "or 'season' for current season leaderboard, "
            "or 'q' to quit: "
        ).strip().lower()

        if user_input == 'q':
            break

        if user_input == "career":
            career_players = [p for p in sorted_players if hasattr(p, "career_earnings")]
            if not career_players:
                print("No career data available yet.")
                continue

            sort_option = input("Sort by (earnings/kills/wins/tournaments/orgs): ").lower()
            if sort_option not in ["earnings", "kills", "wins", "tournaments", "orgs"]:
                print("Invalid option, defaulting to earnings.")
                sort_option = "earnings"

            if sort_option == "orgs":
                org_totals = {}
                for p in career_players:
                    if p.org != "Free Agent":
                        org_totals[p.org] = org_totals.get(p.org, 0) + p.career_earnings

                sorted_orgs = sorted(org_totals.items(), key=lambda x: x[1], reverse=True)

                table = Table(show_header=True, header_style=None)

                table.add_column("Rank", justify="right", width=6)
                table.add_column("Org", width=20)
                table.add_column("Total Earnings", justify="right")

                for rank, (org_name, earnings) in enumerate(sorted_orgs, 1):
                    table.add_row(
                        str(rank),
                        org_name,
                        f"${earnings:,}"
                    )

                console.print()
                console.print(table)
                continue


            if sort_option == "earnings":
                career_players.sort(key=lambda p: p.career_earnings, reverse=True)
            elif sort_option == "kills":
                career_players.sort(key=lambda p: p.career_kills, reverse=True)
            elif sort_option == "wins":
                career_players.sort(key=lambda p: p.career_wins, reverse=True)
            elif sort_option == "tournaments":
                career_players.sort(key=lambda p: p.career_tournaments, reverse=True)

            table = Table(title=" CAREER LEADERBOARD ")

            table.add_column("Rank", justify="right")
            table.add_column("Player")
            table.add_column("Wins", justify="right")
            table.add_column("Tournaments", justify="right")
            table.add_column("Kills", justify="right")
            table.add_column("Earnings", justify="right")

            for rank, p in enumerate(career_players, 1):
                table.add_row(
                    str(rank),
                    p.name,
                    str(p.career_wins),
                    str(p.career_tournaments),
                    str(p.career_kills),
                    f"${p.career_earnings:,}"
                )

            console.print(table)

        elif user_input == "season":
            if not SEASON["season_players"]:
                print("No season data yet — play some tournaments!")
                continue

            active_names = {p.name for p in players}

            season_players = []
            for name, stats in SEASON["season_players"].items():
                if name not in active_names:
                    continue

                player = next((p for p in sorted_players if p.name == name), None)
                season_players.append((player, name, stats))


            sort_option = input("Sort by (earnings/points/wins/elims): ").lower()
            if sort_option == "points":
                season_players.sort(key=lambda x: x[2]["points"], reverse=True)
            elif sort_option == "wins":
                season_players.sort(key=lambda x: x[2]["wins"], reverse=True)
            elif sort_option == "elims":
                season_players.sort(key=lambda x: x[2]["elims"], reverse=True)
            else:
                season_players.sort(key=lambda x: x[2]["earnings"], reverse=True)

            table = Table(show_header=True, header_style=None)

            table.add_column("Rank", justify="right", width=6)
            table.add_column("Player", width=15)
            table.add_column("Points", justify="right", width=8)
            table.add_column("Wins", justify="right", width=6)
            table.add_column("Elims", justify="right", width=8)
            table.add_column("Earnings", justify="right")

            for rank, (p, name, stats) in enumerate(season_players, 1):
                display_name = p.name if p else name
                table.add_row(
                    str(rank),
                    display_name,
                    str(stats["points"]),
                    str(stats["wins"]),
                    str(stats["elims"]),
                    f"${stats['earnings']:,}"
                )

            console.print()
            console.print(table)
            continue


        player = None
        if user_input.isdigit():
            rank = int(user_input)
            if 1 <= rank <= len(players):
                player = sorted_players[rank-1]
            else:
                print(f"Please enter a valid rank between 1 and {len(players)}.")
                continue
        else:
            org_names = {p.org.lower() for p in sorted_players if p.org != "Free Agent"}
            if user_input in org_names:
                show_org_page(user_input, sorted_players)
                continue

            matches = [p for p in sorted_players if user_input in p.name.lower()]
            if len(matches) == 0:
                print(f"No players found matching '{user_input}'.")
                continue
            elif len(matches) == 1:
                player = matches[0]
            else:
                print("Multiple matches found:")
                for idx, p in enumerate(matches, 1):
                    print(f"{idx}. {p.name}")
                choice = input("Enter the number of the player you want: ")
                if not choice.isdigit() or not (1 <= int(choice) <= len(matches)):
                    print("Invalid choice. Try again.")
                    continue
                player = matches[int(choice)-1]

        if player:
            rank = sorted_players.index(player) + 1

            console.print(f"\n{player.name}")
            console.print(f"{player.org}")
            console.print(f"Ranking: #{rank}")
            console.print(f"Total Points: {player.total_points}")
            console.print(f"Total Kills: {player.total_elims}")
            console.print(f"Total Wins: {player.wins}\n")

            table = Table(title="MATCH HISTORY", show_lines=True)
            table.add_column("MATCH", justify="left", style="")
            table.add_column("PLACEMENT", justify="left", style="")
            table.add_column("KILLS", justify="left", style="")

            for idx, (placement, kills) in enumerate(zip(player.placements, player.match_kills), 1):
                table.add_row(str(idx), str(placement), str(kills))

            console.print(table)

            if hasattr(player, "career_earnings"):
                print(f"\n🏅 Career Stats for {player.name}")
                print(f"Total Tournament Wins: {player.career_wins}")
                print(f"Total Cash Cup Wins: {player.career_cashcup_wins}")
                print(f"Total Victory Cup Game Wins: {player.career_victorycup_wins}")
                print(f"Total FNCS Wins: {player.career_fncs_wins}")
                print(f"Total LAN Wins: {player.career_lan_wins}")
                print(f"Total Tournaments: {player.career_tournaments}")
                print(f"Total Kills: {player.career_kills}")
                print(f"Total Earnings: ${player.career_earnings:,}")
                print(f"Best Finish: {player.best_finish}")

            if player.name in SEASON["season_players"]:
                s = SEASON["season_players"][player.name]
                print(f"\n📆 Season {SEASON['current_season']} Stats")
                print(f"Season Points: {s['points']}")
                print(f"Season Wins: {s['wins']}")
                print(f"Season Elims: {s['elims']}")
                print(f"Season Earnings: ${s['earnings']:,}")


def export_tournament_results(players: List[Player], matches: int):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    t_type = CONFIG["tournament_type"]
    t_label = TOURNAMENT_TYPES[t_type]["label"]
    
    t_type = CONFIG["tournament_type"]
    t_label = TOURNAMENT_TYPES[t_type]["label"]

    safe_label = t_label.replace(" ", "")
    tournament_dir = os.path.join(TOURNAMENTS_ROOT, safe_label)

    os.makedirs(tournament_dir, exist_ok=True)
    region = CONFIG.get("region", "EU")


    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{safe_label}_{region}_{timestamp}.txt"
    filepath = os.path.join(tournament_dir, filename)


    sorted_players = sorted(
        players,
        key=lambda p: (p.total_points, p.wins, p.total_elims, -p.average_placement),
        reverse=True
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("FORTNITE TOURNAMENT SIMULATOR REPORT\n")
        f.write("═" * 55 + "\n")
        f.write(f"Tournament Type : {t_label}\n")
        f.write(f"Matches Played  : {matches}\n")
        f.write(f"Date            : {timestamp}\n")
        f.write("═" * 55 + "\n\n")

        f.write("MATCH RESULTS\n")
        f.write("─" * 55 + "\n")
        for match_num in range(1, matches + 1):
            winners = [p for p in players if p.placements[match_num - 1] == 1]
            winner = winners[0].name if winners else "Unknown"
            f.write(f"Game {match_num:<2} → {winner} 👑\n")
        f.write("\n")

        f.write("─" * 55 + "\n")
        f.write("FINAL LEADERBOARD\n")
        f.write("─" * 55 + "\n")
        f.write(
            f"{'Rank':<6}{'Player':<15}{'Points':<8}"
            f"{'Elims':<8}{'Wins':<6}{'Avg Place'}\n"
        )
        f.write("─" * 55 + "\n")

        for rank, p in enumerate(sorted_players, 1):
            f.write(
                f"{rank:<6}{p.name:<15}{p.total_points:<8}"
                f"{p.total_elims:<8}{p.wins:<6}{p.average_placement:.2f}\n"
            )

        # MVP
        mvp = sorted_players[0]
        f.write("\n")
        f.write("MVP OF THE TOURNAMENT\n")
        f.write("═" * 55 + "\n")
        f.write(
            f"{mvp.name} finishes 1st with "
            f"{mvp.total_points} points, "
            f"{mvp.total_elims} eliminations, "
            f"and {mvp.wins} wins.\n"
        )

        f.write("═" * 55 + "\n")

    print(f"📁 Tournament results exported to /tournaments/{safe_label}/{filename}")
 

def cycle_tournament_type():
    keys = list(TOURNAMENT_TYPES.keys())
    current = CONFIG["tournament_type"]
    idx = keys.index(current)
    CONFIG["tournament_type"] = keys[(idx + 1) % len(keys)]
    save_config(CONFIG)
    
def view_season_history():
    if not SEASON["history"]:
        print("No completed seasons yet.")
        return

    print("\n📜 SEASON HISTORY")
    print("━" * 50)
    for s in SEASON["history"]:
        print(f"Season {s['season']} — MVP: {s['champion']}")
        

def tournament_template_menu():
    keys = list(TOURNAMENT_TEMPLATES.keys())

    while True:
        print("\n" + "━" * 45)
        print("📋 TOURNAMENT TEMPLATES")
        print("━" * 45)

        for i, key in enumerate(keys, 1):
            label = TOURNAMENT_TEMPLATES[key]["label"]
            print(f"{i}. {label}")

        print("\nB. Back")
        print("━" * 45)

        choice = input("> ").strip().lower()

        if choice == "b":
            return

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(keys):
                apply_tournament_template(keys[idx])
                sim_sleep(1)
                return

        print("Invalid option.")
        

def print_season_progress_bar():
    played = SEASON["tournaments_played"]
    total = SEASON["tournaments_per_season"]
    
    if total == 0:
        print("Season progress: (no tournaments set)")
        return
    
    # Bar settings
    bar_length = 16
    filled = min(played, total)
    empty = bar_length - filled
    
    # Build the bar
    filled_char = "█"
    empty_char = "░"
    
    bar = (
        filled_char * filled +
        empty_char * empty
    )
    
    percent = (played / total) * 100 if total > 0 else 0
    
    print(f"[{bar}] ({percent:.0f}%)")


def main_menu():
    load_season()

    
    while True:
        print("\n" + "━" * 50)
        print(f"🏟️ FORTNITE TOURNAMENT SIM v{CONFIG['version']} ({CONFIG['build']})")   
        print("━" * 50)
        splash = random.choice(load_splash_texts())
        print(Colors.SOFT_PURPLE + Colors.ITALIC + splash + Colors.RESET)  
        print(f"\n📆 SEASON {SEASON['current_season']} - {CONFIG['region']}")
        print(f"Tournaments Played: {SEASON['tournaments_played']} / {SEASON['tournaments_per_season']}")   
        print_season_progress_bar()
        print("\n1. Start Tournament")
        print("2. Tournament Setup")
        print("3. View Season History")
        print("4. Tournament Templates")
        print("5. Mods & Extras")
        print("6. Patch Notes")
        print("0. Exit")
        print("━" * 50)
        
        choice = input("> ").strip()

        if choice == "1":
            print("\n🚀 Tournament starting...\n")
            sim_sleep(1)
            return "START"

        elif choice == "2":
            pre_tournament_menu()

        elif choice == "3":
            view_season_history()

        elif choice == "4":
            tournament_template_menu()

        elif choice == "5":
            while True:
                print("\n" + "━" * 45)
                print("🎮 MODS & EXTRAS")
                print("━" * 45)
                
                if not ACTIVE_MODS:
                    print("No mods loaded.")
                else:
                    print("Active mods:")
                    for i, mod in enumerate(ACTIVE_MODS, 1):
                        status = "ON" if mod.enabled else "OFF"
                        print(f"  {i}. [{status}] {mod.name}")
                
                print("\nCommands:")
                print("  t <number>   → toggle mod on/off")
                print("  r            → reset all mods to OFF")
                print("  b            → back to main menu")
                print("━" * 45)
                
                mod_choice = input("> ").strip().lower()
                
                if mod_choice == "b":
                    break
                    
                elif mod_choice == "r":
                    for mod in ACTIVE_MODS:
                        mod.enabled = False
                        save_active_mods(ACTIVE_MODS)
                    print("All mods have been reset to OFF.")
                    sim_sleep(1)
                    
                elif mod_choice.startswith("t "):
                    try:
                        idx = int(mod_choice.split()[1]) - 1
                        if 0 <= idx < len(ACTIVE_MODS):
                            mod = ACTIVE_MODS[idx]
                            mod.enabled = not mod.enabled
                            save_active_mods(ACTIVE_MODS)
                            status = "ON" if mod.enabled else "OFF"
                            print(f"→ {mod.name} is now {status}")
                            sim_sleep(0.8)
                        else:
                            print("Invalid mod number.")
                    except (ValueError, IndexError):
                        print("Invalid input. Use format: t 1")
                
                else:
                    print("Unknown command. Use t <number>, r, or b.")

        elif choice == "6":
            show_patch_notes()
        
        elif choice == "0":
            print("\nThanks for playing! See you next drop! 👋")
            exit()
            
        else:
            print("Invalid option.")


def show_patch_notes():
    print("\n" + "═" * 60)
    print("📜  PATCH NOTES  –  Fortnite Tournament Simulator")
    print("═" * 60)
    print("Last updated: January 17, 2026")
    print("")
    
    print("v1.1.3 - Small QOL Update (January 17, 2026)")
    print("──────────────────────────────────────") 
    print("✨ New")
    print("• Tournament leaderboard TXTs have been updated and are now stored in its own folder instead")
    print("• New season progress bar in the main menu")
    print("• Season length increased from 12 → 16 tournaments")
    print("• New toggleable win ticker, calculates probability of a player winning the tournament!")
    print("")
    print("🔧 Balance & Behaviour Tweaks")
    print("• Player skill calibration pass:")
    print(" Adjusted a small number of players' skill based on real, recent solo tournament results.")
    print(" These changes affect consistency, not guaranteed outcomes.")
    print(" Noticeable adjustments include:")
    print("  • Upl (slight increase)")
    print("  • Kombek (slight increase)")
    print("  • Blacha (slight increase)")
    print("  • Hris (slight increase)")
    print("")
    print("• Org roster changes:")
    print("  • Darm & Demus joined T1")
    print("")
    
     
    print("v1.1.2 - (January 12, 2026)")
    print("──────────────────────────────────────") 
    print("✨ New")
    print("• New mod: Rage Quit")
    print(" - Players can rage quit and refuse to play the rest of the tournament!")
    print(" - Occurs after enough bad placements or bad leaderboard placement")
    print("• New Rage Quit themed splash texts")
    print("• MVP quotes at the end of the season -- what does the MVP have to say?")
    print("")
    print("🔧 Balance & Behaviour Tweaks")
    print("• Player skill calibration pass:")
    print(" Adjusted a small number of players' skill based on real, recent solo tournament results.")
    print(" These changes affect consistency, not guaranteed outcomes.")
    print(" Noticeable adjustments include:")
    print("  • Akiira (slight increase)")
    print("  • Kurama (slight increase)")
    print("  • Werex (slight increase)")
    print("  • Seyyto (slight increase)")
    print("  • Pixx (slight increase)")
    print("  • Darm (slight increase)")
    print("  • Demus (slight increase)")
    print("  • IDrop (slight increase)")
    print("  • t3eny (slight decrease)")  
    print("")
    print("🐛 Fixes")
    print("• Prevented unintended stat carryover between matches")
    print("• Fixed cases where rage quit players have extra matches added to history")
    print("")
    print("🔮 Looking Ahead")
    print("• Major revamp of fight logic and engagements")
    print("• Save files and deeper season persistence")
    print("• Expanded regional player pools")
    print("")
    
    
    print("v1.1.1 Hotfix (January 10, 2026)")
    print("──────────────────────────────────────")
    print("• Fixed bug where crashed/no-loaded players would receive high placements")
    print("• Added new splash texts")
    print("• Org roster changes:")
    print("  - Kami left Al Qadsiah")
    print("  - Charyy left RVL")
    print("  - Flickzy left Aight")
    print("")
    
    print("v1.1.0 – Mods Update (January 9, 2026)")
    print("──────────────────────────────────────")
    print("• Complete mod system with toggle menu & descriptions")
    print("• New mods added:")
    print("  - Technical Issues (crashes/no-loads)")
    print("  - Ping Difference (realistic ping swings)")
    print("  - Stream Snipe (high-profile eliminations)")
    print("  - Zero Build Flashback (chaotic no-build moments)")
    print("• Fixed spawn-time crash/no-load placement bugs")
    print("• Eliminated ghost fights from dead players")
    print("• Improved MVP calculation (earnings prioritized)")
    print("• Better broadcast feel with new spawn summaries")
    print("")
    
    print("v1.0.0 – Initial Release (December 2025)")
    print("──────────────────────────────────────")
    print("• Full tournament simulation (FNCS, Cash Cup, LAN, Victory Cup)")
    print("• Career stats, season tracking & history")
    print("• Placement + elim points, prize pools, org tags")
    print("• Dynamic commentary, top 10 standings & movement arrows")
    print("• Configurable speed, templates & setup menu")
    print("")
    
    print("═" * 60)
    input("\nPress Enter to return to main menu...")
    

def pre_tournament_menu():
    while True:
        print("\n" + "━" * 45)
        print("🎮 TOURNAMENT CONFIG")
        print("━" * 45)
        print(f"1. PLAYERS:         [{CONFIG['players']}]")
        print(f"2. MATCHES:         [{CONFIG['matches']}]")
        print(f"3. STORM CIRCLES:   [{CONFIG['storm_circles']}]")
        print(f"4. ELIM POINTS:     [{CONFIG['elim_points']}]")

        t_type = CONFIG["tournament_type"]
        t_label = TOURNAMENT_TYPES[t_type]["label"]
        print(f"5. TOURNAMENT TYPE: [{t_label}]")

        print(f"6. SPEED:           [{CONFIG['speed']}]")
        ticker_status = "ON" if CONFIG.get("show_win_tickers", True) else "OFF"
        print(f"7. REGION:          [{CONFIG.get('region', 'EU')}]")
        print(f"8. WIN TICKERS:     [{ticker_status}]")
        print(f"9. WALKOUTS:        [{ 'ON' if CONFIG.get('walkouts', False) else 'OFF' }]")
        print(f"0. RESET TO DEFAULT")
        print("\nType a number to change it, or 'B' to return to main menu")
        print("━" * 45)

        choice = input("> ").strip().lower()

        if choice == "b":
            return
            
        elif choice == "0":
            confirm = input("Are you sure you want to reset all config to default? (y/n)").strip().lower()
            if confirm == "y":
                CONFIG.clear()
                CONFIG.update(DEFAULT_CONFIG.copy())
                save_config(CONFIG)
                print("✅ Config has been reset to default!")
                sim_sleep(1)
            else:
                print("Reset cancelled.")

        elif choice == "1":
            val = input("Enter number of players: ").strip()
            if val.isdigit():
                CONFIG["players"] = int(val)
                save_config(CONFIG)
                if CONFIG["players"] > 100:
                    print("⚠️  100+ players is not recommended (performance & pacing)")
                if CONFIG["players"] < 20:
                    print("⚠️  Very low player counts may feel unrealistic")

        elif choice == "2":
            val = input("Enter number of matches: ").strip()
            if val.isdigit():
                CONFIG["matches"] = int(val)
                save_config(CONFIG)
                if CONFIG["matches"] > 20:
                    print("⚠️  Long tournaments heavily favor consistency")
                if CONFIG["matches"] < 5:
                    print("⚠️  Short formats create extreme RNG")

        elif choice == "3":
            val = input("Enter storm circles: ").strip()
            if val.isdigit():
                CONFIG["storm_circles"] = int(val)
                save_config(CONFIG)
                if CONFIG["storm_circles"] < 5:
                    print("⚠️  Fewer circles = faster, bloodier games")
                if CONFIG["storm_circles"] > 12:
                    print("⚠️  Too many circles can stall the midgame")

        elif choice == "4":
            val = input("Enter elim points: ").strip()
            if val.isdigit():
                CONFIG["elim_points"] = int(val)
                save_config(CONFIG)
                if CONFIG["elim_points"] >= 5:
                    print("⚠️  High elim points strongly reward aggression")
                if CONFIG["elim_points"] == 0:
                    print("⚠️  No elim points = pure placement meta")

        elif choice == "5":
            cycle_tournament_type()
            t = CONFIG["tournament_type"]
            save_config(CONFIG)
            print(f"🏆 Tournament set to {TOURNAMENT_TYPES[t]['label']}")

        elif choice == "6":
            speeds = ["SLOW", "NORMAL", "FAST", "INSTANT"]
            current = speeds.index(CONFIG["speed"])
            CONFIG["speed"] = speeds[(current + 1) % len(speeds)]
            save_config(CONFIG)
            if CONFIG["speed"] == "FAST":
                print("⚠️  FAST mode reduces dramatic pauses")
            if CONFIG["speed"] == "INSTANT":
                print("⚠️  INSTANT mode removes all cinematic viewing")
                
        elif choice == "7":
            regions = list(PRO_PLAYER_POOLS.keys())
            region = CONFIG.get("region", "EU")
            current = regions.index(region)
            CONFIG["region"] = regions[(current + 1) % len(regions)]
            save_config(CONFIG)
            print(f"🌍 Region set to {CONFIG['region']}")
            print(f"⚠️ Please restart the simulator to apply changes properly!")

                
        elif choice == "8":
            CONFIG["show_win_tickers"] = not CONFIG.get("show_win_tickers", True)
            status = "ON" if CONFIG["show_win_tickers"] else "OFF"
            print(f"Win ticker now {status} (shows at halftime + before finals)")
            save_config(CONFIG)
            
        elif choice == "9":
            CONFIG["walkouts"] = not CONFIG.get("walkouts", False)
            status = "ON" if CONFIG["walkouts"] else "OFF"
            print(f"Player walkouts before tournaments are now {status}")
            save_config(CONFIG)
            
        else:
            print("Invalid option.")




if __name__ == "__main__":
    action = main_menu()

    if action == "START":
        players = simulate_tournament()
        leaderboard = sort_leaderboard(players)
        print_leaderboard(leaderboard)
        export_tournament_results(players, CONFIG["matches"])
        show_player_history(players)

