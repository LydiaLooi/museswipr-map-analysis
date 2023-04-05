from musemapalyzr.constants import (
    DEFAULT_SAMPLE_RATE,
    FOUR_STACK,
    LONG_INTERVAL,
    SHORT_INTERVAL,
    THREE_STACK,
    TWO_STACK,
    VARYING_STACKS,
)
from musemapalyzr.entities import Note, Segment
from musemapalyzr.map_pattern_analysis import VaryingStacksPattern

valid_note1 = Note(0, 0)
valid_note2 = Note(0, 0.1 * DEFAULT_SAMPLE_RATE)
valid_note3 = Note(0, 0.2 * DEFAULT_SAMPLE_RATE)
valid_note4 = Note(0, 0.3 * DEFAULT_SAMPLE_RATE)
valid_note5 = Note(0, 0.4 * DEFAULT_SAMPLE_RATE)
valid_note6 = Note(0, 0.5 * DEFAULT_SAMPLE_RATE)
valid_note7 = Note(0, 0.6 * DEFAULT_SAMPLE_RATE)
valid_note8 = Note(0, 0.7 * DEFAULT_SAMPLE_RATE)


def test_valid_current_two_stack_when_first():
    current_pattern = Segment(TWO_STACK, [], 0, 0)

    group = VaryingStacksPattern(VARYING_STACKS, [])
    added = group.check_segment(current_pattern)
    assert added


def test_valid_interval_when_first():
    current_pattern = Segment(SHORT_INTERVAL, [], 0, 0)

    group = VaryingStacksPattern(VARYING_STACKS, [])
    added = group.check_segment(current_pattern)
    assert added


def test_valid_stack_when_interval_previous():
    previous_pattern = Segment(SHORT_INTERVAL, [], 0, 0)
    current_pattern = Segment(TWO_STACK, [], 0, 0)

    group = VaryingStacksPattern(VARYING_STACKS, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added


def test_valid_stack_when_stack_previous():
    previous_pattern = Segment(TWO_STACK, [], 0, 0)
    current_pattern = Segment(FOUR_STACK, [], 0, 0)

    group = VaryingStacksPattern(VARYING_STACKS, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added


def test_valid_stack_when_ends_with_interval_returns_False_but_adds():
    current_pattern = Segment(LONG_INTERVAL, [], 0, 0)

    patterns = [
        Segment(SHORT_INTERVAL, [], 0, 0),
        Segment(TWO_STACK, [], 0, 0),
        Segment(THREE_STACK, [], 0, 0),
    ]

    group = VaryingStacksPattern(VARYING_STACKS, patterns)
    added = group.check_segment(current_pattern)
    assert added is False
    assert group.segments[-1].segment_name == LONG_INTERVAL
