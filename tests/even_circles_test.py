from pattern_analysis import EvenCirclesGroup, Pattern, Note
from constants import EVEN_CIRCLES, TWO_STACK, THREE_STACK, FOUR_STACK, SWITCH, ZIG_ZAG, TIME_CONVERSION


valid_note1 = Note(0, 0)
valid_note2 = Note(0, 0.1 * TIME_CONVERSION)
valid_note3 = Note(0, 0.2 * TIME_CONVERSION)
valid_note4 = Note(0, 0.3 * TIME_CONVERSION) 
valid_note5 = Note(0, 0.4 * TIME_CONVERSION) 


def test_valid_current_four_stack_when_first():
    current_pattern = Pattern(FOUR_STACK, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_current_switch_when_first():
    current_pattern = Pattern(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_first():
    current_pattern = Pattern(ZIG_ZAG, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_valid_current_switch_when_two_stack_previous():
    current_pattern = Pattern(SWITCH, [valid_note2, valid_note3], 0)
    previous_pattern = Pattern(TWO_STACK, [valid_note1, valid_note2], 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_valid_current_three_stack_when_switch_previous():
    current_pattern = Pattern(THREE_STACK, [valid_note2, valid_note3, valid_note4], 0, 0)
    previous_pattern = Pattern(SWITCH, [valid_note1, valid_note2], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added

def test_invalid_current_pattern_when_valid_previous():
    current_pattern = Pattern(ZIG_ZAG, [], 0, 0)
    previous_pattern = Pattern(SWITCH, [], 0, 0)
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False


def test_valid_current_pattern_with_different_time_difference_not_added():
    current_pattern = Pattern(TWO_STACK, [valid_note2, valid_note4])
    previous_pattern = Pattern(SWITCH, [valid_note1, valid_note2])
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False

def test_invalid_when_gap_between_switch_and_stack():
    current_pattern = Pattern(SWITCH, [valid_note1, valid_note2])
    previous_pattern = Pattern(SWITCH, [valid_note3, valid_note4])
    group = EvenCirclesGroup(EVEN_CIRCLES, [previous_pattern])
    added = group.check_pattern(current_pattern)
    assert added is False