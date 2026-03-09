import json
import os
import math
import random
import time
import datetime
from dataclasses import dataclass, field
from typing import List
from utils import display_name, ORG_TAGS, Colors, sim_sleep, DEFAULT_CONFIG, CONFIG, BASE_DIR, DATA_DIR, save_config, \
    load_config, save_active_mods, load_active_mods
from rich.console import Console
from rich.table import Table
from mods import (
    TechnicalIssuesMod,
    RageQuitMod,
    ZeroBuildFlashbackMod,
    StreamSnipedMod,
    PingDiffMod,
    ClutchFactorMod,
)

console = Console(highlight=False)

ACTIVE_MODS = [
    TechnicalIssuesMod(crash_chance=0.008, no_load_chance=0.012),
    RageQuitMod(),
    ZeroBuildFlashbackMod(),
    StreamSnipedMod(),
    ClutchFactorMod(),
]

ACTIVE_MODS = load_active_mods(ACTIVE_MODS)

TOURNAMENTS_ROOT = os.path.join(BASE_DIR, "tournaments")

REGION = CONFIG.get("region", "EU").lower()
REGION_DATA_DIR = os.path.join(DATA_DIR, REGION)
os.makedirs(REGION_DATA_DIR, exist_ok=True)
CAREER_FILE = os.path.join(REGION_DATA_DIR, "career_stats.json")
SEASON_FILE = os.path.join(REGION_DATA_DIR, "season_data.json")
SOCIAL_FILE = os.path.join(REGION_DATA_DIR, "social_data.json")
SPLASH_FILE = "splash.txt"
SEASON = {
    "current_season": 1,
    "tournaments_played": 0,
    "tournaments_per_season": 16,
    "season_players": {},
    "history": [],
}

os.makedirs(DATA_DIR, exist_ok=True)

SAVES_DIR = os.path.join(BASE_DIR, "saves")
os.makedirs(SAVES_DIR, exist_ok=True)
CURRENT_SAVE_FILE = os.path.join(DATA_DIR, "current_save.txt")


def get_current_save():
    """Get the name of the currently loaded save"""
    if os.path.exists(CURRENT_SAVE_FILE):
        with open(CURRENT_SAVE_FILE, "r") as f:
            return f.read().strip()
    return "default"


def set_current_save(save_name):
    """Set the current save name"""
    with open(CURRENT_SAVE_FILE, "w") as f:
        f.write(save_name)


def get_save_path(save_name):
    """Get the directory path for a specific save"""
    return os.path.join(SAVES_DIR, save_name)


def list_saves():
    """List all available saves with their info"""
    saves = []
    if not os.path.exists(SAVES_DIR):
        return saves

    for save_name in os.listdir(SAVES_DIR):
        save_path = get_save_path(save_name)
        if os.path.isdir(save_path):
            info = {
                "name": save_name,
                "regions": {},
                "last_played": "Never"
            }

            for region in ["eu", "na", "br", "oce", "mixed"]:
                region_dir = os.path.join(save_path, region)
                career_file = os.path.join(region_dir, "career_stats.json")
                season_file = os.path.join(region_dir, "season_data.json")

                if os.path.exists(career_file) or os.path.exists(season_file):
                    region_info = {
                        "tournaments": 0,
                        "season": 1,
                        "last_played": "Never"
                    }

                    if os.path.exists(career_file):
                        try:
                            with open(career_file, "r") as f:
                                career_data = json.load(f)
                                if career_data:
                                    first_player = list(career_data.values())[0]
                                    region_info["tournaments"] = first_player.get("tournaments", 0)
                        except:
                            pass

                    if os.path.exists(season_file):
                        try:
                            with open(season_file, "r") as f:
                                season_data = json.load(f)
                                region_info["season"] = season_data.get("current_season", 1)

                            mtime = os.path.getmtime(season_file)
                            region_info["last_played"] = datetime.datetime.fromtimestamp(mtime).strftime(
                                "%Y-%m-%d %H:%M")
                        except:
                            pass

                    info["regions"][region.upper()] = region_info

            if info["regions"]:
                most_recent = max(
                    info["regions"].values(),
                    key=lambda x: x["last_played"]
                )
                info["last_played"] = most_recent["last_played"]

            saves.append(info)

    return sorted(saves, key=lambda x: x["last_played"], reverse=True)


def create_save(save_name):
    """Create a new save file"""
    save_path = get_save_path(save_name)
    if os.path.exists(save_path):
        return False, "Save already exists"

    os.makedirs(save_path, exist_ok=True)
    return True, "Save created successfully"


def load_save(save_name):
    """Load a save by copying its data to the active data directory"""
    global REGION, REGION_DATA_DIR, CAREER_FILE, SEASON_FILE, SEASON

    save_path = get_save_path(save_name)
    if not os.path.exists(save_path):
        return False, "Save does not exist"

    current_save = get_current_save()
    if current_save != save_name:
        save_current_to_file(current_save)

    import shutil
    if os.path.exists(DATA_DIR):
        backup_dir = DATA_DIR + "_backup_temp"
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.copytree(DATA_DIR, backup_dir)
        shutil.rmtree(DATA_DIR)

    shutil.copytree(save_path, DATA_DIR)

    set_current_save(save_name)

    REGION = CONFIG.get("region", "EU").lower()
    REGION_DATA_DIR = os.path.join(DATA_DIR, REGION)
    CAREER_FILE = os.path.join(REGION_DATA_DIR, "career_stats.json")
    SEASON_FILE = os.path.join(REGION_DATA_DIR, "season_data.json")

    load_season()

    return True, f"Loaded save: {save_name}"


def save_current_to_file(save_name):
    """Save current data directory to a save file"""
    import shutil
    save_path = get_save_path(save_name)

    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    for item in os.listdir(DATA_DIR):
        if item == "current_save.txt":
            continue
        src = os.path.join(DATA_DIR, item)
        dst = os.path.join(save_path, item)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)


def delete_save(save_name):
    """Delete a save file"""
    if save_name == get_current_save():
        return False, "Cannot delete currently loaded save"

    save_path = get_save_path(save_name)
    if not os.path.exists(save_path):
        return False, "Save does not exist"

    import shutil
    shutil.rmtree(save_path)
    return True, f"Deleted save: {save_name}"


