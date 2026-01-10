import json
import os
import random
import time
import datetime
from dataclasses import dataclass, field
from typing import List
from utils import display_name, ORG_TAGS
from mods import (
    TechnicalIssuesMod,
    ZeroBuildFlashbackMod,
    StreamSnipedMod,
    PingDiffMod
)

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

ACTIVE_MODS = [
    TechnicalIssuesMod(crash_chance=0.008, no_load_chance=0.012),
    ZeroBuildFlashbackMod(),
    StreamSnipedMod(),
    PingDiffMod(bad_ping_chance=0.22),
]

CAREER_FILE = "career_stats.json"
SEASON_FILE = "season_data.json"
SPLASH_FILE = "splash.txt"
SEASON = {
    "current_season": 1,
    "tournaments_played": 0,
    "tournaments_per_season": 12,
    "season_players": {},
    "history": []
}

def load_splash_texts():
    try:
        with open(SPLASH_FILE, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        return lines if lines else ["Welcome to the chaos..."]
    except FileNotFoundError:
        return ["No splash.txt found... dropping in silence"]
    except Exception:
        return ["Error loading splashes... pretend this is funny"]

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------

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
    "version": "1.1.1",
    "build": "Stable", # or "Experimental"
}


random.seed(CONFIG["random_seed"])

def sim_sleep(seconds):
    if CONFIG["speed"] == "INSTANT":
        return
    elif CONFIG["speed"] == "FAST":
        time.sleep(seconds * 0.65)
    elif CONFIG["speed"] == "SLOW":
        time.sleep(seconds * 1.35)
    else:  # NORMAL
        time.sleep(seconds)


pro_players_skills = [
    ("Swizzy", 110, "Fragger", "Free Agent"),
    ("Merstach", 109, "Fragger", "Gentle Mates"),
    ("Vico", 108, "Fragger", "BIG"),
    ("Wox", 107, "Strategist", "HavoK"),
    ("Pixie", 106, "Fragger", "HavoK"),
    ("MariusCOW", 105, "Aggressive", "Gentle Mates"),
    ("Tjino", 110, "Aggressive", "HavoK"),
    ("PabloWingu", 109, "Aggressive", "HavoK"),
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
    ("t3eny", 109, "Aggressive", "Free Agent"),
    ("Trulex", 98, "Strategist", "Free Agent"),
    ("Tayson", 97, "Strategist", "Falcons"),
    ("IDrop", 96, "Fragger", "HavoK"),
    ("Rezon", 95, "Fragger", "Wave"),
    ("Setty", 99, "Passive", "Free Agent"),
    ("Panzer", 98, "Strategist", "Free Agent"),
    ("Vadeal", 87, "Passive", "Wave"),
    ("Focus", 86, "Fragger", "Free Agent"),
    ("Akiira", 85, "Fragger", "Gentle Mates"),
    ("Rax", 84, "Fragger", "Free Agent"),
    ("Kurama", 89, "Fragger", "Solary"),
    ("Werex", 88, "Strategist", "Lyost"),
    ("Seyyto", 87, "Strategist", "Free Agent"),
    ("Kiro", 86, "Strategist", "Free Agent"),
    ("Podasai", 85, "Strategist", "Free Agent"),
    ("Momsy", 89, "Strategist", "Free Agent"),
    ("Pixx", 88, "Passive", "HavoK"),
    ("Demus", 87, "Fragger", "Free Agent"),
    ("Darm", 85, "Fragger", "BIG"),
    ("Sangild", 85, "Strategist", "Free Agent"),
    ("Huty", 84, "Strategist", "The One"),
    ("F1shyX", 83, "Strategist", "Free Agent"),
    ("Mappi", 83, "Strategist", "Free Agent"),
    ("Moneymaker", 82, "Fragger", "Free Agent"),
    ("Mongraal", 81, "Aggressive", "Free Agent"),
    ("Wheat", 80, "Strategist", "Free Agent"),
    ("NeFrizi", 79, "Strategist", "Detect"),
    ("Twi", 78, "Aggressive", "Free Agent"),
    ("SkyJump", 77, "Fragger", "Solary"),
    ("Mikson", 76, "Fragger", "Free Agent"),
    ("Upl", 75, "Fragger", "Free Agent"),
    ("Kombek", 74, "Fragger", "Free Agent"),
    ("Blacha", 73, "Passive", "Free Agent"),
    ("Hris", 72, "Fragger", "Free Agent"),
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
    ("Franek", 80, "Aggressive", "Free Agent"),
    ("Asa", 80, "Passive", "Free Agent"),
    ("Belusi", 79, "Fragger", "Free Agent"),
    ("Refsgaard", 78, "Strategist", "Free Agent"),
    ("Nxthan", 77, "Fragger", "HavoK"),
    ("Juu", 76, "Strategist", "FataL"),
]

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
        "tournament_type": "CASH_CUP"
    },
    "FNCS": {
        "label": "FNCS GRAND FINALS",
        "players": 100,
        "matches": 12,
        "storm_circles": 12,
        "elim_points": 3,
        "tournament_type": "FNCS"
    },
    "LAN": {
        "label": "LAN EVENT",
        "players": 100,
        "matches": 12,
        "storm_circles": 12,
        "elim_points": 4,
        "tournament_type": "LAN"
    },
    "VICTORY_CUP": {
        "label": "VICTORY CUP",
        "players": 100,
        "matches": 4,
        "storm_circles": 12,
        "elim_points": 0,
        "tournament_type": "VICTORY_CUP"
    }
}

