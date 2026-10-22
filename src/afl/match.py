"""Match DraftGuru draft picks to AFL Tables players by name.

Names are compared after normalising (lowercase, no accents or punctuation).
Nothing is guessed: picks that can't be matched to exactly one player are
labelled "unmatched" or "ambiguous" so they can be reviewed by hand.
"""

import difflib
import re
import unicodedata

import pandas as pd

# AFL Tables team names -> DraftGuru club names, where they differ
TEAM_NAMES = {
    "Brisbane Lions": "Brisbane",
    "Greater Western Sydney": "GWS",
    "Kangaroos": "North Melbourne",
}


def normalise_name(name: str) -> str:
    """'Brock O'Brien' -> 'brock obrien'; 'Alex Neal-Bullen' -> 'alex neal bullen'."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.lower().replace("-", " ")
    name = re.sub(r"[^a-z ]", "", name)
    return " ".join(name.split())


def match_picks(picks: pd.DataFrame, seasons: pd.DataFrame) -> pd.DataFrame:
    """Add AFL Tables columns to `picks`.

    picks:   output of draftguru.national_picks()
    seasons: output of afltables.all_season_games()

    Adds: match_status, afltables_url, afltables_games (all games in `seasons`)
    and afltables_games_after_draft (games in seasons after the draft year).
    """
    seasons = seasons.assign(
        team=seasons["team"].replace(TEAM_NAMES),
        name_key=seasons["player"].map(normalise_name),
    )
    # One row per AFL Tables player: name, career span and clubs played for
    players = seasons.groupby("afltables_url").agg(
        name_key=("name_key", "first"),
        last_season=("season", "max"),
        clubs=("team", set),
    )

    results = []
    for pick in picks.itertuples():
        candidates = players[
            (players["name_key"] == normalise_name(pick.player))
            # Drafted in Nov/Dec, so the first possible season is the next year
            & (players["last_season"] > pick.draft_year)
        ]
        status = "name"
        if len(candidates) > 1:
            candidates = candidates[candidates["clubs"].map(lambda clubs: pick.club in clubs)]
            status = "name + club"

        if len(candidates) == 1:
            url = candidates.index[0]
        else:
            url = None
            if len(candidates) > 1 or status == "name + club":
                status = "ambiguous"
            elif pick.games_after_draft == 0:
                status = "never played"  # AFL Tables only lists players who played
            else:
                status = "unmatched"
        results.append({"match_status": status, "afltables_url": url})

    matched = pd.concat([picks.reset_index(drop=True), pd.DataFrame(results)], axis=1)

    # Games from AFL Tables for each matched player
    games = seasons.groupby("afltables_url")["games"].sum()
    matched["afltables_games"] = matched["afltables_url"].map(games)

    after = matched[["afltables_url", "draft_year"]].merge(seasons, on="afltables_url", how="left")
    after = after[after["season"] > after["draft_year"]]
    games_after = after.groupby(["afltables_url", "draft_year"])["games"].sum()
    matched["afltables_games_after_draft"] = [
        games_after.get((url, year)) for url, year in zip(matched["afltables_url"], matched["draft_year"])
    ]
    return matched


def suggest_names(name: str, draft_year: int, seasons: pd.DataFrame, n: int = 3) -> list[str]:
    """Closest AFL Tables names (active after `draft_year`), for manual review only."""
    active = seasons.loc[seasons["season"] > draft_year, "player"].unique()
    return difflib.get_close_matches(name, active, n=n, cutoff=0.6)
