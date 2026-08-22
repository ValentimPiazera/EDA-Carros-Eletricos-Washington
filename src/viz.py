"""The eight figures of `II-analysis`, and the palettes they are drawn with.

Every function takes a frame already aggregated by `utils` and returns a
Plotly figure, leaving `fig.show()` to the notebook. Titles and axis labels
are still the Portuguese strings the exported PNGs in `images/` show, so that
a figure rebuilt here is the same figure the README links to.

Plotly does not render on GitHub, so a new figure is not finished until its
PNG has been exported into `images/` and referenced from the README.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# The project's default qualitative palette. The figures that depart from it
# do so for a reason: pastels for the city funnel, which is a ranking and not
# a comparison, and bolder sequences where one point per model has to stay
# tellable apart.
PALETTE = px.colors.qualitative.D3
CITY_PALETTE = px.colors.qualitative.Pastel
EARLY_PERIOD_PALETTE = px.colors.qualitative.Bold
LATE_PERIOD_PALETTE = px.colors.qualitative.Alphabet
MARKET_SHARE_PALETTE = px.colors.qualitative.Prism

# Figure 2 compares two known categories, so its two colours are named rather
# than taken from a sequence: the BEV blue carries the fleet, PHEV is grey.
VEHICLE_TYPE_COLOURS = {"BEV": "#5B8DB8", "PHEV": "#B0B0B0"}


def top_makes_bar(frame: pd.DataFrame) -> go.Figure:
    """Figure 1: the ten makes with the most vehicles registered."""
    fig = px.bar(
        frame,
        x="Quantidade",
        y="Marca",
        title="<b>Figura 1: Top 10 Marcas na Frota<b>",
        width=800,
        height=600,
        color="Marca",
        color_discrete_sequence=PALETTE,
    )
    fig.update_layout(title_x=0.5)
    return fig


def vehicle_type_pie(frame: pd.DataFrame) -> go.Figure:
    """Figure 2: the share of the fleet held by BEVs and by PHEVs."""
    fig = px.pie(
        frame,
        values="Quantidade",
        names="Tipo",
        title="<b>Figura 2: Proporção entre BEVs e PHEVs na Frota<b>",
        width=600,
        height=400,
        color="Tipo",
        color_discrete_map=VEHICLE_TYPE_COLOURS,
    )
    fig.update_layout(title_x=0.5, legend_title="Tipo")
    return fig


def model_year_area(frame: pd.DataFrame) -> go.Figure:
    """Figure 3: how the surviving fleet is spread across model years."""
    return px.area(
        frame,
        x="Ano",
        y="Quantidade",
        title="<b>Figura 3: Curva de Idade Entre a Frota<b>",
        width=1000,
        height=500,
    )


def cafv_by_type_bar(frame: pd.DataFrame) -> go.Figure:
    """Figure 4: CAFV eligibility within each vehicle type."""
    fig = px.bar(
        frame,
        x="Electric Vehicle Type",
        y="Contagem",
        color="CAFV Status",
        title=(
            "<b>Figura 4: Correlação Entre Tipo Tecnológico "
            "e Elegibilidade CAFV</b>"
        ),
        barmode="stack",
        template="plotly_white",
    )
    fig.update_layout(
        xaxis_title="Tipo de Veículo",
        yaxis_title="Volume de Registros",
        legend_title="Status CAFV",
    )
    return fig


def top_cities_funnel(frame: pd.DataFrame) -> go.Figure:
    """Figure 5: the fifteen cities with the most vehicles registered."""
    fig = px.funnel(
        frame,
        x="Quantidade",
        y="Cidade",
        width=800,
        height=600,
        title="<b>Figura 5: Top 15 Cidades com Mais Veículos Registrados<b>",
        color="Cidade",
        color_discrete_sequence=CITY_PALETTE,
    )
    fig.update_layout(title_x=0.5)
    return fig


def range_vs_volume_scatter(
    frame: pd.DataFrame, title: str, palette: list[str]
) -> go.Figure:
    """Figures 6 and 7: mean range against volume, one point per model.

    Read as a shape rather than a trend: from model year 2021 on the DOL has
    researched the range of a minority of vehicles, so the later period is a
    selected subsample, not the market.
    """
    return px.scatter(
        frame,
        x="Quantidade",
        y="Autonomia",
        size="Quantidade",
        title=title,
        color="Modelo",
        labels={"Autonomia": "Autonomia em Milhas"},
        color_discrete_sequence=palette,
        template="plotly_white",
    )


def early_period_scatter(frame: pd.DataFrame) -> go.Figure:
    """Figure 6: range against volume for model years 2015 to 2019."""
    return range_vs_volume_scatter(
        frame,
        "<b>Figura 6: Relação de Autonomia e Quantidade "
        "Registrada 2015 - 2019<b>",
        EARLY_PERIOD_PALETTE,
    )


def late_period_scatter(frame: pd.DataFrame) -> go.Figure:
    """Figure 7: range against volume for model years 2020 to 2026."""
    return range_vs_volume_scatter(
        frame,
        "<b>Figura 7: Relação de Autonomia e Quantidade "
        "Registrada 2020- 2026<b>",
        LATE_PERIOD_PALETTE,
    )


def market_share_treemap(frame: pd.DataFrame) -> go.Figure:
    """Figure 8: each make's share of the fleet, as a percentage."""
    fig = px.treemap(
        frame,
        path=["Marca"],
        values="Participação",
        color="Marca",
        color_discrete_sequence=MARKET_SHARE_PALETTE,
        title="<b> Figura 8: Marketshare Geral em Porcentagem",
    )
    fig.update_traces(
        textinfo="label+value",
        texttemplate="<b>%{label}</b><br>%{value:.1f}%",
        textfont_size=14,
    )
    fig.update_layout(title_x=0.5)
    return fig
