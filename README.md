# afl-analytics

Exploratory AFL analytics in Python, with a focus on questions relevant to
list management and recruitment.

## Questions

1. **Draft pick value** ([notebook](notebooks/01_draft_pick_value.ipynb), exploratory):
   how many AFL games does each national
   draft pick number typically produce, and how have Port Adelaide's picks
   performed against that curve?
2. **Height and age at draft** ([pre-registered plan](docs/preregistration_height_age.md)):
   at the same pick number, do taller or older draftees do better or worse than
   is typical for that pick? [Results](notebooks/02_height_age_at_draft.ipynb):
   the pre-registered height test for picks 41–80 was inconclusive; mature-age
   draftees (19+) beat their pick by about 19 games over 8 seasons.
3. **Mature-age draftees** ([pre-registered hold-out test](docs/preregistration_mature_age_holdout.md),
   [notebook](notebooks/04_mature_age_draftees.ipynb)): the 2019–2021 hold-out
   test was inconclusive (only 16 mature-age picks). In 2005–2018, mature-age
   picks played like juniors taken about 20 places earlier, through both fewer
   busts and more long careers, with the edge concentrated in 20–22-year-olds.
4. **Country vs metro Victorian draftees** ([pre-registered plan](docs/preregistration_country_metro.md),
   [notebook](notebooks/05_country_vs_metro.ipynb)): no sign country players are
   overlooked. Once drafted, both groups matched their pick (difference +1.5
   games over 8 seasons, 95% CI −8.4 to +11.4).
5. **Where the stars come from** ([star-curve definitions](docs/star_curve_definitions.md),
   [notebook](notebooks/06_where_stars_come_from.ipynb)): 79% of the top 36
   Brownlow vote-getters (2024–2026) were top-20 national picks, against 17% of
   all entrants. All-Australians are broader (10% were rookies). The chance of
   a top-36 season falls from 43% for picks 1–5 to about 15% for picks 6–30,
   then to under 5%.
6. **Time on by team** ([notebook](notebooks/07_time_on_by_team.ipynb)): using
   every 2025 and 2026 scoring progression (434 matches), scoring is slightly
   slower in time on (after the 20-minute mark) early in matches, and margins
   narrow. Teams' time-on edges barely carry over between seasons (correlation
   0.16); only Essendon and the Western Bulldogs faded in time on in both.
7. **Goal-kicking momentum** ([pre-registered plan](docs/preregistration_momentum.md),
   [notebook](notebooks/08_goal_momentum.ipynb)): the team that kicked the last
   goal kicks the next one 52.7% of the time, against 51.4% if each match's
   goals came in random order (+1.4 points, 95% CI +0.4 to +2.3). After two in a
   row it's +2.2 points (CI +0.8 to +3.6). That's real but small (about one
   extra back-to-back goal every three or four games), and it may reflect
   good and bad patches within a match rather than the last goal itself.
8. **Predicting Port Adelaide home crowds** ([prediction plan](docs/prediction_plan_attendance.md),
   [notebook](notebooks/09_port_home_attendance.ipynb)): of Port's recent form,
   the time slot and whether it's a Showdown, only the Showdown clearly helps
   (+14,445 people). Trained on 2014–2024, the Showdown-only model missed the
   2025–2026 crowds by 3,923 on average, against 5,798 for predicting the
   average (1,875 better, 95% CI 648 to 3,535). An exploratory regression adding
   day, night (6pm+), Gather Round and form did best (test error 3,122), but
   apart from the Showdown each effect is small and uncertain. Most of the
   remaining error is whole seasons running high or low. A next-game version
   that also tracks recent crowds and early-season interest cut
   cross-validated error by about a quarter (5,111 to 3,916), and halved it in
   2022, but matched the five-variable model on 2025–2026 (3,129 vs 3,122),
   when crowds didn't drift. Predicting every Showdown at the median training
   Showdown crowd (50,397) improved Showdown errors but left overall error
   unchanged. Adding the opponent's tier helped: big Victorian clubs bring
   about 3,800 more people (95% CI 1,300 to 6,500), and test error fell to
   2,914, the lowest of any model. Wet games (BOM rainfall at Adelaide Airport)
   drew fewer people, but a wet/dry flag (1mm or 4mm) didn't improve
   cross-validated predictions. The final model keeps rain anyway, on footy
   logic (−1,734 people on wet days). It misses 2025–2026 crowds by 3,060 on
   average, against 6,183 for predicting the average. Pooling with Adelaide's
   home games doubled the data and confirmed the effects, with rain now clear
   (−1,824, 95% CI −3,301 to −474), but it didn't predict Port's crowds better.
   Opponent form didn't help either.

## Tools

- **Club draft record** ([notebook](notebooks/03_club_draft_record.ipynb)): set
  `CLUB` in the first cell to any club to see its picks against the league
  curve and its rank on the games-vs-expected benchmark.

## Data sources

All data comes from two excellent community-run sites. Thank you to the people
who build and maintain them.

- **[AFL Tables](https://afltables.com/)**: match results, player match
  statistics, scoring progressions and career records.
- **[DraftGuru](https://www.draftguru.com.au/)**: AFL draft history, including
  pick numbers, clubs and draft types.

Both are small hobby sites, so the scraper here is deliberately polite:

- Every page is cached in `data/raw/` and never downloaded twice.
- Requests are made one at a time, with a 1–2 second pause between them.
- Requests send a User-Agent naming this project and a contact email.
- Only the pages needed for the current question are fetched.

Cached pages and processed data are not committed to this repository. Running
the code will rebuild them.

## Project layout

```
src/afl/          reusable code (fetching, parsing)
notebooks/        exploratory analysis
data/raw/         cached HTML pages (gitignored)
data/processed/   cleaned CSV/parquet outputs (gitignored)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
