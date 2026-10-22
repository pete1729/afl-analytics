# Pre-registration: is goal-kicking momentum real?

Written and committed **before** any repeat rate was computed. The only figures
looked at were sample sizes (to estimate power). Where the analysis departs from
this plan, the notebook will say so and why.

## Question

Commentators talk about "momentum" all the time. **If a team kicked the last
goal, is it more likely to kick the next one than you'd expect from the two
teams' goal totals alone? And is it more likely still after kicking the last
two?**

## Why not just compare with 50%

Better teams kick more goals. If one team kicks 60% of a match's goals and the
order is completely random, the same team still kicks consecutive goals 52% of
the time (0.6 × 0.6 + 0.4 × 0.4). So each match has to be compared with
random orderings of **its own** goals, not with 50%.

After a goal, play restarts with a centre bounce that both rucks contest, so the
scoring team gets no built-in restart advantage.

## Data

- Every 2025 and 2026 match on AFL Tables (home-and-away and finals): 434
  matches, parsed by `src/afl/scoring.py`. Every match's summed points equal its
  scoreboard.
- Scoring events are in the order AFL Tables lists them, which is
  chronological within each quarter.

## Definitions

- **Goals only.** Behinds are ignored, so a behind between two goals doesn't
  break a run.
- **Runs reset each quarter.** A goal's "previous goal" must be in the same
  quarter. The first goal of each quarter is never an outcome, only a previous
  goal for the next one.
- **Repeat:** a goal kicked by the same team that kicked the previous goal.
- **Test 1 (after one goal):** among every goal that has a previous goal in the
  same quarter, the share that are repeats. That's the **repeat rate**.
- **Test 2 (after two goals):** among every goal whose previous **two** goals in
  the same quarter were kicked by the same team, the share kicked by that team
  again. (The run may be longer than two.)

## Baseline: what no momentum looks like

- **Shuffle:** within each match, randomly reorder all the match's goals
  (which team kicked each one), keeping each team's total and the number of
  goals in each quarter. Then recompute both repeat rates.
- **Expected rate:** the pooled repeat rate across all matches, averaged over
  **1,000 shuffles** (seed 2026).
- Comparing within each match takes care of team strength. Because the shuffled
  matches have the same short quarters, it also avoids the known bias that
  streak statistics have in short sequences.

## Primary tests

- **Statistic (each test):** observed repeat rate minus expected repeat rate, in
  percentage points.
- **Interval:** 95% bootstrap interval, 2,000 resamples of **matches**, seed
  2026. Each resample recomputes both the observed and the expected rate from
  the resampled matches' own shuffles.
- **Reading (two-sided, since "anti-momentum" is possible):**
  - *momentum* if the whole interval is above 0;
  - *anti-momentum* if the whole interval is below 0;
  - *inconclusive* otherwise.
- Test 2 is judged on its own interval. "Does the effect get stronger after two
  goals" is answered descriptively by comparing the two point estimates.

## Power

- Test 1: **9,207** goals have a previous goal in the same quarter.
- Test 2: **3,972** goals follow two goals in a row by the same team.

Treating goals as independent, the standard errors are about 0.5 and 0.8
percentage points. **So the tests have roughly 80% power to detect an effect of
about 1.5 points (test 1) and 2.2 points (test 2).** Resampling whole matches
may widen the intervals slightly. Smaller real effects will probably read as
inconclusive, and that wouldn't be evidence of no momentum.

## Secondary (reported, not used to judge the primary tests)

1. The naive comparison with 50%, to show how much team strength alone inflates
   the repeat rate.
2. Each test for 2025 and 2026 separately.
3. After three goals in a row (descriptive; smaller sample).

## Not planned

No changes to the definitions, the seasons or the shuffle after seeing results.
No wind or quarter-by-quarter adjustment (agreed before writing this), no
behinds, no score-margin or time-gap conditions, and no team-by-team momentum
rankings.

## Known limitations

- The shuffle keeps each team's goal total for the **whole match**. If a team
  plays better in one part of a match for reasons other than momentum (a key
  injury, a tactical change, the wind), its goals will bunch together and look
  like momentum. So a positive result would be an upper bound on true momentum.
- Goals are the only events used. Momentum could still show up in other ways
  (inside-50s, possession) that goals miss.
- Two seasons only. The time-on analysis (notebook 07) found that
  single-season patterns often didn't hold up.
