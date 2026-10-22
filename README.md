# afl-analytics

Exploratory AFL analytics in Python, with a focus on questions relevant to
list management and recruitment.

## Questions

1. **Draft pick value** ([notebook](notebooks/01_draft_pick_value.ipynb), exploratory):
   how many AFL games does each national
   draft pick number typically produce, and how have Port Adelaide's picks
   performed against that curve?

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