def apply_tournament_template(key):
    template = TOURNAMENT_TEMPLATES[key]

    CONFIG["players"] = template["players"]
    CONFIG["matches"] = template["matches"]
    CONFIG["storm_circles"] = template["storm_circles"]
    CONFIG["elim_points"] = template["elim_points"]
    CONFIG["tournament_type"] = template["tournament_type"]

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

previous_top10 = []


def print_top10_cumulative(players: List[Player]):
    global previous_top10

    top10_cumulative = sorted(
        players,
        key=lambda p: (
            p.total_points,
            p.wins,
            p.average_elims,
            -p.average_placement
        ),
        reverse=True
    )[:10]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 CURRENT TOP 10 STANDINGS 📊")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")

    for rank, p in enumerate(top10_cumulative, 1):
        # Determine previous rank movement
        prev_rank = None
        for idx, prev_p in enumerate(previous_top10, 1):
            if prev_p.name == p.name:
                prev_rank = idx
                break

        if prev_rank is None:
            movement = "🆕"
        elif prev_rank > rank:
            diff = prev_rank - rank
            movement = f"{Colors.SOFT_GREEN}↑{diff}{Colors.RESET}"
        elif prev_rank < rank:
            diff = rank - prev_rank
            movement = f"{Colors.SOFT_RED}↓{diff}{Colors.RESET}"
        else:
            movement = f"{Colors.LIGHT_GRAY}→{Colors.RESET}"

        # Top 3 medals
        if rank == 1:
            medal = " 🥇"
        elif rank == 2:
            medal = " 🥈"
        elif rank == 3:
            medal = " 🥉"
        else:
            medal = f"{rank:>2}."

        # Points bar (scaled, max width 20)
        bar_length = min(10, p.total_points // 50)
        points_bar = "█" * bar_length

        print(
            f"{medal} {p.name:<15} | Points: {p.total_points:<4} [{points_bar:<10}] "
            f"| Elims: {p.total_elims:<2} 🗡️ | Wins: {p.wins:<2} ⭐ | {movement}"
        )

    previous_top10 = top10_cumulative.copy()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━")
    sim_sleep(2)


def get_victory_commentary(winner, match_number: int, total_matches: int):
    wins = winner.wins
    prev_wins = getattr(winner, "previous_wins", wins - 1)

    commentary = []

    # --------------------------------------------------
    # FIRST EVER WIN
    # --------------------------------------------------
    if wins == 1:

        if match_number == 1:
            commentary = [
                "Opens the tournament with a massive statement.",
                "First game. First win. You couldn’t script it better.",
                "Starts the day absolutely on fire.",
                "Sets the tone early — this lobby has been warned.",
                "Game 1 and already making noise.",
                "That is how you announce yourself.",
                "What a way to start the tournament.",
                "Opens the tournament with a statement win.",
                f"Coming in hot! {winner.name} steals a win in the first game.",
            ]

        elif match_number == total_matches:
            commentary = [
                "Leaves it until the final game — and delivers.",
                "First win in the LAST possible moment.",
                "When it mattered most, they showed up.",
                "Clutch factor through the roof in the final game.",
                "That win changes everything.",
                "Ice in the veins — unbelievable timing.",
                "Leaves it late — but still gets it done.",
                "First win, last chance. Ice cold.",
            ]

        else:
            commentary = [
                "Finally breaks through with their first win.",
                "That pressure has been building all tournament.",
                "They’ve been knocking on the door — now it’s kicked in.",
                "Persistence pays off in a big way.",
                "That win was overdue.",
                "Momentum might just be shifting.",
                "Gets the monkey off their back.",
            ]


    elif wins >= 2 and prev_wins == wins - 1:

        if wins == 2:
            commentary = [
                "Back-to-back wins to start the tournament.",
                "Two games. Two victories. Unreal pace.",
                "No cooldown between wins — straight dominance.",
                "They’re setting the bar ridiculously high.",
                "This could get scary if it continues.",
                "The rest of the lobby is already chasing.",
                "Wins the first two games — unreal pace.",
                "Nobody is slowing them down right now.",
            ]

        elif wins == 3:
            commentary = [
                "That’s three wins in a row.",
                "Absolute control of the tournament.",
                "This is starting to feel inevitable.",
                "Nobody has an answer right now.",
                "They’re playing a different game.",
                "Pure dominance from start to finish.",
                "This is turning into a solo highlight reel.",
            ]

        else:  # 4+ win streak
            commentary = [
                f"{wins} wins in a row — this is unreal.",
                "This is turning into a solo highlight reel.",
                "The lobby belongs to them right now.",
                "Every fight feels unfair.",
                "They are dictating the entire tournament.",
                "This is historic-level dominance."
            ]

    else:

        if match_number == total_matches:
            commentary = [
                "Closes out the tournament with a huge win.",
                "Ends the day exactly how they wanted.",
                "That’s a perfect way to finish.",
                "Final game, final statement.",
                "They saved something special for the end.",
                "That win will be remembered."
            ]

        else:
            commentary = [
                f"That’s win number {wins} of the tournament.",
                "Keeps themselves firmly in the title race.",
                "Another crucial Victory Royale.",
                "They stay right in the mix.",
                "That win could be massive for the standings.",
                "Consistency like this wins tournaments."
            ]

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

    update_confidence(players)
    print_top10_cumulative(players)
    sim_sleep(1)
    print(f"Match {match_number} complete! ✅")
    print("━" * 40)
    sim_sleep(1)


def simulate_tournament():
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
    print("\n" + "━"*60)
    print(" FINAL FORTNITE TOURNAMENT LEADERBOARD")
    print("━"*60)
    print(f"{'Rank':<6}{'Player':<15}{'Points':<10}{'Elims':<10}{'Wins':<6}{'Avg Place'}")
    print("━"*60)
    for rank, p in enumerate(players, 1):
        print(
            f"{rank:<6}{p.name:<16}{p.total_points:<10}{p.total_elims:<10}"
            f"{p.wins:<6}{p.average_placement:.2f} +${p.tournament_earnings:,}"
        )
    print("━"*60)

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
    print("\n" + "━" * 60)
    print(f"🏁 SEASON {SEASON['current_season']} COMPLETE")
    print("━" * 60)
    print(f"👑 MVP: {champion}")
    print(f"⭐ Earnings: ${stats['earnings']:,} | Points: {stats['points']} | Wins: {stats['wins']} | Elims: {stats['elims']}")
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
            "\nEnter a placement number, player name, org name, or 'career' for career leaderboard, or 'q' to quit: "
        )
        if user_input.lower() == 'q':
            break


        if user_input.lower() == "career":
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
                print(f"\n{'Rank':<6}{'Org':<20}{'Total Earnings'}")
                print("━"*50)
                for rank, (org_name, earnings) in enumerate(sorted_orgs, 1):
                    print(f"{rank:<6}{org_name:<20}${earnings:,}")
                print("━"*50)
                continue

            if sort_option == "earnings":
                career_players.sort(key=lambda p: p.career_earnings, reverse=True)
            elif sort_option == "kills":
                career_players.sort(key=lambda p: p.career_kills, reverse=True)
            elif sort_option == "wins":
                career_players.sort(key=lambda p: p.career_wins, reverse=True)
            elif sort_option == "tournaments":
                career_players.sort(key=lambda p: p.career_tournaments, reverse=True)

            print(f"\n{'Rank':<6}{'Player':<15}{'Wins':<6}{'Tournaments':<12}{'Kills':<8}{'Earnings'}")
            print("━"*60)
            for rank, p in enumerate(career_players, 1):
                print(f"{rank:<6}{p.name:<16}{p.career_wins:<6}{p.career_tournaments:<12}{p.career_kills:<8}${p.career_earnings:,}")
            print("━"*60)
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
            if user_input.lower() in org_names:
                show_org_page(user_input, sorted_players)
                continue

            matches = [p for p in sorted_players if user_input.lower() in p.name.lower()]
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


        rank = sorted_players.index(player) + 1
        print(f"\n{player.name}")
        print(f"{player.org}")
        print(f"Ranking: #{rank}")
        print(f"Total Points: {player.total_points}")
        print(f"Total Kills: {player.total_elims}")
        print(f"Total Wins: {player.wins}\n")
        print(f"{'MATCH':<8}{'PLACEMENT':<12}{'KILLS'}")
        print("━"*30)
        for idx, (placement, kills) in enumerate(zip(player.placements, player.match_kills), 1):
            print(f"{idx:<8}{placement:<12}{kills}")
        print("━"*30)


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
    filename = f"tournament_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Fortnite Tournament Results ({matches} Matches)\n")
        f.write("="*50+"\n\n")

        for match_num in range(1, matches+1):
            match_winners = [p for p in players if p.placements[match_num-1] == 1]
            winner_name = match_winners[0].name if match_winners else "Unknown"
            f.write(f"Game {match_num}: {winner_name} (Winner)\n")
        t_type = CONFIG["tournament_type"]
        t_label = TOURNAMENT_TYPES[t_type]["label"]

        f.write(f"\nFinal Leaderboard ({t_label})\n")
        f.write("="*50+"\n")
        f.write(f"{'Rank':<6}{'Player':<15}{'Points':<10}{'Elims':<10}{'Wins':<6}{'Avg Place'}\n")
        f.write("-"*50+"\n")

        sorted_players = sorted(
            players,
            key=lambda p: (p.total_points, p.wins, p.total_elims, -p.average_placement),
            reverse=True
        )

        for rank, p in enumerate(sorted_players, 1):
            f.write(f"{rank:<6}{p.name:<15}{p.total_points:<10}{p.total_elims:<10}{p.wins:<6}{p.average_placement:.2f}\n")

        f.write("="*50+"\n")

    print(f"Tournament results exported to {filename}")
    

