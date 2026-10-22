# Pre-registration: height and age at draft vs draft outcomes

Written and committed **before** any outcome by height or age was computed.
Where the analysis departs from this plan, the notebook will say so and why.

## Question

AFL clubs choose players partly on physical profile. **At a given pick number,
do height or age at the draft predict whether a player does better or worse
than is typical for that pick?** If they do, clubs are systematically
overvaluing or undervaluing that attribute.

The idea that prompted this: at later picks, clubs may favour tall players who
don't go on to play many games, while shorter players are overlooked.

## Data

- National draft picks 2005–2018, picks 1–80 (1,004 picks), from DraftGuru,
  with height at draft and date of birth (1,003 of 1,004 have a date of birth).
- Games per season from AFL Tables, 2006–2026. All 911 picks who played are
  matched (898 by name, 13 by reviewed manual match).

## Definitions

- **Outcome: games in the first 8 seasons after the draft** (seasons Y+1 to Y+8
  for draft year Y), including finals. Picks who never played count as 0.
  Eight seasons is the longest window that is complete for the 2018 draft.
- **Bust**: fewer than 50 games in the window. **Massive bust**: fewer than 20.
- **Expected outcome at a pick**: the mean outcome of all picks within ±2 of
  that pick number (about 70 players), as in notebook 01. Mean rather than
  median, because value is about expected return and late picks are heavily skewed.
- **Residual**: actual minus expected. Positive means the player did better than
  is typical for his pick.
- **Age at draft**: age on 30 November of the draft year. **Junior**: under
  19.0. **Mature-age**: 19.0 or older. The cutoff is a natural gap in the age
  distribution, chosen before looking at outcomes.
- **Height bands** (for charts and tables only): ≤182, 183–189, 190+ cm.
  These are roughly thirds of picks 41–80.

## Hypotheses and tests

Confidence intervals are 95% bootstrap intervals (2,000 resamples of players).

**H1, primary: among picks 41–80, taller players have lower residual games.**
- Test: slope of residual games on height (cm) by ordinary least squares,
  reported per 5cm.
- Supported if the whole interval is below 0. Contradicted if the whole
  interval is above 0. Otherwise inconclusive.
- This is the only primary test. Everything below is secondary and will be
  labelled that way.

**H1 secondary analyses**
- a. The same slope for picks 1–40, to see whether any effect is specific to late picks.
- b. Bust and massive-bust rates: slope of (bust − expected bust rate at the
  pick) on height, for picks 41–80.
- c. Late development: repeat H1 with a 10-season window (drafts 2005–2016 only).
  If the slope moves towards 0 by more than half, report that any height effect
  may be about development timing rather than ability.

**H2, secondary: age at draft**
- a. Juniors, picks 1–80: slope of residual games on age, per 6 months. A
  negative slope means younger draftees do better than their pick, which would
  suggest clubs overvalue physical maturity.
- b. Mature-age vs junior, picks 1–80: difference in mean residual games.
  Expect mature-age players to look good in an 8-season window, because they're
  ready to play sooner. So a 10-season comparison is reported alongside.

## Robustness checks (reported, not used to choose results)

1. Exclude academy and father-son picks (their pick number is set by a rival
   club's bid, not by the drafting club's choice).
2. Exclude recycled players (anyone with AFL games before their draft year).
3. Use the expected outcome *without* the player's own result (leave-one-out).

## Not planned

No further attributes, no slicing by club, and no changing the cutoffs, windows
or pick ranges after seeing results. Birth month and pathway are left for later.

## Known limitations

- Games played is a proxy for value. It doesn't measure quality or role.
- Height partly stands in for position (ruck, key position, small forward),
  which isn't in the data.
- Only drafted players are observed. We can test whether short players
  *outperform their pick*, but not whether clubs overlook short players
  who were never drafted.
- 2020 was a shortened season. It falls inside the window for the 2011–2018
  drafts, lowering their totals a little across all heights and ages.
- Injuries produce busts that recruiting couldn't foresee.
