"""Helpers for draft outcome analysis: outcome windows, expected values and bootstraps."""

import numpy as np
import pandas as pd


def games_in_window(picks: pd.DataFrame, seasons: pd.DataFrame, n_seasons: int) -> pd.Series:
    """Games each pick played in the `n_seasons` seasons after their draft year.

    Seasons Y+1 to Y+n for draft year Y. Picks with no AFL Tables match
    (they never played) get 0.
    """
    joined = picks[["afltables_url", "draft_year"]].reset_index().merge(
        seasons[["afltables_url", "season", "games"]], on="afltables_url", how="inner"
    )
    in_window = joined[
        (joined["season"] > joined["draft_year"])
        & (joined["season"] <= joined["draft_year"] + n_seasons)
    ]
    games = in_window.groupby("index")["games"].sum()
    return games.reindex(picks.index, fill_value=0)


def games_before_draft(picks: pd.DataFrame, seasons: pd.DataFrame) -> pd.Series:
    """Games each pick played in seasons up to and including their draft year."""
    joined = picks[["afltables_url", "draft_year"]].reset_index().merge(
        seasons[["afltables_url", "season", "games"]], on="afltables_url", how="inner"
    )
    before = joined[joined["season"] <= joined["draft_year"]]
    games = before.groupby("index")["games"].sum()
    return games.reindex(picks.index, fill_value=0)


def expected_at_pick(picks: pd.DataFrame, value: str, window: int = 2,
                     leave_one_out: bool = False) -> pd.Series:
    """Expected `value` for each pick: the mean over all picks within +/- `window`.

    With leave_one_out=True, each player's own result is left out of their
    expected value, so a player can't pull their own baseline towards them.
    """
    expected = pd.Series(index=picks.index, dtype=float)
    for idx, pick in picks["pick"].items():
        nearby = picks.loc[(picks["pick"] - pick).abs() <= window, value]
        if leave_one_out:
            expected[idx] = (nearby.sum() - picks.at[idx, value]) / (len(nearby) - 1)
        else:
            expected[idx] = nearby.mean()
    return expected


def add_residuals(data: pd.DataFrame, games_col: str, window: int = 2,
                  leave_one_out: bool = False) -> pd.DataFrame:
    """Add outcome columns and their residuals against the expected value at each pick.

    games:         copied from `games_col` (e.g. "games_8")
    bust:          1 if under 50 games, else 0
    massive_bust:  1 if under 20 games, else 0
    expected_<x>, resid_<x> for each of those three
    """
    data = data.copy()
    data["games"] = data[games_col]
    data["bust"] = (data["games"] < 50).astype(float)
    data["massive_bust"] = (data["games"] < 20).astype(float)
    for col in ["games", "bust", "massive_bust"]:
        data[f"expected_{col}"] = expected_at_pick(data, col, window=window,
                                                   leave_one_out=leave_one_out)
        data[f"resid_{col}"] = data[col] - data[f"expected_{col}"]
    return data


def slope(x, y) -> float:
    """Ordinary least squares slope of y on x."""
    return np.polyfit(x, y, 1)[0]


def bootstrap(df: pd.DataFrame, statistic, n: int = 2000, seed: int = 2026):
    """Point estimate and 95% bootstrap interval for statistic(df).

    Resamples rows (players) with replacement. The expected-at-pick baseline
    is held fixed, as the pre-registration specifies.
    """
    rng = np.random.default_rng(seed)
    estimates = [
        statistic(df.iloc[rng.integers(0, len(df), len(df))])
        for _ in range(n)
    ]
    low, high = np.percentile(estimates, [2.5, 97.5])
    return statistic(df), low, high


def verdict(low: float, high: float) -> str:
    """Pre-registered reading of a 95% interval for a slope (H1 expects negative)."""
    if high < 0:
        return "supported (interval below 0)"
    if low > 0:
        return "contradicted (interval above 0)"
    return "inconclusive (interval includes 0)"