def cycle_tournament_type():
    keys = list(TOURNAMENT_TYPES.keys())
    current = CONFIG["tournament_type"]
    idx = keys.index(current)
    CONFIG["tournament_type"] = keys[(idx + 1) % len(keys)]
    
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


def main_menu():
    load_season()
    
    while True:
        print("\n" + "━" * 50)
        print(f"🏟️ FORTNITE TOURNAMENT SIM v{CONFIG['version']} ({CONFIG['build']})")   
        print("━" * 50)
        splash = random.choice(load_splash_texts())
        print(Colors.SOFT_PURPLE + Colors.ITALIC + splash + Colors.RESET)  
        print(f"\n📆 SEASON {SEASON['current_season']}")
        print(f"Tournaments Played: {SEASON['tournaments_played']} / {SEASON['tournaments_per_season']}")
        
        print("\n1. Start Tournament")
        print("2. Tournament Setup")
        print("3. View Season History")
        print("4. Tournament Templates")
        print("5. Mods & Extras")
        print("6. Patch Notes")
        print("7. Exit")
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
                    print("All mods have been reset to OFF.")
                    sim_sleep(1)
                    
                elif mod_choice.startswith("t "):
                    try:
                        idx = int(mod_choice.split()[1]) - 1
                        if 0 <= idx < len(ACTIVE_MODS):
                            mod = ACTIVE_MODS[idx]
                            mod.enabled = not mod.enabled
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
        
        elif choice == "7":
            print("\nThanks for playing! See you next drop! 👋")
            exit()
            
        else:
            print("Invalid option.")


