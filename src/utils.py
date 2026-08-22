"""Small analytical helpers: outlier checks and the aggregations charted.

Each aggregation returns the frame that a figure in `II-analysis` is drawn
from, which is also the table the notebook displays before plotting it. The
column names they produce are still the Portuguese ones the figures label
their axes with; translating them is a separate step from moving them here.
"""

import pandas as pd

# Rows below this share of the fence are not outliers by the IQR rule; the
# multiplier is the textbook 1.5, kept explicit so the choice is visible.
IQR_MULTIPLIER = 1.5

# The two CAFV statuses as figure 4 labels them.
CAFV_LABELS = {
    "Eligible": "Elegível",
    "Not Eligible (Low Range)": "Não Elegível (Baixa Autonomia)",
}


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


def top_makes(frame: pd.DataFrame, count: int = 10) -> pd.DataFrame:
    """Return the `count` makes with the most vehicles registered."""
    makes = frame["Make"].value_counts().reset_index()
    makes.columns = ["Marca", "Quantidade"]
    return makes.head(count)


def vehicle_type_counts(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the BEV/PHEV split of the fleet."""
    types = frame["Electric Vehicle Type"].value_counts().reset_index()
    types.columns = ["Tipo", "Quantidade"]
    return types


def registrations_by_year(frame: pd.DataFrame) -> pd.DataFrame:
    """Return how many surviving vehicles carry each model year.

    A model-year composition of the fleet as it stands, not a sales series:
    there is no registration date in the export, and 2026 is three weeks long.
    """
    years = frame["Model Year"].value_counts().sort_index().reset_index()
    years.columns = ["Ano", "Quantidade"]
    return years


def cafv_by_type(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the CAFV eligibility counts within each vehicle type.

    The unresearched rows are `NaN` in `CAFV Status` and `groupby` drops them,
    so this counts only the vehicles the DOL has actually ruled on.
    """
    counts = (
        frame.groupby(["Electric Vehicle Type", "CAFV Status"])
        .size()
        .reset_index(name="Contagem")
    )
    counts["CAFV Status"] = counts["CAFV Status"].map(CAFV_LABELS)
    return counts


def top_cities(frame: pd.DataFrame, count: int = 15) -> pd.DataFrame:
    """Return the `count` cities with the most vehicles, ascending.

    A volume ranking, which tracks population rather than adoption: a claim
    that one city adopts faster than another needs a per-capita denominator.
    """
    cities = frame["City"].value_counts().head(count).reset_index()
    cities.columns = ["Cidade", "Quantidade"]
    return cities.sort_values(
        by="Quantidade", ascending=True, ignore_index=True
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
            "Model Year": "Quantidade",
            "Electric Range": "Autonomia",
            "Model": "Modelo",
        }
    )
    period = period.dropna()
    period = period.drop(columns=["Make", "Electric Vehicle Type"])
    period["Autonomia"] = period["Autonomia"].round()
    return period


def market_share(frame: pd.DataFrame) -> pd.DataFrame:
    """Return each make's share of the fleet, as a percentage."""
    share = frame["Make"].value_counts(normalize=True).reset_index()
    share.columns = ["Marca", "Participação"]
    share["Participação"] = (share["Participação"] * 100).round(1)
    return share
