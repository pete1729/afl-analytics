# Prediction plan: Port Adelaide home attendance

Written and committed **before** any model was fitted or scored. The details
below were agreed with the user before any analysis code was written. Where the
notebook departs from this plan, it will say so and why.

**What had been seen already:** while checking the season-page layout, the
2025 and 2026 Port home attendances were printed (the raw rows, no model). For
the training seasons, only summary figures were looked at: games per season,
average crowd by season, time slot and Showdown, and the correlation between
recent form and crowd (0.02).

## Question

How accurately can Port Adelaide's home attendance be predicted from three
things known before the game: **Port's recent record**, **the day/time slot**,
and **whether it's a Showdown**? And how much better is that than just
predicting the average crowd?

## Data

- AFL Tables season pages (`src/afl/attendance.py`), which list each match's
  date, local start time, venue and attendance.
- **Seasons 2014–2026** (the Adelaide Oval era), **leaving out 2020 and 2021**:
  shortened quarters and crowd limits in 2020, and crowd caps and games without
  crowds in 2021. The 2013 and 2021 pages are used only for recent form at the
  start of 2014 and 2022.
- **Home game:** Port is listed as the home team and the venue is Adelaide
  Oval. This leaves out the Shanghai games (none fall in these seasons anyway)
  and Showdowns where Adelaide is the home team.
- **Left out:** finals (the AFL runs finals ticketing) and **Gather Round**
  (any home-and-away round played entirely in South Australia, 2023 onwards).
  In Gather Round the AFL runs ticketing and interstate fans travel.
- That leaves **11 home games in every season: 99 for training, 22 for testing.**
- **2022 crowd caps:** checked, and none were binding. Non-Showdown games drew
  23,000–31,000, and the 2022 Showdown drew 50,090. 2022 stays in.

## Predictors

- **Recent form:** Port's win % over its previous 10 games (draws count as
  half). It runs across seasons and includes finals, so round 1 reflects the end
  of last season.
- **Time slot** (Adelaide local start time; night means a 5pm start or later):
  Thursday or other weeknight, Friday night, Saturday afternoon, Saturday
  night, Sunday afternoon, Sunday night. Training has no Sunday night games, so
  a Sunday night game in the test seasons would be predicted as a Sunday
  afternoon game.
- **Showdown:** Port v Adelaide.

## Models

All are ordinary least squares regressions, with the slot entered as one
dummy per slot:

- **Baseline:** the average training crowd, used as the prediction for every game.
- **A:** Showdown only.
- **B:** Showdown + time slot.
- **C:** Showdown + time slot + recent form (the full model from the brief).

## Validation

- **Metric:** mean absolute error (MAE), in people.
- **Choosing a model (training seasons only):** leave-one-season-out
  cross-validation over the 9 training seasons. Fit on 8 seasons, predict the
  9th, and repeat for each season. The baseline's average is recomputed in each
  fold. The model with the lowest cross-validated MAE is the **chosen model**.
- **Test (looked at once, at the end):** refit the chosen model and the baseline
  on all 99 training games, then predict the 22 games of 2025 and 2026.
- **Primary result:** test MAE of the chosen model against the baseline, and the
  improvement (baseline MAE minus model MAE). The 95% bootstrap interval comes
  from resampling the 22 test games (2,000 resamples, seed 2026).
- **Secondary:** if the chosen model isn't C, C's test MAE is also reported for
  completeness. Per-game errors, and error split by Showdown or not, are
  descriptive only.
