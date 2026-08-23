"""The six figures of `II-analysis`, and the palettes they are drawn with.

Every function takes a frame already aggregated by `utils` and returns a
Plotly figure, leaving `fig.show()` to the notebook.

Plotly does not render on GitHub, so a new figure is not finished until its
PNG has been exported into `images/` and referenced from the README.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# The project's default qualitative palette, and the bolder sequences the two
# scatter plots need to keep one point per model tellable apart. The map is
# the only figure on a continuous scale, because a count is continuous.
PALETTE = px.colors.qualitative.D3
EARLY_PERIOD_PALETTE = px.colors.qualitative.Bold
LATE_PERIOD_PALETTE = px.colors.qualitative.Alphabet

# The two vehicle types are named colours rather than sequence entries, so
# that BEV stays the same blue and PHEV the same grey wherever they appear.
VEHICLE_TYPE_COLOURS = {"BEV": "#5B8DB8", "PHEV": "#B0B0B0"}


def top_makes_bar(frame: pd.DataFrame) -> go.Figure:
    """Figure 1: the ten leading makes, in the fleet and in recent years.

    Two bars per make rather than one. The fleet-wide bar is a ranking of a
    decade of accumulation; the recent bar is the one that says who is
    selling now, and the gap between them is the finding.
    """
    fig = px.bar(
        frame,
        x="Share",
        y="Make",
        color="Era",
        barmode="group",
        title="<b>Figure 1: Top 10 Makes, Whole Fleet Against Recent "
        "Model Years</b>",
        labels={"Share": "Share of registrations (%)"},
        width=900,
        height=650,
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(title_x=0.5, legend_title="")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def model_year_area(frame: pd.DataFrame) -> go.Figure:
    """Figure 2: how the surviving fleet is spread across model years.

    The last point is annotated because it is not comparable to the others:
    the export was taken three weeks into its model year, so the fall at the
    right-hand edge is the snapshot date and not the market.
    """
    fig = px.area(
        frame,
        x="Model Year",
        y="Registrations",
        title="<b>Figure 2: Model Year Profile of the Fleet</b>",
        width=1000,
        height=500,
    )
    last = frame.loc[frame["Model Year"].idxmax()]
    fig.add_annotation(
        x=last["Model Year"],
        y=last["Registrations"],
        text=f"{int(last['Model Year'])} is three weeks long —<br>"
        "the file was exported on 22 January",
        showarrow=True,
        arrowhead=2,
        ax=-70,
        ay=-50,
        align="left",
    )
    fig.update_layout(title_x=0.5)
    return fig


def registration_map(frame: pd.DataFrame) -> go.Figure:
    """Figure 3: where in Washington the fleet is registered.

    Drawn on Plotly's built-in geography rather than map tiles, so the
    notebook still runs with no network. One bubble per geocoded point, its
    area proportional to the registrations sitting on it — which is the
    granularity the DOL publishes, not a choice made here.
    """
    fig = px.scatter_geo(
        frame,
        lon="Longitude",
        lat="Latitude",
        size="Registrations",
        color="Registrations",
        hover_name="City",
        scope="usa",
        fitbounds="locations",
        size_max=38,
        opacity=0.75,
        color_continuous_scale="Viridis",
        width=1000,
        height=650,
        title="<b>Figure 3: Where the Fleet Is Registered</b>",
    )
    fig.update_layout(title_x=0.5)
    fig.update_geos(showsubunits=True, subunitcolor="white")
    return fig


def range_by_year_lines(
    frame: pd.DataFrame,
    min_coverage: float = 0.5,
    min_measured: int = 30,
) -> go.Figure:
    """Figure 4: median range by model year, drawn only where it was measured.

    The BEV line stops at 2020 on purpose. It is not that battery range
    stopped improving — it is that the DOL stopped researching it, and a line
    drawn through 0.3% of a model year would be an invention. Leaving the gap
    visible is the finding; the annotation says so out loud.

    `min_measured` trims the other end for the same reason. Model year 2010
    holds two plug-in hybrids and 2002 a single battery-electric car: their
    coverage is a perfect 100%, and a median of one car is still not a trend.
    """
    drawn = frame[
        (frame["Coverage"] >= min_coverage)
        & (frame["Measured"] >= min_measured)
    ]
    fig = px.line(
        drawn,
        x="Model Year",
        y="Median Electric Range",
        color="Electric Vehicle Type",
        markers=True,
        title="<b>Figure 4: Median Range by Model Year, Where the DOL "
        "Researched It</b>",
        labels={"Median Electric Range": "Median Electric Range (miles)"},
        color_discrete_map=VEHICLE_TYPE_COLOURS,
        template="plotly_white",
        width=1000,
        height=500,
        hover_data={"Registrations": True, "Coverage": ":.0%"},
    )
    bevs = drawn[drawn["Electric Vehicle Type"] == "BEV"]
    if not bevs.empty:
        last = bevs.loc[bevs["Model Year"].idxmax()]
        fig.add_annotation(
            x=last["Model Year"],
            y=last["Median Electric Range"],
            text="the DOL stopped researching BEV range here —<br>"
            "4% of model year 2021 and nothing after",
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-60,
            align="left",
        )
    fig.update_layout(title_x=0.5, legend_title="Type")
    return fig


def range_vs_volume_scatter(
    frame: pd.DataFrame, title: str, palette: list[str]
) -> go.Figure:
    """Figures 5 and 6: mean range against volume, one point per model.

    Only models the DOL has actually researched reach this chart, so both
    axes describe the same vehicles. What that leaves out is itself the
    finding for the later period: almost every recent BEV.
    """
    fig = px.scatter(
        frame,
        x="Registrations",
        y="Mean Electric Range",
        size="Registrations",
        title=title,
        color="Model",
        labels={"Mean Electric Range": "Mean Electric Range (miles)"},
        hover_data={"Coverage": ":.0%"},
        color_discrete_sequence=palette,
        template="plotly_white",
    )
    fig.update_layout(title_x=0.5)
    return fig


def early_period_scatter(frame: pd.DataFrame) -> go.Figure:
    """Figure 5: range against volume for model years 2015 to 2019."""
    return range_vs_volume_scatter(
        frame,
        "<b>Figure 5: Mean Range Against Volume Registered, 2015-2019</b>",
        EARLY_PERIOD_PALETTE,
    )


def late_period_scatter(frame: pd.DataFrame) -> go.Figure:
    """Figure 6: range against volume for model years 2020 to 2026."""
    return range_vs_volume_scatter(
        frame,
        "<b>Figure 6: Mean Range Against Volume Registered, 2020-2026</b>",
        LATE_PERIOD_PALETTE,
    )
