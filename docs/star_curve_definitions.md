# Definitions: the star-probability curve

Written and committed **before** any star-probability figure was computed. This
is a description of how often each pick produces a star, not a hypothesis test,
but fixing the definitions first stops the results from shaping them.

## Question

For each national draft pick, **what is the chance the player becomes one of
the league's best players?** This is the "ceiling" counterpart to notebook 01's
games curve, which measures the "floor".

## Definitions

- **Star season:** a season in which the player ranks in the **top 36 of all
  players for Brownlow votes** (about 2 per club). Ties at 36th place are all
  included. Seasons 2006–2026, from AFL Tables.
- **Population:** national draft picks 1–80, 2005–2018 (1,004 picks), as in
  notebooks 02, 04 and 05. Picks who never played have no star seasons.
- **Window:** the first 8 seasons after the draft (Y+1 to Y+8), the same window
  as notebooks 02 and 05, complete for every draft.
- **Main outcome:** at least one star season in the window.
- **Second outcome:** two or more star seasons in the window (a sustained star,
  not a one-season spike).
- **Curve:** the share of picks within **±5** of each pick number who reach the
  outcome. The window is wider than the games curve's ±2 because star seasons
  are much rarer, so ±2 would be very noisy.
- **Bands (for tables):** picks 1–5, 6–10, 11–20, 21–30, 31–40, 41–60, 61–80.
- **Uncertainty:** 95% bootstrap intervals, 2,000 resamples of players, seed 2026.

## Also reported

1. **Floor and ceiling side by side, by band:** the share playing 50+ games in
   the window (not a bust) alongside the share with a star season.
2. **Mature-age vs junior:** actual star rate minus the expected star rate at
   their picks (the ±5 curve), for each group, with intervals. Mature-age means
   19.0+ on 30 November of the draft year, as before. This revisits notebook 04's
   "150+ games" ceiling result with a quality measure, so it's **exploratory**.
3. **Where star seasons come from:** of all star seasons in 2006–2026 by
   players who entered the AFL in 2005–2018, the share by entry route (national
   picks by band, rookie, mid-season, other).

## Known limitations

- Brownlow votes favour midfielders. Key defenders, rucks and some key forwards
  rarely make the top 36, so this is a curve for "star by Brownlow votes", not
  for every kind of elite player. (The All-Australian section of notebook 06
  gives a position-balanced view of current stars.)
- An 8-season window can miss stars who peak late, especially tall players.
- Votes depend partly on team quality: stronger teams win more games and so
  collect more votes.

## Addendum: adding All-Australian selection (written before computing it)

Added after the Brownlow-only results were seen. They suggested the Brownlow
misses key-position players (e.g. pick 1's low star rate alongside many tall
number-one picks). **No All-Australian-based figure had been computed when this
was written.**

- **Star season (broad):** a season in which the player is in the top 36 for
  Brownlow votes **or** is named in that season's **All-Australian team** (the
  team as published by DraftGuru, 22 or 23 players; not the 40-man squad).
- **Also reported:** All-Australian selection on its own.
- **Data:** DraftGuru's All-Australian pages for 2006–2026. They link to the same
  DraftGuru player URLs as the draft pages, so picks are joined on URL with no
  name matching. A player drafted twice is counted only for the draft whose
  8-season window contains the selection.
- **Everything else is unchanged:** the same population (national picks 1–80,
  2005–2018), the same 8-season window, at least one star season (main) and two
  or more (second), the same ±5 curve, bands, bootstrap settings and
  mature-age comparison. The picks 1–5 table is repeated with the broad definition.