def rename_save(old_name, new_name):
    """Rename a save file"""
    old_path = get_save_path(old_name)
    new_path = get_save_path(new_name)

    if not os.path.exists(old_path):
        return False, "Save does not exist"

    if os.path.exists(new_path):
        return False, "A save with that name already exists"

    os.rename(old_path, new_path)

    if get_current_save() == old_name:
        set_current_save(new_name)

    return True, f"Renamed save to: {new_name}"


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
        ("Swizzy", 110, "Fragger", "Vitality"),
        ("Merstach", 109, "Fragger", "Gentle Mates"),
        ("Vico", 108, "Fragger", "BIG"),
        ("Wox", 107, "Strategist", "HavoK"),
        ("Pixie", 106, "Fragger", "HavoK"),
        ("MariusCOW", 105, "Aggressive", "Gentle Mates"),
        ("Tjino", 108, "Aggressive", "HavoK"),
        ("PabloWingu", 108, "Aggressive", "HavoK"),
        ("Chap", 108, "Fragger", "Free Agent"),
        ("Shxrk", 107, "Fragger", "BIG"),
        ("Scroll", 106, "Strategist", "Atlantic"),
        ("Th0masHD", 104, "Strategist", "Virtus Pro"),
        ("Kami", 109, "Rat", "Free Agent"),
        ("Chico", 101, "Strategist", "Free Agent"),
        ("Charyy", 104, "Passive", "Free Agent"),
        ("Japko", 105, "Fragger", "Free Agent"),
        ("Queasy", 102, "Rat", "Vitality"),
        ("Flickzy", 105, "Aggressive", "Free Agent"),
        ("P1ngfnz", 100, "Fragger", "Free Agent"),
        ("Malibuca", 106, "Strategist", "BIG"),
        ("Vanyak3k", 105, "Passive", "Gentle Mates"),
        ("Fredoxie", 103, "Strategist", "Free Agent"),
        ("MrSavage", 101, "Aggressive", "XSET"),
        ("Sky", 105, "Strategist", "Atlantic"),
        ("t3eny", 106, "Aggressive", "Free Agent"),
        ("Trulex", 98, "Strategist", "Free Agent"),
        ("Tayson", 100, "Strategist", "Free Agent"),
        ("IDrop", 104, "Fragger", "HavoK"),
        ("Rezon", 95, "Fragger", "WAVE"),
        ("Setty", 102, "Passive", "Free Agent"),
        ("Panzer", 98, "Strategist", "Free Agent"),
        ("Nebs", 90, "Strategist", "Free Agent"),
        ("Vadeal", 87, "Passive", "WAVE"),
        ("Focus", 100, "Fragger", "Virtus Pro"),
        ("Akiira", 97, "Fragger", "Gentle Mates"),
        ("Rax", 99, "Fragger", "Free Agent"),
        ("Kurama", 99, "Fragger", "Solary"),
        ("Werex", 98, "Strategist", "Lyost"),
        ("Seyyto", 94, "Strategist", "Free Agent"),
        ("Kiro", 86, "Strategist", "Free Agent"),
        ("Podasai", 85, "Strategist", "Free Agent"),
        ("Momsy", 89, "Strategist", "Lyost"),
        ("Pixx", 90, "Passive", "HavoK"),
        ("Demus", 92, "Fragger", "T1"),
        ("Darm", 90, "Fragger", "T1"),
        ("Sangild", 85, "Strategist", "Free Agent"),
        ("Huty", 84, "Strategist", "The One"),
        ("F1shyX", 83, "Strategist", "Free Agent"),
        ("Mappi", 83, "Strategist", "Free Agent"),
        ("Moneymaker", 82, "Fragger", "XP42"),
        ("Mongraal", 81, "Aggressive", "Free Agent"),
        ("Wheat", 80, "Strategist", "FLC"),
        ("NeFrizi", 79, "Strategist", "Detect"),
        ("Twi", 78, "Aggressive", "Free Agent"),
        ("SkyJump", 77, "Fragger", "Solary"),
        ("Mikson", 76, "Fragger", "Free Agent"),
        ("Upl", 80, "Fragger", "Free Agent"),
        ("Kombek", 79, "Fragger", "GameWard"),
        ("Blacha", 78, "Passive", "Free Agent"),
        ("Hris", 77, "Fragger", "Free Agent"),
        ("Ankido", 71, "Strategist", "BIG"),
        ("Cringe", 70, "Strategist", "XP42"),
        ("Volko", 69, "Strategist", "BIG"),
        ("JannisZ", 78, "Passive", "CGN"),
        ("Pinq", 75, "Passive", "Free Agent"),
        ("Dela", 83, "Aggressive", "Free Agent"),
        ("Bevvys", 83, "Aggressive", "Free Agent"),
        ("Eclipse", 78, "Aggressive", "Free Agent"),
        ("Hellfire", 83, "Strategist", "Free Agent"),
        ("Andilex", 86, "Fragger", "MGA"),
        ("Kiduoo", 71, "Passive", "Free Agent"),
        ("Robin", 70, "Strategist", "FOKUS"),
        ("Kyto", 70, "Fragger", "Free Agent"),
        ("Hijoe", 70, "Strategist", "Aight"),
        ("Dandepuzo", 73, "Fragger", "TKRF"),
        ("iFr0zi", 70, "Rat", "MGA"),
        ("Skvii", 85, "Strategist", "Free Agent"),
        ("Fastroki", 70, "Strategist", "FOKUS"),
        ("1Lusha", 76, "Aggressive", "Lyost"),
        ("S1neD", 78, "Strategist", "NTO Corp"),
        ("F1n4ik", 75, "Fragger", "FLC"),
        ("Howly", 75, "Fragger", "Free Agent"),
        ("G13ras", 70, "Strategist", "Detect"),
        ("CZB", 79, "Aggressive", "Free Agent"),
        ("Axeforce", 78, "Aggressive", "Free Agent"),
        ("Fnajen", 79, "Fragger", "Orphee"),
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
        ("Cheatiin", 93, "Fragger", "Aight"),
        ("Trexer", 90, "Fragger", "Aight"),
        ("Ghost", 85, "Strategist", "Free Agent"),
        ("Kaan", 85, "Aggressive", "Free Agent"),
        ("Faded", 85, "Strategist", "Free Agent"),
        ("SShur4", 79, "Strategist", "Free Agent"),
        ("Repairs", 79, "Strategist", "Free Agent"),
        ("Prax", 87, "Aggressive", "PTH"),
        ("Hyper", 80, "Fragger", "OneProdige"),
        ("Julle", 81, "Strategist", "Free Agent"),
        ("Minori", 82, "Strategist", "Solary"),
        ("Darkos", 81, "Strategist", "Solary"),
    ],

    "NA": [
        ('Peterbot', 113, 'Fragger', 'Falcons'),
        ('Cold', 109, 'Aggressive', 'Twisted Minds'),
        ('Ajerss', 108, 'Fragger', 'Gen.G'),
        ('Pollo', 108, 'Fragger', 'Falcons'),
        ('Higgs', 107, 'Aggressive', 'XSET'),
        ('Eomzo', 107, 'Strategist', 'Elite'),
        ('Muz', 106, 'Fragger', 'XSET'),
        ('Rapid', 106, 'Strategist', 'Twisted Minds'),
        ('Ritualx', 105, 'Fragger', 'Gen.G'),
        ('Boltz', 105, 'Aggressive', 'Twisted Minds'),
        ('Clix', 104, 'Fragger', 'XSET'),
        ('Sphinx', 104, 'Passive', 'Free Agent'),
        ('Acorn', 103, 'Rat', 'Twisted Minds'),
        ('Khanada', 103, 'Fragger', 'Dignitas'),
        ('Cooper', 102, 'Fragger', 'Dignitas'),
        ("Veno", 102, "Fragger", "XSET"),
        ('Threats', 102, 'Aggressive', 'Free Agent'),
        ('Ark', 102, 'Fragger', 'Dignitas'),
        ('Rise', 101, 'Rat', 'Free Agent'),
        ('Bugha', 101, 'Strategist', 'Free Agent'),
        ('Josh', 101, 'Fragger', 'Free Agent'),
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
        ('Vergo', 73, 'Strategist', 'Void'),
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
        ('Krreon', 67, 'Strategist', 'M77'),
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
        ('Noizy', 62, 'Rat', 'Monarcos'),
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
        ('Freeze', 59, 'Passive', 'One True Army'),
        ('Phenom', 58, 'Fragger', 'Free Agent'),
        ('Nekko', 58, 'Rat', 'Quantum'),
        ('NoahWPlays', 58, 'Strategist', 'Free Agent'),
        ('Sandman', 57, 'Passive', 'Free Agent'),
        ('Nurface', 57, 'Aggressive', 'Free Agent'),
        ('Circ', 56, 'Strategist', 'Free Agent'),
    ],
    "MIXED": [
        ("Peterbot", 113, "Fragger", "Falcons"),
        ("Swizzy", 110, "Fragger", "Vitality"),
        ("Cold", 109, "Aggressive", "Twisted Minds"),
        ("Kami", 109, "Rat", "Free Agent"),
        ("Merstach", 109, "Fragger", "Gentle Mates"),
        ("Ajerss", 108, "Fragger", "Gen.G"),
        ("Chap", 108, "Fragger", "Free Agent"),
        ("PabloWingu", 108, "Aggressive", "HavoK"),
        ("Pollo", 108, "Fragger", "Falcons"),
        ("Tjino", 108, "Aggressive", "HavoK"),
        ("Vico", 108, "Fragger", "BIG"),
        ("Eomzo", 107, "Strategist", "Elite"),
        ("Higgs", 107, "Aggressive", "XSET"),
        ("Shxrk", 107, "Fragger", "BIG"),
        ("Wox", 107, "Strategist", "HavoK"),
        ("Muz", 106, "Fragger", "XSET"),
        ("Pixie", 106, "Fragger", "HavoK"),
        ("Rapid", 106, "Strategist", "Twisted Minds"),
        ("t3eny", 106, "Aggressive", "Free Agent"),
        ("Boltz", 105, "Aggressive", "Twisted Minds"),
        ("Flickzy", 105, "Aggressive", "Free Agent"),
        ("Malibuca", 106, "Strategist", "BIG"),
        ("MariusCOW", 105, "Aggressive", "Gentle Mates"),
        ("Ritualx", 105, "Fragger", "Gen.G"),
        ("Vanyak3k", 105, "Passive", "Gentle Mates"),
        ("Charyy", 104, "Passive", "Free Agent"),
        ("Clix", 104, "Fragger", "XSET"),
        ("IDrop", 104, "Fragger", "HavoK"),
        ("Japko", 104, "Fragger", "Free Agent"),
        ("Scroll", 106, "Strategist", "Atlantic"),
        ("Sphinx", 104, "Passive", "Free Agent"),
        ("Acorn", 103, "Rat", "Twisted Minds"),
        ("Fredoxie", 103, "Strategist", "Free Agent"),
        ("Khanada", 103, "Fragger", "Dignitas"),
        ("Queasy", 102, "Rat", "Vitality"),
        ("Th0masHD", 103, "Strategist", "Virtus Pro"),
        ("Ark", 102, "Fragger", "Dignitas"),
        ("Cooper", 102, "Fragger", "Dignitas"),
        ("Setty", 102, "Passive", "Free Agent"),
        ("Threats", 102, "Aggressive", "Free Agent"),
        ("Veno", 102, "Fragger", "XSET"),
        ("Bugha", 101, "Strategist", "Free Agent"),
        ("Chico", 101, "Strategist", "Free Agent"),
        ("MrSavage", 101, "Aggressive", "XSET"),
        ("Rise", 101, "Rat", "Free Agent"),
        ("Avivv", 100, "Fragger", "2AM"),
        ("P1ngfnz", 100, "Fragger", "Free Agent"),
        ("Reet", 100, "Strategist", "Free Agent"),
        ("Shadow", 100, "Fragger", "Free Agent"),
        ("Sky", 105, "Strategist", "Atlantic"),
        ("Tayson", 100, "Strategist", "Free Agent"),
        ("GMoney", 99, "Fragger", "2AM"),
        ("Kurama", 99, "Fragger", "Solary"),
        ("Skqttles", 99, "Passive", "Free Agent"),
        ("VerT", 99, "Strategist", "Void"),
        ("Panzer", 98, "Strategist", "Free Agent"),
        ("Trulex", 98, "Strategist", "Free Agent"),
        ("Werex", 98, "Strategist", "Lyost"),
        ("Akiira", 97, "Fragger", "Gentle Mates"),
        ("Rax", 96, "Fragger", "Free Agent"),
        ("EpikWhale", 95, "Strategist", "Free Agent"),
        ("Mero", 95, "Fragger", "Xen"),
        ("Rezon", 95, "Fragger", "WAVE"),
        ("Seyyto", 94, "Strategist", "Free Agent"),
        ("Bucke", 93, "Strategist", "Dignitas"),
        ("Demus", 92, "Fragger", "T1"),
        ("Darm", 90, "Fragger", "T1"),
        ("Pixx", 90, "Passive", "HavoK"),
        ("Momsy", 89, "Strategist", "Lyost"),
        ("PXMP", 88, "Aggressive", "Elite"),
        ("Aminished", 87, "Strategist", "Past Bliss"),
        ("Noxy", 87, "Passive", "Free Agent"),
        ("Vadeal", 87, "Passive", "WAVE"),
        ("Andilex", 86, "Fragger", "MGA"),
        ("Focus", 100, "Fragger", "Virtus Pro"),
        ("Kiro", 86, "Strategist", "Free Agent"),
        ("Braydz", 85, "Fragger", "Free Agent"),
        ("Podasai", 85, "Strategist", "Free Agent"),
        ("Sangild", 85, "Strategist", "Free Agent"),
        ("Skvii", 85, "Strategist", "Free Agent"),
        ("Artskill", 84, "Aggressive", "Free Agent"),
        ("Huty", 84, "Strategist", "The One"),
        ("Chimp", 76, "Fragger", "Team Pulsar"),
        ("Channce", 76, "Fragger", "Team Pulsar"),
        ("Brycx", 75, "Strategist", "Free Agent"),
        ("Curve", 74, "Aggressive", "Free Agent"),
        ("Deyy", 74, "Aggressive", "Free Agent"),
        ("oSydd", 74, "Fragger", "Free Agent"),
        ("Vergo", 73, "Strategist", "Void"),
        ("Visxals", 73, "Strategist", "Free Agent"),
        ("Parz", 72, "Passive", "Free Agent"),
        ("Seek", 72, "Aggressive", "Free Agent"),
        ("Bacca", 71, "Fragger", "Free Agent"),
        ("Curly", 71, "Strategist", "Free Agent"),
        ("Dash", 70, "Fragger", "REIGN"),
        ("Mason", 70, "Strategist", "Void"),
        ("Nvtylerh", 70, "Aggressive", "Free Agent"),
        ("Kraez", 69, "Aggressive", "Cynapse"),
        ("Paper", 69, "Passive", "Free Agent"),
        ("VicterV", 69, "Fragger", "Free Agent"),
    ],
}


def get_pro_players_from_config():
    region = CONFIG.get("region", "EU")
    pool = PRO_PLAYER_POOLS.get(region)

    if not pool:
        raise ValueError(f"No player pool found for region '{region}'")

    return pool


ARCHETYPES = ["Fragger", "Passive", "Strategist", "Aggressive", "Rat"]

