"""Parse the scoring progression on AFL Tables match pages.

The progression table (anchor name="prog") is malformed: quarter header rows
are never closed, so pandas.read_html only returns one row. Instead we:

1. cut out the progression table's HTML,
2. split it on the quarter headers, e.g. "1st quarter (33m 38s)", keeping each
   quarter's actual length (the last one is called "Final quarter"),
3. parse the <tr> rows within each quarter. Each row has 5 cells:
   home event | home time | score | away time | away event,
   with &nbsp; on the side that didn't score.

The final summary rows ("Biggest lead...", "Game time...") are skipped.
"""

import re
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup

from afl.fetch import fetch

SEASON_URL = "https://afltables.com/afl/seas/{year}.html"
GAMES_URL = "https://afltables.com/afl/stats/games/"

QUARTER_HEADER = re.compile(
    r"<td[^>]*colspan=5[^>]*><b>(1st|2nd|3rd|Final) quarter \((\d+)m (\d+)s\)")
QUARTER_NUMBER = {"1st": 1, "2nd": 2, "3rd": 3, "Final": 4}


def to_seconds(text: str) -> int:
    """'14m 8s' -> 848."""
    minutes, seconds = re.fullmatch(r"(\d+)m (\d+)s", text.strip()).groups()
    return int(minutes) * 60 + int(seconds)


def parse_event(text: str) -> tuple[str | None, str]:
    """'Ollie Wines goal' -> ('Ollie Wines', 'goal'); 'Rushed behind' -> (None, 'behind')."""
    text = text.strip()
    if text == "Rushed behind":
        return None, "behind"
    player, kind = text.rsplit(" ", 1)
    if kind not in ("goal", "behind"):
        raise ValueError(f"Unexpected scoring event: {text!r}")
    return player, kind


def final_scores(html: str) -> dict[str, int]:
    """Final points for each team, from the scoreboard at the top of the page."""
    board = pd.read_html(StringIO(html))[0]
    # Rows 1 and 2 are the two teams; the last score column is the final score
    return {row[1]: int(str(row[5]).split(".")[-1]) for row in board.iloc[1:3].itertuples(index=False)}


def scoring_progression(html: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (events, quarters) for one match page.

    events:   quarter, seconds, team, opponent, player, kind ("goal"/"behind"), points
    quarters: quarter, length_seconds
    """
    start = html.index('<a name="prog">')
    table = html[start:html.index("</table>", start)]
    header = BeautifulSoup(table[:table.index("quarter")], "lxml")
    home, away = [th.get_text(strip=True) for th in header.find_all("th")[1::4]][:2]

    # re.split with groups gives: [before, q, mins, secs, chunk, q, mins, secs, chunk, ...]
    parts = QUARTER_HEADER.split(table)
    events, quarters = [], []
    for i in range(1, len(parts), 4):
        quarter = QUARTER_NUMBER[parts[i]]
        quarters.append({"quarter": quarter, "length_seconds": int(parts[i + 1]) * 60 + int(parts[i + 2])})

        for row in BeautifulSoup(f"<table>{parts[i + 3]}</table>", "lxml").find_all("tr"):
            cells = [td.get_text(" ", strip=True).replace("\xa0", "").strip() for td in row.find_all("td")]
            if len(cells) != 5 or cells[0].startswith("Biggest lead"):
                continue  # summary rows at the end of the table
            home_event, home_time, _score, away_time, away_event = cells
            if home_event:
                team, opponent, event, time = home, away, home_event, home_time
            else:
                team, opponent, event, time = away, home, away_event, away_time
            player, kind = parse_event(event)
            events.append({"quarter": quarter, "seconds": to_seconds(time), "team": team,
                           "opponent": opponent, "player": player, "kind": kind,
                           "points": 6 if kind == "goal" else 1})
    return pd.DataFrame(events), pd.DataFrame(quarters)


def check_match(events: pd.DataFrame, html: str) -> bool:
    """True if each team's summed points equal its final score on the scoreboard."""
    summed = events.groupby("team")["points"].sum()
    return all(summed.get(team, 0) == points for team, points in final_scores(html).items())


def season_match_urls(year: int) -> list[str]:
    """Links to every match page on a season page, in the order they appear."""
    html = fetch(SEASON_URL.format(year=year), encoding="latin-1")
    links = re.findall(rf'href="\.\./stats/games/({year}/\d+\.html)"', html)
    return [GAMES_URL + link for link in dict.fromkeys(links)]  # drop repeats, keep order
