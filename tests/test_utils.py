import numpy as np
import pandas as pd
import pytest

from src import utils


def ranges(types, miles):
    return pd.DataFrame(
        {"Electric Vehicle Type": types, "Electric Range": miles}
    )


def test_a_range_inside_the_bounds_of_its_type_is_not_flagged():
    fine = ranges(["BEV", "PHEV"], [215.0, 32.0])
    assert utils.implausible_range(fine).empty


def test_a_type_with_no_bounds_is_flagged_rather_than_skipped():
    flagged = utils.implausible_range(ranges(["FCEV", np.nan], [9999.0, 3.0]))
    assert len(flagged) == 2
    assert set(flagged["Plausibility"]) == {utils.UNBOUNDED_TYPE}


def test_each_flagged_row_names_the_rule_it_broke():
    flagged = utils.implausible_range(ranges(["BEV", "PHEV"], [10.0, 500.0]))
    assert list(flagged["Plausibility"]) == [
        utils.BELOW_FLOOR,
        utils.ABOVE_CEILING,
    ]


def test_a_missing_range_is_nothing_to_complain_about():
    assert utils.implausible_range(ranges(["BEV"], [np.nan])).empty


def models(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "Make",
            "Model",
            "Electric Vehicle Type",
            "Model Year",
            "Electric Range",
        ],
    )


def test_the_range_series_carries_the_coverage_behind_each_median():
    frame = models(
        [
            ["TESLA", "MODEL Y", "BEV", 2023, np.nan],
            ["TESLA", "MODEL Y", "BEV", 2023, np.nan],
            ["TESLA", "MODEL Y", "BEV", 2023, 300.0],
            ["JEEP", "WRANGLER", "PHEV", 2023, 21.0],
        ]
    )
    series = utils.range_by_model_year(frame).set_index(
        "Electric Vehicle Type"
    )
    assert series.loc["BEV", "Coverage"] == pytest.approx(1 / 3)
    assert series.loc["PHEV", "Coverage"] == 1.0
    assert series.loc["BEV", "Registrations"] == 3


def test_a_model_the_dol_barely_researched_is_left_out():
    frame = models(
        [
            ["TESLA", "MODEL Y", "BEV", 2023, np.nan],
            ["TESLA", "MODEL Y", "BEV", 2023, np.nan],
            ["TESLA", "MODEL Y", "BEV", 2023, 300.0],
            ["JEEP", "WRANGLER", "PHEV", 2023, 21.0],
        ]
    )
    plotted = utils.models_by_period(frame, 2020, 2026)
    assert list(plotted["Model"]) == ["JEEP WRANGLER PHEV"]


def test_the_volume_of_a_plotted_model_counts_only_measured_rows_too():
    frame = models(
        [
            ["JEEP", "WRANGLER", "PHEV", 2023, 21.0],
            ["JEEP", "WRANGLER", "PHEV", 2024, 21.0],
        ]
    )
    plotted = utils.models_by_period(frame, 2020, 2026).iloc[0]
    assert plotted["Registrations"] == 2
    assert plotted["Coverage"] == 1.0
    assert plotted["Mean Electric Range"] == 21.0


def fleet(rows):
    return pd.DataFrame(
        rows, columns=["Make", "Model", "Electric Vehicle Type", "Model Year"]
    )


def test_the_model_ranking_keeps_the_make_in_the_label():
    frame = fleet(
        [
            ["TESLA", "MODEL Y", "BEV", 2023],
            ["TESLA", "MODEL Y", "BEV", 2023],
            ["JEEP", "WRANGLER", "PHEV", 2023],
        ]
    )
    top = utils.top_models(frame)
    assert list(top["Model"]) == ["TESLA MODEL Y", "JEEP WRANGLER"]
    assert list(top["Registrations"]) == [2, 1]


def test_a_model_year_too_small_to_read_as_a_mix_is_left_out():
    frame = fleet(
        [["TESLA", "MODEL Y", "BEV", 2023]] * 4
        + [["JEEP", "WRANGLER", "PHEV", 2023]]
        + [["TESLA", "MODEL 3", "BEV", 1999]]
    )
    mix = utils.type_mix_by_year(frame, min_registrations=5)
    assert list(mix["Model Year"].unique()) == [2023]
    assert list(mix["Share"]) == [80.0, 20.0]


def test_concentration_counts_the_leader_the_top_three_and_the_makes():
    frame = fleet(
        [["TESLA", "MODEL Y", "BEV", 2023]] * 5
        + [["KIA", "NIRO", "BEV", 2023]] * 3
        + [["FORD", "MACH-E", "BEV", 2023]] * 1
        + [["JEEP", "WRANGLER", "PHEV", 2023]] * 1
    )
    row = utils.concentration_by_year(frame, min_registrations=5).iloc[0]
    assert row["Leading make"] == "TESLA"
    assert row["Leader share"] == 50.0
    assert row["Top 3 share"] == 90.0
    assert row["Makes present"] == 4


def test_the_quartile_test_returns_the_rows_outside_the_fence():
    frame = pd.DataFrame({"miles": [10, 11, 12, 13, 1000]})
    assert list(utils.outliers_quartile(frame, "miles")["miles"]) == [1000]


def test_the_quartile_test_returns_an_empty_frame_when_all_is_well():
    frame = pd.DataFrame({"miles": [10, 11, 12, 13]})
    assert utils.outliers_quartile(frame, "miles").empty