ARCHETYPE_SWITCH_MAP = {
    "Aggressive": "Strategist",
    "Fragger": "Passive",
    "Passive": "Aggressive",
    "Strategist": "Fragger",
    "Rat": "Aggressive",
}

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

    "ELITE_SERIES": {
        "label": "ELITE SERIES",
        "prize_pool": [
            (1, 1, 40_000),
            (2, 2, 30_000),
            (3, 3, 22_500),
            (4, 4, 16_000),
            (5, 5, 13_000),
            (6, 6, 10_500),
            (7, 7, 8_000),
            (8, 8, 6_500),
            (9, 9, 5_000),
            (10, 10, 4_000),
            (11, 25, 2_000),
            (26, 50, 1_000),
            (51, 75, 500),
            (76, 90, 250),
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
            (76, 90, 5_000),
            (91, 100, 2_500)
        ],
    },

    "VICTORY_CUP": {
        "label": "VICTORY CUP",
        "points_per_win": 100,
        "money_per_point": 4
    },

    "RELOAD": {
        "label": "RELOAD",
        "prize_pool": [
            (1, 1, 50_000),
            (2, 2, 35_000),
            (3, 3, 25_000),
            (4, 4, 18_000),
            (5, 5, 14_000),
            (6, 10, 10_000),
            (11, 20, 5_000),
            (21, 30, 2_500),
            (31, 40, 1_000),
        ],
        "reboot_on_kill": True,
        "starting_reboots": 0,
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
    "ELITE_SERIES": {
        "label": "ELITE SERIES",
        "players": 100,
        "matches": 8,
        "storm_circles": 12,
        "elim_points": 3,
        "tournament_type": "ELITE_SERIES",
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
    },
    "RELOAD": {
        "label": "RELOAD",
        "players": 40,
        "matches": 8,
        "storm_circles": 8,
        "elim_points": 2,
        "tournament_type": "RELOAD",
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
    career_elite_series_wins: int = 0
    career_reload_wins: int = 0
    career_fncs_wins: int = 0
    career_lan_wins: int = 0
    career_victorycup_wins: int = 0
    best_finish: int = 999
    career_achievements: list = field(default_factory=list)

    current_rank: int = 0
    points_to_first: int = 0
    points_to_above: int = 0
    points_to_below: int = 0
    safety_margin: int = 0

    risk_tolerance: float = 0.5
    grief_bias: float = 0.0

    rivals: dict = field(default_factory=dict)
    fear: dict = field(default_factory=dict)
    friends: set = field(default_factory=set)

    _has_rage_quit: bool = field(default=False)

    original_archetype: str = ""
    current_archetype: str = ""
    has_switched_archetype: bool = False

    loot: float = 0.0
    contested_drop: bool = False
    time_since_fight: int = 0

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

        decay_rate = 0.9
        if p.skill >= 100:
            decay_rate = 0.92

        p.confidence *= decay_rate

        if percentile < 0.05:
            p.confidence += 0.055
        elif percentile < 0.15:
            p.confidence += 0.03
        elif percentile < 0.30:
            p.confidence += 0.015

        elif percentile > 0.95:
            penalty = 0.05
            if p.skill >= 100:
                penalty = 0.035
            p.confidence -= penalty
        elif percentile > 0.85:
            penalty = 0.035
            if p.skill >= 100:
                penalty = 0.025
            p.confidence -= penalty
        elif percentile > 0.70:
            penalty = 0.02
            if p.skill >= 100:
                penalty = 0.015
            p.confidence -= penalty

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
    create_backup(SEASON_FILE, "season_data")


def load_social_data():
    """Load friendships and rivalries from social_data.json"""
    if os.path.exists(SOCIAL_FILE):
        with open(SOCIAL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"friendships": {}, "rivalries": {}}


def save_social_data(social_data):
    """Save friendships and rivalries to social_data.json"""
    with open(SOCIAL_FILE, "w", encoding="utf-8") as f:
        json.dump(social_data, f, indent=2)
    create_backup(SOCIAL_FILE, "social_data")


def create_backup(source_file, backup_prefix, max_backups=20):
    """Create a timestamped backup and manage old backups"""
    if not os.path.exists(source_file):
        return

    backup_dir = os.path.join(REGION_DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_filename = f"{backup_prefix}_backup_{timestamp}.json"
    backup_path = os.path.join(backup_dir, backup_filename)

    try:
        with open(source_file, "r", encoding="utf-8") as src:
            data = json.load(src)
        with open(backup_path, "w", encoding="utf-8") as dst:
            json.dump(data, dst, indent=2)
    except Exception as e:
        print(f"⚠️  Backup failed: {e}")
        return

    try:
        all_backups = sorted([
            f for f in os.listdir(backup_dir)
            if f.startswith(backup_prefix) and f.endswith(".json")
        ])

        if len(all_backups) > max_backups:
            for old_backup in all_backups[:-max_backups]:
                os.remove(os.path.join(backup_dir, old_backup))
    except Exception:
        pass


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
            p.career_elite_series_wins = stats.get("elite_series_wins", 0)
            p.career_reload_wins = stats.get("reload_wins", 0)
            p.career_fncs_wins = stats.get("fncs_wins", 0)
            p.career_lan_wins = stats.get("lan_wins", 0)
            p.career_victorycup_wins = stats.get("victorycup_wins", 0)
            p.best_finish = stats.get("best_finish", 999)
            p.career_achievements = stats.get("achievements", [])


def update_social_data(players: List[Player]):
    """Update friendships and rivalries based on tournament outcomes"""
    social_data = load_social_data()

    if "friendships" not in social_data:
        social_data["friendships"] = {}
    if "rivalries" not in social_data:
        social_data["rivalries"] = {}

    id_to_player = {p.id: p for p in players}

    for p in players:
        p_key = p.name

        if p_key not in social_data["friendships"]:
            social_data["friendships"][p_key] = {}
        if p_key not in social_data["rivalries"]:
            social_data["rivalries"][p_key] = {}

        for friend_id in p.friends:
            friend = id_to_player.get(friend_id)
            if not friend:
                continue

            friend_key = friend.name
            current_strength = social_data["friendships"][p_key].get(friend_key, 1.0)

            killed_friend = p.rivals.get(friend_id, 0) > 0

            placement_diff = abs(p.final_placement - friend.final_placement) if hasattr(p,
                                                                                        'final_placement') and hasattr(
                friend, 'final_placement') else 0
            both_good = (hasattr(p, 'final_placement') and hasattr(friend, 'final_placement') and
                         p.final_placement <= 10 and friend.final_placement <= 10)
            both_bad = (hasattr(p, 'final_placement') and hasattr(friend, 'final_placement') and
                        p.final_placement > 50 and friend.final_placement > 50)

            if killed_friend:
                current_strength -= 0.15
            elif both_good:
                current_strength += 0.08
            elif both_bad:
                current_strength += 0.05
            elif placement_diff > 40:
                current_strength -= 0.05
            else:
                current_strength += 0.02

            current_strength = max(0.0, min(2.0, current_strength))

            if current_strength < 0.3:
                if friend_key in social_data["friendships"][p_key]:
                    del social_data["friendships"][p_key][friend_key]
            else:
                social_data["friendships"][p_key][friend_key] = round(current_strength, 2)

        for rival_id, hatred in p.rivals.items():
            rival = id_to_player.get(rival_id)
            if not rival:
                continue

            rival_key = rival.name
            current_rivalry = social_data["rivalries"][p_key].get(rival_key, 0.0)

            decay_rate = 0.75
            decayed_rivalry = current_rivalry * decay_rate

            new_rivalry = decayed_rivalry + (hatred * 0.5)
            new_rivalry = min(20.0, new_rivalry)

            if new_rivalry >= 1.0:
                social_data["rivalries"][p_key][rival_key] = round(new_rivalry, 2)
            elif rival_key in social_data["rivalries"][p_key]:
                del social_data["rivalries"][p_key][rival_key]

    save_social_data(social_data)


def save_career_data(players: List[Player]):
    existing_data = {}
    if os.path.exists(CAREER_FILE):
        try:
            with open(CAREER_FILE, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = {}

    for p in players:
        existing_data[p.name] = {
            "earnings": p.career_earnings,
            "kills": p.career_kills,
            "tournaments": p.career_tournaments,
            "wins": p.career_wins,
            "cashcup_wins": p.career_cashcup_wins,
            "elite_series_wins": p.career_elite_series_wins,
            "reload_wins": p.career_reload_wins,
            "fncs_wins": p.career_fncs_wins,
            "lan_wins": p.career_lan_wins,
            "victorycup_wins": p.career_victorycup_wins,
            "best_finish": p.best_finish,
            "achievements": getattr(p, "career_achievements", [])
        }

    with open(CAREER_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2)

    create_backup(CAREER_FILE, "career_stats")


def init_season_players(players):
    for p in players:
        if p.name not in SEASON["season_players"]:
            SEASON["season_players"][p.name] = {
                "points": 0,
                "wins": 0,
                "elims": 0,
                "earnings": 0
            }


def placement_points(placement: int, tournament_type: str = None) -> int:
    if tournament_type == "RELOAD":
        if placement > 30:
            return 0
        if 21 <= placement <= 30:
            return 31 - placement
        if 11 <= placement <= 20:
            return 31 - placement
        if 6 <= placement <= 10:
            return 32 - placement
        if placement == 5:
            return 30
        if placement == 4:
            return 35
        if placement == 3:
            return 40
        if placement == 2:
            return 50
        if placement == 1:
            return 60
        return 0

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
        "Fragger": 1.30,
        "Aggressive": 1.45,
        "Strategist": 0.90,
        "Passive": 0.80,
        "Rat": 0.50,
    }

    return base * multipliers.get(player.current_archetype, 1.0)


def get_survival_weight(player):
    multipliers = {
        "Fragger": 0.85,
        "Aggressive": 0.75,
        "Strategist": 1.25,
        "Passive": 1.40,
        "Rat": 1.70,
    }
    return 1.0 * multipliers.get(player.current_archetype, 1.0)


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

    projections.sort(key=lambda x: x[0], reverse=True)

    for i, (proj_pts, curr_pts, wins, p) in enumerate(projections[:6]):
        chance = (math.exp(proj_pts / scale) / total_exp) * 100
        chance = max(0.5, min(99.5, chance))

        bar_len = int(chance / 12.5)
        bar = "█" * bar_len + "░" * (8 - bar_len)

        print(f"{i + 1:>2}. {display_name(p):<15} {chance:>5.1f}% [{bar}] ({curr_pts} pts)")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sim_sleep(1.5)


LEGEND_COMMENTARY = [
    "This is why their name is etched into history.",
    "Years of dominance showing up right on cue.",
    "That’s not luck — that’s legacy.",
    "They’ve done this before. Many times.",
    "Moments like this are routine for legends.",
    "This is muscle memory at championship level.",
    "The lobby knows exactly who just won.",
    "Another chapter in an already stacked career.",
]

GOAT_COMMENTARY = [
    "Different tier. Different rules.",
    "This lobby is just another page in the history book.",
    "They make greatness look casual.",
    "The GOAT does GOAT things.",
    "This isn’t a tournament — it’s a reminder.",
    "Generational talent on full display.",
    "The skill gap just introduced itself.",
    "They’re not chasing history. They *are* history.",
]


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
                f"First blood? Nah, first ROYALE. {name} is cooking!",
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

    tier = get_career_tier(winner)

    if tier in ("Legend", "GOAT"):
        legacy_roll = random.random()

        chance = 0.35 if tier == "GOAT" else 0.22

        if legacy_roll < chance:
            legacy_lines = GOAT_COMMENTARY if tier == "GOAT" else LEGEND_COMMENTARY

            if random.random() < 0.5:
                return random.choice(legacy_lines)
            else:
                return f"{random.choice(commentary)} {random.choice(legacy_lines)}"

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
    total_games = CONFIG["matches"]
    games_remaining = total_games - match_number
    is_crunch_time = (games_remaining <= 2)

    risk = 0.4

    if is_crunch_time and player.current_rank <= 10:
        gap_to_first = player.points_to_first
        gap_to_below = player.points_to_below
        gap_from_above = player.points_to_above

        intensity_multiplier = 1.0 if games_remaining == 0 else 0.7

        if player.current_rank == 1:
            if gap_to_below >= 40:
                risk = 0.25
                player.grief_bias = 0.1 * intensity_multiplier
            elif gap_to_below >= 20:
                risk = 0.35
                player.grief_bias = 0.2 * intensity_multiplier
            else:
                risk = 0.5
                player.grief_bias = 0.4 * intensity_multiplier

        elif player.current_rank == 2:
            if gap_to_first >= 100:
                risk = 1.0
                player.grief_bias = 1.2 * intensity_multiplier
            elif gap_to_first >= 70:
                if gap_to_below >= 50:
                    risk = 0.95
                    player.grief_bias = 1.3 * intensity_multiplier
                elif gap_to_below >= 20:
                    risk = 0.8
                    player.grief_bias = 0.8 * intensity_multiplier
                else:
                    risk = 0.65
                    player.grief_bias = 0.5 * intensity_multiplier
            elif gap_to_first >= 40:
                if gap_to_below >= 30:
                    risk = 0.85
                    player.grief_bias = 0.9 * intensity_multiplier
                else:
                    risk = 0.7
                    player.grief_bias = 0.6 * intensity_multiplier
            else:
                risk = 0.75
                player.grief_bias = 0.7 * intensity_multiplier

        elif 3 <= player.current_rank <= 5:
            if gap_to_first >= 60:
                risk = 0.9
                player.grief_bias = 0.8 * intensity_multiplier
            elif gap_to_first >= 30:
                risk = 0.75
                player.grief_bias = 0.6 * intensity_multiplier
            else:
                risk = 0.65
                player.grief_bias = 0.5 * intensity_multiplier

        elif 6 <= player.current_rank <= 10:
            prize_cutoff_distance = abs(player.current_rank - 10)
            if prize_cutoff_distance <= 2:
                if gap_to_below <= 15:
                    risk = 0.5
                    player.grief_bias = 0.3 * intensity_multiplier
                else:
                    risk = 0.65
                    player.grief_bias = 0.4 * intensity_multiplier
            else:
                risk = 0.7
                player.grief_bias = 0.5 * intensity_multiplier

    elif is_crunch_time and 11 <= player.current_rank <= 30:
        intensity_multiplier = 1.0 if games_remaining == 0 else 0.7
        gap_to_prize = player.current_rank - 10
        if gap_to_prize <= 5 and player.points_to_above <= 25:
            risk = 0.85
            player.grief_bias = 0.6 * intensity_multiplier
        elif gap_to_prize <= 10 and player.points_to_above <= 40:
            risk = 0.75
            player.grief_bias = 0.5 * intensity_multiplier
        else:
            risk = 0.6
            player.grief_bias = 0.3 * intensity_multiplier

    else:
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


def choose_target(attacker, players, match_number=1, config=None):
    targets = [p for p in players if p != attacker]

    max_rivalry = 0
    most_hated = None
    for t in targets:
        hatred = attacker.rivals.get(t.id, 0)
        if hatred > max_rivalry:
            max_rivalry = hatred
            most_hated = t

    if max_rivalry >= 5:
        toxic_threshold = 0.15 + (max_rivalry - 5) * 0.08
        if random.random() < min(0.65, toxic_threshold):
            return most_hated

    weights = []
    is_crunch_time = match_number >= (config.get("matches", 12) - 2) if config else False
    social_data = load_social_data()

    for t in targets:
        w = t.skill

        is_friend = t.id in attacker.friends
        friendship_strength = 1.0

        if is_friend:
            friendship_strength = social_data.get("friendships", {}).get(attacker.name, {}).get(t.name, 1.0)

        if is_friend and not is_crunch_time:
            if friendship_strength >= 1.5:
                w *= 0.25
            elif friendship_strength >= 1.0:
                w *= 0.4
            else:
                w *= 0.6
        elif is_friend and is_crunch_time and attacker.grief_bias < 0.8:
            if friendship_strength >= 1.5:
                w *= 0.5
            else:
                w *= 0.7

        if attacker.grief_bias > 0.8 and t.current_rank == 1:
            w *= (1 + attacker.grief_bias * 3.0)
        elif attacker.grief_bias > 0 and t.current_rank < attacker.current_rank:
            w *= (1 + attacker.grief_bias)

        hatred = attacker.rivals.get(t.id, 0)
        w *= (1 + hatred * 0.25)

        fear = attacker.fear.get(t.id, 0)
        w *= max(0.4, 1 - fear * 0.15)

        if t.current_rank > 50:
            w *= 0.7

        weights.append(max(w, 1))

    return random.choices(targets, weights=weights, k=1)[0]


def register_elim(killer: Player, victim: Player, match_number: int = 1):
    base_rivalry = random.uniform(0.8, 1.3)

    are_friends = victim.id in killer.friends
    friendship_strength = 1.0

    if are_friends:
        social_data = load_social_data()
        friendship_strength = social_data.get("friendships", {}).get(killer.name, {}).get(victim.name, 1.0)

    did_emote = random.random() < 0.12
    if did_emote:
        base_rivalry += random.uniform(2.0, 3.5)
        if random.random() < 0.1:
            emote_messages = [
                f"{Colors.ITALIC}💀 {display_name(killer)} hits the emote on {display_name(victim)}!{Colors.RESET}",
                f"{Colors.ITALIC}🕺 {display_name(killer)} is dancing... {display_name(victim)} won't forget that.{Colors.RESET}",
                f"{Colors.ITALIC}😤 {display_name(killer)} with the disrespectful emote on {display_name(victim)}!{Colors.RESET}",
            ]
            print(random.choice(emote_messages))

    skill_gap = victim.skill - killer.skill
    if skill_gap >= 15:
        base_rivalry += random.uniform(1.5, 2.5)
    elif skill_gap >= 10:
        base_rivalry += random.uniform(0.8, 1.5)

    if victim.current_rank <= 3:
        base_rivalry += random.uniform(1.2, 2.0)
    elif victim.current_rank <= 10:
        base_rivalry += random.uniform(0.6, 1.2)
    elif victim.current_rank <= 20 and victim.points_to_above <= 30:
        base_rivalry += random.uniform(0.5, 1.0)

    is_crunch_time = match_number >= 10
    if is_crunch_time:
        base_rivalry *= 1.3

    if are_friends:
        if friendship_strength >= 1.5:
            base_rivalry *= 0.25
        elif friendship_strength >= 1.0:
            base_rivalry *= 0.35
        else:
            base_rivalry *= 0.5

    killer.rivals[victim.id] = killer.rivals.get(victim.id, 0) + base_rivalry
    victim.fear[killer.id] = victim.fear.get(killer.id, 0) + 1


def is_underperforming(player: Player, match_number: int):
    if match_number < 3:
        return False

    avg_place = player.average_placement
    expected = 50 - (player.skill - 80)

    return (
            avg_place > expected + 12
            and player.total_elims < match_number * 1.2
    )


def maybe_switch_archetype(player: Player, match_number: int):
    if not CONFIG.get("archetype_switching", True):
        return

    if player.has_switched_archetype:
        return

    if not is_underperforming(player, match_number):
        return

    games_over = match_number - 3

    base_chance = 0.12
    ramp_per_game = 0.06
    max_chance = 0.45

    switch_chance = min(
        max_chance,
        base_chance + games_over * ramp_per_game
    )

    if random.random() > switch_chance:
        return

    new_type = ARCHETYPE_SWITCH_MAP.get(player.current_archetype)
    if not new_type:
        return

    player.current_archetype = new_type
    player.has_switched_archetype = True


def simulate_match(players: List[Player], match_number: int):
    update_tournament_context(players)

    for p in players:
        update_player_strategy(p, match_number)

    for mod in ACTIVE_MODS:
        if mod.enabled:
            mod.on_match_start(players, match_number, CONFIG)

    weather_reports = [
        "☀️ Clear skies. Perfect conditions for high-kill games.",
        "🌧️ Light rain reported. The Storm feels extra cold today...",
        "🌫️ Heavy fog. Expect close-quarters combat in the mid-game.",
        "🌩️ Thunderstorms detected. The Storm is highly unstable!",
        "🌬️ High winds. Watch your rotations carefully.",
        "☄️ Strange atmospheric activity. Something is coming..."
    ]
    current_weather = random.choice(weather_reports)

    print("\n" + "━" * 50)
    print(f"🪂 GAME {match_number} / {CONFIG['matches']} — BATTLE BUS LAUNCHING")
    print("━" * 50)
    sim_sleep(1)
    print(current_weather)
    sim_sleep(1.5)

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
        print(f"...and {len(players) - 10} more players")
        sim_sleep(0.5)

    print("\n🪂 Players are now landing on the island…")
    sim_sleep(2)

    for p in players:
        p.loot = 0.0
        p.contested_drop = False
        p.time_since_fight = 0

    drop_counts = {}
    for p in players:
        if p.drop_poi not in drop_counts:
            drop_counts[p.drop_poi] = []
        drop_counts[p.drop_poi].append(p)

    for poi, droppers in drop_counts.items():
        if len(droppers) > 1:
            for p in droppers:
                p.contested_drop = True

    pre_dead_count = 0
    for player in players:
        for mod in ACTIVE_MODS:
            if mod.enabled:
                result = mod.on_player_spawn(player, match_number, CONFIG)
                if result in ("NO_LOAD", "CRASH"):
                    pre_dead_count += 1
                    reason = "didn't load in" if result == "NO_LOAD" else "crashed"
                    print(
                        f"{'❌' if result == 'NO_LOAD' else '💥'} {Colors.SOFT_RED}{display_name(player)} {reason}! {Colors.RESET}")
                    player.alive = False

    if pre_dead_count > 0:
        print(f"\n⚠️  {pre_dead_count} player(s) eliminated before fights began\n")
        sim_sleep(1.2)

    alive = [p for p in players if p.alive]
    current_placement = len(alive)
    placements = {}
    elims = {p.id: 0 for p in players}

    is_reload = CONFIG["tournament_type"] == "RELOAD"
    reboots_enabled = True
    reboot_cutoff = math.ceil(len(players) * 0.5)

    if is_reload:
        reboots = {p.id: 0 for p in players}
        print(f"\n{Colors.SOFT_CYAN + Colors.BOLD}🔄 RELOAD MODE: Each elim earns 1 reboot!{Colors.RESET}")
        print(f"{Colors.LIGHT_GRAY}   Reboots disable at {reboot_cutoff} players remaining{Colors.RESET}")
        sim_sleep(1)

    rage_quitters = [p for p in players if getattr(p, '_has_rage_quit', False)]
    if rage_quitters:
        print(
            f"\n{Colors.SOFT_RED + Colors.BOLD}😤 {len(rage_quitters)} player(s) have rage quit and won't play this match!{Colors.RESET}")
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
        if attacker.contested_drop and attacker.time_since_fight <= 2:
            if defender.drop_poi == attacker.drop_poi:
                return True

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
        if player.current_archetype == "Fragger":
            base *= 1.2
        elif player.current_archetype == "Aggressive":
            base *= 1.35
        elif player.current_archetype == "Passive":
            base *= 0.8

        confidence_boost = 0.15
        if player.skill >= 100:
            confidence_boost = 0.20
        base *= (1.0 + player.confidence * confidence_boost)

        loot_boost = 1.0 + (player.loot * 0.15)
        base *= loot_boost

        fear_level = player.fear.get(target.id, 0)
        base *= max(0.65, 1 - fear_level * 0.08)
        if late_game and player.skill >= 85:
            base *= 1.1
        return max(base, 1)

    def get_defense_weight(player, attacker):
        base = player.skill
        if player.current_archetype == "Passive":
            base *= 1.1
        elif player.current_archetype == "Aggressive":
            base *= 0.9

        confidence_boost = 0.1
        if player.skill >= 100:
            confidence_boost = 0.15
        base *= (1.0 + player.confidence * confidence_boost)

        loot_boost = 1.0 + (player.loot * 0.12)
        base *= loot_boost

        fear_level = player.fear.get(attacker.id, 0)
        base *= max(0.65, 1 - fear_level * 0.08)
        return max(base, 1)

    while len(alive) > 1:
        if is_reload and reboots_enabled and len(alive) <= reboot_cutoff:
            reboots_enabled = False
            print(
                f"\n{Colors.SOFT_RED + Colors.BOLD}⚠️  REBOOTS DISABLED! {len(alive)} players remaining - all deaths are now permanent!{Colors.RESET}\n")
            sim_sleep(1.5)

        attacker = choose_attacker(alive)
        defender = choose_target(attacker, alive, match_number, CONFIG)

        hatred = attacker.rivals.get(defender.id, 0)
        is_toxic_grief = hatred >= 5 and random.random() < 0.3

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
            if not is_toxic_grief:
                continue
            else:
                if random.random() < 0.05:
                    print(
                        f"{Colors.SOFT_RED}{Colors.ITALIC}🔥 {display_name(attacker)} is hunting down {display_name(defender)} — this rivalry has gotten personal!{Colors.RESET}")
                    sim_sleep(0.5)

        p1, p2 = attacker, defender

        atk1 = get_attack_weight(p1, p2)
        def2 = get_defense_weight(p2, p1)

        p1_win_chance = atk1 / (atk1 + def2)
        skill_gap = abs(p1.skill - p2.skill)

        if p1.skill >= 100 or p2.skill >= 100:
            variance_modifier = max(0.35, 1 - skill_gap / 80)
        else:
            variance_modifier = max(0.25, 1 - skill_gap / 100)

        roll = random.random() * variance_modifier

        current_leaderboard = sorted(players, key=lambda p: p.total_points, reverse=True)[:5]
        top5_names = {p.name for p in current_leaderboard}

        if CONFIG.get("killfeed_highlights", True):
            current_leaderboard = sorted(players, key=lambda p: p.total_points, reverse=True)[:5]
            top5_names = {p.name for p in current_leaderboard}

            def colored_name(p):
                base = display_name(p)
                if p.name in top5_names:
                    return f"{Colors.SOFT_GOLD}{base}{Colors.RESET}"
                return base
        else:
            def colored_name(p):
                return display_name(p)

        if roll < p1_win_chance:
            elims[p1.id] += 1
            register_elim(p1, p2, match_number)

            rivalry_p1_to_p2 = p1.rivals.get(p2.id, 0)
            rivalry_p2_to_p1 = p2.rivals.get(p1.id, 0)

            if rivalry_p1_to_p2 >= 5:
                conf_boost = min(0.3, 0.15 + (rivalry_p1_to_p2 - 5) * 0.02)
                p1.confidence = min(1.0, p1.confidence + conf_boost)

            if rivalry_p2_to_p1 >= 5:
                conf_loss = min(0.25, 0.12 + (rivalry_p2_to_p1 - 5) * 0.02)
                p2.confidence = max(-1.0, p2.confidence - conf_loss)

            p1.loot = max(0.0, p1.loot - 0.1)
            looted_amount = p2.loot * 0.7
            p1.loot = min(1.0, p1.loot + looted_amount)
            p1.time_since_fight = 0

            if is_reload:
                reboots[p1.id] += 1

            if is_reload and reboots_enabled and reboots.get(p2.id, 0) > 0:
                reboots[p2.id] -= 1
                emoji = "🔄"
                print(
                    f"{colored_name(p1)} {emoji} {colored_name(p2)} {Colors.SOFT_GREEN}(REBOOTED! {reboots[p2.id]} left){Colors.RESET}")
                p2.confidence = max(0.5, p2.confidence * 0.92)
                p2.loot = max(0.0, p2.loot - 0.25)
                p2.time_since_fight = 0
            else:
                p2.alive = False
                alive.remove(p2)
                placements[p2.id] = current_placement
                current_placement -= 1
                emoji = "🌩️" if random.random() < 0.05 else "⚔️"
                reboot_msg = f" {Colors.SOFT_RED}(OUT OF REBOOTS){Colors.RESET}" if is_reload and not reboots_enabled else ""
                print(
                    f"{colored_name(p1)} {emoji} {colored_name(p2)} {Colors.LIGHT_GRAY}(Placement: {placements[p2.id]}){reboot_msg}{Colors.RESET}")
                for mod in ACTIVE_MODS:
                    if mod.enabled:
                        mod.on_player_eliminated(p2, p1, CONFIG)
        else:
            elims[p2.id] += 1
            register_elim(p2, p1, match_number)

            rivalry_p2_to_p1 = p2.rivals.get(p1.id, 0)
            rivalry_p1_to_p2 = p1.rivals.get(p2.id, 0)

            if rivalry_p2_to_p1 >= 5:
                conf_boost = min(0.3, 0.15 + (rivalry_p2_to_p1 - 5) * 0.02)
                p2.confidence = min(1.0, p2.confidence + conf_boost)

            if rivalry_p1_to_p2 >= 5:
                conf_loss = min(0.25, 0.12 + (rivalry_p1_to_p2 - 5) * 0.02)
                p1.confidence = max(-1.0, p1.confidence - conf_loss)

            p2.loot = max(0.0, p2.loot - 0.1)
            looted_amount = p1.loot * 0.7
            p2.loot = min(1.0, p2.loot + looted_amount)
            p2.time_since_fight = 0

            if is_reload:
                reboots[p2.id] += 1

            if is_reload and reboots_enabled and reboots.get(p1.id, 0) > 0:
                reboots[p1.id] -= 1
                emoji = "🔄"
                print(
                    f"{colored_name(p2)} {emoji} {colored_name(p1)} {Colors.SOFT_GREEN}(REBOOTED! {reboots[p1.id]} left){Colors.RESET}")
                p1.confidence = max(0.5, p1.confidence * 0.92)
                p1.loot = max(0.0, p1.loot - 0.25)
                p1.time_since_fight = 0
            else:
                p1.alive = False
                alive.remove(p1)
                placements[p1.id] = current_placement
                current_placement -= 1
                emoji = "🌩️" if random.random() < 0.05 else "⚔️"
                reboot_msg = f" {Colors.SOFT_RED}(OUT OF REBOOTS){Colors.RESET}" if is_reload and not reboots_enabled else ""
                print(
                    f"{colored_name(p2)} {emoji} {colored_name(p1)} {Colors.LIGHT_GRAY}(Placement: {placements[p1.id]}){reboot_msg}{Colors.RESET}")
                for mod in ACTIVE_MODS:
                    if mod.enabled:
                        mod.on_player_eliminated(p1, p2, CONFIG)

        for p in alive:
            if p != attacker and p != defender:
                p.time_since_fight += 1
                if p.contested_drop and p.time_since_fight <= 3:
                    loot_gain = 0.03
                elif p.time_since_fight <= 5:
                    loot_gain = 0.08
                else:
                    loot_gain = 0.05

                p.loot = min(1.0, p.loot + loot_gain)

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
        for rival_id, rivalry_level in p.rivals.items():
            if rivalry_level >= 5:
                rival = next((r for r in players if r.id == rival_id), None)
                if rival and not p.alive and rival.alive:
                    conf_loss = 0.05 + (rivalry_level - 5) * 0.01
                    p.confidence = max(-1.0, p.confidence - min(0.15, conf_loss))

                elif rival and p.alive and not rival.alive:
                    rival_killer = next((k for k in players if rival_id in [v.id for v in players if
                                                                            not v.alive and k.rivals.get(v.id, 0) > 0]),
                                        None)
                    if rival_killer and rival_killer.id != p.id:
                        conf_loss = 0.03 + (rivalry_level - 5) * 0.005
                        p.confidence = max(-1.0, p.confidence - min(0.1, conf_loss))

    for p in players:
        placement = placements.get(p.id, len(players))
        elim_count = elims.get(p.id, 0)

        t_type = CONFIG["tournament_type"]
        if t_type == "VICTORY_CUP":
            pts = TOURNAMENT_TYPES[t_type]["points_per_win"] if placement == 1 else 0
        else:
            pts = placement_points(placement, t_type) + elim_count * CONFIG["elim_points"]

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
    if t_type == "VICTORY_CUP":
        print(f"• Placement Points: 100")
    else:
        print(f"• Placement Points: {placement_points(1)}")

    sim_sleep(0.5)
    print(f"• Total Points: {winner.total_points}")
    sim_sleep(1)

    print(f"\n👑 {Colors.ITALIC}{commentary}{Colors.RESET}\n")
    sim_sleep(1)
    print("━" * 50)
    sim_sleep(1)

    for mod in ACTIVE_MODS:
        if mod.enabled and hasattr(mod, 'on_match_end'):
            mod.on_match_end(players, winner, CONFIG)

    update_confidence(players)
    if CONFIG.get("archetype_switching", True):
        for p in players:
            maybe_switch_archetype(p, match_number)
    print_top10_cumulative(players)

    if CONFIG.get("show_win_tickers", True):
        halfway_game = CONFIG["matches"] // 2
        before_final_game = CONFIG["matches"] - 1

        if match_number == halfway_game or match_number == before_final_game:
            if match_number == halfway_game:
                print("\n🎙️ Caster: Let's check the odds before the second half of the tournament...")
                sim_sleep(2)
                print("\n" + "─" * 50)
                print("HALFTIME UPDATE – WIN % TICKER")
            else:
                print("\n🎙️ Caster: Quick odds check before the final drop...")
                sim_sleep(2)
                print("\n" + "─" * 50)
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
    new_seed = random.randint(1, 1_000_000)
    CONFIG["random_seed"] = new_seed
    random.seed(new_seed)
    save_config(CONFIG)
    pro_players_skills = get_pro_players_from_config()

    players = []

    num_pro_players = min(len(pro_players_skills), CONFIG["players"])

    weights = [skill ** 2.5 for name, skill, arch, org in pro_players_skills]

    weighted_pool = []
    for i, player in enumerate(pro_players_skills):
        w = weights[i]
        key = random.random() ** (1.0 / w)
        weighted_pool.append((key, player))

    weighted_pool.sort(key=lambda x: x[0], reverse=True)
    selected_pros = [player for key, player in weighted_pool[:num_pro_players]]

    selected_pros.sort(key=lambda x: x[1], reverse=True)

    for i, (name, skill, arch, org) in enumerate(selected_pros):
        variance = random.uniform(-0.05, 0.05)
        adjusted_skill = round(skill * (1 + variance))
        adjusted_skill = max(1, adjusted_skill)

        players.append(Player(
            id=i,
            name=name,
            skill=adjusted_skill,
            archetype=arch,
            org=org
        ))

    for p in players:
        p.original_archetype = p.archetype
        p.current_archetype = p.archetype
        p.has_switched_archetype = False

    for i in range(num_pro_players, CONFIG["players"]):
        base_skill = random.randint(1, 75)
        variance = random.uniform(-0.05, 0.05)
        adjusted_skill = round(base_skill * (1 + variance))
        adjusted_skill = max(1, adjusted_skill)

        players.append(Player(
            id=i,
            name=f"Fill_{i + 1}",
            skill=adjusted_skill
        ))

    assign_archetypes(players)

    players.sort(key=lambda p: p.skill, reverse=True)

    for i, p in enumerate(players):
        p.id = i

    social_data = load_social_data()

    for p in players:
        p_key = p.name

        if p_key in social_data.get("friendships", {}):
            for friend_name, strength in social_data["friendships"][p_key].items():
                friend = next((other for other in players if other.name == friend_name), None)
                if friend:
                    p.friends.add(friend.id)

        if p_key in social_data.get("rivalries", {}):
            for rival_name, hatred in social_data["rivalries"][p_key].items():
                rival = next((other for other in players if other.name == rival_name), None)
                if rival:
                    p.rivals[rival.id] = hatred

    for p in players:
        if len(p.friends) < 2:
            num_needed = random.randint(2, 3) - len(p.friends)
            potential_friends = [other for other in players if other.id != p.id and other.id not in p.friends]
            if len(potential_friends) >= num_needed:
                chosen_friends = random.sample(potential_friends, num_needed)
                for friend in chosen_friends:
                    p.friends.add(friend.id)
                    friend.friends.add(p.id)

    for mod in ACTIVE_MODS:
        if mod.enabled:
            mod.on_tournament_start(players, CONFIG)

    load_career_data(players)

    if CONFIG.get("walkouts", False):
        walkout_hype(players)

    for match_number in range(1, CONFIG["matches"] + 1):
        simulate_match(players, match_number)

        if CONFIG.get("archetype_switching", True):
            for p in players:
                maybe_switch_archetype(p, match_number)

    update_careers(players)
    save_career_data(players)
    update_social_data(players)
    print(f"{Colors.LIGHT_GRAY}💾 Career data saved (backup created){Colors.RESET}")
    init_season_players(players)
    update_season_stats(players)
    for p in players:
        p.current_archetype = p.original_archetype
        p.has_switched_archetype = False
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
    console.print("\n" + "━" * 60)
    console.print(" FINAL FORTNITE TOURNAMENT LEADERBOARD")
    console.print("━" * 60)

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
    console.print("━" * 60)


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
        if rank <= 10:
            p.career_achievements.append({
                "placement": rank,
                "type": t_type,
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "earnings": earned
            })

        if rank == 1 and t_type != "VICTORY_CUP":
            p.career_wins += 1
            if t_type == "CASH_CUP":
                p.career_cashcup_wins += 1
            elif t_type == "ELITE_SERIES":
                p.career_elite_series_wins += 1
            elif t_type == "RELOAD":
                p.career_reload_wins += 1
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
        "leaderboard": leaderboard[:15]
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
    print(
        f"⭐ Earnings: ${stats['earnings']:,} | Points: {stats['points']} | Wins: {stats['wins']} | Elims: {stats['elims']}")
    print(f"   MVP Quote: {random.choice(mvp_quotes)}")
    print("━" * 60)
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


def compare_players(p1, p2):
    console.print("\n⚔️ PLAYER COMPARISON ⚔️")
    console.print("━" * 60)

    def arrow(val1, val2, higher_is_better=True):
        if val1 == val2:
            return "[grey]—[/]"
        if (val1 > val2 and higher_is_better) or (val1 < val2 and not higher_is_better):
            return "[green]▲[/]"
        else:
            return "[red]▼[/]"

    top10 = lambda p: sum(1 for a in getattr(p, "career_achievements", []) if a["placement"] <= 10)
    top5 = lambda p: sum(1 for a in getattr(p, "career_achievements", []) if a["placement"] <= 5)
    top3 = lambda p: sum(1 for a in getattr(p, "career_achievements", []) if a["placement"] <= 3)
    dominance = lambda \
            p: p.career_lan_wins * 3 + p.career_fncs_wins * 2 + p.career_cashcup_wins * 1 + p.career_victorycup_wins * 1
    major_ratio = lambda p: (p.career_lan_wins + p.career_fncs_wins) / max(1, (
            p.career_cashcup_wins + p.career_victorycup_wins))
    earnings_per_major = lambda p: p.career_earnings / max(1, (p.career_lan_wins + p.career_fncs_wins))
    total_major_wins = lambda p: p.career_fncs_wins + p.career_lan_wins

    table = Table(
        show_header=True,
        header_style="bold",
        box=None,
        show_lines=True
    )

    table.add_column("", justify="left", width=22)
    table.add_column(p1.name, justify="center", width=16)
    table.add_column("│", justify="center", width=3)
    table.add_column(p2.name, justify="center", width=16)

    table.add_row("Org", p1.org, "│", p2.org)
    table.add_row("Career Tier", f"👑 {get_career_tier(p1)}", "│", f"👑 {get_career_tier(p2)}")

    table.add_row("📊 CAREER OVERVIEW", "—", "—", "—")
    table.add_row("Tournament Wins", f"{arrow(p1.career_wins, p2.career_wins)} {p1.career_wins}", "│",
                  f"{arrow(p2.career_wins, p1.career_wins)} {p2.career_wins}")
    table.add_row("Tournaments Played",
                  f"{arrow(p1.career_tournaments, p2.career_tournaments)} {p1.career_tournaments}", "│",
                  f"{arrow(p2.career_tournaments, p1.career_tournaments)} {p2.career_tournaments}")
    table.add_row("Career Eliminations", f"{arrow(p1.career_kills, p2.career_kills)} {p1.career_kills}", "│",
                  f"{arrow(p2.career_kills, p1.career_kills)} {p2.career_kills}")
    table.add_row("Career Earnings", f"{arrow(p1.career_earnings, p2.career_earnings)} ${p1.career_earnings:,}", "│",
                  f"{arrow(p2.career_earnings, p1.career_earnings)} ${p2.career_earnings:,}")

    table.add_row("🏆 MAJOR TITLES", "—", "—", "—")
    table.add_row("LAN Titles", f"{arrow(p1.career_lan_wins, p2.career_lan_wins)} {p1.career_lan_wins}", "│",
                  f"{arrow(p2.career_lan_wins, p1.career_lan_wins)} {p2.career_lan_wins}")
    table.add_row("FNCS Titles", f"{arrow(p1.career_fncs_wins, p2.career_fncs_wins)} {p1.career_fncs_wins}", "│",
                  f"{arrow(p2.career_fncs_wins, p1.career_fncs_wins)} {p2.career_fncs_wins}")
    table.add_row("Total Major Wins", f"{arrow(total_major_wins(p1), total_major_wins(p2))} {total_major_wins(p1)}",
                  "│", f"{arrow(total_major_wins(p2), total_major_wins(p1))} {total_major_wins(p2)}")

    table.add_row("Cash Cup Wins", f"{arrow(p1.career_cashcup_wins, p2.career_cashcup_wins)} {p1.career_cashcup_wins}",
                  "│", f"{arrow(p2.career_cashcup_wins, p1.career_cashcup_wins)} {p2.career_cashcup_wins}")
    table.add_row("Victory Cup Wins",
                  f"{arrow(p1.career_victorycup_wins, p2.career_victorycup_wins)} {p1.career_victorycup_wins}", "│",
                  f"{arrow(p2.career_victorycup_wins, p1.career_victorycup_wins)} {p2.career_victorycup_wins}")

    table.add_row("🎯 BEST PLACEMENT", "—", "—", "—")
    table.add_row("Best Finish", f"{arrow(p1.best_finish, p2.best_finish, higher_is_better=False)} #{p1.best_finish}",
                  "│", f"{arrow(p2.best_finish, p1.best_finish, higher_is_better=False)} #{p2.best_finish}")

    table.add_row("📈 DERIVED STATS", "—", "—", "—")
    table.add_row("Top 3 Finishes", f"{arrow(top3(p1), top3(p2))} {top3(p1)}", "│",
                  f"{arrow(top3(p2), top3(p1))} {top3(p2)}")
    table.add_row("Top 5 Finishes", f"{arrow(top5(p1), top5(p2))} {top5(p1)}", "│",
                  f"{arrow(top5(p2), top5(p1))} {top5(p2)}")
    table.add_row("Top 10 Finishes", f"{arrow(top10(p1), top10(p2))} {top10(p1)}", "│",
                  f"{arrow(top10(p2), top10(p1))} {top10(p2)}")
    table.add_row("Dominance Score", f"{arrow(dominance(p1), dominance(p2))} {dominance(p1)}", "│",
                  f"{arrow(dominance(p2), dominance(p1))} {dominance(p2)}")
    table.add_row("Major/Minor Ratio", f"{arrow(major_ratio(p1), major_ratio(p2))} {major_ratio(p1):.2f}", "│",
                  f"{arrow(major_ratio(p2), major_ratio(p1))} {major_ratio(p2):.2f}")
    table.add_row("Earnings per Major",
                  f"{arrow(earnings_per_major(p1), earnings_per_major(p2))} ${earnings_per_major(p1):,.0f}", "│",
                  f"{arrow(earnings_per_major(p2), earnings_per_major(p1))} ${earnings_per_major(p2):,.0f}")
    table.add_row(
        "GOAT Index",
        f"{arrow(get_goat_index(p1), get_goat_index(p2))} {get_goat_index(p1):,}",
        "│",
        f"{arrow(get_goat_index(p2), get_goat_index(p1))} {get_goat_index(p2):,}"
    )

    console.print(table)
    console.print("━" * 60)


def show_player_history(players: List[Player]):
    sorted_players = sort_leaderboard(players)
    while True:
        user_input = input(
            "\nChoose an option:\n"
            "  • [number]        → View player by rank\n"
            "  • [player name]   → View player profile\n"
            "  • [org name]      → View org page\n"
            "  • career          → Career leaderboard\n"
            "  • season          → Season leaderboard\n"
            "  • goat            → 🐐 GOAT leaderboard\n"
            "  • compare A B     → Compare two players\n"
            "  • q               → Quit\n"
            "> "
        ).strip().lower()

        if user_input == 'q':
            break

        if user_input.startswith("compare"):
            parts = user_input.split()

            if len(parts) < 3:
                print("Usage: compare <player1> <player2>")
                continue

            name1 = parts[1]
            name2 = parts[2]

            p1 = next((p for p in players if name1 in p.name.lower()), None)
            p2 = next((p for p in players if name2 in p.name.lower()), None)

            if not p1 or not p2:
                print("One or both players not found.")
                continue

            compare_players(p1, p2)
            continue

        if user_input == "goat":
            goat_players = [p for p in sorted_players if hasattr(p, "career_earnings")]

            if not goat_players:
                print("No career data available yet.")
                continue

            goat_players.sort(key=get_goat_index, reverse=True)

            table = Table(title="🐐 GOAT LEADERBOARD", show_header=True, header_style="bold")

            table.add_column("Rank", justify="right", width=4)
            table.add_column("Player", width=10)
            table.add_column("GOAT Index", justify="right", width=12)
            table.add_column("Majors", justify="right", width=6)
            table.add_column("Earnings", justify="right", width=12)

            for rank, p in enumerate(goat_players, 1):
                majors = p.career_lan_wins + p.career_fncs_wins

                table.add_row(
                    str(rank),
                    p.name,
                    f"{get_goat_index(p):,}",
                    str(majors),
                    f"${p.career_earnings:,}"
                )

            console.print()
            console.print(table)
            continue

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
            table.add_column("Career Tier", justify="right")

            for rank, p in enumerate(career_players, 1):
                table.add_row(
                    str(rank),
                    p.name,
                    str(p.career_wins),
                    str(p.career_tournaments),
                    str(p.career_kills),
                    f"${p.career_earnings:,}",
                    get_career_tier(p)
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
                player = sorted_players[rank - 1]
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
                player = matches[int(choice) - 1]

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
                print(f"\n🏅 Career Stats — {player.name} (👑 {get_career_tier(player)})")
                print("─" * 35)

                print("🏆 MAJOR TOURNAMENT VICTORIES")
                print(f"  LAN Titles:            {player.career_lan_wins:,}")
                print(f"  FNCS Titles:           {player.career_fncs_wins:,}")
                print(f"  Total Major Wins:      {get_major_wins(player):,}")
                print(f"  Elite Series Wins:     {player.career_elite_series_wins:,}")
                print(f"  Reload Wins:           {player.career_reload_wins:,}")
                print(f"  Cash Cup Wins:         {player.career_cashcup_wins:,}")
                print(f"  Victory Cup Game Wins: {player.career_victorycup_wins:,}")
                print(f"  Overall Tournament Wins: {player.career_wins:,}")

                print("\n📊 CAREER OVERVIEW")
                print(f"  GOAT Index:            {get_goat_index(player)}")
                print(f"  Tournaments Played:    {player.career_tournaments:,}")
                print(f"  Career Eliminations:   {player.career_kills:,}")
                print(f"  Career Earnings:       ${player.career_earnings:,}")
                print(f"  Best Placement:        #{player.best_finish}")

                top_achievements = get_top_achievements(player)

                if top_achievements:
                    print("\n🏆 CAREER HIGHLIGHTS")
                    print("─" * 35)
                    for a in top_achievements:
                        medal = {1: "🥇", 2: "🥈", 3: "🥉", 4: "#4", 5: "#5", 6: "#6", 7: "#7", 8: "#8", 9: "#9",
                                 10: "#10"}.get(a["placement"], "•")
                        t_label = TOURNAMENT_TYPES[a["type"]]["label"]
                        print(f"{medal} {t_label} ({a['date']})")

            print("─" * 35)
            if player.name in SEASON["season_players"]:
                s = SEASON["season_players"][player.name]
                print(f"\n📆 Season {SEASON['current_season']} Stats")
                print(f"Season Points: {s['points']}")
                print(f"Season Wins: {s['wins']}")
                print(f"Season Elims: {s['elims']}")
                print(f"Season Earnings: ${s['earnings']:,}")

                try:
                    with open(SEASON_FILE, "r", encoding="utf-8") as f:
                        season_data = json.load(f)
                except FileNotFoundError:
                    season_data = {"history": []}
                except json.JSONDecodeError:
                    season_data = {"history": []}

                player_prime = {"season": None, "earnings": 0}

                if "history" in season_data:
                    for season_entry in season_data["history"]:
                        season_num = season_entry.get("season", "?")
                        leaderboard = season_entry.get("leaderboard", [])

                        player_entry = next(
                            (entry for entry in leaderboard if entry[0] == player.name),
                            None
                        )

                        if player_entry:
                            earnings = player_entry[1].get("earnings", 0)
                            if earnings > player_prime["earnings"]:
                                player_prime = {"season": season_num, "earnings": earnings}

                if player_prime["season"] is not None:
                    print(
                        f"🏆 Prime Season: Season {player_prime['season']} — ${player_prime['earnings']:,} earnings")
                else:
                    print(f"🏆 Prime Season: No prime season yet -- keep grinding!")


def get_major_wins(player):
    return player.career_lan_wins + player.career_fncs_wins


def get_career_tier(player):
    score = (
            player.career_earnings / 500_000 +
            player.career_wins * 3.0 +
            player.career_lan_wins * 8.0 +
            player.career_fncs_wins * 7.0 +
            player.career_elite_series_wins * 5.0 +
            player.career_cashcup_wins * 2.0 +
            player.career_tournaments * 0.15 +
            player.career_kills / 1000
    )

    if score < 30:
        return "Rookie"
    elif score < 45:
        return "Challenger"
    elif score < 60:
        return "Contender"
    elif score < 80:
        return "Elite"
    elif score < 140:
        return "Champion"
    elif score < 200:
        return "Legend"
    else:
        return "GOAT"


def get_top_achievements(player, limit=6):
    if not hasattr(player, "career_achievements"):
        return []

    def weight(a):
        placement_scores = {1: 100, 2: 85, 3: 70, 4: 55, 5: 40}
        score = placement_scores.get(a["placement"], max(0, 40 - (a["placement"] - 5) * 2))

        type_multiplier = {
            "LAN": 4,
            "FNCS": 3,
            "ELITE_SERIES": 2,
            "RELOAD": 1.5,
            "CASH_CUP": 1.0,
            "VICTORY_CUP": 0.5
        }
        score *= type_multiplier.get(a["type"], 1.0)

        return score

    return sorted(
        player.career_achievements,
        key=weight,
        reverse=True
    )[:limit]


def get_goat_index(p):
    majors = p.career_lan_wins + p.career_fncs_wins

    return round(
        p.career_lan_wins * 120 +
        p.career_fncs_wins * 90 +
        p.career_elite_series_wins * 25 +
        p.career_reload_wins * 18 +
        p.career_cashcup_wins * 12 +
        p.career_victorycup_wins * 8 +

        sum(1 for a in getattr(p, "career_achievements", []) if a["placement"] <= 10) * 4 +

        min(p.career_earnings / 100_000, 60) +

        p.career_tournaments * 0.75,
        2
    )


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

    bar_length = 16
    filled = min(played, total)
    empty = bar_length - filled

    filled_char = "█"
    empty_char = "░"

    bar = (
            filled_char * filled +
            empty_char * empty
    )

    percent = (played / total) * 100 if total > 0 else 0

    print(f"[{bar}] ({percent:.0f}%)")


def restore_from_backup_menu():
    """Menu for restoring from automatic backups"""
    backup_dir = os.path.join(REGION_DATA_DIR, "backups")

    if not os.path.exists(backup_dir):
        print("\n❌ No backups found. Backups are created after each tournament.")
        input("\nPress Enter to continue...")
        return

    career_backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("career_stats_backup_")], reverse=True)
    season_backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("season_data_backup_")], reverse=True)

    if not career_backups and not season_backups:
        print("\n❌ No backups found. Backups are created after each tournament.")
        input("\nPress Enter to continue...")
        return

    while True:
        print("\n" + "━" * 60)
        print("🔄 RESTORE FROM BACKUP")
        print("━" * 60)
        print(f"\nBackup Location: {backup_dir}")
        print(f"Career Backups: {len(career_backups)} | Season Backups: {len(season_backups)}")

        print("\n⚠️  WARNING: Restoring will overwrite your current data!")
        print("   Current data will be backed up automatically before restore.\n")

        print("Available Backups (most recent first):")
        print("─" * 60)

        if career_backups:
            print("\n💼 CAREER DATA BACKUPS:")
            for i, backup in enumerate(career_backups[:10], 1):
                timestamp = backup.replace("career_stats_backup_", "").replace(".json", "")
                print(f"  C{i}. {timestamp}")
            if len(career_backups) > 10:
                print(f"  ... and {len(career_backups) - 10} more")

        if season_backups:
            print("\n📆 SEASON DATA BACKUPS:")
            for i, backup in enumerate(season_backups[:10], 1):
                timestamp = backup.replace("season_data_backup_", "").replace(".json", "")
                print(f"  S{i}. {timestamp}")
            if len(season_backups) > 10:
                print(f"  ... and {len(season_backups) - 10} more")

        print("\n" + "─" * 60)
        print("Commands:")
        print("  C <#>   → Restore Career Data from backup")
        print("  S <#>   → Restore Season Data from backup")
        print("  BOTH <#> → Restore both Career & Season from matching timestamp")
        print("  B       → Back to Save Management")
        print("━" * 60)

        choice = input("> ").strip().lower()

        if choice == "b":
            break

        elif choice.startswith("c "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(career_backups):
                    backup_file = career_backups[idx]
                    backup_path = os.path.join(backup_dir, backup_file)
                    timestamp = backup_file.replace("career_stats_backup_", "").replace(".json", "")

                    print(f"\n⚠️  Restore career data from {timestamp}?")
                    print("   Your current career data will be backed up first.")
                    confirm = input("Continue? (y/n): ").strip().lower()

                    if confirm == "y":
                        create_backup(CAREER_FILE, "career_stats")

                        import shutil
                        shutil.copy2(backup_path, CAREER_FILE)
                        print(f"✅ Career data restored from {timestamp}")
                        print("🔄 Please restart the simulator to see changes.")
                        sim_sleep(2)
                else:
                    print("❌ Invalid backup number")
            except (ValueError, IndexError):
                print("❌ Usage: C <number>")
            sim_sleep(0.8)

        elif choice.startswith("s "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(season_backups):
                    backup_file = season_backups[idx]
                    backup_path = os.path.join(backup_dir, backup_file)
                    timestamp = backup_file.replace("season_data_backup_", "").replace(".json", "")

                    print(f"\n⚠️  Restore season data from {timestamp}?")
                    print("   Your current season data will be backed up first.")
                    confirm = input("Continue? (y/n): ").strip().lower()

                    if confirm == "y":
                        save_season()

                        import shutil
                        shutil.copy2(backup_path, SEASON_FILE)
                        print(f"✅ Season data restored from {timestamp}")
                        print("🔄 Please restart the simulator to see changes.")
                        sim_sleep(2)
                else:
                    print("❌ Invalid backup number")
            except (ValueError, IndexError):
                print("❌ Usage: S <number>")
            sim_sleep(0.8)

        elif choice.startswith("both "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < min(len(career_backups), len(season_backups)):
                    career_file = career_backups[idx]
                    season_file = season_backups[idx]
                    career_path = os.path.join(backup_dir, career_file)
                    season_path = os.path.join(backup_dir, season_file)

                    career_time = career_file.replace("career_stats_backup_", "").replace(".json", "")
                    season_time = season_file.replace("season_data_backup_", "").replace(".json", "")

                    print(f"\n⚠️  Restore both career and season data?")
                    print(f"   Career backup: {career_time}")
                    print(f"   Season backup: {season_time}")
                    print("   Current data will be backed up first.")
                    confirm = input("Continue? (y/n): ").strip().lower()

                    if confirm == "y":
                        create_backup(CAREER_FILE, "career_stats")
                        save_season()

                        import shutil
                        shutil.copy2(career_path, CAREER_FILE)
                        shutil.copy2(season_path, SEASON_FILE)
                        print(f"✅ Career and season data restored")
                        print("🔄 Please restart the simulator to see changes.")
                        sim_sleep(2)
                else:
                    print("❌ Invalid backup number or mismatched backup counts")
            except (ValueError, IndexError):
                print("❌ Usage: BOTH <number>")
            sim_sleep(0.8)

        else:
            print("❌ Unknown command")
            sim_sleep(0.8)


def save_management_menu():
    """Menu for managing save files"""
    while True:
        print("\n" + "━" * 50)
        print("💾 SAVE MANAGEMENT")
        print("━" * 50)

        current = get_current_save()
        saves = list_saves()

        print(f"\nCurrent Save: {Colors.SOFT_GREEN + Colors.BOLD}{current}{Colors.RESET}")
        print("\nAvailable Saves:")
        print("─" * 50)

        if not saves:
            print("  No saves found. Create one to get started!")
        else:
            for i, save_info in enumerate(saves, 1):
                is_current = " ← CURRENT" if save_info["name"] == current else ""
                print(f"{i}. {Colors.BOLD}{save_info['name']}{Colors.RESET}{is_current}")

                if save_info["regions"]:
                    for region, region_data in sorted(save_info["regions"].items()):
                        print(f"   {region}: Season {region_data['season']} | {region_data['tournaments']} tournaments")
                else:
                    print("   No data yet")

                print(f"   Last played: {save_info['last_played']}")
                if i < len(saves):
                    print()

        print("\n" + "─" * 50)
        print("Commands:")
        print("  N       → Create New Save")
        print("  L <#>   → Load Save")
        print("  R <#>   → Rename Save")
        print("  D <#>   → Delete Save")
        print("  S       → Save Current Progress")
        print("  RESTORE → Restore from Backup")
        print("  B       → Back to Main Menu")
        print("━" * 50)

        choice = input("> ").strip().lower()

        if choice == "b":
            save_current_to_file(current)
            print(f"💾 Progress auto-saved to: {current}")
            sim_sleep(0.8)
            break

        elif choice == "n":
            name = input("Enter save name: ").strip()
            if not name:
                print("❌ Save name cannot be empty")
                continue

            import re
            name = re.sub(r'[<>:"/\\|?*]', '', name)

            success, msg = create_save(name)
            if success:
                print(f"✅ {msg}")
                sim_sleep(0.8)
            else:
                print(f"❌ {msg}")
                sim_sleep(0.8)

        elif choice == "s":
            save_current_to_file(current)
            print(f"✅ Progress saved to: {current}")
            sim_sleep(0.8)

        elif choice.startswith("l "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(saves):
                    save_name = saves[idx]["name"]
                    print(f"\n⚠️  Loading '{save_name}' will save your current progress first.")
                    confirm = input("Continue? (y/n): ").strip().lower()
                    if confirm == "y":
                        success, msg = load_save(save_name)
                        if success:
                            print(f"✅ {msg}")
                            print("🔄 Restarting to apply changes...")
                            sim_sleep(1.5)
                            print("\n⚠️  Please restart the simulator to complete save load.")
                            exit()
                        else:
                            print(f"❌ {msg}")
                else:
                    print("❌ Invalid save number")
            except (ValueError, IndexError):
                print("❌ Usage: L <number>")
            sim_sleep(0.8)

        elif choice.startswith("r "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(saves):
                    old_name = saves[idx]["name"]
                    new_name = input(f"Enter new name for '{old_name}': ").strip()
                    if not new_name:
                        print("❌ Name cannot be empty")
                        continue

                    import re
                    new_name = re.sub(r'[<>:"/\\|?*]', '', new_name)

                    success, msg = rename_save(old_name, new_name)
                    if success:
                        print(f"✅ {msg}")
                    else:
                        print(f"❌ {msg}")
                else:
                    print("❌ Invalid save number")
            except (ValueError, IndexError):
                print("❌ Usage: R <number>")
            sim_sleep(0.8)

        elif choice.startswith("d "):
            try:
                idx = int(choice.split()[1]) - 1
                if 0 <= idx < len(saves):
                    save_name = saves[idx]["name"]
                    if save_name == current:
                        print("❌ Cannot delete currently loaded save")
                    else:
                        confirm = input(f"⚠️  Delete '{save_name}'? This cannot be undone! (y/n): ").strip().lower()
                        if confirm == "y":
                            success, msg = delete_save(save_name)
                            if success:
                                print(f"✅ {msg}")
                            else:
                                print(f"❌ {msg}")
                else:
                    print("❌ Invalid save number")
            except (ValueError, IndexError):
                print("❌ Usage: D <number>")
            sim_sleep(0.8)

        elif choice == "restore":
            restore_from_backup_menu()

        else:
            print("❌ Unknown command")
            sim_sleep(0.8)


def how_to_play_guide():
    while True:
        print("\n" + "━" * 60)
        print("📖 HOW TO PLAY - FORTNITE TOURNAMENT SIMULATOR")
        print("━" * 60)
        print("1. Config Options")
        print("2. Understanding the Kill Feed")
        print("3. Tournament Types")
        print("4. Mods System")
        print("5. Player Mechanics")
        print("6. Career & Season Stats")
        print("B. Back to Main Menu")
        print("━" * 60)

        choice = input("> ").strip().lower()

        if choice == "b":
            break

        elif choice == "1":
            print("\n" + "━" * 60)
            print("⚙️  CONFIG OPTIONS")
            print("━" * 60)
            print("\n📊 PLAYERS:")
            print("  Number of players in each tournament")
            print("  • More players = longer games, more variance")
            print("  • Fewer players = faster, more consistent results")

            print("\n🎮 MATCHES:")
            print("  Number of games per tournament")
            print("  • Standard tournaments: 6-12 games")
            print("  • More games = more consistent rankings")

            print("\n🌀 STORM CIRCLES:")
            print("  Number of storm phases per game")
            print("  • More circles = longer games, more fights")
            print("  • Fewer circles = faster games, early aggression")

            print("\n💀 ELIM POINTS:")
            print("  Points awarded per elimination")
            print("  • Higher = fragging is more rewarded")
            print("  • Lower = placement matters more")

            print("\n🏆 TOURNAMENT TYPE:")
            print("  Changes format, prize pool, and scoring")
            print("  • Cash Cup: Standard competitive format")
            print("  • Elite Series: Higher stakes, better players")
            print("  • FNCS: Major tournament with prestige")
            print("  • LAN: Offline event, highest prestige")
            print("  • RELOAD: 40 players, respawn mechanic")
            print("  • Victory Cup: Battle Royale, winner-takes-all")

            print("\n🌍 REGION:")
            print("  Player pool and competition level")
            print("  • EU: Toughest competition")
            print("  • NA: High skill ceiling")
            print("  • MIXED: Best of EU + NA for LANs")

            print("\n🚶 WALKOUTS:")
            print("  Player introductions before tournament")
            print("  • ON: Shows hype walkouts (adds time)")
            print("  • OFF: Skip straight to tournament")

            print("\n🎯 ARCHETYPE SWITCHING:")
            print("  Players can change playstyle if underperforming")
            print("  • ON: Dynamic adaptation mid-tournament")
            print("  • OFF: Players stick to their style")

            print("\n📺 KILLFEED HIGHLIGHTS:")
            print("  Emphasizes top 5 players in kill feed")
            print("  • ON: Gold names for leaderboard players")
            print("  • OFF: Standard kill feed")

            input("\nPress Enter to continue...")

        elif choice == "2":
            print("\n" + "━" * 60)
            print("🎯 UNDERSTANDING THE KILL FEED")
            print("━" * 60)

            print("\n🌟 GOLD NAMES:")
            print(f"  {Colors.SOFT_GOLD}Bugha{Colors.RESET} ⚔️ Clix")
            print("  = Player is currently in top 5 on leaderboard")

            print("\n💀 EMOTES:")
            print(f"  {Colors.SOFT_PURPLE}💀 Clix hits the emote on Bugha!{Colors.RESET}")
            print("  = Disrespectful elimination, major rivalry boost")

            print("\n🔥 TOXIC RIVALRIES:")
            print(f"  {Colors.SOFT_RED}🔥 Bugha is hunting down Clix — this rivalry has gotten personal!{Colors.RESET}")
            print("  = Player ignoring strategy to grief their rival")

            print("\n✅ REVENGE:")
            print(f"  {Colors.SOFT_GREEN}✅ Bugha finally got revenge on Clix!{Colors.RESET}")
            print("  = Player eliminated their toxic rival (8+ rivalry)")

            print("\n⭐ CLUTCH ELIMINATIONS:")
            print("  ⭐ CLUTCH ELIM! Bugha ⚔️ Clix")
            print("  = Clutch player getting kill in high-pressure situation")

            print("\n🔄 RELOAD MODE:")
            print(f"  Bugha 🔄 Clix {Colors.SOFT_GREEN}(REBOOTED! 2 left){Colors.RESET}")
            print("  = Player used a reboot to respawn")
            print(f"  Bugha ⚔️ Clix {Colors.SOFT_RED}(OUT OF REBOOTS){Colors.RESET}")
            print("  = Player eliminated with no reboots left")

            input("\nPress Enter to continue...")

        elif choice == "3":
            print("\n" + "━" * 60)
            print("🏆 TOURNAMENT TYPES")
            print("━" * 60)

            print("\n💰 CASH CUP:")
            print("  • Standard competitive format")
            print("  • Prize pool: $10K first place")
            print("  • Career weight: 12 points per win")

            print("\n⭐ ELITE SERIES:")
            print("  • Standard competitive format with higher stakes")
            print("  • Prize pool: $50K first place")
            print("  • Career weight: 25 points per win")

            print("\n🔄 RELOAD SOLOS:")
            print("  • 40 players, 8 games")
            print("  • Respawn mechanic: kill = +1 reboot")
            print("  • Reboots disable at 50% remaining")
            print("  • Prize pool: $40K first place")
            print("  • Career weight: 18 points per win")
            print("  • Custom point system for smaller lobby")

            print("\n🏆 FNCS (MAJOR):")
            print("  • Highest stakes online tournament")
            print("  • Prize pool: $100K first place")
            print("  • Career weight: 90 points per win")

            print("\n🏟️  LAN (MAJOR):")
            print("  • Offline championship event")
            print("  • Prize pool: $250K first place")
            print("  • Career weight: 120 points per win")

            print("\n👑 VICTORY CUP:")
            print("  • Battle Royale format")
            print("  • Points only for Victory Royales")
            print("  • Prize pool: $400 per game win")
            print("  • Career weight: 8 points per win")

            input("\nPress Enter to continue...")

        elif choice == "4":
            print("\n" + "━" * 60)
            print("🎮 MODS SYSTEM")
            print("━" * 60)

            print("\n💥 TECHNICAL ISSUES:")
            print("  • Players can crash or fail to load")
            print("  • Adds realism to tournament chaos")

            print("\n😤 RAGE QUIT:")
            print("  • Tilted players may quit mid-tournament")
            print("  • More likely after bad performances")

            print("\n🔙 ZERO BUILD FLASHBACK:")
            print("  • Players suddenly play like it's Zero Build")
            print("  • Temporary skill debuff")

            print("\n👀 STREAM SNIPED:")
            print("  • Players get targeted by stream snipers")
            print("  • Can ruin good tournament runs")

            print("\n💎 CLUTCH FACTOR:")
            print("  • 25% players are clutch (better under pressure)")
            print("  • 25% players are chokers (worse under pressure)")
            print("  • Pressure situations: top 15 alive, final 3 games")

            print("\n🌐 PING DIFF:")
            print("  • Some players get bad connection")
            print("  • Affects fight outcomes negatively")

            print("\nMods can be toggled in 'Mods & Extras' menu")

            input("\nPress Enter to continue...")

        elif choice == "5":
            print("\n" + "━" * 60)
            print("👤 PLAYER MECHANICS")
            print("━" * 60)

            print("\n🎯 SKILL (1-113):")
            print("  • Base fighting ability")
            print("  • ±5% variance each tournament")
            print("  • Top players: 105-113")
            print("  • Mid tier: 90-104")
            print("  • Lower tier: 75-89")

            print("\n😊 CONFIDENCE (-1.0 to 1.0):")
            print("  • Affected by placements each game")
            print("  • Top 5% finish: +confidence")
            print("  • Bottom 5% finish: -confidence")
            print("  • Boosts attack/defense when high")

            print("\n🎒 LOOT (0.0 to 1.0):")
            print("  • Gradually increases when not fighting")
            print("  • Lost when fighting, refreshed from kills")
            print("  • +15% attack, +12% defense at full loot")
            print("  • Contested drops = slower loot gain")

            print("\n🔥 RIVALRIES:")
            print("  • Build up from repeated eliminations")
            print("  • Emoting: +2.0 to +3.5 rivalry")
            print("  • Dying to worse player: +1.5 to +2.5")
            print("  • Crucial placement grief: +1.2 to +2.0")
            print("  • 5+ rivalry = toxic griefing starts")
            print("  • Killing rival = confidence boost")
            print("  • Dying to rival = confidence loss")
            print("  • Persists across tournaments in social_data.json")
            print("  • Decays by 25% each tournament if no new interactions")
            print("  • After 3-5 tournaments with no beef, rivalry fades completely")

            print("\n 🫂 FRIENDSHIPS:")
            print("  • Every player starts with 2-3 mutual friends")
            print("  • Friendship strength: 0.0 (broken) to 2.0 (best friends)")
            print("  • Grows: Both place well together, don't fight each other, loyalty")
            print("  • Decays: Killing friends, griefing in crucial moments, big placement gaps")
            print("  • Under 0.3 strength: friendship dissolved")
            print("  • 1.5+ strength: best friends")
            print("  • 1.0-1.5 strength: good friends")
            print("  • Under 1.0 strength: weakening")
            print("  • In crucial moments, with the tournament on the line, players will still target their friends")
            print("  • Persists across tournaments in social_data.json")

            print("\n🎭 ARCHETYPES:")
            print("  • Fragger: +20% attack")
            print("  • Aggressive: +35% attack, -10% defense")
            print("  • Passive: -20% attack, +10% defense")
            print("  • Strategist: Balanced, smart positioning")
            print("  • Rat: Avoids fights, survives longer")

            print("\n⚡ TOURNAMENT PRESSURE (Final 2-3 Games):")
            print("  • Players adjust strategy based on placement")
            print("  • 2nd place far behind 1st = grief mode")
            print("  • 1st place ahead = play defensive")
            print("  • Bubble players = desperate aggression")

            input("\nPress Enter to continue...")

        elif choice == "6":
            print("\n" + "━" * 60)
            print("📊 CAREER & SEASON STATS")
            print("━" * 60)

            print("\n🏆 CAREER STATS:")
            print("  • Persist across all seasons forever")
            print("  • Track tournament wins by type")
            print("  • Career earnings accumulate")
            print("  • Top 10 finishes saved as achievements")

            print("\n📈 GOAT INDEX:")
            print("  Career ranking formula:")
            print("  • LAN wins: 120 points each")
            print("  • FNCS wins: 90 points each")
            print("  • Elite Series wins: 25 points each")
            print("  • RELOAD wins: 18 points each")
            print("  • Cash Cup wins: 12 points each")
            print("  • Victory Cup wins: 8 points each")
            print("  • Top 10 finishes: 4 points each")
            print("  • Career earnings: 1 point per $100K")

            print("\n📆 SEASON STATS:")
            print("  • Reset every 16 tournaments")
            print("  • Track season champion and top performers")
            print("  • Season leaderboard for competitive rankings")

            print("\n💾 SAVE FILES:")
            print("  • Multiple saves = separate careers")
            print("  • Each save has isolated stats")
            print("  • Auto-backup after every tournament")
            print("  • Can restore from last 20 backups")

            print("\n🎯 CAREER HIGHLIGHTS:")
            print("  • Shows your best tournament finishes")
            print("  • Weighted by tournament prestige")
            print("  • LAN 1st > FNCS 1st > Elite 1st > etc.")

            input("\nPress Enter to continue...")

        else:
            print("❌ Invalid option")
            sim_sleep(0.5)


def main_menu():
    if not get_current_save() or get_current_save() == "":
        set_current_save("default")
        create_save("default")

    load_season()

    while True:
        print("\n" + "━" * 50)
        print(f"🏟️ FORTNITE TOURNAMENT SIM v{CONFIG['version']} ({CONFIG['build']})")
        print("━" * 50)
        splash = random.choice(load_splash_texts())
        print(Colors.SOFT_PURPLE + Colors.ITALIC + splash + Colors.RESET)
        print(f"\n📆 SEASON {SEASON['current_season']} - {CONFIG['region']}")
        print(f"💾 Save: {get_current_save()}")
        print(f"Tournaments Played: {SEASON['tournaments_played']} / {SEASON['tournaments_per_season']}")
        print_season_progress_bar()
        print("\n1. Start Tournament")
        print("2. Tournament Setup")
        print("3. View Season History")
        print("4. Tournament Templates")
        print("5. Mods & Extras")
        print("6. Save Management")
        print("7. How to Play")
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
            save_management_menu()

        elif choice == "7":
            how_to_play_guide()

        elif choice == "0":
            current_save = get_current_save()
            save_current_to_file(current_save)
            print(f"\n💾 Progress saved to: {current_save}")
            print("\nThanks for playing! See you next drop! 👋")
            exit()

        else:
            print("Invalid option.")


def pre_tournament_menu():
    while True:
        print("\n" + "━" * 45)
        print("🎮 TOURNAMENT CONFIG")
        print("━" * 45)

        print(f"1. PLAYERS:              [{CONFIG['players']}]")
        print(f"2. MATCHES:              [{CONFIG['matches']}]")
        print(f"3. STORM CIRCLES:        [{CONFIG['storm_circles']}]")
        print(f"4. ELIM POINTS:          [{CONFIG['elim_points']}]")
        t_type = CONFIG["tournament_type"]
        print(f"5. TOURNAMENT TYPE:      [{TOURNAMENT_TYPES[t_type]['label']}]")
        print(f"6. SPEED:                [{CONFIG['speed']}]")

        switching_status = "ON" if CONFIG.get("archetype_switching", True) else "OFF"
        print(f"7. ARCHETYPE SWITCHING:  [{switching_status}]")
        print(f"8. WALKOUTS:             [{'ON' if CONFIG.get('walkouts', False) else 'OFF'}]")

        print(f"9. REGION:               [{CONFIG.get('region', 'EU')}]")
        ticker_status = "ON" if CONFIG.get("show_win_tickers", True) else "OFF"
        print(f"10. WIN TICKERS:         [{ticker_status}]")
        print(f"11. KILLFEED HIGHLIGHTS: [{'ON' if CONFIG.get('killfeed_highlights', False) else 'OFF'}]")

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
            CONFIG["archetype_switching"] = not CONFIG.get("archetype_switching", True)
            status = "ON" if CONFIG["archetype_switching"] else "OFF"
            print(f"Archetype switching now {status}")
            save_config(CONFIG)
        elif choice == "8":
            CONFIG["walkouts"] = not CONFIG.get("walkouts", False)
            status = "ON" if CONFIG["walkouts"] else "OFF"
            print(f"Player walkouts before tournaments are now {status}")
            save_config(CONFIG)
        elif choice == "9":
            regions = list(PRO_PLAYER_POOLS.keys())
            region = CONFIG.get("region", "EU")
            current = regions.index(region)
            CONFIG["region"] = regions[(current + 1) % len(regions)]
            save_config(CONFIG)
            print(f"🌍 Region set to {CONFIG['region']}")
            print(f"⚠️ Please restart the simulator to apply changes properly!")
        elif choice == "10":
            CONFIG["show_win_tickers"] = not CONFIG.get("show_win_tickers", True)
            status = "ON" if CONFIG["show_win_tickers"] else "OFF"
            print(f"Win ticker now {status} (shows at halftime + before finals)")
            save_config(CONFIG)
        elif choice == "11":
            CONFIG["killfeed_highlights"] = not CONFIG.get("killfeed_highlights", True)
            status = "ON" if CONFIG["killfeed_highlights"] else "OFF"
            print(f"Killfeed Top 5 Highlights now {status} (gold glow for leaderboard climbers)")
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

        current_save = get_current_save()
        save_current_to_file(current_save)
        print(f"\n{Colors.SOFT_GREEN}💾 Progress auto-saved to: {current_save}{Colors.RESET}")