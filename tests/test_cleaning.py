import numpy as np
import pandas as pd
import pytest

from src import cleaning


def utilities(*names):
    return pd.DataFrame({"Electric Utility": list(names)})


def ranges(types, miles):
    return pd.DataFrame(
        {"Electric Vehicle Type": types, "Electric Range": miles}
    )


def source_rows(**overrides):
    row = {
        "VIN (1-10)": "5YJ3E1EA7K",
        "County": "King",
        "City": "Sedro Woolley",
        "State": "WA",
        "Postal Code": 98101.0,
        "Model Year": 2020,
        "Make": "TESLA",
        "Model": "MODEL 3",
        "Electric Vehicle Type": "Battery Electric Vehicle (BEV)",
        cleaning.CAFV_COLUMN: "Clean Alternative Fuel Vehicle Eligible",
        "Electric Range": 266.0,
        "Legislative District": 43.0,
        "DOL Vehicle ID": 123456789,
        "Vehicle Location": "POINT (-122.3 47.6)",
        "Electric Utility": "PUGET SOUND ENERGY INC||CITY OF TACOMA - (WA)",
        "2020 Census Tract": 53033007800,
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_a_provider_whose_name_merely_contains_inc_survives_intact():
    cleaned = cleaning.simplify_utility(
        utilities("CITY OF PRINCETON", "LINCOLN ELECTRIC COOP")
    )
    assert list(cleaned["Electric Utility"]) == [
        "City Of Princeton",
        "Lincoln Electric Coop",
    ]


def test_a_trailing_inc_goes_and_takes_the_comma_before_it_with_it():
    cleaned = cleaning.simplify_utility(
        utilities(
            "PUGET SOUND ENERGY INC",
            "OKANOGAN COUNTY ELEC COOP, INC",
            "CITY OF TACOMA - (WA)",
        )
    )
    assert list(cleaned["Electric Utility"]) == [
        "Puget Sound Energy",
        "Okanogan County Elec Coop",
        "City Of Tacoma",
    ]


def test_only_the_first_provider_of_a_packed_field_is_kept():
    cleaned = cleaning.simplify_utility(
        utilities("BONNEVILLE POWER ADMINISTRATION||CITY OF TACOMA - (WA)")
    )
    assert list(cleaned["Electric Utility"]) == [
        "Bonneville Power Administration"
    ]


def test_the_no_known_provider_placeholder_becomes_nan():
    cleaned = cleaning.simplify_utility(
        utilities("NO KNOWN ELECTRIC UTILITY SERVICE")
    )
    assert cleaned["Electric Utility"].isna().all()


def test_a_range_outside_the_bounds_of_its_own_type_is_blanked():
    cleaned = cleaning.blank_unusable_range(
        ranges(["PHEV", "BEV", "BEV", "PHEV"], [1.0, 0.0, 29.0, 500.0])
    )
    assert cleaned["Electric Range"].isna().all()


def test_a_low_but_published_plug_in_range_survives():
    cleaned = cleaning.blank_unusable_range(
        ranges(["PHEV", "PHEV", "BEV"], [6.0, 9.0, 215.0])
    )
    assert list(cleaned["Electric Range"]) == [6.0, 9.0, 215.0]


def test_the_range_rule_holds_either_side_of_the_type_abbreviation():
    verbose = ranges(["Plug-in Hybrid Electric Vehicle (PHEV)"], [1.0])
    cleaned = cleaning.blank_unusable_range(verbose)
    assert cleaned["Electric Range"].isna().all()


def test_a_status_is_dropped_when_the_range_behind_it_was_blanked():
    frame = pd.DataFrame(
        {
            cleaning.CAFV_COLUMN: [
                "Not eligible due to low battery range",
                "Clean Alternative Fuel Vehicle Eligible",
            ],
            "Electric Range": [np.nan, 215.0],
        }
    )
    cleaned = cleaning.shorten_cafv_status(frame)
    assert list(cleaned["CAFV Status"].isna()) == [True, False]


def test_a_range_sitting_exactly_on_its_type_floor_survives():
    cleaned = cleaning.blank_unusable_range(
        ranges(["PHEV", "BEV"], [5.0, 30.0])
    )
    assert list(cleaned["Electric Range"]) == [5.0, 30.0]


def test_cleaning_a_frame_leaves_the_frame_it_was_given_untouched():
    frame = ranges(["PHEV"], [1.0])
    cleaning.blank_unusable_range(frame)
    assert list(frame["Electric Range"]) == [1.0]


def test_a_city_the_source_spells_two_ways_is_collapsed_onto_one():
    frame = pd.DataFrame({"City": ["Sedro Woolley", "Sedro-Woolley"]})
    cleaned = cleaning.standardise_city(frame)
    assert set(cleaned["City"]) == {"Sedro-Woolley"}


def test_the_pipeline_turns_a_source_row_into_an_export_row():
    cleaned = cleaning.clean(source_rows())
    assert list(cleaned.columns) == [
        "County",
        "City",
        "Model Year",
        "Make",
        "Model",
        "Electric Vehicle Type",
        "CAFV Status",
        "Electric Range",
        "Electric Utility",
        "Vehicle Age",
        "Longitude",
        "Latitude",
    ]
    assert cleaned.iloc[0]["Electric Vehicle Type"] == "BEV"
    assert cleaned.iloc[0]["CAFV Status"] == "Eligible"
    assert cleaned.iloc[0]["Electric Utility"] == "Puget Sound Energy"
    assert cleaned.iloc[0]["City"] == "Sedro-Woolley"
    assert cleaned.iloc[0]["Vehicle Age"] == cleaning.SNAPSHOT_YEAR - 2020


def test_the_pipeline_drops_a_row_registered_outside_washington():
    assert cleaning.clean(source_rows(State="CA")).empty


def test_the_source_point_becomes_a_longitude_and_a_latitude():
    cleaned = cleaning.clean(
        source_rows(**{"Vehicle Location": "POINT (-122.20563 47.76144)"})
    )
    assert cleaned.iloc[0]["Longitude"] == -122.20563
    assert cleaned.iloc[0]["Latitude"] == 47.76144
    assert "Vehicle Location" not in cleaned.columns


def test_a_registration_with_no_point_keeps_empty_coordinates():
    cleaned = cleaning.clean(source_rows(**{"Vehicle Location": None}))
    assert cleaned[["Longitude", "Latitude"]].isna().all().all()


def test_the_export_check_passes_on_what_the_pipeline_produces():
    counts = cleaning.check_export(cleaning.clean(source_rows()))
    assert counts["rows"] == 1
    assert counts["columns"] == 12


def test_a_vehicle_type_the_project_has_never_seen_survives_visibly():
    verbose = "Fuel Cell Electric Vehicle (FCEV)"
    cleaned = cleaning.abbreviate_vehicle_type(
        pd.DataFrame({"Electric Vehicle Type": [verbose]})
    )
    assert list(cleaned["Electric Vehicle Type"]) == [verbose]


def test_the_export_check_refuses_a_type_outside_the_mapping():
    broken = cleaning.clean(
        source_rows(
            **{"Electric Vehicle Type": "Fuel Cell Electric Vehicle (FCEV)"}
        )
    )
    with pytest.raises(AssertionError, match="vehicle types outside"):
        cleaning.check_export(broken)


def test_the_export_check_raises_on_a_point_outside_washington():
    broken = cleaning.clean(source_rows())
    broken.loc[0, "Longitude"] = -80.0
    with pytest.raises(AssertionError, match="coordinates outside Washington"):
        cleaning.check_export(broken)


def test_the_export_check_raises_on_a_status_left_without_a_range():
    broken = cleaning.clean(source_rows())
    broken.loc[0, "Electric Range"] = np.nan
    with pytest.raises(AssertionError, match="statuses left without a range"):
        cleaning.check_export(broken)


def test_the_export_check_raises_on_a_city_spelled_two_ways():
    broken = pd.concat(
        [cleaning.clean(source_rows()), cleaning.clean(source_rows())],
        ignore_index=True,
    )
    broken.loc[1, "City"] = "Sedro Woolley"
    with pytest.raises(AssertionError, match="cities spelled more than one"):
        cleaning.check_export(broken)
