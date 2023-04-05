from musemapalyzr.constants import DEFAULT_SAMPLE_RATE
from musemapalyzr.entities import Note, Segment
from musemapalyzr.map_pattern_analysis import OtherPattern


def test_invalid_tolerance_with_gap():
    previous_pattern = Segment(
        "", [Note(0, 1 * DEFAULT_SAMPLE_RATE), Note(0, 2 * DEFAULT_SAMPLE_RATE)]
    )
    current_pattern = Segment(
        "", [Note(0, 3 * DEFAULT_SAMPLE_RATE), Note(0, 4 * DEFAULT_SAMPLE_RATE)]
    )

    valid = OtherPattern("", []).interval_between_segments_is_tolerable(
        previous_pattern, current_pattern
    )
    assert not valid


def test_valid_tolerance_with_no_gap():
    previous_pattern = Segment(
        "", [Note(0, 21.60 * DEFAULT_SAMPLE_RATE), Note(0, 21.78 * DEFAULT_SAMPLE_RATE)]
    )
    current_pattern = Segment(
        "", [Note(0, 21.78 * DEFAULT_SAMPLE_RATE), Note(0, 21.96 * DEFAULT_SAMPLE_RATE)]
    )

    valid = OtherPattern("", []).interval_between_segments_is_tolerable(
        previous_pattern, current_pattern
    )
    assert valid


def test_invalid_tolerance():
    previous_pattern = Segment(
        "", [Note(0, 1 * DEFAULT_SAMPLE_RATE), Note(0, 2 * DEFAULT_SAMPLE_RATE)]
    )
    current_pattern = Segment(
        "", [Note(0, 4 * DEFAULT_SAMPLE_RATE), Note(0, 5 * DEFAULT_SAMPLE_RATE)]
    )

    valid = OtherPattern("", []).interval_between_segments_is_tolerable(
        previous_pattern, current_pattern
    )
    assert not valid
