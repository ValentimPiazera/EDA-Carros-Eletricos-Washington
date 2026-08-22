import numpy as np
import pandas as pd

from src import cleaning


def utilities(*names):
    return pd.DataFrame({"Electric Utility": list(names)})


def ranges(types, miles):
    return pd.DataFrame(
        {"Electric Vehicle Type": types, "Electric Range": miles}
    )


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


def test_cleaning_a_frame_leaves_the_frame_it_was_given_untouched():
    frame = ranges(["PHEV"], [1.0])
    cleaning.blank_unusable_range(frame)
    assert list(frame["Electric Range"]) == [1.0]
