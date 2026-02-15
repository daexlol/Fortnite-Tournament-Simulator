if __name__ == "__main__":
    raise RuntimeError("mods.py should not be run directly!")

import random
from utils import display_name, Colors, sim_sleep, CONFIG


class Mod:
    name = "BaseMod"
    enabled = False

    def on_tournament_start(self, players, config):
        pass

    def on_match_start(self, players, match_number, config):
        pass

    def on_player_spawn(self, player, match_number, config):
        pass

    def on_fight(self, attacker, defender, config):
        return True

    def on_player_eliminated(self, victim, killer, config):
        pass


class TechnicalIssuesMod(Mod):
    name = "Technical Issues"

    def __init__(self, crash_chance=0.008, no_load_chance=0.012):
        self.crash_chance = crash_chance
        self.no_load_chance = no_load_chance

    def on_player_spawn(self, player, match_number, config):
        if not self.enabled:
            return None
        if random.random() < self.no_load_chance:
            player.alive = False
            return "NO_LOAD"
        if random.random() < self.crash_chance:
            player.alive = False
            return "CRASH"
        return None


class RageQuitMod(Mod):
    name = "Rage Quit"
    description = "Players tilt hard and bail on the rest of the tournament"

    def __init__(self, tilt_threshold=5, rage_chance_base=0.08):
        self.tilt_threshold = tilt_threshold
        self.rage_chance_base = rage_chance_base
        self.player_bad_streaks = {}

    def on_match_end(self, players, winner, config):
        if not self.enabled:
            return

        leaderboard = sorted(players, key=lambda p: p.total_points, reverse=True)
        for rank, p in enumerate(leaderboard, 1):
            badness = 0
            if rank > len(players) * 0.75:
                badness += 2
            if p.total_elims < 1:
                badness += 2
            if p.placements and p.placements[-1] > 80:
                badness += 2

            streak = self.player_bad_streaks.setdefault(p.id, [])
            streak.append(badness)
            streak[:] = streak[-7:]

            avg_bad = sum(streak) / len(streak) if streak else 0
            if avg_bad >= self.tilt_threshold and not getattr(p, '_has_rage_quit', False):
                chance = min(0.35, self.rage_chance_base * (avg_bad - self.tilt_threshold + 1))
                if random.random() < chance:
                    print(f"{Colors.SOFT_RED + Colors.BOLD}😡 {display_name(p)} RAGE QUIT the tournament!{Colors.RESET}")
                    print(f"   └─ Tilted after {len(streak)} bad games (avg: {avg_bad:.1f})")
                    sim_sleep(1.5)
                    p._has_rage_quit = True

                    remaining_games = CONFIG["matches"] - len(p.placements)


class ZeroBuildFlashbackMod(Mod):
    name = "Zero Build Flashback"

    def on_fight(self, attacker, defender, config):
        if not self.enabled:
            return True
        if random.random() < 0.03:
            print(f"🌀 {attacker.name} is having Zero Build flashbacks! No build fight!")
            attacker.skill = max(1, attacker.skill * 0.65)
            defender.skill = min(200, defender.skill * 1.15)
        return True


class StreamSnipedMod(Mod):
    name = "Stream Snipe"

    def on_player_eliminated(self, victim, killer, config):
        if not self.enabled:
            return
        if victim.skill >= 100 and random.random() < 0.08:
            print(f"🎥 {victim.name} just got STREAM-SNIPED by {killer.name}!")
            killer.confidence += 0.25
            victim.confidence -= 0.35


class PingDiffMod(Mod):
    name = "Ping Difference"

    def __init__(self, bad_ping_chance=0.22):
        self.bad_ping_chance = bad_ping_chance

    def on_fight(self, attacker, defender, config):
        if not self.enabled:
            return True

        for p in [attacker, defender]:
            if random.random() < self.bad_ping_chance:
                if random.random() < 0.5:
                    p.skill = max(1, p.skill * 0.70)
                else:
                    p.skill = min(200, p.skill * 1.18)
        return True


class ClutchFactorMod(Mod):
    name = "Clutch Factor"
    description = "Players either rise to pressure or completely fold"

    def __init__(self):
        self.player_clutch_genes = {}
        self.current_match = 0
        self.alive_tracking = {}

    def on_tournament_start(self, players, config):
        if not self.enabled:
            return
        clutch_count = 0
        choke_count = 0
        for p in players:
            if p.id not in self.player_clutch_genes:
                roll = random.random()
                if roll < 0.25:
                    self.player_clutch_genes[p.id] = "CLUTCH"
                    clutch_count += 1
                elif roll < 0.50:
                    self.player_clutch_genes[p.id] = "CHOKER"
                    choke_count += 1
                else:
                    self.player_clutch_genes[p.id] = "NORMAL"

        print(
            f"{Colors.SOFT_CYAN}🎲 Clutch Factor initialized: {clutch_count} clutch players, {choke_count} chokers{Colors.RESET}")
        sim_sleep(1)

    def on_match_start(self, players, match_number, config):
        if not self.enabled:
            return
        self.current_match = match_number
        self.alive_tracking = {p.id: True for p in players if p.alive}

    def on_fight(self, attacker, defender, config):
        if not self.enabled:
            return True

        alive_count = len(self.alive_tracking)
        total_matches = config.get("matches", 12)

        for p in [attacker, defender]:
            gene = self.player_clutch_genes.get(p.id, "NORMAL")

            if gene == "NORMAL":
                continue

            is_pressure = False
            pressure_type = ""

            if alive_count <= 15 and alive_count > 1:
                is_pressure = True
                pressure_type = "ENDGAME"

            if self.current_match >= total_matches - 2:
                is_pressure = True
                pressure_type = "FINALS"

            if is_pressure and random.random() < 0.25:
                if gene == "CLUTCH":
                    p.skill = min(200, p.skill * 1.30)
                    p.confidence = min(2.0, p.confidence * 1.12)
                    if random.random() < 0.2:
                        print(
                            f"{Colors.SOFT_GREEN + Colors.BOLD}💎 {display_name(p)} is LOCKED IN! ({pressure_type}){Colors.RESET}")
                        sim_sleep(0.25)

                elif gene == "CHOKER":
                    p.skill = max(1, p.skill * 0.68)
                    p.confidence = max(0.1, p.confidence * 0.82)
                    if random.random() < 0.2:
                        print(
                            f"{Colors.SOFT_RED}😰 {display_name(p)} is feeling the pressure... ({pressure_type}){Colors.RESET}")
                        sim_sleep(0.25)

        return True

    def on_player_eliminated(self, victim, killer, config):
        if not self.enabled:
            return

        if victim.id in self.alive_tracking:
            del self.alive_tracking[victim.id]

        alive_count = len(self.alive_tracking)
        gene = self.player_clutch_genes.get(killer.id, "NORMAL")

        if alive_count <= 10 and alive_count > 1 and gene == "CLUTCH" and random.random() < 0.15:
            print(
                f"{Colors.GOLD + Colors.BOLD}⭐ {display_name(killer)} with the CLUTCH ELIM! (Top {alive_count}){Colors.RESET}")
            killer.confidence = min(2.0, killer.confidence * 1.18)
            sim_sleep(0.25)