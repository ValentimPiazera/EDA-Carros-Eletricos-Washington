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


def top_models(frame: pd.DataFrame, count: int = 10) -> pd.DataFrame:
    """Return the `count` individual models with the most registrations.

    Aggregating by make hides where the concentration actually sits: two
    Teslas alone are a third of the fleet, and no manufacturer-level chart
    shows that.
    """
    models = frame.assign(
        Model=frame["Make"] + " " + frame["Model"]
    ).value_counts(["Model", "Electric Vehicle Type"])
    models = models.reset_index(name="Registrations")
    return models.head(count)


def type_mix_by_year(
    frame: pd.DataFrame, min_registrations: int = 500
) -> pd.DataFrame:
    """Return the BEV/PHEV share of each model year.

    The fleet-wide 79.8/20.2 split is an accumulation and hides the movement
    entirely: plug-ins were 46.4% of model year 2017, fell to 12.8% by 2023
    and came back to 21.7% by 2025. Model years too small to be read as a mix
    are dropped rather than drawn as noise.
    """
    counts = frame.value_counts(["Model Year", "Electric Vehicle Type"])
    counts = counts.reset_index(name="Registrations")
    totals = counts.groupby("Model Year")["Registrations"].transform("sum")
    counts["Share"] = (counts["Registrations"] / totals * 100).round(1)
    counts["Year Total"] = totals
    kept = counts[counts["Year Total"] >= min_registrations]
    return kept.sort_values(
        ["Model Year", "Electric Vehicle Type"], ignore_index=True
    )


def concentration_by_year(
    frame: pd.DataFrame, min_registrations: int = 500
) -> pd.DataFrame:
    """Return how concentrated each model year's makes are.

    The fleet-wide share table says Tesla holds 40.7% and stops there. Split
    by model year, the same counts say something the accumulated figure
    cannot: concentration peaked in 2021 and has fallen every year since,
    while the number of makes on sale nearly doubled.
    """
    rows = []
    for year, group in frame.groupby("Model Year"):
        if len(group) < min_registrations:
            continue
        shares = group["Make"].value_counts(normalize=True) * 100
        rows.append(
            {
                "Model Year": year,
                "Leading make": shares.index[0],
                "Leader share": round(shares.iloc[0], 1),
                "Top 3 share": round(shares.head(3).sum(), 1),
                "Makes present": group["Make"].nunique(),
            }
        )
    return pd.DataFrame(rows)


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


def range_distribution(frame: pd.DataFrame, band: int = 25) -> pd.DataFrame:
    """Return how many vehicles of each type fall in each range band.

    Binned here rather than in the browser: a Plotly histogram ships every
    value it is given, and 99,977 of them would weigh more than the notebook
    they sit in. The counts are what the figure needs anyway.
    """
    known = frame[frame["Electric Range"].notna()]
    edges = list(range(0, int(known["Electric Range"].max()) + band + 1, band))
    bands = pd.cut(known["Electric Range"], bins=edges)
    counts = (
        known.groupby([bands, "Electric Vehicle Type"], observed=True)
        .size()
        .reset_index(name="Registrations")
    )
    counts["Range band"] = (
        counts["Electric Range"].apply(lambda edge: edge.left).astype(int)
    )
    return counts.drop(columns=["Electric Range"]).sort_values(
        ["Range band", "Electric Vehicle Type"], ignore_index=True
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
    """Return median range and volume per model, where the two are comparable.

    The median rather than the mean, and for the same reason figure 7 uses
    one: a model that runs across five model years carries a different rating
    in each, so the average of them describes no version of the car. The Leaf
    spans 73 to 151 miles inside the 2015-2019 window alone.

    Both numbers are drawn from the same rows. The count used to come from
    `Model Year`, which counts every row in the group, while the average
    skipped the `NaN`s — so a model's height came from the rows the DOL had
    researched and its width from all of them. `Coverage` now travels with
    every row, and a model the DOL has barely researched is left out rather
    than drawn as though it were measured.
    """
    period = frame[
        (frame["Model Year"] >= first_year)
        & (frame["Model Year"] <= last_year)
    ]
    grouped = period.groupby(["Make", "Model", "Electric Vehicle Type"]).agg(
        **{
            "Median Electric Range": ("Electric Range", "median"),
            "Registrations": ("Electric Range", "size"),
            "Measured": ("Electric Range", "count"),
        }
    )
    grouped = grouped.reset_index()
    grouped["Coverage"] = grouped["Measured"] / grouped["Registrations"]
    grouped["Model"] = grouped["Make"] + " " + grouped["Model"]
    comparable = grouped[
        (grouped["Measured"] > 0) & (grouped["Coverage"] >= min_coverage)
    ]
    return comparable.drop(columns=["Make", "Measured"]).reset_index(drop=True)


def models_by_periods(
    frame: pd.DataFrame,
    periods: tuple[tuple[int, int], ...] = ((2015, 2019), (2020, 2026)),
    min_coverage: float = 0.5,
) -> pd.DataFrame:
    """Stack several periods into one frame, labelled for faceting.

    Drawn as one figure with a panel each rather than two figures, so that
    what the later panel is missing is visible against the earlier one
    instead of being asserted in the prose underneath it.
    """
    parts = []
    for first_year, last_year in periods:
        part = models_by_period(frame, first_year, last_year, min_coverage)
        part["Period"] = f"{first_year}–{last_year}"
        parts.append(part)
    return pd.concat(parts, ignore_index=True)


def market_share(frame: pd.DataFrame) -> pd.DataFrame:
    """Return each make's share of the fleet, as a percentage."""
    share = frame["Make"].value_counts(normalize=True).reset_index()
    share.columns = ["Make", "Share"]
    share["Share"] = (share["Share"] * 100).round(1)
    return share
