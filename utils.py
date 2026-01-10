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
}

def display_name(player):
    if player.org == "Free Agent":
        return player.name

    tag = ORG_TAGS.get(player.org)
    if not tag:
        return player.name  # fallback safety

    return f"{tag} {player.name}"
