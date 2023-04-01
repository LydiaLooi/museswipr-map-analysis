from pattern_analysis import Pattern, OtherGroup
from entities import Note
from constants import TIME_CONVERSION


def test_invalid_tolerance_with_gap():
    previous_pattern = Pattern("", [Note(0, 1 * TIME_CONVERSION), Note(0, 2 * TIME_CONVERSION)])
    current_pattern = Pattern("", [Note(0, 3 * TIME_CONVERSION), Note(0, 4 * TIME_CONVERSION)])

    valid = OtherGroup("", []).interval_between_patterns_is_tolerable(previous_pattern, current_pattern)
    assert not valid

def test_valid_tolerance_with_no_gap():
    previous_pattern = Pattern("", [Note(0, 21.60 * TIME_CONVERSION), Note(0, 21.78 * TIME_CONVERSION)])
    current_pattern = Pattern("", [Note(0, 21.78 * TIME_CONVERSION), Note(0, 21.96 * TIME_CONVERSION)])

    valid = OtherGroup("", []).interval_between_patterns_is_tolerable(previous_pattern, current_pattern)
    assert valid

def test_invalid_tolerance():
    previous_pattern = Pattern("", [Note(0, 1 * TIME_CONVERSION), Note(0, 2 * TIME_CONVERSION)])
    current_pattern = Pattern("", [Note(0, 4 * TIME_CONVERSION), Note(0, 5 * TIME_CONVERSION)])

    valid = OtherGroup("", []).interval_between_patterns_is_tolerable(previous_pattern, current_pattern)
    assert not valid