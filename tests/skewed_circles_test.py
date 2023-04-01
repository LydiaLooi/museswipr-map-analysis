from pattern_analysis import SkewedCirclesGroup, Note, Pattern
from constants import SKEWED_CIRCLES, TWO_STACK, THREE_STACK, FOUR_STACK, SWITCH, ZIG_ZAG, TIME_CONVERSION, SINGLE_STREAMS


valid_note1 = Note(0, 0)
valid_note2 = Note(0, 0.1 * TIME_CONVERSION)
valid_note3 = Note(0, 0.2 * TIME_CONVERSION)
valid_note4 = Note(0, 0.3 * TIME_CONVERSION) 
valid_note5 = Note(0, 0.4 * TIME_CONVERSION) 


def test_valid_current_four_stack_when_first():
    current_pattern = Pattern(FOUR_STACK, [], 0, 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_current_zig_zag_when_first():
    current_pattern = Pattern(ZIG_ZAG, [valid_note1, valid_note2, valid_note3], 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_first():
    current_pattern = Pattern(SINGLE_STREAMS, [], 0, 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_valid_current_zig_zag_when_two_stack_previous():
    previous_pattern = Pattern(TWO_STACK, [valid_note1, valid_note2], 0)
    current_pattern = Pattern(ZIG_ZAG, [valid_note2, valid_note3, valid_note4], 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_zig_zag_when_two_stack_previous():
    previous_pattern = Pattern(TWO_STACK, [valid_note1, valid_note2], 0)
    current_pattern = Pattern(ZIG_ZAG, [valid_note2, valid_note3, valid_note4, valid_note5], 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_valid_current_three_stack_when_zig_zag_previous():
    previous_pattern = Pattern(ZIG_ZAG, [valid_note1, valid_note2, valid_note3], 0)
    current_pattern = Pattern(THREE_STACK, [valid_note3, valid_note4, valid_note5], 0)
    
    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_valid_previous():
    previous_pattern = Pattern(ZIG_ZAG, [valid_note1, valid_note2, valid_note3], 0)
    current_pattern = Pattern(SWITCH, [valid_note3, valid_note4], 0)

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False


def test_valid_current_pattern_with_different_time_difference_not_added():
    previous_pattern = Pattern(SWITCH, [valid_note1, valid_note2])
    current_pattern = Pattern(TWO_STACK, [valid_note2, valid_note4])

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_invalid_when_gap_between_switch_and_stack():
    previous_pattern = Pattern(SWITCH, [valid_note1, valid_note2])
    current_pattern = Pattern(THREE_STACK, [valid_note3, valid_note4, valid_note5])

    group = SkewedCirclesGroup(SKEWED_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False