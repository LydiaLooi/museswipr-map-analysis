from map_pattern_analysis import EvenCirclesGroup, Segment, Note
from constants import EVEN_CIRCLES, TWO_STACK, THREE_STACK, FOUR_STACK, SWITCH, ZIG_ZAG, DEFAULT_SAMPLE_RATE, SHORT_INTERVAL


valid_note1 = Note(0, 0)
valid_note2 = Note(0, 0.1 * DEFAULT_SAMPLE_RATE)
valid_note3 = Note(0, 0.2 * DEFAULT_SAMPLE_RATE)
valid_note4 = Note(0, 0.3 * DEFAULT_SAMPLE_RATE) 
valid_note5 = Note(0, 0.4 * DEFAULT_SAMPLE_RATE) 


def test_valid_current_four_stack_when_first():
    current_pattern = Segment(FOUR_STACK, [], 0, 0)
    group = EvenCirclesGroup(pattern_name=EVEN_CIRCLES, segments=[])
    added = group.check_segment(current_pattern)
    assert added

def test_valid_current_switch_when_first():
    current_pattern = Segment(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_segment(current_pattern)
    assert added

def test_invalid_current_pattern_when_first():
    current_pattern = Segment(ZIG_ZAG, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_segment(current_pattern)
    assert added is False

def test_valid_current_switch_when_two_stack_previous():
    current_pattern = Segment(SWITCH, [valid_note2, valid_note3], 0)
    previous_pattern = Segment(TWO_STACK, [valid_note1, valid_note2], 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added

def test_valid_current_three_stack_when_switch_previous():
    current_pattern = Segment(THREE_STACK, [valid_note2, valid_note3, valid_note4], 0, 0)
    previous_pattern = Segment(SWITCH, [valid_note1, valid_note2], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added

def test_invalid_current_pattern_when_valid_previous():
    current_pattern = Segment(ZIG_ZAG, [], 0, 0)
    previous_pattern = Segment(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added is False


def test_valid_current_pattern_with_different_time_difference_not_added():
    current_pattern = Segment(TWO_STACK, [valid_note2, valid_note4])
    previous_pattern = Segment(SWITCH, [valid_note1, valid_note2])
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added is False

def test_invalid_when_gap_between_switch_and_stack():
    previous_pattern = Segment(SWITCH, [valid_note1, valid_note2])
    current_pattern = Segment(TWO_STACK, [valid_note3, valid_note4])

    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added is False


def test_starting_with_interval_adds_it_and_returns_True():
    current_pattern = Segment(SHORT_INTERVAL, [valid_note1, valid_note2])

    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_segment(current_pattern)
    assert added is True
    assert group.segments[0].segment_name == SHORT_INTERVAL

def test_ending_with_interval_adds_it_and_returns_False():
    previous_pattern = Segment(TWO_STACK, [valid_note1, valid_note2])
    current_pattern = Segment(SHORT_INTERVAL, [valid_note2, valid_note3])

    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_segment(current_pattern)
    assert added is False
    assert group.segments[-1].segment_name == SHORT_INTERVAL
