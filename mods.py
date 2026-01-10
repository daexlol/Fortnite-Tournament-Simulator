if __name__ == "__main__":
    raise RuntimeError("mods.py should not be run directly!")

import random
from utils import display_name

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
        return True  # allow fight by default

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
                    print(f"📡 {p.name} is teleporting (bad ping disadvantage)!")
                    p.skill = max(1, p.skill * 0.70)
                else:
                    print(f"📡 {p.name} has god-ping this fight!")
                    p.skill = min(200, p.skill * 1.18)
        return True
