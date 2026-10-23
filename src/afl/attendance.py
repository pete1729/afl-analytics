"""Every match on an AFL Tables season page, with date, start time, venue and crowd.

Season pages list each match as a small two-row table:

    home team | quarter scores | final score | date, time, Att: and Venue:
    away team | quarter scores | final score | result and match-stats link

Round headers ("Round 5", "Qualifying Final") sit in their own tables just
before each round's matches, so we walk the tables in page order and remember
the latest header. The start time is the venue's local time; the time in
brackets after it (Melbourne standard time) is ignored.
"""

import re
from datetime import datetime

import pandas as pd
from bs4 import BeautifulSoup

from afl.fetch import fetch

SEASON_URL = "https://afltables.com/afl/seas/{year}.html"

ROUND_HEADER = re.compile(r"^(Round \d+|[A-Za-z ]+ Final)$")
# Attendance is optional: some 2021 games list none (crowds were barred)
MATCH_INFO = re.compile(r"(\w{3} \d{2}-\w{3}-\d{4}) (\d{1,2}:\d{2} [AP]M).*?(?:Att: ([\d,]+)\s+)?Venue: (.+)$")

# South Australian venues, used to spot Gather Round (a round played entirely in SA)
SA_VENUES = {"Adelaide Oval", "Norwood Oval", "Summit Sports Park", "Barossa Park"}


def season_matches(year: int) -> pd.DataFrame:
    """One row per match: season, round, finals, start, home, away, scores, attendance, venue."""
    html = fetch(SEASON_URL.format(year=year), encoding="latin-1")
    rows, current_round = [], None
    for table in BeautifulSoup(html, "lxml").find_all("table"):
        cells = table.find_all("td")
        first = cells[0].get_text(" ", strip=True).replace("* see notes", "").strip() if cells else ""
        if ROUND_HEADER.match(first):
            current_round = first
            continue

        trs = table.find_all("tr", recursive=False)
        if len(trs) != 2:
            continue
        home_cells, away_cells = (tr.find_all("td", recursive=False) for tr in trs)
        if len(home_cells) != 4 or "Venue:" not in home_cells[3].get_text():
            continue
        info = MATCH_INFO.search(home_cells[3].get_text(" ", strip=True))
        date, time, attendance, venue = info.groups()
        rows.append({
            "season": year,
            "round": current_round,
            "final": current_round.endswith("Final"),
            "start": datetime.strptime(f"{date} {time}", "%a %d-%b-%Y %I:%M %p"),
            "home": home_cells[0].get_text(strip=True),
            "away": away_cells[0].get_text(strip=True),
            "home_score": int(home_cells[2].get_text(strip=True)),
            "away_score": int(away_cells[2].get_text(strip=True)),
            "attendance": int(attendance.replace(",", "")) if attendance else None,
            "venue": venue.strip(),
        })
    return pd.DataFrame(rows)


def gather_rounds(matches: pd.DataFrame) -> set[tuple[int, str]]:
    """(season, round) pairs where every match was played in South Australia (finals aside)."""
    in_sa = matches[~matches["final"]].groupby(["season", "round"])["venue"].agg(lambda v: v.isin(SA_VENUES).all())
    return set(in_sa[in_sa].index)


def time_slot(start: datetime) -> str:
    """Coarse day/time slot, e.g. 'Saturday afternoon'. Night means a 5pm start or later.

    Thursday and Friday games are always at night. Other weekdays (public
    holidays) are grouped with Thursday night, the other midweek slot.
    """
    day = start.strftime("%A")
    night = start.hour >= 17
    if day == "Friday":
        return "Friday night"
    if day in ("Saturday", "Sunday"):
        return f"{day} {'night' if night else 'afternoon'}"
    return "Thursday or other weeknight"


def recent_form(matches: pd.DataFrame, team: str, n: int = 10) -> pd.Series:
    """`team`'s win % over its previous `n` games before each match (draws count as half).

    Runs across season boundaries and includes finals, so round 1 uses the end
    of last season. Indexed like `matches`; NaN for other teams' games and for
    matches with fewer than `n` earlier games in `matches`.
    """
    games = matches[(matches["home"] == team) | (matches["away"] == team)].sort_values("start")
    is_home = games["home"] == team
    margin = (games["home_score"] - games["away_score"]).where(is_home, games["away_score"] - games["home_score"])
    result = (margin > 0) * 1.0 + (margin == 0) * 0.5
    # shift(1) so each game only sees results from before it
    form = 100 * result.rolling(n).mean().shift(1)
    return form.reindex(matches.index)


def both_teams_form(matches: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """recent_form() for both teams in every match: columns home_form and away_form."""
    out = pd.DataFrame(index=matches.index, columns=["home_form", "away_form"], dtype=float)
    for team in pd.unique(matches[["home", "away"]].to_numpy().ravel()):
        form = recent_form(matches, team, n)
        for side in ("home", "away"):
            rows = matches[side] == team
            out.loc[rows, f"{side}_form"] = form[rows]
    return out
