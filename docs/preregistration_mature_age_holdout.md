# Pre-registration: mature-age draftees, hold-out test on 2019–2021 drafts

Written and committed **before** the DraftGuru pages for the 2019, 2020 and
2021 drafts were fetched. Where the analysis departs from this plan, the
notebook will say so and why.

## Background

In the 2005–2018 national drafts, mature-age draftees (19.0+ at the draft) beat
their pick by about 19 more games than juniors over their first 8 seasons
(95% CI +10.7 to +27.6; notebook 02, H2b). That was a secondary result, found
in the same data used to explore. This plan tests it on drafts that haven't
been analysed.

**What has and hasn't been seen.** The AFL Tables season pages (to 2026) and
DraftGuru's birth-month pages are already cached, so games and birth dates for
2019–2021 draftees are on disk. Neither has been joined to those drafts or
analysed. The 2019–2021 draft lists (who was picked, and at which pick) have
not been fetched.

## Hypothesis

**H: in the 2019–2021 national drafts, mature-age draftees beat their pick by
more than junior draftees do, over their first 5 seasons.**

## Data and definitions

Same as notebook 02 unless stated otherwise.

- **Picks:** national draft picks 1–80, 2019–2021, from DraftGuru year pages.
- **Outcome:** games in the first 5 seasons after the draft (Y+1 to Y+5),
  including finals, from AFL Tables. That's 2020–24, 2021–25 and 2022–26, all
  complete. Picks who never played count as 0.
- **Mature-age:** 19.0 or older on 30 November of the draft year. Junior: under
  19.0. (The 2020 draft was held in December, but the reference date stays
  30 November so the definition doesn't change.)
- **Matching:** the existing name matcher and manual-match file. Any new
  unmatched picks who played will be resolved only with the same three pieces
  of evidence (name variant, drafting club, games agreeing with DraftGuru) and
  listed in the notebook.
- **Expected outcome at a pick:** the mean 5-season games of all 2019–2021 picks
  within **±4** of that pick, **leaving out the player's own result**.
  - The window is wider than notebook 02's ±2 because there are only 3 drafts
    (about 25 players per window instead of about 14). Leaving the player out
    matters more with smaller windows.
  - The baseline comes from the same three drafts, not from 2005–2018, so the
    shortened 2020 season and any changes in list rules affect both groups equally.
- **Residual:** actual minus expected.

## Test

- **Statistic:** mean residual of mature-age draftees minus mean residual of juniors.
- **Interval:** 95% bootstrap interval, 2,000 resamples of players, seed 2026.
- **Reading:** *supported* if the whole interval is above 0, *contradicted* if
  the whole interval is below 0, *inconclusive* otherwise.

## Expected size and power

On 2005–2018 data, this exact design (3 consecutive drafts, 5 seasons, ±4
window, leave-one-out) gave an average difference of **+13.6 games**, with a
standard error of about 6 and about 33 mature-age players per 3-draft slice.
The interval excluded 0 in 8 of the 12 slices. So **even if the effect is real,
there's roughly a 1 in 3 chance of an inconclusive result**. An inconclusive
result would therefore not count as evidence against the effect.

The same check showed the effect varied over time: it was smaller for drafts
around 2011–2015. That was noticed during this power check, not looked for.

## Secondary (reported, not used to judge H)

1. The same test using notebook 02's original baseline (±2 window, not
   leave-one-out).
2. Excluding bid-matched picks (academy, father-son, scholarship, zone).
3. Excluding recycled players (anyone with AFL games before their draft year).
4. Bust rates (under 20 games and under 50 games in the window) for mature-age
   vs junior, compared with what's expected at their picks.

## Not planned

No changes to the age cutoff, window length, pick range or baseline after
seeing the 2019–2021 data.
