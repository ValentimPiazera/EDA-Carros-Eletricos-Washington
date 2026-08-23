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
    known = frame[frame["Electric Range"].notna()].copy()
    floor, ceiling = cleaning.range_bounds(known)

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


def registrations_by_location(frame: pd.DataFrame) -> pd.DataFrame:
    """Return one row per geocoded point, with how many cars sit on it.

    The DOL geocodes a registration to the centroid of its postal area, so
    270 thousand vehicles collapse onto 825 points. Aggregating to those
    points is not a simplification imposed here — it is the granularity the
    source actually has, and drawing one dot per car would invent precision
    the file never had. The 78 rows with no location at all are dropped.
    """
    located = frame.dropna(subset=["Longitude", "Latitude"])
    points = located.groupby(["City", "Longitude", "Latitude"]).size()
    return points.reset_index(name="Registrations").sort_values(
        "Registrations", ascending=False, ignore_index=True
    )


def make_share_by_era(
    frame: pd.DataFrame, recent_from: int = 2024, count: int = 10
) -> pd.DataFrame:
    """Return each top make's share of the whole fleet and of recent years.

    Figure 1 on its own ranks a decade of accumulation, which is why
    Chevrolet and Nissan sit second and third on it: the Bolt and the Leaf
    sold in volume years ago. Setting the fleet-wide share beside the share
    of the newest model years turns the same counts into a statement about
    where the market is going rather than where it has been.
    """
    top = frame["Make"].value_counts().head(count).index
    recent = frame[frame["Model Year"] >= recent_from]
    shares = pd.DataFrame(
        {
            "Whole fleet": frame["Make"].value_counts(normalize=True),
            f"Model years {recent_from} onwards": recent["Make"].value_counts(
                normalize=True
            ),
        }
    )
    shares = (shares.loc[top] * 100).round(1).fillna(0.0)
    shares.index.name = "Make"
    return shares.reset_index().melt(
        id_vars="Make", var_name="Era", value_name="Share"
    )


def range_by_model_year(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the median range per model year and type, with its coverage.

    `Coverage` is the share of that year's vehicles the DOL actually
    researched, and it is the column that decides whether the median beside
    it means anything. It has to travel with the figure rather than sit in a
    footnote: for BEVs it falls off a cliff after model year 2020 — 4.2% in
    2021 and zero in most years after — while for PHEVs it stays at 100%
    throughout. A median drawn from 0.3% of a year is not a measurement of
    that year.
    """
    grouped = frame.groupby(["Model Year", "Electric Vehicle Type"]).agg(
        **{
            "Registrations": ("Electric Range", "size"),
            "Measured": ("Electric Range", "count"),
            "Median Electric Range": ("Electric Range", "median"),
        }
    )
    grouped = grouped.reset_index()
    grouped["Coverage"] = grouped["Measured"] / grouped["Registrations"]
    return grouped


def models_by_period(
    frame: pd.DataFrame,
    first_year: int,
    last_year: int,
    min_coverage: float = 0.5,
) -> pd.DataFrame:
    """Return mean range and volume per model, for a period, where comparable.

    Make, model and type are concatenated into a single label so that each
    point identifies one car.

    Both numbers are drawn honestly. The count used to come from `Model Year`,
    which counts every row in the group, while the mean skipped the `NaN`s —
    so a model's height came from the rows the DOL had researched and its
    width from all of them. For the Tesla Model Y that meant a mean built from
    4% of 57,163 registrations, all of them model year 2020, plotted against a
    bubble sized by the whole 2020-2026 window. `Coverage` now travels with
    every row, and a model the DOL has barely researched is left out rather
    than drawn as though it were measured.
    """
    period = frame[
        (frame["Model Year"] >= first_year)
        & (frame["Model Year"] <= last_year)
    ]
    grouped = period.groupby(["Make", "Model", "Electric Vehicle Type"]).agg(
        **{
            "Mean Electric Range": ("Electric Range", "mean"),
            "Registrations": ("Electric Range", "size"),
            "Measured": ("Electric Range", "count"),
        }
    )
    grouped = grouped.reset_index()
    grouped["Coverage"] = grouped["Measured"] / grouped["Registrations"]
    grouped["Model"] = (
        grouped["Make"]
        + " "
        + grouped["Model"]
        + " "
        + grouped["Electric Vehicle Type"]
    )
    comparable = grouped[
        (grouped["Measured"] > 0) & (grouped["Coverage"] >= min_coverage)
    ].copy()
    comparable["Mean Electric Range"] = comparable[
        "Mean Electric Range"
    ].round()
    return comparable.drop(
        columns=["Make", "Electric Vehicle Type", "Measured"]
    )


def market_share(frame: pd.DataFrame) -> pd.DataFrame:
    """Return each make's share of the fleet, as a percentage."""
    share = frame["Make"].value_counts(normalize=True).reset_index()
    share.columns = ["Make", "Share"]
    share["Share"] = (share["Share"] * 100).round(1)
    return share
