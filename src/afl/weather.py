"""Daily rainfall from Bureau of Meteorology (BOM) Climate Data Online downloads.

BOM blocks scripted downloads, so the zips are downloaded by hand into
data/raw/bom/ (Climate Data Online -> Rainfall -> Daily -> "All years of data").

BOM credits each reading to the morning it's taken: the rainfall for a date is
the 24 hours to 9am that day. So rain during an afternoon or night game on
date D shows up in the reading for D + 1.
"""

import zipfile

import pandas as pd

from afl.fetch import RAW_DIR

BOM_DIR = RAW_DIR / "bom"
ADELAIDE_AIRPORT = "023034"  # automatic station, about 7 km west of Adelaide Oval


def daily_rainfall(station: str = ADELAIDE_AIRPORT) -> pd.DataFrame:
    """One row per date: rainfall (mm) in the 24 hours to 9am, days covered, quality flag."""
    path = BOM_DIR / f"IDCJAC0009_{station}_1800.zip"
    with zipfile.ZipFile(path) as archive:
        with archive.open(f"IDCJAC0009_{station}_1800_Data.csv") as csv:
            raw = pd.read_csv(csv)
    raw.columns = ["product", "station", "year", "month", "day", "rain_mm", "days", "quality"]
    raw["date"] = pd.to_datetime(raw[["year", "month", "day"]])
    return raw.set_index("date")[["rain_mm", "days", "quality"]]


def game_day_rain(starts: pd.Series, rainfall: pd.DataFrame) -> pd.Series:
    """Rain (mm) from 9am on each game day to 9am the next day, i.e. the next morning's reading.

    NaN if that reading is missing or covers more than one day.
    """
    reading = rainfall.reindex(starts.dt.normalize() + pd.Timedelta(days=1))
    one_day = reading["days"].isna() | (reading["days"] == 1)  # blank means a normal 1-day reading
    return pd.Series(reading["rain_mm"].where(one_day).to_numpy(), index=starts.index)
