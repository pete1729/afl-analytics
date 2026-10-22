"""Build the per-pick draft outcomes table used by the analysis notebooks."""

import pandas as pd

from afl.afltables import all_season_games
from afl.analysis import games_before_draft, games_in_window
from afl.draftguru import birth_dates, national_picks
from afl.match import load_manual_matches, match_picks

LAST_SEASON = 2026
MATURE_AGE = 19.0  # age on 30 November of the draft year (see docs/ pre-registrations)


def draft_outcomes(first_draft: int, last_draft: int, windows=(5, 8, 10),
                   max_pick: int = 80) -> pd.DataFrame:
    """One row per national draft pick (picks 1 to max_pick), with outcomes and attributes.

    Columns added to national_picks():
      dob, age, mature_age      age on 30 November of the draft year; age is NaN when
                                the date of birth is unknown, so filter on age.notna()
                                before comparing mature-age and junior players
      match_status, afltables_url
      games_<n>                 games in the n seasons after the draft, for each n in
                                `windows`; NaN where those seasons aren't complete yet
      prior_games               AFL games up to and including the draft year
      bid_matched               academy, father-son, scholarship or zone picks
    """
    picks = pd.concat([national_picks(year) for year in range(first_draft, last_draft + 1)],
                      ignore_index=True)
    picks = picks.merge(birth_dates(), on="draftguru_url", how="left")

    # Matching uses 2006 onwards, as validated in notebook 01. Earlier seasons are
    # only used to count games played before the draft.
    seasons = all_season_games(2006, LAST_SEASON)
    early_seasons = all_season_games(1995, 2005)

    df = match_picks(picks, seasons, load_manual_matches())
    df = df[df["pick"] <= max_pick].copy()

    df["age"] = (pd.to_datetime(df["draft_year"].astype(str) + "-11-30") - df["dob"]).dt.days / 365.25
    df["mature_age"] = df["age"] >= MATURE_AGE  # False when age is unknown: filter on age first

    for n in windows:
        games = games_in_window(df, seasons, n).astype(float)
        games[df["draft_year"] + n > LAST_SEASON] = float("nan")  # window not finished
        df[f"games_{n}"] = games

    df["prior_games"] = games_before_draft(df, pd.concat([early_seasons, seasons]))
    df["bid_matched"] = df["signing"].str.match(r"(Academy|Father-Son|Scholarship|Zone)")
    return df
