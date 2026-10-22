"""Parse draft-year pages from DraftGuru (https://www.draftguru.com.au)."""

import re
from io import StringIO

import pandas as pd

from afl.fetch import fetch

BASE_URL = "https://www.draftguru.com.au"


def parse_games(text: str) -> tuple[int, int] | tuple[None, None]:
    """Split DraftGuru's games text into (career games, games for drafting club).

    "76 (27)" means 76 career games, 27 of them for the drafting club.
    "218" (no brackets) means every game was for the drafting club.
    """
    match = re.fullmatch(r"(\d+)(?:\s*\((\d+)\))?", text.strip())
    if match is None:
        return None, None
    career = int(match.group(1))
    for_club = int(match.group(2)) if match.group(2) else career
    return career, for_club


def national_picks(year: int) -> pd.DataFrame:
    """Return one row per national draft pick made in `year`."""
    html = fetch(f"{BASE_URL}/years/{year}")
    if html is None:
        return pd.DataFrame()

    # extract_links="body" turns every cell into a (text, link) pair,
    # which gives us each player's DraftGuru URL alongside their name.
    table = pd.read_html(StringIO(html), extract_links="body")[0]
    table.columns = [col.replace("↧", "").strip() for col in table.columns]

    def text(column):
        # Swap non-breaking spaces (\xa0) for normal spaces
        return table[column].map(lambda cell: (cell[0] or "").replace("\xa0", " ").strip())

    games = text("Games").map(parse_games)
    picks = pd.DataFrame({
        "draft_year": year,
        "draft": text("Draft"),
        "pick": pd.to_numeric(text("#"), errors="coerce"),
        "club": text("Club"),
        "player": text("Player"),
        "draftguru_url": BASE_URL + table["Player"].map(lambda cell: cell[1] or ""),
        "pick_note": text("Pick"),  # e.g. "Priority (Carlton)", "Compensation (...)"
        "signing": text("Signing"),  # e.g. "Academy (Sydney)", "Father-Son (...)"
        "career_games": games.map(lambda g: g[0]),
        "games_for_drafting_club": games.map(lambda g: g[1]),
    })

    picks = picks[picks["draft"] == "National"].drop(columns="draft")
    picks["pick"] = picks["pick"].astype(int)
    return picks.reset_index(drop=True)
