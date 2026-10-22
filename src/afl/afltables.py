"""Parse pages from AFL Tables (https://afltables.com). Pages are latin-1 encoded."""

from io import StringIO

import pandas as pd

from afl.fetch import fetch

BASE_URL = "https://afltables.com/afl/stats"


def season_games(year: int) -> pd.DataFrame:
    """Return games played by every player in one season, one row per player-team.

    Uses the season "Player Lists" page, which has one table per team.
    """
    html = fetch(f"{BASE_URL}/{year}.html", encoding="latin-1")
    if html is None:
        return pd.DataFrame()

    rows = []
    for table in pd.read_html(StringIO(html), extract_links="body"):
        # Team tables have a two-level header; the top level starts with the team name,
        # e.g. "Adelaide [Players Game by Game][Team Game by Game]".
        if not isinstance(table.columns, pd.MultiIndex):
            continue
        team = table.columns[0][0].split(" [")[0]
        table.columns = table.columns.get_level_values(1)

        for player_cell, games_cell in zip(table["Player"], table["GM"]):
            # Player rows are (text, link) pairs. The "37 players used" footer
            # spans the whole row, so it arrives as a plain string instead.
            if not isinstance(player_cell, tuple) or player_cell[1] is None:
                continue
            name, link = player_cell
            games = games_cell[0]
            surname, first_name = name.split(", ", 1)  # "Dawson, Jordan"
            rows.append({
                "season": year,
                "team": team,
                "player": f"{first_name} {surname}",
                # The player-page URL is AFL Tables' unique ID for a player
                "afltables_url": f"{BASE_URL}/{link}",
                "games": int(games),
            })
    return pd.DataFrame(rows)


def all_season_games(first_year: int, last_year: int) -> pd.DataFrame:
    """Stack season_games() for every season from first_year to last_year."""
    seasons = [season_games(year) for year in range(first_year, last_year + 1)]
    return pd.concat(seasons, ignore_index=True)
