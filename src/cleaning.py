"""Cleaning steps applied to the raw Washington State DOL export.

Every function takes a frame and returns a new one, so that a notebook cell
can be re-run without compounding the edit before it. They are written in the
order they are applied, which `clean` pins and `check_export` verifies —
several of them read a column an earlier step writes or a later step removes,
and getting that order wrong fails quietly rather than loudly.
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

# What a published `Electric Range` can be, per vehicle type, as (floor,
# ceiling) in miles. The BEV floor is what a car cannot go under and still be
# battery-electric; the PHEV floor sits just under the smallest figure the DOL
# actually publishes here — 6 miles, for the 2012-2015 Prius Plug-in and the
# Revuelto. This is the project's single definition of a possible range:
# `blank_unusable_range` cleans by it and `utils.implausible_range` audits by
# it, so the two cannot drift apart.
#
# These numbers delete data. Widen them and an implausible figure survives
# into the averages; tighten them and genuine ratings are destroyed silently —
# a PHEV floor of 40 would erase every Prius Plug-in in the file. Both edges
# are pinned by tests, and `check_export` re-checks the finished export.
PLAUSIBLE_RANGE = {"BEV": (30.0, 400.0), "PHEV": (5.0, 160.0)}

# One city, two spellings, straight from the source. Collapsed onto the form
# the DOL itself uses most often, except where the only difference is the
# capitalisation of a proper noun, where the correct capitalisation wins.
# None of the three reaches figure 5 — the largest, Sedro-Woolley, ranks about
# 103rd once joined — but they inflate the count of distinct cities by three.
CITY_SPELLINGS = {
    "Sedro Woolley": "Sedro-Woolley",
    "Silver Lake": "Silverlake",
    "Mccleary": "McCleary",
}

# Trailing noise on the utility names. Both patterns are anchored to the end
# of the provider token, and `\bINC\b` to a word boundary, so that a name
# merely containing those letters — CITY OF PRINCETON, LINCOLN ELECTRIC —
# survives intact. Stripping a bare "INC" anywhere would maul both.
UTILITY_SUFFIXES = [r"\s*-\s*\(WA\)$", r",?\s*\bINC\b\.?$"]

# Not a provider: the source's way of saying no provider is on file, which
# makes it an absence, and absences are `NaN` here as they are everywhere else.
# Written as `.str.title()` leaves it, which is what `test_cleaning` pins.
UNKNOWN_UTILITY = "No Known Electric Utility Service"


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


def range_bounds(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Return the floor and ceiling each row's own vehicle type allows.

    `replace` rather than `map` on the type, so callers get the same answer
    either side of `abbreviate_vehicle_type`: it shortens the source's
    sentences and leaves an already-shortened `BEV` or `PHEV` alone. A type
    with no entry in `PLAUSIBLE_RANGE` yields `NaN` bounds, which compare
    false against everything — `utils.implausible_range` is what reports
    those rows rather than letting them pass unexamined.
    """
    types = frame["Electric Vehicle Type"].replace(VEHICLE_TYPE_MAPPING)
    floor = types.map({t: low for t, (low, _) in PLAUSIBLE_RANGE.items()})
    ceiling = types.map({t: high for t, (_, high) in PLAUSIBLE_RANGE.items()})
    return floor, ceiling


def blank_unusable_range(frame: pd.DataFrame) -> pd.DataFrame:
    """Blank every `Electric Range` that cannot describe the row it sits on.

    One rule, read off `PLAUSIBLE_RANGE`: a figure outside what the row's own
    vehicle type can reach is not a measurement of that vehicle, so it becomes
    `NaN` rather than an average-dragging number. On this export it catches
    three things — the DOL's 0 for a battery it has not researched, the 1 that
    32 model year 2025 Mercedes-Benz plug-ins carry in a file with nothing at
    all between 2 and 5 miles, and 8 rows badged BEV holding 29 miles, which is
    the published figure for the *plug-in* Hyundai IONIQ. In that last case the
    row's type and its range disagree; blanking says which of the two this
    project trusts, and `utils.implausible_range` then audits the result.

    Genuine low figures survive: 6 miles for the 2012-2015 Prius Plug-in and
    the Revuelto, 8 and 9 for the Mercedes C350e, are all real EPA ratings and
    all sit above their type's floor.
    """
    frame = frame.copy()
    ranges = frame["Electric Range"]
    floor, ceiling = range_bounds(frame)
    unusable = (ranges < floor) | (ranges > ceiling)
    frame.loc[unusable, "Electric Range"] = np.nan
    return frame


