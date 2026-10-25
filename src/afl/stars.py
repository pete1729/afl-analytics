"""Find the league's top players and trace how each one entered the AFL."""

from io import StringIO

import pandas as pd

from afl.draftguru import BASE_URL, birth_dates, year_movements
from afl.fetch import fetch
from afl.match import TEAM_NAMES, load_manual_matches, normalise_name

MOVES = ["Trade", "Free Agency"]  # every other row type is a way into the AFL
BID_MATCHED = r"(Academy|Father-Son|Scholarship|Zone|NGA)"


def season_totals(seasons: pd.DataFrame, first: int, last: int) -> pd.DataFrame:
    """Brownlow votes and games per player over seasons first..last, with latest club."""
    window = seasons[seasons["season"].between(first, last)].sort_values("season")
    totals = window.groupby("afltables_url").agg(
        player=("player", "last"),
        club=("team", "last"),  # club in the most recent season played
        votes=("brownlow_votes", "sum"),
        games=("games", "sum"),
    )
    totals["club"] = totals["club"].replace(TEAM_NAMES)
    return totals


def top_players(seasons: pd.DataFrame, first: int, last: int, n: int = 36) -> pd.DataFrame:
    """Players ranked in the top `n` for Brownlow votes over first..last.

    Ties at the cutoff are all included, so there can be slightly more than `n`.
    """
    totals = season_totals(seasons, first, last)
    totals["rank"] = totals["votes"].rank(ascending=False, method="min").astype(int)
    return totals[totals["rank"] <= n].sort_values("rank").reset_index()


def top_per_club(seasons: pd.DataFrame, first: int, last: int, n: int = 2) -> pd.DataFrame:
    """Each club's top `n` vote-getters over first..last, counting votes earned for that club.

    A player who changed clubs is ranked at each club on the votes he polled there.
    Ties at the cutoff are all included.
    """
    window = seasons[seasons["season"].between(first, last)].assign(
        club=lambda d: d["team"].replace(TEAM_NAMES))
    by_club = window.groupby(["club", "afltables_url"]).agg(
        player=("player", "last"), votes=("brownlow_votes", "sum"), games=("games", "sum"),
    ).reset_index()
    by_club["rank"] = by_club.groupby("club")["votes"].rank(ascending=False, method="min").astype(int)
    return by_club[by_club["rank"] <= n].sort_values(["club", "rank"]).reset_index(drop=True)


def brownlow_top(seasons: pd.DataFrame, n: int, first: int = 2006, last: int = 2026) -> pd.DataFrame:
    """(season, afltables_url) for every player in the top `n` for Brownlow votes that season.

    Ties at the cutoff are all included.
    """
    votes = seasons[seasons["season"].between(first, last)].groupby(["season", "afltables_url"])[
        "brownlow_votes"].sum().reset_index()
    votes["rank"] = votes.groupby("season")["brownlow_votes"].rank(ascending=False, method="min")
    return votes.loc[votes["rank"] <= n, ["season", "afltables_url"]]


def star_season_counts(picks: pd.DataFrame, seasons: pd.DataFrame, squad: pd.DataFrame,
                       years: int | None = 8) -> pd.DataFrame:
    """Star seasons for each pick, under each definition in docs/star_curve_definitions.md.

    `picks` needs draft_year, afltables_url and draftguru_url (as from draft_outcomes()).
    Counts seasons draft_year+1 to draft_year+`years`, or every season after the
    draft if `years` is None. Returns one row per pick (same index) with columns
    squad, brownlow36, brownlow40 and either40 (squad or Brownlow top 40).
    """
    keys = picks[["draft_year", "afltables_url", "draftguru_url"]].reset_index()
    squad_seasons = squad[["draftguru_url", "year"]].rename(columns={"year": "season"})
    hits = {
        "squad": keys.merge(squad_seasons, on="draftguru_url"),
        "brownlow36": keys.merge(brownlow_top(seasons, 36), on="afltables_url"),
        "brownlow40": keys.merge(brownlow_top(seasons, 40), on="afltables_url"),
    }
    hits["either40"] = pd.concat([hits["squad"], hits["brownlow40"]])
    counts = {}
    for name, h in hits.items():
        later = h["season"] > h["draft_year"]
        if years is not None:
            later &= h["season"] <= h["draft_year"] + years
        counts[name] = (h[later].drop_duplicates(["index", "season"]).groupby("index").size()
                        .reindex(picks.index, fill_value=0))
    return pd.DataFrame(counts)


def all_movements(first_year: int, last_year: int) -> pd.DataFrame:
    """year_movements() for every year, stacked, with the year as a column."""
    years = [year_movements(year).assign(year=year) for year in range(first_year, last_year + 1)]
    return pd.concat(years, ignore_index=True)


