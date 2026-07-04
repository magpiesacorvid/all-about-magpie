import json
import re
from pathlib import Path

data = json.loads(Path("stats.json").read_text())

# Icons shown either side of each game's heading
GAME_ICONS = {
    "Deadlock": "https://cdn.fastly.steamstatic.com/apps/deadlock/images/react/oldgods/rem_helper.png",
    "Overwatch": "https://cdn.betterttv.net/emote/698afc803df753bf3f83fcbd/3x.png",
}

# Colored/styled heading text for each game
GAME_HEADINGS = {
    "Deadlock": '<span style="color:#eedfbf">Deadlock</span>',
    "Overwatch": 'Ove<span style="color:#ef6414">rwa</span>tch',
}

# Heroes shown in a sub-table under each game, sorted by total games played
GAME_HEROES = {
    "Deadlock": ["Celeste", "Silver", "Paige", "Ivy"],
    "Overwatch": ["D.Va", "Lucio", "Freja", "Symmetra"],
}

# Portrait shown depending on whether the hero's win rate is
# above/at 50% ("gloat") or below 50% ("critical")
HERO_IMAGES = {
    "Celeste": {
        "gloat": "https://deadlock.wiki/images/7/70/Celeste_Gloat.png",
        "critical": "https://deadlock.wiki/images/4/41/Celeste_Critical_Health.png",
    },
    "Paige": {
        "gloat": "https://deadlock.wiki/images/9/9f/Paige_Gloat.png",
        "critical": "https://deadlock.wiki/images/0/02/Paige_Critical.png",
    },
    "Silver": {
        "gloat": "https://deadlock.wiki/images/4/44/Silver_Gloat_Portrait.png",
        "critical": "https://deadlock.wiki/images/8/8b/Silver_Critical_Health.png",
    },
    "Ivy": {
        "gloat": "https://deadlock.wiki/images/4/45/Ivy_Gloat_.png",
        "critical": "https://deadlock.wiki/images/3/37/Ivy_Critical_.png",
    },
    "D.Va": {
        "gloat": "https://cdn3.emoji.gg/emojis/5341-dvapeace.png",
        "critical": "https://cdn3.emoji.gg/emojis/2766-dvamad.png",
    },
    "Lucio": {
        "gloat": "https://cdn3.emoji.gg/emojis/8866-luciocool.png",
        "critical": "https://cdn.betterttv.net/emote/5bc3e33f555f4b166afde06d/3x.png",
    },
    "Freja": {
        "gloat": "https://i.pinimg.com/736x/31/33/7a/31337adb5d3962e15a2c2ad9fe3856dc.jpg",
        "critical": "https://i.pinimg.com/736x/3e/22/9f/3e229f35064784743b6a4442b75ebce1.jpg",
    },
    "Symmetra": {
        "gloat": "https://cdn3.emoji.gg/emojis/8861-symmetragiggle.png",
        "critical": "https://cdn3.emoji.gg/emojis/6694-symmetrasigh.png",
    },
}


def total_games(g):
    return g["wins"] + g["losses"]


def wr(g):
    t = total_games(g)
    return (g["wins"] / t * 100) if t else 0


def hero_image(hero, g):
    key = "gloat" if wr(g) >= 50 else "critical"
    return HERO_IMAGES[hero][key]


def game_section(name, g):
    icon = GAME_ICONS[name]
    heading = GAME_HEADINGS[name]

    heading_html = (
        f'<h3 align="center"><img src="{icon}" height="22" valign="middle"> '
        f'{heading} '
        f'<img src="{icon}" height="22" valign="middle"></h3>'
    )
    stats_html = (
        f'<p align="center">Wins: {g["wins"]}<br>'
        f'Losses: {g["losses"]}<br>'
        f'Win Rate: {wr(g):.1f}%</p>'
    )

    heroes_sorted = sorted(GAME_HEROES[name], key=lambda h: total_games(data[h]), reverse=True)

    header_cells = []
    image_cells = []
    stats_cells = []
    for hero in heroes_sorted:
        hg = data[hero]
        img = hero_image(hero, hg)
        header_cells.append(hero)
        image_cells.append(f'<img src="{img}" width="60">')
        stats_cells.append(f"{hg['wins']}W - {hg['losses']}L ({wr(hg):.1f}%)")

    table = (
        "| " + " | ".join(header_cells) + " |\n"
        "|" + "|".join([":---:"] * len(header_cells)) + "|\n"
        "| " + " | ".join(image_cells) + " |\n"
        "| " + " | ".join(stats_cells) + " |"
    )

    heroes_html = (
        '<h4 align="center">Heroes</h4>\n\n'
        '<div align="center" markdown="1" style="display:flex; justify-content:center;">\n\n'
        f"{table}\n\n"
        '</div>'
    )

    return f"{heading_html}\n\n{stats_html}\n\n{heroes_html}"


sections = [game_section("Deadlock", data["Deadlock"]), game_section("Overwatch", data["Overwatch"])]

stats_block = (
    '<h2 align="center">Game Stats</h2>\n\n'
    + "\n\n".join(sections)
    + "\n"
)

readme_path = Path("README.md")
readme = readme_path.read_text()

new_readme = re.sub(
    r"<!-- START_STATS -->.*?<!-- END_STATS -->",
    f"<!-- START_STATS -->\n\n{stats_block}\n<!-- END_STATS -->",
    readme,
    flags=re.DOTALL,
)

readme_path.write_text(new_readme)