def drop_unused_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Drop the seven columns the analysis asks nothing of."""
    return frame.drop(columns=COLS_TO_DROP)


def shorten_cafv_status(frame: pd.DataFrame) -> pd.DataFrame:
    """Rename the CAFV column and shorten its sentence-long values.

    A status is only ever as good as the range it was read off, so a row left
    without a range is left without a ruling too. The source already does this
    for the batteries it has not researched; applying it to the rows
    `blank_unusable_range` emptied keeps the invariant exact — every status in
    the export is one the range column can still account for.
    """
    frame = frame.rename(columns={CAFV_COLUMN: "CAFV Status"})
    frame["CAFV Status"] = frame["CAFV Status"].map(CAFV_MAPPING)
    frame.loc[frame["Electric Range"].isna(), "CAFV Status"] = np.nan
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

    `Bonneville Power Administration` is kept under its own name. It is the
    federal wholesaler rather than a retail supplier, but it is what the
    source records, and relabelling it would be an editorial judgement rather
    than a cleaning step.
    """
    frame = frame.copy()
    # Drop the other providers first: there is no sense stripping suffixes
    # from text that is about to be discarded. Cutting at the separator with
    # a regex rather than `.str.split(...).str[0]` keeps the column in the
    # string dtype, where the list-and-index route drops it to object and
    # leaves the frame no longer comparable to its own round-tripped CSV.
    utility = frame["Electric Utility"].str.replace(r"\|.*$", "", regex=True)
    for suffix in UTILITY_SUFFIXES:
        utility = utility.str.replace(suffix, "", regex=True)
    utility = utility.str.strip().str.title()
    frame["Electric Utility"] = utility.replace(UNKNOWN_UTILITY, np.nan)
    return frame


def standardise_city(frame: pd.DataFrame) -> pd.DataFrame:
    """Collapse the three cities the source spells two ways.

    Sedro-Woolley is 300 rows against 80, Silverlake 32 against 1 and
    McCleary 67 against 2, so each was being counted as two places. The
    counts are too small to move figure 5, but they made the fleet look like
    it covered 494 cities when it covers 491.
    """
    frame = frame.copy()
    frame["City"] = frame["City"].replace(CITY_SPELLINGS)
    return frame


def clean(frame: pd.DataFrame) -> pd.DataFrame:
    """Run every cleaning step, in the one order that is correct.

    The order matters and the dependencies are silent, which is why this
    exists rather than a loose sequence of calls: `keep_washington` reads
    `State`, which `drop_unused_columns` then removes, and
    `shorten_cafv_status` reads `Electric Range`, so it has to run after the
    unusable figures have been blanked or it keeps rulings the range column
    can no longer account for.

    `I-cleaning` walks the same sequence a step at a time, because the
    walk is the narrative. `check_export` is what catches the two diverging.
    """
    frame = drop_incomplete_rows(frame)
    frame = keep_washington(frame)
    frame = blank_unusable_range(frame)
    frame = drop_unused_columns(frame)
    frame = shorten_cafv_status(frame)
    frame = abbreviate_vehicle_type(frame)
    frame = add_vehicle_age(frame)
    frame = simplify_utility(frame)
    return standardise_city(frame)


def check_export(frame: pd.DataFrame) -> pd.Series:
    """Assert what the cleaned export promises, and report the counts.

    A sanity check that only prints is not a check, so this one raises. Each
    line corresponds to a defect this project actually shipped at some point:
    ranges impossible for their own type, a CAFV ruling left behind by the
    range it was read off, and one city arriving under two spellings.
    """
    ranges = frame["Electric Range"]
    floor, ceiling = range_bounds(frame)
    spellings = frame["City"].dropna().unique()
    keys = pd.Series(
        [name.upper().replace(" ", "").replace("-", "") for name in spellings]
    )
    counts = pd.Series(
        {
            "rows": len(frame),
            "columns": frame.shape[1],
            "ranges outside their type's bounds": int(
                ((ranges < floor) | (ranges > ceiling)).sum()
            ),
            "statuses left without a range": int(
                (frame["CAFV Status"].notna() & ranges.isna()).sum()
            ),
            "ages disagreeing with the model year": int(
                (
                    frame["Vehicle Age"] != SNAPSHOT_YEAR - frame["Model Year"]
                ).sum()
            ),
            "cities spelled more than one way": len(keys) - keys.nunique(),
            "required fields left empty": int(
                frame[["County", "City", "Make", "Model"]].isna().sum().sum()
            ),
        }
    )
    broken = counts.drop(["rows", "columns"])
    broken = broken[broken > 0]
    if not broken.empty:
        raise AssertionError(
            f"the export breaks its own invariants: {broken.to_dict()}"
        )
    return counts
