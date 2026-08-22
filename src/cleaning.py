"""Cleaning steps applied to the raw Washington State DOL export.

Every function takes a frame and returns a new one, so that a notebook cell
can be re-run without compounding the edit before it. They are written in the
order `I-cleaning` applies them, and `keep_washington` has to come before
`drop_unused_columns`, which is what removes the `State` column it reads.
"""

import numpy as np
import pandas as pd

# The year the raw file was exported (2026-01-22). Hard-coded on purpose:
# `Vehicle Age` has to stay correct as the snapshot ages, which it would not
# if it were measured against the current year.
SNAPSHOT_YEAR = 2026

# Registration plumbing and geography below city level. Dropping
# `Vehicle Location` and `Postal Code` is what puts a map out of reach, so
# reintroducing one means reintroducing them here.
COLS_TO_DROP = [
    "Vehicle Location",
    "Legislative District",
    "VIN (1-10)",
    "Postal Code",
    "2020 Census Tract",
    "DOL Vehicle ID",
    "State",
]

CAFV_COLUMN = "Clean Alternative Fuel Vehicle (CAFV) Eligibility"

# The third value is not a third status: it is the DOL saying it has not
# researched the battery, which is an absence of data and maps to NaN.
CAFV_MAPPING = {
    "Clean Alternative Fuel Vehicle Eligible": "Eligible",
    "Not eligible due to low battery range": "Not Eligible (Low Range)",
    "Eligibility unknown as battery range has not been researched": np.nan,
}

VEHICLE_TYPE_MAPPING = {
    "Battery Electric Vehicle (BEV)": "BEV",
    "Plug-in Hybrid Electric Vehicle (PHEV)": "PHEV",
}

# Trailing noise on the utility names, stripped in this order: " - INC" has to
# go before the bare "INC" or the dash would be left behind.
UTILITY_SUFFIXES = [" - (WA)", " - INC", "INC"]


def drop_incomplete_rows(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop the ten rows that carry no registration details at all.

    They are missing `County`, `City`, `Postal Code`, `Electric Utility` and
    `2020 Census Tract` together, so `City` alone is enough to find them.
    """
    return frame.dropna(subset=["City"])


def keep_washington(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep only the vehicles registered in Washington State.

    649 rows are registered elsewhere. The copy is deliberate: the caller goes
    on assigning columns to the result, and without it that assignment lands
    on a slice, whose behaviour depends on the pandas version.
    """
    return frame[frame["State"] == "WA"].copy()


def blank_unresearched_range(frame: pd.DataFrame) -> pd.DataFrame:
    """Replace the zero placeholder in `Electric Range` with `NaN`.

    The DOL writes 0 for vehicles whose range it has not researched, not for
    vehicles without a battery. Left as zeros they would drag every average
    down; as `NaN` they are excluded and the missingness stays visible.
    """
    frame = frame.copy()
    frame["Electric Range"] = frame["Electric Range"].replace(0, np.nan)
    return frame


def drop_unused_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop the seven columns the analysis asks nothing of."""
    return frame.drop(columns=COLS_TO_DROP)


def shorten_cafv_status(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename the CAFV column and shorten its sentence-long values."""
    frame = frame.rename(columns={CAFV_COLUMN: "CAFV Status"})
    frame["CAFV Status"] = frame["CAFV Status"].map(CAFV_MAPPING)
    return frame


def abbreviate_vehicle_type(frame: pd.DataFrame) -> pd.DataFrame:
    """Abbreviate `Electric Vehicle Type` to `BEV` and `PHEV`."""
    frame = frame.copy()
    frame["Electric Vehicle Type"] = frame["Electric Vehicle Type"].map(
        VEHICLE_TYPE_MAPPING
    )
    return frame


def add_vehicle_age(frame: pd.DataFrame) -> pd.DataFrame:
    """Add `Vehicle Age` in years, as `SNAPSHOT_YEAR - Model Year`.

    Exactly collinear with `Model Year` by construction: it is there for
    readability, never as a second variable.
    """
    frame = frame.copy()
    frame["Vehicle Age"] = (SNAPSHOT_YEAR - frame["Model Year"]).astype(
        np.int64
    )
    return frame


def simplify_utility(frame: pd.DataFrame) -> pd.DataFrame:
    """Keep the first provider listed in `Electric Utility`, standardised.

    The source packs every provider serving the address into a single field
    separated by `||`. Keeping the first one is what makes the column
    categorical enough to group and chart, at the cost of the multi-provider
    information — a simplification, not an oversight.
    """
    frame = frame.copy()
    utility = frame["Electric Utility"]
    for suffix in UTILITY_SUFFIXES:
        utility = utility.str.replace(suffix, "", regex=False)
    utility = utility.str.split("|").str[0]
    frame["Electric Utility"] = utility.str.strip().str.title()
    return frame
