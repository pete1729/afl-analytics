# afl-analytics

Exploratory AFL analytics in Python, with a focus on questions relevant to
list management and recruitment.

Where a question is a real test rather than exploration, the plan (hypothesis,
outcome, sample and decision rule) is written and committed in `docs/` before
any result is computed. Changes made after seeing results are labelled as
addenda, and mistakes found later are corrected openly as errata. Null and
inconclusive results are reported alongside the positive ones.

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
   all entrants. All-Australians are broader (10% were rookies). On the most
   position-balanced star measure (a season in the All-Australian squad), the
   chance of a star season within 8 seasons falls steadily: 44% for picks 1–5,
   26% for 6–10, 16% for 21–30 and 6–9% after pick 30. The squad and the
   Brownlow top 40 overlap by only about half, and Brownlow-based measures
   exaggerate both the drop after pick 5 and how rare late-pick stars are.
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
   [notebook](notebooks/09_port_home_attendance.ipynb)): a Showdown is by far
   the biggest effect (+14,445 people), and big Victorian opponents add about
   3,800 (95% CI 1,300 to 6,500). Wet days cost about 1,700. Trained on
   2014–2024, the final model misses 2025–2026 crowds by about 3,060 on
   average, against 6,183 for just predicting the average. Most of the
   remaining error is whole seasons running high or low. The notebook also
   covers the variants tried along the way (time slots, form, recent crowds,
   pooling with Adelaide's home games).
9. **Is pick 1 worth picks 7 and 12?** ([notebook](notebooks/10_pick_1_vs_7_and_12.ipynb)):
   the price of matching a pick-1 academy bid. On the star curve (All-Australian
   squad or Brownlow top 40 within 8 seasons), pick 1 gives about a 49% chance of
   a star, against 42% for pick 7 and 35% for pick 12. Taking both later picks
   gives a 62% chance of at least one star, if the two are independent.
10. **Slow-starting top-20 picks** ([notebook](notebooks/11_slow_starting_top_picks.ipynb),
    exploratory): prompted by Port trading for Luke Pedlar (pick 11 in 2020,
    39 games in 5 injury-hit seasons). Of top-20 picks with under 50 games in
    their first 5 seasons, 4% ever had a star season (All-Australian squad or
    Brownlow top 40), against 57% of those with 50 or more. Three of the four
    who did were key-position talls. The best mid-sized careers were useful
    120–200-game players rather than stars.

## Tools

- **Club draft record** ([notebook](notebooks/03_club_draft_record.ipynb)): set
  `CLUB` in the first cell to any club to see its picks against the league
  curve and its rank on the games-vs-expected benchmark.

## Data sources

Almost all data comes from two excellent community-run sites. Thank you to the
people who build and maintain them.

- **[AFL Tables](https://afltables.com/)**: match results, crowds, player match
  statistics, scoring progressions and career records.
- **[DraftGuru](https://www.draftguru.com.au/)**: AFL draft history, including
  pick numbers, clubs, draft types and All-Australian selections.
- **[Bureau of Meteorology](http://www.bom.gov.au/climate/data/)** (notebook 09
  only): daily rainfall at Adelaide Airport. BOM blocks scripted downloads, so
  download the zip by hand (Climate Data Online → Rainfall → Daily, station
  023034, "All years of data") into `data/raw/bom/`.

AFL Tables and DraftGuru are small hobby sites, so the scraper here is
deliberately polite:

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
docs/             pre-registered plans and definitions
data/raw/         cached HTML pages (gitignored)
data/processed/   cleaned CSV/parquet outputs (gitignored)
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the notebooks

The notebooks are committed with their outputs, so you can read them on GitHub
without running anything. To run them yourself, start Jupyter from the repo's
root folder with the virtual environment active:

```bash
source .venv/bin/activate
jupyter lab
```

A first run downloads every page it needs (a few thousand in total across all
notebooks), one at a time with a pause between each, so expect it to take a
while. Later runs read from the cache in `data/raw/` and are fast.
