"""The nine figures of `II-analysis`, and the palettes they are drawn with.

Every function takes a frame already aggregated by `utils` and returns a
Plotly figure, leaving `fig.show()` to the notebook.

Plotly does not render on GitHub, so a new figure is not finished until its
PNG has been exported into `images/` and referenced from the README.
"""

import importlib.util
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src import cleaning

# The last model year the export covers in full. A count for the snapshot
# year is still a true count, which is why figure 4 draws 2026 and annotates
# it; a *share* of it is not, because three weeks of registrations are not a
# random sample of a model year. The two figures that draw shares stop here.
LAST_COMPLETE_YEAR = cleaning.SNAPSHOT_YEAR - 1

# The project's default qualitative palette. Only figure 1 still needs a
# sequence: every other categorical figure splits on vehicle type, which has
# two named colours, and the map is continuous because a count is.
PALETTE = px.colors.qualitative.D3

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


def top_models_bar(frame: pd.DataFrame) -> go.Figure:
    """Figure 2: the ten individual models with the most registrations."""
    fig = px.bar(
        frame,
        x="Registrations",
        y="Model",
        color="Electric Vehicle Type",
        title="<b>Figure 2: Top 10 Models in the Fleet</b>",
        width=900,
        height=600,
        color_discrete_map=VEHICLE_TYPE_COLOURS,
    )
    fig.update_layout(title_x=0.5, legend_title="Type")
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def type_mix_bars(
    frame: pd.DataFrame, through_year: int = LAST_COMPLETE_YEAR
) -> go.Figure:
    """Figure 3: how each model year splits between BEV and PHEV.

    Stops at the last complete model year. A share taken from three weeks of
    the snapshot year is not a smaller measurement of that year, it is a
    biased one — model year 2026 reads 93.9% BEV against 78.3% for 2025, and
    that gap is the calendar rather than the market.
    """
    drawn = frame[frame["Model Year"] <= through_year]
    fig = px.bar(
        drawn,
        x="Model Year",
        y="Share",
        color="Electric Vehicle Type",
        barmode="stack",
        title="<b>Figure 3: BEV and PHEV Share of Each Model Year</b>",
        labels={"Share": "Share of the model year (%)"},
        hover_data={"Registrations": True},
        color_discrete_map=VEHICLE_TYPE_COLOURS,
        template="plotly_white",
        width=1000,
        height=500,
    )
    fig.update_layout(title_x=0.5, legend_title="Type")
    return fig


def concentration_lines(
    frame: pd.DataFrame, through_year: int = LAST_COMPLETE_YEAR
) -> go.Figure:
    """Figure 9: how concentrated each model year is, over how many makes.

    Two shares on the left axis against the count of makes on the right. Also
    stops at the last complete model year, and for a sharper reason than
    figure 3: model year 2026 reads 75.2% for the leader against 26.4% for
    2025, which would draw a spike reversing the whole trend out of three
    weeks of registrations.
    """
    drawn = frame[frame["Model Year"] <= through_year]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=drawn["Model Year"],
            y=drawn["Makes present"],
            name="Makes present",
            marker_color="#D9D9D9",
            hovertemplate="%{y} makes in model year %{x}<extra></extra>",
        ),
        secondary_y=True,
    )
    for column, colour in [
        ("Top 3 share", PALETTE[1]),
        ("Leader share", PALETTE[0]),
    ]:
        fig.add_trace(
            go.Scatter(
                x=drawn["Model Year"],
                y=drawn[column],
                name=column,
                mode="lines+markers",
                line={"color": colour, "width": 3},
            ),
            secondary_y=False,
        )
    fig.update_layout(
        title="<b>Figure 9: Concentration by Model Year</b>",
        title_x=0.5,
        template="plotly_white",
        width=1000,
        height=550,
        legend_title="",
        barmode="overlay",
    )
    fig.update_yaxes(
        title_text="Share of the model year (%)",
        range=[0, 100],
        secondary_y=False,
    )
    fig.update_yaxes(
        title_text="Makes present", rangemode="tozero", secondary_y=True
    )
    fig.update_xaxes(title_text="Model Year")
    return fig