def show_patch_notes():
    print("\n" + "═" * 60)
    print("📜  PATCH NOTES  –  Fortnite Tournament Simulator")
    print("═" * 60)
    print("Last updated: January 10, 2026")
    print("")
    
    print("v1.1.1 Hotfix (January 10, 2026)")
    print("──────────────────────────────────────")
    print("• Fixed bug where crashed/no-loaded players would receive high placements")
    print("• Added new splash texts")
    print("• Added new splash texts")
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
        print("🎮 TOURNAMENT SETUP")
        print("━" * 45)
        print(f"1. PLAYERS:         [{CONFIG['players']}]")
        print(f"2. MATCHES:         [{CONFIG['matches']}]")
        print(f"3. STORM CIRCLES:   [{CONFIG['storm_circles']}]")
        print(f"4. ELIM POINTS:     [{CONFIG['elim_points']}]")

        t_type = CONFIG["tournament_type"]
        t_label = TOURNAMENT_TYPES[t_type]["label"]
        print(f"5. TOURNAMENT TYPE: [{t_label}]")

        print(f"6. SPEED:           [{CONFIG['speed']}]")
        print("\nType a number to change it, or 'B' to return to main menu")
        print("━" * 45)

        choice = input("> ").strip().lower()

        if choice == "b":
            return

        elif choice == "1":
            val = input("Enter number of players: ").strip()
            if val.isdigit():
                CONFIG["players"] = int(val)
                if CONFIG["players"] > 100:
                    print("⚠️  100+ players is not recommended (performance & pacing)")
                if CONFIG["players"] < 20:
                    print("⚠️  Very low player counts may feel unrealistic")

        elif choice == "2":
            val = input("Enter number of matches: ").strip()
            if val.isdigit():
                CONFIG["matches"] = int(val)
                if CONFIG["matches"] > 20:
                    print("⚠️  Long tournaments heavily favor consistency")
                if CONFIG["matches"] < 5:
                    print("⚠️  Short formats create extreme RNG")

        elif choice == "3":
            val = input("Enter storm circles: ").strip()
            if val.isdigit():
                CONFIG["storm_circles"] = int(val)
                if CONFIG["storm_circles"] < 5:
                    print("⚠️  Fewer circles = faster, bloodier games")
                if CONFIG["storm_circles"] > 12:
                    print("⚠️  Too many circles can stall the midgame")

        elif choice == "4":
            val = input("Enter elim points: ").strip()
            if val.isdigit():
                CONFIG["elim_points"] = int(val)
                if CONFIG["elim_points"] >= 5:
                    print("⚠️  High elim points strongly reward aggression")
                if CONFIG["elim_points"] == 0:
                    print("⚠️  No elim points = pure placement meta")

        elif choice == "5":
            cycle_tournament_type()
            t = CONFIG["tournament_type"]
            print(f"🏆 Tournament set to {TOURNAMENT_TYPES[t]['label']}")

        elif choice == "6":
            speeds = ["SLOW", "NORMAL", "FAST", "INSTANT"]
            current = speeds.index(CONFIG["speed"])
            CONFIG["speed"] = speeds[(current + 1) % len(speeds)]
            if CONFIG["speed"] == "FAST":
                print("⚠️  FAST mode reduces dramatic pauses")
            if CONFIG["speed"] == "INSTANT":
                print("⚠️  INSTANT mode removes all cinematic viewing")

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

