"""Parse draft-year pages from DraftGuru (https://www.draftguru.com.au)."""

import re
from io import StringIO

import pandas as pd

from afl.fetch import fetch

BASE_URL = "https://www.draftguru.com.au"


def parse_games(text: str) -> tuple[int, int] | tuple[None, None]:
    """Split DraftGuru's games text into (games after draft, games for drafting club).

    "76 (27)" means 76 games after this draft selection, 27 of them for the
    drafting club. "218" (no brackets) means every game was for the drafting club.

    Note these are games *after* the selection, not lifetime career games: for a
    recycled player re-drafted later in their career, earlier games aren't counted.
    (Checked against AFL Tables: all 898 matched picks agree on this basis.)
    """
    match = re.fullmatch(r"(\d+)(?:\s*\((\d+)\))?", text.strip())
    if match is None:
        return None, None
    after_draft = int(match.group(1))
    for_club = int(match.group(2)) if match.group(2) else after_draft
    return after_draft, for_club


def year_movements(year: int) -> pd.DataFrame:
    """Every player movement DraftGuru lists for `year`, one row each.

    `draft` says what kind: "National", "Rookie", "Mid-Season", "Pre-Season",
    "Pre-Draft", "Post-Draft", "Trade" or "Free Agency". For trades and free
    agency, `club` is the club the player moved to, and `pick` is empty.
    """
    html = fetch(f"{BASE_URL}/years/{year}")
    if html is None:
        return pd.DataFrame()

    # extract_links="body" turns every cell into a (text, link) pair,
    # which gives us each player's DraftGuru URL alongside their name.
    table = pd.read_html(StringIO(html), extract_links="body")[0]
    table.columns = [col.replace("↧", "").strip() for col in table.columns]

    def text(column):
        # Swap non-breaking spaces (\xa0) for normal spaces, and drop zero-width spaces
        return table[column].map(
            lambda cell: (cell[0] or "").replace("\xa0", " ").replace("​", "").strip())

    games = text("Games").map(parse_games)
    moves = pd.DataFrame({
        "draft_year": year,
        "draft": text("Draft"),
        "pick": pd.to_numeric(text("#"), errors="coerce"),
        "club": text("Club"),
        "player": text("Player"),
        "draftguru_url": BASE_URL + table["Player"].map(lambda cell: cell[1] or ""),
        "pick_note": text("Pick"),  # e.g. "Priority (Carlton)", "Compensation (...)"
        "signing": text("Signing"),  # e.g. "Academy (Sydney)", "Father-Son (...)"
        "height_cm": pd.to_numeric(text("Height").str.replace("cm", ""), errors="coerce"),
        # e.g. "Drysdale/Christian College Geelong/Geelong U18": local club, school, U18 club
        "pathway": text("Original Club"),
        "games_after_draft": games.map(lambda g: g[0]),
        "games_for_drafting_club": games.map(lambda g: g[1]),
    })

    # The last club in the pathway, e.g. "Geelong U18" or a state-league club
    moves["pathway_club"] = moves["pathway"].str.split("/").str[-1].str.strip()
    return moves


def national_picks(year: int) -> pd.DataFrame:
    """Return one row per national draft pick made in `year`."""
    moves = year_movements(year)
    if moves.empty:
        return moves
    picks = moves[moves["draft"] == "National"].drop(columns="draft")
    picks["pick"] = picks["pick"].astype(int)
    return picks.reset_index(drop=True)


def birth_dates() -> pd.DataFrame:
    """Date of birth for every player DraftGuru lists, from its 12 birth-month pages.

    Returns columns draftguru_url and dob. The URLs match those from
    national_picks(), so the two join exactly without name matching.
    """
    months = []
    for month in range(1, 13):
        html = fetch(f"{BASE_URL}/birth-months/{month}")
        if html is None:
            continue
        table = pd.read_html(StringIO(html), extract_links="body")[0]
        # The first column is headed "Birth Month" but holds the player's name and link
        months.append(pd.DataFrame({
            "draftguru_url": BASE_URL + table["Birth Month"].map(lambda cell: cell[1] or ""),
            "dob": pd.to_datetime(table["DOB"].map(lambda cell: cell[0]), errors="coerce"),
        }))
    return pd.concat(months, ignore_index=True)