def match_to_draftguru(players: pd.DataFrame, movements: pd.DataFrame,
                       seasons: pd.DataFrame) -> pd.DataFrame:
    """Add draftguru_url and match_status to AFL Tables players (needs afltables_url, player).

    Same rules as the draft matcher: an exact normalised name, narrowed by clubs
    played for if several DraftGuru players share it, and the reviewed manual
    matches first. Anything else is left unmatched, not guessed.
    """
    manual = {at: dg for dg, at in load_manual_matches().items()}
    clubs_played = (seasons.assign(club=seasons["team"].replace(TEAM_NAMES))
                    .groupby("afltables_url")["club"].agg(set))
    dg = movements.assign(name_key=movements["player"].map(normalise_name))
    dg_clubs = dg.groupby("draftguru_url")["club"].agg(set)

    urls, statuses = [], []
    for row in players.itertuples():
        if row.afltables_url in manual:
            urls.append(manual[row.afltables_url])
            statuses.append("manual")
            continue
        candidates = dg.loc[dg["name_key"] == normalise_name(row.player), "draftguru_url"].unique()
        status = "name"
        if len(candidates) > 1:
            played = clubs_played.get(row.afltables_url, set())
            candidates = [c for c in candidates if dg_clubs[c] & played]
            status = "name + club"
        if len(candidates) == 1:
            urls.append(candidates[0])
            statuses.append(status)
        else:
            urls.append(None)
            statuses.append("ambiguous" if len(candidates) > 1 else "unmatched")
    return players.assign(draftguru_url=urls, match_status=statuses)


def entry_routes(urls, movements: pd.DataFrame) -> pd.DataFrame:
    """How each DraftGuru player first entered the AFL, and the clubs he moved to after.

    The entry is his earliest row that isn't a trade or free-agency move: a
    national, rookie, mid-season, pre-season or mini-draft pick, or a pre- or
    post-draft signing. If a player has no such row (e.g. a pre-listing that
    DraftGuru records as a trade, or an entry before the first year in
    `movements`), his first record is used and labelled for manual review.
    """
    dobs = birth_dates().drop_duplicates("draftguru_url").set_index("draftguru_url")["dob"]
    rows = []
    for url in urls:
        history = movements[movements["draftguru_url"] == url].sort_values("year")
        if history.empty:
            rows.append({"draftguru_url": url, "entry_route": "Not found"})
            continue
        entries = history[~history["draft"].isin(MOVES)]
        first = entries.iloc[0] if len(entries) else history.iloc[0]
        route = first["draft"] if len(entries) else f"{first['draft']} (no draft record: check)"
        dob = dobs.get(url)
        later = history[history["draft"].isin(MOVES) & (history.index != first.name)]
        rows.append({
            "draftguru_url": url,
            "entry_route": route,
            "entry_year": int(first["year"]),
            "entry_pick": first["pick"],
            "entry_club": first["club"],
            "signing": first["signing"],
            "bid_matched": bool(pd.Series([first["signing"]]).str.match(BID_MATCHED).iloc[0]),
            "height_cm": first["height_cm"],
            "pathway_club": first["pathway_club"],
            "age_at_entry": ((pd.Timestamp(f"{int(first['year'])}-11-30") - dob).days / 365.25
                             if pd.notna(dob) else None),
            "moved_to": " > ".join(later["club"]),  # clubs joined by trade or free agency
        })
    return pd.DataFrame(rows)


def all_australian_squad(first_year: int, last_year: int) -> pd.DataFrame:
    """Every All-Australian squad member for each season, with DraftGuru links.

    The squad is the final team plus the players named in the squad but left
    out of the team. DraftGuru lists the second group on one page for all years
    (from 2007, when the squad began), so the squad is that page joined with
    the team pages. Years before 2007 return the team alone.
    """
    html = fetch(f"{BASE_URL}/awards/all-australian-squad")
    page = pd.read_html(StringIO(html), extract_links="body")[0]
    left_out = pd.DataFrame({
        "year": page["Year"].map(lambda c: int(c[0])),
        "player": page["Player"].map(lambda c: c[0].replace("\xa0", " ")),
        "draftguru_url": BASE_URL + page["Player"].map(lambda c: c[1] or ""),
        "in_team": False,
    })
    team = pd.concat([all_australian(year) for year in range(first_year, last_year + 1)])
    team = team[["year", "player", "draftguru_url"]].assign(in_team=True)
    left_out = left_out[left_out["year"].between(first_year, last_year)]
    return pd.concat([team, left_out], ignore_index=True)


def all_australian(year: int) -> pd.DataFrame:
    """The All-Australian team for `year`, from DraftGuru (positions and player links)."""
    html = fetch(f"{BASE_URL}/awards/all-australian/{year}")
    if html is None:
        return pd.DataFrame()
    table = pd.read_html(StringIO(html), extract_links="body")[0]
    return pd.DataFrame({
        "year": year,
        "position": table["Position"].map(lambda c: c[0]),
        "player": table["Player"].map(lambda c: c[0].replace("\xa0", " ")),
        "draftguru_url": BASE_URL + table["Player"].map(lambda c: c[1] or ""),
        "club": table["Club"].map(lambda c: c[0]),
        "drafted": table["Drafted"].map(lambda c: c[0]),  # DraftGuru's own summary
    })
