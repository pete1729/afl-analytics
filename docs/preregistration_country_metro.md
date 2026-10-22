# Pre-registration: country vs metro Victorian draftees

Written and committed **before** any outcome was compared between country and
metro players. The only figures looked at were group sizes and the overall
spread of residual games (to estimate power). Where the analysis departs from
this plan, the notebook will say so and why.

## Question

Are country players overlooked? **At the same pick number, do Victorian
draftees from country under-18 clubs beat their pick by more than those from
metro clubs?** If they do, clubs have been undervaluing country players, for
example because they're seen less often or play in a weaker local competition.

## Why Victoria only

Victoria's under-18 competition (TAC Cup, then NAB League, now Talent League)
is organised into regional clubs with geographic zones. So the under-18 club
listed last in DraftGuru's pathway gives a clean country/metro label.

Other states' pathways run through metro-based state-league clubs, so a
country label there would need home towns looked up player by player. They're
out of scope.

## Data

- National draft picks 1–80, 2005–2018 (DraftGuru), as in notebooks 02 and 04.
- **Pathway:** the last club in DraftGuru's "Original Club" chain (e.g.
  `Drysdale / Christian College Geelong / Geelong U18` gives `Geelong U18`).
- Games per season from AFL Tables, with all picks who played matched.

## Groups

| Group | Under-18 clubs (as DraftGuru names them) | Picks |
|---|---|---|
| **Country** | Murray U18, Gippsland U18, North Ballarat U18 (later GWV Rebels), Bendigo U18 | 113 |
| **Metro** | Oakleigh U18, Sandringham U18, Dandenong U18, Calder U18, Eastern U18, Northern U18, Western U18 | 320 |
| Geelong (separate) | Geelong U18 | 55 |

- **Geelong** is a regional city, so it's not clearly country or metro. It's left
  out of the primary test and added to the country group in a secondary check.
- **Dandenong** (which includes the Mornington Peninsula) and **Calder** (which
  reaches into the Macedon Ranges) cover some semi-rural areas but are treated
  as metro.
- Players whose last listed club is a state-league or other club are excluded,
  even if they came through a Victorian under-18 club earlier. That keeps the
  test on the standard junior pathway.

## Definitions (same as notebook 02)

- **Outcome:** games in the first 8 seasons after the draft.
- **Expected at a pick:** the mean outcome of **all** 2005–2018 picks (every
  state) within ±2 of that pick. So each player is compared with the league,
  not just with other Victorians.
- **Residual:** actual minus expected.
- **Bust:** under 50 games in the window. **Massive bust:** under 20.

## Primary test

- **Statistic:** mean residual games of country picks minus mean residual games
  of metro picks.
- **Interval:** 95% bootstrap interval, 2,000 resamples of players, seed 2026.
- **Reading:** *supported* (country players undervalued) if the whole interval
  is above 0; *contradicted* (country players overvalued) if the whole interval
  is below 0; *inconclusive* otherwise.

## Power

The residual standard deviation across all picks is about 49 games, giving a
standard error of about 5.3 games for this difference. **The test has roughly
80% power to detect a difference of about 15 games.** Smaller real differences
will probably read as inconclusive, and that wouldn't be evidence of no difference.

## Secondary (reported, not used to judge the primary test)

1. Bust and massive-bust rates for each group, against the expected rate at their picks.
2. Geelong counted as country.
3. Excluding mature-age players (19.0+ at the draft; 34 Victorian under-18 picks).
4. Excluding bid-matched picks (academy, father-son, scholarship, zone).
5. A 10-season window (2005–2016 drafts).
6. Separately for picks 1–40 and 41–80.

**Descriptive only, not tests:**
- average pick and share of picks by group
- the result for each individual under-18 club, with its sample size

## Not planned

No changes to the groups, Geelong's treatment, the window or the pick range
after seeing results. No other states, and no school or other pathway attributes.

## Known limitations

- An under-18 club zone is a rough stand-in for where a player grew up. Some
  country players board at Melbourne schools and play for metro clubs.
- We only see drafted players. A positive result would mean drafted country
  players beat their pick, not that undrafted country players were missed.
- Club-level results (e.g. one strong country club) could drive a group result.
  The per-club table will show this.

## Erratum (added after sign-off, before any outcome was compared)

The metro count of **320** above is wrong; the correct figure is **309**. The
power check joined pathway clubs to picks by DraftGuru URL, which double-counted
players drafted twice (Ben Jacobs, Mitch Brown, Billy Hartung, Daniel Currie,
Matthew Spangher, and Simon Buckley, whose second selection was pick 85). The
group definitions are unchanged. The standard error for the difference rises
slightly, from about 5.3 to 5.4 games, so power is essentially unchanged.