def model_year_area(frame: pd.DataFrame) -> go.Figure:
    """Figure 4: how the surviving fleet is spread across model years.

    The last point is annotated because it is not comparable to the others:
    the export was taken three weeks into its model year, so the fall at the
    right-hand edge is the snapshot date and not the market.
    """
    fig = px.area(
        frame,
        x="Model Year",
        y="Registrations",
        title="<b>Figure 4: Model Year Profile of the Fleet</b>",
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
    """Figure 5: where in Washington the fleet is registered.

    Drawn on Plotly's built-in geography rather than map tiles, so the
    notebook still runs with no network. One bubble per geocoded point, its
    area proportional to the registrations sitting on it — which is the
    granularity the DOL publishes, not a choice made here.

    Size carries the count and nothing else does. Colouring by the same
    number as well looked informative and was not: registrations run 6518:1
    across the points, so a linear scale painted 800 of the 825 the same dark
    end of the ramp and spent a legend on it.
    """
    fig = px.scatter_geo(
        frame,
        lon="Longitude",
        lat="Latitude",
        size="Registrations",
        hover_name="City",
        scope="usa",
        fitbounds="locations",
        size_max=40,
        opacity=0.6,
        color_discrete_sequence=[VEHICLE_TYPE_COLOURS["BEV"]],
        width=1000,
        height=520,
        title="<b>Figure 5: Where the Fleet Is Registered</b>",
    )
    fig.update_layout(title_x=0.5)
    fig.update_geos(showsubunits=True, subunitcolor="white")
    return fig


def range_distribution_bars(frame: pd.DataFrame) -> go.Figure:
    """Figure 6: the two populations `Electric Range` actually contains.

    The point is the gap between the humps. It is also the reason the
    quartile test in `I-cleaning` came back empty: a fence drawn across both
    types at once runs from -248 to 493 miles, which is wider than the data
    it is meant to police, so nothing can fall outside it.
    """
    fig = px.bar(
        frame,
        x="Range band",
        y="Registrations",
        color="Electric Vehicle Type",
        barmode="overlay",
        opacity=0.85,
        title="<b>Figure 6: Electric Range Distribution by Vehicle Type</b>",
        labels={"Range band": "Electric range (miles, band of 25)"},
        color_discrete_map=VEHICLE_TYPE_COLOURS,
        template="plotly_white",
        width=1000,
        height=500,
    )
    fig.add_annotation(
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.96,
        showarrow=False,
        align="right",
        bordercolor="#B0B0B0",
        borderwidth=1,
        borderpad=6,
        bgcolor="white",
        text="A quartile fence drawn across both types<br>"
        "runs from -248 to 493 miles — wider than<br>"
        "the data, which is why it flagged nothing",
    )
    fig.update_layout(title_x=0.5, legend_title="Type", bargap=0.05)
    return fig


def range_by_year_lines(
    frame: pd.DataFrame,
    min_coverage: float = 0.5,
    min_measured: int = 30,
) -> go.Figure:
    """Figure 7: median range by model year, drawn only where it was measured.

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
        title="<b>Figure 7: Median Range by Model Year, Where the DOL "
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
    frame: pd.DataFrame, label_count: int = 3
) -> go.Figure:
    """Figure 8: median range against volume, one point per model, per period.

    One figure with a panel each rather than two figures, so that what the
    later panel is missing reads against the earlier one instead of being
    asserted underneath it.

    Three encodings were taken out. Volume was on the x axis *and* in the
    bubble size, which spent the strongest channel on a variable already
    shown and buried the crowded corner under the big markers. Colour carried
    model identity across 55 models in an 11-colour palette, so five models
    shared each colour; it now carries vehicle type, which is two colours and
    means something. And volume runs 4838:1 in the earlier window, so a
    linear axis pinned 84% of the models into the left tenth of the plot —
    hence the log scale.

    Only three points per panel are labelled — the busiest model and the two
    longest-legged — because a chart that needs a mouse is a chart that cannot
    be exported to `images/`, and because labelling the top three by volume as
    well stacked three names on top of each other in the later panel, where
    the busiest models all sit at much the same height. They are set to the
    left of their marker for the same reason: the busiest model is at the
    right edge of its panel by definition, and a label sitting to its right
    is a label half outside the image.
    """
    labelled = frame.copy()
    labelled["Label"] = ""
    for _, panel in frame.groupby("Period"):
        notable = set(panel.nlargest(1, "Registrations").index)
        notable |= set(
            panel.nlargest(label_count - 1, "Median Electric Range").index
        )
        labelled.loc[sorted(notable), "Label"] = frame.loc[
            sorted(notable), "Model"
        ]
    fig = px.scatter(
        labelled,
        x="Registrations",
        y="Median Electric Range",
        color="Electric Vehicle Type",
        facet_col="Period",
        log_x=True,
        text="Label",
        hover_name="Model",
        hover_data={"Coverage": ":.0%", "Label": False},
        color_discrete_map=VEHICLE_TYPE_COLOURS,
        category_orders={"Electric Vehicle Type": ["BEV", "PHEV"]},
        labels={
            "Median Electric Range": "Median electric range (miles)",
            "Registrations": "Registrations (log scale)",
        },
        template="plotly_white",
        width=1100,
        height=560,
        title="<b>Figure 8: Median Range Against Volume Registered, "
        "by Model</b>",
    )
    fig.update_traces(
        textposition="top left", marker={"size": 9}, cliponaxis=False
    )
    fig.update_layout(title_x=0.5, legend_title="Type")
    return fig


def export_figures(
    figures: dict[str, go.Figure], directory: str = "images", scale: int = 2
) -> pd.DataFrame:
    """Write each figure to `directory` as a PNG, and report what was written.

    Plotly does not render on GitHub, so these files are the whole of what a
    reader sees without executing anything — which is why a figure is not
    finished until its PNG exists and the README links it.

    Exporting needs `kaleido`, which is a development dependency and not a
    runtime one. Without it this writes nothing and says so, rather than
    failing a notebook that is complete in every other respect: the analysis
    does not depend on the export, only the shop window does.
    """
    if importlib.util.find_spec("kaleido") is None:
        return pd.DataFrame(
            {
                "File": list(figures),
                "Written": "no — install kaleido to export",
                "KB": pd.NA,
            }
        )
    target = Path(directory)
    target.mkdir(parents=True, exist_ok=True)
    written = []
    for name, figure in figures.items():
        path = target / f"{name}.png"
        figure.write_image(path, scale=scale)
        written.append(
            {
                "File": path.as_posix(),
                "Written": "yes",
                "KB": round(path.stat().st_size / 1024),
            }
        )
    return pd.DataFrame(written)
