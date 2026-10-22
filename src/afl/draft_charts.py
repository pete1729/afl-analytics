"""Draft-record charts and tables for one club against the league-wide pick curve.

Used by notebooks/03_club_draft_record.ipynb. Games are DraftGuru's games after
the draft (to the end of the latest season), as in notebook 01.
"""

import matplotlib.pyplot as plt
import pandas as pd

MAX_PICK = 80
WINDOW = 2  # the curve at pick p uses all picks from p-2 to p+2

# Grey for context, blue for the typical curve, orange for the club in focus
GREY, BLUE, BLUE_BAND, ORANGE, INK, TITLE = (
    "#c3c2b7", "#2a78d6", "#cde2fb", "#eb6834", "#52514e", "#0b0b0b")


def apply_style() -> None:
    """Quiet axes and grid, so the data stands out."""
    plt.rcParams.update({
        "figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
        "axes.grid": True, "grid.color": "#e8e7e3", "grid.linewidth": 0.8,
    })


def pick_curve(picks: pd.DataFrame) -> pd.DataFrame:
    """Median, mean and quartiles of games after draft for each pick (picks +/- WINDOW)."""
    rows = []
    for p in range(1, MAX_PICK + 1):
        nearby = picks.loc[(picks["pick"] - p).abs() <= WINDOW, "games_after_draft"]
        rows.append({"pick": p, "n": len(nearby), "median": nearby.median(), "mean": nearby.mean(),
                     "q25": nearby.quantile(0.25), "q75": nearby.quantile(0.75)})
    return pd.DataFrame(rows).set_index("pick")


def draw_curve(ax, picks: pd.DataFrame, curve: pd.DataFrame) -> None:
    """All picks as grey dots, with the median and middle-50% band."""
    shown = picks[picks["pick"] <= MAX_PICK]
    ax.scatter(shown["pick"], shown["games_after_draft"], s=9, color=GREY, alpha=0.6,
               linewidths=0, label="Individual pick")
    ax.fill_between(curve.index, curve["q25"], curve["q75"], color=BLUE_BAND, alpha=0.8,
                    linewidth=0, label="Middle 50% (picks ±2)")
    ax.plot(curve.index, curve["median"], color=BLUE, linewidth=2, label="Median (picks ±2)")
    ax.set_xlim(0, MAX_PICK + 1)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("National draft pick number")
    ax.set_ylabel("AFL games after being drafted")


def club_picks(picks: pd.DataFrame, curve: pd.DataFrame, club: str) -> pd.DataFrame:
    """One club's picks, with the curve's median at each pick as the expected games."""
    rows = picks[picks["club"] == club].copy()
    rows["expected"] = rows["pick"].map(curve["median"])  # NaN beyond MAX_PICK
    rows["vs_expected"] = rows["games_after_draft"] - rows["expected"]
    return rows


def plot_club_picks(picks: pd.DataFrame, curve: pd.DataFrame, club: str,
                    n_above: int = 5, n_below: int = 3):
    """The club's picks over the league curve, labelling the biggest hits and misses."""
    rows = club_picks(picks, curve, club)
    shown = rows[rows["pick"] <= MAX_PICK]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    draw_curve(ax, picks, curve)
    ax.scatter(shown["pick"], shown["games_after_draft"], s=45, color=ORANGE,
               edgecolors="white", linewidths=1.5, zorder=3, label=f"{club} pick")

    to_label = pd.concat([shown.nlargest(n_above, "vs_expected"),
                          shown.nsmallest(n_below, "vs_expected")])
    placed = []  # (pick, games) of labels already drawn
    for row in to_label.sort_values("pick").itertuples():
        # Step a label one line away for each nearby earlier label it would overlap:
        # downwards normally, upwards near the x-axis where there's no room below
        clashes = sum(abs(row.pick - p) < 12 and abs(row.games_after_draft - g) < 20
                      for p, g in placed)
        step = 12 if row.games_after_draft < 50 else -12
        ax.annotate(f"{row.player} ({row.draft_year})", (row.pick, row.games_after_draft),
                    xytext=(6, 4 + step * clashes), textcoords="offset points",
                    fontsize=8, color=TITLE)
        placed.append((row.pick, row.games_after_draft))

    first, last = picks["draft_year"].min(), picks["draft_year"].max()
    ax.set_title(f"{club} national draft picks vs the typical curve, {first}–{last}",
                 loc="left", color=TITLE)
    ax.legend(frameon=False, loc="upper right")
    return fig


def club_benchmark(picks: pd.DataFrame, curve: pd.DataFrame) -> pd.DataFrame:
    """Every club's games produced vs expected, for picks 1 to MAX_PICK.

    vs_mean is the main measure: total games / sum of the mean at each pick.
    vs_median is shown for comparison but favours clubs that drafted late,
    because late picks are heavily skewed (see notebook 01).
    """
    in_range = picks[picks["pick"] <= MAX_PICK].copy()
    in_range["expected_mean"] = in_range["pick"].map(curve["mean"])
    in_range["expected_median"] = in_range["pick"].map(curve["median"])
    in_range["above_median"] = in_range["games_after_draft"] > in_range["expected_median"]

    clubs = in_range.groupby("club").agg(
        picks=("pick", "size"),
        average_pick=("pick", "mean"),
        games=("games_after_draft", "sum"),
        expected_mean=("expected_mean", "sum"),
        expected_median=("expected_median", "sum"),
        share_above_median=("above_median", "mean"),
        games_for_club=("games_for_drafting_club", "sum"),
    )
    clubs["vs_mean"] = clubs["games"] / clubs["expected_mean"]
    clubs["vs_median"] = clubs["games"] / clubs["expected_median"]
    clubs["share_kept"] = clubs["games_for_club"] / clubs["games"]
    clubs["rank_vs_mean"] = clubs["vs_mean"].rank(ascending=False).astype(int)
    clubs["rank_vs_median"] = clubs["vs_median"].rank(ascending=False).astype(int)
    return clubs.sort_values("vs_mean", ascending=False)


def plot_club_benchmark(clubs: pd.DataFrame, club: str, first: int, last: int):
    """Horizontal bars of vs_mean for every club, with `club` highlighted."""
    clubs = clubs.sort_values("vs_mean")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(clubs.index, clubs["vs_mean"],
            color=[ORANGE if c == club else GREY for c in clubs.index], height=0.6)
    ax.axvline(1, color=INK, linewidth=1, linestyle="--", zorder=0)
    for y, (_, row) in enumerate(clubs.iterrows()):
        ax.annotate(f"{row['vs_mean']:.2f}  ({int(row['picks'])} picks)", (row["vs_mean"], y),
                    xytext=(4, 0), textcoords="offset points", va="center", fontsize=8,
                    color=INK, bbox=dict(facecolor="white", edgecolor="none", pad=1))
    ax.grid(axis="y", visible=False)
    ax.set_xlim(0, clubs["vs_mean"].max() * 1.2)
    ax.set_xlabel(f"Games produced ÷ games expected (mean at each pick number, picks 1–{MAX_PICK})")
    ax.set_title(f"Draft returns by drafting club, {first}–{last}", loc="left", color=TITLE)
    return fig
