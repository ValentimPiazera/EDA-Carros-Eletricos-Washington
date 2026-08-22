"""Small analytical helpers: the outlier check and the aggregations charted.

Each aggregation returns the frame one of the figures in `II-analysis` is
drawn from, which is also the table the notebook displays before plotting it.
Count columns are named `Registrations`, after what they hold rather than
after the column they were counted from.
"""

import numpy as np
import pandas as pd

from src import cleaning

# The textbook 1.5, kept as a named constant so the choice of fence is
# visible rather than buried in the arithmetic below.
IQR_MULTIPLIER = 1.5

# What `implausible_range` says about a row it flags.
BELOW_FLOOR = "below the floor for its type"
ABOVE_CEILING = "above the ceiling for its type"
UNBOUNDED_TYPE = "no bounds are defined for this type"


def outliers_quartile(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return the rows falling outside the IQR fence of `column`.

    Run on a column that is mostly `NaN` this returns an empty frame rather
    than an answer — `Electric Range` is 63% missing, so it has to be split by
    vehicle type before the result means anything.
    """
    first_quartile = frame[column].quantile(0.25)
    third_quartile = frame[column].quantile(0.75)
    spread = third_quartile - first_quartile
    lower_fence = first_quartile - IQR_MULTIPLIER * spread
    upper_fence = third_quartile + IQR_MULTIPLIER * spread
    return frame[(frame[column] < lower_fence) | (frame[column] > upper_fence)]


def implausible_range(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the rows whose `Electric Range` is impossible for their type.

    Audits what `cleaning.blank_unusable_range` was supposed to have settled,
    against the same `cleaning.PLAUSIBLE_RANGE` bounds, and adds a
    `Plausibility` column naming the rule each row broke.

    The quartile test cannot do this job. `Electric Range` is bimodal — BEVs
    around 215 miles against PHEVs around 32 — so a fence drawn across both,
    on a column that is 63% `NaN`, comfortably swallows a plug-in claiming a
    single mile. Bounds taken from the domain are what catch it.

    A type with no bounds is reported rather than skipped: `map` turns any
    category the source adds into `NaN`, and a vehicle this project has never
    heard of is exactly what a plausibility gate should be loudest about.
    """
    bounds = cleaning.PLAUSIBLE_RANGE
    known = frame[frame["Electric Range"].notna()].copy()
    types = known["Electric Vehicle Type"]
    floor = types.map({t: low for t, (low, _) in bounds.items()})
    ceiling = types.map({t: high for t, (_, high) in bounds.items()})

    unbounded = floor.isna()
    below = known["Electric Range"] < floor
    above = known["Electric Range"] > ceiling
    known["Plausibility"] = np.select(
        [unbounded, below, above],
        [UNBOUNDED_TYPE, BELOW_FLOOR, ABOVE_CEILING],
        default="",
    )
    flagged = known[unbounded | below | above]
    return flagged.sort_values(["Electric Vehicle Type", "Electric Range"])


def top_makes(frame: pd.DataFrame, count: int = 10) -> pd.DataFrame:
    """Return the `count` makes with the most vehicles registered."""
    makes = frame["Make"].value_counts().reset_index()
    makes.columns = ["Make", "Registrations"]
    return makes.head(count)


def vehicle_type_counts(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the BEV/PHEV split of the fleet."""
    types = frame["Electric Vehicle Type"].value_counts().reset_index()
    types.columns = ["Type", "Registrations"]
    return types


def registrations_by_year(frame: pd.DataFrame) -> pd.DataFrame:
    """Return how many surviving vehicles carry each model year.

    The model-year profile of the fleet as it stands, not a sales series:
    there is no registration date in the export, and 2026 is three weeks long.
    """
    years = frame["Model Year"].value_counts().sort_index().reset_index()
    years.columns = ["Model Year", "Registrations"]
    return years


def cafv_by_type(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the CAFV eligibility counts within each vehicle type.

    The unresearched rows are `NaN` in `CAFV Status` and `groupby` drops them,
    so this counts only the vehicles the DOL has actually ruled on.
    """
    return (
        frame.groupby(["Electric Vehicle Type", "CAFV Status"])
        .size()
        .reset_index(name="Registrations")
    )


def top_cities(frame: pd.DataFrame, count: int = 15) -> pd.DataFrame:
    """Return the `count` cities with the most vehicles, ascending.

    A volume ranking, which tracks population rather than adoption: a claim
    that one city adopts faster than another needs a per-capita denominator.
    """
    cities = frame["City"].value_counts().head(count).reset_index()
    cities.columns = ["City", "Registrations"]
    return cities.sort_values(
        by="Registrations", ascending=True, ignore_index=True
    )


def models_by_period(
    frame: pd.DataFrame, first_year: int, last_year: int
) -> pd.DataFrame:
    """Return mean range and registration count per model, for a period.

    Make, model and type are concatenated into a single label so that each
    point in figures 6 and 7 identifies one car. Models whose mean range is
    `NaN` are dropped, which from model year 2021 on is most of them: the
    result describes the subsample the DOL has researched, not the market.
    """
    period = frame[
        (frame["Model Year"] >= first_year)
        & (frame["Model Year"] <= last_year)
    ]
    period = period.groupby(["Make", "Model", "Electric Vehicle Type"]).agg(
        {"Electric Range": "mean", "Model Year": "count"}
    )
    period = period.reset_index()
    period["Model"] = (
        period["Make"]
        + " "
        + period["Model"]
        + " "
        + period["Electric Vehicle Type"]
    )
    period = period.rename(
        columns={
            "Model Year": "Registrations",
            "Electric Range": "Mean Electric Range",
        }
    )
    period = period.dropna()
    period = period.drop(columns=["Make", "Electric Vehicle Type"])
    period["Mean Electric Range"] = period["Mean Electric Range"].round()
    return period


def market_share(frame: pd.DataFrame) -> pd.DataFrame:
    """Return each make's share of the fleet, as a percentage."""
    share = frame["Make"].value_counts(normalize=True).reset_index()
    share.columns = ["Make", "Share"]
    share["Share"] = (share["Share"] * 100).round(1)
    return share
